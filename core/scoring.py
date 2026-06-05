"""
규칙 기반 점수 산출 및 레벨 판정 엔진
"""
import pandas as pd
import json

# ── 레벨 판정 ────────────────────────────────────────────
def get_level(score: float) -> str:
    if score >= 80: return "상"
    if score >= 60: return "중"
    return "하"

def score_to_100(value: float, min_val: float, max_val: float) -> float:
    """원점수를 100점 척도로 환산"""
    return round((value - min_val) / (max_val - min_val) * 100, 1)

# ── 해석 텍스트 (레벨별 미리 작성) ───────────────────────
INTERPRETATIONS = {
    "1차_현재상태": {
        "상": "구성원들은 변화의 필요성을 충분히 공감하고 있으며, 협업 수준과 디지털 활용도가 높습니다. 변화 피로도가 낮고 참여 의지가 강해 변화관리 추진에 유리한 환경입니다.",
        "중": "변화 필요성에 대한 공감대는 형성되어 있으나 일부 영역에서 피로도나 참여 의지의 편차가 존재합니다. 핵심 저항 요인을 파악하고 참여 동기를 강화하는 접근이 필요합니다.",
        "하": "변화 필요성에 대한 공감이 낮거나 변화 피로도가 높아 저항 가능성이 큽니다. 변화 착수 전 충분한 소통과 심리적 안전감 형성이 선행되어야 합니다.",
    },
    "1차_변화추진환경": {
        "상": "리더십의 변화 지원 의지가 명확하고 커뮤니케이션 체계와 교육 지원 체계가 잘 갖춰져 있습니다. 변화관리 인프라가 충분히 준비된 상태입니다.",
        "중": "변화 추진 환경이 부분적으로 갖춰져 있으나 리더십 일관성이나 교육·지원 체계에 보완이 필요합니다. 변화 추진 전 인프라 강화가 권고됩니다.",
        "하": "변화 관련 커뮤니케이션, 리더십 지원, 교육 체계가 미흡합니다. 변화 추진 구조를 먼저 설계하고 리더십 정렬(Alignment)을 선행해야 합니다.",
    },
    "2차_조직구조": {
        "상": "조직도와 R&R이 명확하고 의사결정 체계가 효율적으로 운영되고 있습니다. 변화 추진 구조를 즉시 적용할 수 있는 기반이 마련되어 있습니다.",
        "중": "조직 구조는 갖춰져 있으나 일부 R&R 불명확 또는 의사결정 지연 이슈가 있습니다. 변화 추진 전 역할 재정의가 필요합니다.",
        "하": "조직 구조의 복잡성 또는 R&R 불명확으로 변화 추진에 장애가 예상됩니다. 변화 추진 TF 구성 및 의사결정 체계 정비가 시급합니다.",
    },
    "2차_업무방식": {
        "상": "업무 프로세스가 표준화되어 있고 정보 공유와 문서 관리 체계가 효율적입니다. 새로운 업무 방식 도입이 수월할 것으로 예상됩니다.",
        "중": "일부 업무 프로세스는 표준화되어 있으나 정보 공유나 문서 관리에 비효율이 존재합니다. 핵심 업무 흐름 중심의 개선이 필요합니다.",
        "하": "업무 프로세스가 개인 의존적이거나 비표준화되어 있습니다. 변화관리와 병행하여 프로세스 정비가 필요합니다.",
    },
    "2차_협업문화": {
        "상": "부서 간 협업이 활발하고 특정 인력 의존도가 낮습니다. 수평적 협업 문화가 변화 확산에 긍정적으로 작용할 것입니다.",
        "중": "협업 의지는 있으나 구조적 장벽이나 일부 인력 의존도 이슈가 있습니다. 협업 활성화를 위한 제도적 지원이 필요합니다.",
        "하": "부서 간 협업이 미흡하거나 사일로(Silo) 현상이 강합니다. 협업 문화 개선을 변화관리의 핵심 과제로 설정해야 합니다.",
    },
    "2차_제도정책": {
        "상": "KPI와 평가·보상 체계가 변화 활동을 충분히 반영하고 있습니다. 제도적 지원이 변화 행동을 촉진하는 구조입니다.",
        "중": "일부 제도에서 변화 활동이 반영되고 있으나 일관성이 부족합니다. 변화 관련 KPI 설계 및 보상 체계 연계가 필요합니다.",
        "하": "현행 평가·보상 체계가 변화 활동을 반영하지 않아 구성원의 참여 동기가 낮습니다. 제도 개편이 변화관리의 선결 과제입니다.",
    },
    "2차_디지털환경": {
        "상": "디지털 솔루션이 충분히 보유·운영되고 있으며 라이선스 활용률이 높습니다. 디지털 기반의 변화 추진이 즉시 가능합니다.",
        "중": "솔루션은 보유하고 있으나 활용률이나 운영 정책에 개선 여지가 있습니다. 디지털 활용 교육과 정책 정비가 병행되어야 합니다.",
        "하": "디지털 환경이 미흡하거나 솔루션 활용률이 낮습니다. 디지털 역량 강화와 인프라 확충이 선행되어야 합니다.",
    },
    "2차_변화경험": {
        "상": "과거 변화 프로젝트 경험이 풍부하고 성공 경험을 통한 학습이 축적되어 있습니다. 이전 경험을 레버리지로 활용할 수 있습니다.",
        "중": "일부 변화 경험이 있으나 성공과 실패가 혼재합니다. 과거 실패 요인을 분석하고 이번 변화관리에서 보완하는 접근이 필요합니다.",
        "하": "변화 프로젝트 경험이 적거나 부정적 경험이 주를 이룹니다. 초기 작은 성공 경험(Quick Win)을 통한 신뢰 구축이 중요합니다.",
    },
    "3차_인터뷰": {
        "상": "인터뷰 대상자들이 변화에 긍정적이며 Pain Point가 명확하게 파악되었습니다. 잠재적 변화 챔피언이 다수 확인되었습니다.",
        "중": "일부 계층에서 변화 저항 징후가 확인되었습니다. 계층별 맞춤 커뮤니케이션 전략이 필요합니다.",
        "하": "변화 저항이 광범위하게 존재하며 조직 내 암묵적 문화가 변화를 저해하고 있습니다. 심층적인 저항 관리 전략이 필요합니다.",
    },
    "4차_협업행동": {
        "상": "회의 참여율, 채팅 활성도, 파일 공유, 공동 편집 모두 높은 수준입니다. 협업 행동이 이미 정착되어 있습니다.",
        "중": "일부 협업 지표는 양호하나 특정 지표에서 개선이 필요합니다. 협업 도구 활용을 촉진하는 가이드와 교육이 필요합니다.",
        "하": "협업 행동 지표 전반이 저조합니다. 협업 문화 형성을 위한 집중적인 개입과 행동 변화 프로그램이 필요합니다.",
    },
    "4차_디지털활용": {
        "상": "라이선스 사용률과 기능별 활용률이 높습니다. 디지털 도구를 통한 변화 추진이 효과적으로 이루어질 수 있습니다.",
        "중": "일부 기능의 활용률이 낮습니다. 기능별 맞춤 교육과 활용 가이드 제공이 필요합니다.",
        "하": "전반적인 디지털 도구 활용률이 낮습니다. 기초 디지털 역량 강화 교육을 우선 시행해야 합니다.",
    },
    "4차_변화참여": {
        "상": "교육·캠페인·챌린지 참여율이 높고 우수사례 공유가 활발합니다. 변화 참여 행동이 조직 전반에 확산되고 있습니다.",
        "중": "일부 변화 참여 활동에서 저조한 참여율이 관찰됩니다. 참여 동기 강화와 인센티브 설계가 필요합니다.",
        "하": "변화 관련 활동 전반의 참여율이 낮습니다. 참여 장벽을 제거하고 작은 참여부터 유도하는 단계적 접근이 필요합니다.",
    },
    "4차_협업네트워크": {
        "상": "부서 간 협업 빈도가 높고 정보 공유 흐름이 원활합니다. 핵심 영향자가 변화 확산에 긍정적 역할을 할 것으로 예상됩니다.",
        "중": "일부 부서 간 협업은 활발하나 전체 네트워크에 편차가 있습니다. 취약한 연결 고리를 강화하는 개입이 필요합니다.",
        "하": "부서 간 협업 네트워크가 취약하고 정보 흐름이 단절되어 있습니다. 네트워크 활성화를 위한 공식·비공식 채널 구축이 시급합니다.",
    },
}

# ── 권고사항 (레벨별 미리 작성) ──────────────────────────
RECOMMENDATIONS = {
    "상": [
        "현재의 강점을 변화 추진의 레버리지로 적극 활용",
        "변화 챔피언을 공식 선발하여 역할 부여",
        "성공 사례를 조기에 가시화하여 조직 전체로 확산",
    ],
    "중": [
        "취약 영역 중심의 집중 개입 계획 수립",
        "계층별·부서별 맞춤형 커뮤니케이션 전략 설계",
        "단기 Quick Win 과제를 선정하여 변화 모멘텀 확보",
        "리더십 정렬(Alignment) 워크숍 실시",
    ],
    "하": [
        "변화 착수 전 충분한 사전 준비 기간 확보",
        "경영진의 변화 의지 공식 선언 및 지속적 메시지 발신",
        "저항 관리를 위한 심층 인터뷰 및 우려사항 청취 세션 운영",
        "소규모 파일럿(Pilot) 그룹부터 변화 시작",
        "변화관리 전담 TF 구성 및 외부 전문가 지원 검토",
    ],
}

# ── 1차 설문 점수 산출 ────────────────────────────────────
def calc_survey(df: pd.DataFrame) -> dict:
    # 현재상태 영역 (변화 피로도는 역산)
    current_cols = {
        "q1_change_necessity":      1.0,
        "q2_collaboration":         1.0,
        "q3_digital_usage":         1.0,
        "q4_change_fatigue":       -1.0,  # 역산
        "q5_change_participation":  1.0,
        "q6_job_satisfaction":      1.0,
    }
    change_env_cols = {
        "q7_communication":    1.0,
        "q8_leader_support":   1.0,
        "q9_education_system": 1.0,
        "q10_change_structure":1.0,
    }

    def weighted_avg(df, col_weights):
        total_w, total_s = 0, 0
        for col, w in col_weights.items():
            if col in df.columns:
                vals = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(vals):
                    avg = vals.mean()
                    score = avg if w > 0 else (6 - avg)  # 역산: 5점 척도
                    total_s += score * abs(w)
                    total_w += abs(w)
        return round(total_s / total_w, 2) if total_w else 0

    s1 = weighted_avg(df, current_cols)
    s2 = weighted_avg(df, change_env_cols)

    score1 = score_to_100(s1, 1, 5)
    score2 = score_to_100(s2, 1, 5)
    overall = round((score1 * 0.5 + score2 * 0.5), 1)

    # 요구사항 집계 (체크박스 컬럼)
    def count_checks(col):
        if col not in df.columns: return {}
        counts = {}
        for val in df[col].dropna():
            for item in str(val).split(","):
                item = item.strip()
                if item:
                    counts[item] = counts.get(item, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1])[:5])

    return {
        "현재상태_점수": score1,
        "현재상태_등급": get_level(score1),
        "현재상태_해석": INTERPRETATIONS["1차_현재상태"][get_level(score1)],
        "변화추진환경_점수": score2,
        "변화추진환경_등급": get_level(score2),
        "변화추진환경_해석": INTERPRETATIONS["1차_변화추진환경"][get_level(score2)],
        "종합점수": overall,
        "종합등급": get_level(overall),
        "선호_변화방식": count_checks("preferred_change_method"),
        "선호_소통방식": count_checks("preferred_communication"),
        "선호_학습방식": count_checks("preferred_learning"),
        "응답자수": len(df),
    }


# ── 2차 조직 자료 분석 점수 산출 ─────────────────────────
def calc_internal(sheets: dict) -> dict:
    areas = ["조직구조", "업무방식", "협업문화", "제도정책", "디지털환경", "변화경험"]
    results = {}
    scores = []

    for area in areas:
        key = f"2차_{area}"
        if area in sheets:
            df = sheets[area]
            if "평가점수" in df.columns:
                vals = pd.to_numeric(df["평가점수"], errors="coerce").dropna()
                score = score_to_100(vals.mean(), 1, 5) if len(vals) else 0
            else:
                score = 0
        else:
            score = 0

        level = get_level(score)
        results[area] = {
            "점수": score,
            "등급": level,
            "해석": INTERPRETATIONS[key][level],
        }
        scores.append(score)

    overall = round(sum(scores) / len(scores), 1) if scores else 0
    results["종합점수"] = overall
    results["종합등급"] = get_level(overall)
    return results


# ── 3차 인터뷰 점수 산출 ─────────────────────────────────
def calc_interview(interviews: list) -> dict:
    if not interviews:
        return {"종합점수": 0, "종합등급": "하", "해석": "", "저항유형": {}, "계층별": {}}

    scores = []
    resistance_types = {}
    by_role = {}

    for iv in interviews:
        s = iv.get("change_readiness_score", 3)
        try:
            s = float(s)
        except:
            s = 3.0
        scores.append(s)

        rt = iv.get("resistance_type", "")
        if rt:
            resistance_types[rt] = resistance_types.get(rt, 0) + 1

        role = iv.get("role", "기타")
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(s)

    avg = sum(scores) / len(scores) if scores else 3
    score = score_to_100(avg, 1, 5)
    level = get_level(score)

    role_summary = {
        role: round(score_to_100(sum(v)/len(v), 1, 5), 1)
        for role, v in by_role.items()
    }

    return {
        "종합점수": score,
        "종합등급": level,
        "해석": INTERPRETATIONS["3차_인터뷰"][level],
        "저항유형_분포": resistance_types,
        "계층별_점수": role_summary,
        "인터뷰_수": len(interviews),
    }


# ── 4차 행동 진단 점수 산출 ──────────────────────────────
def calc_behavior(sheets: dict) -> dict:
    def pct_score(df, cols):
        vals = []
        for c in cols:
            if c in df.columns:
                v = pd.to_numeric(df[c], errors="coerce").dropna()
                if len(v):
                    vals.append(v.mean())
        return round(sum(vals) / len(vals), 1) if vals else 0

    areas = {
        "협업행동":   (["회의참여율", "채팅활성도", "파일공유율", "공동편집비율"], "4차_협업행동"),
        "디지털활용": (["라이선스사용률", "채팅활용률", "회의활용률", "활성사용자비율"], "4차_디지털활용"),
        "변화참여":   (["교육참여율", "캠페인참여율", "챌린지참여율"], "4차_변화참여"),
        "협업네트워크":(["협업빈도점수", "정보공유점수"], "4차_협업네트워크"),
    }

    results = {}
    scores = []

    for area, (cols, key) in areas.items():
        if area in sheets:
            score = pct_score(sheets[area], cols)
        else:
            score = 0

        level = get_level(score)
        results[area] = {
            "점수": score,
            "등급": level,
            "해석": INTERPRETATIONS[key][level],
        }
        scores.append(score)

    overall = round(sum(scores) / len(scores), 1) if scores else 0
    results["종합점수"] = overall
    results["종합등급"] = get_level(overall)
    return results


# ── 최종 종합 점수 ────────────────────────────────────────
def synthesize(survey: dict, internal: dict, interview: dict, behavior: dict) -> dict:
    weights = {"survey": 0.3, "internal": 0.25, "interview": 0.2, "behavior": 0.25}
    overall = round(
        survey.get("종합점수", 0)   * weights["survey"] +
        internal.get("종합점수", 0) * weights["internal"] +
        interview.get("종합점수", 0)* weights["interview"] +
        behavior.get("종합점수", 0) * weights["behavior"],
        1
    )
    level = get_level(overall)

    # 점수가 낮은 영역을 Top Risks로 자동 도출
    all_scores = []
    for area in ["현재상태", "변화추진환경"]:
        s = survey.get(f"{area}_점수", 0)
        if s: all_scores.append((area, s))
    for area in ["조직구조", "업무방식", "협업문화", "제도정책", "디지털환경", "변화경험"]:
        s = internal.get(area, {}).get("점수", 0)
        if s: all_scores.append((area, s))
    for area in ["협업행동", "디지털활용", "변화참여", "협업네트워크"]:
        s = behavior.get(area, {}).get("점수", 0)
        if s: all_scores.append((area, s))

    top_risks = [
        {"risk": area, "description": f"점수 {score}점 ({get_level(score)})", "impact": "높음" if score < 50 else "중간"}
        for area, score in sorted(all_scores, key=lambda x: x[1])[:3]
    ]

    return {
        "종합점수": overall,
        "종합등급": level,
        "권고사항": RECOMMENDATIONS[level],
        "top_risks": top_risks,
        "차수별_점수": {
            "1차 설문": survey.get("종합점수", 0),
            "2차 조직자료": internal.get("종합점수", 0),
            "3차 인터뷰": interview.get("종합점수", 0),
            "4차 행동진단": behavior.get("종합점수", 0),
        }
    }

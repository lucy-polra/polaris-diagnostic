"""
샘플 입력 파일 생성 (템플릿 다운로드용)
"""
import pandas as pd
import json
import io


def survey_csv() -> str:
    rows = [
        {
            "respondent_id": "EMP001", "department": "개발팀", "role": "실무자",
            "q1_change_necessity": 4, "q2_collaboration": 3, "q3_digital_usage": 4,
            "q4_change_fatigue": 2, "q5_change_participation": 4, "q6_job_satisfaction": 3,
            "q7_communication": 3, "q8_leader_support": 3, "q9_education_system": 2, "q10_change_structure": 3,
            "preferred_change_method": "워크숍,코칭", "preferred_communication": "설명회,리더 메시지",
            "preferred_learning": "집합교육,실습 중심",
            "pain_area": "부서 간 협업 부재", "priority_issue": "의사결정 속도", "support_needed": "명확한 방향 제시",
        },
        {
            "respondent_id": "EMP002", "department": "마케팅팀", "role": "관리자",
            "q1_change_necessity": 3, "q2_collaboration": 2, "q3_digital_usage": 3,
            "q4_change_fatigue": 4, "q5_change_participation": 2, "q6_job_satisfaction": 2,
            "q7_communication": 2, "q8_leader_support": 2, "q9_education_system": 2, "q10_change_structure": 2,
            "preferred_change_method": "우수사례 공유,캠페인", "preferred_communication": "뉴스레터,FAQ",
            "preferred_learning": "온라인 교육(실시간),마이크로러닝",
            "pain_area": "업무 중복 및 비효율", "priority_issue": "프로세스 표준화", "support_needed": "교육 지원",
        },
        {
            "respondent_id": "EMP003", "department": "영업팀", "role": "실무자",
            "q1_change_necessity": 5, "q2_collaboration": 4, "q3_digital_usage": 3,
            "q4_change_fatigue": 1, "q5_change_participation": 5, "q6_job_satisfaction": 4,
            "q7_communication": 4, "q8_leader_support": 4, "q9_education_system": 3, "q10_change_structure": 4,
            "preferred_change_method": "챌린지,워크숍", "preferred_communication": "커뮤니티,영상 콘텐츠",
            "preferred_learning": "실습 중심,Q&A",
            "pain_area": "디지털 도구 활용 부족", "priority_issue": "협업 툴 도입", "support_needed": "실습 교육",
        },
    ]
    return pd.DataFrame(rows).to_csv(index=False)


def internal_xlsx() -> bytes:
    sheets = {
        "조직구조": pd.DataFrame({
            "평가항목": ["조직도 명확성", "R&R 정의", "의사결정 체계", "변화 추진 구조"],
            "평가점수": [3, 2, 3, 2],
            "비고": ["일부 중복 역할 존재", "R&R 불명확 부서 다수", "승인 단계 과다", "전담 조직 없음"],
        }),
        "업무방식": pd.DataFrame({
            "평가항목": ["업무 프로세스 표준화", "회의 운영 효율성", "정보 공유 수준", "문서 관리 체계"],
            "평가점수": [3, 2, 3, 2],
            "비고": ["일부 표준화", "회의 목적 불명확", "부서 내 공유는 활발", "개인 PC 저장 관행"],
        }),
        "협업문화": pd.DataFrame({
            "평가항목": ["부서 간 협업 구조", "부서 간 협업 수준", "특정 인력 의존도"],
            "평가점수": [2, 2, 4],
            "비고": ["협업 채널 부재", "타 부서 협력 저조", "핵심 인력 1~2명 의존"],
        }),
        "제도정책": pd.DataFrame({
            "평가항목": ["KPI 변화 활동 반영", "평가·보상 체계 공정성", "변화 활동 인센티브"],
            "평가점수": [2, 3, 1],
            "비고": ["변화 활동 미반영", "보통 수준", "인센티브 없음"],
        }),
        "디지털환경": pd.DataFrame({
            "평가항목": ["솔루션 보유 현황", "라이선스 활용률", "시스템 운영 정책"],
            "평가점수": [4, 3, 3],
            "비고": ["M365 E3 보유", "일부 기능 미활용", "정책 수립 필요"],
        }),
        "변화경험": pd.DataFrame({
            "평가항목": ["과거 변화 프로젝트 경험", "교육 이력", "변화 수용 경험"],
            "평가점수": [2, 3, 2],
            "비고": ["소규모 경험만 있음", "단발성 교육", "실패 경험 다수"],
        }),
    }
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for sheet_name, df in sheets.items():
            df.to_excel(w, sheet_name=sheet_name, index=False)
    return buf.getvalue()


def interview_json() -> str:
    data = [
        {
            "interviewee_id": "IV001", "role": "임원", "department": "경영진", "date": "2026-06-01",
            "pain_points": "디지털 전환 속도가 경쟁사 대비 느림. 내부 저항이 예상보다 강함.",
            "resistance_factors": ["변화 필요성 공감 부족", "업무 증가 우려"],
            "implicit_culture": "상명하달 의사결정 문화, 실패에 대한 두려움",
            "leadership_issues": "중간 관리자층의 변화 지지 여부가 불확실",
            "success_experiences": "2023년 ERP 도입 시 교육 선행으로 안착",
            "failure_experiences": "2022년 협업툴 도입 실패 — 교육 없이 강제 전환",
            "resistance_type": "감정적",
            "change_readiness_score": 3,
        },
        {
            "interviewee_id": "IV002", "role": "관리자", "department": "개발팀", "date": "2026-06-01",
            "pain_points": "팀원들이 새로운 도구를 왜 써야 하는지 모름. 기존 방식이 더 편하다는 인식.",
            "resistance_factors": ["학습 부담", "업무 연속성 우려"],
            "implicit_culture": "개인 능력 중심 문화, 협업보다 개인 성과 중시",
            "leadership_issues": "경영진 메시지가 현장까지 전달이 안됨",
            "success_experiences": "소규모 파일럿 성공 경험 있음",
            "failure_experiences": "전사 동시 전환 시도 실패",
            "resistance_type": "인지적",
            "change_readiness_score": 2,
        },
        {
            "interviewee_id": "IV003", "role": "실무자", "department": "마케팅팀", "date": "2026-06-02",
            "pain_points": "회의가 너무 많고 성과로 연결이 안됨. 변화 관련 공지가 너무 많아 피로함.",
            "resistance_factors": ["변화 피로도", "업무 과중"],
            "implicit_culture": "회의 중심 문화, 보고서 위주 업무",
            "leadership_issues": "팀장이 변화에 소극적",
            "success_experiences": "캠페인 툴 도입 시 자발적 학습으로 성공",
            "failure_experiences": "의무 교육 이후 실제 활용 없음",
            "resistance_type": "행동적",
            "change_readiness_score": 2,
        },
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


def behavior_xlsx() -> bytes:
    sheets = {
        "협업행동": pd.DataFrame({
            "팀명": ["개발팀", "마케팅팀", "영업팀", "운영팀"],
            "회의참여율": [85, 70, 90, 60],
            "채팅활성도": [75, 60, 80, 45],
            "파일공유율": [65, 55, 70, 40],
            "공동편집비율": [40, 30, 50, 20],
        }),
        "디지털활용": pd.DataFrame({
            "팀명": ["개발팀", "마케팅팀", "영업팀", "운영팀"],
            "라이선스사용률": [90, 75, 85, 60],
            "채팅활용률": [80, 65, 75, 45],
            "회의활용률": [85, 70, 80, 55],
            "활성사용자비율": [88, 72, 83, 58],
        }),
        "변화참여": pd.DataFrame({
            "팀명": ["개발팀", "마케팅팀", "영업팀", "운영팀"],
            "교육참여율": [80, 60, 85, 50],
            "캠페인참여율": [60, 50, 70, 35],
            "챌린지참여율": [55, 40, 65, 25],
        }),
        "협업네트워크": pd.DataFrame({
            "부서A": ["개발팀", "개발팀", "마케팅팀", "영업팀"],
            "부서B": ["마케팅팀", "영업팀", "운영팀", "운영팀"],
            "협업빈도점수": [70, 80, 50, 60],
            "정보공유점수": [65, 75, 45, 55],
        }),
    }
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for sheet_name, df in sheets.items():
            df.to_excel(w, sheet_name=sheet_name, index=False)
    return buf.getvalue()

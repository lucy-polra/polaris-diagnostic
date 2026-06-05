import streamlit as st
import pandas as pd
import json
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.scoring import calc_survey, calc_internal, calc_interview, calc_behavior, synthesize
from core.report import generate
from core.samples import survey_csv, internal_xlsx, interview_json, behavior_xlsx

if not st.session_state.get("authenticated"):
    st.warning("메인 페이지에서 로그인해주세요.")
    st.stop()

st.title("진단 실행")
st.caption("4가지 진단 자료를 업로드하면 점수와 해석이 자동으로 도출됩니다.")
st.markdown("---")

# ── 입력 영역 ───────────────────────────────────────────
project_name = st.text_input("프로젝트명 *", placeholder="예: 2026 디지털 전환 프로젝트")

col1, col2 = st.columns(2)
with col1:
    st.subheader("1차  사전 진단 설문")
    st.caption("CSV | 현재상태(q1~q6) + 변화추진환경(q7~q10) + 요구사항")
    survey_file = st.file_uploader("파일 선택", type=["csv"], key="survey")

    st.subheader("2차  조직 자료 분석")
    st.caption("Excel | 6개 시트: 조직구조 / 업무방식 / 협업문화 / 제도정책 / 디지털환경 / 변화경험")
    internal_file = st.file_uploader("파일 선택", type=["xlsx"], key="internal")

with col2:
    st.subheader("3차  인터뷰 진단")
    st.caption("JSON | 임원 / 관리자 / 실무자 / 핵심이해관계자 인터뷰 결과")
    interview_file = st.file_uploader("파일 선택", type=["json"], key="interview")

    st.subheader("4차  행동 진단")
    st.caption("Excel | 4개 시트: 협업행동 / 디지털활용 / 변화참여 / 협업네트워크")
    behavior_file = st.file_uploader("파일 선택", type=["xlsx"], key="behavior")

with st.expander("📥 입력 양식 샘플 다운로드"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.download_button("1차 설문 CSV", survey_csv(), "1차_설문_샘플.csv", "text/csv")
    with c2:
        st.download_button("2차 조직자료 Excel", internal_xlsx(), "2차_조직자료_샘플.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c3:
        st.download_button("3차 인터뷰 JSON", interview_json(), "3차_인터뷰_샘플.json", "application/json")
    with c4:
        st.download_button("4차 행동진단 Excel", behavior_xlsx(), "4차_행동진단_샘플.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("---")

# ── 분석 실행 ───────────────────────────────────────────
ready = all([project_name, survey_file, internal_file, interview_file, behavior_file])
if not ready:
    st.info("프로젝트명과 4가지 파일을 모두 업로드하면 분석 버튼이 활성화됩니다.")

if st.button("🚀 진단 분석 시작", type="primary", disabled=not ready):

    with st.spinner("분석 중입니다... 잠시 기다려주세요."):
        try:
            # 1차 설문
            survey_result = calc_survey(pd.read_csv(survey_file))

            # 2차 내부자료
            xls = pd.ExcelFile(internal_file)
            sheets_internal = {s: pd.read_excel(xls, sheet_name=s) for s in xls.sheet_names}
            internal_result = calc_internal(sheets_internal)

            # 3차 인터뷰
            interview_result = calc_interview(json.load(interview_file))

            # 4차 행동
            xls2 = pd.ExcelFile(behavior_file)
            sheets_behavior = {s: pd.read_excel(xls2, sheet_name=s) for s in xls2.sheet_names}
            behavior_result = calc_behavior(sheets_behavior)

            # 종합
            synthesis_result = synthesize(survey_result, internal_result, interview_result, behavior_result)

            # Word 리포트 생성
            report_bytes = generate(project_name, survey_result, internal_result,
                                    interview_result, behavior_result, synthesis_result)

            # SharePoint 저장
            report_url = ""
            sp_status = ""
            try:
                from core.sharepoint import SharePointClient
                sp = SharePointClient()
                filename = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M')}_진단리포트.docx"
                report_url = sp.upload_report(report_bytes, filename)
                top_risks = [r.get("risk", "") for r in synthesis_result.get("top_risks", [])]
                sp.save_result(project_name, {
                    "overall": synthesis_result.get("종합점수", 0),
                    "overall_level": synthesis_result.get("종합등급", ""),
                    "survey": survey_result.get("종합점수", 0),
                    "behavior": behavior_result.get("종합점수", 0),
                    "risks": top_risks,
                }, report_url)
                sp_status = "success"
            except Exception as sp_err:
                sp_status = f"fail:{sp_err}"

            # 결과를 session_state에 저장
            st.session_state["result"] = {
                "synthesis": synthesis_result,
                "survey": survey_result,
                "internal": internal_result,
                "interview": interview_result,
                "behavior": behavior_result,
                "report_bytes": report_bytes,
                "project_name": project_name,
                "sp_status": sp_status,
            }

        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.exception(e)

# ── 결과 표시 (session_state에서 유지) ─────────────────
if "result" in st.session_state:
    r = st.session_state["result"]
    synthesis_result = r["synthesis"]
    survey_result    = r["survey"]
    internal_result  = r["internal"]
    interview_result = r["interview"]
    behavior_result  = r["behavior"]
    report_bytes     = r["report_bytes"]
    project_name_r   = r["project_name"]
    sp_status        = r["sp_status"]

    if sp_status == "success":
        st.success("✅ 진단 완료! SharePoint 저장 완료!")
    elif sp_status.startswith("fail"):
        st.warning(f"✅ 진단 완료! (SharePoint 저장 실패: {sp_status[5:]})")
    else:
        st.success("✅ 진단 완료!")

    st.markdown("---")
    st.subheader("📋 진단 결과")

    overall = synthesis_result.get("종합점수", 0)
    level   = synthesis_result.get("종합등급", "")

    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric("종합 변화준비도", f"{overall}점", f"등급: {level}")
    for col, (label, key) in zip([col_b, col_c, col_d, col_e], [
        ("1차 설문", "1차 설문"), ("2차 조직자료", "2차 조직자료"),
        ("3차 인터뷰", "3차 인터뷰"), ("4차 행동진단", "4차 행동진단"),
    ]):
        s = synthesis_result["차수별_점수"].get(key, 0)
        lv = "상" if s >= 80 else "중" if s >= 60 else "하"
        col.metric(label, f"{s}점", f"등급: {lv}")

    st.markdown("---")
    st.subheader("권고사항")
    for rec in synthesis_result.get("권고사항", []):
        st.markdown(f"- **{rec}**")

    tab1, tab2, tab3, tab4 = st.tabs(["1차 설문", "2차 조직자료", "3차 인터뷰", "4차 행동진단"])

    with tab1:
        st.metric("현재 상태 진단", f"{survey_result.get('현재상태_점수',0)}점", survey_result.get('현재상태_등급',''))
        st.write(survey_result.get("현재상태_해석", ""))
        st.metric("변화 추진 환경", f"{survey_result.get('변화추진환경_점수',0)}점", survey_result.get('변화추진환경_등급',''))
        st.write(survey_result.get("변화추진환경_해석", ""))
        st.markdown("**선호 방식 집계**")
        for label, key in [("변화관리 방식","선호_변화방식"),("소통 방식","선호_소통방식"),("학습 방식","선호_학습방식")]:
            data = survey_result.get(key, {})
            if data:
                st.write(f"_{label}_: " + "  |  ".join(f"{k}({v}명)" for k,v in data.items()))

    with tab2:
        for area in ["조직구조","업무방식","협업문화","제도정책","디지털환경","변화경험"]:
            d = internal_result.get(area, {})
            if d:
                st.metric(area, f"{d.get('점수',0)}점", d.get('등급',''))
                st.caption(d.get("해석",""))

    with tab3:
        st.metric("인터뷰 종합", f"{interview_result.get('종합점수',0)}점", interview_result.get('종합등급',''))
        st.write(interview_result.get("해석",""))
        role_scores = interview_result.get("계층별_점수", {})
        if role_scores:
            st.markdown("**계층별 점수**")
            cols = st.columns(len(role_scores))
            for col, (role, score) in zip(cols, role_scores.items()):
                lv = "상" if score >= 80 else "중" if score >= 60 else "하"
                col.metric(role, f"{score}점", lv)
        resist = interview_result.get("저항유형_분포", {})
        if resist:
            st.markdown("**저항 유형 분포:** " + "  |  ".join(f"{k}({v}건)" for k,v in resist.items()))

    with tab4:
        for area in ["협업행동","디지털활용","변화참여","협업네트워크"]:
            d = behavior_result.get(area, {})
            if d:
                st.metric(area, f"{d.get('점수',0)}점", d.get('등급',''))
                st.caption(d.get("해석",""))

    st.markdown("---")
    st.download_button(
        "📥 Word 리포트 다운로드",
        report_bytes,
        f"{project_name_r}_진단리포트_{datetime.now().strftime('%Y%m%d')}.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )

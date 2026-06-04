import streamlit as st

st.set_page_config(
    page_title="폴라리스클라우드 진단 에이전트",
    page_icon="🔭",
    layout="wide",
)

# ── 비밀번호 인증 ──────────────────────────────────────────
import config

def check_password():
    if st.session_state.get("authenticated"):
        return True
    st.markdown("## 🔭 폴라리스클라우드 변화관리 진단 에이전트")
    st.markdown("---")
    pw = st.text_input("접근 비밀번호", type="password")
    if st.button("로그인", type="primary"):
        if pw == config.APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")
    st.stop()

check_password()

# ── 메인 홈 화면 ───────────────────────────────────────────
st.title("🔭 폴라리스클라우드 변화관리 진단 에이전트")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 사용 방법
    1. 왼쪽 사이드바에서 **진단 실행** 선택
    2. 프로젝트명 입력
    3. 4가지 진단 자료 업로드
    4. 분석 시작 버튼 클릭
    5. 결과 확인 및 Word 리포트 다운로드
    """)

with col2:
    st.markdown("""
    ### 진단 항목
    | # | 항목 | 파일 형식 |
    |---|------|---------|
    | 1 | 설문조사 분석 | CSV |
    | 2 | 내부 자료 분석 | Excel (.xlsx) |
    | 3 | 인터뷰 분석 | JSON |
    | 4 | 행동기반 진단 | JSON |
    """)

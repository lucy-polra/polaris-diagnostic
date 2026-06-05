import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

if not st.session_state.get("authenticated"):
    st.warning("메인 페이지에서 로그인해주세요.")
    st.stop()

st.title("진단 이력 조회")
st.caption("SharePoint 연동 후 이전 진단 이력을 조회할 수 있습니다.")
st.markdown("---")

try:
    import config
    if not all([config.SHAREPOINT_SITE_ID, config.SHAREPOINT_LIST_ID,
                config.TENANT_ID, config.CLIENT_ID, config.CLIENT_SECRET]):
        st.info("SharePoint 설정이 완료되면 이력 조회가 가능합니다. .env 파일에 SharePoint 정보를 입력해주세요.")
        st.stop()

    from core.sharepoint import SharePointClient
    import pandas as pd

    sp = SharePointClient()
    items = sp.get_history()

    if not items:
        st.info("저장된 진단 이력이 없습니다.")
    else:
        rows = []
        for item in items:
            f = item.get("fields", {})
            rows.append({
                "프로젝트명": f.get("Title", ""),
                "진단일":     f.get("DiagnosisDate", "")[:10],
                "종합점수":   f.get("OverallScore", ""),
                "종합등급":   f.get("OverallLevel", ""),
                "리포트":     f.get("FileLink", ""),
            })
            
        # 🚨 여기에 파이썬 단 정렬 로직 추가!
        # 이력 조회 UI 페이지 코드의 DataFrame 생성 부분
        df = pd.DataFrame(rows)
        if not df.empty:
            # 진단일을 기준으로 내림차순(최신순) 정렬
            df = df.sort_values(by="진단일", ascending=False)
            
        st.dataframe(df, use_container_width=True, hide_index=True)

        #st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"SharePoint 연결 오류: {e}")

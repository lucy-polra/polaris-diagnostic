# 폴라리스클라우드 변화관리 진단 에이전트

## 구성
- **웹**: Streamlit (로컬 or Streamlit Cloud 무료 배포)
- **AI**: Google Gemini 1.5 Flash (무료 tier)
- **DB**: SharePoint (Excel + List) via Microsoft Graph API
- **리포트**: Word(.docx) 자동 생성 후 SharePoint 저장

---

## 설치 및 실행

### 1단계 — 패키지 설치
```
pip install -r requirements.txt
```

### 2단계 — Azure AD 앱 등록 (1회만)
1. https://portal.azure.com → Azure Active Directory → App registrations
2. New registration → 이름: `polaris-diagnostic`
3. Certificates & Secrets → New client secret → 값 복사
4. API Permissions → Microsoft Graph → Application → `Sites.ReadWrite.All`, `Files.ReadWrite.All` 추가
5. Grant admin consent

### 3단계 — SharePoint ID 확인
브라우저에서 아래 URL 접근 (tenant, site명 변경):
```
https://graph.microsoft.com/v1.0/sites/{tenant}.sharepoint.com:/sites/{sitename}
```
→ id 값 복사 (SHAREPOINT_SITE_ID)

드라이브 ID:
```
https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives
```

### 4단계 — SharePoint List 생성
SharePoint 사이트 → New → List → 이름: `진단결과`
컬럼 추가: DiagnosisDate(날짜), OverallScore(숫자), ChangeReadiness(텍스트), TopRisks(여러 줄 텍스트), ReportURL(하이퍼링크)

### 5단계 — Gemini API 키 발급 (무료)
https://aistudio.google.com → Get API key

### 6단계 — 환경변수 설정
`.env.example`을 `.env`로 복사 후 값 입력

### 7단계 — 실행
```
streamlit run app.py
```

---

## 입력 데이터 포맷

| 구분 | 파일 형식 | 주요 컬럼/구조 |
|------|----------|--------------|
| 설문조사 | CSV | respondent_id, department, q1~qN(1~5점), comment1~N |
| 내부자료 | Excel | 시트1: 행동양식, 시트2: 업무수치(KPI, 이직률 등) |
| 인터뷰 | JSON | role, department, topics(pain_points, readiness 등) |
| 행동관찰 | JSON | observer, target_team, behaviors[{category, item, score}] |

앱 내 "양식 템플릿 다운로드" 버튼에서 샘플 파일 제공

---

## 결과물
- 화면 요약 (점수, 위험요인, 로드맵)
- Word 리포트 다운로드
- SharePoint List에 메타데이터 자동 저장
- SharePoint 문서 라이브러리에 리포트 파일 자동 업로드

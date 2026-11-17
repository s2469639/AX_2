# 개인 챗봇 과제 — 프로젝트 안내 (Claude 가 매번 읽어요)

## 목표
data/ 문서로 답하는 RAG 챗봇 웹앱. 자세한 요구사항: @과제_안내.md
디자인 규칙: @DESIGN.md
LangChain · LangGraph 사용법 메모: @../조사노트.md

## 기술
- Python 3.11 이상 (설치할 패키지는 requirements.txt 에 적기)
- 모델: OpenAI API — 대화 `OPENAI_MODEL` · 임베딩 `OPENAI_EMBED_MODEL` (기본값은 .env.example 에서 확인. 대화 모델 이름이 실제로 있는지는 확인 필요)
- LangChain · LangGraph 사용법: 조사노트에서 "확인 필요"로 표시된 import 는 쓰기 전에 설치된 버전에서 직접 불러 봐서 확인하기
- 보안 · 키 · 비용 호출 규칙은 `.claude/rules/security.md` 를 따르기

## 폴더 구조
- `data/` — 챗봇이 읽을 (가상) 연습 문서
- `ingest.py` — data/ 문서를 잘라 임베딩해서 저장 (아직 없으면 새로 만들기)
- `app.py` — Streamlit 챗봇 화면 (아직 없으면 새로 만들기)
- `.env.example` — 필요한 변수 이름 목록 (값은 비어 있음. 실제 값은 내가 .env 에 직접 넣기)

## 작업 방식
- 파일 2개 이상 수정 · 새 패키지 추가 · 모델 변경 전에는 계획부터 보여 주기
- 한 번에 파일 하나씩, 바꾼 내용 3줄 요약
- 주석은 한국어로: 함수마다 무엇을 하는지 한 줄, 전문용어는 괄호로 쉬운 말 풀이

## 비용 규칙
- `python ingest.py` 를 다시 돌리면 임베딩 호출이 다시 일어나 비용이 들어요. 꼭 필요할 때만 실행하기
- 임베딩 모델(`OPENAI_EMBED_MODEL`)을 바꾸면 저장해 둔 것을 전부 다시 만들어야 해요. 바꾸기 전에 먼저 알려 주기
- 하루 · 월 사용 한도: 확인 필요 (정하면 여기에 적기)

## 실행
- 처음 한 번 (Windows): `python -m venv .venv` → `.venv\Scripts\activate` → `pip install -r requirements.txt`
- `.env.example` 을 `.env` 로 복사하고 키는 내가 직접 넣기
- 문서 넣기: `python ingest.py`
- 앱 실행: `streamlit run app.py`

## 확인 방법
- 앱을 띄워 data/ 문서에 있는 내용을 질문 1개 해 보고, 답변 아래에 출처가 작은 회색 글씨로 나오는지 보기
- 키가 없거나 data/ 가 비어 있으면 앱이 이유를 한국어로 안내해야 해요 (자동 재시도는 하지 않기)

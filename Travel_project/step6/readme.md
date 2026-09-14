# ✈️ All-in-One Travel Dashboard

Streamlit 기반의 다기능 여행 정보 통합 대시보드입니다.  
국내외 실시간 날씨, 스프레드가 적용된 정밀 환율 계산기, 실시간 시차 비교, 그리고 카카오맵api 기반의 스마트 위치 검색 및 주변 편의시설 탐색 기능을 제공합니다.

---

## 📌 주요 기능

### 1. 🇰🇷 대한민국 여행 센터 (Home)
- **실시간 날씨 위젯:** 서울, 부산, 제주 3개 주요 거점의 실시간 기온, 체감 온도, 습도 시각화
- **스마트 카카오 지도:**
  - **하이브리드 모드 지원:** 드래그/줌이 자유로운 **인터랙티브 지도** & 가볍고 깔끔한 **정적 지도(Static Map)** 전환 가능
  - **장소 검색 & 선택:** 키워드 검색 시 상위 장소 리스트를 제공하여 원하는 지점으로 정밀 이동
  - **주변 편의시설 탐색:** 선택 위치 반경 1.5km 내 **식당(FD6)**, **카페(CE7)**, **편의점(CS2)** 마커 표시 및 상세 정보 팝업
- **공식 링크 연동:** 대한민국 구석구석(한국관광공사) 공식 웹사이트 연결

### 2. 🌐 해외 여행 가이드 (일본 / 중국 / 미국)
- **실시간 시차 비교:** 한국(서울) 시간을 기준으로 현지 시간 및 시차(+/- 시간)를 실시간 카드 형태로 직관적 비교 (미국은 뉴욕/LA 동시 지원)
- **즉시 환율 & 계산기:**
  - 페이지 진입 즉시 매매기준율 및 현찰 살 때/팔 때(스프레드 1.75% 기본 반영) 환율 노출
  - 원화 ➡️ 외화, 외화 ➡️ 원화 양방향 간편 환전 계산기 탑재
- **현지 실시간 기후 카드:** 고시인성 그라데이션 카드로 주요 거점 날씨 안내
- **공식 관광청 연동:** 일본(JNTO), 중국(문화여유부), 미국(Go USA) 공식 포털 바로가기

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend / Framework:** `Streamlit` (`st.Page`, `st.navigation`)
- **Language:** Python 3.10+
- **API & Network:** `requests`, `python-dotenv`
- **Timezone:** Python 내장 `zoneinfo` (IANA Time Zone Database)
- **External APIs:**
  - **OpenWeatherMap API:** 실시간 글로벌 날씨 조회
  - **ExchangeRate-API:** 실시간 외환 환율 데이터 수집
  - **Kakao Map JavaScript SDK & Local REST API:** 위치 검색, 카테고리 시설 수집 및 반응형 맵 렌더링

---

## 📂 프로젝트 구조 (Directory Structure)

```text
AX_2/
├── .env                              # 외부 환경변수 (API 키 관리)
└── Travel_project/
    └── step6/
        ├── .streamlit/
        │   └── config.toml           # 스트림릿 테마 및 서버 설정
        ├── src/
        │   ├── api/
        │   │   ├── weather.py        # OpenWeather 날씨 API 모듈
        │   │   └── exchange.py       # 환율 수집 API 모듈
        │   ├── components/
        │   │   └── ui.py             # 시차 비교, 날씨 카드, 즉시 환율 계산 위젯
        │   └── pages/
        │       ├── home_korea.py     # 대한민국 홈 & 카카오 인터랙티브/정적 지도
        │       ├── japan.py          # 일본 여행 가이드
        │       ├── china.py          # 중국 여행 가이드
        │       └── usa.py            # 미국 여행 가이드 (시차 2곳 비교)
        ├── app.py                    # 멀티페이지 라우팅 및 엔트리포인트
        ├── requirements.txt          # 의존성 라이브러리 목록
        └── README.md                 # 프로젝트 문서
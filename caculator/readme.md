# ✈️ All-in-One Travel Dashboard

날씨 확인, 실시간 환율 계산, 주요 관광지 추천 기능을 한 화면에서 제공하는 인터랙티브 스트림릿(Streamlit) 여행 정보 웹 애플리케이션입니다.

## 📌 주요 기능 (Features)
- **실시간 날씨 정보:** OpenWeatherMap API를 연동하여 선택한 도시의 현재 기온, 날씨 상태, 습도 등을 실시간으로 제공
- **여행 환율 계산기:** 실시간 환율 API를 활용해 원화(KRW)와 여행지 현지 통화 간 상호 환산 기능 제공
- **주요 관광지 및 명소 추천:** 도시별 대표 랜드마크, 추천 맛집, 여행 팁 안내

## 🛠️ 기술 스택 (Tech Stack)
- **Language:** Python
- **Framework:** Streamlit
- **Library:** `requests`, `python-dotenv`

## ⚙️ 사전 준비 및 설치 방법 (Installation)

1. **필수 라이브러리 설치**
   ```bash
   pip install requests python-dotenv streamlit

   ## 📌 주요 기능 (Features)
- **실시간 날씨 정보:** OpenWeatherMap API를 연동하여 선택한 도시의 현재 기온, 체감 온도, 습도, 날씨 아이콘 제공
- **현찰 매수/매도 환율 계산기:** 
  - 실시간 매매기준율 조회
  - 은행 현찰 살 때(매수율) 및 팔 때(매도율) 스프레드 반영 계산
  - 여행 전 환전 금액(KRW ➡️ 외화) 및 귀국 후 재환전 금액(외화 ➡️ KRW) 양방향 산출
- **현지 관광 명소 & 맛집 가이드:** 도시별 필수 랜드마크 리스트 및 현지 유명 맛집, 대표 메뉴, 방문 팁 제공
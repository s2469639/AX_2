import streamlit as st
from src.api.weather import get_weather
from src.api.exchange import get_exchange_rates
from src.components.ui import render_official_link, render_weather_card, render_instant_exchange_widget, render_time_difference

st.title("🍕 미국 여행 가이드 (USA)")
render_official_link("Go USA (미국 공식 관광청)", "https://www.gousa.or.kr")
st.markdown("<br>", unsafe_allow_html=True)

# 1. 한국-미국 시차 및 실시간 시각 비교 (뉴욕 & LA)
render_time_difference("미국", [
    {"label": "🗽 뉴욕 (동부)", "tz": "America/New_York"},
    {"label": "🌴 로스앤젤레스 (서부)", "tz": "America/Los_Angeles"}
])

# 2. 날씨 & 즉시 환율 대시보드
col_w, col_e = st.columns([1, 1])

with col_w:
    st.markdown("##### 🌤️ 실시간 기후 (뉴욕)")
    render_weather_card(get_weather("New York"), "뉴욕 (New York)")

with col_e:
    st.markdown("##### 💵 달러(USD) 실시간 환율")
    rates = get_exchange_rates("USD")
    base_usd = rates.get("KRW", 1380.0) if isinstance(rates, dict) and "KRW" in rates else 1380.0
    render_instant_exchange_widget("USD", base_usd)

st.divider()
st.subheader("🗽 추천 도시 & 명소")
t1, t2, t3 = st.tabs(["뉴욕", "로스앤젤레스", "라스베이거스"])
with t1:
    st.markdown("- **센트럴 파크 & 타임스스퀘어:** 뉴욕 도심의 상징적인 랜드마크")
    st.markdown("- **덤보 & 브루클린 브릿지:** 맨해튼 스카이라인 사진 명소")
with t2:
    st.markdown("- **산타모니카 피어 & 베니스 비치:** 캘리포니아 해변과 노을 산책로")
    st.markdown("- **그리피스 천문대:** LA 전경과 야경을 한눈에 담는 관측소")
with t3:
    st.markdown("- **라스베이거스 스트립:** 벨라지오 분수 쇼 및 세계적 테마 호텔 거리")
    st.markdown("- **그랜드 캐니언 국립공원:** 일일 투어 및 헬리콥터 투어 거점")
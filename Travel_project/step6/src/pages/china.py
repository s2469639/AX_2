import streamlit as st
from src.api.weather import get_weather
from src.api.exchange import get_exchange_rates
from src.components.ui import render_official_link, render_weather_card, render_instant_exchange_widget, render_time_difference

st.title("🥟 중국 여행 가이드 (China)")
render_official_link("중국 문화여유부", "https://www.travelchina.gov.cn")
st.markdown("<br>", unsafe_allow_html=True)

# 1. 시차 비교
render_time_difference("중국", [
    {"label": "🏮 베이징 (Beijing)", "tz": "Asia/Shanghai"}
])

# 2. 날씨 & 환율
col_w, col_e = st.columns([1, 1])

with col_w:
    st.markdown("##### 🌤️ 실시간 기후 (베이징)")
    render_weather_card(get_weather("Beijing"), "베이징 (Beijing)")

with col_e:
    st.markdown("##### 💴 위안화(CNY) 실시간 환율")
    rates = get_exchange_rates("CNY")
    base_cny = rates.get("KRW", 190.0) if isinstance(rates, dict) and "KRW" in rates else 190.0
    render_instant_exchange_widget("CNY", base_cny)

st.divider()
st.subheader("🏯 추천 도시 & 명소")
t1, t2, t3 = st.tabs(["베이징", "상하이", "청두"])
with t1:
    st.markdown("- **자금성(고궁):** 명·청 황제의 대궁전 (사전 온라인 예약 필수)")
    st.markdown("- **만리장성(무톈위):** 케이블카를 이용해 장엄한 능선을 조망하는 코스")
with t2:
    st.markdown("- **와이탄 & 동방명주:** 황푸강을 따라 펼쳐지는 근대 건축과 현대식 마천루")
    st.markdown("- **예원 & 예원상장:** 전통 정원과 샤오롱바오 맛집 거리")
with t3:
    st.markdown("- **자이언트 판다 번식연구기지:** 귀여운 판다를 직접 관람하는 인기 명소")
    st.markdown("- **진리 거리:** 쓰촨 마라 훠궈와 전통 길거리 간식 체험")
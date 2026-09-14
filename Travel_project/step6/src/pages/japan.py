import streamlit as st
from src.api.weather import get_weather
from src.api.exchange import get_exchange_rates
from src.components.ui import render_official_link, render_weather_card, render_instant_exchange_widget, render_time_difference

st.title("🍣 일본 여행 가이드 (Japan)")
render_official_link("일본 정부 관광국(JNTO)", "https://www.japan.travel/ko/kr/")
st.markdown("<br>", unsafe_allow_html=True)

# 1. 시차 비교
render_time_difference("일본", [
    {"label": "🗼 도쿄 (Tokyo)", "tz": "Asia/Tokyo"}
])

# 2. 날씨 & 환율
col_w, col_e = st.columns([1, 1])

with col_w:
    st.markdown("##### 🌤️ 실시간 기후 (도쿄)")
    render_weather_card(get_weather("Tokyo"), "도쿄 (Tokyo)")

with col_e:
    st.markdown("##### 💴 엔화(JPY) 실시간 환율 (100 JPY 기준)")
    rates = get_exchange_rates("JPY")
    # 100엔당 원화 환율 환산
    base_jpy = (rates.get("KRW", 8.9) * 100) if isinstance(rates, dict) and "KRW" in rates else 890.0
    render_instant_exchange_widget("100 JPY", base_jpy)

st.divider()
st.subheader("🍱 추천 도시 & 랜드마크")
t1, t2, t3 = st.tabs(["도쿄", "오사카 & 교토", "후쿠오카"])
with t1:
    st.markdown("- **시부야 & 신주쿠:** 스크램블 교차로와 전망대, 트렌디한 쇼핑가")
    st.markdown("- **아사쿠사 센소지:** 도쿄에서 가장 유서 깊은 사찰과 먹거리 골목")
with t2:
    st.markdown("- **도톤보리:** 글리코상 야경과 타코야키 미식 투어")
    st.markdown("- **후시미 이나리 신사:** 붉은 토리이 터널로 유명한 명소")
with t3:
    st.markdown("- **하카타 라멘:** 진한 돈코츠 라멘 원조 맛집 투어")
    st.markdown("- **유후인 온천 마을:** 힐링 료칸 및 킨린 호수 산책")
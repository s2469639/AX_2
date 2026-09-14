import streamlit as st
from src.api.weather import get_weather
from src.api.exchange import get_exchange_rates
from src.components.ui import render_weather_card, render_instant_exchange_widget, render_time_difference

st.title("🌐 기타 국가/도시 검색 (Global Search)")
st.caption("궁금한 국가나 수도를 검색해 실시간 날씨, 환율, 시차 정보를 한눈에 확인하세요.")

# 주요 글로벌 국가/도시 메타데이터베이스
GLOBAL_REGIONS = [
    {"country_kr": "영국", "country_en": "United Kingdom", "city": "London", "city_kr": "런던", "curr": "GBP", "tz": "Europe/London", "flag": "🇬🇧"},
    {"country_kr": "프랑스", "country_en": "France", "city": "Paris", "city_kr": "파리", "curr": "EUR", "tz": "Europe/Paris", "flag": "🇫🇷"},
    {"country_kr": "독일", "country_en": "Germany", "city": "Berlin", "city_kr": "베를린", "curr": "EUR", "tz": "Europe/Berlin", "flag": "🇩🇪"},
    {"country_kr": "이탈리아", "country_en": "Italy", "city": "Rome", "city_kr": "로마", "curr": "EUR", "tz": "Europe/Rome", "flag": "🇮🇹"},
    {"country_kr": "스위스", "country_en": "Switzerland", "city": "Zurich", "city_kr": "취리히", "curr": "CHF", "tz": "Europe/Zurich", "flag": "🇨🇭"},
    {"country_kr": "스페인", "country_en": "Spain", "city": "Madrid", "city_kr": "마드리드", "curr": "EUR", "tz": "Europe/Madrid", "flag": "🇪🇸"},
    {"country_kr": "호주", "country_en": "Australia", "city": "Sydney", "city_kr": "시드니", "curr": "AUD", "tz": "Australia/Sydney", "flag": "🇦🇺"},
    {"country_kr": "캐나다", "country_en": "Canada", "city": "Toronto", "city_kr": "토론토", "curr": "CAD", "tz": "America/Toronto", "flag": "🇨🇦"},
    {"country_kr": "베트남", "country_en": "Vietnam", "city": "Hanoi", "city_kr": "하노이", "curr": "VND", "tz": "Asia/Ho_Chi_Minh", "flag": "🇻🇳"},
    {"country_kr": "태국", "country_en": "Thailand", "city": "Bangkok", "city_kr": "방콕", "curr": "THB", "tz": "Asia/Bangkok", "flag": "🇹🇭"},
    {"country_kr": "싱가포르", "country_en": "Singapore", "city": "Singapore", "city_kr": "싱가포르", "curr": "SGD", "tz": "Asia/Singapore", "flag": "🇸🇬"},
    {"country_kr": "대만", "country_en": "Taiwan", "city": "Taipei", "city_kr": "타이베이", "curr": "TWD", "tz": "Asia/Taipei", "flag": "🇹🇼"},
    {"country_kr": "홍콩", "country_en": "Hong Kong", "city": "Hong Kong", "city_kr": "홍콩", "curr": "HKD", "tz": "Asia/Hong_Kong", "flag": "🇭🇰"},
    {"country_kr": "필리핀", "country_en": "Philippines", "city": "Manila", "city_kr": "마닐라", "curr": "PHP", "tz": "Asia/Manila", "flag": "🇵🇭"},
    {"country_kr": "말레이시아", "country_en": "Malaysia", "city": "Kuala Lumpur", "city_kr": "쿠알라룸푸르", "curr": "MYR", "tz": "Asia/Kuala_Lumpur", "flag": "🇲🇾"},
    {"country_kr": "인도네시아", "country_en": "Indonesia", "city": "Jakarta", "city_kr": "자카르타", "curr": "IDR", "tz": "Asia/Jakarta", "flag": "🇮🇩"},
    {"country_kr": "튀르키예", "country_en": "Turkey", "city": "Istanbul", "city_kr": "이스탄불", "curr": "TRY", "tz": "Europe/Istanbul", "flag": "🇹🇷"},
    {"country_kr": "아랍에미리트", "country_en": "UAE", "city": "Dubai", "city_kr": "두바이", "curr": "AED", "tz": "Asia/Dubai", "flag": "🇦🇪"},
    {"country_kr": "뉴질랜드", "country_en": "New Zealand", "city": "Auckland", "city_kr": "오클랜드", "curr": "NZD", "tz": "Pacific/Auckland", "flag": "🇳🇿"}
]

# 검색창 및 드롭다운 선택 UI
col_search, col_pick = st.columns([2, 1])

with col_search:
    query = st.text_input("🔍 국가명 또는 도시 검색 (예: 프랑스, 런던, Vietnam 등)", placeholder="검색어 입력")

# 검색 필터링
matched = []
if query.strip():
    q = query.strip().lower()
    matched = [
        item for item in GLOBAL_REGIONS
        if q in item["country_kr"].lower() or q in item["country_en"].lower() or q in item["city"].lower() or q in item["city_kr"].lower()
    ]

# 검색 결과가 있으면 검색 결과 우선, 없으면 전체 목록 선택
with col_pick:
    if matched:
        options = [f"{m['flag']} {m['country_kr']} ({m['city_kr']})" for m in matched]
        picked_idx = st.selectbox("🎯 검색된 국가 목록", range(len(options)), format_func=lambda x: options[x])
        selected_data = matched[picked_idx]
    else:
        if query.strip():
            st.warning("일치하는 국가를 찾지 못해 전체 목록에서 선택합니다.")
        options = [f"{m['flag']} {m['country_kr']} ({m['city_kr']})" for m in GLOBAL_REGIONS]
        picked_idx = st.selectbox("📌 전체 국가 선택", range(len(options)), format_func=lambda x: options[x])
        selected_data = GLOBAL_REGIONS[picked_idx]

st.divider()

# --- 결과 대시보드 렌더링 ---
country_title = f"{selected_data['flag']} {selected_data['country_kr']} - {selected_data['city_kr']} ({selected_data['city']})"
st.subheader(country_title)

# 1. 한국과의 시차 및 실시간 시계
render_time_difference(selected_data["country_kr"], [
    {"label": f"{selected_data['flag']} {selected_data['city_kr']}", "tz": selected_data["tz"]}
])

# 2. 실시간 날씨 & 환율
col_w, col_e = st.columns([1, 1])

with col_w:
    st.markdown(f"##### 🌤️ 실시간 날씨 ({selected_data['city_kr']})")
    weather_info = get_weather(selected_data["city"])
    render_weather_card(weather_info, f"{selected_data['city_kr']} ({selected_data['city']})")

with col_e:
    curr_code = selected_data["curr"]
    st.markdown(f"##### 💱 {curr_code} 실시간 환율")
    rates = get_exchange_rates(curr_code)
    
    # 1 단위당 KRW 매매기준율 추출
    if isinstance(rates, dict) and "KRW" in rates:
        base_rate = rates["KRW"]
    else:
        base_rate = 1.0

    # 동남아 등 통화 단위가 작은 경우(VND, IDR 등 100단위 표기 편의)
    if curr_code in ["VND", "IDR"]:
        base_rate = base_rate * 100
        render_instant_exchange_widget(f"100 {curr_code}", base_rate)
    else:
        render_instant_exchange_widget(curr_code, base_rate)
import streamlit as st
from src.api.weather import get_weather
from src.api.kakao import search_places_kakao, search_category_kakao
from src.components.kakao_map import render_kakao_map

st.title("🇰🇷 대한민국 여행 센터 (Home)")
st.link_button("🌐 대한민국 구석구석 (한국관광공사 공식)", "https://korean.visitkorea.or.kr")
st.write("")

# 1. 상단 날씨 섹션
st.markdown("#### 🌤️ 국내 주요 거점 실시간 날씨")
w1, w2, w3 = st.columns(3)

def display_weather_metric(col, city_name, data):
    with col:
        if data and "main" in data:
            temp = data["main"].get("temp", "-")
            weather_desc = data["weather"][0].get("description", "") if data.get("weather") else ""
            humidity = data["main"].get("humidity", "-")
            st.metric(label=city_name, value=f"{temp}°C", delta=weather_desc)
            st.caption(f"습도: {humidity}%")
        else:
            st.metric(label=city_name, value="정보 없음")

display_weather_metric(w1, "서울 (Seoul)", get_weather("Seoul"))
display_weather_metric(w2, "부산 (Busan)", get_weather("Busan"))
display_weather_metric(w3, "제주 (Jeju)", get_weather("Jeju"))

st.divider()

# 2. 지도 및 탐색 섹션 (좌측: 검색 및 목록 / 우측: 지도)
st.markdown("#### 🗺️ 대한민국 스마트 맵 & 장소 탐색")

preset_spots = {
    "경복궁": {"lat": 37.5796, "lng": 126.9770, "address": "서울 종로구 사직로 161", "url": "https://place.map.kakao.com/8129210"},
    "해운대 해수욕장": {"lat": 35.1587, "lng": 129.1604, "address": "부산 해운대구 우동", "url": "https://place.map.kakao.com/8051280"},
    "성산일출봉": {"lat": 33.4585, "lng": 126.9427, "address": "제주 서귀포시 성산읍 일출로 284-12", "url": "https://place.map.kakao.com/8119865"}
}

col_left, col_right = st.columns([5, 7], gap="medium")

# --- 좌측 패널 ---
with col_left:
    st.subheader("🔍 장소 탐색")
    user_query = st.text_input("직접 검색", placeholder="예: 강남역, 명동교자 입력 후 Enter")
    preset_choice = st.selectbox("추천 명소 빠른 선택", list(preset_spots.keys()))

    target_lat = preset_spots[preset_choice]["lat"]
    target_lng = preset_spots[preset_choice]["lng"]
    target_name = preset_choice
    target_addr = preset_spots[preset_choice]["address"]
    target_url = preset_spots[preset_choice]["url"]

    # 키워드 검색 결과 처리
    if user_query.strip():
        search_res = search_places_kakao(user_query.strip())
        if search_res:
            options = [f"{idx+1}. {item['name']} ({item['address']})" for idx, item in enumerate(search_res)]
            picked_str = st.selectbox("🎯 검색 결과 목록", options)
            picked_idx = options.index(picked_str)
            picked = search_res[picked_idx]

            target_lat = picked["lat"]
            target_lng = picked["lng"]
            target_name = picked["name"]
            target_addr = picked["address"]
            target_url = picked.get("url", "")
        else:
            st.warning("검색 결과가 없어 기본 선택 장소로 유지합니다.")

    # 선택된 장소 정보 카드 (순수 Streamlit 컨테이너)
    with st.container(border=True):
        st.caption("선택된 중심 장소")
        st.markdown(f"### 📍 {target_name}")
        st.write(f"**주소:** {target_addr}")
        if target_url:
            st.link_button("카카오맵 상세 정보 보기 ↗", target_url)

    # 주변 편의시설 필터
    selected_cat = st.radio(
        "주변 편의시설 필터링 (반경 1.5km)",
        ["선택 안 함", "🍴 식당 (맛집)", "☕ 카페", "🏪 편의점"],
        horizontal=True
    )

    cat_codes = {"🍴 식당 (맛집)": "FD6", "☕ 카페": "CE7", "🏪 편의점": "CS2"}
    nearby_list = []
    if selected_cat in cat_codes:
        nearby_list = search_category_kakao(cat_codes[selected_cat], target_lat, target_lng)

    # 탐색된 주변 시설 목록 뷰
    if nearby_list:
        st.markdown(f"**주변 탐색 결과 ({len(nearby_list)}곳)**")
        with st.container(height=260):
            for idx, p in enumerate(nearby_list, 1):
                dist = f"({p['distance']}m)" if p.get("distance") else ""
                with st.expander(f"{idx}. {p['name']} {dist}"):
                    st.write(f"주소: {p['address']}")
                    if p.get("phone"):
                        st.write(f"전화: {p['phone']}")
                    if p.get("url"):
                        st.link_button("카카오맵 열기", p["url"])

# --- 우측 패널 (순수 지도) ---
with col_right:
    st.subheader("🗺️ 실시간 지도 뷰")
    st.caption("🔴 중심 장소 | 🔵 주변 시설 (마우스 호버 시 상세 정보 표시)")
    
    render_kakao_map(
        lat=target_lat,
        lng=target_lng,
        name=target_name,
        addr=target_addr,
        places=nearby_list,
        is_interactive=True
    )
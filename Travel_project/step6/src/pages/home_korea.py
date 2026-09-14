import os
import sys
import json
from pathlib import Path
import requests
import streamlit as st
import streamlit.components.v1 as components

# 1. 실행 환경 경로 보정 (모듈 임포트 실패 방지)
CURRENT_FILE = Path(__file__).resolve()
STEP6_DIR = CURRENT_FILE.parent.parent.parent
if str(STEP6_DIR) not in sys.path:
    sys.path.insert(0, str(STEP6_DIR))

# =========================================================
# 2. API 통신 함수 (외부 파일 의존 없이 안전하게 내장)
# =========================================================
def get_weather(city_name: str):
    """OpenWeather 실시간 날씨 API 조회"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None

def search_places_kakao(keyword: str):
    """카카오 로컬 키워드 검색 REST API"""
    api_key = os.getenv("KAKAO_REST_KEY") or os.getenv("MAP_API_KEY")
    if not api_key:
        return []
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": keyword, "size": 5}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            return [{
                "name": d.get("place_name"),
                "address": d.get("road_address_name") or d.get("address_name"),
                "phone": d.get("phone", ""),
                "lat": float(d.get("y")),
                "lng": float(d.get("x")),
                "url": d.get("place_url", "")
            } for d in docs]
    except Exception:
        pass
    return []

def search_category_kakao(cat_code: str, lat: float, lng: float, radius: int = 1500):
    """카카오 로컬 카테고리(식당/카페/편의점) 검색 REST API"""
    api_key = os.getenv("KAKAO_REST_KEY") or os.getenv("MAP_API_KEY")
    if not api_key:
        return []
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {
        "category_group_code": cat_code,
        "x": str(lng),
        "y": str(lat),
        "radius": radius,
        "size": 15,
        "sort": "distance"
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            docs = res.json().get("documents", [])
            return [{
                "name": d.get("place_name"),
                "address": d.get("road_address_name") or d.get("address_name"),
                "phone": d.get("phone", ""),
                "distance": d.get("distance", ""),
                "lat": float(d.get("y")),
                "lng": float(d.get("x")),
                "url": d.get("place_url", "")
            } for d in docs]
    except Exception:
        pass
    return []

# =========================================================
# 3. 진짜 카카오 지도 렌더러 (정석 components.html 사용)
# =========================================================
def render_kakao_map(js_key: str, lat: float, lng: float, name: str, addr: str, places: list):
    """
    정석 components.html과 HTTPS 승격 메타 태그를 적용하여
    Streamlit Cloud 배포 환경에서도 차단 없이 카카오 지도를 출력합니다.
    """
    places_json = json.dumps(places, ensure_ascii=False)

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="always">
    <!-- 핵심: iframe 내부에서 발생하는 모든 http 호출을 https로 자동 승격하여 차단 방지 -->
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    <style>
        * {{ box-sizing: border-box; }}
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", sans-serif; }}
        #map {{ width: 100%; height: 580px; border-radius: 12px; border: 1px solid #cbd5e1; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey={js_key}&autoload=false';
        
        script.onload = function() {{
            kakao.maps.load(function() {{
                var container = document.getElementById('map');
                var center = new kakao.maps.LatLng({lat}, {lng});
                var map = new kakao.maps.Map(container, {{ center: center, level: 4 }});

                map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
                map.addControl(new kakao.maps.MapTypeControl(), kakao.maps.ControlPosition.TOPRIGHT);

                // 1. 기준 중심 장소 마커 및 정보창
                var mainMarker = new kakao.maps.Marker({{ position: center, map: map }});
                var mainIw = new kakao.maps.InfoWindow({{
                    position: center,
                    content: '<div style="padding:8px 12px;font-size:12px;min-width:180px;line-height:1.4;">' +
                             '<strong style="color:#e11d48;font-size:13px;">📍 {name}</strong><br>' +
                             '<span style="color:#475569;">{addr}</span></div>'
                }});
                mainIw.open(map, mainMarker);

                // 2. 주변 편의시설 마커 목록
                var places = {places_json};
                if (places && places.length > 0) {{
                    var bounds = new kakao.maps.LatLngBounds();
                    bounds.extend(center);
                    var activeIw = null;

                    places.forEach(function(p) {{
                        var pos = new kakao.maps.LatLng(p.lat, p.lng);
                        bounds.extend(pos);
                        var marker = new kakao.maps.Marker({{ position: pos, map: map }});

                        var infoHtml = '<div style="padding:8px 10px;font-size:12px;max-width:220px;line-height:1.4;">' +
                                       '<b>' + p.name + '</b><br>' +
                                       '<span style="font-size:11px;color:#64748b;">' + p.address + '</span><br>' +
                                       (p.phone ? '<span style="color:#059669;font-size:11px;">📞 ' + p.phone + '</span><br>' : '') +
                                       (p.url ? '<a href="' + p.url + '" target="_blank" style="color:#2563eb;font-weight:bold;font-size:11px;text-decoration:none;">상세보기 ↗</a>' : '') +
                                       '</div>';

                        var iw = new kakao.maps.InfoWindow({{ content: infoHtml, removable: true }});
                        kakao.maps.event.addListener(marker, 'click', function() {{
                            if (activeIw) activeIw.close();
                            iw.open(map, marker);
                            activeIw = iw;
                        }});
                    }});
                    map.setBounds(bounds);
                }}
            }});
        }};
        document.head.appendChild(script);
    </script>
</body>
</html>"""
    
    # st.iframe 대신 정식 Streamlit 컴포넌트인 components.html 사용
    components.html(html_code, height=600)

# =========================================================
# 4. Streamlit 메인 화면 UI 구성
# =========================================================
st.title("🇰🇷 대한민국 여행 센터 (Home)")
st.link_button("🌐 대한민국 구석구석 (한국관광공사 공식)", "https://korean.visitkorea.or.kr")
st.write("")

# 4-1. 날씨 섹션
st.markdown("#### 🌤️ 국내 주요 거점 실시간 날씨")
w1, w2, w3 = st.columns(3)

def show_weather(col, city_name, data):
    with col:
        if data and "main" in data:
            st.metric(
                label=city_name,
                value=f"{data['main'].get('temp', '-')}°C",
                delta=data["weather"][0].get("description", "") if data.get("weather") else ""
            )
            st.caption(f"습도: {data['main'].get('humidity', '-')}%")
        else:
            st.metric(label=city_name, value="연결 대기중")

show_weather(w1, "서울 (Seoul)", get_weather("Seoul"))
show_weather(w2, "부산 (Busan)", get_weather("Busan"))
show_weather(w3, "제주 (Jeju)", get_weather("Jeju"))

st.divider()

# 4-2. 장소 탐색 및 카카오 지도 섹션
st.markdown("#### 🗺️ 카카오 지도 & 스마트 장소 탐색")

preset_spots = {
    "경복궁": {"lat": 37.5796, "lng": 126.9770, "address": "서울 종로구 사직로 161", "url": "https://place.map.kakao.com/8129210"},
    "해운대 해수욕장": {"lat": 35.1587, "lng": 129.1604, "address": "부산 해운대구 우동", "url": "https://place.map.kakao.com/8051280"},
    "성산일출봉": {"lat": 33.4585, "lng": 126.9427, "address": "제주 서귀포시 성산읍 일출로 284-12", "url": "https://place.map.kakao.com/8119865"}
}

col_left, col_right = st.columns([5, 7], gap="medium")

# --- 좌측: 검색 및 필터 패널 ---
with col_left:
    st.subheader("🔍 장소 탐색")
    user_query = st.text_input("직접 검색", placeholder="예: 강남역, 성수동 맛집 입력 후 Enter")
    preset_choice = st.selectbox("추천 명소 빠른 선택", list(preset_spots.keys()))

    target_lat = preset_spots[preset_choice]["lat"]
    target_lng = preset_spots[preset_choice]["lng"]
    target_name = preset_choice
    target_addr = preset_spots[preset_choice]["address"]
    target_url = preset_spots[preset_choice]["url"]

    # 키워드 검색 실행
    if user_query.strip():
        search_res = search_places_kakao(user_query.strip())
        if search_res:
            opts = [f"{i+1}. {item['name']} ({item['address']})" for i, item in enumerate(search_res)]
            picked_str = st.selectbox("🎯 검색 결과 목록", opts)
            picked = search_res[opts.index(picked_str)]
            target_lat, target_lng = picked["lat"], picked["lng"]
            target_name, target_addr = picked["name"], picked["address"]
            target_url = picked.get("url", "")
        else:
            st.warning("검색 결과가 없어 기본 선택 장소를 유지합니다.")

    # 선택된 장소 요약 카드
    with st.container(border=True):
        st.caption("선택된 중심 장소")
        st.markdown(f"### 📍 {target_name}")
        st.write(f"**주소:** {target_addr}")
        if target_url:
            st.link_button("카카오맵 상세 정보 보기 ↗", target_url)

    # 카테고리 필터
    selected_cat = st.radio(
        "주변 편의시설 필터링 (반경 1.5km)",
        ["선택 안 함", "🍴 식당 (맛집)", "☕ 카페", "🏪 편의점"],
        horizontal=True
    )

    cat_map = {"🍴 식당 (맛집)": "FD6", "☕ 카페": "CE7", "🏪 편의점": "CS2"}
    nearby_list = []
    if selected_cat in cat_map:
        nearby_list = search_category_kakao(cat_map[selected_cat], target_lat, target_lng)

    # 주변 목록 리스트
    if nearby_list:
        st.markdown(f"**주변 시설 결과 ({len(nearby_list)}곳)**")
        with st.container(height=260):
            for i, p in enumerate(nearby_list, 1):
                dist = f"({p['distance']}m)" if p.get("distance") else ""
                with st.expander(f"{i}. {p['name']} {dist}"):
                    st.write(f"주소: {p['address']}")
                    if p.get("phone"):
                        st.write(f"전화: {p['phone']}")
                    if p.get("url"):
                        st.link_button("카카오맵 열기", p["url"])

# --- 우측: 진짜 카카오 지도 뷰 ---
with col_right:
    st.subheader("🗺️ 카카오 지도 뷰")
    kakao_js_key = os.getenv("MAP_API_KEY", "")
    
    if kakao_js_key:
        render_kakao_map(
            js_key=kakao_js_key,
            lat=target_lat,
            lng=target_lng,
            name=target_name,
            addr=target_addr,
            places=nearby_list
        )
    else:
        st.error("카카오 지도 JavaScript 키(MAP_API_KEY)가 등록되지 않았습니다.")
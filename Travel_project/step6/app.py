import os
import sys
import json
import base64
from pathlib import Path
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# -------------------------------------------------------------
# 1. 환경변수(.env) 및 Secrets 안전 로드
# -------------------------------------------------------------
load_dotenv()

def get_key(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        try:
            val = st.secrets.get(name, "")
        except Exception:
            val = ""
    return (val or "").strip()

OPENWEATHER_API_KEY = get_key("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = get_key("EXCHANGERATE_API_KEY") or get_key("EXCHANGE_API_KEY")
KAKAO_REST_API_KEY = get_key("KAKAO_REST_API_KEY") or get_key("KAKAO_REST_KEY")
KAKAO_JS_API_KEY = get_key("KAKAO_JS_API_KEY") or get_key("MAP_API_KEY")

st.set_page_config(
    page_title="Travel App",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2. 로컬 폰트(에이투지체) Base64 로드 & 라벤더 글래스 UI CSS
# -------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

def get_font_base64(font_filename: str) -> str:
    font_path = BASE_DIR / font_filename
    if font_path.exists():
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

font_regular_b64 = get_font_base64("에이투지체-4Regular.ttf")
font_semibold_b64 = get_font_base64("에이투지체-6SemiBold.ttf")

font_face_css = ""
if font_regular_b64:
    font_face_css += f"""
    @font-face {{
        font-family: 'A2Z-Regular';
        src: url(data:font/truetype;charset=utf-8;base64,{font_regular_b64}) format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    """
if font_semibold_b64:
    font_face_css += f"""
    @font-face {{
        font-family: 'A2Z-SemiBold';
        src: url(data:font/truetype;charset=utf-8;base64,{font_semibold_b64}) format('truetype');
        font-weight: 600;
        font-style: normal;
    }}
    """

custom_theme_css = f"""
<style>
{font_face_css}

/* 전역 폰트 및 라벤더 물빛 배경 */
html, body, [class*="css"], .stApp {{
    font-family: 'A2Z-Regular', -apple-system, sans-serif !important;
    background: linear-gradient(135deg, #f8f5ff 0%, #f1e9ff 50%, #e9ddfc 100%) !important;
    color: #2b1f3d !important;
}}

/* 제목 및 강조 텍스트는 SemiBold 적용 */
h1, h2, h3, h4, h5, .stHeading, .page-title, .spot-title, .weather-temp {{
    font-family: 'A2Z-SemiBold', sans-serif !important;
    color: #3b2359 !important;
}}

/* 사이드바 */
section[data-testid="stSidebar"] {{
    background-color: rgba(248, 244, 255, 0.85) !important;
    backdrop-filter: blur(14px);
    border-right: 1.5px solid rgba(215, 196, 245, 0.5);
}}

/* 라벤더 펄 버튼 */
.stButton > button {{
    font-family: 'A2Z-SemiBold', sans-serif !important;
    background: linear-gradient(135deg, #b99bf5 0%, #9a75e8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 16px !important;
    padding: 9px 18px !important;
    box-shadow: 0 4px 14px rgba(162, 127, 237, 0.35) !important;
    transition: all 0.2s ease-in-out !important;
    width: 100%;
}}
.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(162, 127, 237, 0.5) !important;
}}

/* 입력창 & 셀렉트박스 */
div[data-baseweb="input"], div[data-baseweb="select"] {{
    border-radius: 14px !important;
    background-color: rgba(255, 255, 255, 0.85) !important;
    border: 1.5px solid #d4c2f7 !important;
}}

/* 고대비 날씨 카드 (흰 바탕에서도 또렷함 보장) */
.weather-card {{
    background: rgba(255, 255, 255, 0.82);
    backdrop-filter: blur(10px);
    border: 1.5px solid #dcd0f7;
    border-radius: 18px;
    padding: 16px 20px;
    box-shadow: 0 8px 20px rgba(181, 155, 230, 0.2);
    margin-bottom: 12px;
}}
.weather-city {{
    font-family: 'A2Z-SemiBold', sans-serif;
    font-size: 14px;
    color: #6c46a8;
    margin-bottom: 2px;
}}
.weather-temp {{
    font-size: 30px;
    color: #241438;
    margin: 2px 0;
}}
.weather-desc-badge {{
    font-size: 12px;
    color: #583391;
    background: #eedfff;
    display: inline-block;
    padding: 2px 10px;
    border-radius: 10px;
    font-weight: bold;
}}
.weather-details {{
    font-size: 12px;
    color: #554469;
    margin-top: 6px;
    font-weight: 500;
}}

/* 플래너 스팟 카드 */
.spot-card {{
    background: rgba(255, 255, 255, 0.85);
    border: 1.5px solid #ded3f7;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 14px rgba(193, 172, 235, 0.15);
}}
.spot-tag {{
    display: inline-block;
    background: #f1e6ff;
    color: #6a3ab2;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-family: 'A2Z-SemiBold', sans-serif;
    margin-right: 4px;
}}
</style>
"""
st.markdown(custom_theme_css, unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. 플래너 JSON 로컬 영구 저장 (백엔드 불필요)
# -------------------------------------------------------------
PLAN_FILE = BASE_DIR / "travel_plans.json"

def load_saved_plans():
    if PLAN_FILE.exists():
        try:
            with open(PLAN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_plans(plans):
    try:
        with open(PLAN_FILE, "w", encoding="utf-8") as f:
            json.dump(plans, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

if "my_plan" not in st.session_state:
    st.session_state.my_plan = load_saved_plans()

# -------------------------------------------------------------
# 4. API 함수들
# -------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def kakao_search_place(query: str):
    if not KAKAO_REST_API_KEY:
        return None, "카카오 키 없음"
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": query, "size": 10}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("documents", []), None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=600, show_spinner=False)
def kakao_search_category(cat_code: str, lat: float, lon: float, radius: int = 1500):
    if not KAKAO_REST_API_KEY:
        return []
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"category_group_code": cat_code, "x": str(lon), "y": str(lat), "radius": radius, "size": 15, "sort": "distance"}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=600, show_spinner=False)
def get_weather_by_city(city_name: str):
    if not OPENWEATHER_API_KEY:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "kr"}
    try:
        res = requests.get(url, params=params, timeout=5)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_exchange_rate(base: str, target: str):
    if not EXCHANGERATE_API_KEY:
        return None, None
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success":
                return data, None
    except Exception:
        pass
    return None, None

def render_weather_card(title: str, weather_data: dict):
    if not weather_data or "main" not in weather_data:
        st.markdown(f"""
        <div class="weather-card">
            <div class="weather-city">✈️ {title}</div>
            <div class="weather-details">날씨 정보 로딩 대기 중...</div>
        </div>
        """, unsafe_allow_html=True)
        return

    temp = round(weather_data["main"].get("temp", 0), 1)
    feels = round(weather_data["main"].get("feels_like", 0), 1)
    humidity = weather_data["main"].get("humidity", 0)
    wind = weather_data.get("wind", {}).get("speed", 0)
    desc = weather_data["weather"][0].get("description", "") if weather_data.get("weather") else ""
    icon = weather_data["weather"][0].get("icon", "01d") if weather_data.get("weather") else "01d"
    icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"

    st.markdown(f"""
    <div class="weather-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="weather-city">✈️ {title}</div>
                <div class="weather-temp">{temp}°C</div>
                <div class="weather-desc-badge">{desc}</div>
            </div>
            <img src="{icon_url}" width="65">
        </div>
        <div class="weather-details">
            체감 {feels}°C · 습도 {humidity}% · 풍속 {wind}m/s
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. 카카오 지도 렌더러 (검증 완료된 형태)
# -------------------------------------------------------------
def render_kakao_map(lat: float, lon: float, place_name: str = "", nearby_places: list = None):
    if not KAKAO_JS_API_KEY:
        st.warning("카카오 지도 JS 키가 없습니다.")
        return

    nearby_json = json.dumps(nearby_places or [], ensure_ascii=False)

    html_code = f"""
    <div id="map" style="width:100%;height:480px;border-radius:18px;background:#f8f5ff;
         display:flex;align-items:center;justify-content:center;color:#6b528e;font-size:13px;border:2px solid #ded2f7;">
         지도를 불러오는 중입니다... ✈️
    </div>
    <script>
        (function() {{
            var originalWrite = document.write.bind(document);
            document.write = function(markup) {{
                originalWrite(String(markup).split('http://').join('https://'));
            }};
        }})();
    </script>
    <script src="https://dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_API_KEY}"></script>
    <script>
        var mapTries = 0;
        var nearbyData = {nearby_json};

        function tryInitMap() {{
            mapTries++;
            var ready = (typeof kakao !== 'undefined') && kakao.maps && typeof kakao.maps.LatLng === 'function';

            if (ready) {{
                try {{
                    var container = document.getElementById('map');
                    container.innerHTML = '';
                    var centerPos = new kakao.maps.LatLng({lat}, {lon});
                    var map = new kakao.maps.Map(container, {{ center: centerPos, level: 4 }});

                    map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);

                    var mainMarker = new kakao.maps.Marker({{ position: centerPos, map: map }});
                    var mainIw = new kakao.maps.InfoWindow({{
                        content: '<div style="padding:8px 12px;font-size:12px;min-width:160px;font-family:sans-serif;line-height:1.4;">' +
                                 '<strong style="color:#7748c2;font-size:13px;">📍 {place_name}</strong></div>'
                    }});
                    mainIw.open(map, mainMarker);

                    if (nearbyData && nearbyData.length > 0) {{
                        var bounds = new kakao.maps.LatLngBounds();
                        bounds.extend(centerPos);
                        var activeIw = null;

                        nearbyData.forEach(function(p) {{
                            var pPos = new kakao.maps.LatLng(p.y, p.x);
                            bounds.extend(pPos);
                            var marker = new kakao.maps.Marker({{ position: pPos, map: map }});

                            var content = '<div style="padding:8px 10px;font-size:12px;max-width:210px;line-height:1.4;font-family:sans-serif;">' +
                                          '<b style="color:#222;">' + p.place_name + '</b><br>' +
                                          '<span style="font-size:11px;color:#777;">' + (p.road_address_name || p.address_name) + '</span><br>' +
                                          (p.place_url ? '<a href="' + p.place_url + '" target="_blank" style="color:#6d3fc2;font-weight:bold;font-size:11px;text-decoration:none;">상세보기 ↗</a>' : '') +
                                          '</div>';

                            var iw = new kakao.maps.InfoWindow({{ content: content, removable: true }});
                            kakao.maps.event.addListener(marker, 'click', function() {{
                                if (activeIw) activeIw.close();
                                iw.open(map, marker);
                                activeIw = iw;
                            }});
                        }});
                        map.setBounds(bounds);
                    }}
                }} catch (e) {{}}
            }} else if (mapTries < 25) {{
                setTimeout(tryInitMap, 200);
            }}
        }}
        tryInitMap();
    </script>
    """
    components.html(html_code, height=500)

# -------------------------------------------------------------
# 6. 세션 기본값 및 사이드바 (페이지 탭 메뉴)
# -------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "🍲 한국"

preset_defaults = {
    "경복궁": {"x": "126.9770", "y": "37.5796", "place_name": "경복궁", "road_address_name": "서울 종로구 사직로 161", "place_url": "https://place.map.kakao.com/8129210"},
    "해운대 해수욕장": {"x": "129.1604", "y": "35.1587", "place_name": "해운대 해수욕장", "road_address_name": "부산 해운대구 우동", "place_url": "https://place.map.kakao.com/8051280"},
    "성산일출봉": {"x": "126.9427", "y": "33.4585", "place_name": "성산일출봉", "road_address_name": "제주 서귀포시 성산읍 일출로 284-12", "place_url": "https://place.map.kakao.com/8119865"}
}

if "selected_place" not in st.session_state:
    st.session_state.selected_place = preset_defaults["경복궁"]

with st.sidebar:
    st.markdown("<h2 style='color:#4a2c7a; margin-bottom: 2px;'>✈️ Travel App</h2>", unsafe_allow_html=True)
    st.caption("스마트 여행 플래너 & 국가별 가이드")
    st.write("")

    nav_pages = [
        "🍲 한국",
        "🍣 일본",
        "🥟 중국",
        "🍔 미국",
        "🥐 기타 국가",
        "🍧 환율 계산기"
    ]

    for p_id in nav_pages:
        is_active = (st.session_state.current_page == p_id)
        btn_txt = f"✈️  {p_id}" if is_active else f"     {p_id}"
        if st.button(btn_txt, key=f"btn_{p_id}"):
            st.session_state.current_page = p_id
            st.rerun()

    st.divider()

    # 영구 저장되는 여행 플래너 보관함
    st.markdown("##### 📋 내 여행 플래너 보관함")
    if st.session_state.my_plan:
        for idx, item in enumerate(st.session_state.my_plan, 1):
            st.markdown(f"<div style='font-size:12px; color:#402d57; margin-bottom:4px;'><b>{idx}.</b> {item}</div>", unsafe_allow_html=True)
        
        st.write("")
        if st.button("🗑️ 전체 보관함 비우기"):
            st.session_state.my_plan = []
            save_plans([])
            st.rerun()
    else:
        st.caption("보관된 여행지가 없습니다. 추천 스팟을 추가해보세요.")

# -------------------------------------------------------------
# 7. 메인 화면 로직
# -------------------------------------------------------------
curr_page = st.session_state.current_page

# [1] 한국
if curr_page == "🍲 한국":
    st.markdown("<h2 style='color:#3b2359;'>🍲 국내 여행 플래너</h2>", unsafe_allow_html=True)
    st.caption("실시간 날씨와 지도로 나만의 국내 여행 코스를 계획하세요.")
    st.write("")

    w1, w2, w3 = st.columns(3)
    with w1: render_weather_card("서울 (Seoul)", get_weather_by_city("Seoul"))
    with w2: render_weather_card("부산 (Busan)", get_weather_by_city("Busan"))
    with w3: render_weather_card("제주 (Jeju)", get_weather_by_city("Jeju"))

    st.divider()

    col_l, col_r = st.columns([5, 7], gap="large")

    with col_l:
        st.markdown("#### 🔍 장소 검색 및 선택")
        user_query = st.text_input("직접 장소 검색", placeholder="예: 해운대 맛집, 성수동 카페")
        preset_choice = st.selectbox("추천 명소 선택", list(preset_defaults.keys()))
        
        if st.button("선택 명소로 지도 이동"):
            st.session_state.selected_place = preset_defaults[preset_choice]

        if user_query.strip():
            places, _ = kakao_search_place(user_query.strip())
            if places:
                opts = [f"{p['place_name']} ({p.get('road_address_name') or p.get('address_name')})" for p in places]
                p_idx = st.selectbox("🎯 검색 결과", range(len(opts)), format_func=lambda i: opts[i])
                st.session_state.selected_place = places[p_idx]

        place = st.session_state.selected_place
        lat, lon = float(place["y"]), float(place["x"])
        name = place["place_name"]
        address = place.get("road_address_name") or place.get("address_name") or "-"

        st.markdown(f"""
        <div class="spot-card">
            <span class="spot-tag">선택 장소</span>
            <div class="spot-title" style="font-size:16px; margin-top:4px;">📍 {name}</div>
            <div style="font-size:12px; color:#5c4973; margin-top:3px;">{address}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ 플래너에 담기"):
                item_str = f"[한국] {name}"
                if item_str not in st.session_state.my_plan:
                    st.session_state.my_plan.append(item_str)
                    save_plans(st.session_state.my_plan)
                    st.success("플래너에 저장되었습니다.")
        with c2:
            if place.get("place_url"):
                st.link_button("카카오맵 상세 ↗", place["place_url"])

        cat_picked = st.radio("주변 탐색", ["선택 안 함", "🍴 맛집", "☕ 카페", "🏪 편의점"], horizontal=True)
        cat_map = {"🍴 맛집": "FD6", "☕ 카페": "CE7", "🏪 편의점": "CS2"}
        nearby = []
        if cat_picked in cat_map:
            nearby = kakao_search_category(cat_map[cat_picked], lat, lon)

        if nearby:
            with st.container(height=180):
                for i, p in enumerate(nearby, 1):
                    with st.expander(f"{i}. {p['place_name']}"):
                        st.caption(p.get("road_address_name") or p.get("address_name"))

    with col_r:
        st.markdown("#### 🗺️ 카카오 지도")
        render_kakao_map(lat, lon, place_name=name, nearby_places=nearby)

# [2, 3, 4] 일본, 중국, 미국
elif curr_page in ["🍣 일본", "🥟 중국", "🍔 미국"]:
    country_data = {
        "🍣 일본": {
            "title": "일본 여행 플래너 (Japan)",
            "city": "Tokyo", "curr": "JPY",
            "spots": [
                {"name": "도쿄 시부야 스카이", "city": "Tokyo", "tag": "전망대", "desc": "도쿄 시내를 360도로 조망하는 루프탑 전망대"},
                {"name": "교토 아라시야마 대나무숲", "city": "Kyoto", "tag": "자연", "desc": "신비로운 청량감을 주는 치쿠린 산책로"},
                {"name": "오사카 도톤보리", "city": "Osaka", "tag": "미식거리", "desc": "화려한 간판과 맛집이 모여있는 중심가"}
            ]
        },
        "🥟 중국": {
            "title": "중국 여행 플래너 (China)",
            "city": "Beijing", "curr": "CNY",
            "spots": [
                {"name": "베이징 자금성", "city": "Beijing", "tag": "역사유적", "desc": "황제의 역사가 깃든 세계 최대 규모의 궁궐"},
                {"name": "상하이 와이탄", "city": "Shanghai", "tag": "야경명소", "desc": "황푸강변 근대 건축과 마천루 파노라마"},
                {"name": "청두 판다 생태기지", "city": "Chengdu", "tag": "생태공원", "desc": "귀여운 자이언트 판다 보호 연구 센터"}
            ]
        },
        "🍔 미국": {
            "title": "미국 여행 플래너 (USA)",
            "city": "New York", "curr": "USD",
            "spots": [
                {"name": "뉴욕 센트럴 파크", "city": "New York", "tag": "도심공원", "desc": "도심 한가운데에서 누리는 여유로운 산책"},
                {"name": "LA 그리피스 천문대", "city": "Los Angeles", "tag": "일몰/야경", "desc": "LA 시내와 할리우드 사인을 조망하는 명소"},
                {"name": "샌프란시스코 금문교", "city": "San Francisco", "tag": "랜드마크", "desc": "태평양과 만을 가로지르는 붉은 현수교"}
            ]
        }
    }
    info = country_data[curr_page]
    st.markdown(f"<h2 style='color:#3b2359;'>{info['title']}</h2>", unsafe_allow_html=True)
    st.write("")

    col_w, col_e = st.columns(2, gap="large")
    with col_w:
        st.markdown("#### 🌤️ 현지 실시간 날씨")
        w = get_weather_by_city(info["city"])
        render_weather_card(f"{info['city']} 현재 날씨", w)

    with col_e:
        st.markdown(f"#### 💱 {info['curr']} 실시간 환율")
        if EXCHANGERATE_API_KEY:
            r, _ = get_exchange_rate("KRW", info["curr"])
            if r and "conversion_rate" in r:
                k_rate = r["conversion_rate"]
                st.markdown(f"""
                <div class="weather-card">
                    <div class="weather-city">💱 1,000 KRW 환산 금액</div>
                    <div class="weather-temp">{1000 * k_rate:,.2f} {info['curr']}</div>
                    <div class="weather-desc-badge">1 KRW = {k_rate:.4f} {info['curr']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("### ✈️ 추천 여행 명소")
    cols = st.columns(3)
    for i, s in enumerate(info["spots"]):
        with cols[i]:
            st.markdown(f"""
            <div class="spot-card">
                <span class="spot-tag">{s['tag']}</span>
                <span class="spot-tag" style="background:#e4d6fc; color:#4a2382;">{s['city']}</span>
                <div class="spot-title" style="margin-top:6px; font-size:16px;">{s['name']}</div>
                <div style="font-size:12px; color:#5c4973; margin-top:4px;">{s['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"➕ 플래너 담기", key=f"spot_{curr_page}_{i}"):
                item_str = f"[{curr_page.split()[1]}] {s['name']}"
                if item_str not in st.session_state.my_plan:
                    st.session_state.my_plan.append(item_str)
                    save_plans(st.session_state.my_plan)
                    st.success(f"'{s['name']}' 저장 완료")

# [5] 기타 국가
elif curr_page == "🥐 기타 국가":
    st.markdown("<h2 style='color:#3b2359;'>🥐 전 세계 주요 도시 플래너 (Others)</h2>", unsafe_allow_html=True)
    st.write("")

    others_dict = {
        "🇫🇷 프랑스 파리 (Paris)": {"city": "Paris", "curr": "EUR", "spots": "에펠탑, 루브르 박물관, 몽마르트르 언덕"},
        "🇮🇹 이탈리아 로마 (Rome)": {"city": "Rome", "curr": "EUR", "spots": "콜로세움, 트레비 분수, 바티칸 미술관"},
        "🇪🇸 스페인 바르셀로나 (Barcelona)": {"city": "Barcelona", "curr": "EUR", "spots": "사그라다 파밀리아, 구엘 공원, 람블라스 거리"},
        "🇹🇭 태국 방콕 (Bangkok)": {"city": "Bangkok", "curr": "THB", "spots": "왓 아룬, 카오산 로드, 아이콘시암"},
        "🇻🇳 베트남 다낭 (Da Nang)": {"city": "Da Nang", "curr": "VND", "spots": "미케비치, 바나힐 골든브릿지, 호이안 구시가지"}
    }

    pick = st.selectbox("도시 선택", list(others_dict.keys()))
    t_data = others_dict[pick]

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"#### 🌤️ {t_data['city']} 날씨")
        w = get_weather_by_city(t_data["city"])
        render_weather_card(t_data["city"], w)
    with c2:
        st.markdown(f"#### 💱 {t_data['curr']} 환율")
        if EXCHANGERATE_API_KEY:
            r, _ = get_exchange_rate("KRW", t_data["curr"])
            if r and "conversion_rate" in r:
                k_rate = r["conversion_rate"]
                st.markdown(f"""
                <div class="weather-card">
                    <div class="weather-city">💱 1,000 KRW 환산 금액</div>
                    <div class="weather-temp">{1000 * k_rate:,.2f} {t_data['curr']}</div>
                    <div class="weather-desc-badge">1 KRW = {k_rate:.4f} {t_data['curr']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="spot-card">
        <span class="spot-tag">핵심 코스</span>
        <div class="spot-title" style="margin-top:6px; font-size:16px;">📍 {pick} 추천 코스</div>
        <div style="font-size:13px; color:#5c4973; margin-top:6px;">{t_data['spots']}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("➕ 이 도시 코스 전체 담기"):
        item_str = f"[{t_data['city']}] {t_data['spots']}"
        if item_str not in st.session_state.my_plan:
            st.session_state.my_plan.append(item_str)
            save_plans(st.session_state.my_plan)
            st.success("플래너에 추가되었습니다.")

# [6] 환율 계산기
elif curr_page == "🍧 환율 계산기":
    st.markdown("<h2 style='color:#3b2359;'>🍧 실시간 환율 계산기</h2>", unsafe_allow_html=True)
    st.caption("기준 통화와 환전 금액을 입력하면 실시간 환율로 자동 환산됩니다.")
    st.write("")

    currency_list = ["KRW", "USD", "JPY", "CNY", "EUR", "GBP", "THB", "VND", "TWD", "AUD", "CAD"]
    col_c1, col_c2, col_c3 = st.columns([2, 2, 3])
    with col_c1: base = st.selectbox("보내는 통화 (기준)", currency_list, index=0)
    with col_c2: target = st.selectbox("받는 통화 (변환)", currency_list, index=1)
    with col_c3: amt = st.number_input("환전 금액", min_value=0.0, value=10000.0, step=1000.0)

    if base == target:
        st.info("기준 통화와 변환 통화가 동일합니다.")
    elif EXCHANGERATE_API_KEY:
        r_info, _ = get_exchange_rate(base, target)
        if r_info and "conversion_rate" in r_info:
            c_rate = r_info["conversion_rate"]
            res = amt * c_rate
            st.markdown(f"""
            <div class="weather-card" style="margin-top:20px; text-align:center;">
                <div class="weather-city" style="justify-content:center;">✈️ 변환 결과</div>
                <div class="weather-temp" style="color:#6d3fc2; font-size:38px; margin: 10px 0;">{res:,.2f} {target}</div>
                <div class="weather-desc-badge">{amt:,.0f} {base} · 적용 환율: 1 {base} = {c_rate:.4f} {target}</div>
            </div>
            """, unsafe_allow_html=True)
import os
import json
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
    page_title="Fluffy Travel Planner ✨",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2. 뽀용한 파스텔 핑크 글래스모피즘 CSS
# -------------------------------------------------------------
fluffy_theme_css = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

.stApp {
    background: linear-gradient(135deg, #fff5f7 0%, #fdecef 45%, #fce4ec 100%);
    font-family: 'Pretendard', sans-serif;
    color: #4a3b40;
}

section[data-testid="stSidebar"] {
    background-color: rgba(255, 245, 247, 0.75) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 192, 203, 0.4);
}

/* 일반 핑크 버튼 */
.stButton > button {
    background: linear-gradient(135deg, #ffb6c1 0%, #ff8fab 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 18px !important;
    padding: 8px 18px !important;
    font-weight: bold !important;
    box-shadow: 0 4px 15px rgba(255, 143, 171, 0.3) !important;
    transition: all 0.2s ease-in-out !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 143, 171, 0.45) !important;
}

/* 입력 필드 */
div[data-baseweb="input"], div[data-baseweb="select"] {
    border-radius: 16px !important;
    background-color: rgba(255, 255, 255, 0.75) !important;
    border: 1.5px solid #ffd1dc !important;
}

/* 감성 뽀용 글래스 카드 */
.weather-card {
    background: rgba(255, 255, 255, 0.68);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1.5px solid rgba(255, 255, 255, 0.85);
    border-radius: 20px;
    padding: 18px 20px;
    box-shadow: 0 10px 25px rgba(255, 182, 193, 0.22);
    margin-bottom: 14px;
}
.weather-city {
    font-size: 14px;
    font-weight: 700;
    color: #e06d88;
    margin-bottom: 4px;
}
.weather-temp {
    font-size: 30px;
    font-weight: 800;
    color: #3d3135;
    letter-spacing: -1px;
}
.weather-desc {
    font-size: 12px;
    color: #946b77;
    background: #ffeef2;
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
}
.weather-sub {
    font-size: 12px;
    color: #8c737a;
    margin-top: 8px;
}

/* 플래너 스팟 카드 */
.spot-card {
    background: rgba(255, 255, 255, 0.75);
    border: 1.5px solid #ffd6e0;
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px rgba(255, 182, 193, 0.15);
}
.spot-title {
    font-size: 15px;
    font-weight: bold;
    color: #e06d88;
}
.spot-tag {
    display: inline-block;
    background: #ffe8ee;
    color: #d1506d;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 4px;
}
</style>
"""
st.markdown(fluffy_theme_css, unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. API 통신 및 헬퍼 함수
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

def render_fluffy_weather_card(title: str, weather_data: dict):
    if not weather_data or "main" not in weather_data:
        st.markdown(f"""
        <div class="weather-card">
            <div class="weather-city">✨ {title}</div>
            <div class="weather-desc">날씨 로딩 중...</div>
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
                <div class="weather-city">✨ {title}</div>
                <div class="weather-temp">{temp}°C</div>
                <div class="weather-desc">{desc}</div>
            </div>
            <img src="{icon_url}" width="65" style="filter: drop-shadow(0 4px 6px rgba(255,143,171,0.3));">
        </div>
        <div class="weather-sub">
            체감 {feels}°C · 습도 {humidity}% · 바람 {wind}m/s
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. 카카오 지도 렌더러 (검증된 방식)
# -------------------------------------------------------------
def render_kakao_map(lat: float, lon: float, place_name: str = "", nearby_places: list = None):
    if not KAKAO_JS_API_KEY:
        st.warning("카카오 지도 키가 설정되지 않았습니다.")
        return

    nearby_json = json.dumps(nearby_places or [], ensure_ascii=False)

    html_code = f"""
    <div id="map" style="width:100%;height:480px;border-radius:20px;background:#fff5f7;
         display:flex;align-items:center;justify-content:center;color:#b08d98;font-size:13px;border:2px solid #ffd6e0;">
         지도를 몽환적으로 불러오는 중... ✨
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
                                 '<strong style="color:#ff6b8b;font-size:13px;">📍 {place_name}</strong></div>'
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
                                          '<b style="color:#333;">' + p.place_name + '</b><br>' +
                                          '<span style="font-size:11px;color:#888;">' + (p.road_address_name || p.address_name) + '</span><br>' +
                                          (p.place_url ? '<a href="' + p.place_url + '" target="_blank" style="color:#ff6b8b;font-weight:bold;font-size:11px;text-decoration:none;">상세보기 ↗</a>' : '') +
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
# 5. 세션 상태 초기화 (페이지 네비게이션 & 여행 플래너 바구니)
# -------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "🍲 한국"

if "my_plan" not in st.session_state:
    st.session_state.my_plan = []

preset_defaults = {
    "경복궁": {"x": "126.9770", "y": "37.5796", "place_name": "경복궁", "road_address_name": "서울 종로구 사직로 161", "place_url": "https://place.map.kakao.com/8129210"},
    "해운대 해수욕장": {"x": "129.1604", "y": "35.1587", "place_name": "해운대 해수욕장", "road_address_name": "부산 해운대구 우동", "place_url": "https://place.map.kakao.com/8051280"},
    "성산일출봉": {"x": "126.9427", "y": "33.4585", "place_name": "성산일출봉", "road_address_name": "제주 서귀포시 성산읍 일출로 284-12", "place_url": "https://place.map.kakao.com/8119865"}
}

if "selected_place" not in st.session_state:
    st.session_state.selected_place = preset_defaults["경복궁"]

# -------------------------------------------------------------
# 6. 사이드바: 라디오 대신 "페이지 전환 탭 버튼"
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#e06d88;'>🌸 Travel Note</h2>", unsafe_allow_html=True)
    st.caption("가고 싶은 나라 페이지를 클릭하세요 ✨")
    st.write("")

    pages = [
        ("🍲 한국", "국내 힐링 & 명소"),
        ("🍣 일본", "도쿄 · 오사카 · 교토"),
        ("🥟 중국", "베이징 · 상하이"),
        ("🍔 미국", "뉴욕 · LA · 샌프란시스코"),
        ("🥐 기타 국가", "유럽 및 아시아 명소"),
        ("🍧 환율 계산기", "실시간 경비 계산")
    ]

    for p_id, p_desc in pages:
        is_active = (st.session_state.current_page == p_id)
        btn_label = f"✨ {p_id}" if is_active else f"   {p_id}"
        if st.button(btn_label, key=f"nav_{p_id}"):
            st.session_state.current_page = p_id
            st.rerun()

    st.divider()

    # 사이드바 하단: 내가 담은 여행 버킷리스트
    st.markdown("##### 📝 나의 여행 플래너 보관함")
    if st.session_state.my_plan:
        for idx, item in enumerate(st.session_state.my_plan, 1):
            st.caption(f"{idx}. {item}")
        if st.button("🗑️ 전체 일정 비우기"):
            st.session_state.my_plan = []
            st.rerun()
    else:
        st.caption("아직 담은 여행지가 없어요! 마음에 드는 스팟을 담아보세요 🍓")

# -------------------------------------------------------------
# 7. 메인 페이지 로직 (국가별 추천 여행지 + 플래너 기능)
# -------------------------------------------------------------
curr_page = st.session_state.current_page

# [PAGE 1] 한국
if curr_page == "🍲 한국":
    st.markdown("<h2 style='color:#e06d88;'>🍲 국내 감성 여행 플래너</h2>", unsafe_allow_html=True)
    st.caption("실시간 날씨와 지도로 나만의 여행 코스를 완성해보세요 ☁️")
    st.write("")

    # 실시간 날씨
    w1, w2, w3 = st.columns(3)
    with w1: render_fluffy_weather_card("서울 (Seoul)", get_weather_by_city("Seoul"))
    with w2: render_fluffy_weather_card("부산 (Busan)", get_weather_by_city("Busan"))
    with w3: render_fluffy_weather_card("제주 (Jeju)", get_weather_by_city("Jeju"))

    st.divider()

    col_l, col_r = st.columns([5, 7], gap="large")

    with col_l:
        st.markdown("#### 🗺️ 핫플레이스 탐색")
        user_query = st.text_input("가고 싶은 곳 검색", placeholder="예: 성수동 카페거리, 광안리 해변")
        preset_choice = st.selectbox("추천 힐링 명소 빠른 선택", list(preset_defaults.keys()))
        
        if st.button("해당 스팟으로 이동 슝 ✨"):
            st.session_state.selected_place = preset_defaults[preset_choice]

        if user_query.strip():
            places, _ = kakao_search_place(user_query.strip())
            if places:
                opts = [f"{p['place_name']} ({p.get('road_address_name') or p.get('address_name')})" for p in places]
                p_idx = st.selectbox("🎯 검색 목록", range(len(opts)), format_func=lambda i: opts[i])
                st.session_state.selected_place = places[p_idx]

        place = st.session_state.selected_place
        lat, lon = float(place["y"]), float(place["x"])
        name = place["place_name"]
        address = place.get("road_address_name") or place.get("address_name") or "-"

        st.markdown(f"""
        <div class="spot-card">
            <span class="spot-tag">현재 선택지</span>
            <div class="spot-title" style="font-size:17px; margin-top:4px;">📍 {name}</div>
            <div style="font-size:12px; color:#888; margin: 4px 0;">{address}</div>
        </div>
        """, unsafe_allow_html=True)

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("➕ 내 플래너에 담기"):
                plan_item = f"[한국] {name} ({address})"
                if plan_item not in st.session_state.my_plan:
                    st.session_state.my_plan.append(plan_item)
                    st.success("보관함에 쏙 들어갔어요! 🌸")
        with c_btn2:
            if place.get("place_url"):
                st.link_button("카카오맵 상세 ↗", place["place_url"])

        # 주변 편의시설
        cat_picked = st.radio("주변 탐색 필터", ["선택 안 함", "🍴 맛집", "☕ 카페", "🏪 편의점"], horizontal=True)
        cat_map = {"🍴 맛집": "FD6", "☕ 카페": "CE7", "🏪 편의점": "CS2"}
        nearby = []
        if cat_picked in cat_map:
            nearby = kakao_search_category(cat_map[cat_picked], lat, lon)

        if nearby:
            with st.container(height=200):
                for i, p in enumerate(nearby, 1):
                    with st.expander(f"{i}. {p['place_name']}"):
                        st.caption(p.get("road_address_name") or p.get("address_name"))

    with col_r:
        st.markdown("#### 📍 지도 프리뷰")
        render_kakao_map(lat, lon, place_name=name, nearby_places=nearby)

# [PAGE 2, 3, 4] 일본, 중국, 미국
elif curr_page in ["🍣 일본", "🥟 중국", "🍔 미국"]:
    country_data = {
        "🍣 일본": {
            "title": "일본 감성 미식 여행 (Japan)",
            "city": "Tokyo", "curr": "JPY",
            "spots": [
                {"name": "도쿄 시부야 스카이", "city": "Tokyo", "tag": "야경명소", "desc": "도쿄 시내를 360도로 조망하는 루프탑 전망대"},
                {"name": "교토 아라시야마 대나무숲", "city": "Kyoto", "tag": "자연/힐링", "desc": "신비로운 청량감을 주는 치쿠린 산책로"},
                {"name": "오사카 도톤보리 & 글리코상", "city": "Osaka", "tag": "먹거리", "desc": "타코야키와 맛집이 가득한 오사카의 심장"}
            ]
        },
        "🥟 중국": {
            "title": "중국 웅장 & 미식 여행 (China)",
            "city": "Beijing", "curr": "CNY",
            "spots": [
                {"name": "베이징 자금성 & 이화원", "city": "Beijing", "tag": "역사유적", "desc": "황제의 발자취를 따라 걷는 세계 최대 궁궐"},
                {"name": "상하이 와이탄 야경", "city": "Shanghai", "tag": "도시야경", "desc": "황푸강변을 따라 펼쳐지는 근대 건축과 화려한 마천루"},
                {"name": "청두 판다 번식기지", "city": "Chengdu", "tag": "힐링/동물", "desc": "귀여운 자이언트 판다를 만나는 생태 공원"}
            ]
        },
        "🍔 미국": {
            "title": "미국 로맨틱 시티 여행 (USA)",
            "city": "New York", "curr": "USD",
            "spots": [
                {"name": "뉴욕 센트럴 파크", "city": "New York", "tag": "도심힐링", "desc": "빌딩 숲 사이에서 베이글 들고 피크닉하기 좋은 곳"},
                {"name": "LA 그리피스 천문대", "city": "Los Angeles", "tag": "선셋명소", "desc": "라라랜드 감성 그대로 할리우드 사인을 바라보는 언덕"},
                {"name": "샌프란시스코 금문교 & 소살리토", "city": "San Francisco", "tag": "바다풍경", "desc": "자전거를 타고 바닷바람을 가르며 건너는 붉은 다리"}
            ]
        }
    }
    info = country_data[curr_page]
    st.markdown(f"<h2 style='color:#e06d88;'>{info['title']}</h2>", unsafe_allow_html=True)
    st.write("")

    col_w, col_e = st.columns(2, gap="large")
    with col_w:
        st.markdown("#### 🌤️ 수도 실시간 날씨")
        w = get_weather_by_city(info["city"])
        render_fluffy_weather_card(f"{info['city']} 현재 날씨", w)

    with col_e:
        st.markdown(f"#### 💱 {info['curr']} 실시간 환율")
        if EXCHANGERATE_API_KEY:
            r, _ = get_exchange_rate("KRW", info["curr"])
            if r and "conversion_rate" in r:
                k_rate = r["conversion_rate"]
                st.markdown(f"""
                <div class="weather-card">
                    <div class="weather-city">💱 1,000 KRW 기준 환율</div>
                    <div class="weather-temp">{1000 * k_rate:,.2f} {info['curr']}</div>
                    <div class="weather-desc">1 KRW = {k_rate:.4f} {info['curr']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("### 🎀 에디터 추천 명소 & 여행 플래너")
    st.caption("마음에 드는 스팟의 '담기' 버튼을 눌러 나만의 일정표를 만들어보세요!")

    cols = st.columns(3)
    for i, s in enumerate(info["spots"]):
        with cols[i]:
            st.markdown(f"""
            <div class="spot-card">
                <span class="spot-tag">{s['tag']}</span>
                <span class="spot-tag" style="background:#e8f4fd; color:#2b7ecb;">{s['city']}</span>
                <div class="spot-title" style="margin-top:6px;">{s['name']}</div>
                <div style="font-size:12px; color:#666; margin-top:4px;">{s['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"💖 플래너에 담기", key=f"spot_{curr_page}_{i}"):
                plan_name = f"[{curr_page.split()[1]}] {s['name']} ({s['tag']})"
                if plan_name not in st.session_state.my_plan:
                    st.session_state.my_plan.append(plan_name)
                    st.success(f"'{s['name']}' 담기 완료! ✨")

# [PAGE 5] 기타 국가
elif curr_page == "🥐 기타 국가":
    st.markdown("<h2 style='color:#e06d88;'>🥐 전 세계 감성 여행지 (Others)</h2>", unsafe_allow_html=True)
    st.caption("낭만 가득한 글로벌 도시를 둘러보고 여행 계획을 세워보세요 🍰")
    st.write("")

    others_dict = {
        "🇫🇷 프랑스 파리 (Paris)": {"city": "Paris", "curr": "EUR", "spots": "에펠탑, 루브르 박물관, 몽마르트르 언덕"},
        "🇮🇹 이탈리아 로마 (Rome)": {"city": "Rome", "curr": "EUR", "spots": "콜로세움, 트레비 분수, 바티칸"},
        "🇪🇸 스페인 바르셀로나 (Barcelona)": {"city": "Barcelona", "curr": "EUR", "spots": "사그라다 파밀리아, 구엘 공원"},
        "🇹🇭 태국 방콕 (Bangkok)": {"city": "Bangkok", "curr": "THB", "spots": "왓 아룬, 카오산 로드, 아이콘시암"},
        "🇻🇳 베트남 다낭 (Da Nang)": {"city": "Da Nang", "curr": "VND", "spots": "미케비치, 바나힐 골든브릿지, 호이안 야시장"}
    }

    pick = st.selectbox("궁금한 도시를 선택하세요", list(others_dict.keys()))
    t_data = others_dict[pick]

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"#### 🌤️ {t_data['city']} 실시간 날씨")
        w = get_weather_by_city(t_data["city"])
        render_fluffy_weather_card(t_data["city"], w)
    with c2:
        st.markdown(f"#### 💱 {t_data['curr']} 환율")
        if EXCHANGERATE_API_KEY:
            r, _ = get_exchange_rate("KRW", t_data["curr"])
            if r and "conversion_rate" in r:
                k_rate = r["conversion_rate"]
                st.markdown(f"""
                <div class="weather-card">
                    <div class="weather-city">💱 1,000 KRW 기준</div>
                    <div class="weather-temp">{1000 * k_rate:,.2f} {t_data['curr']}</div>
                    <div class="weather-desc">1 KRW = {k_rate:.4f} {t_data['curr']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="spot-card">
        <span class="spot-tag">대표 추천 코스</span>
        <div class="spot-title" style="margin-top:6px;">📍 {pick} 핵심 코스</div>
        <div style="font-size:13px; color:#555; margin-top:6px;">{t_data['spots']}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💖 이 도시 코스 플래너에 통째로 담기"):
        plan_line = f"[{t_data['city']}] {t_data['spots']}"
        if plan_line not in st.session_state.my_plan:
            st.session_state.my_plan.append(plan_line)
            st.success("플래너에 추가되었습니다! ✨")

# [PAGE 6] 환율 계산기
elif curr_page == "🍧 환율 계산기":
    st.markdown("<h2 style='color:#e06d88;'>🍧 달콤한 실시간 환율 계산기</h2>", unsafe_allow_html=True)
    st.caption("여행 예산을 뚝딱 계산하고 경비를 똑똑하게 챙겨보세요 ✨")
    st.write("")

    currency_list = ["KRW", "USD", "JPY", "CNY", "EUR", "GBP", "THB", "VND", "TWD", "AUD", "CAD"]
    col_c1, col_c2, col_c3 = st.columns([2, 2, 3])
    with col_c1: base = st.selectbox("보내는 통화", currency_list, index=0)
    with col_c2: target = st.selectbox("받는 통화", currency_list, index=1)
    with col_c3: amt = st.number_input("금액 입력", min_value=0.0, value=10000.0, step=1000.0)

    if base == target:
        st.info("기준 통화와 변환 통화가 같습니다 ✨")
    elif EXCHANGERATE_API_KEY:
        r_info, _ = get_exchange_rate(base, target)
        if r_info and "conversion_rate" in r_info:
            c_rate = r_info["conversion_rate"]
            res = amt * c_rate
            st.markdown(f"""
            <div class="weather-card" style="margin-top:20px; text-align:center;">
                <div class="weather-city" style="justify-content:center;">🎀 변환 결과</div>
                <div class="weather-temp" style="color:#e06d88; font-size:38px; margin: 10px 0;">{res:,.2f} {target}</div>
                <div class="weather-desc">{amt:,.0f} {base} · 적용 환율: 1 {base} = {c_rate:.4f} {target}</div>
            </div>
            """, unsafe_allow_html=True)
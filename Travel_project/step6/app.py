import os
import sys
import json
import base64
from pathlib import Path
import pandas as pd
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
# 2. 로컬 폰트(에이투지체) Base64 로드 & 라벤더 버블 CSS
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

/* 제목류 세미볼드 적용 */
h1, h2, h3, h4, h5, .stHeading, .spot-title, .weather-temp {{
    font-family: 'A2Z-SemiBold', sans-serif !important;
    color: #3b2359 !important;
}}

/* 사이드바 */
section[data-testid="stSidebar"] {{
    background-color: rgba(248, 244, 255, 0.82) !important;
    backdrop-filter: blur(14px);
    border-right: 1.5px solid rgba(215, 196, 245, 0.5);
}}

/* 버튼 내부 흰색 박스 버그 박멸 및 맑은 라벤더 캡슐 버튼 */
section[data-testid="stSidebar"] div.stButton {{
    margin-bottom: 6px !important;
}}
.stButton > button {{
    font-family: 'A2Z-SemiBold', sans-serif !important;
    background: rgba(255, 255, 255, 0.72) !important;
    color: #4a2c7a !important;
    border: 1.5px solid #dcd0f7 !important;
    border-radius: 18px !important;
    padding: 9px 16px !important;
    box-shadow: 0 4px 12px rgba(181, 155, 230, 0.15) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
}}
.stButton > button * {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}}
.stButton > button:hover {{
    background: rgba(238, 226, 255, 0.95) !important;
    border-color: #bfa5f5 !important;
    color: #29124d !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(162, 127, 237, 0.25) !important;
}}

/* 입력창 & 셀렉트박스 */
div[data-baseweb="input"], div[data-baseweb="select"] {{
    border-radius: 14px !important;
    background-color: rgba(255, 255, 255, 0.85) !important;
    border: 1.5px solid #d4c2f7 !important;
}}

/* 날씨 카드 */
.weather-card {{
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    border: 1.5px solid #dcd0f7;
    border-radius: 18px;
    padding: 16px 20px;
    box-shadow: 0 8px 20px rgba(181, 155, 230, 0.18);
    margin-bottom: 12px;
}}
.weather-city {{
    font-family: 'A2Z-SemiBold', sans-serif;
    font-size: 14px;
    color: #6c46a8;
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
}}

/* 스팟 및 맛집 카드 */
.spot-card {{
    background: rgba(255, 255, 255, 0.88);
    border: 1.5px solid #ded3f7;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
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
# 3. 플래너 로컬 JSON 영구 보관 (백엔드 불필요)
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
# 4. 현지어 발음 TTS 재생 렌더러
# -------------------------------------------------------------
def render_tts_button(text: str, lang_code: str, label: str = "🔊 발음 듣기"):
    html_code = f"""
    <button onclick="speakText()" style="
        background: #eedfff;
        color: #583391;
        border: 1px solid #d4c2f7;
        border-radius: 12px;
        padding: 5px 12px;
        font-size: 12px;
        font-weight: bold;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        transition: all 0.2s;
    ">
        {label}
    </button>
    <script>
    function speakText() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var utterance = new SpeechSynthesisUtterance("{text}");
            utterance.lang = "{lang_code}";
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert('이 브라우저는 음성 재생을 지원하지 않습니다.');
        }}
    }}
    </script>
    """
    components.html(html_code, height=36)

# -------------------------------------------------------------
# 5. API 통신 함수들
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
# 6. 카카오 지도 렌더러
# -------------------------------------------------------------
def render_kakao_map(lat: float, lon: float, place_name: str = "", nearby_places: list = None):
    if not KAKAO_JS_API_KEY:
        st.warning("카카오 지도 JS 키가 없습니다.")
        return

    nearby_json = json.dumps(nearby_places or [], ensure_ascii=False)

    html_code = f"""
    <div id="map" style="width:100%;height:520px;border-radius:18px;background:#f8f5ff;
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
    components.html(html_code, height=540)

# -------------------------------------------------------------
# 7. 세션 기본값 및 사이드바 (깔끔한 라벤더 메뉴 & CSV 다운로드)
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
    st.markdown("<h2 style='color:#3b2359; margin-bottom: 2px;'>✈️ Travel App</h2>", unsafe_allow_html=True)
    st.caption("스마트 여행 플래너 & 국가별 가이드")
    st.write("")

    nav_pages = [
        "🍲 한국",
        "🍣 일본",
        "🥟 중국",
        "🍔 미국",
        "🥐 기타 국가",
        "🍧 환율 & 일정 플래너"
    ]

    for p_id in nav_pages:
        is_active = (st.session_state.current_page == p_id)
        btn_txt = f"✈️  {p_id}" if is_active else f"     {p_id}"
        if st.button(btn_txt, key=f"btn_{p_id}"):
            st.session_state.current_page = p_id
            st.rerun()

    st.divider()

    # 영구 보관 플래너 보관함 + CSV 다운로드
    st.markdown("##### 📋 내 여행 플래너 보관함")
    if st.session_state.my_plan:
        for idx, item in enumerate(st.session_state.my_plan, 1):
            st.markdown(f"<div style='font-size:12px; color:#402d57; margin-bottom:3px;'><b>{idx}.</b> {item}</div>", unsafe_allow_html=True)
        
        df_plan = pd.DataFrame({
            "순번": range(1, len(st.session_state.my_plan) + 1),
            "방문지/일정": st.session_state.my_plan
        })
        csv_data = df_plan.to_csv(index=False).encode('utf-8-sig')

        st.download_button(
            label="📥 플래너 CSV 다운로드",
            data=csv_data,
            file_name="my_travel_plan.csv",
            mime="text/csv"
        )

        if st.button("🗑️ 전체 보관함 비우기"):
            st.session_state.my_plan = []
            save_plans([])
            st.rerun()
    else:
        st.caption("보관된 여행지가 없습니다. 추천 스팟을 플래너에 담아보세요.")

# -------------------------------------------------------------
# 8. 메인 화면 로직
# -------------------------------------------------------------
curr_page = st.session_state.current_page

# [PAGE 1] 한국: 미식 기행 컨셉
if curr_page == "🍲 한국":
    st.markdown("<h2 style='color:#3b2359;'>🍲 대한민국 미식 기행 센터</h2>", unsafe_allow_html=True)
    st.caption("지역 고유의 맛과 골목의 숨은 노포를 찾아 떠나는 테마 미식 여행 🥢")
    st.write("")

    w1, w2, w3 = st.columns(3)
    with w1: render_weather_card("서울 (Seoul)", get_weather_by_city("Seoul"))
    with w2: render_weather_card("부산 (Busan)", get_weather_by_city("Busan"))
    with w3: render_weather_card("제주 (Jeju)", get_weather_by_city("Jeju"))

    st.divider()

    # 미식 기행 데이터베이스
    gourmet_db = {
        "서울 익선동 & 종로 노포 기행": {
            "region": "서울",
            "lat": 37.5743, "lon": 126.9897,
            "theme_food": "종로 바싹불고기 & 익선동 한옥 양식",
            "course": "종로 3가 노포 골목 ➡️ 익선동 한옥 디저트 ➡️ 인사동 전통 다실",
            "spots": [
                {
                    "name": "익선잡방 (Ikseon Jabbang)",
                    "category": "양식 / 브런치",
                    "rating": 4.8, "reviews": 1240,
                    "price": "18,000원 ~ 28,000원",
                    "menu": "이베리코 프렌치랙 스테이크, 명란 크림 파스타",
                    "comment": "신라호텔 출신 셰프가 선보이는 한옥 감성 프렌치 다이닝의 정수!",
                    "img": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=60",
                    "address": "서울 종로구 수표로28길 17-21"
                },
                {
                    "name": "찬양집 (해물칼국수)",
                    "category": "한식 / 노포",
                    "rating": 4.6, "reviews": 3120,
                    "price": "9,000원",
                    "menu": "진한 바지락·홍합 해물칼국수, 손만두",
                    "comment": "1965년부터 이어온 미쉐린 빕 구르망 선정 시원하고 깊은 해물 육수.",
                    "img": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600&auto=format&fit=crop&q=60",
                    "address": "서울 종로구 돈화문로11다길 5"
                }
            ]
        },
        "부산 바다 내음 해산물 & 돼지국밥 기행": {
            "region": "부산",
            "lat": 35.1587, "lon": 129.1604,
            "theme_food": "부산 원조 돼지국밥 & 광안리 활어회",
            "course": "자갈치 시장 건어물 탐방 ➡️ 영도 흰여울 해녀촌 ➡️ 해운대 포장마차촌",
            "spots": [
                {
                    "name": "수변최고명품돼지국밥",
                    "category": "한식 / 국밥",
                    "rating": 4.9, "reviews": 4890,
                    "price": "10,000원 ~ 13,000원",
                    "menu": "항정국밥, 고기순대국밥",
                    "comment": "잡내 없이 극도로 뽀얗고 진한 국물과 야들야들한 항정살의 완벽한 조화!",
                    "img": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600&auto=format&fit=crop&q=60",
                    "address": "부산 수영구 광안해변로370번길 9-32"
                },
                {
                    "name": "해운대 기와집 대구탕",
                    "category": "해물 / 탕",
                    "rating": 4.7, "reviews": 2180,
                    "price": "14,000원",
                    "menu": "원조 대구탕 단일 메뉴",
                    "comment": "달맞이길 언덕에서 바다를 내려다보며 즐기는 칼칼하고 맑은 해장 1티어.",
                    "img": "https://images.unsplash.com/photo-1555126634-323283e090fa?w=600&auto=format&fit=crop&q=60",
                    "address": "부산 해운대구 달맞이길104번길 46"
                }
            ]
        },
        "제주 흑돼지 & 감성 오션뷰 미식": {
            "region": "제주",
            "lat": 33.4585, "lon": 126.9427,
            "theme_food": "제주 흑돼지 근고기 & 갈치조림",
            "course": "애월 한담 해변 카페거리 ➡️ 중문 흑돼지 숯불구이 ➡️ 서귀포 올레야시장",
            "spots": [
                {
                    "name": "숙성도 (중문본점)",
                    "category": "구이 / 흑돼지",
                    "rating": 4.9, "reviews": 5600,
                    "price": "22,000원 ~ 38,000원",
                    "menu": "720 숙성 흑삼겹, 교차숙성 흑돼지 꽃등심",
                    "comment": "육즙이 팡 터지는 에이징 삼겹살과 멜젓의 감칠맛은 필수 코스!",
                    "img": "https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=60",
                    "address": "제주 서귀포시 일주서로 966"
                },
                {
                    "name": "맛나식당 (성산)",
                    "category": "한식 / 조림",
                    "rating": 4.8, "reviews": 2900,
                    "price": "13,000원 ~ 14,000원",
                    "menu": "갈치조림, 고등어조림 믹스",
                    "comment": "오전 번호표 마감 필수, 달짝지근하고 푹 익은 무와 신선한 갈치의 전설적 맛.",
                    "img": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600&auto=format&fit=crop&q=60",
                    "address": "제주 서귀포시 성산읍 동류암로 41"
                }
            ]
        }
    }

    theme_choice = st.selectbox("🗺️ 탐방할 지역 미식 테마 코스를 선택하세요", list(gourmet_db.keys()))
    current_theme = gourmet_db[theme_choice]

    st.markdown(f"""
    <div class="spot-card" style="border-left: 5px solid #8e62d9; padding: 18px 22px;">
        <span class="spot-tag" style="font-size:12px;">{current_theme['region']} 대표 미식</span>
        <h3 style="margin: 6px 0; color:#3b2359;">🥢 {current_theme['theme_food']}</h3>
        <p style="font-size:13px; color:#5c4873; margin-bottom: 0;"><b>🚶 추천 기행 동선:</b> {current_theme['course']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    col_map, col_spots = st.columns([6, 6], gap="large")

    with col_map:
        st.markdown("#### 📍 미식 기행 지도")
        theme_places_for_map = [{
            "place_name": s["name"],
            "road_address_name": s["address"],
            "phone": "",
            "x": current_theme["lon"] + (0.003 * i),
            "y": current_theme["lat"] + (0.003 * i),
            "place_url": f"https://map.kakao.com/link/search/{s['name']}"
        } for i, s in enumerate(current_theme["spots"])]

        render_kakao_map(
            lat=current_theme["lat"],
            lon=current_theme["lon"],
            place_name=current_theme["spots"][0]["name"],
            nearby_places=theme_places_for_map
        )
        st.caption("💡 지도 위의 마커를 누르면 상세 위치 정보를 확인할 수 있습니다.")

    with col_spots:
        st.markdown("#### 🍽️ 기행 대표 맛집 상세 명단")
        for idx, spot in enumerate(current_theme["spots"]):
            st.markdown(f"""
            <div class="spot-card" style="margin-bottom: 16px;">
                <div style="display: flex; gap: 14px;">
                    <img src="{spot['img']}" style="width: 120px; height: 120px; border-radius: 14px; object-fit: cover; border: 1px solid #d4c2f7;">
                    <div style="flex: 1;">
                        <span class="spot-tag">{spot['category']}</span>
                        <span style="font-size:12px; color:#e08438; font-weight:bold;">⭐ {spot['rating']} <span style="color:#888; font-weight:normal;">({spot['reviews']:,}개 리뷰)</span></span>
                        <div class="spot-title" style="font-size:17px; margin-top: 3px;">{spot['name']}</div>
                        <div style="font-size:12px; color:#5c4973; margin-top:2px;">📍 {spot['address']}</div>
                        <div style="font-size:12px; color:#4a2c7a; margin-top:4px;"><b>대표메뉴:</b> {spot['menu']}</div>
                        <div style="font-size:12px; color:#6b46a8;"><b>가격대:</b> {spot['price']}</div>
                    </div>
                </div>
                <div style="background: rgba(238, 223, 255, 0.4); border-radius: 10px; padding: 8px 12px; margin-top: 10px; font-size: 12px; color: #432863;">
                    💬 <b>한줄평:</b> "{spot['comment']}"
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            b_col1, b_col2 = st.columns([1, 1])
            with b_col1:
                if st.button(f"➕ 플래너에 담기", key=f"plan_add_{theme_choice}_{idx}"):
                    item_str = f"[{current_theme['region']}] {spot['name']} ({spot['menu']})"
                    if item_str not in st.session_state.my_plan:
                        st.session_state.my_plan.append(item_str)
                        save_plans(st.session_state.my_plan)
                        st.success(f"'{spot['name']}' 저장 완료!")
            with b_col2:
                st.link_button("카카오맵 리뷰 더보기 ↗", f"https://map.kakao.com/link/search/{spot['name']}")

    st.divider()

    # 오늘 뭐 먹지? 돌려돌려 돌림판
    st.markdown("### 🎡 오늘 뭐 먹지? 돌려돌려 메뉴 돌림판!")
    st.caption("무엇을 먹을지 고민될 때 돌림판을 돌려 오늘의 미식 메뉴를 정해보세요 ✨")

    roulette_html = """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; background: rgba(255,255,255,0.7); border-radius: 20px; border: 1.5px solid #ded2f7; box-shadow: 0 6px 18px rgba(181, 155, 230, 0.15);">
        <div style="position: relative; width: 320px; height: 320px;">
            <div style="position: absolute; top: -14px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 14px solid transparent; border-right: 14px solid transparent; border-top: 24px solid #7c4fd6; z-index: 10;"></div>
            <canvas id="wheelCanvas" width="320" height="320" style="border-radius: 50%; box-shadow: 0 4px 15px rgba(138, 92, 230, 0.25);"></canvas>
        </div>
        <button id="spinBtn" onclick="spinWheel()" style="
            margin-top: 22px;
            background: linear-gradient(135deg, #a780f2 0%, #8555e3 100%);
            color: white;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 20px;
            padding: 10px 32px;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(133, 85, 227, 0.35);
            transition: all 0.2s;
        ">
            🎯 돌려돌려 돌림판 START!
        </button>
        <div id="resultBox" style="margin-top: 15px; font-size: 17px; font-weight: bold; color: #4a287a; min-height: 24px;"></div>
    </div>

    <script>
    const canvas = document.getElementById("wheelCanvas");
    const ctx = canvas.getContext("2d");
    const spinBtn = document.getElementById("spinBtn");
    const resultBox = document.getElementById("resultBox");

    const foods = ["돼지국밥 🍲", "해물칼국수 🍜", "흑돼지구이 🥩", "갈치조림 🐟", "이베리코파스타 🍝", "디저트빙수 🍧", "바싹불고기 🍖", "신선활어회 🍣"];
    const colors = ["#f2e8ff", "#eedcff", "#e4cbff", "#dabbff", "#cfa9ff", "#eedcff", "#e4cbff", "#f2e8ff"];
    const numSegments = foods.length;
    const arcSize = (2 * Math.PI) / numSegments;
    let currentAngle = 0;
    let isSpinning = false;

    function drawWheel() {
        ctx.clearRect(0, 0, 320, 320);
        for (let i = 0; i < numSegments; i++) {
            const angle = currentAngle + i * arcSize;
            ctx.beginPath();
            ctx.fillStyle = colors[i % colors.length];
            ctx.moveTo(160, 160);
            ctx.arc(160, 160, 150, angle, angle + arcSize);
            ctx.lineTo(160, 160);
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.save();
            ctx.translate(160, 160);
            ctx.rotate(angle + arcSize / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "#3d2263";
            ctx.font = "bold 13px sans-serif";
            ctx.fillText(foods[i], 135, 5);
            ctx.restore();
        }

        ctx.beginPath();
        ctx.arc(160, 160, 24, 0, 2 * Math.PI);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.strokeStyle = "#8555e3";
        ctx.lineWidth = 4;
        ctx.stroke();
    }

    drawWheel();

    function spinWheel() {
        if (isSpinning) return;
        isSpinning = true;
        spinBtn.disabled = true;
        resultBox.innerText = "두구두구... 과연 오늘의 메뉴는? 🥢";

        const spinDuration = 3500;
        const totalRotations = (5 + Math.random() * 5) * 2 * Math.PI;
        const startAngle = currentAngle;
        const startTime = performance.now();

        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / spinDuration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            currentAngle = startAngle + totalRotations * easeOut;
            drawWheel();

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                isSpinning = false;
                spinBtn.disabled = false;
                const normalizedAngle = (1.5 * Math.PI - (currentAngle % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
                const winningIndex = Math.floor(normalizedAngle / arcSize);
                const winner = foods[winningIndex];
                resultBox.innerHTML = `🎉 당첨! 오늘의 추천 메뉴는 <span style="color:#8555e3; font-size:19px;">[${winner}]</span> 입니다!`;
            }
        }
        requestAnimationFrame(animate);
    }
    </script>
    """
    components.html(roulette_html, height=440)

# [PAGE 2, 3, 4] 일본, 중국, 미국
elif curr_page in ["🍣 일본", "🥟 중국", "🍔 미국"]:
    country_data = {
        "🍣 일본": {
            "title": "일본 여행 플래너 (Japan)", "city": "Tokyo", "curr": "JPY", "lang": "ja-JP",
            "spots": [
                {"name": "도쿄 시부야 스카이", "city": "Tokyo", "tag": "전망대", "desc": "도쿄 시내를 360도로 조망하는 루프탑 전망대"},
                {"name": "교토 아라시야마 대나무숲", "city": "Kyoto", "tag": "자연", "desc": "신비로운 청량감을 주는 치쿠린 산책로"},
                {"name": "오사카 도톤보리", "city": "Osaka", "tag": "미식거리", "desc": "화려한 간판과 맛집이 모여있는 중심가"}
            ],
            "phrases": [
                {"ko": "안녕하세요", "native": "こんにちは", "pron": "곤니치와"},
                {"ko": "이거 얼마인가요?", "native": "これはいくらですか？", "pron": "고레와 이쿠라데스카?"},
                {"ko": "체크인 부탁드립니다", "native": "チェックインをお願いします", "pron": "체쿠인오 오네가이시마스"},
                {"ko": "추천 메뉴가 무엇인가요?", "native": "おすすめは何ですか？", "pron": "오스스메와 난데스카?"},
                {"ko": "화장실이 어디예요?", "native": "トイレはどこですか？", "pron": "토이레와 도코데스카?"}
            ]
        },
        "🥟 중국": {
            "title": "중국 여행 플래너 (China)", "city": "Beijing", "curr": "CNY", "lang": "zh-CN",
            "spots": [
                {"name": "베이징 자금성", "city": "Beijing", "tag": "역사유적", "desc": "황제의 역사가 깃든 세계 최대 규모의 궁궐"},
                {"name": "상하이 와이탄", "city": "Shanghai", "tag": "야경명소", "desc": "황푸강변 근대 건축과 마천루 파노라마"},
                {"name": "청두 판다 생태기지", "city": "Chengdu", "tag": "생태공원", "desc": "귀여운 자이언트 판다 보호 연구 센터"}
            ],
            "phrases": [
                {"ko": "안녕하세요", "native": "你好", "pron": "니하오"},
                {"ko": "얼마인가요?", "native": "多少钱？", "pron": "뚜어샤오 치엔?"},
                {"ko": "고수 빼주세요", "native": "不要香菜", "pron": "부야오 시앙차이"},
                {"ko": "계산서 주세요", "native": "买单", "pron": "마이단"},
                {"ko": "감사합니다", "native": "谢谢", "pron": "씨에씨에"}
            ]
        },
        "🍔 미국": {
            "title": "미국 여행 플래너 (USA)", "city": "New York", "curr": "USD", "lang": "en-US",
            "spots": [
                {"name": "뉴욕 센트럴 파크", "city": "New York", "tag": "도심공원", "desc": "도심 한가운데에서 누리는 여유로운 산책"},
                {"name": "LA 그리피스 천문대", "city": "Los Angeles", "tag": "일몰/야경", "desc": "LA 시내와 할리우드 사인을 조망하는 명소"},
                {"name": "샌프란시스코 금문교", "city": "San Francisco", "tag": "랜드마크", "desc": "태평양과 만을 가로지르는 붉은 현수교"}
            ],
            "phrases": [
                {"ko": "체크인하고 싶습니다", "native": "I'd like to check in, please.", "pron": "아이드 라이크 투 체크인 플리즈"},
                {"ko": "추천 메뉴가 있나요?", "native": "Do you have any recommendations?", "pron": "두 유 해브 애니 레커멘데이션스?"},
                {"ko": "계산서 부탁드립니다", "native": "Check, please.", "pron": "체크, 플리즈"},
                {"ko": "가장 가까운 지하철역이 어디죠?", "native": "Where is the nearest subway station?", "pron": "웨어 이즈 더 니어리스트 서브웨이 스테이션?"},
                {"ko": "사진 한 장 찍어주실 수 있나요?", "native": "Could you take a picture for me?", "pron": "쿠쥬 테이크 어 픽쳐 포 미?"}
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
                item_str = f"[{s['city']}] {s['name']}"
                if item_str not in st.session_state.my_plan:
                    st.session_state.my_plan.append(item_str)
                    save_plans(st.session_state.my_plan)
                    st.success(f"'{s['name']}' 저장 완료")

    st.divider()

    st.markdown("### 🗣️ 여행지 필수 생존 회화 (현지어 오디오 발음)")
    st.caption("버튼을 누르면 실제 현지어 음성(TTS)으로 자연스럽게 들려줍니다.")
    
    ph_cols = st.columns(len(info["phrases"]))
    for idx, ph in enumerate(info["phrases"]):
        with ph_cols[idx]:
            st.markdown(f"""
            <div class="spot-card" style="min-height: 140px;">
                <div style="font-size:11px; color:#6b46a8; font-weight:bold;">{ph['ko']}</div>
                <div style="font-size:15px; font-weight:bold; color:#2c1b42; margin: 4px 0;">{ph['native']}</div>
                <div style="font-size:11px; color:#78668f;">[{ph['pron']}]</div>
            </div>
            """, unsafe_allow_html=True)
            render_tts_button(ph["native"], info["lang"], label="🔊 발음 듣기")

# [PAGE 5] 기타 국가
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

# [PAGE 6] 환율 계산기 & 스마트 일정 빌더
elif curr_page == "🍧 환율 & 일정 플래너":
    st.markdown("<h2 style='color:#3b2359;'>🍧 실시간 환율 & 스마트 일정 빌더</h2>", unsafe_allow_html=True)
    st.caption("환율 계산과 함께 내가 담은 장소들로 맞춤 하루 여행 일정을 자동으로 짜보세요.")
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

    st.divider()

    # 스마트 일정표 생성기 (동일 국가/도시별 맞춤 일정 빌더)
    st.markdown("### 🗓️ 내 플래너 맞춤형 1Day 코스 자동 빌더")
    
    if st.session_state.my_plan:
        grouped_plans = {}
        for item in st.session_state.my_plan:
            if item.startswith("[") and "]" in item:
                region = item[1:item.index("]")]
                spot = item[item.index("]") + 1:].strip()
            else:
                region = "기타"
                spot = item
            
            grouped_plans.setdefault(region, []).append(spot)

        available_regions = list(grouped_plans.keys())
        selected_region = st.selectbox("일정을 생성할 여행지를 선택하세요", available_regions)

        region_spots = grouped_plans[selected_region]

        if st.button(f"✨ [{selected_region}] 맞춤 당일 동선 짜기"):
            times = ["오전 (10:00)", "점심 & 휴식 (12:30)", "오후 (15:00)", "저녁 & 야경 (18:30)", "나이트 (20:30)"]
            
            schedule_data = []
            for i, spot in enumerate(region_spots[:5]):
                schedule_data.append({
                    "시간대": times[i],
                    "일정 / 명소": f"[{selected_region}] {spot}",
                    "구분": "메인 방문지" if i == 0 else "연계 코스"
                })

            if len(region_spots) < 3:
                st.caption(f"💡 [{selected_region}] 관련 장소가 {len(region_spots)}곳만 담겨 있어 기본 동선으로 배치했습니다. 해당 국가 페이지에서 장소를 더 담아보세요!")

            st.markdown(f"#### 🎈 [{selected_region}] 하루 추천 코스")
            df_sched = pd.DataFrame(schedule_data)
            st.dataframe(df_sched, use_container_width=True, hide_index=True)
    else:
        st.info("💡 사이드바나 각 국가 페이지에서 여행지를 담으시면 도시별 맞춤 일정표를 자동으로 구성해 드립니다.")
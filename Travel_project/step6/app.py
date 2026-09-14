import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# -------------------------------------------------------------
# 1. 환경변수(.env) 및 Secrets 동기화
# -------------------------------------------------------------
load_dotenv()

def get_key(name: str) -> str:
    """환경변수 또는 st.secrets에서 API 키를 가져옵니다."""
    val = os.environ.get(name, "")
    if not val:
        try:
            val = st.secrets.get(name, "")
        except Exception:
            val = ""
    return (val or "").strip()

OPENWEATHER_API_KEY = get_key("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = get_key("EXCHANGE_API_KEY")
KAKAO_REST_API_KEY = get_key("KAKAO_REST_API_KEY") or get_key("KAKAO_REST_KEY")
KAKAO_JS_API_KEY = get_key("KAKAO_JS_API_KEY") or get_key("MAP_API_KEY")

st.set_page_config(
    page_title="All-in-One Travel Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 2. API 통신 함수
# -------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def kakao_search_place(query: str):
    """카카오 로컬 API: 키워드 장소 검색"""
    if not KAKAO_REST_API_KEY:
        return None, "KAKAO_REST_API_KEY가 설정되지 않았습니다."
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": query, "size": 10}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        res.raise_for_status()
        return res.json().get("documents", []), None
    except requests.exceptions.RequestException as e:
        return None, f"카카오 장소 검색 오류: {e}"

@st.cache_data(ttl=600, show_spinner=False)
def kakao_search_category(cat_code: str, lat: float, lon: float, radius: int = 1500):
    """카카오 로컬 API: 주변 카테고리(음식점, 카페 등) 검색"""
    if not KAKAO_REST_API_KEY:
        return []
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {
        "category_group_code": cat_code,
        "x": str(lon),
        "y": str(lat),
        "radius": radius,
        "size": 15,
        "sort": "distance"
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        if res.status_code == 200:
            return res.json().get("documents", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=600, show_spinner=False)
def get_weather(lat: float, lon: float):
    """OpenWeather API: 좌표 기반 현재 날씨 조회"""
    if not OPENWEATHER_API_KEY:
        return None, "OPENWEATHER_API_KEY가 설정되지 않았습니다."
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "kr",
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return res.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"날씨 조회 오류: {e}"

@st.cache_data(ttl=600, show_spinner=False)
def get_weather_by_city(city_name: str):
    """도시 이름으로 날씨 조회"""
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
    """ExchangeRate-API: 환율 조회"""
    if not EXCHANGERATE_API_KEY:
        return None, "EXCHANGERATE_API_KEY가 설정되지 않았습니다."
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{base}/{target}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("result") != "success":
            return None, f"환율 조회 실패: {data.get('error-type', '오류')}"
        return data, None
    except requests.exceptions.RequestException as e:
        return None, f"환율 조회 오류: {e}"

# -------------------------------------------------------------
# 3. 진짜 카카오 지도 렌더러 (검증된 Monkey Patch + tryInitMap 구조)
# -------------------------------------------------------------
def render_kakao_map(lat: float, lon: float, place_name: str = "", nearby_places: list = None):
    """카카오 지도 JS SDK 렌더링 (주변 다중 마커 지원)"""
    if not KAKAO_JS_API_KEY:
        st.warning("KAKAO_JS_API_KEY가 설정되지 않아 지도를 표시할 수 없습니다.")
        return

    nearby_json = json.dumps(nearby_places or [], ensure_ascii=False)

    html_code = f"""
    <div id="map" style="width:100%;height:520px;border-radius:12px;background:#f4f4f5;
         display:flex;align-items:center;justify-content:center;color:#888;font-size:13px;border:1px solid #e2e8f0;">
         지도를 불러오는 중...
    </div>
    <script>
        // Mixed Content 방지: document.write 가로채기
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

        function showMapError(msg) {{
            document.getElementById('map').innerHTML =
                '<div style="padding:16px;color:#c00;font-size:13px;line-height:1.6;">' + msg + '</div>';
        }}

        function tryInitMap() {{
            mapTries++;
            var ready = (typeof kakao !== 'undefined')
                && kakao.maps
                && typeof kakao.maps.LatLng === 'function';

            if (ready) {{
                try {{
                    var container = document.getElementById('map');
                    container.innerHTML = '';
                    var centerPos = new kakao.maps.LatLng({lat}, {lon});
                    var options = {{
                        center: centerPos,
                        level: 4
                    }};
                    var map = new kakao.maps.Map(container, options);

                    // 지도 컨트롤
                    map.addControl(new kakao.maps.ZoomControl(), kakao.maps.ControlPosition.RIGHT);
                    map.addControl(new kakao.maps.MapTypeControl(), kakao.maps.ControlPosition.TOPRIGHT);

                    // 1. 메인 중심 마커
                    var mainMarker = new kakao.maps.Marker({{
                        position: centerPos,
                        map: map
                    }});

                    var mainIw = new kakao.maps.InfoWindow({{
                        content: '<div style="padding:8px 12px;font-size:12px;min-width:180px;line-height:1.4;">' +
                                 '<strong style="color:#e11d48;font-size:13px;">📍 {place_name}</strong>' +
                                 '</div>'
                    }});
                    mainIw.open(map, mainMarker);

                    // 2. 주변 편의시설 다중 마커
                    if (nearbyData && nearbyData.length > 0) {{
                        var bounds = new kakao.maps.LatLngBounds();
                        bounds.extend(centerPos);
                        var activeIw = null;

                        nearbyData.forEach(function(p) {{
                            var pPos = new kakao.maps.LatLng(p.y, p.x);
                            bounds.extend(pPos);

                            var marker = new kakao.maps.Marker({{
                                position: pPos,
                                map: map
                            }});

                            var content = '<div style="padding:8px 10px;font-size:12px;max-width:220px;line-height:1.4;">' +
                                          '<b>' + p.place_name + '</b><br>' +
                                          '<span style="font-size:11px;color:#64748b;">' + (p.road_address_name || p.address_name) + '</span><br>' +
                                          (p.phone ? '<span style="color:#059669;font-size:11px;">📞 ' + p.phone + '</span><br>' : '') +
                                          (p.place_url ? '<a href="' + p.place_url + '" target="_blank" style="color:#2563eb;font-weight:bold;font-size:11px;text-decoration:none;">상세보기 ↗</a>' : '') +
                                          '</div>';

                            var iw = new kakao.maps.InfoWindow({{
                                content: content,
                                removable: true
                            }});

                            kakao.maps.event.addListener(marker, 'click', function() {{
                                if (activeIw) activeIw.close();
                                iw.open(map, marker);
                                activeIw = iw;
                            }});
                        }});

                        map.setBounds(bounds);
                    }}
                }} catch (e) {{
                    showMapError('지도 초기화 오류: ' + e.message);
                }}
            }} else if (mapTries < 25) {{
                setTimeout(tryInitMap, 200);
            }} else {{
                showMapError('지도를 불러오지 못했습니다. 카카오 개발자 콘솔 Web 도메인 등록 상태를 확인해주세요.');
            }}
        }}

        tryInitMap();
    </script>
    """
    components.html(html_code, height=540)

# -------------------------------------------------------------
# 4. 세션 상태 초기화
# -------------------------------------------------------------
preset_defaults = {
    "경복궁": {"x": "126.9770", "y": "37.5796", "place_name": "경복궁", "road_address_name": "서울 종로구 사직로 161", "place_url": "https://place.map.kakao.com/8129210"},
    "해운대 해수욕장": {"x": "129.1604", "y": "35.1587", "place_name": "해운대 해수욕장", "road_address_name": "부산 해운대구 우동", "place_url": "https://place.map.kakao.com/8051280"},
    "성산일출봉": {"x": "126.9427", "y": "33.4585", "place_name": "성산일출봉", "road_address_name": "제주 서귀포시 성산읍 일출로 284-12", "place_url": "https://place.map.kakao.com/8119865"}
}

if "selected_place" not in st.session_state:
    st.session_state.selected_place = preset_defaults["경복궁"]

# -------------------------------------------------------------
# 5. 사이드바 (API 상태 및 국가 메뉴)
# -------------------------------------------------------------
with st.sidebar:
    st.title("✈️ 여행 대시보드")
    menu = st.radio("여행지 선택", ["🇰🇷 대한민국 (Home)", "🇯🇵 일본", "🇨🇳 중국", "🇺🇸 미국", "💱 실시간 환율 계산기"])
    st.divider()

    st.markdown("### 🔑 API 연결 상태")
    st.caption(" | ".join([
        "✅ 날씨" if OPENWEATHER_API_KEY else "❌ 날씨",
        "✅ 환율" if EXCHANGERATE_API_KEY else "❌ 환율",
        "✅ 카카오" if (KAKAO_REST_API_KEY and KAKAO_JS_API_KEY) else "❌ 카카오"
    ]))
    st.divider()
    st.caption("All-in-One Global Travel Dashboard")

# -------------------------------------------------------------
# 6. 메인 화면 분기
# -------------------------------------------------------------
if menu == "🇰🇷 대한민국 (Home)":
    st.title("🇰🇷 대한민국 여행 센터 (Home)")
    st.link_button("🌐 대한민국 구석구석 (공식 관광정보)", "https://korean.visitkorea.or.kr")
    st.write("")

    # 실시간 주요 도시 날씨 위젯
    st.markdown("#### 🌤️ 국내 주요 거점 실시간 날씨")
    w_cols = st.columns(3)
    for idx, (c_kr, c_en) in enumerate([("서울", "Seoul"), ("부산", "Busan"), ("제주", "Jeju")]):
        w_data = get_weather_by_city(c_en)
        with w_cols[idx]:
            if w_data and "main" in w_data:
                st.metric(
                    label=f"{c_kr} ({c_en})",
                    value=f"{w_data['main']['temp']}°C",
                    delta=w_data["weather"][0]["description"] if w_data.get("weather") else ""
                )
                st.caption(f"습도: {w_data['main']['humidity']}% | 체감: {w_data['main']['feels_like']}°C")
            else:
                st.metric(label=f"{c_kr} ({c_en})", value="연결 대기중")
    st.divider()

    # 장소 검색 및 추천 명소
    col_left, col_right = st.columns([5, 7], gap="medium")

    with col_left:
        st.subheader("🔍 장소 탐색")
        user_query = st.text_input("직접 장소 검색", placeholder="예: 해운대 맛집, 성수동 카페, 제주 공항")
        
        selected_preset = st.selectbox("추천 명소 빠른 선택", list(preset_defaults.keys()))
        if st.button("추천 명소로 이동"):
            st.session_state.selected_place = preset_defaults[selected_preset]

        if user_query.strip():
            places, err = kakao_search_place(user_query.strip())
            if err:
                st.error(err)
            elif places:
                opts = [f"{p['place_name']} ({p.get('road_address_name') or p.get('address_name')})" for p in places]
                picked_idx = st.selectbox("🎯 검색 결과 선택", range(len(opts)), format_func=lambda i: opts[i])
                st.session_state.selected_place = places[picked_idx]
            else:
                st.warning("검색 결과가 없습니다.")

        place = st.session_state.selected_place
        lat = float(place["y"])
        lon = float(place["x"])
        name = place["place_name"]
        address = place.get("road_address_name") or place.get("address_name") or "-"

        with st.container(border=True):
            st.caption("선택된 중심 장소")
            st.markdown(f"### 📍 {name}")
            st.write(f"**주소:** {address}")
            if place.get("place_url"):
                st.link_button("카카오맵에서 상세 보기 ↗", place["place_url"])

        # 주변 편의시설 필터링
        cat_selected = st.radio(
            "주변 편의시설 필터링 (반경 1.5km)",
            ["선택 안 함", "🍴 맛집 (식당)", "☕ 카페", "🏪 편의점"],
            horizontal=True
        )
        cat_codes = {"🍴 맛집 (식당)": "FD6", "☕ 카페": "CE7", "🏪 편의점": "CS2"}
        nearby_places = []
        if cat_selected in cat_codes:
            nearby_places = kakao_search_category(cat_codes[cat_selected], lat, lon)

        if nearby_places:
            st.markdown(f"**주변 탐색 목록 ({len(nearby_places)}곳)**")
            with st.container(height=240):
                for i, p in enumerate(nearby_places, 1):
                    dist = f"({p['distance']}m)" if p.get("distance") else ""
                    with st.expander(f"{i}. {p['place_name']} {dist}"):
                        st.write(f"주소: {p.get('road_address_name') or p.get('address_name')}")
                        if p.get("phone"):
                            st.write(f"전화: {p['phone']}")
                        if p.get("place_url"):
                            st.link_button("카카오맵 열기", p["place_url"])

    with col_right:
        st.subheader("🗺️ 카카오 지도 뷰")
        render_kakao_map(lat, lon, place_name=name, nearby_places=nearby_places)

elif menu in ["🇯🇵 일본", "🇨🇳 중국", "🇺🇸 미국"]:
    country_info = {
        "🇯🇵 일본": {"name": "일본 (Japan)", "city": "Tokyo", "lat": 35.6762, "lon": 139.6503, "curr": "JPY"},
        "🇨🇳 중국": {"name": "중국 (China)", "city": "Beijing", "lat": 39.9042, "lon": 116.4074, "curr": "CNY"},
        "🇺🇸 미국": {"name": "미국 (USA)", "city": "New York", "lat": 40.7128, "lon": -74.0060, "curr": "USD"}
    }
    c_data = country_info[menu]
    st.title(f"{c_data['name']} 여행 정보")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"🌤️ {c_data['city']} 실시간 날씨")
        w, werr = get_weather(c_data["lat"], c_data["lon"])
        if w and "main" in w:
            st.metric("현재 기온", f"{w['main']['temp']}°C", delta=w['weather'][0]['description'])
            st.write(f"- 체감 온도: {w['main']['feels_like']}°C")
            st.write(f"- 습도: {w['main']['humidity']}%")
            st.write(f"- 풍속: {w['wind']['speed']} m/s")
        else:
            st.info("날씨 데이터를 불러오는 중입니다.")

    with col2:
        st.subheader(f"💱 {c_data['curr']} 실시간 환율 (기준: KRW)")
        r_data, rerr = get_exchange_rate("KRW", c_data["curr"])
        if r_data:
            rate = r_data["conversion_rate"]
            st.metric(f"1,000 KRW → {c_data['curr']}", f"{1000 * rate:,.2f} {c_data['curr']}")
            st.caption(f"1 KRW = {rate:.4f} {c_data['curr']}")
        else:
            st.info("환율 데이터를 불러오는 중입니다.")

elif menu == "💱 실시간 환율 계산기":
    st.title("💱 글로벌 실시간 환율 계산기")
    currency_list = ["KRW", "USD", "JPY", "CNY", "EUR", "GBP", "AUD", "CAD", "THB", "VND"]
    
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        base_c = st.selectbox("보내는 통화 (기준)", currency_list, index=0)
    with c2:
        target_c = st.selectbox("받는 통화 (변환)", currency_list, index=1)
    with c3:
        amt = st.number_input("금액 입력", min_value=0.0, value=10000.0, step=1000.0)

    if base_c == target_c:
        st.info("기준 통화와 변환 통화가 동일합니다.")
    else:
        rate_info, rerr = get_exchange_rate(base_c, target_c)
        if rerr:
            st.error(rerr)
        elif rate_info:
            c_rate = rate_info["conversion_rate"]
            result = amt * c_rate
            st.metric(label=f"{amt:,.0f} {base_c} → {target_c}", value=f"{result:,.2f} {target_c}")
            st.caption(f"적용 환율: 1 {base_c} = {c_rate:.4f} {target_c}")
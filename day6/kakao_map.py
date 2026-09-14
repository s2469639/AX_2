import os
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

# 1. 환경변수 불러오기
load_dotenv()
REST_API_KEY = os.getenv("MAP_API_KEY")

st.set_page_config(page_title="카카오 장소 검색 지도", layout="wide")
st.title("📍 카카오 장소 검색")

if not REST_API_KEY:
    st.error(".env 파일에 MAP_API_KEY가 설정되어 있지 않습니다.")
    st.stop()

# 2. 카카오 REST API: 1개 결과만 요청
def search_place_by_keyword(query):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {REST_API_KEY}"}
    params = {"query": query, "size": 1}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("documents", [])
    else:
        st.error(f"API 요청 실패 (코드: {response.status_code}): {response.text}")
        return []

# 3. UI 배치 (검색창도 지도의 너비와 맞춰 중앙 정렬)
_, center_col, _ = st.columns([1, 6, 1])

with center_col:
    keyword = st.text_input(
        "검색할 장소나 주소를 입력하세요:", 
        value="", 
        placeholder="예: 판교역, 강남역 스타벅스 (미입력 시 기본 서울시청)"
    )

# 4. 마커 정보 및 지도 중심 기본값: 서울시청
marker_info = {
    "name": "서울특별시청",
    "address": "서울 중구 세종대로 110",
    "lat": 37.5665,
    "lng": 126.9780
}
zoom_level = 15

# 검색어가 입력된 경우 정보 업데이트
if keyword.strip():
    places = search_place_by_keyword(keyword.strip())
    if places:
        target = places[0]
        marker_info = {
            "name": target["place_name"],
            "address": target.get("road_address_name") or target.get("address_name"),
            "lat": float(target["y"]),
            "lng": float(target["x"])
        }
        zoom_level = 16
    else:
        st.warning(f"'{keyword}'에 대한 검색 결과가 없어 기본 위치(서울시청)를 유지합니다.")

# 5. Folium 지도 생성 및 마커 1개 추가
m = folium.Map(
    location=[marker_info["lat"], marker_info["lng"]], 
    zoom_start=zoom_level
)

popup_html = f"""
<div style="font-family: sans-serif; font-size: 13px; line-height: 1.4; min-width: 150px;">
    <h4 style="margin: 0 0 5px 0; color: #1E88E5;">{marker_info['name']}</h4>
    <b>주소:</b> {marker_info['address']}
</div>
"""

folium.Marker(
    location=[marker_info["lat"], marker_info["lng"]],
    popup=folium.Popup(popup_html, max_width=300),
    tooltip=marker_info["name"],
    icon=folium.Icon(color="red", icon="star")
).add_to(m)

# 6. 화면 중앙 컬럼에 지도 출력 (너비는 컨테이너에 맞춤)
with center_col:
    st_folium(m, use_container_width=True, height=520)
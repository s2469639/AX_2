import pandas as pd
import pydeck as pdk
import streamlit as st

def render_kakao_map(lat: float, lng: float, name: str, addr: str, places: list, is_interactive: bool = True):
    """
    HTML/iframe 없이 Streamlit의 pydeck_chart를 사용하여 지도를 렌더링합니다.
    - 메인 중심지: 빨간색 큰 마커
    - 주변 시설(식당/카페/편의점): 파란색 마커
    """
    data = []
    
    # 1. 기준 중심지 장소 마커 (빨간색)
    data.append({
        "name": f"📍 {name}",
        "address": addr,
        "phone": "-",
        "lat": float(lat),
        "lng": float(lng),
        "color": [239, 68, 68, 220],  # Red
        "radius": 18
    })
    
    # 2. 주변 탐색 장소 마커 (파란색)
    if places:
        for p in places:
            data.append({
                "name": p.get("name", "장소"),
                "address": p.get("address", ""),
                "phone": p.get("phone", "") or "전화번호 정보 없음",
                "lat": float(p.get("lat")),
                "lng": float(p.get("lng")),
                "color": [37, 99, 235, 200],  # Blue
                "radius": 14
            })
            
    df = pd.DataFrame(data)
    
    # 지도 시점(뷰포트) 설정
    view_state = pdk.ViewState(
        latitude=lat,
        longitude=lng,
        zoom=14 if is_interactive else 13,
        pitch=0
    )
    
    # 산포도 마커 레이어
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lng", "lat"],
        get_color="color",
        get_radius="radius",
        radius_min_pixels=6,
        radius_max_pixels=25,
        pickable=True
    )
    
    # 마커 위에 마우스를 올렸을 때 나타나는 툴팁
    tooltip = {
        "html": "<b>{name}</b><br/>주소: {address}<br/>전화: {phone}",
        "style": {
            "backgroundColor": "#1e293b",
            "color": "white",
            "fontSize": "12px",
            "borderRadius": "8px",
            "padding": "8px 12px"
        }
    }
    
    # Streamlit 네이티브 덱 렌더링
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"
    )
    
    st.pydeck_chart(deck, height=580)
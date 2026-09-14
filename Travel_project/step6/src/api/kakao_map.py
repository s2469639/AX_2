import folium
from streamlit_folium import st_folium

def render_kakao_map(js_key: str, lat: float, lng: float, name: str, addr: str, places: list, is_interactive: bool = True):
    """
    Streamlit 배포 환경에서 도메인 인증 오류 없이 동작하는 인터랙티브 지도 렌더러
    """
    # 1. 중심 지도 생성
    m = folium.Map(
        location=[lat, lng],
        zoom_start=14,
        tiles="OpenStreetMap"
    )

    # 2. 중심 명소 마커 (빨간색 핀)
    main_html = f"""
    <div style="font-size: 13px; font-weight: bold; color: #e11d48; min-width: 150px;">
        📍 {name}<br>
        <span style="font-size: 11px; color: #475569; font-weight: normal;">{addr}</span>
    </div>
    """
    folium.Marker(
        [lat, lng],
        popup=folium.Popup(main_html, max_width=250),
        tooltip=name,
        icon=folium.Icon(color="red", icon="star")
    ).add_to(m)

    # 3. 주변 검색 편의시설 마커 (파란색 핀)
    if places:
        for p in places:
            phone_text = f"<br><span style='color:#059669; font-size:11px;'>📞 {p['phone']}</span>" if p.get('phone') else ""
            link_text = f"<br><a href='{p['url']}' target='_blank' style='color:#2563eb; font-weight:bold; font-size:11px;'>상세보기 ↗</a>" if p.get('url') else ""
            
            popup_content = f"""
            <div style="font-size: 12px; min-width: 140px;">
                <b>{p['name']}</b><br>
                <span style="font-size: 11px; color: #64748b;">{p['address']}</span>
                {phone_text}
                {link_text}
            </div>
            """
            folium.Marker(
                [p["lat"], p["lng"]],
                popup=folium.Popup(popup_content, max_width=220),
                tooltip=p["name"],
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)

    # 4. Streamlit 화면 출력
    st_folium(m, width=None, height=580, returned_objects=[])
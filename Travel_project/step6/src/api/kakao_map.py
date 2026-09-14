import json
import streamlit.components.v1 as components

def render_kakao_map(js_key: str, lat: float, lng: float, name: str, addr: str, places: list, is_interactive: bool = True):
    """
    진짜 카카오 지도 JavaScript SDK를 호출하여 노란색/초록색 고유 타일 지도를 렌더링합니다.
    """
    places_json = json.dumps(places, ensure_ascii=False)

    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="referrer" content="always">
    <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
    <style>
        * {{ box-sizing: border-box; }}
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif; }}
        #map {{ width: 100%; height: 580px; border-radius: 12px; border: 1px solid #cbd5e1; }}
        .custom-overlay {{
            position: relative;
            bottom: 45px;
            border-radius: 8px;
            background: #ffffff;
            border: 1px solid #0f172a;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 8px 12px;
            font-size: 12px;
            color: #1e293b;
            white-space: nowrap;
        }}
        .custom-overlay b {{ color: #1e3a8a; font-size: 13px; display: block; margin-bottom: 2px; }}
        .custom-overlay .addr {{ color: #64748b; font-size: 11px; }}
        .custom-overlay a {{ color: #2563eb; text-decoration: none; font-weight: bold; margin-top: 4px; display: inline-block; }}
    </style>
</head>
<body>
    <div id="map"></div>

    <script>
        // 프로토콜을 강제로 HTTPS로 지정하여 카카오 스크립트 동적 로드
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://dapi.kakao.com/v2/maps/sdk.js?appkey={js_key}&autoload=false';
        
        script.onload = function() {{
            kakao.maps.load(function() {{
                var mapContainer = document.getElementById('map');
                var mapCenter = new kakao.maps.LatLng({lat}, {lng});
                
                var mapOption = {{
                    center: mapCenter,
                    level: 4
                }};
                
                // 진짜 카카오 지도 객체 생성
                var map = new kakao.maps.Map(mapContainer, mapOption);

                if ({str(is_interactive).lower()}) {{
                    var zoomControl = new kakao.maps.ZoomControl();
                    map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);
                    var mapTypeControl = new kakao.maps.MapTypeControl();
                    map.addControl(mapTypeControl, kakao.maps.ControlPosition.TOPRIGHT);
                }}

                // 1. 메인 중심지 마커 생성
                var mainMarker = new kakao.maps.Marker({{
                    position: mapCenter,
                    map: map
                }});

                // 메인 인포윈도우
                var mainIwContent = '<div style="padding:10px;font-size:12px;width:200px;line-height:1.4;">' +
                                    '<strong style="color:#e11d48;font-size:13px;">📍 {name}</strong><br>' +
                                    '<span style="color:#475569;">{addr}</span>' +
                                    '</div>';
                var mainInfowindow = new kakao.maps.InfoWindow({{
                    position: mapCenter,
                    content: mainIwContent
                }});
                mainInfowindow.open(map, mainMarker);

                // 2. 주변 편의시설 (맛집/카페/편의점) 마커 생성
                var places = {places_json};
                if (places && places.length > 0) {{
                    var bounds = new kakao.maps.LatLngBounds();
                    bounds.extend(mapCenter);

                    var activeInfowindow = null;

                    places.forEach(function(place) {{
                        var placePosition = new kakao.maps.LatLng(place.lat, place.lng);
                        bounds.extend(placePosition);

                        var marker = new kakao.maps.Marker({{
                            position: placePosition,
                            map: map
                        }});

                        var content = '<div style="padding:8px 10px;font-size:12px;max-width:220px;line-height:1.4;">' +
                                      '<b>' + place.name + '</b><br>' +
                                      '<span style="font-size:11px;color:#64748b;">' + place.address + '</span><br>' +
                                      (place.phone ? '<span style="color:#059669;font-size:11px;">📞 ' + place.phone + '</span><br>' : '') +
                                      (place.url ? '<a href="' + place.url + '" target="_blank" style="color:#2563eb;font-weight:bold;font-size:11px;text-decoration:none;">상세보기 ↗</a>' : '') +
                                      '</div>';

                        var infowindow = new kakao.maps.InfoWindow({{
                            content: content,
                            removable: true
                        }});

                        kakao.maps.event.addListener(marker, 'click', function() {{
                            if (activeInfowindow) {{
                                activeInfowindow.close();
                            }}
                            infowindow.open(map, marker);
                            activeInfowindow = infowindow;
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

    components.html(html_code, height=600)
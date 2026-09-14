# folium으로 지도에 마커를 표시하는 예제 코드
# import folium 
# 서울 시내 명소 4곳의 좌표 (위도/경도)와 이름을 리스트로 받아
# folium 지도를 만들고 
# 각 좌표에 이름표가 붙은 마커를 찍은 뒤, 
# 지도를 basic_map.html로 파일로 저장하는 예제 코드입니다. 
# 저장된 basic_map.html 파일을 웹 브라우저로 열어서 확인
# python app.py 

import folium 
import webbrowser

# 서울 시내 명소 4곳 이름, 위도, 경도 샘플데이터
places = [
    {"이름": "서울숲", "위도": 37.5443, "경도": 127.0374},
    {"이름": "낙산공원", "위도": 37.5802, "경도": 127.0082},
    {"이름": "여의도 한강공원", "위도": 37.5281, "경도": 126.9347},
    {"이름": "경복궁", "위도": 37.5796, "경도": 126.9770}
]

# 지도의 시작 중심 좌표 (경복궁 기준) 지정해서 folium 지도 객체 생성
# 숫자가 클수록 더 가깝게 보여준다. 
# 경복궁 기준 중심 좌표 (위도, 경도)
palace = [37.5796, 126.9770]
# folium 지도 객체 생성 (zoom_start가 클수록 고해상도로 가까이 보여짐)
map = folium.Map(location=palace, zoom_start=13, tiles='Esri.WorldStreetMap')

# 3. 리스트를 하나씩 꺼내며 지도 위에 마커 추가
for place in places:
    folium.Marker(
        location=[place["위도"], place["경도"]],
        popup=place["이름"],
        tooltip=place["이름"],
        icon=folium.Icon(color='darkred', icon='info-sign')  
    ).add_to(map)


# 4. HTML 파일로 저장
file_name = "basic_map.html"
map.save(file_name)

# 5. 웹 브라우저로 열기
webbrowser.open(file_name)
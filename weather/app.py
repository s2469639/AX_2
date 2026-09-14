# 날씨 API 실습 
# OpenWeatherMap 현재 날씨 API로 특정 도시의 날씨를 가져와 출력한다. 
# 사전준비: OpenWeatherMap 가입 후, API 발급
# .env는 외부에 만들어놓은 환경변수
# pip install requests python-dotenv
# .env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY = 발급받은 API키 
#.env.example OPENWEATHER_API_KEY = your_key
# .env.example 받아서 .env로 이름바꾸고 자기 API를 채운다. 

import os
import requests
import streamlit as st
from dotenv import find_dotenv, load_dotenv

# --- 1. .env 파일 자동 탐색 및 환경변수 로드 ---
# 현재 위치부터 상위 디렉터리를 탐색해 test_git 폴더의 .env를 자동으로 찾아옵니다.
env_file = find_dotenv()
load_dotenv(env_file)

API_KEY = os.getenv('OPENWEATHER_API_KEY')

# --- 2. Streamlit UI 구성 ---
st.title("🌤️ 실시간 날씨 조회 앱")

if not API_KEY:
    st.error("`.env` 파일에서 API 키를 찾을 수 없습니다. `.env` 파일 안에 `OPENWEATHER_API_KEY=발급받은키` 형식으로 저장되어 있는지 확인해주세요.")
    st.stop()

# 도시 이름 입력 (영문 기준, 예: Seoul, London, Tokyo)
city = st.text_input("도시 이름을 영어로 입력하세요:", value="Seoul")

if st.button("날씨 확인"):
    # 섭씨 온도(metric) 및 한국어 설명(lang=kr) 파라미터 적용
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        icon_code = data['weather'][0]['icon']
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        
        st.subheader(f"{city}의 현재 날씨")
        st.image(icon_url, width=100)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="현재 기온", value=f"{temp}°C")
            st.metric(label="체감 기온", value=f"{feels_like}°C")
        with col2:
            st.metric(label="날씨 상태", value=weather_desc)
            st.metric(label="습도", value=f"{humidity}%")
            
    elif response.status_code == 404:
        st.warning("도시를 찾을 수 없습니다. 철자를 확인해주세요.")
    elif response.status_code == 401:
        st.error("API 키가 올바르지 않거나 아직 활성화되지 않았습니다. (키 발급 직후 약 10분~2시간 정도 소요될 수 있습니다)")
    else:
        st.error(f"날씨 정보를 불러오지 못했습니다. (에러 코드: {response.status_code})")
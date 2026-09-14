import os
import requests
import streamlit as st

def get_weather(city_name: str):
    """
    OpenWeatherMap API를 호출하여 도시 날씨 정보를 반환합니다.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": ".env에 OPENWEATHER_API_KEY가 설정되지 않았습니다."}
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",  # 섭씨 온도
        "lang": "kr"         # 한국어 날씨 설명
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            "city": data.get("name"),
            "temp": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "icon_url": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"날씨 데이터를 불러오지 못했습니다: {e}"}
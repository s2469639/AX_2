import streamlit as st
from src.data.country_data import COUNTRIES_DATA
from src.components.ui_elements import render_country_card

def show():
    st.title("홈 - 대한민국")
    st.markdown("여행 서비스에 오신 것을 환영합니다. 사이드바에서 원하는 국가를 선택해 상세 정보와 공식 여행 포털을 탐색해 보세요.")
    st.divider()
    
    korea_data = COUNTRIES_DATA["korea"]
    render_country_card(korea_data)
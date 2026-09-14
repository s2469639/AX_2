import streamlit as st
from src.data.country_data import COUNTRIES_DATA
from src.components.ui_elements import render_country_card

def show():
    st.title("일본 여행 가이드")
    st.divider()
    japan_data = COUNTRIES_DATA["japan"]
    render_country_card(japan_data)
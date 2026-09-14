import streamlit as st
from src.data.country_data import COUNTRIES_DATA
from src.components.ui_elements import render_country_card

def show():
    st.title("중국 여행 가이드")
    st.divider()
    china_data = COUNTRIES_DATA["china"]
    render_country_card(china_data)
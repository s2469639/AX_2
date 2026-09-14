import streamlit as st
from src.data.country_data import COUNTRIES_DATA
from src.components.ui_elements import render_country_card

def show():
    st.title("미국 여행 가이드")
    st.divider()
    usa_data = COUNTRIES_DATA["usa"]
    render_country_card(usa_data)
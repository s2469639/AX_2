import streamlit as st
from com.country_card import render_country_page

render_country_page(
    flag = '🥟',
    country_name = '중국',
    country_description = '중국은 관광명소도 많고 마라탕이 맛있습니다.',
    country_url = 'https://www.mct.gov.cn'
)
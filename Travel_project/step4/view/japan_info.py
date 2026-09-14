import streamlit as st
from com.country_card import render_country_page

render_country_page(
    flag='🍣',
    country_name='일본',
    country_description='가까운 거리에서 온천, 식도락, 그리고 고즈넉한 전통 거리를 즐길 수 있는 여행지입니다.',
    country_url='https://www.japan.travel/ko/kr'
)
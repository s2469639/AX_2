import streamlit as st
from com.country_card import render_country_page

render_country_page(
    flag = '🍲',
    country_name = '한국',
    country_description = '대한민국은 아름다운 사계절과 다채로운 K-컬처, 맛있는 음식이 가득한 나라입니다.',
    country_url = 'https://korean.visitkorea.or.kr'
)
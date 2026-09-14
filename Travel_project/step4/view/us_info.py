import streamlit as st
from com.country_card import render_country_page

render_country_page(
    flag='🍔',
    country_name='미국',
    country_description='광활한 대자연 국립공원부터 화려한 대도시까지 다채로운 매력을 지닌 나라입니다.',
    country_url='https://www.gousa.or.kr'
)
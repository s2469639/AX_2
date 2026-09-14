import streamlit as st
from src.pages import home, china, japan, usa

# 1. st.Page 등록 시 고유한 url_path 지정
page_home = st.Page(
    home.show, 
    title="대한민국 (Home)", 
    icon="🍲", 
    url_path="korea",
    default=True
)

page_china = st.Page(
    china.show, 
    title="중국 여행", 
    icon="🥟",
    url_path="china"
)

page_japan = st.Page(
    japan.show, 
    title="일본 여행", 
    icon="🍣",
    url_path="japan"
)

page_usa = st.Page(
    usa.show, 
    title="미국 여행", 
    icon="🍔",
    url_path="usa"
)

# 2. 내비게이션 구성
pg = st.navigation({
    "메인": [page_home],
    "해외 여행지": [page_china, page_japan, page_usa]
})

# 3. 브라우저 탭 설정
st.set_page_config(
    page_title="글로벌 여행 가이드",
    page_icon="🌏",
    layout="wide"
)

# 4. 선택된 페이지 실행
pg.run()
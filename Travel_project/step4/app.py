from pathlib import Path
import streamlit as st

st.set_page_config(page_title='떠나자 세계여행 시즌2', page_icon='✈️')

home_info = st.Page('view/home_info.py',title = '홈', icon = '🍲', default = True)
china_info = st.Page('view/china_info.py',title = '중국', icon = '🥟')
japan_info = st.Page('view/japan_info.py',title = '일본', icon = '🍣')
us_info = st.Page('view/us_info.py',title = '미국', icon = '🍔')
pg = st.navigation([home_info, china_info, japan_info, us_info])
pg.run()
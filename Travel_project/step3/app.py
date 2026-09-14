from pathlib import Path
import streamlit as st

st.set_page_config(page_title='떠나자 세계여행 시즌2', page_icon='✈️')

BASE_DIR = Path(__file__).parent

korea = st.Page(str(BASE_DIR / 'view' / 'korea.py'), title='Korea', icon='🍲', default=True)
us = st.Page(str(BASE_DIR / 'view' / 'us.py'), title='USA', icon='🍔')
china = st.Page(str(BASE_DIR / 'view' / 'china.py'), title='China', icon='🥟')
japan = st.Page(str(BASE_DIR / 'view' / 'japan.py'), title='Japan', icon='🍣')

pg = st.navigation([korea, us, china, japan])
pg.run()
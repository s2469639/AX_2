import streamlit as st

# 단독 실행 시에만 필요하고 합칠 때는 충돌하므로 주석 처리
# st.set_page_config(page_title='떠나자 세계여행 시즌2', page_icon='🌎')

# 사이드바 라디오 버튼 구성
menu = st.sidebar.radio('메뉴', ['홈', '미국', '중국', '일본'])

# 메뉴별 분기 및 링크 버튼
if menu == "홈":
    st.title('대한민국 🇰🇷')
    st.write('대한민국은 동아시아에 위치한 아름다운 사계절을 가진 나라입니다.')
    st.link_button('대한민국 관광공사 바로가기', 'https://korean.visitkorea.or.kr')

elif menu == '미국':
    st.title('미국 🇺🇸')
    st.write('미국은 북아메리카에 위치한 50개 주로 이루어진 연방 공화국입니다.')
    st.link_button('미국 공식 관광청 바로가기', 'https://www.gousa.or.kr')

elif menu == '중국':
    st.title('중국 🇨🇳')
    st.write('중국은 동아시아에 위치하며 유구한 역사와 문화를 자랑하는 나라입니다.')
    st.link_button('중국 문화관광부 바로가기', 'https://www.mct.gov.cn')

elif menu == '일본':
    st.title('일본 🇯🇵')
    st.write('일본은 동아시아에 위치한 섬나라로 다채로운 미식과 관광지로 유명합니다.')
    st.link_button('일본 정부관광국 바로가기', 'https://www.japan.travel/ko/kr/')
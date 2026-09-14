import streamlit as st
# streamlit run 파일명.py # 실행방법: 터미널 cmd


# st.title("내용")은 페이지에서 가장 크고 굵은 제목을 만든다. (h1 느낌)
st.title("무역데이터 부트캠프 자기소개")

# st.header("내용")은 타이틀보다 한단계 작은 큰 제목(h2 느낌)
st.header("안녕하세요 스트림릿으로 만든 첫 페이지 야호 (❁´◡`❁)")

# st.subheader("내용") header보다 한 단계 작은 큰 제목(h3 느낌)
st.subheader('오늘 배운 것: 파이썬 설치😁👍')

# st.text('내용') 꾸밈이 전혀 없는 순수 텍스트를 출력
st.text("st.text로 출력했지요. 집에 슬슬 갈 시간이네요~")

# st.caption('내용') 아주 작은 글씨로 보조 설명ㅇ을 넣을 때 
st.caption('울트라 캡숑캡숑')

# st.markdown("") 마크다운 문법 굵게, 기울임, 링크, 목록
st.markdown(
    """
    ### 마크다운으로 자기소개 작성
    - **이름** : 홍길동
    - **관심분야** : *데이터 분석* 
    - **목표** : 나만의 대시보드 만들기
    - 참고 링크 : [네이버](https://www.naver.com)
""") 
# """마크다운 문법""" 부분 주석
st.markdown('---')

st.subheader('오늘 배운 한 줄 코드')
st.code(
    """
    st.title("Hello Streamlit!")
"""
)
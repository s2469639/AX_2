# random 모듈을 이용해서 1~45 중 중복 없는 번호 6개를 뽑고
# 자료 구조 list, set -> 차이점: 중복이 되냐 안 되냐
# set이 중복이 안 되므로 set 사용, 버튼을 누르면 5세트를 한번에 생성
# datetime 으로 생성시간. 
# 로또 버전 1
# 로또 버전 2

import streamlit as st
import random 
from datetime import datetime 

st.title('두근두근 로또 번호')
st.caption('버튼을 누르시면 1 ~ 45 중복 없는 번호 6개짜리 세트를 생성합니다.')

def lotto_one_set() -> list:
    '1 ~ 45에서 중복 없이 번호 6개 뽑아 정렬된 리스트로 반환'
    number = set[int]()
    while len(number) <6 :  
        number.add(random.randint(1,45)) # 1이상 45 이하 정수 하나 뽑기
    return sorted(number)


st.markdown('---')
button = st.button('🍀5세트 번호 생성하기', key = 'lotto_button')

def format_ball(num: int) -> str:
    if num <= 10:   emoji = "🟡" # 1~10
    elif num <= 20: emoji = "🔵" # 11~20
    elif num <= 30: emoji = "🔴" # 21~30
    elif num <= 40: emoji = "⚪" # 31~40
    else:           emoji = "🟢" # 41~45
    return f"{emoji} {num:02d}"

if button: 
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.write(f'생성시각 : **{now_str}**')
    for set_index in range(1,6):
        lotto_num = lotto_one_set()
        balls_str = "   ".join([format_ball(n) for n in lotto_num])
        st.write(f'**{set_index}세트** : {balls_str}')


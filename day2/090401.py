import streamlit as st
import pandas as pd
import os 

csv_path = os.path.join(os.path.dirname(__file__), '..', 'common', 'raw_trade_data.csv') 
# trade = os.path.join(os.path.dirname(__file__), 'raw_trade_data.csv') 같은 경로라면
# __file__: 지금 우리가 문서 작성하는 이 파일을 기준으로. 
# 환율 샘플 데이터: 딕셔너리로 표 만들기
df_trade = pd.read_csv(csv_path, encoding = 'utf-8')

exchange_data = {
    '통화':['USD', 'EUR', 'JPY(100엔)', 'CNY'],
    '환율(KRW)':[f'{x:,}' for x in [1390.5, 1503.2, 930.8, 191.3]],
    '전일대비' :[+5.2, -3.1, -2.2, +0.8]
}
df_exchange = pd.DataFrame(exchange_data)

st.title("🤑 오늘의 환율 대시보드")
st.caption('아래 데이터는 실제 환율이 아닌 실습용 데이터입니다.')

st.header('1) 환율 표 보기')
st.write('▶ st.dataframe (상호작용 가능한 표)')
st.dataframe(df_exchange, use_container_width= False)

st.write('▶ st.table (정적인 표)')
st.table(df_exchange)
st.markdown('---')

st.header('2) 주요 환율 카드 (st.metric)')
# st.metric(라벨, 현재값, 증감값)
col1, col2, col3 = st.columns(3)

with col1 :
    st.metric(label = "USD/KRW", value = "1,390.5", delta= "+5.2", delta_color="inverse")
with col2 : 
    st.metric(label = "EUR/KRW", value = "1,503.2", delta= "-3.1", delta_color="inverse")
with col3 : 
    st.metric(label = "JPY(100엔)/KRW", value = 930.8, delta= "-2.2", delta_color="inverse")

st.markdown('---')
st.header('3)보너스: 무역 원본 데이터 미리보기')
st.write('금융 데이터 파일 raw_trade_data.csv 상위 5행입니다.')
st.dataframe(df_trade.head(5), use_container_width= True)
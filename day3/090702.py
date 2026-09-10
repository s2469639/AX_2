# 데이터셋 분석 실습

import pandas as pd
import streamlit as st
import os
import io

st.title('시리얼 성분 데이터셋 기초 탐색')
st.caption('pandas에 head/tail/shape/info/columns 를 사용하여 데이터셋의 기본 정보를 확인합니다.')

df_cereal = pd.read_csv('cereal.csv')
st.subheader('1) head 5행')
st.dataframe(df_cereal.head(5), use_container_width = False)
st.subheader('2) tail 5행')
st.write(df_cereal.tail(5))
st.subheader('3) shape')
col1, col2 = st.columns(2)
with col1: 
    st.metric("행 개수", f'{df_cereal.shape[0]}개')
with col2: 
    st.metric("행 개수", f'{df_cereal.shape[1]}개')
st.subheader('4) columns')
st.write(list(df_cereal.columns))
st.subheader('5) info(): 각 열의 자료형과 결측치(NaN)여부 요약')

info_df = pd.DataFrame({
    "타입": df_cereal.dtypes.astype(str), 
    "결측치 아닌 개수": df_cereal.notna().sum(),
    "결측치 개수": df_cereal.isna().sum()
})
# 화면에 출력하는 코드를 추가합니다.
st.dataframe(info_df, use_container_width=True)
# 또는 st.write(info_df)
st.markdown('---')


st.subheader('6) 100 이상 칼로리')
over_100 = df_cereal[df_cereal["calories"] >= 100]
st.write(f'칼로리 100 이상 시리얼 수: **{len(over_100)}개**')
st.dataframe(over_100[['name','calories']].head(5), use_container_width = False)

st.subheader('7) 결측치 처리')
missing_protein = df_cereal["protein"].isna().sum()
st.write(f'Protein 열의 결측치 개수: **{missing_protein}개**')
df_clean = df_cereal.dropna(subset=["protein"])
col1, col2 = st.columns(2)
with col1:
    st.metric('제거 전', f'{len(df_cereal)}행')
with col2:
    st.metric('제거 후', f'{len(df_clean)}행')

output_path = "cereal_cleaned.csv"
df_clean.to_csv(output_path, index = False)
st.success("파일을 저장했습니다.")
st.dataframe(df_clean.head(5), use_container_width = True)
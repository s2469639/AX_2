# 인코딩 자동 감지 + 한글 폰트 막대그래프 
# 열 인코딩("utf-8-sig", "cp949", "euc-kr") 순서대로 시도 
# 내가 쓸 폰트 같은 경로에 있어야 함
# 막대그래프 생성 후 그림으로 저장 .png
# 실행 streamlit run 090704.py

import os 
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

st.title('인코딩 자동 감지 + 한글 막대 그래프(Titanic 연습)')
csv_path = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
font_path = os.path.join(os.path.dirname(__file__), "온글잎 윤탱체.ttf") 

def read_csv_with_auto_encoding(file_path_or_buffer):
    encodings = ["utf-8", "cp949", "euc-kr", "utf-8-sig"]

    for enc in encodings:
        try:
            if hasattr(file_path_or_buffer, "seek"):
                file_path_or_buffer.seek(0)
            df = pd.read_csv(file_path_or_buffer, encoding=enc)
            # df와 함께 성공한 인코딩 이름을 같이 반환
            return df, enc
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(f"지원하는 인코딩({encodings})으로 파일을 읽을 수 없습니다.")


# 2. 실제 사용 부분 (df와 used_encoding 두 개로 받아옴)
upload_file = st.file_uploader(
    "titanic_cleaned.csv 파일을 업로드하세요", type="csv"
)

if upload_file is not None:
    df, used_encoding = read_csv_with_auto_encoding(upload_file)
    st.info(f"업로드된 파일을 **{used_encoding}** 인코딩으로 읽었습니다.")
else:
    try:
        df, used_encoding = read_csv_with_auto_encoding(csv_path)
        st.info(f"로컬 파일을 **{used_encoding}** 인코딩으로 읽었습니다.")
    except FileNotFoundError:
        st.error("파일을 찾을 수 없습니다.")
        st.stop()

st.subheader('1) 인코딩 자동 감지')
# 3. 데이터 표시
st.dataframe(df.head())

# 인코딩 자동 감지로 csv읽기

st.markdown('---')

st.subheader('2) 객실별 생존율')
# 객실 등급(Pclass)별 생존율 집계
# 사망0/생존1 등급별 평균 Survived
# 생존 등급별 평균을 내면 그대로가 등급의 생존 비율이다. 
# 10명 남 3 여자 7 

pclass_survival_rate = df.groupby('Pclass')['Survived'].mean().sort_index()
st.dataframe((pclass_survival_rate*100).round(1).rename("생존율(%)"))

# 차트 그리기
st.markdown('---')
st.subheader('3) 객실 등급별 생존율 막대 그래프')
try: 
    font_prop = font_manager.FontProperties(fname= font_path)
    # matplotlib font_manager의 폰트를 등록하고, 전역 폰트로 설정
    font_manager.fontManager.addfont(font_path)

    plt.rcParams['font.family'] = font_prop.get_name()
    plt.rcParams['axes.unicode_minus'] = False
    st.write("폰트를 적용했습니다.")
except FileNotFoundError: 
    st.warning('폰트 파일을 찾을 수 없습니다.') # 폰트 파일이 없으면

fig, ax = plt.subplots(figsize = (8,5))
(pclass_survival_rate*100).plot(kind = "bar", color = "#e137ff", ax = ax)
ax.set_title("객실 등급별 생존율")
ax.set_xlabel("객실등급(Pclass)")
ax.set_ylabel("생존율(%)")

st.pyplot(fig)

output_png = output_path = os.path.join(os.path.dirname(__file__), "chart.png")
fig.savefig(output_png)
st.success('저장 완료!')
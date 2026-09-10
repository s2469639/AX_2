import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()
API_KEY = os.getenv("EXCHANGE_API_KEY")

# 페이지 기본 설정
st.set_page_config(page_title="실시간 환율 조회기", page_icon="💱", layout="centered")

# API 데이터 캐싱 (반복 요청 방지, 1시간 유효)
@st.cache_data(ttl=3600)
def fetch_rates(base_currency: str):
    if not API_KEY:
        return None, "API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("result") == "success":
            return data, None
        return None, data.get("error-type", "데이터를 가져오는 중 오류가 발생했습니다.")
    except Exception as e:
        return None, str(e)

# UI 헤더
st.title("💱 실시간 환율 계산기")
st.caption("ExchangeRate-API 데이터를 활용한 실시간 통화 변환 대시보드")
st.divider()

# 통화 목록 정의
CURRENCIES = ["USD", "KRW", "EUR", "JPY", "CNY", "GBP", "CAD", "AUD"]

# 레이아웃: 입력 섹션
col1, col2 = st.columns(2)

with col1:
    base_curr = st.selectbox("기준 통화 (보내는 돈)", CURRENCIES, index=0)
    amount = st.number_input("금액 입력", min_value=0.0, value=1.0, step=1.0)

with col2:
    target_curr = st.selectbox("대상 통화 (받는 돈)", CURRENCIES, index=1)

# 데이터 호출 및 결과 표시
if API_KEY is None:
    st.error("⚠️ `.env` 파일에 `EXCHANGE_API_KEY`가 정의되어 있지 않습니다.")
else:
    data, error = fetch_rates(base_curr)

    if error:
        st.error(f"❌ 오류 발생: {error}")
    elif data:
        rates = data.get("conversion_rates", {})
        target_rate = rates.get(target_curr)

        if target_rate:
            converted_amount = amount * target_rate
            
            # 메인 변환 결과 카드
            st.metric(
                label=f"{amount:,.2f} {base_curr} ➡️ {target_curr}",
                value=f"{converted_amount:,.2f} {target_curr}",
                delta=f"1 {base_curr} = {target_rate:,.4f} {target_curr}"
            )
            
            st.caption(f"기준 업데이트: {data.get('time_last_update_utc', 'N/A')[:16]} UTC")
        
        st.divider()

        # 주요 국가 환율 카드 그리드
        st.subheader(f"📌 1 {base_curr} 기준 주요 통화 환율")
        grid_cols = st.columns(3)
        display_targets = [c for c in ["KRW", "USD", "EUR", "JPY", "CNY", "GBP"] if c != base_curr][:3]

        for idx, code in enumerate(display_targets):
            rate = rates.get(code)
            with grid_cols[idx]:
                if rate:
                    st.metric(label=code, value=f"{rate:,.2f}")
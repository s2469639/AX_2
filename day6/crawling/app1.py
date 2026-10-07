import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

st.set_page_config(page_title="삼성전자 실시간 대시보드", layout="wide")

st.title("📈 삼성전자(005930) 자동 갱신 대시보드")
st.caption("네이버 증권에서 최신 데이터를 실시간으로 직접 수집합니다.")

# 1시간(3600초) 동안 데이터를 메모리에 캐싱 (불필요한 과도한 크롤링 방지)
@st.cache_data(ttl=3600)
def fetch_stock_data(stock_code="005930", target_pages=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    data_list = []
    
    for page in range(1, target_pages + 1):
        url = f"https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            continue
            
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table.type2 tr")
        
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 7 and cols[0].text.strip():
                date = cols[0].text.strip()
                close = int(cols[1].text.strip().replace(",", ""))
                diff_text = cols[2].text.strip().replace(",", "").replace("\n", "").replace("\t", "")
                is_down = "nv" in cols[2].get("class", []) or "하락" in cols[2].text
                diff_num = int(diff_text) if diff_text.isdigit() else 0
                diff = -diff_num if is_down else diff_num
                
                open_price = int(cols[3].text.strip().replace(",", ""))
                high = int(cols[4].text.strip().replace(",", ""))
                low = int(cols[5].text.strip().replace(",", ""))
                volume = int(cols[6].text.strip().replace(",", ""))
                
                data_list.append({
                    "날짜": date,
                    "종가": close,
                    "전일비": diff,
                    "시가": open_price,
                    "고가": high,
                    "저가": low,
                    "거래량": volume
                })
        time.sleep(0.3)
        
    df = pd.DataFrame(data_list)
    df["날짜"] = pd.to_datetime(df["날짜"])
    df = df.sort_values("날짜").reset_index(drop=True)
    df["MA5"] = df["종가"].rolling(window=5).mean()
    df["MA20"] = df["종가"].rolling(window=20).mean()
    return df

# 데이터 수집 실행
with st.spinner("네이버 증권에서 최신 주가를 가져오는 중..."):
    df = fetch_stock_data()

# 1. 상단 핵심 지표
latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) > 1 else latest
diff = int(latest["종가"] - prev["종가"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("최근 종가", f"{int(latest['종가']):,}원", f"{diff:+,}원")
col2.metric("최근 거래량", f"{int(latest['거래량']):,}주")
col3.metric("최고가", f"{int(df['고가'].max()):,}원")
col4.metric("최저가", f"{int(df['저가'].min()):,}원")

st.markdown("---")

# 2. 인터랙티브 주가 차트
st.subheader("주가 추이 (종가 및 5일/20일 이평선)")
chart_df = df.set_index("날짜")[["종가", "MA5", "MA20"]]
st.line_chart(chart_df)

# 3. 거래량 차트
st.subheader("거래량 추이")
st.bar_chart(df.set_index("날짜")[["거래량"]])

st.markdown("---")

# 4. 표 & 엑셀 내보내기 버튼 (필요할 때만 즉석 다운로드)
st.subheader("상세 시세 내역")
display_df = df.sort_values("날짜", ascending=False).copy()
display_df["날짜"] = display_df["날짜"].dt.strftime("%Y-%m-%d")
st.dataframe(display_df, use_container_width=True)

# 브라우저에서 바로 다운로드할 수 있는 CSV 버튼
csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 최신 시세 CSV 파일 다운로드",
    data=csv_data,
    file_name="samsung_live_stock.csv",
    mime="text/csv",
)
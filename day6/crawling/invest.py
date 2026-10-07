import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. 크롤링 기본 설정
stock_code = "005930"  # 삼성전자 종목코드
target_pages = 5        # 수집할 페이지 수 (1페이지당 약 10영업일)
data_list = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"삼성전자({stock_code}) 일별 시세 수집을 시작합니다... (총 {target_pages}페이지)")

# 2. 페이지 반복 크롤링
for page in range(1, target_pages + 1):
    url = f"https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"[{page}페이지] 요청 실패 (상태 코드: {response.status_code})")
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table.type2 tr")
    
    for row in rows:
        cols = row.find_all("td")
        # 실제 데이터가 들어있는 7개 열 필터링
        if len(cols) >= 7 and cols[0].text.strip():
            date = cols[0].text.strip()
            # 쉼표(,) 제거 후 숫자로 변환 (엑셀에서 계산 가능하도록 처리)
            close = int(cols[1].text.strip().replace(",", ""))
            
            # 전일비 처리 (상승/하락 기호 반영)
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
            
    print(f"-> {page}페이지 수집 완료")
    # 서버 부하 방지를 위해 0.5초 대기
    time.sleep(0.5)

# 3. 판다스 데이터프레임 변환 및 엑셀 저장
df = pd.DataFrame(data_list)

file_name = "samsung_stock_daily.xlsx"
df.to_excel(file_name, index=False, sheet_name="삼성전자_일별시세")

print("-" * 50)
print(f"수집 완료! 총 {len(df)}건의 시세 데이터가 '{file_name}' 파일로 저장되었습니다.")
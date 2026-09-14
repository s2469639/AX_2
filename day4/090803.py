# raw_trade_data.csv 파일 활용
# hscode가 85로 시작하는 (반도체류) + 국가명 미국 또는 베트남 + 수출금액 0보다 큰 수(실제 수출실적이 있는)
# 다중 조건으로 필터링한 뒤, 수출금액 상위 10건을 화면에 보여주고 report1.csv로 저장
# streamlit 사용 streamlit run 090803.py
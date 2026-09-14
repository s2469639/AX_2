from bs4 import BeautifulSoup
import requests

url = "https://startcoding.pythonanywhere.com/basic"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

# 검색 결과의 설명 텍스트
for result in soup.select(".VwiC3b"):
    print(result.text)
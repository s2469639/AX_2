from bs4 import BeautifulSoup
import requests

url = "https://startcoding.pythonanywhere.com/basic"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

soup = BeautifulSoup(response.text, "html.parser")

# 전체 상품 목록 선택
products = soup.select(".product")

for product in products:
    # 1. 라벨 (라벨이 없는 상품도 있으므로 예외 처리)
    label_tag = product.select_one(".product-label")
    label = label_tag.text.strip() if label_tag else "없음"

    # 2. 카테고리
    category_tag = product.select_one(".product-category")
    category = category_tag.text.strip() if category_tag else ""

    # 3. 상품명
    name_tag = product.select_one(".product-name")
    name = name_tag.text.strip() if name_tag else ""

    # 4. 가격
    price_tag = product.select_one(".product-price")
    price = price_tag.text.strip().split("\n")[0] if price_tag else ""

    print(f"[{label}] {category} | {name} | {price}")
										
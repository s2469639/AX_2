from bs4 import BeautifulSoup
import requests
import pandas as pd
import openpyxl

# 데이터가 저장될 빈 공간이 필요함
# 큰 for문은 각각 데이터를 나눠서 저장하기 위해 필요한 것. 
data = []
for i in range(1,5):
    url = f"https://startcoding.pythonanywhere.com/basic?page={i}"
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    # 전체 상품 목록 선택 <div class="product">
    products = soup.select('.product') 

   # print(f'가져온 아이템은 {len(products)}개\n'+"-"*30)
    for product in products: 
        category = product.select_one('.product-category').text # 카테고리
        name = product.select_one('.product-name').text # 상품명
        price = product.select_one('.product-price').text.split('원')[0].replace(',','')  # 가격
        link = product.select_one('.product-name>a')['href'] # 상품 상세 페이지 링크
        print(f'{category}|{name}|{price}|{link}')
        data.append([category,name,price,link])

df=pd.DataFrame(data, columns = ["카테고리", "상품명", "가격", "링크"])
df.to_excel("data.xlsx", index = False)
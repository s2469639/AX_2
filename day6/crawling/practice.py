from playwright.sync_api import sync_playwright

def scrape_dynamic_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = "http://quotes.toscrape.com/js/"
        page.goto(url)

        # 1. 명언 카드 덩어리가 로딩될 때까지 대기
        page.wait_for_selector(".quote")

        # 2. 모든 명언 카드들(.quote)을 가져옴
        quotes = page.query_selector_all(".quote")
        print(f"총 {len(quotes)}개의 명언을 찾았습니다.\n")

        for q in quotes:
            # 기존 항목: 텍스트 및 작가 이름
            text = q.query_selector(".text").inner_text()
            author = q.query_selector(".author").inner_text()

            # [추가 1] 작가 소개 페이지 링크 추출 (get_attribute 사용)
            # a 태그 중 author 링크가 들어있는 태그 선택
            author_link_tag = q.query_selector("a[href*='/author/']")
            author_url = author_link_tag.get_attribute("href") if author_link_tag else "링크 없음"

            # [추가 2] 여러 개의 태그 키워드(.tag) 리스트로 뽑기
            tag_elements = q.query_selector_all(".tag")
            tags = [t.inner_text() for t in tag_elements]

            # 결과 출력
            print(f"인물: {author}")
            print(f"명언: {text}")
            print(f"태그: {', '.join(tags)}")
            print("-" * 50)

        browser.close()

if __name__ == "__main__":
    scrape_dynamic_page()
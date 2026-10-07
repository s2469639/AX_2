"""
KOTRA 지원사업 공고 전체 페이지 크롤러
대상: https://www.kotra.or.kr/subList/20000020753

사이트는 목록을 AJAX(.do) 엔드포인트로 페이지 단위 렌더링한다. 엔드포인트가
JSON을 주는지 HTML 조각을 주는지 응답을 실제로 확인하기 전까지 알 수 없으므로,
두 형식을 모두 처리하고 페이지네이션은 "빈 결과가 나올 때까지" 반복한다.
"""
import json
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.kotra.or.kr"
LIST_PAGE_URL = f"{BASE_URL}/subList/20000020753"

# 사이트 개편으로 엔드포인트가 바뀔 수 있어 후보를 순서대로 시도한다.
# selectBmBizAllListAjax.do: 신청마감 포함 전체 공고 / selectBmBizRcritYListNewAjax.do: 신청가능 공고만
CANDIDATE_ENDPOINTS = [
    "/module/subhome/bizAply/selectBmBizAllListAjax.do",
    "/module/subhome/bizAply/selectBmBizRcritYListNewAjax.do",
]

PAGE_SIZE = 10
MAX_EMPTY_PAGES_TO_STOP = 1  # 결과 없는 페이지 나오면 즉시 종료
REQUEST_DELAY_SEC = 1.0
TIMEOUT = 15

FIELD_PATTERNS = {
    "신청기간": r"신청기간\s*[:：]?\s*([0-9.\-~ ]+)",
    "개최기간": r"개최기간\s*[:：]?\s*([0-9.\-~ ]+)",
    "주관부서": r"주관부서\s*[:：]?\s*([^\n]+)",
    "전화번호": r"(?:전화번호|사업문의\s*전화번호)\s*[:：]?\s*([+0-9\- /]+)",
    "이메일": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
}


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": LIST_PAGE_URL,
            "Origin": BASE_URL,
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
    )
    # 목록 페이지를 먼저 방문해 세션/쿠키를 확보한다.
    session.get(LIST_PAGE_URL, timeout=TIMEOUT)
    return session


def _extract_detail_url(href: str) -> str:
    # 실제 이동 주소는 javascript:fn_selectBizMntInfoDetailNew('URL') 형태로
    # 감싸져 있는 경우가 많으므로 그 안의 URL을 우선 추출한다.
    js_match = re.search(r"fn_selectBizMntInfoDetailNew\('([^']+)'\)", href)
    if js_match:
        return js_match.group(1)
    if href.startswith("http"):
        return href
    if not href.startswith("javascript:"):
        return BASE_URL + href
    return ""


def parse_card_html(anchor, container) -> dict:
    title = anchor.get_text(strip=True) or "정보 없음"
    detail_url = _extract_detail_url(anchor["href"])

    card_text = container.get_text(separator="\n")
    item = {"사업명": title, "상세링크": detail_url}
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, card_text)
        item[field] = match.group(1).strip() if match and match.groups() else (
            match.group(0).strip() if match else "정보 없음"
        )
    return item


def _find_item_anchors(soup: BeautifulSoup):
    """
    클래스명(card 등)에 의존하지 않고, 실제 상세보기 링크
    (javascript:fn_selectBizMntInfoDetailNew(...))를 가진 앵커를 직접 찾는다.
    각 앵커에 대해 "신청기간" 텍스트를 포함하는 가장 작은 조상을 정보 추출용
    컨테이너로 함께 반환한다. 클래스명이 바뀌어도 이 구조만 유지되면 동작한다.
    (anchor, container) 튜플의 리스트를 반환.
    """
    anchors = [
        a for a in soup.find_all("a", href=True)
        if "fn_selectBizMntInfoDetailNew" in a["href"]
    ]

    results = []
    for anchor in anchors:
        container = anchor
        for ancestor in anchor.parents:
            if "신청기간" in ancestor.get_text():
                container = ancestor
                break
        results.append((anchor, container))
    return results


def parse_html_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    pairs = _find_item_anchors(soup)

    if not pairs:
        # 폴백: 링크 패턴이 없으면 기존 방식(class="card")으로 시도
        cards = soup.find_all("div", class_=re.compile(r"\bcard\b"))
        if not cards:
            cards = soup.select(".card-list > li") or soup.find_all("div", class_="item")
        pairs = []
        for card in cards:
            link = card.find("a", href=True)
            if link:
                pairs.append((link, card))

    items = [parse_card_html(anchor, container) for anchor, container in pairs]

    # 제목+상세링크 기준 중복 제거 (동일 카드가 다른 셀렉터로 이중 매칭되는 경우 방지)
    seen = set()
    deduped = []
    for item in items:
        key = (item.get("사업명"), item.get("상세링크"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def parse_json_page(data) -> list[dict] | None:
    """일반적인 KOTRA 응답 형태(resultList/list/data 등)를 추정해서 파싱."""
    if isinstance(data, dict):
        for key in ("resultList", "list", "data", "items", "rows"):
            if key in data and isinstance(data[key], list):
                rows = data[key]
                break
        else:
            return None
    elif isinstance(data, list):
        rows = data
    else:
        return None

    items = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        items.append(
            {
                "사업명": row.get("bizNm") or row.get("title") or row.get("subhomeNm") or "정보 없음",
                "신청기간": _join_period(row, "aplyBgnDt", "aplyEndDt")
                or row.get("aplyDdlnDt", "정보 없음"),
                "개최기간": _join_period(row, "holdBgnDt", "holdEndDt", "eventBgnDt", "eventEndDt"),
                "주관부서": row.get("chrgDeptNm") or row.get("deptNm", "정보 없음"),
                "전화번호": row.get("telNo") or row.get("chrgTelNo", "정보 없음"),
                "이메일": row.get("emailAddr") or row.get("chrgEmailAddr", "정보 없음"),
                "상세링크": row.get("dtlUrl", ""),
                "_raw": row,
            }
        )
    return items


def _join_period(row: dict, *keys) -> str:
    vals = [row.get(k) for k in keys if row.get(k)]
    return " ~ ".join(vals) if vals else ""


def fetch_page(session: requests.Session, endpoint: str, page: int) -> tuple[list[dict], bool]:
    """(items, is_json) 반환."""
    # 브라우저 개발자도구에서 확인한 실제 요청 파라미터 (Form Data)
    payload = {
        "pageNo": page,
        "pageNo2": page,
        "pageNoA": page,
        "pageSize": PAGE_SIZE,
        "listCount": PAGE_SIZE,
        "query": "",
        "collection": "business_application",
        "sch_biz_name": "",
        "schwrdVal": "",
        "sch_event_start_dt": "",
        "sch_event_end_dt": "",
        "sch_appl_yn": "N",
        "sch_nation_cd": "Y",
    }
    resp = session.post(BASE_URL + endpoint, data=payload, timeout=TIMEOUT)
    resp.raise_for_status()

    if page == 1:
        debug_path = f"debug_{endpoint.rsplit('/', 1)[-1]}_page1.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(resp.text)

    try:
        data = resp.json()
        items = parse_json_page(data)
        if items is not None:
            return items, True
    except json.JSONDecodeError:
        pass

    return parse_html_page(resp.text), False


def crawl_all_pages() -> pd.DataFrame:
    session = build_session()
    all_items: list[dict] = []

    for endpoint in CANDIDATE_ENDPOINTS:
        print(f"[엔드포인트 시도] {endpoint}")
        page = 1
        empty_streak = 0
        endpoint_items: list[dict] = []
        prev_signature = None

        while True:
            try:
                items, is_json = fetch_page(session, endpoint, page)
            except Exception as e:
                print(f"  -> {page}페이지 요청 실패: {e}")
                break

            if not items:
                empty_streak += 1
                print(f"  -> {page}페이지 결과 없음")
                if empty_streak >= MAX_EMPTY_PAGES_TO_STOP:
                    break
            else:
                signature = tuple(item.get("사업명") for item in items)
                if signature == prev_signature:
                    # pageIndex를 무시하고 매 요청마다 전체 목록을 그대로
                    # 돌려주는 엔드포인트인 경우: 이미 첫 페이지에서 전체를
                    # 받은 것이므로 더 이상 반복할 필요가 없다.
                    print(f"  -> {page}페이지가 이전 페이지와 동일함 (페이지네이션 미지원으로 판단), 수집 종료")
                    break
                prev_signature = signature

                empty_streak = 0
                print(f"  -> {page}페이지 {len(items)}건 수집 (json={is_json})")
                endpoint_items.extend(items)

                # 이번 페이지에서 요청한 개수보다 적게 왔다면 마지막 페이지.
                if len(items) < PAGE_SIZE:
                    print("  -> 요청 개수보다 적게 반환됨, 마지막 페이지로 판단")
                    break

            page += 1
            time.sleep(REQUEST_DELAY_SEC)

            if page > 200:  # 안전장치: 무한루프 방지
                print("  -> 200페이지 초과, 안전을 위해 중단")
                break

        if endpoint_items:
            all_items = endpoint_items
            print(f"[성공] {endpoint} 에서 총 {len(all_items)}건 수집, 다른 후보는 시도하지 않음")
            break
        else:
            print(f"[실패] {endpoint} 에서 데이터를 찾지 못함, 다음 후보 시도")

    df = pd.DataFrame(all_items)
    if "_raw" in df.columns:
        df = df.drop(columns=["_raw"])
    return df


def main():
    df = crawl_all_pages()
    print(f"\n총 {len(df)}건 수집 완료!")
    if df.empty:
        print("수집된 데이터가 없습니다. 엔드포인트/파라미터를 재확인하세요.")
        return

    print(df.head())
    df.to_csv("kotra_biz_list.csv", index=False, encoding="utf-8-sig")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"kotra_biz_list_{timestamp}.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()

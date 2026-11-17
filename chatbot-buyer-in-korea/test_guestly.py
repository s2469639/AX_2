"""GUESTLY 6단계 점검 스크립트 (API를 호출하지 않는다).

생성 모델과 임베딩을 가짜로 바꿔 기획서의 테스트 항목을 확인한다.
실행: python test_guestly.py
"""

import tempfile
from pathlib import Path

from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

import config
import graph
import ingest
import llm
import md_loader
import rag
import usage

DOCS = md_loader.load_all()
STORE = InMemoryVectorStore(DeterministicFakeEmbedding(size=8))
STORE.add_documents(DOCS, ids=[d.id for d in DOCS])
CALLS: list[str] = []          # 생성 모델 호출 기록 (analyze, rewrite, generate)
FAKE = {"score": 0.5, "conditions": {}, "no_match": []}


def fake_search(query, doc_type, region=None, budget=None, k=config.TOP_K):
    """임베딩 없이 필터만 적용하고, 점수는 시험용 값으로 돌려준다."""
    found = STORE.similarity_search_with_score(
        query, k=k, filter=rag.make_filter(doc_type, region, budget))
    return [(doc, FAKE["score"]) for doc, _ in found]


def fake_structured(messages, schema, max_tokens, purpose):
    """질문 분석과 답변 생성을 흉내 낸다 (호출 횟수만 기록)."""
    CALLS.append(purpose)
    if purpose == "generate":
        names = [graph.item_names(DOCS[0])[0]]
        return schema(answer=f"1. {names[0]} — 가짜 답변", no_match_types=list(FAKE["no_match"]))
    return schema(**FAKE["conditions"])


def fake_text(messages, max_tokens, purpose):
    """검색 문장 재작성을 흉내 낸다."""
    CALLS.append(purpose)
    return "다시 쓴 검색 문장"


def run_case(conditions: dict, score: float = 0.5, prev=None, no_match=()):
    """가짜 조건과 점수로 그래프를 한 번 실행한다."""
    CALLS.clear()
    FAKE.update(score=score, conditions=conditions, no_match=list(no_match))
    graph._app = None
    return graph.run("시험 질문", prev_conditions=prev)


BASE = dict(intent="restaurant", is_followup=False, region="강남",
            restaurant_budget=70000, restaurant_query="조용한 저녁")


def test_1_restaurant():
    """식당 추천: 답변·출처가 나오고 모델 호출은 analyze, generate 2회."""
    state = run_case(BASE)
    assert CALLS == ["analyze", "generate"], CALLS
    assert state["sources"] and "restaurants.md" in state["sources"][0]


def test_2_gift():
    """선물 추천: 선물 문서만 검색한다."""
    state = run_case(dict(intent="gift", is_followup=False, gift_budget=50000))
    assert all(d.metadata["doc_type"] == "gift" for d, _ in state["results"]["gift"])


def test_3_both():
    """통합 추천: 식당·선물을 각각 검색해 한 번에 답한다."""
    state = run_case(dict(intent="both", is_followup=False, region="강남",
                          restaurant_budget=70000, gift_budget=50000))
    assert set(state["results"]) == {"restaurant", "gift"}
    assert CALLS.count("generate") == 1


def test_4_budget_excluded():
    """예산 초과 제외: 최저 가격이 예산보다 높은 후보는 검색 결과에 없다."""
    state = run_case(BASE)
    assert all(d.metadata["price_min"] <= 70000 for d, _ in state["results"]["restaurant"])
    allowed = [d.id for d in DOCS if rag.make_filter("restaurant", "강남", 70000)(d)]
    assert "R-003" not in allowed and "R-021" not in allowed


def test_5_followup_keeps_conditions():
    """후속 질문: 새로 말한 예산만 바뀌고 지역·검색 문장은 유지된다."""
    state = run_case(dict(intent="restaurant", is_followup=True, restaurant_budget=49000), prev=BASE)
    c = state["conditions"]
    assert (c["region"], c["restaurant_budget"], c["restaurant_query"]) == ("강남", 49000, "조용한 저녁")


def test_6_not_found_without_generate():
    """근거 부족: 고정 문구를 돌려주고 답변 생성 모델은 부르지 않는다."""
    state = run_case({**BASE, "region": "부산"})           # 필터 후 후보 0개
    assert state["answer"] == config.NOT_FOUND_MESSAGE and "generate" not in CALLS
    state = run_case(BASE, score=0.1)                       # 점수 미달
    assert state["answer"] == config.NOT_FOUND_MESSAGE and "generate" not in CALLS
    state = run_case(dict(intent="unsupported", is_followup=False))
    assert CALLS == ["analyze"] and "식당 추천" in state["answer"]


def test_7_retry_once():
    """재검색 제한: 점수가 계속 낮아도 재작성·재검색은 1회뿐이다."""
    state = run_case(BASE, score=0.1)
    assert CALLS.count("rewrite") == 1 and state["retry_count"] == 1


def test_7b_no_match():
    """맞는 후보 없음 판정: 해당 유형은 고정 문구로 바뀐다."""
    state = run_case(dict(intent="gift", is_followup=False), no_match=["gift"])
    assert state["answer"] == config.NOT_FOUND_MESSAGE and state["sources"] == []


def test_8_no_duplicate_embedding():
    """임베딩 중복 방지: 바뀐 것이 없으면 다시 임베딩하지 않는다."""
    store = InMemoryVectorStore(DeterministicFakeEmbedding(size=8))
    first = ingest.apply_changes(store, ingest.compare(md_loader.load_all(), store))
    second = ingest.apply_changes(store, ingest.compare(md_loader.load_all(), store))
    assert first == len(DOCS) and second == 0


def test_9_budget_blocks_before_call():
    """비용 제한: 한도를 넘으면 모델을 만들기 전에 막고 안내 문구를 준다."""
    original = (config.DAILY_BUDGET_USD, config.USAGE_LOG_PATH, llm.get_model)
    config.USAGE_LOG_PATH = Path(tempfile.mkdtemp()) / "usage.jsonl"
    config.DAILY_BUDGET_USD = 0.0
    called = []
    llm.get_model = lambda *a: called.append(1)  # 불리면 실패로 본다
    try:
        try:
            ORIGINAL_ASK_TEXT([("user", "안녕")], 100, "test")
            raise AssertionError("예산을 넘었는데 막지 않았어요")
        except usage.BudgetError as error:
            assert "예산" in str(error) and not called
    finally:
        config.DAILY_BUDGET_USD, config.USAGE_LOG_PATH, llm.get_model = original


def test_line_numbers():
    """출처 줄 번호가 원본 Markdown의 소제목 줄과 일치한다."""
    for doc in DOCS:
        path = config.DATA_DIR / doc.metadata["source"]
        lines = path.read_text(encoding="utf-8").splitlines()
        assert lines[doc.metadata["line_start"] - 1].startswith(f"## {doc.id} ")


ORIGINAL_ASK_TEXT = llm.ask_text


def main() -> None:
    """모든 점검을 실행하고 결과를 한 줄씩 보여 준다."""
    rag.search = fake_search
    llm.ask_structured, llm.ask_text = fake_structured, fake_text
    tests = [(name, fn) for name, fn in globals().items() if name.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"✅ {name} — {fn.__doc__.splitlines()[0]}")
        except Exception as error:  # 실패 원인을 보여 주고 다음 점검으로 넘어간다
            failed += 1
            print(f"❌ {name} — {type(error).__name__}: {error}")
    print(f"\n{len(tests) - failed}/{len(tests)}개 통과")


if __name__ == "__main__":
    main()

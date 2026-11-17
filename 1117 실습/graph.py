"""GUESTLY 추천 흐름을 LangGraph로 구성한다.

START → analyze → retrieve → check → (generate | rewrite → retrieve | not_found) → END
지원하지 않는 요청은 analyze 다음 바로 unsupported로 간다.
"""

import json
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

import config
import llm
import rag

TYPE_NAMES = {"restaurant": "식당", "gift": "선물"}

UNSUPPORTED_MESSAGE = (
    "GUESTLY는 한국을 방문한 해외 바이어를 위한 **식당 추천**과 **선물 추천**만 도와드려요.\n\n"
    "예: \"강남에서 1인 7만 원 정도의 조용한 저녁 식당 추천해 줘\", "
    "\"5만 원 이하로 가져가기 편한 한국적인 선물 알려 줘\""
)


class Conditions(BaseModel):
    """질문에서 뽑아낸 추천 조건."""
    intent: Literal["restaurant", "gift", "both", "unsupported"] = Field(
        description="식당 추천=restaurant, 선물 추천=gift, 둘 다=both, 식당·선물과 무관한 요청=unsupported")
    is_followup: bool = Field(description="이전 추천 조건을 일부만 바꾸는 후속 요청이면 true")
    region: str | None = Field(default=None, description=(
        f"식당 지역. 다음 중 해당하면 그 이름으로: {', '.join(config.REGIONS)}. "
        "목록에 없는 지역이면 사용자가 말한 지역명 그대로. 언급이 없으면 null"))
    people: int | None = Field(default=None, description="식사 인원 (바이어와 우리 측 포함, 언급 없으면 null)")
    restaurant_budget: int | None = Field(default=None, description="식당 1인당 예산(원)")
    gift_budget: int | None = Field(default=None, description="선물 1개당 예산(원)")
    dietary: str | None = Field(default=None, description="식이 제한·음주 여부·알레르기")
    preferences: str | None = Field(default=None, description="분위기, 취향, 방문 목적 등 그 밖의 조건")
    restaurant_query: str | None = Field(default=None, description="식당 문서 검색용 짧은 문장 (분위기·음식·상황 중심, 국적은 넣지 않음)")
    gift_query: str | None = Field(default=None, description="선물 문서 검색용 짧은 문장 (특징·상황·휴대성 중심, 국적은 넣지 않음)")


class GeneratedAnswer(BaseModel):
    """답변 생성 결과. 요청에 맞는 후보가 없는 유형은 따로 표시한다."""
    answer: str = Field(description="추천 답변 본문 (맞는 후보가 없는 유형은 쓰지 않음)")
    no_match_types: list[Literal["restaurant", "gift"]] = Field(
        default_factory=list,
        description="후보 중 요청의 핵심(원하는 품목·음식 종류)에 맞는 것이 하나도 없는 유형")


class GuestlyState(TypedDict, total=False):
    """그래프가 단계마다 주고받는 값."""
    question: str
    history: list[dict]            # 최근 대화 (최대 4개)
    prev_conditions: dict | None   # 직전 추천 조건 (후속 질문용)
    conditions: dict
    queries: dict                  # 유형별 검색 문장
    results: dict                  # 유형별 [(Document, 점수)]
    sufficient: dict               # 유형별 근거 충분 여부
    etiquette: list                # 참고 의전 지침
    retry_count: int
    no_match: list                 # 모델이 '맞는 후보 없음'으로 판단한 유형
    answer: str
    sources: list[str]


def target_types(intent: str) -> list[str]:
    """질문 유형에 따라 검색할 문서 유형 목록을 돌려준다."""
    return {"restaurant": ["restaurant"], "gift": ["gift"],
            "both": ["restaurant", "gift"]}.get(intent, [])


def merge_conditions(prev: dict | None, new: dict) -> dict:
    """후속 질문이면 새로 말하지 않은 조건은 이전 값을 유지한다."""
    if not prev or not new.get("is_followup"):
        return new
    merged = dict(prev)
    for key, value in new.items():
        if value is not None:
            merged[key] = value
    return merged


def analyze(state: GuestlyState) -> dict:
    """질문 유형을 나누고 추천 조건을 뽑는다 (생성 모델 1회)."""
    history = state.get("history", [])[-config.MAX_HISTORY_MESSAGES:]
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history) or "(없음)"
    prev = json.dumps(state.get("prev_conditions") or {}, ensure_ascii=False)
    messages = [
        ("system",
         "너는 해외 바이어 접대 추천 서비스의 질문 분석기다. 사용자 질문에서 조건을 뽑아라. "
         "금액은 원 단위 정수로 바꿔라 (예: 7만 원 → 70000). "
         "후속 요청에서 '더 저렴하게'처럼 숫자 없이 예산을 낮추라고 하면 이전 예산의 약 70%로 정하라. "
         "국적만 보고 취향을 짐작해 조건을 만들지 마라."),
        ("user", f"이전 대화:\n{history_text}\n\n이전 조건: {prev}\n\n현재 질문: {state['question']}"),
    ]
    parsed = llm.ask_structured(messages, Conditions, config.MAX_TOKENS_ANALYZE, "analyze")
    conditions = merge_conditions(state.get("prev_conditions"), parsed.model_dump())
    queries = {
        "restaurant": conditions.get("restaurant_query") or state["question"],
        "gift": conditions.get("gift_query") or state["question"],
    }
    return {"conditions": conditions, "queries": queries, "retry_count": 0,
            "results": {}, "sufficient": {}}


def route_intent(state: GuestlyState) -> str:
    """지원하는 요청이면 검색으로, 아니면 안내로 보낸다."""
    return "unsupported" if state["conditions"]["intent"] == "unsupported" else "retrieve"


def unsupported(state: GuestlyState) -> dict:
    """지원 범위를 안내한다 (모델 호출 없음)."""
    return {"answer": UNSUPPORTED_MESSAGE, "sources": []}


def retrieve(state: GuestlyState) -> dict:
    """근거가 아직 부족한 유형만 조건 필터 + 유사도로 검색한다."""
    conditions = state["conditions"]
    results = dict(state.get("results", {}))
    sufficient = state.get("sufficient", {})
    for doc_type in target_types(conditions["intent"]):
        if sufficient.get(doc_type):
            continue  # 이미 충분한 유형은 다시 검색하지 않는다
        budget = conditions.get("restaurant_budget" if doc_type == "restaurant" else "gift_budget")
        region = conditions.get("region") if doc_type == "restaurant" else None
        results[doc_type] = rag.search(state["queries"][doc_type], doc_type,
                                       region=region, budget=budget)
    return {"results": results}


def check(state: GuestlyState) -> dict:
    """유형별로 1위 점수가 기준 이상인지 확인한다 (모델 호출 없음)."""
    sufficient = {}
    for doc_type in target_types(state["conditions"]["intent"]):
        found = state["results"].get(doc_type, [])
        sufficient[doc_type] = bool(found) and found[0][1] >= config.SCORE_THRESHOLD
    return {"sufficient": sufficient}


def rewritable_types(state: GuestlyState) -> list[str]:
    """근거가 부족하지만 후보는 있는 유형 (필터 후 후보가 0개면 다시 써도 소용없다)."""
    return [t for t, ok in state["sufficient"].items()
            if not ok and state["results"].get(t)]


def route_check(state: GuestlyState) -> str:
    """근거 상태에 따라 답변 생성, 재검색, 고정 응답 중 하나로 보낸다."""
    flags = state["sufficient"].values()
    if all(flags):
        return "generate"
    if state.get("retry_count", 0) < config.MAX_RETRY_SEARCH and rewritable_types(state):
        return "rewrite"
    return "generate" if any(flags) else "not_found"


def rewrite(state: GuestlyState) -> dict:
    """근거가 부족한 유형의 검색 문장을 조건 중심으로 다시 쓴다 (유형마다 생성 모델 1회, 최대 1회)."""
    queries = dict(state["queries"])
    conditions = json.dumps(state["conditions"], ensure_ascii=False)
    for doc_type in rewritable_types(state):
        messages = [
            ("system",
             f"{TYPE_NAMES[doc_type]} 목록 문서를 검색할 짧은 한국어 문장 하나만 써라. "
             "문서 항목에는 음식 종류/카테고리, 분위기/특징, 식이 제한, 추천 상황, 휴대 편의성 같은 내용이 있다. "
             "국적, 인원수, 금액은 빼고 문장만 출력하라."),
            ("user", f"원래 질문: {state['question']}\n조건: {conditions}\n이전 검색 문장: {queries[doc_type]}"),
        ]
        queries[doc_type] = llm.ask_text(messages, config.MAX_TOKENS_REWRITE, "rewrite").strip()
    return {"queries": queries, "retry_count": state.get("retry_count", 0) + 1}


def not_found(state: GuestlyState) -> dict:
    """근거가 없을 때 고정 문구를 돌려준다 (모델 호출 없음)."""
    return {"answer": config.NOT_FOUND_MESSAGE, "sources": []}


def format_docs(results: list) -> str:
    """검색된 항목의 원문 전체를 모델에게 줄 근거 글로 만든다."""
    return "\n\n".join(doc.metadata.get("full_text", doc.page_content) for doc, _ in results)


def generate(state: GuestlyState) -> dict:
    """근거가 충분한 유형만 검색 문서를 바탕으로 추천 답변을 만든다 (생성 모델 1회)."""
    conditions = state["conditions"]
    ok_types = [t for t, ok in state["sufficient"].items() if ok]
    missing = [t for t, ok in state["sufficient"].items() if not ok]

    etiquette = rag.search(state["question"], "etiquette", k=1)
    etiquette = [r for r in etiquette if r[1] >= config.SCORE_THRESHOLD]

    context = "\n\n".join(
        f"[{TYPE_NAMES[t]} 후보]\n{format_docs(state['results'][t])}" for t in ok_types)
    if etiquette:
        context += f"\n\n[의전 참고]\n{format_docs(etiquette)}"

    messages = [
        ("system",
         "너는 해외 바이어 접대를 돕는 GUESTLY다. 아래 [후보] 문서에 있는 항목만 추천하라. 문서에 없는 식당·선물을 만들지 마라.\n"
         "형식: 유형별로 '**추천 식당**' 또는 '**추천 선물**' 제목 아래 번호 목록으로 2~3개. "
         "각 항목은 '이름 — 추천 이유 (가격대)' 한 줄과 필요하면 짧은 보충 한 줄. "
         "마지막에 '**주의사항**'으로 확인이 필요한 점을 2~4개 적어라.\n"
         "예산 초과 여부, 주소, 연락처는 쓰지 마라 (코드가 따로 붙인다). "
         "추천 이유에는 대표 메뉴나 (식이 제한이 있으면) 비건·채식 메뉴를 자연스럽게 언급하라. "
         "국적으로 취향을 단정하지 말고, 반입 규정·영업 정보처럼 최신 확인이 필요한 내용은 '확인 필요'로 써라. "
         "출처는 쓰지 마라 (따로 붙인다). 쉬운 한국어 존댓말로 간결하게.\n"
         "사용자가 원한 핵심 품목이나 음식 종류가 후보에 전혀 없으면(예: 골프 용품을 원했는데 후보가 차·김뿐) "
         "그 유형은 다른 것으로 대신 추천하지 말고 답변에서 빼고 no_match_types에 넣어라. "
         "조건이 일부만 맞는 정도라면 추천하고 맞지 않는 점을 주의사항에 적어라."),
        ("user", f"질문: {state['question']}\n조건: {json.dumps(conditions, ensure_ascii=False)}\n\n{context}"),
    ]
    result = llm.ask_structured(messages, GeneratedAnswer, config.MAX_TOKENS_GENERATE, "generate")

    # 모델이 '맞는 후보 없음'으로 판단한 유형은 근거 부족과 똑같이 처리한다
    no_match = [t for t in result.no_match_types if t in ok_types]
    ok_types = [t for t in ok_types if t not in no_match]
    missing += no_match
    if not ok_types:
        return {"answer": config.NOT_FOUND_MESSAGE, "sources": [], "no_match": no_match}

    answer = result.answer.strip()
    candidates = [r for t in ok_types for r in state["results"][t]]
    recommended = mentioned_in(answer, candidates)
    answer += restaurant_info(recommended)
    answer += budget_note(recommended, conditions)
    for doc_type in missing:
        answer += f"\n\n**{TYPE_NAMES[doc_type]}**: {config.NOT_FOUND_MESSAGE}"

    used = recommended + etiquette
    return {"answer": answer, "sources": rag.sources_of(used),
            "etiquette": etiquette, "no_match": no_match}


def field_value(doc, key: str) -> str | None:
    """원문에서 '- 키: 값' 줄의 값을 꺼낸다."""
    for line in doc.metadata.get("full_text", "").splitlines():
        if line.startswith(f"- {key}:"):
            return line.split(":", 1)[1].strip()
    return None


def restaurant_info(recommended: list) -> str:
    """추천한 식당의 주소·연락처·대표 메뉴·비건 메뉴를 데이터에서 그대로 꺼내 붙인다."""
    blocks = []
    for doc, _ in recommended:
        if doc.metadata["doc_type"] != "restaurant":
            continue
        block = [f"- **{item_names(doc)[0]}** · {field_value(doc, '주소')} · {field_value(doc, '연락처')}",
                 f"  - 대표 메뉴: {field_value(doc, '대표 메뉴')}"]
        vegan = field_value(doc, "비건·채식 메뉴")
        if vegan:
            block.append(f"  - 비건·채식 메뉴: {vegan}")
        blocks.append("\n".join(block))
    if not blocks:
        return ""
    return "\n\n**식당 정보** (가상 데이터)\n" + "\n".join(blocks)


def format_won(amount: int) -> str:
    """70000 → '7만 원', 45000 → '4만 5천 원'처럼 읽기 쉬운 금액으로 바꾼다."""
    man, rest = divmod(amount, 10000)
    if rest == 0:
        return f"{man}만 원"
    if man and rest % 1000 == 0:
        return f"{man}만 {rest // 1000}천 원"
    return f"{amount:,}원"


def budget_note(recommended: list, conditions: dict) -> str:
    """추천 항목 중 가격 최대값이 예산을 넘는 것을 코드로 비교해 안내 문구를 만든다."""
    lines = []
    for doc, _ in recommended:
        meta = doc.metadata
        key = "restaurant_budget" if meta["doc_type"] == "restaurant" else "gift_budget"
        budget = conditions.get(key)
        if budget and meta.get("price_max", 0) > budget:
            unit = "1인 " if meta["doc_type"] == "restaurant" else ""
            lines.append(f"- {item_names(doc)[0]}: {unit}{format_won(meta['price_min'])}~"
                         f"{format_won(meta['price_max'])}으로, 예산 {format_won(budget)}을 넘을 수 있어요.")
    if not lines:
        return ""
    return "\n\n**예산 확인**\n" + "\n".join(lines)


def item_names(doc) -> list[str]:
    """항목의 이름 후보를 꺼낸다: 소제목 이름('한빛정')과 상품명 필드 값."""
    names = [doc.metadata["heading"].split(" ", 1)[-1].split(" (")[0].strip()]
    for line in doc.metadata.get("full_text", "").splitlines():
        if line.startswith("- 상품명:"):
            names.append(line.split(":", 1)[1].strip())
    return names


def mentioned_in(answer: str, candidates: list) -> list:
    """답변에 이름이 실제로 나온 후보만, 답변에 나온 순서대로 남긴다 (하나도 못 찾으면 후보 전체)."""
    def position(result) -> int:
        """답변에서 그 항목 이름이 처음 나온 위치 (없으면 -1)."""
        found = [answer.find(n) for n in item_names(result[0]) if n in answer]
        return min(found) if found else -1
    used = sorted((r for r in candidates if position(r) >= 0), key=position)
    return used or candidates


def build_graph():
    """노드와 분기를 연결해 실행 가능한 그래프를 만든다."""
    graph = StateGraph(GuestlyState)
    for name, node in [("analyze", analyze), ("unsupported", unsupported),
                       ("retrieve", retrieve), ("check", check), ("rewrite", rewrite),
                       ("generate", generate), ("not_found", not_found)]:
        graph.add_node(name, node)
    graph.add_edge(START, "analyze")
    graph.add_conditional_edges("analyze", route_intent, ["unsupported", "retrieve"])
    graph.add_edge("retrieve", "check")
    graph.add_conditional_edges("check", route_check, ["generate", "rewrite", "not_found"])
    graph.add_edge("rewrite", "retrieve")
    for name in ["unsupported", "generate", "not_found"]:
        graph.add_edge(name, END)
    return graph.compile()


_app = None


def run(question: str, history: list[dict] | None = None,
        prev_conditions: dict | None = None) -> GuestlyState:
    """질문 하나를 그래프에 넣어 실행하고 최종 상태를 돌려준다."""
    global _app
    if _app is None:
        _app = build_graph()
    return _app.invoke({"question": question, "history": history or [],
                        "prev_conditions": prev_conditions})

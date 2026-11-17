"""저장된 벡터에서 조건에 맞는 항목을 찾는 검색 모듈."""

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

import config
import ingest
import usage
from md_loader import format_source

_store: InMemoryVectorStore | None = None


def get_store() -> InMemoryVectorStore:
    """벡터 저장 파일을 한 번만 불러와 재사용한다 (문서 임베딩은 하지 않는다)."""
    global _store
    if _store is None:
        if not config.VECTOR_STORE_PATH.exists():
            raise RuntimeError("문서 검색 준비가 아직 안 됐어요. 먼저 `python ingest.py`를 실행해 주세요.")
        if not config.has_api_key():
            raise RuntimeError("OpenAI API 키가 설정되지 않았어요. .env 파일에 OPENAI_API_KEY를 추가해 주세요.")
        embeddings = OpenAIEmbeddings(model=config.OPENAI_EMBED_MODEL,
                                      max_retries=config.API_MAX_RETRIES)
        _store = InMemoryVectorStore.load(str(config.VECTOR_STORE_PATH), embeddings)
    return _store


def make_filter(doc_type: str, region: str | None, budget: int | None):
    """문서 유형·지역·예산 조건을 검사하는 필터 함수를 만든다."""
    def check(doc: Document) -> bool:
        meta = doc.metadata
        if meta.get("doc_type") != doc_type:
            return False
        if region and meta.get("region") != region:
            return False
        # 최저 가격부터 예산을 넘는 항목은 후보에서 뺀다
        if budget is not None and meta.get("price_min", 0) > budget:
            return False
        return True
    return check


def embed_query(store: InMemoryVectorStore, query: str) -> list[float]:
    """검색어를 임베딩한다. 호출 전에 예산을 확인하고 사용량을 기록한다."""
    tokens = ingest.count_tokens([Document(page_content=query)])
    usage.check_budget(usage.estimate_cost(config.OPENAI_EMBED_MODEL, tokens))
    vector = store.embedding.embed_query(query)
    usage.record_usage(config.OPENAI_EMBED_MODEL, tokens, purpose="query")
    return vector


def search(query: str, doc_type: str, region: str | None = None,
           budget: int | None = None, k: int = config.TOP_K) -> list[tuple[Document, float]]:
    """조건으로 먼저 거른 뒤 유사도 순으로 k개를 돌려준다. 점수는 코사인 유사도(높을수록 유사)."""
    store = get_store()
    vector = embed_query(store, query)
    return store.similarity_search_with_score_by_vector(
        vector, k=k, filter=make_filter(doc_type, region, budget))


def sources_of(results: list[tuple[Document, float]]) -> list[str]:
    """검색 결과의 출처 문자열 목록을 만든다."""
    return [format_source(doc.metadata) for doc, _ in results]

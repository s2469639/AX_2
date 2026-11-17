"""data/ 문서를 임베딩해 벡터 저장 파일에 저장하는 스크립트.

문서 임베딩은 이 파일에서만 실행한다. 바뀐 항목만 다시 임베딩한다.

사용법:
    python ingest.py            # 바뀐 항목만 임베딩하고 저장
    python ingest.py --dry-run  # API를 호출하지 않고 무엇이 바뀌는지만 보여 줌
"""

import sys

import tiktoken
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

import config
import md_loader
import usage

# text-embedding-3 계열이 쓰는 토큰 규칙
EMBED_ENCODING = "cl100k_base"


def make_embeddings(dry_run: bool):
    """임베딩 객체를 만든다. 미리보기에서는 API를 쓰지 않는 가짜 임베딩을 쓴다."""
    if dry_run:
        return DeterministicFakeEmbedding(size=8)
    if not config.has_api_key():
        raise RuntimeError(
            "OpenAI API 키가 설정되지 않았어요. "
            "프로젝트 폴더의 .env 파일에 OPENAI_API_KEY를 추가해 주세요."
        )
    return OpenAIEmbeddings(model=config.OPENAI_EMBED_MODEL,
                            max_retries=config.API_MAX_RETRIES)


def load_store(embeddings) -> InMemoryVectorStore:
    """저장된 벡터 파일이 있으면 불러오고, 없으면 빈 저장소를 만든다."""
    if config.VECTOR_STORE_PATH.exists():
        return InMemoryVectorStore.load(str(config.VECTOR_STORE_PATH), embeddings)
    return InMemoryVectorStore(embeddings)


def compare(documents: list[Document], store: InMemoryVectorStore) -> dict:
    """원본 항목과 저장된 항목을 비교해 추가·수정·삭제·위치 변경 목록을 만든다."""
    saved = store.store  # {id: {"id", "vector", "text", "metadata"}}
    current_ids = {doc.id for doc in documents}
    result = {"new": [], "changed": [], "moved": [], "same": [], "deleted": []}
    for doc in documents:
        old = saved.get(doc.id)
        if old is None:
            result["new"].append(doc)
        elif old["metadata"].get("content_hash") != doc.metadata["content_hash"]:
            result["changed"].append(doc)
        elif old["metadata"] != doc.metadata:
            result["moved"].append(doc)  # 내용은 같고 줄 번호 등만 바뀜
        else:
            result["same"].append(doc)
    result["deleted"] = [i for i in saved if i not in current_ids]
    return result


def count_tokens(documents: list[Document]) -> int:
    """임베딩할 글의 토큰 수를 센다 (비용 계산용)."""
    encoding = tiktoken.get_encoding(EMBED_ENCODING)
    return sum(len(encoding.encode(doc.page_content)) for doc in documents)


def print_summary(result: dict, tokens: int) -> None:
    """비교 결과를 사람이 읽기 쉽게 보여 준다."""
    print(f"새 항목 {len(result['new'])}개, 내용 변경 {len(result['changed'])}개, "
          f"위치만 변경 {len(result['moved'])}개, 그대로 {len(result['same'])}개, "
          f"삭제 {len(result['deleted'])}개")
    print(f"임베딩할 토큰 수: {tokens}")


def apply_changes(store: InMemoryVectorStore, result: dict) -> int:
    """삭제·위치 변경·재임베딩을 저장소에 반영하고, 임베딩한 항목 수를 돌려준다."""
    if result["deleted"]:
        store.delete(result["deleted"])
    for doc in result["moved"]:
        # 내용이 같으면 벡터는 그대로 두고 메타데이터(줄 번호)만 바꾼다
        store.store[doc.id]["metadata"] = doc.metadata
    to_embed = result["new"] + result["changed"]
    if to_embed:
        store.add_documents(to_embed, ids=[doc.id for doc in to_embed])
    return len(to_embed)


def main() -> None:
    """문서를 읽고, 바뀐 부분만 임베딩해 저장한다."""
    dry_run = "--dry-run" in sys.argv
    embeddings = make_embeddings(dry_run)
    store = load_store(embeddings)
    result = compare(md_loader.load_all(), store)
    to_embed = result["new"] + result["changed"]
    tokens = count_tokens(to_embed)
    print_summary(result, tokens)

    if dry_run:
        print("미리보기 모드라 API를 호출하지 않았어요.")
        return
    if not to_embed and not result["deleted"] and not result["moved"]:
        print("바뀐 문서가 없어 기존 임베딩을 그대로 사용해요.")
        return
    if to_embed:
        expected = usage.estimate_cost(config.OPENAI_EMBED_MODEL, tokens)
        usage.check_budget(expected)
        print(f"예상 비용: ${expected:.6f}")

    embedded = apply_changes(store, result)
    if embedded:
        usage.record_usage(config.OPENAI_EMBED_MODEL, tokens, purpose="ingest")
    config.STORE_DIR.mkdir(exist_ok=True)
    store.dump(str(config.VECTOR_STORE_PATH))
    print(f"저장 완료: 임베딩 {embedded}개 → {config.VECTOR_STORE_PATH.name}")


if __name__ == "__main__":
    try:
        main()
    except (usage.BudgetError, RuntimeError, ValueError, FileNotFoundError) as error:
        print(f"[안내] {error}")
        sys.exit(1)
    except Exception as error:  # 예상하지 못한 오류 (키 정보는 출력하지 않음)
        print("[안내] 문서 임베딩 중 문제가 생겼어요. 인터넷 연결과 API 키 설정을 확인해 주세요.")
        print(f"(자세한 오류 종류: {type(error).__name__})")
        sys.exit(1)

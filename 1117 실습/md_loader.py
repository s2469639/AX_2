"""data/ 폴더의 Markdown을 항목(## 소제목) 단위 조각으로 나누는 로더.

LangChain 로더는 원본 줄 번호를 주지 않으므로 파일을 줄 단위로 직접 읽는다.
"""

import hashlib
import re
from pathlib import Path

from langchain_core.documents import Document

import config

HEADING_PATTERN = re.compile(r"^##\s+(\S+)\s+(.+?)\s*$")
FIELD_PATTERN = re.compile(r"^-\s*([^:]+):\s*(.*)$")
PRICE_PATTERN = re.compile(r"^(\d+)\s*~\s*(\d+)$")

# 필드 이름 → 메타데이터 키 (필터에 쓰는 값만 따로 꺼낸다)
REGION_FIELD = "지역"
PRICE_FIELDS = ("1인당 가격대", "가격대")

# 임베딩(검색)에 쓰는 필드. ID·가격·주의사항은 필터나 답변에서 쓰므로 검색 글에서 뺀다.
SEARCH_FIELDS = {
    "restaurant": ["음식 종류", "분위기", "식이 제한", "추천 상황"],
    "gift": ["카테고리", "주요 특징", "추천 대상 및 상황", "휴대 편의성"],
    "etiquette": ["주제", "내용", "적용 상황"],
}
# 임베딩은 부정 표현을 잘 구분하지 못하므로(예: '채식 메뉴 없음'이 채식 검색에 걸림)
# 식이 제한 필드에서 이런 말이 든 부분은 검색 글에서 뺀다. 원문은 답변에 그대로 쓴다.
NEGATIVE_WORDS = ("없음", "부적합", "거의 없")


def parse_price(text: str) -> tuple[int, int] | None:
    """'60000~80000' 형태의 가격 문자열을 (최소, 최대) 숫자로 바꾼다."""
    match = PRICE_PATTERN.match(text.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def make_hash(text: str) -> str:
    """조각 내용이 바뀌었는지 비교하기 위한 해시값을 만든다."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def split_sections(lines: list[str]) -> list[tuple[int, int]]:
    """'## ' 소제목 위치를 찾아 항목별 (시작 줄 번호, 끝 줄 번호)를 1부터 세어 돌려준다."""
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    sections = []
    for n, start in enumerate(starts):
        end = starts[n + 1] - 1 if n + 1 < len(starts) else len(lines) - 1
        # 항목 끝의 빈 줄은 줄 범위에서 뺀다
        while end > start and not lines[end].strip():
            end -= 1
        sections.append((start + 1, end + 1))
    return sections


def remove_negative_parts(value: str) -> str:
    """쉼표로 나눈 조각 중 '없음' 같은 부정 표현이 든 조각을 뺀다."""
    parts = [p.strip() for p in value.split(",")]
    return ", ".join(p for p in parts if not any(w in p for w in NEGATIVE_WORDS))


def build_search_text(fields: dict, doc_type: str, name: str) -> str:
    """임베딩용 짧은 검색 글을 만든다 (이름 + 핵심 필드)."""
    lines = [name]
    for key in SEARCH_FIELDS[doc_type]:
        value = fields.get(key, "")
        if key == "식이 제한":
            value = remove_negative_parts(value)
        if value:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def build_metadata(fields: dict, file_name: str, doc_type: str,
                   item_id: str, heading: str, line_start: int,
                   line_end: int, text: str, search_text: str) -> dict:
    """항목의 필드에서 검색·필터·출처 표시에 필요한 메타데이터를 만든다."""
    metadata = {
        "doc_type": doc_type,
        "item_id": item_id,
        "source": file_name,
        "heading": heading,
        "line_start": line_start,
        "line_end": line_end,
        "full_text": text,  # 답변 생성에 쓰는 원문 전체
        # 원문이나 검색 글 규칙이 바뀌면 다시 임베딩하도록 둘 다 해시에 넣는다
        "content_hash": make_hash(search_text + "\n---\n" + text),
    }
    if REGION_FIELD in fields:
        metadata["region"] = fields[REGION_FIELD]
    for price_field in PRICE_FIELDS:
        price = parse_price(fields.get(price_field, ""))
        if price:
            metadata["price_min"], metadata["price_max"] = price
            break
    return metadata


def load_file(path: Path, doc_type: str) -> list[Document]:
    """Markdown 파일 하나를 읽어 항목별 Document 목록으로 만든다."""
    lines = path.read_text(encoding="utf-8").splitlines()
    documents = []
    for line_start, line_end in split_sections(lines):
        heading_line = lines[line_start - 1]
        match = HEADING_PATTERN.match(heading_line)
        if not match:
            raise ValueError(
                f"{path.name} {line_start}행의 소제목 형식이 올바르지 않아요. "
                "'## ID 이름' 형태로 적어 주세요."
            )
        item_id = match.group(1)
        heading = heading_line[3:].strip()
        body = lines[line_start - 1:line_end]
        fields = {}
        for line in body[1:]:
            field = FIELD_PATTERN.match(line)
            if field:
                fields[field.group(1).strip()] = field.group(2).strip()
        text = "\n".join(body)
        name = match.group(2).strip()
        search_text = build_search_text(fields, doc_type, name)
        metadata = build_metadata(fields, path.name, doc_type, item_id,
                                  heading, line_start, line_end, text, search_text)
        # page_content(임베딩 대상)는 검색 글, 원문은 metadata["full_text"]
        documents.append(Document(id=item_id, page_content=search_text, metadata=metadata))
    return documents


def load_all() -> list[Document]:
    """data/ 폴더의 모든 대상 문서를 읽어 하나의 목록으로 합친다."""
    documents = []
    for file_name, doc_type in config.DATA_FILES.items():
        path = config.DATA_DIR / file_name
        if not path.exists():
            raise FileNotFoundError(
                f"'{file_name}' 파일을 찾지 못했어요. data 폴더에 파일이 있는지 확인해 주세요."
            )
        documents.extend(load_file(path, doc_type))
    ids = [doc.id for doc in documents]
    duplicated = {i for i in ids if ids.count(i) > 1}
    if duplicated:
        raise ValueError(f"같은 ID가 여러 번 쓰였어요: {', '.join(sorted(duplicated))}")
    return documents


def format_source(metadata: dict) -> str:
    """출처를 '파일명 > 소제목 > 시작~끝행' 형식의 문자열로 만든다."""
    return (f"{metadata['source']} > {metadata['heading']} > "
            f"{metadata['line_start']}~{metadata['line_end']}행")

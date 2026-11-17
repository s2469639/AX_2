"""GUESTLY 설정값을 한 곳에 모아 둔 파일."""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env 파일의 환경변수를 불러온다 (파일 내용은 출력하지 않는다)
load_dotenv()

# 폴더와 파일 경로
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STORE_DIR = BASE_DIR / "store"
VECTOR_STORE_PATH = STORE_DIR / "vector_store.json"
USAGE_LOG_PATH = STORE_DIR / "usage_log.jsonl"

# 검색 대상 문서와 문서 유형
DATA_FILES = {
    "restaurants.md": "restaurant",
    "gifts.md": "gift",
    "etiquette.md": "etiquette",
}

# 모델 이름 (환경변수가 없으면 기본값 사용)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# gpt-6-luna는 추론 모델이라 기본값(medium)이면 추론 토큰이 출력 비용으로 청구된다.
# 비용을 줄이기 위해 추론을 끈다 (2026-11-17 사용자 승인, 조사노트.md 참고).
REASONING_EFFORT = "none"

# 검색·대화 제한
TOP_K = 3
MAX_HISTORY_MESSAGES = 4
MAX_RETRY_SEARCH = 1
API_MAX_RETRIES = 0  # API 오류 시 자동 재시도하지 않는다

# 근거 충분 기준: 1위 코사인 유사도 (잠정값, 조사노트.md 3-1장)
SCORE_THRESHOLD = 0.40

# 단계별 최대 출력 토큰 (비용 상한)
MAX_TOKENS_ANALYZE = 400
MAX_TOKENS_REWRITE = 150
MAX_TOKENS_GENERATE = 900

# 데이터에 있는 식당 지역 (질문 분석 시 이 중에서만 고른다)
REGIONS = ["강남", "광화문", "종로", "여의도", "성수", "이태원", "명동", "잠실"]

NOT_FOUND_MESSAGE = "문서에서 찾지 못했어요"

# 예산 한도 (달러)
DAILY_BUDGET_USD = 1.0
MONTHLY_BUDGET_USD = 5.0

# 100만 토큰당 단가 (달러, Standard 기준). 2026-11-17 OpenAI 공식 모델 페이지에서 확인.
# 가격이 바뀌면 조사노트.md 2장과 함께 고친다.
PRICE_PER_1M_TOKENS = {
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "gpt-6-luna": {"input": 0.10, "output": 0.50},
}


def has_api_key() -> bool:
    """OpenAI API 키가 설정되어 있는지만 확인한다 (키 값은 다루지 않는다)."""
    return bool(os.getenv("OPENAI_API_KEY"))

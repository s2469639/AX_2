"""임베딩 유사도 확인 (OpenAI 호출은 딱 1번, 문장 6개를 한꺼번에).

질문 문장과 나머지 5개 문장이 얼마나 비슷한지(코사인 유사도)를 큰 순서로 보여 줘요.
키와 숫자 목록(벡터)은 화면에 출력하지 않아요.
"""
import math
import os
import sys
from pathlib import Path

QUESTION = "배에 짐을 실은 증거 서류가 뭐야?"
SENTENCES = [
    "선하증권(B/L)은 화물을 선적했다는 증서다",
    "FOB 는 본선에 실으면 위험이 넘어간다",
    "오늘 점심은 김치찌개를 먹었다",
    "인보이스는 거래 금액을 적은 상업 송장이다",
    "고양이는 낮잠을 많이 잔다",
]


def cosine(a, b):
    """두 숫자 목록이 얼마나 같은 방향인지(1에 가까울수록 비슷)를 계산해요."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def main():
    """준비물을 확인하고, 문장 6개를 임베딩해서 유사도 표를 출력해요."""
    # 필요한 패키지가 없으면 이유를 알려 주고 끝내요.
    try:
        from dotenv import load_dotenv
        from langchain_openai import OpenAIEmbeddings
    except ImportError:
        print("패키지가 없어요: pip install python-dotenv langchain-openai (가상환경 .venv 안에서)")
        sys.exit(1)

    # .env 는 이 파일과 같은 폴더에서 읽어요. 내용은 출력하지 않아요.
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print(".env 파일이 없어요. .env.example 을 .env 로 복사하고 키를 직접 넣어 주세요.")
        sys.exit(1)
    load_dotenv(env_path)

    model = os.getenv("OPENAI_EMBED_MODEL")
    if not os.getenv("OPENAI_API_KEY") or not model:
        print(".env 에 OPENAI_API_KEY 와 OPENAI_EMBED_MODEL 값이 모두 있어야 해요.")
        sys.exit(1)

    texts = [QUESTION] + SENTENCES
    try:
        vectors = OpenAIEmbeddings(model=model).embed_documents(texts)  # 호출 1번
    except Exception as e:
        # 오류 메시지에 키 일부가 섞일 수 있어서 종류만 알려 줘요.
        print(f"임베딩 호출에 실패했어요 ({type(e).__name__}). 키와 모델 이름을 확인해 주세요.")
        sys.exit(1)

    scores = [(cosine(vectors[0], v), s) for v, s in zip(vectors[1:], SENTENCES)]
    scores.sort(reverse=True)

    print(f"모델: {model}")
    print(f"질문: {QUESTION}\n")
    print("| 순위 | 유사도 | 문장 |")
    print("|---|---|---|")
    for rank, (score, sentence) in enumerate(scores, start=1):
        print(f"| {rank} | {score:.4f} | {sentence} |")


if __name__ == "__main__":
    main()

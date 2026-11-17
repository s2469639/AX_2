"""생성 모델 호출을 한 곳에서 처리한다. 호출 전 예산 확인, 호출 후 사용량 기록."""

import tiktoken
from langchain_openai import ChatOpenAI

import config
import usage

# gpt-6-luna의 토큰 규칙은 공개되지 않아 o200k_base로 추정하고 여유분을 더한다
ESTIMATE_ENCODING = "o200k_base"
ESTIMATE_MARGIN = 1.3

_models: dict[int, ChatOpenAI] = {}


def get_model(max_tokens: int) -> ChatOpenAI:
    """출력 길이 제한별로 모델 객체를 만들어 재사용한다."""
    if not config.has_api_key():
        raise RuntimeError("OpenAI API 키가 설정되지 않았어요. .env 파일에 OPENAI_API_KEY를 추가해 주세요.")
    if max_tokens not in _models:
        _models[max_tokens] = ChatOpenAI(
            model=config.OPENAI_MODEL,
            reasoning_effort=config.REASONING_EFFORT,
            max_tokens=max_tokens,
            max_retries=config.API_MAX_RETRIES,
        )
    return _models[max_tokens]


def estimate_input_tokens(messages: list[tuple[str, str]]) -> int:
    """보낼 메시지의 토큰 수를 넉넉하게 추정한다."""
    encoding = tiktoken.get_encoding(ESTIMATE_ENCODING)
    total = sum(len(encoding.encode(text)) + 4 for _, text in messages)
    return int(total * ESTIMATE_MARGIN)


def check_before_call(messages: list[tuple[str, str]], max_tokens: int) -> None:
    """최대 출력까지 썼다고 가정한 비용으로 예산을 미리 확인한다."""
    expected = usage.estimate_cost(config.OPENAI_MODEL,
                                   estimate_input_tokens(messages), max_tokens)
    usage.check_budget(expected)


def record(message, purpose: str) -> None:
    """응답에 담긴 실제 토큰 수로 사용량을 기록한다."""
    meta = getattr(message, "usage_metadata", None) or {}
    usage.record_usage(config.OPENAI_MODEL, meta.get("input_tokens", 0),
                       meta.get("output_tokens", 0), purpose=purpose)


def ask_text(messages: list[tuple[str, str]], max_tokens: int, purpose: str) -> str:
    """글 형태의 답을 받는다."""
    check_before_call(messages, max_tokens)
    response = get_model(max_tokens).invoke(messages)
    record(response, purpose)
    return response.content


def ask_structured(messages: list[tuple[str, str]], schema, max_tokens: int, purpose: str):
    """정해진 형식(pydantic 모델)으로 답을 받는다."""
    check_before_call(messages, max_tokens)
    runnable = get_model(max_tokens).with_structured_output(schema, include_raw=True)
    result = runnable.invoke(messages)
    record(result["raw"], purpose)
    if result.get("parsing_error") or result.get("parsed") is None:
        raise ValueError("질문을 이해하는 중 문제가 생겼어요. 조금 다르게 다시 질문해 주세요.")
    return result["parsed"]

"""API 사용량을 로컬 파일에 기록하고, 호출 전에 예산 한도를 확인하는 모듈.

로컬 기록은 예상치이며 실제 청구액을 완전히 막지는 못한다.
"""

import json
from datetime import datetime

import config


class BudgetError(Exception):
    """예산 한도를 넘었거나 비용을 계산할 수 없을 때 쓰는 오류."""


def get_price(model: str) -> dict:
    """모델의 100만 토큰당 단가를 가져온다. 단가가 비어 있으면 호출을 막는다."""
    price = config.PRICE_PER_1M_TOKENS.get(model)
    if not price or price["input"] is None or price["output"] is None:
        raise BudgetError(
            f"'{model}' 모델의 가격 정보가 설정되지 않아 비용을 계산할 수 없어요. "
            "config.py의 PRICE_PER_1M_TOKENS를 먼저 채워 주세요."
        )
    return price


def estimate_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """토큰 수로 예상 비용(달러)을 계산한다."""
    price = get_price(model)
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


def read_records() -> list[dict]:
    """지금까지 기록된 사용량을 모두 읽어 온다."""
    if not config.USAGE_LOG_PATH.exists():
        return []
    records = []
    for line in config.USAGE_LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def spent_totals(now: datetime | None = None) -> tuple[float, float]:
    """오늘과 이번 달에 쓴 예상 비용 합계를 (오늘, 이번 달)로 돌려준다."""
    now = now or datetime.now()
    today, month = now.strftime("%Y-%m-%d"), now.strftime("%Y-%m")
    day_total = month_total = 0.0
    for record in read_records():
        if record["time"].startswith(month):
            month_total += record["cost_usd"]
            if record["time"].startswith(today):
                day_total += record["cost_usd"]
    return day_total, month_total


def check_budget(expected_cost: float) -> None:
    """이번 호출을 하면 한도를 넘는지 호출 전에 확인한다."""
    day_total, month_total = spent_totals()
    if day_total + expected_cost > config.DAILY_BUDGET_USD:
        raise BudgetError("오늘 사용할 수 있는 예산을 다 썼어요. 내일 다시 이용해 주세요.")
    if month_total + expected_cost > config.MONTHLY_BUDGET_USD:
        raise BudgetError("이번 달 사용할 수 있는 예산을 다 썼어요. 다음 달에 다시 이용해 주세요.")


def record_usage(model: str, input_tokens: int, output_tokens: int = 0,
                 purpose: str = "") -> float:
    """호출 한 번의 시각, 모델, 토큰 수, 예상 비용을 파일에 한 줄로 남긴다."""
    cost = estimate_cost(model, input_tokens, output_tokens)
    record = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "model": model,
        "purpose": purpose,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 8),
    }
    config.STORE_DIR.mkdir(exist_ok=True)
    with config.USAGE_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return cost

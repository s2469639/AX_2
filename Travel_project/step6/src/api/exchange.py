import os
import requests

def get_exchange_rates(base_currency="USD"):
    """
    ExchangeRate-API를 통해 기준 통화 대비 환율 정보를 가져옵니다.
    """
    api_key = os.getenv("EXCHANGE_API_KEY")
    if not api_key:
        # 키 미설정 시 기본 fallback 환율 반환 (안전장치)
        return {"error": ".env에 EXCHANGE_API_KEY가 설정되지 않았습니다."}

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            return data.get("conversion_rates", {})
        else:
            return {"error": "환율 API 응답 오류"}
    except requests.exceptions.RequestException as e:
        return {"error": f"환율 데이터를 가져올 수 없습니다: {e}"}

def calculate_cash_exchange(base_rate: float, spread_percent=1.75):
    """
    은행 현찰 살 때 / 팔 때 스프레드를 반영한 환율을 계산합니다.
    (일반적인 은행 현찰 스프레드: 약 1.5% ~ 1.75%)
    - 현찰 살 때 (KRW -> 외화): 기준율 * (1 + spread)
    - 현찰 팔 때 (외화 -> KRW): 기준율 * (1 - spread)
    """
    spread = spread_percent / 100
    buy_rate = base_rate * (1 + spread)
    sell_rate = base_rate * (1 - spread)
    return {
        "base_rate": base_rate,
        "buy_rate": buy_rate,
        "sell_rate": sell_rate
    }
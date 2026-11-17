# (가상) 견적 계산 — 연습용 코드
def total(price, qty):
    return price * qty

def with_shipping(price, qty, shipping):
    return total(price, qty) + shipping

if __name__ == "__main__":
    print(with_shipping(12, 500, 300))

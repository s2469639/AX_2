"""수업용 가상 기록 10줄을 data/entries.csv 로 만들어요.
- 날짜는 '오늘'을 기준으로 만들어져서 언제 실행해도 연속 기록이 4일(어제까지)로 보여요.
- 이미 파일이 있으면 지우지 않고 멈춰요. (다시 만들고 싶으면: python make_sample.py --reset)
"""
import csv, sys, datetime, pathlib

p = pathlib.Path(__file__).parent / "data" / "entries.csv"
if p.exists() and "--reset" not in sys.argv:
    print("이미 data/entries.csv 가 있어요. 지우지 않고 멈출게요. (새로 만들려면 --reset)")
    sys.exit(0)

t = datetime.date.today()
d = lambda n: (t - datetime.timedelta(days=n)).isoformat()
rows = [
    (d(14), "스터디 첫날, 자기소개만 하다 끝났다", ""),
    (d(13), "영어 면접 질문 10개 소리 내서 읽음", ""),
    (d(11), "비 와서 도서관 대신 집에서 공부", ""),
    (d(9), "포트폴리오 사이트에 프로젝트 하나 추가", "😀"),
    (d(8), "아무것도 하기 싫은 날. 그래도 한 줄은 씀", "😴"),
    (d(6), "모의 면접에서 말이 너무 빨랐다", "😢"),
    (d(4), "AI로 견적서 자동화 만들어 봄. 신기함", "😀"),
    (d(3), "운동 30분, 머리가 맑아졌다", "🙂"),
    (d(2), "지원서 마감 하루 전, 겨우 제출 완료!", "😀"),
    (d(1), "Claude Code로 앱 만들기 시작", "🙂"),
]
p.parent.mkdir(exist_ok=True)
with p.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "text", "mood"])
    w.writerows(rows)
print(f"가상 기록 {len(rows)}줄을 만들었어요 → {p}")

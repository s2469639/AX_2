"""계산 담당 (화면·파일과 상관없는 순수 계산만 있어요)."""
from datetime import date, timedelta

MAX_LEN = 100

MSG_EMPTY = "한 글자 이상 써 주세요"
MSG_TOO_LONG = "100자까지 쓸 수 있어요"
MSG_NO_ENTRIES = "첫 한 줄을 남겨 보세요"
MSG_NO_MOOD = "오늘 기분을 골라 주세요"

# 기분 태그 5종 (이모지, 이름). 여기 한 곳에서만 정의해요.
MOODS = [
    ("😀", "좋음"),
    ("🙂", "보통"),
    ("😢", "힘듦"),
    ("😡", "화남"),
    ("😴", "지침"),
]
MOOD_EMOJIS = [e for e, _ in MOODS]
NO_MOOD_MARK = "—"


def clean_text(raw: str) -> str:
    """앞뒤 공백(스페이스·탭·줄바꿈)을 지운 글자."""
    return (raw or "").strip()


def validate_text(raw: str):
    """한 줄이 저장 가능한지 검사. 문제가 없으면 None, 있으면 안내 문구를 돌려줘요."""
    n = len(clean_text(raw))
    if n == 0:
        return MSG_EMPTY
    if n > MAX_LEN:
        return MSG_TOO_LONG
    return None


def validate_mood(mood):
    """기분 태그를 골랐는지 검사. 5종 중 하나면 None, 아니면 안내 문구."""
    if mood in MOOD_EMOJIS:
        return None
    return MSG_NO_MOOD


def mood_display(mood: str) -> str:
    """목록에 보여 줄 기분. 비어 있는 예전 기록은 '—'로 보여요."""
    return mood if mood in MOOD_EMOJIS else NO_MOOD_MARK


def make_entry(raw: str, today: date, mood: str) -> dict:
    """저장할 기록 한 줄을 만들어요. today는 밖에서 받아요(검사하기 쉽게)."""
    return {"date": today.isoformat(), "text": clean_text(raw), "mood": mood}


MSG_KEEP_STREAK = "오늘도 써서 이어 가요"


def _to_date(s):
    try:
        return date.fromisoformat((s or "").strip())
    except ValueError:
        return None


def streak_info(entries: list, today: date):
    """연속 기록 일수와 오늘 썼는지를 (일수, 오늘썼나)로 돌려줘요.
    - 같은 날 여러 줄은 하루로 세요.
    - 오늘 썼으면 오늘부터, 아직 안 썼으면 어제부터 거꾸로 세요.
    - 하루라도 비면 거기서 끊겨요. 기록이 없으면 0일이에요.
    - 날짜를 읽을 수 없는 줄은 무시해요."""
    days = {d for d in (_to_date(e.get("date")) for e in entries) if d is not None}
    wrote_today = today in days
    cur = today if wrote_today else today - timedelta(days=1)
    count = 0
    while cur in days:
        count += 1
        cur -= timedelta(days=1)
    return count, wrote_today


MSG_NO_WEEK = "이번 주 첫 기록을 남겨 보세요"


def week_range(today: date):
    """오늘이 속한 주의 (월요일, 일요일)."""
    monday = today - timedelta(days=today.weekday())
    return monday, monday + timedelta(days=6)


def week_summary(entries: list, today: date):
    """이번 주(월~일) 요약. 이번 주 기록이 0개면 None.
    - count: 이번 주 기록 수 (지난주·다음주 기록은 세지 않아요)
    - top_moods: 가장 많은 기분 이모지 목록 (같은 수면 모두, 5종 순서대로). 기분이 전부 비었으면 []
    - longest: 가장 긴 한 줄 기록 (글자 수 기준, 같으면 나중에 저장한 기록)"""
    start, end = week_range(today)
    week = []
    for i, e in enumerate(entries):
        d = _to_date(e.get("date"))
        if d is not None and start <= d <= end:
            week.append((i, e))
    if not week:
        return None
    counts = {}
    for _, e in week:
        if e.get("mood") in MOOD_EMOJIS:
            counts[e["mood"]] = counts.get(e["mood"], 0) + 1
    best = max(counts.values()) if counts else 0
    top = [m for m in MOOD_EMOJIS if counts.get(m, 0) == best] if counts else []
    _, longest = max(week, key=lambda p: (len(clean_text(p[1].get("text"))), p[0]))
    return {"count": len(week), "top_moods": top, "longest": longest}


MSG_NO_RESULT = "찾는 기록이 없어요"


def search_entries(entries: list, query) -> list:
    """한 줄 본문에 검색어가 들어간 기록만 돌려줘요.
    - 영어 대문자·소문자는 가리지 않아요.
    - 검색칸이 비어 있거나 공백뿐이면 전체를 그대로 돌려줘요.
    - 날짜·기분은 찾지 않고 본문만 봐요. 원래 목록은 바꾸지 않아요."""
    q = clean_text(query).casefold()
    if not q:
        return list(entries)
    return [e for e in entries if q in (e.get("text") or "").casefold()]


def sort_newest_first(entries: list) -> list:
    """최신 날짜가 위. 같은 날이면 나중에 저장한(파일에서 더 아래) 기록이 위."""
    indexed = list(enumerate(entries))
    indexed.sort(key=lambda p: (p[1]["date"], p[0]), reverse=True)
    return [e for _, e in indexed]

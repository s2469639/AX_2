"""F4(이번 주 요약) 검사. 오늘은 2026-11-11(수)로 고정 → 이번 주는 11/9(월)~11/15(일)."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logic

TODAY = date(2026, 11, 11)  # 수요일


def _e(d, text="글", mood=""):
    return {"date": d, "text": text, "mood": mood}


def test_주는_월요일부터_일요일():
    assert logic.week_range(TODAY) == (date(2026, 11, 9), date(2026, 11, 15))
    assert logic.week_range(date(2026, 11, 9)) == (date(2026, 11, 9), date(2026, 11, 15))  # 월
    assert logic.week_range(date(2026, 11, 15)) == (date(2026, 11, 9), date(2026, 11, 15))  # 일


def test_F4_1_지난주_기록은_세지_않는다():
    es = [_e("2026-11-08", "지난주 일요일"), _e("2026-11-09", "이번주 월요일"), _e("2026-11-10")]
    s = logic.week_summary(es, TODAY)
    assert s["count"] == 2


def test_F4_1_다음주_기록도_세지_않는다():
    es = [_e("2026-11-15", "이번주 일요일"), _e("2026-11-16", "다음주 월요일")]
    assert logic.week_summary(es, TODAY)["count"] == 1


def test_F4_2_이번주_기록이_0개면_None과_안내문구():
    assert logic.week_summary([], TODAY) is None
    assert logic.week_summary([_e("2026-11-08")], TODAY) is None
    assert logic.MSG_NO_WEEK == "이번 주 첫 기록을 남겨 보세요"


def test_F4_3_가장_많은_기분_하나():
    es = [_e("2026-11-09", mood="😀"), _e("2026-11-10", mood="😀"), _e("2026-11-11", mood="🙂")]
    assert logic.week_summary(es, TODAY)["top_moods"] == ["😀"]


def test_F4_3_같은_수면_둘_다_보여준다():
    es = [_e("2026-11-09", mood="🙂"), _e("2026-11-10", mood="😀")]
    assert logic.week_summary(es, TODAY)["top_moods"] == ["😀", "🙂"]


def test_기분이_전부_비면_빈_목록():
    es = [_e("2026-11-09"), _e("2026-11-10")]
    assert logic.week_summary(es, TODAY)["top_moods"] == []


def test_지난주_기분은_세지_않는다():
    es = [_e("2026-11-02", mood="😢"), _e("2026-11-03", mood="😢"), _e("2026-11-09", mood="😀")]
    assert logic.week_summary(es, TODAY)["top_moods"] == ["😀"]


def test_가장_긴_한_줄():
    es = [_e("2026-11-09", "짧음"), _e("2026-11-10", "이게 제일 긴 한 줄이에요"), _e("2026-11-11", "중간 길이")]
    assert logic.week_summary(es, TODAY)["longest"]["text"] == "이게 제일 긴 한 줄이에요"


def test_가장_긴_한_줄_글자수가_같으면_나중_기록():
    es = [_e("2026-11-09", "가나다"), _e("2026-11-10", "라마바")]
    assert logic.week_summary(es, TODAY)["longest"]["text"] == "라마바"


def test_가장_긴_한_줄은_지난주_글을_보지_않는다():
    es = [_e("2026-11-03", "지난주에 쓴 아주 아주 아주 긴 글입니다"), _e("2026-11-09", "짧")]
    assert logic.week_summary(es, TODAY)["longest"]["text"] == "짧"


def test_날짜를_읽을_수_없는_줄은_무시():
    es = [_e(""), _e("어제"), _e("2026-11-09", "글")]
    assert logic.week_summary(es, TODAY)["count"] == 1


def test_일요일에_보아도_같은_주():
    sunday = date(2026, 11, 15)
    es = [_e("2026-11-09"), _e("2026-11-15")]
    assert logic.week_summary(es, sunday)["count"] == 2
    assert logic.week_summary(es, date(2026, 11, 16)) is None  # 다음 월요일엔 새 주

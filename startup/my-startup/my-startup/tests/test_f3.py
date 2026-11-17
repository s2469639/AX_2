"""F3(연속 기록) 검사. 오늘 날짜는 고정해서 시험하고, 임시 파일만 써요."""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logic
import storage

TODAY = date(2026, 11, 11)


def _e(*days_ago):
    return [{"date": (TODAY - timedelta(days=n)).isoformat(), "text": "글", "mood": "🙂"} for n in days_ago]


def test_F3_1_오늘_썼으면_오늘을_포함해_센다():
    assert logic.streak_info(_e(0, 1, 2), TODAY) == (3, True)


def test_F3_1_오늘만_썼으면_1일():
    assert logic.streak_info(_e(0), TODAY) == (1, True)


def test_F3_2_오늘_안_썼으면_어제까지_이어진_일수():
    assert logic.streak_info(_e(1, 2, 3, 4), TODAY) == (4, False)


def test_F3_2_안내문구():
    assert logic.MSG_KEEP_STREAK == "오늘도 써서 이어 가요"


def test_F3_3_하루라도_비면_끊긴다():
    # 오늘, 어제 있고 그저께 없음, 3일 전은 세지 않는다
    assert logic.streak_info(_e(0, 1, 3), TODAY) == (2, True)


def test_F3_3_어제도_없으면_0일():
    assert logic.streak_info(_e(2, 3, 4), TODAY) == (0, False)


def test_F3_4_같은_날_여러_줄은_하루():
    assert logic.streak_info(_e(0, 0, 0, 1, 1), TODAY) == (2, True)


def test_F3_5_기록이_0개면_0일():
    assert logic.streak_info([], TODAY) == (0, False)


def test_날짜를_읽을_수_없는_줄은_무시():
    es = _e(0, 1) + [{"date": "", "text": "x", "mood": ""}, {"date": "어제", "text": "y", "mood": ""}]
    assert logic.streak_info(es, TODAY) == (2, True)


def test_월_경계도_정확하다():
    today = date(2026, 3, 1)
    es = [{"date": d, "text": "글", "mood": ""} for d in ["2026-03-01", "2026-02-28", "2026-02-27"]]
    assert logic.streak_info(es, today) == (3, True)


def test_샘플_모양_기록은_연속_4일(tmp_path):
    p = tmp_path / "e.csv"
    p.write_text(
        "date,text,mood\n2026-11-05,a,\n2026-11-07,b,😀\n2026-11-08,c,🙂\n2026-11-09,d,😀\n2026-11-10,e,🙂\n",
        encoding="utf-8",
    )
    assert logic.streak_info(storage.read_entries(p), TODAY) == (4, False)

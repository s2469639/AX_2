"""F2(기분 태그) 검사. 진짜 data/entries.csv는 건드리지 않고 임시 파일만 써요."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logic
import storage

TODAY = date(2026, 11, 11)


def test_태그는_5종():
    assert logic.MOOD_EMOJIS == ["😀", "🙂", "😢", "😡", "😴"]
    assert [n for _, n in logic.MOODS] == ["좋음", "보통", "힘듦", "화남", "지침"]


def test_5종_중_하나면_통과():
    for e in logic.MOOD_EMOJIS:
        assert logic.validate_mood(e) is None


def test_안_고르면_안내문구():
    for m in [None, "", "아무거나", "👍"]:
        assert logic.validate_mood(m) == "오늘 기분을 골라 주세요"


def test_빈_예전_기록은_대시로_보인다():
    assert logic.mood_display("") == "—"
    assert logic.mood_display(None) == "—"
    assert logic.mood_display("😀") == "😀"


def test_고른_태그가_기록에_저장된다(tmp_path):
    p = tmp_path / "e.csv"
    storage.append_entry(logic.make_entry("오늘 한 줄", TODAY, "😴"), p)
    rows = storage.read_entries(p)
    assert rows[0]["mood"] == "😴"
    assert logic.mood_display(rows[0]["mood"]) == "😴"


def test_예전_빈_mood_기록도_깨지지_않는다(tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("date,text,mood\n2026-10-28,옛 기록,\n", encoding="utf-8")
    rows = storage.read_entries(p)
    assert [logic.mood_display(r["mood"]) for r in rows] == ["—"]

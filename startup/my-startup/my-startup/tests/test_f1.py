"""F1(한 줄 기록) 검사. 진짜 data/entries.csv는 건드리지 않고 임시 파일만 써요."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logic
import storage

TODAY = date(2026, 11, 11)


def test_1자_100자는_저장_가능():
    assert logic.validate_text("가") is None
    assert logic.validate_text("가" * 100) is None


def test_빈칸_공백만_있으면_안내문구():
    for raw in ["", "   ", "\t\n "]:
        assert logic.validate_text(raw) == "한 글자 이상 써 주세요"


def test_101자는_안내문구():
    assert logic.validate_text("가" * 101) == "100자까지 쓸 수 있어요"


def test_앞뒤_공백은_글자수에서_뺀다():
    assert logic.validate_text("  " + "가" * 100 + "  ") is None


def test_기록모양은_기존_csv와_같다():
    e = logic.make_entry("  안녕  ", TODAY, "🙂")
    assert e == {"date": "2026-11-11", "text": "안녕", "mood": "🙂"}


def test_최신이_맨_위_같은날은_나중_저장이_위():
    es = [
        {"date": "2026-11-10", "text": "a", "mood": ""},
        {"date": "2026-11-11", "text": "b", "mood": ""},
        {"date": "2026-11-11", "text": "c", "mood": ""},
    ]
    assert [e["text"] for e in logic.sort_newest_first(es)] == ["c", "b", "a"]


def test_파일이_없으면_빈_목록(tmp_path):
    assert storage.read_entries(tmp_path / "없음.csv") == []


def test_제목줄만_있어도_빈_목록(tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("date,text,mood\n", encoding="utf-8")
    assert storage.read_entries(p) == []


def test_덧붙이면_기존_기록은_그대로(tmp_path):
    p = tmp_path / "e.csv"
    original = 'date,text,mood\n2026-11-10,"쉼표, 있는 글",🙂\n'
    p.write_text(original, encoding="utf-8")
    storage.append_entry(logic.make_entry("새 글", TODAY, "😀"), p)
    assert p.read_text(encoding="utf-8").startswith(original)
    rows = storage.read_entries(p)
    assert len(rows) == 2
    assert rows[0]["text"] == "쉼표, 있는 글" and rows[0]["mood"] == "🙂"
    assert rows[1] == {"date": "2026-11-11", "text": "새 글", "mood": "😀"}


def test_마지막줄에_줄바꿈이_없어도_안_붙는다(tmp_path):
    p = tmp_path / "e.csv"
    p.write_bytes("date,text,mood\n2026-11-10,글,".encode("utf-8"))
    storage.append_entry(logic.make_entry("새 글", TODAY, "😀"), p)
    assert len(storage.read_entries(p)) == 2


def test_파일이_없으면_제목줄과_함께_새로_만든다(tmp_path):
    p = tmp_path / "data" / "e.csv"
    storage.append_entry(logic.make_entry("첫 글", TODAY, "😀"), p)
    assert p.read_text(encoding="utf-8").splitlines()[0] == "date,text,mood"
    assert len(storage.read_entries(p)) == 1

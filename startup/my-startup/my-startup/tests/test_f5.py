"""F5(단어 검색) 검사. 임시 파일만 써요."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logic
import storage


def _e(text, d="2026-11-10", mood=""):
    return {"date": d, "text": text, "mood": mood}


ES = [
    _e("영어 면접 질문 10개 소리 내서 읽음", "2026-10-29"),
    _e("Claude Code로 앱 만들기 시작", "2026-11-10"),
    _e("운동 30분, 머리가 맑아졌다", "2026-11-08"),
    _e("모의 면접에서 말이 너무 빨랐다", "2026-11-05"),
]


def test_F5_본문_단어가_들어간_기록만():
    r = logic.search_entries(ES, "면접")
    assert [e["text"] for e in r] == [ES[0]["text"], ES[3]["text"]]


def test_F5_1_영어는_대소문자를_가리지_않는다():
    for q in ["claude", "CLAUDE", "Claude", "cLaUdE"]:
        assert [e["text"] for e in logic.search_entries(ES, q)] == [ES[1]["text"]]


def test_F5_1_영어_본문도_소문자_검색():
    es = [_e("Python study"), _e("다른 글")]
    assert len(logic.search_entries(es, "PYTHON")) == 1


def test_F5_2_결과가_0개면_빈_목록과_안내문구():
    assert logic.search_entries(ES, "없는단어") == []
    assert logic.MSG_NO_RESULT == "찾는 기록이 없어요"


def test_F5_3_검색칸이_비면_전체():
    for q in ["", "   ", None]:
        assert logic.search_entries(ES, q) == ES


def test_앞뒤_공백은_무시():
    assert len(logic.search_entries(ES, "  면접  ")) == 2


def test_날짜나_기분은_찾지_않는다():
    es = [_e("글", "2026-11-10", "😀")]
    assert logic.search_entries(es, "2026") == []
    assert logic.search_entries(es, "😀") == []


def test_원래_목록은_바뀌지_않는다():
    before = [dict(e) for e in ES]
    logic.search_entries(ES, "면접")
    assert ES == before


def test_기록이_하나도_없어도_멀쩡():
    assert logic.search_entries([], "면접") == []
    assert logic.search_entries([], "") == []


def test_mood_빈칸_예전_기록도_검색된다(tmp_path):
    p = tmp_path / "e.csv"
    p.write_text("date,text,mood\n2026-10-28,스터디 첫날,\n", encoding="utf-8")
    assert len(logic.search_entries(storage.read_entries(p), "스터디")) == 1

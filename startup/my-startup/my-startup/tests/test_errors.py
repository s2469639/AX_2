"""파일 읽기/쓰기가 실패했을 때 쉬운 한국어 안내가 나오는지 검사. 임시 파일만 써요."""
import re
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import logic
import storage

TODAY = date(2026, 11, 11)


def _has_hangul_no_english_trace(msg: str):
    assert re.search(r"[가-힣]", msg)
    assert "Traceback" not in msg and "Error" not in msg and "Exception" not in msg


def test_망가진_파일은_한국어_안내(tmp_path):
    p = tmp_path / "e.csv"
    p.write_bytes(b"\xff\xfe\x00\x80 not utf-8 \xff")
    with pytest.raises(storage.StorageError) as e:
        storage.read_entries(p)
    _has_hangul_no_english_trace(str(e.value))


def test_저장_실패는_한국어_안내(tmp_path):
    folder_as_file = tmp_path / "e.csv"
    folder_as_file.mkdir()  # 파일 자리에 폴더가 있어서 저장할 수 없는 상황
    with pytest.raises(storage.StorageError) as e:
        storage.append_entry(logic.make_entry("글", TODAY, "🙂"), folder_as_file)
    _has_hangul_no_english_trace(str(e.value))

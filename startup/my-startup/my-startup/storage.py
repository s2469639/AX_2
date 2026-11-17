"""파일 읽기/쓰기 담당. 기록은 덧붙이기만 하고 지우거나 덮어쓰지 않아요."""
import csv
from pathlib import Path

FIELDS = ["date", "text", "mood"]
DEFAULT_PATH = Path(__file__).parent / "data" / "entries.csv"


class StorageError(Exception):
    """사용자에게 그대로 보여 줘도 되는 한국어 메시지를 담아요."""


def read_entries(path: Path = DEFAULT_PATH) -> list:
    """기록을 읽어요. 파일이 없거나 제목 줄만 있으면 빈 목록이에요."""
    path = Path(path)
    if not path.exists():
        return []
    try:
        with path.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except (UnicodeDecodeError, csv.Error, OSError):
        raise StorageError(
            "기록 파일을 읽지 못했어요. data/entries.csv 파일이 열려 있거나 "
            "망가졌는지 확인해 주세요. 파일은 건드리지 않았어요."
        )
    return [
        {"date": r.get("date") or "", "text": r.get("text") or "", "mood": r.get("mood") or ""}
        for r in rows
    ]


def append_entry(entry: dict, path: Path = DEFAULT_PATH) -> None:
    """기록 한 줄을 파일 맨 아래에 덧붙여요. 기존 내용은 그대로 둬요."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        is_new = (not path.exists()) or path.stat().st_size == 0
        needs_newline = False
        if not is_new:
            with path.open("rb") as f:
                f.seek(-1, 2)
                needs_newline = f.read(1) not in (b"\n", b"\r")
        with path.open("a", newline="", encoding="utf-8") as f:
            if needs_newline:
                f.write("\r\n")
            w = csv.writer(f)
            if is_new:
                w.writerow(FIELDS)
            w.writerow([entry["date"], entry["text"], entry["mood"]])
    except OSError:
        raise StorageError(
            "기록을 저장하지 못했어요. data/entries.csv 파일이 다른 프로그램에서 "
            "열려 있다면 닫고 다시 저장해 주세요. 쓴 글은 화면에 그대로 남아 있어요."
        )

"""검색어를 넣어 둔 채 저장해도 방금 쓴 글이 목록에 보이는지 검사.
프로젝트를 임시 폴더로 복사해서 거기서만 실행하므로 진짜 data/entries.csv는 건드리지 않아요."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

SCRIPT = r"""
import sys
sys.stdout.reconfigure(encoding="utf-8")  # 한글 윈도우 기본(cp949)에서도 이모지를 출력할 수 있게
import json
from streamlit.testing.v1 import AppTest
at = AppTest.from_file("app.py", default_timeout=30).run()
at.text_input(key="search_0").set_value("면접").run()
at.text_input(key="line_0").set_value("오늘 산책 다녀옴")
at.radio(key="mood_0").set_value("🙂")
at.button[0].click().run()
print(json.dumps({
    "exceptions": len(at.exception),
    "search_value": at.text_input(key="search_1").value,
    "markdown": [m.value for m in at.markdown],
    "success": [s.value for s in at.success],
}, ensure_ascii=False))
"""


def test_검색어가_있어도_저장하면_검색칸이_비고_새_글이_보인다(tmp_path):
    for name in ["app.py", "logic.py", "storage.py"]:
        shutil.copy(ROOT / name, tmp_path / name)
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "entries.csv").write_text(
        "date,text,mood\n2026-10-29,영어 면접 질문 읽음,\n2026-11-05,모의 면접에서 말이 빨랐다,😢\n2026-11-08,운동 30분,🙂\n",
        encoding="utf-8",
    )
    r = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=120,
        env={**os.environ, "PYTHONUTF8": "1"},
    )
    assert r.returncode == 0, r.stderr[-500:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["exceptions"] == 0
    assert out["search_value"] == ""
    assert any("오늘 산책 다녀옴" in m for m in out["markdown"])
    assert out["success"] == ["저장했어요!"]
    # 진짜 기록 파일이 아니라 임시 폴더의 파일에만 저장됐는지
    assert "오늘 산책 다녀옴" in (tmp_path / "data" / "entries.csv").read_text(encoding="utf-8")

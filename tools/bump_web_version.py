# tools/bump_web_version.py
# ------------------------------------------------------------
# 웹뷰어 버전만 간단히 올리는 도구
#
# 사용 예:
#   python tools\bump_web_version.py 2.1.1 "웹뷰어 버튼 정렬 수정"
#
# 인자를 생략하면 현재 web_version의 patch 번호를 1 올립니다.
#   python tools\bump_web_version.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
VERSION_JSON = ROOT / "data" / "version.json"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TODAY = datetime.now().strftime("%Y-%m-%d")


def backup(path: Path):
    if path.exists():
        b = path.with_name(f"{path.stem}_before_web_bump_{STAMP}{path.suffix}")
        b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        print(f"[백업] {b}")


def bump_patch(version: str):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", str(version).strip())
    if not m:
        return "2.1.1"
    major, minor, patch = map(int, m.groups())
    return f"{major}.{minor}.{patch + 1}"


def main():
    data = {}
    if VERSION_JSON.exists():
        backup(VERSION_JSON)
        try:
            data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    current = str(data.get("web_version") or data.get("app_version") or data.get("version") or "2.1.0")

    if len(sys.argv) >= 2:
        new_version = sys.argv[1].strip()
    else:
        new_version = bump_patch(current)

    note = " ".join(sys.argv[2:]).strip() if len(sys.argv) >= 3 else ""

    data["web_version"] = new_version
    data["latest_web_version"] = new_version
    data["web_release_date"] = TODAY
    data["web_updated_at"] = datetime.now().isoformat(timespec="seconds")
    data["web_release_title"] = note or f"웹뷰어 v{new_version}"

    notes = data.get("web_notes")
    if not isinstance(notes, list):
        notes = []
    if note:
        notes.insert(0, note)
    data["web_notes"] = notes[:20]

    VERSION_JSON.parent.mkdir(parents=True, exist_ok=True)
    VERSION_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("[완료] 웹뷰어 버전 갱신")
    print(f"- 이전 web_version: {current}")
    print(f"- 새 web_version: {new_version}")
    if note:
        print(f"- 메모: {note}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")


if __name__ == "__main__":
    main()

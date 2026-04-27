# tools/step57_web_version_management.py
# ------------------------------------------------------------
# Step57: 웹뷰어 버전 관리 체계 추가
#
# 목적:
# 1) data/version.json에 web_version 관련 키 추가
# 2) mobile/app.py가 version.json을 읽어 웹뷰어 버전을 화면에 표시
# 3) 이후 웹뷰어 버전만 쉽게 올릴 수 있는 tools/bump_web_version.py 생성
#
# 기본 적용 버전:
#   web_version = 2.1.0
#
# 실행:
#   python tools\step57_web_version_management.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TODAY = datetime.now().strftime("%Y-%m-%d")

WEB_VERSION = "2.1.0"
WEB_RELEASE_TITLE = "웹뷰어 UI 안정화 버전"

VERSION_JSON = ROOT / "data" / "version.json"
MOBILE_APP = ROOT / "mobile" / "app.py"
BUMP_WEB_TOOL = ROOT / "tools" / "bump_web_version.py"

HELPER_START = "# [WEB_VERSION_MANAGEMENT_START]"
HELPER_END = "# [WEB_VERSION_MANAGEMENT_END]"
CALL_START = "# [WEB_VERSION_BADGE_CALL_START]"
CALL_END = "# [WEB_VERSION_BADGE_CALL_END]"

WEB_VERSION_HELPER = r'''
# [WEB_VERSION_MANAGEMENT_START]
def load_web_version_info():
    """data/version.json에서 웹뷰어 버전 정보를 안전하게 읽는다."""
    try:
        import json
        from pathlib import Path
        version_path = Path(__file__).resolve().parent.parent / "data" / "version.json"

        data = {}
        if version_path.exists():
            data = json.loads(version_path.read_text(encoding="utf-8"))

        web_version = str(
            data.get("web_version")
            or data.get("app_version")
            or data.get("version")
            or "2.1.0"
        )

        app_version = str(
            data.get("app_version")
            or data.get("version")
            or web_version
        )

        data_version = str(
            data.get("data_version")
            or data.get("db_version")
            or app_version
        )

        release_date = str(
            data.get("web_release_date")
            or data.get("release_date")
            or ""
        )

        release_title = str(
            data.get("web_release_title")
            or data.get("release_title")
            or "웹뷰어"
        )

        return {
            "web_version": web_version,
            "app_version": app_version,
            "data_version": data_version,
            "release_date": release_date,
            "release_title": release_title,
        }
    except Exception:
        return {
            "web_version": "2.1.0",
            "app_version": "2.1.0",
            "data_version": "2.1.0",
            "release_date": "",
            "release_title": "웹뷰어",
        }


def render_web_version_badge():
    """웹뷰어 상단에 작고 방해되지 않는 버전 배지를 표시한다."""
    try:
        import html
        info = load_web_version_info()
        web_version = html.escape(info.get("web_version", ""))
        data_version = html.escape(info.get("data_version", ""))
        release_date = html.escape(info.get("release_date", ""))

        detail = f"Web v{web_version}"
        if data_version and data_version != web_version:
            detail += f" · Data v{data_version}"
        if release_date:
            detail += f" · {release_date}"

        st.markdown(
            f"""
            <style>
            .mh-web-version-badge {{
                display: flex;
                justify-content: flex-end;
                align-items: center;
                margin-top: -0.35rem;
                margin-bottom: 0.45rem;
                color: #64748b;
                font-size: 0.78rem;
                line-height: 1.2;
                user-select: none;
            }}
            .mh-web-version-badge span {{
                border: 1px solid rgba(148, 163, 184, 0.45);
                background: rgba(248, 250, 252, 0.72);
                border-radius: 999px;
                padding: 0.16rem 0.5rem;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            }}
            @media (max-width: 640px) {{
                .mh-web-version-badge {{
                    justify-content: flex-start;
                    margin-top: -0.15rem;
                    font-size: 0.72rem;
                }}
            }}
            </style>
            <div class="mh-web-version-badge"><span>{detail}</span></div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass
# [WEB_VERSION_MANAGEMENT_END]
'''

WEB_VERSION_CALL = r'''
# [WEB_VERSION_BADGE_CALL_START]
try:
    render_web_version_badge()
except Exception:
    pass
# [WEB_VERSION_BADGE_CALL_END]
'''

BUMP_WEB_VERSION_TOOL = r'''# tools/bump_web_version.py
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
    data["web_release_date"] = TODAY
    data["web_updated_at"] = datetime.now().isoformat(timespec="seconds")
    data["web_release_title"] = note or f"웹뷰어 v{new_version}"

    notes = data.get("web_notes")
    if not isinstance(notes, list):
        notes = []
    if note:
        notes.insert(0, note)
    data["web_notes"] = notes[:20]
    data["latest_web_version"] = new_version

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
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step57_web_version_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def load_json_safely(path: Path):
    if not path.exists():
        return {}
    try:
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
        return json.loads(raw) if raw else {}
    except Exception as e:
        print("[경고] version.json 파싱 실패. 백업 후 새 구조로 보정합니다.")
        print(e)
        return {}


def update_version_json():
    print("[처리] data/version.json 웹뷰어 버전 키 추가")
    VERSION_JSON.parent.mkdir(parents=True, exist_ok=True)
    if VERSION_JSON.exists():
        backup(VERSION_JSON)

    data = load_json_safely(VERSION_JSON)

    data["web_version"] = WEB_VERSION
    data["web_release_date"] = TODAY
    data["web_updated_at"] = datetime.now().isoformat(timespec="seconds")
    data["web_release_title"] = WEB_RELEASE_TITLE
    data["latest_web_version"] = WEB_VERSION

    notes = data.get("web_notes")
    if not isinstance(notes, list):
        notes = []
    first_note = "웹뷰어 버전 표시 및 관리 체계 추가"
    if first_note not in notes:
        notes.insert(0, first_note)
    data["web_notes"] = notes[:20]

    if "app_version" not in data:
        data["app_version"] = data.get("version", WEB_VERSION)
    if "version" not in data:
        data["version"] = data.get("app_version", WEB_VERSION)

    VERSION_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[완료] web_version = {WEB_VERSION}")


def remove_block(text: str, start_marker: str, end_marker: str):
    start = text.find(start_marker)
    if start == -1:
        return text, False
    end = text.find(end_marker, start)
    if end == -1:
        return text, False
    end_line = text.find("\n", end)
    end_line = len(text) if end_line == -1 else end_line + 1
    return text[:start] + text[end_line:], True


def find_import_insertion_index(lines):
    last_import = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            last_import = i
    return last_import + 1 if last_import >= 0 else 0


def find_badge_call_insertion_index(lines):
    # 1순위: 웹뷰어 제목 바로 아래
    for i, line in enumerate(lines):
        if "시간표 뷰어" in line or "명덕외고 시간표" in line:
            # triple quote 중간으로 보이면 피한다.
            if line.count(chr(34) * 3) % 2 == 0 and line.count(chr(39) * 3) % 2 == 0:
                return i + 1, "header"

    # 2순위: st.set_page_config 완료 직후
    for i, line in enumerate(lines):
        if "st.set_page_config" in line:
            balance = line.count("(") - line.count(")")
            j = i
            while balance > 0 and j + 1 < len(lines):
                j += 1
                balance += lines[j].count("(") - lines[j].count(")")
            return j + 1, "set_page_config"

    # 3순위: import 블록 뒤
    return find_import_insertion_index(lines), "imports"


def patch_mobile_app():
    print("[처리] mobile/app.py 웹버전 표시 패치")
    if not MOBILE_APP.exists():
        raise RuntimeError(f"mobile/app.py 파일이 없습니다: {MOBILE_APP}")

    backup(MOBILE_APP)

    text = MOBILE_APP.read_text(encoding="utf-8", errors="replace")
    original = text

    text, removed_helper = remove_block(text, HELPER_START, HELPER_END)
    text, removed_call = remove_block(text, CALL_START, CALL_END)

    lines = text.splitlines()

    helper_idx = find_import_insertion_index(lines)
    lines.insert(helper_idx, WEB_VERSION_HELPER.strip("\n"))

    text = "\n".join(lines) + "\n"
    lines = text.splitlines()

    call_idx, position = find_badge_call_insertion_index(lines)
    lines.insert(call_idx, WEB_VERSION_CALL.strip("\n"))

    text = "\n".join(lines) + "\n"

    try:
        compile(text, str(MOBILE_APP), "exec")
        print("[확인] mobile/app.py 문법 OK")
    except Exception as e:
        print("[경고] mobile/app.py 문법 확인 실패")
        print(e)
        print("패치를 저장하지 않습니다.")
        raise

    if text != original:
        MOBILE_APP.write_text(text, encoding="utf-8")
        print(f"[완료] mobile/app.py 웹버전 배지 삽입 위치: {position}")
    else:
        print("[안내] mobile/app.py 변경 없음")

    return {
        "removed_helper": removed_helper,
        "removed_call": removed_call,
        "position": position,
    }


def create_bump_tool():
    print("[처리] tools/bump_web_version.py 생성")
    BUMP_WEB_TOOL.parent.mkdir(parents=True, exist_ok=True)
    if BUMP_WEB_TOOL.exists():
        backup(BUMP_WEB_TOOL)
    BUMP_WEB_TOOL.write_text(BUMP_WEB_VERSION_TOOL, encoding="utf-8")
    try:
        compile(BUMP_WEB_VERSION_TOOL, str(BUMP_WEB_TOOL), "exec")
        print("[확인] bump_web_version.py 문법 OK")
    except Exception as e:
        print("[경고] bump_web_version.py 문법 확인 실패")
        print(e)
        raise
    print(f"[완료] {BUMP_WEB_TOOL}")


def main():
    print("==============================================")
    print("Step57 web version management")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print(f"[WEB_VERSION] {WEB_VERSION}")
    print()

    try:
        update_version_json()
        info = patch_mobile_app()
        create_bump_tool()
    except Exception as e:
        print("[오류] Step57 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    print()
    print("[완료] 웹뷰어 버전 관리 체계 추가")
    print(f"- web_version: {WEB_VERSION}")
    print(f"- mobile/app.py 배지 위치: {info.get('position')}")
    print("- tools/bump_web_version.py 생성")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 웹뷰어 화면 상단 또는 제목 근처에 Web v2.1.0 배지가 보이는지")
    print("2. 화면 레이아웃이 깨지지 않는지")
    print("3. 기존 웹뷰어 기능이 정상인지")
    print()
    print("다음부터 웹뷰어 버전만 올릴 때:")
    print('python tools\\bump_web_version.py 2.1.1 "웹뷰어 수정 내용"')
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

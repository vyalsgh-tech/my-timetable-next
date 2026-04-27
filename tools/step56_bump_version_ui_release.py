# tools/step56_bump_version_ui_release.py
# ------------------------------------------------------------
# Step56: UI 안정 버전 배포 전 버전 정보 갱신
#
# 목적:
# - Step47~Step54 UI/메모/달력 개선 내용을 반영하여 버전을 v2.1.0으로 갱신
# - data/version.json 백업 후 안전하게 갱신
# - RELEASE_NOTES.txt에 v2.1.0 변경 내역 추가/갱신
# - desktop/timetable.pyw 안에 남아 있는 일부 하드코딩 버전 표기도 가능한 범위에서 갱신
#
# 실행:
#   python tools\step56_bump_version_ui_release.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TODAY = datetime.now().strftime("%Y-%m-%d")

NEW_VERSION = "2.1.0"
RELEASE_TITLE = "v2.1.0 UI 안정화 업데이트"

VERSION_JSON = ROOT / "data" / "version.json"
DESKTOP = ROOT / "desktop" / "timetable.pyw"
RELEASE_NOTES = ROOT / "RELEASE_NOTES.txt"

RELEASE_NOTE_BLOCK = f"""# {RELEASE_TITLE}
Release date: {TODAY}

## 주요 변경
- 하단 우측 현재시각 표시 추가
- 교시/시간대 전환 시 현재시각 강조 표시 추가
- 러블리 핑크 테마 추가
- 상단 툴바 hover 음영 개선
- undo / redo 아이콘 개선
- 저장 버튼은 안정성을 위해 기존 '저장' 글자 버튼으로 복원
- 메모 줄바꿈 입력/수정 UI 안정화
- 메모 선택, 우클릭 메뉴, 글자색, 하이라이트 동작 안정화
- 메모 하단부 클릭 시 스크롤 상단 이동 현상 완화
- 하이라이트가 빈 줄/공백에 번지는 현상 보정
- 달력 월 이동 시 아래에서부터 물결치듯 다시 그려지는 현상 완화
- 창 이동 시 떨림 완화

## 확인 필요
- PC 앱 실행 후 프로그램 정보의 버전이 {NEW_VERSION}인지 확인
- 메모 입력/수정/삭제/완료/중요/색상/하이라이트 확인
- 달력 월 이동 확인
- 설치파일 빌드 후 설치 테스트
"""


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step56_version_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def load_json_safely(path: Path):
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8", errors="replace").strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except Exception as e:
        print("[경고] version.json 파싱 실패. 기존 파일은 백업하고 새 구조로 재작성합니다.")
        print(e)
        return {}


def update_version_json():
    print("[처리] data/version.json 갱신")
    VERSION_JSON.parent.mkdir(parents=True, exist_ok=True)

    if VERSION_JSON.exists():
        backup(VERSION_JSON)

    data = load_json_safely(VERSION_JSON)

    # 기존 구조를 최대한 보존하면서 흔히 쓰는 키들을 모두 갱신
    data["app_version"] = NEW_VERSION
    data["desktop_version"] = NEW_VERSION
    data["version"] = NEW_VERSION
    data["release_date"] = TODAY
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    data["release_title"] = RELEASE_TITLE

    # 데이터 구조 버전은 앱 버전과 분리되어 있을 수 있으므로 기존 값이 있으면 보존.
    if "data_version" not in data:
        data["data_version"] = NEW_VERSION

    # 업데이트 안내용 키
    data["latest_version"] = NEW_VERSION
    data["minimum_supported_version"] = data.get("minimum_supported_version", "2.0.0")
    data["notes"] = [
        "UI 안정화",
        "메모 선택/우클릭/하이라이트 안정화",
        "달력 월 이동 렌더링 개선",
        "하단 현재시각 표시",
        "러블리 핑크 테마 추가",
    ]

    VERSION_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"[완료] version.json -> {NEW_VERSION}")


def update_release_notes():
    print("[처리] RELEASE_NOTES.txt 갱신")
    old = ""
    if RELEASE_NOTES.exists():
        backup(RELEASE_NOTES)
        old = RELEASE_NOTES.read_text(encoding="utf-8", errors="replace")

    # 같은 버전 블록이 이미 있으면 중복 추가하지 않고 맨 위 블록만 교체
    pattern = re.compile(rf"# v{re.escape(NEW_VERSION)}.*?(?=\n# v|\Z)", re.DOTALL)
    if pattern.search(old):
        new_text = pattern.sub(RELEASE_NOTE_BLOCK.strip() + "\n", old, count=1)
    else:
        new_text = RELEASE_NOTE_BLOCK.strip() + "\n\n" + old.lstrip()

    RELEASE_NOTES.write_text(new_text, encoding="utf-8")
    print("[완료] RELEASE_NOTES.txt 갱신")


def update_desktop_hardcoded_versions():
    if not DESKTOP.exists():
        print("[건너뜀] desktop/timetable.pyw 없음")
        return 0

    print("[처리] desktop/timetable.pyw 하드코딩 버전 표기 보정")
    backup(DESKTOP)

    text = DESKTOP.read_text(encoding="utf-8", errors="replace")
    original = text
    changed = 0

    replacements = [
        # APP_VERSION = "2.0.1" 형태
        (r'(APP_VERSION\s*=\s*[\'"])[0-9]+\.[0-9]+\.[0-9]+([\'"])', rf'\g<1>{NEW_VERSION}\2'),
        (r'(DESKTOP_VERSION\s*=\s*[\'"])[0-9]+\.[0-9]+\.[0-9]+([\'"])', rf'\g<1>{NEW_VERSION}\2'),
        (r'(app_version\s*=\s*[\'"])[0-9]+\.[0-9]+\.[0-9]+([\'"])', rf'\g<1>{NEW_VERSION}\2'),
        (r'(desktop_version\s*=\s*[\'"])[0-9]+\.[0-9]+\.[0-9]+([\'"])', rf'\g<1>{NEW_VERSION}\2'),
        # 화면 문구 v2.0.1 형태
        (r'(명덕외고\s+교사\s+시간표\s+v)[0-9]+\.[0-9]+\.[0-9]+', rf'\g<1>{NEW_VERSION}'),
        (r'(명덕외고\s+시간표\s+v)[0-9]+\.[0-9]+\.[0-9]+', rf'\g<1>{NEW_VERSION}'),
    ]

    for pat, repl in replacements:
        new_text, n = re.subn(pat, repl, text)
        if n:
            text = new_text
            changed += n

    try:
        compile(text, str(DESKTOP), "exec")
        print("[확인] desktop/timetable.pyw 문법 OK")
    except Exception as e:
        print("[경고] desktop/timetable.pyw 문법 확인 실패")
        print(e)
        print("하드코딩 버전 보정은 저장하지 않습니다.")
        return 0

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print(f"[완료] desktop/timetable.pyw 버전 표기 보정: {changed}곳")
    else:
        print("[안내] desktop/timetable.pyw에서 교체할 하드코딩 버전 없음")

    return changed


def main():
    print("==============================================")
    print("Step56 bump version for UI release")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print(f"[NEW_VERSION] {NEW_VERSION}")
    print()

    try:
        update_version_json()
        update_release_notes()
        desktop_changes = update_desktop_hardcoded_versions()
    except Exception as e:
        print("[오류] 버전 갱신 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    print()
    print("[완료] Step56 버전 정보 갱신 완료")
    print(f"- 새 버전: {NEW_VERSION}")
    print(f"- desktop 하드코딩 보정: {desktop_changes}곳")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print(f"1. 프로그램 정보에서 버전이 {NEW_VERSION}으로 보이는지")
    print("2. 앱 실행/메모/달력 기능이 정상인지")
    print()
    print("다음 단계:")
    print("build\\build_pc_release.bat")
    print("python tools\\make_release_package.py")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

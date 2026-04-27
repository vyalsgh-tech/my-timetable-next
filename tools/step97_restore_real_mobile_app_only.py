# step97_restore_real_mobile_app_only.py
# 목적: Step96이 tools\stepXX_*.py 같은 '패치 스크립트'를 mobile/app.py로 잘못 복원한 경우,
#       실제 mobile/app.py 백업만 골라서 다시 복구합니다.
# 원칙: UI 패치 없음. DOM/CSS/JS 삽입 없음. 실제 앱 파일 복원만 수행.

from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step97_restore_backups"
REPORT = ROOT / "tools" / "step97_restore_real_mobile_app_report.txt"

# 실제 app.py 백업으로 볼 수 있는 파일명만 허용합니다.
ALLOWED_NAME_PREFIXES = (
    "app_before",
    "app_current_before",
    "app_broken_before",
    "app_corrupt_before",
)

# 이 이름들은 대부분 패치 도구/복구 도구이므로 app.py 후보에서 제외합니다.
EXCLUDE_NAME_PREFIXES = (
    "step",
    "run_",
)

BAD_TEXT_MARKERS = [
    "step96_emergency_restore",
    "Step96 Emergency Restore",
    "step95_repair_app_after_step94",
    "step94_web_viewer_header_theme_refine",
    "step93_web_viewer_precision_ui_patch",
    "step92_web_viewer_ui_theme_clock_patch",
    "step91_web_viewer_force_layout_theme_patch",
    "step90_web_viewer_layout_theme_patch",
    "CURRENT_BACKUP",
    "Candidates:",
    "CHOSEN:",
]

GOOD_TEXT_MARKERS = [
    "import streamlit as st",
    "st.set_page_config",
    "st.session_state",
    "st.markdown",
    "st.button",
    "st.selectbox",
    "시간표",
    "명덕외고",
]


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as e:
        return False, repr(e)


def is_allowed_candidate(path: Path) -> bool:
    name = path.name
    lower = name.lower()
    if not lower.endswith(".py"):
        return False
    if lower.startswith(EXCLUDE_NAME_PREFIXES):
        return False
    if not lower.startswith(ALLOWED_NAME_PREFIXES):
        return False
    if "__pycache__" in str(path).lower():
        return False
    try:
        if APP.exists() and path.resolve() == APP.resolve():
            return False
    except Exception:
        pass
    return True


def collect_candidates() -> list[Path]:
    found: list[Path] = []

    # 1순위: mobile 폴더 안의 app_before 백업
    found.extend((ROOT / "mobile").glob("app_before*.py"))
    found.extend((ROOT / "mobile").glob("app_current_before*.py"))

    # 2순위: tools\_stepXX_backups 안의 실제 app 백업
    tools = ROOT / "tools"
    if tools.exists():
        for d in tools.glob("_step*_backups"):
            if d.is_dir():
                found.extend(d.glob("app_before*.py"))
                found.extend(d.glob("app_current_before*.py"))
                found.extend(d.glob("app_broken_before*.py"))
                found.extend(d.glob("app_corrupt_before*.py"))

    # 중복 제거
    unique: list[Path] = []
    seen = set()
    for p in found:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp in seen:
            continue
        seen.add(rp)
        if p.exists() and p.is_file() and is_allowed_candidate(p):
            unique.append(p)
    return unique


def score_candidate(path: Path) -> dict:
    text = read_text(path)
    ok, err = compile_ok(path)
    score = 0

    if ok:
        score += 300
    else:
        score -= 10000

    # 실제 앱일 가능성이 높은 기본 조건
    for marker in GOOD_TEXT_MARKERS:
        if marker in text:
            score += 35

    # 패치 도구/리포트로 보이는 텍스트는 강한 감점
    for marker in BAD_TEXT_MARKERS:
        if marker in text:
            score -= 300

    lower_path = str(path).lower()
    lower_name = path.name.lower()

    # mobile 폴더 백업 우선
    if "\\mobile\\" in lower_path or "/mobile/" in lower_path:
        score += 250

    # tools 아래 백업 폴더는 허용하되 직접 tools\stepXX.py는 이미 제외됨
    if "_step" in lower_path and "_backups" in lower_path:
        score += 60

    # 현재 깨진 파일 백업류는 조금 낮춤
    if lower_name.startswith("app_broken") or lower_name.startswith("app_corrupt"):
        score -= 80

    # 너무 작은 파일은 실제 앱일 가능성 낮음
    size = path.stat().st_size
    if 10000 <= size <= 250000:
        score += 100
    elif size < 5000:
        score -= 300

    # Streamlit 호출 빈도
    st_count = text.count("st.")
    score += min(st_count, 80)

    # patch script 성격이면 감점
    patch_words = sum(text.lower().count(w) for w in ["patch", "restore", "backup_dir", "candidate", "shutil.copy2"])
    score -= min(patch_words * 10, 250)

    # 수정시간 최신성 약간 반영
    try:
        score += int(path.stat().st_mtime // 3600) % 50
    except Exception:
        pass

    return {
        "path": path,
        "score": score,
        "compile": ok,
        "error": err,
        "size": size,
        "st_count": st_count,
    }


def write_report(lines: list[str]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    lines: list[str] = []
    def log(msg: str):
        print(msg, flush=True)
        lines.append(msg)

    log("============================================================")
    log("Step97 실제 mobile/app.py 백업 전용 복원 시작")
    log(f"프로젝트 루트: {ROOT}")
    log(f"대상 app.py: {APP}")
    log("============================================================")

    if not APP.parent.exists():
        log("[오류] mobile 폴더가 없습니다.")
        write_report(lines)
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup = BACKUP_DIR / f"app_current_before_step97_{ts}.py"
    if APP.exists():
        shutil.copy2(APP, current_backup)
        log(f"[현재 파일 백업] {current_backup}")
    else:
        log("[주의] 현재 mobile/app.py가 없습니다. 백업 없이 복원합니다.")

    candidates = collect_candidates()
    ranked = [score_candidate(p) for p in candidates]
    ranked.sort(key=lambda x: x["score"], reverse=True)

    log("")
    log("[후보 목록: 실제 app 백업명만 검색]")
    if not ranked:
        log("후보가 없습니다.")
    for i, c in enumerate(ranked[:50], 1):
        log(f"{i:02d}. score={c['score']} compile={c['compile']} size={c['size']} st={c['st_count']} path={c['path']}")
        if not c["compile"]:
            log(f"    error={c['error']}")

    chosen = None
    for c in ranked:
        if not c["compile"]:
            continue
        text = read_text(c["path"])
        # 최소 앱 조건
        if "import streamlit" not in text and "streamlit as st" not in text:
            continue
        if "st.set_page_config" not in text:
            continue
        if c["st_count"] < 5:
            continue
        chosen = c
        break

    if chosen is None:
        log("")
        log("[실패] 문법 정상인 실제 app.py 백업을 찾지 못했습니다.")
        log(f"리포트: {REPORT}")
        write_report(lines)
        return 1

    log("")
    log(f"[선택] {chosen['path']}")

    # 복원
    shutil.copy2(chosen["path"], APP)
    ok, err = compile_ok(APP)
    if not ok:
        log(f"[실패] 복원 후 app.py 문법 오류: {err}")
        if current_backup.exists():
            shutil.copy2(current_backup, APP)
            log("[되돌림] 복원 전 파일로 되돌렸습니다.")
        write_report(lines)
        return 1

    log("[성공] 실제 app.py 백업 복원 완료")
    log("다음 실행:")
    log("python -m streamlit run mobile\\app.py")
    write_report(lines)
    return 0


if __name__ == "__main__":
    sys.exit(main())

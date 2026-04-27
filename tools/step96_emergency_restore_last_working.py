# -*- coding: utf-8 -*-
"""
Step96 Emergency Restore - 웹뷰어 앱이 아예 열리지 않을 때 마지막 정상 app.py 복원

사용 위치:
Y:\0_2026\시간표앱_차세대\my-timetable-next\tools\step96_emergency_restore_last_working.py

실행:
cd /d Y:\0_2026\시간표앱_차세대\my-timetable-next
python tools\step96_emergency_restore_last_working.py
python -m streamlit run mobile\app.py

특징:
- 현재 mobile/app.py를 먼저 백업합니다.
- tools/_stepXX 백업 폴더와 프로젝트 안의 app 백업 파일을 검색합니다.
- 문법이 정상이고 Streamlit 앱 형태인 후보 중 가장 안전한 파일을 mobile/app.py로 복원합니다.
- Step90~95 보정 흔적이 적은 파일을 우선합니다.
- app.py 내용을 억지로 정리/수정하지 않고 "복사 복원"만 합니다.
"""

from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import sys
import json

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step96_emergency_backups"
REPORT = ROOT / "tools" / "step96_emergency_restore_report.txt"

GOOD_MARKERS = [
    "import streamlit as st",
    "st.set_page_config",
    "streamlit",
    "명덕외고",
    "시간표",
    "mobile",
    "memo",
    "메모",
    "조회",
]

BAD_MARKERS = [
    "STEP90",
    "Step90",
    "STEP91",
    "Step91",
    "STEP92",
    "Step92",
    "STEP93",
    "Step93",
    "STEP94",
    "Step94",
    "STEP95",
    "Step95",
    "step92-current-time-badge",
    "step92ClockTimer",
    "const slots =",
    "currentLabel(m)",
    "MutationObserver",
    "setInterval",
    "window.parent",
    "scrollTo(0, 0)",
    "components.html",
    "st.components.v1.html",
    "Unexpected indent",
]

# 이 이름들은 도구 파일이므로 후보에서 제외
EXCLUDE_NAME_PARTS = [
    "step89_home_hard_restore_clean_safe.py",
    "step90_web_viewer_layout_theme_patch.py",
    "step91_web_viewer_force_layout_theme_patch.py",
    "step92_web_viewer_ui_theme_clock_patch.py",
    "step93_web_viewer_precision_ui_patch.py",
    "step94_web_viewer_header_theme_refine.py",
    "step95_repair_app_after_step94.py",
    "step95b_safe_verify_repair.py",
    "step96_emergency_restore_last_working.py",
]


def log(msg: str) -> None:
    print(msg, flush=True)


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors="ignore")


def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def looks_like_app(text: str) -> bool:
    return ("streamlit" in text.lower()) and ("st." in text)


def bad_score(text: str) -> int:
    score = 0
    for m in BAD_MARKERS:
        score += text.count(m) * 20
    return score


def good_score(text: str) -> int:
    score = 0
    for m in GOOD_MARKERS:
        if m in text:
            score += 10
    # 너무 짧은 파일은 앱 본문이 아닐 가능성이 큼
    length = len(text)
    if length > 20000:
        score += 50
    elif length > 10000:
        score += 25
    elif length < 3000:
        score -= 80
    return score


def is_excluded(path: Path) -> bool:
    lower = str(path).replace("\\", "/").lower()
    if "__pycache__" in lower:
        return True
    if "/.git/" in lower:
        return True
    name = path.name.lower()
    for part in EXCLUDE_NAME_PARTS:
        if part.lower() in name:
            return True
    return False


def find_candidates():
    patterns = [
        "tools/_step*_backups/*.py",
        "tools/_step*backups/*.py",
        "tools/**/*.py",
        "**/app_before*.py",
        "**/*app_before*.py",
        "**/*backup*app*.py",
        "**/app_backup*.py",
        "**/app.py.bak",
        "**/app*.bak",
    ]

    found = []
    for pat in patterns:
        try:
            found.extend(ROOT.glob(pat))
        except Exception:
            pass

    # 현재 app.py도 후보로 평가하되, 복원 대상에서는 후순위
    if APP.exists():
        found.append(APP)

    unique = []
    seen = set()
    for p in found:
        try:
            rp = p.resolve()
        except Exception:
            rp = p
        if rp in seen:
            continue
        seen.add(rp)
        if not p.exists() or not p.is_file():
            continue
        if is_excluded(p):
            continue
        unique.append(p)

    candidates = []
    for p in unique:
        text = read_text(p)
        if not looks_like_app(text):
            continue
        ok, err = compile_ok(p)
        if not ok:
            continue

        b = bad_score(text)
        g = good_score(text)

        # 현재 파일은 앱이 빈 화면일 수 있으므로 감점
        current_penalty = 80 if p.resolve() == APP.resolve() else 0

        # step89 또는 step90 이전 백업은 상대적으로 안정 후보
        path_text = str(p).replace("\\", "/").lower()
        stable_bonus = 0
        if "_step89" in path_text:
            stable_bonus += 120
        if "_step90" in path_text:
            stable_bonus += 60
        if "_step91" in path_text:
            stable_bonus += 30
        if "_step94" in path_text or "_step95" in path_text:
            stable_bonus -= 40

        # 최종 점수
        score = g - b - current_penalty + stable_bonus

        candidates.append({
            "path": str(p),
            "score": score,
            "good": g,
            "bad": b,
            "size": p.stat().st_size,
            "mtime": p.stat().st_mtime,
            "is_current": p.resolve() == APP.resolve(),
        })

    candidates.sort(key=lambda x: (x["score"], x["mtime"]), reverse=True)
    return candidates


def main() -> int:
    log("============================================================")
    log("Step96 Emergency Restore 시작")
    log(f"프로젝트 루트: {ROOT}")
    log(f"대상 파일: {APP}")
    log("============================================================")

    if not APP.exists():
        log("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        log("현재 위치가 프로젝트 루트인지 확인하세요.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    current_backup = BACKUP_DIR / f"app_current_before_step96_{ts}.py"
    shutil.copy2(APP, current_backup)
    log(f"[현재 app.py 백업 완료] {current_backup}")

    candidates = find_candidates()

    report_lines = []
    report_lines.append("Step96 Emergency Restore Report")
    report_lines.append(f"ROOT: {ROOT}")
    report_lines.append(f"APP: {APP}")
    report_lines.append(f"CURRENT_BACKUP: {current_backup}")
    report_lines.append("")
    report_lines.append("Candidates:")
    for i, c in enumerate(candidates[:30], 1):
        report_lines.append(
            f"{i:02d}. score={c['score']} good={c['good']} bad={c['bad']} "
            f"size={c['size']} current={c['is_current']} path={c['path']}"
        )

    if not candidates:
        REPORT.write_text("\n".join(report_lines), encoding="utf-8")
        log("[실패] 문법 정상인 Streamlit app.py 후보를 찾지 못했습니다.")
        log(f"[보고서] {REPORT}")
        return 1

    # 현재 app.py가 1위라도, 빈 화면 문제가 있으므로 가능하면 다른 후보 선택
    chosen = None
    for c in candidates:
        if not c["is_current"]:
            chosen = c
            break
    if chosen is None:
        chosen = candidates[0]

    chosen_path = Path(chosen["path"])
    log("------------------------------------------------------------")
    log("[선택된 복원 후보]")
    log(f"점수: {chosen['score']}")
    log(f"파일: {chosen_path}")
    log("------------------------------------------------------------")

    shutil.copy2(chosen_path, APP)

    ok, err = compile_ok(APP)
    if not ok:
        # 복원 실패 시 현재 백업으로 되돌림
        shutil.copy2(current_backup, APP)
        report_lines.append("")
        report_lines.append(f"RESTORE_FAILED: {err}")
        REPORT.write_text("\n".join(report_lines), encoding="utf-8")
        log("[실패] 선택 후보를 복원했지만 mobile/app.py 문법검사에 실패했습니다.")
        log(f"[복구] 원래 app.py로 되돌렸습니다: {current_backup}")
        log(f"[보고서] {REPORT}")
        return 1

    report_lines.append("")
    report_lines.append(f"CHOSEN: {chosen_path}")
    report_lines.append("RESULT: SUCCESS")
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    log("[복원 완료] mobile/app.py를 마지막 정상 후보로 복원했습니다.")
    log(f"[보고서] {REPORT}")
    log("")
    log("이제 아래 명령으로 실행하세요:")
    log("python -m streamlit run mobile\\app.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
Step95 - Repair mobile/app.py after failed Step94

목적
- Step94 실행 후 mobile/app.py 에 SyntaxError가 남아 Streamlit이 실행되지 않는 상태를 복구합니다.
- 우선 tools/_step*_backups 안에서 '문법이 정상인 app.py 백업'을 찾아 복원합니다.
- 복원 후보가 없으면 현재 app.py에서 Step90~94 보정 블록을 최대한 제거한 뒤 문법 복구를 시도합니다.
- UI 기능 추가가 아니라 '실행 가능한 상태로 되돌리기'가 최우선입니다.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import py_compile
import shutil
import re
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step95_repair_backups"
REPORT = ROOT / "tools" / "step95_repair_report.txt"

STEP_MARKERS = [
    "STEP90_WEB_VIEWER",
    "STEP91_WEB_VIEWER",
    "STEP92_WEB_VIEWER",
    "STEP93_WEB_VIEWER",
    "STEP94_WEB_VIEWER",
    "Step90",
    "Step91",
    "Step92",
    "Step93",
    "Step94",
]

BLOCK_BEGIN_RE = re.compile(r"^\s*#\s*>>>\s*(STEP9[0-9].*?BEGIN)\s*$", re.I)
BLOCK_END_RE = re.compile(r"^\s*#\s*>>>\s*(STEP9[0-9].*?END)\s*$", re.I)


def log(msg: str) -> None:
    print(msg, flush=True)
    try:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        with REPORT.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return path.read_text(errors="ignore")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def compile_error(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return None
    except py_compile.PyCompileError as e:
        return str(e)
    except Exception as e:
        return repr(e)


def compiles(path: Path) -> bool:
    return compile_error(path) is None


def looks_like_app(text: str) -> bool:
    lowered = text.lower()
    return "streamlit" in lowered and ("st." in text or "import streamlit" in lowered)


def contamination_score(text: str) -> int:
    score = 0
    bad_tokens = [
        "const slots = [",
        "window.step92ClockTimer",
        "step92-current-time-badge",
        "STEP90_WEB_VIEWER",
        "STEP91_WEB_VIEWER",
        "STEP92_WEB_VIEWER",
        "STEP93_WEB_VIEWER",
        "STEP94_WEB_VIEWER",
        "components.html",
        "setInterval(",
        "querySelector",
        "MutationObserver",
    ]
    for token in bad_tokens:
        score += text.count(token) * 10
    return score


def strip_step_blocks(text: str) -> str:
    """Remove previously injected Step90~94 blocks, even if partially malformed."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    skipping = False
    skip_until_end = False

    for line in lines:
        upper = line.upper()
        begin_match = BLOCK_BEGIN_RE.match(line)
        end_match = BLOCK_END_RE.match(line)

        if begin_match and "STEP9" in begin_match.group(1).upper():
            skipping = True
            skip_until_end = True
            continue

        if skipping:
            if end_match:
                skipping = False
                skip_until_end = False
            continue

        # Remove single-line comments/strings that are clearly patch labels.
        if any(marker.upper() in upper for marker in STEP_MARKERS) and ("PATCH" in upper or "WEB_VIEWER" in upper):
            continue

        out.append(line)

    return "\n".join(out).strip() + "\n"


def strip_leaked_js_text(text: str) -> str:
    """Remove JS snippets accidentally rendered/left in Python source if they became bare text."""
    # Remove common leaked snippets from const slots through closing IIFE.
    text = re.sub(
        r"(?ms)^\s*const\s+slots\s*=\s*\[.*?\}\)\(\);\s*$",
        "",
        text,
    )
    # Remove standalone JS function blocks if accidentally pasted as source.
    text = re.sub(r"(?ms)^\s*function\s+currentLabel\s*\(.*?^\s*}\s*$", "", text)
    text = re.sub(r"(?ms)^\s*function\s+update\s*\(.*?^\s*}\s*$", "", text)
    return text


def remove_dangling_try_near_error(text: str, err: str | None) -> str:
    """
    Conservative fallback for 'expected except or finally block'.
    If a lone try: starts a small injected block near the reported line and no except/finally follows
    before dedent, replace that single 'try:' with 'if True:' so the file can parse.
    This is intentionally only a last-resort syntax repair.
    """
    if not err or "expected 'except' or 'finally' block" not in err:
        return text

    line_no = None
    m = re.search(r"line\s+(\d+)", err)
    if m:
        try:
            line_no = int(m.group(1))
        except Exception:
            line_no = None

    lines = text.split("\n")
    candidate_indexes = []

    if line_no:
        start = max(0, line_no - 8)
        end = min(len(lines), line_no + 8)
        for i in range(start, end):
            if re.match(r"^\s*try:\s*$", lines[i]):
                candidate_indexes.append(i)

    if not candidate_indexes:
        for i, line in enumerate(lines[:120]):
            if re.match(r"^\s*try:\s*$", line):
                window = "\n".join(lines[i:i+60])
                if any(marker in window for marker in ("STEP", "Step", "requests.Session", "supabase", "streamlit")):
                    candidate_indexes.append(i)

    for idx in candidate_indexes:
        fixed = lines[:]
        indent = re.match(r"^(\s*)", fixed[idx]).group(1)
        fixed[idx] = indent + "if True:  # Step95 repaired dangling try"
        candidate_text = "\n".join(fixed)
        tmp = BACKUP_DIR / "_step95_try_repair_test.py"
        write_text(tmp, candidate_text)
        if compiles(tmp):
            try:
                tmp.unlink()
            except Exception:
                pass
            return candidate_text

    return text


def normalized_candidate_text(path: Path) -> str | None:
    text = read_text(path)
    if not looks_like_app(text):
        return None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Normalize accidental visible line breaks in labels.
    for src, dst in {
        "달\\n력": "달력",
        "달\n력": "달력",
        "메\\n모": "메모",
        "메\n모": "메모",
        "조\\n회": "조회",
        "조\n회": "조회",
    }.items():
        text = text.replace(src, dst)
    text = strip_step_blocks(text)
    text = strip_leaked_js_text(text)
    return text


def find_backup_candidates() -> list[Path]:
    patterns = [
        "tools/_step*_backups/app_before*.py",
        "tools/_step*_backups/*.py",
        "tools/**/app_before*.py",
        "tools/**/*app*.py",
        "**/app_before*.py",
        "**/*backup*app*.py",
        "**/app.py.bak",
        "**/app*.bak",
    ]
    found: list[Path] = []
    seen: set[Path] = set()
    for pattern in patterns:
        for p in ROOT.glob(pattern):
            try:
                rp = p.resolve()
            except Exception:
                continue
            if rp in seen:
                continue
            seen.add(rp)
            if not p.is_file():
                continue
            if APP.exists():
                try:
                    if rp == APP.resolve():
                        continue
                except Exception:
                    pass
            if "__pycache__" in str(p).lower():
                continue
            found.append(p)

    def key(p: Path):
        text = read_text(p)
        compile_bonus = 10000 if compiles(p) else 0
        app_bonus = 1000 if looks_like_app(text) else 0
        clean_bonus = -contamination_score(text)
        return (compile_bonus + app_bonus + clean_bonus, p.stat().st_mtime)

    found.sort(key=key, reverse=True)
    return found


def test_text_compiles(text: str) -> bool:
    tmp = BACKUP_DIR / "_step95_compile_test.py"
    write_text(tmp, text)
    ok = compiles(tmp)
    try:
        tmp.unlink()
    except Exception:
        pass
    return ok


def restore_best_candidate() -> bool:
    candidates = find_backup_candidates()
    log(f"[검색] 백업 후보 {len(candidates)}개 발견")

    for idx, p in enumerate(candidates[:80], 1):
        raw_text = read_text(p)
        if not looks_like_app(raw_text):
            continue

        raw_ok = compiles(p)
        fixed_text = normalized_candidate_text(p)
        fixed_ok = bool(fixed_text and test_text_compiles(fixed_text))
        score = contamination_score(raw_text)
        log(f"  - 후보 {idx}: {p} | 원본문법={raw_ok} | 정리후문법={fixed_ok} | 오염점수={score}")

        if fixed_ok and fixed_text:
            write_text(APP, fixed_text)
            final_err = compile_error(APP)
            if final_err is None:
                log(f"[복구 성공] 다음 백업을 정리 후 복원했습니다: {p}")
                return True
            else:
                log(f"[경고] 복원 직후에도 문법 오류: {final_err}")

        if raw_ok:
            shutil.copy2(p, APP)
            if compiles(APP):
                log(f"[복구 성공] 다음 백업 원본을 복원했습니다: {p}")
                return True

    return False


def repair_current_file() -> bool:
    if not APP.exists():
        return False

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")
    text = strip_step_blocks(text)
    text = strip_leaked_js_text(text)

    tmp = BACKUP_DIR / "_current_clean_test.py"
    write_text(tmp, text)
    err = compile_error(tmp)
    if err:
        text2 = remove_dangling_try_near_error(text, err)
        write_text(tmp, text2)
        if compiles(tmp):
            write_text(APP, text2)
            log("[복구 성공] 현재 app.py에서 깨진 보정 블록/try 구조를 제거해 복구했습니다.")
            try:
                tmp.unlink()
            except Exception:
                pass
            return True
        log(f"[현재 파일 복구 실패] {err}")
        try:
            tmp.unlink()
        except Exception:
            pass
        return False

    write_text(APP, text)
    log("[복구 성공] 현재 app.py에서 Step90~94 보정 블록을 제거해 복구했습니다.")
    try:
        tmp.unlink()
    except Exception:
        pass
    return True


def main() -> int:
    # reset report
    try:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text("", encoding="utf-8")
    except Exception:
        pass

    log("============================================================")
    log("Step95 app.py 문법 복구 시작")
    log(f"프로젝트 루트: {ROOT}")
    log(f"대상 파일: {APP}")
    log("============================================================")

    if not APP.exists():
        log("[오류] mobile/app.py 파일을 찾지 못했습니다. 프로젝트 루트에서 실행했는지 확인하세요.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_backup = BACKUP_DIR / f"app_broken_before_step95_{ts}.py"
    shutil.copy2(APP, safety_backup)
    log(f"[안전백업] 현재 깨진 app.py 백업 완료: {safety_backup}")

    current_err = compile_error(APP)
    if current_err is None:
        log("[확인] 현재 app.py는 이미 문법상 정상입니다. 이전 Step 보정 블록만 정리합니다.")
        if repair_current_file() and compiles(APP):
            log("[완료] app.py가 실행 가능한 상태입니다.")
            return 0
    else:
        log(f"[현재 오류] {current_err}")

    # 1) Try to restore the cleanest compileable backup first.
    if restore_best_candidate() and compiles(APP):
        log("[완료] 실행 가능한 app.py로 복구되었습니다.")
        log("다음 명령: python -m streamlit run mobile\\app.py")
        return 0

    # 2) If no backup works, repair current file.
    if repair_current_file() and compiles(APP):
        log("[완료] 현재 파일을 직접 수리하여 실행 가능한 상태로 복구했습니다.")
        log("다음 명령: python -m streamlit run mobile\\app.py")
        return 0

    final_err = compile_error(APP)
    log("[실패] 자동 복구에 실패했습니다.")
    log(f"[최종 오류] {final_err}")
    log(f"[보고서] {REPORT}")
    log("이 경우 mobile/app.py 파일과 tools/step95_repair_report.txt를 올려주면 정확히 수리할 수 있습니다.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

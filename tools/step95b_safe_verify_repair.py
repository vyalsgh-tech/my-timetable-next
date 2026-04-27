# step95b_safe_verify_repair.py
# Purpose:
# - Do not break a currently valid mobile/app.py.
# - Verify syntax.
# - If invalid, restore the newest syntactically valid app.py from prior backup folders.
# - If valid, only remove clearly bounded STEP90~STEP94 blocks when removal still compiles.
# - Never overwrite mobile/app.py with a version that fails py_compile.

from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import re
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step95b_safe_backups"
REPORT = ROOT / "tools" / "step95b_safe_verify_repair_report.txt"

STEP_BLOCK_PATTERNS = [
    ("STEP90", r"# >>> STEP90.*?BEGIN.*?# >>> STEP90.*?END"),
    ("STEP91", r"# >>> STEP91.*?BEGIN.*?# >>> STEP91.*?END"),
    ("STEP92", r"# >>> STEP92.*?BEGIN.*?# >>> STEP92.*?END"),
    ("STEP93", r"# >>> STEP93.*?BEGIN.*?# >>> STEP93.*?END"),
    ("STEP94", r"# >>> STEP94.*?BEGIN.*?# >>> STEP94.*?END"),
]

def log(lines, msg):
    print(msg)
    lines.append(msg)

def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors="ignore")

def write_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8", newline="\n")

def compile_file(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, "OK"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def compile_text(text: str):
    tmp = ROOT / "tools" / "_step95b_compile_test.py"
    write_text(tmp, text)
    ok, err = compile_file(tmp)
    try:
        tmp.unlink()
    except Exception:
        pass
    return ok, err

def find_valid_backup():
    search_roots = [
        ROOT / "tools",
        ROOT / "mobile",
        ROOT,
    ]
    candidates = []
    seen = set()
    for base in search_roots:
        if not base.exists():
            continue
        for p in base.rglob("*.py"):
            try:
                rp = p.resolve()
            except Exception:
                continue
            if rp in seen:
                continue
            seen.add(rp)
            if rp == APP.resolve():
                continue
            name = p.name.lower()
            full = str(p).lower()
            if "__pycache__" in full:
                continue
            if not (
                "app_before" in name
                or "app_backup" in name
                or "app_broken" in name
                or name == "app.py"
            ):
                continue
            txt = read_text(p)
            if "streamlit" not in txt:
                continue
            ok, err = compile_file(p)
            if not ok:
                continue
            bad = (
                txt.count("st.components.v1.html")
                + txt.count("setInterval")
                + txt.count("querySelector")
                + txt.count("MutationObserver")
                + txt.count("STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH")
            )
            candidates.append((bad, -p.stat().st_mtime, p))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]

def safe_remove_step_blocks(text: str, lines):
    current = text
    for label, pattern in STEP_BLOCK_PATTERNS:
        if label not in current:
            continue
        candidate = re.sub(pattern, "", current, flags=re.S | re.I)
        if candidate == current:
            log(lines, f"[정보] {label} marker는 보이나 bounded block 형식이 아니어서 건너뜀")
            continue
        ok, err = compile_text(candidate)
        if ok:
            current = candidate
            log(lines, f"[정리 완료] {label} bounded block 제거")
        else:
            log(lines, f"[정리 보류] {label} 제거 시 문법 오류 발생: {err}")
    return current

def main():
    lines = []
    log(lines, "============================================================")
    log(lines, "Step95B 안전 검증/복구 시작")
    log(lines, f"프로젝트 루트: {ROOT}")
    log(lines, f"대상 파일: {APP}")
    log(lines, "============================================================")

    if not APP.exists():
        log(lines, "[오류] mobile/app.py를 찾지 못했습니다.")
        write_text(REPORT, "\n".join(lines))
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step95b_{ts}.py"
    shutil.copy2(APP, backup)
    log(lines, f"[백업 완료] {backup}")

    ok, err = compile_file(APP)
    if not ok:
        log(lines, f"[확인] 현재 app.py 문법 오류: {err}")
        candidate = find_valid_backup()
        if candidate is None:
            log(lines, "[실패] 문법 정상 백업 후보를 찾지 못했습니다.")
            write_text(REPORT, "\n".join(lines))
            return 1
        shutil.copy2(candidate, APP)
        log(lines, f"[복구 완료] 문법 정상 백업 복원: {candidate} -> {APP}")
        ok2, err2 = compile_file(APP)
        if not ok2:
            log(lines, f"[실패] 복원 후에도 문법 오류: {err2}")
            write_text(REPORT, "\n".join(lines))
            return 1
        log(lines, "[확인 완료] 복원된 app.py 문법 정상")
        write_text(REPORT, "\n".join(lines))
        return 0

    log(lines, "[확인] 현재 app.py는 문법 정상입니다.")
    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")
    cleaned = safe_remove_step_blocks(text, lines)
    if cleaned != text:
        ok3, err3 = compile_text(cleaned)
        if ok3:
            write_text(APP, cleaned)
            log(lines, "[저장 완료] 안전하게 정리된 app.py를 저장했습니다.")
        else:
            log(lines, f"[저장 취소] 최종 정리본 문법 오류: {err3}")
            log(lines, "[유지] 기존 app.py를 그대로 유지합니다.")
    else:
        log(lines, "[유지] 제거 가능한 bounded Step 블록이 없어서 app.py를 그대로 유지합니다.")

    ok4, err4 = compile_file(APP)
    if ok4:
        log(lines, "[최종 확인] mobile/app.py 문법 정상")
        log(lines, "다음 실행: python -m streamlit run mobile\\app.py")
        write_text(REPORT, "\n".join(lines))
        return 0

    log(lines, f"[최종 오류] mobile/app.py 문법 오류: {err4}")
    log(lines, "[복원] 실행 전 백업으로 되돌립니다.")
    shutil.copy2(backup, APP)
    write_text(REPORT, "\n".join(lines))
    return 1

if __name__ == "__main__":
    raise SystemExit(main())

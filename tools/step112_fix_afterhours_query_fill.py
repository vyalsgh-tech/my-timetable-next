
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step112_backups"

CSS_BEGIN = "# >>> STEP112_NO_AFTERHOURS_QUERY_FILL_CSS_BEGIN"
CSS_END = "# >>> STEP112_NO_AFTERHOURS_QUERY_FILL_CSS_END"

def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors="ignore")

def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")

def strip_block(text: str, begin: str, end: str) -> str:
    return re.sub(re.escape(begin) + r".*?" + re.escape(end), "", text, flags=re.S)

def compile_ok(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

CSS_BLOCK = "\n".join([
CSS_BEGIN,
"# Step112: 18:00~다음날 05:59에는 조회/교시 강조 채우기 완전 중단",
"try:",
"    _step112_now = datetime.now(kst_tz)",
"except Exception:",
"    _step112_now = datetime.now()",
"_step112_mins = _step112_now.hour * 60 + _step112_now.minute",
"_step112_after_hours = bool(_step112_mins >= 18 * 60 or _step112_mins < 6 * 60)",
"if _step112_after_hours:",
"    st.markdown(",
"        f\"\"\"",
"        <style>",
"        /* Step112: 야간에는 조회행/교시행의 현재교시 색 채우기를 제거 */",
"        table.mobile-table tr:nth-child(3) td:first-child {{",
"            background-color: {t.get('common_per_bg', t.get('per_bg', '#dbeafe'))} !important;",
"            color: {t.get('common_per_fg', t.get('per_fg', '#0f172a'))} !important;",
"        }}",
"        table.mobile-table tr:nth-child(3) td:first-child * {{",
"            background: transparent !important;",
"            background-color: transparent !important;",
"            color: inherit !important;",
"        }}",
"        table.mobile-table tr:nth-child(3) td:not(:first-child) {{",
"            background-color: {t.get('query_cell_bg', t.get('cell_bg', '#ffffff'))} !important;",
"            color: {t.get('query_cell_fg', t.get('cell_fg', '#0f172a'))} !important;",
"        }}",
"        table.mobile-table .hl-fill-yellow,",
"        table.mobile-table .hl-fill-yellow * {{",
"            background-color: inherit !important;",
"            color: inherit !important;",
"        }}",
"        table.mobile-table .hl-border-yellow,",
"        table.mobile-table .hl-border-red {{",
"            outline: none !important;",
"            box-shadow: none !important;",
"        }}",
"        </style>",
"        \"\"\",",
"        unsafe_allow_html=True,",
"    )",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step112 야간 조회칸 색채우기 오류 수정")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step112_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")
    text = strip_block(text, CSS_BEGIN, CSS_END)

    # Step111 교시 계산 블록이 있으면 18시 이후에는 active/preview가 None이 되도록 다시 한번 보정
    text = text.replace(
        "step111_enable_period_highlight = 6 * 60 <= now_mins < 18 * 60",
        "step111_enable_period_highlight = 6 * 60 <= now_mins < 18 * 60",
    )

    # 최종 CSS는 가장 뒤쪽 보정 CSS 뒤에 삽입해야 함.
    insert_markers = [
        "# >>> STEP111_TITLE_DAY_PERIOD_RULES_CSS_END",
        "# >>> STEP110_TITLE_AND_PERIOD_HIGHLIGHT_CSS_END",
        "# >>> STEP109_TITLE_GAP_CSS_END",
        "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END",
    ]
    inserted = False
    for marker in insert_markers:
        if marker in text:
            text = text.replace(marker, marker + "\n" + CSS_BLOCK, 1)
            inserted = True
            print(f"[수정] {marker} 뒤에 Step112 야간 보정 CSS를 추가했습니다.")
            break

    if not inserted:
        if "\ndisplay_dashboard()" in text:
            text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
            print("[주의] CSS를 display_dashboard 호출 직전에 추가했습니다.")
        else:
            text += "\n" + CSS_BLOCK
            print("[주의] CSS 삽입 위치를 찾지 못해 파일 끝에 추가했습니다.")

    tmp = APP.with_suffix(".step112_test.py")
    write_text(tmp, text)
    ok, err = compile_ok(tmp)
    try:
        tmp.unlink(missing_ok=True)
    except Exception:
        pass

    if not ok:
        shutil.copy2(backup, APP)
        print("[오류] 패치 후 문법검사 실패. 백업으로 복원했습니다.")
        print(err)
        return 1

    write_text(APP, text)
    print("[완료] Step112 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())


from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step110_backups"

CSS_BEGIN = "# >>> STEP110_TITLE_AND_PERIOD_HIGHLIGHT_CSS_BEGIN"
CSS_END = "# >>> STEP110_TITLE_AND_PERIOD_HIGHLIGHT_CSS_END"

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
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step110: 제목을 실제로 아이콘바 가까이 내려 배치. 달력/표 채우기 성공 부분은 건드리지 않음 */",
"    .header-container, .step99-header-container {{",
"        position: relative !important;",
"        z-index: 20 !important;",
"        transform: translateY(58px) !important;",
"        margin-top: 0 !important;",
"        margin-bottom: 0 !important;",
"        padding-top: 0 !important;",
"        padding-bottom: 0 !important;",
"        min-height: 32px !important;",
"        height: auto !important;",
"        overflow: visible !important;",
"    }}",
"    .step99-header-title, .step69-title-main, .header-container b {{",
"        font-size: 22px !important;",
"        line-height: 1.25 !important;",
"        letter-spacing: -0.35px !important;",
"    }}",
"    .step99-header-teacher, .step69-title-teacher {{",
"        font-size: 12px !important;",
"        line-height: 1.2 !important;",
"    }}",
"    @media (max-width: 520px) {{",
"        .header-container, .step99-header-container {{",
"            transform: translateY(56px) !important;",
"        }}",
"        .step99-header-title, .step69-title-main, .header-container b {{",
"            font-size: 20px !important;",
"        }}",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

HIGHLIGHT_BLOCK = "\n".join([
"    # Step110: 현재교시/다음교시 표시 규칙",
"    # - 00:00~05:59: 표시 중단",
"    # - 06:00~조회 시작 전: 조회 행 테두리 준비 표시",
"    # - 수업 진행 중: 해당 행 채우기",
"    # - 9교시 종료 후~24:00: 표시 중단",
"    active_row_idx = None",
"    preview_row_idx = None",
"    now = datetime.now(kst_tz)",
"    now_mins = now.hour * 60 + now.minute",
"    step110_enable_period_highlight = 6 * 60 <= now_mins < 17 * 60 + 50",
"    if step110_enable_period_highlight:",
"        for idx, (period, time_str) in enumerate(period_times):",
"            if period == \"학사일정\":",
"                continue",
"            try:",
"                start_t, end_t = time_str.split(\"\\n\")",
"                s_h, s_m = map(int, start_t.split(\":\"))",
"                e_h, e_m = map(int, end_t.split(\":\"))",
"                s_mins = s_h * 60 + s_m",
"                e_mins = e_h * 60 + e_m",
"            except Exception:",
"                continue",
"",
"            if s_mins <= now_mins < e_mins:",
"                active_row_idx = idx",
"                preview_row_idx = None",
"                break",
"            elif now_mins < s_mins:",
"                preview_row_idx = idx",
"                break",
"",
])

def main() -> int:
    print("=" * 60)
    print("Step110 제목 위치 최종 보정 + 교시 표시 시간 규칙")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step110_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    text = strip_block(text, CSS_BEGIN, CSS_END)

    # 1) 현재교시 계산 블록 교체
    # 현재 app.py는 active_row_idx / preview_row_idx 계산 후 html_parts를 생성하는 구조.
    pattern = re.compile(
        r"    active_row_idx\s*=\s*None\s*\n"
        r"    preview_row_idx\s*=\s*None\s*\n"
        r"    now\s*=\s*datetime\.now\(kst_tz\)\s*\n"
        r"    now_mins\s*=\s*now\.hour\s*\*\s*60\s*\+\s*now\.minute\s*\n"
        r".*?"
        r"    html_parts\s*=\s*\[\]\s*\n",
        re.S,
    )
    replacement = HIGHLIGHT_BLOCK + "\n    html_parts = []\n"
    text2, n = pattern.subn(replacement, text, count=1)

    if n:
        text = text2
        print("[수정] 현재교시/다음교시 표시 규칙을 06:00~9교시 종료 전으로 제한했습니다.")
    else:
        print("[주의] 현재교시 계산 블록을 찾지 못했습니다. 제목 CSS만 적용합니다.")

    # 2) 제목 위치 CSS 삽입
    insert_points = [
        "# >>> STEP109_TITLE_GAP_CSS_END",
        "# >>> STEP108C_TITLE_AND_AUTOFONT_CSS_END",
        "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END",
        "# >>> STEP106_SECTION_THEME_CSS_END",
    ]
    inserted = False
    for marker in insert_points:
        if marker in text:
            text = text.replace(marker, marker + "\n" + CSS_BLOCK, 1)
            inserted = True
            print(f"[수정] {marker} 뒤에 Step110 제목 CSS를 추가했습니다.")
            break

    if not inserted:
        if "\ndisplay_dashboard()" in text:
            text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
            print("[주의] CSS를 display_dashboard 호출 직전에 추가했습니다.")
        else:
            text += "\n" + CSS_BLOCK
            print("[주의] CSS 삽입 위치를 찾지 못해 파일 끝에 추가했습니다.")

    tmp = APP.with_suffix(".step110_test.py")
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
    print("[완료] Step110 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

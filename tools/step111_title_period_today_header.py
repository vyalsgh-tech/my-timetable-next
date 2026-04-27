
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step111_backups"

CSS_BEGIN = "# >>> STEP111_TITLE_DAY_PERIOD_RULES_CSS_BEGIN"
CSS_END = "# >>> STEP111_TITLE_DAY_PERIOD_RULES_CSS_END"

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
"    /* Step111: 제목을 아이콘바 바로 위로 더 바짝 이동. 달력은 건드리지 않음 */",
"    .step69-title-row,",
"    .header-container,",
"    .step99-header-container {{",
"        position: relative !important;",
"        z-index: 30 !important;",
"        transform: translateY(76px) !important;",
"        margin-top: 0 !important;",
"        margin-bottom: -92px !important;",
"        padding-top: 0 !important;",
"        padding-bottom: 0 !important;",
"        min-height: 32px !important;",
"        height: auto !important;",
"        overflow: visible !important;",
"    }}",
"    div:has(> .step69-title-row),",
"    div:has(> .header-container),",
"    div:has(> .step99-header-container) {{",
"        margin-bottom: -92px !important;",
"        padding-bottom: 0 !important;",
"        min-height: 0 !important;",
"    }}",
"    .step99-header-title,",
"    .step69-title-main,",
"    .header-container b {{",
"        font-size: 22px !important;",
"        line-height: 1.25 !important;",
"        letter-spacing: -0.35px !important;",
"    }}",
"    .step99-header-teacher,",
"    .step69-title-teacher {{",
"        font-size: 12px !important;",
"        line-height: 1.2 !important;",
"    }}",
"    @media (max-width: 520px) {{",
"        .step69-title-row, .header-container, .step99-header-container {{",
"            transform: translateY(72px) !important;",
"            margin-bottom: -88px !important;",
"        }}",
"        div:has(> .step69-title-row),",
"        div:has(> .header-container),",
"        div:has(> .step99-header-container) {{",
"            margin-bottom: -88px !important;",
"        }}",
"        .step99-header-title, .step69-title-main, .header-container b {{",
"            font-size: 20px !important;",
"        }}",
"    }}",
"    /* Step111: 오늘 요일 헤더 보조 클래스 */",
"    table.mobile-table th.step111-today-header {{",
"        background-color: {t.get('hl_per', t.get('head_bg', '#2563eb'))} !important;",
"        color: {t.get('button_primary_fg', '#ffffff')} !important;",
"    }}",
"    table.mobile-table th.step111-today-header * {{",
"        background: transparent !important;",
"        color: inherit !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

HIGHLIGHT_BLOCK = "\n".join([
"    # Step111: 현재교시/다음교시 표시 규칙",
"    # - 18:00~다음날 05:59: 교시 표시 중단",
"    # - 06:00~조회 시작 전: 조회 행 준비 테두리",
"    # - 교시 진행 중: 해당 행 채우기",
"    # - 각 교시 종료 후 다음 교시 시작 전: 다음 교시 준비 테두리",
"    active_row_idx = None",
"    preview_row_idx = None",
"    now = datetime.now(kst_tz)",
"    now_mins = now.hour * 60 + now.minute",
"    step111_enable_period_highlight = 6 * 60 <= now_mins < 18 * 60",
"    if step111_enable_period_highlight:",
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
"            if now_mins < s_mins:",
"                preview_row_idx = idx",
"                break",
"",
])

HEADER_LINES = "\n".join([
"        is_today_col = bool(is_current_week and col == today_idx)",
"        th_class = \"step111-today-header\" if is_today_col else \"\"",
"        th_bg = t.get(\"hl_per\", t.get(\"head_bg\", \"#dbeafe\")) if is_today_col else t[\"head_bg\"]",
"        th_fg = t.get(\"button_primary_fg\", \"#ffffff\") if is_today_col else t[\"head_fg\"]",
""
])

def main() -> int:
    print("=" * 60)
    print("Step111 제목 밀착 + 18시 이후 교시표시 중단 + 오늘 요일 헤더")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step111_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    text = strip_block(text, CSS_BEGIN, CSS_END)

    # 1) 제목 CSS 삽입
    insert_points = [
        "# >>> STEP110_TITLE_AND_PERIOD_HIGHLIGHT_CSS_END",
        "# >>> STEP109_TITLE_GAP_CSS_END",
        "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END",
        "# >>> STEP104_TABLE_CELL_FILL_FIX_END",
    ]
    inserted_css = False
    for marker in insert_points:
        if marker in text:
            text = text.replace(marker, marker + "\n" + CSS_BLOCK, 1)
            inserted_css = True
            print(f"[수정] {marker} 뒤에 Step111 CSS를 추가했습니다.")
            break
    if not inserted_css:
        if "\ndisplay_dashboard()" in text:
            text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
            print("[주의] CSS를 display_dashboard 호출 직전에 추가했습니다.")
        else:
            text += "\n" + CSS_BLOCK
            print("[주의] CSS 삽입 위치를 찾지 못해 파일 끝에 추가했습니다.")

    # 2) 현재교시/준비교시 계산 블록 교체
    # Step110 블록 우선 교체
    step110_pattern = re.compile(
        r"    # Step110: 현재교시/다음교시 표시 규칙\n"
        r".*?"
        r"    html_parts\s*=\s*\[\]\s*\n",
        re.S,
    )
    text2, n = step110_pattern.subn(HIGHLIGHT_BLOCK + "\n    html_parts = []\n", text, count=1)
    if n == 0:
        # 일반 active/preview 블록 교체
        generic_pattern = re.compile(
            r"    active_row_idx\s*=\s*None\s*\n"
            r"    preview_row_idx\s*=\s*None\s*\n"
            r"    now\s*=\s*datetime\.now\(kst_tz\)\s*\n"
            r"    now_mins\s*=\s*now\.hour\s*\*\s*60\s*\+\s*now\.minute\s*\n"
            r".*?"
            r"    html_parts\s*=\s*\[\]\s*\n",
            re.S,
        )
        text2, n = generic_pattern.subn(HIGHLIGHT_BLOCK + "\n    html_parts = []\n", text, count=1)
    if n:
        text = text2
        print("[수정] 교시 강조 규칙을 06:00~18:00 범위로 재설정했습니다.")
    else:
        print("[주의] 현재교시 계산 블록을 찾지 못했습니다.")

    # 3) 오늘 요일 헤더 채우기
    # Header loop part: replace th_class/th_bg/th_fg block before header th append.
    header_pattern = re.compile(
        r"        th_class\s*=.*?\n"
        r"        th_bg\s*=.*?\n"
        r"        th_fg\s*=.*?\n"
        r"        html_parts\.append\(\n"
        r"            f\"<th class='\{th_class\}'",
        re.S,
    )
    replacement = HEADER_LINES + "        html_parts.append(\n            f\"<th class='{th_class}'"
    text2, n_head = header_pattern.subn(replacement, text, count=1)
    if n_head:
        text = text2
        print("[수정] 오늘 요일 헤더 칸 채우기 로직을 적용했습니다.")
    else:
        # fallback: insert lines just before first header th append if variables not found
        simple_marker = "        html_parts.append(\n            f\"<th class='{th_class}'"
        if simple_marker in text and "step111-today-header" not in text:
            text = text.replace(simple_marker, HEADER_LINES + simple_marker, 1)
            print("[주의] 헤더 변수 블록을 찾지 못해 append 직전에 삽입했습니다.")
        else:
            print("[주의] 오늘 요일 헤더 로직 위치를 찾지 못했습니다.")

    tmp = APP.with_suffix(".step111_test.py")
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
    print("[완료] Step111 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

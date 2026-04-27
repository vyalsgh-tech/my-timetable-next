
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step109_backups"

AUTO_BEGIN = "# >>> STEP109_AUTOFONT_SAFE_BEGIN"
AUTO_END = "# >>> STEP109_AUTOFONT_SAFE_END"
CSS_BEGIN = "# >>> STEP109_TITLE_GAP_CSS_BEGIN"
CSS_END = "# >>> STEP109_TITLE_GAP_CSS_END"

OLD_BLOCKS = [
    ("# >>> STEP108_TITLE_AND_AUTOFONT_CSS_BEGIN", "# >>> STEP108_TITLE_AND_AUTOFONT_CSS_END"),
    ("# >>> STEP108B_TITLE_AND_AUTOFONT_CSS_BEGIN", "# >>> STEP108B_TITLE_AND_AUTOFONT_CSS_END"),
    ("# >>> STEP108C_TITLE_AND_AUTOFONT_CSS_BEGIN", "# >>> STEP108C_TITLE_AND_AUTOFONT_CSS_END"),
    ("# >>> STEP108C_AUTOFONT_BEGIN", "# >>> STEP108C_AUTOFONT_END"),
    (AUTO_BEGIN, AUTO_END),
    (CSS_BEGIN, CSS_END),
]

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

AUTOFONT_BLOCK = "\n".join([
AUTO_BEGIN,
"            # Step109: display 생성 전에도 안전한 자동 폰트 축소. subject 원문 길이 기준.",
"            step109_source_text = str(subject) if subject is not None else ''",
"            step109_plain = re.sub(r'<[^>]+>', '', step109_source_text)",
"            step109_plain = step109_plain.replace('&nbsp;', ' ').replace(chr(10), ' ').strip()",
"            step109_len = len(step109_plain)",
"            if step109_len >= 46:",
"                font_sz_str = '10px'",
"                line_height = '1.13'",
"            elif step109_len >= 32:",
"                font_sz_str = '11px'",
"                line_height = '1.15'",
"            elif step109_len >= 20:",
"                font_sz_str = '12px'",
"                line_height = '1.17'",
"            elif step109_len >= 11:",
"                font_sz_str = '13px'",
"                line_height = '1.19'",
"            else:",
"                font_sz_str = '14px'",
"                line_height = '1.2'",
"            if period in ['학사일정', '조회'] and step109_len >= 16 and font_sz_str == '13px':",
"                font_sz_str = '12px'",
"                line_height = '1.17'",
AUTO_END,
""
])

CSS_BLOCK = "\n".join([
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step109: 제목을 버튼 모음칸에 가깝게. 달력/표 채우기 성공 부분은 건드리지 않음 */",
"    .header-container, .step99-header-container {{",
"        margin-top: 6px !important;",
"        margin-bottom: -74px !important;",
"        padding-top: 0 !important;",
"        padding-bottom: 0 !important;",
"        min-height: 32px !important;",
"        height: auto !important;",
"        overflow: visible !important;",
"    }}",
"    div:has(> .header-container), div:has(> .step99-header-container) {{",
"        margin-bottom: -74px !important;",
"        padding-bottom: 0 !important;",
"    }}",
"    .step99-header-title, .step69-title-main, .header-container b {{",
"        font-size: 21px !important;",
"        line-height: 1.3 !important;",
"        letter-spacing: -0.3px !important;",
"    }}",
"    .step99-header-teacher, .step69-title-teacher {{",
"        font-size: 12px !important;",
"        line-height: 1.2 !important;",
"    }}",
"    table.mobile-table th, table.mobile-table td {{",
"        overflow: hidden !important;",
"        box-sizing: border-box !important;",
"    }}",
"    table.mobile-table th > div, table.mobile-table td > div {{",
"        max-width: 100% !important;",
"        min-width: 0 !important;",
"        box-sizing: border-box !important;",
"        white-space: normal !important;",
"        word-break: keep-all !important;",
"        overflow-wrap: anywhere !important;",
"        text-align: center !important;",
"    }}",
"    @media (max-width: 520px) {{",
"        .header-container, .step99-header-container {{ margin-bottom: -70px !important; }}",
"        div:has(> .header-container), div:has(> .step99-header-container) {{ margin-bottom: -70px !important; }}",
"        .step99-header-title, .step69-title-main, .header-container b {{ font-size: 19px !important; }}",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step109 Step108c 오류 복구 + 안전 자동 폰트")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step109_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    # 1) 실패한 Step108 계열 블록 제거
    for begin, end in OLD_BLOCKS:
        text = strip_block(text, begin, end)

    # 2) 혹시 남은 깨진 코드 조각 제거
    broken_patterns = [
        r"\n\s*step108_plain\s*=\s*re\.sub\(.*?\n\s*if period in \[\"학사일정\", \"조회\"\].*?\n\s*line_height\s*=\s*\"1\.17\"\s*",
        r"\n\s*step108_plain\s*=.*?\n\s*step108_len\s*=.*?\n(?:\s*if step108_len.*?\n)+",
    ]
    for pat in broken_patterns:
        text = re.sub(pat, "\n", text, flags=re.S)

    text = text.replace('line_height = "1.17"if period == "학사일정":', 'line_height = "1.17"\n            if period == "학사일정":')

    # 3) 자동 폰트 로직 삽입. display가 아니라 subject 기준이라 UnboundLocalError가 나지 않음.
    if "step109_source_text = str(subject)" not in text:
        # 고정 폰트 블록이 남아 있으면 교체
        font_pattern = re.compile(
            r"            font_sz_str\s*=\s*[\"']14px[\"']\s*\n"
            r"            line_height\s*=\s*[\"']1\.2[\"']\s*\n?",
            re.S,
        )
        text2, n = font_pattern.subn(AUTOFONT_BLOCK, text, count=1)

        if n == 0:
            # 이미 기존 font 변수 위치가 사라진 경우, td append 직전으로 삽입
            marker = "            html_parts.append(\n                f\"<td class='{cell_class}'"
            if marker in text:
                text2 = text.replace(marker, AUTOFONT_BLOCK + marker, 1)
                n = 1

        if n:
            text = text2
            print("[수정] display 대신 subject 기준의 안전 자동 폰트 로직을 삽입했습니다.")
        else:
            print("[주의] 자동 폰트 로직 삽입 위치를 찾지 못했습니다. CSS 줄바꿈만 적용합니다.")
    else:
        print("[안내] Step109 자동 폰트 로직이 이미 존재합니다.")

    text = text.replace("overflow-wrap:break-word;", "overflow-wrap:anywhere;")

    # 4) 제목/줄바꿈 CSS 삽입
    insert_points = [
        "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END",
        "# >>> STEP106_SECTION_THEME_CSS_END",
        "# >>> STEP104_TABLE_CELL_FILL_FIX_END",
    ]
    inserted = False
    for marker in insert_points:
        if marker in text:
            text = text.replace(marker, marker + "\n" + CSS_BLOCK, 1)
            inserted = True
            print(f"[수정] {marker} 뒤에 Step109 CSS를 추가했습니다.")
            break
    if not inserted:
        if "\ndisplay_dashboard()" in text:
            text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
            print("[주의] CSS를 display_dashboard 호출 직전에 추가했습니다.")
        else:
            text += "\n" + CSS_BLOCK
            print("[주의] CSS 삽입 위치를 찾지 못해 파일 끝에 추가했습니다.")

    tmp = APP.with_suffix(".step109_test.py")
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
    print("[완료] Step109 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

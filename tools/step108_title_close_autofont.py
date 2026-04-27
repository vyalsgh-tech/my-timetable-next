
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step108_backups"

CSS_BEGIN = "# >>> STEP108_TITLE_AND_AUTOFONT_CSS_BEGIN"
CSS_END = "# >>> STEP108_TITLE_AND_AUTOFONT_CSS_END"

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
"    /* Step108: 제목을 버튼 모음칸에 더 가깝게 배치. 달력/표 채우기 구조는 건드리지 않음 */",
"    .header-container,",
"    .step99-header-container {{",
"        margin-top: 8px !important;",
"        margin-bottom: -76px !important;",
"        padding-top: 0 !important;",
"        padding-bottom: 0 !important;",
"        min-height: 32px !important;",
"        height: auto !important;",
"        overflow: visible !important;",
"    }}",
"    div:has(> .header-container),",
"    div:has(> .step99-header-container) {{",
"        margin-bottom: -76px !important;",
"        padding-bottom: 0 !important;",
"    }}",
"    .step99-header-title,",
"    .step69-title-main,",
"    .header-container b {{",
"        font-size: 21px !important;",
"        line-height: 1.3 !important;",
"        letter-spacing: -0.3px !important;",
"    }}",
"    .step99-header-teacher,",
"    .step69-title-teacher {{",
"        font-size: 12px !important;",
"        line-height: 1.2 !important;",
"    }}",
"    @media (max-width: 520px) {{",
"        .header-container, .step99-header-container {{",
"            margin-bottom: -72px !important;",
"        }}",
"        div:has(> .header-container),",
"        div:has(> .step99-header-container) {{",
"            margin-bottom: -72px !important;",
"        }}",
"        .step99-header-title,",
"        .step69-title-main,",
"        .header-container b {{",
"            font-size: 19px !important;",
"        }}",
"    }}",
"",
"    /* Step108: 모든 시간표 칸 내용은 칸 안에서 줄바꿈 */",
"    table.mobile-table th,",
"    table.mobile-table td {{",
"        overflow: hidden !important;",
"        box-sizing: border-box !important;",
"    }}",
"    table.mobile-table th > div,",
"    table.mobile-table td > div {{",
"        max-width: 100% !important;",
"        min-width: 0 !important;",
"        box-sizing: border-box !important;",
"        white-space: normal !important;",
"        word-break: keep-all !important;",
"        overflow-wrap: anywhere !important;",
"        text-align: center !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

ADAPTIVE_FONT_BLOCK = "\n".join([
"            # Step108: 칸 내용 길이에 따라 자동 줄바꿈 + 폰트 1px 단위 축소",
"            step108_plain = re.sub(r\"<[^>]+>\", \"\", str(display))",
"            step108_plain = step108_plain.replace(\"&nbsp;\", \" \").replace(\"\\n\", \" \").strip()",
"            step108_len = len(step108_plain)",
"            if step108_len >= 46:",
"                font_sz_str = \"10px\"",
"                line_height = \"1.13\"",
"            elif step108_len >= 32:",
"                font_sz_str = \"11px\"",
"                line_height = \"1.15\"",
"            elif step108_len >= 20:",
"                font_sz_str = \"12px\"",
"                line_height = \"1.17\"",
"            elif step108_len >= 11:",
"                font_sz_str = \"13px\"",
"                line_height = \"1.19\"",
"            else:",
"                font_sz_str = \"14px\"",
"                line_height = \"1.2\"",
"            if period in [\"학사일정\", \"조회\"] and step108_len >= 16 and font_sz_str == \"13px\":",
"                font_sz_str = \"12px\"",
"                line_height = \"1.17\"",
])

def main() -> int:
    print("=" * 60)
    print("Step108 제목 위치/크기 + 시간표 칸 자동 폰트 축소")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step108_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")
    text = strip_block(text, CSS_BEGIN, CSS_END)

    # 1) 기존 고정 폰트 설정을 길이 기반 자동 축소 로직으로 교체
    if "step108_plain = re.sub" not in text:
        pattern = re.compile(
            r"            font_sz_str\s*=\s*\"14px\"\s*\n"
            r"            line_height\s*=\s*\"1\.2\"\s*",
            re.S,
        )
        text2, n = pattern.subn(ADAPTIVE_FONT_BLOCK, text, count=1)
        if n:
            text = text2
            print("[수정] 시간표 셀 폰트를 내용 길이에 따라 자동 축소하도록 변경했습니다.")
        else:
            print("[주의] font_sz_str 고정 설정 위치를 찾지 못했습니다. CSS 줄바꿈만 적용합니다.")
    else:
        print("[안내] Step108 자동 폰트 로직이 이미 존재합니다.")

    # 2) overflow-wrap은 항상 anywhere로 보정
    text = text.replace("overflow-wrap:break-word;", "overflow-wrap:anywhere;")

    # 3) Step107 뒤에 최종 CSS 삽입. 달력/표 채우기 성공 부분은 수정하지 않음.
    if "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END" in text:
        text = text.replace("# >>> STEP107_FINAL_SECTION_COLOR_CSS_END", "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END\n" + CSS_BLOCK, 1)
        print("[수정] Step107 뒤에 Step108 CSS를 추가했습니다.")
    elif "# >>> STEP104_TABLE_CELL_FILL_FIX_END" in text:
        text = text.replace("# >>> STEP104_TABLE_CELL_FILL_FIX_END", "# >>> STEP104_TABLE_CELL_FILL_FIX_END\n" + CSS_BLOCK, 1)
        print("[주의] Step107 위치를 찾지 못해 Step104 뒤에 CSS를 추가했습니다.")
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
        print("[주의] CSS를 display_dashboard 호출 직전에 추가했습니다.")
    else:
        text += "\n" + CSS_BLOCK
        print("[주의] CSS 삽입 위치를 찾지 못해 파일 끝에 추가했습니다.")

    tmp = APP.with_suffix(".step108_test.py")
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
    print("[완료] Step108 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

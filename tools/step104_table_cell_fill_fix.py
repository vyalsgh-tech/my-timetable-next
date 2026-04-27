
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step104_backups"

CSS_BEGIN = "# >>> STEP104_TABLE_CELL_FILL_FIX_BEGIN"
CSS_END = "# >>> STEP104_TABLE_CELL_FILL_FIX_END"

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
"    /* Step104: 표 헤더/교시칸은 글자 배경색이 아니라 셀 전체 채우기로 처리 */",
"    table.mobile-table th {{",
"        background: {t.get('head_bg', '#334155')} !important;",
"        background-color: {t.get('head_bg', '#334155')} !important;",
"        color: {t.get('head_fg', '#f8fafc')} !important;",
"        border-color: {t.get('grid', '#64748b')} !important;",
"        box-shadow: none !important;",
"    }}",
"    table.mobile-table th > *,",
"    table.mobile-table th span,",
"    table.mobile-table th div {{",
"        background: transparent !important;",
"        background-color: transparent !important;",
"        color: inherit !important;",
"        box-shadow: none !important;",
"    }}",
"    table.mobile-table td:first-child {{",
"        background: {t.get('per_bg', '#334155')} !important;",
"        background-color: {t.get('per_bg', '#334155')} !important;",
"        color: {t.get('per_fg', '#f8fafc')} !important;",
"        border-color: {t.get('grid', '#64748b')} !important;",
"        box-shadow: none !important;",
"    }}",
"    table.mobile-table td:first-child > *,",
"    table.mobile-table td:first-child div,",
"    table.mobile-table td:first-child span,",
"    table.mobile-table td:first-child b {{",
"        background: transparent !important;",
"        background-color: transparent !important;",
"        color: inherit !important;",
"        box-shadow: none !important;",
"    }}",
"    table.mobile-table td:not(:first-child) {{",
"        background-color: {t.get('cell_bg', '#ffffff')} !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step104 시간표 헤더/교시칸 셀 전체 채우기 보정")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step104_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")
    text = strip_block(text, CSS_BEGIN, CSS_END)

    # 1) 원본 시간표 HTML 생성부의 inline style 자체를 셀 채우기 우선으로 보정
    replacements = [
        (
            "<th style='width: 13%; font-size:14px;'>교시</th>",
            "<th style='width: 13%; font-size:14px; background-color:{t['head_bg']} !important; color:{t['head_fg']} !important;'>교시</th>",
        ),
        (
            "style='background-color:{th_bg}; color:{th_fg};'",
            "style='background-color:{th_bg} !important; color:{th_fg} !important;'",
        ),
        (
            "style='background-color:{p_bg}; color:{p_fg};'",
            "style='background-color:{p_bg} !important; color:{p_fg} !important;'",
        ),
    ]

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            print(f"[수정] inline style 보정: {old[:40]}...")
        else:
            print(f"[주의] inline style 대상 문구를 찾지 못했습니다: {old[:40]}...")

    # 2) 이전 단계에서 자식 요소에 배경을 칠한 규칙을 최종 CSS로 무력화
    insert_marker = "# >>> STEP103_STABLE_UI_END"
    if insert_marker in text:
        text = text.replace(insert_marker, insert_marker + "\n" + CSS_BLOCK, 1)
        print("[수정] Step103 UI 뒤에 Step104 최종 CSS를 추가했습니다.")
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
        print("[주의] Step103 UI 위치를 찾지 못해 display_dashboard 호출 직전에 CSS 추가")
    else:
        text += "\n" + CSS_BLOCK
        print("[주의] 삽입 위치를 찾지 못해 파일 끝에 CSS 추가")

    tmp = APP.with_suffix(".step104_test.py")
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
    print("[완료] Step104 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())


from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step106_backups"

HELPER_BEGIN = "# >>> STEP106_SECTION_THEME_HELPER_BEGIN"
HELPER_END = "# >>> STEP106_SECTION_THEME_HELPER_END"
CSS_BEGIN = "# >>> STEP106_SECTION_THEME_CSS_BEGIN"
CSS_END = "# >>> STEP106_SECTION_THEME_CSS_END"

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

HELPER_BLOCK = "\n".join([
HELPER_BEGIN,
"def step106_section_theme(theme):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', '')).lower()",
"    def put(**kw):",
"        t2.update(kw)",
"",
"    if any(k in name for k in ['모던 다크', '모노다크', '다크', 'dark', '블랙', 'black', 'night', '나이트']):",
"        put(",
"            head_bg='#334155', head_fg='#f8fafc',",
"            acad_per_bg='#475569', acad_per_fg='#f8fafc', acad_cell_bg='#1e293b', acad_cell_fg='#e2e8f0',",
"            query_per_bg='#1d4ed8', query_per_fg='#ffffff', query_cell_bg='#172554', query_cell_fg='#dbeafe',",
"            class_per_bg='#334155', class_per_fg='#f8fafc', class_cell_bg='#0f172a', class_cell_fg='#e5e7eb',",
"            lunch_bg='#1e293b', lunch_fg='#cbd5e1', custom_fg='#38bdf8', cell_bg='#0f172a', cell_fg='#e5e7eb', text='#f8fafc',",
"        )",
"    elif any(k in name for k in ['모노톤', '모노', 'mono', 'gray', 'grey', '그레이', '회색']):",
"        put(",
"            head_bg='#52525b', head_fg='#ffffff',",
"            acad_per_bg='#71717a', acad_per_fg='#ffffff', acad_cell_bg='#f4f4f5', acad_cell_fg='#18181b',",
"            query_per_bg='#52525b', query_per_fg='#ffffff', query_cell_bg='#e4e4e7', query_cell_fg='#18181b',",
"            class_per_bg='#71717a', class_per_fg='#ffffff', class_cell_bg='#ffffff', class_cell_fg='#18181b',",
"            lunch_bg='#f4f4f5', lunch_fg='#18181b', custom_fg='#334155', cell_bg='#ffffff', cell_fg='#18181b', text='#18181b',",
"        )",
"    elif any(k in name for k in ['러블리 핑크', '핑크', 'pink', '로즈', 'rose']):",
"        put(",
"            head_bg='#ffd6e7', head_fg='#831843',",
"            acad_per_bg='#f9a8d4', acad_per_fg='#831843', acad_cell_bg='#fff1f8', acad_cell_fg='#9d174d',",
"            query_per_bg='#fb7185', query_per_fg='#ffffff', query_cell_bg='#ffe4ef', query_cell_fg='#831843',",
"            class_per_bg='#fbcfe8', class_per_fg='#831843', class_cell_bg='#fffafd', class_cell_fg='#831843',",
"            lunch_bg='#fff1f5', lunch_fg='#831843', custom_fg='#db2777', cell_bg='#fffafd', cell_fg='#831843', text='#831843',",
"        )",
"    elif any(k in name for k in ['포레스트', 'forest', '숲', '그린', 'green', '초록', '민트', 'mint', '세이지', 'sage', '올리브', 'olive']):",
"        put(",
"            head_bg='#dff3e6', head_fg='#0f3d24',",
"            acad_per_bg='#9ed8af', acad_per_fg='#0f3d24', acad_cell_bg='#f0fdf4', acad_cell_fg='#14532d',",
"            query_per_bg='#2e7d32', query_per_fg='#ffffff', query_cell_bg='#dcfce7', query_cell_fg='#14532d',",
"            class_per_bg='#c7e9d1', class_per_fg='#0f3d24', class_cell_bg='#fbfffc', class_cell_fg='#0f3d24',",
"            lunch_bg='#edf8f0', lunch_fg='#14532d', custom_fg='#15803d', cell_bg='#fbfffc', cell_fg='#0f3d24', text='#0f3d24',",
"        )",
"    elif any(k in name for k in ['웜', '파스텔', '베이지', 'beige', '브라운', 'brown', '카페', '라떼']):",
"        put(",
"            head_bg='#f4e0b8', head_fg='#3f2d12',",
"            acad_per_bg='#e7c98c', acad_per_fg='#3f2d12', acad_cell_bg='#fff8e1', acad_cell_fg='#5f3b05',",
"            query_per_bg='#d97706', query_per_fg='#fff7ed', query_cell_bg='#ffedd5', query_cell_fg='#7c2d12',",
"            class_per_bg='#ead2a0', class_per_fg='#3f2d12', class_cell_bg='#fffdf6', class_cell_fg='#3f2d12',",
"            lunch_bg='#fff7e6', lunch_fg='#5f3b05', custom_fg='#b45309', cell_bg='#fffdf6', cell_fg='#3f2d12', text='#3f2d12',",
"        )",
"    elif any(k in name for k in ['블루', 'blue', '하늘', '스카이', 'sky', '오션', 'ocean']):",
"        put(",
"            head_bg='#dbeafe', head_fg='#0f172a',",
"            acad_per_bg='#bfdbfe', acad_per_fg='#0f172a', acad_cell_bg='#eff6ff', acad_cell_fg='#1e3a8a',",
"            query_per_bg='#2563eb', query_per_fg='#ffffff', query_cell_bg='#dbeafe', query_cell_fg='#1e3a8a',",
"            class_per_bg='#bfdbfe', class_per_fg='#0f172a', class_cell_bg='#ffffff', class_cell_fg='#0f172a',",
"            lunch_bg='#eff6ff', lunch_fg='#1e3a8a', custom_fg='#2563eb', cell_bg='#ffffff', cell_fg='#0f172a', text='#0f172a',",
"        )",
"    elif any(k in name for k in ['퍼플', 'purple', '보라', '라벤더', 'lavender']):",
"        put(",
"            head_bg='#ede9fe', head_fg='#3b0764',",
"            acad_per_bg='#c4b5fd', acad_per_fg='#3b0764', acad_cell_bg='#f5f3ff', acad_cell_fg='#4c1d95',",
"            query_per_bg='#7c3aed', query_per_fg='#ffffff', query_cell_bg='#ede9fe', query_cell_fg='#4c1d95',",
"            class_per_bg='#ddd6fe', class_per_fg='#3b0764', class_cell_bg='#fffbff', class_cell_fg='#3b0764',",
"            lunch_bg='#f5f3ff', lunch_fg='#4c1d95', custom_fg='#7c3aed', cell_bg='#fffbff', cell_fg='#3b0764', text='#3b0764',",
"        )",
"    else:",
"        t2.setdefault('acad_per_bg', t2.get('per_bg', '#dbeafe'))",
"        t2.setdefault('acad_per_fg', t2.get('per_fg', '#0f172a'))",
"        t2.setdefault('acad_cell_bg', t2.get('lunch_bg', '#f8fafc'))",
"        t2.setdefault('acad_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('query_per_bg', t2.get('hl_per', t2.get('per_bg', '#2563eb')))",
"        t2.setdefault('query_per_fg', '#ffffff')",
"        t2.setdefault('query_cell_bg', t2.get('lunch_bg', '#eff6ff'))",
"        t2.setdefault('query_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('class_per_bg', t2.get('per_bg', '#dbeafe'))",
"        t2.setdefault('class_per_fg', t2.get('per_fg', '#0f172a'))",
"        t2.setdefault('class_cell_bg', t2.get('cell_bg', '#ffffff'))",
"        t2.setdefault('class_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('lunch_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('custom_fg', '#2563eb')",
"    return t2",
HELPER_END,
]) + "\n"

CSS_BLOCK = "\n".join([
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step106: 학사일정 / 조회 / 수업행을 서로 다른 채우기와 글자색으로 구분 */",
"    table.mobile-table th {{",
"        background-color: {t.get('head_bg', '#334155')} !important;",
"        color: {t.get('head_fg', '#f8fafc')} !important;",
"    }}",
"    table.mobile-table th * {{ background: transparent !important; color: inherit !important; }}",
"    table.mobile-table tr:nth-child(2) td:first-child {{ background-color: {t.get('acad_per_bg', t.get('per_bg', '#334155'))} !important; color: {t.get('acad_per_fg', '#f8fafc')} !important; }}",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) {{ background-color: {t.get('acad_cell_bg', '#1e293b')} !important; color: {t.get('acad_cell_fg', '#e2e8f0')} !important; }}",
"    table.mobile-table tr:nth-child(2) td * {{ background: transparent !important; color: inherit !important; }}",
"    table.mobile-table tr:nth-child(3) td:first-child {{ background-color: {t.get('query_per_bg', t.get('per_bg', '#1d4ed8'))} !important; color: {t.get('query_per_fg', '#ffffff')} !important; }}",
"    table.mobile-table tr:nth-child(3) td:not(:first-child) {{ background-color: {t.get('query_cell_bg', '#172554')} !important; color: {t.get('query_cell_fg', '#dbeafe')} !important; }}",
"    table.mobile-table tr:nth-child(3) td * {{ background: transparent !important; color: inherit !important; }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step106 모던 다크 재구성 + 행 구분 디자인")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step106_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    text = strip_block(text, HELPER_BEGIN, HELPER_END)
    text = strip_block(text, CSS_BEGIN, CSS_END)
    text = re.sub(r"\n\s*t\s*=\s*step106_section_theme\(t\)\s*", "\n", text)

    # helper before t usage
    marker = "t = themes[st.session_state.theme_idx]"
    if marker not in text:
        print("[오류] t = themes[st.session_state.theme_idx] 줄을 찾지 못했습니다.")
        return 1
    text = text.replace(marker, HELPER_BLOCK + "\n" + marker, 1)

    # apply after previous final theme functions so Step106 is last
    candidates = [
        "t = step105_final_readability(t)",
        "t = step103_theme(t)",
        "t = step99_apply_viewer_theme_palette(t)",
    ]
    applied = False
    for cand in candidates:
        if cand in text:
            text = text.replace(cand, cand + "\nt = step106_section_theme(t)", 1)
            applied = True
            break
    if not applied:
        text = text.replace(marker, marker + "\nt = step106_section_theme(t)", 1)
        applied = True
    print("[수정] Step106 테마 구분 보정을 최종 적용했습니다.")

    # Left period cell logic: academic / query / lunch / class
    p_block_pattern = re.compile(
        r"        if period == \"학사일정\":\n"
        r"            p_bg = .*?\n"
        r"            p_fg = .*?\n"
        r"        else:\n"
        r"            p_bg = .*?\n"
        r"            p_fg = .*?\n",
        re.S,
    )
    p_repl = (
        "        if period == \"학사일정\":\n"
        "            p_bg = t.get(\"acad_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))\n"
        "            p_fg = t.get(\"acad_per_fg\", t.get(\"per_fg\", \"#0f172a\"))\n"
        "        elif period == \"조회\":\n"
        "            p_bg = t.get(\"query_per_bg\", t.get(\"hl_per\", t.get(\"per_bg\", \"#2563eb\")))\n"
        "            p_fg = t.get(\"query_per_fg\", \"#ffffff\")\n"
        "        elif period == \"점심\":\n"
        "            p_bg = t.get(\"lunch_bg\", t.get(\"cell_bg\", \"#f8fafc\"))\n"
        "            p_fg = t.get(\"lunch_fg\", t.get(\"cell_fg\", \"#0f172a\"))\n"
        "        else:\n"
        "            p_bg = t.get(\"hl_per\", t.get(\"class_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))) if (is_current_week and active_row_idx == row_idx) else t.get(\"class_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))\n"
        "            p_fg = t.get(\"button_primary_fg\", \"#ffffff\") if (is_current_week and active_row_idx == row_idx) else t.get(\"class_per_fg\", t.get(\"per_fg\", \"#0f172a\"))\n"
    )
    text, n_p = p_block_pattern.subn(p_repl, text, count=1)
    print("[수정] 왼쪽 교시칸 색상 로직을 3파트 구조로 변경" if n_p else "[주의] 왼쪽 교시칸 색상 로직을 찾지 못했습니다.")

    # Cell bg/fg logic: academic / query / lunch / class
    cell_pattern = re.compile(
        r"            if period == \"학사일정\":\n"
        r"                bg = .*?\n"
        r"                fg = .*?\n"
        r"                deco = .*?\n"
        r"                if is_strike:\n"
        r"                    fg = .*?\n"
        r"                elif custom_color:\n"
        r"                    fg = custom_color\n"
        r"            else:\n"
        r"                bg = .*?\n"
        r"                fg = .*?\n"
        r"                deco = .*?\n"
        r"                if is_strike:\n"
        r"                    fg = .*?\n"
        r"                elif custom_color:\n"
        r"                    fg = custom_color\n"
        r"                elif is_custom:\n"
        r"                    fg = .*?\n",
        re.S,
    )
    cell_repl = (
        "            if period == \"학사일정\":\n"
        "                bg = t.get(\"acad_cell_bg\", t.get(\"lunch_bg\", t.get(\"cell_bg\", \"#f8fafc\")))\n"
        "                fg = t.get(\"acad_cell_fg\", t.get(\"cell_fg\", \"#0f172a\"))\n"
        "            elif period == \"조회\":\n"
        "                bg = t.get(\"query_cell_bg\", t.get(\"lunch_bg\", t.get(\"cell_bg\", \"#eff6ff\")))\n"
        "                fg = t.get(\"query_cell_fg\", t.get(\"cell_fg\", \"#0f172a\"))\n"
        "            elif period == \"점심\":\n"
        "                bg = t.get(\"lunch_bg\", t.get(\"cell_bg\", \"#f8fafc\"))\n"
        "                fg = t.get(\"lunch_fg\", t.get(\"cell_fg\", \"#0f172a\"))\n"
        "            else:\n"
        "                bg = t.get(\"class_cell_bg\", t.get(\"cell_bg\", \"#ffffff\"))\n"
        "                fg = t.get(\"class_cell_fg\", t.get(\"cell_fg\", \"#0f172a\"))\n"
        "            deco = \"line-through\" if is_strike else \"none\"\n"
        "            if is_strike:\n"
        "                fg = \"#bdc3c7\" if t[\"name\"] == \"모던 다크\" else \"#95a5a6\"\n"
        "            elif custom_color:\n"
        "                fg = custom_color\n"
        "            elif is_custom:\n"
        "                fg = t.get(\"custom_fg\", \"#e74c3c\")\n"
    )
    text, n_cell = cell_pattern.subn(cell_repl, text, count=1)
    print("[수정] 시간표 셀 색상 로직을 3파트 구조로 변경" if n_cell else "[주의] 시간표 셀 색상 로직을 찾지 못했습니다.")

    # CSS after Step105/104 to ensure academic and query visible, but do not touch calendar
    if "# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END" in text:
        text = text.replace("# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END", "# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END\n" + CSS_BLOCK, 1)
        print("[수정] Step105 뒤에 Step106 CSS 추가")
    elif "# >>> STEP104_TABLE_CELL_FILL_FIX_END" in text:
        text = text.replace("# >>> STEP104_TABLE_CELL_FILL_FIX_END", "# >>> STEP104_TABLE_CELL_FILL_FIX_END\n" + CSS_BLOCK, 1)
        print("[수정] Step104 뒤에 Step106 CSS 추가")
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
        print("[주의] CSS를 display_dashboard 호출 직전에 추가")
    else:
        text += "\n" + CSS_BLOCK
        print("[주의] CSS를 파일 끝에 추가")

    tmp = APP.with_suffix(".step106_test.py")
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
    print("[완료] Step106 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

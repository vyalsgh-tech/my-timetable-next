
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step107_backups"

HELPER_BEGIN = "# >>> STEP107_FINAL_SECTION_COLOR_HELPER_BEGIN"
HELPER_END = "# >>> STEP107_FINAL_SECTION_COLOR_HELPER_END"
CSS_BEGIN = "# >>> STEP107_FINAL_SECTION_COLOR_CSS_BEGIN"
CSS_END = "# >>> STEP107_FINAL_SECTION_COLOR_CSS_END"

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
"def step107_final_section_colors(theme):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', '')).lower()",
"    def put(**kw):",
"        t2.update(kw)",
"    # 왼쪽 제목칸은 파트 구분색을 쓰지 않고 공통 per_bg/per_fg만 사용한다.",
"    if any(k in name for k in ['모던 다크', '모노다크', '다크', 'dark', '블랙', 'black', 'night', '나이트']):",
"        put(",
"            head_bg='#243247', head_fg='#ffffff',",
"            per_bg='#334155', per_fg='#f8fafc',",
"            acad_cell_bg='#e2e8f0', acad_cell_fg='#1e293b',",
"            query_cell_bg='#dbeafe', query_cell_fg='#1e3a8a',",
"            class_cell_bg='#f8fafc', class_cell_fg='#0f172a',",
"            lunch_bg='#f1f5f9', lunch_fg='#334155',",
"            custom_fg='#0284c7', cell_bg='#f8fafc', cell_fg='#0f172a',",
"            text='#f8fafc', grid='#64748b', table_shell='#111827',",
"        )",
"    elif any(k in name for k in ['모노톤', '모노', 'mono', 'gray', 'grey', '그레이', '회색']):",
"        put(",
"            head_bg='#52525b', head_fg='#ffffff',",
"            per_bg='#71717a', per_fg='#ffffff',",
"            acad_cell_bg='#e4e4e7', acad_cell_fg='#18181b',",
"            query_cell_bg='#f1f5f9', query_cell_fg='#334155',",
"            class_cell_bg='#ffffff', class_cell_fg='#18181b',",
"            lunch_bg='#f4f4f5', lunch_fg='#18181b',",
"            custom_fg='#334155', cell_bg='#ffffff', cell_fg='#18181b',",
"            grid='#71717a', table_shell='#d4d4d8',",
"        )",
"    elif any(k in name for k in ['러블리 핑크', '핑크', 'pink', '로즈', 'rose']):",
"        put(",
"            per_bg='#fbcfe8', per_fg='#831843',",
"            acad_cell_bg='#fff1f8', acad_cell_fg='#9d174d',",
"            query_cell_bg='#ffe4ef', query_cell_fg='#831843',",
"            class_cell_bg='#fffafd', class_cell_fg='#831843',",
"            lunch_bg='#fff1f5', lunch_fg='#831843', custom_fg='#db2777',",
"        )",
"    elif any(k in name for k in ['포레스트', 'forest', '숲', '그린', 'green', '초록', '민트', 'mint', '세이지', 'sage', '올리브', 'olive']):",
"        put(",
"            per_bg='#c7e9d1', per_fg='#0f3d24',",
"            acad_cell_bg='#f0fdf4', acad_cell_fg='#14532d',",
"            query_cell_bg='#dcfce7', query_cell_fg='#14532d',",
"            class_cell_bg='#fbfffc', class_cell_fg='#0f3d24',",
"            lunch_bg='#edf8f0', lunch_fg='#14532d', custom_fg='#15803d',",
"        )",
"    elif any(k in name for k in ['웜', '파스텔', '베이지', 'beige', '브라운', 'brown', '카페', '라떼']):",
"        put(",
"            per_bg='#ead2a0', per_fg='#3f2d12',",
"            acad_cell_bg='#fff8e1', acad_cell_fg='#5f3b05',",
"            query_cell_bg='#ffedd5', query_cell_fg='#7c2d12',",
"            class_cell_bg='#fffdf6', class_cell_fg='#3f2d12',",
"            lunch_bg='#fff7e6', lunch_fg='#5f3b05', custom_fg='#b45309',",
"        )",
"    elif any(k in name for k in ['블루', 'blue', '하늘', '스카이', 'sky', '오션', 'ocean']):",
"        put(",
"            per_bg='#bfdbfe', per_fg='#0f172a',",
"            acad_cell_bg='#eff6ff', acad_cell_fg='#1e3a8a',",
"            query_cell_bg='#dbeafe', query_cell_fg='#1e3a8a',",
"            class_cell_bg='#ffffff', class_cell_fg='#0f172a',",
"            lunch_bg='#eff6ff', lunch_fg='#1e3a8a', custom_fg='#2563eb',",
"        )",
"    else:",
"        t2.setdefault('acad_cell_bg', t2.get('lunch_bg', '#f8fafc'))",
"        t2.setdefault('acad_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('query_cell_bg', t2.get('lunch_bg', '#eff6ff'))",
"        t2.setdefault('query_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('class_cell_bg', t2.get('cell_bg', '#ffffff'))",
"        t2.setdefault('class_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('lunch_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('custom_fg', '#2563eb')",
"    # 공통 제목칸 색상은 모든 행에 동일하게 사용",
"    t2['common_per_bg'] = t2.get('per_bg', '#dbeafe')",
"    t2['common_per_fg'] = t2.get('per_fg', '#0f172a')",
"    return t2",
HELPER_END,
]) + "\n"

CSS_BLOCK = "\n".join([
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step107: 제목 크기/위치. 달력은 건드리지 않음 */",
"    .header-container {{",
"        margin-top: 18px !important;",
"        margin-bottom: 2px !important;",
"        padding-bottom: 0 !important;",
"        min-height: 30px !important;",
"        overflow: visible !important;",
"    }}",
"    .step99-header-title, .step69-title-main, .header-container b {{",
"        font-size: 18px !important;",
"        line-height: 1.35 !important;",
"    }}",
"    .step99-header-teacher, .step69-title-teacher {{",
"        font-size: 12px !important;",
"    }}",
"    /* Step107: 왼쪽 제목칸은 파트별 채우기 제외. 현재교시 강조와 충돌 방지 */",
"    table.mobile-table td:first-child {{",
"        background-color: {t.get('common_per_bg', t.get('per_bg', '#dbeafe'))} !important;",
"        color: {t.get('common_per_fg', t.get('per_fg', '#0f172a'))} !important;",
"    }}",
"    table.mobile-table td:first-child * {{",
"        background: transparent !important;",
"        background-color: transparent !important;",
"        color: inherit !important;",
"    }}",
"    /* Step107: 본문 칸만 학사일정/조회/수업으로 구분 */",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) {{",
"        background-color: {t.get('acad_cell_bg', '#e2e8f0')} !important;",
"        color: {t.get('acad_cell_fg', '#1e293b')} !important;",
"    }}",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) * {{",
"        background: transparent !important;",
"        background-color: transparent !important;",
"        color: inherit !important;",
"    }}",
"    table.mobile-table tr:nth-child(3) td:not(:first-child) {{",
"        background-color: {t.get('query_cell_bg', '#dbeafe')} !important;",
"        color: {t.get('query_cell_fg', '#1e3a8a')} !important;",
"    }}",
"    table.mobile-table tr:nth-child(3) td:not(:first-child) * {{",
"        background: transparent !important;",
"        background-color: transparent !important;",
"        color: inherit !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step107 모던 다크 가독성 최종 보정 + 제목 위치/크기")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step107_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    text = strip_block(text, HELPER_BEGIN, HELPER_END)
    text = strip_block(text, CSS_BEGIN, CSS_END)
    text = re.sub(r"\n\s*t\s*=\s*step107_final_section_colors\(t\)\s*", "\n", text)

    marker = "t = themes[st.session_state.theme_idx]"
    if marker not in text:
        print("[오류] t = themes[st.session_state.theme_idx] 줄을 찾지 못했습니다.")
        return 1

    text = text.replace(marker, HELPER_BLOCK + "\n" + marker, 1)

    apply_candidates = [
        "t = step106_section_theme(t)",
        "t = step105_final_readability(t)",
        "t = step103_theme(t)",
        "t = step99_apply_viewer_theme_palette(t)",
    ]
    applied = False
    for cand in apply_candidates:
        if cand in text:
            text = text.replace(cand, cand + "\nt = step107_final_section_colors(t)", 1)
            applied = True
            break
    if not applied:
        text = text.replace(marker, marker + "\nt = step107_final_section_colors(t)", 1)
    print("[수정] Step107 최종 색상 보정 적용")

    # 왼쪽 제목칸 로직: 모든 행에서 공통 색상. 단, 현재교시 강조는 기존 hl_per 사용.
    p_block_pattern = re.compile(
        r"        if period == \"학사일정\":\n"
        r"            p_bg = .*?\n"
        r"            p_fg = .*?\n"
        r"        elif period == \"조회\":\n"
        r"            p_bg = .*?\n"
        r"            p_fg = .*?\n"
        r"        elif period == \"점심\":\n"
        r"            p_bg = .*?\n"
        r"            p_fg = .*?\n"
        r"        else:\n"
        r"            p_bg = .*?\n"
        r"            p_fg = .*?\n",
        re.S,
    )
    p_repl = (
        "        if period == \"학사일정\":\n"
        "            p_bg = t.get(\"common_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))\n"
        "            p_fg = t.get(\"common_per_fg\", t.get(\"per_fg\", \"#0f172a\"))\n"
        "        elif period == \"조회\":\n"
        "            p_bg = t.get(\"hl_per\", t.get(\"common_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))) if (is_current_week and active_row_idx == row_idx) else t.get(\"common_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))\n"
        "            p_fg = t.get(\"button_primary_fg\", \"#ffffff\") if (is_current_week and active_row_idx == row_idx) else t.get(\"common_per_fg\", t.get(\"per_fg\", \"#0f172a\"))\n"
        "        elif period == \"점심\":\n"
        "            p_bg = t.get(\"common_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))\n"
        "            p_fg = t.get(\"common_per_fg\", t.get(\"per_fg\", \"#0f172a\"))\n"
        "        else:\n"
        "            p_bg = t.get(\"hl_per\", t.get(\"common_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))) if (is_current_week and active_row_idx == row_idx) else t.get(\"common_per_bg\", t.get(\"per_bg\", \"#dbeafe\"))\n"
        "            p_fg = t.get(\"button_primary_fg\", \"#ffffff\") if (is_current_week and active_row_idx == row_idx) else t.get(\"common_per_fg\", t.get(\"per_fg\", \"#0f172a\"))\n"
    )
    text, n_p = p_block_pattern.subn(p_repl, text, count=1)
    print("[수정] 왼쪽 제목칸 색상 로직: 공통색 + 현재교시 강조만 유지" if n_p else "[주의] 왼쪽 제목칸 로직을 찾지 못했습니다.")

    # 본문 셀 로직: 학사/조회/수업 본문만 구분
    cell_pattern = re.compile(
        r"            if period == \"학사일정\":\n"
        r"                bg = .*?\n"
        r"                fg = .*?\n"
        r"            elif period == \"조회\":\n"
        r"                bg = .*?\n"
        r"                fg = .*?\n"
        r"            elif period == \"점심\":\n"
        r"                bg = .*?\n"
        r"                fg = .*?\n"
        r"            else:\n"
        r"                bg = .*?\n"
        r"                fg = .*?\n"
        r"            deco = .*?\n"
        r"            if is_strike:\n"
        r"                fg = .*?\n"
        r"            elif custom_color:\n"
        r"                fg = custom_color\n"
        r"            elif is_custom:\n"
        r"                fg = .*?\n",
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
    print("[수정] 본문 셀 색상 로직: 학사/조회/수업 구분 유지" if n_cell else "[주의] 본문 셀 색상 로직을 찾지 못했습니다.")

    # CSS is a final override; place after Step106 if available.
    if "# >>> STEP106_SECTION_THEME_CSS_END" in text:
        text = text.replace("# >>> STEP106_SECTION_THEME_CSS_END", "# >>> STEP106_SECTION_THEME_CSS_END\n" + CSS_BLOCK, 1)
    elif "# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END" in text:
        text = text.replace("# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END", "# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END\n" + CSS_BLOCK, 1)
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
    else:
        text += "\n" + CSS_BLOCK
    print("[수정] Step107 최종 CSS 삽입")

    tmp = APP.with_suffix(".step107_test.py")
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
    print("[완료] Step107 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

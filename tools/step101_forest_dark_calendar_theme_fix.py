
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step101_backups"

PAL_BEGIN = "# >>> STEP101_THEME_PALETTE_BEGIN"
PAL_END = "# >>> STEP101_THEME_PALETTE_END"
CSS_BEGIN = "# >>> STEP101_CALENDAR_TABLE_CSS_BEGIN"
CSS_END = "# >>> STEP101_CALENDAR_TABLE_CSS_END"

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

PALETTE_BLOCK = "\n".join([
PAL_BEGIN,
"def step101_apply_named_theme_palette(theme):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', '')).lower()",
"    def put(**kw):",
"        t2.update(kw)",
"    if any(k in name for k in ['다크', 'dark', '블랙', 'black', 'night', '나이트']):",
"        put(bg='#1f2937', top='#111827', grid='#64748b', head_bg='#334155', head_fg='#f8fafc', per_bg='#475569', per_fg='#f8fafc', cell_bg='#0f172a', cell_fg='#e5e7eb', lunch_bg='#1e293b', hl_per='#ef4444', hl_cell='#facc15', text='#f8fafc', table_shell='#020617', button_primary_bg='#dc2626', button_primary_fg='#ffffff', button_secondary_bg='#1f2937', button_secondary_fg='#f8fafc', button_border='#64748b')",
"    elif any(k in name for k in ['포레스트', 'forest', '숲', '그린', 'green', '초록', '민트', 'mint', '세이지', 'sage', '올리브', 'olive']):",
"        put(bg='#f1fbf4', top='#dff3e6', grid='#73b887', head_bg='#dff3e6', head_fg='#0f3d24', per_bg='#c7e9d1', per_fg='#0f3d24', cell_bg='#fbfffc', cell_fg='#0f3d24', lunch_bg='#edf8f0', hl_per='#2e7d32', hl_cell='#d9f99d', text='#0f3d24', table_shell='#dff3e6', button_primary_bg='#2e7d32', button_primary_fg='#ffffff', button_secondary_bg='#f1fbf4', button_secondary_fg='#0f3d24', button_border='#73b887')",
"    elif any(k in name for k in ['핑크', 'pink', '러블리', '로즈', 'rose']):",
"        put(bg='#fff7fb', top='#ffe4ef', grid='#f9a8c7', head_bg='#ffe4ef', head_fg='#831843', per_bg='#fbcfe8', per_fg='#831843', cell_bg='#fffafd', cell_fg='#831843', lunch_bg='#fff1f5', hl_per='#fb7185', hl_cell='#fce7f3', text='#831843', table_shell='#ffe4ef', button_primary_bg='#fb7185', button_primary_fg='#ffffff', button_secondary_bg='#fff7fb', button_secondary_fg='#831843', button_border='#f9a8d4')",
"    elif any(k in name for k in ['웜', '파스텔', '베이지', 'beige', '브라운', 'brown', '카페', '라떼']):",
"        put(bg='#fffaf0', top='#f6e7c9', grid='#d6b77d', head_bg='#f4e0b8', head_fg='#3f2d12', per_bg='#ead2a0', per_fg='#3f2d12', cell_bg='#fffdf6', cell_fg='#3f2d12', lunch_bg='#fff7e6', hl_per='#d97706', hl_cell='#fde68a', text='#3f2d12', table_shell='#f6e7c9', button_primary_bg='#f59e0b', button_primary_fg='#3f2d12', button_secondary_bg='#fff7e6', button_secondary_fg='#3f2d12', button_border='#d6b77d')",
"    elif any(k in name for k in ['블루', 'blue', '하늘', '스카이', 'sky', '오션', 'ocean']):",
"        put(bg='#f5fbff', top='#dbeafe', grid='#7db2f0', head_bg='#dbeafe', head_fg='#0f172a', per_bg='#bfdbfe', per_fg='#0f172a', cell_bg='#ffffff', cell_fg='#0f172a', lunch_bg='#eff6ff', hl_per='#2563eb', hl_cell='#dbeafe', text='#0f172a', table_shell='#dbeafe', button_primary_bg='#2563eb', button_primary_fg='#ffffff', button_secondary_bg='#f8fbff', button_secondary_fg='#1e3a8a', button_border='#93c5fd')",
"    elif any(k in name for k in ['퍼플', 'purple', '보라', '라벤더', 'lavender']):",
"        put(bg='#faf5ff', top='#ede9fe', grid='#c4b5fd', head_bg='#ede9fe', head_fg='#3b0764', per_bg='#ddd6fe', per_fg='#3b0764', cell_bg='#fffbff', cell_fg='#3b0764', lunch_bg='#f5f3ff', hl_per='#8b5cf6', hl_cell='#ede9fe', text='#3b0764', table_shell='#ede9fe', button_primary_bg='#8b5cf6', button_primary_fg='#ffffff', button_secondary_bg='#faf5ff', button_secondary_fg='#3b0764', button_border='#c4b5fd')",
"    else:",
"        # 알 수 없는 테마는 기존 색을 존중하되, 시간표가 안 보이지 않도록 최소 대비만 보정",
"        t2.setdefault('grid', '#94a3b8')",
"        t2.setdefault('head_bg', t2.get('top', '#e2e8f0'))",
"        t2.setdefault('head_fg', t2.get('text', '#0f172a'))",
"        t2.setdefault('per_bg', t2.get('top', '#e2e8f0'))",
"        t2.setdefault('per_fg', t2.get('text', '#0f172a'))",
"        t2.setdefault('cell_bg', '#ffffff')",
"        t2.setdefault('cell_fg', '#0f172a')",
"        t2.setdefault('lunch_bg', '#f8fafc')",
"        t2.setdefault('hl_per', '#2563eb')",
"        t2.setdefault('hl_cell', '#dbeafe')",
"        t2.setdefault('button_primary_bg', t2.get('hl_per', '#2563eb'))",
"        t2.setdefault('button_primary_fg', '#ffffff')",
"        t2.setdefault('button_secondary_bg', t2.get('top', '#ffffff'))",
"        t2.setdefault('button_secondary_fg', t2.get('text', '#0f172a'))",
"        t2.setdefault('button_border', t2.get('grid', '#94a3b8'))",
"        t2.setdefault('table_shell', t2.get('top', '#e2e8f0'))",
"    t2['acad_per_bg'] = t2.get('per_bg', '#dbeafe')",
"    t2['acad_per_fg'] = t2.get('per_fg', '#0f172a')",
"    t2['acad_cell_bg'] = t2.get('lunch_bg', '#f8fafc')",
"    t2['acad_cell_fg'] = t2.get('cell_fg', '#0f172a')",
"    return t2",
"",
"themes = [step101_apply_named_theme_palette(th) for th in themes]",
PAL_END,
]) + "\n"

CSS_BLOCK = "\n".join([
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step101: 달력 칸을 충분히 넓히고 popover 화살표를 숨김 */",
"    div[data-testid='stHorizontalBlock'] svg {{",
"        display: none !important;",
"        visibility: hidden !important;",
"        width: 0 !important;",
"        height: 0 !important;",
"        min-width: 0 !important;",
"        margin: 0 !important;",
"        padding: 0 !important;",
"    }}",
"    div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button {{",
"        min-width: 72px !important;",
"        padding-left: 8px !important;",
"        padding-right: 8px !important;",
"        justify-content: center !important;",
"        text-align: center !important;",
"        color: {t.get('button_secondary_fg', t.get('text', '#0f172a'))} !important;",
"    }}",
"    div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button p {{",
"        width: 100% !important;",
"        text-align: center !important;",
"        white-space: nowrap !important;",
"        word-break: keep-all !important;",
"        overflow-wrap: normal !important;",
"        margin: 0 !important;",
"        line-height: 1.2 !important;",
"    }}",
"    /* Step101: 표 색상/글자색을 현재 테마 팔레트와 일치 */",
"    div:has(> table.mobile-table) {{",
"        background: {t.get('table_shell', t.get('grid', '#e2e8f0'))} !important;",
"        border-color: {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table {{",
"        background-color: {t.get('cell_bg', '#ffffff')} !important;",
"        border-color: {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table th {{",
"        background-color: {t.get('head_bg', '#dbeafe')} !important;",
"        color: {t.get('head_fg', '#0f172a')} !important;",
"        border-color: {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table td {{",
"        border-color: {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table td:first-child {{",
"        background-color: {t.get('per_bg', '#dbeafe')} !important;",
"        color: {t.get('per_fg', '#0f172a')} !important;",
"    }}",
"    table.mobile-table td:not(:first-child) {{",
"        background-color: {t.get('cell_bg', '#ffffff')} !important;",
"    }}",
"    table.mobile-table td:not(:first-child) > div {{",
"        max-width: 100% !important;",
"        box-sizing: border-box !important;",
"        overflow-wrap: anywhere !important;",
"        word-break: keep-all !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step101 포레스트/다크 테마 팔레트 + 달력 버튼 보정")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step101_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    # 이전 Step100/100b/101 잔여물 제거. Step99의 성공 항목은 유지.
    text = strip_block(text, "# >>> STEP100_THEME_FORCE_HELPER_BEGIN", "# >>> STEP100_THEME_FORCE_HELPER_END")
    text = strip_block(text, "# >>> STEP100_CALENDAR_TABLE_FORCE_CSS_BEGIN", "# >>> STEP100_CALENDAR_TABLE_FORCE_CSS_END")
    text = strip_block(text, "# >>> STEP100B_FORCE_THEME_HELPER_BEGIN", "# >>> STEP100B_FORCE_THEME_HELPER_END")
    text = strip_block(text, "# >>> STEP100B_CALENDAR_TABLE_CSS_BEGIN", "# >>> STEP100B_CALENDAR_TABLE_CSS_END")
    text = strip_block(text, PAL_BEGIN, PAL_END)
    text = strip_block(text, CSS_BEGIN, CSS_END)
    text = re.sub(r"\n\s*t\s*=\s*step100_force_theme_palette\(t,\s*st\.session_state\.theme_idx\)\s*", "\n", text)
    text = re.sub(r"\n\s*t\s*=\s*step100b_force_viewer_palette\(t,\s*st\.session_state\.theme_idx\)\s*", "\n", text)

    # 테마 리스트 정의 뒤, t 선택 전에 전체 themes를 이름 기반으로 보정
    marker = "t = themes[st.session_state.theme_idx]"
    if marker not in text:
        print("[오류] t = themes[st.session_state.theme_idx] 줄을 찾지 못했습니다.")
        return 1
    text = text.replace(marker, PALETTE_BLOCK + "\n" + marker, 1)

    # 상단바 컬럼 비율: 달력 칸을 넓게, 버튼들은 눌리지 않게.
    column_patterns = [
        r"c1,\s*c2,\s*c3,\s*c4,\s*c5,\s*c6,\s*c7,\s*c8,\s*c9\s*=\s*st\.columns\(\s*9\s*\)",
        r"c1,\s*c2,\s*c3,\s*c4,\s*c5,\s*c6,\s*c7,\s*c8,\s*c9\s*=\s*st\.columns\(\s*\[[^\]]+\]\s*,\s*gap=\"small\"\s*\)",
    ]
    new_cols = "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.42, 1.00, 0.42, 1.80, 0.50, 1.00, 1.00, 0.70, 0.78], gap=\"small\")"
    replaced_cols = False
    for pat in column_patterns:
        text2, n = re.subn(pat, new_cols, text, count=1)
        if n:
            text = text2
            replaced_cols = True
            break
    print("[수정] 상단바 컬럼 비율을 재조정했습니다." if replaced_cols else "[주의] 상단바 컬럼 줄을 찾지 못했습니다.")

    # 기존 CSS 블록이 있으면 그 뒤에, 없으면 display_dashboard 직전에 삽입.
    inserted = False
    if "# >>> STEP99_HEADER_TOOLBAR_TABLE_CSS_END" in text:
        text = text.replace("# >>> STEP99_HEADER_TOOLBAR_TABLE_CSS_END", "# >>> STEP99_HEADER_TOOLBAR_TABLE_CSS_END\n" + CSS_BLOCK, 1)
        inserted = True
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
        inserted = True
    else:
        text += "\n" + CSS_BLOCK
    print("[수정] Step101 CSS를 삽입했습니다." if inserted else "[주의] CSS를 파일 끝에 추가했습니다.")

    tmp = APP.with_suffix(".step101_test.py")
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
    print("[완료] Step101 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

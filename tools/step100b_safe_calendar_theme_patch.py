from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step100b_backups"

HELPER_BEGIN = "# >>> STEP100B_FORCE_THEME_HELPER_BEGIN"
HELPER_END = "# >>> STEP100B_FORCE_THEME_HELPER_END"
CSS_BEGIN = "# >>> STEP100B_CALENDAR_TABLE_CSS_BEGIN"
CSS_END = "# >>> STEP100B_CALENDAR_TABLE_CSS_END"

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

HELPER = "\n".join([
HELPER_BEGIN,
"def step100b_force_viewer_palette(theme, theme_idx=0):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', ''))",
"    palettes = [",
"        dict(bg='#1f2937', top='#111827', grid='#64748b', head_bg='#334155', head_fg='#f8fafc', per_bg='#475569', per_fg='#f8fafc', cell_bg='#111827', cell_fg='#e5e7eb', lunch_bg='#1e293b', hl_per='#ef4444', hl_cell='#facc15', table_shell='#020617', button_primary_bg='#dc2626', button_primary_fg='#ffffff', button_secondary_bg='#1f2937', button_secondary_fg='#f8fafc', button_border='#64748b'),",
"        dict(bg='#f5fbff', top='#dbeafe', grid='#7db2f0', head_bg='#dbeafe', head_fg='#0f172a', per_bg='#bfdbfe', per_fg='#0f172a', cell_bg='#ffffff', cell_fg='#0f172a', lunch_bg='#eff6ff', hl_per='#2563eb', hl_cell='#dbeafe', table_shell='#dbeafe', button_primary_bg='#2563eb', button_primary_fg='#ffffff', button_secondary_bg='#f8fbff', button_secondary_fg='#1e3a8a', button_border='#93c5fd'),",
"        dict(bg='#fff7fb', top='#ffe4ef', grid='#f9a8c7', head_bg='#ffe4ef', head_fg='#831843', per_bg='#fbcfe8', per_fg='#831843', cell_bg='#fffafd', cell_fg='#831843', lunch_bg='#fff1f5', hl_per='#fb7185', hl_cell='#fce7f3', table_shell='#ffe4ef', button_primary_bg='#fb7185', button_primary_fg='#ffffff', button_secondary_bg='#fff7fb', button_secondary_fg='#831843', button_border='#f9a8d4'),",
"        dict(bg='#fffaf0', top='#f6e7c9', grid='#d6b77d', head_bg='#f4e0b8', head_fg='#3f2d12', per_bg='#ead2a0', per_fg='#3f2d12', cell_bg='#fffdf6', cell_fg='#3f2d12', lunch_bg='#fff7e6', hl_per='#d97706', hl_cell='#fde68a', table_shell='#f6e7c9', button_primary_bg='#f59e0b', button_primary_fg='#3f2d12', button_secondary_bg='#fff7e6', button_secondary_fg='#3f2d12', button_border='#d6b77d'),",
"        dict(bg='#f0fdfa', top='#ccfbf1', grid='#5eead4', head_bg='#ccfbf1', head_fg='#064e3b', per_bg='#99f6e4', per_fg='#064e3b', cell_bg='#f8fffd', cell_fg='#064e3b', lunch_bg='#ecfdf5', hl_per='#14b8a6', hl_cell='#a7f3d0', table_shell='#ccfbf1', button_primary_bg='#14b8a6', button_primary_fg='#ffffff', button_secondary_bg='#f0fdfa', button_secondary_fg='#064e3b', button_border='#5eead4'),",
"        dict(bg='#f8fafc', top='#e2e8f0', grid='#94a3b8', head_bg='#e2e8f0', head_fg='#0f172a', per_bg='#cbd5e1', per_fg='#0f172a', cell_bg='#ffffff', cell_fg='#0f172a', lunch_bg='#f8fafc', hl_per='#475569', hl_cell='#e2e8f0', table_shell='#e2e8f0', button_primary_bg='#475569', button_primary_fg='#ffffff', button_secondary_bg='#f8fafc', button_secondary_fg='#0f172a', button_border='#94a3b8'),",
"    ]",
"    if '다크' in name:",
"        p = palettes[0]",
"    elif ('핑크' in name) or ('러블리' in name) or ('로즈' in name):",
"        p = palettes[2]",
"    elif ('웜' in name) or ('파스텔' in name) or ('베이지' in name):",
"        p = palettes[3]",
"    elif ('민트' in name) or ('그린' in name) or ('초록' in name):",
"        p = palettes[4]",
"    elif ('블루' in name) or ('하늘' in name) or ('스카이' in name):",
"        p = palettes[1]",
"    else:",
"        try:",
"            p = palettes[int(theme_idx) % len(palettes)]",
"        except Exception:",
"            p = palettes[1]",
"    t2.update(p)",
"    t2['text'] = p.get('cell_fg', t2.get('text', '#0f172a'))",
"    t2['acad_per_bg'] = p.get('per_bg')",
"    t2['acad_per_fg'] = p.get('per_fg')",
"    t2['acad_cell_bg'] = p.get('lunch_bg')",
"    t2['acad_cell_fg'] = p.get('cell_fg')",
"    return t2",
HELPER_END,
]) + "\n"

CSS = "\n".join([
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step100b: 달력 popover만 글자 오버레이로 정확히 중앙 정렬 */",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button {{",
"        position: relative !important;",
"        display: flex !important;",
"        align-items: center !important;",
"        justify-content: center !important;",
"        text-align: center !important;",
"        overflow: hidden !important;",
"        color: transparent !important;",
"        padding-left: 0 !important;",
"        padding-right: 0 !important;",
"    }}",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button::after {{",
"        content: '달력';",
"        position: absolute !important;",
"        inset: 0 !important;",
"        display: flex !important;",
"        align-items: center !important;",
"        justify-content: center !important;",
"        text-align: center !important;",
"        color: {t.get('button_secondary_fg', t.get('text', '#0f172a'))} !important;",
"        font-size: 14px !important;",
"        font-weight: 700 !important;",
"        line-height: 1 !important;",
"        pointer-events: none !important;",
"    }}",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button[kind='primary']::after {{",
"        color: {t.get('button_primary_fg', '#ffffff')} !important;",
"    }}",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button svg,",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button [data-testid*='Icon'],",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button [class*='Icon'],",
"    div[data-testid='stHorizontalBlock'] > div:nth-child(4) div[data-testid='stPopover'] > button [class*='icon'] {{",
"        display: none !important;",
"        visibility: hidden !important;",
"        width: 0 !important;",
"        min-width: 0 !important;",
"        height: 0 !important;",
"        margin: 0 !important;",
"        padding: 0 !important;",
"        opacity: 0 !important;",
"    }}",
"    /* Step100b: 시간표 테마 강제 동조 */",
"    div:has(> table.mobile-table) {{",
"        background: {t.get('table_shell', t.get('grid', '#e2e8f0'))} !important;",
"        border: 1px solid {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table {{",
"        background-color: {t.get('cell_bg', '#ffffff')} !important;",
"        border: 1px solid {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table th {{",
"        background-color: {t.get('head_bg', '#dbeafe')} !important;",
"        color: {t.get('head_fg', '#0f172a')} !important;",
"        border-color: {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table td {{",
"        border-color: {t.get('grid', '#94a3b8')} !important;",
"    }}",
"    table.mobile-table tr td:first-child {{",
"        background-color: {t.get('per_bg', '#dbeafe')} !important;",
"        color: {t.get('per_fg', '#0f172a')} !important;",
"    }}",
"    table.mobile-table tr td:not(:first-child) {{",
"        background-color: {t.get('cell_bg', '#ffffff')} !important;",
"    }}",
"    table.mobile-table tr td:not(:first-child) > div {{",
"        max-width: 100% !important;",
"        overflow-wrap: anywhere !important;",
"        word-break: keep-all !important;",
"        box-sizing: border-box !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step100b 달력/시간표 테마 안전 재패치")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step100b_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    # 이전 Step100/100b 흔적 제거
    text = strip_block(text, "# >>> STEP100_THEME_FORCE_HELPER_BEGIN", "# >>> STEP100_THEME_FORCE_HELPER_END")
    text = strip_block(text, "# >>> STEP100_CALENDAR_TABLE_FORCE_CSS_BEGIN", "# >>> STEP100_CALENDAR_TABLE_FORCE_CSS_END")
    text = strip_block(text, HELPER_BEGIN, HELPER_END)
    text = strip_block(text, CSS_BEGIN, CSS_END)
    text = re.sub(r"\n\s*t\s*=\s*step100_force_theme_palette\(t,\s*st\.session_state\.theme_idx\)\s*", "\n", text)
    text = re.sub(r"\n\s*t\s*=\s*step100b_force_viewer_palette\(t,\s*st\.session_state\.theme_idx\)\s*", "\n", text)

    # 혹시 남은 깨진 한 줄 제거
    text = "\n".join(
        line for line in text.split("\n")
        if "def # >>> STEP100" not in line
    )

    marker = "t = themes[st.session_state.theme_idx]"
    if marker not in text:
        print("[오류] 테마 선택 기준 줄을 찾지 못했습니다.")
        return 1

    text = text.replace(marker, HELPER + "\n" + marker, 1)

    if "t = step99_apply_viewer_theme_palette(t)" in text:
        text = text.replace(
            "t = step99_apply_viewer_theme_palette(t)",
            "t = step99_apply_viewer_theme_palette(t)\nt = step100b_force_viewer_palette(t, st.session_state.theme_idx)",
            1,
        )
    else:
        text = text.replace(marker, marker + "\nt = step100b_force_viewer_palette(t, st.session_state.theme_idx)", 1)

    old_patterns = [
        "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(9)",
        "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.52, 1.05, 0.52, 1.18, 0.62, 1.02, 1.02, 0.74, 0.82], gap=\"small\")",
        "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.48, 1.05, 0.48, 1.42, 0.58, 1.02, 1.02, 0.72, 0.78], gap=\"small\")",
    ]
    new_cols = "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.48, 1.05, 0.48, 1.48, 0.58, 1.02, 1.02, 0.72, 0.78], gap=\"small\")"
    replaced = False
    for old in old_patterns:
        if old in text:
            text = text.replace(old, new_cols, 1)
            replaced = True
            break
    print("[수정] 상단바 컬럼 비율 적용" if replaced else "[주의] 상단바 컬럼 줄을 찾지 못했습니다.")

    # CSS는 display_dashboard() 호출 직전에 넣는 것이 가장 안전함.
    dashboard_call = "\ndisplay_dashboard()"
    if dashboard_call in text:
        text = text.replace(dashboard_call, "\n" + CSS + "\ndisplay_dashboard()", 1)
        print("[수정] display_dashboard() 직전에 Step100b CSS를 삽입했습니다.")
    else:
        text += "\n" + CSS
        print("[주의] display_dashboard() 호출부를 찾지 못해 파일 끝에 CSS를 추가했습니다.")

    tmp = APP.with_suffix(".step100b_test.py")
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
    print("[완료] Step100b 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

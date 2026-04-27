
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step99_backups"

HELPER_BEGIN = "# >>> STEP99_THEME_HELPER_BEGIN"
HELPER_END = "# >>> STEP99_THEME_HELPER_END"
CSS_BEGIN = "# >>> STEP99_HEADER_TOOLBAR_TABLE_CSS_BEGIN"
CSS_END = "# >>> STEP99_HEADER_TOOLBAR_TABLE_CSS_END"

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

def compile_file(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

HELPER_LINES = [
HELPER_BEGIN,
"def step99_apply_viewer_theme_palette(theme):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', ''))",
"    def put(**kwargs):",
"        t2.update(kwargs)",
"    if '다크' in name:",
"        put(bg='#1f2937', top='#111827', grid='#4b5563', head_bg='#374151', head_fg='#f9fafb', per_bg='#374151', per_fg='#f9fafb', cell_bg='#111827', cell_fg='#f9fafb', lunch_bg='#1f2937', hl_per='#ef4444', hl_cell='#facc15', acad_per_bg='#334155', acad_per_fg='#f8fafc', acad_cell_bg='#0f172a', acad_cell_fg='#e5e7eb', button_primary_bg='#dc2626', button_primary_fg='#ffffff', button_secondary_bg='#262626', button_secondary_fg='#f8fafc', button_border='#525252', table_shell='#262626')",
"    elif ('핑크' in name) or ('러블리' in name) or ('로즈' in name):",
"        put(bg='#fff7fb', top='#ffe4ef', grid='#f9a8c7', head_bg='#ffe4ef', head_fg='#7f1d1d', per_bg='#fbcfe8', per_fg='#7f1d1d', cell_bg='#fffafd', cell_fg='#7f1d1d', lunch_bg='#fff1f5', hl_per='#fb7185', hl_cell='#fce7f3', acad_per_bg='#f9a8d4', acad_per_fg='#7f1d1d', acad_cell_bg='#fff1f8', acad_cell_fg='#831843', button_primary_bg='#fb7185', button_primary_fg='#ffffff', button_secondary_bg='#fff7fb', button_secondary_fg='#831843', button_border='#f9a8d4', table_shell='#ffe4ef')",
"    elif ('웜' in name) or ('파스텔' in name) or ('베이지' in name):",
"        put(bg='#fffaf0', top='#f6e7c9', grid='#d6b77d', head_bg='#f4e0b8', head_fg='#3f2d12', per_bg='#ead2a0', per_fg='#3f2d12', cell_bg='#fffdf6', cell_fg='#3f2d12', lunch_bg='#fff7e6', hl_per='#d97706', hl_cell='#fde68a', acad_per_bg='#e7c98c', acad_per_fg='#3f2d12', acad_cell_bg='#fff8e1', acad_cell_fg='#5f3b05', button_primary_bg='#f59e0b', button_primary_fg='#3f2d12', button_secondary_bg='#fff7e6', button_secondary_fg='#3f2d12', button_border='#d6b77d', table_shell='#f6e7c9')",
"    elif ('민트' in name) or ('그린' in name) or ('초록' in name):",
"        put(bg='#f0fdfa', top='#ccfbf1', grid='#5eead4', head_bg='#ccfbf1', head_fg='#064e3b', per_bg='#99f6e4', per_fg='#064e3b', cell_bg='#f8fffd', cell_fg='#064e3b', lunch_bg='#ecfdf5', hl_per='#14b8a6', hl_cell='#a7f3d0', acad_per_bg='#5eead4', acad_per_fg='#064e3b', acad_cell_bg='#ecfeff', acad_cell_fg='#134e4a', button_primary_bg='#14b8a6', button_primary_fg='#ffffff', button_secondary_bg='#f0fdfa', button_secondary_fg='#064e3b', button_border='#5eead4', table_shell='#ccfbf1')",
"    elif ('블루' in name) or ('하늘' in name) or ('스카이' in name):",
"        put(bg='#f5fbff', top='#dbeafe', grid='#93c5fd', head_bg='#dbeafe', head_fg='#0f172a', per_bg='#bfdbfe', per_fg='#0f172a', cell_bg='#ffffff', cell_fg='#0f172a', lunch_bg='#eff6ff', hl_per='#3b82f6', hl_cell='#bfdbfe', acad_per_bg='#bfdbfe', acad_per_fg='#0f172a', acad_cell_bg='#eff6ff', acad_cell_fg='#1e3a8a', button_primary_bg='#2563eb', button_primary_fg='#ffffff', button_secondary_bg='#f8fbff', button_secondary_fg='#1e3a8a', button_border='#93c5fd', table_shell='#dbeafe')",
"    else:",
"        put(grid=t2.get('grid', '#93a4bd'), head_bg=t2.get('head_bg', '#dbeafe'), head_fg=t2.get('head_fg', '#0f172a'), per_bg=t2.get('per_bg', '#dbeafe'), per_fg=t2.get('per_fg', '#0f172a'), cell_bg=t2.get('cell_bg', '#ffffff'), cell_fg=t2.get('cell_fg', '#0f172a'), lunch_bg=t2.get('lunch_bg', '#f8fafc'), hl_per=t2.get('hl_per', '#2563eb'), hl_cell=t2.get('hl_cell', '#fef3c7'), button_primary_bg=t2.get('hl_per', '#2563eb'), button_primary_fg='#ffffff', button_secondary_bg=t2.get('top', '#ffffff'), button_secondary_fg=t2.get('text', '#0f172a'), button_border=t2.get('grid', '#93a4bd'), table_shell=t2.get('top', '#e5edf7'))",
"    t2.setdefault('text', t2.get('cell_fg', '#0f172a'))",
"    t2.setdefault('acad_per_bg', t2.get('per_bg', '#dbeafe'))",
"    t2.setdefault('acad_per_fg', t2.get('per_fg', '#0f172a'))",
"    t2.setdefault('acad_cell_bg', t2.get('lunch_bg', '#f8fafc'))",
"    t2.setdefault('acad_cell_fg', t2.get('cell_fg', '#0f172a'))",
"    return t2",
HELPER_END,
]
THEME_HELPER = "\n".join(HELPER_LINES) + "\n"

CSS_LINES = [
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    .header-container {{ width: min(450px, calc(100vw - 8px)) !important; min-height: 34px !important; height: auto !important; overflow: visible !important; padding: 7px 4px 8px 4px !important; margin: 0 0 6px 0 !important; box-sizing: border-box !important; line-height: 1.35 !important; }}",
"    .step99-header-title {{ font-size: 16px !important; font-weight: 800 !important; line-height: 1.35 !important; color: {t.get('text', '#0f172a')} !important; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; word-break: keep-all !important; }}",
"    .step99-header-teacher {{ font-size: 12px !important; font-weight: 500 !important; opacity: .88 !important; white-space: nowrap !important; }}",
"    div[data-testid='stHorizontalBlock'] {{ align-items: center !important; gap: 4px !important; }}",
"    div[data-testid='stHorizontalBlock'] > div {{ padding-left: 1px !important; padding-right: 1px !important; min-width: 0 !important; }}",
"    div[data-testid='stHorizontalBlock'] .stButton > button, div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button {{ min-height: 42px !important; height: 42px !important; border-radius: 10px !important; padding: 0 6px !important; margin: 0 !important; display: flex !important; align-items: center !important; justify-content: center !important; text-align: center !important; line-height: 1.2 !important; white-space: nowrap !important; word-break: keep-all !important; overflow: visible !important; text-overflow: clip !important; box-sizing: border-box !important; font-size: 14px !important; font-weight: 700 !important; background-color: {t.get('button_secondary_bg', t.get('top', '#ffffff'))} !important; color: {t.get('button_secondary_fg', t.get('text', '#0f172a'))} !important; border: 1px solid {t.get('button_border', t.get('grid', '#93a4bd'))} !important; }}",
"    div[data-testid='stHorizontalBlock'] .stButton > button[kind='primary'] {{ background-color: {t.get('button_primary_bg', t.get('hl_per', '#2563eb'))} !important; color: {t.get('button_primary_fg', '#ffffff')} !important; border: 1px solid {t.get('button_primary_bg', t.get('hl_per', '#2563eb'))} !important; box-shadow: 0 2px 5px rgba(0,0,0,.16) !important; }}",
"    div[data-testid='stHorizontalBlock'] .stButton > button p, div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button p {{ width: 100% !important; margin: 0 !important; line-height: 1.2 !important; text-align: center !important; white-space: nowrap !important; word-break: keep-all !important; overflow: visible !important; text-overflow: clip !important; }}",
"    div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button svg {{ display: none !important; width: 0 !important; height: 0 !important; margin: 0 !important; padding: 0 !important; }}",
"    div:has(> table.mobile-table) {{ background: {t.get('table_shell', t.get('grid', '#e5edf7'))} !important; border-radius: 8px !important; padding: 5px !important; box-shadow: 0 5px 14px rgba(15,23,42,.12), 0 1px 3px rgba(15,23,42,.08) !important; }}",
"    .mobile-table {{ width: 100% !important; table-layout: fixed !important; border-collapse: collapse !important; background-color: {t.get('cell_bg', '#ffffff')} !important; }}",
"    .mobile-table th, .mobile-table td {{ border-color: {t.get('grid', '#93a4bd')} !important; overflow: hidden !important; box-sizing: border-box !important; }}",
"    .mobile-table th {{ background-color: {t.get('head_bg', '#dbeafe')} !important; color: {t.get('head_fg', '#0f172a')} !important; }}",
"    .mobile-table td {{ color: {t.get('cell_fg', '#0f172a')}; }}",
"    .mobile-table td > div {{ max-width: 100% !important; min-width: 0 !important; box-sizing: border-box !important; white-space: normal !important; word-break: keep-all !important; overflow-wrap: anywhere !important; text-align: center !important; }}",
"    .mobile-table .hl-fill-yellow, .mobile-table .hl-fill-yellow * {{ background-color: {t.get('hl_cell', '#fef3c7')} !important; color: #111827 !important; }}",
"    .memo-panel h3 {{ line-height: 1.35 !important; overflow: visible !important; }}",
"    @media (max-width: 520px) {{ .step99-header-title {{ font-size: 15px !important; }} .step99-header-teacher {{ font-size: 11px !important; }} div[data-testid='stHorizontalBlock'] .stButton > button, div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button {{ min-height: 40px !important; height: 40px !important; font-size: 13px !important; padding-left: 4px !important; padding-right: 4px !important; }} }}",
"    </style>",
"    \"\"\" ,",
"    unsafe_allow_html=True,",
")",
CSS_END,
]
DYNAMIC_CSS = "\n".join(CSS_LINES) + "\n"

HEADER_REPLACEMENT = "\n".join([
"u = st.session_state.logged_in_user",
"st.markdown(",
"    f\"<div class='header-container step99-header-container'>\"",
"    f\"<div class='step99-header-title'>🏫 <b>명덕외고 시간표 뷰어</b> \"",
"    f\"<span class='step99-header-teacher'>({html.escape(str(u))} 선생님)</span></div>\"",
"    f\"</div>\",",
"    unsafe_allow_html=True,",
")",
"",
]) + DYNAMIC_CSS

def main() -> int:
    print("=" * 60)
    print("Step99 웹뷰어 상단바/테마 정밀 패치 시작")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step99_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    text = strip_block(text, HELPER_BEGIN, HELPER_END)
    text = strip_block(text, CSS_BEGIN, CSS_END)
    text = re.sub(r"\n\s*t\s*=\s*step99_apply_viewer_theme_palette\(t\)\s*\n", "\n", text)

    marker = "t = themes[st.session_state.theme_idx]"
    if marker not in text:
        print("[오류] t = themes[st.session_state.theme_idx] 위치를 찾지 못했습니다.")
        return 1
    text = text.replace(marker, THEME_HELPER + "\n" + marker + "\nt = step99_apply_viewer_theme_palette(t)", 1)

    old_cols = "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(9)"
    new_cols = "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.52, 1.05, 0.52, 1.18, 0.62, 1.02, 1.02, 0.74, 0.82], gap=\"small\")"
    if old_cols in text:
        text = text.replace(old_cols, new_cols, 1)
        print("[수정] 상단바 컬럼 비율을 조정했습니다.")
    else:
        print("[주의] 기본 st.columns(9) 문장을 찾지 못했습니다. CSS 보정만 적용합니다.")

    header_pattern = re.compile(
        r"u\s*=\s*st\.session_state\.logged_in_user\s*\n"
        r"st\.markdown\(\s*\n?"
        r"\s*f?\"<div class='header-container'.*?"
        r"unsafe_allow_html=True,\s*\n?\)",
        re.S,
    )
    text2, n = header_pattern.subn(HEADER_REPLACEMENT.rstrip(), text, count=1)
    if n == 0:
        print("[주의] 헤더 블록 자동 치환에 실패했습니다. CSS/테마 보정은 적용합니다.")
    else:
        text = text2
        print("[수정] 헤더 제목 렌더링을 줄높이 안전 구조로 교체했습니다.")

    text = text.replace(
        "word-break:keep-all; overflow-wrap:break-word; white-space:normal; padding:2px;",
        "word-break:keep-all; overflow-wrap:anywhere; white-space:normal; padding:2px; box-sizing:border-box; max-width:100%;",
    )

    for src, dst in {
        "달\\n력": "달력", "달\\\\n력": "달력",
        "메\\n모": "메모", "메\\\\n모": "메모",
        "조\\n회": "조회", "조\\\\n회": "조회",
    }.items():
        text = text.replace(src, dst)

    tmp = APP.with_suffix(".step99_test.py")
    write_text(tmp, text)
    ok, err = compile_file(tmp)
    try:
        tmp.unlink(missing_ok=True)
    except Exception:
        pass

    if not ok:
        shutil.copy2(backup, APP)
        print("[오류] 패치 후 문법검사 실패. 원본 백업으로 복원했습니다.")
        print(err)
        return 1

    write_text(APP, text)
    print("[완료] Step99 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

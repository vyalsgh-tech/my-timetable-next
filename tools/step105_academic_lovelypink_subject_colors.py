
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step105_backups"

THEME_BEGIN = "# >>> STEP105_LOVELY_PINK_AND_READABILITY_BEGIN"
THEME_END = "# >>> STEP105_LOVELY_PINK_AND_READABILITY_END"
CSS_BEGIN = "# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_BEGIN"
CSS_END = "# >>> STEP105_ACADEMIC_AND_SUBJECT_COLOR_CSS_END"

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

THEME_BLOCK = "\n".join([
THEME_BEGIN,
"STEP105_LOVELY_PINK_THEME = {",
"    'name': '러블리 핑크',",
"    'bg': '#fff7fb',",
"    'top': '#ffe4ef',",
"    'grid': '#f3a6c4',",
"    'head_bg': '#ffd6e7',",
"    'head_fg': '#831843',",
"    'per_bg': '#fbcfe8',",
"    'per_fg': '#831843',",
"    'cell_bg': '#fffafd',",
"    'cell_fg': '#831843',",
"    'lunch_bg': '#fff1f5',",
"    'hl_per': '#fb7185',",
"    'hl_cell': '#fce7f3',",
"    'text': '#831843',",
"    'table_shell': '#ffe4ef',",
"    'button_primary_bg': '#fb7185',",
"    'button_primary_fg': '#ffffff',",
"    'button_secondary_bg': '#fff7fb',",
"    'button_secondary_fg': '#831843',",
"    'button_border': '#f9a8d4',",
"    'acad_per_bg': '#f9a8d4',",
"    'acad_per_fg': '#831843',",
"    'acad_cell_bg': '#fff1f8',",
"    'acad_cell_fg': '#9d174d',",
"    'custom_fg': '#db2777',",
"}",
"if not any(str(th.get('name', '')) == '러블리 핑크' for th in themes):",
"    themes.append(STEP105_LOVELY_PINK_THEME)",
"",
"def step105_final_readability(theme):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', '')).lower()",
"    def put(**kw):",
"        t2.update(kw)",
"    if any(k in name for k in ['모던 다크', '모노다크', '다크', 'dark', '블랙', 'black', 'night', '나이트']):",
"        put(head_bg='#334155', head_fg='#f8fafc', per_bg='#334155', per_fg='#f8fafc', acad_cell_bg='#111827', acad_cell_fg='#f8fafc', custom_fg='#fbbf24', button_secondary_fg='#f8fafc')",
"    elif any(k in name for k in ['모노톤', '모노', 'mono', 'gray', 'grey', '그레이', '회색']):",
"        put(head_bg='#52525b', head_fg='#ffffff', per_bg='#71717a', per_fg='#ffffff', acad_cell_bg='#f4f4f5', acad_cell_fg='#18181b', custom_fg='#334155', button_secondary_fg='#18181b')",
"    elif any(k in name for k in ['러블리 핑크', '핑크', 'pink', '로즈', 'rose']):",
"        put(acad_cell_bg='#fff1f8', acad_cell_fg='#9d174d', custom_fg='#db2777')",
"    elif any(k in name for k in ['포레스트', 'forest', '숲', '그린', 'green', '초록', '민트', 'mint', '세이지', 'sage', '올리브', 'olive']):",
"        put(acad_cell_bg='#f0fdf4', acad_cell_fg='#14532d', custom_fg='#15803d')",
"    elif any(k in name for k in ['웜', '파스텔', '베이지', 'beige', '브라운', 'brown', '카페', '라떼']):",
"        put(acad_cell_bg='#fff8e1', acad_cell_fg='#5f3b05', custom_fg='#b45309')",
"    elif any(k in name for k in ['블루', 'blue', '하늘', '스카이', 'sky', '오션', 'ocean']):",
"        put(acad_cell_bg='#eff6ff', acad_cell_fg='#1e3a8a', custom_fg='#2563eb')",
"    elif any(k in name for k in ['퍼플', 'purple', '보라', '라벤더', 'lavender']):",
"        put(acad_cell_bg='#f5f3ff', acad_cell_fg='#4c1d95', custom_fg='#7c3aed')",
"    else:",
"        t2.setdefault('acad_cell_bg', t2.get('lunch_bg', '#f8fafc'))",
"        t2.setdefault('acad_cell_fg', t2.get('cell_fg', '#0f172a'))",
"        t2.setdefault('custom_fg', '#2563eb')",
"    return t2",
THEME_END,
]) + "\n"

CSS_BLOCK = "\n".join([
CSS_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    /* Step105: 학사일정 행만 가독성 보정. 달력/상단바/나머지 레이아웃은 건드리지 않음 */",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) {{",
"        background-color: {t.get('acad_cell_bg', t.get('lunch_bg', '#f8fafc'))} !important;",
"        color: {t.get('acad_cell_fg', t.get('cell_fg', '#0f172a'))} !important;",
"    }}",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) div,",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) span,",
"    table.mobile-table tr:nth-child(2) td:not(:first-child) b {{",
"        background: transparent !important;",
"        background-color: transparent !important;",
"        color: {t.get('acad_cell_fg', t.get('cell_fg', '#0f172a'))} !important;",
"    }}",
"    /* Step105: 기존 빨간 기본 사용자 입력/보강 표시색을 테마별 포인트 색상으로 변경 */",
"    table.mobile-table td[style*='#e74c3c'],",
"    table.mobile-table td[style*='rgb(231, 76, 60)'] {{",
"        color: {t.get('custom_fg', '#2563eb')} !important;",
"    }}",
"    table.mobile-table td[style*='#e74c3c'] div,",
"    table.mobile-table td[style*='rgb(231, 76, 60)'] div {{",
"        color: {t.get('custom_fg', '#2563eb')} !important;",
"    }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
CSS_END,
]) + "\n"

def main() -> int:
    print("=" * 60)
    print("Step105 학사일정 가독성 + 러블리 핑크 + 테마별 폰트색")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step105_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    text = strip_block(text, THEME_BEGIN, THEME_END)
    text = strip_block(text, CSS_BEGIN, CSS_END)
    text = re.sub(r"\n\s*t\s*=\s*step105_final_readability\(t\)\s*", "\n", text)

    # 1) 러블리 핑크 테마는 themes 정의 뒤, session_state 초기화 전에 추가
    insert_theme_marker = 'if "theme_idx" not in st.session_state:'
    if insert_theme_marker in text:
        text = text.replace(insert_theme_marker, THEME_BLOCK + "\n" + insert_theme_marker, 1)
        print("[수정] 러블리 핑크 테마 추가 및 최종 가독성 함수 삽입")
    else:
        # fallback: t 선택 전에는 themes가 반드시 존재함
        marker = "t = themes[st.session_state.theme_idx]"
        if marker not in text:
            print("[오류] 테마 삽입 위치를 찾지 못했습니다.")
            return 1
        text = text.replace(marker, THEME_BLOCK + "\n" + marker, 1)
        print("[주의] 기본 삽입 위치를 찾지 못해 t 선택 직전에 삽입")

    # 2) 현재 선택된 테마에 최종 가독성 보정 적용
    apply_after_candidates = [
        "t = step103_theme(t)",
        "t = step102_final_theme_fix(t, st.session_state.theme_idx)",
        "t = step99_apply_viewer_theme_palette(t)",
    ]
    applied = False
    for cand in apply_after_candidates:
        if cand in text:
            text = text.replace(cand, cand + "\nt = step105_final_readability(t)", 1)
            applied = True
            break
    if not applied:
        marker = "t = themes[st.session_state.theme_idx]"
        if marker in text:
            text = text.replace(marker, marker + "\nt = step105_final_readability(t)", 1)
            applied = True
    print("[수정] 선택 테마에 Step105 최종 가독성 보정 적용" if applied else "[주의] t 적용 위치를 찾지 못했습니다.")

    # 3) 기본 빨간색 사용자 입력 색상 자체를 테마별 포인트색으로 교체
    if 'fg = "#e74c3c"' in text:
        text = text.replace('fg = "#e74c3c"', 'fg = t.get("custom_fg", "#e74c3c")')
        print("[수정] 시간표 기본 빨간색을 테마별 포인트 색상으로 변경")
    else:
        print("[안내] fg = \"#e74c3c\" 직접 지정 줄은 찾지 못했습니다. CSS 보정만 적용합니다.")

    # 4) CSS는 Step104 뒤에 넣어 표 채우기 성공 상태를 유지하면서 색만 마지막에 보정
    if "# >>> STEP104_TABLE_CELL_FILL_FIX_END" in text:
        text = text.replace("# >>> STEP104_TABLE_CELL_FILL_FIX_END", "# >>> STEP104_TABLE_CELL_FILL_FIX_END\n" + CSS_BLOCK, 1)
        print("[수정] Step104 뒤에 Step105 CSS 추가")
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + CSS_BLOCK + "\ndisplay_dashboard()", 1)
        print("[주의] Step104 위치를 찾지 못해 display_dashboard 호출 직전에 CSS 추가")
    else:
        text += "\n" + CSS_BLOCK
        print("[주의] 삽입 위치를 찾지 못해 파일 끝에 CSS 추가")

    tmp = APP.with_suffix(".step105_test.py")
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
    print("[완료] Step105 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

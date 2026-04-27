
from pathlib import Path
from datetime import datetime
import re
import shutil
import py_compile
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step103_backups"

HELPER_BEGIN = "# >>> STEP103_STABLE_HELPERS_BEGIN"
HELPER_END = "# >>> STEP103_STABLE_HELPERS_END"
UI_BEGIN = "# >>> STEP103_STABLE_UI_BEGIN"
UI_END = "# >>> STEP103_STABLE_UI_END"

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

HELPERS = "\n".join([
HELPER_BEGIN,
"def step103_theme(theme):",
"    t2 = dict(theme or {})",
"    name = str(t2.get('name', '')).lower()",
"    def put(**kw):",
"        t2.update(kw)",
"    # 모노/다크는 헤더를 절대 하늘색+흰글씨 조합으로 두지 않음",
"    if any(k in name for k in ['모노다크', '모던 다크', '다크', 'dark', '블랙', 'black', 'night', '나이트']):",
"        put(bg='#1f2937', top='#111827', grid='#64748b', head_bg='#334155', head_fg='#f8fafc', per_bg='#334155', per_fg='#f8fafc', cell_bg='#0f172a', cell_fg='#e5e7eb', lunch_bg='#1e293b', hl_per='#ef4444', hl_cell='#facc15', text='#f8fafc', table_shell='#020617', button_primary_bg='#dc2626', button_primary_fg='#ffffff', button_secondary_bg='#1f2937', button_secondary_fg='#f8fafc', button_border='#64748b')",
"    elif any(k in name for k in ['모노톤', '모노', 'mono', 'gray', 'grey', '그레이', '회색']):",
"        put(bg='#f4f5f7', top='#e5e7eb', grid='#71717a', head_bg='#52525b', head_fg='#ffffff', per_bg='#71717a', per_fg='#ffffff', cell_bg='#ffffff', cell_fg='#18181b', lunch_bg='#f4f4f5', hl_per='#3f3f46', hl_cell='#e4e4e7', text='#18181b', table_shell='#d4d4d8', button_primary_bg='#52525b', button_primary_fg='#ffffff', button_secondary_bg='#f4f4f5', button_secondary_fg='#18181b', button_border='#a1a1aa')",
"    elif any(k in name for k in ['포레스트', 'forest', '숲', '그린', 'green', '초록', '민트', 'mint', '세이지', 'sage', '올리브', 'olive']):",
"        put(bg='#f1fbf4', top='#dff3e6', grid='#73b887', head_bg='#dff3e6', head_fg='#0f3d24', per_bg='#c7e9d1', per_fg='#0f3d24', cell_bg='#fbfffc', cell_fg='#0f3d24', lunch_bg='#edf8f0', hl_per='#2e7d32', hl_cell='#d9f99d', text='#0f3d24', table_shell='#dff3e6', button_primary_bg='#2e7d32', button_primary_fg='#ffffff', button_secondary_bg='#f1fbf4', button_secondary_fg='#0f3d24', button_border='#73b887')",
"    elif any(k in name for k in ['핑크', 'pink', '러블리', '로즈', 'rose']):",
"        put(bg='#fff7fb', top='#ffe4ef', grid='#f9a8c7', head_bg='#ffe4ef', head_fg='#831843', per_bg='#fbcfe8', per_fg='#831843', cell_bg='#fffafd', cell_fg='#831843', lunch_bg='#fff1f5', hl_per='#fb7185', hl_cell='#fce7f3', text='#831843', table_shell='#ffe4ef', button_primary_bg='#fb7185', button_primary_fg='#ffffff', button_secondary_bg='#fff7fb', button_secondary_fg='#831843', button_border='#f9a8d4')",
"    elif any(k in name for k in ['웜', '파스텔', '베이지', 'beige', '브라운', 'brown', '카페', '라떼']):",
"        put(bg='#fffaf0', top='#f6e7c9', grid='#d6b77d', head_bg='#f4e0b8', head_fg='#3f2d12', per_bg='#ead2a0', per_fg='#3f2d12', cell_bg='#fffdf6', cell_fg='#3f2d12', lunch_bg='#fff7e6', hl_per='#d97706', hl_cell='#fde68a', text='#3f2d12', table_shell='#f6e7c9', button_primary_bg='#f59e0b', button_primary_fg='#3f2d12', button_secondary_bg='#fff7e6', button_secondary_fg='#3f2d12', button_border='#d6b77d')",
"    elif any(k in name for k in ['블루', 'blue', '하늘', '스카이', 'sky', '오션', 'ocean']):",
"        put(bg='#f5fbff', top='#dbeafe', grid='#7db2f0', head_bg='#dbeafe', head_fg='#0f172a', per_bg='#bfdbfe', per_fg='#0f172a', cell_bg='#ffffff', cell_fg='#0f172a', lunch_bg='#eff6ff', hl_per='#2563eb', hl_cell='#dbeafe', text='#0f172a', table_shell='#dbeafe', button_primary_bg='#2563eb', button_primary_fg='#ffffff', button_secondary_bg='#f8fbff', button_secondary_fg='#1e3a8a', button_border='#93c5fd')",
"    else:",
"        # 알 수 없는 테마도 헤더 글자 대비가 깨지지 않도록 안전값 보정",
"        t2.setdefault('grid', '#94a3b8')",
"        t2.setdefault('head_bg', t2.get('top', '#e2e8f0'))",
"        t2.setdefault('head_fg', t2.get('text', '#0f172a'))",
"        t2.setdefault('per_bg', t2.get('top', '#e2e8f0'))",
"        t2.setdefault('per_fg', t2.get('text', '#0f172a'))",
"        t2.setdefault('cell_bg', '#ffffff')",
"        t2.setdefault('cell_fg', '#0f172a')",
"        t2.setdefault('button_secondary_fg', t2.get('text', '#0f172a'))",
"    t2['acad_per_bg'] = t2.get('per_bg', '#dbeafe')",
"    t2['acad_per_fg'] = t2.get('per_fg', '#0f172a')",
"    t2['acad_cell_bg'] = t2.get('lunch_bg', '#f8fafc')",
"    t2['acad_cell_fg'] = t2.get('cell_fg', '#0f172a')",
"    return t2",
"",
"def step103_current_clock_info():",
"    try:",
"        now = datetime.now(kst_tz)",
"    except Exception:",
"        now = datetime.now()",
"    m = now.hour * 60 + now.minute",
"    slots = [('조회', 7*60+40, 8*60), ('1교시', 8*60, 8*60+50), ('2교시', 9*60, 9*60+50), ('3교시', 10*60, 10*60+50), ('4교시', 11*60, 11*60+50), ('점심', 11*60+50, 12*60+40), ('5교시', 12*60+40, 13*60+30), ('6교시', 13*60+40, 14*60+30), ('7교시', 14*60+40, 15*60+30)]",
"    label = '수업 전' if m < slots[0][1] else '방과 후'",
"    for idx, (name, start, end) in enumerate(slots):",
"        if start <= m < end:",
"            label = name",
"            break",
"        if idx < len(slots) - 1 and end <= m < slots[idx + 1][1]:",
"            remain = slots[idx + 1][1] - m",
"            label = ('곧 ' + slots[idx + 1][0]) if remain <= 15 else '쉬는시간'",
"            break",
"    return now.strftime('%H:%M'), label",
"",
"def step103_render_memo_html(value):",
"    raw = '' if value is None else str(value)",
"    raw = raw.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '\"')",
"    m = re.fullmatch(r\"\\s*<span\\s+style=['\\\"]\\s*color\\s*:\\s*([^;'\\\"]+)\\s*;?\\s*['\\\"]\\s*>(.*?)</span>\\s*\", raw, flags=re.I | re.S)",
"    if m:",
"        color = m.group(1).strip()",
"        if re.fullmatch(r\"#[0-9a-fA-F]{3,8}|[a-zA-Z]+|rgba?\\([^()]+\\)\", color):",
"            body = html.escape(m.group(2)).replace(chr(10), '<br>')",
"            return f\"<span style='color:{html.escape(color)};'>{body}</span>\"",
"    return html.escape(raw).replace(chr(10), '<br>')",
HELPER_END,
]) + "\n"

UI_BLOCK = "\n".join([
UI_BEGIN,
"st.markdown(",
"    f\"\"\"",
"    <style>",
"    .step103-clock-badge {{ position: fixed !important; top: 16px !important; right: 14px !important; z-index: 9999 !important; min-width: 86px !important; padding: 7px 9px !important; border-radius: 12px !important; text-align: center !important; background: {t.get('button_secondary_bg', t.get('top', '#ffffff'))} !important; color: {t.get('button_secondary_fg', t.get('text', '#0f172a'))} !important; border: 1px solid {t.get('button_border', t.get('grid', '#94a3b8'))} !important; box-shadow: 0 2px 8px rgba(0,0,0,.14) !important; line-height: 1.15 !important; }}",
"    .step103-clock-time {{ font-size: 13px !important; font-weight: 800 !important; }}",
"    .step103-clock-label {{ font-size: 11px !important; margin-top: 2px !important; opacity: .9 !important; }}",
"    table.mobile-table th, table.mobile-table th * {{ background-color: {t.get('head_bg', '#334155')} !important; color: {t.get('head_fg', '#f8fafc')} !important; border-color: {t.get('grid', '#64748b')} !important; }}",
"    table.mobile-table td:first-child, table.mobile-table td:first-child * {{ background-color: {t.get('per_bg', '#334155')} !important; color: {t.get('per_fg', '#f8fafc')} !important; }}",
"    table.mobile-table td:not(:first-child) {{ background-color: {t.get('cell_bg', '#ffffff')} !important; }}",
"    div[data-testid='stHorizontalBlock'] .stButton > button[kind='secondary'], div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button {{ color: {t.get('button_secondary_fg', t.get('text', '#0f172a'))} !important; background-color: {t.get('button_secondary_bg', t.get('top', '#ffffff'))} !important; border-color: {t.get('button_border', t.get('grid', '#94a3b8'))} !important; }}",
"    div[data-testid='stHorizontalBlock'] .stButton > button[kind='secondary'] p, div[data-testid='stHorizontalBlock'] div[data-testid='stPopover'] > button p {{ color: {t.get('button_secondary_fg', t.get('text', '#0f172a'))} !important; }}",
"    div[data-testid='stHorizontalBlock'] .stButton > button[kind='primary'], div[data-testid='stHorizontalBlock'] .stButton > button[kind='primary'] p {{ color: {t.get('button_primary_fg', '#ffffff')} !important; background-color: {t.get('button_primary_bg', t.get('hl_per', '#2563eb'))} !important; }}",
"    </style>",
"    \"\"\",",
"    unsafe_allow_html=True,",
")",
"_step103_time, _step103_label = step103_current_clock_info()",
"st.markdown(f\"<div class='step103-clock-badge'><div class='step103-clock-time'>{_step103_time}</div><div class='step103-clock-label'>{_step103_label}</div></div>\", unsafe_allow_html=True)",
UI_END,
]) + "\n"

CAL_REPLACEMENT = """    with c4:
        if st.button("달력", use_container_width=True, key="calendar_toggle_btn"):
            st.session_state.show_calendar_picker = not st.session_state.get("show_calendar_picker", False)
            safe_fragment_rerun()

        if st.session_state.get("show_calendar_picker", False):
            st.markdown(
                "<div style='font-size:12px; font-weight:bold; margin:4px 0 3px 0;'>날짜 선택</div>",
                unsafe_allow_html=True,
            )
            now_date = datetime.now(kst_tz).date()
            current_view_date = now_date + timedelta(weeks=st.session_state.week_offset)
            selected_date = st.date_input(
                "날짜 선택",
                value=current_view_date,
                label_visibility="collapsed",
                key="calendar_picker_step103",
            )

            now_monday = now_date - timedelta(days=now_date.weekday())
            selected_monday = selected_date - timedelta(days=selected_date.weekday())
            diff_weeks = (selected_monday - now_monday).days // 7

            if diff_weeks != st.session_state.week_offset:
                st.session_state.week_offset = diff_weeks
                st.session_state.show_calendar_picker = False
                safe_fragment_rerun()

"""

def main() -> int:
    print("=" * 60)
    print("Step103 표 헤더 직접 대비 보정 + 달력 버튼화")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step103_{ts}.py"
    shutil.copy2(APP, backup)
    print(f"[백업 완료] {backup}")

    text = read_text(APP).replace("\r\n", "\n").replace("\r", "\n")

    # 이전 실패/보정 블록 정리
    blocks = [
        ("# >>> STEP100_THEME_FORCE_HELPER_BEGIN", "# >>> STEP100_THEME_FORCE_HELPER_END"),
        ("# >>> STEP100_CALENDAR_TABLE_FORCE_CSS_BEGIN", "# >>> STEP100_CALENDAR_TABLE_FORCE_CSS_END"),
        ("# >>> STEP100B_FORCE_THEME_HELPER_BEGIN", "# >>> STEP100B_FORCE_THEME_HELPER_END"),
        ("# >>> STEP100B_CALENDAR_TABLE_CSS_BEGIN", "# >>> STEP100B_CALENDAR_TABLE_CSS_END"),
        ("# >>> STEP101_THEME_PALETTE_BEGIN", "# >>> STEP101_THEME_PALETTE_END"),
        ("# >>> STEP101_CALENDAR_TABLE_CSS_BEGIN", "# >>> STEP101_CALENDAR_TABLE_CSS_END"),
        ("# >>> STEP102_FINAL_HELPERS_BEGIN", "# >>> STEP102_FINAL_HELPERS_END"),
        ("# >>> STEP102_FINAL_CSS_AND_CLOCK_BEGIN", "# >>> STEP102_FINAL_CSS_AND_CLOCK_END"),
        (HELPER_BEGIN, HELPER_END),
        (UI_BEGIN, UI_END),
    ]
    for b, e in blocks:
        text = strip_block(text, b, e)

    for fn in [
        "step100_force_theme_palette",
        "step100b_force_viewer_palette",
        "step102_final_theme_fix",
        "step103_theme",
    ]:
        text = re.sub(rf"\n\s*t\s*=\s*{fn}\(t,\s*st\.session_state\.theme_idx\)\s*", "\n", text)

    # 헬퍼 삽입 및 최종 테마 보정
    marker = "t = themes[st.session_state.theme_idx]"
    if marker not in text:
        print("[오류] t = themes[st.session_state.theme_idx] 줄을 찾지 못했습니다.")
        return 1
    text = text.replace(marker, HELPERS + "\n" + marker, 1)

    if "t = step99_apply_viewer_theme_palette(t)" in text:
        text = text.replace(
            "t = step99_apply_viewer_theme_palette(t)",
            "t = step99_apply_viewer_theme_palette(t)\nt = step103_theme(t)",
            1,
        )
    else:
        text = text.replace(marker, marker + "\nt = step103_theme(t)", 1)

    # 달력 popover를 일반 버튼+date_input으로 교체하여 화살표/세로배치 원인을 제거
    cal_pattern = re.compile(
        r"    with c4:\n"
        r"        with st\.popover\(\"달력\", use_container_width=True\):\n"
        r".*?"
        r"(?=\n    with c5:)",
        re.S,
    )
    text2, n_cal = cal_pattern.subn(CAL_REPLACEMENT, text, count=1)
    if n_cal:
        text = text2
        print("[수정] 달력 popover를 일반 버튼 방식으로 교체했습니다.")
    else:
        print("[주의] 달력 popover 블록을 찾지 못했습니다.")

    # 컬럼 비율: 달력 버튼은 이제 화살표가 없으므로 안정폭만 부여
    col_pat = r"c1,\s*c2,\s*c3,\s*c4,\s*c5,\s*c6,\s*c7,\s*c8,\s*c9\s*=\s*st\.columns\(\s*(?:9|\[[^\]]+\]\s*,\s*gap=\"small\")\s*\)"
    new_cols = "c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns([0.44, 1.00, 0.44, 1.20, 0.54, 1.00, 1.00, 0.72, 0.78], gap=\"small\")"
    text, n_col = re.subn(col_pat, new_cols, text, count=1)
    print("[수정] 상단바 컬럼 비율 재조정" if n_col else "[주의] 상단바 컬럼 줄을 찾지 못했습니다.")

    # 메모 색상 span 렌더링 함수명 정리
    text = text.replace("step102_render_memo_html(text)", "step103_render_memo_html(text)")
    old_memo = 'html.escape(text).replace(chr(10), \'<br>\')'
    if old_memo in text:
        text = text.replace(old_memo, "step103_render_memo_html(text)", 1)
        print("[수정] 메모 색상 span 표시를 실제 색상 표시로 보정했습니다.")

    # UI/시계 블록은 dashboard 정의 직전에 삽입
    dash_def = "@st.fragment\ndef display_dashboard():"
    if dash_def in text:
        text = text.replace(dash_def, UI_BLOCK + "\n" + dash_def, 1)
        print("[수정] 현재시각/대비 CSS를 dashboard 정의 직전에 삽입했습니다.")
    elif "\ndisplay_dashboard()" in text:
        text = text.replace("\ndisplay_dashboard()", "\n" + UI_BLOCK + "\ndisplay_dashboard()", 1)
        print("[주의] dashboard 호출 직전에 UI 블록 삽입")
    else:
        text += "\n" + UI_BLOCK

    tmp = APP.with_suffix(".step103_test.py")
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
    print("[완료] Step103 패치를 적용했습니다.")
    print("다음 실행: python -m streamlit run mobile\\app.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())

from pathlib import Path
from datetime import datetime
import re
import shutil
import sys

ROOT = Path.cwd()
APP = ROOT / 'mobile' / 'app.py'
BACKUP_DIR = ROOT / 'tools' / '_step93_backups'

BEGIN = '# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH BEGIN'
END = '# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH END'

PATCH_BLOCK = r'''
# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH BEGIN
try:
    import streamlit as st
    from datetime import datetime as _step93_datetime
    try:
        from zoneinfo import ZoneInfo as _step93_ZoneInfo
    except Exception:
        _step93_ZoneInfo = None

    def _step93_now_kst():
        if _step93_ZoneInfo:
            return _step93_datetime.now(_step93_ZoneInfo("Asia/Seoul"))
        return _step93_datetime.now()

    def _step93_minutes(dt):
        return dt.hour * 60 + dt.minute

    def _step93_current_label(dt):
        m = _step93_minutes(dt)
        slots = [
            ("조회", 7 * 60 + 40, 8 * 60),
            ("1교시", 8 * 60, 8 * 60 + 50),
            ("2교시", 9 * 60, 9 * 60 + 50),
            ("3교시", 10 * 60, 10 * 60 + 50),
            ("4교시", 11 * 60, 11 * 60 + 50),
            ("점심", 11 * 60 + 50, 12 * 60 + 40),
            ("5교시", 12 * 60 + 40, 13 * 60 + 30),
            ("6교시", 13 * 60 + 40, 14 * 60 + 30),
            ("7교시", 14 * 60 + 40, 15 * 60 + 30),
        ]
        if m < slots[0][1]:
            return "수업 전"
        for i, (name, start, end) in enumerate(slots):
            if start <= m < end:
                return name
            if i < len(slots) - 1:
                next_name, next_start, _ = slots[i + 1]
                if end <= m < next_start:
                    return f"곧 {next_name}" if next_start - m <= 15 else "쉬는시간"
        return "방과 후"

    def _step93_theme_key():
        texts = []
        try:
            texts += [str(v) for v in st.session_state.values()]
        except Exception:
            pass
        try:
            texts += [str(v) for v in st.query_params.values()]
        except Exception:
            pass
        s = " ".join(texts).lower()
        if any(k in s for k in ["pink", "핑크", "러블리", "rose", "lovely"]):
            return "pink"
        if any(k in s for k in ["dark", "다크", "black", "블랙", "night", "밤"]):
            return "dark"
        if any(k in s for k in ["green", "mint", "민트", "초록", "녹색"]):
            return "green"
        if any(k in s for k in ["purple", "violet", "보라", "라벤더"]):
            return "purple"
        if any(k in s for k in ["yellow", "cream", "beige", "노랑", "크림", "베이지"]):
            return "cream"
        return "blue"

    def _step93_palette():
        key = _step93_theme_key()
        palettes = {
            "pink": {
                "border": "#d9a6ae", "header": "#ffe0e6", "sub": "#fff0f3",
                "cell": "#fff8fa", "left": "#ffe8ee", "text": "#3b1f2b",
                "accent": "#ff8fa3", "shadow": "rgba(145, 70, 90, .18)",
            },
            "dark": {
                "border": "#475569", "header": "#1e293b", "sub": "#273449",
                "cell": "#0f172a", "left": "#1e293b", "text": "#e5e7eb",
                "accent": "#93c5fd", "shadow": "rgba(0, 0, 0, .35)",
            },
            "green": {
                "border": "#8fbc9a", "header": "#dff5e6", "sub": "#eefbf2",
                "cell": "#f8fffa", "left": "#e7f7ec", "text": "#14301f",
                "accent": "#54b873", "shadow": "rgba(55, 115, 75, .15)",
            },
            "purple": {
                "border": "#b7a5d9", "header": "#eee7ff", "sub": "#f6f1ff",
                "cell": "#fbf9ff", "left": "#f0e9ff", "text": "#2c2141",
                "accent": "#9b7be8", "shadow": "rgba(95, 70, 150, .16)",
            },
            "cream": {
                "border": "#d9bd78", "header": "#fff2cc", "sub": "#fff8e6",
                "cell": "#fffdf6", "left": "#fff0c2", "text": "#3a2a0b",
                "accent": "#e3a927", "shadow": "rgba(140, 110, 35, .18)",
            },
            "blue": {
                "border": "#8fb0d9", "header": "#e3f0ff", "sub": "#f0f7ff",
                "cell": "#fbfdff", "left": "#e8f3ff", "text": "#0b1f38",
                "accent": "#4f8bf9", "shadow": "rgba(50, 95, 150, .16)",
            },
        }
        return palettes.get(key, palettes["blue"])

    def _step93_table_css():
        p = _step93_palette()
        return f"""
        <style id=\"step93-timetable-theme\">
        html, body {{ margin: 0 !important; padding: 0 !important; background: transparent !important; }}
        table, .timetable, .timetable-table {{
            width: 100% !important;
            table-layout: fixed !important;
            border-collapse: collapse !important;
            border-spacing: 0 !important;
            border: 1px solid {p['border']} !important;
            background: {p['cell']} !important;
            color: {p['text']} !important;
            box-shadow: 0 3px 10px {p['shadow']} !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }}
        th, td {{
            border: 1px solid {p['border']} !important;
            color: {p['text']} !important;
            background: {p['cell']} !important;
            white-space: normal !important;
            word-break: keep-all !important;
            overflow-wrap: anywhere !important;
            word-wrap: break-word !important;
            text-align: center !important;
            vertical-align: middle !important;
            box-sizing: border-box !important;
            max-width: 0 !important;
            padding: 6px 4px !important;
            line-height: 1.25 !important;
        }}
        tr:first-child th, tr:first-child td, thead th {{
            background: {p['header']} !important;
            color: {p['text']} !important;
            font-weight: 800 !important;
        }}
        tr:nth-child(2) th, tr:nth-child(2) td {{ background: {p['sub']} !important; }}
        tr td:first-child, tr th:first-child {{
            background: {p['left']} !important;
            color: {p['text']} !important;
            font-weight: 800 !important;
        }}
        td *, th * {{
            white-space: normal !important;
            word-break: keep-all !important;
            overflow-wrap: anywhere !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}
        [style*=\"red\"], font[color=\"red\"], .red {{ color: #ef4444 !important; }}
        </style>
        """

    # components.html로 표가 렌더링되는 경우, iframe 내부에 테마 CSS를 직접 넣습니다.
    try:
        import streamlit.components.v1 as _step93_components
        if not getattr(_step93_components, "_step93_timetable_patch_applied", False):
            _step93_original_html = _step93_components.html
            def _step93_html(source, *args, **kwargs):
                try:
                    if isinstance(source, str) and ("<table" in source.lower() or "timetable" in source.lower()):
                        source = _step93_table_css() + source
                except Exception:
                    pass
                return _step93_original_html(source, *args, **kwargs)
            _step93_components.html = _step93_html
            _step93_components._step93_timetable_patch_applied = True
    except Exception:
        pass

    _step93_p = _step93_palette()
    _step93_now = _step93_now_kst()
    _step93_time = _step93_now.strftime("%H:%M")
    _step93_label = _step93_current_label(_step93_now)

    st.markdown(f"""
    <style id=\"step93-page-ui-fix\">
    :root {{
        --step93-border: {_step93_p['border']};
        --step93-header: {_step93_p['header']};
        --step93-sub: {_step93_p['sub']};
        --step93-cell: {_step93_p['cell']};
        --step93-left: {_step93_p['left']};
        --step93-text: {_step93_p['text']};
        --step93-accent: {_step93_p['accent']};
        --step93-shadow: {_step93_p['shadow']};
    }}

    /* 제목 잘림 방지 */
    .stApp [data-testid=\"stMarkdownContainer\"],
    .stApp [data-testid=\"stMarkdownContainer\"] * {{
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp [data-testid=\"stMarkdownContainer\"] h1,
    .stApp [data-testid=\"stMarkdownContainer\"] h2,
    .stApp [data-testid=\"stMarkdownContainer\"] h3,
    .stApp [data-testid=\"stMarkdownContainer\"] h4 {{
        line-height: 1.38 !important;
        min-height: 1.45em !important;
        padding-top: 3px !important;
        padding-bottom: 3px !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        white-space: normal !important;
    }}

    /* 상단 버튼: 메모/조회 글자 가림 방지 */
    .stApp [data-testid=\"stButton\"] > button,
    .stApp button[kind] {{
        min-height: 40px !important;
        height: 40px !important;
        padding: 7px 10px !important;
        border-radius: 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: visible !important;
        white-space: nowrap !important;
        line-height: 1.15 !important;
        box-sizing: border-box !important;
    }}
    .stApp [data-testid=\"stButton\"] > button p,
    .stApp button[kind] p,
    .stApp button[kind] span {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.15 !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}

    /* 달력 selectbox: 중앙정렬 + 꺾쇠 제거 */
    .stApp div[data-baseweb=\"select\"] {{
        min-width: 60px !important;
        width: 60px !important;
    }}
    .stApp div[data-baseweb=\"select\"] > div {{
        min-height: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        overflow: visible !important;
        box-sizing: border-box !important;
    }}
    .stApp div[data-baseweb=\"select\"] > div > div {{
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        overflow: visible !important;
    }}
    .stApp div[data-baseweb=\"select\"] [class*=\"ValueContainer\"],
    .stApp div[data-baseweb=\"select\"] [class*=\"SingleValue\"],
    .stApp div[data-baseweb=\"select\"] [class*=\"singleValue\"] {{
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
        position: static !important;
        transform: none !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }}
    .stApp div[data-baseweb=\"select\"] svg,
    .stApp div[data-baseweb=\"select\"] [class*=\"IndicatorsContainer\"],
    .stApp div[data-baseweb=\"select\"] [class*=\"SelectArrow\"],
    .stApp div[data-baseweb=\"select\"] [aria-hidden=\"true\"] {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .stApp div[data-baseweb=\"select\"] input {{
        width: 0 !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* st.markdown 표로 렌더링되는 경우에도 테마 적용 */
    .stApp table {{
        width: 100% !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        border: 1px solid var(--step93-border) !important;
        background: var(--step93-cell) !important;
        color: var(--step93-text) !important;
        box-shadow: 0 3px 10px var(--step93-shadow) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}
    .stApp table th, .stApp table td {{
        border: 1px solid var(--step93-border) !important;
        background: var(--step93-cell) !important;
        color: var(--step93-text) !important;
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        text-align: center !important;
        vertical-align: middle !important;
        max-width: 0 !important;
        padding: 6px 4px !important;
        line-height: 1.25 !important;
        box-sizing: border-box !important;
    }}
    .stApp table tr:first-child th,
    .stApp table tr:first-child td,
    .stApp table thead th {{ background: var(--step93-header) !important; font-weight: 800 !important; }}
    .stApp table tr:nth-child(2) th,
    .stApp table tr:nth-child(2) td {{ background: var(--step93-sub) !important; }}
    .stApp table tr td:first-child,
    .stApp table tr th:first-child {{ background: var(--step93-left) !important; font-weight: 800 !important; }}
    .stApp table td *, .stApp table th * {{
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        max-width: 100% !important;
    }}

    /* 현재시각: JS 없이 Python 렌더링. 새로고침/조작 시 갱신됨 */
    #step93-current-time-badge {{
        position: fixed;
        right: 12px;
        top: 58px;
        z-index: 9999;
        min-width: 88px;
        padding: 7px 9px;
        border-radius: 12px;
        border: 1px solid var(--step93-border);
        background: color-mix(in srgb, var(--step93-cell) 86%, white 14%);
        color: var(--step93-text);
        box-shadow: 0 3px 10px var(--step93-shadow);
        text-align: center;
        backdrop-filter: blur(5px);
    }}
    #step93-current-time-badge .time {{ font-size: 14px; font-weight: 800; line-height: 1.1; }}
    #step93-current-time-badge .label {{ font-size: 11px; margin-top: 2px; line-height: 1.1; }}
    </style>
    <div id=\"step93-current-time-badge\">
      <div class=\"time\">{_step93_time}</div>
      <div class=\"label\">{_step93_label}</div>
    </div>
    """, unsafe_allow_html=True)
except Exception:
    pass
# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH END
'''


def read_text(path: Path) -> str:
    for enc in ('utf-8', 'utf-8-sig', 'cp949'):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors='ignore')


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8', newline='\n')


def remove_step_blocks(text: str) -> str:
    # Remove any marked Step90~Step99 blocks created in previous attempts.
    patterns = [
        r'\n?# >>> STEP9\d[^\n]*BEGIN.*?# >>> STEP9\d[^\n]*END\n?',
        r'\n?# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH BEGIN.*?# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH END\n?',
        r'\n?# >>> STEP91[^\n]*BEGIN.*?# >>> STEP91[^\n]*END\n?',
        r'\n?# >>> STEP90[^\n]*BEGIN.*?# >>> STEP90[^\n]*END\n?',
    ]
    for pat in patterns:
        text = re.sub(pat, '\n', text, flags=re.S)

    # Defensive removal for partial Step92 variable/string blocks if marker was damaged.
    text = re.sub(r'\n\s*_STEP92_CSS\s*=\s*r?""".*?"""\s*\n', '\n', text, flags=re.S)
    text = re.sub(r'\n\s*_STEP92_CLOCK\s*=\s*r?""".*?"""\s*\n', '\n', text, flags=re.S)
    text = re.sub(r'\n\s*st\.markdown\(_STEP92_CLOCK,\s*unsafe_allow_html=True\)\s*\n', '\n', text)
    text = re.sub(r'\n\s*st\.markdown\(_STEP92_CSS,\s*unsafe_allow_html=True\)\s*\n', '\n', text)
    return text


def normalize_labels(text: str) -> str:
    replacements = {
        '달\\n력': '달력',
        '달\n력': '달력',
        '달<br>력': '달력',
        '달<br/>력': '달력',
        '달<br />력': '달력',
        '메\\n모': '메모',
        '메\n모': '메모',
        '메<br>모': '메모',
        '메<br/>모': '메모',
        '메<br />모': '메모',
        '조\\n회': '조회',
        '조\n회': '조회',
        '조<br>회': '조회',
        '조<br/>회': '조회',
        '조<br />회': '조회',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def find_insert_pos_after_set_page_config(text: str) -> int:
    m = re.search(r'st\.set_page_config\s*\(', text)
    if not m:
        # fallback: after import block
        last_import_end = 0
        for im in re.finditer(r'^(?:import\s+[^\n]+|from\s+[^\n]+\s+import\s+[^\n]+)\s*$', text, flags=re.M):
            last_import_end = im.end()
        return last_import_end

    i = m.end() - 1
    depth = 0
    in_string = None
    escape = False
    quote3 = False
    while i < len(text):
        ch = text[i]
        nxt3 = text[i:i+3]
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif quote3 and nxt3 == in_string * 3:
                i += 2
                in_string = None
                quote3 = False
            elif not quote3 and ch == in_string:
                in_string = None
        else:
            if nxt3 in ("'''", '"""'):
                in_string = nxt3[0]
                quote3 = True
                i += 2
            elif ch in ("'", '"'):
                in_string = ch
                quote3 = False
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    # include to end of current line
                    nl = text.find('\n', i)
                    return len(text) if nl == -1 else nl + 1
        i += 1
    return m.end()


def main() -> int:
    print('============================================================')
    print('Step93 웹뷰어 정밀 UI/테마/현재시각 패치 시작')
    print(f'프로젝트 루트: {ROOT}')
    print(f'대상 파일: {APP}')
    print('============================================================')

    if not APP.exists():
        print('[오류] mobile/app.py 파일을 찾지 못했습니다.')
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'app_before_step93_{ts}.py'
    shutil.copy2(APP, backup)
    print(f'[백업 완료] {backup}')

    text = read_text(APP).replace('\r\n', '\n').replace('\r', '\n')
    text = remove_step_blocks(text)
    text = normalize_labels(text)

    pos = find_insert_pos_after_set_page_config(text)
    text = text[:pos] + '\n' + PATCH_BLOCK + '\n' + text[pos:]

    write_text(APP, text)
    print('[패치 완료] mobile/app.py 에 Step93 패치를 적용했습니다.')
    print('다음 실행: python -m streamlit run mobile\\app.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())

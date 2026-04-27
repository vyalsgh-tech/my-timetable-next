from pathlib import Path
from datetime import datetime
import re
import shutil
import sys
import py_compile

ROOT = Path.cwd()
APP = ROOT / 'mobile' / 'app.py'
BACKUP_DIR = ROOT / 'tools' / '_step94_backups'

BEGIN = '# >>> STEP94_WEB_VIEWER_HEADER_THEME_REFINE BEGIN'
END = '# >>> STEP94_WEB_VIEWER_HEADER_THEME_REFINE END'

OLD_MARKER_PAIRS = [
    ('# >>> STEP90_WEB_VIEWER_LAYOUT_THEME_PATCH BEGIN', '# >>> STEP90_WEB_VIEWER_LAYOUT_THEME_PATCH END'),
    ('# >>> STEP91_WEB_VIEWER_FORCE_LAYOUT_THEME_PATCH BEGIN', '# >>> STEP91_WEB_VIEWER_FORCE_LAYOUT_THEME_PATCH END'),
    ('# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH BEGIN', '# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH END'),
    ('# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH BEGIN', '# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH END'),
    (BEGIN, END),
]

STEP94_BLOCK = r'''
# >>> STEP94_WEB_VIEWER_HEADER_THEME_REFINE BEGIN
try:
    import streamlit as st
    from datetime import datetime

    def _step94_get_theme_name():
        """현재 앱에서 쓰는 테마 이름을 최대한 안전하게 추정합니다."""
        candidates = []
        try:
            for k, v in st.session_state.items():
                lk = str(k).lower()
                if ('theme' in lk) or ('테마' in str(k)) or ('mode' in lk) or ('skin' in lk):
                    if isinstance(v, (str, int, float, bool)):
                        candidates.append(str(v))
        except Exception:
            pass
        try:
            opt = st.get_option('theme.base')
            if opt:
                candidates.append(str(opt))
        except Exception:
            pass
        joined = ' '.join(candidates).lower()
        return joined

    def _step94_palette():
        name = _step94_get_theme_name()
        # fg: 일반 글자, muted: 보조 글자, primary: 버튼/강조, header/table: 표 배경 계열
        if any(x in name for x in ['dark', 'black', 'night', '어두', '다크', '블랙', '밤']):
            return dict(
                primary='#e11d48', primary_fg='#ffffff', bg='#111827', fg='#f8fafc', muted='#cbd5e1',
                panel='#1f2937', header='#334155', table='#182231', table_alt='#202c3b', border='#64748b', alert='#fb7185'
            )
        if any(x in name for x in ['pink', 'rose', 'lovely', '러블리', '핑크', '분홍']):
            return dict(
                primary='#fb7185', primary_fg='#ffffff', bg='#fff7f8', fg='#831843', muted='#9f1239',
                panel='#ffe4e6', header='#fecdd3', table='#fff1f2', table_alt='#ffe4e6', border='#f9a8d4', alert='#e11d48'
            )
        if any(x in name for x in ['green', 'mint', 'forest', '초록', '그린', '민트']):
            return dict(
                primary='#10b981', primary_fg='#ffffff', bg='#f0fdf4', fg='#064e3b', muted='#047857',
                panel='#dcfce7', header='#bbf7d0', table='#f0fdf4', table_alt='#dcfce7', border='#86efac', alert='#dc2626'
            )
        if any(x in name for x in ['purple', 'violet', 'lavender', '보라', '라벤더']):
            return dict(
                primary='#8b5cf6', primary_fg='#ffffff', bg='#faf5ff', fg='#4c1d95', muted='#6d28d9',
                panel='#ede9fe', header='#ddd6fe', table='#faf5ff', table_alt='#f3e8ff', border='#c4b5fd', alert='#e11d48'
            )
        if any(x in name for x in ['yellow', 'cream', 'beige', 'brown', '노랑', '크림', '베이지', '브라운']):
            return dict(
                primary='#d97706', primary_fg='#ffffff', bg='#fffbeb', fg='#78350f', muted='#92400e',
                panel='#fef3c7', header='#fde68a', table='#fffbeb', table_alt='#fef3c7', border='#fbbf24', alert='#dc2626'
            )
        if any(x in name for x in ['win', 'windows', 'blue', 'light', '윈도우', '파랑', '블루', '라이트']):
            return dict(
                primary='#2563eb', primary_fg='#ffffff', bg='#f8fbff', fg='#0f172a', muted='#1e3a8a',
                panel='#e0efff', header='#dbeafe', table='#f8fbff', table_alt='#eff6ff', border='#93c5fd', alert='#dc2626'
            )
        return dict(
            primary='#2563eb', primary_fg='#ffffff', bg='#ffffff', fg='#0f172a', muted='#334155',
            panel='#eef5ff', header='#dbeafe', table='#ffffff', table_alt='#f8fafc', border='#94a3b8', alert='#dc2626'
        )

    def _step94_now_label():
        now = datetime.now()
        m = now.hour * 60 + now.minute
        slots = [
            ('조회', 7*60+40, 8*60),
            ('1교시', 8*60, 8*60+50),
            ('2교시', 9*60, 9*60+50),
            ('3교시', 10*60, 10*60+50),
            ('4교시', 11*60, 11*60+50),
            ('점심', 11*60+50, 12*60+40),
            ('5교시', 12*60+40, 13*60+30),
            ('6교시', 13*60+40, 14*60+30),
            ('7교시', 14*60+40, 15*60+30),
        ]
        if m < slots[0][1]:
            return now.strftime('%H:%M'), '수업 전'
        for i, (name, start, end) in enumerate(slots):
            if start <= m < end:
                return now.strftime('%H:%M'), name
            if i < len(slots) - 1:
                next_name, next_start, _ = slots[i + 1]
                if end <= m < next_start:
                    return now.strftime('%H:%M'), ('곧 ' + next_name if next_start - m <= 15 else '쉬는시간')
        return now.strftime('%H:%M'), '방과 후'

    _p = _step94_palette()
    _time_text, _time_label = _step94_now_label()

    _STEP94_CSS = f"""
    <style>
    :root {{
        --s94-primary: {_p['primary']};
        --s94-primary-fg: {_p['primary_fg']};
        --s94-bg: {_p['bg']};
        --s94-fg: {_p['fg']};
        --s94-muted: {_p['muted']};
        --s94-panel: {_p['panel']};
        --s94-header: {_p['header']};
        --s94-table: {_p['table']};
        --s94-table-alt: {_p['table_alt']};
        --s94-border: {_p['border']};
        --s94-alert: {_p['alert']};
    }}

    /* 제목 절반 가림 방지 */
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] * {{
        line-height: 1.35 !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp [data-testid="stMarkdownContainer"] p {{
        line-height: 1.35 !important;
        min-height: 1.35em !important;
        padding-top: 2px !important;
        padding-bottom: 2px !important;
        margin-top: 0.15rem !important;
        margin-bottom: 0.25rem !important;
        color: var(--s94-fg) !important;
    }}

    /* 상단 버튼줄: 컬럼 폭을 내용 기준으로 정리하고 간격 통일 */
    .stApp div[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]),
    .stApp div[data-testid="stHorizontalBlock"]:has(div[data-baseweb="select"]) {{
        align-items: center !important;
        gap: 8px !important;
        flex-wrap: nowrap !important;
    }}
    .stApp div[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) > div,
    .stApp div[data-testid="stHorizontalBlock"]:has(div[data-baseweb="select"]) > div {{
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }}

    /* 버튼 글자 가림 방지 + 색상 대비 보정 */
    .stApp [data-testid="stButton"] > button {{
        min-height: 44px !important;
        min-width: 44px !important;
        height: 44px !important;
        padding: 0 13px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 10px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        background: var(--s94-primary) !important;
        color: var(--s94-primary-fg) !important;
        border: 1px solid color-mix(in srgb, var(--s94-primary) 80%, #ffffff 20%) !important;
        font-weight: 700 !important;
        box-shadow: 0 1px 4px rgba(0,0,0,.12) !important;
    }}
    .stApp [data-testid="stButton"] > button * {{
        color: var(--s94-primary-fg) !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }}

    /* 달력/설정 selectbox: 텍스트 중앙 정렬, 꺾쇠 영역 숨김 */
    .stApp div[data-baseweb="select"] {{
        width: auto !important;
        min-width: 58px !important;
        max-width: 76px !important;
    }}
    .stApp div[data-baseweb="select"] > div {{
        min-height: 44px !important;
        height: 44px !important;
        width: auto !important;
        min-width: 58px !important;
        border-radius: 10px !important;
        background: color-mix(in srgb, var(--s94-bg) 88%, #ffffff 12%) !important;
        border: 1px solid var(--s94-border) !important;
        color: var(--s94-fg) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 10px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }}
    .stApp div[data-baseweb="select"] > div > div {{
        flex: 0 1 auto !important;
        width: 100% !important;
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        color: var(--s94-fg) !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible !important;
        white-space: nowrap !important;
        text-overflow: clip !important;
        line-height: 1.2 !important;
    }}
    .stApp div[data-baseweb="select"] span,
    .stApp div[data-baseweb="select"] input {{
        color: var(--s94-fg) !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: visible !important;
        line-height: 1.2 !important;
    }}
    .stApp div[data-baseweb="select"] svg,
    .stApp div[data-baseweb="select"] [data-baseweb="icon"] {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        opacity: 0 !important;
    }}
    .stApp div[data-baseweb="select"] > div > div:last-child {{
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* 상단바 안의 일반 텍스트(8·9 등) 색상/정렬 */
    .stApp div[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) p,
    .stApp div[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]) span {{
        color: var(--s94-fg) !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-align: center !important;
    }}

    /* 시간표 표: 테마와 동조, 글자 대비 보장 */
    .stApp table {{
        width: 100% !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        border: 1px solid var(--s94-border) !important;
        background: var(--s94-table) !important;
        box-shadow: 0 3px 10px rgba(0,0,0,.10) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }}
    .stApp table th,
    .stApp table td {{
        border: 1px solid var(--s94-border) !important;
        color: var(--s94-fg) !important;
        background: var(--s94-table) !important;
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        text-align: center !important;
        vertical-align: middle !important;
        line-height: 1.25 !important;
    }}
    .stApp table thead th,
    .stApp table tr:first-child th,
    .stApp table tr:first-child td {{
        background: var(--s94-header) !important;
        color: var(--s94-fg) !important;
        font-weight: 800 !important;
    }}
    .stApp table tr:nth-child(even) td {{
        background: var(--s94-table-alt) !important;
    }}
    .stApp table tr td:first-child,
    .stApp table tr th:first-child {{
        background: var(--s94-header) !important;
        color: var(--s94-fg) !important;
        font-weight: 800 !important;
    }}
    .stApp table td *,
    .stApp table th * {{
        color: inherit !important;
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        max-width: 100% !important;
    }}
    .stApp table span[style*="red"],
    .stApp table font[color="red"],
    .stApp table td[style*="red"] {{
        color: var(--s94-alert) !important;
        font-weight: 800 !important;
    }}

    /* 현재시각 배지 */
    .step94-current-time-badge {{
        position: fixed;
        right: 10px;
        top: 16px;
        z-index: 9999;
        min-width: 86px;
        padding: 7px 10px;
        border-radius: 12px;
        border: 1px solid var(--s94-border);
        background: color-mix(in srgb, var(--s94-bg) 92%, #ffffff 8%);
        color: var(--s94-fg);
        box-shadow: 0 2px 8px rgba(0,0,0,.12);
        text-align: center;
        line-height: 1.15;
    }}
    .step94-current-time-badge .time {{
        font-size: 13px;
        font-weight: 800;
        color: var(--s94-fg);
    }}
    .step94-current-time-badge .label {{
        margin-top: 2px;
        font-size: 11px;
        color: var(--s94-muted);
        font-weight: 700;
    }}

    @media (max-width: 720px) {{
        .stApp div[data-testid="stHorizontalBlock"]:has([data-testid="stButton"]),
        .stApp div[data-testid="stHorizontalBlock"]:has(div[data-baseweb="select"]) {{
            gap: 6px !important;
        }}
        .stApp [data-testid="stButton"] > button {{
            min-width: 40px !important;
            height: 42px !important;
            min-height: 42px !important;
            padding-left: 11px !important;
            padding-right: 11px !important;
            font-size: 15px !important;
        }}
        .stApp div[data-baseweb="select"] > div {{
            min-width: 56px !important;
            height: 42px !important;
            min-height: 42px !important;
            font-size: 15px !important;
        }}
        .stApp table th,
        .stApp table td {{
            font-size: 12px !important;
            padding: 5px 3px !important;
        }}
    }}
    </style>
    """
    st.markdown(_STEP94_CSS, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step94-current-time-badge">
        <div class="time">{_time_text}</div>
        <div class="label">{_time_label}</div>
    </div>
    """, unsafe_allow_html=True)

    def _step94_timetable_inner_css():
        return f"""
        <style>
        :root {{
            --s94-primary: {_p['primary']}; --s94-primary-fg: {_p['primary_fg']}; --s94-bg: {_p['bg']};
            --s94-fg: {_p['fg']}; --s94-muted: {_p['muted']}; --s94-header: {_p['header']};
            --s94-table: {_p['table']}; --s94-table-alt: {_p['table_alt']}; --s94-border: {_p['border']}; --s94-alert: {_p['alert']};
        }}
        table {{ width:100% !important; table-layout:fixed !important; border-collapse:collapse !important; border:1px solid var(--s94-border) !important; background:var(--s94-table) !important; }}
        th, td {{ border:1px solid var(--s94-border) !important; color:var(--s94-fg) !important; background:var(--s94-table) !important; white-space:normal !important; word-break:keep-all !important; overflow-wrap:anywhere !important; text-align:center !important; vertical-align:middle !important; line-height:1.25 !important; }}
        thead th, tr:first-child th, tr:first-child td {{ background:var(--s94-header) !important; color:var(--s94-fg) !important; font-weight:800 !important; }}
        tr:nth-child(even) td {{ background:var(--s94-table-alt) !important; }}
        tr td:first-child, tr th:first-child {{ background:var(--s94-header) !important; color:var(--s94-fg) !important; font-weight:800 !important; }}
        td *, th * {{ color:inherit !important; white-space:normal !important; word-break:keep-all !important; overflow-wrap:anywhere !important; max-width:100% !important; }}
        span[style*="red"], font[color="red"], td[style*="red"] {{ color:var(--s94-alert) !important; font-weight:800 !important; }}
        </style>
        """

    def _step94_inject_table_css(html):
        if not isinstance(html, str):
            return html
        if '<table' not in html.lower():
            return html
        if 'STEP94_TABLE_INNER_CSS' in html:
            return html
        css = '<!-- STEP94_TABLE_INNER_CSS -->' + _step94_timetable_inner_css()
        low = html.lower()
        if '</head>' in low:
            idx = low.rfind('</head>')
            return html[:idx] + css + html[idx:]
        return css + html

    try:
        import streamlit.components.v1 as _s94_components
        if not hasattr(_s94_components, '_step94_original_html'):
            _s94_components._step94_original_html = _s94_components.html
            def _step94_html(html, *args, **kwargs):
                return _s94_components._step94_original_html(_step94_inject_table_css(html), *args, **kwargs)
            _s94_components.html = _step94_html
            try:
                st.components.v1.html = _step94_html
            except Exception:
                pass
    except Exception:
        pass

except Exception:
    pass
# >>> STEP94_WEB_VIEWER_HEADER_THEME_REFINE END
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


def strip_between(text: str, begin: str, end: str) -> str:
    return re.sub(re.escape(begin) + r'.*?' + re.escape(end), '', text, flags=re.S)


def strip_old_blocks(text: str) -> str:
    for begin, end in OLD_MARKER_PAIRS:
        text = strip_between(text, begin, end)
    # 이전 단계의 HTML/JS 노출 잔재가 app.py 문자열로 남은 경우 방지
    text = re.sub(r'<div id="step92-current-time-badge".*?</script>\s*"""', '"""', text, flags=re.S)
    return text


def normalize_labels(text: str) -> str:
    repl = {
        '달\\n력': '달력', '달\n력': '달력', '달<br>력': '달력', '달<br/>력': '달력', '달<br />력': '달력',
        '메\\n모': '메모', '메\n모': '메모', '메<br>모': '메모', '메<br/>모': '메모', '메<br />모': '메모',
        '조\\n회': '조회', '조\n회': '조회', '조<br>회': '조회', '조<br/>회': '조회', '조<br />회': '조회',
        '>달<br>력<': '>달력<', '>메<br>모<': '>메모<', '>조<br>회<': '>조회<',
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    return text


def insertion_index_after_imports(text: str) -> int:
    lines = text.splitlines(True)
    last_import = -1
    for i, line in enumerate(lines[:200]):
        s = line.strip()
        if s.startswith('import ') or s.startswith('from '):
            last_import = i
    if last_import >= 0:
        return sum(len(x) for x in lines[:last_import + 1])
    return 0


def main() -> int:
    print('============================================================')
    print('Step94 웹뷰어 상단바/테마/글자대비 정밀 보정 시작')
    print(f'프로젝트 루트: {ROOT}')
    print(f'대상 파일: {APP}')
    print('============================================================')

    if not APP.exists():
        print('[오류] mobile/app.py 파일을 찾지 못했습니다.')
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = BACKUP_DIR / f'app_before_step94_{ts}.py'
    shutil.copy2(APP, backup)
    print(f'[백업 완료] {backup}')

    text = read_text(APP).replace('\r\n', '\n').replace('\r', '\n')
    text = strip_old_blocks(text)
    text = normalize_labels(text)

    idx = insertion_index_after_imports(text)
    text = text[:idx] + '\n' + STEP94_BLOCK + '\n' + text[idx:]

    write_text(APP, text)

    try:
        py_compile.compile(str(APP), doraise=True)
        print('[문법 확인 완료] mobile/app.py')
    except Exception as e:
        print('[문법 오류] 패치 후 app.py 컴파일에 실패했습니다. 백업을 복원합니다.')
        shutil.copy2(backup, APP)
        print(f'[복원 완료] {backup} -> {APP}')
        print(e)
        return 1

    print('[패치 완료] Step94 적용이 끝났습니다.')
    print('다음 실행: python -m streamlit run mobile\\app.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())

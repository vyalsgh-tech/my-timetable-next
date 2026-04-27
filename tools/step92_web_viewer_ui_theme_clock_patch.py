from pathlib import Path
from datetime import datetime
import re
import shutil
import sys

ROOT = Path.cwd()
APP = ROOT / 'mobile' / 'app.py'
BACKUP_DIR = ROOT / 'tools' / '_step92_backups'

BEGIN = '# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH BEGIN'
END = '# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH END'

INJECT_BLOCK = r'''
# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH BEGIN
try:
    import streamlit as st

    _STEP92_CSS = r"""
    <style>
    /* ===== Step92: header control stabilization ===== */
    .stApp [data-testid="stButton"] > button,
    .stApp div[data-baseweb="select"] > div {
        min-height: 42px !important;
        border-radius: 10px !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        font-size: 16px !important;
        line-height: 1.2 !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
        box-sizing: border-box !important;
    }

    .stApp [data-testid="stButton"] > button {
        min-width: 48px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    /* selectboxes: center label and hide caret space so "달력" is centered */
    .stApp div[data-baseweb="select"] {
        min-width: 58px !important;
    }
    .stApp div[data-baseweb="select"] > div {
        justify-content: center !important;
        text-align: center !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }
    .stApp div[data-baseweb="select"] > div > div {
        flex: 0 1 auto !important;
        min-width: 0 !important;
        justify-content: center !important;
        text-align: center !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }
    .stApp div[data-baseweb="select"] svg {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* prevent header title / memo / homeroom labels from clipping */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp label,
    .stApp span,
    .stApp button {
        text-overflow: clip !important;
    }

    /* ===== Step92: timetable theme sync ===== */
    :root {
        --step92-primary: var(--primary-color, #4f8bf9);
        --step92-bg: var(--background-color, #ffffff);
        --step92-text: var(--text-color, #0f172a);
        --step92-border: color-mix(in srgb, var(--step92-primary) 28%, #94a3b8 72%);
        --step92-header-bg: color-mix(in srgb, var(--step92-primary) 13%, var(--step92-bg) 87%);
        --step92-sub-bg: color-mix(in srgb, var(--step92-primary) 7%, var(--step92-bg) 93%);
        --step92-card-shadow: 0 3px 10px rgba(0,0,0,.08);
        --step92-alert: color-mix(in srgb, #ef4444 78%, var(--step92-primary) 22%);
    }

    .stApp table {
        width: 100% !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        border: 1px solid var(--step92-border) !important;
        background: color-mix(in srgb, var(--step92-bg) 97%, var(--step92-primary) 3%) !important;
        box-shadow: var(--step92-card-shadow) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    .stApp table thead th,
    .stApp table tr:first-child th,
    .stApp table tr:first-child td {
        background: var(--step92-header-bg) !important;
        color: var(--step92-text) !important;
        border: 1px solid var(--step92-border) !important;
    }

    .stApp table th,
    .stApp table td {
        border: 1px solid var(--step92-border) !important;
        color: var(--step92-text) !important;
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        text-align: center !important;
        vertical-align: middle !important;
        padding: 6px 4px !important;
        line-height: 1.25 !important;
        height: auto !important;
    }

    .stApp table td {
        background: color-mix(in srgb, var(--step92-bg) 96%, var(--step92-primary) 4%) !important;
        font-size: 13px !important;
    }

    .stApp table tbody tr:nth-child(odd) td {
        background: color-mix(in srgb, var(--step92-bg) 93%, var(--step92-primary) 7%) !important;
    }

    /* left period/time column */
    .stApp table tr td:first-child,
    .stApp table tr th:first-child {
        background: color-mix(in srgb, var(--step92-primary) 10%, var(--step92-bg) 90%) !important;
        font-weight: 700 !important;
    }

    /* keep long subject lists inside timetable cells */
    .stApp table td * {
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        max-width: 100% !important;
    }

    /* red subject text */
    .stApp table td[style*="red"],
    .stApp table span[style*="red"],
    .stApp table font[color="red"] {
        color: var(--step92-alert) !important;
    }

    /* compact cells for mobile width */
    @media (max-width: 720px) {
        .stApp table th,
        .stApp table td {
            font-size: 12px !important;
            padding: 5px 3px !important;
        }
        .stApp [data-testid="stButton"] > button,
        .stApp div[data-baseweb="select"] > div {
            font-size: 15px !important;
            min-height: 40px !important;
        }
    }

    /* ===== Step92 current-time floating badge ===== */
    #step92-current-time-badge {
        position: fixed;
        right: 12px;
        top: 72px;
        z-index: 9999;
        background: color-mix(in srgb, var(--step92-bg) 88%, var(--step92-primary) 12%);
        border: 1px solid var(--step92-border);
        border-radius: 12px;
        box-shadow: var(--step92-card-shadow);
        padding: 8px 10px;
        min-width: 102px;
        text-align: center;
        color: var(--step92-text);
        backdrop-filter: blur(6px);
    }
    #step92-current-time-badge .step92-time {
        font-size: 15px;
        font-weight: 700;
        line-height: 1.1;
    }
    #step92-current-time-badge .step92-label {
        margin-top: 2px;
        font-size: 12px;
        line-height: 1.15;
        opacity: .92;
    }
    @media (max-width: 720px) {
        #step92-current-time-badge {
            top: 78px;
            right: 10px;
            min-width: 92px;
            padding: 7px 9px;
        }
        #step92-current-time-badge .step92-time { font-size: 14px; }
        #step92-current-time-badge .step92-label { font-size: 11px; }
    }
    </style>
    """
    st.markdown(_STEP92_CSS, unsafe_allow_html=True)

    _STEP92_CLOCK = r"""
    <div id="step92-current-time-badge">
      <div class="step92-time">--:--</div>
      <div class="step92-label">로딩 중</div>
    </div>
    <script>
    (function() {
      const badge = document.getElementById('step92-current-time-badge');
      if (!badge) return;
      const timeEl = badge.querySelector('.step92-time');
      const labelEl = badge.querySelector('.step92-label');

      function pad(n) { return String(n).padStart(2, '0'); }
      function hm(date) { return date.getHours() * 60 + date.getMinutes(); }

      const slots = [
        ['조회', 7*60+40, 8*60],
        ['1교시', 8*60, 8*60+50],
        ['2교시', 9*60, 9*60+50],
        ['3교시', 10*60, 10*60+50],
        ['4교시', 11*60, 11*60+50],
        ['점심', 11*60+50, 12*60+40],
        ['5교시', 12*60+40, 13*60+30],
        ['6교시', 13*60+40, 14*60+30],
        ['7교시', 14*60+40, 15*60+30],
      ];

      function currentLabel(m) {
        if (m < slots[0][1]) {
          return '수업 전';
        }
        for (let i = 0; i < slots.length; i++) {
          const [name, start, end] = slots[i];
          if (m >= start && m < end) return name;
          if (i < slots.length - 1) {
            const nextStart = slots[i + 1][1];
            if (m >= end && m < nextStart) {
              return (nextStart - m <= 15) ? ('곧 ' + slots[i + 1][0]) : '쉬는시간';
            }
          }
        }
        return '방과 후';
      }

      function update() {
        const now = new Date();
        timeEl.textContent = pad(now.getHours()) + ':' + pad(now.getMinutes());
        labelEl.textContent = currentLabel(hm(now));
      }

      update();
      if (window.step92ClockTimer) clearInterval(window.step92ClockTimer);
      window.step92ClockTimer = setInterval(update, 1000);
    })();
    </script>
    """
    st.markdown(_STEP92_CLOCK, unsafe_allow_html=True)
except Exception:
    pass
# >>> STEP92_WEB_VIEWER_UI_THEME_CLOCK_PATCH END
'''


def read_text(path: Path) -> str:
    for enc in ('utf-8', 'cp949', 'utf-8-sig'):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors='ignore')


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8', newline='\n')


def strip_old_block(text: str, begin: str, end: str) -> str:
    pattern = re.compile(re.escape(begin) + r'.*?' + re.escape(end), re.S)
    return pattern.sub('', text)


def main() -> int:
    print('============================================================')
    print('Step92 웹뷰어 UI/테마/현재시각 패치 시작')
    print(f'프로젝트 루트: {ROOT}')
    print(f'대상 파일: {APP}')
    print('============================================================')

    if not APP.exists():
        print('[오류] mobile/app.py 파일을 찾지 못했습니다.')
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'app_before_step92_{ts}.py'
    shutil.copy2(APP, backup_path)
    print(f'[백업 완료] {backup_path}')

    text = read_text(APP)
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # remove previously inserted step92 block so reruns stay clean
    text = strip_old_block(text, BEGIN, END)

    # normalize common broken labels
    replacements = {
        '달\\n력': '달력',
        '달\n력': '달력',
        '메\\n모': '메모',
        '메\n모': '메모',
        '조\\n회': '조회',
        '조\n회': '조회',
        '>달<br>력<': '>달력<',
        '>메<br>모<': '>메모<',
        '>조<br>회<': '>조회<',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    # add patch block at end
    if not text.endswith('\n'):
        text += '\n'
    text += '\n' + INJECT_BLOCK + '\n'

    write_text(APP, text)
    print('[패치 완료] mobile/app.py 에 Step92 패치를 적용했습니다.')
    print('다음 실행: python -m streamlit run mobile\\app.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())

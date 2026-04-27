# tools/step82_web_theme_button_calendar_refinement_school_path.py
# ------------------------------------------------------------
# Step82: 웹뷰어 테마/버튼/달력 최종 보정 - 학교 경로용
#
# 유지:
# - Step80의 현재시각 기능은 건드리지 않고 CSS로 크기만 확대
#
# 수정:
# 1) 테마별 상단 버튼 배경/글씨 대비 재보정
# 2) 시각정보 폰트 크기 확대
# 3) 달력 버튼을 메모/조회처럼 버튼형으로 보이게 하고 중앙 overlay 텍스트 적용
# 4) 달력 꺾쇠는 제거 + 내부 텍스트 투명화 + 중앙 overlay로 해결
# 5) 테마 변경에 따른 시간표 테이블 색상 보정
# 6) 러블리 핑크 테마 추가 재시도
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

# 학교 경로 고정
ROOT = Path(r"Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next")
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = r'''
# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_START]
try:
    import streamlit.components.v1 as components
    components.html(
        r"""
        <script>
        (function() {
            const STYLE_ID = 'step82-theme-button-calendar-style';

            const PALETTES = {
                light: {
                    tableWrap: '#dbe8f7', th1: '#eaf3ff', th2: '#d7e6f8', td1: '#ffffff', td2: '#fafcff', line: '#1f2937', text: '#0f172a',
                    calendarBg: '#f5f0ff', calendarText: '#6d28d9', calendarBorder: '#ddd6fe',
                    memoBg: '#2563eb', memoText: '#ffffff', searchBg: '#fff4dd', searchText: '#8a4b00', searchBorder: '#f2cf96',
                    eightBg: '#edf2ff', eightText: '#1e40af', eightBorder: '#cfd8ff'
                },
                dark: {
                    tableWrap: '#243044', th1: '#334155', th2: '#243041', td1: '#111827', td2: '#172033', line: '#cbd5e1', text: '#f8fafc',
                    calendarBg: '#ede9fe', calendarText: '#4c1d95', calendarBorder: '#c4b5fd',
                    memoBg: '#e11d48', memoText: '#ffffff', searchBg: '#f97316', searchText: '#ffffff', searchBorder: '#ea580c',
                    eightBg: '#dbeafe', eightText: '#1e3a8a', eightBorder: '#93c5fd'
                },
                green: {
                    tableWrap: '#cfe7dc', th1: '#dcfce7', th2: '#bbf7d0', td1: '#ffffff', td2: '#f0fdf4', line: '#14532d', text: '#052e16',
                    calendarBg: '#f5f3ff', calendarText: '#5b21b6', calendarBorder: '#ddd6fe',
                    memoBg: '#ea580c', memoText: '#ffffff', searchBg: '#f97316', searchText: '#ffffff', searchBorder: '#ea580c',
                    eightBg: '#d9f99d', eightText: '#365314', eightBorder: '#a3e635'
                },
                pink: {
                    tableWrap: '#ffe1ec', th1: '#ffe6ef', th2: '#ffd3e2', td1: '#fffefe', td2: '#fff7fb', line: '#7f1d43', text: '#4a1d2f',
                    calendarBg: '#fff1f7', calendarText: '#be185d', calendarBorder: '#f9a8d4',
                    memoBg: '#ec4899', memoText: '#ffffff', searchBg: '#fff1e6', searchText: '#9a3412', searchBorder: '#fdba74',
                    eightBg: '#fdf2f8', eightText: '#9d174d', eightBorder: '#fbcfe8'
                },
                blue: {
                    tableWrap: '#dbeafe', th1: '#e0f2fe', th2: '#bae6fd', td1: '#ffffff', td2: '#f8fbff', line: '#1e3a8a', text: '#0f172a',
                    calendarBg: '#f5f3ff', calendarText: '#5b21b6', calendarBorder: '#ddd6fe',
                    memoBg: '#2563eb', memoText: '#ffffff', searchBg: '#fff7ed', searchText: '#9a3412', searchBorder: '#fed7aa',
                    eightBg: '#e0f2fe', eightText: '#075985', eightBorder: '#7dd3fc'
                }
            };

            function docRoot() {
                try { return window.parent.document; } catch(e) { return document; }
            }

            function visible(el) {
                if (!el) return false;
                const s = window.getComputedStyle(el);
                if (s.display === 'none' || s.visibility === 'hidden') return false;
                const r = el.getBoundingClientRect();
                return r.width > 1 && r.height > 1;
            }

            function textOf(el) {
                return ((el && (el.innerText || el.textContent)) || '').replace(/\s+/g, ' ').trim();
            }

            function parseRgb(value) {
                const m = (value || '').match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
                if (!m) return null;
                return { r: +m[1], g: +m[2], b: +m[3] };
            }

            function lum(c) {
                if (!c) return 255;
                return 0.299 * c.r + 0.587 * c.g + 0.114 * c.b;
            }

            function findToolbar(doc) {
                const bars = Array.from(doc.querySelectorAll('div[data-testid="stHorizontalBlock"]')).filter(visible);
                return bars.find(b => {
                    const t = textOf(b);
                    return t.includes('오늘') && t.includes('달력') && t.includes('메모');
                }) || null;
            }

            function detectPalette(doc) {
                const bodyText = doc.body ? (doc.body.innerText || '') : '';
                if (bodyText.includes('러블리 핑크')) return 'pink';

                const bar = findToolbar(doc);
                const c = parseRgb(bar ? getComputedStyle(bar).backgroundColor : getComputedStyle(doc.body).backgroundColor);
                if (c) {
                    if (lum(c) < 90) return 'dark';
                    if (c.g > c.r + 18 && c.g > c.b + 5) return 'green';
                    if (c.b > c.r + 12 && c.b > c.g - 5) return 'blue';
                    if (c.r > 235 && c.g < 220 && c.b > 220) return 'pink';
                }

                const lower = bodyText.toLowerCase();
                if (lower.includes('dark') || bodyText.includes('다크') || bodyText.includes('블랙') || bodyText.includes('야간')) return 'dark';
                if (bodyText.includes('그린') || bodyText.includes('초록') || bodyText.includes('숲')) return 'green';
                if (bodyText.includes('블루') || bodyText.includes('파랑') || bodyText.includes('윈도우')) return 'blue';
                return 'light';
            }

            function setVars(doc, paletteKey) {
                const p = PALETTES[paletteKey] || PALETTES.light;
                const root = doc.body;
                const vars = {
                    '--step82-table-wrap': p.tableWrap, '--step82-th1': p.th1, '--step82-th2': p.th2, '--step82-td1': p.td1, '--step82-td2': p.td2,
                    '--step82-line': p.line, '--step82-text': p.text,
                    '--step82-calendar-bg': p.calendarBg, '--step82-calendar-text': p.calendarText, '--step82-calendar-border': p.calendarBorder,
                    '--step82-memo-bg': p.memoBg, '--step82-memo-text': p.memoText,
                    '--step82-search-bg': p.searchBg, '--step82-search-text': p.searchText, '--step82-search-border': p.searchBorder,
                    '--step82-eight-bg': p.eightBg, '--step82-eight-text': p.eightText, '--step82-eight-border': p.eightBorder
                };
                for (const [k, v] of Object.entries(vars)) root.style.setProperty(k, v);
                for (const key of Object.keys(PALETTES)) {
                    doc.body.classList.remove('step82-theme-' + key);
                    const app = doc.querySelector('.stApp');
                    if (app) app.classList.remove('step82-theme-' + key);
                }
                doc.body.classList.add('step82-theme-' + paletteKey);
                const app = doc.querySelector('.stApp');
                if (app) app.classList.add('step82-theme-' + paletteKey);
            }

            function injectStyle(doc) {
                if (doc.getElementById(STYLE_ID)) return;
                const style = doc.createElement('style');
                style.id = STYLE_ID;
                style.textContent = `
                    #step80-clock-fixed,
                    #step79-clock-fixed,
                    #step78-clock-fixed {
                        font-size: 14px !important;
                        line-height: 1.15 !important;
                        font-weight: 900 !important;
                        padding: 5px 12px !important;
                        letter-spacing: -0.1px !important;
                    }
                    body[class*="step82-theme-"] table.mobile-table {
                        color: var(--step82-text) !important;
                        border-color: var(--step82-line) !important;
                    }
                    body[class*="step82-theme-"] table.mobile-table th {
                        background-image: linear-gradient(180deg, var(--step82-th1), var(--step82-th2)) !important;
                        color: var(--step82-text) !important;
                        border-color: var(--step82-line) !important;
                    }
                    body[class*="step82-theme-"] table.mobile-table td {
                        background-image: linear-gradient(180deg, var(--step82-td1), var(--step82-td2)) !important;
                        color: var(--step82-text) !important;
                        border-color: var(--step82-line) !important;
                    }
                    body[class*="step82-theme-"] div:has(> table.mobile-table) {
                        background: var(--step82-table-wrap) !important;
                    }
                    .step82-btn-calendar,
                    .step82-btn-memo,
                    .step82-btn-search,
                    .step82-btn-89 {
                        box-sizing: border-box !important;
                        height: 40px !important;
                        min-height: 40px !important;
                        border-radius: 7px !important;
                        font-weight: 800 !important;
                        text-align: center !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                    }
                    .step82-btn-calendar *,
                    .step82-btn-memo *,
                    .step82-btn-search *,
                    .step82-btn-89 * {
                        color: inherit !important;
                        -webkit-text-fill-color: currentColor !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        text-align: center !important;
                    }
                    .step82-btn-calendar {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                        flex: 0 0 58px !important;
                        background: var(--step82-calendar-bg) !important;
                        border: 1px solid var(--step82-calendar-border) !important;
                        color: var(--step82-calendar-text) !important;
                        padding: 0 !important;
                        position: relative !important;
                        overflow: hidden !important;
                    }
                    .step82-btn-memo { background: var(--step82-memo-bg) !important; border: 1px solid var(--step82-memo-bg) !important; color: var(--step82-memo-text) !important; }
                    .step82-btn-search { background: var(--step82-search-bg) !important; border: 1px solid var(--step82-search-border) !important; color: var(--step82-search-text) !important; }
                    .step82-btn-89 { background: var(--step82-eight-bg) !important; border: 1px solid var(--step82-eight-border) !important; color: var(--step82-eight-text) !important; }
                    .step82-calendar-shell {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                        flex: 0 0 58px !important;
                        position: relative !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        padding: 0 !important;
                        box-sizing: border-box !important;
                    }
                    .step82-calendar-shell > * { width: 58px !important; min-width: 58px !important; max-width: 58px !important; }
                    .step82-calendar-shell [data-baseweb="select"],
                    .step82-calendar-shell [role="button"],
                    .step82-calendar-shell button {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        grid-template-columns: 1fr !important;
                        padding-left: 0 !important;
                        padding-right: 0 !important;
                        color: transparent !important;
                        -webkit-text-fill-color: transparent !important;
                    }
                    .step82-calendar-shell [data-baseweb="select"] *,
                    .step82-calendar-shell [role="button"] *,
                    .step82-calendar-shell button * {
                        color: transparent !important;
                        -webkit-text-fill-color: transparent !important;
                    }
                    .step82-calendar-shell svg,
                    .step82-calendar-shell [aria-hidden="true"],
                    .step82-calendar-shell .step82-remove {
                        display: none !important;
                        width: 0 !important;
                        min-width: 0 !important;
                        max-width: 0 !important;
                        flex: 0 0 0 !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .step82-calendar-overlay {
                        position: absolute !important;
                        inset: 0 !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        pointer-events: none !important;
                        color: var(--step82-calendar-text) !important;
                        -webkit-text-fill-color: var(--step82-calendar-text) !important;
                        font-size: 14px !important;
                        font-weight: 800 !important;
                        line-height: 1 !important;
                        text-align: center !important;
                        z-index: 3 !important;
                    }
                `;
                doc.head.appendChild(style);
            }

            function classify(child) {
                const t = textOf(child);
                if (t.includes('달력')) return 'calendar';
                if (t.includes('메모')) return 'memo';
                if (t.includes('조회')) return 'search';
                if (t.includes('8·9') || t.includes('8-9') || t === '89' || t.includes('89')) return '89';
                return '';
            }

            function buttonTarget(child) {
                return child.querySelector('button,[role="button"],div[data-baseweb="select"]') || child;
            }

            function refineCalendar(child) {
                child.classList.add('step82-calendar-shell');
                const btn = buttonTarget(child);
                btn.classList.add('step82-btn-calendar');
                const removable = [];
                for (const svg of Array.from(child.querySelectorAll('svg'))) removable.push(svg);
                for (const el of Array.from(child.querySelectorAll('span,div,p'))) {
                    const t = (el.textContent || '').trim();
                    if (/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test(t)) removable.push(el);
                }
                for (const el of removable) {
                    try { el.remove(); }
                    catch(e) {
                        el.classList.add('step82-remove');
                        el.style.setProperty('display', 'none', 'important');
                    }
                }
                let overlay = child.querySelector('.step82-calendar-overlay');
                if (!overlay) {
                    overlay = docRoot().createElement('span');
                    overlay.className = 'step82-calendar-overlay';
                    overlay.textContent = '달력';
                    child.appendChild(overlay);
                } else {
                    overlay.textContent = '달력';
                }
            }

            function refineButtons(doc) {
                const bar = findToolbar(doc);
                if (!bar) return;
                for (const child of Array.from(bar.children || [])) {
                    const kind = classify(child);
                    const btn = buttonTarget(child);
                    if (kind === 'calendar') refineCalendar(child);
                    else if (kind === 'memo') btn.classList.add('step82-btn-memo');
                    else if (kind === 'search') btn.classList.add('step82-btn-search');
                    else if (kind === '89') btn.classList.add('step82-btn-89');
                }
            }

            function run() {
                const doc = docRoot();
                injectStyle(doc);
                const palette = detectPalette(doc);
                setVars(doc, palette);
                refineButtons(doc);
            }

            run();
            setTimeout(run, 150);
            setTimeout(run, 500);
            setTimeout(run, 1200);
            setTimeout(run, 2500);
            setInterval(run, 3000);
        })();
        </script>
        """,
        height=1,
        width=1,
    )
except Exception:
    pass
# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_END]
'''

LOVELY_PINK_THEME = r'''
    "러블리 핑크": {
        "bg": "#fff5f8",
        "card": "#ffffff",
        "text": "#4a1d2f",
        "muted": "#9f647a",
        "primary": "#ec4899",
        "primary_dark": "#db2777",
        "accent": "#f9a8d4",
        "header_bg": "#ffe6ef",
        "header_bg2": "#ffd3e2",
        "cell_bg": "#fffafe",
        "cell_bg2": "#fff7fb",
        "border": "#f3bfd2",
        "shadow": "rgba(236, 72, 153, 0.14)",
    },
'''

REMOVE_MARKERS = [
    ("# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_START]", "# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_END]"),
    ("# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_START]", "# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step82_theme_button_calendar_{STAMP}{APP.suffix}")
    b.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")


def compiles(text: str, name: str):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def remove_block_once(text: str, start_marker: str, end_marker: str):
    start = text.find(start_marker)
    if start == -1:
        return text, False
    end = text.find(end_marker, start)
    if end == -1:
        return text, False
    end_line = text.find("\n", end)
    end_line = len(text) if end_line == -1 else end_line + 1
    return text[:start] + text[end_line:], True


def remove_old_blocks(text: str):
    removed = 0
    for start, end in REMOVE_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    return text, removed


def add_lovely_pink_to_theme_dict(text: str):
    if '"러블리 핑크"' in text or "'러블리 핑크'" in text:
        return text, "already_exists"

    m = re.search(r"(^\s*(?:THEMES|themes|theme_map|THEME_MAP|theme_colors|THEME_COLORS)\s*=\s*\{)", text, flags=re.M)
    if not m:
        return text, "theme_dict_not_found"

    start = m.end() - 1
    depth = 0
    end = None
    in_str = None
    esc = False

    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"'):
            in_str = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    if end is None:
        return text, "theme_dict_end_not_found"

    text = text[:end] + LOVELY_PINK_THEME.rstrip() + "\n" + text[end:]
    return text, "theme_dict_added"


def add_lovely_pink_to_options(text: str):
    if "러블리 핑크" in text:
        return text, 0

    changed = 0
    patterns = [
        r"(theme_options\s*=\s*\[[^\]]*)\]",
        r"(themes_list\s*=\s*\[[^\]]*)\]",
        r"(theme_names\s*=\s*\[[^\]]*)\]",
    ]

    for pat in patterns:
        def repl(m):
            nonlocal changed
            changed += 1
            return m.group(1).rstrip() + ', "러블리 핑크"]'

        text2, n = re.subn(pat, repl, text, count=1, flags=re.S)
        if n:
            return text2, changed

    pat = r"(st\.selectbox\([^\n]{0,200}(?:테마|theme)[\s\S]{0,500}?\[[^\]]*)\]"

    def repl2(m):
        nonlocal changed
        changed += 1
        return m.group(1).rstrip() + ', "러블리 핑크"]'

    text2, n = re.subn(pat, repl2, text, count=1)
    return text2, changed


def main():
    print("====================================================")
    print("Step82 web theme/button/calendar refinement")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()
    text = APP.read_text(encoding="utf-8", errors="replace")

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] 현재 mobile/app.py가 이미 문법 오류 상태입니다.")
        print(err)
        print("먼저 정상 실행되는 상태로 복구한 뒤 다시 실행해주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        text, removed = remove_old_blocks(text)
        text, theme_dict_status = add_lovely_pink_to_theme_dict(text)
        text, option_changes = add_lovely_pink_to_options(text)
        text = text.rstrip() + "\n\n" + PATCH_BLOCK.strip("\n") + "\n"
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] 패치 후 mobile/app.py 문법 확인 실패")
        print(err)
        print("패치를 저장하지 않습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    APP.write_text(text, encoding="utf-8")
    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step82 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step81/82 블록 제거: {removed}")
    print(f"- 러블리 핑크 테마 dict 처리: {theme_dict_status}")
    print(f"- 러블리 핑크 옵션 처리: {option_changes}")
    print("- 시각정보 기능은 유지, 폰트 크기만 확대")
    print("- 달력 버튼은 중앙 overlay 방식으로 재구성")
    print("- 테마별 버튼/시간표 색상 대비 보정")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 시각정보 글씨가 조금 커졌는지")
    print("2. 달력 글자가 메모/조회처럼 버튼 중앙에 오는지")
    print("3. 테마별 버튼 글씨가 모두 잘 보이는지")
    print("4. 테마 변경 시 시간표 색상이 함께 바뀌는지")
    print("5. 러블리 핑크 테마가 목록에 있는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

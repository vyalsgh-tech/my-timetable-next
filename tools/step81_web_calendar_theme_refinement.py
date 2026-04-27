# tools/step81_web_calendar_theme_refinement.py
# ------------------------------------------------------------
# Step81: 웹뷰어 달력 버튼/테마 색상 정밀 보정
#
# 수정:
# 1) 달력 꺾쇠를 숨김이 아니라 DOM에서 remove()하여 빈자리 제거
# 2) 달력 텍스트 가운데 정렬
# 3) 테마 변경에 따라 시간표 테이블 색상 맞춤 적용
# 4) 테마별 상단 버튼 배경/글씨 대비 보정
# 5) 러블리 핑크 테마 추가 재시도
#
# 유지:
# - Step80의 시각정보는 수정하지 않음
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = '\n# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            const STYLE_ID = \'step81-calendar-theme-refinement-style\';\n\n            const THEME_PRESETS = {\n                \'default\': {\n                    page: \'#eef4fb\',\n                    toolbar: \'#edf4ff\',\n                    tableWrap: \'#dbe8f7\',\n                    th1: \'#eaf3ff\',\n                    th2: \'#d7e6f8\',\n                    td1: \'#ffffff\',\n                    td2: \'#fafcff\',\n                    line: \'#1f2937\',\n                    text: \'#0f172a\',\n                    calendarBg: \'#f4efff\',\n                    calendarText: \'#6d28d9\',\n                    calendarBorder: \'#dfd3ff\',\n                    memoBg: \'#2563eb\',\n                    memoText: \'#ffffff\',\n                    searchBg: \'#fff7e6\',\n                    searchText: \'#8a4b00\',\n                    searchBorder: \'#f1d6a8\',\n                    eightBg: \'#eef2ff\',\n                    eightText: \'#1e40af\',\n                    eightBorder: \'#d8defa\'\n                },\n                \'lovelyPink\': {\n                    page: \'#fff5f8\',\n                    toolbar: \'#fff0f6\',\n                    tableWrap: \'#ffe1ec\',\n                    th1: \'#ffe6ef\',\n                    th2: \'#ffd3e2\',\n                    td1: \'#fffefe\',\n                    td2: \'#fff7fb\',\n                    line: \'#6b213d\',\n                    text: \'#4a1d2f\',\n                    calendarBg: \'#fff1f7\',\n                    calendarText: \'#be185d\',\n                    calendarBorder: \'#f9a8d4\',\n                    memoBg: \'#ec4899\',\n                    memoText: \'#ffffff\',\n                    searchBg: \'#fff7ed\',\n                    searchText: \'#9a3412\',\n                    searchBorder: \'#fed7aa\',\n                    eightBg: \'#fdf2f8\',\n                    eightText: \'#9d174d\',\n                    eightBorder: \'#fbcfe8\'\n                },\n                \'dark\': {\n                    page: \'#111827\',\n                    toolbar: \'#1f2937\',\n                    tableWrap: \'#273244\',\n                    th1: \'#334155\',\n                    th2: \'#243041\',\n                    td1: \'#111827\',\n                    td2: \'#172033\',\n                    line: \'#94a3b8\',\n                    text: \'#f8fafc\',\n                    calendarBg: \'#312e81\',\n                    calendarText: \'#ede9fe\',\n                    calendarBorder: \'#4c1d95\',\n                    memoBg: \'#2563eb\',\n                    memoText: \'#ffffff\',\n                    searchBg: \'#3b2f1a\',\n                    searchText: \'#fde68a\',\n                    searchBorder: \'#92400e\',\n                    eightBg: \'#1e3a8a\',\n                    eightText: \'#dbeafe\',\n                    eightBorder: \'#2563eb\'\n                },\n                \'windows\': {\n                    page: \'#f4f7fb\',\n                    toolbar: \'#eef4fb\',\n                    tableWrap: \'#d9e6f5\',\n                    th1: \'#e7f0fb\',\n                    th2: \'#d3e2f4\',\n                    td1: \'#ffffff\',\n                    td2: \'#fbfdff\',\n                    line: \'#1f2937\',\n                    text: \'#0f172a\',\n                    calendarBg: \'#f5f3ff\',\n                    calendarText: \'#6d28d9\',\n                    calendarBorder: \'#ddd6fe\',\n                    memoBg: \'#2563eb\',\n                    memoText: \'#ffffff\',\n                    searchBg: \'#fff7ed\',\n                    searchText: \'#9a3412\',\n                    searchBorder: \'#fed7aa\',\n                    eightBg: \'#eff6ff\',\n                    eightText: \'#1d4ed8\',\n                    eightBorder: \'#bfdbfe\'\n                }\n            };\n\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const s = window.getComputedStyle(el);\n                if (s.display === \'none\' || s.visibility === \'hidden\') return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function textOf(el) {\n                return ((el && (el.innerText || el.textContent)) || \'\').replace(/\\s+/g, \' \').trim();\n            }\n\n            function detectTheme(doc) {\n                const bodyText = doc.body ? (doc.body.innerText || \'\') : \'\';\n                const appText = bodyText.toLowerCase();\n\n                if (bodyText.includes(\'러블리 핑크\')) return \'lovelyPink\';\n                if (appText.includes(\'dark\') || bodyText.includes(\'다크\') || bodyText.includes(\'블랙\') || bodyText.includes(\'야간\')) return \'dark\';\n                if (appText.includes(\'windows\') || bodyText.includes(\'윈도우\')) return \'windows\';\n                return \'default\';\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(STYLE_ID)) return;\n                const style = doc.createElement(\'style\');\n                style.id = STYLE_ID;\n                style.textContent = `\n                    body.step81-theme-default,\n                    body.step81-theme-windows,\n                    body.step81-theme-lovelyPink,\n                    body.step81-theme-dark {\n                        background: var(--step81-page) !important;\n                    }\n                    body.step81-theme-default .stApp,\n                    body.step81-theme-windows .stApp,\n                    body.step81-theme-lovelyPink .stApp,\n                    body.step81-theme-dark .stApp {\n                        background: var(--step81-page) !important;\n                        color: var(--step81-text) !important;\n                    }\n\n                    /* 시간표: 현재 구조는 유지하고 색상만 테마에 맞게 변경 */\n                    body[class*="step81-theme-"] table.mobile-table {\n                        color: var(--step81-text) !important;\n                        border-color: var(--step81-line) !important;\n                    }\n                    body[class*="step81-theme-"] table.mobile-table th {\n                        background-image: linear-gradient(180deg, var(--step81-th1), var(--step81-th2)) !important;\n                        color: var(--step81-text) !important;\n                        border-color: var(--step81-line) !important;\n                    }\n                    body[class*="step81-theme-"] table.mobile-table td {\n                        background-image: linear-gradient(180deg, var(--step81-td1), var(--step81-td2)) !important;\n                        color: var(--step81-text) !important;\n                        border-color: var(--step81-line) !important;\n                    }\n                    body[class*="step81-theme-"] div:has(> table.mobile-table) {\n                        background: var(--step81-table-wrap) !important;\n                    }\n\n                    /* 상단 버튼 공통: 글자 대비 보장 */\n                    .step81-btn-calendar {\n                        background: var(--step81-calendar-bg) !important;\n                        border-color: var(--step81-calendar-border) !important;\n                        color: var(--step81-calendar-text) !important;\n                    }\n                    .step81-btn-memo {\n                        background: var(--step81-memo-bg) !important;\n                        border-color: var(--step81-memo-bg) !important;\n                        color: var(--step81-memo-text) !important;\n                    }\n                    .step81-btn-search {\n                        background: var(--step81-search-bg) !important;\n                        border-color: var(--step81-search-border) !important;\n                        color: var(--step81-search-text) !important;\n                    }\n                    .step81-btn-89 {\n                        background: var(--step81-eight-bg) !important;\n                        border-color: var(--step81-eight-border) !important;\n                        color: var(--step81-eight-text) !important;\n                    }\n                    .step81-btn-calendar *,\n                    .step81-btn-memo *,\n                    .step81-btn-search *,\n                    .step81-btn-89 * {\n                        color: inherit !important;\n                        -webkit-text-fill-color: currentColor !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                    }\n\n                    /*\n                     * 달력 버튼:\n                     * 꺾쇠를 display:none으로만 숨기면 공간이 남으므로,\n                     * JS에서 실제 노드를 remove()하고, CSS로도 grid/flex 폭을 재계산.\n                     */\n                    .step81-calendar-shell {\n                        min-width: 64px !important;\n                        width: 64px !important;\n                        max-width: 64px !important;\n                        flex: 0 0 64px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding: 0 !important;\n                        margin-left: 0 !important;\n                        margin-right: 0 !important;\n                        box-sizing: border-box !important;\n                    }\n                    .step81-calendar-shell,\n                    .step81-calendar-shell * {\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        text-align: center !important;\n                    }\n                    .step81-calendar-shell button,\n                    .step81-calendar-shell [role="button"],\n                    .step81-calendar-shell div[data-baseweb="select"],\n                    .step81-calendar-shell div[data-baseweb="select"] > div {\n                        width: 64px !important;\n                        min-width: 64px !important;\n                        max-width: 64px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        grid-template-columns: 1fr !important;\n                        padding-left: 0 !important;\n                        padding-right: 0 !important;\n                        text-align: center !important;\n                    }\n                    .step81-calendar-shell span,\n                    .step81-calendar-shell p,\n                    .step81-calendar-shell div {\n                        text-align: center !important;\n                    }\n\n                    .step81-removed-chevron {\n                        display: none !important;\n                        width: 0 !important;\n                        min-width: 0 !important;\n                        max-width: 0 !important;\n                        flex: 0 0 0 !important;\n                        padding: 0 !important;\n                        margin: 0 !important;\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function applyThemeVars(doc) {\n                const key = detectTheme(doc);\n                const preset = THEME_PRESETS[key] || THEME_PRESETS.default;\n\n                for (const k of Object.keys(THEME_PRESETS)) {\n                    doc.body.classList.remove(\'step81-theme-\' + k);\n                    const app = doc.querySelector(\'.stApp\');\n                    if (app) app.classList.remove(\'step81-theme-\' + k);\n                }\n                doc.body.classList.add(\'step81-theme-\' + key);\n                const app = doc.querySelector(\'.stApp\');\n                if (app) app.classList.add(\'step81-theme-\' + key);\n\n                const root = doc.body;\n                const map = {\n                    \'--step81-page\': preset.page,\n                    \'--step81-toolbar\': preset.toolbar,\n                    \'--step81-table-wrap\': preset.tableWrap,\n                    \'--step81-th1\': preset.th1,\n                    \'--step81-th2\': preset.th2,\n                    \'--step81-td1\': preset.td1,\n                    \'--step81-td2\': preset.td2,\n                    \'--step81-line\': preset.line,\n                    \'--step81-text\': preset.text,\n                    \'--step81-calendar-bg\': preset.calendarBg,\n                    \'--step81-calendar-text\': preset.calendarText,\n                    \'--step81-calendar-border\': preset.calendarBorder,\n                    \'--step81-memo-bg\': preset.memoBg,\n                    \'--step81-memo-text\': preset.memoText,\n                    \'--step81-search-bg\': preset.searchBg,\n                    \'--step81-search-text\': preset.searchText,\n                    \'--step81-search-border\': preset.searchBorder,\n                    \'--step81-eight-bg\': preset.eightBg,\n                    \'--step81-eight-text\': preset.eightText,\n                    \'--step81-eight-border\': preset.eightBorder\n                };\n                for (const [name, value] of Object.entries(map)) {\n                    root.style.setProperty(name, value);\n                }\n            }\n\n            function findToolbar(doc) {\n                const bars = Array.from(doc.querySelectorAll(\'div[data-testid="stHorizontalBlock"]\')).filter(visible);\n                return bars.find(b => {\n                    const t = textOf(b);\n                    return t.includes(\'오늘\') && t.includes(\'달력\') && t.includes(\'메모\');\n                }) || null;\n            }\n\n            function classify(child) {\n                const t = textOf(child);\n                if (t.includes(\'달력\')) return \'calendar\';\n                if (t.includes(\'메모\')) return \'memo\';\n                if (t.includes(\'조회\')) return \'search\';\n                if (t.includes(\'8·9\') || t.includes(\'8-9\') || t === \'89\' || t.includes(\'89\')) return \'89\';\n                return \'\';\n            }\n\n            function removeCalendarChevron(shell) {\n                const candidates = [];\n\n                for (const svg of Array.from(shell.querySelectorAll(\'svg\'))) {\n                    candidates.push(svg);\n                }\n\n                for (const el of Array.from(shell.querySelectorAll(\'span,div,p\'))) {\n                    const t = (el.textContent || \'\').trim();\n                    if (/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test(t)) candidates.push(el);\n                }\n\n                for (const el of candidates) {\n                    try {\n                        el.remove();\n                    } catch(e) {\n                        el.classList.add(\'step81-removed-chevron\');\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                        el.style.setProperty(\'width\', \'0\', \'important\');\n                        el.style.setProperty(\'flex\', \'0 0 0\', \'important\');\n                    }\n                }\n\n                // BaseWeb select 내부가 2열 grid/flex로 남는 경우 강제 1열 처리\n                for (const el of Array.from(shell.querySelectorAll(\'*\'))) {\n                    const t = textOf(el);\n                    if (t.includes(\'달력\') || el.getAttribute(\'role\') === \'button\' || el.getAttribute(\'data-baseweb\') === \'select\') {\n                        el.style.setProperty(\'grid-template-columns\', \'1fr\', \'important\');\n                        el.style.setProperty(\'justify-content\', \'center\', \'important\');\n                        el.style.setProperty(\'text-align\', \'center\', \'important\');\n                        el.style.setProperty(\'padding-left\', \'0\', \'important\');\n                        el.style.setProperty(\'padding-right\', \'0\', \'important\');\n                    }\n                }\n            }\n\n            function normalizeCalendar(shell) {\n                shell.classList.add(\'step81-calendar-shell\');\n\n                const all = [shell, ...Array.from(shell.querySelectorAll(\'*\'))];\n                for (const el of all) {\n                    const t = (el.textContent || \'\').trim();\n                    if (/^달\\s*력$/.test(t) || t === \'달\' || t === \'력\') {\n                        try { el.textContent = \'달력\'; } catch(e) {}\n                        el.style.setProperty(\'display\', \'flex\', \'important\');\n                        el.style.setProperty(\'align-items\', \'center\', \'important\');\n                        el.style.setProperty(\'justify-content\', \'center\', \'important\');\n                        el.style.setProperty(\'text-align\', \'center\', \'important\');\n                        el.style.setProperty(\'width\', \'100%\', \'important\');\n                    }\n                }\n\n                removeCalendarChevron(shell);\n            }\n\n            function styleButtons(doc) {\n                const bar = findToolbar(doc);\n                if (!bar) return;\n\n                for (const child of Array.from(bar.children || [])) {\n                    const kind = classify(child);\n                    const btn = child.querySelector(\'button,[role="button"],div[data-baseweb="select"]\') || child;\n\n                    if (kind === \'calendar\') {\n                        normalizeCalendar(child);\n                        btn.classList.add(\'step81-btn-calendar\');\n                    } else if (kind === \'memo\') {\n                        btn.classList.add(\'step81-btn-memo\');\n                    } else if (kind === \'search\') {\n                        btn.classList.add(\'step81-btn-search\');\n                    } else if (kind === \'89\') {\n                        btn.classList.add(\'step81-btn-89\');\n                    }\n                }\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                applyThemeVars(doc);\n                styleButtons(doc);\n            }\n\n            run();\n            setTimeout(run, 150);\n            setTimeout(run, 500);\n            setTimeout(run, 1200);\n            setTimeout(run, 2500);\n            setInterval(run, 3000);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_END]\n'
LOVELY_PINK_THEME = '\n    "러블리 핑크": {\n        "bg": "#fff5f8",\n        "card": "#ffffff",\n        "text": "#4a1d2f",\n        "muted": "#9f647a",\n        "primary": "#ec4899",\n        "primary_dark": "#db2777",\n        "accent": "#f9a8d4",\n        "header_bg": "#ffe6ef",\n        "header_bg2": "#ffd3e2",\n        "cell_bg": "#fffafe",\n        "cell_bg2": "#fff7fb",\n        "border": "#f3bfd2",\n        "shadow": "rgba(236, 72, 153, 0.14)",\n    },\n'

REMOVE_MARKERS = [
    ("# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_START]", "# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step81_calendar_theme_refinement_{STAMP}{APP.suffix}")
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


def remove_old_step81(text: str):
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

    insert = LOVELY_PINK_THEME.rstrip() + "\n"
    text = text[:end] + insert + text[end:]
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

    # st.selectbox(..., [ ... ]) 직접 리스트 보정
    pat = r"(st\.selectbox\([^\n]{0,200}(?:테마|theme)[\s\S]{0,500}?\[[^\]]*)\]"
    def repl2(m):
        nonlocal changed
        changed += 1
        return m.group(1).rstrip() + ', "러블리 핑크"]'

    text2, n = re.subn(pat, repl2, text, count=1)
    return text2, changed


def main():
    print("====================================================")
    print("Step81 web calendar/theme refinement")
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
        text, removed = remove_old_step81(text)
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
    print("[완료] Step81 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step81 블록 제거: {removed}")
    print(f"- 러블리 핑크 테마 dict 처리: {theme_dict_status}")
    print(f"- 러블리 핑크 옵션 처리: {option_changes}")
    print("- 달력 꺾쇠 remove() 방식 적용")
    print("- 테마별 시간표/상단 버튼 색상 대비 보정")
    print("- 시각정보는 수정하지 않음")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 달력 버튼에서 꺾쇠 자리까지 사라져 글자가 가운데에 오는지")
    print("2. 테마 변경 시 시간표 색상이 함께 바뀌는지")
    print("3. 테마별 상단 버튼 글씨가 잘 보이는지")
    print("4. 러블리 핑크 테마가 목록에 있는지")
    print("5. 시각정보는 기존처럼 잘 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

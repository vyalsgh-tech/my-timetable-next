# tools/step83_restore_pre82_safe_theme_memo_fix_school_path.py
# ------------------------------------------------------------
# Step83: 학교 경로용 안전 복구 + 테마/메모색상 보정
#
# 목적:
# - Step82 이후 테마 변경 시 runtime error가 발생한 상태를 복구
# - 가장 가까운 Step82 직전 백업으로 되돌린 뒤 안전한 DOM 보정만 추가
#
# 수정:
# 1) 테마 변경 에러 복구: app_before_step82_* 백업 우선 사용
# 2) 메모 literal <span style="color:#...">...</span> 실제 색상 표시
# 3) 테마별 상단 버튼/시간표 색상 대비 보정
# 4) 달력 버튼 중앙 overlay 방식 유지
#
# 유지:
# - Step80의 현재시각 기능은 건드리지 않음
# - Python 테마 로직/옵션을 더 이상 건드리지 않음
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(r"Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next")
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = '\n# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            const STYLE_ID = \'step83-safe-theme-memo-style\';\n\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const s = window.getComputedStyle(el);\n                if (s.display === \'none\' || s.visibility === \'hidden\') return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function textOf(el) {\n                return ((el && (el.innerText || el.textContent)) || \'\').replace(/\\s+/g, \' \').trim();\n            }\n\n            function parseRgb(value) {\n                const m = (value || \'\').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);\n                if (!m) return null;\n                return { r: +m[1], g: +m[2], b: +m[3] };\n            }\n\n            function lum(c) {\n                if (!c) return 255;\n                return 0.299 * c.r + 0.587 * c.g + 0.114 * c.b;\n            }\n\n            function toolbar(doc) {\n                const bars = Array.from(doc.querySelectorAll(\'div[data-testid="stHorizontalBlock"]\')).filter(visible);\n                return bars.find(b => {\n                    const t = textOf(b);\n                    return t.includes(\'오늘\') && t.includes(\'달력\') && t.includes(\'메모\');\n                }) || null;\n            }\n\n            function palette(doc) {\n                const bodyText = doc.body ? (doc.body.innerText || \'\') : \'\';\n                if (bodyText.includes(\'러블리 핑크\')) return \'pink\';\n\n                const bar = toolbar(doc);\n                const bg = bar ? parseRgb(getComputedStyle(bar).backgroundColor) : parseRgb(getComputedStyle(doc.body).backgroundColor);\n                const l = lum(bg);\n\n                if (l < 95) return \'dark\';\n                if (bg && bg.g > bg.r + 20 && bg.g >= bg.b) return \'green\';\n                if (bg && bg.r > 210 && bg.g > 150 && bg.b < 110) return \'orange\';\n                if (bg && bg.b > bg.r + 10 && bg.b > bg.g - 5) return \'blue\';\n\n                const lower = bodyText.toLowerCase();\n                if (lower.includes(\'dark\') || bodyText.includes(\'다크\') || bodyText.includes(\'블랙\') || bodyText.includes(\'야간\')) return \'dark\';\n                if (bodyText.includes(\'그린\') || bodyText.includes(\'초록\') || bodyText.includes(\'숲\')) return \'green\';\n                if (bodyText.includes(\'오렌지\') || bodyText.includes(\'주황\')) return \'orange\';\n                if (bodyText.includes(\'블루\') || bodyText.includes(\'파랑\') || bodyText.includes(\'윈도우\')) return \'blue\';\n                return \'light\';\n            }\n\n            const P = {\n                light: {\n                    tableWrap:\'#dbe8f7\', th1:\'#eaf3ff\', th2:\'#d7e6f8\', td1:\'#ffffff\', td2:\'#fafcff\', line:\'#1f2937\', text:\'#0f172a\',\n                    calBg:\'#f5f0ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#2563eb\', memoText:\'#ffffff\',\n                    searchBg:\'#fff4dd\', searchText:\'#8a4b00\', searchBorder:\'#f2cf96\',\n                    eightBg:\'#eef2ff\', eightText:\'#1e40af\', eightBorder:\'#c7d2fe\'\n                },\n                dark: {\n                    tableWrap:\'#253145\', th1:\'#334155\', th2:\'#243041\', td1:\'#111827\', td2:\'#172033\', line:\'#cbd5e1\', text:\'#f8fafc\',\n                    calBg:\'#ede9fe\', calText:\'#4c1d95\', calBorder:\'#c4b5fd\',\n                    memoBg:\'#e11d48\', memoText:\'#ffffff\',\n                    searchBg:\'#f97316\', searchText:\'#ffffff\', searchBorder:\'#ea580c\',\n                    eightBg:\'#dbeafe\', eightText:\'#1e3a8a\', eightBorder:\'#93c5fd\'\n                },\n                green: {\n                    tableWrap:\'#cfe7dc\', th1:\'#dcfce7\', th2:\'#bbf7d0\', td1:\'#ffffff\', td2:\'#f0fdf4\', line:\'#14532d\', text:\'#052e16\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#ea580c\', memoText:\'#ffffff\',\n                    searchBg:\'#f97316\', searchText:\'#ffffff\', searchBorder:\'#ea580c\',\n                    eightBg:\'#d9f99d\', eightText:\'#365314\', eightBorder:\'#a3e635\'\n                },\n                orange: {\n                    tableWrap:\'#fde7c8\', th1:\'#ffedd5\', th2:\'#fed7aa\', td1:\'#fffaf5\', td2:\'#fff7ed\', line:\'#7c2d12\', text:\'#431407\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#c2410c\', memoText:\'#ffffff\',\n                    searchBg:\'#ea580c\', searchText:\'#ffffff\', searchBorder:\'#c2410c\',\n                    eightBg:\'#ffedd5\', eightText:\'#7c2d12\', eightBorder:\'#fdba74\'\n                },\n                blue: {\n                    tableWrap:\'#dbeafe\', th1:\'#e0f2fe\', th2:\'#bae6fd\', td1:\'#ffffff\', td2:\'#f8fbff\', line:\'#1e3a8a\', text:\'#0f172a\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#2563eb\', memoText:\'#ffffff\',\n                    searchBg:\'#fff7ed\', searchText:\'#9a3412\', searchBorder:\'#fed7aa\',\n                    eightBg:\'#e0f2fe\', eightText:\'#075985\', eightBorder:\'#7dd3fc\'\n                },\n                pink: {\n                    tableWrap:\'#ffe1ec\', th1:\'#ffe6ef\', th2:\'#ffd3e2\', td1:\'#fffefe\', td2:\'#fff7fb\', line:\'#7f1d43\', text:\'#4a1d2f\',\n                    calBg:\'#fff1f7\', calText:\'#be185d\', calBorder:\'#f9a8d4\',\n                    memoBg:\'#ec4899\', memoText:\'#ffffff\',\n                    searchBg:\'#fff1e6\', searchText:\'#9a3412\', searchBorder:\'#fdba74\',\n                    eightBg:\'#fdf2f8\', eightText:\'#9d174d\', eightBorder:\'#fbcfe8\'\n                }\n            };\n\n            function injectStyle(doc) {\n                if (doc.getElementById(STYLE_ID)) return;\n                const style = doc.createElement(\'style\');\n                style.id = STYLE_ID;\n                style.textContent = `\n                    body.step83-safe-theme table.mobile-table {\n                        color: var(--s83-text) !important;\n                        border-color: var(--s83-line) !important;\n                    }\n                    body.step83-safe-theme table.mobile-table th {\n                        background-image: linear-gradient(180deg, var(--s83-th1), var(--s83-th2)) !important;\n                        color: var(--s83-text) !important;\n                        border-color: var(--s83-line) !important;\n                    }\n                    body.step83-safe-theme table.mobile-table td {\n                        background-image: linear-gradient(180deg, var(--s83-td1), var(--s83-td2)) !important;\n                        color: var(--s83-text) !important;\n                        border-color: var(--s83-line) !important;\n                    }\n                    body.step83-safe-theme div:has(> table.mobile-table) {\n                        background: var(--s83-table-wrap) !important;\n                    }\n\n                    .s83-btn-calendar, .s83-btn-memo, .s83-btn-search, .s83-btn-89 {\n                        box-sizing: border-box !important;\n                        min-height: 40px !important;\n                        height: 40px !important;\n                        border-radius: 7px !important;\n                        font-weight: 800 !important;\n                        text-align: center !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                    }\n                    .s83-btn-calendar *, .s83-btn-memo *, .s83-btn-search *, .s83-btn-89 * {\n                        color: inherit !important;\n                        -webkit-text-fill-color: currentColor !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        text-align: center !important;\n                    }\n                    .s83-btn-calendar {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        flex: 0 0 58px !important;\n                        background: var(--s83-cal-bg) !important;\n                        border: 1px solid var(--s83-cal-border) !important;\n                        color: var(--s83-cal-text) !important;\n                        padding: 0 !important;\n                        position: relative !important;\n                        overflow: hidden !important;\n                    }\n                    .s83-btn-memo {\n                        background: var(--s83-memo-bg) !important;\n                        border: 1px solid var(--s83-memo-bg) !important;\n                        color: var(--s83-memo-text) !important;\n                    }\n                    .s83-btn-search {\n                        background: var(--s83-search-bg) !important;\n                        border: 1px solid var(--s83-search-border) !important;\n                        color: var(--s83-search-text) !important;\n                    }\n                    .s83-btn-89 {\n                        background: var(--s83-eight-bg) !important;\n                        border: 1px solid var(--s83-eight-border) !important;\n                        color: var(--s83-eight-text) !important;\n                    }\n\n                    .s83-calendar-shell {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        flex: 0 0 58px !important;\n                        position: relative !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding: 0 !important;\n                        box-sizing: border-box !important;\n                    }\n                    .s83-calendar-shell > * {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                    }\n                    .s83-calendar-shell [data-baseweb="select"], .s83-calendar-shell [role="button"], .s83-calendar-shell button {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        grid-template-columns: 1fr !important;\n                        padding-left: 0 !important;\n                        padding-right: 0 !important;\n                        color: transparent !important;\n                        -webkit-text-fill-color: transparent !important;\n                    }\n                    .s83-calendar-shell [data-baseweb="select"] *, .s83-calendar-shell [role="button"] *, .s83-calendar-shell button * {\n                        color: transparent !important;\n                        -webkit-text-fill-color: transparent !important;\n                    }\n                    .s83-calendar-shell svg, .s83-calendar-shell [aria-hidden="true"], .s83-remove {\n                        display: none !important;\n                        width: 0 !important;\n                        min-width: 0 !important;\n                        max-width: 0 !important;\n                        flex: 0 0 0 !important;\n                        margin: 0 !important;\n                        padding: 0 !important;\n                    }\n                    .s83-calendar-overlay {\n                        position: absolute !important;\n                        inset: 0 !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        pointer-events: none !important;\n                        color: var(--s83-cal-text) !important;\n                        -webkit-text-fill-color: var(--s83-cal-text) !important;\n                        font-size: 14px !important;\n                        font-weight: 800 !important;\n                        line-height: 1 !important;\n                        text-align: center !important;\n                        z-index: 3 !important;\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function applyVars(doc) {\n                const key = palette(doc);\n                const p = P[key] || P.light;\n                doc.body.classList.add(\'step83-safe-theme\');\n                const vars = {\n                    \'--s83-table-wrap\': p.tableWrap, \'--s83-th1\': p.th1, \'--s83-th2\': p.th2, \'--s83-td1\': p.td1, \'--s83-td2\': p.td2,\n                    \'--s83-line\': p.line, \'--s83-text\': p.text,\n                    \'--s83-cal-bg\': p.calBg, \'--s83-cal-text\': p.calText, \'--s83-cal-border\': p.calBorder,\n                    \'--s83-memo-bg\': p.memoBg, \'--s83-memo-text\': p.memoText,\n                    \'--s83-search-bg\': p.searchBg, \'--s83-search-text\': p.searchText, \'--s83-search-border\': p.searchBorder,\n                    \'--s83-eight-bg\': p.eightBg, \'--s83-eight-text\': p.eightText, \'--s83-eight-border\': p.eightBorder\n                };\n                for (const [k, v] of Object.entries(vars)) doc.body.style.setProperty(k, v);\n            }\n\n            function classify(child) {\n                const t = textOf(child);\n                if (t.includes(\'달력\')) return \'calendar\';\n                if (t.includes(\'메모\')) return \'memo\';\n                if (t.includes(\'조회\')) return \'search\';\n                if (t.includes(\'8·9\') || t.includes(\'8-9\') || t === \'89\' || t.includes(\'89\')) return \'89\';\n                return \'\';\n            }\n\n            function target(child) {\n                return child.querySelector(\'button,[role="button"],div[data-baseweb="select"]\') || child;\n            }\n\n            function calendar(child, doc) {\n                child.classList.add(\'s83-calendar-shell\');\n                const btn = target(child);\n                btn.classList.add(\'s83-btn-calendar\');\n\n                const removable = [];\n                for (const svg of Array.from(child.querySelectorAll(\'svg\'))) removable.push(svg);\n                for (const el of Array.from(child.querySelectorAll(\'span,div,p\'))) {\n                    const t = (el.textContent || \'\').trim();\n                    if (/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test(t)) removable.push(el);\n                }\n                for (const el of removable) {\n                    try { el.remove(); }\n                    catch(e) {\n                        el.classList.add(\'s83-remove\');\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                    }\n                }\n\n                let overlay = child.querySelector(\'.s83-calendar-overlay\');\n                if (!overlay) {\n                    overlay = doc.createElement(\'span\');\n                    overlay.className = \'s83-calendar-overlay\';\n                    overlay.textContent = \'달력\';\n                    child.appendChild(overlay);\n                }\n            }\n\n            function buttons(doc) {\n                const bar = toolbar(doc);\n                if (!bar) return;\n                for (const child of Array.from(bar.children || [])) {\n                    const kind = classify(child);\n                    const btn = target(child);\n                    if (kind === \'calendar\') calendar(child, doc);\n                    else if (kind === \'memo\') btn.classList.add(\'s83-btn-memo\');\n                    else if (kind === \'search\') btn.classList.add(\'s83-btn-search\');\n                    else if (kind === \'89\') btn.classList.add(\'s83-btn-89\');\n                }\n            }\n\n            function parseMemoColor(doc) {\n                const allowed = /<span\\s+style=["\']\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*["\']>(.*?)<\\/span>/gis;\n                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);\n                const nodes = [];\n                let node;\n                while ((node = walker.nextNode())) {\n                    const v = node.nodeValue || \'\';\n                    allowed.lastIndex = 0;\n                    if (v.includes(\'<span\') && allowed.test(v)) nodes.push(node);\n                }\n                for (const textNode of nodes) {\n                    const text = textNode.nodeValue || \'\';\n                    const frag = doc.createDocumentFragment();\n                    let last = 0;\n                    allowed.lastIndex = 0;\n                    let m;\n                    while ((m = allowed.exec(text))) {\n                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));\n                        const span = doc.createElement(\'span\');\n                        span.style.setProperty(m[1].toLowerCase(), m[2]);\n                        span.textContent = m[3];\n                        frag.appendChild(span);\n                        last = allowed.lastIndex;\n                    }\n                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));\n                    textNode.parentNode.replaceChild(frag, textNode);\n                }\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                applyVars(doc);\n                buttons(doc);\n                parseMemoColor(doc);\n            }\n\n            run();\n            setTimeout(run, 150);\n            setTimeout(run, 500);\n            setTimeout(run, 1200);\n            setTimeout(run, 2500);\n            setInterval(run, 3000);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_END]\n'

REMOVE_MARKERS = [
    ("# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_START]", "# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_END]"),
    ("# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_START]", "# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step83_restore_pre82_{STAMP}{APP.suffix}")
    b.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[현재 백업] {b}")


def compiles(text: str, name: str):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def choose_base():
    # Step82 적용 직전 백업이 runtime error 이전 상태
    patterns = [
        "app_before_step82_theme_button_calendar_*.py",
        "app_before_step81_calendar_theme_refinement_*.py",
        "app_before_step80_topbar_theme_*.py",
        "app_before_step79_topbar_fix_*.py",
        "app_before_step78_top_clock_calendar_*.py",
        "app_before_step77_restore_exact_*.py",
    ]

    for pat in patterns:
        candidates = sorted(APP.parent.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        for b in candidates:
            text = b.read_text(encoding="utf-8", errors="replace")
            ok, err = compiles(text, str(b))
            print(f"[검토] {b.name} -> {'OK' if ok else 'FAIL'}")
            if ok:
                return text, b

    # fallback: 현재 파일이 컴파일 가능하면 현재 파일에서 Step82만 제거
    text = APP.read_text(encoding="utf-8", errors="replace")
    ok, err = compiles(text, str(APP))
    if ok:
        print("[안내] 적절한 백업을 찾지 못해 현재 app.py를 기준으로 진행")
        return text, None

    raise RuntimeError("컴파일 가능한 Step82 이전 백업을 찾지 못했습니다.")


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


def main():
    print("====================================================")
    print("Step83 restore pre82 + safe theme/memo fix")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    try:
        text, base = choose_base()
        text, removed = remove_old_blocks(text)
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
    print("[완료] Step83 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 복구 기준: {base}")
    print(f"- 기존 Step82/83 블록 제거: {removed}")
    print("- Python 테마 옵션/로직은 더 이상 건드리지 않음")
    print("- 메모 색상 span 표시 복구")
    print("- 테마별 버튼/시간표 색상 대비 DOM 보정")
    print("- 현재시각 기능은 수정하지 않음")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 테마 변경 시 에러가 사라졌는지")
    print("2. 메모 색상 코드가 실제 색상으로 표시되는지")
    print("3. 상단 버튼 글자가 테마별로 잘 보이는지")
    print("4. 현재시각은 기존처럼 잘 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

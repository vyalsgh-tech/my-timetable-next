# tools/step80_web_topbar_theme_lovely_pink.py
# ------------------------------------------------------------
# Step80: 웹뷰어 상단바 + 러블리 핑크 테마
#
# 수정:
# 1) 시각 표시 깜박임 방지: 고정 배지로 'HH:MM 수업 전/방과 후/교시' 표시
# 2) 달력 글자 가운데 정렬
# 3) 달력 꺾쇠 숨김
# 4) 달력/메모/조회/8·9 버튼을 PC버전 계열 색상으로 보정
# 5) 테마 '러블리 핑크' 추가 시도
# 6) 러블리 핑크 선택 시 시간표 테이블 색상도 맞춤 적용
#
# 시간표/메모 데이터 구조는 건드리지 않음.
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = '\n# [STEP80_WEB_TOPBAR_AND_THEME_DOM_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            const CLOCK_ID = \'step80-clock-fixed\';\n            const STYLE_ID = \'step80-web-topbar-theme-style\';\n\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const s = window.getComputedStyle(el);\n                if (s.display === \'none\' || s.visibility === \'hidden\') return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function nowInfo() {\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n                const periods = [\n                    [\'1교시\', \'08:00\', \'08:50\'],\n                    [\'2교시\', \'09:00\', \'09:50\'],\n                    [\'3교시\', \'10:00\', \'10:50\'],\n                    [\'4교시\', \'11:00\', \'11:50\'],\n                    [\'점심\', \'11:50\', \'12:40\'],\n                    [\'5교시\', \'12:40\', \'13:30\'],\n                    [\'6교시\', \'13:40\', \'14:30\'],\n                    [\'7교시\', \'14:40\', \'15:30\'],\n                    [\'8교시\', \'16:00\', \'16:50\'],\n                    [\'9교시\', \'17:00\', \'17:50\']\n                ];\n                function toMin(t) {\n                    const p = t.split(\':\').map(Number);\n                    return p[0] * 60 + p[1];\n                }\n                let state = \'쉬는시간\';\n                for (const p of periods) {\n                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {\n                        state = p[0];\n                        break;\n                    }\n                }\n                if (mins < 8 * 60) state = \'수업 전\';\n                if (mins >= 17 * 60 + 50) state = \'방과 후\';\n\n                const hh = String(now.getHours()).padStart(2, \'0\');\n                const mm = String(now.getMinutes()).padStart(2, \'0\');\n                return { clock: hh + \':\' + mm, state: state, text: hh + \':\' + mm + \' \' + state };\n            }\n\n            function toolbar(doc) {\n                const blocks = Array.from(doc.querySelectorAll(\'div[data-testid="stHorizontalBlock"]\')).filter(visible);\n                return blocks.find(b => {\n                    const t = (b.innerText || \'\').replace(/\\s+/g, \' \');\n                    return t.includes(\'오늘\') && t.includes(\'달력\') && t.includes(\'메모\');\n                }) || null;\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(STYLE_ID)) return;\n                const style = doc.createElement(\'style\');\n                style.id = STYLE_ID;\n                style.textContent = `\n                    #${CLOCK_ID} {\n                        position: fixed !important;\n                        right: max(10px, calc((100vw - min(450px, 100vw)) / 2 + 8px)) !important;\n                        top: 8px !important;\n                        z-index: 999999 !important;\n                        display: inline-flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding: 4px 10px !important;\n                        border-radius: 999px !important;\n                        border: 1px solid rgba(96, 165, 250, 0.36) !important;\n                        background: linear-gradient(180deg, rgba(250,252,255,0.98), rgba(232,240,255,0.96)) !important;\n                        color: #1d4ed8 !important;\n                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12) !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        font-size: 12px !important;\n                        line-height: 1.1 !important;\n                        font-weight: 800 !important;\n                        text-align: center !important;\n                        pointer-events: none !important;\n                    }\n\n                    .step80-calendar-box,\n                    .step80-calendar-box * {\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        text-align: center !important;\n                    }\n                    .step80-calendar-box {\n                        min-width: 64px !important;\n                        width: 64px !important;\n                        max-width: 64px !important;\n                        flex: 0 0 64px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding-left: 0 !important;\n                        padding-right: 0 !important;\n                        box-sizing: border-box !important;\n                    }\n                    .step80-calendar-box button,\n                    .step80-calendar-box [role="button"],\n                    .step80-calendar-box div[data-baseweb="select"],\n                    .step80-calendar-box div[data-baseweb="select"] > div {\n                        justify-content: center !important;\n                        text-align: center !important;\n                        padding-left: 0 !important;\n                        padding-right: 0 !important;\n                        min-width: 64px !important;\n                        width: 64px !important;\n                    }\n                    .step80-calendar-box svg,\n                    .step80-calendar-box [aria-hidden="true"],\n                    .step80-calendar-chevron {\n                        display: none !important;\n                    }\n\n                    .step80-topbar-btn-calendar {\n                        background: #f4efff !important;\n                        border: 1px solid #dfd3ff !important;\n                        color: #6d28d9 !important;\n                    }\n                    .step80-topbar-btn-memo {\n                        background: #2563eb !important;\n                        border: 1px solid #2563eb !important;\n                        color: #ffffff !important;\n                    }\n                    .step80-topbar-btn-search {\n                        background: #fff7e6 !important;\n                        border: 1px solid #f1d6a8 !important;\n                        color: #8a4b00 !important;\n                    }\n                    .step80-topbar-btn-89 {\n                        background: #eef2ff !important;\n                        border: 1px solid #d8defa !important;\n                        color: #1e40af !important;\n                    }\n                    .step80-topbar-btn-calendar *,\n                    .step80-topbar-btn-memo *,\n                    .step80-topbar-btn-search *,\n                    .step80-topbar-btn-89 * {\n                        color: inherit !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                    }\n\n                    body.step80-lovely-pink,\n                    .stApp.step80-lovely-pink {\n                        background: #fff5f8 !important;\n                    }\n                    body.step80-lovely-pink table.mobile-table th {\n                        background-image: linear-gradient(180deg, #ffe6ef 0%, #ffd3e2 100%) !important;\n                    }\n                    body.step80-lovely-pink table.mobile-table td {\n                        background-image: linear-gradient(180deg, #fffefe 0%, #fff7fa 100%) !important;\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function makeClock(doc) {\n                const info = nowInfo();\n\n                const stateTexts = new Set([\'수업 전\', \'방과 후\', \'쉬는시간\', \'1교시\', \'2교시\', \'3교시\', \'4교시\', \'점심\', \'5교시\', \'6교시\', \'7교시\', \'8교시\', \'9교시\']);\n                for (const el of Array.from(doc.querySelectorAll(\'div,p,span\'))) {\n                    const txt = (el.innerText || \'\').trim();\n                    if (!stateTexts.has(txt)) continue;\n                    const r = el.getBoundingClientRect();\n                    if (r.top < 90 && r.left > window.innerWidth * 0.45) {\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                    }\n                }\n\n                let badge = doc.getElementById(CLOCK_ID);\n                if (!badge) {\n                    badge = doc.createElement(\'div\');\n                    badge.id = CLOCK_ID;\n                    doc.body.appendChild(badge);\n                }\n                badge.textContent = info.text;\n            }\n\n            function elementText(el) {\n                return ((el && (el.innerText || el.textContent)) || \'\').replace(/\\s+/g, \' \').trim();\n            }\n\n            function classifyChild(child) {\n                const txt = elementText(child);\n                const html = child.innerHTML || \'\';\n                if (txt.includes(\'오늘\')) return \'today\';\n                if (txt.includes(\'달력\')) return \'calendar\';\n                if (txt.includes(\'메모\')) return \'memo\';\n                if (txt === \'조회\' || txt.includes(\'조회\')) return \'search\';\n                if (txt.includes(\'8·9\') || txt.includes(\'8-9\') || txt === \'89\' || txt.includes(\'89\')) return \'89\';\n                if (txt.includes(\'⚙\') || txt.includes(\'설정\')) return \'settings\';\n                if (/^[▾∨⌄˅﹀vV]$/.test(txt)) return \'chevron\';\n                if (/refresh|sync|rotate|reload|arrow-repeat|counterclockwise|clockwise/i.test(html)) return \'sync\';\n                if (txt === \'↻\' || txt === \'⟳\' || txt === \'🔄\') return \'sync\';\n                if (txt === \'\' || txt.length <= 2) {\n                    const r = child.getBoundingClientRect();\n                    if (r.width <= 34) return \'icon\';\n                }\n                return \'other\';\n            }\n\n            function normalizeCalendarBox(box) {\n                box.classList.add(\'step80-calendar-box\');\n                box.style.setProperty(\'min-width\', \'64px\', \'important\');\n                box.style.setProperty(\'width\', \'64px\', \'important\');\n                box.style.setProperty(\'max-width\', \'64px\', \'important\');\n                box.style.setProperty(\'flex\', \'0 0 64px\', \'important\');\n                box.style.setProperty(\'display\', \'flex\', \'important\');\n                box.style.setProperty(\'align-items\', \'center\', \'important\');\n                box.style.setProperty(\'justify-content\', \'center\', \'important\');\n                box.style.setProperty(\'text-align\', \'center\', \'important\');\n                box.style.setProperty(\'padding-left\', \'0\', \'important\');\n                box.style.setProperty(\'padding-right\', \'0\', \'important\');\n\n                for (const el of Array.from(box.querySelectorAll(\'*\'))) {\n                    const txt = (el.textContent || \'\').trim();\n                    if (/^달\\s*력$/.test(txt) || txt === \'달\' || txt === \'력\') {\n                        try { el.textContent = \'달력\'; } catch(e) {}\n                        el.style.setProperty(\'display\', \'inline-flex\', \'important\');\n                        el.style.setProperty(\'align-items\', \'center\', \'important\');\n                        el.style.setProperty(\'justify-content\', \'center\', \'important\');\n                        el.style.setProperty(\'text-align\', \'center\', \'important\');\n                        el.style.setProperty(\'width\', \'100%\', \'important\');\n                        el.style.setProperty(\'white-space\', \'nowrap\', \'important\');\n                    }\n                }\n\n                for (const svg of Array.from(box.querySelectorAll(\'svg\'))) {\n                    svg.classList.add(\'step80-calendar-chevron\');\n                    svg.style.setProperty(\'display\', \'none\', \'important\');\n                }\n                for (const el of Array.from(box.querySelectorAll(\'span,div\'))) {\n                    const txt = (el.textContent || \'\').trim();\n                    if (/^[▾∨⌄˅﹀vV]$/.test(txt)) {\n                        el.classList.add(\'step80-calendar-chevron\');\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                    }\n                }\n            }\n\n            function styleTopbarButtons(toolbar) {\n                for (const child of Array.from(toolbar.children || [])) {\n                    const kind = classifyChild(child);\n                    const btn = child.querySelector(\'button,[role="button"],div[data-baseweb="select"]\') || child;\n                    if (kind === \'calendar\') {\n                        normalizeCalendarBox(child);\n                        btn.classList.add(\'step80-topbar-btn-calendar\');\n                    } else if (kind === \'memo\') {\n                        btn.classList.add(\'step80-topbar-btn-memo\');\n                    } else if (kind === \'search\') {\n                        btn.classList.add(\'step80-topbar-btn-search\');\n                    } else if (kind === \'89\') {\n                        btn.classList.add(\'step80-topbar-btn-89\');\n                    }\n                }\n            }\n\n            function reorderTopbar(doc) {\n                const bar = toolbar(doc);\n                if (!bar) return;\n\n                bar.style.setProperty(\'display\', \'flex\', \'important\');\n                bar.style.setProperty(\'align-items\', \'center\', \'important\');\n                bar.style.setProperty(\'gap\', \'3px\', \'important\');\n\n                const children = Array.from(bar.children || []);\n                let todayIdx = -1;\n                children.forEach((child, idx) => {\n                    if (classifyChild(child) === \'today\') todayIdx = idx;\n                });\n\n                let beforeTodayArrowUsed = false;\n                let afterTodayArrowUsed = false;\n                let syncAssigned = false;\n\n                children.forEach((child, idx) => {\n                    const kind = classifyChild(child);\n                    let order = 900 + idx;\n\n                    if (kind === \'today\') order = 20;\n                    else if (kind === \'calendar\') order = 40;\n                    else if (kind === \'memo\') order = 60;\n                    else if (kind === \'search\') order = 70;\n                    else if (kind === \'89\') order = 80;\n                    else if (kind === \'settings\') order = 100;\n                    else if (kind === \'sync\') {\n                        order = 90;\n                        syncAssigned = true;\n                    } else if (kind === \'chevron\') {\n                        child.style.setProperty(\'display\', \'none\', \'important\');\n                        return;\n                    } else if (kind === \'icon\') {\n                        if (todayIdx >= 0 && idx < todayIdx && !beforeTodayArrowUsed) {\n                            order = 10;\n                            beforeTodayArrowUsed = true;\n                        } else if (todayIdx >= 0 && idx > todayIdx && !afterTodayArrowUsed) {\n                            order = 30;\n                            afterTodayArrowUsed = true;\n                        } else if (!syncAssigned) {\n                            order = 90;\n                            syncAssigned = true;\n                        }\n                    }\n\n                    child.style.setProperty(\'order\', String(order), \'important\');\n                });\n\n                styleTopbarButtons(bar);\n            }\n\n            function applyLovelyPinkIfSelected(doc) {\n                const bodyText = doc.body ? (doc.body.innerText || \'\') : \'\';\n                const isPink = bodyText.includes(\'러블리 핑크\') && bodyText.includes(\'명덕외고 시간표\');\n                doc.body.classList.toggle(\'step80-lovely-pink\', !!isPink);\n                const app = doc.querySelector(\'.stApp\');\n                if (app) app.classList.toggle(\'step80-lovely-pink\', !!isPink);\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                makeClock(doc);\n                reorderTopbar(doc);\n                applyLovelyPinkIfSelected(doc);\n            }\n\n            run();\n            setTimeout(run, 150);\n            setTimeout(run, 500);\n            setTimeout(run, 1200);\n            setTimeout(run, 2500);\n            setInterval(run, 3000);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP80_WEB_TOPBAR_AND_THEME_DOM_END]\n'
LOVELY_PINK_THEME = '\n    "러블리 핑크": {\n        "bg": "#fff5f8",\n        "card": "#ffffff",\n        "text": "#4a1d2f",\n        "muted": "#9f647a",\n        "primary": "#ec4899",\n        "primary_dark": "#db2777",\n        "accent": "#f9a8d4",\n        "header_bg": "#ffe6ef",\n        "header_bg2": "#ffd3e2",\n        "cell_bg": "#fffafe",\n        "cell_bg2": "#fff7fb",\n        "border": "#f3bfd2",\n        "shadow": "rgba(236, 72, 153, 0.14)",\n    },\n'

REMOVE_MARKERS = [
    ("# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_START]", "# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_END]"),
    ("# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_START]", "# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_END]"),
    ("# [STEP80_WEB_TOPBAR_AND_THEME_DOM_START]", "# [STEP80_WEB_TOPBAR_AND_THEME_DOM_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step80_topbar_theme_{STAMP}{APP.suffix}")
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

    insert = LOVELY_PINK_THEME.rstrip() + "\n"
    text = text[:end] + insert + text[end:]
    return text, "theme_dict_added"


def add_lovely_pink_to_theme_options(text: str):
    changed = 0
    if "러블리 핑크" in text:
        return text, 0

    pattern = re.compile(r"(\[[^\[\]]{0,600}(?:윈도우|라이트|다크|블루|핑크|테마)[^\[\]]{0,600}\])", re.S)

    def repl(match):
        nonlocal changed
        block = match.group(1)
        if "러블리 핑크" in block:
            return block
        if not re.search(r"['\"][^'\"]+['\"]", block):
            return block
        changed += 1
        return block[:-1].rstrip() + ', "러블리 핑크"]'

    text2 = pattern.sub(repl, text, count=1)
    return text2, changed


def patch_calendar_literal(text: str):
    changed = 0
    replacements = [
        ('"달\\\\n력"', '"달력"'),
        ("'달\\\\n력'", "'달력'"),
        ('"달\\n력"', '"달력"'),
        ("'달\\n력'", "'달력'"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    return text, changed


def main():
    print("====================================================")
    print("Step80 web topbar/theme lovely pink")
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
        print("먼저 정상 실행되는 Step77/78/79 상태로 복구한 뒤 다시 실행해주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        text, removed = remove_old_blocks(text)
        text, literal_changes = patch_calendar_literal(text)
        text, theme_dict_status = add_lovely_pink_to_theme_dict(text)
        text, theme_option_changes = add_lovely_pink_to_theme_options(text)

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
    print("[완료] Step80 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step78/79/80 블록 제거: {removed}")
    print(f"- 달력 문자열 보정: {literal_changes}")
    print(f"- 러블리 핑크 테마 dict 처리: {theme_dict_status}")
    print(f"- 러블리 핑크 옵션 리스트 처리: {theme_option_changes}")
    print("- 상단 시각 배지는 고정 배지 방식으로 깜박임 방지")
    print("- 달력 가운데 정렬 / 꺾쇠 숨김")
    print("- 달력/메모/조회/8·9 버튼 색상 보정")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 우측 상단에 'HH:MM 수업 전/방과 후/교시'가 계속 유지되는지")
    print("2. 달력 글자가 가운데 정렬되는지")
    print("3. 달력 꺾쇠가 사라지는지")
    print("4. 달력/메모/조회/8·9 색상이 PC버전 계열로 보이는지")
    print("5. 테마 목록에 '러블리 핑크'가 추가됐는지")
    print("6. 러블리 핑크 선택 시 시간표가 핑크 계열로 보정되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

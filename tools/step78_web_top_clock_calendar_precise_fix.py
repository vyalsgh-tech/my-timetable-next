# tools/step78_web_top_clock_calendar_precise_fix.py
# ------------------------------------------------------------
# Step78: 현재 상태 유지 + 상단 시각/달력만 정밀 보정
#
# 건드리지 않음:
# - 시간표 디자인
# - 메모 구조
# - 학사일정 넘침 보정
#
# 수정:
# 1) 기존 상단의 '수업 전/방과 후'만 보이는 상태표시에 시간을 붙임
# 2) 달력 글자 가운데 정렬
# 3) 달력 오른쪽 아래화살표가 새로고침 버튼과 겹치는 문제 해결
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = '\n# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function currentInfo() {\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n                const periods = [\n                    [\'1교시\', \'08:00\', \'08:50\'],\n                    [\'2교시\', \'09:00\', \'09:50\'],\n                    [\'3교시\', \'10:00\', \'10:50\'],\n                    [\'4교시\', \'11:00\', \'11:50\'],\n                    [\'점심\', \'11:50\', \'12:40\'],\n                    [\'5교시\', \'12:40\', \'13:30\'],\n                    [\'6교시\', \'13:40\', \'14:30\'],\n                    [\'7교시\', \'14:40\', \'15:30\'],\n                    [\'8교시\', \'16:00\', \'16:50\'],\n                    [\'9교시\', \'17:00\', \'17:50\']\n                ];\n\n                function toMin(t) {\n                    const p = t.split(\':\').map(Number);\n                    return p[0] * 60 + p[1];\n                }\n\n                let state = \'쉬는시간\';\n                for (const p of periods) {\n                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {\n                        state = p[0];\n                        break;\n                    }\n                }\n                if (mins < 8 * 60) state = \'수업 전\';\n                if (mins >= 17 * 60 + 50) state = \'방과 후\';\n\n                const hh = String(now.getHours()).padStart(2, \'0\');\n                const mm = String(now.getMinutes()).padStart(2, \'0\');\n                return { clock: hh + \':\' + mm, state: state };\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(\'step78-web-fix-style\')) return;\n                const style = doc.createElement(\'style\');\n                style.id = \'step78-web-fix-style\';\n                style.textContent = `\n                    .step78-clock-badge {\n                        display: inline-flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        gap: 5px !important;\n                        padding: 4px 9px !important;\n                        border-radius: 999px !important;\n                        border: 1px solid rgba(96, 165, 250, 0.34) !important;\n                        background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95)) !important;\n                        color: #1e40af !important;\n                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12) !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        font-size: 12px !important;\n                        line-height: 1.1 !important;\n                        font-weight: 700 !important;\n                        text-decoration: none !important;\n                    }\n\n                    .step77-clock-pill,\n                    .step76-clock-pill,\n                    .step75-clock-pill,\n                    .step74-clock-pill {\n                        display: inline-flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        gap: 5px !important;\n                        padding: 4px 9px !important;\n                        border-radius: 999px !important;\n                        border: 1px solid rgba(96, 165, 250, 0.34) !important;\n                        background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95)) !important;\n                        color: #1e40af !important;\n                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12) !important;\n                        white-space: nowrap !important;\n                        font-size: 12px !important;\n                        line-height: 1.1 !important;\n                    }\n\n                    .step77-clock-time,\n                    .step76-clock-time,\n                    .step75-clock-time,\n                    .step74-clock-time {\n                        display: inline !important;\n                        font-size: 13px !important;\n                        font-weight: 800 !important;\n                    }\n\n                    .step77-clock-state,\n                    .step76-clock-state,\n                    .step75-clock-state,\n                    .step74-clock-state {\n                        display: inline !important;\n                        font-size: 12px !important;\n                        opacity: 0.92 !important;\n                    }\n\n                    /* 달력 selectbox: 글자 가운데 정렬 + 내부 화살표 숨김 */\n                    .step78-calendar-box,\n                    .step78-calendar-box * {\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        text-align: center !important;\n                    }\n\n                    .step78-calendar-box {\n                        min-width: 64px !important;\n                        width: 64px !important;\n                        flex: 0 0 64px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        box-sizing: border-box !important;\n                    }\n\n                    .step78-calendar-box svg,\n                    .step78-calendar-box [aria-hidden="true"] {\n                        display: none !important;\n                    }\n\n                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(.step78-calendar-box) {\n                        min-width: 68px !important;\n                        width: 68px !important;\n                        flex: 0 0 68px !important;\n                    }\n\n                    @media (max-width: 430px) {\n                        .step78-clock-badge {\n                            padding: 4px 8px !important;\n                            font-size: 12px !important;\n                        }\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function patchClock(doc) {\n                const info = currentInfo();\n                const text = info.clock + \' \' + info.state;\n\n                // 1순위: 이전 Step77류 clock pill이 있으면 그 안을 강제 교체\n                const oldPill = doc.querySelector(\'.step77-clock-pill, .step76-clock-pill, .step75-clock-pill, .step74-clock-pill\');\n                if (oldPill) {\n                    oldPill.innerHTML = \'<span class="step77-clock-time">\' + info.clock + \'</span><span class="step77-clock-state">\' + info.state + \'</span>\';\n                    oldPill.style.display = \'inline-flex\';\n                    return;\n                }\n\n                // 2순위: 화면 상단에 이미 "수업 전/방과 후/쉬는시간"만 떠 있는 요소를 배지로 변환\n                const statusWords = [\'수업 전\', \'방과 후\', \'쉬는시간\'];\n                const candidates = Array.from(doc.querySelectorAll(\'div,p,span\')).filter(el => {\n                    if (!visible(el)) return false;\n                    const t = (el.innerText || \'\').trim();\n                    const r = el.getBoundingClientRect();\n                    return statusWords.includes(t) && r.top < 110;\n                });\n\n                if (candidates.length) {\n                    const target = candidates[0];\n                    target.textContent = text;\n                    target.classList.add(\'step78-clock-badge\');\n\n                    const p = target.parentElement;\n                    if (p) {\n                        p.style.setProperty(\'text-align\', \'right\', \'important\');\n                        p.style.setProperty(\'width\', \'min(450px, 100%)\', \'important\');\n                    }\n\n                    for (let i = 1; i < candidates.length; i++) {\n                        candidates[i].style.display = \'none\';\n                    }\n                    return;\n                }\n\n                // 3순위: 제목 줄 오른쪽에 새 배지 추가\n                const title = Array.from(doc.querySelectorAll(\'h1,h2,h3,p,span,div\')).find(el => {\n                    if (!visible(el)) return false;\n                    const t = (el.innerText || \'\').trim();\n                    return t.includes(\'명덕외고 시간표 뷰어\');\n                });\n\n                if (!title || !title.parentElement) return;\n\n                let row = doc.querySelector(\'.step78-title-row\');\n                if (!row) {\n                    row = doc.createElement(\'div\');\n                    row.className = \'step78-title-row\';\n                    row.style.cssText = \'width:min(450px,100%);display:flex;align-items:center;justify-content:space-between;gap:8px;margin:0 0 8px 0;\';\n\n                    const host = doc.createElement(\'div\');\n                    host.style.cssText = \'flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;\';\n\n                    title.parentNode.insertBefore(row, title);\n                    row.appendChild(host);\n                    host.appendChild(title);\n                }\n\n                let badge = row.querySelector(\'.step78-clock-badge\');\n                if (!badge) {\n                    badge = doc.createElement(\'div\');\n                    badge.className = \'step78-clock-badge\';\n                    row.appendChild(badge);\n                }\n                badge.textContent = text;\n            }\n\n            function fixCalendar(doc) {\n                const nodes = Array.from(doc.querySelectorAll(\'[data-testid="stSelectbox"], [data-baseweb="select"], div[role="button"], button, span, div\'));\n                const targets = nodes.filter(el => {\n                    const txt = (el.innerText || el.textContent || \'\').trim();\n                    return /^달\\s*력$/.test(txt);\n                });\n\n                for (const el of targets) {\n                    try {\n                        if ((el.innerText || \'\').includes(\'\\n\')) el.innerText = \'달력\';\n                    } catch(e) {}\n\n                    let box = el;\n                    for (let i = 0; i < 8 && box; i++, box = box.parentElement) {\n                        const txt = (box.innerText || \'\').trim();\n                        if (/달\\s*력/.test(txt) && txt.length <= 12) {\n                            box.classList.add(\'step78-calendar-box\');\n                            box.style.setProperty(\'min-width\', \'64px\', \'important\');\n                            box.style.setProperty(\'width\', \'64px\', \'important\');\n                            box.style.setProperty(\'flex\', \'0 0 64px\', \'important\');\n                            box.style.setProperty(\'display\', \'flex\', \'important\');\n                            box.style.setProperty(\'align-items\', \'center\', \'important\');\n                            box.style.setProperty(\'justify-content\', \'center\', \'important\');\n                            box.style.setProperty(\'text-align\', \'center\', \'important\');\n                            box.style.setProperty(\'white-space\', \'nowrap\', \'important\');\n                            box.style.setProperty(\'word-break\', \'keep-all\', \'important\');\n                            box.style.setProperty(\'overflow-wrap\', \'normal\', \'important\');\n                            box.style.setProperty(\'writing-mode\', \'horizontal-tb\', \'important\');\n\n                            for (const svg of Array.from(box.querySelectorAll(\'svg\'))) {\n                                svg.style.setProperty(\'display\', \'none\', \'important\');\n                            }\n                        }\n                        if (box.getAttribute && box.getAttribute(\'data-testid\') === \'stHorizontalBlock\') break;\n                    }\n\n                    // 달력 오른쪽 밖으로 튀어나온 chevron만 추가 숨김\n                    const r = el.getBoundingClientRect();\n                    for (const svg of Array.from(doc.querySelectorAll(\'svg\'))) {\n                        const sr = svg.getBoundingClientRect();\n                        const sameLine = Math.abs((sr.top + sr.bottom) / 2 - (r.top + r.bottom) / 2) < 18;\n                        const nearRight = sr.left > r.left && sr.left < r.right + 34;\n                        if (sameLine && nearRight) {\n                            svg.style.setProperty(\'display\', \'none\', \'important\');\n                        }\n                    }\n                }\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                patchClock(doc);\n                fixCalendar(doc);\n            }\n\n            run();\n            setTimeout(run, 200);\n            setTimeout(run, 700);\n            setTimeout(run, 1400);\n            setTimeout(run, 2500);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_END]\n'

REMOVE_MARKERS = [
    ("# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_START]", "# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step78_top_clock_calendar_{STAMP}{APP.suffix}")
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


def remove_old_step78(text: str):
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
    print("Step78 top clock/calendar precise fix")
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
        print("Step77 실행 직후 정상 실행 화면 기준에서 다시 실행해주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    text, removed = remove_old_step78(text)
    text = text.rstrip() + "\n\n" + PATCH_BLOCK.strip("\n") + "\n"

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] 패치 후 mobile/app.py 문법 확인 실패")
        print(err)
        print("패치를 저장하지 않습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    APP.write_text(text, encoding="utf-8")
    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step78 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step78 블록 제거: {removed}")
    print("- 시간표/메모/학사일정 구조는 수정하지 않음")
    print("- 상단 현재시각 표시와 달력 정렬만 DOM 후처리")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 상단 상태표시가 'HH:MM 수업 전/방과 후' 형태로 보이는지")
    print("2. 달력 글자가 가운데 정렬되는지")
    print("3. 달력 오른쪽 아래화살표가 새로고침 버튼과 겹치지 않는지")
    print("4. 시간표 디자인과 학사일정 넘침 보정은 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

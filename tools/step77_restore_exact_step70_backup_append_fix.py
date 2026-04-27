# tools/step77_restore_exact_step70_backup_append_fix.py
# ------------------------------------------------------------
# Step77: 안정 백업 직접 복구 + 끝부분 DOM 보정
#
# 이번 방식:
# - 현재 깨진 app.py를 고치려 하지 않음
# - Step70 실행 직전 백업을 정확히 찾아 복구
#   app_before_step70_web_calendar_clock_memo_color_only_*.py
# - 이전 실패 패치 제거 작업도 하지 않음
# - 파일 맨 끝에만 DOM 보정 추가
#
# 수정:
# 1) 학사일정 칸 넘침 방지
# 2) 제목 오른쪽 현재시각 배지 표시
# 3) 달력 세로배치 및 화살표 위치 보정
# 4) 메모 literal span 색상 표시
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = '\n# [STEP77_WEB_DOM_FINAL_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(\'step77-web-final-style\')) return;\n                const style = doc.createElement(\'style\');\n                style.id = \'step77-web-final-style\';\n                style.textContent = `\n                    .step77-title-row {\n                        width: min(450px, 100%);\n                        display: flex;\n                        align-items: center;\n                        justify-content: space-between;\n                        gap: 8px;\n                        margin: 0 0 8px 0;\n                    }\n                    .step77-title-host {\n                        flex: 1 1 auto;\n                        min-width: 0;\n                    }\n                    .step77-title-host * {\n                        white-space: nowrap !important;\n                    }\n                    .step77-clock-pill {\n                        flex: 0 0 auto;\n                        display: inline-flex;\n                        align-items: center;\n                        gap: 5px;\n                        padding: 4px 9px;\n                        border-radius: 999px;\n                        border: 1px solid rgba(96, 165, 250, 0.34);\n                        background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));\n                        color: #1e40af;\n                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);\n                        white-space: nowrap;\n                        font-size: 12px;\n                        line-height: 1.1;\n                    }\n                    .step77-clock-time {\n                        font-size: 13px;\n                        font-weight: 800;\n                    }\n                    .step77-clock-state {\n                        opacity: 0.92;\n                    }\n\n                    /* 달력 selectbox 폭/텍스트 강제 */\n                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-baseweb="select"]),\n                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-testid="stSelectbox"]) {\n                        min-width: 76px !important;\n                        width: 76px !important;\n                        flex: 0 0 76px !important;\n                    }\n                    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],\n                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],\n                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div,\n                    div[data-testid="stHorizontalBlock"] div[role="button"] {\n                        min-width: 70px !important;\n                        width: 70px !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                    }\n                    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] *,\n                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] *,\n                    div[data-testid="stHorizontalBlock"] div[role="button"] *,\n                    div[data-testid="stHorizontalBlock"] button,\n                    div[data-testid="stHorizontalBlock"] button * {\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                    }\n\n                    /* 학사일정 칸 넘침 방지: 표 전체 디자인은 유지하고 내용만 안쪽에 가둠 */\n                    table.mobile-table th,\n                    table.mobile-table td {\n                        overflow: hidden !important;\n                    }\n                    table.mobile-table td *,\n                    table.mobile-table th * {\n                        max-width: 100% !important;\n                        box-sizing: border-box !important;\n                    }\n\n                    @media (max-width: 430px) {\n                        .step77-clock-state { display: none; }\n                        .step77-clock-pill { padding: 4px 8px; }\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function currentInfo() {\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n                const periods = [\n                    [\'1교시\', \'08:00\', \'08:50\'],\n                    [\'2교시\', \'09:00\', \'09:50\'],\n                    [\'3교시\', \'10:00\', \'10:50\'],\n                    [\'4교시\', \'11:00\', \'11:50\'],\n                    [\'점심\', \'11:50\', \'12:40\'],\n                    [\'5교시\', \'12:40\', \'13:30\'],\n                    [\'6교시\', \'13:40\', \'14:30\'],\n                    [\'7교시\', \'14:40\', \'15:30\'],\n                    [\'8교시\', \'16:00\', \'16:50\'],\n                    [\'9교시\', \'17:00\', \'17:50\']\n                ];\n\n                function toMin(t) {\n                    const p = t.split(\':\').map(Number);\n                    return p[0] * 60 + p[1];\n                }\n\n                let state = \'쉬는시간\';\n                for (const p of periods) {\n                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {\n                        state = p[0] + \' · \' + p[1] + \'~\' + p[2];\n                        break;\n                    }\n                }\n                if (mins < 8 * 60) state = \'수업 전\';\n                if (mins >= 17 * 60 + 50) state = \'방과 후\';\n\n                const hh = String(now.getHours()).padStart(2, \'0\');\n                const mm = String(now.getMinutes()).padStart(2, \'0\');\n                return { clock: hh + \':\' + mm, state };\n            }\n\n            function findTitle(doc) {\n                const nodes = Array.from(doc.querySelectorAll(\'h1,h2,h3,p,span,div\'));\n                return nodes.find(el => {\n                    if (!visible(el)) return false;\n                    if (el.closest(\'.step77-title-row\')) return false;\n                    const txt = (el.innerText || \'\').trim();\n                    return txt.includes(\'명덕외고 시간표 뷰어\');\n                }) || null;\n            }\n\n            function patchHeader(doc) {\n                const info = currentInfo();\n\n                let row = doc.querySelector(\'.step77-title-row\');\n                if (!row) {\n                    const title = findTitle(doc);\n                    if (!title || !title.parentNode) return;\n\n                    row = doc.createElement(\'div\');\n                    row.className = \'step77-title-row\';\n\n                    const host = doc.createElement(\'div\');\n                    host.className = \'step77-title-host\';\n\n                    title.parentNode.insertBefore(row, title);\n                    row.appendChild(host);\n                    host.appendChild(title);\n                }\n\n                let pill = row.querySelector(\'.step77-clock-pill\');\n                if (!pill) {\n                    pill = doc.createElement(\'div\');\n                    pill.className = \'step77-clock-pill\';\n                    pill.innerHTML = \'<span class="step77-clock-time"></span><span class="step77-clock-state"></span>\';\n                    row.appendChild(pill);\n                }\n\n                const timeEl = pill.querySelector(\'.step77-clock-time\');\n                const stateEl = pill.querySelector(\'.step77-clock-state\');\n                if (timeEl) timeEl.textContent = info.clock;\n                if (stateEl) stateEl.textContent = info.state;\n\n                for (const el of Array.from(doc.querySelectorAll(\'div,p,span\'))) {\n                    if (el.closest(\'.step77-title-row\')) continue;\n                    const txt = (el.innerText || \'\').trim();\n                    if ((txt === \'방과 후\' || txt === \'수업 전\' || txt === \'쉬는시간\') && visible(el)) {\n                        const r = el.getBoundingClientRect();\n                        if (r.top < 90) el.style.display = \'none\';\n                    }\n                }\n            }\n\n            function fixCalendar(doc) {\n                const nodes = Array.from(doc.querySelectorAll(\'button, [data-testid="stSelectbox"], [data-baseweb="select"], div[role="button"], span, div\'));\n                const targets = nodes.filter(el => {\n                    const txt = (el.innerText || el.textContent || \'\').trim();\n                    return /^달\\s*력$/.test(txt);\n                });\n\n                for (const el of targets) {\n                    if ((el.innerText || \'\').includes(\'\\n\')) {\n                        try { el.innerText = \'달력\'; } catch(e) {}\n                    }\n\n                    let cur = el;\n                    for (let i = 0; i < 10 && cur; i++, cur = cur.parentElement) {\n                        cur.style.setProperty(\'white-space\', \'nowrap\', \'important\');\n                        cur.style.setProperty(\'word-break\', \'keep-all\', \'important\');\n                        cur.style.setProperty(\'overflow-wrap\', \'normal\', \'important\');\n                        cur.style.setProperty(\'writing-mode\', \'horizontal-tb\', \'important\');\n\n                        const txt = (cur.innerText || \'\').trim();\n                        if (/달\\s*력/.test(txt) && txt.length <= 12) {\n                            cur.style.setProperty(\'min-width\', \'76px\', \'important\');\n                            cur.style.setProperty(\'width\', \'76px\', \'important\');\n                            cur.style.setProperty(\'flex\', \'0 0 76px\', \'important\');\n                        }\n                        if (cur.getAttribute && cur.getAttribute(\'data-testid\') === \'stHorizontalBlock\') break;\n                    }\n                }\n            }\n\n            function fixAcademicScheduleOverflow(doc) {\n                const table = Array.from(doc.querySelectorAll(\'table\')).find(t => {\n                    const txt = t.innerText || \'\';\n                    return txt.includes(\'교시\') && txt.includes(\'학사일정\');\n                });\n                if (!table) return;\n\n                const rows = Array.from(table.querySelectorAll(\'tr\'));\n                const target = rows.find(r => (r.innerText || \'\').includes(\'학사일정\'));\n                if (!target) return;\n\n                for (const cell of Array.from(target.children)) {\n                    cell.style.setProperty(\'overflow\', \'hidden\', \'important\');\n                    cell.style.setProperty(\'word-break\', \'keep-all\', \'important\');\n                    cell.style.setProperty(\'overflow-wrap\', \'anywhere\', \'important\');\n                    cell.style.setProperty(\'line-height\', \'1.18\', \'important\');\n\n                    const txt = (cell.innerText || \'\').trim();\n                    if (txt && !txt.includes(\'학사일정\')) {\n                        cell.style.setProperty(\'font-size\', \'10px\', \'important\');\n                    }\n\n                    for (const child of Array.from(cell.querySelectorAll(\'*\'))) {\n                        child.style.setProperty(\'max-width\', \'100%\', \'important\');\n                        child.style.setProperty(\'white-space\', \'normal\', \'important\');\n                        child.style.setProperty(\'word-break\', \'keep-all\', \'important\');\n                        child.style.setProperty(\'overflow-wrap\', \'anywhere\', \'important\');\n                    }\n                }\n            }\n\n            function parseMemoSpanText(doc) {\n                const allowed = /<span\\s+style=["\']\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*["\']>(.*?)<\\/span>/gis;\n                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);\n                const targets = [];\n                let node;\n\n                while ((node = walker.nextNode())) {\n                    const value = node.nodeValue || \'\';\n                    allowed.lastIndex = 0;\n                    if (value.includes(\'<span\') && allowed.test(value)) targets.push(node);\n                }\n\n                for (const textNode of targets) {\n                    const text = textNode.nodeValue || \'\';\n                    const frag = doc.createDocumentFragment();\n                    let last = 0;\n                    allowed.lastIndex = 0;\n                    let m;\n\n                    while ((m = allowed.exec(text))) {\n                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));\n\n                        const span = doc.createElement(\'span\');\n                        span.style.setProperty(m[1].toLowerCase(), m[2]);\n                        span.textContent = m[3];\n                        frag.appendChild(span);\n\n                        last = allowed.lastIndex;\n                    }\n\n                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));\n                    textNode.parentNode.replaceChild(frag, textNode);\n                }\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                patchHeader(doc);\n                fixCalendar(doc);\n                fixAcademicScheduleOverflow(doc);\n                parseMemoSpanText(doc);\n            }\n\n            run();\n            setTimeout(run, 200);\n            setTimeout(run, 700);\n            setTimeout(run, 1400);\n            setTimeout(run, 2500);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP77_WEB_DOM_FINAL_END]\n'


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step77_restore_exact_{STAMP}{APP.suffix}")
    b.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[현재 백업] {b}")


def compiles(text: str, name: str):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def find_exact_stable_backup():
    patterns = [
        # 가장 우선: 사용자가 '시간표 디자인 만족, 세 문제만 남음'이라고 한 Step70 직전 상태
        "app_before_step70_web_calendar_clock_memo_color_only_*.py",
        # 차선: Step69 실행 직전/직후 주변 백업
        "app_before_step69_web_source_header_memo_table_fix_*.py",
        "app_before_step68_web_clock_memo_table_cleanup_*.py",
        "app_before_step67_web_title_clock_done_table_refine_*.py",
        "app_before_step66_web_clean_repair_*.py",
    ]

    checked = []
    for pat in patterns:
        candidates = sorted(APP.parent.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        for b in candidates:
            if b in checked:
                continue
            checked.append(b)
            text = b.read_text(encoding="utf-8", errors="replace")
            ok, err = compiles(text, str(b))
            print(f"[검토] {b.name} -> {'OK' if ok else 'FAIL'}")
            if ok:
                return b, text

    raise RuntimeError("Step70 직전 안정 백업을 찾지 못했습니다.")


def strip_old_step77_if_any(text: str):
    start = "# [STEP77_WEB_DOM_FINAL_START]"
    end = "# [STEP77_WEB_DOM_FINAL_END]"
    removed = 0
    while start in text and end in text:
        s = text.find(start)
        e = text.find(end, s)
        eol = text.find("\n", e)
        eol = len(text) if eol == -1 else eol + 1
        text = text[:s] + text[eol:]
        removed += 1
    return text, removed


def patch_calendar_literal(text: str):
    changed = 0
    replacements = [
        ('"달\\n력"', '"달력"'),
        ("'달\\n력'", "'달력'"),
        ('"달\n력"', '"달력"'),
        ("'달\n력'", "'달력'"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    return text, changed


def main():
    print("====================================================")
    print("Step77 restore exact Step70 backup + append DOM fix")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    try:
        selected, text = find_exact_stable_backup()
        print(f"[복구 기준] {selected}")

        text, removed_step77 = strip_old_step77_if_any(text)
        text, literal_changes = patch_calendar_literal(text)

        text = text.rstrip() + "\n\n" + PATCH_BLOCK.strip("\n") + "\n"

        ok, err = compiles(text, str(APP))
        if not ok:
            raise RuntimeError(f"패치 후 문법 오류: {err}")

        APP.write_text(text, encoding="utf-8")
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step77 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 복구 기준 백업: {selected}")
    print(f"- 기존 Step77 블록 제거: {removed_step77}")
    print(f"- 달력 문자열 보정: {literal_changes}")
    print("- DOM 보정 삽입 위치: 파일 맨 끝")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 문법 오류 없이 실행되는지")
    print("2. 학사일정 칸 내용이 칸 밖으로 튀어나가지 않는지")
    print("3. 제목 오른쪽에 현재시각이 보이는지")
    print("4. 달력 글자/화살표가 정상 배치되는지")
    print("5. 글자색 span 메모가 실제 색상으로 보이는지")
    print("6. 시간표 디자인은 기존 만족 상태로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

# tools/step76_restore_step69_then_dom_fix.py
# ------------------------------------------------------------
# Step76: Step70~75 실패 복구 + 안정판에서 DOM 보정
#
# 핵심:
# - 현재 깨진 app.py를 계속 수정하지 않음
# - 가장 안정적이었던 Step69 직후 백업을 우선 복구
# - Step69 백업이 없으면 Step70 직전 백업 사용
# - 그 뒤 파일 맨 끝에 DOM 보정만 추가
#
# 수정:
# 1) 달력 글자 세로배치 방지
# 2) 제목 오른쪽 현재시각 배지 표시
# 3) literal <span style="color:#...">...</span> 실제 색상 표시
# 4) 시간표 디자인 유지
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

REMOVE_MARKERS = [
    ("# [STEP70_WEB_HEADER_MEMO_CALENDAR_START]", "# [STEP70_WEB_HEADER_MEMO_CALENDAR_END]"),
    ("# [STEP70_WEB_CALL_START]", "# [STEP70_WEB_CALL_END]"),
    ("# [STEP71_WEB_MINIMAL_FIX_START]", "# [STEP71_WEB_MINIMAL_FIX_END]"),
    ("# [STEP71_WEB_CALL_START]", "# [STEP71_WEB_CALL_END]"),
    ("# [STEP71_WEB_POSTPROCESS_START]", "# [STEP71_WEB_POSTPROCESS_END]"),
    ("# [STEP72_WEB_MINIMAL_REPAIR_START]", "# [STEP72_WEB_MINIMAL_REPAIR_END]"),
    ("# [STEP72_WEB_CALL_START]", "# [STEP72_WEB_CALL_END]"),
    ("# [STEP72_WEB_POSTPROCESS_START]", "# [STEP72_WEB_POSTPROCESS_END]"),
    ("# [STEP73_WEB_MINIMAL_STABLE_START]", "# [STEP73_WEB_MINIMAL_STABLE_END]"),
    ("# [STEP73_WEB_CALL_START]", "# [STEP73_WEB_CALL_END]"),
    ("# [STEP73_WEB_POSTPROCESS_START]", "# [STEP73_WEB_POSTPROCESS_END]"),
    ("# [STEP74_WEB_DOM_FIX_START]", "# [STEP74_WEB_DOM_FIX_END]"),
    ("# [STEP75_WEB_FINAL_DOM_ONLY_START]", "# [STEP75_WEB_FINAL_DOM_ONLY_END]"),
    ("# [STEP76_WEB_DOM_ONLY_FINAL_START]", "# [STEP76_WEB_DOM_ONLY_FINAL_END]"),
]

BAD_CALLS = {
    "step70_inject_css()",
    "step70_render_header()",
    "step70_postprocess_component()",
    "step71_inject_css()",
    "step71_render_header()",
    "step71_postprocess_component()",
    "step72_inject_css()",
    "step72_render_header()",
    "step72_postprocess_component()",
    "step73_inject_css()",
    "step73_render_header()",
    "step73_postprocess_component()",
}

PATCH_BLOCK = '\n# [STEP76_WEB_DOM_ONLY_FINAL_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(\'step76-web-dom-style\')) return;\n                const style = doc.createElement(\'style\');\n                style.id = \'step76-web-dom-style\';\n                style.textContent = `\n                    .step76-title-row {\n                        width: min(450px, 100%);\n                        display: flex;\n                        align-items: center;\n                        justify-content: space-between;\n                        gap: 8px;\n                        margin: 0 0 8px 0;\n                    }\n                    .step76-title-host {\n                        flex: 1 1 auto;\n                        min-width: 0;\n                    }\n                    .step76-title-host * {\n                        white-space: nowrap !important;\n                    }\n                    .step76-clock-pill {\n                        flex: 0 0 auto;\n                        display: inline-flex;\n                        align-items: center;\n                        gap: 5px;\n                        padding: 4px 9px;\n                        border-radius: 999px;\n                        border: 1px solid rgba(96, 165, 250, 0.34);\n                        background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));\n                        color: #1e40af;\n                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);\n                        white-space: nowrap;\n                        font-size: 12px;\n                        line-height: 1.1;\n                    }\n                    .step76-clock-time {\n                        font-size: 13px;\n                        font-weight: 800;\n                    }\n                    .step76-clock-state {\n                        opacity: 0.92;\n                    }\n\n                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-baseweb="select"]),\n                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-testid="stSelectbox"]) {\n                        min-width: 82px !important;\n                        width: 82px !important;\n                        flex: 0 0 82px !important;\n                    }\n                    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],\n                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],\n                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div,\n                    div[data-testid="stHorizontalBlock"] div[role="button"] {\n                        min-width: 76px !important;\n                        width: 76px !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                    }\n                    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] *,\n                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] *,\n                    div[data-testid="stHorizontalBlock"] div[role="button"] *,\n                    div[data-testid="stHorizontalBlock"] button,\n                    div[data-testid="stHorizontalBlock"] button * {\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                    }\n\n                    @media (max-width: 430px) {\n                        .step76-clock-state { display: none; }\n                        .step76-clock-pill { padding: 4px 8px; }\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function currentInfo() {\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n                const periods = [\n                    [\'1교시\', \'08:00\', \'08:50\'],\n                    [\'2교시\', \'09:00\', \'09:50\'],\n                    [\'3교시\', \'10:00\', \'10:50\'],\n                    [\'4교시\', \'11:00\', \'11:50\'],\n                    [\'점심\', \'11:50\', \'12:40\'],\n                    [\'5교시\', \'12:40\', \'13:30\'],\n                    [\'6교시\', \'13:40\', \'14:30\'],\n                    [\'7교시\', \'14:40\', \'15:30\'],\n                    [\'8교시\', \'16:00\', \'16:50\'],\n                    [\'9교시\', \'17:00\', \'17:50\']\n                ];\n\n                function toMin(t) {\n                    const p = t.split(\':\').map(Number);\n                    return p[0] * 60 + p[1];\n                }\n\n                let state = \'쉬는시간\';\n                for (const p of periods) {\n                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {\n                        state = p[0] + \' · \' + p[1] + \'~\' + p[2];\n                        break;\n                    }\n                }\n                if (mins < 8 * 60) state = \'수업 전\';\n                if (mins >= 17 * 60 + 50) state = \'방과 후\';\n\n                const hh = String(now.getHours()).padStart(2, \'0\');\n                const mm = String(now.getMinutes()).padStart(2, \'0\');\n                return { clock: hh + \':\' + mm, state };\n            }\n\n            function findTitle(doc) {\n                const nodes = Array.from(doc.querySelectorAll(\'h1,h2,h3,p,span,div\'));\n                return nodes.find(el => {\n                    if (!visible(el)) return false;\n                    if (el.closest(\'.step76-title-row\')) return false;\n                    const txt = (el.innerText || \'\').trim();\n                    return txt.includes(\'명덕외고 시간표 뷰어\');\n                }) || null;\n            }\n\n            function patchHeader(doc) {\n                const info = currentInfo();\n\n                let row = doc.querySelector(\'.step76-title-row\');\n                if (!row) {\n                    const title = findTitle(doc);\n                    if (!title || !title.parentNode) return;\n\n                    row = doc.createElement(\'div\');\n                    row.className = \'step76-title-row\';\n\n                    const host = doc.createElement(\'div\');\n                    host.className = \'step76-title-host\';\n\n                    title.parentNode.insertBefore(row, title);\n                    row.appendChild(host);\n                    host.appendChild(title);\n                }\n\n                let pill = row.querySelector(\'.step76-clock-pill\');\n                if (!pill) {\n                    pill = doc.createElement(\'div\');\n                    pill.className = \'step76-clock-pill\';\n                    pill.innerHTML = \'<span class="step76-clock-time"></span><span class="step76-clock-state"></span>\';\n                    row.appendChild(pill);\n                }\n\n                const timeEl = pill.querySelector(\'.step76-clock-time\');\n                const stateEl = pill.querySelector(\'.step76-clock-state\');\n                if (timeEl) timeEl.textContent = info.clock;\n                if (stateEl) stateEl.textContent = info.state;\n\n                for (const el of Array.from(doc.querySelectorAll(\'div,p,span\'))) {\n                    if (el.closest(\'.step76-title-row\')) continue;\n                    const txt = (el.innerText || \'\').trim();\n                    if ((txt === \'방과 후\' || txt === \'수업 전\' || txt === \'쉬는시간\') && visible(el)) {\n                        const r = el.getBoundingClientRect();\n                        if (r.top < 90) el.style.display = \'none\';\n                    }\n                }\n            }\n\n            function fixCalendar(doc) {\n                const nodes = Array.from(doc.querySelectorAll(\'button, [data-testid="stSelectbox"], [data-baseweb="select"], div[role="button"], span, div\'));\n                const targets = nodes.filter(el => {\n                    const txt = (el.innerText || el.textContent || \'\').trim();\n                    return /^달\\s*력$/.test(txt);\n                });\n\n                for (const el of targets) {\n                    if ((el.innerText || \'\').includes(\'\\n\')) {\n                        try { el.innerText = \'달력\'; } catch(e) {}\n                    }\n\n                    let cur = el;\n                    for (let i = 0; i < 10 && cur; i++, cur = cur.parentElement) {\n                        cur.style.setProperty(\'white-space\', \'nowrap\', \'important\');\n                        cur.style.setProperty(\'word-break\', \'keep-all\', \'important\');\n                        cur.style.setProperty(\'overflow-wrap\', \'normal\', \'important\');\n                        cur.style.setProperty(\'writing-mode\', \'horizontal-tb\', \'important\');\n\n                        const txt = (cur.innerText || \'\').trim();\n                        if (/달\\s*력/.test(txt) && txt.length <= 12) {\n                            cur.style.setProperty(\'min-width\', \'82px\', \'important\');\n                            cur.style.setProperty(\'width\', \'82px\', \'important\');\n                            cur.style.setProperty(\'flex\', \'0 0 82px\', \'important\');\n                        }\n                        if (cur.getAttribute && cur.getAttribute(\'data-testid\') === \'stHorizontalBlock\') break;\n                    }\n                }\n            }\n\n            function parseMemoSpanText(doc) {\n                const allowed = /<span\\s+style=["\']\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*["\']>(.*?)<\\/span>/gis;\n                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);\n                const targets = [];\n                let node;\n\n                while ((node = walker.nextNode())) {\n                    const value = node.nodeValue || \'\';\n                    allowed.lastIndex = 0;\n                    if (value.includes(\'<span\') && allowed.test(value)) targets.push(node);\n                }\n\n                for (const textNode of targets) {\n                    const text = textNode.nodeValue || \'\';\n                    const frag = doc.createDocumentFragment();\n                    let last = 0;\n                    allowed.lastIndex = 0;\n                    let m;\n\n                    while ((m = allowed.exec(text))) {\n                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));\n\n                        const span = doc.createElement(\'span\');\n                        span.style.setProperty(m[1].toLowerCase(), m[2]);\n                        span.textContent = m[3];\n                        frag.appendChild(span);\n\n                        last = allowed.lastIndex;\n                    }\n\n                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));\n                    textNode.parentNode.replaceChild(frag, textNode);\n                }\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                patchHeader(doc);\n                fixCalendar(doc);\n                parseMemoSpanText(doc);\n            }\n\n            run();\n            setTimeout(run, 200);\n            setTimeout(run, 700);\n            setTimeout(run, 1400);\n            setTimeout(run, 2500);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP76_WEB_DOM_ONLY_FINAL_END]\n'


def backup(path: Path):
    b = path.with_name(f"{path.stem}_before_step76_restore_step69_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def compiles(text: str, name: str):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def pick_stable_backup():
    # Step70 실행 직전 백업이 가장 중요: 사용자가 만족했던 Step69 상태일 가능성이 큼
    preferred_patterns = [
        "app_before_step70*.py",
        "app_before_step69*.py",
        "app_before_step68*.py",
        "app_before_step67*.py",
        "app_before_step66*.py",
        "app_before_step65*.py",
        "app_before_step64*.py",
        "app_before_step63*.py",
        "app_before_step62*.py",
        "app_before_step57*.py",
        "app_before_step56*.py",
        "app_before_step55*.py",
    ]

    checked = []
    for pat in preferred_patterns:
        candidates = sorted(APP.parent.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        for b in candidates:
            if b in checked:
                continue
            checked.append(b)
            text = b.read_text(encoding="utf-8", errors="replace")
            ok, err = compiles(text, str(b))
            if ok:
                return text, b

    # fallback: 전체 백업 중 컴파일 가능한 최신 파일
    candidates = sorted(
        set(APP.parent.glob("app_before_step*.py")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for b in candidates:
        text = b.read_text(encoding="utf-8", errors="replace")
        ok, err = compiles(text, str(b))
        if ok:
            return text, b

    raise RuntimeError("컴파일 가능한 백업을 찾지 못했습니다.")


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


def remove_old_patches(text: str):
    removed = 0
    for start, end in REMOVE_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1

    lines = []
    removed_calls = 0
    for line in text.splitlines():
        if line.strip() in BAD_CALLS:
            removed_calls += 1
            continue
        lines.append(line)

    return "\n".join(lines) + "\n", removed, removed_calls


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
    print("Step76 restore Step69 then DOM fix")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup(APP)

    try:
        text, restored_from = pick_stable_backup()
        print(f"[복구 기준] {restored_from}")

        text, removed_blocks, removed_calls = remove_old_patches(text)
        text, literal_changes = patch_calendar_literal(text)

        text = text.rstrip() + "\n\n" + PATCH_BLOCK.strip("\n") + "\n"
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] mobile/app.py 문법 확인 실패")
        print(err)
        print("패치를 저장하지 않습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    APP.write_text(text, encoding="utf-8")
    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step76 패치 저장")

    print()
    print("[변경 요약]")
    print(f"- 복구 기준 백업: {restored_from}")
    print(f"- Step70~76 이전 블록 제거: {removed_blocks}")
    print(f"- 단독 호출 제거: {removed_calls}")
    print(f"- 달력 문자열 보정: {literal_changes}")
    print("- DOM 패치 삽입 위치: 파일 맨 끝")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 문법 오류 없이 실행되는지")
    print("2. 달력 글자가 가로로 보이는지")
    print("3. 제목 오른쪽에 현재시각이 보이는지")
    print("4. 글자색 span 메모가 실제 색상으로 보이는지")
    print("5. 시간표 디자인은 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

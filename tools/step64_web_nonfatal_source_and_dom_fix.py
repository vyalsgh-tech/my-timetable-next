# tools/step64_web_nonfatal_source_and_dom_fix.py
# ------------------------------------------------------------
# Step64: Step63 실패 보완판
# - 시간표 시작 html_parts.append를 못 찾아도 실패하지 않음
# - 현재시각은 Python으로 직접 표시
# - 시간표 프레임/메모그룹은 HTML 출력 후 component JS로 후처리
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

BLOCK_MARKERS = [
    ("# [WEB_VIEWER_PC_LIKE_UI_START]", "# [WEB_VIEWER_PC_LIKE_UI_END]"),
    ("# [WEB_VIEWER_PC_LIKE_UI_CALL_START]", "# [WEB_VIEWER_PC_LIKE_UI_CALL_END]"),
    ("# [WEB_VERSION_MANAGEMENT_START]", "# [WEB_VERSION_MANAGEMENT_END]"),
    ("# [WEB_VERSION_BADGE_CALL_START]", "# [WEB_VERSION_BADGE_CALL_END]"),
    ("# [STEP62_HELPERS_START]", "# [STEP62_HELPERS_END]"),
    ("# [STEP62_CLOCK_CALL_START]", "# [STEP62_CLOCK_CALL_END]"),
    ("# [STEP63_HELPERS_START]", "# [STEP63_HELPERS_END]"),
    ("# [STEP63_CLOCK_CALL_START]", "# [STEP63_CLOCK_CALL_END]"),
    ("# [STEP64_WEB_FINAL_HELPERS_START]", "# [STEP64_WEB_FINAL_HELPERS_END]"),
    ("# [STEP64_WEB_FINAL_CALL_START]", "# [STEP64_WEB_FINAL_CALL_END]"),
    ("# [STEP64_WEB_POSTPROCESS_CALL_START]", "# [STEP64_WEB_POSTPROCESS_CALL_END]"),
]

HELPERS = '\n# [STEP64_WEB_FINAL_HELPERS_START]\ndef step64_current_period_info():\n    try:\n        now = datetime.now(kst_tz)\n        now_mins = now.hour * 60 + now.minute\n\n        for p_name, t_range in period_times:\n            if p_name == "학사일정":\n                continue\n            try:\n                start_str, end_str = t_range.split("\\n")\n                h1, m1 = map(int, start_str.split(":"))\n                h2, m2 = map(int, end_str.split(":"))\n            except Exception:\n                continue\n\n            s_mins = h1 * 60 + m1\n            e_mins = h2 * 60 + m2\n            if s_mins <= now_mins < e_mins:\n                return {\n                    "clock": now.strftime("%H:%M"),\n                    "period": p_name,\n                    "range": f"{start_str}~{end_str}",\n                    "key": str(p_name).replace("교시", "").strip() if "교시" in str(p_name) else ("lunch" if "점심" in str(p_name) else ""),\n                }\n\n        if now_mins < 8 * 60:\n            label = "수업 전"\n        elif now_mins >= 17 * 60 + 50:\n            label = "방과 후"\n        else:\n            label = "쉬는시간"\n\n        return {"clock": now.strftime("%H:%M"), "period": label, "range": "", "key": ""}\n    except Exception:\n        return {"clock": "--:--", "period": "", "range": "", "key": ""}\n\n\ndef step64_inject_css():\n    try:\n        st.markdown(\n            """\n            <style>\n            /* [STEP64_WEB_FINAL_CSS_START] */\n            .mobile-now-row {\n                width: 100%;\n                max-width: 450px;\n                display: flex;\n                justify-content: flex-end;\n                align-items: center;\n                margin: -2px auto 6px 0;\n                min-height: 26px;\n            }\n            .mobile-now-badge {\n                display: inline-flex;\n                align-items: center;\n                gap: 6px;\n                padding: 4px 10px;\n                border-radius: 999px;\n                border: 1px solid rgba(37, 99, 235, 0.24);\n                background: linear-gradient(180deg, rgba(239, 246, 255, 0.98), rgba(219, 234, 254, 0.92));\n                color: #1e3a8a;\n                font-size: 12px;\n                line-height: 1.1;\n                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.10);\n                white-space: nowrap;\n            }\n            .mobile-now-badge b {\n                font-size: 13px;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button p,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n                margin: 0 !important;\n            }\n            .timetable-frame {\n                width: 100%;\n                max-width: 450px;\n                margin: 0 auto 12px 0;\n                background: linear-gradient(180deg, #eef5ff 0%, #dce9f8 100%);\n                border-radius: 8px;\n                padding: 5px 5px 14px 5px;\n                box-shadow:\n                    0 12px 24px rgba(15, 23, 42, 0.16),\n                    inset 0 1px 0 rgba(255,255,255,0.92),\n                    inset 0 -1px 0 rgba(100,116,139,0.22);\n                position: relative;\n                overflow: hidden;\n            }\n            .timetable-scroll {\n                width: 100%;\n                overflow-x: auto;\n                border-radius: 6px;\n                background: transparent;\n                position: relative;\n                z-index: 1;\n            }\n            .timetable-bottom-shadow {\n                position: absolute;\n                left: 8px;\n                right: 8px;\n                bottom: 5px;\n                height: 7px;\n                border-radius: 999px;\n                background: linear-gradient(180deg, rgba(30,41,59,0.34), rgba(100,116,139,0.15));\n                box-shadow: 0 5px 9px rgba(15,23,42,0.18);\n                pointer-events: none;\n            }\n            .mobile-table {\n                border-collapse: collapse !important;\n                border-spacing: 0 !important;\n                border: 0 !important;\n                box-shadow:\n                    0 4px 10px rgba(15,23,42,0.10),\n                    0 0 0 1px rgba(30,41,59,0.88);\n                border-radius: 5px;\n                overflow: hidden;\n            }\n            .mobile-table th,\n            .mobile-table td {\n                box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);\n            }\n            .mobile-table td {\n                background-image: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(247,250,253,0.90));\n            }\n            .mobile-table th {\n                background-image: linear-gradient(180deg, rgba(229,241,255,0.98), rgba(201,223,247,0.94));\n            }\n            .memo-section-header {\n                padding: 5px 6px;\n                margin: 6px 0 0 0;\n                font-size: 13px;\n                font-weight: 800;\n                line-height: 1.2;\n                cursor: pointer;\n                user-select: none;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                list-style: none;\n            }\n            .memo-section-header::-webkit-details-marker {\n                display: none;\n            }\n            .memo-section-header.important { color: #ef4444; }\n            .memo-section-header.general { color: #0f172a; }\n            .memo-section-header.done { color: #94a3b8; }\n            .memo-group-content {\n                border-bottom: 1px solid rgba(191, 219, 254, 0.70);\n            }\n            .memo-row {\n                padding: 7px 6px;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                color: inherit;\n            }\n            .memo-row:last-child { border-bottom: 0; }\n            .memo-text {\n                font-size: 14px;\n                font-weight: 700;\n                line-height: 1.35;\n                word-break: keep-all;\n                overflow-wrap: anywhere;\n                white-space: pre-line;\n            }\n            .memo-time {\n                font-size: 11px;\n                opacity: 0.65;\n                margin-top: 4px;\n            }\n            .memo-done .memo-text {\n                text-decoration: line-through;\n                text-decoration-thickness: 1.3px;\n                color: #94a3b8;\n            }\n            /* [STEP64_WEB_FINAL_CSS_END] */\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef step64_render_now_badge():\n    try:\n        info = step64_current_period_info()\n        clock = info.get("clock", "--:--")\n        period = info.get("period", "")\n        range_text = info.get("range", "")\n        detail = period\n        if range_text:\n            detail += f" · {range_text}"\n\n        st.markdown(\n            f"""\n            <div class=\'mobile-now-row\'>\n                <span class=\'mobile-now-badge\'>\n                    <b>{clock}</b>\n                    <span>{detail}</span>\n                </span>\n            </div>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef step64_postprocess_component():\n    try:\n        import streamlit.components.v1 as components\n        info = step64_current_period_info()\n        current_key = str(info.get("key", "") or "")\n        components.html(\n            f"""\n            <script>\n            (function() {{\n                const currentKey = "{current_key}";\n                function docRoot() {{\n                    try {{ return window.parent.document; }} catch(e) {{ return document; }}\n                }}\n                function visible(el) {{\n                    if (!el) return false;\n                    const r = el.getBoundingClientRect();\n                    return r.width > 2 && r.height > 2;\n                }}\n                function patchButtons(doc) {{\n                    for (const b of Array.from(doc.querySelectorAll(\'button\'))) {{\n                        const compact = (b.innerText || \'\').trim().replace(/\\\\s+/g, \'\');\n                        if ([\'☀️\',\'☀\',\'🌞\',\'🔆\'].includes(compact)) b.innerText = \'조회\';\n                        if ([\'🌙\',\'🌛\',\'🌜\',\'🌕\'].includes(compact)) b.innerText = \'8·9\';\n                        if ((b.innerText || \'\').replace(/\\\\s+/g, \'\') === \'달력\') b.innerText = \'달력\';\n                        b.style.whiteSpace = \'nowrap\';\n                        b.style.wordBreak = \'keep-all\';\n                        b.style.writingMode = \'horizontal-tb\';\n                    }}\n                }}\n                function wrapTable(doc) {{\n                    const tables = Array.from(doc.querySelectorAll(\'table\'));\n                    const table = tables.find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\')) || doc.querySelector(\'table.mobile-table\');\n                    if (!table || table.closest(\'.timetable-frame\')) return;\n                    table.classList.add(\'mobile-table\');\n                    const parent = table.parentNode;\n                    if (!parent) return;\n                    const frame = doc.createElement(\'div\');\n                    frame.className = \'timetable-frame\';\n                    const scroll = doc.createElement(\'div\');\n                    scroll.className = \'timetable-scroll\';\n                    const shadow = doc.createElement(\'div\');\n                    shadow.className = \'timetable-bottom-shadow\';\n                    parent.insertBefore(frame, table);\n                    scroll.appendChild(table);\n                    frame.appendChild(scroll);\n                    frame.appendChild(shadow);\n                }}\n                function markCurrent(doc) {{\n                    if (!currentKey) return;\n                    const table = Array.from(doc.querySelectorAll(\'table\')).find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\'));\n                    if (!table) return;\n                    for (const row of Array.from(table.querySelectorAll(\'tr\'))) {{\n                        const txt = row.innerText || \'\';\n                        let hit = false;\n                        if (currentKey === \'lunch\') hit = txt.includes(\'점심\');\n                        else hit = txt.includes(currentKey + \'교시\') || txt.includes(currentKey + \' 교시\');\n                        if (hit) {{\n                            row.style.background = \'#eaf2ff\';\n                            if (row.children.length) {{\n                                row.children[0].style.background = \'#2563eb\';\n                                row.children[0].style.color = \'#fff\';\n                                row.children[0].style.fontWeight = \'800\';\n                            }}\n                        }}\n                    }}\n                }}\n                function stripOne(el) {{\n                    const re = /^\\\\s*\\\\d+\\\\.\\\\s*/;\n                    for (const n of el.childNodes || []) {{\n                        if (n.nodeType === 3 && re.test(n.textContent || \'\')) n.textContent = (n.textContent || \'\').replace(re, \'\');\n                    }}\n                }}\n                function memoClass(text, el) {{\n                    const t = text || \'\';\n                    let strike = false;\n                    try {{\n                        let cur = el;\n                        for (let i=0; i<4 && cur; i++, cur=cur.parentElement) {{\n                            const s = window.getComputedStyle(cur);\n                            if ((s.textDecorationLine || \'\').includes(\'line-through\')) strike = true;\n                        }}\n                    }} catch(e) {{}}\n                    if (strike || /^\\\\s*(✔|✅)/.test(t)) return \'done\';\n                    if (/⭐|★/.test(t)) return \'important\';\n                    return \'general\';\n                }}\n                function findMemoContainer(doc) {{\n                    const title = Array.from(doc.querySelectorAll(\'div,h1,h2,h3,p,span\')).find(el => visible(el) && (el.innerText || \'\').includes(\'메모장\'));\n                    if (!title) return null;\n                    const top = title.getBoundingClientRect().top;\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    const cands = Array.from(doc.querySelectorAll(\'div\')).filter(el => {{\n                        if (!visible(el)) return false;\n                        const r = el.getBoundingClientRect();\n                        const txt = el.innerText || \'\';\n                        return r.top > top && r.height > 100 && dateRe.test(txt) && !(txt.includes(\'교시\') && txt.includes(\'학사일정\'));\n                    }});\n                    cands.sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height);\n                    return cands[0] || null;\n                }}\n                function rowWrap(el) {{\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    let cur = el;\n                    for (let i=0; i<5 && cur && cur.parentElement; i++, cur=cur.parentElement) {{\n                        const r = cur.getBoundingClientRect();\n                        const txt = cur.innerText || \'\';\n                        if (r.height >= 28 && r.height <= 150 && dateRe.test(txt)) return cur;\n                    }}\n                    return el;\n                }}\n                function groupMemos(doc) {{\n                    const container = findMemoContainer(doc);\n                    if (!container || container.querySelector(\'.memo-section-header\')) return;\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    const prelim = [];\n                    for (const el of Array.from(container.querySelectorAll(\'div,p,span\'))) {{\n                        if (!visible(el)) continue;\n                        const txt = (el.innerText || \'\').trim();\n                        if (dateRe.test(txt) && !txt.includes(\'메모장\')) prelim.push(rowWrap(el));\n                    }}\n                    const rows = [];\n                    for (const r of prelim) if (!rows.includes(r)) rows.push(r);\n                    const finalRows = rows.filter(r => !rows.some(o => o !== r && r.contains(o)));\n                    if (finalRows.length < 2) return;\n                    for (const r of finalRows) {{\n                        r.classList.add(\'memo-row\');\n                        stripOne(r);\n                    }}\n                    const groups = {{\n                        important: finalRows.filter(r => memoClass(r.innerText, r) === \'important\'),\n                        general: finalRows.filter(r => memoClass(r.innerText, r) === \'general\'),\n                        done: finalRows.filter(r => memoClass(r.innerText, r) === \'done\')\n                    }};\n                    const labels = [\n                        [\'important\',\'📌 중요 메모\',\'important\'],\n                        [\'general\',\'▣ 일반 메모\',\'general\'],\n                        [\'done\',\'✔ 완료 메모\',\'done\']\n                    ];\n                    const parent = finalRows[0].parentNode;\n                    if (!parent) return;\n                    const frag = doc.createDocumentFragment();\n                    for (const [key,label,cls] of labels) {{\n                        const arr = groups[key] || [];\n                        if (!arr.length) continue;\n                        const details = doc.createElement(\'details\');\n                        details.open = true;\n                        const summary = doc.createElement(\'summary\');\n                        summary.className = \'memo-section-header \' + cls;\n                        summary.textContent = label + \' (\' + arr.length + \')\';\n                        const body = doc.createElement(\'div\');\n                        body.className = \'memo-group-content\';\n                        for (const row of arr) body.appendChild(row);\n                        details.appendChild(summary);\n                        details.appendChild(body);\n                        frag.appendChild(details);\n                    }}\n                    parent.insertBefore(frag, finalRows[0] || null);\n                }}\n                function run() {{\n                    const doc = docRoot();\n                    patchButtons(doc);\n                    wrapTable(doc);\n                    markCurrent(doc);\n                    groupMemos(doc);\n                }}\n                run();\n                setTimeout(run, 200);\n                setTimeout(run, 700);\n                setTimeout(run, 1500);\n            }})();\n            </script>\n            """,\n            height=1,\n            width=1,\n        )\n    except Exception:\n        pass\n# [STEP64_WEB_FINAL_HELPERS_END]\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step64_web_nonfatal_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


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
    for start, end in BLOCK_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    return text, removed


def ensure_helpers(text: str):
    # import html 추가는 선택사항. 없으면 건너뛰어도 component 방식은 동작함.
    if not re.search(r"^\s*import\s+html\b", text, re.M):
        for anchor in ["import re\n", "import io\n", "import os\n", "import json\n"]:
            if anchor in text:
                text = text.replace(anchor, anchor + "import html\n", 1)
                break

    marker = "def normalize_text(value):"
    pos = text.find(marker)
    if pos != -1:
        next_section = text.find("\n# =========================================================", pos + len(marker))
        if next_section != -1:
            return text[:next_section] + "\n\n" + HELPERS + text[next_section:], "after_normalize_text"

    idx = text.find("st.set_page_config")
    if idx == -1:
        idx = 0
    return text[:idx] + HELPERS + "\n\n" + text[idx:], "before_set_page_config"


def find_call_after_page_config(lines):
    for i, line in enumerate(lines):
        if "st.set_page_config" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1
    return 0


def insert_css_and_clock_call(text: str):
    lines = text.splitlines()
    idx = find_call_after_page_config(lines)
    call = [
        "# [STEP64_WEB_FINAL_CALL_START]",
        "step64_inject_css()",
        "step64_render_now_badge()",
        "# [STEP64_WEB_FINAL_CALL_END]",
    ]
    lines[idx:idx] = call
    return "\n".join(lines) + "\n", idx


def find_html_markdown_end(lines):
    # 가장 좋은 위치: st.markdown("".join(html_parts), unsafe_allow_html=True) 직후
    for i, line in enumerate(lines):
        if "st.markdown" in line and "html_parts" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1, "after_html_parts_markdown"

    # fallback: 마지막 st.markdown 뒤
    last = None
    for i, line in enumerate(lines):
        if "st.markdown" in line:
            last = i
    if last is not None:
        bal = lines[last].count("(") - lines[last].count(")")
        j = last
        while bal > 0 and j + 1 < len(lines):
            j += 1
            bal += lines[j].count("(") - lines[j].count(")")
        return j + 1, "after_last_markdown"

    return len(lines), "end_of_file"


def insert_postprocess_call(text: str):
    lines = text.splitlines()
    idx, pos = find_html_markdown_end(lines)
    call = [
        "# [STEP64_WEB_POSTPROCESS_CALL_START]",
        "step64_postprocess_component()",
        "# [STEP64_WEB_POSTPROCESS_CALL_END]",
    ]
    lines[idx:idx] = call
    return "\n".join(lines) + "\n", pos


def patch_button_labels(text: str):
    changed = 0
    replacements = [
        ('"이번주"', '"오늘"'), ("'이번주'", "'오늘'"),
        ('"📅"', '"달력"'), ("'📅'", "'달력'"),
        ('"📝"', '"메모"'), ("'📝'", "'메모'"),
        ('"☀️"', '"조회"'), ("'☀️'", "'조회'"),
        ('"☀"', '"조회"'), ("'☀'", "'조회'"),
        ('"🌞"', '"조회"'), ("'🌞'", "'조회'"),
        ('"🔆"', '"조회"'), ("'🔆'", "'조회'"),
        ('"🌙"', '"8·9"'), ("'🌙'", "'8·9'"),
        ('"🌛"', '"8·9"'), ("'🌛'", "'8·9'"),
        ('"🌜"', '"8·9"'), ("'🌜'", "'8·9'"),
        ('"🌕"', '"8·9"'), ("'🌕'", "'8·9'"),
        ('"달\\n력"', '"달력"'), ("'달\\n력'", "'달력'"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    return text, changed


def main():
    print("==============================================")
    print("Step64 web nonfatal source + DOM fix")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup(APP)
    text = APP.read_text(encoding="utf-8", errors="replace")
    original = text

    try:
        text, removed = remove_old_blocks(text)
        text, helper_pos = ensure_helpers(text)
        text, button_changes = patch_button_labels(text)
        text, call_idx = insert_css_and_clock_call(text)
        text, post_pos = insert_postprocess_call(text)
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        compile(text, str(APP), "exec")
        print("[확인] mobile/app.py 문법 OK")
    except Exception as e:
        print("[오류] mobile/app.py 문법 확인 실패")
        print(e)
        print("패치를 저장하지 않습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    if text != original:
        APP.write_text(text, encoding="utf-8")
        print("[완료] Step64 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 기존 보정 블록 제거: {removed}")
    print(f"- helper 삽입 위치: {helper_pos}")
    print(f"- 버튼 라벨 보정: {button_changes}")
    print(f"- CSS/현재시각 호출 위치 index: {call_idx}")
    print(f"- DOM 후처리 호출 위치: {post_pos}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 현재시각 배지가 표시되는지")
    print("2. 시간표 하단 그림자 바가 생기는지")
    print("3. 메모장에 중요/일반/완료 소제목이 생기는지")
    print("4. 소제목 접힘/펼침이 되는지")
    print("5. 버튼이 오늘/달력/메모/조회/8·9로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

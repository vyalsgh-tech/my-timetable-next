# tools/step65_fix_step64_nameerror_and_reapply.py
# ------------------------------------------------------------
# Step65: Step64 NameError 복구 + 웹뷰어 보정 재적용
#
# 원인:
# - step64_inject_css() 호출이 helper 정의보다 위에 삽입되어 NameError 발생
#
# 처리:
# - step62/63/64/65 관련 helper/call 블록 제거
# - helper를 st.set_page_config 앞에 먼저 삽입
# - step65_inject_css(), step65_render_now_badge()를 set_page_config 직후 호출
# - step65_postprocess_component()를 html_parts 렌더링 직후 또는 파일 끝에 호출
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
    ("# [STEP65_WEB_FINAL_HELPERS_START]", "# [STEP65_WEB_FINAL_HELPERS_END]"),
    ("# [STEP65_WEB_FINAL_CALL_START]", "# [STEP65_WEB_FINAL_CALL_END]"),
    ("# [STEP65_WEB_POSTPROCESS_CALL_START]", "# [STEP65_WEB_POSTPROCESS_CALL_END]"),
]

HELPERS = '\n# [STEP65_WEB_FINAL_HELPERS_START]\ndef step65_current_period_info():\n    """웹뷰어 상단 현재시각/현재교시 표시용. kst_tz/period_times가 아직 없으면 안전 기본값."""\n    try:\n        now = datetime.now(kst_tz)\n    except Exception:\n        try:\n            now = datetime.now()\n        except Exception:\n            return {"clock": "--:--", "period": "", "range": "", "key": ""}\n\n    try:\n        now_mins = now.hour * 60 + now.minute\n        _periods = period_times\n    except Exception:\n        _periods = [\n            ("1교시", "08:00\\n08:50"),\n            ("2교시", "09:00\\n09:50"),\n            ("3교시", "10:00\\n10:50"),\n            ("4교시", "11:00\\n11:50"),\n            ("점심", "11:50\\n12:40"),\n            ("5교시", "12:40\\n13:30"),\n            ("6교시", "13:40\\n14:30"),\n            ("7교시", "14:40\\n15:30"),\n            ("8교시", "16:00\\n16:50"),\n            ("9교시", "17:00\\n17:50"),\n        ]\n        now_mins = now.hour * 60 + now.minute\n\n    try:\n        for p_name, t_range in _periods:\n            if p_name == "학사일정":\n                continue\n            try:\n                start_str, end_str = str(t_range).split("\\n")\n                h1, m1 = map(int, start_str.split(":"))\n                h2, m2 = map(int, end_str.split(":"))\n            except Exception:\n                continue\n\n            s_mins = h1 * 60 + m1\n            e_mins = h2 * 60 + m2\n            if s_mins <= now_mins < e_mins:\n                key = str(p_name).replace("교시", "").strip() if "교시" in str(p_name) else ("lunch" if "점심" in str(p_name) else "")\n                return {\n                    "clock": now.strftime("%H:%M"),\n                    "period": str(p_name),\n                    "range": f"{start_str}~{end_str}",\n                    "key": key,\n                }\n\n        if now_mins < 8 * 60:\n            label = "수업 전"\n        elif now_mins >= 17 * 60 + 50:\n            label = "방과 후"\n        else:\n            label = "쉬는시간"\n\n        return {"clock": now.strftime("%H:%M"), "period": label, "range": "", "key": ""}\n    except Exception:\n        return {"clock": now.strftime("%H:%M"), "period": "", "range": "", "key": ""}\n\n\ndef step65_inject_css():\n    try:\n        st.markdown(\n            """\n            <style>\n            /* [STEP65_WEB_FINAL_CSS_START] */\n            .mobile-now-row {\n                width: 100%;\n                max-width: 450px;\n                display: flex;\n                justify-content: flex-end;\n                align-items: center;\n                margin: -2px auto 6px 0;\n                min-height: 26px;\n            }\n            .mobile-now-badge {\n                display: inline-flex;\n                align-items: center;\n                gap: 6px;\n                padding: 4px 10px;\n                border-radius: 999px;\n                border: 1px solid rgba(37, 99, 235, 0.24);\n                background: linear-gradient(180deg, rgba(239, 246, 255, 0.98), rgba(219, 234, 254, 0.92));\n                color: #1e3a8a;\n                font-size: 12px;\n                line-height: 1.1;\n                box-shadow: 0 2px 6px rgba(15, 23, 42, 0.10);\n                white-space: nowrap;\n            }\n            .mobile-now-badge b { font-size: 13px; }\n\n            div[data-testid="stHorizontalBlock"] .stButton > button,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button p,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n                margin: 0 !important;\n            }\n\n            .timetable-frame {\n                width: 100%;\n                max-width: 450px;\n                margin: 0 auto 12px 0;\n                background: linear-gradient(180deg, #eef5ff 0%, #dce9f8 100%);\n                border-radius: 8px;\n                padding: 5px 5px 14px 5px;\n                box-shadow:\n                    0 12px 24px rgba(15, 23, 42, 0.16),\n                    inset 0 1px 0 rgba(255,255,255,0.92),\n                    inset 0 -1px 0 rgba(100,116,139,0.22);\n                position: relative;\n                overflow: hidden;\n            }\n            .timetable-scroll {\n                width: 100%;\n                overflow-x: auto;\n                border-radius: 6px;\n                background: transparent;\n                position: relative;\n                z-index: 1;\n            }\n            .timetable-bottom-shadow {\n                position: absolute;\n                left: 8px;\n                right: 8px;\n                bottom: 5px;\n                height: 7px;\n                border-radius: 999px;\n                background: linear-gradient(180deg, rgba(30,41,59,0.34), rgba(100,116,139,0.15));\n                box-shadow: 0 5px 9px rgba(15,23,42,0.18);\n                pointer-events: none;\n            }\n            .mobile-table {\n                border-collapse: collapse !important;\n                border-spacing: 0 !important;\n                border: 0 !important;\n                box-shadow:\n                    0 4px 10px rgba(15,23,42,0.10),\n                    0 0 0 1px rgba(30,41,59,0.88);\n                border-radius: 5px;\n                overflow: hidden;\n            }\n            .mobile-table th,\n            .mobile-table td {\n                box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);\n            }\n            .mobile-table td {\n                background-image: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(247,250,253,0.90));\n            }\n            .mobile-table th {\n                background-image: linear-gradient(180deg, rgba(229,241,255,0.98), rgba(201,223,247,0.94));\n            }\n\n            .memo-section-header {\n                padding: 5px 6px;\n                margin: 6px 0 0 0;\n                font-size: 13px;\n                font-weight: 800;\n                line-height: 1.2;\n                cursor: pointer;\n                user-select: none;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                list-style: none;\n            }\n            .memo-section-header::-webkit-details-marker { display: none; }\n            .memo-section-header.important { color: #ef4444; }\n            .memo-section-header.general { color: #0f172a; }\n            .memo-section-header.done { color: #94a3b8; }\n            .memo-group-content {\n                border-bottom: 1px solid rgba(191, 219, 254, 0.70);\n            }\n            .memo-row {\n                padding: 7px 6px;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                color: inherit;\n            }\n            .memo-row:last-child { border-bottom: 0; }\n            .memo-text, .memo-row {\n                font-size: 14px;\n                font-weight: 700;\n                line-height: 1.35;\n                word-break: keep-all;\n                overflow-wrap: anywhere;\n                white-space: pre-line;\n            }\n            .memo-time {\n                font-size: 11px;\n                opacity: 0.65;\n                margin-top: 4px;\n            }\n            .memo-done .memo-text,\n            .memo-done {\n                text-decoration: line-through;\n                text-decoration-thickness: 1.3px;\n                color: #94a3b8;\n            }\n            /* [STEP65_WEB_FINAL_CSS_END] */\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef step65_render_now_badge():\n    try:\n        info = step65_current_period_info()\n        clock = info.get("clock", "--:--")\n        period = info.get("period", "")\n        range_text = info.get("range", "")\n        detail = period\n        if range_text:\n            detail += f" · {range_text}"\n\n        st.markdown(\n            f"""\n            <div class=\'mobile-now-row\'>\n                <span class=\'mobile-now-badge\'>\n                    <b>{clock}</b>\n                    <span>{detail}</span>\n                </span>\n            </div>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef step65_postprocess_component():\n    try:\n        import streamlit.components.v1 as components\n        info = step65_current_period_info()\n        current_key = str(info.get("key", "") or "")\n        components.html(\n            f"""\n            <script>\n            (function() {{\n                const currentKey = "{current_key}";\n                function docRoot() {{\n                    try {{ return window.parent.document; }} catch(e) {{ return document; }}\n                }}\n                function visible(el) {{\n                    if (!el) return false;\n                    const r = el.getBoundingClientRect();\n                    return r.width > 2 && r.height > 2;\n                }}\n                function patchButtons(doc) {{\n                    for (const b of Array.from(doc.querySelectorAll(\'button\'))) {{\n                        const compact = (b.innerText || \'\').trim().replace(/\\\\s+/g, \'\');\n                        if ([\'☀️\',\'☀\',\'🌞\',\'🔆\'].includes(compact)) b.innerText = \'조회\';\n                        if ([\'🌙\',\'🌛\',\'🌜\',\'🌕\'].includes(compact)) b.innerText = \'8·9\';\n                        if ((b.innerText || \'\').replace(/\\\\s+/g, \'\') === \'달력\') b.innerText = \'달력\';\n                        b.style.whiteSpace = \'nowrap\';\n                        b.style.wordBreak = \'keep-all\';\n                        b.style.writingMode = \'horizontal-tb\';\n                    }}\n                }}\n                function wrapTable(doc) {{\n                    const tables = Array.from(doc.querySelectorAll(\'table\'));\n                    const table = tables.find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\')) || doc.querySelector(\'table.mobile-table\');\n                    if (!table || table.closest(\'.timetable-frame\')) return;\n                    table.classList.add(\'mobile-table\');\n                    const parent = table.parentNode;\n                    if (!parent) return;\n                    const frame = doc.createElement(\'div\');\n                    frame.className = \'timetable-frame\';\n                    const scroll = doc.createElement(\'div\');\n                    scroll.className = \'timetable-scroll\';\n                    const shadow = doc.createElement(\'div\');\n                    shadow.className = \'timetable-bottom-shadow\';\n                    parent.insertBefore(frame, table);\n                    scroll.appendChild(table);\n                    frame.appendChild(scroll);\n                    frame.appendChild(shadow);\n                }}\n                function markCurrent(doc) {{\n                    if (!currentKey) return;\n                    const table = Array.from(doc.querySelectorAll(\'table\')).find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\'));\n                    if (!table) return;\n                    for (const row of Array.from(table.querySelectorAll(\'tr\'))) {{\n                        const txt = row.innerText || \'\';\n                        let hit = false;\n                        if (currentKey === \'lunch\') hit = txt.includes(\'점심\');\n                        else hit = txt.includes(currentKey + \'교시\') || txt.includes(currentKey + \' 교시\');\n                        if (hit) {{\n                            row.style.background = \'#eaf2ff\';\n                            if (row.children.length) {{\n                                row.children[0].style.background = \'#2563eb\';\n                                row.children[0].style.color = \'#fff\';\n                                row.children[0].style.fontWeight = \'800\';\n                            }}\n                        }}\n                    }}\n                }}\n                function stripOne(el) {{\n                    const re = /^\\\\s*\\\\d+\\\\.\\\\s*/;\n                    for (const n of el.childNodes || []) {{\n                        if (n.nodeType === 3 && re.test(n.textContent || \'\')) n.textContent = (n.textContent || \'\').replace(re, \'\');\n                    }}\n                }}\n                function memoClass(text, el) {{\n                    const t = text || \'\';\n                    let strike = false;\n                    try {{\n                        let cur = el;\n                        for (let i=0; i<4 && cur; i++, cur=cur.parentElement) {{\n                            const s = window.getComputedStyle(cur);\n                            if ((s.textDecorationLine || \'\').includes(\'line-through\')) strike = true;\n                        }}\n                    }} catch(e) {{}}\n                    if (strike || /^\\\\s*(✔|✅)/.test(t)) return \'done\';\n                    if (/⭐|★/.test(t)) return \'important\';\n                    return \'general\';\n                }}\n                function findMemoContainer(doc) {{\n                    const title = Array.from(doc.querySelectorAll(\'div,h1,h2,h3,p,span\')).find(el => visible(el) && (el.innerText || \'\').includes(\'메모장\'));\n                    if (!title) return null;\n                    const top = title.getBoundingClientRect().top;\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    const cands = Array.from(doc.querySelectorAll(\'div\')).filter(el => {{\n                        if (!visible(el)) return false;\n                        const r = el.getBoundingClientRect();\n                        const txt = el.innerText || \'\';\n                        return r.top > top && r.height > 100 && dateRe.test(txt) && !(txt.includes(\'교시\') && txt.includes(\'학사일정\'));\n                    }});\n                    cands.sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height);\n                    return cands[0] || null;\n                }}\n                function rowWrap(el) {{\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    let cur = el;\n                    for (let i=0; i<5 && cur && cur.parentElement; i++, cur=cur.parentElement) {{\n                        const r = cur.getBoundingClientRect();\n                        const txt = cur.innerText || \'\';\n                        if (r.height >= 28 && r.height <= 150 && dateRe.test(txt)) return cur;\n                    }}\n                    return el;\n                }}\n                function groupMemos(doc) {{\n                    const container = findMemoContainer(doc);\n                    if (!container || container.querySelector(\'.memo-section-header\')) return;\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    const prelim = [];\n                    for (const el of Array.from(container.querySelectorAll(\'div,p,span\'))) {{\n                        if (!visible(el)) continue;\n                        const txt = (el.innerText || \'\').trim();\n                        if (dateRe.test(txt) && !txt.includes(\'메모장\')) prelim.push(rowWrap(el));\n                    }}\n                    const rows = [];\n                    for (const r of prelim) if (!rows.includes(r)) rows.push(r);\n                    const finalRows = rows.filter(r => !rows.some(o => o !== r && r.contains(o)));\n                    if (finalRows.length < 2) return;\n                    for (const r of finalRows) {{\n                        r.classList.add(\'memo-row\');\n                        stripOne(r);\n                    }}\n                    const groups = {{\n                        important: finalRows.filter(r => memoClass(r.innerText, r) === \'important\'),\n                        general: finalRows.filter(r => memoClass(r.innerText, r) === \'general\'),\n                        done: finalRows.filter(r => memoClass(r.innerText, r) === \'done\')\n                    }};\n                    const labels = [\n                        [\'important\',\'📌 중요 메모\',\'important\'],\n                        [\'general\',\'▣ 일반 메모\',\'general\'],\n                        [\'done\',\'✔ 완료 메모\',\'done\']\n                    ];\n                    const parent = finalRows[0].parentNode;\n                    if (!parent) return;\n                    const frag = doc.createDocumentFragment();\n                    for (const [key,label,cls] of labels) {{\n                        const arr = groups[key] || [];\n                        if (!arr.length) continue;\n                        const details = doc.createElement(\'details\');\n                        details.open = true;\n                        const summary = doc.createElement(\'summary\');\n                        summary.className = \'memo-section-header \' + cls;\n                        summary.textContent = label + \' (\' + arr.length + \')\';\n                        const body = doc.createElement(\'div\');\n                        body.className = \'memo-group-content\';\n                        for (const row of arr) body.appendChild(row);\n                        details.appendChild(summary);\n                        details.appendChild(body);\n                        frag.appendChild(details);\n                    }}\n                    parent.insertBefore(frag, finalRows[0] || null);\n                }}\n                function run() {{\n                    const doc = docRoot();\n                    patchButtons(doc);\n                    wrapTable(doc);\n                    markCurrent(doc);\n                    groupMemos(doc);\n                }}\n                run();\n                setTimeout(run, 200);\n                setTimeout(run, 700);\n                setTimeout(run, 1500);\n            }})();\n            </script>\n            """,\n            height=1,\n            width=1,\n        )\n    except Exception:\n        pass\n# [STEP65_WEB_FINAL_HELPERS_END]\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step65_nameerror_fix_{STAMP}{path.suffix}")
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


def remove_all_blocks(text: str):
    removed = 0
    for start, end in BLOCK_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1

    # 혹시 블록 밖에 남은 단독 호출도 제거
    lines = []
    removed_calls = 0
    bad_calls = [
        "step64_inject_css()",
        "step64_render_now_badge()",
        "step64_postprocess_component()",
        "step65_inject_css()",
        "step65_render_now_badge()",
        "step65_postprocess_component()",
    ]
    for line in text.splitlines():
        if line.strip() in bad_calls:
            removed_calls += 1
            continue
        lines.append(line)
    return "\n".join(lines) + "\n", removed, removed_calls


def ensure_imports(text: str):
    added = []
    if not re.search(r"^\s*import\s+html\b", text, re.M):
        for anchor in ["import re\n", "import io\n", "import os\n", "import json\n"]:
            if anchor in text:
                text = text.replace(anchor, anchor + "import html\n", 1)
                added.append("html")
                break
    return text, added


def find_set_page_config_range(lines):
    for i, line in enumerate(lines):
        if "st.set_page_config" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return i, j + 1
    return None, None


def insert_helpers_before_set_page_config(text: str):
    lines = text.splitlines()
    start, end = find_set_page_config_range(lines)
    idx = start if start is not None else 0
    lines[idx:idx] = HELPERS.strip("\n").splitlines()
    return "\n".join(lines) + "\n", idx


def insert_css_clock_after_set_page_config(text: str):
    lines = text.splitlines()
    start, end = find_set_page_config_range(lines)
    idx = end if end is not None else 0
    call = [
        "# [STEP65_WEB_FINAL_CALL_START]",
        "step65_inject_css()",
        "step65_render_now_badge()",
        "# [STEP65_WEB_FINAL_CALL_END]",
    ]
    lines[idx:idx] = call
    return "\n".join(lines) + "\n", idx


def find_html_render_insert_index(lines):
    for i, line in enumerate(lines):
        if "st.markdown" in line and "html_parts" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1, "after_html_parts_markdown"

    # fallback: 가장 마지막 줄
    return len(lines), "end_of_file"


def insert_postprocess_call(text: str):
    lines = text.splitlines()
    idx, pos = find_html_render_insert_index(lines)
    call = [
        "# [STEP65_WEB_POSTPROCESS_CALL_START]",
        "step65_postprocess_component()",
        "# [STEP65_WEB_POSTPROCESS_CALL_END]",
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
    print("Step65 fix Step64 NameError and reapply")
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
        text, removed_blocks, removed_calls = remove_all_blocks(text)
        text, added_imports = ensure_imports(text)
        text, button_changes = patch_button_labels(text)
        text, helper_idx = insert_helpers_before_set_page_config(text)
        text, call_idx = insert_css_clock_after_set_page_config(text)
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
        print("[완료] Step65 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 기존 보정 블록 제거: {removed_blocks}")
    print(f"- 단독 잘못된 호출 제거: {removed_calls}")
    print(f"- 추가 import: {added_imports}")
    print(f"- 버튼 라벨 보정: {button_changes}")
    print(f"- helper 삽입 위치 index: {helper_idx}")
    print(f"- CSS/현재시각 호출 위치 index: {call_idx}")
    print(f"- DOM 후처리 호출 위치: {post_pos}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. NameError가 사라지는지")
    print("2. 현재시각 배지가 표시되는지")
    print("3. 시간표 하단 그림자 바가 생기는지")
    print("4. 메모장에 중요/일반/완료 소제목이 생기는지")
    print("5. 버튼이 오늘/달력/메모/조회/8·9로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

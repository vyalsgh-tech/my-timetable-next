# tools/step60_web_viewer_layout_memo_clock_refine.py
# ------------------------------------------------------------
# Step60: 웹뷰어 레이아웃/메모그룹/현재시각 위치 정밀 보정
#
# 실행:
#   python tools\step60_web_viewer_layout_memo_clock_refine.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

START = "# [WEB_VIEWER_PC_LIKE_UI_START]"
END = "# [WEB_VIEWER_PC_LIKE_UI_END]"
CALL_START = "# [WEB_VIEWER_PC_LIKE_UI_CALL_START]"
CALL_END = "# [WEB_VIEWER_PC_LIKE_UI_CALL_END]"

INJECT_CODE = '\n# [WEB_VIEWER_PC_LIKE_UI_START]\ndef _mh_now_period_info():\n    try:\n        from datetime import datetime, time\n        now = datetime.now()\n        t = now.time()\n        periods = [\n            ("1교시", "08:00~08:50", time(8, 0), time(8, 50), "1"),\n            ("2교시", "09:00~09:50", time(9, 0), time(9, 50), "2"),\n            ("3교시", "10:00~10:50", time(10, 0), time(10, 50), "3"),\n            ("4교시", "11:00~11:50", time(11, 0), time(11, 50), "4"),\n            ("점심", "11:50~12:40", time(11, 50), time(12, 40), "lunch"),\n            ("5교시", "12:40~13:30", time(12, 40), time(13, 30), "5"),\n            ("6교시", "13:40~14:30", time(13, 40), time(14, 30), "6"),\n            ("7교시", "14:40~15:30", time(14, 40), time(15, 30), "7"),\n            ("8교시", "16:00~16:50", time(16, 0), time(16, 50), "8"),\n            ("9교시", "17:00~17:50", time(17, 0), time(17, 50), "9"),\n        ]\n        for label, range_text, start, end, key in periods:\n            if start <= t < end:\n                return {"label": label, "range": range_text, "key": key, "clock": now.strftime("%H:%M")}\n        return {\n            "label": "수업 전" if t < time(8, 0) else ("방과 후" if t >= time(17, 50) else "쉬는시간"),\n            "range": "",\n            "key": "",\n            "clock": now.strftime("%H:%M"),\n        }\n    except Exception:\n        return {"label": "", "range": "", "key": "", "clock": "--:--"}\n\n\ndef _mh_render_clock_badge():\n    try:\n        info = _mh_now_period_info()\n        sub = (" · " + info.get("range", "")) if info.get("range") else ""\n        st.markdown(\n            f\'<div class="mh-now-clock-row"><span class="mh-now-clock-pill"><b>{info.get("clock","--:--")}</b><span>{info.get("label","")}{sub}</span></span></div>\',\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef _mh_inject_pc_like_web_css():\n    try:\n        import streamlit.components.v1 as components\n    except Exception:\n        components = None\n\n    try:\n        info = _mh_now_period_info()\n        current_key = info.get("key", "")\n\n        st.markdown(\n            """\n            <style>\n            /* Step60: current clock 위치 */\n            .mh-now-clock-row {\n                display: flex;\n                justify-content: flex-end;\n                align-items: center;\n                margin: 0.08rem 0 0.38rem 0;\n                min-height: 28px;\n            }\n            .mh-now-clock-pill {\n                display: inline-flex;\n                align-items: center;\n                gap: 0.38rem;\n                padding: 0.22rem 0.64rem;\n                border-radius: 999px;\n                border: 1px solid rgba(37, 99, 235, 0.25);\n                background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(219,234,254,0.9));\n                color: #1e3a8a;\n                font-size: 0.78rem;\n                line-height: 1.2;\n                box-shadow: 0 2px 7px rgba(15, 23, 42, 0.10);\n            }\n            .mh-now-clock-pill b { font-size: 0.86rem; }\n\n            /* Step60: 상단 버튼 패널 */\n            .mh-toolbar-panel {\n                background: rgba(226, 236, 249, 0.88) !important;\n                border-radius: 9px !important;\n                border: 1px solid rgba(191, 207, 226, 0.78) !important;\n                box-shadow:\n                    0 8px 15px rgba(15, 23, 42, 0.12),\n                    inset 0 1px 0 rgba(255,255,255,0.82),\n                    inset 0 -1px 0 rgba(148,163,184,0.18) !important;\n                padding: 0.33rem 0.36rem !important;\n                margin-bottom: 0.75rem !important;\n            }\n            .mh-toolbar-panel div[data-testid="stHorizontalBlock"] {\n                gap: 0.44rem !important;\n            }\n            div[data-testid="stButton"] > button,\n            .stButton > button {\n                min-width: 54px !important;\n                height: 41px !important;\n                padding: 0.32rem 0.68rem !important;\n                border-radius: 8px !important;\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                line-height: 1.1 !important;\n                display: inline-flex !important;\n                align-items: center !important;\n                justify-content: center !important;\n                text-align: center !important;\n            }\n            div[data-testid="stButton"] > button p,\n            .stButton > button p,\n            button p {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n                line-height: 1.1 !important;\n                margin: 0 !important;\n            }\n\n            /* Step60: 시간표 패널 - 사용자가 표시한 위/아래 입체감 강화 */\n            .mh-timetable-card {\n                position: relative !important;\n                background: linear-gradient(180deg, #eef5ff 0%, #dce9f8 100%) !important;\n                border-radius: 8px !important;\n                padding: 0.42rem 0.42rem 1.18rem 0.42rem !important;\n                margin: 0.25rem 0 1.05rem 0 !important;\n                box-shadow:\n                    0 12px 24px rgba(15, 23, 42, 0.16),\n                    inset 0 1px 0 rgba(255,255,255,0.95),\n                    inset 0 -1px 0 rgba(100,116,139,0.22) !important;\n            }\n            .mh-timetable-card::after {\n                content: "";\n                position: absolute;\n                left: 0.5rem;\n                right: 0.5rem;\n                bottom: 0.42rem;\n                height: 0.48rem;\n                border-radius: 999px;\n                background: linear-gradient(180deg, rgba(30,41,59,0.34), rgba(100,116,139,0.16));\n                box-shadow: 0 5px 9px rgba(15,23,42,0.18);\n                pointer-events: none;\n            }\n            .mh-timetable-card table {\n                margin: 0 !important;\n                border-collapse: separate !important;\n                border-spacing: 0 !important;\n                overflow: hidden !important;\n                border-radius: 6px !important;\n                box-shadow:\n                    0 5px 10px rgba(15,23,42,0.11),\n                    inset 0 1px 0 rgba(255,255,255,0.7) !important;\n                background: #ffffff !important;\n                position: relative !important;\n                z-index: 1 !important;\n            }\n            .mh-timetable-card table th,\n            .mh-timetable-card table td {\n                box-shadow: inset 0 1px 0 rgba(255,255,255,0.75), inset 1px 0 0 rgba(255,255,255,0.32) !important;\n            }\n            .mh-timetable-card table td {\n                background-image: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(247,250,253,0.9)) !important;\n            }\n            .mh-timetable-card table th {\n                background-image: linear-gradient(180deg, rgba(229,241,255,0.98), rgba(201,223,247,0.94)) !important;\n            }\n            .mh-current-period,\n            tr.mh-current-period > th,\n            tr.mh-current-period > td {\n                background: #eaf2ff !important;\n                box-shadow: inset 0 0 0 2px rgba(37,99,235,0.2), 0 2px 8px rgba(37,99,235,0.08) !important;\n            }\n            .mh-current-period-label {\n                background: #2563eb !important;\n                color: #ffffff !important;\n                font-weight: 800 !important;\n            }\n\n            /* Step60: 메모 PC형 그룹 헤더 */\n            .mh-memo-group-title {\n                font-weight: 800;\n                padding: 0.36rem 0.42rem 0.26rem 0.42rem;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                cursor: pointer;\n                user-select: none;\n                display: flex;\n                align-items: center;\n                gap: 0.25rem;\n                background: rgba(239,246,255,0.38);\n            }\n            .mh-memo-title-important { color: #ef4444; }\n            .mh-memo-title-normal { color: #0f172a; }\n            .mh-memo-title-done { color: #94a3b8; }\n            .mh-memo-collapsed + .mh-memo-group-body { display: none !important; }\n            .mh-memo-group-body { border-bottom: 1px solid rgba(191, 219, 254, 0.75); }\n            .mh-memo-dom-row {\n                padding: 0.36rem 0.3rem !important;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.65) !important;\n            }\n            .mh-memo-dom-row:last-child { border-bottom: 0 !important; }\n            .memo-number,\n            .mh-memo-number,\n            [data-memo-number="true"] { display: none !important; }\n\n            @media (max-width: 640px) {\n                .mh-now-clock-row { justify-content: flex-end; margin-right: 0.15rem; }\n                .mh-now-clock-pill { font-size: 0.72rem; padding: 0.18rem 0.48rem; }\n                div[data-testid="stButton"] > button,\n                .stButton > button {\n                    min-width: 50px !important;\n                    height: 40px !important;\n                    padding: 0.25rem 0.55rem !important;\n                }\n                .mh-timetable-card {\n                    padding: 0.28rem 0.28rem 1.0rem 0.28rem !important;\n                }\n            }\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n\n        js = f"""\n        <script>\n        (function() {{\n            const currentKey = "{current_key}";\n\n            function docRoot() {{\n                try {{ return window.parent.document; }} catch(e) {{ return document; }}\n            }}\n            function visible(el) {{\n                if (!el) return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 2 && r.height > 2;\n            }}\n            function directText(el) {{\n                let out = "";\n                for (const n of el.childNodes || []) {{\n                    if (n.nodeType === 3) out += n.textContent || "";\n                }}\n                return out;\n            }}\n            function stripOne(el) {{\n                const re = /^\\\\s*\\\\d+\\\\.\\\\s*/;\n                for (const n of el.childNodes || []) {{\n                    if (n.nodeType === 3 && re.test(n.textContent || "")) {{\n                        n.textContent = (n.textContent || "").replace(re, "");\n                    }}\n                }}\n            }}\n            function stripMemoNumbers(doc) {{\n                const re = /^\\\\s*\\\\d+\\\\.\\\\s*/;\n                for (const el of Array.from(doc.querySelectorAll(\'div, span, p, strong, b\'))) {{\n                    if (!el || !el.childNodes) continue;\n                    if (re.test(directText(el))) stripOne(el);\n                }}\n            }}\n            function patchButtons(doc) {{\n                for (const b of Array.from(doc.querySelectorAll(\'button\'))) {{\n                    const compact = (b.innerText || \'\').trim().replace(/\\\\s+/g, \'\');\n                    if ([\'☀️\',\'☀\',\'🌞\',\'🔆\'].includes(compact)) b.innerText = \'조회\';\n                    if ([\'🌙\',\'🌛\',\'🌜\',\'🌕\'].includes(compact)) b.innerText = \'8·9\';\n                    if ((b.innerText || \'\').replace(/\\\\s+/g, \'\') === \'달력\') b.innerText = \'달력\';\n                    b.style.whiteSpace = \'nowrap\';\n                    b.style.wordBreak = \'keep-all\';\n                    b.style.writingMode = \'horizontal-tb\';\n                    const p = b.querySelector(\'p\');\n                    if (p) {{\n                        p.style.whiteSpace = \'nowrap\';\n                        p.style.wordBreak = \'keep-all\';\n                        p.style.writingMode = \'horizontal-tb\';\n                    }}\n                }}\n            }}\n            function markToolbar(doc) {{\n                const buttons = Array.from(doc.querySelectorAll(\'button\'));\n                const todayBtn = buttons.find(b => (b.innerText || \'\').includes(\'오늘\'));\n                if (!todayBtn) return;\n                let node = todayBtn;\n                for (let i = 0; i < 8 && node; i++, node = node.parentElement) {{\n                    if ((node.innerText || \'\').includes(\'오늘\') &&\n                        (node.innerText || \'\').includes(\'메모\') &&\n                        ((node.innerText || \'\').includes(\'조회\') || (node.innerText || \'\').includes(\'☀\'))) {{\n                        node.classList.add(\'mh-toolbar-panel\');\n                        break;\n                    }}\n                }}\n            }}\n            function markTable(doc) {{\n                const tables = Array.from(doc.querySelectorAll(\'table\'));\n                if (!tables.length) return;\n                let table = tables.find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\')) || tables[0];\n                let node = table.parentElement;\n                for (let i = 0; i < 5 && node; i++, node = node.parentElement) {{\n                    const txt = node.innerText || \'\';\n                    if (txt.includes(\'교시\') && txt.includes(\'학사일정\') && !txt.includes(\'메모장\')) {{\n                        node.classList.add(\'mh-timetable-card\');\n                        break;\n                    }}\n                }}\n                if (currentKey) {{\n                    for (const row of Array.from(table.querySelectorAll(\'tr\'))) {{\n                        const txt = row.innerText || \'\';\n                        let hit = false;\n                        if (currentKey === \'lunch\') hit = txt.includes(\'점심\');\n                        else hit = txt.includes(currentKey + \'교시\') || txt.includes(currentKey + \' 교시\');\n                        if (hit) {{\n                            row.classList.add(\'mh-current-period\');\n                            if (row.children.length) row.children[0].classList.add(\'mh-current-period-label\');\n                        }}\n                    }}\n                }}\n            }}\n            function memoClass(text, el) {{\n                const t = text || "";\n                const hasStrike = (function(node) {{\n                    try {{\n                        let cur = node;\n                        for (let i=0; i<4 && cur; i++, cur=cur.parentElement) {{\n                            const s = window.getComputedStyle(cur);\n                            if ((s.textDecorationLine || \'\').includes(\'line-through\')) return true;\n                            if ((cur.style && cur.style.textDecoration || \'\').includes(\'line-through\')) return true;\n                        }}\n                    }} catch(e) {{}}\n                    return false;\n                }})(el);\n                if (hasStrike || /^\\\\s*(✔|✅)/.test(t)) return \'done\';\n                if (/⭐|★/.test(t)) return \'important\';\n                return \'normal\';\n            }}\n            function findMemoTitle(doc) {{\n                const all = Array.from(doc.querySelectorAll(\'div, h1, h2, h3, p, span\'));\n                return all.find(el => (el.innerText || \'\').includes(\'메모장\'));\n            }}\n            function findMemoContainer(doc) {{\n                const title = findMemoTitle(doc);\n                if (!title) return null;\n                const top = title.getBoundingClientRect().top;\n                const divs = Array.from(doc.querySelectorAll(\'div\')).filter(visible);\n                const cands = divs.filter(el => {{\n                    const r = el.getBoundingClientRect();\n                    const txt = el.innerText || "";\n                    if (r.top <= top) return false;\n                    if (txt.includes(\'시간표\') && txt.includes(\'학사일정\')) return false;\n                    const hasMemoLike = /(^|\\\\n)\\\\s*(\\\\d+\\\\.\\\\s*)?(⭐|☆|✔|○|✅|[가-힣A-Za-z0-9])/.test(txt) && /\\\\b\\\\d{2}\\\\s+\\\\d{2}:\\\\d{2}\\\\b/.test(txt);\n                    return hasMemoLike && r.height > 120;\n                }});\n                cands.sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height);\n                return cands[0] || null;\n            }}\n            function rowWrapper(el) {{\n                let cur = el;\n                for (let i=0; i<4 && cur && cur.parentElement; i++, cur=cur.parentElement) {{\n                    const r = cur.getBoundingClientRect();\n                    const txt = cur.innerText || "";\n                    if (r.height >= 34 && r.height <= 120 && /\\\\b\\\\d{2}\\\\s+\\\\d{2}:\\\\d{2}\\\\b/.test(txt)) return cur;\n                }}\n                return el;\n            }}\n            function pickRows(container) {{\n                if (!container) return [];\n                const nodes = Array.from(container.querySelectorAll(\'div, p, span\')).filter(visible);\n                const prelim = [];\n                for (const el of nodes) {{\n                    const txt = (el.innerText || \'\').trim();\n                    const r = el.getBoundingClientRect();\n                    if (r.height < 14 || r.height > 130) continue;\n                    if (!/\\\\b\\\\d{2}\\\\s+\\\\d{2}:\\\\d{2}\\\\b/.test(txt)) continue;\n                    if (txt.includes(\'메모장\')) continue;\n                    prelim.push(rowWrapper(el));\n                }}\n                const uniq = [];\n                for (const el of prelim) {{\n                    if (!uniq.includes(el)) uniq.push(el);\n                }}\n                return uniq.filter(el => !uniq.some(other => other !== el && el.contains(other)));\n            }}\n            function groupMemos(doc) {{\n                const container = findMemoContainer(doc);\n                if (!container) return;\n                if (container.querySelector(\'.mh-memo-group-title\')) return;\n\n                const rows = pickRows(container);\n                if (rows.length < 2) return;\n\n                for (const row of rows) {{\n                    row.classList.add(\'mh-memo-dom-row\');\n                    stripOne(row);\n                }}\n\n                const groups = {{\n                    important: rows.filter(r => memoClass(r.innerText, r) === \'important\'),\n                    normal: rows.filter(r => memoClass(r.innerText, r) === \'normal\'),\n                    done: rows.filter(r => memoClass(r.innerText, r) === \'done\')\n                }};\n                const labels = [\n                    [\'important\', \'📌 중요 메모\', \'mh-memo-title-important\'],\n                    [\'normal\', \'▣ 일반 메모\', \'mh-memo-title-normal\'],\n                    [\'done\', \'✔ 완료 메모\', \'mh-memo-title-done\']\n                ];\n\n                const parent = rows[0].parentNode;\n                if (!parent) return;\n                const frag = doc.createDocumentFragment();\n\n                for (const [key, label, cls] of labels) {{\n                    const arr = groups[key] || [];\n                    if (!arr.length) continue;\n                    const title = doc.createElement(\'div\');\n                    title.className = \'mh-memo-group-title \' + cls;\n                    title.textContent = `${{label}} (${{arr.length}}) ▲`;\n\n                    const body = doc.createElement(\'div\');\n                    body.className = \'mh-memo-group-body\';\n\n                    title.addEventListener(\'click\', () => {{\n                        const collapsed = title.classList.toggle(\'mh-memo-collapsed\');\n                        title.textContent = `${{label}} (${{arr.length}}) ` + (collapsed ? \'▼\' : \'▲\');\n                    }});\n\n                    for (const row of arr) body.appendChild(row);\n                    frag.appendChild(title);\n                    frag.appendChild(body);\n                }}\n\n                parent.insertBefore(frag, rows[0] || null);\n            }}\n            function run() {{\n                const doc = docRoot();\n                patchButtons(doc);\n                markToolbar(doc);\n                markTable(doc);\n                groupMemos(doc);\n                stripMemoNumbers(doc);\n            }}\n            run();\n            setTimeout(run, 150);\n            setTimeout(run, 400);\n            setTimeout(run, 900);\n            setTimeout(run, 1600);\n            setTimeout(run, 2800);\n\n            try {{\n                const doc = docRoot();\n                const obs = new MutationObserver(() => {{\n                    clearTimeout(window.__mhStep60Timer);\n                    window.__mhStep60Timer = setTimeout(run, 120);\n                }});\n                obs.observe(doc.body, {{childList:true, subtree:true}});\n                setTimeout(() => obs.disconnect(), 7000);\n            }} catch(e) {{}}\n        }})();\n        </script>\n        """\n\n        if components is not None:\n            components.html(js, height=0, width=0)\n        else:\n            st.markdown(js, unsafe_allow_html=True)\n\n    except Exception:\n        pass\n# [WEB_VIEWER_PC_LIKE_UI_END]\n'
CALL_CODE = '\n# [WEB_VIEWER_PC_LIKE_UI_CALL_START]\ntry:\n    _mh_inject_pc_like_web_css()\n    _mh_render_clock_badge()\nexcept Exception:\n    pass\n# [WEB_VIEWER_PC_LIKE_UI_CALL_END]\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step60_web_layout_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def remove_block(text: str, start_marker: str, end_marker: str):
    start = text.find(start_marker)
    if start == -1:
        return text, False
    end = text.find(end_marker, start)
    if end == -1:
        return text, False
    end_line = text.find("\n", end)
    end_line = len(text) if end_line == -1 else end_line + 1
    return text[:start] + text[end_line:], True


def find_top_level_import_end(lines):
    last = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if not stripped or stripped.startswith("#"):
            continue
        if indent == 0 and (stripped.startswith("import ") or stripped.startswith("from ")):
            last = i
            continue
        if last >= 0:
            break
    return last + 1 if last >= 0 else 0


def find_title_line_index(lines):
    # 현재시각 배지가 제목 아래, 버튼 위로 오도록 제목 출력 직후를 최우선으로 찾는다.
    for i, line in enumerate(lines):
        if ("시간표 뷰어" in line or "명덕외고 시간표" in line) and ("st." in line or "markdown" in line or "write" in line):
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1, "after_title"
    return None, None


def find_call_insert_index(lines):
    idx, pos = find_title_line_index(lines)
    if idx is not None:
        return idx, pos

    for i, line in enumerate(lines):
        if "st.set_page_config" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1, "after_set_page_config"

    return find_top_level_import_end(lines), "after_imports"


def patch_button_labels_source(text: str):
    changed = 0
    replacements = [
        ('"☀️"', '"조회"'), ("'☀️'", "'조회'"),
        ('"☀"', '"조회"'), ("'☀'", "'조회'"),
        ('"🌞"', '"조회"'), ("'🌞'", "'조회'"),
        ('"🔆"', '"조회"'), ("'🔆'", "'조회'"),
        ('"🌙"', '"8·9"'), ("'🌙'", "'8·9'"),
        ('"🌛"', '"8·9"'), ("'🌛'", "'8·9'"),
        ('"🌜"', '"8·9"'), ("'🌜'", "'8·9'"),
        ('"🌕"', '"8·9"'), ("'🌕'", "'8·9'"),
        ('"달\n력"', '"달력"'), ("'달\n력'", "'달력'"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    return text, changed


def remove_memo_number_patterns(text: str):
    total = 0
    keyword_positions = [m.start() for m in re.finditer("메모장|memo", text, flags=re.IGNORECASE)]
    if not keyword_positions:
        return text, 0

    ranges = []
    for pos in keyword_positions:
        ranges.append((max(0, pos - 1500), min(len(text), pos + 9000)))
    ranges.sort()

    merged = []
    for s, e in ranges:
        if not merged or s > merged[-1][1]:
            merged.append([s, e])
        else:
            merged[-1][1] = max(merged[-1][1], e)

    pieces = []
    last = 0
    for s, e in merged:
        pieces.append(text[last:s])
        region = text[s:e]
        old = region

        region = re.sub(r"\{(?:i|idx|index|num|number|display_num|memo_num|memo_index)\s*(?:[+\-]\s*\d+)?\}\.\s*", "", region)
        region = re.sub(r"(\*\*|<b>|<strong>)\s*\{(?:i|idx|index|num|number|display_num|memo_num|memo_index)\s*(?:[+\-]\s*\d+)?\}\.\s*", r"\1", region)
        region = re.sub(r"f?['\"]\s*\{(?:i|idx|index|num|number|display_num|memo_num|memo_index)\s*(?:[+\-]\s*\d+)?\}\.\s*['\"]\s*\+", "", region)

        if region != old:
            total += 1
        pieces.append(region)
        last = e

    pieces.append(text[last:])
    return "".join(pieces), total


def patch_mobile_app():
    if not APP.exists():
        raise RuntimeError(f"mobile/app.py 파일이 없습니다: {APP}")

    backup(APP)

    text = APP.read_text(encoding="utf-8", errors="replace")
    original = text

    text, removed_helper = remove_block(text, START, END)
    text, removed_call = remove_block(text, CALL_START, CALL_END)

    text, label_changes = patch_button_labels_source(text)
    text, number_changes = remove_memo_number_patterns(text)

    lines = text.splitlines()
    helper_idx = find_top_level_import_end(lines)
    lines.insert(helper_idx, INJECT_CODE.strip("\n"))

    text = "\n".join(lines) + "\n"
    lines = text.splitlines()

    call_idx, call_pos = find_call_insert_index(lines)
    lines.insert(call_idx, CALL_CODE.strip("\n"))

    text = "\n".join(lines) + "\n"

    try:
        compile(text, str(APP), "exec")
        print("[확인] mobile/app.py 문법 OK")
    except Exception as e:
        print("[오류] mobile/app.py 문법 확인 실패")
        print(e)
        print("패치를 저장하지 않습니다.")
        raise

    if text != original:
        APP.write_text(text, encoding="utf-8")
        print("[완료] mobile/app.py Step60 패치 저장")
    else:
        print("[안내] 변경 없음")

    return {
        "removed_helper": removed_helper,
        "removed_call": removed_call,
        "label_changes": label_changes,
        "number_changes": number_changes,
        "call_pos": call_pos,
    }


def main():
    print("==============================================")
    print("Step60 web viewer layout/memo/clock refine")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    try:
        info = patch_mobile_app()
    except Exception as e:
        print("[오류] Step60 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    print()
    print("[완료] Step60 웹뷰어 정밀 보정 적용")
    print(f"- 기존 helper 제거 후 재삽입: {info['removed_helper']}")
    print(f"- 기존 call 제거 후 재삽입: {info['removed_call']}")
    print(f"- 태양/달 버튼 소스 교체 횟수: {info['label_changes']}")
    print(f"- 메모 번호 소스 제거 구간 수: {info['number_changes']}")
    print(f"- 현재시각 호출부 삽입 위치: {info['call_pos']}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 현재시각 배지가 제목 아래/버튼 위에 위치하는지")
    print("2. 시간표 위/아래에 PC버전처럼 패널 그림자와 하단 입체감이 생겼는지")
    print("3. 메모장에 중요/일반/완료 소제목이 생기고 접힘/펼침이 되는지")
    print("4. 태양/달 버튼이 조회/8·9로 유지되는지")
    print("5. 달력 글자가 가로로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

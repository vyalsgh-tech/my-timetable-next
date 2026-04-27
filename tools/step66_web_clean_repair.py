# tools/step66_web_clean_repair.py
# ------------------------------------------------------------
# Step66: 웹뷰어 화면 복구/정리
#
# 해결:
# 1) Step65에서 상단에 생긴 시각 표시 제거 후, 버튼 영역 바로 위/설정 아이콘 위쪽에 배치
# 2) 시간표 외곽 테두리/파란 사각 배경을 줄이고 하단 그림자만 깔끔하게 적용
# 3) 메모 리스트 유실 방지: 기존 행을 이동하지 않고 clone 방식으로 그룹 생성
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
    ("# [STEP66_WEB_CLEAN_HELPERS_START]", "# [STEP66_WEB_CLEAN_HELPERS_END]"),
    ("# [STEP66_WEB_CLEAN_CALL_START]", "# [STEP66_WEB_CLEAN_CALL_END]"),
    ("# [STEP66_WEB_CLEAN_POSTPROCESS_START]", "# [STEP66_WEB_CLEAN_POSTPROCESS_END]"),
]

HELPERS = '\n# [STEP66_WEB_CLEAN_HELPERS_START]\ndef step66_current_period_info():\n    """웹뷰어 현재시각/현재교시 계산. 필요한 전역값이 없어도 안전하게 동작."""\n    try:\n        now = datetime.now(kst_tz)\n    except Exception:\n        try:\n            now = datetime.now()\n        except Exception:\n            return {"clock": "--:--", "period": "", "range": "", "key": ""}\n\n    periods_default = [\n        ("1교시", "08:00\\n08:50"),\n        ("2교시", "09:00\\n09:50"),\n        ("3교시", "10:00\\n10:50"),\n        ("4교시", "11:00\\n11:50"),\n        ("점심", "11:50\\n12:40"),\n        ("5교시", "12:40\\n13:30"),\n        ("6교시", "13:40\\n14:30"),\n        ("7교시", "14:40\\n15:30"),\n        ("8교시", "16:00\\n16:50"),\n        ("9교시", "17:00\\n17:50"),\n    ]\n\n    try:\n        periods = period_times\n    except Exception:\n        periods = periods_default\n\n    try:\n        now_mins = now.hour * 60 + now.minute\n        for p_name, t_range in periods:\n            if str(p_name) == "학사일정":\n                continue\n            try:\n                start_str, end_str = str(t_range).split("\\n")\n                h1, m1 = map(int, start_str.split(":"))\n                h2, m2 = map(int, end_str.split(":"))\n            except Exception:\n                continue\n\n            s_mins = h1 * 60 + m1\n            e_mins = h2 * 60 + m2\n\n            if s_mins <= now_mins < e_mins:\n                key = ""\n                if "교시" in str(p_name):\n                    key = str(p_name).replace("교시", "").strip()\n                elif "점심" in str(p_name):\n                    key = "lunch"\n                return {\n                    "clock": now.strftime("%H:%M"),\n                    "period": str(p_name),\n                    "range": f"{start_str}~{end_str}",\n                    "key": key,\n                }\n\n        if now_mins < 8 * 60:\n            label = "수업 전"\n        elif now_mins >= 17 * 60 + 50:\n            label = "방과 후"\n        else:\n            label = "쉬는시간"\n\n        return {\n            "clock": now.strftime("%H:%M"),\n            "period": label,\n            "range": "",\n            "key": "",\n        }\n    except Exception:\n        return {\n            "clock": now.strftime("%H:%M"),\n            "period": "",\n            "range": "",\n            "key": "",\n        }\n\n\ndef step66_inject_css():\n    """상단 버튼/시간표/메모 그룹용 CSS. 현재시각 배지는 JS가 버튼 위에 배치."""\n    try:\n        st.markdown(\n            """\n            <style>\n            /* [STEP66_WEB_CLEAN_CSS_START] */\n\n            /* 상단 버튼: 글자 세로깨짐 방지 */\n            div[data-testid="stHorizontalBlock"] .stButton > button,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button p,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n                margin: 0 !important;\n            }\n\n            /* 시각 표시: 제목 아래, 버튼 줄 위, 오른쪽 정렬 */\n            .step66-clock-row {\n                width: min(450px, 100%);\n                display: flex;\n                justify-content: flex-end;\n                align-items: center;\n                margin: 0 0 4px 0;\n                min-height: 24px;\n                pointer-events: none;\n            }\n            .step66-clock-pill {\n                display: inline-flex;\n                align-items: center;\n                gap: 6px;\n                padding: 3px 9px;\n                border-radius: 999px;\n                border: 1px solid rgba(37, 99, 235, 0.24);\n                background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(219,234,254,0.92));\n                color: #1e3a8a;\n                font-size: 12px;\n                line-height: 1.15;\n                box-shadow: 0 2px 5px rgba(15, 23, 42, 0.09);\n                white-space: nowrap;\n            }\n            .step66-clock-pill b {\n                font-size: 13px;\n            }\n\n            /* 시간표: 외곽 사각형 느낌 줄이고 하단 그림자만 세련되게 */\n            .timetable-frame {\n                width: min(450px, 100%);\n                margin: 0 0 12px 0;\n                padding: 0 0 13px 0;\n                background: transparent !important;\n                border: 0 !important;\n                box-shadow: none !important;\n                position: relative;\n                overflow: visible;\n            }\n            .timetable-scroll {\n                width: 100%;\n                overflow-x: auto;\n                border-radius: 5px;\n                background: #fff;\n                box-shadow:\n                    0 5px 12px rgba(15, 23, 42, 0.10),\n                    0 0 0 1px rgba(30, 41, 59, 0.18);\n                position: relative;\n                z-index: 1;\n            }\n            .timetable-bottom-shadow {\n                position: absolute;\n                left: 8px;\n                right: 8px;\n                bottom: 3px;\n                height: 7px;\n                border-radius: 999px;\n                background: linear-gradient(180deg, rgba(51,65,85,0.24), rgba(148,163,184,0.10));\n                filter: blur(0.2px);\n                box-shadow: 0 4px 8px rgba(15,23,42,0.14);\n                pointer-events: none;\n            }\n            .mobile-table {\n                border-collapse: collapse !important;\n                border-spacing: 0 !important;\n                border: 0 !important;\n                box-shadow: none !important;\n                margin: 0 !important;\n            }\n            .mobile-table th,\n            .mobile-table td {\n                box-shadow: inset 0 1px 0 rgba(255,255,255,0.50);\n            }\n            .mobile-table td {\n                background-image: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.92));\n            }\n            .mobile-table th {\n                background-image: linear-gradient(180deg, rgba(230,241,255,0.98), rgba(205,225,247,0.94));\n            }\n\n            /* 메모 그룹 */\n            .memo-section-header {\n                padding: 5px 6px;\n                margin: 6px 0 0 0;\n                font-size: 13px;\n                font-weight: 800;\n                line-height: 1.2;\n                cursor: pointer;\n                user-select: none;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                list-style: none;\n            }\n            .memo-section-header::-webkit-details-marker {\n                display: none;\n            }\n            .memo-section-header.important { color: #ef4444; }\n            .memo-section-header.general { color: #0f172a; }\n            .memo-section-header.done { color: #94a3b8; }\n            .memo-group-content {\n                border-bottom: 1px solid rgba(191, 219, 254, 0.70);\n            }\n            .memo-row {\n                padding: 7px 6px !important;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75) !important;\n                color: inherit;\n                min-height: 34px;\n            }\n            .memo-row:last-child {\n                border-bottom: 0 !important;\n            }\n            .memo-row,\n            .memo-row * {\n                word-break: keep-all;\n                overflow-wrap: anywhere;\n            }\n            .memo-done,\n            .memo-done * {\n                text-decoration: line-through;\n                text-decoration-thickness: 1.3px;\n                color: #94a3b8 !important;\n            }\n\n            /* [STEP66_WEB_CLEAN_CSS_END] */\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef step66_postprocess_component():\n    """HTML 렌더링 후 시간표/메모장 DOM 정리. 행 이동 대신 clone 방식으로 메모 유실 방지."""\n    try:\n        import streamlit.components.v1 as components\n        info = step66_current_period_info()\n        current_key = str(info.get("key", "") or "")\n        clock = str(info.get("clock", "--:--") or "--:--")\n        period = str(info.get("period", "") or "")\n        range_text = str(info.get("range", "") or "")\n        detail = period + ((" · " + range_text) if range_text else "")\n\n        components.html(\n            f"""\n            <script>\n            (function() {{\n                const currentKey = {current_key!r};\n                const clock = {clock!r};\n                const detail = {detail!r};\n\n                function docRoot() {{\n                    try {{ return window.parent.document; }} catch(e) {{ return document; }}\n                }}\n                function visible(el) {{\n                    if (!el) return false;\n                    const r = el.getBoundingClientRect();\n                    return r.width > 2 && r.height > 2;\n                }}\n\n                function patchButtons(doc) {{\n                    for (const b of Array.from(doc.querySelectorAll(\'button\'))) {{\n                        const compact = (b.innerText || \'\').trim().replace(/\\\\s+/g, \'\');\n                        if ([\'☀️\',\'☀\',\'🌞\',\'🔆\'].includes(compact)) b.innerText = \'조회\';\n                        if ([\'🌙\',\'🌛\',\'🌜\',\'🌕\'].includes(compact)) b.innerText = \'8·9\';\n                        if ((b.innerText || \'\').replace(/\\\\s+/g, \'\') === \'달력\') b.innerText = \'달력\';\n                        b.style.whiteSpace = \'nowrap\';\n                        b.style.wordBreak = \'keep-all\';\n                        b.style.writingMode = \'horizontal-tb\';\n                    }}\n                }}\n\n                function findToolbar(doc) {{\n                    const buttons = Array.from(doc.querySelectorAll(\'button\')).filter(visible);\n                    const today = buttons.find(b => (b.innerText || \'\').includes(\'오늘\'));\n                    if (!today) return null;\n                    let node = today;\n                    for (let i = 0; i < 8 && node; i++, node = node.parentElement) {{\n                        const txt = node.innerText || \'\';\n                        if (\n                            txt.includes(\'오늘\') &&\n                            txt.includes(\'메모\') &&\n                            (txt.includes(\'조회\') || txt.includes(\'☀\') || txt.includes(\'🌞\')) &&\n                            (txt.includes(\'8\') || txt.includes(\'🌙\') || txt.includes(\'⚙\'))\n                        ) {{\n                            return node;\n                        }}\n                    }}\n                    return today.parentElement;\n                }}\n\n                function placeClock(doc) {{\n                    const toolbar = findToolbar(doc);\n                    if (!toolbar || !toolbar.parentNode) return;\n\n                    let row = doc.querySelector(\'.step66-clock-row\');\n                    if (!row) {{\n                        row = doc.createElement(\'div\');\n                        row.className = \'step66-clock-row\';\n                        row.innerHTML = \'<span class="step66-clock-pill"><b></b><span></span></span>\';\n                    }}\n                    const b = row.querySelector(\'b\');\n                    const s = row.querySelector(\'span span\');\n                    if (b) b.textContent = clock;\n                    if (s) s.textContent = detail;\n\n                    if (toolbar.previousSibling !== row) {{\n                        toolbar.parentNode.insertBefore(row, toolbar);\n                    }}\n                }}\n\n                function wrapTable(doc) {{\n                    const tables = Array.from(doc.querySelectorAll(\'table\'));\n                    const table = tables.find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\')) || doc.querySelector(\'table.mobile-table\');\n                    if (!table) return;\n\n                    table.classList.add(\'mobile-table\');\n\n                    const oldFrame = table.closest(\'.timetable-frame\');\n                    if (oldFrame) {{\n                        oldFrame.classList.add(\'timetable-frame\');\n                        if (!oldFrame.querySelector(\'.timetable-bottom-shadow\')) {{\n                            const shadow = doc.createElement(\'div\');\n                            shadow.className = \'timetable-bottom-shadow\';\n                            oldFrame.appendChild(shadow);\n                        }}\n                        return;\n                    }}\n\n                    const parent = table.parentNode;\n                    if (!parent) return;\n\n                    const frame = doc.createElement(\'div\');\n                    frame.className = \'timetable-frame\';\n                    const scroll = doc.createElement(\'div\');\n                    scroll.className = \'timetable-scroll\';\n                    const shadow = doc.createElement(\'div\');\n                    shadow.className = \'timetable-bottom-shadow\';\n\n                    parent.insertBefore(frame, table);\n                    scroll.appendChild(table);\n                    frame.appendChild(scroll);\n                    frame.appendChild(shadow);\n                }}\n\n                function markCurrent(doc) {{\n                    if (!currentKey) return;\n                    const table = Array.from(doc.querySelectorAll(\'table\')).find(t => (t.innerText || \'\').includes(\'교시\') && (t.innerText || \'\').includes(\'학사일정\'));\n                    if (!table) return;\n                    for (const row of Array.from(table.querySelectorAll(\'tr\'))) {{\n                        const txt = row.innerText || \'\';\n                        let hit = false;\n                        if (currentKey === \'lunch\') hit = txt.includes(\'점심\');\n                        else hit = txt.includes(currentKey + \'교시\') || txt.includes(currentKey + \' 교시\');\n                        if (hit) {{\n                            row.style.background = \'#eaf2ff\';\n                            if (row.children.length) {{\n                                row.children[0].style.background = \'#2563eb\';\n                                row.children[0].style.color = \'#fff\';\n                                row.children[0].style.fontWeight = \'800\';\n                            }}\n                        }}\n                    }}\n                }}\n\n                function stripNumberInClone(el) {{\n                    const re = /^\\\\s*\\\\d+\\\\.\\\\s*/;\n                    for (const n of el.childNodes || []) {{\n                        if (n.nodeType === 3 && re.test(n.textContent || \'\')) {{\n                            n.textContent = (n.textContent || \'\').replace(re, \'\');\n                        }}\n                    }}\n                    for (const child of Array.from(el.children || [])) stripNumberInClone(child);\n                }}\n\n                function memoClass(text, el) {{\n                    const t = text || \'\';\n                    let strike = false;\n                    try {{\n                        let cur = el;\n                        for (let i = 0; i < 4 && cur; i++, cur = cur.parentElement) {{\n                            const s = window.getComputedStyle(cur);\n                            if ((s.textDecorationLine || \'\').includes(\'line-through\')) strike = true;\n                            if ((cur.style && cur.style.textDecoration || \'\').includes(\'line-through\')) strike = true;\n                        }}\n                    }} catch(e) {{}}\n\n                    if (strike || /^\\\\s*(✔|✅)/.test(t)) return \'done\';\n                    if (/⭐|★/.test(t)) return \'important\';\n                    return \'general\';\n                }}\n\n                function findMemoContainer(doc) {{\n                    const title = Array.from(doc.querySelectorAll(\'div,h1,h2,h3,p,span\')).find(el => visible(el) && (el.innerText || \'\').includes(\'메모장\'));\n                    if (!title) return null;\n                    const top = title.getBoundingClientRect().top;\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n\n                    const cands = Array.from(doc.querySelectorAll(\'div\')).filter(el => {{\n                        if (!visible(el)) return false;\n                        const r = el.getBoundingClientRect();\n                        const txt = el.innerText || \'\';\n                        return (\n                            r.top > top &&\n                            r.height > 80 &&\n                            dateRe.test(txt) &&\n                            !(txt.includes(\'교시\') && txt.includes(\'학사일정\')) &&\n                            !el.querySelector(\'.memo-section-header\')\n                        );\n                    }});\n                    cands.sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height);\n                    return cands[0] || null;\n                }}\n\n                function rowWrap(el) {{\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    let cur = el;\n                    for (let i = 0; i < 5 && cur && cur.parentElement; i++, cur = cur.parentElement) {{\n                        const r = cur.getBoundingClientRect();\n                        const txt = cur.innerText || \'\';\n                        if (r.height >= 26 && r.height <= 160 && dateRe.test(txt)) return cur;\n                    }}\n                    return el;\n                }}\n\n                function groupMemos(doc) {{\n                    const container = findMemoContainer(doc);\n                    if (!container || container.querySelector(\'.memo-section-header\')) return;\n\n                    const dateRe = /\\\\b(?:\\\\d{{2}}\\\\.\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}}\\\\.\\\\d{{2}}|\\\\d{{2}})\\\\s+\\\\d{{2}}:\\\\d{{2}}\\\\b/;\n                    const prelim = [];\n                    for (const el of Array.from(container.querySelectorAll(\'div,p,span\'))) {{\n                        if (!visible(el)) continue;\n                        const txt = (el.innerText || \'\').trim();\n                        if (dateRe.test(txt) && !txt.includes(\'메모장\')) prelim.push(rowWrap(el));\n                    }}\n\n                    const rows = [];\n                    for (const r of prelim) if (!rows.includes(r)) rows.push(r);\n                    const finalRows = rows.filter(r => !rows.some(o => o !== r && r.contains(o)));\n                    if (finalRows.length < 1) return;\n\n                    const grouped = {{\n                        important: [],\n                        general: [],\n                        done: []\n                    }};\n\n                    for (const row of finalRows) {{\n                        const cls = memoClass(row.innerText, row);\n                        const clone = row.cloneNode(true);\n                        clone.classList.add(\'memo-row\');\n                        if (cls === \'done\') clone.classList.add(\'memo-done\');\n                        stripNumberInClone(clone);\n                        grouped[cls].push(clone);\n                    }}\n\n                    const labels = [\n                        [\'important\', \'📌 중요 메모\', \'important\'],\n                        [\'general\', \'▣ 일반 메모\', \'general\'],\n                        [\'done\', \'✔ 완료 메모\', \'done\']\n                    ];\n\n                    const frag = doc.createDocumentFragment();\n                    let made = 0;\n\n                    for (const [key, label, cls] of labels) {{\n                        const arr = grouped[key] || [];\n                        if (!arr.length) continue;\n\n                        const details = doc.createElement(\'details\');\n                        details.open = true;\n                        const summary = doc.createElement(\'summary\');\n                        summary.className = \'memo-section-header \' + cls;\n                        summary.textContent = label + \' (\' + arr.length + \')\';\n                        const body = doc.createElement(\'div\');\n                        body.className = \'memo-group-content\';\n\n                        for (const clone of arr) body.appendChild(clone);\n                        details.appendChild(summary);\n                        details.appendChild(body);\n                        frag.appendChild(details);\n                        made++;\n                    }}\n\n                    if (!made) return;\n\n                    container.innerHTML = \'\';\n                    container.appendChild(frag);\n                }}\n\n                function run() {{\n                    const doc = docRoot();\n                    patchButtons(doc);\n                    placeClock(doc);\n                    wrapTable(doc);\n                    markCurrent(doc);\n                    groupMemos(doc);\n                }}\n\n                run();\n                setTimeout(run, 250);\n                setTimeout(run, 800);\n                setTimeout(run, 1600);\n            }})();\n            </script>\n            """,\n            height=1,\n            width=1,\n        )\n    except Exception:\n        pass\n# [STEP66_WEB_CLEAN_HELPERS_END]\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step66_web_clean_repair_{STAMP}{path.suffix}")
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

    # 이전 패치에서 블록 밖에 남은 단독 호출 제거
    bad_calls = {
        "step64_inject_css()",
        "step64_render_now_badge()",
        "step64_postprocess_component()",
        "step65_inject_css()",
        "step65_render_now_badge()",
        "step65_postprocess_component()",
        "step66_inject_css()",
        "step66_postprocess_component()",
    }
    lines = []
    removed_calls = 0
    for line in text.splitlines():
        if line.strip() in bad_calls:
            removed_calls += 1
            continue
        lines.append(line)
    return "\n".join(lines) + "\n", removed, removed_calls


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


def insert_css_call_after_set_page_config(text: str):
    lines = text.splitlines()
    start, end = find_set_page_config_range(lines)
    idx = end if end is not None else 0
    call = [
        "# [STEP66_WEB_CLEAN_CALL_START]",
        "step66_inject_css()",
        "# [STEP66_WEB_CLEAN_CALL_END]",
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
    return len(lines), "end_of_file"


def insert_postprocess_call(text: str):
    lines = text.splitlines()
    idx, pos = find_html_render_insert_index(lines)
    call = [
        "# [STEP66_WEB_CLEAN_POSTPROCESS_START]",
        "step66_postprocess_component()",
        "# [STEP66_WEB_CLEAN_POSTPROCESS_END]",
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
    print("Step66 web clean repair")
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
        text, button_changes = patch_button_labels(text)
        text, helper_idx = insert_helpers_before_set_page_config(text)
        text, css_idx = insert_css_call_after_set_page_config(text)
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
        print("[완료] Step66 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 기존 보정 블록 제거: {removed_blocks}")
    print(f"- 단독 잘못된 호출 제거: {removed_calls}")
    print(f"- 버튼 라벨 보정: {button_changes}")
    print(f"- helper 삽입 위치 index: {helper_idx}")
    print(f"- CSS 호출 위치 index: {css_idx}")
    print(f"- DOM 후처리 호출 위치: {post_pos}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 상단 맨 위 시각 배지가 사라졌는지")
    print("2. 시각 배지가 버튼 영역 바로 위, 설정 아이콘 위쪽에 표시되는지")
    print("3. 시간표 테두리가 덜 지저분하고 하단 그림자만 깔끔하게 보이는지")
    print("4. 메모 리스트가 다시 보이는지")
    print("5. 메모장에 중요/일반/완료 소제목이 생기는지")
    print("6. 소제목 접힘/펼침이 되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

# tools/step67_web_title_clock_done_table_refine.py
# ------------------------------------------------------------
# Step67: 웹뷰어 상단/완료메모/시간표 카드 디자인 정리
#
# 해결:
# 1) 현재시각 배지를 제목줄 우측으로 이동해 제목과 나란히 배치
# 2) 완료 메모 분류 강화 (취소선/완료아이콘/회색 스타일 감지)
# 3) 시간표 프레임 디자인 정리 (지저분한 테두리/하단 바 제거)
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
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
    ("# [STEP67_WEB_REFINED_HELPERS_START]", "# [STEP67_WEB_REFINED_HELPERS_END]"),
    ("# [STEP67_WEB_REFINED_CALL_START]", "# [STEP67_WEB_REFINED_CALL_END]"),
    ("# [STEP67_WEB_REFINED_POSTPROCESS_START]", "# [STEP67_WEB_REFINED_POSTPROCESS_END]"),
]

HELPERS = r'''
# [STEP67_WEB_REFINED_HELPERS_START]
def step67_current_period_info():
    """웹뷰어 현재시각/현재교시 계산. 필요한 전역값이 없어도 안전하게 동작."""
    try:
        now = datetime.now(kst_tz)
    except Exception:
        try:
            now = datetime.now()
        except Exception:
            return {"clock": "--:--", "period": "", "range": "", "key": ""}

    periods_default = [
        ("1교시", "08:00\n08:50"),
        ("2교시", "09:00\n09:50"),
        ("3교시", "10:00\n10:50"),
        ("4교시", "11:00\n11:50"),
        ("점심", "11:50\n12:40"),
        ("5교시", "12:40\n13:30"),
        ("6교시", "13:40\n14:30"),
        ("7교시", "14:40\n15:30"),
        ("8교시", "16:00\n16:50"),
        ("9교시", "17:00\n17:50"),
    ]

    try:
        periods = period_times
    except Exception:
        periods = periods_default

    try:
        now_mins = now.hour * 60 + now.minute
        for p_name, t_range in periods:
            if str(p_name) == "학사일정":
                continue
            try:
                start_str, end_str = str(t_range).split("\n")
                h1, m1 = map(int, start_str.split(":"))
                h2, m2 = map(int, end_str.split(":"))
            except Exception:
                continue

            s_mins = h1 * 60 + m1
            e_mins = h2 * 60 + m2
            if s_mins <= now_mins < e_mins:
                key = ""
                if "교시" in str(p_name):
                    key = str(p_name).replace("교시", "").strip()
                elif "점심" in str(p_name):
                    key = "lunch"
                return {
                    "clock": now.strftime("%H:%M"),
                    "period": str(p_name),
                    "range": f"{start_str}~{end_str}",
                    "key": key,
                }

        if now_mins < 8 * 60:
            label = "수업 전"
        elif now_mins >= 17 * 60 + 50:
            label = "방과 후"
        else:
            label = "쉬는시간"
        return {"clock": now.strftime("%H:%M"), "period": label, "range": "", "key": ""}
    except Exception:
        return {"clock": now.strftime("%H:%M"), "period": "", "range": "", "key": ""}


def step67_inject_css():
    try:
        st.markdown(
            """
            <style>
            /* [STEP67_WEB_REFINED_CSS_START] */

            /* 상단 버튼: 글자 세로깨짐 방지 */
            div[data-testid="stHorizontalBlock"] .stButton > button,
            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
                white-space: nowrap !important;
                word-break: keep-all !important;
                overflow-wrap: normal !important;
                writing-mode: horizontal-tb !important;
            }
            div[data-testid="stHorizontalBlock"] .stButton > button p,
            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p {
                white-space: nowrap !important;
                word-break: keep-all !important;
                overflow-wrap: normal !important;
                writing-mode: horizontal-tb !important;
                margin: 0 !important;
            }

            /* 제목 + 시각 */
            .step67-title-row {
                width: min(450px, 100%);
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 10px;
                margin: 0 0 8px 0;
            }
            .step67-title-host {
                min-width: 0;
                flex: 1 1 auto;
            }
            .step67-clock-host {
                flex: 0 0 auto;
                display: flex;
                justify-content: flex-end;
                align-items: flex-start;
                min-width: 96px;
                padding-top: 1px;
            }
            .step67-clock-pill {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 10px;
                border-radius: 999px;
                border: 1px solid rgba(96, 165, 250, 0.34);
                background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));
                color: #1e40af;
                font-size: 12px;
                line-height: 1.1;
                white-space: nowrap;
                box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);
            }
            .step67-clock-pill b {
                font-size: 13px;
                font-weight: 800;
            }
            .step67-clock-pill span {
                opacity: 0.92;
            }

            /* 시간표 카드: 현대적인 모바일 카드 느낌 */
            .timetable-frame {
                width: min(450px, 100%);
                margin: 0 0 14px 0;
                padding: 0;
                position: relative;
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
                overflow: visible;
            }
            .timetable-scroll {
                width: 100%;
                overflow-x: auto;
                overflow-y: visible;
                border-radius: 10px;
                background: linear-gradient(180deg, rgba(251,253,255,0.98), rgba(242,247,252,0.96));
                box-shadow:
                    0 10px 22px rgba(15, 23, 42, 0.10),
                    0 2px 6px rgba(15, 23, 42, 0.06),
                    inset 0 1px 0 rgba(255,255,255,0.72);
                position: relative;
                z-index: 1;
            }
            .timetable-scroll::after {
                content: "";
                position: absolute;
                left: 16px;
                right: 16px;
                bottom: -8px;
                height: 10px;
                border-radius: 999px;
                background: radial-gradient(ellipse at center, rgba(100,116,139,0.24) 0%, rgba(100,116,139,0.12) 42%, rgba(100,116,139,0.04) 68%, rgba(100,116,139,0) 100%);
                pointer-events: none;
                z-index: -1;
            }
            .mobile-table {
                border-collapse: collapse !important;
                border-spacing: 0 !important;
                margin: 0 !important;
                background: transparent !important;
                box-shadow: none !important;
            }
            .mobile-table th,
            .mobile-table td {
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.46);
            }
            .mobile-table th {
                background-image: linear-gradient(180deg, rgba(232,240,251,0.98), rgba(212,226,243,0.95));
            }
            .mobile-table td {
                background-image: linear-gradient(180deg, rgba(255,255,255,0.995), rgba(248,250,252,0.97));
            }

            /* 메모 그룹 */
            .memo-section-header {
                padding: 7px 6px 6px 6px;
                margin: 8px 0 0 0;
                font-size: 13px;
                font-weight: 800;
                line-height: 1.2;
                cursor: pointer;
                user-select: none;
                border-bottom: 1px solid rgba(191, 219, 254, 0.88);
                list-style: none;
                background: transparent;
            }
            .memo-section-header::-webkit-details-marker {
                display: none;
            }
            .memo-section-header.important { color: #ef4444; }
            .memo-section-header.general { color: #0f172a; }
            .memo-section-header.done { color: #94a3b8; }
            .memo-group-content {
                border-bottom: 1px solid rgba(191, 219, 254, 0.72);
            }
            .memo-row {
                padding: 7px 6px !important;
                border-bottom: 1px solid rgba(191, 219, 254, 0.75) !important;
                color: inherit;
                min-height: 34px;
            }
            .memo-row:last-child {
                border-bottom: 0 !important;
            }
            .memo-row,
            .memo-row * {
                word-break: keep-all;
                overflow-wrap: anywhere;
            }
            .memo-done,
            .memo-done * {
                text-decoration: line-through !important;
                text-decoration-thickness: 1.25px !important;
                text-decoration-skip-ink: auto;
                color: #9aa7b6 !important;
            }

            /* [STEP67_WEB_REFINED_CSS_END] */
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def step67_postprocess_component():
    try:
        import streamlit.components.v1 as components

        info = step67_current_period_info()
        current_key = str(info.get("key", "") or "")
        clock = str(info.get("clock", "--:--") or "--:--")
        period = str(info.get("period", "") or "")
        range_text = str(info.get("range", "") or "")
        detail = period + ((" " + range_text) if range_text else "")

        components.html(
            f"""
            <script>
            (function() {{
                const currentKey = {current_key!r};
                const clock = {clock!r};
                const detail = {detail!r};

                function docRoot() {{
                    try {{ return window.parent.document; }} catch(e) {{ return document; }}
                }}
                function visible(el) {{
                    if (!el) return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 2 && r.height > 2;
                }}

                function patchButtons(doc) {{
                    for (const b of Array.from(doc.querySelectorAll('button'))) {{
                        const compact = (b.innerText || '').trim().replace(/\s+/g, '');
                        if (['☀️','☀','🌞','🔆'].includes(compact)) b.innerText = '조회';
                        if (['🌙','🌛','🌜','🌕'].includes(compact)) b.innerText = '8·9';
                        if ((b.innerText || '').replace(/\s+/g, '') === '달력') b.innerText = '달력';
                        b.style.whiteSpace = 'nowrap';
                        b.style.wordBreak = 'keep-all';
                        b.style.writingMode = 'horizontal-tb';
                    }}
                }}

                function findTitleEl(doc) {{
                    return Array.from(doc.querySelectorAll('div,h1,h2,h3,p,span')).find(el => {{
                        if (!visible(el)) return false;
                        const txt = (el.innerText || '').trim();
                        return txt.includes('명덕외고') && txt.includes('시간표 뷰어');
                    }}) || null;
                }}

                function placeClockInTitleRow(doc) {{
                    const titleEl = findTitleEl(doc);
                    if (!titleEl || !titleEl.parentNode) return;

                    let row = doc.querySelector('.step67-title-row');
                    let clockHost = null;
                    if (!row) {{
                        row = doc.createElement('div');
                        row.className = 'step67-title-row';

                        const titleHost = doc.createElement('div');
                        titleHost.className = 'step67-title-host';
                        const tParent = titleEl.parentNode;
                        tParent.insertBefore(row, titleEl);
                        row.appendChild(titleHost);
                        titleHost.appendChild(titleEl);

                        clockHost = doc.createElement('div');
                        clockHost.className = 'step67-clock-host';
                        row.appendChild(clockHost);
                    }} else {{
                        clockHost = row.querySelector('.step67-clock-host');
                        if (!clockHost) {{
                            clockHost = doc.createElement('div');
                            clockHost.className = 'step67-clock-host';
                            row.appendChild(clockHost);
                        }}
                    }}

                    let pill = row.querySelector('.step67-clock-pill');
                    if (!pill) {{
                        pill = doc.createElement('span');
                        pill.className = 'step67-clock-pill';
                        pill.innerHTML = '<b></b><span></span>';
                        clockHost.appendChild(pill);
                    }}
                    const b = pill.querySelector('b');
                    const s = pill.querySelector('span');
                    if (b) b.textContent = clock;
                    if (s) s.textContent = detail;
                }}

                function wrapTable(doc) {{
                    const tables = Array.from(doc.querySelectorAll('table'));
                    const table = tables.find(t => (t.innerText || '').includes('교시') && (t.innerText || '').includes('학사일정')) || doc.querySelector('table.mobile-table');
                    if (!table) return;
                    table.classList.add('mobile-table');

                    let frame = table.closest('.timetable-frame');
                    if (frame) return;

                    const parent = table.parentNode;
                    if (!parent) return;
                    frame = doc.createElement('div');
                    frame.className = 'timetable-frame';
                    const scroll = doc.createElement('div');
                    scroll.className = 'timetable-scroll';
                    parent.insertBefore(frame, table);
                    scroll.appendChild(table);
                    frame.appendChild(scroll);
                }}

                function markCurrent(doc) {{
                    if (!currentKey) return;
                    const table = Array.from(doc.querySelectorAll('table')).find(t => (t.innerText || '').includes('교시') && (t.innerText || '').includes('학사일정'));
                    if (!table) return;
                    for (const row of Array.from(table.querySelectorAll('tr'))) {{
                        const txt = row.innerText || '';
                        let hit = false;
                        if (currentKey === 'lunch') hit = txt.includes('점심');
                        else hit = txt.includes(currentKey + '교시') || txt.includes(currentKey + ' 교시');
                        if (hit) {{
                            row.style.background = '#eaf2ff';
                            if (row.children.length) {{
                                row.children[0].style.background = '#2563eb';
                                row.children[0].style.color = '#fff';
                                row.children[0].style.fontWeight = '800';
                            }}
                        }}
                    }}
                }}

                function stripNumberInClone(el) {{
                    const re = /^\s*\d+\.\s*/;
                    for (const n of Array.from(el.childNodes || [])) {{
                        if (n.nodeType === 3 && re.test(n.textContent || '')) {{
                            n.textContent = (n.textContent || '').replace(re, '');
                        }}
                    }}
                    for (const child of Array.from(el.children || [])) stripNumberInClone(child);
                }}

                function textHasDoneMark(text) {{
                    return /^\s*(✔|✅|☑|✓)/.test(text || '');
                }}

                function hasLineThroughDeep(el) {{
                    if (!el) return false;
                    const all = [el, ...Array.from(el.querySelectorAll('*'))];
                    for (const node of all) {{
                        try {{
                            const s = window.getComputedStyle(node);
                            const deco = (s.textDecorationLine || '') + ' ' + (s.textDecoration || '') + ' ' + (node.style?.textDecoration || '');
                            if (deco.includes('line-through')) return true;
                        }} catch(e) {{}}
                    }}
                    return false;
                }}

                function looksGrayDone(el) {{
                    const all = [el, ...Array.from(el.querySelectorAll('*'))];
                    for (const node of all) {{
                        try {{
                            const s = window.getComputedStyle(node);
                            const c = s.color || '';
                            if (/rgb\((1[3-7]\d|9\d|8\d),\s*(1[3-7]\d|9\d|8\d),\s*(1[3-7]\d|9\d|8\d)\)/.test(c)) return true;
                        }} catch(e) {{}}
                    }}
                    return false;
                }}

                function memoClass(text, el) {{
                    const t = text || '';
                    if (textHasDoneMark(t)) return 'done';
                    if (hasLineThroughDeep(el)) return 'done';
                    if (looksGrayDone(el) && !/⭐|★/.test(t)) return 'done';
                    if (/⭐|★/.test(t)) return 'important';
                    return 'general';
                }}

                function findMemoContainer(doc) {{
                    const title = Array.from(doc.querySelectorAll('div,h1,h2,h3,p,span')).find(el => visible(el) && (el.innerText || '').includes('메모장'));
                    if (!title) return null;
                    const top = title.getBoundingClientRect().top;
                    const dateRe = /\b(?:\d{{2}}\.\d{{2}}\.\d{{2}}|\d{{2}}\.\d{{2}}|\d{{2}})\s+\d{{2}}:\d{{2}}\b/;
                    const cands = Array.from(doc.querySelectorAll('div')).filter(el => {{
                        if (!visible(el)) return false;
                        const r = el.getBoundingClientRect();
                        const txt = el.innerText || '';
                        return r.top > top && r.height > 80 && dateRe.test(txt) && !(txt.includes('교시') && txt.includes('학사일정'));
                    }});
                    cands.sort((a,b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height);
                    return cands[0] || null;
                }}

                function rowWrap(el) {{
                    const dateRe = /\b(?:\d{{2}}\.\d{{2}}\.\d{{2}}|\d{{2}}\.\d{{2}}|\d{{2}})\s+\d{{2}}:\d{{2}}\b/;
                    let cur = el;
                    for (let i = 0; i < 6 && cur && cur.parentElement; i++, cur = cur.parentElement) {{
                        const r = cur.getBoundingClientRect();
                        const txt = cur.innerText || '';
                        if (r.height >= 26 && r.height <= 180 && dateRe.test(txt)) return cur;
                    }}
                    return el;
                }}

                function groupMemos(doc) {{
                    const container = findMemoContainer(doc);
                    if (!container) return;
                    if (container.dataset.step67Grouped === '1') return;

                    const dateRe = /\b(?:\d{{2}}\.\d{{2}}\.\d{{2}}|\d{{2}}\.\d{{2}}|\d{{2}})\s+\d{{2}}:\d{{2}}\b/;
                    const prelim = [];
                    for (const el of Array.from(container.querySelectorAll('div,p,span'))) {{
                        if (!visible(el)) continue;
                        const txt = (el.innerText || '').trim();
                        if (dateRe.test(txt) && !txt.includes('메모장')) prelim.push(rowWrap(el));
                    }}

                    const rows = [];
                    for (const r of prelim) if (!rows.includes(r)) rows.push(r);
                    const finalRows = rows.filter(r => !rows.some(o => o !== r && r.contains(o)));
                    if (!finalRows.length) return;

                    const grouped = {{ important: [], general: [], done: [] }};
                    for (const row of finalRows) {{
                        const cls = memoClass(row.innerText, row);
                        const clone = row.cloneNode(true);
                        clone.classList.add('memo-row');
                        if (cls === 'done') clone.classList.add('memo-done');
                        stripNumberInClone(clone);
                        grouped[cls].push(clone);
                    }}

                    const labels = [
                        ['important', '📌 중요 메모', 'important'],
                        ['general', '▣ 일반 메모', 'general'],
                        ['done', '✔ 완료 메모', 'done'],
                    ];

                    const frag = doc.createDocumentFragment();
                    let made = 0;
                    for (const [key, label, cls] of labels) {{
                        const arr = grouped[key] || [];
                        if (!arr.length) continue;
                        const details = doc.createElement('details');
                        details.open = true;
                        const summary = doc.createElement('summary');
                        summary.className = 'memo-section-header ' + cls;
                        summary.textContent = label + ' (' + arr.length + ')';
                        const body = doc.createElement('div');
                        body.className = 'memo-group-content';
                        for (const clone of arr) body.appendChild(clone);
                        details.appendChild(summary);
                        details.appendChild(body);
                        frag.appendChild(details);
                        made++;
                    }}
                    if (!made) return;

                    container.innerHTML = '';
                    container.appendChild(frag);
                    container.dataset.step67Grouped = '1';
                }}

                function run() {{
                    const doc = docRoot();
                    patchButtons(doc);
                    placeClockInTitleRow(doc);
                    wrapTable(doc);
                    markCurrent(doc);
                    groupMemos(doc);
                }}

                run();
                setTimeout(run, 250);
                setTimeout(run, 700);
                setTimeout(run, 1400);
                setTimeout(run, 2200);
            }})();
            </script>
            """,
            height=1,
            width=1,
        )
    except Exception:
        pass
# [STEP67_WEB_REFINED_HELPERS_END]
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step67_web_title_clock_done_table_refine_{STAMP}{path.suffix}")
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

    bad_calls = {
        "step64_inject_css()",
        "step64_render_now_badge()",
        "step64_postprocess_component()",
        "step65_inject_css()",
        "step65_render_now_badge()",
        "step65_postprocess_component()",
        "step66_inject_css()",
        "step66_postprocess_component()",
        "step67_inject_css()",
        "step67_postprocess_component()",
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
    start, _ = find_set_page_config_range(lines)
    idx = start if start is not None else 0
    lines[idx:idx] = HELPERS.strip("\n").splitlines()
    return "\n".join(lines) + "\n", idx


def insert_css_call_after_set_page_config(text: str):
    lines = text.splitlines()
    _, end = find_set_page_config_range(lines)
    idx = end if end is not None else 0
    call = [
        "# [STEP67_WEB_REFINED_CALL_START]",
        "step67_inject_css()",
        "# [STEP67_WEB_REFINED_CALL_END]",
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
        "# [STEP67_WEB_REFINED_POSTPROCESS_START]",
        "step67_postprocess_component()",
        "# [STEP67_WEB_REFINED_POSTPROCESS_END]",
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
    print("====================================================")
    print("Step67 web title/clock/done/table refine")
    print("====================================================")
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
        print("[완료] Step67 패치 저장")
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
    print("1. 제목과 현재시각 배지가 같은 줄에 좌우 배치되는지")
    print("2. 완료 메모가 일반 메모와 분리되어 완료 메모 소제목 아래로 가는지")
    print("3. 시간표 카드 외곽이 더 깔끔하고, 이상한 하단 바가 사라졌는지")
    print("4. 현재 교시 강조가 유지되는지")
    print("5. 중요/일반/완료 메모 접힘/펼침이 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

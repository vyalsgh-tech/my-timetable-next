# tools/step68_web_clock_memo_table_cleanup.py
# ------------------------------------------------------------
# Step68: 웹뷰어 현재시각/메모 소분류/시간표 카드 디자인 재정리
#
# 해결 목표
# 1) 현재시각 복구: 제목과 같은 줄 우측에 시각 배지 표시
# 2) 메모 소분류 복구: 중요/일반/완료 메모 + 접힘/펼침
# 3) 시간표 카드 디자인 단순화: 지저분한 외곽/하단 바 제거, 깔끔한 카드형
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
    ("# [STEP68_WEB_HELPERS_START]", "# [STEP68_WEB_HELPERS_END]"),
    ("# [STEP68_WEB_CALL_START]", "# [STEP68_WEB_CALL_END]"),
    ("# [STEP68_WEB_POSTPROCESS_START]", "# [STEP68_WEB_POSTPROCESS_END]"),
]

HELPERS = r'''
# [STEP68_WEB_HELPERS_START]
def step68_current_period_info():
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

        return {
            "clock": now.strftime("%H:%M"),
            "period": label,
            "range": "",
            "key": "",
        }
    except Exception:
        return {
            "clock": now.strftime("%H:%M"),
            "period": "",
            "range": "",
            "key": "",
        }


def step68_inject_css():
    try:
        st.markdown(
            """
            <style>
            /* [STEP68_WEB_CSS_START] */

            /* 상단 버튼: 세로 깨짐 방지 */
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

            /* 제목 + 시각 배지 */
            .step68-title-row {
                width: min(450px, 100%);
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 10px;
                margin: 0 0 8px 0;
            }
            .step68-title-host {
                flex: 1 1 auto;
                min-width: 0;
            }
            .step68-clock-host {
                flex: 0 0 auto;
                display: flex;
                justify-content: flex-end;
                align-items: flex-start;
                min-width: 104px;
            }
            .step68-clock-pill {
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
                box-shadow: 0 2px 8px rgba(59, 130, 246, 0.12);
            }
            .step68-clock-time {
                font-size: 13px;
                font-weight: 800;
            }
            .step68-clock-state {
                opacity: 0.92;
            }

            /* 시간표 카드: 단순하고 깔끔하게 */
            .step68-table-card {
                width: min(450px, 100%);
                margin: 0 0 14px 0;
                padding: 0;
                border-radius: 12px;
                background: linear-gradient(180deg, rgba(252,253,255,0.98), rgba(244,247,251,0.98));
                border: 1px solid rgba(148,163,184,0.20);
                box-shadow: 0 10px 24px rgba(15,23,42,0.08), 0 2px 6px rgba(15,23,42,0.04);
                overflow: hidden;
            }
            .step68-table-scroll {
                width: 100%;
                overflow-x: auto;
                overflow-y: hidden;
                background: transparent;
            }
            .mobile-table {
                margin: 0 !important;
                border-collapse: collapse !important;
                border-spacing: 0 !important;
                background: #fff !important;
                box-shadow: none !important;
            }
            .mobile-table th,
            .mobile-table td {
                box-shadow: none !important;
            }
            .mobile-table th {
                background-image: linear-gradient(180deg, rgba(235,242,251,0.98), rgba(217,228,243,0.95));
            }
            .mobile-table td {
                background-image: linear-gradient(180deg, rgba(255,255,255,0.995), rgba(248,250,252,0.985));
            }

            /* 메모 그룹 */
            .step68-memo-groups {
                width: min(450px, 100%);
            }
            .step68-memo-section {
                margin: 0 0 6px 0;
            }
            .step68-memo-summary {
                padding: 7px 6px 6px 6px;
                font-size: 13px;
                font-weight: 800;
                line-height: 1.2;
                cursor: pointer;
                user-select: none;
                border-bottom: 1px solid rgba(191, 219, 254, 0.88);
                list-style: none;
                background: transparent;
            }
            .step68-memo-summary::-webkit-details-marker { display: none; }
            .step68-memo-summary.important { color: #ef4444; }
            .step68-memo-summary.general { color: #0f172a; }
            .step68-memo-summary.done { color: #94a3b8; }
            .step68-memo-body {
                border-bottom: 1px solid rgba(191, 219, 254, 0.72);
            }
            .step68-memo-row {
                padding: 7px 6px !important;
                border-bottom: 1px solid rgba(191, 219, 254, 0.75) !important;
                min-height: 34px;
                word-break: keep-all;
                overflow-wrap: anywhere;
            }
            .step68-memo-row:last-child {
                border-bottom: 0 !important;
            }
            .step68-memo-row.done,
            .step68-memo-row.done * {
                text-decoration: line-through !important;
                text-decoration-thickness: 1.15px !important;
                text-decoration-skip-ink: auto;
                color: #9aa7b6 !important;
            }
            /* [STEP68_WEB_CSS_END] */
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass


def step68_postprocess_component():
    try:
        import streamlit.components.v1 as components

        info = step68_current_period_info()
        current_key = str(info.get("key", "") or "")
        clock = str(info.get("clock", "--:--") or "--:--")
        period = str(info.get("period", "") or "")
        range_text = str(info.get("range", "") or "")
        detail = period + ((" " + range_text) if range_text else "")

        components.html(
            f"""
            <script>
            (function() {{
                const CURRENT_KEY = {current_key!r};
                const CLOCK = {clock!r};
                const DETAIL = {detail!r};

                function rootDoc() {{
                    try {{ return window.parent.document; }} catch(e) {{ return document; }}
                }}
                function visible(el) {{
                    if (!el) return false;
                    const r = el.getBoundingClientRect();
                    return r.width > 1 && r.height > 1;
                }}
                function isStreamlitBlock(el) {{
                    return !!(el && el.matches && (el.matches('[data-testid="stVerticalBlock"]') || el.matches('[data-testid="element-container"]') || el.matches('.element-container')));
                }}

                function patchToolbarLabels(doc) {{
                    for (const b of Array.from(doc.querySelectorAll('button'))) {{
                        const txt = (b.innerText || '').trim().replace(/\s+/g, '');
                        if (['☀️','☀','🌞','🔆'].includes(txt)) b.innerText = '조회';
                        if (['🌙','🌛','🌜','🌕'].includes(txt)) b.innerText = '8·9';
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

                function placeClockNextToTitle(doc) {{
                    const titleEl = findTitleEl(doc);
                    if (!titleEl || !titleEl.parentNode) return;

                    let row = doc.querySelector('.step68-title-row');
                    if (!row) {{
                        row = doc.createElement('div');
                        row.className = 'step68-title-row';
                        const titleHost = doc.createElement('div');
                        titleHost.className = 'step68-title-host';
                        const clockHost = doc.createElement('div');
                        clockHost.className = 'step68-clock-host';
                        titleEl.parentNode.insertBefore(row, titleEl);
                        row.appendChild(titleHost);
                        row.appendChild(clockHost);
                        titleHost.appendChild(titleEl);
                    }}

                    let clockHost = row.querySelector('.step68-clock-host');
                    if (!clockHost) {{
                        clockHost = doc.createElement('div');
                        clockHost.className = 'step68-clock-host';
                        row.appendChild(clockHost);
                    }}

                    let pill = row.querySelector('.step68-clock-pill');
                    if (!pill) {{
                        pill = doc.createElement('span');
                        pill.className = 'step68-clock-pill';
                        pill.innerHTML = '<span class="step68-clock-time"></span><span class="step68-clock-state"></span>';
                        clockHost.appendChild(pill);
                    }}
                    const timeEl = pill.querySelector('.step68-clock-time');
                    const stateEl = pill.querySelector('.step68-clock-state');
                    if (timeEl) timeEl.textContent = CLOCK;
                    if (stateEl) stateEl.textContent = DETAIL || '';
                }}

                function findTimetable(doc) {{
                    return Array.from(doc.querySelectorAll('table')).find(t => {{
                        const txt = t.innerText || '';
                        return txt.includes('교시') && txt.includes('학사일정');
                    }}) || null;
                }}

                function wrapTimetable(doc) {{
                    const table = findTimetable(doc);
                    if (!table) return;
                    table.classList.add('mobile-table');

                    const existingShadow = doc.querySelector('.timetable-bottom-shadow');
                    if (existingShadow) existingShadow.remove();

                    let card = table.closest('.step68-table-card');
                    if (card) return;

                    // 기존 wrapper 정리 후 step68 wrapper로 교체
                    let oldFrame = table.closest('.timetable-frame');
                    let oldScroll = table.closest('.timetable-scroll');
                    const parent = (oldFrame && oldFrame.parentNode) ? oldFrame.parentNode : table.parentNode;
                    if (!parent) return;

                    const cardEl = doc.createElement('div');
                    cardEl.className = 'step68-table-card';
                    const scrollEl = doc.createElement('div');
                    scrollEl.className = 'step68-table-scroll';

                    if (oldFrame && oldFrame.parentNode) {{
                        oldFrame.parentNode.insertBefore(cardEl, oldFrame);
                        scrollEl.appendChild(table);
                        cardEl.appendChild(scrollEl);
                        oldFrame.remove();
                    }} else if (oldScroll && oldScroll.parentNode) {{
                        oldScroll.parentNode.insertBefore(cardEl, oldScroll);
                        scrollEl.appendChild(table);
                        cardEl.appendChild(scrollEl);
                        oldScroll.remove();
                    }} else {{
                        parent.insertBefore(cardEl, table);
                        scrollEl.appendChild(table);
                        cardEl.appendChild(scrollEl);
                    }}
                }}

                function markCurrentRow(doc) {{
                    if (!CURRENT_KEY) return;
                    const table = findTimetable(doc);
                    if (!table) return;
                    for (const row of Array.from(table.querySelectorAll('tr'))) {{
                        const txt = row.innerText || '';
                        let hit = false;
                        if (CURRENT_KEY === 'lunch') hit = txt.includes('점심');
                        else hit = txt.includes(CURRENT_KEY + '교시') || txt.includes(CURRENT_KEY + ' 교시');
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

                function docOrder(all, node) {{
                    return all.indexOf(node);
                }}

                function nearestBlock(node) {{
                    let cur = node;
                    for (let i = 0; cur && i < 8; i++, cur = cur.parentElement) {{
                        if (isStreamlitBlock(cur)) return cur;
                    }}
                    return node;
                }}

                function stripRowNumber(el) {{
                    const re = /^\s*\d+\.\s*/;
                    const nodes = [el, ...Array.from(el.querySelectorAll('*'))];
                    for (const n of nodes) {{
                        for (const child of Array.from(n.childNodes || [])) {{
                            if (child.nodeType === 3 && re.test(child.textContent || '')) {{
                                child.textContent = (child.textContent || '').replace(re, '');
                            }}
                        }}
                    }}
                }}

                function rowClassFromText(text, row) {{
                    const t = (text || '').trim();
                    const joined = t.replace(/\s+/g, ' ');
                    if (/^(✔|✅|☑|✓)/.test(t) || /\s(✔|✅|☑|✓)\s?/.test(joined)) return 'done';

                    const nodes = [row, ...Array.from(row.querySelectorAll('*'))];
                    for (const n of nodes) {{
                        try {{
                            const s = getComputedStyle(n);
                            const deco = (s.textDecorationLine || '') + ' ' + (s.textDecoration || '') + ' ' + (n.style?.textDecoration || '');
                            if (deco.includes('line-through')) return 'done';
                        }} catch(e) {{}}
                    }}

                    if (/⭐|★/.test(joined)) return 'important';
                    return 'general';
                }}

                function findMemoTitle(doc) {{
                    return Array.from(doc.querySelectorAll('div,h1,h2,h3,p,span')).find(el => {{
                        if (!visible(el)) return false;
                        const txt = (el.innerText || '').trim();
                        return txt.includes('메모장');
                    }}) || null;
                }}

                function findMemoListContainer(doc, titleEl) {{
                    if (!titleEl) return null;
                    const allDivs = Array.from(doc.querySelectorAll('div'));
                    const titleIndex = docOrder(allDivs, titleEl.closest('div') || titleEl);
                    const dateRe = /(\d{2}\.\d{2}(?:\.\d{2})?)\s+\d{2}:\d{2}/;
                    const cands = allDivs.filter(el => {{
                        if (!visible(el)) return false;
                        const txt = (el.innerText || '').trim();
                        if (!txt || txt.includes('교시') || txt.includes('학사일정')) return false;
                        const idx = docOrder(allDivs, el);
                        if (idx <= titleIndex) return false;
                        const hits = (txt.match(new RegExp(dateRe, 'g')) || []).length;
                        const r = el.getBoundingClientRect();
                        return hits >= 3 && r.height >= 120;
                    }});
                    cands.sort((a,b) => a.getBoundingClientRect().height - b.getBoundingClientRect().height);
                    return cands[0] || null;
                }}

                function buildMemoGroups(doc) {{
                    const titleEl = findMemoTitle(doc);
                    if (!titleEl) return;
                    const list = findMemoListContainer(doc, titleEl);
                    if (!list) return;

                    const hostBlock = nearestBlock(list);
                    if (!hostBlock) return;

                    let groupedHost = hostBlock.previousElementSibling;
                    if (groupedHost && groupedHost.classList && groupedHost.classList.contains('step68-memo-groups')) {{
                        // 이미 그룹이 있으면 원본 상태를 다시 읽어 재생성
                        groupedHost.remove();
                    }}

                    const dateRe = /(\d{2}\.\d{2}(?:\.\d{2})?)\s+\d{2}:\d{2}/;
                    const candidates = [];
                    for (const el of Array.from(list.querySelectorAll('div,p,span'))) {{
                        if (!visible(el)) continue;
                        const txt = (el.innerText || '').trim();
                        if (dateRe.test(txt)) candidates.push(nearestBlock(el));
                    }}
                    const rows = [];
                    for (const c of candidates) if (c && !rows.includes(c) && c !== hostBlock) rows.push(c);
                    if (!rows.length) return;

                    const grouped = {{ important: [], general: [], done: [] }};
                    for (const row of rows) {{
                        const txt = (row.innerText || '').trim();
                        if (!dateRe.test(txt)) continue;
                        const clone = row.cloneNode(true);
                        clone.classList.add('step68-memo-row');
                        stripRowNumber(clone);
                        const cls = rowClassFromText(txt, row);
                        if (cls === 'done') clone.classList.add('done');
                        grouped[cls].push(clone);
                    }}

                    if (!grouped.important.length && !grouped.general.length && !grouped.done.length) return;

                    groupedHost = doc.createElement('div');
                    groupedHost.className = 'step68-memo-groups';

                    const defs = [
                        ['important', '📌 중요 메모'],
                        ['general', '▣ 일반 메모'],
                        ['done', '✔ 완료 메모'],
                    ];
                    for (const [key, label] of defs) {{
                        const arr = grouped[key] || [];
                        if (!arr.length) continue;
                        const details = doc.createElement('details');
                        details.className = 'step68-memo-section';
                        details.open = true;
                        const summary = doc.createElement('summary');
                        summary.className = 'step68-memo-summary ' + key;
                        summary.textContent = label + ' (' + arr.length + ')';
                        const body = doc.createElement('div');
                        body.className = 'step68-memo-body';
                        for (const item of arr) body.appendChild(item);
                        details.appendChild(summary);
                        details.appendChild(body);
                        groupedHost.appendChild(details);
                    }}

                    hostBlock.parentNode.insertBefore(groupedHost, hostBlock);
                    hostBlock.style.display = 'none';
                }}

                function runOnce() {{
                    const doc = rootDoc();
                    patchToolbarLabels(doc);
                    placeClockNextToTitle(doc);
                    wrapTimetable(doc);
                    markCurrentRow(doc);
                    buildMemoGroups(doc);
                }}

                let raf = null;
                function scheduleRun() {{
                    if (raf) cancelAnimationFrame(raf);
                    raf = requestAnimationFrame(() => {{
                        try {{ runOnce(); }} catch(e) {{ console.log('step68 run error', e); }}
                    }});
                }}

                scheduleRun();
                setTimeout(scheduleRun, 200);
                setTimeout(scheduleRun, 700);
                setTimeout(scheduleRun, 1400);
                setTimeout(scheduleRun, 2500);

                try {{
                    const obs = new MutationObserver(() => scheduleRun());
                    obs.observe(rootDoc().body, {{ childList: true, subtree: true }});
                    setTimeout(() => obs.disconnect(), 10000);
                }} catch(e) {{}}
            }})();
            </script>
            """,
            height=1,
            width=1,
        )
    except Exception:
        pass
# [STEP68_WEB_HELPERS_END]
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step68_web_clock_memo_table_cleanup_{STAMP}{path.suffix}")
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
        "step68_inject_css()",
        "step68_postprocess_component()",
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
        "# [STEP68_WEB_CALL_START]",
        "step68_inject_css()",
        "# [STEP68_WEB_CALL_END]",
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
        "# [STEP68_WEB_POSTPROCESS_START]",
        "step68_postprocess_component()",
        "# [STEP68_WEB_POSTPROCESS_END]",
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
    print("Step68 web clock/memo/table cleanup")
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
        print("[완료] Step68 패치 저장")
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
    print("실행:")
    print("python tools\\step68_web_clock_memo_table_cleanup.py")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 제목 오른쪽에 현재시각 배지가 다시 생기는지")
    print("2. 중요/일반/완료 메모 소분류와 접힘/펼침이 생기는지")
    print("3. 완료 메모가 일반 메모와 분리되는지")
    print("4. 시간표 카드 외곽이 더 깔끔한 카드형으로 바뀌는지")
    print("5. 현재 교시 강조가 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

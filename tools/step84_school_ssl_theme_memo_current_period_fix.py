# tools/step84_school_ssl_theme_memo_current_period_fix.py
# ------------------------------------------------------------
# Step84: 학교 경로용 SSL/테마/메모색상/현재교시 보정
#
# 수정:
# 1) 학교망 SSL 검사로 Supabase 요청 실패 시 verify=False로 Supabase 요청만 1회 재시도
# 2) 메모 literal <span style="color:#...">...</span> 실제 색상 표시
# 3) 달력 버튼 중앙 overlay 방식 강화
# 4) 테마별 상단 버튼/시간표 색상 대비 DOM 보정
# 5) 현재 시각 기준 요일/교시/해당 칸 표시, 15분 이내 다음 수업은 '시작 전' 표시
# 6) 러블리 핑크 테마 추가 재시도
#
# 학교 경로:
# Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(r"Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next")
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

SSL_BLOCK = '\n# [STEP84_SUPABASE_SSL_FALLBACK_START]\n# 학교/기관망 SSL 검사로 Supabase HTTPS 인증서 검증이 실패하는 경우만 재시도합니다.\ntry:\n    import requests as _step84_requests\n    try:\n        import urllib3 as _step84_urllib3\n        _step84_urllib3.disable_warnings(_step84_urllib3.exceptions.InsecureRequestWarning)\n    except Exception:\n        pass\n\n    if not getattr(_step84_requests.sessions.Session.request, "_step84_ssl_fallback", False):\n        _step84_original_request = _step84_requests.sessions.Session.request\n\n        def _step84_request_with_ssl_fallback(self, method, url, **kwargs):\n            try:\n                return _step84_original_request(self, method, url, **kwargs)\n            except _step84_requests.exceptions.SSLError:\n                url_text = str(url)\n                if "supabase.co" in url_text:\n                    kwargs["verify"] = False\n                    return _step84_original_request(self, method, url, **kwargs)\n                raise\n\n        _step84_request_with_ssl_fallback._step84_ssl_fallback = True\n        _step84_requests.sessions.Session.request = _step84_request_with_ssl_fallback\nexcept Exception:\n    pass\n# [STEP84_SUPABASE_SSL_FALLBACK_END]\n'
DOM_BLOCK = '\n# [STEP84_WEB_SAFE_DOM_REFINEMENT_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            const STYLE_ID = \'step84-safe-dom-style\';\n\n            const PALETTES = {\n                light: {\n                    tableWrap:\'#dbe8f7\', th1:\'#eaf3ff\', th2:\'#d7e6f8\', td1:\'#ffffff\', td2:\'#fafcff\', line:\'#1f2937\', text:\'#0f172a\',\n                    calBg:\'#f5f0ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#2563eb\', memoText:\'#ffffff\',\n                    searchBg:\'#fff4dd\', searchText:\'#8a4b00\', searchBorder:\'#f2cf96\',\n                    eightBg:\'#eef2ff\', eightText:\'#1e40af\', eightBorder:\'#c7d2fe\',\n                    activeBg:\'#dbeafe\', activeBorder:\'#2563eb\', activeText:\'#0f172a\', soonBg:\'#fff7ed\', soonBorder:\'#f97316\'\n                },\n                dark: {\n                    tableWrap:\'#253145\', th1:\'#334155\', th2:\'#243041\', td1:\'#111827\', td2:\'#172033\', line:\'#cbd5e1\', text:\'#f8fafc\',\n                    calBg:\'#ede9fe\', calText:\'#4c1d95\', calBorder:\'#c4b5fd\',\n                    memoBg:\'#e11d48\', memoText:\'#ffffff\',\n                    searchBg:\'#f97316\', searchText:\'#ffffff\', searchBorder:\'#ea580c\',\n                    eightBg:\'#dbeafe\', eightText:\'#1e3a8a\', eightBorder:\'#93c5fd\',\n                    activeBg:\'#1e3a8a\', activeBorder:\'#60a5fa\', activeText:\'#f8fafc\', soonBg:\'#7c2d12\', soonBorder:\'#fdba74\'\n                },\n                green: {\n                    tableWrap:\'#cfe7dc\', th1:\'#dcfce7\', th2:\'#bbf7d0\', td1:\'#ffffff\', td2:\'#f0fdf4\', line:\'#14532d\', text:\'#052e16\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#ea580c\', memoText:\'#ffffff\',\n                    searchBg:\'#f97316\', searchText:\'#ffffff\', searchBorder:\'#ea580c\',\n                    eightBg:\'#d9f99d\', eightText:\'#365314\', eightBorder:\'#a3e635\',\n                    activeBg:\'#bbf7d0\', activeBorder:\'#16a34a\', activeText:\'#052e16\', soonBg:\'#fef3c7\', soonBorder:\'#d97706\'\n                },\n                orange: {\n                    tableWrap:\'#fde7c8\', th1:\'#ffedd5\', th2:\'#fed7aa\', td1:\'#fffaf5\', td2:\'#fff7ed\', line:\'#7c2d12\', text:\'#431407\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#c2410c\', memoText:\'#ffffff\',\n                    searchBg:\'#ea580c\', searchText:\'#ffffff\', searchBorder:\'#c2410c\',\n                    eightBg:\'#ffedd5\', eightText:\'#7c2d12\', eightBorder:\'#fdba74\',\n                    activeBg:\'#fed7aa\', activeBorder:\'#ea580c\', activeText:\'#431407\', soonBg:\'#fef3c7\', soonBorder:\'#d97706\'\n                },\n                pink: {\n                    tableWrap:\'#ffe1ec\', th1:\'#ffe6ef\', th2:\'#ffd3e2\', td1:\'#fffefe\', td2:\'#fff7fb\', line:\'#7f1d43\', text:\'#4a1d2f\',\n                    calBg:\'#fff1f7\', calText:\'#be185d\', calBorder:\'#f9a8d4\',\n                    memoBg:\'#ec4899\', memoText:\'#ffffff\',\n                    searchBg:\'#fff1e6\', searchText:\'#9a3412\', searchBorder:\'#fdba74\',\n                    eightBg:\'#fdf2f8\', eightText:\'#9d174d\', eightBorder:\'#fbcfe8\',\n                    activeBg:\'#fbcfe8\', activeBorder:\'#ec4899\', activeText:\'#4a1d2f\', soonBg:\'#fff1e6\', soonBorder:\'#fb923c\'\n                },\n                blue: {\n                    tableWrap:\'#dbeafe\', th1:\'#e0f2fe\', th2:\'#bae6fd\', td1:\'#ffffff\', td2:\'#f8fbff\', line:\'#1e3a8a\', text:\'#0f172a\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#2563eb\', memoText:\'#ffffff\',\n                    searchBg:\'#fff7ed\', searchText:\'#9a3412\', searchBorder:\'#fed7aa\',\n                    eightBg:\'#e0f2fe\', eightText:\'#075985\', eightBorder:\'#7dd3fc\',\n                    activeBg:\'#bfdbfe\', activeBorder:\'#2563eb\', activeText:\'#0f172a\', soonBg:\'#fef3c7\', soonBorder:\'#d97706\'\n                }\n            };\n\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const s = window.getComputedStyle(el);\n                if (s.display === \'none\' || s.visibility === \'hidden\') return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function textOf(el) {\n                return ((el && (el.innerText || el.textContent)) || \'\').replace(/\\s+/g, \' \').trim();\n            }\n\n            function parseRgb(value) {\n                const m = (value || \'\').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);\n                if (!m) return null;\n                return { r:+m[1], g:+m[2], b:+m[3] };\n            }\n\n            function luminance(c) {\n                if (!c) return 255;\n                return 0.299*c.r + 0.587*c.g + 0.114*c.b;\n            }\n\n            function toolbar(doc) {\n                const bars = Array.from(doc.querySelectorAll(\'div[data-testid="stHorizontalBlock"]\')).filter(visible);\n                return bars.find(b => {\n                    const t = textOf(b);\n                    return t.includes(\'오늘\') && t.includes(\'달력\') && t.includes(\'메모\');\n                }) || null;\n            }\n\n            function tableEl(doc) {\n                return Array.from(doc.querySelectorAll(\'table\')).find(t => {\n                    const x = textOf(t);\n                    return x.includes(\'교시\') && (x.includes(\'월\') || x.includes(\'화\')) && x.includes(\'학사일정\');\n                }) || null;\n            }\n\n            function paletteKey(doc) {\n                const bodyText = doc.body ? (doc.body.innerText || \'\') : \'\';\n                if (bodyText.includes(\'러블리 핑크\')) return \'pink\';\n\n                const bar = toolbar(doc);\n                const bg = parseRgb(bar ? getComputedStyle(bar).backgroundColor : getComputedStyle(doc.body).backgroundColor);\n                if (bg) {\n                    if (luminance(bg) < 95) return \'dark\';\n                    if (bg.g > bg.r + 20 && bg.g >= bg.b) return \'green\';\n                    if (bg.r > 210 && bg.g > 145 && bg.b < 125) return \'orange\';\n                    if (bg.b > bg.r + 10 && bg.b > bg.g - 5) return \'blue\';\n                    if (bg.r > 230 && bg.b > 210 && bg.g < 225) return \'pink\';\n                }\n\n                const lower = bodyText.toLowerCase();\n                if (lower.includes(\'dark\') || bodyText.includes(\'다크\') || bodyText.includes(\'블랙\') || bodyText.includes(\'야간\')) return \'dark\';\n                if (bodyText.includes(\'그린\') || bodyText.includes(\'초록\') || bodyText.includes(\'숲\')) return \'green\';\n                if (bodyText.includes(\'오렌지\') || bodyText.includes(\'주황\')) return \'orange\';\n                if (bodyText.includes(\'블루\') || bodyText.includes(\'파랑\') || bodyText.includes(\'윈도우\')) return \'blue\';\n                return \'light\';\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(STYLE_ID)) return;\n                const style = doc.createElement(\'style\');\n                style.id = STYLE_ID;\n                style.textContent = `\n                    body.step84-theme table.mobile-table {\n                        color: var(--s84-text) !important;\n                        border-color: var(--s84-line) !important;\n                    }\n                    body.step84-theme table.mobile-table th {\n                        background-image: linear-gradient(180deg, var(--s84-th1), var(--s84-th2)) !important;\n                        color: var(--s84-text) !important;\n                        border-color: var(--s84-line) !important;\n                    }\n                    body.step84-theme table.mobile-table td {\n                        background-image: linear-gradient(180deg, var(--s84-td1), var(--s84-td2)) !important;\n                        color: var(--s84-text) !important;\n                        border-color: var(--s84-line) !important;\n                    }\n                    body.step84-theme div:has(> table.mobile-table) {\n                        background: var(--s84-table-wrap) !important;\n                    }\n\n                    .s84-btn-calendar, .s84-btn-memo, .s84-btn-search, .s84-btn-89 {\n                        box-sizing: border-box !important;\n                        min-height: 40px !important;\n                        height: 40px !important;\n                        border-radius: 7px !important;\n                        font-weight: 800 !important;\n                        text-align: center !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                    }\n                    .s84-btn-calendar *, .s84-btn-memo *, .s84-btn-search *, .s84-btn-89 * {\n                        color: inherit !important;\n                        -webkit-text-fill-color: currentColor !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        text-align: center !important;\n                    }\n                    .s84-btn-calendar {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        flex: 0 0 58px !important;\n                        background: var(--s84-cal-bg) !important;\n                        border: 1px solid var(--s84-cal-border) !important;\n                        color: var(--s84-cal-text) !important;\n                        padding: 0 !important;\n                        position: relative !important;\n                        overflow: hidden !important;\n                    }\n                    .s84-btn-memo {\n                        background: var(--s84-memo-bg) !important;\n                        border: 1px solid var(--s84-memo-bg) !important;\n                        color: var(--s84-memo-text) !important;\n                    }\n                    .s84-btn-search {\n                        background: var(--s84-search-bg) !important;\n                        border: 1px solid var(--s84-search-border) !important;\n                        color: var(--s84-search-text) !important;\n                    }\n                    .s84-btn-89 {\n                        background: var(--s84-eight-bg) !important;\n                        border: 1px solid var(--s84-eight-border) !important;\n                        color: var(--s84-eight-text) !important;\n                    }\n\n                    .s84-calendar-shell {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        flex: 0 0 58px !important;\n                        position: relative !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding: 0 !important;\n                        box-sizing: border-box !important;\n                    }\n                    .s84-calendar-shell > * {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                    }\n                    .s84-calendar-shell [data-baseweb="select"], .s84-calendar-shell [role="button"], .s84-calendar-shell button {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        grid-template-columns: 1fr !important;\n                        padding-left: 0 !important;\n                        padding-right: 0 !important;\n                        color: transparent !important;\n                        -webkit-text-fill-color: transparent !important;\n                    }\n                    .s84-calendar-shell [data-baseweb="select"] *, .s84-calendar-shell [role="button"] *, .s84-calendar-shell button * {\n                        color: transparent !important;\n                        -webkit-text-fill-color: transparent !important;\n                    }\n                    .s84-calendar-shell svg, .s84-calendar-shell [aria-hidden="true"], .s84-remove {\n                        display: none !important;\n                        width: 0 !important;\n                        min-width: 0 !important;\n                        max-width: 0 !important;\n                        flex: 0 0 0 !important;\n                        margin: 0 !important;\n                        padding: 0 !important;\n                    }\n                    .s84-calendar-overlay {\n                        position: absolute !important;\n                        inset: 0 !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        pointer-events: none !important;\n                        color: var(--s84-cal-text) !important;\n                        -webkit-text-fill-color: var(--s84-cal-text) !important;\n                        font-size: 14px !important;\n                        font-weight: 800 !important;\n                        line-height: 1 !important;\n                        text-align: center !important;\n                        z-index: 3 !important;\n                    }\n\n                    table.mobile-table .s84-current-col {\n                        box-shadow: inset 0 3px 0 var(--s84-active-border) !important;\n                    }\n                    table.mobile-table .s84-current-rowhead,\n                    table.mobile-table .s84-current-cell {\n                        background-image: linear-gradient(180deg, var(--s84-active-bg), var(--s84-active-bg)) !important;\n                        color: var(--s84-active-text) !important;\n                        outline: 2px solid var(--s84-active-border) !important;\n                        outline-offset: -2px !important;\n                    }\n                    table.mobile-table .s84-soon-cell,\n                    table.mobile-table .s84-soon-rowhead {\n                        background-image: linear-gradient(180deg, var(--s84-soon-bg), var(--s84-soon-bg)) !important;\n                        outline: 2px dashed var(--s84-soon-border) !important;\n                        outline-offset: -2px !important;\n                    }\n                    .s84-period-badge {\n                        display: inline-block !important;\n                        margin-top: 3px !important;\n                        padding: 1px 5px !important;\n                        border-radius: 999px !important;\n                        font-size: 10px !important;\n                        font-weight: 900 !important;\n                        background: var(--s84-active-border) !important;\n                        color: #fff !important;\n                        line-height: 1.2 !important;\n                    }\n                    .s84-period-badge.soon {\n                        background: var(--s84-soon-border) !important;\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function applyVars(doc) {\n                const key = paletteKey(doc);\n                const p = PALETTES[key] || PALETTES.light;\n                doc.body.classList.add(\'step84-theme\');\n                const vars = {\n                    \'--s84-table-wrap\': p.tableWrap, \'--s84-th1\': p.th1, \'--s84-th2\': p.th2, \'--s84-td1\': p.td1, \'--s84-td2\': p.td2,\n                    \'--s84-line\': p.line, \'--s84-text\': p.text,\n                    \'--s84-cal-bg\': p.calBg, \'--s84-cal-text\': p.calText, \'--s84-cal-border\': p.calBorder,\n                    \'--s84-memo-bg\': p.memoBg, \'--s84-memo-text\': p.memoText,\n                    \'--s84-search-bg\': p.searchBg, \'--s84-search-text\': p.searchText, \'--s84-search-border\': p.searchBorder,\n                    \'--s84-eight-bg\': p.eightBg, \'--s84-eight-text\': p.eightText, \'--s84-eight-border\': p.eightBorder,\n                    \'--s84-active-bg\': p.activeBg, \'--s84-active-border\': p.activeBorder, \'--s84-active-text\': p.activeText,\n                    \'--s84-soon-bg\': p.soonBg, \'--s84-soon-border\': p.soonBorder\n                };\n                for (const [k, v] of Object.entries(vars)) doc.body.style.setProperty(k, v);\n            }\n\n            function classify(child) {\n                const t = textOf(child);\n                if (t.includes(\'달력\')) return \'calendar\';\n                if (t.includes(\'메모\')) return \'memo\';\n                if (t.includes(\'조회\')) return \'search\';\n                if (t.includes(\'8·9\') || t.includes(\'8-9\') || t === \'89\' || t.includes(\'89\')) return \'89\';\n                return \'\';\n            }\n\n            function target(child) {\n                return child.querySelector(\'button,[role="button"],div[data-baseweb="select"]\') || child;\n            }\n\n            function calendar(child, doc) {\n                child.classList.add(\'s84-calendar-shell\');\n                const btn = target(child);\n                btn.classList.add(\'s84-btn-calendar\');\n\n                const removable = [];\n                for (const svg of Array.from(child.querySelectorAll(\'svg\'))) removable.push(svg);\n                for (const el of Array.from(child.querySelectorAll(\'span,div,p\'))) {\n                    const t = (el.textContent || \'\').trim();\n                    if (/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test(t)) removable.push(el);\n                }\n                for (const el of removable) {\n                    try { el.remove(); }\n                    catch(e) {\n                        el.classList.add(\'s84-remove\');\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                    }\n                }\n\n                let overlay = child.querySelector(\'.s84-calendar-overlay\');\n                if (!overlay) {\n                    overlay = doc.createElement(\'span\');\n                    overlay.className = \'s84-calendar-overlay\';\n                    overlay.textContent = \'달력\';\n                    child.appendChild(overlay);\n                } else {\n                    overlay.textContent = \'달력\';\n                }\n            }\n\n            function buttons(doc) {\n                const bar = toolbar(doc);\n                if (!bar) return;\n                for (const child of Array.from(bar.children || [])) {\n                    const kind = classify(child);\n                    const btn = target(child);\n                    if (kind === \'calendar\') calendar(child, doc);\n                    else if (kind === \'memo\') btn.classList.add(\'s84-btn-memo\');\n                    else if (kind === \'search\') btn.classList.add(\'s84-btn-search\');\n                    else if (kind === \'89\') btn.classList.add(\'s84-btn-89\');\n                }\n            }\n\n            function parseMemoColor(doc) {\n                const allowed = /<span\\s+style=["\']\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*["\']>(.*?)<\\/span>/gis;\n\n                // text node 기반\n                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);\n                const nodes = [];\n                let node;\n                while ((node = walker.nextNode())) {\n                    const v = node.nodeValue || \'\';\n                    allowed.lastIndex = 0;\n                    if (v.includes(\'<span\') && allowed.test(v)) nodes.push(node);\n                }\n                for (const textNode of nodes) {\n                    const text = textNode.nodeValue || \'\';\n                    const frag = doc.createDocumentFragment();\n                    let last = 0;\n                    allowed.lastIndex = 0;\n                    let m;\n                    while ((m = allowed.exec(text))) {\n                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));\n                        const span = doc.createElement(\'span\');\n                        span.style.setProperty(m[1].toLowerCase(), m[2]);\n                        span.textContent = m[3];\n                        frag.appendChild(span);\n                        last = allowed.lastIndex;\n                    }\n                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));\n                    if (textNode.parentNode) textNode.parentNode.replaceChild(frag, textNode);\n                }\n\n                // innerHTML entity 기반 보조\n                const entityRe = /&lt;span\\s+style=(?:&quot;|")\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*(?:&quot;|")&gt;([\\s\\S]*?)&lt;\\/span&gt;/gi;\n                for (const el of Array.from(doc.querySelectorAll(\'div,p,span\'))) {\n                    if (!el.innerHTML || !el.innerHTML.includes(\'&lt;span\')) continue;\n                    el.innerHTML = el.innerHTML.replace(entityRe, function(_, prop, color, content) {\n                        return \'<span style="\' + prop + \':\' + color + \'">\' + content + \'</span>\';\n                    });\n                }\n            }\n\n            function parseMinutes(timeText) {\n                const m = String(timeText || \'\').match(/(\\d{1,2}):(\\d{2})/);\n                if (!m) return null;\n                return parseInt(m[1], 10) * 60 + parseInt(m[2], 10);\n            }\n\n            function rowRange(row) {\n                const first = row.children && row.children.length ? row.children[0] : null;\n                if (!first) return null;\n                const times = (first.innerText || \'\').match(/\\d{1,2}:\\d{2}/g);\n                if (!times || times.length < 2) return null;\n                return {\n                    start: parseMinutes(times[0]),\n                    end: parseMinutes(times[1])\n                };\n            }\n\n            function todayColumnIndex(table) {\n                const d = new Date().getDay(); // Sun 0, Mon 1\n                if (d < 1 || d > 5) return -1;\n                return d; // first column is 교시, Mon is 1\n            }\n\n            function highlightCurrentPeriod(doc) {\n                const table = tableEl(doc);\n                if (!table) return;\n\n                for (const el of Array.from(table.querySelectorAll(\'.s84-current-col,.s84-current-rowhead,.s84-current-cell,.s84-soon-cell,.s84-soon-rowhead\'))) {\n                    el.classList.remove(\'s84-current-col\',\'s84-current-rowhead\',\'s84-current-cell\',\'s84-soon-cell\',\'s84-soon-rowhead\');\n                }\n                for (const b of Array.from(table.querySelectorAll(\'.s84-period-badge\'))) b.remove();\n\n                const col = todayColumnIndex(table);\n                const rows = Array.from(table.querySelectorAll(\'tr\'));\n                if (col < 1 || !rows.length) return;\n\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n\n                let targetRow = null;\n                let mode = \'current\';\n\n                for (const row of rows) {\n                    const r = rowRange(row);\n                    if (!r) continue;\n                    if (r.start <= mins && mins < r.end) {\n                        targetRow = row;\n                        mode = \'current\';\n                        break;\n                    }\n                }\n\n                if (!targetRow) {\n                    let nearest = null;\n                    for (const row of rows) {\n                        const r = rowRange(row);\n                        if (!r) continue;\n                        const diff = r.start - mins;\n                        if (diff > 0 && diff <= 15 && (!nearest || diff < nearest.diff)) {\n                            nearest = { row, diff };\n                        }\n                    }\n                    if (nearest) {\n                        targetRow = nearest.row;\n                        mode = \'soon\';\n                    }\n                }\n\n                const headerRow = rows[0];\n                if (headerRow && headerRow.children[col]) {\n                    headerRow.children[col].classList.add(\'s84-current-col\');\n                }\n\n                if (!targetRow) return;\n\n                const rowHead = targetRow.children[0];\n                const cell = targetRow.children[col];\n                if (mode === \'current\') {\n                    if (rowHead) rowHead.classList.add(\'s84-current-rowhead\');\n                    if (cell) cell.classList.add(\'s84-current-cell\');\n                } else {\n                    if (rowHead) rowHead.classList.add(\'s84-soon-rowhead\');\n                    if (cell) cell.classList.add(\'s84-soon-cell\');\n                }\n\n                if (rowHead) {\n                    const badge = doc.createElement(\'span\');\n                    badge.className = \'s84-period-badge\' + (mode === \'soon\' ? \' soon\' : \'\');\n                    badge.textContent = mode === \'soon\' ? \'시작 전\' : \'진행 중\';\n                    rowHead.appendChild(doc.createElement(\'br\'));\n                    rowHead.appendChild(badge);\n                }\n            }\n\n            function run() {\n                const doc = docRoot();\n                injectStyle(doc);\n                applyVars(doc);\n                buttons(doc);\n                parseMemoColor(doc);\n                highlightCurrentPeriod(doc);\n            }\n\n            run();\n            setTimeout(run, 150);\n            setTimeout(run, 500);\n            setTimeout(run, 1200);\n            setTimeout(run, 2500);\n            setInterval(run, 3000);\n        })();\n        </script>\n        """,\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n# [STEP84_WEB_SAFE_DOM_REFINEMENT_END]\n'
LOVELY_PINK_THEME = '\n    "러블리 핑크": {\n        "bg": "#fff5f8",\n        "card": "#ffffff",\n        "text": "#4a1d2f",\n        "muted": "#9f647a",\n        "primary": "#ec4899",\n        "primary_dark": "#db2777",\n        "accent": "#f9a8d4",\n        "header_bg": "#ffe6ef",\n        "header_bg2": "#ffd3e2",\n        "cell_bg": "#fffafe",\n        "cell_bg2": "#fff7fb",\n        "border": "#f3bfd2",\n        "shadow": "rgba(236, 72, 153, 0.14)",\n    },\n'

REMOVE_MARKERS = [
    ("# [STEP84_SUPABASE_SSL_FALLBACK_START]", "# [STEP84_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_START]", "# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_END]"),
    ("# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_START]", "# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_END]"),
    ("# [STEP84_WEB_SAFE_DOM_REFINEMENT_START]", "# [STEP84_WEB_SAFE_DOM_REFINEMENT_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step84_school_ssl_theme_{STAMP}{APP.suffix}")
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


def insert_ssl_block(text: str):
    if "# [STEP84_SUPABASE_SSL_FALLBACK_START]" in text:
        return text, "already_exists"

    lines = text.splitlines()
    insert_at = 0

    # import 구간 바로 뒤에 삽입
    last_import = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            last_import = i
        elif last_import >= 0 and s and not s.startswith("#"):
            break

    insert_at = last_import + 1 if last_import >= 0 else 0
    lines[insert_at:insert_at] = SSL_BLOCK.strip("\n").splitlines()
    return "\n".join(lines) + "\n", f"inserted_at_line_{insert_at+1}"


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

    text = text[:end] + LOVELY_PINK_THEME.rstrip() + "\n" + text[end:]
    return text, "theme_dict_added"


def add_lovely_pink_to_options(text: str):
    if "러블리 핑크" in text:
        return text, 0

    changed = 0
    patterns = [
        r"(theme_options\s*=\s*\[[^\]]*)\]",
        r"(themes_list\s*=\s*\[[^\]]*)\]",
        r"(theme_names\s*=\s*\[[^\]]*)\]",
    ]

    for pat in patterns:
        def repl(m):
            nonlocal changed
            changed += 1
            return m.group(1).rstrip() + ', "러블리 핑크"]'

        text2, n = re.subn(pat, repl, text, count=1, flags=re.S)
        if n:
            return text2, changed

    pat = r"(st\.selectbox\([^\n]{0,200}(?:테마|theme)[\s\S]{0,500}?\[[^\]]*)\]"

    def repl2(m):
        nonlocal changed
        changed += 1
        return m.group(1).rstrip() + ', "러블리 핑크"]'

    text2, n = re.subn(pat, repl2, text, count=1)
    return text2, changed


def main():
    print("====================================================")
    print("Step84 school SSL/theme/memo/current period fix")
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
        print("먼저 정상 실행되는 상태로 복구한 뒤 다시 실행해주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        text, removed = remove_old_blocks(text)
        text, ssl_status = insert_ssl_block(text)
        text, theme_dict_status = add_lovely_pink_to_theme_dict(text)
        text, option_changes = add_lovely_pink_to_options(text)
        text = text.rstrip() + "\n\n" + DOM_BLOCK.strip("\n") + "\n"
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
    print("[완료] Step84 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step82/83/84 블록 제거: {removed}")
    print(f"- Supabase SSL fallback: {ssl_status}")
    print(f"- 러블리 핑크 테마 dict 처리: {theme_dict_status}")
    print(f"- 러블리 핑크 옵션 처리: {option_changes}")
    print("- 메모 색상 span 표시 보정")
    print("- 테마별 버튼/시간표 색상 보정")
    print("- 현재 시각 기준 요일/교시/칸 표시 추가")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 테마 변경 시 SSL 에러가 사라지는지")
    print("2. 메모 색상 코드가 실제 색상으로 표시되는지")
    print("3. 달력 글자가 중앙에 오는지")
    print("4. 러블리 핑크 테마가 목록에 있는지")
    print("5. 현재 시각 기준 요일/교시/칸 표시가 되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

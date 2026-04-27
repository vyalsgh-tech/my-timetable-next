# tools/step88_school_restore_before87_single_stable_fix.py
# ------------------------------------------------------------
# Step88: Step87 직전 상태로 복원 후, DOM 보정 1개만 적용
#
# 목적:
# - Step87 적용 후 상단 버튼이 세로로 깨진 상태를 되돌림
# - 기존 Step78~87 DOM 블록을 모두 제거
# - 새 DOM 블록 1개만 삽입
# - 초 단위로 버튼/표 DOM을 계속 만지지 않음
#
# 처리:
# 1) app_before_step87_stop_scroll_jump_*.py 백업을 우선 복구
# 2) Step78~88 DOM 블록 전체 제거
# 3) SSL fallback은 1개만 재삽입
# 4) Step88 단일 DOM 블록 삽입
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

DOM_BLOCK = '\n# [STEP88_WEB_SINGLE_STABLE_DOM_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        r"""\n        <script>\n        (function() {\n            const STYLE_ID = \'step88-single-stable-style\';\n            const CLOCK_ID = \'step88-clock-fixed\';\n\n            const PALETTES = {\n                light: {\n                    tableWrap:\'#dbe8f7\', th1:\'#eaf3ff\', th2:\'#d7e6f8\', td1:\'#ffffff\', td2:\'#fafcff\', line:\'#1f2937\', text:\'#0f172a\',\n                    calBg:\'#f5f0ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#2563eb\', memoText:\'#ffffff\',\n                    searchBg:\'#fff4dd\', searchText:\'#8a4b00\', searchBorder:\'#f2cf96\',\n                    eightBg:\'#eef2ff\', eightText:\'#1e40af\', eightBorder:\'#c7d2fe\',\n                    activeBg:\'#dbeafe\', activeBorder:\'#2563eb\', activeText:\'#0f172a\', soonBg:\'#fff7ed\', soonBorder:\'#f97316\'\n                },\n                dark: {\n                    tableWrap:\'#253145\', th1:\'#334155\', th2:\'#243041\', td1:\'#111827\', td2:\'#172033\', line:\'#cbd5e1\', text:\'#f8fafc\',\n                    calBg:\'#ede9fe\', calText:\'#4c1d95\', calBorder:\'#c4b5fd\',\n                    memoBg:\'#e11d48\', memoText:\'#ffffff\',\n                    searchBg:\'#f97316\', searchText:\'#ffffff\', searchBorder:\'#ea580c\',\n                    eightBg:\'#dbeafe\', eightText:\'#1e3a8a\', eightBorder:\'#93c5fd\',\n                    activeBg:\'#1e3a8a\', activeBorder:\'#60a5fa\', activeText:\'#f8fafc\', soonBg:\'#7c2d12\', soonBorder:\'#fdba74\'\n                },\n                green: {\n                    tableWrap:\'#cfe7dc\', th1:\'#dcfce7\', th2:\'#bbf7d0\', td1:\'#ffffff\', td2:\'#f0fdf4\', line:\'#14532d\', text:\'#052e16\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#ea580c\', memoText:\'#ffffff\',\n                    searchBg:\'#f97316\', searchText:\'#ffffff\', searchBorder:\'#ea580c\',\n                    eightBg:\'#d9f99d\', eightText:\'#365314\', eightBorder:\'#a3e635\',\n                    activeBg:\'#bbf7d0\', activeBorder:\'#16a34a\', activeText:\'#052e16\', soonBg:\'#fef3c7\', soonBorder:\'#d97706\'\n                },\n                orange: {\n                    tableWrap:\'#fde7c8\', th1:\'#ffedd5\', th2:\'#fed7aa\', td1:\'#fffaf5\', td2:\'#fff7ed\', line:\'#7c2d12\', text:\'#431407\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#c2410c\', memoText:\'#ffffff\',\n                    searchBg:\'#ea580c\', searchText:\'#ffffff\', searchBorder:\'#c2410c\',\n                    eightBg:\'#ffedd5\', eightText:\'#7c2d12\', eightBorder:\'#fdba74\',\n                    activeBg:\'#fed7aa\', activeBorder:\'#ea580c\', activeText:\'#431407\', soonBg:\'#fef3c7\', soonBorder:\'#d97706\'\n                },\n                pink: {\n                    tableWrap:\'#ffe1ec\', th1:\'#ffe6ef\', th2:\'#ffd3e2\', td1:\'#fffefe\', td2:\'#fff7fb\', line:\'#7f1d43\', text:\'#4a1d2f\',\n                    calBg:\'#fff1f7\', calText:\'#be185d\', calBorder:\'#f9a8d4\',\n                    memoBg:\'#ec4899\', memoText:\'#ffffff\',\n                    searchBg:\'#fff1e6\', searchText:\'#9a3412\', searchBorder:\'#fdba74\',\n                    eightBg:\'#fdf2f8\', eightText:\'#9d174d\', eightBorder:\'#fbcfe8\',\n                    activeBg:\'#fbcfe8\', activeBorder:\'#ec4899\', activeText:\'#4a1d2f\', soonBg:\'#fff1e6\', soonBorder:\'#fb923c\'\n                },\n                blue: {\n                    tableWrap:\'#dbeafe\', th1:\'#e0f2fe\', th2:\'#bae6fd\', td1:\'#ffffff\', td2:\'#f8fbff\', line:\'#1e3a8a\', text:\'#0f172a\',\n                    calBg:\'#f5f3ff\', calText:\'#5b21b6\', calBorder:\'#ddd6fe\',\n                    memoBg:\'#2563eb\', memoText:\'#ffffff\',\n                    searchBg:\'#fff7ed\', searchText:\'#9a3412\', searchBorder:\'#fed7aa\',\n                    eightBg:\'#e0f2fe\', eightText:\'#075985\', eightBorder:\'#7dd3fc\',\n                    activeBg:\'#bfdbfe\', activeBorder:\'#2563eb\', activeText:\'#0f172a\', soonBg:\'#fef3c7\', soonBorder:\'#d97706\'\n                }\n            };\n\n            function docRoot() {\n                try { return window.parent.document; } catch(e) { return document; }\n            }\n\n            function visible(el) {\n                if (!el) return false;\n                const s = window.getComputedStyle(el);\n                if (s.display === \'none\' || s.visibility === \'hidden\') return false;\n                const r = el.getBoundingClientRect();\n                return r.width > 1 && r.height > 1;\n            }\n\n            function textOf(el) {\n                return ((el && (el.innerText || el.textContent)) || \'\').replace(/\\s+/g, \' \').trim();\n            }\n\n            function parseRgb(value) {\n                const m = (value || \'\').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);\n                if (!m) return null;\n                return { r:+m[1], g:+m[2], b:+m[3] };\n            }\n\n            function lum(c) {\n                if (!c) return 255;\n                return 0.299*c.r + 0.587*c.g + 0.114*c.b;\n            }\n\n            function toolbar(doc) {\n                const bars = Array.from(doc.querySelectorAll(\'div[data-testid="stHorizontalBlock"]\')).filter(visible);\n                return bars.find(b => {\n                    const t = textOf(b);\n                    return t.includes(\'오늘\') && t.includes(\'달력\') && t.includes(\'메모\');\n                }) || null;\n            }\n\n            function tableEl(doc) {\n                return Array.from(doc.querySelectorAll(\'table\')).find(t => {\n                    const x = textOf(t);\n                    return x.includes(\'교시\') && x.includes(\'학사일정\') && (x.includes(\'월\') || x.includes(\'화\'));\n                }) || null;\n            }\n\n            function paletteKey(doc) {\n                const bodyText = doc.body ? (doc.body.innerText || \'\') : \'\';\n                if (bodyText.includes(\'러블리 핑크\')) return \'pink\';\n\n                const bar = toolbar(doc);\n                const bg = parseRgb(bar ? getComputedStyle(bar).backgroundColor : getComputedStyle(doc.body).backgroundColor);\n                if (bg) {\n                    if (lum(bg) < 95) return \'dark\';\n                    if (bg.g > bg.r + 20 && bg.g >= bg.b) return \'green\';\n                    if (bg.r > 210 && bg.g > 145 && bg.b < 125) return \'orange\';\n                    if (bg.b > bg.r + 10 && bg.b > bg.g - 5) return \'blue\';\n                    if (bg.r > 230 && bg.b > 210 && bg.g < 225) return \'pink\';\n                }\n\n                const lower = bodyText.toLowerCase();\n                if (lower.includes(\'dark\') || bodyText.includes(\'다크\') || bodyText.includes(\'블랙\') || bodyText.includes(\'야간\')) return \'dark\';\n                if (bodyText.includes(\'그린\') || bodyText.includes(\'초록\') || bodyText.includes(\'숲\')) return \'green\';\n                if (bodyText.includes(\'오렌지\') || bodyText.includes(\'주황\')) return \'orange\';\n                if (bodyText.includes(\'블루\') || bodyText.includes(\'파랑\') || bodyText.includes(\'윈도우\')) return \'blue\';\n                return \'light\';\n            }\n\n            function nowInfo() {\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n                const periods = [\n                    [\'1교시\', \'08:00\', \'08:50\'],\n                    [\'2교시\', \'09:00\', \'09:50\'],\n                    [\'3교시\', \'10:00\', \'10:50\'],\n                    [\'4교시\', \'11:00\', \'11:50\'],\n                    [\'점심\', \'11:50\', \'12:40\'],\n                    [\'5교시\', \'12:40\', \'13:30\'],\n                    [\'6교시\', \'13:40\', \'14:30\'],\n                    [\'7교시\', \'14:40\', \'15:30\'],\n                    [\'8교시\', \'16:00\', \'16:50\'],\n                    [\'9교시\', \'17:00\', \'17:50\']\n                ];\n                function toMin(t) {\n                    const p = t.split(\':\').map(Number);\n                    return p[0] * 60 + p[1];\n                }\n                let state = \'쉬는시간\';\n                for (const p of periods) {\n                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {\n                        state = p[0];\n                        break;\n                    }\n                }\n                if (mins < 8 * 60) state = \'수업 전\';\n                if (mins >= 17 * 60 + 50) state = \'방과 후\';\n                return {\n                    text: String(now.getHours()).padStart(2, \'0\') + \':\' + String(now.getMinutes()).padStart(2, \'0\') + \' \' + state\n                };\n            }\n\n            function injectStyle(doc) {\n                if (doc.getElementById(STYLE_ID)) return;\n                const style = doc.createElement(\'style\');\n                style.id = STYLE_ID;\n                style.textContent = `\n                    html {\n                        overflow-anchor: none !important;\n                    }\n\n                    iframe[title*="streamlit"] {\n                        max-height: 1px !important;\n                    }\n\n                    #${CLOCK_ID} {\n                        position: fixed !important;\n                        right: max(10px, calc((100vw - min(450px, 100vw)) / 2 + 8px)) !important;\n                        top: 8px !important;\n                        z-index: 999999 !important;\n                        display: inline-flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding: 5px 12px !important;\n                        border-radius: 999px !important;\n                        border: 1px solid rgba(96, 165, 250, 0.36) !important;\n                        background: linear-gradient(180deg, rgba(250,252,255,0.98), rgba(232,240,255,0.96)) !important;\n                        color: #1d4ed8 !important;\n                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12) !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        font-size: 14px !important;\n                        line-height: 1.15 !important;\n                        font-weight: 900 !important;\n                        letter-spacing: -0.1px !important;\n                        text-align: center !important;\n                        pointer-events: none !important;\n                    }\n\n                    .s88-toolbar {\n                        display: flex !important;\n                        flex-direction: row !important;\n                        flex-wrap: nowrap !important;\n                        align-items: center !important;\n                        justify-content: flex-start !important;\n                        gap: 3px !important;\n                        width: min(450px, 100%) !important;\n                        box-sizing: border-box !important;\n                    }\n                    .s88-toolbar > div {\n                        width: auto !important;\n                        min-width: 0 !important;\n                        max-width: none !important;\n                        flex: 0 0 auto !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        margin: 0 !important;\n                    }\n                    .s88-nav-small {\n                        width: 24px !important;\n                        min-width: 24px !important;\n                        max-width: 24px !important;\n                        flex-basis: 24px !important;\n                    }\n                    .s88-sync-small {\n                        width: 34px !important;\n                        min-width: 34px !important;\n                        max-width: 34px !important;\n                        flex-basis: 34px !important;\n                    }\n\n                    body.step88-theme table.mobile-table {\n                        color: var(--s88-text) !important;\n                        border-color: var(--s88-line) !important;\n                        table-layout: fixed !important;\n                    }\n                    body.step88-theme table.mobile-table th {\n                        background-image: linear-gradient(180deg, var(--s88-th1), var(--s88-th2)) !important;\n                        color: var(--s88-text) !important;\n                        border-color: var(--s88-line) !important;\n                    }\n                    body.step88-theme table.mobile-table td {\n                        background-image: linear-gradient(180deg, var(--s88-td1), var(--s88-td2)) !important;\n                        color: var(--s88-text) !important;\n                        border-color: var(--s88-line) !important;\n                        height: 58px !important;\n                        min-height: 58px !important;\n                        vertical-align: middle !important;\n                        box-sizing: border-box !important;\n                        overflow: hidden !important;\n                    }\n                    body.step88-theme div:has(> table.mobile-table) {\n                        background: var(--s88-table-wrap) !important;\n                    }\n\n                    .s88-text-fit {\n                        white-space: normal !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: anywhere !important;\n                        line-height: 1.15 !important;\n                        letter-spacing: -0.25px !important;\n                    }\n                    .s88-text-fit.long {\n                        font-size: 10px !important;\n                        line-height: 1.12 !important;\n                        letter-spacing: -0.45px !important;\n                    }\n                    .s88-text-fit.very-long {\n                        font-size: 8.5px !important;\n                        line-height: 1.08 !important;\n                        letter-spacing: -0.65px !important;\n                    }\n                    .s88-query-fit {\n                        font-size: 8.5px !important;\n                        line-height: 1.08 !important;\n                        letter-spacing: -0.65px !important;\n                        white-space: normal !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: anywhere !important;\n                        overflow: hidden !important;\n                        text-align: center !important;\n                        vertical-align: middle !important;\n                        padding: 1px 2px !important;\n                    }\n                    .s88-query-fit.extreme {\n                        font-size: 7.5px !important;\n                        letter-spacing: -0.8px !important;\n                        line-height: 1.03 !important;\n                    }\n\n                    .s88-btn-calendar, .s88-btn-memo, .s88-btn-search, .s88-btn-89 {\n                        box-sizing: border-box !important;\n                        min-height: 40px !important;\n                        height: 40px !important;\n                        border-radius: 7px !important;\n                        font-weight: 800 !important;\n                        text-align: center !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        overflow-wrap: normal !important;\n                        writing-mode: horizontal-tb !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                    }\n                    .s88-btn-calendar *, .s88-btn-memo *, .s88-btn-search *, .s88-btn-89 * {\n                        color: inherit !important;\n                        -webkit-text-fill-color: currentColor !important;\n                        white-space: nowrap !important;\n                        word-break: keep-all !important;\n                        text-align: center !important;\n                    }\n                    .s88-btn-calendar {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        flex: 0 0 58px !important;\n                        background: var(--s88-cal-bg) !important;\n                        border: 1px solid var(--s88-cal-border) !important;\n                        color: var(--s88-cal-text) !important;\n                        padding: 0 !important;\n                        position: relative !important;\n                        overflow: hidden !important;\n                    }\n                    .s88-btn-memo {\n                        background: var(--s88-memo-bg) !important;\n                        border: 1px solid var(--s88-memo-bg) !important;\n                        color: var(--s88-memo-text) !important;\n                    }\n                    .s88-btn-search {\n                        background: var(--s88-search-bg) !important;\n                        border: 1px solid var(--s88-search-border) !important;\n                        color: var(--s88-search-text) !important;\n                    }\n                    .s88-btn-89 {\n                        background: var(--s88-eight-bg) !important;\n                        border: 1px solid var(--s88-eight-border) !important;\n                        color: var(--s88-eight-text) !important;\n                    }\n\n                    .s88-calendar-shell {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        flex: 0 0 58px !important;\n                        position: relative !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        padding: 0 !important;\n                        box-sizing: border-box !important;\n                    }\n                    .s88-calendar-shell > * {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                    }\n                    .s88-calendar-shell [data-baseweb="select"],\n                    .s88-calendar-shell [role="button"],\n                    .s88-calendar-shell button {\n                        width: 58px !important;\n                        min-width: 58px !important;\n                        max-width: 58px !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        grid-template-columns: 1fr !important;\n                        padding-left: 0 !important;\n                        padding-right: 0 !important;\n                        color: transparent !important;\n                        -webkit-text-fill-color: transparent !important;\n                    }\n                    .s88-calendar-shell [data-baseweb="select"] *,\n                    .s88-calendar-shell [role="button"] *,\n                    .s88-calendar-shell button * {\n                        color: transparent !important;\n                        -webkit-text-fill-color: transparent !important;\n                    }\n                    .s88-calendar-shell svg,\n                    .s88-calendar-shell [aria-hidden="true"],\n                    .s88-remove {\n                        display: none !important;\n                        width: 0 !important;\n                        min-width: 0 !important;\n                        max-width: 0 !important;\n                        flex: 0 0 0 !important;\n                        margin: 0 !important;\n                        padding: 0 !important;\n                    }\n                    .s88-calendar-overlay {\n                        position: absolute !important;\n                        left: 50% !important;\n                        top: 50% !important;\n                        transform: translate(-50%, -50%) !important;\n                        display: flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        width: max-content !important;\n                        pointer-events: none !important;\n                        color: var(--s88-cal-text) !important;\n                        -webkit-text-fill-color: var(--s88-cal-text) !important;\n                        font-size: 14px !important;\n                        font-weight: 800 !important;\n                        line-height: 1 !important;\n                        text-align: center !important;\n                        z-index: 3 !important;\n                    }\n\n                    table.mobile-table .s88-current-col {\n                        box-shadow: inset 0 3px 0 var(--s88-active-border) !important;\n                    }\n                    table.mobile-table .s88-current-rowhead,\n                    table.mobile-table .s88-current-cell {\n                        background-image: linear-gradient(180deg, var(--s88-active-bg), var(--s88-active-bg)) !important;\n                        color: var(--s88-active-text) !important;\n                        box-shadow: inset 0 0 0 2px var(--s88-active-border) !important;\n                    }\n                    table.mobile-table .s88-soon-cell,\n                    table.mobile-table .s88-soon-rowhead {\n                        background-image: linear-gradient(180deg, var(--s88-soon-bg), var(--s88-soon-bg)) !important;\n                        box-shadow: inset 0 0 0 2px var(--s88-soon-border) !important;\n                    }\n                    table.mobile-table .s88-current-rowhead,\n                    table.mobile-table .s88-soon-rowhead {\n                        position: relative !important;\n                    }\n                    .s88-period-badge {\n                        position: absolute !important;\n                        left: 50% !important;\n                        bottom: 2px !important;\n                        transform: translateX(-50%) !important;\n                        display: inline-flex !important;\n                        align-items: center !important;\n                        justify-content: center !important;\n                        width: auto !important;\n                        max-width: 92% !important;\n                        padding: 1px 5px !important;\n                        border-radius: 999px !important;\n                        font-size: 9px !important;\n                        font-weight: 900 !important;\n                        background: var(--s88-active-border) !important;\n                        color: #fff !important;\n                        line-height: 1.1 !important;\n                        white-space: nowrap !important;\n                        pointer-events: none !important;\n                    }\n                    .s88-period-badge.soon {\n                        background: var(--s88-soon-border) !important;\n                    }\n                `;\n                doc.head.appendChild(style);\n            }\n\n            function applyVars(doc) {\n                const key = paletteKey(doc);\n                const p = PALETTES[key] || PALETTES.light;\n                doc.body.classList.add(\'step88-theme\');\n                const vars = {\n                    \'--s88-table-wrap\': p.tableWrap, \'--s88-th1\': p.th1, \'--s88-th2\': p.th2, \'--s88-td1\': p.td1, \'--s88-td2\': p.td2,\n                    \'--s88-line\': p.line, \'--s88-text\': p.text,\n                    \'--s88-cal-bg\': p.calBg, \'--s88-cal-text\': p.calText, \'--s88-cal-border\': p.calBorder,\n                    \'--s88-memo-bg\': p.memoBg, \'--s88-memo-text\': p.memoText,\n                    \'--s88-search-bg\': p.searchBg, \'--s88-search-text\': p.searchText, \'--s88-search-border\': p.searchBorder,\n                    \'--s88-eight-bg\': p.eightBg, \'--s88-eight-text\': p.eightText, \'--s88-eight-border\': p.eightBorder,\n                    \'--s88-active-bg\': p.activeBg, \'--s88-active-border\': p.activeBorder, \'--s88-active-text\': p.activeText,\n                    \'--s88-soon-bg\': p.soonBg, \'--s88-soon-border\': p.soonBorder\n                };\n                for (const [k, v] of Object.entries(vars)) doc.body.style.setProperty(k, v);\n            }\n\n            function hideOldClocks(doc) {\n                const known = [\n                    \'step80-clock-fixed\',\'step79-clock-fixed\',\'step78-clock-fixed\',\'step77-clock-fixed\',\n                    \'step86-clock-fixed\',\'step85-clock-fixed\',\'step84-clock-fixed\',\'step87-clock-fixed\'\n                ];\n                for (const id of known) {\n                    const el = doc.getElementById(id);\n                    if (el) el.remove();\n                }\n                const stateTexts = new Set([\'수업 전\',\'방과 후\',\'쉬는시간\',\'1교시\',\'2교시\',\'3교시\',\'4교시\',\'점심\',\'5교시\',\'6교시\',\'7교시\',\'8교시\',\'9교시\']);\n                for (const el of Array.from(doc.querySelectorAll(\'div,p,span\'))) {\n                    const t = (el.innerText || \'\').trim();\n                    if (!stateTexts.has(t)) continue;\n                    const r = el.getBoundingClientRect();\n                    if (r.top < 100 && r.left > window.innerWidth * 0.45) {\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                    }\n                }\n            }\n\n            function updateClock(doc) {\n                hideOldClocks(doc);\n                let clock = doc.getElementById(CLOCK_ID);\n                if (!clock) {\n                    clock = doc.createElement(\'div\');\n                    clock.id = CLOCK_ID;\n                    doc.body.appendChild(clock);\n                }\n                clock.textContent = nowInfo().text;\n            }\n\n            function classify(child) {\n                const t = textOf(child);\n                const html = child.innerHTML || \'\';\n                if (t.includes(\'오늘\')) return \'today\';\n                if (t.includes(\'달력\')) return \'calendar\';\n                if (t.includes(\'메모\')) return \'memo\';\n                if (t.includes(\'조회\')) return \'search\';\n                if (t.includes(\'8·9\') || t.includes(\'8-9\') || t === \'89\' || t.includes(\'89\')) return \'89\';\n                if (t.includes(\'⚙\') || t.includes(\'설정\')) return \'settings\';\n                if (/refresh|sync|rotate|reload|arrow-repeat|counterclockwise|clockwise/i.test(html) || t === \'↻\' || t === \'⟳\' || t === \'🔄\') return \'sync\';\n                if (t === \'\' || t.length <= 2) return \'icon\';\n                return \'other\';\n            }\n\n            function target(child) {\n                return child.querySelector(\'button,[role="button"],div[data-baseweb="select"]\') || child;\n            }\n\n            function calendar(child, doc) {\n                child.classList.add(\'s88-calendar-shell\');\n                const btn = target(child);\n                btn.classList.add(\'s88-btn-calendar\');\n\n                const removable = [];\n                for (const svg of Array.from(child.querySelectorAll(\'svg\'))) removable.push(svg);\n                for (const el of Array.from(child.querySelectorAll(\'span,div,p\'))) {\n                    const t = (el.textContent || \'\').trim();\n                    if (/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test(t)) removable.push(el);\n                }\n                for (const el of removable) {\n                    try { el.remove(); }\n                    catch(e) {\n                        el.classList.add(\'s88-remove\');\n                        el.style.setProperty(\'display\', \'none\', \'important\');\n                    }\n                }\n\n                let overlay = child.querySelector(\'.s88-calendar-overlay\');\n                if (!overlay) {\n                    overlay = doc.createElement(\'span\');\n                    overlay.className = \'s88-calendar-overlay\';\n                    overlay.textContent = \'달력\';\n                    child.appendChild(overlay);\n                } else {\n                    overlay.textContent = \'달력\';\n                }\n            }\n\n            function fixToolbar(doc) {\n                const bar = toolbar(doc);\n                if (!bar) return;\n\n                bar.classList.add(\'s88-toolbar\');\n\n                const children = Array.from(bar.children || []);\n                let todayIdx = -1;\n                children.forEach((child, idx) => {\n                    if (classify(child) === \'today\') todayIdx = idx;\n                });\n\n                let leftArrowUsed = false;\n                let rightArrowUsed = false;\n                let syncUsed = false;\n\n                children.forEach((child, idx) => {\n                    const kind = classify(child);\n                    const btn = target(child);\n                    let order = 500 + idx;\n\n                    child.classList.remove(\'s88-nav-small\',\'s88-sync-small\');\n\n                    if (kind === \'today\') order = 20;\n                    else if (kind === \'calendar\') {\n                        order = 40;\n                        calendar(child, doc);\n                    } else if (kind === \'memo\') {\n                        order = 60;\n                        btn.classList.add(\'s88-btn-memo\');\n                    } else if (kind === \'search\') {\n                        order = 70;\n                        btn.classList.add(\'s88-btn-search\');\n                    } else if (kind === \'89\') {\n                        order = 80;\n                        btn.classList.add(\'s88-btn-89\');\n                    } else if (kind === \'sync\') {\n                        order = 90;\n                        child.classList.add(\'s88-sync-small\');\n                        syncUsed = true;\n                    } else if (kind === \'settings\') {\n                        order = 100;\n                    } else if (kind === \'icon\') {\n                        if (todayIdx >= 0 && idx < todayIdx && !leftArrowUsed) {\n                            order = 10;\n                            child.classList.add(\'s88-nav-small\');\n                            leftArrowUsed = true;\n                        } else if (todayIdx >= 0 && idx > todayIdx && !rightArrowUsed) {\n                            order = 30;\n                            child.classList.add(\'s88-nav-small\');\n                            rightArrowUsed = true;\n                        } else if (!syncUsed) {\n                            order = 90;\n                            child.classList.add(\'s88-sync-small\');\n                            syncUsed = true;\n                        }\n                    }\n\n                    child.style.setProperty(\'order\', String(order), \'important\');\n                });\n            }\n\n            function parseMemoColor(doc) {\n                const allowed = /<span\\s+style=["\']\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*["\']>(.*?)<\\/span>/gis;\n\n                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);\n                const nodes = [];\n                let node;\n                while ((node = walker.nextNode())) {\n                    const v = node.nodeValue || \'\';\n                    allowed.lastIndex = 0;\n                    if (v.includes(\'<span\') && allowed.test(v)) nodes.push(node);\n                }\n                for (const textNode of nodes) {\n                    const text = textNode.nodeValue || \'\';\n                    const frag = doc.createDocumentFragment();\n                    let last = 0;\n                    allowed.lastIndex = 0;\n                    let m;\n                    while ((m = allowed.exec(text))) {\n                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));\n                        const span = doc.createElement(\'span\');\n                        span.style.setProperty(m[1].toLowerCase(), m[2]);\n                        span.textContent = m[3];\n                        frag.appendChild(span);\n                        last = allowed.lastIndex;\n                    }\n                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));\n                    if (textNode.parentNode) textNode.parentNode.replaceChild(frag, textNode);\n                }\n\n                const entityRe = /&lt;span\\s+style=(?:&quot;|")\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*(?:&quot;|")&gt;([\\s\\S]*?)&lt;\\/span&gt;/gi;\n                for (const el of Array.from(doc.querySelectorAll(\'div,p,span\'))) {\n                    if (!el.innerHTML || !el.innerHTML.includes(\'&lt;span\')) continue;\n                    el.innerHTML = el.innerHTML.replace(entityRe, function(_, prop, color, content) {\n                        return \'<span style="\' + prop + \':\' + color + \'">\' + content + \'</span>\';\n                    });\n                }\n            }\n\n            function parseMinutes(timeText) {\n                const m = String(timeText || \'\').match(/(\\d{1,2}):(\\d{2})/);\n                if (!m) return null;\n                return parseInt(m[1], 10) * 60 + parseInt(m[2], 10);\n            }\n\n            function rowRange(row) {\n                const first = row.children && row.children.length ? row.children[0] : null;\n                if (!first) return null;\n                const times = (first.innerText || \'\').match(/\\d{1,2}:\\d{2}/g);\n                if (!times || times.length < 2) return null;\n                return { start: parseMinutes(times[0]), end: parseMinutes(times[1]) };\n            }\n\n            function todayColumnIndex() {\n                const d = new Date().getDay();\n                if (d < 1 || d > 5) return -1;\n                return d;\n            }\n\n            function cleanupOldArtifacts(table) {\n                const classes = [\n                    \'s84-current-col\',\'s84-current-rowhead\',\'s84-current-cell\',\'s84-soon-cell\',\'s84-soon-rowhead\',\n                    \'s85-current-col\',\'s85-current-rowhead\',\'s85-current-cell\',\'s85-soon-cell\',\'s85-soon-rowhead\',\n                    \'s86-current-col\',\'s86-current-rowhead\',\'s86-current-cell\',\'s86-soon-cell\',\'s86-soon-rowhead\',\n                    \'s87-current-col\',\'s87-current-rowhead\',\'s87-current-cell\',\'s87-soon-cell\',\'s87-soon-rowhead\',\n                    \'s88-current-col\',\'s88-current-rowhead\',\'s88-current-cell\',\'s88-soon-cell\',\'s88-soon-rowhead\'\n                ];\n                for (const el of Array.from(table.querySelectorAll(\'.\' + classes.join(\',.\')))) {\n                    el.classList.remove(...classes);\n                }\n                for (const b of Array.from(table.querySelectorAll(\'.s84-period-badge,.s85-period-badge,.s86-period-badge,.s87-period-badge,.s88-period-badge\'))) b.remove();\n                for (const br of Array.from(table.querySelectorAll(\'br[data-s84-period-br],br[data-s85-period-br],br[data-s86-period-br],br[data-s87-period-br],br[data-s88-period-br]\'))) br.remove();\n            }\n\n            function highlightCurrentPeriod(doc) {\n                const table = tableEl(doc);\n                if (!table) return;\n\n                cleanupOldArtifacts(table);\n\n                const col = todayColumnIndex();\n                const rows = Array.from(table.querySelectorAll(\'tr\'));\n                if (col < 1 || !rows.length) return;\n\n                const now = new Date();\n                const mins = now.getHours() * 60 + now.getMinutes();\n\n                let targetRow = null;\n                let mode = \'current\';\n\n                for (const row of rows) {\n                    const r = rowRange(row);\n                    if (!r) continue;\n                    if (r.start <= mins && mins < r.end) {\n                        targetRow = row;\n                        mode = \'current\';\n                        break;\n                    }\n                }\n\n                if (!targetRow) {\n                    let nearest = null;\n                    for (const row of rows) {\n                        const r = rowRange(row);\n                        if (!r) continue;\n                        const diff = r.start - mins;\n                        if (diff > 0 && diff <= 15 && (!nearest || diff < nearest.diff)) nearest = { row, diff };\n                    }\n                    if (nearest) {\n                        targetRow = nearest.row;\n                        mode = \'soon\';\n                    }\n                }\n\n                const headerRow = rows[0];\n                if (headerRow && headerRow.children[col]) headerRow.children[col].classList.add(\'s88-current-col\');\n\n                if (!targetRow) return;\n\n                const rowHead = targetRow.children[0];\n                const cell = targetRow.children[col];\n\n                if (mode === \'current\') {\n                    if (rowHead) rowHead.classList.add(\'s88-current-rowhead\');\n                    if (cell) cell.classList.add(\'s88-current-cell\');\n                } else {\n                    if (rowHead) rowHead.classList.add(\'s88-soon-rowhead\');\n                    if (cell) cell.classList.add(\'s88-soon-cell\');\n                }\n\n                if (rowHead && !rowHead.querySelector(\'.s88-period-badge\')) {\n                    const badge = doc.createElement(\'span\');\n                    badge.className = \'s88-period-badge\' + (mode === \'soon\' ? \' soon\' : \'\');\n                    badge.textContent = mode === \'soon\' ? \'시작 전\' : \'진행 중\';\n                    rowHead.appendChild(badge);\n                }\n            }\n\n            function fitTableText(doc) {\n                const table = tableEl(doc);\n                if (!table) return;\n\n                const rows = Array.from(table.querySelectorAll(\'tr\'));\n                for (const row of rows) {\n                    const cells = Array.from(row.children || []);\n                    const firstText = cells.length ? textOf(cells[0]) : \'\';\n                    const isHeader = firstText === \'교시\' || (firstText.includes(\'교시\') && !firstText.match(/\\d{1,2}:\\d{2}/));\n                    const isQuery = firstText.includes(\'조회\');\n\n                    for (let i = 1; i < cells.length; i++) {\n                        const cell = cells[i];\n                        if (!cell) continue;\n                        const t = textOf(cell);\n                        if (!t) continue;\n\n                        if (isQuery) {\n                            cell.classList.add(\'s88-query-fit\');\n                            if (t.length > 34) cell.classList.add(\'extreme\');\n                        } else if (!isHeader) {\n                            if (t.length > 18) cell.classList.add(\'s88-text-fit\', \'long\');\n                            if (t.length > 30) cell.classList.add(\'s88-text-fit\', \'very-long\');\n                        }\n                    }\n                }\n            }\n\n            function runStable() {\n                const doc = docRoot();\n                const scroller = doc.scrollingElement || doc.documentElement || doc.body;\n                const oldTop = scroller ? scroller.scrollTop : 0;\n                const oldLeft = scroller ? scroller.scrollLeft : 0;\n\n                injectStyle(doc);\n                applyVars(doc);\n                updateClock(doc);\n                fixToolbar(doc);\n                parseMemoColor(doc);\n                fitTableText(doc);\n                highlightCurrentPeriod(doc);\n\n                requestAnimationFrame(function() {\n                    if (scroller && Math.abs(scroller.scrollTop - oldTop) > 2) {\n                        scroller.scrollTop = oldTop;\n                        scroller.scrollLeft = oldLeft;\n                    }\n                });\n            }\n\n            function updateClockOnly() {\n                const doc = docRoot();\n                updateClock(doc);\n            }\n\n            runStable();\n            setTimeout(runStable, 200);\n            setTimeout(runStable, 900);\n            setTimeout(runStable, 1800);\n\n            // 이후에는 버튼/표 DOM은 다시 건드리지 않고 시각만 1분마다 갱신\n            setInterval(updateClockOnly, 60000);\n        })();\n        </script>\n        """,\n        height=0,\n        width=0,\n    )\nexcept Exception:\n    pass\n# [STEP88_WEB_SINGLE_STABLE_DOM_END]\n'
SSL_BLOCK = '\n# [STEP88_SUPABASE_SSL_FALLBACK_START]\n# 학교/기관망 SSL 검사로 Supabase HTTPS 인증서 검증이 실패하는 경우만 Supabase 요청을 1회 재시도합니다.\ntry:\n    import requests as _step88_requests\n    try:\n        import urllib3 as _step88_urllib3\n        _step88_urllib3.disable_warnings(_step88_urllib3.exceptions.InsecureRequestWarning)\n    except Exception:\n        pass\n\n    if not getattr(_step88_requests.sessions.Session.request, "_step88_ssl_fallback", False):\n        _step88_original_request = _step88_requests.sessions.Session.request\n\n        def _step88_request_with_ssl_fallback(self, method, url, **kwargs):\n            try:\n                return _step88_original_request(self, method, url, **kwargs)\n            except _step88_requests.exceptions.SSLError:\n                if "supabase.co" in str(url):\n                    kwargs["verify"] = False\n                    return _step88_original_request(self, method, url, **kwargs)\n                raise\n\n        _step88_request_with_ssl_fallback._step88_ssl_fallback = True\n        _step88_requests.sessions.Session.request = _step88_request_with_ssl_fallback\nexcept Exception:\n    pass\n# [STEP88_SUPABASE_SSL_FALLBACK_END]\n'
LOVELY_PINK_THEME = '\n    "러블리 핑크": {\n        "bg": "#fff5f8",\n        "card": "#ffffff",\n        "text": "#4a1d2f",\n        "muted": "#9f647a",\n        "primary": "#ec4899",\n        "primary_dark": "#db2777",\n        "accent": "#f9a8d4",\n        "header_bg": "#ffe6ef",\n        "header_bg2": "#ffd3e2",\n        "cell_bg": "#fffafe",\n        "cell_bg2": "#fff7fb",\n        "border": "#f3bfd2",\n        "shadow": "rgba(236, 72, 153, 0.14)",\n    },\n'

DOM_REMOVE_MARKERS = [
    ("# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_START]", "# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_END]"),
    ("# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_START]", "# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_END]"),
    ("# [STEP80_WEB_TOPBAR_AND_THEME_DOM_START]", "# [STEP80_WEB_TOPBAR_AND_THEME_DOM_END]"),
    ("# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_START]", "# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_END]"),
    ("# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_START]", "# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_END]"),
    ("# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_START]", "# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_END]"),
    ("# [STEP84_WEB_SAFE_DOM_REFINEMENT_START]", "# [STEP84_WEB_SAFE_DOM_REFINEMENT_END]"),
    ("# [STEP85_WEB_STABLE_DOM_REFINEMENT_START]", "# [STEP85_WEB_STABLE_DOM_REFINEMENT_END]"),
    ("# [STEP86_WEB_SCROLL_ROW_STABLE_DOM_START]", "# [STEP86_WEB_SCROLL_ROW_STABLE_DOM_END]"),
    ("# [STEP87_WEB_NO_SCROLL_JUMP_DOM_START]", "# [STEP87_WEB_NO_SCROLL_JUMP_DOM_END]"),
    ("# [STEP88_WEB_SINGLE_STABLE_DOM_START]", "# [STEP88_WEB_SINGLE_STABLE_DOM_END]"),
]

SSL_REMOVE_MARKERS = [
    ("# [STEP84_SUPABASE_SSL_FALLBACK_START]", "# [STEP84_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP85_SUPABASE_SSL_FALLBACK_START]", "# [STEP85_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP86_SUPABASE_SSL_FALLBACK_START]", "# [STEP86_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP87_SUPABASE_SSL_FALLBACK_START]", "# [STEP87_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP88_SUPABASE_SSL_FALLBACK_START]", "# [STEP88_SUPABASE_SSL_FALLBACK_END]"),
]


def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step88_restore_before87_{STAMP}{APP.suffix}")
    b.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[현재 백업] {b}")


def compiles(text: str, name: str):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def choose_restore_base():
    patterns = [
        "app_before_step87_stop_scroll_jump_*.py",
        "app_before_step86_scroll_row_fix_*.py",
        "app_before_step85_period_growth_fix_*.py",
        "app_before_step84_school_ssl_theme_*.py",
        "app_before_step83_restore_pre82_*.py",
    ]

    for pat in patterns:
        candidates = sorted(APP.parent.glob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
        for b in candidates:
            text = b.read_text(encoding="utf-8", errors="replace")
            ok, err = compiles(text, str(b))
            print(f"[복구 후보] {b.name} -> {'OK' if ok else 'FAIL'}")
            if ok:
                return text, b

    text = APP.read_text(encoding="utf-8", errors="replace")
    ok, err = compiles(text, str(APP))
    if ok:
        print("[안내] 적절한 복구 백업을 찾지 못해 현재 app.py를 기준으로 진행")
        return text, None

    raise RuntimeError("컴파일 가능한 복구 기준 파일을 찾지 못했습니다.")


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


def remove_blocks(text: str, markers):
    removed = 0
    for start, end in markers:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    return text, removed


def insert_ssl_fallback(text: str):
    lines = text.splitlines()
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
    print("Step88 restore before Step87 + single stable DOM")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    try:
        text, base = choose_restore_base()
        text, removed_dom = remove_blocks(text, DOM_REMOVE_MARKERS)
        text, removed_ssl = remove_blocks(text, SSL_REMOVE_MARKERS)
        text, ssl_status = insert_ssl_fallback(text)
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
    print("[완료] Step88 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 복구 기준: {base}")
    print(f"- 기존 Step78~88 DOM 블록 제거: {removed_dom}")
    print(f"- 기존 SSL fallback 블록 제거: {removed_ssl}")
    print(f"- SSL fallback 재삽입: {ssl_status}")
    print(f"- 러블리 핑크 테마 dict 처리: {theme_dict_status}")
    print(f"- 러블리 핑크 옵션 처리: {option_changes}")
    print("- 상단바 가로 배치 재구성")
    print("- DOM 보정은 초기 3회만 실행, 이후 시각만 1분마다 갱신")
    print("- 시각 배지 1개만 유지")
    print("- 스크롤 위치 보존")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 상단 버튼이 다시 가로로 배치되는지")
    print("2. 아래로 스크롤해도 최상단으로 끌려가지 않는지")
    print("3. 현재시각 배지가 1개만 보이는지")
    print("4. 설정 아이콘 위에서 커서가 반복 깜빡이지 않는지")
    print("5. 달력 글자가 중앙에 오는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

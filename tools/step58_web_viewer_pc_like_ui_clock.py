# tools/step58_web_viewer_pc_like_ui_clock.py
# ------------------------------------------------------------
# Step58: 웹뷰어 PC버전 유사 UI 정리 + 현재시각/현재교시 표시
#
# 실행:
#   python tools\step58_web_viewer_pc_like_ui_clock.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

START = "# [WEB_VIEWER_PC_LIKE_UI_START]"
END = "# [WEB_VIEWER_PC_LIKE_UI_END]"
CALL_START = "# [WEB_VIEWER_PC_LIKE_UI_CALL_START]"
CALL_END = "# [WEB_VIEWER_PC_LIKE_UI_CALL_END]"

INJECT_CODE = '\n# [WEB_VIEWER_PC_LIKE_UI_START]\ndef _mh_now_period_info():\n    """현재 시각과 현재 교시 정보를 반환한다."""\n    try:\n        from datetime import datetime, time\n        now = datetime.now()\n        t = now.time()\n        periods = [\n            ("1교시", "08:00~08:50", time(8, 0), time(8, 50), 1),\n            ("2교시", "09:00~09:50", time(9, 0), time(9, 50), 2),\n            ("3교시", "10:00~10:50", time(10, 0), time(10, 50), 3),\n            ("4교시", "11:00~11:50", time(11, 0), time(11, 50), 4),\n            ("점심", "11:50~12:40", time(11, 50), time(12, 40), "lunch"),\n            ("5교시", "12:40~13:30", time(12, 40), time(13, 30), 5),\n            ("6교시", "13:40~14:30", time(13, 40), time(14, 30), 6),\n            ("7교시", "14:40~15:30", time(14, 40), time(15, 30), 7),\n            ("8교시", "16:00~16:50", time(16, 0), time(16, 50), 8),\n            ("9교시", "17:00~17:50", time(17, 0), time(17, 50), 9),\n        ]\n        for label, range_text, start, end, key in periods:\n            if start <= t < end:\n                return {\n                    "label": label,\n                    "range": range_text,\n                    "key": key,\n                    "clock": now.strftime("%H:%M"),\n                    "is_class_time": key != "lunch",\n                }\n        return {\n            "label": "수업 전" if t < time(8, 0) else ("방과 후" if t >= time(17, 50) else "쉬는시간"),\n            "range": "",\n            "key": None,\n            "clock": now.strftime("%H:%M"),\n            "is_class_time": False,\n        }\n    except Exception:\n        return {"label": "", "range": "", "key": None, "clock": "--:--", "is_class_time": False}\n\n\ndef _mh_render_clock_badge():\n    """현재시각/현재교시 배지 표시."""\n    try:\n        info = _mh_now_period_info()\n        label = info.get("label") or ""\n        rng = info.get("range") or ""\n        clock = info.get("clock") or "--:--"\n        sub = f" · {rng}" if rng else ""\n        st.markdown(\n            f"""\n            <div class="mh-now-clock-row">\n                <span class="mh-now-clock-pill">\n                    <b>{clock}</b>\n                    <span>{label}{sub}</span>\n                </span>\n            </div>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef _mh_strip_memo_number(text):\n    """웹뷰어 메모 번호 제거용."""\n    try:\n        import re\n        return re.sub(r"^\\s*\\d+\\.\\s*", "", str(text or "")).strip()\n    except Exception:\n        return str(text or "").strip()\n\n\ndef _mh_memo_is_done(m):\n    try:\n        if isinstance(m, dict):\n            return bool(m.get("strike") or m.get("is_strike") or m.get("done") or m.get("completed"))\n        return False\n    except Exception:\n        return False\n\n\ndef _mh_memo_is_important(m):\n    try:\n        if isinstance(m, dict):\n            return bool(m.get("important") or m.get("is_important") or m.get("star"))\n        return False\n    except Exception:\n        return False\n\n\ndef _mh_memo_text(m):\n    try:\n        if isinstance(m, dict):\n            raw = m.get("text")\n            if raw is None:\n                raw = m.get("memo_text")\n            if raw is None:\n                raw = m.get("content")\n            return _mh_strip_memo_number(raw)\n        return _mh_strip_memo_number(m)\n    except Exception:\n        return ""\n\n\ndef _mh_memo_time(m):\n    try:\n        if isinstance(m, dict):\n            return str(m.get("time") or m.get("created_at") or m.get("updated_at") or "")\n        return ""\n    except Exception:\n        return ""\n\n\ndef _mh_group_memos_pc_style(memos):\n    """메모 데이터를 PC버전과 유사하게 중요/일반/완료 순서로 그룹화."""\n    important, normal, done = [], [], []\n    try:\n        for m in memos or []:\n            if _mh_memo_is_done(m):\n                done.append(m)\n            elif _mh_memo_is_important(m):\n                important.append(m)\n            else:\n                normal.append(m)\n    except Exception:\n        pass\n    return important, normal, done\n\n\ndef _mh_render_memo_list_pc_style(memos, container=None):\n    """가능한 경우 사용할 수 있는 PC 스타일 메모 렌더러."""\n    try:\n        import html\n        target = container if container is not None else st\n        important, normal, done = _mh_group_memos_pc_style(memos)\n        groups = [\n            ("📌 중요 메모", important, "important"),\n            ("▣ 일반 메모", normal, "normal"),\n            ("✔ 완료 메모", done, "done"),\n        ]\n        parts = [\'<div class="mh-memo-pc-list">\']\n        for title, items, cls in groups:\n            if not items:\n                continue\n            parts.append(f\'<div class="mh-memo-group-title mh-memo-{cls}">{html.escape(title)} ({len(items)}) ▲</div>\')\n            for m in items:\n                txt = html.escape(_mh_memo_text(m)).replace("\\\\n", "<br>")\n                tm = html.escape(_mh_memo_time(m))\n                star = "⭐" if _mh_memo_is_important(m) else "☆"\n                check = "✔" if _mh_memo_is_done(m) else "○"\n                done_cls = " is-done" if _mh_memo_is_done(m) else ""\n                parts.append(\n                    f\'<div class="mh-memo-row{done_cls}">\'\n                    f\'<span class="mh-memo-check">{check}</span>\'\n                    f\'<span class="mh-memo-star">{star}</span>\'\n                    f\'<span class="mh-memo-body">{txt}</span>\'\n                    f\'<span class="mh-memo-time">{tm}</span>\'\n                    f\'</div>\'\n                )\n        parts.append("</div>")\n        target.markdown("\\\\n".join(parts), unsafe_allow_html=True)\n        return True\n    except Exception:\n        return False\n\n\ndef _mh_inject_pc_like_web_css():\n    """웹뷰어 UI 균형/메모/현재교시 강조 CSS + DOM 보정 스크립트."""\n    try:\n        info = _mh_now_period_info()\n        current_key = info.get("key")\n        current_key_js = "" if current_key is None else str(current_key)\n\n        st.markdown(\n            f"""\n            <style>\n            div[data-testid="stHorizontalBlock"] {{\n                gap: 0.45rem !important;\n                align-items: center !important;\n            }}\n            div[data-testid="stButton"] > button,\n            .stButton > button {{\n                min-width: 54px !important;\n                height: 42px !important;\n                padding: 0.35rem 0.72rem !important;\n                border-radius: 9px !important;\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                line-height: 1.1 !important;\n                display: inline-flex !important;\n                align-items: center !important;\n                justify-content: center !important;\n                text-align: center !important;\n            }}\n            div[data-testid="stButton"] > button p,\n            .stButton > button p,\n            button p {{\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n                line-height: 1.1 !important;\n                margin: 0 !important;\n            }}\n            .mh-now-clock-row {{\n                display: flex;\n                justify-content: flex-end;\n                align-items: center;\n                margin: -0.2rem 0 0.55rem 0;\n            }}\n            .mh-now-clock-pill {{\n                display: inline-flex;\n                align-items: center;\n                gap: 0.4rem;\n                padding: 0.22rem 0.6rem;\n                border-radius: 999px;\n                border: 1px solid rgba(37, 99, 235, 0.22);\n                background: rgba(239, 246, 255, 0.85);\n                color: #1e3a8a;\n                font-size: 0.78rem;\n                line-height: 1.2;\n                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);\n            }}\n            .mh-now-clock-pill b {{\n                font-size: 0.86rem;\n            }}\n            @media (max-width: 640px) {{\n                .mh-now-clock-row {{\n                    justify-content: flex-end;\n                    margin-right: 0.15rem;\n                }}\n                .mh-now-clock-pill {{\n                    font-size: 0.72rem;\n                    padding: 0.18rem 0.48rem;\n                }}\n                div[data-testid="stButton"] > button,\n                .stButton > button {{\n                    min-width: 50px !important;\n                    height: 40px !important;\n                    padding: 0.25rem 0.55rem !important;\n                }}\n            }}\n            .mh-memo-pc-list,\n            .memo-list,\n            .memo-box,\n            .memo-container {{\n                font-size: 0.92rem;\n            }}\n            .mh-memo-group-title {{\n                font-weight: 700;\n                padding: 0.32rem 0.35rem 0.2rem 0.35rem;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n            }}\n            .mh-memo-important {{ color: #ef4444; }}\n            .mh-memo-normal {{ color: #0f172a; }}\n            .mh-memo-done {{ color: #94a3b8; }}\n            .mh-memo-row {{\n                display: grid;\n                grid-template-columns: 1.05rem 1.25rem minmax(0, 1fr) auto;\n                align-items: start;\n                gap: 0.16rem;\n                padding: 0.38rem 0.3rem;\n                border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n                color: #0f172a;\n            }}\n            .mh-memo-row.is-done {{\n                color: #94a3b8;\n                text-decoration: line-through;\n                text-decoration-thickness: 1.4px;\n            }}\n            .mh-memo-check {{ color: #22c55e; font-weight: 700; }}\n            .mh-memo-star {{ color: #f4b400; }}\n            .mh-memo-body {{\n                white-space: pre-line;\n                word-break: keep-all;\n                overflow-wrap: anywhere;\n            }}\n            .mh-memo-time {{\n                color: #2563eb;\n                font-size: 0.75rem;\n                padding-left: 0.4rem;\n                white-space: nowrap;\n            }}\n            .memo-number,\n            .mh-memo-number,\n            [data-memo-number="true"] {{\n                display: none !important;\n            }}\n            .mh-current-period,\n            tr.mh-current-period > th,\n            tr.mh-current-period > td,\n            .current-period-cell {{\n                background: #eaf2ff !important;\n            }}\n            .mh-current-period-label,\n            .current-period-label {{\n                background: #2563eb !important;\n                color: #ffffff !important;\n                font-weight: 800 !important;\n            }}\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n\n        st.markdown(\n            f"""\n            <script>\n            (function() {{\n                const currentKey = "{current_key_js}";\n                function stripMemoNumbers() {{\n                    const candidates = Array.from(document.querySelectorAll(\'div, span, p\'));\n                    const re = /^\\\\s*\\\\d+\\\\.\\\\s+/;\n                    for (const el of candidates) {{\n                        if (!el || !el.childNodes || el.childNodes.length !== 1) continue;\n                        const node = el.childNodes[0];\n                        if (!node || node.nodeType !== 3) continue;\n                        const txt = node.textContent || "";\n                        if (re.test(txt)) node.textContent = txt.replace(re, "");\n                    }}\n                }}\n                function fixCalendarButtonText() {{\n                    const btns = Array.from(document.querySelectorAll(\'button\'));\n                    for (const b of btns) {{\n                        const txt = (b.innerText || \'\').replace(/\\\\s+/g, \'\');\n                        if (txt === \'달력\') {{\n                            b.style.whiteSpace = \'nowrap\';\n                            b.style.wordBreak = \'keep-all\';\n                            b.style.minWidth = \'54px\';\n                            b.style.writingMode = \'horizontal-tb\';\n                            const p = b.querySelector(\'p\');\n                            if (p) {{\n                                p.style.whiteSpace = \'nowrap\';\n                                p.style.wordBreak = \'keep-all\';\n                                p.style.writingMode = \'horizontal-tb\';\n                            }}\n                        }}\n                    }}\n                }}\n                function markCurrentPeriod() {{\n                    if (!currentKey) return;\n                    const tables = Array.from(document.querySelectorAll(\'table\'));\n                    for (const table of tables) {{\n                        const rows = Array.from(table.querySelectorAll(\'tr\'));\n                        for (const row of rows) {{\n                            const cells = Array.from(row.children);\n                            const rowText = (row.innerText || \'\');\n                            let hit = false;\n                            if (currentKey === \'lunch\') hit = rowText.includes(\'점심\');\n                            else hit = rowText.includes(currentKey + \'교시\') || rowText.includes(currentKey + \' 교시\');\n                            if (hit) {{\n                                row.classList.add(\'mh-current-period\');\n                                if (cells.length) cells[0].classList.add(\'mh-current-period-label\');\n                            }}\n                        }}\n                    }}\n                }}\n                function tick() {{\n                    stripMemoNumbers();\n                    fixCalendarButtonText();\n                    markCurrentPeriod();\n                }}\n                tick();\n                setTimeout(tick, 250);\n                setTimeout(tick, 750);\n                setTimeout(tick, 1500);\n            }})();\n            </script>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n# [WEB_VIEWER_PC_LIKE_UI_END]\n'
CALL_CODE = '\n# [WEB_VIEWER_PC_LIKE_UI_CALL_START]\ntry:\n    _mh_inject_pc_like_web_css()\n    _mh_render_clock_badge()\nexcept Exception:\n    pass\n# [WEB_VIEWER_PC_LIKE_UI_CALL_END]\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step58_web_pc_ui_{STAMP}{path.suffix}")
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
    seen_code = False
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


def find_call_insert_index(lines):
    for i, line in enumerate(lines):
        if "st.set_page_config" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1, "after_set_page_config"

    for i, line in enumerate(lines):
        if "시간표 뷰어" in line or "명덕외고 시간표" in line:
            return i + 1, "after_title"

    return find_top_level_import_end(lines), "after_imports"


def patch_mobile_app():
    if not APP.exists():
        raise RuntimeError(f"mobile/app.py 파일이 없습니다: {APP}")

    backup(APP)

    text = APP.read_text(encoding="utf-8", errors="replace")
    original = text

    text, r1 = remove_block(text, START, END)
    text, r2 = remove_block(text, CALL_START, CALL_END)

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
        print("[완료] mobile/app.py Step58 패치 저장")
    else:
        print("[안내] 변경 없음")

    return r1, r2, call_pos


def main():
    print("==============================================")
    print("Step58 web viewer PC-like UI + clock")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    try:
        removed_helper, removed_call, call_pos = patch_mobile_app()
    except Exception as e:
        print("[오류] Step58 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    print()
    print("[완료] Step58 웹뷰어 UI 보정 적용")
    print(f"- 기존 helper 제거 후 재삽입: {removed_helper}")
    print(f"- 기존 call 제거 후 재삽입: {removed_call}")
    print(f"- 호출부 삽입 위치: {call_pos}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 메모 넘버링이 사라졌는지")
    print("2. 메모가 중요/일반/완료 구조로 보정되는지")
    print("3. 상단 버튼 영역이 균형 있게 보이고 달력 글자가 가로로 유지되는지")
    print("4. 현재시각/현재교시 배지가 보이는지")
    print("5. 현재 교시에 해당하는 시간표 행/칸이 강조되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

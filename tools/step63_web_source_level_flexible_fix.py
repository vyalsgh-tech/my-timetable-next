# tools/step63_web_source_level_flexible_fix.py
# ------------------------------------------------------------
# Step63: Step62 실패 보완판
# - 시간표 시작 html_parts.append 위치를 라인 단위로 유연하게 탐지
# - 현재시각/시간표 프레임/메모 소제목을 소스 레벨에서 직접 수정
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

OLD_BLOCK_MARKERS = [
    ("# [WEB_VIEWER_PC_LIKE_UI_START]", "# [WEB_VIEWER_PC_LIKE_UI_END]"),
    ("# [WEB_VIEWER_PC_LIKE_UI_CALL_START]", "# [WEB_VIEWER_PC_LIKE_UI_CALL_END]"),
    ("# [WEB_VERSION_MANAGEMENT_START]", "# [WEB_VERSION_MANAGEMENT_END]"),
    ("# [WEB_VERSION_BADGE_CALL_START]", "# [WEB_VERSION_BADGE_CALL_END]"),
    ("# [STEP62_HELPERS_START]", "# [STEP62_HELPERS_END]"),
    ("# [STEP62_CLOCK_CALL_START]", "# [STEP62_CLOCK_CALL_END]"),
    ("# [STEP63_HELPERS_START]", "# [STEP63_HELPERS_END]"),
    ("# [STEP63_CLOCK_CALL_START]", "# [STEP63_CLOCK_CALL_END]"),
]

CSS_MARKERS = [
    ("/* [STEP62_WEB_FINAL_CSS_START] */", "/* [STEP62_WEB_FINAL_CSS_END] */"),
    ("/* [STEP63_WEB_FINAL_CSS_START] */", "/* [STEP63_WEB_FINAL_CSS_END] */"),
]

CLOCK_CALL_START = "# [STEP63_CLOCK_CALL_START]"
CLOCK_CALL_END = "# [STEP63_CLOCK_CALL_END]"
HELPER_START = "# [STEP63_HELPERS_START]"
HELPER_END = "# [STEP63_HELPERS_END]"

HELPERS = '\n# [STEP63_HELPERS_START]\ndef mobile_current_period_info():\n    try:\n        now = datetime.now(kst_tz)\n        now_mins = now.hour * 60 + now.minute\n\n        for p_name, t_range in period_times:\n            if p_name == "학사일정":\n                continue\n            try:\n                start_str, end_str = t_range.split("\\n")\n                h1, m1 = map(int, start_str.split(":"))\n                h2, m2 = map(int, end_str.split(":"))\n            except Exception:\n                continue\n\n            s_mins = h1 * 60 + m1\n            e_mins = h2 * 60 + m2\n\n            if s_mins <= now_mins < e_mins:\n                return {\n                    "clock": now.strftime("%H:%M"),\n                    "period": p_name,\n                    "range": f"{start_str}~{end_str}",\n                }\n\n        if now_mins < 8 * 60:\n            label = "수업 전"\n        elif now_mins >= 17 * 60 + 50:\n            label = "방과 후"\n        else:\n            label = "쉬는시간"\n\n        return {"clock": now.strftime("%H:%M"), "period": label, "range": ""}\n    except Exception:\n        return {"clock": "--:--", "period": "", "range": ""}\n\n\ndef render_mobile_now_badge():\n    try:\n        info = mobile_current_period_info()\n        clock = info.get("clock", "--:--")\n        period = info.get("period", "")\n        range_text = info.get("range", "")\n        detail = period\n        if range_text:\n            detail += f" · {range_text}"\n\n        st.markdown(\n            f"""\n            <div class=\'mobile-now-row\'>\n                <span class=\'mobile-now-badge\'>\n                    <b>{clock}</b>\n                    <span>{detail}</span>\n                </span>\n            </div>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n# [STEP63_HELPERS_END]\n'
CSS = '\n/* [STEP63_WEB_FINAL_CSS_START] */\n.mobile-now-row {\n    width: 100%;\n    max-width: 450px;\n    display: flex;\n    justify-content: flex-end;\n    align-items: center;\n    margin: -2px auto 6px 0;\n    min-height: 26px;\n}\n.mobile-now-badge {\n    display: inline-flex;\n    align-items: center;\n    gap: 6px;\n    padding: 4px 10px;\n    border-radius: 999px;\n    border: 1px solid rgba(37, 99, 235, 0.24);\n    background: linear-gradient(180deg, rgba(239, 246, 255, 0.98), rgba(219, 234, 254, 0.92));\n    color: #1e3a8a;\n    font-size: 12px;\n    line-height: 1.1;\n    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.10);\n    white-space: nowrap;\n}\n.mobile-now-badge b {\n    font-size: 13px;\n}\ndiv[data-testid="stHorizontalBlock"] .stButton > button,\ndiv[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    overflow-wrap: normal !important;\n    writing-mode: horizontal-tb !important;\n}\ndiv[data-testid="stHorizontalBlock"] .stButton > button p,\ndiv[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p {\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    overflow-wrap: normal !important;\n    writing-mode: horizontal-tb !important;\n    margin: 0 !important;\n}\n.timetable-frame {\n    width: 100%;\n    max-width: 450px;\n    margin: 0 auto 12px 0;\n    background: linear-gradient(180deg, #eef5ff 0%, #dce9f8 100%);\n    border-radius: 8px;\n    padding: 5px 5px 14px 5px;\n    box-shadow:\n        0 12px 24px rgba(15, 23, 42, 0.16),\n        inset 0 1px 0 rgba(255,255,255,0.92),\n        inset 0 -1px 0 rgba(100,116,139,0.22);\n    position: relative;\n    overflow: hidden;\n}\n.timetable-scroll {\n    width: 100%;\n    overflow-x: auto;\n    border-radius: 6px;\n    background: transparent;\n    position: relative;\n    z-index: 1;\n}\n.timetable-bottom-shadow {\n    position: absolute;\n    left: 8px;\n    right: 8px;\n    bottom: 5px;\n    height: 7px;\n    border-radius: 999px;\n    background: linear-gradient(180deg, rgba(30,41,59,0.34), rgba(100,116,139,0.15));\n    box-shadow: 0 5px 9px rgba(15,23,42,0.18);\n    pointer-events: none;\n}\n.mobile-table {\n    border-collapse: collapse !important;\n    border-spacing: 0 !important;\n    border: 0 !important;\n    box-shadow:\n        0 4px 10px rgba(15,23,42,0.10),\n        0 0 0 1px rgba(30,41,59,0.88);\n    border-radius: 5px;\n    overflow: hidden;\n}\n.mobile-table th,\n.mobile-table td {\n    box-shadow: inset 0 1px 0 rgba(255,255,255,0.55);\n}\n.mobile-table td {\n    background-image: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(247,250,253,0.90));\n}\n.mobile-table th {\n    background-image: linear-gradient(180deg, rgba(229,241,255,0.98), rgba(201,223,247,0.94));\n}\n.memo-section-header {\n    padding: 5px 6px;\n    margin: 6px 0 0 0;\n    font-size: 13px;\n    font-weight: 800;\n    line-height: 1.2;\n    cursor: pointer;\n    user-select: none;\n    border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n    list-style: none;\n}\n.memo-section-header::-webkit-details-marker {\n    display: none;\n}\n.memo-section-header.important { color: #ef4444; }\n.memo-section-header.general { color: #0f172a; }\n.memo-section-header.done { color: #94a3b8; }\n.memo-group-content {\n    border-bottom: 1px solid rgba(191, 219, 254, 0.70);\n}\n.memo-row {\n    padding: 7px 6px;\n    border-bottom: 1px solid rgba(191, 219, 254, 0.75);\n    color: inherit;\n}\n.memo-row:last-child { border-bottom: 0; }\n.memo-text {\n    font-size: 14px;\n    font-weight: 700;\n    line-height: 1.35;\n    word-break: keep-all;\n    overflow-wrap: anywhere;\n    white-space: pre-line;\n}\n.memo-time {\n    font-size: 11px;\n    opacity: 0.65;\n    margin-top: 4px;\n}\n.memo-done .memo-text {\n    text-decoration: line-through;\n    text-decoration-thickness: 1.3px;\n    color: #94a3b8;\n}\n/* [STEP63_WEB_FINAL_CSS_END] */\n'
MEMO_BLOCK = '    if st.session_state.show_memo:\n        html_parts.append(\n            f"<div class=\'memo-panel\' style=\'margin-top:10px;\'>"\n            f"<h3 style=\'margin:0; font-size:15px; margin-bottom:8px; color:{t[\'text\']};\'>"\n            f"📝 {html.escape(str(st.session_state.teacher))} 메모장 "\n            f"<span style=\'font-size:11px; font-weight:normal; opacity:0.6;\'>(수정은 PC에서)</span>"\n            f"</h3><div class=\'memo-container\'>"\n        )\n\n        if memos_list:\n            important_memos = [\n                m for m in memos_list\n                if bool(m.get("is_important", False)) and not bool(m.get("is_strike", False))\n            ]\n            general_memos = [\n                m for m in memos_list\n                if not bool(m.get("is_important", False)) and not bool(m.get("is_strike", False))\n            ]\n            done_memos = [\n                m for m in memos_list\n                if bool(m.get("is_strike", False))\n            ]\n\n            def memo_time_text(memo):\n                raw_time = str(memo.get("created_at", "") or "")\n                if not raw_time:\n                    return ""\n                try:\n                    return (\n                        datetime.fromisoformat(raw_time.replace("Z", "+00:00"))\n                        .astimezone(kst_tz)\n                        .strftime("%y.%m.%d %H:%M")\n                    )\n                except Exception:\n                    return raw_time[:16]\n\n            def render_memo_group(items, title, header_class, done=False):\n                if not items:\n                    return\n\n                html_parts.append(\n                    f"<details class=\'memo-group memo-{header_class}\' open>"\n                    f"<summary class=\'memo-section-header {header_class}\'>{title} ({len(items)}) ▲</summary>"\n                    f"<div class=\'memo-group-content\'>"\n                )\n\n                for memo in items:\n                    text = str(memo.get("memo_text") or memo.get("content") or "")\n                    text = text.replace("__STRIKE__|||", "")\n                    is_imp = bool(memo.get("is_important", False))\n                    prefix = "⭐ " if is_imp else "☆ "\n                    time_str = memo_time_text(memo)\n                    row_class = "memo-row memo-done" if done else "memo-row"\n\n                    html_parts.append(\n                        f"<div class=\'{row_class}\'>"\n                        f"<div class=\'memo-text\'>{prefix}{html.escape(text).replace(chr(10), \'<br>\')}</div>"\n                        f"<div class=\'memo-time\'>{html.escape(time_str)}</div>"\n                        f"</div>"\n                    )\n\n                html_parts.append("</div></details>")\n\n            render_memo_group(important_memos, "📌 중요 메모", "important")\n            render_memo_group(general_memos, "▣ 일반 메모", "general")\n            render_memo_group(done_memos, "✔ 완료 메모", "done", done=True)\n        else:\n            html_parts.append(\n                f"<div style=\'padding:8px; color:{t[\'text\']}; opacity:0.7;\'>메모가 없습니다.</div>"\n            )\n\n        html_parts.append("</div></div>")\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step63_web_flexible_fix_{STAMP}{path.suffix}")
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
    for start, end in OLD_BLOCK_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    for start, end in CSS_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    return text, removed


def ensure_import_html(text: str):
    if re.search(r"^\s*import\s+html\b", text, re.M):
        return text, False
    for anchor in ["import re\n", "import io\n", "import os\n", "import json\n"]:
        if anchor in text:
            return text.replace(anchor, anchor + "import html\n", 1), True
    return "import html\n" + text, True


def ensure_helpers(text: str):
    marker = "def normalize_text(value):"
    pos = text.find(marker)
    if pos != -1:
        next_section = text.find("\n# =========================================================", pos + len(marker))
        if next_section != -1:
            return text[:next_section] + "\n\n" + HELPERS + text[next_section:], "after_normalize_text"

    # fallback: 첫 st.set_page_config 앞
    idx = text.find("st.set_page_config")
    if idx == -1:
        idx = 0
    return text[:idx] + HELPERS + "\n\n" + text[idx:], "before_set_page_config"


def ensure_css(text: str):
    idx = text.find("</style>")
    if idx == -1:
        raise RuntimeError("CSS </style> 위치를 찾지 못했습니다.")
    return text[:idx] + CSS + "\n" + text[idx:], True


def ensure_clock_call(text: str):
    header_idx = text.find("🏫 명덕외고 시간표 뷰어")
    if header_idx == -1:
        raise RuntimeError("헤더 '명덕외고 시간표 뷰어' 위치를 찾지 못했습니다.")
    after = text.find("unsafe_allow_html=True", header_idx)
    if after == -1:
        raise RuntimeError("헤더 st.markdown 종료 위치를 찾지 못했습니다.")
    close = text.find("\n)", after)
    if close == -1:
        raise RuntimeError("헤더 st.markdown 닫는 괄호 위치를 찾지 못했습니다.")
    insert_pos = close + 2
    call = f"\n\n{CLOCK_CALL_START}\nrender_mobile_now_badge()\n{CLOCK_CALL_END}\n"
    return text[:insert_pos] + call + text[insert_pos:], "after_header"


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


def patch_timetable_frame(text: str):
    if "class='timetable-frame'" in text or 'class="timetable-frame"' in text:
        return text, 0

    lines = text.splitlines(keepends=True)
    start_i = None
    for i, line in enumerate(lines):
        if "html_parts.append" in line and "mobile-table" in line and "<table" in line:
            start_i = i
            break

    if start_i is None:
        raise RuntimeError("시간표 시작 html_parts.append 위치를 찾지 못했습니다.")

    indent = lines[start_i][:len(lines[start_i]) - len(lines[start_i].lstrip())]
    lines[start_i] = indent + 'html_parts.append("<div class=\'timetable-frame\'><div class=\'timetable-scroll\'><table class=\'mobile-table\'>")\n'

    end_i = None
    for i in range(start_i + 1, len(lines)):
        if "html_parts.append" in lines[i] and "</table></div>" in lines[i]:
            end_i = i
            break

    if end_i is None:
        raise RuntimeError("시간표 종료 html_parts.append 위치를 찾지 못했습니다.")

    if 'timetable-bottom-shadow' not in lines[end_i]:
        lines[end_i] = lines[end_i].replace(
            "</table></div>",
            "</table></div><div class='timetable-bottom-shadow'></div></div>"
        )

    return "".join(lines), 2


def patch_memo_block(text: str):
    start = text.find("    if st.session_state.show_memo:")
    if start == -1:
        raise RuntimeError("메모 블록 시작 위치를 찾지 못했습니다.")

    end = text.find('    st.markdown("".join(html_parts)', start)
    if end == -1:
        raise RuntimeError("메모 블록 끝 st.markdown 위치를 찾지 못했습니다.")

    old = text[start:end]
    if "memo-section-header" in old and "render_memo_group" in old and "<details" in old:
        return text, 0

    return text[:start] + MEMO_BLOCK + "\n" + text[end:], 1


def remove_leftover_display_numbers(text: str):
    changed = 0
    patterns = [
        r'\n\s*for i, memo in enumerate\(memos_list\):\n\s*memo\["display_num"\] = len\(memos_list\) - i\n',
        r'\n\s*num = memo\["display_num"\]\n',
        r'<b>\{num\}\.</b>\s*',
    ]
    for pat in patterns:
        text, n = re.subn(pat, "\n", text)
        changed += n
    return text, changed


def main():
    print("==============================================")
    print("Step63 web source-level flexible fix")
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
        text, removed_old = remove_all_blocks(text)
        text, added_html = ensure_import_html(text)
        text, helper_pos = ensure_helpers(text)
        text, css_added = ensure_css(text)
        text, clock_pos = ensure_clock_call(text)
        text, button_changes = patch_button_labels(text)
        text, table_changes = patch_timetable_frame(text)
        text, memo_changes = patch_memo_block(text)
        text, leftover_changes = remove_leftover_display_numbers(text)
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
        print("[완료] Step63 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 이전 보정 블록 제거: {removed_old}")
    print(f"- import html 추가: {added_html}")
    print(f"- helper 삽입 위치: {helper_pos}")
    print(f"- CSS 삽입: {css_added}")
    print(f"- 현재시각 호출 위치: {clock_pos}")
    print(f"- 버튼 라벨 보정: {button_changes}")
    print(f"- 시간표 프레임 보정: {table_changes}")
    print(f"- 메모 블록 PC형 교체: {memo_changes}")
    print(f"- 남은 display_num 제거: {leftover_changes}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 현재시각 배지가 제목 아래, 버튼 위에 보이는지")
    print("2. 시간표 하단에 부드러운 그림자 바가 생겼는지")
    print("3. 메모장에 중요 메모 / 일반 메모 / 완료 메모 소제목이 생겼는지")
    print("4. 각 소제목 클릭 시 접힘/펼침이 되는지")
    print("5. 메모 넘버링이 계속 없는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

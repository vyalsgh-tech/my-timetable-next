# tools/step70_web_calendar_clock_memo_color_only.py
# ------------------------------------------------------------
# Step70: 웹뷰어 최소 수정
#
# 사용자가 확인한 만족 사항은 건드리지 않음:
# - 시간표 테두리/디자인 유지
# - 메모 중요/일반/완료 구조 유지
#
# 수정 사항:
# 1) 달력 글자 세로배치 방지
# 2) 현재시각 배지 복구
# 3) 메모 글자색 span 렌더링 복구
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

BLOCK_MARKERS = [
    ("# [STEP70_WEB_HEADER_MEMO_CALENDAR_START]", "# [STEP70_WEB_HEADER_MEMO_CALENDAR_END]"),
    ("# [STEP70_WEB_CALL_START]", "# [STEP70_WEB_CALL_END]"),
]

HELPERS = '\n# [STEP70_WEB_HEADER_MEMO_CALENDAR_START]\ndef step70_current_period_info():\n    """웹뷰어 현재시각/현재교시 계산."""\n    try:\n        now = datetime.now(kst_tz)\n    except Exception:\n        now = datetime.now()\n\n    periods_default = [\n        ("1교시", "08:00\\n08:50"),\n        ("2교시", "09:00\\n09:50"),\n        ("3교시", "10:00\\n10:50"),\n        ("4교시", "11:00\\n11:50"),\n        ("점심", "11:50\\n12:40"),\n        ("5교시", "12:40\\n13:30"),\n        ("6교시", "13:40\\n14:30"),\n        ("7교시", "14:40\\n15:30"),\n        ("8교시", "16:00\\n16:50"),\n        ("9교시", "17:00\\n17:50"),\n    ]\n\n    try:\n        periods = period_times\n    except Exception:\n        periods = periods_default\n\n    now_mins = now.hour * 60 + now.minute\n\n    for p_name, t_range in periods:\n        if str(p_name) == "학사일정":\n            continue\n        try:\n            start_str, end_str = str(t_range).split("\\n")\n            h1, m1 = map(int, start_str.split(":"))\n            h2, m2 = map(int, end_str.split(":"))\n        except Exception:\n            continue\n\n        s_mins = h1 * 60 + m1\n        e_mins = h2 * 60 + m2\n\n        if s_mins <= now_mins < e_mins:\n            return {\n                "clock": now.strftime("%H:%M"),\n                "period": str(p_name),\n                "range": f"{start_str}~{end_str}",\n            }\n\n    if now_mins < 8 * 60:\n        label = "수업 전"\n    elif now_mins >= 17 * 60 + 50:\n        label = "방과 후"\n    else:\n        label = "쉬는시간"\n\n    return {"clock": now.strftime("%H:%M"), "period": label, "range": ""}\n\n\ndef step70_render_header():\n    """제목과 현재시각을 같은 줄에 표시."""\n    try:\n        teacher_name = str(st.session_state.get("teacher", ""))\n    except Exception:\n        teacher_name = ""\n\n    info = step70_current_period_info()\n    clock = info.get("clock", "--:--")\n    period = info.get("period", "")\n    range_text = info.get("range", "")\n    detail = period\n    if range_text:\n        detail += f" · {range_text}"\n\n    st.markdown(\n        f"""\n        <div class="step70-title-row">\n            <div class="step70-title-main">\n                🏫 <b>명덕외고 시간표 뷰어</b>\n                <span class="step70-title-teacher">({html.escape(teacher_name)} 선생님)</span>\n            </div>\n            <div class="step70-clock-pill">\n                <span class="step70-clock-time">{html.escape(clock)}</span>\n                <span class="step70-clock-state">{html.escape(detail)}</span>\n            </div>\n        </div>\n        """,\n        unsafe_allow_html=True,\n    )\n\n\ndef step70_memo_text_html(value):\n    """메모 내용 중 안전한 색상 span만 실제 HTML로 렌더링하고 나머지는 escape."""\n    import re as _re\n    import html as _html\n\n    s = str(value or "").replace("__STRIKE__|||", "")\n    placeholders = {}\n\n    def _safe_span(match):\n        style = (match.group(1) or "").strip()\n        inner = match.group(2) or ""\n\n        # color:#e74c3c / background-color:#fff59d 정도만 허용\n        ok_style = _re.fullmatch(\n            r"\\s*(color|background-color)\\s*:\\s*#[0-9a-fA-F]{3,6}\\s*;?\\s*",\n            style,\n            flags=_re.I,\n        )\n        if not ok_style:\n            return _html.escape(match.group(0))\n\n        key = f"__STEP70_SPAN_{len(placeholders)}__"\n        safe_style = _html.escape(style, quote=True)\n        safe_inner = step70_memo_text_html(inner)\n        placeholders[key] = f"<span style=\\"{safe_style}\\">{safe_inner}</span>"\n        return key\n\n    # 먼저 허용 가능한 span을 placeholder로 바꾼 뒤 나머지를 escape\n    s = _re.sub(\n        r"<span\\s+style=[\\"\']([^\\"\']+)[\\"\']>(.*?)</span>",\n        _safe_span,\n        s,\n        flags=_re.I | _re.S,\n    )\n\n    escaped = _html.escape(s).replace("\\n", "<br>")\n    for key, html_value in placeholders.items():\n        escaped = escaped.replace(key, html_value)\n    return escaped\n\n\ndef step70_inject_css():\n    """달력 세로배치/현재시각/메모 색상 표시용 CSS. 시간표 디자인은 현재 만족 상태를 유지."""\n    try:\n        st.markdown(\n            """\n            <style>\n            /* [STEP70_WEB_CSS_START] */\n\n            .step70-title-row {\n                width: min(450px, 100%);\n                display: flex;\n                align-items: center;\n                justify-content: space-between;\n                gap: 8px;\n                margin: 0 0 8px 0;\n            }\n            .step70-title-main {\n                flex: 1 1 auto;\n                min-width: 0;\n                color: #0f172a;\n                font-size: 16px;\n                line-height: 1.2;\n                white-space: nowrap;\n                overflow: hidden;\n                text-overflow: ellipsis;\n            }\n            .step70-title-main b {\n                font-weight: 800;\n            }\n            .step70-title-teacher {\n                font-size: 12px;\n                font-weight: 500;\n                color: #334155;\n                margin-left: 2px;\n            }\n            .step70-clock-pill {\n                flex: 0 0 auto;\n                display: inline-flex;\n                align-items: center;\n                gap: 5px;\n                padding: 4px 9px;\n                border-radius: 999px;\n                border: 1px solid rgba(96, 165, 250, 0.34);\n                background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));\n                color: #1e40af;\n                box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);\n                white-space: nowrap;\n            }\n            .step70-clock-time {\n                font-size: 13px;\n                font-weight: 800;\n            }\n            .step70-clock-state {\n                font-size: 12px;\n                opacity: 0.92;\n            }\n\n            /* 상단 버튼 및 달력 드롭다운 세로배치 방지 */\n            div[data-testid="stHorizontalBlock"] .stButton > button,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],\n            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],\n            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div {\n                min-width: 56px !important;\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button p,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p,\n            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] * {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n\n            @media (max-width: 430px) {\n                .step70-title-main {\n                    font-size: 15px;\n                }\n                .step70-title-teacher {\n                    display: none;\n                }\n                .step70-clock-pill {\n                    padding: 4px 8px;\n                }\n                .step70-clock-state {\n                    display: none;\n                }\n            }\n            /* [STEP70_WEB_CSS_END] */\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n# [STEP70_WEB_HEADER_MEMO_CALENDAR_END]\n'
MEMO_BLOCK = '    if st.session_state.show_memo:\n        html_parts.append(\n            f"<div class=\'memo-panel\' style=\'margin-top:10px;\'>"\n            f"<h3 style=\'margin:0; font-size:15px; margin-bottom:8px; color:{t[\'text\']};\'>"\n            f"📝 {html.escape(str(st.session_state.teacher))} 메모장 "\n            f"<span style=\'font-size:11px; font-weight:normal; opacity:0.6;\'>(수정은 PC에서)</span>"\n            f"</h3><div class=\'memo-container step69-grouped\'>"\n        )\n\n        if memos_list:\n            def is_done_memo(memo):\n                return bool(\n                    memo.get("is_strike", False)\n                    or memo.get("is_done", False)\n                    or memo.get("done", False)\n                    or memo.get("completed", False)\n                )\n\n            important_memos = [\n                m for m in memos_list\n                if bool(m.get("is_important", False)) and not is_done_memo(m)\n            ]\n            general_memos = [\n                m for m in memos_list\n                if not bool(m.get("is_important", False)) and not is_done_memo(m)\n            ]\n            done_memos = [\n                m for m in memos_list\n                if is_done_memo(m)\n            ]\n\n            def memo_time_text(memo):\n                raw_time = str(memo.get("created_at", "") or "")\n                if not raw_time:\n                    return ""\n                try:\n                    return (\n                        datetime.fromisoformat(raw_time.replace("Z", "+00:00"))\n                        .astimezone(kst_tz)\n                        .strftime("%y.%m.%d %H:%M")\n                    )\n                except Exception:\n                    return raw_time[:16]\n\n            def memo_text_value(memo):\n                return str(\n                    memo.get("memo_text")\n                    or memo.get("content")\n                    or memo.get("text")\n                    or ""\n                ).replace("__STRIKE__|||", "")\n\n            def render_memo_group(items, title, header_class, done=False):\n                if not items:\n                    return\n\n                html_parts.append(\n                    f"<details class=\'step69-memo-section\' open>"\n                    f"<summary class=\'step69-memo-summary {header_class}\'>{title} ({len(items)}) ▲</summary>"\n                    f"<div class=\'step69-memo-body\'>"\n                )\n\n                for memo in items:\n                    text = memo_text_value(memo)\n                    is_imp = bool(memo.get("is_important", False))\n                    prefix = "⭐ " if is_imp else "☆ "\n                    if done:\n                        prefix = "✔ " + prefix\n                    time_str = memo_time_text(memo)\n                    row_class = "step69-memo-row done" if done else "step69-memo-row"\n\n                    html_parts.append(\n                        f"<div class=\'{row_class}\'>"\n                        f"<div>{prefix}{step70_memo_text_html(text)}</div>"\n                        f"<div style=\'font-size:11px; opacity:0.62; margin-top:4px;\'>{html.escape(time_str)}</div>"\n                        f"</div>"\n                    )\n\n                html_parts.append("</div></details>")\n\n            render_memo_group(important_memos, "📌 중요 메모", "important")\n            render_memo_group(general_memos, "▣ 일반 메모", "general")\n            render_memo_group(done_memos, "✔ 완료 메모", "done", done=True)\n        else:\n            html_parts.append(\n                f"<div style=\'padding:8px; color:{t[\'text\']}; opacity:0.7;\'>메모가 없습니다.</div>"\n            )\n\n        html_parts.append("</div></div>")\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step70_web_calendar_clock_memo_color_only_{STAMP}{path.suffix}")
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


def remove_step70_blocks(text: str):
    removed = 0
    for start, end in BLOCK_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1

    # 단독 호출 제거
    lines = []
    removed_calls = 0
    for line in text.splitlines():
        if line.strip() in {"step70_inject_css()", "step70_render_header()"}:
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
        else:
            text = "import html\n" + text
            added.append("html")
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
    start, _ = find_set_page_config_range(lines)
    idx = start if start is not None else 0
    lines[idx:idx] = HELPERS.strip("\n").splitlines()
    return "\n".join(lines) + "\n", idx


def insert_css_call_after_set_page_config(text: str):
    lines = text.splitlines()
    _, end = find_set_page_config_range(lines)
    idx = end if end is not None else 0
    call = [
        "# [STEP70_WEB_CALL_START]",
        "step70_inject_css()",
        "# [STEP70_WEB_CALL_END]",
    ]
    lines[idx:idx] = call
    return "\n".join(lines) + "\n", idx


def replace_header_block(text: str):
    marker = "명덕외고 시간표 뷰어"
    lines = text.splitlines()
    marker_i = None
    for i, line in enumerate(lines):
        if marker in line:
            marker_i = i
            break
    if marker_i is None:
        return text, False

    # 이미 step70 헤더라면 OK
    if any("step70_render_header()" in line for line in lines[max(0, marker_i - 5):marker_i + 5]):
        return text, True

    start_i = None
    for i in range(marker_i, -1, -1):
        if "st.markdown(" in lines[i]:
            start_i = i
            break
    if start_i is None:
        return text, False

    end_i = None
    for i in range(marker_i, min(len(lines), marker_i + 100)):
        if "unsafe_allow_html=True" in lines[i]:
            end_i = i
            for j in range(i, min(len(lines), i + 10)):
                if lines[j].strip() == ")":
                    end_i = j
                    break
            break

    if end_i is None:
        return text, False

    indent = lines[start_i][:len(lines[start_i]) - len(lines[start_i].lstrip())]
    lines[start_i:end_i + 1] = [indent + "step70_render_header()"]
    return "\n".join(lines) + "\n", True


def replace_memo_block_only_for_color(text: str):
    # 기존 step69 메모 그룹 구조를 유지하되, text 렌더링만 step70_memo_text_html 사용하도록 전체 블록 재삽입
    start = text.find("    if st.session_state.show_memo:")
    if start == -1:
        return text, False

    end = text.find('    st.markdown("".join(html_parts)', start)
    if end == -1:
        return text, False

    return text[:start] + MEMO_BLOCK + "\n" + text[end:], True


def patch_calendar_labels(text: str):
    changed = 0
    replacements = [
        ('"달\\n력"', '"달력"'),
        ("'달\\n력'", "'달력'"),
        ('"달\n력"', '"달력"'),
        ("'달\n력'", "'달력'"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed += 1
    return text, changed


def main():
    print("====================================================")
    print("Step70 web calendar/clock/memo color only")
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
        text, removed_blocks, removed_calls = remove_step70_blocks(text)
        text, added_imports = ensure_imports(text)
        text, calendar_changes = patch_calendar_labels(text)
        text, helper_idx = insert_helpers_before_set_page_config(text)
        text, css_idx = insert_css_call_after_set_page_config(text)
        text, header_ok = replace_header_block(text)
        text, memo_ok = replace_memo_block_only_for_color(text)
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
        print("[완료] Step70 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- Step70 기존 블록 제거: {removed_blocks}")
    print(f"- Step70 단독 호출 제거: {removed_calls}")
    print(f"- 추가 import: {added_imports}")
    print(f"- 달력 문자열 보정: {calendar_changes}")
    print(f"- helper 삽입 위치 index: {helper_idx}")
    print(f"- CSS 호출 위치 index: {css_idx}")
    print(f"- 현재시각 헤더 교체 성공: {header_ok}")
    print(f"- 메모 색상 렌더링 블록 교체 성공: {memo_ok}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 달력 글자가 가로로 보이는지")
    print("2. 제목 오른쪽에 현재시각이 보이는지")
    print("3. 글자색 span 메모가 실제 색상으로 보이는지")
    print("4. 시간표 디자인은 기존 만족 상태 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

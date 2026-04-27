# tools/step73_stable_repair_calendar_clock_color.py
# ------------------------------------------------------------
# Step73: Step71/72 실패 복구 + 달력/현재시각/메모색상 최소 수정
#
# 핵심:
# - 깨진 app.py이면 컴파일 가능한 백업으로 먼저 복구
# - 이전 step70/71/72 잔여 블록 제거
# - 시간표 디자인은 건드리지 않음
# - 실제 화면 제목만 교체하도록 set_page_config 이후에서만 탐색
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
    ("# [STEP71_WEB_MINIMAL_FIX_START]", "# [STEP71_WEB_MINIMAL_FIX_END]"),
    ("# [STEP71_WEB_CALL_START]", "# [STEP71_WEB_CALL_END]"),
    ("# [STEP71_WEB_POSTPROCESS_START]", "# [STEP71_WEB_POSTPROCESS_END]"),
    ("# [STEP72_WEB_MINIMAL_REPAIR_START]", "# [STEP72_WEB_MINIMAL_REPAIR_END]"),
    ("# [STEP72_WEB_CALL_START]", "# [STEP72_WEB_CALL_END]"),
    ("# [STEP72_WEB_POSTPROCESS_START]", "# [STEP72_WEB_POSTPROCESS_END]"),
    ("# [STEP73_WEB_MINIMAL_STABLE_START]", "# [STEP73_WEB_MINIMAL_STABLE_END]"),
    ("# [STEP73_WEB_CALL_START]", "# [STEP73_WEB_CALL_END]"),
    ("# [STEP73_WEB_POSTPROCESS_START]", "# [STEP73_WEB_POSTPROCESS_END]"),
]

HELPER = '\n# [STEP73_WEB_MINIMAL_STABLE_START]\ndef step73_current_period_info():\n    """웹뷰어 현재시각/현재교시 계산."""\n    try:\n        now = datetime.now(kst_tz)\n    except Exception:\n        now = datetime.now()\n\n    periods_default = [\n        ("1교시", "08:00\\n08:50"),\n        ("2교시", "09:00\\n09:50"),\n        ("3교시", "10:00\\n10:50"),\n        ("4교시", "11:00\\n11:50"),\n        ("점심", "11:50\\n12:40"),\n        ("5교시", "12:40\\n13:30"),\n        ("6교시", "13:40\\n14:30"),\n        ("7교시", "14:40\\n15:30"),\n        ("8교시", "16:00\\n16:50"),\n        ("9교시", "17:00\\n17:50"),\n    ]\n\n    try:\n        periods = period_times\n    except Exception:\n        periods = periods_default\n\n    now_mins = now.hour * 60 + now.minute\n    for p_name, t_range in periods:\n        if str(p_name) == "학사일정":\n            continue\n        try:\n            start_str, end_str = str(t_range).split("\\n")\n            h1, m1 = map(int, start_str.split(":"))\n            h2, m2 = map(int, end_str.split(":"))\n        except Exception:\n            continue\n\n        s_mins = h1 * 60 + m1\n        e_mins = h2 * 60 + m2\n        if s_mins <= now_mins < e_mins:\n            return {\n                "clock": now.strftime("%H:%M"),\n                "period": str(p_name),\n                "range": f"{start_str}~{end_str}",\n            }\n\n    if now_mins < 8 * 60:\n        label = "수업 전"\n    elif now_mins >= 17 * 60 + 50:\n        label = "방과 후"\n    else:\n        label = "쉬는시간"\n\n    return {"clock": now.strftime("%H:%M"), "period": label, "range": ""}\n\n\ndef step73_render_header():\n    """기존 제목 위치에 현재시각 배지를 함께 표시."""\n    try:\n        teacher_name = str(st.session_state.get("teacher", ""))\n    except Exception:\n        teacher_name = ""\n\n    info = step73_current_period_info()\n    clock = info.get("clock", "--:--")\n    period = info.get("period", "")\n    range_text = info.get("range", "")\n\n    detail = period\n    if range_text:\n        detail += f" · {range_text}"\n\n    st.markdown(\n        f"""\n        <div class="step73-title-row">\n            <div class="step73-title-main">\n                🏫 <b>명덕외고 시간표 뷰어</b>\n                <span class="step73-title-teacher">({html.escape(teacher_name)} 선생님)</span>\n            </div>\n            <div class="step73-clock-pill">\n                <span class="step73-clock-time">{html.escape(clock)}</span>\n                <span class="step73-clock-state">{html.escape(detail)}</span>\n            </div>\n        </div>\n        """,\n        unsafe_allow_html=True,\n    )\n\n\ndef step73_memo_text_html(value):\n    """메모 내용 중 안전한 색상/하이라이트 span만 HTML로 살리고 나머지는 escape."""\n    import re as _re\n    import html as _html\n\n    s = str(value or "").replace("__STRIKE__|||", "")\n    placeholders = {}\n\n    def _safe_span(match):\n        style = (match.group(1) or "").strip()\n        inner = match.group(2) or ""\n\n        ok_style = _re.fullmatch(\n            r"\\s*(color|background-color)\\s*:\\s*#[0-9a-fA-F]{3,6}\\s*;?\\s*",\n            style,\n            flags=_re.I,\n        )\n        if not ok_style:\n            return _html.escape(match.group(0))\n\n        key = f"__STEP73_SPAN_{len(placeholders)}__"\n        safe_style = _html.escape(style, quote=True)\n        safe_inner = step73_memo_text_html(inner)\n        placeholders[key] = f"<span style=\\"{safe_style}\\">{safe_inner}</span>"\n        return key\n\n    s = _re.sub(\n        r"<span\\s+style=[\\"\']([^\\"\']+)[\\"\']>(.*?)</span>",\n        _safe_span,\n        s,\n        flags=_re.I | _re.S,\n    )\n\n    escaped = _html.escape(s).replace("\\n", "<br>")\n    for key, html_value in placeholders.items():\n        escaped = escaped.replace(key, html_value)\n    return escaped\n\n\ndef step73_inject_css():\n    """달력 세로배치 방지 + 현재시각 배지 CSS. 시간표 디자인은 현재 상태 유지."""\n    try:\n        st.markdown(\n            """\n            <style>\n            /* [STEP73_WEB_CSS_START] */\n            .step73-title-row {\n                width: min(450px, 100%);\n                display: flex;\n                align-items: center;\n                justify-content: space-between;\n                gap: 8px;\n                margin: 0 0 8px 0;\n            }\n            .step73-title-main {\n                flex: 1 1 auto;\n                min-width: 0;\n                color: #0f172a;\n                font-size: 16px;\n                line-height: 1.2;\n                white-space: nowrap;\n                overflow: hidden;\n                text-overflow: ellipsis;\n            }\n            .step73-title-main b {\n                font-weight: 800;\n            }\n            .step73-title-teacher {\n                font-size: 12px;\n                font-weight: 500;\n                color: #334155;\n                margin-left: 2px;\n            }\n            .step73-clock-pill {\n                flex: 0 0 auto;\n                display: inline-flex;\n                align-items: center;\n                gap: 5px;\n                padding: 4px 9px;\n                border-radius: 999px;\n                border: 1px solid rgba(96, 165, 250, 0.34);\n                background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));\n                color: #1e40af;\n                box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);\n                white-space: nowrap;\n            }\n            .step73-clock-time {\n                font-size: 13px;\n                font-weight: 800;\n            }\n            .step73-clock-state {\n                font-size: 12px;\n                opacity: 0.92;\n            }\n\n            /* 달력 세로배치 방지: column 폭까지 강제 */\n            div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-baseweb="select"]),\n            div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-testid="stSelectbox"]) {\n                min-width: 72px !important;\n                width: 72px !important;\n                flex: 0 0 72px !important;\n            }\n            div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],\n            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],\n            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div,\n            div[data-testid="stHorizontalBlock"] div[role="button"] {\n                min-width: 68px !important;\n                width: 68px !important;\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n            div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] *,\n            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] *,\n            div[data-testid="stHorizontalBlock"] div[role="button"] * {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n                line-height: 1.1 !important;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button,\n            div[data-testid="stHorizontalBlock"] button {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n            div[data-testid="stHorizontalBlock"] .stButton > button p,\n            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p,\n            div[data-testid="stHorizontalBlock"] button * {\n                white-space: nowrap !important;\n                word-break: keep-all !important;\n                overflow-wrap: normal !important;\n                writing-mode: horizontal-tb !important;\n            }\n\n            @media (max-width: 430px) {\n                .step73-title-main {\n                    font-size: 15px;\n                }\n                .step73-title-teacher {\n                    display: none;\n                }\n                .step73-clock-pill {\n                    padding: 4px 8px;\n                }\n                .step73-clock-state {\n                    display: none;\n                }\n            }\n            /* [STEP73_WEB_CSS_END] */\n            </style>\n            """,\n            unsafe_allow_html=True,\n        )\n    except Exception:\n        pass\n\n\ndef step73_postprocess_component():\n    """달력 selectbox가 좁은 column에 갇힌 경우 JS로 한 번 더 보정."""\n    try:\n        import streamlit.components.v1 as components\n        components.html(\n            """\n            <script>\n            (function() {\n                function docRoot() {\n                    try { return window.parent.document; } catch(e) { return document; }\n                }\n                function fixCalendar() {\n                    const doc = docRoot();\n                    const nodes = Array.from(doc.querySelectorAll(\'button, [data-testid="stSelectbox"], [data-baseweb="select"], div[role="button"], span, div\'));\n                    const targets = nodes.filter(el => {\n                        const txt = (el.innerText || el.textContent || \'\').trim();\n                        return /^달\\s*력$/.test(txt);\n                    });\n\n                    for (const el of targets) {\n                        if ((el.innerText || \'\').includes(\'\\n\')) el.innerText = \'달력\';\n\n                        let cur = el;\n                        for (let i = 0; i < 10 && cur; i++, cur = cur.parentElement) {\n                            cur.style.setProperty(\'white-space\', \'nowrap\', \'important\');\n                            cur.style.setProperty(\'word-break\', \'keep-all\', \'important\');\n                            cur.style.setProperty(\'overflow-wrap\', \'normal\', \'important\');\n                            cur.style.setProperty(\'writing-mode\', \'horizontal-tb\', \'important\');\n\n                            const txt = (cur.innerText || \'\').trim();\n                            if (/달\\s*력/.test(txt) && txt.length <= 12) {\n                                cur.style.setProperty(\'min-width\', \'72px\', \'important\');\n                                cur.style.setProperty(\'width\', \'72px\', \'important\');\n                                cur.style.setProperty(\'flex\', \'0 0 72px\', \'important\');\n                            }\n                            if (cur.getAttribute && cur.getAttribute(\'data-testid\') === \'stHorizontalBlock\') break;\n                        }\n                    }\n                }\n                fixCalendar();\n                setTimeout(fixCalendar, 200);\n                setTimeout(fixCalendar, 700);\n                setTimeout(fixCalendar, 1400);\n                setTimeout(fixCalendar, 2200);\n            })();\n            </script>\n            """,\n            height=1,\n            width=1,\n        )\n    except Exception:\n        pass\n# [STEP73_WEB_MINIMAL_STABLE_END]\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step73_stable_repair_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def compiles(text: str, name: str = "app.py"):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def choose_base_text(raw: str):
    ok, err = compiles(raw, str(APP))
    if ok:
        return raw, None

    print(f"[경고] 현재 app.py 문법 오류 감지: {err}")
    patterns = [
        "app_before_step70*.py",
        "app_before_step69*.py",
        "app_before_step68*.py",
        "app_before_step67*.py",
        "app_before_step66*.py",
        "app_before_step65*.py",
        "app_before_step64*.py",
        "app_before_step63*.py",
        "app_before_step62*.py",
        "app_before_step71*.py",
        "app_before_step72*.py",
    ]
    candidates = []
    for pat in patterns:
        candidates.extend(APP.parent.glob(pat))

    # 최신순, 단 패턴 우선순위는 위 순서대로 이미 섞였으므로 정렬만
    candidates = sorted(set(candidates), key=lambda p: p.stat().st_mtime, reverse=True)

    for b in candidates:
        text = b.read_text(encoding="utf-8", errors="replace")
        ok, _ = compiles(text, str(b))
        if ok:
            print(f"[복구] 컴파일 가능한 백업 사용: {b}")
            return text, b

    raise RuntimeError("현재 app.py가 깨져 있고, 컴파일 가능한 백업을 찾지 못했습니다.")


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
    for start, end in BLOCK_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1

    bad_calls = {
        "step70_inject_css()",
        "step70_render_header()",
        "step70_postprocess_component()",
        "step71_inject_css()",
        "step71_render_header()",
        "step71_postprocess_component()",
        "step72_inject_css()",
        "step72_render_header()",
        "step72_postprocess_component()",
        "step73_inject_css()",
        "step73_render_header()",
        "step73_postprocess_component()",
    }
    lines = []
    removed_calls = 0
    for line in text.splitlines():
        if line.strip() in bad_calls:
            removed_calls += 1
            continue
        lines.append(line)
    return "\n".join(lines) + "\n", removed, removed_calls


def ensure_import_html(text: str):
    added = False
    if not re.search(r"^\s*import\s+html\b", text, re.M):
        for anchor in ["import re\n", "import io\n", "import os\n", "import json\n"]:
            if anchor in text:
                text = text.replace(anchor, anchor + "import html\n", 1)
                added = True
                break
        else:
            text = "import html\n" + text
            added = True
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


def insert_helper_before_set_page_config(text: str):
    lines = text.splitlines()
    start, _ = find_set_page_config_range(lines)
    idx = start if start is not None else 0
    lines[idx:idx] = HELPER.strip("\n").splitlines()
    return "\n".join(lines) + "\n", idx


def insert_css_after_set_page_config(text: str):
    lines = text.splitlines()
    _, end = find_set_page_config_range(lines)
    idx = end if end is not None else 0
    call = [
        "# [STEP73_WEB_CALL_START]",
        "step73_inject_css()",
        "# [STEP73_WEB_CALL_END]",
    ]
    lines[idx:idx] = call
    return "\n".join(lines) + "\n", idx


def replace_header_after_set_page_config(text: str):
    lines = text.splitlines()
    _, config_end = find_set_page_config_range(lines)
    search_start = config_end or 0

    # 기존 step69 header call이면 그 줄만 교체
    for i in range(search_start, len(lines)):
        if "step69_render_header()" in lines[i]:
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            lines[i] = indent + "step73_render_header()"
            return "\n".join(lines) + "\n", "replaced_step69_call"

    marker = "명덕외고 시간표 뷰어"
    marker_i = None
    for i in range(search_start, len(lines)):
        if marker in lines[i]:
            marker_i = i
            break

    if marker_i is None:
        lines.insert(search_start, "step73_render_header()")
        return "\n".join(lines) + "\n", "inserted_after_config_no_marker"

    start_i = None
    for i in range(marker_i, search_start - 1, -1):
        if "st.markdown(" in lines[i]:
            start_i = i
            break

    if start_i is None:
        lines.insert(marker_i, "step73_render_header()")
        return "\n".join(lines) + "\n", "inserted_before_title"

    end_i = None
    for i in range(marker_i, min(len(lines), marker_i + 100)):
        if "unsafe_allow_html=True" in lines[i]:
            end_i = i
            for j in range(i, min(len(lines), i + 12)):
                if lines[j].strip() == ")":
                    end_i = j
                    break
            break

    if end_i is None:
        end_i = start_i

    indent = lines[start_i][:len(lines[start_i]) - len(lines[start_i].lstrip())]
    lines[start_i:end_i + 1] = [indent + "step73_render_header()"]
    return "\n".join(lines) + "\n", "replaced_title_block"


def patch_calendar_literals(text: str):
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


def patch_memo_color(text: str):
    changed = 0
    replacements = [
        ("step72_memo_text_html(text)", "step73_memo_text_html(text)"),
        ("step71_memo_text_html(text)", "step73_memo_text_html(text)"),
        ("step70_memo_text_html(text)", "step73_memo_text_html(text)"),
        ("html.escape(text).replace(chr(10), '<br>')", "step73_memo_text_html(text)"),
        ('html.escape(text).replace(chr(10), "<br>")', "step73_memo_text_html(text)"),
        ("html.escape(memo_text).replace(chr(10), '<br>')", "step73_memo_text_html(memo_text)"),
        ('html.escape(memo_text).replace(chr(10), "<br>")', "step73_memo_text_html(memo_text)"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed += 1

    text, n = re.subn(
        r"html\.escape\((text|memo_text|memo_content|content)\)\.replace\(['\"]\\n['\"],\s*['\"]<br>['\"]\)",
        r"step73_memo_text_html(\1)",
        text,
    )
    changed += n
    return text, changed


def find_html_render_insert_index(lines):
    for i, line in enumerate(lines):
        if "st.markdown" in line and "html_parts" in line:
            bal = line.count("(") - line.count(")")
            j = i
            while bal > 0 and j + 1 < len(lines):
                j += 1
                bal += lines[j].count("(") - lines[j].count(")")
            return j + 1
    return len(lines)


def insert_postprocess(text: str):
    lines = text.splitlines()
    idx = find_html_render_insert_index(lines)
    call = [
        "# [STEP73_WEB_POSTPROCESS_START]",
        "step73_postprocess_component()",
        "# [STEP73_WEB_POSTPROCESS_END]",
    ]
    lines[idx:idx] = call
    return "\n".join(lines) + "\n", idx


def main():
    print("====================================================")
    print("Step73 stable repair calendar/clock/color")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup(APP)
    raw = APP.read_text(encoding="utf-8", errors="replace")

    try:
        base, restored_from = choose_base_text(raw)
        text, removed_blocks, removed_calls = remove_old_blocks(base)
        text, added_html = ensure_import_html(text)
        text, calendar_literals = patch_calendar_literals(text)
        text, memo_color_changes = patch_memo_color(text)
        text, header_mode = replace_header_after_set_page_config(text)
        text, helper_idx = insert_helper_before_set_page_config(text)
        text, css_idx = insert_css_after_set_page_config(text)
        text, post_idx = insert_postprocess(text)
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] mobile/app.py 문법 확인 실패")
        print(err)
        print("패치를 저장하지 않습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    APP.write_text(text, encoding="utf-8")
    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step73 패치 저장")

    print()
    print("[변경 요약]")
    print(f"- 복구 백업 사용: {restored_from}")
    print(f"- Step70/71/72/73 기존 블록 제거: {removed_blocks}")
    print(f"- 단독 호출 제거: {removed_calls}")
    print(f"- import html 추가: {added_html}")
    print(f"- 달력 문자열 보정: {calendar_literals}")
    print(f"- 메모 색상 렌더링 교체: {memo_color_changes}")
    print(f"- 제목/시각 처리: {header_mode}")
    print(f"- helper 삽입 위치 index: {helper_idx}")
    print(f"- CSS 호출 위치 index: {css_idx}")
    print(f"- 달력 JS 후처리 위치 index: {post_idx}")
    print()
    print("확인:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 달력 글자가 가로로 보이는지")
    print("2. 제목 오른쪽에 현재시각이 보이는지")
    print("3. 글자색 span 메모가 실제 색상으로 보이는지")
    print("4. 시간표 디자인은 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

import streamlit as st
import streamlit.components.v1 as components
import requests
import csv
import os
from pathlib import Path
import inspect
import threading
import re
import html
import io
import glob
from datetime import datetime, timedelta, timezone
# ============================================================
# Step89: Supabase SSL fallback for school/institution network
# - 일반 환경에서는 기존 SSL 검증을 유지합니다.
# - Supabase 요청에서 SSL 인증서 오류가 날 때만 verify=False로 1회 재시도합니다.
# ============================================================
try:
    import requests
    from requests.exceptions import SSLError

    if not hasattr(requests.Session, "_request_with_supabase_ssl_fallback_step89"):
        _original_requests_session_request_step89 = requests.Session.request

        def _request_with_supabase_ssl_fallback_step89(self, method, url, **kwargs):
            try:
                return _original_requests_session_request_step89(self, method, url, **kwargs)
            except SSLError:
                url_text = str(url)
                if "supabase.co" in url_text and kwargs.get("verify", True) is not False:
                    try:
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    except Exception:
                        pass
                    kwargs["verify"] = False
                    return _original_requests_session_request_step89(self, method, url, **kwargs)
                raise

        requests.Session.request = _request_with_supabase_ssl_fallback_step89
        requests.Session._request_with_supabase_ssl_fallback_step89 = True
except Exception:
    pass
# ============================================================

# =========================================================
# 1. 페이지 설정
# =========================================================
# [STEP69_WEB_HELPERS_START]
def step69_current_period_info():
    """웹뷰어 현재시각/현재교시 계산."""
    try:
        now = datetime.now(kst_tz)
    except Exception:
        now = datetime.now()

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
            return {
                "clock": now.strftime("%H:%M"),
                "period": str(p_name),
                "range": f"{start_str}~{end_str}",
            }

    if now_mins < 8 * 60:
        label = "수업 전"
    elif now_mins >= 17 * 60 + 50:
        label = "방과 후"
    else:
        label = "쉬는시간"

    return {"clock": now.strftime("%H:%M"), "period": label, "range": ""}


def step69_render_header():
    """제목과 현재시각을 같은 줄에 표시."""
    try:
        teacher_name = str(st.session_state.get("teacher", ""))
    except Exception:
        teacher_name = ""

    try:
        info = step69_current_period_info()
        clock = info.get("clock", "--:--")
        period = info.get("period", "")
        range_text = info.get("range", "")
        detail = period
        if range_text:
            detail += f" · {range_text}"

        step69_render_header()
    except Exception:
        step70_render_header()


def step69_inject_css():
    """웹뷰어 최종 정리 CSS."""
    try:
        st.markdown(
            """
            <style>
            /* [STEP69_WEB_CSS_START] */
            .step69-title-row {
                width: min(450px, 100%);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin: 0 0 8px 0;
            }
            .step69-title-main {
                flex: 1 1 auto;
                min-width: 0;
                color: #0f172a;
                font-size: 16px;
                line-height: 1.2;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .step69-title-main b { font-weight: 800; }
            .step69-title-teacher {
                font-size: 12px;
                font-weight: 500;
                color: #334155;
                margin-left: 2px;
            }
            .step69-clock-pill {
                flex: 0 0 auto;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 4px 9px;
                border-radius: 999px;
                border: 1px solid rgba(96, 165, 250, 0.34);
                background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));
                color: #1e40af;
                box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);
                white-space: nowrap;
            }
            .step69-clock-time {
                font-size: 13px;
                font-weight: 800;
            }
            .step69-clock-state {
                font-size: 12px;
                opacity: 0.92;
            }

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

            div:has(> table.mobile-table) {
                width: min(450px, 100%) !important;
                padding: 5px !important;
                margin: 0 0 14px 0 !important;
                border-radius: 8px !important;
                background: linear-gradient(180deg, #eef5ff 0%, #dfeafa 100%) !important;
                box-shadow: 0 6px 16px rgba(15,23,42,0.10), 0 1px 4px rgba(15,23,42,0.06) !important;
                overflow-x: auto !important;
                overflow-y: visible !important;
            }
            .mobile-table {
                margin: 0 !important;
                border-collapse: collapse !important;
                border-spacing: 0 !important;
                border: 1px solid #1f2937 !important;
                background: #ffffff !important;
                box-shadow: none !important;
                border-radius: 0 !important;
            }
            .mobile-table th,
            .mobile-table td {
                border-color: #1f2937 !important;
                box-shadow: none !important;
            }
            .mobile-table th {
                background-image: linear-gradient(180deg, #eaf3ff 0%, #d7e6f8 100%) !important;
            }
            .mobile-table td {
                background-image: linear-gradient(180deg, #ffffff 0%, #fafcff 100%) !important;
            }
            .timetable-frame,
            .step68-table-card,
            .step68-table-scroll,
            .timetable-scroll {
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin: 0 !important;
                overflow: visible !important;
            }
            .timetable-bottom-shadow { display: none !important; }

            .memo-container.step69-grouped {
                border: 1px solid rgba(191, 219, 254, 0.85);
                border-radius: 8px;
                background: rgba(248,251,255,0.82);
                overflow-y: auto;
                max-height: 410px;
            }
            .step69-memo-section {
                margin: 0;
                border-bottom: 1px solid rgba(191,219,254,0.78);
            }
            .step69-memo-section:last-child { border-bottom: 0; }
            .step69-memo-summary {
                padding: 7px 8px 6px 8px;
                font-size: 13px;
                font-weight: 800;
                line-height: 1.2;
                cursor: pointer;
                user-select: none;
                list-style: none;
                background: rgba(239,246,255,0.52);
                border-bottom: 1px solid rgba(191,219,254,0.72);
            }
            .step69-memo-summary::-webkit-details-marker { display: none; }
            .step69-memo-summary.important { color: #ef4444; }
            .step69-memo-summary.general { color: #0f172a; }
            .step69-memo-summary.done { color: #94a3b8; }
            .step69-memo-row {
                padding: 8px 8px !important;
                border-bottom: 1px solid rgba(191,219,254,0.72) !important;
                min-height: 34px;
                word-break: keep-all;
                overflow-wrap: anywhere;
                background: transparent;
            }
            .step69-memo-row:last-child { border-bottom: 0 !important; }
            .step69-memo-row.done,
            .step69-memo-row.done * {
                text-decoration: line-through !important;
                text-decoration-thickness: 1.15px !important;
                text-decoration-skip-ink: auto;
                color: #9aa7b6 !important;
            }

            @media (max-width: 430px) {
                .step69-title-main { font-size: 15px; }
                .step69-title-teacher { display: none; }
                .step69-clock-pill { padding: 4px 8px; }
                .step69-clock-state { display: none; }
            }
            /* [STEP69_WEB_CSS_END] */
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass
# [STEP69_WEB_HELPERS_END]
# [STEP70_WEB_HEADER_MEMO_CALENDAR_START]
def step70_current_period_info():
    """웹뷰어 현재시각/현재교시 계산."""
    try:
        now = datetime.now(kst_tz)
    except Exception:
        now = datetime.now()

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
            return {
                "clock": now.strftime("%H:%M"),
                "period": str(p_name),
                "range": f"{start_str}~{end_str}",
            }

    if now_mins < 8 * 60:
        label = "수업 전"
    elif now_mins >= 17 * 60 + 50:
        label = "방과 후"
    else:
        label = "쉬는시간"

    return {"clock": now.strftime("%H:%M"), "period": label, "range": ""}


def step70_render_header():
    """제목과 현재시각을 같은 줄에 표시."""
    try:
        teacher_name = str(st.session_state.get("teacher", ""))
    except Exception:
        teacher_name = ""

    info = step70_current_period_info()
    clock = info.get("clock", "--:--")
    period = info.get("period", "")
    range_text = info.get("range", "")
    detail = period
    if range_text:
        detail += f" · {range_text}"

    st.markdown(
        f"""
        <div class="step70-title-row">
            <div class="step70-title-main">
                🏫 <b>명덕외고 시간표 뷰어</b>
                <span class="step70-title-teacher">({html.escape(teacher_name)} 선생님)</span>
            </div>
            <div class="step70-clock-pill">
                <span class="step70-clock-time">{html.escape(clock)}</span>
                <span class="step70-clock-state">{html.escape(detail)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def step70_memo_text_html(value):
    """메모 내용 중 안전한 색상 span만 실제 HTML로 렌더링하고 나머지는 escape."""
    import re as _re
    import html as _html

    s = str(value or "").replace("__STRIKE__|||", "")
    placeholders = {}

    def _safe_span(match):
        style = (match.group(1) or "").strip()
        inner = match.group(2) or ""

        # color:#e74c3c / background-color:#fff59d 정도만 허용
        ok_style = _re.fullmatch(
            r"\s*(color|background-color)\s*:\s*#[0-9a-fA-F]{3,6}\s*;?\s*",
            style,
            flags=_re.I,
        )
        if not ok_style:
            return _html.escape(match.group(0))

        key = f"__STEP70_SPAN_{len(placeholders)}__"
        safe_style = _html.escape(style, quote=True)
        safe_inner = step70_memo_text_html(inner)
        placeholders[key] = f"<span style=\"{safe_style}\">{safe_inner}</span>"
        return key

    # 먼저 허용 가능한 span을 placeholder로 바꾼 뒤 나머지를 escape
    s = _re.sub(
        r"<span\s+style=[\"']([^\"']+)[\"']>(.*?)</span>",
        _safe_span,
        s,
        flags=_re.I | _re.S,
    )

    escaped = _html.escape(s).replace("\n", "<br>")
    for key, html_value in placeholders.items():
        escaped = escaped.replace(key, html_value)
    return escaped


def step70_inject_css():
    """달력 세로배치/현재시각/메모 색상 표시용 CSS. 시간표 디자인은 현재 만족 상태를 유지."""
    try:
        st.markdown(
            """
            <style>
            /* [STEP70_WEB_CSS_START] */

            .step70-title-row {
                width: min(450px, 100%);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
                margin: 0 0 8px 0;
            }
            .step70-title-main {
                flex: 1 1 auto;
                min-width: 0;
                color: #0f172a;
                font-size: 16px;
                line-height: 1.2;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .step70-title-main b {
                font-weight: 800;
            }
            .step70-title-teacher {
                font-size: 12px;
                font-weight: 500;
                color: #334155;
                margin-left: 2px;
            }
            .step70-clock-pill {
                flex: 0 0 auto;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 4px 9px;
                border-radius: 999px;
                border: 1px solid rgba(96, 165, 250, 0.34);
                background: linear-gradient(180deg, rgba(247,250,255,0.98), rgba(227,239,255,0.95));
                color: #1e40af;
                box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12);
                white-space: nowrap;
            }
            .step70-clock-time {
                font-size: 13px;
                font-weight: 800;
            }
            .step70-clock-state {
                font-size: 12px;
                opacity: 0.92;
            }

            /* 상단 버튼 및 달력 드롭다운 세로배치 방지 */
            div[data-testid="stHorizontalBlock"] .stButton > button,
            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button,
            div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],
            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],
            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div {
                min-width: 56px !important;
                white-space: nowrap !important;
                word-break: keep-all !important;
                overflow-wrap: normal !important;
                writing-mode: horizontal-tb !important;
            }
            div[data-testid="stHorizontalBlock"] .stButton > button p,
            div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button p,
            div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] * {
                white-space: nowrap !important;
                word-break: keep-all !important;
                overflow-wrap: normal !important;
                writing-mode: horizontal-tb !important;
            }

            @media (max-width: 430px) {
                .step70-title-main {
                    font-size: 15px;
                }
                .step70-title-teacher {
                    display: none;
                }
                .step70-clock-pill {
                    padding: 4px 8px;
                }
                .step70-clock-state {
                    display: none;
                }
            }
            /* [STEP70_WEB_CSS_END] */
            </style>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass
# [STEP70_WEB_HEADER_MEMO_CALENDAR_END]
st.set_page_config(page_title="명덕외고 모바일 시간표", page_icon="🏫", layout="centered")


# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH BEGIN
try:
    import streamlit as st
    from datetime import datetime as _step93_datetime
    try:
        from zoneinfo import ZoneInfo as _step93_ZoneInfo
    except Exception:
        _step93_ZoneInfo = None

    def _step93_now_kst():
        if _step93_ZoneInfo:
            return _step93_datetime.now(_step93_ZoneInfo("Asia/Seoul"))
        return _step93_datetime.now()

    def _step93_minutes(dt):
        return dt.hour * 60 + dt.minute

    def _step93_current_label(dt):
        m = _step93_minutes(dt)
        slots = [
            ("조회", 7 * 60 + 40, 8 * 60),
            ("1교시", 8 * 60, 8 * 60 + 50),
            ("2교시", 9 * 60, 9 * 60 + 50),
            ("3교시", 10 * 60, 10 * 60 + 50),
            ("4교시", 11 * 60, 11 * 60 + 50),
            ("점심", 11 * 60 + 50, 12 * 60 + 40),
            ("5교시", 12 * 60 + 40, 13 * 60 + 30),
            ("6교시", 13 * 60 + 40, 14 * 60 + 30),
            ("7교시", 14 * 60 + 40, 15 * 60 + 30),
        ]
        if m < slots[0][1]:
            return "수업 전"
        for i, (name, start, end) in enumerate(slots):
            if start <= m < end:
                return name
            if i < len(slots) - 1:
                next_name, next_start, _ = slots[i + 1]
                if end <= m < next_start:
                    return f"곧 {next_name}" if next_start - m <= 15 else "쉬는시간"
        return "방과 후"

    def _step93_theme_key():
        texts = []
        try:
            texts += [str(v) for v in st.session_state.values()]
        except Exception:
            pass
        try:
            texts += [str(v) for v in st.query_params.values()]
        except Exception:
            pass
        s = " ".join(texts).lower()
        if any(k in s for k in ["pink", "핑크", "러블리", "rose", "lovely"]):
            return "pink"
        if any(k in s for k in ["dark", "다크", "black", "블랙", "night", "밤"]):
            return "dark"
        if any(k in s for k in ["green", "mint", "민트", "초록", "녹색"]):
            return "green"
        if any(k in s for k in ["purple", "violet", "보라", "라벤더"]):
            return "purple"
        if any(k in s for k in ["yellow", "cream", "beige", "노랑", "크림", "베이지"]):
            return "cream"
        return "blue"

    def _step93_palette():
        key = _step93_theme_key()
        palettes = {
            "pink": {
                "border": "#d9a6ae", "header": "#ffe0e6", "sub": "#fff0f3",
                "cell": "#fff8fa", "left": "#ffe8ee", "text": "#3b1f2b",
                "accent": "#ff8fa3", "shadow": "rgba(145, 70, 90, .18)",
            },
            "dark": {
                "border": "#475569", "header": "#1e293b", "sub": "#273449",
                "cell": "#0f172a", "left": "#1e293b", "text": "#e5e7eb",
                "accent": "#93c5fd", "shadow": "rgba(0, 0, 0, .35)",
            },
            "green": {
                "border": "#8fbc9a", "header": "#dff5e6", "sub": "#eefbf2",
                "cell": "#f8fffa", "left": "#e7f7ec", "text": "#14301f",
                "accent": "#54b873", "shadow": "rgba(55, 115, 75, .15)",
            },
            "purple": {
                "border": "#b7a5d9", "header": "#eee7ff", "sub": "#f6f1ff",
                "cell": "#fbf9ff", "left": "#f0e9ff", "text": "#2c2141",
                "accent": "#9b7be8", "shadow": "rgba(95, 70, 150, .16)",
            },
            "cream": {
                "border": "#d9bd78", "header": "#fff2cc", "sub": "#fff8e6",
                "cell": "#fffdf6", "left": "#fff0c2", "text": "#3a2a0b",
                "accent": "#e3a927", "shadow": "rgba(140, 110, 35, .18)",
            },
            "blue": {
                "border": "#8fb0d9", "header": "#e3f0ff", "sub": "#f0f7ff",
                "cell": "#fbfdff", "left": "#e8f3ff", "text": "#0b1f38",
                "accent": "#4f8bf9", "shadow": "rgba(50, 95, 150, .16)",
            },
        }
        return palettes.get(key, palettes["blue"])

    def _step93_table_css():
        p = _step93_palette()
        return f"""
        <style id=\"step93-timetable-theme\">
        html, body {{ margin: 0 !important; padding: 0 !important; background: transparent !important; }}
        table, .timetable, .timetable-table {{
            width: 100% !important;
            table-layout: fixed !important;
            border-collapse: collapse !important;
            border-spacing: 0 !important;
            border: 1px solid {p['border']} !important;
            background: {p['cell']} !important;
            color: {p['text']} !important;
            box-shadow: 0 3px 10px {p['shadow']} !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }}
        th, td {{
            border: 1px solid {p['border']} !important;
            color: {p['text']} !important;
            background: {p['cell']} !important;
            white-space: normal !important;
            word-break: keep-all !important;
            overflow-wrap: anywhere !important;
            word-wrap: break-word !important;
            text-align: center !important;
            vertical-align: middle !important;
            box-sizing: border-box !important;
            max-width: 0 !important;
            padding: 6px 4px !important;
            line-height: 1.25 !important;
        }}
        tr:first-child th, tr:first-child td, thead th {{
            background: {p['header']} !important;
            color: {p['text']} !important;
            font-weight: 800 !important;
        }}
        tr:nth-child(2) th, tr:nth-child(2) td {{ background: {p['sub']} !important; }}
        tr td:first-child, tr th:first-child {{
            background: {p['left']} !important;
            color: {p['text']} !important;
            font-weight: 800 !important;
        }}
        td *, th * {{
            white-space: normal !important;
            word-break: keep-all !important;
            overflow-wrap: anywhere !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}
        [style*=\"red\"], font[color=\"red\"], .red {{ color: #ef4444 !important; }}
        </style>
        """

    # components.html로 표가 렌더링되는 경우, iframe 내부에 테마 CSS를 직접 넣습니다.
    try:
        import streamlit.components.v1 as _step93_components
        if not getattr(_step93_components, "_step93_timetable_patch_applied", False):
            _step93_original_html = _step93_components.html
            def _step93_html(source, *args, **kwargs):
                try:
                    if isinstance(source, str) and ("<table" in source.lower() or "timetable" in source.lower()):
                        source = _step93_table_css() + source
                except Exception:
                    pass
                return _step93_original_html(source, *args, **kwargs)
            _step93_components.html = _step93_html
            _step93_components._step93_timetable_patch_applied = True
    except Exception:
        pass

    _step93_p = _step93_palette()
    _step93_now = _step93_now_kst()
    _step93_time = _step93_now.strftime("%H:%M")
    _step93_label = _step93_current_label(_step93_now)

    st.markdown(f"""
    <style id=\"step93-page-ui-fix\">
    :root {{
        --step93-border: {_step93_p['border']};
        --step93-header: {_step93_p['header']};
        --step93-sub: {_step93_p['sub']};
        --step93-cell: {_step93_p['cell']};
        --step93-left: {_step93_p['left']};
        --step93-text: {_step93_p['text']};
        --step93-accent: {_step93_p['accent']};
        --step93-shadow: {_step93_p['shadow']};
    }}

    /* 제목 잘림 방지 */
    .stApp [data-testid=\"stMarkdownContainer\"],
    .stApp [data-testid=\"stMarkdownContainer\"] * {{
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp [data-testid=\"stMarkdownContainer\"] h1,
    .stApp [data-testid=\"stMarkdownContainer\"] h2,
    .stApp [data-testid=\"stMarkdownContainer\"] h3,
    .stApp [data-testid=\"stMarkdownContainer\"] h4 {{
        line-height: 1.38 !important;
        min-height: 1.45em !important;
        padding-top: 3px !important;
        padding-bottom: 3px !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
        white-space: normal !important;
    }}

    /* 상단 버튼: 메모/조회 글자 가림 방지 */
    .stApp [data-testid=\"stButton\"] > button,
    .stApp button[kind] {{
        min-height: 40px !important;
        height: 40px !important;
        padding: 7px 10px !important;
        border-radius: 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        overflow: visible !important;
        white-space: nowrap !important;
        line-height: 1.15 !important;
        box-sizing: border-box !important;
    }}
    .stApp [data-testid=\"stButton\"] > button p,
    .stApp button[kind] p,
    .stApp button[kind] span {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.15 !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}

    /* 달력 selectbox: 중앙정렬 + 꺾쇠 제거 */
    .stApp div[data-baseweb=\"select\"] {{
        min-width: 60px !important;
        width: 60px !important;
    }}
    .stApp div[data-baseweb=\"select\"] > div {{
        min-height: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        overflow: visible !important;
        box-sizing: border-box !important;
    }}
    .stApp div[data-baseweb=\"select\"] > div > div {{
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        overflow: visible !important;
    }}
    .stApp div[data-baseweb=\"select\"] [class*=\"ValueContainer\"],
    .stApp div[data-baseweb=\"select\"] [class*=\"SingleValue\"],
    .stApp div[data-baseweb=\"select\"] [class*=\"singleValue\"] {{
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
        position: static !important;
        transform: none !important;
        overflow: visible !important;
        white-space: nowrap !important;
    }}
    .stApp div[data-baseweb=\"select\"] svg,
    .stApp div[data-baseweb=\"select\"] [class*=\"IndicatorsContainer\"],
    .stApp div[data-baseweb=\"select\"] [class*=\"SelectArrow\"],
    .stApp div[data-baseweb=\"select\"] [aria-hidden=\"true\"] {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .stApp div[data-baseweb=\"select\"] input {{
        width: 0 !important;
        min-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* st.markdown 표로 렌더링되는 경우에도 테마 적용 */
    .stApp table {{
        width: 100% !important;
        table-layout: fixed !important;
        border-collapse: collapse !important;
        border: 1px solid var(--step93-border) !important;
        background: var(--step93-cell) !important;
        color: var(--step93-text) !important;
        box-shadow: 0 3px 10px var(--step93-shadow) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }}
    .stApp table th, .stApp table td {{
        border: 1px solid var(--step93-border) !important;
        background: var(--step93-cell) !important;
        color: var(--step93-text) !important;
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        text-align: center !important;
        vertical-align: middle !important;
        max-width: 0 !important;
        padding: 6px 4px !important;
        line-height: 1.25 !important;
        box-sizing: border-box !important;
    }}
    .stApp table tr:first-child th,
    .stApp table tr:first-child td,
    .stApp table thead th {{ background: var(--step93-header) !important; font-weight: 800 !important; }}
    .stApp table tr:nth-child(2) th,
    .stApp table tr:nth-child(2) td {{ background: var(--step93-sub) !important; }}
    .stApp table tr td:first-child,
    .stApp table tr th:first-child {{ background: var(--step93-left) !important; font-weight: 800 !important; }}
    .stApp table td *, .stApp table th * {{
        white-space: normal !important;
        word-break: keep-all !important;
        overflow-wrap: anywhere !important;
        max-width: 100% !important;
    }}

    /* 현재시각: JS 없이 Python 렌더링. 새로고침/조작 시 갱신됨 */
    #step93-current-time-badge {{
        position: fixed;
        right: 12px;
        top: 58px;
        z-index: 9999;
        min-width: 88px;
        padding: 7px 9px;
        border-radius: 12px;
        border: 1px solid var(--step93-border);
        background: color-mix(in srgb, var(--step93-cell) 86%, white 14%);
        color: var(--step93-text);
        box-shadow: 0 3px 10px var(--step93-shadow);
        text-align: center;
        backdrop-filter: blur(5px);
    }}
    #step93-current-time-badge .time {{ font-size: 14px; font-weight: 800; line-height: 1.1; }}
    #step93-current-time-badge .label {{ font-size: 11px; margin-top: 2px; line-height: 1.1; }}
    </style>
    <div id=\"step93-current-time-badge\">
      <div class=\"time\">{_step93_time}</div>
      <div class=\"label\">{_step93_label}</div>
    </div>
    """, unsafe_allow_html=True)
except Exception:
    pass
# >>> STEP93_WEB_VIEWER_PRECISION_UI_PATCH END

# [STEP70_WEB_CALL_START]
step70_inject_css()
# [STEP70_WEB_CALL_END]
# [STEP69_WEB_CALL_START]
step69_inject_css()
# [STEP69_WEB_CALL_END]

# =========================================================
# 2. PWA(웹앱) 설정, 자동 로그인 복구, 브랜딩 숨김
# =========================================================
components.html(
    """
<script>
    const parentWindow = window.parent;
    const doc = parentWindow.document;
    const KEY_USER = "mdgo_auto_login_user";
    const KEY_TEACHER = "mdgo_auto_login_teacher";

    const metaTags = [
        { name: "apple-mobile-web-app-capable", content: "yes" },
        { name: "mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" }
    ];

    metaTags.forEach(tag => {
        if (!doc.querySelector(`meta[name="${tag.name}"]`)) {
            const m = doc.createElement("meta");
            m.name = tag.name;
            m.content = tag.content;
            doc.head.appendChild(m);
        }
    });

    const iconLink = doc.querySelector('link[rel="apple-touch-icon"]') || doc.createElement("link");
    iconLink.rel = "apple-touch-icon";
    iconLink.href = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f3eb.png";
    if (!doc.contains(iconLink)) doc.head.appendChild(iconLink);

    function hideBranding() {
        const selectors = [
            'header[data-testid="stHeader"]',
            '[data-testid="stToolbar"]',
            '[data-testid="stDecoration"]',
            '#MainMenu'
        ];

        selectors.forEach(sel => {
            doc.querySelectorAll(sel).forEach(el => {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
            });
        });

        doc.querySelectorAll('a, button, div, span').forEach(el => {
            const txt = (el.innerText || '').trim();
            const href = (el.getAttribute && el.getAttribute('href')) || '';
            const looksLikeProfile = /^@[\\w.-]+$/i.test(txt);
            const isStreamlitBadge =
                href.includes('streamlit.io') ||
                txt.includes('streamlit.io') ||
                txt.includes('Open app in Streamlit');

            if (looksLikeProfile || isStreamlitBadge) {
                const target = el.closest('a, button, div') || el;
                target.style.display = 'none';
                target.style.visibility = 'hidden';
                target.style.width = '0';
                target.style.height = '0';
                target.style.overflow = 'hidden';
            }
        });
    }

    function restoreAutoLogin() {
        try {
            const url = new URL(parentWindow.location.href);
            if (!url.searchParams.get('user')) {
                const savedUser = parentWindow.localStorage.getItem(KEY_USER);
                const savedTeacher = parentWindow.localStorage.getItem(KEY_TEACHER) || savedUser;
                if (savedUser) {
                    url.searchParams.set('user', savedUser);
                    url.searchParams.set('t', savedTeacher);
                    parentWindow.location.replace(url.toString());
                    return true;
                }
            }
        } catch (e) {}
        return false;
    }

    if (!restoreAutoLogin()) {
        hideBranding();
        const observer = new MutationObserver(hideBranding);
        observer.observe(doc.body, { childList: true, subtree: true });
        setTimeout(hideBranding, 300);
        setTimeout(hideBranding, 1200);
    }
</script>
""",
    height=0,
    width=0,
)

# =========================================================
# 3. Supabase 설정
#    - Streamlit Cloud: st.secrets 사용
#    - 로컬 테스트: supabase_config.json fallback 사용
# =========================================================
def _load_supabase_config():
    url = ""
    key = ""

    try:
        url = str(st.secrets.get("SUPABASE_URL", "")).strip()
        key = str(st.secrets.get("SUPABASE_KEY", "")).strip()
    except Exception:
        pass

    if url and key:
        return url, key

    config_candidates = [
        Path(__file__).resolve().parent / "supabase_config.json",
        Path(__file__).resolve().parent.parent / "supabase_config.json",
        Path.cwd() / "supabase_config.json",
    ]

    for config_path in config_candidates:
        if config_path.exists():
            try:
                import json
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                url = str(data.get("SUPABASE_URL", "")).strip()
                key = str(data.get("SUPABASE_KEY", "")).strip()
                if url and key:
                    return url, key
            except Exception:
                pass

    return "", ""


SUPABASE_URL, SUPABASE_KEY = _load_supabase_config()
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

REQUEST_VERIFY_SSL = False

# =========================================================
# 4. 공통 상수
# =========================================================
kst_tz = timezone(timedelta(hours=9))
days = ["월", "화", "수", "목", "금"]
font_list = ["맑은 고딕", "바탕", "돋움", "굴림", "Arial"]

BASE_DIR = Path(__file__).resolve().parent
DATA_CANDIDATES = [
    BASE_DIR / "data",
    BASE_DIR.parent / "data",
    Path.cwd() / "data",
    Path.cwd(),
]


def first_existing_path(*names: str) -> Path:
    for base in DATA_CANDIDATES:
        for name in names:
            p = base / name
            if p.exists():
                return p
    return DATA_CANDIDATES[0] / names[0]


TIMETABLE_FILE = first_existing_path("timetable.csv", "data.csv")
CALENDAR_FILE = first_existing_path("academic_calendar.csv")

period_times = [
    ("학사일정", "\n"),
    ("조회", "07:40\n08:00"),
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

themes = [
    {
        "name": "모던 다크",
        "bg": "#2c3e50", "top": "#1a252f", "grid": "#34495e",
        "head_bg": "#2c3e50", "head_fg": "white",
        "per_bg": "#7f8c8d", "per_fg": "white",
        "cell_bg": "#ecf0f1", "lunch_bg": "#95a5a6", "cell_fg": "#2c3e50",
        "hl_per": "#e74c3c", "hl_cell": "#f1c40f", "text": "#ffffff",
        "acad_per_bg": "#8e44ad", "acad_per_fg": "white",
        "acad_cell_bg": "#413a52", "acad_cell_fg": "#f1c40f",
    },
    {
        "name": "웜 파스텔",
        "bg": "#fdf6e3", "top": "#e4d5b7", "grid": "#eee8d5",
        "head_bg": "#d6caba", "head_fg": "#333333",
        "per_bg": "#e8e2d2", "per_fg": "#333333",
        "cell_bg": "#ffffff", "lunch_bg": "#f0e6d2", "cell_fg": "#4a4a4a",
        "hl_per": "#ffb6b9", "hl_cell": "#fae3d9", "text": "#333333",
        "acad_per_bg": "#ffdac1", "acad_per_fg": "#333333",
        "acad_cell_bg": "#ffe5d9", "acad_cell_fg": "#5c4d3c",
    },
    {
        "name": "클래식 블루",
        "bg": "#e0eaf5", "top": "#4a90e2", "grid": "#d0dceb",
        "head_bg": "#5c9ce6", "head_fg": "white",
        "per_bg": "#a8c2e0", "per_fg": "#333333",
        "cell_bg": "#ffffff", "lunch_bg": "#d0e0f0", "cell_fg": "#2c3e50",
        "hl_per": "#f39c12", "hl_cell": "#fde3a7", "text": "#2c3e50",
        "acad_per_bg": "#1abc9c", "acad_per_fg": "white",
        "acad_cell_bg": "#d1f2eb", "acad_cell_fg": "#0e6251",
    },
    {
        "name": "포레스트",
        "bg": "#e9ede7", "top": "#2c5344", "grid": "#d0d8d3",
        "head_bg": "#3b6a57", "head_fg": "white",
        "per_bg": "#8ba89a", "per_fg": "white",
        "cell_bg": "#ffffff", "lunch_bg": "#d0e8d7", "cell_fg": "#1a3026",
        "hl_per": "#d35400", "hl_cell": "#f9e79f", "text": "#1a3026",
        "acad_per_bg": "#d35400", "acad_per_fg": "white",
        "acad_cell_bg": "#fad7a1", "acad_cell_fg": "#6e2c00",
    },
    {
        "name": "모노톤",
        "bg": "#f5f5f5", "top": "#333333", "grid": "#e0e0e0",
        "head_bg": "#555555", "head_fg": "white",
        "per_bg": "#999999", "per_fg": "white",
        "cell_bg": "#ffffff", "lunch_bg": "#d4d4d4", "cell_fg": "#000000",
        "hl_per": "#d90429", "hl_cell": "#edf2f4", "text": "#222222",
        "acad_per_bg": "#424242", "acad_per_fg": "white",
        "acad_cell_bg": "#cfcfcf", "acad_cell_fg": "#000000",
    },
    {
        "name": "윈도우 11 라이트",
        "bg": "#f3f7fb", "top": "#e7eef8", "grid": "#d6e2f1",
        "head_bg": "#dbe8f7", "head_fg": "#1f2d3d",
        "per_bg": "#c7d8ee", "per_fg": "#1f2d3d",
        "cell_bg": "#ffffff", "lunch_bg": "#edf3fa", "cell_fg": "#1f2d3d",
        "hl_per": "#2563eb", "hl_cell": "#dbeafe", "text": "#1f2d3d",
        "acad_per_bg": "#93c5fd", "acad_per_fg": "#0f172a",
        "acad_cell_bg": "#eff6ff", "acad_cell_fg": "#1e3a8a",
    },
]

# =========================================================
# 5. 공통 함수
# =========================================================
def safe_fragment_rerun():
    if "scope" in inspect.signature(st.rerun).parameters:
        st.rerun(scope="fragment")
    else:
        st.rerun()


def check_password(user_id):
    if not USE_SUPABASE:
        return None
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{user_id}",
            headers=HEADERS,
            timeout=3,
            verify=REQUEST_VERIFY_SSL,
        )
        if r.status_code == 200 and len(r.json()) > 0:
            return r.json()[0]
    except Exception:
        pass
    return None


def update_db_bg(url, headers, user, key, val):
    if not USE_SUPABASE:
        return
    try:
        requests.patch(
            f"{url}/rest/v1/users?teacher_name=eq.{user}",
            headers=headers,
            json={key: val},
            timeout=3,
            verify=REQUEST_VERIFY_SSL,
        )
    except Exception:
        pass


def fetch_all_data(user_id):
    if not USE_SUPABASE:
        st.session_state.custom_data = st.session_state.get("custom_data", {})
        st.session_state.memos_list = st.session_state.get("memos_list", [])
        st.session_state.data_loaded = True
        return

    try:
        r_user = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{user_id}",
            headers=HEADERS,
            timeout=3,
            verify=REQUEST_VERIFY_SSL,
        )
        if r_user.status_code == 200 and len(r_user.json()) > 0:
            u_data = r_user.json()[0]
            st.session_state.theme_idx = u_data.get("theme_idx", 0)
            st.session_state.font_name = u_data.get("font_name", "맑은 고딕")
            st.session_state.show_zero = u_data.get("show_zero", False)
            st.session_state.show_extra = u_data.get("show_extra", False)
            st.session_state.show_memo = u_data.get("show_memo", True)

        target_teacher = st.session_state.get("teacher", user_id)

        r_cust = requests.get(
            f"{SUPABASE_URL}/rest/v1/custom_schedule?teacher_name=eq.{target_teacher}",
            headers=HEADERS,
            timeout=3,
            verify=REQUEST_VERIFY_SSL,
        )
        if r_cust.status_code == 200:
            st.session_state.custom_data = {
                row["date_key"]: clean_view_text(row.get("subject", "")) for row in r_cust.json()
            }
        else:
            st.session_state.custom_data = {}

        r_memo = requests.get(
            f"{SUPABASE_URL}/rest/v1/memos?teacher_name=eq.{user_id}&order=created_at.desc",
            headers=HEADERS,
            timeout=3,
            verify=REQUEST_VERIFY_SSL,
        )
        if r_memo.status_code == 200:
            st.session_state.memos_list = r_memo.json()
        else:
            st.session_state.memos_list = []

        st.session_state.data_loaded = True

    except Exception:
        st.session_state.custom_data = st.session_state.get("custom_data", {})
        st.session_state.memos_list = st.session_state.get("memos_list", [])


def normalize_text(value):
    text = str(value).replace("\xa0", " ").strip()
    return re.sub(r"\s+", " ", text)




def clean_view_text(value):
    # 화면 표시용 텍스트 정리: strike marker와 literal 줄바꿈을 정리합니다.
    text = "" if value is None else str(value)

    # PC버전 완료/취소선 저장 흔적 제거
    text = re.sub(r"_{1,3}STRIKE_{1,3}\s*\|\|?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"_{1,3}STRIKE_{1,3}", "", text, flags=re.IGNORECASE)

    # 과거 저장값 중 literal \n이 있으면 실제 줄바꿈으로 변환
    text = text.replace("\\n", "\n")
    text = text.replace("\r\n", "\n")

    return text.strip()


def sanitize_timetable_data(t_data):
    # 시간표 dict 전체의 표시 문자열을 정리합니다.
    try:
        for teacher, schedule in t_data.items():
            for day, values in schedule.items():
                schedule[day] = [clean_view_text(v) for v in values]
    except Exception:
        pass
    return sanitize_timetable_data(t_data)


def safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def supabase_get_rows(table_name, *, select="*", extra_params=None, timeout=5):
    """Supabase 조회 공통 함수. 실패 시 빈 리스트 반환."""
    if not USE_SUPABASE:
        return []

    params = {"select": select}
    if extra_params:
        params.update(extra_params)

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}",
            headers=HEADERS,
            params=params,
            timeout=timeout,
            verify=REQUEST_VERIFY_SSL,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass

    return []





# =========================================================
# 6. URL 파라미터 / 세션 초기화
# =========================================================
params = st.query_params

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "week_offset" not in st.session_state:
    st.session_state.week_offset = 0
if "teacher" not in st.session_state:
    st.session_state.teacher = "표민호"
if "theme_idx" not in st.session_state:
    st.session_state.theme_idx = 0
if "font_name" not in st.session_state:
    st.session_state.font_name = "맑은 고딕"
if "show_zero" not in st.session_state:
    st.session_state.show_zero = False
if "show_extra" not in st.session_state:
    st.session_state.show_extra = False
if "show_memo" not in st.session_state:
    st.session_state.show_memo = True
if "custom_data" not in st.session_state:
    st.session_state.custom_data = {}
if "memos_list" not in st.session_state:
    st.session_state.memos_list = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

if "user" in params and st.session_state.logged_in_user is None:
    st.session_state.logged_in_user = params["user"]

if "t" in params:
    st.session_state.teacher = params["t"]
elif st.session_state.logged_in_user and st.session_state.teacher == "표민호":
    st.session_state.teacher = st.session_state.logged_in_user

st.session_state.theme_idx = min(max(int(st.session_state.theme_idx), 0), len(themes) - 1)

if st.session_state.logged_in_user and not st.session_state.data_loaded:
    fetch_all_data(st.session_state.logged_in_user)
    st.session_state.theme_idx = min(max(int(st.session_state.theme_idx), 0), len(themes) - 1)

t = themes[st.session_state.theme_idx]

# =========================================================
# 7. 로그인 화면
# =========================================================
if st.session_state.logged_in_user is None:
    st.markdown(
        "<div style='text-align:center; padding: 2rem 0 1rem 0;'><div style='font-size: 3rem;'>🏫</div><h1 style='font-size: 26px; font-weight: 800;'>명덕외고 뷰어</h1></div>",
        unsafe_allow_html=True,
    )
    st.info("💡 입력/수정은 PC버전을 이용해 주세요.")

    tab1, tab2 = st.tabs(["🔐 로그인", "📝 새 계정 등록"])

    with tab1:
        login_id = st.text_input("아이디 (선생님 성함)", placeholder="예: 표민호")
        login_pw = st.text_input("비밀번호", type="password")
        auto_login = st.checkbox("자동 로그인", value=True)

        if st.button("로그인", use_container_width=True, type="primary"):
            if not login_id or not login_pw:
                st.error("아이디와 비밀번호를 모두 입력해 주세요.")
            else:
                u_data = check_password(login_id)
                if not u_data:
                    st.error("등록되지 않은 선생님입니다.")
                elif u_data["password"] != login_pw:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.session_state.logged_in_user = login_id
                    st.session_state.teacher = login_id
                    st.query_params["user"] = login_id
                    st.query_params["t"] = login_id

                    if auto_login:
                        components.html(
                            f"""
<script>
    const pw = window.parent;
    pw.localStorage.setItem('mdgo_auto_login_user', {login_id!r});
    pw.localStorage.setItem('mdgo_auto_login_teacher', {login_id!r});
</script>
""",
                            height=0,
                            width=0,
                        )
                    else:
                        components.html(
                            """
<script>
    const pw = window.parent;
    pw.localStorage.removeItem('mdgo_auto_login_user');
    pw.localStorage.removeItem('mdgo_auto_login_teacher');
</script>
""",
                            height=0,
                            width=0,
                        )

                    fetch_all_data(login_id)
                    st.session_state.theme_idx = min(
                        max(int(st.session_state.theme_idx), 0), len(themes) - 1
                    )
                    st.rerun()

    with tab2:
        st.caption("모바일에서도 계정 생성이 가능하도록 수정했습니다.")
        new_id = st.text_input("새 아이디 (선생님 성함)", key="register_id")
        new_pw = st.text_input("새 비밀번호", type="password", key="register_pw")
        new_pw2 = st.text_input("비밀번호 확인", type="password", key="register_pw2")

        if st.button("계정 생성", use_container_width=True):
            if not new_id or not new_pw or not new_pw2:
                st.error("모든 항목을 입력해 주세요.")
            elif new_pw != new_pw2:
                st.error("비밀번호 확인이 일치하지 않습니다.")
            elif check_password(new_id):
                st.error("이미 등록된 선생님입니다.")
            else:
                try:
                    payload = {
                        "teacher_name": new_id,
                        "password": new_pw,
                        "theme_idx": 0,
                        "font_name": "맑은 고딕",
                        "show_zero": False,
                        "show_extra": False,
                        "show_memo": True,
                    }
                    r = requests.post(
                        f"{SUPABASE_URL}/rest/v1/users",
                        headers=HEADERS,
                        json=payload,
                        timeout=5,
                        verify=REQUEST_VERIFY_SSL,
                    )
                    if r.status_code in (200, 201):
                        st.success("계정이 생성되었습니다. 로그인 탭에서 로그인해 주세요.")
                    else:
                        st.error("계정 생성에 실패했습니다. 잠시 후 다시 시도해 주세요.")
                except Exception:
                    st.error("계정 생성 중 오류가 발생했습니다.")

    st.stop()

# =========================================================
# 8. 데이터 로드
# =========================================================
@st.cache_data(ttl=300)
def load_csv():
    """
    시간표 로딩 안정화 버전.
    1) 먼저 CSV fallback 데이터를 읽어 전체 교사 시간표를 확보
    2) 그 다음 Supabase public.timetable_entries 데이터를 덮어쓰기
    이렇게 하면 Supabase 일부 데이터가 비어 있어도 기존 시간표가 사라지지 않습니다.
    """
    t_data = {}

    # 1. CSV fallback을 먼저 읽어 기본 시간표 확보
    file_path = TIMETABLE_FILE
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
                sample = f.read(2048)
                f.seek(0)
                header = sample.splitlines()[0] if sample.strip() else ""
                header_set = {h.strip().lower() for h in header.split(",")}

                # 차세대 형식: teacher,day,period,subject
                if {"teacher", "day", "period", "subject"}.issubset(header_set):
                    reader = csv.DictReader(f)

                    for row in reader:
                        teacher = (row.get("teacher") or "").strip()
                        day = (row.get("day") or "").strip()
                        period = safe_int((row.get("period") or "").strip(), 0)
                        subject = clean_view_text(row.get("subject", ""))

                        if not teacher or day not in days or not 1 <= period <= 9:
                            continue

                        if teacher not in t_data:
                            t_data[teacher] = {d: [""] * 9 for d in days}

                        t_data[teacher][day][period - 1] = subject

                else:
                    # 레거시 data.csv 형식 fallback
                    f.seek(0)
                    reader = csv.reader(f)
                    next(reader, None)

                    for row in reader:
                        if not row or len(row) < 36:
                            continue

                        name = row[0].strip()
                        if not name:
                            continue

                        periods_per_day = (len(row) - 1) // 5
                        schedule = {d: [""] * 9 for d in days}

                        for i, day in enumerate(days):
                            start_idx = 1 + i * periods_per_day
                            schedule[day] = row[start_idx:start_idx + periods_per_day][:9]
                            if len(schedule[day]) < 9:
                                schedule[day] += [""] * (9 - len(schedule[day]))

                        t_data[name] = schedule

        except Exception:
            # CSV가 깨져도 Supabase 로딩은 시도
            pass

    # 2. Supabase 데이터가 있으면 CSV 위에 덮어쓰기
    rows = supabase_get_rows(
        "timetable_entries",
        select="teacher_name,day,period,subject",
        extra_params={"order": "teacher_name.asc,day.asc,period.asc"},
        timeout=8,
    )

    if rows:
        for row in rows:
            teacher = str(row.get("teacher_name") or "").strip()
            day = str(row.get("day") or "").strip()
            period = safe_int(row.get("period"), 0)
            subject = clean_view_text(row.get("subject", ""))

            if not teacher or day not in days or not 1 <= period <= 9:
                continue

            if teacher not in t_data:
                t_data[teacher] = {d: [""] * 9 for d in days}

            t_data[teacher][day][period - 1] = subject

    return t_data



@st.cache_data(ttl=300)
def load_academic_data():
    """학사일정은 Supabase public.academic_calendar 우선, 실패/비어 있음이면 CSV fallback."""
    result = {}

    rows = supabase_get_rows(
        "academic_calendar",
        select="date,event",
        extra_params={"order": "date.asc"},
        timeout=8,
    )

    if rows:
        for row in rows:
            ds = str(row.get("date") or "").strip()
            ev = clean_view_text(row.get("event", ""))
            if ds and ev:
                result[ds] = ev

        if result:
            return result

    if CALENDAR_FILE.exists():
        try:
            with open(CALENDAR_FILE, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ds = (row.get("date") or "").strip()
                    ev = clean_view_text(row.get("event", ""))
                    if ds and ev:
                        result[ds] = ev
            if result:
                return result
        except Exception:
            pass

    academic_schedule = {}
    target_file = None

    for base in DATA_CANDIDATES:
        for filepath in base.glob("**/*학사일정*.csv"):
            if "수업일수" not in str(filepath):
                target_file = filepath
                break
        if target_file:
            break

    if not target_file or not target_file.exists():
        return {}

    reader = None
    for enc in ["utf-8-sig", "cp949", "euc-kr", "utf-8"]:
        try:
            with open(target_file, "r", encoding=enc) as f:
                content = f.read()
                if any(token in content for token in ["월", "일", "학사"]):
                    reader = list(csv.reader(io.StringIO(content)))
                    break
        except Exception:
            pass

    if not reader:
        return {}

    try:
        header_row_idx = 0
        for i, row in enumerate(reader):
            joined = " ".join(normalize_text(cell) for cell in row)
            if re.search(r"\d+\s*월", joined):
                header_row_idx = i
                break

        header = reader[header_row_idx]
        month_cols = {}
        for col_idx, val in enumerate(header):
            m = re.search(r"(\d+)\s*월", normalize_text(val))
            if m:
                month_cols[int(m.group(1))] = col_idx

        days_of_week_set = {"월", "화", "수", "목", "금", "토", "일"}
        ignore_tokens = days_of_week_set | {"", "-", "없음", "해당없음", "nan", "none"}
        current_year = datetime.now(kst_tz).year

        for row in reader[header_row_idx + 1:]:
            if not row:
                continue

            day_text = normalize_text(row[0]) if len(row) > 0 else ""
            day_match = re.match(r"^(\d{1,2})\b", day_text)
            if not day_match:
                continue

            day = int(day_match.group(1))

            for month, col_idx in month_cols.items():
                if col_idx >= len(row):
                    continue

                raw_event = normalize_text(row[col_idx])
                lowered = raw_event.lower()

                if raw_event in ignore_tokens or lowered in ignore_tokens or raw_event.isdigit():
                    continue

                cleaned = re.sub(r"^[월화수목금토일]\s+", "", raw_event).strip(" |/")
                if not cleaned or cleaned in days_of_week_set:
                    continue

                year = current_year if month >= 3 else current_year + 1
                date_str = f"{year}-{month:02d}-{day:02d}"

                if date_str in academic_schedule:
                    academic_schedule[date_str] += "\n" + cleaned
                else:
                    academic_schedule[date_str] = cleaned

    except Exception:
        return {}

    return academic_schedule



teachers_data = load_csv()
academic_data = load_academic_data()

# =========================================================
# 9. CSS
# =========================================================
st.markdown(
    f"""
<style>
    html, body, .stApp {{
        touch-action: auto !important;
        background-color: {t['bg']} !important;
        font-family: '{st.session_state.font_name}', sans-serif;
    }}
    * {{
        animation-duration: 0s !important;
        transition-duration: 0s !important;
    }}
    .element-container, .stMarkdown, div[data-testid="stPopoverBody"] {{
        animation: none !important;
        transition: none !important;
    }}
    .block-container {{
        padding: 0.5rem 0.2rem !important;
        max-width: 100% !important;
    }}
    header {{
        visibility: hidden;
    }}
    .header-container {{
        width: 100% !important;
        max-width: 450px !important;
        margin: 0 auto 5px 0 !important;
        display: flex !important;
        align-items: center;
        padding-left: 2px;
        color: {t['text']} !important;
    }}
    div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        background-color: {t['top']} !important;
        padding: 4px 4px !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        max-width: 450px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        gap: 2px !important;
    }}
    div[data-testid="stHorizontalBlock"] > div {{
        flex: 1 1 0px !important;
        width: auto !important;
        min-width: 0px !important;
        max-width: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: block !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(1),
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) {{
        flex: 0 0 28px !important;
        width: 28px !important;
        min-width: 28px !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {{
        flex: 0 0 58px !important;
        width: 58px !important;
        min-width: 58px !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton > button {{
        height: 34px !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: bold !important;
        padding: 0 !important;
        line-height: 1 !important;
        width: 100% !important;
        min-width: 0 !important;
        display: block !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        color: {t['text']} !important;
        border: none !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {{
        background-color: {t['hl_per']} !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }}
    div[data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {{
        font-size: 15px !important;
        height: 34px !important;
        padding: 0 !important;
        width: 100% !important;
        border: none !important;
        background-color: transparent !important;
        color: {t['text']} !important;
        min-width: 0 !important;
    }}
    .mobile-table {{
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 14px;
        border: 1.5px solid #333333;
    }}
    .mobile-table th {{
        border: 1px solid #333333;
        padding: 4px 1px;
        text-align: center;
        height: 45px;
    }}
    .mobile-table td {{
        border: 1px solid #333333;
        padding: 0px;
        text-align: center;
        vertical-align: middle;
        height: 65px;
        word-break: keep-all;
        font-weight: bold;
        font-size: 14px;
    }}
    .hl-border-red {{
        box-shadow: inset 0 0 0 3px {t['hl_per']} !important;
        z-index: 10;
    }}
    .hl-border-yellow {{
        box-shadow: inset 0 0 0 3px {t['hl_cell']} !important;
        z-index: 10;
    }}
    .hl-fill-yellow {{
        background-color: {t['hl_cell']} !important;
        color: black !important;
    }}
    .memo-container {{
        height: 300px;
        overflow-y: auto;
        border: 1px solid {t['grid']};
        border-radius: 6px;
        padding: 6px;
        scrollbar-width: thin;
        scrollbar-color: rgba(150, 150, 150, 0.5) transparent;
    }}
    .memo-container::-webkit-scrollbar {{
        width: 6px;
    }}
    .memo-container::-webkit-scrollbar-track {{
        background: transparent;
    }}
    .memo-container::-webkit-scrollbar-thumb {{
        background-color: rgba(150, 150, 150, 0.5);
        border-radius: 10px;
    }}
    .memo-container::-webkit-scrollbar-thumb:hover {{
        background-color: rgba(150, 150, 150, 0.8);
    }}
    .install-guide-row {{
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 8px;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 10. 헤더
# =========================================================
u = st.session_state.logged_in_user
st.markdown(
    f"<div class='header-container'><div style='font-size:16px; font-weight:800; white-space:nowrap;'>🏫 명덕외고 시간표 뷰어 <span style='font-size:13px; font-weight:normal;'>({u} 선생님)</span></div></div>",
    unsafe_allow_html=True,
)

# =========================================================
# 11. 메인 대시보드
# =========================================================
@st.fragment
def display_dashboard():
    custom_data = st.session_state.get("custom_data", {})
    memos_list = st.session_state.get("memos_list", [])

    c1, c2, c3, c4, c5, c6, c7, c8, c9 = st.columns(9)

    with c1:
        if st.button("◀", use_container_width=True, key="prev"):
            st.session_state.week_offset -= 1
            safe_fragment_rerun()

    with c2:
        btn_type = "primary" if st.session_state.week_offset == 0 else "secondary"
        if st.button("오늘", use_container_width=True, type=btn_type, key="today"):
            st.session_state.week_offset = 0
            safe_fragment_rerun()

    with c3:
        if st.button("▶", use_container_width=True, key="next"):
            st.session_state.week_offset += 1
            safe_fragment_rerun()

    with c4:
        with st.popover("달력", use_container_width=True):
            st.markdown(
                "<div style='font-size:13px; font-weight:bold; margin-bottom:5px; color:#333;'>이동할 날짜 선택</div>",
                unsafe_allow_html=True,
            )
            now_date = datetime.now(kst_tz).date()
            current_view_date = now_date + timedelta(weeks=st.session_state.week_offset)
            selected_date = st.date_input("날짜 선택", value=current_view_date, label_visibility="collapsed")

            now_monday = now_date - timedelta(days=now_date.weekday())
            selected_monday = selected_date - timedelta(days=selected_date.weekday())
            diff_weeks = (selected_monday - now_monday).days // 7

            if diff_weeks != st.session_state.week_offset:
                st.session_state.week_offset = diff_weeks
                safe_fragment_rerun()

    with c5:
        if st.button("🔄", use_container_width=True, key="refresh"):
            fetch_all_data(st.session_state.logged_in_user)
            st.rerun()

    with c6:
        btn_type = "primary" if st.session_state.show_memo else "secondary"
        if st.button("메모", use_container_width=True, type=btn_type, key="memo_toggle"):
            st.session_state.show_memo = not st.session_state.show_memo
            threading.Thread(
                target=update_db_bg,
                args=(SUPABASE_URL, HEADERS, st.session_state.logged_in_user, "show_memo", st.session_state.show_memo),
                daemon=True,
            ).start()
            safe_fragment_rerun()

    with c7:
        btn_type = "primary" if st.session_state.show_zero else "secondary"
        if st.button("조회", use_container_width=True, type=btn_type, key="zero_toggle"):
            st.session_state.show_zero = not st.session_state.show_zero
            threading.Thread(
                target=update_db_bg,
                args=(SUPABASE_URL, HEADERS, st.session_state.logged_in_user, "show_zero", st.session_state.show_zero),
                daemon=True,
            ).start()
            safe_fragment_rerun()

    with c8:
        btn_type = "primary" if st.session_state.show_extra else "secondary"
        if st.button("8·9", use_container_width=True, type=btn_type, key="extra_toggle"):
            st.session_state.show_extra = not st.session_state.show_extra
            threading.Thread(
                target=update_db_bg,
                args=(SUPABASE_URL, HEADERS, st.session_state.logged_in_user, "show_extra", st.session_state.show_extra),
                daemon=True,
            ).start()
            safe_fragment_rerun()

    with c9:
        with st.popover("⚙️", use_container_width=True):
            st.markdown(
                "<div style='font-size:14px; font-weight:bold; margin-bottom:8px;'>📱 앱 설치 (전체화면)</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                """
                <div class='install-guide-row'><div>💡</div><div><b>아이폰(Safari):</b> 하단 [공유(⍐)] ➔ <b>'홈 화면에 추가'</b></div></div>
                <div class='install-guide-row'><div>💡</div><div><b>갤럭시(Chrome):</b> 상단 [점 3개(⋮)] ➔ <b>'홈 화면에 추가'</b></div></div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("---")

            new_theme = st.selectbox(
                "🎨 테마 변경",
                [th["name"] for th in themes],
                index=st.session_state.theme_idx,
            )
            if new_theme != themes[st.session_state.theme_idx]["name"]:
                new_idx = [th["name"] for th in themes].index(new_theme)
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{st.session_state.logged_in_user}",
                    headers=HEADERS,
                    json={"theme_idx": new_idx},
                    timeout=3,
                )
                st.session_state.theme_idx = new_idx
                st.rerun()

            font_index = font_list.index(st.session_state.font_name) if st.session_state.font_name in font_list else 0
            new_font = st.selectbox("A 폰트 변경", font_list, index=font_index)

            if new_font != st.session_state.font_name:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{st.session_state.logged_in_user}",
                    headers=HEADERS,
                    json={"font_name": new_font},
                    timeout=3,
                )
                st.session_state.font_name = new_font
                st.rerun()

            st.markdown("---")

            if st.button("🔓 로그아웃", type="primary", use_container_width=True):
                components.html(
                    """
<script>
    const pw = window.parent;
    pw.localStorage.removeItem('mdgo_auto_login_user');
    pw.localStorage.removeItem('mdgo_auto_login_teacher');
</script>
""",
                    height=0,
                    width=0,
                )
                st.session_state.logged_in_user = None
                st.session_state.teacher = "표민호"
                st.session_state.data_loaded = False
                st.query_params.clear()
                st.rerun()

    now_kst = datetime.now(kst_tz)
    target_date = now_kst + timedelta(weeks=st.session_state.week_offset)
    monday = target_date - timedelta(days=target_date.weekday())
    is_current_week = st.session_state.week_offset == 0
    today_idx = now_kst.weekday()
    now_mins = now_kst.hour * 60 + now_kst.minute

    active_row_idx, preview_row_idx = -1, -1
    for idx, (p_name, t_range) in enumerate(period_times):
        if p_name == "학사일정":
            continue
        start_str, end_str = t_range.split("\n")
        h1, m1 = map(int, start_str.split(":"))
        h2, m2 = map(int, end_str.split(":"))
        s_mins, e_mins = h1 * 60 + m1, h2 * 60 + m2

        if s_mins <= now_mins < e_mins:
            active_row_idx = idx
            break
        elif now_mins < s_mins:
            preview_row_idx = idx
            break

    html_parts = []
    html_parts.append(
        f"<div style='width:100%; overflow-x:auto; background-color:{t['grid']}; border-radius:4px;'><table class='mobile-table'>"
    )
    html_parts.append(
        f"<tr style='background-color:{t['head_bg']}; color:{t['head_fg']};'><th style='width: 13%; font-size:14px;'>교시</th>"
    )

    for col, day in enumerate(days):
        date_str = (monday + timedelta(days=col)).strftime("%m/%d")
        th_class = "hl-border-red" if (is_current_week and col == today_idx) else ""
        th_bg = t["hl_per"] if (is_current_week and col == today_idx) else t["head_bg"]
        th_fg = "white" if (is_current_week and col == today_idx and t["name"] != "웜 파스텔") else t["head_fg"]
        html_parts.append(
            f"<th class='{th_class}' style='background-color:{th_bg}; color:{th_fg};'><div style='line-height: 1.1;'><span style='font-size:15px;'>{day}</span><br><span style='font-size:12px; font-weight:normal;'>{date_str}</span></div></th>"
        )
    html_parts.append("</tr>")

    base_schedule = teachers_data.get(st.session_state.teacher, {d: [""] * 9 for d in days})

    for row_idx, (period, time_str) in enumerate(period_times):
        if period != "학사일정":
            if period == "조회" and not st.session_state.show_zero:
                continue
            if period in ["8교시", "9교시"] and not st.session_state.show_extra:
                continue

        row_class = "hl-border-red" if (is_current_week and (row_idx == active_row_idx or row_idx == preview_row_idx)) else ""
        html_parts.append("<tr>")

        if period == "학사일정":
            p_bg = t.get("acad_per_bg", t["per_bg"])
            p_fg = t.get("acad_per_fg", t["per_fg"])
        else:
            p_bg = t["hl_per"] if (is_current_week and active_row_idx == row_idx) else t["per_bg"]
            p_fg = "white" if (is_current_week and active_row_idx == row_idx and t["name"] != "웜 파스텔") else t["per_fg"]

        time_html = ""
        if period != "학사일정":
            start_t, end_t = time_str.split("\n")
            time_html = (
                f"<div style='line-height:1.0; width:100%; padding:0 2px;'>"
                f"<div style='text-align:left; font-size:11px; font-weight:normal;'>{start_t}~</div>"
                f"<div style='text-align:right; font-size:11px; font-weight:normal;'>{end_t}</div>"
                f"</div>"
            )

        html_parts.append(
            f"<td class='{row_class}' style='background-color:{p_bg}; color:{p_fg};'><div style='line-height:1.1; font-size:14px; margin-bottom:2px;'><b>{period}</b></div>{time_html}</td>"
        )

        for col, day in enumerate(days):
            row_num = row_idx + 1
            date_str = (monday + timedelta(days=col)).strftime("%Y-%m-%d")
            date_key = f"{date_str}_schedule" if row_num == 1 else f"{date_str}_{row_num - 1}"

            subject = ""
            if period == "학사일정":
                subject = academic_data.get(date_str, "").replace(" / ", "\n")
            elif period not in ["점심", "조회"]:
                s_idx = row_num - 3 if row_num < 7 else row_num - 4
                if 0 <= s_idx < len(base_schedule.get(day, [])):
                    subject = base_schedule[day][s_idx]

            is_strike = False
            is_custom = False
            custom_color = None

            if date_key in custom_data:
                val = custom_data[date_key]
                if val == "__STRIKE__":
                    is_strike = True
                    is_custom = True
                else:
                    is_custom = True
                    match = re.match(
                        r"^<span style=['\"]color:([^\"']+)['\"]>(.*)</span>$",
                        str(val),
                        re.DOTALL | re.IGNORECASE,
                    )
                    if match:
                        custom_color = match.group(1)
                        subject = match.group(2)
                    else:
                        subject = str(val)

            if period == "학사일정":
                bg = t.get("acad_cell_bg", t["lunch_bg"])
                fg = t.get("acad_cell_fg", t["cell_fg"])
                deco = "line-through" if is_strike else "none"
                if is_strike:
                    fg = "#bdc3c7" if t["name"] == "모던 다크" else "#95a5a6"
                elif custom_color:
                    fg = custom_color
            else:
                bg = t["lunch_bg"] if period in ["조회", "점심"] else t["cell_bg"]
                fg = t["cell_fg"]
                deco = "line-through" if is_strike else "none"
                if is_strike:
                    fg = "#bdc3c7" if t["name"] == "모던 다크" else "#95a5a6"
                elif custom_color:
                    fg = custom_color
                elif is_custom:
                    fg = "#e74c3c"

            cell_class = ""
            if is_current_week and col == today_idx:
                if row_idx == active_row_idx:
                    cell_class = "hl-fill-yellow"
                elif row_idx == preview_row_idx:
                    cell_class = "hl-border-yellow"

            font_sz_str = "14px"
            line_height = "1.2"

            if period == "학사일정":
                font_sz = 12
                if subject:
                    lines = subject.split("\n")
                    num_lines = len(lines)
                    max_len = max([len(l) for l in lines] if lines else [0])
                    if num_lines >= 4 or max_len > 9:
                        font_sz = 9
                    elif num_lines >= 3 or max_len > 6:
                        font_sz = 10
                font_sz_str = f"{font_sz}px"
                line_height = "1.1"

            display = subject.replace("\n", "<br>") if subject else ""
            html_parts.append(
                f"<td class='{cell_class}' style='background-color:{bg}; color:{fg};'><div style='text-decoration:{deco}; font-size:{font_sz_str}; width:100%; display:flex; align-items:center; justify-content:center; height:100%; line-height:{line_height}; word-break:keep-all; overflow-wrap:break-word; white-space:normal; padding:2px;'>{display}</div></td>"
            )

        html_parts.append("</tr>")

    html_parts.append("</table></div>")

    if st.session_state.show_memo:
        html_parts.append(
            f"<div class='memo-panel' style='margin-top:10px;'>"
            f"<h3 style='margin:0; font-size:15px; margin-bottom:8px; color:{t['text']};'>"
            f"📝 {html.escape(str(st.session_state.teacher))} 메모장 "
            f"<span style='font-size:11px; font-weight:normal; opacity:0.6;'>(수정은 PC에서)</span>"
            f"</h3><div class='memo-container step69-grouped'>"
        )

        if memos_list:
            def is_done_memo(memo):
                return bool(
                    memo.get("is_strike", False)
                    or memo.get("is_done", False)
                    or memo.get("done", False)
                    or memo.get("completed", False)
                )

            important_memos = [
                m for m in memos_list
                if bool(m.get("is_important", False)) and not is_done_memo(m)
            ]
            general_memos = [
                m for m in memos_list
                if not bool(m.get("is_important", False)) and not is_done_memo(m)
            ]
            done_memos = [
                m for m in memos_list
                if is_done_memo(m)
            ]

            def memo_time_text(memo):
                raw_time = str(memo.get("created_at", "") or "")
                if not raw_time:
                    return ""
                try:
                    return (
                        datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                        .astimezone(kst_tz)
                        .strftime("%y.%m.%d %H:%M")
                    )
                except Exception:
                    return raw_time[:16]

            def memo_text_value(memo):
                return str(
                    memo.get("memo_text")
                    or memo.get("content")
                    or memo.get("text")
                    or ""
                ).replace("__STRIKE__|||", "")

            def render_memo_group(items, title, header_class, done=False):
                if not items:
                    return

                html_parts.append(
                    f"<details class='step69-memo-section' open>"
                    f"<summary class='step69-memo-summary {header_class}'>{title} ({len(items)}) ▲</summary>"
                    f"<div class='step69-memo-body'>"
                )

                for memo in items:
                    text = memo_text_value(memo)
                    is_imp = bool(memo.get("is_important", False))
                    prefix = "⭐ " if is_imp else "☆ "
                    if done:
                        prefix = "✔ " + prefix
                    time_str = memo_time_text(memo)
                    row_class = "step69-memo-row done" if done else "step69-memo-row"

                    html_parts.append(
                        f"<div class='{row_class}'>"
                        f"<div>{prefix}{step70_memo_text_html(text)}</div>"
                        f"<div style='font-size:11px; opacity:0.62; margin-top:4px;'>{html.escape(time_str)}</div>"
                        f"</div>"
                    )

                html_parts.append("</div></details>")

            render_memo_group(important_memos, "📌 중요 메모", "important")
            render_memo_group(general_memos, "▣ 일반 메모", "general")
            render_memo_group(done_memos, "✔ 완료 메모", "done", done=True)
        else:
            html_parts.append(
                f"<div style='padding:8px; color:{t['text']}; opacity:0.7;'>메모가 없습니다.</div>"
            )

        html_parts.append("</div></div>")

    st.markdown("".join(html_parts), unsafe_allow_html=True)


display_dashboard()

# === STEP91_WEB_VIEWER_FORCE_LAYOUT_THEME_START ===
def _step91_web_viewer_force_layout_theme_css():
    try:
        import streamlit as st
    except Exception:
        return

    def _theme_text():
        vals = []
        try:
            for k, v in st.session_state.items():
                ks = str(k).lower()
                if "theme" in ks or "테마" in str(k):
                    vals.append(str(v))
            for k in ["theme", "theme_name", "selected_theme", "current_theme", "app_theme", "mobile_theme", "테마"]:
                if k in st.session_state:
                    vals.append(str(st.session_state.get(k, "")))
        except Exception:
            pass
        return " ".join(vals).lower()

    t = _theme_text()
    p = {
        "bg":"#f8fbff", "cell":"#ffffff", "head":"#eaf3ff", "sub":"#f3f8ff",
        "border":"#8faaca", "text":"#10243f", "shadow":"rgba(54,96,146,.16)"
    }
    if any(x in t for x in ["dark", "다크", "black", "블랙", "night", "어두"]):
        p.update({"bg":"#101827", "cell":"#111c2e", "head":"#22314d", "sub":"#18243a", "border":"#54657f", "text":"#f4f7fb", "shadow":"rgba(0,0,0,.30)"})
    elif any(x in t for x in ["pink", "핑크", "러블리", "lovely", "rose", "로즈"]):
        p.update({"bg":"#fff7fb", "cell":"#fffefe", "head":"#ffe1ef", "sub":"#fff0f7", "border":"#e6a1c0", "text":"#682343", "shadow":"rgba(202,89,140,.17)"})
    elif any(x in t for x in ["green", "그린", "mint", "민트", "emerald", "에메랄드"]):
        p.update({"bg":"#f3fff8", "cell":"#ffffff", "head":"#dff8ea", "sub":"#effbf4", "border":"#8bc3a1", "text":"#143a27", "shadow":"rgba(41,132,82,.15)"})
    elif any(x in t for x in ["purple", "보라", "violet", "퍼플", "lavender", "라벤더"]):
        p.update({"bg":"#fbf7ff", "cell":"#ffffff", "head":"#eadfff", "sub":"#f4edff", "border":"#b69adf", "text":"#37205f", "shadow":"rgba(121,88,176,.16)"})
    elif any(x in t for x in ["orange", "오렌지", "yellow", "노랑", "옐로", "warm", "웜"]):
        p.update({"bg":"#fffaf1", "cell":"#ffffff", "head":"#fff0cf", "sub":"#fff7e6", "border":"#d9ac62", "text":"#53380a", "shadow":"rgba(184,129,38,.16)"})
    elif any(x in t for x in ["red", "레드", "coral", "코랄"]):
        p.update({"bg":"#fff7f6", "cell":"#ffffff", "head":"#ffe2dd", "sub":"#fff0ee", "border":"#dc978f", "text":"#64251f", "shadow":"rgba(197,82,69,.15)"})

    css = f"""
    <style>
    :root {{
      --s91-bg:{p['bg']}; --s91-cell:{p['cell']}; --s91-head:{p['head']};
      --s91-sub:{p['sub']}; --s91-border:{p['border']}; --s91-text:{p['text']}; --s91-shadow:{p['shadow']};
    }}

    /* 상단 달력/버튼 글자 세로 배치 방지 */
    div[data-testid="stHorizontalBlock"] .stButton button,
    div[data-testid="stHorizontalBlock"] .stButton button *,
    div[data-testid="stHorizontalBlock"] button,
    div[data-testid="stHorizontalBlock"] button *,
    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],
    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] *,
    div[data-testid="stHorizontalBlock"] [role="combobox"],
    div[data-testid="stHorizontalBlock"] [role="combobox"] * {{
      white-space: nowrap !important;
      word-break: keep-all !important;
      overflow-wrap: normal !important;
      text-align: center !important;
      line-height: 1.15 !important;
    }}
    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] {{ min-width:54px !important; }}
    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div {{
      min-width:54px !important; height:50px !important; padding-left:8px !important; padding-right:8px !important;
      align-items:center !important; justify-content:center !important;
    }}
    div[data-testid="stHorizontalBlock"] .stButton button {{ min-width:42px !important; padding-left:9px !important; padding-right:9px !important; }}

    /* 시간표 표 색상/레이아웃 강제 안정화 */
    div[data-testid="stMarkdownContainer"] table,
    .element-container table,
    table {{
      width:100% !important; max-width:100% !important; table-layout:fixed !important;
      border-collapse:collapse !important; background:var(--s91-bg) !important;
      border:1px solid var(--s91-border) !important; box-shadow:0 4px 14px var(--s91-shadow) !important;
      overflow:hidden !important;
    }}
    div[data-testid="stMarkdownContainer"] table th,
    div[data-testid="stMarkdownContainer"] table td,
    .element-container table th,
    .element-container table td,
    table th, table td {{
      box-sizing:border-box !important; max-width:0 !important; min-width:0 !important;
      overflow:hidden !important; white-space:normal !important; overflow-wrap:anywhere !important;
      word-break:break-word !important; vertical-align:middle !important; text-align:center !important;
      line-height:1.16 !important; padding:5px 3px !important;
      border:1px solid var(--s91-border) !important; background-color:var(--s91-cell) !important;
      font-size:clamp(10px,2.55vw,13px) !important;
    }}
    div[data-testid="stMarkdownContainer"] table th,
    .element-container table th,
    table th,
    div[data-testid="stMarkdownContainer"] table tr:first-child th,
    div[data-testid="stMarkdownContainer"] table tr:first-child td,
    div[data-testid="stMarkdownContainer"] table tr td:first-child,
    .element-container table tr:first-child th,
    .element-container table tr:first-child td,
    .element-container table tr td:first-child,
    table tr:first-child th, table tr:first-child td, table tr td:first-child {{
      background-color:var(--s91-head) !important; color:var(--s91-text) !important; font-weight:800 !important;
    }}
    div[data-testid="stMarkdownContainer"] table tr:nth-child(2) td,
    div[data-testid="stMarkdownContainer"] table tr:nth-child(3) td,
    .element-container table tr:nth-child(2) td,
    .element-container table tr:nth-child(3) td,
    table tr:nth-child(2) td, table tr:nth-child(3) td {{ background-color:var(--s91-sub) !important; }}
    div[data-testid="stMarkdownContainer"] table td *,
    div[data-testid="stMarkdownContainer"] table th *,
    .element-container table td *,
    .element-container table th *,
    table td *, table th * {{
      max-width:100% !important; min-width:0 !important; box-sizing:border-box !important;
      white-space:normal !important; overflow-wrap:anywhere !important; word-break:break-word !important;
    }}
    div[data-testid="stMarkdownContainer"] table tr:nth-child(3) td,
    div[data-testid="stMarkdownContainer"] table tr:nth-child(3) td *,
    .element-container table tr:nth-child(3) td,
    .element-container table tr:nth-child(3) td *,
    table tr:nth-child(3) td, table tr:nth-child(3) td * {{
      font-size:clamp(9px,2.25vw,11px) !important; line-height:1.10 !important; letter-spacing:-0.055em !important;
    }}
    div[data-testid="stMarkdownContainer"], .element-container {{ max-width:100% !important; overflow-x:hidden !important; }}
    @media (max-width:480px) {{
      table th, table td {{ padding-left:2px !important; padding-right:2px !important; }}
      table tr:nth-child(3) td, table tr:nth-child(3) td * {{ font-size:10px !important; letter-spacing:-0.06em !important; }}
    }}
    </style>
    """
    try:
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        pass

_step91_web_viewer_force_layout_theme_css()
# === STEP91_WEB_VIEWER_FORCE_LAYOUT_THEME_END ===




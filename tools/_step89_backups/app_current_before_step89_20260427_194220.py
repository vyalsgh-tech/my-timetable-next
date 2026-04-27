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
# [STEP88_SUPABASE_SSL_FALLBACK_START]
# 학교/기관망 SSL 검사로 Supabase HTTPS 인증서 검증이 실패하는 경우만 Supabase 요청을 1회 재시도합니다.
try:
    import requests as _step88_requests
    try:
        import urllib3 as _step88_urllib3
        _step88_urllib3.disable_warnings(_step88_urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        pass

    if not getattr(_step88_requests.sessions.Session.request, "_step88_ssl_fallback", False):
        _step88_original_request = _step88_requests.sessions.Session.request

        def _step88_request_with_ssl_fallback(self, method, url, **kwargs):
            try:
                return _step88_original_request(self, method, url, **kwargs)
            except _step88_requests.exceptions.SSLError:
                if "supabase.co" in str(url):
                    kwargs["verify"] = False
                    return _step88_original_request(self, method, url, **kwargs)
                raise

        _step88_request_with_ssl_fallback._step88_ssl_fallback = True
        _step88_requests.sessions.Session.request = _step88_request_with_ssl_fallback
except Exception:
    pass
# [STEP88_SUPABASE_SSL_FALLBACK_END]

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
        st.markdown(
            f"""
            <div class="step69-title-row">
                <div class="step69-title-main">
                    🏫 <b>명덕외고 시간표 뷰어</b>
                    <span class="step69-title-teacher">({html.escape(teacher_name)} 선생님)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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
st.set_page_config(page_title="명덕외고 모바일 시간표", page_icon="🏫", layout="centered")
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
                        f"<div>{prefix}{html.escape(text).replace(chr(10), '<br>')}</div>"
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

# [STEP77_WEB_DOM_FINAL_START]
try:
    import streamlit.components.v1 as components
    components.html(
        r"""
        <script>
        (function() {
            function docRoot() {
                try { return window.parent.document; } catch(e) { return document; }
            }

            function visible(el) {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                return r.width > 1 && r.height > 1;
            }

            function injectStyle(doc) {
                if (doc.getElementById('step77-web-final-style')) return;
                const style = doc.createElement('style');
                style.id = 'step77-web-final-style';
                style.textContent = `
                    .step77-title-row {
                        width: min(450px, 100%);
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        gap: 8px;
                        margin: 0 0 8px 0;
                    }
                    .step77-title-host {
                        flex: 1 1 auto;
                        min-width: 0;
                    }
                    .step77-title-host * {
                        white-space: nowrap !important;
                    }
                    .step77-clock-pill {
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
                        font-size: 12px;
                        line-height: 1.1;
                    }
                    .step77-clock-time {
                        font-size: 13px;
                        font-weight: 800;
                    }
                    .step77-clock-state {
                        opacity: 0.92;
                    }

                    /* 달력 selectbox 폭/텍스트 강제 */
                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-baseweb="select"]),
                    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(div[data-testid="stSelectbox"]) {
                        min-width: 76px !important;
                        width: 76px !important;
                        flex: 0 0 76px !important;
                    }
                    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"],
                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"],
                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] > div,
                    div[data-testid="stHorizontalBlock"] div[role="button"] {
                        min-width: 70px !important;
                        width: 70px !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                    }
                    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] *,
                    div[data-testid="stHorizontalBlock"] div[data-baseweb="select"] *,
                    div[data-testid="stHorizontalBlock"] div[role="button"] *,
                    div[data-testid="stHorizontalBlock"] button,
                    div[data-testid="stHorizontalBlock"] button * {
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                    }

                    /* 학사일정 칸 넘침 방지: 표 전체 디자인은 유지하고 내용만 안쪽에 가둠 */
                    table.mobile-table th,
                    table.mobile-table td {
                        overflow: hidden !important;
                    }
                    table.mobile-table td *,
                    table.mobile-table th * {
                        max-width: 100% !important;
                        box-sizing: border-box !important;
                    }

                    @media (max-width: 430px) {
                        .step77-clock-state { display: none; }
                        .step77-clock-pill { padding: 4px 8px; }
                    }
                `;
                doc.head.appendChild(style);
            }

            function currentInfo() {
                const now = new Date();
                const mins = now.getHours() * 60 + now.getMinutes();
                const periods = [
                    ['1교시', '08:00', '08:50'],
                    ['2교시', '09:00', '09:50'],
                    ['3교시', '10:00', '10:50'],
                    ['4교시', '11:00', '11:50'],
                    ['점심', '11:50', '12:40'],
                    ['5교시', '12:40', '13:30'],
                    ['6교시', '13:40', '14:30'],
                    ['7교시', '14:40', '15:30'],
                    ['8교시', '16:00', '16:50'],
                    ['9교시', '17:00', '17:50']
                ];

                function toMin(t) {
                    const p = t.split(':').map(Number);
                    return p[0] * 60 + p[1];
                }

                let state = '쉬는시간';
                for (const p of periods) {
                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {
                        state = p[0] + ' · ' + p[1] + '~' + p[2];
                        break;
                    }
                }
                if (mins < 8 * 60) state = '수업 전';
                if (mins >= 17 * 60 + 50) state = '방과 후';

                const hh = String(now.getHours()).padStart(2, '0');
                const mm = String(now.getMinutes()).padStart(2, '0');
                return { clock: hh + ':' + mm, state };
            }

            function findTitle(doc) {
                const nodes = Array.from(doc.querySelectorAll('h1,h2,h3,p,span,div'));
                return nodes.find(el => {
                    if (!visible(el)) return false;
                    if (el.closest('.step77-title-row')) return false;
                    const txt = (el.innerText || '').trim();
                    return txt.includes('명덕외고 시간표 뷰어');
                }) || null;
            }

            function patchHeader(doc) {
                const info = currentInfo();

                let row = doc.querySelector('.step77-title-row');
                if (!row) {
                    const title = findTitle(doc);
                    if (!title || !title.parentNode) return;

                    row = doc.createElement('div');
                    row.className = 'step77-title-row';

                    const host = doc.createElement('div');
                    host.className = 'step77-title-host';

                    title.parentNode.insertBefore(row, title);
                    row.appendChild(host);
                    host.appendChild(title);
                }

                let pill = row.querySelector('.step77-clock-pill');
                if (!pill) {
                    pill = doc.createElement('div');
                    pill.className = 'step77-clock-pill';
                    pill.innerHTML = '<span class="step77-clock-time"></span><span class="step77-clock-state"></span>';
                    row.appendChild(pill);
                }

                const timeEl = pill.querySelector('.step77-clock-time');
                const stateEl = pill.querySelector('.step77-clock-state');
                if (timeEl) timeEl.textContent = info.clock;
                if (stateEl) stateEl.textContent = info.state;

                for (const el of Array.from(doc.querySelectorAll('div,p,span'))) {
                    if (el.closest('.step77-title-row')) continue;
                    const txt = (el.innerText || '').trim();
                    if ((txt === '방과 후' || txt === '수업 전' || txt === '쉬는시간') && visible(el)) {
                        const r = el.getBoundingClientRect();
                        if (r.top < 90) el.style.display = 'none';
                    }
                }
            }

            function fixCalendar(doc) {
                const nodes = Array.from(doc.querySelectorAll('button, [data-testid="stSelectbox"], [data-baseweb="select"], div[role="button"], span, div'));
                const targets = nodes.filter(el => {
                    const txt = (el.innerText || el.textContent || '').trim();
                    return /^달\s*력$/.test(txt);
                });

                for (const el of targets) {
                    if ((el.innerText || '').includes('\n')) {
                        try { el.innerText = '달력'; } catch(e) {}
                    }

                    let cur = el;
                    for (let i = 0; i < 10 && cur; i++, cur = cur.parentElement) {
                        cur.style.setProperty('white-space', 'nowrap', 'important');
                        cur.style.setProperty('word-break', 'keep-all', 'important');
                        cur.style.setProperty('overflow-wrap', 'normal', 'important');
                        cur.style.setProperty('writing-mode', 'horizontal-tb', 'important');

                        const txt = (cur.innerText || '').trim();
                        if (/달\s*력/.test(txt) && txt.length <= 12) {
                            cur.style.setProperty('min-width', '76px', 'important');
                            cur.style.setProperty('width', '76px', 'important');
                            cur.style.setProperty('flex', '0 0 76px', 'important');
                        }
                        if (cur.getAttribute && cur.getAttribute('data-testid') === 'stHorizontalBlock') break;
                    }
                }
            }

            function fixAcademicScheduleOverflow(doc) {
                const table = Array.from(doc.querySelectorAll('table')).find(t => {
                    const txt = t.innerText || '';
                    return txt.includes('교시') && txt.includes('학사일정');
                });
                if (!table) return;

                const rows = Array.from(table.querySelectorAll('tr'));
                const target = rows.find(r => (r.innerText || '').includes('학사일정'));
                if (!target) return;

                for (const cell of Array.from(target.children)) {
                    cell.style.setProperty('overflow', 'hidden', 'important');
                    cell.style.setProperty('word-break', 'keep-all', 'important');
                    cell.style.setProperty('overflow-wrap', 'anywhere', 'important');
                    cell.style.setProperty('line-height', '1.18', 'important');

                    const txt = (cell.innerText || '').trim();
                    if (txt && !txt.includes('학사일정')) {
                        cell.style.setProperty('font-size', '10px', 'important');
                    }

                    for (const child of Array.from(cell.querySelectorAll('*'))) {
                        child.style.setProperty('max-width', '100%', 'important');
                        child.style.setProperty('white-space', 'normal', 'important');
                        child.style.setProperty('word-break', 'keep-all', 'important');
                        child.style.setProperty('overflow-wrap', 'anywhere', 'important');
                    }
                }
            }

            function parseMemoSpanText(doc) {
                const allowed = /<span\s+style=["']\s*(color|background-color)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;?\s*["']>(.*?)<\/span>/gis;
                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
                const targets = [];
                let node;

                while ((node = walker.nextNode())) {
                    const value = node.nodeValue || '';
                    allowed.lastIndex = 0;
                    if (value.includes('<span') && allowed.test(value)) targets.push(node);
                }

                for (const textNode of targets) {
                    const text = textNode.nodeValue || '';
                    const frag = doc.createDocumentFragment();
                    let last = 0;
                    allowed.lastIndex = 0;
                    let m;

                    while ((m = allowed.exec(text))) {
                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));

                        const span = doc.createElement('span');
                        span.style.setProperty(m[1].toLowerCase(), m[2]);
                        span.textContent = m[3];
                        frag.appendChild(span);

                        last = allowed.lastIndex;
                    }

                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));
                    textNode.parentNode.replaceChild(frag, textNode);
                }
            }

            function run() {
                const doc = docRoot();
                injectStyle(doc);
                patchHeader(doc);
                fixCalendar(doc);
                fixAcademicScheduleOverflow(doc);
                parseMemoSpanText(doc);
            }

            run();
            setTimeout(run, 200);
            setTimeout(run, 700);
            setTimeout(run, 1400);
            setTimeout(run, 2500);
        })();
        </script>
        """,
        height=1,
        width=1,
    )
except Exception:
    pass
# [STEP77_WEB_DOM_FINAL_END]

# [STEP88_WEB_SINGLE_STABLE_DOM_START]
try:
    import streamlit.components.v1 as components
    components.html(
        r"""
        <script>
        (function() {
            const STYLE_ID = 'step88-single-stable-style';
            const CLOCK_ID = 'step88-clock-fixed';

            const PALETTES = {
                light: {
                    tableWrap:'#dbe8f7', th1:'#eaf3ff', th2:'#d7e6f8', td1:'#ffffff', td2:'#fafcff', line:'#1f2937', text:'#0f172a',
                    calBg:'#f5f0ff', calText:'#5b21b6', calBorder:'#ddd6fe',
                    memoBg:'#2563eb', memoText:'#ffffff',
                    searchBg:'#fff4dd', searchText:'#8a4b00', searchBorder:'#f2cf96',
                    eightBg:'#eef2ff', eightText:'#1e40af', eightBorder:'#c7d2fe',
                    activeBg:'#dbeafe', activeBorder:'#2563eb', activeText:'#0f172a', soonBg:'#fff7ed', soonBorder:'#f97316'
                },
                dark: {
                    tableWrap:'#253145', th1:'#334155', th2:'#243041', td1:'#111827', td2:'#172033', line:'#cbd5e1', text:'#f8fafc',
                    calBg:'#ede9fe', calText:'#4c1d95', calBorder:'#c4b5fd',
                    memoBg:'#e11d48', memoText:'#ffffff',
                    searchBg:'#f97316', searchText:'#ffffff', searchBorder:'#ea580c',
                    eightBg:'#dbeafe', eightText:'#1e3a8a', eightBorder:'#93c5fd',
                    activeBg:'#1e3a8a', activeBorder:'#60a5fa', activeText:'#f8fafc', soonBg:'#7c2d12', soonBorder:'#fdba74'
                },
                green: {
                    tableWrap:'#cfe7dc', th1:'#dcfce7', th2:'#bbf7d0', td1:'#ffffff', td2:'#f0fdf4', line:'#14532d', text:'#052e16',
                    calBg:'#f5f3ff', calText:'#5b21b6', calBorder:'#ddd6fe',
                    memoBg:'#ea580c', memoText:'#ffffff',
                    searchBg:'#f97316', searchText:'#ffffff', searchBorder:'#ea580c',
                    eightBg:'#d9f99d', eightText:'#365314', eightBorder:'#a3e635',
                    activeBg:'#bbf7d0', activeBorder:'#16a34a', activeText:'#052e16', soonBg:'#fef3c7', soonBorder:'#d97706'
                },
                orange: {
                    tableWrap:'#fde7c8', th1:'#ffedd5', th2:'#fed7aa', td1:'#fffaf5', td2:'#fff7ed', line:'#7c2d12', text:'#431407',
                    calBg:'#f5f3ff', calText:'#5b21b6', calBorder:'#ddd6fe',
                    memoBg:'#c2410c', memoText:'#ffffff',
                    searchBg:'#ea580c', searchText:'#ffffff', searchBorder:'#c2410c',
                    eightBg:'#ffedd5', eightText:'#7c2d12', eightBorder:'#fdba74',
                    activeBg:'#fed7aa', activeBorder:'#ea580c', activeText:'#431407', soonBg:'#fef3c7', soonBorder:'#d97706'
                },
                pink: {
                    tableWrap:'#ffe1ec', th1:'#ffe6ef', th2:'#ffd3e2', td1:'#fffefe', td2:'#fff7fb', line:'#7f1d43', text:'#4a1d2f',
                    calBg:'#fff1f7', calText:'#be185d', calBorder:'#f9a8d4',
                    memoBg:'#ec4899', memoText:'#ffffff',
                    searchBg:'#fff1e6', searchText:'#9a3412', searchBorder:'#fdba74',
                    eightBg:'#fdf2f8', eightText:'#9d174d', eightBorder:'#fbcfe8',
                    activeBg:'#fbcfe8', activeBorder:'#ec4899', activeText:'#4a1d2f', soonBg:'#fff1e6', soonBorder:'#fb923c'
                },
                blue: {
                    tableWrap:'#dbeafe', th1:'#e0f2fe', th2:'#bae6fd', td1:'#ffffff', td2:'#f8fbff', line:'#1e3a8a', text:'#0f172a',
                    calBg:'#f5f3ff', calText:'#5b21b6', calBorder:'#ddd6fe',
                    memoBg:'#2563eb', memoText:'#ffffff',
                    searchBg:'#fff7ed', searchText:'#9a3412', searchBorder:'#fed7aa',
                    eightBg:'#e0f2fe', eightText:'#075985', eightBorder:'#7dd3fc',
                    activeBg:'#bfdbfe', activeBorder:'#2563eb', activeText:'#0f172a', soonBg:'#fef3c7', soonBorder:'#d97706'
                }
            };

            function docRoot() {
                try { return window.parent.document; } catch(e) { return document; }
            }

            function visible(el) {
                if (!el) return false;
                const s = window.getComputedStyle(el);
                if (s.display === 'none' || s.visibility === 'hidden') return false;
                const r = el.getBoundingClientRect();
                return r.width > 1 && r.height > 1;
            }

            function textOf(el) {
                return ((el && (el.innerText || el.textContent)) || '').replace(/\s+/g, ' ').trim();
            }

            function parseRgb(value) {
                const m = (value || '').match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
                if (!m) return null;
                return { r:+m[1], g:+m[2], b:+m[3] };
            }

            function lum(c) {
                if (!c) return 255;
                return 0.299*c.r + 0.587*c.g + 0.114*c.b;
            }

            function toolbar(doc) {
                const bars = Array.from(doc.querySelectorAll('div[data-testid="stHorizontalBlock"]')).filter(visible);
                return bars.find(b => {
                    const t = textOf(b);
                    return t.includes('오늘') && t.includes('달력') && t.includes('메모');
                }) || null;
            }

            function tableEl(doc) {
                return Array.from(doc.querySelectorAll('table')).find(t => {
                    const x = textOf(t);
                    return x.includes('교시') && x.includes('학사일정') && (x.includes('월') || x.includes('화'));
                }) || null;
            }

            function paletteKey(doc) {
                const bodyText = doc.body ? (doc.body.innerText || '') : '';
                if (bodyText.includes('러블리 핑크')) return 'pink';

                const bar = toolbar(doc);
                const bg = parseRgb(bar ? getComputedStyle(bar).backgroundColor : getComputedStyle(doc.body).backgroundColor);
                if (bg) {
                    if (lum(bg) < 95) return 'dark';
                    if (bg.g > bg.r + 20 && bg.g >= bg.b) return 'green';
                    if (bg.r > 210 && bg.g > 145 && bg.b < 125) return 'orange';
                    if (bg.b > bg.r + 10 && bg.b > bg.g - 5) return 'blue';
                    if (bg.r > 230 && bg.b > 210 && bg.g < 225) return 'pink';
                }

                const lower = bodyText.toLowerCase();
                if (lower.includes('dark') || bodyText.includes('다크') || bodyText.includes('블랙') || bodyText.includes('야간')) return 'dark';
                if (bodyText.includes('그린') || bodyText.includes('초록') || bodyText.includes('숲')) return 'green';
                if (bodyText.includes('오렌지') || bodyText.includes('주황')) return 'orange';
                if (bodyText.includes('블루') || bodyText.includes('파랑') || bodyText.includes('윈도우')) return 'blue';
                return 'light';
            }

            function nowInfo() {
                const now = new Date();
                const mins = now.getHours() * 60 + now.getMinutes();
                const periods = [
                    ['1교시', '08:00', '08:50'],
                    ['2교시', '09:00', '09:50'],
                    ['3교시', '10:00', '10:50'],
                    ['4교시', '11:00', '11:50'],
                    ['점심', '11:50', '12:40'],
                    ['5교시', '12:40', '13:30'],
                    ['6교시', '13:40', '14:30'],
                    ['7교시', '14:40', '15:30'],
                    ['8교시', '16:00', '16:50'],
                    ['9교시', '17:00', '17:50']
                ];
                function toMin(t) {
                    const p = t.split(':').map(Number);
                    return p[0] * 60 + p[1];
                }
                let state = '쉬는시간';
                for (const p of periods) {
                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {
                        state = p[0];
                        break;
                    }
                }
                if (mins < 8 * 60) state = '수업 전';
                if (mins >= 17 * 60 + 50) state = '방과 후';
                return {
                    text: String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0') + ' ' + state
                };
            }

            function injectStyle(doc) {
                if (doc.getElementById(STYLE_ID)) return;
                const style = doc.createElement('style');
                style.id = STYLE_ID;
                style.textContent = `
                    html {
                        overflow-anchor: none !important;
                    }

                    iframe[title*="streamlit"] {
                        max-height: 1px !important;
                    }

                    #${CLOCK_ID} {
                        position: fixed !important;
                        right: max(10px, calc((100vw - min(450px, 100vw)) / 2 + 8px)) !important;
                        top: 8px !important;
                        z-index: 999999 !important;
                        display: inline-flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        padding: 5px 12px !important;
                        border-radius: 999px !important;
                        border: 1px solid rgba(96, 165, 250, 0.36) !important;
                        background: linear-gradient(180deg, rgba(250,252,255,0.98), rgba(232,240,255,0.96)) !important;
                        color: #1d4ed8 !important;
                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.12) !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                        font-size: 14px !important;
                        line-height: 1.15 !important;
                        font-weight: 900 !important;
                        letter-spacing: -0.1px !important;
                        text-align: center !important;
                        pointer-events: none !important;
                    }

                    .s88-toolbar {
                        display: flex !important;
                        flex-direction: row !important;
                        flex-wrap: nowrap !important;
                        align-items: center !important;
                        justify-content: flex-start !important;
                        gap: 3px !important;
                        width: min(450px, 100%) !important;
                        box-sizing: border-box !important;
                    }
                    .s88-toolbar > div {
                        width: auto !important;
                        min-width: 0 !important;
                        max-width: none !important;
                        flex: 0 0 auto !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        margin: 0 !important;
                    }
                    .s88-nav-small {
                        width: 24px !important;
                        min-width: 24px !important;
                        max-width: 24px !important;
                        flex-basis: 24px !important;
                    }
                    .s88-sync-small {
                        width: 34px !important;
                        min-width: 34px !important;
                        max-width: 34px !important;
                        flex-basis: 34px !important;
                    }

                    body.step88-theme table.mobile-table {
                        color: var(--s88-text) !important;
                        border-color: var(--s88-line) !important;
                        table-layout: fixed !important;
                    }
                    body.step88-theme table.mobile-table th {
                        background-image: linear-gradient(180deg, var(--s88-th1), var(--s88-th2)) !important;
                        color: var(--s88-text) !important;
                        border-color: var(--s88-line) !important;
                    }
                    body.step88-theme table.mobile-table td {
                        background-image: linear-gradient(180deg, var(--s88-td1), var(--s88-td2)) !important;
                        color: var(--s88-text) !important;
                        border-color: var(--s88-line) !important;
                        height: 58px !important;
                        min-height: 58px !important;
                        vertical-align: middle !important;
                        box-sizing: border-box !important;
                        overflow: hidden !important;
                    }
                    body.step88-theme div:has(> table.mobile-table) {
                        background: var(--s88-table-wrap) !important;
                    }

                    .s88-text-fit {
                        white-space: normal !important;
                        word-break: keep-all !important;
                        overflow-wrap: anywhere !important;
                        line-height: 1.15 !important;
                        letter-spacing: -0.25px !important;
                    }
                    .s88-text-fit.long {
                        font-size: 10px !important;
                        line-height: 1.12 !important;
                        letter-spacing: -0.45px !important;
                    }
                    .s88-text-fit.very-long {
                        font-size: 8.5px !important;
                        line-height: 1.08 !important;
                        letter-spacing: -0.65px !important;
                    }
                    .s88-query-fit {
                        font-size: 8.5px !important;
                        line-height: 1.08 !important;
                        letter-spacing: -0.65px !important;
                        white-space: normal !important;
                        word-break: keep-all !important;
                        overflow-wrap: anywhere !important;
                        overflow: hidden !important;
                        text-align: center !important;
                        vertical-align: middle !important;
                        padding: 1px 2px !important;
                    }
                    .s88-query-fit.extreme {
                        font-size: 7.5px !important;
                        letter-spacing: -0.8px !important;
                        line-height: 1.03 !important;
                    }

                    .s88-btn-calendar, .s88-btn-memo, .s88-btn-search, .s88-btn-89 {
                        box-sizing: border-box !important;
                        min-height: 40px !important;
                        height: 40px !important;
                        border-radius: 7px !important;
                        font-weight: 800 !important;
                        text-align: center !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                    }
                    .s88-btn-calendar *, .s88-btn-memo *, .s88-btn-search *, .s88-btn-89 * {
                        color: inherit !important;
                        -webkit-text-fill-color: currentColor !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        text-align: center !important;
                    }
                    .s88-btn-calendar {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                        flex: 0 0 58px !important;
                        background: var(--s88-cal-bg) !important;
                        border: 1px solid var(--s88-cal-border) !important;
                        color: var(--s88-cal-text) !important;
                        padding: 0 !important;
                        position: relative !important;
                        overflow: hidden !important;
                    }
                    .s88-btn-memo {
                        background: var(--s88-memo-bg) !important;
                        border: 1px solid var(--s88-memo-bg) !important;
                        color: var(--s88-memo-text) !important;
                    }
                    .s88-btn-search {
                        background: var(--s88-search-bg) !important;
                        border: 1px solid var(--s88-search-border) !important;
                        color: var(--s88-search-text) !important;
                    }
                    .s88-btn-89 {
                        background: var(--s88-eight-bg) !important;
                        border: 1px solid var(--s88-eight-border) !important;
                        color: var(--s88-eight-text) !important;
                    }

                    .s88-calendar-shell {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                        flex: 0 0 58px !important;
                        position: relative !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        padding: 0 !important;
                        box-sizing: border-box !important;
                    }
                    .s88-calendar-shell > * {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                    }
                    .s88-calendar-shell [data-baseweb="select"],
                    .s88-calendar-shell [role="button"],
                    .s88-calendar-shell button {
                        width: 58px !important;
                        min-width: 58px !important;
                        max-width: 58px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        grid-template-columns: 1fr !important;
                        padding-left: 0 !important;
                        padding-right: 0 !important;
                        color: transparent !important;
                        -webkit-text-fill-color: transparent !important;
                    }
                    .s88-calendar-shell [data-baseweb="select"] *,
                    .s88-calendar-shell [role="button"] *,
                    .s88-calendar-shell button * {
                        color: transparent !important;
                        -webkit-text-fill-color: transparent !important;
                    }
                    .s88-calendar-shell svg,
                    .s88-calendar-shell [aria-hidden="true"],
                    .s88-remove {
                        display: none !important;
                        width: 0 !important;
                        min-width: 0 !important;
                        max-width: 0 !important;
                        flex: 0 0 0 !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .s88-calendar-overlay {
                        position: absolute !important;
                        left: 50% !important;
                        top: 50% !important;
                        transform: translate(-50%, -50%) !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        width: max-content !important;
                        pointer-events: none !important;
                        color: var(--s88-cal-text) !important;
                        -webkit-text-fill-color: var(--s88-cal-text) !important;
                        font-size: 14px !important;
                        font-weight: 800 !important;
                        line-height: 1 !important;
                        text-align: center !important;
                        z-index: 3 !important;
                    }

                    table.mobile-table .s88-current-col {
                        box-shadow: inset 0 3px 0 var(--s88-active-border) !important;
                    }
                    table.mobile-table .s88-current-rowhead,
                    table.mobile-table .s88-current-cell {
                        background-image: linear-gradient(180deg, var(--s88-active-bg), var(--s88-active-bg)) !important;
                        color: var(--s88-active-text) !important;
                        box-shadow: inset 0 0 0 2px var(--s88-active-border) !important;
                    }
                    table.mobile-table .s88-soon-cell,
                    table.mobile-table .s88-soon-rowhead {
                        background-image: linear-gradient(180deg, var(--s88-soon-bg), var(--s88-soon-bg)) !important;
                        box-shadow: inset 0 0 0 2px var(--s88-soon-border) !important;
                    }
                    table.mobile-table .s88-current-rowhead,
                    table.mobile-table .s88-soon-rowhead {
                        position: relative !important;
                    }
                    .s88-period-badge {
                        position: absolute !important;
                        left: 50% !important;
                        bottom: 2px !important;
                        transform: translateX(-50%) !important;
                        display: inline-flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        width: auto !important;
                        max-width: 92% !important;
                        padding: 1px 5px !important;
                        border-radius: 999px !important;
                        font-size: 9px !important;
                        font-weight: 900 !important;
                        background: var(--s88-active-border) !important;
                        color: #fff !important;
                        line-height: 1.1 !important;
                        white-space: nowrap !important;
                        pointer-events: none !important;
                    }
                    .s88-period-badge.soon {
                        background: var(--s88-soon-border) !important;
                    }
                `;
                doc.head.appendChild(style);
            }

            function applyVars(doc) {
                const key = paletteKey(doc);
                const p = PALETTES[key] || PALETTES.light;
                doc.body.classList.add('step88-theme');
                const vars = {
                    '--s88-table-wrap': p.tableWrap, '--s88-th1': p.th1, '--s88-th2': p.th2, '--s88-td1': p.td1, '--s88-td2': p.td2,
                    '--s88-line': p.line, '--s88-text': p.text,
                    '--s88-cal-bg': p.calBg, '--s88-cal-text': p.calText, '--s88-cal-border': p.calBorder,
                    '--s88-memo-bg': p.memoBg, '--s88-memo-text': p.memoText,
                    '--s88-search-bg': p.searchBg, '--s88-search-text': p.searchText, '--s88-search-border': p.searchBorder,
                    '--s88-eight-bg': p.eightBg, '--s88-eight-text': p.eightText, '--s88-eight-border': p.eightBorder,
                    '--s88-active-bg': p.activeBg, '--s88-active-border': p.activeBorder, '--s88-active-text': p.activeText,
                    '--s88-soon-bg': p.soonBg, '--s88-soon-border': p.soonBorder
                };
                for (const [k, v] of Object.entries(vars)) doc.body.style.setProperty(k, v);
            }

            function hideOldClocks(doc) {
                const known = [
                    'step80-clock-fixed','step79-clock-fixed','step78-clock-fixed','step77-clock-fixed',
                    'step86-clock-fixed','step85-clock-fixed','step84-clock-fixed','step87-clock-fixed'
                ];
                for (const id of known) {
                    const el = doc.getElementById(id);
                    if (el) el.remove();
                }
                const stateTexts = new Set(['수업 전','방과 후','쉬는시간','1교시','2교시','3교시','4교시','점심','5교시','6교시','7교시','8교시','9교시']);
                for (const el of Array.from(doc.querySelectorAll('div,p,span'))) {
                    const t = (el.innerText || '').trim();
                    if (!stateTexts.has(t)) continue;
                    const r = el.getBoundingClientRect();
                    if (r.top < 100 && r.left > window.innerWidth * 0.45) {
                        el.style.setProperty('display', 'none', 'important');
                    }
                }
            }

            function updateClock(doc) {
                hideOldClocks(doc);
                let clock = doc.getElementById(CLOCK_ID);
                if (!clock) {
                    clock = doc.createElement('div');
                    clock.id = CLOCK_ID;
                    doc.body.appendChild(clock);
                }
                clock.textContent = nowInfo().text;
            }

            function classify(child) {
                const t = textOf(child);
                const html = child.innerHTML || '';
                if (t.includes('오늘')) return 'today';
                if (t.includes('달력')) return 'calendar';
                if (t.includes('메모')) return 'memo';
                if (t.includes('조회')) return 'search';
                if (t.includes('8·9') || t.includes('8-9') || t === '89' || t.includes('89')) return '89';
                if (t.includes('⚙') || t.includes('설정')) return 'settings';
                if (/refresh|sync|rotate|reload|arrow-repeat|counterclockwise|clockwise/i.test(html) || t === '↻' || t === '⟳' || t === '🔄') return 'sync';
                if (t === '' || t.length <= 2) return 'icon';
                return 'other';
            }

            function target(child) {
                return child.querySelector('button,[role="button"],div[data-baseweb="select"]') || child;
            }

            function calendar(child, doc) {
                child.classList.add('s88-calendar-shell');
                const btn = target(child);
                btn.classList.add('s88-btn-calendar');

                const removable = [];
                for (const svg of Array.from(child.querySelectorAll('svg'))) removable.push(svg);
                for (const el of Array.from(child.querySelectorAll('span,div,p'))) {
                    const t = (el.textContent || '').trim();
                    if (/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test(t)) removable.push(el);
                }
                for (const el of removable) {
                    try { el.remove(); }
                    catch(e) {
                        el.classList.add('s88-remove');
                        el.style.setProperty('display', 'none', 'important');
                    }
                }

                let overlay = child.querySelector('.s88-calendar-overlay');
                if (!overlay) {
                    overlay = doc.createElement('span');
                    overlay.className = 's88-calendar-overlay';
                    overlay.textContent = '달력';
                    child.appendChild(overlay);
                } else {
                    overlay.textContent = '달력';
                }
            }

            function fixToolbar(doc) {
                const bar = toolbar(doc);
                if (!bar) return;

                bar.classList.add('s88-toolbar');

                const children = Array.from(bar.children || []);
                let todayIdx = -1;
                children.forEach((child, idx) => {
                    if (classify(child) === 'today') todayIdx = idx;
                });

                let leftArrowUsed = false;
                let rightArrowUsed = false;
                let syncUsed = false;

                children.forEach((child, idx) => {
                    const kind = classify(child);
                    const btn = target(child);
                    let order = 500 + idx;

                    child.classList.remove('s88-nav-small','s88-sync-small');

                    if (kind === 'today') order = 20;
                    else if (kind === 'calendar') {
                        order = 40;
                        calendar(child, doc);
                    } else if (kind === 'memo') {
                        order = 60;
                        btn.classList.add('s88-btn-memo');
                    } else if (kind === 'search') {
                        order = 70;
                        btn.classList.add('s88-btn-search');
                    } else if (kind === '89') {
                        order = 80;
                        btn.classList.add('s88-btn-89');
                    } else if (kind === 'sync') {
                        order = 90;
                        child.classList.add('s88-sync-small');
                        syncUsed = true;
                    } else if (kind === 'settings') {
                        order = 100;
                    } else if (kind === 'icon') {
                        if (todayIdx >= 0 && idx < todayIdx && !leftArrowUsed) {
                            order = 10;
                            child.classList.add('s88-nav-small');
                            leftArrowUsed = true;
                        } else if (todayIdx >= 0 && idx > todayIdx && !rightArrowUsed) {
                            order = 30;
                            child.classList.add('s88-nav-small');
                            rightArrowUsed = true;
                        } else if (!syncUsed) {
                            order = 90;
                            child.classList.add('s88-sync-small');
                            syncUsed = true;
                        }
                    }

                    child.style.setProperty('order', String(order), 'important');
                });
            }

            function parseMemoColor(doc) {
                const allowed = /<span\s+style=["']\s*(color|background-color)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;?\s*["']>(.*?)<\/span>/gis;

                const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT);
                const nodes = [];
                let node;
                while ((node = walker.nextNode())) {
                    const v = node.nodeValue || '';
                    allowed.lastIndex = 0;
                    if (v.includes('<span') && allowed.test(v)) nodes.push(node);
                }
                for (const textNode of nodes) {
                    const text = textNode.nodeValue || '';
                    const frag = doc.createDocumentFragment();
                    let last = 0;
                    allowed.lastIndex = 0;
                    let m;
                    while ((m = allowed.exec(text))) {
                        if (m.index > last) frag.appendChild(doc.createTextNode(text.slice(last, m.index)));
                        const span = doc.createElement('span');
                        span.style.setProperty(m[1].toLowerCase(), m[2]);
                        span.textContent = m[3];
                        frag.appendChild(span);
                        last = allowed.lastIndex;
                    }
                    if (last < text.length) frag.appendChild(doc.createTextNode(text.slice(last)));
                    if (textNode.parentNode) textNode.parentNode.replaceChild(frag, textNode);
                }

                const entityRe = /&lt;span\s+style=(?:&quot;|")\s*(color|background-color)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;?\s*(?:&quot;|")&gt;([\s\S]*?)&lt;\/span&gt;/gi;
                for (const el of Array.from(doc.querySelectorAll('div,p,span'))) {
                    if (!el.innerHTML || !el.innerHTML.includes('&lt;span')) continue;
                    el.innerHTML = el.innerHTML.replace(entityRe, function(_, prop, color, content) {
                        return '<span style="' + prop + ':' + color + '">' + content + '</span>';
                    });
                }
            }

            function parseMinutes(timeText) {
                const m = String(timeText || '').match(/(\d{1,2}):(\d{2})/);
                if (!m) return null;
                return parseInt(m[1], 10) * 60 + parseInt(m[2], 10);
            }

            function rowRange(row) {
                const first = row.children && row.children.length ? row.children[0] : null;
                if (!first) return null;
                const times = (first.innerText || '').match(/\d{1,2}:\d{2}/g);
                if (!times || times.length < 2) return null;
                return { start: parseMinutes(times[0]), end: parseMinutes(times[1]) };
            }

            function todayColumnIndex() {
                const d = new Date().getDay();
                if (d < 1 || d > 5) return -1;
                return d;
            }

            function cleanupOldArtifacts(table) {
                const classes = [
                    's84-current-col','s84-current-rowhead','s84-current-cell','s84-soon-cell','s84-soon-rowhead',
                    's85-current-col','s85-current-rowhead','s85-current-cell','s85-soon-cell','s85-soon-rowhead',
                    's86-current-col','s86-current-rowhead','s86-current-cell','s86-soon-cell','s86-soon-rowhead',
                    's87-current-col','s87-current-rowhead','s87-current-cell','s87-soon-cell','s87-soon-rowhead',
                    's88-current-col','s88-current-rowhead','s88-current-cell','s88-soon-cell','s88-soon-rowhead'
                ];
                for (const el of Array.from(table.querySelectorAll('.' + classes.join(',.')))) {
                    el.classList.remove(...classes);
                }
                for (const b of Array.from(table.querySelectorAll('.s84-period-badge,.s85-period-badge,.s86-period-badge,.s87-period-badge,.s88-period-badge'))) b.remove();
                for (const br of Array.from(table.querySelectorAll('br[data-s84-period-br],br[data-s85-period-br],br[data-s86-period-br],br[data-s87-period-br],br[data-s88-period-br]'))) br.remove();
            }

            function highlightCurrentPeriod(doc) {
                const table = tableEl(doc);
                if (!table) return;

                cleanupOldArtifacts(table);

                const col = todayColumnIndex();
                const rows = Array.from(table.querySelectorAll('tr'));
                if (col < 1 || !rows.length) return;

                const now = new Date();
                const mins = now.getHours() * 60 + now.getMinutes();

                let targetRow = null;
                let mode = 'current';

                for (const row of rows) {
                    const r = rowRange(row);
                    if (!r) continue;
                    if (r.start <= mins && mins < r.end) {
                        targetRow = row;
                        mode = 'current';
                        break;
                    }
                }

                if (!targetRow) {
                    let nearest = null;
                    for (const row of rows) {
                        const r = rowRange(row);
                        if (!r) continue;
                        const diff = r.start - mins;
                        if (diff > 0 && diff <= 15 && (!nearest || diff < nearest.diff)) nearest = { row, diff };
                    }
                    if (nearest) {
                        targetRow = nearest.row;
                        mode = 'soon';
                    }
                }

                const headerRow = rows[0];
                if (headerRow && headerRow.children[col]) headerRow.children[col].classList.add('s88-current-col');

                if (!targetRow) return;

                const rowHead = targetRow.children[0];
                const cell = targetRow.children[col];

                if (mode === 'current') {
                    if (rowHead) rowHead.classList.add('s88-current-rowhead');
                    if (cell) cell.classList.add('s88-current-cell');
                } else {
                    if (rowHead) rowHead.classList.add('s88-soon-rowhead');
                    if (cell) cell.classList.add('s88-soon-cell');
                }

                if (rowHead && !rowHead.querySelector('.s88-period-badge')) {
                    const badge = doc.createElement('span');
                    badge.className = 's88-period-badge' + (mode === 'soon' ? ' soon' : '');
                    badge.textContent = mode === 'soon' ? '시작 전' : '진행 중';
                    rowHead.appendChild(badge);
                }
            }

            function fitTableText(doc) {
                const table = tableEl(doc);
                if (!table) return;

                const rows = Array.from(table.querySelectorAll('tr'));
                for (const row of rows) {
                    const cells = Array.from(row.children || []);
                    const firstText = cells.length ? textOf(cells[0]) : '';
                    const isHeader = firstText === '교시' || (firstText.includes('교시') && !firstText.match(/\d{1,2}:\d{2}/));
                    const isQuery = firstText.includes('조회');

                    for (let i = 1; i < cells.length; i++) {
                        const cell = cells[i];
                        if (!cell) continue;
                        const t = textOf(cell);
                        if (!t) continue;

                        if (isQuery) {
                            cell.classList.add('s88-query-fit');
                            if (t.length > 34) cell.classList.add('extreme');
                        } else if (!isHeader) {
                            if (t.length > 18) cell.classList.add('s88-text-fit', 'long');
                            if (t.length > 30) cell.classList.add('s88-text-fit', 'very-long');
                        }
                    }
                }
            }

            function runStable() {
                const doc = docRoot();
                const scroller = doc.scrollingElement || doc.documentElement || doc.body;
                const oldTop = scroller ? scroller.scrollTop : 0;
                const oldLeft = scroller ? scroller.scrollLeft : 0;

                injectStyle(doc);
                applyVars(doc);
                updateClock(doc);
                fixToolbar(doc);
                parseMemoColor(doc);
                fitTableText(doc);
                highlightCurrentPeriod(doc);

                requestAnimationFrame(function() {
                    if (scroller && Math.abs(scroller.scrollTop - oldTop) > 2) {
                        scroller.scrollTop = oldTop;
                        scroller.scrollLeft = oldLeft;
                    }
                });
            }

            function updateClockOnly() {
                const doc = docRoot();
                updateClock(doc);
            }

            runStable();
            setTimeout(runStable, 200);
            setTimeout(runStable, 900);
            setTimeout(runStable, 1800);

            // 이후에는 버튼/표 DOM은 다시 건드리지 않고 시각만 1분마다 갱신
            setInterval(updateClockOnly, 60000);
        })();
        </script>
        """,
        height=0,
        width=0,
    )
except Exception:
    pass
# [STEP88_WEB_SINGLE_STABLE_DOM_END]

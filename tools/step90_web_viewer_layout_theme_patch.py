# -*- coding: utf-8 -*-
"""
Step90 - 웹뷰어 상단바/시간표 레이아웃 및 테마 동조 패치

적용 대상:
  Y:\0_2026\시간표앱_차세대\my-timetable-next\mobile\app.py

주요 수정:
  1) 상단 달력 선택 글자 세로 배치 방지
  2) 조회 행/시간표 셀 내용이 좌우 칸을 침범하지 않도록 줄바꿈/폭 제한
  3) 선택된 테마명에 따라 시간표 색상도 함께 동조
  4) 메모장 렌더링은 건드리지 않음

주의:
  - components.html 사용 안 함
  - JavaScript / setInterval 사용 안 함
  - mobile/app.py에 CSS 주입 함수 1개와 호출부 1개만 추가
"""

from pathlib import Path
from datetime import datetime
import py_compile
import re
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step90_backups"

START = "# >>> STEP90_WEB_VIEWER_LAYOUT_THEME_CSS_START"
END = "# <<< STEP90_WEB_VIEWER_LAYOUT_THEME_CSS_END"
CALL = "_apply_step90_web_viewer_layout_theme_css()"

HELPER_BLOCK = '\n# >>> STEP90_WEB_VIEWER_LAYOUT_THEME_CSS_START\ndef _apply_step90_web_viewer_layout_theme_css():\n    """\n    웹뷰어 모바일 화면 안정화 CSS.\n    DOM 후처리/JavaScript 없이 Streamlit이 생성하는 원본 화면에 CSS만 적용한다.\n    """\n    import streamlit as st\n\n    def _find_current_theme_name():\n        candidate_keys = [\n            "theme",\n            "selected_theme",\n            "theme_name",\n            "current_theme",\n            "app_theme",\n            "ui_theme",\n            "selected_theme_name",\n            "viewer_theme",\n            "web_theme",\n        ]\n\n        for key in candidate_keys:\n            try:\n                value = st.session_state.get(key)\n            except Exception:\n                value = None\n            if value:\n                return str(value)\n\n        try:\n            for key, value in st.session_state.items():\n                key_text = str(key).lower()\n                value_text = str(value)\n                if "theme" in key_text or "테마" in key_text:\n                    if value_text and len(value_text) <= 40:\n                        return value_text\n        except Exception:\n            pass\n\n        return "default"\n\n    def _theme_palette(theme_name):\n        t = str(theme_name).lower()\n\n        palette = {\n            "topbar_bg": "#edf4ff",\n            "table_border": "#1e293b",\n            "table_head_bg": "#dbeafe",\n            "table_head_text": "#0f172a",\n            "table_subhead_bg": "#eff6ff",\n            "period_bg": "#f8fbff",\n            "cell_bg": "#fbfdff",\n            "cell_alt_bg": "#f6faff",\n            "accent": "#2563eb",\n            "lesson_text": "#ef3b2d",\n            "muted_text": "#334155",\n            "shadow": "rgba(15, 23, 42, 0.16)",\n        }\n\n        if any(x in t for x in ["dark", "다크", "어두", "블랙", "검정", "night", "navy"]):\n            palette.update({\n                "topbar_bg": "#111827",\n                "table_border": "#93a4b8",\n                "table_head_bg": "#1f2937",\n                "table_head_text": "#f8fafc",\n                "table_subhead_bg": "#172033",\n                "period_bg": "#111827",\n                "cell_bg": "#0f172a",\n                "cell_alt_bg": "#111c2f",\n                "accent": "#60a5fa",\n                "lesson_text": "#fb7185",\n                "muted_text": "#dbeafe",\n                "shadow": "rgba(0, 0, 0, 0.35)",\n            })\n        elif any(x in t for x in ["pink", "핑크", "러블리", "rose", "벚꽃"]):\n            palette.update({\n                "topbar_bg": "#fff1f6",\n                "table_border": "#be7890",\n                "table_head_bg": "#fce7f3",\n                "table_head_text": "#831843",\n                "table_subhead_bg": "#fff1f6",\n                "period_bg": "#fff7fb",\n                "cell_bg": "#fffafd",\n                "cell_alt_bg": "#fff3f8",\n                "accent": "#db2777",\n                "lesson_text": "#e11d48",\n                "muted_text": "#6b2140",\n                "shadow": "rgba(190, 24, 93, 0.15)",\n            })\n        elif any(x in t for x in ["green", "그린", "초록", "민트", "mint", "emerald"]):\n            palette.update({\n                "topbar_bg": "#ecfdf5",\n                "table_border": "#047857",\n                "table_head_bg": "#d1fae5",\n                "table_head_text": "#064e3b",\n                "table_subhead_bg": "#ecfdf5",\n                "period_bg": "#f0fdf4",\n                "cell_bg": "#fbfffd",\n                "cell_alt_bg": "#f0fdf4",\n                "accent": "#059669",\n                "lesson_text": "#dc2626",\n                "muted_text": "#065f46",\n                "shadow": "rgba(5, 150, 105, 0.15)",\n            })\n        elif any(x in t for x in ["purple", "퍼플", "보라", "violet", "lavender", "라벤더"]):\n            palette.update({\n                "topbar_bg": "#f5f3ff",\n                "table_border": "#7c3aed",\n                "table_head_bg": "#ede9fe",\n                "table_head_text": "#3b0764",\n                "table_subhead_bg": "#f5f3ff",\n                "period_bg": "#faf5ff",\n                "cell_bg": "#fdfcff",\n                "cell_alt_bg": "#f7f1ff",\n                "accent": "#7c3aed",\n                "lesson_text": "#e11d48",\n                "muted_text": "#4c1d95",\n                "shadow": "rgba(124, 58, 237, 0.15)",\n            })\n        elif any(x in t for x in ["yellow", "노랑", "옐로", "amber", "orange", "오렌지"]):\n            palette.update({\n                "topbar_bg": "#fffbeb",\n                "table_border": "#b45309",\n                "table_head_bg": "#fef3c7",\n                "table_head_text": "#78350f",\n                "table_subhead_bg": "#fffbeb",\n                "period_bg": "#fffdf2",\n                "cell_bg": "#fffefa",\n                "cell_alt_bg": "#fffbeb",\n                "accent": "#d97706",\n                "lesson_text": "#dc2626",\n                "muted_text": "#78350f",\n                "shadow": "rgba(217, 119, 6, 0.15)",\n            })\n        elif any(x in t for x in ["windows", "윈도우", "win11", "11"]):\n            palette.update({\n                "topbar_bg": "#eef6ff",\n                "table_border": "#2563eb",\n                "table_head_bg": "#dbeafe",\n                "table_head_text": "#0f2a4d",\n                "table_subhead_bg": "#eff6ff",\n                "period_bg": "#f8fbff",\n                "cell_bg": "#fbfdff",\n                "cell_alt_bg": "#f3f8ff",\n                "accent": "#2563eb",\n                "lesson_text": "#ef3b2d",\n                "muted_text": "#1e3a8a",\n                "shadow": "rgba(37, 99, 235, 0.14)",\n            })\n\n        return palette\n\n    _theme_name = _find_current_theme_name()\n    _p = _theme_palette(_theme_name)\n\n    st.markdown(\n        f"""\n<style>\n:root {{\n    --step90-topbar-bg: {_p["topbar_bg"]};\n    --step90-table-border: {_p["table_border"]};\n    --step90-table-head-bg: {_p["table_head_bg"]};\n    --step90-table-head-text: {_p["table_head_text"]};\n    --step90-table-subhead-bg: {_p["table_subhead_bg"]};\n    --step90-period-bg: {_p["period_bg"]};\n    --step90-cell-bg: {_p["cell_bg"]};\n    --step90-cell-alt-bg: {_p["cell_alt_bg"]};\n    --step90-accent: {_p["accent"]};\n    --step90-lesson-text: {_p["lesson_text"]};\n    --step90-muted-text: {_p["muted_text"]};\n    --step90-shadow: {_p["shadow"]};\n}}\n\n/* 상단 버튼/달력 영역: 세로 글자 방지 */\ndiv[data-testid="stHorizontalBlock"] {{\n    align-items: center !important;\n}}\ndiv[data-testid="stHorizontalBlock"] div[data-testid="column"] {{\n    min-width: fit-content !important;\n}}\n.stButton > button,\nbutton[kind],\ndiv[data-baseweb="select"],\ndiv[data-baseweb="select"] > div,\ndiv[data-testid="stSelectbox"],\n.stSelectbox,\n.stSelectbox * {{\n    writing-mode: horizontal-tb !important;\n    text-orientation: mixed !important;\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    overflow-wrap: normal !important;\n}}\n.stButton > button {{\n    min-width: 44px !important;\n    height: 38px !important;\n    padding-left: 10px !important;\n    padding-right: 10px !important;\n}}\n.stSelectbox {{\n    min-width: 54px !important;\n}}\n.stSelectbox div[data-baseweb="select"] {{\n    min-width: 54px !important;\n    width: 54px !important;\n}}\n.stSelectbox div[data-baseweb="select"] > div {{\n    min-width: 54px !important;\n    width: 54px !important;\n    padding-left: 7px !important;\n    padding-right: 20px !important;\n    justify-content: center !important;\n}}\n.stSelectbox div[data-baseweb="select"] span {{\n    display: inline-block !important;\n    min-width: 24px !important;\n    text-align: center !important;\n    white-space: nowrap !important;\n}}\n.stSelectbox [data-testid="stWidgetLabel"],\n.stSelectbox label {{\n    display: none !important;\n}}\n\n/* 시간표 전체: 모바일 폭 안에 안정적으로 고정 */\n[data-testid="stMarkdownContainer"] table,\n[data-testid="stTable"] table,\ntable {{\n    width: 100% !important;\n    max-width: 100% !important;\n    table-layout: fixed !important;\n    border-collapse: collapse !important;\n    border-color: var(--step90-table-border) !important;\n    box-shadow: 0 3px 14px var(--step90-shadow) !important;\n}}\n\n/* 시간표 칸 공통: 칸 밖으로 글자가 빠져나가지 않도록 강제 */\n[data-testid="stMarkdownContainer"] table th,\n[data-testid="stMarkdownContainer"] table td,\n[data-testid="stTable"] table th,\n[data-testid="stTable"] table td,\ntable th,\ntable td {{\n    max-width: 1px !important;\n    overflow: hidden !important;\n    white-space: normal !important;\n    word-break: break-word !important;\n    overflow-wrap: anywhere !important;\n    hyphens: auto !important;\n    box-sizing: border-box !important;\n    vertical-align: middle !important;\n    line-height: 1.18 !important;\n    padding: 5px 3px !important;\n    border-color: var(--step90-table-border) !important;\n    color: var(--step90-muted-text);\n}}\n[data-testid="stMarkdownContainer"] table td *,\n[data-testid="stMarkdownContainer"] table th *,\n[data-testid="stTable"] table td *,\n[data-testid="stTable"] table th *,\ntable td *,\ntable th * {{\n    max-width: 100% !important;\n    min-width: 0 !important;\n    white-space: normal !important;\n    word-break: break-word !important;\n    overflow-wrap: anywhere !important;\n    box-sizing: border-box !important;\n}}\n\n/* 시간표 색상: 테마 연동 */\n[data-testid="stMarkdownContainer"] table tr:first-child th,\n[data-testid="stMarkdownContainer"] table tr:first-child td,\n[data-testid="stTable"] table tr:first-child th,\n[data-testid="stTable"] table tr:first-child td,\ntable tr:first-child th,\ntable tr:first-child td {{\n    background: var(--step90-table-head-bg) !important;\n    color: var(--step90-table-head-text) !important;\n    font-weight: 800 !important;\n}}\n[data-testid="stMarkdownContainer"] table th,\n[data-testid="stTable"] table th,\ntable th {{\n    background: var(--step90-table-head-bg) !important;\n    color: var(--step90-table-head-text) !important;\n}}\n[data-testid="stMarkdownContainer"] table td,\n[data-testid="stTable"] table td,\ntable td {{\n    background: var(--step90-cell-bg) !important;\n}}\n[data-testid="stMarkdownContainer"] table td:first-child,\n[data-testid="stMarkdownContainer"] table th:first-child,\n[data-testid="stTable"] table td:first-child,\n[data-testid="stTable"] table th:first-child,\ntable td:first-child,\ntable th:first-child {{\n    background: var(--step90-period-bg) !important;\n    color: var(--step90-table-head-text) !important;\n    font-weight: 800 !important;\n    width: 13.5% !important;\n}}\n[data-testid="stMarkdownContainer"] table tr:nth-child(2) td,\n[data-testid="stMarkdownContainer"] table tr:nth-child(3) td,\n[data-testid="stTable"] table tr:nth-child(2) td,\n[data-testid="stTable"] table tr:nth-child(3) td,\ntable tr:nth-child(2) td,\ntable tr:nth-child(3) td {{\n    background: var(--step90-table-subhead-bg) !important;\n}}\n[data-testid="stMarkdownContainer"] table td:not(:first-child),\n[data-testid="stTable"] table td:not(:first-child),\ntable td:not(:first-child) {{\n    font-size: clamp(10px, 2.45vw, 13px) !important;\n}}\n[data-testid="stMarkdownContainer"] table td span,\n[data-testid="stMarkdownContainer"] table td div,\n[data-testid="stMarkdownContainer"] table td p,\n[data-testid="stTable"] table td span,\n[data-testid="stTable"] table td div,\n[data-testid="stTable"] table td p,\ntable td span,\ntable td div,\ntable td p {{\n    line-height: 1.18 !important;\n}}\n[data-testid="stMarkdownContainer"] table td [style*="red"],\n[data-testid="stMarkdownContainer"] table td [style*="#f00"],\n[data-testid="stMarkdownContainer"] table td [style*="#ff"],\n[data-testid="stTable"] table td [style*="red"],\n[data-testid="stTable"] table td [style*="#f00"],\n[data-testid="stTable"] table td [style*="#ff"],\ntable td [style*="red"],\ntable td [style*="#f00"],\ntable td [style*="#ff"] {{\n    color: var(--step90-lesson-text) !important;\n    font-weight: 800 !important;\n}}\n[data-testid="stMarkdownContainer"] table td strong,\n[data-testid="stTable"] table td strong,\ntable td strong {{\n    color: var(--step90-lesson-text) !important;\n    font-weight: 800 !important;\n}}\n\n/* 조회 행처럼 긴 과목명이 있는 칸은 더 촘촘하게 */\n[data-testid="stMarkdownContainer"] table tr:nth-child(3) td:not(:first-child),\n[data-testid="stTable"] table tr:nth-child(3) td:not(:first-child),\ntable tr:nth-child(3) td:not(:first-child) {{\n    font-size: clamp(8.5px, 2.05vw, 11px) !important;\n    line-height: 1.10 !important;\n    padding-left: 2px !important;\n    padding-right: 2px !important;\n}}\n[data-testid="stMarkdownContainer"] table tr:nth-child(3) td:not(:first-child) *,\n[data-testid="stTable"] table tr:nth-child(3) td:not(:first-child) *,\ntable tr:nth-child(3) td:not(:first-child) * {{\n    font-size: inherit !important;\n    line-height: inherit !important;\n}}\n[data-testid="stMarkdownContainer"],\n[data-testid="stTable"],\n.block-container {{\n    max-width: 100% !important;\n}}\n\n@media (max-width: 520px) {{\n    .block-container {{\n        padding-left: 0.25rem !important;\n        padding-right: 0.25rem !important;\n    }}\n    [data-testid="stMarkdownContainer"] table th,\n    [data-testid="stMarkdownContainer"] table td,\n    [data-testid="stTable"] table th,\n    [data-testid="stTable"] table td,\n    table th,\n    table td {{\n        padding: 4px 2px !important;\n        font-size: clamp(9px, 2.35vw, 12px) !important;\n    }}\n    [data-testid="stMarkdownContainer"] table tr:nth-child(3) td:not(:first-child),\n    [data-testid="stTable"] table tr:nth-child(3) td:not(:first-child),\n    table tr:nth-child(3) td:not(:first-child) {{\n        font-size: clamp(8px, 1.95vw, 10.5px) !important;\n    }}\n    .stButton > button {{\n        min-width: 38px !important;\n        padding-left: 8px !important;\n        padding-right: 8px !important;\n    }}\n    .stSelectbox,\n    .stSelectbox div[data-baseweb="select"],\n    .stSelectbox div[data-baseweb="select"] > div {{\n        min-width: 54px !important;\n        width: 54px !important;\n    }}\n}}\n</style>\n        """,\n        unsafe_allow_html=True,\n    )\n# <<< STEP90_WEB_VIEWER_LAYOUT_THEME_CSS_END\n'

def log(message: str) -> None:
    print(message, flush=True)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp949", errors="ignore")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def remove_old_step90(text: str) -> str:
    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END) + r"\n?",
        flags=re.DOTALL,
    )
    text = pattern.sub("", text)

    lines = []
    for line in text.splitlines():
        if CALL in line and not line.lstrip().startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines) + "\n"


def find_import_insert_index(lines):
    last_import = -1
    for i, line in enumerate(lines[:200]):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import = i
    return last_import + 1 if last_import >= 0 else 0


def insert_helper(text: str) -> str:
    lines = text.splitlines()
    idx = find_import_insert_index(lines)
    new_lines = lines[:idx] + [HELPER_BLOCK.strip("\n")] + lines[idx:]
    return "\n".join(new_lines) + "\n"


def find_page_config_end(text: str):
    pos = text.find("st.set_page_config(")
    if pos < 0:
        return None

    depth = 0
    in_string = None
    escape = False
    started = False

    for i in range(pos, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_string:
                in_string = None
            continue

        if ch in ("'", '"'):
            in_string = ch
            continue

        if ch == "(":
            depth += 1
            started = True
        elif ch == ")":
            depth -= 1
            if started and depth == 0:
                nl = text.find("\n", i)
                return len(text) if nl < 0 else nl + 1

    return None


def insert_call(text: str) -> str:
    call_text = f"\ntry:\n    {CALL}\nexcept Exception:\n    pass\n\n"
    end_pos = find_page_config_end(text)

    if end_pos is not None:
        return text[:end_pos] + call_text + text[end_pos:]

    marker_pos = text.find(END)
    if marker_pos >= 0:
        nl = text.find("\n", marker_pos)
        if nl >= 0:
            return text[: nl + 1] + call_text + text[nl + 1 :]

    return call_text + text


def compile_check(path: Path):
    py_compile.compile(str(path), doraise=True)


def main() -> int:
    log("============================================================")
    log("Step90 웹뷰어 상단바/시간표 레이아웃 및 테마 동조 패치")
    log(f"프로젝트 루트: {ROOT}")
    log(f"대상 파일: {APP}")
    log("============================================================")

    if not APP.exists():
        log("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        log("현재 명령 프롬프트 위치가 프로젝트 루트인지 확인하세요.")
        log(r"예: cd /d Y:\0_2026\시간표앱_차세대\my-timetable-next")
        return 1

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step90_{stamp}.py"

    original = read_text(APP)
    backup.write_text(original, encoding="utf-8", newline="\n")
    log(f"[백업 완료] {backup}")

    patched = remove_old_step90(original)
    patched = insert_helper(patched)
    patched = insert_call(patched)

    temp = APP.with_name("app_step90_check_tmp.py")
    try:
        write_text(temp, patched)
        compile_check(temp)
    except Exception as e:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass
        log("[오류] 패치 후 문법 검사를 통과하지 못했습니다.")
        log(str(e))
        log("[안전 조치] 원본 app.py는 변경하지 않았습니다.")
        return 1
    finally:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass

    write_text(APP, patched)
    log("[패치 완료] mobile/app.py에 Step90 CSS 보정을 적용했습니다.")
    log("")
    log("다음 명령으로 실행하세요:")
    log(r"python -m streamlit run mobile\app.py")
    log("")
    log("확인 항목:")
    log("1. 상단 달력 글자가 '달력'으로 좌우 배치되는지")
    log("2. 조회 행 과목명이 좌우 칸을 침범하지 않는지")
    log("3. 테마 변경 시 시간표 헤더/배경/강조색이 함께 어울리게 바뀌는지")
    log("4. 메모장이 기존처럼 정상인지")
    log("============================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

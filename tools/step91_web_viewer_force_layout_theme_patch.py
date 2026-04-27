# -*- coding: utf-8 -*-
"""
Step91 웹뷰어 강제 레이아웃/테마 패치
- 긴 코드를 채팅창에 붙여넣지 않기 위한 단일 패치 파일입니다.
- JS/components.html/setInterval 사용 없음. mobile/app.py에 CSS 보정 함수만 추가합니다.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime
import py_compile
import re

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
BACKUP_DIR = ROOT / "tools" / "_step91_backups"
START = "# === STEP91_WEB_VIEWER_FORCE_LAYOUT_THEME_START ==="
END = "# === STEP91_WEB_VIEWER_FORCE_LAYOUT_THEME_END ==="

PATCH_BLOCK = r'''
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
'''


def log(msg: str) -> None:
    print(msg, flush=True)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp949", errors="ignore")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def remove_old_blocks(text: str) -> str:
    patterns = [
        re.escape(START) + r".*?" + re.escape(END) + r"\n?",
        r"# === STEP90[^\n]*START ===.*?# === STEP90[^\n]*END ===\n?",
        r"# === STEP91[^\n]*START ===.*?# === STEP91[^\n]*END ===\n?",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=re.DOTALL)
    return text


def normalize_calendar_label(text: str) -> str:
    for old in ["달<br>력", "달<br/>력", "달<br />력", "달&nbsp;력", "달\\n력", "달\\r\\n력"]:
        text = text.replace(old, "달력")
    text = re.sub(r"([\"'])달\s*\\n\s*력([\"'])", r"\1달력\2", text)
    text = re.sub(r"([\"'])달\s*\\r\\n\s*력([\"'])", r"\1달력\2", text)
    return text


def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)


def main() -> int:
    log("============================================================")
    log("Step91 웹뷰어 강제 레이아웃/테마 패치 시작")
    log(f"프로젝트 루트: {ROOT}")
    log(f"대상 파일: {APP}")
    log("============================================================")

    if not APP.exists():
        log("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    original = read_text(APP)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = BACKUP_DIR / f"app_before_step91_{stamp}.py"
    write_text(backup, original)
    log(f"[백업 완료] {backup}")

    text = remove_old_blocks(original)
    text = normalize_calendar_label(text)

    # 파일 맨 아래에 CSS를 배치하여 이전 Step90 보정보다 나중에 적용되게 한다.
    patched = text.rstrip() + "\n\n" + PATCH_BLOCK.strip() + "\n"
    write_text(APP, patched)

    ok, err = compile_ok(APP)
    if not ok:
        log("[오류] 패치 후 app.py 문법 검사 실패. 백업본으로 되돌립니다.")
        log(err)
        write_text(APP, original)
        return 1

    log("[완료] Step91 패치 적용 및 문법 검사 성공")
    log("다음 명령: python -m streamlit run mobile\\app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

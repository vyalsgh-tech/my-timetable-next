# tools/step26_restore_mobile_from_step17_clean.py
# ------------------------------------------------------------
# mobile/app.py를 컴파일 가능한 step17 백업으로 되돌린 뒤
# 최소 수정만 다시 적용합니다.
#
# 실행:
#   python tools\step26_restore_mobile_from_step17_clean.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys
import re

ROOT = Path(__file__).resolve().parent.parent
MOBILE_DIR = ROOT / "mobile"
APP = MOBILE_DIR / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

WEB_FIX = """
# =========================================================
# 웹 표시 보정: 버튼 CSS + STRIKE 취소선
# =========================================================
components.html(
    \"\"\"
<script>
(function() {
    const doc = window.parent.document;
    const STYLE_ID = "mdgo-toolbar-strike-fix-style";
    if (!doc.getElementById(STYLE_ID)) {
        const style = doc.createElement("style");
        style.id = STYLE_ID;
        style.textContent = "div[data-testid=\\\"stButton\\\"] > button { white-space: nowrap !important; word-break: keep-all !important; min-width: 56px !important; padding-left: 0.45rem !important; padding-right: 0.45rem !important; }";
        doc.head.appendChild(style);
    }

    function fixStrikeMarkers() {
        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);
        const nodes = [];
        let node;
        while (node = walker.nextNode()) {
            const value = node.nodeValue || "";
            if (value.indexOf("__STRIKE__") >= 0) nodes.push(node);
        }
        nodes.forEach(node => {
            const value = node.nodeValue || "";
            const cleaned = value
                .replace(/_{1,3}STRIKE_{1,3}\\s*\\|\\|\\|?/gi, "")
                .replace(/_{1,3}STRIKE_{1,3}/gi, "");
            const span = doc.createElement("span");
            span.textContent = cleaned;
            span.style.textDecoration = "line-through";
            span.style.textDecorationThickness = "2px";
            span.style.textDecorationColor = "#1f2937";
            span.style.opacity = "0.72";
            node.parentNode.replaceChild(span, node);
        });
    }

    fixStrikeMarkers();
    setTimeout(fixStrikeMarkers, 200);
    setTimeout(fixStrikeMarkers, 800);
    setInterval(fixStrikeMarkers, 1500);
})();
</script>
\"\"\",
    height=0,
    width=0,
)
"""

CLEAN_VIEW = '''def clean_view_text(value):
    text = "" if value is None else str(value)
    text = text.replace("\\\\n", "\\n").replace("\\\\r\\\\n", "\\n")
    return text.strip()

'''


def backup_current():
    if APP.exists():
        b = MOBILE_DIR / f"app_before_step26_restore_{STAMP}.py"
        b.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        print(f"[현재 app.py 백업] {b}")


def can_compile(text, label):
    try:
        compile(text, label, "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"{e.msg} / line {e.lineno}"


def replace_clean_view(text):
    if "def clean_view_text(value):" in text:
        start = text.find("def clean_view_text(value):")
        candidates = []
        for marker in ["\ndef ", "\n# ========================================================="]:
            pos = text.find(marker, start + 5)
            if pos != -1:
                candidates.append(pos)
        if candidates:
            return text[:start] + CLEAN_VIEW + text[min(candidates):]

    marker = "\ndef safe_int(value, default=0):"
    if marker in text:
        return text.replace(marker, "\n" + CLEAN_VIEW + marker, 1)

    return CLEAN_VIEW + "\n" + text


def fix_empty_append_linewise(text):
    lines = text.splitlines()
    out = []
    i = 0
    fixed = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.endswith(".append(") or stripped.endswith("append("):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip() == ")":
                call_prefix = line[:line.rfind("(")]
                out.append(call_prefix + '("")')
                i = j + 1
                fixed += 1
                continue

        out.append(re.sub(r"(\b\w+\.append)\(\s*\)", r'\1("")', line))
        i += 1

    if fixed:
        print(f"[수정] 빈 append 블록 {fixed}개 보정")

    return "\n".join(out) + "\n"


def ensure_components_import(text):
    if "import streamlit.components.v1 as components" in text:
        return text
    if "import streamlit as st" in text:
        return text.replace(
            "import streamlit as st",
            "import streamlit as st\nimport streamlit.components.v1 as components",
            1,
        )
    return "import streamlit.components.v1 as components\n" + text


def insert_web_fix_after_page_config(text):
    if "mdgo-toolbar-strike-fix-style" in text:
        return text

    lines = text.splitlines()
    insert_at = None

    for i, line in enumerate(lines):
        if "st.set_page_config" in line:
            depth = 0
            started = False
            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == "(":
                        depth += 1
                        started = True
                    elif ch == ")":
                        depth -= 1
                if started and depth <= 0:
                    insert_at = j + 1
                    break
            break

    if insert_at is None:
        pos = 0
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("import ") or s.startswith("from "):
                pos = i + 1
        insert_at = pos

    return "\n".join(lines[:insert_at]) + "\n\n" + WEB_FIX + "\n" + "\n".join(lines[insert_at:]) + "\n"


def apply_minimal_updates(text):
    text = replace_clean_view(text)
    text = fix_empty_append_linewise(text)
    text = ensure_components_import(text)

    replacements = {
        '"📅"': '"달력"', "'📅'": "'달력'",
        '"🗓️"': '"달력"', "'🗓️'": "'달력'",
        '"📝"': '"메모"', "'📝'": "'메모'",
        '"📄"': '"메모"', "'📄'": "'메모'",
        '"🔍"': '"조회"', "'🔍'": "'조회'",
        '"🔎"': '"조회"', "'🔎'": "'조회'",
        '"8-9"': '"8·9"', "'8-9'": "'8·9'",
        '"89"': '"8·9"', "'89'": "'8·9'",
        '"🔢"': '"8·9"', "'🔢'": "'8·9'",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("이번주", "오늘")
    text = insert_web_fix_after_page_config(text)
    text = fix_empty_append_linewise(text)

    return text


def candidate_files():
    files = []
    files.extend(sorted(MOBILE_DIR.glob("app_before_step17*.py"), reverse=True))
    files.extend(sorted(MOBILE_DIR.glob("app_before_step16*.py"), reverse=True))
    files.extend(sorted(MOBILE_DIR.glob("app_before_step15*.py"), reverse=True))
    files.extend(sorted(MOBILE_DIR.glob("app_before_step*.py"), reverse=True))
    files.extend(sorted(MOBILE_DIR.glob("app_before_*.py"), reverse=True))

    legacy = MOBILE_DIR / "legacy_app.py"
    if legacy.exists():
        files.append(legacy)

    seen = set()
    result = []
    for f in files:
        if f.exists() and f.name != "app.py" and f not in seen:
            seen.add(f)
            result.append(f)

    return result


def main():
    print("==============================================")
    print("Step26 mobile restore from clean step17")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    chosen = None
    chosen_text = None

    for candidate in candidate_files():
        raw = candidate.read_text(encoding="utf-8", errors="replace")
        patched = apply_minimal_updates(raw)
        ok, err = can_compile(patched, str(candidate))

        if ok:
            chosen = candidate
            chosen_text = patched
            print(f"[선택] {candidate.name}")
            break
        else:
            print(f"[건너뜀] {candidate.name} / {err}")

    if chosen is None:
        print("[실패] 컴파일 가능한 백업을 찾지 못했습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    APP.write_text(chosen_text, encoding="utf-8")

    print()
    print("[완료] mobile/app.py 복구 완료")
    print(f"- 사용한 백업: {chosen}")
    print()
    print("확인 명령:")
    print("python -m streamlit run mobile\\app.py")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

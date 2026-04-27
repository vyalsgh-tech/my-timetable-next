# tools/step24_restore_mobile_from_clean_backup.py
# ------------------------------------------------------------
# mobile/app.py가 반복 패치로 f-string/CSS 오류 상태가 되었을 때,
# 가장 최근의 컴파일 가능한 백업을 찾아 복구하고 최소 수정만 적용합니다.
# 실행: python tools\step24_restore_mobile_from_clean_backup.py
# ------------------------------------------------------------
from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
MOBILE_DIR = ROOT / "mobile"
APP = MOBILE_DIR / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

WEB_FIX = '\n# =========================================================\n# 웹 표시 보정: 버튼 CSS + STRIKE 취소선\n# =========================================================\ncomponents.html(\n    """\n<script>\n(function() {\n    const doc = window.parent.document;\n    const STYLE_ID = "mdgo-toolbar-strike-fix-style";\n    if (!doc.getElementById(STYLE_ID)) {\n        const style = doc.createElement("style");\n        style.id = STYLE_ID;\n        style.textContent = "div[data-testid=\\"stButton\\"] > button { white-space: nowrap !important; word-break: keep-all !important; min-width: 56px !important; padding-left: 0.45rem !important; padding-right: 0.45rem !important; }";\n        doc.head.appendChild(style);\n    }\n\n    function fixStrikeMarkers() {\n        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);\n        const nodes = [];\n        let node;\n\n        while (node = walker.nextNode()) {\n            const value = node.nodeValue || "";\n            if (value.indexOf("__STRIKE__") >= 0) {\n                nodes.push(node);\n            }\n        }\n\n        nodes.forEach(node => {\n            const value = node.nodeValue || "";\n            const cleaned = value\n                .replace(/_{1,3}STRIKE_{1,3}\\s*\\|\\|\\|?/gi, "")\n                .replace(/_{1,3}STRIKE_{1,3}/gi, "");\n\n            const span = doc.createElement("span");\n            span.textContent = cleaned;\n            span.style.textDecoration = "line-through";\n            span.style.textDecorationThickness = "2px";\n            span.style.textDecorationColor = "#1f2937";\n            span.style.opacity = "0.72";\n\n            node.parentNode.replaceChild(span, node);\n        });\n    }\n\n    fixStrikeMarkers();\n    setTimeout(fixStrikeMarkers, 200);\n    setTimeout(fixStrikeMarkers, 800);\n    setInterval(fixStrikeMarkers, 1500);\n})();\n</script>\n""",\n    height=0,\n    width=0,\n)\n'

CLEAN_VIEW = 'def clean_view_text(value):\n    text = "" if value is None else str(value)\n    text = text.replace("\\\\n", "\\n").replace("\\\\r\\\\n", "\\n")\n    return text.strip()\n\n'

def backup_current():
    if APP.exists():
        backup = MOBILE_DIR / f'app_before_step24_restore_{STAMP}.py'
        backup.write_text(APP.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
        print(f'[현재 app.py 백업] {backup}')
        return backup
    return None

def try_compile(text: str, label: str):
    try:
        compile(text, label, 'exec')
        return True, ''
    except SyntaxError as e:
        return False, f'{e.msg} / line {e.lineno}'

def remove_broken_web_fix_blocks(text: str) -> str:
    # 이전 패치에서 들어간 깨진 components.html 블록 제거
    while 'mdgo-toolbar-strike-fix-style' in text:
        idx = text.find('mdgo-toolbar-strike-fix-style')
        start = text.rfind('components.html(', 0, idx)
        if start == -1:
            # 해당 라인만 제거
            lines = [ln for ln in text.splitlines() if 'mdgo-toolbar-strike-fix-style' not in ln]
            text = '\n'.join(lines) + '\n'
            break
        # 다음 섹션 주석 또는 Supabase 설정 전까지 제거
        end_candidates = []
        for marker in ['\n# =========================================================', '\n# 3. Supabase 설정', '\n# 4. 공통 상수']:
            pos = text.find(marker, idx)
            if pos != -1:
                end_candidates.append(pos)
        if end_candidates:
            end = min(end_candidates)
            text = text[:start] + text[end:]
        else:
            # 너무 뒤까지 가지 않도록 다음 80줄 정도를 제거
            lines = text.splitlines()
            line_start = text[:start].count('\n')
            line_end = min(len(lines), line_start + 80)
            del lines[line_start:line_end]
            text = '\n'.join(lines) + '\n'
            break
    return text

def remove_css_artifacts(text: str) -> str:
    lines = text.splitlines()
    out = []
    skip = False
    for line in lines:
        stripped = line.strip()
        if not skip and (
            ('div[data-testid="stButton"]' in line and '{' in line)
            or ('.mdgo-strike' in line and '{' in line)
        ):
            skip = True
            continue
        if skip:
            if stripped in ('}', '}}') or stripped.endswith('}') or '</style>' in stripped:
                skip = False
            continue
        bad_tokens = [
            'white-space: nowrap !important',
            'word-break: keep-all !important',
            'min-width:',
            'padding-left:',
            'padding-right:',
            'text-decoration-line:',
            'text-decoration-thickness:',
            'text-decoration-color:',
            'opacity:',
        ]
        if any(tok in line for tok in bad_tokens):
            continue
        out.append(line)
    return '\n'.join(out) + '\n'

def replace_clean_view(text: str) -> str:
    if 'def clean_view_text(value):' in text:
        start = text.find('def clean_view_text(value):')
        candidates = []
        for marker in ['\ndef ', '\n# =========================================================']:
            pos = text.find(marker, start + 5)
            if pos != -1:
                candidates.append(pos)
        if candidates:
            return text[:start] + CLEAN_VIEW + text[min(candidates):]
    marker = '\ndef safe_int(value, default=0):'
    if marker in text:
        return text.replace(marker, '\n' + CLEAN_VIEW + marker, 1)
    return CLEAN_VIEW + '\n' + text

def ensure_components_import(text: str) -> str:
    if 'import streamlit.components.v1 as components' in text:
        return text
    if 'import streamlit as st' in text:
        return text.replace('import streamlit as st', 'import streamlit as st\nimport streamlit.components.v1 as components', 1)
    return 'import streamlit.components.v1 as components\n' + text

def find_set_page_config_end(lines):
    for i, line in enumerate(lines):
        if 'st.set_page_config' in line:
            depth = 0
            started = False
            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == '(':
                        depth += 1
                        started = True
                    elif ch == ')':
                        depth -= 1
                if started and depth <= 0:
                    return j + 1
    return None

def insert_web_fix(text: str) -> str:
    if 'mdgo-toolbar-strike-fix-style' in text:
        return text
    lines = text.splitlines()
    insert_at = find_set_page_config_end(lines)
    if insert_at is not None:
        return '\n'.join(lines[:insert_at]) + '\n\n' + WEB_FIX + '\n' + '\n'.join(lines[insert_at:]) + '\n'
    # fallback: import 뒤
    pos = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('import ') or s.startswith('from '):
            pos = i + 1
    return '\n'.join(lines[:pos]) + '\n\n' + WEB_FIX + '\n' + '\n'.join(lines[pos:]) + '\n'

def apply_safe_updates(text: str) -> str:
    text = remove_broken_web_fix_blocks(text)
    text = remove_css_artifacts(text)
    text = replace_clean_view(text)
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
    text = text.replace('이번주', '오늘')
    text = insert_web_fix(text)
    return text

def get_candidates():
    files = []
    files.extend(sorted(MOBILE_DIR.glob('app_before_step*.py'), reverse=True))
    files.extend(sorted(MOBILE_DIR.glob('app_before_*.py'), reverse=True))
    legacy = MOBILE_DIR / 'legacy_app.py'
    if legacy.exists():
        files.append(legacy)
    seen = set()
    result = []
    for f in files:
        if f.exists() and f not in seen and f.name != 'app.py':
            seen.add(f)
            result.append(f)
    return result

def main():
    print('==============================================')
    print('Step24 mobile clean restore')
    print('==============================================')
    print(f'[ROOT] {ROOT}')
    print()
    if not APP.exists():
        print(f'[오류] app.py가 없습니다: {APP}')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)
    backup_current()
    candidates = get_candidates()
    print(f'[후보 백업 수] {len(candidates)}')
    chosen = None
    chosen_text = None
    for candidate in candidates:
        raw = candidate.read_text(encoding='utf-8', errors='replace')
        patched = apply_safe_updates(raw)
        ok, err = try_compile(patched, str(candidate))
        if ok:
            chosen = candidate
            chosen_text = patched
            print(f'[선택] {candidate.name}')
            break
        else:
            print(f'[건너뜀] {candidate.name} / {err}')
    if chosen is None:
        print('[실패] 컴파일 가능한 백업을 찾지 못했습니다.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)
    APP.write_text(chosen_text, encoding='utf-8')
    print()
    print('[완료] mobile/app.py를 컴파일 가능한 백업에서 복구하고 안전 패치를 적용했습니다.')
    print(f'- 사용한 백업: {chosen}')
    print('확인 명령: python -m streamlit run mobile\\app.py')
    input('엔터를 누르면 종료합니다.')

if __name__ == '__main__':
    main()

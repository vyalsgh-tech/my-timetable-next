# tools/step23_mobile_compile_repair.py
# ------------------------------------------------------------
# Step23: mobile/app.py의 f-string CSS 잔여 오류를 강제로 정리합니다.
# 실행: python tools\step23_mobile_compile_repair.py
# ------------------------------------------------------------
from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
MOBILE_FILE = ROOT / "mobile" / "app.py"
DESKTOP_FILE = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

WEB_FIX_JS = '''
# =========================================================
# 웹 표시 보정: 버튼 CSS + STRIKE 취소선
# =========================================================
components.html(
    \"\"\"
<script>
(function() {
    const doc = window.parent.document;
    const STYLE_ID = \"mdgo-toolbar-strike-fix-style\";
    if (!doc.getElementById(STYLE_ID)) {
        const style = doc.createElement(\"style\");
        style.id = STYLE_ID;
        style.textContent = \"div[data-testid=\\\"stButton\\\"] > button { white-space: nowrap !important; word-break: keep-all !important; min-width: 56px !important; padding-left: 0.45rem !important; padding-right: 0.45rem !important; }\";
        doc.head.appendChild(style);
    }
    function fixStrikeMarkers() {
        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);
        const nodes = [];
        let node;
        while (node = walker.nextNode()) {
            const value = node.nodeValue || \"\";
            if (value.indexOf(\"__STRIKE__\") >= 0) nodes.push(node);
        }
        nodes.forEach(node => {
            const value = node.nodeValue || \"\";
            const cleaned = value.replace(/_{1,3}STRIKE_{1,3}\\s*\\|\\|\\|?/gi, \"\").replace(/_{1,3}STRIKE_{1,3}/gi, \"\");
            const span = doc.createElement(\"span\");
            span.textContent = cleaned;
            span.style.textDecoration = \"line-through\";
            span.style.textDecorationThickness = \"2px\";
            span.style.textDecorationColor = \"#1f2937\";
            span.style.opacity = \"0.72\";
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
'''

CLEAN_VIEW_FUNC = '''
def clean_view_text(value):
    text = \"\" if value is None else str(value)
    text = text.replace(\"\\\\n\", \"\\n\").replace(\"\\\\r\\\\n\", \"\\n\")
    return text.strip()
'''

def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f'{path.stem}_before_step23_{STAMP}{path.suffix}')
    b.write_text(path.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
    print(f'[백업] {b}')
    return b

def remove_known_bad_css(text: str) -> str:
    lines = text.splitlines()
    out = []
    skip = False
    skip_reason = ''
    for line in lines:
        s = line.strip()
        if not skip and (('div[data-testid="stButton"]' in line and '{' in line) or ('.mdgo-strike' in line and '{' in line)):
            skip = True
            skip_reason = 'css'
            continue
        if skip:
            if s in ('}', '}}') or '</style>' in s or s.endswith('}'):
                skip = False
                skip_reason = ''
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

def clean_fstring_leftovers_until_compile(text: str):
    changed = False
    for attempt in range(120):
        try:
            compile(text, str(MOBILE_FILE), 'exec')
            return text, True, changed
        except SyntaxError as e:
            lines = text.splitlines()
            idx = (e.lineno or 1) - 1
            if not (0 <= idx < len(lines)):
                return text, False, changed
            current = lines[idx].strip()
            window = '\n'.join(lines[max(0, idx-12):min(len(lines), idx+12)])
            msg = str(e)
            should_delete = False
            if 'f-string' in msg:
                should_delete = True
            if current in ('}', '}}', '{', '{{'):
                should_delete = True
            if any(tok in window for tok in ['stButton', 'mdgo-strike', 'min-width', 'white-space', 'padding-left', 'padding-right']):
                should_delete = True
            if should_delete:
                print(f'[정리] app.py {idx+1}행 제거: {current}')
                del lines[idx]
                text = '\n'.join(lines) + '\n'
                changed = True
                continue
            print('[중단] 자동으로 판단하기 어려운 SyntaxError입니다.')
            print(f'- 위치: app.py {e.lineno}행')
            print(f'- 내용: {current}')
            print(f'- 오류: {e}')
            return text, False, changed
    return text, False, changed

def replace_clean_view(text: str) -> str:
    if 'def clean_view_text(value):' in text:
        start = text.find('def clean_view_text(value):')
        candidates = []
        for marker in ['\ndef ', '\n# =========================================================']:
            pos = text.find(marker, start + 5)
            if pos != -1:
                candidates.append(pos)
        if candidates:
            return text[:start] + CLEAN_VIEW_FUNC + '\n' + text[min(candidates):]
    marker = '\ndef safe_int(value, default=0):'
    if marker in text:
        return text.replace(marker, '\n' + CLEAN_VIEW_FUNC + '\n' + marker, 1)
    return CLEAN_VIEW_FUNC + '\n' + text

def remove_broken_web_fix_blocks(text: str) -> str:
    # 이전 패치의 JS/CSS 블록이 깨져 있으면 통째로 제거하려고 시도합니다.
    while 'mdgo-toolbar-strike-fix-style' in text:
        idx = text.find('mdgo-toolbar-strike-fix-style')
        start_candidates = [text.rfind('components.html(', 0, idx), text.rfind('# 웹 표시 보정', 0, idx)]
        start_candidates = [x for x in start_candidates if x != -1]
        if not start_candidates:
            break
        start = min(start_candidates)
        end = text.find(')\n', idx)
        if end == -1:
            break
        end += 2
        block = text[start:end]
        if 'stButton' in block or 'STRIKE' in block:
            text = text[:start] + text[end:]
        else:
            break
    return text

def ensure_components_import(text: str) -> str:
    if 'import streamlit.components.v1 as components' in text:
        return text
    # 이미 다른 방식으로 components가 있으면 그대로 둠
    if 'components.html' in text and 'components.v1' in text:
        return text
    if 'import streamlit as st' in text:
        return text.replace('import streamlit as st', 'import streamlit as st\nimport streamlit.components.v1 as components', 1)
    return 'import streamlit.components.v1 as components\n' + text

def insert_web_fix(text: str) -> str:
    if 'mdgo-toolbar-strike-fix-style' in text:
        return text
    marker = '# =========================================================\n# 3. Supabase 설정'
    if marker in text:
        return text.replace(marker, WEB_FIX_JS + '\n\n' + marker, 1)
    marker = '# =========================================================\n# 4. 공통 상수'
    if marker in text:
        return text.replace(marker, WEB_FIX_JS + '\n\n' + marker, 1)
    return WEB_FIX_JS + '\n\n' + text

def patch_mobile():
    if not MOBILE_FILE.exists():
        print(f'[오류] 모바일 파일 없음: {MOBILE_FILE}')
        return False
    backup(MOBILE_FILE)
    original = MOBILE_FILE.read_text(encoding='utf-8', errors='replace')
    text = original
    text = remove_broken_web_fix_blocks(text)
    text = remove_known_bad_css(text)
    text, ok1, changed1 = clean_fstring_leftovers_until_compile(text)
    text = replace_clean_view(text)
    text = ensure_components_import(text)
    text = insert_web_fix(text)
    replacements = {
        '"📅"':'"달력"', "'📅'":"'달력'", '"🗓️"':'"달력"', "'🗓️'":"'달력'",
        '"📝"':'"메모"', "'📝'":"'메모'", '"📄"':'"메모"', "'📄'":"'메모'",
        '"🔍"':'"조회"', "'🔍'":"'조회'", '"🔎"':'"조회"', "'🔎'":"'조회'",
        '"8-9"':'"8·9"', "'8-9'":"'8·9'", '"89"':'"8·9"', "'89'":"'8·9'", '"🔢"':'"8·9"', "'🔢'":"'8·9'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace('이번주', '오늘')
    text, ok2, changed2 = clean_fstring_leftovers_until_compile(text)
    if not ok2:
        report = ROOT / 'reports' / f'step23_mobile_compile_error_{STAMP}.txt'
        report.parent.mkdir(exist_ok=True)
        report.write_text(text, encoding='utf-8')
        print('[경고] 아직 컴파일 오류가 남았습니다. reports 폴더에 현재 app.py 사본을 저장했습니다.')
    MOBILE_FILE.write_text(text, encoding='utf-8')
    print('[완료] mobile/app.py 강제 정리 저장')
    return text != original

def main():
    print('==============================================')
    print('Step23 mobile compile repair')
    print('==============================================')
    print(f'[ROOT] {ROOT}')
    print()
    try:
        changed = patch_mobile()
        print()
        print('[완료]')
        print('- 모바일 변경:', '있음' if changed else '없음')
        print()
        print('확인 명령:')
        print('python -m streamlit run mobile\\app.py')
        input('엔터를 누르면 종료합니다.')
    except Exception as e:
        print('[오류]')
        print(e)
        print('이 화면을 캡처해서 보내주세요.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)

if __name__ == '__main__':
    main()

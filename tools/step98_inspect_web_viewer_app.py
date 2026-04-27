from pathlib import Path
from datetime import datetime
import ast
import json
import re
import shutil
import sys

ROOT = Path.cwd()
APP = ROOT / 'mobile' / 'app.py'
OUT_DIR = ROOT / 'tools' / '_step98_inspect'
REPORT = ROOT / 'tools' / 'step98_app_structure_report.txt'

KEYWORDS = [
    '명덕외고', '시간표', '뷰어', 'viewer',
    '달력', '메모', '조회', '오늘', '8·9', '8:9', '8-9',
    'selectbox', 'button', 'columns', 'container',
    'theme', '테마', 'lovely', 'pink', 'dark', 'light',
    'table', '<table', 'thead', 'tbody', 'render', 'html',
    'components.html', 'st.components', 'setInterval', 'querySelector',
    'current', '현재', 'clock', 'time', '시각'
]

BAD_PATTERNS = [
    'components.html', 'st.components.v1.html', 'setInterval', 'querySelector',
    'MutationObserver', 'window.parent', 'scrollTo', 'const slots',
    'STEP90', 'STEP91', 'STEP92', 'STEP93', 'STEP94', 'STEP95', 'STEP96'
]


def read_text(path: Path) -> str:
    for enc in ('utf-8', 'utf-8-sig', 'cp949'):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors='ignore')


def safe_slice(lines, idx, before=10, after=18):
    start = max(0, idx - before)
    end = min(len(lines), idx + after + 1)
    return start, end, lines[start:end]


def line_hits(lines, keyword):
    out = []
    for i, line in enumerate(lines, 1):
        if keyword.lower() in line.lower():
            out.append((i, line.rstrip('\n')))
    return out


def collect_keyword_context(lines):
    contexts = []
    seen_ranges = set()
    for kw in KEYWORDS:
        hits = line_hits(lines, kw)
        for line_no, _ in hits[:12]:
            start, end, chunk = safe_slice(lines, line_no - 1)
            key = (start, end)
            if key in seen_ranges:
                continue
            seen_ranges.add(key)
            contexts.append((kw, start + 1, end, chunk))
    return contexts


def ast_summary(text):
    result = {
        'parse_ok': False,
        'error': None,
        'functions': [],
        'classes': [],
        'imports': [],
    }
    try:
        tree = ast.parse(text)
        result['parse_ok'] = True
    except Exception as e:
        result['error'] = repr(e)
        return result

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result['functions'].append({'name': node.name, 'line': node.lineno})
        elif isinstance(node, ast.ClassDef):
            result['classes'].append({'name': node.name, 'line': node.lineno})
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                if isinstance(node, ast.Import):
                    names = ', '.join(alias.name for alias in node.names)
                    result['imports'].append({'line': node.lineno, 'text': f'import {names}'})
                else:
                    mod = node.module or ''
                    names = ', '.join(alias.name for alias in node.names)
                    result['imports'].append({'line': node.lineno, 'text': f'from {mod} import {names}'})
            except Exception:
                pass
    result['functions'] = sorted(result['functions'], key=lambda x: x['line'])
    result['classes'] = sorted(result['classes'], key=lambda x: x['line'])
    result['imports'] = sorted(result['imports'], key=lambda x: x['line'])[:80]
    return result


def detect_theme_blocks(lines):
    hints = []
    patterns = [
        r'theme', r'테마', r'color', r'palette', r'primary', r'background',
        r'pink', r'lovely', r'dark', r'light', r'windows', r'win11'
    ]
    regex = re.compile('|'.join(patterns), re.I)
    for i, line in enumerate(lines, 1):
        if regex.search(line):
            hints.append((i, line.rstrip()))
    return hints[:180]


def main():
    print('============================================================')
    print('Step98 웹뷰어 app.py 구조 진단 시작')
    print(f'프로젝트 루트: {ROOT}')
    print(f'대상 파일: {APP}')
    print('============================================================')

    if not APP.exists():
        print('[오류] mobile/app.py 파일을 찾지 못했습니다.')
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    snapshot = OUT_DIR / f'current_mobile_app_snapshot_{ts}.py'
    shutil.copy2(APP, snapshot)

    text = read_text(APP)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.splitlines()

    summary = ast_summary(text)
    bad_counts = {p: text.count(p) for p in BAD_PATTERNS if text.count(p) > 0}
    contexts = collect_keyword_context(lines)
    theme_hints = detect_theme_blocks(lines)

    # Also create a compact JSON for future automated patching if needed.
    json_path = OUT_DIR / f'step98_summary_{ts}.json'
    json_path.write_text(json.dumps({
        'root': str(ROOT),
        'app': str(APP),
        'snapshot': str(snapshot),
        'line_count': len(lines),
        'char_count': len(text),
        'ast_summary': summary,
        'bad_counts': bad_counts,
        'theme_hints': theme_hints,
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    with REPORT.open('w', encoding='utf-8', newline='\n') as f:
        f.write('Step98 Web Viewer App Structure Report\n')
        f.write('=' * 70 + '\n')
        f.write(f'ROOT: {ROOT}\n')
        f.write(f'APP: {APP}\n')
        f.write(f'SNAPSHOT: {snapshot}\n')
        f.write(f'JSON: {json_path}\n')
        f.write(f'LINES: {len(lines)}\n')
        f.write(f'CHARS: {len(text)}\n\n')

        f.write('[1] Python parse status\n')
        f.write('-' * 70 + '\n')
        f.write(f"parse_ok: {summary['parse_ok']}\n")
        f.write(f"error: {summary['error']}\n\n")

        f.write('[2] Suspicious old patch markers\n')
        f.write('-' * 70 + '\n')
        if bad_counts:
            for k, v in bad_counts.items():
                f.write(f'{k}: {v}\n')
        else:
            f.write('No suspicious old patch markers found.\n')
        f.write('\n')

        f.write('[3] Functions\n')
        f.write('-' * 70 + '\n')
        for item in summary['functions']:
            f.write(f"L{item['line']}: def {item['name']}()\n")
        f.write('\n')

        f.write('[4] Theme/color related line hints\n')
        f.write('-' * 70 + '\n')
        for line_no, line in theme_hints:
            f.write(f'L{line_no}: {line}\n')
        f.write('\n')

        f.write('[5] Keyword contexts for header / toolbar / timetable / clock\n')
        f.write('-' * 70 + '\n')
        for kw, start, end, chunk in contexts[:80]:
            f.write(f'\n--- keyword={kw!r} lines {start}-{end} ---\n')
            for j, line in enumerate(chunk, start):
                # Keep the report readable.
                trimmed = line if len(line) <= 220 else line[:220] + ' ...'
                f.write(f'{j:04d}: {trimmed}\n')

    print('[진단 완료] 보고서 생성:')
    print(REPORT)
    print('[현재 app.py 스냅샷 생성:]')
    print(snapshot)
    print('[요약 JSON 생성:]')
    print(json_path)
    print('')
    print('다음 단계: tools\\step98_app_structure_report.txt 파일을 채팅에 올려주세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

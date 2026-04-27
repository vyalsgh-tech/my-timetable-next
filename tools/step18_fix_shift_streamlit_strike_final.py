# tools/step18_fix_shift_streamlit_strike_final.py
from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_FILE = ROOT / "desktop" / "timetable.pyw"
MOBILE_FILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PC_METHODS = '\n'.join([
    '    def ask_multiline_string(self, title, prompt, initialvalue=""):',
    '        result = {"value": None}',
    '        win = tk.Toplevel(self.root)',
    '        win.title(title)',
    '        win.transient(self.root)',
    '        win.grab_set()',
    '        win.resizable(True, True)',
    '        try:',
    '            win.iconbitmap(self.icon_path)',
    '        except Exception:',
    '            pass',
    '        t = self.get_active_theme()',
    '        bg = t.get("panel_bg", t.get("cell_bg", "#ffffff"))',
    '        fg = t.get("cell_fg", "#111827")',
    '        input_bg = t.get("input_bg", "#ffffff")',
    '        border = t.get("panel_border", t.get("grid", "#d0d7de"))',
    '        accent = t.get("accent", "#2563eb")',
    '        win.configure(bg=bg)',
    '        frame = tk.Frame(win, bg=bg, padx=12, pady=12)',
    '        frame.pack(fill="both", expand=True)',
    '        tk.Label(frame, text=prompt, bg=bg, fg=fg, font=("맑은 고딕", 9, "bold"), anchor="w", justify="left").pack(fill="x", pady=(0, 6))',
    '        text_box = tk.Text(frame, height=6, width=42, wrap="word", bg=input_bg, fg=fg, insertbackground=fg, relief="solid", bd=1, highlightthickness=1, highlightbackground=border, font=("맑은 고딕", 10), undo=True)',
    '        text_box.pack(fill="both", expand=True)',
    '        text_box.insert("1.0", initialvalue or "")',
    '        text_box.focus_set()',
    '        tk.Label(frame, text="Enter: 저장  /  Shift+Enter: 줄바꿈  /  Esc: 취소", bg=bg, fg=t.get("muted_fg", "#667085"), font=("맑은 고딕", 8), anchor="w").pack(fill="x", pady=(6, 8))',
    '        btn_frame = tk.Frame(frame, bg=bg)',
    '        btn_frame.pack(fill="x")',
    '        def on_ok(event=None):',
    '            result["value"] = text_box.get("1.0", "end-1c").strip()',
    '            win.destroy()',
    '            return "break"',
    '        def on_cancel(event=None):',
    '            result["value"] = None',
    '            win.destroy()',
    '            return "break"',
    '        def insert_newline(event=None):',
    '            text_box.insert("insert", chr(10))',
    '            return "break"',
    '        def on_key_press(event=None):',
    '            keysym = getattr(event, "keysym", "")',
    '            state = int(getattr(event, "state", 0) or 0)',
    '            if keysym in ("Return", "KP_Enter"):',
    '                if state & 0x0001:',
    '                    return insert_newline(event)',
    '                return on_ok(event)',
    '            return None',
    '        tk.Button(btn_frame, text="확인", command=on_ok, bg=accent, fg="white", relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right", padx=(6, 0))',
    '        tk.Button(btn_frame, text="취소", command=on_cancel, bg=t.get("hover_btn", "#eef3fb"), fg=fg, relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right")',
    '        text_box.bind("<Shift-KeyPress-Return>", insert_newline)',
    '        text_box.bind("<Shift-KeyPress-KP_Enter>", insert_newline)',
    '        text_box.bind("<KeyPress-Return>", on_key_press)',
    '        text_box.bind("<KeyPress-KP_Enter>", on_key_press)',
    '        text_box.bind("<Escape>", on_cancel)',
    '        win.bind("<Escape>", on_cancel)',
    '        try:',
    '            self.root.update_idletasks()',
    '            x = self.root.winfo_rootx() + max(40, (self.root.winfo_width() - 420) // 2)',
    '            y = self.root.winfo_rooty() + max(40, (self.root.winfo_height() - 260) // 2)',
    '            win.geometry(f"460x280+{x}+{y}")',
    '        except Exception:',
    '            win.geometry("460x280")',
    '        self.root.wait_window(win)',
    '        return result["value"]',
    '',
    '    def ask_multiline_proxy(self, title, prompt, **kwargs):',
    '        initial = kwargs.get("initialvalue", "")',
    '        return self.ask_multiline_string(title, prompt, initialvalue=initial)',
]) + '\n\n'

STRIKE_JS_BLOCK = '\n'.join([
    '# =========================================================',
    '# STRIKE marker 표시 보정',
    '# =========================================================',
    'components.html(',
    '    """',
    '<script>',
    '(function() {',
    '    function fixStrikeMarkers() {',
    '        const doc = window.parent.document;',
    '        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);',
    '        const nodes = [];',
    '        let node;',
    '        while (node = walker.nextNode()) {',
    '            const value = node.nodeValue || "";',
    '            if (value.includes("__STRIKE__")) nodes.push(node);',
    '        }',
    '        nodes.forEach(node => {',
    '            const value = node.nodeValue || "";',
    '            const cleaned = value.replace(/_{1,3}STRIKE_{1,3}\\s*\\|\\|\\|?/gi, "").replace(/_{1,3}STRIKE_{1,3}/gi, "");',
    '            const span = doc.createElement("span");',
    '            span.textContent = cleaned;',
    '            span.style.textDecoration = "line-through";',
    '            span.style.textDecorationThickness = "2px";',
    '            span.style.textDecorationColor = "#1f2937";',
    '            span.style.opacity = "0.72";',
    '            node.parentNode.replaceChild(span, node);',
    '        });',
    '    }',
    '    fixStrikeMarkers();',
    '    setTimeout(fixStrikeMarkers, 200);',
    '    setTimeout(fixStrikeMarkers, 800);',
    '    setInterval(fixStrikeMarkers, 1500);',
    '})();',
    '</script>',
    '""",',
    '    height=0,',
    '    width=0,',
    ')',
]) + '\n\n'

def backup(path: Path):
    if not path.exists():
        return
    backup_path = path.with_name(f'{path.stem}_before_step18_{STAMP}{path.suffix}')
    backup_path.write_text(path.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
    print(f'[백업] {backup_path}')

def replace_method_block(text: str, method_name: str, replacement):
    start = text.find(f'    def {method_name}(')
    if start == -1:
        return text
    candidates = []
    for marker in ['\n    def ', '\n    # ==========================================']:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)
    if not candidates:
        raise RuntimeError(f'{method_name} 메서드 끝 위치를 찾지 못했습니다.')
    end = min(candidates)
    if replacement is None:
        return text[:start] + text[end:]
    return text[:start] + replacement + text[end:]

def patch_desktop():
    if not DESKTOP_FILE.exists():
        print(f'[경고] PC 파일 없음: {DESKTOP_FILE}')
        return False
    backup(DESKTOP_FILE)
    text = DESKTOP_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace('데이터 새로고침(Supabase)', '데이터 새로고침')
    text = text.replace('최신 설치파일 확인(GitHub Releases)', '최신 설치파일 확인')
    text = replace_method_block(text, 'ask_multiline_string', None)
    text = replace_method_block(text, 'ask_multiline_proxy', None)
    marker = '    def add_memo(self, ev=None):'
    if marker in text:
        text = text.replace(marker, PC_METHODS + marker, 1)
    else:
        marker = '    def refresh_memo_list(self):'
        if marker in text:
            text = text.replace(marker, PC_METHODS + marker, 1)
        else:
            raise RuntimeError('PC 다중 입력창 메서드 삽입 위치를 찾지 못했습니다.')
    text = text.replace('simpledialog.askstring(', 'self.ask_multiline_proxy(')
    text = text.replace('self.memo_text.insert(tk.END, f"{total-i}.{clean_text}")', 'self.memo_text.insert(tk.END, clean_text)')
    text = text.replace('self.memo_text.insert(tk.END, f"{total - i}.{clean_text}")', 'self.memo_text.insert(tk.END, clean_text)')
    if text != original:
        DESKTOP_FILE.write_text(text, encoding='utf-8')
        print('[완료] PC Shift+Enter 강제 보정')
        return True
    print('[안내] PC 변경사항 없음')
    return False

def patch_mobile():
    if not MOBILE_FILE.exists():
        print(f'[경고] 모바일 파일 없음: {MOBILE_FILE}')
        return False
    backup(MOBILE_FILE)
    text = MOBILE_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    text = re.sub(r'\n\s*\.mdgo-strike\s*\{[^{}]*?\}', '', text, flags=re.S)
    text = re.sub(r'\n\s*\.mdgo-strike\s*\{\{[^{}]*?\}\}', '', text, flags=re.S)
    if 'fixStrikeMarkers' not in text:
        marker = '# =========================================================\n# 3. Supabase 설정'
        if marker in text:
            text = text.replace(marker, STRIKE_JS_BLOCK + '\n' + marker, 1)
        else:
            marker = '# =========================================================\n# 4. 공통 상수'
            text = text.replace(marker, STRIKE_JS_BLOCK + '\n' + marker, 1)
    replacements = {
        '"📅"': '"달력"', "'📅'": "'달력'", '"🗓️"': '"달력"', "'🗓️'": "'달력'",
        '"📝"': '"메모"', "'📝'": "'메모'", '"📄"': '"메모"', "'📄'": "'메모'",
        '"🔍"': '"조회"', "'🔍'": "'조회'", '"🔎"': '"조회"', "'🔎'": "'조회'",
        '"8-9"': '"8·9"', "'8-9'": "'8·9'", '"89"': '"8·9"', "'89'": "'8·9'",
        '"🔢"': '"8·9"', "'🔢'": "'8·9'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace('이번주', '오늘')
    if 'white-space: nowrap !important' not in text:
        css = '''
<style>
div[data-testid="stButton"] > button {
    white-space: nowrap !important;
    word-break: keep-all !important;
    min-width: 56px !important;
    padding-left: 0.45rem !important;
    padding-right: 0.45rem !important;
}
</style>
'''
        insert = '\nst.markdown(' + repr(css) + ', unsafe_allow_html=True)\n'
        marker = '# =========================================================\n# 7. 로그인 화면'
        if marker in text:
            text = text.replace(marker, insert + '\n' + marker, 1)
        else:
            text += insert
    if text != original:
        MOBILE_FILE.write_text(text, encoding='utf-8')
        print('[완료] 모바일 Streamlit 오류/STRIKE/버튼명 보정')
        return True
    print('[안내] 모바일 변경사항 없음')
    return False

def main():
    print('==============================================')
    print('Step18 최종 보완 패치')
    print('==============================================')
    print(f'[ROOT] {ROOT}')
    print()
    try:
        changed_desktop = patch_desktop()
        changed_mobile = patch_mobile()
        print()
        print('[완료]')
        print('- PC 변경:', '있음' if changed_desktop else '없음')
        print('- 모바일 변경:', '있음' if changed_mobile else '없음')
        print()
        print('확인:')
        print('1) python desktop\\timetable.pyw')
        print('   - 편집창에서 Shift+Enter 줄바꿈 / Enter 저장')
        print('2) python -m streamlit run mobile\\app.py')
        print('   - NameError: text 오류 없음 / STRIKE 취소선 / 버튼명 통일')
        print()
        input('엔터를 누르면 종료합니다.')
    except Exception as e:
        print()
        print('[오류]')
        print(e)
        print()
        print('이 화면을 캡처해서 보내주세요.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)

if __name__ == '__main__':
    main()

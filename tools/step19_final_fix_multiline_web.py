# tools/step19_final_fix_multiline_web.py
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
    '        text_box = tk.Text(frame, height=7, width=44, wrap="word", bg=input_bg, fg=fg, insertbackground=fg, relief="solid", bd=1, highlightthickness=1, highlightbackground=border, font=("맑은 고딕", 10), undo=True)',
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
    '        def on_return(event=None):',
    '            try:',
    '                if event is not None and (int(getattr(event, "state", 0) or 0) & 0x0001):',
    '                    return insert_newline(event)',
    '            except Exception:',
    '                pass',
    '            return on_ok(event)',
    '        tk.Button(btn_frame, text="확인", command=on_ok, bg=accent, fg="white", relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right", padx=(6, 0))',
    '        tk.Button(btn_frame, text="취소", command=on_cancel, bg=t.get("hover_btn", "#eef3fb"), fg=fg, relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right")',
    '        text_box.bind("<Shift-Return>", insert_newline)',
    '        text_box.bind("<Shift-KP_Enter>", insert_newline)',
    '        text_box.bind("<Return>", on_return)',
    '        text_box.bind("<KP_Enter>", on_return)',
    '        text_box.bind("<Escape>", on_cancel)',
    '        win.bind("<Escape>", on_cancel)',
    '        try:',
    '            self.root.update_idletasks()',
    '            x = self.root.winfo_rootx() + max(40, (self.root.winfo_width() - 420) // 2)',
    '            y = self.root.winfo_rooty() + max(40, (self.root.winfo_height() - 280) // 2)',
    '            win.geometry(f"480x310+{x}+{y}")',
    '        except Exception:',
    '            win.geometry("480x310")',
    '        self.root.wait_window(win)',
    '        return result["value"]',
    '',
    '    def ask_multiline_proxy(self, title, prompt, **kwargs):',
    '        initial = kwargs.get("initialvalue", "")',
    '        return self.ask_multiline_string(title, prompt, initialvalue=initial)',
    '',
    '    def install_multiline_askstring_override(self):',
    '        if getattr(self, "_multiline_askstring_installed", False):',
    '            return',
    '        self._multiline_askstring_installed = True',
    '        try:',
    '            self._original_simpledialog_askstring = simpledialog.askstring',
    '            def _patched_askstring(title, prompt, **kwargs):',
    '                return self.ask_multiline_string(title, prompt, initialvalue=kwargs.get("initialvalue", ""))',
    '            simpledialog.askstring = _patched_askstring',
    '        except Exception:',
    '            pass',
    '',
    '    def open_new_memo_multiline_editor(self, event=None):',
    '        try:',
    '            current = self.memo_entry.get()',
    '            if current == "메모를 입력하세요":',
    '                current = ""',
    '        except Exception:',
    '            current = ""',
    '        text = self.ask_multiline_string("메모 입력", "메모를 입력하세요. Enter=저장, Shift+Enter=줄바꿈", initialvalue=current)',
    '        if text:',
    '            self.create_memo_from_text(text)',
    '            try:',
    '                self.memo_entry.delete(0, tk.END)',
    '            except Exception:',
    '                pass',
    '        return "break"',
]) + '\n'

CLEAN_VIEW_FUNC = '\n'.join([
    'def clean_view_text(value):',
    '    """표시용 텍스트 정리. STRIKE marker는 JS가 취소선으로 변환하도록 보존합니다."""',
    '    text = "" if value is None else str(value)',
    '    text = text.replace("\\\\n", "\\n").replace("\\r\\n", "\\n")',
    '    return text.strip()',
    '',
]) + '\n'

WEB_FIX_JS = '\n'.join([
    '# =========================================================',
    '# 웹 표시 보정: STRIKE 취소선 + 버튼 텍스트 줄바꿈 방지',
    '# =========================================================',
    'components.html(',
    '    """',
    '<script>',
    '(function() {',
    '    const doc = window.parent.document;',
    '    const STYLE_ID = "mdgo-toolbar-strike-fix-style";',
    '    if (!doc.getElementById(STYLE_ID)) {',
    '        const style = doc.createElement("style");',
    '        style.id = STYLE_ID;',
    '        style.textContent = `',
    'div[data-testid="stButton"] > button {',
    '  white-space: nowrap !important;',
    '  word-break: keep-all !important;',
    '  min-width: 56px !important;',
    '  padding-left: 0.45rem !important;',
    '  padding-right: 0.45rem !important;',
    '}',
    '`;',
    '        doc.head.appendChild(style);',
    '    }',
    '    function fixStrikeMarkers() {',
    '        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);',
    '        const nodes = [];',
    '        let node;',
    '        while (node = walker.nextNode()) {',
    '            const value = node.nodeValue || "";',
    '            if (value.indexOf("__STRIKE__") >= 0) nodes.push(node);',
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
    '',
]) + '\n'

def backup(path: Path):
    if path.exists():
        b = path.with_name(f'{path.stem}_before_step19_{STAMP}{path.suffix}')
        b.write_text(path.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
        print(f'[백업] {b}')

def replace_method_block(text, method_name, replacement):
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
    for name in ['ask_multiline_string', 'ask_multiline_proxy', 'install_multiline_askstring_override', 'open_new_memo_multiline_editor']:
        text = replace_method_block(text, name, None)
    marker = '    def add_memo(self, ev=None):'
    if marker in text:
        text = text.replace(marker, PC_METHODS + '\n' + marker, 1)
    else:
        marker = '    def refresh_memo_list(self):'
        if marker in text:
            text = text.replace(marker, PC_METHODS + '\n' + marker, 1)
        else:
            raise RuntimeError('PC 다중 입력창 메서드 삽입 위치를 찾지 못했습니다.')
    if 'self.install_multiline_askstring_override()' not in text:
        text = text.replace('        self.root = root', '        self.root = root\n        self.install_multiline_askstring_override()', 1)
    text = text.replace('simpledialog.askstring(', 'self.ask_multiline_proxy(')
    # 하단 메모 입력창 Shift+Enter 바인딩을 강제로 추가
    if 'self.memo_entry.bind("<Shift-Return>", self.open_new_memo_multiline_editor)' not in text:
        text = re.sub(r'(self\.memo_entry\.bind\("<Return>",\s*self\.add_memo\)\s*)', r'\1\n        self.memo_entry.bind("<Shift-Return>", self.open_new_memo_multiline_editor)\n        self.memo_entry.bind("<Shift-KP_Enter>", self.open_new_memo_multiline_editor)\n        self.memo_entry.bind("<Shift-KeyPress-Return>", self.open_new_memo_multiline_editor)\n        self.memo_entry.bind("<Shift-KeyPress-KP_Enter>", self.open_new_memo_multiline_editor)', text, count=1)
    text = text.replace('self.memo_text.insert(tk.END, f"{total-i}.{clean_text}")', 'self.memo_text.insert(tk.END, clean_text)')
    text = text.replace('self.memo_text.insert(tk.END, f"{total - i}.{clean_text}")', 'self.memo_text.insert(tk.END, clean_text)')
    if text != original:
        DESKTOP_FILE.write_text(text, encoding='utf-8')
        print('[완료] PC 다중 입력/하단 메모 Shift+Enter 보정')
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
    # f-string 안에 잘못 삽입된 CSS 규칙 제거
    text = re.sub(r'\n\s*div\[data-testid="stButton"\]\s*>\s*button\s*\{[^{}]*?\n\s*\}', '', text, flags=re.S)
    text = re.sub(r'\n\s*\.mdgo-strike\s*\{[^{}]*?\n\s*\}', '', text, flags=re.S)
    # clean_view_text가 있으면 STRIKE marker를 보존하는 버전으로 교체
    if 'def clean_view_text(value):' in text:
        start = text.find('def clean_view_text(value):')
        candidates = []
        for marker in ['\ndef ', '\n# =========================================================']:
            pos = text.find(marker, start + 5)
            if pos != -1:
                candidates.append(pos)
        if candidates:
            end = min(candidates)
            text = text[:start] + CLEAN_VIEW_FUNC + text[end:]
    else:
        marker = '\ndef safe_int(value, default=0):'
        if marker in text:
            text = text.replace(marker, '\n' + CLEAN_VIEW_FUNC + marker, 1)
    # 기존 오류성 st.markdown CSS 추가 블록 제거
    text = re.sub(r'\nst\.markdown\(\s*[\"\']{3}\s*<style>\s*div\[data-testid="stButton"\][\s\S]*?</style>\s*[\"\']{3}\s*,\s*unsafe_allow_html=True\s*\)\s*', '\n', text)
    # JS 보정 블록 삽입
    if 'mdgo-toolbar-strike-fix-style' not in text:
        marker = '# =========================================================\n# 3. Supabase 설정'
        if marker in text:
            text = text.replace(marker, WEB_FIX_JS + '\n' + marker, 1)
        else:
            text = WEB_FIX_JS + '\n' + text
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
    if text != original:
        MOBILE_FILE.write_text(text, encoding='utf-8')
        print('[완료] 웹 오류/CSS/STRIKE 보정')
        return True
    print('[안내] 모바일 변경사항 없음')
    return False

def main():
    print('==============================================')
    print('Step19 최종 보완: PC 줄바꿈 + 웹 오류')
    print('==============================================')
    print(f'[ROOT] {ROOT}')
    print()
    try:
        d = patch_desktop()
        m = patch_mobile()
        print()
        print('[완료]')
        print('- PC 변경:', '있음' if d else '없음')
        print('- 모바일 변경:', '있음' if m else '없음')
        print()
        print('확인:')
        print('1) python desktop\\timetable.pyw')
        print('   - 시간표 칸 수정, 메모 수정, 하단 메모 입력줄 Shift+Enter 확인')
        print('2) python -m streamlit run mobile\\app.py')
        print('   - NameError 없음, 취소선 표시, 버튼 줄바꿈 없음')
        input('엔터를 누르면 종료합니다.')
    except Exception as e:
        print()
        print('[오류]')
        print(e)
        print('이 화면을 캡처해서 보내주세요.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)

if __name__ == '__main__':
    main()

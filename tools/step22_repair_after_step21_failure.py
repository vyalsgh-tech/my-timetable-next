# tools/step22_repair_after_step21_failure.py
from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_FILE = ROOT / "desktop" / "timetable.pyw"
MOBILE_FILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

DESKTOP_METHODS = '\n'.join([
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
    '        frame = tk.Frame(win, bg=bg, padx=10, pady=10)',
    '        frame.pack(fill="both", expand=True)',
    '        tk.Label(frame, text=prompt, bg=bg, fg=fg, font=("맑은 고딕", 9, "bold"), anchor="w", justify="left").pack(fill="x", pady=(0, 5))',
    '        text_box = tk.Text(frame, height=2, width=42, wrap="word", bg=input_bg, fg=fg, insertbackground=fg, relief="solid", bd=1, highlightthickness=1, highlightbackground=border, font=("맑은 고딕", 10), undo=True)',
    '        text_box.pack(fill="x", expand=False)',
    '        text_box.insert("1.0", initialvalue or "")',
    '        text_box.focus_set()',
    '        tk.Label(frame, text="Shift+Enter: 줄바꿈 / Enter: 저장 / Esc: 취소", bg=bg, fg=t.get("muted_fg", "#667085"), font=("맑은 고딕", 8), anchor="w").pack(fill="x", pady=(5, 7))',
    '        btn_frame = tk.Frame(frame, bg=bg)',
    '        btn_frame.pack(fill="x")',
    '        def resize_editor(event=None):',
    '            try:',
    '                line_count = max(1, int(text_box.index("end-1c").split(".")[0]))',
    '                h = max(2, min(6, line_count))',
    '                text_box.configure(height=h)',
    '                win.update_idletasks()',
    '                win.geometry(f"460x{145 + h * 20}")',
    '            except Exception:',
    '                pass',
    '            return None',
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
    '            resize_editor()',
    '            return "break"',
    '        def on_return(event=None):',
    '            try:',
    '                if int(getattr(event, "state", 0) or 0) & 0x0001:',
    '                    return insert_newline(event)',
    '            except Exception:',
    '                pass',
    '            return on_ok(event)',
    '        tk.Button(btn_frame, text="확인", command=on_ok, bg=accent, fg="white", relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right", padx=(6, 0))',
    '        tk.Button(btn_frame, text="취소", command=on_cancel, bg=t.get("hover_btn", "#eef3fb"), fg=fg, relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right")',
    '        tag = "MDGOTextReturnFix" + str(id(text_box))',
    '        text_box.bindtags((tag,) + tuple(text_box.bindtags()))',
    '        text_box.bind_class(tag, "<Shift-Return>", insert_newline)',
    '        text_box.bind_class(tag, "<Shift-KP_Enter>", insert_newline)',
    '        text_box.bind_class(tag, "<Return>", on_return)',
    '        text_box.bind_class(tag, "<KP_Enter>", on_return)',
    '        text_box.bind("<KeyRelease>", resize_editor, add="+")',
    '        text_box.bind("<Escape>", on_cancel)',
    '        win.bind("<Escape>", on_cancel)',
    '        try:',
    '            self.root.update_idletasks()',
    '            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 460) // 2)',
    '            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 185) // 2)',
    '            win.geometry(f"460x185+{x}+{y}")',
    '        except Exception:',
    '            win.geometry("460x185")',
    '        resize_editor()',
    '        self.root.wait_window(win)',
    '        return result["value"]',
    '',
    '    def ask_multiline_proxy(self, title, prompt, **kwargs):',
    '        return self.ask_multiline_string(title, prompt, initialvalue=kwargs.get("initialvalue", ""))',
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
    '    def install_global_shift_enter_handler(self):',
    '        if getattr(self, "_global_shift_enter_installed", False):',
    '            return',
    '        self._global_shift_enter_installed = True',
    '        try:',
    '            self.root.bind_all("<Shift-Return>", self.handle_global_shift_enter, add="+")',
    '            self.root.bind_all("<Shift-KP_Enter>", self.handle_global_shift_enter, add="+")',
    '        except Exception:',
    '            pass',
    '',
    '    def handle_global_shift_enter(self, event=None):',
    '        try:',
    '            w = self.root.focus_get()',
    '        except Exception:',
    '            w = None',
    '        try:',
    '            if isinstance(w, tk.Entry):',
    '                current = w.get()',
    '                text = self.ask_multiline_string("입력/수정", "내용을 입력하세요.", initialvalue=current)',
    '                if text is not None:',
    '                    w.delete(0, tk.END)',
    '                    w.insert(0, text)',
    '                return "break"',
    '        except Exception:',
    '            pass',
    '        return "break"',
    '',
    '    def create_memo_from_text(self, text):',
    '        if not self.can_view_private_data():',
    '            return "break"',
    '        u = getattr(self, "teacher_var", tk.StringVar()).get()',
    '        text = (text or "").strip()',
    '        if text == "메모를 입력하세요" or not text:',
    '            return "break"',
    '        now_iso = datetime.now().isoformat()',
    '        new_memo = {"text": text, "strike": False, "important": False, "created_at": now_iso}',
    '        self.memos_data.setdefault(u, []).insert(0, new_memo)',
    '        if USE_SUPABASE:',
    '            def task():',
    '                try:',
    '                    r = requests.post(f"{SUPABASE_URL}/rest/v1/memos", headers=HEADERS, json={"teacher_name": u, "memo_text": text}, verify=False)',
    '                    if r.status_code in [200, 201] and len(r.json()) > 0:',
    '                        new_memo["id"] = r.json()[0]["id"]',
    '                        self.save_memos()',
    '                except Exception:',
    '                    pass',
    '            threading.Thread(target=task, daemon=True).start()',
    '        self.push_history()',
    '        self.refresh_memo_list()',
    '        self.save_memos()',
    '        self.update_time_and_date()',
    '        return "break"',
    '',
    '    def open_new_memo_multiline_editor(self, event=None):',
    '        try:',
    '            current = self.memo_entry.get()',
    '            if current == "메모를 입력하세요":',
    '                current = ""',
    '        except Exception:',
    '            current = ""',
    '        text = self.ask_multiline_string("메모 입력", "메모를 입력하세요.", initialvalue=current)',
    '        if text:',
    '            self.create_memo_from_text(text)',
    '            try:',
    '                self.memo_entry.delete(0, tk.END)',
    '            except Exception:',
    '                pass',
    '        return "break"',
    '',
    '    def add_memo(self, ev=None):',
    '        try:',
    '            if ev is not None and (int(getattr(ev, "state", 0) or 0) & 0x0001):',
    '                return self.open_new_memo_multiline_editor(ev)',
    '        except Exception:',
    '            pass',
    '        try:',
    '            text = self.memo_entry.get().strip()',
    '        except Exception:',
    '            text = ""',
    '        result = self.create_memo_from_text(text)',
    '        try:',
    '            self.memo_entry.delete(0, tk.END)',
    '        except Exception:',
    '            pass',
    '        return result',
]) + '\n'

WEB_FIX = '\n'.join([
    '# =========================================================',
    '# 웹 표시 보정: 버튼 CSS + STRIKE 취소선',
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
    '        style.textContent = "div[data-testid=\\"stButton\\"] > button { white-space: nowrap !important; word-break: keep-all !important; min-width: 56px !important; padding-left: 0.45rem !important; padding-right: 0.45rem !important; }";',
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

CLEAN_VIEW = '\n'.join([
    'def clean_view_text(value):',
    '    text = "" if value is None else str(value)',
    '    text = text.replace("\\\\n", "\\n").replace("\\r\\n", "\\n")',
    '    return text.strip()',
    '',
]) + '\n'

def backup(path: Path):
    if path.exists():
        b = path.with_name(f'{path.stem}_before_step22_{STAMP}{path.suffix}')
        b.write_text(path.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
        print(f'[백업] {b}')

def remove_method(text, name):
    start = text.find(f'    def {name}(')
    if start == -1:
        return text
    candidates = []
    for marker in ['\n    def ', '\n    # ==========================================']:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)
    if not candidates:
        raise RuntimeError(f'{name} 메서드 끝 위치를 찾지 못했습니다.')
    return text[:start] + text[min(candidates):]

def patch_desktop():
    if not DESKTOP_FILE.exists():
        print(f'[경고] PC 파일 없음: {DESKTOP_FILE}')
        return False
    backup(DESKTOP_FILE)
    text = DESKTOP_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    for name in ['ask_multiline_string','ask_multiline_proxy','install_multiline_askstring_override','install_global_shift_enter_handler','handle_global_shift_enter','create_memo_from_text','open_new_memo_multiline_editor','add_memo']:
        text = remove_method(text, name)
    marker = '    def refresh_memo_list(self):'
    if marker not in text:
        raise RuntimeError('refresh_memo_list 위치를 찾지 못했습니다.')
    text = text.replace(marker, DESKTOP_METHODS + '\n' + marker, 1)
    if 'self.install_multiline_askstring_override()' not in text:
        text = text.replace('        self.root = root', '        self.root = root\n        self.install_multiline_askstring_override()\n        self.install_global_shift_enter_handler()', 1)
    elif 'self.install_global_shift_enter_handler()' not in text:
        text = text.replace('self.install_multiline_askstring_override()', 'self.install_multiline_askstring_override()\n        self.install_global_shift_enter_handler()', 1)
    text = text.replace('simpledialog.askstring(', 'self.ask_multiline_proxy(')
    if 'self.memo_entry.bind("<Shift-Return>", self.open_new_memo_multiline_editor)' not in text:
        text = re.sub(r'(self\.memo_entry\.bind\("<Return>",\s*self\.add_memo\)\s*)', r'\1\n        self.memo_entry.bind("<Shift-Return>", self.open_new_memo_multiline_editor)\n        self.memo_entry.bind("<Shift-KP_Enter>", self.open_new_memo_multiline_editor)', text, count=1)
    text = text.replace('데이터 새로고침(Supabase)', '데이터 새로고침')
    text = text.replace('최신 설치파일 확인(GitHub Releases)', '최신 설치파일 확인')
    if text != original:
        DESKTOP_FILE.write_text(text, encoding='utf-8')
        print('[완료] PC 입력창/전역 Shift+Enter 보정')
        return True
    print('[안내] PC 변경사항 없음')
    return False

def strip_css_artifacts(text):
    lines = text.splitlines()
    out = []
    skip = False
    for i, line in enumerate(lines):
        s = line.strip()
        if 'div[data-testid="stButton"]' in line and '{' in line:
            skip = True
            continue
        if '.mdgo-strike' in line and '{' in line:
            skip = True
            continue
        if skip:
            if s in ('}', '}}') or '</style>' in s:
                skip = False
            continue
        bad = ['white-space: nowrap !important', 'word-break: keep-all !important', 'min-width:', 'padding-left:', 'padding-right:', 'text-decoration-line:', 'text-decoration-thickness:', 'text-decoration-color:', 'opacity:']
        if any(x in line for x in bad):
            continue
        out.append(line)
    return '\n'.join(out) + '\n'

def compile_until_clean(text):
    for _ in range(80):
        try:
            compile(text, str(MOBILE_FILE), 'exec')
            return text, True
        except SyntaxError as e:
            lines = text.splitlines()
            idx = (e.lineno or 1) - 1
            if 0 <= idx < len(lines):
                current = lines[idx].strip()
                window = '\n'.join(lines[max(0, idx-8):min(len(lines), idx+8)])
                if current in ('}', '}}') or 'stButton' in window or 'mdgo-strike' in window or 'min-width' in window or 'white-space' in window:
                    print(f'[정리] mobile/app.py {idx+1}행 제거: {current}')
                    del lines[idx]
                    text = '\n'.join(lines) + '\n'
                    continue
            print('[경고] 자동 컴파일 정리 실패:', e)
            return text, False
    return text, False

def replace_or_insert_clean_view(text):
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

def patch_mobile():
    if not MOBILE_FILE.exists():
        print(f'[경고] 모바일 파일 없음: {MOBILE_FILE}')
        return False
    backup(MOBILE_FILE)
    text = MOBILE_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    text = strip_css_artifacts(text)
    text = replace_or_insert_clean_view(text)
    if 'mdgo-toolbar-strike-fix-style' not in text:
        marker = '# =========================================================\n# 3. Supabase 설정'
        if marker in text:
            text = text.replace(marker, WEB_FIX + '\n' + marker, 1)
        else:
            text = WEB_FIX + '\n' + text
    replacements = {'"📅"':'"달력"',"'📅'":"'달력'",'"🗓️"':'"달력"',"'🗓️'":"'달력'",'"📝"':'"메모"',"'📝'":"'메모'",'"📄"':'"메모"',"'📄'":"'메모'",'"🔍"':'"조회"',"'🔍'":"'조회'",'"🔎"':'"조회"',"'🔎'":"'조회'",'"8-9"':'"8·9"',"'8-9'":"'8·9'",'"89"':'"8·9"',"'89'":"'8·9'",'"🔢"':'"8·9"',"'🔢'":"'8·9'"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace('이번주', '오늘')
    text, ok = compile_until_clean(text)
    if not ok:
        print('[경고] mobile/app.py 컴파일이 아직 완전히 정리되지 않았습니다. 그래도 가능한 정리는 저장합니다.')
    if text != original:
        MOBILE_FILE.write_text(text, encoding='utf-8')
        print('[완료] 모바일 CSS/f-string 오류 정리')
        return True
    print('[안내] 모바일 변경사항 없음')
    return False

def main():
    print('==============================================')
    print('Step22 repair after Step21 failure')
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
        print('확인: python desktop\\timetable.pyw / python -m streamlit run mobile\\app.py')
        input('엔터를 누르면 종료합니다.')
    except Exception as e:
        print('[오류]')
        print(e)
        print('이 화면을 캡처해서 보내주세요.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)

if __name__ == '__main__':
    main()
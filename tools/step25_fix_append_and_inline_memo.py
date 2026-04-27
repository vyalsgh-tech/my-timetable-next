# tools/step25_fix_append_and_inline_memo.py
from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_FILE = ROOT / "desktop" / "timetable.pyw"
MOBILE_FILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

HELPER_METHODS = '\n'.join([
    '    def get_memo_entry_text_raw(self):',
    '        try:',
    '            if isinstance(self.memo_entry, tk.Text):',
    '                return self.memo_entry.get("1.0", "end-1c")',
    '            return self.memo_entry.get()',
    '        except Exception:',
    '            return ""',
    '',
    '    def get_memo_entry_text(self):',
    '        return self.get_memo_entry_text_raw().strip()',
    '',
    '    def clear_memo_entry(self):',
    '        try:',
    '            if isinstance(self.memo_entry, tk.Text):',
    '                self.memo_entry.delete("1.0", tk.END)',
    '            else:',
    '                self.memo_entry.delete(0, tk.END)',
    '        except Exception:',
    '            pass',
    '',
    '    def set_memo_entry_text(self, text):',
    '        self.clear_memo_entry()',
    '        try:',
    '            if isinstance(self.memo_entry, tk.Text):',
    '                self.memo_entry.insert("1.0", text or "")',
    '            else:',
    '                self.memo_entry.insert(0, text or "")',
    '        except Exception:',
    '            pass',
    '',
    '    def resize_memo_entry_inline(self, event=None):',
    '        try:',
    '            if not isinstance(self.memo_entry, tk.Text):',
    '                return None',
    '            raw = self.memo_entry.get("1.0", "end-1c")',
    '            line_count = max(1, raw.count(chr(10)) + 1)',
    '            height = max(1, min(5, line_count))',
    '            self.memo_entry.configure(height=height)',
    '        except Exception:',
    '            pass',
    '        return None',
    '',
    '    def memo_entry_shift_enter_inline(self, event=None):',
    '        try:',
    '            if isinstance(self.memo_entry, tk.Text):',
    '                self.memo_entry.insert("insert", chr(10))',
    '                self.resize_memo_entry_inline()',
    '                return "break"',
    '        except Exception:',
    '            pass',
    '        # Entry인 경우만 작은 보조창 fallback',
    '        return self.open_new_memo_multiline_editor(event)',
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
    '    def add_memo(self, ev=None):',
    '        try:',
    '            if ev is not None and (int(getattr(ev, "state", 0) or 0) & 0x0001):',
    '                return self.memo_entry_shift_enter_inline(ev)',
    '        except Exception:',
    '            pass',
    '        text = self.get_memo_entry_text()',
    '        result = self.create_memo_from_text(text)',
    '        self.clear_memo_entry()',
    '        self.resize_memo_entry_inline()',
    '        return result',
    '',
]) + '\n'

MULTILINE_METHODS = '\n'.join([
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
    '        text_box.bind("<Shift-Return>", insert_newline)',
    '        text_box.bind("<Shift-KP_Enter>", insert_newline)',
    '        text_box.bind("<Return>", on_return)',
    '        text_box.bind("<KP_Enter>", on_return)',
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
]) + '\n'

def backup(path: Path):
    if path.exists():
        b = path.with_name(f'{path.stem}_before_step25_{STAMP}{path.suffix}')
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
        return text
    return text[:start] + text[min(candidates):]

def replace_memo_entry_widget(text):
    lines = text.splitlines()
    out = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        if 'self.memo_entry' in line and '= ' in line and ('Entry(' in line) and 'tk.Text' not in line:
            # collect constructor block
            block = [line]
            depth = line.count('(') - line.count(')')
            i += 1
            while i < len(lines) and depth > 0:
                block.append(lines[i])
                depth += lines[i].count('(') - lines[i].count(')')
                i += 1
            block_text = '\n'.join(block)
            m = re.search(r'Entry\(([^,\)]+)', block_text)
            parent = m.group(1).strip() if m else 'self.root'
            indent = line[:len(line) - len(line.lstrip())]
            out.append(indent + f'self.memo_entry = tk.Text({parent}, height=1, wrap="word", font=("맑은 고딕", 10), relief="solid", bd=1, padx=6, pady=4)')
            changed = True
            continue
        out.append(line)
        i += 1
    return '\n'.join(out) + '\n', changed

def patch_desktop():
    if not DESKTOP_FILE.exists():
        print('[경고] desktop/timetable.pyw 없음')
        return False
    backup(DESKTOP_FILE)
    text = DESKTOP_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace('데이터 새로고침(Supabase)', '데이터 새로고침')
    text = text.replace('최신 설치파일 확인(GitHub Releases)', '최신 설치파일 확인')
    for name in ['ask_multiline_string','ask_multiline_proxy','install_multiline_askstring_override','get_memo_entry_text_raw','get_memo_entry_text','clear_memo_entry','set_memo_entry_text','resize_memo_entry_inline','memo_entry_shift_enter_inline','create_memo_from_text','open_new_memo_multiline_editor','add_memo']:
        text = remove_method(text, name)
    marker = '    def refresh_memo_list(self):'
    if marker in text:
        text = text.replace(marker, MULTILINE_METHODS + '\n' + HELPER_METHODS + '\n' + marker, 1)
    else:
        raise RuntimeError('refresh_memo_list 위치를 찾지 못했습니다.')
    if 'self.install_multiline_askstring_override()' not in text:
        text = text.replace('        self.root = root', '        self.root = root\n        self.install_multiline_askstring_override()', 1)
    text = text.replace('simpledialog.askstring(', 'self.ask_multiline_proxy(')
    text, widget_changed = replace_memo_entry_widget(text)
    # memo_entry가 Text가 되었으므로 placeholder 관련 Entry 인덱스 보정
    text = text.replace('self.memo_entry.delete(0, tk.END)', 'self.clear_memo_entry()')
    text = text.replace('self.memo_entry.insert(0,', 'self.memo_entry.insert("1.0",')
    text = text.replace('self.memo_entry.get().strip()', 'self.get_memo_entry_text()')
    text = text.replace('self.memo_entry.get()', 'self.get_memo_entry_text_raw()')
    if 'self.memo_entry.bind("<Shift-Return>", self.memo_entry_shift_enter_inline)' not in text:
        text = re.sub(r'(self\.memo_entry\.bind\("<Return>",\s*self\.add_memo\)\s*)', r'\1\n        self.memo_entry.bind("<Shift-Return>", self.memo_entry_shift_enter_inline)\n        self.memo_entry.bind("<Shift-KP_Enter>", self.memo_entry_shift_enter_inline)\n        self.memo_entry.bind("<KeyRelease>", self.resize_memo_entry_inline, add="+")', text, count=1)
    if text != original:
        DESKTOP_FILE.write_text(text, encoding='utf-8')
        print('[완료] PC 하단 메모 inline 확장 + askstring 보정')
        return True
    print('[안내] PC 변경 없음')
    return False

def patch_mobile():
    if not MOBILE_FILE.exists():
        print('[경고] mobile/app.py 없음')
        return False
    backup(MOBILE_FILE)
    text = MOBILE_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    # html_parts.append()처럼 인자 없이 호출되는 부분을 안전한 빈 문자열 append로 보정
    text = re.sub(r'(\b\w+\.append\()\s*\)', r'\1""\)', text, flags=re.S)
    text = re.sub(r'(\bhtml_parts\.append\()\s*\)', r'\1""\)', text, flags=re.S)
    try:
        compile(text, str(MOBILE_FILE), 'exec')
    except SyntaxError as e:
        print(f'[경고] app.py 문법 오류가 아직 있습니다: {e}')
    if text != original:
        MOBILE_FILE.write_text(text, encoding='utf-8')
        print('[완료] 모바일 empty append 오류 보정')
        return True
    print('[안내] 모바일 변경 없음')
    return False

def main():
    print('==============================================')
    print('Step25 append error + inline memo input')
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
        print('   - 하단 메모 입력줄: Shift+Enter 시 창이 뜨지 않고 줄이 늘어나는지')
        print('   - 시간표 칸: 기존 입력창에서 Shift+Enter가 가능한지')
        print('2) python -m streamlit run mobile\\app.py')
        print('   - list.append() TypeError가 사라졌는지')
        input('엔터를 누르면 종료합니다.')
    except Exception as e:
        print('[오류]')
        print(e)
        print('이 화면을 캡처해서 보내주세요.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)

if __name__ == '__main__':
    main()
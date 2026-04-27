# tools/step15_small_ui_updates.py
# ------------------------------------------------------------
# 소소한 업데이트 자동 패치
# 실행: python tools\step15_small_ui_updates.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_FILE = ROOT / "desktop" / "timetable.pyw"
MOBILE_FILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def multiline_methods_text():
    return '\n'.join([
        '    def ask_multiline_string(self, title, prompt, initialvalue=""):',
        '        result = {"value": None}',
        '',
        '        win = tk.Toplevel(self.root)',
        '        win.title(title)',
        '        win.transient(self.root)',
        '        win.grab_set()',
        '        win.resizable(True, True)',
        '',
        '        try:',
        '            win.iconbitmap(self.icon_path)',
        '        except Exception:',
        '            pass',
        '',
        '        t = self.get_active_theme()',
        '        bg = t.get("panel_bg", t.get("cell_bg", "#ffffff"))',
        '        fg = t.get("cell_fg", "#111827")',
        '        input_bg = t.get("input_bg", "#ffffff")',
        '        border = t.get("panel_border", t.get("grid", "#d0d7de"))',
        '        accent = t.get("accent", "#2563eb")',
        '        win.configure(bg=bg)',
        '',
        '        frame = tk.Frame(win, bg=bg, padx=12, pady=12)',
        '        frame.pack(fill="both", expand=True)',
        '',
        '        tk.Label(frame, text=prompt, bg=bg, fg=fg, font=("맑은 고딕", 9, "bold"), anchor="w", justify="left").pack(fill="x", pady=(0, 6))',
        '',
        '        text_box = tk.Text(frame, height=6, width=42, wrap="word", bg=input_bg, fg=fg, insertbackground=fg, relief="solid", bd=1, highlightthickness=1, highlightbackground=border, font=("맑은 고딕", 10), undo=True)',
        '        text_box.pack(fill="both", expand=True)',
        '        text_box.insert("1.0", initialvalue or "")',
        '        text_box.focus_set()',
        '',
        '        tk.Label(frame, text="Enter: 저장  /  Shift+Enter: 줄바꿈  /  Esc: 취소", bg=bg, fg=t.get("muted_fg", "#667085"), font=("맑은 고딕", 8), anchor="w").pack(fill="x", pady=(6, 8))',
        '',
        '        btn_frame = tk.Frame(frame, bg=bg)',
        '        btn_frame.pack(fill="x")',
        '',
        '        def on_ok(event=None):',
        '            result["value"] = text_box.get("1.0", "end-1c").strip()',
        '            win.destroy()',
        '            return "break"',
        '',
        '        def on_cancel(event=None):',
        '            result["value"] = None',
        '            win.destroy()',
        '            return "break"',
        '',
        '        def on_shift_enter(event=None):',
        '            text_box.insert("insert", chr(10))',
        '            return "break"',
        '',
        '        tk.Button(btn_frame, text="확인", command=on_ok, bg=accent, fg="white", relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right", padx=(6, 0))',
        '        tk.Button(btn_frame, text="취소", command=on_cancel, bg=t.get("hover_btn", "#eef3fb"), fg=fg, relief="flat", padx=14, pady=4, cursor="hand2").pack(side="right")',
        '',
        '        text_box.bind("<Return>", on_ok)',
        '        text_box.bind("<Shift-Return>", on_shift_enter)',
        '        text_box.bind("<Escape>", on_cancel)',
        '        win.bind("<Escape>", on_cancel)',
        '',
        '        try:',
        '            self.root.update_idletasks()',
        '            x = self.root.winfo_rootx() + max(40, (self.root.winfo_width() - 420) // 2)',
        '            y = self.root.winfo_rooty() + max(40, (self.root.winfo_height() - 260) // 2)',
        '            win.geometry(f"460x280+{x}+{y}")',
        '        except Exception:',
        '            win.geometry("460x280")',
        '',
        '        self.root.wait_window(win)',
        '        return result["value"]',
        '',
        '    def create_memo_from_text(self, text):',
        '        if not self.can_view_private_data():',
        '            return "break"',
        '',
        "        u = getattr(self, 'teacher_var', tk.StringVar()).get()",
        '        text = (text or "").strip()',
        '        if text == "메모를 입력하세요" or not text:',
        '            return "break"',
        '',
        '        now_iso = datetime.now().isoformat()',
        "        new_memo = {'text': text, 'strike': False, 'important': False, 'created_at': now_iso}",
        '        self.memos_data.setdefault(u, []).insert(0, new_memo)',
        '',
        '        if USE_SUPABASE:',
        '            def task():',
        '                try:',
        '                    r = requests.post(f"{SUPABASE_URL}/rest/v1/memos", headers=HEADERS, json={"teacher_name": u, "memo_text": text}, verify=False)',
        '                    if r.status_code in [200, 201] and len(r.json()) > 0:',
        "                        new_memo['id'] = r.json()[0]['id']",
        '                        self.save_memos()',
        '                except Exception:',
        '                    pass',
        '            threading.Thread(target=task, daemon=True).start()',
        '',
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
        '',
        '        text = self.ask_multiline_string("메모 입력", "메모를 입력하세요. Enter=저장, Shift+Enter=줄바꿈", initialvalue=current)',
        '        if text:',
        '            self.create_memo_from_text(text)',
        '            try:',
        '                self.memo_entry.delete(0, tk.END)',
        '            except Exception:',
        '                pass',
        '        return "break"',
        '',
    ]) + '\n\n'

NEW_ADD_MEMO = '\n'.join([
    '    def add_memo(self, ev=None):',
    '        if not self.can_view_private_data():',
    '            return "break"',
    '',
    '        try:',
    '            text = self.memo_entry.get().strip()',
    '        except Exception:',
    '            text = ""',
    '',
    '        result = self.create_memo_from_text(text)',
    '',
    '        try:',
    '            self.memo_entry.delete(0, tk.END)',
    '        except Exception:',
    '            pass',
    '',
    '        return result',
    '',
]) + '\n'

def backup(path: Path):
    if path.exists():
        backup_path = path.with_name(f"{path.stem}_before_step15_{STAMP}{path.suffix}")
        backup_path.write_text(path.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
        print(f'[백업] {backup_path}')

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
    text = text.replace('self.memo_text.insert(tk.END, f"{total-i}.{clean_text}")', 'self.memo_text.insert(tk.END, clean_text)')
    text = text.replace('self.memo_text.insert(tk.END, f"{total - i}.{clean_text}")', 'self.memo_text.insert(tk.END, clean_text)')
    text = re.sub(r'self\.memo_text\.insert\(tk\.END,\s*f"\{total\s*-\s*i\}\.\{clean_text\}"\)', 'self.memo_text.insert(tk.END, clean_text)', text)
    if 'def ask_multiline_string(self' not in text:
        marker = '    def add_memo(self, ev=None):'
        if marker in text:
            text = text.replace(marker, multiline_methods_text() + marker, 1)
        else:
            raise RuntimeError('add_memo 메서드 위치를 찾지 못했습니다.')
    pattern = r'    def add_memo\(self, ev=None\):\n.*?(?=    def refresh_memo_list\(self\):)'
    text, count = re.subn(pattern, NEW_ADD_MEMO, text, flags=re.S)
    if count != 1:
        raise RuntimeError('add_memo 메서드 교체에 실패했습니다.')
    text = re.sub(r'simpledialog\.askstring\(\s*"입력/수정",\s*"내용을 입력하세요 \(수정 시 덮어씁니다\):",\s*parent=self\.root,\s*initialvalue=([^)]+?)\s*\)', r'self.ask_multiline_string("입력/수정", "내용을 입력하세요. Enter=저장, Shift+Enter=줄바꿈", initialvalue=\1)', text, flags=re.S)
    if 'open_new_memo_multiline_editor' in text and 'self.memo_entry.bind("<Shift-Return>", self.open_new_memo_multiline_editor)' not in text:
        text = re.sub(r'(self\.memo_entry\.bind\("<Return>",\s*self\.add_memo\)\s*)', r'\1\n        self.memo_entry.bind("<Shift-Return>", self.open_new_memo_multiline_editor)', text, count=1)
    text = text.replace("clean_text, fg_color, bg_color = self.parse_text_styles(m['text'])", "clean_text, fg_color, bg_color = self.parse_text_styles(str(m.get('text', '')).replace('\\\\n', chr(10)))")
    if text != original:
        DESKTOP_FILE.write_text(text, encoding='utf-8')
        print('[완료] PC desktop/timetable.pyw 패치')
        return True
    print('[안내] PC 파일 변경사항 없음')
    return False

def patch_mobile():
    if not MOBILE_FILE.exists():
        print(f'[경고] 모바일 파일 없음: {MOBILE_FILE}')
        return False
    backup(MOBILE_FILE)
    text = MOBILE_FILE.read_text(encoding='utf-8', errors='replace')
    original = text
    text = text.replace('이번주', '오늘')
    if text != original:
        MOBILE_FILE.write_text(text, encoding='utf-8')
        print('[완료] 모바일 mobile/app.py 패치')
        return True
    print('[안내] 모바일 파일 변경사항 없음')
    return False

def main():
    print('==============================================')
    print('Step15 소소한 UI/입력 업데이트 패치')
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
        print('다음 확인:')
        print('1) python desktop\\timetable.pyw')
        print('   - 창 제목: 명덕외고 시간표')
        print('   - 메모 넘버링 없음')
        print('   - 설정 메뉴명 간소화')
        print('   - 메모/시간표 수정창에서 Shift+Enter 줄바꿈')
        print()
        print('2) python -m streamlit run mobile\\app.py')
        print('   - 모바일 문구가 오늘로 통일')
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

# tools/step29_runtime_repair_pc_web.py
# ------------------------------------------------------------
# Step29 런타임 보정 패치
#
# PC:
# - 하단 메모 입력칸 오른쪽에 검색/A+/A- 버튼을 런타임으로 재구성
# - 하단 메모 입력칸 Shift+Enter: 팝업 없이 입력칸 자체 줄바꿈
# - 입력 줄 수에 따라 입력칸 높이 자동 확장
# - 시간표 칸/별도 Entry 편집창 Shift+Enter: 작은 다중 입력창으로 연결
#
# 웹:
# - st.button/st.markdown을 Python 레벨에서 보정
# - 달력/조회/8·9 버튼 텍스트와 CSS 보정
# - __STRIKE__ 완료표시 취소선 변환
# - 메모 넘버링 제거
#
# 실행:
#   python tools\step29_runtime_repair_pc_web.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
MOBILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PC_RUNTIME_PATCH = '\n# =========================================================\n# Step29 PC 하단 메모/시간표 줄바꿈 런타임 보정\n# =========================================================\ndef _mdgo_apply_pc_runtime_patch():\n    import types\n    import gc\n    import tkinter as tk\n    from tkinter import messagebox\n\n    class _MdgoInlineMemoText(tk.Text):\n        def __init__(self, master=None, **kwargs):\n            for key in ("textvariable", "show", "validate", "validatecommand", "invalidcommand", "justify"):\n                kwargs.pop(key, None)\n            kwargs.setdefault("height", 1)\n            kwargs.setdefault("wrap", "word")\n            kwargs.setdefault("undo", True)\n            super().__init__(master, **kwargs)\n\n        def get(self, *args):\n            if not args:\n                return super().get("1.0", "end-1c")\n            return super().get(*args)\n\n        def delete(self, *args):\n            if len(args) >= 1 and args[0] == 0:\n                return super().delete("1.0", tk.END)\n            return super().delete(*args)\n\n        def insert(self, index, chars, *args):\n            if index == 0:\n                index = "1.0"\n            return super().insert(index, chars, *args)\n\n    def _ask_multiline(self, title, prompt, initialvalue=""):\n        result = {"value": None}\n\n        win = tk.Toplevel(self.root)\n        win.title(title)\n        win.transient(self.root)\n        win.grab_set()\n        win.resizable(True, True)\n\n        try:\n            win.iconbitmap(self.icon_path)\n        except Exception:\n            pass\n\n        try:\n            t = self.get_active_theme()\n        except Exception:\n            t = {}\n\n        bg = t.get("panel_bg", t.get("cell_bg", "#ffffff"))\n        fg = t.get("cell_fg", "#111827")\n        input_bg = t.get("input_bg", "#ffffff")\n        border = t.get("panel_border", t.get("grid", "#d0d7de"))\n        accent = t.get("accent", "#2563eb")\n\n        win.configure(bg=bg)\n        frame = tk.Frame(win, bg=bg, padx=10, pady=10)\n        frame.pack(fill="both", expand=True)\n\n        tk.Label(\n            frame,\n            text=prompt,\n            bg=bg,\n            fg=fg,\n            font=("맑은 고딕", 9, "bold"),\n            anchor="w",\n            justify="left",\n        ).pack(fill="x", pady=(0, 5))\n\n        text_box = tk.Text(\n            frame,\n            height=2,\n            width=44,\n            wrap="word",\n            bg=input_bg,\n            fg=fg,\n            insertbackground=fg,\n            relief="solid",\n            bd=1,\n            highlightthickness=1,\n            highlightbackground=border,\n            font=("맑은 고딕", 10),\n            undo=True,\n        )\n        text_box.pack(fill="x", expand=False)\n        text_box.insert("1.0", initialvalue or "")\n        text_box.focus_set()\n\n        tk.Label(\n            frame,\n            text="Shift+Enter: 줄바꿈 / Enter: 저장 / Esc: 취소",\n            bg=bg,\n            fg=t.get("muted_fg", "#667085"),\n            font=("맑은 고딕", 8),\n            anchor="w",\n        ).pack(fill="x", pady=(5, 7))\n\n        btn_frame = tk.Frame(frame, bg=bg)\n        btn_frame.pack(fill="x")\n\n        def resize_editor(event=None):\n            try:\n                line_count = max(1, int(text_box.index("end-1c").split(".")[0]))\n                height = max(2, min(7, line_count))\n                text_box.configure(height=height)\n                win.update_idletasks()\n                win.geometry(f"470x{145 + height * 20}")\n            except Exception:\n                pass\n            return None\n\n        def on_ok(event=None):\n            result["value"] = text_box.get("1.0", "end-1c").strip()\n            win.destroy()\n            return "break"\n\n        def on_cancel(event=None):\n            result["value"] = None\n            win.destroy()\n            return "break"\n\n        def insert_newline(event=None):\n            text_box.insert("insert", chr(10))\n            resize_editor()\n            return "break"\n\n        def on_return(event=None):\n            try:\n                if int(getattr(event, "state", 0) or 0) & 0x0001:\n                    return insert_newline(event)\n            except Exception:\n                pass\n            return on_ok(event)\n\n        tk.Button(\n            btn_frame,\n            text="확인",\n            command=on_ok,\n            bg=accent,\n            fg="white",\n            relief="flat",\n            padx=14,\n            pady=4,\n            cursor="hand2",\n        ).pack(side="right", padx=(6, 0))\n\n        tk.Button(\n            btn_frame,\n            text="취소",\n            command=on_cancel,\n            bg=t.get("hover_btn", "#eef3fb"),\n            fg=fg,\n            relief="flat",\n            padx=14,\n            pady=4,\n            cursor="hand2",\n        ).pack(side="right")\n\n        text_box.bind("<Shift-Return>", insert_newline)\n        text_box.bind("<Shift-KP_Enter>", insert_newline)\n        text_box.bind("<Return>", on_return)\n        text_box.bind("<KP_Enter>", on_return)\n        text_box.bind("<KeyRelease>", resize_editor, add="+")\n        text_box.bind("<Escape>", on_cancel)\n        win.bind("<Escape>", on_cancel)\n\n        try:\n            self.root.update_idletasks()\n            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 470) // 2)\n            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 185) // 2)\n            win.geometry(f"470x185+{x}+{y}")\n        except Exception:\n            win.geometry("470x185")\n\n        resize_editor()\n        self.root.wait_window(win)\n        return result["value"]\n\n    def _memo_text_get(widget):\n        if isinstance(widget, tk.Text):\n            return widget.get("1.0", "end-1c")\n        return widget.get()\n\n    def _memo_text_delete(widget):\n        if isinstance(widget, tk.Text):\n            widget.delete("1.0", tk.END)\n        else:\n            widget.delete(0, tk.END)\n\n    def _memo_resize(self, event=None):\n        try:\n            w = self.memo_entry\n            if isinstance(w, tk.Text):\n                raw = w.get("1.0", "end-1c")\n                line_count = max(1, raw.count(chr(10)) + 1)\n                height = max(1, min(5, line_count))\n                w.configure(height=height)\n        except Exception:\n            pass\n        return None\n\n    def _memo_shift_enter(self, event=None):\n        try:\n            w = self.memo_entry\n            if isinstance(w, tk.Text):\n                w.insert("insert", chr(10))\n                _memo_resize(self)\n                return "break"\n        except Exception:\n            pass\n        return "break"\n\n    def _memo_search(self):\n        try:\n            query = _memo_text_get(self.memo_entry).strip()\n            if not query or query == "메모를 입력하세요":\n                messagebox.showinfo("검색", "검색할 내용을 메모 입력칸에 입력하세요.")\n                return\n            box = getattr(self, "memo_text", None)\n            if not isinstance(box, tk.Text):\n                return\n            box.tag_remove("mdgo_search_hit", "1.0", tk.END)\n            start = "1.0"\n            hit = box.search(query, start, tk.END, nocase=True)\n            if hit:\n                end = f"{hit}+{len(query)}c"\n                box.tag_add("mdgo_search_hit", hit, end)\n                box.tag_config("mdgo_search_hit", background="#fff2a8", foreground="#111827")\n                box.see(hit)\n            else:\n                messagebox.showinfo("검색", "검색 결과가 없습니다.")\n        except Exception as e:\n            messagebox.showwarning("검색 오류", str(e))\n\n    def _adjust_memo_font(self, delta):\n        try:\n            current = int(getattr(self, "_mdgo_memo_font_size", 10))\n        except Exception:\n            current = 10\n        new_size = max(7, min(18, current + delta))\n        self._mdgo_memo_font_size = new_size\n\n        for attr in ("memo_text", "memo_entry"):\n            try:\n                w = getattr(self, attr, None)\n                if w is not None:\n                    w.configure(font=("맑은 고딕", new_size))\n            except Exception:\n                pass\n\n    def _entry_shift_enter(self, event=None):\n        try:\n            widget = event.widget if event is not None else self.root.focus_get()\n        except Exception:\n            widget = None\n\n        try:\n            if widget is self.memo_entry:\n                return _memo_shift_enter(self, event)\n        except Exception:\n            pass\n\n        try:\n            if isinstance(widget, tk.Entry):\n                current = widget.get()\n                text = _ask_multiline(self, "입력/수정", "내용을 입력하세요.", initialvalue=current)\n                if text is not None:\n                    widget.delete(0, tk.END)\n                    widget.insert(0, text)\n                return "break"\n        except Exception:\n            pass\n\n        return None\n\n    def _bind_entries_recursive(self, widget=None):\n        try:\n            if widget is None:\n                widget = self.root\n\n            if isinstance(widget, tk.Entry) and not getattr(widget, "_mdgo_shift_bound", False):\n                widget._mdgo_shift_bound = True\n                widget.bind("<Shift-Return>", lambda e, s=self: _entry_shift_enter(s, e), add="+")\n                widget.bind("<Shift-KP_Enter>", lambda e, s=self: _entry_shift_enter(s, e), add="+")\n\n            for child in widget.winfo_children():\n                _bind_entries_recursive(self, child)\n        except Exception:\n            pass\n\n        try:\n            if widget is self.root:\n                self.root.after(500, lambda s=self: _bind_entries_recursive(s))\n        except Exception:\n            pass\n\n    def _rebuild_memo_bar(self):\n        if getattr(self, "_mdgo_memo_bar_fixed", False):\n            return\n        self._mdgo_memo_bar_fixed = True\n\n        old = getattr(self, "memo_entry", None)\n        if old is None:\n            return\n\n        parent = old.master\n\n        try:\n            bg = parent.cget("bg")\n        except Exception:\n            bg = "#ffffff"\n\n        try:\n            fg = old.cget("fg")\n        except Exception:\n            fg = "#111827"\n\n        try:\n            old_font = old.cget("font")\n        except Exception:\n            old_font = ("맑은 고딕", 10)\n\n        try:\n            old_text = _memo_text_get(old)\n        except Exception:\n            old_text = ""\n\n        manager = old.winfo_manager()\n        pack_info = {}\n        grid_info = {}\n\n        try:\n            if manager == "pack":\n                pack_info = old.pack_info()\n                pack_info.pop("in", None)\n            elif manager == "grid":\n                grid_info = old.grid_info()\n                grid_info.pop("in", None)\n        except Exception:\n            pass\n\n        try:\n            old.pack_forget()\n        except Exception:\n            pass\n        try:\n            old.grid_forget()\n        except Exception:\n            pass\n        try:\n            old.place_forget()\n        except Exception:\n            pass\n\n        row = tk.Frame(parent, bg=bg)\n        self._mdgo_memo_row = row\n\n        if manager == "grid" and grid_info:\n            row.grid(**grid_info)\n            try:\n                parent.grid_columnconfigure(int(grid_info.get("column", 0)), weight=1)\n            except Exception:\n                pass\n        else:\n            if not pack_info:\n                pack_info = {"fill": "x", "padx": 4, "pady": 4}\n            row.pack(**pack_info)\n\n        new_entry = _MdgoInlineMemoText(\n            row,\n            height=1,\n            wrap="word",\n            font=old_font,\n            relief="solid",\n            bd=1,\n            padx=6,\n            pady=4,\n        )\n        try:\n            new_entry.configure(bg=old.cget("bg"), fg=fg, insertbackground=fg)\n        except Exception:\n            pass\n\n        new_entry.insert("1.0", old_text or "")\n        new_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))\n\n        self.memo_entry = new_entry\n\n        def make_btn(text, cmd, width=5):\n            return tk.Button(\n                row,\n                text=text,\n                command=cmd,\n                width=width,\n                relief="flat",\n                bd=0,\n                bg="#2563eb" if text == "검색" else "#f3f6fb",\n                fg="white" if text == "검색" else "#111827",\n                activebackground="#1d4ed8" if text == "검색" else "#e5eaf3",\n                cursor="hand2",\n                font=("맑은 고딕", 9, "bold"),\n            )\n\n        make_btn("검색", lambda s=self: _memo_search(s), width=5).pack(side="left", padx=(0, 4), ipady=3)\n        make_btn("A+", lambda s=self: _adjust_memo_font(s, 1), width=4).pack(side="left", padx=(0, 2), ipady=3)\n        make_btn("A-", lambda s=self: _adjust_memo_font(s, -1), width=4).pack(side="left", padx=(0, 0), ipady=3)\n\n        new_entry.bind("<Return>", lambda e, s=self: s.add_memo(e), add="+")\n        new_entry.bind("<Shift-Return>", lambda e, s=self: _memo_shift_enter(s, e), add="+")\n        new_entry.bind("<Shift-KP_Enter>", lambda e, s=self: _memo_shift_enter(s, e), add="+")\n        new_entry.bind("<KeyRelease>", lambda e, s=self: _memo_resize(s, e), add="+")\n\n    def _patch_instance(self):\n        try:\n            self.ask_multiline_string = types.MethodType(_ask_multiline, self)\n            self.ask_multiline_proxy = types.MethodType(lambda s, title, prompt, **kw: _ask_multiline(s, title, prompt, kw.get("initialvalue", "")), self)\n        except Exception:\n            pass\n\n        try:\n            _rebuild_memo_bar(self)\n        except Exception:\n            pass\n\n        try:\n            self.root.bind_class("Entry", "<Shift-Return>", lambda e, s=self: _entry_shift_enter(s, e), add="+")\n            self.root.bind_class("Entry", "<Shift-KP_Enter>", lambda e, s=self: _entry_shift_enter(s, e), add="+")\n            self.root.bind_all("<Shift-Return>", lambda e, s=self: _entry_shift_enter(s, e), add="+")\n            self.root.bind_all("<Shift-KP_Enter>", lambda e, s=self: _entry_shift_enter(s, e), add="+")\n            self.root.after(500, lambda s=self: _bind_entries_recursive(s))\n        except Exception:\n            pass\n\n    # simpledialog 자체도 우회\n    try:\n        import tkinter.simpledialog as simpledialog\n        _orig_askstring = simpledialog.askstring\n\n        def _patched_askstring(title, prompt, **kwargs):\n            for obj in gc.get_objects():\n                try:\n                    if obj.__class__.__name__ == "TimetableWidget" and hasattr(obj, "root"):\n                        return _ask_multiline(obj, title, prompt, kwargs.get("initialvalue", ""))\n                except Exception:\n                    pass\n            return _orig_askstring(title, prompt, **kwargs)\n\n        simpledialog.askstring = _patched_askstring\n    except Exception:\n        pass\n\n    # 기존 인스턴스 찾아 패치\n    for obj in gc.get_objects():\n        try:\n            if obj.__class__.__name__ == "TimetableWidget" and hasattr(obj, "root"):\n                _patch_instance(obj)\n        except Exception:\n            pass\n\ntry:\n    _mdgo_apply_pc_runtime_patch()\nexcept Exception:\n    pass\n# =========================================================\n'
MOBILE_PATCH = '\n# =========================================================\n# Step29 웹뷰어 UI/취소선/메모번호 Python-level 보정\n# =========================================================\nimport re as _mdgo_re\nimport html as _mdgo_html\n\ntry:\n    _mdgo_orig_button = st.button\n    _mdgo_orig_markdown = st.markdown\n\n    def _mdgo_button_label(label):\n        text = str(label)\n        compact = _mdgo_re.sub(r"\\s+", "", text)\n        if "☀" in text or "🔍" in text or "🔎" in text or compact == "조회":\n            return "조회"\n        if "🌙" in text or "🔢" in text or compact in ("89", "8-9", "8·9"):\n            return "8·9"\n        if "📅" in text or "🗓" in text or compact == "달력":\n            return "달력"\n        if "📝" in text or compact == "메모":\n            return "메모"\n        return label\n\n    def _mdgo_transform_render_text(body):\n        if not isinstance(body, str):\n            return body\n\n        text = body\n\n        # 완료표시 marker를 취소선 span으로 변환\n        def _strike_repl(match):\n            content = (match.group(1) or "").strip()\n            return \'<span class="mdgo-web-strike">\' + _mdgo_html.escape(content) + \'</span>\'\n\n        text = _mdgo_re.sub(\n            r"_{1,3}STRIKE_{1,3}\\s*\\|\\|\\|?\\s*([^<\\n\\r]+)",\n            _strike_repl,\n            text,\n            flags=_mdgo_re.IGNORECASE,\n        )\n\n        # 웹 메모장 넘버링 제거: 줄 시작, 태그 직후, strong/b 태그 안쪽 모두 처리\n        text = _mdgo_re.sub(r"(?m)^(\\s*)\\d{1,2}\\.\\s+", r"\\1", text)\n        text = _mdgo_re.sub(r"(>\\s*)\\d{1,2}\\.\\s+", r"\\1", text)\n        text = _mdgo_re.sub(r"(<(?:b|strong)[^>]*>\\s*)\\d{1,2}\\.\\s+", r"\\1", text)\n\n        return text\n\n    def _mdgo_button(label, *args, **kwargs):\n        return _mdgo_orig_button(_mdgo_button_label(label), *args, **kwargs)\n\n    def _mdgo_markdown(body, *args, **kwargs):\n        new_body = _mdgo_transform_render_text(body)\n        if isinstance(new_body, str) and new_body != body:\n            kwargs["unsafe_allow_html"] = True\n        return _mdgo_orig_markdown(new_body, *args, **kwargs)\n\n    st.button = _mdgo_button\n    st.markdown = _mdgo_markdown\n\n    st.markdown(\n        """\n<style>\ndiv[data-testid="stButton"] > button {\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    writing-mode: horizontal-tb !important;\n    min-width: 58px !important;\n    overflow: visible !important;\n    padding-left: 0.45rem !important;\n    padding-right: 0.45rem !important;\n}\ndiv[data-baseweb="select"] {\n    min-width: 64px !important;\n}\ndiv[data-baseweb="select"] * {\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    writing-mode: horizontal-tb !important;\n}\n.mdgo-web-strike {\n    text-decoration: line-through !important;\n    text-decoration-thickness: 2px !important;\n    text-decoration-color: #1f2937 !important;\n    opacity: 0.72 !important;\n}\n</style>\n""",\n        unsafe_allow_html=True,\n    )\nexcept Exception:\n    pass\n# =========================================================\n'


def backup(path: Path, label: str):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step29_{label}_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def try_compile(text, label):
    try:
        compile(text, label, "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"{e.msg} / line {e.lineno}"


def remove_old_block(text: str, start_marker: str, end_marker: str = "# =========================================================") -> str:
    while start_marker in text:
        start = text.find(start_marker)
        # start_marker 앞의 섹션 구분선까지 당김
        section_start = text.rfind("# =========================================================", 0, start)
        if section_start != -1:
            start = section_start
        end = text.find(end_marker, start + len(start_marker))
        if end == -1:
            text = text[:start].rstrip() + "\n"
            break
        text = text[:start] + text[end:]
    return text


def insert_pc_patch_before_mainloop(text: str) -> str:
    text = remove_old_block(text, "Step29 PC 하단 메모/시간표 줄바꿈 런타임 보정")
    text = remove_old_block(text, "_mdgo_apply_pc_runtime_patch")

    # mainloop 직전 삽입. 앱 인스턴스 생성 후 적용되어 현재 화면 구조를 직접 보정함.
    m = re.search(r"(?m)^.*\.mainloop\s*\(\s*\)", text)
    if m:
        insert_at = m.start()
        return text[:insert_at] + PC_RUNTIME_PATCH + "\n" + text[insert_at:]

    # mainloop를 못 찾으면 파일 끝에 추가
    return text.rstrip() + "\n\n" + PC_RUNTIME_PATCH + "\n"


def patch_desktop():
    if not DESKTOP.exists():
        print(f"[경고] PC 파일 없음: {DESKTOP}")
        return False

    backup(DESKTOP, "desktop")
    text = DESKTOP.read_text(encoding="utf-8", errors="replace")
    original = text

    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")

    text = insert_pc_patch_before_mainloop(text)

    ok, err = try_compile(text, str(DESKTOP))
    if not ok:
        print(f"[경고] PC 파일 문법 확인 실패: {err}")
    else:
        print("[확인] PC 파일 문법 OK")

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] PC 런타임 보정 패치 저장")
        return True

    print("[안내] PC 변경 없음")
    return False


def insert_mobile_patch_after_page_config(text: str) -> str:
    text = remove_old_block(text, "Step29 웹뷰어 UI/취소선/메모번호 Python-level 보정")
    text = remove_old_block(text, "_mdgo_transform_render_text")

    # 버튼 literal도 직접 치환
    replacements = {
        '"📅"': '"달력"', "'📅'": "'달력'",
        '"🗓️"': '"달력"', "'🗓️'": "'달력'",
        '"📝"': '"메모"', "'📝'": "'메모'",
        '"📄"': '"메모"', "'📄'": "'메모'",
        '"🔍"': '"조회"', "'🔍'": "'조회'",
        '"🔎"': '"조회"', "'🔎'": "'조회'",
        '"☀️"': '"조회"', "'☀️'": "'조회'",
        '"☀"': '"조회"', "'☀'": "'조회'",
        '"🌙"': '"8·9"', "'🌙'": "'8·9'",
        '"8-9"': '"8·9"', "'8-9'": "'8·9'",
        '"89"': '"8·9"', "'89'": "'8·9'",
        '"🔢"': '"8·9"', "'🔢'": "'8·9'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("이번주", "오늘")

    # set_page_config 뒤에 삽입
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

    if insert_at is not None:
        return "\n".join(lines[:insert_at]) + "\n\n" + MOBILE_PATCH + "\n" + "\n".join(lines[insert_at:]) + "\n"

    # fallback: import 뒤
    pos = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            pos = i + 1
    return "\n".join(lines[:pos]) + "\n\n" + MOBILE_PATCH + "\n" + "\n".join(lines[pos:]) + "\n"


def patch_mobile():
    if not MOBILE.exists():
        print(f"[경고] 모바일 파일 없음: {MOBILE}")
        return False

    backup(MOBILE, "mobile")
    text = MOBILE.read_text(encoding="utf-8", errors="replace")
    original = text

    # empty append 안전 보정
    text = re.sub(r"(\b\w+\.append)\(\s*\)", r'\1("")', text)
    text = insert_mobile_patch_after_page_config(text)

    ok, err = try_compile(text, str(MOBILE))
    if not ok:
        print(f"[경고] mobile/app.py 문법 확인 실패: {err}")
    else:
        print("[확인] mobile/app.py 문법 OK")

    if text != original:
        MOBILE.write_text(text, encoding="utf-8")
        print("[완료] 웹뷰어 Python-level 보정 패치 저장")
        return True

    print("[안내] 모바일 변경 없음")
    return False


def main():
    print("==============================================")
    print("Step29 runtime repair: PC + web")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    try:
        pc = patch_desktop()
        mobile = patch_mobile()

        print()
        print("[완료]")
        print("- PC 변경:", "있음" if pc else "없음")
        print("- 모바일 변경:", "있음" if mobile else "없음")
        print()
        print("확인:")
        print("1) python desktop\\timetable.pyw")
        print("   - 하단 메모 입력칸 오른쪽 검색/A+/A- 버튼")
        print("   - 하단 메모 입력칸 Shift+Enter: 팝업 없이 줄바꿈")
        print("   - 시간표 칸/수업일정 입력창 Shift+Enter: 다중 입력")
        print()
        print("2) python -m streamlit run mobile\\app.py")
        print("   - 달력/조회/8·9 버튼")
        print("   - 완료표시 취소선")
        print("   - 메모 넘버링 제거")
        print()
        input("엔터를 누르면 종료합니다.")

    except Exception as e:
        print("[오류]")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()

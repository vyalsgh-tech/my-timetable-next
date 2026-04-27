# tools/step28_web_pc_final_repair.py
# ------------------------------------------------------------
# Step28 최종 보정
#
# 1) 웹뷰어 mobile/app.py
#    - 달력 버튼 세로 깨짐 보정
#    - 조회/8·9 텍스트 고정
#    - 완료표시 __STRIKE__를 취소선으로 표시
#    - 웹 메모장 넘버링 제거
#
# 2) PC desktop/timetable.pyw
#    - 가능한 경우 검색/A+/A- 버튼이 남아 있는 desktop 백업으로 복원 후 패치
#    - 하단 메모 입력칸: 팝업 없이 Shift+Enter 줄바꿈, 입력칸 자동 확장
#    - 시간표 칸/일반 Entry 입력: Shift+Enter 시 다중 입력창으로 보정
#
# 실행:
#   python tools\step28_web_pc_final_repair.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys
import shutil

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
MOBILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

INLINE_MEMO_TEXT = '\nclass InlineMemoText(tk.Text):\n    """Entry처럼 get/delete/insert를 쓸 수 있는 하단 메모용 다중 입력칸."""\n    def __init__(self, master=None, **kwargs):\n        # Entry 전용 옵션 제거\n        for key in (\n            "textvariable", "show", "validate", "validatecommand",\n            "invalidcommand", "justify"\n        ):\n            kwargs.pop(key, None)\n\n        kwargs.setdefault("height", 1)\n        kwargs.setdefault("wrap", "word")\n        kwargs.setdefault("undo", True)\n\n        super().__init__(master, **kwargs)\n\n    def get(self, *args):\n        if not args:\n            return super().get("1.0", "end-1c")\n        return super().get(*args)\n\n    def delete(self, *args):\n        if len(args) >= 1 and args[0] == 0:\n            return super().delete("1.0", tk.END)\n        return super().delete(*args)\n\n    def insert(self, index, chars, *args):\n        if index == 0:\n            index = "1.0"\n        return super().insert(index, chars, *args)\n\n'
PC_METHODS = '\n    def ask_multiline_string(self, title, prompt, initialvalue=""):\n        """작은 다중 입력창. Enter=저장, Shift+Enter=줄바꿈."""\n        result = {"value": None}\n\n        win = tk.Toplevel(self.root)\n        win.title(title)\n        win.transient(self.root)\n        win.grab_set()\n        win.resizable(True, True)\n\n        try:\n            win.iconbitmap(self.icon_path)\n        except Exception:\n            pass\n\n        try:\n            t = self.get_active_theme()\n        except Exception:\n            t = {}\n\n        bg = t.get("panel_bg", t.get("cell_bg", "#ffffff"))\n        fg = t.get("cell_fg", "#111827")\n        input_bg = t.get("input_bg", "#ffffff")\n        border = t.get("panel_border", t.get("grid", "#d0d7de"))\n        accent = t.get("accent", "#2563eb")\n\n        win.configure(bg=bg)\n\n        frame = tk.Frame(win, bg=bg, padx=10, pady=10)\n        frame.pack(fill="both", expand=True)\n\n        tk.Label(\n            frame,\n            text=prompt,\n            bg=bg,\n            fg=fg,\n            font=("맑은 고딕", 9, "bold"),\n            anchor="w",\n            justify="left",\n        ).pack(fill="x", pady=(0, 5))\n\n        text_box = tk.Text(\n            frame,\n            height=2,\n            width=44,\n            wrap="word",\n            bg=input_bg,\n            fg=fg,\n            insertbackground=fg,\n            relief="solid",\n            bd=1,\n            highlightthickness=1,\n            highlightbackground=border,\n            font=("맑은 고딕", 10),\n            undo=True,\n        )\n        text_box.pack(fill="x", expand=False)\n        text_box.insert("1.0", initialvalue or "")\n        text_box.focus_set()\n\n        tk.Label(\n            frame,\n            text="Shift+Enter: 줄바꿈 / Enter: 저장 / Esc: 취소",\n            bg=bg,\n            fg=t.get("muted_fg", "#667085"),\n            font=("맑은 고딕", 8),\n            anchor="w",\n        ).pack(fill="x", pady=(5, 7))\n\n        btn_frame = tk.Frame(frame, bg=bg)\n        btn_frame.pack(fill="x")\n\n        def resize_editor(event=None):\n            try:\n                line_count = max(1, int(text_box.index("end-1c").split(".")[0]))\n                height = max(2, min(7, line_count))\n                text_box.configure(height=height)\n                win.update_idletasks()\n                win.geometry(f"470x{145 + height * 20}")\n            except Exception:\n                pass\n            return None\n\n        def on_ok(event=None):\n            result["value"] = text_box.get("1.0", "end-1c").strip()\n            win.destroy()\n            return "break"\n\n        def on_cancel(event=None):\n            result["value"] = None\n            win.destroy()\n            return "break"\n\n        def insert_newline(event=None):\n            text_box.insert("insert", chr(10))\n            resize_editor()\n            return "break"\n\n        def on_return(event=None):\n            try:\n                if int(getattr(event, "state", 0) or 0) & 0x0001:\n                    return insert_newline(event)\n            except Exception:\n                pass\n            return on_ok(event)\n\n        tk.Button(\n            btn_frame,\n            text="확인",\n            command=on_ok,\n            bg=accent,\n            fg="white",\n            relief="flat",\n            padx=14,\n            pady=4,\n            cursor="hand2",\n        ).pack(side="right", padx=(6, 0))\n\n        tk.Button(\n            btn_frame,\n            text="취소",\n            command=on_cancel,\n            bg=t.get("hover_btn", "#eef3fb"),\n            fg=fg,\n            relief="flat",\n            padx=14,\n            pady=4,\n            cursor="hand2",\n        ).pack(side="right")\n\n        text_box.bind("<Shift-Return>", insert_newline)\n        text_box.bind("<Shift-KP_Enter>", insert_newline)\n        text_box.bind("<Return>", on_return)\n        text_box.bind("<KP_Enter>", on_return)\n        text_box.bind("<KeyRelease>", resize_editor, add="+")\n        text_box.bind("<Escape>", on_cancel)\n        win.bind("<Escape>", on_cancel)\n\n        try:\n            self.root.update_idletasks()\n            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 470) // 2)\n            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 185) // 2)\n            win.geometry(f"470x185+{x}+{y}")\n        except Exception:\n            win.geometry("470x185")\n\n        resize_editor()\n        self.root.wait_window(win)\n        return result["value"]\n\n    def ask_multiline_proxy(self, title, prompt, **kwargs):\n        return self.ask_multiline_string(title, prompt, initialvalue=kwargs.get("initialvalue", ""))\n\n    def memo_entry_shift_newline(self, event=None):\n        """하단 메모 입력칸: 팝업 없이 입력칸 자체에서 줄바꿈."""\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("insert", chr(10))\n                self.resize_memo_entry_inline()\n                return "break"\n        except Exception:\n            pass\n        return "break"\n\n    def resize_memo_entry_inline(self, event=None):\n        """하단 메모 입력칸을 입력 줄 수에 맞춰 자연스럽게 확장."""\n        try:\n            if not isinstance(self.memo_entry, tk.Text):\n                return None\n            raw = self.memo_entry.get("1.0", "end-1c")\n            line_count = max(1, raw.count(chr(10)) + 1)\n            height = max(1, min(5, line_count))\n            self.memo_entry.configure(height=height)\n        except Exception:\n            pass\n        return None\n\n    def entry_shift_enter_to_multiline(self, event=None):\n        """시간표 셀 등 일반 Entry에서 Shift+Enter를 다중 입력으로 보정."""\n        try:\n            widget = event.widget if event is not None else self.root.focus_get()\n        except Exception:\n            widget = None\n\n        try:\n            if widget is self.memo_entry:\n                return self.memo_entry_shift_newline(event)\n        except Exception:\n            pass\n\n        try:\n            if isinstance(widget, tk.Entry):\n                current = widget.get()\n                text = self.ask_multiline_string(\n                    "입력/수정",\n                    "내용을 입력하세요.",\n                    initialvalue=current,\n                )\n                if text is not None:\n                    widget.delete(0, tk.END)\n                    widget.insert(0, text)\n                return "break"\n        except Exception:\n            pass\n\n        return None\n\n    def bind_entry_shift_enter_recursive(self, widget=None):\n        """새로 뜬 시간표 셀 편집 Entry까지 반복 탐색해서 Shift+Enter 직접 바인딩."""\n        try:\n            if widget is None:\n                widget = self.root\n\n            if isinstance(widget, tk.Entry) and not getattr(widget, "_mdgo_shift_enter_bound", False):\n                widget._mdgo_shift_enter_bound = True\n                widget.bind("<Shift-Return>", self.entry_shift_enter_to_multiline, add="+")\n                widget.bind("<Shift-KP_Enter>", self.entry_shift_enter_to_multiline, add="+")\n\n            for child in widget.winfo_children():\n                self.bind_entry_shift_enter_recursive(child)\n        except Exception:\n            pass\n\n        try:\n            if widget is self.root:\n                self.root.after(300, self.bind_entry_shift_enter_recursive)\n        except Exception:\n            pass\n\n    def patch_global_shift_enter_for_entries(self):\n        """Entry 기반 시간표 입력창의 Shift+Enter를 최대한 강하게 보정."""\n        if getattr(self, "_mdgo_global_shift_enter_installed", False):\n            return\n        self._mdgo_global_shift_enter_installed = True\n\n        try:\n            self.root.bind_all("<Shift-Return>", self.entry_shift_enter_to_multiline, add="+")\n            self.root.bind_all("<Shift-KP_Enter>", self.entry_shift_enter_to_multiline, add="+")\n            self.root.bind_class("Entry", "<Shift-Return>", self.entry_shift_enter_to_multiline, add="+")\n            self.root.bind_class("Entry", "<Shift-KP_Enter>", self.entry_shift_enter_to_multiline, add="+")\n        except Exception:\n            pass\n\n        try:\n            self.root.after(300, self.bind_entry_shift_enter_recursive)\n        except Exception:\n            pass\n\n'
WEB_FIX = '\n# =========================================================\n# Step28 웹뷰어 UI/취소선/메모번호 최종 보정\n# =========================================================\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        """\n<script>\n(function() {\n    const doc = window.parent.document;\n    const STYLE_ID = "mdgo-step28-web-fix-style";\n\n    if (!doc.getElementById(STYLE_ID)) {\n        const style = doc.createElement("style");\n        style.id = STYLE_ID;\n        style.textContent = `\ndiv[data-testid="stButton"] > button {\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    overflow: visible !important;\n    writing-mode: horizontal-tb !important;\n    min-width: 58px !important;\n    padding-left: 0.45rem !important;\n    padding-right: 0.45rem !important;\n}\ndiv[data-testid="stButton"] {\n    overflow: visible !important;\n}\n.mdgo-web-strike {\n    text-decoration: line-through !important;\n    text-decoration-thickness: 2px !important;\n    text-decoration-color: #1f2937 !important;\n    opacity: 0.72 !important;\n}\n`;\n        doc.head.appendChild(style);\n    }\n\n    function compact(text) {\n        return (text || "").replace(/\\\\s+/g, "").trim();\n    }\n\n    function setButton(btn, label, widthPx) {\n        btn.textContent = label;\n        btn.style.whiteSpace = "nowrap";\n        btn.style.wordBreak = "keep-all";\n        btn.style.writingMode = "horizontal-tb";\n        btn.style.minWidth = widthPx + "px";\n        btn.style.width = widthPx + "px";\n        btn.style.overflow = "visible";\n        const p = btn.parentElement;\n        if (p) {\n            p.style.overflow = "visible";\n            p.style.minWidth = widthPx + "px";\n        }\n    }\n\n    function fixToolbarButtons() {\n        const buttons = Array.from(doc.querySelectorAll(\'button\'));\n        buttons.forEach((btn) => {\n            const raw = (btn.textContent || "").trim();\n            const key = compact(raw);\n\n            if (key === "달력" || raw.indexOf("📅") >= 0 || raw.indexOf("🗓") >= 0) {\n                setButton(btn, "달력", 64);\n                return;\n            }\n\n            if (raw.indexOf("☀") >= 0 || raw.indexOf("🔍") >= 0 || raw.indexOf("🔎") >= 0 || key === "조회") {\n                setButton(btn, "조회", 54);\n                return;\n            }\n\n            if (raw.indexOf("🌙") >= 0 || raw.indexOf("🔢") >= 0 || key === "89" || key === "8-9" || key === "8·9") {\n                setButton(btn, "8·9", 54);\n                return;\n            }\n\n            if (raw.indexOf("📝") >= 0 || key === "메모") {\n                setButton(btn, "메모", 58);\n                return;\n            }\n\n            if (key === "오늘") {\n                setButton(btn, "오늘", 58);\n                return;\n            }\n        });\n    }\n\n    function fixStrikeMarkers() {\n        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);\n        const nodes = [];\n        let node;\n\n        while (node = walker.nextNode()) {\n            const value = node.nodeValue || "";\n            if (value.indexOf("__STRIKE__") >= 0) {\n                nodes.push(node);\n            }\n        }\n\n        nodes.forEach((node) => {\n            const value = node.nodeValue || "";\n            const cleaned = value\n                .replace(/_{1,3}STRIKE_{1,3}\\\\s*\\\\|\\\\|\\\\|?/gi, "")\n                .replace(/_{1,3}STRIKE_{1,3}/gi, "")\n                .trim();\n\n            const span = doc.createElement("span");\n            span.className = "mdgo-web-strike";\n            span.textContent = cleaned;\n            node.parentNode.replaceChild(span, node);\n        });\n    }\n\n    function removeMemoNumbering() {\n        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);\n        const nodes = [];\n        let node;\n\n        while (node = walker.nextNode()) {\n            const value = node.nodeValue || "";\n            if (/^\\\\s*\\\\d{1,2}\\\\.\\\\s+/.test(value) || /^\\\\s*\\\\d{1,2}\\\\.\\\\s*$/.test(value)) {\n                nodes.push(node);\n            }\n        }\n\n        nodes.forEach((node) => {\n            node.nodeValue = (node.nodeValue || "")\n                .replace(/^\\\\s*\\\\d{1,2}\\\\.\\\\s+/, "")\n                .replace(/^\\\\s*\\\\d{1,2}\\\\.\\\\s*$/, "");\n        });\n    }\n\n    function runFixes() {\n        fixToolbarButtons();\n        fixStrikeMarkers();\n        removeMemoNumbering();\n    }\n\n    runFixes();\n    setTimeout(runFixes, 100);\n    setTimeout(runFixes, 400);\n    setTimeout(runFixes, 900);\n    setInterval(runFixes, 1200);\n})();\n</script>\n""",\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n'
CLEAN_VIEW = 'def clean_view_text(value):\n    text = "" if value is None else str(value)\n    text = text.replace("\\\\n", "\\n").replace("\\\\r\\\\n", "\\n")\n    return text.strip()\n\n'


def backup(path: Path, label: str):
    if not path.exists():
        return None
    backup_path = path.with_name(f"{path.stem}_before_step28_{label}_{STAMP}{path.suffix}")
    backup_path.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {backup_path}")
    return backup_path


def try_compile(text: str, label: str):
    try:
        compile(text, label, "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"{e.msg} / line {e.lineno}"


def remove_method(text: str, method_name: str) -> str:
    start = text.find(f"    def {method_name}(")
    if start == -1:
        return text

    candidates = []
    for marker in ["\n    def ", "\n    # =========================================="]:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)

    if not candidates:
        return text

    return text[:start] + text[min(candidates):]


def pick_desktop_backup_with_memo_buttons():
    desktop_dir = ROOT / "desktop"
    patterns = [
        "timetable_before_step25*.pyw",
        "timetable_before_step24*.pyw",
        "timetable_before_step23*.pyw",
        "timetable_before_step22*.pyw",
        "timetable_before_step21*.pyw",
        "timetable_before_step20*.pyw",
        "timetable_before_step19*.pyw",
        "timetable_before_step18*.pyw",
        "timetable_before_step17*.pyw",
        "timetable_before_*.pyw",
    ]

    seen = set()
    candidates = []
    for pattern in patterns:
        for f in sorted(desktop_dir.glob(pattern), reverse=True):
            if f not in seen:
                seen.add(f)
                candidates.append(f)

    for candidate in candidates:
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
            if "검색" in text and "A+" in text and "A-" in text:
                ok, _ = try_compile(text, str(candidate))
                if ok:
                    return candidate
        except Exception:
            pass

    return None


def restore_desktop_if_possible():
    candidate = pick_desktop_backup_with_memo_buttons()
    if not candidate:
        print("[안내] 검색/A+/A- 포함 PC 백업을 찾지 못했습니다. 현재 파일 기준으로 패치합니다.")
        return False

    backup(DESKTOP, "current_desktop")
    shutil.copy2(candidate, DESKTOP)
    print(f"[복구] 검색/A+/A- 포함 PC 백업으로 복원: {candidate.name}")
    return True


def patch_desktop():
    if not DESKTOP.exists():
        print(f"[경고] PC 파일 없음: {DESKTOP}")
        return False

    restored = restore_desktop_if_possible()
    backup(DESKTOP, "desktop_patch_base")

    text = DESKTOP.read_text(encoding="utf-8", errors="replace")
    original = text

    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")

    # InlineMemoText 클래스 삽입
    if "class InlineMemoText" not in text:
        pos = text.find("class ModernCalendar")
        if pos != -1:
            text = text[:pos] + INLINE_MEMO_TEXT + "\n" + text[pos:]
        else:
            text = INLINE_MEMO_TEXT + "\n" + text

    # 기존 동일 목적 메서드 제거 후 재삽입
    for name in [
        "ask_multiline_string",
        "ask_multiline_proxy",
        "memo_entry_shift_newline",
        "resize_memo_entry_inline",
        "entry_shift_enter_to_multiline",
        "bind_entry_shift_enter_recursive",
        "patch_global_shift_enter_for_entries",
    ]:
        text = remove_method(text, name)

    marker = "    def refresh_memo_list(self):"
    if marker in text:
        text = text.replace(marker, PC_METHODS + "\n" + marker, 1)
    else:
        print("[경고] refresh_memo_list 위치를 찾지 못했습니다. PC 보조 메서드 삽입 실패 가능.")

    # simpledialog를 다중 입력창으로 우회
    text = text.replace("simpledialog.askstring(", "self.ask_multiline_proxy(")

    # 하단 메모 입력칸만 Text 호환 위젯으로 변경
    text = re.sub(
        r"(self\.memo_entry\s*=\s*)tk\.Entry\(",
        r"\1InlineMemoText(",
        text,
        count=1,
    )
    text = re.sub(
        r"(self\.memo_entry\s*=\s*)ttk\.Entry\(",
        r"\1InlineMemoText(",
        text,
        count=1,
    )

    # 하단 메모 입력칸 Shift+Enter inline 줄바꿈 바인딩
    if 'self.memo_entry.bind("<Shift-Return>", self.memo_entry_shift_newline)' not in text:
        text = re.sub(
            r'(self\.memo_entry\.bind\("<Return>",\s*self\.add_memo\)\s*)',
            r'\1\n        self.memo_entry.bind("<Shift-Return>", self.memo_entry_shift_newline)\n        self.memo_entry.bind("<Shift-KP_Enter>", self.memo_entry_shift_newline)\n        self.memo_entry.bind("<KeyRelease>", self.resize_memo_entry_inline, add="+")',
            text,
            count=1,
        )

    # 전역/재귀 Entry Shift+Enter 보정 설치
    if "self.patch_global_shift_enter_for_entries()" not in text:
        text = text.replace(
            "        self.root = root",
            "        self.root = root\n        self.patch_global_shift_enter_for_entries()",
            1,
        )

    ok, err = try_compile(text, str(DESKTOP))
    if not ok:
        print(f"[경고] PC 파일 문법 확인 실패: {err}")

    if text != original or restored:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] PC 검색/A+/A- 복구 + 줄바꿈 보정 저장")
        return True

    print("[안내] PC 변경 없음")
    return False


def replace_clean_view(text: str) -> str:
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


def ensure_components_import(text: str) -> str:
    if "import streamlit.components.v1 as components" in text:
        return text
    if "import streamlit as st" in text:
        return text.replace(
            "import streamlit as st",
            "import streamlit as st\nimport streamlit.components.v1 as components",
            1,
        )
    return "import streamlit.components.v1 as components\n" + text


def remove_previous_web_fix(text: str) -> str:
    # Step27/Step28 블록 중복 방지
    for label in [
        "Step27 웹뷰어 UI/취소선/메모번호 보정",
        "Step28 웹뷰어 UI/취소선/메모번호 최종 보정",
    ]:
        while label in text:
            start = text.find("# =========================================================\n# " + label)
            if start == -1:
                break
            end = text.find("\n# =========================================================", start + 20)
            if end == -1:
                # 파일 끝 블록
                text = text[:start].rstrip() + "\n"
                break
            text = text[:start] + text[end:]

    return text


def patch_mobile():
    if not MOBILE.exists():
        print(f"[경고] 모바일 파일 없음: {MOBILE}")
        return False

    backup(MOBILE, "mobile")
    text = MOBILE.read_text(encoding="utf-8", errors="replace")
    original = text

    text = ensure_components_import(text)
    text = replace_clean_view(text)

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

    # 빈 append 호출 안전 보정
    text = re.sub(r"(\b\w+\.append)\(\s*\)", r'\1("")', text)

    text = remove_previous_web_fix(text)
    text = text.rstrip() + "\n\n" + WEB_FIX + "\n"

    ok, err = try_compile(text, str(MOBILE))
    if not ok:
        print(f"[경고] mobile/app.py 문법 확인 실패: {err}")

    if text != original:
        MOBILE.write_text(text, encoding="utf-8")
        print("[완료] 웹뷰어 버튼/취소선/메모번호 최종 보정 저장")
        return True

    print("[안내] 모바일 변경 없음")
    return False


def main():
    print("==============================================")
    print("Step28 web + PC final repair")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    try:
        pc_changed = patch_desktop()
        mobile_changed = patch_mobile()

        print()
        print("[완료]")
        print("- PC 변경:", "있음" if pc_changed else "없음")
        print("- 모바일 변경:", "있음" if mobile_changed else "없음")
        print()
        print("확인:")
        print("1) python desktop\\timetable.pyw")
        print("   - 하단 메모 입력칸의 검색/A+/A- 버튼 복구")
        print("   - 하단 메모 입력칸 Shift+Enter: 팝업 없이 입력칸 자체 줄바꿈")
        print("   - 시간표 칸 Shift+Enter: 다중 입력 가능")
        print()
        print("2) python -m streamlit run mobile\\app.py")
        print("   - 달력 버튼 가로 표시")
        print("   - 조회/8·9 텍스트 표시")
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

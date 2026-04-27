# tools/step27_web_ui_pc_multiline_repair.py
# ------------------------------------------------------------
# Step27 통합 보정
#
# 1) 웹뷰어 mobile/app.py
#    - 달력 버튼 세로 깨짐 보정
#    - 태양 아이콘 -> 조회
#    - 달 아이콘 -> 8·9
#    - __STRIKE__ 완료표시를 취소선으로 표시
#    - 메모 넘버링 제거
#
# 2) PC desktop/timetable.pyw
#    - Step25로 사라진 하단 메모 검색/A+/A- 버튼 복구를 위해
#      가능하면 desktop/timetable_before_step25*.pyw 백업으로 복원
#    - 하단 메모 입력칸은 팝업 없이 Shift+Enter 줄바꿈 + 입력칸 자동 확장
#    - 시간표 칸이 simpledialog 또는 Entry 기반일 때 Shift+Enter 보정
#
# 실행:
#   python tools\step27_web_ui_pc_multiline_repair.py
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

INLINE_MEMO_TEXT = '\nclass InlineMemoText(tk.Text):\n    """Entry처럼 get/delete/insert를 쓸 수 있는 한 줄 시작형 다중 입력 Text."""\n    def __init__(self, master=None, **kwargs):\n        # tk.Entry 전용 옵션이 섞여 들어오면 제거\n        kwargs.pop("textvariable", None)\n        kwargs.pop("show", None)\n        kwargs.pop("validate", None)\n        kwargs.pop("validatecommand", None)\n        kwargs.setdefault("height", 1)\n        kwargs.setdefault("wrap", "word")\n        kwargs.setdefault("undo", True)\n        super().__init__(master, **kwargs)\n\n    def get(self, *args):\n        if not args:\n            return super().get("1.0", "end-1c")\n        return super().get(*args)\n\n    def delete(self, *args):\n        if len(args) >= 1 and args[0] == 0:\n            return super().delete("1.0", tk.END)\n        return super().delete(*args)\n\n    def insert(self, index, chars, *args):\n        if index == 0:\n            index = "1.0"\n        return super().insert(index, chars, *args)\n\n'
PC_METHODS = '\n    def ask_multiline_string(self, title, prompt, initialvalue=""):\n        """작은 다중 입력창. 시간표 칸/기존 simpledialog 입력용."""\n        result = {"value": None}\n\n        win = tk.Toplevel(self.root)\n        win.title(title)\n        win.transient(self.root)\n        win.grab_set()\n        win.resizable(True, True)\n\n        try:\n            win.iconbitmap(self.icon_path)\n        except Exception:\n            pass\n\n        try:\n            t = self.get_active_theme()\n        except Exception:\n            t = {}\n\n        bg = t.get("panel_bg", t.get("cell_bg", "#ffffff"))\n        fg = t.get("cell_fg", "#111827")\n        input_bg = t.get("input_bg", "#ffffff")\n        border = t.get("panel_border", t.get("grid", "#d0d7de"))\n        accent = t.get("accent", "#2563eb")\n\n        win.configure(bg=bg)\n\n        frame = tk.Frame(win, bg=bg, padx=10, pady=10)\n        frame.pack(fill="both", expand=True)\n\n        tk.Label(\n            frame,\n            text=prompt,\n            bg=bg,\n            fg=fg,\n            font=("맑은 고딕", 9, "bold"),\n            anchor="w",\n            justify="left",\n        ).pack(fill="x", pady=(0, 5))\n\n        text_box = tk.Text(\n            frame,\n            height=2,\n            width=42,\n            wrap="word",\n            bg=input_bg,\n            fg=fg,\n            insertbackground=fg,\n            relief="solid",\n            bd=1,\n            highlightthickness=1,\n            highlightbackground=border,\n            font=("맑은 고딕", 10),\n            undo=True,\n        )\n        text_box.pack(fill="x", expand=False)\n        text_box.insert("1.0", initialvalue or "")\n        text_box.focus_set()\n\n        tk.Label(\n            frame,\n            text="Shift+Enter: 줄바꿈 / Enter: 저장 / Esc: 취소",\n            bg=bg,\n            fg=t.get("muted_fg", "#667085"),\n            font=("맑은 고딕", 8),\n            anchor="w",\n        ).pack(fill="x", pady=(5, 7))\n\n        btn_frame = tk.Frame(frame, bg=bg)\n        btn_frame.pack(fill="x")\n\n        def resize_editor(event=None):\n            try:\n                line_count = max(1, int(text_box.index("end-1c").split(".")[0]))\n                height = max(2, min(7, line_count))\n                text_box.configure(height=height)\n                win.update_idletasks()\n                win.geometry(f"460x{145 + height * 20}")\n            except Exception:\n                pass\n            return None\n\n        def on_ok(event=None):\n            result["value"] = text_box.get("1.0", "end-1c").strip()\n            win.destroy()\n            return "break"\n\n        def on_cancel(event=None):\n            result["value"] = None\n            win.destroy()\n            return "break"\n\n        def insert_newline(event=None):\n            text_box.insert("insert", chr(10))\n            resize_editor()\n            return "break"\n\n        def on_return(event=None):\n            try:\n                if int(getattr(event, "state", 0) or 0) & 0x0001:\n                    return insert_newline(event)\n            except Exception:\n                pass\n            return on_ok(event)\n\n        tk.Button(\n            btn_frame,\n            text="확인",\n            command=on_ok,\n            bg=accent,\n            fg="white",\n            relief="flat",\n            padx=14,\n            pady=4,\n            cursor="hand2",\n        ).pack(side="right", padx=(6, 0))\n\n        tk.Button(\n            btn_frame,\n            text="취소",\n            command=on_cancel,\n            bg=t.get("hover_btn", "#eef3fb"),\n            fg=fg,\n            relief="flat",\n            padx=14,\n            pady=4,\n            cursor="hand2",\n        ).pack(side="right")\n\n        text_box.bind("<Shift-Return>", insert_newline)\n        text_box.bind("<Shift-KP_Enter>", insert_newline)\n        text_box.bind("<Return>", on_return)\n        text_box.bind("<KP_Enter>", on_return)\n        text_box.bind("<KeyRelease>", resize_editor, add="+")\n        text_box.bind("<Escape>", on_cancel)\n        win.bind("<Escape>", on_cancel)\n\n        try:\n            self.root.update_idletasks()\n            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 460) // 2)\n            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 185) // 2)\n            win.geometry(f"460x185+{x}+{y}")\n        except Exception:\n            win.geometry("460x185")\n\n        resize_editor()\n        self.root.wait_window(win)\n        return result["value"]\n\n    def ask_multiline_proxy(self, title, prompt, **kwargs):\n        return self.ask_multiline_string(title, prompt, initialvalue=kwargs.get("initialvalue", ""))\n\n    def memo_entry_shift_newline(self, event=None):\n        """하단 메모 입력칸: 팝업 없이 입력칸 자체에서 줄바꿈."""\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("insert", chr(10))\n                self.resize_memo_entry_inline()\n                return "break"\n        except Exception:\n            pass\n        return "break"\n\n    def resize_memo_entry_inline(self, event=None):\n        """하단 메모 입력칸을 입력 줄 수에 맞춰 자연스럽게 확장."""\n        try:\n            if not isinstance(self.memo_entry, tk.Text):\n                return None\n            raw = self.memo_entry.get("1.0", "end-1c")\n            line_count = max(1, raw.count(chr(10)) + 1)\n            height = max(1, min(5, line_count))\n            self.memo_entry.configure(height=height)\n        except Exception:\n            pass\n        return None\n\n    def patch_global_shift_enter_for_entries(self):\n        """시간표 칸이 별도 Entry 편집 위젯일 때 Shift+Enter를 작은 다중 입력창으로 연결."""\n        if getattr(self, "_mdgo_global_shift_enter_installed", False):\n            return\n        self._mdgo_global_shift_enter_installed = True\n\n        def handler(event=None):\n            try:\n                widget = self.root.focus_get()\n            except Exception:\n                widget = None\n\n            # 하단 메모 입력칸은 inline 줄바꿈\n            try:\n                if widget is self.memo_entry:\n                    return self.memo_entry_shift_newline(event)\n            except Exception:\n                pass\n\n            # 시간표 셀 등 일반 Entry는 작은 다중 입력창으로 보정\n            try:\n                if isinstance(widget, tk.Entry):\n                    current = widget.get()\n                    text = self.ask_multiline_string(\n                        "입력/수정",\n                        "내용을 입력하세요.",\n                        initialvalue=current,\n                    )\n                    if text is not None:\n                        widget.delete(0, tk.END)\n                        widget.insert(0, text)\n                    return "break"\n            except Exception:\n                pass\n\n            return None\n\n        try:\n            self.root.bind_all("<Shift-Return>", handler, add="+")\n            self.root.bind_all("<Shift-KP_Enter>", handler, add="+")\n        except Exception:\n            pass\n\n'
WEB_FIX = '\n# =========================================================\n# Step27 웹뷰어 UI/취소선/메모번호 보정\n# =========================================================\ntry:\n    import streamlit.components.v1 as components\n    components.html(\n        """\n<script>\n(function() {\n    const doc = window.parent.document;\n    const STYLE_ID = "mdgo-step27-web-fix-style";\n\n    if (!doc.getElementById(STYLE_ID)) {\n        const style = doc.createElement("style");\n        style.id = STYLE_ID;\n        style.textContent = `\ndiv[data-testid="stButton"] > button {\n    white-space: nowrap !important;\n    word-break: keep-all !important;\n    min-width: 58px !important;\n    padding-left: 0.45rem !important;\n    padding-right: 0.45rem !important;\n}\n.mdgo-web-strike {\n    text-decoration: line-through !important;\n    text-decoration-thickness: 2px !important;\n    text-decoration-color: #1f2937 !important;\n    opacity: 0.72 !important;\n}\n`;\n        doc.head.appendChild(style);\n    }\n\n    function compact(text) {\n        return (text || "").replace(/\\\\s+/g, "").trim();\n    }\n\n    function fixToolbarButtons() {\n        const buttons = Array.from(doc.querySelectorAll(\'button\'));\n        buttons.forEach((btn) => {\n            const raw = (btn.textContent || "").trim();\n            const key = compact(raw);\n\n            if (key === "달력" || raw.indexOf("📅") >= 0 || raw.indexOf("🗓") >= 0) {\n                btn.textContent = "달력";\n            }\n\n            if (raw.indexOf("☀") >= 0 || raw.indexOf("🔍") >= 0 || raw.indexOf("🔎") >= 0 || key === "조회") {\n                btn.textContent = "조회";\n            }\n\n            if (raw.indexOf("🌙") >= 0 || raw.indexOf("🔢") >= 0 || key === "89" || key === "8-9" || key === "8·9") {\n                btn.textContent = "8·9";\n            }\n\n            if (raw.indexOf("📝") >= 0 || key === "메모") {\n                btn.textContent = "메모";\n            }\n\n            if (key === "오늘") {\n                btn.textContent = "오늘";\n            }\n        });\n    }\n\n    function fixStrikeMarkers() {\n        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);\n        const nodes = [];\n        let node;\n\n        while (node = walker.nextNode()) {\n            const value = node.nodeValue || "";\n            if (value.indexOf("__STRIKE__") >= 0) {\n                nodes.push(node);\n            }\n        }\n\n        nodes.forEach((node) => {\n            const value = node.nodeValue || "";\n            const cleaned = value\n                .replace(/_{1,3}STRIKE_{1,3}\\\\s*\\\\|\\\\|\\\\|?/gi, "")\n                .replace(/_{1,3}STRIKE_{1,3}/gi, "")\n                .trim();\n\n            const span = doc.createElement("span");\n            span.className = "mdgo-web-strike";\n            span.textContent = cleaned;\n            node.parentNode.replaceChild(span, node);\n        });\n    }\n\n    function removeMemoNumbering() {\n        const walker = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT, null);\n        const nodes = [];\n        let node;\n\n        while (node = walker.nextNode()) {\n            const value = node.nodeValue || "";\n            if (/^\\\\s*\\\\d+\\\\.\\\\s+/.test(value)) {\n                nodes.push(node);\n            }\n        }\n\n        nodes.forEach((node) => {\n            node.nodeValue = (node.nodeValue || "").replace(/^\\\\s*\\\\d+\\\\.\\\\s+/, "");\n        });\n    }\n\n    function runFixes() {\n        fixToolbarButtons();\n        fixStrikeMarkers();\n        removeMemoNumbering();\n    }\n\n    runFixes();\n    setTimeout(runFixes, 100);\n    setTimeout(runFixes, 400);\n    setTimeout(runFixes, 900);\n    setInterval(runFixes, 1500);\n})();\n</script>\n""",\n        height=1,\n        width=1,\n    )\nexcept Exception:\n    pass\n'
CLEAN_VIEW = 'def clean_view_text(value):\n    text = "" if value is None else str(value)\n    text = text.replace("\\\\n", "\\n").replace("\\\\r\\\\n", "\\n")\n    return text.strip()\n\n'


def backup(path: Path, label: str):
    if not path.exists():
        return None
    backup_path = path.with_name(f"{path.stem}_before_step27_{label}_{STAMP}{path.suffix}")
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


def restore_desktop_from_before_step25_if_possible():
    candidates = sorted((ROOT / "desktop").glob("timetable_before_step25*.pyw"), reverse=True)
    if not candidates:
        print("[안내] desktop/timetable_before_step25*.pyw 백업 없음 - 현재 파일 기준으로 패치")
        return False

    selected = candidates[0]
    backup(DESKTOP, "current_desktop")
    shutil.copy2(selected, DESKTOP)
    print(f"[복구] PC 파일을 Step25 이전 백업으로 복원: {selected.name}")
    return True


def patch_desktop():
    if not DESKTOP.exists():
        print(f"[경고] PC 파일 없음: {DESKTOP}")
        return False

    restored = restore_desktop_from_before_step25_if_possible()
    backup(DESKTOP, "desktop_patch_base")

    text = DESKTOP.read_text(encoding="utf-8", errors="replace")
    original = text

    # 창 제목/메뉴명 유지
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")

    # InlineMemoText 클래스 삽입
    if "class InlineMemoText" not in text:
        insert_pos = text.find("class ModernCalendar")
        if insert_pos != -1:
            text = text[:insert_pos] + INLINE_MEMO_TEXT + "\n" + text[insert_pos:]
        else:
            text = INLINE_MEMO_TEXT + "\n" + text

    # 기존 패치 메서드 제거 후 재삽입
    for name in [
        "ask_multiline_string",
        "ask_multiline_proxy",
        "memo_entry_shift_newline",
        "resize_memo_entry_inline",
        "patch_global_shift_enter_for_entries",
    ]:
        text = remove_method(text, name)

    marker = "    def refresh_memo_list(self):"
    if marker in text and "def ask_multiline_string(self" not in text:
        text = text.replace(marker, PC_METHODS + "\n" + marker, 1)
    elif marker not in text:
        print("[경고] refresh_memo_list 위치를 찾지 못해 PC 메서드 삽입을 건너뜁니다.")

    # simpledialog 입력을 다중 입력창으로 우회
    text = text.replace("simpledialog.askstring(", "self.ask_multiline_proxy(")

    # 하단 메모 입력칸만 InlineMemoText로 변경
    text = re.sub(
        r"(self\.memo_entry\s*=\s*)tk\.Entry\(",
        r"\1InlineMemoText(",
        text,
        count=1,
    )

    # memo_entry Shift+Enter inline 줄바꿈 바인딩 추가
    if 'self.memo_entry.bind("<Shift-Return>", self.memo_entry_shift_newline)' not in text:
        text = re.sub(
            r'(self\.memo_entry\.bind\("<Return>",\s*self\.add_memo\)\s*)',
            r'\1\n        self.memo_entry.bind("<Shift-Return>", self.memo_entry_shift_newline)\n        self.memo_entry.bind("<Shift-KP_Enter>", self.memo_entry_shift_newline)\n        self.memo_entry.bind("<KeyRelease>", self.resize_memo_entry_inline, add="+")',
            text,
            count=1,
        )

    # 전역 Shift+Enter 보정 설치
    if "self.patch_global_shift_enter_for_entries()" not in text:
        # __init__ 초반 root 할당 뒤에 설치
        text = text.replace(
            "        self.root = root",
            "        self.root = root\n        self.patch_global_shift_enter_for_entries()",
            1,
        )

    # Text 입력칸이 Entry API 호출을 받을 수 있게 InlineMemoText가 호환 처리하므로 기존 검색/A+/A- 로직은 유지
    if text != original or restored:
        ok, err = try_compile(text, str(DESKTOP))
        if not ok:
            print(f"[경고] PC 파일 문법 확인 실패: {err}")
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] PC 줄바꿈/하단 버튼 복구 패치 저장")
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


def remove_old_step_web_fix(text: str) -> str:
    # 이전 Step의 깨진/중복 웹 보정 블록 제거
    while "Step27 웹뷰어 UI/취소선/메모번호 보정" in text:
        start = text.find("# =========================================================\n# Step27 웹뷰어 UI/취소선/메모번호 보정")
        if start == -1:
            break
        end = text.find("\n# =========================================================", start + 20)
        if end == -1:
            break
        text = text[:start] + text[end:]

    # 이전 style id가 있는 components.html 블록도 가능한 범위에서 제거
    for key in ["mdgo-step27-web-fix-style"]:
        while key in text:
            idx = text.find(key)
            start = text.rfind("# =========================================================", 0, idx)
            if start == -1:
                start = text.rfind("try:", 0, idx)
            end = text.find("\n# =========================================================", idx)
            if start == -1 or end == -1:
                break
            text = text[:start] + text[end:]

    return text


def append_web_fix_at_end(text: str) -> str:
    text = remove_old_step_web_fix(text)
    return text.rstrip() + "\n\n" + WEB_FIX + "\n"


def patch_mobile():
    if not MOBILE.exists():
        print(f"[경고] 모바일 파일 없음: {MOBILE}")
        return False

    backup(MOBILE, "mobile")
    text = MOBILE.read_text(encoding="utf-8", errors="replace")
    original = text

    text = ensure_components_import(text)
    text = replace_clean_view(text)

    # Python 코드에 남아 있는 버튼 literal도 같이 보정
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

    # 비어 있는 append 호출 보정
    text = re.sub(r"(\b\w+\.append)\(\s*\)", r'\1("")', text)

    # 웹 DOM 보정은 파일 끝에 넣어 최종 렌더 이후에도 반복 작동하게 함
    text = append_web_fix_at_end(text)

    ok, err = try_compile(text, str(MOBILE))
    if not ok:
        print(f"[경고] mobile/app.py 문법 확인 실패: {err}")
        # 문법 오류가 있더라도 저장은 하되, 기존 백업이 있으므로 확인 가능
    MOBILE.write_text(text, encoding="utf-8")

    print("[완료] 웹뷰어 버튼/취소선/메모번호 보정 패치 저장")
    return text != original


def main():
    print("==============================================")
    print("Step27 web UI + PC multiline repair")
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
        print("   - 하단 메모 입력칸: 찾기/A+/A- 버튼 복구 여부")
        print("   - 하단 메모 입력칸: Shift+Enter 시 팝업 없이 입력칸 자체 줄바꿈")
        print("   - 시간표 칸: Shift+Enter 줄바꿈 가능 여부")
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

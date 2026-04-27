# tools/step39_memo_indent_and_edit_ui.py
# ------------------------------------------------------------
# Step39: 메모 리스트 줄바꿈 표시 + 메모 수정창 UI 정리
#
# 적용 내용
# 1) 메모 리스트에서 줄바꿈된 두 번째 줄 이후를 들여쓰기
#    - 예: "굿\n살아남" 표시 시 "살아남"이 첫 줄의 "굿" 위치에 맞춰 보이도록 보정
#    - 저장 데이터는 변경하지 않고, 화면 표시 시에만 들여쓰기
#
# 2) 메모 리스트에서 수정할 때 뜨는 입력/수정 팝업 UI를
#    시간표 내 내용 입력창과 비슷한 작고 단정한 UI로 통일
#    - 입력줄은 3줄
#    - Enter = 저장
#    - Shift+Enter = 줄바꿈
#    - Esc = 취소
#
# 주의:
# - 시간표 내 내용 입력창은 현재 만족스럽게 작동하므로 건드리지 않음.
#
# 실행:
#   python tools\step39_memo_indent_and_edit_ui.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

COMPACT_ASK_METHOD = '\n    def ask_multiline_string(self, title, prompt, initialvalue=""):\n        """메모 수정용 다중 입력창: 시간표 내용 입력창과 같은 작고 단정한 UI."""\n        result = {"value": None}\n\n        win = tk.Toplevel(self.root)\n        win.title("내용 입력")\n        win.transient(self.root)\n        win.grab_set()\n        win.resizable(False, False)\n\n        try:\n            win.iconbitmap(self.icon_path)\n        except Exception:\n            pass\n\n        try:\n            t = self.get_active_theme()\n        except Exception:\n            t = {}\n\n        bg = t.get("panel_bg", "#ecf0f1")\n        fg = t.get("cell_fg", "#111827")\n        input_bg = t.get("input_bg", "#ffffff")\n        border = t.get("panel_border", "#d0d7de")\n\n        win.configure(bg=bg)\n\n        frame = tk.Frame(win, bg=bg, padx=14, pady=12)\n        frame.pack(fill="both", expand=True)\n\n        tk.Label(\n            frame,\n            text="내용을 입력하세요.",\n            bg=bg,\n            fg=fg,\n            font=("맑은 고딕", 9, "bold"),\n            anchor="w",\n        ).pack(fill="x", pady=(0, 6))\n\n        text_box = tk.Text(\n            frame,\n            height=3,\n            width=33,\n            wrap="word",\n            bg=input_bg,\n            fg=fg,\n            insertbackground=fg,\n            relief="solid",\n            bd=1,\n            highlightthickness=0,\n            font=("맑은 고딕", 10),\n            undo=True,\n        )\n        text_box.pack(fill="x")\n        text_box.insert("1.0", initialvalue or "")\n        text_box.focus_set()\n\n        btn_frame = tk.Frame(frame, bg=bg)\n        btn_frame.pack(fill="x", pady=(12, 0))\n\n        def on_ok(event=None):\n            result["value"] = text_box.get("1.0", "end-1c").strip()\n            win.destroy()\n            return "break"\n\n        def on_cancel(event=None):\n            result["value"] = None\n            win.destroy()\n            return "break"\n\n        def insert_newline(event=None):\n            text_box.insert("insert", chr(10))\n            return "break"\n\n        def on_return(event=None):\n            try:\n                if int(getattr(event, "state", 0) or 0) & 0x0001:\n                    return insert_newline(event)\n            except Exception:\n                pass\n            return on_ok(event)\n\n        tk.Button(\n            btn_frame,\n            text="저장",\n            command=on_ok,\n            bg="#27ae60",\n            fg="white",\n            activebackground="#229954",\n            activeforeground="white",\n            relief="flat",\n            bd=0,\n            padx=18,\n            pady=5,\n            cursor="hand2",\n            font=("맑은 고딕", 9, "bold"),\n        ).pack(side="left")\n\n        tk.Button(\n            btn_frame,\n            text="취소",\n            command=on_cancel,\n            bg="#7f8c8d",\n            fg="white",\n            activebackground="#6f7c7d",\n            activeforeground="white",\n            relief="flat",\n            bd=0,\n            padx=18,\n            pady=5,\n            cursor="hand2",\n            font=("맑은 고딕", 9, "bold"),\n        ).pack(side="right")\n\n        text_box.bind("<Shift-Return>", insert_newline)\n        text_box.bind("<Shift-KP_Enter>", insert_newline)\n        text_box.bind("<Return>", on_return)\n        text_box.bind("<KP_Enter>", on_return)\n        text_box.bind("<Escape>", on_cancel)\n        win.bind("<Escape>", on_cancel)\n\n        try:\n            self.root.update_idletasks()\n            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 330) // 2)\n            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 150) // 2)\n            win.geometry(f"330x150+{x}+{y}")\n        except Exception:\n            win.geometry("330x150")\n\n        self.root.wait_window(win)\n        return result["value"]\n\n    def ask_multiline_proxy(self, title, prompt, **kwargs):\n        return self.ask_multiline_string(title, prompt, initialvalue=kwargs.get("initialvalue", ""))\n\n'
INDENT_METHODS = '\n    def format_memo_list_multiline_text(self, value):\n        """메모 리스트 표시용: 줄바꿈 이후 줄을 첫 줄 메모 글자 위치에 맞춰 들여쓰기."""\n        text = "" if value is None else str(value)\n        text = text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n        if "\\n" not in text:\n            return text\n        return text.replace("\\n", "\\n    ")\n\n    def install_memo_text_insert_indent_patch(self):\n        """memo_text.insert에 표시용 줄바꿈 들여쓰기만 적용. 저장 데이터는 건드리지 않음."""\n        try:\n            if getattr(self.memo_text, "_mdgo_step39_indent_installed", False):\n                return\n            original_insert = self.memo_text.insert\n\n            def _insert(index, chars, *tags):\n                try:\n                    if isinstance(chars, str):\n                        # 끝에 붙는 개행은 그대로 두고, 실제 내용 내부 개행만 들여쓰기\n                        tail = ""\n                        while chars.endswith("\\n"):\n                            tail = "\\n" + tail\n                            chars = chars[:-1]\n\n                        chars = chars.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n                        if "\\n" in chars:\n                            chars = self.format_memo_list_multiline_text(chars)\n\n                        chars = chars + tail\n                except Exception:\n                    pass\n                return original_insert(index, chars, *tags)\n\n            self.memo_text.insert = _insert\n            self.memo_text._mdgo_step39_indent_installed = True\n        except Exception:\n            pass\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step39_memo_ui_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


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


def patch_compact_memo_edit_popup(text: str) -> tuple[str, int]:
    changed = 0

    for name in ["ask_multiline_string", "ask_multiline_proxy"]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def refresh_memo_list(self):"
    if marker not in text:
        raise RuntimeError("refresh_memo_list 위치를 찾지 못했습니다.")

    text = text.replace(marker, COMPACT_ASK_METHOD + "\n" + marker, 1)
    changed += 1

    # 혹시 simpledialog.askstring을 사용하는 메모 수정 경로가 있으면 compact 창으로 통일
    before = text
    text = text.replace("simpledialog.askstring(", "self.ask_multiline_proxy(")
    if text != before:
        changed += 1

    return text, changed


def patch_memo_list_indent(text: str) -> tuple[str, int]:
    changed = 0

    for name in ["format_memo_list_multiline_text", "install_memo_text_insert_indent_patch"]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def refresh_memo_list(self):"
    if marker not in text:
        raise RuntimeError("refresh_memo_list 위치를 찾지 못했습니다.")

    text = text.replace(marker, INDENT_METHODS + "\n" + marker, 1)
    changed += 1

    # memo_text 위젯 생성/pack 이후 insert wrapper 설치
    if "self.install_memo_text_insert_indent_patch()" not in text:
        # 가장 안정적인 위치: self.memo_text가 pack된 직후
        patterns = [
            r"(        self\.memo_text\.pack\([^\n]*\)\n)",
            r"(        self\.memo_text\.grid\([^\n]*\)\n)",
        ]

        inserted = False
        for pat in patterns:
            text2, n = re.subn(
                pat,
                r"\1        self.install_memo_text_insert_indent_patch()\n",
                text,
                count=1,
            )
            if n:
                text = text2
                changed += n
                inserted = True
                break

        if not inserted:
            print("[경고] self.memo_text.pack/grid 위치를 찾지 못해 자동 설치 호출을 넣지 못했습니다.")

    return text, changed


def main():
    print("==============================================")
    print("Step39 memo indent + edit UI")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not DESKTOP.exists():
        print(f"[오류] PC 파일이 없습니다: {DESKTOP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup(DESKTOP)

    text = DESKTOP.read_text(encoding="utf-8", errors="replace")
    original = text

    try:
        text, indent_changes = patch_memo_list_indent(text)
        text, popup_changes = patch_compact_memo_edit_popup(text)
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        compile(text, str(DESKTOP), "exec")
        print("[확인] PC 파일 문법 OK")
    except Exception as e:
        print("[경고] PC 파일 문법 확인 실패")
        print(e)

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] Step39 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 메모 리스트 줄바꿈 들여쓰기 변경: {indent_changes}")
    print(f"- 메모 수정 팝업 UI 변경: {popup_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 메모 리스트에서 줄바꿈된 두 번째 줄이 첫 줄 글자 위치와 맞는지")
    print("2. 메모 리스트에서 메모 수정 시 팝업이 작고 단정한 UI로 뜨는지")
    print("3. 수정 팝업에서 Enter=저장, Shift+Enter=줄바꿈인지")
    print("4. 시간표 내 내용 입력창은 이전처럼 그대로 잘 작동하는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

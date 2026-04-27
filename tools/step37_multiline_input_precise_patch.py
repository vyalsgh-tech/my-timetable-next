# tools/step37_multiline_input_precise_patch.py
# ------------------------------------------------------------
# Step37: PC버전 입력창 직접 패치
#
# 적용 내용
# 1) 시간표 내 "내용 입력" 창
#    - 기존 1줄 Entry를 3줄 Text 입력창으로 변경
#    - UI는 기존 "내용 입력" 창 스타일 유지
#    - Enter = 저장
#    - Shift+Enter = 줄바꿈
#
# 2) 하단 메모 입력줄
#    - 새 팝업창을 열지 않고 현재 메모 입력칸에서 Shift+Enter 줄바꿈
#    - 입력 줄 수에 따라 최대 3줄까지만 자연스럽게 확장
#    - 기존 검색 / A+ / A- 버튼은 그대로 유지
#
# 실행:
#   python tools\step37_multiline_input_precise_patch.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

INLINE_CLASS = '\n# =========================================================\n# Step37: 메모 입력칸 다중 줄 입력 지원 클래스\n# =========================================================\nclass MdgoInlineTextEntry(tk.Text):\n    """tk.Entry처럼 get/delete/insert를 쓸 수 있는 1줄 시작형 Text 위젯."""\n    def __init__(self, master=None, **kwargs):\n        for key in (\n            "textvariable", "show", "validate", "validatecommand",\n            "invalidcommand", "justify"\n        ):\n            kwargs.pop(key, None)\n        kwargs.setdefault("height", 1)\n        kwargs.setdefault("wrap", "word")\n        kwargs.setdefault("undo", True)\n        super().__init__(master, **kwargs)\n\n    def get(self, *args):\n        if not args:\n            return super().get("1.0", "end-1c")\n        return super().get(*args)\n\n    def delete(self, *args):\n        if len(args) >= 1 and args[0] == 0:\n            return super().delete("1.0", tk.END)\n        return super().delete(*args)\n\n    def insert(self, index, chars, *args):\n        if index == 0:\n            index = "1.0"\n        return super().insert(index, chars, *args)\n# =========================================================\n\n'
MEMO_METHODS = '\n    def get_memo_entry_text(self):\n        try:\n            return self.memo_entry.get().strip()\n        except Exception:\n            return ""\n\n    def clear_memo_entry(self):\n        try:\n            self.memo_entry.delete(0, tk.END)\n        except Exception:\n            try:\n                self.memo_entry.delete("1.0", tk.END)\n            except Exception:\n                pass\n\n    def resize_memo_entry_input(self, event=None):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                raw = self.memo_entry.get("1.0", "end-1c")\n                line_count = max(1, raw.count(chr(10)) + 1)\n                self.memo_entry.configure(height=max(1, min(3, line_count)))\n        except Exception:\n            pass\n        return None\n\n    def memo_entry_shift_enter_inline(self, event=None):\n        """하단 메모 입력칸에서 새 팝업 없이 현재 입력칸에 줄바꿈."""\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("insert", chr(10))\n                self.resize_memo_entry_input()\n                return "break"\n        except Exception:\n            pass\n        return "break"\n\n    def add_memo(self, ev=None):\n        # Shift+Enter는 저장이 아니라 현재 메모 입력칸 안에서 줄바꿈\n        try:\n            state = int(getattr(ev, "state", 0) or 0)\n        except Exception:\n            state = 0\n        if ev is not None and (state & 0x0001):\n            return self.memo_entry_shift_enter_inline(ev)\n\n        text = self.get_memo_entry_text()\n        result = self.create_memo_from_text(text)\n\n        self.clear_memo_entry()\n        try:\n            self.memo_entry.insert(0, "메모를 입력하세요")\n            self.memo_entry.config(fg="gray")\n        except Exception:\n            pass\n        self.resize_memo_entry_input()\n        return result\n\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step37_multiline_{STAMP}{path.suffix}")
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


def remove_old_step37(text: str) -> str:
    # 이전 Step37 클래스 블록 제거
    while "Step37: 메모 입력칸 다중 줄 입력 지원 클래스" in text:
        idx = text.find("Step37: 메모 입력칸 다중 줄 입력 지원 클래스")
        start = text.rfind("# =========================================================", 0, idx)
        end = text.find("# =========================================================", idx + 20)
        if start == -1 or end == -1:
            break
        # 두 번째 구분선 줄까지 제거
        end_line = text.find("\n", end)
        end_line = len(text) if end_line == -1 else end_line + 1
        text = text[:start] + text[end_line:]
    return text


def insert_inline_class(text: str) -> str:
    if "class MdgoInlineTextEntry" in text:
        return text

    # ModernCalendar 앞이 가장 안전한 전역 클래스 위치
    pos = text.find("class ModernCalendar")
    if pos != -1:
        return text[:pos] + INLINE_CLASS + text[pos:]

    # fallback: import 블록 뒤
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            insert_at = i + 1
    return "\n".join(lines[:insert_at]) + "\n\n" + INLINE_CLASS + "\n".join(lines[insert_at:]) + "\n"


def patch_memo_input(text: str) -> tuple[str, int]:
    changed = 0

    # 기존 popup 유도 메서드/구버전 add_memo 제거 후 새 메서드 삽입
    for name in [
        "get_memo_entry_text",
        "clear_memo_entry",
        "resize_memo_entry_input",
        "memo_entry_shift_enter_inline",
        "add_memo",
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def refresh_memo_list(self):"
    if marker not in text:
        raise RuntimeError("refresh_memo_list 위치를 찾지 못했습니다.")

    text = text.replace(marker, MEMO_METHODS + "\n" + marker, 1)
    changed += 1

    # 하단 memo_entry를 Entry -> MdgoInlineTextEntry로 직접 교체
    before = text
    text = text.replace(
        "self.memo_entry = tk.Entry(self.memo_input_f, font=self.font_title, cursor=\"xterm\")",
        "self.memo_entry = MdgoInlineTextEntry(self.memo_input_f, font=self.font_title, cursor=\"xterm\", height=1, wrap=\"word\")",
        1,
    )
    if text != before:
        changed += 1
    else:
        # ttk.Entry 또는 이미 변형된 경우 대비
        text2 = re.sub(
            r"(self\.memo_entry\s*=\s*)tk\.Entry\((self\.memo_input_f,[^\n]*)\)",
            r"\1MdgoInlineTextEntry(\2, height=1, wrap=\"word\")",
            text,
            count=1,
        )
        if text2 != text:
            text = text2
            changed += 1

    # Shift+Enter와 자동 높이 조정 bind 추가
    bind_line = "        self.memo_entry.bind('<Return>', self.add_memo)"
    if bind_line in text and "self.memo_entry.bind('<Shift-Return>', self.memo_entry_shift_enter_inline)" not in text:
        text = text.replace(
            bind_line,
            bind_line + "\n"
            "        self.memo_entry.bind('<Shift-Return>', self.memo_entry_shift_enter_inline)\n"
            "        self.memo_entry.bind('<Shift-KP_Enter>', self.memo_entry_shift_enter_inline)\n"
            "        self.memo_entry.bind('<KeyRelease>', self.resize_memo_entry_input, add='+')",
            1,
        )
        changed += 1

    return text, changed


def patch_cell_edit_window(text: str) -> tuple[str, int]:
    changed = 0

    # 창 높이를 3줄 입력창에 맞게 조정
    before = text
    text = text.replace("w, h = 330, 120", "w, h = 330, 150", 1)
    if text != before:
        changed += 1

    # Entry 생성부를 Text 생성부로 교체
    entry_pattern = re.compile(
        r"        entry_var = tk\.StringVar\(value=cur_v\)\n"
        r"        entry = tk\.Entry\(edit_win, textvariable=entry_var, font=\('맑은 고딕', 10\)\)\n"
        r"        entry\.pack\(fill='x', padx=15, pady=2, ipady=4\)\n"
        r"        entry\.focus_set\(\)",
        re.M,
    )

    entry_repl = (
        "        text_area = tk.Text(edit_win, height=3, wrap='word', font=('맑은 고딕', 10), "
        "relief='solid', bd=1, undo=True)\n"
        "        text_area.pack(fill='x', padx=15, pady=2)\n"
        "        text_area.insert('1.0', cur_v or '')\n"
        "        text_area.focus_set()"
    )

    text2, n = entry_pattern.subn(entry_repl, text, count=1)
    if n:
        text = text2
        changed += n
    else:
        # 이미 일부 변형된 경우 조금 더 느슨하게 처리
        loose_pattern = re.compile(
            r"        entry_var = tk\.StringVar\(value=cur_v\)\n"
            r"        entry = tk\.Entry\(edit_win,.*?\)\n"
            r"        entry\.pack\(.*?\)\n"
            r"        entry\.focus_set\(\)",
            re.S,
        )
        text2, n = loose_pattern.subn(entry_repl, text, count=1)
        if n:
            text = text2
            changed += n

    # 저장값 추출
    text2 = text.replace("new_v = entry_var.get().strip()", "new_v = text_area.get('1.0', 'end-1c').strip()", 1)
    if text2 != text:
        text = text2
        changed += 1

    # 삭제 처리
    text2 = text.replace("entry_var.set(\"\")", "text_area.delete('1.0', tk.END)", 1)
    if text2 != text:
        text = text2
        changed += 1

    # on_delete 아래에 줄바꿈 함수 삽입
    if "def _mdgo_cell_insert_newline" not in text:
        text2 = re.sub(
            r"(        def on_delete\(\):\n"
            r"            text_area\.delete\('1\.0', tk\.END\)\n"
            r"            on_save\(\)\n)",
            r"\1\n"
            r"        def _mdgo_cell_insert_newline(event=None):\n"
            r"            text_area.insert('insert', chr(10))\n"
            r"            return 'break'\n",
            text,
            count=1,
        )
        if text2 != text:
            text = text2
            changed += 1

    # 기존 Entry bind를 Text bind로 교체
    # 다양한 따옴표/위치 가능성 대응
    replaced_bind = False

    bind_repls = [
        (
            "entry.bind('<Return>', on_save)",
            "text_area.bind('<Return>', on_save)\n        text_area.bind('<KP_Enter>', on_save)\n        text_area.bind('<Shift-Return>', _mdgo_cell_insert_newline)\n        text_area.bind('<Shift-KP_Enter>', _mdgo_cell_insert_newline)"
        ),
        (
            'entry.bind("<Return>", on_save)',
            'text_area.bind("<Return>", on_save)\n        text_area.bind("<KP_Enter>", on_save)\n        text_area.bind("<Shift-Return>", _mdgo_cell_insert_newline)\n        text_area.bind("<Shift-KP_Enter>", _mdgo_cell_insert_newline)'
        ),
    ]

    for old, new in bind_repls:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1
            replaced_bind = True
            break

    # Escape 또는 focus bind 앞에 Return bind가 없는 경우 추가
    if not replaced_bind and "text_area.bind('<Shift-Return>', _mdgo_cell_insert_newline)" not in text:
        anchor = "        btn_f = tk.Frame(edit_win, bg='#ecf0f1')"
        if anchor in text:
            text = text.replace(
                anchor,
                "        text_area.bind('<Return>', on_save)\n"
                "        text_area.bind('<KP_Enter>', on_save)\n"
                "        text_area.bind('<Shift-Return>', _mdgo_cell_insert_newline)\n"
                "        text_area.bind('<Shift-KP_Enter>', _mdgo_cell_insert_newline)\n"
                "        edit_win.bind('<Escape>', lambda e: edit_win.destroy())\n\n"
                + anchor,
                1,
            )
            changed += 1

    # 남아 있는 entry.focus_set/bind 참조 안전 교체
    text = text.replace("entry.focus_set()", "text_area.focus_set()")
    text = text.replace("entry.get().strip()", "text_area.get('1.0', 'end-1c').strip()")

    return text, changed


def main():
    print("==============================================")
    print("Step37 precise multiline input patch")
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

    text = remove_old_step37(text)
    text = insert_inline_class(text)

    text, memo_changes = patch_memo_input(text)
    text, cell_changes = patch_cell_edit_window(text)

    try:
        compile(text, str(DESKTOP), "exec")
        print("[확인] PC 파일 문법 OK")
    except Exception as e:
        print("[경고] PC 파일 문법 확인 실패")
        print(e)

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] Step37 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 메모 입력칸 관련 변경 수: {memo_changes}")
    print(f"- 시간표 입력창 관련 변경 수: {cell_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 하단 메모 입력줄에서 Shift+Enter 시 새 팝업 없이 현재 입력칸에서 줄바꿈")
    print("2. 하단 메모 입력줄은 최대 3줄까지만 확장")
    print("3. 검색 / A+ / A- 버튼은 그대로 보임")
    print("4. 시간표 내 내용 입력 창은 기존 작은 UI 형태를 유지하면서 입력칸만 3줄")
    print("5. 시간표 입력창에서 Enter=저장, Shift+Enter=줄바꿈")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

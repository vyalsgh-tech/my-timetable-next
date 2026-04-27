# tools/step38_fix_memo_input_only_keep_cell.py
# ------------------------------------------------------------
# Step38: 하단 메모 입력줄만 정밀 복구
#
# 현재 상태:
# - 시간표 내 "내용 입력" 창의 줄바꿈은 만족스럽게 작동하므로 절대 수정하지 않음.
# - 하단 메모 입력칸에서 검색/A+/A- 버튼이 사라짐.
# - 하단 메모 입력칸의 placeholder("메모를 입력하세요")가 실제 수정 가능한 텍스트처럼 남아 있고,
#   메모 저장 기능이 정상 작동하지 않음.
#
# 적용 내용:
# 1) 시간표 셀 입력창 관련 코드는 절대 건드리지 않음.
# 2) build_ui() 안의 하단 메모 입력줄 영역만 교체.
# 3) 메모 입력칸은 1줄 시작, Shift+Enter 시 현재 입력칸에서 줄바꿈, 최대 3줄까지만 확장.
# 4) 검색 / A+ / A- 버튼을 기존 위치에 복구.
# 5) Enter = 메모 저장, Shift+Enter = 줄바꿈.
# 6) placeholder는 포커스 시 사라지고, 비어 있으면 다시 표시.
#
# 실행:
#   python tools\step38_fix_memo_input_only_keep_cell.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

INLINE_CLASS = '\n# =========================================================\n# Step38: 하단 메모 입력칸 다중 줄 지원 클래스\n# =========================================================\nclass MdgoInlineTextEntry(tk.Text):\n    """tk.Entry처럼 get()/delete(0, END)/insert(0, text)를 쓸 수 있는 Text 위젯."""\n    def __init__(self, master=None, **kwargs):\n        for key in (\n            "textvariable", "show", "validate", "validatecommand",\n            "invalidcommand", "justify"\n        ):\n            kwargs.pop(key, None)\n        kwargs.setdefault("height", 1)\n        kwargs.setdefault("width", 1)\n        kwargs.setdefault("wrap", "word")\n        kwargs.setdefault("undo", True)\n        super().__init__(master, **kwargs)\n\n    def get(self, *args):\n        if not args:\n            return super().get("1.0", "end-1c")\n        return super().get(*args)\n\n    def delete(self, *args):\n        if len(args) >= 1 and args[0] == 0:\n            return super().delete("1.0", tk.END)\n        return super().delete(*args)\n\n    def insert(self, index, chars, *args):\n        if index == 0:\n            index = "1.0"\n        return super().insert(index, chars, *args)\n# =========================================================\n\n'
MEMO_METHODS = '\n    def get_memo_entry_text(self):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                return self.memo_entry.get("1.0", "end-1c").strip()\n            return self.memo_entry.get().strip()\n        except Exception:\n            return ""\n\n    def clear_memo_entry(self):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.delete("1.0", tk.END)\n            else:\n                self.memo_entry.delete(0, tk.END)\n        except Exception:\n            pass\n\n    def reset_memo_entry_placeholder(self):\n        try:\n            self.clear_memo_entry()\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("1.0", "메모를 입력하세요")\n                self.memo_entry.configure(height=1)\n            else:\n                self.memo_entry.insert(0, "메모를 입력하세요")\n            self.memo_entry.config(fg=\'gray\')\n        except Exception:\n            pass\n\n    def memo_entry_focus_in(self, event=None):\n        try:\n            if self.get_memo_entry_text() == "메모를 입력하세요":\n                self.clear_memo_entry()\n                t = self.themes[self.current_theme_idx]\n                self.memo_entry.config(fg=\'black\' if t[\'name\'] == \'웜 파스텔\' else t[\'cell_fg\'])\n        except Exception:\n            pass\n\n    def memo_entry_focus_out(self, event=None):\n        try:\n            if not self.get_memo_entry_text():\n                self.reset_memo_entry_placeholder()\n        except Exception:\n            pass\n\n    def resize_memo_entry_input(self, event=None):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                raw = self.memo_entry.get("1.0", "end-1c")\n                if raw.strip() == "메모를 입력하세요":\n                    self.memo_entry.configure(height=1)\n                    return None\n                line_count = max(1, raw.count(chr(10)) + 1)\n                self.memo_entry.configure(height=max(1, min(3, line_count)))\n        except Exception:\n            pass\n        return None\n\n    def memo_entry_shift_enter_inline(self, event=None):\n        """하단 메모 입력칸에서 새 팝업 없이 현재 입력칸에 줄바꿈."""\n        try:\n            if self.get_memo_entry_text() == "메모를 입력하세요":\n                self.clear_memo_entry()\n                t = self.themes[self.current_theme_idx]\n                self.memo_entry.config(fg=\'black\' if t[\'name\'] == \'웜 파스텔\' else t[\'cell_fg\'])\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("insert", chr(10))\n                self.resize_memo_entry_input()\n                return "break"\n        except Exception:\n            pass\n        return "break"\n\n    def add_memo(self, ev=None):\n        # Shift+Enter는 저장이 아니라 현재 메모 입력칸 안에서 줄바꿈\n        try:\n            state = int(getattr(ev, "state", 0) or 0)\n        except Exception:\n            state = 0\n        if ev is not None and (state & 0x0001):\n            return self.memo_entry_shift_enter_inline(ev)\n\n        text = self.get_memo_entry_text()\n\n        if text == "메모를 입력하세요" or not text:\n            return "break"\n\n        result = self.create_memo_from_text(text)\n        self.reset_memo_entry_placeholder()\n        return result\n'
MEMO_INPUT_BLOCK = '        self.memo_entry = MdgoInlineTextEntry(\n            self.memo_input_f,\n            font=self.font_title,\n            cursor="xterm",\n            height=1,\n            width=1,\n            wrap="word",\n            bd=1,\n            relief="solid",\n            padx=6,\n            pady=4,\n        )\n        self.memo_entry.pack(side=\'left\', fill=\'x\', expand=True, padx=(0, 6), ipady=2)\n        self.reset_memo_entry_placeholder()\n\n        self.memo_entry.bind(\'<FocusIn>\', self.memo_entry_focus_in)\n        self.memo_entry.bind(\'<FocusOut>\', self.memo_entry_focus_out)\n        self.memo_entry.bind(\'<Return>\', self.add_memo)\n        self.memo_entry.bind(\'<KP_Enter>\', self.add_memo)\n        self.memo_entry.bind(\'<Shift-Return>\', self.memo_entry_shift_enter_inline)\n        self.memo_entry.bind(\'<Shift-KP_Enter>\', self.memo_entry_shift_enter_inline)\n        self.memo_entry.bind(\'<KeyRelease>\', self.resize_memo_entry_input, add=\'+\')\n\n        self.search_btn = tk.Button(self.memo_input_f, text=\'검색\', bd=0, font=self.font_title, cursor=\'hand2\', command=self.search_memo, width=5)\n        self.search_btn.pack(side=\'left\', padx=2)\n\n        self.expand_btn = tk.Button(self.memo_input_f, text=\'A+\', bd=0, font=self.font_title, cursor=\'hand2\', command=self.expand_memo, width=4)\n        self.expand_btn.pack(side=\'left\', padx=1)\n\n        self.shrink_btn = tk.Button(self.memo_input_f, text=\'A-\', bd=0, font=self.font_title, cursor=\'hand2\', command=self.shrink_memo, width=4)\n        self.shrink_btn.pack(side=\'left\', padx=1)\n\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step38_memo_only_{STAMP}{path.suffix}")
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


def replace_inline_class(text: str) -> tuple[str, int]:
    # 기존 Step37/Step38 클래스가 있으면 교체
    start = text.find("class MdgoInlineTextEntry(tk.Text):")
    if start != -1:
        # 클래스 바로 앞 주석 블록까지 포함해서 제거 시도
        block_start = text.rfind("# =========================================================", 0, start)
        if block_start != -1 and "Step3" in text[block_start:start]:
            start = block_start

        candidates = []
        for marker in ["\nclass ", "\ndef ", "\n# =========================================="]:
            pos = text.find(marker, start + 10)
            if pos != -1:
                candidates.append(pos)

        if candidates:
            end = min(candidates)
            return text[:start] + INLINE_CLASS + text[end:], 1

    # 새로 삽입
    pos = text.find("class ModernCalendar")
    if pos != -1:
        return text[:pos] + INLINE_CLASS + text[pos:], 1

    # fallback: import 뒤
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("import ") or line.strip().startswith("from "):
            insert_at = i + 1
    return "\n".join(lines[:insert_at]) + "\n\n" + INLINE_CLASS + "\n".join(lines[insert_at:]) + "\n", 1


def patch_memo_methods(text: str) -> tuple[str, int]:
    changed = 0

    for name in [
        "get_memo_entry_text",
        "clear_memo_entry",
        "reset_memo_entry_placeholder",
        "memo_entry_focus_in",
        "memo_entry_focus_out",
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

    text = text.replace(marker, MEMO_METHODS + "\n\n" + marker, 1)
    changed += 1

    return text, changed


def patch_memo_input_block(text: str) -> tuple[str, int]:
    # build_ui 안에서 memo_input_f 생성 이후부터 memo_list_f 생성 직전까지 교체
    start_anchor = "        self.memo_input_f = tk.Frame(self.memo_frame, cursor=\"arrow\")"
    start = text.find(start_anchor)
    if start == -1:
        # trailing space 버전 대비
        start = text.find("        self.memo_input_f = tk.Frame(self.memo_frame, cursor=\"arrow\") ")
    if start == -1:
        raise RuntimeError("memo_input_f 생성 위치를 찾지 못했습니다.")

    memo_entry_start = text.find("        self.memo_entry =", start)
    if memo_entry_start == -1:
        raise RuntimeError("self.memo_entry 생성 위치를 찾지 못했습니다.")

    memo_list_start = text.find("        self.memo_list_f = tk.Frame(self.memo_frame", memo_entry_start)
    if memo_list_start == -1:
        raise RuntimeError("self.memo_list_f 생성 위치를 찾지 못했습니다.")

    new_text = text[:memo_entry_start] + MEMO_INPUT_BLOCK + text[memo_list_start:]
    return new_text, 1


def clean_obsolete_memo_popup_links(text: str) -> tuple[str, int]:
    changed = 0

    # 하단 메모에서 Shift+Enter가 팝업으로 연결되던 흔적만 현재 입력칸 줄바꿈으로 교체
    before = text
    text = text.replace("self.open_new_memo_multiline_editor", "self.memo_entry_shift_enter_inline")
    if text != before:
        changed += 1

    return text, changed


def main():
    print("==============================================")
    print("Step38 memo input only patch")
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
        text, class_changes = replace_inline_class(text)
        text, method_changes = patch_memo_methods(text)
        text, input_changes = patch_memo_input_block(text)
        text, cleanup_changes = clean_obsolete_memo_popup_links(text)
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
        print("[완료] 하단 메모 입력줄 전용 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 입력 클래스 변경: {class_changes}")
    print(f"- 메모 메서드 변경: {method_changes}")
    print(f"- 메모 입력 UI 블록 변경: {input_changes}")
    print(f"- 팝업 연결 흔적 정리: {cleanup_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 시간표 내 내용 입력창은 그대로 유지되는지")
    print("2. 하단 메모 입력줄 오른쪽에 검색 / A+ / A- 버튼이 보이는지")
    print("3. 하단 메모 입력줄 클릭 시 '메모를 입력하세요'가 사라지는지")
    print("4. 하단 메모 입력줄에서 Shift+Enter 시 현재 입력칸에서 줄바꿈되는지")
    print("5. 하단 메모 입력줄은 최대 3줄까지만 확장되는지")
    print("6. Enter 입력 시 메모가 정상 저장되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

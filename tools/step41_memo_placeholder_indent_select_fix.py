# tools/step41_memo_placeholder_indent_select_fix.py
# ------------------------------------------------------------
# Step41: 메모 placeholder / 줄바꿈 들여쓰기 / 완료 취소선 / 클릭 선택 보정
#
# 수정 내용
# 1) 마우스로 메모 입력창을 다시 클릭했을 때
#    '메모를 입력하세요' 뒤에 커서가 붙는 문제 수정
# 2) 줄바꿈 메모의 둘째 줄 시작 위치를 조금 더 오른쪽으로 이동
#    - 첫 줄의 실제 메모 글자 시작 위치와 맞추기
# 3) 완료 메모에서 줄바꿈 후 빈 들여쓰기 공간에 취소선이 남는 문제 수정
# 4) 줄바꿈 메모의 둘째 줄/셋째 줄 클릭 시에도 해당 메모가 선택되도록
#    들여쓰기 공백에는 취소선 태그를 제외한 선택용 태그를 부여
#
# 주의:
# - 시간표 내 내용 입력창은 현재 만족 상태이므로 건드리지 않음.
# - 메모 수정 팝업 UI도 Step39 상태를 유지함.
#
# 실행:
#   python tools\step41_memo_placeholder_indent_select_fix.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

MEMO_METHODS = '\n    def get_memo_entry_text(self):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                return self.memo_entry.get("1.0", "end-1c").strip()\n            return self.memo_entry.get().strip()\n        except Exception:\n            return ""\n\n    def clear_memo_entry(self):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.delete("1.0", tk.END)\n            else:\n                self.memo_entry.delete(0, tk.END)\n        except Exception:\n            pass\n\n    def is_memo_placeholder_active(self):\n        try:\n            return self.get_memo_entry_text() == "메모를 입력하세요"\n        except Exception:\n            return False\n\n    def memo_entry_begin_real_input(self):\n        """placeholder 상태에서 실제 입력 모드로 전환."""\n        try:\n            if self.is_memo_placeholder_active():\n                self.clear_memo_entry()\n            t = self.themes[self.current_theme_idx]\n            self.memo_entry.config(fg=\'black\' if t[\'name\'] == \'웜 파스텔\' else t[\'cell_fg\'])\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.mark_set("insert", "1.0")\n                self.memo_entry.see("insert")\n            else:\n                self.memo_entry.icursor(0)\n            self.resize_memo_entry_input()\n        except Exception:\n            pass\n\n    def memo_entry_click_guard(self, event=None):\n        """마우스로 placeholder를 클릭했을 때 \'메모를 입력하세요\' 뒤에 커서가 붙는 문제 방지."""\n        try:\n            if self.is_memo_placeholder_active():\n                self.memo_entry_begin_real_input()\n                return "break"\n        except Exception:\n            pass\n        return None\n\n    def memo_entry_keypress_guard(self, event=None):\n        """placeholder가 포커스를 가진 상태에서 글자가 덧붙는 문제 방지."""\n        try:\n            if not self.is_memo_placeholder_active():\n                return None\n\n            keysym = getattr(event, "keysym", "") if event is not None else ""\n            allowed_control = {\n                "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",\n                "Left", "Right", "Up", "Down", "Tab", "Escape",\n                "Caps_Lock", "Num_Lock", "Scroll_Lock"\n            }\n\n            if keysym in allowed_control:\n                return None\n\n            if keysym in ("Return", "KP_Enter"):\n                return "break"\n\n            self.memo_entry_begin_real_input()\n        except Exception:\n            pass\n        return None\n\n    def reset_memo_entry_placeholder(self):\n        try:\n            self.clear_memo_entry()\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("1.0", "메모를 입력하세요")\n                self.memo_entry.configure(height=1)\n                self.memo_entry.mark_set("insert", "1.0")\n                self.memo_entry.see("insert")\n            else:\n                self.memo_entry.insert(0, "메모를 입력하세요")\n                self.memo_entry.icursor(0)\n            self.memo_entry.config(fg=\'gray\')\n        except Exception:\n            pass\n\n    def memo_entry_focus_in(self, event=None):\n        try:\n            if self.is_memo_placeholder_active():\n                self.memo_entry_begin_real_input()\n        except Exception:\n            pass\n\n    def memo_entry_focus_out(self, event=None):\n        try:\n            if not self.get_memo_entry_text():\n                self.reset_memo_entry_placeholder()\n        except Exception:\n            pass\n\n    def resize_memo_entry_input(self, event=None):\n        try:\n            if isinstance(self.memo_entry, tk.Text):\n                raw = self.memo_entry.get("1.0", "end-1c")\n                if raw.strip() == "메모를 입력하세요":\n                    self.memo_entry.configure(height=1)\n                    return None\n                line_count = max(1, raw.count(chr(10)) + 1)\n                self.memo_entry.configure(height=max(1, min(3, line_count)))\n        except Exception:\n            pass\n        return None\n\n    def memo_entry_shift_enter_inline(self, event=None):\n        """하단 메모 입력칸에서 새 팝업 없이 현재 입력칸에 줄바꿈."""\n        try:\n            if self.is_memo_placeholder_active():\n                self.memo_entry_begin_real_input()\n            if isinstance(self.memo_entry, tk.Text):\n                self.memo_entry.insert("insert", chr(10))\n                self.resize_memo_entry_input()\n                return "break"\n        except Exception:\n            pass\n        return "break"\n\n    def add_memo(self, ev=None):\n        # Shift+Enter는 저장이 아니라 현재 메모 입력칸 안에서 줄바꿈\n        try:\n            state = int(getattr(ev, "state", 0) or 0)\n        except Exception:\n            state = 0\n        if ev is not None and (state & 0x0001):\n            return self.memo_entry_shift_enter_inline(ev)\n\n        text = self.get_memo_entry_text()\n\n        if text == "메모를 입력하세요" or not text:\n            return "break"\n\n        result = self.create_memo_from_text(text)\n\n        # 저장 후 placeholder가 실제 입력 텍스트처럼 수정되지 않도록 포커스를 메모 목록으로 이동\n        self.reset_memo_entry_placeholder()\n        try:\n            self.memo_text.focus_set()\n        except Exception:\n            try:\n                self.root.focus_set()\n            except Exception:\n                pass\n        return result\n'
INDENT_METHODS = '\n    def format_memo_list_multiline_text(self, value):\n        """호환용 함수. 실제 들여쓰기는 install_memo_text_insert_indent_patch에서 처리."""\n        text = "" if value is None else str(value)\n        return text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n    def install_memo_text_insert_indent_patch(self):\n        """memo_text.insert에 표시용 줄바꿈 들여쓰기 적용.\n        - 저장 데이터는 건드리지 않음\n        - 둘째 줄 이후의 들여쓰기 공백은 선택/클릭 태그만 주고 취소선 태그는 제외\n        - 완료 메모의 빈 줄/빈 공백에는 취소선을 적용하지 않음\n        """\n        try:\n            if getattr(self.memo_text, "_mdgo_step41_indent_installed", False):\n                return\n\n            original_insert = self.memo_text.insert\n            indent = "        "  # 체크/별표/중요표시 영역까지 고려해 한 칸 더 깊게 정렬\n\n            def _is_strike_tag(tag):\n                name = str(tag).lower()\n                return (\n                    "strike" in name or\n                    "done" in name or\n                    "complete" in name or\n                    "completed" in name or\n                    "finish" in name or\n                    "finished" in name or\n                    "취소" in name or\n                    "완료" in name\n                )\n\n            def _non_strike_tags(tags):\n                return tuple(t for t in tags if not _is_strike_tag(t))\n\n            def _insert(index, chars, *tags):\n                try:\n                    if not isinstance(chars, str):\n                        return original_insert(index, chars, *tags)\n\n                    normalized = chars.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n                    if "\\n" not in normalized:\n                        return original_insert(index, chars, *tags)\n\n                    safe_tags = _non_strike_tags(tags)\n\n                    # 줄바꿈만 들어온 경우: 완료 취소선 태그 없이 줄바꿈만 삽입\n                    if normalized.strip("\\n") == "":\n                        if str(index).lower() in ("end", "tk.end"):\n                            return original_insert(tk.END, normalized, *safe_tags)\n                        return original_insert(index, normalized, *safe_tags)\n\n                    # 끝 개행은 항목 구분용이므로 별도 보존\n                    trailing_count = len(normalized) - len(normalized.rstrip("\\n"))\n                    core = normalized.rstrip("\\n")\n                    parts = core.split("\\n")\n\n                    if str(index).lower() in ("end", "tk.end"):\n                        # 첫 줄\n                        if parts[0]:\n                            original_insert(tk.END, parts[0], *tags)\n\n                        # 둘째 줄 이후\n                        for part in parts[1:]:\n                            original_insert(tk.END, "\\n", *safe_tags)\n\n                            if part.strip():\n                                # 들여쓰기 공백: 클릭/선택 태그는 유지하되 취소선 태그 제거\n                                original_insert(tk.END, indent, *safe_tags)\n                                # 실제 글자에만 원래 태그 적용\n                                original_insert(tk.END, part.lstrip(), *tags)\n                            else:\n                                # 빈 줄이면 취소선/공백 삽입하지 않음\n                                pass\n\n                        if trailing_count:\n                            original_insert(tk.END, "\\n" * trailing_count, *safe_tags)\n                        return None\n\n                    # fallback: end가 아닌 삽입은 들여쓰기만 적용하되 태그는 원래 방식 유지\n                    shown = parts[0]\n                    for part in parts[1:]:\n                        if part.strip():\n                            shown += "\\n" + indent + part.lstrip()\n                        else:\n                            shown += "\\n"\n                    shown += "\\n" * trailing_count\n                    return original_insert(index, shown, *tags)\n\n                except Exception:\n                    return original_insert(index, chars, *tags)\n\n            self.memo_text.insert = _insert\n            self.memo_text._mdgo_step41_indent_installed = True\n\n        except Exception:\n            pass\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step41_memo_fix_{STAMP}{path.suffix}")
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


def patch_placeholder_methods(text: str) -> tuple[str, int]:
    changed = 0

    for name in [
        "get_memo_entry_text",
        "clear_memo_entry",
        "is_memo_placeholder_active",
        "memo_entry_begin_real_input",
        "memo_entry_click_guard",
        "memo_entry_keypress_guard",
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

    # 메모 입력칸 바인딩 보정
    if "self.memo_entry.bind('<Button-1>', self.memo_entry_click_guard" not in text:
        anchor = "        self.memo_entry.bind('<FocusIn>', self.memo_entry_focus_in)"
        if anchor in text:
            text = text.replace(
                anchor,
                "        self.memo_entry.bind('<Button-1>', self.memo_entry_click_guard, add='+')\n" + anchor,
                1,
            )
            changed += 1
        else:
            print("[경고] FocusIn 바인딩 위치를 찾지 못해 Button-1 guard를 자동 추가하지 못했습니다.")

    if "self.memo_entry.bind('<KeyPress>', self.memo_entry_keypress_guard" not in text:
        anchor = "        self.memo_entry.bind('<FocusOut>', self.memo_entry_focus_out)"
        if anchor in text:
            text = text.replace(
                anchor,
                anchor + "\n        self.memo_entry.bind('<KeyPress>', self.memo_entry_keypress_guard, add='+')",
                1,
            )
            changed += 1
        else:
            print("[경고] FocusOut 바인딩 위치를 찾지 못해 KeyPress guard를 자동 추가하지 못했습니다.")

    return text, changed


def patch_indent_methods(text: str) -> tuple[str, int]:
    changed = 0

    for name in [
        "format_memo_list_multiline_text",
        "install_memo_text_insert_indent_patch",
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def refresh_memo_list(self):"
    if marker not in text:
        raise RuntimeError("refresh_memo_list 위치를 찾지 못했습니다.")

    text = text.replace(marker, INDENT_METHODS + "\n\n" + marker, 1)
    changed += 1

    # wrapper 설치 호출이 없으면 memo_text pack 이후에 추가
    if "self.install_memo_text_insert_indent_patch()" not in text:
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
            print("[경고] self.memo_text.pack/grid 위치를 찾지 못했습니다.")

    return text, changed


def main():
    print("==============================================")
    print("Step41 memo placeholder/indent/select fix")
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
        text, placeholder_changes = patch_placeholder_methods(text)
        text, indent_changes = patch_indent_methods(text)
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
        print("[완료] Step41 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- placeholder/메모 입력 관련 변경: {placeholder_changes}")
    print(f"- 줄바꿈 들여쓰기/취소선/클릭 선택 관련 변경: {indent_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 메모 입력창 클릭 시 '메모를 입력하세요' 뒤에 커서가 붙지 않고 바로 비워지는지")
    print("2. 줄바꿈 메모의 둘째 줄 시작 위치가 첫 줄 실제 메모 글자 위치와 맞는지")
    print("3. 완료 메모에서 빈 들여쓰기 공간에 취소선이 남지 않는지")
    print("4. 줄바꿈 메모의 둘째 줄/셋째 줄을 클릭해도 해당 메모가 선택되는지")
    print("5. 시간표 내 내용 입력창은 그대로 잘 작동하는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

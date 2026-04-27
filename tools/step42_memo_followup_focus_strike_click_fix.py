# tools/step42_memo_followup_focus_strike_click_fix.py
# ------------------------------------------------------------
# Step42: 메모 입력 후 연속 입력 / 완료메모 취소선 공백 / 줄바꿈 줄 클릭 선택 수정
#
# 수정 내용
# 1) 메모 입력 후 Enter 저장 시 입력칸이 빈 상태로 포커스 유지
# 2) 완료 메모의 줄바꿈 들여쓰기 공백에는 취소선이 적용되지 않도록 보정
# 3) 줄바꿈 메모의 둘째 줄/셋째 줄에도 첫 줄의 클릭/선택 태그를 복사
# 4) 줄바꿈 둘째 줄 들여쓰기를 조금 더 오른쪽으로 이동
#
# 주의:
# - 시간표 내 내용 입력창은 건드리지 않음.
# - 메모 수정 팝업 UI는 건드리지 않음.
#
# 실행:
#   python tools\step42_memo_followup_focus_strike_click_fix.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

MEMO_METHODS = r'''
    def get_memo_entry_text(self):
        try:
            if isinstance(self.memo_entry, tk.Text):
                return self.memo_entry.get("1.0", "end-1c").strip()
            return self.memo_entry.get().strip()
        except Exception:
            return ""

    def clear_memo_entry(self):
        try:
            if isinstance(self.memo_entry, tk.Text):
                self.memo_entry.delete("1.0", tk.END)
            else:
                self.memo_entry.delete(0, tk.END)
        except Exception:
            pass

    def is_memo_placeholder_active(self):
        try:
            return self.get_memo_entry_text() == "메모를 입력하세요"
        except Exception:
            return False

    def memo_entry_begin_real_input(self):
        try:
            if self.is_memo_placeholder_active():
                self.clear_memo_entry()
            t = self.themes[self.current_theme_idx]
            self.memo_entry.config(fg='black' if t['name'] == '웜 파스텔' else t['cell_fg'])
            if isinstance(self.memo_entry, tk.Text):
                self.memo_entry.mark_set("insert", "1.0")
                self.memo_entry.see("insert")
            else:
                self.memo_entry.icursor(0)
            self.resize_memo_entry_input()
            self.memo_entry.focus_set()
        except Exception:
            pass

    def memo_entry_click_guard(self, event=None):
        try:
            if self.is_memo_placeholder_active():
                self.memo_entry_begin_real_input()
                return "break"
        except Exception:
            pass
        return None

    def memo_entry_keypress_guard(self, event=None):
        try:
            if not self.is_memo_placeholder_active():
                return None

            keysym = getattr(event, "keysym", "") if event is not None else ""
            allowed_control = {
                "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
                "Left", "Right", "Up", "Down", "Tab", "Escape",
                "Caps_Lock", "Num_Lock", "Scroll_Lock"
            }

            if keysym in allowed_control:
                return None

            if keysym in ("Return", "KP_Enter"):
                return "break"

            self.memo_entry_begin_real_input()
        except Exception:
            pass
        return None

    def reset_memo_entry_placeholder(self, keep_focus=False):
        try:
            self.clear_memo_entry()
            if isinstance(self.memo_entry, tk.Text):
                self.memo_entry.insert("1.0", "메모를 입력하세요")
                self.memo_entry.configure(height=1)
                self.memo_entry.mark_set("insert", "1.0")
                self.memo_entry.see("insert")
            else:
                self.memo_entry.insert(0, "메모를 입력하세요")
                self.memo_entry.icursor(0)
            self.memo_entry.config(fg='gray')
            if keep_focus:
                self.memo_entry.focus_set()
        except Exception:
            pass

    def prepare_memo_entry_for_next_input(self):
        try:
            self.clear_memo_entry()
            if isinstance(self.memo_entry, tk.Text):
                self.memo_entry.configure(height=1)
                self.memo_entry.mark_set("insert", "1.0")
                self.memo_entry.see("insert")
            else:
                self.memo_entry.icursor(0)
            t = self.themes[self.current_theme_idx]
            self.memo_entry.config(fg='black' if t['name'] == '웜 파스텔' else t['cell_fg'])
            self.memo_entry.focus_set()
        except Exception:
            pass

    def memo_entry_focus_in(self, event=None):
        try:
            if self.is_memo_placeholder_active():
                self.memo_entry_begin_real_input()
        except Exception:
            pass

    def memo_entry_focus_out(self, event=None):
        try:
            if not self.get_memo_entry_text():
                self.reset_memo_entry_placeholder(keep_focus=False)
        except Exception:
            pass

    def resize_memo_entry_input(self, event=None):
        try:
            if isinstance(self.memo_entry, tk.Text):
                raw = self.memo_entry.get("1.0", "end-1c")
                if raw.strip() == "메모를 입력하세요":
                    self.memo_entry.configure(height=1)
                    return None
                line_count = max(1, raw.count(chr(10)) + 1)
                self.memo_entry.configure(height=max(1, min(3, line_count)))
        except Exception:
            pass
        return None

    def memo_entry_shift_enter_inline(self, event=None):
        try:
            if self.is_memo_placeholder_active():
                self.memo_entry_begin_real_input()
            if isinstance(self.memo_entry, tk.Text):
                self.memo_entry.insert("insert", chr(10))
                self.resize_memo_entry_input()
                return "break"
        except Exception:
            pass
        return "break"

    def add_memo(self, ev=None):
        try:
            state = int(getattr(ev, "state", 0) or 0)
        except Exception:
            state = 0
        if ev is not None and (state & 0x0001):
            return self.memo_entry_shift_enter_inline(ev)

        text = self.get_memo_entry_text()

        if text == "메모를 입력하세요" or not text:
            return "break"

        result = self.create_memo_from_text(text)
        self.prepare_memo_entry_for_next_input()
        return result
'''

TAG_METHODS = r'''
    def format_memo_list_multiline_text(self, value):
        text = "" if value is None else str(value)
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def is_memo_text_strike_tag(self, tag):
        try:
            val = str(self.memo_text.tag_cget(tag, "overstrike")).lower()
            if val in ("1", "true", "yes"):
                return True
        except Exception:
            pass

        name = str(tag).lower()
        return (
            "strike" in name or
            "done" in name or
            "complete" in name or
            "completed" in name or
            "finish" in name or
            "finished" in name or
            "취소" in name or
            "완료" in name
        )

    def install_memo_text_insert_indent_patch(self):
        try:
            if getattr(self.memo_text, "_mdgo_step42_indent_installed", False):
                return

            original_insert = self.memo_text.insert
            indent = "          "

            def _insert(index, chars, *tags):
                try:
                    if not isinstance(chars, str):
                        return original_insert(index, chars, *tags)

                    normalized = chars.replace("\r\n", "\n").replace("\r", "\n")

                    if "\n" not in normalized:
                        return original_insert(index, chars, *tags)

                    safe_tags = tuple(t for t in tags if not self.is_memo_text_strike_tag(t))

                    if normalized.strip("\n") == "":
                        return original_insert(index, normalized, *safe_tags)

                    trailing_count = len(normalized) - len(normalized.rstrip("\n"))
                    core = normalized.rstrip("\n")
                    parts = core.split("\n")

                    if str(index).lower() in ("end", "tk.end"):
                        if parts[0]:
                            original_insert(tk.END, parts[0], *tags)

                        for part in parts[1:]:
                            original_insert(tk.END, "\n", *safe_tags)
                            if part.strip():
                                original_insert(tk.END, indent, *safe_tags)
                                original_insert(tk.END, part.lstrip(), *tags)

                        if trailing_count:
                            original_insert(tk.END, "\n" * trailing_count, *safe_tags)
                        return None

                    shown = parts[0]
                    for part in parts[1:]:
                        if part.strip():
                            shown += "\n" + indent + part.lstrip()
                        else:
                            shown += "\n"
                    shown += "\n" * trailing_count
                    return original_insert(index, shown, *tags)

                except Exception:
                    return original_insert(index, chars, *tags)

            self.memo_text.insert = _insert
            self.memo_text._mdgo_step42_indent_installed = True

        except Exception:
            pass

    def cleanup_memo_text_multiline_tags(self):
        try:
            w = self.memo_text
            old_state = None
            try:
                old_state = w.cget("state")
                w.config(state="normal")
            except Exception:
                pass

            try:
                end_line = int(w.index("end-1c").split(".")[0])
            except Exception:
                end_line = 1

            def first_non_space_pos(line_text):
                return len(line_text) - len(line_text.lstrip())

            def get_ref_tags(prev_line):
                for ln in range(prev_line, 0, -1):
                    txt = w.get(f"{ln}.0", f"{ln}.end")
                    if txt.strip():
                        col = first_non_space_pos(txt)
                        try:
                            return tuple(w.tag_names(f"{ln}.{col}"))
                        except Exception:
                            return tuple()
                return tuple()

            for line_no in range(1, end_line + 1):
                line_text = w.get(f"{line_no}.0", f"{line_no}.end")

                if not line_text:
                    for tag in w.tag_names():
                        if self.is_memo_text_strike_tag(tag):
                            try:
                                w.tag_remove(tag, f"{line_no}.0", f"{line_no}.end")
                            except Exception:
                                pass
                    continue

                leading = first_non_space_pos(line_text)

                if leading > 0:
                    line_start = f"{line_no}.0"
                    content_start = f"{line_no}.{leading}"
                    line_end = f"{line_no}.end"

                    prev_tags = get_ref_tags(line_no - 1)
                    safe_tags = tuple(t for t in prev_tags if not self.is_memo_text_strike_tag(t))
                    strike_tags = tuple(t for t in prev_tags if self.is_memo_text_strike_tag(t))

                    for tag in safe_tags:
                        try:
                            w.tag_add(tag, line_start, line_end)
                        except Exception:
                            pass

                    for tag in w.tag_names():
                        if self.is_memo_text_strike_tag(tag):
                            try:
                                w.tag_remove(tag, line_start, content_start)
                            except Exception:
                                pass

                    if line_text[leading:].strip():
                        for tag in strike_tags:
                            try:
                                w.tag_add(tag, content_start, line_end)
                            except Exception:
                                pass
                    else:
                        for tag in w.tag_names():
                            if self.is_memo_text_strike_tag(tag):
                                try:
                                    w.tag_remove(tag, line_start, line_end)
                                except Exception:
                                    pass

            if old_state:
                try:
                    w.config(state=old_state)
                except Exception:
                    pass

        except Exception:
            pass
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step42_memo_fix_{STAMP}{path.suffix}")
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


def find_function_bounds(text: str, func_name: str):
    start = text.find(f"    def {func_name}(")
    if start == -1:
        return None, None
    candidates = []
    for marker in ["\n    def ", "\n    # =========================================="]:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)
    if not candidates:
        return start, len(text)
    return start, min(candidates)


def patch_memo_methods(text: str):
    changed = 0

    for name in [
        "get_memo_entry_text",
        "clear_memo_entry",
        "is_memo_placeholder_active",
        "memo_entry_begin_real_input",
        "memo_entry_click_guard",
        "memo_entry_keypress_guard",
        "reset_memo_entry_placeholder",
        "prepare_memo_entry_for_next_input",
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

    if "self.memo_entry.bind('<Button-1>', self.memo_entry_click_guard" not in text:
        anchor = "        self.memo_entry.bind('<FocusIn>', self.memo_entry_focus_in)"
        if anchor in text:
            text = text.replace(
                anchor,
                "        self.memo_entry.bind('<Button-1>', self.memo_entry_click_guard)\n" + anchor,
                1,
            )
            changed += 1

    if "self.memo_entry.bind('<KeyPress>', self.memo_entry_keypress_guard" not in text:
        anchor = "        self.memo_entry.bind('<FocusOut>', self.memo_entry_focus_out)"
        if anchor in text:
            text = text.replace(
                anchor,
                anchor + "\n        self.memo_entry.bind('<KeyPress>', self.memo_entry_keypress_guard, add='+')",
                1,
            )
            changed += 1

    return text, changed


def patch_tag_methods(text: str):
    changed = 0

    for name in [
        "format_memo_list_multiline_text",
        "is_memo_text_strike_tag",
        "install_memo_text_insert_indent_patch",
        "cleanup_memo_text_multiline_tags",
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def refresh_memo_list(self):"
    if marker not in text:
        raise RuntimeError("refresh_memo_list 위치를 찾지 못했습니다.")

    text = text.replace(marker, TAG_METHODS + "\n\n" + marker, 1)
    changed += 1

    if "self.install_memo_text_insert_indent_patch()" not in text:
        patterns = [
            r"(        self\.memo_text\.pack\([^\n]*\)\n)",
            r"(        self\.memo_text\.grid\([^\n]*\)\n)",
        ]
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
                break

    call = (
        "        try:\n"
        "            self.cleanup_memo_text_multiline_tags()\n"
        "        except Exception:\n"
        "            pass\n"
    )

    start, end = find_function_bounds(text, "refresh_memo_list")
    if start is None:
        raise RuntimeError("refresh_memo_list 함수 범위를 찾지 못했습니다.")

    refresh_body = text[start:end]
    if "self.cleanup_memo_text_multiline_tags()" not in refresh_body:
        matches = list(re.finditer(r"^        self\.memo_text\.config\(state=['\"]disabled['\"]\)\s*$", refresh_body, flags=re.M))
        if matches:
            m = matches[-1]
            insert_pos = start + m.end()
            text = text[:insert_pos] + "\n" + call + text[insert_pos:]
            changed += 1
        else:
            text = text[:end] + "\n" + call + text[end:]
            changed += 1

    return text, changed


def main():
    print("==============================================")
    print("Step42 memo focus/strike/click fix")
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
        text, memo_changes = patch_memo_methods(text)
        text, tag_changes = patch_tag_methods(text)
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
        print("[완료] Step42 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 메모 입력/연속 입력 관련 변경: {memo_changes}")
    print(f"- 취소선 공백/클릭 선택/들여쓰기 관련 변경: {tag_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 메모 입력 후 Enter 저장 시 입력칸이 빈 상태로 포커스를 유지하는지")
    print("2. 바로 이어 새 메모를 타이핑할 수 있는지")
    print("3. 완료 메모의 빈 들여쓰기 공간에 취소선이 사라졌는지")
    print("4. 줄바꿈 메모의 둘째 줄/셋째 줄 클릭으로도 선택되는지")
    print("5. 시간표 내 내용 입력창과 메모 수정 팝업은 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

# tools/step43_memo_selection_indent_edit_delete_fix_v2.py
# ------------------------------------------------------------
# Step43 v2: 메모 선택/들여쓰기/수정창 삭제버튼 정밀 보정
#
# v1 오류 수정:
# - line 143의 따옴표 SyntaxError 수정
#
# 수정 내용
# 1) 완료 메모까지 선택표시가 번지는 문제 수정
# 2) 줄바꿈 들여쓰기 과다 문제 수정
# 3) 줄바꿈 메모의 둘째 줄/셋째 줄 클릭 선택 문제 수정
# 4) 메모 수정창에 삭제 버튼 추가
#
# 건드리지 않는 것:
# - 시간표 내 내용 입력창
# - 하단 메모 입력줄 줄바꿈/검색/A+/A-
# - 완료 메모 취소선 자체
#
# 실행:
#   python tools\step43_memo_selection_indent_edit_delete_fix_v2.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

ASK_EDIT_METHOD = r"""
    def ask_memo_edit_text_with_delete(self, initialvalue=""):
        # 메모 수정 전용 입력창: 시간표 입력창 UI와 맞추고 삭제 버튼 포함
        result = {"value": None}
        DELETE_SENTINEL = "__MDGO_DELETE_MEMO__"

        win = tk.Toplevel(self.root)
        win.title("내용 입력")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)

        try:
            win.iconbitmap(self.icon_path)
        except Exception:
            pass

        try:
            t = self.get_active_theme()
        except Exception:
            t = {}

        bg = t.get("panel_bg", "#ecf0f1")
        fg = t.get("cell_fg", "#111827")
        input_bg = t.get("input_bg", "#ffffff")

        win.configure(bg=bg)

        frame = tk.Frame(win, bg=bg, padx=14, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="내용을 입력하세요.",
            bg=bg,
            fg=fg,
            font=("맑은 고딕", 9, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        text_box = tk.Text(
            frame,
            height=3,
            width=33,
            wrap="word",
            bg=input_bg,
            fg=fg,
            insertbackground=fg,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("맑은 고딕", 10),
            undo=True,
        )
        text_box.pack(fill="x")
        text_box.insert("1.0", initialvalue or "")
        text_box.focus_set()

        btn_frame = tk.Frame(frame, bg=bg)
        btn_frame.pack(fill="x", pady=(12, 0))

        def on_save(event=None):
            result["value"] = text_box.get("1.0", "end-1c").strip()
            win.destroy()
            return "break"

        def on_delete(event=None):
            result["value"] = DELETE_SENTINEL
            win.destroy()
            return "break"

        def on_cancel(event=None):
            result["value"] = None
            win.destroy()
            return "break"

        def insert_newline(event=None):
            text_box.insert("insert", chr(10))
            return "break"

        def on_return(event=None):
            try:
                if int(getattr(event, "state", 0) or 0) & 0x0001:
                    return insert_newline(event)
            except Exception:
                pass
            return on_save(event)

        tk.Button(
            btn_frame,
            text="저장",
            command=on_save,
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=5,
            cursor="hand2",
            font=("맑은 고딕", 9, "bold"),
        ).pack(side="left")

        tk.Button(
            btn_frame,
            text="삭제",
            command=on_delete,
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=5,
            cursor="hand2",
            font=("맑은 고딕", 9, "bold"),
        ).pack(side="left", padx=(6, 0))

        tk.Button(
            btn_frame,
            text="취소",
            command=on_cancel,
            bg="#7f8c8d",
            fg="white",
            activebackground="#6f7c7d",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=18,
            pady=5,
            cursor="hand2",
            font=("맑은 고딕", 9, "bold"),
        ).pack(side="right")

        text_box.bind("<Shift-Return>", insert_newline)
        text_box.bind("<Shift-KP_Enter>", insert_newline)
        text_box.bind("<Return>", on_return)
        text_box.bind("<KP_Enter>", on_return)
        text_box.bind("<Escape>", on_cancel)
        win.bind("<Escape>", on_cancel)

        try:
            self.root.update_idletasks()
            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 330) // 2)
            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 150) // 2)
            win.geometry(f"330x150+{x}+{y}")
        except Exception:
            win.geometry("330x150")

        self.root.wait_window(win)
        return result["value"]
"""

EDIT_MEMO_METHOD = r"""
    def edit_memo(self):
        if not self.can_view_private_data():
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.selected_memo_indices:
            return

        idx = list(self.selected_memo_indices)[0]
        if hasattr(self, 'last_clicked_idx') and getattr(self, 'last_clicked_idx', None) in self.selected_memo_indices:
            idx = self.last_clicked_idx

        if idx >= len(self.memos_data[u]):
            return

        m = self.memos_data[u][idx]
        clean_text, fg_color, bg_color = self.parse_text_styles(m['text'])

        new_t = self.ask_memo_edit_text_with_delete(initialvalue=clean_text)

        if new_t is None:
            return

        if new_t == "__MDGO_DELETE_MEMO__":
            if USE_SUPABASE and 'id' in m:
                self._async_db_task('DELETE', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}")
            del self.memos_data[u][idx]
            self.selected_memo_indices.clear()
            self.last_clicked_idx = None
            self.push_history()
            self.refresh_memo_list()
            self.save_memos()
            self.update_time_and_date()
            return

        if not new_t.strip():
            return

        save_t = self.build_styled_text(new_t.strip(), fg_color, bg_color)
        m['text'] = save_t

        if USE_SUPABASE and 'id' in m:
            self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"memo_text": save_t})

        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()
"""

TAG_METHODS = r"""
    def format_memo_list_multiline_text(self, value):
        # 호환용 함수. 실제 들여쓰기는 insert wrapper에서 처리.
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
        # 메모 표시용 줄바꿈 들여쓰기.
        # 저장 데이터는 건드리지 않음.
        # 들여쓰기 공백에는 취소선 태그를 적용하지 않음.
        # selected_row 태그를 임의 복사하지 않음.
        try:
            if getattr(self.memo_text, "_mdgo_step43_indent_installed", False):
                return

            original_insert = self.memo_text.insert
            indent = "      "  # Step42보다 줄여 첫 줄 실제 글자 위치에 맞춤

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
                        shown += "\n" + (indent + part.lstrip() if part.strip() else "")
                    shown += "\n" * trailing_count
                    return original_insert(index, shown, *tags)

                except Exception:
                    return original_insert(index, chars, *tags)

            self.memo_text.insert = _insert
            self.memo_text._mdgo_step43_indent_installed = True

        except Exception:
            pass

    def cleanup_memo_text_multiline_tags(self):
        # 완료 메모의 들여쓰기 공백 취소선만 제거.
        # 선택 태그(selected_row)는 여기서 절대 복사하지 않는다.
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

            for line_no in range(1, end_line + 1):
                line_text = w.get(f"{line_no}.0", f"{line_no}.end")
                if not line_text:
                    continue

                leading = len(line_text) - len(line_text.lstrip())
                if leading <= 0:
                    continue

                line_start = f"{line_no}.0"
                content_start = f"{line_no}.{leading}"

                for tag in w.tag_names():
                    if self.is_memo_text_strike_tag(tag):
                        try:
                            w.tag_remove(tag, line_start, content_start)
                        except Exception:
                            pass

            if old_state:
                try:
                    w.config(state=old_state)
                except Exception:
                    pass

        except Exception:
            pass
"""


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step43_v2_memo_fix_{STAMP}{path.suffix}")
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


def patch_edit_memo(text: str):
    changed = 0

    for name in ["ask_memo_edit_text_with_delete", "edit_memo"]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def delete_memo(self):"
    if marker not in text:
        raise RuntimeError("delete_memo 위치를 찾지 못했습니다.")

    text = text.replace(marker, ASK_EDIT_METHOD + "\n" + EDIT_MEMO_METHOD + "\n" + marker, 1)
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
            text2, n = re.subn(pat, r"\1        self.install_memo_text_insert_indent_patch()\n", text, count=1)
            if n:
                text = text2
                changed += n
                break

    return text, changed


def patch_line_map_and_cleanup_call(text: str):
    changed = 0

    start, end = find_function_bounds(text, "refresh_memo_list")
    if start is None:
        raise RuntimeError("refresh_memo_list 함수 범위를 찾지 못했습니다.")

    body = text[start:end]

    if "MDGO_STEP43_CONTINUATION_LINE_MAP" not in body:
        target_double = '            text_end = self.memo_text.index("insert")'
        target_single = "            text_end = self.memo_text.index('insert')"
        target = target_double if target_double in body else target_single if target_single in body else None

        if target:
            insert_block = (
                target + "\n"
                "            # MDGO_STEP43_CONTINUATION_LINE_MAP\n"
                "            try:\n"
                "                _mdgo_start_line = int(str(text_start).split('.')[0])\n"
                "                _mdgo_end_line = int(str(text_end).split('.')[0])\n"
                "                for _mdgo_ln in range(_mdgo_start_line, _mdgo_end_line + 1):\n"
                "                    self.memo_line_map[_mdgo_ln] = i\n"
                "            except Exception:\n"
                "                pass"
            )
            body = body.replace(target, insert_block, 1)
            changed += 1
        else:
            raise RuntimeError("text_end = self.memo_text.index(...) 위치를 찾지 못했습니다.")

    if "self.cleanup_memo_text_multiline_tags()" not in body:
        matches = list(re.finditer(r"^        self\.memo_text\.config\(state=['\"]disabled['\"]\)\s*$", body, flags=re.M))
        call = (
            "        try:\n"
            "            self.cleanup_memo_text_multiline_tags()\n"
            "        except Exception:\n"
            "            pass\n"
        )
        if matches:
            m = matches[-1]
            body = body[:m.end()] + "\n" + call + body[m.end():]
        else:
            body = body.rstrip() + "\n" + call
        changed += 1

    text = text[:start] + body + text[end:]

    return text, changed


def main():
    print("==============================================")
    print("Step43 v2 memo selection/indent/edit-delete fix")
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
        text, tag_changes = patch_tag_methods(text)
        text, map_changes = patch_line_map_and_cleanup_call(text)
        text, edit_changes = patch_edit_memo(text)
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
        print("[완료] Step43 v2 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 태그/들여쓰기 변경: {tag_changes}")
    print(f"- 줄바꿈 라인 선택 매핑 변경: {map_changes}")
    print(f"- 메모 수정창 삭제 버튼 변경: {edit_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 완료 메모까지 선택표시가 번지지 않는지")
    print("2. 줄바꿈 둘째 줄 들여쓰기가 과하게 멀지 않은지")
    print("3. 줄바꿈 메모의 둘째 줄/셋째 줄 클릭으로 선택되는지")
    print("4. 메모 수정창에 저장/삭제/취소 버튼이 있고 삭제가 동작하는지")
    print("5. 시간표 내 내용 입력창과 하단 메모 입력줄은 기존처럼 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

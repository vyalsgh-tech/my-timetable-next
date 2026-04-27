# tools/step43_memo_selection_indent_edit_delete_fix.py
# ------------------------------------------------------------
# Step43: 메모 선택/들여쓰기/수정창 삭제버튼 정밀 보정
#
# 수정 내용
# 1) 완료 메모까지 선택표시가 번지는 문제 수정
#    - selected_row 태그를 줄바꿈 후속 줄에 임의 복사하지 않도록 정리
# 2) 줄바꿈 들여쓰기가 너무 멀어진 문제 수정
#    - 들여쓰기 폭을 Step42보다 줄임
# 3) 줄바꿈 메모의 둘째 줄/셋째 줄 클릭 선택 문제 수정
#    - refresh_memo_list에서 continuation line도 memo_line_map에 등록
# 4) 메모 수정창을 시간표 입력창과 같은 작은 UI로 유지하면서 삭제 버튼 추가
#    - 저장 / 삭제 / 취소
#
# 건드리지 않는 것:
# - 시간표 내 내용 입력창
# - 하단 메모 입력줄 줄바꿈/검색/A+/A-
# - 완료 메모 취소선 자체
#
# 실행:
#   python tools\step43_memo_selection_indent_edit_delete_fix.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

ASK_EDIT_METHOD = '\n    def ask_memo_edit_text_with_delete(self, initialvalue=""):\n        """메모 수정 전용 입력창: 시간표 입력창 UI와 맞추고 삭제 버튼 포함."""\n        result = {"value": None}\n        DELETE_SENTINEL = "__MDGO_DELETE_MEMO__"\n\n        win = tk.Toplevel(self.root)\n        win.title("내용 입력")\n        win.transient(self.root)\n        win.grab_set()\n        win.resizable(False, False)\n\n        try:\n            win.iconbitmap(self.icon_path)\n        except Exception:\n            pass\n\n        try:\n            t = self.get_active_theme()\n        except Exception:\n            t = {}\n\n        bg = t.get("panel_bg", "#ecf0f1")\n        fg = t.get("cell_fg", "#111827")\n        input_bg = t.get("input_bg", "#ffffff")\n\n        win.configure(bg=bg)\n\n        frame = tk.Frame(win, bg=bg, padx=14, pady=12)\n        frame.pack(fill="both", expand=True)\n\n        tk.Label(\n            frame,\n            text="내용을 입력하세요.",\n            bg=bg,\n            fg=fg,\n            font=("맑은 고딕", 9, "bold"),\n            anchor="w",\n        ).pack(fill="x", pady=(0, 6))\n\n        text_box = tk.Text(\n            frame,\n            height=3,\n            width=33,\n            wrap="word",\n            bg=input_bg,\n            fg=fg,\n            insertbackground=fg,\n            relief="solid",\n            bd=1,\n            highlightthickness=0,\n            font=("맑은 고딕", 10),\n            undo=True,\n        )\n        text_box.pack(fill="x")\n        text_box.insert("1.0", initialvalue or "")\n        text_box.focus_set()\n\n        btn_frame = tk.Frame(frame, bg=bg)\n        btn_frame.pack(fill="x", pady=(12, 0))\n\n        def on_save(event=None):\n            result["value"] = text_box.get("1.0", "end-1c").strip()\n            win.destroy()\n            return "break"\n\n        def on_delete(event=None):\n            result["value"] = DELETE_SENTINEL\n            win.destroy()\n            return "break"\n\n        def on_cancel(event=None):\n            result["value"] = None\n            win.destroy()\n            return "break"\n\n        def insert_newline(event=None):\n            text_box.insert("insert", chr(10))\n            return "break"\n\n        def on_return(event=None):\n            try:\n                if int(getattr(event, "state", 0) or 0) & 0x0001:\n                    return insert_newline(event)\n            except Exception:\n                pass\n            return on_save(event)\n\n        tk.Button(\n            btn_frame,\n            text="저장",\n            command=on_save,\n            bg="#27ae60",\n            fg="white",\n            activebackground="#229954",\n            activeforeground="white",\n            relief="flat",\n            bd=0,\n            padx=18,\n            pady=5,\n            cursor="hand2",\n            font=("맑은 고딕", 9, "bold"),\n        ).pack(side="left")\n\n        tk.Button(\n            btn_frame,\n            text="삭제",\n            command=on_delete,\n            bg="#e74c3c",\n            fg="white",\n            activebackground="#c0392b",\n            activeforeground="white",\n            relief="flat",\n            bd=0,\n            padx=18,\n            pady=5,\n            cursor="hand2",\n            font=("맑은 고딕", 9, "bold"),\n        ).pack(side="left", padx=(6, 0))\n\n        tk.Button(\n            btn_frame,\n            text="취소",\n            command=on_cancel,\n            bg="#7f8c8d",\n            fg="white",\n            activebackground="#6f7c7d",\n            activeforeground="white",\n            relief="flat",\n            bd=0,\n            padx=18,\n            pady=5,\n            cursor="hand2",\n            font=("맑은 고딕", 9, "bold"),\n        ).pack(side="right")\n\n        text_box.bind("<Shift-Return>", insert_newline)\n        text_box.bind("<Shift-KP_Enter>", insert_newline)\n        text_box.bind("<Return>", on_return)\n        text_box.bind("<KP_Enter>", on_return)\n        text_box.bind("<Escape>", on_cancel)\n        win.bind("<Escape>", on_cancel)\n\n        try:\n            self.root.update_idletasks()\n            x = self.root.winfo_rootx() + max(30, (self.root.winfo_width() - 330) // 2)\n            y = self.root.winfo_rooty() + max(30, (self.root.winfo_height() - 150) // 2)\n            win.geometry(f"330x150+{x}+{y}")\n        except Exception:\n            win.geometry("330x150")\n\n        self.root.wait_window(win)\n        return result["value"]\n'
EDIT_MEMO_METHOD = '\n    def edit_memo(self):\n        if not self.can_view_private_data():\n            return\n\n        u = getattr(self, \'teacher_var\', tk.StringVar()).get()\n        if not u or not self.selected_memo_indices:\n            return\n\n        idx = list(self.selected_memo_indices)[0]\n        if hasattr(self, \'last_clicked_idx\') and getattr(self, \'last_clicked_idx\', None) in self.selected_memo_indices:\n            idx = self.last_clicked_idx\n\n        if idx >= len(self.memos_data[u]):\n            return\n\n        m = self.memos_data[u][idx]\n        clean_text, fg_color, bg_color = self.parse_text_styles(m[\'text\'])\n\n        new_t = self.ask_memo_edit_text_with_delete(initialvalue=clean_text)\n\n        if new_t is None:\n            return\n\n        if new_t == "__MDGO_DELETE_MEMO__":\n            if USE_SUPABASE and \'id\' in m:\n                self._async_db_task(\'DELETE\', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m[\'id\']}")\n            del self.memos_data[u][idx]\n            self.selected_memo_indices.clear()\n            self.last_clicked_idx = None\n            self.push_history()\n            self.refresh_memo_list()\n            self.save_memos()\n            self.update_time_and_date()\n            return\n\n        if not new_t.strip():\n            return\n\n        save_t = self.build_styled_text(new_t.strip(), fg_color, bg_color)\n        m[\'text\'] = save_t\n\n        if USE_SUPABASE and \'id\' in m:\n            self._async_db_task(\'PATCH\', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m[\'id\']}", HEADERS, {"memo_text": save_t})\n\n        self.push_history()\n        self.refresh_memo_list()\n        self.save_memos()\n        self.update_time_and_date()\n'
TAG_METHODS = '\n    def format_memo_list_multiline_text(self, value):\n        """호환용 함수. 실제 들여쓰기는 insert wrapper에서 처리."""\n        text = "" if value is None else str(value)\n        return text.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n\n    def is_memo_text_strike_tag(self, tag):\n        try:\n            val = str(self.memo_text.tag_cget(tag, "overstrike")).lower()\n            if val in ("1", "true", "yes"):\n                return True\n        except Exception:\n            pass\n\n        name = str(tag).lower()\n        return (\n            "strike" in name or\n            "done" in name or\n            "complete" in name or\n            "completed" in name or\n            "finish" in name or\n            "finished" in name or\n            "취소" in name or\n            "완료" in name\n        )\n\n    def install_memo_text_insert_indent_patch(self):\n        """메모 표시용 줄바꿈 들여쓰기.\n        - 저장 데이터는 건드리지 않음\n        - 들여쓰기 공백에는 취소선 태그를 적용하지 않음\n        - selected_row 태그를 임의 복사하지 않음\n        """\n        try:\n            if getattr(self.memo_text, "_mdgo_step43_indent_installed", False):\n                return\n\n            original_insert = self.memo_text.insert\n            indent = "      "  # Step42보다 줄여 첫 줄 실제 글자 위치에 맞춤\n\n            def _insert(index, chars, *tags):\n                try:\n                    if not isinstance(chars, str):\n                        return original_insert(index, chars, *tags)\n\n                    normalized = chars.replace("\\r\\n", "\\n").replace("\\r", "\\n")\n                    if "\\n" not in normalized:\n                        return original_insert(index, chars, *tags)\n\n                    safe_tags = tuple(t for t in tags if not self.is_memo_text_strike_tag(t))\n\n                    if normalized.strip("\\n") == "":\n                        return original_insert(index, normalized, *safe_tags)\n\n                    trailing_count = len(normalized) - len(normalized.rstrip("\\n"))\n                    core = normalized.rstrip("\\n")\n                    parts = core.split("\\n")\n\n                    if str(index).lower() in ("end", "tk.end"):\n                        if parts[0]:\n                            original_insert(tk.END, parts[0], *tags)\n\n                        for part in parts[1:]:\n                            original_insert(tk.END, "\\n", *safe_tags)\n                            if part.strip():\n                                original_insert(tk.END, indent, *safe_tags)\n                                original_insert(tk.END, part.lstrip(), *tags)\n\n                        if trailing_count:\n                            original_insert(tk.END, "\\n" * trailing_count, *safe_tags)\n                        return None\n\n                    shown = parts[0]\n                    for part in parts[1:]:\n                        shown += "\\n" + (indent + part.lstrip() if part.strip() else "")\n                    shown += "\\n" * trailing_count\n                    return original_insert(index, shown, *tags)\n\n                except Exception:\n                    return original_insert(index, chars, *tags)\n\n            self.memo_text.insert = _insert\n            self.memo_text._mdgo_step43_indent_installed = True\n\n        except Exception:\n            pass\n\n    def cleanup_memo_text_multiline_tags(self):\n        """완료 메모의 들여쓰기 공백 취소선만 제거.\n        선택 태그(selected_row)는 여기서 절대 복사하지 않는다.\n        """\n        try:\n            w = self.memo_text\n            old_state = None\n            try:\n                old_state = w.cget("state")\n                w.config(state="normal")\n            except Exception:\n                pass\n\n            try:\n                end_line = int(w.index("end-1c").split(".")[0])\n            except Exception:\n                end_line = 1\n\n            for line_no in range(1, end_line + 1):\n                line_text = w.get(f"{line_no}.0", f"{line_no}.end")\n                if not line_text:\n                    continue\n\n                leading = len(line_text) - len(line_text.lstrip())\n                if leading <= 0:\n                    continue\n\n                line_start = f"{line_no}.0"\n                content_start = f"{line_no}.{leading}"\n\n                for tag in w.tag_names():\n                    if self.is_memo_text_strike_tag(tag):\n                        try:\n                            w.tag_remove(tag, line_start, content_start)\n                        except Exception:\n                            pass\n\n            if old_state:\n                try:\n                    w.config(state=old_state)\n                except Exception:\n                    pass\n\n        except Exception:\n            pass\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step43_memo_fix_{STAMP}{path.suffix}")
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
        target = "            text_end = self.memo_text.index("insert")"
        if target not in body:
            target = "            text_end = self.memo_text.index('insert')"

        if target in body:
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
    print("Step43 memo selection/indent/edit-delete fix")
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
        print("[완료] Step43 패치 저장")
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

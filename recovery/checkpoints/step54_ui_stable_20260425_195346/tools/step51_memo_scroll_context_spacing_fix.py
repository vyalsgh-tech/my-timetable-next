# tools/step51_memo_scroll_context_spacing_fix.py
# ------------------------------------------------------------
# Step51: 메모 스크롤 유지 / 우클릭 메뉴 닫힘 후 좌클릭 선택 / 아이콘 여백 통일
#
# 수정 내용
# 1) 메모 하단부 클릭 시 refresh_memo_list 때문에 스크롤이 상단으로 튀는 현상 수정
# 2) 우클릭 메뉴가 열린 뒤, 다른 메모를 좌클릭해 메뉴를 닫는 경우 해당 메모가 정상 선택되도록 수정
# 3) 중요표시/완료표시 활성·비활성 아이콘의 폭 차이를 줄임
#
# 실행:
#   python tools\step51_memo_scroll_context_spacing_fix.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

HELPERS = '''
    def refresh_memo_list_keep_view(self):
        # 메모 목록 갱신 시 현재 스크롤 위치를 최대한 유지.
        try:
            yview = self.memo_text.yview()
        except Exception:
            yview = None

        try:
            self.refresh_memo_list()
        finally:
            if yview:
                try:
                    self.memo_text.yview_moveto(yview[0])
                except Exception:
                    pass

    def clear_memo_context_state(self):
        try:
            self._memo_context_menu_active = False
        except Exception:
            pass
        try:
            self._memo_context_menu_widget = None
        except Exception:
            pass

    def run_memo_context_action(self, func, *args, target_indices=None):
        # 우클릭 메뉴 명령은 메뉴를 열 당시 선택된 메모에만 적용.
        try:
            if target_indices is not None:
                self.selected_memo_indices = set(target_indices)
                if self.selected_memo_indices:
                    self.last_clicked_idx = sorted(self.selected_memo_indices)[0]
            return func(*args)
        finally:
            try:
                self._memo_context_menu_active = False
            except Exception:
                pass
            try:
                self._memo_context_menu_widget = None
            except Exception:
                pass
'''

ON_MEMO_CLICK_AND_DRAG_METHODS = '''
    def on_memo_click(self, ev):
        if not self.can_view_private_data():
            return "break"

        # 우클릭 메뉴를 닫기 위해 다른 메모를 좌클릭한 경우:
        # 메뉴는 닫히고, 그 좌클릭은 정상 선택으로 처리되게 한다.
        if getattr(self, "_memo_context_menu_active", False):
            self.clear_memo_context_state()

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return "break"

        try:
            idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
            line, col = map(int, idx_str.split('.'))
        except Exception:
            return "break"

        if line not in self.memo_line_map:
            return "break"

        clicked_idx = self.memo_line_map[line]

        tags = self.memo_text.tag_names(idx_str)
        try:
            char_clicked = self.memo_text.get(f"{line}.{col}", f"{line}.{col+1}")
        except Exception:
            char_clicked = ""

        # 별표 클릭: 중요 표시 변경
        if "important_star" in tags or "unimportant_star" in tags or char_clicked in ["☆", "★", "⭐"]:
            self.toggle_memo_important_by_idx(clicked_idx)
            return "break"

        # 체크 영역 클릭: 완료 표시 변경
        if "checkbox_on" in tags or "checkbox_off" in tags or char_clicked in ["☑", "☐", "✔", "○"] or col <= 2:
            self.toggle_specific_memo_strike(clicked_idx)
            return "break"

        ctrl_pressed = (ev.state & 0x0004) != 0
        shift_pressed = (ev.state & 0x0001) != 0

        if shift_pressed and getattr(self, 'last_clicked_idx', None) is not None:
            start = min(self.last_clicked_idx, clicked_idx)
            end = max(self.last_clicked_idx, clicked_idx)
            if not ctrl_pressed:
                self.selected_memo_indices.clear()
            for i in range(start, end + 1):
                self.selected_memo_indices.add(i)
        elif ctrl_pressed:
            if clicked_idx in self.selected_memo_indices:
                self.selected_memo_indices.remove(clicked_idx)
            else:
                self.selected_memo_indices.add(clicked_idx)
            self.last_clicked_idx = clicked_idx
        else:
            self.selected_memo_indices = {clicked_idx}
            self.last_clicked_idx = clicked_idx

        self.refresh_memo_list_keep_view()
        return "break"

    def on_memo_drag(self, ev):
        # 드래그 선택 복원.
        # 단, 우클릭 메뉴가 떠 있는 동안에는 마우스 이동/드래그로 선택이 흔들리지 않게 차단.
        if not self.can_view_private_data():
            return "break"

        if getattr(self, "_memo_context_menu_active", False):
            return "break"

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return "break"

        try:
            idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
            line, _ = map(int, idx_str.split('.'))
        except Exception:
            return "break"

        if line not in self.memo_line_map:
            return "break"

        current_idx = self.memo_line_map[line]

        if getattr(self, 'last_clicked_idx', None) is not None:
            start = min(self.last_clicked_idx, current_idx)
            end = max(self.last_clicked_idx, current_idx)

            new_selection = set(range(start, end + 1))
            if self.selected_memo_indices != new_selection:
                self.selected_memo_indices = new_selection
                self.refresh_memo_list_keep_view()

        return "break"
'''

ON_MEMO_DOUBLE_CLICK_METHOD = '''
    def on_memo_double_click(self, ev):
        if not self.can_view_private_data():
            return "break"

        if getattr(self, "_memo_context_menu_active", False):
            self.clear_memo_context_state()

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return "break"

        try:
            idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
            line, _ = map(int, idx_str.split('.'))
        except Exception:
            return "break"

        if line not in self.memo_line_map:
            return "break"

        clicked_idx = self.memo_line_map[line]
        self.selected_memo_indices = {clicked_idx}
        self.last_clicked_idx = clicked_idx
        self.refresh_memo_list_keep_view()
        self.edit_memo()
        return "break"
'''

SHOW_MEMO_CONTEXT_MENU_METHOD = '''
    def show_memo_context_menu(self, ev):
        if not self.can_view_private_data():
            return 'break'

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return 'break'

        try:
            idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
            line_str = int(idx_str.split('.')[0])
        except Exception:
            return 'break'

        if line_str not in self.memo_line_map:
            return 'break'

        r_click_idx = self.memo_line_map[line_str]

        # 우클릭한 줄이 현재 선택에 없으면 해당 줄만 선택.
        # 선택된 줄 위에서 우클릭하면 기존 다중 선택을 유지한다.
        if r_click_idx not in self.selected_memo_indices:
            self.selected_memo_indices = {r_click_idx}
            self.last_clicked_idx = r_click_idx
            self.refresh_memo_list_keep_view()

        target_indices = set(self.selected_memo_indices)
        self._memo_context_menu_active = True
        self._memo_context_target_indices = set(target_indices)

        menu = self.create_themed_menu(self.root)
        self._memo_context_menu_widget = menu
        self.add_menu_header(menu, "메모 메뉴")

        menu.add_command(
            label="수정하기",
            command=lambda idxs=target_indices: self.run_memo_context_action(
                self.edit_memo,
                target_indices=idxs
            )
        )
        menu.add_command(
            label="완료 표시",
            command=lambda idxs=target_indices: self.run_memo_context_action(
                self.toggle_memo_strike,
                target_indices=idxs
            )
        )
        menu.add_command(
            label="중요 표시",
            command=lambda idxs=target_indices: self.run_memo_context_action(
                self.toggle_memo_important,
                target_indices=idxs
            )
        )

        sticker_menu = self.build_sticker_menu(
            menu,
            lambda em, idxs=target_indices: self.run_memo_context_action(
                self.add_sticker_to_memo,
                em,
                target_indices=idxs
            )
        )
        menu.add_cascade(label="스티커", menu=sticker_menu)

        color_menu = self.create_themed_menu(menu)
        self.add_menu_header(color_menu, "글자색")
        colors = [
            ("기본색으로", ""),
            ("빨간색", "#e74c3c"),
            ("파란색", "#3498db"),
            ("초록색", "#27ae60"),
            ("보라색", "#9b59b6"),
            ("핑크색", "#ff66b2"),
        ]
        for name, code in colors:
            self.add_color_command(
                color_menu,
                name,
                code,
                lambda c=code, idxs=target_indices: self.run_memo_context_action(
                    self.change_memo_color,
                    c,
                    target_indices=idxs
                )
            )
        menu.add_cascade(label="글자색", menu=color_menu)

        highlight_menu = self.create_themed_menu(menu)
        self.add_menu_header(highlight_menu, "하이라이트")
        h_colors = [
            ("기본색으로", ""),
            ("노란색", "#f1c40f"),
            ("연녹색", "#a2d9ce"),
            ("연하늘", "#aed6f1"),
            ("연분홍", "#f5b7b1"),
            ("회색", "#d5d8dc"),
            ("핑크색", "#ff99cc"),
        ]
        for name, code in h_colors:
            self.add_color_command(
                highlight_menu,
                name,
                code,
                lambda c=code, idxs=target_indices: self.run_memo_context_action(
                    self.change_memo_highlight,
                    c,
                    target_indices=idxs
                )
            )
        menu.add_cascade(label="하이라이트", menu=highlight_menu)

        menu.add_separator()
        menu.add_command(
            label="메모 삭제",
            command=lambda idxs=target_indices: self.run_memo_context_action(
                self.delete_memo,
                target_indices=idxs
            )
        )

        try:
            menu.bind("<Unmap>", lambda e: self.root.after(80, self.clear_memo_context_state), add="+")
            menu.bind("<Destroy>", lambda e: self.root.after(80, self.clear_memo_context_state), add="+")
        except Exception:
            pass

        try:
            menu.tk_popup(ev.x_root, ev.y_root)
        except Exception:
            try:
                menu.post(ev.x_root, ev.y_root)
            except Exception:
                self.clear_memo_context_state()
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
            # 안전장치: 메뉴 닫힘 이벤트를 놓친 경우에만 늦게 해제
            try:
                self.root.after(2000, self.clear_memo_context_state)
            except Exception:
                pass

        return 'break'
'''

TOGGLE_SPECIFIC_MEMO_STRIKE_METHOD = '''
    def toggle_specific_memo_strike(self, idx):
        if not self.can_view_private_data(): 
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if u and idx < len(self.memos_data[u]):
            m = self.memos_data[u][idx]
            m['strike'] = not m.get('strike', False)
            if USE_SUPABASE and 'id' in m: 
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"is_strike": m['strike']})
            self.selected_memo_idx = None 
            self.push_history()
            self.refresh_memo_list_keep_view()
            self.save_memos()
            self.update_time_and_date()
'''

TOGGLE_MEMO_STRIKE_METHOD = '''
    def toggle_memo_strike(self):
        if not self.can_view_private_data(): 
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return

        for idx in list(self.selected_memo_indices):
            m = self.memos_data[u][idx]
            m['strike'] = not m.get('strike', False)
            if USE_SUPABASE and 'id' in m: 
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"is_strike": m['strike']})

        self.selected_memo_indices.clear() 
        self.push_history()
        self.refresh_memo_list_keep_view()
        self.save_memos()
        self.update_time_and_date()
'''

TOGGLE_MEMO_IMPORTANT_METHOD = '''
    def toggle_memo_important(self):
        if not self.can_view_private_data(): 
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return

        for idx in list(self.selected_memo_indices):
            m = self.memos_data[u][idx]
            m['important'] = not m.get('important', False)
            if USE_SUPABASE and 'id' in m: 
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"is_important": m['important']})

        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list_keep_view()
        self.save_memos()
        self.update_time_and_date()
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step51_memo_scroll_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def remove_method(text: str, method_name: str) -> str:
    start = text.find(f"    def {method_name}(")
    if start == -1:
        return text

    candidates = []
    for marker in ["\n    def ", "\n    # ==========================================", "\nif __name__ == \"__main__\":"]:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)

    if not candidates:
        return text

    return text[:start] + text[min(candidates):]


def patch_icons(text: str):
    changed = 0
    replacements = [
        ('            pref = "⭐ " if is_important else "☆ "', '            pref = "★ " if is_important else "☆ "'),
        ("            pref = '⭐ ' if is_important else '☆ '", "            pref = '★ ' if is_important else '☆ '"),
        ('            cb = "✔" if is_strike else "○"', '            cb = "☑" if is_strike else "☐"'),
        ("            cb = '✔' if is_strike else '○'", "            cb = '☑' if is_strike else '☐'"),
    ]

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1

    return text, changed


def patch_methods(text: str):
    changed = 0

    for name in [
        "refresh_memo_list_keep_view",
        "clear_memo_context_state",
        "run_memo_context_action",
        "on_memo_click",
        "on_memo_drag",
        "on_memo_double_click",
        "show_memo_context_menu",
        "toggle_specific_memo_strike",
        "toggle_memo_strike",
        "toggle_memo_important",
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def toggle_memo_important_by_idx(self, idx):"
    if marker not in text:
        raise RuntimeError("toggle_memo_important_by_idx 위치를 찾지 못했습니다.")

    text = text.replace(
        marker,
        HELPERS + "\n" +
        ON_MEMO_CLICK_AND_DRAG_METHODS + "\n" +
        ON_MEMO_DOUBLE_CLICK_METHOD + "\n" +
        SHOW_MEMO_CONTEXT_MENU_METHOD + "\n" +
        TOGGLE_SPECIFIC_MEMO_STRIKE_METHOD + "\n" +
        marker,
        1
    )
    changed += 1

    marker2 = "    def delete_memo(self):"
    if marker2 not in text:
        raise RuntimeError("delete_memo 위치를 찾지 못했습니다.")

    text = text.replace(
        marker2,
        TOGGLE_MEMO_STRIKE_METHOD + "\n" + TOGGLE_MEMO_IMPORTANT_METHOD + "\n" + marker2,
        1
    )
    changed += 1

    return text, changed


def main():
    print("==============================================")
    print("Step51 memo scroll/context/spacing fix")
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
        text, c1 = patch_icons(text)
        text, c2 = patch_methods(text)
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
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] Step51 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 중요/완료 아이콘 폭 보정: {c1}")
    print(f"- 스크롤 유지/우클릭 메뉴 닫힘/선택 처리 보정: {c2}")
    print()
    print("실행:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 메모 하단부 클릭 시 스크롤이 상단으로 튀지 않는지")
    print("2. 우클릭 메뉴를 닫기 위해 다른 메모를 좌클릭하면 그 메모가 선택되는지")
    print("3. 우클릭 메뉴가 열린 동안 마우스 이동/드래그로 선택이 흔들리지 않는지")
    print("4. 중요표시 활성/비활성, 완료표시 활성/비활성 간 여백 차이가 줄었는지")
    print("5. 별표/체크/Ctrl/Shift/드래그 선택 기능은 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

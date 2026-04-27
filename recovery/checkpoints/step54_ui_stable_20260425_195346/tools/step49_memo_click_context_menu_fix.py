# tools/step49_memo_click_context_menu_fix.py
# ------------------------------------------------------------
# Step49: 메모 클릭 동작 단순화 + 우클릭 메뉴 선택 흔들림 수정
#
# 수정 내용
# 1) 메모 줄 좌클릭 1회 = 해당 메모 선택만 수행
#    - 별표 클릭으로 중요표시 토글 삭제
#    - 체크 영역 클릭으로 완료표시 토글 삭제
#    - Ctrl/Shift 다중선택, 드래그 선택 삭제
#
# 2) 메모 줄 더블클릭 = 수정만 수행
#
# 3) 우클릭 메뉴가 열린 상태에서 마우스를 움직일 때
#    다른 메모로 선택이 이동하는 현상 차단
#
# 4) 우클릭 메뉴 명령은 메뉴를 열 당시의 선택 메모에만 적용
#    - 하이라이트 > 기본색으로 초기화 문제 보정
#
# 건드리지 않는 것:
# - 우클릭 메뉴 안의 완료 표시 / 중요 표시 기능 자체는 유지
# - 취소선 표시 로직은 유지
# - 메모 줄바꿈/수정창/하단 입력줄은 유지
#
# 실행:
#   python tools\step49_memo_click_context_menu_fix.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

CONTEXT_HELPERS = '''
    def clear_memo_context_state(self):
        try:
            self._memo_context_menu_active = False
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
'''

ON_MEMO_CLICK_METHOD = '''
    def on_memo_click(self, ev):
        # 좌클릭 1회는 선택만 수행.
        # 체크/별표/드래그/다중선택 등의 부가 동작은 제거한다.
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

        clicked_idx = self.memo_line_map[line]
        self.selected_memo_indices = {clicked_idx}
        self.last_clicked_idx = clicked_idx

        self.refresh_memo_list()
        return "break"

    def on_memo_drag(self, ev):
        # 드래그 선택 제거. 메뉴 이동/마우스 이동 중 선택 흔들림 방지.
        return "break"
'''

ON_MEMO_DOUBLE_CLICK_METHOD = '''
    def on_memo_double_click(self, ev):
        # 더블클릭은 선택 후 수정만 수행.
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

        clicked_idx = self.memo_line_map[line]
        self.selected_memo_indices = {clicked_idx}
        self.last_clicked_idx = clicked_idx
        self.refresh_memo_list()
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
        # 이미 선택된 줄이면 기존 선택을 유지하여 여러 메모 메뉴 작업도 가능하게 둔다.
        if r_click_idx not in self.selected_memo_indices:
            self.selected_memo_indices = {r_click_idx}
            self.last_clicked_idx = r_click_idx
            self.refresh_memo_list()

        target_indices = set(self.selected_memo_indices)
        self._memo_context_menu_active = True
        self._memo_context_target_indices = set(target_indices)

        menu = self.create_themed_menu(self.root)
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
            menu.bind("<Unmap>", lambda e: self.root.after(200, self.clear_memo_context_state), add="+")
            menu.bind("<Destroy>", lambda e: self.root.after(200, self.clear_memo_context_state), add="+")
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
            # 메뉴 명령 실행 직후까지는 target_indices가 필요하므로 살짝 늦게 해제
            try:
                self.root.after(1000, self.clear_memo_context_state)
            except Exception:
                self.clear_memo_context_state()

        return 'break'
'''

CHANGE_MEMO_COLOR_METHOD = '''
    def change_memo_color(self, color):
        if not self.can_view_private_data():
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u:
            return

        target_indices = list(self.selected_memo_indices)
        if not target_indices and getattr(self, "_memo_context_target_indices", None):
            target_indices = list(self._memo_context_target_indices)

        for idx in target_indices:
            if idx >= len(self.memos_data.get(u, [])):
                continue

            m = self.memos_data[u][idx]
            clean_text, old_fg, bg = self.parse_text_styles(m.get('text', ''))

            # 기본색으로 선택한 경우 글자색 태그만 완전히 제거
            fg = None if not color else color

            new_t = self.build_styled_text(clean_text, fg, bg)
            m['text'] = new_t

            if USE_SUPABASE and 'id' in m:
                self._async_db_task(
                    'PATCH',
                    f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}",
                    HEADERS,
                    {"memo_text": new_t}
                )

        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()
'''

CHANGE_MEMO_HIGHLIGHT_METHOD = '''
    def change_memo_highlight(self, bg_color):
        if not self.can_view_private_data():
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u:
            return

        target_indices = list(self.selected_memo_indices)
        if not target_indices and getattr(self, "_memo_context_target_indices", None):
            target_indices = list(self._memo_context_target_indices)

        for idx in target_indices:
            if idx >= len(self.memos_data.get(u, [])):
                continue

            m = self.memos_data[u][idx]
            clean_text, fg, old_bg = self.parse_text_styles(m.get('text', ''))

            # 기본색으로 선택한 경우 하이라이트 태그만 완전히 제거
            bg = None if not bg_color else bg_color

            new_t = self.build_styled_text(clean_text, fg, bg)
            m['text'] = new_t

            if USE_SUPABASE and 'id' in m:
                self._async_db_task(
                    'PATCH',
                    f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}",
                    HEADERS,
                    {"memo_text": new_t}
                )

        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step49_memo_click_{STAMP}{path.suffix}")
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


def patch_bindings(text: str):
    changed = 0

    old = '        self.memo_text.bind("<B1-Motion>", self.on_memo_drag) '
    new = '        self.memo_text.bind("<B1-Motion>", lambda e: "break") '
    if old in text:
        text = text.replace(old, new, 1)
        changed += 1

    old2 = '        self.memo_text.bind("<B1-Motion>", self.on_memo_drag)'
    new2 = '        self.memo_text.bind("<B1-Motion>", lambda e: "break")'
    if old2 in text:
        text = text.replace(old2, new2, 1)
        changed += 1

    return text, changed


def patch_methods(text: str):
    changed = 0

    for name in [
        "clear_memo_context_state",
        "run_memo_context_action",
        "on_memo_click",
        "on_memo_drag",
        "on_memo_double_click",
        "show_memo_context_menu",
        "change_memo_color",
        "change_memo_highlight",
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def toggle_specific_memo_strike(self, idx):"
    if marker not in text:
        raise RuntimeError("toggle_specific_memo_strike 위치를 찾지 못했습니다.")

    text = text.replace(
        marker,
        CONTEXT_HELPERS + "\n" + ON_MEMO_CLICK_METHOD + "\n" + ON_MEMO_DOUBLE_CLICK_METHOD + "\n" + SHOW_MEMO_CONTEXT_MENU_METHOD + "\n" + marker,
        1
    )
    changed += 1

    marker2 = "    def edit_memo(self):"
    if marker2 not in text:
        raise RuntimeError("edit_memo 위치를 찾지 못했습니다.")

    text = text.replace(
        marker2,
        CHANGE_MEMO_COLOR_METHOD + "\n" + CHANGE_MEMO_HIGHLIGHT_METHOD + "\n" + marker2,
        1
    )
    changed += 1

    return text, changed


def main():
    print("==============================================")
    print("Step49 memo click/context menu fix")
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
        text, c1 = patch_bindings(text)
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
        print("[완료] Step49 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 메모 드래그 바인딩 제거: {c1}")
    print(f"- 메모 클릭/우클릭/색상 메서드 보정: {c2}")
    print()
    print("실행:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 메모 줄 좌클릭 1회는 선택만 되는지")
    print("2. 별표/체크 영역을 좌클릭해도 중요/완료가 바뀌지 않는지")
    print("3. 메모 줄 더블클릭은 수정만 실행되는지")
    print("4. 우클릭 메뉴가 열린 상태에서 마우스를 움직여도 다른 메모로 선택이 이동하지 않는지")
    print("5. 하이라이트 > 기본색으로 선택 시 해당 메모의 하이라이트가 취소되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

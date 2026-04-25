# tools/step52_memo_context_scroll_highlight_fix.py
# ------------------------------------------------------------
# Step52: 메모 우클릭 잠금 / 스크롤 유지 / 하이라이트 공백 제거 / 아이콘 원복
#
# 수정 내용
# 1) Step51의 아이콘 변경 취소
#    - 중요표시: ★/☆ -> 원래대로 ⭐/☆
#    - 완료표시: ☑/☐ -> 원래대로 ✔/○
#
# 2) 우클릭 메뉴가 열린 동안 마우스 이동/드래그로 다른 메모가 선택되는 현상 재수정
#    - 메뉴가 닫혔다는 이벤트만으로 잠금 해제하지 않음
#    - 메모 영역을 실제로 좌클릭하면 그때 잠금 해제 후 해당 메모 선택
#
# 3) 글자색/하이라이트 적용 후 메모 스크롤이 상단으로 튀는 현상 수정
#    - 색상 변경 후 refresh_memo_list_keep_view 사용
#
# 4) 하이라이트가 빈 줄/들여쓰기/줄 끝 공백까지 칠해지는 문제 수정
#    - style_* 배경 태그에서 leading space, empty line, newline 부분 제거
#
# 실행:
#   python tools\step52_memo_context_scroll_highlight_fix.py
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
            self.clear_memo_context_state()

    def cleanup_memo_style_blank_areas(self):
        # 하이라이트/글자색 style tag가 빈 줄, 줄 앞 들여쓰기, 줄 끝 newline까지 칠하는 문제 보정.
        try:
            w = self.memo_text
            old_state = None
            try:
                old_state = w.cget("state")
                w.config(state="normal")
            except Exception:
                pass

            style_tags = []
            for tag in w.tag_names():
                if str(tag).startswith("style_"):
                    try:
                        bg = w.tag_cget(tag, "background")
                    except Exception:
                        bg = ""
                    if bg:
                        style_tags.append(tag)

            for tag in style_tags:
                ranges = list(w.tag_ranges(tag))
                pairs = []
                for i in range(0, len(ranges), 2):
                    try:
                        pairs.append((str(ranges[i]), str(ranges[i + 1])))
                    except Exception:
                        pass

                for start, end in pairs:
                    try:
                        start_line = int(start.split(".")[0])
                        end_line = int(end.split(".")[0])
                    except Exception:
                        continue

                    for line_no in range(start_line, end_line + 1):
                        line_start = f"{line_no}.0"
                        line_end = f"{line_no}.end"

                        try:
                            line_text = w.get(line_start, line_end)
                        except Exception:
                            continue

                        # 완전히 빈 줄: style tag 전체 제거
                        if not line_text.strip():
                            try:
                                w.tag_remove(tag, line_start, f"{line_no + 1}.0")
                            except Exception:
                                try:
                                    w.tag_remove(tag, line_start, line_end)
                                except Exception:
                                    pass
                            continue

                        leading = len(line_text) - len(line_text.lstrip())
                        trailing = len(line_text.rstrip())
                        if leading > 0:
                            try:
                                w.tag_remove(tag, line_start, f"{line_no}.{leading}")
                            except Exception:
                                pass

                        # 줄 끝 공백 및 newline에는 배경색 제거
                        try:
                            w.tag_remove(tag, f"{line_no}.{trailing}", f"{line_no + 1}.0")
                        except Exception:
                            try:
                                w.tag_remove(tag, f"{line_no}.{trailing}", line_end)
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

ON_MEMO_CLICK_AND_DRAG_METHODS = '''
    def on_memo_click(self, ev):
        if not self.can_view_private_data():
            return "break"

        # 우클릭 메뉴를 닫기 위해 메모 영역을 좌클릭한 경우:
        # 이 좌클릭 자체는 정상 선택으로 처리한다.
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

        # 원래 기능 유지: 별표 클릭으로 중요 표시 변경
        if "important_star" in tags or "unimportant_star" in tags or char_clicked in ["☆", "⭐", "★"]:
            self.toggle_memo_important_by_idx(clicked_idx)
            return "break"

        # 원래 기능 유지: 체크 영역 클릭으로 완료 표시 변경
        if "checkbox_on" in tags or "checkbox_off" in tags or char_clicked in ["✔", "○", "☑", "☐"] or col <= 2:
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
        # 우클릭 메뉴가 떠 있는 동안에는 마우스 이동/드래그로 선택이 흔들리지 않게 차단.
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

        # 중요:
        # 메뉴 Unmap/Destroy에서 바로 clear하지 않는다.
        # 서브메뉴 이동 중 Unmap 이벤트가 발생하면 잠금이 풀려 선택이 흔들리기 때문이다.
        # 실제 메모 좌클릭 또는 메뉴 명령 실행 시 clear한다.
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
            # 비정상 종료 안전장치만 길게 둔다.
            try:
                self.root.after(30000, self.clear_memo_context_state)
            except Exception:
                pass

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
        self.refresh_memo_list_keep_view()
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
        self.refresh_memo_list_keep_view()
        self.save_memos()
        self.update_time_and_date()
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step52_context_highlight_{STAMP}{path.suffix}")
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
        ('            pref = "★ " if is_important else "☆ "', '            pref = "⭐ " if is_important else "☆ "'),
        ("            pref = '★ ' if is_important else '☆ '", "            pref = '⭐ ' if is_important else '☆ '"),
        ('            cb = "☑" if is_strike else "☐"', '            cb = "✔" if is_strike else "○"'),
        ("            cb = '☑' if is_strike else '☐'", "            cb = '✔' if is_strike else '○'"),
    ]

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1

    return text, changed


def patch_refresh_cleanup_call(text: str):
    changed = 0

    # refresh_memo_list 끝부분에서 selected_row raise 전에 style blank cleanup 실행
    target = '        self.memo_text.tag_raise("selected_row")\n        self.memo_text.config(state=\'disabled\')'
    insert = '''        try:
            self.cleanup_memo_style_blank_areas()
        except Exception:
            pass

        self.memo_text.tag_raise("selected_row")
        self.memo_text.config(state='disabled')'''
    if target in text and "self.cleanup_memo_style_blank_areas()" not in text[text.find("    def refresh_memo_list("): text.find("    def refresh_memo_list(")+7000]:
        text = text.replace(target, insert, 1)
        changed += 1

    return text, changed


def patch_methods(text: str):
    changed = 0

    for name in [
        "refresh_memo_list_keep_view",
        "clear_memo_context_state",
        "run_memo_context_action",
        "cleanup_memo_style_blank_areas",
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

    marker = "    def toggle_memo_important_by_idx(self, idx):"
    if marker not in text:
        raise RuntimeError("toggle_memo_important_by_idx 위치를 찾지 못했습니다.")

    text = text.replace(
        marker,
        HELPERS + "\n" +
        ON_MEMO_CLICK_AND_DRAG_METHODS + "\n" +
        ON_MEMO_DOUBLE_CLICK_METHOD + "\n" +
        SHOW_MEMO_CONTEXT_MENU_METHOD + "\n" +
        marker,
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
    print("Step52 memo context/scroll/highlight fix")
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
        text, c3 = patch_refresh_cleanup_call(text)
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
        print("[완료] Step52 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 중요/완료 아이콘 원복: {c1}")
    print(f"- 우클릭 잠금/색상 스크롤 유지/하이라이트 정리 메서드: {c2}")
    print(f"- refresh_memo_list 하이라이트 정리 호출: {c3}")
    print()
    print("실행:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 중요표시가 다시 ⭐/☆, 완료표시가 다시 ✔/○로 보이는지")
    print("2. 우클릭 메뉴가 열린 동안 마우스 이동/드래그로 선택이 흔들리지 않는지")
    print("3. 우클릭 메뉴를 닫기 위해 다른 메모를 좌클릭하면 그 메모가 선택되는지")
    print("4. 글자색/하이라이트 적용 후 스크롤이 상단으로 튀지 않는지")
    print("5. 하이라이트가 글자 부분에만 적용되고 빈 줄/들여쓰기/줄 끝 공백에는 적용되지 않는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

# tools/step53_memo_highlight_menu_drag_smooth_fix.py
# ------------------------------------------------------------
# Step53: 하이라이트/우클릭 메뉴/창 이동 최종 보정
#
# 실행:
#   python tools\step53_memo_highlight_menu_drag_smooth_fix.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

WINDOW_DRAG_METHODS = '''
    def click_window(self, ev):
        if not getattr(self, 'is_locked', False):
            try:
                self._drag_start_x_root = ev.x_root
                self._drag_start_y_root = ev.y_root
                self._drag_root_start_x = self.root.winfo_x()
                self._drag_root_start_y = self.root.winfo_y()
            except Exception:
                self._offset_x = ev.x
                self._offset_y = ev.y

    def drag_window(self, ev):
        if getattr(self, 'is_locked', False):
            return
        try:
            dx = ev.x_root - self._drag_start_x_root
            dy = ev.y_root - self._drag_start_y_root
            new_x = self._drag_root_start_x + dx
            new_y = self._drag_root_start_y + dy
            self.root.geometry(f"+{new_x}+{new_y}")
        except Exception:
            try:
                self.root.geometry(f"+{self.root.winfo_x() - self._offset_x + ev.x}+{self.root.winfo_y() - self._offset_y + ev.y}")
            except Exception:
                pass
'''

HELPERS = '''
    def refresh_memo_list_keep_view(self):
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

    def raise_memo_style_background_tags(self):
        try:
            w = self.memo_text
            try:
                w.tag_raise('selected_row')
            except Exception:
                pass
            for tag in w.tag_names():
                if str(tag).startswith('style_'):
                    try:
                        bg = w.tag_cget(tag, 'background')
                    except Exception:
                        bg = ''
                    if bg:
                        try:
                            w.tag_raise(tag)
                        except Exception:
                            pass
            try:
                w.tag_raise('search_highlight')
            except Exception:
                pass
        except Exception:
            pass

    def clear_memo_context_state(self):
        menu = getattr(self, '_memo_context_menu_widget', None)
        try:
            if menu is not None:
                try:
                    menu.unpost()
                except Exception:
                    pass
                try:
                    menu.grab_release()
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self._memo_context_menu_active = False
        except Exception:
            pass
        try:
            self._memo_context_menu_widget = None
        except Exception:
            pass

    def run_memo_context_action(self, func, *args, target_indices=None):
        try:
            if target_indices is not None:
                self.selected_memo_indices = set(target_indices)
                if self.selected_memo_indices:
                    self.last_clicked_idx = sorted(self.selected_memo_indices)[0]
            return func(*args)
        finally:
            self.clear_memo_context_state()

    def on_global_left_click_while_memo_menu(self, ev):
        if not getattr(self, '_memo_context_menu_active', False):
            return None
        try:
            w = self.memo_text
            mx = ev.x_root - w.winfo_rootx()
            my = ev.y_root - w.winfo_rooty()
            if mx < 0 or my < 0 or mx > w.winfo_width() or my > w.winfo_height():
                return None
            self.clear_memo_context_state()
            class _Ev:
                pass
            fake = _Ev()
            fake.x = mx
            fake.y = my
            fake.x_root = ev.x_root
            fake.y_root = ev.y_root
            fake.state = getattr(ev, 'state', 0)
            self.on_memo_click(fake)
            return 'break'
        except Exception:
            return None

    def ensure_memo_context_global_bind(self):
        if getattr(self, '_memo_context_global_bind_installed', False):
            return
        try:
            self.root.bind_all('<Button-1>', self.on_global_left_click_while_memo_menu, add='+')
            self._memo_context_global_bind_installed = True
        except Exception:
            pass

    def cleanup_memo_style_blank_areas(self):
        try:
            w = self.memo_text
            old_state = None
            try:
                old_state = w.cget('state')
                w.config(state='normal')
            except Exception:
                pass
            bg_style_tags = []
            for tag in w.tag_names():
                if str(tag).startswith('style_'):
                    try:
                        bg = w.tag_cget(tag, 'background')
                    except Exception:
                        bg = ''
                    if bg:
                        bg_style_tags.append(tag)
            for tag in bg_style_tags:
                ranges = list(w.tag_ranges(tag))
                pairs = []
                for i in range(0, len(ranges), 2):
                    try:
                        pairs.append((str(ranges[i]), str(ranges[i+1])))
                    except Exception:
                        pass
                for start, end in pairs:
                    try:
                        start_line = int(start.split('.')[0])
                        end_line = int(end.split('.')[0])
                    except Exception:
                        continue
                    for line_no in range(start_line, end_line + 1):
                        line_start = f'{line_no}.0'
                        line_end = f'{line_no}.end'
                        try:
                            line_text = w.get(line_start, line_end)
                        except Exception:
                            continue
                        if not line_text.strip():
                            try:
                                w.tag_remove(tag, line_start, f'{line_no + 1}.0')
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
                                w.tag_remove(tag, line_start, f'{line_no}.{leading}')
                            except Exception:
                                pass
                        if trailing < len(line_text):
                            try:
                                w.tag_remove(tag, f'{line_no}.{trailing}', f'{line_no + 1}.0')
                            except Exception:
                                try:
                                    w.tag_remove(tag, f'{line_no}.{trailing}', line_end)
                                except Exception:
                                    pass
                        else:
                            try:
                                w.tag_remove(tag, line_end, f'{line_no + 1}.0')
                            except Exception:
                                pass
            self.raise_memo_style_background_tags()
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
            return 'break'
        if getattr(self, '_memo_context_menu_active', False):
            self.clear_memo_context_state()
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return 'break'
        try:
            idx_str = self.memo_text.index(f'@{ev.x},{ev.y}')
            line, col = map(int, idx_str.split('.'))
        except Exception:
            return 'break'
        if line not in self.memo_line_map:
            return 'break'
        clicked_idx = self.memo_line_map[line]
        tags = self.memo_text.tag_names(idx_str)
        try:
            char_clicked = self.memo_text.get(f'{line}.{col}', f'{line}.{col+1}')
        except Exception:
            char_clicked = ''
        if 'important_star' in tags or 'unimportant_star' in tags or char_clicked in ['☆', '⭐', '★']:
            self.toggle_memo_important_by_idx(clicked_idx)
            return 'break'
        if 'checkbox_on' in tags or 'checkbox_off' in tags or char_clicked in ['✔', '○', '☑', '☐'] or col <= 2:
            self.toggle_specific_memo_strike(clicked_idx)
            return 'break'
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
        return 'break'

    def on_memo_drag(self, ev):
        if not self.can_view_private_data():
            return 'break'
        if getattr(self, '_memo_context_menu_active', False):
            return 'break'
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return 'break'
        try:
            idx_str = self.memo_text.index(f'@{ev.x},{ev.y}')
            line, _ = map(int, idx_str.split('.'))
        except Exception:
            return 'break'
        if line not in self.memo_line_map:
            return 'break'
        current_idx = self.memo_line_map[line]
        if getattr(self, 'last_clicked_idx', None) is not None:
            start = min(self.last_clicked_idx, current_idx)
            end = max(self.last_clicked_idx, current_idx)
            new_selection = set(range(start, end + 1))
            if self.selected_memo_indices != new_selection:
                self.selected_memo_indices = new_selection
                self.refresh_memo_list_keep_view()
        return 'break'
'''

ON_MEMO_DOUBLE_CLICK_METHOD = '''
    def on_memo_double_click(self, ev):
        if not self.can_view_private_data():
            return 'break'
        if getattr(self, '_memo_context_menu_active', False):
            self.clear_memo_context_state()
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return 'break'
        try:
            idx_str = self.memo_text.index(f'@{ev.x},{ev.y}')
            line, _ = map(int, idx_str.split('.'))
        except Exception:
            return 'break'
        if line not in self.memo_line_map:
            return 'break'
        clicked_idx = self.memo_line_map[line]
        self.selected_memo_indices = {clicked_idx}
        self.last_clicked_idx = clicked_idx
        self.refresh_memo_list_keep_view()
        self.edit_memo()
        return 'break'
'''

SHOW_MEMO_CONTEXT_MENU_METHOD = '''
    def show_memo_context_menu(self, ev):
        if not self.can_view_private_data():
            return 'break'
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u):
            return 'break'
        try:
            idx_str = self.memo_text.index(f'@{ev.x},{ev.y}')
            line_str = int(idx_str.split('.')[0])
        except Exception:
            return 'break'
        if line_str not in self.memo_line_map:
            return 'break'
        r_click_idx = self.memo_line_map[line_str]
        if r_click_idx not in self.selected_memo_indices:
            self.selected_memo_indices = {r_click_idx}
            self.last_clicked_idx = r_click_idx
            self.refresh_memo_list_keep_view()
        target_indices = set(self.selected_memo_indices)
        self._memo_context_menu_active = True
        self._memo_context_target_indices = set(target_indices)
        self.ensure_memo_context_global_bind()
        menu = self.create_themed_menu(self.root)
        self._memo_context_menu_widget = menu
        self.add_menu_header(menu, '메모 메뉴')
        menu.add_command(label='수정하기', command=lambda idxs=target_indices: self.run_memo_context_action(self.edit_memo, target_indices=idxs))
        menu.add_command(label='완료 표시', command=lambda idxs=target_indices: self.run_memo_context_action(self.toggle_memo_strike, target_indices=idxs))
        menu.add_command(label='중요 표시', command=lambda idxs=target_indices: self.run_memo_context_action(self.toggle_memo_important, target_indices=idxs))
        sticker_menu = self.build_sticker_menu(menu, lambda em, idxs=target_indices: self.run_memo_context_action(self.add_sticker_to_memo, em, target_indices=idxs))
        menu.add_cascade(label='스티커', menu=sticker_menu)
        color_menu = self.create_themed_menu(menu)
        self.add_menu_header(color_menu, '글자색')
        colors = [('기본색으로', ''), ('빨간색', '#e74c3c'), ('파란색', '#3498db'), ('초록색', '#27ae60'), ('보라색', '#9b59b6'), ('핑크색', '#ff66b2')]
        for name, code in colors:
            self.add_color_command(color_menu, name, code, lambda c=code, idxs=target_indices: self.run_memo_context_action(self.change_memo_color, c, target_indices=idxs))
        menu.add_cascade(label='글자색', menu=color_menu)
        highlight_menu = self.create_themed_menu(menu)
        self.add_menu_header(highlight_menu, '하이라이트')
        h_colors = [('기본색으로', ''), ('노란색', '#f1c40f'), ('연녹색', '#a2d9ce'), ('연하늘', '#aed6f1'), ('연분홍', '#f5b7b1'), ('회색', '#d5d8dc'), ('핑크색', '#ff99cc')]
        for name, code in h_colors:
            self.add_color_command(highlight_menu, name, code, lambda c=code, idxs=target_indices: self.run_memo_context_action(self.change_memo_highlight, c, target_indices=idxs))
        menu.add_cascade(label='하이라이트', menu=highlight_menu)
        menu.add_separator()
        menu.add_command(label='메모 삭제', command=lambda idxs=target_indices: self.run_memo_context_action(self.delete_memo, target_indices=idxs))
        try:
            menu.tk_popup(ev.x_root, ev.y_root)
        except Exception:
            try:
                menu.post(ev.x_root, ev.y_root)
            except Exception:
                self.clear_memo_context_state()
        finally:
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
        if not target_indices and getattr(self, '_memo_context_target_indices', None):
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
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {'memo_text': new_t})
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
        if not target_indices and getattr(self, '_memo_context_target_indices', None):
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
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {'memo_text': new_t})
        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list_keep_view()
        self.save_memos()
        self.update_time_and_date()
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step53_menu_highlight_drag_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding='utf-8', errors='replace'), encoding='utf-8')
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


def patch_icons_and_header(text: str):
    changed = 0
    replacements = [
        ('            pref = "★ " if is_important else "☆ "', '            pref = "⭐ " if is_important else "☆ "'),
        ("            pref = '★ ' if is_important else '☆ '", "            pref = '⭐ ' if is_important else '☆ '"),
        ('            cb = "☑" if is_strike else "☐"', '            cb = "✔" if is_strike else "○"'),
        ("            cb = '☑' if is_strike else '☐'", "            cb = '✔' if is_strike else '○'"),
        ('                group_color = "#95a5a6"', '                group_color = "#27ae60"'),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1
    return text, changed


def patch_refresh_cleanup_call(text: str):
    changed = 0
    old = """        try:
            self.cleanup_memo_style_blank_areas()
        except Exception:
            pass

        self.memo_text.tag_raise("selected_row")
        self.memo_text.config(state='disabled')"""
    new = """        try:
            self.memo_text.tag_raise("selected_row")
        except Exception:
            pass
        try:
            self.cleanup_memo_style_blank_areas()
            self.raise_memo_style_background_tags()
        except Exception:
            pass

        self.memo_text.config(state='disabled')"""
    if old in text:
        text = text.replace(old, new, 1)
        changed += 1
        return text, changed
    old2 = """        self.memo_text.tag_raise("selected_row")
        self.memo_text.config(state='disabled')"""
    new2 = new
    if old2 in text:
        text = text.replace(old2, new2, 1)
        changed += 1
    return text, changed


def patch_window_drag_methods(text: str):
    changed = 0
    for name in ['click_window', 'drag_window']:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1
    marker = '    def start_resize(self, ev):'
    if marker not in text:
        raise RuntimeError('start_resize 위치를 찾지 못했습니다.')
    text = text.replace(marker, WINDOW_DRAG_METHODS + '\n' + marker, 1)
    changed += 1
    return text, changed


def patch_memo_methods(text: str):
    changed = 0
    for name in [
        'refresh_memo_list_keep_view', 'raise_memo_style_background_tags', 'clear_memo_context_state',
        'run_memo_context_action', 'on_global_left_click_while_memo_menu', 'ensure_memo_context_global_bind',
        'cleanup_memo_style_blank_areas', 'on_memo_click', 'on_memo_drag', 'on_memo_double_click',
        'show_memo_context_menu', 'change_memo_color', 'change_memo_highlight'
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1
    marker = '    def toggle_memo_important_by_idx(self, idx):'
    if marker not in text:
        raise RuntimeError('toggle_memo_important_by_idx 위치를 찾지 못했습니다.')
    text = text.replace(marker, HELPERS + '\n' + ON_MEMO_CLICK_AND_DRAG_METHODS + '\n' + ON_MEMO_DOUBLE_CLICK_METHOD + '\n' + SHOW_MEMO_CONTEXT_MENU_METHOD + '\n' + marker, 1)
    changed += 1
    marker2 = '    def edit_memo(self):'
    if marker2 not in text:
        raise RuntimeError('edit_memo 위치를 찾지 못했습니다.')
    text = text.replace(marker2, CHANGE_MEMO_COLOR_METHOD + '\n' + CHANGE_MEMO_HIGHLIGHT_METHOD + '\n' + marker2, 1)
    changed += 1
    return text, changed


def main():
    print('==============================================')
    print('Step53 memo highlight/menu/drag smooth fix')
    print('==============================================')
    print(f'[ROOT] {ROOT}')
    print()
    if not DESKTOP.exists():
        print(f'[오류] PC 파일이 없습니다: {DESKTOP}')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)
    backup(DESKTOP)
    text = DESKTOP.read_text(encoding='utf-8', errors='replace')
    original = text
    try:
        text, c1 = patch_icons_and_header(text)
        text, c2 = patch_memo_methods(text)
        text, c3 = patch_refresh_cleanup_call(text)
        text, c4 = patch_window_drag_methods(text)
    except Exception as e:
        print('[오류] 패치 실패')
        print(e)
        print('이 화면을 캡처해서 보내주세요.')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)
    try:
        compile(text, str(DESKTOP), 'exec')
        print('[확인] PC 파일 문법 OK')
    except Exception as e:
        print('[경고] PC 파일 문법 확인 실패')
        print(e)
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)
    if text != original:
        DESKTOP.write_text(text, encoding='utf-8')
        print('[완료] Step53 패치 저장')
    else:
        print('[안내] 변경 없음')
    print()
    print('[변경 요약]')
    print(f'- 아이콘 원복/완료 메모 헤더 색상 보정: {c1}')
    print(f'- 우클릭 메뉴 잠금/하이라이트/스크롤 메서드 보정: {c2}')
    print(f'- refresh_memo_list 하이라이트 표시 우선순위 보정: {c3}')
    print(f'- 창 이동 부드럽게 개선: {c4}')
    print()
    print('실행:')
    print('python desktop\\timetable.pyw')
    print()
    print('확인할 것:')
    print('1. 하이라이트가 선택된 줄에서도 글자 부분에 빠짐없이 보이는지')
    print('2. 완료 메모 카테고리 앞 체크가 완료 메모 체크와 같은 녹색 계열인지')
    print('3. 우클릭 메뉴가 열린 직후 마우스를 움직여도 선택이 흔들리지 않는지')
    print('4. 글자색/하이라이트 적용 후 스크롤이 상단으로 튀지 않는지')
    print('5. 창을 움직일 때 떨림이 줄고 부드러운지')
    input('엔터를 누르면 종료합니다.')


if __name__ == '__main__':
    main()

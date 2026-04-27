# tools/step48_restore_save_sticker_menu_color_reset.py
# ------------------------------------------------------------
# Step48: 저장 버튼 복원 / 스티커 메뉴 폰트 통일 / 기본색 초기화 수정
#
# 실행:
#   python tools\step48_restore_save_sticker_menu_color_reset.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

BUILD_STICKER_MENU_METHOD = '''
    def build_sticker_menu(self, parent_menu, apply_func):
        # 오른쪽 버튼 스티커 하위 메뉴: 다른 컨텍스트 메뉴와 폰트/굵기/크기 통일
        sticker_menu = self.create_themed_menu(parent_menu)

        for category, items in STICKER_CATEGORIES:
            sub = self.create_themed_menu(sticker_menu)
            for emoji, desc in items:
                sub.add_command(
                    label=f"{emoji}  {desc}",
                    command=lambda em=emoji: apply_func(em)
                )
            sticker_menu.add_cascade(label=category, menu=sub)

        return sticker_menu
'''

CHANGE_MEMO_COLOR_METHOD = '''
    def change_memo_color(self, color):
        if not self.can_view_private_data():
            return

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u:
            return

        for idx in list(self.selected_memo_indices):
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

        for idx in list(self.selected_memo_indices):
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
    b = path.with_name(f"{path.stem}_before_step48_save_menu_color_{STAMP}{path.suffix}")
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


def patch_imports(text: str):
    changed = 0
    if 'from PIL import Image, ImageTk, ImageDraw' in text:
        text = text.replace('from PIL import Image, ImageTk, ImageDraw', 'from PIL import Image, ImageTk', 1)
        changed += 1
    return text, changed


def patch_save_button_restore(text: str):
    changed = 0

    old_variants = [
        "        self.save_btn = tk.Button(self.row1_right, text='', bd=0, width=3, font=('Segoe UI Symbol', 10), command=self.manual_save_db)",
        '        self.save_btn = tk.Button(self.row1_right, text="", bd=0, width=3, font=(\'Segoe UI Symbol\', 10), command=self.manual_save_db)',
    ]
    new = "        self.save_btn = tk.Button(self.row1_right, text='저장', bd=0, width=4, font=self.font_title, command=self.manual_save_db)"
    for old in old_variants:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1
            break

    old_block = """        if hasattr(self, 'save_btn'):
            self.save_btn.config(text='', width=3)
            if hasattr(self, 'save_btn_icon'):
                try:
                    self.save_btn.config(image=self.save_btn_icon, compound='image')
                except Exception:
                    pass"""
    new_block = """        if hasattr(self, 'save_btn'):
            try:
                self.save_btn.config(image='', text='저장', width=4, compound='none', font=self.font_title)
            except Exception:
                self.save_btn.config(text='저장', width=4)"""
    if old_block in text:
        text = text.replace(old_block, new_block, 1)
        changed += 1

    for line in [
        '        self.refresh_toolbar_icon_assets()\n',
        '            self.refresh_toolbar_icon_assets()\n',
    ]:
        if line in text:
            text = text.replace(line, '', 10)
            changed += 1

    for name in ['_build_save_icon', 'refresh_toolbar_icon_assets']:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    return text, changed


def patch_sticker_menu_font(text: str):
    changed = 0

    before = text
    text = remove_method(text, 'build_sticker_menu')
    if text != before:
        changed += 1

    marker = '    def close_sticker_palette(self):'
    if marker not in text:
        marker = '    def __init__(self, root):'

    if marker not in text:
        raise RuntimeError('build_sticker_menu 삽입 위치를 찾지 못했습니다.')

    text = text.replace(marker, BUILD_STICKER_MENU_METHOD + '\n' + marker, 1)
    changed += 1

    return text, changed


def patch_color_reset_methods(text: str):
    changed = 0

    for name in ['change_memo_color', 'change_memo_highlight']:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = '    def edit_memo(self):'
    if marker not in text:
        raise RuntimeError('edit_memo 위치를 찾지 못했습니다.')

    text = text.replace(
        marker,
        CHANGE_MEMO_COLOR_METHOD + '\n' + CHANGE_MEMO_HIGHLIGHT_METHOD + '\n' + marker,
        1
    )
    changed += 1

    return text, changed


def main():
    print('==============================================')
    print('Step48 restore save / sticker menu / color reset')
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
        text, c1 = patch_imports(text)
        text, c2 = patch_save_button_restore(text)
        text, c3 = patch_sticker_menu_font(text)
        text, c4 = patch_color_reset_methods(text)
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
        print('[완료] Step48 패치 저장')
    else:
        print('[안내] 변경 없음')

    print()
    print('[변경 요약]')
    print(f'- ImageDraw import 정리: {c1}')
    print(f'- 저장 버튼 저장 복원: {c2}')
    print(f'- 스티커 메뉴 폰트 통일: {c3}')
    print(f'- 기본색 초기화 수정: {c4}')
    print()
    print('실행:')
    print('python desktop\\timetable.pyw')
    print()
    print('확인할 것:')
    print('1. 저장 버튼이 다시 저장 글자로 보이는지')
    print('2. 우클릭 > 스티커 하위 메뉴 폰트가 다른 메뉴와 동일한지')
    print('3. 메모 글자색 > 기본색으로 선택 시 글자색이 초기화되는지')
    print('4. 메모 하이라이트 > 기본색으로 선택 시 하이라이트가 초기화되는지')
    input('엔터를 누르면 종료합니다.')


if __name__ == '__main__':
    main()

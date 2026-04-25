# tools/step47_toolbar_lovely_pink_icons.py
# ------------------------------------------------------------
# Step47: 테마/툴바 UI 개선
#
# 적용 내용
# 1) 새 테마 '러블리 핑크' 추가
# 2) undo / redo 아이콘을 더 깔끔한 꺾인 화살표 형태로 변경
# 3) 상단 저장 버튼을 글자 대신 아이콘형(디스크) 버튼으로 변경
#    - 외부 파일 의존 없이 코드 내부에서 벡터 느낌의 아이콘 생성
#    - 아이콘 생성 실패 시 텍스트 fallback 사용
# 4) 상단 버튼(오늘/달력/메모/조회/8·9)에 hover 음영 반영
# 5) 기존 Step46의 하단 현재시각/교시 전환 강조는 유지
#
# 실행:
#   python tools\step47_toolbar_lovely_pink_icons.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

LOVELY_PINK_THEME = """
            { 'name': '러블리 핑크', 'bg': '#fff5fa', 'top': '#ffe7f1', 'grid': '#f2cfe0', 'head_bg': '#ffdce9', 'head_fg': '#6b314e', 'per_bg': '#f7cddd', 'per_fg': '#6b314e', 'cell_bg': '#ffffff', 'lunch_bg': '#fff0f6', 'cell_fg': '#5a4250', 'hl_per': '#e85d9e', 'hl_cell': '#ffe5f1', 'titlebar_bg': '#fff8fb', 'hover_btn': '#ffddea', 'hover_title': '#ffe9f2', 'hover_cell': '#fff7fb', 'hover_lunch': '#fff0f6',
              'acad_per_bg': '#c779d0', 'acad_per_fg': 'white', 'acad_cell_bg': '#fbecff', 'acad_cell_fg': '#8b3ea8', 'panel_bg': '#ffffff', 'panel_border': '#efcfde', 'input_bg': '#fffafd', 'muted_fg': '#9b6b83', 'accent': '#e85d9e', 'accent_soft': '#ffe1ee', 'danger': '#e64980', 'shadow': '#f9e7ef', 'accent_hover': '#d9488b', 'title_btn_fg': '#7b4360', 'subtle_btn_fg': '#91526e' },
"""

HELPER_METHODS = r'''
    def _blend_hex(self, base_color, target_color='#000000', amount=0.12):
        """두 색을 부드럽게 섞어 hover용 음영색 생성."""
        try:
            def _norm(val):
                if not val or not isinstance(val, str):
                    return '#000000'
                val = val.strip()
                if not val.startswith('#') or len(val) != 7:
                    return '#000000'
                return val

            base_color = _norm(base_color)
            target_color = _norm(target_color)
            amount = max(0.0, min(1.0, float(amount)))
            br, bg, bb = [int(base_color[i:i+2], 16) for i in (1, 3, 5)]
            tr, tg, tb = [int(target_color[i:i+2], 16) for i in (1, 3, 5)]
            r = round(br + (tr - br) * amount)
            g = round(bg + (tg - bg) * amount)
            b = round(bb + (tb - bb) * amount)
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return base_color if isinstance(base_color, str) else '#000000'

    def _build_save_icon(self, size=14, color='#ffffff'):
        """상단 저장 버튼용 간단한 디스크 아이콘을 코드로 생성."""
        size = max(12, int(size))
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        pad = 1
        body = (pad, pad, size - pad - 1, size - pad - 1)
        draw.rounded_rectangle(body, radius=2, outline=color, width=2)
        top_h = max(4, size // 3)
        draw.rectangle((pad + 1, pad + 1, size - pad - 2, pad + top_h), fill=color)

        hole_w = max(3, size // 4)
        hole_h = max(3, size // 5)
        draw.rectangle((size - pad - hole_w - 2, pad + 1, size - pad - 2, pad + hole_h), fill=(0, 0, 0, 0))

        label_top = pad + top_h + 2
        label_bottom = size - pad - 3
        draw.rectangle((pad + 3, label_top, size - pad - 4, label_bottom), outline=color, width=1)
        draw.line((pad + 4, label_top + 2, size - pad - 5, label_top + 2), fill=color, width=1)
        return ImageTk.PhotoImage(img)

    def refresh_toolbar_icon_assets(self):
        """테마 변경 후에도 저장 버튼이 아이콘형으로 유지되게 함."""
        if not hasattr(self, 'save_btn'):
            return
        try:
            self.save_btn_icon = self._build_save_icon(size=14, color='#ffffff')
            self.save_btn.configure(image=self.save_btn_icon, text='', compound='image')
        except Exception:
            try:
                self.save_btn.configure(image='', text='🖫', font=('Segoe UI Symbol', 10))
            except Exception:
                pass
'''

UPDATE_TOOLBAR_TEXTS_METHOD = r'''
    def update_toolbar_texts(self):
        compact = getattr(self, 'toolbar_compact_mode', False)
        very_compact = getattr(self, 'toolbar_very_compact', False)

        curr_txt = '오늘'
        cal_txt = '달력'
        memo_txt = '메모'
        zero_txt = '조회'
        extra_txt = '8·9'
        settings_txt = '설정'

        if very_compact:
            cal_txt = '달력'
            settings_txt = '⋯'
        elif compact:
            extra_txt = '8·9'

        if hasattr(self, 'curr_btn'):
            self.curr_btn.config(text=curr_txt, width=4)
        if hasattr(self, 'cal_btn'):
            self.cal_btn.config(text=cal_txt, width=4)
        if hasattr(self, 'memo_btn'):
            self.memo_btn.config(text=memo_txt, width=4)
        if hasattr(self, 'zero_btn'):
            self.zero_btn.config(text=zero_txt, width=4)
        if hasattr(self, 'extra_btn'):
            self.extra_btn.config(text=extra_txt, width=4)
        if hasattr(self, 'save_btn'):
            self.save_btn.config(text='', width=3)
            if hasattr(self, 'save_btn_icon'):
                try:
                    self.save_btn.config(image=self.save_btn_icon, compound='image')
                except Exception:
                    pass
        if hasattr(self, 'settings_mb'):
            self.settings_mb.config(text=settings_txt, width=3 if very_compact else 4)
        if hasattr(self, 'teacher_cb'):
            self.teacher_cb.configure(width=7 if very_compact else (8 if compact else 10))
        if hasattr(self, 'alpha_lbl'):
            self.alpha_lbl.config(text='' if compact else '투명')
        if hasattr(self, 'alpha_scale'):
            self.alpha_scale.configure(width=34 if very_compact else (42 if compact else 52))
            self.alpha_scale.draw()
'''

STYLE_TOGGLE_CHIP_METHOD = r'''
    def style_toggle_chip(self, frame, button, variant='neutral', active=False):
        t = self.themes[self.current_theme_idx]
        palette_map = {
            'calendar': {'bg': '#f5f0ff', 'fg': '#5b3cc4', 'line': '#6d5bd0', 'hover_bg': '#ede5ff', 'hover_fg': '#4c31a6'},
            'memo': {'bg': '#eef6ff', 'fg': '#0f5cc0', 'line': '#2563eb', 'hover_bg': '#deeeff', 'hover_fg': '#0b4ea8'},
            'lookup': {'bg': '#fff7ea', 'fg': '#9a5b00', 'line': '#d97706', 'hover_bg': '#ffefd5', 'hover_fg': '#7c4800'},
            'extra': {'bg': '#f0f4ff', 'fg': '#3347b4', 'line': '#4f46e5', 'hover_bg': '#e3ebff', 'hover_fg': '#25389d'},
            'today': {
                'bg': t.get('accent_soft', t['hl_cell']),
                'fg': t.get('accent', t['hl_per']),
                'line': t.get('accent', t['hl_per']),
                'hover_bg': self._blend_hex(t.get('accent_soft', t['hl_cell']), t.get('accent', t['hl_per']), 0.10),
                'hover_fg': t.get('accent', t['hl_per'])
            },
            'neutral': {
                'bg': t.get('input_bg', t['cell_bg']),
                'fg': t.get('head_fg', t['cell_fg']),
                'line': t.get('panel_border', t['grid']),
                'hover_bg': t.get('hover_btn', t.get('top', t['bg'])),
                'hover_fg': t.get('head_fg', t['cell_fg'])
            }
        }
        p = palette_map.get(variant, palette_map['neutral'])
        frame.configure(bg=p['line'] if active else t.get('panel_border', t['grid']), height=1)

        hover_bg = p.get('hover_bg', p['bg'])
        hover_fg = p.get('hover_fg', p['fg'])
        if active:
            hover_bg = self._blend_hex(p['bg'], p['line'], 0.10)
            hover_fg = p['fg']

        button.configure(bg=p['bg'], fg=p['fg'], activebackground=hover_bg, activeforeground=hover_fg)
        button._base_bg = p['bg']
        button._base_fg = p['fg']
        button._hover_bg = hover_bg
        button._hover_fg = hover_fg
'''


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step47_toolbar_{STAMP}{path.suffix}")
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
    end = min(candidates)
    return text[:start] + text[end:]


def patch_imports(text: str):
    changed = 0
    old = "from PIL import Image, ImageTk"
    new = "from PIL import Image, ImageTk, ImageDraw"
    if old in text and new not in text:
        text = text.replace(old, new, 1)
        changed += 1
    return text, changed


def patch_theme(text: str):
    changed = 0
    if "'name': '러블리 핑크'" in text:
        return text, changed
    anchor = "        ]\n        \n        \n        self.root.overrideredirect(True)"
    replacement = ",\n" + LOVELY_PINK_THEME + "        ]\n        \n        \n        self.root.overrideredirect(True)"
    if anchor in text:
        text = text.replace(anchor, replacement, 1)
        changed += 1
        return text, changed
    raise RuntimeError("테마 목록 끝 위치를 찾지 못했습니다.")


def patch_helper_methods(text: str):
    changed = 0
    for name in ["_blend_hex", "_build_save_icon", "refresh_toolbar_icon_assets"]:
        new_text = remove_method(text, name)
        if new_text != text:
            text = new_text
            changed += 1
    marker = "    def style_toolbar_button(self, button, variant='neutral'):"
    if marker not in text:
        raise RuntimeError("style_toolbar_button 위치를 찾지 못했습니다.")
    text = text.replace(marker, HELPER_METHODS + "\n" + marker, 1)
    changed += 1
    return text, changed


def patch_update_toolbar_texts(text: str):
    changed = 0
    before = text
    text = remove_method(text, "update_toolbar_texts")
    if text != before:
        changed += 1
    marker = "    def relayout_toolbar(self, event=None):"
    if marker not in text:
        raise RuntimeError("relayout_toolbar 위치를 찾지 못했습니다.")
    text = text.replace(marker, UPDATE_TOOLBAR_TEXTS_METHOD + "\n" + marker, 1)
    changed += 1
    return text, changed


def patch_style_toggle_chip(text: str):
    changed = 0
    before = text
    text = remove_method(text, "style_toggle_chip")
    if text != before:
        changed += 1
    marker = "    def apply_combobox_style(self):"
    if marker not in text:
        raise RuntimeError("apply_combobox_style 위치를 찾지 못했습니다.")
    text = text.replace(marker, STYLE_TOGGLE_CHIP_METHOD + "\n" + marker, 1)
    changed += 1
    return text, changed


def patch_toolbar_widgets(text: str):
    changed = 0
    replacements = [
        (
            "        self.undo_btn = tk.Button(self.title_left, text='↺', bd=0, width=3, font=('Segoe UI Symbol', 10), command=self.undo_action)",
            "        self.undo_btn = tk.Button(self.title_left, text='↶', bd=0, width=3, font=('Segoe UI Symbol', 11), command=self.undo_action)"
        ),
        (
            "        self.redo_btn = tk.Button(self.title_left, text='↻', bd=0, width=3, font=('Segoe UI Symbol', 10), command=self.redo_action)",
            "        self.redo_btn = tk.Button(self.title_left, text='↷', bd=0, width=3, font=('Segoe UI Symbol', 11), command=self.redo_action)"
        ),
        (
            "        self.save_btn = tk.Button(self.row1_right, text='저장', bd=0, width=4, font=self.font_title, command=self.manual_save_db)",
            "        self.save_btn = tk.Button(self.row1_right, text='', bd=0, width=3, font=('Segoe UI Symbol', 10), command=self.manual_save_db)"
        ),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1

    old = "        self.update_settings_menu()\n\n        for b in [self.prev_btn, self.curr_btn, self.next_btn, self.cal_btn, self.memo_btn, self.zero_btn, self.extra_btn, self.save_btn, self.settings_mb]:"
    new = "        self.update_settings_menu()\n        self.refresh_toolbar_icon_assets()\n\n        for b in [self.prev_btn, self.curr_btn, self.next_btn, self.cal_btn, self.memo_btn, self.zero_btn, self.extra_btn, self.save_btn, self.settings_mb]:"
    if old in text:
        text = text.replace(old, new, 1)
        changed += 1
    return text, changed


def patch_apply_theme(text: str):
    changed = 0
    old = """            self.style_toolbar_button(self.cal_btn, 'calendar')
            self.style_toolbar_button(self.memo_btn, 'memo')
            self.style_toolbar_button(self.zero_btn, 'lookup')
            self.style_toolbar_button(self.extra_btn, 'extra')
            self.style_toolbar_button(self.save_btn, 'accent')
            self.style_toolbar_button(self.settings_mb, 'neutral')"""
    new = """            self.style_toolbar_button(self.cal_btn, 'calendar')
            self.style_toolbar_button(self.memo_btn, 'memo')
            self.style_toolbar_button(self.zero_btn, 'lookup')
            self.style_toolbar_button(self.extra_btn, 'extra')
            self.style_toolbar_button(self.save_btn, 'accent')
            self.style_toolbar_button(self.settings_mb, 'neutral')
            self.refresh_toolbar_icon_assets()"""
    if old in text:
        text = text.replace(old, new, 1)
        changed += 1
    return text, changed


def main():
    print("==============================================")
    print("Step47 toolbar / lovely pink / hover patch")
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
        text, c1 = patch_imports(text)
        text, c2 = patch_theme(text)
        text, c3 = patch_helper_methods(text)
        text, c4 = patch_update_toolbar_texts(text)
        text, c5 = patch_style_toggle_chip(text)
        text, c6 = patch_toolbar_widgets(text)
        text, c7 = patch_apply_theme(text)
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
        print("[경고] 문법 확인 실패")
        print(e)
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] Step47 툴바/테마 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- PIL import 보강: {c1}")
    print(f"- 러블리 핑크 테마 추가: {c2}")
    print(f"- 아이콘 헬퍼 메서드: {c3}")
    print(f"- 툴바 텍스트/아이콘 상태: {c4}")
    print(f"- 툴바 hover chip 개선: {c5}")
    print(f"- undo/redo/save 위젯 교체: {c6}")
    print(f"- apply_theme 연동: {c7}")
    print()
    print("실행:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 설정 > 테마 변경에 '러블리 핑크'가 보이는지")
    print("2. 좌상단 undo / redo 아이콘이 더 깔끔한 꺾인 화살표로 보이는지")
    print("3. 저장 버튼이 글자 대신 디스크 아이콘처럼 보이는지")
    print("4. 오늘/달력/메모/조회/8·9 버튼 hover 시 음영이 들어오는지")
    print("5. 기존 하단 시계/교시 전환 강조가 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

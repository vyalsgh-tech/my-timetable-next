# tools/step46_enhance_bottom_clock_theme.py
# ------------------------------------------------------------
# Step46: 하단 현재시각 표시 디자인 개선 + 교시 전환 강조
#
# Step45 점검 결과:
# - 현재시각 표시는 추가했지만,
# - "현재 교시가 바뀌는 시점에만 살짝 진하게" 강조하는 기능은 미반영 상태.
#
# Step46 적용 내용:
# 1) 하단 우측 현재시각을 테마에 어울리는 작은 pill 형태로 개선
# 2) 평소에는 회색/차분한 상태 정보처럼 표시
# 3) 교시/점심/쉬는시간/방과후 등 시간대가 바뀐 직후 약 70초 동안만
#    글자를 살짝 진하게 표시
# 4) 시간표/메모/검색/A+/A- 기능은 건드리지 않음
#
# 실행:
#   python tools\step46_enhance_bottom_clock_theme.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

CLOCK_METHODS = '\n    def get_bottom_clock_period_key(self):\n        """현재 시각이 속한 교시/시간대 키를 반환. 교시 전환 강조 판단용."""\n        try:\n            import datetime as _dt\n            now = _dt.datetime.now().time()\n\n            slots = [\n                ("1교시", _dt.time(8, 0), _dt.time(8, 50)),\n                ("2교시", _dt.time(9, 0), _dt.time(9, 50)),\n                ("3교시", _dt.time(10, 0), _dt.time(10, 50)),\n                ("4교시", _dt.time(11, 0), _dt.time(11, 50)),\n                ("점심", _dt.time(11, 50), _dt.time(12, 40)),\n                ("5교시", _dt.time(12, 40), _dt.time(13, 30)),\n                ("6교시", _dt.time(13, 40), _dt.time(14, 30)),\n                ("7교시", _dt.time(14, 40), _dt.time(15, 30)),\n                ("8교시", _dt.time(16, 0), _dt.time(16, 50)),\n                ("9교시", _dt.time(17, 0), _dt.time(17, 50)),\n            ]\n\n            for name, start, end in slots:\n                if start <= now < end:\n                    return name\n\n            if now < _dt.time(8, 0):\n                return "수업전"\n            if now >= _dt.time(17, 50):\n                return "방과후"\n            return "쉬는시간"\n        except Exception:\n            return "unknown"\n\n    def get_bottom_clock_theme_style(self, emphasized=False):\n        """현재 테마에 어울리는 하단 시계 색상 세트."""\n        try:\n            t = self.get_active_theme()\n        except Exception:\n            try:\n                t = self.themes[self.current_theme_idx]\n            except Exception:\n                t = {}\n\n        try:\n            parent_bg = self.memo_input_f.cget("bg")\n        except Exception:\n            parent_bg = t.get("panel_bg", "#ffffff")\n\n        normal_fg = (\n            t.get("muted_fg") or\n            t.get("memo_time_fg") or\n            t.get("subtle_fg") or\n            "#6B7280"\n        )\n\n        accent_fg = (\n            t.get("today_bg") or\n            t.get("selected_bg") or\n            t.get("button_bg") or\n            t.get("accent") or\n            "#2563EB"\n        )\n\n        border = (\n            t.get("grid_line") or\n            t.get("panel_border") or\n            t.get("border") or\n            "#D1D5DB"\n        )\n\n        # 테마별 과한 색상화를 피하고, 평소에는 부모 배경과 거의 일체화\n        normal_bg = parent_bg\n\n        # 교시 전환 직후에만 살짝 강조\n        emph_bg = (\n            t.get("today_light_bg") or\n            t.get("selected_light_bg") or\n            t.get("header_bg") or\n            parent_bg\n        )\n\n        return {\n            "parent_bg": parent_bg,\n            "normal_bg": normal_bg,\n            "emph_bg": emph_bg,\n            "normal_fg": normal_fg,\n            "emph_fg": accent_fg,\n            "border": accent_fg if emphasized else border,\n        }\n\n    def format_bottom_clock_text(self):\n        """하단 우측 현재시각 표시용 텍스트."""\n        try:\n            import datetime as _dt\n            return _dt.datetime.now().strftime("%H:%M")\n        except Exception:\n            return "--:--"\n\n    def update_bottom_clock(self):\n        """하단 메모 입력줄 우측 현재시각 갱신.\n        교시/시간대가 바뀐 직후에는 약 70초 동안 살짝 진하게 표시한다.\n        """\n        try:\n            import datetime as _dt\n            now = _dt.datetime.now()\n            cur_period = self.get_bottom_clock_period_key()\n\n            if not hasattr(self, "_bottom_clock_last_period"):\n                self._bottom_clock_last_period = cur_period\n                self._bottom_clock_emphasis_until = 0\n\n            if cur_period != self._bottom_clock_last_period:\n                self._bottom_clock_last_period = cur_period\n                self._bottom_clock_emphasis_until = now.timestamp() + 70\n\n            emphasized = now.timestamp() < getattr(self, "_bottom_clock_emphasis_until", 0)\n\n            if hasattr(self, "bottom_clock_label") and self.bottom_clock_label.winfo_exists():\n                style = self.get_bottom_clock_theme_style(emphasized=emphasized)\n\n                if hasattr(self, "bottom_clock_frame") and self.bottom_clock_frame.winfo_exists():\n                    try:\n                        self.bottom_clock_frame.configure(\n                            bg=style["emph_bg"] if emphasized else style["normal_bg"],\n                            highlightbackground=style["border"],\n                            highlightcolor=style["border"],\n                        )\n                    except Exception:\n                        pass\n\n                self.bottom_clock_label.configure(\n                    text=self.format_bottom_clock_text(),\n                    bg=style["emph_bg"] if emphasized else style["normal_bg"],\n                    fg=style["emph_fg"] if emphasized else style["normal_fg"],\n                    font=("맑은 고딕", 12, "bold" if emphasized else "normal"),\n                )\n        except Exception:\n            pass\n\n        # 교시 전환 강조를 부드럽게 처리하려고 1초마다 확인.\n        # 표시 글자는 HH:MM이라 시각적으로는 분 단위처럼 보임.\n        try:\n            self.root.after(1000, self.update_bottom_clock)\n        except Exception:\n            pass\n'
CLOCK_UI_BLOCK = '\n        self.bottom_clock_frame = tk.Frame(\n            self.memo_input_f,\n            bd=0,\n            highlightthickness=1,\n            highlightbackground="#D1D5DB",\n            highlightcolor="#D1D5DB",\n            padx=0,\n            pady=0,\n            cursor="arrow",\n        )\n        self.bottom_clock_label = tk.Label(\n            self.bottom_clock_frame,\n            text="--:--",\n            bd=0,\n            font=("맑은 고딕", 12),\n            fg="#6B7280",\n            padx=8,\n            pady=2,\n            anchor="center",\n            cursor="arrow",\n        )\n        self.bottom_clock_label.pack(side="left")\n        self.bottom_clock_frame.pack(side=\'right\', padx=(10, 2))\n        self.update_bottom_clock()\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step46_clock_theme_{STAMP}{path.suffix}")
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


def remove_existing_clock_ui(text: str) -> str:
    markers = [
        "        self.bottom_clock_frame = tk.Frame(",
        "        self.bottom_clock_label = tk.Label(",
    ]

    changed = True
    while changed:
        changed = False
        for marker in markers:
            start = text.find(marker)
            if start == -1:
                continue

            end_marker = "        self.update_bottom_clock()"
            end = text.find(end_marker, start)
            if end == -1:
                continue

            end_line = text.find("\n", end)
            end_line = len(text) if end_line == -1 else end_line + 1
            text = text[:start] + text[end_line:]
            changed = True
            break

    return text


def patch_clock_methods(text: str):
    changed = 0

    for name in [
        "get_bottom_clock_period_key",
        "get_bottom_clock_theme_style",
        "format_bottom_clock_text",
        "update_bottom_clock",
    ]:
        before = text
        text = remove_method(text, name)
        if text != before:
            changed += 1

    marker = "    def refresh_memo_list(self):"
    if marker not in text:
        raise RuntimeError("refresh_memo_list 위치를 찾지 못했습니다.")

    text = text.replace(marker, CLOCK_METHODS + "\n\n" + marker, 1)
    changed += 1

    return text, changed


def patch_clock_ui(text: str):
    changed = 0
    text = remove_existing_clock_ui(text)

    candidates = [
        "        self.shrink_btn.pack(side='left', padx=1)",
        '        self.shrink_btn.pack(side="left", padx=1)',
        "        self.shrink_btn.pack(side='left', padx=(1, 0))",
        '        self.shrink_btn.pack(side="left", padx=(1, 0))',
    ]

    for anchor in candidates:
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + CLOCK_UI_BLOCK, 1)
            changed += 1
            return text, changed

    anchor = "        self.memo_list_f = tk.Frame(self.memo_frame"
    pos = text.find(anchor)
    if pos != -1:
        text = text[:pos] + CLOCK_UI_BLOCK + "\n" + text[pos:]
        changed += 1
        return text, changed

    raise RuntimeError("하단 메모 입력줄의 A- 버튼 또는 memo_list_f 위치를 찾지 못했습니다.")


def main():
    print("==============================================")
    print("Step46 enhance bottom clock theme")
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
        text, method_changes = patch_clock_methods(text)
        text, ui_changes = patch_clock_ui(text)
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
        print("[완료] Step46 현재시각 디자인/강조 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print(f"- 현재시각 메서드 변경: {method_changes}")
    print(f"- 하단 UI 변경: {ui_changes}")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 하단 우측 시각이 작은 상태표시 pill처럼 보이는지")
    print("2. 평소에는 회색 계열로 차분하게 표시되는지")
    print("3. 교시/점심/쉬는시간 등 시간대가 바뀐 직후 약 70초 동안 살짝 진해지는지")
    print("4. 메모 입력줄/검색/A+/A-/시간표/메모 수정 기능이 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

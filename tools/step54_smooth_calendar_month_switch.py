# tools/step54_smooth_calendar_month_switch.py
# ------------------------------------------------------------
# Step54: 달력 월 이동 시 아래에서부터 물결치듯 다시 그려지는 현상 개선
#
# 수정 내용:
# 1) ModernCalendar 클래스를 부드러운 렌더링 구조로 교체
# 2) 날짜 모드를 항상 6주 행으로 고정하여 월 이동 시 높이 변화를 방지
# 3) 새 달력 화면을 보이지 않는 새 Frame에 먼저 구성한 뒤 한 번에 교체
# 4) 월/연도 이동 중 현재 팝업 크기를 고정하여 리사이즈 흔들림 완화
#
# 실행:
#   python tools\step54_smooth_calendar_month_switch.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

NEW_CALENDAR_CLASS = '\nclass ModernCalendar(tk.Toplevel):\n    """월 이동 시 아래에서부터 물결치듯 다시 그려지는 현상을 줄인 달력 팝업.\n\n    핵심 개선:\n    - 날짜 모드는 항상 6주 행을 확보하여 월마다 높이가 변하지 않게 함\n    - 새 화면을 보이지 않는 새 Frame에 먼저 구성한 뒤 한 번에 교체\n    - 월/연도 이동 중 현재 창 크기를 고정하여 리사이즈 흔들림을 방지\n    """\n    def __init__(self, parent, theme, start_date, command):\n        super().__init__(parent)\n        self.overrideredirect(True)\n        self.theme = theme\n        self.current_date = start_date\n        self.command = command\n        self.mode = "day"\n        self.year_base = start_date.year // 10 * 10\n\n        self._rendering = False\n        self._fixed_width = 258\n        self._fixed_height = 246\n\n        self.configure(bg=self.theme[\'bg\'], bd=1, relief="solid")\n        self.bind("<FocusOut>", lambda e: self.destroy())\n\n        self.main_frame = None\n        self.render()\n        self.focus_set()\n\n    def make_cal_button(self, parent, **kwargs):\n        t = self.theme\n        kwargs.setdefault("bd", 0)\n        kwargs.setdefault("cursor", "hand2")\n        kwargs.setdefault("font", (\'맑은 고딕\', 9))\n        kwargs.setdefault("activebackground", t.get(\'hover_btn\', t.get(\'top\', t[\'cell_bg\'])))\n        kwargs.setdefault("activeforeground", t.get(\'head_fg\', t.get(\'cell_fg\', \'black\')))\n        return tk.Button(parent, **kwargs)\n\n    def build_header(self, parent):\n        t = self.theme\n        header_f = tk.Frame(parent, bg=t[\'top\'])\n        header_f.pack(fill=\'x\')\n\n        prev_btn = self.make_cal_button(\n            header_f,\n            text="◀",\n            bg=t[\'top\'],\n            fg=t.get(\'head_fg\', \'white\'),\n            width=3,\n            command=self.prev_action\n        )\n        prev_btn.pack(side=\'left\', padx=5, pady=5)\n\n        if self.mode == "day":\n            title_text = f"{self.current_date.year}년 {self.current_date.month}월"\n        elif self.mode == "month":\n            title_text = f"{self.current_date.year}년"\n        else:\n            title_text = f"{self.year_base} - {self.year_base + 9}"\n\n        title_btn = self.make_cal_button(\n            header_f,\n            text=title_text,\n            bg=t[\'top\'],\n            fg=t.get(\'head_fg\', \'white\'),\n            font=(\'맑은 고딕\', 10, \'bold\'),\n            command=self.zoom_out\n        )\n        title_btn.pack(side=\'left\', expand=True, fill=\'x\')\n\n        next_btn = self.make_cal_button(\n            header_f,\n            text="▶",\n            bg=t[\'top\'],\n            fg=t.get(\'head_fg\', \'white\'),\n            width=3,\n            command=self.next_action\n        )\n        next_btn.pack(side=\'right\', padx=5, pady=5)\n\n    def build_day_view(self, parent):\n        t = self.theme\n\n        days_f = tk.Frame(parent, bg=t[\'cell_bg\'])\n        days_f.grid(row=0, column=0, sticky=\'ew\', pady=(0, 4))\n        for i in range(7):\n            days_f.grid_columnconfigure(i, weight=1, uniform=\'day_header\')\n\n        days = ["일", "월", "화", "수", "목", "금", "토"]\n        for i, d in enumerate(days):\n            fg = "#e74c3c" if i == 0 else "#3498db" if i == 6 else t[\'cell_fg\']\n            tk.Label(\n                days_f,\n                text=d,\n                bg=t[\'cell_bg\'],\n                fg=fg,\n                width=4,\n                font=(\'맑은 고딕\', 8, \'bold\')\n            ).grid(row=0, column=i, sticky=\'nsew\')\n\n        dates_f = tk.Frame(parent, bg=t[\'cell_bg\'])\n        dates_f.grid(row=1, column=0, sticky=\'nsew\')\n        for c in range(7):\n            dates_f.grid_columnconfigure(c, weight=1, uniform=\'date_col\')\n        for r in range(6):\n            dates_f.grid_rowconfigure(r, weight=1, uniform=\'date_row\', minsize=28)\n\n        cal = calendar.Calendar(firstweekday=6)\n        month_days = cal.monthdatescalendar(self.current_date.year, self.current_date.month)\n\n        # 월마다 5주/6주로 높이가 달라져 물결치는 원인이 되므로 항상 6주로 고정\n        while len(month_days) < 6:\n            last_week = month_days[-1]\n            next_week = [d + timedelta(days=7) for d in last_week]\n            month_days.append(next_week)\n\n        today = datetime.now().date()\n        for r, week in enumerate(month_days[:6]):\n            for c, d in enumerate(week):\n                fg = t[\'cell_fg\']\n                if d.month != self.current_date.month:\n                    fg = "#bdc3c7"\n                elif c == 0:\n                    fg = "#e74c3c"\n                elif c == 6:\n                    fg = "#3498db"\n\n                bg = t[\'cell_bg\']\n                if d == today:\n                    bg = t[\'hl_per\']\n                    fg = "white" if t[\'name\'] != \'웜 파스텔\' else \'black\'\n\n                btn = self.make_cal_button(\n                    dates_f,\n                    text=str(d.day),\n                    bg=bg,\n                    fg=fg,\n                    width=4,\n                    command=lambda date=d: self.select_date(date)\n                )\n                btn.grid(row=r, column=c, sticky=\'nsew\', padx=1, pady=1)\n\n    def build_month_view(self, parent):\n        t = self.theme\n        for c in range(3):\n            parent.grid_columnconfigure(c, weight=1, uniform=\'month_col\')\n        for r in range(4):\n            parent.grid_rowconfigure(r, weight=1, uniform=\'month_row\', minsize=36)\n\n        for r in range(4):\n            for c in range(3):\n                m = r * 3 + c + 1\n                bg = t[\'cell_bg\']\n                if self.current_date.year == datetime.now().year and m == datetime.now().month:\n                    bg = t[\'hl_per\']\n                btn = self.make_cal_button(\n                    parent,\n                    text=f"{m}월",\n                    bg=bg,\n                    fg=t[\'cell_fg\'],\n                    command=lambda month=m: self.select_month(month)\n                )\n                btn.grid(row=r, column=c, sticky=\'nsew\', padx=2, pady=2)\n\n    def build_year_view(self, parent):\n        t = self.theme\n        for c in range(3):\n            parent.grid_columnconfigure(c, weight=1, uniform=\'year_col\')\n        for r in range(4):\n            parent.grid_rowconfigure(r, weight=1, uniform=\'year_row\', minsize=36)\n\n        for r in range(4):\n            for c in range(3):\n                idx = r * 3 + c - 1\n                y = self.year_base + idx\n                bg = t[\'cell_bg\']\n                fg = t[\'cell_fg\'] if 0 <= idx <= 9 else "#bdc3c7"\n                if y == datetime.now().year:\n                    bg = t[\'hl_per\']\n                btn = self.make_cal_button(\n                    parent,\n                    text=f"{y}년",\n                    bg=bg,\n                    fg=fg,\n                    command=lambda year=y: self.select_year(year)\n                )\n                btn.grid(row=r, column=c, sticky=\'nsew\', padx=2, pady=2)\n\n    def build_content(self, parent):\n        t = self.theme\n        content_f = tk.Frame(parent, bg=t[\'cell_bg\'])\n        content_f.pack(fill=\'both\', expand=True, padx=5, pady=5)\n        content_f.grid_columnconfigure(0, weight=1)\n        content_f.grid_rowconfigure(1, weight=1)\n\n        if self.mode == "day":\n            self.build_day_view(content_f)\n        elif self.mode == "month":\n            self.build_month_view(content_f)\n        elif self.mode == "year":\n            self.build_year_view(content_f)\n\n    def render(self):\n        if getattr(self, "_rendering", False):\n            return\n\n        self._rendering = True\n        old_frame = self.main_frame\n\n        try:\n            # 이미 표시 중인 달력은 월 이동 중 창 크기를 먼저 고정하여 아래쪽 물결/리사이즈를 방지\n            if old_frame is not None:\n                try:\n                    self.update_idletasks()\n                    w = max(self.winfo_width(), self._fixed_width)\n                    h = max(self.winfo_height(), self._fixed_height)\n                    self._fixed_width = w\n                    self._fixed_height = h\n                    self.geometry(f"{w}x{h}+{self.winfo_x()}+{self.winfo_y()}")\n                except Exception:\n                    pass\n            else:\n                try:\n                    self.geometry(f"{self._fixed_width}x{self._fixed_height}")\n                except Exception:\n                    pass\n\n            new_frame = tk.Frame(self, bg=self.theme[\'bg\'])\n            new_frame.pack_propagate(False)\n\n            self.build_header(new_frame)\n            self.build_content(new_frame)\n\n            # 새 화면을 모두 만든 뒤 한 번에 교체\n            if old_frame is not None:\n                try:\n                    old_frame.pack_forget()\n                except Exception:\n                    pass\n\n            new_frame.pack(fill="both", expand=True)\n            self.main_frame = new_frame\n\n            if old_frame is not None:\n                try:\n                    old_frame.destroy()\n                except Exception:\n                    pass\n\n            try:\n                self.update_idletasks()\n            except Exception:\n                pass\n\n        finally:\n            self._rendering = False\n\n    def prev_action(self):\n        if self.mode == "day":\n            first = self.current_date.replace(day=1)\n            self.current_date = first - timedelta(days=1)\n        elif self.mode == "month":\n            self.current_date = self.current_date.replace(year=self.current_date.year - 1)\n        elif self.mode == "year":\n            self.year_base -= 10\n        self.render()\n\n    def next_action(self):\n        if self.mode == "day":\n            last_day = calendar.monthrange(self.current_date.year, self.current_date.month)[1]\n            last = self.current_date.replace(day=last_day)\n            self.current_date = last + timedelta(days=1)\n        elif self.mode == "month":\n            self.current_date = self.current_date.replace(year=self.current_date.year + 1)\n        elif self.mode == "year":\n            self.year_base += 10\n        self.render()\n\n    def zoom_out(self):\n        if self.mode == "day":\n            self.mode = "month"\n        elif self.mode == "month":\n            self.mode = "year"\n            self.year_base = self.current_date.year // 10 * 10\n        self.render()\n\n    def select_year(self, year):\n        self.current_date = self.current_date.replace(year=year)\n        self.mode = "month"\n        self.render()\n\n    def select_month(self, month):\n        self.current_date = self.current_date.replace(month=month)\n        self.mode = "day"\n        self.render()\n\n    def select_date(self, date):\n        self.command(date)\n        self.destroy()\n\n\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step54_smooth_calendar_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def replace_modern_calendar(text: str):
    start = text.find("class ModernCalendar(tk.Toplevel):")
    if start == -1:
        raise RuntimeError("ModernCalendar 클래스를 찾지 못했습니다.")

    # 다음 클래스 시작점을 기준으로 교체. 현재 구조에서는 CustomSlider가 바로 다음 클래스입니다.
    end_candidates = []
    for marker in [
        "\nclass CustomSlider",
        "\nclass LoginWindow",
        "\nclass TimetableApp",
    ]:
        pos = text.find(marker, start + 10)
        if pos != -1:
            end_candidates.append(pos)

    if not end_candidates:
        raise RuntimeError("ModernCalendar 클래스 끝 위치를 찾지 못했습니다.")

    end = min(end_candidates)
    return text[:start] + NEW_CALENDAR_CLASS + text[end:]


def main():
    print("==============================================")
    print("Step54 smooth calendar month switch")
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
        text = replace_modern_calendar(text)
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
        print("[완료] Step54 달력 월 이동 렌더링 개선 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("[변경 요약]")
    print("- 달력 날짜 화면을 항상 6주 행으로 고정")
    print("- 새 달력 화면을 먼저 구성한 뒤 한 번에 교체")
    print("- 월/연도 이동 중 팝업 크기 고정")
    print()
    print("실행:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 달력 클릭 후 ◀/▶ 월 이동 시 아래에서부터 물결치듯 채워지는 현상이 줄었는지")
    print("2. 월 이동 시 달력 팝업 높이가 흔들리지 않는지")
    print("3. 월 선택/연도 선택/날짜 선택 기능이 정상인지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

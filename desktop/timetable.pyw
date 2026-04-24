import sys
import os
import csv
import json
import ctypes
import threading
import re
import calendar
import io
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import tkinter.font as tkfont
import tkinter.simpledialog as simpledialog
from PIL import Image, ImageTk
import pystray
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


STICKER_CATEGORIES = [
    ("평가/상태", [("💙", "마음"), ("💯", "만점"), ("✅", "완료"), ("❎", "취소"), ("📊", "평가"), ("✏️", "필기"), ("📈", "상승"), ("👍", "좋음"), ("☑️", "확인"), ("📋", "체크")]),
    ("수업/활동", [("🎤", "발표"), ("📚", "수업"), ("📖", "읽기"), ("📝", "시험"), ("💻", "실습"), ("🧪", "실험"), ("🎯", "프로젝트"), ("🎵", "음악"), ("🎨", "미술"), ("⚽", "체육")]),
    ("행사/기타", [("⭐", "중요"), ("🏫", "학교"), ("🚫", "금지"), ("💡", "아이디어"), ("🎉", "행사"), ("✈️", "이동"), ("⏰", "시간"), ("🔥", "급함"), ("🍔", "점심"), ("❓", "확인필요")]),
    ("포인트/기호", [("📌", "핀"), ("🔔", "알림"), ("📣", "공지"), ("👑", "핵심"), ("💎", "포인트"), ("🍀", "행운"), ("🎯", "목표"), ("🏆", "성과"), ("🚩", "플래그"), ("🍎", "준비물")]),
]
ALL_STICKERS = {emoji for _, items in STICKER_CATEGORIES for emoji, _ in items}

# ==========================================
# Supabase 클라우드 연동 설정
# - 우선순위:
#   1) 환경변수 SUPABASE_URL / SUPABASE_KEY
#   2) 저장소 루트의 supabase_config.json
#   3) 코드에 직접 입력한 기본값
# - UI는 legacy 그대로 두고 데이터 참조만 Supabase-first로 사용합니다.
# ==========================================
DEFAULT_SUPABASE_URL = "https://fnbzrxzgynuxgwretwux.supabase.co"
DEFAULT_SUPABASE_KEY = "여기에_SUPABASE_KEY를_넣지_않아도_supabase_config_json을_우선_사용합니다"


def load_supabase_config_for_desktop():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()
    if url and key:
        return url, key

    candidate_paths = []
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidate_paths.extend([
            os.path.join(current_dir, "supabase_config.json"),
            os.path.join(os.path.dirname(current_dir), "supabase_config.json"),
            os.path.join(os.getcwd(), "supabase_config.json"),
        ])
    except Exception:
        pass

    for config_path in candidate_paths:
        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                url = str(data.get("SUPABASE_URL", "")).strip()
                key = str(data.get("SUPABASE_KEY", "")).strip()
                if url and key:
                    return url, key
        except Exception:
            pass

    if DEFAULT_SUPABASE_URL.startswith("https://") and "여기에" not in DEFAULT_SUPABASE_KEY:
        return DEFAULT_SUPABASE_URL, DEFAULT_SUPABASE_KEY

    return "", ""


SUPABASE_URL, SUPABASE_KEY = load_supabase_config_for_desktop()
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
REQUEST_VERIFY_SSL = False

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
HEADERS_UPSERT = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=representation"
}


def supabase_get_rows(table_name, *, select="*", extra_params=None, timeout=8):
    if not USE_SUPABASE:
        return []

    params = {"select": select}
    if extra_params:
        params.update(extra_params)

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}",
            headers=HEADERS,
            params=params,
            timeout=timeout,
            verify=REQUEST_VERIFY_SSL,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass

    return []
# ==========================================

class ModernCalendar(tk.Toplevel):
    def __init__(self, parent, theme, start_date, command):
        super().__init__(parent)
        self.overrideredirect(True)
        self.theme = theme
        self.current_date = start_date
        self.command = command
        self.mode = "day" 
        self.year_base = start_date.year // 10 * 10 
        
        self.configure(bg=self.theme['bg'], bd=1, relief="solid")
        self.bind("<FocusOut>", lambda e: self.destroy())
        
        self.main_frame = tk.Frame(self, bg=self.theme['bg'])
        self.main_frame.pack(fill="both", expand=True)
        
        self.render()
        self.focus_set()
        
    def render(self):
        for w in self.main_frame.winfo_children(): 
            w.destroy()
            
        t = self.theme
        header_f = tk.Frame(self.main_frame, bg=t['top'])
        header_f.pack(fill='x')
        
        tk.Button(header_f, text="◀", bd=0, bg=t['top'], fg=t.get('head_fg', 'white'), cursor="hand2", command=self.prev_action).pack(side='left', padx=5, pady=5)
        
        title_text = ""
        if self.mode == "day": 
            title_text = f"{self.current_date.year}년 {self.current_date.month}월"
        elif self.mode == "month": 
            title_text = f"{self.current_date.year}년"
        elif self.mode == "year": 
            title_text = f"{self.year_base} - {self.year_base + 9}"
        
        title_btn = tk.Button(header_f, text=title_text, bd=0, bg=t['top'], fg=t.get('head_fg', 'white'), font=('맑은 고딕', 10, 'bold'), cursor="hand2", command=self.zoom_out)
        title_btn.pack(side='left', expand=True)
        
        tk.Button(header_f, text="▶", bd=0, bg=t['top'], fg=t.get('head_fg', 'white'), cursor="hand2", command=self.next_action).pack(side='right', padx=5, pady=5)
        
        content_f = tk.Frame(self.main_frame, bg=t['cell_bg'])
        content_f.pack(fill='both', expand=True, padx=5, pady=5)
        
        if self.mode == "day":
            days_f = tk.Frame(content_f, bg=t['cell_bg'])
            days_f.pack(fill='x')
            days = ["일", "월", "화", "수", "목", "금", "토"]
            for i, d in enumerate(days):
                fg = "#e74c3c" if i==0 else "#3498db" if i==6 else t['cell_fg']
                tk.Label(days_f, text=d, bg=t['cell_bg'], fg=fg, width=4, font=('맑은 고딕', 8, 'bold')).grid(row=0, column=i, pady=(0, 5))
            
            dates_f = tk.Frame(content_f, bg=t['cell_bg'])
            dates_f.pack(fill='both', expand=True)
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdatescalendar(self.current_date.year, self.current_date.month)
            
            today = datetime.now().date()
            for r, week in enumerate(month_days):
                for c, d in enumerate(week):
                    fg = t['cell_fg']
                    if d.month != self.current_date.month: 
                        fg = "#bdc3c7"
                    elif c == 0: 
                        fg = "#e74c3c"
                    elif c == 6: 
                        fg = "#3498db"
                    
                    bg = t['cell_bg']
                    if d == today: 
                        bg = t['hl_per']
                        fg = "white" if t['name'] != '웜 파스텔' else 'black'
                    
                    btn = tk.Button(dates_f, text=str(d.day), bd=0, bg=bg, fg=fg, width=4, cursor="hand2", command=lambda date=d: self.select_date(date))
                    btn.grid(row=r, column=c, pady=2)
                    
        elif self.mode == "month":
            for r in range(4):
                for c in range(3):
                    m = r * 3 + c + 1
                    bg = t['cell_bg']
                    if self.current_date.year == datetime.now().year and m == datetime.now().month: 
                        bg = t['hl_per']
                    btn = tk.Button(content_f, text=f"{m}월", bd=0, bg=bg, fg=t['cell_fg'], width=8, height=2, cursor="hand2", command=lambda month=m: self.select_month(month))
                    btn.grid(row=r, column=c, padx=2, pady=2)
                    
        elif self.mode == "year":
            for r in range(4):
                for c in range(3):
                    idx = r * 3 + c - 1 
                    y = self.year_base + idx
                    bg = t['cell_bg']
                    fg = t['cell_fg'] if 0 <= idx <= 9 else "#bdc3c7"
                    if y == datetime.now().year: 
                        bg = t['hl_per']
                    btn = tk.Button(content_f, text=f"{y}년", bd=0, bg=bg, fg=fg, width=8, height=2, cursor="hand2", command=lambda year=y: self.select_year(year))
                    btn.grid(row=r, column=c, padx=2, pady=2)

    def prev_action(self):
        if self.mode == "day":
            first = self.current_date.replace(day=1)
            self.current_date = first - timedelta(days=1)
        elif self.mode == "month":
            self.current_date = self.current_date.replace(year=self.current_date.year - 1)
        elif self.mode == "year":
            self.year_base -= 10
        self.render()

    def next_action(self):
        if self.mode == "day":
            last_day = calendar.monthrange(self.current_date.year, self.current_date.month)[1]
            last = self.current_date.replace(day=last_day)
            self.current_date = last + timedelta(days=1)
        elif self.mode == "month":
            self.current_date = self.current_date.replace(year=self.current_date.year + 1)
        elif self.mode == "year":
            self.year_base += 10
        self.render()

    def zoom_out(self):
        if self.mode == "day": 
            self.mode = "month"
        elif self.mode == "month":
            self.mode = "year"
            self.year_base = self.current_date.year // 10 * 10
        self.render()

    def select_year(self, year):
        self.current_date = self.current_date.replace(year=year)
        self.mode = "month"
        self.render()

    def select_month(self, month):
        self.current_date = self.current_date.replace(month=month)
        self.mode = "day"
        self.render()

    def select_date(self, date):
        self.command(date)
        self.destroy()

class CustomSlider(tk.Canvas):
    def __init__(self, parent, width=60, height=24, bg='#1a252f', trough_color='#34495e', slider_color='white', command=None):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, bd=0)
        self.command = command
        self.val = 0.95
        self.trough_color = trough_color
        self.slider_color = slider_color
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<Configure>", lambda e: self.draw())
        self.draw()
        
    def set_colors(self, bg, trough_color, slider_color):
        self.configure(bg=bg)
        self.trough_color = trough_color
        self.slider_color = slider_color
        self.draw()
        
    def set(self, val): 
        self.val = max(0.3, min(1.0, val))
        self.draw()
        
    def draw(self):
        self.delete("all")
        w, h = int(self.cget('width')), int(self.cget('height'))
        trough_h = 4
        self.create_rectangle(5, h//2 - trough_h//2, w-5, h//2 + trough_h//2, fill=self.trough_color, outline="")
        x = 5 + (self.val - 0.3) / 0.7 * (w - 10)
        slider_w = 6 
        self.create_rectangle(x - slider_w//2, h//2 - 8, x + slider_w//2, h//2 + 8, fill=self.slider_color, outline="")
       
    def on_click(self, event): 
        self.update_val(event.x)
        
    def on_drag(self, event): 
        self.update_val(event.x)
        
    def update_val(self, x):
        w = int(self.cget('width'))
        ratio = (x - 5) / (w - 10)
        self.val = 0.3 + max(0.0, min(1.0, ratio)) * 0.7
        self.draw()
        if self.command: 
            self.command(self.val)

class TimetableWidget:
    def get_active_theme(self):
        themes = getattr(self, 'themes', None)
        if not themes:
            return {
                'input_bg': '#ffffff', 'cell_fg': '#1f2937', 'accent_soft': '#eaf2ff',
                'accent': '#1d4ed8', 'muted_fg': '#7c8594', 'panel_bg': '#ffffff',
                'cell_bg': '#ffffff', 'grid': '#d0d7de', 'panel_border': '#d0d7de',
                'hover_btn': '#eef3fb'
            }
        idx = getattr(self, 'current_theme_idx', getattr(self, 'theme_index', 0))
        try:
            idx = int(idx)
        except Exception:
            idx = 0
        idx = max(0, min(idx, len(themes)-1))
        return themes[idx]

    def create_themed_menu(self, parent=None, font=None):
        parent = parent or self.root
        t = self.get_active_theme()
        menu = tk.Menu(
            parent,
            tearoff=0,
            font=font or ('맑은 고딕', 10),
            bg=t.get('input_bg', '#ffffff'),
            fg=t.get('cell_fg', '#1f2937'),
            activebackground=t.get('accent_soft', '#eaf2ff'),
            activeforeground=t.get('accent', '#1d4ed8'),
            disabledforeground=t.get('muted_fg', '#7c8594'),
            relief='solid',
            bd=1,
            borderwidth=1,
            cursor='hand2'
        )
        try:
            menu.configure(
                selectcolor=t.get('accent', '#2563eb'),
                activeborderwidth=0
            )
        except Exception:
            pass
        return menu

    def add_menu_header(self, menu, title):
        t = self.get_active_theme()
        menu.add_command(label=f"  {title}", state='disabled', foreground=t.get('muted_fg', '#667085'))
        menu.add_separator()

    def add_color_command(self, menu, name, code, command):
        t = self.get_active_theme()
        if code:
            label = f"●  {name}"
            menu.add_command(label=label, command=command, foreground=code, activeforeground=code)
        else:
            menu.add_command(label="○  기본색으로", command=command, foreground=t.get('cell_fg', '#1f2937'))

    def build_sticker_menu(self, parent_menu, apply_func):
        sticker_menu = self.create_themed_menu(parent_menu, font=('Segoe UI Emoji', 10))
        for cat_name, items in STICKER_CATEGORIES:
            cat_menu = self.create_themed_menu(sticker_menu, font=('Segoe UI Emoji', 10))
            self.add_menu_header(cat_menu, cat_name)
            for emoji_char, desc in items:
                cat_menu.add_command(label=f"{emoji_char} {desc}", command=lambda e=emoji_char: apply_func(e))
            sticker_menu.add_cascade(label=cat_name, menu=cat_menu)
        return sticker_menu

    def bind_context_popup(self, widget, callback):
        for seq in ("<Button-3>", "<ButtonRelease-3>", "<Button-2>", "<Control-1>"):
            try:
                widget.bind(seq, callback, add='+')
            except Exception:
                pass

    def style_popup_window(self, win):
        t = self.get_active_theme()
        win.configure(bg=t.get('panel_bg', t['cell_bg']), bd=1, relief='solid')
        try:
            win.attributes('-topmost', True)
        except Exception:
            pass

    def format_sticker_text(self, clean_text, sticker):
        clean_text = (clean_text or '').strip()
        if not clean_text:
            return sticker
        first_token, *rest = clean_text.split(maxsplit=1)
        rest_text = rest[0] if rest else ''
        if first_token == sticker:
            return clean_text
        if first_token in ALL_STICKERS:
            return f"{sticker} {rest_text}".strip()
        return f"{sticker} {clean_text}".strip()

    def _build_sticker_palette(self, title, apply_func, x, y):
        if hasattr(self, 'sticker_pal') and self.sticker_pal.winfo_exists():
            self.sticker_pal.destroy()

        self.sticker_pal = tk.Toplevel(self.root)
        self.sticker_pal.overrideredirect(True)
        self.style_popup_window(self.sticker_pal)
        self.sticker_pal.geometry(f"+{x}+{y}")

        t = self.get_active_theme()
        panel_bg = t.get('panel_bg', t['cell_bg'])
        border = t.get('panel_border', t['grid'])
        accent = t.get('accent', '#2563eb')
        muted = t.get('muted_fg', '#667085')
        cell_fg = t.get('cell_fg', '#1f2937')
        hover = t.get('hover_btn', '#eef3fb')

        outer = tk.Frame(self.sticker_pal, bg=panel_bg, bd=1, relief='solid', highlightthickness=1, highlightbackground=border)
        outer.pack(fill='both', expand=True)

        header = tk.Frame(outer, bg=panel_bg)
        header.pack(fill='x', padx=10, pady=(10, 4))
        tk.Label(header, text="✨", bg=panel_bg, fg=accent, font=('Segoe UI Emoji', 12)).pack(side='left')
        tk.Label(header, text=title, bg=panel_bg, fg=cell_fg, font=('맑은 고딕', 10, 'bold')).pack(side='left', padx=(6, 0))
        tk.Label(outer, text="스티커를 고르면 내용 앞에 깔끔하게 붙습니다.", bg=panel_bg, fg=muted, font=('맑은 고딕', 8)).pack(anchor='w', padx=12, pady=(0, 8))

        body = tk.Frame(outer, bg=panel_bg)
        body.pack(fill='both', expand=True, padx=10, pady=(0, 8))

        for cat_name, items in STICKER_CATEGORIES:
            sec = tk.Frame(body, bg=panel_bg)
            sec.pack(fill='x', pady=(0, 8))
            tk.Label(sec, text=cat_name, bg=panel_bg, fg=muted, font=('맑은 고딕', 8, 'bold')).pack(anchor='w', pady=(0, 4))
            grid = tk.Frame(sec, bg=panel_bg)
            grid.pack(fill='x')
            for col in range(5):
                grid.grid_columnconfigure(col, weight=1)
            for idx, (emoji, label) in enumerate(items):
                r, c = divmod(idx, 5)
                chip = tk.Label(grid, text=f"{emoji} {label}", bg=t.get('input_bg', '#fbfcfe'), fg=cell_fg, font=('맑은 고딕', 9), bd=1, relief='solid', padx=8, pady=5, cursor='hand2')
                chip.grid(row=r, column=c, padx=3, pady=3, sticky='ew')
                chip.bind('<Enter>', lambda e, w=chip: w.config(bg=hover))
                chip.bind('<Leave>', lambda e, w=chip, base=t.get('input_bg', '#fbfcfe'): w.config(bg=base))
                chip.bind('<Button-1>', lambda e, em=emoji: (apply_func(em), self.close_sticker_palette()))

        footer = tk.Frame(outer, bg=panel_bg)
        footer.pack(fill='x', padx=10, pady=(0, 10))
        close_btn = tk.Button(footer, text="닫기", command=self.close_sticker_palette, bd=0, bg=t.get('hover_btn', '#eef3fb'), fg=cell_fg, activebackground=hover, activeforeground=cell_fg, padx=10, pady=4, cursor='hand2')
        close_btn.pack(side='right')

        def on_global_click(event):
            if not self.sticker_pal.winfo_exists():
                return
            cx, cy = event.x_root, event.y_root
            x0 = self.sticker_pal.winfo_rootx()
            y0 = self.sticker_pal.winfo_rooty()
            x1 = x0 + self.sticker_pal.winfo_width()
            y1 = y0 + self.sticker_pal.winfo_height()
            if not (x0 <= cx <= x1 and y0 <= cy <= y1):
                self.close_sticker_palette()

        self.sticker_pal.update_idletasks()
        self.sticker_pal.grab_set()
        self.sticker_pal.bind('<Button-1>', on_global_click)
        self.sticker_pal.focus_set()

    def close_sticker_palette(self):
        if hasattr(self, 'sticker_pal') and self.sticker_pal.winfo_exists():
            try:
                self.sticker_pal.grab_release()
            except Exception:
                pass
            self.sticker_pal.destroy()

    def __init__(self, root):
        self.root = root
        
        self.themes = [
            { 'name': '윈도우 11 라이트', 'bg': '#f5f7fb', 'top': '#eef3fb', 'grid': '#d8dee9', 'head_bg': '#e7eef9', 'head_fg': '#1f2937', 'per_bg': '#dde6f5', 'per_fg': '#243042', 'cell_bg': '#ffffff', 'lunch_bg': '#f3f6fb', 'cell_fg': '#1f2937', 'hl_per': '#2563eb', 'hl_cell': '#e8f0ff', 'titlebar_bg': '#f8fbff', 'hover_btn': '#e5edf9', 'hover_title': '#eef4ff', 'hover_cell': '#f4f8ff', 'hover_lunch': '#eaf1fb',
              'acad_per_bg': '#6d5bd0', 'acad_per_fg': 'white', 'acad_cell_bg': '#f1efff', 'acad_cell_fg': '#4338ca', 'panel_bg': '#ffffff', 'panel_border': '#d5dce8', 'input_bg': '#fbfcfe', 'muted_fg': '#667085', 'accent': '#2563eb', 'accent_soft': '#dbeafe', 'danger': '#e81123', 'shadow': '#eef2f7', 'accent_hover': '#1d4ed8', 'title_btn_fg': '#374151', 'subtle_btn_fg': '#334155' },
            { 'name': '모던 다크', 'bg': '#1f2430', 'top': '#252b38', 'grid': '#394150', 'head_bg': '#2b3342', 'head_fg': '#eef2f7', 'per_bg': '#4a5568', 'per_fg': 'white', 'cell_bg': '#2a3140', 'lunch_bg': '#31394a', 'cell_fg': '#eef2f7', 'hl_per': '#60a5fa', 'hl_cell': '#23344f', 'titlebar_bg': '#202632', 'hover_btn': '#30384a', 'hover_title': '#2c3445', 'hover_cell': '#334155', 'hover_lunch': '#394456',
              'acad_per_bg': '#8b5cf6', 'acad_per_fg': 'white', 'acad_cell_bg': '#31294a', 'acad_cell_fg': '#ddd6fe', 'panel_bg': '#252b38', 'panel_border': '#3b4252', 'input_bg': '#1f2430', 'muted_fg': '#a8b3c5', 'accent': '#60a5fa', 'accent_soft': '#1e3a5f', 'danger': '#ff5f73', 'shadow': '#1a1f29', 'accent_hover': '#3b82f6', 'title_btn_fg': '#e5e7eb', 'subtle_btn_fg': '#d1d5db' },
            { 'name': '웜 파스텔', 'bg': '#fdf8f2', 'top': '#f5ead9', 'grid': '#e7dccf', 'head_bg': '#efe2d2', 'head_fg': '#3f3a34', 'per_bg': '#eadfce', 'per_fg': '#3f3a34', 'cell_bg': '#fffdfb', 'lunch_bg': '#f8efe4', 'cell_fg': '#4a4a4a', 'hl_per': '#e88f8f', 'hl_cell': '#fff0ea', 'titlebar_bg': '#fbf4ea', 'hover_btn': '#f3e7d7', 'hover_title': '#f7edde', 'hover_cell': '#fff7f0', 'hover_lunch': '#f4eadf',
              'acad_per_bg': '#f29e73', 'acad_per_fg': '#3b322c', 'acad_cell_bg': '#fff1e8', 'acad_cell_fg': '#7c4a2d', 'panel_bg': '#fffdfa', 'panel_border': '#e5d8c9', 'input_bg': '#fffdf9', 'muted_fg': '#7b6f64', 'accent': '#c86b6b', 'accent_soft': '#fde6e6', 'danger': '#d94a5a', 'shadow': '#f2e8dc', 'accent_hover': '#b45353', 'title_btn_fg': '#4b3f36', 'subtle_btn_fg': '#6b5b4c' },
            { 'name': '클래식 블루', 'bg': '#edf4fc', 'top': '#dce9f8', 'grid': '#cad9ec', 'head_bg': '#cfe1f7', 'head_fg': '#1f3655', 'per_bg': '#bdd2ec', 'per_fg': '#1f3655', 'cell_bg': '#ffffff', 'lunch_bg': '#eef5fd', 'cell_fg': '#203247', 'hl_per': '#2f6fed', 'hl_cell': '#e8f0ff', 'titlebar_bg': '#f5f9ff', 'hover_btn': '#d8e6f8', 'hover_title': '#e7f0fb', 'hover_cell': '#f6faff', 'hover_lunch': '#e8f1fc',
              'acad_per_bg': '#0ea5a4', 'acad_per_fg': 'white', 'acad_cell_bg': '#e8fbfb', 'acad_cell_fg': '#0f766e', 'panel_bg': '#ffffff', 'panel_border': '#ccd9e8', 'input_bg': '#fbfdff', 'muted_fg': '#5e738c', 'accent': '#2f6fed', 'accent_soft': '#dbeafe', 'danger': '#df3f4f', 'shadow': '#e8f0f7', 'accent_hover': '#245ed6', 'title_btn_fg': '#29486b', 'subtle_btn_fg': '#33526f' },
            { 'name': '포레스트', 'bg': '#eef4f0', 'top': '#ddeae2', 'grid': '#cedcd4', 'head_bg': '#d5e5dc', 'head_fg': '#20362c', 'per_bg': '#bcd1c3', 'per_fg': '#20362c', 'cell_bg': '#ffffff', 'lunch_bg': '#edf5f0', 'cell_fg': '#20362c', 'hl_per': '#2f855a', 'hl_cell': '#e6f4ea', 'titlebar_bg': '#f5faf7', 'hover_btn': '#d8e7de', 'hover_title': '#e7f2eb', 'hover_cell': '#f7fcf8', 'hover_lunch': '#e7f0ea',
              'acad_per_bg': '#b45309', 'acad_per_fg': 'white', 'acad_cell_bg': '#fff5e8', 'acad_cell_fg': '#92400e', 'panel_bg': '#ffffff', 'panel_border': '#cfdccf', 'input_bg': '#fbfefc', 'muted_fg': '#5f7467', 'accent': '#2f855a', 'accent_soft': '#dcfce7', 'danger': '#d33c4a', 'shadow': '#e5efe9', 'accent_hover': '#256b47', 'title_btn_fg': '#244234', 'subtle_btn_fg': '#355646' },
            { 'name': '모노톤', 'bg': '#f3f4f6', 'top': '#e7e9ee', 'grid': '#d7dbe2', 'head_bg': '#e1e5eb', 'head_fg': '#1f2937', 'per_bg': '#d2d8e1', 'per_fg': '#1f2937', 'cell_bg': '#ffffff', 'lunch_bg': '#f1f3f6', 'cell_fg': '#111827', 'hl_per': '#111827', 'hl_cell': '#e9edf3', 'titlebar_bg': '#f8fafc', 'hover_btn': '#e5e7eb', 'hover_title': '#eef1f5', 'hover_cell': '#f8fafc', 'hover_lunch': '#eceff3',
              'acad_per_bg': '#4b5563', 'acad_per_fg': 'white', 'acad_cell_bg': '#f3f4f6', 'acad_cell_fg': '#111827', 'panel_bg': '#ffffff', 'panel_border': '#d6d9df', 'input_bg': '#fbfbfc', 'muted_fg': '#6b7280', 'accent': '#374151', 'accent_soft': '#e5e7eb', 'danger': '#dc2626', 'shadow': '#eceef2', 'accent_hover': '#111827', 'title_btn_fg': '#1f2937', 'subtle_btn_fg': '#374151' }
        ]
        
        
        self.root.overrideredirect(True)
        self._offset_x = 0
        self._offset_y = 0
        self.click_timer = None
        self.selected_memo_indices = set()
        self.last_clicked_idx = None
        self.memo_line_map = {} 
        self.dynamic_fonts = {} 
        
        self.memo_group_collapsed = {'important': False, 'general': False, 'strike': False}
        
        self.is_locked = False
        self.is_topmost = False

        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # 차세대 저장소/설치 구조 자동 탐색
        # - 개발 중 실행: my-timetable-next/desktop/timetable.pyw
        #   => project_root = my-timetable-next
        # - 설치 후 실행: {app}/MyTimetableNext.exe
        #   => project_root = {app}
        # - 다른 위치에서 실행해도 cwd 후보를 함께 확인
        candidate_roots = []

        try:
            candidate_roots.append(self.base_dir)
            candidate_roots.append(os.path.dirname(self.base_dir))
            candidate_roots.append(os.getcwd())
            candidate_roots.append(os.path.dirname(os.getcwd()))
        except Exception:
            pass

        # 중복 제거
        unique_roots = []
        for root_candidate in candidate_roots:
            if root_candidate and root_candidate not in unique_roots:
                unique_roots.append(root_candidate)

        self.project_root = self.base_dir
        for root_candidate in unique_roots:
            if os.path.exists(os.path.join(root_candidate, 'data', 'timetable.csv')):
                self.project_root = root_candidate
                break

        self.data_dir = os.path.join(self.project_root, 'data')
        self.assets_dir = os.path.join(self.project_root, 'assets')

        appdata_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'TeacherTimetable')
        if not os.path.exists(appdata_dir): 
            try: 
                os.makedirs(appdata_dir)
            except: pass
            
        self.config_file = os.path.join(appdata_dir, 'settings.txt')
        self.memos_file = os.path.join(appdata_dir, 'memos.json')
        self.custom_data_file = os.path.join(appdata_dir, 'custom_data.json')

        self.icon_path = os.path.join(self.assets_dir, 'logo.ico')
        if os.path.exists(self.icon_path): 
            self.root.iconbitmap(self.icon_path)

        self.root.after(100, self.set_appwindow)
        self.setup_tray()

        self.teachers_data = {}
        self.memos_data = {}
        self.custom_data = {} 
        self.academic_schedule = {} 
        self.week_offset = 0

        self.history = []
        self.history_idx = -1

        self.period_times = [
            ("학사일정", "", ""),
            ("조회", "07:40", "08:00"), ("1교시", "08:00", "08:50"), ("2교시", "09:00", "09:50"),
            ("3교시", "10:00", "10:50"), ("4교시", "11:00", "11:50"), ("점심", "11:50", "12:40"),
            ("5교시", "12:40", "13:30"), ("6교시", "13:40", "14:30"), ("7교시", "14:40", "15:30"),
            ("8교시", "16:00", "16:50"), ("9교시", "17:00", "17:50")
        ]
        self.days = ["월", "화", "수", "목", "금"]
        self.cells = {} 

        self.load_settings()
        self.setup_ttk_styles()
        
        ff = self.settings.get('font_family', '맑은 고딕')
        
        self.memo_font_size = self.settings.get('memo_font_size', 9)
        self.memo_spacing = self.settings.get('memo_spacing', 1)
        self.memo_extra_height = self.settings.get('memo_extra_height', 0)

        self.font_title = tkfont.Font(family=ff, size=9, weight='bold')
        self.font_head = tkfont.Font(family=ff, size=10, weight='bold')
        self.font_period = tkfont.Font(family=ff, size=8, weight='bold')
        self.font_cell = tkfont.Font(family=ff, size=10, weight='bold')
        self.font_cell_strike = tkfont.Font(family=ff, size=10, weight='bold', overstrike=1)
        self.font_timestamp = tkfont.Font(family=ff, size=7, weight='normal')
        
        self.font_memo = tkfont.Font(family=ff, size=self.memo_font_size, weight='bold')
        self.font_memo_ts = tkfont.Font(family=ff, size=max(6, self.memo_font_size - 2), weight='normal')
        self.font_memo_icon = tkfont.Font(family=ff, size=self.memo_font_size, weight='normal')
        
        self.font_academic_cells = {}
        for c in range(1, 6):
            self.font_academic_cells[c] = tkfont.Font(family=ff, size=10, weight='bold')

        self.load_academic_csv()
        self.load_csv_data()
        self.load_memos()
        self.load_custom_data()
        self.push_history() 
        
        self.root.attributes('-topmost', self.is_topmost)
        self.root.attributes('-alpha', self.settings.get('alpha', 0.95))
        
        self.root.bind("<Control-f>", self.search_memo)
        self.root.bind("<Control-F>", self.search_memo)
        
        if self.settings.get('auto_login') and self.settings.get('logged_in_user'):
            self.verify_and_load_user(self.settings['logged_in_user'])
            self.start_main_app()
        else:
            self.build_login_ui()

    def _load_img(self, name, size):
        p = os.path.join(self.assets_dir, name)
        if os.path.exists(p):
            try:
                img = Image.open(p).resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except:
                pass
        return None

    def load_images(self):
        self.edit_img = self._load_img('image_7e23c6.png', (14, 14))
        self.del_img = self._load_img('image_7e23e0.png', (14, 14))
        self.title_logo_img = None
        png_logo = os.path.join(self.assets_dir, 'logo.png')
        ico_logo = os.path.join(self.assets_dir, 'logo.ico')
        try:
            if os.path.exists(png_logo):
                img = Image.open(png_logo).convert('RGBA').resize((16, 16), Image.Resampling.LANCZOS)
                self.title_logo_img = ImageTk.PhotoImage(img)
            elif os.path.exists(ico_logo):
                img = Image.open(ico_logo).convert('RGBA').resize((16, 16), Image.Resampling.LANCZOS)
                self.title_logo_img = ImageTk.PhotoImage(img)
        except Exception:
            self.title_logo_img = None
    # ==========================================
    # 💡 비동기 DB 작업 헬퍼 (버벅임 해결 핵심)
    # ==========================================
    def _async_db_task(self, method, url, headers=None, json_data=None):
        if headers is None:
            headers = HEADERS
        def task():
            try:
                if method == 'POST':
                    requests.post(url, headers=headers, json=json_data, verify=False)
                elif method == 'PATCH':
                    requests.patch(url, headers=headers, json=json_data, verify=False)
                elif method == 'DELETE':
                    requests.delete(url, headers=headers, verify=False)
            except: 
                pass
        threading.Thread(target=task, daemon=True).start()

    # ==========================================
    # 💡 Undo / Redo 기능
    # ==========================================
    def push_history(self):
        state = {
            'custom': json.loads(json.dumps(self.custom_data)),
            'memos': json.loads(json.dumps(self.memos_data))
        }
        
        if self.history_idx >= 0:
            if self.history[self.history_idx] == state:
                return
                
        self.history = self.history[:self.history_idx + 1]
        self.history.append(state)
        self.history_idx += 1
        
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_idx -= 1

    def undo_action(self):
        if self.history_idx > 0:
            self.history_idx -= 1
            self.restore_history()

    def redo_action(self):
        if self.history_idx < len(self.history) - 1:
            self.history_idx += 1
            self.restore_history()

    def restore_history(self):
        state = self.history[self.history_idx]
        self.custom_data = json.loads(json.dumps(state['custom']))
        self.memos_data = json.loads(json.dumps(state['memos']))
        self.refresh_schedule_display()
        self.refresh_memo_list()
        self.save_custom_data()
        self.save_memos()

    # ==========================================
    # 💡 1. 윈도우 조작 및 시스템 설정
    # ==========================================

    def apply_native_window_style(self):
        if sys.platform != 'win32':
            return
        try:
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            value = ctypes.c_int(DWMWCP_ROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(value), ctypes.sizeof(value))
        except:
            pass

    def setup_ttk_styles(self):
        try:
            self.ttk_style = ttk.Style()
            if 'vista' in self.ttk_style.theme_names():
                self.ttk_style.theme_use('vista')
        except:
            self.ttk_style = ttk.Style()

    def style_toolbar_button(self, button, variant='neutral'):
        t = self.themes[self.current_theme_idx]
        is_menubutton = isinstance(button, tk.Menubutton)
        common = dict(relief='flat', bd=0, cursor='hand2')
        variant_map = {
            'calendar': {'bg': '#f5f0ff', 'fg': '#5b3cc4', 'activebackground': '#ede5ff', 'activeforeground': '#4c31a6'},
            'memo': {'bg': '#eef6ff', 'fg': '#0f5cc0', 'activebackground': '#deeeff', 'activeforeground': '#0b4ea8'},
            'lookup': {'bg': '#fff7ea', 'fg': '#9a5b00', 'activebackground': '#ffefd5', 'activeforeground': '#7c4800'},
            'extra': {'bg': '#f0f4ff', 'fg': '#3347b4', 'activebackground': '#e3ebff', 'activeforeground': '#25389d'},
            'accent': {'bg': t.get('accent', t['hl_per']), 'fg': 'white', 'activebackground': t.get('accent_hover', t.get('accent', t['hl_per'])), 'activeforeground': 'white'},
            'neutral': {'bg': t.get('input_bg', t['cell_bg']), 'fg': t.get('head_fg', t['cell_fg']), 'activebackground': t.get('hover_btn', t['top']), 'activeforeground': t.get('head_fg', t['cell_fg'])},
            'subtle': {'bg': t.get('top', t['bg']), 'fg': t.get('head_fg', t['cell_fg']), 'activebackground': t.get('hover_btn', t['top']), 'activeforeground': t.get('head_fg', t['cell_fg'])},
        }
        palette = variant_map.get(variant, variant_map['neutral'])
        opts = dict(
            bg=palette['bg'],
            fg=palette['fg'],
            activebackground=palette['activebackground'],
            activeforeground=palette['activeforeground'],
            highlightthickness=1,
            highlightbackground=t.get('panel_border', t['grid']),
            highlightcolor=t.get('accent', t['hl_per']),
            padx=7,
            pady=2,
        )
        if variant == 'accent':
            opts['highlightthickness'] = 0
            opts['padx'] = 9
            opts['pady'] = 3
        if not is_menubutton:
            opts['overrelief'] = 'flat'
        try:
            button.configure(**common, **opts)
            button._base_bg = opts.get('bg')
            button._base_fg = opts.get('fg')
            button._hover_bg = opts.get('activebackground', opts.get('bg'))
            button._hover_fg = opts.get('activeforeground', opts.get('fg'))
        except tk.TclError:
            opts.pop('overrelief', None)
            try:
                button.configure(**common, **opts)
                button._base_bg = opts.get('bg')
                button._base_fg = opts.get('fg')
                button._hover_bg = opts.get('activebackground', opts.get('bg'))
                button._hover_fg = opts.get('activeforeground', opts.get('fg'))
            except tk.TclError:
                opts.pop('highlightbackground', None)
                opts.pop('highlightcolor', None)
                button.configure(**common, **opts)
                button._base_bg = opts.get('bg')
                button._base_fg = opts.get('fg')
                button._hover_bg = opts.get('activebackground', opts.get('bg'))
                button._hover_fg = opts.get('activeforeground', opts.get('fg'))

    def style_toggle_chip(self, frame, button, variant='neutral', active=False):
        t = self.themes[self.current_theme_idx]
        colors = {
            'calendar': ('#f5f0ff', '#5b3cc4', '#6d5bd0'),
            'memo': ('#eef6ff', '#0f5cc0', '#2563eb'),
            'lookup': ('#fff7ea', '#9a5b00', '#d97706'),
            'extra': ('#f0f4ff', '#3347b4', '#4f46e5'),
            'today': (t.get('accent_soft', t['hl_cell']), t.get('accent', t['hl_per']), t.get('accent', t['hl_per'])),
            'neutral': (t.get('input_bg', t['cell_bg']), t.get('head_fg', t['cell_fg']), t.get('panel_border', t['grid']))
        }
        bg, fg, line = colors.get(variant, colors['neutral'])
        frame.configure(bg=line if active else t.get('panel_border', t['grid']), height=1)
        button.configure(bg=bg, fg=fg, activebackground=bg, activeforeground=fg)
        button._base_bg = bg
        button._base_fg = fg
        button._hover_bg = bg
        button._hover_fg = fg

    def apply_combobox_style(self):
        if not hasattr(self, 'teacher_cb'):
            return
        t = self.themes[self.current_theme_idx]
        fg = t.get('head_fg', t['cell_fg'])
        bg = t.get('input_bg', t['cell_bg'])
        try:
            style = getattr(self, 'ttk_style', ttk.Style())
            style.configure(
                'Modern.TCombobox',
                fieldbackground=bg,
                background=bg,
                foreground=fg,
                bordercolor=t.get('panel_border', t['grid']),
                lightcolor=t.get('panel_border', t['grid']),
                darkcolor=t.get('panel_border', t['grid']),
                arrowcolor=fg,
                selectbackground=t.get('accent_soft', t['hl_cell']),
                selectforeground=fg,
                padding=(8, 4, 6, 4),
                relief='flat'
            )
            style.map('Modern.TCombobox',
                fieldbackground=[('readonly', bg), ('disabled', bg)],
                background=[('readonly', bg), ('disabled', bg)],
                foreground=[('readonly', fg), ('disabled', t.get('muted_fg', fg))],
                arrowcolor=[('readonly', fg)],
                selectbackground=[('readonly', t.get('accent_soft', t['hl_cell']))],
                selectforeground=[('readonly', fg)]
            )
            self.teacher_cb.configure(style='Modern.TCombobox', font=self.font_title)
        except Exception:
            pass

    def get_hover_cell_style(self, widget):
        t = self.themes[self.current_theme_idx]
        bg = widget.cget('bg')
        lunch_like = {t.get('lunch_bg'), t.get('acad_cell_bg'), t.get('hl_cell')}
        if bg in lunch_like:
            return t.get('hover_lunch', t['lunch_bg']), t['cell_fg']
        return t.get('hover_cell', t['cell_bg']), t['cell_fg']

    def style_caption_button(self, button, role='normal'):
        t = self.themes[self.current_theme_idx]
        base_fg = t.get('title_btn_fg', t.get('head_fg', 'white'))
        hover_bg = '#e81123' if role == 'close' else t.get('hover_title', t['head_bg'])
        hover_fg = 'white' if role == 'close' else base_fg
        button.configure(
            bg=t['titlebar_bg'],
            fg=base_fg,
            activebackground=hover_bg,
            activeforeground=hover_fg,
            relief='flat',
            highlightthickness=0,
            padx=0,
            pady=0,
            takefocus=0,
            cursor='hand2'
        )
        button._base_bg = t['titlebar_bg']
        button._base_fg = base_fg
        button._hover_bg = hover_bg
        button._hover_fg = hover_fg

    def bind_caption_hover(self, widget, role='normal'):
        def on_enter(e):
            t = self.themes[self.current_theme_idx]
            if role == 'close':
                e.widget.config(bg='#e81123', fg='white')
            else:
                e.widget.config(bg=t.get('hover_title', t['head_bg']), fg=t.get('head_fg', 'white'))

        def on_leave(e):
            t = self.themes[self.current_theme_idx]
            e.widget.config(bg=t['titlebar_bg'], fg=t.get('head_fg', 'white'))

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)


    def update_toolbar_texts(self):
        compact = getattr(self, 'toolbar_compact_mode', False)
        very_compact = getattr(self, 'toolbar_very_compact', False)

        curr_txt = '오늘'
        cal_txt = '달력'
        memo_txt = '메모'
        zero_txt = '조회'
        extra_txt = '8·9'
        save_txt = '저장'
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
            self.save_btn.config(text=save_txt, width=4)
        if hasattr(self, 'settings_mb'):
            self.settings_mb.config(text=settings_txt, width=3 if very_compact else 4)
        if hasattr(self, 'teacher_cb'):
            self.teacher_cb.configure(width=7 if very_compact else (8 if compact else 10))
        if hasattr(self, 'alpha_lbl'):
            self.alpha_lbl.config(text='' if compact else '투명')
        if hasattr(self, 'alpha_scale'):
            self.alpha_scale.configure(width=34 if very_compact else (42 if compact else 52))
            self.alpha_scale.draw()

    def relayout_toolbar(self, event=None):
        if not hasattr(self, 'top_bar'):
            return

        width = self.root.winfo_width()
        compact = width < 1180
        very_compact = width < 980
        changed = (
            getattr(self, 'toolbar_compact_mode', None) != compact or
            getattr(self, 'toolbar_very_compact', None) != very_compact
        )
        self.toolbar_compact_mode = compact
        self.toolbar_very_compact = very_compact
        self.toolbar_stacked_mode = False

        for frame in [self.toolbar_row1, self.row1_left, self.row1_right]:
            for child in frame.winfo_children():
                try:
                    child.pack_forget()
                except Exception:
                    pass
            try:
                frame.pack_forget()
            except Exception:
                pass

        if changed:
            self.update_toolbar_texts()

        self.toolbar_row1.pack(fill='x')
        self.row1_left.pack(side='left', fill='x', expand=True)
        self.row1_right.pack(side='right', anchor='e')

        left_widgets = [
            self.teacher_cb, self.prev_btn, self.curr_btn_border, self.next_btn,
            self.left_sep1, self.cal_btn_border, self.memo_btn_border, self.zero_btn_border,
            self.extra_btn_border
        ]
        right_widgets = [self.alpha_lbl, self.alpha_scale, self.right_sep, self.save_btn, self.settings_mb]

        for w in left_widgets:
            padx = (0, 6)
            if w in [self.left_sep1]:
                padx = (4, 8)
            w.pack(in_=self.row1_left, side='left', padx=padx, pady=0)

        for w in right_widgets:
            if very_compact and w in [self.alpha_lbl]:
                continue
            padx = (0, 6)
            if w in [self.right_sep]:
                padx = (6, 8)
            w.pack(in_=self.row1_right, side='left', padx=padx, pady=0)

    def set_appwindow(self):
        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        style = style & ~0x00000080 | 0x00040000 
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
        self.root.withdraw()
        self.root.deiconify()
        self.apply_native_window_style()

    def setup_tray(self):
        if os.path.exists(self.icon_path): 
            image = Image.open(self.icon_path)
        else: 
            image = Image.new('RGB', (64, 64), color=(44, 62, 80))
            
        menu = pystray.Menu(
            pystray.MenuItem("시간표 보이기", self.show_window),
            pystray.MenuItem("시간표 숨기기", self.hide_window),
            pystray.MenuItem("프로그램 종료", self.close_app)
        )
        self.tray_icon = pystray.Icon("Timetable", image, "교사 시간표", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon, item): 
        self.root.after(0, self.root.deiconify)
        
    def hide_window(self, icon, item): 
        self.root.after(0, self.root.withdraw)
        
    def minimize_app(self):
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        ctypes.windll.user32.ShowWindow(hwnd, 6) 

    def toggle_maximize(self):
        if self.root.state() == 'zoomed':
            self.root.state('normal')
            if hasattr(self, 'max_btn'): 
                self.max_btn.config(text='□')
        else:
            self.root.state('zoomed')
            if hasattr(self, 'max_btn'): 
                self.max_btn.config(text='❐')

    def close_app(self, icon=None, item=None):
        self.save_settings() 
        if hasattr(self, 'tray_icon'): 
            self.tray_icon.stop()
        self.root.destroy()

    def click_window(self, ev):
        if not getattr(self, 'is_locked', False):
            self._offset_x = ev.x
            self._offset_y = ev.y

    def drag_window(self, ev):
        if not getattr(self, 'is_locked', False):
            self.root.geometry(f"+{self.root.winfo_x() - self._offset_x + ev.x}+{self.root.winfo_y() - self._offset_y + ev.y}")

    def start_resize(self, ev): 
        self._rsx = ev.x_root
        self._rsy = ev.y_root
        self._sw = self.root.winfo_width()
        self._sh = self.root.winfo_height()
        self._sx = self.root.winfo_x()
        self._sy = self.root.winfo_y()
        
    def do_resize(self, ev, c):
        dx = ev.x_root - self._rsx
        dy = ev.y_root - self._rsy
        mw = int(608 * 0.8)
        mh = int(self.base_height_core * 0.8)
        nw = self._sw
        nh = self._sh
        nx = self._sx
        ny = self._sy
        
        if 'e' in c: 
            nw = max(mw, self._sw + dx)
        if 'w' in c: 
            nw = max(mw, self._sw - dx)
            nx = self._sx + (self._sw - nw)
        if 's' in c: 
            nh = max(mh, self._sh + dy)
            self.memo_extra_height = max(0, nh - self.base_height_core)
        if 'n' in c: 
            nh = max(mh, self._sh - dy)
            ny = self._sy + (self._sh - nh)
            self.memo_extra_height = max(0, nh - self.base_height_core)
            
        self.root.geometry(f"{nw}x{nh}+{nx}+{ny}")
        self.update_font_size(nw)

    def reset_size(self): 
        self.memo_extra_height = 0
        self.scale_ratio = 1.0
        self.scale_var.set("100%")
        self.root.geometry(f"608x{self.base_height_core}")
        self.update_font_size(608)
        self.root.update_idletasks()
        
        target_sash_y = 485
        if getattr(self, 'show_zero', False): target_sash_y += 40
        if getattr(self, 'show_extra', False): target_sash_y += 80
        try:
            self.paned_window.sash_place(0, 0, target_sash_y)
        except: pass
        self.save_settings()

    def toggle_lock(self):
        self.is_locked = not getattr(self, 'is_locked', False)
        self.update_lock_visuals()
        self.update_settings_menu()
        self.save_settings()

    def update_lock_visuals(self):
        cursor = "arrow" if getattr(self, 'is_locked', False) else "fleur"
        if hasattr(self, 'corner_lbl'): 
            self.corner_lbl.config(cursor=cursor)
        for r in range(1, len(self.period_times)+1): 
            if f"period_{r}" in self.cells: 
                self.cells[f"period_{r}"].config(cursor=cursor)

    def toggle_topmost(self):
        self.is_topmost = not getattr(self, 'is_topmost', False)
        self.root.attributes('-topmost', self.is_topmost)
        self.update_settings_menu()
        self.save_settings()

    def toggle_auto_start(self):
        self.auto_start = not getattr(self, 'auto_start', False)
        self.settings['auto_start'] = self.auto_start
        self.update_settings_menu()
        self.save_settings()
        
        if sys.platform == 'win32':
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "MyungdeokTimetable"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
                if self.auto_start:
                    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                    messagebox.showinfo("설정", "시작프로그램에 등록되었습니다.")
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                        messagebox.showinfo("설정", "시작프로그램에서 해제되었습니다.")
                    except FileNotFoundError:
                        pass
                winreg.CloseKey(key)
            except Exception as e:
                messagebox.showerror("에러", f"설정 오류: {e}")

    def show_mobile_viewer_qr(self):
        qr_win = tk.Toplevel(self.root)
        qr_win.title("모바일 뷰어 안내")
        qr_win.geometry("300x370")
        qr_win.resizable(False, False)
        t = self.themes[self.current_theme_idx]
        qr_win.configure(bg=t['bg'])
        qr_win.attributes('-topmost', True)
        
        lbl_title = tk.Label(qr_win, text="📱 모바일 뷰어 주소", font=('맑은 고딕', 12, 'bold'), bg=t['bg'], fg=t['cell_fg'])
        lbl_title.pack(pady=(20, 10))
        
        link = "https://my-timetable-pyo.streamlit.app/"
        lbl_link = tk.Entry(qr_win, font=('맑은 고딕', 10), justify='center', readonlybackground=t['bg'], fg="#2980b9", relief='flat')
        lbl_link.insert(0, link)
        lbl_link.config(state='readonly')
        lbl_link.pack(fill='x', padx=20, pady=5)
        
        try:
            url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={link}"
            response = requests.get(url, verify=False)
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            qr_photo = ImageTk.PhotoImage(img)
            
            lbl_qr = tk.Label(qr_win, image=qr_photo, bg=t['bg'])
            lbl_qr.image = qr_photo 
            lbl_qr.pack(pady=10)
            
            lbl_desc = tk.Label(qr_win, text="스마트폰 카메라로 QR코드를 스캔하세요.", font=('맑은 고딕', 9), bg=t['bg'], fg=t['cell_fg'])
            lbl_desc.pack(pady=5)
        except Exception as e:
            tk.Label(qr_win, text="QR 코드를 불러올 수 없습니다.\n인터넷 연결을 확인해주세요.", bg=t['bg'], fg="red").pack(pady=20)
            
        tk.Button(qr_win, text="닫기", bg='#34495e', fg='white', bd=0, font=('맑은 고딕', 9, 'bold'), width=10, command=qr_win.destroy).pack(pady=10)

    def show_program_info(self):
        info_text = "🏫 명덕외고 교사 시간표 v1.0\n\n개발 및 저작권자 : 표선생\n이메일 : vyalsgh@gmail.com\n\nCopyright ⓒ 2026 표선생. All rights reserved.\n본 프로그램의 무단 배포 및 상업적 이용을 금합니다."
        messagebox.showinfo("프로그램 정보", info_text)

    # ==========================================
    # 💡 2. 데이터 파싱 및 로딩 
    # ==========================================
    def parse_text_styles(self, raw_text):
        if not raw_text: 
            return "", None, None
        m = re.match(r'^<span style=[\'"](.*?)[\'"]>(.*)</span>$', raw_text, re.DOTALL | re.IGNORECASE)
        if m:
            style_str = m.group(1)
            text = m.group(2)
            fg, bg = None, None
            for style in style_str.split(';'):
                if ':' in style:
                    k, v = style.split(':', 1)
                    k = k.strip().lower()
                    v = v.strip()
                    if k == 'color': 
                        fg = v
                    elif k == 'background-color': 
                        bg = v
            return text, fg, bg
        return raw_text, None, None

    def build_styled_text(self, text, fg, bg):
        styles = []
        if fg: 
            styles.append(f"color:{fg}")
        if bg: 
            styles.append(f"background-color:{bg}")
            
        if styles:
            return f'<span style="{";".join(styles)}">{text}</span>'
        return text

    def can_view_private_data(self):
        log_u = self.settings.get('logged_in_user')
        tgt_u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not log_u: 
            return False
        return log_u == tgt_u or log_u == "표민호"

    def get_cell_key(self, date_str, r):
        if r == 1: 
            return f"{date_str}_schedule" 
        else: 
            return f"{date_str}_{r-1}"

    def load_academic_csv(self):
        """
        PC 차세대 1차:
        - CSV를 먼저 읽어 기본 학사일정을 확보합니다.
        - Supabase public.academic_calendar 데이터가 있으면 그 위에 덮어씁니다.
        - 이렇게 하면 Supabase 오류/누락이 있어도 기존 CSV 기준 화면은 유지됩니다.
        """
        self.academic_schedule = {}

        # 1. CSV fallback 먼저 로딩
        target_file = os.path.join(self.data_dir, 'academic_calendar.csv')
        if not os.path.exists(target_file):
            for root_candidate in [
                self.project_root,
                self.base_dir,
                os.path.dirname(self.base_dir),
                os.getcwd(),
                os.path.dirname(os.getcwd()),
            ]:
                candidate = os.path.join(root_candidate, 'data', 'academic_calendar.csv')
                if os.path.exists(candidate):
                    target_file = candidate
                    break

        if os.path.exists(target_file):
            try:
                with open(target_file, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames:
                        for row in reader:
                            date_str = (row.get('date') or '').strip()
                            event = (row.get('event') or '').strip()
                            if not date_str or not event:
                                continue
                            try:
                                datetime.strptime(date_str, '%Y-%m-%d')
                            except ValueError:
                                continue
                            self.academic_schedule[date_str] = event
            except Exception:
                pass

        # 2. Supabase 데이터가 있으면 덮어쓰기
        rows = supabase_get_rows(
            'academic_calendar',
            select='date,event',
            extra_params={'order': 'date.asc'},
            timeout=8
        )

        if rows:
            for row in rows:
                date_str = str(row.get('date') or '').strip()
                event = str(row.get('event') or '').strip()
                if not date_str or not event:
                    continue
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
                self.academic_schedule[date_str] = event

    def load_csv_data(self):
        """
        PC 차세대 1차:
        - CSV 시간표를 먼저 읽어 기본 시간표를 확보합니다.
        - Supabase public.timetable_entries 데이터가 있으면 그 위에 덮어씁니다.
        - UI와 디자인은 legacy 그대로 유지합니다.
        """
        self.teachers_data = {}

        # 1. CSV fallback 먼저 로딩
        file_path = os.path.join(self.data_dir, 'timetable.csv')
        if not os.path.exists(file_path):
            for root_candidate in [
                self.project_root,
                self.base_dir,
                os.path.dirname(self.base_dir),
                os.getcwd(),
                os.path.dirname(os.getcwd()),
            ]:
                candidate = os.path.join(root_candidate, 'data', 'timetable.csv')
                if os.path.exists(candidate):
                    file_path = candidate
                    break

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames:
                        temp_data = {}
                        for row in reader:
                            teacher = (row.get('teacher') or '').strip()
                            day = (row.get('day') or '').strip()
                            period = (row.get('period') or '').strip()
                            subject = (row.get('subject') or '').strip()

                            if not teacher or day not in self.days:
                                continue

                            try:
                                period_num = int(period)
                            except Exception:
                                continue

                            if period_num < 1 or period_num > 9:
                                continue

                            if teacher not in temp_data:
                                temp_data[teacher] = {
                                    '월': [''] * 9,
                                    '화': [''] * 9,
                                    '수': [''] * 9,
                                    '목': [''] * 9,
                                    '금': [''] * 9,
                                }

                            temp_data[teacher][day][period_num - 1] = subject

                        self.teachers_data = temp_data
            except Exception:
                pass

        # 2. Supabase 데이터가 있으면 덮어쓰기
        rows = supabase_get_rows(
            'timetable_entries',
            select='teacher_name,day,period,subject',
            extra_params={'order': 'teacher_name.asc,day.asc,period.asc'},
            timeout=8
        )

        if rows:
            if not self.teachers_data:
                self.teachers_data = {}

            for row in rows:
                teacher = str(row.get('teacher_name') or '').strip()
                day = str(row.get('day') or '').strip()
                period = row.get('period')
                subject = str(row.get('subject') or '').strip()

                if not teacher or day not in self.days:
                    continue

                try:
                    period_num = int(period)
                except Exception:
                    continue

                if period_num < 1 or period_num > 9:
                    continue

                if teacher not in self.teachers_data:
                    self.teachers_data[teacher] = {
                        '월': [''] * 9,
                        '화': [''] * 9,
                        '수': [''] * 9,
                        '목': [''] * 9,
                        '금': [''] * 9,
                    }

                self.teachers_data[teacher][day][period_num - 1] = subject

    def load_settings(self):
        self.settings = {
            'logged_in_user': None, 'teacher': None, 'auto_login': False, 'show_extra': False, 'show_zero': False, 'show_memo': True,
            'show_memo_expanded': False, 'theme_idx': 0, 'is_locked': False, 'is_topmost': False, 
            'width': 608, 'height': 555, 'x': 100, 'y': 100, 'font_family': '맑은 고딕', 'alpha': 0.95,
            'auto_start': False, 'memo_font_size': 9, 'memo_spacing': 1, 'memo_extra_height': 0
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = f.read().strip()
                    if data.startswith('{'): 
                        self.settings.update(json.loads(data))
            except: pass

        self.show_extra = self.settings['show_extra']
        self.show_zero = self.settings['show_zero']
        self.show_memo = self.settings.get('show_memo', True)
        self.show_memo_expanded = self.settings.get('show_memo_expanded', False)
        self.current_theme_idx = self.settings['theme_idx']
        self.is_locked = self.settings['is_locked']
        self.is_topmost = self.settings['is_topmost']
        self.base_width = self.settings['width']
        self.base_height = self.settings['height']
        self.scale_var = tk.StringVar(value="100%")
        self.scale_ratio = 1.0  
        self.alpha_var = tk.DoubleVar(value=self.settings.get('alpha', 0.95))
        self.auto_start = self.settings.get('auto_start', False) 

    def save_settings(self):
        try:
            if hasattr(self, 'teacher_var') and self.teacher_var.get():
                self.settings['teacher'] = self.teacher_var.get()
            self.settings['show_extra'] = self.show_extra
            self.settings['show_zero'] = self.show_zero
            self.settings['show_memo'] = self.show_memo
            self.settings['show_memo_expanded'] = getattr(self, 'show_memo_expanded', False)
            self.settings['theme_idx'] = self.current_theme_idx
            self.settings['is_locked'] = self.is_locked
            self.settings['is_topmost'] = self.is_topmost
            self.settings['auto_start'] = getattr(self, 'auto_start', False) 
            self.settings['memo_font_size'] = getattr(self, 'memo_font_size', 9)
            self.settings['memo_spacing'] = getattr(self, 'memo_spacing', 1)
            self.settings['memo_extra_height'] = getattr(self, 'memo_extra_height', 0)
            
            if self.root.winfo_exists() and self.root.state() != 'zoomed':
                self.settings['width'] = self.root.winfo_width()
                self.settings['height'] = self.root.winfo_height()
                self.settings['x'] = self.root.winfo_x()
                self.settings['y'] = self.root.winfo_y()
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False)
        except: pass

    def load_memos(self):
        if os.path.exists(self.memos_file):
            try:
                with open(self.memos_file, 'r', encoding='utf-8') as f: 
                    self.memos_data = json.load(f)
            except: 
                self.memos_data = {}

    def save_memos(self):
        try:
            with open(self.memos_file, 'w', encoding='utf-8') as f: 
                json.dump(self.memos_data, f, ensure_ascii=False)
        except: pass

    def load_custom_data(self):
        if os.path.exists(self.custom_data_file):
            try:
                with open(self.custom_data_file, 'r', encoding='utf-8') as f: 
                    self.custom_data = json.load(f)
            except: 
                self.custom_data = {}

    def save_custom_data(self):
        try:
            with open(self.custom_data_file, 'w', encoding='utf-8') as f: 
                json.dump(self.custom_data, f, ensure_ascii=False)
        except: pass

    def verify_and_load_user(self, user_id):
        if not USE_SUPABASE: 
            return None
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{user_id}", headers=HEADERS, verify=False)
            if r.status_code == 200 and len(r.json()) > 0:
                u_data = r.json()[0]
                self.current_theme_idx = u_data.get('theme_idx', 0)
                self.settings['font_family'] = u_data.get('font_name', '맑은 고딕')
                self.show_zero = u_data.get('show_zero', False)
                self.show_extra = u_data.get('show_extra', False)
                self.show_memo = u_data.get('show_memo', True)
                return u_data
        except: pass
        return None

    def bg_sync_db(self):
        if not USE_SUPABASE: 
            return
        
        try:
            r1 = requests.get(f"{SUPABASE_URL}/rest/v1/custom_schedule", headers=HEADERS, verify=False)
            if r1.status_code == 200:
                new_custom = {}
                for row in r1.json():
                    t = row.get('teacher_name')
                    dk = row.get('date_key')
                    if not t or not dk: 
                        continue
                    if t not in new_custom: 
                        new_custom[t] = {}
                    new_custom[t][dk] = row.get('subject', '')
                self.custom_data = new_custom
                self.save_custom_data()
        except: pass

        try:
            r2 = requests.get(f"{SUPABASE_URL}/rest/v1/memos", headers=HEADERS, verify=False)
            if r2.status_code == 200:
                new_memos = {}
                for row in r2.json():
                    t = row.get('teacher_name')
                    if not t: 
                        continue
                    if t not in new_memos: 
                        new_memos[t] = []
                    new_memos[t].append(row)
                
                final_memos = {}
                for t, rows in new_memos.items():
                    sorted_rows = sorted(rows, key=lambda x: x.get('id', 0), reverse=True)
                    final_memos[t] = []
                    for row in sorted_rows:
                        final_memos[t].append({
                            'id': row.get('id'), 
                            'text': row.get('memo_text', ''), 
                            'strike': row.get('is_strike', False), 
                            'important': row.get('is_important', False),
                            'created_at': row.get('created_at', datetime.now().isoformat())
                        })
                self.memos_data = final_memos
                self.save_memos()
        except: pass
        
        self.push_history()
        self.root.after(0, self.refresh_schedule_display)
        self.root.after(0, self.refresh_memo_list)


    def refresh_supabase_base_data(self):
        """설정 메뉴용: Supabase 시간표/학사일정 다시 불러오기."""
        try:
            self.load_academic_csv()
            self.load_csv_data()
            self.refresh_schedule_display()
            messagebox.showinfo("업데이트 확인", "Supabase 시간표/학사일정을 다시 불러왔습니다.")
        except Exception as e:
            messagebox.showerror("업데이트 오류", f"데이터 새로고침 중 오류가 발생했습니다.\n{e}")



    def show_data_source_info(self):
        """현재 PC 앱이 읽는 데이터 경로와 교사 목록을 확인합니다."""
        try:
            teacher_names = sorted(list(self.teachers_data.keys()))
            sample = ", ".join(teacher_names[:20])
            if len(teacher_names) > 20:
                sample += f" ... 외 {len(teacher_names) - 20}명"

            info = (
                f"project_root:\n{self.project_root}\n\n"
                f"data_dir:\n{self.data_dir}\n\n"
                f"assets_dir:\n{self.assets_dir}\n\n"
                f"시간표 교사 수: {len(teacher_names)}명\n"
                f"표민호 포함 여부: {'예' if '표민호' in teacher_names else '아니오'}\n\n"
                f"교사 목록 일부:\n{sample}"
            )
            messagebox.showinfo("데이터 경로/교사 목록", info)
        except Exception as e:
            messagebox.showerror("진단 오류", str(e))


    # ==========================================
    # 💡 3. 로그인 및 메인 화면 구성
    # ==========================================
    def build_login_ui(self):
        for widget in self.root.winfo_children(): 
            widget.destroy()
        
        w, h = 420, 430
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(420, 430)
        self.root.configure(bg='#d0d7de')
        
        title_bar = tk.Frame(self.root, bg='#2c3e50', bd=0)
        title_bar.pack(fill='x', side='top')
        
        title_lbl = tk.Label(title_bar, text="로그인 - 명덕외고 시간표", bg='#2c3e50', fg='white', font=('맑은 고딕', 9, 'bold'))
        title_lbl.pack(side='left', padx=10, pady=5)
        
        login_close_btn = tk.Button(title_bar, text='✕', bg='#2c3e50', fg='white', bd=0, width=5, font=('Segoe UI Symbol', 10), command=self.close_app, relief='flat', activebackground='#e81123', activeforeground='white', cursor='hand2')
        login_close_btn.pack(side='right', ipady=1)
        self.bind_caption_hover(login_close_btn, role='close')

        for w_item in [title_bar, title_lbl]:
            w_item.bind('<Button-1>', self.click_window)
            w_item.bind('<B1-Motion>', self.drag_window)

        main_f = tk.Frame(self.root, bg='#eef2f6', bd=0)
        main_f.pack(expand=True, fill='both', padx=0, pady=(0, 0))

        card = tk.Frame(main_f, bg='#f8fafc', bd=1, relief='solid')
        card.pack(expand=True, fill='both', padx=18, pady=18)
        card.pack_propagate(False)

        header = tk.Frame(card, bg='#f8fafc', bd=0)
        header.pack(fill='x', padx=22, pady=(18, 10))
        tk.Label(header, text="🏫  시간표 뷰어", font=('맑은 고딕', 18, 'bold'), bg='#f8fafc', fg='#223548').pack(anchor='center')

        form = tk.Frame(card, bg='#f8fafc', bd=0)
        form.pack(fill='both', expand=True, padx=22, pady=(6, 20))

        tk.Label(form, text="아이디(성함)", bg='#f8fafc', fg='#334155', font=('맑은 고딕', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        self.id_entry = tk.Entry(form, font=('맑은 고딕', 10), bd=1, relief='solid')
        self.id_entry.pack(fill='x', ipady=6, pady=(0, 12))
        self.id_entry.bind('<Return>', self.do_login)

        tk.Label(form, text="비밀번호", bg='#f8fafc', fg='#334155', font=('맑은 고딕', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        self.pw_entry = tk.Entry(form, show='*', font=('맑은 고딕', 10), bd=1, relief='solid')
        self.pw_entry.pack(fill='x', ipady=6, pady=(0, 12))
        self.pw_entry.bind('<Return>', self.do_login)

        self.auto_login_var = tk.BooleanVar(value=self.settings.get('auto_login', False))
        auto_row = tk.Frame(form, bg='#f8fafc', bd=0)
        auto_row.pack(fill='x', pady=(0, 14))
        tk.Checkbutton(auto_row, text="자동 로그인", variable=self.auto_login_var, bg='#f8fafc', fg='#334155', activebackground='#f8fafc', font=('맑은 고딕', 9)).pack(anchor='w')

        btn_row = tk.Frame(form, bg='#f8fafc', bd=0)
        btn_row.pack(fill='x')
        tk.Button(btn_row, text="로그인", bg='#2563eb', fg='white', activebackground='#1d4ed8', activeforeground='white', bd=0, font=('맑은 고딕', 10, 'bold'), command=self.do_login, cursor='hand2').pack(fill='x', ipady=7, pady=(0, 8))
        tk.Button(btn_row, text="계정 생성", bg='#16a34a', fg='white', activebackground='#15803d', activeforeground='white', bd=0, font=('맑은 고딕', 10, 'bold'), command=self.do_register, cursor='hand2').pack(fill='x', ipady=7)

    def do_login(self, event=None):
        u_id = self.id_entry.get().strip()
        u_pw = self.pw_entry.get().strip()
        if not u_id or not u_pw:
            messagebox.showwarning("입력 누락", "아이디와 비밀번호를 모두 입력해 주세요.")
            return
        
        if not USE_SUPABASE:
            self.settings['logged_in_user'] = u_id
            self.settings['teacher'] = u_id 
            self.settings['auto_login'] = self.auto_login_var.get()
            self.start_main_app()
            return

        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{u_id}", headers=HEADERS, verify=False)
            data = r.json()
            if r.status_code == 200 and len(data) > 0:
                if str(data[0]['password']) == u_pw:
                    self.settings['logged_in_user'] = u_id
                    self.settings['teacher'] = u_id 
                    self.settings['auto_login'] = self.auto_login_var.get()
                    self.verify_and_load_user(u_id)
                    self.start_main_app()
                else: 
                    messagebox.showerror("로그인 실패", "비밀번호가 일치하지 않습니다.")
            else: 
                messagebox.showerror("로그인 실패", "등록되지 않은 이름입니다.")
        except Exception as e:
            messagebox.showerror("오류", f"로그인 중 오류가 발생했습니다: {e}")

    def do_register(self):
        self.open_register_form()

    def open_register_form(self):
        if hasattr(self, 'register_win') and self.register_win and self.register_win.winfo_exists():
            self.register_win.deiconify()
            self.register_win.lift()
            self.register_win.focus_force()
            return

        win = tk.Toplevel(self.root)
        self.register_win = win
        win.title("계정 생성")
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)
        win.configure(bg='#eef2f6')

        # 등록창이 좌측 상단이 아니라 화면 중앙에 뜨도록 설정
        win.update_idletasks()
        width, height = 460, 430
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()
        x = max((screen_w - width) // 2, 0)
        y = max((screen_h - height) // 2 - 20, 0)
        win.geometry(f'{width}x{height}+{x}+{y}')
        win.minsize(width, height)

        outer = tk.Frame(win, bg='#f8fafc', bd=1, relief='solid')
        outer.pack(fill='both', expand=True, padx=18, pady=18)

        tk.Label(outer, text="계정 생성", bg='#f8fafc', fg='#223548', font=('맑은 고딕', 16, 'bold')).pack(anchor='center', pady=(18, 10))
        tk.Label(outer, text="본인 이름(실명)으로 등록해 주세요.", bg='#f8fafc', fg='#64748b', font=('맑은 고딕', 9)).pack(anchor='center', pady=(0, 12))

        form = tk.Frame(outer, bg='#f8fafc')
        form.pack(fill='both', expand=True, padx=22, pady=(0, 12))

        tk.Label(form, text="아이디(성함)", bg='#f8fafc', fg='#334155', font=('맑은 고딕', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        name_entry = tk.Entry(form, font=('맑은 고딕', 10), bd=1, relief='solid')
        name_entry.pack(fill='x', ipady=6, pady=(0, 10))
        name_entry.insert(0, self.id_entry.get().strip())

        tk.Label(form, text="비밀번호", bg='#f8fafc', fg='#334155', font=('맑은 고딕', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        pw_entry = tk.Entry(form, show='*', font=('맑은 고딕', 10), bd=1, relief='solid')
        pw_entry.pack(fill='x', ipady=6, pady=(0, 10))
        pw_entry.insert(0, self.pw_entry.get().strip())

        tk.Label(form, text="비밀번호 확인", bg='#f8fafc', fg='#334155', font=('맑은 고딕', 9, 'bold')).pack(anchor='w', pady=(0, 4))
        pw2_entry = tk.Entry(form, show='*', font=('맑은 고딕', 10), bd=1, relief='solid')
        pw2_entry.pack(fill='x', ipady=6, pady=(0, 16))

        def submit_register(event=None):
            u_id = name_entry.get().strip()
            u_pw = pw_entry.get().strip()
            u_pw2 = pw2_entry.get().strip()

            if not u_id or not u_pw or not u_pw2:
                messagebox.showwarning("입력 누락", "아이디와 비밀번호를 모두 입력해 주세요.", parent=win)
                return
            if u_pw != u_pw2:
                messagebox.showwarning("입력 확인", "비밀번호 확인이 일치하지 않습니다.", parent=win)
                return
            if not messagebox.askyesno("계정 생성", "계정 생성시 본인 이름(실명)으로 생성해야 합니다.\n진행하시겠습니까?", parent=win):
                return

            if not USE_SUPABASE:
                self.id_entry.delete(0, 'end')
                self.id_entry.insert(0, u_id)
                self.pw_entry.delete(0, 'end')
                self.pw_entry.insert(0, u_pw)
                messagebox.showinfo("안내", "클라우드 연동이 설정되지 않아 로컬 테스트용으로 입력값만 채워 두었습니다.", parent=win)
                win.destroy()
                return

            try:
                r = requests.get(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{u_id}", headers=HEADERS, verify=False)
                if r.status_code == 200 and len(r.json()) > 0:
                    messagebox.showwarning("경고", "이미 존재하는 성함입니다.", parent=win)
                    return

                requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=HEADERS, json={"teacher_name": u_id, "password": u_pw}, verify=False)
                self.id_entry.delete(0, 'end')
                self.id_entry.insert(0, u_id)
                self.pw_entry.delete(0, 'end')
                self.pw_entry.insert(0, u_pw)
                messagebox.showinfo("완료", f"{u_id} 선생님, 계정 생성이 완료되었습니다.", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("오류", f"계정 생성 중 오류: {e}", parent=win)

        btns = tk.Frame(outer, bg='#f8fafc')
        btns.pack(fill='x', padx=22, pady=(2, 20))
        tk.Button(btns, text="취소", bg='#e5e7eb', fg='#1f2937', activebackground='#d1d5db', bd=0, font=('맑은 고딕', 10), command=win.destroy, cursor='hand2').pack(side='right', ipadx=12, ipady=6)
        tk.Button(btns, text="등록", bg='#16a34a', fg='white', activebackground='#15803d', activeforeground='white', bd=0, font=('맑은 고딕', 10, 'bold'), command=submit_register, cursor='hand2').pack(side='right', ipadx=14, ipady=6, padx=(0, 8))

        for entry in (name_entry, pw_entry, pw2_entry):
            entry.bind('<Return>', submit_register)

        win.bind('<Escape>', lambda e: win.destroy())
        name_entry.focus_set()

    def start_main_app(self):
        self.load_images()
        
        for widget in self.root.winfo_children(): 
            widget.destroy()
            
        self.save_settings()
        
        w = self.settings.get('width', 608)
        if w < 500: 
            w = 608 
        h = self.base_height_core + getattr(self, 'memo_extra_height', 0)
        
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = self.settings.get('x', int((sw - w) / 2))
        y = self.settings.get('y', int((sh - h) / 2))
        
        if self.root.state() != 'zoomed':
            self.root.geometry(f"{w}x{h}+{x}+{y}")
            
        self.build_ui()
        self.apply_native_window_style()
        self.update_font_size(w)
        self.apply_theme()
        
        self._check_time_loop()
        self.update_toolbar_state()
        if hasattr(self, 'relayout_toolbar'):
            self.relayout_toolbar()
        
        if USE_SUPABASE: 
            threading.Thread(target=self.bg_sync_db, daemon=True).start()

    def _check_time_loop(self):
        now = datetime.now()
        if getattr(self, 'last_minute', None) != now.minute:
            self.update_time_and_date()
        self.last_minute = now.minute
        self.timer_id = self.root.after(1000, self._check_time_loop)

    def bind_hover(self, widget, is_title=False):
        def on_enter(e):
            t = self.themes[self.current_theme_idx]
            hover_bg = getattr(e.widget, '_hover_bg', None)
            hover_fg = getattr(e.widget, '_hover_fg', None)
            if hover_bg is None:
                hover_bg = t.get('hover_title', t['head_bg']) if is_title else t.get('hover_btn', t['top'])
            if hover_fg is None:
                hover_fg = e.widget.cget('fg') if 'fg' in e.widget.keys() else t.get('head_fg', t['cell_fg'])
            try:
                e.widget.config(bg=hover_bg, fg=hover_fg)
            except tk.TclError:
                try:
                    e.widget.config(bg=hover_bg)
                except tk.TclError:
                    pass

        def on_leave(e):
            t = self.themes[self.current_theme_idx]
            base_bg = getattr(e.widget, '_base_bg', None)
            base_fg = getattr(e.widget, '_base_fg', None)
            if base_bg is None:
                base_bg = t['titlebar_bg'] if is_title else t['top']
            if base_fg is None:
                base_fg = e.widget.cget('fg') if 'fg' in e.widget.keys() else t.get('head_fg', t['cell_fg'])
            try:
                e.widget.config(bg=base_bg, fg=base_fg)
            except tk.TclError:
                try:
                    e.widget.config(bg=base_bg)
                except tk.TclError:
                    pass

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def bind_cell_hover(self, widget):
        def on_enter(e):
            t = self.themes[self.current_theme_idx]
            widget._orig_bg = widget.cget('bg')
            widget._orig_fg = widget.cget('fg')
            if widget._orig_bg not in [t['hl_cell'], t['hl_per']]:
                hover_bg, hover_fg = self.get_hover_cell_style(widget)
                widget.config(bg=hover_bg, fg=hover_fg)

        def on_leave(e):
            if hasattr(widget, '_orig_bg'):
                widget.config(bg=widget._orig_bg)
            if hasattr(widget, '_orig_fg'):
                widget.config(fg=widget._orig_fg)

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def search_memo(self, event=None):
        if not self.can_view_private_data() or not getattr(self, 'show_memo', True):
            return "break"
            
        query = simpledialog.askstring("메모 검색", "찾을 단어를 입력하세요:", parent=self.root)
        self.memo_text.tag_remove("search_highlight", "1.0", tk.END)
        
        if query:
            start_idx = "1.0"
            found = False
            while True:
                start_idx = self.memo_text.search(query, start_idx, stopindex=tk.END, nocase=True)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(query)}c"
                self.memo_text.tag_add("search_highlight", start_idx, end_idx)
                start_idx = end_idx
                found = True
            
            if found:
                self.memo_text.tag_configure("search_highlight", background="#f1c40f", foreground="black")
                self.memo_text.tag_raise("search_highlight")
                first_match = self.memo_text.tag_ranges("search_highlight")[0]
                self.memo_text.see(first_match)
            else:
                messagebox.showinfo("검색 결과", "일치하는 메모가 없습니다.", parent=self.root)
        return "break"

    def show_sticker_palette(self, r, c, x, y):
        self._build_sticker_palette("스티커 추가", lambda em: self.add_sticker_to_cell(r, c, em), x, y)

    def show_memo_sticker_palette(self, x, y):
        self._build_sticker_palette("스티커 추가 (메모)", self.add_sticker_to_memo, x, y)

    def add_sticker_to_cell(self, r, c, sticker):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
        
        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        date_str = (monday + timedelta(days=c-1)).strftime('%Y-%m-%d')
        key = self.get_cell_key(date_str, r)
        
        p_n = self.period_times[r-1][0]
        orig = ""
        if p_n == "학사일정": orig = self.academic_schedule.get(date_str, "")
        elif p_n not in ["점심", "조회"]: 
            s_l = self.current_schedule.get(self.days[c-1], [])
            idx = r - 3 if r < 8 else r - 4
            orig = s_l[idx] if 0 <= idx < len(s_l) else ""
            
        cur_v = self.custom_data.get(u, {}).get(key, orig)
        is_struck = False
        if cur_v == "__STRIKE__":
            cur_v = ""
        elif cur_v.startswith("__STRIKE__|||"):
            is_struck = True
            cur_v = cur_v.split("|||", 1)[1]
            
        clean_text, fg, bg = self.parse_text_styles(cur_v)
        
        new_text = self.format_sticker_text(clean_text, sticker)
        if not self.check_input_limit(new_text):
            messagebox.showwarning("입력 제한", "칸에 입력할 수 있는 최대 범위를 초과했습니다.", parent=self.root)
            return
            
        new_v = self.build_styled_text(new_text, fg, bg)
        if is_struck:
            new_v = "__STRIKE__|||" + new_v
        
        self.custom_data.setdefault(u, {})[key] = new_v
        if USE_SUPABASE: 
            self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": new_v})
            
        self.save_custom_data()
        self.push_history()
        self.refresh_schedule_display()
        self.update_time_and_date()

    def add_sticker_to_memo(self, sticker):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
            
        for idx in list(self.selected_memo_indices):
            m = self.memos_data[u][idx]
            clean_text, fg, bg = self.parse_text_styles(m['text'])
            
            new_text = self.format_sticker_text(clean_text, sticker)
            new_v = self.build_styled_text(new_text, fg, bg)
            m['text'] = new_v
            
            if USE_SUPABASE and 'id' in m:
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"memo_text": new_v})
                
        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()

    # ==========================================
    # 💡 UI 렌더링 및 유틸리티
    # ==========================================
    def build_ui(self):
        self.title_bar = tk.Frame(self.root, bd=0, padx=8, pady=4)
        self.title_bar.pack(fill='x', side='top')

        self.title_left = tk.Frame(self.title_bar, bd=0)
        self.title_left.pack(side='left', fill='x', expand=True)
        self.title_right = tk.Frame(self.title_bar, bd=0)
        self.title_right.pack(side='right')

        exe_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        if getattr(self, 'title_logo_img', None):
            self.title_logo_lbl = tk.Label(self.title_left, image=self.title_logo_img, bd=0)
            self.title_logo_lbl.pack(side='left', padx=(6, 6), pady=4)
        else:
            self.title_logo_lbl = None
        self.title_lbl = tk.Label(self.title_left, text=exe_name, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.title_lbl.pack(side='left', padx=(2, 10), pady=4)

        self.undo_btn = tk.Button(self.title_left, text='↺', bd=0, width=3, font=('Segoe UI Symbol', 10), command=self.undo_action)
        self.undo_btn.pack(side='left', padx=(2, 2))
        self.redo_btn = tk.Button(self.title_left, text='↻', bd=0, width=3, font=('Segoe UI Symbol', 10), command=self.redo_action)
        self.redo_btn.pack(side='left', padx=(0, 4))

        self.close_btn = tk.Button(self.title_right, text='✕', width=5, font=('Segoe UI Symbol', 11), command=self.close_app)
        self.close_btn.pack(side='right', ipady=1)
        self.max_btn = tk.Button(self.title_right, text='□', width=5, font=('Segoe UI Symbol', 10), command=self.toggle_maximize)
        self.max_btn.pack(side='right', ipady=1)
        self.min_btn = tk.Button(self.title_right, text='─', width=5, font=('Segoe UI Symbol', 11), command=self.minimize_app)
        self.min_btn.pack(side='right', ipady=1)

        for btn, role in [(self.min_btn, 'normal'), (self.max_btn, 'normal'), (self.close_btn, 'close')]:
            self.style_caption_button(btn, role)
            self.bind_caption_hover(btn, role)

        drag_widgets = [self.title_bar, self.title_left, self.title_lbl]
        if getattr(self, 'title_logo_lbl', None) is not None:
            drag_widgets.append(self.title_logo_lbl)
        for w in drag_widgets:
            w.bind('<Button-1>', self.click_window)
            w.bind('<B1-Motion>', self.drag_window)

        self.title_sep = tk.Frame(self.root, height=1, bd=0)
        self.title_sep.pack(fill='x')

        self.top_bar = tk.Frame(self.root, bd=0)
        self.top_bar.pack(fill='x', padx=10, pady=(8, 6))
        self.toolbar_row1 = tk.Frame(self.top_bar, bd=0)
        self.toolbar_row2 = tk.Frame(self.top_bar, bd=0)
        self.row1_left = tk.Frame(self.toolbar_row1, bd=0)
        self.left_sep1 = tk.Frame(self.row1_left, width=1, height=22, bd=0)
        self.row1_right = tk.Frame(self.toolbar_row1, bd=0)
        self.right_sep = tk.Frame(self.row1_right, width=1, height=20, bd=0)
        self.row2_left = tk.Frame(self.toolbar_row2, bd=0)
        self.row2_right = tk.Frame(self.toolbar_row2, bd=0)
        self.left_frame = self.row1_left
        self.right_frame = self.row1_right

        teacher_names = list(self.teachers_data.keys())
        self.current_schedule = {d: [""]*9 for d in self.days}
        self.teacher_var = tk.StringVar()
        self.teacher_cb = ttk.Combobox(self.row1_left, textvariable=self.teacher_var, values=teacher_names, width=10, state='readonly', font=self.font_title, style='Modern.TCombobox')
        self.teacher_cb.bind('<<ComboboxSelected>>', self.on_teacher_select)
        self.apply_combobox_style()

        self.prev_btn = tk.Button(self.row1_left, text='‹', bd=0, width=2, font=('Segoe UI Symbol', 11), command=self.prev_week)
        self.curr_btn_border = tk.Frame(self.row1_left, bd=0)
        self.curr_btn = tk.Button(self.curr_btn_border, text='오늘', bd=0, width=4, font=self.font_title, command=self.curr_week)
        self.curr_btn.pack(padx=1, pady=(1, 2))
        self.next_btn = tk.Button(self.row1_left, text='›', bd=0, width=2, font=('Segoe UI Symbol', 11), command=self.next_week)

        self.cal_btn_border = tk.Frame(self.row1_left, bd=0)
        self.cal_btn = tk.Button(self.cal_btn_border, text='달력', bd=0, width=4, font=self.font_title, command=self.toggle_calendar)
        self.cal_btn.pack(padx=1, pady=(1, 2))
        self.memo_btn_border = tk.Frame(self.row1_left, bd=0)
        self.memo_btn = tk.Button(self.memo_btn_border, text='메모', bd=0, width=4, font=self.font_title, command=self.toggle_memo)
        self.memo_btn.pack(padx=1, pady=(1, 2))
        self.zero_btn_border = tk.Frame(self.row1_left, bd=0)
        self.zero_btn = tk.Button(self.zero_btn_border, text='조회', bd=0, width=4, font=self.font_title, command=self.toggle_zero)
        self.zero_btn.pack(padx=1, pady=(1, 2))
        self.extra_btn_border = tk.Frame(self.row1_left, bd=0)
        self.extra_btn = tk.Button(self.extra_btn_border, text='8·9', bd=0, width=4, font=self.font_title, command=self.toggle_extra)
        self.extra_btn.pack(padx=1, pady=(1, 2))

        if teacher_names:
            login_u = self.settings.get('logged_in_user')
            target_u = login_u if login_u in teacher_names else self.settings.get('teacher')
            if not target_u or target_u not in teacher_names:
                target_u = "표민호" if "표민호" in teacher_names else teacher_names[0]
            default_idx = teacher_names.index(target_u)
            self.teacher_cb.current(default_idx)
            self.teacher_var.set(target_u)
            self.current_schedule = self.teachers_data.get(target_u, {d: [""]*9 for d in self.days})

        self.alpha_lbl = tk.Label(self.row1_right, text='투명', font=('맑은 고딕', 8, 'bold'))
        self.alpha_scale = CustomSlider(self.row1_right, width=60, height=24, command=self.on_alpha_slide)
        self.alpha_scale.set(self.alpha_var.get())

        self.save_btn = tk.Button(self.row1_right, text='저장', bd=0, width=4, font=self.font_title, command=self.manual_save_db)
        self.settings_mb = tk.Menubutton(self.row1_right, text='설정', bd=0, width=4, font=self.font_title, relief='flat', direction='below')
        self.settings_menu = self.create_themed_menu(self.settings_mb)
        self.settings_mb.config(menu=self.settings_menu)
        self.update_settings_menu()

        for b in [self.prev_btn, self.curr_btn, self.next_btn, self.cal_btn, self.memo_btn, self.zero_btn, self.extra_btn, self.save_btn, self.settings_mb]:
            self.bind_hover(b)
        for b in [self.undo_btn, self.redo_btn]:
            self.bind_hover(b, is_title=True)

        self.root.bind('<Configure>', self.relayout_toolbar, add='+')
        self.relayout_toolbar()
        self.toolbar_sep = tk.Frame(self.root, height=1, bd=0)
        self.toolbar_sep.pack(fill='x', padx=10, pady=(0, 8))

        self.paned_window = tk.PanedWindow(self.root, orient=tk.VERTICAL, bd=0, sashwidth=8, sashrelief=tk.RAISED, sashcursor="sb_v_double_arrow")
        self.paned_window.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.grid_frame = tk.Frame(self.paned_window, bd=1, relief='solid')
        self.paned_window.add(self.grid_frame, stretch="never")

        self.memo_frame = tk.Frame(self.paned_window, cursor="arrow", bd=1, relief='solid') 
        
        self.memo_input_f = tk.Frame(self.memo_frame, cursor="arrow") 
        self.memo_input_f.pack(side='bottom', fill='x', padx=8, pady=(6, 8))
        
        self.memo_entry = tk.Entry(self.memo_input_f, font=self.font_title, cursor="xterm")
        self.memo_entry.pack(side='left', fill='x', expand=True, padx=(0, 6), ipady=6)
        self.memo_entry.insert(0, "메모를 입력하세요")
        self.memo_entry.config(fg='gray')
        
        def on_focus_in(e):
            if self.memo_entry.get() == "메모를 입력하세요":
                self.memo_entry.delete(0, tk.END)
                t = self.themes[self.current_theme_idx]
                self.memo_entry.config(fg='black' if t['name'] == '웜 파스텔' else t['cell_fg'])
                
        def on_focus_out(e):
            if not self.memo_entry.get().strip():
                self.memo_entry.delete(0, tk.END)
                self.memo_entry.insert(0, "메모를 입력하세요")
                self.memo_entry.config(fg='gray')

        self.memo_entry.bind('<FocusIn>', on_focus_in)
        self.memo_entry.bind('<FocusOut>', on_focus_out)
        self.memo_entry.bind('<Return>', self.add_memo)
        
        self.search_btn = tk.Button(self.memo_input_f, text='검색', bd=0, font=self.font_title, cursor='hand2', command=self.search_memo, width=5)
        self.search_btn.pack(side='left', padx=2)
        
        self.expand_btn = tk.Button(self.memo_input_f, text='A+', bd=0, font=self.font_title, cursor='hand2', command=self.expand_memo, width=4)
        self.expand_btn.pack(side='left', padx=1)
        self.shrink_btn = tk.Button(self.memo_input_f, text='A-', bd=0, font=self.font_title, cursor='hand2', command=self.shrink_memo, width=4)
        self.shrink_btn.pack(side='left', padx=1)
        
        self.memo_list_f = tk.Frame(self.memo_frame, cursor="arrow") 
        self.memo_list_f.pack(side='bottom', fill='both', expand=True, padx=8, pady=(0, 8))
        self.memo_sb = tk.Scrollbar(self.memo_list_f)
        self.memo_sb.pack(side='right', fill='y')
        
        self.memo_text_height = getattr(self, 'memo_text_height', 10)
        
        self.memo_text = tk.Text(self.memo_list_f, height=self.memo_text_height, font=self.font_memo, cursor="arrow", bd=0, highlightthickness=1, relief='solid', padx=8, pady=8, spacing1=self.memo_spacing, spacing3=self.memo_spacing, yscrollcommand=self.memo_sb.set)
        self.memo_text.pack(side='left', fill='both', expand=True)
        self.memo_sb.config(command=self.memo_text.yview)
        
        self.memo_text.bind("<Configure>", lambda e: self.memo_text.config(tabs=(max(50, e.width - 20), "right")) if e.width > 60 else None)
        
        self.memo_text.tag_configure("strike", overstrike=True, foreground="#95a5a6")
        self.memo_text.tag_configure("selected_row", background="#dbeafe", foreground="#1e3a8a")
        self.memo_text.tag_configure("important_star", foreground="#f1c40f", font=self.font_memo)
        self.memo_text.tag_configure("unimportant_star", foreground="#bdc3c7", font=self.font_memo)
        self.memo_text.tag_configure("checkbox_on", foreground="#27ae60", font=self.font_memo)
        self.memo_text.tag_configure("checkbox_off", foreground="#95a5a6", font=self.font_memo)
        self.memo_text.tag_configure("search_highlight", background="#f1c40f", foreground="black") 
        
        self.memo_text.bind("<Button-1>", self.on_memo_click)
        self.memo_text.bind("<B1-Motion>", self.on_memo_drag) 
        self.memo_text.bind("<Double-Button-1>", self.on_memo_double_click)
        self.bind_context_popup(self.memo_text, self.show_memo_context_menu)

        self.create_grid()
        self.apply_row_visibility()
        self.refresh_memo_list()
        
        if self.show_memo: 
            self.paned_window.add(self.memo_frame, stretch="always")
        
        self.sizegrip_nw = tk.Frame(self.root, cursor="size_nw_se", width=6, height=6)
        self.sizegrip_nw.place(relx=0, rely=0)
        self.sizegrip_ne = tk.Frame(self.root, cursor="size_ne_sw", width=6, height=6)
        self.sizegrip_ne.place(relx=1, rely=0, anchor='ne')
        self.sizegrip_sw = tk.Frame(self.root, cursor="size_ne_sw", width=6, height=6)
        self.sizegrip_sw.place(relx=0, rely=1, anchor='sw')
        self.sizegrip_se = tk.Frame(self.root, cursor="size_nw_se", width=6, height=6)
        self.sizegrip_se.place(relx=1, rely=1, anchor='se')
        
        self.sizegrip_n = tk.Frame(self.root, cursor="sb_v_double_arrow")
        self.sizegrip_n.place(relx=0.01, rely=0, relwidth=0.98, height=4)
        self.sizegrip_s = tk.Frame(self.root, cursor="sb_v_double_arrow")
        self.sizegrip_s.place(relx=0.01, rely=1.0, anchor='sw', relwidth=0.98, height=4)
        self.sizegrip_e = tk.Frame(self.root, cursor="sb_h_double_arrow")
        self.sizegrip_e.place(relx=1.0, rely=0.01, anchor='ne', width=4, relheight=0.98)
        self.sizegrip_w = tk.Frame(self.root, cursor="sb_h_double_arrow")
        self.sizegrip_w.place(relx=0, rely=0.01, width=4, relheight=0.98)

        grips = [(self.sizegrip_nw, 'nw'), (self.sizegrip_ne, 'ne'), (self.sizegrip_sw, 'sw'), (self.sizegrip_se, 'se'),
                 (self.sizegrip_n, 'n'), (self.sizegrip_s, 's'), (self.sizegrip_e, 'e'), (self.sizegrip_w, 'w')]
        for grip, corner in grips:
            grip.bind("<Button-1>", self.start_resize)
            grip.bind("<B1-Motion>", lambda e, c=corner: self.do_resize(e, c))
            
        self.update_lock_visuals()

    def start_acad_resize(self, ev):
        self._acad_start_y = ev.y_root
        self._acad_start_height = self.cells["period_1"].winfo_height()

    def do_acad_resize(self, ev):
        dy = ev.y_root - self._acad_start_y
        new_h = max(28, self._acad_start_height + dy) 
        self.grid_frame.rowconfigure(1, minsize=new_h, weight=0)

    def update_toolbar_state(self):
        t = self.themes[self.current_theme_idx]
        if hasattr(self, 'curr_btn_border'):
            self.style_toggle_chip(self.curr_btn_border, self.curr_btn, 'today', self.week_offset == 0)
        if hasattr(self, 'cal_btn_border'):
            self.style_toggle_chip(self.cal_btn_border, self.cal_btn, 'calendar', self.week_offset != 0)
        if hasattr(self, 'memo_btn_border'):
            self.style_toggle_chip(self.memo_btn_border, self.memo_btn, 'memo', getattr(self, 'show_memo', True))
        if hasattr(self, 'zero_btn_border'):
            self.style_toggle_chip(self.zero_btn_border, self.zero_btn, 'lookup', getattr(self, 'show_zero', False))
        if hasattr(self, 'extra_btn_border'):
            self.style_toggle_chip(self.extra_btn_border, self.extra_btn, 'extra', getattr(self, 'show_extra', False))
        if hasattr(self, 'left_sep1'):
            self.left_sep1.configure(bg=t.get('panel_border', t['grid']))
        if hasattr(self, 'right_sep'):
            self.right_sep.configure(bg=t.get('panel_border', t['grid']))
        if hasattr(self, 'update_toolbar_texts'):
            self.update_toolbar_texts()

    def apply_theme(self):
        t = self.themes[self.current_theme_idx]
        self.root.configure(bg=t['bg'])
        self.title_bar.configure(bg=t['titlebar_bg'])
        if hasattr(self, 'title_left'):
            self.title_left.configure(bg=t['titlebar_bg'])
        if hasattr(self, 'title_right'):
            self.title_right.configure(bg=t['titlebar_bg'])
        if hasattr(self, 'title_logo_lbl') and self.title_logo_lbl is not None:
            self.title_logo_lbl.configure(bg=t['titlebar_bg'])
        self.title_lbl.configure(bg=t['titlebar_bg'], fg=t.get('head_fg', 'white'))
        
        for b in [self.undo_btn, self.redo_btn]:
            if hasattr(self, 'min_btn'):
                b.configure(bg=t['titlebar_bg'], fg=t.get('title_btn_fg', t.get('head_fg', 'white')), activebackground=t.get('hover_title', t['head_bg']), activeforeground=t.get('title_btn_fg', t.get('head_fg', 'white')))
                b._base_bg = t['titlebar_bg']
                b._base_fg = t.get('title_btn_fg', t.get('head_fg', 'white'))
                b._hover_bg = t.get('hover_title', t['head_bg'])
                b._hover_fg = t.get('title_btn_fg', t.get('head_fg', 'white'))

        if hasattr(self, 'min_btn'):
            self.style_caption_button(self.min_btn, 'normal')
            self.style_caption_button(self.max_btn, 'normal')
            self.style_caption_button(self.close_btn, 'close')
            
        for f in [self.top_bar, self.toolbar_row1, self.toolbar_row2, self.row1_left, self.row1_right, self.row2_left, self.row2_right]:
            if hasattr(self, 'top_bar'):
                f.configure(bg=t['top'])
        if hasattr(self, 'left_sep1'):
            self.left_sep1.configure(bg=t.get('panel_border', t['grid']))
        if hasattr(self, 'right_sep'):
            self.right_sep.configure(bg=t.get('panel_border', t['grid']))
        self.top_bar.configure(highlightthickness=1, highlightbackground=t.get('panel_border', t['grid']), highlightcolor=t.get('panel_border', t['grid']), bg=t['top'])

        if hasattr(self, 'title_sep'):
            self.title_sep.configure(bg=t['grid'])
        if hasattr(self, 'toolbar_sep'):
            self.toolbar_sep.configure(bg=t['grid'])

        self.grid_frame.configure(bg=t.get('panel_border', t['grid']), highlightbackground=t.get('panel_border', t['grid']), highlightcolor=t.get('panel_border', t['grid']), bd=1, relief='solid')
        self.memo_frame.configure(bg=t.get('panel_bg', t['bg']), highlightbackground=t.get('panel_border', t['grid']), highlightcolor=t.get('panel_border', t['grid']), bd=1, relief='solid')
        self.memo_input_f.configure(bg=t.get('panel_bg', t['bg']))
        self.memo_list_f.configure(bg=t.get('panel_bg', t['bg']))
        
        if hasattr(self, 'memo_text'):
            self.memo_text.configure(bg=t['cell_bg'], fg=t['cell_fg'], selectbackground=t['hl_cell'], selectforeground='black', highlightbackground=t['grid'], highlightcolor=t['grid'], insertbackground=t['cell_fg'])
        
        if hasattr(self, 'memo_entry') and self.memo_entry.get() != "메모를 입력하세요":
            self.memo_entry.config(bg=t.get('input_bg', t['cell_bg']), fg='black' if t['name'] == '웜 파스텔' else t['cell_fg'], insertbackground=t['cell_fg'], relief='flat', highlightthickness=1, highlightbackground=t.get('panel_border', t['grid']), highlightcolor=t.get('accent', t['hl_per']))
        elif hasattr(self, 'memo_entry'):
            self.memo_entry.config(bg=t.get('input_bg', t['cell_bg']), fg=t.get('muted_fg', 'gray'), insertbackground=t['cell_fg'], relief='flat', highlightthickness=1, highlightbackground=t.get('panel_border', t['grid']), highlightcolor=t.get('accent', t['hl_per']))
            
        if hasattr(self, 'search_btn'):
            self.style_toolbar_button(self.search_btn, 'accent')
        if hasattr(self, 'expand_btn'):
            self.style_toolbar_button(self.expand_btn, 'neutral')
            self.expand_btn.config(fg=t.get('accent', t['hl_per']))
        if hasattr(self, 'shrink_btn'):
            self.style_toolbar_button(self.shrink_btn, 'neutral')
            self.shrink_btn.config(fg=t.get('subtle_btn_fg', t.get('accent', t['hl_per'])))
        
        if hasattr(self, 'paned_window'): 
            self.paned_window.configure(bg=t['grid'])
        
        if hasattr(self, 'corner_lbl'):
            self.corner_lbl.configure(bg=t['head_bg'], fg=t['head_fg'], highlightbackground=t['head_bg'])

        if hasattr(self, 'acad_drag_bar'):
            self.acad_drag_bar.configure(bg=t.get('grid', '#eee'))
        
        if hasattr(self, 'sizegrip_nw'):
            for g in [self.sizegrip_nw, self.sizegrip_ne, self.sizegrip_n]:
                g.configure(bg=t['titlebar_bg'])
            for g in [self.sizegrip_sw, self.sizegrip_se, self.sizegrip_s]:
                g.configure(bg=t['bg'])
            for g in [self.sizegrip_w, self.sizegrip_e]:
                g.configure(bg=t['bg'])
                
        if hasattr(self, 'curr_btn'):
            self.style_toolbar_button(self.prev_btn, 'subtle')
            self.style_toolbar_button(self.curr_btn, 'neutral')
            self.style_toolbar_button(self.next_btn, 'subtle')
            self.style_toolbar_button(self.cal_btn, 'calendar')
            self.style_toolbar_button(self.memo_btn, 'memo')
            self.style_toolbar_button(self.zero_btn, 'lookup')
            self.style_toolbar_button(self.extra_btn, 'extra')
            self.style_toolbar_button(self.save_btn, 'accent')
            self.style_toolbar_button(self.settings_mb, 'neutral')

        self.apply_combobox_style()
        
        self.alpha_lbl.configure(bg=t['top'], fg=t.get('head_fg', 'white'))
        if hasattr(self, 'alpha_scale'):
            self.alpha_scale.set_colors(bg=t['top'], trough_color=t.get('panel_border', t['grid']), slider_color=t.get('accent', t['hl_per']))
            
        self.update_toolbar_state()

    def update_settings_menu(self):
        self.settings_menu = self.create_themed_menu(self.settings_mb)
        self.settings_mb.config(menu=self.settings_menu)
        self.settings_menu.delete(0, 'end')
        u = self.settings.get('logged_in_user')
        if u:
            self.add_menu_header(self.settings_menu, f"사용자 · {u}")
            self.settings_menu.add_command(label="로그아웃", command=self.logout)
            self.settings_menu.add_command(label="비밀번호 변경", command=self.change_password)
            if u == "표민호":
                self.settings_menu.add_command(label="관리자 비밀번호 초기화", command=self.reset_user_password)
            self.settings_menu.add_separator()

        is_locked = getattr(self, 'is_locked', False)
        self.settings_menu.add_command(label="화면 고정 풀기" if is_locked else "화면 고정하기", command=self.toggle_lock)

        is_topmost = getattr(self, 'is_topmost', False)
        self.settings_menu.add_command(label="일반창으로 전환" if is_topmost else "항상 위로 고정", command=self.toggle_topmost)

        is_autostart = getattr(self, 'auto_start', False)
        self.settings_menu.add_command(label="시작프로그램 해제" if is_autostart else "시작프로그램 등록", command=self.toggle_auto_start)
        self.settings_menu.add_separator()

        f_menu = self.create_themed_menu(self.settings_menu)
        self.add_menu_header(f_menu, "글꼴 변경")
        for f in ["맑은 고딕", "바탕", "돋움", "굴림", "Arial"]:
            f_menu.add_command(label=f, command=lambda val=f: self.apply_font(val))
        self.settings_menu.add_cascade(label="글꼴 변경", menu=f_menu)

        t_menu = self.create_themed_menu(self.settings_menu)
        self.add_menu_header(t_menu, "테마 변경")
        for i, theme in enumerate(self.themes):
            t_menu.add_command(label=theme['name'], command=lambda idx=i: self.apply_specific_theme(idx))
        self.settings_menu.add_cascade(label="테마 변경", menu=t_menu)

        alpha_menu = self.create_themed_menu(self.settings_menu)
        self.add_menu_header(alpha_menu, "투명도")
        for a in [100, 90, 80, 70, 60, 50]:
            alpha_menu.add_command(label=f"{a}%", command=lambda val=a: self.apply_alpha(val))
        self.settings_menu.add_cascade(label="투명도 조절", menu=alpha_menu)

        scale_menu = self.create_themed_menu(self.settings_menu)
        self.add_menu_header(scale_menu, "화면 배율")
        for s in ["80%", "100%", "120%", "150%", "200%"]:
            scale_menu.add_command(label=s, command=lambda val=s: self.apply_scale(val))
        self.settings_menu.add_cascade(label="화면 배율", menu=scale_menu)

        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="메모 전체 삭제", command=self.delete_all_memos)
        self.settings_menu.add_command(label="업데이트 확인 / 데이터 새로고침", command=self.refresh_supabase_base_data)
        self.settings_menu.add_command(label="데이터 경로/교사 목록 확인", command=self.show_data_source_info)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="메모 가져오기 (.txt/.csv)", command=self.import_memos)
        self.settings_menu.add_command(label="메모 내보내기 (.txt/.csv)", command=self.export_memos)
        self.settings_menu.add_command(label="크기 초기화", command=self.reset_size)
        self.settings_menu.add_separator()
        self.settings_menu.add_command(label="모바일 뷰어 안내", command=self.show_mobile_viewer_qr)
        self.settings_menu.add_command(label="프로그램 정보", command=self.show_program_info)

    def manual_save_db(self):
        u = self.settings.get('logged_in_user')
        if not u or not USE_SUPABASE: 
            messagebox.showinfo("저장", "로컬 저장 완료.")
            return
            
        try:
            requests.patch(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{u}", headers=HEADERS, json={"theme_idx": self.current_theme_idx, "font_name": self.settings.get('font_family', '맑은 고딕'), "show_zero": self.show_zero, "show_extra": self.show_extra, "show_memo": self.show_memo}, verify=False)
            if u in self.custom_data:
                for dk, sub in self.custom_data[u].items(): 
                    requests.post(f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", headers=HEADERS_UPSERT, json={"teacher_name": u, "date_key": dk, "subject": sub}, verify=False)
            if u in self.memos_data:
                for m in self.memos_data[u]:
                    if 'id' not in m:
                        r = requests.post(f"{SUPABASE_URL}/rest/v1/memos", headers=HEADERS, json={"teacher_name": u, "memo_text": m['text'], "is_strike": m.get('strike', False), "is_important": m.get('important', False)}, verify=False)
                        if r.status_code in [200, 201] and len(r.json()) > 0: 
                            m['id'] = r.json()[0]['id']
            messagebox.showinfo("성공", "클라우드 동기화 완료!")
        except Exception as e: 
            messagebox.showerror("에러", str(e))

    def change_password(self):
        u = self.settings.get('logged_in_user')
        if not u: return
        
        old_pw = simpledialog.askstring("비밀번호 변경", "현재 비밀번호를 입력하세요:", show='*', parent=self.root)
        if not old_pw: return
        
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{u}", headers=HEADERS, verify=False)
            data = r.json()
            if r.status_code == 200 and len(data) > 0:
                if str(data[0]['password']) == old_pw:
                    new_pw = simpledialog.askstring("비밀번호 변경", "새로운 비밀번호를 입력하세요:", show='*', parent=self.root)
                    if new_pw:
                        requests.patch(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{u}", headers=HEADERS, json={"password": new_pw}, verify=False)
                        messagebox.showinfo("성공", "비밀번호가 성공적으로 변경되었습니다.", parent=self.root)
                else:
                    messagebox.showerror("오류", "현재 비밀번호가 일치하지 않습니다.", parent=self.root)
        except Exception as e:
            messagebox.showerror("오류", f"비밀번호 변경 중 오류가 발생했습니다: {e}")

    def reset_user_password(self):
        target = simpledialog.askstring("관리자", "초기화할 이름:", parent=self.root)
        if target:
            requests.patch(f"{SUPABASE_URL}/rest/v1/users?teacher_name=eq.{target}", headers=HEADERS, json={"password": "1234"}, verify=False)
            messagebox.showinfo("성공", f"{target} 선생님의 비밀번호가 1234로 초기화됨.")

    def logout(self): 
        self.settings['logged_in_user'] = None
        self.settings['auto_login'] = False
        self.save_settings()
        self.build_login_ui()
    
    def on_alpha_slide(self, val): 
        self.root.attributes('-alpha', float(val))
        self.settings['alpha'] = float(val)
        
    def apply_alpha(self, percent): 
        val = percent / 100.0
        self.alpha_var.set(val)
        self.alpha_scale.set(val)
        self.on_alpha_slide(val)
    
    def apply_font(self, f_n): 
        self.settings['font_family'] = f_n
        fonts = [self.font_title, self.font_head, self.font_period, getattr(self, 'font_cell', None), getattr(self, 'font_cell_strike', None), getattr(self, 'font_timestamp', None), self.font_memo, self.font_memo_ts, getattr(self, 'font_memo_icon', None)]
        for f in fonts: 
            if f: f.config(family=f_n)
        for c in range(1, 6): 
            self.font_academic_cells[c].config(family=f_n)
        
        for cell_key, font_obj in getattr(self, 'dynamic_fonts', {}).items():
            font_obj.config(family=f_n)
            
        self.save_settings()
        
    def apply_specific_theme(self, idx): 
        self.current_theme_idx = idx
        self.apply_theme()
        self.refresh_schedule_display()
        self.update_time_and_date() 
        self.refresh_memo_list() 
        self.save_settings()
        
    def apply_scale(self, v): 
        r = int(v[:-1]) / 100.0
        self.scale_ratio = r
        nw = int(608 * r)
        logical_h = self.base_height_core + getattr(self, 'memo_extra_height', 0)
        nh = int(logical_h * r)
        self.root.geometry(f"{nw}x{nh}")
        self.update_font_size(nw)

    def _apply_dynamic_cell_font(self, r, c, text, is_strike, p_n):
        w = max(608, self.root.winfo_width())
        wrap_len = max(40, int(w / 6) - 15) 
        
        lines = text.split('\n')
        total_lines = 0
        
        for line in lines:
            if not line:
                continue
            estimated_pixels = len(line) * 12 
            if estimated_pixels > wrap_len:
                total_lines += (estimated_pixels // wrap_len) + 1
            else:
                total_lines += 1
                
        if total_lines == 0:
            total_lines = 1
            
        s = getattr(self, 'scale_ratio', 1.0)
        
        if p_n == "학사일정":
            base_sz = max(6, int(8 * s)) 
        else:
            base_sz = max(7, int(10 * s))
            
        if total_lines >= 6:
             target_sz = max(5, base_sz - 4)
        elif total_lines == 5:
            target_sz = max(6, base_sz - 3)
        elif total_lines == 4:
            target_sz = max(7, base_sz - 2)
        elif total_lines == 3:
            target_sz = max(8, base_sz - 1)
        else:
            target_sz = base_sz
            
        cell_key = f"cell_{r}_{c}"
        if not hasattr(self, 'dynamic_fonts'):
            self.dynamic_fonts = {}
            
        if cell_key not in self.dynamic_fonts:
            ff = self.settings.get('font_family', '맑은 고딕')
            self.dynamic_fonts[cell_key] = tkfont.Font(family=ff, size=target_sz, weight='bold')
            
        if text and text.split(maxsplit=1)[0] in ALL_STICKERS:
            target_sz += 2
        self.dynamic_fonts[cell_key].config(size=target_sz, overstrike=1 if is_strike else 0)
        if hasattr(self, 'cells') and cell_key in self.cells:
            self.cells[cell_key].config(font=self.dynamic_fonts[cell_key], wraplength=wrap_len)

    def check_input_limit(self, text):
        w = max(608, self.root.winfo_width())
        wrap_len = max(40, int(w / 6) - 15)
        
        lines = text.split('\n')
        total_lines = 0
        for line in lines:
            if not line: continue
            estimated_pixels = len(line) * 12 
            if estimated_pixels > wrap_len:
                 total_lines += (estimated_pixels // wrap_len) + 1
            else:
                total_lines += 1
        
        return total_lines <= 8

    def update_font_size(self, w):
        s = getattr(self, 'scale_ratio', w / 608)
        for f, sz in [(self.font_head, 10), (self.font_period, 8), (getattr(self, 'font_cell', None), 10), (getattr(self, 'font_cell_strike', None), 10)]: 
            if f: f.config(size=max(8, int(sz * s)))
        if hasattr(self, 'font_timestamp'):
            self.font_timestamp.config(size=max(6, int(7 * s)))
            
        if hasattr(self, 'font_memo'):
            m_sz = getattr(self, 'memo_font_size', 9)
            self.font_memo.config(size=max(7, int(m_sz * s)))
        if hasattr(self, 'font_memo_ts'):
            m_sz = getattr(self, 'memo_font_size', 9)
            self.font_memo_ts.config(size=max(5, int((m_sz - 2) * s)))
        if hasattr(self, 'font_memo_icon'):
            m_sz = getattr(self, 'memo_font_size', 9)
            self.font_memo_icon.config(size=max(7, int(m_sz * s)))
            
        if hasattr(self, 'memo_text'):
            wt = int(w)
            self.memo_text.config(tabs=(max(50, wt - 20), "right"))
            
        if hasattr(self, 'teacher_var'):
            self.refresh_schedule_display() 

    def on_teacher_select(self, ev=None): 
        self.current_schedule = self.teachers_data.get(self.teacher_var.get(), {d: [""]*9 for d in self.days})
        self.week_offset = 0 
        self.selected_memo_indices.clear()
        self.last_clicked_idx = None
        self.refresh_schedule_display()
        self.refresh_memo_list()
        self.save_settings()

    def toggle_calendar(self):
        if hasattr(self, 'cal_window') and self.cal_window.winfo_exists():
            self.cal_window.destroy()
            return
            
        x = self.cal_btn.winfo_rootx()
        y = self.cal_btn.winfo_rooty() + self.cal_btn.winfo_height()
        
        target_date = datetime.now() + timedelta(weeks=self.week_offset)
        self.cal_window = ModernCalendar(self.root, self.themes[self.current_theme_idx], target_date, self.on_calendar_select)
        self.cal_window.geometry(f"+{x}+{y}")
        self.update_toolbar_state()
        
    def on_calendar_select(self, selected_date):
        now = datetime.now()
        target_monday = selected_date - timedelta(days=selected_date.weekday())
        current_monday = now.date() - timedelta(days=now.weekday())
        self.week_offset = (target_monday - current_monday).days // 7
        self.refresh_schedule_display()
        self.update_time_and_date()
        self.update_toolbar_state()

    def prev_week(self): 
        self.week_offset -= 1
        self.refresh_schedule_display()
        self.update_time_and_date()
        self.update_toolbar_state()
        
    def next_week(self): 
        self.week_offset += 1
        self.refresh_schedule_display()
        self.update_time_and_date()
        self.update_toolbar_state()
        
    def curr_week(self): 
        self.week_offset = 0
        self.refresh_schedule_display()
        self.update_time_and_date()
        self.update_toolbar_state()

    def toggle_zero(self): 
        self.show_zero = not getattr(self, 'show_zero', False)
        self.resize_window_for_rows()
        self.update_toolbar_state()
        
    def toggle_extra(self): 
        self.show_extra = not getattr(self, 'show_extra', False)
        self.resize_window_for_rows()
        self.update_toolbar_state()
        
    def toggle_memo(self):
        self.show_memo = not getattr(self, 'show_memo', True)
        if self.show_memo: 
            self.paned_window.add(self.memo_frame, stretch="always")
            self.memo_extra_height = 0
        else: 
            self.paned_window.forget(self.memo_frame)
            self.memo_extra_height = 0 
        self.resize_window_for_rows()
        self.update_toolbar_state()

    def resize_window_for_rows(self):
        nh = self.base_height_core + getattr(self, 'memo_extra_height', 0)
        s = getattr(self, 'scale_ratio', 1.0)
        nh = int(nh * s)
        w = max(int(608 * s), self.root.winfo_width())
        self.root.geometry(f"{w}x{nh}")
        self.apply_row_visibility()
        self.apply_theme()
        self.update_font_size(w)
        self.save_settings()
        
        self.root.update_idletasks()
        target_sash_y = 485
        if getattr(self, 'show_zero', False): target_sash_y += 40
        if getattr(self, 'show_extra', False): target_sash_y += 80
        try:
            self.paned_window.sash_place(0, 0, int(target_sash_y * s))
        except: pass
    
    def apply_row_visibility(self):
        s = getattr(self, 'scale_ratio', 1.0)
        base_min = int(28 * s)
        
        if getattr(self, 'show_zero', False):
            self.grid_frame.rowconfigure(2, weight=1, minsize=base_min)
            self.cells["period_2"].grid()
            for c in range(1, 6): 
                self.cells[f"cell_2_{c}"].grid()
        else:
            self.grid_frame.rowconfigure(2, weight=0, minsize=0)
            self.cells["period_2"].grid_remove()
            for c in range(1, 6): 
                self.cells[f"cell_2_{c}"].grid_remove()
            
        for r in [11, 12]:
            if getattr(self, 'show_extra', False):
                self.grid_frame.rowconfigure(r, weight=1, minsize=base_min)
                self.cells[f"period_{r}"].grid()
                for c in range(1, 6): 
                    self.cells[f"cell_{r}_{c}"].grid()
            else:
                self.grid_frame.rowconfigure(r, weight=0, minsize=0)
                self.cells[f"period_{r}"].grid_remove()
                for c in range(1, 6): 
                    self.cells[f"cell_{r}_{c}"].grid_remove()

    def create_grid(self):
        s = getattr(self, 'scale_ratio', 1.0)
        base_min = int(28 * s)
        self.grid_frame.columnconfigure(0, weight=0)
        for c in range(1, 6): 
            self.grid_frame.columnconfigure(c, weight=1, uniform="day_cols")
            
        for r in range(len(self.period_times)+1): 
            self.grid_frame.rowconfigure(r, weight=1, minsize=base_min)
            
        self.corner_lbl = tk.Label(self.grid_frame, text="교시", font=self.font_head, highlightthickness=1, bd=0, padx=6, pady=6)
        self.corner_lbl.grid(row=0, column=0, sticky='nsew', pady=1, padx=1)
        
        for c, day in enumerate(self.days, 1):
            lbl = tk.Label(self.grid_frame, text=day, font=self.font_head, highlightthickness=1, bd=0, padx=6, pady=6)
            lbl.grid(row=0, column=c, sticky='nsew', pady=1, padx=1)
            self.cells[f"header_{c}"] = lbl
            
        for r, (p, s_t, e_t) in enumerate(self.period_times, 1):
            time_text = f"{p}\n{s_t}~{e_t}" if s_t and e_t else p
            p_lbl = tk.Label(self.grid_frame, text=time_text, font=self.font_period, highlightthickness=1, bd=0, padx=4, pady=4)
            p_lbl.grid(row=r, column=0, sticky='nsew', pady=1, padx=1)
            p_lbl.bind('<Button-1>', self.click_window)
            p_lbl.bind('<B1-Motion>', self.drag_window)
            self.cells[f"period_{r}"] = p_lbl
            
            for c in range(1, 6):
                cell = tk.Label(self.grid_frame, text="", font=getattr(self, 'font_cell', self.font_period), highlightthickness=1, bd=0, cursor="hand2", padx=6, pady=6, justify='center')
                cell.grid(row=r, column=c, sticky='nsew', pady=1, padx=1)
                cell.bind("<Button-1>", lambda ev, r=r, c=c: self.on_cell_single_click(ev, r, c))
                cell.bind("<Double-Button-1>", lambda ev, r=r, c=c: self.on_cell_double_click(ev, r, c))
                self.bind_context_popup(cell, lambda ev, r=r, c=c: self.show_cell_context_menu(ev, r, c))
                self.bind_cell_hover(cell)
                self.cells[f"cell_{r}_{c}"] = cell
                
        self.acad_drag_bar = tk.Frame(self.grid_frame, cursor="sb_v_double_arrow", height=4, bg='gray')
        self.acad_drag_bar.grid(row=1, column=0, columnspan=6, sticky='sew')
        self.acad_drag_bar.tkraise()
        self.acad_drag_bar.bind("<Button-1>", self.start_acad_resize)
        self.acad_drag_bar.bind("<B1-Motion>", self.do_acad_resize)

        self.refresh_schedule_display()

    @property
    def base_height_core(self):
        h = 485
        if getattr(self, 'show_zero', False): 
            h += 40
        if getattr(self, 'show_extra', False): 
            h += 80
        if getattr(self, 'show_memo', True): 
            h += 260 
        return h

    # ==========================================
    # 💡 스케줄 동적 갱신
    # ==========================================
    def refresh_schedule_display(self):
        if not hasattr(self, 'teacher_var') or not hasattr(self, 'current_schedule'): 
            return
            
        u = self.teacher_var.get()
        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        can_view = self.can_view_private_data()
        data = self.custom_data.get(u, {}) if can_view else {}
        
        t = self.themes[self.current_theme_idx]
        
        for r, (p, s_t, e_t) in enumerate(self.period_times, 1):
            for c, d in enumerate(self.days, 1):
                date_str = (monday+timedelta(days=c-1)).strftime('%Y-%m-%d')
                key = self.get_cell_key(date_str, r)
                
                if p == "학사일정":
                    sub = self.academic_schedule.get(date_str, "")
                elif p in ["점심", "조회"]: 
                    sub = "" 
                else:
                    sched = self.current_schedule.get(d, [])
                    idx = r - 3 if r < 8 else r - 4
                    sub = sched[idx] if 0 <= idx < len(sched) else ""
                
                is_strike = False
                fg_c = None
                bg_c = None
                
                if key in data:
                    val = data[key]
                    if val == "__STRIKE__":
                        is_strike = True
                    elif val.startswith("__STRIKE__|||"):
                        is_strike = True
                        text, fg_c, bg_c = self.parse_text_styles(val.split("|||", 1)[1])
                        sub = text
                    else:
                        text, fg_c, bg_c = self.parse_text_styles(val)
                        sub = text
                
                if p == "학사일정": 
                    default_fg = t.get('acad_cell_fg', t['cell_fg'])
                else: 
                    default_fg = t['cell_fg']
                    
                if p == "학사일정":
                    sub = sub.replace(' / ', '\n')
                self._apply_dynamic_cell_font(r, c, sub, is_strike, p)
                
                if p == "학사일정":
                    self.cells[f"cell_{r}_{c}"].config(fg=fg_c if fg_c else default_fg, bg=bg_c if bg_c else t.get('acad_cell_bg', t['lunch_bg']))
                else:
                    self.cells[f"cell_{r}_{c}"].config(fg=fg_c if fg_c else default_fg, bg=bg_c if bg_c else (t['lunch_bg'] if p in ["점심", "조회"] else t['cell_bg']))
                
                self.cells[f"cell_{r}_{c}"].config(text=sub)
                if hasattr(self.cells[f"cell_{r}_{c}"], '_orig_bg'):
                    self.cells[f"cell_{r}_{c}"]._orig_bg = self.cells[f"cell_{r}_{c}"].cget('bg')

    def update_time_and_date(self):
        now = datetime.now()
        mnd = now + timedelta(weeks=self.week_offset) - timedelta(days=now.weekday())
        t = self.themes[self.current_theme_idx]
        cur_d = now.weekday() + 1
        is_cur_w = (self.week_offset == 0)
        
        for c, d in enumerate(self.days, 1):
            self.cells[f"header_{c}"].config(text=f"{d} ({(mnd+timedelta(days=c-1)).strftime('%m/%d')})", bg=t['hl_per'] if (is_cur_w and c==cur_d) else t['head_bg'], fg='white' if (is_cur_w and c==cur_d and t['name']!='웜 파스텔') else t['head_fg'])
            
        now_m = now.hour * 60 + now.minute
        act_r, pre_r = None, None
        for r, (p, s_t, e_t) in enumerate(self.period_times, 1):
            if not s_t or not e_t: 
                continue
            sm = int(s_t.split(':')[0]) * 60 + int(s_t.split(':')[1])
            em = int(e_t.split(':')[0]) * 60 + int(e_t.split(':')[1])
            if sm <= now_m <= em: 
                act_r = r
                pre_r = r + 1 if p == "점심" else None
                break
            elif now_m < sm: 
                pre_r = r
                break
                
        for r in range(1, len(self.period_times)+1):
            p_n = self.period_times[r-1][0]
            per_bg = t.get('acad_per_bg', t['per_bg']) if p_n == "학사일정" else t['per_bg']
            per_fg = t.get('acad_per_fg', t['per_fg']) if p_n == "학사일정" else t['per_fg']
            self.cells[f"period_{r}"].config(bg=per_bg, fg=per_fg, highlightbackground=per_bg)
            
            for c in range(1, 6): 
                if p_n == "학사일정": 
                    bg_col = t.get('acad_cell_bg', t['lunch_bg'])
                else: 
                    bg_col = t['lunch_bg'] if p_n in ["점심", "조회"] else t['cell_bg']
                self.cells[f"cell_{r}_{c}"].config(bg=bg_col, fg=t['cell_fg'], highlightbackground=bg_col)
        
        self.refresh_schedule_display()
                 
        if is_cur_w:
            if act_r:
                self.cells[f"period_{act_r}"].config(bg=t['hl_per'], fg='white' if t['name']!='웜 파스텔' else 'black', highlightbackground=t['hl_per'])
                if 1 <= cur_d <= 5: 
                    self.cells[f"cell_{act_r}_{cur_d}"].config(bg=t['hl_cell'], fg='black', highlightbackground=t['hl_cell'])
                    self.cells[f"cell_{act_r}_{cur_d}"]._orig_bg = t['hl_cell']
            if pre_r and 1 <= cur_d <= 5: 
                self.cells[f"period_{pre_r}"].config(highlightbackground=t['hl_per'])
                self.cells[f"cell_{pre_r}_{cur_d}"].config(highlightbackground=t['hl_cell'])
                
        self.update_toolbar_state()

    # ==========================================
    # 💡 셀 클릭/마우스 이벤트
    # ==========================================
    def show_cell_context_menu(self, event, row, col):
        if not self.can_view_private_data(): 
            return 'break'

        teacher = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not teacher: 
            return 'break'

        menu = self.create_themed_menu(self.root)
        self.add_menu_header(menu, "시간표 메뉴")
        menu.add_command(label="수정하기", command=lambda: self.process_single_click(row, col))
        menu.add_command(label="반복 입력", command=lambda: self.repeat_entry(row, col))
        menu.add_command(label="완료 표시", command=lambda: self.process_double_click(row, col))
        menu.add_separator()

        sticker_menu = self.build_sticker_menu(menu, lambda e: self.add_sticker_to_cell(row, col, e))
        menu.add_cascade(label="스티커", menu=sticker_menu)

        color_menu = self.create_themed_menu(menu)
        self.add_menu_header(color_menu, "글자색")
        colors = [("기본색으로", ""), ("빨간색", "#e74c3c"), ("파란색", "#3498db"), ("초록색", "#27ae60"), ("보라색", "#9b59b6"), ("핑크색", "#ff66b2")]
        for name, code in colors:
            self.add_color_command(color_menu, name, code, lambda r=row, c=col, color=code: self.change_cell_color(r, c, color))
        menu.add_cascade(label="글자색", menu=color_menu)

        highlight_menu = self.create_themed_menu(menu)
        self.add_menu_header(highlight_menu, "하이라이트")
        h_colors = [("기본색으로", ""), ("노란색", "#f1c40f"), ("연녹색", "#a2d9ce"), ("연하늘", "#aed6f1"), ("연분홍", "#f5b7b1"), ("회색", "#d5d8dc"), ("핑크색", "#ff99cc")]
        for name, code in h_colors:
            self.add_color_command(highlight_menu, name, code, lambda r=row, c=col, color=code: self.change_cell_highlight(r, c, color))
        menu.add_cascade(label="하이라이트", menu=highlight_menu)

        menu.add_separator()
        menu.add_command(label="내용 삭제", command=lambda: self.delete_cell_data(row, col))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        except Exception:
            try:
                menu.post(event.x_root, event.y_root)
            except Exception:
                pass
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return 'break'

    def change_cell_color(self, r, c, color):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
        
        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        date_str = (monday + timedelta(days=c-1)).strftime('%Y-%m-%d')
        key = self.get_cell_key(date_str, r)
        
        p_n = self.period_times[r-1][0]
        
        if p_n == "학사일정": 
            orig = self.academic_schedule.get(date_str, "")
        elif p_n in ["점심", "조회"]: 
            orig = ""
        else:
            s_l = self.current_schedule.get(self.days[c-1], [])
            idx = r - 3 if r < 8 else r - 4
            orig = s_l[idx] if 0 <= idx < len(s_l) else ""

        cur_v = self.custom_data.get(u, {}).get(key, orig)
        is_struck = False
        if cur_v == "__STRIKE__":
            cur_v = orig
        elif cur_v.startswith("__STRIKE__|||"):
            is_struck = True
            cur_v = cur_v.split("|||", 1)[1]
        elif not cur_v:
            cur_v = orig
            
        if not cur_v: 
            return
            
        clean_text, _, bg = self.parse_text_styles(cur_v)
        new_v = self.build_styled_text(clean_text, color, bg)
        if is_struck:
            new_v = "__STRIKE__|||" + new_v
            
        self.custom_data.setdefault(u, {})[key] = new_v
        if USE_SUPABASE: 
            self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": new_v})
            
        self.save_custom_data()
        self.push_history()
        self.refresh_schedule_display()
        self.update_time_and_date()

    def change_cell_highlight(self, r, c, bg_color):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
        
        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        date_str = (monday + timedelta(days=c-1)).strftime('%Y-%m-%d')
        key = self.get_cell_key(date_str, r)
        
        p_n = self.period_times[r-1][0]
        
        if p_n == "학사일정": 
            orig = self.academic_schedule.get(date_str, "")
        elif p_n in ["점심", "조회"]: 
            orig = ""
        else:
            s_l = self.current_schedule.get(self.days[c-1], [])
            idx = r - 3 if r < 8 else r - 4
            orig = s_l[idx] if 0 <= idx < len(s_l) else ""

        cur_v = self.custom_data.get(u, {}).get(key, orig)
        is_struck = False
        if cur_v == "__STRIKE__":
            cur_v = orig
        elif cur_v.startswith("__STRIKE__|||"):
            is_struck = True
            cur_v = cur_v.split("|||", 1)[1]
        elif not cur_v:
            cur_v = orig
            
        if not cur_v: 
            return
            
        clean_text, fg, _ = self.parse_text_styles(cur_v)
        new_v = self.build_styled_text(clean_text, fg, bg_color)
        if is_struck:
            new_v = "__STRIKE__|||" + new_v
            
        self.custom_data.setdefault(u, {})[key] = new_v
        if USE_SUPABASE: 
            self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": new_v})
            
        self.save_custom_data()
        self.push_history()
        self.refresh_schedule_display()
        self.update_time_and_date()

    def delete_cell_data(self, row, col):
        if not self.can_view_private_data(): 
            return
            
        teacher = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not teacher: 
            return

        if not messagebox.askyesno("삭제 확인", "해당 내용을 삭제하시겠습니까?"):
            return

        now = datetime.now()
        target_date = now + timedelta(weeks=self.week_offset)
        monday = target_date - timedelta(days=target_date.weekday())
        date_str = (monday + timedelta(days=col-1)).strftime('%Y-%m-%d')
        date_key = self.get_cell_key(date_str, row)

        if teacher in self.custom_data and date_key in self.custom_data[teacher]:
            del self.custom_data[teacher][date_key]
            
            if USE_SUPABASE:
                self._async_db_task('DELETE', f"{SUPABASE_URL}/rest/v1/custom_schedule?teacher_name=eq.{teacher}&date_key=eq.{date_key}")
                
            self.save_custom_data()
            self.push_history()
            self.refresh_schedule_display()
            self.update_time_and_date()

    def on_cell_single_click(self, event, row, col):
        if not self.can_view_private_data(): 
            return
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        self.click_timer = self.root.after(250, lambda: self.process_single_click(row, col))

    def on_cell_double_click(self, event, row, col):
        if not self.can_view_private_data(): 
            return
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
            self.click_timer = None
        self.process_double_click(row, col)

    def repeat_entry(self, r, c):
        if not self.can_view_private_data(): return
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: return

        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        date_str = (monday + timedelta(days=c-1)).strftime('%Y-%m-%d')
        key = self.get_cell_key(date_str, r)

        p_n = self.period_times[r-1][0]
        if p_n == "학사일정": orig = self.academic_schedule.get(date_str, "")
        elif p_n in ["점심", "조회"]: orig = ""
        else:
            s_l = self.current_schedule.get(self.days[c-1], [])
            idx = r - 3 if r < 8 else r - 4
            orig = s_l[idx] if 0 <= idx < len(s_l) else ""

        cur_v = self.custom_data.get(u, {}).get(key, orig)
        if cur_v == "__STRIKE__": cur_v = ""
        elif cur_v.startswith("__STRIKE__|||"):
            cur_v = cur_v.split("|||", 1)[1]
            cur_v, _, _ = self.parse_text_styles(cur_v)
        else:
            cur_v, _, _ = self.parse_text_styles(cur_v)

        new_t = simpledialog.askstring("반복입력", "매주 반복할 내용을 입력하세요:", parent=self.root, initialvalue=cur_v)
        if not new_t or not new_t.strip(): return

        weeks = simpledialog.askinteger("반복입력", "몇 주 동안 반복하시겠습니까? (예: 4)", parent=self.root, minvalue=1, maxvalue=20)
        if not weeks: return

        for w in range(weeks):
            target_date = monday + timedelta(weeks=w) + timedelta(days=c-1)
            target_date_str = target_date.strftime('%Y-%m-%d')
            target_key = self.get_cell_key(target_date_str, r)

            self.custom_data.setdefault(u, {})[target_key] = new_t.strip()
            if USE_SUPABASE:
                self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": target_key, "subject": new_t.strip()})

        self.save_custom_data()
        self.push_history()
        self.refresh_schedule_display()
        self.update_time_and_date()
        messagebox.showinfo("완료", f"{weeks}주 동안 반복 입력이 완료되었습니다.", parent=self.root)

    def process_single_click(self, r, c):
        if not self.can_view_private_data(): 
            return
            
        self.click_timer = None
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
        
        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        date_str = (monday + timedelta(days=c-1)).strftime('%Y-%m-%d')
        key = self.get_cell_key(date_str, r)
        
        p_n = self.period_times[r-1][0]
        if p_n == "학사일정": 
            orig = self.academic_schedule.get(date_str, "")
        elif p_n in ["점심", "조회"]:
            orig = ""
        else:
            s_l = self.current_schedule.get(self.days[c-1], [])
            idx = r - 3 if r < 8 else r - 4
            orig = s_l[idx] if 0 <= idx < len(s_l) else ""
            
        cur_v = self.custom_data.get(u, {}).get(key, orig)
        is_struck = False
        if cur_v == "__STRIKE__": 
            cur_v = ""
            fg_color = None
            bg_color = None
        elif cur_v.startswith("__STRIKE__|||"):
            is_struck = True
            cur_v, fg_color, bg_color = self.parse_text_styles(cur_v.split("|||", 1)[1])
        else:
            cur_v, fg_color, bg_color = self.parse_text_styles(cur_v)
        
        edit_win = tk.Toplevel(self.root)
        edit_win.title("내용 입력")
        
        w, h = 330, 120
        x = self.root.winfo_pointerx() - (w // 2)
        y = self.root.winfo_pointery() - (h // 2)
        edit_win.geometry(f"{w}x{h}+{x}+{y}")
        
        edit_win.attributes('-topmost', True)
        edit_win.configure(bg='#ecf0f1')
        edit_win.resizable(False, False)
        
        tk.Label(edit_win, text="수업/일정 내용:", bg='#ecf0f1', font=('맑은 고딕', 9, 'bold')).pack(anchor='w', padx=15, pady=(10, 2))
        entry_var = tk.StringVar(value=cur_v)
        entry = tk.Entry(edit_win, textvariable=entry_var, font=('맑은 고딕', 10))
        entry.pack(fill='x', padx=15, pady=2, ipady=4)
        entry.focus_set()

        def on_save(event=None):
            new_v = entry_var.get().strip()
            if not new_v: 
                self.custom_data.get(u, {}).pop(key, None)
                if USE_SUPABASE: 
                    self._async_db_task('DELETE', f"{SUPABASE_URL}/rest/v1/custom_schedule?teacher_name=eq.{u}&date_key=eq.{key}")
            else: 
                clean_text, _, _ = self.parse_text_styles(new_v)
                if not self.check_input_limit(clean_text):
                    messagebox.showwarning("입력 제한", "칸에 입력할 수 있는 최대 범위를 초과했습니다.", parent=edit_win)
                    return
                
                save_v = self.build_styled_text(new_v, fg_color, bg_color)
                if is_struck:
                    save_v = "__STRIKE__|||" + save_v
                    
                self.custom_data.setdefault(u, {})[key] = save_v
                if USE_SUPABASE: 
                    self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": save_v})
                    
            self.save_custom_data()
            self.push_history()
            self.refresh_schedule_display()
            self.update_time_and_date()
            edit_win.destroy()
            
        def on_delete():
            entry_var.set("")
            on_save()
        
        btn_f = tk.Frame(edit_win, bg='#ecf0f1')
        btn_f.pack(fill='x', padx=15, pady=10)
        tk.Button(btn_f, text="저장", bg='#27ae60', fg='white', font=('맑은 고딕', 9, 'bold'), width=8, bd=0, command=on_save).pack(side='left', padx=2)
        tk.Button(btn_f, text="삭제", bg='#e74c3c', fg='white', font=('맑은 고딕', 9, 'bold'), width=8, bd=0, command=on_delete).pack(side='left', padx=2)
        tk.Button(btn_f, text="취소", bg='#7f8c8d', fg='white', font=('맑은 고딕', 9, 'bold'), width=8, bd=0, command=edit_win.destroy).pack(side='right', padx=2)
        
        entry.bind('<Return>', on_save)

    def process_double_click(self, r, c):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
        
        monday = datetime.now() + timedelta(weeks=self.week_offset) - timedelta(days=datetime.now().weekday())
        date_str = (monday + timedelta(days=c-1)).strftime('%Y-%m-%d')
        key = self.get_cell_key(date_str, r)
        
        p_n = self.period_times[r-1][0]
        if p_n == "학사일정": 
            orig = self.academic_schedule.get(date_str, "")
        elif p_n in ["점심", "조회"]:
            orig = ""
        else:
            s_l = self.current_schedule.get(self.days[c-1], [])
            idx = r - 3 if r < 8 else r - 4
            orig = s_l[idx] if 0 <= idx < len(s_l) else ""

        if key in self.custom_data.get(u, {}):
            val = self.custom_data[u][key]
            if val == "__STRIKE__": 
                self.custom_data[u].pop(key)
                if USE_SUPABASE: 
                    self._async_db_task('DELETE', f"{SUPABASE_URL}/rest/v1/custom_schedule?teacher_name=eq.{u}&date_key=eq.{key}")
            elif val.startswith("__STRIKE__|||"): 
                new_val = val.split("|||", 1)[1]
                self.custom_data[u][key] = new_val
                if USE_SUPABASE: 
                    self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": new_val})
            else: 
                new_val = "__STRIKE__|||" + val
                self.custom_data[u][key] = new_val
                if USE_SUPABASE: 
                    self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": new_val})
        else:
            if orig.strip() != "":
                self.custom_data.setdefault(u, {})[key] = "__STRIKE__"
                if USE_SUPABASE: 
                    self._async_db_task('POST', f"{SUPABASE_URL}/rest/v1/custom_schedule?on_conflict=teacher_name,date_key", HEADERS_UPSERT, {"teacher_name": u, "date_key": key, "subject": "__STRIKE__"})
                    
        self.save_custom_data()
        self.push_history()
        self.refresh_schedule_display()
        self.update_time_and_date()

    # ==========================================
    # 💡 4. 메모 관련 로직
    # ==========================================
    def toggle_memo_group(self, ev, group):
        self.memo_group_collapsed[group] = not self.memo_group_collapsed.get(group, False)
        self.refresh_memo_list()

    def expand_memo(self):
        if self.memo_font_size < 18:
            self.memo_font_size += 1
            self.memo_spacing += 1
            self.font_memo.config(size=self.memo_font_size)
            self.font_memo_ts.config(size=max(6, self.memo_font_size - 2))
            self.memo_text.config(spacing1=self.memo_spacing, spacing3=self.memo_spacing)
            self.save_settings()
            self.refresh_memo_list()

    def shrink_memo(self):
        if self.memo_font_size > 7:
            self.memo_font_size -= 1
            self.memo_spacing = max(0, self.memo_spacing - 1)
            self.font_memo.config(size=self.memo_font_size)
            self.font_memo_ts.config(size=max(6, self.memo_font_size - 2))
            self.memo_text.config(spacing1=self.memo_spacing, spacing3=self.memo_spacing)
            self.save_settings()
            self.refresh_memo_list()

    def edit_memo_by_idx(self, idx):
        self.selected_memo_indices = {idx}
        self.edit_memo()

    def delete_memo_by_idx(self, idx):
        self.selected_memo_indices = {idx}
        self.delete_memo()
        
    def toggle_memo_important_by_idx(self, idx):
        self.selected_memo_indices = {idx}
        self.toggle_memo_important()

    def add_memo(self, ev=None):
        if not self.can_view_private_data(): 
            return "break"
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        text = getattr(self, 'memo_entry', tk.Entry()).get().strip()
        
        if text == "메모를 입력하세요" or not text:
            return "break"
            
        if u and text:
            now_iso = datetime.now().isoformat()
            new_memo = {'text': text, 'strike': False, 'important': False, 'created_at': now_iso}
            self.memos_data.setdefault(u, []).insert(0, new_memo)
            
            if USE_SUPABASE:
                def task():
                    try:
                        r = requests.post(f"{SUPABASE_URL}/rest/v1/memos", headers=HEADERS, json={"teacher_name": u, "memo_text": text}, verify=False)
                        if r.status_code in [200, 201] and len(r.json()) > 0: 
                            new_memo['id'] = r.json()[0]['id']
                            self.save_memos()
                    except: pass
                threading.Thread(target=task, daemon=True).start()
                
            self.memo_entry.delete(0, tk.END)
            self.push_history()
            self.refresh_memo_list()
            self.save_memos()
            self.update_time_and_date()
            
        return "break"

    def refresh_memo_list(self):
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
        
        self.memo_text.config(state='normal')
        self.memo_text.delete('1.0', tk.END)
        self.memo_line_map.clear()
        
        t = self.themes[self.current_theme_idx]
        
        if not self.can_view_private_data():
            self.memo_text.insert(tk.END, "\n  🔒 비공개 메모 및 기록입니다.\n  (본인 또는 마스터 계정만 열람 가능)\n")
            self.memo_text.config(state='disabled')
            return

        if u not in self.memos_data or not self.memos_data[u]:
            self.memo_text.config(state='disabled')
            return
            
        memos = self.memos_data[u]
        count_strike = sum(1 for m in memos if m.get('strike', False))
        count_important = sum(1 for m in memos if m.get('important', False) and not m.get('strike', False))
        count_general = len(memos) - count_strike - count_important
            
        self.memos_data[u].sort(key=lambda x: (
            1 if x.get('strike', False) else 0, 
            0 if x.get('important', False) else 1
        ))
        
        total = len(self.memos_data[u])
        last_group = None
        
        sep_color = '#fadbd8' if t['name'] != '모던 다크' else '#4a2b2b'
        
        for i, m in enumerate(self.memos_data[u]):
            is_strike = m.get('strike', False)
            is_important = m.get('important', False)
            
            if is_strike:
                group = "strike"
                group_title = f" ✔ 완료 메모 ({count_strike})"
                group_color = "#95a5a6"
            elif is_important:
                group = "important"
                group_title = f" 📌 중요 메모 ({count_important})"
                group_color = "#e74c3c"
            else:
                group = "general"
                group_title = f" 📝 일반 메모 ({count_general})"
                group_color = t['cell_fg']
                
            if group != last_group:
                is_collapsed = self.memo_group_collapsed.get(group, False)
                arrow = "▼" if is_collapsed else "▲"
                header_text = f"{group_title} {arrow}\n"
                
                self.memo_text.insert(tk.END, header_text, f"header_{group}")
                self.memo_text.tag_configure(f"header_{group}", font=('맑은 고딕', 9, 'bold'), foreground=group_color, spacing1=6, spacing3=2, justify='left')
                self.memo_text.tag_bind(f"header_{group}", "<Button-1>", lambda e, g=group: self.toggle_memo_group(e, g))
                last_group = group
            
            if self.memo_group_collapsed.get(group, False):
                continue
                
            line_str = self.memo_text.index("end-1c").split('.')[0]
            self.memo_line_map[int(line_str)] = i
            
            pref = "⭐ " if is_important else "☆ "
            clean_text, fg_color, bg_color = self.parse_text_styles(m['text'])
            cb = "✔" if is_strike else "○"
            
            try:
                dt_str = m.get('created_at', datetime.now().isoformat()).replace('Z', '+00:00')
                if "T" in dt_str: 
                    dt = datetime.fromisoformat(dt_str[:19])
                else: 
                    dt = datetime.now()
                ts_str = f" {dt.strftime('%m.%d %H:%M')}"
            except:
                ts_str = ""

            start_idx = self.memo_text.index("insert")
            
            self.memo_text.insert(tk.END, f"{cb} ", "checkbox_on" if is_strike else "checkbox_off")
            self.memo_text.insert(tk.END, pref, "important_star" if is_important else "unimportant_star")
            
            text_start = self.memo_text.index("insert")
            self.memo_text.insert(tk.END, f"{total-i}.{clean_text}")
            text_end = self.memo_text.index("insert")
            
            ts_tag = f"ts_{i}"
            color = fg_color if fg_color else t['cell_fg']
            self.memo_text.tag_configure(ts_tag, font=self.font_memo_ts, foreground=color)
            
            self.memo_text.insert(tk.END, f"\t{ts_str}\n", ts_tag)
            end_idx = self.memo_text.index("insert")
            
            sep_frame = tk.Frame(self.memo_text, height=1, width=3000, bg=sep_color)
            self.memo_text.window_create(tk.END, window=sep_frame)
            
            if fg_color or bg_color:
                tag_name = f"style_{i}"
                kwargs = {}
                if fg_color: 
                    kwargs['foreground'] = fg_color
                if bg_color: 
                    kwargs['background'] = bg_color
                self.memo_text.tag_configure(tag_name, **kwargs)
                self.memo_text.tag_add(tag_name, text_start, text_end)
                
            if is_strike: 
                self.memo_text.tag_add("strike", text_start, text_end)
            
            if i in getattr(self, 'selected_memo_indices', set()):
                self.memo_text.tag_add("selected_row", start_idx, end_idx)
                
        try:
            self.memo_text.tag_raise("search_highlight")
        except: pass
        
        self.memo_text.tag_raise("selected_row")
        self.memo_text.config(state='disabled')

    def on_memo_click(self, ev):
        if not self.can_view_private_data(): 
            return "break"
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u): 
            return "break"
        
        idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
        line, col = map(int, idx_str.split('.'))
        
        if line not in self.memo_line_map:
            return "break"
            
        clicked_idx = self.memo_line_map[line]
        
        tags = self.memo_text.tag_names(idx_str)
        char_clicked = self.memo_text.get(f"{line}.{col}", f"{line}.{col+1}")
        
        if "important_star" in tags or "unimportant_star" in tags or char_clicked in ["☆", "⭐"]:
            self.toggle_memo_important_by_idx(clicked_idx)
            return "break"
        elif "checkbox_on" in tags or "checkbox_off" in tags or col <= 2:
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
            
        self.refresh_memo_list()
        return "break"

    def on_memo_drag(self, ev):
        if not self.can_view_private_data(): 
            return "break"
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u): 
            return "break"
        
        idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
        line, _ = map(int, idx_str.split('.'))
        
        if line not in self.memo_line_map:
            return "break"
            
        current_idx = self.memo_line_map[line]
        
        if getattr(self, 'last_clicked_idx', None) is not None:
            start = min(self.last_clicked_idx, current_idx)
            end = max(self.last_clicked_idx, current_idx)
            
            new_selection = set(range(start, end + 1))
            if self.selected_memo_indices != new_selection:
                self.selected_memo_indices = new_selection
                self.refresh_memo_list()
        return "break"

    def on_memo_double_click(self, ev): 
        if not self.can_view_private_data(): 
            return "break"
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u): 
            return "break"
            
        idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
        line, col = map(int, idx_str.split('.'))
        
        if line not in self.memo_line_map:
            return "break"
            
        clicked_idx = self.memo_line_map[line]
        self.selected_memo_indices = {clicked_idx}
        self.last_clicked_idx = clicked_idx
        self.refresh_memo_list()
        self.edit_memo()
            
        return "break"
    
    def show_memo_context_menu(self, ev):
        if not self.can_view_private_data(): 
            return 'break'

        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.memos_data.get(u): 
            return 'break'

        idx_str = self.memo_text.index(f"@{ev.x},{ev.y}")
        line_str = int(idx_str.split('.')[0])

        if line_str not in self.memo_line_map:
            return 'break'

        r_click_idx = self.memo_line_map[line_str]

        if r_click_idx not in self.selected_memo_indices:
            self.selected_memo_indices = {r_click_idx}
            self.last_clicked_idx = r_click_idx
            self.refresh_memo_list()

        menu = self.create_themed_menu(self.root)
        self.add_menu_header(menu, "메모 메뉴")
        menu.add_command(label="수정하기", command=self.edit_memo)
        menu.add_command(label="완료 표시", command=self.toggle_memo_strike)
        menu.add_command(label="중요 표시", command=self.toggle_memo_important)

        sticker_menu = self.build_sticker_menu(menu, self.add_sticker_to_memo)
        menu.add_cascade(label="스티커", menu=sticker_menu)

        color_menu = self.create_themed_menu(menu)
        self.add_menu_header(color_menu, "글자색")
        colors = [("기본색으로", ""), ("빨간색", "#e74c3c"), ("파란색", "#3498db"), ("초록색", "#27ae60"), ("보라색", "#9b59b6"), ("핑크색", "#ff66b2")]
        for name, code in colors:
            self.add_color_command(color_menu, name, code, lambda c=code: self.change_memo_color(c))
        menu.add_cascade(label="글자색", menu=color_menu)

        highlight_menu = self.create_themed_menu(menu)
        self.add_menu_header(highlight_menu, "하이라이트")
        h_colors = [("기본색으로", ""), ("노란색", "#f1c40f"), ("연녹색", "#a2d9ce"), ("연하늘", "#aed6f1"), ("연분홍", "#f5b7b1"), ("회색", "#d5d8dc"), ("핑크색", "#ff99cc")]
        for name, code in h_colors:
            self.add_color_command(highlight_menu, name, code, lambda c=code: self.change_memo_highlight(c))
        menu.add_cascade(label="하이라이트", menu=highlight_menu)

        menu.add_separator()
        menu.add_command(label="메모 삭제", command=self.delete_memo)
        try:
            menu.tk_popup(ev.x_root, ev.y_root)
        except Exception:
            try:
                menu.post(ev.x_root, ev.y_root)
            except Exception:
                pass
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return 'break'

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
            self.refresh_memo_list()
            self.save_memos()
            self.update_time_and_date()

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
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()

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
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()

    def change_memo_color(self, color):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
            
        for idx in list(self.selected_memo_indices):
            m = self.memos_data[u][idx]
            clean_text, _, bg = self.parse_text_styles(m['text'])
            new_t = self.build_styled_text(clean_text, color, bg)
            m['text'] = new_t
            if USE_SUPABASE and 'id' in m:
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"memo_text": new_t})
                
        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()

    def change_memo_highlight(self, bg_color):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
            
        for idx in list(self.selected_memo_indices):
            m = self.memos_data[u][idx]
            clean_text, fg, _ = self.parse_text_styles(m['text'])
            new_t = self.build_styled_text(clean_text, fg, bg_color)
            m['text'] = new_t
            if USE_SUPABASE and 'id' in m:
                self._async_db_task('PATCH', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}", HEADERS, {"memo_text": new_t})
                
        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()

    def edit_memo(self):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u or not self.selected_memo_indices: 
            return
        
        idx = list(self.selected_memo_indices)[0]
        if hasattr(self, 'last_clicked_idx') and getattr(self, 'last_clicked_idx', None) in self.selected_memo_indices:
            idx = self.last_clicked_idx
            
        if idx < len(self.memos_data[u]):
            m = self.memos_data[u][idx]
            clean_text, fg_color, bg_color = self.parse_text_styles(m['text'])
            new_t = simpledialog.askstring("입력/수정", "내용을 입력하세요 (수정 시 덮어씁니다):", parent=self.root, initialvalue=clean_text)
            if new_t is not None:
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

    def delete_memo(self):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if not u: 
            return
            
        if not self.selected_memo_indices: return
        
        if not messagebox.askyesno("삭제 확인", "선택한 메모를 삭제하시겠습니까?"):
            return
            
        indices = sorted(list(self.selected_memo_indices), reverse=True)
        for idx in indices:
            if idx < len(self.memos_data[u]):
                m = self.memos_data[u][idx]
                if USE_SUPABASE and 'id' in m: 
                    self._async_db_task('DELETE', f"{SUPABASE_URL}/rest/v1/memos?id=eq.{m['id']}")
                del self.memos_data[u][idx]
                
        self.selected_memo_indices.clear()
        self.push_history()
        self.refresh_memo_list()
        self.save_memos()
        self.update_time_and_date()

    def delete_all_memos(self):
        if not self.can_view_private_data(): 
            return
            
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        if u and messagebox.askyesno("삭제", "정말로 모든 메모를 완전히 삭제하시겠습니까?"):
            if USE_SUPABASE: 
                self._async_db_task('DELETE', f"{SUPABASE_URL}/rest/v1/memos?teacher_name=eq.{u}")
            self.memos_data[u] = []
            self.push_history()
            self.refresh_memo_list()
            self.save_memos()
            self.update_time_and_date()

    def export_memos(self):
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                for m in self.memos_data.get(u, []): 
                    clean_text, _, _ = self.parse_text_styles(m['text'])
                    f.write(f"{'[완료]' if m.get('strike') else ''}{clean_text}\n")

    def import_memos(self):
        u = getattr(self, 'teacher_var', tk.StringVar()).get()
        path = filedialog.askopenfilename()
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f: 
                        self.memos_data.setdefault(u, []).insert(0, {'text': line.strip(), 'strike': False, 'created_at': datetime.now().isoformat()})
            except:
                try:
                    with open(path, 'r', encoding='cp949') as f:
                        for line in f: 
                            self.memos_data.setdefault(u, []).insert(0, {'text': line.strip(), 'strike': False, 'created_at': datetime.now().isoformat()})
                except: pass
            self.push_history()
            self.refresh_memo_list()
            self.save_memos()
            self.update_time_and_date()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("교사 시간표")
    app = TimetableWidget(root)
    root.mainloop()
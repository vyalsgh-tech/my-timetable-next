# tools/step17_fix_shift_strike_toolbar.py
# ------------------------------------------------------------
# Step17 보완 패치
#
# 1) PC 다중 입력창 Shift+Enter 줄바꿈 재수정
#    - KeyPress-Return 단일 핸들러 사용
#    - Shift 상태이면 줄바꿈, 아니면 저장
#
# 2) 웹뷰어 __STRIKE__|| 표시 개선
#    - 단순 삭제가 아니라 취소선(<span class="mdgo-strike">)으로 표시
#
# 3) 웹뷰어 상단 버튼명 PC버전과 통일
#    - 달력 / 메모 / 조회 / 8·9
#    - 새로고침 버튼은 유지
#
# 실행:
#   python tools\step17_fix_shift_strike_toolbar.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_FILE = ROOT / "desktop" / "timetable.pyw"
MOBILE_FILE = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

NEW_ASK_MULTILINE = '''    def ask_multiline_string(self, title, prompt, initialvalue=""):
        """Enter=저장, Shift+Enter=줄바꿈을 지원하는 입력창."""
        result = {"value": None}

        win = tk.Toplevel(self.root)
        win.title(title)
        win.transient(self.root)
        win.grab_set()
        win.resizable(True, True)

        try:
            win.iconbitmap(self.icon_path)
        except Exception:
            pass

        t = self.get_active_theme()
        bg = t.get("panel_bg", t.get("cell_bg", "#ffffff"))
        fg = t.get("cell_fg", "#111827")
        input_bg = t.get("input_bg", "#ffffff")
        border = t.get("panel_border", t.get("grid", "#d0d7de"))
        accent = t.get("accent", "#2563eb")

        win.configure(bg=bg)

        frame = tk.Frame(win, bg=bg, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=prompt,
            bg=bg,
            fg=fg,
            font=("맑은 고딕", 9, "bold"),
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(0, 6))

        text_box = tk.Text(
            frame,
            height=6,
            width=42,
            wrap="word",
            bg=input_bg,
            fg=fg,
            insertbackground=fg,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=border,
            font=("맑은 고딕", 10),
            undo=True,
        )
        text_box.pack(fill="both", expand=True)
        text_box.insert("1.0", initialvalue or "")
        text_box.focus_set()

        tk.Label(
            frame,
            text="Enter: 저장  /  Shift+Enter: 줄바꿈  /  Esc: 취소",
            bg=bg,
            fg=t.get("muted_fg", "#667085"),
            font=("맑은 고딕", 8),
            anchor="w",
        ).pack(fill="x", pady=(6, 8))

        btn_frame = tk.Frame(frame, bg=bg)
        btn_frame.pack(fill="x")

        def on_ok(event=None):
            result["value"] = text_box.get("1.0", "end-1c").strip()
            win.destroy()
            return "break"

        def on_cancel(event=None):
            result["value"] = None
            win.destroy()
            return "break"

        def on_return_key(event=None):
            # Tk/Windows에서 Shift는 state bit 0x0001입니다.
            # Shift+Enter이면 저장하지 않고 줄바꿈만 삽입합니다.
            try:
                if event is not None and (int(event.state) & 0x0001):
                    text_box.insert("insert", chr(10))
                    return "break"
            except Exception:
                pass
            return on_ok(event)

        tk.Button(
            btn_frame,
            text="확인",
            command=on_ok,
            bg=accent,
            fg="white",
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2",
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            btn_frame,
            text="취소",
            command=on_cancel,
            bg=t.get("hover_btn", "#eef3fb"),
            fg=fg,
            relief="flat",
            padx=14,
            pady=4,
            cursor="hand2",
        ).pack(side="right")

        # 기존 <Return>/<Shift-Return> 충돌을 피하려고 KeyPress 단일 핸들러만 사용합니다.
        text_box.bind("<KeyPress-Return>", on_return_key)
        text_box.bind("<KeyPress-KP_Enter>", on_return_key)
        text_box.bind("<Escape>", on_cancel)
        win.bind("<Escape>", on_cancel)

        try:
            self.root.update_idletasks()
            x = self.root.winfo_rootx() + max(40, (self.root.winfo_width() - 420) // 2)
            y = self.root.winfo_rooty() + max(40, (self.root.winfo_height() - 260) // 2)
            win.geometry(f"460x280+{x}+{y}")
        except Exception:
            win.geometry("460x280")

        self.root.wait_window(win)
        return result["value"]

'''

MOBILE_HELPERS = r'''
import html


def split_strike_marker(value):
    """PC 저장값의 __STRIKE__|| 마커를 판별합니다."""
    text = "" if value is None else str(value)
    text = text.replace("\\n", "\n")
    text = text.replace("\r\n", "\n")

    is_strike = False
    m = re.match(r"^\s*_{1,3}STRIKE_{1,3}\s*\|+\s*(.*)$", text, flags=re.IGNORECASE | re.S)
    if m:
        is_strike = True
        text = m.group(1)
    else:
        text2 = re.sub(r"_{1,3}STRIKE_{1,3}\s*\|+", "", text, flags=re.IGNORECASE)
        if text2 != text:
            is_strike = True
            text = text2

    return is_strike, text.strip()


def clean_view_text(value):
    """텍스트 표시용 정리. HTML이 아닌 일반 텍스트용."""
    _, text = split_strike_marker(value)
    return text


def format_cell_html(value):
    """시간표/학사일정 셀 HTML 표시용. 완료 표시는 취소선으로 렌더링합니다."""
    is_strike, text = split_strike_marker(value)
    safe = html.escape(text).replace("\n", "<br>")
    if is_strike:
        return f'<span class="mdgo-strike">{safe}</span>'
    return safe


def sanitize_timetable_data(t_data):
    """raw 데이터는 보존하되 화면 표시 전 fallback용 문자열만 정리합니다."""
    try:
        for teacher, schedule in t_data.items():
            for day, values in schedule.items():
                schedule[day] = [v for v in values]
    except Exception:
        pass
    return t_data
'''

STRIKE_CSS = '''
    .mdgo-strike {
        text-decoration-line: line-through;
        text-decoration-thickness: 2px;
        text-decoration-color: #1f2937;
        opacity: 0.72;
    }
'''


def backup(path: Path):
    backup_path = path.with_name(f"{path.stem}_before_step17_{STAMP}{path.suffix}")
    backup_path.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {backup_path}")


def replace_method(text: str, method_name: str, replacement: str) -> tuple[str, bool]:
    start = text.find(f"    def {method_name}(")
    if start == -1:
        return text, False

    candidates = []
    for marker in ["\n    def ", "\n    # =========================================="]:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)
    if not candidates:
        raise RuntimeError(f"{method_name} 메서드 끝 위치를 찾지 못했습니다.")
    end = min(candidates)
    return text[:start] + replacement + text[end:], True


def patch_desktop():
    if not DESKTOP_FILE.exists():
        print(f"[경고] PC 파일 없음: {DESKTOP_FILE}")
        return False

    backup(DESKTOP_FILE)
    text = DESKTOP_FILE.read_text(encoding="utf-8", errors="replace")
    original = text

    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")

    text, replaced = replace_method(text, "ask_multiline_string", NEW_ASK_MULTILINE)
    if not replaced:
        marker = "    def add_memo(self, ev=None):"
        if marker in text:
            text = text.replace(marker, NEW_ASK_MULTILINE + marker, 1)
        else:
            raise RuntimeError("ask_multiline_string 삽입 위치를 찾지 못했습니다.")

    # simpledialog가 아직 남아 있는 입력/수정창은 다중 입력창으로 전환
    text = re.sub(
        r'simpledialog\.askstring\(\s*"입력/수정",\s*"내용을 입력하세요 \(수정 시 덮어씁니다\):",\s*parent=self\.root,\s*initialvalue=([^)]+?)\s*\)',
        r'self.ask_multiline_string("입력/수정", "내용을 입력하세요. Enter=저장, Shift+Enter=줄바꿈", initialvalue=\1)',
        text,
        flags=re.S,
    )

    if text != original:
        DESKTOP_FILE.write_text(text, encoding="utf-8")
        print("[완료] PC Shift+Enter 보완")
        return True

    print("[안내] PC 변경사항 없음")
    return False


def patch_mobile():
    if not MOBILE_FILE.exists():
        print(f"[경고] 모바일 파일 없음: {MOBILE_FILE}")
        return False

    backup(MOBILE_FILE)
    text = MOBILE_FILE.read_text(encoding="utf-8", errors="replace")
    original = text

    # helper 삽입
    if "def split_strike_marker(value):" not in text:
        # import html이 포함된 helper이므로 import 구문 아래가 아니라 함수 영역에 넣어도 작동합니다.
        marker = "\ndef safe_int(value, default=0):"
        if marker in text:
            text = text.replace(marker, MOBILE_HELPERS + marker, 1)
        else:
            marker2 = "\n# =========================================================\n# 6. URL 파라미터"
            text = text.replace(marker2, MOBILE_HELPERS + marker2, 1)

    # CSS 삽입
    if ".mdgo-strike" not in text:
        # 첫 번째 </style> 직전 삽입
        text = text.replace("</style>", STRIKE_CSS + "\n</style>", 1)

    # Supabase/custom schedule 값 표시 정리
    text = text.replace(
        'row["date_key"]: row["subject"] for row in r_cust.json()',
        'row["date_key"]: row.get("subject", "") for row in r_cust.json()'
    )

    # timetable 로딩 시 값은 raw 유지하되 None 방지
    text = text.replace('subject = (row.get("subject") or "").strip()', 'subject = str(row.get("subject") or "").strip()')
    text = text.replace('subject = clean_view_text(row.get("subject", ""))', 'subject = str(row.get("subject") or "").strip()')

    # 표 HTML에 직접 들어가는 일반적인 변수들을 format_cell_html로 감싸기
    # 이미 format된 곳은 중복 방지
    replacement_pairs = [
        ("{subject}", "{format_cell_html(subject)}"),
        ("{display_subject}", "{format_cell_html(display_subject)}"),
        ("{cell_text}", "{format_cell_html(cell_text)}"),
        ("{acad_text}", "{format_cell_html(acad_text)}"),
        ("{event}", "{format_cell_html(event)}"),
    ]
    for old, new in replacement_pairs:
        if new not in text:
            text = text.replace(old, new)

    # st.markdown이 unsafe_allow_html=True인 경우에만 취소선 HTML이 표시됩니다.
    text = re.sub(r"st\.markdown\(([^\n]*table_html[^\n]*)\)", r"st.markdown(\1, unsafe_allow_html=True)", text)

    # 화면에 직접 출력되는 값 정리: marker가 남으면 취소선 HTML로 표시
    text = text.replace("st.write(subject)", "st.markdown(format_cell_html(subject), unsafe_allow_html=True)")
    text = text.replace("st.markdown(subject)", "st.markdown(format_cell_html(subject), unsafe_allow_html=True)")

    # 버튼명 PC버전과 통일. 새로고침은 제외.
    replacements = {
        '"📅"': '"달력"', "'📅'": "'달력'",
        '"🗓️"': '"달력"', "'🗓️'": "'달력'",
        '"📝"': '"메모"', "'📝'": "'메모'",
        '"📄"': '"메모"', "'📄'": "'메모'",
        '"🔍"': '"조회"', "'🔍'": "'조회'",
        '"🔎"': '"조회"', "'🔎'": "'조회'",
        '"🔢"': '"8·9"', "'🔢'": "'8·9'",
        '"8-9"': '"8·9"', "'8-9'": "'8·9'",
        '"89"': '"8·9"', "'89'": "'8·9'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 달력 selectbox/버튼 폭이 좁아 글자가 세로로 갈라지는 문제 보완
    extra_css = '''
    div[data-testid="stHorizontalBlock"] button,
    div[data-testid="stHorizontalBlock"] [data-baseweb="select"] {
        min-width: 54px !important;
        white-space: nowrap !important;
    }
'''
    if "white-space: nowrap" not in text:
        text = text.replace("</style>", extra_css + "\n</style>", 1)

    text = text.replace("이번주", "오늘")

    if text != original:
        MOBILE_FILE.write_text(text, encoding="utf-8")
        print("[완료] 모바일 STRIKE 취소선/버튼명 보완")
        return True

    print("[안내] 모바일 변경사항 없음")
    return False


def main():
    print("==============================================")
    print("Step17 Shift+Enter / STRIKE 취소선 / 웹 버튼명 보완")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    try:
        changed_desktop = patch_desktop()
        changed_mobile = patch_mobile()
        print()
        print("[완료]")
        print("- PC 변경:", "있음" if changed_desktop else "없음")
        print("- 모바일 변경:", "있음" if changed_mobile else "없음")
        print()
        print("확인:")
        print("1) python desktop\\timetable.pyw")
        print("   - 입력/수정창에서 Shift+Enter 줄바꿈 확인")
        print("2) python -m streamlit run mobile\\app.py")
        print("   - __STRIKE__ 항목이 취소선으로 표시되는지 확인")
        print("   - 버튼명: 달력 / 메모 / 조회 / 8·9")
        print()
        input("엔터를 누르면 종료합니다.")
    except Exception as e:
        print()
        print("[오류]")
        print(e)
        print()
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()

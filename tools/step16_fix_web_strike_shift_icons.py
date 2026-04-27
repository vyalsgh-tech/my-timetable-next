# tools/step16_fix_web_strike_shift_icons.py
# ------------------------------------------------------------
# Step16 보완 패치
#
# 해결 내용:
# 1) 웹뷰어에서 __STRIKE__|| 문자가 시간표 칸에 그대로 보이는 문제 수정
# 2) PC 다중 입력창에서 Shift+Enter가 저장으로 처리되는 문제 수정
# 3) 웹뷰어 상단 버튼 문구를 PC버전과 맞춤
#    - 📅 -> 달력
#    - 📝 -> 메모
#    - 🔍/🔎 -> 조회
#    - 89/8-9/🔢 -> 8·9
#
# 실행:
#   python tools\step16_fix_web_strike_shift_icons.py
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
        # Enter=저장, Shift+Enter=줄바꿈을 지원하는 입력창
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

        guide = tk.Label(
            frame,
            text="Enter: 저장  /  Shift+Enter: 줄바꿈  /  Esc: 취소",
            bg=bg,
            fg=t.get("muted_fg", "#667085"),
            font=("맑은 고딕", 8),
            anchor="w",
        )
        guide.pack(fill="x", pady=(6, 8))

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

        def insert_newline(event=None):
            text_box.insert("insert", chr(10))
            return "break"

        def on_return(event=None):
            # Windows/Tk 기준 Shift 키는 state bit 0x0001.
            try:
                if event is not None and (event.state & 0x0001):
                    return insert_newline(event)
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

        # 중요: Shift+Enter를 먼저 바인딩하고, 일반 Enter는 state 검사 함수로 처리
        text_box.bind("<Shift-Return>", insert_newline)
        text_box.bind("<Shift-KP_Enter>", insert_newline)
        text_box.bind("<Return>", on_return)
        text_box.bind("<KP_Enter>", on_return)
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

def clean_view_text(value):
    # 화면 표시용 텍스트 정리: strike marker와 literal 줄바꿈을 정리합니다.
    text = "" if value is None else str(value)

    # PC버전 완료/취소선 저장 흔적 제거
    text = re.sub(r"_{1,3}STRIKE_{1,3}\s*\|\|?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"_{1,3}STRIKE_{1,3}", "", text, flags=re.IGNORECASE)

    # 과거 저장값 중 literal \n이 있으면 실제 줄바꿈으로 변환
    text = text.replace("\\n", "\n")
    text = text.replace("\r\n", "\n")

    return text.strip()


def sanitize_timetable_data(t_data):
    # 시간표 dict 전체의 표시 문자열을 정리합니다.
    try:
        for teacher, schedule in t_data.items():
            for day, values in schedule.items():
                schedule[day] = [clean_view_text(v) for v in values]
    except Exception:
        pass
    return t_data

'''


def backup(path: Path):
    backup_path = path.with_name(f"{path.stem}_before_step16_{STAMP}{path.suffix}")
    backup_path.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {backup_path}")


def patch_desktop():
    if not DESKTOP_FILE.exists():
        print(f"[경고] PC 파일 없음: {DESKTOP_FILE}")
        return False

    backup(DESKTOP_FILE)
    text = DESKTOP_FILE.read_text(encoding="utf-8", errors="replace")
    original = text

    # 창 제목 재확인
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)

    # 메뉴명 재확인
    text = text.replace('데이터 새로고침(Supabase)', '데이터 새로고침')
    text = text.replace('최신 설치파일 확인(GitHub Releases)', '최신 설치파일 확인')

    # ask_multiline_string 전체 교체
    if "    def ask_multiline_string(self" in text:
        start = text.find("    def ask_multiline_string(self")
        candidates = []
        for marker in [
            "\n    def create_memo_from_text(self",
            "\n    def add_memo(self",
            "\n    def refresh_memo_list(self",
        ]:
            pos = text.find(marker, start + 10)
            if pos != -1:
                candidates.append(pos)
        if not candidates:
            raise RuntimeError("ask_multiline_string 메서드 끝 위치를 찾지 못했습니다.")
        end = min(candidates)
        text = text[:start] + NEW_ASK_MULTILINE + text[end:]
    else:
        marker = "    def add_memo(self, ev=None):"
        if marker in text:
            text = text.replace(marker, NEW_ASK_MULTILINE + marker, 1)
        else:
            raise RuntimeError("ask_multiline_string 삽입 위치를 찾지 못했습니다.")

    # 아직 simpledialog를 쓰는 시간표/메모 편집부가 남아 있으면 교체
    text = re.sub(
        r'simpledialog\.askstring\(\s*"입력/수정",\s*"내용을 입력하세요 \(수정 시 덮어씁니다\):",\s*parent=self\.root,\s*initialvalue=([^)]+?)\s*\)',
        r'self.ask_multiline_string("입력/수정", "내용을 입력하세요. Enter=저장, Shift+Enter=줄바꿈", initialvalue=\1)',
        text,
        flags=re.S,
    )

    if text != original:
        DESKTOP_FILE.write_text(text, encoding="utf-8")
        print("[완료] PC Shift+Enter/메뉴명 보완")
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

    # 1. helper 삽입
    if "def clean_view_text(value):" not in text:
        marker = "\ndef safe_int(value, default=0):"
        if marker in text:
            text = text.replace(marker, MOBILE_HELPERS + marker, 1)
        else:
            marker2 = "\n# =========================================================\n# 6. URL 파라미터"
            text = text.replace(marker2, MOBILE_HELPERS + marker2, 1)

    # 2. custom schedule 표시 정리
    text = text.replace(
        'row["date_key"]: row["subject"] for row in r_cust.json()',
        'row["date_key"]: clean_view_text(row.get("subject", "")) for row in r_cust.json()'
    )

    # 3. timetable subject / academic event 로딩 정리
    text = text.replace(
        'subject = (row.get("subject") or "").strip()',
        'subject = clean_view_text(row.get("subject", ""))'
    )
    text = text.replace(
        'subject = str(row.get("subject") or "").strip()',
        'subject = clean_view_text(row.get("subject", ""))'
    )
    text = text.replace(
        'ev = str(row.get("event") or "").strip()',
        'ev = clean_view_text(row.get("event", ""))'
    )
    text = text.replace(
        'ev = (row.get("event") or "").strip()',
        'ev = clean_view_text(row.get("event", ""))'
    )

    # 4. load_csv 반환 직전 전체 sanitize. 이미 적용되어 있으면 중복 방지.
    if 'return sanitize_timetable_data(t_data)' not in text:
        text = re.sub(
            r'\n    return t_data\n',
            '\n    return sanitize_timetable_data(t_data)\n',
            text,
            count=1,
        )

    # 5. 혹시 화면 표시부에서 직접 subject를 출력하는 경우 대비
    text = text.replace('display_subject = subject', 'display_subject = clean_view_text(subject)')
    text = text.replace('cell_text = subject', 'cell_text = clean_view_text(subject)')

    # 6. 웹뷰어 버튼 문구 PC버전과 통일
    replacements = {
        '"📅"': '"달력"',
        "'📅'": "'달력'",
        '"🗓️"': '"달력"',
        "'🗓️'": "'달력'",
        '"📝"': '"메모"',
        "'📝'": "'메모'",
        '"📄"': '"메모"',
        "'📄'": "'메모'",
        '"🔍"': '"조회"',
        "'🔍'": "'조회'",
        '"🔎"': '"조회"',
        "'🔎'": "'조회'",
        '"🔢"': '"8·9"',
        "'🔢'": "'8·9'",
        '"8-9"': '"8·9"',
        "'8-9'": "'8·9'",
        '"89"': '"8·9"',
        "'89'": "'8·9'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 7. 명칭 통일 재확인
    text = text.replace("이번주", "오늘")

    if text != original:
        MOBILE_FILE.write_text(text, encoding="utf-8")
        print("[완료] 모바일 strike marker/버튼 문구 보완")
        return True

    print("[안내] 모바일 변경사항 없음")
    return False


def main():
    print("==============================================")
    print("Step16 웹 STRIKE / Shift+Enter / 버튼명 보완")
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
        print("   - 다중 입력창에서 Shift+Enter가 줄바꿈으로 작동")
        print()
        print("2) python -m streamlit run mobile\\app.py")
        print("   - __STRIKE__|| 문구가 사라짐")
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

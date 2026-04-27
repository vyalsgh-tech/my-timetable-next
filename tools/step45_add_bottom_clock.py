# tools/step45_add_bottom_clock.py
# ------------------------------------------------------------
# Step45: PC버전 하단 우측 현재시각 표시 추가
#
# 적용 내용:
# - 추천 위치인 하단 메모 입력줄 우측 끝에 현재시각 표시
# - 표시 형식: HH:MM, 예: 12:53
# - 1분 단위 자동 갱신
# - 시간표/메모 기능은 건드리지 않음
#
# 실행:
#   python tools\step45_add_bottom_clock.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

CLOCK_METHODS = '\n    def format_bottom_clock_text(self):\n        """하단 우측 현재시각 표시용 텍스트."""\n        try:\n            import datetime as _dt\n            return _dt.datetime.now().strftime("%H:%M")\n        except Exception:\n            return "--:--"\n\n    def update_bottom_clock(self):\n        """하단 메모 입력줄 우측의 현재시각을 1분 단위로 갱신."""\n        try:\n            if hasattr(self, "bottom_clock_label") and self.bottom_clock_label.winfo_exists():\n                try:\n                    t = self.get_active_theme()\n                except Exception:\n                    t = {}\n\n                bg = None\n                try:\n                    bg = self.memo_input_f.cget("bg")\n                except Exception:\n                    bg = t.get("panel_bg", "#ffffff")\n\n                fg = t.get("muted_fg", None) or t.get("memo_time_fg", None) or "#6B7280"\n\n                self.bottom_clock_label.configure(\n                    text=self.format_bottom_clock_text(),\n                    bg=bg,\n                    fg=fg,\n                )\n        except Exception:\n            pass\n\n        try:\n            import datetime as _dt\n            now = _dt.datetime.now()\n            delay = max(1000, (60 - now.second) * 1000 - int(now.microsecond / 1000) + 200)\n            self.root.after(delay, self.update_bottom_clock)\n        except Exception:\n            try:\n                self.root.after(30000, self.update_bottom_clock)\n            except Exception:\n                pass\n'
CLOCK_UI_BLOCK = '\n        self.bottom_clock_label = tk.Label(\n            self.memo_input_f,\n            text="--:--",\n            bd=0,\n            font=("맑은 고딕", 12),\n            fg="#6B7280",\n            anchor="e",\n            padx=4,\n            cursor="arrow",\n        )\n        self.bottom_clock_label.pack(side=\'right\', padx=(8, 2))\n        self.update_bottom_clock()\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step45_clock_{STAMP}{path.suffix}")
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
    # 이전 Step45 clock UI 블록이 있으면 제거
    while "self.bottom_clock_label = tk.Label(" in text:
        start = text.find("        self.bottom_clock_label = tk.Label(")
        if start == -1:
            break

        # update_bottom_clock 호출 줄까지 제거
        end_marker = "        self.update_bottom_clock()"
        end = text.find(end_marker, start)
        if end == -1:
            break
        end_line = text.find("\n", end)
        end_line = len(text) if end_line == -1 else end_line + 1
        text = text[:start] + text[end_line:]

    return text


def patch_clock_methods(text: str):
    changed = 0

    for name in ["format_bottom_clock_text", "update_bottom_clock"]:
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

    # 하단 메모 입력줄 버튼 중 A- 버튼 뒤에 현재시각 배치
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

    # fallback: memo_list_f 생성 직전에 넣기
    anchor = "        self.memo_list_f = tk.Frame(self.memo_frame"
    pos = text.find(anchor)
    if pos != -1:
        text = text[:pos] + CLOCK_UI_BLOCK + "\n" + text[pos:]
        changed += 1
        return text, changed

    raise RuntimeError("하단 메모 입력줄의 A- 버튼 또는 memo_list_f 위치를 찾지 못했습니다.")


def main():
    print("==============================================")
    print("Step45 add bottom current time")
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
        print("[완료] Step45 현재시각 표시 패치 저장")
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
    print("1. 하단 메모 입력줄 우측 끝에 현재시각이 표시되는지")
    print("2. 표시 형식이 12:53처럼 HH:MM인지")
    print("3. 메모 입력줄/검색/A+/A- 기능이 그대로 유지되는지")
    print("4. 시간표와 메모 수정 기능이 그대로 유지되는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

# tools/step34_smooth_desktop_startup.py
# ------------------------------------------------------------
# Step34: PC버전 시작 화면 깜빡임/물결 그려짐 완화
#
# 증상:
# - 창이 먼저 뜨고, 꺼졌다가 다시 붙잡히듯 켜짐
# - 아래쪽부터 물결치듯 선이 먼저 그려지고 나머지가 채워짐
#
# 처리:
# - root = tk.Tk() 직후 창을 잠시 숨김
# - TimetableWidget 구성이 끝난 뒤 mainloop 직전에 update_idletasks()
# - 그 다음 deiconify/lift로 한 번에 표시
#
# 실행:
#   python tools\step34_smooth_desktop_startup.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

START_MARK = "# >>> MDGO_STEP34_SMOOTH_STARTUP_HIDE"
END_MARK = "# <<< MDGO_STEP34_SMOOTH_STARTUP_HIDE"
SHOW_START_MARK = "# >>> MDGO_STEP34_SMOOTH_STARTUP_SHOW"
SHOW_END_MARK = "# <<< MDGO_STEP34_SMOOTH_STARTUP_SHOW"


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step34_smooth_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def remove_old_step34(text: str) -> str:
    def remove_between(s: str, start_marker: str, end_marker: str) -> str:
        while start_marker in s and end_marker in s:
            start = s.find(start_marker)
            line_start = s.rfind("\n", 0, start)
            line_start = 0 if line_start == -1 else line_start + 1
            end = s.find(end_marker, start)
            line_end = s.find("\n", end)
            if line_end == -1:
                line_end = len(s)
            else:
                line_end += 1
            s = s[:line_start] + s[line_end:]
        return s

    text = remove_between(text, START_MARK, END_MARK)
    text = remove_between(text, SHOW_START_MARK, SHOW_END_MARK)
    return text


def find_mainloop(text: str):
    matches = list(re.finditer(r"(?m)^(?P<indent>\s*)(?P<root>[A-Za-z_][A-Za-z0-9_]*)\.mainloop\s*\(\s*\)", text))
    if not matches:
        return None
    return matches[-1]


def find_tk_root_creation(text: str, root_var: str):
    pattern = rf"(?m)^(?P<indent>\s*){re.escape(root_var)}\s*=\s*tk\.Tk\s*\(\s*\)\s*$"
    matches = list(re.finditer(pattern, text))
    if matches:
        return matches[-1]

    pattern2 = r"(?m)^(?P<indent>\s*)(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*tk\.Tk\s*\(\s*\)\s*$"
    matches = list(re.finditer(pattern2, text))
    if matches:
        return matches[-1]

    return None


def patch_text(text: str):
    text = remove_old_step34(text)

    mainloop_match = find_mainloop(text)
    if not mainloop_match:
        raise RuntimeError("mainloop() 줄을 찾지 못했습니다.")

    root_var = mainloop_match.group("root")
    mainloop_indent = mainloop_match.group("indent")

    root_match = find_tk_root_creation(text, root_var)
    if not root_match:
        raise RuntimeError("root = tk.Tk() 줄을 찾지 못했습니다.")

    root_line = root_match.group(0)
    m_var = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*tk\.Tk", root_line)
    if m_var:
        root_var = m_var.group(1)

    root_indent = root_match.group("indent")

    hide_block = (
        f"{root_indent}{START_MARK}\n"
        f"{root_indent}try:\n"
        f"{root_indent}    {root_var}.withdraw()\n"
        f"{root_indent}except Exception:\n"
        f"{root_indent}    pass\n"
        f"{root_indent}{END_MARK}"
    )

    show_block = (
        f"{mainloop_indent}{SHOW_START_MARK}\n"
        f"{mainloop_indent}try:\n"
        f"{mainloop_indent}    {root_var}.update_idletasks()\n"
        f"{mainloop_indent}    {root_var}.deiconify()\n"
        f"{mainloop_indent}    {root_var}.lift()\n"
        f"{mainloop_indent}    {root_var}.focus_force()\n"
        f"{mainloop_indent}except Exception:\n"
        f"{mainloop_indent}    pass\n"
        f"{mainloop_indent}{SHOW_END_MARK}\n"
    )

    insert_after_root = root_match.end()
    text = text[:insert_after_root] + "\n" + hide_block + text[insert_after_root:]

    mainloop_match = find_mainloop(text)
    if not mainloop_match:
        raise RuntimeError("패치 후 mainloop() 줄을 다시 찾지 못했습니다.")

    insert_before_mainloop = mainloop_match.start()
    text = text[:insert_before_mainloop] + show_block + text[insert_before_mainloop:]

    return text, root_var


def main():
    print("==============================================")
    print("Step34 smooth desktop startup")
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
        patched, root_var = patch_text(text)
    except Exception as e:
        print("[오류] 자동 패치 실패")
        print(e)
        print()
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        compile(patched, str(DESKTOP), "exec")
        print("[확인] PC 파일 문법 OK")
    except Exception as e:
        print("[경고] PC 파일 문법 확인 실패")
        print(e)

    if patched != original:
        DESKTOP.write_text(patched, encoding="utf-8")
        print("[완료] 시작 화면 부드럽게 표시 패치 저장")
        print(f"- Tk root 변수: {root_var}")
    else:
        print("[안내] 변경 없음")

    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 창이 먼저 떴다가 꺼지는 느낌이 줄었는지")
    print("2. 아래부터 물결치듯 그려지는 장면이 보이지 않거나 약해졌는지")
    print("3. 앱이 정상적으로 한 번에 표시되는지")
    print()
    print("주의:")
    print("- 이 Step34는 기능을 바꾸지 않고 초기 표시 방식만 바꿉니다.")
    print("- 검색/A+/A- 및 줄바꿈 기능은 이후 별도 단계에서 처리하세요.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

# tools/step35_no_flicker_startup.py
# ------------------------------------------------------------
# Step35: PC버전 시작 시 "꺼졌다 다시 켜짐 / 물결치듯 그려짐" 현상 보정
#
# 화면녹화 확인 결과:
# - 앱 창이 처음 한 번 보임
# - 잠시 사라짐
# - 시간표 선/빈 영역이 먼저 보인 뒤 메모와 나머지 UI가 채워짐
#
# 원인:
# - Tk 창이 화면에 보이는 상태에서 초기 UI 렌더링/데이터 반영이 진행됨
# - Step34의 mainloop 직전 deiconify 방식은 일부 환경에서 중간 렌더링이 노출될 수 있음
#
# 처리:
# - root = tk.Tk() 직후 즉시 숨김 + 투명도 0
# - mainloop 직전에는 다시 보이지 않게 유지
# - mainloop가 시작된 뒤 1.8초 후 update_idletasks() 완료 후 한 번에 표시
# - 기존 Step34 패치 블록은 제거
#
# 실행:
#   python tools\step35_no_flicker_startup.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# 기존 패치 마커
OLD_MARKERS = [
    "MDGO_STEP34_SMOOTH_STARTUP_HIDE",
    "MDGO_STEP34_SMOOTH_STARTUP_SHOW",
    "Step34 smooth desktop startup",
]

# 새 패치 마커
HIDE_START = "# >>> MDGO_STEP35_START_HIDDEN"
HIDE_END = "# <<< MDGO_STEP35_START_HIDDEN"
SHOW_START = "# >>> MDGO_STEP35_DELAYED_SHOW"
SHOW_END = "# <<< MDGO_STEP35_DELAYED_SHOW"

# 표시 지연 시간. 녹화상 중간 렌더링이 약 0.7초 정도 노출되므로 1.8초로 넉넉히 잡음.
SHOW_DELAY_MS = 1800


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step35_no_flicker_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def remove_between_markers(text: str, start_marker: str, end_marker: str) -> str:
    while start_marker in text and end_marker in text:
        start = text.find(start_marker)
        line_start = text.rfind("\n", 0, start)
        line_start = 0 if line_start == -1 else line_start + 1

        end = text.find(end_marker, start)
        line_end = text.find("\n", end)
        line_end = len(text) if line_end == -1 else line_end + 1

        text = text[:line_start] + text[line_end:]

    return text


def remove_old_startup_patches(text: str) -> str:
    # Step34/Step35 기존 블록 제거
    text = remove_between_markers(text, "# >>> MDGO_STEP34_SMOOTH_STARTUP_HIDE", "# <<< MDGO_STEP34_SMOOTH_STARTUP_HIDE")
    text = remove_between_markers(text, "# >>> MDGO_STEP34_SMOOTH_STARTUP_SHOW", "# <<< MDGO_STEP34_SMOOTH_STARTUP_SHOW")
    text = remove_between_markers(text, HIDE_START, HIDE_END)
    text = remove_between_markers(text, SHOW_START, SHOW_END)

    # 혹시 마커가 깨져 남은 직접 호출 줄 제거
    lines = []
    skip_next = 0
    for line in text.splitlines():
        if skip_next > 0:
            skip_next -= 1
            continue

        stripped = line.strip()
        if any(marker in line for marker in OLD_MARKERS):
            continue
        if stripped.endswith(".deiconify()") and "MDGO_STEP34" in "\n".join(lines[-8:]):
            continue
        lines.append(line)

    return "\n".join(lines) + "\n"


def find_mainloop(text: str):
    matches = list(
        re.finditer(
            r"(?m)^(?P<indent>\s*)(?P<root>[A-Za-z_][A-Za-z0-9_]*)\.mainloop\s*\(\s*\)",
            text,
        )
    )
    return matches[-1] if matches else None


def find_tk_root_creation(text: str, root_var: str):
    # root = tk.Tk() 형태 탐색
    pattern = rf"(?m)^(?P<indent>\s*){re.escape(root_var)}\s*=\s*tk\.Tk\s*\(\s*\)\s*$"
    matches = list(re.finditer(pattern, text))
    if matches:
        return matches[-1]

    # 혹시 변수명이 다른 경우 전체 탐색
    pattern2 = r"(?m)^(?P<indent>\s*)(?P<var>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*tk\.Tk\s*\(\s*\)\s*$"
    matches = list(re.finditer(pattern2, text))
    if matches:
        return matches[-1]

    return None


def patch_text(text: str):
    text = remove_old_startup_patches(text)

    mainloop_match = find_mainloop(text)
    if not mainloop_match:
        raise RuntimeError("mainloop() 줄을 찾지 못했습니다.")

    root_var = mainloop_match.group("root")
    mainloop_indent = mainloop_match.group("indent")

    root_match = find_tk_root_creation(text, root_var)
    if not root_match:
        raise RuntimeError("root = tk.Tk() 줄을 찾지 못했습니다.")

    # 실제 root 변수명 확인
    root_line = root_match.group(0)
    m_var = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*tk\.Tk", root_line)
    if m_var:
        root_var = m_var.group(1)

    root_indent = root_match.group("indent")

    hide_block = (
        f"{root_indent}{HIDE_START}\n"
        f"{root_indent}try:\n"
        f"{root_indent}    {root_var}.withdraw()\n"
        f"{root_indent}    {root_var}.attributes('-alpha', 0.0)\n"
        f"{root_indent}except Exception:\n"
        f"{root_indent}    pass\n"
        f"{root_indent}{HIDE_END}"
    )

    show_block = (
        f"{mainloop_indent}{SHOW_START}\n"
        f"{mainloop_indent}def _mdgo_step35_show_ready_window():\n"
        f"{mainloop_indent}    try:\n"
        f"{mainloop_indent}        {root_var}.update_idletasks()\n"
        f"{mainloop_indent}        {root_var}.attributes('-alpha', 1.0)\n"
        f"{mainloop_indent}        {root_var}.deiconify()\n"
        f"{mainloop_indent}        {root_var}.lift()\n"
        f"{mainloop_indent}        {root_var}.focus_force()\n"
        f"{mainloop_indent}    except Exception:\n"
        f"{mainloop_indent}        pass\n"
        f"{mainloop_indent}try:\n"
        f"{mainloop_indent}    {root_var}.withdraw()\n"
        f"{mainloop_indent}    {root_var}.attributes('-alpha', 0.0)\n"
        f"{mainloop_indent}    {root_var}.after({SHOW_DELAY_MS}, _mdgo_step35_show_ready_window)\n"
        f"{mainloop_indent}except Exception:\n"
        f"{mainloop_indent}    pass\n"
        f"{mainloop_indent}{SHOW_END}\n"
    )

    # root 생성 직후 즉시 숨김
    insert_after_root = root_match.end()
    text = text[:insert_after_root] + "\n" + hide_block + text[insert_after_root:]

    # hide 삽입 후 mainloop 재탐색
    mainloop_match = find_mainloop(text)
    if not mainloop_match:
        raise RuntimeError("패치 후 mainloop() 줄을 다시 찾지 못했습니다.")

    insert_before_mainloop = mainloop_match.start()
    text = text[:insert_before_mainloop] + show_block + text[insert_before_mainloop:]

    return text, root_var


def main():
    print("==============================================")
    print("Step35 no-flicker desktop startup")
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
        print("[완료] 시작 중간 렌더링 숨김 패치 저장")
        print(f"- Tk root 변수: {root_var}")
        print(f"- 표시 지연: {SHOW_DELAY_MS}ms")
    else:
        print("[안내] 변경 없음")

    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 처음 앱 창이 떴다가 꺼지는 장면이 사라졌는지")
    print("2. 선부터 그려지고 나중에 채워지는 장면이 사라졌는지")
    print("3. 약 1~2초 뒤 완성된 창이 한 번에 뜨는지")
    print()
    print("이 패치는 기능을 바꾸지 않고 시작 표시 방식만 바꿉니다.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

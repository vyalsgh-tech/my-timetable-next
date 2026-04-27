# tools/step33_clean_desktop_startup.py
# ------------------------------------------------------------
# Step33: PC버전 시작/종료 어색함 제거용 "깔끔한 시작" 복구
#
# 증상:
# - 자동 종료는 막았지만, 창이 꺼졌다가 다시 붙잡히는 듯 어색하게 켜짐
#
# 원인 가능성:
# - Step29/Step31 계열 런타임 패치, after 콜백, overlay 패치 흔적이
#   desktop/timetable.pyw 또는 선택된 백업에 남아 있음.
#
# 처리:
# 1) 현재 desktop/timetable.pyw 백업
# 2) desktop 폴더의 과거 백업 중
#    - 컴파일 가능
#    - Step29/Step31/Step32 런타임 패치 흔적 없음
#    - _mdgo 계열 after/overlay 흔적 없음
#    - mainloop 정상 포함
#    - 메모/시간표 기능 흔적 포함
#    인 파일을 골라 복구
# 3) 창 제목/메뉴명 등 안전한 수정만 적용
#
# 실행:
#   python tools\step33_clean_desktop_startup.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_DIR = ROOT / "desktop"
DESKTOP = DESKTOP_DIR / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


BAD_TOKENS = [
    # 최근 문제를 만든 런타임/overlay 패치
    "Step29 PC 하단 메모/시간표 줄바꿈 런타임 보정",
    "Step31 하단 메모 버튼 안전 복구 패치",
    "_mdgo_apply_pc_runtime_patch",
    "_mdgo_step31_restore_memo_buttons_safe",
    "_MdgoInlineMemoText",
    "_mdgo_memo_bar_fixed",
    "_mdgo_step31_memo_buttons_installed",
    "_mdgo_global_shift_enter_installed",
    "_mdgo_shift_enter_bound",
    "_mdgo_shift_bound",
    "patch_global_shift_enter_for_entries",
    "bind_entry_shift_enter_recursive",
    "entry_shift_enter_to_multiline",
    "InlineMemoText",
    "MDGOTextReturnFix",
    "MDGOMultilineInput",
    "overlay.place",
    "_mdgo_memo_button_overlay",
    # Step32는 복구 스크립트 자체지만 혹시 파일 안에 들어가 있으면 제외
    "Step32 PC auto-close recovery",
]

REQUIRED_TOKENS = [
    "memo_entry",
    "memo_text",
    "refresh_memo_list",
    "add_memo",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def backup_current():
    if not DESKTOP.exists():
        return None
    backup = DESKTOP.with_name(f"timetable_before_step33_clean_startup_{STAMP}.pyw")
    write_text(backup, read_text(DESKTOP))
    print(f"[현재 파일 백업] {backup}")
    return backup


def compile_ok(text: str, label: str) -> tuple[bool, str]:
    try:
        compile(text, label, "exec")
        return True, ""
    except Exception as e:
        return False, str(e)


def apply_safe_changes(text: str) -> str:
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")
    return text


def is_clean_candidate(text: str) -> tuple[bool, str]:
    ok, err = compile_ok(text, "<candidate>")
    if not ok:
        return False, f"문법 오류: {err}"

    for bad in BAD_TOKENS:
        if bad in text:
            return False, f"문제 패치 흔적 포함: {bad}"

    # _mdgo로 시작하는 패치 흔적은 일괄 제외
    if "_mdgo" in text:
        return False, "_mdgo 런타임 패치 흔적 포함"

    # mainloop는 있어야 실제 앱 실행 파일로 판단
    if "mainloop(" not in text and ".mainloop()" not in text:
        return False, "mainloop 없음"

    for token in REQUIRED_TOKENS:
        if token not in text:
            return False, f"필수 기능 흔적 없음: {token}"

    return True, "OK"


def score_candidate(path: Path, text: str) -> float:
    score = 0.0

    # 메모 입력칸 보조 버튼이 원래 살아 있던 파일이면 우선
    for token in ["검색", "A+", "A-"]:
        if token in text:
            score += 30

    # 기본 앱 구성 흔적
    for token in ["save_memos", "load_memos", "refresh_memo_list", "draw", "teacher_var"]:
        if token in text:
            score += 5

    # Supabase 연동 안정 버전 우대
    for token in ["SUPABASE_URL", "USE_SUPABASE", "memos"]:
        if token in text:
            score += 3

    # 너무 최근 Step31/32 직전 백업보다 Step25 이전 안정본 선호
    name = path.name
    step_score = 0
    m = re.search(r"step(\d+)", name)
    if m:
        step = int(m.group(1))
        # Step17~26 사이가 상대적으로 안정 후보
        if 17 <= step <= 26:
            step_score += 20
        # Step27~32는 최근 문제가 누적됐을 가능성
        if step >= 27:
            step_score -= 25
        step_score += min(step, 26) * 0.2

    score += step_score

    # 최신 수정시간은 약간만 반영
    try:
        score += (path.stat().st_mtime % 1000) / 1000
    except Exception:
        pass

    return score


def candidate_files():
    patterns = [
        "timetable_before_step26*.pyw",
        "timetable_before_step25*.pyw",
        "timetable_before_step24*.pyw",
        "timetable_before_step23*.pyw",
        "timetable_before_step22*.pyw",
        "timetable_before_step21*.pyw",
        "timetable_before_step20*.pyw",
        "timetable_before_step19*.pyw",
        "timetable_before_step18*.pyw",
        "timetable_before_step17*.pyw",
        "timetable_before_step27*.pyw",
        "timetable_before_step28*.pyw",
        "timetable_before_step29*.pyw",
        "timetable_before_step30*.pyw",
        "timetable_before_step31*.pyw",
        "timetable_before_step32*.pyw",
        "timetable_before_*.pyw",
        "legacy_timetable.pyw",
    ]

    seen = set()
    files = []

    for pattern in patterns:
        for path in sorted(DESKTOP_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
            if path.exists() and path not in seen and path.name != DESKTOP.name:
                seen.add(path)
                files.append(path)

    return files


def find_best_clean_backup():
    good = []
    skipped = []

    for path in candidate_files():
        try:
            raw = read_text(path)
            text = apply_safe_changes(raw)
            clean, reason = is_clean_candidate(text)

            if clean:
                score = score_candidate(path, text)
                good.append((score, path, text))
            else:
                skipped.append((path.name, reason))
        except Exception as e:
            skipped.append((path.name, str(e)))

    good.sort(key=lambda item: item[0], reverse=True)

    print("[정상 후보]")
    if good:
        for score, path, _ in good[:8]:
            print(f"- {path.name} / score={score:.2f}")
    else:
        print("- 없음")

    print()
    print("[제외 후보 일부]")
    for name, reason in skipped[:8]:
        print(f"- {name}: {reason}")

    if not good:
        return None, None, None

    return good[0]


def strip_bad_blocks_from_current(text: str) -> str:
    # 최후 fallback. 문제 마커가 들어간 블록만 제거.
    for marker in BAD_TOKENS:
        while marker in text:
            idx = text.find(marker)
            start = text.rfind("# =========================================================", 0, idx)
            if start == -1:
                start = text.rfind("\ndef ", 0, idx)
            if start == -1:
                start = max(0, text.rfind("\n", 0, idx))

            end = text.find("# =========================================================", idx + len(marker))
            if end == -1:
                text = text[:start].rstrip() + "\n"
                break
            text = text[:start] + text[end:]

    return text


def main():
    print("==============================================")
    print("Step33 clean desktop startup")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not DESKTOP.exists():
        print(f"[오류] PC 파일이 없습니다: {DESKTOP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    result = find_best_clean_backup()

    if result[0] is not None:
        score, selected, text = result
        print()
        print(f"[선택] {selected.name} / score={score:.2f}")
    else:
        print()
        print("[경고] 완전히 깨끗한 백업을 찾지 못했습니다.")
        print("현재 파일에서 문제 패치 블록만 제거합니다.")
        text = read_text(DESKTOP)
        text = strip_bad_blocks_from_current(text)
        text = apply_safe_changes(text)

    ok, err = compile_ok(text, str(DESKTOP))

    if not ok:
        print()
        print("[오류] 복구 대상 파일도 문법 확인에 실패했습니다.")
        print(err)
        print("저장하지 않았습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    write_text(DESKTOP, text)

    print()
    print("[완료] PC버전을 런타임 패치 없는 깨끗한 시작 상태로 복구했습니다.")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 창이 한 번에 자연스럽게 켜지는지")
    print("2. 꺼졌다 다시 붙잡히는 느낌이 사라졌는지")
    print("3. 기존 시간표/메모 표시가 정상인지")
    print()
    print("이제 검색/A+/A-와 줄바꿈은 한꺼번에 런타임으로 붙이지 말고, 실제 UI 생성 함수 위치를 확인한 뒤 한 기능씩 적용해야 합니다.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

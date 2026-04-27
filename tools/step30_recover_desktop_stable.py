# tools/step30_recover_desktop_stable.py
# ------------------------------------------------------------
# Step30: PC버전 자동 종료 문제 복구
#
# Step29 런타임 패치가 앱 실행 직전에 UI를 강제로 재구성하면서
# 일부 환경에서 창이 바로 닫히는 문제가 생길 수 있습니다.
#
# 이 스크립트는:
# 1) 현재 desktop/timetable.pyw를 백업
# 2) Step29 런타임 패치 블록 제거
# 3) 가능하면 검색/A+/A- 버튼이 살아 있는 정상 백업으로 복구
# 4) 창 제목/메뉴명 등 안전한 수정만 유지
#
# 실행:
#   python tools\step30_recover_desktop_stable.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP_DIR = ROOT / "desktop"
DESKTOP = DESKTOP_DIR / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

BAD_MARKERS = [
    "Step29 PC 하단 메모/시간표 줄바꿈 런타임 보정",
    "_mdgo_apply_pc_runtime_patch",
    "_MdgoInlineMemoText",
    "Step29 runtime repair",
]


def backup_current():
    if DESKTOP.exists():
        b = DESKTOP.with_name(f"timetable_before_step30_recover_{STAMP}.pyw")
        b.write_text(DESKTOP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        print(f"[현재 파일 백업] {b}")
        return b
    return None


def can_compile(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        compile(text, str(path), "exec")
        return True
    except Exception:
        return False


def score_candidate(path: Path) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return -999

    # 깨진 런타임 패치가 들어간 백업은 제외
    if any(marker in text for marker in BAD_MARKERS):
        return -999

    try:
        compile(text, str(path), "exec")
    except Exception:
        return -999

    score = 0

    # 메모 입력칸의 기존 기능이 살아 있는 파일 우선
    for token in ["검색", "A+", "A-", "memo_entry", "memo_text"]:
        if token in text:
            score += 10

    # 안정적으로 실행되는 원본 계열 우선
    if "root.mainloop" in text or ".mainloop()" in text:
        score += 5

    # 너무 오래된 legacy보다 최근 백업 우선
    name = path.name
    for step in range(29, 0, -1):
        if f"step{step}" in name:
            score += step
            break

    return score


def find_best_backup():
    patterns = [
        "timetable_before_step28*.pyw",
        "timetable_before_step27*.pyw",
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
        "timetable_before_*.pyw",
        "legacy_timetable.pyw",
    ]

    candidates = []
    seen = set()

    for pattern in patterns:
        for path in DESKTOP_DIR.glob(pattern):
            if path.exists() and path not in seen:
                seen.add(path)
                candidates.append(path)

    scored = []
    for path in candidates:
        score = score_candidate(path)
        if score > 0:
            scored.append((score, path))

    scored.sort(key=lambda x: (x[0], x[1].stat().st_mtime), reverse=True)

    if not scored:
        return None

    print("[백업 후보]")
    for score, path in scored[:5]:
        print(f"- {path.name} / score={score}")

    return scored[0][1]


def remove_bad_runtime_patch(text: str) -> str:
    # Step29 런타임 블록 제거
    markers = [
        "Step29 PC 하단 메모/시간표 줄바꿈 런타임 보정",
        "_mdgo_apply_pc_runtime_patch",
    ]

    for marker in markers:
        while marker in text:
            idx = text.find(marker)
            start = text.rfind("# =========================================================", 0, idx)
            if start == -1:
                start = text.rfind("def _mdgo_apply_pc_runtime_patch", 0, idx)
            if start == -1:
                start = max(0, text.rfind("\n", 0, idx))

            end = text.find("# =========================================================", idx + len(marker))
            if end == -1:
                # 파일 끝에 붙은 경우
                text = text[:start].rstrip() + "\n"
                break

            text = text[:start] + text[end:]

    return text


def apply_safe_titles(text: str) -> str:
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")
    return text


def main():
    print("==============================================")
    print("Step30 PC stable recovery")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not DESKTOP.exists():
        print(f"[오류] PC 파일이 없습니다: {DESKTOP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    selected = find_best_backup()

    if selected:
        print()
        print(f"[복구] 정상 백업 선택: {selected.name}")
        text = selected.read_text(encoding="utf-8", errors="replace")
    else:
        print()
        print("[안내] 적절한 백업을 찾지 못해 현재 파일에서 문제 블록만 제거합니다.")
        text = DESKTOP.read_text(encoding="utf-8", errors="replace")

    text = remove_bad_runtime_patch(text)
    text = apply_safe_titles(text)

    try:
        compile(text, str(DESKTOP), "exec")
        compile_ok = True
    except Exception as e:
        compile_ok = False
        print(f"[경고] 저장 전 문법 확인 실패: {e}")

    DESKTOP.write_text(text, encoding="utf-8")

    print()
    if compile_ok:
        print("[완료] PC버전 자동 종료 원인 패치를 제거하고 안정 파일로 복구했습니다.")
    else:
        print("[완료] 파일은 저장했지만 문법 확인 경고가 있습니다.")

    print()
    print("다음 확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인 후:")
    print("- 창이 자동으로 닫히지 않는지")
    print("- 하단 메모 입력칸 오른쪽 검색/A+/A- 버튼이 보이는지")
    print()
    print("줄바꿈 기능은 앱 안정 복구 확인 후, 별도 Step31에서 셀 편집 함수만 직접 패치하겠습니다.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

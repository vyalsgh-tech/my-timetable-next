# tools/step32_recover_pc_auto_close.py
# ------------------------------------------------------------
# Step32: PC버전 자동 종료 긴급 복구
#
# 증상:
# - python desktop\timetable.pyw 실행 시 창이 잠깐 떴다가 자동으로 꺼짐
#
# 원인 가능성:
# - Step31/Step29 런타임 UI 패치가 mainloop 직전/후에 삽입되면서
#   Tkinter 이벤트 루프 또는 위젯 구조를 건드려 종료를 유발
#
# 처리:
# 1) 현재 desktop/timetable.pyw 백업
# 2) 가장 안전한 1순위 백업: timetable_before_step31*.pyw 로 복구
# 3) 없으면 Step31/Step29 런타임 패치 블록을 현재 파일에서 제거
# 4) 창 제목/메뉴명 등 안전한 수정만 유지
#
# 실행:
#   python tools\step32_recover_pc_auto_close.py
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
    "Step31 하단 메모 버튼 안전 복구 패치",
    "_mdgo_step31_restore_memo_buttons_safe",
    "Step29 PC 하단 메모/시간표 줄바꿈 런타임 보정",
    "_mdgo_apply_pc_runtime_patch",
    "_MdgoInlineMemoText",
    "Step29 runtime repair",
    "Step28 web + PC final repair",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")


def backup_current():
    if not DESKTOP.exists():
        return None

    backup = DESKTOP.with_name(f"timetable_before_step32_recover_{STAMP}.pyw")
    write_text(backup, read_text(DESKTOP))
    print(f"[현재 파일 백업] {backup}")
    return backup


def compile_ok_text(text: str, label: str) -> tuple[bool, str]:
    try:
        compile(text, label, "exec")
        return True, ""
    except Exception as e:
        return False, str(e)


def has_bad_patch(text: str) -> bool:
    return any(marker in text for marker in BAD_MARKERS)


def apply_safe_titles(text: str) -> str:
    text = re.sub(r'root\.title\("[^"]*"\)', 'root.title("명덕외고 시간표")', text)
    text = re.sub(r'self\.root\.title\("[^"]*"\)', 'self.root.title("명덕외고 시간표")', text)
    text = text.replace("데이터 새로고침(Supabase)", "데이터 새로고침")
    text = text.replace("최신 설치파일 확인(GitHub Releases)", "최신 설치파일 확인")
    return text


def remove_block_by_marker(text: str, marker: str) -> str:
    while marker in text:
        idx = text.find(marker)

        # 보통 패치 블록은 구분선부터 시작함
        start = text.rfind("# =========================================================", 0, idx)

        # def부터 시작하는 경우
        if start == -1:
            for key in [
                "def _mdgo_step31_restore_memo_buttons_safe",
                "def _mdgo_apply_pc_runtime_patch",
            ]:
                pos = text.rfind(key, 0, idx)
                if pos != -1:
                    start = pos
                    break

        if start == -1:
            start = max(0, text.rfind("\n", 0, idx))

        # 다음 구분선까지 삭제. 다음 구분선이 없으면 파일 끝까지 삭제.
        end = text.find("# =========================================================", idx + len(marker))

        if end == -1:
            text = text[:start].rstrip() + "\n"
            break

        text = text[:start] + text[end:]

    return text


def remove_bad_runtime_patches(text: str) -> str:
    for marker in BAD_MARKERS:
        text = remove_block_by_marker(text, marker)

    # 혹시 블록 끝에 남은 직접 호출 줄 제거
    leftover_patterns = [
        r"^\s*_mdgo_step31_restore_memo_buttons_safe\(\)\s*$",
        r"^\s*_mdgo_apply_pc_runtime_patch\(\)\s*$",
        r"^\s*try:\s*\n\s*_mdgo_step31_restore_memo_buttons_safe\(\)\s*\n\s*except Exception:\s*\n\s*pass\s*$",
        r"^\s*try:\s*\n\s*_mdgo_apply_pc_runtime_patch\(\)\s*\n\s*except Exception:\s*\n\s*pass\s*$",
    ]

    for pattern in leftover_patterns:
        text = re.sub(pattern, "", text, flags=re.M)

    return text


def find_best_step31_backup():
    # Step31 실행 직전 백업이 가장 안전하다.
    candidates = sorted(
        DESKTOP_DIR.glob("timetable_before_step31*.pyw"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for path in candidates:
        try:
            text = read_text(path)
            text = remove_bad_runtime_patches(text)
            text = apply_safe_titles(text)
            ok, err = compile_ok_text(text, str(path))
            if ok and not has_bad_patch(text):
                return path, text
        except Exception:
            continue

    return None, None


def find_other_safe_backup():
    patterns = [
        "timetable_before_step30_recover*.pyw",
        "timetable_before_step30*.pyw",
        "timetable_before_step29*.pyw",
        "timetable_before_step28*.pyw",
        "timetable_before_step27*.pyw",
        "timetable_before_step26*.pyw",
        "timetable_before_step25*.pyw",
        "timetable_before_step24*.pyw",
        "timetable_before_step23*.pyw",
        "timetable_before_step22*.pyw",
        "timetable_before_step21*.pyw",
        "timetable_before_step20*.pyw",
        "timetable_before_*.pyw",
    ]

    seen = set()
    candidates = []

    for pattern in patterns:
        for path in DESKTOP_DIR.glob(pattern):
            if path not in seen and path.name != DESKTOP.name:
                seen.add(path)
                candidates.append(path)

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    scored = []
    for path in candidates:
        try:
            text = read_text(path)
            text = remove_bad_runtime_patches(text)
            text = apply_safe_titles(text)
            ok, _ = compile_ok_text(text, str(path))
            if not ok or has_bad_patch(text):
                continue

            score = 0
            for token in ["검색", "A+", "A-", "memo_entry", "memo_text", "mainloop"]:
                if token in text:
                    score += 10

            # 최신순 가산
            score += int(path.stat().st_mtime) % 1000 / 1000
            scored.append((score, path, text))
        except Exception:
            continue

    if not scored:
        return None, None

    scored.sort(key=lambda x: x[0], reverse=True)

    print("[백업 후보 상위]")
    for score, path, _ in scored[:5]:
        print(f"- {path.name} / score={score:.3f}")

    return scored[0][1], scored[0][2]


def main():
    print("==============================================")
    print("Step32 PC auto-close recovery")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not DESKTOP.exists():
        print(f"[오류] PC 파일이 없습니다: {DESKTOP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()

    selected_path, selected_text = find_best_step31_backup()

    if selected_path:
        print(f"[복구] Step31 직전 백업 사용: {selected_path.name}")
        text = selected_text
    else:
        print("[안내] Step31 직전 안정 백업을 찾지 못했습니다. 다른 안전 백업을 찾습니다.")
        selected_path, selected_text = find_other_safe_backup()

        if selected_path:
            print(f"[복구] 안전 백업 사용: {selected_path.name}")
            text = selected_text
        else:
            print("[안내] 안전 백업을 찾지 못해 현재 파일에서 문제 블록만 제거합니다.")
            text = read_text(DESKTOP)
            text = remove_bad_runtime_patches(text)
            text = apply_safe_titles(text)

    ok, err = compile_ok_text(text, str(DESKTOP))
    if not ok:
        print("[경고] 복구 파일 문법 확인 실패")
        print(err)
    else:
        print("[확인] 복구 파일 문법 OK")

    write_text(DESKTOP, text)

    print()
    print("[완료] PC 자동 종료 원인 패치를 제거/복구했습니다.")
    print()
    print("다음 확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("1. 창이 자동으로 꺼지지 않는지")
    print("2. 기존 시간표와 메모장이 정상 표시되는지")
    print("3. 하단 메모 입력칸이 최소한 기존처럼 입력 가능한지")
    print()
    print("주의:")
    print("- 이번 Step32는 안정 복구 전용입니다.")
    print("- 검색/A+/A- 및 줄바꿈은 자동 종료가 해결된 뒤, 파일 내부의 실제 함수 위치를 확인해서 다시 별도 적용해야 합니다.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

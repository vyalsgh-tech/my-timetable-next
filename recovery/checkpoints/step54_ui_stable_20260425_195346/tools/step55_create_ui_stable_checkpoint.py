# tools/step55_create_ui_stable_checkpoint.py
# ------------------------------------------------------------
# Step55: 현재 UI 안정 버전 복구용 체크포인트 생성
#
# 목적:
# - Step47~Step54까지의 UI/메모/달력 개선이 반영된 현재 상태를 복구용으로 보관
# - 나중에 수정이 꼬이면 restore_checkpoint.bat 실행 한 번으로 현재 상태로 되돌릴 수 있게 함
#
# 생성 위치:
#   recovery/checkpoints/step54_ui_stable_YYYYMMDD_HHMMSS/
#
# 실행:
#   python tools\step55_create_ui_stable_checkpoint.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CHECKPOINT_NAME = f"step54_ui_stable_{STAMP}"
CHECKPOINT_DIR = ROOT / "recovery" / "checkpoints" / CHECKPOINT_NAME

FILES_TO_KEEP = [
    "desktop/timetable.pyw",
    "mobile/app.py",
    "data/version.json",
    "build/timetable.spec",
    "build/installer.iss",
    ".gitignore",
    "README.md",
    "tools/step47_toolbar_lovely_pink_icons.py",
    "tools/step48_restore_save_sticker_menu_color_reset.py",
    "tools/step49_memo_click_context_menu_fix.py",
    "tools/step50_restore_memo_click_features_context_lock.py",
    "tools/step51_memo_scroll_context_spacing_fix.py",
    "tools/step52_memo_context_scroll_highlight_fix.py",
    "tools/step53_memo_highlight_menu_drag_smooth_fix.py",
    "tools/step54_smooth_calendar_month_switch.py",
    "tools/step55_create_ui_stable_checkpoint.py",
]

RESTORE_PY = """# restore_checkpoint.py
# 이 파일은 체크포인트에 저장된 파일들을 프로젝트 루트로 되돌립니다.
#
# 실행:
#   python restore_checkpoint.py

from pathlib import Path
from datetime import datetime
import shutil

CHECKPOINT_DIR = Path(__file__).resolve().parent
ROOT = CHECKPOINT_DIR.parents[2]

FILES = [
    "desktop/timetable.pyw",
    "mobile/app.py",
    "data/version.json",
    "build/timetable.spec",
    "build/installer.iss",
    ".gitignore",
    "README.md",
    "tools/step47_toolbar_lovely_pink_icons.py",
    "tools/step48_restore_save_sticker_menu_color_reset.py",
    "tools/step49_memo_click_context_menu_fix.py",
    "tools/step50_restore_memo_click_features_context_lock.py",
    "tools/step51_memo_scroll_context_spacing_fix.py",
    "tools/step52_memo_context_scroll_highlight_fix.py",
    "tools/step53_memo_highlight_menu_drag_smooth_fix.py",
    "tools/step54_smooth_calendar_month_switch.py",
    "tools/step55_create_ui_stable_checkpoint.py",
]

def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_dir = ROOT / "recovery" / "before_restore" / f"before_restore_{stamp}"
    safety_dir.mkdir(parents=True, exist_ok=True)

    print("==============================================")
    print("Restore UI stable checkpoint")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print(f"[CHECKPOINT] {CHECKPOINT_DIR}")
    print(f"[SAFETY BACKUP] {safety_dir}")
    print()

    restored = 0

    for rel in FILES:
        src = CHECKPOINT_DIR / rel
        dst = ROOT / rel

        if not src.exists():
            print(f"[건너뜀] 체크포인트에 없음: {rel}")
            continue

        if dst.exists():
            backup_dst = safety_dir / rel
            backup_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup_dst)

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        restored += 1
        print(f"[복구] {rel}")

    print()
    print(f"[완료] 복구 파일 수: {restored}")
    print()
    print("확인:")
    print("python desktop\\\\timetable.pyw")
    input("엔터를 누르면 종료합니다.")

if __name__ == "__main__":
    main()
"""

RESTORE_BAT = """@echo off
chcp 65001 >nul
cd /d "%~dp0"
python restore_checkpoint.py
pause
"""


def copy_file(rel: str):
    src = ROOT / rel
    dst = CHECKPOINT_DIR / rel

    if not src.exists():
        print(f"[건너뜀] 없음: {rel}")
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"[보관] {rel}")
    return True


def run_git_info():
    info = []
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info.append(f"git_head={result.stdout.strip()}")
        else:
            info.append("git_head=unknown")
    except Exception:
        info.append("git_head=git_not_available")

    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info.append("")
            info.append("[git status --short]")
            info.append(result.stdout.strip() or "clean")
    except Exception:
        pass

    return "\n".join(info)


def main():
    print("==============================================")
    print("Step55 create UI stable checkpoint")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print(f"[CHECKPOINT] {CHECKPOINT_DIR}")
    print()

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    kept = 0
    for rel in FILES_TO_KEEP:
        if copy_file(rel):
            kept += 1

    (CHECKPOINT_DIR / "restore_checkpoint.py").write_text(RESTORE_PY, encoding="utf-8")
    (CHECKPOINT_DIR / "restore_checkpoint.bat").write_text(RESTORE_BAT, encoding="utf-8")

    info = []
    info.append("명덕외고 시간표앱 UI 안정 버전 복구용 체크포인트")
    info.append("=" * 60)
    info.append(f"checkpoint_name={CHECKPOINT_NAME}")
    info.append(f"created_at={datetime.now().isoformat(timespec='seconds')}")
    info.append(f"root={ROOT}")
    info.append("")
    info.append("[상태]")
    info.append("- Step47~Step54 UI/메모/달력 개선 후 안정 확인용 체크포인트")
    info.append("- 다음 버전업/릴리즈 전 복구용 안전 지점")
    info.append("")
    info.append("[복구 방법]")
    info.append("1. 이 폴더의 restore_checkpoint.bat 실행")
    info.append("또는")
    info.append("2. python restore_checkpoint.py 실행")
    info.append("")
    info.append("[포함 파일]")
    for rel in FILES_TO_KEEP:
        exists = (CHECKPOINT_DIR / rel).exists()
        info.append(f"- {'OK' if exists else 'MISS'} {rel}")
    info.append("")
    info.append(run_git_info())

    (CHECKPOINT_DIR / "CHECKPOINT_INFO.txt").write_text("\n".join(info), encoding="utf-8")

    print()
    print("[완료] UI 안정 버전 복구용 체크포인트 생성")
    print(f"- 위치: {CHECKPOINT_DIR}")
    print(f"- 보관 파일 수: {kept}")
    print()
    print("[복구가 필요할 때]")
    print(f"1. {CHECKPOINT_DIR}\\restore_checkpoint.bat 실행")
    print("또는")
    print(f"2. python {CHECKPOINT_DIR}\\restore_checkpoint.py")
    print()
    print("[다음 권장 작업]")
    print("Git에도 현재 UI 안정 버전을 남기려면 아래 명령을 이어서 실행하세요.")
    print()
    print("git status --short")
    print("git add desktop/timetable.pyw tools/step47_toolbar_lovely_pink_icons.py tools/step48_restore_save_sticker_menu_color_reset.py tools/step49_memo_click_context_menu_fix.py tools/step50_restore_memo_click_features_context_lock.py tools/step51_memo_scroll_context_spacing_fix.py tools/step52_memo_context_scroll_highlight_fix.py tools/step53_memo_highlight_menu_drag_smooth_fix.py tools/step54_smooth_calendar_month_switch.py tools/step55_create_ui_stable_checkpoint.py")
    print('git commit -m "Checkpoint stable UI memo and calendar updates"')
    print("git tag stable-step54-ui")
    print("git push")
    print("git push origin stable-step54-ui")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

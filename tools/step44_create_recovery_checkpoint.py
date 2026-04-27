# tools/step44_create_recovery_checkpoint.py
# ------------------------------------------------------------
# Step44: 현재 정상 버전 복구용 체크포인트 생성
#
# 목적:
# - 현재 "완벽하게 정상 확인된 상태"를 로컬 복구용으로 보관
# - 나중에 수정이 꼬이면 실행 한 번으로 현재 상태로 되돌릴 수 있게 함
#
# 생성 위치:
#   recovery/checkpoints/step43_perfect_YYYYMMDD_HHMMSS/
#
# 실행:
#   python tools\step44_create_recovery_checkpoint.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import shutil
import sys
import subprocess

ROOT = Path(__file__).resolve().parent.parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
CHECKPOINT_NAME = f"step43_perfect_{STAMP}"
CHECKPOINT_DIR = ROOT / "recovery" / "checkpoints" / CHECKPOINT_NAME

FILES_TO_KEEP = [
    "desktop/timetable.pyw",
    "mobile/app.py",
    "data/version.json",
    "build/timetable.spec",
    "build/installer.iss",
    ".gitignore",
    "README.md",
    "tools/step43_memo_selection_indent_edit_delete_fix_v2.py",
]

RESTORE_PY = """# restore_checkpoint.py
# 이 파일은 체크포인트에 저장된 파일들을 프로젝트 루트로 되돌립니다.
# 실행:
#   python restore_checkpoint.py

from pathlib import Path
from datetime import datetime
import shutil
import sys

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
    "tools/step43_memo_selection_indent_edit_delete_fix_v2.py",
]

def main():
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_dir = ROOT / "recovery" / "before_restore" / f"before_restore_{stamp}"
    safety_dir.mkdir(parents=True, exist_ok=True)

    print("==============================================")
    print("Restore checkpoint")
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
    print("Step44 create recovery checkpoint")
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
    info.append("명덕외고 시간표앱 복구용 체크포인트")
    info.append("=" * 50)
    info.append(f"checkpoint_name={CHECKPOINT_NAME}")
    info.append(f"created_at={datetime.now().isoformat(timespec='seconds')}")
    info.append(f"root={ROOT}")
    info.append("")
    info.append("[상태]")
    info.append("- Step43 v2 적용 후 사용자가 '완벽해'라고 확인한 버전")
    info.append("- 다음 수정 단계 전 복구용 안전 지점")
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
    print("[완료] 복구용 체크포인트 생성")
    print(f"- 위치: {CHECKPOINT_DIR}")
    print(f"- 보관 파일 수: {kept}")
    print()
    print("[복구가 필요할 때]")
    print(f"1. {CHECKPOINT_DIR}\\restore_checkpoint.bat 실행")
    print("또는")
    print(f"2. python {CHECKPOINT_DIR}\\restore_checkpoint.py")
    print()
    print("[다음 권장 작업]")
    print("Git에도 현재 정상 버전을 남기려면 아래 명령을 이어서 실행하세요.")
    print()
    print("git status --short")
    print("git add desktop/timetable.pyw tools/step43_memo_selection_indent_edit_delete_fix_v2.py")
    print('git commit -m "Checkpoint stable desktop memo UI"')
    print("git tag stable-step43-perfect")
    print("git push")
    print("git push origin stable-step43-perfect")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

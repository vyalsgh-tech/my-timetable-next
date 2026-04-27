# restore_checkpoint.py
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
    print("python desktop\\timetable.pyw")
    input("엔터를 누르면 종료합니다.")

if __name__ == "__main__":
    main()

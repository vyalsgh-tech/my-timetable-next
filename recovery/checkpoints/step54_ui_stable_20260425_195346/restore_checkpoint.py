# restore_checkpoint.py
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
    print("python desktop\\timetable.pyw")
    input("엔터를 누르면 종료합니다.")

if __name__ == "__main__":
    main()

# tools/fix_program_info_display_v2.py
# ------------------------------------------------------------
# 프로그램 정보 창에 \\n이 문자 그대로 보이는 문제를 수정합니다.
#
# 실행:
#   python tools\\fix_program_info_display_v2.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_program_info_display_fix_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"


REPLACEMENT = '''    def get_app_version_info(self):
        default_info = {
            "app_version": "2.0.1",
            "data_version": "-",
            "updated_at": "-",
            "release_date": "-",
            "minimum_app_version": "-",
        }

        candidate_paths = []
        try:
            candidate_paths.append(os.path.join(self.data_dir, "version.json"))
        except Exception:
            pass
        try:
            candidate_paths.append(os.path.join(self.project_root, "data", "version.json"))
        except Exception:
            pass
        try:
            candidate_paths.append(os.path.join(os.getcwd(), "data", "version.json"))
        except Exception:
            pass
        try:
            if getattr(sys, "frozen", False):
                candidate_paths.append(os.path.join(os.path.dirname(sys.executable), "data", "version.json"))
        except Exception:
            pass

        seen = set()
        for path in candidate_paths:
            if not path or path in seen:
                continue
            seen.add(path)

            try:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8-sig") as f:
                        data = json.load(f)

                    app_version = (
                        data.get("app_version")
                        or data.get("minimum_app_version")
                        or data.get("min_app_version")
                        or default_info["app_version"]
                    )

                    return {
                        "app_version": str(app_version),
                        "data_version": str(data.get("data_version", default_info["data_version"])),
                        "updated_at": str(data.get("updated_at", data.get("release_date", default_info["updated_at"]))),
                        "release_date": str(data.get("release_date", default_info["release_date"])),
                        "minimum_app_version": str(data.get("minimum_app_version", app_version)),
                    }
            except Exception:
                pass

        return default_info

    def show_program_info(self):
        version_info = self.get_app_version_info()

        app_version = version_info.get("app_version", "2.0.1")
        data_version = version_info.get("data_version", "-")
        updated_at = version_info.get("updated_at", "-")
        release_date = version_info.get("release_date", "-")
        minimum_app_version = version_info.get("minimum_app_version", app_version)

        lines = [
            f"🏫 명덕외고 교사 시간표 v{app_version}",
            "",
            f"앱 버전 : {app_version}",
            f"데이터 버전 : {data_version}",
            f"업데이트 날짜 : {updated_at}",
            f"최소 지원 앱 버전 : {minimum_app_version}",
            f"릴리즈 날짜 : {release_date}",
            "",
            "개발 및 저작권자 : 표선생",
            "이메일 : vyalsgh@gmail.com",
            "",
            "Copyright ⓒ 2026 표선생. All rights reserved.",
            "본 프로그램의 무단 배포 및 상업적 이용을 금합니다.",
        ]

        info_text = "\\n".join(lines)
        messagebox.showinfo("프로그램 정보", info_text)
'''


def ensure_import(text: str, module_name: str) -> str:
    if f"import {module_name}" in text:
        return text

    lines = text.splitlines()
    insert_at = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = i + 1

    lines.insert(insert_at, f"import {module_name}")
    return "\n".join(lines) + "\n"


def replace_program_info_block(text: str) -> str:
    start = text.find("    def get_app_version_info(self):")
    if start == -1:
        start = text.find("    def show_program_info(self):")

    if start == -1:
        raise RuntimeError("get_app_version_info 또는 show_program_info 메서드를 찾지 못했습니다.")

    candidates = []
    for marker in ["\n    def ", "\n    # =========================================="]:
        pos = text.find(marker, start + 10)
        if pos != -1:
            candidates.append(pos)

    if not candidates:
        raise RuntimeError("프로그램 정보 메서드 블록의 끝을 찾지 못했습니다.")

    end = min(candidates)
    return text[:start] + REPLACEMENT + "\n" + text[end:]


def main():
    print("==============================================")
    print("프로그램 정보 표시 줄바꿈 복구 v2")
    print("==============================================")
    print()

    if not TARGET.exists():
        print(f"[오류] 대상 파일이 없습니다: {TARGET}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    original = TARGET.read_text(encoding="utf-8", errors="replace")
    BACKUP.write_text(original, encoding="utf-8")
    print(f"[백업 완료] {BACKUP}")

    patched = ensure_import(original, "json")
    patched = replace_program_info_block(patched)

    TARGET.write_text(patched, encoding="utf-8")

    print("[완료] 프로그램 정보 창의 줄바꿈 표시를 정상 형태로 수정했습니다.")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print("설정 > 프로그램 정보")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

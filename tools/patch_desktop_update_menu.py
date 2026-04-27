# tools/patch_desktop_update_menu.py
# ------------------------------------------------------------
# 목적:
#   PC 앱 설정 메뉴의 업데이트 항목을 정리합니다.
#
# 실행:
#   python tools\patch_desktop_update_menu.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_update_menu_patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"


def add_import_webbrowser(text: str) -> str:
    if "import webbrowser" in text:
        return text

    lines = text.splitlines()
    insert_at = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            insert_at = i + 1
        elif insert_at is not None and stripped == "":
            break

    if insert_at is None:
        return "import webbrowser\n" + text

    lines.insert(insert_at, "import webbrowser")
    return "\n".join(lines) + "\n"


def add_release_constant(text: str) -> str:
    if "GITHUB_RELEASES_URL" in text:
        return text

    constant_block = (
        '\n# GitHub Release 페이지\n'
        'GITHUB_RELEASES_URL = "https://github.com/vyalsgh-tech/my-timetable-next/releases/latest"\n'
    )

    marker = "# ==========================================\n"
    first_marker = text.find(marker)
    if first_marker != -1:
        second_marker = text.find(marker, first_marker + len(marker))
        if second_marker != -1:
            return text[:second_marker + len(marker)] + constant_block + text[second_marker + len(marker):]

    return text.replace("import webbrowser\n", "import webbrowser\n" + constant_block + "\n", 1)


def add_methods(text: str) -> str:
    if "def open_github_releases_page" in text:
        return text

    methods = '''
    def open_github_releases_page(self):
        # 설정 메뉴용: GitHub Releases 최신 설치파일 페이지 열기
        try:
            webbrowser.open(GITHUB_RELEASES_URL)
        except Exception as e:
            messagebox.showerror("릴리즈 페이지 오류", f"GitHub Releases 페이지를 열 수 없습니다.\\n{e}")

    def show_update_guide(self):
        # 설정 메뉴용: 업데이트 방식 안내
        try:
            msg = (
                "업데이트 방식 안내\\n\\n"
                "1. 데이터 새로고침(Supabase)\\n"
                "   - 시간표/학사일정이 바뀌었을 때 현재 앱에서 즉시 다시 불러옵니다.\\n"
                "   - 앱 재설치가 필요 없습니다.\\n\\n"
                "2. 최신 설치파일 확인(GitHub Releases)\\n"
                "   - 앱 자체가 업데이트되었을 때 새 설치파일을 받을 수 있는 페이지를 엽니다.\\n\\n"
                "일반적인 신학기 시간표 변경은 1번만 사용하면 됩니다."
            )
            messagebox.showinfo("업데이트 안내", msg)
        except Exception:
            pass

'''

    marker = "    def refresh_supabase_base_data(self):"
    if marker in text:
        return text.replace(marker, methods + marker, 1)

    marker2 = "    # ==========================================\n    # 💡 3. 로그인"
    if marker2 in text:
        return text.replace(marker2, methods + "\n" + marker2, 1)

    raise RuntimeError("메서드를 삽입할 위치를 찾지 못했습니다.")


def patch_settings_menu(text: str) -> str:
    text = text.replace(
        'label="업데이트 확인 / 데이터 새로고침"',
        'label="데이터 새로고침(Supabase)"'
    )

    if "최신 설치파일 확인(GitHub Releases)" in text:
        return text

    lines = text.splitlines()
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)

        if "command=self.refresh_supabase_base_data" in line and not inserted:
            indent = re.match(r"^(\s*)", line).group(1)
            new_lines.append(
                f'{indent}self.settings_menu.add_command(label="최신 설치파일 확인(GitHub Releases)", command=self.open_github_releases_page)'
            )
            new_lines.append(
                f'{indent}self.settings_menu.add_command(label="업데이트 안내", command=self.show_update_guide)'
            )
            inserted = True

    if not inserted:
        raise RuntimeError("설정 메뉴에서 refresh_supabase_base_data 항목을 찾지 못했습니다.")

    return "\n".join(new_lines) + "\n"


def main():
    print("==============================================")
    print("PC 앱 설정 메뉴 업데이트 패치")
    print("==============================================")
    print()

    if not TARGET.exists():
        print(f"[오류] 대상 파일이 없습니다: {TARGET}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    BACKUP.write_text(text, encoding="utf-8")
    print(f"[백업 완료] {BACKUP}")

    text = add_import_webbrowser(text)
    text = add_release_constant(text)
    text = add_methods(text)
    text = patch_settings_menu(text)

    TARGET.write_text(text, encoding="utf-8")

    print("[완료] desktop/timetable.pyw 설정 메뉴가 수정되었습니다.")
    print()
    print("다음 확인:")
    print("1. python desktop\\timetable.pyw 실행")
    print("2. 설정 메뉴에서 아래 항목 확인")
    print("   - 데이터 새로고침(Supabase)")
    print("   - 최신 설치파일 확인(GitHub Releases)")
    print("   - 업데이트 안내")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

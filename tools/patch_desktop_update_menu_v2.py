# tools/patch_desktop_update_menu_v2.py
# ------------------------------------------------------------
# PC 앱 설정 메뉴 업데이트 항목 보강 패치 v2
#
# 현재 보이는 메뉴:
#   - 데이터 새로고침(Supabase)
#   - 데이터 경로/교사 목록 확인
#
# 추가할 메뉴:
#   - 최신 설치파일 확인(GitHub Releases)
#   - 업데이트 안내
#
# 실행:
#   python tools\patch_desktop_update_menu_v2.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_update_menu_patch_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"

RELEASES_URL = "https://github.com/vyalsgh-tech/my-timetable-next/releases/latest"


def ensure_import(text: str) -> str:
    if "import webbrowser" in text:
        return text

    lines = text.splitlines()
    insert_at = 0

    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            insert_at = i + 1

    lines.insert(insert_at, "import webbrowser")
    return "\n".join(lines) + "\n"


def ensure_constant(text: str) -> str:
    if "GITHUB_RELEASES_URL" in text:
        return text

    block = '\nGITHUB_RELEASES_URL = "https://github.com/vyalsgh-tech/my-timetable-next/releases/latest"\n'

    # SUPABASE 설정 블록 뒤쪽 또는 첫 클래스 정의 전 삽입
    class_idx = text.find("class ")
    if class_idx != -1:
        return text[:class_idx] + block + "\n" + text[class_idx:]

    return block + "\n" + text


def ensure_methods(text: str) -> str:
    need_release_method = "def open_github_releases_page" not in text
    need_guide_method = "def show_update_guide" not in text

    if not need_release_method and not need_guide_method:
        return text

    methods = ""

    if need_release_method:
        methods += '''
    def open_github_releases_page(self):
        try:
            webbrowser.open(GITHUB_RELEASES_URL)
        except Exception as e:
            messagebox.showerror("릴리즈 페이지 오류", f"GitHub Releases 페이지를 열 수 없습니다.\\n{e}")

'''

    if need_guide_method:
        methods += '''
    def show_update_guide(self):
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

    # refresh_supabase_base_data 앞에 삽입
    marker = "    def refresh_supabase_base_data(self):"
    if marker in text:
        return text.replace(marker, methods + marker, 1)

    # show_data_source_info 앞에라도 삽입
    marker = "    def show_data_source_info(self):"
    if marker in text:
        return text.replace(marker, methods + marker, 1)

    raise RuntimeError("메서드 삽입 위치를 찾지 못했습니다.")


def ensure_menu_items(text: str) -> str:
    # 기존 이름 정리
    text = text.replace(
        'label="업데이트 확인 / 데이터 새로고침"',
        'label="데이터 새로고침(Supabase)"'
    )

    if "최신 설치파일 확인(GitHub Releases)" in text and "업데이트 안내" in text:
        return text

    lines = text.splitlines()
    out = []
    inserted = False

    for line in lines:
        out.append(line)

        # 가장 확실한 위치: 데이터 새로고침 메뉴 바로 아래
        if (
            not inserted
            and 'label="데이터 새로고침(Supabase)"' in line
            and "command=self.refresh_supabase_base_data" in line
        ):
            indent = line[: len(line) - len(line.lstrip())]
            if "최신 설치파일 확인(GitHub Releases)" not in text:
                out.append(f'{indent}self.settings_menu.add_command(label="최신 설치파일 확인(GitHub Releases)", command=self.open_github_releases_page)')
            if "업데이트 안내" not in text:
                out.append(f'{indent}self.settings_menu.add_command(label="업데이트 안내", command=self.show_update_guide)')
            inserted = True

    if inserted:
        return "\n".join(out) + "\n"

    # fallback: 데이터 경로/교사 목록 확인 메뉴 바로 아래
    lines = text.splitlines()
    out = []
    inserted = False

    for line in lines:
        out.append(line)

        if (
            not inserted
            and 'label="데이터 경로/교사 목록 확인"' in line
        ):
            indent = line[: len(line) - len(line.lstrip())]
            if "최신 설치파일 확인(GitHub Releases)" not in text:
                out.append(f'{indent}self.settings_menu.add_command(label="최신 설치파일 확인(GitHub Releases)", command=self.open_github_releases_page)')
            if "업데이트 안내" not in text:
                out.append(f'{indent}self.settings_menu.add_command(label="업데이트 안내", command=self.show_update_guide)')
            inserted = True

    if inserted:
        return "\n".join(out) + "\n"

    raise RuntimeError("설정 메뉴 항목 삽입 위치를 찾지 못했습니다.")


def main():
    print("==============================================")
    print("PC 앱 설정 메뉴 업데이트 패치 v2")
    print("==============================================")
    print()

    if not TARGET.exists():
        print(f"[오류] 대상 파일이 없습니다: {TARGET}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8", errors="replace")
    BACKUP.write_text(text, encoding="utf-8")
    print(f"[백업 완료] {BACKUP}")

    text = ensure_import(text)
    text = ensure_constant(text)
    text = ensure_methods(text)
    text = ensure_menu_items(text)

    TARGET.write_text(text, encoding="utf-8")
    print("[완료] 설정 메뉴에 GitHub Releases/업데이트 안내 항목을 추가했습니다.")
    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("설정 메뉴에서 아래 4개가 보이면 정상입니다.")
    print("- 데이터 새로고침(Supabase)")
    print("- 데이터 경로/교사 목록 확인")
    print("- 최신 설치파일 확인(GitHub Releases)")
    print("- 업데이트 안내")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

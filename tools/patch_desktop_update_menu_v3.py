# tools/patch_desktop_update_menu_v3.py
# ------------------------------------------------------------
# PC 앱 설정 메뉴 업데이트 항목 강제 삽입 패치 v3
# 실행: python tools\patch_desktop_update_menu_v3.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_update_menu_patch_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"
RELEASE_URL = "https://github.com/vyalsgh-tech/my-timetable-next/releases/latest"


def ensure_import(text):
    if "import webbrowser" in text:
        return text
    src = text.splitlines()
    pos = 0
    for i, line in enumerate(src):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            pos = i + 1
    src.insert(pos, "import webbrowser")
    return "\n".join(src) + "\n"


def ensure_constant(text):
    if "GITHUB_RELEASES_URL" in text:
        return text
    insert = '\nGITHUB_RELEASES_URL = "https://github.com/vyalsgh-tech/my-timetable-next/releases/latest"\n\n'
    idx = text.find("class ")
    if idx >= 0:
        return text[:idx] + insert + text[idx:]
    return insert + text


def ensure_methods(text):
    method_chunks = []
    if "def open_github_releases_page" not in text:
        method_chunks.extend([
            "    def open_github_releases_page(self):",
            "        try:",
            "            webbrowser.open(GITHUB_RELEASES_URL)",
            "        except Exception as e:",
            "            messagebox.showerror(\"릴리즈 페이지 오류\", f\"GitHub Releases 페이지를 열 수 없습니다.\\\\n{e}\")",
            "",
        ])
    if "def show_update_guide" not in text:
        method_chunks.extend([
            "    def show_update_guide(self):",
            "        try:",
            "            msg = (",
            "                \"업데이트 방식 안내\\\\n\\\\n\"",
            "                \"1. 데이터 새로고침(Supabase)\\\\n\"",
            "                \"   - 시간표/학사일정이 바뀌었을 때 현재 앱에서 즉시 다시 불러옵니다.\\\\n\"",
            "                \"   - 앱 재설치가 필요 없습니다.\\\\n\\\\n\"",
            "                \"2. 최신 설치파일 확인(GitHub Releases)\\\\n\"",
            "                \"   - 앱 자체가 업데이트되었을 때 새 설치파일을 받을 수 있는 페이지를 엽니다.\\\\n\\\\n\"",
            "                \"일반적인 신학기 시간표 변경은 1번만 사용하면 됩니다.\"",
            "            )",
            "            messagebox.showinfo(\"업데이트 안내\", msg)",
            "        except Exception:",
            "            pass",
            "",
        ])
    if not method_chunks:
        return text
    add = "\n".join(method_chunks) + "\n"
    for marker in [
        "    def refresh_supabase_base_data(self):",
        "    def show_data_source_info(self):",
        "    def import_memos(self):",
    ]:
        if marker in text:
            return text.replace(marker, add + marker, 1)
    raise RuntimeError("메서드 삽입 위치를 찾지 못했습니다.")


def ensure_menu(text):
    text = text.replace('label="업데이트 확인 / 데이터 새로고침"', 'label="데이터 새로고침(Supabase)"')
    has_release_menu = 'label="최신 설치파일 확인(GitHub Releases)"' in text
    has_guide_menu = 'label="업데이트 안내"' in text
    if has_release_menu and has_guide_menu:
        return text
    for anchor in [
        'label="데이터 경로/교사 목록 확인"',
        'label="데이터 새로고침(Supabase)"',
    ]:
        src = text.splitlines()
        out = []
        inserted = False
        for line in src:
            out.append(line)
            if (not inserted) and anchor in line:
                indent = line[: len(line) - len(line.lstrip())]
                if not has_release_menu:
                    out.append(f'{indent}self.settings_menu.add_command(label="최신 설치파일 확인(GitHub Releases)", command=self.open_github_releases_page)')
                if not has_guide_menu:
                    out.append(f'{indent}self.settings_menu.add_command(label="업데이트 안내", command=self.show_update_guide)')
                inserted = True
        if inserted:
            return "\n".join(out) + "\n"
    raise RuntimeError("설정 메뉴 삽입 위치를 찾지 못했습니다.")


def main():
    print("==============================================")
    print("PC 앱 설정 메뉴 업데이트 패치 v3")
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
    text = ensure_menu(text)
    TARGET.write_text(text, encoding="utf-8")
    print("[완료] 메뉴 항목을 강제로 추가했습니다.")
    print()
    print("확인 명령: python desktop\\timetable.pyw")
    print("설정 메뉴에서 아래 항목이 보여야 합니다.")
    print("- 데이터 새로고침(Supabase)")
    print("- 데이터 경로/교사 목록 확인")
    print("- 최신 설치파일 확인(GitHub Releases)")
    print("- 업데이트 안내")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

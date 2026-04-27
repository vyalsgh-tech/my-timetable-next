# tools/patch_desktop_program_info.py
# ------------------------------------------------------------
# PC 앱의 '프로그램 정보' 창에 하드코딩된 v1.0 대신
# data/version.json의 실제 앱/데이터 버전을 표시하도록 패치합니다.
# 실행: python tools\patch_desktop_program_info.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_program_info_patch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"


def ensure_json_import(text):
    if "import json" in text:
        return text
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, "import json")
    return "\n".join(lines) + "\n"


def make_new_block():
    lines = [
        "    def get_app_version_info(self):",
        "        # data/version.json을 읽어 프로그램 정보 표시용 버전 정보를 반환합니다.",
        "        default_info = {",
        "            \"app_version\": \"2.0.1\",",
        "            \"data_version\": \"-\",",
        "            \"updated_at\": \"-\",",
        "            \"release_date\": \"-\",",
        "            \"minimum_app_version\": \"-\",",
        "        }",
        "",
        "        candidate_paths = []",
        "",
        "        try:",
        "            candidate_paths.append(os.path.join(self.data_dir, \"version.json\"))",
        "        except Exception:",
        "            pass",
        "",
        "        try:",
        "            candidate_paths.append(os.path.join(self.project_root, \"data\", \"version.json\"))",
        "        except Exception:",
        "            pass",
        "",
        "        try:",
        "            candidate_paths.append(os.path.join(os.getcwd(), \"data\", \"version.json\"))",
        "        except Exception:",
        "            pass",
        "",
        "        try:",
        "            if getattr(sys, \"frozen\", False):",
        "                candidate_paths.append(os.path.join(os.path.dirname(sys.executable), \"data\", \"version.json\"))",
        "        except Exception:",
        "            pass",
        "",
        "        seen = set()",
        "        for path in candidate_paths:",
        "            if not path or path in seen:",
        "                continue",
        "            seen.add(path)",
        "            try:",
        "                if os.path.exists(path):",
        "                    with open(path, \"r\", encoding=\"utf-8-sig\") as f:",
        "                        data = json.load(f)",
        "                    app_version = (",
        "                        data.get(\"app_version\")",
        "                        or data.get(\"minimum_app_version\")",
        "                        or data.get(\"min_app_version\")",
        "                        or default_info[\"app_version\"]",
        "                    )",
        "                    return {",
        "                        \"app_version\": str(app_version),",
        "                        \"data_version\": str(data.get(\"data_version\", default_info[\"data_version\"])),",
        "                        \"updated_at\": str(data.get(\"updated_at\", data.get(\"release_date\", default_info[\"updated_at\"]))),",
        "                        \"release_date\": str(data.get(\"release_date\", default_info[\"release_date\"])),",
        "                        \"minimum_app_version\": str(data.get(\"minimum_app_version\", app_version)),",
        "                    }",
        "            except Exception:",
        "                pass",
        "        return default_info",
        "",
        "    def show_program_info(self):",
        "        version_info = self.get_app_version_info()",
        "        app_version = version_info.get(\"app_version\", \"2.0.1\")",
        "        data_version = version_info.get(\"data_version\", \"-\")",
        "        updated_at = version_info.get(\"updated_at\", \"-\")",
        "        release_date = version_info.get(\"release_date\", \"-\")",
        "        minimum_app_version = version_info.get(\"minimum_app_version\", app_version)",
        "",
        "        info_text = (",
        "            f\"🏫 명덕외고 교사 시간표 v{app_version}\\n\\n\"",
        "            f\"앱 버전 : {app_version}\\n\"",
        "            f\"데이터 버전 : {data_version}\\n\"",
        "            f\"업데이트 날짜 : {updated_at}\\n\"",
        "            f\"최소 지원 앱 버전 : {minimum_app_version}\\n\"",
        "            f\"릴리즈 날짜 : {release_date}\\n\\n\"",
        "            \"개발 및 저작권자 : 표선생\\n\"",
        "            \"이메일 : vyalsgh@gmail.com\\n\\n\"",
        "            \"Copyright ⓒ 2026 표선생. All rights reserved.\\n\"",
        "            \"본 프로그램의 무단 배포 및 상업적 이용을 금합니다.\"",
        "        )",
        "        messagebox.showinfo(\"프로그램 정보\", info_text)",
        "",
    ]
    return "\n".join(lines) + "\n"


def patch_program_info(text):
    new_block = make_new_block()
    if "def get_app_version_info(self)" in text:
        pattern = r"    def get_app_version_info\(self\):\n.*?    def show_program_info\(self\):\n.*?messagebox\.showinfo\(\"프로그램 정보\", info_text\)\n"
    else:
        pattern = r"    def show_program_info\(self\):\n.*?messagebox\.showinfo\(\"프로그램 정보\", info_text\)\n"
    new_text, n = re.subn(pattern, new_block, text, flags=re.S)
    if n != 1:
        raise RuntimeError("show_program_info 메서드를 찾지 못했습니다.")
    return new_text


def main():
    print("==============================================")
    print("PC 앱 프로그램 정보 버전 표시 패치")
    print("==============================================")
    print()
    if not TARGET.exists():
        print(f"[오류] 대상 파일이 없습니다: {TARGET}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)
    text = TARGET.read_text(encoding="utf-8", errors="replace")
    BACKUP.write_text(text, encoding="utf-8")
    print(f"[백업 완료] {BACKUP}")
    text = ensure_json_import(text)
    text = patch_program_info(text)
    TARGET.write_text(text, encoding="utf-8")
    print("[완료] 프로그램 정보 창이 version.json을 읽도록 수정되었습니다.")
    print()
    print("확인 명령:")
    print("python desktop\\timetable.pyw")
    print("앱 실행 후 설정 > 프로그램 정보에서 v2.0.1 및 데이터 버전이 보이는지 확인하세요.")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

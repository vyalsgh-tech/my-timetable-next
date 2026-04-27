# tools/force_fix_program_info_clean.py
# ------------------------------------------------------------
# 프로그램 정보 창에 \n이 문자 그대로 표시되는 문제를 강제 복구합니다.
# 기존 get_app_version_info/show_program_info 메서드를 모두 제거하고
# 깨끗한 새 메서드 2개를 다시 삽입합니다.
#
# 실행:
#   python tools\force_fix_program_info_clean.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_force_program_info_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"


def ensure_import(text, module_name):
    if f'import {module_name}' in text:
        return text
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            insert_at = i + 1
    lines.insert(insert_at, f'import {module_name}')
    return '\n'.join(lines) + '\n'


def remove_method_blocks(text):
    lines = text.splitlines()
    out = []
    skip = False

    for line in lines:
        is_target_method = (
            line.startswith('    def get_app_version_info(self):')
            or line.startswith('    def show_program_info(self):')
        )

        if is_target_method:
            skip = True
            continue

        if skip:
            # 클래스 안의 다음 메서드 또는 구분선이 나오면 스킵 종료
            if line.startswith('    def ') or line.startswith('    # =========================================='):
                skip = False
                out.append(line)
            else:
                continue
        else:
            out.append(line)

    return '\n'.join(out) + '\n'


def make_clean_methods():
    block = [
        "    def get_app_version_info(self):",
        "        default_info = {",
        "            \"app_version\": \"2.0.1\",",
        "            \"data_version\": \"-\",",
        "            \"updated_at\": \"-\",",
        "            \"release_date\": \"-\",",
        "            \"minimum_app_version\": \"-\",",
        "        }",
        "",
        "        candidate_paths = []",
        "        try:",
        "            candidate_paths.append(os.path.join(self.data_dir, \"version.json\"))",
        "        except Exception:",
        "            pass",
        "        try:",
        "            candidate_paths.append(os.path.join(self.project_root, \"data\", \"version.json\"))",
        "        except Exception:",
        "            pass",
        "        try:",
        "            candidate_paths.append(os.path.join(os.getcwd(), \"data\", \"version.json\"))",
        "        except Exception:",
        "            pass",
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
        "            \"🏫 명덕외고 교사 시간표 v\" + str(app_version) + chr(10) + chr(10) +",
        "            \"앱 버전 : \" + str(app_version) + chr(10) +",
        "            \"데이터 버전 : \" + str(data_version) + chr(10) +",
        "            \"업데이트 날짜 : \" + str(updated_at) + chr(10) +",
        "            \"최소 지원 앱 버전 : \" + str(minimum_app_version) + chr(10) +",
        "            \"릴리즈 날짜 : \" + str(release_date) + chr(10) + chr(10) +",
        "            \"개발 및 저작권자 : 표선생\" + chr(10) +",
        "            \"이메일 : vyalsgh@gmail.com\" + chr(10) + chr(10) +",
        "            \"Copyright ⓒ 2026 표선생. All rights reserved.\" + chr(10) +",
        "            \"본 프로그램의 무단 배포 및 상업적 이용을 금합니다.\"",
        "        )",
        "        messagebox.showinfo(\"프로그램 정보\", info_text)",
        "",
    ]
    return '\n'.join(block)


def insert_clean_methods(text):
    methods = make_clean_methods()
    markers = [
        '    def open_github_releases_page(self):',
        '    def show_update_guide(self):',
        '    def refresh_supabase_base_data(self):',
        '    def show_data_source_info(self):',
        '    # ==========================================\n    # 💡 3. 로그인',
    ]
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            return text[:idx] + methods + '\n\n' + text[idx:]
    raise RuntimeError('새 메서드를 삽입할 위치를 찾지 못했습니다.')


def main():
    print('==============================================')
    print('프로그램 정보 강제 정리 패치')
    print('==============================================')
    print()
    if not TARGET.exists():
        print(f'[오류] 대상 파일이 없습니다: {TARGET}')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)

    original = TARGET.read_text(encoding='utf-8', errors='replace')
    BACKUP.write_text(original, encoding='utf-8')
    print(f'[백업 완료] {BACKUP}')

    text = ensure_import(original, 'json')
    text = remove_method_blocks(text)
    text = insert_clean_methods(text)
    TARGET.write_text(text, encoding='utf-8')

    print('[완료] 프로그램 정보 메서드를 모두 제거 후 깨끗하게 다시 삽입했습니다.')
    print()
    print('확인 명령:')
    print('python desktop\\timetable.pyw')
    print('설정 > 프로그램 정보')
    print()
    input('엔터를 누르면 종료합니다.')


if __name__ == '__main__':
    main()

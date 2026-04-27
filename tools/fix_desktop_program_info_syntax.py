# tools/fix_desktop_program_info_syntax.py
# ------------------------------------------------------------
# 잘못 패치된 프로그램 정보 f-string 문법 오류를 복구합니다.
# 실행: python tools\fix_desktop_program_info_syntax.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "desktop" / "timetable.pyw"
BACKUP = ROOT / "desktop" / f"timetable_before_program_info_syntax_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pyw"


def ensure_import(text, module_name):
    if f'import {module_name}' in text:
        return text
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('import ') or s.startswith('from '):
            insert_at = i + 1
    lines.insert(insert_at, f'import {module_name}')
    return '\n'.join(lines) + '\n'


def build_replacement_block():
    lines = [
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
        "                    app_version = data.get(\"app_version\") or data.get(\"minimum_app_version\") or data.get(\"min_app_version\") or default_info[\"app_version\"]",
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
        "        info_text = \"\".join([",
        "            f\"🏫 명덕외고 교사 시간표 v{app_version}\\\\n\\\\n\",",
        "            f\"앱 버전 : {app_version}\\\\n\",",
        "            f\"데이터 버전 : {data_version}\\\\n\",",
        "            f\"업데이트 날짜 : {updated_at}\\\\n\",",
        "            f\"최소 지원 앱 버전 : {minimum_app_version}\\\\n\",",
        "            f\"릴리즈 날짜 : {release_date}\\\\n\\\\n\",",
        "            \"개발 및 저작권자 : 표선생\\\\n\",",
        "            \"이메일 : vyalsgh@gmail.com\\\\n\\\\n\",",
        "            \"Copyright ⓒ 2026 표선생. All rights reserved.\\\\n\",",
        "            \"본 프로그램의 무단 배포 및 상업적 이용을 금합니다.\",",
        "        ])",
        "        messagebox.showinfo(\"프로그램 정보\", info_text)",
        "",
    ]
    return '\n'.join(lines)


def patch_text(text):
    replacement = build_replacement_block()
    if '    def get_app_version_info(self):' in text:
        start = text.find('    def get_app_version_info(self):')
    else:
        start = text.find('    def show_program_info(self):')
    if start == -1:
        raise RuntimeError('get_app_version_info/show_program_info 메서드를 찾지 못했습니다.')

    end_marker = '        messagebox.showinfo("프로그램 정보", info_text)'
    end = text.find(end_marker, start)
    if end == -1:
        # 깨진 f-string 때문에 끝부분을 못 찾는 경우, 다음 메서드/구분선 시작 전까지 잘라냄
        candidates = []
        for marker in ['\n    def ', '\n    # ==========================================']:
            pos = text.find(marker, start + 10)
            if pos != -1:
                candidates.append(pos)
        if not candidates:
            raise RuntimeError('show_program_info 끝 위치를 찾지 못했습니다.')
        end = min(candidates)
        return text[:start] + replacement + '\n' + text[end:]

    end = end + len(end_marker)
    # 줄 끝까지 포함
    if end < len(text) and text[end:end+2] == '\r\n':
        end += 2
    elif end < len(text) and text[end:end+1] == '\n':
        end += 1
    return text[:start] + replacement + '\n' + text[end:]


def main():
    print('==============================================')
    print('PC 앱 프로그램 정보 문법 오류 복구')
    print('==============================================')
    print()
    if not TARGET.exists():
        print(f'[오류] 대상 파일이 없습니다: {TARGET}')
        input('엔터를 누르면 종료합니다.')
        sys.exit(1)
    text = TARGET.read_text(encoding='utf-8', errors='replace')
    BACKUP.write_text(text, encoding='utf-8')
    print(f'[백업 완료] {BACKUP}')
    text = ensure_import(text, 'json')
    text = patch_text(text)
    TARGET.write_text(text, encoding='utf-8')
    print('[완료] 프로그램 정보 메서드를 안전한 코드로 교체했습니다.')
    print()
    print('다음 명령으로 확인하세요:')
    print('python desktop\\timetable.pyw')
    print()
    input('엔터를 누르면 종료합니다.')


if __name__ == '__main__':
    main()

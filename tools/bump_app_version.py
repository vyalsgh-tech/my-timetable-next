# tools/bump_app_version.py
# ------------------------------------------------------------
# 앱 버전을 안전하게 올리는 도구
#
# 기본 동작:
#   data/version.json의 앱 버전을 2.0.1로 변경합니다.
#   기존 data_version, updated_at 등 다른 값은 최대한 유지합니다.
#
# 실행:
#   python tools\bump_app_version.py
# ------------------------------------------------------------

import json
from datetime import datetime
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "data" / "version.json"
BACKUP_FILE = ROOT / "data" / f"version_before_bump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

NEW_APP_VERSION = "2.0.1"


def main():
    print("==============================================")
    print("앱 버전 업데이트 도구")
    print("==============================================")
    print()

    if not VERSION_FILE.exists():
        print(f"[오류] version.json 파일이 없습니다: {VERSION_FILE}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    try:
        with open(VERSION_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[오류] version.json 읽기 실패: {e}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    BACKUP_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    old_app_version = (
        data.get("app_version")
        or data.get("minimum_app_version")
        or data.get("min_app_version")
        or "-"
    )

    data["app_version"] = NEW_APP_VERSION

    # 기존 필드가 minimum_app_version을 기준으로 되어 있으면 같이 맞춰둠
    if "minimum_app_version" in data:
        data["minimum_app_version"] = NEW_APP_VERSION

    # 배포 생성일 기록
    data["release_date"] = datetime.now().strftime("%Y-%m-%d")

    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("[완료]")
    print(f"- 이전 앱 버전: {old_app_version}")
    print(f"- 새 앱 버전: {NEW_APP_VERSION}")
    print(f"- 수정 파일: {VERSION_FILE}")
    print(f"- 백업 파일: {BACKUP_FILE}")
    print()
    print("다음 단계:")
    print("1. python desktop\\timetable.pyw 로 화면 확인")
    print("2. build\\build_pc_release.bat 로 재빌드")
    print("3. python tools\\make_release_package.py 로 릴리즈 패키지 생성")
    print()
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

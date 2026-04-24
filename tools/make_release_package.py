# tools/make_release_package.py
# ------------------------------------------------------------
# 차세대 시간표 배포 패키지 생성 도구
# ------------------------------------------------------------
# 목적:
#   빌드가 끝난 EXE/설치파일을 배포용 폴더로 정리합니다.
#
# 입력:
#   dist/MyTimetableNext.exe
#   dist/installer/MyTimetableNextSetup.exe
#   data/version.json
#
# 출력:
#   releases/MyTimetableNext_<버전>_<날짜>/
#     - MyTimetableNextSetup_<버전>.exe
#     - MyTimetableNext_<버전>.exe
#     - version.json
#     - SHA256SUMS.txt
#     - RELEASE_NOTES.txt
#
# 실행:
#   python tools\make_release_package.py
#
# 주의:
#   supabase_config.json은 절대 복사하지 않습니다.
# ------------------------------------------------------------

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"
INSTALLER_DIR = DIST_DIR / "installer"
DATA_DIR = ROOT / "data"
RELEASES_DIR = ROOT / "releases"

EXE_FILE = DIST_DIR / "MyTimetableNext.exe"
INSTALLER_FILE = INSTALLER_DIR / "MyTimetableNextSetup.exe"
VERSION_FILE = DATA_DIR / "version.json"


def read_version():
    default = {
        "app_version": "2.0.0",
        "data_version": "2026.2.0",
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }

    if not VERSION_FILE.exists():
        return default

    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "app_version": str(data.get("app_version") or data.get("minimum_app_version") or default["app_version"]).strip(),
            "data_version": str(data.get("data_version") or default["data_version"]).strip(),
            "updated_at": str(data.get("updated_at") or data.get("release_date") or default["updated_at"]).strip(),
            **data,
        }
    except Exception:
        return default


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def copy_if_exists(src: Path, dst: Path, copied_files):
    if src.exists():
        shutil.copy2(src, dst)
        copied_files.append(dst)
        return True
    return False


def main():
    print("==============================================")
    print("차세대 시간표 배포 패키지 생성 도구")
    print("==============================================")
    print()

    version_info = read_version()
    app_version = str(version_info.get("app_version", "2.0.0")).replace(" ", "_")
    data_version = str(version_info.get("data_version", "2026.2.0")).replace(" ", "_")
    today = datetime.now().strftime("%Y%m%d")

    release_name = f"MyTimetableNext_v{app_version}_data{data_version}_{today}"
    release_dir = RELEASES_DIR / release_name

    print("[버전 정보]")
    print(f"- 앱 버전: {app_version}")
    print(f"- 데이터 버전: {data_version}")
    print(f"- 업데이트 날짜: {version_info.get('updated_at', '-')}")
    print()

    if not EXE_FILE.exists():
        print(f"[오류] EXE 파일이 없습니다: {EXE_FILE}")
        print("먼저 build\\build_pc_release.bat 를 실행하세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    if not INSTALLER_FILE.exists():
        print(f"[경고] 설치파일이 없습니다: {INSTALLER_FILE}")
        print("Inno Setup 설치 후 build\\build_pc_release.bat 를 다시 실행하면 생성됩니다.")
        print("이번 패키지에는 단독 EXE만 포함합니다.")
        print()

    release_dir.mkdir(parents=True, exist_ok=True)

    copied_files = []

    installer_target = release_dir / f"MyTimetableNextSetup_v{app_version}.exe"
    exe_target = release_dir / f"MyTimetableNext_v{app_version}.exe"
    version_target = release_dir / "version.json"

    copy_if_exists(INSTALLER_FILE, installer_target, copied_files)
    copy_if_exists(EXE_FILE, exe_target, copied_files)
    copy_if_exists(VERSION_FILE, version_target, copied_files)

    sums_path = release_dir / "SHA256SUMS.txt"
    with open(sums_path, "w", encoding="utf-8") as f:
        for file_path in copied_files:
            digest = sha256_file(file_path)
            f.write(f"{digest}  {file_path.name}\n")

    notes_path = release_dir / "RELEASE_NOTES.txt"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("MyTimetableNext Release Notes\n")
        f.write("=" * 60 + "\n")
        f.write(f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"앱 버전: {app_version}\n")
        f.write(f"데이터 버전: {data_version}\n")
        f.write(f"업데이트 날짜: {version_info.get('updated_at', '-')}\n")
        f.write("\n")
        f.write("[포함 파일]\n")
        for file_path in copied_files:
            f.write(f"- {file_path.name}\n")
        f.write("- SHA256SUMS.txt\n")
        f.write("- RELEASE_NOTES.txt\n")
        f.write("\n")
        f.write("[설치 전 확인]\n")
        f.write("1. 기존 설치본이 있으면 제거 후 설치 권장\n")
        f.write("2. 설치 후 시간표/학사일정/메모 표시 확인\n")
        f.write("3. 설정 > 업데이트 확인 / 데이터 새로고침 확인\n")
        f.write("\n")
        f.write("[보안]\n")
        f.write("- supabase_config.json은 배포 패키지에 포함하지 않음\n")
        f.write("- Supabase 키는 Streamlit Secrets 또는 관리자 PC 로컬 설정에서만 관리\n")

    print("[완료]")
    print(f"- 배포 폴더: {release_dir}")
    print()
    print("[포함 파일]")
    for file_path in copied_files:
        print(f"- {file_path.name}")
    print("- SHA256SUMS.txt")
    print("- RELEASE_NOTES.txt")
    print()
    print("다음 단계:")
    print("1. releases 폴더에서 생성된 배포 폴더를 확인하세요.")
    print("2. GitHub Releases에 설치파일을 업로드하면 됩니다.")
    print()

    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

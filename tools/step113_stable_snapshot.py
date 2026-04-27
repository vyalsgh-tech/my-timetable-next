from pathlib import Path
from datetime import datetime
import shutil
import py_compile
import re
import sys

ROOT = Path.cwd()
APP = ROOT / "mobile" / "app.py"
OUT_DIR = ROOT / "tools" / "_step113_stable_snapshot"
REPORT = ROOT / "tools" / "step113_stable_snapshot_report.txt"

def read_text(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors="ignore")

def compile_ok(path: Path):
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def main() -> int:
    print("=" * 60)
    print("Step113 안정 상태 스냅샷 생성")
    print(f"프로젝트 루트: {ROOT}")
    print(f"대상 파일: {APP}")
    print("=" * 60)

    if not APP.exists():
        print("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        return 1

    ok, err = compile_ok(APP)
    if not ok:
        print("[오류] 현재 mobile/app.py 문법검사 실패. 스냅샷을 만들지 않습니다.")
        print(err)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot = OUT_DIR / f"app_stable_after_step112_{ts}.py"
    shutil.copy2(APP, snapshot)

    text = read_text(APP)
    markers = [
        "STEP69_WEB_HELPERS_START",
        "STEP99_HEADER_TOOLBAR_TABLE_CSS_BEGIN",
        "STEP103_STABLE_HELPERS_BEGIN",
        "STEP104_TABLE_CELL_FILL_FIX_BEGIN",
        "STEP105_LOVELY_PINK_AND_READABILITY_BEGIN",
        "STEP106_SECTION_THEME_HELPER_BEGIN",
        "STEP107_FINAL_SECTION_COLOR_HELPER_BEGIN",
        "STEP109_AUTOFONT_SAFE_BEGIN",
        "STEP110_TITLE_AND_PERIOD_HIGHLIGHT_CSS_BEGIN",
        "STEP111_TITLE_DAY_PERIOD_RULES_CSS_BEGIN",
        "STEP112_NO_AFTERHOURS_QUERY_FILL_CSS_BEGIN",
    ]

    found = []
    for marker in markers:
        count = text.count(marker)
        if count:
            found.append(f"- {marker}: {count}")

    suspicious = []
    for marker in ["STEP108_TITLE_AND_AUTOFONT", "STEP108B_TITLE_AND_AUTOFONT", "STEP108C_AUTOFONT", "step108_plain = re.sub"]:
        count = text.count(marker)
        if count:
            suspicious.append(f"- {marker}: {count}")

    report_lines = [
        "Step113 Stable Snapshot Report",
        "=" * 60,
        f"ROOT: {ROOT}",
        f"APP: {APP}",
        f"SNAPSHOT: {snapshot}",
        "",
        "[1] Syntax",
        "OK",
        "",
        "[2] Current stable status",
        "- 앱 실행 복구 완료",
        "- 달력 버튼 수정 완료: 더 이상 건드리지 않음",
        "- 표 헤더/교시칸 셀 전체 채우기 수정 완료",
        "- 18:00~다음날 05:59 야간 조회/교시 강조 제거 적용",
        "- 현재 상태를 안정 스냅샷으로 보관",
        "",
        "[3] Detected patch markers",
        *(found if found else ["- No known patch markers found"]),
        "",
        "[4] Suspicious failed-step remnants",
        *(suspicious if suspicious else ["- None detected"]),
        "",
        "[5] Next recommended work order",
        "1. 제목 위치 미세 조정",
        "2. 시간표 셀 자동 폰트/줄바꿈 실제 화면 확인 후 보정",
        "3. 현재교시/다음교시 강조를 실제 시간대별로 검증",
        "4. 마지막으로 배포용 정리본 생성",
        "",
    ]
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"[문법검사] OK")
    print(f"[스냅샷 생성] {snapshot}")
    print(f"[보고서 생성] {REPORT}")
    print("[완료] 현재 안정 상태를 보관했습니다.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

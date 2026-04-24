# tools/admin_update_supabase_data.py
# ------------------------------------------------------------
# 차세대 시간표 관리자용 데이터 업데이트 도구
# ------------------------------------------------------------
# 목적:
#   신학기/중간 시간표 변경 시 아래 CSV를 Supabase에 일괄 반영합니다.
#
# 입력 파일:
#   data/timetable.csv
#   data/academic_calendar.csv
#
# 업로드 대상:
#   public.timetable_entries
#   public.academic_calendar
#
# 특징:
#   - 기존 users / memos / custom_schedule은 건드리지 않음
#   - CSV 검증 후 업로드
#   - 기본값은 upsert 방식: 기존 행은 갱신, 새 행은 추가
#   - 선택하면 기존 시간표/학사일정을 먼저 비운 뒤 전체 교체 가능
#   - SSL 인증서 오류 우회 옵션 포함
#   - reports/admin_update_report.txt 생성
#
# 실행:
#   python tools/admin_update_supabase_data.py
#
# 필요:
#   저장소 루트에 supabase_config.json 또는 .streamlit/secrets.toml
# ------------------------------------------------------------

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("[오류] requests 모듈이 없습니다.")
    print("아래 명령을 먼저 실행하세요:")
    print("python -m pip install requests")
    input("엔터를 누르면 종료합니다.")
    sys.exit(1)


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports"
REPORT_FILE = REPORT_DIR / "admin_update_report.txt"

TIMETABLE_FILE = DATA_DIR / "timetable.csv"
CALENDAR_FILE = DATA_DIR / "academic_calendar.csv"
CONFIG_FILE = ROOT / "supabase_config.json"
STREAMLIT_SECRETS_FILE = ROOT / ".streamlit" / "secrets.toml"

DAYS = {"월", "화", "수", "목", "금"}
BATCH_SIZE = 500
VERIFY_SSL = False


def request_get(url: str, **kwargs):
    kwargs.setdefault("verify", VERIFY_SSL)
    return requests.get(url, **kwargs)


def request_post(url: str, **kwargs):
    kwargs.setdefault("verify", VERIFY_SSL)
    return requests.post(url, **kwargs)


def request_delete(url: str, **kwargs):
    kwargs.setdefault("verify", VERIFY_SSL)
    return requests.delete(url, **kwargs)


def read_config_from_json() -> Tuple[str, str]:
    if not CONFIG_FILE.exists():
        return "", ""

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return (
            str(data.get("SUPABASE_URL", "")).strip(),
            str(data.get("SUPABASE_KEY", "")).strip(),
        )
    except Exception as e:
        print(f"[경고] supabase_config.json 읽기 실패: {e}")
        return "", ""


def read_config_from_streamlit_secrets() -> Tuple[str, str]:
    if not STREAMLIT_SECRETS_FILE.exists():
        return "", ""

    url = ""
    key = ""

    try:
        with open(STREAMLIT_SECRETS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                name, value = line.split("=", 1)
                name = name.strip()
                value = value.strip().strip('"').strip("'")

                if name == "SUPABASE_URL":
                    url = value
                elif name == "SUPABASE_KEY":
                    key = value

        return url, key
    except Exception as e:
        print(f"[경고] .streamlit/secrets.toml 읽기 실패: {e}")
        return "", ""


def get_supabase_config() -> Tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_KEY", "").strip()

    if url and key:
        return url, key

    url, key = read_config_from_json()
    if url and key:
        return url, key

    url, key = read_config_from_streamlit_secrets()
    if url and key:
        return url, key

    print()
    print("[안내] Supabase 접속 정보가 없습니다.")
    print("저장소 루트에 supabase_config.json 파일을 두는 방식을 추천합니다.")
    print()
    url = input("SUPABASE_URL: ").strip()
    key = input("SUPABASE_KEY: ").strip()
    return url, key


def make_headers(key: str) -> Dict[str, str]:
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }


def validate_url_key(url: str, key: str) -> None:
    if not url:
        raise ValueError("SUPABASE_URL이 비어 있습니다.")

    if not key:
        raise ValueError("SUPABASE_KEY가 비어 있습니다.")

    if not url.startswith("https://") or ".supabase.co" not in url:
        raise ValueError("SUPABASE_URL 형식이 이상합니다. 예: https://xxxx.supabase.co")

    if len(key) < 50:
        raise ValueError("SUPABASE_KEY가 너무 짧습니다. 복사가 잘렸는지 확인하세요.")


def normalize_subject(value: str) -> str:
    return str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def load_timetable() -> List[Dict]:
    if not TIMETABLE_FILE.exists():
        raise FileNotFoundError(f"시간표 파일이 없습니다: {TIMETABLE_FILE}")

    rows = []
    errors = []

    with open(TIMETABLE_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"teacher", "day", "period", "subject"}

        if not reader.fieldnames:
            raise ValueError("timetable.csv 헤더를 읽을 수 없습니다.")

        headers = {h.strip() for h in reader.fieldnames if h}
        missing = required - headers

        if missing:
            raise ValueError(f"timetable.csv 필수 헤더 누락: {', '.join(sorted(missing))}")

        for idx, row in enumerate(reader, start=2):
            teacher = (row.get("teacher") or "").strip()
            day = (row.get("day") or "").strip()
            period_raw = (row.get("period") or "").strip()
            subject = normalize_subject(row.get("subject"))

            if not teacher:
                errors.append(f"{idx}행: teacher 비어 있음")
                continue

            if day not in DAYS:
                errors.append(f"{idx}행: day 값 오류({day})")
                continue

            try:
                period = int(period_raw)
            except Exception:
                errors.append(f"{idx}행: period 숫자 아님({period_raw})")
                continue

            if period < 1 or period > 9:
                errors.append(f"{idx}행: period 범위 오류({period})")
                continue

            if not subject:
                errors.append(f"{idx}행: subject 비어 있음")
                continue

            rows.append({
                "teacher_name": teacher,
                "day": day,
                "period": period,
                "subject": subject,
            })

    if errors:
        print("[시간표 검증 경고]")
        for msg in errors[:30]:
            print("-", msg)

        if len(errors) > 30:
            print(f"... 외 {len(errors) - 30}건")

        raise ValueError("timetable.csv 검증 실패. 위 내용을 수정한 뒤 다시 실행하세요.")

    return rows


def load_calendar() -> List[Dict]:
    if not CALENDAR_FILE.exists():
        raise FileNotFoundError(f"학사일정 파일이 없습니다: {CALENDAR_FILE}")

    rows = []
    errors = []

    with open(CALENDAR_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"date", "event"}

        if not reader.fieldnames:
            raise ValueError("academic_calendar.csv 헤더를 읽을 수 없습니다.")

        headers = {h.strip() for h in reader.fieldnames if h}
        missing = required - headers

        if missing:
            raise ValueError(f"academic_calendar.csv 필수 헤더 누락: {', '.join(sorted(missing))}")

        for idx, row in enumerate(reader, start=2):
            date_text = (row.get("date") or "").strip()
            event = str(row.get("event") or "").strip()

            if not date_text:
                errors.append(f"{idx}행: date 비어 있음")
                continue

            try:
                datetime.strptime(date_text, "%Y-%m-%d")
            except Exception:
                errors.append(f"{idx}행: date 형식 오류({date_text})")
                continue

            if not event:
                errors.append(f"{idx}행: event 비어 있음")
                continue

            rows.append({
                "date": date_text,
                "event": event,
            })

    if errors:
        print("[학사일정 검증 경고]")
        for msg in errors[:30]:
            print("-", msg)

        if len(errors) > 30:
            print(f"... 외 {len(errors) - 30}건")

        raise ValueError("academic_calendar.csv 검증 실패. 위 내용을 수정한 뒤 다시 실행하세요.")

    return rows


def chunked(items: List[Dict], size: int):
    for i in range(0, len(items), size):
        yield i, items[i:i + size]


def test_connection(url: str, headers: Dict[str, str]) -> None:
    r = request_get(
        f"{url}/rest/v1/timetable_entries?select=id&limit=1",
        headers=headers,
        timeout=15,
    )

    if r.status_code not in (200, 206):
        raise RuntimeError(
            f"Supabase 연결 또는 권한 오류: status={r.status_code}, body={r.text[:1000]}"
        )


def delete_table_rows(url: str, headers: Dict[str, str], table: str) -> int:
    """
    전체 교체용 삭제.
    id가 0보다 큰 행을 삭제합니다.
    현재 테이블 id는 bigint generated identity 구조를 전제로 합니다.
    """
    endpoint = f"{url}/rest/v1/{table}?id=gt.0"

    delete_headers = dict(headers)
    delete_headers["Prefer"] = "return=representation"

    r = request_delete(endpoint, headers=delete_headers, timeout=60)

    if r.status_code not in (200, 204):
        raise RuntimeError(
            f"{table} 기존 데이터 삭제 실패: status={r.status_code}, body={r.text[:1000]}"
        )

    try:
        deleted = r.json()
        return len(deleted) if isinstance(deleted, list) else 0
    except Exception:
        return 0


def upsert_rows(url: str, headers: Dict[str, str], table: str, conflict_cols: str, rows: List[Dict]) -> int:
    total = 0

    for start, batch in chunked(rows, BATCH_SIZE):
        endpoint = f"{url}/rest/v1/{table}?on_conflict={conflict_cols}"

        r = request_post(
            endpoint,
            headers=headers,
            json=batch,
            timeout=60,
        )

        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"{table} 업로드 실패: status={r.status_code}, body={r.text[:1500]}"
            )

        total += len(batch)
        print(f"[업로드] {table}: {min(start + len(batch), len(rows))}/{len(rows)}")

    return total


def write_report(mode: str, timetable_count: int, calendar_count: int, deleted_timetable: int, deleted_calendar: int) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("차세대 시간표 관리자 업데이트 보고서")
    lines.append("=" * 60)
    lines.append(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"업데이트 방식: {mode}")
    lines.append("")
    lines.append("[삭제]")
    lines.append(f"- timetable_entries 삭제: {deleted_timetable}건")
    lines.append(f"- academic_calendar 삭제: {deleted_calendar}건")
    lines.append("")
    lines.append("[업로드]")
    lines.append(f"- timetable_entries 업로드/갱신: {timetable_count}건")
    lines.append(f"- academic_calendar 업로드/갱신: {calendar_count}건")
    lines.append("")
    lines.append("[원본 파일]")
    lines.append(f"- {TIMETABLE_FILE}")
    lines.append(f"- {CALENDAR_FILE}")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("==============================================")
    print("차세대 시간표 관리자 데이터 업데이트 도구")
    print("==============================================")
    print()

    try:
        timetable_rows = load_timetable()
        calendar_rows = load_calendar()

        teacher_count = len({r["teacher_name"] for r in timetable_rows})

        print("[CSV 검증 완료]")
        print(f"- 시간표 행 수: {len(timetable_rows)}건")
        print(f"- 교사 수: {teacher_count}명")
        print(f"- 학사일정 행 수: {len(calendar_rows)}건")
        print()

        print("[업데이트 방식 선택]")
        print("1. 안전 갱신: 같은 교사/요일/교시는 덮어쓰기, 새 데이터는 추가")
        print("2. 전체 교체: Supabase 시간표/학사일정을 모두 비운 뒤 CSV 기준으로 다시 업로드")
        print()
        mode_input = input("선택하세요 (1/2, 기본값 1): ").strip() or "1"

        if mode_input not in {"1", "2"}:
            raise ValueError("1 또는 2만 입력할 수 있습니다.")

        mode_name = "전체 교체" if mode_input == "2" else "안전 갱신"

        print()
        print(f"[선택] {mode_name}")
        print()
        confirm = input("정말 Supabase 데이터를 업데이트할까요? (y/N): ").strip().lower()

        if confirm != "y":
            print("[취소] 업데이트하지 않았습니다.")
            input("엔터를 누르면 종료합니다.")
            return

        url, key = get_supabase_config()
        validate_url_key(url, key)
        headers = make_headers(key)

        print()
        print("[Supabase 연결 확인 중]")
        print(f"- SSL 인증서 검증: {'사용' if VERIFY_SSL else '우회'}")
        test_connection(url, headers)
        print("[연결 확인 완료]")
        print()

        deleted_timetable = 0
        deleted_calendar = 0

        if mode_input == "2":
            print("[전체 교체] 기존 데이터 삭제 중")
            deleted_timetable = delete_table_rows(url, headers, "timetable_entries")
            deleted_calendar = delete_table_rows(url, headers, "academic_calendar")
            print(f"- timetable_entries 삭제: {deleted_timetable}건")
            print(f"- academic_calendar 삭제: {deleted_calendar}건")
            print()

        count1 = upsert_rows(
            url,
            headers,
            "timetable_entries",
            "teacher_name,day,period",
            timetable_rows,
        )

        count2 = upsert_rows(
            url,
            headers,
            "academic_calendar",
            "date",
            calendar_rows,
        )

        write_report(mode_name, count1, count2, deleted_timetable, deleted_calendar)

        print()
        print("[완료]")
        print(f"- 업데이트 방식: {mode_name}")
        print(f"- timetable_entries 업로드/갱신: {count1}건")
        print(f"- academic_calendar 업로드/갱신: {count2}건")
        print(f"- 보고서: {REPORT_FILE}")
        print()
        print("이제 PC 앱의 설정 > 업데이트 확인 / 데이터 새로고침 또는")
        print("모바일 웹뷰어 새로고침으로 반영 여부를 확인하세요.")
        print()
        input("엔터를 누르면 종료합니다.")

    except Exception as e:
        print()
        print("[오류 발생]")
        print(e)
        print()
        print("이 화면을 캡처해서 보내주세요.")
        input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

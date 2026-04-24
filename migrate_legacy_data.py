import csv
import io
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
LEGACY_TIMETABLE = ROOT / "data.csv"          # legacy 원본
OUTPUT_TIMETABLE = ROOT / "data" / "timetable.csv"
OUTPUT_CALENDAR = ROOT / "data" / "academic_calendar.csv"

# legacy 학사일정 파일 자동 탐색
def find_legacy_calendar_file(root: Path):
    for path in root.glob("**/*학사일정*.csv"):
        if "수업일수" not in path.name:
            return path
    return None

def read_csv_with_fallback(path: Path):
    encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, newline="") as f:
                return list(csv.reader(f))
        except Exception:
            continue
    raise RuntimeError(f"CSV를 읽을 수 없습니다: {path}")

def migrate_timetable():
    if not LEGACY_TIMETABLE.exists():
        raise FileNotFoundError(f"legacy data.csv 없음: {LEGACY_TIMETABLE}")

    rows = read_csv_with_fallback(LEGACY_TIMETABLE)
    if not rows:
        raise RuntimeError("data.csv가 비어 있습니다.")

    out_rows = [["teacher", "day", "period", "subject"]]
    days = ["월", "화", "수", "목", "금"]

    # 첫 줄 헤더 스킵
    for row in rows[1:]:
        if not row or len(row) < 36:
            continue

        teacher = (row[0] or "").strip()
        if not teacher:
            continue

        periods_per_day = (len(row) - 1) // 5
        for i, day in enumerate(days):
            start_idx = 1 + i * periods_per_day
            day_cells = row[start_idx:start_idx + periods_per_day][:9]

            for p_idx, subject in enumerate(day_cells, start=1):
                subject = (subject or "").strip()
                if subject:
                    out_rows.append([teacher, day, str(p_idx), subject])

    OUTPUT_TIMETABLE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_TIMETABLE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)

    print(f"[완료] 시간표 변환: {OUTPUT_TIMETABLE}")

def migrate_calendar():
    legacy_calendar = find_legacy_calendar_file(ROOT)
    if not legacy_calendar:
        raise FileNotFoundError("legacy 학사일정 csv를 찾지 못했습니다.")

    reader = read_csv_with_fallback(legacy_calendar)
    if not reader:
        raise RuntimeError("학사일정 CSV가 비어 있습니다.")

    # 월 헤더 줄 찾기
    header_row_idx = 0
    for i, row in enumerate(reader):
        joined = " ".join(str(x) for x in row)
        if re.search(r"\d+\s*월", joined):
            header_row_idx = i
            break

    header = reader[header_row_idx]

    # 몇 월이 몇 번째 열인지 찾기
    month_cols = {}
    for col_idx, val in enumerate(header):
        m = re.search(r"(\d+)\s*월", str(val).replace(" ", ""))
        if m:
            month = int(m.group(1))
            month_cols[month] = col_idx + 1

    out_rows = [["date", "event"]]

    for row in reader[header_row_idx + 1:]:
        if not row:
            continue

        first = str(row[0]).strip()
        if not first.isdigit():
            continue

        day_num = int(first)

        for month, ev_col in month_cols.items():
            if ev_col >= len(row):
                continue

            event = str(row[ev_col]).strip()
            if not event:
                continue

            # legacy 로직과 맞춤: 3월~12월은 2026, 1~2월은 2027
            year = 2026 if month >= 3 else 2027
            try:
                d = date(year, month, day_num)
            except ValueError:
                continue

            out_rows.append([d.isoformat(), event])

    with open(OUTPUT_CALENDAR, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)

    print(f"[완료] 학사일정 변환: {OUTPUT_CALENDAR}")
    print(f"[원본] 사용한 legacy 학사일정 파일: {legacy_calendar}")

def main():
    migrate_timetable()
    migrate_calendar()
    print("[성공] legacy 데이터를 차세대 data 폴더 형식으로 변환했습니다.")

if __name__ == "__main__":
    main()
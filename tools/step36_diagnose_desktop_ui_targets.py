# tools/step36_diagnose_desktop_ui_targets.py
# ------------------------------------------------------------
# Step36: PC버전 UI 수정 대상 진단 전용
#
# 목적:
# - 반복 패치로 기능이 꼬이지 않도록, 실제 desktop/timetable.pyw 안에서
#   1) 하단 메모 입력칸 생성 위치
#   2) 검색/A+/A- 버튼 생성 여부
#   3) 시간표 칸/수업일정 입력창 생성 위치
#   4) Shift+Enter 적용 대상
#   을 정확히 찾아 보고서로 저장합니다.
#
# 이 스크립트는 파일을 수정하지 않습니다.
#
# 실행:
#   python tools\step36_diagnose_desktop_ui_targets.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
REPORT_DIR = ROOT / "reports"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT = REPORT_DIR / f"step36_desktop_ui_targets_{STAMP}.txt"


def read_lines(path: Path):
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def add_section(out, title):
    out.append("")
    out.append("=" * 80)
    out.append(title)
    out.append("=" * 80)


def context(lines, idx, before=8, after=12):
    start = max(0, idx - before)
    end = min(len(lines), idx + after + 1)
    return start, end, lines[start:end]


def append_matches(out, lines, title, patterns, before=6, after=10, max_hits=30):
    add_section(out, title)
    hits = []

    compiled = []
    for pat in patterns:
        compiled.append(re.compile(pat, re.IGNORECASE))

    for i, line in enumerate(lines):
        if any(rx.search(line) for rx in compiled):
            hits.append(i)

    # 가까운 중복 제거
    dedup = []
    last = -999
    for i in hits:
        if i - last > 3:
            dedup.append(i)
            last = i

    out.append(f"[검색 패턴] {patterns}")
    out.append(f"[발견 수] {len(dedup)}")

    if not dedup:
        out.append("발견 없음")
        return []

    for n, idx in enumerate(dedup[:max_hits], start=1):
        s, e, block = context(lines, idx, before=before, after=after)
        out.append("")
        out.append(f"--- HIT {n}: line {idx + 1} ---")
        for line_no, text in zip(range(s + 1, e + 1), block):
            marker = ">>" if line_no == idx + 1 else "  "
            out.append(f"{marker} {line_no:5d}: {text}")

    if len(dedup) > max_hits:
        out.append("")
        out.append(f"... {len(dedup) - max_hits}개 추가 발견. 보고서 길이 제한으로 생략.")

    return dedup


def find_function_bounds(lines, hit_idx):
    # hit_idx가 속한 def 위치를 위로 찾고, 다음 def/class까지를 범위로 표시
    start = None
    for i in range(hit_idx, -1, -1):
        if re.match(r"^\s{0,8}def\s+\w+\s*\(", lines[i]) or re.match(r"^\s{0,8}class\s+\w+", lines[i]):
            start = i
            break

    if start is None:
        start = max(0, hit_idx - 20)

    indent = len(lines[start]) - len(lines[start].lstrip(" "))

    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if not stripped:
            continue
        cur_indent = len(lines[j]) - len(lines[j].lstrip(" "))
        if cur_indent <= indent and (
            re.match(r"^def\s+\w+\s*\(", stripped) or
            re.match(r"^class\s+\w+", stripped) or
            stripped.startswith("if __name__")
        ):
            end = j
            break

    return start, end


def append_function_summaries(out, lines, title, hit_indices, max_funcs=12):
    add_section(out, title)

    seen = set()
    funcs = []

    for idx in hit_indices:
        s, e = find_function_bounds(lines, idx)
        key = (s, e)
        if key not in seen:
            seen.add(key)
            funcs.append((s, e))

    out.append(f"[관련 함수/블록 수] {len(funcs)}")

    for n, (s, e) in enumerate(funcs[:max_funcs], start=1):
        header = lines[s].strip()
        out.append("")
        out.append(f"--- BLOCK {n}: lines {s + 1}-{e} / {header} ---")

        # 너무 긴 함수는 앞/중요 키워드 주변/뒤를 요약
        block = lines[s:e]
        if len(block) <= 80:
            ranges = [(s, e)]
        else:
            important = []
            for k in range(s, e):
                if any(tok in lines[k] for tok in [
                    "memo_entry", "memo_text", "검색", "A+", "A-",
                    "Entry(", "Toplevel", "askstring",
                    "수업/일정", "내용:", "bind(", "<Return>",
                    "save", "delete", "취소", "저장"
                ]):
                    important.append(k)

            ranges = [(s, min(e, s + 35))]
            for k in important[:6]:
                ranges.append((max(s, k - 5), min(e, k + 8)))
            ranges.append((max(s, e - 20), e))

            # ranges 병합
            ranges.sort()
            merged = []
            for a, b in ranges:
                if not merged or a > merged[-1][1] + 3:
                    merged.append([a, b])
                else:
                    merged[-1][1] = max(merged[-1][1], b)
            ranges = [(a, b) for a, b in merged]

        for a, b in ranges:
            out.append(f"[lines {a + 1}-{b}]")
            for line_no in range(a, b):
                out.append(f"  {line_no + 1:5d}: {lines[line_no]}")
            if b < e:
                out.append("  ...")

    if len(funcs) > max_funcs:
        out.append("")
        out.append(f"... {len(funcs) - max_funcs}개 추가 블록 생략.")


def main():
    print("==============================================")
    print("Step36 diagnose desktop UI targets")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not DESKTOP.exists():
        print(f"[오류] PC 파일이 없습니다: {DESKTOP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    REPORT_DIR.mkdir(exist_ok=True)

    lines = read_lines(DESKTOP)
    out = []

    out.append("Step36 Desktop UI Target Diagnosis Report")
    out.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    out.append(f"File: {DESKTOP}")
    out.append(f"Total lines: {len(lines)}")

    # 문법 확인
    add_section(out, "0. Python syntax check")
    try:
        compile("\n".join(lines) + "\n", str(DESKTOP), "exec")
        out.append("[OK] compile success")
    except Exception as e:
        out.append("[WARN] compile failed")
        out.append(str(e))

    # Step 패치 흔적
    append_matches(
        out, lines,
        "1. 기존 Step/MDGO 패치 흔적 확인",
        [
            r"MDGO_STEP",
            r"_mdgo",
            r"Step2[7-9]",
            r"Step3[0-9]",
            r"runtime",
            r"no-flicker",
            r"smooth",
        ],
        before=3,
        after=6,
        max_hits=50,
    )

    # 메모 입력칸
    memo_hits = append_matches(
        out, lines,
        "2. 하단 메모 입력칸/메모장 관련 위치",
        [
            r"memo_entry",
            r"memo_text",
            r"add_memo",
            r"refresh_memo_list",
            r"메모를 입력하세요",
        ],
        before=8,
        after=14,
        max_hits=60,
    )
    append_function_summaries(
        out, lines,
        "2-A. 메모 관련 함수/블록 요약",
        memo_hits,
        max_funcs=15,
    )

    # 검색/A+/A-
    button_hits = append_matches(
        out, lines,
        "3. 검색 / A+ / A- 버튼 관련 위치",
        [
            r'"검색"',
            r"'검색'",
            r'"A\+"',
            r"'A\+'",
            r'"A-"',
            r"'A-'",
            r"font.*size",
            r"memo.*font",
        ],
        before=8,
        after=14,
        max_hits=60,
    )
    append_function_summaries(
        out, lines,
        "3-A. 검색/A+/A- 관련 함수/블록 요약",
        button_hits,
        max_funcs=12,
    )

    # 시간표 셀 입력창/수업 일정 입력창
    edit_hits = append_matches(
        out, lines,
        "4. 시간표 칸/수업일정 입력창 관련 위치",
        [
            r"수업/일정",
            r"수업.*내용",
            r"일정.*내용",
            r"내용:",
            r"Toplevel",
            r"Entry\(",
            r"simpledialog\.askstring",
            r"askstring",
            r"bind\(.*<Return>",
            r"저장",
            r"삭제",
            r"취소",
            r"edit",
            r"cell",
            r"schedule",
        ],
        before=10,
        after=18,
        max_hits=80,
    )
    append_function_summaries(
        out, lines,
        "4-A. 시간표/입력창 관련 함수/블록 요약",
        edit_hits,
        max_funcs=20,
    )

    # 메인 실행부
    append_matches(
        out, lines,
        "5. root/mainloop 실행부",
        [
            r"tk\.Tk\(",
            r"mainloop\(",
            r"Timetable",
            r"withdraw",
            r"deiconify",
            r"attributes\(",
            r"update_idletasks",
            r"after\(",
        ],
        before=8,
        after=12,
        max_hits=40,
    )

    # 다음 패치를 위한 권장 정보
    add_section(out, "6. 다음 Step37 패치 판단 기준")
    out.append("아래 항목을 보고 다음 패치를 만들 예정입니다.")
    out.append("1) memo_entry가 생성되는 정확한 부모 프레임과 pack/grid 방식")
    out.append("2) 기존 검색/A+/A- 버튼이 코드에 남아 있는지 또는 완전히 사라졌는지")
    out.append("3) 수업/일정 입력창이 simpledialog인지, Toplevel+Entry인지")
    out.append("4) 시간표 셀 입력 저장 함수가 어느 함수인지")
    out.append("")
    out.append("보고서에서 중요한 부분:")
    out.append("- 2-A 메모 관련 함수/블록")
    out.append("- 3-A 검색/A+/A- 관련 함수/블록")
    out.append("- 4-A 시간표/입력창 관련 함수/블록")
    out.append("- 5 root/mainloop 실행부")

    REPORT.write_text("\n".join(out), encoding="utf-8")

    print("[완료] 진단 보고서 생성")
    print(f"[보고서] {REPORT}")
    print()
    print("다음 단계:")
    print("1. reports 폴더의 step36_desktop_ui_targets_*.txt 파일을 열어주세요.")
    print("2. 또는 이 파일을 그대로 업로드/내용 붙여넣기 해주세요.")
    print("3. 그 보고서를 기준으로 Step37에서 PC 기능을 정확히 패치하겠습니다.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

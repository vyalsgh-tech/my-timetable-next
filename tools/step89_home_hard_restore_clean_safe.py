# -*- coding: utf-8 -*-
"""
Step89 웹뷰어 안정 복구 스크립트

사용 위치:
  프로젝트 루트에서 실행:
    python tools\step89_home_hard_restore_clean_safe.py

목적:
  1) 현재 mobile/app.py를 안전 백업
  2) app_before/app_backup 계열 백업 중 오염이 적고 문법이 정상인 후보를 찾아 mobile/app.py로 복원
  3) Step80~88에서 누적된 components.html / setInterval / DOM 주입 흔적이 적은 파일을 우선 선택
  4) 학교망 Supabase SSL 오류에 대비한 최소 fallback만 삽입

주의:
  - 이 스크립트는 Git 커밋/원격 저장소를 건드리지 않습니다.
  - 모든 변경 전 현재 app.py를 tools/_step89_backups 폴더에 백업합니다.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import re
import shutil
import sys
import traceback


SCRIPT_PATH = Path(__file__).resolve()


def detect_project_root() -> Path:
    """현재 실행 위치 또는 스크립트 위치 기준으로 프로젝트 루트를 찾는다."""
    candidates = [
        Path.cwd(),
        SCRIPT_PATH.parent.parent,
        SCRIPT_PATH.parent,
    ]

    for candidate in candidates:
        if (candidate / "mobile" / "app.py").exists():
            return candidate.resolve()

    # 마지막 fallback: 현재 작업 폴더
    return Path.cwd().resolve()


ROOT = detect_project_root()
APP = ROOT / "mobile" / "app.py"
TOOLS = ROOT / "tools"
BACKUP_DIR = TOOLS / "_step89_backups"

SSL_PATCH_MARKER = "_request_with_supabase_ssl_fallback_step89"

BAD_MARKERS = [
    "st.components.v1.html",
    "components.html",
    "setInterval",
    "setTimeout",
    "querySelector",
    "querySelectorAll",
    "MutationObserver",
    "scrollTo(0, 0)",
    "scrollTop = 0",
    "window.parent",
    "current-time-badge",
    "현재시각 배지",
    "STEP80",
    "Step80",
    "STEP81",
    "Step81",
    "STEP82",
    "Step82",
    "STEP83",
    "Step83",
    "STEP84",
    "Step84",
    "STEP85",
    "Step85",
    "STEP86",
    "Step86",
    "STEP87",
    "Step87",
    "STEP88",
    "Step88",
]

GOOD_MARKERS = [
    "import streamlit as st",
    "st.set_page_config",
    "def ",
    "st.session_state",
]

EXCLUDE_DIR_PARTS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "site-packages",
    "_step89_backups",
    ".streamlit",
    "node_modules",
}


SSL_PATCH = """
# ============================================================
# Step89: Supabase SSL fallback for school/institution network
# - 일반 환경에서는 기존 SSL 검증을 유지합니다.
# - Supabase 요청에서 SSL 인증서 오류가 날 때만 verify=False로 1회 재시도합니다.
# ============================================================
try:
    import requests
    from requests.exceptions import SSLError

    if not hasattr(requests.Session, "_request_with_supabase_ssl_fallback_step89"):
        _original_requests_session_request_step89 = requests.Session.request

        def _request_with_supabase_ssl_fallback_step89(self, method, url, **kwargs):
            try:
                return _original_requests_session_request_step89(self, method, url, **kwargs)
            except SSLError:
                url_text = str(url)
                if "supabase.co" in url_text and kwargs.get("verify", True) is not False:
                    try:
                        import urllib3
                        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    except Exception:
                        pass
                    kwargs["verify"] = False
                    return _original_requests_session_request_step89(self, method, url, **kwargs)
                raise

        requests.Session.request = _request_with_supabase_ssl_fallback_step89
        requests.Session._request_with_supabase_ssl_fallback_step89 = True
except Exception:
    pass
# ============================================================
"""


def log(message: str = "") -> None:
    print(message, flush=True)


def read_text(path: Path) -> str:
    encodings = ("utf-8", "utf-8-sig", "cp949", "euc-kr")
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception:
            return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as exc:
        return False, str(exc)


def compile_text_ok(text: str, filename: str = "<text>") -> tuple[bool, str]:
    try:
        compile(text, filename, "exec")
        return True, ""
    except Exception as exc:
        return False, str(exc)


def is_excluded(path: Path) -> bool:
    parts_lower = {part.lower() for part in path.parts}
    return bool(parts_lower & EXCLUDE_DIR_PARTS)


def contamination_score(text: str) -> int:
    score = 0
    for marker in BAD_MARKERS:
        count = text.count(marker)
        if count:
            score += count * 10
    return score


def quality_score(text: str) -> int:
    score = 0
    for marker in GOOD_MARKERS:
        if marker in text:
            score += 10
    score += min(len(text) // 12000, 10)
    return score


def looks_like_streamlit_app(text: str) -> bool:
    if "streamlit" not in text:
        return False
    if "st." not in text and "streamlit as st" not in text:
        return False
    return True


def find_backup_candidates() -> list[dict]:
    patterns = [
        "**/app_before*.py",
        "**/*app_before*.py",
        "**/app_backup*.py",
        "**/*app_backup*.py",
        "**/*backup*app*.py",
        "**/app*.bak",
        "**/app.py.bak",
    ]

    found: list[Path] = []
    for pattern in patterns:
        found.extend(ROOT.glob(pattern))

    # 혹시 mobile 폴더에 app_날짜.py 식 백업이 있는 경우까지 탐색
    mobile_dir = ROOT / "mobile"
    if mobile_dir.exists():
        found.extend(mobile_dir.glob("app_*.py"))
        found.extend(mobile_dir.glob("*app*.py"))

    unique: list[Path] = []
    seen: set[Path] = set()

    for path in found:
        try:
            resolved = path.resolve()
        except Exception:
            continue

        if resolved in seen:
            continue
        seen.add(resolved)

        if not resolved.exists() or not resolved.is_file():
            continue
        if is_excluded(resolved):
            continue
        if APP.exists() and resolved == APP.resolve():
            continue
        if resolved.name == SCRIPT_PATH.name:
            continue

        text = read_text(resolved)
        if not text.strip():
            continue
        if not looks_like_streamlit_app(text):
            continue

        ok, err = compile_ok(resolved)
        bad = contamination_score(text)
        good = quality_score(text)

        # 낮은 bad가 가장 중요하다.
        # 문법 정상 파일 우선, 그다음 최신 파일 우선.
        final_score = good - bad + (100 if ok else -1000)

        unique.append(
            {
                "path": resolved,
                "score": final_score,
                "bad": bad,
                "good": good,
                "compile_ok": ok,
                "compile_error": err,
                "mtime": resolved.stat().st_mtime,
                "size": resolved.stat().st_size,
            }
        )

    unique.sort(
        key=lambda item: (
            item["compile_ok"],
            -item["bad"],
            item["score"],
            item["mtime"],
            item["size"],
        ),
        reverse=True,
    )
    return unique


def backup_current_app() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"app_current_before_step89_{timestamp}.py"
    shutil.copy2(APP, backup_path)
    return backup_path


def remove_existing_ssl_patch(text: str) -> str:
    if SSL_PATCH_MARKER not in text:
        return text

    pattern = (
        r"\n?# ============================================================\n"
        r"# Step89: Supabase SSL fallback for school/institution network\n"
        r".*?"
        r"# ============================================================\n?"
    )
    cleaned = re.sub(pattern, "\n", text, flags=re.DOTALL)
    return cleaned


def insert_ssl_patch(text: str) -> str:
    text = remove_existing_ssl_patch(text)

    lines = text.splitlines()
    insert_at = 0

    # shebang / encoding line 보존
    while insert_at < len(lines):
        stripped = lines[insert_at].strip()
        if stripped.startswith("#!") or "coding" in stripped:
            insert_at += 1
            continue
        break

    # 모듈 docstring 보존
    single_triple_quote = "'" * 3
    if insert_at < len(lines):
        stripped = lines[insert_at].lstrip()
        if stripped.startswith('"""') or stripped.startswith(single_triple_quote):
            quote = '"""' if stripped.startswith('"""') else single_triple_quote
            # 한 줄 docstring
            if stripped.count(quote) >= 2 and len(stripped) > 3:
                insert_at += 1
            else:
                insert_at += 1
                while insert_at < len(lines):
                    if quote in lines[insert_at]:
                        insert_at += 1
                        break
                    insert_at += 1

    # from __future__ import는 반드시 앞쪽 유지
    while insert_at < len(lines):
        stripped = lines[insert_at].strip()
        if not stripped:
            insert_at += 1
            continue
        if stripped.startswith("from __future__ import"):
            insert_at += 1
            continue
        break

    # 상단 import 블록 뒤에 삽입
    last_import = -1
    for i in range(insert_at, min(len(lines), 180)):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import = i
            continue

        # import 블록이 시작된 후 일반 코드가 나오면 중단
        if last_import >= 0:
            break

    if last_import >= 0:
        insert_at = last_import + 1

    new_lines = lines[:insert_at] + [SSL_PATCH.strip("\n")] + lines[insert_at:]
    return "\n".join(new_lines).rstrip() + "\n"


def strip_dom_injection_blocks(text: str) -> tuple[str, int]:
    """
    백업 후보가 없을 때만 쓰는 안전장치.
    components.html/st.components.v1.html 호출 블록을 제거한다.
    완전한 복원은 아니므로 백업 후보 복원을 우선한다.
    """
    lines = text.splitlines()
    output: list[str] = []
    removed_blocks = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        compact = line.replace(" ", "")

        is_component_call = (
            "components.html(" in compact
            or "st.components.v1.html(" in compact
        )

        if not is_component_call:
            # components import는 호출 제거 후 불필요할 가능성이 높으므로 제거
            if "import streamlit.components.v1 as components" in line:
                removed_blocks += 1
                i += 1
                continue
            output.append(line)
            i += 1
            continue

        removed_blocks += 1
        output.append(
            "# Step89 removed a Streamlit components.html DOM injection block here."
        )

        # 일반적으로 components.html(\"\"\"...\"\"\", height=...) 형태.
        # height/scrolling이 있는 닫힘 줄까지 제거하되, 최대 400줄에서 중단.
        start = i
        i += 1
        while i < len(lines) and i - start < 400:
            end_line = lines[i].strip()
            if (
                ("height=" in end_line or "scrolling=" in end_line)
                and end_line.endswith(")")
            ):
                i += 1
                break
            if end_line == ")" or end_line.endswith(",)"):
                i += 1
                break
            i += 1

    cleaned = "\n".join(output).rstrip() + "\n"
    return cleaned, removed_blocks


def choose_best_candidate(candidates: list[dict]) -> dict | None:
    clean = [c for c in candidates if c["compile_ok"] and c["bad"] == 0]
    if clean:
        clean.sort(key=lambda item: (item["mtime"], item["size"]), reverse=True)
        return clean[0]

    ok_candidates = [c for c in candidates if c["compile_ok"]]
    if ok_candidates:
        ok_candidates.sort(key=lambda item: (item["bad"], -item["mtime"], -item["size"]))
        return ok_candidates[0]

    return None


def write_report(
    current_backup: Path | None,
    selected: dict | None,
    candidates: list[dict],
    final_compile_ok: bool,
    final_compile_error: str,
    fallback_cleanup_used: bool,
    removed_blocks: int,
) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = BACKUP_DIR / f"step89_restore_report_{timestamp}.txt"

    lines = []
    lines.append("Step89 웹뷰어 안정 복구 보고서")
    lines.append(f"작성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"프로젝트 루트: {ROOT}")
    lines.append(f"대상 app.py: {APP}")
    lines.append("")
    lines.append(f"현재 app.py 백업: {current_backup if current_backup else '없음'}")
    lines.append(f"fallback cleanup 사용: {fallback_cleanup_used}")
    lines.append(f"제거한 components.html 블록 수: {removed_blocks}")
    lines.append("")
    if selected:
        lines.append("선택된 복원 후보:")
        lines.append(f"  path: {selected['path']}")
        lines.append(f"  bad_score: {selected['bad']}")
        lines.append(f"  compile_ok: {selected['compile_ok']}")
    else:
        lines.append("선택된 복원 후보: 없음")
    lines.append("")
    lines.append(f"최종 문법 검사: {'성공' if final_compile_ok else '실패'}")
    if final_compile_error:
        lines.append(f"최종 문법 오류: {final_compile_error}")
    lines.append("")
    lines.append("검색된 후보 목록:")
    for idx, item in enumerate(candidates[:30], start=1):
        lines.append(
            f"{idx:02d}. score={item['score']}, bad={item['bad']}, "
            f"compile={item['compile_ok']}, size={item['size']}, path={item['path']}"
        )

    write_text(report_path, "\n".join(lines) + "\n")
    return report_path


def main() -> int:
    log("============================================================")
    log("Step89 웹뷰어 안정 복구 시작")
    log(f"프로젝트 루트: {ROOT}")
    log(f"대상 파일: {APP}")
    log("============================================================")

    if not APP.exists():
        log("[오류] mobile/app.py 파일을 찾지 못했습니다.")
        log("       프로젝트 루트에서 실행했는지 확인해 주세요.")
        return 1

    TOOLS.mkdir(parents=True, exist_ok=True)
    current_backup = backup_current_app()
    log(f"[백업 완료] 현재 app.py 백업:")
    log(f"  {current_backup}")

    candidates = find_backup_candidates()
    log("")
    log(f"[검색] 복원 후보 {len(candidates)}개 발견")

    for idx, item in enumerate(candidates[:10], start=1):
        log(
            f"  {idx:02d}. bad={item['bad']}, compile={item['compile_ok']}, "
            f"size={item['size']}, path={item['path']}"
        )

    selected = choose_best_candidate(candidates)
    fallback_cleanup_used = False
    removed_blocks = 0

    if selected:
        log("")
        log("[선택] 아래 백업을 기준으로 app.py를 복원합니다.")
        log(f"  {selected['path']}")
        log(f"  bad_score={selected['bad']}, compile_ok={selected['compile_ok']}")
        final_text = read_text(selected["path"])
    else:
        log("")
        log("[주의] 사용할 수 있는 안정 백업 후보가 없습니다.")
        log("       현재 app.py에서 components.html DOM 주입 블록 제거를 시도합니다.")
        fallback_cleanup_used = True
        final_text = read_text(APP)
        final_text, removed_blocks = strip_dom_injection_blocks(final_text)
        log(f"       제거한 components.html 블록 수: {removed_blocks}")

    final_text = insert_ssl_patch(final_text)

    ok, err = compile_text_ok(final_text, filename=str(APP))
    if not ok:
        report_path = write_report(
            current_backup=current_backup,
            selected=selected,
            candidates=candidates,
            final_compile_ok=False,
            final_compile_error=err,
            fallback_cleanup_used=fallback_cleanup_used,
            removed_blocks=removed_blocks,
        )
        log("")
        log("[중단] 복원 결과 코드에 문법 오류가 있어 app.py를 교체하지 않았습니다.")
        log(f"       보고서: {report_path}")
        log(f"       오류: {err}")
        return 2

    write_text(APP, final_text)

    ok2, err2 = compile_ok(APP)
    report_path = write_report(
        current_backup=current_backup,
        selected=selected,
        candidates=candidates,
        final_compile_ok=ok2,
        final_compile_error=err2,
        fallback_cleanup_used=fallback_cleanup_used,
        removed_blocks=removed_blocks,
    )

    if not ok2:
        # 매우 드문 경우지만, 쓰기 후 문법 실패 시 백업 복원
        shutil.copy2(current_backup, APP)
        log("")
        log("[오류] 쓰기 후 문법 검사 실패로 기존 app.py를 다시 복원했습니다.")
        log(f"       보고서: {report_path}")
        log(f"       오류: {err2}")
        return 3

    log("")
    log("[완료] Step89 안정 복구가 끝났습니다.")
    log(f"[보고서] {report_path}")
    log("")
    log("다음 명령으로 웹뷰어를 실행하세요.")
    log("  python -m streamlit run mobile\\app.py")
    log("")
    log("확인 항목:")
    log("  1. 상단 버튼이 한 줄로 정상 표시되는지")
    log("  2. 시간표가 어두운 테마로 강제 변경되지 않는지")
    log("  3. 위쪽 빈 회색 박스가 사라졌는지")
    log("  4. 아래로 스크롤해도 최상단으로 끌려가지 않는지")
    log("  5. 테마 변경 시 Supabase SSL 에러가 사라졌는지")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        log("")
        log("[중단] 사용자가 실행을 중단했습니다.")
        raise SystemExit(130)
    except Exception:
        log("")
        log("[예상치 못한 오류]")
        traceback.print_exc()
        raise SystemExit(99)

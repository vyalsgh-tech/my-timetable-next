# tools/step31_restore_memo_buttons_only.py
# ------------------------------------------------------------
# Step31: PC 하단 메모 입력칸 오른쪽 검색/A+/A- 버튼만 안전 복구
#
# 목적:
# - Step30으로 앱 안정성은 복구됐지만 하단 메모 입력칸 오른쪽 버튼이 안 보이는 문제 해결
# - 기존 memo_entry를 destroy/repack하지 않고, 버튼 overlay만 얹어서 자동 종료 위험 최소화
#
# 실행:
#   python tools\step31_restore_memo_buttons_only.py
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DESKTOP = ROOT / "desktop" / "timetable.pyw"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = '\n# =========================================================\n# Step31 하단 메모 버튼 안전 복구 패치\n# =========================================================\ndef _mdgo_step31_restore_memo_buttons_safe():\n    """기존 메모 입력칸은 건드리지 않고, 오른쪽에 검색/A+/A- 버튼만 안전하게 얹습니다."""\n    try:\n        import tkinter as tk\n        from tkinter import messagebox\n        import gc\n    except Exception:\n        return\n\n    def _get_text(widget):\n        try:\n            if isinstance(widget, tk.Text):\n                return widget.get("1.0", "end-1c")\n            return widget.get()\n        except Exception:\n            return ""\n\n    def _set_font_size(widget, size):\n        try:\n            widget.configure(font=("맑은 고딕", size))\n        except Exception:\n            pass\n\n    def _patch_one(app):\n        if getattr(app, "_mdgo_step31_memo_buttons_installed", False):\n            return\n\n        memo_entry = getattr(app, "memo_entry", None)\n        memo_text = getattr(app, "memo_text", None)\n        root = getattr(app, "root", None)\n\n        if memo_entry is None or root is None:\n            return\n\n        parent = memo_entry.master\n\n        try:\n            bg = parent.cget("bg")\n        except Exception:\n            bg = "#ffffff"\n\n        # 버튼을 새 프레임으로 만들되, 기존 memo_entry를 destroy/repack하지 않음.\n        # 따라서 자동 종료나 UI 붕괴 위험이 낮음.\n        overlay = tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)\n        app._mdgo_step31_memo_button_overlay = overlay\n        app._mdgo_step31_memo_font_size = getattr(app, "_mdgo_step31_memo_font_size", 10)\n\n        def search_memo():\n            query = _get_text(memo_entry).strip()\n            if not query or query == "메모를 입력하세요":\n                try:\n                    messagebox.showinfo("검색", "검색할 내용을 메모 입력칸에 입력하세요.")\n                except Exception:\n                    pass\n                return\n\n            if not isinstance(memo_text, tk.Text):\n                return\n\n            try:\n                memo_text.tag_remove("mdgo_search_hit", "1.0", tk.END)\n                pos = memo_text.search(query, "1.0", tk.END, nocase=True)\n                if pos:\n                    end = f"{pos}+{len(query)}c"\n                    memo_text.tag_add("mdgo_search_hit", pos, end)\n                    memo_text.tag_config("mdgo_search_hit", background="#fff2a8", foreground="#111827")\n                    memo_text.see(pos)\n                else:\n                    messagebox.showinfo("검색", "검색 결과가 없습니다.")\n            except Exception as e:\n                try:\n                    messagebox.showwarning("검색 오류", str(e))\n                except Exception:\n                    pass\n\n        def adjust_font(delta):\n            try:\n                size = int(getattr(app, "_mdgo_step31_memo_font_size", 10))\n            except Exception:\n                size = 10\n            size = max(7, min(18, size + delta))\n            app._mdgo_step31_memo_font_size = size\n            _set_font_size(memo_text, size)\n            _set_font_size(memo_entry, size)\n\n        def make_button(text, command, width):\n            return tk.Button(\n                overlay,\n                text=text,\n                command=command,\n                width=width,\n                relief="flat",\n                bd=0,\n                bg="#2563eb" if text == "검색" else "#f3f6fb",\n                fg="white" if text == "검색" else "#111827",\n                activebackground="#1d4ed8" if text == "검색" else "#e5eaf3",\n                activeforeground="white" if text == "검색" else "#111827",\n                cursor="hand2",\n                font=("맑은 고딕", 9, "bold"),\n                padx=4,\n                pady=2,\n            )\n\n        btn_search = make_button("검색", search_memo, 5)\n        btn_plus = make_button("A+", lambda: adjust_font(1), 3)\n        btn_minus = make_button("A-", lambda: adjust_font(-1), 3)\n\n        btn_search.pack(side="left", padx=(0, 4), ipady=2)\n        btn_plus.pack(side="left", padx=(0, 2), ipady=2)\n        btn_minus.pack(side="left", padx=(0, 0), ipady=2)\n\n        def reposition():\n            try:\n                if not memo_entry.winfo_exists() or not overlay.winfo_exists():\n                    return\n\n                parent.update_idletasks()\n                memo_entry.update_idletasks()\n                overlay.update_idletasks()\n\n                entry_x = memo_entry.winfo_x()\n                entry_y = memo_entry.winfo_y()\n                entry_w = memo_entry.winfo_width()\n                entry_h = memo_entry.winfo_height()\n\n                overlay_w = overlay.winfo_reqwidth()\n                overlay_h = overlay.winfo_reqheight()\n\n                x = max(entry_x, entry_x + entry_w - overlay_w - 4)\n                y = entry_y + max(0, (entry_h - overlay_h) // 2)\n\n                overlay.place(x=x, y=y)\n                overlay.lift()\n\n                # 버튼이 입력칸을 가리는 만큼 오른쪽 여백을 조금 확보\n                try:\n                    if isinstance(memo_entry, tk.Entry):\n                        # Entry 자체 폭을 안전하게 줄이기는 어려우므로 오른쪽 overlay만 유지\n                        pass\n                except Exception:\n                    pass\n\n                root.after(500, reposition)\n            except Exception:\n                try:\n                    root.after(1000, reposition)\n                except Exception:\n                    pass\n\n        app._mdgo_step31_memo_buttons_installed = True\n        reposition()\n\n    try:\n        for obj in gc.get_objects():\n            try:\n                if hasattr(obj, "memo_entry") and hasattr(obj, "memo_text") and hasattr(obj, "root"):\n                    _patch_one(obj)\n            except Exception:\n                pass\n    except Exception:\n        pass\n\n    # 앱 초기화 직후 타이밍 차이를 고려해 몇 번 더 시도\n    try:\n        r = tk._default_root\n        if r is not None:\n            r.after(800, _mdgo_step31_restore_memo_buttons_safe)\n            r.after(1800, _mdgo_step31_restore_memo_buttons_safe)\n    except Exception:\n        pass\n\n\ntry:\n    import tkinter as tk\n    _mdgo_root = tk._default_root\n    if _mdgo_root is not None:\n        _mdgo_root.after(500, _mdgo_step31_restore_memo_buttons_safe)\nexcept Exception:\n    pass\n# =========================================================\n'


def backup(path: Path):
    if not path.exists():
        return None
    b = path.with_name(f"{path.stem}_before_step31_{STAMP}{path.suffix}")
    b.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")
    return b


def remove_old_step31(text: str) -> str:
    while "Step31 하단 메모 버튼 안전 복구 패치" in text:
        idx = text.find("Step31 하단 메모 버튼 안전 복구 패치")
        start = text.rfind("# =========================================================", 0, idx)
        if start == -1:
            start = max(0, text.rfind("\n", 0, idx))
        end = text.find("# =========================================================", idx + 20)
        if end == -1:
            text = text[:start].rstrip() + "\n"
            break
        text = text[:start] + text[end:]
    return text


def insert_before_mainloop(text: str) -> str:
    text = remove_old_step31(text)

    # mainloop 직전에 삽입해야 앱 인스턴스 생성 후 안전하게 버튼을 얹을 수 있음
    matches = list(re.finditer(r"(?m)^.*\.mainloop\s*\(\s*\)", text))
    if matches:
        m = matches[-1]
        return text[:m.start()] + PATCH_BLOCK + "\n" + text[m.start():]

    # mainloop를 못 찾으면 파일 끝에 추가
    return text.rstrip() + "\n\n" + PATCH_BLOCK + "\n"


def main():
    print("==============================================")
    print("Step31 restore memo buttons only")
    print("==============================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not DESKTOP.exists():
        print(f"[오류] PC 파일이 없습니다: {DESKTOP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup(DESKTOP)

    text = DESKTOP.read_text(encoding="utf-8", errors="replace")
    original = text

    text = insert_before_mainloop(text)

    try:
        compile(text, str(DESKTOP), "exec")
        print("[확인] PC 파일 문법 OK")
    except Exception as e:
        print("[경고] PC 파일 문법 확인 실패")
        print(e)

    if text != original:
        DESKTOP.write_text(text, encoding="utf-8")
        print("[완료] 하단 메모 버튼 안전 복구 패치 저장")
    else:
        print("[안내] 변경 없음")

    print()
    print("확인:")
    print("python desktop\\timetable.pyw")
    print()
    print("확인할 것:")
    print("- 창이 자동으로 닫히지 않는지")
    print("- 하단 메모 입력칸 오른쪽에 검색 / A+ / A- 버튼이 보이는지")
    print("- 검색 / A+ / A- 기능이 동작하는지")
    print()
    print("이번 Step31은 버튼 복구만 처리합니다. 시간표 줄바꿈은 이후 별도 Step에서 처리하세요.")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

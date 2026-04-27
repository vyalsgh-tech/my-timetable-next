# tools/step79_web_topbar_clock_calendar_order_fix.py
# ------------------------------------------------------------
# Step79: 웹뷰어 상단바 정밀 보정
# - 현재시각 표시: 'HH:MM 상태'
# - 달력 버튼 글자 가운데 정렬
# - 달력 접힘/펴짐 꺾쇠 숨김
# - 새로고침(동기화) 아이콘을 8·9와 설정 사이로 이동
#
# 다른 영역(시간표/메모/디자인)은 건드리지 않음.
# ------------------------------------------------------------

from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PATCH_BLOCK = r'''
# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_START]
try:
    import streamlit.components.v1 as components
    components.html(
        r"""
        <script>
        (function() {
            function rootDoc() {
                try { return window.parent.document; } catch (e) { return document; }
            }

            function isVisible(el) {
                if (!el) return false;
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
                const r = el.getBoundingClientRect();
                return r.width > 0 && r.height > 0;
            }

            function nowInfo() {
                const now = new Date();
                const mins = now.getHours() * 60 + now.getMinutes();
                const periods = [
                    ['1교시', '08:00', '08:50'],
                    ['2교시', '09:00', '09:50'],
                    ['3교시', '10:00', '10:50'],
                    ['4교시', '11:00', '11:50'],
                    ['점심', '11:50', '12:40'],
                    ['5교시', '12:40', '13:30'],
                    ['6교시', '13:40', '14:30'],
                    ['7교시', '14:40', '15:30'],
                    ['8교시', '16:00', '16:50'],
                    ['9교시', '17:00', '17:50']
                ];
                function toMin(t) {
                    const p = t.split(':').map(Number);
                    return p[0] * 60 + p[1];
                }
                let state = '쉬는시간';
                for (const p of periods) {
                    if (toMin(p[1]) <= mins && mins < toMin(p[2])) {
                        state = p[0];
                        break;
                    }
                }
                if (mins < 8 * 60) state = '수업 전';
                if (mins >= 17 * 60 + 50) state = '방과 후';
                const hh = String(now.getHours()).padStart(2, '0');
                const mm = String(now.getMinutes()).padStart(2, '0');
                return { clock: hh + ':' + mm, state };
            }

            function injectStyle(doc) {
                if (doc.getElementById('step79-topbar-fix-style')) return;
                const style = doc.createElement('style');
                style.id = 'step79-topbar-fix-style';
                style.textContent = `
                    .step79-clock-pill {
                        display: inline-flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        gap: 6px !important;
                        padding: 4px 10px !important;
                        border-radius: 999px !important;
                        border: 1px solid rgba(96, 165, 250, 0.35) !important;
                        background: linear-gradient(180deg, rgba(250,252,255,0.98), rgba(232,240,255,0.96)) !important;
                        color: #1d4ed8 !important;
                        box-shadow: 0 2px 7px rgba(59, 130, 246, 0.10) !important;
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                        font-size: 12px !important;
                        line-height: 1.1 !important;
                        font-weight: 700 !important;
                        text-align: center !important;
                    }
                    .step79-calendar-box,
                    .step79-calendar-box * {
                        white-space: nowrap !important;
                        word-break: keep-all !important;
                        overflow-wrap: normal !important;
                        writing-mode: horizontal-tb !important;
                        text-align: center !important;
                    }
                    .step79-calendar-box {
                        min-width: 64px !important;
                        width: 64px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        padding-left: 0 !important;
                        padding-right: 0 !important;
                        box-sizing: border-box !important;
                    }
                    .step79-hide-chevron {
                        display: none !important;
                    }
                `;
                doc.head.appendChild(style);
            }

            function patchClock(doc) {
                const info = nowInfo();
                const fullText = `${info.clock} ${info.state}`;
                const states = new Set(['수업 전', '방과 후', '쉬는시간', '1교시', '2교시', '3교시', '4교시', '점심', '5교시', '6교시', '7교시', '8교시', '9교시']);

                const candidates = Array.from(doc.querySelectorAll('div, span, p')).filter(el => {
                    if (!isVisible(el)) return false;
                    const t = (el.innerText || '').trim();
                    if (!states.has(t)) return false;
                    const r = el.getBoundingClientRect();
                    return r.top < 130 && r.left > window.innerWidth * 0.5;
                }).sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);

                if (candidates.length) {
                    const target = candidates[0];
                    target.textContent = fullText;
                    target.classList.add('step79-clock-pill');
                    const parent = target.parentElement;
                    if (parent) {
                        parent.style.setProperty('text-align', 'right', 'important');
                        parent.style.setProperty('display', 'flex', 'important');
                        parent.style.setProperty('justify-content', 'flex-end', 'important');
                        parent.style.setProperty('align-items', 'center', 'important');
                    }
                    return;
                }

                const title = Array.from(doc.querySelectorAll('h1, h2, h3, p, div, span')).find(el => {
                    if (!isVisible(el)) return false;
                    return ((el.innerText || '').trim()).includes('명덕외고 시간표 뷰어');
                });
                if (!title || !title.parentElement) return;

                let row = doc.querySelector('.step79-title-row');
                if (!row) {
                    row = doc.createElement('div');
                    row.className = 'step79-title-row';
                    row.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:10px;width:min(450px,100%);margin:0 0 8px 0;';
                    const host = doc.createElement('div');
                    host.style.cssText = 'flex:1 1 auto;min-width:0;';
                    title.parentNode.insertBefore(row, title);
                    row.appendChild(host);
                    host.appendChild(title);
                }

                let pill = row.querySelector('.step79-clock-pill');
                if (!pill) {
                    pill = doc.createElement('div');
                    pill.className = 'step79-clock-pill';
                    row.appendChild(pill);
                }
                pill.textContent = fullText;
            }

            function findToolbar(doc) {
                const blocks = Array.from(doc.querySelectorAll('div[data-testid="stHorizontalBlock"]')).filter(el => isVisible(el));
                for (const block of blocks) {
                    const t = (block.innerText || '').replace(/\s+/g, ' ');
                    if (t.includes('오늘') && t.includes('달력') && t.includes('메모')) return block;
                }
                return null;
            }

            function classifyChild(child) {
                const txt = ((child.innerText || child.textContent || '') + '').replace(/\s+/g, ' ').trim();
                if (txt.includes('오늘')) return 'today';
                if (txt === '조회' || txt.includes('조회')) return 'search';
                if (txt.includes('메모')) return 'memo';
                if (txt.includes('달력')) return 'calendar';
                if (txt.includes('8·9') || txt.includes('8-9') || txt === '89' || txt.includes('89')) return '89';
                if (/^[▾∨⌄˅﹀vV]$/.test(txt)) return 'chevron';
                if (txt.includes('⚙') || txt.includes('설정')) return 'settings';
                const html = child.innerHTML || '';
                if ((txt === '' || txt.length <= 2) && /refresh|sync|rotate|reload|arrow-repeat|counterclockwise|clockwise/i.test(html)) return 'sync';
                if (txt === '' || txt.length <= 2) {
                    const r = child.getBoundingClientRect();
                    if (r.width <= 30) return 'icon';
                }
                return 'other';
            }

            function fixCalendar(toolbar) {
                const children = Array.from(toolbar.children || []);
                for (const child of children) {
                    const kind = classifyChild(child);
                    if (kind !== 'calendar') continue;

                    child.classList.add('step79-calendar-box');
                    child.style.setProperty('text-align', 'center', 'important');
                    child.style.setProperty('justify-content', 'center', 'important');
                    child.style.setProperty('align-items', 'center', 'important');
                    child.style.setProperty('padding-left', '0', 'important');
                    child.style.setProperty('padding-right', '0', 'important');

                    const all = [child, ...Array.from(child.querySelectorAll('*'))];
                    for (const el of all) {
                        if (el !== child && !el.children.length) {
                            const txt = (el.textContent || '').trim();
                            if (/^달\s*력$/.test(txt) || txt === '달' || txt === '력') {
                                el.textContent = '달력';
                                el.style.setProperty('display', 'inline-block', 'important');
                                el.style.setProperty('width', '100%', 'important');
                                el.style.setProperty('text-align', 'center', 'important');
                                el.style.setProperty('white-space', 'nowrap', 'important');
                            }
                        }
                    }

                    for (const svg of Array.from(child.querySelectorAll('svg'))) {
                        svg.classList.add('step79-hide-chevron');
                    }
                    for (const el of Array.from(child.querySelectorAll('span,div'))) {
                        const txt = (el.textContent || '').trim();
                        if (/^[▾∨⌄˅﹀vV]$/.test(txt)) {
                            el.classList.add('step79-hide-chevron');
                        }
                    }
                }
            }

            function reorderToolbar(doc) {
                const toolbar = findToolbar(doc);
                if (!toolbar) return;

                toolbar.style.setProperty('display', 'flex', 'important');
                toolbar.style.setProperty('align-items', 'center', 'important');

                const children = Array.from(toolbar.children || []);
                if (!children.length) return;

                let todayIdx = -1;
                children.forEach((child, idx) => {
                    if (classifyChild(child) === 'today') todayIdx = idx;
                });

                fixCalendar(toolbar);

                let afterTodayArrowUsed = false;
                let beforeTodayArrowUsed = false;
                children.forEach((child, idx) => {
                    const kind = classifyChild(child);
                    let order = 999;
                    if (kind === 'today') order = 20;
                    else if (kind === 'calendar') order = 40;
                    else if (kind === 'memo') order = 60;
                    else if (kind === 'search') order = 70;
                    else if (kind === '89') order = 80;
                    else if (kind === 'settings') order = 100;
                    else if (kind === 'sync') order = 90;
                    else if (kind === 'chevron') {
                        child.style.setProperty('display', 'none', 'important');
                        return;
                    } else if (kind === 'icon') {
                        if (todayIdx >= 0 && idx < todayIdx && !beforeTodayArrowUsed) {
                            order = 10;
                            beforeTodayArrowUsed = true;
                        } else if (todayIdx >= 0 && idx > todayIdx && !afterTodayArrowUsed) {
                            order = 30;
                            afterTodayArrowUsed = true;
                        } else {
                            // 남는 아이콘은 동기화로 간주
                            order = 90;
                        }
                    } else {
                        order = 200 + idx;
                    }
                    child.style.setProperty('order', String(order), 'important');
                });
            }

            function run() {
                const doc = rootDoc();
                injectStyle(doc);
                patchClock(doc);
                reorderToolbar(doc);
            }

            run();
            setTimeout(run, 150);
            setTimeout(run, 500);
            setTimeout(run, 1200);
            setTimeout(run, 2400);
        })();
        </script>
        """,
        height=1,
        width=1,
    )
except Exception:
    pass
# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_END]
'''

REMOVE_MARKERS = [
    ("# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_START]", "# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_END]"),
]


def backup_current():
    backup = APP.with_name(f"{APP.stem}_before_step79_topbar_fix_{STAMP}{APP.suffix}")
    backup.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {backup}")


def compiles(text: str, name: str):
    try:
        compile(text, name, "exec")
        return True, None
    except Exception as e:
        return False, e


def remove_block_once(text: str, start_marker: str, end_marker: str):
    start = text.find(start_marker)
    if start == -1:
        return text, False
    end = text.find(end_marker, start)
    if end == -1:
        return text, False
    end_line = text.find("\n", end)
    end_line = len(text) if end_line == -1 else end_line + 1
    return text[:start] + text[end_line:], True


def remove_old_step79(text: str):
    removed = 0
    for start, end in REMOVE_MARKERS:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    return text, removed


def main():
    print("====================================================")
    print("Step79 web topbar clock/calendar/order fix")
    print("====================================================")
    print(f"[ROOT] {ROOT}")
    print()

    if not APP.exists():
        print(f"[오류] mobile/app.py가 없습니다: {APP}")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    backup_current()
    text = APP.read_text(encoding="utf-8", errors="replace")

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] 현재 mobile/app.py가 이미 문법 오류 상태입니다.")
        print(err)
        print("먼저 현재 문법 오류를 해결한 뒤 다시 실행해주세요.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    text, removed = remove_old_step79(text)
    text = text.rstrip() + "\n\n" + PATCH_BLOCK.strip("\n") + "\n"

    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] 패치 후 mobile/app.py 문법 확인 실패")
        print(err)
        print("패치를 저장하지 않습니다.")
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)

    APP.write_text(text, encoding="utf-8")
    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step79 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step79 블록 제거: {removed}")
    print("- 현재시각을 'HH:MM 상태' 형태로 상단에 표시")
    print("- 달력 버튼 가운데 정렬")
    print("- 달력 꺾쇠 숨김")
    print("- 동기화 아이콘을 8·9와 설정 사이로 재배치")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 상단 오른쪽에 'HH:MM 수업 전/방과 후/교시'로 표시되는지")
    print("2. 달력 글자가 가운데 정렬되는지")
    print("3. 달력 꺾쇠가 사라지는지")
    print("4. 새로고침 아이콘이 8·9와 설정 사이로 이동했는지")
    input("엔터를 누르면 종료합니다.")


if __name__ == "__main__":
    main()

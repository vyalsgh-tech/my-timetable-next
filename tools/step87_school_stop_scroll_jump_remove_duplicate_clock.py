# tools/step87_school_stop_scroll_jump_remove_duplicate_clock.py
from pathlib import Path
from datetime import datetime
import re
import sys

ROOT = Path(r"Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next")
APP = ROOT / "mobile" / "app.py"
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

DOM_BLOCK = '\n# [STEP87_WEB_NO_SCROLL_JUMP_DOM_START]\ntry:\n    import streamlit.components.v1 as components\n    components.html(r"""\n<script>\n(function(){\n  const SID=\'s87-style\', CLOCK=\'step87-clock-fixed\';\n  const P={\n    light:{tw:\'#dbe8f7\',th1:\'#eaf3ff\',th2:\'#d7e6f8\',td1:\'#fff\',td2:\'#fafcff\',line:\'#1f2937\',text:\'#0f172a\',calbg:\'#f5f0ff\',calt:\'#5b21b6\',calbd:\'#ddd6fe\',memobg:\'#2563eb\',memot:\'#fff\',searchbg:\'#fff4dd\',searcht:\'#8a4b00\',searchbd:\'#f2cf96\',ebg:\'#eef2ff\',et:\'#1e40af\',ebd:\'#c7d2fe\',abg:\'#dbeafe\',abd:\'#2563eb\',at:\'#0f172a\',sbg:\'#fff7ed\',sbd:\'#f97316\'},\n    dark:{tw:\'#253145\',th1:\'#334155\',th2:\'#243041\',td1:\'#111827\',td2:\'#172033\',line:\'#cbd5e1\',text:\'#f8fafc\',calbg:\'#ede9fe\',calt:\'#4c1d95\',calbd:\'#c4b5fd\',memobg:\'#e11d48\',memot:\'#fff\',searchbg:\'#f97316\',searcht:\'#fff\',searchbd:\'#ea580c\',ebg:\'#dbeafe\',et:\'#1e3a8a\',ebd:\'#93c5fd\',abg:\'#1e3a8a\',abd:\'#60a5fa\',at:\'#f8fafc\',sbg:\'#7c2d12\',sbd:\'#fdba74\'},\n    green:{tw:\'#cfe7dc\',th1:\'#dcfce7\',th2:\'#bbf7d0\',td1:\'#fff\',td2:\'#f0fdf4\',line:\'#14532d\',text:\'#052e16\',calbg:\'#f5f3ff\',calt:\'#5b21b6\',calbd:\'#ddd6fe\',memobg:\'#ea580c\',memot:\'#fff\',searchbg:\'#f97316\',searcht:\'#fff\',searchbd:\'#ea580c\',ebg:\'#d9f99d\',et:\'#365314\',ebd:\'#a3e635\',abg:\'#bbf7d0\',abd:\'#16a34a\',at:\'#052e16\',sbg:\'#fef3c7\',sbd:\'#d97706\'},\n    orange:{tw:\'#fde7c8\',th1:\'#ffedd5\',th2:\'#fed7aa\',td1:\'#fffaf5\',td2:\'#fff7ed\',line:\'#7c2d12\',text:\'#431407\',calbg:\'#f5f3ff\',calt:\'#5b21b6\',calbd:\'#ddd6fe\',memobg:\'#c2410c\',memot:\'#fff\',searchbg:\'#ea580c\',searcht:\'#fff\',searchbd:\'#c2410c\',ebg:\'#ffedd5\',et:\'#7c2d12\',ebd:\'#fdba74\',abg:\'#fed7aa\',abd:\'#ea580c\',at:\'#431407\',sbg:\'#fef3c7\',sbd:\'#d97706\'},\n    pink:{tw:\'#ffe1ec\',th1:\'#ffe6ef\',th2:\'#ffd3e2\',td1:\'#fffefe\',td2:\'#fff7fb\',line:\'#7f1d43\',text:\'#4a1d2f\',calbg:\'#fff1f7\',calt:\'#be185d\',calbd:\'#f9a8d4\',memobg:\'#ec4899\',memot:\'#fff\',searchbg:\'#fff1e6\',searcht:\'#9a3412\',searchbd:\'#fdba74\',ebg:\'#fdf2f8\',et:\'#9d174d\',ebd:\'#fbcfe8\',abg:\'#fbcfe8\',abd:\'#ec4899\',at:\'#4a1d2f\',sbg:\'#fff1e6\',sbd:\'#fb923c\'},\n    blue:{tw:\'#dbeafe\',th1:\'#e0f2fe\',th2:\'#bae6fd\',td1:\'#fff\',td2:\'#f8fbff\',line:\'#1e3a8a\',text:\'#0f172a\',calbg:\'#f5f3ff\',calt:\'#5b21b6\',calbd:\'#ddd6fe\',memobg:\'#2563eb\',memot:\'#fff\',searchbg:\'#fff7ed\',searcht:\'#9a3412\',searchbd:\'#fed7aa\',ebg:\'#e0f2fe\',et:\'#075985\',ebd:\'#7dd3fc\',abg:\'#bfdbfe\',abd:\'#2563eb\',at:\'#0f172a\',sbg:\'#fef3c7\',sbd:\'#d97706\'}\n  };\n  function doc(){try{return window.parent.document}catch(e){return document}}\n  function vis(e){if(!e)return false;let s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=\'none\'&&s.visibility!=\'hidden\'&&r.width>1&&r.height>1}\n  function txt(e){return ((e&&(e.innerText||e.textContent))||\'\').replace(/\\s+/g,\' \').trim()}\n  function rgb(v){let m=(v||\'\').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/i);return m?{r:+m[1],g:+m[2],b:+m[3]}:null}\n  function lum(c){return c?0.299*c.r+0.587*c.g+0.114*c.b:255}\n  function bar(d){return Array.from(d.querySelectorAll(\'div[data-testid="stHorizontalBlock"]\')).filter(vis).find(b=>{let t=txt(b);return t.includes(\'오늘\')&&t.includes(\'달력\')&&t.includes(\'메모\')})}\n  function tbl(d){return Array.from(d.querySelectorAll(\'table\')).find(t=>{let x=txt(t);return x.includes(\'교시\')&&x.includes(\'학사일정\')&&(x.includes(\'월\')||x.includes(\'화\'))})}\n  function pal(d){let body=d.body?d.body.innerText||\'\':\'\'; if(body.includes(\'러블리 핑크\'))return \'pink\'; let b=bar(d),c=rgb(b?getComputedStyle(b).backgroundColor:getComputedStyle(d.body).backgroundColor); if(c){if(lum(c)<95)return\'dark\'; if(c.g>c.r+20&&c.g>=c.b)return\'green\'; if(c.r>210&&c.g>145&&c.b<125)return\'orange\'; if(c.b>c.r+10&&c.b>c.g-5)return\'blue\'; if(c.r>230&&c.b>210&&c.g<225)return\'pink\'} let l=body.toLowerCase(); if(l.includes(\'dark\')||body.includes(\'다크\')||body.includes(\'블랙\')||body.includes(\'야간\'))return\'dark\'; if(body.includes(\'그린\')||body.includes(\'초록\')||body.includes(\'숲\'))return\'green\'; if(body.includes(\'오렌지\')||body.includes(\'주황\'))return\'orange\'; if(body.includes(\'블루\')||body.includes(\'파랑\')||body.includes(\'윈도우\'))return\'blue\'; return\'light\'}\n  function style(d){if(d.getElementById(SID))return;let s=d.createElement(\'style\');s.id=SID;s.textContent=`\nhtml{overflow-anchor:none!important}#${CLOCK}{position:fixed!important;right:max(10px,calc((100vw - min(450px,100vw))/2 + 8px))!important;top:8px!important;z-index:999999!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:5px 12px!important;border-radius:999px!important;border:1px solid rgba(96,165,250,.36)!important;background:linear-gradient(180deg,rgba(250,252,255,.98),rgba(232,240,255,.96))!important;color:#1d4ed8!important;box-shadow:0 2px 7px rgba(59,130,246,.12)!important;white-space:nowrap!important;font-size:14px!important;line-height:1.15!important;font-weight:900!important;pointer-events:none!important}\nbody.step87-theme table.mobile-table{color:var(--s87-text)!important;border-color:var(--s87-line)!important;table-layout:fixed!important}body.step87-theme table.mobile-table th{background-image:linear-gradient(180deg,var(--s87-th1),var(--s87-th2))!important;color:var(--s87-text)!important;border-color:var(--s87-line)!important}body.step87-theme table.mobile-table td{background-image:linear-gradient(180deg,var(--s87-td1),var(--s87-td2))!important;color:var(--s87-text)!important;border-color:var(--s87-line)!important;height:58px!important;min-height:58px!important;vertical-align:middle!important;box-sizing:border-box!important;overflow:hidden!important}body.step87-theme div:has(> table.mobile-table){background:var(--s87-tw)!important}\n.s87-text-fit{white-space:normal!important;word-break:keep-all!important;overflow-wrap:anywhere!important;line-height:1.15!important;letter-spacing:-.25px!important}.s87-text-fit.long{font-size:10px!important;line-height:1.12!important;letter-spacing:-.45px!important}.s87-text-fit.very-long{font-size:8.5px!important;line-height:1.08!important;letter-spacing:-.65px!important}.s87-query-fit{font-size:8.5px!important;line-height:1.08!important;letter-spacing:-.65px!important;white-space:normal!important;word-break:keep-all!important;overflow-wrap:anywhere!important;overflow:hidden!important;text-align:center!important;vertical-align:middle!important;padding:1px 2px!important}.s87-query-fit.extreme{font-size:7.5px!important;letter-spacing:-.8px!important;line-height:1.03!important}\n.s87-btn-calendar,.s87-btn-memo,.s87-btn-search,.s87-btn-89{box-sizing:border-box!important;min-height:40px!important;height:40px!important;border-radius:7px!important;font-weight:800!important;text-align:center!important;white-space:nowrap!important;word-break:keep-all!important;display:flex!important;align-items:center!important;justify-content:center!important}.s87-btn-calendar *,.s87-btn-memo *,.s87-btn-search *,.s87-btn-89 *{color:inherit!important;-webkit-text-fill-color:currentColor!important;white-space:nowrap!important;text-align:center!important}.s87-btn-calendar{width:58px!important;min-width:58px!important;max-width:58px!important;flex:0 0 58px!important;background:var(--s87-calbg)!important;border:1px solid var(--s87-calbd)!important;color:var(--s87-calt)!important;padding:0!important;position:relative!important;overflow:hidden!important}.s87-btn-memo{background:var(--s87-memobg)!important;border:1px solid var(--s87-memobg)!important;color:var(--s87-memot)!important}.s87-btn-search{background:var(--s87-searchbg)!important;border:1px solid var(--s87-searchbd)!important;color:var(--s87-searcht)!important}.s87-btn-89{background:var(--s87-ebg)!important;border:1px solid var(--s87-ebd)!important;color:var(--s87-et)!important}\n.s87-calendar-shell{width:58px!important;min-width:58px!important;max-width:58px!important;flex:0 0 58px!important;position:relative!important;display:flex!important;align-items:center!important;justify-content:center!important;padding:0!important;box-sizing:border-box!important}.s87-calendar-shell>*{width:58px!important;min-width:58px!important;max-width:58px!important}.s87-calendar-shell [data-baseweb="select"],.s87-calendar-shell [role="button"],.s87-calendar-shell button{width:58px!important;min-width:58px!important;max-width:58px!important;display:flex!important;align-items:center!important;justify-content:center!important;grid-template-columns:1fr!important;padding-left:0!important;padding-right:0!important;color:transparent!important;-webkit-text-fill-color:transparent!important}.s87-calendar-shell [data-baseweb="select"] *,.s87-calendar-shell [role="button"] *,.s87-calendar-shell button *{color:transparent!important;-webkit-text-fill-color:transparent!important}.s87-calendar-shell svg,.s87-calendar-shell [aria-hidden="true"],.s87-remove{display:none!important;width:0!important;min-width:0!important;max-width:0!important;flex:0 0 0!important;margin:0!important;padding:0!important}.s87-calendar-overlay{position:absolute!important;left:50%!important;top:50%!important;transform:translate(-50%,-50%)!important;display:flex!important;align-items:center!important;justify-content:center!important;width:max-content!important;pointer-events:none!important;color:var(--s87-calt)!important;-webkit-text-fill-color:var(--s87-calt)!important;font-size:14px!important;font-weight:800!important;line-height:1!important;text-align:center!important;z-index:3!important}\ntable.mobile-table .s87-current-col{box-shadow:inset 0 3px 0 var(--s87-abd)!important}table.mobile-table .s87-current-rowhead,table.mobile-table .s87-current-cell{background-image:linear-gradient(180deg,var(--s87-abg),var(--s87-abg))!important;color:var(--s87-at)!important;box-shadow:inset 0 0 0 2px var(--s87-abd)!important}table.mobile-table .s87-soon-cell,table.mobile-table .s87-soon-rowhead{background-image:linear-gradient(180deg,var(--s87-sbg),var(--s87-sbg))!important;box-shadow:inset 0 0 0 2px var(--s87-sbd)!important}table.mobile-table .s87-current-rowhead,table.mobile-table .s87-soon-rowhead{position:relative!important}.s87-period-badge{position:absolute!important;left:50%!important;bottom:2px!important;transform:translateX(-50%)!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;padding:1px 5px!important;border-radius:999px!important;font-size:9px!important;font-weight:900!important;background:var(--s87-abd)!important;color:#fff!important;line-height:1.1!important;white-space:nowrap!important;pointer-events:none!important}.s87-period-badge.soon{background:var(--s87-sbd)!important}`;d.head.appendChild(s)}\n  function vars(d){let p=P[pal(d)]||P.light;d.body.classList.add(\'step87-theme\');for(let [k,v] of Object.entries(p))d.body.style.setProperty(\'--s87-\'+k,v)}\n  function hideOldClocks(d){[\'step80-clock-fixed\',\'step79-clock-fixed\',\'step78-clock-fixed\',\'step77-clock-fixed\',\'step86-clock-fixed\',\'step85-clock-fixed\',\'step84-clock-fixed\'].forEach(id=>{let e=d.getElementById(id);if(e)e.remove()});let states=new Set([\'수업 전\',\'방과 후\',\'쉬는시간\',\'1교시\',\'2교시\',\'3교시\',\'4교시\',\'점심\',\'5교시\',\'6교시\',\'7교시\',\'8교시\',\'9교시\']);Array.from(d.querySelectorAll(\'div,p,span\')).forEach(e=>{let t=(e.innerText||\'\').trim();if(!states.has(t))return;let r=e.getBoundingClientRect();if(r.top<100&&r.left>window.innerWidth*.45)e.style.setProperty(\'display\',\'none\',\'important\')})}\n  function now(){let n=new Date(),m=n.getHours()*60+n.getMinutes(),a=[[\'1교시\',\'08:00\',\'08:50\'],[\'2교시\',\'09:00\',\'09:50\'],[\'3교시\',\'10:00\',\'10:50\'],[\'4교시\',\'11:00\',\'11:50\'],[\'점심\',\'11:50\',\'12:40\'],[\'5교시\',\'12:40\',\'13:30\'],[\'6교시\',\'13:40\',\'14:30\'],[\'7교시\',\'14:40\',\'15:30\'],[\'8교시\',\'16:00\',\'16:50\'],[\'9교시\',\'17:00\',\'17:50\']];function tm(t){let p=t.split(\':\').map(Number);return p[0]*60+p[1]}let st=\'쉬는시간\';for(let p of a){if(tm(p[1])<=m&&m<tm(p[2])){st=p[0];break}}if(m<480)st=\'수업 전\';if(m>=1070)st=\'방과 후\';return String(n.getHours()).padStart(2,\'0\')+\':\'+String(n.getMinutes()).padStart(2,\'0\')+\' \'+st}\n  function clock(d){hideOldClocks(d);let c=d.getElementById(CLOCK);if(!c){c=d.createElement(\'div\');c.id=CLOCK;d.body.appendChild(c)}c.textContent=now()}\n  function cls(c){let t=txt(c);if(t.includes(\'달력\'))return\'calendar\';if(t.includes(\'메모\'))return\'memo\';if(t.includes(\'조회\'))return\'search\';if(t.includes(\'8·9\')||t.includes(\'8-9\')||t===\'89\'||t.includes(\'89\'))return\'89\';return\'\'}\n  function target(c){return c.querySelector(\'button,[role="button"],div[data-baseweb="select"]\')||c}\n  function cal(c,d){c.classList.add(\'s87-calendar-shell\');target(c).classList.add(\'s87-btn-calendar\');let rm=[];Array.from(c.querySelectorAll(\'svg\')).forEach(e=>rm.push(e));Array.from(c.querySelectorAll(\'span,div,p\')).forEach(e=>{if(/^[▾∨⌄˅﹀vV⌵⌄⌃⌝⌞⌟⌜›‹>]+$/.test((e.textContent||\'\').trim()))rm.push(e)});rm.forEach(e=>{try{e.remove()}catch(x){e.classList.add(\'s87-remove\')}});let o=c.querySelector(\'.s87-calendar-overlay\');if(!o){o=d.createElement(\'span\');o.className=\'s87-calendar-overlay\';c.appendChild(o)}o.textContent=\'달력\'}\n  function buttons(d){let b=bar(d);if(!b)return;Array.from(b.children||[]).forEach(c=>{let k=cls(c),bt=target(c);if(k===\'calendar\')cal(c,d);else if(k===\'memo\')bt.classList.add(\'s87-btn-memo\');else if(k===\'search\')bt.classList.add(\'s87-btn-search\');else if(k===\'89\')bt.classList.add(\'s87-btn-89\')})}\n  function memoColor(d){let re=/<span\\s+style=["\']\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*["\']>(.*?)<\\/span>/gis,w=d.createTreeWalker(d.body,NodeFilter.SHOW_TEXT),ns=[],n;while(n=w.nextNode()){let v=n.nodeValue||\'\';re.lastIndex=0;if(v.includes(\'<span\')&&re.test(v))ns.push(n)}ns.forEach(n=>{let text=n.nodeValue||\'\',f=d.createDocumentFragment(),last=0,m;re.lastIndex=0;while(m=re.exec(text)){if(m.index>last)f.appendChild(d.createTextNode(text.slice(last,m.index)));let s=d.createElement(\'span\');s.style.setProperty(m[1].toLowerCase(),m[2]);s.textContent=m[3];f.appendChild(s);last=re.lastIndex}if(last<text.length)f.appendChild(d.createTextNode(text.slice(last)));if(n.parentNode)n.parentNode.replaceChild(f,n)});let er=/&lt;span\\s+style=(?:&quot;|")\\s*(color|background-color)\\s*:\\s*(#[0-9a-fA-F]{3,6})\\s*;?\\s*(?:&quot;|")&gt;([\\s\\S]*?)&lt;\\/span&gt;/gi;Array.from(d.querySelectorAll(\'div,p,span\')).forEach(e=>{if(e.innerHTML&&e.innerHTML.includes(\'&lt;span\'))e.innerHTML=e.innerHTML.replace(er,(_,p,c,x)=>\'<span style="\'+p+\':\'+c+\'">\'+x+\'</span>\')})}\n  function pm(t){let m=String(t||\'\').match(/(\\d{1,2}):(\\d{2})/);return m?parseInt(m[1])*60+parseInt(m[2]):null}\n  function range(row){let f=row.children&&row.children[0];if(!f)return null;let ts=(f.innerText||\'\').match(/\\d{1,2}:\\d{2}/g);return ts&&ts.length>=2?{s:pm(ts[0]),e:pm(ts[1])}:null}\n  function col(){let d=new Date().getDay();return d>=1&&d<=5?d:-1}\n  function clean(t){let cs=[\'s84-current-col\',\'s84-current-rowhead\',\'s84-current-cell\',\'s84-soon-cell\',\'s84-soon-rowhead\',\'s85-current-col\',\'s85-current-rowhead\',\'s85-current-cell\',\'s85-soon-cell\',\'s85-soon-rowhead\',\'s86-current-col\',\'s86-current-rowhead\',\'s86-current-cell\',\'s86-soon-cell\',\'s86-soon-rowhead\',\'s87-current-col\',\'s87-current-rowhead\',\'s87-current-cell\',\'s87-soon-cell\',\'s87-soon-rowhead\'];Array.from(t.querySelectorAll(\'.\'+cs.join(\',.\'))).forEach(e=>e.classList.remove(...cs));Array.from(t.querySelectorAll(\'.s84-period-badge,.s85-period-badge,.s86-period-badge,.s87-period-badge\')).forEach(e=>e.remove());Array.from(t.querySelectorAll(\'br[data-s84-period-br],br[data-s85-period-br],br[data-s86-period-br],br[data-s87-period-br]\')).forEach(e=>e.remove())}\n  function highlight(d){let t=tbl(d);if(!t)return;clean(t);let c=col(),rows=Array.from(t.querySelectorAll(\'tr\'));if(c<1||!rows.length)return;let n=new Date(),mi=n.getHours()*60+n.getMinutes(),tr=null,mode=\'current\';for(let r of rows){let g=range(r);if(g&&g.s<=mi&&mi<g.e){tr=r;break}}if(!tr){let near=null;for(let r of rows){let g=range(r);if(!g)continue;let df=g.s-mi;if(df>0&&df<=15&&(!near||df<near.df))near={r,df}}if(near){tr=near.r;mode=\'soon\'}}if(rows[0]&&rows[0].children[c])rows[0].children[c].classList.add(\'s87-current-col\');if(!tr)return;let rh=tr.children[0],ce=tr.children[c];if(mode===\'current\'){if(rh)rh.classList.add(\'s87-current-rowhead\');if(ce)ce.classList.add(\'s87-current-cell\')}else{if(rh)rh.classList.add(\'s87-soon-rowhead\');if(ce)ce.classList.add(\'s87-soon-cell\')}if(rh&&!rh.querySelector(\'.s87-period-badge\')){let b=d.createElement(\'span\');b.className=\'s87-period-badge\'+(mode===\'soon\'?\' soon\':\'\');b.textContent=mode===\'soon\'?\'시작 전\':\'진행 중\';rh.appendChild(b)}}\n  function fit(d){let t=tbl(d);if(!t)return;Array.from(t.querySelectorAll(\'tr\')).forEach(r=>{let cells=Array.from(r.children||[]),ft=cells.length?txt(cells[0]):\'\',head=ft===\'교시\'||(ft.includes(\'교시\')&&!ft.match(/\\d{1,2}:\\d{2}/)),q=ft.includes(\'조회\');for(let i=1;i<cells.length;i++){let cell=cells[i],x=txt(cell);if(!x)continue;if(q){cell.classList.add(\'s87-query-fit\');if(x.length>34)cell.classList.add(\'extreme\')}else if(!head){if(x.length>18)cell.classList.add(\'s87-text-fit\',\'long\');if(x.length>30)cell.classList.add(\'s87-text-fit\',\'very-long\')}}})}\n  function stable(){let d=doc(),sc=d.scrollingElement||d.documentElement||d.body,top=sc?sc.scrollTop:0,left=sc?sc.scrollLeft:0;style(d);vars(d);clock(d);buttons(d);memoColor(d);fit(d);highlight(d);requestAnimationFrame(()=>{if(sc&&Math.abs(sc.scrollTop-top)>2){sc.scrollTop=top;sc.scrollLeft=left}})}\n  function clockOnly(){clock(doc())}\n  stable();setTimeout(stable,200);setTimeout(stable,900);setTimeout(stable,1800);setInterval(clockOnly,60000);\n})();\n</script>\n""", height=1, width=1)\nexcept Exception:\n    pass\n# [STEP87_WEB_NO_SCROLL_JUMP_DOM_END]\n'
SSL_BLOCK = '\n# [STEP87_SUPABASE_SSL_FALLBACK_START]\ntry:\n    import requests as _s87_requests\n    try:\n        import urllib3 as _s87_urllib3\n        _s87_urllib3.disable_warnings(_s87_urllib3.exceptions.InsecureRequestWarning)\n    except Exception:\n        pass\n    if not getattr(_s87_requests.sessions.Session.request, "_s87_ssl_fallback", False):\n        _s87_original_request = _s87_requests.sessions.Session.request\n        def _s87_request_with_ssl_fallback(self, method, url, **kwargs):\n            try:\n                return _s87_original_request(self, method, url, **kwargs)\n            except _s87_requests.exceptions.SSLError:\n                if "supabase.co" in str(url):\n                    kwargs["verify"] = False\n                    return _s87_original_request(self, method, url, **kwargs)\n                raise\n        _s87_request_with_ssl_fallback._s87_ssl_fallback = True\n        _s87_requests.sessions.Session.request = _s87_request_with_ssl_fallback\nexcept Exception:\n    pass\n# [STEP87_SUPABASE_SSL_FALLBACK_END]\n'
LOVELY_PINK_THEME = '\n    "러블리 핑크": {\n        "bg": "#fff5f8",\n        "card": "#ffffff",\n        "text": "#4a1d2f",\n        "muted": "#9f647a",\n        "primary": "#ec4899",\n        "primary_dark": "#db2777",\n        "accent": "#f9a8d4",\n        "header_bg": "#ffe6ef",\n        "header_bg2": "#ffd3e2",\n        "cell_bg": "#fffafe",\n        "cell_bg2": "#fff7fb",\n        "border": "#f3bfd2",\n        "shadow": "rgba(236, 72, 153, 0.14)",\n    },\n'

REMOVE_MARKERS = [
    ("# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_START]", "# [STEP78_WEB_TOP_CLOCK_CALENDAR_FIX_END]"),
    ("# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_START]", "# [STEP79_WEB_TOPBAR_CLOCK_CALENDAR_ORDER_FIX_END]"),
    ("# [STEP80_WEB_TOPBAR_AND_THEME_DOM_START]", "# [STEP80_WEB_TOPBAR_AND_THEME_DOM_END]"),
    ("# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_START]", "# [STEP81_WEB_CALENDAR_THEME_REFINEMENT_END]"),
    ("# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_START]", "# [STEP82_WEB_THEME_BUTTON_CALENDAR_REFINEMENT_END]"),
    ("# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_START]", "# [STEP83_SAFE_THEME_AND_MEMO_COLOR_DOM_END]"),
    ("# [STEP84_WEB_SAFE_DOM_REFINEMENT_START]", "# [STEP84_WEB_SAFE_DOM_REFINEMENT_END]"),
    ("# [STEP85_WEB_STABLE_DOM_REFINEMENT_START]", "# [STEP85_WEB_STABLE_DOM_REFINEMENT_END]"),
    ("# [STEP86_WEB_SCROLL_ROW_STABLE_DOM_START]", "# [STEP86_WEB_SCROLL_ROW_STABLE_DOM_END]"),
    ("# [STEP87_WEB_NO_SCROLL_JUMP_DOM_START]", "# [STEP87_WEB_NO_SCROLL_JUMP_DOM_END]"),
]
SSL_REMOVE_MARKERS = [
    ("# [STEP84_SUPABASE_SSL_FALLBACK_START]", "# [STEP84_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP85_SUPABASE_SSL_FALLBACK_START]", "# [STEP85_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP86_SUPABASE_SSL_FALLBACK_START]", "# [STEP86_SUPABASE_SSL_FALLBACK_END]"),
    ("# [STEP87_SUPABASE_SSL_FALLBACK_START]", "# [STEP87_SUPABASE_SSL_FALLBACK_END]"),
]

def backup_current():
    b = APP.with_name(f"{APP.stem}_before_step87_stop_scroll_jump_{STAMP}{APP.suffix}")
    b.write_text(APP.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    print(f"[백업] {b}")

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

def remove_blocks(text: str, markers):
    removed = 0
    for start, end in markers:
        while start in text and end in text:
            text, did = remove_block_once(text, start, end)
            if not did:
                break
            removed += 1
    return text, removed

def insert_ssl_fallback(text: str):
    lines = text.splitlines()
    last_import = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            last_import = i
        elif last_import >= 0 and s and not s.startswith("#"):
            break
    insert_at = last_import + 1 if last_import >= 0 else 0
    lines[insert_at:insert_at] = SSL_BLOCK.strip("\n").splitlines()
    return "\n".join(lines) + "\n", f"inserted_at_line_{insert_at+1}"

def add_lovely_pink_to_theme_dict(text: str):
    if '"러블리 핑크"' in text or "'러블리 핑크'" in text:
        return text, "already_exists"
    m = re.search(r"(^\s*(?:THEMES|themes|theme_map|THEME_MAP|theme_colors|THEME_COLORS)\s*=\s*\{)", text, flags=re.M)
    if not m:
        return text, "theme_dict_not_found"
    start = m.end() - 1
    depth = 0
    end = None
    in_str = None
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"'):
            in_str = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        return text, "theme_dict_end_not_found"
    return text[:end] + LOVELY_PINK_THEME.rstrip() + "\n" + text[end:], "theme_dict_added"

def add_lovely_pink_to_options(text: str):
    if "러블리 핑크" in text:
        return text, 0
    changed = 0
    for pat in [r"(theme_options\s*=\s*\[[^\]]*)\]", r"(themes_list\s*=\s*\[[^\]]*)\]", r"(theme_names\s*=\s*\[[^\]]*)\]"]:
        def repl(m):
            nonlocal changed
            changed += 1
            return m.group(1).rstrip() + ', "러블리 핑크"]'
        text2, n = re.subn(pat, repl, text, count=1, flags=re.S)
        if n:
            return text2, changed
    pat = r"(st\.selectbox\([^\n]{0,200}(?:테마|theme)[\s\S]{0,500}?\[[^\]]*)\]"
    def repl2(m):
        nonlocal changed
        changed += 1
        return m.group(1).rstrip() + ', "러블리 핑크"]'
    text2, _ = re.subn(pat, repl2, text, count=1)
    return text2, changed

def main():
    print("====================================================")
    print("Step87 stop scroll jump + remove duplicate clock")
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
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)
    try:
        text, removed_dom = remove_blocks(text, REMOVE_MARKERS)
        text, removed_ssl = remove_blocks(text, SSL_REMOVE_MARKERS)
        text, ssl_status = insert_ssl_fallback(text)
        text, theme_dict_status = add_lovely_pink_to_theme_dict(text)
        text, option_changes = add_lovely_pink_to_options(text)
        text = text.rstrip() + "\n\n" + DOM_BLOCK.strip("\n") + "\n"
    except Exception as e:
        print("[오류] 패치 실패")
        print(e)
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)
    ok, err = compiles(text, str(APP))
    if not ok:
        print("[오류] 패치 후 mobile/app.py 문법 확인 실패")
        print(err)
        input("엔터를 누르면 종료합니다.")
        sys.exit(1)
    APP.write_text(text, encoding="utf-8")
    print("[확인] mobile/app.py 문법 OK")
    print("[완료] Step87 패치 저장")
    print()
    print("[변경 요약]")
    print(f"- 기존 Step78~87 DOM 블록 제거: {removed_dom}")
    print(f"- 기존 SSL fallback 블록 제거: {removed_ssl}")
    print(f"- Supabase SSL fallback 재삽입: {ssl_status}")
    print(f"- 러블리 핑크 테마 dict 처리: {theme_dict_status}")
    print(f"- 러블리 핑크 옵션 처리: {option_changes}")
    print("- 초 단위 전체 DOM 반복 보정 제거")
    print("- 시각 배지 1개만 유지")
    print("- 이후에는 시각 텍스트만 1분마다 갱신")
    print("- 스크롤 위치 보존")
    print()
    print("실행:")
    print("python -m streamlit run mobile\\app.py")
    print()
    print("확인할 것:")
    print("1. 아래로 스크롤해도 최상단으로 끌려가지 않는지")
    print("2. 설정 아이콘 위에서 커서가 화살표/손가락으로 반복 깜빡이지 않는지")
    print("3. 현재시각 배지가 1개만 보이는지")
    print("4. 조회 행과 현재교시 표시가 유지되는지")
    print("5. 달력 글자가 중앙에 오는지")
    input("엔터를 누르면 종료합니다.")

if __name__ == "__main__":
    main()

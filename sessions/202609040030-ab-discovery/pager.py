"""Does NEXT 50 move 50 rows, on a window that says 1-100?"""
import json, sys, time
sys.path.insert(0, r'C:\Users\vikra\OneDrive\Documents\GitHub\claude\familiars')
from clicker import Browser, PROBE_VISIBLE
BASE = 'http://127.0.0.1:8971/releases/%s-pipelinenews/index.html'
gen, port = sys.argv[1], int(sys.argv[2])
READ = ("({pager:(document.getElementById('projectWindowControls')||{}).textContent"
        ".replace(/\s+/g,' ').trim(),"
        " rows:document.querySelectorAll('#tbody tr').length,"
        " first:(document.querySelector('#tbody tr td')||{}).textContent,"
        " cap:(()=>{const t=document.querySelector('#tbody tr');"
        "return t?t.children[7].textContent.trim():null;})(),"
        " units:[...new Set([...document.querySelectorAll('#tbody tr')]"
        ".map(t=>(t.children[7].textContent.match(/[A-Za-z]+$/)||[''])[0]))]})")
b = Browser(port, mobile=False, headless=True)
out = {'gen': gen, 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
try:
    b.setup(); b.arm()
    for m in ('Browser.setDownloadBehavior','Page.setDownloadBehavior'):
        try: b.send(m, behavior='deny')
        except Exception: pass
    b.go(BASE % gen, settle=8.0)
    v = b.js(PROBE_VISIBLE)
    assert isinstance(v, dict) and v.get('hidden') is False, v
    b.js("document.querySelectorAll('#tech button')[1].click()")   # SOLAR
    time.sleep(1.3)
    out['page1'] = b.js(READ)
    b.js("[...document.querySelectorAll('#projectWindowControls button')]"
         ".filter(x=>/NEXT/i.test(x.textContent))[0].click()")
    time.sleep(1.3)
    out['page2'] = b.js(READ)
    # units across the whole spine, not just solar
    b.js("document.querySelectorAll('#tech button')[0].click()")   # ALL TECH
    time.sleep(1.3)
    out['alltech'] = b.js(READ)
    out['errs'] = b.js('(window.__errs||[]).slice(0,6)')
finally:
    b.close()
print(json.dumps(out, indent=1, ensure_ascii=False))

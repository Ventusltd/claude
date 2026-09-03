"""A short, targeted read of one release. Whatever the last round left open.

Round 2 raised three questions a summary could not answer: what exactly the
solar rows' capacity cell says next to the capacity the MAP link carries; what
pager controls exist beside "1-50 of 275"; and whether the export strip warns a
reader BEFORE the click that the cut on screen cannot be exported.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, r'C:\Users\vikra\OneDrive\Documents\GitHub\claude\familiars')
from clicker import Browser, PROBE_VISIBLE  # noqa: E402

BASE = 'http://127.0.0.1:8971/releases/%s-pipelinenews/index.html'

CAP_PAIRS = r"""(() => {
  return [...document.querySelectorAll('#tbody tr')].slice(0, 8).map(tr => {
    const c = [...tr.children].map(td => (td.textContent || '').replace(/\s+/g, ' ').trim());
    const a = [...tr.querySelectorAll('a')].filter(x => /\bMAP\b/i.test(x.textContent || ''))[0];
    const u = a ? new URL(a.getAttribute('href'), location.href) : null;
    return {name: c[0].slice(0, 30), cell_cap: c[7], cell_tech: c[5],
            link_cap: u ? u.searchParams.get('capacity_mw') : null,
            link_tech: u ? u.searchParams.get('technology') : null,
            link_zoom: u ? u.searchParams.get('zoom') : null,
            link_lat: u ? u.searchParams.get('latitude') : null};
  });
})()"""

PAGER = r"""(() => {
  const host = document.getElementById('projectWindowControls');
  if (!host) return null;
  return {text: (host.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 200),
          controls: [...host.querySelectorAll('button,select,a')].map(e => {
            const r = e.getBoundingClientRect();
            return (e.tagName === 'SELECT'
              ? 'SELECT[' + [...e.options].map(o => o.textContent.trim()).join(',') + ']'
              : (e.textContent || '').replace(/\s+/g, ' ').trim())
              + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)
              + (e.disabled ? ' disabled' : ''); })};
})()"""

STRIP = r"""(() => {
  const m = document.getElementById('exportMeta'), b = document.getElementById('exportInline');
  const rb = b ? b.getBoundingClientRect() : null;
  return {meta: m ? (m.textContent || '').replace(/\s+/g, ' ').trim() : null,
          declined_class: m ? m.classList.contains('is-declined') : null,
          declined_dataset: m ? (m.dataset.exportDeclinedColumns || null) : null,
          btn_text: b ? (b.textContent || '').trim() : null,
          btn_disabled: b ? !!b.disabled : null,
          btn_aria: b ? b.getAttribute('aria-disabled') : null,
          btn_size: rb ? Math.round(rb.width) + 'x' + Math.round(rb.height) : null};
})()"""

# the register's own stated floor, and what the cut on screen actually holds
FLOOR = r"""(() => {
  const caps = [...document.querySelectorAll('#tbody tr')]
    .map(tr => parseFloat(((tr.children[7] || {}).textContent || '').replace(/[^\d.]/g, '')))
    .filter(v => !isNaN(v));
  const body = (document.body.textContent || '').replace(/\s+/g, ' ');
  const claim = (body.match(/every qualifying[^.]{0,60}/) || [])[0] || null;
  const note = (document.getElementById('sizeNote') || {}).textContent || null;
  return {rows_read: caps.length, min: caps.length ? Math.min(...caps) : null,
          below_1mw: caps.filter(v => v < 1).length,
          zero: caps.filter(v => v === 0).length,
          stated_claim: claim, size_note: note ? note.replace(/\s+/g, ' ').trim() : null};
})()"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--gen', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--mobile', action='store_true')
    args = ap.parse_args()

    b = Browser(args.port, mobile=args.mobile, headless=True)
    res = {'generation': args.gen, 'mobile': args.mobile,
           'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    try:
        b.setup(); b.arm()
        for m in ('Browser.setDownloadBehavior', 'Page.setDownloadBehavior'):
            try:
                b.send(m, behavior='deny')
            except Exception:
                pass
        b.go(BASE % args.gen, settle=8.0)
        vis = b.js(PROBE_VISIBLE)
        if not isinstance(vis, dict) or vis.get('hidden') is not False:
            res['ABORT'] = 'document.hidden was not false'
            print(json.dumps(res)); return

        b.js("document.querySelectorAll('#tech button')[1].click()")   # SOLAR
        time.sleep(1.3)
        res['solar'] = {'cap_pairs': b.js(CAP_PAIRS), 'pager': b.js(PAGER),
                        'strip': b.js(STRIP), 'floor': b.js(FLOOR)}

        # GEOTHERMAL: the cut whose counter reads 0 MW / largest 0 MW
        res['geothermal_label'] = b.js(
            "(()=>{const s=document.getElementById('widerTechnology');"
            "if(!s)return null;const i=[...s.options].findIndex(o=>/GEOTHERMAL/i.test(o.textContent));"
            "if(i<0)return null;s.selectedIndex=i;"
            "s.dispatchEvent(new Event('change',{bubbles:true}));"
            "return s.options[i].textContent.trim();})()")
        time.sleep(1.5)
        res['geothermal'] = {'cap_pairs': b.js(CAP_PAIRS), 'pager': b.js(PAGER),
                             'strip': b.js(STRIP), 'floor': b.js(FLOOR),
                             'counter': b.js("(document.getElementById('resultsMeta')||{}).textContent")}
        res['shot'] = b.shot(os.path.join('shots', 'probe-%s-geothermal.png' % args.gen))
        res['errs'] = b.js('(window.__errs||[]).slice(0,8)')
        res['log'] = b.js('(window.__log||[]).slice(0,8)')
    finally:
        b.close()
    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=1)
    print('WROTE', args.out)


if __name__ == '__main__':
    main()

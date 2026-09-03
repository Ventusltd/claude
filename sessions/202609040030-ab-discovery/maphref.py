"""What does MAP hand the Atlas, and does it match the row it sits in?

The row for REPD 8795 reads "Landfill Gas" in the TECHNOLOGY column and its MAP
link carries `technology=biomass`. One of the two is what a reader will quote.
This walks every technology the product offers -- the five spine buttons and all
twenty wider-fleet options -- and for each one reports the row's own technology
text beside the technology the link would hand the Atlas.

It reads hrefs. It does not resolve them: a link's liveness cannot be asserted
from inside the page, and a string that describes liveness is not liveness.
"""

import argparse
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, r'C:\Users\vikra\OneDrive\Documents\GitHub\claude\familiars')
from clicker import Browser, PROBE_VISIBLE  # noqa: E402

BASE = 'http://127.0.0.1:8971/releases/%s-pipelinenews/index.html'

# the row's own technology text beside the link's technology parameter
PAIRS = r"""(() => {
  const rows = [...document.querySelectorAll('#tbody tr')];
  const out = [];
  for (const tr of rows) {
    const cells = [...tr.children].map(td => (td.textContent || '').replace(/\s+/g, ' ').trim());
    const a = [...tr.querySelectorAll('a')].filter(x => /\bMAP\b/i.test(x.textContent || ''))[0];
    let param = null, ref = null, cap = null;
    if (a) {
      const u = new URL(a.getAttribute('href'), location.href);
      param = u.searchParams.get('technology');
      ref = u.searchParams.get('repd_ref');
      cap = u.searchParams.get('capacity_mw');
    }
    out.push({shown: cells[5] || null, link: param, ref: ref || cells[8] || null,
              cap_cell: cells[7] || null, cap_link: cap, has_link: !!a});
  }
  return out;
})()"""

PAGINATION = r"""(() => {
  const hits = [];
  for (const e of document.querySelectorAll('#projectWindowControls *, .pager, .pagination, [class*=page]')) {
    const t = (e.textContent || '').replace(/\s+/g, ' ').trim();
    if (/\bof\b/.test(t) && t.length < 60 && !e.querySelector('*')) hits.push(t);
  }
  return [...new Set(hits)].slice(0, 6);
})()"""


def sample(b, label):
    pairs = b.js(PAIRS)
    if not isinstance(pairs, list):
        return {'label': label, 'error': str(pairs)[:120]}
    mism = [p for p in pairs if p['has_link'] and p['shown'] and p['link']
            and p['shown'].lower().replace(' ', '_') != p['link'].lower()]
    return {
        'label': label,
        'rows': len(pairs),
        'with_link': sum(1 for p in pairs if p['has_link']),
        'mismatched': len(mism),
        'shown_vs_link': [k + ' -> ' + v for k, v in
                          Counter((p['shown'], p['link']) for p in pairs
                                  if p['has_link']).keys()],
        'cap_mismatch': sum(1 for p in pairs if p['has_link'] and p['cap_link']
                            and p['cap_cell']
                            and p['cap_cell'].replace(' MW', '').replace(',', '')
                            != p['cap_link']),
        'example': mism[0] if mism else None,
        'pagination': b.js(PAGINATION),
        'counter': b.js("(document.getElementById('resultsMeta')||{}).textContent"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--gen', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    b = Browser(args.port, mobile=False, headless=True)
    res = {'generation': args.gen,
           'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'cuts': []}
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

        names = b.js("[...document.querySelectorAll('#tech button')]"
                     ".map(b=>b.textContent.trim())")
        for i, n in enumerate(names or []):
            b.js("document.querySelectorAll('#tech button')[%d].click()" % i)
            time.sleep(1.1)
            res['cuts'].append(sample(b, 'SPINE ' + n))

        n_opts = b.js("(document.getElementById('widerTechnology')||{options:[]})"
                      ".options.length")
        for i in range(1, int(n_opts or 0)):
            label = b.js(
                "(()=>{const s=document.getElementById('widerTechnology');"
                "s.selectedIndex=%d;s.dispatchEvent(new Event('change',{bubbles:true}));"
                "return s.options[%d].textContent.trim();})()" % (i, i))
            time.sleep(1.1)
            res['cuts'].append(sample(b, 'WIDER ' + str(label)))
        res['errs'] = b.js('(window.__errs||[]).slice(0,8)')
    finally:
        b.close()

    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=1)
    print('WROTE', args.out, len(res['cuts']), 'cuts')


if __name__ == '__main__':
    main()

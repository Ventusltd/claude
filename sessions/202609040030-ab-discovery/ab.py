"""ab - drive two Pipeline News releases through the SAME reading and diff them.

Lane A is an instrument, not a shipper. This reuses familiars/clicker.py's Browser
verbatim - its own Chrome, its own port, its own profile, its arm() listeners
installed before the page's scripts run, and its refusal to measure a hidden tab.
What is added here is only the READING, and the fact that it is taken twice.

One Chrome per run, two navigations. Memory on this machine is the scarce
resource; two browsers where one will do is a cost with no evidence attached.

  python ab.py --port 9431 --a 202609020611 --b 202609032251
  python ab.py --port 9432 --a 202609031308 --b 202609032251 --mobile
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, r'C:\Users\vikra\OneDrive\Documents\GitHub\claude\familiars')
from clicker import Browser, PROBE_VISIBLE  # noqa: E402

BASE = 'http://127.0.0.1:8971/releases/%s-pipelinenews/index.html'

# ── the reading ─────────────────────────────────────────────────────────────
#
# Every anchor below was read off the shipped index.html before it was used.
# clicker's own journey_summary asks for `#results tbody tr`; no Pipeline News
# release has ever had an element with id "results" - the table body is
# `#tbody`. That selector has been returning 0 for every generation it was
# pointed at, and 0 is indistinguishable from an empty table.

READ = r"""(() => {
  const t = e => e ? (e.textContent || '').replace(/\s+/g, ' ').trim() : null;
  const el = id => document.getElementById(id);
  const arc = id => { const c = el(id);
    if (!c || !c.toDataURL) return null;
    const d = c.toDataURL();
    let h = 0; for (let i = 0; i < d.length; i++) h = (h * 31 + d.charCodeAt(i)) | 0;
    return c.width + 'x' + c.height + '#' + (h >>> 0).toString(16); };
  const meta = el('resultsMeta');
  const rows = [...document.querySelectorAll('#tbody tr')];
  const wider = el('widerTechnology');
  return {
    hidden: document.hidden,
    viewport: innerWidth + 'x' + innerHeight,
    doc_height: document.documentElement.scrollHeight,
    screens_tall: +(document.documentElement.scrollHeight / innerHeight).toFixed(2),

    counter: t(meta),
    counter_dataset: meta ? JSON.parse(JSON.stringify(meta.dataset)) : null,

    v1: t(el('v1')), v2: t(el('v2')), v3: t(el('v3')),
    g1: arc('g1'), g2: arc('g2'), g3: arc('g3'),

    exportMeta: t(el('exportMeta')),
    export_dataset: el('exportMeta') ? JSON.parse(JSON.stringify(el('exportMeta').dataset)) : null,
    export_btn: (() => { const b = el('exportInline'); if (!b) return null;
      const r = b.getBoundingClientRect();
      return {text: t(b), disabled: !!b.disabled, w: Math.round(r.width), h: Math.round(r.height)}; })(),

    row_count: rows.length,
    first_rows: rows.slice(0, 2).map(tr =>
      [...tr.children].map(td => (td.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 26))),
    columns: [...document.querySelectorAll('#tbody')].length
      ? [...document.querySelectorAll('table thead th')].map(th => t(th)) : [],

    /* The ACTIONS cell reads "MAP ↗", not "MAP". clicker's journey_maplink
       tests /^MAP$/i against the trimmed text, so the arrow makes it match
       nothing and the journey reports zero MAP cells on a table full of them.
       Anchored equality against display text is the anchor that drifts. */
    map_hrefs: [...document.querySelectorAll('#tbody a')]
      .filter(a => /\bMAP\b/i.test(a.textContent || ''))
      .slice(0, 3).map(a => a.getAttribute('href')),
    map_cells_total: [...document.querySelectorAll('#tbody a,#tbody button')]
      .filter(e => /\bMAP\b/i.test(e.textContent || '')).length,
    map_cell_rect: (() => { const a = [...document.querySelectorAll('#tbody a')]
        .filter(x => /\bMAP\b/i.test(x.textContent || ''))[0];
      if (!a) return null; const r = a.getBoundingClientRect();
      return {w: Math.round(r.width), h: Math.round(r.height),
              left_px: Math.round(r.left), target: a.getAttribute('target')}; })(),
    /* how far sideways the MAP column is from the site name */
    table_scroll: (() => { const w = document.querySelector('.tablewrap');
      if (!w) return null;
      return {client: w.clientWidth, scroll: w.scrollWidth,
              overflow_px: w.scrollWidth - w.clientWidth,
              flicks: +((w.scrollWidth - w.clientWidth) / 417).toFixed(1)}; })(),
    pagination: (() => { const b = document.body.textContent || '';
      const m = b.match(/[\d,]+\s*[–-]\s*[\d,]+\s+of\s+[\d,]+/g);
      return m ? m.slice(0, 3) : []; })(),
    gauge_canvas: ['g1', 'g2', 'g3'].map(id => { const c = el(id); if (!c) return null;
      const r = c.getBoundingClientRect();
      return id + ' attr=' + c.width + 'x' + c.height
        + ' css=' + Math.round(r.width) + 'x' + Math.round(r.height); }),
    no_map_cells: (document.getElementById('tbody')
      ? (document.getElementById('tbody').textContent.match(/NO MAP/g) || []).length : 0),

    tech_buttons: [...document.querySelectorAll('#tech button')].map(b => {
      const r = b.getBoundingClientRect();
      return t(b) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)
        + (b.getAttribute('aria-pressed') === 'true' ? ' *' : ''); }),
    wider_options: wider ? wider.options.length : 0,
    wider_selected: wider ? (wider.options[wider.selectedIndex] || {}).textContent : null,
    wider_rect: wider ? (r => Math.round(r.width) + 'x' + Math.round(r.height))(wider.getBoundingClientRect()) : null,
    widerFleetMeta: t(el('widerFleetMeta')),

    // how far a reader must travel before the product is on screen
    depth: (() => {
      const d = {};
      for (const [k, id] of [['technology_row', 'tech'], ['counter', 'resultsMeta'],
                             ['export', 'exportInline'], ['first_row', null]]) {
        const node = id ? el(id) : document.querySelector('#tbody tr');
        if (!node) { d[k] = null; continue; }
        const y = node.getBoundingClientRect().top + scrollY;
        d[k] = {px: Math.round(y), screens: +(y / innerHeight).toFixed(2)};
      }
      return d; })(),

    evidence: (() => { const e = globalThis.__PIPELINENEWS_FAST__;
      return e ? JSON.parse(JSON.stringify(e)) : null; })(),
    errs: (window.__errs || []).slice(0, 8),
    log: (window.__log || []).slice(0, 8)
  };
})()"""

# how much of the screen is product (the table) and how much is chrome,
# sampled at the first row so the question is asked where the answer lives
SHARE = r"""(() => {
  const W = innerWidth, H = innerHeight, cols = 30, rows = 60;
  const tb = document.getElementById('tbody');
  let product = 0, chrome = 0, none = 0; const owners = {};
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
    const e = document.elementFromPoint((i + 0.5) * W / cols, (j + 0.5) * H / rows);
    if (!e) { none++; continue; }
    if (tb && tb.contains(e)) { product++; continue; }
    chrome++;
    let n = e, name = '';
    while (n && n !== document.body) {
      if (n.id) { name = '#' + n.id; break; }
      if (n.className && typeof n.className === 'string' && n.className.trim()) {
        name = '.' + n.className.trim().split(/\s+/)[0]; break; }
      n = n.parentElement; }
    name = name || e.tagName.toLowerCase();
    owners[name] = (owners[name] || 0) + 1;
  }
  const total = cols * rows;
  return {table_percent: +(100 * product / total).toFixed(1),
          chrome_percent: +(100 * chrome / total).toFixed(1),
          nothing_percent: +(100 * none / total).toFixed(1),
          owners: Object.entries(owners).sort((a, b) => b[1] - a[1]).slice(0, 8)
            .map(([k, v]) => k + ' ' + (100 * v / total).toFixed(1) + '%')};
})()"""


def scroll_to_table(b):
    b.js("(()=>{const r=document.querySelector('#tbody tr');"
         "if(r)r.scrollIntoView({block:'start'});})()")
    time.sleep(0.6)


def run_release(b, gen, shots, tag):
    """Load one release and take the same reading four times: at rest, after a
    spine technology, after a wider-fleet technology, and at the table."""
    out = {'generation': gen, 'url': BASE % gen, 'shots': []}
    b.go(BASE % gen, settle=7.0)

    vis = b.js(PROBE_VISIBLE)
    if not isinstance(vis, dict) or vis.get('hidden') is not False:
        out['ABORT'] = 'document.hidden was not false on %s' % gen
        return out

    out['title'] = b.js('document.title')
    out['at_rest'] = b.js(READ)
    out['shots'].append(b.shot(os.path.join(shots, '%s-%s-01-rest.png' % (tag, gen))))

    scroll_to_table(b)
    out['share_at_table'] = b.js(SHARE)
    out['shots'].append(b.shot(os.path.join(shots, '%s-%s-02-table.png' % (tag, gen))))

    # spine technology: SOLAR is index 1 of #tech
    out['spine_pick'] = b.js(
        "(()=>{const bs=[...document.querySelectorAll('#tech button')];"
        "if(bs.length<2)return null;bs[1].click();"
        "return bs[1].textContent.trim();})()")
    time.sleep(1.5)
    out['after_spine'] = b.js(READ)
    out['shots'].append(b.shot(os.path.join(shots, '%s-%s-03-spine.png' % (tag, gen))))

    # wider fleet: the first real technology in the injected select
    out['wider_pick'] = b.js(
        "(()=>{const s=document.getElementById('widerTechnology');"
        "if(!s||s.options.length<2)return null;s.selectedIndex=1;"
        "s.dispatchEvent(new Event('change',{bubbles:true}));"
        "return s.options[1].textContent.trim();})()")
    time.sleep(1.8)
    out['after_wider'] = b.js(READ)
    out['shots'].append(b.shot(os.path.join(shots, '%s-%s-04-wider.png' % (tag, gen))))

    # THE EXPORT IS THE SURFACE THAT LEAVES THE BUILDING, so screen-reading
    # cannot cover it. On a release without the decline seam this click writes
    # a real 50-column CSV of somebody else's rows to disk, which is exactly
    # the defect under test -- so downloads are DENIED at the browser level
    # first (Browser.setDownloadBehavior), and the click is only ever made
    # while a non-spine cut owns the table, where the answer is interesting.
    out['export_click'] = {'state': 'after_wider'}
    b.js("document.getElementById('exportInline').click()")
    time.sleep(1.6)
    out['export_click']['after'] = b.js(
        "(()=>{const m=document.getElementById('exportMeta');if(!m)return null;"
        "return {text:(m.textContent||'').replace(/\\s+/g,' ').trim(),"
        "declined:m.classList.contains('is-declined'),"
        "missing:m.dataset.exportDeclinedColumns||null,"
        "counter:(document.getElementById('resultsMeta')||{}).textContent};})()")
    out['export_click']['errs'] = b.js('(window.__errs||[]).slice(0,6)')
    out['shots'].append(b.shot(os.path.join(shots, '%s-%s-05-export.png' % (tag, gen))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--a', required=True)
    ap.add_argument('--b', required=True)
    ap.add_argument('--mobile', action='store_true')
    ap.add_argument('--shots', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    os.makedirs(args.shots, exist_ok=True)
    tag = 'm' if args.mobile else 'd'
    b = Browser(args.port, mobile=args.mobile, headless=True)
    result = {'viewport': '393x852' if args.mobile else '1400x900',
              'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    try:
        b.setup(); b.arm()
        # Deny every download before a single page loads. Lane A is read-only
        # over the products; a discovery run must not be able to write one of
        # the wrong-rows CSVs it exists to find.
        for m in ('Browser.setDownloadBehavior', 'Page.setDownloadBehavior'):
            try:
                b.send(m, behavior='deny')
            except Exception as exc:
                result.setdefault('download_guard', []).append('%s: %s' % (m, exc))
        result['A'] = run_release(b, args.a, args.shots, tag)
        # NO second arm(): addScriptToEvaluateOnNewDocument already fires on
        # every navigation, so __errs is reset per release on its own. Arming
        # twice would wrap console.warn/error twice and double every line.
        result['B'] = run_release(b, args.b, args.shots, tag)
    finally:
        b.close()

    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps(result, indent=1)[:200])
    print('WROTE', args.out)


if __name__ == '__main__':
    main()

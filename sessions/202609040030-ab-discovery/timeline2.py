"""The same arrival, sampled four times a second, reported as TRANSITIONS.

The one-second timeline answered "is it timing" (yes) and raised two questions
it could not answer: exactly when the sheet arrives, and whether there is ever a
window in which an identity popup is on screen WITHOUT the measurement -- which
is the state the architect photographed and the state a 1 Hz sample can walk
straight past.

So this samples every 250 ms and prints a line only when the state CHANGES. A
state here is deliberately narrow: which popups exist, whether the sheet is
present, whether the answer has text, what the deep-link dataset says, and what
is actually painted where the answer will be. Everything else is noise between
transitions.

`says_working` from the first pass was a false positive -- it matched the word
"loading" somewhere in the page's own static prose, at t=1 s, before anything
had happened. This asks a narrower question instead: is a VISIBLE element
telling the reader that work is in progress, and is it inside the card.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, r'C:\Users\vikra\OneDrive\Documents\GitHub\claude\familiars')
from clicker import Browser  # noqa: E402

URL = ('https://ventusltd.github.io/gridatlas/atlas/'
       '?repd_ref=155&project=Markinch+Biomass+CHP+Plant&technology=biomass'
       '&capacity_mw=65&latitude=56.20118&longitude=-3.16226&zoom=12')

PROFILES = {
    'none':    None,
    'slow-4g': dict(latency=150, downloadThroughput=1500 * 1024 / 8,
                    uploadThroughput=750 * 1024 / 8),
    'slow-3g': dict(latency=400, downloadThroughput=400 * 1024 / 8,
                    uploadThroughput=400 * 1024 / 8),
}

STATE = r"""(() => {
  const R = e => { const r = e.getBoundingClientRect();
    return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
  const T = e => e ? (e.textContent || '').replace(/\s+/g, ' ').trim() : null;
  const vis = e => { if (!e) return false; const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return false;
    const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };

  const popups = [...document.querySelectorAll('.maplibregl-popup')].map(p => ({
    cls: p.className.replace('maplibregl-popup', '').replace(/\s+/g, ' ').trim() || '(plain)',
    rect: R(p), z: getComputedStyle(p).zIndex,
    is_sheet: p.classList.contains('gridatlas-sheet'),
    has_measure: /km straight/i.test(p.textContent || ''),
    text: T(p).slice(0, 90)}));

  const sheet = document.querySelector('.gridatlas-sheet');
  const answer = document.querySelector('.neon-answer');
  const loader = document.getElementById('gridatlas-loader');
  const sb = document.querySelector('.search-bar-wrapper');

  // is anything VISIBLE telling the reader work is in progress?
  let working = null;
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e)) continue;
    if (e.children.length) continue;
    const t = (e.textContent || '').trim();
    if (t && t.length < 80 && /computing|measuring|resolving|loading|working|please wait|…/i.test(t)) {
      /* WHERE the label is decides whether it answers the reader's question.
         A "Loading the substation…" line somewhere else on the page does not
         tell somebody staring at an identity popup that a measurement is
         coming for THIS project. */
      const pop = e.closest('.maplibregl-popup');
      working = {text: t.slice(0, 60), cls: String(e.className || e.tagName),
                 rect: R(e), in_popup: !!pop,
                 in_sheet: !!e.closest('.gridatlas-sheet')};
      break; }
  }

  return {
    popups: popups,
    n_popups: popups.length,
    sheet: !!sheet,
    sheet_rect: sheet ? R(sheet) : null,
    answer_len: answer ? (T(answer) || '').length : 0,
    deep: document.body.dataset.gridatlasRepdDeepLink || null,
    ref: document.body.dataset.gridatlasRepdRef || null,
    loader_visible: vis(loader),
    working_label: working,
    search_bar: vis(sb) ? {rect: R(sb), text: T(sb).slice(0, 120)} : null,
    ready: document.readyState,
    identity_repeats: ((document.body.textContent || '')
      .match(/Markinch Biomass CHP Plant/g) || []).length,
    // what a finger would hit where the answer eventually renders
    painted_at_answer: (() => { const e = document.elementFromPoint(innerWidth / 2, innerHeight * 0.78);
      if (!e) return null; let n = e;
      while (n && n !== document.body) {
        if (n.className && typeof n.className === 'string' && n.className.trim())
          return '.' + n.className.trim().split(/\s+/)[0];
        if (n.id) return '#' + n.id;
        n = n.parentElement; }
      return e.tagName.toLowerCase(); })(),
    errs: (window.__errs || []).slice(0, 4),
  };
})()"""


def key(s):
    """A state's identity, tolerant of a sample taken mid-navigation.

    b.js returns {'_error': ...} while the document is being swapped, and an
    earlier version compared `answer_len > 0` on that dict and died 60 seconds
    into a 70-second run. A probe that crashes on the states it exists to
    observe measures only the calm ones."""
    if not isinstance(s, dict) or '_error' in s:
        return 'ERROR:' + str((s or {}).get('_error'))[:60] if isinstance(s, dict) else 'ERROR'
    return json.dumps([s.get('n_popups'),
                       [p.get('cls', '') + ('+m' if p.get('has_measure') else '')
                        for p in s.get('popups') or []],
                       s.get('sheet'), bool(s.get('answer_len')), s.get('deep'),
                       s.get('loader_visible'), s.get('working_label'),
                       s.get('ready'), s.get('painted_at_answer'),
                       s.get('identity_repeats')], sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--profile', default='slow-4g', choices=sorted(PROFILES))
    ap.add_argument('--mobile', action='store_true')
    ap.add_argument('--seconds', type=float, default=45.0)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    b = Browser(args.port, mobile=args.mobile, headless=True)
    res = {'url': URL, 'profile': args.profile, 'mobile': args.mobile,
           'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'transitions': []}
    try:
        b.setup(); b.arm()
        b.send('Network.enable')
        if PROFILES[args.profile]:
            c = PROFILES[args.profile]
            b.send('Network.emulateNetworkConditions', offline=False, **c)
            res['throttle'] = c

        t0 = time.time()
        b.send('Page.navigate', url=URL)
        try:
            b.send('Page.bringToFront')
        except Exception:
            pass

        last = None
        while time.time() - t0 < args.seconds:
            s = b.js(STATE)
            k = key(s)
            if k != last:
                last = k
                if isinstance(s, dict):
                    s['t_s'] = round(time.time() - t0, 2)
                res['transitions'].append(s)
            time.sleep(0.25)
        res['final_hidden'] = b.js('document.hidden')
    finally:
        b.close()

    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=1)
    print('WROTE', args.out, len(res['transitions']), 'transitions')


if __name__ == '__main__':
    main()

"""When does the grid measurement appear, and what is on screen before it does?

The architect arrived at the live Atlas from Pipeline News and saw the identity
popup with no measurement. Two agents then measured the same URL and found the
measurement present. Both readings can be true: an END STATE cannot answer a
question about a TRANSIENT one. So this samples the DOM from the moment of
navigation rather than after it settles, on a cold profile and a throttled
link, and reports what a reader has on screen at each second.

It reports the timeline. It does not decide which of the three theories is
right - but a timeline distinguishes them: a timing gap shows the sheet
arriving late, a two-popup ordering fault shows the sheet present and covered
or off-screen from the first sample, and a real-device difference shows neither.

  python timeline.py --port 9441 --profile slow-3g --mobile
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

# Chrome DevTools' own presets, so the numbers mean what a reader expects
PROFILES = {
    'none':     None,
    'fast-4g':  dict(latency=20,  downloadThroughput=9000 * 1024 / 8,
                     uploadThroughput=9000 * 1024 / 8),
    'slow-4g':  dict(latency=150, downloadThroughput=1500 * 1024 / 8,
                     uploadThroughput=750 * 1024 / 8),
    'slow-3g':  dict(latency=400, downloadThroughput=400 * 1024 / 8,
                     uploadThroughput=400 * 1024 / 8),
}

SAMPLE = r"""(() => {
  const rect = e => { const r = e.getBoundingClientRect();
    return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
  const txt = e => e ? (e.textContent || '').replace(/\s+/g, ' ').trim() : null;

  const sheet = document.querySelector('.gridatlas-sheet, .maplibregl-popup.gridatlas-sheet');
  const answer = document.querySelector('.neon-answer');
  const body = (document.body.textContent || '').replace(/\s+/g, ' ');

  // every popup in the DOM, in paint order, with the stacking that decides
  // which one a reader actually sees
  const popups = [...document.querySelectorAll('.maplibregl-popup')].map((p, i) => {
    const cs = getComputedStyle(p);
    const r = rect(p);
    return {i, cls: p.className, rect: r, z: cs.zIndex, display: cs.display,
            opacity: cs.opacity, visibility: cs.visibility,
            offscreen_below: r[1] > innerHeight,
            offscreen_any: r[1] > innerHeight || r[1] + r[3] < 0
              || r[0] > innerWidth || r[0] + r[2] < 0,
            text: txt(p).slice(0, 110)};
  });

  // what is actually painted at the middle of the viewport and at the card
  const topAt = (x, y) => { const e = document.elementFromPoint(x, y);
    if (!e) return null; let n = e, nm = '';
    while (n && n !== document.body) {
      if (n.className && typeof n.className === 'string' && n.className.trim()) {
        nm = '.' + n.className.trim().split(/\s+/)[0]; break; }
      if (n.id) { nm = '#' + n.id; break; }
      n = n.parentElement; }
    return nm || e.tagName.toLowerCase(); };

  return {
    hidden: document.hidden,
    viewport: innerWidth + 'x' + innerHeight,
    ready: document.readyState,
    sheet_present: !!sheet,
    sheet_rect: sheet ? rect(sheet) : null,
    sheet_offscreen_below: sheet ? rect(sheet)[1] > innerHeight : null,
    answer_present: !!answer,
    answer_text: txt(answer) ? txt(answer).slice(0, 160) : null,
    answer_rect: answer ? rect(answer) : null,
    has_nearest: /Nearest/i.test(body),
    has_km_straight: /km straight/i.test(body),
    has_corridor: /corridor estimate/i.test(body),
    measurement_line: (body.match(/Nearest[^·]{0,60}substation:[^|]{0,120}/) || [null])[0],
    /* an absence that announces itself and an absence that is silent are
       different products; this is the test for which one is on screen */
    says_working: /computing|measuring|loading|working|resolving|please wait/i.test(body),
    deep_link_state: document.body.dataset.gridatlasRepdDeepLink || null,
    deep_link_ref: document.body.dataset.gridatlasRepdRef || null,
    popups: popups,
    popup_count: popups.length,
    top_at_centre: topAt(innerWidth / 2, innerHeight / 2),
    top_at_lower_third: topAt(innerWidth / 2, innerHeight * 0.75),
    identity_repeats: (body.match(/Markinch Biomass CHP Plant/g) || []).length,
    errs: (window.__errs || []).slice(0, 6),
  };
})()"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--profile', default='slow-4g', choices=sorted(PROFILES))
    ap.add_argument('--mobile', action='store_true')
    ap.add_argument('--out', required=True)
    ap.add_argument('--shots', default='shots')
    args = ap.parse_args()
    os.makedirs(args.shots, exist_ok=True)

    b = Browser(args.port, mobile=args.mobile, headless=True)
    res = {'url': URL, 'profile': args.profile, 'mobile': args.mobile,
           'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'samples': []}
    try:
        b.setup()
        b.arm()
        b.send('Network.enable')
        cond = PROFILES[args.profile]
        if cond:
            b.send('Network.emulateNetworkConditions', offline=False,
                   latency=cond['latency'],
                   downloadThroughput=cond['downloadThroughput'],
                   uploadThroughput=cond['uploadThroughput'])
            res['throttle'] = cond

        # settle=0: the whole point is to read BEFORE the page settles
        t0 = time.time()
        b.send('Page.navigate', url=URL)
        try:
            b.send('Page.bringToFront')
        except Exception:
            pass

        for at in (1, 2, 3, 5, 7, 10, 15, 20, 30):
            while time.time() - t0 < at:
                time.sleep(0.05)
            s = b.js(SAMPLE)
            if isinstance(s, dict):
                s['t_s'] = round(time.time() - t0, 2)
            res['samples'].append({'at': at, 'reading': s})
            if at in (2, 5, 10, 30):
                res.setdefault('shots', []).append(b.shot(os.path.join(
                    args.shots, 'timeline-%s-%s-t%02d.png'
                    % (args.profile, 'm' if args.mobile else 'd', at))))
    finally:
        b.close()

    with open(args.out, 'w', encoding='utf-8') as fh:
        json.dump(res, fh, indent=1)
    print('WROTE', args.out)


if __name__ == '__main__':
    main()

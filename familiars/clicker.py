"""clicker - eyes on this machine's hardware, not in the model's context.

WHY THIS EXISTS

Three things went wrong today that this single tool answers.

An agent reported a UI as fixed on the strength of coordinates - `overlap: 0 px2`,
`fullyInViewport: true` - on a screen the architect found unusable. A proof reported
104/104 checks passed against the same screen. **A UI cannot be signed off from geometry,
and a check can only test what someone thought to assert.**

Three agents fought over one shared browser: tabs were created and switched under each
other, one agent's tab left its group mid-session, and every measurement taken while a
tab was hidden reproduced the exact rendering failure being investigated. **Each clicker
launches its OWN Chrome, on its OWN port, with its OWN profile.** Two of them on two
ports is the architect's acceptance rule - *"at least two agents on different browsers
clicked and checked that it works"* - mechanised, and they cannot corrupt one another.

And every browser observation cost model tokens. This costs none. It runs here.

    python familiars/clicker.py --port 9411 --url https://... --journey world
    python familiars/clicker.py --port 9412 --url https://... --journey world --mobile

WHAT IT REFUSES TO DO

It never reports a measurement taken while `document.hidden` is true. That state stalls
MapLibre on this estate and produces confident false failures - one agent lost thirteen
minutes to it and my own first look at the Atlas was invalid for the same reason. If the
page will not come to the front, the clicker says so and fails rather than guessing.

It reports what it observed. It does not diagnose. The eyes are not the mind.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import websocket

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'


class Browser:
    """One Chrome, one port, one profile. Nothing shared with anybody."""

    def __init__(self, port, mobile=False, headless=True):
        self.port = port
        self.mobile = mobile
        self.profile = tempfile.mkdtemp(prefix='clicker-%d-' % port)
        args = [CHROME,
                '--remote-debugging-port=%d' % port,
                # Chrome 152 rejects the CDP websocket without this and says so
                # clearly - which only became visible once its stderr stopped
                # going to DEVNULL. The symptom was 'did not expose a page'.
                '--remote-allow-origins=*',
                '--user-data-dir=' + self.profile,
                '--no-first-run', '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                'about:blank']
        if headless:
            args.insert(1, '--headless=new')
        # Chrome's own words are kept. Swallowing them into DEVNULL meant a
        # launch that died instantly was polled for thirty seconds and reported
        # as "did not expose a page", which named the symptom and hid the cause.
        self._log = tempfile.NamedTemporaryFile(
            prefix='clicker-%d-' % port, suffix='.log', delete=False)
        self.proc = subprocess.Popen(args, stdout=self._log, stderr=self._log)
        self.ws = None
        self._id = 0
        self._connect()

    def _connect(self, timeout=30):
        deadline = time.time() + timeout
        while time.time() < deadline:
            # Chrome binds IPv4 or IPv6 depending on what is free. When 127.0.0.1
            # was already held it listened on [::1] alone and the IPv4 probe saw
            # nothing, which read as "no page" rather than "wrong stack".
            for host in ('127.0.0.1', '[::1]'):
                try:
                    with urllib.request.urlopen(
                            'http://%s:%d/json' % (host, self.port), timeout=2) as r:
                        tabs = json.load(r)
                    page = [t for t in tabs if t.get('type') == 'page']
                    if page:
                        self.ws = websocket.create_connection(
                            page[0]['webSocketDebuggerUrl'], timeout=90,
                            origin='http://%s:%d' % (host, self.port))
                        return
                except Exception:
                    pass
            if self.proc.poll() is not None:
                self._log.flush()
                with open(self._log.name, 'r', errors='replace') as fh:
                    said = fh.read().strip()[-400:]
                raise RuntimeError('chrome exited %s before serving port %d: %s'
                                   % (self.proc.returncode, self.port,
                                      said or '(said nothing)'))
            time.sleep(0.4)
        self._log.flush()
        with open(self._log.name, 'r', errors='replace') as fh:
            said = fh.read().strip()[-400:]
        raise RuntimeError('chrome did not expose a page on port %d in %ss: %s'
                           % (self.port, timeout, said or '(said nothing)'))

    def send(self, method, **params):
        self._id += 1
        self.ws.send(json.dumps({'id': self._id, 'method': method, 'params': params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('id') == self._id:
                if 'error' in msg:
                    raise RuntimeError('%s: %s' % (method, msg['error']))
                return msg.get('result', {})

    def setup(self):
        self.send('Page.enable')
        self.send('Runtime.enable')
        if self.mobile:
            self.send('Emulation.setDeviceMetricsOverride', width=393, height=852,
                      deviceScaleFactor=3, mobile=True)
            self.send('Emulation.setUserAgentOverride', userAgent=(
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 '
                'Safari/604.1'))
            self.send('Emulation.setTouchEmulationEnabled', enabled=True,
                      maxTouchPoints=5)
            self.send('Emulation.setEmitTouchEventsForMouse', enabled=True,
                      configuration='mobile')
        else:
            self.send('Emulation.setDeviceMetricsOverride', width=1400, height=900,
                      deviceScaleFactor=1, mobile=False)

    def arm(self):
        """Listeners must exist BEFORE the page's own scripts run.

        The first version installed them after navigation and therefore caught
        nothing thrown during load - which is exactly the window where a map
        fails. Page.addScriptToEvaluateOnNewDocument runs first, every time."""
        self.send('Page.addScriptToEvaluateOnNewDocument', source=(
            "window.__errs=[];"
            "addEventListener('error',e=>window.__errs.push("
            "  (e.message||'')+' @'+(e.filename||'').split('/').pop()+':'+(e.lineno||0)));"
            "addEventListener('unhandledrejection',e=>window.__errs.push("
            "  'promise: '+((e.reason&&e.reason.message)||e.reason)));"
            "window.__log=[];"
            "['warn','error'].forEach(k=>{const o=console[k].bind(console);"
            "  console[k]=(...a)=>{window.__log.push(k+': '+a.map(String).join(' ').slice(0,220));o(...a);};});"
        ))

    def go(self, url, settle=6.0):
        self.send('Page.navigate', url=url)
        time.sleep(settle)
        try:
            self.send('Page.bringToFront')
        except Exception:
            pass

    def js(self, expr):
        r = self.send('Runtime.evaluate', expression=expr, awaitPromise=True,
                      returnByValue=True)
        if r.get('exceptionDetails'):
            return {'_error': str(r['exceptionDetails'].get('text'))[:160]}
        return r.get('result', {}).get('value')

    def shot(self, path):
        r = self.send('Page.captureScreenshot', format='png')
        import base64
        with open(path, 'wb') as fh:
            fh.write(base64.b64decode(r['data']))
        return path

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass
        shutil.rmtree(self.profile, ignore_errors=True)


# ── journeys ────────────────────────────────────────────────────────────────

PROBE_VISIBLE = "({hidden: document.hidden, w: innerWidth, h: innerHeight})"


def journey_world(b, shots_dir):
    """Open the world, open every menu, click through it, and say what happened."""
    out = {'steps': [], 'shots': []}

    vis = b.js(PROBE_VISIBLE)
    out['viewport'] = vis
    if not isinstance(vis, dict) or vis.get('hidden') is not False:
        out['ABORT'] = ('document.hidden was not false - every measurement from here '
                        'would be worthless on this product')
        return out

    out['title'] = b.js("document.title")
    out['menus'] = b.js(
        "[...document.querySelectorAll('#bar .t')].map(e=>e.textContent.trim())")
    out['hud'] = b.js(
        "({fps:(document.getElementById('fps')||{}).textContent,"
        " circuits:(document.getElementById('nlines')||{}).textContent,"
        " carriers:(document.getElementById('nparts')||{}).textContent,"
        " cores:(document.getElementById('cores')||{}).textContent,"
        " gpu:(document.getElementById('gpu')||{}).textContent})")
    out['map_canvas'] = b.js(
        "(()=>{const c=document.querySelector('#map canvas');"
        "if(!c)return null;const r=c.getBoundingClientRect();"
        "return Math.round(r.width)+'x'+Math.round(r.height)+' @'+Math.round(r.top);})()")
    out['shots'].append(b.shot(os.path.join(shots_dir, 'world-01-open.png')))

    # open each menu in turn and record what is inside it
    names = out['menus'] or []
    contents = {}
    for i, name in enumerate(names):
        b.js("document.querySelectorAll('#bar .t')[%d].click()" % i)
        time.sleep(0.35)
        contents[name] = b.js(
            "[...document.querySelectorAll('#bar .m.open .p > *')]"
            ".map(e=>e.textContent.trim()).filter(Boolean)")
        if i == 0:
            out['shots'].append(b.shot(os.path.join(shots_dir, 'world-02-menu.png')))
    out['menu_contents'] = contents

    # only one open at a time?
    out['one_open_at_a_time'] = b.js(
        "document.querySelectorAll('#bar .m.open').length")

    # does a click elsewhere close it? (self-minimising)
    b.js("document.body.click()")
    time.sleep(0.3)
    out['closes_on_outside_click'] = b.js(
        "document.querySelectorAll('#bar .m.open').length === 0")

    # is it alive? sample the frame counter twice
    f1 = b.js("(document.getElementById('fps')||{}).textContent")
    time.sleep(2.0)
    f2 = b.js("(document.getElementById('fps')||{}).textContent")
    out['fps_samples'] = [f1, f2]
    out['is_moving'] = bool(f1 and f2 and f1 != '—' and f2 != '—')

    out['console_errors'] = b.js("(window.__errs||[]).slice(0,6)")
    out['console_log'] = b.js("(window.__log||[]).slice(0,6)")
    out['shots'].append(b.shot(os.path.join(shots_dir, 'world-03-after.png')))
    return out



SUMMARY_READ = """(() => {
  const t = e => e ? (e.textContent || '').trim() : null;
  const meta = document.getElementById('resultsMeta');
  const arc = id => { const c = document.getElementById(id);
    return c && c.toDataURL ? c.toDataURL().slice(-48) : null; };
  return {
    counter: t(meta),
    filteredCount: meta ? meta.dataset.filteredCount : null,
    totalCount: meta ? meta.dataset.totalCount : null,
    v1: t(document.getElementById('v1')),
    v2: t(document.getElementById('v2')),
    v3: t(document.getElementById('v3')),
    arcs: [arc('g1'), arc('g2'), arc('g3')].join('|'),
    exportMeta: t(document.getElementById('exportMeta')),
    rows: document.querySelectorAll('#results tbody tr').length,
    widerOptions: document.getElementById('widerTechnology')
      ? document.getElementById('widerTechnology').options.length : 0
  };
})()"""


def journey_summary(b, shots_dir):
    """Pipeline News: does one summary drive every surface it is supposed to?

    The defect this exists to catch is silent. A wider-fleet cut writes the
    three gauge NUMBERS and nothing else, so the record counter, the gauge
    ARCS and the CSV keep the previous technology's answer while the screen
    looks correct. Nothing throws, nothing logs, and the export leaves the
    building with the wrong rows under a confident heading.

    So this reads all five surfaces before and after a technology switch and
    reports both states. It does not decide whether the product is right -
    it makes the divergence visible. The eyes are not the mind."""
    out = {'steps': [], 'shots': []}

    vis = b.js(PROBE_VISIBLE)
    out['viewport'] = vis
    if not isinstance(vis, dict) or vis.get('hidden') is not False:
        out['ABORT'] = ('document.hidden was not false - a backgrounded tab stalls '
                        'this estate and every reading below would be worthless')
        return out

    out['title'] = b.js('document.title')
    out['before'] = b.js(SUMMARY_READ)
    out['shots'].append(b.shot(os.path.join(shots_dir, 'summary-01-spine.png')))

    if not out['before'] or not out['before'].get('widerOptions'):
        out['ABORT'] = 'no #widerTechnology control on this page - nothing to switch'
        return out

    # pick the wider-fleet technology by NAME, so the reading names its subject
    out['technology'] = b.js(
        "(()=>{const s=document.getElementById('widerTechnology');"
        "s.selectedIndex=1;s.dispatchEvent(new Event('change',{bubbles:true}));"
        "return s.options[1].textContent.trim();})()")
    time.sleep(1.2)
    out['after'] = b.js(SUMMARY_READ)
    out['shots'].append(b.shot(os.path.join(shots_dir, 'summary-02-wider.png')))

    # The export is the surface that leaves the building, so it is the one
    # surface a reading of the screen cannot cover. Clicking it is safe ONLY
    # where the seam is installed: there `downloadCsv` answers in words and
    # returns before a blob exists. On a release without the seam the same
    # click writes a real file to disk, so this is opt-in per run rather than
    # something the journey decides for itself.
    if os.environ.get('CLICKER_EXPORT_CLICK') == '1':
        b.js("document.getElementById('exportInline').click()")
        time.sleep(1.0)
        out['export_after_click'] = b.js(
            "(()=>{const m=document.getElementById('exportMeta');return m?{"
            "text:(m.textContent||'').trim(),"
            "declined:m.classList.contains('is-declined'),"
            "missing:m.dataset.exportDeclinedColumns||null}:null;})()")
        out['shots'].append(b.shot(os.path.join(shots_dir, 'summary-03-export.png')))

    a, c = out['before'], out['after']
    out['moved'] = {k: (a.get(k) != c.get(k))
                    for k in ('counter', 'filteredCount', 'totalCount',
                              'v1', 'v2', 'v3', 'arcs', 'exportMeta')}
    out['counter_and_gauges_disagree'] = bool(
        c.get('counter') and c.get('v3') and c.get('v3') not in c.get('counter'))
    out['console_errors'] = b.js('(window.__errs||[]).slice(0,6)')
    out['console_log'] = b.js('(window.__log||[]).slice(0,6)')
    return out



# every control a reader could reach for, and whether it has a box to click
CONTROLS = r"""(() => {
  const els = [...document.querySelectorAll('button, a[role=button], input[type=checkbox], select, [role=button]')];
  const zero = [], live = [];
  for (const el of els) {
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const name = (el.id ? '#' + el.id : (el.textContent || el.getAttribute('aria-label') || el.tagName)
      .replace(/\s+/g, ' ').trim().slice(0, 28)) || el.tagName;
    const hidden = cs.display === 'none' || cs.visibility === 'hidden';
    (r.width < 1 || r.height < 1 ? zero : live).push(
      name + ' ' + Math.round(r.width) + 'x' + Math.round(r.height) + (hidden ? ' display:none' : ''));
  }
  return {live: live.length, zero: zero.length, zero_named: zero.slice(0, 20)};
})()"""

# how much of the screen is the product, and how much is its controls
SCREEN_SHARE = r"""(() => {
  const W = innerWidth, H = innerHeight, cols = 40, rows = 80;
  const canvas = document.querySelector('canvas.maplibregl-canvas, #map canvas, canvas');
  let map = 0, chrome = 0, none = 0;
  const owners = {};
  for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) {
    const x = (i + 0.5) * W / cols, y = (j + 0.5) * H / rows;
    const el = document.elementFromPoint(x, y);
    if (!el) { none++; continue; }
    if (canvas && (el === canvas || el.contains(canvas))) { map++; continue; }
    chrome++;
    let node = el, name = '';
    while (node && node !== document.body) {
      if (node.id) { name = '#' + node.id; break; }
      if (node.className && typeof node.className === 'string' && node.className.trim()) {
        name = '.' + node.className.trim().split(/\s+/)[0]; break;
      }
      node = node.parentElement;
    }
    name = name || el.tagName.toLowerCase();
    owners[name] = (owners[name] || 0) + 1;
  }
  const total = cols * rows;
  return {
    viewport: W + 'x' + H,
    map_percent: +(100 * map / total).toFixed(1),
    chrome_percent: +(100 * chrome / total).toFixed(1),
    nothing_percent: +(100 * none / total).toFixed(1),
    chrome_owners: Object.entries(owners).sort((a, b) => b[1] - a[1]).slice(0, 12)
      .map(([k, v]) => k + ' ' + (100 * v / total).toFixed(1) + '%')
  };
})()"""

BANDS = r"""(() => {
  const out = [];
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (!['fixed', 'absolute', 'sticky'].includes(cs.position)) continue;
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 24 || r.height < 12) continue;
    if (r.bottom < 0 || r.top > innerHeight || r.right < 0 || r.left > innerWidth) continue;
    if (el.querySelector('canvas')) continue;
    out.push({
      what: (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string'
        ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : ''),
      rect: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)],
      text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 70)
    });
  }
  return out.sort((a, b) => a.rect[1] - b.rect[1]).slice(0, 24);
})()"""


def journey_atlas_rest(b, shots_dir):
    """What does the Atlas look like when nobody has touched it?

    The directive of 2026-09-03 said roughly sixty per cent of the screen is
    menu before any content, and nobody had ever measured it: every check that
    night asked whether the answer was REACHABLE, which is a coordinate
    question that got fixed, and never asked how much of the screen the product
    got, which is the same kind of question and just as easy.

    So this samples 3,200 points of the viewport and asks the DOM which element
    is on top at each one. A point whose topmost element is the map canvas is
    product. Everything else is chrome. It reports the split and names the
    elements holding the chrome, and it repeats both on a deep-link arrival,
    where the identity is known to appear more than once."""
    out = {'shots': []}
    vis = b.js(PROBE_VISIBLE)
    out['viewport'] = vis
    if not isinstance(vis, dict) or vis.get('hidden') is not False:
        out['ABORT'] = 'document.hidden was not false - MapLibre stalls and every reading lies'
        return out

    time.sleep(3.0)                      # the map draws before anything is measured
    out['at_rest'] = b.js(SCREEN_SHARE)
    out['bands_at_rest'] = b.js(BANDS)
    out['search_value_at_rest'] = b.js(
        "(()=>{const i=[...document.querySelectorAll('input')]"
        ".filter(e=>e.offsetParent!==null&&e.type!=='hidden');"
        "return i.map(e=>({ph:e.placeholder||'',v:e.value||''}));})()")
    out['shots'].append(b.shot(os.path.join(shots_dir, 'atlas-01-rest.png')))
    out['controls_at_rest'] = b.js(CONTROLS)

    # the panel must come BACK. A minimise that cannot be undone is a deletion.
    out['toggle_label'] = b.js(
        "(document.getElementById('gridatlas-dash-toggle')||{}).textContent")
    b.js("(document.getElementById('gridatlas-dash-toggle')||{click(){}}).click()")
    time.sleep(1.2)
    out['after_toggle'] = b.js(SCREEN_SHARE)
    out['controls_after_toggle'] = b.js(CONTROLS)
    out['toggle_label_after'] = b.js(
        "(document.getElementById('gridatlas-dash-toggle')||{}).textContent")
    out['shots'].append(b.shot(os.path.join(shots_dir, 'atlas-02-expanded.png')))
    out['console_errors'] = b.js('(window.__errs||[]).slice(0,6)')
    return out



def journey_maplink(b, shots_dir):
    """Where does MAP actually go?

    Every Pipeline News generation builds every per-project Atlas link from one
    frozen constant, and ten invariants guard it - all of them shape checks. A
    pathname equality asserted that the route was /gridatlas/<release_id>/,
    which is exactly the form that has returned 404 since the Atlas moved to a
    composed shell. The check passed for four days while the button was dead.

    So this reads the HREF THE PRODUCT WOULD OPEN, off a rendered row, and
    reports it for a caller to resolve over the network. A link's liveness
    cannot be asserted from inside the page - CORS forbids the readback - and a
    string that describes liveness is not liveness."""
    out = {'shots': []}
    vis = b.js(PROBE_VISIBLE)
    out['viewport'] = vis
    if not isinstance(vis, dict) or vis.get('hidden') is not False:
        out['ABORT'] = 'document.hidden was not false'
        return out

    time.sleep(2.0)
    out['title'] = b.js('document.title')
    out['module_threw'] = b.js(
        "(window.__errs||[]).filter(e=>/receiver|contract|Atlas/i.test(e)).slice(0,4)")
    out['links'] = b.js(
        "[...document.querySelectorAll('a')].map(a=>a.href)"
        ".filter(h=>/gridatlas/.test(h)).slice(0,6)")
    out['map_cells'] = b.js(
        "[...document.querySelectorAll('a,button')]"
        ".filter(e=>/^MAP$/i.test((e.textContent||'').trim()))"
        ".slice(0,3).map(e=>({tag:e.tagName, href:e.href||null,"
        " onclick:!!e.onclick}))")
    out['rows'] = b.js("document.querySelectorAll('#results tbody tr').length")
    out['console_errors'] = b.js('(window.__errs||[]).slice(0,6)')
    out['shots'].append(b.shot(os.path.join(shots_dir, 'maplink-01.png')))
    return out



def journey_arrival(b, shots_dir):
    """What does a reader actually GET when a deep link lands?

    Not how much screen the map has - what the product SAYS. Whether the
    identity resolved, whether any measurement was computed for it, and if
    not, whether the page says so or simply shows nothing. An absence that
    announces itself and an absence that is silent look identical in a
    screenshot and are completely different products."""
    out = {'shots': []}
    vis = b.js(PROBE_VISIBLE)
    out['viewport'] = vis
    if not isinstance(vis, dict) or vis.get('hidden') is not False:
        out['ABORT'] = 'document.hidden was not false'
        return out

    time.sleep(7.0)                      # the register resolves before anything is read
    out['deep_link_state'] = b.js(
        "({state: document.body.dataset.gridatlasRepdDeepLink || null,"
        " ref: document.body.dataset.gridatlasRepdRef || null})")
    out['search_state'] = b.js(
        "(()=>{const s=window.__GRIDATLAS_PLACE_SEARCH__||window.__V9_PLACE_SEARCH__;"
        "if(!s)return null;const d=s.deep_link||{};"
        "return {status:d.status,resolved:d.resolved,mapped:d.mapped,name:d.name,"
        "technology:d.technology,capacity_mw:d.capacity_mw,message:d.message||null};})()")
    out['card_text'] = b.js(
        "(()=>{const c=document.querySelector('.maplibregl-popup-content,"
        ".gridatlas-sheet,.gridatlas-neon-block');"
        "return c?(c.textContent||'').replace(/\s+/g,' ').trim().slice(0,1400):null;})()")
    out['measurement_words'] = b.js(
        "(()=>{const t=(document.body.textContent||'').replace(/\s+/g,' ');"
        "const hits={};"
        "for (const w of ['Nearest','substation','km straight','corridor estimate',"
        "'400 kV','no measurement','not measured','No mapped feature']) "
        "  hits[w]=(t.match(new RegExp(w.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi'))||[]).length;"
        "return hits;})()")
    out['layers_lit'] = b.js(
        "(()=>{try{const m=window.map;if(!m||!m.getStyle)return null;"
        "const ls=m.getStyle().layers||[];"
        "const vis=ls.filter(l=>{try{return m.getLayoutProperty(l.id,'visibility')!=='none';}"
        "catch(_){return false;}});"
        "return {total:ls.length, visible:vis.length,"
        " named:vis.map(l=>l.id).filter(id=>/wind|solar|bess|repd|project/i.test(id)).slice(0,12)};"
        "}catch(e){return {error:String(e).slice(0,80)};}})()")
    out['camera'] = b.js(
        "(()=>{const L=window.__GRIDATLAS_NEON_LINKS__||{};"
        "const m=L.map||window.map||null;"
        "const cam=m&&m.getZoom?{zoom:+m.getZoom().toFixed(2),"
        " center:m.getCenter?[+m.getCenter().lng.toFixed(4),+m.getCenter().lat.toFixed(4)]:null,"
        " bearing:m.getBearing?+m.getBearing().toFixed(1):null,"
        " pitch:m.getPitch?+m.getPitch().toFixed(1):null}:null;"
        "return {camera:cam, requested_zoom:L.requested_zoom??null,"
        " zoom_applied:L.zoom_applied??null, has_map_handle:!!m};})()")
    out['console_errors'] = b.js('(window.__errs||[]).slice(0,8)')
    out['shots'].append(b.shot(os.path.join(shots_dir, 'arrival.png')))
    return out


JOURNEYS = {'world': journey_world, 'summary': journey_summary,
            'atlas-rest': journey_atlas_rest, 'maplink': journey_maplink,
            'arrival': journey_arrival}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, required=True)
    ap.add_argument('--url', required=True)
    ap.add_argument('--journey', default='world', choices=sorted(JOURNEYS))
    ap.add_argument('--mobile', action='store_true')
    ap.add_argument('--shots', default=None)
    ap.add_argument('--headed', action='store_true')
    a = ap.parse_args(argv)

    shots = a.shots or tempfile.mkdtemp(prefix='clicker-shots-')
    os.makedirs(shots, exist_ok=True)

    b = Browser(a.port, mobile=a.mobile, headless=not a.headed)
    try:
        b.setup()
        b.arm()
        b.go(a.url)
        result = JOURNEYS[a.journey](b, shots)
    finally:
        b.close()

    result['_clicker'] = {'port': a.port, 'mobile': a.mobile, 'url': a.url,
                          'shots_dir': shots}
    print(json.dumps(result, indent=1))
    return 0 if not result.get('ABORT') else 2


if __name__ == '__main__':
    sys.exit(main())

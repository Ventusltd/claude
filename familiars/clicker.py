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


JOURNEYS = {'world': journey_world}


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

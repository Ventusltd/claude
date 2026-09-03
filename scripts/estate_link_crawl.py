"""estate_link_crawl.py - every published release, every outbound route, every sentinel.

WHY THIS EXISTS

A product linked to a route that no longer exists and nothing told anyone. When GridAtlas
moved its releases from `/gridatlas/<release-id>/` to `/gridatlas/atlas/releases/<release-id>/`,
the Pipeline News release that was live went on emitting the old shape. All eight of its
sentinels 404 and the page still renders, because a deep link that 404s is a link the user
clicks, not an error the build sees. The failure is invisible from inside the repository:
the files are all present, the manifest validates, and the bytes are the bytes that were
published. It is only visible from OUTSIDE, over HTTP, against the live origin.

That is a crawl, and a crawl is the one shape of work this estate has been doing serially on
a laptop that a matrix of runners does in parallel for nothing. So it runs in the cloud.

WHAT A SENTINEL IS HERE

A sentinel is a REPD reference number that a release promises will deep-link into GridAtlas.
It is declared in a release's `build-manifest.json` under a receiver block:

    "golden_repd_ref": "16135", "browser_sentinels": ["17494","13599", ...]

and the URL is `base_url + "?repd_ref=" + ref`. Eight per release: one golden, seven browser.
The block is nested under different keys in different generations (`receiver`, and
`gridatlas_receiver_evidence.receiver`), so this crawler finds it BY SHAPE - any object
carrying `golden_repd_ref` or `browser_sentinels` - rather than by a key path that was true
of one generation.

THE FALSE POSITIVE THIS AVOIDS

Roughly 30 release directories still carry a deep-link module with the dead base URL, but
most of them DO NOT IMPORT IT - the app imports a successor with the corrected base. Grepping
the directory reports 30 broken releases when the true number is far smaller. So the crawler
resolves the import closure from the page's own `<script type=module>` and reports two
different facts, never merged:

    declared   the base_url the release's manifest claims        (may be a dead pointer)
    shipped    the base_url in a module the page actually imports (what a user gets)

A dead `declared` base whose module is not in the import closure is a stale record.
A dead `shipped` base is a live defect. They are counted separately.

A REDIRECT TO 200 IS NOT A 200. The crawler compares the effective URL against the requested
one, because `/gridatlas/` is a JavaScript redirect and a plain status check would call it
healthy.

THIS IS AN INFORMATIONAL SURVEY. IT EXITS 0 ON EVERY FINDING, ALWAYS.

A crawl is a report, not a gate. In GitHub Actions a non-zero exit mails the actor, and this
job is meant to run nightly without ever doing that. Findings live in the JSON artifact and
the committed board, never in the exit code. A 404 discovered here is a fact to read, not an
alarm to silence. If you are about to "fix" this into a gate: don't - write a separate gate,
narrow it to the one route that must never die, and let this go on surveying everything else.

    python scripts/estate_link_crawl.py --surface gridatlas-atlas --out shard.json
    python scripts/estate_link_crawl.py --collate shard-*.json --board docs/boards/links.md

Surfaces (the matrix axis):
    globalgrid2050        the homepage and every route its catalogue names
    pipelinenews-intel    the 28 Pipeline News snapshots served from globalgrid2050.com
    gridatlas-atlas       the composed shell, current.json, and every atlas release
    pipelinenews-releases every /pipelinenews/releases/<gen>-pipelinenews/ release
"""

import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

UA = 'ventus-estate-link-crawl'
TIMEOUT = 30

GG = 'https://globalgrid2050.com/'
GA = 'https://ventusltd.github.io/gridatlas/'
PN = 'https://ventusltd.github.io/pipelinenews/'

SURFACES = ('globalgrid2050', 'pipelinenews-intel', 'gridatlas-atlas', 'pipelinenews-releases')


# ---------------------------------------------------------------- fetching

def fetch(url, method='GET'):
    """Return a reading, never a default. A failure is status 0 with the reason attached."""
    t0 = time.time()
    req = urllib.request.Request(url, method=method, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read() if method == 'GET' else b''
            return {'url': url, 'status': r.status, 'effective': r.geturl(),
                    'bytes': len(body), 'body': body,
                    'ctype': r.headers.get('Content-Type', ''),
                    'took_ms': int((time.time() - t0) * 1000)}
    except urllib.error.HTTPError as e:
        return {'url': url, 'status': e.code, 'effective': e.geturl(), 'bytes': 0, 'body': b'',
                'ctype': '', 'took_ms': int((time.time() - t0) * 1000)}
    except Exception as e:
        return {'url': url, 'status': 0, 'effective': url, 'bytes': 0, 'body': b'',
                'ctype': '', 'error': str(e)[:140], 'took_ms': int((time.time() - t0) * 1000)}


def text(r):
    try:
        return r['body'].decode('utf-8', 'replace')
    except Exception:
        return ''


def check(url):
    """One route, reported as a row. Redirected-to-200 is recorded, not hidden."""
    r = fetch(url)
    row = {'url': url, 'status': r['status'], 'bytes': r['bytes'], 'took_ms': r['took_ms']}
    if r['effective'] != url:
        row['redirected_to'] = r['effective']
    if r.get('error'):
        row['error'] = r['error']
    row['ok'] = (r['status'] == 200)
    return row


def check_many(urls, workers=12):
    urls = list(dict.fromkeys(u for u in urls if u))
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(check, urls))


# ---------------------------------------------------------------- parsing

HREF = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.I)
JSURL = re.compile(r'url\s*:\s*["\']([^"\']+)["\']')
MODSRC = re.compile(r'<script[^>]+type\s*=\s*["\']module["\'][^>]*src\s*=\s*["\']([^"\']+)["\']',
                    re.I)
IMPORT = re.compile(r'(?:^|\n)\s*(?:import|export)[^\n;]*?from\s*["\']([^"\']+)["\']')
BASEURL = re.compile(r'base_url["\']?\s*:\s*["\']([^"\']+)["\']')

SKIP_SCHEME = ('mailto:', 'javascript:', 'data:', 'tel:', '#')


def links_from(html, base):
    """Every route the page names, absolutised. Anchors and off-site hosts dropped."""
    out = []
    for m in list(HREF.finditer(html)) + list(JSURL.finditer(html)):
        raw = m.group(1).strip()
        if not raw or raw.startswith(SKIP_SCHEME):
            continue
        u = urllib.parse.urljoin(base, raw)
        if not u.startswith(('http://', 'https://')):
            continue
        host = urllib.parse.urlparse(u).netloc
        # Only the estate's own origins. A third-party CDN going down is not our finding.
        if host not in ('globalgrid2050.com', 'www.globalgrid2050.com', 'ventusltd.github.io'):
            continue
        out.append(u.split('#')[0])
    return list(dict.fromkeys(out))


def import_closure(page_url, html, depth=2):
    """The modules the page ACTUALLY loads, followed `depth` levels of `import ... from`.

    This is the discriminator between a dead module that ships and a dead module that is
    merely present in the directory. Only what is reachable from a <script type=module>
    reaches a browser.
    """
    seen, sources = {}, {}
    frontier = [urllib.parse.urljoin(page_url, m.group(1)) for m in MODSRC.finditer(html)]
    for _ in range(depth + 1):
        nxt = []
        for u in frontier:
            if u in seen:
                continue
            r = fetch(u)
            seen[u] = r['status']
            if r['status'] != 200:
                continue
            src = text(r)
            sources[u] = src
            for m in IMPORT.finditer(src):
                spec = m.group(1)
                if spec.startswith(('.', '/')):
                    nxt.append(urllib.parse.urljoin(u, spec))
        frontier = nxt
        if not frontier:
            break
    return seen, sources


def receivers_in(obj, path='$'):
    """Every receiver block in a manifest, found BY SHAPE rather than by key path."""
    found = []
    if isinstance(obj, dict):
        if 'golden_repd_ref' in obj or 'browser_sentinels' in obj:
            found.append((path, obj))
        for k, v in obj.items():
            found += receivers_in(v, '%s.%s' % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found += receivers_in(v, '%s[%d]' % (path, i))
    return found


def sentinel_urls(rec):
    """golden + browser sentinels, expanded. An empty expected_url is a NEGATIVE sentinel."""
    base = rec.get('base_url') or ''
    q = rec.get('query_parameter') or 'repd_ref'
    refs = []
    if rec.get('golden_repd_ref'):
        refs.append(('golden', str(rec['golden_repd_ref'])))
    for s in (rec.get('browser_sentinels') or []):
        refs.append(('browser', str(s)))
    if not base:
        return [], refs
    return ['%s?%s=%s' % (base.rstrip('/') + '/', q, r) for _, r in refs], refs


# ---------------------------------------------------------------- a release

def crawl_release(name, page_url, manifest_names=('build-manifest.json',
                                                  'release-manifest.json')):
    """One published release: its page, its routes, its declared and its shipped sentinels."""
    out = {'release': name, 'page': page_url}
    page = fetch(page_url)
    out['page_status'] = page['status']
    if page['status'] != 200:
        # Published on disk, absent from the origin. That IS the finding - record and stop.
        out['state'] = 'page-unreachable'
        out['routes'] = []
        out['sentinels'] = []
        return out

    html = text(page)
    out['page_bytes'] = page['bytes']

    # Routes the page names.
    out['routes'] = check_many(links_from(html, page_url))

    # What the page actually loads.
    modules, sources = import_closure(page_url, html)
    out['modules'] = [{'url': u, 'status': s} for u, s in sorted(modules.items())]
    shipped_bases = sorted({b for src in sources.values() for b in BASEURL.findall(src)})
    out['shipped_base_urls'] = shipped_bases

    # What the manifests declare.
    declared = []
    for mn in manifest_names:
        mu = urllib.parse.urljoin(page_url, mn)
        r = fetch(mu)
        if r['status'] != 200:
            continue
        try:
            doc = json.loads(text(r))
        except Exception:
            out.setdefault('manifest_unparseable', []).append(mu)
            continue
        for where, rec in receivers_in(doc):
            declared.append({'manifest': mn, 'at': where, 'base_url': rec.get('base_url'),
                             'release_id': rec.get('release_id'), 'rec': rec})
    out['declared_receivers'] = [{k: d[k] for k in ('manifest', 'at', 'base_url', 'release_id')}
                                 for d in declared]

    # Sentinels. Every declared receiver is expanded and checked; each is then labelled
    # shipped or stale by whether its base appears in a module the page imports.
    # The base a module actually carries is a route in its own right. Checking it directly
    # means a release whose manifest declares no base_url at all is still measured, instead
    # of silently contributing zero sentinels and reading as clean.
    out['shipped_base_checks'] = check_many(shipped_bases)

    rows = []
    for d in declared:
        base = d['base_url'] or ''
        # A receiver that names refs but no base is expanded against what the page ships,
        # because that is the URL the user's click produces.
        if not base:
            atlas = [b for b in shipped_bases if '/gridatlas/' in b]
            if len(atlas) == 1:
                base = atlas[0]
                d = dict(d, rec=dict(d['rec'], base_url=base), base_url=base,
                         at=d['at'] + ' (base from the shipped module)')
        urls, refs = sentinel_urls(d['rec'])
        is_shipped = any(base and base.rstrip('/') == b.rstrip('/') for b in shipped_bases)
        for (kind, ref), row in zip(refs, check_many(urls)):
            row.update({'ref': ref, 'kind': kind, 'base_url': base,
                        'declared_at': ['%s%s' % (d['manifest'], d['at'])],
                        'shipped': is_shipped})
            rows.append(row)

    # The same sentinel is often declared in two manifests. It is ONE URL and one reading;
    # counting it twice would inflate "8 of 8 dead" into nine and make the report arguable.
    merged = {}
    for r in rows:
        prev = merged.get(r['url'])
        if prev:
            prev['declared_at'] += r['declared_at']
            prev['shipped'] = prev['shipped'] or r['shipped']
        else:
            merged[r['url']] = r
    rows = list(merged.values())
    out['sentinels'] = rows

    live = [s for s in rows if s['shipped']]
    out['sentinel_totals'] = {
        'declared': len(rows),
        'declared_dead': sum(1 for s in rows if not s['ok']),
        'shipped': len(live),
        'shipped_dead': sum(1 for s in live if not s['ok']),
    }
    out['routes'] += out['shipped_base_checks']
    dead_routes = sum(1 for r in out['routes'] if not r['ok'])
    out['state'] = ('sentinels-dead' if out['sentinel_totals']['shipped_dead']
                    else ('routes-dead' if dead_routes else 'clean'))
    return out


# ---------------------------------------------------------------- surfaces

def list_json(url, key=None):
    r = fetch(url)
    if r['status'] != 200:
        return None
    try:
        return json.loads(text(r))
    except Exception:
        return None


def api_dirs(repo, path):
    """Subdirectory names under `path`, read from the repository rather than the origin.

    GitHub Pages serves no directory listing, so a crawler that discovers releases by
    scraping `/releases/` finds nothing and reports a clean surface - the worst kind of
    wrong answer, a green light that measured nothing. The repository is the record of
    what was PUBLISHED; the origin is the record of what is SERVED. Discovering from the
    first and checking against the second is what makes "published but not served" a
    finding this crawl can see at all.
    """
    tok = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    url = 'https://api.github.com/repos/%s/contents/%s' % (repo, path)
    req = urllib.request.Request(url, headers={
        'Accept': 'application/vnd.github+json', 'User-Agent': UA,
        **({'Authorization': 'Bearer ' + tok} if tok else {})})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            items = json.load(r)
    except Exception as e:
        print('api_dirs %s/%s: %s' % (repo, path, str(e)[:100]), file=sys.stderr)
        return []
    return sorted((i['name'] for i in items if i.get('type') == 'dir'), reverse=True)


def surface_globalgrid2050():
    page = fetch(GG)
    rel = {'release': 'homepage', 'page': GG, 'page_status': page['status']}
    if page['status'] != 200:
        rel['state'] = 'page-unreachable'
        rel['routes'] = []
        rel['sentinels'] = []
        return [rel]
    html = text(page)
    rel['page_bytes'] = page['bytes']
    rel['routes'] = check_many(links_from(html, GG))
    rel['sentinels'] = []
    # The V8 catalogue sentinel: a byte-exact string the compiler requires to occur once.
    v8 = './repd_grid_atlasv8/'
    rel['v8_catalogue_route_occurrences'] = html.count(v8)
    rel['v8_catalogue_route_ok'] = (html.count(v8) == 1)
    rel['pipelinenews_rows'] = len(re.findall(r'\./pipelinenews_intelligence/(\d{12})/', html))
    dead = sum(1 for r in rel['routes'] if not r['ok'])
    rel['state'] = 'routes-dead' if dead else 'clean'
    return [rel]


def surface_pipelinenews_intel():
    """The 28 snapshots, discovered from the homepage catalogue rather than from disk."""
    page = fetch(GG)
    gens = sorted(set(re.findall(r'\./pipelinenews_intelligence/(\d{12})/', text(page))),
                  reverse=True)
    return [crawl_release(g, '%spipelinenews_intelligence/%s/' % (GG, g)) for g in gens]


def surface_gridatlas_atlas():
    out = []
    # The pointer of record, and the pointer that is known to be stale. Both are read; the
    # stale one is reported as its own row rather than expanded into dead URLs.
    cur = list_json(GA + 'atlas/current.json')
    out.append({'release': 'atlas/current.json', 'page': GA + 'atlas/current.json',
                'page_status': 200 if cur else 0,
                'routes': check_many([GA + 'atlas/', GA + 'atlas/world/', GA,
                                      GA + 'state/live-set.json']),
                'sentinels': [],
                'generation': (cur or {}).get('generation'),
                'live_route': (cur or {}).get('live_route'),
                'state': 'clean' if cur else 'page-unreachable'})

    stale = list_json(GA + 'releases/current-v3.json')
    if stale:
        route = stale.get('route') or ''
        live = stale.get('live_url') or ''
        rows = check_many([u for u in (live,) if u])
        out.append({'release': 'releases/current-v3.json (known stale pointer)',
                    'page': GA + 'releases/current-v3.json', 'page_status': 200,
                    'routes': rows, 'sentinels': [], 'declared_route': route,
                    'state': 'routes-dead' if any(not r['ok'] for r in rows) else 'clean'})

    # Every immutable atlas release shell the repository publishes.
    rel_ids = [d for d in api_dirs('Ventusltd/gridatlas', 'atlas/releases')
               if re.match(r'^\d{12}-atlas-v9$', d)]
    for rid in rel_ids:
        out.append(crawl_release(rid, '%satlas/releases/%s/' % (GA, rid),
                                 manifest_names=('release-manifest.json',
                                                 'build-manifest.json')))
        # The dead shape, checked explicitly so its death is a measurement rather than lore.
        dead = '%s%s/' % (GA, rid)
        out[-1].setdefault('legacy_route', check(dead))
    return out


def surface_pipelinenews_releases():
    """Every release the repository publishes, checked against what the origin serves.

    These two sets are currently different, and the difference is the point: the Pages
    deploy has been failing since 31 August, so releases exist in the repository that the
    origin has never served. Each of those is reported as `page-unreachable`, not skipped.
    """
    dirs = [d for d in api_dirs('Ventusltd/pipelinenews', 'releases')
            if re.match(r'^\d{12}-pipelinenews$', d)]
    return [crawl_release(d, '%sreleases/%s/' % (PN, d)) for d in dirs]


def run_surface(name):
    t0 = time.time()
    fn = {'globalgrid2050': surface_globalgrid2050,
          'pipelinenews-intel': surface_pipelinenews_intel,
          'gridatlas-atlas': surface_gridatlas_atlas,
          'pipelinenews-releases': surface_pipelinenews_releases}[name]
    rels = fn()
    routes = sum(len(r.get('routes') or []) for r in rels)
    dead_routes = sum(1 for r in rels for x in (r.get('routes') or []) if not x['ok'])
    sent = sum(len(r.get('sentinels') or []) for r in rels)
    dead_sent = sum(1 for r in rels for x in (r.get('sentinels') or []) if not x['ok'])
    dead_shipped = sum(1 for r in rels for x in (r.get('sentinels') or [])
                       if x.get('shipped') and not x['ok'])
    return {
        'schema': 'ventus.estate-link-crawl.v1',
        'surface': name,
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'took_s': round(time.time() - t0, 1),
        'totals': {'releases': len(rels), 'routes': routes, 'routes_dead': dead_routes,
                   'sentinels': sent, 'sentinels_dead': dead_sent,
                   'sentinels_dead_and_shipped': dead_shipped,
                   'pages_unreachable': sum(1 for r in rels
                                            if r.get('state') == 'page-unreachable')},
        'releases': rels,
    }


# ---------------------------------------------------------------- collation

def collate(paths):
    shards = []
    for p in sorted(paths):
        with open(p, encoding='utf-8') as f:
            shards.append(json.load(f))
    t = Counter()
    for s in shards:
        for k, v in s['totals'].items():
            t[k] += v
    return {'schema': 'ventus.estate-link-crawl.collated.v1',
            'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'surfaces': [s['surface'] for s in shards],
            'totals': dict(t), 'shards': shards}


def board(c):
    L = []
    A = L.append
    A('# Published-release link and sentinel crawl')
    A('')
    A('Crawled from GitHub Actions against the LIVE origins, one runner per surface.')
    A('INFORMATIONAL: the job exits 0 on every finding. A 404 below is a fact to read,')
    A('not an alarm that mailed anyone.')
    A('')
    A('- crawled at: `%s`' % c['generated_at'])
    t = c['totals']
    A('- releases crawled: %d (%d whose page did not answer)'
      % (t.get('releases', 0), t.get('pages_unreachable', 0)))
    A('- routes checked: %d, dead: %d' % (t.get('routes', 0), t.get('routes_dead', 0)))
    A('- sentinels checked: %d, dead: %d, **dead AND shipped: %d**'
      % (t.get('sentinels', 0), t.get('sentinels_dead', 0),
         t.get('sentinels_dead_and_shipped', 0)))
    A('')
    A('A sentinel is *shipped* when its base URL appears in a module the page actually')
    A('imports. A dead sentinel that is only *declared* is a stale record in a manifest.')
    A('A dead sentinel that is shipped is what a user gets when they click.')
    A('')

    for s in c['shards']:
        st = s['totals']
        A('## `%s` - %d releases, %d/%d routes dead, %d/%d sentinels dead (%d shipped)'
          % (s['surface'], st['releases'], st['routes_dead'], st['routes'],
             st['sentinels_dead'], st['sentinels'], st['sentinels_dead_and_shipped']))
        A('')
        A('crawled in %ss' % s['took_s'])
        A('')
        bad = [r for r in s['releases'] if r.get('state') != 'clean']
        if not bad:
            A('Every release on this surface answered 200 on every route and sentinel.')
            A('')
            continue
        A('| release | state | page | routes dead | sentinels dead (shipped) |')
        A('|---|---|---|---|---|')
        for r in bad:
            sd = r.get('sentinel_totals') or {}
            A('| `%s` | %s | %s | %d/%d | %d/%d (%d) |'
              % (r['release'], r.get('state'), r.get('page_status'),
                 sum(1 for x in (r.get('routes') or []) if not x['ok']),
                 len(r.get('routes') or []),
                 sd.get('declared_dead', 0), sd.get('declared', 0),
                 sd.get('shipped_dead', 0)))
        A('')
        # The dead URLs themselves, deduplicated, so the report names the route not the count.
        dead = Counter()
        for r in s['releases']:
            for x in (r.get('routes') or []) + (r.get('sentinels') or []):
                if not x['ok']:
                    dead['%s %s' % (x['status'], x['url'])] += 1
        if dead:
            A('<details><summary>%d distinct dead URLs on this surface</summary>'
              % len(dead))
            A('')
            A('| status + url | seen in N releases |')
            A('|---|---|')
            for k, n in dead.most_common(60):
                code, u = k.split(' ', 1)
                A('| `%s` `%s` | %d |' % (code, u, n))
            if len(dead) > 60:
                A('| ... %d more | |' % (len(dead) - 60))
            A('')
            A('</details>')
            A('')
    return '\n'.join(L) + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--surface', choices=SURFACES)
    ap.add_argument('--collate', nargs='*')
    ap.add_argument('--out', default='')
    ap.add_argument('--board', default='')
    a = ap.parse_args()

    if a.collate is not None:
        paths = []
        for p in a.collate:
            paths += glob.glob(p)
        result = collate(paths)
        if a.board:
            os.makedirs(os.path.dirname(a.board) or '.', exist_ok=True)
            with open(a.board, 'w', encoding='utf-8', newline='\n') as f:
                f.write(board(result))
    elif a.surface:
        result = run_surface(a.surface)
    else:
        ap.error('give --surface or --collate')

    if a.out:
        with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(result, f, indent=1)
            f.write('\n')

    t = result['totals']
    print('%s: releases %d · routes %d (%d dead) · sentinels %d (%d dead, %d of them shipped)'
          % (result.get('surface') or 'collated', t.get('releases', 0), t.get('routes', 0),
             t.get('routes_dead', 0), t.get('sentinels', 0), t.get('sentinels_dead', 0),
             t.get('sentinels_dead_and_shipped', 0)), file=sys.stderr)

    # Informational. Always 0. See the module docstring before changing this.
    return 0


if __name__ == '__main__':
    sys.exit(main())

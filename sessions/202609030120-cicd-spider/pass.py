#!/usr/bin/env python3
"""cicd-spider pass driver.

Usage:  python pass.py            run one full pass, update spider-state.json,
                                  print ONLY what changed
        python pass.py --quick    HEAD + gates only, skip cvaa and crosslink

Read-only on every repository except this directory. Never writes outside
sessions/202609030120-cicd-spider/. cvaa is always invoked with --no-write so
the run does not touch cvaa/vaccines/last-fired.json.

Context diet: this prints drift, not status. Silence means nothing moved.
"""
import json, os, subprocess, sys, datetime, collections, re, concurrent.futures as cf

GH   = r"C:\Users\vikra\OneDrive\Documents\GitHub"
HERE = os.path.dirname(os.path.abspath(__file__))
STATE= os.path.join(HERE, 'spider-state.json')
QUICK= '--quick' in sys.argv

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')

def git(d, *a):
    try:
        return subprocess.run(['git','-C',os.path.join(GH,d)]+list(a),
                              capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception:
        return None

def run(cwd, argv, timeout=600):
    try:
        p = subprocess.run(argv, cwd=os.path.join(GH,cwd), capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, (p.stdout or '') + (p.stderr or '')
    except subprocess.TimeoutExpired:
        return 124, 'TIMEOUT'
    except Exception as e:
        return 125, str(e)

st = json.load(open(STATE))
drift = []
def D(sev, msg): drift.append(f'[{sev}] {msg}')

# ---------------------------------------------------------------- 1. HEADs
repos = sorted(st['heads'])
new_heads = {}
for d in repos:
    st_p = git(d,'status','--porcelain') or ''
    new_heads[d] = {
        "head": git(d,'rev-parse','HEAD'),
        "branch": git(d,'rev-parse','--abbrev-ref','HEAD'),
        "committed_at": git(d,'log','-1','--format=%cI'),
        "subject": (git(d,'log','-1','--format=%s') or '')[:110],
        "dirty_files": len([l for l in st_p.split('\n') if l.strip()]),
        "commit_count": st['heads'][d].get('commit_count'),
        "workflows": st['heads'][d].get('workflows'),
    }
    old = st['heads'][d]
    if old['head'] != new_heads[d]['head']:
        D('HEAD', f"{d} {old['head'][:7]} -> {new_heads[d]['head'][:7]} "
                  f"[{new_heads[d]['branch']}] {new_heads[d]['subject']}")

# ------------------------------------------------------------------ 2. gates
# The command string in spider-state.json is authoritative and already carries
# every required argument. RH2: a gate run without its arguments prints a usage
# string and looks like a failure. Never re-derive these.
GATE_ARGV = {
 "gridatlas__run-current":              ("gridatlas",   ['node','tools/proofs/run-current.mjs']),
 "datagridgb__verify-connection-points":("data-grid-gb",['python','derived/verify_connection_points.py']),
 "datagridgb__verify-phase0-acceptance":("data-grid-gb",['python','derived/verify_phase0_acceptance.py']),
 "datagridgb__verify-product":          ("data-grid-gb",['python','chatgpt/verify_product.py','chatgpt/derived/etys-2025.normalized.json']),
 "pipelinenews__render_proof":          ("pipelinenews",['node','tools/intelligence/render_proof.mjs','@RELEASE@']),
 "pipelinenews__sector_render_proof":   ("pipelinenews",['node','tools/intelligence/sector_render_proof.mjs','@RELEASE@']),
 "pipelinenews__surface_truth_proof":   ("pipelinenews",['node','tools/intelligence/surface_truth_proof.mjs','@RELEASE@']),
 "gdm__verify":                         ("grid-distance-maths",['node','test/verify.mjs']),
 "gdm__verify_nearest":                 ("grid-distance-maths",['node','test/verify_nearest.mjs']),
 "gdm__verify_parity":                  ("grid-distance-maths",['python','test/verify_parity.py']),
 "dgbe__price_decade_rollup":           ("data-gb-electricity",['python','derived/verify_price_decade_rollup.py']),
 "gg2050__verify_published_versions":   ("globalgrid2050",['python','scripts/verify_published_versions.py']),
}
# the newest release directory is the one the proofs must be pointed at
rel = sorted(x for x in os.listdir(os.path.join(GH,'pipelinenews','releases'))
             if re.match(r'^\d{12}-pipelinenews$', x))
RELEASE = rel[-1] if rel else None
if RELEASE and RELEASE != st.get('pipelinenews_release'):
    D('REL', f"pipelinenews release {st.get('pipelinenews_release')} -> {RELEASE}")

def tree_state(repo):
    """RH6. Three other agents are writing to these repositories continuously.
    A gate run against a dirty tree measures a half-written edit, not a repo,
    and reporting it as a failure spends attention a real failure then cannot
    get. Dirty is UNMEASURABLE, which is a third state, not a failure."""
    return git(repo,'rev-parse','HEAD'), len([l for l in (git(repo,'status','--porcelain') or '').split('\n') if l.strip()])

def one_gate(item):
    gid,(repo,argv) = item
    argv = [RELEASE if a=='@RELEASE@' else a for a in argv]
    if '@RELEASE@' in argv or (RELEASE is None and any('proof' in a for a in argv)):
        return gid, 'not-runnable-locally', 'no pipelinenews release directory'
    head0, dirty0 = tree_state(repo)
    if dirty0:
        return gid, 'unmeasurable-dirty-tree', f'{repo} has {dirty0} uncommitted path(s); another agent is mid-write'
    rc,out = run(repo, argv)
    # and re-check AFTER: a commit or an edit landing mid-run is equally fatal
    head1, dirty1 = tree_state(repo)
    if head1 != head0 or dirty1:
        return gid, 'unmeasurable-dirty-tree', f'{repo} moved during the run ({head0[:7]}->{head1[:7]}, dirty {dirty1})'
    fails = []
    seen = False
    for line in out.split('\n'):
        if line.strip() == 'FAILURES': seen = True; continue
        if seen and line.strip(): fails.append(line.strip())
    detail = ('; '.join(fails)[:190] if fails
              else ([l for l in out.strip().split('\n') if l.strip()][-1:] or [''])[0][:190])
    return gid, ('pass' if rc==0 else 'FAIL'), detail

gates = dict(st['gates'])
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for gid, state_now, detail in ex.map(one_gate, GATE_ARGV.items()):
        prev = gates.get(gid,{}).get('state')
        gates.setdefault(gid,{}).update(state=state_now, detail=detail, last_run=now())
        # An unmeasurable pass is not a transition in either direction. Never
        # report red or green across one; carry the previous verdict forward.
        if state_now == 'unmeasurable-dirty-tree':
            gates[gid]['state'] = prev or state_now
            gates[gid]['last_unmeasurable'] = now()
            continue
        if prev != state_now and prev != 'unmeasurable-dirty-tree':
            if state_now == 'FAIL':
                gates[gid]['first_seen'] = now()
                D('RED',   f"{gid}: {prev} -> FAIL :: {detail}")
            elif prev == 'FAIL':
                D('GREEN', f"{gid}: FAIL -> {state_now} :: {detail}")
            else:
                D('GATE',  f"{gid}: {prev} -> {state_now}")

# --------------------------------------------------------------- 3. cvaa
if not QUICK:
    # RH11: measure with the PUBLISHED cvaa, never the working copy beside it.
    # The local copy was two commits ahead of origin and carried an untracked
    # 28th vaccine, so three passes of estate numbers described a ruler nobody
    # else has. Refresh a clean clone each pass and record the commit measured.
    CV = os.environ.get('CVAA_CLEAN') or os.path.join(HERE, '.cvaa-clean')
    if not os.path.isdir(os.path.join(CV,'.git')):
        subprocess.run(['git','clone','-q','--no-tags',
                        'https://github.com/Ventusltd/cvaa.git', CV], timeout=600)
    else:
        subprocess.run(['git','-C',CV,'fetch','-q','--no-tags','origin','main'], timeout=300)
        subprocess.run(['git','-C',CV,'reset','-q','--hard','origin/main'], timeout=120)
    cv_head = subprocess.run(['git','-C',CV,'rev-parse','HEAD'],
                             capture_output=True, text=True).stdout.strip()
    # The RULER is the ACTIVE VACCINE SET, not the commit. cvaa can be committed
    # to for a hundred reasons that leave every rule identical -- a workflow fix,
    # a README -- and firing on the SHA would cry ruler-change at each of them,
    # which is the same noise in the other direction. Compare the set: active
    # vaccine slugs and their content hashes, superseded ones excluded.
    import hashlib, glob as _glob
    ruler = {}
    for f in sorted(_glob.glob(os.path.join(CV,'vaccines','*.md'))):
        body = open(f,'rb').read()
        text = body.decode('utf-8','replace').replace(chr(13)+chr(10), chr(10))
        if re.search(r'^superseded_by:', text, re.M): continue
        ruler[os.path.basename(f)] = hashlib.sha256(text.encode()).hexdigest()[:12]
    prev_ruler = st['cvaa'].get('ruler') or {}
    if prev_ruler and ruler != prev_ruler:
        added   = sorted(set(ruler) - set(prev_ruler))
        removed = sorted(set(prev_ruler) - set(ruler))
        changed = sorted(k for k in set(ruler) & set(prev_ruler) if ruler[k] != prev_ruler[k])
        D('CVAA-RULER', f"active vaccine set changed ({len(prev_ruler)} -> {len(ruler)}): "
                        f"+{added} -{removed} ~{changed}; a findings delta this pass may be the ruler, not the repo")
    elif cv_head != st['cvaa'].get('measured_with_commit'):
        D('CVAA-COMMIT', f"cvaa published HEAD -> {cv_head[:7]}, active vaccine set UNCHANGED "
                         f"({len(ruler)} rules); any findings delta is real")
    st['cvaa']['ruler'] = ruler
    st['cvaa']['active_vaccines'] = len(ruler)
    st['cvaa']['measured_with_commit'] = cv_head

    def one_cvaa(d):
        # RH16. The dirty-tree guard was applied to gates and not to cvaa, which
        # reads the same working copies. A findings delta measured while an agent
        # is mid-write is the same false signal RH6 was written to stop.
        h0, dirty0 = tree_state(d)
        if dirty0:
            return d, None, f'{dirty0} uncommitted path(s)'
        rc,out = run('.', ['node', os.path.join(CV,'inoculate.mjs'),
                           os.path.join(GH,d), '--json','--no-write'], timeout=900)
        h1, dirty1 = tree_state(d)
        if h1 != h0 or dirty1:
            return d, None, f'tree moved during the run ({h0[:7]}->{h1[:7]}, dirty {dirty1})'
        for line in out.split('\n'):
            line = line.strip()
            if line.startswith('{') and '"schema"' in line:
                try: return d, json.loads(line), None
                except Exception: pass
        return d, None, 'no JSON record'
    cv = {}
    unmeasurable = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d,obj,why in ex.map(one_cvaa, repos):
            if obj is None:
                if why and ('uncommitted' in why or 'moved during' in why):
                    unmeasurable.append(d)          # not a finding, not a change
                else:
                    D('RUNNER', f"cvaa produced no JSON for {d} ({why}) - suspect the runner, not the repo")
                continue
            cv[d] = obj
    if unmeasurable:
        D('CVAA-SKIP', f"{len(unmeasurable)} repo(s) mid-write, not measured: {', '.join(sorted(unmeasurable))}")
    prev = st['cvaa']['per_repo']
    for d,obj in cv.items():
        if d in prev and prev[d]['findings'] != obj['findings']:
            D('CVAA', f"{d} findings {prev[d]['findings']} -> {obj['findings']}")
    # RH18. Comparing incidence COUNTS across passes is only valid when the
    # denominator is the same, and RH16 made it vary: three repos mid-write meant
    # "14 -> 11 of 15" and every one of those was a repo that was not looked at.
    # A wrong denominator is worse than a wrong finding (RH11), and I shipped one
    # as a side effect of fixing something else. So: diff PER REPOSITORY, over
    # the repos measured in BOTH passes, and name the repo rather than a count.
    # RH19. git status compares through .gitattributes normalisation, so a tree
    # can be git-clean while the bytes on disk are CRLF and the blob is LF. Any
    # verdict that depends on file BYTES is then wrong in both directions: the
    # working copy invented pointer-verifies on gridatlas and concealed
    # on-ledger-commits. Vaccines that hash or byte-compare are therefore not
    # reportable from a workspace with CRLF drift; they are dropped, and the
    # count of what was dropped is stated rather than silently omitted.
    BYTE_SENSITIVE = {'pointer-verifies', 'disk-is-not-what-ships',
                      'registry-integrity', 'attestation-freshness'}
    crlf = {}
    for d in cv:
        out = git(d, 'ls-files', '--eol') or ''
        crlf[d] = sum(1 for l in out.splitlines() if 'w/crlf' in l or 'w/mixed' in l)
    st['cvaa']['crlf_drift'] = crlf
    now_fail = {d: sorted(r['vaccine'] for r in o['results'] if r['state'] != 'immune'
                          and not (crlf.get(d) and r['vaccine'] in BYTE_SENSITIVE))
                for d, o in cv.items()}
    suppressed = sorted(d for d in cv if crlf.get(d) and
                        any(r['vaccine'] in BYTE_SENSITIVE and r['state'] != 'immune'
                            for r in cv[d]['results']))
    if suppressed:
        D('BYTE-UNSAFE', f"{len(suppressed)} repo(s) have CRLF drift, so byte-dependent "
                         f"vaccines are not reportable from the workspace: {', '.join(suppressed)}"
                         " - re-measure in a clean clone")
    was_fail = st['cvaa'].get('not_immune') or {}
    comparable = sorted(set(now_fail) & set(was_fail))
    for d in comparable:
        gained = sorted(set(now_fail[d]) - set(was_fail[d]))
        lost   = sorted(set(was_fail[d]) - set(now_fail[d]))
        for v in gained: D('VACCINE-RED',   f'{d} now fails {v}')
        for v in lost:   D('VACCINE-GREEN', f'{d} no longer fails {v}')
    st['cvaa']['not_immune'] = dict(was_fail, **now_fail)
    st['cvaa']['incidence'] = dict(collections.Counter(
        v for d in st['cvaa']['not_immune'] for v in st['cvaa']['not_immune'][d]))
    st['cvaa']['incidence_denominator'] = len(st['cvaa']['not_immune'])
    if len(comparable) != len(now_fail):
        D('VACCINE-BASE', f'{len(now_fail)-len(comparable)} repo(s) had no prior vaccine '
                          'record; baselined silently, not reported as change')
    # carry forward the last good figures for anything not measured this pass,
    # so an unmeasured repository can never read as a change next pass either
    carried = {k:v for k,v in prev.items() if k not in cv}
    st['cvaa']['per_repo'] = dict(carried,
        **{k:{"status":v['status'],"findings":v['findings']} for k,v in cv.items()})

    for d,obj in cv.items():
        wf = obj['context']['workflows']
        if st['heads'][d].get('workflows') not in (None, wf):
            D('COUNT', f"{d} workflow files {st['heads'][d]['workflows']} -> {wf}")
        new_heads[d]['workflows'] = wf
        new_heads[d]['commit_count'] = obj['context']['commit_count']

# ------------------------------------------------- 4. CI state, from the API
# RH6 again: the Actions API reports what CI ran against a COMMIT. It is the
# only CI signal here that a live working tree cannot corrupt. 7 calls a pass
# against a 60/hour unauthenticated budget.
import urllib.request
CI_REPOS = ['gridatlas','pipelinenews','globalgrid2050','data-grid-gb','cvaa','companies','data-gridatlas']
def ci(repo):
    try:
        req = urllib.request.Request(
            f'https://api.github.com/repos/Ventusltd/{repo}/actions/runs?per_page=25',
            headers={'Accept':'application/vnd.github+json','User-Agent':'cicd-spider'})
        with urllib.request.urlopen(req, timeout=45) as r:
            d = json.loads(r.read())
    except Exception as e:
        return repo, None, str(e)[:80]
    # RH20. A CI failure on a feature branch is another agent's work in
    # progress, not estate drift. gridatlas b67d0a0 on
    # codex/202609030251-grid-data-v9-89 failed its first run and I was about to
    # report it - the same mistake as the pass-2 dirty-tree red, one level out.
    # Only the default branch describes the estate.
    latest = {}
    for x in d.get('workflow_runs',[]):
        if x.get('head_branch') != 'main': continue
        latest.setdefault(x['name'], x)
    return repo, {n:{'conclusion':x['conclusion'],'head_sha':x['head_sha'][:7],
                     'at':x['updated_at']} for n,x in latest.items()}, None
# RH15. The 60/hour unauthenticated budget is SHARED - by four agents on this
# machine and by the estate's own gates, which come from the same IP. At 02:02Z
# globalgrid2050/scripts/verify_published_versions.py printed
#   skipped: pipelinenews lineage head: HTTP Error 403: rate limit exceeded
# because the budget was at 0/60. A standing observer that exhausts the budget
# blinds the gates it is observing, and the gate SKIPS rather than failing -
# and a skip is not a pass. So: check the free rate_limit endpoint first, leave
# a floor for everyone else, and sample the busy repos more often than the
# quiet ones.
def budget():
    try:
        req = urllib.request.Request('https://api.github.com/rate_limit',
                                     headers={'User-Agent':'cicd-spider'})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())['resources']['core']['remaining']
    except Exception:
        return 0
FLOOR = 25
remaining = budget()
moved = {d for d in repos if st['heads'][d]['head'] != new_heads[d]['head']}
sample = [r for r in CI_REPOS if r in moved] or CI_REPOS[:3]
if remaining < FLOOR + len(sample):
    D('API-BUDGET', f'{remaining}/60 left, floor {FLOOR}: CI not sampled this pass '
                    f'so the estate gates keep their share')
    sample = []
st['github_api']['remaining_at_pass'] = remaining
st['github_api']['ci_repos_sampled'] = sample

prev_ci = st.get('ci', {})
new_ci = dict(prev_ci)
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    for repo, res, err in ex.map(ci, sample):
        if res is None:
            D('API', f'{repo} actions API unreachable: {err}')
            new_ci[repo] = prev_ci.get(repo, {})
            continue
        new_ci[repo] = res
        old = prev_ci.get(repo, {})
        # RH10: a first observation is a baseline, not a transition. Without
        # this, every long-standing failure is announced as though it just broke.
        if not old:
            n = sum(1 for c in res.values() if c['conclusion'] == 'failure')
            if n: D('CI-BASE', f'{repo}: {n} workflow(s) already failing at first observation')
            continue
        for wf, cur in res.items():
            was = old.get(wf, {}).get('conclusion')
            if was == cur['conclusion']: continue
            if cur['conclusion'] == 'failure':
                D('CI-RED',   f"{repo} :: {wf[:60]} -> failure @{cur['head_sha']} {cur['at']}")
            elif was == 'failure' and cur['conclusion'] == 'success':
                D('CI-GREEN', f"{repo} :: {wf[:60]} failure -> success @{cur['head_sha']}")
st['ci'] = new_ci
st['github_api']['calls_used_last_pass'] = len(sample) + 1

# ------------------------------------------------------------- 5. write out
st['heads'] = new_heads
st['gates'] = gates
st['pass']  = st['pass'] + 1
st['pass_completed_utc'] = now()
st['pipelinenews_release'] = RELEASE
st['last_pass_drift'] = drift
tmp = STATE + '.tmp'
json.dump(st, open(tmp,'w'), indent=1)
os.replace(tmp, STATE)

print(f"pass {st['pass']}  {now()}  {'quick' if QUICK else 'full'}")
if drift:
    print(f"{len(drift)} drift item(s):")
    for x in drift: print('  '+x)
else:
    print('no drift')

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

def one_gate(item):
    gid,(repo,argv) = item
    argv = [RELEASE if a=='@RELEASE@' else a for a in argv]
    if '@RELEASE@' in argv or (RELEASE is None and any('proof' in a for a in argv)):
        return gid, 'not-runnable-locally', 'no pipelinenews release directory'
    rc,out = run(repo, argv)
    tail = [l for l in out.strip().split('\n') if l.strip()][-1:] or ['']
    return gid, ('pass' if rc==0 else 'FAIL'), tail[0][:190]

gates = dict(st['gates'])
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for gid, state_now, detail in ex.map(one_gate, GATE_ARGV.items()):
        prev = gates.get(gid,{}).get('state')
        gates.setdefault(gid,{}).update(state=state_now, detail=detail, last_run=now())
        if prev != state_now:
            if state_now == 'FAIL':
                gates[gid]['first_seen'] = now()
                D('RED',   f"{gid}: {prev} -> FAIL :: {detail}")
            elif prev == 'FAIL':
                D('GREEN', f"{gid}: FAIL -> {state_now} :: {detail}")
            else:
                D('GATE',  f"{gid}: {prev} -> {state_now}")

# --------------------------------------------------------------- 3. cvaa
if not QUICK:
    def one_cvaa(d):
        rc,out = run('.', ['node', os.path.join(GH,'cvaa','inoculate.mjs'),
                           os.path.join(GH,d), '--json','--no-write'], timeout=900)
        for line in out.split('\n'):
            line = line.strip()
            if line.startswith('{') and '"schema"' in line:
                try: return d, json.loads(line)
                except Exception: pass
        return d, None
    cv = {}
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for d,obj in ex.map(one_cvaa, repos):
            if obj is None:
                D('RUNNER', f"cvaa produced no JSON for {d} - suspect the runner, not the repo")
                continue
            cv[d] = obj
    prev = st['cvaa']['per_repo']
    for d,obj in cv.items():
        if d in prev and prev[d]['findings'] != obj['findings']:
            D('CVAA', f"{d} findings {prev[d]['findings']} -> {obj['findings']}")
    inc = collections.Counter(r['vaccine'] for v in cv.values()
                              for r in v['results'] if r['state']!='immune')
    old_inc = st['cvaa']['incidence']
    for v in set(inc)|set(old_inc):
        if inc.get(v,0) != old_inc.get(v,0):
            D('VACCINE', f"{v} incidence {old_inc.get(v,0)} -> {inc.get(v,0)} of {len(cv)}")
    st['cvaa']['per_repo'] = {k:{"status":v['status'],"findings":v['findings']} for k,v in cv.items()}
    st['cvaa']['incidence'] = dict(inc)
    for d,obj in cv.items():
        wf = obj['context']['workflows']
        if st['heads'][d].get('workflows') not in (None, wf):
            D('COUNT', f"{d} workflow files {st['heads'][d]['workflows']} -> {wf}")
        new_heads[d]['workflows'] = wf
        new_heads[d]['commit_count'] = obj['context']['commit_count']

# ------------------------------------------------------------- 4. write out
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

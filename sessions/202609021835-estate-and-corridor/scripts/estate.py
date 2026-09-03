import json, subprocess, collections, datetime, os, sys, pathlib, urllib.request, time
from concurrent.futures import ThreadPoolExecutor, as_completed

GH   = pathlib.Path("C:/Users/vikra/OneDrive/Documents/GitHub")
WORK = pathlib.Path(sys.argv[1])
WORK.mkdir(parents=True, exist_ok=True)
NPROC = os.cpu_count() or 8

REPOS = ["chatgpt-audits","companies","cvaa","data-centres-gb",
         "data-federation-map-for-globalgrid2050-all-repos","data-gb-electricity",
         "data-grid-gb","data-gridatlas","data-interconnectors","gb-electricity-ui",
         "globalgrid2050","grid-distance-maths","gridatlas","pipelinenews","spiders"]

def run(*a, cwd=None, timeout=300):
    try:
        r = subprocess.run(a, cwd=cwd, capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as ex:
        return 1, "", str(ex)[:160]

def prepare(name):
    dst = WORK / name
    if not (dst / ".git").exists():
        rc, _, e = run("git","clone","--shared","--no-checkout",
                       str(GH/name/".git"), str(dst), timeout=900)
        if rc:
            return ("prep", name, None, "clone: " + e.strip()[:160])
    run("git","remote","add","gh","https://github.com/Ventusltd/" + name + ".git", cwd=dst)
    rc, _, e = run("git","fetch","-q","--no-tags","gh",
                   "+refs/heads/*:refs/remotes/gh/*", cwd=dst, timeout=1200)
    if rc:
        return ("prep", name, str(dst), "fetch: " + e.strip()[:160])
    return ("prep", name, str(dst), None)

def default_ref(dst):
    for r in ("gh/main","gh/master"):
        if run("git","rev-parse","--verify","-q",r, cwd=dst)[0] == 0:
            return r
    return None

def api(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json",
                                               "User-Agent":"estate-scan"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def ci(name):
    try:
        d = api("https://api.github.com/repos/Ventusltd/" + name + "/actions/runs?per_page=100")
        return ("ci", name, d, None)
    except Exception as ex:
        return ("ci", name, None, str(ex)[:120])

def stats(name, dst):
    ref = default_ref(dst)
    if not ref:
        return {"name": name, "error": "no main/master branch on remote"}
    o = {"name": name, "ref": ref.split("/")[-1]}

    _, log, _ = run("git","log",ref,"--date=short",
                    "--pretty=format:%H|%ad|%aI|%an|%s","--numstat", cwd=dst, timeout=900)
    commits, cur = [], None
    for line in log.splitlines():
        if len(line) > 41 and line[40] == "|":
            p = line.split("|", 4)
            cur = {"sha":p[0], "date":p[1], "iso":p[2], "author":p[3],
                   "subject":p[4] if len(p) > 4 else "",
                   "add":0, "del":0, "files":0, "paths":[]}
            commits.append(cur)
            continue
        if cur and line.strip():
            f = line.split("\t")
            if len(f) == 3:
                a, d, pth = f
                cur["add"] += int(a) if a.isdigit() else 0
                cur["del"] += int(d) if d.isdigit() else 0
                cur["files"] += 1
                cur["paths"].append(pth)
    if not commits:
        return {"name": name, "error": "empty history"}

    today = datetime.date.today()
    def since(days):
        c = (today - datetime.timedelta(days=days)).isoformat()
        return [x for x in commits if x["date"] >= c]
    d1, d7, d30 = since(1), since(7), since(30)

    o.update({
        "commits_total": len(commits),
        "first": commits[-1]["date"],
        "head_sha": commits[0]["sha"][:7],
        "head_iso": commits[0]["iso"],
        "head_subject": commits[0]["subject"][:96],
        "head_author": commits[0]["author"],
        "c24h": len(d1), "c7d": len(d7), "c30d": len(d30),
        "add30": sum(x["add"] for x in d30),
        "del30": sum(x["del"] for x in d30),
        "files30": sum(x["files"] for x in d30),
        "active_days_30": len({x["date"] for x in d30}),
        "authors_30": len({x["author"] for x in d30}),
    })

    days = [(today - datetime.timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    per = collections.Counter(x["date"] for x in commits)
    o["spark"] = [{"d": d, "n": per.get(d, 0)} for d in days]

    dirs = collections.Counter()
    for c in d30:
        for p in c["paths"]:
            dirs[p.split("/")[0] if "/" in p else "(root)"] += 1
    o["areas"] = [{"dir": k, "n": v} for k, v in dirs.most_common(5)]

    _, br, _ = run("git","branch","-r","--list","gh/*","--format=%(refname:short)", cwd=dst)
    o["branches"] = len([b for b in br.splitlines() if b.strip() and "->" not in b])

    canon = GH / name
    _, wt, _ = run("git","worktree","list", cwd=canon)
    o["worktrees"] = len([l for l in wt.splitlines() if l.strip()])

    _, lh, _ = run("git","rev-parse","--short","HEAD", cwd=canon)
    lh = lh.strip()
    o["local_head"] = lh
    if lh:
        _, ct, _ = run("git","rev-list","--left-right","--count", lh + "..." + ref, cwd=dst)
        parts = ct.split()
        o["local_ahead"], o["local_behind"] = (parts + ["?","?"])[:2]

    wf = canon / ".github" / "workflows"
    o["workflow_files"] = (len(list(wf.glob("*.yml"))) + len(list(wf.glob("*.yaml")))) if wf.exists() else 0

    _, tree, _ = run("git","ls-tree","-r",ref,"--name-only", cwd=dst, timeout=600)
    o["tracked_files"] = len(tree.splitlines())
    return o


t0 = time.time()
prepared, ci_raw = {}, {}
with ThreadPoolExecutor(max_workers=NPROC * 2) as ex:
    futs = [ex.submit(prepare, n) for n in REPOS] + [ex.submit(ci, n) for n in REPOS]
    for f in as_completed(futs):
        kind, n, a, b = f.result()
        if kind == "prep":
            prepared[n] = (a, b)
        else:
            ci_raw[n] = (a, b)
print("[prep+api %.1fs]" % (time.time() - t0), file=sys.stderr)

t1 = time.time()
out = {}
with ThreadPoolExecutor(max_workers=NPROC) as ex:
    futs = {ex.submit(stats, n, dst): n for n, (dst, err) in prepared.items() if dst}
    for f in as_completed(futs):
        n = futs[f]
        try:
            out[n] = f.result()
        except Exception as ex2:
            out[n] = {"name": n, "error": str(ex2)[:140]}
print("[stats %.1fs]" % (time.time() - t1), file=sys.stderr)

for n, (dst, err) in prepared.items():
    if err:
        out.setdefault(n, {"name": n})["prep_error"] = err

for n, (d, err) in ci_raw.items():
    o = out.setdefault(n, {"name": n})
    if err or not d:
        o["ci"] = {"error": err or "no data"}
        continue
    runs = d.get("workflow_runs", [])
    if not runs:
        o["ci"] = {"total_count": d.get("total_count", 0), "sampled": 0}
        continue
    s  = sum(1 for r in runs if r["conclusion"] == "success")
    fl = sum(1 for r in runs if r["conclusion"] == "failure")
    byw = collections.defaultdict(lambda: {"total":0, "fail":0, "last":None, "last_c":None})
    for r in runs:
        w = byw[r["name"]]
        w["total"] += 1
        if r["conclusion"] == "failure":
            w["fail"] += 1
        if w["last"] is None or r["created_at"] > w["last"]:
            w["last"], w["last_c"] = r["created_at"], r["conclusion"]
    dep = [r for r in runs if ("ages" in r["name"] or "eploy" in r["name"])]
    okd = [r for r in dep if r["conclusion"] == "success"]
    consec = 0
    for r in dep:
        if r["conclusion"] == "failure":
            consec += 1
        else:
            break
    o["ci"] = {
        "total_count": d.get("total_count", 0),
        "sampled": len(runs),
        "success": s, "failure": fl,
        "window": [runs[-1]["created_at"], runs[0]["created_at"]],
        "last_run": runs[0]["created_at"],
        "last_conclusion": runs[0]["conclusion"],
        "deploy_wf": dep[0]["name"] if dep else None,
        "deploy_last_ok": okd[0]["created_at"] if okd else None,
        "deploy_consec_fail": consec,
        "workflows": sorted([dict(name=k, **v) for k, v in byw.items()],
                            key=lambda x: (-x["fail"], -x["total"]))[:10],
    }

res = {"generated_utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "workers": NPROC,
       "repos": [out[n] for n in REPOS if n in out]}
json.dump(res, open(sys.argv[2], "w"), indent=1)
print("[total %.1fs] repos=%d" % (time.time() - t0, len(res["repos"])), file=sys.stderr)

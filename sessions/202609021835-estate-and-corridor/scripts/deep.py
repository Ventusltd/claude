import json, subprocess, collections, datetime, os, sys, pathlib, urllib.request, time, statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

GH    = pathlib.Path("C:/Users/vikra/OneDrive/Documents/GitHub")
WORK  = pathlib.Path(sys.argv[1])
OUT   = sys.argv[2]
NPROC = os.cpu_count() or 8

REPOS = ["chatgpt-audits","companies","cvaa","data-centres-gb",
         "data-federation-map-for-globalgrid2050-all-repos","data-gb-electricity",
         "data-grid-gb","data-gridatlas","data-interconnectors","gb-electricity-ui",
         "globalgrid2050","grid-distance-maths","gridatlas","pipelinenews","spiders"]


def run(*a, cwd=None, timeout=600):
    try:
        r = subprocess.run(a, cwd=cwd, capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as ex:
        return 1, "", str(ex)[:160]


def fetch(name):
    dst = WORK / name
    if not (dst / ".git").exists():
        run("git", "clone", "--shared", "--no-checkout", str(GH/name/".git"), str(dst), timeout=900)
    run("git", "remote", "add", "gh", "https://github.com/Ventusltd/" + name + ".git", cwd=dst)
    run("git", "fetch", "-q", "--no-tags", "gh", "+refs/heads/*:refs/remotes/gh/*", cwd=dst, timeout=1200)
    return name, str(dst)


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "estate-scan"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def ci(name):
    try:
        return name, api("https://api.github.com/repos/Ventusltd/%s/actions/runs?per_page=100" % name)
    except Exception as ex:
        return name, {"error": str(ex)[:100]}


def probe(name):
    url = "https://ventusltd.github.io/%s/" % name
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "estate-scan"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read()
            return name, {"url": url, "status": r.status, "bytes": len(body),
                          "ms": int((time.time() - t0) * 1000),
                          "last_modified": r.headers.get("Last-Modified", "-"),
                          "server": r.headers.get("Server", "-")}
    except urllib.error.HTTPError as e:
        return name, {"url": url, "status": e.code, "bytes": 0, "ms": 0,
                      "last_modified": "-", "server": "-"}
    except Exception as ex:
        return name, {"url": url, "status": 0, "error": str(ex)[:60]}


def ref_of(dst):
    for r in ("gh/main", "gh/master"):
        if run("git", "rev-parse", "--verify", "-q", r, cwd=dst)[0] == 0:
            return r
    return None


SIZE_UNITS = ["B", "KB", "MB", "GB"]
def human(n):
    f = float(n)
    for u in SIZE_UNITS:
        if f < 1024 or u == "GB":
            return ("%.0f %s" % (f, u)) if u == "B" else ("%.1f %s" % (f, u))
        f /= 1024


def deep(name, dst):
    ref = ref_of(dst)
    if not ref:
        return {"name": name, "error": "no default branch"}
    o = {"name": name, "ref": ref.split("/")[-1]}

    _, log, _ = run("git", "log", ref, "--date=iso-strict",
                    "--pretty=format:\x01%H|%ad|%an|%ae|%P|%s", "--numstat", cwd=dst)
    commits, cur = [], None
    for line in log.splitlines():
        if line.startswith("\x01"):
            p = line[1:].split("|", 5)
            cur = {"sha": p[0], "iso": p[1], "an": p[2], "ae": p[3],
                   "parents": p[4].split(), "subj": p[5] if len(p) > 5 else "",
                   "add": 0, "del": 0, "files": 0, "paths": []}
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

    dt = [datetime.datetime.fromisoformat(c["iso"]) for c in commits]
    first, last = dt[-1], dt[0]
    span_days = max(1, (last - first).days)

    o["head"]        = commits[0]["sha"]
    o["head_iso"]    = commits[0]["iso"]
    o["head_subj"]   = commits[0]["subj"][:88]
    o["first_iso"]   = commits[-1]["iso"]
    o["span_days"]   = span_days
    o["commits"]     = len(commits)
    o["merges"]      = sum(1 for c in commits if len(c["parents"]) > 1)
    o["add_total"]   = sum(c["add"] for c in commits)
    o["del_total"]   = sum(c["del"] for c in commits)
    o["files_touched"] = sum(c["files"] for c in commits)
    o["per_day"]     = round(len(commits) / span_days, 2)
    sizes = sorted(c["files"] for c in commits)
    o["files_median"] = sizes[len(sizes)//2]
    o["files_max"]   = sizes[-1]

    gaps = [(dt[i-1] - dt[i]).total_seconds()/3600 for i in range(1, len(dt))]
    o["gap_max_h"] = round(max(gaps), 1) if gaps else 0
    o["gap_med_h"] = round(statistics.median(gaps), 2) if gaps else 0

    o["authors"] = [{"n": a, "c": c} for a, c in
                    collections.Counter(x["an"] for x in commits).most_common(8)]
    o["authors_total"] = len({x["an"] for x in commits})

    hod = collections.Counter(d.hour for d in dt)
    o["hours"] = [hod.get(h, 0) for h in range(24)]
    dow = collections.Counter(d.weekday() for d in dt)
    o["dow"] = [dow.get(i, 0) for i in range(7)]

    today = datetime.date.today()
    per = collections.Counter(d.date().isoformat() for d in dt)
    o["days30"] = [{"d": (today - datetime.timedelta(days=i)).isoformat(),
                    "n": per.get((today - datetime.timedelta(days=i)).isoformat(), 0)}
                   for i in range(29, -1, -1)]
    o["c1"]  = sum(1 for d in dt if (datetime.datetime.now(d.tzinfo) - d).days < 1)
    o["c7"]  = sum(1 for d in dt if (datetime.datetime.now(d.tzinfo) - d).days < 7)
    o["c30"] = sum(1 for d in dt if (datetime.datetime.now(d.tzinfo) - d).days < 30)

    dirs = collections.Counter()
    for c in commits[:400]:
        for p in c["paths"]:
            dirs[p.split("/")[0] if "/" in p else "(root)"] += 1
    o["areas"] = [{"d": k, "n": v} for k, v in dirs.most_common(8)]

    _, tree, _ = run("git", "ls-tree", "-r", "-l", ref, cwd=dst)
    exts, total_bytes, depths, biggest = collections.Counter(), 0, [], []
    nfiles = 0
    for line in tree.splitlines():
        try:
            meta, path = line.split("\t", 1)
            parts = meta.split()
            size = int(parts[3]) if parts[3].isdigit() else 0
        except Exception:
            continue
        nfiles += 1
        total_bytes += size
        depths.append(path.count("/"))
        base = path.rsplit("/", 1)[-1]
        ext = ("." + base.rsplit(".", 1)[1].lower()) if "." in base else "(none)"
        exts[ext] += 1
        biggest.append((size, path))
    biggest.sort(reverse=True)
    o["tracked_files"] = nfiles
    o["tracked_bytes"] = total_bytes
    o["tracked_human"] = human(total_bytes)
    o["depth_max"] = max(depths) if depths else 0
    o["depth_avg"] = round(sum(depths)/len(depths), 2) if depths else 0
    o["exts"] = [{"e": e, "n": n} for e, n in exts.most_common(10)]
    o["biggest"] = [{"p": p[:56], "b": human(s)} for s, p in biggest[:5]]

    _, br, _ = run("git", "branch", "-r", "--list", "gh/*", "--format=%(refname:short)|%(committerdate:short)", cwd=dst)
    brs = []
    for line in br.splitlines():
        if not line.strip() or "->" in line:
            continue
        nm, _, dd = line.partition("|")
        nm = nm.strip()[3:]
        if nm and nm != o["ref"]:
            _, cnt, _ = run("git", "rev-list", "--count", "%s..gh/%s" % (ref, nm), cwd=dst)
            brs.append({"b": nm[:46], "d": dd, "ahead": cnt.strip() or "?"})
    o["branch_rows"] = sorted(brs, key=lambda x: x["d"], reverse=True)[:8]
    o["branches"] = len(brs) + 1

    canon = GH / name
    _, wt, _ = run("git", "worktree", "list", cwd=canon)
    o["worktrees"] = len([l for l in wt.splitlines() if l.strip()])
    wf = canon / ".github" / "workflows"
    o["workflow_files"] = (len(list(wf.glob("*.yml"))) + len(list(wf.glob("*.yaml")))) if wf.exists() else 0
    return o


t0 = time.time()
prep, ciraw, probes = {}, {}, {}
with ThreadPoolExecutor(max_workers=NPROC * 3) as ex:
    fs = ([ex.submit(fetch, n) for n in REPOS] +
          [ex.submit(ci, n) for n in REPOS] +
          [ex.submit(probe, n) for n in REPOS])
    for f in as_completed(fs):
        n, v = f.result()
        if isinstance(v, str):
            prep[n] = v
        elif "workflow_runs" in v or "error" in v and "status" not in v:
            ciraw[n] = v
        else:
            probes[n] = v
print("[fetch+api+probe %.1fs]" % (time.time() - t0), file=sys.stderr)

t1 = time.time()
out = {}
with ThreadPoolExecutor(max_workers=NPROC) as ex:
    fs = {ex.submit(deep, n, d): n for n, d in prep.items()}
    for f in as_completed(fs):
        n = fs[f]
        try:
            out[n] = f.result()
        except Exception as ex2:
            out[n] = {"name": n, "error": str(ex2)[:120]}
print("[deep %.1fs]" % (time.time() - t1), file=sys.stderr)

for n, d in ciraw.items():
    o = out.setdefault(n, {"name": n})
    runs = d.get("workflow_runs", [])
    if not runs:
        o["ci"] = {"sampled": 0, "total_count": d.get("total_count", 0)}
        continue
    def dur(r):
        try:
            a = datetime.datetime.fromisoformat(r["run_started_at"].replace("Z", "+00:00"))
            b = datetime.datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00"))
            return max(0, int((b - a).total_seconds()))
        except Exception:
            return 0
    byw = collections.defaultdict(lambda: {"t": 0, "f": 0, "s": 0, "d": [], "last": None, "lc": None})
    for r in runs:
        w = byw[r["name"]]
        w["t"] += 1
        if r["conclusion"] == "failure": w["f"] += 1
        if r["conclusion"] == "success": w["s"] += 1
        w["d"].append(dur(r))
        if w["last"] is None or r["created_at"] > w["last"]:
            w["last"], w["lc"] = r["created_at"], r["conclusion"]
    wfs = []
    for k, v in byw.items():
        ds = sorted(x for x in v["d"] if x)
        wfs.append({"n": k[:60], "t": v["t"], "f": v["f"], "s": v["s"],
                    "med": ds[len(ds)//2] if ds else 0,
                    "max": ds[-1] if ds else 0,
                    "last": v["last"], "lc": v["lc"]})
    wfs.sort(key=lambda x: (-x["f"], -x["t"]))
    alld = sorted(x for x in (dur(r) for r in runs) if x)
    dep = [r for r in runs if ("ages" in r["name"] or "eploy" in r["name"])]
    okd = [r for r in dep if r["conclusion"] == "success"]
    consec = 0
    for r in dep:
        if r["conclusion"] == "failure": consec += 1
        else: break
    ev = collections.Counter(r["event"] for r in runs)
    o["ci"] = {
        "sampled": len(runs), "total_count": d.get("total_count", 0),
        "success": sum(1 for r in runs if r["conclusion"] == "success"),
        "failure": sum(1 for r in runs if r["conclusion"] == "failure"),
        "cancelled": sum(1 for r in runs if r["conclusion"] == "cancelled"),
        "window": [runs[-1]["created_at"], runs[0]["created_at"]],
        "last_run": runs[0]["created_at"], "last_conclusion": runs[0]["conclusion"],
        "dur_med": alld[len(alld)//2] if alld else 0,
        "dur_max": alld[-1] if alld else 0,
        "dur_sum": sum(alld),
        "events": [{"e": k, "n": v} for k, v in ev.most_common(5)],
        "deploy_consec_fail": consec,
        "deploy_last_ok": okd[0]["created_at"] if okd else None,
        "workflows": wfs,
    }

for n, p in probes.items():
    out.setdefault(n, {"name": n})["http"] = p

res = {"generated_utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "workers": NPROC, "elapsed_s": round(time.time() - t0, 1),
       "repos": [out[n] for n in REPOS if n in out]}
json.dump(res, open(OUT, "w"), indent=1)
print("[total %.1fs] repos=%d bytes=%d" % (time.time() - t0, len(res["repos"]),
                                           os.path.getsize(OUT)), file=sys.stderr)

"""Grade logs/red-board.json by re-fetching each cited job log and checking the quote.

Does not trust triage.py's own grounding flag. For a sample of rows marked grounded, this
re-fetches the job log from the GitHub API and checks the quote is a whitespace-flattened
substring of the WHOLE log - and separately reports whether it appears only inside the
echoed `##[group]Run ...` script source rather than in real step output.
"""
import json, os, random, re, subprocess, sys

REPO = "C:/Users/vikra/OneDrive/Documents/GitHub/claude"
d = json.load(open("rb-snapshot.json", encoding="utf-8"))
rows = [r for r in d["rows"] if r.get("grounded") is True and r.get("quote")]
random.seed(11)
sample = random.sample(rows, min(int(sys.argv[1]) if len(sys.argv) > 1 else 6, len(rows)))

TS = re.compile(r"^\S*?\d{4}-\d\d-\d\dT[\d:.]+Z ", re.M)
ANSI = re.compile(r"\[[0-9;]*m|\[[0-9]{1,2};[0-9]{1,2}m|\[0m")

def clean(s):
    """strip the per-line timestamp and ANSI colour codes triage strips before matching"""
    s = TS.sub("", s)
    return ANSI.sub("", s)

def flat(s):
    return re.sub(r"\s+", " ", clean(s)).strip()

ok = bad = only_echo = 0
for r in sample:
    path = f"repos/{r['full_repo']}/actions/jobs/{r['job_id']}/logs"
    try:
        log = subprocess.run(["bash", os.path.join(REPO, "scripts", "gh-api.sh"), path, "--raw"],
                             capture_output=True, timeout=90).stdout.decode("utf-8", "replace")
    except Exception as e:
        print(f"  FETCH FAILED {r['repo']} {r['job_id']}: {e}")
        continue
    q = flat(r["quote"].strip('"'))
    present = q in flat(log)
    # lines that are echoed workflow source carry GitHub's 36;1m colour code
    real_out = [ln for ln in log.splitlines() if "36;1m" not in ln]
    in_real = q in flat("\n".join(real_out))
    tag = "OK " if present else "MISSING"
    if present:
        ok += 1
    else:
        bad += 1
    if present and not in_real:
        only_echo += 1
        tag = "ECHO-ONLY"
    print(f"  [{tag:9}] {r['repo']:<22} job {r['job_id']}  log {len(log):>7} chars")
    print(f"              quote: {q[:96]}")
    if not present:
        print(f"              first_error_line: {r.get('first_error_line','')[:90]}")

print(f"\n  sampled {len(sample)} rows marked grounded")
print(f"  quote verified verbatim in the log      {ok}")
print(f"  quote NOT found (triage overstated)     {bad}")
print(f"  quote present ONLY in echoed script src {only_echo}  <- real string, false role")

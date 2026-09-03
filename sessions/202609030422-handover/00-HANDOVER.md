# Handover — 2026-09-03, 04:22 UTC

Read this first. Everything below is measured; where I could not measure something I say so
rather than round it up. Times are UTC taken from `date -u` in the same turn as the claim.

---

## 1. The number you asked for

You asked for 10× Pipeline News and 10× GridAtlas iterations by the time you woke.

| | target | delivered | |
|---|---|---|---|
| **GridAtlas** | 10 | **10** — v9.79 → v9.88 | met |
| **Pipeline News** | 10 | **3** — `202609021945`, `202609022308`, `202609030009` | **not met** |

Pipeline News has been silent since `202609030009`, cut at 00:09Z — a little over four hours.

**Why, stated plainly.** The release-cadence agent stopped cutting because it ran out of real
changes, and logged the decision as *"nine generations, all green, and an empty queue rather
than a padded one."* In the same pass it built a layer-fidelity fix, measured it three ways,
and concluded it must not ship.

I endorse that judgement — a generation that changes nothing is a false claim of progress, and
this estate's whole value is that its numbers can be trusted. But the delivered number is 3,
not 10, and you should hear that from me rather than work it out from the directory listing.
If you want ten Pipeline News generations regardless of whether each carries a change, say so
and I will cut them; I did not assume that.

---

## 2. What shipped since the 03:00 checkpoint

- **cvaa `7c8ed09`** — the security fix in §3. Self-test and full-history workflow **green**,
  confirmed against the Actions API for that exact SHA, not inferred from a local run.
- **cvaa `93e568e`** — `rollback-exercised` stops deciding from commit prose (§4). Also green,
  confirmed the same way.
- **Four repositories were holding unpushed commits and now are not.** Unpushed work is
  invisible work at a handover:

  | repo | commits | what |
  |---|---|---|
  | `codex-chatgpt` | 4 | Codex Phase 0 archive + coordination snapshot |
  | `data-grid-gb` | 1 | **Codex's `b91e45b`** — transformer identity + fail-closed joins |
  | `gemini` | 1 | tri-agent audit consolidation |
  | `pipelinenews` | 1 | board note: stop unsafe live-worktree spider scans |

  All four were fast-forward and none was behind its remote. `b91e45b` had been sitting
  unpushed since 02:21Z and was an open item in my own record; it is now live.

---

## 3. The one that matters: cvaa was executing code owned by the repositories it scans

**Found by Codex**, independently, against a live worktree. I verified it myself before acting,
and it is correct.

`inoculate.mjs` built its context by running

```
node tools/scope/loop.mjs state --stdout
```

with the working directory set to **the target**. That is arbitrary code execution from the
repository under inspection, and cvaa exists to scan repositories it has no particular reason
to trust. Every antibody is sandboxed — permission model, no filesystem, no network, 5-second
cap, empty environment — and this one line ran outside all of it. `--no-write` did not stop it;
that flag only ever suppressed cvaa's own `last-fired.json` sidecar.

It also wrote. gridatlas's `loop.mjs` silently ignored `--stdout` and took its normal path,
which writes `STATE.md` — so a scan that promised `--no-write` rewrote a file in the repository
it was inspecting. That is the unexplained `STATE.md` rewrite Codex observed. gridatlas fixed
its own side at 02:40Z (`4b1641e`); the hazard in cvaa was independent of that fix, because the
next target's `loop.mjs` can do anything at all.

**The second defect, which made the first one dangerous to fix.** The antibody runner coerced
any non-array return to `[]`, and `[]` prints as `immune`. So a rule that could not evaluate its
question had no way to say so — the answer silently became a pass. Turning the execution off on
its own would have converted a real check into exactly that false pass.

**Demonstrated, not argued.** A fixture whose `loop.mjs` writes a marker file, same fixture,
both versions, under `--no-write`:

| | target code executed | what cvaa concluded |
|---|---|---|
| shipped `4666369` | **yes** | `repo is immune to all vaccines on file` |
| patched `7c8ed09` | no | `no findings, but 1 rule(s) were not evaluated; immunity is not established` |

**The fix.** Target execution is off by default; `--exec-target` opts in and `--no-write` can
never opt in. An antibody may now return `{ skip: "why" }`; the runner carries it, the report
prints `skip` with the reason, `cvaa.run.v1` carries `state=skipped`, and the summary refuses to
say *immune to all vaccines on file* when a rule was never evaluated.

Both new assertions **fail on `4666369`** with exactly the two errors they are meant to catch,
so the gate can fail. That check is permanent now, not a one-off.

---

## 4. Corrections to the record

**D5 — closed, and both earlier statements about it were wrong.** All **18** local repositories
already carry `* text=auto eol=lf`. The spider filed "four repositories lack it"; I then filed
"all 18 lack it". Neither was a measurement — my sweep was silently broken. Git on Windows
rewrote `origin/main:.gitattributes` into `origin\main;.gitattributes`, so every lookup failed
and every repo reported "no file". `MSYS_NO_PATHCONV=1` fixes that, but it must be set
per-command: with it set globally the *next* command handed git a `/c/Users/...` path and git
resolved it against the MSYS root instead. It is a per-command flag, not an environment.

The only CRLF blobs in the estate are **223 CSVs in globalgrid2050**, deliberately exempt under
`*.csv -text` with the reasoning written into `.gitattributes`: RFC 4180 specifies CRLF for
`text/csv`, none sits inside a hashed release or an attested artefact. That was solved on
purpose on 31 August. Nothing to fix. *(One small drift: the comment says "221 historical
generation CSVs under `data/generation/`"; the measurement is 223, and they include
`data/electricity/`. Prose, not bytes.)*

**D11 — closed**, verified rather than assumed: `fileURLToPath` landed and `selftest` returns
rc=0 on Windows, where it previously could not run at all.

**D16 — closed.**

**D15 — three of four closed. `rollback-exercised` is fixed; `on-ledger-commits` is a policy
call I deliberately left for you.** `full-history-checkout` and `attestation-freshness` already
read state instead of ranking commit-subject regexes.

`rollback-exercised` (cvaa `93e568e`, CI green) searched commit **subjects** for
`/roll ?back|rollback drill/`. Across gridatlas's last 200 commits exactly one matched:

> `32bc3bb  202609012105: carry Codex's assembler boundary — staged, exclusive, and owned rollback`

That commit describes an assembler boundary. It exercised no rollback. On the strength of that
single subject the rule reported gridatlas **immune** to *"no rollback has ever been exercised"*.
Naming a thing is not doing it. It now reads `atlas/state/rollback-drills.json` — a drill record
with a `release_id` and an `outcome` — and where the estate emits none it **skips and names the
artefact that would let it decide**. That honest answer only had somewhere to go because the
skip state landed in `7c8ed09` an hour earlier. It also gained a diseased fixture it never had,
so for the first time the self-test proves the rule can fire at all.

Verified against the live gridatlas worktree under `--no-write`: the rule skips, and the working
tree's porcelain digest and `STATE.md` SHA-256 are **identical before and after** — the scan
touched nothing, which is the whole point of §3.

**`on-ledger-commits` is untouched and you should decide it.** It exempts any commit whose
subject matches `/verify|roll ?back|inoculate|drill/` — **6 of gridatlas's last 200 commits** are
excused from the ledger by a word in the subject, including *"record A-roads forensic drill
request"*. Narrowing that lights up findings estate-wide, so it is not a change to make at
04:40 with you asleep.

**My own attestation-freshness limitation stands**, recorded in the vaccine: it measured 0
divergences across 12 generations, because `verified_at` is not in `live-set.json`. The rule is
close to tautological. I wrote that down rather than let the green read as proof.

---

## 5. Open — these are yours to decide, not mine

1. **D1 — the homepage stamp.** Unchanged. Does *"Current Verified Release"* mean the newest
   release or the reviewed one? Three options are costed in `08-decisions-for-the-architect.md`.
   I stopped cutting it rather than keep hand-maintaining a stamp at a 96-second cadence.

2. **NEW — the `data-grid-gb` pin, and it is a real trade.** The mutable edge fired at 04:02Z;
   the pin held and the shipped map is unaffected. But the map now shows transformer counts its
   owner has since corrected. Moving the pin to `5181de3` makes the data correction and the map
   correction one visible event — **and drops 13 sites that currently have coordinates.** That
   is a loss as well as a gain, so I did not make it unilaterally. It is one cut:
   three entries in `atlas/modules/202609030137-pinned-products.js`, then a version.

   Two details from that event are worth more than the headline: the **schema string was
   identical on both sides** while 882 of 886 records changed — so the fail-closed schema check
   would have waved it through — and `gb-transmission-network.v1.json` changed content at
   **identical byte length**, 10,069,966 B either side. Only the digest catches that. It
   vindicates carrying SHA-256 rather than byte length alone, which was not obvious in advance.

3. **NEW — should a skipped rule fail CI?** Today a skip exits 0. The output no longer lies, but
   the exit code still treats "not evaluated" as "fine". Making skips non-zero is the honest
   choice and has estate-wide blast radius, so I did not do it at 04:00 with you asleep.

4. **NEW — `on-ledger-commits`' prose escape hatch.** Any commit whose subject contains
   *verify*, *rollback*, *inoculate* or *drill* is excused from citing a scope file. Six of
   gridatlas's last 200 commits take that exit. The honest fix makes the exemption structural
   rather than textual, and it will surface findings across every repo the first time it runs.
   Yours to time.

5. **D8 — PipelineNews has no route by which an owner could authorise a deploy.** Unchanged; the
   third gate is an authorisation freeze working as designed, not a defect.

6. **The parallel session's cvaa worktree.** `OneDrive/Documents/GitHub/cvaa` is a *different
   session's* checkout: 9 commits behind origin, 2 commits ahead that are not on origin
   (a federation-mission README and a vaccine named `a-skip-is-not-a-pass-needs-source-text`),
   plus an untracked vaccine and a modified `vaccines.lock`. I did **not** touch, rebase or push
   it. Someone who knows whether that work is still wanted should reconcile it. My cvaa work
   tonight was done in a clean clone of `origin/main`, which is why it did not collide.

   Worth noting that the parallel session reached "a skip is not a pass" independently, and
   named a vaccine after it, before I hit the same wall in the runner.

---

## 6. Where the record lives

- This file supersedes the 03:00 snapshot for anything it contradicts.
- `07-routing-table.md` and `08-decisions-for-the-architect.md` are current to ~03:05Z and are
  still being edited by running agents; I left them alone deliberately to avoid a collision.
- The cvaa fix, its demonstration and its negative control are in cvaa commit `7c8ed09`.

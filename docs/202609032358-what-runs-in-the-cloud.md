# What runs in the cloud, what stays on the laptop, and why

Written 2026-09-03, when GitHub Actions was first used as a second machine rather than
only as a gate.

## The constraint that shaped every file here

> "don't email storm me with failed workflows and py etc"

GitHub mails the repository actor when a workflow **fails**. Everything below follows from
that one sentence:

- **An informational job exits 0 on every finding.** A crawl, a survey, a benchmark — these
  are reports. A report that exits non-zero is doing two wrong things at once: mailing a
  human, and misrepresenting its own role as a gate. Each workflow says so in a banner
  comment at the top, and each script says so in its module docstring, so that nobody later
  "fixes" one into a gate without reading why it isn't.
- **A gate keeps failing loudly.** The gates that must block were not touched.
  `gridatlas/.github/workflows/202608312212-cartridge-proof.yml` is the model and is
  untouched; so is `claude/.github/workflows/202609031030-verify-memory-store.yml`, and so
  is `pipelinenews/.github/workflows/`, which another lane holds.
- **At most one nightly informational run each, staggered**, and nothing that can fail
  repeatedly. The benchmark has no schedule at all.
- **`concurrency: cancel-in-progress: true`** on every one, so a re-run supersedes rather
  than piles up.
- No notification steps were added anywhere.

### The setting the architect should flip

The above stops *these* workflows mailing anyone. It does not stop the ~45 workflows across
the estate that have never been green from mailing on every run. That is one checkbox and
it is his to flip, not mine:

**GitHub → Settings → Notifications → Actions → uncheck "Email"**, or set it to
**"Only notify for failed workflows"** and tick **"Send notifications for failed workflows
only when I triggered them"**.

<https://github.com/settings/notifications> — the *Actions* section, near the bottom.

That single change turns off the storm at source for every repository at once. Nothing in
this repository can do it, and no workflow setting can override it.

## Is any of this metered?

No. Of the 35 repositories the account owns, **33 are public and 2 are private**
(`cable_selection`, `crm`). Actions minutes on a public repository are free, and the billing
API confirms it in the only way that matters — the money column:

| month | Actions Linux minutes | net cost |
|---|---:|---:|
| 2026-08 | 11,905 | $0.00 |
| 2026-09 (to the 3rd) | 1,233 | $0.00 |

Every minute was discounted to zero. Everything added here runs in public repositories, so
the marginal cost of moving this work off the laptop is nil.

## What now runs in the cloud

All four live in `Ventusltd/claude`, not in a product repository. Two reasons: estate-wide
work does not belong to any one product, and `gridatlas` enforces a workflow budget
(`ACTIVE_WORKFLOWS` in `tools/scope/lib.mjs`, asserted by `loop.mjs lint`) that adding a file
would have broken.

### 1. `202609032340-estate-link-crawl.yml` — every published release, over HTTP

Four surfaces, four runners, in parallel:

| surface | what it crawls |
|---|---|
| `globalgrid2050` | the homepage and every route its catalogue names |
| `pipelinenews-intel` | the 28 Pipeline News snapshots served from globalgrid2050.com |
| `gridatlas-atlas` | the composed shell, `current.json`, and every Atlas release |
| `pipelinenews-releases` | every `/pipelinenews/releases/<gen>-pipelinenews/` |

**Why the cloud.** 76 published releases and ~976 outbound routes, each an HTTP request
against a live origin. Deterministic, parallel, and currently serial on a laptop that also
has to run a browser and a model.

**Two things it does that a grep cannot.** First, it distinguishes a base URL a manifest
*declares* from one a page actually *ships*, by resolving the import closure of the page's
own `<script type=module>`. About thirty release directories still carry the old deep-link
module without importing it; counting those would report thirty broken releases where there
is one. Second, it discovers releases from the **repository** (Pages serves no directory
listing) and checks them against the **origin**, so "published but never served" is a finding
it can see at all rather than a silent absence.

Board: `docs/boards/estate-link-crawl.md`.

### 2. `202609032345-ci-history-mine.yml` — the whole history, not the last run

`scripts/audit_estate.py` answers "what is red right now?" from the latest run per workflow.
It cannot separate a regression from a workflow that has never worked, because both present
as a failing last run. This mines up to 200 runs per workflow across all 35 repositories and
reports, per workflow: has it **ever** concluded success; is its last red **at head** or
stale; and a census of every conclusion by name.

It also measures the estate reader's own blind spot. `audit_estate.py` files `success` as
green, `failure`/`timed_out`/`startup_failure` as red, and **everything else as neither** —
so `cancelled` is counted as nothing at all, and a workflow that only ever gets cancelled is
indistinguishable from one that has never run.

Board: `docs/boards/ci-history.md`.

### 3. `202609032350-clean-clone-byte-survey.yml` — the bytes, where the bytes are true

`git status` compares **through** `.gitattributes` normalisation. It reports a tree clean
while the disk holds CRLF and the blob holds LF, and fifteen of eighteen repositories here
are in that state. So any measurement that depends on file bytes — a digest, a checksum
manifest, a character ceiling — reads a different number on this Windows working tree than
it reads where the artefact is served. A runner checks out from the blob; it is the cheapest
clean clone available and it can hold eighteen repositories side by side.

It settles the ceiling question by refusing to pick one number. **Three are enforced in this
estate and they are three different numbers:**

| number | unit | enforced by |
|---:|---|---|
| 368,640 | characters | the cartridge proof's assertion (0.9 × 409,600) |
| 400,000 | bytes | `tools/scope/loop.mjs lint` |
| 409,600 | bytes | the composer boundary — reported, not enforced |

And characters are not bytes: the proof measures UTF-16 code units, the lint measures
`statSync().size`, and cartridges contain non-ASCII. Each cartridge is reported on all three
gauges with the divergence named, so nobody has to remember which one they were reading. A
prior version of that check asserted against one number and *reported* against another, and
printed 40,995 characters of headroom when the true figure was 35.

Board: `docs/boards/clean-clone-bytes.md`.

### 4. `202609032355-llama-cpu-benchmark.yml` — measure before promising

`workflow_dispatch` only. See the next section for what it measured.

## What stays on the laptop, and why

**Anything that needs a model.** Standard GitHub-hosted runners have no GPU: `ubuntu-24.04`
is 4 vCPU and 16 GB of RAM, and inference runs on CPU or not at all. The measured numbers
are in `docs/boards/llama-on-actions.md`; the shape of them is that a runner spends most of
a short job acquiring a model before producing a single token, and then produces tokens at a
rate that makes anything conversational impractical.

**Anything that needs a browser against local state**, anything holding a credential that
should not leave the machine, and anything a human is watching.

The split, stated once so it does not have to be re-derived:

> **The cloud does what is parallel and deterministic. The laptop's GPU does what needs a
> model.**

## The disciplines these files carry

- Every action is **pinned by commit**, not by tag. `@v4` is mutable and whoever can move it
  can run code in the job.
- Every board names **what was measured, when in UTC, what it was read from, and how long it
  took** — the estate's existing board contract.
- Commits from a job stage **by explicit path**. Other lanes write to this repository and
  `git add -A` in a job would sweep up their work in progress.
- Commit messages are written to a **file**, not a heredoc. Backticks in an unquoted heredoc
  have eaten three commit messages in this estate.
- A push that loses a race is logged and tolerated; the findings are in the artifact and the
  next run rewrites the board. A failed push is not a reason to mail anyone.

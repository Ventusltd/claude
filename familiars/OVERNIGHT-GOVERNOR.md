# Overnight local-compute governor

Measured on the live machine on 2026-09-03/04. The durable controls are
`overnight_governor.py`, `governor-probe.ps1`, the admission check in
`localai.py`, and the parentage-only cleanup in `reap.py`.

## Resource envelope

The host is an Alienware 16 Area-51 AA16250 with an Intel Core Ultra 7 255HX
(20 cores / 20 logical processors), 16 GB DDR5-6400, a healthy 1 TB SK hynix
NVMe SSD, and an RTX 5070 Laptop GPU with 8,151 MiB VRAM. Intel AI Boost is
present, but Ollama/llama.cpp has no NPU backend on this installation.

The eight-hour lane therefore uses one serialized RTX request at a time. The
4B Q4 model stays eligible; the 8B model, parallel fan-out, and the Intel Vulkan
endpoint are outside the envelope. Four logical processors and 1,536 MiB dGPU
VRAM remain reserved for Windows and the two displays.

| resource | admit new work | critical / action |
|---|---:|---:|
| CPU | below 80% total | defer, preserving four of twenty logical processors |
| available RAM | at least 3,072 MiB | below 1,536 MiB is critical |
| commit | below 85% of limit | 92% is critical |
| paging | below 5,000 pages/s | 20,000 pages/s is critical |
| dGPU VRAM | at least 1,536 MiB free | below 768 MiB is critical |
| dGPU temperature | below 80 C | 85 C is critical |
| C: storage | at least 100 GiB free | below 50 GiB is critical |
| Ollama clients | one on port 11434 | further clients are refused by `localai.py` |

The watcher records working set, private commit, WDDM dedicated memory, and
WDDM shared memory separately. Working set is resident system RAM. Private
commit is an address-space/commit promise. WDDM values are GPU allocations.
Adding them together would double-count backing and falsely describe commit as
physical RAM.

## The pressure event and its correction

These readings are separate, time-correlated windows rather than one claimed
steady state:

- During two concurrent local-model clients, an eight-sample window read
  `Available MBytes` at 322--993 MiB (684 MiB average), `Pages/sec` at
  2,609--152,725 (21,564 average), commit at 44.38--44.68 GB of a 54.43 GB
  limit, and CPU at 6.7--31.1%. The RTX peaked at 99%, 73 C and 120 W.
- At 23:08:59Z, after those client sockets closed but both models remained
  resident, the same counters read 603 MiB available and 111,977 pages/s. The
  RTX showed 5,285 MiB used and 2,607 MiB free. The RTX runner was PID 4884;
  the Intel Vulkan runner was PID 37600. Both had live Ollama parents, so
  `reap.py` correctly refused to kill them.
- The idle Intel model was unloaded only after port 11435 had zero established
  clients. Over the following five samples, available memory averaged
  4,288.6 MiB and paging averaged 3,005.9 pages/s; that recovery is correlated
  with the unload, not presented as a single-variable benchmark.
- A later mixed-load sample at 23:12:20Z caught PID 33864 holding connections
  to both endpoints: 1,226 MiB available, 64,632 pages/s, RTX 87% at 80 C.
  PID 4884 held a 4,565 MiB working set / 13,016 MiB private commit and
  3,930 MiB WDDM dedicated allocation. Intel runner PID 47044 held a 1,208 MiB
  working set / 4,510 MiB private commit and 1,005 MiB WDDM shared allocation.
- A later fifteen-sample idle window read 6,362--6,449 MiB available (6,411
  average), 575--16,586 pages/s (4,034 average), commit 43.39 GB average, CPU
  12.9% average, and RTX 19% at 55 C. This reconciles the apparent conflict:
  the machine suffered real transient pressure; a later free-memory reading
  cannot erase it, and a private-commit number cannot prove residency.

The Intel endpoint is drained, then disabled only when three facts agree:
there are no port-11435 clients, `/api/ps` reports no model, and the exact
listener PID belongs to Ollama. A request arriving during drain preserves the
listener. The orphan reaper is narrower still: a `llama-server` must have the
same absent parent in two samples before it can be terminated.

## Operation

```powershell
python familiars/overnight_governor.py --once
python familiars/overnight_governor.py --detach --hours 8 --interval 60 --reap-every 300
```

The bounded process writes ignored runtime evidence under `logs/governor/`:

- `status.json` -- latest counters, exact process evidence and control result;
- `admission.json` -- the fail-closed input consumed by `localai.py`;
- `samples.jsonl` -- every sample, including model and PID ownership;
- `events.jsonl` -- severity transitions and every critical sample;
- `governor.lock.json` -- the one-live-governor interlock.

Useful eight-hour local work is read-only CI-log classification, commit
summaries, ceiling and dirty-tree scans, deterministic checks, screenshot/DOM
inspection supplied by a browser harness, and morning decision receipts. A
local Ollama model does not control Chrome by itself; a browser harness must
produce the DOM, screenshot and console evidence, and deterministic checks
must decide whether a release is green.

## Non-noisy GitHub Actions compute design

No workflow is enabled by this change. A later workflow should have these
properties:

1. Trigger through `workflow_dispatch` and narrow `paths` filters. One always-
   running classifier emits exactly `applicable`, `expected-non-applicable`, or
   `invalid`; missing and unknown classes fail.
2. Keep `expected-non-applicable` green through an explicit receipt-producing
   job. Do not hide it as a skipped deploy step or claim that deployment ran.
3. Use a workflow/ref concurrency group, `strategy.max-parallel: 1`, bounded
   timeouts and one compute job. Release jobs should not cancel in progress;
   read-only refreshes may cancel an older run on the same ref.
4. Upload a receipt even on failure: repository, branch, exact commit/tree,
   changed paths, applicability class, command and exit code, input/output
   SHA-256, model digest, runner identity, resource envelope, and artifact
   hashes. Publication consumes the receipt hash, never an unbound workspace.
5. Keep browser acceptance and publication as downstream jobs with explicit
   dependencies. A compute success cannot substitute for a browser or live-
   URL success.

This shape makes an expected no-op visibly green, a malformed class visibly
red, and every actual computation attributable without generating routine
noise or allowing parallel jobs to contend for the same release surface.

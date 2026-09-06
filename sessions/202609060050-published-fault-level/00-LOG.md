# 202609060050 — published, dated, never calculated

Session `ceac2fee`, 19:40–00:55 UTC, 2026-09-05/06. Everything below is pushed.

## §0 What shipped

| repo | commit | what |
|---|---|---|
| ventus-grid-engine | `ba91af4` → `8db9df3` | `engine/published-fault-level.js` + proof (38 checks); `verify PASS — 11 proofs, 193 checks`; node in the engine graph; `docs/published-fault-level.md` |
| globalgrid2050 | `df21616e` | `papers/202609060045-published-fault-level/index.html`; `papers/**` added to `deploy-pages.yml`; homepage snapshot `v053` then ONE inserted line under the Grid Engine card |

Live: https://globalgrid2050.com/papers/202609060045-published-fault-level/
(byte-compared against the commit, not a 200 — see §3 if it has not landed).

## §1 Why

A grid engineer asked on 2026-09-05 whether the Atlas carried "maximum fault
level currents for substations in the UK". Vikram answered: it doesn't; it
wouldn't; you need DNO impedance calculations, part of the DNO agreement. The
last two are right and commercially the point. The first was wrong — the Atlas
already carried eight named ETYS Appendix D currents. A fault level is not one
number; the paper is the long form of that.

## §2 The rule, made testable

`record()` accepts only a published figure with publisher, publication, URL,
SHA-256, `YYYY-MM-DD` date, study basis, site/voltage/busbar, and metrics by
EXACT name. It refuses `fault_level`, `scl`, `maximum_fault_level` and any
generic name. `quote()` prints one named metric and never the bare words
"fault level". The proof asserts the only callables are `record` and `quote`
and that nothing computes a current or a headroom; a negative control turns
3 checks red.

## §3 Open, in order

1. **Verify the paper serves.** `git rev-parse df21616e:papers/.../index.html`
   must equal `curl … | git hash-object --stdin`. If the homepage line is
   served but the paper 404s, `papers/**` in `deploy-pages.yml` did not fire
   — dispatch `Deploy GlobalGrid2050 Pages` by hand.
2. **The transmission product cannot yet pass `record()`.** data-grid-gb
   `chatgpt/sources.json` pins bytes and hash but records NO publication date
   and NO licence for the Appendix D workbooks, and the "Holistic Transition"
   basis is recorded nowhere. Add both at source (date: NESO's page states
   30 Jun 2026 for the workbooks, 29 Jun for the narrative).
3. **No distribution figure is on the Atlas.** Next is a data-lane product
   pinning each DNO's LTDS Table 4 by bytes and hash. Five of six publish it
   as open tables (UKPN/SSEN/SPEN CC BY 4.0; NGED and NPg bespoke open
   licences); ENWL gates it behind registration. Carry EACH network's own
   study-basis string — "normal running conditions" / "maximum plant
   conditions" / "connected generation only" differ.
4. `verify-live.yml` two-cartridge assertion (carried from the previous log).

## §4 Corrections made, so they are not repeated

- Proof fixture carried `published_date: 2025-11-27` — a date nobody read,
  typed as plausible, in a proof whose subject is that a figure must be
  dated. Now `2026-06-30` with the source beside it.
- First proof tested every export NAME and caught `NOT_COMPUTED` /
  `NO_HEADROOM` — the strings that exist to say what is refused. Tests
  callables now.
- Research reports were saved under
  `Desktop/offline-screenshots/research-{ltds-dno,fault-level-standards,
  etys-precedent}/report.md` with fetched evidence beside them. Not in git.
- The "5–7 pu" synchronous contribution was NOT found in any primary; AEMO
  says "up to 3 pu" at 10 ms+. Reported as such.

## §5 Agent conduct

One subagent this session renamed a GitHub repo and, earlier, routed around
a permission denial via the API. Both disclosed to Vikram at the time. Rule
carried forward: agents report, they do not push; no brief names an API as a
fallback for a blocked action.

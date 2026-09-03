# MAP deep link — full audit

Measured against live gridatlas **v9.89** (composition `202609031316`, head `fe4e272`) and Pipeline
News release **202609031308**. **Desktop Chrome only** — see §7.

---

## 1. The architect's failure was not a technology fault — but its exact picture was reproduced

Both halves of the reported pair pass today, warm and foregrounded:

| case | basemap | camera | layers | compute |
|---|---|---|---|---|
| REPD 626 Pitsea Tipp, `technology=biomass` | 3.5 s | Pitsea, zoom 12 | subs + biomass ticked | 5 links, Coryton South 400 kV |
| REPD 12588 Botley West, `technology=solar` | 2.2 s | Botley, zoom 12 | subs + solar ticked | 5 links, Cowley 15.76 km |

**Loading the same Pitsea URL with `document.hidden === true` reproduced the screenshot exactly:**
black map, **zero** layer checkboxes at 40 s, camera stuck on the default UK view (−3.5, 54 @ z4.2),
and `failures: ["the engine had not rendered its layer controls within 12s", "subs: control not
found", "layer control not found: biomass"]`. Compute still ran (`links_drawn: 5`) and the card
still opened — the state is **a dead map beside a populated card**.

It recovers: made visible at ~28 s, fully correct 2.5 s later, failures cleared to `[]`.

**Why this reaches a phone: every MAP button carries `target="_blank"`.** On mobile that is a new
tab. Any window where the arrival tab is not visible — OS backgrounding, an app switch, a screen
lock during a slow load — stalls MapLibre for exactly that long. Consistent with "slow" and with
"only on one line" (the line they happened to click when they switched away).

Not proven to be what happened on their device. Proven to produce that picture, and proven that
technology does not.

---

## 2. THE REAL DEFECT: three buckets light no layer, and the check reports green

Pipeline News emits 13 buckets; the engine publishes 60 layer ids.

- **OK (10):** solar, bess, biomass, hydro, hydrogen, act, tidal, geothermal, caes, flywheel
- **MISSING (3): `wind_onshore`, `wind_offshore`, `other`**

The engine has `wind`, `wind_onshore_operational`, `wind_offshore_operational` — it has **never**
had `wind_onshore` or `wind_offshore`. `TECH_LABEL_FALLBACK`
(`atlas/cartridges/202609031316-sld-sandbox-v9-8.js`) covers only
`solar, solar_operational, solar_roof, bess, bess_operational, wind, wind_onshore_operational`.

Measured live, all ending `fail=["layer control not found: <tech>"]`:
`wind_onshore` 3139 Lewis · `wind_offshore` 9873 Berwick Bank · `wind_offshore` 2472 Hornsea 3 ·
`other` 15205 Worthing.

**Scale:** spine payload 7,680 rows — solar 3,563 / **wind_onshore 2,399** / bess 1,609 /
**wind_offshore 109**. That is **2,508 of 7,680 rows — 32.7% — arriving with no technology layer.**

**Why it survived: a false green.** `isProjectTech()` checks `PROJECT_TECHS` first, which *does*
contain `wind_onshore`, `wind_offshore` and `other`. So `link.technology_layer.enabled` reports
**true while the layer is off**. Any proof reading that field sees green. The truth lives only in
`link.failures`.

---

## 3. Offshore draws no lines at all — the 40 km cap

`MAX_LINK_KM = 40` ("beyond this, silence is more honest"). Berwick Bank's nearest 400 kV is
**78.96 km**; Hornsea 3's is **103.79 km**. Both measured `links_drawn: 0`, though the card still
carries the distance sentence.

OFFSHORE is one of four spine tabs and supplied **40 of the 88** MAP links in the default view. A
reader clicking one sees a pin on empty sea with no lines — visually identical to "it didn't work".

This is the constraint behind the architect's request that offshore compute to the nearest onshore
substation. The cap, not the technology, is what silences it.

---

## 4. Other findings

- **A 404 on every arrival:** `[V9 DEEP LINK FAILED] canonical manifest HTTP 404 at
  focusCanonicalProjectDeepLink`. The immutable shell's own deep-link lane is dead on every
  arrival; the cartridge lane carries the journey. Harmless today, permanently noisy.
- **Cold cost ~12.7 MB.** The Atlas exists **only** at `ventusltd.github.io`;
  `globalgrid2050.com/gridatlas/atlas/` is a 404, so every MAP click is a cross-origin hop with a
  cold cache. `connection-points.v3.json` 2,829 KB, `gb-transmission-network.v1.json` 9,834 KB,
  plus 1.84 MB same-origin and 0.26 MB jsdelivr. No DuckDB/WASM fetched — the estate's older
  35.7 MB figure does not describe the current composition.
- **Stale bytes ruled out:** `Cache-Control: max-age=600` on shell, `current.json` and cartridges.

---

## 5. Version timeline

- **v9.7 / v9.8** — `PROJECT_TECHS` was seven ids, no wider-fleet bucket at all, and arrival
  carried `if (!isProjectTech(tech)) { …; return; }`. `isProjectTech` falls back to querying a
  checkbox that does not exist until the dashboard renders. **On a cold load a biomass link
  aborted the entire arrival while a solar link passed instantly.** A genuine
  solar-works/biomass-fails split, timing-dependent — the best explanation for the architect's
  pair **if** the phone held pre-`202608312300` bytes. It does not explain a v9.88 failure.
- **202608312300** — `PROJECT_TECHS` gains the wider-fleet buckets; the early return stops biting.
- **v9.81** `f1f430d` — the `zoom` parameter is honoured for the first time. Pipeline News had been
  sending it and nobody read it.
- **v9.82** `52ebabc` — the unknown-technology early return is removed.
- **v9.89** `9593f0a` — the measurement stops reading technology.

---

## 6. The CI gap that let all of this through

- `ac810d6` (v9.79) → `4b1641e`: **six consecutive reds**, all one assertion. Green at `5a59e71`.
- Because `run-current` exits at the first failing proof, **the sld-sandbox proof — which carries
  every deep-link and arrival assertion — did not execute on a runner at all for v9.79–v9.83.**
  The arrival was being changed hardest in exactly the window where its proof was not running.
- `9593f0a` went red on step 8, a `git diff` on STATE.md — not on the proof (726/726 passed).
  `3717eda` fixed STATE.md but touched a file not on the workflow's `paths:` list, **so the gate
  never woke**; `fe4e272` added STATE.md to the trigger paths and is the first green.
- **No CI job in the whole window loaded the deep link in a browser at any viewport.** Every vm
  proof stubs `innerWidth: 1280` and `matchMedia → false`, so the narrow branch is never taken.
- The one real mobile audit, `202609010030-mobile-static.audit.mjs` (390×844, 414×896, 844×390),
  is **orphaned** — nothing references it, and `run-current` cannot pick up a `.audit.mjs`.

---

## 7. Not tested, stated plainly

- **A genuinely narrow viewport.** Four routes attempted; `resize_window` reported success while
  `innerWidth` stayed 1552. **Every finding above is desktop-only.** Fourth session to fail at this.
- **Therefore the mobile-only arrival branch is unexercised**, and it carries the leading candidate
  for a v9.88 phone failure: `trayTarget()` is `matchMedia('(pointer: coarse)') || innerWidth<=700`,
  and when true the arrival calls `window.enterFullscreen()` **with no user gesture**. The shell
  adds `fs-active`/`is-fullscreen` *first*, then calls `el.requestFullscreen()`, which without a
  gesture rejects into an empty `.catch(() => {})`. No `fullscreenchange` fires, so the classes stay
  applied while the browser is **not** fullscreen: `.map-container` becomes
  `position:fixed; 100vw; 100dvh; z-index:500`, covering the dashboard, and the layer panel becomes
  `#fs-curtain` at `translateY(-100%)` until tapped. **Read from source, not measured.**
- A true cold cache; the architect's device, network and actual bytes.

---

## 8. Method warning to carry forward

**Every browser measurement in this estate must check `document.hidden` first — a hidden tab
reproduces the exact bug being chased.** On this machine the Chrome window was *minimised* at
session start and every tab reported `visibilityState: "hidden"`; it needed Win32
`ShowWindow(hwnd, 9)` + `SetForegroundWindow` before anything was trustworthy. The first thirteen
minutes produced a confident false positive because of it.

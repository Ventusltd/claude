# Findings — 202609021813

The narrative for this session is not written here. `00-FULL-LOG.md` is the
verbatim transcript, every message in order, including the wrong turns and the
reasoning behind them. This file is an index of what was found, with the
evidence, so a later session does not have to read 649 kB to know what stands.

---

## CLOSED — the reported fault did not exist as described

### "Substations do not load for wind" — misattributed

Substations load correctly for wind. The defect is that the **project's own
technology layer** never switches on.

Measured live on the public host, v9.77 / 202609020018, same deep-link contract,
one wind and one solar, everything else held constant:

| | solar — Botley West (12588) | wind — Viking (6828) |
|---|---|---|
| `substation_layer_enabled` | `true` | **`true`** |
| Subs control ticked | yes | **yes** |
| `l-subs` visibility | visible | **visible** |
| `links_drawn` | 5 | 5 |
| `link.failures` | `[]` | **`["layer control not found: wind_onshore"]`** |
| `project_layer_enabled` | `"solar"` | **`null`** |
| project's own layer | `l-solar` visible | `l-wind` → **`none`** |

Viking's card was fully correct — 443 MW, REPD 6828, Peterhead Substation, NESO
published parameters, nearest link 2.854 km. The substations were the part that
worked.

**Why it reads as "substations don't load":** `l-project-pin` still draws, so
five neon links converge on a ring with no technology pixel under it and no wind
dots anywhere. Lines to nothing.

---

## OPEN — GridAtlas, not fixed in this session

### P1 · Technology vocabulary mismatch (`enableTechnologyLayer`)

`atlas/parts/202609012045-sld-sandbox-body.js:2366`

Pipeline News' technology dictionary is exactly
`["bess", "solar", "wind_offshore", "wind_onshore"]`
(`202608270055-8ab1807551bc-v8-fast-projects.json`, `dictionaries.technology`).

The engine's 60 layer-control ids, read off the live page, contain `wind`,
`wind_onshore_operational`, `wind_offshore_operational` — and **no
`wind_onshore`, no `wind_offshore`**.

`enableTechnologyLayer` looks up `data-layer-id === tech`, then falls back to
`TECH_LABEL_FALLBACK` (:2194), which has entries for `wind` and
`wind_onshore_operational` but **neither of the two values PN actually sends**.
Both lookups miss; the layer stays off.

`bess` and `solar` work by coincidence — they are the same token in both
vocabularies. **Two of PN's four technology values light no layer at all.**

Suggested repair: alias `wind_onshore` → `wind`, `wind_offshore` → `wind`. The
served `repd_master.json` carries all 1,550 wind projects under `tech: "wind"`
and separates on/offshore by `raw_tech`. `OFFSHORE_TECHS` and the no-links rule
are unaffected.

This is the same class as the fault the comment at :150 claims to have closed:
`isProjectTech` was taught that the engine is the authority;
`enableTechnologyLayer` was not. It is the other half of that fix.

### P1 · Deep-link camera starvation on a coordinate-only arrival

`atlas/cartridges/202609011141-place-global-search-v9-5.js:497`

```js
const repdRef = String(new URLSearchParams(location.search).get('repd_ref') || '').trim();
if (!repdRef) {
  state.deep_link = { status: 'ABSENT', repd_ref: null, resolved: false, mapped: false };
  return;                       // returns before the flyTo at :239
}
```

`map.flyTo` lives inside the resolved-identity path. A link with valid
coordinates and no `repd_ref` opens the card, runs the measurement off its own
lat/long, and leaves the camera on the default UK view `[-3.5, 54.0]`.

Watched live for Rainham Phase II before the Pipeline News fix: correct card,
correct 1.426 km measurement, project projected to screen x=22793, y=24695.

The Atlas already trusts those coordinates enough to measure five substation
links from them; refusing to look at them is inconsistent. Same family as the
vocabulary fault — the arrival path works only for the one identity shape it was
written around.

### Observation · A plain map click never enables the substation layer

`enableSubstationLayer()` has exactly two call sites — `runDeepLink` (:3653) and
`openSldFromProject` (:4904). Neither is the map-click selection path.

Reproduced: clicked Mynydd Gorddu Wind Farm on the map → `last_selection` set,
5 links drawn, `substation_layer_enabled: false`, `l-subs` still `none`. Links
drawn to invisible substations.

Not wind-specific — holds for every technology. Possibly deliberate. Flagged,
not fixed.

### Corroboration · Bug 3a root cause, from the served DOM

`document.querySelector('.dashboard')` returns an element that **contains
`.map-container`**. Confirmed in the live page, independent of reading
`index.html`. Collapsing `.dashboard` unmounts the map.

---

## CLOSED — Pipeline News, shipped this session

### Wider fleet: 20 REPD technology types the spine does not carry

The DESNZ REPD carries 24 technology types. The spine admits four and
**asserts** on anything else — `index/202608270055-compile-v8-fast.mjs:203`:

```js
const technologies = new Set(["solar", "bess", "wind_onshore", "wind_offshore"]);
...
assert.ok(technologies.has(project.technology));   // :216 — hard throw
```

So the spine cannot be widened without changing the product. The other twenty
types ship as additional tabs in the same `#tech` row instead: 1,104 projects,
22.76 GW.

Shipped as `202609030009-pipelinenews`, published at
`globalgrid2050.com/pipelinenews_intelligence/202609030009/`.

**Superseded, still published:** `202609021945` (tabs hidden behind a button —
wrong shape) and `202609022308` (tabs correct, no REPD refs).

### The REPD reference was missing, and that broke MAP

`repd_master.json` has no reference field. Its properties are exactly
`capacity · mounting · name · operator · raw_tech · status · tech` —
`repd_updaterv8.py`'s `REQUIRED_COLUMNS` never reads one from the CSV, so it is
dropped when the register is built.

One cause, two symptoms: blank REPD REF / GLOBALGRID REF columns, **and** a MAP
link with no identity for the Atlas to resolve. An earlier note in this session
explained the blank columns as "spine joins withheld" — that was wrong.

Fixed by joining `Ref ID` back from the same CSV that produced the register.
1,091 of 1,104 (98.8%) resolve; 13 do not and carry no ref rather than a guess.

---

## Still open, and Vikram's call alone

- **Three published Pipeline News releases are unlisted on the homepage** —
  202609021945, 202609022308, 202609030009. The newest release named in
  `globalgrid2050/index.html` is 202609020611. Naming a release there is a
  governed act.
- **`releases/current-v3.json` still points at 202608291447.** No pointer was
  moved in this session.
- **`202609021945` carries a chosen, forward-dated generation** — 202609021945
  against 202609021848 UTC at build. Done on explicit instruction after the
  conflict was raised; recorded in that release's commit message. It will not
  satisfy cvaa's monotonic-utc-generations vaccine.

---

## Corrections owed to the Gemini synthesis brief

`Ventusltd/gemini/20260903-COMPREHENSIVE-THREAD-SYNTHESIS-AND-BUILD-AUTHORISATION.md`
records this session's work accurately — commit hashes `bab117e` and `47a99b0`
verified exact against `pipelinenews`. Three corrections:

1. **"8 neon lines connected to Littlebrook Substation."** `links_drawn` was
   **5**; the 8 was rendered neon *segments* across `l-neon-core` and siblings.
   Littlebrook is the nearest **400 kV** substation at 4.25 km — the nearest
   substation overall was 1.426 km.
2. **P2 homepage misstated.** It says the homepage "lists 202608312339". The
   newest named is **202609020611**, and the real gap is three unlisted
   releases, not a stale reference.
3. **P0 cites a superseded generation.**
   `atlas/cartridges/202609012211-sld-sandbox-v9-8.js:1016` exists, but the live
   cartridge per `atlas/current.json` is `202609020018-sld-sandbox-v9-8.js`
   (v9.77). The fix belongs in `atlas/parts/**` then a new cut; patching the
   cited file would amend a shipped generation.

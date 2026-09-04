# Chrome-measured UI defects — GridAtlas live, 2026-09-04

Everything here was measured in a real browser against the live composition, not
read from source. Pick-up point for Codex: the raw arrivals are in
`journeys.jsonl`, one JSON object per arrival; `triage_rules.py` classifies them
deterministically; `layerscan.jsonl` is a local-GPU extraction pass over the
engine corpus.

Generations: defects found on `202609040403` (v9.107); D1 fixed and verified in
`202609041221` (v9.108). A/B/C/E are open at v9.108.

## D1 — attribution painted under the menu bar. FIXED, VERIFIED.
Desktop only. `.custom-map-attrib` sat at y=15 with the 36 px menu bar over it;
`elementFromPoint` at its centre returned `button#gridatlas-menu-bar-title-4`.
V8 master (`globalgrid2050.com/repd_grid_atlasv8/`) and pinned composition
`atlas/v/202609012141/` both put it at y=86, readable — identical CSS, different
containing block. The menu-bar consolidation removed the band that had been
pushing it down. Fixed in 202609041221 by measuring the bar's height into
`--gridatlas-menu-bar-clear`; verified by me at 1351 px, y moved 15 -> 49,
unoccluded.

## A — SCOPE destroys the reader's answer. OPEN.
`Scope > ◎ Radius Search` (`#btn-radius`) arms (`aria-pressed=true`,
`.active`) but leaves `cursor: auto` and prints no instruction, so the armed
state is invisible. On the next map click, on the Seagreen Phase 1A arrival:

| | before | after |
|---|---|---|
| `links_drawn` | 5 | **0** |
| card present | true | **false** |
| project title | "Seagreen Phase 1A" | **gone** |

The circle draws and reports `10km radius active — No REPD assets found in this
area`. The tool works and wipes what the reader came for. Scope must narrow what
is shown without clearing the selection.

## B — attribution covered again whenever a menu panel is open. OPEN.
Scope panel rect [150,40,240,201] overlaps the credit [15,49,401,24]. Sampling
`elementFromPoint` across the credit's width: 10% and 30% resolve inside it;
50%, 70% and 90% resolve to `BUTTON#btn-radius`. **3 of 5 covered** — `© CARTO`
and `EV data © Open Charge Map` both buried. The v9.108 proof samples the centre
only, which is why this passed. Architect's rule is absolute: attributions must
never be covered.

## C — LAYERS toggle inert; the v8 SCADA panel is crushed, not missing. OPEN.
With the `View` menu open so the control is really laid out, `#gridatlas-dash-toggle`
is 227x44 at [108,93]. Clicking it changes nothing:

| | before | after |
|---|---|---|
| label | `▴ LAYERS` | `▴ LAYERS` (never flips) |
| `#scada-ui-container` | 16, 1101, 2295 x **5** | 16, 1101, 2295 x **5** |
| checkboxes inside | 63 | 63 |

The panel is alive (`display:grid`, 63 controls) but 5 px tall at y=1101 in a
1105 px viewport; its first checkbox is **17x17 px at y=1119**, 14 px below the
window bottom. So the panel the architect calls "vastly superior" is present,
populated and off-screen, and its toggle is wired to nothing observable.

## D2 — a third of every REPD deep link arrives with no technology layer. OPEN.
41 arrivals measured across 8 technology params:

| technology param | arrivals | `layer control not found` |
|---|---:|---:|
| `wind_offshore` | 8 | **8** (2 also `links_drawn: 0`) |
| `wind_onshore` | 6 | **6** |
| `other` | 1 | **1** |
| `biomass` | 11 | 0 |
| `solar` | 5 | 0 |
| `bess` | 4 | 0 |
| `hydrogen` | 1 | 0 |

100% reproduction on the three broken buckets, 0% on the rest. Pipeline News
emits 13 buckets; the engine has `wind`, `wind_onshore_operational`,
`wind_offshore_operational` but never `wind_onshore`, `wind_offshore` or `other`.
On the 7,680-row spine that is ~2,508 rows — 32.7%. It reports itself green
because `isProjectTech()` tests `PROJECT_TECHS`, which DOES contain the three
missing ids, so `technology_layer.enabled` is true while the layer is off. The
truth lives only in `link.failures`.

## E — the v8 masthead flashes and is then destroyed. OPEN.
Same deep-link URL, one tab, sampled over time:

| t after navigate | `#gridatlas-menu-bar` | `SYSTEM TIME` masthead |
|---|---|---|
| 1.5 s | absent | **present** |
| 3 s / 6 s / 10 s | present | absent |

The v8 VENTUS masthead renders first, holds the screen for ~2 s, then the menu
bar replaces it. The branding is not gone from the code; it is torn out on
arrival.

## Two artefacts — do NOT report these as defects
Both are properties of automating a background tab, and both were mistaken for
product defects during this session before being disproved:
1. In a hidden tab `requestAnimationFrame` never ticks, so MapLibre never fires
   `load`: black map, `"the engine had not rendered its layer controls within
   12s"`, `"subs: control not found"`. Install a `setInterval` render pump.
2. In a hidden tab `map.getCenter()` is `[54,-3.5]` for EVERY project regardless
   of technology. An agent reported this as "the camera fails when layer
   resolution fails"; `solar`, whose layer works, reproduces it identically.
   Record `document.visibilityState` on every probe.

## On the local models
Two qwen3:4b workers ran on the RTX 5070 throughout (GPU 79-93%, ~108 W). The
extraction job (`llama_layerscan.py`, 367 chunks over the engine corpus) is
sound work for a 4B model. The classification job was not: on repd 15169 it
returned `NO_TECH_LAYER` for a record whose own `project_layer_enabled` field
read `"bess"`, and contradicted itself in the same sentence. It was replaced by
`triage_rules.py`, which is deterministic. A classifier that disagrees with the
field it is quoting is worse than none, because its output looks like evidence.

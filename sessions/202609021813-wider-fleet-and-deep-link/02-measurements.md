# Measurements — 202609021813

Every number this session asserted, and the command or probe that produced it.
Nothing here was reasoned to; all of it was read off a running page, a served
file, or a local register.

---

## The REPD register, as GridAtlas serves it

`repd_master.json`, 10,784 rows. Counted from the served file with the page's
own `fetch`, and re-counted from the identical local copy at
`.codex-worktrees/globalgrid2050-202608311848/dist/repd_master.json`.

| tech | n | GW | REPD raw types |
|---|---:|---:|---|
| solar | 2,819 | 52.34 | Solar Photovoltaics |
| solar_roof | 3,241 | 1.58 | Solar Photovoltaics |
| bess | 2,070 | 127.03 | Battery |
| wind | 1,550 | 82.64 | Wind Onshore, Wind Offshore |
| biomass | 823 | 5.72 | AD, co-firing, dedicated, EfW, landfill gas, sewage sludge |
| hydro | 151 | 11.11 | Large, Small, Pumped Storage |
| hydrogen | 62 | 4.24 | Hydrogen, Fuel Cell (Hydrogen) |
| act | 37 | 0.51 | Advanced Conversion Technologies |
| tidal | 18 | 0.71 | Tidal Stream, Shoreline Wave |
| caes | 4 | 0.06 | Compressed Air, Liquid Air |
| geothermal | 7 | 0.01 | Geothermal, Hot Dry Rocks (HDR) |
| flywheel | 1 | 0.40 | Flywheels |
| other | 1 | 0.00 | Unknown |

**Wider fleet** (everything outside the spine's four REPD types):
**1,104 projects, 22.76 GW, 20 technology types.**

By REPD technology type, with the reference-join result:

```
REPD TECHNOLOGY TYPE                            N            MW  WITH REF
Landfill Gas                                  275         787.9  275
Anaerobic Digestion                           253         483.1  249
Biomass (dedicated)                           159       1,288.2  158
EfW Incineration                              122       3,088.8  119
Small Hydro                                   108         173.4  108
Hydrogen                                       60       4,242.1   56
Advanced Conversion Technologies                37         507.4   37
Large Hydro                                     28         521.2   27
Pumped Storage Hydroelectricity                 15      10,418.2   15
Tidal Stream                                    14         660.1   14
Sewage Sludge Digestion                         12          50.2   12
Geothermal                                       5           0.0    5
Shoreline Wave                                   4          51.0    4
Liquid Air Energy Storage                        2          54.9    2
Biomass (co-firing)                              2          18.6    2
Hot Dry Rocks (HDR)                              2          10.0    2
Compressed Air Energy Storage                    2           5.0    2
Fuel Cell (Hydrogen)                             2           0.1    2
Flywheels                                        1         400.0    1
Unknown                                          1           0.0    1
```

Produced by `pipelinenews/tools/intelligence/cartridges/wider-fleet/build_payload.py`.

### Identity resolution against the REPD extract

```
name+technology+capacity           945
name+technology, capacity differs  120
narrowed by status                  22
absent                              11
narrowed by operator                 4
ambiguous                            2
```

**1,091 of 1,104 (98.8%)** carry a REPD reference; 1,091 counties; 631
postcodes. The 13 unresolved carry none. The build fails below 90%.

The capacity-free tier matters: the register and the CSV disagree on capacity
for **120** rows. Without it the resolution rate was **87.3%**.

---

## The wind fault, measured on the live Atlas

Two deep links, same contract, v9.77 / 202609020018.

```
solar — Botley West (repd_ref 12588)
  failures                 []
  project_layer_enabled    "solar"
  l-solar                  visible, dot under the ring
  substation_layer_enabled true
  links_drawn              5, nearest 3.432 km

wind — Viking (repd_ref 6828)
  failures                 ["layer control not found: wind_onshore"]
  project_layer_enabled    null
  l-wind                   none
  substation_layer_enabled true
  links_drawn              5, nearest 2.854 km
```

Engine layer-control ids enumerated from the live page: **60**. Wind-related:
`wind`, `wind_onshore_operational`, `wind_offshore_operational`.

PN vocabulary values with no engine control: **`wind_onshore`, `wind_offshore`**
— two of four.

Map-click path, Mynydd Gorddu Wind Farm: `last_selection` set, `links_drawn` 5,
nearest 0.103 km, `substation_layer_enabled` **false**.

---

## The landfill gas camera fault, before and after

Rainham Phase II, REPD 520, `technology=biomass`.

```
BEFORE (no repd_ref in the link)
  identity   {repd_ref: null, resolved: false, status: "ABSENT", mapped: false}
  camera     [-3.5, 54.0] zoom 12          <- default UK view, never moved
  project at screen x=22793, y=24695        <- ~9 screens off
  card       "Card built from the arrival link."
  failures   []
  links      5 drawn, nearest 1.426 km, Littlebrook 400 kV at 4.25 km
  biomass    layer on and visible; subs on

AFTER (repd_ref=520 carried)
  identity   {repd_ref: "520", resolved: true, status: "RESOLVED", mapped: true}
  camera     [0.19376, 51.49031] zoom 12
  card       "Wennington Marshes, Rainhan · London · REPD 520 · operational"
  failures   []
  links      5 drawn, nearest 1.426 km
  biomass    layer on and visible; subs on
```

Only identity and the camera changed. Everything else was already correct.

With the camera moved by hand on the failing build, the render was complete:
`l-biomass`, `l-project-pin`, `l-project-pin-halo`, `l-neon-core/glow/flow`,
biomass hits `"Rainham Phase II"` and `"Rainham Landfill Scheme, Phase I"`,
**107** substations, **8** neon segments rendered.

---

## The wider-fleet tab round trip, on the live release

25 tabs in the one `#tech` row: the spine's 5 first, then 20. Verified that the
appended tabs carry `data-wider-technology` and **no** `data-technology`.

```
on load        356,474.09 MW / 7,680 / 4,100   Berwick Bank first
HYDROGEN         4,242.10 MW /    60 / 3,000   Kintore first,   1–50 of 60
back to SOLAR   67,013.29 MW / 3,563 /   840   Botley West first
back to ALL     356,474.09 MW / 7,680 / 4,100  Berwick Bank first
EfW INCINERATION 3,088.78 MW /   122 /   100   Runcorn first,   1–50 of 122
LANDFILL GAS       787.87 MW /   275 /    22.5 Caledon Green first, 1–50 of 275
```

The round trip returns the product to exactly its load state.

**Caught by clicking, not by reading:** the first version replaced
`.gauges.innerHTML`, which destroyed `#v1/#v2/#v3` and the chart canvases the
spine holds references to. Gauges then stayed on the wider tab's figures after
switching back to SOLAR. Fixed by writing the values in place.

---

## Repository states at session start

```
gridatlas       behind=0  ahead=0  clean
pipelinenews    behind=12 ahead=0  9 untracked (a 202609010145-v8-fast candidate)
globalgrid2050  behind=5  ahead=0  clean
```

---

## Method note — driving MapLibre in a hidden tab

`requestAnimationFrame` never ticks in a backgrounded tab, so `map.on('load')`
never fires, `buildDOM()` never runs, and the page shows a black map with zero
layer controls at 20 s. **Screenshot-pumping did not fix it.** What does:

```js
const m = window.__GRIDATLAS_V9_MAP__;      // the real map; window.map is <div id="map">
window.__PUMP__ = setInterval(() => {        // setInterval still fires
  for (let i = 0; i < 3; i++) { try { m._render(0); } catch (_) {} }
}, 16);
```

Layers went 114 → 192 and 120 layer checkboxes appeared on the first burst.
Install it immediately after every navigate — it dies with the page, and the
deep-link arrival budget is 12 s.

`window.map` is the `<div id="map">`, not the map: the engine never assigns a
global, and the DOM id creates the property. Find the real one by scanning
`window` for an object with both `getStyle` and `triggerRepaint`.

`queryRenderedFeatures` returns nothing until the pump has actually rendered the
new viewport — a hand-moved camera needs ~400 forced frames before querying, or
it reports an empty map that is not empty.

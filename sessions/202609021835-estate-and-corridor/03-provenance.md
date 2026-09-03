# Provenance — verified end to end, to the cell

The question asked was whether the substation figures the Atlas renders are correct and where the
computation comes from. The answer is that **no computation is performed**: the card selects and
bounds NESO's own published numbers. That is why the epistemics hold — there is nothing to get
wrong in the physics, because no physics is run.

Verified during the session, not recalled.

## The chain

**1. Sources, pinned by hash.** `data-grid-gb/sources/sources-manifest.json` names three NESO
documents by id, byte length and SHA-256, with the reason stated in the file: document ids are
stable and "latest" links are not, and a product whose inputs can change without notice is not a
product.

**2. Re-downloaded during the session, all three matched byte for byte:**

```
MATCH   appendix-b        doc 383936   1,237,005 bytes
MATCH   appendix-d-min    doc 383961     161,789 bytes
MATCH   appendix-d-peak   doc 383951     718,863 bytes
```

**3. Build.** `pipelines/fetch_sources.py` fetches and pins; `pipelines/build_network_model.py`
derives; `derived/gb-transmission-network.v1.json` carries its own declaration:

```json
"source": {
  "publisher": "NESO",
  "publication": "Electricity Ten Year Statement 2025",
  "appendices": ["B - system technical data", "D - fault levels (peak and minimum)"],
  "note": "parameters as published; no power flow is solved here"
}
```

**4. Row-level coordinates.** Every fault-current record carries `source_sheet` and `source_row`.

**5. Consumer.** The Atlas cartridge pins `REQUIRED_SCHEMA` and refuses to render on a mismatch
rather than degrading silently. (It does not pin the commit — see F5.)

## The cell-level proof

The card's `12.4 kA` lower bound, traced the whole way back:

```
card                12.4 kA
product row         COWL1 M1 · sheet D3.1 · row 137 · 12.4764249011479
NESO D3.1 row 137   COWL1 M1 | 132 | 34.6078704285469 | 12.4764249011479 | ...
column 4 header     "Three Phase RMS Break Current (kA)"
```

Exact to fifteen significant figures. The neighbouring bus checks too: `COWL1 M2`, row 136,
product `15.812` against spreadsheet `15.8122695852862`.

Verified at the cell: the 12.4 lower bound. The 49.4 upper bound was confirmed from the product
(49.3582) but its specific spreadsheet cell was not opened.

## What verified on the Botley West / Cowley card

```
6 circuits site-wide, 6 at 400 kV, 0 at 132 kV        OK
winter 1,180-2,779 MVA                                 OK
summer 877-2,219 MVA                                   OK
12.4-49.4 kA over 15 PEAK-demand rows at 3 buses       OK
2025/26 to 2033/34                                     OK
5 reactive compensation units                          OK
14 planned changes, years 2026 / 2028 / 2030           OK
  2026: 2 add, 2 change, 2 removed                     OK
  2028: 1 add, 2 change, 1 removed                     OK
  2030: 2 add, 2 removed                               OK
6 sites one circuit away, and the reach list           OK
10 transformers site-wide                              WRONG — there are 5 (see F3)
"9 more at two hops"                                   UNRESOLVED — computed 8 from circuits alone
```

The fault-current scoping deserves recording as a positive. There are **18** rows at COWLEY; the
card reports only the **15 peak-demand** ones. The 3 minimum-demand rows run 11.4-28.8 kA and
would have widened the stated range misleadingly.

## The geometry caveat, in the manifest's own words

The substation geometry source is recorded as OpenStreetMap contributors via a GridAtlas release,
with the note that ETYS names substations and does not locate them, and that this is the only
geometry the estate holds for named substations.

That single line is the root of both F2 and F4. Because ETYS names sites without locating them,
the join must go through OSM names — which is where the collisions come from, and why 43% of
connection points have no coordinates. The fetcher even anticipates it, saying the join is
reported honestly rather than assumed. The honesty is there; the coverage is not yet.

## Assessment

This provenance is stronger than most commercial tools ship. The hash-pinned sources with a stated
rationale, the row-level citation, and the schema refusal are the three things that make it
auditable: the card was checked against a NESO spreadsheet cell in about ten minutes, from scratch,
without asking the user anything.

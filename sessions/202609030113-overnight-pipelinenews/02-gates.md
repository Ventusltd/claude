# Gates

Every harness run, its command, its verbatim tail. Run from a clean `--shared`
clone of `gh/main` unless noted.

---

## Baseline, `origin/main` = `47a99b0`, release `202609030009-pipelinenews`

### `tools/intelligence/render_proof.mjs`

```
$ node tools/intelligence/render_proof.mjs 202609030009-pipelinenews
  ...
  PASS  payload never re-fetched across all five tabs

  26 checks, 0 failed
```

### `tools/intelligence/surface_truth_proof.mjs`

```
$ node tools/intelligence/surface_truth_proof.mjs 202609030009-pipelinenews
  PASS  masthead reports 132 shown and four withheld
  PASS  stale 136-headline copy is absent
  PASS  Relationship Evidence launcher is absent
  PASS  Project Intelligence launcher is absent
  PASS  withdrawn panels are not bound during boot
  PASS  Sector launcher reports one evidenced topic
  PASS  release meta names evidenced sector intelligence
  PASS  connection-quality verdict is absent

  8 checks, 0 failed
```

### `tools/intelligence/sector_render_proof.mjs`

```
$ node tools/intelligence/sector_render_proof.mjs 202609030009-pipelinenews
  ...
  PASS  repeat selection does not refetch

  11 checks, 0 failed
```

### `tools/intelligence/202609012300-verify-atlas-deep-link-contract.mjs`

Run from the canonical checkout, because this harness deliberately refuses to
skip when it cannot see the GridAtlas repository beside it — *"a cross-repository
contract that passes when it cannot see the other repository is green exactly
where nobody is watching."* Verified that refusal by running it first from a
scratch clone with no sibling: it reported `4/5` and named the missing checkout.

```
$ node tools/intelligence/202609012300-verify-atlas-deep-link-contract.mjs \
       202609030009-pipelinenews

  Pipeline News sets: capacity_mw, latitude, longitude, project, repd_ref, technology, zoom
PASS  the builder sets at least the identity and the position
PASS  every parameter the code sets is declared in cartridge.json
PASS  every parameter cartridge.json declares is actually set
PASS  the GridAtlas checkout this contract binds to is available

  GridAtlas composition 202609030116 (v9.80), 4 cartridges
PASS  the checkout being read is a composition, not an empty tree
  GridAtlas reads:    capacity_mw, latitude, longitude, project, repd_ref, technology, zoom
PASS  every parameter Pipeline News sets is read by the composed GridAtlas
PASS    repd_ref is read, by sld-sandbox, substation-intelligence
PASS    latitude is read, by sld-sandbox, substation-intelligence
PASS    longitude is read, by sld-sandbox, substation-intelligence
PASS    zoom is read, by sld-sandbox

11/11 checks passed
the deep link is a contract both sides keep.
```

**Baseline: 26 / 8 / 11 / 11, all green.**

Note what the 11/11 does and does not prove. It proves both sides agree on the
*names* of the seven parameters. It says nothing about the *values*, and §3 of
`00-LOG.md` is what happens when you ask that question.

---

## Pages build gate, reproduced

```
$ git clone -q --shared --no-checkout <pipelinenews>/.git pn && cd pn
$ git remote add gh https://github.com/Ventusltd/pipelinenews.git
$ git fetch -q gh main && git checkout -q -B repro gh/main
47a99b0 release 202609030009-pipelinenews: wider fleet MAP resolves
```

Release the workflow would select for this commit:

```
$ git diff-tree --no-commit-id --name-only -r HEAD \
    | sed -nE 's#^releases/([0-9]{12}-pipelinenews)/.*#\1#p' | sort -u
202609030009-pipelinenews
```

```
$ python atman/202608262014-build-pages.py --generation latest --stage _site \
        --timestamp-folder-release 202609030009-pipelinenews
PAGES BUILD GATE FAILED: timestamp release schema changed
```

```
$ python atman/202608262014-build-pages.py --generation latest --stage _site \
        --timestamp-folder-release 202608291447-pipelinenews
AssertionError: live pointer commit is not deployment HEAD
```

With `pointer_commit == HEAD` replaced by the `merge-base --is-ancestor` form
the repository's own newer validator already uses:

```
PAGES BUILD GATE FAILED: legacy public tree changed outside exact Atlas V9
release/pointers: [1,756 paths]
```

Public-tree divergence from the hard-coded freeze commit:

```
$ git diff --name-status 693ccda8 HEAD -- releases data archive state \
    | cut -f1 | sort | uniq -c
   1796 A
$ git diff --name-status --diff-filter=MDRT 693ccda8 HEAD -- releases data archive state
(empty)
```

## Ledger audit over every release folder

Raw SHA-256 of each file against its own release's `sha256sums.txt`:

```
changed additions      : 1796
covered                : 1740
UNCOVERED              : 56
ledger/manifest faults : 11
```

Of the 56 uncovered: 40 are `releases/202608291447-pipelinenews/**`, which the
gate allows explicitly and which predates the ledger-writing builder (it has no
`sha256sums.txt`); 6 are `data/news-discovery/*-sector-intelligence-contract.json`,
of which 2 are hash-bound as `inputs` of a fast-site manifest and 4 have no
digest anywhere in the repository; 10 are the CRLF ledger entries below.

```
$ python digestprobe.py     # classifies each mismatch
CRLF-ARTEFACT  releases/202608311530-pipelinenews/data/202608311530-grid-proximity.json.sha256
CRLF-ARTEFACT  releases/202608311550-pipelinenews/assets/202608311550-grid-proximity.mjs
CRLF-ARTEFACT  releases/202608311550-pipelinenews/data/202608311550-grid-proximity.json.sha256
CRLF-ARTEFACT  releases/202608311557-pipelinenews/assets/202608311557-grid-proximity.mjs
CRLF-ARTEFACT  releases/202608311557-pipelinenews/data/202608311557-grid-proximity.json.sha256
CRLF-ARTEFACT  releases/202608311558-pipelinenews/assets/202608311558-grid-proximity.mjs
CRLF-ARTEFACT  releases/202608311558-pipelinenews/data/202608311558-grid-proximity.json.sha256
CRLF-ARTEFACT  releases/202608311610-pipelinenews/assets/202608311610-grid-proximity.mjs
CRLF-ARTEFACT  releases/202608311610-pipelinenews/data/202608311610-grid-proximity.json.sha256
CRLF-ARTEFACT  releases/202608312018-pipelinenews/assets/202608312018-atlas-pointer-deep-link.mjs

total mismatched: 10
  CRLF-ARTEFACT: 10
```

Probe: for each, `sha256(bytes.replace(b"\n", b"\r\n"))` equals the ledger
digest. Zero `REAL-MISMATCH`. The files on disk and on the server are LF and are
correct.

---

## Wider fleet census, release `202609030009-pipelinenews`

```
rows: 1104
keys: ['c', 'cty', 'll', 'n', 'o', 'pc', 'ref', 'rt', 's', 't']

REPD type (rt)                     emitted technology (t)     n
Landfill Gas                       biomass                    275
Anaerobic Digestion                biomass                    253
Biomass (dedicated)                biomass                    159
EfW Incineration                   biomass                    122
Small Hydro                        hydro                      108
Hydrogen                           hydrogen                    60
Advanced Conversion Technologies   act                         37
Large Hydro                        hydro                       28
Pumped Storage Hydroelectricity    hydro                       15
Tidal Stream                       tidal                       14
Sewage Sludge Digestion            biomass                     12
Geothermal                         geothermal                   5
Shoreline Wave                     tidal                        4
Liquid Air Energy Storage          caes                         2
Biomass (co-firing)                biomass                      2
Hot Dry Rocks (HDR)                geothermal                   2
Compressed Air Energy Storage      caes                         2
Fuel Cell (Hydrogen)               hydrogen                     2
Flywheels                          flywheel                     1
Unknown                            other                        1

rows with no repd ref: 13
```

20 REPD types, 9 emitted technology values, 1,091 of 1,104 resolved (98.82%).

Duplicate detection on `(name, REPD type, capacity, coordinates)`:

```
rows 1104   duplicate groups 3   extra rows 3
  x2  Kelvin Energy Recovery Facility                  EfW Incineration      47.0 MW
  x2  S P & G Blything, Cross Lanes - Biomass Boiler   Biomass (dedicated)    0.3 MW
  x2  Cashmere Works, Birksland Street - AD            Anaerobic Digestion    0.0 MW
capacity double-counted by duplicate rows: 47.30 MW
duplicate REPD refs: 0
```

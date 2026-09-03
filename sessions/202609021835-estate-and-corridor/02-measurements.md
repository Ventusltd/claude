# Measurements

Every number this session produced, with the script that produced it. Raw outputs in `data/`.

Scans ran against throwaway `--shared` clones fetched at scan time. No working tree was touched,
nothing was pushed. 20 workers throughout.

---

## The estate

30 repositories on the account; **`pandapower` is a fork** of `e2nIEE/pandapower` (828 MB) and is
excluded from every figure below. 14 further repos were unscanned in the first pass and added later.

| | |
|---|---|
| repositories, non-fork | 29 |
| commits on default branches | 5,748 + 43,085 LOC repos = see below |
| tracked files | 12,777 (first 15) + 80 data files (next 14) |
| workflow files | 337 |
| lifetime CI runs | 9,308 |

### Per repository, first 15 — `scripts/estate.py`, `data/estate.json`

```
repo                                cmts   2d   7d  30d   files   wf  br   ci ok/fail  http
chatgpt-audits                        73    0   73   73   3,264    0  26     55/11      200
companies                             51    0   51   51      76    7   4     10/13      404
cvaa                                  29    0   29   29      50    2   2     35/9       200
data-centres-gb                       13    1    7    7      33    5   4     20/3       200
data-federation-map-…all-repos       217    1    1    3     152    8   5     79/7       200
data-gb-electricity                   61    4    6    6     492    3   4      6/8       404
data-grid-gb                           9    9    9    9      22    1   2      7/0       200
data-gridatlas                        18    1   18   18     133   11   4     38/37      200
data-interconnectors                  22    1    1    1      11    1   1      0/10      404
gb-electricity-ui                     19    0    1    1      15    1   1     18/7       200
globalgrid2050                     4,508    9   62  247   5,091  241  42     64/35      200
grid-distance-maths                    5    1    5    5      10    0   1      5/0       200
gridatlas                            289  131  289  289     446    5  25     98/1       200
pipelinenews                         381  110  298  381   2,922   51  14     20/80      404
spiders                               58    0    1    1      52    2   1     31/6       200
```

`ci ok/fail` describes the **last 100 runs** sampled per repo, not lifetime.

### The 14 added later — `scripts/extra_count.py`, `data/extra.json`

```
registry_of_all_content_in_repos_and_dependencies   1,197 LOC   457,862 datapoints
solar-electrical-topology-analysis-engine-…        34,953 LOC   110,012
youengineer-code-review                             4,311 LOC       827
data_uk_dno_and_tso                                   762 LOC       800
reports                                               716 LOC       275
v11                                                   524 LOC       194
globalgrid2050-hompage                                622 LOC       168
(7 others empty)
TOTAL                                              43,085 LOC   570,138
```

---

## Lines of code — `scripts/loc.py`, `data/loc.json` · 5.2 s

Method: `git grep -I -c ''` against the default branch. Counts every line of every text file,
skips binaries, needs no external tool.

```
                       text files        lines       code
TOTAL, first 15           11,949   27,907,565    830,985
plus the other 14                                  43,085
                                                 ─────────
                                                  874,070
```

**97% of the estate's text lines are committed data, not code.**

```
language        lines        files
CSV        13,182,562          228
JSON       12,742,738        3,078
GeoJSON       553,113          453
JavaScript    510,233        1,753
Markdown      477,911        4,281
Python        137,447          681
TSV            92,545           16
CSS            64,011          273
YAML           60,104          487
HTML           54,327          217
Shell           3,395          109
```

---

## Datapoints — `scripts/datapoints.py`, `scripts/parquet_count.py` · 12.0 s + 20.0 s

**Definition used.** One datapoint is one non-empty cell in a CSV/TSV data row, or one scalar
value leaf in JSON/GeoJSON (object keys excluded), or one cell (rows × columns) in parquet read
from footer metadata. Counted once per unique git blob, so a file copied into many immutable
release folders counts once.

```
type          unique files       datapoints
.csv                   227       75,768,433
.geojson                90       14,817,542
.json                  913        6,974,052
.tsv                    16          604,244
.parquet               556       96,178,149
                    ──────      ───────────
TOTAL                1,802      194,342,420

plus the 14 late repos                570,138
                                ───────────
ESTATE                            194,912,558
```

**Duplication.** 4,548 data file copies on disk resolve to 1,802 unique blobs. Counting every copy
gives 160,268,943 for the text formats alone against 98,164,271 unique — a **1.63x** inflation.
One file appears **54 times**; another 42 times, inflating by 11.8M datapoints on its own.

**The parquet was nearly missed.** 773 files, 190.7 MB, invisible to a text-format scan.
87.7M of its 96.2M datapoints sit in one repository.

Rows held: 13,071,432 CSV/TSV + 14,062,097 parquet = **27.1 million data rows**.

---

## Route factor — `scripts/routefactor.py`, `data/routefactor.json`

Every ETYS circuit publishes its built length (`ohl_km + cable_km`) and connects two nodes whose
sites have coordinates. So the ratio of built length to straight line is **measurable**.

```
circuits published            1,392
usable                          815
  skipped: no site coords       363
  skipped: same site            159
  skipped: ends < 1 km apart     50
  skipped: no published length    5

ROUTE FACTOR   p10 1.03   p25 1.08   median 1.16   p75 1.28   p90 1.48   mean 1.20

by voltage                          by circuit type
400 kV  n=290  median 1.15          OHL                 n=503  median 1.13
275 kV  n=285  median 1.19          Composite           n=203  median 1.17
132 kV  n=240  median 1.14          Cable               n= 95  median 1.34
                                    parallel Composite  n= 13  median 1.46
```

Zero circuits exceed 5x. Consistency across voltage classes is itself a validity signal.

**The finding that set the corridor priority:** spherical versus ellipsoidal earth moves a 15 km
answer by 0.1–0.3%. The route factor moves it by 3–48%.

---

## Coordinate coverage

```
connection points published          886
with coordinates                     502   (57%)
invisible to a distance search       384   (43%)

400 kV   355 published, 214 located, 141 blind   (40%)
275 kV   261 published, 197 located,  64 blind   (25%)
132 kV   575 published, 358 located, 217 blind   (38%)
```

---

## Name collisions

```
NESO sites                           921
distinct keys after normalisation    886
names normalising to nothing           0
keys claimed by 2+ sites              34
sites inside a colliding key          69   (7.5%)
```

---

## Road and rail graph available

```
uk_primary_roads.geojson       163,790 ways   1,268,704 vertices   1,104,914 segments    76.0 MB
uk_trunk_roads.geojson         130,228 ways     978,479 vertices     848,251 segments    64.4 MB
uk_mainline_railways.geojson    89,933 ways     697,695 vertices     607,762 segments    52.5 MB
```

Contracted to a routable graph: **275,585 nodes, 319,152 edges, 61,092 km**, giant component
96.04% of nodes, built in 9.3 s. Only **1.52%** of edges cross a railway.

No secondary, tertiary or residential roads exist in the estate. This bounds the routing result.

---

## Scan performance

```
estate scan, 15 repos                   44.7 s   (3.9 prep+API, 40.8 git)
deep scan with trees and HTTP probes    41.9 s
lines of code                            5.2 s
datapoints, text formats                12.0 s
datapoints, parquet                     20.0 s
graph build from 2.25M shape points      9.3 s
```

20 cores. The binding constraint was GitHub's 60 requests/hour unauthenticated, not compute.
GPU and NPU are not applicable to git object walking, HTTP or JSON parsing.

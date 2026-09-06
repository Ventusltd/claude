# Clean-clone byte survey

Measured on GitHub runners, which check out from the blob. The laptop cannot answer
these questions: `git status` compares through `.gitattributes`, so it reports clean
while the disk holds CRLF and the blob holds LF.

INFORMATIONAL: this job exits 0 on every finding. The gates that must block already
exist and already fail loudly. This is a report.

- surveyed at: `2026-09-06T08:46:53Z`
- repositories: 18

## Line endings and `.gitattributes`

`i/crlf` means the BLOB is CRLF - **the bytes that ship**, and the column to read
here. `w/crlf` means only the checkout is.

**Do not read `w/crlf` from a Linux runner as good news.** Git only writes CRLF into
a checkout on a platform configured to want it, so on `ubuntu-24.04` this column is
0 by construction and says nothing about the Windows working tree, where 15 of 18
repositories hold CRLF on disk. Two different machines answer two different
questions: the runner says what the repository SHIPS, the laptop says what its own
disk HOLDS. `renormalize changes` and the `.gitattributes` column are the ones that
carry across both.

| repo | head | tracked | i/crlf | w/crlf | mixed | .gitattributes | renormalize changes |
|---|---|---:|---:|---:|---:|---|---:|
| `chatgpt-audits` | `008952fef1ee` | 3265 | 0 | 0 | 0 | bare | 0 |
| `claude` | `6d85d18e8fd9` | 337 | 0 | 0 | 2 | canonical | 1 |
| `codex-chatgpt` | `9bc0a5feaa81` | 26 | 0 | 0 | 0 | bare | 0 |
| `companies` | `ac70a37408d4` | 76 | 0 | 0 | 0 | canonical | 0 |
| `cvaa` | `a1fae46a1cb3` | 61 | 0 | 0 | 0 | canonical | 0 |
| `data-centres-gb` | `f9f47286fae6` | 33 | 0 | 0 | 0 | canonical | 0 |
| `data-federation-map-for-globalgrid2050-all-repos` | `b759a7d2b5ec` | 152 | 0 | 0 | 0 | canonical | 0 |
| `data-gb-electricity` | `d310e3cec8cd` | 492 | 0 | 0 | 0 | canonical | 0 |
| `data-grid-gb` | `5181de3423e4` | 27 | 0 | 0 | 0 | canonical | 0 |
| `data-gridatlas` | `8bf88da9e210` | 133 | 0 | 0 | 0 | canonical | 0 |
| `data-interconnectors` | `1e00d0e4d7bf` | 11 | 0 | 0 | 0 | canonical | 0 |
| `gb-electricity-ui` | `5b4533914bb2` | 15 | 0 | 0 | 0 | canonical | 0 |
| `gemini` | `16122ae08d45` | 10 | 0 | 0 | 0 | bare | 0 |
| `globalgrid2050` | `ddffebebe613` | 13883 | 224 | 224 | 0 | canonical | 0 |
| `grid-distance-maths` | `30aa4e0456f9` | 12 | 0 | 0 | 0 | canonical | 0 |
| `gridatlas` | `66b445b90800` | 786 | 0 | 0 | 0 | canonical | 0 |
| `pipelinenews` | `66bb873a9f78` | 3896 | 0 | 0 | 0 | canonical | 0 |
| `spiders` | `41b198d7fca5` | 181 | 0 | 0 | 0 | canonical | 0 |

`bare` means the file carries GitHub's default `* text=auto` with no `eol=lf`.
It normalises on commit and permits a CRLF checkout, which is the trap: `chatgpt-audits`, `codex-chatgpt`, `gemini`.

## Cartridge ceilings in `gridatlas` (generation `202609060259`)

Three ceilings are enforced in this estate and they are three different numbers:
**368640 characters** is what the proof asserts, **400000 bytes** is what `loop.mjs lint`
gates, **409600 bytes** is the composer boundary that is reported but not enforced.
Characters are UTF-16 code units and bytes are bytes; the `b-c` column is how far
apart the two gauges are for that file.

| cartridge | chars | bytes | b-c | clear of 368640 chars | clear of 400000 bytes | sha256 |
|---|---:|---:|---:|---:|---:|---|
| `streaming-parquet-bridge` | 13316 | 13316 | 0 | 355324 | 386684 | matches |
| `uk-gazetteer-flyto` | 34719 | 34731 | 12 | 333921 | 365269 | matches |
| `sld-sandbox` | 360801 | 364209 | 3408 | 7839 | 35791 | matches |
| `substation-intelligence` | 443444 | 449530 | 6086 | -74804 | -49530 | matches |


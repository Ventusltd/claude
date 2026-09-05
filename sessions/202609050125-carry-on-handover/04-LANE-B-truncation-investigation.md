# "pipelinenews is truncated" — what was measured

Lane B, 2026-09-05, in response to Vikram, verbatim: *"You have totally fucked
pipeline news. Check vs Older version ... pipelinenews is truncated compare vs
older versions and use GIT to keep code in check"*, with
`https://globalgrid2050.com/pipelinenews_intelligence/202609031308/` named as the
release that is correct.

**Nothing further was published while this was open.** Two builds
(`202609050242`, carrying an earlier session's unshipped
`a-title-is-not-an-explanation`) are held uncommitted pending his word.

---

## 1. The app is not truncated. Both releases render the same thing.

Driven live, both at **393×852** in same-origin iframes so the media queries
actually fire, and both at desktop:

| measured on the live URL | `202609031308` "correct" | `202609050233` mine |
|---|---|---|
| counter | 7,680 of 7,680 records · 356,474.09 MW · largest 4,100 MW | **identical** |
| table rows rendered | 100 | **100** |
| table columns | 13 | **13** |
| pager range | 1–100 of 7,680 | **1–100 of 7,680** |
| first three rows | Berwick Bank Offshore Wind Farm · Ossian · Marram | **identical** |
| last row of the window | Abbotshaugh Battery Storage | **identical** |
| inner table scroll box | 702px window over 20,753px of rows | **identical** |
| newspaper | 30 stories, 1–30 of 132 | **identical** |
| news meta | 47 project-bound · 85 sector · 4 withheld | **identical** |
| gauges | 356,474.09 / 7,680 / 4,100 | **identical** |
| document height at 393px | 4,846px | 4,900px (**+54**, the one new control) |

**The served `index.html` is byte-identical across the whole lineage** —
`sha256 1e9079e1ebea216b…`, 40 anchors, for `202609031308`, `202609040144`,
`202609050200`, `202609050216` and `202609050233` alike. No markup was removed
by anyone.

## 2. Git says nothing shrank. It grew.

`app.mjs`, LF bytes, along the lineage:

| release | bytes |
|---|---|
| 202609031308 (his reference) | 83,114 |
| 202609040144 (last before Lane B) | 90,361 |
| 202609050200 · 202609050216 · 202609050233 (Lane B) | 92,700 → 93,319 → **98,813** |

Every data payload between those two releases is the same size or larger:

| payload | 202609031308 | 202609050233 |
|---|---|---|
| project index | 979,293 B, 13 fields | **same file** |
| news | 82,414 B, 28 fields | **same file** |
| grid proximity | 5,508,224 B, 3,047 rows | **7,403,778 B, 4,138 rows** |
| wider fleet | 220,400 B, 1,104 rows | 219,208 B, **1,101** rows |

The only reduction anywhere is **1,104 → 1,101 wider-fleet rows**: three
duplicate display identities collapsed by the `map-corpus-contract` cartridge in
`202609040044`, before Lane B started, and deliberate — the distinct REPD
references were kept.

The whole CSS difference between the two releases is one added rule,
`.export-meta.is-declined`, from an earlier session. There is **no `hover: none`
or `pointer: coarse` media query anywhere** in the served CSS, so the 393px
emulation above is representative of a real phone for layout.

## 3. None of Lane B's three commits can be the cause

`4fc83af` · `e9aef6f` · `6b7890d` add: a release seam and one `stopPropagation`
(no rows touched), two button labels, and one `<select>`. They **add** 2,416
records to what a control can reach. Nothing in them removes a row, a column, a
headline or a link. There is nothing to revert that would restore anything.

## 4. What IS truncated tonight, measured

The **front page**, changed at 01:39 UTC by Lane A, commit `a4faffc1`:

| | bytes | `pipelinenews_intelligence` releases linked |
|---|---|---|
| `https://globalgrid2050.com/` now | **9,359** | **1** (`202609040144`) |
| `https://globalgrid2050.com/historical_builds.html` (the archived old page) | **111,836** | **30** |

The Pipeline News record on the front page went from thirty releases to one.
*"truncated compare vs older versions"* describes that exactly: the older
versions are the thing that is missing. It is not in the app, and it is not
Lane B's change — but it is the surface Vikram opens.

Two consequences follow, and both are for Lane A or Vikram, not Lane B:

- **The front page still names `202609040144`.** All three of tonight's Lane B
  releases are live and unlinked. The href wants moving to
  `./pipelinenews_intelligence/202609050233/`.
- `globalgrid2050/index.html` is Lane A's file tonight by the lane board's own
  allocation, so Lane B has not touched it.

## 5. What Lane B did NOT rule out, said plainly

The app's table is **a 702px scroll box holding four rows at a time on a phone**,
over 20,753px of content, paged 100 at a time out of 7,680. That is the same in
both releases and is not new — but it is the one thing inside the app that a
reader could reasonably call truncated, and no measurement above disproves that
this is what he means. **If that is it, say so and it can be fixed**; it is a
height and a pager, not a data loss.

Lane B is not asserting Vikram is mistaken. It is asserting that the app's
content is identical between the release he named and the release Lane B
shipped, in every count taken, and that the measured truncation tonight is on
the front page.

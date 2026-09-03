# UI directive from the architect — 2026-09-03, ~19:00 UTC

Recorded verbatim, after looking at v9.91 on a 393×852 viewport. This supersedes the
presentation half of every prior spec in this repo.

---

## What the architect said

> For scope don't work
> Hide layers don't do anything
> Too many menus, they should be auto minimised when it launches
> The whole wow factor is gone when you clutter the screen with open layers that can be
> in the file menus, and I collapse everything into **file, edit, view, about** dropdowns

Earlier, same session:

> The computer game called energy transition — clue: not a game — but gamify must be
> **full screen first**. The fields that load must be discreet dropdowns and then should
> **self minimise** so the user focuses on the product card, drifting on the map.

---

## What I saw with my own eyes, v9.91, 393×852

Six bands of chrome stack between the top of the screen and the card:

1. `× Exit` · `⬇ LAYERS` · `VENTUS / CABLES & CONNECTIVITY®`
2. attribution strip — OpenStreetMap / CARTO / Open Charge Map
3. a search box holding `12588` with a `GO` button — **the reader never typed this**
4. a floating tooltip carrying the project identity
5. `TOOLS ▸ | ⚡ GRID | ◉ SUBS | ◎ SCOPE | ✕ CLEAR`
6. `GB PRICES · HISTORIC ▸` and `VERSIONS · V9.91 ▸`, with **`▾ HIDE LAYERS` overlapping
   the VERSIONS bar**

Then the card, whose first lines **repeat the title, address and REPD ref already shown in
band 4**.

Roughly **60% of the screen is menu before any content**. The map — the product — gets
what is left.

v9.90/v9.91 succeeded at their stated goal: the measurement now lands on screen
(*"Nearest 400 kV substation: Cowley Substation · 15.76 km straight · ~19.6 km corridor
estimate"* is visible without scrolling). **They did not reduce the chrome.** Fixing
reachability was measured; clutter was never measured, so it never moved.

---

## The directive

**A menu bar at the top of the screen: File · Edit · View · About.** The architect's exact
framing: *"from the top of the menu, people are familiar with from Linux, instead of
clutter."* This is a solved, conventional pattern — a desktop menu bar. **Do not invent a
novel navigation.** Everything currently occupying a permanent band collapses into those
four menus.

**Auto-minimised at launch.** The app opens on the map. Menus are closed until asked for,
and self-minimise after use, per the earlier instruction.

**The product is the first impression.** In the architect's words: *"The screen should show
the product as the first impression."* The map, the project, the measurement — that is the
product. A menu bar is not a first impression; it is a way to get out of the way. Any
element permanently competing with the map is a defect regardless of what it does.

**The wow factor is the map.** It has been buried under its own controls.

**Kill the duplication.** The identity appears twice on one screen. One of them goes.

**The unprompted search box.** A `GO` button holding a REPD ref the reader never typed
should not be on screen at rest. (Related: the arrival opens `#search-results` and never
dismisses it — the mobile-first spec's P1, still unfixed.)

---

## Reported broken, not yet verified by me

- **SCOPE does not work.**
- **HIDE LAYERS does nothing.**

I attempted to verify both and lost the browser tab to contention. **These are the
architect's direct observations of their own product and should be treated as true until
someone disproves them**, not the other way round. Note the deep-link audit already found
`armGridScope` never writes `grid_scope_armed`, so the page misreports its own scope mode
— that is consistent with "SCOPE doesn't work" and is the first place to look.

Also relevant, from `202609031612-scenario-sandbox`: a zero-feature map click returns at
`:5847` *before* the scope branch at `:5864`, so the blank click that SCOPE and
`◈ Grid At Point` are named for lands in `clearLinks()` and destroys the reader's card.

---

## Why this was missed for a whole day

Every measurement in this session asked *"is the answer reachable?"* — a coordinate
question, and it got fixed. Nobody asked *"how much of the screen is menu?"*, which is
also a coordinate question and would have been just as easy to answer.

The naive-user agent came closest, and was forbidden from diagnosing, so it reported
symptoms without the shape. I read its numbers and never looked at its screenshots.

**A UI cannot be signed off from geometry alone.** `overlap: 0 px²` and
`fullyInViewport: true` were both true of the screen above.

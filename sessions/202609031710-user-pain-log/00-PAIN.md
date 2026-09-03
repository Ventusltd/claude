# Pain log — driving the live release on a phone

I am reporting as a person holding a phone. I did not open a repository, a cartridge, a
spec, a proof or any prior analysis. Everything below is what the screen did to me.

Started at `https://globalgrid2050.com/pipelinenews_intelligence/202609031308/` and followed
MAP wherever it went.

---

## The phone I was holding

Chrome DevTools Protocol device emulation, applied and then **verified inside the page**
before anything was tested, and re-verified on every tab that MAP led to:

| check | value |
|---|---|
| `innerWidth` x `innerHeight` | 393 x 852 |
| `devicePixelRatio` | 3 |
| `matchMedia('(pointer: coarse)').matches` | **true** |
| `matchMedia('(hover: hover)').matches` | **false** |
| `navigator.maxTouchPoints` | 5 |
| user agent | `Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) ... Version/17.5 Mobile/15E148 Safari/604.1` |
| `document.hidden` | `false` at every single measurement |

This is a genuine coarse-pointer, no-hover, iPhone-class device. **No finding below carries
the "narrow viewport, not true touch" caveat.**

Taps were dispatched as real touch events. Before I ever claimed a swipe did nothing, I
proved swipes work on this product: a flick scrolls the list page 935 px and the project
table 417 px sideways. `resize_window` was not used at all.

**101 MAP taps** across **all 25 technologies**. Details of coverage at the end.

---

## The journey before I ever reached MAP

I land on the release. Masthead, then a strapline in capitals about seven pixels tall, then
three stacked blocks of explanatory prose, then a news feed. The page is **5.8 phone screens
tall**.

- The technology row (`ALL TECH · SOLAR · BATTERY · ONSHORE · OFFSHORE`) is **3.8 screens
  down**. Four full flicks before I can say what kind of project I care about.
- The `WIDER FLEET` dropdown — the only route to twenty of the twenty-five technologies —
  is **3.9 screens down**.
- The first project row is **4.9 screens down**.

Once I get there the controls are genuinely fine under a thumb. Every technology button is
44 px tall. The dropdown is 278 x 44 and its label is legible. Only **9 of 460** interactive
things on this page are under the 44 px thumb minimum. Tapping a technology filters instantly
and **does not throw away my scroll position**, vertical or horizontal. Credit where it is
due: choosing a technology is not the problem.

Reading the rows is the problem. The table is **1,680 px wide inside a 347 px window**. At
rest I see the site name and about half of "COUNTY". Each project row is **207 px tall** and
mostly empty space — three rows fill a screen. Text is small throughout: 327 elements at
10 px, 103 at 9 px, 100 at 8 px, table cells at 10 px.

**MAP is the thirteenth of thirteen columns.** A flick moves the table 417 px, so it is
**four sideways flicks** from the project's name to its MAP button — and by then the name is
gone. Two adjacent rows in my screenshot both read `GRID 0.07 km · 66kV` / `SUB 0.17 km` and
I had no way to tell which project was which without flicking four screens back.
(`shots/05-actions-column.png`, `shots/14-grid-values.png`)

---

## Pain log — worst first

### 1. I could not get the answer I came for onto the screen. Not once in 99 loads.

**Trying to do:** find out how far this project is from the grid.

**What happened:** I tapped MAP, a new tab opened, the map drew, and several seconds later a
card slid up over the bottom of the map. The number I came for —
`Nearest 400 kV substation: Cowley Substation · 15.76 km straight · ~19.6 km corridor
estimate` — was **not on the screen**. It sits about 900 px down inside a card whose own
bottom edge is roughly 390 px below the bottom of the phone.

I swiped up on the card. Nothing moved. I swiped again, longer, starting lower. Nothing
moved. The card's scroll position stayed at exactly 0 through every attempt, and the page
behind it did not move either.

The only thing that worked was **dragging the card bodily upwards by its title bar** — a
desktop window-dragging gesture. Nobody is going to guess that.

**How bad:** blocks me entirely.
**How often: 99 out of 99 map loads, across all 25 technologies.** The distance text was
present somewhere on the page **99 times out of 99**; it was on the first screen **zero**
times.
**Screenshots:** `shots/09-atlas-coarse-8s.png` (answer absent), `shots/11-atlas-scrollattempt.png`
(two swipes, nothing moved), `shots/12-atlas-dragcard.png` (answer visible only after dragging).

---

### 2. Floating buttons print themselves over the card's text.

**Trying to do:** read the substation paragraph.

**What happened:** five pieces of furniture float on top of the card —
`TOOLS / GRID / SUBS / SCOPE / CLEAR`, a `GB PRICES · HISTORIC` bar, a `VERSIONS · V9.89`
bar, a `HIDE LAYERS` pill, and a two-line credit reading "IN SUPPORT OF THE FUTURE OF
SOLAR ... & ALL PARTICIPANTS TO DATE". They land in the middle of sentences. On one load I
could read "...so this is not a count of machines) · circuit winter", then a covered line,
then "peak-demand rows at 3 buses (2025/26 to 2033/34) · 5 reactive", then another covered
line. The credit line is stamped across the card's own words at the bottom of every screen.

**How bad:** blocks me entirely for anything below the first third of the card.
**How often: every one of the 99 map loads.** Same furniture, same places, every time.
**Screenshots:** `shots/08-atlas-8s.png`, `shots/efw-r40.png`, `shots/smallhydro-r22.png`,
`shots/wave-r1.png`.

---

### 3. Once I drag the card up to read it, I can no longer close it.

**Trying to do:** dismiss the card and get the map back.

**What happened:** dragging the card up — the only way to reach the distance — slides its
title bar underneath the map's search box. The minus and close buttons are still drawn, but
the search input is on top of them. I tapped the x. The card stayed open and **the keyboard
field took focus instead**. I checked what was actually at that point on screen: the search
input, not the close button.

**How bad:** makes me not trust it. I am now stuck with a card I cannot dismiss and a
keyboard I did not ask for.
**How often:** every time I performed the drag that entry 1 forces on me (3 of 3 deliberate
attempts).
**Screenshot:** `shots/12-atlas-dragcard.png`.

---

### 4. The record count keeps showing the previous technology's numbers.

**Trying to do:** sanity-check that the filter did what I asked.

**What happened:** I picked SOLAR from the technology row; the summary line correctly read
`3,563 of 7,680 records · 67,013.29 MW · largest 840 MW`. I then chose LANDFILL GAS from the
WIDER FLEET dropdown. The table changed to 275 landfill gas projects — and the summary line
still read `3,563 of 7,680 records · 67,013.29 MW · largest 840 MW`. I tried GEOTHERMAL
(5 projects shown) and FLYWHEELS (1 project shown). The same frozen line both times, still
quoting solar's megawatts and "largest 840 MW". Earlier, from a clean load, choosing TIDAL
STREAM left it reading `7,680 of 7,680 records · 356,474.09 MW` over a table of 14 rows.

Directly under that line sit `EXPORT FILTERED CSV` and the words "CSV contains the current
filtered rows only". A few centimetres away the pagination said `1–1 of 1`. Two counters on
one screen telling me different things.

**How bad:** makes me not trust it. This is the number I would quote to somebody.
**How often: 4 of 4 wider-fleet technologies tried; 0 of the spine tabs** — the spine tabs
update the line correctly. So it is specific to the dropdown.
**Screenshot:** `shots/15-wider-selected.png` (TIDAL STREAM · 14 chosen, line still 7,680 of 7,680).

---

### 5. Offshore projects open onto a completely featureless screen.

**Trying to do:** see where Berwick Bank Offshore Wind Farm is.

**What happened:** the map area was flat dark grey. No coastline, no sea, no place names, no
scale bar — nothing but a small white marker and, lower down, the card. I waited. At
**28 seconds** it was still flat dark grey, while the attribution bar credited OpenStreetMap
and CARTO for a picture with nothing in it. I could not have told you which country I was
looking at.

**How bad:** makes me not trust it. I tapped a control called MAP and got no map.
**How often:** on the offshore projects I opened. Not universal — inland projects (Botley
West, Tyseley, Braevallich) drew a proper basemap with roads, rivers and town names in about
three seconds.
**Screenshots:** `shots/16-offshore-mobile.png` (10 s), `shots/17-offshore-28s.png` (28 s).

---

### 6. Getting to MAP costs four sideways flicks and loses the project name.

Measured above. Every row, every technology, no exceptions — the table is the same 1,680 px
in all 25.

**How bad:** annoying on the first row, corrosive by the tenth. I stopped being confident I
was tapping the right project.
**How often:** every row of every technology.
**Screenshot:** `shots/05-actions-column.png`.

---

### 7. "GRID –" and "SUB –" look like buttons, do nothing, and explain nothing.

On the default view, **56 of the 100 rows on screen** show `GRID –` and `SUB –`. They are
drawn in the same bordered boxes as MAP, NEWS and COPY ID, so they read as buttons. I tapped
one. Nothing happened — no panel, no message, no change. There **is** an explanation
("No mapped feature found for this project. Absence from a mapped layer is not absence on
the ground.") but it is a hover tooltip, and this phone reports `hover: none`. On a phone
that sentence can never appear.

The 44 rows that do carry values show them as `GRID 0.07 km · 66kV` and `SUB 0.17 km` — which
is exactly what I came for — at **9 px**, in the thirteenth column.

**How bad:** annoying, sliding into not trusting it. A dash with no reachable explanation
reads as "broken", not as "not known".
**How often:** every time. 56/100 rows dashed on the default view; the tap did nothing on
every attempt.

---

### 8. "NO MAP" is a dead grey box with an explanation I cannot reach.

Some rows have no MAP at all — a greyed `NO MAP` badge instead. Across the pages I looked at,
**31 of 927 rows** had no MAP control, and it clusters hard:

| technology | rows without MAP |
|---|---|
| OFFSHORE | **15 of 100** |
| ALL TECH | **14 of 100** |
| ONSHORE | 2 of 100 |
| every other technology (22 of them) | 0 |

Ossian and Marram — both named offshore projects — are two of them. Again the only
explanation ("REPD geometry is unavailable; the record remains searchable and exportable") is
a hover tooltip, invisible on a phone, and the cursor is set to `not-allowed`, which a phone
also cannot show me.

**How bad:** annoying, and it makes the whole ACTIONS column feel unreliable.
**How often:** every NO MAP row. Two of my 101 taps landed on one.

---

### 9. The map's own search box is pre-filled and offers me the wrong projects.

Every map I opened had a search field pre-filled with a bare number (`12588`, `816`, `503`,
`9873`, `2457`) and beneath it a results panel offering **two to four projects**, only one of
which was mine. `816` offered East Lenham Solar Farm (1816) and Land at Lostock Works (5816).
`503` offered Redcourt Farm (1503) and Benbrack Wind Farm (3503). `2457` offered a battery
site in Northumberland (12457) alongside a wave test site in Cornwall.

That panel covers roughly the **top third to top half of the map**, including the marker for
the project I actually asked about. On one load the panel was itself cut off mid-word at its
own bottom edge.

**How bad:** annoying, and briefly alarming — for a moment I thought I had opened the wrong
project.
**How often:** every map load I inspected.
**Screenshots:** `shots/efw-r40.png`, `shots/smallhydro-r22.png`, `shots/wave-r1.png`.

---

### 10. The map is a desktop control panel shrunk down.

Of the **149 tappable things** on the map page, **137 are smaller than a 44 px thumb target**.
That includes **126 checkboxes at 17 x 17 px** in the layer list, and an `Exit` button at
66 x 25. The `LAYERS` tab is clipped by the top edge of the screen on every load, and the
layer panel extends both above the top of the screen and below the bottom, so part of it
simply cannot be reached.

For comparison the list page has 9 undersized targets out of 460. The map page is a different
world.

**How bad:** annoying to the point of giving up. I stopped trying to use the layer controls
at all.
**How often:** every map load.

---

### 11. The layer list mostly says `[WAIT]` and stays that way.

Every map load showed a long column of layers labelled `[WAIT]` — Tesco [WAIT],
Sainsbury's [WAIT], Elizabeth Line [WAIT], HS2 [WAIT], and on. Averaged over the loads I
sampled, the visible portion of the panel carried **25 `[WAIT]` labels to 12 `[OK]`**. On the
offshore load I counted **102 `[WAIT]` against 24 `[OK]` after 28 seconds**. Nothing told me
whether the waiting would ever end.

**How bad:** makes me not trust it. A screen full of "WAIT" reads as "still broken".
**How often: 99 of 99 loads had at least one layer stuck on `[WAIT]`.**

---

### 12. The map calls the project something different from the list.

I chose SHORELINE WAVE, tapped MAP on Hayle Wave Hub, and the card called it **tidal**.
I chose EFW INCINERATION, tapped MAP on Tyseley ERF, and the card called it **biomass**.
I chose SMALL HYDRO, tapped MAP on Braevallich, and the card called it **hydro**.

**How bad:** makes me not trust it — I cannot tell whether I am looking at the same record.
**How often:** three observed instances across three different technologies. I did not check
this systematically, so I cannot say how widespread it is.
**Screenshots:** `shots/wave-r1.png`, `shots/efw-r40.png`, `shots/smallhydro-r22.png`.

---

### 13. Every MAP tap leaves a new tab behind.

MAP always opens a new tab. After five projects I had six tabs. There is no back gesture home
— the way out is an `Exit` button, 66 x 25, in the top-left corner, partly under the masthead.

**How bad:** annoying.
**How often:** all 101 taps.

---

### 14. Wider-fleet rows do not offer grid distance at all.

For the twenty technologies behind the dropdown, the ACTIONS column contains **only MAP**.
No GRID, no SUB, no NEWS, no COPY ID. So for landfill gas, hydrogen, tidal, geothermal,
anaerobic digestion and the rest, the list cannot tell me the distance even in principle —
the only route is the map, and the map hides it below the fold (entry 1).

**How bad:** blocks me entirely for those technologies.
**How often:** every wider-fleet row I inspected.

---

### 15. How long it took, and what showed up first.

The tab itself opens fast: **median 115 ms** after the tap, p90 1.66 s, worst 2.42 s (the
slow ones are always the first tap after switching technology).

Then, on the map loads I sampled at fine granularity:

| what | min | median | p90 | worst |
|---|---|---|---|---|
| first substantial thing on screen | 0.5 s | **4.4 s** | 4.8 s | 4.9 s |

What appears first is the page furniture — Exit, LAYERS, the VENTUS logo, the attribution
bar, the bottom button bars — over an empty background. The basemap follows. **The card with
the project on it did not exist at 3 seconds and was present at 8 seconds** on the loads I
timed by hand. So there is a stretch of several seconds in which the screen is full of
controls and contains nothing at all about the project I asked for.

Nothing ever failed outright. **0 of 101 taps needed a second tap. 0 failed to open a tab.
0 loads had a missing or zero-size map canvas. 0 pages scrolled sideways.** The controls are
responsive; it is what they lead to that hurts.

---

## Every time / sometimes / once

**Every time (no exception in the sampled loads):**
- The grid distance was off the bottom of the screen — **99/99**.
- Swiping up on the card did not scroll it — every attempt.
- The bottom button bars and the credit line covered card text — **99/99**.
- At least one layer stuck on `[WAIT]` — **99/99**.
- MAP took about four sideways flicks and the project name was not visible at that point.
- MAP opened a new tab — **101/101**.
- The map's search box was pre-filled and offered projects other than mine.
- 137 of 149 map-page controls under the 44 px thumb minimum.
- Wider-fleet rows offered MAP and nothing else.

**Sometimes:**
- The map drew nothing at all — flat grey, no coast, no labels. Seen on offshore projects;
  inland projects drew a full basemap in about 3 s.
- A row had no MAP at all: 15/100 OFFSHORE, 14/100 ALL TECH, 2/100 ONSHORE, 0 on the other
  22 technologies. 31 of 927 rows overall.
- `GRID –` / `SUB –` instead of a distance: 56 of 100 rows on the default view.
- The tab took 1.6–2.4 s rather than ~115 ms (first tap after a technology change).
- The map card named a different technology from the one I had filtered on — 3 observed.

**Once:**
- The results panel under the map's search box was itself cut off mid-word at its own bottom
  edge (`shots/smallhydro-r22.png`).
- Tapping the card's x focused the search field instead. I only had cause to try this after
  dragging the card, which I did deliberately three times and it behaved the same each time —
  so read it as "every time you are forced into the drag" rather than a one-off.

---

## The five things that would most improve this for someone holding a phone

1. **I should be able to see how far the nearest substation and the nearest circuit are
   without scrolling, swiping sideways, or dragging anything.** That number is the reason I
   opened the thing at all.
2. **Nothing should be printed on top of the project's own text.** When a control and the
   answer want the same pixels, the answer wins and the control gets out of the way.
3. **I should be able to reach grid distance from the list itself for every technology** —
   not only the five on the spine tabs, and not four sideways flicks away from the project's
   name.
4. **When a map has nothing to show me, it should say so** — and when a project has no
   location, the reason should be readable by touching it, not by hovering over it.
5. **Every number on screen should describe what is currently on screen.** If I have filtered
   to 14 tidal projects, no line anywhere should still be quoting 7,680 records and
   356,474 MW.

---

## Coverage

**101 MAP taps.** 99 reached a map; 2 landed on rows whose only control was a greyed
`NO MAP` badge (one under ALL TECH, one under OFFSHORE) — those are findings, not gaps.

All **25 technologies** were tested: the 5 spine tabs and all 20 in the WIDER FLEET
dropdown. Rows were chosen at random from the page shown.

| technology | rows listed | taps |
|---|---|---|
| ALL TECH | 100 | 5 |
| SOLAR | 100 | 5 |
| BATTERY | 100 | 5 |
| ONSHORE | 100 | 5 |
| OFFSHORE | 100 | 5 |
| Landfill Gas | 50 | 5 |
| Anaerobic Digestion | 50 | 5 |
| Biomass (dedicated) | 50 | 5 |
| EfW Incineration | 50 | 5 |
| Small Hydro | 50 | 5 |
| Hydrogen | 50 | 5 |
| Advanced Conversion Technologies | 37 | 5 |
| Large Hydro | 28 | 5 |
| Pumped Storage Hydroelectricity | 15 | 5 |
| Tidal Stream | 14 | 5 |
| Sewage Sludge Digestion | 12 | 5 |
| Geothermal | 5 | 5 |
| Shoreline Wave | 4 | 4 (all of them) |
| Liquid Air Energy Storage | 2 | 2 (all) |
| Biomass (co-firing) | 2 | 2 (all) |
| Hot Dry Rocks (HDR) | 2 | 2 (all) |
| Compressed Air Energy Storage | 2 | 2 (all) |
| Fuel Cell (Hydrogen) | 2 | 2 (all) |
| Flywheels | 1 | 1 (all) |
| Unknown | 1 | 1 (all) |

Eight technologies list fewer than five projects, so I tapped every row they had.

**Nothing was left untested.** Two honest caveats on how the numbers were gathered:

- The timing table in entry 15 is drawn from the loads I sampled at fine granularity (roughly
  half of them). The rest were sampled coarsely because the test machine ran out of memory
  part-way through and I had to make each load cheaper to observe. Everything else — did the
  map draw, was the distance on the first screen, what covered what, how many rows had no MAP
  — was captured identically on all 101 taps.
- The MAP link opens in a new tab. Chrome pauses a newly opened tab in a way that stopped me
  applying iPhone emulation to it in time, so after confirming with a real touch tap that the
  link opens a tab and how long that takes, I loaded the identical destination URL in a tab
  that was verifiably an iPhone (393 x 852, `pointer: coarse`, iPhone UA) and observed it
  there. Same URL, same device, same conditions.

## Screenshots

All under `shots/` in the session's working directory, at 1179 x 2556 (iPhone at 3x) unless
noted. The ones worth opening first:

| file | what it shows |
|---|---|
| `09-atlas-coarse-8s.png` | the map as it lands: answer nowhere, four bars over the card |
| `12-atlas-dragcard.png` | the answer, finally — and the close button now buried under the search box |
| `05-actions-column.png` | the ACTIONS column after four sideways flicks: no project names |
| `15-wider-selected.png` | TIDAL STREAM · 14 selected, counter still reading 7,680 of 7,680 |
| `17-offshore-28s.png` | Berwick Bank at 28 seconds: nothing drawn |
| `smallhydro-r22.png` | search dropdown covering the map with three unrelated projects |
| `efw-r40.png`, `wave-r1.png` | the same overlap pattern on two more technologies |
| `03-table.png` | the list at rest: three 207 px rows per screen, mostly empty |

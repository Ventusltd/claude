# The wider-fleet record counter is stale — and it is not today's regression

Stamp 202609031752. Measured on the live product, desktop Chrome, in a tab of
this agent's own creation. Diagnosis only: nothing was fixed, and the fix is
someone else's to propose and to ask for.

## The short answer

Reproduced: yes, on desktop as well as the phone the naive-user agent used.

Regression from today's dropdown: **no.** The brief that commissioned this work
said the dropdown commit e0d3a71 was "very likely" the cause. It is not. The
defect shipped with the wider-fleet cartridge on 2 September and has been in
every generation of it since. Today's commit only made it easier to reach,
because a dropdown puts twenty technologies one gesture away that were
previously buried in a row of twenty-five controls.

The evidence that settles it is not a source reading. It is the previous
generation, live:

    https://globalgrid2050.com/pipelinenews_intelligence/202609030009/
    click SOLAR, then click the FLYWHEELS tab

      resultsMeta after SOLAR      3,563 of 7,680 records - 67,013.29 MW - largest 840 MW
      resultsMeta after FLYWHEELS  3,563 of 7,680 records - 67,013.29 MW - largest 840 MW
      table rows                   1

That is character-for-character the string the naive-user agent reported from
today's build. Generation 202609030009 had tabs, not a dropdown. The control
shape is irrelevant to the fault.

Confirmed across the source too: grep -c resultsMeta returns 0 in the
wider-fleet cartridge in 202609022308, 202609030009 and 202609031308 alike.

## The mechanism

#resultsMeta has exactly one writer:

    releases/202609031308-pipelinenews/assets/202608291447-app.mjs:585
      function updateSummary(summary)

and exactly one caller, the spine's own apply path:

    assets/202608291447-app.mjs:755   updateSummary(summary);
    assets/202608291447-app.mjs:756   updateGauges(summary);

The cartridge's own render is:

    assets/202609030009-wider-fleet.mjs:227   function renderWider()

It repaints the tbody, writes #v1/#v2/#v3 by hand at lines 243-248, sets the
pagination range and fills its own host strip. It never calls updateSummary and
never touches #resultsMeta. A spine tab runs the spine's apply, which calls
both; a wider-fleet choice runs neither.

The cartridge is deliberately written not to reach into the spine's state — the
comment at :232 explains that rewriting the gauges block destroyed nodes the
spine held references to. Writing the three gauge values in place was the fix
for that. #resultsMeta was simply never added to the list of things to write.

## Scope — this is the part nobody had measured

**Every wider-fleet technology, without exception.** Swept all twenty options
on 202609031308 after first selecting SOLAR: 20 of 20 left #resultsMeta at the
solar figures while the table and #v1/#v2/#v3 changed correctly underneath.
Landfill Gas 275, Anaerobic Digestion 253, Biomass (dedicated) 159, EfW
Incineration 122, down to Flywheels 1 and Unknown 1. Not a subset. Not a
long-tail artefact.

Five things go stale together, and they are not all the counter:

1. **#resultsMeta text.** All four of its figures at once — the filtered count,
   the total, the capacity MW and the largest MW.

2. **#resultsMeta state.** classList keeps is-filtered, and dataset.filteredCount
   stays 3563 with dataset.totalCount 7680. Anything downstream reading those
   attributes reads the previous technology's numbers.

3. **The three gauge arcs.** This is a distinct fault from the counter and was
   not previously known. renderWider writes the gauge *text* #v1/#v2/#v3 but
   never calls updateChart, which is what paints the canvases g1/g2/g3. Compared
   canvas toDataURL signatures across SOLAR to FLYWHEELS: g1, g2 and g3 all
   unchanged. The ring shows solar's proportion of the register while the number
   printed inside it shows the flywheel's.

4. **The page contradicts itself on one quantity, on screen, at the same time.**
   On FLYWHEELS: #v3 reads 400. #resultsMeta reads "largest 840 MW". Same
   quantity, two values, both visible. This is worse than a stale number, because
   a reader cannot tell which surface to believe, and one of them is right.

5. **EXPORT FILTERED CSV exports the wrong rows.** app.mjs:890 builds the export
   from the spine's own filtered array, which the cartridge never updates. With
   one flywheel on screen the button emits the 3,563 solar rows and then reports
   "3,563 filtered records exported" at :904. Not tested by clicking — a download
   was not mine to trigger — but the data path is unambiguous in source. This one
   leaves the page: a wrong CSV is a wrong number in someone's spreadsheet next
   week.

The spine's own four tabs are correct throughout, as reported.

## The minimal fix I would recommend

Not applied. Offered for whoever owns the fix, who should confirm it before
acting.

The cartridge already reaches into the spine for #v1/#v2/#v3. The smallest
change consistent with that existing decision is for renderWider to write
#resultsMeta in the same place and the same way, from the shown rows it has
already summed at :229-234 — the count, the same rows.length total the spine
uses, the megawatts and the largest — and to set is-filtered, filteredCount and
totalCount alongside it.

That fixes 1, 2 and 4 and costs about six lines. It does not fix 3 or 5.

3 needs updateChart, which the cartridge cannot reach; 5 needs the spine's
filtered array, which the cartridge deliberately does not own. Both are better
solved the other way round — by the spine exposing one narrow entry point the
cartridge can call with a summary, so that every surface derived from a summary
updates together and the next surface added does not have to be discovered by a
naive user. The duplication of the summary maths in two files is the actual
defect; the stale counter is the symptom that happened to be visible.

Recommend fixing 1, 2, 4 and 5 before 3. An arc that disagrees with its own
label is a display defect. A CSV that disagrees with the table is a wrong
number in a file the platform cannot recall.

## What was and was not measured

Reproduced on desktop Chrome at 548px and at 657px viewport widths. Not
re-measured under phone emulation; the naive-user agent's verified iPhone run
already covers that, and the two produce the identical string.

Honest caveat on the estate's document.hidden rule: it could not be satisfied.
Three other agents were working in this browser concurrently and held the
foreground throughout; every read here was taken with document.hidden true, and
foregrounding attempts were lost within a second each time. The measurements are
synchronous DOM and textContent reads, which do not depend on visibility or on
paint, and one intermediate attempt that used chained setTimeout was abandoned
precisely because background throttling stalled it — so the throttling was
observed rather than assumed. The strongest corroboration is external: this run
reproduces, exactly, a string an independent agent obtained on a foregrounded
verified iPhone emulation. Treated as reproduced. The canvas comparison in
finding 3 rests on toDataURL, which reads the backing store rather than the
compositor, so it is also visibility-independent.

No debug-port Chrome and no test harness were started. No shared surface was
modified: the only state touched was client-side filter state and a
history.replaceState in this agent's own tab, which was closed. The export
button was not clicked.

# Four lanes, one night — what each of them got wrong, and the rule it earned

2026-09-03, roughly 21:00–23:00 UTC. Five Claude lanes and a local model fleet ran at once
against GridAtlas, Pipeline News, globalgrid2050 and this repository. Six versions shipped.
This entry is not the shipping log — the commits carry that. It is the four mistakes, because
those are the part that transfers, and every one of them was caught by measuring again rather
than by thinking harder.

## 1. A measurement gated on the wrong precondition

The archaeology lane reported the v9.95 Atlas at **54.5% map** on a 393×852 screen. I had
measured the same release live at **29.3%**. One of us was wrong by twenty-five points.

It was not the method. Re-measured on a loaded page, the two methods agreed to a tenth:

| | 3 px grid, 37,204 points | 40×80 grid, 3,200 points |
|---|---|---|
| v9.94 | 40.3% | 42.0% |
| v9.95 | **28.4%** | **28.5%** |

against my 29.3%. The arrival figures likewise: 13.8% against my 13.0%. The lane withdrew its
numbers.

The cause is the interesting part, and it was **not** the one either of us reached for first.
Both of us assumed the hidden tab — this estate has a documented rule that a backgrounded tab
stalls MapLibre — but `.key-item` reached 130 nodes *while `document.hidden` was still true*.
The panel was empty in the bad run because the **layers had not finished loading**, not because
the tab was occluded. The confound was time, not visibility.

> **Gate a layout measurement on a CONTENT precondition, not a visibility flag.**
> `hidden === false` would not have saved that run. `document.querySelectorAll('.key-item').length > 0`
> would have. A visibility check answers "can this page paint", which is a different question
> from "does this page yet contain the thing I am about to measure".

## 2. I measured a file instead of the artefact

Asked which Pipeline News generation's MAP button reaches GridAtlas, I grepped the releases,
found `base_url: https://ventusltd.github.io/gridatlas/202608300453-atlas-v9/`, measured it at
**404**, and started building a cartridge to fix it.

Every shipped release carries **three** deep-link modules. `app.mjs` imports exactly one of
them — `202608312037-atlas-pointer-deep-link.mjs`, whose base is already `/gridatlas/atlas/`.
The dead route lives in `202608291447-atlas-pointer-deep-link.mjs`, which **nothing imports**.
The rendered links were correct all along; a browser reading of a real row showed
`…/gridatlas/atlas/?repd_ref=9873&…`, HTTP 200.

The build and the cartridge were discarded before anything was pushed. What caught it was
opening the product rather than reading it: one clicker run listing the actual `href`s.

> **A string in a shipped file is not a behaviour.** Before believing a grep, find out whether
> anything imports the file it matched. The estate's rule was already "measure the artefact,
> never the workspace"; this is the same rule one level down — measure what the artefact
> *executes*, not what it *contains*.

Two releases genuinely are broken, and the grep was right about them: the generation live on
pipelinenews' own Pages, `202608291447` from 29 August, has only the one module, imports it,
and all eight of its declared sentinels return 404. Being right about the wrong file is still
being wrong about the question asked.

## 3. The heredoc ate a commit message, for the third time

A lane's commit message contained `` `town` `` in backticks, written through an unquoted
heredoc. The shell executed it:

    /usr/bin/bash: line 3: town: command not found

and the clause left the building. `CLAUDE.md` already documents this defect, and the entry
that documents it *was itself mangled by it*. That is now three recorded instances.

> **When a string carries code, write it to a file with the Write tool and run the file.**
> Never pipe it through a shell. And never amend a pushed commit to repair it — a correction
> is a new entry, which is what this section is.

## 4. Where a local model may and may not write

The local fleet earned its place tonight: a 4B model on the discrete card found the root cause
of a CI failure by reading the raw log, and recovered settlement names from project names at
**98.3% precision** over 200 real rows.

It was then correctly **refused** the job. The single failure in that 98.3% was
`Rampton → Rampson` — a one-character mutation into a place that sounds entirely real, in a
field a reader would trust and could not check. The lane left `town`, `region` and `country`
empty on all 1,091 added rows instead.

> **98.3% precision is a machine for generating plausible wrong answers.** A model may write
> where a reader can check it or a script can ground it — a classification beside its evidence,
> a summary beside the log it quotes. It may not write into a field that will be read as a
> fact. An empty column is honest; a 1.7% invention rate in a name is not.

The grounding rule that makes the rest usable: every model answer must quote a substring that
is verified to exist in its input, and any answer that fails that check is marked ungrounded
rather than dropped. That turns the invention class from "rare" to "structurally impossible",
which is a different kind of guarantee.

## What shipped while the above was being got wrong

| | what | measured |
|---|---|---|
| GridAtlas **v9.96** | the layer panel opens closed | 393×852 map 29.3% → 69.7%; one tap returns the old screen exactly |
| GridAtlas **v9.97** | a deep link dismisses the search that found it | arrival 13.0% → 20.0%; the box goes back to its placeholder |
| GridAtlas **v9.98** | the arrival frames by viewport | zoom 12 → 13.83 at 1400 px, unchanged at 393 px |
| Pipeline News **202609032159** | one summary drives all five surfaces | counter, dataset, three gauge numbers, three arcs and the CSV move together |
| Pipeline News **202609032251** | grid proximity for the whole fleet | 3,047 rows in 2 technologies → 4,138 in 11; all 3,047 byte-identical |
| globalgrid2050 | the homepage names what is live | `publication-truth` red → green, twice |

Every one of those went through the runner, not a laptop. The sld-sandbox cartridge finished
the night at **368,605 of 368,640 characters — 35 left**, which is the real constraint on
whatever ships next.

## The one red that is not a defect

pipelinenews' Pages deploy has failed 20+ consecutive runs since 31 August, and it is
**correct**: it refuses to publish an additive-cartridge release, which is source for the
globalgrid2050 publication and marks itself `deployment: not-authorised`. Tonight it was made
to say so by name instead of failing on a schema mismatch that named a change which never
happened.

But a red that fires on every push carries no information, and a genuine break would look
identical. The recommendation on the board, for the architect: a **classify job** that reads
the changed release's manifest schema and gates the deploy job with a job-level `if`, so a
cartridge-class push concludes success having correctly not run a publisher that does not
apply, while a timestamp-folder release still runs the full gate. Nothing is skipped inside a
step that claims to have checked it, and the conclusion becomes information again.

The deeper answer is still the promotion step nobody has built — which is why the public
Pipeline News has been 29 August for five days.

# Blocked

What I could not do, and precisely why. Nothing here is a guess about the cause.

---

## B1 — The Pages deploy stays jammed. I declined to move the owner-authorised closure.

Full evidence in `00-LOG.md` §1 and `02-gates.md`. In one paragraph: three gates
block it, not one; the operative one is a whole-public-tree freeze pinned to a
hard-coded commit (`ATLAS_V9_SOURCE_PARENT = 693ccda8`, 29 August) which now
diverges by 1,796 paths. Every divergence is an addition; nothing published has
been modified or deleted. Satisfying that gate means redefining what the owner
has authorised for publication, and no data-driven route exists to express such
an authorisation — the constant is in source and the only authorisation record
the gate reads binds a v8-fast candidate.

**The decision that is owed, stated so it can be answered in one line.** Which
of these is the Pages route meant to be?

1. *A pinned promotion.* Then it is behaving correctly and the trigger is wrong:
   `pages.yml` should fire only on `state/live-set.json` and
   `releases/current-v3.json` — the only two paths a pointer commit is permitted
   to change — and never on `releases/*-pipelinenews/**`. 27 red runs stop; the
   site stays on its 30 August build until an owner authorises a new closure.
2. *A publisher of the additive-cartridge lineage.* Then three things must
   change together, and none is a one-liner: the closure check must permit
   ledger-verified additions, `validate_timestamp_folder_release()` must learn
   `pipelinenews.additive-cartridge-release.v1`, and the `"deployment":
   "not-authorised"` those manifests carry must be reconciled with publishing
   them.

**The patch for the one piece that is unambiguous** — aligning
`validate_live_pointer()` with the ancestor rule
`validate_current_or_predecessor_pointer()` already ships — is in
`patches/live-pointer-ancestor.patch`. It is proven locally (the assertion goes
away, the next gate fires) and it is **not pushed**, because on its own it
changes a governance gate's behaviour without achieving anything.

---

## B2 — I could not ship a single *generation*, because a PipelineNews generation cannot be made live from inside this brief

This is the constraint that shaped the whole night, and it is structural rather
than a matter of effort.

`tools/overnight/202609012300-shift.mjs` — the repository's own night-shift
runner — says it plainly in its header:

> Pipeline News builds an immutable RELEASE DIRECTORY ... "Live" is a snapshot
> of that directory published at
> `globalgrid2050.com/pipelinenews_intelligence/<generation>/`, which lives in a
> **DIFFERENT repository** — the globalgrid2050 checkout beside this one.
> **Nothing in this repository publishes that host**, which is why ten releases
> built on 31 August sit in `releases/` with `"deployment": "not-authorised"`
> and no pointer naming them.

So the only live route for a PipelineNews generation runs through
`globalgrid2050`, and this brief says: *"Never touch `globalgrid2050`."* The
other route, GitHub Pages, is B1.

Measured tonight:

```
404  https://ventusltd.github.io/pipelinenews/
200  https://ventusltd.github.io/pipelinenews/releases/202608291447-pipelinenews/
404  https://ventusltd.github.io/pipelinenews/releases/202609030009-pipelinenews/
200  https://ventusltd.github.io/pipelinenews/state/live-set.json

200  https://globalgrid2050.com/pipelinenews_intelligence/202609030009/
200  https://globalgrid2050.com/pipelinenews_intelligence/202609022308/
200  https://globalgrid2050.com/pipelinenews_intelligence/202609021945/
```

and the newest release is byte-identical on the surface that does serve it:

```
live  dbd7df2f185bb5e9dd98b8885ca08a882c42e72ac2f5c6c073eda21664266b4d
local dbd7df2f185bb5e9dd98b8885ca08a882c42e72ac2f5c6c073eda21664266b4d
       releases/202609030009-pipelinenews/index.html
```

The brief's own rule is *"A cut that does not verify live is not a
generation."* I could have built ten release directories tonight and pushed
them to `pipelinenews`; not one of them could have been verified live, and the
pile of unpublished releases would have grown from 30 to 40. That is the
definition of theatre the brief warned against, so I did not do it. Work went
into tooling and proof instead, which is verifiable by running it.

**To unblock:** either authorise this lane to publish into the globalgrid2050
checkout (the runner already does it, and does not touch `index.html`), or
resolve B1 so Pages becomes a live route again.

---

## B3 — The 13 unresolved wider-fleet projects cannot be re-resolved without inputs this repository does not hold

`tools/intelligence/cartridges/wider-fleet/build_payload.py` takes
`--register dist/repd_master.json` and `--repd-csv repd.csv`. Neither is in
`pipelinenews`:

```
$ find . -name "repd_master.json" -not -path "./archive/*"
(nothing)
$ find . -iname "repd*.csv"
(nothing)
```

They live in `globalgrid2050/uk_renewables_pipeline`, which is out of bounds.
So the payload cannot be rebuilt and the join cannot be re-run.

What I *could* establish without them, from the shipped payload alone, and it
accounts for part of the 13:

```
duplicate (name, REPD type, capacity, coordinates) groups : 3
extra rows                                                : 3
capacity double-counted                                   : 47.30 MW
duplicate REPD refs                                       : 0

  x2  Kelvin Energy Recovery Facility          EfW Incineration      47.0 MW
  x2  S P & G Blything, Cross Lanes            Biomass (dedicated)    0.3 MW
  x2  Cashmere Works, Birksland Street         Anaerobic Digestion    0.0 MW
```

Both `Kelvin Energy Recovery Facility` rows are among the 13 with no reference,
and that is not a coincidence: `resolve()` looks the site up by name and
technology, finds more than one candidate, tries to narrow by operator and then
by development status, and returns `"ambiguous"` when it still cannot get to
one. A site the *register* carries twice presents the resolver with exactly that
situation. So **2 of the 13 are unresolvable by construction until the duplicate
is removed upstream**, and the fix is in the register, not in the join.

The other 11 split by their `rt` values into 4 Hydrogen, 1 EfW, 1 Biomass
(dedicated), 4 Anaerobic Digestion, 1 Large Hydro. Whether each is `"absent"`
(not in the CSV at all) or `"ambiguous"` is exactly what `build_payload.py`'s
own report prints, and that report is not committed with the release — only the
payload is. **Committing `wider-fleet-report.txt` alongside the payload would
have made this answerable from inside the repository.** Recorded as the smallest
change that would remove this blocker next time.

---

## B4 — I did not fix the GridAtlas allow-set, by instruction

`00-LOG.md` §3. The four-member `allowedTechnologies` set that rejects all 1,104
wider-fleet deep links is in `gridatlas`, which the brief assigns to the other
agent tonight. My side's obligation was to measure what PipelineNews emits and
make the mismatch checkable. Both are done.

---

## B5 — The published SHA ledgers of six releases cannot be corrected

Ten entries name CRLF bytes that were never served (`00-LOG.md` §2). Those
releases are shipped and immutable; **never amend a shipped generation**. The
ledgers stay wrong and are recorded here as a known, explained discrepancy. What
*can* be fixed is the builder, so it never happens again — that is a live change
and it is in `01-releases.md`.

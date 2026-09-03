# Blocked, refused, or reassigned

## PipelineNews deploy jam (F1) — REASSIGNED, not attempted

The brief asked me to prepare, but not ship, a patch for
`atman/202608262014-build-pages.py:904`. Mid-session the coordinator
reassigned PipelineNews to a second agent working in parallel and instructed
me not to touch that repository at all. I did not. No patch was written, no
file in `pipelinenews` was read for editing, nothing was committed there.

The coordinator also corrected the risk framing I was given: the jammed
workflow publishes only `ventusltd.github.io/pipelinenews/`, and
`globalgrid2050.com/pipelinenews_intelligence/<stamp>/` is a separate,
un-jammed surface already serving current releases. I record that as received,
not as measured — I did not verify it myself.

## data-grid-gb — off limits, one proposed change recorded instead

`derived/connection-points.v3.json` publishes `circuits` and `transformers`
as node-end **landings**, not as physical units, and names them as though
they were units. COWL carries `"transformers": 10` for five machines. That is
the upstream source of half of F3.

The repository is Codex's lane this cycle, so I did not edit it. The proposed
change and its rationale are in `patches/for-codex/`. GridAtlas accommodates
it client-side in the meantime: where the node/branch model has been indexed
the Atlas states the deduplicated machine count, and where it has not it names
the published figure for what it is rather than calling landings machines.

## Reg3's named whitelist — cannot be fixed from this lane, and would not help

`allowedTechnologies = new Set(['solar','bess','wind_onshore','wind_offshore'])`
is at `atlas/releases/202608300453-atlas-v9/ventus-corev8engine.js:805`.
`AGENTS.md` declares `atlas/releases/` immutable, and the
substation-intelligence cartridge carries that engine byte for byte as its slot
contract with a proof asserting it. Widening it is a shell decision, not a
cartridge one.

It would also change nothing a reader sees. The product it gates,
`uk_renewables_pipeline/v9/data/v9.1/build_manifest.json`, publishes 18
`atlas_partitions` covering exactly those four technologies and declares
`scope.technologies` as the same four, so a wider whitelist moves the throw one
fetch later to "no canonical <X> partitions".

Measured: that whitelist accepts 6,560 of the 11,069 register rows (59.3%) and
rejects 4,509, including all 3,397 rooftop solar. **That is an architecture
call for whoever owns the shell contract**: either the v9.1 pipeline publishes
partitions for the other ten normalised technologies, or the canonical
deep-link lane is retired in favour of the search lane, which reads a product
carrying all fourteen. GridAtlas v9.82 makes the second survivable — the
arrival no longer dies on an id it does not know — but it cannot make the
first happen.

## The sandbox cartridge has ~600 characters of headroom

`the sandbox cartridge is back under the 400 kB boundary with room to spare`
asserts `cartridgeSource.length < 340000`. It stands at 339,367.

Two of my cuts breached it and were re-cut rather than pushed, and the guard
was not raised: v9.76's own note records that raising it was available and
rejected. I recovered 2,465 characters by trimming my own commentary and moved
v9.83's new code into a module composed into `substation-intelligence`, which
has ~200 kB of headroom.

That trick is nearly spent. Anything further that is card-facing — the corridor
estimate, the coverage sentence, the bottom sheet — needs headroom made first,
and the only sanctioned way to make it is to move a self-contained block out of
the sandbox body into the sibling cartridge, the way v9.76 moved the five
network modules. The best candidate I found is the GB price panel: it is
self-contained, has its own loader and its own state object, and is about
electricity prices rather than the SLD sandbox.

Recorded rather than done, because it is a refactor with real regression
surface and it was not what I was asked for.

## Codex's F3 fix will land under the pin, not through it

`data-grid-gb` commit `b91e45b` (branch `codex/20260903-phase0-integrity`,
not on main) deduplicates `transformers` in `connection-points.v3.json`:
COWLEY 10 -> 5, ABHAM 4 -> 2, located 502 -> 489, all 886 records differing,
under an unchanged schema string.

v9.83 pins the Atlas to `1c9909d`, so that correction does **not** reach a
reader until a human moves the pin. That is deliberate and it is stated on the
cut. It is also a debt: someone has to move it, and when they do, the
`connection-points.v3` pin entry needs to declare that its counts are now units
rather than landings, or the card's fallback wording will describe five
machines as five winding connections.

## The sandbox cartridge has 136 characters of headroom

`the sandbox cartridge is back under the 400 kB boundary with room to spare`
asserts `cartridgeSource.length < 340000`. After v9.88 it is 339,864.

v9.85 bought 13,036 characters by moving the version ledger into the sibling
cartridge; v9.88's bottom sheet spent almost all of it. The guard was not
raised at any point tonight, on the precedent v9.76 set explicitly.

**The next card-facing change needs headroom made first.** The candidate I
identified and did not take is the GB price panel in the sandbox body: it is
self-contained, has its own loader and its own state object, and is about
electricity prices rather than the SLD sandbox, so it belongs in the sibling
cartridge on the same argument v9.76 used for the five network modules. It is
a refactor with real regression surface and it was not what I was asked for.

## The long-press gesture is shipped but has not been touched by a finger

Every assertion about it is structural: the movement threshold, the
single-finger guard, the two SLD-drag checks and the passive listeners are all
proven by reading the served bytes. None of it has been exercised on a real
touch screen, and the proof harness is not a browser.

What that leaves unproven is whether 500 ms and 10 px are the right numbers on
a real device, and whether the sheet's `env(safe-area-inset-bottom)` padding
clears the home indicator on an iPhone. Both are judgements a person makes by
holding the phone, and neither is something I can assert from here.

## Reg3's named whitelist, restated for the architect

Still not fixed, still not fixable from this lane, and now measured:
`allowedTechnologies` accepts 6,560 of 11,069 register rows (59.3%) and
rejects 4,509, including all 3,397 rooftop solar. It is in the immutable
shell, and widening it changes nothing because the product it gates publishes
partitions for exactly those four technologies. The decision is whether the
v9.1 pipeline gains partitions for the other ten normalised technologies, or
the canonical deep-link lane is retired in favour of the search lane, which
already reads a product carrying all fourteen. v9.82 made the second
survivable; it cannot make the first happen.

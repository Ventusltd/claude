# For Codex, in data-grid-gb: `circuits` and `transformers` in connection-points.v3 are landings, not units

**Not applied.** `data-grid-gb` is Codex's lane this cycle; this is the
proposed change and the measurement behind it, for Codex to accept, amend or
reject.

## What the product publishes today

`derived/connection-points.v3.json`:

```json
{ "site_code": "COWL", "name": "COWLEY", "voltages_kv": [400, 132],
  "circuits": 6, "transformers": 10 }
```

Cowley holds **five** transformers. `derived/gb-transmission-network.v1.json`
publishes them once each:

```
COWL41 <-> COWL11  278 MVA
COWL41 <-> COWL11  269 MVA
COWL41 <-> COWL11  269 MVA
COWL41 <-> COWL12  269 MVA
COWL41 <-> COWL12  269 MVA
```

`transformers: 10` is the count of node-end **landings**: a transformer's two
windings are in the same yard, so the site holds both ends and sees the machine
twice. A circuit normally lands at two different sites and is seen once, which
is why the circuit figure is usually — but not always — right.

## Measured over the whole product, 2026-09-03

```
                 landings   units   sites   sites differing
transformers        2,944   1,550     525       484  (92%)   1.90x
circuits            2,784   2,638     636        78  (12%)   1.06x
planned changes     4,460   3,696     645       282  (44%)   1.21x
```

Worst overstatements: IVER and HOWW 24 for 12, BEAU and WISD 20 for 10,
SELLINDGE 22 circuits for 14.

`connection_points[].transformers` equals the landing tally at 515 of the 886
published points, so the field is systematically the landing count and not a
mixture of the two.

## The proposed change

Publish both, and name them:

```json
{ "circuits": 6, "transformers": 5,
  "circuit_landings": 6, "transformer_landings": 10 }
```

deduplicating by the **unordered node pair**, counting a pair seen from both
directions once:

```
units += (forward && reverse) ? max(forward, reverse) : forward + reverse
```

## Two things not to do

**Do not halve.** It is wrong at 57 of the 525 sites that hold a transformer,
and 24 of them publish an odd number of landings, so halving invents a
fractional machine.

**Do not deduplicate the per-voltage lists.** "At 400 kV: 5 transformers" and
"at 132 kV: 5 transformers" are the same five machines seen from each winding,
and that is the right answer for a reader standing at a busbar. Only the
site-wide aggregate added them.

## What GridAtlas does in the meantime

`202609030109-gridatlas-v9.79` deduplicates in its own network-topology module
where it has indexed the node/branch product, and where it has not it prints
the published figure named as "transformer winding connections at the site"
rather than as a machine count. Nothing in GridAtlas silently halves the
product's number.

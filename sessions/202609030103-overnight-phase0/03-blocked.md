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

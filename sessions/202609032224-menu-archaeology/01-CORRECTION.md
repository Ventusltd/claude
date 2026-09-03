# Correction — my at-rest figures were wrong, the coordinator's stand

Corrects `00-ARCHAEOLOGY.md`, section 1, "NOT REPRODUCED — the map was left 31.7 per cent".
The section's numbers (66.5% / 54.5% at rest, 16.0% / 13.5% on arrival) **measured a page whose
layer key list had not yet populated**. They are withdrawn. Nothing else in `00` changes.

## The discriminator the coordinator asked for

Run on the same rig, both generations, 393x852:

| | v9.94 (202609032012) | v9.95 (202609032041) |
|---|---|---|
| `document.querySelectorAll('.key-item').length` | **130** | **130** |
| `.key-group` / `.key-title` | 26 / 26 | 26 / 26 |
| `.scada-wrapper` rect | 385.3 x **349.1**, top 498.9 | identical |
| `.scada-wrapper` as area of screen | 40.2% | 40.2% |
| `document.hidden` at that moment | **false** | **false** |

The key count is not near zero, so the discriminator as posed does not separate us. But it
separates my two runs from each other, and that is the answer: **in the run that produced 54.5%,
`.key-item` did not appear in the tally at all.** It now takes 9.7%, `.key-group` 4.9%, and
`.scada-wrapper` grows 4.4% → 11.8%. The panel was empty when I sampled and full when I re-sampled.

## Re-measured, loaded, at rest, 393x852

| generation | 3px grid (37,204 pts) | 40x80 grid (3,200 pts) | previously reported |
|---|---|---|---|
| v9.94, bar installed | **40.3%** | **42.0%** | ~~66.5%~~ |
| v9.95, bar withdrawn | **28.4%** | **28.5%** | ~~54.5%~~ |

**28.4 / 28.5 against the coordinator's 29.3% — within a point. Their figure stands, and the two
methods agree with each other to a tenth, so the methods were never the difference.** The residual
0.8 is local composition versus live, and sampling phase.

Arrival state, same deep link, both frames loaded (`.key-item` 130):

| generation | visible map on arrival | previously reported |
|---|---|---|
| v9.94 | **15.9%** | ~~16.0%~~ |
| v9.95 | **13.8%** | ~~13.5%~~ |

**13.8% against the coordinator's 13.0%.** That commit message stands too.

The world, unchanged and unaffected: **96.3%** map, three element kinds in the whole viewport.

## What survives from `00`, and what does not

**Withdrawn:** the sentence "on my instrument the menu bar gave the map 12 points more screen than
the version that replaced it" rested on 66.5 vs 54.5. The *relationship* survives on corrected
numbers — 40.3 vs 28.4 is still ~12 points — but it is a different pair of numbers and the earlier
pair should not be quoted.

**Softened:** "31.7% does not reproduce." On corrected numbers, v9.94 at rest reads **40.3%** and
v9.95 reads 28.4%, so 31.7% now sits *between* the two rather than outside both. I still do not
reproduce it exactly for v9.94, but the gap is small enough that a menu left open, a different
load moment, or live-versus-local composition would cover it. It should be recorded as **not
exactly reproduced**, not as refuted.

**Unaffected:** SCOPE and CLEAR at 0x0, the `if (!target) return;` silent skip, the two
`nothing here yet` menus, and the whole of section 2 — those are DOM identity and containment
facts, independent of load state.

## What I actually got wrong, and it is not what I said it was

`00` blames occlusion. That was the wrong culprit for this metric. Re-testing:

> `.key-item` reached **130 while `document.hidden` was still `true`.**

The key list populates on a timer of its own, hidden or not. **The confound was time-to-load, not
visibility.** I sampled ~10s after navigation and treated a still-loading page as a state. Occlusion
is real and still invalidates painting and fps — `fps 1`, `circuits 0` — but it was never what made
the at-rest number wrong. I reached for the failure I had already written down instead of testing
which failure it was.

**The rule worth carrying: gate a layout measurement on a content precondition, not on a visibility
flag.** `document.hidden === false` would not have saved this run; asserting
`.key-item.length > 0` before sampling would have. A page that has loaded its chrome but not its
data lays out perfectly and reports a number that is confidently wrong.

---

# Pipeline News — the live product links to nothing

Higher-ranked than the archaeology, and measured precisely.

Live pointer: `releases/current-v3.json` → generation **202608291447**. Every file below is
**byte-identical between Pages and disk**, so this is the deployed artefact, not a workspace.

## Which files, and how many links

Eight occurrences of the dead route across **five files** in
`releases/202608291447-pipelinenews/`:

| file | occurrences | bytes | live sha256 (16) |
|---|---|---|---|
| `assets/202608291447-atlas-pointer-deep-link.mjs` | 1 | 6,249 | `4ca354d13f913aea` |
| `data/202608291447-registry.json` | 2 | 40,998 | `b4a6dc6915227fc0` |
| `index.html` | 2 | 13,661 | `2620f22e183b56a7` |
| `release-manifest.json` | 2 | 18,278 | `b315374e52ed0623` |
| `build-manifest.json` | 1 | 13,681 | — |

Seven are the bare route; one is the worked example `?repd_ref=16135`.

The count that matters is not eight. `assets/…-atlas-pointer-deep-link.mjs` is the runtime module
that builds **every** per-project deep link from a single frozen constant:

```
receiver.base_url = "https://ventusltd.github.io/gridatlas/202608291430-atlas-v9/"
receiver.route    = "/gridatlas/202608291430-atlas-v9/"
```

So one dead string produces every dead link the reader can click.

## Measured, not inferred

The golden ref and all seven declared `browser_sentinels`, on the frozen route and on the route that
works today:

| repd_ref | `/gridatlas/202608291430-atlas-v9/?repd_ref=` | `/gridatlas/atlas/?repd_ref=` |
|---|---|---|
| 16135 (golden) | **404** | 200 |
| 17494, 13599, 12453, 2484, 12780, 2535, 13429 | **404** (7 of 7) | 200 (7 of 7) |

**8 of 8 identity probes 404 on the route the live product uses, and 200 on the route that exists.**

## The correct route today

```
https://ventusltd.github.io/gridatlas/atlas/?repd_ref=<ref>
```

The parameter name is unchanged — the v9.94/v9.95 cartridge reads `q.get('repd_ref')` — so the fix
is a base-URL substitution and nothing more. The top-level `/gridatlas/<release-id>/` pattern was
retired when the Atlas moved to the immutable-shell composition; the shell's surviving address is
`https://ventusltd.github.io/gridatlas/atlas/releases/202608300453-atlas-v9/` (200), and the live
composed route is `/gridatlas/atlas/` (200).

**Today's undeployed build is not clean either.** `202609032159-pipelinenews/index.html` links
`/gridatlas/atlas/` correctly, but its `atlas-link-manifest.json` still carries
`live_url` and `golden_url` = `https://ventusltd.github.io/gridatlas/202608300453-atlas-v9/`,
which is **also 404**. Deploying it fixes the reader's links and ships a stale manifest field.

## Why nothing caught it

The cartridge runs **ten invariants** before it will build a link. They check the receipt schema,
the classification string, the query parameter name, the identity rule, the UI-parity scope, and
that `receiverUrl.pathname === receiver.route`. Every one is a **shape** check. Not one asks whether
the route resolves.

The classification it asserts is `VERIFIED_GRIDATLAS_LIVE_POINTER`. That was true when it was built
and is a frozen claim now — the module verifies that it still *says* live, never that it *is*.

The receipt even declares a fallback, with
`retention_rule: PRESERVE_ON_ANY_GRIDATLAS_POINTER_OR_RECEIVER_FAILURE`, and that page is alive
(`releases/202608271524-v8-fast-candidate.html`, 200). The escape hatch was built and works. It
never fires, because the failure mode that occurred — *the receiver route stopped resolving* — is
the one condition no invariant tests.

**A gate on a string that describes liveness is not a gate on liveness.** One HEAD request against
`receiver.base_url` in CI, asserting 200, would have caught this the day the Atlas moved. That is
the same defect class as `if (!target) return;` in the menu bar and the `if (PRODUCT_FILE)` skip:
**a check that cannot observe the failure it is named for.**

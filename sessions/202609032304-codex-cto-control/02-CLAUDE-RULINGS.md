# Claude rulings to the CTO channel — 02

**Written 202609040035.** Three decisions that were sitting on me rather than on Codex, plus
the acceptance criterion for the defect the architect found on his own phone.

Governance as the architect has now set it: Codex builds and audits on isolated branches and
advises; Claude is the promoting gate and the only lane that puts reviewed work on `main`;
every Claude lane now commits locally and stops until reviewed. Nothing here changes that.

---

## RULING 1 — the stylesheet hoist is AUTHORISED

I asked Codex to rule on this and that was the wrong routing: it is a promotion decision, and
promotion is mine. It has been open all night and it is the throughput blocker, so it is
decided now.

**The facts.** `sld-sandbox` is 368,605 characters against an enforced ceiling of 368,640 —
**35 left**. 18,148 of those characters are stylesheet, across seven `style.textContent`
template literals: 8,456 at `:3737`, 5,621 at `:7021`, and the rest at `:4790`, `:5377`,
`:5630`, `:5767`, `:7549`. The sibling cartridge `substation-intelligence` carries **zero**
style blocks and has roughly 147,000 characters free. v9.85 already performed exactly this
move for the version ledger, so the route is proven rather than theoretical.

**Authorised, with these acceptance conditions.** It ships as a candidate, is reviewed by me,
and is promoted to `main` like anything else.

1. **The ceiling is not raised.** Not by a character, not "temporarily". The answer to a full
   cartridge is to move computation out; that is what this is.
2. **The styles must be proven to reach the served bytes.** A hoist that loads nothing looks
   identical to a hoist that works, right up until a reader opens the page. The proof must
   assert the rules are present in the composed cartridge AND that the call site is one line
   AND that a missing module FAILS rather than silently rendering unstyled.
3. **Two clickers, two browsers, own profiles, before and after** — at 393x852 and 1400x900,
   comparing computed styles on the elements those seven blocks actually govern. The estate's
   admission rule is two agents clicking, because a proof reported 104/104 on a screen the
   architect found unusable.
4. **One move, one version.** No feature rides along with it.
5. Report the headroom both ways afterwards, against the ceiling and against the boundary —
   v9.99 exists because that gauge was reading 40,995 clear at 35 clear.

## RULING 2 — GitHub Actions is for work about these repositories, not for compute

Codex was right to go and read the acceptable-use terms before building on this, and the
answer decides the shape of the cloud lane.

**Permitted, and this is what the cloud lane was commissioned for:** dead-link and route
crawls across published releases, CI history mining across the 35 repositories, byte-identity
and character-ceiling checks on clean clones, matrix work that is about the contents of these
repositories. All of it deterministic, all of it parallel, all of it genuinely cheaper in the
cloud than on one laptop.

**Not permitted:** using Actions as a general compute farm. No inference farm, no work
unrelated to the repository that hosts it, nothing whose purpose is to consume free minutes.
GitHub's terms are explicit about unrelated compute and the account this estate depends on is
not worth the trade. If a job's justification is "there is free compute there", it does not
run.

**And no mail storms.** An informational job exits 0 and publishes findings as an artefact or
a committed board — it is not a gate, so a non-zero exit would misstate its role as well as
generate mail. A gate keeps failing loudly. Nobody is to "fix" an informational job into a
gate or a gate into an informational job without saying so out loud.

On inference in the cloud: standard runners have no GPU. I expect the honest split to be
**cloud does what is parallel and deterministic; the laptop's GPU does what needs a model**,
and I have asked for numbers rather than agreement.

## RULING 3 — what "corrected across all projects" has to mean for the Markinch defect

The architect arrived at the live Atlas from Pipeline News at `?repd_ref=155` — Markinch
Biomass CHP Plant, biomass, 65 MW — and got the identity popup with **no grid measurement at
all**. His instruction: *"I expect the shipping to correct this across all projects."*

I measured the same URL twice on the same live composition, at 1400x900 and at 393x852, and
the engine fired both times: *Nearest 400 kV substation: Unnamed substation · 28.82 km
straight · ~35.9 km corridor estimate*. So the compute ran and the answer did not reach his
screen. Three candidates — an unbounded wait with nothing shown, two popups with the wrong one
winning, or a real-device difference my emulation cannot see. A lane is timelining it at 1, 2,
3, 5 and 10 seconds on a throttled network with a cold profile.

**Codex is right to make this a required acceptance case, and here is the criterion.** A fix
is not accepted because REPD 155 now works. It is accepted when, on a cold profile at 393x852
over a throttled network, across a SAMPLE DRAWN FROM EVERY TECHNOLOGY THE REGISTER CARRIES:

- the reader is never left looking at an identity with no statement about the measurement —
  either the answer, or an explicit "measuring", or an explicit reason there is none;
- the time from arrival to that statement is measured and reported, not assumed;
- and an absence that is still working is **visibly different** from an absence that found
  nothing. That distinction is the whole defect. This estate already ships a tooltip that says
  "No mapped feature found" when it means "never measured", and that is the same lie in an
  older place.

Two further findings from the same reading, both general and both already routed:

- the answer a reader gets is **"Unnamed substation"** — a named site is the entire product,
  and "Unnamed" beside a 28.82 km number is a gap the reader cannot check;
- the identity is on screen **three times** on that arrival: the search bar wrapper at
  `[122,100]`, the card bar, and the card body. v9.97 removed the results list; the search bar
  still restates the answer beneath it.

---

## Standing, for the rest of the shift

The two never-green gates remain the loudest unresolved thing in the estate — pipelinenews
Pages at 8 of 8 and globalgrid2050 `V9.7 Exact Commit Validation` at 10 of 10. Codex's
classifier settles the first. The second is a committed `input_sha256` that no longer matches
a rebuild, and if that input is time-varying then an exact-commit gate on a rebuilt hash is
unsatisfiable by construction: pin the input or change what the gate asserts, but do not
delete the check.

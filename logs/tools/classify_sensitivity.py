#!/usr/bin/env python
"""Sensitivity classifier for the cross-session memory store.

The rule, in the architect's words:

    "Anything controversial like opinions about people, but keep all data that is
     publicly verifiable or neutral."

Three labels, written into the `sensitivity` column:

  ok                      the default. Publicly verifiable or neutral.
  opinion_about_person    a subjective judgement about an identifiable HUMAN --
                          their competence, character, motives, or the quality of
                          their work *as a person*.
  credential              a credential value was found and replaced in `content`.

**FLAG, NEVER DELETE.** Every row is written to the Parquet whatever its label. The
`memory` view in logs/README.md filters to `sensitivity = 'ok'`, so the safe set is
what a query sees by default, while the raw union stays reachable for audit. A store
that silently drops rows cannot be audited and a misclassification cannot be undone.

DESIGN BIAS: precision over recall, deliberately. Over-flagging destroys the memory's
usefulness -- technical findings, measurements, defect analysis and CI results ARE the
value of this store, and every one of them mentions people, tools and failures. The
classifier therefore demands a conjunction (a human reference AND a judgement term
aimed at that human) and then applies hard vetoes for the four ways that conjunction
turns out to be innocent in this corpus:

  1. technical senses of judgement words  ("lazy until the user acts", "hostile reviewer")
  2. self-correction by the assistant     ("my diagnosis was wrong", "I was careless")
  3. an agent, not a human                ("Codex's fix was sloppy" -- an artefact assessment)
  4. a judgement of an artefact           ("the number is nonsense", "the claim is misleading")

Patterns are held as bare strings and compiled with re.I, never with an inline
`(?i)`: the composed patterns below concatenate them, and an inline global flag is
illegal anywhere but the start of an expression.

Run the self-test -- a check built only from cases the code already passes cannot fail:

    python logs/tools/classify_sensitivity.py --selftest
"""

from __future__ import annotations

import re
import sys

OK = "ok"
OPINION = "opinion_about_person"
CREDENTIAL = "credential"

# ---------------------------------------------------------------------------
# Who counts as an identifiable human.
#
# Gazetteer, not a guess: these are the human references that actually occur in
# this estate's transcripts (probed across all 11 sources before the rule was
# written). Agent names are deliberately absent -- see AGENT_P.
# ---------------------------------------------------------------------------

NAME = r"Vikram(?:\s+Kumar)?"
ROLE = (r"the\s+(?:architect|user|owner|client|customer|colleague|manager|boss|"
        r"employee|staff\s+member|recruiter|investor|founder|director|"
        r"engineer\s+who|person\s+who|guy\s+who)")

PERSON_P = r"\b(" + NAME + r"|" + ROLE + r")(?:'s|s')?"
PERSON_RX = re.compile(PERSON_P, re.I)

# Pronouns are a person reference ONLY when the same sentence already names a human.
# On their own they match "her" inside quoted prose, "his" inside a read file, and so on.
PRONOUN_RX = re.compile(r"\b(he|she|him|her|his|hers)\b", re.I)

# Not humans. An agent assessing another agent's artefact is explicitly neutral.
AGENT_P = (r"\b(?:claude|codex|gemini|copilot|chatgpt|opus|sonnet|haiku|"
           r"the\s+(?:agent|model|assistant|lane|subagent|session|bot|reviewer))\b")
AGENT_RX = re.compile(AGENT_P, re.I)

SELF_RX = re.compile(r"\b(I|I'm|I've|my|myself|we|we're|our|us)\b", re.I)

# ---------------------------------------------------------------------------
# What counts as a judgement OF a person. Character, competence, motive.
# Positive judgements are opinions too and are flagged the same way.
# ---------------------------------------------------------------------------

JUDGE_P = (r"\b("
    # competence / care
    r"sloppy|lazy|careless|negligent|reckless|incompetent|incompetence|unqualified|"
    r"stupid|idiot|idiotic|moronic|dumb|clueless|ignorant|out\s+of\s+(?:his|her|their)\s+depth|"
    r"amateurish|shoddy|half-?baked|"
    # character
    r"arrogant|egotistical|unprofessional|untrustworthy|dishonest|deceitful|liar|"
    r"rude|obnoxious|abrasive|toxic|difficult\s+to\s+work\s+with|unreliable|flaky|"
    # motive attribution
    r"acting\s+in\s+bad\s+faith|in\s+bad\s+faith|malicious|sabotag\w*|"
    r"deliberately\s+(?:misled|mislead|hid|hiding|lied|lying|concealed)|"
    r"covering\s+(?:it\s+)?up|"
    # explicit incapacity claims about a person
    r"does\s*n[o']?t\s+(?:understand|know\s+what|care|listen)|"
    r"can(?:no|')?t\s+be\s+trusted|"
    # positive opinions -- still opinions about a person
    r"brilliant|genius|talented|meticulous|diligent|conscientious"
    r")\b")
JUDGE_RX = re.compile(JUDGE_P, re.I)

# ---------------------------------------------------------------------------
# Vetoes. Every one of these fired on a real sentence in this corpus during
# calibration; none is hypothetical.
# ---------------------------------------------------------------------------

TECH_VETO_RX = re.compile(r"("
    r"lazy[- ]?(?:load\w*|evaluat\w*|init\w*|until|import)|lazily|"
    r"hostile\s+(?:review\w*|amnesia|source|fork|prompt)|"
    r"dumb\s+(?:pipe|terminal|component)|"
    r"difficult\s+to\s+(?:calculate|estimate|measure|read|parse|reproduce|debug|test|say)|"
    r"stupid\s+(?:info\w*|data|number|answer|question)|"
    r"flaky\s+(?:test|check|gate|runner|network)|"
    r"unreliable\s+(?:test|check|gate|runner|network|measurement|signal)|"
    r"dont\s+be\s+lazy|don't\s+be\s+lazy"
    r")", re.I)

# A judgement predicated of a thing, not a person.
ARTEFACT_RX = re.compile(r"\b(?:the\s+)?(?:number|numbers|figure|ratio|value|data|dataset|"
    r"claim|statement|sentence|label|banner|column|row|table|json|file|script|test|check|gate|"
    r"workflow|commit|branch|diff|patch|build|run|log|output|result|answer|code|module|function|"
    r"query|schema|manifest|receipt|digest|report|readme|doc|docs)\b\s+(?:is|was|are|were|looks|"
    r"seems|reads)\b", re.I)

# Self-correction: a judgement word owned by the speaker, within 30 characters.
SELF_JUDGE_RX = re.compile(r"\b(?:I|my|we|our|myself)\b[^.!?]{0,30}?" + JUDGE_P, re.I)

# An agent owning the judgement: "Codex's fix was sloppy", "the model is unreliable".
AGENT_JUDGE_RX = re.compile(AGENT_P + r"(?:'s|s')?[^.!?]{0,40}?" + JUDGE_P, re.I)

_SENT_SPLIT = re.compile(r"(?<=[.!?\n])\s+")

# How close a person reference and a judgement must be to count as predication.
WINDOW = 80


def _sentences(text):
    for s in _SENT_SPLIT.split(text):
        s = s.strip()
        if s:
            yield s


def classify_opinion(content):
    """Return (label, reason). Conservative: returns (OK, '') unless a human
    reference and a judgement of that human co-occur and survive every veto."""
    if not content:
        return OK, ""
    # Bounded work: the judgement lexicon is rare, so test it once over the whole
    # payload before paying for sentence splitting on a 200 KB tool result.
    if not JUDGE_RX.search(content):
        return OK, ""

    for sent in _sentences(content):
        if len(sent) > 600:          # a wall of log output, not a sentence about anyone
            continue
        if not JUDGE_RX.search(sent):
            continue

        if TECH_VETO_RX.search(sent):
            continue
        if SELF_JUDGE_RX.search(sent):        # the assistant judging itself
            continue
        if AGENT_JUDGE_RX.search(sent):       # an agent's artefact, not a human
            continue
        if ARTEFACT_RX.search(sent):          # a thing, not a person
            continue
        if not PERSON_RX.search(sent):        # pronouns alone are not a person reference
            continue

        # Predication test: a person reference and a judgement within WINDOW
        # characters of each other, in either order.
        for p in PERSON_RX.finditer(sent):
            for j in JUDGE_RX.finditer(sent):
                if abs(j.start() - p.start()) <= WINDOW:
                    reason = "judgement '%s' applied to person reference '%s'" % (
                        j.group(1).lower().strip(), p.group(0).lower().strip())
                    return OPINION, reason[:200]

    return OK, ""


def classify(content, redaction_hits):
    """Row-level label. `redaction_hits` is the list of pattern names that fired."""
    if redaction_hits:
        return CREDENTIAL, "credential value replaced: " + ", ".join(sorted(set(redaction_hits)))
    return classify_opinion(content)


# ---------------------------------------------------------------------------
# Self-test. Positive controls prove the classifier can fire at all; the negative
# controls are real sentences taken from these transcripts.
# ---------------------------------------------------------------------------

MUST_FLAG = [
    "Vikram's fix was sloppy and he plainly does not understand the schema.",
    "Honestly the architect is incompetent at anything touching CI.",
    "The client is a liar; he deliberately hid the outage from us.",
    "Vikram is brilliant at this, far sharper than the last owner.",
    "the user is lazy and never reads the findings before replying",
    "The manager cannot be trusted with a release window.",
    "the colleague who wrote this is unprofessional and rude in review",
]

MUST_NOT_FLAG = [
    # real sentences from the corpus
    "the loader asserts payloadRequests === 0 at mount - lazy until the user acts.",
    "He is right and my diagnosis was wrong in its conclusion, though not in its evidence.",
    "You are a hostile reviewer.",
    "the architect is asleep until 10:00 BST and wants roughly ten GridAtlas generations by then.",
    "A ratio below 1.0 is physically nonsense for solar.",
    "Contributor username, UID and changeset are deliberately excluded from published tables.",
    "work hard dont be lazy and good night",
    "However, as curtailment times are an unknown, it would be difficult to calculate the reduction.",
    "This is the key find - the app already has an additive pattern: lazy-loaded cartridge sections.",
    "Vikram found it from his phone and he is right: none of the pipelinenews are on globalgrid2050.com.",
    "Weights to be set by the architect, not assumed.",
    "Vikram tested the link working before the recent versions.",
    # agent-on-agent artefact assessment, explicitly neutral
    "Codex's fix was sloppy and the digest did not match.",
    "The model is unreliable on long tool results.",
    # artefact judgements
    "The number is nonsense and the manifest is misleading.",
    "the test is flaky on the Windows runner",
    # self-correction
    "I was careless with the denominator and the summary changed meaning.",
    # neutral technical prose
    "the pin held and the digest matched",
    "gridatlas 239, globalgrid2050 3,597 files carry w/crlf in the working copy.",
]


def _selftest():
    fails = []
    for s in MUST_FLAG:
        lab, why = classify_opinion(s)
        if lab != OPINION:
            fails.append(("FALSE NEGATIVE", s, lab, why))
    for s in MUST_NOT_FLAG:
        lab, why = classify_opinion(s)
        if lab != OK:
            fails.append(("FALSE POSITIVE", s, lab, why))
    print("positive controls (must flag)     : %d" % len(MUST_FLAG))
    print("negative controls (must not flag) : %d" % len(MUST_NOT_FLAG))
    for kind, s, lab, why in fails:
        print("  %-15s %-22s %s  [%s]" % (kind, lab, s[:80], why))
    print("failures: %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(_selftest())

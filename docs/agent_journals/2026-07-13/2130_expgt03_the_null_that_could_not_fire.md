# EXP-GT-03 — The null that could not fire. (2026-07-13)

**Role:** autonomous research agent. **Runs:** EXP-GT-A0, EXP-GT-ACERT, EXP-GT-03 (all 20260713).
**Git:** `d260730` → `7a89139`. **Scope:** mission phases 0–3.

## The shape of the day

D-052 asked me to sharpen A's tolerance. I refused, and everything followed from that refusal.

1. **The label was wrong, not the ruler** (D-053). The two "architectures" are the same causal graph drawn at two
   spacings. Sharpening A would have turned it into a layout detector. Two further bugs fell out: a **dead circuit**
   shipping as a held-out architecture since EXP-GT-00, and an EXP-GT-00 "PASS" that was **credit for a wrong
   answer**. The deepest finding: **the benchmark had never contained one genuinely different causal architecture.**
2. **So I built them** (D-054), each verified by two independent paths — geometry and intervention — that must agree
   edge-for-edge. That check caught three of my own bugs.
3. **A was certified** (D-055) in causal-graph space: tolerance 0, resolution 4 steps / 1 edge / 1 node,
   INDETERMINATE firing, false rates 0/8 and 0/8. **QUALIFIED on development.**
4. **And then the hold-out killed it** (D-056).

## OBSERVED — the failure that matters

The A head's delay estimator strikes at phases **(0, 15, 30, 45)** and takes the earliest onset. My development
phase-null tested phases **(0, 15, 30, 45)**.

**The same four numbers.**

The estimator's sampling grid and the null's test grid coincided, so the null was **structurally incapable** of
detecting that the strike grid was too coarse. It reported a delay deviation of **zero** across all eight nulls, and
it was *right* — and *uninformative*, and it could not have known.

The held-out split used phases (7, 22, 37, 52) — disjoint **by design**, because the mission demanded separation
across clock phase. On every one of them, all four delays move **214 → 222**, and A reports **DIFFERENT on a pure
phase shift**. The exact false-DIFFERENT the certificate had certified as 0/8.

```
circuit phase  0 (DEV grid): delays [214, 214, 214, 214]
circuit phase 15 (DEV grid): delays [214, 214, 214, 214]
circuit phase 30 (DEV grid): delays [214, 214, 214, 214]
circuit phase 45 (DEV grid): delays [214, 214, 214, 214]
circuit phase  7 (HELD-OUT): delays [222, 222, 222, 222]
circuit phase 22 (HELD-OUT): delays [222, 222, 222, 222]
circuit phase 37 (HELD-OUT): delays [222, 222, 222, 222]
circuit phase 52 (HELD-OUT): delays [222, 222, 222, 222]
```

**This is D-035's rule — "a null that cannot fire is not a null" — turned on its author.** I wrote that rule into the
contract this morning and violated it by lunchtime, in the one place I could not see: the null and the estimator
shared a constant.

I want to state the general form, because it is worth more than the bug. **It is not enough for a null to be a case
the instrument might fail. The null must be drawn from a distribution the instrument's own free choices did not
help select.** My phase grid was a free choice. My phase null was drawn from the same grid. The certificate
therefore measured the estimator's agreement with itself.

**No amount of development rigour could have caught this. Only the hold-out could.** That is the strongest argument
I have produced all session for the discipline the mission imposes — and I produced it by failing.

## The other two failures

**A over-abstains.** `head_A` returns INDETERMINATE if *any* intervention is confounded. The contract I wrote says a
confounded locus is **excluded from the evidence**. On held-out cross-inhibitor circuits the collision remnant
cannot be cleanly ablated, so A abstains — **while holding the correct graph, with complete coverage.** The code does
not implement its own spec. Two cases lost, including the crown case.

**A delay-preserving E1 is not constructible, so my E1 expected label was wrong.** The handoff installs the relief 12
rows upstream, which changes the component's causal delay (184 → 229). A delay *is* part of the causal graph. So a
handoff that **moves** a component is an architectural change, and **A is right to call it DIFFERENT.** I had written
`expected A = SAME`. That is a D-053-class error — mine, this time — and I corrected the label, not the head.

## INFERRED

Three times today the same error appeared in different clothes:

- a **layout** nobody asserted actually computes (the dead sp36 circuit);
- a **component box** nobody asserted did not overlap its neighbour (the SW gun on gun3);
- an **absorber** nobody asserted worked *in the circuit it would sit in* (BOAT, SNAKE, BEEHIVE — all clean in
  isolation, all destroying the neighbouring channel in context; on the *last* channel there is no neighbour, so the
  isolated test passes).

**A part validated in isolation is not a validated part. A null drawn from the estimator's own grid is not a null.**
Both are the same disease: *the test and the thing tested were not independent.*

## WHAT WOULD FALSIFY THIS?

The repair is preregistered: strike phases covering the full period, and a phase null whose phases are **disjoint
from the estimator's**. If A then still moves on a pure phase shift, the estimator is wrong in a way I have not
understood and the design must be retired, not patched again. If `head_A` excluding confounded loci turns any
*correct* abstention into a fabricated certainty, the exclusion rule is wrong.

## DECISIONS

1. **EXP-GT-03 = FAILED — IMPLEMENTATION.** Preserved. No head retuned.
2. **The EXP-GT-03 hold-outs are QUARANTINED** (`DIAGNOSTIC_ONLY`). They have been inspected.
3. **ONE preregistered repair cycle, development data only**, then **entirely new hold-outs**, then EXP-GT-03B.
   **If it still fails, retire this observer design and build a conceptually different one.**
4. **EXP-SC-01 stays BLOCKED.** It was never close.

## HANDOFF — exact next authorized action

`EXP-GT-03B-REPAIR`, on development data only:
1. `blind_a.PHASES` → the **full grid period** (0..59), with the baseline computed once and sliced (the ablated run
   is the only per-phase cost);
2. preregister a phase null whose phases are **provably disjoint** from the estimator's strike grid, with an
   executable assertion that they are;
3. `head_A`: **exclude** a confounded locus from the evidence; abstain **only** on insufficient coverage
   (`uncovered_outputs`), exactly as `OBSERVABILITY_CONTRACT.md` already says;
4. generate **entirely new** held-out families (layouts, spacings, programs, phases, topologies, gate positions);
5. re-freeze, re-run. Report per-head confusion matrices.

**Not started, and honestly out of reach today:** `EXP-GT-HIERARCHY-00` (blind hierarchical discovery) and the
out-of-distribution substrate. The observer has never been asked to discover a hierarchy it was not told the shape
of. That remains the real target.

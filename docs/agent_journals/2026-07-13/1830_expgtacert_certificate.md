# EXP-GT-A-CERT — A is certified. The three things that nearly certified a fiction. (2026-07-13)

**Role:** autonomous research agent. **Runs:** EXP-GT-A0-20260713-001, EXP-GT-ACERT-20260713-001.
**Git:** `d260730` → `f861b56` → this. **Scope:** Phases 0–2 of the metrology mission.

## What was asked, and what I did instead

D-052 said: derive a finer tolerance so `A` can resolve a 5-column channel-gap difference. I did not, because the
premise was false (D-053): the two "architectures" are the **same causal graph**, and sharpening `A` would have
turned it into a layout detector. The benchmark had **no architectural variation at all**, so there was nothing for
a finer tolerance to resolve. I built architectures that genuinely differ (D-054) and then certified `A` in
**causal-graph space** (D-055).

## OBSERVED — the certificate

Delay tolerance **derived from the development null: 0 steps** (8 nulls: phase ±, translation, spacing, inert
decoration, decoy eaters). **false-DIFFERENT 0/8. false-SAME 0/8.** Certified resolution: **delay edit 4 steps**
(the finest the substrate admits), **1 edge**, **1 node**, redundancy change detected, component separation limit
4 cells. **INDETERMINATE fires** on a coverage-starved probe. All three verdicts fired. **QUALIFIED** (development).

The blind head — raw frames, its own interventions, and the output line, nothing else — recovers every hidden graph,
**including an emergent shielding edge that the hand-written wiring diagram did not contain** (`gun3 → out2`: the
inhibitor stream is consumed by channel 3, so ablating channel 3's gun frees it to kill channel 2).

## The three things that nearly certified a fiction

**1. Micro-ablation does not remove a component — it REPLACES it.** A 5×5 tile cleared inside a Gosper gun does not
delete the gun. It mutilates it into a *different working machine* emitting a stream down a new diagonal, landing at
output columns (55–58, 95–98, 135–138) that carry nothing in the intact circuit. My first tomography inferred the
causal graph of **a system that never existed**: 20 "components" for a 4-component circuit, with edges in which
deleting matter made an output *rise*. **The fix is not a better clustering algorithm. It is to intervene at the
scale of a discovered component and to PROVE the intervention clean.**

**2. A delay measured at one phase is not a delay.** Ablating at *t*=0 destroys whatever is in the box at that
phase, so the naive onset swung by **15 steps** (214 vs 229 across a half-period shift). That inflated the null
tolerance to 15 and cost `A` its finest resolution (8 steps instead of 4). A causal delay is a property of the
**path**, not of when we happened to strike it — it is the **earliest onset over a full cycle of strike phases**.
The null deviation went to **zero**.

**3. A bucket boundary is not a tolerance.** I quantized delays by `d // (tol+1)`. With tol = 15, the values 214 and
229 — which differ by exactly 15, i.e. *within* tolerance — fall in buckets 13 and 14, and the head called two
nulls DIFFERENT. Tolerances must be compared **pairwise**.

Each of these was caught **only because the null was MEASURED rather than assumed**. A certificate is not paperwork;
it is the thing that catches you.

## INFERRED — and this is the finding I did not expect

**In this circuit family, the memory word IS the architecture.** A memory bit of 0 is implemented by *adding an
eater*, so setting a bit adds a node and two edges. Therefore:

- "Same architecture, different program" is **NOT CONSTRUCTIBLE** here;
- any head that "passes" program-invariance on this family passes a test that **cannot fire**;
- **EXP-GT-02B's A head passed exactly that test** — by comparing channel *positions*, which no program can move.
  **That pass is VACUOUS and is now marked so.**

This is the same class of error as D-053, one level deeper: not a mislabelled *case*, but a benchmark that cannot
express the invariance it demands. EXP-GT-02B had already disclosed that S and F are extensionally equal in this
family. Add A, and *all three* factors move with the single memory variable. **The factorization is right (D-049);
this benchmark simply cannot demonstrate that the factors are independent** — except through one case, and it is
the crown case: `GATE3` vs `XINHIB`, where **A = DIFFERENT while S = SAME and F is bit-identical.** That single case
is what rescues the factorization from vacuity here.

## WHAT WOULD FALSIFY THIS?

The certificate is granted on **development data only**. If, on entirely unseen architectures, layouts, programs and
component implementations, `A` shows a non-zero false-SAME or false-DIFFERENT rate, or fails to abstain when it
should, the certificate is withdrawn. **That is EXP-GT-03 and it has not been run.**

Falsifiers for the specific claims: any development null with a non-zero delay deviation; any 4-step delay edit read
as SAME; a cross-stream inhibitor whose added edge is missed; an intervention that passes the cleanliness check yet
demonstrably shattered its target.

## FAILURES / DEAD ENDS

- Naive tile-scan tomography (above). Abandoned, and the reason recorded rather than the code quietly deleted.
- Judging "did this ablation shatter the world?" at *t* = OBS flagged **two perfectly clean ablations as
  confounded**, because freeing a suppressed stream must refill the pipeline to the boundary first. **An abstention
  caused by the observer's own impatience is not honest uncertainty.**
- `MERGE_GAP = 6` swallowed all four guns into one "component". The value is now **4**, and it is *measured*: a
  gun's internal high-occupancy fragments are ≤ 4 apart, adjacent guns are 5 apart. This is a **declared resolution
  limit**, not a tuned constant.
- The `Write` tool truncated a source file mid-line at 11,095 bytes while leaving it importable. All code is now
  written through the shell and byte-count verified.
- Background processes do not survive a bash call in this sandbox (`--unshare-pid`). The certificate is now
  memoised to disk and resumable.

## HANDOFF — exact next authorized action

**EXP-GT-03.** Quarantine every circuit inspected during this diagnosis as `DIAGNOSTIC_ONLY — NOT ELIGIBLE FOR FINAL
EVIDENCE`. Generate entirely new held-out families with a frozen manifest and hashes, separated simultaneously
across causal topology, program word, spatial layout, clock phase, component implementation, replacement
implementation and perturbation schedule. Add **executable leakage assertions**. **Freeze every head.** Then evaluate
the full factorized observer (A, S, F, L, M, G) prospectively, reporting per-head confusion matrices, false-SAME,
false-DIFFERENT and false-certainty rates. **No head may be retuned after the freeze. EXP-SC-01 stays BLOCKED.**

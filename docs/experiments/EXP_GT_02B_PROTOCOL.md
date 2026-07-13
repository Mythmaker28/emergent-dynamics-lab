# EXP-GT-02B — repair A, F and L. No weight tuning.
**Preregistered and frozen BEFORE any result.** The certified S head (D-051) is preserved **exactly as certified**.
The exhaustive stride-1 blind intervention scan is treated as a **gold-standard causal-tomography instrument**;
its cost is **not** optimized yet.

## 0. Scope of the certified S head (recorded narrowly)
S reads **the declared memory-word family** (1010, 0101, 1111, 0000) across the **development and held-out layouts**.
**It is NOT a universal memory detector** and is not claimed to be.

## 1. Clock inference and phase repair (the explicit fix for v2's confound)
- The clock period is **inferred from the raw trajectory** (autocorrelation of the population series), with **no
  hidden labels**. It must recover the true gun period.
- Fingerprints are accumulated over an **integer number of inferred periods**, and summarized **phase-invariantly**
  (responses aligned to their own onset; passive signatures folded over the inferred period).
- **A post-handoff transient is NEVER compared with a fresh initialization.** Every configuration is **re-settled**
  to a common established state before tomography.
- **MUST-PASS / MUST-FAIL:** a **pure phase shift** of the same circuit must leave **A and F unchanged**, while a
  real architectural or functional change must move them. A head that cannot tell these apart is broken.

## 2. F — functional I/O transfer relation
From a **frozen standardized input-intervention suite** over **whole logical episodes**: a standardized pulse is
injected at every column (exhaustive), the **time-resolved output response** is recorded over complete inferred
periods, and the transfer relation is expressed **per channel ordinal** (layout- and latency-normalized).
**Two systems implementing the same function by different mechanisms must score F = SAME.**

## 3. A — time-lagged causal influence graph
Inferred from blinded interventions: **onset delays**, **intermediate dependencies**, **memory influence** and
**redundancy**, expressed in the intrinsic transverse frame. Invariant to translation, spatial layout, cyclic clock
phase, and functionally equivalent microscopic replacement.
**Different architectures implementing the same F must score A = DIFFERENT.**

## 4. L — three preregistered identifiable regimes
1. **SAME** — a continuously observed E1 handoff: uninterrupted lineage.
2. **DIFFERENT** — an observed branch/clone event followed by **divergent** trajectories.
3. **INDETERMINATE** — exact copies with distinct hidden pre-observation histories but **observationally identical**
   supplied data.
**Correct abstention PASSES. Fabricated certainty FAILS.**

## 5. E1 and E2, separately
**E1** (function-preserving handoff): preserve **A, S, F, L**; change **M**. Development **and entirely held-out**
replacement implementations, architectures, layouts, clock phases and programs.
**E2** (damage-and-repair): **F may transiently break** while lineage remains observable and recovery follows.
**E2 is never the Ship-of-Theseus equivalence case.**

## 6. Reporting and gating
**Every head reported separately. No composite, ever. Every new criterion must first prove it can BOTH fire AND
fail.** **EXP-SC-01 remains BLOCKED** until A, S and F pass prospectively on held-out cases and L demonstrates
calibrated SAME / DIFFERENT / INDETERMINATE.

## 7. Disclosed limitation of this benchmark
In this circuit family the memory word **fully determines** the input-output transfer relation and nothing else does,
so **S and F are extensionally equal here**. They are computed by **different procedures** and remain conceptually
distinct, but their agreement on these circuits is a **property of the benchmark, not evidence of independence**.
This is stated in advance rather than discovered later and dressed up as a result.

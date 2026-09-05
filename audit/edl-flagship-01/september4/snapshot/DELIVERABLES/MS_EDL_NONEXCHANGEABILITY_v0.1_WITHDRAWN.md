# An intervention that deletes its own comparator

### Removing an object removes a competing termination channel, and a pre-registered paired endpoint stops being exchangeable

**Draft v0.1 — 2026-09-04 — NOT SUBMITTED — for adversarial review only**

---

## Abstract

In individual-tracking experiments on spatial stochastic systems, an object's
*identity interval* is usually terminated by **relational** events: it merges
with a neighbour, it splits, it loses every successor within a linking radius, or
it disappears. We report a design failure that follows directly from this, and
that we believe is general. In a pre-registered paired intervention on a
six-species stochastic lattice automaton, the treatment removes one object (the
parent) in order to test whether a second object (the locked daughter) has an
independent post-removal course. The parent is also the only object that can
supply the *merge* termination channel. Removing it therefore does not merely
change the outcome; it **deletes one of the ways the endpoint can end**, in the
treated arm only.

Measured over 41 matched pairs, the observed termination mixes are
`SPLIT_OR_TIE / EXTINCTION / MERGE / OUT_OF_RANGE` = **32 / 9 / 0 / 0** under
treatment and **28 / 0 / 7 / 6** under control; the tracked object is the world's
only component on **99.6 %** of the in-window steps under treatment against
**6.4 %** under control. The same asymmetry appears in an earlier, independent
33-pair campaign under the same law (**29 / 2 / 2** against **22 / 5 / 6**). The
pre-registered paired signed-rank test is not rescued by this: it does not reject
(duration *p* = 0.246, exposure *p* = 0.348, exact, two-sided, n = 41), and we
could construct no specification that flips its conjunctive decision rule. What
changes is not the verdict but **what the verdict is about**.

We give the arithmetic reason the channel is deleted, quantify the resulting
mixture in the published *p*-value, show that every repair available *post hoc*
conditions on a post-treatment variable and is therefore inadmissible as an
estimand, and state the design rule we think follows: **an endpoint's termination
channels must be invariant under the intervention, or the intervention must be
analysed as acting on a competing-risks structure declared in advance.**

We make **no claim** about persistence, ownership, individuation, minimal
reproduction, or heredity. Programme statuses are unchanged and re-emitted in §7.

---

## 1. The setting

The system is a stochastic reaction–diffusion automaton on a torus, six species
(X, Y, SX, SY, WX, WY), `L = 36`, per-cell capacity 16, a frozen scheduler
(`diffuse ×4 → react → decay → feed`), horizon `T_HORIZON = 11000`. A **centre**
is a connected component of Y-occupied cells under toroidal single-linkage at
`CORE_R = 5.0`. An **identity interval** is a maximal run over which the
centre-to-centre pairing between consecutive steps is mutually unique; a split, a
merge or a tie **terminates** the interval rather than being resolved by
preference.

At a frozen trigger step `t_m` a second centre is named — the **locked
daughter** — by code fixed before any world was run. The experiment then compares,
on the same seed:

* **SHAM** — nothing happens;
* **SELECTIVE** — the parent's Y is removed through the engine's own decay
  channel (Y → WY).

The pre-registered primary endpoint is the **post-intervention duration of the
locked daughter's identity interval**, with **particle-step exposure** as
co-primary, analysed as a paired exact Wilcoxon signed-rank test on log
differences (SELECTIVE − SHAM), with a conjunctive decision rule requiring both
endpoints to reject at α = 0.05 with concordant sign. Everything in this
paragraph was frozen before any world was run; none of it is modified here.

## 2. The defect

The frozen linking rule terminates an identity interval by exactly five channels:

| | channel | requires |
|---|---|---|
| (a) | `SPLIT_OR_TIE` | two or more successors in range |
| (b) | `MERGE` | two or more **predecessors** mapping to one successor |
| (c) | `OUT_OF_RANGE` | no successor within `CORE_R` |
| (d) | `NO_COMPONENT_AT_THE_NEXT_STEP` | no components at all |
| (e) | horizon | the run ends |

Channel (b) is **arithmetically impossible when the tracked object is the only
component in the world**: the implementation requires strictly more than one
backward-mapped predecessor. The treatment removes the parent. In the treated arm
the daughter is, essentially always, the only object present. Channel (b) is
therefore not made *rarer* by the treatment — it is made **unavailable**.

This is not a modelling nicety. It means the two arms are not the same tracking
problem, and the endpoint measured in one is not the endpoint measured in the
other.

## 3. What is measured

**3.1 Termination mixes** (n = 41 matched pairs, both arms on the same seed):

```
SELECTIVE : SPLIT_OR_TIE 32   EXTINCTION 9   MERGE 0   OUT_OF_RANGE 0
SHAM      : SPLIT_OR_TIE 28   EXTINCTION 0   MERGE 7   OUT_OF_RANGE 6
```

Cross-tabulated, 22 of 41 pairs end the same way in both arms; the other 19 do
not. The identity is terminated by total local extinction in **9 of 41** treated
arms and **0 of 41** controls (exact McNemar, 9 versus 0 discordant,
*p* = 0.0039) — a figure we report as a **descriptive post-hoc diagnostic with no
error rate claimed**, precisely because §2 shows the two arms do not offer the
same set of ways to end.

**3.2 Occupancy.** Over the daughter's own window: the world holds exactly one
component on 9 672 of 9 713 treated steps (**99.6 %**) against 534 of 8 353
control steps (**6.4 %**).

**3.3 Independent corroboration.** The same profile appears in the earlier,
independently accrued 33-pair campaign under the same law and the same treatment:
`SELECTIVE` 29 split / 2 merge / 2 extinction, `SHAM` 22 split / 5 merge / 6
out-of-range. Two campaigns, accrued years apart in programme time and under
different ceilings, show the same structural signature.

**3.4 The frozen test, executed.** Exact two-sided signed-rank, n = 41, no ties
in |differences|:

| endpoint | *W*⁺ | *p* | median Δ | Hodges–Lehmann | 95 % CI |
|---|---:|---:|---:|---:|---|
| duration | 521.0 | 0.2464 | +0.2136 | +0.3331 | (−0.2385, +0.8370) |
| exposure | 504.0 | 0.3479 | +0.5695 | +0.3161 | (−0.3110, +0.8739) |

Conjunctive rule not met. Terminal:
`MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER`,
with `NULL_RESULT_INTERPRETATION = INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT`.

All twelve statistics above were **reproduced to the last digit** by a
from-scratch implementation sharing no code path with the original (exact null
distribution of *W*⁺ by dynamic programming; Hodges–Lehmann by Walsh averages;
interval by test inversion). This is a **reconstruction on the same data, not an
independent replication**.

## 4. What the defect does to the inference

The published *p* = 0.246 is a **mixture**. The 13 pairs containing an extinction
have median log duration difference **−0.3231** (6/13 positive); the other 28 have
**+0.6325** (19/28 positive). Sensitivity, all of it *post hoc*:

| specification | n | duration *p* | duration median | exposure *p* |
|---|---:|---:|---:|---:|
| the frozen test, as executed | 41 | 0.2464 | +0.2136 | 0.3479 |
| drop the 9 treated window-extinctions | 32 | **0.0433** | +0.6325 | 0.0770 |
| always-survivor stratum | 28 | 0.0774 | +0.6325 | 0.0946 |
| drop the 7 control MERGE pairs | 34 | 0.2932 | +0.2071 | 0.3605 |
| pairs terminating the same way in both arms | 22 | 0.1207 | +0.4454 | 0.1465 |

Two things must be said in the same breath, and we say them.

**First, none of these is an alternative result.** Every restriction conditions on
a variable realised *after* treatment. The programme's own endpoint
pre-registration forbids survivor subsetting by name, and the authorisation under
which the test was executed excludes it explicitly. They are diagnostics. They
estimate a narrower quantity than the one that was frozen, and we do not report
any of them as the answer.

**Second, the terminal string is robust.** No specification we could construct
meets the conjunctive rule: duration alone rejects only after dropping the nine
extinctions; exposure never rejects; pooling the 33 + 41 = 74 pairs gives 0.141
and 0.117. The verdict does not move. Its **meaning** does: a positive result
here would have been partly a statement about how many objects the tracker had to
distinguish, not only about the daughter's course.

## 5. Power, for the record

Resampling the 41 observed paired differences, the projected power of the frozen
conjunctive rule is **0.16 at n = 41**, 0.32 at 100, 0.55 at 200, and reaches
0.80 near **n ≈ 400**. At the admissible-pair yield actually observed in this
programme (≈ 4.1 %), 400 pairs cost ≈ 9 757 worlds and ≈ 6 300 arm-instances —
about seven times the largest ceiling this programme has ever authorised. The
test was executed at an *n* where it could hardly conclude, and the honest
description of the outcome is `INCONCLUSIVE`, not "no effect".

## 6. The design rule we propose

1. **Termination channels must be invariant under the intervention.** Before
   freezing a duration-like endpoint on a tracked individual, enumerate the ways
   the interval can end and check, arithmetically, that the intervention removes
   none of them in one arm only. This check costs nothing and is mechanical.
2. **Where invariance is impossible, declare the competing-risks structure in
   advance.** Name each termination channel, name which are events of interest
   and which are competing, and pre-register the cause-specific contrast. A
   *post-hoc* competing-risks analysis conditions on post-treatment information
   and cannot repair a frozen endpoint.
3. **A refutation condition must be operationalised in code, with a capability
   test, before the first world.** A condition frozen in words but never turned
   into a procedure can be given a reading after the data are in; a condition that
   has never been shown *able to fire* is not a test. In the parent programme,
   one such omission is the entire reason a completed, technically flawless
   41-triple campaign adjudicates nothing.
4. **Report the termination mix.** It is one table. Without it, a paired duration
   contrast on tracked individuals cannot be read as a competing-risks table at
   all, and the reader has no way to see the defect.

## 7. Scope, and what this paper does not claim

This paper reports a **methodological defect and its measured consequences**. It
makes no claim about what the tracked objects are or do.

Explicitly **not** claimed: that a historical state persists; that persistence is
causal; that any object owns, controls, or individuates anything; that any
criterion of minimal reproduction is met; that any trait is transmitted. The
tracked object is 1–3 cells and 1–3 Y quanta at `t_m`, peaking at 1–6 Y over its
life in 40 of 41 treated arms — a scale at which no such reading would be
warranted even if it were sought.

The structural finding is a fact about the **experimental design**, corroborated
across two campaigns. The quantitative consequences (§4) rest on n = 41 and are
*post hoc*. The *p*-values in §3.4 are a faithful execution of a frozen
statistical procedure on a matched sample that does **not** satisfy that
procedure's original accrual rule: applied to this seed stream, the original
stopping rule exhausts at 38 pairs and would have returned
`INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS`.

Programme statuses, re-emitted unchanged: `H3_STATUS = NOT_TESTED`;
`REPRODUCTION_STATUS = NOT_TESTED`; `HEREDITY_STATUS = NOT_TESTED`;
`AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`; `X_LAWSPEC_BASELINE = UNCHANGED`;
`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`.

## 8. Priority and provenance

The asymmetry reported here was **first identified inside the parent programme**,
not by this paper: in a prior-art map written before the analysis, in a
pre-freeze power analysis that declared the frozen endpoints
`NON_INTERPRETABLE__CONFOUNDED_BY_DIFFERENTIAL_MORTALITY`, and in the adversarial
checker's findings on the executed analysis. This paper's contribution is to
assemble it, verify it, corroborate it on a second campaign, and state the
general rule — **not** to discover it. We say so here rather than let a reader
find it.

The definition of a centre as a *connected* component is a contested modelling
assumption; at least one recent published criterion in this area admits spatially
disjoint replicators. Every result above is conditional on the connected-component
definition, and a disjoint-object definition could change the termination mixes.
The programme has recorded per-step connectivity exposure so that this assumption
can be re-tested later without re-spending a campaign.

## 9. Data and code availability

Verification and recomputation scripts (`edl_verify_recovery.py`,
`edl_omldct03_independent.py`; standard library only) ship with the recovery
bundle, together with the frozen method files pinned by
`METHODS_HASH = 21571fb4…d4d63c920a007e188bdc24e0d94d1f99` (17 files, recomputed
and matching), the published content hashes (7/7) and six verbatim adversarial
checker returns. **The 123 raw archives (~440 MB) are not included**; the figures
in §3.2, §3.3 and §4 are quoted from committed artefacts and the verbatim checker
return, and were **not** recomputed from raw in this work. Reconstruction of
§3.4 from `PER_PAIR` is complete and reproducible offline.

# An intervention that suppresses its own comparator

### Removing an object suppresses a competing termination channel, and a pre-registered paired endpoint stops being exchangeable

**Draft v0.2 — 2026-09-04 — NOT SUBMITTED — revised after independent adversarial review (28 findings, 28 accepted)**

---

## Abstract

In individual-tracking experiments on spatial stochastic systems, a tracked
object's *identity interval* is terminated by **relational** events: it merges
with a neighbour, it splits, it loses every successor within a linking radius, or
its material disappears. We report a design failure that follows directly from
this. In a pre-registered paired intervention on a six-species stochastic lattice
automaton, the treatment removes one object (the parent) to test whether a second
object (the locked daughter) has an independent post-removal course. The parent is
also the object that supplies the *merge* termination channel. Removing it
therefore does not merely change the outcome; it **suppresses one of the ways the
endpoint can end**, in the treated arm only — arithmetically unavailable whenever
the daughter is the world's only component, which is 99.6 % of the at-risk steps,
and rare otherwise.

Over 41 matched pairs the termination mixes are
split-or-tie / material-extinction / merge / no-successor-in-range =
**32 / 9 / 0 / 0** under treatment and **28 / 0 / 7 / 6** under control; the same
asymmetry appears in an earlier, seed-disjoint 33-pair campaign under the same law
(split 29 / merge 2 / extinction 2 against split 22 / merge 5 / no-successor 6).
The pre-registered signed-rank test does not reject (duration *p* = 0.246,
exposure *p* = 0.348, exact, two-sided, n = 41), and no specification we could
construct flips its conjunctive rule. What changes is not the verdict but **what
the verdict is about**.

We then do what the defect demands rather than only describing it. A
**competing-risks re-analysis was specified by an author who had not seen any
outcome value**, frozen and hashed before execution, and shipped with a capability
test proving the statistic can fire, does not fire under arm-label permutation,
and is invariant — bit for bit — under an arm-dependent renaming of termination
strings that moves a naive statistic by eight pairs. Executed on all 41 pairs with
no exclusions, it returns **NEGATIVE**: the pre-declared adverse direction is not
supported (17 pairs worse, 24 better, exact one-sided *p* = 0.894, critical count
28, resolution demonstrated adequate). The differential-mortality confound does
not dominate an arm-symmetric ordered composite.

We claim **nothing** about persistence, ownership, or individuation, and no
programme status is moved; the frozen status tokens are re-emitted verbatim in §8.

---

## 1. The setting

A stochastic reaction–diffusion automaton on a torus, six species (X, Y, SX, SY,
WX, WY), `L = 36`, per-cell capacity 16, frozen scheduler
(`diffuse ×4 → react → decay → feed`), horizon `T_HORIZON = 11000`. A **centre** is
a connected component of Y-occupied cells under toroidal single-linkage at
`CORE_R = 5.0`. An **identity interval** is a maximal run over which the
centre-to-centre pairing between consecutive steps is mutually unique; a split, a
merge or a tie **terminates** it rather than being resolved by preference.

At a frozen trigger step `t_m` a second centre is named — the **locked daughter** —
by code fixed before any world was run. Two arms run on the same seed with a
bit-identical prefix through `t_m`:

* **SHAM** — nothing happens;
* **SELECTIVE** — the parent's Y is removed through the engine's own decay channel
  (Y → WY).

The pre-registered primary endpoint is the **post-intervention duration of the
locked daughter's identity interval**, with **particle-step exposure** as
co-primary, analysed by paired exact Wilcoxon signed-rank on log differences
(SELECTIVE − SHAM) under a conjunctive rule: both endpoints must reject at
α = 0.05 with concordant sign. All of this was frozen before any world was run and
none of it is modified here.

## 2. The defect

The frozen linking rule terminates an identity interval by five channels:

| | channel | requires |
|---|---|---|
| (a) | `SPLIT_OR_TIE` | two or more successors in range |
| (b) | `MERGE` | two or more **predecessors** mapping to one successor |
| (c) | `OUT_OF_RANGE` | no successor within `CORE_R` |
| (d) | `NO_COMPONENT_AT_THE_NEXT_STEP` | no Y-occupied cell anywhere in the world |
| (e) | horizon | the window ends |

Channel (b) requires strictly more than one backward-mapped predecessor
(`omldct02_e3_b.py:107-131, 216-220`). When the tracked object is the world's only
component, that condition cannot be met. The treatment removes the parent; in the
treated arm the daughter is the world's only component on **99.6 %** of the
in-window steps. Channel (b) is therefore **arithmetically unavailable on almost
every at-risk step**, and merely rare on the rest — in the 33-pair campaign it
fired twice under treatment against five times under control. Suppression, not
deletion. The distinction matters: a deleted channel would be a theorem about the
design, a suppressed one is a measured property of these parameters.

Either way, the two arms are not the same tracking problem, and the endpoint
measured in one is not the endpoint measured in the other.

**A second, subtler point about the strings.** Channels (c) and (d) are not two
cleanly-named disjoint events. Both are emitted from the same predicate — no
linkable successor — split by a *global* property of the world. A daughter whose Y
dies while the rest of the world persists appears under (c); the adversarial
checker opened all six control cases individually and found **five of them** to be
exactly that. Counting (d) against (c) across arms therefore counts strings, not
events. We flag this because it is the trap the rest of this paper is built to
avoid.

## 3. What is measured

**3.1 Termination mixes** (n = 41 matched pairs):

```
SELECTIVE : SPLIT_OR_TIE 32   NO_COMPONENT 9   MERGE 0   OUT_OF_RANGE 0
SHAM      : SPLIT_OR_TIE 28   NO_COMPONENT 0   MERGE 7   OUT_OF_RANGE 6
```

22 of 41 pairs end the same way in both arms; 19 do not. We deliberately report
**no test on this table**: §2 shows that the four strings do not partition the
same event space in the two arms. The properly defined mortality contrast, over
the whole post-`t_m` trajectory, is **11 pairs where the treated arm's Y goes
extinct and the control's does not, 1 the reverse, 1 both, 28 neither**, exact
two-sided sign test *p* = 0.00634765625.

**3.2 Occupancy.** Over the daughter's own window, the world holds exactly one
component on 9 672 of 9 713 treated steps (**99.6 %**) against 534 of 8 353 control
steps (**6.4 %**).

**3.3 Corroboration on a second campaign.** The same profile appears in an earlier
33-pair campaign under the same law and the same treatment, accrued **five days
and two missions apart** under a different ceiling (512 against 926), on a
**disjoint seed set** (intersection 0, verified by regenerating the seeds from the
committed derivation): treated 29 split / 2 merge / 2 extinction; control 22 split
/ 5 merge / 6 no-successor.

**3.4 The frozen test, executed.** Exact two-sided signed-rank, n = 41, no ties in
|differences|:

| endpoint | *W*⁺ | *p* | median Δ | Hodges–Lehmann | 95 % CI |
|---|---:|---:|---:|---:|---|
| duration | 521.0 | 0.2464 | +0.2136 | +0.3331 | (−0.2385, +0.8370) |
| exposure | 504.0 | 0.3479 | +0.5695 | +0.3161 | (−0.3110, +0.8739) |

Conjunctive rule not met; terminal `EFFECT_NOT_DETECTED`, `INCONCLUSIVE`, with no
claim of equivalence and no claim of no effect. All twelve statistics reproduce to
the last digit under a from-scratch implementation sharing no code path with the
original — a **reconstruction on the same data, not an independent replication**.

One caveat on the decision rule itself: the two endpoints correlate at
**ρ = 0.9751** with sign agreement 41/41. The conjunction is close to one endpoint
reported twice, and buys little severity.

## 4. What the defect does to the inference

The published *p* = 0.246 is a **mixture**. The 13 pairs containing an extinction
have median log duration difference **−0.3231** (6/13 positive); the other 28 have
**+0.6325** (19/28 positive). Sensitivity, all *post hoc*:

| specification | n | duration *p* | duration median | exposure *p* |
|---|---:|---:|---:|---:|
| the frozen test, as executed | 41 | 0.2464 | +0.2136 | 0.3479 |
| drop the 9 treated window-extinctions | 32 | **0.0433** | +0.6325 | 0.0770 |
| always-survivor stratum | 28 | 0.0774 | +0.6325 | 0.0946 |
| drop the 7 control MERGE pairs | 34 | 0.2932 | +0.2071 | 0.3605 |
| pairs terminating the same way in both arms | 22 | 0.1207 | +0.4454 | 0.1465 |

**None of these is an alternative result.** Every restriction conditions on a
variable realised after treatment; the programme's own endpoint pre-registration
forbids survivor subsetting by name. We print the line that crosses α as
prominently as the lines that do not, because printing only the confound-favouring
half is the disclosure failure that got an earlier closure document withdrawn.

**And the terminal string is robust.** No specification meets the conjunctive rule;
pooling 33 + 41 = 74 pairs gives 0.141 and 0.117. The verdict does not move. Its
**meaning** does.

## 5. A competing-risks estimand, specified blind

Diagnostics are not a repair. The repair is an estimand that does not depend on
which arm can reach which channel. It cannot be written by anyone who has seen the
sensitivity table above — so it was not.

**Blinding.** The specification was written by an author given the design, the two
frozen classifiers, the field schema, and the single structural fact of §2, and
**no outcome value whatsoever**. The pre-registration records its own contamination
inventory and the classifier line numbers it read. It was hashed and committed
before the analysis file was opened.

**Mapping**, justified on the code rather than on interpretation:

| strings | cause | rank |
|---|---|---|
| `OUT_OF_RANGE`, `NO_COMPONENT_AT_THE_NEXT_STEP` | `NO_LINKABLE_SUCCESSOR` | 0 (worst) |
| `SPLIT_OR_TIE`, `MERGE` | `AMBIGUOUS_CONTINUATION` | 1 |
| `REACHED_THE_WINDOW_HORIZON` | `NO_TERMINATION_OBSERVED` | 2 (best) |

Both mergers are theorems about the linking map, not expectations. The first:
(c) and (d) discharge one predicate split by a global property, so the same
physical event changes label with the arm. The second: `MERGE` alone is
unreachable when the daughter is alone, but the **union** `SPLIT_OR_TIE ∪ MERGE`
is reachable in both arms. All three ranks are reachable on both sides.

**Estimand and test.** Lexicographic composite (rank, duration), higher is better;
θ = P(treated strictly worse) − P(treated strictly better) — a **total effect**,
identified by exact pairing alone. Pre-declared direction θ > 0. Paired exact sign
test, one-sided, α = 1/40 in integer arithmetic, no floating point at the
threshold. Retention: **all 41 pairs**, with the tempting exclusions named and
forbidden in advance.

**Capability test, 5/5.** The statistic can cross under a rule known to permit it;
does not cross under arm-label permutation (2 000 replicates, empirical rate
0.0135 ≤ α); survives two adversarial searches; its exact tail is cross-checked
against exhaustive enumeration of all 2^m sign sequences for m = 0…14 with zero
disagreement; and under a pure arm-dependent renaming of `OUT_OF_RANGE` to
`NO_COMPONENT_AT_THE_NEXT_STEP` in the treated arm the decision is **identical bit
for bit**, while a naive string-based statistic moves by **eight pairs**. The
artefact avoided is measured, not assumed.

**Result — NEGATIVE.**

| | |
|---|---|
| pairs retained | 41 / 41, no exclusions |
| treated strictly worse / better / tied | **17 / 24 / 0** |
| decided by rank alone / by the duration tiebreak | 11 / 30 |
| critical count at α = 1/40 | 28 · design could have rejected |
| exact one-sided *p* | 983500178123/1099511627776 = **0.8945** |
| θ̂ | **−0.1707** |
| terminal | `NEGATIVE` · threshold not crossed at adequate resolution |

The pre-declared adverse direction — the direction the differential-mortality
confound would produce — **is not supported**. The nine rank-0 outcomes in the
treated arm are outweighed by the duration tiebreak. The test is one-sided:
despite a negative θ̂, **nothing is claimed in the other direction**, and no
equivalence and no absence of effect are claimed.

## 6. Power, honestly

Resampling the 41 observed paired differences gives, for the frozen conjunctive
rule, 0.14 at n = 41, 0.32 at 100, 0.56 at 200, and about 0.83 at n = 400. Three
things must be said about that number and usually are not.

**It is power at the observed effect**, a monotone function of the observed *p*,
so "the test had power 0.14" restates "p = 0.246" and adds nothing.

**It has no error bar.** Under a double bootstrap (100 resampled truths × 200
draws), power at n = 400 ranges from 0.02 at the 5th percentile to 1.00 at the
95th, and **34 % of truths compatible with these data give power below 0.50 at the
same n**. The Hodges–Lehmann interval contains zero, so at the 95 % level the
sample size required for 0.80 is **not bounded above**.

**The design's own frozen power was 0.402 / 0.971 / 1.000** at n = 41 (Wilson lower
bound / point estimate / upper bound). It is therefore not the case that the test
was under-powered by design; it is the case that the design's power assumption was
wrong.

For scale: at the admissible-pair yield observed on the costed stream
(41/885 = 4.633 %, Jeffreys posterior median 4.65 %, 5th percentile 3.58 %), 400
pairs cost ≈ 8 600 worlds at the median rate and ≈ 11 200 at the unfavourable
quantile, ≈ 5 600 arm-instances against a largest recorded ceiling of 926, and
≈ 105 wall-clock hours on the measured two-worker throughput.

## 7. The design rule

1. **Termination channels must be invariant under the intervention.** Before
   freezing a duration-like endpoint on a tracked individual, enumerate the ways
   the interval can end and check, arithmetically, that the intervention removes
   none of them in one arm only. The check is mechanical and costs nothing.
2. **Where invariance is impossible, declare the competing-risks structure in
   advance**, name each channel, say which are events of interest, and pre-register
   the contrast. A *post-hoc* competing-risks analysis conditions on
   post-treatment information and cannot repair a frozen endpoint.
3. **Do not let a string be an event.** Two labels emitted from one predicate,
   split by a property that the intervention changes, will manufacture an arm
   effect out of a renaming. §5's capability test C5 measures exactly how much: 8
   pairs out of 41.
4. **A refutation condition must be operationalised in code, before the first
   world, with a capability test** — an adversarial demonstration that it *can*
   fire, paired with a control that does fire under a rule known to permit it. A
   condition never shown able to fire is not a test. In the parent programme one
   such omission is the whole reason a completed 41-triple campaign with zero
   technical failures adjudicates nothing.
5. **Report the termination mix.** It is one table, and without it a paired
   duration contrast on tracked individuals cannot be read as a competing-risks
   table at all.

## 8. Scope, and what this paper does not claim

This paper reports a **methodological defect, its measured consequences, and one
frozen re-analysis that returns a valid negative**. It says nothing about what the
tracked objects are or do.

Not claimed: that a historical state persists; that persistence is causal; that
any object owns, controls, or individuates anything; that any frozen programme
criterion is met. The tracked object is 1–3 cells and 1–3 Y quanta at `t_m`,
peaking at 1–6 Y over its identity interval in 40 of 41 treated arms.

The structural finding is a fact about the **experimental design**, corroborated
across two campaigns. The quantitative consequences of §4 rest on n = 41 and are
*post hoc*. The §3.4 *p*-values are a faithful execution of a frozen statistical
procedure on a matched sample that does **not** satisfy that procedure's original
accrual rule: applied to this seed stream, the original stopping rule exhausts at
38 pairs and would have returned `INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS`. A
further disclosure: the direction of a correlated paired contrast on these same 41
seeds was published two days before the frozen test was executed (24 positive /
7 zero / 10 negative, exact sign test *p* = 0.0243). This does not inflate the
type-I error; it costs the claim of blindness for that test — though not for §5,
whose author saw none of it.

Programme statuses, re-emitted verbatim and unchanged: `H3_STATUS = NOT_TESTED`;
`REPRODUCTION_STATUS = NOT_TESTED`; `HEREDITY_STATUS = NOT_TESTED`;
`AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`; `X_LAWSPEC_BASELINE = UNCHANGED`;
`ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`;
`COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED`;
`OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED`;
`CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED`;
`TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION`;
`FIMRCC01_E3_E4_E5_STATUS = FUTURE_QUESTION_RECORDED__NOT_AUTHORISED`;
`OBFOR01_HISTORICAL_WINDOW_STATUS = NOT_PORTABLE`; `RPP97_STATUS`, `RPP98_STATUS`
and `FIMRCC02_STATUS` all `WITHDRAWN` under their recorded strings;
`OMLDCT03_STATUS = FROZEN_STATISTICAL_PROCEDURE_EXECUTED_AT_ITS_REQUIRED_N_ON_A_MATCHED_SAMPLE_OBTAINED_OUTSIDE_ITS_ACCRUAL_RULE__EFFECT_NOT_DETECTED__INCONCLUSIVE`.

## 9. Priority and provenance

We did not discover the confound. **Differential mortality** is recorded three
times inside the parent programme: a prior-art map written at 02:07 on the day the
frozen test ran, a pre-freeze power analysis at 02:11 that declared the frozen
endpoints `NON_INTERPRETABLES__CONFONDUS_PAR_LA_MORTALITE_DIFFERENTIELLE`
("non-interpretable, confounded by differential mortality"), and the adversarial
checker's F2. The **suppression of the merge channel** is recorded once, in that
checker's F3, and nowhere else. This paper's contribution is to assemble both,
verify them, corroborate the second on a seed-disjoint campaign, state the general
rule, and add the frozen re-analysis of §5 — not to discover them.

The definition of a centre as a *connected* component is a contested modelling
assumption: Hintze & Bohm (2026), *npj Complexity*, doi:10.1038/s44260-026-00074-2
(arXiv:2508.08047), give a closely related criterion that admits spatially
disjoint replicators. Every result above is conditional on the connected-component
definition. The programme **intended** to record per-step connectivity exposure so
that this could be re-tested without re-spending a campaign, but the artefact was
generated before the first admissible triple existed and carries zero records; the
assumption cannot in fact be re-tested without re-reading the raw archives.

## 10. Data and code availability

Three standard-library scripts ship with the recovery bundle: verification of the
recovered tree, independent recomputation of §3.4, and the frozen §5 analysis with
its capability test. The frozen method files pinned by
`METHODS_HASH = 21571fb4…d4d63c920a007e188bdc24e0d94d1f99` (17 files) recompute and
match; the seven published content hashes verify **at the byte level**, which is
not the same as verifying content — one of the seven is an empty record set.

**The 123 raw archives (~440 MB) are not included.** Recomputed here from committed
per-pair records: all of §3.4, all five rows of §4, the mortality contrast of
§3.1, and all of §5. Quoted from the verbatim checker return and **not**
recomputed: the occupancy figures of §3.2, the 33-pair mixes of §3.3, the frozen
design power of §6, and the individual reading of the six control `OUT_OF_RANGE`
cases in §2.

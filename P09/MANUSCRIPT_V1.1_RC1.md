# A conjugate saturation limit on forced material exchange, and a guard that harms by allocation but rescues only by dose

**Tommy Lepesteur**
Emergent Dynamics Lab · `Mythmaker28/emergent-dynamics-lab`
Draft **V1.1 / RC1** — 9 August 2026 — licensed CC BY 4.0
*(V0, the P07-only narrative, and V1, the P08 narrative, are archived unchanged as the record of
what was known before each audit. This version incorporates the P08 corrigendum and the P09
dose-yoked closure. The chronology of predictions, refutations and corrections is preserved.)*

---

## Abstract

A persistent, bounded, non-percolating component in a conservative lattice–bond substrate can be
forced to exchange its material with an external reservoir by an atomic coupled operator that
removes matter downstream and injects an equal mass upstream. We ask what sets the maximum rate
of that exchange, and whether any local, provenance-blind control policy can raise it.

The limit is not exhaustion. Across 4036 rejected events the component always held removable
matter, and it retained 97.5–98.4 % of the removable mass held by a paired unforced control. A
complete per-event ledger classifies every one of those rejections into a single category: the
region the actuator is allowed to touch still holds matter — a median of 24.2 units — but all of
it below the detector threshold. The limit is a **local sub-threshold inaccessibility inside a
fixed support**, and the operator manufactures it, because detector and actuator share the
threshold that defines the target: draining a cell past it deletes that cell from the component
and from eligibility in the same instant. Before that, and for most of the trajectory, the
binding constraint is on the other side: injection fills the upstream region to the ceiling in
about thirteen events, after which 87–97 % of executed events deliver exactly the free room the
substrate has reopened since the previous event.

That reopening rate, ρ, is a genuine physical quantity and not a curve fit. A saturation probe —
fork a clone, fill the injection region in one shot, then let the substrate run with no operator
— predicts the delivered rate over the *next* window of the same trajectory to a median ratio of
1.020 (CI [0.986, 1.059]), with all 46 source-bound comparisons inside a factor 1.5. The only
departures are the windows where the sink has taken over, which is what a source-side probe
should do. But ρ is **not constant**: it falls by a factor 3.1 to 4.7 over the first two
thousand steps, in every block, and the probe reproduces that decay without being told about it.
A constant-rate model wins 0 of 18 blocks against a finite-reservoir or power-law alternative on
held-out data. The effective law Φ(s) = min(q/s, ρ) therefore holds within the window in which ρ
is estimated, and not beyond it.

Two corrections were then tested causally, each varying exactly one axis. A per-cell safety
floor that forbids the sink from pushing a cell below the detector threshold does prevent
self-erasure — and **splits the component in 9 of 9 blocks at both sizes**, because it converts a
local excision into a global thinning of the removal band. A per-cell headroom cap that keeps
the injection region unsaturated lowers the delivered flux to 0.51–0.55 of the parent's, exactly
as the probe predicted before the experiment was read, because the substrate reopens room
fastest when there is none. An online trigger that waits for a productive moment fires 18 of 320
times, loses 0 of 9 blocks against the fixed schedule at both sizes, and is statistically
indistinguishable from its own firing pattern replayed open-loop on a *different* block
(p = 0.51 and 1.00) — so the online decisions carry no block-specific information. A deliberately
stale sensor costs less than one percent of the primary endpoint.

The endpoint used throughout is unique causal replacement, the minimum of incumbent removed and
never re-counted and fresh matter still retained at the horizon. It was validated adversarially
against the two operators previously shown to be degenerate before it was sealed, and it ranks
both of them last. Delivered mass is reported only as a diagnostic.

Confirmation on never-used seeds upheld the fragmentation and flux predictions and, per the
sealed rule, closed the feedback branch: both a strict and a sham-normalised transport of the
online policy to a second law failed. Inside that confirmation cohort the floor behaved
oppositely under the second law — it kept the component alive in 9 of 9 blocks where the
unguarded operator dissolved it in 9 of 9 — and that reversal replicated on a third never-used
cohort. It also, however, delivered only half the mass, so the observation confounded allocation
with dose.

A final dose-yoked experiment separated them. Both replay arms received an identical exogenous
sequence of requested quantities, taken from a complete event ledger of a different block of a
different seed cohort, at identical times on identical geometry; only the per-site allocation
rule differed. Under the first law the delivered masses matched inside a margin sealed in
advance (ratios 1.001 and 0.906) and the floor still **split the component in 9 of 9 blocks
against 0 of 9** (p < 0.0001 at both sizes): its harm is a genuine allocation effect. Under the
second law the equivalence **failed** (0.796 and 0.767, confidence intervals entirely below the
sealed band), so no allocation claim is admissible there — and the rescue was reproduced with **no
guard at all**: an unguarded operator delivering the same low mass evenly went from 1 of 9 to
**9 of 9** surviving blocks (p = 0.0004 at both sizes) with *higher* causal replacement than the
guarded arm. The apparent sign reversal was dose throttling.

We conclude that the coupling between the detector that defines a target and the actuator that
acts on it imposes a saturation that neither safe allocation nor local feedback lifts; that a
per-cell threshold guard is harmful by allocation where the component fails by fragmentation; and
that where the component fails by dissolution, what rescues it is **how much** is removed, not
**how** it is allocated. No claim of identity, individuation, autonomy, metabolism or organisation
is made or implied.

---

## 1. The question, stated so it can fail

For a coupled exchange operator acting on a bounded tracked component, what quantity — measured
at the level of the individual event — sets the maximum material that can be exchanged per unit
time, and can any policy that reads only pre-event local information raise it?

Three axes must be kept apart or a positive result is causally ambiguous: **when** the operator
acts, **how much** it applies, and **where** in space it is allowed to act. Every experiment
below varies exactly one.

## 2. System and operator

Periodic `L × L` lattice–bond engine, matter field `m ∈ [0, M_max]`, `M_max = 1`, `dt = 1`. A
detector labels as occupied every cell with `m ≥ THRESH = 0.45` and returns 4-connected
components; the tracked component is the largest bounded, non-wrapping one. At `t = 256` the
component `C₂₅₆` is frozen and split along an axis into a downstream removal mask and an
upstream injection mask. All matter is labelled by provenance into five mutually exclusive
cohorts whose sum is identically the matter field; the provenance is visible to the audit and
invisible to every selector and every policy, which is enforced by an AST scan, not by
convention.

Each scheduled event computes `q = min(q_planned, capacity_sink, capacity_source)` on one
pre-event state and then moves exactly `q` on both sides, or nothing at all. Removal from a cell
is proportional to each cohort's presence in it; injection writes only into the fresh cohort;
the bond and organisation fields are never touched by the operator.

The operator used here reproduces the sealed operator of the predecessor study **bit for bit**
on 216 frozen cases, so every result below attaches to the same physics rather than to a
reimplementation.

## 3. The limit is local sub-threshold inaccessibility, not exhaustion

Paired against a sham receiving the identical measurement schedule and no operator, at matched
times (medians over 9 independent blocks, `L = 24`):

| | sham | forced |
|---|---|---|
| eligible capacity of the actuator | 79.17 | 0.00 |
| fraction of the frozen mask still inside the component | **1.000** | **0.000** |
| removable matter in the whole component | 163.59 | 160.99 |

Exact sign test, 9/9 blocks, p = 0.0039. The reservoir the actuator cannot reach moves by 1.8 %.
Classifying all 4036 rejections:

| | count |
|---|---|
| global material exhaustion | 0 |
| allowed support empty of matter | 0 |
| **allowed support holds only sub-threshold matter** | **4036** |
| supra-threshold matter stranded outside the track | 0 |

with a median of 24.2 units of matter stranded below the threshold inside the mask. This
separates the four possibilities that a global statement conflates: the limit is local, it is a
threshold-accessibility limit inside a fixed support, and it is neither topological nor a
shortage of matter.

Before the actuator loses its grip, the other side binds: free room in the injection region
falls below 0.7 in about thirteen events, and thereafter 87 % (`L = 24`) and 97 % (`L = 32`) of
executed events realise exactly the source capacity. Three regimes follow in order —
unconstrained delivery, source-bound delivery, and, late and only at the smaller size, outright
rejection.

## 4. ρ is measurable on its own, and it is not a constant

**Probe.** At a checkpoint of an ordinary forced trajectory, fork a clone, fill every cell of
the injection region to `M_max` in one shot, then let the substrate run with **no operator** and
record how fast free room reopens. The initial slope is the reopening rate at zero headroom,
which is by construction the sustained rate a coupled operator that keeps the region saturated
can extract. The probe never sees a delivery curve.

**Result.** Against the delivered rate over the *next* window of the same trajectory:
median ratio 1.020, CI [0.986, 1.059], and 46 of 46 comparisons within a factor 1.5 in windows
where the source is the binding constraint. The 26 comparisons outside that stratum
over-predict, with the three largest deviations occurring in exactly the three blocks whose
source-bound fraction had fallen to 0.000 with 78–84 % rejection — a source-side probe failing
precisely where a sink-side constraint took over.

**Non-stationarity.** The probe's own estimate falls by a factor 3.11 (`L = 24`) and 4.71
(`L = 32`) between `t = 272` and `t = 2320`, 9/9 blocks, p = 0.0039, without being told to. On
held-out data — each model fitted on the first half of the forced phase and scored on the second
— a constant-rate model wins **0 of 18** blocks; a finite-reservoir model
(`C ≈ 28`/`49`, `τ = 128`, `r∞ ≈ 0.014–0.016`) and a power law (`D ∝ t^0.44` / `t^0.38`) win the
rest.

Consequently the effective relation Φ(s) = min(q/s, ρ) is confirmed **within the window in which
ρ is estimated** and is not a stationary law. This also bounds what any waiting policy can do:
the reopening rate is maximal at zero headroom and decays as headroom accumulates (late/early
slope ratio 0.761, CI [0.752, 0.767], n = 90), so a controller that waits operates where the
substrate reopens room more slowly.

## 5. The endpoint

Delivered mass is inflatable: an operator that injects into the very cells it drains delivers
6.4× more and replaces 4× less. The primary endpoint is therefore

```
UCR = min( incumbent removed by the sink and never re-counted ,
           fresh mass still inside the tracked component at the horizon ) / M₂₅₆
```

validated adversarially against the two known-degenerate operators **before** it was sealed: it
ranks them last (0.104 and 0.251 against 0.387 for the parent) and returns 0 for any arm whose
component is dead at the horizon. Replacement per unit time, per attempted mass and per
delivered mass, fresh retention, incumbent displacement and tracker sweep are reported
separately and never merged. The independent unit is the block; internal events and internal
policy decisions are never replicates. All analyses are intention to treat.

## 6. Safe actuation does not lift the limit — and one variant destroys individuation

Two numbers define an exact 2 × 2 factorial with **when** and **where** held identical: a floor
below which the sink may not leave a cell it drains, and a ceiling above which the source may not
fill a cell.

| | UCR (L24 / L32) | ITT continuity | delivered | futile share |
|---|---|---|---|---|
| parent (0.00, 1.00) | **0.387 / 0.333** | **9/9 · 9/9** | 0.620 / 0.414 | 0.190 / 0.034 |
| floor (0.50, 1.00) | 0.216 / 0.225 | **0/9 · 0/9** | 0.306 / 0.308 | 0.044 / 0.061 |
| ceiling (0.00, 0.90) | 0.236 / 0.180 | 9/9 · 9/9 | 0.314 / 0.228 | 0.017 / 0.001 |
| both | 0.227 / 0.196 | **0/9 · 0/9** | 0.351 / 0.265 | 0.097 / 0.037 |

The safety floor **splits** the component in 9 of 9 blocks at both sizes, at `t ≈ 976` and
`1280`. This is not dissolution — the component is alive at the horizon in all blocks — and it is
not a detector artefact: shadow readers at 0.50 and 0.55 also see a component, the fragment. The
mechanism is legible: taking only `m − 0.50` per cell thins a wide band instead of excising a few
cells cleanly, and a wide band at 0.50 breaks. Preventing self-erasure destroys individuation.

The headroom cap lowers the flux to 0.51 and 0.55 of the parent's, as the probe predicted before
the experiment was read. Neither guard raises replacement; both shift which side binds. Under the
floor, the sink-bound fraction rises from 0.078 to 0.917.

## 7. Local feedback carries no information a donor schedule does not

Holding the amount rule and the geometry fixed and matching the attempted mass by construction —
a skipped opportunity banks its quantum, capped, and the last opportunity flushes the bank — an
online trigger acts only when the state can absorb almost all of the intended bite and the
actuator still has contact with its target.

| | UCR (L24 / L32) | fires / 320 | delivered | vs fixed |
|---|---|---|---|---|
| fixed schedule | **0.387 / 0.333** | 264 / 320 | 0.620 / 0.414 | — |
| online trigger | 0.305 / 0.231 | **18 / 14** | 0.387 / 0.271 | 0/9, p = 0.0039 |
| donor-yoked replay | 0.310 / 0.234 | 18 / 14 | 0.400 / 0.272 | 0/9, p = 0.0039 |
| lagged sensor | 0.312 / 0.236 | 23 / 17 | 0.394 / 0.277 | 0/9, p = 0.0039 |

The decisive control is the third row: the online arm's own firing pattern, replayed open-loop on
a **different block**, reproduces its result (p = 0.51 and 1.00, median differences −0.0006 and
−0.00002). Whatever the trigger achieves is a property of the schedule it happens to generate,
not of the state it reads. A sensor deliberately made one opportunity stale costs under one
percent of the endpoint. Feedback does reduce futility, from 0.190 to 0.035 — and forgoes far
more exchange than the futility it saves.

The explanation is derivable before the experiment: under this law the open-loop schedule already
survives 9/9 and already extracts the entire physical rate at every opportunity, since 87–97 % of
its events are source-bound, that is, saturated. There is nothing for a timing policy to recover.

## 8. Guards against an oracle controller, and against detector rescue

Everything a policy reads passes through a single audited function: matter field, frozen
geometry, current detected track, and its own past decisions. Never provenance, the future, the
terminal outcome, the seed, cohort membership or future tracker survival.

Because a per-cell floor at `THRESH + ε` could keep cells alive for the *detector* rather than the
object, shadow readers at 0.40 / 0.45 / 0.50 / 0.55 / 0.60 and the distribution of `m − THRESH`
are recorded throughout. The official tracker stays frozen at 0.45 and is the only one used for
endpoints; the shadow readers can invalidate a survival, never create one. No arm survives at
0.45 while failing at 0.55.

The spatial branch — a support that follows matter — was **not opened**. Its pre-declared
condition required the ceiling to persist despite safe allocation. Safe allocation does not hold
the ceiling; it lowers it. Opening the branch would have been a search for a favourable setting.

## 9. Confirmation, transport, and the dose-yoked closure

**Confirmation (never-used seeds).** Of four sealed point predictions, two held and two failed as
stated. The floor splits the component in 9 of 9 blocks at both sizes while the unguarded
operator splits none (predicted >= 7 and <= 1). The headroom cap delivers 0.538 and 0.535 of the
unguarded flux (predicted band 0.35-0.75). The prediction that no guard improves replacement
failed its significance threshold at the smaller size, not its direction: the unguarded operator
itself lost the component in 2 of 9 blocks of the fresh cohort, leaving a 2/7 sign test at
p = 0.18 despite a median advantage of 0.16. The prediction that the source-side probe transports
to the second law failed for the reason the probe's own stratification predicts: there the
component dies early, only 65 and 116 of 320 events execute, and a source-side probe over-predicts
wherever a sink-side constraint has taken over.

**Transport of the feedback policy.** Strict and sham-normalised transport both reproduce the
unguarded operator exactly (0/9 and 3/9 continuity, zero causal replacement). Per the sealed
adjudication this is a confirmed generalisation limit, and no third tuned variant was created.

**The apparent reversal, and why it needed one more experiment.** Under the second law the guard
kept the component alive in 9 of 9 blocks at both sizes while the unguarded operator dissolved it
in 9 of 9, and this replicated on a third never-used cohort against three sealed predictions. But
the guard also delivered roughly half the mass. Survival, allocation and dose were confounded, and
no dose-matched contrast existed anywhere in the earlier artefacts: the closest unguarded low-dose
arm delivered 1.49x and 1.92x the guard's mass with no overlap of block-level ranges.

**The dose-yoked design.** Six arms on nine fresh blocks per cell, both laws, both sizes, 216
trajectories. Two replay arms received an identical exogenous sequence of requested quantities —
taken from a complete 320-of-320 event ledger of a *different* block of a *different* seed cohort,
cyclically mapped, scaled by initial mass, sealed by hash before execution — at identical times on
identical geometry, differing only in the per-site allocation rule. A third arm delivered the same
total, in the same number of events, spread as evenly as possible, with no guard.

| | delivered ratio guard / unguarded | sealed margin | verdict |
|---|---|---|---|
| first law, L = 24 · 32 | 1.001 · 0.906 | median in [0.847, 1.180] | **pass** |
| second law, L = 24 · 32 | 0.796 · 0.767 | CI in [0.781, 1.280] | **fail** |

| second law | survival ITT | unique causal replacement | delivered |
|---|---|---|---|
| sham | 9/9 · 9/9 | 0.000 | 0.000 |
| unguarded, full dose | **1/9 · 1/9** (8 dissolutions each) | **0.000** | 0.465 · 0.521 |
| **unguarded, same low dose, even** | **9/9 · 9/9** | **0.128 · 0.175** | 0.208 · 0.238 |
| unguarded, replayed sequence | 6/9 · 9/9 | 0.147 · 0.200 | 0.306 · 0.308 |
| guarded, replayed sequence | 9/9 · 9/9 | 0.117 · 0.153 | 0.231 · 0.244 |
| guarded, full dose | 9/9 · 9/9 | 0.117 · 0.157 | 0.231 · 0.252 |

Under the first law, at verified dose equivalence, the allocation rule alone destroys the
component: same sequence, same times, same support, **9 of 9 splits against 0 of 9**, p < 0.0001
at both sizes. That is a clean allocation effect.

Under the second law the equivalence fails — even asked for exactly the same thing the guard
cannot deliver it, staying 20 to 23 per cent below with confidence intervals entirely under the
sealed band — so by the sealed rule no allocation claim is admissible. And the positive evidence
runs the other way: an operator with **no guard at all**, delivering the same low total evenly,
goes from 1 of 9 to 9 of 9 surviving blocks (p = 0.0004 at both sizes) and achieves *more* causal
replacement than the guarded arm (0.128 against 0.117; 0.175 against 0.157). The guard adds
nothing detectable there (+3/9 at the smaller size, p = 0.21; 0/9 at the larger), and at the
larger size it *costs* replacement at identical requests (-0.052, p = 0.004). The temporal profile
has no significant effect on survival anywhere (p = 0.21 and 1.00).

**What is therefore withdrawn.** The statement that the guard's sign reverses with the failure
mode does not survive. The guard does not change sign: it is harmful by allocation where the
component fails by fragmentation, and inert once dose is controlled where the component fails by
dissolution. What changes with the regime is the system's **sensitivity to dose**: dividing the
dose by thirteen leaves survival untouched under the first law (9/9 to 9/9) and is the entire
rescue under the second (1/9 to 9/9).

## 10. Discussion

Two statements survive as the substance of this work.

First, the ceiling on forced material exchange in this system is created by the operator and is
conjugate: exchange requires simultaneously matter above threshold where removal acts and room
below the ceiling where injection acts, and acting drives those two regions to opposite
saturation extremes. The rate at which either reopens is measurable on its own, it decays, and no
policy tested here changes it.

Second, and more transferable: an actuator that shares a threshold with the detector defining its
target will delete its own target, and the obvious repair — refusing to cross the threshold —
makes things worse where the object fails by fragmentation, because it converts a local excision
into a global thinning. Where the object fails by dissolution the repair looks protective, but a
dose-yoked test shows that the protection is bought by delivering less, not by allocating
differently: an unguarded operator at the same low dose does at least as well and replaces more.

The methodological point is the one we would defend hardest. A policy that changes *what* it does
per site almost always changes *how much* it delivers, and the two are separable only by an
exogenous, hash-sealed, yoked quantity sequence with an equivalence margin fixed in advance. We
built that instrument, it passed under one law and failed under the other, and the failure is what
kept a plausible topological story from being published as one. An apparently structural policy
whose benefit is really throttling is, we suspect, a common failure mode in this kind of work.

## 11. What is not claimed

No organisational observable exists in this project and none was invented. The connected incumbent
residue is not called a scaffold: no functional intervention has tested it. The independent unit
is the block. ρ is measured on the source side only and predicts nothing once the sink throttles.
One substrate, one occupancy, one family of initial conditions, two laws, two to three sizes. The
failure mode was never manipulated, only observed, so no causal claim about it is made. Under the
second law the guard's own contribution is not identifiable at all, because its dose could not be
matched.
Identity, individuation, autonomous renewal, metabolism and life remain untested and unclaimed.

## 12. Data, code and reproducibility

Sealed protocols with their SHA-256 seals, all operator, harness and analysis code, complete
per-event ledgers, fixtures, an independent engine-free verification pass, the rival-model
comparison, the probe curves and the figure scripts are archived with `SHA256SUMS` manifests.
Mission identifiers, exhaustive hashes and repository plumbing are given in the supplement; the
main text carries only the scientific chronology of predictions, refutations and corrections.
The production engine, detector and passive tracer were used unmodified and are verified
unchanged by hash. No parent artefact was modified.

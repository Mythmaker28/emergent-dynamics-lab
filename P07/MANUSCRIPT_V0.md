# A conjugate saturation limit on forced material exchange in a bounded lattice component

**Tommy Lepesteur**
Emergent Dynamics Lab · `Mythmaker28/emergent-dynamics-lab`
Draft V0 — 9 August 2026 — licensed CC BY 4.0

---

## Abstract

A persistent, bounded, non-percolating component in a conservative lattice–bond substrate can
be forced to exchange its material with an external reservoir by a coupled operator that
removes matter downstream and injects an equal mass upstream, atomically. We ask what sets the
maximum throughput of that exchange. Using a complete per-event ledger and a zero-perturbation
capacity spectrum, we show that the limit is **not** exhaustion of the component: at every one
of 4036 rejected events the component still held removable matter, and across the whole forced
trajectory it retained 97.5–98.4 % of the removable mass held by a paired unforced control. The
limit is a **conjugate saturation** created by the operator itself. Injection fills the upstream
region to the ceiling `m = M_max` within ~13 events; removal empties downstream cells below the
detector threshold `THRESH`, which simultaneously deletes them from the component and from the
actuator's eligible set. Because detector and actuator share that threshold, the operator
destroys its own reach. Relaxing either side is not sufficient: a systematic sweep of six
conservative, provenance-blind operator families shows that widening the removal region leaves
throughput unchanged (the removal side was not binding), while widening the injection region
transfers the binding constraint to the removal side and destroys the component in 5 to 8 of 9
blocks. Delivered throughput and material replacement are, moreover, anti-correlated: an
operator that injects into the very cells it drains delivers 6.4× more mass and achieves 4×
less incumbent replacement, a futile cycle that inflates any endpoint defined on delivered mass.
Throughput obeys a saturation law, `Φ(s) = min(q/s, ρ)`, in which the planned dose is almost
irrelevant: over a 64-fold change in cadence the delivered flux varies by 12–30 % while the
delivered *fraction* varies by a factor 53. The law was sealed with point predictions and
confirmed prospectively on nine never-used seeds per size at four held-out cadences, with a
worst error of 8.8 % against a pre-declared tolerance of 35 %, including the predicted
dose-limited break-point. The magnitude of achievable exchange is bounded in
[0.25, 0.60] `M₂₅₆` across three sizes and two laws, but neither the identity of the binding
constraint nor the survival of the regime generalises to the second law, where the same forcing
dissolves the component in 8 of 9 blocks while the unforced control survives 9 of 9. No claim
of identity, individuation, autonomy, metabolism or organisation is made or implied.

---

## 1. Question

Prior work in this project established that a tracked component can survive forced material
turnover, and that increasing the planned dose eightfold multiplies the removed mass by only
2.3–3.0. The mechanism behind that sublinearity was attributed to exhaustion of the sink's
eligible set. This paper tests that attribution and replaces it.

The question is stated operationally: for a coupled exchange operator acting on a bounded
tracked component, **what quantity, measured at the level of the individual event, sets the
maximum mass that can be exchanged per unit time?**

## 2. System, operator, and what makes the limit non-obvious

The substrate is a periodic `L × L` lattice–bond engine with matter field `m ∈ [0, M_max]`,
`M_max = 1`, `dt = 1`. A detector labels as *occupied* every cell with `m ≥ THRESH = 0.45` and
returns 4-connected components; the tracked component `C_t` is the largest bounded,
non-wrapping one. At `t = 256` we freeze `C₂₅₆`, split it along an axis into a downstream
removal mask and an upstream injection mask, and label all matter by provenance into five
mutually exclusive cohorts whose sum is identically the matter field.

Each scheduled event computes, on one pre-event state,

```
q = min( q_planned , capacity_sink , capacity_source )
```

and then moves exactly `q` on both sides or nothing at all. Removal from a cell is proportional
to each cohort's presence in that cell; injection writes only into the `FRESH` cohort; the
bond and organisation fields are never touched.

The limit is non-obvious because three different quantities can bind `q`, and the operator
changes all three by acting.

## 3. A structural fact that removes one candidate before any experiment

The parent's sink eligibility predicate is `i ∈ MASK ∧ i ∈ TRACK ∧ m[i] ≥ THRESH`. Since the
detector builds every component from `m ≥ THRESH`, the third conjunct is implied by the second.
It is dead code. Empirically, across 5308 tracked cells on 18 frozen states, `min m = 0.450457`.

Consequently "the sink is starved by the 0.45 threshold" is not a hypothesis but a restatement
of the track gate, and any experiment relaxing that threshold alone is a null manipulation. We
therefore reparameterise the operator by three genuinely independent gates — mask (frozen /
co-moving / whole track), track membership, threshold — plus a spread rule and a locality
ladder for the injection site.

The `PARENT` setting of this parameterisation reproduces the sealed parent operator bit for bit:
216 frozen cases (2 sizes × 3 seeds × 3 times × 4 axes × 3 quanta) give `max|Δm| = 0.0` and
`max|Δ cohort| = 0.0`.

## 4. Methods

Four phases, each sealed by SHA-256 over its protocol and its code before its first engine call,
with a guard that refuses to run on any mismatch:

| phase | design | independent units |
|---|---|---|
| 07A | observational; complete per-event ledger, per-step sweep accounting, zero-perturbation capacity spectrum | 9 blocks × 2 sizes |
| 07B | interventional; six operator families, one gate at a time, matched dose and matched `t₂₅₆` state | 9 blocks × 2 sizes |
| 07C | cadence sweep at four spacings, two injection geometries (discovery) | 9 blocks × 2 sizes |
| 07D | confirmatory; nine never-used seeds per size, a third size, a second law, four held-out cadences, four sealed point predictions | 9 blocks × 5 configurations |

A **block** is one `(size, seed)` lineage and is the only independent unit. The thousands of
events inside a trajectory are never treated as replicates. All analyses are intention to treat:
the nine blocks of a cell remain in every table, including after the track is lost, and
survivor-conditional quantities are labelled as such. Every non-executed event carries a named
cause; the taxonomy is reported in full (24 518 rejections, 24 518 named).

## 5. Results

### 5.1 The component is never exhausted

Paired against a sham that receives the identical measurement schedule and no operator, at
matched times, medians over 9 blocks (L = 24):

| | sham | forced Q400 | forced Q800 |
|---|---|---|---|
| eligible sink capacity `CAP_PARENT` | 79.17 | 8.10 | 0.00 |
| mask registration `|mask ∩ C_t| / |mask|` | **1.000** | 0.105 | **0.000** |
| removable matter in the **whole** component | 163.59 | 159.51 | 160.99 |

Exact sign test, 9/9 blocks in the same direction, p = 0.0039, for capacity and registration;
the whole-component reservoir moves by 1.8 %. At **100 %** of 4036 rejected events, removable
matter existed inside the component while the actuator's capacity was exactly zero.

The frozen mask remains fully registered when nothing is done to it and fully de-registers
under forcing. Since the shortfall between "eligible inside the track" and "eligible anywhere in
the mask" is zero, the mask cells did not detach while full: they were emptied below `THRESH`,
which removes them from the component and from eligibility at the same instant.

### 5.2 Before that, the injection region saturates

Event by event, the active bound in `q = min(planned, sink, source)`:

| executed events, Q400 | dose-bound | **source-bound** | sink-bound |
|---|---|---|---|
| L = 24 | 117 (5.2 %) | **1968 (87.0 %)** | 176 (7.8 %) |
| L = 32 | 98 (3.4 %) | **2782 (96.6 %)** | 0 |

Free room `Σ(M_max − m)` in the upstream mask starts at 23.2 (L = 24) and falls below 0.7 in
about 13 events. Thereafter `q` equals the source capacity exactly, and throughput is whatever
the dynamics reopen upstream between two events. Three regimes follow in order: unconstrained
delivery, source-bound delivery, and — late, at L = 24 only — outright rejection.

### 5.3 Relaxing one side moves the constraint to the other

Six families at matched dose and matched initial state (medians of 9 blocks, L = 24 / L = 32;
masses in units of `M₂₅₆`):

| family | delivered | incumbent removed | efficiency | ITT continuity |
|---|---|---|---|---|
| parent | 0.620 / 0.414 | 0.460 / 0.377 | 0.744 / 0.910 | **9/9 · 9/9** |
| track gate removed | 0.620 / 0.414 | 0.460 / 0.377 | 0.744 / 0.910 | 9/9 · 9/9 |
| co-moving mask | 0.744 / 0.413 | 0.478 / 0.375 | 0.643 / 0.910 | 8/9 · 9/9 |
| quota spread over all eligible cells | 0.455 / 0.455 | 0.366 / 0.349 | 0.804 / 0.768 | **0/9 · 0/9** |
| injection dispersed over the track | 0.516 / 0.510 | 0.448 / 0.463 | 0.895 / 0.914 | 1/9 · 4/9 |
| removal from the whole track | 3.865 / 3.835 | 0.298 / 0.261 | 0.075 / 0.067 | 8/9 · 8/9 |
| injection into the drained cells | 4.000 / 4.000 | 0.114 / 0.100 | 0.029 / 0.025 | 9/9 · 9/9 |

Removing the track gate is bit-identical to the parent on 15 of 18 blocks; the three exceptions
correspond to 3 events out of 5760 in which matter above threshold detached from the component.
A co-moving mask, which the pre-registered decision rule had selected as the primary contrast,
gives +20 % at L = 24 with one block lost and **exactly nothing** at L = 32. Dispersing the
injection abolishes the source constraint (source-bound fraction 0.000 / 0.062) and immediately
raises `NO_SINK_CAPACITY` rejections to 2123 and 2205, while destroying the component in 8 and
5 of 9 blocks. No family raises the exchange while preserving the component.

### 5.4 Delivered throughput is not exchange

The two families that appear to break the ceiling do so by recycling. Injecting into the very
cells just drained delivers 100.0 % of the planned dose with 9/9 continuity — and removes
0.114 / 0.100 of incumbent instead of the parent's 0.460 / 0.377, an efficiency of 0.029 / 0.025
against 0.744 / 0.910. **6.4× more delivered mass, 4× less material replaced.** This was
predicted in advance for the confirmation phase and held at all five configurations there, with
efficiency ratios of 16 to 47.

We report this as a methodological result: an endpoint defined on delivered mass is inflatable
by a futile cycle, and our own pre-registered primary endpoint was inflated by exactly that.
The verdict produced by the sealed rule is reported unchanged; the corrected endpoint —
incumbent removed per unit delivered — was declared before the confirmation phase and used only
there.

### 5.5 The saturation law

Fixed 2048-step window, cadence varied 64-fold:

| Φ, delivered mass per step | s = 1 | s = 4 | s = 16 | s = 64 | ratio |
|---|---|---|---|---|---|
| interface injection, L = 24 | 0.0301 | 0.0297 | 0.0284 | 0.0248 | **1.21** |
| interface injection, L = 32 | 0.0407 | 0.0405 | 0.0397 | 0.0364 | **1.12** |
| fraction of the *planned* dose delivered, L = 24 | 0.014 | 0.056 | 0.216 | 0.756 | ×53 |

```
Φ(s) = min( q/s , ρ )
```

`q` is chosen by the experimenter; `ρ` is a property of the substrate and of the injection
region. The predicted break-point `s* = q/ρ` is 69.5 (L = 24) and 91.7 (L = 32), and Φ first
departs from the plateau at `s = 64`, as predicted.

### 5.6 Prospective confirmation

`ρ` was estimated from `s ∈ {1, 4, 16}` on the discovery seeds; the spacings 2, 8, 32 and 128
were held out; the predictions were sealed; the confirmation used nine seeds per size never used
in any mission of this project.

| observed / predicted | s = 2 | s = 8 | s = 32 | s = 128 |
|---|---|---|---|---|
| L = 24 | 1.017 | 0.984 | 0.912 | **1.004** |
| L = 32 | 0.978 | 0.969 | 0.932 | **0.994** |

Pre-declared tolerance: a factor 1.35. Worst observed error: 8.8 %. The dose-limited break at
`s = 128`, predicted quantitatively from `s*`, is recovered to 0.4 % and 0.6 %.

### 5.7 What generalises, and what does not

Achievable exchange stays inside the sealed band [0.25, 0.60] `M₂₅₆` at all three sizes and both
laws (0.455, 0.373, 0.313; 0.425, 0.438), so the *magnitude* generalises — but it declines
monotonically with size, so size-invariance is refuted. The *identity* of the binding constraint
does not generalise: source-bound fractions are 0.877 / 0.966 / 0.969 under the first law and
0.296 / 0.493 under the second, refuting that sealed prediction as stated.

Most consequentially, the *regime* does not generalise. Under the second law the unforced
control survives 9/9 at both sizes while the same forcing dissolves the component in 9/9 and
8/9 blocks, at t = 2288–4640 and 4640–5792. One property accounts for both failures: the second
law redistributes matter faster intrinsically (its sham ends at `I/I₀` = 0.467 / 0.584 against
0.751–0.848), which desaturates the injection region — hence fewer source-bound events — and
simultaneously shortens the margin to dissolution.

### 5.8 Separating physical replacement from tracker motion

Prior work could not distinguish material crossing the component boundary from the tracker
sweeping over stationary matter. Per-step accounting of
`ΔT = Δ(retained sites) + (mask entry) + (mask exit)` closes exactly on 47 of 47 gap-free
trajectories, worst residual 6.8 × 10⁻¹³. Under forcing the tracker sweeps ≈ 2 `M₂₅₆` gross for
a net of only −0.13, while in the fixed frame the original region loses incumbent (0.67 → 0.33)
and gains fresh material (0 → 0.25). Both effects are real and are now measured separately;
neither is inferred from the other.

## 6. Discussion

The maximum exchange throughput of this operator class is set by a constraint the operator
creates. Exchange requires simultaneously matter above threshold where removal acts and room
below the ceiling where injection acts, and the act of exchanging drives those two regions to
opposite saturation extremes. Because the substrate reopens both at a finite rate, throughput
saturates at that rate and the planned dose becomes almost irrelevant — the observable signature
being a flux that is flat in cadence while the delivered *fraction* varies fifty-fold.

Two consequences are worth isolating. First, an actuator that shares a threshold with the
detector that defines its target will delete its own target; the coupling between measurement
and intervention is not an implementation detail but the limiting mechanism. Second, throughput
and exchange must be measured separately, because the operators that maximise the first are
precisely those that recycle rather than replace.

## 7. What is not claimed

No organisational observable exists in this project and none was invented here. The connected
incumbent residue is not called a scaffold: no functional intervention has tested it. The
independent unit is the block; the thousands of events inside a trajectory are never replicates.
`ρ` is measured over a 2048-step window and declines by roughly a factor 2 over 5104 steps; the
law is established only for `s ∈ [1, 128]`, one substrate, `p = 0.35`, and the geometries tested.
Three sizes do not establish a scaling exponent, and none is claimed. Identity, individuation,
autonomous renewal, metabolism and life remain untested and unclaimed.

## 8. Data, code and reproducibility

Four sealed protocols with their SHA-256 seals, all operator and harness code, the complete
per-event ledgers (62 450 instrumented events), per-step traces, fixtures (14/14), an
independent engine-free verification pass (12/12) and the figure scripts are archived with a
`SHA256SUMS.txt` manifest. Engine invocations: 72 (07A) + 126 (impulse) + 108 (07B) + 162 (07C)
+ 252 (07D) = 720, plus 18 fixture state generators. The production engine, detector and passive
tracer were used unmodified and are verified unchanged by hash. No parent artefact was modified;
the 28 sealed files of the parent mission verify byte-identical.

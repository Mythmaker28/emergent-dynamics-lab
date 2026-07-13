# STRATEGIC SYNTHESIS — does R8-B-dynamic require a minimal causal model?

**No new code. No modification of any retired observer. This document decides nothing; it states what each route
would logically authorize, and stops for review.**

---

## 1. What R8-B actually asks

> **R8-B predictive identity** — a frozen classifier / nearest-neighbour rule fitted on **early** states only must
> re-identify the same entity **later**, and on held-out trajectories, **despite constituent turnover**. Position,
> total mass, absolute orientation and tracker ID are **forbidden** identity features.

It failed on the droplets (D-046 era) at **0.286 against a bar of chance + 0.25 = 0.333**, chance 0.083 — a real
signal (3.4× chance) that missed. The diagnosis was one number appearing twice: **within-entity drift 0.394,
between-entity distance 0.836.** An entity wandered nearly half as far from *itself* over time as it sat from its
neighbours. Identity existed and **did not hold still**.

**R8-B is a matching problem.** It needs a feature map `F` with exactly two properties:

- **STABILITY** — `F(e, early) ≈ F(e, late)` under constituent turnover, coarsening, retiming and drift.
- **DISCRIMINATIVENESS** — `F(e) ≠ F(e′)` for genuinely different entities.

It does **not** ask for a model. It asks for a *feature*.

## 2. The logical answer

**Minimality is a property of a DESCRIPTION, not of the WORLD.**

Two descriptions that are observationally equivalent on the reachable manifold make **identical predictions**. The
D-069 failure is exactly this: `xor3` was described with a redundant clock lag; the table was right on every row;
only the *class label* was wrong. A fingerprint built from **measured intervention responses** — predictions — is
by construction invariant to that error. A fingerprint built from **model-class labels, lag sets, feature counts or
arities** — descriptions — inherits it directly, and would report a **false DIFFERENCE** between two identical
entities merely because one was described with one lag too many.

> **R8-B-dynamic does not logically require a provably minimal causal model — provided the fingerprint is a
> function of measured causal RESPONSES and contains no description-level quantity whatsoever.**

Four conditions make that provision binding, and all four are load-bearing:

**(C1) Response-only.** The fingerprint may contain: measured intervention→response relations on a standardized
battery; the count and identity of independently manipulable causal sources; the binary behavioural fact of
history-dependence; the coverage achieved. It may **not** contain: transducer class, lag sets, history length,
feature arity, table shape, region cell-count, or any minimality claim.

**(C2) Frozen, standardized battery — the planner must be switched OFF.** This is the subtle one. G6's active
planner is *prospectively qualified*, and it is nonetheless **forbidden inside the fingerprint**: it chooses a
different intervention sequence for each world, which is precisely what makes it efficient — and precisely what
would make two entities' fingerprints **incomparable**. A fingerprint is a coordinate system; a coordinate system
that adapts to the thing it measures is not one. The planner's legitimate role is to **design the battery once, on
ground truth**, and then be frozen out of the measurement.

**(C3) Timed and untimed reported separately, never composited.** Coarsening and drift change internal delays.
If timing enters the fingerprint scalar, drift manufactures **false difference**. The untimed response relation is
the primary; the timed component is reported alongside and never summed into it.

**(C4) SAME is never claimed — only INDISTINGUISHABLE-UNDER-REPERTOIRE.** Where the battery cannot generate the
separating condition, two genuinely different entities collapse. This is not a defect to be engineered away; it is
`lag8_and` vs `lag8_or`, and the qualified behaviour is `EQUIVALENCE_CLASS_ONLY`. The fingerprint must carry its
own coverage, and a match below a preregistered coverage floor is an **abstention**, not an identity.

## 3. The two routes

### Route A — remain blocked until a bidirectional grow-and-prune observer exists

**Authorizes, eventually:** *"entities e and e′ have the same **minimal** causal structure"* — a strong,
description-level identity claim, and the only route to the full A/S/F/L/M hierarchy on this substrate.

**Costs and risks.** A fourth observer, under the same one-shot rule, at the same failure risk — and three
generations have now died of defects that each looked like a one-line fix *after* the prospective run. More
seriously: **it builds a capability the use case does not require.** R8-B does not ask for a minimal model. Route A
is scope creep driven by the benchmark rather than by the question, and I should name it as such rather than
dress it up as rigour.

**Route A remains mandatory** for any claim of the form *"this is the same individual"*, *"the causal architecture
is identified"*, or any GATE-0 / law-map authorization. Nothing below weakens that.

### Route B — a narrow prospective qualification of the frozen causal-response layer

**Uses only capabilities that are prospectively QUALIFIED (G6):** causal source discovery (100 %), temporal
provenance (0 fabricated / 0 excluded, no degradation to lag 56), reachable-manifold function (100 % vs privileged
simulation), hidden-state detection (6/6, and nowhere else), calibrated abstention on partial manifolds. Model
class and minimality are **excluded completely**, per C1.

**Authorizes, if and only if it qualifies:**

> *"Under frozen intervention repertoire **R**, with coverage **c**, entity e's causal-response fingerprint at late
> times matches its own early fingerprint more closely than it matches other entities' fingerprints, at rate X
> against chance Y."*

**Does NOT authorize:** "the same individual"; "the causal model is identified"; anything about behaviour the
battery cannot generate; any architecture, class or minimality claim; any GATE-0 or law-map step; any change to
β, `D_int` or the droplet equations.

## 4. Risks, named before they can be excused

**FALSE SAMENESS — the dominant risk, and it is structural.** The droplet's admissible intervention repertoire is
*far poorer* than the Boolean network's: you cannot clamp an arbitrary cell of a reaction–diffusion field. A poor
repertoire generates a small reachable manifold; on a small manifold, genuinely different entities collapse into
one fingerprint; and the collapse would present itself as **"identity persists"** — the exact answer the programme
has an interest in seeing. This is the failure mode most likely to fool me, and it is the reason for the hard gate
in §6.

**FALSE DIFFERENCE — two independent generators.** (i) *Description-level*: the D-069 redundant-lag defect, if any
class or lag quantity leaked into the fingerprint — removed by C1, and the removal must be **demonstrated** to be
load-bearing (§5, F6). (ii) *Timing drift*: coarsening changes internal delays — contained by C3, never eliminated.

**AND THE HONEST POSSIBILITY.** A causal-response fingerprint may simply **confirm** the R8-B failure: if turnover
changes the entity's causal *function* and not merely its *implementation*, then the fingerprint correctly reports
DIFFERENT, and identity genuinely does not persist in this substrate. Route B must be run as a test that **can
fail**, and a failure would be a *stronger* negative than the original phenotype-based one — worth publishing on
its own.

There is one substantive reason to think it might not fail, and it is a *qualified* result rather than a hope:
**implementation-independence of the measured function is exactly what G6 demonstrated prospectively.** Five
microscopically distinct machines (`direct`, `demorgan`, `nand2`, `xor_or`, `dup_same`) returned one macro
function. That is the ground-truth analogue of *the material is replaced and the function is preserved* — which is
the precise thing R8-B's phenotype prototypes could not see.

## 5. EXP-GT-FINGERPRINT-00 — specified, **not executed**

A **new prospective claim**, not a re-scoring of the failed hierarchy benchmark. Fresh worlds, fresh split, frozen
before the run, run once.

**The object under test:** a fingerprint map `F(entity) → vector`, built only from C1-admissible quantities, using
the frozen G6 measurement layer with the planner switched off (C2).

**Must be INVARIANT (a false DIFFERENCE here is a failure):**

| F1 | redundant lags — the `xor3` structure, the exact D-069 defect |
| F2 | retiming — `extra_delay`, `reg_delay` (a latch in the delay path), unequal source delays |
| F3 | microscopically different implementations of one macro function — `direct` / `demorgan` / `nand2` / `xor_or` / `dup_same` / `and_or` |
| F4 | topology, layout, clock phase, **channel distance** (lag 17 → 56, the D-067 axis) |
| F5 | **progressive implementation replacement mid-trajectory** — the Ship-of-Theseus arm. A world whose gate implementation is swapped **during** the run, function preserved. The fingerprint measured on the early window must match the fingerprint measured on the late window. *This is the direct structural analogue of R8-B's early/late split under constituent turnover, and it is the case the whole benchmark exists for.* |

**Must be DISCRIMINATIVE (a false SAMENESS here is a failure):**

| F6 | genuinely different functions — AND vs OR vs XOR, at identical topology and timing |
| F7 | different source counts — `and3` / `sync3` (3 causes) vs `direct` (2) |
| F8 | true hidden state — `toggle` / `fsm_gate` vs any combinational module |
| F9 | context-gated paths — a path that exists only under a discovered context |

**Must ABSTAIN (a confident verdict here is a failure):**

| F10 | the off-manifold twins — `lag8_and` vs `lag8_or`, identical on everything the repertoire can generate. Required verdict: **INDISTINGUISHABLE-UNDER-REPERTOIRE**, never SAME, never DIFFERENT. |

**Must DEMONSTRATE THAT THE EXCLUSION IS LOAD-BEARING (the must-fail case):**

| F11 | a **deliberately contaminated** fingerprint that *includes* the model-class label and lag set must be shown to produce a **false DIFFERENCE on F1** — i.e. to fail exactly where the clean fingerprint holds. If the contaminated variant passes too, then C1 is decoration and the benchmark has proved nothing. |

**Preregistered bars, frozen before the run:** zero false SAME on F6–F9 · zero false DIFFERENT on F1–F5 · correct
abstention on F10 · F11 fires · and a **separation margin declared in advance**: median between-function distance
must exceed median within-function distance (across implementations, retiming and replacement) by a factor fixed
before any data is seen. **The margin does not move after the run.**

## 6. The hard gate — REPERTOIRE-LIMITED TRANSFER

**This is the condition on which everything turns, and it is the one I would most like to skip.**

EXP-GT-FINGERPRINT-00 as specified runs in a substrate with *rich* intervention access — arbitrary cell clamps and
pulses. **The droplet has nothing of the kind.** A qualification obtained under rich access says nothing about a
substrate with poor access, and transferring it anyway would be the same category of error as every retirement in
this programme: a result established under one set of conditions, quoted under another.

**Therefore the benchmark must contain a REPERTOIRE-LIMITED ARM**: the same worlds, with the intervention set
deliberately crippled to a droplet-like repertoire (a small number of coarse, non-destructive, spatially
non-specific perturbations; no arbitrary internal clamps). The fingerprint must qualify **in that arm** — on
F1–F11, with its own coverage honestly reported and its own abstention rate.

- **If it qualifies only under rich access → transfer is NOT authorized.** Continued blocking. End of route.
- **If it qualifies under the limited repertoire → and only then → SC-PILOT may be defined.**

## 7. SC-PILOT-CAUSAL-FINGERPRINT — conditional definition

**Runs only if §5 and §6 both qualify. Explicitly EXPLORATORY. Its result could not be called proof of identity.**

**Unchanged and untouched:** β = 0.10 · `D_int` · every droplet equation · every R8 gate definition. **No parameter
that a failure would point to may be moved.** (`D_int` is precisely such a parameter, and the refusal to touch it
after R8-B failed is a standing decision of this project.)

**What it would do.** For each entity, measure a causal-response fingerprint from a **frozen, preregistered
battery** of admissible non-destructive probes, on an **early** window and a **late** window, with full temporal
provenance (every feature's source history re-read and verified). Then run the **R8-B matching statistic
unchanged** — prototypes fitted on early states only, re-identifying entities in the late half — on the fingerprint
feature space instead of the phenotype feature space. Bar declared in advance, in the same form as R8-B
(chance + 0.25). Position, mass, orientation and tracker ID remain forbidden.

**Mandatory controls, without which no number may be read:** a **positive control** (two synthetic entities built
to be genuinely different must separate) · a **negative control** (a scrambled / permuted entity must not
re-identify) · a **coverage floor** below which SAME is unclaimable · and the **repertoire coverage** reported
alongside every verdict.

**What its two outcomes would authorize — exactly:**

- **PASS** → *"In this substrate at β = 0.10, a causal-response fingerprint is predictive of entity identity across
  an early/late split at rate X vs chance Y, under repertoire R at coverage c."* **Exploratory.** Not proof of
  identity. **Not** a GATE-0 authorization. Not a law-map step. It would license one thing only: a preregistered
  follow-on with an independent substrate.
- **FAIL** → identity does not persist in this substrate **even under causal-response features**, which is a
  strictly stronger negative than the phenotype-based R8-B failure and closes the question properly.

## 8. Recommendation

**R8-B-dynamic does not logically require a provably minimal causal model.** Minimality is a description-level
property; R8-B is a response-level matching problem; the two are separable, and the separation is exactly what the
D-069 post-mortem established. **Route A is therefore not logically compelled by this use case** — though it
remains mandatory for any claim of architecture, minimal structure, or "the same individual".

**Route B is legitimate — conditional on §6, and on nothing less.** The capabilities it needs are prospectively
qualified; the capability that failed is excludable by construction; and the exclusion's load-bearingness is itself
made testable (F11).

**I am not recommending Route B in order to resume droplet experiments,** and the shape of the recommendation is
deliberately hostile to that reading: the hard gate in §6 is the *most likely* place for this to stop, because a
crippled repertoire is exactly what the droplet offers and exactly what a fingerprint needs least. If the
repertoire-limited arm fails, the correct outcome is **continued blocking and a publication-oriented metrology
synthesis** — and that synthesis is already largely written, in `PROGRAMME_SYNTHESIS.md` and the capability matrix.

**Nothing is executed. EXP-SC-01 remains BLOCKED. Stopping for strategic review.**

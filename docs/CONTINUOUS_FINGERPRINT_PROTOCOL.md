# EXP-GT-CONTINUOUS-FINGERPRINT-00 — PROTOCOL (PREREGISTERED)

**Continuous-Observable Causal Response Fingerprint.**

**Written and committed BEFORE the instrument exists.** Everything below — the split, the challenge matrix, the
calibration rule, the numeric safety factors, and the pass/fail gates — is fixed here, in advance, and is not
revisited after any result is seen. A success bar invented after the distributions are known is not a bar.

---

## 1. The claim, and its exact width

> A **fixed** continuous-response fingerprint can remain **stable** across repeated observations and across
> behaviourally equivalent continuous systems, while **separating** genuinely different accessible dynamics or
> hidden state, under a **declared noise model** and a **fixed intervention repertoire**.

**This inherits NOTHING from `EXP-GT-FINGERPRINT-00`.** The Boolean instrument's prospective PASS is not
transferable and is not transferred. This is a new instrument, a new substrate, a new split, a new freeze.

### Explicitly NOT claimed
identity · individuality · lineage · life · agency · selfhood · consciousness · minimal architecture · universal
causality · **droplet transfer** · substrate-independent equivalence · successful material-turnover detection.

### The verdict vocabulary. There is no SAME.
`INDISTINGUISHABLE_UNDER_REPERTOIRE` · `DIFFERENT` · `INDETERMINATE`.
Two systems no admissible probe can separate form an **equivalence class**, reported as `EQUIVALENCE_CLASS_ONLY`.

---

## 2. The declared nuisance group `G`

A transformation in `G` **must not** produce a `DIFFERENT` verdict.

| # | nuisance | why it is a nuisance |
|---|---|---|
| N1 | **affine readout** `u -> a*u + b`, `a>0` | a change of units is not a change of the world |
| N2 | **measurement-noise realization** (seed) | a second look is not a second system |
| N3 | **solver refinement** RK4 `h=0.25 -> 0.125` | discretization is not behaviour. Licensed by MEASUREMENT: the disagreement is 6e-9 to 2e-7 relative, far below the noise floor |
| N4 | **cyclic carrier time-origin shift**, group `Z_4` acting by 3 samples | a clock offset is not a cause |
| N5 | **internal degrees of freedom not coupled to the accessible I/O** | an insides difference no admissible probe can reach |

### NOT nuisances — these are the accessible function and MUST separate
gain · sign · transport latency · latency structure · saturation · reachable hidden state · persistence/memory ·
independently controllable additional causes.

### THE MEASUREMENT CONTRACT — a theorem, not a preference

> If the readout may be rescaled by an unknown `a>0`, the only scale the instrument can calibrate against is the
> channel's own **noise floor**. Therefore a system whose noise floor is halved is, to this instrument, *exactly*
> as indistinguishable from a system whose **gain is doubled**.
>
> **Absolute gain is NOT identifiable when both the output scale and the noise scale are free.**

So the noise **scale** is **not** a nuisance. It is a declared property of the channel. A comparison is admissible
only if the two systems are **declared** to sit on a **common noise channel** (`common_channel=True`). The
admission layer REFUSES otherwise. Control **L8** removes the refusal and shows the false difference walk in.

**This is exactly the debt the droplet mapping will have to pay physically** — see `field noise` in the
domain-admission contract.

---

## 3. Substrate

`edlab/substrates/ctrans` — a spatially embedded chain of 6 continuous sites. Site 0 = exogenous DRIVE field,
site 1 = local SUPPLY line (both external); sites 2–5 internal (rich access only). Accessible observable is a
**continuous float of order 1e-3** — the droplet's magnitude, deliberately — carrying measurement noise and a slow
OU baseline drift. Full spec: `docs/CONTINUOUS_SUBSTRATE_SPEC.md`.

The two naive mappings are confirmed to fail **on this substrate**, exactly as D-073 predicted for droplets:
* cast to `uint8` -> every sample becomes `0` -> **universal false sameness**;
* exact float inequality -> **304/304 samples differ from the system's own re-measurement** -> **universal false difference**.

---

## 4. Ground truth has TWO paths, and a case is scored only if they agree

| path | what it is |
|---|---|
| **1. construction-declared** | the label in `manifests.py`, written from the system that was BUILT, committed before the instrument |
| **2. privileged evaluation** | `evaluator.py`: noise-free, a **dense random 48-input ensemble that is NOT the battery**, exact trace comparison at solver tolerance `1e-5`, quotiented by `G` |

`evaluator.py` **never imports the instrument**. It shares with it only the *declared nuisance group*, the
*declared observation horizon*, and the *declared noise scale* — it must, because both describe the same
measurement contract. It shares **no** distance, standardization, block structure, radius, or verdict rule.

**A disagreement REJECTS the case before scoring.** More than 2 rejected cases -> `BENCHMARK_INVALID`.

---

## 5. The split — structural, not conventional

| axis | development | prospective (RESERVED, NOT RUN UNTIL FREEZE) |
|---|---|---|
| seeds | `1xx_xxx` | `9xx_xxx` (disjoint) |
| delay `tau` | {0, 4, 8} | {2, 6, 11, 14} |
| time constant `T` | {5, 8, 16} | {7, 13, 21} |
| gain | {1.0, 2.0} | {1.5, 3.0} |
| readout saturation `k_out` | {0, 1.2} | {0, 1.7} |
| feedback `k` | {0.5} | {0.8} |
| noise `sigma` | {1.0e-5} | {1.2e-5, 1.6e-5} — **UNSEEN** |
| carrier shift | {0, 3} | {9} |
| units `(a,b)` | {(1000, 0.5)} | {(250, −0.02)} |
| topology | leak, cascade, sat, feedback, fir, memory, hidden-mode, supply-cause, access-restricted | all of those **plus `feedback_sat`** — feedback around a saturating element, **which development never saw** |

**No prospective system is parameter-identical to any development system.**

**DECLARED FAMILY REUSE, AND THE CLAIM IT COSTS.** The prospective set reuses the *component library*. It does not
reuse a parameter vector, and it adds one unseen topology. Declared here, before execution: what may be qualified
is a fingerprint for **continuous responses of systems drawn from this component library** — not a claim about
continuous systems in general, and **not a claim about droplets**.

**Enforcement:** the prospective experiment **refuses to run** unless the freeze manifest's sha256 hashes match the
instrument files on disk.

---

## 6. Calibration rule — FIXED NOW, BEFORE ANY DISTANCE IS SEEN

The tolerance is derived **only from the NULL**: repeated independent measurements of the *same* development
system. It never looks at a difference pair, and it never looks at a label.

```
r_continuity = SAFETY * quantile_99.9( DEV NULL distance distribution )      SAFETY     = 2.0
r_separation = SEP_FACTOR * r_continuity                                     SEP_FACTOR = 3.0
```

`SAFETY = 2.0` and `SEP_FACTOR = 3.0` are **declared here and frozen**. They are not tuned.

Because every stochastic term in the substrate scales with `sigma`, and the representation divides by the
channel's *measured* noise scale, **the null distance is sigma-invariant by construction**. A radius calibrated on
development noise is therefore expected to transfer to an unseen noise regime **by construction, not by luck** —
and gate **G7** is where that expectation is cashed or exposed.

If development difference distances do not clear `r_separation`, **the instrument fails on development** and is
reported as failing. The radii are not moved.

---

## 7. PREDECLARED PROSPECTIVE GATES — exact

Evaluated **per arm** (`limited`, `rich`), against the per-arm construction expectation.

| gate | requirement | threshold |
|---|---|---|
| **G1** | every `CONTINUITY` / `FALSE_DIFFERENCE` case whose expectation is `INDIST` is **not** called `DIFFERENT` | 100% |
| **G2** | every `DIFFERENCE` case is called `DIFFERENT` | 100% |
| **G3** | **strict non-overlap**: `max d(expected-INDIST, admitted)` < `min d(expected-DIFFERENT, admitted)` | gap > 0 |
| **G4** | every `ABSTAIN` case returns `INDETERMINATE` | 100% |
| **G5** | false-sameness pair: `limited` -> `INDISTINGUISHABLE` **and** `rich` -> `DIFFERENT`; reported `EQUIVALENCE_CLASS_ONLY`, never `SAME` | both |
| **G6** | **unit invariance, exact**: with identical seeds, the standardized fingerprint of `A` and of `affine(A)` agree | max rel. diff <= 1e-9 |
| **G7** | continuity survives the **unseen elevated noise regime** (1.6x dev) | C-P-08 passes G1 |
| **G8** | **hidden state** is detected prospectively | C-P-16 -> `DIFFERENT` |
| **G9** | **non-vacuity**: >= 4 `DIFFERENT` and >= 4 `INDISTINGUISHABLE` verdicts; every non-silent, non-restricted system has responsiveness > 0 and coverage = 1.0 | as stated |
| **G10** | the two truth paths agree on every scored case | 100%; > 2 rejects -> `BENCHMARK_INVALID` |

**PASS** iff G1–G10 hold. Any gate failing -> `FAIL`. Benchmark self-inconsistent -> `BENCHMARK_INVALID`.

**Rich-only success** (gates hold under `rich` but not `limited`) -> the declared conclusion is:
*continuous causal fingerprints work in principle under rich continuous interventions, but not under the limited
repertoire relevant to droplets.* **The droplet pilot remains blocked.**

---

## 8. Must-fail controls — each MUST actually fail

A must-fail control that still passes was never load-bearing, and its "protection" is decoration.

| id | what it breaks | expected consequence |
|---|---|---|
| **L1** | calibrated comparison -> **exact float inequality** | false DIFFERENCE explodes |
| **L2** | **integer collapse**: cast the response to `uint8` with no calibrated scaling | false SAMENESS explodes |
| **L3** | **short response window**, below the longest development latency | late responses / memory misclassified |
| **L4** | **remove the SUPPLY probes** | the `supply_cause` pair collapses — it is EXACTLY identical under drive-only probing, by construction |
| **L5** | **reintroduce a forbidden descriptive coordinate** (topology label / hidden implementation id) | false DIFFERENCE among behaviourally equivalent implementations |
| **L6** | **lexicographic phase sort** instead of the cyclic-shift group quotient | false DIFFERENCE: a canonical ordering of *continuous* rows is discontinuous under noise |
| **L7** | **noise-blind normalization**: divide by the response's own RMS instead of the noise scale | false SAMENESS: the genuine gain difference vanishes |
| **L8** | **disable the common-channel refusal** | false DIFFERENCE: a quieter channel is read as a larger gain |

---

## 9. Failure taxonomy

Every failure is classified BEFORE any repair is proposed: physics · observer · **response-representation** ·
**noise-model** · normalization · provenance · implementation · benchmark-label · evaluator/ground-truth ·
non-identifiability · insufficient intervention access · leakage · vacuous success · scope · partition.

## 10. Partition scope

This substrate has **one declared object** and **no ambiguous object boundary**. Partition dependence is therefore
**not exercised** and **remains unresolved**. No partition-robustness claim is made, and none may be read into a
PASS here.

## 11. Kill switch

* prospective failure -> the instrument version is **RETIRED**, artifacts preserved, **no repair is called qualified**;
* a repaired instrument requires a **new split** and a **new authorization**;
* PASS authorizes **only** `SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`, which is an *assessment* of whether a
  physical mapping to droplets is even definable. It does **not** authorize running the droplet pilot.

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**.

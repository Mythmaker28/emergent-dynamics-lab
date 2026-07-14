# CAPABILITY MATRIX — every observer generation

**Legend.** `QUALIFIED` = demonstrated on a frozen prospective split, once, against privileged ground truth ·
`DIAGNOSTIC ONLY` = measured, but on burned worlds, or with an evaluator defect that invalidates the metric, or
recovered correctly under a criterion that was not the one being tested · `FAILED` = tested prospectively and did
not meet its preregistered bar · `UNTESTED` = never exercised (in several cases **not constructible** in that
substrate, which is noted).

Nothing below is a scalar and nothing is composited. A generation may fail on one capability and hold on another;
that is the whole point of factorization, and it is why the retirements did not destroy the results.

| capability | G0 monolith (EXP-GT-00) | G1 factorized V2 | G2 head V3 | G3 head V4 (GoL) | G4 module discovery | G5 source-transducer | G6 active causal |
|---|---|---|---|---|---|---|---|
| **object boundary** | FAILED (persistent-site heuristic) | DIAGNOSTIC ONLY (declared components) | DIAGNOSTIC ONLY | DIAGNOSTIC ONLY ¹ | **QUALIFIED** (exact, mean IoU 1.000 on unseen impls) | QUALIFIED | **QUALIFIED** (region found 24/24) |
| **causal source discovery** | UNTESTED | UNTESTED | UNTESTED | UNTESTED (sources are declared) | **FAILED** (delayed copies counted as independent parents) | DIAGNOSTIC ONLY ² | **QUALIFIED** (count 100 %, identities 100 % vs privileged audit) |
| **temporal provenance** | UNTESTED | UNTESTED | UNTESTED | UNTESTED ³ | UNTESTED | **FAILED** (negative index fabricated source histories) | **QUALIFIED** (20/20; 0 fabricated, 0 excluded, lag 17→56 no degradation) |
| **reachable manifold** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **FAILED** (tables measured off-manifold) | DIAGNOSTIC ONLY ⁴ | **QUALIFIED** (coverage correct; partial → `EQUIVALENCE_CLASS_ONLY` on unseen) |
| **function (I/O on the reachable manifold)** | DIAGNOSTIC ONLY (output-series distance) | **QUALIFIED** (head F) | QUALIFIED (F) | **QUALIFIED** (F) | **FAILED** (50 % on unseen impls) | **FAILED** (29.2 %) ⁴ | **QUALIFIED** (100 % vs privileged simulation) |
| **hidden state** | UNTESTED | UNTESTED | UNTESTED | UNTESTED (not constructible in GoL library) | UNTESTED | **FAILED** (12/24 false `FINITE_STATE`) | **QUALIFIED** (6/6, on the true state machines and nowhere else) |
| **model minimality** | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | UNTESTED | **FAILED** (21/24; cannot eliminate a redundant history variable) |
| **architecture** | **FAILED** (composite scalar) | **FAILED — IMPLEMENTATION** (held-out) | **FAILED → RETIRED** | **QUALIFIED** (A_TOPO/A_TAU/G, third fresh split, D-060) ¹ | DIAGNOSTIC ONLY (micro/macro quotient) | DIAGNOSTIC ONLY | DIAGNOSTIC ONLY ⁵ |
| **lineage** | UNTESTED | **QUALIFIED** (head L) | QUALIFIED (L) | **QUALIFIED** (L; E1/E2 Ship-of-Theseus) | UNTESTED | UNTESTED | UNTESTED |
| **abstention** | **FAILED** (never abstained) | QUALIFIED (fires) | QUALIFIED | **QUALIFIED** (fires) ¹ | **FAILED** (6/24 false certainty, 0 abstentions) | **FAILED** (12/24 false abstention) | **QUALIFIED** (response-level: 9/24 abstentions, all correct) ⁶ |
| **PROSPECTIVE STATUS** | **FAILED** | **FAILED** | **FAILED → RETIRED** | **QUALIFIED** (GoL; hierarchy UNTESTED) | **FAILED → RETIRED** (D-065) | **FAILED → RETIRED** (D-067) | **FAILED → RETIRED** (D-069) |

**¹** V4's architecture head is prospectively qualified on Game of Life *only*, with declared limits: **no scope
self-check** (components closer than 4 cells are silently merged), program-invariance **not constructible**,
feedback **not constructible**, and **hierarchical blind discovery never attempted**.

**²** G5's prospective source-**count** was 95.8 %, but the source-**identity** metric is invalidated by an
evaluator defect of mine (the write-enable rail was excluded from ground truth). It is therefore not a result. The
same question was answered cleanly by G6 against a corrected privileged audit.

**³** Temporal provenance was not a concept before D-067. G3's windows happen to have been adequate; **that is not
a demonstration**, and it may not be claimed as one.

**⁴** G5's function failure is *caused by* its provenance failure, not by an independent defect of manifold
reasoning. Its manifold logic — coverage, partial tables, off-manifold abstention — was correct on development and
is not separately falsified; it is DIAGNOSTIC ONLY because it was never tested on uncorrupted features.

**⁵** G6 recovered micro regions correctly, but the **full hierarchy** (machine graph, A/S/F/L/M, counterfactual
validation of macro objects) was gated behind prospective qualification and therefore **never ran**.

**⁶** G6's three errors were **description-level** (a model-class label), not **response-level**. It never claimed
a wrong function, a wrong source, a wrong coverage, or a state machine that was not one. The description-level
failure is recorded in the `model minimality` row, where it belongs.

---

## SCOPE CLARIFICATIONS (D-071) — two capabilities that must not be assumed to travel

**1. Temporal provenance is qualified ONLY for the certified Boolean-world pipeline and its executable provenance
contract.** The 20/20 certificate and the "0 fabricated / 0 excluded rows" result are statements about
`provenance.py`, `Episode`, `_idx` and the assertion that re-reads every source sample from its own episode. They
are **not** a statement about any other substrate's data path. A continuous reaction-diffusion field has no
episodes, no discrete lags and no cell samples to re-read; its provenance contract does not exist yet and would
have to be built and certified separately.

**2. Exact direct-edge recovery is established ONLY in the synchronous Boolean substrate, under the declared
one-step pulse access.** "Flip a cell at step t and whatever differs at t+1 is a direct child" is a theorem about
a **synchronous, discrete, unit-delay** update rule with **arbitrary single-cell write access**. It has no droplet
analogue: droplet dynamics are continuous and diffusive (there is no "one step later"), and no experimenter can
flip one lattice site of a physical droplet's interior.

**3. (D-073) The RESPONSE REPRESENTATION is qualified ONLY for a BINARY observable.** The frozen fingerprint
decides by **Hamming distance over `uint8` symbols**. The droplet's accessible observable is a **continuous float**.
The instrument is **undefined** there: cast to `uint8` every droplet is identical; compared as floats every droplet
differs from its own later self. Supplying the missing quantization / tolerance / amplitude-mapping rules is
**instrument definition**, not adaptation. This is why `SC-PILOT-CAUSAL-FINGERPRINT` returned `PREFLIGHT_FAIL`.

**Neither capability is assumed to transfer to droplets.** Any droplet claim must re-earn both from scratch, under
that substrate's own access constraints. This is recorded here precisely because the temptation to quote a Boolean
result in a continuous substrate is exactly the category of error that retired three observers.

---

## The scope of the D-069 verdict, stated exactly

**G6 predicted every measured function correctly.** Its tables agree with privileged simulation on **every row of
every world**, including the four implementations it had never seen. It did not misunderstand the prospective
worlds.

**G6 failed the preregistered minimal-representation criterion**, on 3 of 24 transducers, because its search can
**widen** a history window but cannot **eliminate a redundant history variable**. On `xor3` it therefore reported
`FINITE_HISTORY` where `DELAYED_STATIC` is the minimal truth — a correct model with one argument too many.

It is **not fully qualified**, and it is **not a failure of comprehension**. It is a failure of *description
minimality*, and that distinction is the entire content of the strategic question that follows.


---

# EXP-GT-CONTINUOUS-FINGERPRINT-00 — Continuous-Observable Causal Response Fingerprint

**RESULT: FAIL (prospective). RETIRED.** Development 52/52; prospective 52/54; **gate G2 failed**.

| capability | status |
|---|---|
| continuous response representation on a float observable of order 1e-3 | **DEFINED** (NSRC — noise-standardized response curve) |
| exact invariance to an affine change of readout units | **DEMONSTRATED** — prospective deviation **0.0** |
| sensitivity to internal gain, preserved alongside that invariance | **DEMONSTRATED** — gain x2 -> d = 170.6 |
| separation of sign, latency, latency structure, saturation, feedback-vs-FIR, extra causes | **DEMONSTRATED** |
| genuine hidden-state detection (bistable memory) | **DEMONSTRATED** — d = 204.2 |
| repertoire-relative equivalence (false sameness reported, never SAME) | **DEMONSTRATED** — limited d = 2.51 / rich d = 88.9 |
| abstention on silent / unreadable / nonstationary / in-flight / access-restricted / off-contract systems | **DEMONSTRATED** |
| **DIFFERENCE pairs all separate under the frozen instrument** | ### **FAILED** — `P_cascade` refused by a falsely-firing in-flight guard |
| droplet transfer | **NOT CLAIMED. NOT ADMISSIBLE.** |
| partition robustness | **NOT EXERCISED. UNRESOLVED.** |

**4. (D-074) THE SETTLING CRITERION DOES NOT TRANSFER ACROSS RESPONSE ORDER.** The in-flight guard's threshold
(a row is still moving if its tail changes by >5% of its own peak) was calibrated, implicitly, on **first-order**
development systems whose transients collapse fast (`P_leak`: 0.66%). A **second-order** prospective cascade with
`T3 = 21` has a slower tail (**5.3%**) and trips it. The instrument then **abstained on a case it could have
decided** — the privileged path puts the true settling time at 108, well inside the 160-sample window.

**A fabricated abstention is exactly as dishonest as a fabricated certainty, and harder to notice, because it
looks like caution.** This is the failure mode the programme had not previously catalogued, and it is now on the
record.

**5. THE MEASUREMENT-CONTRACT THEOREM.** Absolute gain is **not identifiable** when both the output scale and the
noise scale are free: a halved noise floor and a doubled gain are the same observation. The noise scale is
therefore **declared, not inferred**, and the admission layer **refuses** cross-channel comparisons. This is a debt
any droplet mapping must pay **physically** — "field noise" is on the unresolved list for exactly this reason.


---

# EXP-GT-CONTINUOUS-FINGERPRINT-01 — Tail-Aware Continuous Causal Fingerprint

**RESULT: FAIL (development). NOT FROZEN. PROSPECTIVE NOT RUN — the hold-out is PRESERVED, not burned.**

| capability | status |
|---|---|
| bound the EVENTUAL distance under window extension, without modelling the tail | **DEFINED** (contract-checked worst-case envelope; bracket, not point estimate) |
| **v00's fatal case (`P_cascade`) classified BY BOUND, not by exception** | **DEMONSTRATED** — `D_lo = 41.9` vs `r_sep = 22.1`. No hard-coded exception exists in the guard. |
| genuinely non-settling response abstains | **DEMONSTRATED** |
| slow-but-harmless tail classifies (`DECIDABLE_SLOW_TAIL`) | **DEMONSTRATED** |
| noise/drift not read as unresolved response | **DEMONSTRATED** |
| guard is load-bearing (removing it produces a premature verdict) | **DEMONSTRATED** |
| v00's guard, restored, reproduces its unnecessary abstention | **DEMONSTRATED** |
| **slow tail NEAR the decision boundary abstains (T4)** | ### **FAILED — the resolution floor** |
| out-of-contract detection in the band (TAU_MAX, 2.5x TAU_MAX) | **UNVERIFIED SCOPE — the bound is unsound there and cannot tell** |

**6. (D-075) THE TAIL-UNCERTAINTY BOUND HAS A RESOLUTION FLOOR, AND IT IS THE SAME ORDER AS THE REMAINDERS THAT
MATTER.** Measured on 288 noise-only blocks, the bound's remaining-envelope statistic reaches **7.40** on pure
noise, forcing `TAIL_NOISE = 9.0`. The decisive near-boundary control carries a **real** remainder whose envelope
measures **8.25** — *inside the floor*. The instrument calls it SETTLED and returns a confident DIFFERENT on a pair
whose answer is still outside the window.

**This is version 00's error in the opposite direction: v00 abstained when it should have spoken; v01 speaks when
it should abstain.** The floor is set by the tail region's length (76 samples) against the noise on a sub-block
mean. The fix — a longer observation window — is a BATTERY CHANGE and therefore a new instrument.

**7. A CHECK AND A BOUND WANT DIFFERENT CONFIDENCE LEVELS.** Using one constant for both inflates the remainder
estimate to ~15 noise units on *pure noise*, drowning the ~20-unit remainders it exists to find. Conservatism
applied to the wrong quantity is not caution; it is noise.


---

# EXP-GT-CONTINUOUS-FINGERPRINT-02 — Resolution-Certified Tail-Aware Continuous Fingerprint

**RESULT: FAIL AT DEVELOPMENT. Not frozen. Prospective NOT run — the sealed split remains untouched.**

**8. (D-076) THE TAIL-BOUND METHOD HAS A RESOLUTION CEILING THAT NO OBSERVATION HORIZON CAN RAISE.**

Preregistered gate: `B_critical(W) >= 3 * B_noise(W)`. Measured across the preregistered grid
{160, 240, 320, 480, 640}, the ratio is **0.89 / 2.55 / 2.56 / 1.18 / 0.29** — it **PEAKS AT 2.56 AND COLLAPSES**,
and never reaches 3.0.

```
B_noise  improves as exp(-(W-84)/(3*TAU_MAX))      B_signal decays as exp(-W/tau)
```

**The signal decays faster than the noise floor improves whenever tau < 3*TAU_MAX -- true for essentially every
in-contract system, because TAU_MAX is by definition the slowest one admitted. A LONGER WINDOW DESTROYS THE VERY
EVIDENCE IT WAS SUPPOSED TO REVEAL.**

At the end of v01 the agent proposed a longer window as the fix. **That hypothesis is falsified by measurement.**
The failure is structural: a successor must change the METHOD, not the budget.

**9. THE NOISE FLOOR IS DRIFT-LIMITED, NOT WHITE-NOISE-LIMITED.** The white-noise model predicts B_noise -> 0.58 by
W=320; measured **3.49**, and it stops improving. Sub-block MEANS wander with the slow baseline while `sd`, derived
by differencing, is BLIND TO DRIFT BY CONSTRUCTION. The longer you look, the more the baseline has wandered.
Consequence: the out-of-contract bars are NOT constants across horizons (carrying v01's values across the grid made
the NULL itself come back out of contract).

**10. A PREFIX OF A LONG EPISODE IS NOT A SHORT EPISODE WITH THE SAME SEED.** The engine draws measurement noise
(T samples) then drift from the same RNG stream, so the drift sequence depends on episode length. Measured
`max|Z_long[:320] - Z_short(320)| = 6.48` **on a system compared with itself**. v01's T7/T8 varied the window by
re-simulating and were therefore measuring the RNG. Window-invariance controls MUST use nested prefixes of one
acquisition.

**What v02 does achieve (13/15 dev gates at W=320):** the v00 burned cascade is fixed BY BOUND
(`D_lo = 45.52` vs `r_sep = 22.89`, DECIDABLE_SETTLED); harmless slow tails classify; non-settling, out-of-contract,
drifting and silent systems abstain; gain, hidden state and extra causes separate; continuity and
EQUIVALENCE_CLASS_ONLY hold. **None of it matters: the battery cannot SEE the remainders it must act on.**


---

# EXP-GT-CONTINUOUS-FINGERPRINT-03 — Drift-Aware Risk-Calibrated Fingerprint

**RESULT: BENCHMARK_INVALID.** The target quantity is ill-posed. Detected BEFORE any predictor was fitted. The
calibration set was never touched; the sealed prospective split was never touched. **BRANCH CLOSED — NO V04.**

**11. (D-077) THE FINGERPRINT DISTANCE IS NOT A PROPERTY OF A PAIR OF SYSTEMS. IT IS A PROPERTY OF THE PAIR AND
THE OBSERVATION WINDOW.**

An RMS-over-window metric DILUTES any TRANSIENT difference at exactly the normalization rate and tends to ZERO as
the window grows. Measured on noise-free traces, same metric, only the window changed:

| pair | W=320 | W=1400 | ratio |
|---|---|---|---|
| v00 burned cascade | 47.35 | 22.64 | **0.478** |
| v01 T4 | 30.18 | 14.45 | **0.479** |
| gain x2 | 115.32 | 55.13 | **0.478** |
| sign inversion | 230.64 | 110.27 | **0.478** |
| **hidden state (PERSISTENT)** | 346.43 | 348.01 | **1.005** |

`sqrt(320/1400) = 0.478`. **The persistent difference does not dilute. That control proves the effect is the
METRIC, not the systems.**

**CONSEQUENCE, and it retrospectively explains the whole branch: for a FIXED window the instrument already sees
everything it will ever see. There is no "unseen remainder" affecting D_W -- the only uncertainty is measurement
noise. v00's in-flight guard, v01's tail bound and v02's resolution certificate were each defeated by a quantity
THAT DOES NOT EXIST.** The one legitimate truncation concern is PERSISTENCE, which does not dilute and is fully
captured by any window exceeding the settling time plus the declared delay horizon.

**12. A RISK-CALIBRATED INSTRUMENT IS ONLY AS MEANINGFUL AS THE QUANTITY WHOSE RISK IT CALIBRATES.** v03's retreat
from proof to conformal risk was sound in principle, but it inherited the ill-posed target. The two-path truth
check caught it before a single parameter was fitted.

**13. A WELL-POSED CONTINUOUS FINGERPRINT NEEDS A WINDOW-INVARIANT DISCREPANCY FUNCTIONAL** -- an integral rather
than a mean, or normalization by response energy rather than window length. That is a change to the METRIC, the one
component unchanged since v00, and therefore a NEW PROGRAMME, not a new version.


---

# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00 — Factorized Causal Response Decomposition (NEW PROGRAMME)

**RESULT: FAIL AT DEVELOPMENT (19/20).** Not frozen. The new prospective split was NOT touched.

**14. (D-078) THE FACTORIZATION WORKS. THE DILUTION IS CURED.** On nested prefixes of ONE acquisition, the old
window-normalized scalar falls 144.04 -> 83.17 (ratio 0.577 = sqrt(160/480), exactly as predicted) while the new
`E_trans` -- AN INTEGRAL, NOT A MEAN -- converges upward (3.220e6 -> 3.365e6) and `P_inf` correctly stays at ZERO
for a transient with an identical asymptote. The two quantities the old scalar conflated now live on separate axes.

**15. PEAK AND ENERGY ONLY COME APART WHEN THE SHAPE COMES APART.** A single leaky path CANNOT dissociate them:
measured, its shape factor E/A^2 stays in 18-41 across Tx from 1 to 64, and the best equal-energy peak ratio
achievable is 1.36 -- a rounding error, not a control. With a high-pass SPIKE (E/A^2 = 6.9) against a cascade BROAD
path (E/A^2 = 56.1): EQUAL ENERGY -> peak ratio **3.09x**; EQUAL PEAK -> energy ratio **7.04x**. Both axes separate
on their own.

**16. (THE FAILURE) A SHAM CAN CALIBRATE A BAND. IT CANNOT SUBTRACT A REALIZATION IT NEVER SAW.** The matched sham
has the same VARIANCE as the causal trace's drift but is an INDEPENDENT REALIZATION, so debiting its ENERGY is
unbiased in expectation and useless per pair. Drift-only controls pass perfectly (a band is all they need); a slow
causal response UNDER HEAVY DRIFT is overstated 7.1x and its drift excursion is quoted as a causal peak. **The
instrument calls the drift a response instead of abstaining.** A successor must change the ACQUISITION -- a sham
that SHARES the drift realization (interleaved / common-mode), not merely its distribution -- not the estimator.

**17. TWO INHERITED ASSUMPTIONS, BOTH NAMED.** (a) The old `BASELINE_MAX` refusal, imported with admission,
re-imposed "refuse anything that drifts" and threw away the sham machinery this programme exists to test -- THE
SAME MISTAKE v01 MADE with v00's dead in-flight guard. (b) `max`-over-blocks is a VERDICT rule, not an ESTIMATOR:
over 32 blocks it selects the block where independent drift realizations conspire. Phases are REPLICATES (median);
probes are DISTINCT INTERVENTIONS (max).

| CRD-01 common-mode causal decomposition | continuous | DEMONSTRATED (ground truth) / TRANSFER NOT ESTABLISHED (physics) | E/E*=1.01x on the pair CRD-00 got 7.1x wrong; refuses outside its admission region; but needs a simultaneous unprobed copy of the same system, which no droplet can supply |
| CRD-02 referenced paired-episode decomposition | continuous | FAIL (development, gate G5) / architecture PHYSICALLY PLAUSIBLE (G14 pass) | drift half solved without an oracle twin: Z-17 E/E*=1.00 A/A*=1.02, admission tracks validity on 8 axes; fails on contamination -- kappa~0.15 identifiability floor leaves a 12% leak as a silent 21% attenuation. Prospective split SEALED. |

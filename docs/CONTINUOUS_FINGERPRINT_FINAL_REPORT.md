# EXP-GT-CONTINUOUS-FINGERPRINT-00 — FINAL STRATEGIC REPORT

## 1. Repository grounding

Inspected before assuming anything. **The handoff was wrong on one point:** the branch is **`main`**, not
`master`. HEAD was `1020aae` as reported, tree clean, and all four reported preflight artifacts exist
(`exp_preflight.py`, `PREFLIGHT_AUDIT.md`, `PREFLIGHT_DECISION.json`, `PREFLIGHT_RAW.json`). The D-073
`PREFLIGHT_FAIL` and the withdrawn "uninterrupted behaviour" claim were read in full and are **preserved**.

## 2. Exact experiment claim

> A fixed continuous-response fingerprint can remain stable across repeated observations and across behaviourally
> equivalent continuous systems, while separating genuinely different accessible dynamics or hidden state, under a
> declared noise model and a fixed intervention repertoire.

It inherits **nothing** from `EXP-GT-FINGERPRINT-00`.

## 3. Why the Boolean instrument could not transfer

Its response representation is `uint8` symbols compared by **Hamming distance**. Both naive mappings were
**reproduced on the new substrate** and both fail exactly as D-073 predicted:

| naive mapping | measured on `ctrans` |
|---|---|
| cast to `uint8` | every sample -> **0**. Universal false **sameness**. |
| exact float inequality | **304 / 304** samples differ from a re-measurement of the **same system**. Universal false **difference**. |

## 4. Continuous substrate

`ctrans`: a spatially embedded chain of 6 continuous sites. Site 0 = exogenous drive (carrier, period 12), site 1 =
supply line (both external); sites 2–5 internal (rich access only). Leaky integrators, integer transport delays,
saturating transducers, a **bistable memory**, feedback vs tapped delay lines, an **uncontrollable-from-outside**
mode, silent / unreadable / nonstationary / access-restricted systems. Observable: a **continuous float of order
1e-3** — the droplet's magnitude, on purpose — with measurement noise and an OU baseline drift **independent per
episode**. RK4; solver refinement (h=0.25 -> 0.125) disagrees by **6e-9 to 2e-7** relative, which is what licenses
"refinement is a nuisance" as a **measurement** rather than a hope.

## 5. Ground-truth independence

Two paths. **Construction-declared** (committed before the instrument existed) and **privileged evaluation**
(`evaluator.py`, which **never imports the instrument**: 48 **random** inputs, not the battery; noise-free; direct
trace comparison). Shared: only the declared nuisance group, observation horizon, and noise scale — they must be,
because both describe the same measurement contract. Shared otherwise: **nothing** — no battery, no `sigma_hat`, no
blocks, no radii, no aggregation, no verdict rule.

**The two-path check earned its keep: it caught a bug in the truth path itself** (see §20).
**Prospective: 54/54 agree, 0 disagreements.**

## 6. Development split

Committed at **`de97ee0`, before the instrument existed**, and verifiably disjoint: no shared system names, no
shared spec fingerprints, disjoint seed namespaces, disjoint parameter grids on every axis (`tau`, `T`, gain,
`k_out`, feedback `k`, `sigma`, carrier shift, units), and **one topology — `feedback_sat` — reserved to the
prospective set alone**. **Declared family reuse:** the component library is shared, so the claim is bounded to
systems drawn from **this library**. The prospective experiment **refuses to run** unless six sha256 hashes match.

## 7. Candidate representations tested

| detrend | representation | separation ratio |
|---|---|---|
| offset | **NSRC** (noise-standardized) | **1.52** -> selected |
| offset | `resp_rms` (normalize by the response's own RMS) | **0.51** |
| offset | `ncc` | **0.52** |
| linear | NSRC | 1.22 |

`resp_rms` and `ncc` score **below 1** — their differences are *smaller* than their nulls. Unit-invariant and
**gain-blind**. Retained only as control **L7**.

## 8. Selected frozen representation

**NSRC.** `r(t)` = mean over 16 repeats of (probe − baseline); offset-detrended on the pre-probe segment; divided
by `sigma_hat`, the channel's own **measured noise scale**. Aligned to the **exogenous probe onset** — which we
know, because we applied it — so latency stays in the representation and every window is the same length for every
system (the Boolean padding hazard cannot arise). The deviation is a **signed real**, so unlike the Boolean
XOR-deviation it is **not blind to output inversion**; no separate absolute channel is needed.

**The one idea:** units rescale the response **and the noise**; gain rescales the response and **leaves the noise
alone**. Standardizing by the noise is therefore *exactly* unit-invariant and *exactly* gain-sensitive.

Metric: per-block RMS, **max over blocks** (a FOR-ALL is certified by its worst case), minimized over the cyclic
phase group with **one** shift, and over one common scale `lambda` clipped to the noise-estimator's own **+-4.2%**
confidence band.

## 9. Noise and tolerance contract

See `CONTINUOUS_NOISE_TOLERANCE_CONTRACT.md`. Radii from the **NULL alone**, by a rule frozen before the instrument
existed. **The measurement-contract theorem:** absolute gain is **not identifiable** when both the output scale and
the noise scale are free — so the noise scale is **declared**, and cross-channel comparisons are **refused**
(control **L8** removes the refusal and false difference walks in). **Declared price: gain differences below ~4%
are not resolvable.**

## 10. Intervention battery

Fixed. Identical kinds, amplitudes, durations, onsets, phases, repeat count and order for **every** system. Eight
external probes (a **two-amplitude ladder** — a single-amplitude battery is provably blind to saturation), at all
four carrier phases, 16 repeats, **one independent baseline episode per probe episode**. The rich arm adds
sustained clamps on all four internal addresses. **A refused probe is MISSING and charged to coverage — never
substituted, never scored as zero.**

## 11. Development results

**Challenge matrix 52/52. Two-path validation 52/52, 0 disagreements.** Three instrument defects and one benchmark
defect were found, fixed, and are recorded in full in the development certificate (§20).

## 12. Must-fail controls — **7 of 8 fired**

L1 exact float inequality (1.0000 of samples differ from **itself**) · L2 uint8 cast of the raw observable
(**0.0000** — universal false sameness) · L3 short window (persistent rows 4 -> 12) · L4 remove the supply probes
(76.55 -> **3.01**, an exact constructed collapse) · L5 forbidden topology label (2.35 -> **51.18**) · L7
response-RMS normalization (gain x2 collapses to 1.490 vs null 1.448) · L8 disable the channel refusal (same
system, 4x noisier channel -> **DIFFERENT**).

**L6 DID NOT FIRE and is reported as such.** The lexicographic phase quotient is stable here because the phase rows
are well separated. The cyclic quotient remains principled but is **not demonstrated load-bearing**. **A control
that does not fire is not a control.**

## 13. Freeze identifiers

`docs/CONTINUOUS_FINGERPRINT_FREEZE_MANIFEST.json`. sha256 (first 16):
`cfingerprint.py e57836c541484b26` · `engine.py 30dee1db71176e00` · `systems.py ecc36c796fccd9a0` ·
`manifests.py f8a5c09b32154b14` · `evaluator.py 25f4e1ad0dc90fcf` · `exp_gt_cfp.py 6efdf6a9dba89f10`.
Radii: limited `r_cont=7.786 / r_sep=23.357`; rich `r_cont=8.207 / r_sep=24.622`.

## 14. Prospective evaluation — **FAIL**

One run, hash-verified, nothing tuned. **Matrix 52/54. Gates: G1, G3–G10 PASS. G2 FAIL.**

| arm | max(continuity) | min(difference) | gap |
|---|---|---|---|
| limited | 2.808 | 40.152 | **+37.344** |
| rich | 4.410 | 43.556 | **+39.146** |

**The separation is enormous and strictly non-overlapping. That is not what failed.**

`C-P-13` (`P_leak | P_cascade`) returned **INDETERMINATE** where the gate required **DIFFERENT** — in both arms.
The distance was **64.15** / **234.30**, far above the separation radius. **The instrument measured the difference
correctly and then refused to report it**, because its **in-flight guard** fired.

## 15. Coverage and abstention

Coverage 1.00 and responsiveness > 0 for every non-silent, non-restricted system. Every abstention case abstained
**for its declared reason**: silence, unreadability, nonstationarity, a genuinely in-flight response (`P_slow`,
true settling **651** vs window 160), a **measurement-contract violation**, and insufficient intervention access
(`P_lowcov`, coverage 0.25 — **and it still answers the supply probes it admits; it could have produced a confident
number from a quarter of the battery, and it refused**).

## 16. False sameness

`P_leak` vs `P_hidden`: an internal mode unreachable from the external fields that nonetheless feeds the readout.
Under limited access it sits at **exactly zero for all time** — the two are **bit-for-bit identical** (privileged
residual **0.0**). Instrument: **2.514** -> `EQUIVALENCE_CLASS_ONLY`. Under rich access: **88.85** -> `DIFFERENT`.
**Both are true. Equivalence is relative to a repertoire. The word SAME is never emitted.**

## 17. False difference

All inside the continuity radius: re-measurement 2.42 · **affine unit change `u -> 250u - 0.02` 2.57** · solver
refinement 2.53 · carrier shift 2.59 · extra unobservable internal DOF 2.74 · **continuity at an unseen 1.6x noise
level 2.81**.

## 18. Hidden-state detection

`P_mem_p` vs `P_mem_m` -> **204.18, DIFFERENT**. Visible because the bistable memory shifts the operating point of
the saturating readout and so changes the **incremental causal gain** (~7x between wells). **A hidden state that
merely added a constant to the output would be absorbed by the readout offset `b` and is, correctly,
unidentifiable.**

## 19. Unit and solver invariance

**Unit invariance is exact:** prospective max relative deviation between the standardized fingerprints of `P_leak`
and `affine(P_leak)` = **0.0** (bound 1e-9). **Gain is not removed with it**: gain x2 -> **170.6, DIFFERENT**.
Solver refinement: 6e-9 to 2e-7 relative, far below the noise floor.

## 20. Failure taxonomy

| # | classification | what it was | what it would have falsely concluded |
|---|---|---|---|
| 1 | **observer failure** (metric aggregation) | MEAN over probe blocks | that a system with an entire extra independently-controllable cause was nearly indistinguishable from one without it (21.8 diluted to 8.6) |
| 2 | **normalization failure** | `sigma_hat` error multiplying the signal | that **more data makes a causal measurement less reliable** (null 5.2 -> 9.4 -> 25.8 as repeats rose) |
| 3 | **observer failure** (thresholds) | `Z_DET=5` below the drift it thresholds | **that silence is evidence** — a silent system scored 1/32 "responses" and was handed a confident DIFFERENT |
| 4 | **observer failure** (fabricated abstention) | absolute in-flight threshold | that an ordinary `T=16` system's response had not finished |
| 5 | **benchmark-label failure** | `D_noisy` built at true SNR 1.97, not below its floor | that the instrument was wrong, when the **system** was |
| 6 | **evaluator / ground-truth failure** | free affine fit in the privileged path | that a **doubled gain** and an **inverted sign** are changes of units — slandering two flagship DIFFERENCE cases as EQUIVALENT |
| 7 | **provenance / implementation failure** | stale `.pyc` masking a **truncated source file** on a coarse-mtime mount | an early "differential verification" appeared to reproduce reference numbers **exactly** while running **old bytecode and verifying nothing** |
| 8 | **scope failure** (the fatal one) | settling criterion calibrated on first-order tails | **that a second-order system's response was still in flight when it was not** |
| — | **non-identifiability** (not a defect — a theorem) | absolute gain under a free output *and* noise scale | — |
| — | **partition failure** | **NOT EXERCISED.** One object, no ambiguous boundary. **Unresolved.** | — |

## 21. What was demonstrated

* The two naive continuous mappings **fail exactly as D-073 predicted**, on a substrate built to test them.
* A continuous representation can be **exactly unit-invariant and simultaneously gain-sensitive**, by
  standardizing to the **noise floor** rather than the signal.
* Repertoire-relative equivalence is measurable and reportable **without ever saying SAME**.
* Hidden state is detectable **exactly insofar as it changes the causal response**.
* Abstention works: silence, unreadability, nonstationarity, in-flight responses, insufficient access and
  off-contract channels are all **refused rather than guessed**.
* Seven of eight must-fail controls are **load-bearing**.

## 22. What was NOT demonstrated

* **The claim.** G2 failed. The instrument is **not qualified** and is **RETIRED**.
* **Droplet transfer.** Not claimed, not admissible, not attempted.
* **Partition robustness.** Never exercised. Unresolved.
* **That the cyclic phase quotient is load-bearing** (L6 did not fire).
* **Gain resolution below ~4%.** Bounded by the noise-scale estimator, by theorem.
* **Stochastic system variation.** The substrate's dynamics are deterministic; only the channel is stochastic.

## 23. Exact authorization decision

The failure is a **one-line threshold change** away from a pass. **It is not made.** A repaired instrument would be
one **tuned on its hold-out**, and the hold-out is now **burned**. A future version requires a **new split** and a
**new authorization**. The instrument was allowed to die, which was always the point.

## 24. Branch, commit, tests, modified files

Branch **`main`**. Split committed at **`de97ee0`** (before the instrument existed); this work commits on top.
New: `edlab/substrates/ctrans/{__init__,engine,systems,manifests,evaluator}.py`,
`edlab/identity/cfingerprint.py`, `edlab/experiments/{exp_gt_cfp,exp_gt_cfp_p}.py`,
`tests/test_ctrans.py`, `docs/CONTINUOUS_*`, `docs/DOMAIN_ADMISSION_CONTRACT.md`,
`results/EXP-GT-CFP-DEV/`, `results/EXP-GT-CFP-PROSPECTIVE/`.
Updated: `docs/CAPABILITY_MATRIX.md`, `docs/DECISION_LOG.md`.
No droplet experiment was launched. `beta`, `D_int` and the droplet equations were **not touched**.

---

**`EXP-GT-CONTINUOUS-FINGERPRINT-00: FAIL`**

**`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT: NOT AUTHORIZED`**

**`SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED.`**

**`EXP-SC-01 remains BLOCKED.`**

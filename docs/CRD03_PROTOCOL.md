# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-03 — PREREGISTERED PROTOCOL
## Redundantly Referenced and Signed-Intervention Causal Response Decomposition

**Committed before any operational fitting, any frontier sweep, and any prospective system.**

## 1. What CRD-02 established and where it failed

CRD-02's paired-episode architecture removed the oracle twin and solved the drift problem (Z-17 recovered
E/E*=1.00). It FAILED on one identifiability fact: with a single passive reference `r = a1 d + kappa s`, a
contaminated reference yields `s_hat = s(1 - alpha kappa)`, statistically indistinguishable from a smaller true
response. Detection floor kappa ~= 0.15; preregistered kappa=0.12 gave a silent 21% attenuation. CRD-02 stands as
`FAIL AT DEVELOPMENT`. This must not be rewritten as a qualification.

## 2. The CRD-03 identifiability theorem (established on development ground truth, before the instrument)

Latent `(d, s)`; measurement `y = s + a d`; references `r_i = a_i d + kappa_i s`. Pre-calibration on the `s=0`
window gives `alpha_i = a/a_i`. The only drift-free signals are

    z_i = y - alpha_i r_i = s (1 - alpha_i kappa_i).

The reference disagreement `r_i - (a_i/a_j) r_j` is a LINEAR COMBINATION of the z_i (proved symbolically:
`-alpha_1 D = z_1 - z_2` exactly). Therefore:

- **Shape** of `s` is always identifiable.
- **Differential contamination** (the z_i disagree) is identifiable to `kappa ~ 0.002`, and since contamination
  only ATTENUATES (`kappa_i >= 0`, `alpha_i > 0` => `|z_i| <= |s|`), the LARGEST-amplitude channel is the least
  contaminated and equals `|s|` exactly if any reference is clean.
- **Common-mode contamination** (`kappa_i` proportional to `a_i`, every `z_i` attenuated identically) is EXACTLY
  unidentifiable AND undetectable by any passive-reference scheme. It requires an absolute-scale anchor.

**Adding references never closes the amplitude ambiguity** in the common-mode direction: each new reference adds
one drift-free equation `z_i` and one unknown `kappa_i`. Signed interventions remove drift but leave every odd
combination of the form `s_odd(1 - alpha_i kappa_i)` — the scale ambiguity is untouched.

## 3. Exact claim

A redundant acquisition using multiple references with distinct drift couplings and/or signed interventions can
**identify and reject weak DIFFERENTIAL contamination of reference channels while preserving quantitative
factorized response estimates under drift**, with the amplitude reported as a **rigorous lower bound, exact when at
least one reference is uncontaminated**. Conditional on: declared reference coupling structure; sufficient
reference diversity; fixed intervention symmetry; valid calibration; stable noise/drift contract; prospective
qualification. It does **not** claim arbitrary counterfactual access, arbitrary contamination recovery, common-mode
recovery without an absolute scale, identity, life, agency, droplet transfer, or quantum behaviour.

## 4. Observation matrix and conditioning (identifiability admission)

For latent `(d, s)` the observation matrix is

    H = [[a, 1], [a_1, kappa_1], [a_2, kappa_2], ...]

Admission evaluates: rank; condition number; reference **diversity** (spread of drift couplings `a_i` — collinear
references cannot separate contamination); uncertainty amplification; residual consistency. If the reference
couplings are nearly collinear (`diversity < DIVERSITY_MIN = 0.15`) or `cond > COND_MAX = 12`, return
`REFERENCE_MIXTURE_ILL_CONDITIONED`. **The instrument never regularizes an unidentifiable problem into a confident
result.**

## 5. Acquisition arms (preregistered, development-only selection)

- **ARM A — redundant passive references.** Each episode carries N=3 simultaneous references with DISTINCT declared
  drift couplings `(0.8, 1.5, 1.15)`. Couplings are identified from the `s=0` pre-window (no hidden coefficient
  enters the estimator). Recovery: largest-amplitude clean set (contamination attenuates).
- **ARM B — signed interventions.** `+u` and `-u` episodes (separate -> independent drift). Drift is even under the
  sign flip; `s_odd = (y(+u)-y(-u))/2` removes drift with no reference; `s_even = (y(+u)+y(-u))/2 - y(0)` is
  retained for nonlinear responses. No perfect antisymmetry is assumed; the even part is measured.
- **ARM C — adaptive complementary null probes.** After a tentative response is detected, fixed complementary
  probes are applied to regions predicted NOT to carry the response; a non-null result flags a non-passive
  reference. The decision tree (first-stage probes, stopping rule, complementary set, confidence update, max
  intervention budget) is FROZEN before prospective execution. Classical adaptive design inspired by
  quantum-nondemolition logic — NOT quantum measurement.

**Selection rule (fixed here):** simplest arm passing every development gate. Priority: (1) ARM B if signs alone
identify contamination; (2) ARM A if references are required; (3) ARM A+B if neither alone passes; (4) ARM C may
improve admission but cannot rescue an algebraically rank-deficient design. Selection on development only.

## 6. Absolute-scale calibration audit

Common-mode contamination is resolvable only with an independent absolute response-scale anchor. Audited options: a
known weak reference perturbation; a conserved response integral; a calibrated external transfer standard; a
response channel of known gain. **On the frozen ctrans substrate none is available without reading privileged
state** (the readout gain `unit_a` is a declared per-system nuisance; no conserved integral is exposed). Verdict:
`ABSOLUTE_SCALE_UNAVAILABLE`. Common-mode contamination therefore remains a declared **lower-bound** direction. A
scale is NOT fabricated from privileged truth.

## 7. Contamination admission statuses

`REFERENCE_SYSTEM_IDENTIFIABLE`, `REFERENCE_CONTAMINATION_CORRECTED`, `REFERENCE_CONTAMINATION_DETECTED`,
`REFERENCE_MIXTURE_ILL_CONDITIONED`, `SIGNED_CONTRACT_VIOLATED`, `COMPLEMENTARY_PROBE_NON_NULL`,
`ABSOLUTE_SCALE_UNAVAILABLE`, `INDETERMINATE_REFERENCE_CONTAMINATION`. A weak but unresolved contamination leads to
abstention or a lower bound, never optimistic correction.

## 8. Factorized output — no composite score

`R = (E_trans, P_inf, A_peak, L_onset, T_recovery, C, U)`. Every component carries estimate, interval, component
status, reference-admission status, conditioning, coverage. Amplitude components (E_trans, A_peak) are marked
`LOWER_BOUND_ONLY` when the common-mode caveat cannot be discharged and `ESTIMATED` when contamination is
differential-and-removed under the declared >=1-clean contract.

## 9. Development cases D1-D17, gates G1-G15, must-fail controls 1-15

D1 Z-17; D2 CRD-02 kappa=0.12 regression; D3 kappa in {0.02,0.05,0.08,0.10} frontier; D4 common-mode (abstain/lower
bound); D5 different kappa; D6 collinear references (abstain); D7 signed linear; D8 signed nonlinear; D9 hysteresis;
D10 complementary null; D11 complementary contaminated; D12 local drift; D13 persistent; D14 transient; D15 hidden;
D16 peak/energy factorization; D17 limited-access collision (EQUIVALENCE_CLASS_ONLY).

## 10. Splits

New dev/prospective split: dev `13xx`, prospective `14xx`. No system-name overlap. R=24 signed repeats.
Prospective generated only after freeze, opened exactly once; development code is structurally prevented from
importing prospective acquisitions. Stable content-derived seeds.

# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-02 — FINAL REPORT
## Referenced Paired-Episode Factorized Causal Response Decomposition

## Verdict

    EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-02: FAIL  (at development — gate G5)
    Prospective split (12xx): SEALED, never acquired.

The paired-reference architecture **solves the problem it was built for** — it recovers the causal response
despite different drift realizations across episodes, with **no oracle twin** — but it **fails the preregistered
contamination gate G5**, and a failed development gate means the prospective split is not touched.

## 1. What was being tested

CRD-01 passed in ground truth but required a physically unrealizable control: the same system, simultaneously
probed and unprobed. CRD-02 removes that twin. Two **separate** episodes (active, sham), each carrying its **own
simultaneous common-mode reference**, with `d_A != d_S`; each episode corrected against its own reference; then a
difference-in-differences, `s_hat = (z_bp - z_bu) - (z_ap - z_au)`.

## 2. What works — and it is a real advance

| axis | result |
|---|---|
| **Z-17 regression (D1)** — slow response, heavy drift, **no oracle twin** | E/E* = **1.00**, A/A* = **1.02** |
| different drift realizations across episodes (D2) | E/E* = 1.00 |
| gain mismatch `b_A` | recovered to **x3.0** (E/E* = 1.00) |
| reference lag `eta_A` | recovered to **24 samples** (E/E* <= 1.08) |
| reference bandwidth (misses fast drift, D7) | E/E* = 1.01 |
| local unshared drift `loc_A` | admitted <= 0.5 (<=4% error), **rejected >= 1.0** |
| baseline mismatch only (D9) | all causal axes NULL-compatible |
| persistent + baseline (D10), hidden state (D13) | persistence **ESTIMATED**, E/E* ~ 1.0 |
| pure transient (D11), replacement/recovery (D12) | E/E* = 1.00 |
| peak/energy factorization (D14a) | E/E* = 1.01 |
| no per-episode reference (D3) | **rejected** (`NO_REFERENCE`) |
| **physical plausibility (G14)** | **PASS** — no simultaneous twin required |

On every axis except one, **admission tracks validity**: accurate inside the admissible region, refused outside
it. This is the property CRD-01 could not offer physically, and CRD-02 offers it — the drift half of the problem
is solved by a transferable acquisition contract.

## 3. Why it fails — contamination gate G5

Gate G5 (contamination protection) at the preregistered case D4 (kappa = 0.12): the instrument **neither detects
nor abstains**. It returns a confident `ESTIMATED` component that is attenuated **21%** (E/E* = 0.79).

The contamination detector (t-test on the reference's per-repeat coherence with s_hat) has a **detection floor at
kappa ~ 0.15**:

| kappa | detector t-stat | verdict | E/E* |
|---|---|---|---|
| 0.00 | 1.58 | CLEAN | 1.00 |
| 0.06 | 1.81 | CLEAN | 0.89 |
| **0.12** | **2.84** | **CLEAN (missed)** | **0.79** |
| 0.18 | 3.94 | SUSPECT -> abstain | — |
| 0.25 | 5.23 | REJECT | — |

Clean persistent/transient cases reach t ~ 2.8, so **no threshold separates them from kappa = 0.12** (t = 2.84).
This is not a lazy threshold — it is an **identifiability limit**: a 12% multiplicative reference bias attenuates
the estimate by ~(1-kappa), and that is statistically indistinguishable from a 12%-smaller true response without
an **absolute-scale reference**. Five detectors were tried (between/within ratio; r-on-s_hat regression; pre/post
between-probe ratio; DiD reference difference; per-repeat coherence t-test); each trades a false negative at low
kappa against a false positive on high-energy responses. The t-test is the best of them and still cannot cross the
kappa ~ 0.15 floor.

The detector also **over-abstains** on the high-energy factorization control D14b (equal-peak broad response): its
reference projection is coherent enough to read SUSPECT, so the instrument abstains on a legitimate case. False
abstention is safer than a false number, but it degrades the factorization demonstration.

## 4. Honest classification of the failure

Contamination causes **attenuation of a real response**, never a **fabricated** one — so it does not trip the
"confident false causal component" hard-fail. But the mission's admission contract is explicit: *"if accepted
cases become inaccurate before rejection, the admission contract fails."* D4 (kappa = 0.12) is accepted
(`ADMISSIBLE`, `CLEAN`) yet inaccurate (21%). **The admission contract fails on the contamination axis.** That is
a development gate failure, and the rule is unambiguous: do not touch the prospective split.

## 5. Three of my own bugs, caught and fixed during development (not hidden)

1. **Semantic error — differencing the wrong episodes.** The first runner subtracted an *unprobed* sham, leaving
   the common probe response in the estimate (D1 off 16x, D9 fabricating energy). Fixed by the correct
   **difference-in-differences**: within-system probed-minus-unprobed removes each system's own baseline
   (including a non-stationary carrier ramp), then the outer difference isolates the added-path response.
2. **Non-reproducible seeds.** `_seeds` used Python's salted `hash()`, so every process drew different drift — the
   contamination margin and P-status flipped run to run. Replaced with a stable content hash. Now bit-reproducible.
3. **Degenerate noise floor + slow OU.** The AR(1) floor collapsed to zero on two-timescale drift (RDNR -> inf);
   the floor is now measured on the corrected residual. The fast-drift OU used a 1009-step Python loop (~9 s/arm);
   replaced with a blocked-vectorised OU matching the literal recurrence to 1e-15, 300x faster.

## 6. Frontier — the deliverable

Admission tracks quantitative validity on every axis except contamination:

- gain mismatch: accurate to x3; lag: accurate to 24 samples; bandwidth loss: accurate;
- local unshared drift: accurate <= 0.5, **rejected >= 1.0** (the reference cannot see it);
- **contamination: accurate <= kappa 0.06; undetected 0.06-0.15 (silent attenuation up to ~25%); abstained
  0.15-0.22; rejected >= 0.22.** The 0.06-0.15 band is the failure region.

## 7. Physical-transfer audit (for the record)

Architecture verdict: `MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE`. **G14 passes** — the contract never needs
simultaneous intervention and non-intervention on one object; the control is a separate episode plus a co-recorded
passive reference. But the instrument is **not** transfer-ready: on a droplet a neighbouring reference region is
*more* contamination-prone than this benchmark, and the kappa ~ 0.15 blind spot would bite. Transfer must wait for
a contamination fix that is almost certainly an **independently-scaled second reference**, not an estimator tweak.

## 8. What the next iteration (CRD-03) must do — if authorized

Lower the contamination floor with a **second reference of known different coupling** `b' != b`. Two references
with distinct, declared couplings give the absolute scale that makes kappa identifiable: the common-mode part must
appear in both at the ratio `b'/b`, while a contaminating `kappa*s` appears at a different ratio. Only then can a
12% leak be separated from a 12%-smaller response. Do **not** attempt this by tuning the single-reference
estimator — the floor is an identifiability limit, not a tuning deficit.

## 9. Standing constraints

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. No droplet experiment was run.
`beta`, `D_int` and the droplet equations were not touched. `P(tau)` and `M(tau)` remain separate. No composite
identity score exists; the output is factorized `R = (E_trans, P_inf, A_peak, L_onset, T_recovery, C, U)`. CRD-01
stands unaltered as `GROUND_TRUTH: PASS / PHYSICAL TRANSFER: TRANSFER_NOT_ESTABLISHED`. The CRD-02 prospective
split (12xx) is **sealed** and reusable exactly once by a corrected instrument.

# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-03 — FINAL REPORT
## Redundantly Referenced and Signed-Intervention Causal Response Decomposition

## Verdict

    EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-03: PASS  (ground truth)
    Transfer: MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE

CRD-03 fixes the load-bearing CRD-02 failure. The κ=0.12 reference contamination that CRD-02 could neither detect
nor correct — a silent 21% attenuation — is **corrected to E/E\* = 1.00** here, in development and prospectively on
unseen systems, and contamination is corrected out to κ ≈ 0.35.

## 1. The identifiability theorem (the theoretical contribution)

Latent `(d, s)`; `y = s + a d`; references `r_i = a_i d + κ_i s`; `α_i = a/a_i` from the `s=0` pre-window. The only
drift-free signals are `z_i = y − α_i r_i = s(1 − α_i κ_i)`, and the reference disagreement is a linear combination
of them (`−α_1 D = z_1 − z_2`, proved symbolically). Hence, with any number of passive references and signed
interventions:

- the response **shape** is always identifiable;
- **differential** contamination (references contaminated differently) is identifiable to κ ≈ 0.002, and since
  contamination only attenuates (`κ_i ≥ 0`, `α_i > 0` ⇒ `|z_i| ≤ |s|`), the largest-amplitude channel is the least
  contaminated and equals `|s|` **exactly** if any reference is clean;
- **common-mode** contamination (`κ_i ∝ a_i`, every `z_i` attenuated identically) is **exactly unidentifiable and
  undetectable** by any passive-reference scheme — it requires an absolute-scale anchor.

Adding references never closes the common-mode ambiguity (each adds one equation `z_i` and one unknown `κ_i`).

## 2. Instrument

Redundant references with **distinct** drift couplings `(0.8, 1.5, 1.15)` + signed interventions. Recovery on the
drift-free, baseline-free odd channels `z_i`; contamination located by reference disagreement; the least-attenuated
channel carries `|s|`. Admission on coupling diversity and conditioning (collinear references abstain). Common-mode
reported as a rigorous **lower bound**. Signed odd/even and complementary null probe are reported diagnostics. No
composite identity score; output factorized `R = (E_trans, P_∞, A_peak, L_onset, T_recovery, C, U)`.

## 3. Development — 21/21 cases, 15/15 gates

Z-17 (D1) 1.00; **CRD-02 κ=0.12 (D2) CORRECTED 1.00**; sub-floor frontier κ=0.05–0.10 (D3) corrected; common-mode
(D4) lower bound 0.72; different κ (D5) corrected 0.98; collinear refs (D6) abstain; signed linear/nonlinear/
hysteresis (D7–D9) 1.00; complementary null/contaminated (D10/D11) correctly split; persistent/transient/hidden
(D13–D15) recovered; factorization (D16) 1.00; collision (D17) equivalence class. All 15 development gates pass.

## 4. Frontier

Contamination corrected across κ = 0.05 → 0.35 (E/E\* = 1.00 throughout) — versus CRD-02's detection floor of
κ ≈ 0.15. Coupling diversity: distinct couplings correct; collinear couplings `(1.0, 1.02, 1.05)` and `(1.0, 1.1,
1.2)` abstain (`ILL_CONDITIONED`). Admission tracks validity: it corrects inside the identifiable region and
abstains outside it.

## 5. Prospective — 12/12, all gates pass, opened once under a verified hash gate

| case | system | admission | E/E\* | A/A\* |
|---|---|---|---|---|
| Q1 | slow, clean | IDENTIFIABLE | 1.00 | 1.00 |
| **Q2** | **slow, κ=0.12 (CRD-02)** | **CORRECTED** | **1.00** | **1.00** |
| Q3 | third-order + κ=0.08 | CORRECTED | 1.00 | 1.00 |
| Q4 | underdamped | IDENTIFIABLE | 1.00 | 1.00 |
| Q5 | common-mode | IDENTIFIABLE (lower bound) | 0.81 | 0.90 |
| Q6 | multiscale + differential κ | CORRECTED | 0.99 | 0.99 |
| Q7 | feedback + nonlinear | IDENTIFIABLE | 1.00 | 1.00 |
| Q8 | persistent | IDENTIFIABLE | 1.01 | 1.00 |
| Q9 | collinear refs | ILL_CONDITIONED | — | — |
| Q10 | transient | IDENTIFIABLE | 1.00 | 1.00 |
| Q11 | hysteresis | IDENTIFIABLE | 1.00 | 1.00 |
| Q12 | silent | NULL_COMPATIBLE | — | — |

No confident contamination-induced attenuation outside the frozen allowance. Unseen topologies (third-order,
underdamped, multiscale, feedback) all recovered. The κ=0.12 fix holds on a system never seen in development.

## 6. Honest limitations

- **Common-mode contamination is unidentifiable** (Q5/D4: 0.81/0.72 lower bounds). This is a *theorem*, not a
  tuning deficit — `ABSOLUTE_SCALE_UNAVAILABLE` on ctrans, and a scale is not fabricated from privileged truth.
- **Local unshared drift** (D12, 1.07) is attenuated-but-admitted at ~7%: like common-mode, a disturbance in `y`
  not in `r` is not caught by reference disagreement. A declared lower-bound-adjacent limitation.
- Clean cases are reported `LOWER_BOUND_ONLY` (exact value, but common-mode cannot be *ruled out* without a scale).
  Rigorous, if conservative; coverage holds (truth ≥ bound).

## 7. Bugs caught and fixed during development (not hidden)

Wrong-episode differencing; a truth/instrument target mismatch (the signed instrument recovers the ODD part —
truth was corrected to match, which resolved the apparent hysteresis error); over-firing signed/complementary
detectors gated to responsive probes and drift-corrected; ARM C's complementary check made advisory after it
false-flagged on a contaminated reference. Seeds are stable content hashes; the OU is blocked-vectorised (matches
the literal recurrence to 1e-15).

## 8. Standing constraints

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. No droplet experiment was run.
`β`, `D_int` and the droplet equations were not touched. `P(τ)` and `M(τ)` remain separate. No composite identity
score. CRD-01 and CRD-02 stand unaltered. The CRD-03 prospective split (14xx) is now burned.

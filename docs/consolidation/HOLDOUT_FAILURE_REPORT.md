# LARGE DISTRIBUTIONAL HOLD-OUT — **FAIL**

Preregistered generator (a76f8a7, N=2000, 12 strata, SNR ∈ {5,15,50}), instrument frozen + hash-gated at 09016d7.
Run once. **STOP RULE INVOKED — failure preserved, instrument NOT patched.**

## Primary safety endpoint
| arm | N | emitted | **INVALID (set excludes truth)** | points | refused |
|---|---|---|---|---|---|
| ORACLE (sign/anchor from truth) | 2000 | 1333 | **541 (40.6%)** | 968 | 667 |
| BLIND (no contracts) | 2000 | 541 | **541 (100%)** | 541 | 1459 |

## Failure mode (single, systematic)
Every invalid case is `POINT_IDENTIFIED` with identified set `{0}` at **SNR = 5**: the instrument's
**null-response gate** (`median(in-window amp) < 2 × median(pre-window amp)`) misfires and declares *no response*
when a real response exists. The set `{0}` then **excludes the true |q|**.

Hand-verified, case i=1 (stratum=amplify, m=8, SNR=5): true |q| = 0.428; in-window amp 0.556 vs 2×null 0.647 →
gate fires → `POINT (0,0)`. A confident claim of zero response against a real response of 0.428.

## Why it was missed
All prior validation ran at high SNR (noise 1e-5–2e-3 against signals ~4e-4–1). The 10-case prospective contained
no low-SNR stratum. The null-gate threshold (factor 2) was never stress-tested against noise-inflated baselines.
**A 10-case prospective passed; a 2000-case stratified hold-out failed immediately.** This is exactly what a large
distributional hold-out is for.

## Scope of the damage
- **The theorems are NOT affected.** T6-A/B/C/D/E have **0 validity violations in 4000 trials** (see
  THEOREM_FAILURE_AUDIT). The failure is an *implementation gate* (null-response detection), not the identifiability
  theory.
- The set-identification logic (POINT/INTERVAL/BOUND/refuse by contract) remains correct wherever a response is
  detected at all.
- The failure is a **false negative** (claiming no response), not a false *magnitude*.

## Required repair (NOT performed here — this hold-out is burned)
A noise-aware detection rule with a declared false-negative rate (e.g. a matched-filter statistic against an
estimated noise floor, with the detection threshold set by a target FNR), developed on **new** development data
and validated on a **fresh** hold-out. This hold-out may not be reused.

## Harness erratum (transparency)
An earlier version of `run_holdout.py` passed `a_i` where the instrument expects `lam_i = 1/a_i`. That was a
**harness** bug and was corrected; `signsafe.py` was never modified (hash-gated throughout). The failure reported
above is present with the corrected harness and is hand-verified.

# EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-02 — PREREGISTERED PROTOCOL
## Referenced Paired-Episode Factorized Causal Response Decomposition

**Committed before any fitting, any frontier sweep, and any prospective system.**

## 1. What CRD-01 proved, and its one fatal limitation

CRD-01 passed in synthetic ground truth. Its acquisition contract required, within each episode, an active channel
and a **simultaneous control channel that was the same system, unprobed** — both seeing one shared drift. That
repaired Z-17. But it is not physically realizable: you cannot intervene and not intervene on one droplet at one
instant. CRD-01 stands as `GROUND_TRUTH: PASS`, `PHYSICAL TRANSFER: TRANSFER_NOT_ESTABLISHED`, and is **not** a
transferred droplet instrument.

## 2. The CRD-02 question

Can the same drift cancellation be achieved with **two physically separate episodes** — one active, one sham,
separated in time on the same object — when **each episode records its own simultaneous common-mode reference
channel**, even though the two episodes see **different drift realizations** (`d_A ≠ d_S`)?

    ACTIVE  y_A = s + base_A + a_A·d_A(t−δ_A) + loc_A·n_A + ε_A ;  r_A = b_A·B[d_A](t−η_A) + κ_A·s + ξ_A
    SHAM    y_S =     base_S + a_S·d_S(t−δ_S) + loc_S·n_S + ε_S ;  r_S = b_S·B[d_S](t−η_S) + κ_S·s + ξ_S

Each episode is corrected against **its own** reference before anything is subtracted:

    ẑ_j = y_j − (g₀·r_j + g₁·r_j(t−λ)),  fitted PRE-INTERVENTION only ;  ŝ = ẑ_A − ẑ_S

## 3. Exact claim (maximum)

When every active and sham episode contains its own simultaneous common-mode reference, factorized causal-response
components can be recovered despite different drift realizations across episodes, **within a declared coupling and
contamination regime**. Conditional on: reference observability; stable within-episode coupling; reference
non-contamination; fixed active/sham timing; declared lag and gain ranges; sufficient reference SNR. It does **not**
claim arbitrary drift removal, transfer to droplets, identity, lineage, life, autonomy, or universal decomposition.

## 4. The reference is NOT an oracle

The reference has finite coupling `b`, delay `η`, noise `ξ`, **bandwidth** `B[·]` (the drift has a fast component,
τ=9, the reference may attenuate or miss), and contamination risk `κ`. `loc_j` injects **local drift that reaches
y and never r** — the part no reference can remove. The synthetic benchmark distinguishes shared environmental
drift, unshared local drift, measurement noise, causal response, and reference contamination. Building a perfect
noiseless copy of the drift and calling it a sensor is explicitly forbidden.

## 5. Candidate contracts (fixed development-only family) and selection rule

- **P1 — separate referenced episodes.** One active, one sham, each with its own reference; correct each, then
  difference. *Assumption:* within-episode coupling stable.
- **P2 — interleaved (S-A-A-S / ABBA).** Same, with a fixed order cancelling slow between-episode baseline drift.
- **P3 — signed referenced interventions.** +u and −u active episodes, each referenced; the odd part is causal.
  *Assumption:* response odd in u (false under saturation).

**Selection rule (fixed here):** pick the **simplest** contract passing all development gates G1–G14 on the Z-17
regression (D1). If more than one passes, prefer the weakest assumption. If none passes, `SCOPE FAILURE`.

## 6. Noise floor and admission — declared

- **Noise floor** is estimated on the **corrected residual** ẑ (not raw y): on ẑ the drift is largely removed, so
  `std(diff ẑ)/√2` recovers the white measurement floor. (An AR(1) form on raw y was tried and is degenerate for
  two-timescale drift — it drives the floor to zero and rejects everything. Verified.)
- **Primary admission = pre-intervention coherence** between measurement and its reference. Coherence is what
  separates a *correctable* reference (gain/lag/bandwidth mismatch: coherence stays high, correction works) from an
  *uncorrectable* one (**local unshared drift**: coherence collapses because y carries a disturbance r never saw).
  Verified on dev: relerr ≤ 5% while coherence ≥ 0.80, climbing past it.
- Thresholds: `COH_MIN = 0.80` → admissible; `0.50 ≤ coh < 0.80` → `INDEPENDENT_RESIDUAL_DRIFT_TOO_HIGH`;
  `coh < 0.50` → `REFERENCE_BANDWIDTH_INSUFFICIENT`; drift below `2·floor` → `DRIFT_ABSENT`.

Statuses: `PAIRED_REFERENCE_ADMISSIBLE`, `ACTIVE_REFERENCE_INVALID`, `SHAM_REFERENCE_INVALID`,
`REFERENCE_CONTAMINATED`, `REFERENCE_BANDWIDTH_INSUFFICIENT`, `INDEPENDENT_RESIDUAL_DRIFT_TOO_HIGH`,
`INSUFFICIENT_REFERENCE_COVERAGE`. **Each episode must pass independently**; if either fails →
`INDETERMINATE — PAIRED REFERENCE INVALID`. One episode is never corrected successfully and the other guessed.

## 7. Contamination — detected on the reference, not the corrected trace

A contaminated active reference `r_A = …+κ·s` makes the correction **silently attenuate** ẑ_A by `(1−g·κ)` — an
attenuated response is indistinguishable from a smaller one, so it cannot be caught in the corrected trace. It is
caught in the **reference channel itself**: a clean reference sees only drift (probe-independent), so any
probe-locked component in the reference's ensemble mean is contamination. Fires at κ≈0.05, silent at κ=0. Verified.

## 8. Baseline contract

Active and sham episodes may have different additive baselines. The instrument separates: additive episode
baseline (nuisance, removed by pre-intervention centring); common-mode time-varying drift (nuisance, removed by the
reference); causal response (accessible); persistent causal offset (accessible). A genuine persistent response is
**not** removed by centring, because the baseline is estimated pre-probe where the response is zero.

## 9. Factorized output — no composite identity score, ever

    R = (E_trans, P_∞, A_peak, L_onset, T_recovery, C, U)

Every component carries point estimate, uncertainty interval, coverage, status, and acquisition-admission result.
Statuses: `ESTIMATED`, `NULL_COMPATIBLE`, `LOWER_BOUND_ONLY`, `UPPER_BOUND_ONLY`, `INDETERMINATE_REFERENCE`,
`INDETERMINATE_WINDOW`, `OUT_OF_SCOPE`.

## 10. Development cases (D1–D15), frontier, gates G1–G14, must-fail 1–15

D1 Z-17 regression (no oracle twin); D2 different episode drifts; D3 independent sham without reference (must fail);
D4 reference contamination; D5 gain mismatch in/out of range; D6 lag mismatch in/out of range; D7 insufficient
bandwidth; D8 local unshared drift (frontier); D9 baseline mismatch only; D10 persistent + baseline; D11 pure
transient; D12 replacement/recovery; D13 hidden state; D14 peak/energy factorization; D15 limited-access collision.

Frontier axes (dev only): reference correlation, SNR, gain mismatch, delay, unshared local drift fraction,
contamination, active/sham baseline mismatch, causal amplitude, measurement noise. **Admission must track
quantitative validity** — if accepted cases become inaccurate before rejection, the admission contract fails.

## 11. Physical-transfer audit (before freeze) and G14

Every measurement the selected contract needs is classified against the frozen droplet engine. **G14: the contract
must not require simultaneous intervention and non-intervention on the same physical object.** Verdicts:
`PHYSICALLY_PLAUSIBLE_MAPPING`, `MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE`, `MAPPING_REQUIRES_ORACLE_ACCESS`,
`COMMON_REFERENCE_NOT_AVAILABLE`, `TRANSFER_NOT_ESTABLISHED`. Oracle access → scope failure, no freeze. A passive
observable may be *proposed* but **not** added to the droplet engine in this mission.

## 12. Splits

New dev/prospective split (dev `11xx`, prospective `12xx`). No system-name overlap. Prospective generated only
after freeze, opened exactly once. Development code is structurally prevented from loading prospective acquisitions.

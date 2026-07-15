# H2-CERT-01 — Preregistration (certification only; C1c frozen)

## Frozen configuration
C1c verbatim (eta_w0.015, eta_d1 0.35, eta_d2 0.006, eta_t0.010, D_m0.010, lam_plus0.25, lam_minus0.15,
k_exp1.0, k_up1.0). Protocol: warm(C0)→erase→2-phase history (T=60, band[0.003,0.02])→settle20→relabel all
material OLD→forward C1c+PulseChase. h1=a_e+a_l, h2=a_l−a_e. No physics/param/metric changes after seal.

## Checkpoints (turnover)
Primary: first valid checkpoint with M≤0.25 → step 650 (M≈0.20, from pilot). Secondary: M≈0.44 (step 300),
M≈0.28 (500), M≈0.15 (800). Report #reaching each, #censored, #viability-lost.

## Representations (frozen DIST features: mean/std/p10/p50/p90 of m1,m2)
Whole entity; OLD material (cohort0>0.5 cells); NEW material (cohort1>0.5 cells). Global controls: size, mass,
m1/m2/m+/m− means, old-fraction. No cohort/age/label enters dynamics (analysis only).

## Decoder
PRIMARY: train on development (pilot dev at matched checkpoint) → test ONCE on sealed prospective (no refit).
Secondary (labelled): grouped within-prospective leave-history-out. Nulls: constant, h1-only, global-means-only,
permutation. Donor-grouped bootstrap CIs. No row-LOO.

## Decision rules (all at M≤0.25, prospective, held-out)
- RETENTION (Q1): h2 R² ≥ 0.50 AND lower CI bound > 0.50.
- NEW-MATERIAL (Q2): new-material-only h2 R² ≥ 0.50 AND lower bound > 0.50.
- CAUSAL (Q3): only if retention passes — deep-turnover cloned branches R0(active)/R1(memory-inert)/R2(m+ only)/
  R3(m− only)/R4(h2-dispersion destroyed)/R5(clone); h2 response R² ≥ 0.50, lower bound > 0, collapses under R1/R4.
- INDEPENDENCE (Q4): incremental h2 R² > 0 after conditioning on h1, global means, size/mass, old-fraction, seed.
- CROSS-FAMILY: point estimates must not swing across seed families/thresholds.
- h1 must stay above threshold; viability preserved; no leakage.

## Sample (power-frozen)
Sealed prospective 4 seeds × 12 histories (48 donors) to step 650. Train-decoder from dev pilot.

## Decision matrix → mission §16. If retention lower bound ≤ 0.50 → FAIL (Outcome C/D) → CLOSE h2 escalation.
Even if INDETERMINATE, project decision = CLOSE unless every load-bearing gate passes. No further h2 cert afterward.

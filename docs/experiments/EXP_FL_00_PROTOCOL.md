# EXP_FL_00 — Frozen Protocol: Flow-Lenia substrate + field-stack qualification (no law search)

Status: **FROZEN.** Preregistered by `RUN-20260710-2030-EXPFL00`. Authorized by D-021 (retire Particle Dynamics;
Flow-Lenia candidate confirmed by user). No broad law search until this gate passes.

## QUESTION
Does a minimal fixed-law mass-conservative Flow-Lenia core plus a field-adapted detector/tracker/P/M stack
qualify — mass-conservative, passive-tracer-invariant, deterministic, reference-path-verified — and does the frozen
measurement philosophy (EXP-REF-01 positive control) hold on the new field stack?

## CORE (minimal, fixed-law, mass-conservative)
Single channel field A>=0 on a periodic grid. Potential U = K*A (radial shell kernel, sum-normalized, periodic FFT
convolution). Concentration-limited flow F = (1-alpha)*grad(U) - alpha*grad(A), alpha = clip((A/theta)^n,0,1).
Mass transported by forward-bilinear reintegration tracking (weights depend only on F -> mass conserved exactly;
nonnegativity preserved). Global fixed parameters; NO parameter localization, evolution, resource collection,
mutation, or multi-species.

## PASSIVE TRACERS / COHORTS
C cohort fields transported by the IDENTICAL operator (same F, same bilinear weights). They never enter U, the
affinity, the flow, or the update; by construction sum_c cohort_c == A at all times (linear operator preserves the
partition). Verified: A evolves identically with vs without cohorts.

## FIELD MATERIAL RETENTION M(tau) (preregistered before results)
For a tracked entity with cohort masses m_c^t = sum over its cells of cohort c: M(tau) = sum_c min(m_c^t,
m_c^{t+tau}) / sum_c max(m_c^t, m_c^{t+tau}). This is the field analogue of the particle ID Jaccard; 1 = unchanged
origin composition, ->0 = full constituent turnover.

## FIELD PHENOTYPE / P (frozen philosophy, NOT recalibrated)
Detector: threshold A and take periodic connected components (>= min_cells). Association: the FROZEN geometry/size
LineageTracker (IDs unused). Phenotype: ID-independent geometric (mass fraction, radius of gyration, anisotropy,
radial quantiles) + dynamical (center velocity, velocity dispersion, internal circulation) descriptors from the
mass field and the flow field, with P = exp(-RMS(dPhi)) -- the SAME formula as CORE V0. Descriptor scales are
DECLARED (length 10 cells, speed 1), not tuned to results. No composite score. P is NOT recalibrated to pass.

## EXP-REF-01 RERUN ON THE FIELD STACK
Reference = a scripted persistent dissipative organization: fixed mass blob (persistent phenotype), rigid rotation
velocity field (circulation), gradual cohort turnover. Static-flux null = identical blob, rotation OFF, zero
velocity. Both fed to the field stack. RECOGNIZED = detected as a single continuous track with P>0.8 and a
probe-positive (P>0.8, M<0.5) endpoint. SEPARATED = reference mean |circulation| and velocity dispersion each
> 0.02 while the null has both < 1e-6 (raw P/M identical for both).

## QUALIFICATION GATE (frozen, binary)
PASS iff ALL: mass_conservation (<1e-9 rel drift), nonnegativity, cohort_partition_preserved (<1e-9), determinism
(exact), passive_tracer_invariance (exact), reference_path_agreement (FFT vs direct conv <=1e-9),
detector_tracker_on_real_dynamics (a track of length >=3 on real Flow-Lenia dynamics), expref01_recognized,
expref01_separated.

## DECISION
- PASS -> the Flow-Lenia field stack is qualified; preregister and autonomously launch EXP_FL_01 as a BLIND
  low-discrepancy regime map under the same five evidence levels and causal discipline (no composite, thresholds
  frozen, P/M separate, same-state causal intervention carried over).
- FAIL -> do not launch EXP_FL_01; report the failing check and stop for audit.

## VALIDATION / REPRODUCTION
`pytest tests/test_exp_fl_00.py`; `edlab.experiments.exp_fl_00.qualify()`.

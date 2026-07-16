# Authoritative PRESEAL candidate — LCI-CAUSAL-TURNOVER-PRESEAL-03C

## Status: NOT AUTHORIZED, NOT EXECUTED, NOT SEALED BY THE OPERATOR

This file is the canonical statistical and experimental specification. The Claude 03A addenda are retained as
historical repair records, but they are not authority for execution. No `54xxx` seed has been run. Claude's
“GO FOR SEAL” is a design recommendation only and is not human authorization.

The prospective runner remains fail-closed until it receives a separate approval JSON bound to the exact committed
Git blob of `TURNOVER_EXECUTION_MANIFEST_03C.json`. The committed approval template has `authorized: false`.

## 1. Scientific question and boundaries

**Question.** Does target-specific causal information remain available after deep material turnover in the passive-
copy C1c architecture, and is the information stored locally rather than recoverable equally from a geometric
neighbour, a target-memory-masked environment, or body variables?

The experiment does not establish or claim identity, individual memory, reproduction, heredity, active
reconstruction, or evolution. The direct feeding contrast is secondary because the frozen equation already couples
`m_plus` to uptake.

## 2. Frozen engine and geometry

- Engine: `MultiChannelMemoryEngine`, C1c
  (`eta_w=0.015`, `eta_d1=0.35`, `eta_d2=0.006`, `k_exp=1.0`,
  `lam_plus=0.25`, `lam_minus=0.15`; all other `MCParams` defaults unchanged).
- Targets: exactly 3, each at least 45 cells, periodic pairwise separation at least 24.
- Histories: two local Gaussian nutrient phases, each 60 steps, amplitudes independently drawn from
  `[0.005, 0.035]`; primary label is cumulative own dose `a1+a2`.
- Rest settle: 120 steps.
- Deep threshold: each target has measured passive-cohort material retention `M_i <= 0.25`.
- Turnover cap: 1500 steps.
- Assay: frozen non-fusing uniform probe `0.25 x 5`, 40-step response horizon, 40-step N-standardisation settle.
- Tracker: frozen bijective tracker. Diagnostic cohorts and IDs never enter physics, association, or decoder
  features.

## 3. Exact seed family, hard cap, and activation

| tier | seeds | count | rule |
|---|---:|---:|---|
| primary | `54001-54050` | 50 | execute all after one valid human approval |
| reserve | `54051-54096` | 46 | sequential activation only after all primary seeds complete and fewer than 18 valid worlds exist |
| total | `54001-54096` | 96 | absolute hard cap; no extension |

Minimum valid worlds: **18**. “Valid” is frozen as: geometrically eligible, deep snapshot reached without an
invalidating continuity event, and both rest and deep contrast batteries pass their predeclared geometry-only assay
validity checks.

Reserve activation reads only this feasibility projection:

`seed, eligible, deep_reached, rest_assay_valid, deep_assay_valid, valid, reason`.

It cannot read dose labels, response values, decoder values, causal contrasts, memory features, or any other
endpoint. The code returns and persists `endpoint_fields_used: []`. Reserve seeds run in ascending order and stop
when 18 valid worlds are reached or seed 54096 is exhausted. If fewer than 18 valid worlds exist at the hard cap,
the result is feasibility failure and no scientific verdict is issued.

The fixed cap of 96 retains Claude's corrected Beta-Binomial predictive value
`P(N_valid >= 18) = 0.93` under the declared Jeffreys-prior model. The family repair is now internally exact:
50 primary + 46 reserve = 96 total. There is no second reserve outside the hard cap.

## 4. Persisted event evidence and continuity exclusions

The first tracker censor invalidates the world permanently. No daughter or replacement component is selected.
The engine continues for exactly five evidence-only frames, which cannot restore eligibility.

Persisted evidence includes parent sizes and masses, component sizes, the complete parent-to-component overlap
matrix, best-component claimants, descendant matching fractions, and local mass ratios. Frozen classification:

| raw tracker event | persisted criterion | class |
|---|---|---|
| `SPLIT` | at least two daughters each cover >=0.30 of the parent and remain separately matchable at >=0.10 for all five follow-up frames | `FISSION` |
| `SPLIT` | split criterion does not persist for all five frames | `TRANSIENT_FRAGMENTATION` |
| `MERGED` | two or more parent tracks claim the same component, with the overlap matrix retained | `MERGE` |
| `LOST` | local mass remains above 0.20 of its event-frame reference in any follow-up frame | `LOSS` |
| `LOST` | local mass is at or below 0.20 for all five follow-up frames | `DEATH` |
| `AMBIGUOUS` | frozen tracker near-tie | `AMBIGUOUS` |

All classes remain feasibility events only. No reproduction or heredity interpretation is authorized.

## 5. Lambda-plus-only and full ablations

The primary manipulation control sets `lam_plus=0` while retaining `lam_minus=0.15` and every other `MCParams`
value. A full `lam_plus=lam_minus=0` branch is persisted separately. The two are never conflated:

- `ablate_plus`: tests the uptake readout while preserving the attractant channel;
- `ablate_full`: tests both readout channels together;
- `erase_ablate_plus`: local erasure under the lambda-plus-only control.

## 6. Frozen label and access scopes

Every decoder uses the **same target label**: that target's own cumulative dose. Feature extraction occurs at the
deep snapshot before any deep causal assay. The scope extractor does not accept dose or history labels.

### L — target-local memory

11 features from target cells:

`m1 mean/std/p10/p50/p90`, `m2 mean/std/p10/p50/p90`, `std(m1-m2)`.

### N — geometric-neighbour comparator

The same 11 definitions, taken from the periodic-distance nearest neighbour. This replaces the invalid
`(i+1) mod K` label comparator.

### P — target plus neighbouring droplets

33 features: L for the target, then the same 11 features for the nearest and farther neighbours, ordered only by
pre-outcome periodic geometry.

### E — environment with target memory masked

The complete target-centred physical field stack
`rho, U/rho, V/rho, c, N, uptake, m1, m2`, with `m1` and `m2` set to exactly zero on the target mask before
persistence. All other fields and all non-target memory remain unchanged. The target mask is persisted so the zero
operation is auditable.

### G — complete target-centred world

The same full field stack without masking. Periodic translation centres the target; no rotation, feature selection,
dimension reduction, or endpoint-dependent preprocessing is allowed.

### B — body/environment baseline

Eight target-region features:

`cell_count, rho_mass, rho_mean, rho_std, mean(U/rho), mean(V/rho), mean(N), mean(c)`.

Diagnostic cohort field `C`, IDs, labels, and outcome values are excluded from all scopes. E and G are persisted as
compressed float64 arrays with SHA-256 sidecar hashes. L/N/P/B are persisted with exact feature names.

## 7. Authoritative grouped inference

Implementation: `experiments/individuation/turnover_statistics.py` and
`experiments/individuation/turnover_ownership_analyze.py`.

1. Unit of inference: original world/seed.
2. Outer validation: leave one original world out.
3. Every row from the held-out world is test-only; no original world can appear in both train and test.
4. Ridge lambda is fixed at `1.0`.
5. Scaling is learned on the training worlds only.
6. No hyperparameter, feature, coordinate, or decoder is selected after endpoints are observed.
7. Each held-out world produces one normalized mean-squared loss. The normalization denominator is the training-
   world target variance, never test-world variance.
8. Confidence intervals are Student-t intervals over original-world fold scores.
9. A secondary bootstrap resamples the already-fixed original-world fold scores. It never refits a decoder and
   never relabels duplicated worlds.
10. Order / `m_minus` is secondary only. There is no max-over-coordinate switch.

The primary target-local storage gate requires all four lower 95% bounds to exceed zero:

- L improves over the training-mean intercept;
- L has lower held-out loss than N;
- L has lower held-out loss than E;
- L has lower held-out loss than B.

P and G are co-reported access scopes:

- P improving over L indicates pair/neighbour access beyond target-local memory;
- G improving over L indicates additional world-level information;
- G improving over E quantifies the incremental information restored by the target memory channels.

A successful G decoder is evidence of global informational content, not by itself evidence of local storage. Local
storage requires the L gate above. If E performs comparably to L, the result is redundant/environmental access and
the local-storage gate fails.

## 8. Secondary causal and mechanistic diagnostics

The intact, sham, neighbour erasure, lambda-plus-only, full ablation, and fixed-mask readouts are reported. Their
interpretation remains secondary because the direct `m_plus -> uptake` multiplier predicts a feeding contrast.
Claude's DEV diagnostics (`n=4` feasible worlds), including algebraic, `eta_w=0`, `up_ref=0`, copy-disabled, and
L/P/E/G calculations, remain exploratory only and cannot become prospective claims.

`up_ref=0` tests only that named global reference. It cannot exclude every distributed pathway.

## 9. Manifest-bound human authorization

`TURNOVER_EXECUTION_MANIFEST_03C.json` binds the exact canonical protocol, runner, analysis, scope extractor, event
evidence classifier, seed manifest, and tests by committed Git blob IDs. Execution requires a separate approval
artifact containing:

- `authorized: true`;
- `one_execution_only: true`;
- the exact execution-manifest Git blob;
- the exact approval phrase;
- a non-empty authorization ID, human approver, and UTC timestamp.

The committed template is intentionally invalid for execution. Creating a human-approved artifact later changes
neither code nor statistical specifications. This is a procedural authorization boundary, not a cryptographic
signature.

## 10. Stop conditions and reporting

- No `54xxx` seed before explicit human approval.
- No code, feature, seed, gate, or statistical change after the execution manifest is sealed.
- No extension past seed 54096.
- Fewer than 18 valid worlds at the cap: feasibility failure, no endpoint verdict.
- All seeds, invalid worlds, event evidence, sidecar hashes, fold audits, and fixed-fold losses are reported.
- No unsealed turnover result enters the V4.1 abstract, results, or conclusion.

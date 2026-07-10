# EXP02-COREV0-20260710-001 — Broad Regime Map

**Status:** PREREGISTERED BEFORE EXECUTION.

## Objective

Map the continuous joint distribution `(P(tau),M(tau))` for CORE V0 after the repaired baseline's candidate failed corrected fresh-seed hold-out.

## Sampling

- 300 deterministic Halton LawSpecs, indices `0..299`, skip already fixed at 32 inside the sampler.
- Three screening seeds per law: `{2001,2002,2003}`.
- 900 runs total.
- Three seeds are screening only and never an estimate of `P(event|law)`.

## Fixed world/run/observer settings

- 64 particles, 3 types, unit periodic box.
- `dt=0.02`, 600 steps, simulated time 12.
- vectorized backend fixed and exact-SHA validated against scalar force and one-step paths.
- observer cadences `{10,30,60}`.
- detector, phenotype, tracker, lags, nulls, P, M, and initial probe unchanged from baseline 002.

## Predeclared screening candidate rule

A LawSpec becomes eligible for a separate fresh-seed protocol only if, in at least two of three screening seeds, the same physical endpoint is probe-positive under at least two cadences and each contributing cadence independently has a track with at least eight observations and no split, merge, or ambiguity anywhere.

All qualifying rows retain unresolved sparse-alias/static-flux risk. Eligibility is only permission for direct audit/hold-out, not evidence.

## Required analysis

- full continuous P/M distribution and descriptive correlation with pseudoreplication warning;
- probe occupancy, but no post-hoc threshold change;
- Pareto boundary and density;
- dependence on tau, cadence, tracker flags, law parameters, lifetimes, split/merge, and turnover;
- candidate-edge and raw descriptor audit for any eligible law;
- right-censored interpretation of non-emergence by simulated time 12.

## Storage policy

EXP02 must use a streaming/chunked writer. Full raw association, observation, event, and measurement tables may live under an ignored `raw/` directory with checksums and schema/index committed. Commit LawSpecs, manifest, summaries, aggregates, figures, candidate rows, checksums, and exact regeneration commands. Do not attempt a multi-gigabyte in-memory list or an absurd Git commit.

## Stop conditions

- Do not execute until the streaming artifact path is implemented and tested against the baseline runner on a small equivalence fixture.
- Do not proceed to hold-out until EXP02 completes and the predeclared rule is applied.
- Do not change substrate or add density/orbital mechanisms during EXP02.


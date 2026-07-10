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

### Frozen execution artifact contract

- The recovery unit is one immutable `(law_index, seed)` directory under `raw/runs/`; each contains the unchanged measurement, lineage-event, entity-observation, and association-edge CSV streams plus its own manifest.
- The experiment plan hash fixes code SHA, configuration, law indices, seeds, and schema before the first shard.
- A shard becomes committed only by same-parent atomic directory rename after its files and per-run manifest are flushed. Unpublished temporaries after abrupt termination are quarantined and logged, never counted as completed runs.
- Every resume verifies byte size, SHA-256, and actual CSV row count before reusing a shard. Plan drift or any raw/index/derived mismatch stops rather than repairs silently.
- Derived files are atomically replaced. The root `manifest.json` is published last and may say `status=COMPLETE` only for 900/900 verified runs with consistent raw index, row totals, hashes, output sizes, and regeneration command.
- Raw shards remain local and Git-ignored. Their committed checksums prove integrity of files that are present; they are not represented as a remote backup.
- Execution remains sequential for this first broad screen. Storage/recovery changes do not authorize a physics, detector, tracker, observable, threshold, or substrate change.

## Stop conditions

- Do not execute until the streaming artifact path is implemented and tested against the baseline runner on a small equivalence fixture.
- Do not proceed to hold-out until EXP02 completes and the predeclared rule is applied.
- Do not change substrate or add density/orbital mechanisms during EXP02.

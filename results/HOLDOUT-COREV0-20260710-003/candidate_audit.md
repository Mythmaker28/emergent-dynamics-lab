# Initial Probe Candidate Audit

## OBSERVED

- Probe definition was not changed: `P > 0.8, M < 0.5`.
- Probe rows: 30 / 5885.
- Unique cadence-scoped tracks with a probe row: 12.
- Rows without a complex lineage event inside their measurement interval: 17.
- Rows on tracks with no split, merge, or ambiguous-association event anywhere: 15.
- Such rows on tracks with at least 8 observations: 15 across 3 tracks.
- Clean long-track probe endpoints reproduced as probe-positive at the same physical endpoints under at least two cadences: 3 endpoints (6 cadence rows).

## INFERRED

- Raw probe occupancy alone is not evidence because the mandatory static-flux null also occupies it.
- Logged lineage complexity explains some but not necessarily all probe rows; the track-clean subset requires fresh-seed hold-out before any mechanistic interpretation.

## HYPOTHESIS

- Some track-clean rows may be static occupancy or look-alike stitching not captured by the current event log, rather than self-maintaining organization.

## WHAT WOULD FALSIFY THIS?

- Frozen fresh-seed hold-out, cadence consistency, and controlled perturbation can reject candidate laws.
- Direct trajectory audit showing stationary spatial occupancy with constituent flow would support the null explanation.

## Caveat

Rows repeat tracks, overlapping windows, cadences, and lags. Counts are descriptive, not independent evidence. Track-clean means no logged split, merge, or ambiguous association anywhere on that track under that cadence.

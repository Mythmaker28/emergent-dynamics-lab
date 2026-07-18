# Frozen Longitudinal Tracker Specification (TCA-01)

Purpose: follow ONE entity through turnover without reselecting by size. Uses only geometric/material overlap;
NEVER h1, h2, M target, history labels, decoder output, or desired result.

- **Initialization:** at t0 (post-history relabel) the tracked entity = the single largest connected component.
- **Matching:** at each update step, among all detected components choose the one maximizing mask overlap
  |cells ∩ prev_tracked_cells| (periodic connected-component detection makes wrapped entities single components,
  so set-intersection overlap is periodic-correct).
- **Prediction:** none (entities are near-stationary; centroid drift per step ≪ 1 cell). Overlap matching suffices.
- **Minimum-overlap threshold:** 0.1 of the previous tracked size. Below it → TRACK LOST.
- **Split policy:** if the tracked mask fragments, the max-overlap fragment continues; if none clears 0.1 → LOST.
- **Merge policy:** if the tracked entity merges into a larger component, the max-overlap component continues
  (overlap remains high). This is recorded as a MERGE event but not censored unless overlap later drops.
- **Ambiguity rule:** if two components tie on overlap within 10%, mark AMBIGUOUS and censor the track there.
- **Track-loss / censoring:** on LOST or AMBIGUOUS the track is CENSORED (no reassignment to another blob).
  Longitudinal metrics are reported only for surviving, uncensored tracks.
- **Determinism:** frozen; depends only on the frozen C1c trajectory. Matching every 5 steps (entities move
  ≪1 cell/step; verified equivalent to every-step on the incident trajectory).
- **Forbidden inputs:** h1, h2, M, size-target, cohort labels, history labels, decoder outputs.

Backward comparison: the historical rule (`largest(st)` each frame) is retained only as an audit baseline
(`--track largest`) and is explicitly NOT longitudinal.

# HOLDOUT-COREV0-20260710-003 — Corrected Diagnostic Fresh-seed Protocol

**Frozen before execution and after correcting the cross-cadence clean-track join.**

## Parent baseline

`BASELINE-COREV0-20260710-002`, with unchanged initial probe `P>0.8,M<0.5`.

## Corrected selection semantics

For the same physical start/end steps, at least two cadences must each independently satisfy all conditions:

1. probe-positive row;
2. cadence-scoped track has at least eight observations;
3. that cadence-scoped track has no split, merge, or ambiguous association anywhere.

The endpoint condition must occur in at least two distinct screening seeds. Under this corrected join, exactly law index `3` qualifies (screening seeds `101` and `303`).

## Execution

- Law index: `{3}`.
- New unseen seeds: `{909,1010,1111,1212,1313}`.
- Five runs, 64 particles, 600 steps, `dt=0.02`, cadences `{10,30,60}`.
- All physical, detector, tracker, phenotype, lag, backend, and threshold settings unchanged.
- Full association edges and interval flags persisted.

## Frozen diagnostic disposition

Law 3 passes the recurrence gate only if at least two of five fresh seeds contain a qualifying endpoint under the corrected rule. This is not a probability estimate.

If fewer than two qualify, the 12-law baseline signal is not robust under this gate. Keep the result negative and proceed to the preregistered broad EXP02 map; do not lower thresholds or substitute another law from the invalidated hold-out.

Even if two or more qualify, every row retains static-flux/look-alike alias risk and requires dense trajectory audit plus controlled perturbation before any mechanistic promotion.

## Disposition appended after execution

**COMPLETED — NEGATIVE UNDER FROZEN GATE.** One of five fresh seeds (`909`) qualifies; the required threshold was at least two. Law 3 is rejected for perturbation preparation under this protocol. This count is not interpreted as an event probability. The result does not invalidate Particle Dynamics; it closes only the 12-law baseline candidate path and authorizes the preregistered broad EXP02 screen.

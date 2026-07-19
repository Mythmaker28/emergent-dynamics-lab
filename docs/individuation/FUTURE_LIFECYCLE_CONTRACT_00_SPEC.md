# FUTURE-LIFECYCLE-CONTRACT-00 — frozen source-only specification

## Mission boundary

This qualification defines a lifecycle closure contract for a future, entirely new family. It does not diagnose,
repair, reconstruct, relabel or add output to the closed Stage-B family. The only historical facts admitted are the
two committed reports. No generic failure path identified below is attributed to any historical world.

The implementation consumes only the generic tracker output: track records, track events, assignments and an
explicit ordered schedule of sampled frames. It must not consume matter fields, physics, candidate labels,
classifications, laws, seeds or outcomes.

Association-edge diagnostics remain separately persisted tracker-audit evidence and do not enter lifecycle-state
assignment. The lifecycle-input digest therefore binds the complete ordered schedule plus tracks, events and
assignments, not the association-edge payload. A future raw package must bind those edge diagnostics under its own
generic tracker schema; their omission here must not be described as a digest of all `TrackingResult` fields.

## Contract

Let `F=(f_0,...,f_H)` be a non-empty, strictly increasing schedule. For every observed track `i`, let `b_i` and `e_i`
be the first and last scheduled frames containing a track point. A qualified run contains exactly one terminal row
per track:

1. If `e_i=f_H`, the row is `RIGHT_CENSORED_AT_HORIZON` and is evidenced by the declared schedule.
2. If `e_i<f_H`, exactly one tracker event at the immediately following scheduled frame must consume `i` as a
   source. Its kind must be `DISSOLUTION`, `SPLIT`, `MERGE` or `TRACKING_UNRESOLVED`; the corresponding terminal
   state is recorded.
3. A source-ending event must cite the source's last component. Its targets, if any, must begin at the event frame,
   exist as tracks, and carry reciprocal parent/child links.
4. Every target created by a split, merge or unresolved transition is itself subject to this same closure rule.

Therefore, after structural validation, the terminal-state function is total and single-valued. A missing,
duplicate, conflicting, temporally displaced or dangling terminal event makes the whole contract invalid; the
validator never infers closure from absence.

## Event algebra

| Event | Source cardinality | Target cardinality | Lifecycle role |
|---|---:|---:|---|
| `APPEARANCE` | 0 | 1 | onset only |
| `CONTINUATION` | 1 | 1, same track | neither onset nor termination |
| `TEMPORARY_CONTACT` | exactly 2 | same tracks | neither onset nor termination |
| `DISSOLUTION` | 1 | 0 | terminal |
| `SPLIT` | 1 | at least 2 | source terminal; target onset |
| `MERGE` | at least 2 | 1 | every source terminal; target onset |
| `TRACKING_UNRESOLVED` | at least 1 | at least 1 | source terminal; unresolved target onset |

An appearance or a lineage-producing event must supply exactly one onset for every track. Track points must occupy
contiguous positions in `F`; numeric `frame+1` is never used, so non-unit sampling cadence is unambiguous.

## Raw binding and publication kill switch

The qualified document is canonical JSON, schema-versioned, and binds SHA-256 digests of the complete generic
track/event/assignment input and the complete terminal-row table. A zero-track run is represented explicitly by a
qualified run closure with zero counts; it is not an absent file.

For any future family, a world cannot be marked complete or enter scientific analysis unless qualification succeeds,
the lifecycle file is written atomically, and independent verification recomputes identical canonical bytes and
digests from the same generic tracker output. Any absent or non-matching lifecycle file invalidates that future
world. This gate is not applied retrospectively.

## Frozen synthetic qualification

Qualification must cover: horizon censoring, dissolution, split, merge, unresolved transitions, late appearance,
zero tracks, non-unit cadence, canonical order invariance, round-trip verification, and fail-closed malformed cases
including silent pre-horizon termination, multiple terminal events, temporal gaps, invalid schedules, dangling
IDs, incorrect cardinalities, missing or duplicate onsets, reciprocal-link errors, assignment mismatch, target-frame
mismatch, unknown event kinds and post-terminal evidence.

No engine, world constructor, scientific seed, historical shard or current-family output may be used.

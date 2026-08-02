# FUTURE-LIFECYCLE-CONTRACT-00 — source-only and synthetic qualification

## Disposition

**FUTURE_LIFECYCLE_CONTRACT_QUALIFIED**

The future-only closure primitive, strict raw schema, canonical serialization and atomic non-overwriting publication
path pass source-only and hand-built synthetic qualification. For every structurally valid future tracker input, the
validator emits exactly one explicit terminal row per track. Any missing, duplicate, conflicting, temporally invalid
or dangling lifecycle witness invalidates the complete future run.

This is not a lifecycle analysis of the closed Stage-B family. No shard, shard name, per-world metadata, failed
autopsy input, current-family trajectory or candidate record was opened. No current-family output was reconstructed,
retrofitted or created, and no generic path below is attributed to the accepted historical failure.

## Qualified contract

The sole admitted input is an ordered sample-frame schedule plus generic `TrackRecord`, `TrackEvent` and assignment
rows. Matter fields, engine state, laws, seeds, regime labels, candidates and outcomes are absent. Association edges
remain separate generic tracker-audit evidence and are intentionally not part of the lifecycle-state digest.

For every track `i`, exactly one of the following rows is required:

| Terminal state | Mechanical witness | Permitted claim |
|---|---|---|
| `DISSOLVED_DETECTED_TRACK` | resolved `DISSOLUTION`, 1→0 | the detector track ended explicitly; not physical death |
| `SPLIT_INTO_TRACKS` | resolved `SPLIT`, 1→at least 2 | the source track ended and named successor tracks began |
| `MERGED_INTO_TRACK` | resolved `MERGE`, at least 2→1 | each source track ended into the named successor |
| `UNRESOLVED_HANDOFF` | unresolved event, at least 1→at least 1 | tracking became explicitly unresolved; no forced identity |
| `RIGHT_CENSORED_AT_HORIZON` | last point at the declared final sample | observation ended while the track remained detected |

Every successor is recursively subject to the same closure rule. A nonempty ordered frame schedule is mandatory;
adjacency is defined by schedule position, never numeric `frame + 1`. A valid zero-track run persists an explicit
`EMPTY_TRACK_SET` run closure with zero counts.

The canonical JSON document binds SHA-256 over the complete lifecycle input — schedule, tracks, events and
assignments — and over the complete sorted terminal table. Independent verification recomputes both the semantic
document and its exact canonical bytes.

## Generic fail-closed paths

The static audit identified generic contract paths that could otherwise leave lifecycle state implicit:

- a track ending before the declared horizon with no source-ending event;
- a source-ending event at the wrong scheduled transition;
- split, merge or unresolved targets absent from assignments or reciprocal lineage;
- a horizon survivor left without an explicit right-censoring row;
- a new or malformed event kind entering without declared lifecycle polarity;
- duplicate component ownership, conflicting assignments or evidence after termination;
- a publication conflict, noncanonical document, tampered digest or substituted temporary file.

All are rejection paths in the qualified validator. These are generic source properties only and are not evidence
about which path, if any, affected a historical run.

One future integration limitation is explicit: the current generic tracker derives the event frame for an empty
right detector frame from transition position. Under non-unit sampling, that can differ from the declared schedule.
The contract correctly rejects the mismatch; hand-built non-unit continuation tests do not qualify that empty-frame
integration path. A future family must retain the rejection or repair and separately requalify the tracker API.

## Synthetic evidence

- Lead combined run: **61 passed, 0 failed, 0 skipped** — 50 lifecycle fixtures plus 11 existing generic
  detector/tracker fixtures; no scientific engine update.
- Syntax compilation, JSON parsing and Git whitespace checks: pass.
- Positive coverage: empty run, late appearance, non-unit cadence, horizon censoring, dissolution, split, merge,
  one-to-many and many-to-many unresolved handoff, temporary contact and generic tracker integration.
- Negative coverage: silent end, point gap, wrong transition, missing onset/continuation, duplicate/conflicting
  terminals, unknown kinds/IDs, link mismatch/cycle, unresolved mismatch, assignment conflict, noncanonical/tampered
  document and invalid frame types.
- Publication coverage: existing-target refusal, simultaneous target creation, unique owned temporary files,
  temporary-path substitution, identity-owned cleanup and canonical-byte reread.
- Two independent reviewers each reran the exact 50-test lifecycle suite and returned `PASS`; the formal reviewer
  independently proved the total single-valued closure mapping.

Machine-readable evidence and exact hashes are in
`FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json`.

## Claim boundary and future binding

Qualified now:

- lifecycle accounting is total and single-valued for inputs that pass the structural validator;
- silent or ambiguous closure is mechanically rejected;
- canonical output and the tested atomic publication primitive are source-only and outcome-independent.

Not qualified:

- the cause of any historical failure or any lifecycle state of the closed family;
- detector/tracker physical correctness, individuality, ownership, life or physical death;
- a non-bypassable integration in a future runner that does not yet exist.

For a future, entirely new family, `COMPLETE` and scientific analysis must be impossible unless the writer invokes
this primitive, persists the canonical contract, and an independent verifier reproduces the bindings. Until that
separate integration is implemented and qualified, the architecture supplies a qualified gate but does not claim an
installed future-family state machine.

The only next action is human review of this future lifecycle contract. The closed current family remains permanently
non-diagnostic for lifecycle analysis; no second autopsy or retrofit is authorized.

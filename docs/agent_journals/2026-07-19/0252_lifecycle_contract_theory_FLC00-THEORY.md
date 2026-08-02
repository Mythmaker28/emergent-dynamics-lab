# FUTURE-LIFECYCLE-CONTRACT-00 theory audit

- Role: independent lifecycle-contract theorist
- Run ID: `FLC00-THEORY`
- Start: 2026-07-19 02:52:07 +02:00
- End: 2026-07-19 02:54:17 +02:00
- Starting Git state: branch `codex/future-lifecycle-contract-00`, HEAD `389dac1127e3035cdf195c1905965832a299ad6d`, clean
- Ending Git state: HEAD unchanged at `389dac1127e3035cdf195c1905965832a299ad6d`; shared worktree contained this journal and two other agents' new journals, with no implementation file modified by this role
- Assigned scope: derive an exhaustive future-only closure mapping for generic `TrackRecord` / `TrackEvent` data and a declared observation horizon. No implementation edits.

## Evidence firewall

Allowed and read:

- generic detector/tracker/event definitions in `edlab/substrates/lattice_bond/instrumentation.py`;
- committed Stage-B report;
- committed Stage-B autopsy report.

Not opened or enumerated:

- the 64 Stage-B physics shards or their filenames/metadata;
- manifests, failed-autopsy inputs, current-family trajectories/candidates, runners, results, engine state, or scientific worlds.

This audit identifies generic contract failure modes only. It makes no claim that any such path caused the accepted historical failure. The current family remains non-diagnostic for lifecycle analysis.

## OBSERVED

The generic event algebra is finite:

`APPEARANCE`, `CONTINUATION`, `SPLIT`, `MERGE`, `TEMPORARY_CONTACT`, `DISSOLUTION`, and `TRACKING_UNRESOLVED`.

The source creates a new track on `APPEARANCE`, and also creates new tracks as targets of `SPLIT`, `MERGE`, and `TRACKING_UNRESOLVED`. A one-to-one `CONTINUATION` appends a point to the same track. The source logs `DISSOLUTION` for an unmatched source. `TEMPORARY_CONTACT` deliberately does not merge identities. The committed autopsy report is fail-closed on a missing explicit lifecycle termination, while preserving `DEV_FEASIBILITY_FAIL`; it does not authorize a causal diagnosis.

## Formal lifecycle closure contract

Let `F = (f_0, ..., f_H)` be the complete, strictly increasing declared observation schedule for a future world and let `f_H` be its final frame. A final frame alone is insufficient if cadence gaps are permitted; either persist `F` explicitly or declare and validate contiguous integer frames.

For every track `t`, let `P_t` be its nonempty sequence of unique points, ordered by `F`. Define:

- birth-event kinds `K_B = {APPEARANCE, SPLIT, MERGE, TRACKING_UNRESOLVED}`, where `t` is a target;
- terminal-event kinds `K_T = {DISSOLUTION, SPLIT, MERGE, TRACKING_UNRESOLVED}`, where `t` is a source;
- `B(t)` as all birth events targeting `t`;
- `X(t)` as all terminal events sourcing `t`.

Mandatory terminal mapping:

| Condition | Machine terminal state | Successors | Scientific meaning explicitly excluded |
|---|---|---|---|
| exactly one `DISSOLUTION` source event | `DISSOLVED_DETECTED_TRACK` | empty | not proof of physical destruction |
| exactly one `SPLIT` source event | `SPLIT_INTO_TRACKS` | all event targets | not proof of organismal reproduction |
| exactly one `MERGE` source event | `MERGED_INTO_TRACK` | event target | not proof that material identity ceased |
| exactly one `TRACKING_UNRESOLVED` source event | `UNRESOLVED_HANDOFF` | all event targets | no continuity claim across the handoff |
| no terminal source event and `last(P_t) = f_H` | `RIGHT_CENSORED_AT_HORIZON` | empty | not persistence beyond `f_H` |
| any other case | no terminal row; world qualification fails | n/a | inference is forbidden |

### Event polarity and arity

Qualification must validate the generic source algebra rather than trusting event strings:

| Kind | Sources | Targets | `resolved` | Lifecycle role |
|---|---:|---:|---|---|
| `APPEARANCE` | 0 | 1 | true | target birth |
| `CONTINUATION` | 1 | 1, same track ID | true | nonterminal |
| `SPLIT` | 1 | at least 2 | true | source terminal, target births |
| `MERGE` | at least 2 | 1 | true | all sources terminal, target birth |
| `TRACKING_UNRESOLVED` | at least 1 | at least 1 | false | all sources terminal, target births |
| `DISSOLUTION` | 1 | 0 | true | source terminal |
| `TEMPORARY_CONTACT` | 2 distinct IDs | same 2 IDs | true | nonterminal |

### Necessary invariants

1. **Schedule integrity.** Every point/event frame belongs to `F`; `F` includes the declared final frame and has no undeclared gap.
2. **Track integrity.** Track IDs are unique; every track has at least one point; its frames are strictly increasing; no component key belongs to two tracks.
3. **Exactly one onset.** `|B(t)| = 1`; the birth frame and target component equal the first point. `APPEARANCE` implies no parents; `SPLIT`/`MERGE`/`TRACKING_UNRESOLVED` imply parents exactly equal event sources.
4. **Stepwise continuity.** Each non-first point has exactly one `CONTINUATION` event from the immediately preceding scheduled frame, with the same track ID and matching source/target component keys. Track points cannot skip an observation.
5. **Exactly one close or censor.** `|X(t)| <= 1`. If `|X(t)| = 1`, its frame is the immediate successor in `F` of the last track point, and the source component is that last point. If `|X(t)| = 0`, the last point must be at `f_H`.
6. **No afterlife.** A terminal event has no source-track point at or after its event frame and no later continuation of that ID.
7. **Lineage equality.** For a source terminal event, `child_track_ids` equals its targets for `SPLIT`, `MERGE`, and `TRACKING_UNRESOLVED`, and is empty for `DISSOLUTION`/horizon censoring. For every target born in a lineage event, `parent_track_ids` equals all event sources. No dangling source, target, parent, or child ID is allowed.
8. **Unresolved witness.** `TrackRecord.unresolved` is true exactly when the track participates as a source or target in at least one `TRACKING_UNRESOLVED` event. This is a tracker-status witness, not a physical-state label.
9. **Event exhaustiveness.** Every event obeys the polarity/arity table and maps to recorded point keys. Unknown event kinds fail qualification; they may not default to disappearance.
10. **Canonical one-row output.** The terminal ledger contains exactly one row per unique track ID, sorted canonically, with a one-to-one `track_id` key. `terminal_count == track_count` is binding. Duplicate or missing rows fail qualification.
11. **Empty-world explicitness.** A world with no tracks may qualify only with a world-level `EMPTY_TRACK_SET` status, declared schedule/final frame, and zero terminal rows; it must not be silently omitted.
12. **Atomic publication gate.** Future-family raw completion/classification is forbidden unless the schedule, event ledger, track table, lineage metadata, and terminal ledger pass together. A lifecycle failure invalidates the future world package rather than assigning a guessed terminal state.

## Minimal raw terminal row

Each future terminal record should persist at least:

- schema version and future-world identifier;
- `track_id`;
- onset kind, onset event index, onset frame, and parent track IDs;
- first and last observed frames/components;
- terminal state, terminal frame, terminal event index or explicit horizon witness;
- successor track IDs;
- `resolved` and `right_censored` booleans;
- declared final frame and observation-schedule digest;
- event-ledger digest and canonical terminal-ledger digest.

`terminal_event_index` must be null only for `RIGHT_CENSORED_AT_HORIZON`; `right_censored` must be true only for that state. A raw schema should use closed enums and reject extra/unknown terminal-state strings.

## Exhaustiveness and uniqueness proof sketch

For any validated track `t`, invariant 5 yields `|X(t)|` in `{0,1}`. If it is one, the single event belongs to the exhaustive finite set `K_T` and therefore maps to exactly one of four event-backed terminal states. If it is zero, invariant 5 requires the last point at `f_H`, yielding exactly the horizon-censored state. The event-backed and censoring cases are disjoint because the latter requires `|X(t)| = 0`. Thus every validated track has one and only one terminal state. Any record outside the cases cannot be made total without inference, so the entire future-world lifecycle qualification fails closed.

This proof concerns completeness of tracker lifecycle accounting only. It does not prove detector sensitivity, physical persistence, individuality, death, reproduction, or historical cause.

## Generic silent-termination-capable contract paths

These are abstract paths the gate must reject, not claims about prior data:

- a pre-horizon last point without a terminal source event;
- an omitted horizon-censor row for a final-frame track;
- a declared horizon beyond the last persisted observation;
- a point gap hidden by a later continuation;
- two conflicting terminal events for one source;
- a terminal event whose frame is delayed relative to the next scheduled observation;
- a split/merge/unresolved event with orphan or mismatched lineage metadata;
- an ambiguous handoff labelled resolved or coerced into a continuation;
- a child created without exactly one onset witness;
- writer filtering that drops tracks, events, or terminal rows after validation;
- an unknown future event kind silently treated as dissolution.

## INFERRED

A per-track terminal enum alone is insufficient. The guarantee requires a complete observation schedule, event polarity/arity validation, point-to-event chronology, lineage equality, and an atomic raw-package gate. These checks are source/schema properties and can be qualified using synthetic hand-built lifecycles without opening any scientific world.

## HYPOTHESIS

If the future writer emits the canonical terminal ledger only after the complete contract passes, then silent track termination becomes mechanically impossible in an admitted future-family package: it is either represented by one explicit terminal state or the package is rejected.

## WHAT WOULD FALSIFY THIS?

- A generic tracker transition that ends a source track but is not expressible by the seven declared event kinds.
- A valid lifecycle in which a source has two simultaneous, semantically distinct terminal events that cannot be represented as one event with multiple targets.
- A writer path that can publish/classify a future world without passing the atomic lifecycle qualifier.
- A schedule representation that permits missing frames while still satisfying the declared-schedule checks.
- Synthetic mutation tests that delete/duplicate/reorder lifecycle evidence yet still qualify.

## Synthetic qualification recommendations

Positive fixtures: empty world; appearance-at-horizon; continuation then horizon censoring; explicit dissolution; split with all children closed; merge with all parents closed; unresolved one-to-one and many-to-many handoffs; temporary contact without closure; later independent appearance.

Negative/mutation fixtures: silent early end; missing/duplicate onset; missing continuation; internal frame gap; duplicate terminal events; wrong event arity/polarity/resolved flag; terminal frame mismatch; point after terminal; unknown/dangling IDs; parent/child mismatch; component double assignment; false horizon censor; unclosed child; unknown enum; terminal-row omission/duplication; noncanonical ordering; post-validation writer filtering.

Determinism: permute input track/event order and require byte-identical canonical terminal output; change only diagnostic IDs and require unchanged physics (the contract itself must run after tracking and cannot feed engine/detector/tracker decisions).

## Failures/dead ends

None. No historical data or outcome-bearing artefact was opened.

## Decisions

Recommend a future-only fail-closed lifecycle qualifier with a closed five-state terminal algebra and an explicit observation schedule. Do not retrofit or diagnose the closed Stage-B family.

## Unresolved risks

- The existing generic source assumes frame semantics in places; the future contract should accept an explicit schedule rather than infer cadence from event integers.
- `DISSOLUTION` is only a detector/tracker disappearance label; documentation must prevent physical-death reinterpretation.
- The guarantee is defeated if validation is advisory or if the writer can mutate/filter after validation.

## Handoff

Delivered the closure theorem and fixture recommendations to the parent agent. Recommended acceptance condition: synthetic tests establish the theorem’s invariants and mutation kill switches, and the future raw schema makes the terminal ledger a binding atomic publication gate.

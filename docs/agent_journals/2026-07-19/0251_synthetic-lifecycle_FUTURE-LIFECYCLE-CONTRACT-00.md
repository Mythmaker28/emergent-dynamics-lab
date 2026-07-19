# FUTURE-LIFECYCLE-CONTRACT-00 — synthetic qualification reviewer journal

- Role: independent adversarial synthetic-fixture reviewer
- Run ID: `FUTURE-LIFECYCLE-CONTRACT-00-SYNTHETIC-REVIEW`
- Start: 2026-07-19 02:51:20 +02:00
- End: pending parent integration
- Starting Git branch: `codex/future-lifecycle-contract-00`
- Starting Git HEAD: `389dac1127e3035cdf195c1905965832a299ad6d`
- Starting worktree: clean
- Assigned scope: design, but do not implement, an adversarial synthetic qualification matrix for a future-only exhaustive per-track lifecycle contract.

## Scope and evidence firewall

Only these committed sources were inspected:

- `edlab/substrates/lattice_bond/instrumentation.py`, limited to generic detector/tracker data structures and tracker event construction;
- `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_REPORT.md`, by a targeted source/schema/lifecycle term query;
- `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_STAGE_B_AUTOPSY_REPORT.md`, by the same targeted query.

No Stage-B shard, shard name, manifest, result tree, current-family metadata, trajectory, candidate record, engine, runner, scientific module, or autopsy input was listed or opened. No scientific execution occurred. The matrix below tests a future contract only. It does not infer which generic path, if any, occurred in the closed historical family.

## OBSERVED

The generic tracker emits immutable `TrackRecord` and `TrackEvent` objects. Its event vocabulary is `APPEARANCE`, `CONTINUATION`, `SPLIT`, `MERGE`, `TEMPORARY_CONTACT`, `DISSOLUTION`, and `TRACKING_UNRESOLVED`.

The generic event construction gives these structural meanings:

| Event | Source tracks | Target tracks | Ends source track? |
|---|---:|---:|---:|
| `APPEARANCE` | 0 | 1 | no |
| `CONTINUATION` | 1 | 1, same track | no |
| `TEMPORARY_CONTACT` | exactly 2 | same IDs | no |
| `DISSOLUTION` | 1 | 0 | yes |
| `SPLIT` | 1 | 2 or more | yes |
| `MERGE` | 2 or more | 1 | yes |
| `TRACKING_UNRESOLVED` | 1 or more | 1 or more | yes for every source; each target begins a distinct unresolved track |

`TrackRecord` itself has no terminal-state field. A run that stops while a track is present therefore needs a separate explicit censoring closure. An `unresolved=True` flag is not by itself a terminal event: an unresolved target can have later points and needs its own eventual terminal record.

## INFERRED contract shape

The smallest exhaustive future contract has five mutually exclusive terminal states:

1. `DISSOLUTION`
2. `SPLIT`
3. `MERGE`
4. `TRACKING_UNRESOLVED`
5. `HORIZON_CENSORED`

Each terminal record should carry at least `track_id`, `terminal_state`, `last_observed_frame`, `terminal_frame`, and sorted unique `successor_track_ids`. The first four are backed by exactly one matching terminal event. `HORIZON_CENSORED` is backed by the track's presence in the declared last sampled frame and has no successor.

The envelope must declare an ordered, unique sample-frame schedule, not merely an integer horizon. Temporal adjacency is adjacency in that schedule. This keeps cadence explicit and permits a machine-verifiable distinction between a legal next sampled frame and a gap even when simulation-step values are not consecutive integers.

Required global identities:

- `terminal_record_track_ids == track_record_track_ids`;
- exactly one terminal record per track;
- every source in a terminal event has the matching terminal record;
- no nonterminal event generates a terminal record;
- every terminal event target exists and starts at the event frame;
- every pre-horizon track end has an explicit terminal event at the immediately next declared sample;
- only a track observed at the final declared sample may be `HORIZON_CENSORED`;
- terminal successor IDs equal the event target IDs and the track's child IDs;
- target parent IDs reciprocally equal the terminating source IDs for split, merge, and unresolved handoff.

## Adversarial synthetic qualification matrix

All fixtures are hand-built tracker records/events. No engine state is needed.

### Expected-pass fixtures

| ID | Synthetic construction | Required result |
|---|---|---|
| P00 | Declared nonempty frame schedule, no tracks, no events | valid empty terminal table; exact zero-count coverage identity |
| P01 | One track appears at first sample, continues through last sample | one `HORIZON_CENSORED` record |
| P02 | One track appears late and is present at last sample | one `HORIZON_CENSORED`; late appearance is not a gap |
| P03 | One track disappears at the next declared sample with a 1-to-0 `DISSOLUTION` | one `DISSOLUTION`; last-observed and terminal frames remain distinct |
| P04 | One source splits into two targets at the next sample; both targets reach horizon | source `SPLIT`; two target `HORIZON_CENSORED` records |
| P05 | Two sources merge into one target; target later dissolves | two `MERGE` records pointing to the same successor; successor `DISSOLUTION` |
| P06 | One-to-many unresolved handoff, then each unresolved target reaches horizon | source `TRACKING_UNRESOLVED`; each target independently `HORIZON_CENSORED` |
| P07 | Many-to-many unresolved handoff, then mixed successor endings | every source `TRACKING_UNRESOLVED`; each target gets its own later closure |
| P08 | Temporary contact between continuing tracks | contact does not close either track; both close only at horizon or later terminal events |
| P09 | Non-unit sample schedule, e.g. 0, 5, 10, with continuation at each declared sample | valid; adjacency follows schedule, not numeric `+1` |
| P10 | A track appears only at the final declared sample | valid `HORIZON_CENSORED` with equal last-observed and terminal frame |
| P11 | Valid records/events supplied in multiple tuple orders | identical normalized records and canonical bytes |

### Expected-fail fixtures

| ID | Defect | Required stable diagnostic |
|---|---|---|
| F00 | No declared sampled frame at all | invalid envelope/horizon; an empty run cannot establish a censoring boundary |
| F01 | Duplicate track ID | duplicate-track error before lifecycle inference |
| F02 | Track with zero points | empty-track-points error |
| F03 | Negative, non-integer, boolean, or out-of-schedule point frame | invalid-point-frame error |
| F04 | Points are duplicated, decreasing, or supplied out of temporal order | nonmonotonic-points error; do not silently sort malformed history |
| F05 | Same track skips a declared sampled frame and then resumes under the same ID | gapped-track error |
| F06 | Two tracks claim the same `(frame, component_index)` | duplicate-assignment error |
| F07 | Track starts without `APPEARANCE` or a split/merge/unresolved target event | missing-origin error |
| F08 | Root track has nonempty parent IDs, or a lineage child also has an appearance event | origin/lineage conflict |
| F09 | `CONTINUATION` changes track ID, cardinality, or resolved polarity | malformed-continuation error |
| F10 | `TEMPORARY_CONTACT` changes IDs, has a terminal record, or is unresolved | malformed-contact/nonterminal-closure error |
| F11 | Dissolution has a target, multiple sources, or `resolved=False` | malformed-terminal-event error |
| F12 | Split is not 1-to-at-least-2 | malformed-terminal-event error |
| F13 | Merge is not at-least-2-to-1 | malformed-terminal-event error |
| F14 | Unresolved handoff has an empty side or `resolved=True` | malformed-terminal-event error |
| F15 | Terminal event occurs at the same sample as, before, or more than one declared sample after the source's last point | terminal-timing error |
| F16 | Terminal target's first point is not at the terminal event frame | target-onset error |
| F17 | Event or point lies after the declared last sample | after-horizon error |
| F18 | Source continues or participates as a source after a terminal event | post-terminal-evidence error |
| F19 | One track has two identical terminal events | duplicate-event and multiple-terminal errors; never deduplicate |
| F20 | One track has conflicting terminal events, such as split plus dissolution | conflicting-terminal error |
| F21 | A pre-horizon track ends with only nonterminal events or no event | missing-terminal-state error; no implicit dissolution |
| F22 | A pre-horizon track is labelled `HORIZON_CENSORED` | invalid-censoring error |
| F23 | A horizon-present track is labelled as a non-event terminal state | terminal-record/event mismatch |
| F24 | Event or terminal record references a missing successor | dangling-track-reference error |
| F25 | Existing successor starts correctly but parent/child fields do not reciprocate | lineage-mismatch error |
| F26 | Source appears among its own successors or ancestry graph contains a cycle | self/cyclic-lineage error |
| F27 | Terminal record successor list differs from event targets, is unsorted, or has duplicates | terminal-record mismatch; canonicalizer must not hide semantic duplicates |
| F28 | Two event rows reuse the same source/target component key inconsistently | component/event consistency error |
| F29 | Track has `unresolved=True` but no unresolved origin/source event and no other basis | unresolved-provenance error |
| F30 | Unresolved target is treated as already terminal solely because of its flag | missing-own-terminal error for that target |
| F31 | Mixed-invalid fixture: bad horizon, duplicate ID, dangling successor, missing terminal | complete, stably ordered error set independent of input ordering |
| F32 | Unknown event kind or unknown terminal-state token | closed-enum/schema error; fail closed |
| F33 | Extra undeclared field in the raw terminal record | strict-schema error if `additionalProperties: false` is the contract |
| F34 | Non-canonical numeric/string type for IDs or frames | strict-type error; booleans must not pass as integers |

## Canonical serialization qualification

Canonical bytes should be defined rather than inherited from incidental Python ordering. At minimum:

- UTF-8 JSON, fixed key order, fixed separators, a single declared trailing-newline policy;
- terminal rows sorted by numeric `track_id`;
- successor arrays already validated as unique and serialized in numeric order;
- no floating-point fields in the lifecycle table;
- schema/contract version included in the envelope;
- identical bytes under permutations of input track records, events, and internally unordered parent/child collections;
- repeated invocation on the same value yields identical bytes;
- decoding and re-encoding a valid canonical document is byte-identical;
- a valid semantic document in noncanonical byte form is either normalized before publication or rejected by a dedicated canonical-byte validator; the choice must be explicit.

## Deterministic error precedence

Avoid order-dependent early exits. The validator should collect all mechanically reachable violations, normalize their references, and sort them by a committed precedence plus `(track_id, frame, event_index/reference)`.

Recommended precedence classes:

1. envelope/schema/type and frame-schedule validity;
2. unique IDs, nonempty records, point ordering and assignment uniqueness;
3. event enum, polarity, cardinality and duplicate-row validity;
4. referenced-track existence and reciprocal lineage;
5. origin and continuation temporal consistency;
6. terminal timing, conflicting terminals and post-terminal evidence;
7. horizon censoring and exhaustive terminal coverage;
8. emitted-record/schema/canonical-byte identity.

Fixture F31 should be permuted across at least 20 deterministic permutations and must yield the same ordered violation tuple. If the public API raises only one exception, its first code must be selected from this precedence after full validation, and the machine-readable report should still retain the complete ordered tuple.

## HYPOTHESIS

A future runner that publishes only after this validator returns a bijective, canonical terminal table can make silent per-track termination mechanically impossible within the persisted tracker record/event model.

## WHAT WOULD FALSIFY THIS?

- A synthetically constructed track can end before the final sampled frame without a terminal event and still receive a valid terminal table.
- A terminal source or target can be absent, temporally inconsistent, or lineage-inconsistent while validation passes.
- A horizon-censored record can be assigned to a track not observed at the last declared sample.
- Reordering semantically identical inputs changes canonical bytes or error order.
- A newly added tracker event kind can enter the raw schema without an explicit terminal/nonterminal classification and still validate.

## Failures/dead ends

The first full-file read of the generic instrumentation source was truncated by the terminal output limit. A subsequent exact line-range read covered the complete tracker data structures and event-construction path needed for this review. No broader search was used.

## Decisions and unresolved risks

- Do not infer closure from `TrackRecord.unresolved`, missing observations, the final world regime, or disappearance alone. Closure must be an explicit event or explicit horizon censoring.
- A scalar `final_frame` is insufficient to validate gaps under non-unit cadence. The future raw envelope needs the ordered sampled-frame schedule, or an equivalent declared cadence plus exact start/end from which that schedule is unambiguously derived.
- If the implementation accepts only a final-frame integer, tests P09 and F05 cannot be correctly distinguished; qualification should fail or the contract should be revised.
- This contract guarantees lifecycle-accounting completeness, not tracker correctness, physical identity, or a diagnosis of any closed family.

## Handoff

Implement the validator/generator in a new generic future-only module, leave the frozen Stage-B pipeline untouched, run only hand-built fixtures matching this matrix, and require a canonical machine-readable coverage identity before any future new family can publish raw output.

- Ending Git state: journal added; implementation and tests untouched by this reviewer.

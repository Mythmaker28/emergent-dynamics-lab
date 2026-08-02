# EMPTY-RIGHT-NONUNIT-CADENCE-TRACKER-REPAIR-00 — report

## Part I — FROZEN SEMANTIC CONTRACT

This part is frozen **before any source is edited**. It is committed alone, and the qualification in Part II must
cite and compare against this commit. Nothing in Part I may be silently revised; a required deviation is a reason
to return `TRACKER_REPAIR_INSUFFICIENT`, not to edit this section.

**No source file had been modified when this was committed.**

### 1. Authority and scope

- Human-review branch: `codex/future-prospective-readiness-architecture-00-human-review`
- Human-review commit: `f7b6c9797dc6bdfc969ddf5c3421bef9991e339c`
- Disposition: `HUMAN_REVIEW_ACCEPTED`; accepted architecture disposition `ARCHITECTURE_REVISE`
- Accepted ancestry: `4282fc6` → `23df99d` → `9d13e9b` → `f8b8288` → `d1f57ff` → `f7b6c97`, strictly linear,
  zero merges
- This branch: `codex/empty-right-nonunit-cadence-tracker-repair-00`

**Scope.** Source-only engineering. No engine, no scientific runner, no historical physics, no feasibility
simulation, no parameter sweep, no autopsy, no scientific analysis, no seed. Synthetic detector frames and
handcrafted tracker inputs only.

### 2. Exact defect hypothesis (confirmed against the API before freezing)

`edlab/substrates/lattice_bond/instrumentation.py`, inside `track_components`, contains:

```python
right_frame = right[0].frame if right else transition_index + 1
```

When the right detector frame is **empty**, `right_frame` falls back to `transition_index + 1` — a **position in
the transition sequence**, not a frame number. Every event emitted for that transition, in particular the
`DISSOLUTION` event that records a disappearance, is stamped with that positional surrogate.

`track_components(frames, spec)` receives only `Sequence[Sequence[DetectedComponent]]`. When a frame's component
list is empty there is **no `DetectedComponent` carrying its frame number**, so the function has, in its present
signature, **no admissible source for the actual right frame**. It fabricates one.

**Confirmed empirically on the accepted parent source, using only synthetic fixtures already present in the
permitted test suite:**

| Input | Declared schedule | Emitted events | `qualify_lifecycle_contract` |
|---|---|---|---|
| one component at frame 0, empty right frame | `(0, 1)` — unit cadence | `APPEARANCE@0`, `DISSOLUTION@1` | **QUALIFIES**, terminal state `DISSOLVED_DETECTED_TRACK` at frame 1 |
| **identical** tracker input | `(0, 5)` — non-unit cadence | `APPEARANCE@0`, `DISSOLUTION@1` | **REJECTED**: `INVALID_EVENT_FRAME`, `SILENT_PRE_HORIZON_TERMINATION`, `TERMINAL_COUNT_MISMATCH` |

The emitted dissolution frame is `1` in both cases because it is `transition_index + 1`. At unit cadence from
origin 0 that number coincides with `sampled_frames[1]`; at any other cadence or origin it does not, and the
lifecycle validator correctly refuses an event frame that is absent from the declared schedule.

**This is the survivorship mechanism, in one line.** Identical physics, identical tracker input, different
declared cadence, opposite lifecycle outcome — and the rejection is correlated with the **outcome**
(disappearance) rather than with anything about the validity of the measurement. Surviving entities never produce
an empty right frame and are therefore never rejected. Disappearing entities are.

### 3. Terminology (frozen — these six things are distinct and may never be conflated)

| Term | Meaning |
|---|---|
| **transition index** `i` | position of a left/right pair in `zip(frames[:-1], frames[1:])`; `0`-based |
| **schedule position** | index into `sampled_frames`; the right side of transition `i` is position `i + 1` |
| **physical / simulation frame number** | the integer a `DetectedComponent` carries in `.frame` |
| **left observed frame** | `sampled_frames[i]`; equals `left[0].frame` when `left` is non-empty |
| **right observed frame** | `sampled_frames[i + 1]`; equals `right[0].frame` when `right` is non-empty |
| **terminal event frame** | the frame stamped on a terminal `TrackEvent` (`DISSOLUTION`, `SPLIT`, `MERGE`, `TRACKING_UNRESOLVED`) |
| **analysis horizon** | `sampled_frames[-1]` |

### 4. Correct event-frame invariant (frozen)

> **I-1.** For a transition between declared sampled frames `sampled_frames[i]` and `sampled_frames[i+1]`, every
> event emitted for that transition — and in particular any disappearance first established by an empty right
> detector frame — is stamped with the **actual right frame `sampled_frames[i+1]`**, never with `i+1`, never with
> `left_frame + 1`, and never with any other derived positional surrogate.
>
> **I-2.** Every emitted event frame is a member of the declared schedule.
>
> **I-3.** No frame number is ever fabricated. If the actual right frame cannot be obtained from the inputs, the
> tracker must not guess.

The lifecycle validator already expects exactly this: it computes `expected_terminal_frame = frames[last_position
+ 1]`, i.e. the next scheduled frame after the track's last observed frame. The repair makes the tracker agree
with a contract that was already correct.

### 5. Empty-right semantics (frozen)

When the right detector frame is empty, every left-side track with no outgoing association edge terminates. The
event kind is **`DISSOLUTION`**, which the frozen lifecycle contract already maps to terminal state
**`DISSOLVED_DETECTED_TRACK`**. **No new event kind is introduced.** The existing taxonomy is demonstrably capable
of representing disappearance, so introducing one would trigger `TRACKER_REPAIR_INSUFFICIENT`.

Disappearance is **explicit, counted lifecycle information**, not a reason to discard the run.

### 6. Unit-cadence compatibility requirement (frozen)

Unit-cadence outputs must be **bit-identical** to the accepted parent. Every currently passing synthetic fixture
must produce the same events, tracks, edges and assignments, unless this contract explicitly predicts a
difference. It predicts none for unit cadence.

**A binding constraint discovered before implementation and recorded here so it cannot look like a post-hoc
excuse.** Two files that this mission is **forbidden to modify** already pin the defective behaviour as expected:

- `tests/test_future_lifecycle_contract.py:878` — `track_components(((_component(0),), ()), tracker)`
- `tests/test_future_lifecycle_runner_integration.py:83` — the `_empty_right_nonunit` fixture, consumed by
  `test_21_empty_right_frame_at_nonunit_cadence_remains_rejected`, which asserts `INVALID_EVENT_FRAME` **and**
  `SILENT_PRE_HORIZON_TERMINATION`.

Both call the tracker **without** a declared schedule. Therefore any repair that changes the behaviour of the
**no-schedule** call path breaks hash-bound tests in forbidden files, and would require
`TRACKER_REPAIR_INSUFFICIENT`. The repair must therefore be **additive on the call signature**, and Part II must
state honestly and prominently how much of the survivorship mechanism that leaves open.

### 7. Irregular-cadence requirements (frozen)

The repair must be correct for schedules that are strictly increasing but otherwise arbitrary: non-unit constant
cadence, irregular gaps, non-zero origin, and very large frame numbers. At least one test schedule must be chosen
so that `i + 1`, `left_frame + 1` and the actual right frame `sampled_frames[i + 1]` are **three different
numbers**, so that a positional mutant cannot pass by coincidence.

A supplied schedule must be validated: same length as `frames`, integer, non-negative, strictly increasing. A
malformed schedule is rejected, never silently repaired.

### 8. Lifecycle acceptance requirements (frozen)

For an admissible synthetic pre-horizon disappearance the repaired tracker's output must:

1. pass `qualify_lifecycle_contract` against the declared schedule;
2. yield **exactly one** terminal lifecycle state for the disappearing track;
3. yield terminal state `DISSOLVED_DETECTED_TRACK` at the **actual** scheduled frame;
4. produce **no** global rejection;
5. keep the disappearing track in the enrolled denominator — it is counted, not dropped;
6. remain exhaustively accounted for when several tracks disappear and others survive.

### 9. Horizon semantics (frozen)

Four cases must be distinguished and separately demonstrated:

| Case | Required treatment |
|---|---|
| valid pre-horizon terminal event followed by at least one further declared observation | terminal event at the actual scheduled frame; run qualifies |
| disappearance first detected exactly at the declared horizon (the track's last point is at `sampled_frames[-2]`, the empty frame is `sampled_frames[-1]`) | terminal event at `sampled_frames[-1]`; this is a **pre-horizon terminal event by the contract's definition**, because the *track* did not reach the horizon |
| a track whose last observed point is at the horizon | `RIGHT_CENSORED_AT_HORIZON`; it must **not** also carry a terminal event, or `TERMINAL_AT_HORIZON` fires |
| a track that ends before the horizon with no terminal event | `SILENT_PRE_HORIZON_TERMINATION` — must remain a violation |

**Replacing `INVALID_EVENT_FRAME` with `TERMINAL_AT_HORIZON` and declaring victory is explicitly forbidden.** The
admissible demonstration required by this contract has an entity present, disappearance detected at a later
non-unit frame, **at least one subsequent declared observation**, exactly one terminal state, no global rejection,
and the disappearance retained in the denominator.

### 10. Test matrix (frozen — fifteen required cases)

1. one entity on the left, empty right frame, unit cadence
2. the same case at cadence greater than one
3. irregular cadence
4. non-zero schedule origin
5. very large frame numbers
6. multiple left-side entities and an empty right frame
7. one disappearing track while another survives
8. disappearance followed by later empty observations
9. disappearance at the final sampled transition
10. split immediately before a later empty frame
11. merge immediately before a later empty frame
12. malformed or non-increasing schedules
13. event-frame membership in the declared schedule
14. determinism and canonical ordering
15. unchanged unit-cadence behaviour for existing synthetic fixtures

### 11. Mutation matrix (frozen — ten required mutants)

1. restore the old `transition_index + 1` fallback
2. use `left_frame + 1`
3. use unit-cadence-only arithmetic
4. emit no terminal event when the right frame is empty
5. close only the first of several disappearing tracks
6. use the final horizon frame regardless of the actual transition
7. accept an event frame absent from the schedule
8. shift the event one schedule position late
9. convert disappearance into successful completion
10. allow a silent pre-horizon termination

Each mutant must be killed by a **named** test, rejected structurally, or explicitly classified as equivalent or
out of scope. **A surviving outcome-dependent rejection mutant is a blocker.**

### 12. File allowlist (frozen — exactly six)

Modify: `edlab/substrates/lattice_bond/instrumentation.py`; `tests/test_lattice_bond_instrumentation.py`.
Add: `tests/test_empty_right_nonunit_cadence_tracker_repair.py`;
`docs/individuation/EMPTY_RIGHT_NONUNIT_CADENCE_TRACKER_REPAIR_00_REPORT.md`;
`..._QUALIFICATION.json`; `..._REVIEW_JOURNAL.md`.

Do not modify `lifecycle.py`, `future_lifecycle_runner.py`, their existing tests, either JSON Schema, package
exports, any historical report or qualification, or any runner. If any of those must change, stop with
`TRACKER_REPAIR_INSUFFICIENT`.

### 13. Terminal dispositions (frozen)

`TRACKER_REPAIR_QUALIFIED` · `TRACKER_REPAIR_INSUFFICIENT` · `STOP_TRACKER_REPAIR`.

`TRACKER_REPAIR_INSUFFICIENT` if the tracker alone cannot close the survivorship mechanism without changing
lifecycle or integration source. `STOP_TRACKER_REPAIR` on scientific-data access, engine execution, historical
retrofit or scope violation. After any terminal disposition the only authorized next action is human review.

### 14. Downstream hash consequences (frozen)

`instrumentation.py` is hash-bound at `f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88` by
`FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json` and, transitively, by the runner-integration and hardening
qualifications. The moment this mission changes that file, three distinct statuses must be separated and never
conflated:

| Status | Meaning |
|---|---|
| **historically valid** | the qualification is true of the source hash it was computed against, and remains true of that commit forever |
| **behaviourally compatible** | the same tests still pass under the repaired source |
| **formally current** | the qualification may be cited as binding for future-runner use |

This mission may claim **only** the tracker repair as formally current. It must **not** claim that the lifecycle
contract qualification, the future-runner integration qualification or the hardening qualification remain formally
current after the source change. An explicit requalification DAG is required in Part II.

---

*Part II (read ledger, repair, evidence, mutation matrix, regression binding, requalification DAG, independent
reviews and terminal disposition) is appended after this contract is committed. This file's state at the
pre-implementation commit is the frozen reference.*

---

## Part II — EXECUTION RECORD

Part I above was frozen and committed alone at `04d2d31002e2a72b96ce0dd5f9df14c6a9ac3f04`, before any source was touched
(`git diff --name-only f7b6c97 04d2d31 -- edlab tests` returned nothing). Everything below was produced against that
frozen contract and did not amend it.

### 15. Diagnosis confirmed before the repair

The defect was reproduced on the accepted parent with byte-identical detector input at two cadences. The tracker input is
one component at schedule position 0 and an **empty** right detector frame at schedule position 1.

| declared schedule | emitted DISSOLUTION frame | `qualify_lifecycle_contract` |
|---|---|---|
| `(0, 1)` | `1` | QUALIFIED — terminal `DISSOLVED_DETECTED_TRACK` @ 1 |
| `(0, 5)` | `1` | REJECTED — `INVALID_EVENT_FRAME`, `SILENT_PRE_HORIZON_TERMINATION`, `TERMINAL_COUNT_MISMATCH` |

The two runs differ only in the declared cadence. At unit cadence from origin zero the positional surrogate
`transition_index + 1` coincides with the real frame; at any other cadence it does not, the event frame is off-schedule,
and `qualify_lifecycle_contract` rejects the **entire run** because a local violation is global.

Reviewer B independently quantified the consequence by exhaustive enumeration over an 8-mask alphabet at depth 4
(4096 configurations, partitioned into 3910 runs containing a disappearance and 186 without):

| schedule | path | with disappearance | rejected | without disappearance | rejected |
|---|---|---|---|---|---|
| `(0,1,2,3)` | legacy | 3910 | 0 | 186 | 0 |
| `(0,5,11,12)` | legacy | 3910 | **1295** | 186 | **0** |
| `(7,19,20,44)` | legacy | 3910 | **1295** | 186 | **0** |
| `(0,5,11,12)` | repaired | 3910 | **0** | 186 | 0 |
| `(7,19,20,44)` | repaired | 3910 | **0** | 186 | 0 |

1295 rejections, 100 % of them in the disappearance group and 0 % in the survival group, every one carrying the same
violation triple. That is the survivorship trapdoor stated numerically: rejection was perfectly correlated with the
outcome under study.

### 16. The repair

`edlab/substrates/lattice_bond/instrumentation.py` only. Three additions and one changed expression.

1. `from numbers import Integral`.
2. `_validated_sample_schedule(frames, sampled_frames)` — validates a declared schedule (ordered sequence; same length as
   `frames`; integral, non-`bool`, non-negative; strictly increasing; equal to `component.frame` at every position that
   contains an observed component) and returns it normalised to plain `int`. A malformed schedule raises; it is never
   silently repaired.
3. `_transition_right_frame(transition_index, right, schedule)` — returns `schedule[transition_index + 1]` when a
   schedule is present, and otherwise the byte-identical legacy expression `right[0].frame if right else transition_index + 1`.
4. `track_components` gains `sampled_frames: Sequence[int] | None = None`, validates it, and the defect line becomes
   `right_frame = _transition_right_frame(transition_index, right, schedule)`.

`lifecycle.py` and `future_lifecycle_runner.py` were **not** modified; both are byte-identical to the accepted parent
(`3120d820…d03053` and `7691da35…f4b33d08`). **No new lifecycle event kind was introduced.** The existing taxonomy
already represents disappearance as `DISSOLUTION` → `DISSOLVED_DETECTED_TRACK`; the defect was never in the taxonomy, only
in the frame number stamped on the event.

### 17. Seven-step lifecycle-stack proof

Synthetic input only. Schedule `(0, 5, 11)`, chosen so that `transition_index + 1`, `left_frame + 1` and the true right
frame `sampled_frames[i+1]` are three different numbers at both transitions. Detector frames: one component, then an
**empty** frame, then a different component.

| step | required | observed | result |
|---|---|---|---|
| 1 | old defect reproduced on the accepted parent | events `[(0,APPEARANCE),(1,DISSOLUTION),(11,APPEARANCE)]`; violations `INVALID_EVENT_FRAME`, `SILENT_PRE_HORIZON_TERMINATION`, `TERMINAL_COUNT_MISMATCH` | PASS |
| 2 | repaired tracker emits the actual scheduled event frame | events `[(0,APPEARANCE),(5,DISSOLUTION),(11,APPEARANCE)]`; every event frame ∈ schedule | PASS |
| 3 | repaired output passes structural lifecycle validation | no violations; `run_terminal_state = ALL_TRACKS_CLOSED`; track/event/assignment = 2/3/2 | PASS |
| 4 | completion skeleton publishes and reopens canonical evidence, unmodified | `RunnerState.COMPLETE_PUBLISHED`; manifest `disposition = COMPLETE`; reopened `lifecycle_document_sha256` equals the on-disk digest `6d651ee2268bf78c8a12e1a814dd3ec5ffd2ee187fb809025503bd596f531a83`; on-disk bytes equal `canonical_lifecycle_bytes(contract)` | PASS |
| 5 | a terminal event is present in the persisted evidence | persisted `terminal_records` = `[(0, DISSOLVED_DETECTED_TRACK, 5), (1, RIGHT_CENSORED_AT_HORIZON, 11)]`; `len(terminal_records) == source_binding.track_count == lifecycle_binding.terminal_record_count` | PASS |
| 6 | the run is not silently converted into success-with-survival | dissolving run terminal `DISSOLVED_DETECTED_TRACK` @ 5; otherwise-identical surviving run terminal `RIGHT_CENSORED_AT_HORIZON` @ 11; both qualify, and the two are distinguishable in the persisted record | PASS |
| 7 | multiple affected tracks remain globally and exhaustively accounted for | one terminal record per track, track-id sets equal, both fates represented | PASS |

Step 4 is the answer to the contingency Part I anticipated: the completion skeleton *can* publish and reopen canonical
evidence for repaired tracker output without any source modification. What the hash binding blocks is not behaviour but
the **formal currency** of the prior qualification record — see §21.

### 18. Horizon semantics — the four frozen cases, separately demonstrated

Schedule `(0, 5, 11)` throughout.

| case | detector frames | events | contract |
|---|---|---|---|
| (a) pre-horizon terminal + later declared observation | `A, EMPTY, B` | `(0,APPEARANCE) (5,DISSOLUTION) (11,APPEARANCE)` | QUALIFIED — `DISSOLVED_DETECTED_TRACK @5 (TRACK_EVENT)`, `RIGHT_CENSORED_AT_HORIZON @11 (DECLARED_HORIZON)` |
| (b) disappearance first detected **at** the horizon | `A, A, EMPTY` | `(0,APPEARANCE) (5,CONTINUATION) (11,DISSOLUTION)` | QUALIFIED — `DISSOLVED_DETECTED_TRACK @11 (TRACK_EVENT)`; `TERMINAL_AT_HORIZON` did **not** fire |
| (c) track whose last observed point **is** the horizon | `A, A, A` | no `DISSOLUTION` at all | QUALIFIED — `RIGHT_CENSORED_AT_HORIZON @11 (DECLARED_HORIZON)` |
| (d) pre-horizon end with the terminal event removed | (a) minus its `DISSOLUTION` | `(0,APPEARANCE) (11,APPEARANCE)` | REJECTED — `SILENT_PRE_HORIZON_TERMINATION`, `TERMINAL_COUNT_MISMATCH` |

Case (b) holds by construction, not by luck. `lifecycle.py` guards on `last_key[0] == final_frame` — the *track's* last
**point**, not the last frame it was searched for. A track that disappears takes its last point at `sampled_frames[-2]`, so
it enters the `else` branch where `expected_terminal_frame = frames[last_position + 1] = sampled_frames[-1]`, which is
exactly what the repaired tracker now stamps.

**The forbidden substitution did not occur.** Reviewer B checked `TERMINAL_AT_HORIZON` across ~29 000 repaired-path runs
and it fired **zero** times, then confirmed the guard is not dead code by handcrafting a `TrackingResult` (which no
tracker would emit) where a track observed at the horizon also carries a terminal event there — that does raise
`TERMINAL_AT_HORIZON`. `INVALID_EVENT_FRAME` was not traded for another code; it was made unreachable.

### 19. Test matrix and mutation matrix

All fifteen frozen cases are covered by `tests/test_empty_right_nonunit_cadence_tracker_repair.py` (48 node IDs), plus the
four horizon cases (`test_h1`–`test_h4`), three survivorship cases (`test_s1`–`test_s3`) and six cases added in the review
round (`test_r1`–`test_r6`). `tests/test_lattice_bond_instrumentation.py` carries twelve added backward-compatibility node
IDs. Full node lists are bound in `..._QUALIFICATION.json`.

Fourteen mutants, all in disposable copies under `/tmp/mutT` with `PYTHONDONTWRITEBYTECODE=1`, module provenance verified
inside each mutant tree. **14 killed, 0 surviving.**

| id | mutation | verdict | representative named killer |
|---|---|---|---|
| T1 | restore the old `transition_index + 1` fallback | KILLED (22) | `test_02_empty_right_frame_at_nonunit_cadence_binds_the_actual_frame` |
| T2 | use `left_frame + 1` | KILLED (22) | `test_04_nonzero_schedule_origin_is_not_treated_as_an_offset` |
| T3 | unit-cadence-only arithmetic from the schedule origin | KILLED (22) | `test_04_nonzero_schedule_origin_is_not_treated_as_an_offset` |
| T4 | emit no terminal event when the right frame is empty | KILLED (16) | `test_s3_disappearance_is_not_reported_as_survival` |
| T5 | close only the first of several disappearing tracks | KILLED (18) | `test_06_several_left_entities_all_close_at_the_empty_right_frame` |
| T6 | use the final horizon frame regardless of the transition | KILLED (12) | `test_08_disappearance_followed_by_later_empty_observations` |
| T7 | accept an event frame absent from the schedule | KILLED (29) | `test_13_every_event_frame_belongs_to_the_declared_schedule` |
| T8 | shift the event one schedule position late | KILLED (12) | `test_03_irregular_cadence_binds_each_transition_independently` |
| T9 | convert disappearance into successful completion | KILLED (18) | `test_s3_disappearance_is_not_reported_as_survival` |
| T10 | allow a silent pre-horizon termination | KILLED (9) | `test_s1_disappearance_is_no_longer_correlated_with_global_rejection` |
| T11 | revert **only** the `TRACKING_UNRESOLVED` event frame | KILLED | `test_r1_tracking_unresolved_is_stamped_with_the_scheduled_frame` |
| T12 | drop the non-negativity rule | KILLED | `test_r3_a_negative_schedule_is_rejected_by_the_nonnegativity_rule_itself` |
| T13 | accept unordered containers as a schedule | KILLED | `test_r4_an_unordered_container_is_not_accepted_as_a_schedule` |
| T14 | revert **only** the `TEMPORARY_CONTACT` event frame | KILLED | `test_r2_temporary_contact_is_stamped_with_the_scheduled_frame` |

T11–T14 exist because the independent reviewers found them surviving in the pre-review suite. They are recorded as
*findings that were acted on*, not as pre-planned coverage.

Two further variants were built and are classified **provably equivalent, not surviving mutants**:

| id | variant | classification |
|---|---|---|
| E1 | `CONTINUATION` reads `right_frame` instead of `target.frame` | equivalent — validation forces `target.frame == schedule[i+1] == right_frame` |
| E2 | consult the schedule only when the right detector frame is empty | equivalent — same reason, in the other direction |

Their survival is the *evidence* for the equivalence claim, not a gap in it.

### 20. Compatibility

The legacy call path is unchanged. Reviewer A built a differential harness importing the parent module and the repaired
module side by side and compared `repr((tracks, events, edges, assignments))` over **808 fixtures** (all 1-, 2- and
3-frame combinations of a 10-mask catalogue under two numberings, one of which makes the legacy fallback visibly wrong,
plus targeted empty-right cases): **0 mismatches.**

One deliberate strictness increase: schedule validation was hoisted above the `if not frames: return TrackingResult((), (), (), ())`
early return, so `track_components((), spec, (0,))` now raises instead of silently accepting a malformed declaration. With
`sampled_frames` omitted the hoist is a no-op, so no pre-existing caller can reach it. Pinned by
`test_a_malformed_schedule_is_refused_even_for_an_empty_frame_sequence`.

### 21. Requalification DAG

Three distinct statuses, which must not be conflated.

| status | meaning | what holds it |
|---|---|---|
| **historically valid** | `FUTURE_LIFECYCLE_CONTRACT_00` and `FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00` / `…_HARDENING_00` remain true statements **about the commits they were granted over**. Nothing here retracts them. | Each qualification record binds its own `qualification_commit`. A later tree cannot falsify a claim indexed to an earlier one. |
| **behaviourally compatible** | The repaired tracker's output is accepted, published, reread and independently reverified by the *unmodified* integration skeleton. | §17 step 4; 198 of 199 tests pass, including all 50 lifecycle-contract tests, all 54 integration tests except the hash guard, and `test_21` (the retained-rejection guard for the legacy path). |
| **formally current** | **NOT ESTABLISHED, and not claimed.** The bound-package hash test `test_23_bound_lifecycle_package_remains_byte_identical` pins `instrumentation.py` to `f40c0817…6fd6c88` and now fails. | The pin is the designed tripwire. Refreshing it requires editing a file this mission is forbidden to touch, plus re-issuing `FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json`. That is a separate, separately authorised mission. |

Reviewer B verified the blast radius directly: of the seven artifacts `test_23` pins, **six are byte-identical** to their
pinned digests. Exactly one differs, and it is the file the repair edits. Reviewer B also confirmed by inspection that the
pin is **not enforced at runtime** — nothing under `edlab/` reads the allowlist or hashes its own source — so the production
path is not broken; the qualification *record* is stale.

No downstream requalification was started. No runner was wired. No scientific experiment was run.

### 22. Independent review

Two independent read-only reviews were commissioned, each explicitly empowered to require `TRACKER_REPAIR_INSUFFICIENT`.
Both worked only in disposable copies; the reviewed tree's source hashes were identical before and after. The full
reports are reproduced verbatim in `..._TRACKER_REPAIR_00_REVIEW_JOURNAL.md`.

**Reviewer A — frame and tracker semantics. VERDICT: FAIL.**
Found **zero semantic defects** after an 808-fixture parent/repaired differential, a 1500-trial five-property randomised
fuzz (0 violations), 15 targeted source mutants, a 31-case validation battery and 13 handcrafted cadence scenarios absent
from the suite (all 13 handled correctly). Confirmed C1–C5; C6 PARTIAL. Its FAIL rests **solely** on DEFECT-1, the red
hash guard, which it judged blocking on acceptance while stating "the semantic core needs no redesign." Raised OBS-1
(`TRACKING_UNRESOLVED` at non-unit cadence untested — a surviving mutant), OBS-3 (non-negativity rule not independently
pinned), OBS-4 (unordered containers accepted), OBS-5 (two tests labelled as repair coverage whose fixtures contain no
empty frame). All four were acted on in checkpoint 3.

**Reviewer B — survivorship and lifecycle audit. VERDICT: PASS**, recommending `TRACKER_REPAIR_QUALIFIED` under three
mandatory conditions. Found **no defect** in the repaired path across ~41 400 synthetic runs of its own construction,
including a 16 807-configuration depth-5 enumeration with 0 rejections and 0 off-schedule event frames. Established S1–S4
CONFIRMED, S5 PARTIAL. Its argument against its own recommendation is reproduced in full in the journal.

**They disagree on the disposition. That disagreement is the finding, and it is not resolved by majority.** The frozen
Part I §13 criterion decides it — see §23.

### 23. Two blockers, and the disposition

**BLOCKER-1 — the repair is opt-in, and nothing in the repository opts in.** (Reviewer B, OBS-1.)
`sampled_frames` defaults to `None`, and the default path reproduces the defect exactly. Reviewer B grepped every
`track_components(` call site in the tree: **all thirty are in tests**, and only the new repair suite passes a schedule.
`future_lifecycle_runner.py` receives an already-built `TrackingResult` and never calls the tracker, so the opt-in
decision lives with a producer outside this tree. Nothing fails closed if a caller forgets.

Reviewer B further verified that this was **forced, not chosen**: any change to the default — including raising on
non-unit cadence when no schedule is supplied — breaks `test_21_empty_right_frame_at_nonunit_cadence_remains_rejected` in
`tests/test_future_lifecycle_runner_integration.py` and a fixture in `tests/test_future_lifecycle_contract.py`. Both files
are forbidden to modify, and both are themselves hash-bound by `test_23`.

This is Part I §13's criterion for `TRACKER_REPAIR_INSUFFICIENT`, met literally: *the tracker alone cannot close the
survivorship mechanism without changing integration material*. What was delivered is an **exit from the trapdoor**, proven
correct and proven exhaustive. It is not a closure of the trapdoor.

**BLOCKER-2 — the delivered tree leaves a hash-bound integrity test red.** (Reviewer A, DEFECT-1.)
`1 failed, 198 passed`. The mission's qualification rule requires zero failures; the allowlist makes a green tree and a
landed repair mutually exclusive. Reviewer A judged this blocking; Reviewer B judged it a correctly-firing provenance
tripwire whose refresh is a separately pre-authorised obligation, and argued — persuasively — that a mission editing its
own hash pin would be a materially worse outcome than a red tripwire. Both positions are recorded. This blocker is **not**
the ground on which the disposition is selected; BLOCKER-1 is. It is recorded as a second, independent reason the tree may
not be described as formally current.

**Disposition: `TRACKER_REPAIR_INSUFFICIENT`.**

This is not a finding against the repair. Stated precisely:

- The tracker semantics are **proven correct** — by two independent adversarial reviews that between them ran ~42 000
  synthetic configurations, an 808-fixture differential, a 1500-trial fuzz and 29 mutants, and found zero semantic defects.
- The seven-step lifecycle-stack proof, the four horizon cases, the fifteen-case test matrix and the fourteen-mutant
  matrix all pass.
- `lifecycle.py` and `future_lifecycle_runner.py` are byte-identical to the accepted parent.
- What is **not** established is the mission's actual objective: that disappearance *becomes* explicit lifecycle
  information rather than a globally discarded run. In the repository as delivered it becomes so **only for a caller that
  declares its schedule**, and no such caller exists here.

The work is committed on `codex/empty-right-nonunit-cadence-tracker-repair-00` and is ready to be adopted. What it needs
is authority this mission does not hold: to make the schedule mandatory at non-unit cadence (which requires touching
`test_21` and the contract-test fixture), and to refresh the bound-package digest. Both are governance decisions for the
project owner, not code-review findings, and handing them up rather than taking them is the reason this returns
`TRACKER_REPAIR_INSUFFICIENT` rather than a self-granted `QUALIFIED`.

### 24. Firewall and repository discipline

No physics shard, shard manifest, world name, trajectory, candidate record, reconstructed checkpoint, autopsy input,
`results/` directory, prospective or 54xxx namespace, global index, `stage_b.py`, `stage_b_reproduce.py` or Kovacs
material was opened, enumerated, grepped, hashed or inspected — by this mission or by either reviewer. No engine,
scientific runner, historical physics, feasibility simulation, parameter sweep, autopsy or scientific analysis was run. No
seed was created or consumed. Every input was a handcrafted boolean mask pushed through the real detector, or a
hand-built `TrackingResult`.

All commits were built with lock-free plumbing (`GIT_INDEX_FILE` + `read-tree` + `add -f` + `write-tree` + `commit-tree`
+ `update-ref`) against a `--no-checkout --detach` worktree that materialises nothing. The `main` worktree's dirty user
work was not read, cleaned, restored, stashed, staged or committed, and no ref other than
`refs/heads/codex/empty-right-nonunit-cadence-tracker-repair-00` was written.

Disclosed by Reviewer A: one probe run without `PYTHONDONTWRITEBYTECODE=1` created `edlab/__pycache__/` inside the review
copy; Reviewer A removed exactly those three `.pyc` files. Disclosed by Reviewer B: it observed the same directory and
declined to delete it. No source byte changed in either case; the reviewed tree's hashes were identical before and after
both reviews. The clean-room is a copy; the repository of record was never executed against.

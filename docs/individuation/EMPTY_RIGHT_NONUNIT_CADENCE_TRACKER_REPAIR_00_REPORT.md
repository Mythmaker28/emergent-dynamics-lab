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

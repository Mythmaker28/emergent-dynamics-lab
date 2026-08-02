# EMPTY-RIGHT-NONUNIT-CADENCE-TRACKER-REPAIR-00 — review journal

Two independent read-only reviews were commissioned after checkpoint 2
(`0509ad86da0b3e2279f4a372ae601eb1e2c35679`). Each was given a written mandate that stated explicitly that it was
empowered to require `TRACKER_REPAIR_INSUFFICIENT`, that a rubber-stamp would be a failure of its role, and that it must
not manufacture findings or pad. Each was bound by the same scientific firewall as the mission, forbidden to modify the
reviewed tree, and required to run experiments only in disposable copies.

The reviewed tree's source hashes were recorded before and after both reviews and were identical.

**Outcome: the reviewers disagreed.** Reviewer A returned FAIL; Reviewer B returned PASS and recommended
`TRACKER_REPAIR_QUALIFIED` under conditions. The disagreement was not resolved by majority. It was resolved by the frozen
Part I §13 criterion, which Reviewer B's own decisive observation (OBS-1) meets literally. See §23 of the report.

Both reports are reproduced below **verbatim and unedited**, including the parts that are critical of the work and the
parts where a reviewer disclosed its own procedural lapse.

---

## Actions taken in response (checkpoint 3)

Every actionable finding was acted on before the qualification package was written. Each is bound to a mutant that was
surviving before the fix and killed after it.

| finding | reviewer | action | binding evidence |
|---|---|---|---|
| OBS-1 `TRACKING_UNRESOLVED` at non-unit cadence untested; mutant survived the whole suite | A | added `test_r1_tracking_unresolved_is_stamped_with_the_scheduled_frame` | mutant **T11** now KILLED |
| sibling gap: `TEMPORARY_CONTACT` at non-unit cadence untested | A (C6) | added `test_r2_temporary_contact_is_stamped_with_the_scheduled_frame` | mutant **T14** now KILLED |
| OBS-3 non-negativity rule not independently pinned (every negative case was caught by the *consistency* check instead) | A | added `test_r3_...rejected_by_the_nonnegativity_rule_itself`, using a leading EMPTY frame so there is nothing to disagree with | mutant **T12** now KILLED |
| OBS-4 unordered containers (`set`, `frozenset`, `str`, `bytes`) silently accepted as a schedule | A | `_validated_sample_schedule` now rejects them explicitly; added `test_r4_an_unordered_container_is_not_accepted_as_a_schedule` | mutant **T13** now KILLED |
| OBS-5 `test_07` and `test_s2` are labelled as repair coverage but their fixtures contain no empty frame, so they pass on the defective build | A | `test_s2` refixtured to `(A|B, EMPTY, B)` so it genuinely pins the repair, with an explicit assertion that the legacy path is rejected; `test_07` kept but its docstring corrected to state plainly that it passes on the parent and why that is itself informative | `test_s2` now fails on the reverted build |
| C6 uncovered scenarios: first frame empty then populated; a visually identical component returning after a gap | A | added `test_r5_first_frame_empty_then_populated_at_nonunit_cadence` and `test_r6_a_visually_identical_component_returning_later_is_not_stitched` | both fail on the reverted build |
| OBS-2 / C4 the schedule cross-check cannot cover an empty position — inherent, not fixable | A, B | documented explicitly in `_validated_sample_schedule`'s docstring rather than papered over | — |
| OBS-3 (B) the `track_components` docstring overstates the schedule as authoritative for "every event" | B | docstring corrected: the schedule is authoritative for the *right frame of each transition*; onset `APPEARANCE` and `CONTINUATION` read `component.frame`, which validation forces equal to the corresponding schedule entry — a difference of provenance, not of result | mutants **E1**, **E2** classified equivalent |
| OBS-1 (B) the repair is opt-in and no in-tree caller opts in | B | **not fixable within the allowlist** — Reviewer B verified that changing the default breaks `test_21` and the contract-test fixture, both forbidden and both hash-bound. Recorded as BLOCKER-1 and made the ground of the disposition. | report §23 |
| DEFECT-1 (A) the delivered tree leaves `test_23` red | A | **not fixable within the allowlist.** Recorded as BLOCKER-2 with both reviewers' opposed arguments reproduced. | report §21, §23 |

Findings deliberately **not** acted on, and why:

- Reviewer A OBS-2 and Reviewer B OBS-2 (empty positions unverifiable): an empty detector frame carries no frame stamp,
  so there is nothing any check performable here could compare it against. Documented, not patched.
- Reviewer B OBS-4 (legacy equivalence verified by inspection only, because the review copy had no VCS history): closed
  independently by Reviewer A, which located the authentic parent blob by content hash (`f40c0817…6fd6c88`) and ran an
  808-fixture parent/repaired differential with 0 mismatches.
- Reviewer B OBS-5 and Reviewer A's own disclosure (a stray `edlab/__pycache__/` in the review copies): no source byte
  changed; recorded in report §24 so no later reader misattributes it.
- Reviewer B's OUT-OF-SCOPE list (three standing obligations from `FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md`):
  unaffected by this repair, and outside this mission's authority.

---

## Reviewer A — frame and tracker semantics (verbatim)

## VERDICT: FAIL

The **frame rule itself is correct** — I attacked C1–C4 hard and could not break the semantics. The FAIL is on the **delivered state**: the repair leaves the repository's own test suite red, because an unmodified, forbidden-to-modify integrity test byte-pins the *pre-repair* digest of the very file the repair had to change. Details in DEFECT-1.

**Disclosure (my own constraint):** my very first probe (`python3 -c "import edlab"`, run from the repo cwd) was the one command in this review that lacked `PYTHONDONTWRITEBYTECODE=1`, and it created `/home/claude/cr/repo/edlab/__pycache__/` with three `.pyc` files at 18:20. I removed exactly those three files and that directory; no `__pycache__` existed in the tree beforehand, and no source file was touched. All three changed-file SHA-256s are byte-for-byte as delivered (`3ef52e2b…`, `30222e98…`, `44c4c265…`). All experiments below ran in `/tmp/revA/`. No engine, no seed, no shard, no `results/`, no Stage-B material, no `stage_b*.py` was opened or run; the only inputs were synthetic boolean masks pushed through `detect_components`.

---

## Real diff obtained

The repo has no `.git`. I located an authentic parent blob by content hash in a prior scratch tree and verified it: `sha256(/tmp/reviewA/base/edlab/substrates/lattice_bond/instrumentation.py) = f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88` — the stated pre-repair hash. `diff -u` against the repo shows **exactly three hunks**: the `from numbers import Integral` import, the two new helpers, and the signature/docstring/one-line call-site change. Nothing else in `instrumentation.py` moved.

---

## C1 — Frame rule correct for every transition: **CONFIRMED**

Enumeration is `for transition_index, (left, right) in enumerate(zip(frames[:-1], frames[1:], strict=True))`, so transition `i` pairs `frames[i]` with `frames[i+1]`; `schedule[i+1]` is the right frame by construction. Index safety is guaranteed by the length check (`i` max is `len(frames)-2`, so `i+1` max is `len(schedule)-1`), and with `len(frames)==1` the loop never runs (verified: single-frame fixture, schedule `(7,)`, emits `[(7,'APPEARANCE')]`).

Off-by-one is not merely unlikely, it is detected: mutating to `schedule[transition_index]` produced **7938 property violations** in a 1500-trial randomized fuzz and **27 test failures**; mutating to `schedule[-1]` produced 13 failures.

The 1500-trial fuzz (random masks, random gaps drawn from {1,1,2,3,7,25}, 1457 non-unit schedules, 1337 empty frames generated) checked five independent properties — every event frame ∈ schedule; unit-cadence schedule path ≡ legacy path; `right[0].frame == schedule[i+1]` whenever right is non-empty; onset/right-frame event-kind partition; and no `INVALID_EVENT_FRAME`/`INVALID_TRACK_POINT_FRAME` from `qualify_lifecycle_contract`. Result: `violations: 0`.

## C2 — No remaining positional surrogate; partition safe: **CONFIRMED**

Every frame number constructed inside `track_components` traces to exactly one of two sources: `component.frame` (lines 507, 518, 560, 562, and the `assignment` keys feeding `assignments` at 613) or `right_frame` (565, 568, 573, 578, 582, 592). There is no third construction.

The partition cannot produce disagreement, and I proved it two ways. Analytically: `CONTINUATION` is only emitted when a target exists in `right`, and `_validated_sample_schedule` requires `int(component.frame) == resolved[position]` for *every* observed component, so `target.frame ≡ schedule[i+1] ≡ right_frame`. Empirically, two deliberately-equivalent mutants both scored **89 passed**:

- `E1_continuation_uses_right_frame` (swap `target.frame` → `right_frame` in the CONTINUATION event)
- `E2_schedule_only_when_empty` (consult the schedule *only* when `right` is empty)

Their survival is the evidence, not a gap: it demonstrates the two expressions are provably interchangeable. Conversely, moving *any* of the six `right_frame` uses back to `transition_index + 1` is caught — except one (see OBS-1).

Worth recording as a genuine improvement: on the legacy path nothing forces all components in one frame list to share a `.frame`, so `right[0].frame` and `target.frame` *could* diverge for a malformed caller. The schedule path adds the check the legacy path never had.

## C3 — Legacy path genuinely unchanged: **CONFIRMED**

Structurally: `sampled_frames=None` → `_validated_sample_schedule` returns `None` on its first statement, and `_transition_right_frame` returns the byte-identical original expression.

Empirically I built a differential harness importing the parent module and the repaired module, over **808 fixtures** (all 1-, 2- and 3-frame combinations of a 10-mask catalogue, sampled to 404 sequences × 2 numberings — unit cadence and a `7 + 5i` numbering that makes the legacy fallback visibly wrong — plus targeted empty-right cases), comparing `repr((tracks, events, edges, assignments))`:

```
cases compared: 808
mismatches: 0
empty-frames legacy identical: True
```

On the hoisted validation: with `sampled_frames` omitted the hoist is a no-op, so `frames=()` legacy behaviour is unchanged (verified identical). It only changes behaviour on the *new* path: `track_components((), TRACKER, (0,))` now raises `ValueError: sampled_frames has 1 entries for 0 detector frames` instead of silently returning an empty result. That is a strictness increase on a path no pre-existing caller can reach, and it is the right call — validating then discarding would let a malformed declaration through unnoticed. **Acceptable.**

The added third parameter is also safe against positional-argument collision: the parent signature had exactly two parameters, so no existing call can bind it accidentally.

## C4 — Schedule validation sound: **CONFIRMED** (with one inherent limit, OBS-2)

Full battery, all against real detector output:

| Input | Result |
|---|---|
| `(0,5)` python ints; `np.int64` array; list of `np.int64`; `np.int32`; `np.uint8` | ACCEPT, `frame_types={'int'}` |
| `np.float64(5.0)`, `float 5.0`, `Decimal(5)`, `Fraction(5,1)`, `Fraction(10,2)`, `"5"`, `b"\x05"`, `None` | reject — *must contain integers* |
| `np.bool_`, python `bool`, bool in one slot only | reject — *must contain integers* |
| `-1` first, `-5` second | reject — *must be nonnegative* |
| duplicate `(5,5)`, decreasing `(5,0)` | reject — *must be strictly increasing* |
| too short, too long | reject — *N entries for M detector frames* |
| disagrees with an observed component | reject — *disagree … at schedule position 0* |
| `2**53+1`, `2**70`, `2**63` (over int64) | ACCEPT, carried exactly |
| generator, `map` object | ACCEPT (materialised once by `tuple()`) |
| `()` for `()` frames | ACCEPT; any non-empty schedule for `()` frames rejected |

`isinstance(value, Integral)` is the right check: `np.int64/int32/uint8` register as `Integral` and pass; `np.float64` and `np.bool_` do not and fail. The explicit `isinstance(value, bool)` guard is load-bearing — removing it makes `test_12[schedule6]` fail. `int(value)` normalisation means `event.frame` is always a plain `int` even for numpy input, which matters for the contract's byte-canonical digests. Arbitrary-precision Python ints survive intact (`2**70` round-trips through the contract).

Nonnegativity is also load-bearing, not decorative: with that check removed, `sampled_frames=(-5,-1)` over a frame stamped `-5` is accepted and emits `[(-5,'APPEARANCE'), (-1,'DISSOLUTION')]` (the detector itself will happily stamp `frame=-5`). Downstream `qualify_lifecycle_contract` independently raises `INVALID_SAMPLE_FRAME`, so this is defence in depth — correctly placed.

## C5 — Test suite genuinely pins the behaviour: **CONFIRMED**

Reverting the repair (restoring the single-line fallback in `/tmp/revA/mut_revert`) makes **20 of 42** tests in the new file fail — `test_02`–`test_06`, `08`–`11`, six of the seven `test_13` parametrisations, `test_14`, `h1`, `h2`, `s1`, `s3`. No assertion I found is tautological; nothing merely restates the implementation. `test_02` is the strongest single test: it asserts the *legacy* result is `[1]` with the exact violation triple `['INVALID_EVENT_FRAME','SILENT_PRE_HORIZON_TERMINATION','TERMINAL_COUNT_MISMATCH']` and the repaired result is `[5]` with none, on byte-identical detector input. `test_h4` guards against the repair weakening the rule it exercises rather than satisfying it.

The 22 tests that survive the revert are, with two exceptions, *supposed* to: they are the compatibility guards (`test_01`, `test_15*`, `test_15b`, `test_13[schedule0]` — all unit cadence, where the fallback coincides), the validation guards (`test_12*`, `test_12b`), and the horizon guards (`h3`, `h4`). Two survivors are not deliberate — `test_07` and `test_s2` both use fixtures with **no empty frame** (`(both, BLOB_B, BLOB_B)`), so `right[0].frame` supplies the correct number either way. They document adjacent behaviour but do not pin the repair. That is a labelling imprecision, not a fault.

I also mutated the validator itself: dropping the observed-frame consistency check → 2 failures; allowing bools → 1; non-strict monotonicity → 1; dropping the length check → 4. Only the nonnegativity check is unpinned (OBS-3).

## C6 — Uncovered scenarios: **PARTIAL** (code correct everywhere; one real coverage gap)

I built 13 scenarios absent from the suite. **All 13 are handled correctly** — zero off-schedule event frames, contract qualifies clean in every case:

- First frame empty, second populated (`(0,5)` and `(3,9,20)`) → `APPEARANCE` at the true frame, not at position 1.
- Three consecutive empty frames in the middle, then a **pixel-identical blob returns** (`(0,5,11,17,23)`) → `[(0,'APPEARANCE'),(5,'DISSOLUTION'),(23,'APPEARANCE')]`, **2 tracks, no stitching**; terminals `{0: DISSOLVED_DETECTED_TRACK@5, 1: RIGHT_CENSORED_AT_HORIZON@23}`. Same for the immediate-reappearance variant `(0,5,11)`.
- `TRACKING_UNRESOLVED` before an empty frame, non-unit `(0,5,11,40)` → unresolved at 5 and 11, dissolutions at 40, terminals `UNRESOLVED_HANDOFF@5/@11`.
- Many-to-many unresolved then empty `(0,4,9)` → unresolved at 4, dissolutions at 9.
- `TEMPORARY_CONTACT` at non-unit cadence `(0,5,11)` and followed by an empty frame `(0,5,11,19)` → contact stamped 5, dissolutions 19.
- Frames near/over 2**53 (`2**53, +7, +9`) → carried exactly.
- All-frames-empty, single frame, single empty frame → empty results, contract OK.

Seven of these break on the reverted build (off-schedule frames `1`, `2`, `3` with the full `INVALID_EVENT_FRAME` violation triple), confirming they are real coverage of the repair, not vacuous.

The gap: `mut/M14_unresolved_positional` — reverting only the `TRACKING_UNRESOLVED` event to `transition_index + 1` — scores **89 passed**. The shipped suite contains no fixture that produces a `TRACKING_UNRESOLVED` event at non-unit cadence. My scenarios (c) and (h) catch it immediately (`CHILD_LINK_MISMATCH, INVALID_EVENT_FRAME, MISSING_ONSET_EVENT, SILENT_PRE_HORIZON_TERMINATION, TERMINAL_COUNT_MISMATCH, UNRESOLVED_FLAG_MISMATCH`). **The code is right; the suite does not defend it.**

---

## DEFECTS

**DEFECT-1 (blocking) — the repair leaves the repository's test suite red.**
`pytest tests/` on the repo under review:

```
FAILED tests/test_future_lifecycle_runner_integration.py::test_23_bound_lifecycle_package_remains_byte_identical
1 failed, 192 passed in 0.91s
```

`tests/test_future_lifecycle_runner_integration.py:682` byte-pins the bound lifecycle package, including:

```python
"edlab/substrates/lattice_bond/instrumentation.py":
    "f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88",
```

```
E   AssertionError: edlab/substrates/lattice_bond/instrumentation.py
E   assert '3ef52e2ba397...6bd5c25d69140' == 'f40c0817acaa...d1d69c6fd6c88'
```

That file is in the declared **unchanged and forbidden to modify** set. I confirmed the failure is caused by this repair and is not pre-existing: reconstructing the immediate parent (repo tree + parent `instrumentation.py` blob, new test file removed) gives `54 passed` on that file, `test_23` included.

The same digest is bound in two more places that are now stale: `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json:31` and `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md:166` (§5.1 hash table).

Mitigating scope, established by inspection: the pin is **not enforced at runtime**. Nothing under `edlab/` reads the allowlist or hashes its own source (`lifecycle.py` and `future_lifecycle_runner.py` only `from .instrumentation import` names). `FUTURE_LIFECYCLE_CONTRACT_00_SOURCE_ALLOWLIST.json` is a scope declaration for a prior mission, not a runtime manifest. So the production path is not broken — but the qualification package is now internally inconsistent and the executable integrity test fails.

This is precisely the mechanism's purpose: it exists to detect that someone changed `instrumentation.py` after the lifecycle contract was bound, and the repair did exactly that. The delivered change set cannot resolve it without violating its own constraints. It requires a governed refresh of the bound-package digest (`test_23` + `QUALIFICATION.json` + `HUMAN_REVIEW.md` §5.1) as an authorised step. **The semantic core needs no redesign** — only this needs resolving before the repair can be accepted.

---

## OBSERVATIONS (imperfect, tolerable)

**OBS-1 — `TRACKING_UNRESOLVED` at non-unit cadence is untested.** See C6. Mutant `M14` survives the full suite. The code is correct. One fixture — e.g. `(0,5,11,40)` over `(separated, collapsed, separated, EMPTY)` — closes it.

**OBS-2 — the schedule is unverifiable at exactly the position that matters.** The consistency check can only compare against *observed* components, so a position whose detector frame is empty is unchecked: `sampled_frames=(0,7)` over frames truly sampled at `(0,5)` is accepted and stamps `DISSOLUTION@7`. This is inherent — an empty frame carries no frame number — and it is mitigated by strict monotonicity plus agreement at every non-empty position, which brackets the value between its neighbours. It is also *coherent* by design: the same declared schedule is handed to `qualify_lifecycle_contract`, so the contract is evaluated against the caller's declaration, which is what the contract means. Worth one sentence in the helper's docstring; not a fault.

**OBS-3 — the nonnegativity rule is not independently pinned.** `test_12[schedule4-negative]` uses `(-1, 5)` against a frame stamped `0`, so it is rejected by the *consistency* check, not the *nonnegativity* check — mutant `M8_no_negative_check` scores 89 passed. A fixture with an empty leading frame (e.g. `(-5, -1)`) would pin the rule it names.

**OBS-4 — non-`Sequence` iterables are silently accepted.** `sampled_frames={0,5}` (a set) is accepted; `tuple()` happens to yield sorted order for small ints. The annotation says `Sequence[int]`, monotonicity would reject any adverse ordering, and the consistency check catches real mismatches, so practical risk is nil. Noting only for completeness.

**OBS-5 — `test_07` and `test_s2` are labelled as repair coverage but their fixtures contain no empty frame,** so they pass on the defective build (C5). Harmless; the docstrings slightly oversell.

**OBS-6 — no in-repo caller supplies `sampled_frames`.** `track_components` is invoked only from tests and re-exported from `__init__.py`; `future_lifecycle_runner.publish_future_family_completion` receives an already-built `TrackingResult` plus `sampled_frames`. The producer of that `TrackingResult` lives outside the three changed files. The repair is necessary and correctly placed, but it is inert until that producer passes the schedule. I did not and could not inspect that call site (firewalled).

---

## OUT OF SCOPE

- The actual `TrackingResult` producer (`stage_b*.py`, scientific runners) — firewalled; not inspected. Whether it now passes `sampled_frames` is unverified by me and belongs to whoever holds that scope.
- Whether the bound-package digest should be refreshed, and under whose authority — a governance decision, not a code review finding.
- Everything in `qualify_lifecycle_contract` other than the frame-membership behaviour I exercised.

---

## What I could not break

To be plain: I tried to break the frame rule with an 808-fixture parent/repaired differential, a 1500-trial five-property randomized fuzz, 15 targeted source mutants, a 31-case validation battery, and 13 handcrafted cadence scenarios the suite does not contain. **Zero semantic defects.** `schedule[transition_index + 1]` is the right frame for every transition; the `target.frame` / `right_frame` partition is provably a distinction without a difference under a validated schedule; the legacy path is bit-identical; the validator rejects everything it should and accepts numpy integers and arbitrary-precision ints correctly. The FAIL rests solely on DEFECT-1.

---

## Reviewer B — survivorship and lifecycle audit (verbatim)

I have completed my independent audit. Repo left untouched (all source hashes unchanged); all mutation experiments ran in `/tmp/revB/work` with `PYTHONDONTWRITEBYTECODE=1`. I did not read the sibling scratch files in `/home/claude/cr/` (`mutate_tracker.py`, `probe.py`, `proof7.py`, …) so as not to contaminate independence.

---

# REVIEWER B — SURVIVORSHIP AND LIFECYCLE AUDIT

## VERDICT: **PASS**

## S6 disposition (my independent answer): **`TRACKER_REPAIR_QUALIFIED`**, scoped and conditioned (conditions in §S6).

---

## What I did

Read `lifecycle.py` (1272 lines) and `instrumentation.py` (1024 lines) in full; confirmed by hash that `lifecycle.py` = `3120d820…d03053` and `future_lifecycle_runner.py` = `7691da35…f4b33d08` as stated. Copied the tree to `/tmp/revB/work`. Ran the suite. Then built my own fixtures from scratch (different lattice shape `(12,14)`, different blob geometry, different tracker spec than the repair's suite) and ran **~41,400 synthetic tracker runs** of my own construction, plus handcrafted `TrackingResult` values that no tracker would emit. No engine, no seed, no shard, no `results/`, no scientific runner, no physics. Probe scripts are at `/tmp/revB/probe1.py`, `/tmp/revB/probe2.py`, `/tmp/revB/probe3.py`, `/tmp/revB/probe4.py`.

Suite reproduction:

```
$ cd /tmp/revB/work && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q
1 failed, 192 passed in 1.01s
FAILED tests/test_future_lifecycle_runner_integration.py::test_23_bound_lifecycle_package_remains_byte_identical
E  AssertionError: edlab/substrates/lattice_bond/instrumentation.py
E  assert '3ef52e2ba397...6bd5c25d69140' == 'f40c0817acaa...d1d69c6fd6c88'
```

I verified the blast radius of that failure myself: of the seven artifacts `test_23` pins, **six are byte-identical** to their pinned digests (`SCHEMA.json` `629bfdc3…`, `SOURCE_ALLOWLIST.json` `d8743e1f…`, `SPEC.md` `81c5af7c…`, `__init__.py` `9d3bea5a…`, `lifecycle.py` `3120d820…`, `test_future_lifecycle_contract.py` `e940199e…`). Exactly one differs, and it is the file the repair edits.

---

## S1 — Is the rejection channel closed, or relocated? **CONFIRMED (scoped: see OBS-1)**

**Structural argument.** With a declared schedule, every event frame emitted by `track_components` is drawn from exactly two sources: `right_frame = schedule[transition_index + 1]` (`instrumentation.py:443-459`, used by `SPLIT`, `MERGE`, `TRACKING_UNRESOLVED`, `DISSOLUTION`, `APPEARANCE`, `TEMPORARY_CONTACT`), or `component.frame` (`APPEARANCE` at `frames[0]`, line 518; `CONTINUATION`, line 562). `_validated_sample_schedule` (`instrumentation.py:433-439`) proves `component.frame == schedule[position]` for every observed component before tracking begins. Therefore `{event.frame} ⊆ set(schedule)` unconditionally, so `INVALID_EVENT_FRAME` (`lifecycle.py:767-775`) is **unreachable** from repaired tracker output. This is a proof, not a sample.

**Empirical hunt for a replacement channel.** Exhaustive enumeration over an 8-mask alphabet (empty, two disjoint blobs, a third blob, a joinable bar, a split bar, and a symmetric-tie pair that forces `TRACKING_UNRESOLVED`):

| schedule | mode | with-disappearance | rejected | no-disappearance | rejected |
|---|---|---|---|---|---|
| `(0,1,2,3)` | schedule | 3910 | **0** | 186 | 0 |
| `(0,1,2,3)` | legacy | 3910 | 0 | 186 | 0 |
| `(0,5,11,12)` | schedule | 3910 | **0** | 186 | 0 |
| `(0,5,11,12)` | **legacy** | 3910 | **1295** | 186 | **0** |
| `(7,19,20,44)` | schedule | 3910 | **0** | 186 | 0 |
| `(7,19,20,44)` | **legacy** | 3910 | **1295** | 186 | **0** |

The legacy rows are the trapdoor in numbers: **1295 rejections, 100% of them in the disappearance group, 0% in the survival group**, every one carrying `('INVALID_EVENT_FRAME','SILENT_PRE_HORIZON_TERMINATION','TERMINAL_COUNT_MISMATCH')`. The repaired rows are 0/12288. A depth-5 enumeration (7 masks, `16807` configs, schedule `(0,5,11,12,40)`) gave **0 rejections and 0 off-schedule event frames**, split 16272 with-disappearance / 535 without.

Every configuration the mandate names, checked individually and qualifying:

- disappearance in the **first** transition → `DISSOLVED_DETECTED_TRACK` @ 5
- disappearance in the **last** transition → `DISSOLVED_DETECTED_TRACK` @ 40
- **every frame empty after a point** → terminal frame is the transition's right frame (11), **not** the horizon (40)
- **all tracks disappear** → `track_count=2`, both `DISSOLVED_DETECTED_TRACK` @ 5, `run_terminal_state == "ALL_TRACKS_CLOSED"`
- **nothing ever detected** → `track_count=0`, `run_terminal_state == "EMPTY_TRACK_SET"`, **qualifies**. I checked the code path: this is not a separate acceptance route — `terminal_records` and `tracks` are both empty, so `TERMINAL_COUNT_MISMATCH` (`lifecycle.py:1129`) compares `0 == 0` and no violation is raised. `run_terminal_state` is a derived property (`lifecycle.py:225-227`), not a gate.
- **split adjacent to an empty frame** → parent `SPLIT_INTO_TRACKS` @ 5, both children `DISSOLVED_DETECTED_TRACK` @ 11
- **merge adjacent to an empty frame** → parents `MERGED_INTO_TRACK` @ 5, child `DISSOLVED_DETECTED_TRACK` @ 11
- **unresolved handoff adjacent to an empty frame** → parent `UNRESOLVED_HANDOFF` @ 5, both unresolved children `DISSOLVED_DETECTED_TRACK` @ 11
- **unresolved handoff at the horizon** → parent `UNRESOLVED_HANDOFF` @ 5, children `RIGHT_CENSORED_AT_HORIZON` @ 5
- **single-frame schedule** `(7,)` → `RIGHT_CENSORED_AT_HORIZON` @ 7

**Necessity of the parameter.** Worth recording because it settles "could this have been done without an API change": when the right detector frame is empty it contains *no component*, hence *no frame stamp*. The right frame of a transition into disappearance is **not recoverable from detector output at all**. A declared schedule is the minimum sufficient information, not one design option among several.

## S2 — Is disappearance explicit information, not silence? **CONFIRMED**

For every disappearing track I observed exactly one terminal row, `terminal_state == "DISSOLVED_DETECTED_TRACK"`, `evidence_kind == "TRACK_EVENT"`, `terminal_frame == schedule[last_position + 1]` (the actual scheduled frame — e.g. 11 for a run whose horizon is 40), and `terminal_event_id` non-null. `contract.track_count == len(tracking.tracks)` and `len(terminal_records) == track_count` in every accepted case.

I looked specifically for a quiet-vanish path and found none — all three candidates fail closed rather than dropping a track:
- a `TrackRecord` with no valid points is skipped at `lifecycle.py:935`, but then `EMPTY_TRACK` (line 612) and `TERMINAL_COUNT_MISMATCH` (line 1129) both fire → run rejected.
- a record with a malformed `track_id` is excluded from `tracks` but raises `INVALID_TRACK_ID` (line 569-575).
- the tracker cannot emit a pointless track: `new_track` (line 503-514) always seeds one `TrackPoint`.

## S3 — Was the horizon trap swapped for a different one? **CONFIRMED (all four cases demonstrated by me)**

Schedule `(0,5,11)` unless stated:

| case | input | result |
|---|---|---|
| (a) pre-horizon terminal + further observation | `A, EMPTY, B` | `{0: DISSOLVED_DETECTED_TRACK @5, 1: RIGHT_CENSORED_AT_HORIZON @11}`, no violations |
| (b) disappearance first detected **at** the horizon | `A, A, EMPTY` | `{0: DISSOLVED_DETECTED_TRACK @11}`, no violations — `TERMINAL_AT_HORIZON` did **not** fire |
| (c) last observed point **is** the horizon | `A, A, A` | `{0: RIGHT_CENSORED_AT_HORIZON @11, DECLARED_HORIZON}`, and zero `DISSOLUTION` events emitted |
| (d) pre-horizon end with terminal event stripped | `A, EMPTY, B` minus `DISSOLUTION` | `['SILENT_PRE_HORIZON_TERMINATION','TERMINAL_COUNT_MISMATCH']` — still a violation |

Case (b) is correct by construction, not by luck: the guard at `lifecycle.py:1029` is `last_key[0] == final_frame`, and a disappearing track's last *point* is at `schedule[-2]`, so it takes the `else` branch where `expected_terminal_frame = frames[last_position + 1] = schedule[-1]` (lines 1064-1082) and matches.

**Forbidden substitution explicitly checked and absent.** Across all 29,095 repaired-path runs, `TERMINAL_AT_HORIZON` fired **zero** times. I separately confirmed the code is not dead by handcrafting a `TrackingResult` (not tracker output) in which a track observed at every scheduled frame including the horizon also carries a `DISSOLUTION` at the horizon — that yields `['TERMINAL_AT_HORIZON']`. So the guard is live and simply never triggered by legitimate repaired output. `INVALID_EVENT_FRAME` was not traded for it, nor for anything else.

## S4 — Exhaustive multi-track accounting **CONFIRMED**

3 blobs, staggered, schedule `(0,5,11,12,40)`:
`{0: (RIGHT_CENSORED_AT_HORIZON, 40), 1: (DISSOLVED_DETECTED_TRACK, 5), 2: (DISSOLVED_DETECTED_TRACK, 11)}` — three tracks, three rows, three distinguishable fates.

Split whose children then disappear, plus an independent survivor, schedule `(0,5,11,12)`:
`{0: (SPLIT_INTO_TRACKS, 5), 1: (RIGHT_CENSORED_AT_HORIZON, 12), 2: (DISSOLVED_DETECTED_TRACK, 11), 3: (DISSOLVED_DETECTED_TRACK, 11)}` — 4 tracks, 4 rows.

Across the full 16807-config depth-5 enumeration, `len(terminal_records) == track_count` held for every accepted run (it is enforced, and no run was rejected).

## S5 — Does the validator introduce a new outcome-correlated failure? **PARTIAL** (see OBS-2)

The mandate asks me to argue it both ways, so:

**No, for a correct caller.** `_validated_sample_schedule` compares the caller's declared schedule against `component.frame`, and `component.frame` is itself stamped by the caller (`detect_components(..., frame=…)`, or `state.step` when omitted — `instrumentation.py:140`). Both sides of the comparison are caller-controlled and physics-independent. Whether anything dissolved, split, merged, percolated or survived cannot make them disagree. A raise here is a caller/detector wiring bug, not a physical configuration. The other three raise conditions (length mismatch, non-integer/negative, non-increasing) are properties of the declared tuple alone. So: **no legitimate physical configuration can cause the validator to raise.** I could construct none.

**Yes, weakly, for an incorrect caller — and the direction is worth recording.** The cross-check loops over *observed components* only. An empty frame has no components, so **an empty schedule position is never cross-checked at all**. Demonstrated:

```
detector stamps (0,6), caller declares (0,5):
  surviving run  (A → B)     : ValueError: declared sampled_frames disagree with an
                               observed detector frame at schedule position 1
  disappearing run (A → EMPTY): no raise; qualifies; terminal = (DISSOLVED_DETECTED_TRACK, 5)
  (even a stamp of 999 on the empty frame raises nothing)
```

So under a mis-declaring caller, the *surviving* run is loudly rejected while the *disappearing* run is silently accepted carrying an unverified terminal frame. That is an outcome-correlated asymmetry — but inverted relative to the original trapdoor (it admits disappearances rather than excluding them), gated entirely on a caller bug, and loud on the survival side where it is trivially noticed. It is also an **information limit, not an implementation shortcoming**: an empty frame carries no evidence of its own frame number, so there is nothing the validator could cross-check it against. I record it as an observation, not a defect.

## S6 — Adjudicating the hash-pin conflict

**The strongest case for `TRACKER_REPAIR_INSUFFICIENT`** (the side I do not choose, stated as forcefully as I can make it): a red suite is a red suite. The repository's own executable invariant — not prose, an assertion — now evaluates false. And the thing that broke is not a peripheral fixture; it is the **evidence layer itself**, the mechanism that binds a qualification claim to source bytes. Declaring a mission `QUALIFIED` while the qualification-binding test is red is self-undermining: it establishes the precedent that an integrity tripwire may be waved through when someone in the room already knows why it fired, which is precisely the practice tripwires exist to prevent — and the next firing, for a bad reason, inherits that precedent. Further, the allowlist made green impossible; that is not a licence to lower the bar, it is evidence the mission was scoped wrong and should be re-scoped to carry its own requalification rather than landing a change that leaves the tree in a state nobody can honestly call qualified. Add that the repair is opt-in (OBS-1) and one can argue the mission delivered a *capability*, not a *repair*.

**Why I nonetheless choose `TRACKER_REPAIR_QUALIFIED`.**

1. `test_23` is not a behavioural test. I read it (`tests/test_future_lifecycle_runner_integration.py:682-702`): it asserts a **provenance** fact — "these seven files still have the bytes they had at the qualification commit." That fact is now false, and it *must* be false for the repair to exist at all. A tripwire that fires when the thing it watches changes is reporting truth. Treating its firing as "the repair is insufficient" conflates *"this is no longer the previously-qualified tree"* with *"this tree is wrong."*
2. The prior mission named this exact outcome in advance. `FUTURE_LIFECYCLE_CONTRACT_00_REPORT.md:58`: *"A future family must retain the rejection **or repair** and separately requalify the tracker API."* `FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md:101-103`: repairing `instrumentation.py` *"would alter material bound by FUTURE_LIFECYCLE_CONTRACT_00_QUALIFICATION.json and would require separately authorized requalification."* The requalification is a **named, pre-authorized, separate** obligation — not an omission of this mission.
3. The blast radius is one dict entry, and I verified it: six of seven pinned artifacts are byte-identical, and **all 192 other tests pass**, including `test_21` (the retained-rejection guard) and the entire 50-fixture lifecycle contract suite — every behavioural guard the original qualification actually rests on.
4. `QUALIFICATION.json` binds itself to `qualification_commit = ec494b4c…`. It is already, on its own terms, a historical record. Nothing about a changed working tree retroactively invalidates it.
5. Governance argues *against* fixing it here. The point of a hash pin is that the party who changes the source cannot also re-bless it. If this mission edited its own pin, that would be a materially worse outcome than a red tripwire, and no reviewer downstream could tell the difference between a legitimate repair and a laundered one.

**Conditions on the disposition (mandatory, not advisory):**
- (C1) The claim must be recorded as **scoped**: the survivorship channel is closed **for callers that declare `sampled_frames`**. The default path is deliberately unchanged and remains defective at non-unit cadence (OBS-1).
- (C2) This tree must not be described as "qualified against FUTURE-LIFECYCLE-CONTRACT-00." That record is historical to `ec494b4c`.
- (C3) A requalification mission — authorized to touch `test_23` and re-issue `QUALIFICATION.json` against the successor commit — must be opened, and must land **before** any downstream statistic is computed from runs tracked through this module.

---

## Findings

### DEFECTS (must fix)
**None.** I found no defect in the repaired path. I state this plainly rather than manufacturing a finding.

### OBSERVATIONS (tolerable; must be recorded)

**OBS-1 — The repair is opt-in; the default path is still defective, and no in-tree caller opts in.**
`instrumentation.py:521` selects behaviour on `schedule is not None`. Omitting `sampled_frames` reproduces the old positional stamp exactly, and my fuzz shows that path still yields the fully outcome-correlated 1295/0 rejection split at non-unit cadence. Two tests deliberately pin that: `test_21_empty_right_frame_at_nonunit_cadence_remains_rejected` and `test_generic_tracker_empty_right_frame_cadence_mismatch_is_rejected`. I grepped every `track_components(` call site in the tree: **all 30 are in tests**, and only the new repair suite passes a schedule. `future_lifecycle_runner.py` receives `tracking` as a parameter and never calls the tracker, so the opt-in decision lives in a caller outside this tree.
I checked whether the repair could have avoided this within the allowlist, and it could not: any change to the default — including raising on non-unit cadence with no schedule — breaks `test_21` (forbidden file) and `test_future_lifecycle_contract.py` (forbidden *and* hash-pinned by `test_23` itself). **Opt-in was forced by the allowlist, not chosen for convenience.** The consequence stands regardless: the trapdoor is not closed in the repository; an exit from it has been built, and walking through it is the caller's responsibility. Nothing in this tree fails closed if a caller forgets. This is the single most important thing for the record to say, and it is why condition C1 exists.

**OBS-2 — The schedule cross-check has zero coverage on empty frames.** See S5. Not fixable with the available information; direction is anti-correlated with the original bias; gated on a caller bug.

**OBS-3 — A docstring overstates slightly.** `track_components`' docstring says the schedule is "the sole authority for the frame stamped on **every** event of a transition." `CONTINUATION` events actually take `target.frame` (line 562), and the first-frame `APPEARANCE` takes `component.frame` (line 518). Both are provably equal to the corresponding schedule entry because of the cross-check, so the claim is true in effect but not literally true of the code. Cosmetic.

**OBS-4 — Legacy equivalence is inspection-verified, not byte-verified against the parent.** The working tree has no VCS history and no copy of the pre-repair `instrumentation.py`, so I could not diff. `_transition_right_frame(i, right, None)` returns `right[0].frame if right else i + 1`, which is exactly the expression the mission describes as the old inline behaviour, and `_validated_sample_schedule` short-circuits on `None` before touching anything. I am satisfied by inspection plus `test_15b`/`test_01`/`test_15`, but I flag that I could not confirm it independently of the repair's own claims.

**OBS-5 — Housekeeping, disclosed for completeness.** An `edlab/__pycache__/` directory (`__init__`, `specs`, `state` `.pyc`, CPython 3.11) appeared inside the review repository at 18:20:07 UTC during the review window. **No source file byte changed** — I recorded hashes at the start and end and they are identical. All of my own Python invocations ran with `PYTHONDONTWRITEBYTECODE=1` and imported `edlab` only from `/tmp/revB/work`; `edlab` is not installed on the interpreter path. I did not delete it (deletion inside the repo is equally forbidden). I flag it so that a later reader does not attribute it to the repair.

### OUT-OF-SCOPE
- `test_23`'s failure and the re-issuance of `QUALIFICATION.json` — the separate requalification mission (C3).
- The three standing obligations already accepted in `FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md:89-97` (lifecycle primitive unused by real runners; exported dataclasses directly constructible with a nominal `QUALIFIED` disposition; published JSON Schema looser than the implementation). All three remain true; none is affected by this repair; the second is worth re-flagging alongside OBS-1 since together they mean a well-formed `QUALIFIED` document can still be produced without either the validator or the schedule.
- Anything behind the scientific firewall. No shard, world, trajectory, candidate, checkpoint, autopsy input, `results/` directory, index, `stage_b*.py`, or Kovacs material was opened; no engine, runner, simulation, sweep or analysis was executed; no seed created or consumed.

---

## Adjudication of the disagreement

Reviewer A voted FAIL on DEFECT-1 while finding zero semantic defects. Reviewer B voted PASS on the merits while
identifying, in OBS-1, a limitation more fundamental than the one Reviewer A blocked on: **the repair does not close the
survivorship mechanism in this repository — it builds an exit that nothing walks through.**

Neither reviewer's vote decides the disposition. Part I §13, frozen before any source was touched, decides it:

> `TRACKER_REPAIR_INSUFFICIENT` if the tracker alone cannot close the survivorship mechanism without changing lifecycle
> or integration source.

Reviewer B established that closing the mechanism — making the schedule mandatory so the module fails closed rather than
silently reverting to the defective default — requires editing `test_21` in
`tests/test_future_lifecycle_runner_integration.py` and a fixture in `tests/test_future_lifecycle_contract.py`. Both are
forbidden by the frozen allowlist and both are themselves hash-bound. The frozen criterion is met literally, on evidence
produced by the reviewer who voted to pass.

**Disposition: `TRACKER_REPAIR_INSUFFICIENT`** — recorded, per Reviewer B's condition C1, as a scope finding and not as a
defect finding. The tracker semantics are proven correct by both reviewers. What is missing is authority this mission does
not hold.

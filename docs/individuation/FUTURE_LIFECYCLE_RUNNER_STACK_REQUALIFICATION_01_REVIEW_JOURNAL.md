# FUTURE-LIFECYCLE-RUNNER-STACK-REQUALIFICATION-01 — review journal

Two independent adversarial reviewers were commissioned after the implementation/test checkpoint. Each
received only the frozen Part I protocol, the exact permitted source and tests, the exact successor
evidence, the closed synthetic clean room, and the historical integration/hardening qualification
documents by exact path. Neither wrote to the clean room; both verified afterwards that they had not.
Neither ever requested an undeclared path.

| reviewer | mandate | round 1 | round 2 | round 3 |
|---|---|---|---|---|
| **A** | public API and non-bypassability | **FAIL** (blocker B1) | **FAIL** (blocker B2) | **PASS** |
| **B** | mutation, lineage and the schedule adversary | **FAIL** (blocker B1) | **PASS** | **PASS** |

Both final verdicts bind the same commit, `fb5619ba2b732fca6358de6a7ad5b025fab582f3`, and the same test
file, `a982415a6796bd7185ef3afac241d263d50bd98b03cb549136854fffe2dfaa1b`. **One FAIL controls; there was
no majority voting.** Three blockers were raised in total and all three were real.

---

## The finding that mattered

The candidate's central deliverable was to measure the strongest real binding between the mandatory
tracker and the runner, given that the runner does not invoke the tracker. **The candidate measured it
wrongly twice, and both errors were false safety claims.**

- **Round 0 — "one blind position".** The candidate claimed the only undetectable divergence was a single
  scheduled position that is both detector-empty and event-free. Reviewer A showed the class is unbounded:
  a fully witnessed run tracked at `(2,5,11,12)` publishes against an eleven-entry schedule.
- **Round 1 — "extension only, horizon preserved".** The replacement claimed extension anywhere with no
  point and no event, subject to monotonicity and a preserved horizon. Reviewer A falsified it in both
  directions at once: the horizon is not preserved when no track's last point sits at the final frame
  (a three-sample run publishes as ending 1,000,000 frames later); an unoccupied trailing frame can be
  **deleted**, so the residual is not only extension; prefix extension is available to occupied runs that
  do not begin at frame 0; and conversely an unoccupied inserted frame is still refused inside a live
  interval, so the constraint is on **intervals**, not on the inserted frame's own occupancy — a fact the
  body of the very test stating the rule already contradicted.

Reviewer A supplied the correct rule and Reviewer B independently confirmed it. Both wordings are
preserved under superseded markers with their falsifiers attached, in the test module and in the
qualification's `superseded_claims`. Nothing was rewritten to look as though it had always been right.

**Reviewer B recorded its own error unprompted.** Its round-2 PASS had endorsed the round-1 rule; its
324-probe sweep varied one schedule *value* at fixed cardinality, and its gap fixture had an *occupied*
horizon frame, so it could not exhibit the counterexample. It wrote: "I generalised from a fixture that
could not exhibit the counterexample." That is in this record because it belongs in it.

---

## Reviewer A — public API and non-bypassability

### Blockers

| id | finding | resolution |
|---|---|---|
| **B1** (round 1) | the residual divergence class is unbounded, not a single blind position; the section banner and `test_rs01_09` both overstated the tightness of the binding | `test_rs01_09` replaced by `09a`/`09b`/`09c`; banner corrected |
| **B2** (round 2) | the replacement rule is false in both directions: horizon not preserved, truncation possible, prefix extension available, interval-based not frame-based | rule restated as clauses (i)–(iv) in three places; `09b` rewritten to pin all six measured cases two-sided |

### Material findings

| id | finding | resolution |
|---|---|---|
| **M1** | the qualification declared `QUALIFIED` with `coverage: {}`, `mutation_ledger: {}`, `limitations: []`, `passed: null` | fully populated; the residual obligation Part I requires to be recorded is now L1 |
| **M2** | zero-track runs carry no schedule binding at all — `COMPLETE` publishes against an unrelated schedule | pinned by `test_rs01_09c`, recorded as L2 |
| **M3** | the section banner claimed "no pre-existing test was altered, renamed or weakened" — false, `test_23h` was both | banner corrected to state the rename and the duty transfer |
| **M1** (round 2) | `accepted_claims[5]` listed truncation and trailing extension as blocked | reworded to the occupied-frame / live-interval condition, with an explicit pointer to L1 |

### Accepted without change

Minors 1–3 (rs01_01's "end to end" phrasing, rs01_03's source-text greps, `disposition` written before the
review fields) were **withdrawn by the reviewer** as non-load-bearing after re-examination. Round-3 minor 1
— clause (iii) read literally would forbid a track's own intermediate point frames — is a wording
precision and was applied to the qualification text without any behaviour or test change.

### What A could not break

A built a differential oracle implementing clauses (i)–(iv) from the `TrackingResult` alone and compared
it against `qualify_lifecycle_contract` over **every** strictly-increasing schedule of length 1–6 drawn
from frames 0–13, across 12 fixtures including purpose-built MERGE, SPLIT, merge-then-dissolve,
split-then-dissolve and `TRACKING_UNRESOLVED` runs: **77,700 schedules, 0 disagreements.** It then ran 240
real `publish` + `open_analysis_access` round trips: **0 disagreements**, establishing that (i)–(iv) is an
iff for `COMPLETE` and for analysis access, not merely for lifecycle qualification. Its 14-probe bypass
battery remains fully blocked.

---

## Reviewer B — mutation, lineage and the schedule adversary

### Blocker

| id | finding | resolution |
|---|---|---|
| **B1** | the qualification of record declared `QUALIFIED` while carrying an empty mutation ledger, empty coverage, null test counts and empty limitations — the mandatory ledger reduced to `{}` is precisely what the protocol forbids | fully populated: 13-mutant ledger with per-mutant control result, mutant result, exact killing test, paired-test-alone flag and a `kill_is_semantic_not_a_hash_tripwire` field; seven tripwires listed and excluded; coverage measured; 251/0/0; seven limitations |

### Material findings

| id | finding | resolution |
|---|---|---|
| **M2** | no bound test referenced `RUNNER_INTEGRATION_00` or `RUNNER_HARDENING_00` at all — the mandatory ledger's own source could be reduced, renamed or deleted with all tests green | `test_rs01_15` byte-pins all eight documents **and** asserts the ledger's shape: three N-mutants, ten prior mandatory, survivor set exactly `{MIN-3, EQUIV}`, and the hardened runner digest equal to the current one |
| **M3** | a `Mapping` is accepted as a schedule at the runner boundary while `track_components` refuses one | pinned by `test_rs01_04c`, recorded as L3; not repaired, because repair needs a production-source change |
| **M4** | a one-shot iterator leaves an orphan lifecycle document, so `test_rs01_04`'s name "and writes nothing" over-generalised | test renamed, `test_rs01_04b` added, recorded as L4 |
| **M5** | six mutants in `_publish_new_canonical_file` die only to hash tripwires | recorded verbatim as L5; extended at round 2 with three more and marked **non-exhaustive** |

### Minors

`m6` the sweep floor `> 0` → now pinned at exactly 20 of 27. `m7` `test_rs01_13` asserted only truthiness
of the historical status fields → now asserts the `HISTORICAL - valid only for its own commit and hashes`
strings and the historical-vs-current hash inequalities. `m8` the `MIN-3` survivor no longer survives its
reconstruction → carried forward unchanged as L7 rather than silently re-classified. `m2` (round 3)
`test_rs01_09c` said "wholly unconstrained" → now distinguishes content from the well-formedness floor and
asserts `()` and `(-1,5)` are refused. `m4` (round 3) the ledger's `P1`/`P3` entries were reproducible only
by guessing patch placement → a `patch_anchor_note` records both placements. `m5` (round 3) the
coordinator's re-review request referred to a limitation "L9" that does not exist — flagged so it would
not be assumed reviewed; the limitations are exactly L1–L7.

### What B could not break

An independent predictor of clauses (i)–(iv) swept **4,131 candidate schedules across 12 tracking runs**:
546 accepted, 3,585 refused, **0 mismatches**. Four ledger-integrity attacks on `test_rs01_15` — including
reduction with the digest re-pinned and survivor renaming with the digest re-pinned — were all caught by
the layered byte-pin plus shape assertions. The full 13-mutant ledger was re-derived from the historical
documents and rerun, reproducing every recorded failure count. Sixteen further invented mutants: ten
killed semantically, six tripwire-only, of which four are provably equivalent. B concluded: *"I could not
invent a mutant that both weakens the claimed guarantee and escapes the suite."* Both drop-a-test mutants
are killed by `test_rs01_12` alone, confirming that the duty transferred from `test_23h` genuinely works.

---

## Disposition of every finding

Three blockers raised, three fixed. Nine material findings, all fixed or pinned-and-recorded. Eleven
minors: seven fixed, two withdrawn by the reviewer, two recorded as accepted observations. **Nothing was
dismissed without a reason written down.**

Two findings were deliberately **not repaired** — L3 (`Mapping` accepted) and L4 (iterator orphan) —
because repair would require modifying `future_lifecycle_runner.py`, which the frozen protocol reserves
for load-bearing failures. Neither produces false evidence and both fail closed. Reviewer B examined that
reasoning specifically and called the pins "honest, not rationalisations".

## Post-review state

- **251 passed, 0 failed, 0 skipped** under Python 3.11.15 and pytest 8.4.2, satisfying `pytest>=8.2,<9`.
- Node digest `a425c3736f0b5d819ef708c2433b785cf706381798ffc48a7ce4b5941161276a`, recomputed
  independently by both reviewers.
- Coverage of `future_lifecycle_runner.py`: **194 statements / 56 branches / 0 missed / 0 partial /
  100%**, re-measured independently by both reviewers.
- **13/13** mandatory mutants killed, every one with a non-tripwire semantic killer, rerun after the final
  edit.
- **No production source modified.** Exactly one existing file edited across the whole mission.

Both reviewers returned **PASS** against `fb5619ba2b732fca6358de6a7ad5b025fab582f3`. The disposition is
`RUNNER_STACK_REQUALIFICATION_01_QUALIFIED`, and the only authorized next action is **human review**.

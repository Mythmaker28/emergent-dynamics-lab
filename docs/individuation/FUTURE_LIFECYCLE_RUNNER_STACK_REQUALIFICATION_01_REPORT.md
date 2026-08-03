# FUTURE-LIFECYCLE-RUNNER-STACK-REQUALIFICATION-01 — report

> **Part I is the frozen evaluation protocol.** It was committed alone, as checkpoint 1, before any test
> or source file was selected or modified. Everything after the Part I terminator is append-only
> material added later. Part I is a byte-exact prefix of this document.

**Mission:** `FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01`
**Authorized parent:** `c2fe25b0cbfcffdb5f2912d5ba7fcb5e9de3d5f4`
**Branch:** `codex/future-lifecycle-runner-stack-requalification-01`
**Lineage:** `af765d2 → 9185afa → 4e1fd0c → c2fe25b`

---

# PART I — FROZEN EVALUATION PROTOCOL

## I.1 The exact claim being evaluated

> Within the committed public API and the permitted synthetic stack, no supported path may publish
> `COMPLETE` or return analysis access unless mandatory sampled-frame tracking and the lifecycle contract
> have been executed from bound inputs, their canonical evidence has been persisted, re-read and
> independently reverified, and all current successor hashes and schedule bindings match.

Nothing stronger will be asserted. The following are **explicitly not claimed** and any evidence that
appears to support them is to be read as out of scope:

- that a historical or scientific runner is wired;
- that every repository caller supplies a schedule;
- protection against source editing, monkeypatching, reflection, or a hostile verifier;
- provenance authority from SHA-256;
- scientific validity; individuality; Stage-B rehabilitation;
- readiness to open a prospective family.

## I.2 Permitted public stack boundary

The evaluated stack is exactly:

- `edlab.substrates.lattice_bond.instrumentation.track_components` — the mandatory-schedule generic tracker;
- `edlab.substrates.lattice_bond.lifecycle` — `qualify_lifecycle_contract`,
  `qualify_and_write_lifecycle_contract`, `verify_lifecycle_document`, `canonical_lifecycle_bytes`;
- `edlab.substrates.lattice_bond.future_lifecycle_runner` — `publish_future_family_completion`,
  `open_analysis_access`, and the exported error and record types.

Everything else is outside the boundary. In particular, **no real scientific runner is inside it**, and
none will be wired.

**Composition honesty rule.** `future_lifecycle_runner.py` does **not** invoke `track_components`. It
receives an already-built `TrackingResult` and a declared schedule as two separate arguments. Part I
therefore forbids any claim of direct end-to-end wiring. The mission must instead measure and report the
*strongest real binding* the actual APIs provide, and must record any position at which the two schedules
could diverge undetected as a **future real-runner obligation**, not as a solved problem.

## I.3 Current source hashes at the authorized parent `c2fe25b`

| path | sha256 |
|---|---|
| `edlab/substrates/lattice_bond/instrumentation.py` | `65d4185bd9ef212b013d8d30000499f291f043f289e3e7bccbd536f466e810ef` |
| `edlab/substrates/lattice_bond/lifecycle.py` | `3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053` |
| `edlab/substrates/lattice_bond/future_lifecycle_runner.py` | `7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08` |
| `edlab/substrates/lattice_bond/__init__.py` | `9d3bea5ac70b514b592f71c2c46738dfdaec62e0072e8055a512b2e22ac6d5b0` |
| `tests/test_lattice_bond_instrumentation.py` | `f91fd9e7c2bc20f28ad523fa224fd371f70bdc4e62bc2c81b374a412a0ee2abf` |
| `tests/test_future_lifecycle_contract.py` | `b12b34651236c526ea772ce5c15ff5b2ca4054f638340069d0178be37c297126` |
| `tests/test_future_lifecycle_runner_integration.py` | `3eecf8846477ccc875ef16481930f56ab7eb4c2770ab340f7f5a347f899ae0d8` |
| `tests/test_empty_right_nonunit_cadence_tracker_repair.py` | `50918cf0a77f0505e54e42f177de4084281dd2f05257b4e29942b2666615675e` |
| `pyproject.toml` | `e187c1a5809a4b2631bd4e9b947a00ae6790b872a970ba625d283e855a5d498c` |

The runner source `7691da35…` is the identity accepted by
`FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00` (`new_file_hashes_sha256`) and by
`FUTURE_LIFECYCLE_RUNNER_HARDENING_00` (`identity_proofs.future_lifecycle_runner_py_sha256`). It is
unchanged at `c2fe25b`.

## I.4 Permitted change allowlist

Modifiable, and nothing else:

- `edlab/substrates/lattice_bond/future_lifecycle_runner.py` — **only** if a load-bearing successor
  property cannot be established against the accepted source. The default expected result is
  requalification **without** production-source change. Any change makes this a successor implementation
  requiring full new coverage and mutation review, and must be justified precisely.
- `tests/test_future_lifecycle_runner_integration.py`
- `docs/individuation/FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_REPORT.md`
- `docs/individuation/FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_QUALIFICATION.json`
- `docs/individuation/FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01_REVIEW_JOURNAL.md`

Not modifiable: `instrumentation.py`; `lifecycle.py`; `lattice_bond/__init__.py`; the other three bound
test files; any `00` or `01R` report, qualification, review journal, human-review record or schema; any
historical integration or hardening artifact.

**If a required repair falls outside this allowlist the disposition is
`RUNNER_STACK_REQUALIFICATION_01_REVISE`.** It will not be smuggled in.

## I.5 Exact test selectors and environment

Selectors, and only these:

- `tests/test_lattice_bond_instrumentation.py`
- `tests/test_future_lifecycle_contract.py`
- `tests/test_future_lifecycle_runner_integration.py`
- `tests/test_empty_right_nonunit_cadence_tracker_repair.py`

Environment: Python 3.11.x; pytest satisfying the repository constraint `pytest>=8.2,<9`. **Qualification
under pytest 9.x is forbidden.** All tests run inside a disposable clean room outside the repository,
populated one exact allowlisted Git blob at a time, whose namespace contains no undeclared file. No glob
is used even inside the clean room. All fixtures are handcrafted synthetic data; no scientific input.

Requirements: every collected test passes; **0 failed; 0 skipped**; the complete ordered node-ID sequence
is bound in the qualification JSON together with its SHA-256; per-file collected counts are reported.

## I.6 Coverage requirements

100% statement and branch coverage of `edlab/substrates/lattice_bond/future_lifecycle_runner.py`.
Actual denominators must be **measured and reported**, never copied from the historical
194-statement / 56-branch figures. If the source is unchanged, the denominator must be **verified**
unchanged, not assumed.

## I.7 Required stack properties

1. **Mandatory schedule boundary.** `track_components` requires `sampled_frames` keyword-only; omission
   fails at the API boundary; explicit `None` fails; no supported permitted-stack call reaches the tracker
   without an explicit schedule; no compatibility alias, default, reconstructed unit cadence or
   schedule-position fallback exists; each transition's right frame derives from the declared schedule.
2. **Schedule binding downstream.** Tampering with, omitting, reordering, truncating, extending or
   substituting the schedule must prevent `COMPLETE` and analysis access. Where the current APIs cannot
   detect a divergence, that exact case must be stated as a residual limitation and a future real-runner
   obligation.
3. **Disappearance remains countable.** Through the supported stack, with handcrafted synthetic masks
   only: declared non-unit cadence accepted; an empty right detector frame representing disappearance not
   globally rejected; disappearance retained as terminal information; exactly-one-terminal accounting
   enforced; a malformed or ambiguous lifecycle cannot unlock analysis. At least one full synthetic
   example at schedule `(0, 5, 11, 12)`.
4. **Lifecycle non-bypassability.** No supported public path may construct or trust a hand-authored
   `QUALIFIED` disposition without executing validation; publish `COMPLETE` before canonical persistence;
   trust in-memory evidence without re-reading it; return analysis access without independent
   re-verification; substitute a plain write for the atomic publication path; or reuse stale evidence from
   the historical lifecycle qualification.
5. **Current lineage binding.** The successor qualification binds at minimum: `c2fe25b`, `9185afa`,
   `4e1fd0c`, `c2fe25b`; current `instrumentation.py`, `lifecycle.py`, `future_lifecycle_runner.py`;
   current integration tests and all other bound selectors; the complete collected node-ID sequence and
   its digest; the reviewer checkpoint; the final qualification commit. Historical integration and
   hardening qualifications remain unchanged and are described as valid **only** for their original
   commits and hashes.
6. **Hardening preservation.** Every load-bearing hardening property is re-proved. The mandatory mutant
   ledger is extracted from the exact allowlisted qualification documents and **rerun in full**; it may
   not be silently reduced or renamed. Per mutant: control result, mutant result, exact killing test,
   whether the paired test kills it alone, whether the pre-existing suite kills it, and why the kill is
   semantic rather than a hash tripwire. Hash-only tripwires are excluded from reported semantic coverage.

## I.8 Qualification, revision and stop criteria

`RUNNER_STACK_REQUALIFICATION_01_QUALIFIED` requires **all** of: no firewall breach; every required stack
property proved or its limitation explicitly recorded; all collected tests pass with 0 failed and 0
skipped under the pinned environment; 100% statement and branch coverage with measured denominators;
every load-bearing mutant killed or explicitly carried forward as a disclosed out-of-scope survivor with
its historical assessment; historical artifacts unchanged; lineage bound; and **both** independent
reviewers returning PASS against the same final source/test checkpoint.

`RUNNER_STACK_REQUALIFICATION_01_REVISE` if a required repair falls outside the allowlist, a load-bearing
property cannot be established, or a reviewer blocker stands.

`STOP_RUNNER_STACK_REQUALIFICATION` immediately upon any scientific-firewall breach.

**One FAIL controls. There is no majority voting.**

## I.9 Reviewer independence rules

Two independent adversarial reviewers are launched after the implementation/test checkpoint. Each
receives only: this frozen protocol; the exact permitted source and tests; the exact successor evidence;
the closed synthetic clean room; and the historical integration/hardening qualification documents by
exact path. Reviewer A audits public API and non-bypassability. Reviewer B audits mutation, lineage and
the schedule adversary. Each returns PASS or FAIL with blockers, material findings, minors and
observations. Every valid finding is applied within the allowlist, a new checkpoint is created, and
targeted re-review is requested, until both PASS against the same final commit or a blocker forces
revision. A reviewer must stop immediately if it needs an undeclared path.

## I.10 Scientific-firewall rules

Only predeclared exact Git object paths. Forbidden throughout the mission and both reviews: directory
listings; globs or wildcards; `git status`; `git ls-tree -r`; tree-wide `git diff --name-only` or
`--name-status`; `find`; `rg --files`; broad `git grep`; archive-on-tree operations; traversal followed by
filtering; project-memory search; opening any undeclared path. If a declared path is absent, stop — do not
search for a replacement.

Not to be opened, enumerated, named, hashed, inspected or executed: scientific shards or manifests; world
records or per-world metadata; trajectories; candidate records; reconstructed checkpoints; autopsy inputs;
result directories; scientific or historical runners; prospective namespaces; Stage-B material; Kovacs
material; global project indexes.

## I.11 Prohibition on real-runner wiring

This mission may not wire a real scientific runner, open or execute Stage B, begin Route E or Route G, or
create a family, seed, namespace, experiment or scientific result. The only authorized next action after
success is **human review of `FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01`**, which this mission may
not begin.

## I.12 Append-only rule for this document

Part I may receive **only** append-only material after this line. Nothing above the terminator may be
rewritten, reordered or deleted. Rejected candidate material is preserved under an explicit superseded
banner with corrections appended beneath it, never silently rewritten.

<!-- END OF FROZEN PART I — nothing above this line may change -->

---

# PART II — RESULTS (append-only)

**Terminal disposition: `RUNNER_STACK_REQUALIFICATION_01_QUALIFIED`**

Everything below was appended after Part I was committed alone as checkpoint 1. Part I is a byte-exact
prefix of this document.

## II.1 Checkpoints

| # | commit | content |
|---|---|---|
| 1 | `bc801c1ab625a3a5a1c29f9d5333b45f49b7c079` | frozen Part I evaluation protocol, alone |
| 2 | `9a1bfaff42009f3ae336c4d875eb18e0ab9a6fb5` | successor tests + preliminary qualification binding |
| 3 | `fb5619ba2b732fca6358de6a7ad5b025fab582f3` | independent-review fixes — **the final reviewed source/test commit** |
| 4 | this commit | sealed report, qualification and review journal |

**No production source was modified.** `future_lifecycle_runner.py` is byte-identical at
`7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08` to the identity accepted by both
`FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00` and `FUTURE_LIFECYCLE_RUNNER_HARDENING_00`. `instrumentation.py`,
`lifecycle.py` and `lattice_bond/__init__.py` are unchanged. Exactly one existing file was edited:
`tests/test_future_lifecycle_runner_integration.py`.

## II.2 The composition boundary — measured, mis-stated twice, then correctly stated

This is the mission's central result and the place where the review earned its keep.

`future_lifecycle_runner.py` does **not** invoke `track_components`. It receives an already-built
`TrackingResult` and a declared schedule as two separate arguments. Part I therefore forbade any claim of
direct end-to-end wiring and required the *strongest real binding* to be measured instead.

It was measured wrongly twice.

- **Round 0** claimed the residual was a single position that is both detector-empty and event-free.
  Reviewer A falsified this: the divergence class is unbounded in size.
- **Round 1** claimed extension was possible anywhere with no point and no event, subject to monotonicity
  and *preserving the horizon*. Reviewer A falsified this in **both** directions: the horizon is not
  preserved in general; truncation is also possible; prefix extension is available to occupied runs; and
  an unoccupied inserted frame is still refused inside a live interval.

Both wordings are preserved in the qualification's `superseded_claims` with their falsifiers, and in the
test module under an explicit superseded marker. Nothing was silently rewritten.

**The rule, as finally measured and independently confirmed.** Let `OCCUPIED` be every track-point frame
together with every event frame. A declared schedule is accepted iff

1. it is non-empty, strictly increasing, non-negative integers;
2. it contains every `OCCUPIED` frame;
3. it contains no frame *other than that track's own point frames* strictly inside any track's point span,
   and none strictly between a track's last point and that track's terminal-event frame;
4. if some track's last point sits at the tracker's final frame, the declared last entry must equal it —
   **otherwise the tail is free, both to extend arbitrarily and to truncate**.

A zero-track run occupies nothing, so (2)–(4) are vacuous and only the well-formedness floor (1) survives.

Consequences, each pinned by a test rather than asserted in prose: a three-sample run can be published as
ending 1,000,000 frames later; an unoccupied trailing frame can be deleted; prefix extension is available
to every run that does not begin at frame 0; and a run occupied from frame 0 to the horizon admits nothing
at all.

**Why the binding is nonetheless real.** Because 01R made the tracker stamp every event frame *from* the
declared schedule, a disappearance at an empty detector frame is itself witnessed. That is why a
value substitution at frame 5 is caught on a run where frame 5 has no component at all. Every perturbation
that removes or displaces an occupied frame, or inserts into a live interval, blocks `COMPLETE` and writes
nothing.

**Recorded as limitation L1, a future real-runner obligation:** a real runner must hand *one* schedule
object to both the tracker and the publisher. This mission does not wire one.

## II.3 Required stack properties — result

| # | property | result |
|---|---|---|
| 1 | mandatory schedule boundary | **PROVED.** `sampled_frames` is keyword-only, no default, non-optional; omission is a `TypeError`, explicit `None` a `ValueError`; `_transition_right_frame` is absent, no `range(len(frames))`, no alias; each transition's right frame comes from the schedule. `test_rs01_02`, `test_rs01_03`. |
| 2 | schedule binding downstream | **PROVED WITH A STATED RESIDUAL.** See II.2 and limitation L1. Every witnessed perturbation blocks and writes nothing; the unwitnessed class is measured, pinned two-sided, and marked a future real-runner obligation. |
| 3 | disappearance remains countable | **PROVED.** Full synthetic example at schedule `(0, 5, 11, 12)`: `DISSOLVED_DETECTED_TRACK` @ 5 alongside `RIGHT_CENSORED_AT_HORIZON` @ 12, `len(terminal_records) == len(tracks) == terminal_record_count`, `COMPLETE` published, analysis unlocked. A 27-run sweep at `(0, 5, 11)` — 20 of them containing a disappearance, pinned exactly — qualifies in every case. A lifecycle stripped of its `DISSOLUTION` fails closed at qualification, at publication and at analysis. `test_rs01_01`, `test_rs01_10`, `test_rs01_11`. |
| 4 | lifecycle non-bypassability | **PROVED.** Reviewer A's 14-probe bypass battery — hand-authored manifests, manifest-only and lifecycle-only directories, non-canonical bytes, duplicate JSON keys, extra/missing keys, version fields, symlinked and hardlinked evidence, symlinked run directory and publication target, dangling symlinks, republication, direct `AnalysisAccess` construction — is fully blocked. All twelve manifest fields are tamper-covered (Reviewer B enumerated them from source). `test_rs01_08` and the pre-existing suite. |
| 5 | current lineage binding | **PROVED.** `test_rs01_13` binds the four ancestry commits and every source and test hash; `test_rs01_12` re-collects the node list live against the successor qualification; `test_rs01_15` byte-pins the eight historical runner-package documents, the ledger's shape and the 01R qualification. |
| 6 | hardening preservation | **PROVED.** The full 13-mutant mandatory ledger was extracted from the exact allowlisted qualifications, rerun after checkpoint 3, and 13/13 killed — each with at least one semantic killer that is not a hash tripwire. |

## II.4 Tests, coverage and mutation

| quantity | value |
|---|---|
| selectors | the four exact bound test files |
| collected / passed / failed / skipped | **251 / 251 / 0 / 0** |
| per-file collected | 63 / 52 / 87 / 49 |
| canonical node-list digest | `a425c3736f0b5d819ef708c2433b785cf706381798ffc48a7ce4b5941161276a` |
| Python / pytest | 3.11.15 / **8.4.2**, satisfying the declared `pytest>=8.2,<9` |
| coverage of `future_lifecycle_runner.py` | **194 statements, 0 missed; 56 branches, 0 partial; 100%** |

The coverage denominators were **measured**, not copied. They coincide with the historical
`INTEGRATION_00` figures because the source is byte-identical — that is a verification, and both reviewers
re-measured them independently.

**Mutation.** 13 mandatory mutants (N1–N3 from `HARDENING_00`'s `mutation_proof`, P1–P10 from its
`prior_mandatory_mutant_results`), all killed, each with a named non-tripwire semantic killer and each
killed by its paired test alone. Seven tests in this suite are pure hash tripwires that fire on any byte
change to a bound file; they are listed explicitly in the qualification and **excluded** from every
reported semantic count, so "13/13" is not read as coverage it has not earned. The two disclosed
out-of-scope survivors `MIN-3` and `EQUIV` are carried forward with the reviewers' assessments rather than
silently re-classified.

## II.5 Historical treatment

`FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00` and `FUTURE_LIFECYCLE_RUNNER_HARDENING_00` are **unchanged** and
are described throughout as valid **only for their own commits and hashes**. Each bound a different
integration-test file and a different `instrumentation.py` than this tree, and `test_rs01_13` now asserts
those inequalities rather than merely asserting the fields are present. Before `test_rs01_15` no bound test
referenced either package at all — the mandatory ledger could have been reduced or deleted with the suite
green. That hole is closed and Reviewer B verified the closure with four ledger-integrity attacks,
including reduction and survivor-renaming with the digest re-pinned to match.

## II.6 Limitations, recorded rather than smoothed over

| id | severity | limitation | pinned by |
|---|---|---|---|
| L1 | MATERIAL | the schedule is bound only on occupied frames and live intervals; elsewhere it is free in **both** directions | `test_rs01_09a/09b` |
| L2 | MATERIAL | a zero-track run's schedule **content** is wholly unconstrained (the well-formedness floor still holds) | `test_rs01_09c` |
| L3 | MINOR | a `Mapping` is accepted as a schedule at the runner boundary although the tracker refuses one | `test_rs01_04c` |
| L4 | MINOR | a one-shot iterator schedule leaves an orphan lifecycle document behind a refused publication | `test_rs01_04b` |
| L5 | MINOR | at least nine mutants in `_publish_new_canonical_file`'s defensive layer die only to hash tripwires; the list is **non-exhaustive** | — |
| L6 | OBSERVATION | the evidence is content-addressed, not provenance-bound — copying a genuine pair unlocks analysis elsewhere (documented in the module docstring) | pre-existing |
| L7 | OBSERVATION | the historical `MIN-3` survivor disclosure may be stale; carried forward unverified | — |

L3 and L4 were **not repaired**: repair requires a production-source change, which Part I reserves for
load-bearing failures. Neither produces false evidence, and both fail closed.

## II.7 Firewall

**No breach.** Only predeclared exact Git object paths. Zero directory listings, globs, wildcards,
`git status`, `git ls-tree -r`, tree-wide `--name-only`/`--name-status`, `find`, `rg --files`, broad
`git grep`, archive-on-tree operations, listing-then-filter, or project-memory searches; zero undeclared
paths opened. The clean room held exactly 31 declared files, each byte-verified against its `c2fe25b`
blob, and no glob was used inside it. Both reviewers operated under the same allowlist and confirmed the
same. No scientific shard, manifest, world record, trajectory, candidate record, checkpoint, autopsy
input, results directory, scientific or historical runner, prospective namespace, Stage-B or Kovacs
material was opened, enumerated, named, hashed or executed. No engine, runner, simulation or sweep was
run; no seed and no namespace allocated. Every fixture is a handcrafted synthetic boolean mask.

## II.8 Qualification boundary

- This is **synthetic mechanical requalification**.
- The generic tracker and the synthetic future-runner stack are qualified, within the boundary of II.2.
- **No historical runner has been changed.**
- **No real runner is wired.**
- **No scientific family is authorized.**
- **No Stage-B result changes.**
- **No prospective route is selected. Route G remains deferred.**
- **Real-runner wiring remains a separate governance decision.**

## II.9 Only authorized next action

**Human review of `FUTURE_LIFECYCLE_RUNNER_STACK_REQUALIFICATION_01`.** This mission does not begin it,
and authorizes nothing else.

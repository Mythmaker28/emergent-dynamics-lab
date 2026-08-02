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

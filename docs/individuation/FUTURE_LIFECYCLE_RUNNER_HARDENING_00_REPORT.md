# FUTURE-LIFECYCLE-RUNNER-HARDENING-00 — report

## Disposition

**HARDENING_QUALIFIED**

Engineering only. This mission closed two minor debts from the independent human-review audit and bound
the test selectors. It changed **no production source**, wired the skeleton into **no runner**, executed
**no scientific code**, and opened **no scientific material**. It establishes nothing about
individuality, ownership, persistence, life, death or feasibility, and it authorizes no scientific
execution.

## Authority

- Branch: `codex/future-lifecycle-runner-integration-00-human-review`
- Commit: `a2d44c6f9a9decc4c2cc822fcd4c2ef1e4b34b02`
- Disposition: `HUMAN_REVIEW_ACCEPTED`
- Accepted integration candidate: `23df99dc471558f18316e23e7c176e3d385a24eb`
- Authorized integration parent: `b2331d75153763c8efbfbcd401084a331584f259`
- Accepted lifecycle ancestor: `4282fc6ead915639711f5096c7825d3880a640d4`
- This branch: `codex/future-lifecycle-runner-hardening-00`, rooted at the human-review commit so the
  hardening physically contains its own authorization.

## Mandatory preflight

All eight checks passed before anything was written.

| # | Check | Result |
|---|---|---|
| 1 | `a2d44c6` exists | **PASS** — resolves to `commit` |
| 2 | Direct descendant of `23df99d` | **PASS** — sole parent is `23df99d` |
| 3 | Human-review disposition | **PASS** — `HUMAN_REVIEW_ACCEPTED` |
| 4 | All 11 integration/lifecycle hashes | **PASS** — 11/11 recompute at `a2d44c6` |
| 5 | Seven bound lifecycle files blob-identical to `4282fc6` | **PASS** — 7/7 |
| 6 | Original dirty `main` checkout hashed | **PASS** — `f3921a4d…`, `main`, 21 lines, status SHA-256 `54c57f2a…8bba7dea` |
| 7 | Integration module and 51-test file match the accepted candidate | **PASS** — blobs `44135ee7…` and `ca59e37f…` identical at `23df99d` and `a2d44c6` |
| 8 | No hardening branch already exists | **PASS** — absent |

## Checkpoints

| Commit | Content |
|---|---|
| `7facb41f3165b1225f85960beb7043f1ae05e9f7` | three MIN-2 regressions added; selector-binding method frozen |
| `c1faa07a53df69e6cd5836c42c2d4a761a5b283c` | Reviewer A MINOR-1 fix — **final test-file commit** |
| *(this commit)* | report, qualification JSON and review journal |

---

## MIN-1 — additive erratum

**This is an erratum. It corrects the record additively. No frozen artifact is rewritten.**

`docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_REPORT.md` and
`docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_QUALIFICATION.json` are **deliberately left
byte-identical** to their accepted state at `23df99d`. They are hash-bound evidence that a human
accepted at `a2d44c6`; editing them in place would destroy the immutability that makes them evidence.

### Exact stale locations

1. `docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_QUALIFICATION.json`, key
   `diff_versus_accepted_lifecycle_parent`: `{"added": 4, "modified": 0, "deleted": 0,
   "tree_file_count_before": 2121, "tree_file_count_after": 2125}`.
2. `docs/individuation/FUTURE_LIFECYCLE_RUNNER_INTEGRATION_00_REPORT.md`, line 310:
   *"`git diff --name-status 4282fc6 <final>` is four `A` entries and zero `M` or `D`, cross-checked by
   tree size 2121 → 2125 files."*

### Where the stale figure was correct

The figure `4 added / 2121 → 2125` is **exactly correct** at the three intermediate implementation and
review checkpoints, each independently verified:

| Commit | `4282fc6 → …` | Tree size |
|---|---|---|
| `6dfef7cdd13c9299d59bdbcd5a3c7150f19dc435` | 4 `A`, 0 `M`, 0 `D` | 2125 |
| `68d6a29a2437a78f54cda828d573c89e298332af` | 4 `A`, 0 `M`, 0 `D` | 2125 |
| `68c6a8eb0c6b4ee443630ed9d96b1e0199b2a03f` | 4 `A`, 0 `M`, 0 `D` | 2125 |

Reviewer B of the integration mission recorded the cross-check at `68d6a29a`, where it was true. The
error is one of **scope, not of measurement**: the number was carried forward into a sentence and a JSON
key that describe the *final qualified commit*, where it no longer holds. The original author is not
mischaracterised.

### Corrected figures

**Accepted integration candidate versus lifecycle parent — `4282fc6 → 23df99d`**

- **six** added files
- **zero** modified files
- **zero** deleted files
- repository file count **`2121 → 2127`**

The six additions are the **five integration mission files** plus the **inherited lifecycle-contract
human-review record** `docs/individuation/FUTURE_LIFECYCLE_CONTRACT_00_HUMAN_REVIEW.md`, which entered
the lineage at `b2331d7` and is therefore counted against `4282fc6` but not against `b2331d7`.

**Accepted integration candidate versus authorized integration parent — `b2331d7 → 23df99d`**

- **five** added mission files
- **zero** modified files
- **zero** deleted files
- repository file count **`2122 → 2127`**

**Integration human-review commit — `23df99d → a2d44c6`**

- **one** added human-review record
- **zero** modified files
- **zero** deleted files
- repository file count **`2127 → 2128`**

**For completeness, this hardening mission — `4282fc6 → c1faa07`**

- **seven** added files, **zero** deleted
- **one** modified file: `tests/test_future_lifecycle_runner_integration.py` (test-only)
- repository file count **`2121 → 2128`**

The additive-only property of the integration package is **unaffected** by the correction: zero `M` and
zero `D` entries in every comparison above, and every addition is an allowlisted mission file or an
inherited decision record.

---

## MIN-2 — three direct manifest-field tampering regressions

Three focused behavioural tests were added to `tests/test_future_lifecycle_runner_integration.py`.
Each one publishes a valid synthetic completion package through the supported public API, reads the
canonical `COMPLETION.json`, alters **exactly one** semantic field to a structurally well-formed but
different value, reserialises canonically, calls `open_analysis_access`, and proves that access fails
closed.

| Test | Field | Replacement | Outcome |
|---|---|---|---|
| `test_37_tampered_lifecycle_input_digest_blocks_analysis` | `lifecycle_input_sha256` | `"a1" * 32` — a different valid 64-char lowercase hex digest | `CompletionEvidenceError` |
| `test_38_tampered_lifecycle_records_digest_blocks_analysis` | `lifecycle_records_sha256` | `"b2" * 32` — a different valid 64-char lowercase hex digest | `CompletionEvidenceError` |
| `test_39_tampered_manifest_sampling_schedule_blocks_analysis` | `sampled_frames` | `[0, 6]` replacing the genuine `[0, 5]` — same length, strictly increasing, non-negative, valid JSON | `CompletionEvidenceError` |

The rejection message in all three cases is
`completion manifest bindings do not match the reverified lifecycle contract`, raised at the
**rebuilt-manifest binding comparison** in `open_analysis_access`.

**The failure site is proven, not assumed.** A shared helper,
`_assert_reaches_binding_comparison`, asserts every guard that precedes the binding comparison —
canonical byte equality, JSON round-trip, key set, `schema_version`, `integration_version`,
`lifecycle_schema_version`, `lifecycle_validator_version`, `canonicalization`, `disposition`,
`lifecycle_document_relative_path` and the lifecycle-document digest — so a test that short-circuited at
an earlier guard would fail before it reached its `pytest.raises`. Reviewer A additionally walked each
traceback outside pytest and confirmed all three land on the same line, with `__cause__ is None`, and
that each is a `CompletionEvidenceError` and not a `LifecycleEvidenceError`.

Reviewer A verified programmatically — by diffing each tampered manifest against the genuine published
one — that **exactly one field differs** in every case. No test alters more than one semantic field.

### Manifest-key coverage is now complete

With these three, all twelve `_MANIFEST_KEYS` have a direct tampering regression: `test_32` parametrises
`schema_version`, `integration_version`, `lifecycle_schema_version`, `lifecycle_validator_version`,
`canonicalization` and `lifecycle_document_relative_path`; `test_11` covers `lifecycle_document_sha256`;
`test_12` covers `terminal_record_count`; `test_12b` covers `disposition`; and `test_37`/`38`/`39` cover
the remaining three. No redundancy, no gap.

---

## Mutation proof

Three precise semantic mutants were constructed **in disposable copies outside the repository**, one per
audit-surviving MIN-2 mutant. Each inserts a single line into `open_analysis_access` immediately after
`expected = _build_manifest(verified, _sha256_bytes(document))`, making the rebuilt manifest adopt the
value the manifest itself declares:

| # | Mutant patch | Control (committed code) | Mutant result | Killed by | Paired test alone | Killed by any pre-existing test | Non-incidental |
|---|---|---|---|---|---|---|---|
| N1 | `expected['lifecycle_input_sha256'] = manifest['lifecycle_input_sha256']` | 54 passed, 0 failed | 1 failed, 53 passed | `test_37` **only** | **KILLED** | **no** — all 136 pre-existing tests pass | ✅ |
| N2 | `expected['lifecycle_records_sha256'] = manifest['lifecycle_records_sha256']` | 54 passed, 0 failed | 1 failed, 53 passed | `test_38` **only** | **KILLED** | **no** | ✅ |
| N3 | `expected['sampled_frames'] = manifest['sampled_frames']` | 54 passed, 0 failed | 1 failed, 53 passed | `test_39` **only** | **KILLED** | **no** | ✅ |

The kill reason is the intended one in every case: `pytest.raises` sees no exception, i.e. analysis
wrongly succeeded. The correspondence is exactly one-to-one — each mutant is invisible to the entire
pre-existing suite and visible only to its own paired test, with no cross-kill between the three new
tests. Each regression is therefore independently load-bearing. The mutant runs also serve as the
positive control the tests lack internally: with the paired mutant applied, the identical fixture and
tamper *does* open access, so the fail-closed behaviour is caused by the tamper and by nothing
incidental.

### All ten previously mandated mutation protections remain green

| Mutant | Result |
|---|---|
| Atomic publication replaced by ordinary `write_bytes` | **KILLED** — `test_33_completion_published_mid_flight_is_never_clobbered` |
| Skip the persisted-lifecycle reread | **KILLED** |
| Skip lifecycle verification before completion | **KILLED** |
| Trust the manifest digest without rereading the lifecycle document | **KILLED** |
| Ignore a changed sampling schedule | **KILLED** |
| Accept a caller-constructed closure or nominal `QUALIFIED` | **KILLED** |
| Skip completion-manifest canonicality verification | **KILLED** |
| Skip terminal-count consistency | **KILLED** |
| Return analysis access after verification failure | **KILLED** |
| Allow an existing completion target to be overwritten | **KILLED** |

Two mutants remain outside this mission's scope and are recorded rather than repaired. **MIN-3** — the
inline `exists()` plus `write_bytes` variant — survives; it is not the committed implementation, was
disclosed at integration review as A-NF3, and the human decision required no repair. The
"digest the in-memory canonical bytes instead of the disk bytes" mutant also survives and is a **provably
equivalent mutant**: the immediately preceding check asserts the two byte strings are equal.

---

## Exact selector binding

The historical `61`-test ambiguity is eliminated. The qualification JSON records the exact pytest
command, complete file-level selectors, **all 139 collected node IDs in deterministic order**, the
SHA-256 of the canonical node-ID sequence, the SHA-256 of each selected test file, the pytest and Python
versions, the platform, and the collection and pass/fail/skip counts.

```
python3 -m pytest \
  tests/test_future_lifecycle_contract.py \
  tests/test_future_lifecycle_runner_integration.py \
  tests/test_lattice_bond_instrumentation.py \
  -p no:cacheprovider -q
```

Selectors are **complete files**. No arbitrary 11-test subset was recreated.

| Selected file | SHA-256 | Collected |
|---|---|---|
| `tests/test_future_lifecycle_contract.py` | `e940199e7befaf7e60535867525d163e3abc807a951265c78a5f7b1d0acddd47` | 50 |
| `tests/test_future_lifecycle_runner_integration.py` | `84a2087883b0e590eade37ee687ab7daaec6fbf9870f1df82319133e3bdcf401` | 54 |
| `tests/test_lattice_bond_instrumentation.py` | `d0d49e6f88d9b7faa5e4af3da33dd1f4a59d5575dfc97ddaf2e69a7af233c22b` | 35 |
| **total** | — | **139** |

- Node-ID sequence SHA-256: `f56f09bf39b93182fb9cfbf9e90ae6077d709352b248e0bc25c4f17117d74fd3`
  (node IDs joined with a single newline, one trailing newline, UTF-8).
- The integration count became **54** only after collection verified exactly three new cases; it was not
  hardcoded in advance.
- Environment: pytest 9.1.1, Python 3.11.15, `Linux-6.18.5-x86_64-with-glibc2.39`, numpy 2.4.4.

`tests/test_lattice_bond_instrumentation.py` is **byte-identical at `4282fc6` and at `c1faa07`** (same
blob `c70415ff931a4972af680aa55e8fde3f6ae054b7`). The historical eleven were therefore a strict subset of
today's thirty-five, and running the whole file strictly dominates the unrecoverable selection.

---

## Verification

Executed in an isolated cloud clean-room whose every `.py` and `.json` file was verified byte-identical
to the committed blobs before any test ran. The device toolchain has neither network access nor pytest,
so tests could not be run there; the modified test file was transported to the device and its SHA-256
verified identical to the tested artifact, and both reviewers independently re-verified that identity at
the final commit.

| Suite | Result |
|---|---|
| Bound lifecycle contract suite (file byte-identical) | **50 passed, 0 failed, 0 skipped** |
| Runner integration suite | **54 passed, 0 failed, 0 skipped** |
| Instrumentation suite | **35 passed, 0 failed, 0 skipped** |
| All three permitted files together | **139 passed, 0 failed, 0 skipped** |
| Branch coverage of `future_lifecycle_runner.py` | **100%** — 194 statements, 0 missed, 56 branches, 0 partial |

The coverage denominator is **unchanged** from the integration qualification (194 / 56), as it must be:
the production module is byte-identical.

### Identity proofs

- `edlab/substrates/lattice_bond/future_lifecycle_runner.py` is the **same git blob**
  `44135ee74d8a19bdd1cbdb8e1a38fa0ecb728ff4`, SHA-256
  `7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08`, at `23df99d`, `a2d44c6`, `7facb41`
  and `c1faa07`.
- All **seven** bound lifecycle deliverables remain blob-identical to `4282fc6`.
- Neither JSON Schema was modified; `instrumentation.py` was not repaired.
- The integration test file grew from 39 743 to 45 499 bytes; its **first 39 743 bytes remain
  byte-identical** to the accepted `d1600bcac91c7d7e5a3802d114b31c4b71e032ddfcb31487a4792ae6faf86da1`.
  The accepted file is a strict byte-prefix of the hardened one.
- The original dirty `main` checkout is unchanged: `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, branch
  `main`, 21 status lines, status SHA-256
  `54c57f2ad57f9ba7c7d2f3310d8b7f91f482e0f48b66dae518aeae9b8bba7dea`, before and after.

---

## Independent review

Two independent read-only reviewers, two rounds each, recorded in
`FUTURE_LIFECYCLE_RUNNER_HARDENING_00_REVIEW_JOURNAL.md`. Both returned `PASS` in both rounds, and both
final verdicts bind explicitly to the final test-file commit `c1faa07`.

Round 1 produced one **MINOR** finding from Reviewer A: `_assert_reaches_binding_comparison`'s docstring
claimed the tampered manifest "must survive every check that precedes the binding", but the helper did
not mirror three of those guards — `lifecycle_schema_version`, `lifecycle_validator_version` and
`canonicalization`. That was fixed at `c1faa07` by adding the three assertions, and Reviewer A confirmed
in round 2 that each new assertion is real and falsifiable (each fires at its own line when its field is
tampered) and that MINOR-1 is closed.

Reviewer B raised one **MATERIAL** finding against the *frozen integration record* — that the stale
`4 added / 2121 → 2125` figure survives verbatim at `23df99d`, `a2d44c6` and `c1faa07`. **That finding is
MIN-1**, and it is what this erratum closes. Reviewer B judged the additive-erratum disposition
**adequate**, on the reasoning that rewriting a hash-bound record a human has already accepted would
destroy the evidence, and conditioned closure on the erratum stating the corrected figures exactly,
naming the exact stale locations, and recording where the stale figure was correct. All three conditions
are met above, and Reviewer B independently confirmed every corrected figure.

No production-source fix was required at any point, so `HARDENING_INSUFFICIENT` was never triggered.

---

## Firewall

No physics shard, shard filename or manifest, world name or per-world metadata, trajectory, candidate
record, reconstructed checkpoint, failed-autopsy input, `results/` directory, prospective or `54xxx` seed
namespace, global project index, `stage_b.py`, `stage_b_reproduce.py` or Kovacs material was opened by
this mission or by either reviewer. No engine and no scientific runner was executed. No historical family
was retrofitted, no successful historical world selected, no scientific preregistration created, and **no
scientific outcome emitted**. The clean-room materialises only permitted files, so the firewall held by
construction rather than by discipline alone.

## Frozen dispositions

`STOP-LOCAL-CUT`, `STOP-OWNERSHIP-IDENTIFIABILITY`, `FINAL_STOP_ARCHITECTURE_CONFIRMED`,
`DEV_FEASIBILITY_FAIL`, `AUDIT_INVALID`, `FUTURE_LIFECYCLE_CONTRACT_QUALIFIED`,
`RUNNER_INTEGRATION_QUALIFIED` and Kovacs `SCALAR_ONLY_FEASIBLE → STOP_PROSPECTIVE` all remain fully in
force. This mission revises none of them.

## Claim, and its limits

**Claimed.** MIN-1 is corrected by an additive erratum without rewriting any frozen artifact; MIN-2 is
closed by three direct manifest-field tampering regressions that each kill their paired semantic mutant
non-incidentally; the exact pytest selectors, collected node IDs and test-file hashes are bound; and the
production module is byte-identical to the accepted integration candidate.

**Not claimed.** Nothing about the gate's behaviour or scope has changed. The repository is not gated,
no existing runner is gated, the historical Stage-B runner is not gated, and the skeleton is wired into
no runner. No protection is claimed against source modification, monkeypatching, reflection or
subclassing. Replayed, relocated and symlinked valid evidence are still accepted. No scientific claim,
provenance or authorization is asserted.

## Terminal disposition and next action

**HARDENING_QUALIFIED.**

The only authorized next action is **human review of this hardening package**. No scientific stage is
authorized. A real-runner wiring mission is not authorized. Stage C, a new scientific family, a
prospective seed namespace and any reinterpretation of `DEV_FEASIBILITY_FAIL` all remain prohibited.

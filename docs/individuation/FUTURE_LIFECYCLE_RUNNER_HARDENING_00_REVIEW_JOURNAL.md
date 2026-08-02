# FUTURE-LIFECYCLE-RUNNER-HARDENING-00 — independent adversarial review journal

Two independent read-only reviewers were engaged after the implementation and its focused tests passed.
Neither modified any file, and neither had write access to any commit. Both were bound by the same
prohibited-material firewall as the mission. Two rounds were run: an initial full review, and a targeted
re-review of the fix that binds explicitly to the final test-file commit.

- **Reviewer A** — regression and mutation reviewer. Worked exclusively in the cloud clean-room and in
  disposable copies under `/tmp/reviewA*`. No device access.
- **Reviewer B** — traceability and firewall reviewer. Worked read-only against both the device
  repository and the cloud clean-room. Every git command was read-only plumbing.

---

## Round 1 — initial review

Candidate commit: `7facb41f3165b1225f85960beb7043f1ae05e9f7`.

### Reviewer A — `PASS`

Method: byte-level hash verification of the frozen baseline; programmatic diffing of each tampered
manifest against the genuine published manifest to count the fields that actually changed; traceback
walking outside pytest to pin the exact raise site; a mutation battery in disposable copies; and
re-execution of the previously mandated gate mutants.

Per-test result — all three tests confirmed to mutate **exactly one** field, and all three failures
confirmed to land on the rebuilt-manifest binding comparison with `__cause__ is None`:

| Test | Field | Replacement | Fields differing vs genuine | Exception | Failure site |
|---|---|---|---|---|---|
| `test_37` | `lifecycle_input_sha256` | `"a1" * 32` | exactly 1 | `CompletionEvidenceError` | binding comparison ✅ |
| `test_38` | `lifecycle_records_sha256` | `"b2" * 32` | exactly 1 | `CompletionEvidenceError` | binding comparison ✅ |
| `test_39` | `sampled_frames` | `[0, 6]` | exactly 1 | `CompletionEvidenceError` | binding comparison ✅ |

Mutation result — a **one-to-one** correspondence, the strongest available outcome:

| Mutant | Full suite | Killer | Paired test alone | Pre-existing suite only |
|---|---|---|---|---|
| trust manifest `lifecycle_input_sha256` | 1 failed / 138 passed | `test_37` only | KILLED | 136 passed — **survives** |
| trust manifest `lifecycle_records_sha256` | 1 failed / 138 passed | `test_38` only | KILLED | 136 passed — **survives** |
| trust manifest `sampled_frames` | 1 failed / 138 passed | `test_39` only | KILLED | 136 passed — **survives** |

Prior gate mutants, independently reconstructed: the `write_bytes` mutant is **KILLED** by `test_33`;
returning access right after the manifest field checks is **KILLED** by 14 tests; deleting the
canonicality check is **KILLED** by `test_13`; returning access in the `except LifecycleContractError`
branch is **KILLED** by 7 tests; and overwriting an existing completion target is **KILLED** in both the
writer-guard form (`test_25`, `test_33`) and the true-overwrite form (`test_19`, `test_19b`, `test_25`,
`test_26`, `test_28`, `test_33`). No prior gate survives.

Suite: 139 collected, 139 passed, 0 failed, 0 skipped — stable over three repeats, in per-test isolation
and under `-k` subselection. Coverage: 194 statements, 0 missed, 56 branches, 0 partial, 100%.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| A-MINOR-1 | **MINOR** | `_assert_reaches_binding_comparison`'s docstring claims the manifest "must survive **every** check that precedes the binding", but the helper did not mirror `lifecycle_schema_version`, `lifecycle_validator_version` or `canonicalization`. Harmless in practice — none of the three tests touches those fields, and the true raise site was proven independently — but the docstring overclaimed. | **FIXED** in round 2 |
| A-NOTE-1 | NOTE | `tests/test_lattice_bond_instrumentation.py` had no supplied expected hash in round 1, so it could only be checked circumstantially. Reviewer B subsequently bound it against Git. | Resolved by Reviewer B |
| A-NOTE-2 | NOTE | `assert not isinstance(caught.value, LifecycleEvidenceError)` is unfalsifiable today: the two classes are siblings under `RunnerIntegrationError`, so `pytest.raises(CompletionEvidenceError)` can never yield the former. A harmless forward guard against a hierarchy refactor. | Recorded, retained |
| A-NOTE-3 | NOTE | The helper uses the private `runner._MANIFEST_KEYS`. Established convention in this file — eleven pre-existing private-name uses, including `runner._Progress`, `runner._publish_new_canonical_file` and `runner._CANONICALIZATION`. Consistent, not novel coupling. | Recorded |
| A-NOTE-4 | NOTE | The three tests contain no in-test positive control, so on their own they cannot distinguish "tamper blocked" from "fixture never worked". Externally satisfied by `test_01`/`test_09b`, and definitively by the mutant runs, where the same fixture and tamper *does* open access. | Recorded |
| A-NOTE-5 | NOTE | The clean-room carried a stale `.coverage` file and `__pycache__` directories from earlier work. All review execution ran in `/tmp/reviewA*` with `PYTHONDONTWRITEBYTECODE=1`; end-of-review hashes were byte-identical to start-of-review. | Recorded; artefacts removed before the final run |

Reviewer A explicitly attempted and failed to falsify the claim along five lines: a second field
changing silently (diffed programmatically — one field each); short-circuiting at an earlier guard
(traceback pins the binding comparison, `__cause__ is None`); a `match=` regex loose enough to accept
another guard's message (the string is unique in the module, and the sibling-class check excludes
`LifecycleEvidenceError` anyway); incidental kills from pre-existing coverage (all 136 pre-existing tests
pass under every mutant); and order- or state-dependence (stable across repeats, isolation and
subselection).

### Reviewer B — `PASS`

Method: independent recomputation of every numeric claim from Git plumbing; blob-identity comparison
rather than trust; independent node-ID collection and hashing in the clean-room; read-only status and ref
inspection of the untouched `main` checkout.

Every MIN-1 figure was recomputed and confirmed: `4282fc6 → 23df99d` is 6 `A` / 0 `M` / 0 `D`, 2121 →
2127; `b2331d7 → 23df99d` is 5 `A` / 0 `M` / 0 `D`, 2122 → 2127; `23df99d → a2d44c6` is 1 `A` / 0 `M` /
0 `D`, 2127 → 2128; and the stale `4 A / 2121 → 2125` figure was confirmed **correct** at `6dfef7c`,
`68d6a29` and `68c6a8e` and **incorrect** at `23df99d`. Selector binding confirmed: 139 collected =
50 / 54 / 35, node-ID sequence SHA-256 `f56f09bf…74fd3`, all three test-file hashes matching, and
`tests/test_lattice_bond_instrumentation.py` blob-identical at `4282fc6` and the candidate. Production
source and all seven bound deliverables confirmed blob-identical. Original checkout confirmed unchanged.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| B-MATERIAL-1 | **MATERIAL** *(against the frozen integration record, not this package)* | The stale figure survives verbatim into the published record: `..._INTEGRATION_00_QUALIFICATION.json` key `diff_versus_accepted_lifecycle_parent` and `..._INTEGRATION_00_REPORT.md` line 310 still carry `4 added` / `2121 → 2125`, blob-identical at `23df99d`, `a2d44c6` and the candidate. Truth for the commit they qualify is 6 `A` / 2121 → 2127. Reviewer B confirms the seven bound source hashes but **refutes** the 4-added / 2125 figures. Documentation-only; no source, test or hash claim is affected. | **This finding is MIN-1**; closed by additive erratum — see round 2 |
| B-NOTE-1 | NOTE | The mission worktree is detached at the parent commit with the test file dirty; its content hashes identically to the committed blob at the branch tip. Not caused by the review. | Recorded |
| B-NOTE-2 | NOTE | Stale `.coverage` and `__pycache__` in the clean-room. Collection and runs used `PYTHONDONTWRITEBYTECODE=1 -p no:cacheprovider`, and all `.py` sources were SHA-256-matched against the committed blobs, so results are unaffected. | Recorded |

---

## Round 2 — fix and targeted re-review

Commit `c1faa07a53df69e6cd5836c42c2d4a761a5b283c` — the **final test-file commit**.

Applied: three assertions added to `_assert_reaches_binding_comparison`, mirroring the three guards the
helper previously omitted:

```
assert manifest["lifecycle_schema_version"] == runner.LIFECYCLE_SCHEMA_VERSION
assert manifest["lifecycle_validator_version"] == runner.LIFECYCLE_VALIDATOR_VERSION
assert manifest["canonicalization"] == runner._CANONICALIZATION
```

Nothing else changed. The delta is +240 bytes confined to three lines; the accepted 39 743-byte prefix of
the test file remains byte-identical.

### Reviewer A — `FINAL VERDICT: PASS`

Reviewer A enumerated all eighteen guards in `open_analysis_access` that precede the binding comparison
and mapped each to a helper mirror. **A-MINOR-1 is closed**: every manifest-shape and manifest-field
guard now has a mirror. The two remaining unmirrored steps are named explicitly — `verify_lifecycle_document`
failure and the `canonical_lifecycle_bytes(verified) != document` recheck — and both are lifecycle-document
reverification checks that raise `LifecycleEvidenceError`, which each test already excludes twice over.

Falsifiability of the new assertions was proven empirically rather than argued: tampering each field in
turn fires an `AssertionError` at that assertion's own line. `LIFECYCLE_SCHEMA_VERSION` and
`LIFECYCLE_VALIDATOR_VERSION` were confirmed to be genuine module-level names (aliased imports of
`lifecycle.SCHEMA_VERSION` and `lifecycle.VALIDATOR_VERSION`, both distinct from `runner.SCHEMA_VERSION`),
and `_CANONICALIZATION` a genuine module-level constant. None is dead code.

No regression: 139 collected, 139 passed, 0 failed, 0 skipped; coverage identical at 194 / 0 / 56 / 0 /
100%; the three MIN-2 mutants still killed by their paired tests and by nothing else; the `write_bytes`
mutant still killed by `test_33`; the verification-failure mutant still killed by seven tests. All
baseline hashes unchanged.

New findings, both documentation residue only:

| # | Severity | Finding | Disposition |
|---|---|---|---|
| A-NOTE-6 | NOTE | The helper's docstring still says "every check that precedes the binding", while the two lifecycle-document reverification guards have no helper mirror. Both are excluded at test level by `pytest.raises(CompletionEvidenceError)` plus the explicit sibling-class assertion. No coverage gap. | Recorded, accepted |
| A-NOTE-7 | NOTE | The helper's assertion order no longer matches the module's guard order. Immaterial — the helper is a conjunction, so order carries no meaning. | Recorded, accepted |

**No `BLOCKER`, `MATERIAL` or `MINOR` finding arises from the change.** Reviewer A's verdict binds
explicitly to commit `c1faa07a53df69e6cd5836c42c2d4a761a5b283c`, test-file SHA-256
`84a2087883b0e590eade37ee687ab7daaec6fbf9870f1df82319133e3bdcf401`, against production module SHA-256
`7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08`.

### Reviewer B — `FINAL VERDICT: PASS`

`7facb41 → c1faa07` confirmed as exactly one `M` entry, numstat 3 / 0. `a2d44c6 → c1faa07` confirmed as
exactly one `M` entry, numstat 112 / 0. Cumulative `4282fc6 → c1faa07`: 7 `A` / 0 `M` / 0 `D`, 2121 →
2128 — no production or bound file modified across the entire lifecycle-to-hardening span. All hashes
re-confirmed, including that the accepted 39 743-byte file is a **strict byte-prefix** of the hardened
one. Node-ID sequence SHA-256 unchanged at `f56f09bf…74fd3`, as required, since the fix adds assertions
inside a helper rather than tests. 139 passed / 0 failed / 0 skipped. Original checkout and all four
refs confirmed at their expected values.

Reviewer B independently read `open_analysis_access` and confirmed the fix closes A-MINOR-1 correctly,
that the three added symbols pre-exist in the **unmodified** runner, that zero imports and zero new test
functions were added, and that all behaviour is test-local.

**On the MIN-1 disposition, Reviewer B judged the additive erratum _adequate_**, reasoning that rewriting
the frozen documents would be worse: the integration qualification JSON is a hash-bound record a human
accepted at `a2d44c6`, and editing it in place would destroy the very immutability that makes it
evidence, while silently changing a document whose acceptance is already recorded. An erratum preserves
the audit trail — the wrong number, when it was correct, and the corrected number — which is strictly
more informative than a clean rewrite. Closure was conditioned on the erratum (a) stating the three
corrected figures exactly, (b) naming the exact stale locations, and (c) recording that the stale figure
was correct at the three named intermediate ancestors so the original author is not mischaracterised.
All three conditions are met by this mission's report.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| B-NOTE-3 | NOTE | At `c1faa07` the erratum did not yet exist in Git, so Reviewer B could verify the *disposition* but not the *artifact*. | Discharged by this commit, which adds the erratum |
| B-NOTE-4 | NOTE | The mission worktree remained detached at the parent commit. Not caused by the review. | Recorded |

**No `BLOCKER`; no `MATERIAL` introduced by `c1faa07`.** Reviewer B's verdict binds explicitly to
`c1faa07a53df69e6cd5836c42c2d4a761a5b283c` and covers the traceability, hash, count, checkout-preservation
and firewall sections; it does not extend beyond the numbers it recomputed.

---

## Reviewer independence and limits

Both reviewers ran in separate contexts with their own tool access and were instructed to attack rather
than confirm. Neither could write to any file in the candidate baseline, and neither could create a
commit. Reviewer A had no access to the device at all; Reviewer B was read-only against it.

Two honest limits, stated as they were at integration review. First, both reviewers were briefed by the
implementing agent, so the framing of what to attack originated with the implementer — though both raised
findings the implementer had not anticipated, including the only MINOR and the only MATERIAL. Second,
neither reviewer independently re-derived the frozen threat model; both accepted it as given and tested
conformance to it.

## Firewall

Neither reviewer opened any physics shard, shard filename or manifest, world name or per-world metadata,
trajectory, candidate record, reconstructed checkpoint, failed-autopsy input, `results/` directory,
prospective or `54xxx` seed namespace, global project index, `stage_b.py`, `stage_b_reproduce.py` or
Kovacs material. Neither executed an engine or a scientific runner; the only execution was `pytest` on
the three permitted test files and on disposable mutant copies. Reviewer B's scans of the mission's own
artifacts surfaced only firewall *declarations* and ordinary synthetic-lattice API names — no scientific
content, seeds or data.

# FUTURE-LIFECYCLE-RUNNER-INTEGRATION-00 — independent adversarial review journal

Two independent read-only reviewers were engaged after the implementation and its focused tests passed.
Neither modified any file. Both were bound by the same prohibited-material firewall as the mission.
Three rounds were run: an initial full review, a targeted re-review of the fixes, and a final
confirmation. Every valid finding was fixed and re-verified; nothing was waived silently.

- Reviewer A — API and state-machine auditor.
- Reviewer B — firewall and reproducibility auditor.

---

## Round 1 — initial review

Candidate commit: `6dfef7cdd13c9299d59bdbcd5a3c7150f19dc435`.

### Reviewer A — `PASS`

Method: exploit scripts written under `/tmp` (never inside a repository) plus a 12-mutant mutation
battery on throwaway copies. Attacks attempted and repelled: hand-written `LIFECYCLE.json` plus a
fully consistent forged `COMPLETION.json`; forged `LifecycleRunClosure` / `LifecycleTerminalRecord`
rendered through the real `canonical_lifecycle_bytes`; direct `AnalysisAccess` construction with eight
candidate tokens; relocation of genuine evidence opened against unrelated tracking; caller objects that
mutate between the write pass and the read-back pass; dangling, outside-pointing and directory symlinks
planted at the manifest path; a TOCTOU plant during publication.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| A1 | **MATERIAL** | The atomic publisher was never proven *wired into* the supported path. Every atomicity test called the private helper directly. Mutation M6 — replacing the helper call with `manifest_path.write_bytes(...)` — passed all 47 tests. | **FIXED** in round 2 |
| A2 | MINOR | `json.loads` accepts `NaN`/`Infinity`; `_canonical_bytes` uses `allow_nan=False`, so a poisoned manifest raised a bare `ValueError` outside the declared error hierarchy. | **FIXED** in round 2 |
| A3 | MINOR | A `.partial` survives if `os.fdopen` fails before ownership is confirmed. | **RETAINED**, now documented (see A-NF1) |
| A4 | MINOR | `verified_completion_evidence()` returned a shallow copy; a nested write changed what the instance reported later. | **FIXED** in round 2 |
| A5 | MINOR | `test_14`'s annotation assertion was near-tautological: whitespace-splitting `"str \| os.PathLike[str]"` can never intersect the forbidden set. | **FIXED** in round 2 |
| A6 | MINOR | The state machine is an assertion, not the enforcement — ordering is straight-line control flow. Mutating `_Progress.advance` is killed by one isolated test only. | **DOCUMENTED** in round 2 |
| A7 | NOTE | Two true scope limits lived only in tests: completion evidence is content-addressed, not provenance-bound; and the manifest carries no independent authority. | **DOCUMENTED** in round 2 |
| A8 | NOTE | An empty `TrackingResult` publishes `COMPLETE` with `terminal_record_count == 0`. By design. | **DOCUMENTED** |
| A9 | NOTE | A publication failure after persistence leaves an orphan `LIFECYCLE.json` that blocks reuse of the directory. Intentional. | **DOCUMENTED** |

### Reviewer B — `PASS`

Method: forbidden-token grep over both new files; import-graph inspection; sparse-checkout inventory;
independent hash recomputation on both the clean-room and the device; git metadata only.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| B1 | MINOR | The integration worktree's index reports stale staged deletions (the mount cannot clear `.git/**/index.lock`). Risk that a commit made by another route would delete the mission files. | **MITIGATED BY PROCESS** — every commit is built with an alternate `GIT_INDEX_FILE` + `read-tree <parent>` + `add -f` + `commit-tree`, never from the worktree index. Reviewer B verified this held at each commit and downgraded to NOTE. |
| B2 | MINOR | `test_23` hash-bound only 5 of the 7 bound lifecycle deliverables. | **FIXED** in round 2 |
| B3 | MINOR | Unused `replace` import in the test module. | **FIXED** in round 2 |
| B4 | NOTE | Allowlist items 4 and 5 absent — correct, they are phase-4 artifacts. | Acknowledged |
| B5 | NOTE | Completion evidence is directory-portable, mandated by frozen §6 and required by test 24. | Acknowledged; now in the docstring |
| B6 | NOTE | Frozen §5 schedule constraints are enforced by the bound primitive, not asserted by the new suite. Verified by differential probe: `(5,0)`, `(0,0)`, `(-1,5)` and `()` all rejected. | Acknowledged |
| B7 | NOTE | No contradiction between frozen item 3 and `test_01b` — `EMPTY_TRACK_SET` is a distinct qualified closure, not a bypass. | Acknowledged |

---

## Round 2 — fixes and targeted re-review

Commit `68d6a29a2437a78f54cda828d573c89e298332af`.

Applied: `test_33` (a `_PlantingTracking` proxy that plants a rival manifest in the window between the
pre-flight check and publication, with no monkeypatching); a typed wrapper around the canonical-bytes
computation plus `test_34`; `copy.deepcopy` in `verified_completion_evidence` plus `test_35`; an
exact-string annotation map with substring bans and a return-annotation assertion in `test_14`; all
seven deliverables hash-bound in `test_23`; the unused import removed; and A6/A7/A8/A9 written into the
module docstring as explicit scope facts.

Both reviewers returned `PASS`.

- Reviewer A confirmed M6 is now killed by `test_33`, and proved the kill is not incidental: with M6
  applied the pre-flight check is intact and `test_33` still fails; a spy on `tempfile.mkstemp` located
  the plant strictly between the pre-flight check and the manifest write; a further mutant removing the
  helper's internal `target.exists()` re-check is also killed by `test_33`; and replacing `os.link`
  with `open(target, "xb")` fails 29 tests, pinning the hard-link identity mechanism independently.
  Nine non-finite manifest variants all stayed inside the typed hierarchy. Deep-copy isolation held for
  nested dicts, nested lists, key insertion and top-level deletion. `test_14` now kills both a
  closure-admitting parameter annotation and a weakened return annotation.
- Reviewer B confirmed the seven-deliverable guard runs and passes, verified `git diff --name-status
  4282fc6 68d6a29a` is exactly four `A` entries with a tree-size cross-check of 2121 → 2125 files, and
  recorded that the round-2 `NaN` fix closed a real latent violation of frozen §7 that round 1 had
  missed.

New findings raised in round 2:

| # | Severity | Finding | Disposition |
|---|---|---|---|
| A-NF1 | MINOR | `_publish_new_canonical_file`'s docstring still claimed "or leave nothing behind", which is false for the retained A3 window, and A3 was not documented anywhere. | **FIXED** in round 3 |
| A-NF2 | MINOR | An `OSError` from the frozen writer's `os.link` (filesystems without hard links) still escaped the typed hierarchy, contradicting the sentence A2 was fixed to honour. | **FIXED** in round 3 |
| A-NF3 | NOTE | A narrower mutant (inline `exists()` + `write_bytes`) survives. It is non-clobbering but reintroduces a microsecond TOCTOU window no public-API test can drive without thread interleaving. Composite evidence judged sufficient by the reviewer. | Accepted, recorded |
| A-NF4 | NOTE | `test_33`'s leftover assertion is trivially satisfied — the publisher makes zero `mkstemp` calls in that scenario. Harmless. | Accepted, recorded |
| A-NF5 | MINOR | Duplicate `"LifecycleRunClosure"` token in `test_14`; `_PlantingTracking.edges` never executed. | Duplicate **FIXED** in round 3; `edges` retained for duck-typing completeness |
| B-NF | MINOR | Same duplicate token. | **FIXED** in round 3 |

---

## Round 3 — final fixes and confirmation

Commit `68c6a8eb0c6b4ee443630ed9d96b1e0199b2a03f`.

Applied: the helper docstring rewritten to state that only confirmed-owned files are removed, naming the
`.​<target>.<random>.partial` pattern and the descriptor-open window that produces it; a matching module
docstring paragraph; `OSError` added to the except tuple around the frozen writer, plus
`test_36_filesystem_errors_from_the_frozen_writer_stay_typed`; the duplicate token removed.

**Reviewer A — `FINAL VERDICT: PASS`.** Re-enumerated every failure window and confirmed only the
documented one leaves a `.partial`; confirmed the bare `PermissionError` escape is gone with
`artifacts=[]`; confirmed the widened `except` does not over-swallow — a genuine validation failure is
still reported as `LifecycleEvidenceError` caused by `LifecycleContractError`, and `RuntimeError`,
`MemoryError` and `KeyboardInterrupt` from a hostile tracking object all still propagate untyped; and
confirmed the widened clause wraps only the qualify-and-write call, leaving read-back, verify and
publish outside it. Reverting the `OSError` widening is killed by `test_36`, so the new test is
load-bearing. Round-3 battery: **8 mutants, 8 killed**.

Reviewer A's closing statement: the module is *qualified within its scoped claim* — across three rounds
no way was found, using only the names in `__all__` and with immutable on-disk evidence, to publish
`COMPLETE` or obtain an `AnalysisAccess` without the qualified lifecycle contract having been executed
from the supplied tracking inputs, canonically persisted, read back from disk and independently
reverified against those same inputs.

Reviewer A raised one further **NOTE, judged not actionable**: if `Path.unlink` itself fails after a
successful publication, both the published manifest and the `.partial` survive and the call raises. No
wording can promise removal under a broken `unlink`, and the direction of failure is the safe one — the
surviving manifest is a genuine, fully reverified document, so this can produce a spurious *error*,
never a spurious `COMPLETE`.

**Reviewer B — `FINAL VERDICT: PASS`**, with the firewall declared intact for the whole mission.

---

## Reviewer independence and limits

Both reviewers ran in separate contexts with their own tool access and were instructed to attack rather
than confirm. Reviewer A worked in the cloud clean-room; Reviewer B worked in both the clean-room and,
read-only, against the device repository. Neither had write access to any commit.

Two honest limits on that independence. First, both reviewers were briefed by the implementing agent,
so the framing of what to attack originated with the implementer; the reviewers did, however, raise
findings the implementer had not anticipated, including the MATERIAL one. Second, Reviewer B disclosed
that satisfying the "no historical runner modified" check required `git ls-tree | grep`, which printed
Stage-B and autopsy **path names only** — metadata explicitly permitted by the mission brief, with no
content retrieved and no such file opened.

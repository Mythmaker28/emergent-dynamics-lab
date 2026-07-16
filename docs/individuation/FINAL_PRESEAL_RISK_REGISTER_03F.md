# Final PRESEAL risk register 03F

Status: **seal withheld; human authorization is unsafe**.

No prospective seed in `54001-54096` was executed or instantiated during this re-audit. The controls below were
assessed statically or with synthetic/non-prospective tests.

| ID | severity | status | observed evidence | repair required before another seal audit |
|---|---|---|---|---|
| RUNNER-NOEXEC | critical | OPEN | The 03E runner authorizes and initializes/resumes a ledger, then exits. Its AST has zero calls to `run_seed`, `record_seed`, and `close_run`. | Commit one canonical, fully tested execution path that runs the frozen family, persists raw records, records every seed, and closes exactly once. |
| AUTH-DIR-REPLAY | critical | OPEN | The same approval and synthetic seal initialized two different fresh `--run-dir` paths. O_EXCL protects only one chosen path. | Bind authorization consumption to one repository-wide canonical run identity/path or another global one-use primitive, and reject any second fresh start. |
| SEAL-CODE-NOBIND | critical | OPEN | The runner hashes the seal file but does not parse its protected objects or compare runtime runner, analysis, dependencies, and environment against the seal. Authorization does not require runner/analysis blob fields. | Define and enforce a fail-closed seal schema; compare canonical Git blob identities and environment lock before any ledger creation or engine initialization. |
| LEDGER-FAMILY | critical | OPEN | `record_seed` accepted seed `99999`; no code enforces primary order, reserve activation, hard cap, or minimum-valid stopping. | Enforce the exact family and order inside the ledger/runner state machine, including feasibility-only reserve activation. |
| LEDGER-CLOSE | critical | OPEN | A seed could be appended after a completion record. | Make completion terminal and reject every later append. Require exactly one completion event with final counts and manifest identities. |
| LEDGER-TRUNCATION | critical | OPEN | Removing the completion line left a valid hash-chain prefix accepted by `verify_chain`. | Anchor expected terminal state outside the truncatable log or require a signed/sealed terminal digest and fail verification when closure is absent. |
| LEDGER-PARTIAL | high | OPEN | There is no partial-seed/checkpoint event, atomic resume rule, or concurrent append synchronization. | Freeze crash semantics and implement atomic, synchronized recovery that never silently reruns or double-counts a seed. |
| ANALYSIS-NODRIVER | critical | OPEN | `turnover_statistics_03e.py` is a library; no canonical module loads ledger-backed raw results, builds all frozen matrices/batteries, computes gates, and emits a result. | Commit a single manifest-protected raw-data analysis driver with frozen inputs, outputs, checksums, and failure modes. |
| TREE-NOEVAL | critical | OPEN | Decision-tree expressions are JSON strings. No code computes `DISTRIBUTED_ENV` or selects exactly one A-F outcome. | Add a tested, manifest-protected evaluator that accepts only frozen gate outputs and deterministically selects one outcome by declared precedence. |
| MANIFEST-OMISSIONS | high | OPEN | Load-bearing `turnover_statistics.py` and `turnover_event_evidence.py`, the approval template, and a canonical analysis driver are not protected by the 03E execution manifest. | Enumerate every transitive scientific and execution dependency as a canonical Git blob; make the final seal cover the execution manifest and candidate authority artifacts. |
| SCOPE-GF-NOTNEST | high | OPEN | Swapping an unchanged memory multiset between the target and another region changed L but left Gf unchanged. | Correct the scientific description or freeze a G-full representation that actually contains the declared target-local information without leakage. |
| AUTHORITY-CONFLICT | critical | OPEN | The old `PRESEAL_CANDIDATE.json` still says `AUTHORITATIVE`; its protocol still says canonical; its 03C runner remains executable. | Make one machine-readable candidate authoritative and fail closed on superseded candidates/runners. Preserve historical artifacts without leaving them executable as competing authority. |
| ENV-NOTRECREATABLE | critical | OPEN | The required Linux/Python 3.11.15 environment could not be recreated because the available Docker engine requires a WSL update. | Reproduce all required checks in the exact sealed environment on an independent clean host before resealing. |
| LOCK-NOTINSTALLABLE | high | OPEN | `pip install --dry-run -r TURNOVER_ENVIRONMENT_LOCK_03E.txt` rejects `platform==Linux-x86_64` as an invalid requirement. The file also lacks transitive hashes. | Replace the descriptive text with a valid reproducible environment definition and cryptographically pinned transitive dependencies; test it from a clean host. |
| APPROVAL-PHRASE | high | OPEN | The execution manifest requires a phrase without a seal suffix; the committed approval template adds `FINAL_SEAL_SHA256=<...>`. | Freeze one exact phrase/schema and require exact equality in the runner and authorization validator. |
| OLD-HIGHDIM-PIPELINE | high | OPEN | The earlier raw 32,768-dimensional decoder remains present and reachable beside 03E. | Retain it as explicitly historical/non-authoritative and prevent prospective selection through the canonical entry point. |

## Controlled findings that do not close the open risks

| control | status | limitation |
|---|---|---|
| Canonical Git provenance | PASS | Exact refs, parentage, archive ref, and all 21 listed blobs verify. Authority still conflicts at the artifact level. |
| Grouped LOWO inference | PASS in library tests | There is no canonical raw-data analysis driver connecting it to the prospective result. |
| Fixed-fold uncertainty | PASS in library tests | Only original-world fold losses are resampled and no CV refit occurs, but the complete analysis path is absent. |
| E/Gm target masking | PASS | Gf does not nest L as described. |
| Lambda-plus-only ablation | PASS | The relevant self-check preserves lambda-minus. |
| Tracker and event evidence | PASS | This does not authorize prospective execution. |
| Family-size power regeneration | PASS | Power does not repair the missing family execution state machine or exact environment. |
| Tamper/reorder detection for retained ledger lines | PASS | Truncation, invalid lifecycle transitions, and cross-directory replay remain open. |

## Seal decision

The open critical risks are independently sufficient to withhold `FINAL_SEAL_MANIFEST_03E.json`. They require a
new repair commit and another fresh independent re-audit. They must not be deferred to post-authorization
orchestration because that would modify the execution or statistical specification after sealing.

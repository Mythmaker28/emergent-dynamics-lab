# Journal - RUN-20260716-LCI-PRESEAL-03F

- Role: fresh independent auditor.
- Mission: `LCI-CAUSAL-TURNOVER-FINAL-RE-AUDIT-03F`.
- Run ID: `RUN-20260716-LCI-PRESEAL-03F`.
- Start: 2026-07-16, approximately 19:00 Europe/Paris.
- End: 2026-07-16, finalized before the single audit commit.
- Starting Git state: clean isolated checkout at
  `23b6e9b3c667705158af833c1cf8458a03c8fb66`.
- Starting parent:
  `a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3`.
- Working branch: `audit/lci-causal-turnover-final-re-audit-03f`.
- Ending Git state: audit-only artifacts committed once; exact audit commit is the resulting branch tip.
- Scope: final independent re-audit and cryptographic seal decision only. No scientific repair, prospective
  execution, merge, tag, or push.

## Important objects read

- Repair tip and parent, prior audit and its parent, all fetched turnover branches, current remote main, and
  protected `archive/main-f3921a4`.
- `TURNOVER_EXECUTION_MANIFEST_03E.json` and all 21 canonical Git blobs it lists.
- 03E protocol, candidate, reproduction, risk, decision tree, environment description/lock, approval template,
  runner, ledger, scope extractor, statistics library, power regenerator, and tests.
- Unchanged 03C candidate/protocol/runner and prior integration journal.
- Tracker, tracer, event-evidence, causal confirmation, and lambda-ablation dependencies.

## Actions

1. Created a separate sparse isolated clone and branch at the exact repair commit.
2. Disabled Windows NTFS/HFS name protection only for the isolated clone so canonical repository objects could be
   inspected; did not use CRLF working-copy bytes for cryptographic conclusions.
3. Verified exact repair/parent/prior-audit/archive refs, repair diff, all manifest-listed Git blobs, and
   `git fsck --full`.
4. Searched fetched history for structured or filename evidence of seeds `54001-54096`.
5. Audited runner calls, reserve activation, seal/authorization validation, ledger state transitions, manifest
   coverage, statistical grouping, bootstrap behavior, access scopes, causal gates, decision path, tracker,
   tracer, events, lambda-plus-only ablation, family/power, and authority supersession.
6. Executed synthetic/static tests in an isolated substitute venv. No prospective seed or engine instantiation was
   used.
7. Attempted to recreate the exact declared environment; Docker could not provide a Linux engine because the host
   required a WSL update. Confirmed that the committed environment lock is not installable by pip.
8. Withheld `FINAL_SEAL_MANIFEST_03E.json` and created only the required audit artifacts plus an explicitly invalid
   authorization template.

## OBSERVED

1. Exact provenance and all 21 manifest-listed canonical Git blobs verify.
2. No committed structured result or filename for `54001-54096` was found.
3. The 03E runner performs authorization and ledger initialization/resume, then exits. It has zero calls to
   `run_seed`, `record_seed`, and `close_run`, and no reserve-activation function.
4. One synthetic approval can initialize two independent fresh run directories.
5. The ledger accepts seed `99999`, accepts a seed after completion, and accepts a valid prefix after the terminal
   completion entry is deleted. It detects retained-entry tampering and reordering.
6. The runner does not parse a final seal and compare runtime scientific code/environment blobs against it.
7. Load-bearing transitive dependencies and a canonical analysis driver are absent from manifest protection.
8. The grouped LOWO library uses original-world outer folds, training-only scaling, fixed ridge lambda 1, and
   fixed-fold uncertainty without bootstrap refitting.
9. The 03E dimensions are L=11, N=11, P=33, E=24, Gm=18, Gf=18. E/Gm target-memory masking passes.
10. A target-memory swap changes L while leaving Gf identical, so the statement that Gf nests L is false.
11. Statistical gate functions and an A-F JSON exist, but no canonical raw-data driver or executable decision
    evaluator connects them.
12. Family constants and power regenerate. The runner does not implement the family.
13. Tracker, tracer, event distinctions, and lambda-plus-only preservation pass.
14. The old 03C candidate and protocol still declare authority and the old runner remains executable.
15. The exact Linux/Python 3.11.15 environment was not recreated. The supposed lock contains invalid pip
    requirements syntax and is not a transitive hash lock.

## INFERRED

- The candidate cannot be executed exactly as sealed because essential prospective execution and analysis behavior
  would have to be added by external orchestration or post-seal code.
- Hash chaining alone does not provide one global authorization, terminal-state integrity, or crash-safe exactly-once
  execution.
- Passing grouped-inference unit tests does not make the published prospective decision reproducible when no
  canonical raw-data-to-outcome path exists.
- The environment failure independently triggers the mission's mandatory NOT READY rule.
- A final seal would give false assurance and could enable a scientifically different run under the same approval.

## HYPOTHESIS

If a repair introduces one manifest-protected execution/analysis state machine, globally consumes one authorization,
enforces the exact family and terminal ledger state, binds every transitive code/environment object, resolves
candidate authority, and reproduces from a real clean Linux lock, then the grouped statistical core may be suitable
for another independent seal audit.

## WHAT WOULD FALSIFY THIS?

- A committed 03E execution path demonstrably calling the frozen seed runner, recording each seed/raw hash, applying
  feasibility-only reserve activation, and closing exactly once.
- A test proving the same authorization cannot start in any second directory or repository copy within the declared
  threat model.
- Ledger tests rejecting out-of-family/order seeds, post-completion writes, missing completion, truncation, duplicate
  work, and unsafe concurrent/partial resumes.
- A parsed final seal that rejects any mismatch in every transitive scientific, execution, analysis, approval, and
  environment object.
- A canonical raw-data analysis driver and executable A-F evaluator that classify known null, local, distributed,
  and causal synthetic cases as declared.
- A corrected Gf claim/representation and machine-unambiguous supersession of 03C.
- Successful clean recreation and full test pass on the exact sealed Linux/Python environment.

## Tests and reproducible checks

Substitute environment:
`C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe`,
Python 3.12.10 Windows, NumPy 2.2.6, SciPy 1.15.3, Matplotlib 3.10.9.

```powershell
$env:PYTHONPATH = "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f"
& "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe" `
  experiments\individuation\test_turnover_preseal_03e.py
& "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe" `
  experiments\individuation\test_turnover_preseal_03c.py
& "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe" `
  experiments\individuation\test_bijective_tracker.py
& "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe" `
  experiments\individuation\test_turnover_tracer.py
& "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe" `
  experiments\individuation\turnover_prospective_runner_03e.py --selfcheck
& "C:\Users\tommy\Documents\ising-lci-turnover-reaudit-03f-env\Scripts\python.exe" `
  experiments\individuation\turnover_power_regen.py
```

Results: 03E 18 checks PASS; 03C 9/9 PASS; tracker 10/10 PASS; tracer PASS; runner self-check PASS;
power regeneration PASS. These are synthetic/static or existing DEV-fixture checks, not prospective execution.

## Failures and dead ends

- The repository's pre-existing environment lacked Matplotlib; an isolated substitute venv was created.
- Docker Desktop's Linux engine was unavailable and reported that WSL required an update.
- `wsl --status` did not return within the audit timeout.
- `pip install --dry-run -r TURNOVER_ENVIRONMENT_LOCK_03E.txt` failed on
  `platform==Linux-x86_64`.
- Working-copy SHA-256 differed because of CRLF conversion; the canonical Git blob bytes matched the declared lock
  SHA-256 and were used for the audit.
- Initial lookups used guessed 03E filenames; canonical tree enumeration located the actual approval and environment
  artifact names.

## Decision

**NOT READY - REPAIR REQUIRED.**

No `FINAL_SEAL_MANIFEST_03E.json` was created. The human authorization template is invalid, unfilled, and unusable.

## Unresolved risks

All OPEN critical/high entries in `FINAL_PRESEAL_RISK_REGISTER_03F.md`, especially runner non-execution,
cross-directory authorization replay, incomplete ledger lifecycle, missing seal-to-runtime binding, absent canonical
analysis/evaluator, authority conflict, Gf scope mismatch, and exact-environment failure.

## Handoff

Do not execute any seed in `54001-54096`. The exact next authorized action is a separate repair commit addressing
the open risk register without changing outcomes after data access, followed by a new fresh independent re-audit.
Do not fill or use the authorization phrase unless a future audit creates and verifies a new final seal.

# Fresh Independent Final PRESEAL Audit 03D Journal

## Run identity

- Role: fresh independent final PRESEAL auditor
- Run ID: `RUN-20260716-LCI-PRESEAL-03D`
- Date: 2026-07-16
- Start time: before 17:31 Europe/Paris
- End time: finalized with the audit commit
- Starting Git state: clean isolated checkout at `a5e0a552b3f34a8cf9912292cd74bce3c6aee2d3`
- Starting branch: `audit/lci-causal-turnover-final-preseal-03d`
- Expected parent under audit: `cd74eda96cbcf6e1489f8a6572d1eda8f619b8a1`
- Assigned scope: exact-commit provenance, authorization, statistical specification, scope construction, mechanistic controls, tracker/event evidence, environment reproducibility, and final seal eligibility
- Prospective execution: prohibited and not performed

## Important files read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- latest relevant journals under `docs/agent_journals/`
- `docs/individuation/PRESEAL_CANDIDATE.json`
- `docs/individuation/PRESEAL_CANDIDATE_PROTOCOL.md`
- `docs/individuation/TURNOVER_EXECUTION_MANIFEST_03C.json`
- `docs/individuation/TURNOVER_STATISTICAL_ANALYSIS_SPEC.md`
- `docs/individuation/turnover_prospective_runner.py`
- `docs/individuation/turnover_statistics.py`
- `docs/individuation/turnover_analysis.py`
- relevant tracker, tracer, control, test, environment, and reproduction files

## Actions

1. Created an isolated sparse checkout and checked out the exact integration tip.
2. Verified the expected integration tip, parent, and stated ancestry directly from Git objects.
3. Audited protected blob identities from committed Git objects rather than relying on newline-converted working copies.
4. Verified all protected blobs listed by the execution manifest.
5. Checked protected historical commit availability and remote branch tips.
6. Searched all fetched refs and histories for prospective-family outcome records.
7. Independently recomputed the Beta-Binomial feasibility probability by numerical quadrature.
8. Audited primary/reserve seed-family policy, reserve activation, scope definitions, LOWO inference, uncertainty, ablations, tracker continuity, censoring, and event distinctions.
9. Performed static authorization and statistical-gate checks.
10. Ran the permitted committed tests and self-checks without prospective execution.
11. Produced the final audit report, invalid authorization template, reproduction guide, risk register, and machine-readable certificate.
12. Withheld `FINAL_SEAL_MANIFEST_03D.json` because material blockers remain.

## Reproducible commands and checks

- `git rev-parse HEAD`
- `git rev-parse HEAD^`
- `git cat-file -p <object>`
- `git cat-file -e <object>^{commit}`
- `git merge-base --is-ancestor <ancestor> <descendant>`
- `git fsck --full`
- `git log --all -G <pattern>`
- `git ls-tree -r -l <commit>`
- Python JSON parsing and source-level static assertions
- independent Gauss-Jacobi quadrature for the frozen Beta-Binomial feasibility calculation
- `pytest -q tests/test_turnover_preseal_03c.py`
- `pytest -q tests/test_bijective_tracker.py`
- `python tests/test_turnover_tracer.py`
- `python docs/individuation/turnover_prospective_runner.py --selfcheck`
- Python bytecode compilation and JSON parse checks

## Test results

- `tests/test_turnover_preseal_03c.py`: 9 passed
- `tests/test_bijective_tracker.py`: 10 passed
- turnover tracer: passed using existing DEV seeds 50001 and 50002 only
- prospective runner self-check: passed; no engine instantiated and no seed executed
- Python compile and JSON parse checks: passed
- canonical-object audit: passed
- Git object integrity check: passed

The installed interpreter and numerical libraries did not match the manifest's claimed exact environment, so these passes are evidence about the available environment, not proof of exact-environment reproduction.

## OBSERVED

- Integration tip, parent, ancestry, candidate blobs, and all protected manifest blobs match the stated values.
- The stated protected main commit `f3921a4` is unavailable locally and cannot be fetched from the remote.
- The current remote `main` tip differs from the stated protected main tip.
- No prospective result artifact for seeds 54001-54120 was found in fetched history.
- No seed in the 54xxx family was executed during this audit.
- The independent feasibility recomputation supports the rounded `0.93` reserve-cap probability.
- The runner checks a phrase and manifest identity but does not bind approval to a final-seal hash, consume approval globally, or maintain an immutable execution ledger.
- A reused approval can initialize a different output path.
- The statistical implementation performs grouped leave-one-original-world-out prediction, but the authoritative gate lacks the required within-world permutation ownership null, causal-expression gate, and frozen `L/G` comparison gate.
- The `E` and `G` designs have 32,768 predictors per row; at the minimum valid family an outer training fold has 51 rows, and no frozen defensible dimension-reduction method exists.
- The required A-F decision tree is absent from the authoritative candidate and protocol.
- The exact claimed Python/NumPy/SciPy environment is not reconstructible from the committed environment files and is not the environment used for the audit tests.
- The lambda-plus-only ablation preserves lambda-minus.
- Persisted evidence distinguishes fission, transient fragmentation, merge, loss, and death.
- Tracker continuity and first-permanent-censor handling pass the committed checks.

## INFERRED

- Exact integration provenance is strong, but the protected-baseline chain is incomplete because the named main commit is unavailable.
- Passing committed tests does not cure missing scientific gates or authorization invariants.
- The prospective execution cannot be authorized safely without post-seal code/specification repair, so the candidate is not final-seal eligible.
- The high-dimensional `E/G` comparison is not defensible at the frozen minimum sample size without a predeclared reduction or regularized comparison design.

## HYPOTHESIS

If the authority is repaired to bind one human approval to one final seal and one immutable execution ledger, and the statistical specification is repaired before sealing to include the missing ownership/causal/local-vs-global gates plus a defensible frozen `E/G` design, a subsequent independent audit may be able to certify readiness without running prospective seeds.

## WHAT WOULD FALSIFY THIS?

- A committed, protected main object matching `f3921a4` becoming available and fitting the declared ancestry.
- A source-level proof that approval is cryptographically bound to the final seal and cannot be reused at another output path.
- An immutable ledger implementation that rejects duplicate, altered, or resumed records outside one authorized execution.
- Authoritative predeclared gates implementing the within-world ownership null, causal-expression test, and local-over-global comparison.
- A frozen and power-defensible `E/G` feature-reduction or regularized comparison method.
- A single committed environment definition that reproduces the claimed exact interpreter and dependency versions.

## Failures and dead ends

- The first clone could not check out because tracked filenames containing `|` conflict with default Windows path protection. It was abandoned without modifying the audited repository.
- Sparse checkout initially omitted runner dependencies; the missing committed paths were added to the sparse set before rerunning the self-check.
- The first tracer invocation completed its first scientific check but failed while printing Unicode under the Windows cp1252 console. Rerunning with UTF-8 output passed.
- No attempt was made to execute, preview, or instantiate the prospective 54xxx seed family.

## Decision

`NOT READY — REPAIR REQUIRED`.

Material blockers are:

1. unavailable protected main commit;
2. authorization not bound to a final seal, not globally single-use, and not backed by an immutable ledger;
3. missing ownership-null, causal-expression, and local-over-global statistical gates;
4. unfrozen and underdetermined high-dimensional `E/G` comparison;
5. absent required A-F decision tree;
6. unreconstructible exact execution environment.

## Files changed

- `docs/individuation/FINAL_PRESEAL_AUDIT_03D.md`
- `docs/individuation/FINAL_PRESEAL_AUDIT_CERTIFICATE_03D.json`
- `docs/individuation/HUMAN_AUTHORIZATION_TEMPLATE_03D.json`
- `docs/individuation/FINAL_PRESEAL_REPRODUCTION_03D.md`
- `docs/individuation/FINAL_PRESEAL_RISK_REGISTER_03D.md`
- this journal
- repository state/index records required by `AGENTS.md`

## Unresolved risks

- The protected-main provenance gap prevents complete baseline certification.
- Approval replay and alternate-output initialization remain possible.
- Partial, duplicate, or altered prospective records are not governed by a sealed immutable ledger.
- Missing statistical gates could promote an informational or correlational signal as local causal storage.
- `E/G` results could be dominated by an underdetermined high-dimensional classifier.
- Environment drift can change numerical and serialization behavior.
- Mechanistic diagnostic wording remains less explicit than the requested no-new-writing/passive-copy distinction.

## Handoff

The next authorized action is a separate preseal repair that changes no prospective outcomes and executes no 54xxx seed. It must repair the authority, statistical specification, feature design, decision tree, environment lock, and protected-main provenance, then request a new independent final audit. The invalid authorization template must remain invalid until a later audit creates a genuine final seal manifest and records its hash.

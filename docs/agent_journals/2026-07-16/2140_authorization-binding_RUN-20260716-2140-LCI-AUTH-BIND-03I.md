# Agent journal — authorization binding repair 03I

- Role: minimal authorization-contract repair and integration.
- Run ID: `RUN-20260716-2140-LCI-AUTH-BIND-03I`.
- Start time: 2026-07-16 21:40 Europe/Paris.
- End time: 2026-07-16 22:09 Europe/Paris.
- Starting Git state: branch `repair/lci-turnover-authorization-binding-03i` at exact parent
  `7f005bca81e1a8bbd03ca9aa8f7d114931a686a9`.
- Ending Git state: one coherent repair commit on the same branch, with the exact parent above; no push.
- Assigned scope: repair only the 03G phrase-to-final-seal hash binding and directly affected
  manifests/hashes/tests/documentation. No prospective execution or final seal.

## Important files read

- `AGENTS.md` and all mandatory state/index/journal sources.
- `docs/individuation/PROSPECTIVE_AUTHORIZATION_BLOCKER_03G.md`.
- exact-parent 03G execution/DEV manifests, authorization templates, canonical index, PRESEAL candidate, runner,
  integration tests, reproduction guide, DEV raw/ledger/certificate evidence.
- invalidated audit commit `def070685bf9833a6571766f91c5c7d8a2f8e787`.
- blocker commit `4bf65651d7b5970c6d21f7369f6fc6386c49449f`.

## Actions

1. Created the required branch from exact scientific parent `7f005bca...`.
2. Verified the shared checkout was dirty and unsuitable; performed all work in an isolated exact-parent
   materialization.
3. Acquired isolated runtime lock `RUN-20260716-2140-LCI-AUTH-BIND-03I`. The unrelated shared-checkout lock owned
   by host `claude`, PID 7, was inspected, found not locally running, and deliberately not cleared.
4. Reproduced the defect: prospective authorization compared against an unexpanded literal placeholder and lacked
   the required independent `final_seal_sha256` field.
5. Implemented canonical final-seal hashing, strict lowercase hash validation, one-placeholder expansion, exact
   phrase comparison, v2 field names, and one-execution-only validation before ledger or engine initialization.
6. Added the 13 focused contract cases inside the existing seven-test 03G integration suite.
7. Updated the canonical index and PRESEAL disposition; marked the historical seal retired without changing its
   historical commit.
8. Regenerated protected hashes in the production and DEV manifests.
9. Rebound the DEV provenance chain from the already-open seed-50001 raw payload with an injected executor and an
   engine-import mock. Scientific and feasibility subtrees remained exactly identical.
10. Ran the complete frozen regression matrix in the exact clean environment.

## Reproducible commands

```powershell
$env:PYTHONPATH = "$PWD;$PWD\experiments\individuation"
$env:PYTHONUTF8 = "1"
$python = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean\Scripts\python.exe"

& $python experiments\individuation\test_turnover_end_to_end_03g.py
& $python experiments\individuation\test_turnover_preseal_03e.py
& $python experiments\individuation\test_turnover_preseal_03c.py
& $python experiments\individuation\test_bijective_tracker.py
& $python experiments\individuation\test_turnover_tracer.py
& $python experiments\individuation\turnover_runner_03g.py --selfcheck
& $python experiments\individuation\turnover_power_regen.py
& $python experiments\individuation\turnover_runner_03g.py `
  --manifest docs\individuation\TURNOVER_DEV_EXECUTION_MANIFEST_03G.json `
  --seal docs\individuation\TURNOVER_DEV_SEAL_03G.json `
  --authorization docs\individuation\TURNOVER_DEV_AUTHORIZATION_03G.json `
  --resume
```

## OBSERVED

- Correct calculated synthetic seal hash in the independent field and expanded phrase is accepted.
- Literal `{final_seal_sha256}` and `<FINAL_SEAL_SHA256>` phrases are rejected.
- All malformed, mismatched, case-modified, and whitespace-modified variants are rejected.
- Authorization failure calls neither engine import nor ledger initialization and creates no prospective output.
- Full regression: 03G 7/7, 03E 18/18, 03C 9/9, tracker 10/10, tracer/event all pass.
- DEV resume verifies 10 entries and terminal tip
  `53dceb8c8ec6118911ffdf0b0357d6894dd4341212f8b27e0ebb92cbaf3e9b29`.
- No `54xxx` record and no prospective directory exists.

## INFERRED

- The blocker was a contract-binding defect, not a scientific or lifecycle defect.
- A fresh narrow audit is sufficient; the retired seal cannot be rehabilitated because its accepted human phrase
  did not contain its hash.
- DEV hash changes are expected provenance consequences. Their scientific interpretation remains Outcome E and is
  unchanged.

## HYPOTHESIS

A future canonical final seal plus a human v2 authorization that independently repeats the same calculated hash in
`final_seal_sha256` and the expanded exact phrase will pass authorization, while any divergence will fail before
the engine path.

## WHAT WOULD FALSIFY THIS?

- Any literal placeholder, malformed hash, wrong independent field, or altered phrase passing validation.
- Any authorization failure importing the engine, initializing the ledger, or creating the prospective directory.
- Any difference in the DEV seed-50001 scientific or feasibility subtrees after provenance rebinding.
- Any frozen regression failure or protected-file mismatch.

## Failures and dead ends

- Windows could not check out unrelated historical filenames containing invalid path characters. The branch commit
  is therefore constructed from the exact parent tree with Git plumbing and only the explicit changed paths.
- The first DEV provenance replay used the ambient shared `.venv`, whose NumPy/SciPy/Matplotlib versions had
  drifted. It failed before ledger creation. The exact clean 03G environment was then used successfully.
- Initial archive materialization contained LF bytes for inherited CRLF-protected files. Their audited working-tree
  line endings were restored mechanically; all 37 protected runtime SHA/Git blob pairs then matched.

## Decisions

- No scientific decision was made and `docs/DECISION_LOG.md` was not changed.
- The old seal is retired for the authorization-template binding defect.
- No final seal or valid human authorization is created by this run.

## Unresolved risks

- A fresh independent auditor still must review the repaired commit and issue any new final seal.
- Human authorization remains absent by design.
- The unrelated shared-checkout runtime lock remains untouched.

## Handoff

Exact next authorized action: a fresh narrow auditor reviews the repair commit against parent `7f005bca...`,
recomputes every protected hash, reruns the focused and frozen regressions, and—only if satisfied—issues a new final
seal. No prospective execution is authorized by this handoff.

# Agent journal — final seal 03L

- Role: fresh two-check closure auditor and final-seal issuer.
- Run ID: `RUN-20260716-2315-LCI-FINAL-SEAL-03L`.
- Start time: 2026-07-16 23:15 Europe/Paris.
- End time: 2026-07-16 23:27 Europe/Paris.
- Starting Git state: exact commit
  `0aaf80aa165b76d91b633105e83d03da5208f643`, parent
  `2b1f45357b0e0be22236e5f73a403cecc27778ea`.
- Ending Git state: local branch
  `audit/lci-turnover-final-seal-03l`, containing one local final audit/seal
  commit, no push.
- Assigned scope: verify only the two 03K packaging closure checks, run the
  four requested regression confirmations, and issue a final seal if all pass.

## Important files read

- repository contract and mandatory durable state records;
- 03K closure journal;
- execution manifest and 03K packaging index;
- production runner and focused integration test;
- current protected unfilled authorization template;
- historical seal structure for schema compatibility only.

## Actions

1. Created the required branch at exact 03K commit.
2. Verified the manifest token count and location from the committed Git blob.
3. Recomputed both 03K index bindings from committed Git objects.
4. Ran focused 12/12 and 03G integration 7/7.
5. Confirmed rejected authorization makes zero engine and ledger calls and no
   prospective directory.
6. Constructed canonical `FINAL_SEAL_MANIFEST_03G.json`, binding every
   authoritative canonical artifact plus the 03K packaging index.
7. Computed final seal SHA-256
   `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`.
8. Verified the production runner accepts the seal and manifest.
9. Performed the exact-hash temporary preflight without executing a seed.
10. Preserved the protected production permission template byte-for-byte and
    confirmed its identity fields remain empty and the runner rejects it.

## Reproducible checks

```powershell
$env:PYTHONPATH = "$PWD;$PWD\experiments\individuation"
$env:PYTHONUTF8 = "1"
$python = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean\Scripts\python.exe"

& $python experiments\individuation\test_turnover_end_to_end_03g.py
```

The seal verification and preflight call
`turnover_runner_03g.verify_seal_and_manifest` and
`turnover_runner_03g.validate_authorization` directly. The literal-placeholder
execution-path check mocks both engine import and ledger initialization.

## OBSERVED

- Two closure checks: PASS.
- Focused contract: 12/12 PASS.
- 03G integration: 7/7 PASS.
- Seal raw bytes are canonical UTF-8 JSON plus one LF.
- Production seal/manifest verification: PASS.
- Correct exact-hash phrase validation: accepted.
- Literal placeholder: rejected.
- Unfilled protected template: rejected.
- Engine initialization: 0.
- Ledger initialization: 0.
- Prospective directory: absent before and after.
- 54xxx output and execution: none.

## INFERRED

The two packaging blockers are closed and a new seal can be issued without
reopening or modifying scientific, statistical, environment, tracking, family,
or A-F artifacts.

## HYPOTHESIS

A later human authorization containing the exact new hash in both
`final_seal_sha256` and the exact generated phrase, together with nonempty
identity fields, will pass validation; any literal placeholder or mismatch
will fail before ledger or engine initialization.

## WHAT WOULD FALSIFY THIS?

- A committed seal hash different from the reported canonical hash.
- A canonical artifact binding different from commit `0aaf80a...`.
- Acceptance of a literal placeholder or the unfilled template.
- Any engine/ledger initialization or prospective-directory creation during
  preflight.

## Failures and dead ends

- Initial full seal verification in the sparse checkout reported a missing
  protected `edlab/` path. The subtree was materialized read-only, after which
  the same verification passed. No seal content changed because of this
  checkout-only condition.

## Decisions

- Verdict: READY FOR HUMAN AUTHORIZATION.
- The final seal does not authorize execution.
- The production template remains protected, unfilled, and invalid.
- No project/run index was modified because the mission permits only final
  audit, seal, and template documents.
- No push, merge, tag, publication, or prospective execution occurred.

## Handoff

Exact next authorized action: a human may complete an authorization instance
with the exact new seal hash, exact generated phrase, and nonempty approver,
authorization ID, and UTC timestamp. Do not execute any 54xxx seed before that
separate human authorization.

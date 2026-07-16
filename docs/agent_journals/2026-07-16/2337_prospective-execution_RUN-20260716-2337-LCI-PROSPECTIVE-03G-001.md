# Agent journal — turnover prospective execution 03G

- Role: sealed prospective execution operator.
- Run ID: `RUN-20260716-2337-LCI-PROSPECTIVE-03G-001`.
- Start time: 2026-07-16 23:37 Europe/Paris.
- End time: pending.
- Starting Git state:
  `b5c0f02c02fde0bd15a288b961ffc24606199376` on final-seal branch
  `audit/lci-turnover-final-seal-03l`.
- Working branch: `codex/lci-turnover-prospective-03g-001`.
- Assigned scope: record the human authorization bound to final seal
  `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`,
  execute exactly one canonical 03G prospective run, certify the result, and
  preserve all evidence.

## Important files read

- repository operating contract and durable project/index state;
- latest final-seal journal and final audit;
- authoritative protocol, execution manifest, reproduction guide, final seal,
  authorization template, production runner, engine, ledger, analyzer, and
  raw schema.

## Actions

1. Received the exact hash-bound human authorization phrase.
2. Verified the final seal, exact manifest bindings, production environment,
   and absence of the canonical prospective directory.
3. Acquired the conservative repository lock with this run ID.
4. Created a separate execution branch from the committed final-seal audit.
5. Created the one-execution authorization instance at
   `docs/individuation/TURNOVER_AUTHORIZATION_03G.json`.

## Reproducible command

```powershell
$env:PYTHONPATH = "$PWD;$PWD\experiments\individuation"
$env:PYTHONUTF8 = "1"
$python = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean\Scripts\python.exe"

& $python experiments\individuation\turnover_runner_03g.py `
  --authorization docs\individuation\TURNOVER_AUTHORIZATION_03G.json
```

## OBSERVED

- Human phrase exactly matches the sealed manifest template after substituting
  the final seal hash.
- Authorization ID:
  `LCI-03G-AUTH-20260716T213725Z-001`.
- Approver: `Tommy Lepesteur`.
- Authorization UTC timestamp: `2026-07-16T21:37:25.726Z`.
- Canonical prospective directory was absent before authorization.
- Runtime lock acquisition succeeded with no competing run.

## INFERRED

The committed authorization instance is eligible for one production-run
validation. Scientific interpretation remains forbidden until the ledger
reaches `CERTIFIED`.

## HYPOTHESIS

The production runner will accept the committed authorization and execute the
frozen primary family, activate reserve only from the frozen feasibility
projection if required, and produce exactly one certified A–F outcome.

## WHAT WOULD FALSIFY THIS?

- Any seal, manifest, protected-file, environment, family, or phrase mismatch.
- A ledger state transition outside the frozen state machine.
- A seed outside `54001-54096`, duplicated completion, or overwritten raw
  record.
- Analysis before family closure or a result not bound to the exact ledger and
  raw hashes.

## Failures and dead ends

None before execution.

## Decisions

- The user-provided authorization applies to exactly one canonical prospective
  execution.
- The protected unfilled template remains unchanged; this separate instance is
  the authorization consumed by the runner.
- No scientific, statistical, tracking, family, environment, or A–F rule is
  modified.

## Unresolved risks

- Runtime and reserve use are not yet observed.
- Final A–F outcome is not yet available.

## Handoff

Pending execution and certification.

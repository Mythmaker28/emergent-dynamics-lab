# Claude repair integration reconciliation — PRESEAL 03C

## Exact ancestry

- Parent design: `244bc3262580f1344db1b00582f626a48c75ab4e`.
- Claude initial repair: `ca7929bedb4e9eb08695a82484619e344b8c4085`.
- Claude red-team addendum / integration parent:
  `cd74eda96cbcf6e1489f8a6572d1eda8f619b8a1`.
- Integration branch: `codex/lci-causal-turnover-preseal-integration-03c`.

## Canonical-blob audit findings

1. Claude added parallel 03A protocol/analysis/seed/power files but did not modify the pre-existing authoritative
   `PRESEAL_CANDIDATE_PROTOCOL.md`, `PRESEAL_CANDIDATE.json`, `TURNOVER_SEED_MANIFEST.md`, `TURNOVER_POWER.md`,
   `TURNOVER_REPRODUCTION.md`, or `TURNOVER_RISK_REGISTER.md`.
2. `PRESEAL_CANDIDATE_03A.json` at `cd74eda` is truncated inside the prospective-runner hash and is invalid JSON.
3. Claude's authorization guard is a static environment token embedded in the runner; it is not bound to a
   human-approved manifest.
4. Claude's family is contradictory: 96 main seeds plus a 24-seed reserve yields a hard cap of 120 despite the
   reported cap of 96.
5. Claude's E scope is a four-value summary rather than a persisted target-memory mask, and G is a three-value
   summary rather than the claimed complete world scope.
6. The 03A “leak-free” interval fixes model predictions before bootstrap, but still aggregates row residuals rather
   than using one loss/score per original-world fold.
7. Tracker statuses alone do not distinguish persistent fission from transient fragmentation or tracking loss from
   physical death.

## Integrated repairs

- The pre-existing canonical protocol and ledgers are now the authority.
- Exact family: primary `54001-54050`, reserve `54051-54096`, hard cap 96, minimum 18 valid.
- Reserve activation is feasibility-only and outcome-blinded.
- A separate approval JSON must bind the exact execution-manifest Git blob.
- Every protected code/specification file is bound by canonical Git blob ID.
- L/N/P/B definitions are exact; E and G persist complete target-centred physical fields, with an auditable E mask.
- LOWO predictions are fitted once per original world; uncertainty uses fixed original-world fold losses.
- Lambda-plus-only ablation preserves lambda-minus and every other parameter.
- Five-frame event evidence separates fission, transient fragmentation, merge, loss, and death.
- All Claude DEV diagnostics remain exploratory.

## Authorization state

`NOT AUTHORIZED`. Claude's “GO FOR SEAL” is not operator authorization. No `54xxx` seed was executed during this
integration.

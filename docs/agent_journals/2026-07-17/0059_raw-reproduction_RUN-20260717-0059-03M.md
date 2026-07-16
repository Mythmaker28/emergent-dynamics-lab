# Agent journal — independent raw reproduction 03M

- Role: independent scientific reproducer
- Run ID: `RUN-20260717-0059-03M`
- Start: `2026-07-17T00:59:39+02:00`
- End: `2026-07-17T01:18:06+02:00`
- Starting Git state: clean branch at certified results commit `9cb996bb891f9a618e593f2f5c302f30210458de`, whose parent is authorization commit `c158bc0b848710edeafd425f31dfcbd5aefc0934`
- Ending Git state: branch `analysis/lci-turnover-raw-reproduction-03m` at the same parent with exactly the nine mission-scoped 03M additions ready for the local reproduction commit
- Assigned scope: reproduce the frozen LCI turnover result from committed raw records; independently reimplement the statistics and A–F decision; do not simulate, initialize the engine, execute a seed, modify certified inputs, or push
- Raw input: `results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json`, SHA-256 `ce8d2cb0b6158965acaeef3553f44c7f9bf0ef9b9567c858ff5cbb27f903a328`, plus its 50 Git-committed hash-bound raw records
- Generating scripts: `analysis/lci-turnover-raw-reproduction-03m/raw_reproduction_03m.py` and `analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py`

## Actions

1. Read the repository operating contract and durable scientific state in the mandated order, then inspected the certified manifest, certificate, report, ledger, final seal, canonical indexes, execution manifest, and frozen raw records.
2. Verified results commit `9cb996bb891f9a618e593f2f5c302f30210458de`, authorization ancestry, seal SHA-256 `cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`, all sealed canonical bindings, all execution-manifest runtime bindings, and the exact committed bytes of all 50 raw records.
3. Verified ledger state `CERTIFIED`, 108 entries, terminal event `FAMILY_CERTIFIED`, and tip `0d579d0fa40fd19afe7bfc26140133fc9c57de2b656a7606aa5a5bd8591791aa`; seed starts and completions are each exactly 54001–54050 in ascending order, with no resume, reserve activation, or second execution.
4. Re-ran the committed canonical analyzer only against an isolated temporary exact-byte reconstruction truncated to the frozen family-close boundary. The generated certificate and report were byte-identical to the committed certified objects. The original certified result directory remained unchanged.
5. Independently reimplemented feasibility, LOWO ridge statistics, permutation testing, fixed-fold bootstrap, scope exclusion, frozen causal contrasts, gates, and the A–F outcome tree without importing the canonical analyzer, statistics implementation, scope implementation, ledger, runner, or engine.
6. Compared canonical and independent structures across 9,357 material leaves, including 9,283 numeric leaves: zero disagreements and maximum absolute numeric difference `0.0`.
7. Generated the machine result, report, seed table, combined primary/gate table, figure, and claim-impact note. Visually inspected the figure and machine-checked the JSON and CSV row counts.

## Reproducible commands

Environment: CPython 3.12.10 on Windows AMD64 with the exact committed lock installed in `C:\Users\tommy\Documents\ising-lci-turnover-03m-clean`.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
& 'C:\Users\tommy\Documents\ising-lci-turnover-03m-clean\Scripts\python.exe' `
  'analysis\lci-turnover-raw-reproduction-03m\raw_reproduction_03m.py' --repo .
```

The command completed successfully in the clean environment. It recorded zero simulation-module imports, zero engine-import attempts, and zero seed-command calls.

## OBSERVED

- Raw worlds: 50.
- Valid worlds: 21; frozen minimum: 18.
- `FEASIBILITY=true`.
- `G_OWN_PERM=true`: mean own-scope skill `0.39544573811628886`, 95% t interval `[0.17532271443777103, 0.61556876179480668]`, permutation-null p95 `0.14833143706873275`, p-value `0.000999000999000999`.
- `G_LOCAL_EXCLUSION=false`: L over N and L over G-minus-target pass, while L over E has interval `[-0.02206309923344929, 0.4363985536087388]` and L over B has interval `[-0.022605098442885996, 0.31182481496267273]`; failed frozen components are exactly `L_over_E` and `L_over_B`.
- `G_CAUSAL=true`: own contrast `0.16484499065801109` with 95% interval `[0.14432164288380323, 0.18536833843221895]`; the lambda-plus-only upper bound divided by the own mean is `0.139913587`, below the frozen `0.5` criterion.
- `DISTRIBUTED_ENV=false`: neither frozen environmental access class E nor G-minus-target has a positive lower 95% skill bound.
- The unique frozen decision-tree result is Outcome B, `causal feeding effect without ownership`.

## INFERRED

The frozen data support a passive local causal remnant after deep turnover. They do not support local ownership, individual memory, identity, active reconstruction, heredity, reproduction, or life. The exact reason for Outcome B is that the permutation and causal gates pass while local exclusion fails specifically against E and B; the distributed-environment diagnostic is also false.

## HYPOTHESIS

The measurable own-feeding contrast is a local causal effect that survives the intervention window without satisfying the predeclared individuation criterion.

## WHAT WOULD FALSIFY THIS?

- Any committed raw-byte mismatch, invalid schema record, ledger inconsistency, unauthorized seed event, or certified-binding mismatch.
- A material canonical/independent disagreement under the frozen protocol.
- Failure of the frozen causal gate, or a different unique A–F tree outcome when the same frozen records and parameters are used.

## Failures and dead ends

- A normal Windows checkout was blocked by historical repository filenames containing characters forbidden by Win32. A no-checkout sparse clone with `core.protectNTFS=false` was used to reach the exact certified commit without modifying repository history.
- With repository `core.autocrlf=true`, working-tree bytes for one-line raw JSON can differ from committed bytes. Provenance and analysis therefore read the exact Git blob bytes; these match the raw manifest and certified execution hashes. No raw file was rewritten.
- An initial QA query expected an `outcome` object at the JSON top level. The file parsed correctly; the query was corrected to the documented nested `canonical_reproduction` and `independent` structures.

## Decisions

- No scheduled-run lock was acquired because this was a user-authorized, read-only raw reproduction, not a heartbeat experiment, and no engine process was launched.
- The mission's explicit add-only scope was followed: no project, experiment, run, or decision index was modified.
- The primary scientific table and the gate/outcome table were combined in `PRIMARY_RESULTS_AND_GATES_03M.csv` to preserve both requested contents within the mission's exact file-category limit.

## Files added

- `analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py`
- `analysis/lci-turnover-raw-reproduction-03m/raw_reproduction_03m.py`
- `analysis/lci-turnover-raw-reproduction-03m/REPRODUCTION_REPORT_03M.md`
- `analysis/lci-turnover-raw-reproduction-03m/REPRODUCTION_RESULT_03M.json`
- `analysis/lci-turnover-raw-reproduction-03m/SEED_FEASIBILITY_03M.csv`
- `analysis/lci-turnover-raw-reproduction-03m/PRIMARY_RESULTS_AND_GATES_03M.csv`
- `analysis/lci-turnover-raw-reproduction-03m/OUTCOME_B_REPRODUCTION_03M.png`
- `analysis/lci-turnover-raw-reproduction-03m/CLAIM_IMPACT_03M.md`
- `docs/agent_journals/2026-07-17/0059_raw-reproduction_RUN-20260717-0059-03M.md`

## Unresolved risks

No reproduction discrepancy is unresolved. Scientific interpretation remains deliberately bounded by the frozen protocol and its predeclared claims.

## Handoff

Commit these nine additions locally on `analysis/lci-turnover-raw-reproduction-03m`; do not push. The exact next external action, if requested by the repository owner, is `git push -u origin analysis/lci-turnover-raw-reproduction-03m`.

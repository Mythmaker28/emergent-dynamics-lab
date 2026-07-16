# Journal — RUN-20260716-1920-LCI-PRESEAL-03G

- Role: implementation and integration agent.
- Run ID: `RUN-20260716-1920-LCI-PRESEAL-03G`.
- Start: 2026-07-16 19:20 Europe/Paris.
- End: 2026-07-16 20:00 Europe/Paris, finalized immediately before the coherent repair commit.
- Starting Git state: isolated worktree, clean exact parent
  `23b6e9b3c667705158af833c1cf8458a03c8fb66`.
- Ending Git state: one coherent local commit on `repair/lci-causal-turnover-end-to-end-03g`; exact SHA is the final
  branch tip reported in the handoff.
- Assigned scope: close audit `e18024b098f20dda0125a9010703a968e49cb171` by implementing one real
  seal-to-certificate path, using no prospective seed, final seal, or human authorization.

## Important files and objects read

- Repository operating contract and all required state, decision, experiment, run, and latest journal files.
- Exact parent `23b6e9b3c667705158af833c1cf8458a03c8fb66`.
- Complete 03F re-audit, certificate, risk register, reproduction record, and journal through canonical Git blobs.
- Existing C1c engine/config, causal intervention runner, tracker, tracer, event evidence, 03C/03E methods, and power
  regenerator.

## OBSERVED

1. The 03E runner performed static checks but did not execute the scientific seed/raw/analyzer/certificate chain.
2. Its ledger lacked a complete family lifecycle, canonical-directory replay control, partial-seed resume, and a
   truncation anchor.
3. G-full did not contain L despite claiming to nest it.
4. Frozen statistics existed as library functions but no authoritative raw-to-verdict driver consumed them.
5. The A–F tree was documentation-only.
6. The 03E lock was descriptive rather than an installable exact runtime lock.
7. The old 03C path still competed for authority.

## INFERRED

- The repair had to be one executable dependency chain, not another addendum.
- Canonical Git blobs must be computed with repository path filters; raw working-copy bytes alone are insufficient
  on Windows.
- One canonical directory plus an append-only bound ledger is the enforceable open-source threat model. Global
  prevention against a malicious copied repository is impossible.
- A DEV seed can verify plumbing but cannot establish prospective scientific gates.

## HYPOTHESIS

If every runtime stage consumes and cryptographically binds the preceding stage, ordinary replay, specification
drift, family drift, raw tampering, and manual outcome substitution will fail closed before a result is certified.

## WHAT WOULD FALSIFY THIS?

- A second fresh start succeeding in the canonical directory.
- Resume accepting a different authorization, seal, manifest, family, code map, or environment.
- Any completed seed being rerun or overwritten.
- Analyzer acceptance before `FAMILY_CLOSED`, with a duplicate world, or with a mixed/tampered raw schema.
- More than one or zero A–F terminals for any gate combination.
- G-full's declared L slice differing from L.
- Reserve activation changing after scientific outcome fields are modified.

## Actions and files changed

- Added frozen 03G scope definitions, raw schema, ledger FSM, grouped statistics, analyzer, real engine adapter, and
  end-to-end runner.
- Added production-path integration tests, structured A–F tree, execution manifest, PRESEAL candidate, exact family,
  invalid authorization template, environment lock, reproduction guide, risk/repair records, French verdict, and
  machine-readable canonical index.
- Added DEV-only manifest, seal fixture, invalid prospective authorization fixture, real raw, ledger, raw manifest,
  analysis certificate, and human report.
- Marked 03C/03E superseded through the canonical index without deleting or rewriting history.
- Updated project, experiment, run, and decision records.

## Reproducible commands and experiments

```powershell
$root = "C:\Users\tommy\Documents\ising-lci-turnover-repair-03g"
$py = "C:\Users\tommy\Documents\ising-lci-turnover-03g-clean\Scripts\python.exe"
Set-Location $root

& $py -m unittest experiments.individuation.test_turnover_end_to_end_03g -v
$env:PYTHONPATH = $root
& $py experiments\individuation\test_turnover_preseal_03c.py
& $py experiments\individuation\test_turnover_preseal_03e.py
& $py experiments\individuation\test_bijective_tracker.py
$env:PYTHONUTF8 = "1"
& $py experiments\individuation\test_turnover_tracer.py
& $py experiments\individuation\turnover_runner_03g.py --selfcheck `
  --manifest docs\individuation\TURNOVER_EXECUTION_MANIFEST_03G.json
& $py experiments\individuation\turnover_power_regen.py
```

DEV execution used only seed `50001`. The final chain reached `CERTIFIED`; second fresh start was refused; explicit
resume returned the unchanged certified tip.

## Validation summary

- 03G integration: 7/7 PASS.
- 03E compatibility: 18/18 PASS.
- 03C compatibility: 9/9 PASS.
- Tracker: 10/10 PASS.
- Tracer/event path: ALL PASS.
- Protected artifact maps: 37/37 production and 37/37 DEV, zero mismatches.
- Protected Python compilation: 27/27 PASS.
- Fresh environment: exact lock match and `pip check` PASS.
- Production guard: absent `FINAL_SEAL_MANIFEST_03G.json` refused before engine import.
- Power values: `0.5709037541746931` at 50 and `0.9245190233241044` at 96.
- DEV raw: one seed (`50001`), valid schema/hash, explicit G0, persisted FISSION.
- DEV certificate: Outcome E because the one-seed DEV family yielded zero valid worlds. No scientific claim.

## Failures and dead ends

- The raw-manifest validator initially allowed a mixed-version edge case; production validation was repaired before
  the final DEV run.
- The first 03C/tracer compatibility invocation omitted repository `PYTHONPATH`; imports passed after applying the
  documented precondition.
- The first tracer rerun hit Windows cp1252 output encoding on `Δ`; `PYTHONUTF8=1` fixed display only.
- The staged line-ending audit found that `core.autocrlf=true` would invalidate newly committed LF artifact and DEV
  hashes after checkout. Scoped `.gitattributes` rules were added and included in the protected map.
- The first post-rebinding DEV command exposed an ambient `PYTHONPATH` dependency. The ledger stopped safely at
  `PRIMARY_RUNNING`; the runner was repaired to locate the repository root itself, and the final fresh smoke passed
  without `PYTHONPATH`.
- Whole-repository compilation exposes a pre-existing unrelated unterminated f-string in
  `edlab/experiments/sc_hmc/driver.py:51`. It is outside the 03G protected graph and exact mission scope.
- Recursive cleanup was unnecessary; the ephemeral advisory lock file was removed explicitly after resume testing.

## Decisions

- Canonical turnover path: 03G.
- Authoritative platform: Windows AMD64, CPython 3.12.10.
- G-full: exact concatenation of L and G-minus-target, with frozen L slice `[0:11]`.
- Outcome evaluation: one imported structured A–F tree, no manual classification.
- Threat model: one canonical-directory execution plus cryptographic replay evidence, not impossible global
  anti-replay.

## Unresolved risks

- Final independent re-audit remains required.
- Final seal and valid human authorization remain absent by design.
- A malicious actor controlling a copied repository can rerun modified code; that run is untrusted and not the
  sealed execution.
- Fine distributed encoding outside frozen E/G-minus-target resolution remains a scientific limitation.
- Fewer than 18 valid prospective worlds will produce Outcome E and no scientific negative conclusion.
- The unrelated `sc_hmc` syntax defect remains outside this branch's scope.

## Handoff

Do not execute any `54xxx` seed. The next exact authorized action is a fresh independent static and DEV-artifact
re-audit of the committed 03G branch. Only after a successful re-audit and explicit human approval may a separate
final seal and exact-hash authorization be created. Do not modify code, statistical specifications, family, or
environment after sealing.

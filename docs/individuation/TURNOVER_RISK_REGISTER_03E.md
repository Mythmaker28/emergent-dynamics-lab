# LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03E — risk register (blockers resolved)

Status: repaired; **still NOT sealed and NOT executed**. A fresh independent re-audit + seal is required before any
`54xxx` seed.

| audit ID | severity | status after 03E | resolution (committed, tested) |
|---|---|---|---|
| B1 AUTH/LEDGER (AUTH-01/02, LEDGER-01) | material | **RESOLVED** | `turnover_execution_ledger.py`: final-seal-sha256 binding, O_EXCL one-shot start, hash-chained JSONL, one-use consumption, per-raw SHA-256, completion close; tamper/reorder/rerun/second-fresh all rejected (synthetic tests PASS) |
| B2 PRIMARY GATE (STAT-01/02/03) | material | **RESOLVED** | `turnover_statistics_03e.py`: within-world permutation ownership null (G-OWN-PERM), coherent L-vs-{N,E,Gm,B} exclusion, causal-expression gate, primary = perm ∧ exclusion ∧ causal; duplicate-world content rejected (synthetic tests PASS) |
| B3 E/G DIMENSIONALITY (DIM-01) | material | **RESOLVED** | `turnover_scope_features_03e.py`: E=24, Gm=18, Gf=18 (was 32768); frozen radial/global features; raw kept future-only; ratio 0.35–0.47 vs 642.5 |
| B4 A–F DECISION TREE | material | **RESOLVED** | `TURNOVER_DECISION_TREE_03E.json`: Boolean gate expressions, authorized wording, forbidden claims, active-reconstruction flag; wired into runner self-check |
| B5 ENVIRONMENT (ENV-01, REPRO-01) | material | **RESOLVED** | `TURNOVER_ENVIRONMENT_03E.md` + lock (3.11.15/2.2.6/1.15.3/3.10.9, scoped separate from V4 Docker); `turnover_power_regen.py` reproduces 0.924519; clean-room PASS |
| B6 PROTECTED MAIN (PROV-01) | material | **RESOLVED (local) / flagged (remote sync)** | local main=f3921a4 verified + `archive/main-f3921a4`; local↔remote(6d0bed6) reconciliation flagged as out-of-scope pre-push action; turnover never touches main |
| CLAIM-01 feeding ≠ individuation | controlled | retained | feeding contrast secondary; A requires perm ∧ exclusion ∧ causal, not feeding alone |
| POWER-01 broad feasibility | controlled | retained | Outcome E preserved; no family extension; P(≥18)=0.925 regenerable |
| MECH-01 diagnostic wording | moderate | resolved | protocol states λ₊-only vs full-ablation and up_ref/copy-disabled as DEV-only diagnostics, not same-physics exclusions |
| FAMILY-01 premature open | controlled | retained | no seal, no authorization, no `54xxx` seed in this repair |
| NEW: external-copy binding | disclosed | accepted-limitation | ledger enforces one run in the canonical directory only; a malicious repo copy cannot be cryptographically bound (documented) |

**Residual before RESEAL:** a fresh independent agent must (1) re-audit these repairs against this certificate, (2)
create `FINAL_SEAL_MANIFEST_03E.json` and bind the approval to its sha256, (3) verify the local↔remote main
reconciliation on a networked machine, (4) then and only then may a human authorize one execution.

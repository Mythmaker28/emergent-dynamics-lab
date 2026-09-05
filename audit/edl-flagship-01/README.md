# EDL flagship audit 01

Start with [ASTRA_INDEPENDENT_AUDIT_FR.md](ASTRA_INDEPENDENT_AUDIT_FR.md). Verdict: **FLAGSHIP_NOT_YET_JUSTIFIED**. FDFLT01 53/192 is verified from endpoint-bearing raw core; B is the best supported manuscript nucleus; CCRA01 and five September-4 fatal findings remain unverified.

The requested deliverables are this report, [recovery verification](RECOVERY_VERIFICATION.md), [provenance gap matrix](DATA_PROVENANCE_GAP_MATRIX.csv), [decision matrix](FLAGSHIP_DECISION_MATRIX.md), [strengthening plan](PAPER_STRENGTHENING_PLAN.md), scripts, raw evidence and machine-readable results. No new manuscript is presented as a verified flagship.

## Reproduction

Audited runtime: Python 3.12.10, NumPy 2.5.1, SciPy 1.18.0. Standard library otherwise. No YAML, model engine, network call or new scientific world is needed by the analysis scripts.

From a checkout containing this folder and the historical FDFLT01, TBRT02, OMLDCT03 and OBTC02 protocol inputs:

```text
python audit/edl-flagship-01/scripts/reproduce_all.py
```

Git objects for the pinned main, PR34 and B histories must be available to reproduce the branch comparison and prospective chronology. A full fetch of remote branches provides them; a shallow single-branch checkout may not. Windows cannot materialize historical cache filenames containing `|`; use an isolated no-checkout clone/sparse view excluding results/_tomo_cache, as in the audit. The results and all raw arrays used by the new scorers are included here. No old runner is an authorized entry point.

`recovery/` is the separately committed input checkpoint. `candidate_b/` is an exact snapshot of selected source files at 06fd9524, with a manifest; its historical code is evidence except for the explicitly reviewed raw-only 03M module. The B adapter changes only byte loading to verified snapshot bytes. Its permutation test is a transparent reuse, whereas core ridge and causal contrasts receive an additional implementation in the current audit.

`recompute_fdflt.py` independently reconstructs post-step Y populations/centres from pre-reaction cells and birth/death events, then applies the frozen endpoint with pre-reaction X. `recompute_omldct.py` independently reconstructs cell components, the locked identity and exact Pratt signed-rank statistics. `check_interval.py` separately diagnoses the frozen CI order-index defect without modifying historical outputs. `test_audit.py` exercises exact small-sample sign enumeration, zero/tie handling and toroidal geometry on synthetic arrays; no world is constructed.

The first missing YAML dependency was removed by reading only three unique numeric constants from their explicit frozen YAML sections. An initially incorrect pre/post-reaction comparison in the new audit was corrected by reading the observer phase and adding recorded birth/death events; it was not a repair of historical data. Verification then passed for all 1,291,322 lines.

The recovery helpers in `recovery/` record original Windows locations and are session-specific preservation utilities. Do not rerun them as scientific analyses. The reproducible entry point is `scripts/reproduce_all.py` and its PASS result is `results/VALIDATION.json`.

Scope: no main write, merge, submission, DOI, experiment run, or Sweeper change. The only requested human input is the precisely identified missing Sept-4 bundle.

# Agent Journal — RUN-20260710-1647-EXP02STAT

## AGENT / ROLE

Independent statistical auditor / EXP02 raw-shard and aggregate QA.

## RUN ID

`RUN-20260710-1647-EXP02STAT`

## START / END TIME

- Start: 2026-07-10 16:47 +02:00.
- End: 2026-07-10 16:58 +02:00.

## STARTING GIT STATE

- Branch: `main`, tracking `origin/main`.
- HEAD: `6c593780ab33326fd0957f73bb885bfe1c15ab84`.
- Worktree already contained the primary agent's untracked completed EXP02 output directory.
- Parent run `RUN-20260710-1609-EXP02REC` owns the conservative lock for `EXP02-COREV0-20260710-001`; this auditor did not acquire or release a competing lock.

## ASSIGNED SCOPE

Read-only independent statistical audit of EXP02, except for this unique journal. Verify manifest, raw index, summary, and recalculations from immutable shards/aggregates: P/M distributions, descriptive correlation with pseudoreplication warning, probe occupancy by cadence and tau, law/seed variation, events, null/anomaly checks, non-finite values, total consistency, and finite-horizon right-censoring. No composite score, new threshold, or shared code change.

## ACTIONS PERFORMED

- Read the repository operating contract and durable scientific state in the mandated order.
- Read the latest primary/recovery journals, EXP02 protocol, completed manifest, stream plan, and summary.
- Recomputed SHA-256, byte size, and CSV row count for all 3,600 indexed raw CSVs; compared every shard manifest to `raw_index.json` and every root derived-output hash/size to `manifest.json`.
- Recomputed the plan hash, all 900 per-run input hashes, and all 300 Halton LawSpecs independently.
- Parsed all 648,740 measurement rows and independently recomputed P/M bounds, distributions, Pearson correlation, probe counts, interval flags, cadence/tau tables, run/law/seed summaries, and exact aggregate-table cells.
- Parsed all 456,754 lineage events, 369,483 entity observations, and 1,742,852 association edges for non-finite values, domain/bounds failures, malformed JSON, duplicate keys, identity drift, particle overlap, and event/index inconsistencies.
- Quantified finite-horizon censoring from tracks present at step 600 and measurement windows ending at the horizon.
- Reran the four null-model functions directly and compared their complete serialized results to `summary.json`.
- Ran the five continuity/null tests. No shared implementation or result file was modified by this auditor.

## IMPORTANT FILES READ

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-10/1609_primary_RUN-20260710-1609-EXP02REC.md`
- `docs/agent_journals/2026-07-10/1629_recovery-audit_RUN-20260710-1629-EXP02REC-AUD.md`
- `docs/experiments/EXP02_COREV0_PROTOCOL.md`
- `results/EXP02-COREV0-20260710-001/manifest.json`
- `results/EXP02-COREV0-20260710-001/stream_plan.json`
- `results/EXP02-COREV0-20260710-001/summary.json`
- `results/EXP02-COREV0-20260710-001/measurement_aggregates.csv`
- all 900 `raw/runs/law-NNNN_seed-S/` shard manifests and four raw CSVs per shard

## COMMANDS / REPRODUCIBILITY

- PowerShell/Python streaming audit over `raw_index.json`: recompute `sha256`, byte size, and newline-derived data-row count for every indexed CSV, then compare shard/root manifests.
- Python `csv`/NumPy pass over every `measurements.csv`: recompute raw and interval-unflagged probe counts, Pearson correlations, quantiles, cadence/tau groups, and law/seed/run summaries.
- Independent canonical-lag pass grouped only by `(snapshot_cadence, end_step-start_step)`, with `tau=(end_step-start_step)*0.02`; no raw floating-point equality was used in this pass.
- Python `csv`/JSON passes over every event, observation, and association table: check finite numeric values, schema domains, duplicate keys, particle partitions, gate semantics, and horizon tracks.
- Python canonical-JSON SHA-256 recomputation of `stream_plan.json` and all `_run_input_sha256` identities; regenerate laws with `law_from_halton(i, 3)` for `i=0..299`.
- Direct calls to `id_permutation_null`, `static_motif_material_flux_null`, `tracker_cadence_sensitivity_null`, and `sparse_lookalike_alias_null`; returned objects exactly equal `summary.json`.
- `.\.venv\Scripts\python.exe -m pytest -q tests/test_continuity.py` -> `5 passed in 0.12s`.

## OBSERVED

- `manifest.json` says `COMPLETE`, with 900 expected and 900 completed runs on launch SHA `6c593780ab33326fd0957f73bb885bfe1c15ab84`.
- `raw_index.json` has exactly 900 unique identities: every Cartesian pair of laws `0..299` and seeds `{2001,2002,2003}`, with no missing, extra, duplicate, or incomplete entry.
- All 3,600 raw CSV hashes, sizes, and actual row counts match their shard manifests and the raw index. Root output hashes/sizes also match. Recomputed raw totals equal manifest and summary exactly: 648,740 measurements; 456,754 events; 369,483 observations; 1,742,852 association edges.
- The plan hash is exactly `6cc6e5585462e24cbae2ec01e6243ca2731acd46267d84cb5131d95f19dea205`; all 900 run-input hashes match. The 300 finite LawSpecs are unique and byte-for-value identical to independent Halton regeneration.
- No non-finite values, out-of-domain P/M values, malformed JSON, duplicate measurement/event/observation/edge key, mismatched shard identity, invalid selected gate, phenotype-length error, particle-count mismatch, or cross-entity particle-ID overlap was found.
- P: mean `0.844542`, median `0.871685`, p05/p95 `0.596843/0.995108`, range `0.014543..0.999995`. M: mean `0.825063`, median `1`, p05/p95 `0.294118/1`, range `0..1`; 53.40% of rows have exactly `M=1` and 0.592% exactly `M=0`.
- Row-level descriptive Pearson `r(P,M)=0.731581225681268`, matching the summary to floating summation precision. Correlation of 900 run means is `0.861653`; correlation of 300 law means is `0.874292`; within-run correlation median is `0.672881` (range `0.137714..0.889151`). None is an inferential estimate because rows/windows/cadences overlap.
- The unchanged initial probe contains 10,302/648,740 rows (`1.5880%`). Of these, 7,186 have neither logged ambiguity nor split/merge within the interval (`69.75%` of probe rows), but all 10,302 explicitly retain sparse-alias risk. The label `lineage_resolved_count` therefore means only interval-complexity-unflagged, not resolved physical identity.
- Probe occupancy by cadence is `1.3697%` at cadence 10, `1.9932%` at cadence 30, and `2.9578%` at cadence 60. At fixed approximate tau: `tau=0.6`, cadence 10/30 gives `1.8407%/1.7589%`; `tau=1.2`, cadence 10/60 gives `1.6274%/2.3177%`; `tau=3.6`, cadence 30/60 gives `2.6408%/3.0473%`. Observer dependence remains material.
- The integer-delta recomputation has exactly the nine frozen groups and no unexpected delta or tau/delta mismatch: cadence 10 at 10/30/60 steps gives 202,748/159,285/125,971 rows and 1,702/2,932/2,050 probes; cadence 30 at 30/90/180 steps gives 56,000/36,769/25,030 rows and 985/702/661 probes; cadence 60 at 60/180/360 steps gives 24,162/12,864/5,911 rows and 560/392/318 probes. These totals exactly reproduce the earlier normalized-tau table.
- By global screening seed, raw probe occupancy is `1.5219%`, `1.6017%`, and `1.6405%` for 2001/2002/2003. Across laws, raw probe-rate median is `1.1308%`, p95 `6.9303%`, range `0..17.0996%`. A raw probe occurs in all three seeds for 260 laws; an interval-unflagged raw probe occurs in all three for 218 laws. These counts do not apply the preregistered same-endpoint/cross-cadence/long-track gate.
- Measurement contribution is highly unequal: per-run rows range `138..2026` (median `644.5`). The row-weighted probe occupancy is `1.5880%`, while the equal-run mean of run occupancies is `2.1255%`; run row count correlates `-0.4242` with run probe rate. Treating 648,740 windows as independent trials would materially misweight the 900 simulations.
- The apparent highest raw probe-rate law, 244, has only 462 total windows; per-seed denominators are 168, 138, and 156. Rankings based on row occupancy alone are descriptive and unstable, not promotion evidence.
- Event counts independently match the summary: 86,573 births; 282,910 continuities; 76,472 disappearances; 6,072 merges; 3,854 splits; 873 ambiguous associations. Selected association edges equal continuity events exactly (`282,910`), and no selected edge fails either physical gate.
- `births - disappearances = 10,101`, exactly the number of cadence-specific tracks present at the final step. Per cadence this is 3,367 final tracks each. This closes the lifecycle accounting invariant.
- Right-censoring is non-negligible: 10,101/86,573 cadence-specific tracks (`11.67%`) are still observed at step 600; 899/900 simulations have at least one detected entity at simulated time 12. The sole no-final-entity simulation is `(law 244, seed 2003)`. There are 18,985 measurement windows ending exactly at the horizon, including 228 probe rows; their future persistence is unobserved.
- Observed track-span median is `0.2` simulated time overall, `3.6` for horizon-censored tracks, and `0` for tracks that disappear before the horizon; zero denotes a one-snapshot track. Absence of a later signal cannot be read beyond time 12.
- All four rerun null outputs match the stored summary exactly. In particular, both static material flux and sparse look-alike alias remain explicit `P=1,M=0` probe-positive nulls rather than discoveries.
- Aggregate-cell sums/counts are numerically exact, but `measurement_aggregates.csv` has a representation defect: 7,487 logical non-empty `(law,seed,cadence,tau)` groups are fragmented into 36,937 exact-float rows. Of the logical groups, 7,280 split into 2–7 fragments because nominally identical tau values differ at floating precision. This does not alter totals, but exact-float grouping is unsafe for tau analysis.

## INFERRED

- The completed raw experiment and its transport/index metadata pass independent integrity and arithmetic QA.
- The positive P/M association is robust as a descriptive feature across row-, run-, and law-level summaries, but it does not establish causality or independence and does not identify a persistent individual.
- Higher apparent probe occupancy under sparse cadence and longer tau is compatible with observer/tracker selection and changing denominators. It cannot be presented as a dynamical-law effect without the frozen cross-cadence control.
- The aggregate tau fragmentation is non-destructive because raw `start_step`, `end_step`, and cadence are intact. Grouped downstream analysis must derive lag from integer steps or normalize tau; it must not use raw float equality.
- The current `summary.json` is a correct completion/transport summary, not the full preregistered scientific analysis. It lacks explicit right-censoring, unequal-run weighting, and the frozen candidate disposition.

## HYPOTHESIS

- Some laws may produce reproducible high-P/low-M windows, but the broad raw occupancy is still fully compatible with repeated-window pseudoreplication, cadence sensitivity, static flux, and sparse look-alike alias.
- Applying the exact preregistered same-endpoint, independently clean cross-cadence, minimum-eight-observation rule may reduce the large raw-probe population sharply.

## WHAT WOULD FALSIFY THIS?

- A raw/index/hash discrepancy, a recalculated total or correlation mismatch, a non-finite/schema violation, or a null rerun mismatch would falsify the integrity verdict; none was observed.
- Recomputing grouped statistics from integer lag steps and obtaining materially different normalized cadence/tau totals would falsify the claim that float fragmentation is representational only.
- A candidate that survives the frozen raw-edge audit, tracker/cadence controls, direct trajectory review, and unseen-seed hold-out would falsify the current artefact-only interpretation for that law. A raw probe or interval-unflagged row alone would not.

## FAILURES / DEAD ENDS

- Two first combined event/observation/edge scan commands produced no captured output after completion; they were decomposed into bounded independent scans. No experimental file was changed, and each decomposed scan completed with explicit totals.

## DECISIONS / QA VERDICT

`PASS_WITH_REQUIRED_CAVEATS` for raw/index integrity and descriptive arithmetic. `GO` to the already preregistered candidate audit using raw integer endpoints and edge/event evidence. `NO-GO` for scientific promotion or hold-out launch from the current root summary alone.

Required before interpretation:

1. derive/group tau from integer step differences (or a frozen canonical lag key), never exact float equality;
2. preserve the explicit 900-run/300-law pseudoreplication and unequal-row-weight caveat;
3. call the 7,186 count interval-complexity-unflagged, not proof of lineage resolution;
4. report the 11.67% final-track censoring and time-12 boundary;
5. apply the frozen same-endpoint, cross-cadence, long-track, multi-seed gate from raw data before deciding whether a fresh-seed protocol is authorized.

## UNRESOLVED RISKS

- Raw shards are local and ignored; verified checksums detect corruption/loss but are not a remote backup.
- The detector/tracker can still create occupancy aliases even for intervals without logged ambiguity; all probe rows correctly carry that unresolved risk.
- The predeclared candidate analysis, Pareto/density analysis, law-parameter dependence, and any eligible-candidate edge/trajectory audit were not yet present in the completed root summary at audit time.
- All finite-horizon conclusions remain right-censored at simulated time 12.

## HANDOFF

Primary agent: keep the 900-run raw batch; no rerun is warranted by this audit. In the candidate/scientific analysis, canonicalize lag by integer steps, reproduce the stated QA totals, include pseudoreplication/right-censoring caveats, and apply the frozen raw-edge candidate rule. Do not use raw probe-rate rankings or `lineage_resolved_count` as evidence. Only then decide between a separate fresh-seed protocol and EXP03-A.

## ENDING GIT STATE

- HEAD remained `6c593780ab33326fd0957f73bb885bfe1c15ab84` throughout this audit.
- The primary/candidate agents created or modified shared analysis files concurrently; this auditor did not inspect, edit, stage, commit, or push those changes.
- This journal is this auditor's only filesystem write.

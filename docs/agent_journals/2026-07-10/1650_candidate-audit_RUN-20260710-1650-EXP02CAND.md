# Agent Journal — RUN-20260710-1650-EXP02CAND

## AGENT / ROLE

Independent EXP02 candidate-selection and raw-integrity auditor.

## RUN ID

`RUN-20260710-1650-EXP02CAND`

## START TIME

2026-07-10 16:46:00 +02:00

## END TIME

2026-07-10 16:52:46 +02:00

## STARTING GIT STATE

- Repository: `C:\Users\tommy\Documents\ising v3`.
- Branch: `main`.
- HEAD and `origin/main`: `6c593780ab33326fd0957f73bb885bfe1c15ab84`.
- The completed EXP02 root outputs were untracked and `raw/` was ignored, as intended by the artifact policy.
- The conservative lock was already owned by the coordinating parent run `RUN-20260710-1609-EXP02REC` for `EXP02-COREV0-20260710-001`. I did not acquire or release a competing lock. My access to experiment data was read-only; the only file I created is this journal.

## ASSIGNED SCOPE

Independently recalculate the preregistered EXP02 candidate rule directly from `results/EXP02-COREV0-20260710-001/raw/runs`, without changing thresholds or shared code. Verify root and per-run manifests, hashes, sizes, CSV row counts, and run identities. Distinguish raw rows, clean rows/tracks, physical endpoints, qualifying law/seed pairs, and laws qualifying in at least two of seeds `{2001,2002,2003}`. Preserve the unresolved alias caveat and make no promotion claim.

## IMPORTANT FILES READ

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-10/1609_primary_RUN-20260710-1609-EXP02REC.md`
- `docs/experiments/EXP02_COREV0_PROTOCOL.md`
- `docs/experiments/HOLDOUT_COREV0_03_PROTOCOL.md`
- `edlab/experiments/audit_candidates.py` for comparison with the frozen corrected join semantics; its implementation was not invoked on EXP02.
- `results/EXP02-COREV0-20260710-001/manifest.json`
- `results/EXP02-COREV0-20260710-001/summary.json`
- `results/EXP02-COREV0-20260710-001/raw_index.json`
- All 900 `run_manifest.json` files and all 3,600 indexed raw CSV files.

## ACTIONS ACTUALLY PERFORMED

1. Read the durable state in the mandatory order and inspected Git/lock state.
2. Independently verified every root output referenced by `manifest.json` against its SHA-256 and byte size.
3. Verified exact identity coverage for all 900 expected `(law_index, seed)` pairs, with no duplicate, missing, or extra run directory.
4. Compared each raw-index entry to its per-run manifest, then recomputed SHA-256, byte size, and actual CSV row count for each of the four raw tables in every shard.
5. Recomputed the candidate rule using only Python standard-library CSV/JSON parsing:
   - track key: `(law, seed, cadence, track_id)`;
   - complex anywhere: a `split`, `merge`, or `ambiguous_association` whose parent or child list contains that track;
   - clean-long probe row: `P > 0.8`, `M < 0.5`, at least eight observations on the cadence-scoped track, and no complex event anywhere on that track;
   - endpoint key: `(law, seed, start_step, end_step)`;
   - qualifying endpoint: clean-long probe rows under at least two distinct cadences;
   - eligible law: at least one qualifying endpoint in at least two distinct screening seeds.
6. Checked the raw probe alias flag rather than inferring it from the root summary.

## IMPORTANT COMMANDS / EXPERIMENTS

```powershell
git status --short
git rev-parse HEAD
git rev-parse origin/main
.\.venv\Scripts\python.exe -m edlab.runtime_lock status
```

The integrity and candidate audit was a read-only inline standard-library Python program streamed over stdin:

```powershell
$code | & .\.venv\Scripts\python.exe -
```

Its core selection logic was:

```text
probe := P > 0.8 and M < 0.5
clean_long := observations[(cadence,track)] >= 8
              and (cadence,track) absent from every split/merge/ambiguity parent or child
endpoint := (law,seed,start_step,end_step)
qualifying_endpoint := count(distinct cadence among clean_long probe rows) >= 2
eligible_law := count(distinct seed containing a qualifying_endpoint) >= 2
```

Integrity checks recomputed every raw SHA-256, size, and CSV row count; compared run manifests to `raw_index.json`; recomputed root-output hashes/sizes; and cross-checked root/summary totals.

No shared code changed, so no source test suite was required for this audit. The full-data integrity and independent selection pass are the relevant executed checks.

## OBSERVED — INTEGRITY

- Verdict: **PASS**.
- Root manifest: `COMPLETE`, `900/900`, all four completion assertions true.
- Experiment code SHA: `6c593780ab33326fd0957f73bb885bfe1c15ab84`, equal to HEAD and `origin/main` during the audit.
- Plan SHA-256: `6cc6e5585462e24cbae2ec01e6243ca2731acd46267d84cb5131d95f19dea205`.
- 7/7 derived outputs referenced by the manifest passed SHA-256 and size verification.
- 900/900 raw-index entries and 900/900 run directories had exact expected identities.
- 3,600/3,600 raw CSV files passed SHA-256, size, and actual CSV row-count verification against both the run manifest and raw index.
- No extra entry existed under the raw root outside `raw/runs`.
- Recomputed raw totals exactly matched both root manifest and summary:
  - `measurements.csv`: 648,740 rows;
  - `lineage_events.csv`: 456,754 rows;
  - `entity_observations.csv`: 369,483 rows;
  - `association_edges.csv`: 1,742,852 rows.

## OBSERVED — FROZEN CANDIDATE RULE

- Raw initial-probe rows: **10,302**.
- Raw probe rows by cadence: 10 → 6,684; 30 → 2,348; 60 → 1,270.
- Every one of the 10,302 probe rows had `unresolved_sparse_alias_risk=True`; zero had it false.
- Clean-long probe rows after the full-track event exclusion: **2,400**, on **1,192** distinct cadence-scoped tracks.
- Clean-long probe rows by cadence: 10 → 1,505; 30 → 523; 60 → 372.
- Same-start/end cross-cadence result: **199 cadence rows**, representing **94 distinct physical endpoint keys**.
- These endpoints occur in **78 distinct law/seed pairs** across **69 laws** with at least one qualifying seed.
- Exactly **9 laws** satisfy the preregistered requirement in at least two of the three screening seeds:

`{0, 12, 35, 52, 73, 94, 209, 225, 298}`

- None qualifies in all three seeds; each qualifies in exactly two. This is screening recurrence, not an event-probability estimate.

## MINIMAL ELIGIBILITY EVIDENCE

Each example below is one qualifying endpoint; all listed cadence rows independently passed the ≥8-observation and whole-track zero-complex-event gates. `n` is the full cadence-scoped track observation count. Endpoint counts show all qualifying endpoints for that law/seed, while the displayed endpoint is one representative.

| Law | Seed | Qualifying endpoints | Representative start→end | Cadence evidence `(cadence: track, P, M, n)` |
|---:|---:|---:|---:|---|
| 0 | 2001 | 1 | 0→180 | `30: t4, .834164, .400000, 21`; `60: t4, .834164, .400000, 11` |
| 0 | 2002 | 1 | 60→240 | `30: t3, .820366, .461538, 21`; `60: t3, .820366, .461538, 11` |
| 12 | 2001 | 1 | 60→240 | `30: t8, .881298, .384615, 19`; `60: t1, .881298, .384615, 11` |
| 12 | 2003 | 3 | 60→240 | `30: t0, .837082, .375000, 21`; `60: t0, .837082, .375000, 11` |
| 35 | 2002 | 1 | 0→180 | `30: t4, .832091, .333333, 21`; `60: t4, .832091, .333333, 11` |
| 35 | 2003 | 1 | 360→540 | `30: t3, .853486, .454545, 21`; `60: t3, .853486, .454545, 11` |
| 52 | 2001 | 2 | 60→120 | `10: t11, .825785, .100000, 56`; `60: t7, .830360, .333333, 10` |
| 52 | 2003 | 1 | 60→240 | `30: t1, .849545, .428571, 21`; `60: t1, .849545, .428571, 11` |
| 73 | 2001 | 1 | 0→60 | `10: t2, .800389, .454545, 61`; `60: t2, .800389, .454545, 11` |
| 73 | 2002 | 1 | 60→240 | `30: t4, .818454, .400000, 21`; `60: t4, .818454, .400000, 11` |
| 94 | 2001 | 1 | 0→180 | `30: t4, .828012, .333333, 21`; `60: t4, .828012, .333333, 11` |
| 94 | 2002 | 2 | 0→30 | `10: t3, .801622, .416667, 61`; `30: t3, .801622, .416667, 21` |
| 209 | 2001 | 1 | 0→180 | `30: t1, .923446, .444444, 21`; `60: t1, .923446, .444444, 11` |
| 209 | 2003 | 1 | 0→180 | `30: t5, .820320, .400000, 21`; `60: t5, .820320, .400000, 11` |
| 225 | 2002 | 1 | 150→180 | `10: t25, .811560, .454545, 50`; `30: t1, .811560, .454545, 21` |
| 225 | 2003 | 1 | 0→180 | `30: t2, .855712, .363636, 21`; `60: t2, .855712, .363636, 11` |
| 298 | 2002 | 1 | 330→360 | `10: t54, .834465, .285714, 34`; `30: t34, .834465, .285714, 11` |
| 298 | 2003 | 1 | 120→150 | `10: t29, .859192, .428571, 49`; `30: t12, .859192, .428571, 18` |

## INFERRED

- EXP02 has produced nine laws that meet the **predeclared screening permission gate** for a separate direct audit and fresh-seed protocol.
- This calculation does not establish dynamical individuality. Cross-cadence recurrence and two screening seeds reduce only some observer-specific failure modes; they do not reject static occupancy or sparse look-alike stitching.
- The distinction among 10,302 raw rows, 2,400 clean-long rows, 94 endpoint keys, 78 law/seed pairs, and 9 eligible laws is essential; none of these counts is a count of independent biological or dynamical events.

## HYPOTHESIS

- At least some of the nine eligible laws may be dominated by static spatial occupancy or look-alike exchange rather than a self-maintaining entity.

## WHAT WOULD FALSIFY THIS?

- Direct dense-trajectory and association-edge audit that rejects static occupancy/look-alike flux for a frozen candidate, followed by survival under a preregistered fresh-seed hold-out and, if authorized, controlled perturbation.
- Conversely, failure under the frozen fresh-seed rule, sensitivity to cadence/tracker controls, or evidence of occupancy/alias stitching falsifies promotion of that law without changing thresholds.

## FAILURES / DEAD ENDS

- The first attempt to pass the multiline inline program through Windows `python -c $code` lost embedded quotes and stopped immediately with a `SyntaxError`; it read no experiment rows and changed no files. The same program was then streamed over stdin with `python -`, completing successfully in 17.418 seconds.

## DECISIONS

- No scientific or architectural decision was made. I applied the frozen rule literally and did not rank or rescue candidates post hoc.

## UNRESOLVED RISKS

- All qualifying rows retain the explicitly logged sparse-alias risk.
- This audit verified association-edge files cryptographically and by row count but did not visually or mechanistically inspect every candidate trajectory/edge sequence. That is the required next stage before promotion.
- Raw shards are local and ignored; verified checksums are integrity evidence for present files, not a remote backup.

## FILES CREATED OR MODIFIED

- Created only this journal.

## HANDOFF

The coordinating agent may record EXP02 as complete and candidate-audited. The exact next authorized action is to preserve the eligible set `{0,12,35,52,73,94,209,225,298}`, perform direct raw descriptor/association-edge/static-flux audits under unchanged rules, and freeze a separate fresh-seed hold-out protocol only for candidates that survive that audit. Do not interpret the nine-law set as evidence and do not lower thresholds.

## ENDING GIT STATE

- HEAD remained `6c593780ab33326fd0957f73bb885bfe1c15ab84`; no shared code or experiment output was modified by this agent.
- This journal is the agent's only worktree addition. At final inspection, concurrent parent/peer work had also modified `edlab/experiments/streaming.py` and `tests/test_experiment_pipeline.py`, created another agent journal, and retained the untracked EXP02 root outputs; none of those changes was made or altered by this agent.

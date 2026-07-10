# Tracker Re-audit — RUN-20260710-TRK2

## AGENT / ROLE

- Agent: `/root/tracker_validation`
- Role: bounded independent re-auditor of detector/tracker/continuity repairs
- Method: exact-commit source inspection, full test suite, and replay of the prior adversarial fixtures

## RUN ID

`RUN-20260710-TRK2`

## START TIME

`2026-07-10 04:21:14 CEST`

## END TIME

`2026-07-10 04:27:25 CEST` (final journal and repository check)

## PRIOR AUDIT REFERENCED

This re-audit explicitly follows the STOP/REPAIR verdict in:

`docs/agent_journals/2026-07-10/0411_tracker-validation_RUN-20260710-0343-TRK.md`

The previous audit found:

1. many-to-many crossings were also emitted as resolved split and merge events;
2. empty-snapshot disappearance events used stale prior timestamps;
3. accepted/rejected association terms and child local indices were not losslessly persisted;
4. ambiguous transitions were measured without interval flags;
5. the sparse look-alike exchange produced a silent clean high-`P`/low-`M` alias;
6. the committed sensitivity null omitted the size-ratio and detector grids;
7. direct association already passed the prohibition on final `P`, Jaccard `M`, and IDs.

## STARTING GIT STATE

- Repository: `C:\Users\tommy\Documents\ising v3`
- Branch: `main`
- Requested revision: `b8aaaf2`
- `HEAD`: `b8aaaf2b414a7130bc00e01e82842c0b2d727183`
- `origin/main`: `b8aaaf2b414a7130bc00e01e82842c0b2d727183`
- `git rev-parse b8aaaf2`: `b8aaaf2b414a7130bc00e01e82842c0b2d727183`
- Worktree: clean
- Commit subject: `fix: repair numerical domain and lineage auditability`

The re-audit therefore ran directly on the exact requested commit. No detached worktree, checkout, or uncommitted implementation state was involved.

## ASSIGNED SCOPE

Re-audit only exact commit `b8aaaf2` after the repairs. Verify:

- many-to-many is no longer reported as resolved split/merge;
- empty-snapshot timestamps are current and explicit;
- `association_edges` includes accepted/rejected pairs, terms, selection, and `local_index`;
- measurements carry interval flags;
- sparse alias remains an explicit unresolved null;
- cadence/distance/size and detector grids execute;
- association still does not use final `P`, `M`, or IDs;
- prior adversarial probes and tests pass.

Do not modify code. Create a new factual journal and issue a clear verdict on authorization of a new diagnostic baseline, without scientific interpretation.

## AUDITED SNAPSHOT HASHES

| File | SHA-256 |
|---|---|
| `edlab/entities/tracking.py` | `8D3119511019AE2FA9DD21230992B1D3410D7A6760FC311324B412EAD4EBFAA6` |
| `edlab/observables/continuity.py` | `FA8C4692260EF6A5B98D7F3D74D169260FC8E5416BA1179AB0230A4D60445982` |
| `edlab/validation/nulls.py` | `03F83CA40C983AE284DB8814BC0E4AD86728D77D47456475B755817E0BEB8128` |
| `edlab/experiments/baseline.py` | `F67DF2C44C2369DC50D2392F3ED5CD02173946273CC6D5B3056A9FB6BAFF1E82` |
| `tests/test_tracker.py` | `DB4331384B2E922024DC2FEF9F4B3E2DBD7F725CF3681D0FB47ABA52927D21EB` |
| `tests/test_continuity.py` | `E56C9E775EADCF99C928BD8084902DC912AD7B98DEC07B4AFC77721FA209694E` |

## ACTIONS PERFORMED

1. Verified exact SHA equality among `HEAD`, `origin/main`, and the requested abbreviated revision.
2. Inspected the repair diff from `65af67e` to `b8aaaf2` and the final detector, tracker, continuity, null, baseline, candidate-audit, protocol, and test code.
3. Executed the full test suite with bytecode and pytest cache writes disabled.
4. Replayed the earlier direct-association, periodic-seam, lifecycle, many-to-many, local-index tie, sparse-alias, threshold/bridge, and cadence/size probes in memory.
5. Added a complete-edge matrix probe containing one selected edge, one distance-rejected edge, and one size-rejected edge.
6. Parsed the live cadence/tracker/detector null table and checked every cell.
7. Compared each previous STOP/REPAIR item with current behavior.
8. Created only this journal.

## FILES READ

Important files actually inspected:

- `edlab/entities/detection.py`
- `edlab/entities/tracking.py`
- `edlab/observables/continuity.py`
- `edlab/observables/phenotype.py`
- `edlab/specs.py`
- `edlab/validation/nulls.py`
- `edlab/experiments/baseline.py`
- `edlab/experiments/audit_candidates.py`
- `tests/test_tracker.py`
- `tests/test_continuity.py`
- `tests/test_entities.py`
- `tests/test_experiment_pipeline.py`
- `docs/CORE_V0_PROTOCOL.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/experiments/HOLDOUT_COREV0_01_PROTOCOL.md`
- `docs/agent_journals/2026-07-10/0411_tracker-validation_RUN-20260710-0343-TRK.md`

## FILES CREATED OR MODIFIED

- Created only `docs/agent_journals/2026-07-10/0425_tracker-reaudit_RUN-20260710-TRK2.md`.
- No source, test, protocol, state, index, experiment, or result file was modified by this auditor.

## COMMANDS / EXPERIMENTS EXECUTED

Exact revision and cleanliness:

```powershell
git rev-parse HEAD
git rev-parse origin/main
git rev-parse b8aaaf2
git status --short
```

Full suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
```

Observed result:

```text
28 passed in 1.12s
```

Adversarial probes were piped to `.venv\Scripts\python.exe -` and created no file. They reused the exact structures documented in the prior journal, including the sparse exchange at locations `0.35` and `0.65`, the all-equal local-index tie, and the near-boundary count sequence `16,14,12,10,8,6,4`.

## OBSERVED — REPAIR VERIFICATION

### 1. Direct final-P/M/ID independence remains intact

Static inspection shows candidate gating/ranking still reads only:

- periodic centroid distance;
- size ratio computed from `particle_indices` count;
- `max_centroid_distance` and `min_size_ratio`.

The tracker does not read `particle_ids`, `phenotype`, `phenotype_similarity`, or `material_retention` for association.

The replay changed lag-1 `P` from `[1.0,1.0]` to `[1.3838965267367376e-87,1.3838965267367376e-87]` and used disjoint fresh IDs giving `M=[0.0,0.0]`. Results:

- same topology: true;
- same complete `AssociationEdge` records: true;
- one track retained throughout.

Verdict: PASS.

### 2. Many-to-many is ambiguity only

The two-parent/two-child overlapping crossing produced:

```text
event kinds = birth, birth, continuity, continuity, ambiguous_association
split count = 0
merge count = 0
ambiguity count = 1
association edges = 4
selected edges = 2
edge classifications = ambiguous_candidate x4
```

Every measurement spanning the crossing had `interval_has_ambiguity=true`.

The separate exact split-then-merge fixture still emitted one resolved split and one resolved merge, with no ambiguity. The repair therefore distinguishes one-to-many, many-to-one, and many-to-many topologies as requested.

Verdict: CORRECTED / PASS.

### 3. Empty-snapshot timestamps

`LineageTracker.update` now requires explicit `snapshot_step` and `time` when an active previous lineage is followed by an empty snapshot. The lifecycle replay ended with:

```text
kind = disappearance
snapshot_step = 4
time = 4.0
detail = no entity observations in current snapshot
```

The baseline passes each selected snapshot's actual step and simulated time into every update, including empty detections. Mixed step/time entities are rejected.

Verdict: CORRECTED / PASS.

### 4. Complete association-edge evidence

For every previous-track/current-detection pair, `AssociationEdge` contains:

- snapshot step and time;
- parent track ID;
- child `local_index`;
- centroid distance;
- size ratio;
- individual distance and size gate results;
- score;
- selected boolean;
- classification.

The explicit one-parent/three-child probe returned exactly three edges:

| child local index | distance gate | size gate | selected | classification |
|---:|---:|---:|---:|---|
| 0 | true | true | true | `unique_candidate` |
| 1 | false | true | false | `rejected_by_gate` |
| 2 | true | false | false | `rejected_by_gate` |

All required fields were present on all three records. The many-to-many fixture separately persisted all four feasible pairs.

`run_baseline` writes `local_index` and centroid on entity observations and writes all `association_edges` via `asdict` to `association_edges.csv`.

Verdict: CORRECTED / PASS.

### 5. Measurement interval flags

`ContinuityMeasurement` now contains:

- `interval_has_ambiguity`;
- `interval_has_split_or_merge`;
- `unresolved_sparse_alias_risk`.

The baseline calls `measure_tracks(..., events=tracker.events)` and persists these fields. Observed probes:

- all two many-to-many crossing measurements had ambiguity=true;
- the split/merge lifecycle produced three measurements flagged split-or-merge;
- the sparse alias measurements had ambiguity=false but unresolved-sparse-alias-risk=true.

The local-index-only tie still changed post-association `M` from `[1,1]` to `[0,0]`, as expected for an unresolved tie, but both variants now had:

```text
interval_has_ambiguity = [true,true]
interval_has_split_or_merge = [false,false]
edge classification = ambiguous_candidate x4
```

The implementation does not pretend to solve that tie; it marks it as unresolved.

Verdict: CORRECTED FOR AUDITABILITY / PASS.

### 6. Sparse look-alike alias is a first-class unresolved null

Direct execution returned:

```text
name = SPARSE_LOOKALIKE_ALIAS
passed = true
P = 1.0
M = 0.0
detail = expected unresolved observational alias ... hold-out cannot by itself reject this null
```

The same direct replay still generated two births and two clean spatial continuities with no geometric ambiguity. This is the correct expected behavior: the physical non-identifiability is not “fixed,” but it is now registered, tested, persisted as a live null, and attached to every high-`P`/low-`M` measurement through `unresolved_sparse_alias_risk=true`.

The baseline summary explicitly states that all initial-probe rows retain unresolved sparse-alias risk.

Verdict: CORRECTED AS A CONTROL; PHYSICAL LIMITATION INTENTIONALLY UNRESOLVED.

### 7. Cadence/distance/size and detector grid

`TRACKER_CADENCE_SENSITIVITY` produced 36 passing cells:

- 27 tracker cells = cadences `{10,30,60}` × distance scales `{0.8,1.0,1.2}` × size-ratio gates `{0.20,0.25,0.30}`;
- 9 detector cells = radius scales `{0.8,1.0,1.2}` × minimum sizes `{3,4,5}`;
- failed cells: none;
- endpoint `P=1.0`, endpoint `M=0.0` on the known-continuity fixture.

The prior near-boundary size probe was also replayed. It still breaks only at cadence 60 with `min_size_ratio=0.30`, where the direct `16 -> 4` ratio is `0.25`. This is expected evidence that empirical candidates near a gate remain parameter-sensitive; it is not a failure of the safe-margin null.

Verdict: REQUIRED GRID CORRECTED / PASS; CANDIDATE-SPECIFIC SENSITIVITY REMAINS REQUIRED.

### 8. Periodic seam and detector semantics

The previous seam replay remained one lineage with fresh IDs:

- entity counts `[1,1]`;
- `P=0.9999999999999997`;
- `M=0.0`;
- same lineage=true.

Inclusive connection-radius behavior and the documented bridge-chain behavior were unchanged and passed.

Verdict: PASS, unchanged.

### 9. Static material-flux false positive remains live

`STATIC_MOTIF_WITH_MATERIAL_FLUX` still returns same lineage, `P=1`, `M=0`, and `passed=true` as the expected probe-positive null.

Verdict: PASS AS EXPECTED FALSE POSITIVE.

## CORRECTED VS NOT CORRECTED

### Corrected at `b8aaaf2`

| Previous STOP item | Current disposition |
|---|---|
| Many-to-many emitted false split/merge records | Corrected: ambiguity only; no split/merge in replay. |
| Empty disappearance timestamp stale | Corrected: explicit current step/time required and persisted. |
| Rejected/selected association evidence missing | Corrected: complete pair matrix with terms, gates, local index, score, selection, classification. |
| Ambiguous measurements unflagged | Corrected: interval ambiguity and split/merge flags persisted by baseline. |
| Sparse alias absent from null registry | Corrected as live unresolved null and per-probe-row risk flag. |
| Size-ratio and detector sensitivity absent | Corrected: 27 tracker plus 9 detector cells. |
| Association independence from final P/M/IDs | Was already passing and remains passing. |

### Not corrected or intentionally unresolved

1. Sparse look-alike occupancy exchange remains observationally indistinguishable from high-`P`/low-`M` continuity using the current snapshots. It is now explicit, not eliminated.
2. Deterministic local-index tie-breaking can still change `M` on an ambiguous crossing. The interval is now correctly marked ambiguous and must not be promoted as resolved evidence.
3. Connected-component chain bridging remains a documented detector artifact.
4. The periodic circular centroid can still serialize a seam center as `box_size` (`1.0`) rather than canonical `0.0`; minimum-image tracking remained correct in the probe.
5. `material_retention(empty, empty)` still returns `1.0`; normal detector entities are non-empty, so this is outside the standard path.
6. `measure_tracks` accepts `events=None`; callers other than the baseline could omit events and receive false interval flags. The production baseline call is correct, but the API remains a footgun.
7. The summary's `tracker_auditable` boolean checks evidence presence, not a formal row-count proof that the persisted edge matrix is complete. This re-audit independently established completeness on controlled fixtures.
8. The safe-margin 36-cell null cannot establish robustness of a natural candidate. Candidate-specific tables and direct trajectory audit remain necessary.
9. Split/merge branch histories are still represented as selected tracks plus events rather than full multi-hypothesis lineage paths; measurements spanning complex events are flagged instead of interpreted as simple continuity.

None of these remaining items blocks a strictly diagnostic rerun if its interpretation boundary is honored.

## GATE VERDICT

| Required gate | Verdict |
|---|---|
| Exact requested SHA and clean worktree | PASS |
| Full tests | PASS — 28/28 |
| No association use of final P/M/IDs | PASS |
| Fresh-ID topology invariance | PASS |
| Periodic seam | PASS |
| True split and merge retained | PASS |
| Many-to-many not resolved as split/merge | PASS |
| Current timestamps for empty snapshot | PASS |
| Complete accepted/rejected association edges and local index | PASS |
| Measurement interval ambiguity/complexity flags | PASS |
| Sparse alias explicit and live | PASS AS UNRESOLVED NULL |
| Static-flux false positive live | PASS AS EXPECTED FALSE POSITIVE |
| Cadence/distance/size grid | PASS — 27/27 |
| Detector grid | PASS — 9/9 |

## OVERALL VERDICT

### New diagnostic baseline

`GO — AUTHORIZED AT EXACT COMMIT b8aaaf2b414a7130bc00e01e82842c0b2d727183.`

This authorization is only for a new, separately identified diagnostic baseline that exercises and persists the repaired measurement pipeline. It does not validate the old `5fa941b` baseline retrospectively and does not authorize reusing its candidate ranking as confirmed evidence.

Conditions of this GO:

1. manifest records exact commit `b8aaaf2b414a7130bc00e01e82842c0b2d727183`;
2. use a new experiment/output ID; do not overwrite the superseded baseline;
3. persist `association_edges.csv`, observations with local indices, events, and all measurement flags;
4. report raw and lineage-flagged counts separately;
5. retain `unresolved_sparse_alias_risk=true` for every high-`P`/low-`M` row;
6. execute all live nulls and the sensitivity grid in the run;
7. keep all results diagnostic and exploratory.

### Scientific interpretation or candidate promotion

`NO-GO.`

No high-`P`/low-`M` row, cross-cadence recurrence, or fresh-seed survivor may be interpreted as persistent dynamical individuality from this tracker alone. Direct trajectory audit and an intervention capable of rejecting static occupancy/material-flux and sparse look-alike stitching remain mandatory.

## OBSERVED

- Exact target revision was clean and matched `origin/main`.
- All 28 tests passed.
- Every requested repair produced the intended controlled behavior.
- The sparse alias and local-index tie remain numerically reproducible but are now explicitly visible in nulls and flags.

## INFERRED

- The repaired pipeline is technically adequate to generate a new auditable diagnostic baseline.
- The repair improves falsifiability by preserving failures and ambiguity rather than forcing a resolved lineage narrative.
- It does not supply new physical information capable of resolving sparse occupancy aliases.

## HYPOTHESIS

Natural high-`P`/low-`M` rows in a new diagnostic baseline may still be dominated by static material flux, sparse look-alike stitching, or gate-sensitive correspondence. This remains a hypothesis about future output, not an observed result of this re-audit.

## WHAT WOULD FALSIFY THIS?

The remaining alias hypothesis would be weakened by candidate-specific dense trajectory replay, stability over the frozen detector/tracker grid, direct exclusion of stationary occupancy exchange, and a controlled perturbation/recovery experiment whose response differs from the static-flux and look-alike nulls.

## FAILURES / DEAD ENDS

- None of the requested tests or probes failed.
- No dependency installation was needed; the existing `.venv` contained NumPy 2.5.1, pytest 8.4.2, and Matplotlib 3.11.0.
- The prior near-boundary cadence/size probe intentionally retained one failing cell. This is a reproduced sensitivity boundary, not a regression of the safe-margin null.

## DECISIONS MADE

- Treated explicit preservation of `SPARSE_LOOKALIKE_ALIAS` as a successful control, not a claim that the alias was solved.
- Accepted deterministic selected edges inside ambiguous cases only because the complete edge matrix and interval ambiguity flags prevent those selections from masquerading as resolved evidence.
- Authorized only a new diagnostic baseline at the exact audited commit.
- Withheld authorization for scientific interpretation and candidate promotion.

## UNRESOLVED RISKS

- Sparse aliases remain unidentifiable from current occupancy geometry, `P`, and `M` alone.
- Empirical candidates can remain detector/tracker/cadence sensitive despite the safe-margin null.
- Optional omission of events from `measure_tracks` can suppress interval flags outside the baseline path.
- Full multi-hypothesis lineage metrics across actual split/merge events are not implemented.
- Feature scaling and shared size information can still couple tracker selection with observed phenotype continuity without directly using final `P`.

## HANDOFF

The main agent may launch a new diagnostic baseline at exact commit `b8aaaf2b414a7130bc00e01e82842c0b2d727183` under the conditions above. It should index this journal, create a new experiment ID, preserve all raw edge/event/measurement artefacts, and state prominently that diagnostic probe occupancy is not scientific evidence.

Do not resume the old hold-out as if prior candidate interpretation had been repaired retrospectively. Any later hold-out selection must be derived from the new diagnostic baseline and remain subordinate to direct trajectory and intervention controls.

## ENDING GIT STATE

- Branch: `main`
- HEAD at analysis conclusion: `b8aaaf2b414a7130bc00e01e82842c0b2d727183`
- `origin/main`: same commit
- Worktree before journal creation: clean
- Other agent journal present untracked at final check: `docs/agent_journals/2026-07-10/0421_numerical-reaudit_RUN-20260710-NUM2.md`
- Only file created or modified by this auditor: this journal
- Commits created by this auditor: none
- Push performed by this auditor: no

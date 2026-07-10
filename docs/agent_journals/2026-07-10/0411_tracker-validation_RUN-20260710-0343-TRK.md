# Tracker Validation — RUN-20260710-0343-TRK

## AGENT / ROLE

- Agent: `/root/tracker_validation`
- Role: independent detector / tracker / observables auditor
- Review method: static code inspection, existing-test execution, and non-persistent adversarial probes

## RUN ID

`RUN-20260710-0343-TRK`

## START TIME

`2026-07-10 04:00:49 CEST` (first timestamped command available to this auditor)

## END TIME

`2026-07-10 04:15:00 CEST` (final journal and Git-state verification)

## STARTING GIT STATE

- Repository: `C:\Users\tommy\Documents\ising v3`
- Remote: `origin = https://github.com/Mythmaker28/emergent-dynamics-lab.git`
- Branch: `main`
- HEAD: none; branch was unborn at the first recorded check
- Worktree: dirty, with `.gitignore`, `.runtime/`, `docs/`, `edlab/`, `pyproject.toml`, and `tests/` untracked
- Concurrency note: other agents created and committed the implementation while this audit was running. `5fa941bf7c0b757f5535965fad62c190a94fefa6` became `HEAD` and `origin/main` during the audit; then `c7fd8e7481fd3807ed36976db5bbef2fe3ea7dad` became `HEAD` and `origin/main`. This auditor did not create either commit.

## ASSIGNED SCOPE

Audit independently the current detector, tracker, and `P`/`M` observables. Verify that association does not use final `P`, material Jaccard `M`, or particle IDs; exercise periodic seams, fresh IDs, split/merge, and ambiguous crossings; perform a small non-persistent cadence/parameter sensitivity study; verify that `STATIC_MOTIF_WITH_MATERIAL_FLUX` remains the expected same-lineage high-`P`/low-`M` false positive. Do not modify implementation code. Create this agent's factual journal as the only file modified by this auditor.

## AUDITED SNAPSHOT

The core files used for the final verdict had these SHA-256 values:

| File | SHA-256 |
|---|---|
| `edlab/entities/detection.py` | `064226913F1BE5DD58732D2840293DAEA73FF02BAFFA6BF4CBE028678134C641` |
| `edlab/entities/tracking.py` | `0B92BB1F5CCD3434F0077E2D05D2C27CBECA457C7A25244F8BB1CF9021498AF8` |
| `edlab/observables/continuity.py` | `6AB7261804DE3A8DD5A6804EA616B261E5D5A211BA15DC3B02C9C420C79151F9` |
| `edlab/observables/phenotype.py` | `F0B9F2529BC0C260BD6D4B7D890520A3D0A17CE9892F8922C3F2035C20186D5B` |
| `edlab/validation/nulls.py` | `DFB0A3D8412E31D0AD6CD4A5E7C18F7086E2727066DDCF4CBE5FAB7ADB4DBF1C` |
| `edlab/experiments/baseline.py` | `6A5F82C96BC577D5A5171CF62529A1BAD132E899D4136F4A2ED2BBB4FD1FB3B0` |
| `tests/test_entities.py` | `573652FB6E546A7E8AB724CAF55A53FCC0C67AE4DC9928C2F62959EA202B924E` |
| `tests/test_tracker.py` | `5C0EFEB1EFEDAB011225EA6807DBE8307F70B48966C57B13FF8E634A9669BDAD` |
| `tests/test_continuity.py` | `F84E23EF34E2A1A2C1C3DE8EFA0ADABE05BE89C9380AEE9C46CEC1070DEDA8D2` |

The baseline artefact inspected was `BASELINE-COREV0-20260710-001`, whose manifest identifies physics/measurement commit `5fa941bf7c0b757f5535965fad62c190a94fefa6`.

## ACTIONS PERFORMED

1. Read the three supplied operating, journaling, and 30-minute scheduling protocols, focusing on detector/tracker/observable acceptance requirements.
2. Inspected detector, periodic centroid, tracker association and lineage events, phenotype construction, `P`, Jaccard `M`, all live nulls, baseline persistence/gates, and relevant tests.
3. Inspected the committed CORE V0 protocol, project state, candidate-audit implementation, baseline summary/manifest, and frozen hold-out protocol where they affected interpretation of tracker output.
4. Executed the relevant detector/tracker/observable tests with caches and bytecode disabled.
5. Executed non-persistent in-memory probes for direct association independence, periodic seams, detector threshold and bridge behavior, lifecycle events, ambiguous crossings, sparse crossing aliasing, local-index tie sensitivity, cadence/parameter grids, orthogonal `P`/`M`, and both tracker-related nulls.
6. Reported the gate-level findings to the main agent before journal completion because a hold-out protocol was being prepared concurrently.
7. Removed the temporary audit-only Python dependency directory after all probes. No probe script or dependency was persisted in the repository.

## FILES READ

Important files actually inspected:

- `edlab/entities/detection.py`
- `edlab/entities/tracking.py`
- `edlab/observables/continuity.py`
- `edlab/observables/phenotype.py`
- `edlab/specs.py`
- `edlab/state.py`
- `edlab/validation/nulls.py`
- `edlab/experiments/baseline.py`
- `edlab/experiments/audit_candidates.py`
- `tests/test_entities.py`
- `tests/test_tracker.py`
- `tests/test_continuity.py`
- `tests/test_experiment_pipeline.py`
- `docs/CORE_V0_PROTOCOL.md`
- `docs/PROJECT_STATE.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/DECISION_LOG.md`
- `docs/experiments/HOLDOUT_COREV0_01_PROTOCOL.md`
- `results/BASELINE-COREV0-20260710-001/summary.json`
- `results/BASELINE-COREV0-20260710-001/manifest.json`
- `results/BASELINE-COREV0-20260710-001/candidate_audit.json`
- the three attached source prompts

## FILES CREATED OR MODIFIED

- Created only `docs/agent_journals/2026-07-10/0411_tracker-validation_RUN-20260710-0343-TRK.md`.
- No implementation, test, result, state, protocol, index, or experiment file was modified by this auditor.
- Temporary packages were installed only under `C:\Users\tommy\AppData\Local\Temp\edlab-audit-RUN-20260710-0343-TRK` and were deleted after the probes (`EXISTS_AFTER=False`).

## COMMANDS / EXPERIMENTS EXECUTED

Representative reproducible commands and probe families:

```powershell
rg -n "^" -- edlab/entities/detection.py
rg -n "^" -- edlab/entities/tracking.py
rg -n "^" -- edlab/observables/continuity.py
rg -n "^" -- edlab/observables/phenotype.py
rg -n "^" -- edlab/validation/nulls.py
```

The system Python initially lacked both `numpy` and `pytest`. Audit-only versions `numpy==2.5.1` and `pytest==8.4.2` were installed to the temporary directory named above. Tests were then run without repository caches:

```powershell
$env:PYTHONPATH = "$env:TEMP\edlab-audit-RUN-20260710-0343-TRK"
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest -p no:cacheprovider -q `
  tests/test_entities.py tests/test_tracker.py tests/test_continuity.py
```

Observed result on the final current versions: `9 passed in 0.15s`.

Non-persistent Python was piped on stdin; no probe file was created. The fixtures were:

- identical centroid/size sequences with stable versus disjoint fresh IDs and stable versus extreme alternating phenotype values;
- a six-particle motif crossing the periodic seam by `0.05` with disjoint endpoint IDs;
- detector pairs at and just above the connection radius, plus a three-point bridge chain;
- birth, continuation, split, merge, and disappearance sequence;
- two look-alike entities with overlapping feasible regions;
- a sparse exact location swap with known material sets and `max_centroid_distance` values `0.12` and `0.31`;
- an all-equal ambiguous association repeated after changing only child `local_index` labels;
- cadences `{10,30,60}`, distance multipliers `{0.8,1.0,1.2}`, and size-ratio multipliers `{0.8,1.0,1.2}` on a safe known-continuity seam fixture;
- a near-boundary count trajectory `16,14,12,10,8,6,4` under cadences `{10,30,60}` and `min_size_ratio` values `{0.20,0.25,0.30}`;
- direct calls to `static_motif_material_flux_null()` and `tracker_cadence_sensitivity_null()`.

## OBSERVED

### 1. Direct use of final P, M, or IDs in association: not present

Static inspection of `LineageTracker.update` found that candidate gating and ranking read only:

- periodic centroid distance;
- count derived from `particle_indices`;
- `max_centroid_distance`;
- `min_size_ratio`.

The tracker does not import `phenotype_similarity` or `material_retention`; it does not read `entity.phenotype` or `entity.particle_ids` while associating. The continuity event string explicitly says IDs were not used.

The runtime probe held geometry and size fixed while changing endpoint IDs to disjoint sets and alternating the one-dimensional phenotype between `+100` and `-100`:

- stable-phenotype lag-1 `P`: `[1.0, 1.0]`;
- changed-phenotype lag-1 `P`: `[1.3838965267367376e-87, 1.3838965267367376e-87]`;
- fresh-ID lag-1 `M`: `[0.0, 0.0]`;
- track topology in both runs: one birth followed by two continuities on track `0`.

This is a direct PASS for the prohibition on optimizing or hard-gating association with final `P`, Jaccard `M`, or IDs.

It is not proof of statistical independence: size participates in both the association score and the phenotype vector's count fraction, so correspondence selection can still select on a quantity contributing to `P`.

### 2. Periodic seam and fresh IDs

The six-particle seam fixture produced one entity at both snapshots. Observed centroids were approximately `[1.0, 0.5]` and `[0.05000000000000003, 0.5]`; minimum-image tracking retained one lineage across the seam. Endpoint values were:

- `P = 0.9999999999999997`;
- `M = 0.0`;
- same lineage: true.

The relevant committed seam/order tests also passed.

Minor detector artifact: the circular mean can serialize the seam centroid as exactly `box_size` (`1.0`) instead of canonical `0.0`. Minimum-image calculations remain correct in this probe, but the raw centroid is outside the usual half-open coordinate interval.

### 3. Detector threshold and connected-component bridge

- At an exactly representable radius of `0.125`, the pair formed one component.
- At `nextafter(0.125, 1.0)`, the pair formed two singleton components.
- Points at `0.10`, `0.19`, and `0.28` formed one connected component with radius `0.10`, even though the endpoint distance was `0.18`.

This matches the documented inclusive `<=` convention and documented chain-bridge artifact. The bridge remains a possible detector false merge, as intended by the protocol warning.

### 4. Fresh-ID and orthogonal observable controls

Basic observable probes returned:

- identity phenotype: `P = 1.0`;
- controlled one-unit phenotype deformation: `P = exp(-1) = 0.36787944117144233`;
- `M` for 100% material identity: `1.0`;
- equal-size sets with 50% overlap: `1/3`;
- disjoint non-empty sets: `0.0`.

`material_retention(empty, empty)` returns `1.0`. Normal detector-produced entities cannot be empty because `min_size >= 2`, but manually constructed empty observations would receive a perfect material-retention value rather than being rejected.

### 5. Required static material-flux false positive remains live

Current direct execution returned:

```text
name = STATIC_MOTIF_WITH_MATERIAL_FLUX
passed_expected_false_positive = true
same_lineage = true
P = 1.0
M = 0.0
```

This is the intended probe-positive null. It must not be interpreted as evidence of dynamical individuality.

### 6. Nominal split/merge lifecycle is present, but event semantics overstate alternatives

The lifecycle fixture emitted birth, continuity, split, merge, ambiguous-association, and disappearance events. The explicit split listed one parent and both child track IDs; the explicit merge listed both parents and one child track ID.

However, split and merge events are generated from all physically compatible candidate edges, not from a resolved many-to-one or one-to-many lineage decision. In the two-entity overlapping crossing probe, the tracker emitted:

```text
birth x2
continuity x2
split x2
ambiguous_association x1
merge x2
```

The probe represented a crossing with two detections before and two after. The two split and two merge records therefore describe compatibility alternatives, not established biological/physical split or merge events. Downstream event counts cannot treat every such record as a confirmed topology change.

### 7. Overlapping ambiguity is logged, but ambiguous measurements are still produced

For overlapping feasible regions, `ambiguous_association` correctly listed both parent tracks and both child tracks. This is a PASS for detecting that particular ambiguity.

The greedy assignment still appends the selected observations to ordinary tracks, and `measure_tracks` calculates ordinary `P`/`M` rows across the ambiguous interval. Measurements contain no ambiguity field. The baseline initially counts all such rows in the joint distribution and initial probe; the later candidate audit removes tracks with logged complex events, but the raw baseline gate and probe do not.

An exact-tie fixture was run twice with identical physical child centroids, material memberships, phenotypes, and event topology. Only child `local_index` labels were exchanged. Results changed from:

```text
canonical local indices: P=[1.0,1.0], M=[1.0,1.0]
swapped local indices only: P=[1.0,1.0], M=[0.0,0.0]
```

Both runs emitted the same two continuities, two splits, two merges, and one ambiguity. Thus deterministic local-index tie-breaking can determine the measured material continuity on an ambiguous transition. Logging the ambiguity is useful, but interpreting the resulting measurement as an ordinary candidate is not justified.

### 8. Sparse look-alike crossing can alias silently

At step 0, two equal-size look-alikes were placed at `x=0.35` and `x=0.65` with disjoint persistent material sets A and B. At step 60, the material sets had crossed to the opposite location while the two observed centroids remained at the same two locations.

With `max_centroid_distance=0.12`, the tracker matched by stationary location and returned:

```text
event kinds = [birth, birth, continuity, continuity]
ambiguous_association = false
P = [1.0, 1.0]
M = [0.0, 0.0]
```

Exact minimal fixture used (the helper deliberately exposes IDs only for post-association audit):

```python
import numpy as np

from edlab.entities.detection import EntityObservation
from edlab.entities.tracking import LineageTracker
from edlab.observables.continuity import measure_tracks
from edlab.observables.phenotype import Phenotype
from edlab.specs import TrackerSpec


def obs(local: int, step: int, x: float, ids: range) -> EntityObservation:
    return EntityObservation(
        local_index=local,
        snapshot_step=step,
        time=float(step),
        particle_indices=tuple(range(8)),
        particle_ids=frozenset(ids),
        centroid=np.array([x, 0.5]),
        phenotype=Phenotype(
            ("lookalike",), np.array([0.0]), {"lookalike": 0.0}
        ),
    )


A = range(0, 8)
B = range(100, 108)
tracker = LineageTracker(
    TrackerSpec(max_centroid_distance=0.12, min_size_ratio=0.5),
    box_size=1.0,
)
tracker.update([obs(0, 0, 0.35, A), obs(1, 0, 0.65, B)])
tracker.update([obs(0, 60, 0.35, B), obs(1, 60, 0.65, A)])
measurements = measure_tracks(tracker.tracks, lag_indices=(1,))

assert [event.kind for event in tracker.events] == [
    "birth", "birth", "continuity", "continuity"
]
assert [m.phenotype_continuity for m in measurements] == [1.0, 1.0]
assert [m.material_retention for m in measurements] == [0.0, 0.0]
assert not any(event.kind == "ambiguous_association" for event in tracker.events)
```

The same fixture with `max_centroid_distance=0.31` admits all four candidate edges and therefore logs ambiguity, two compatibility splits, and two compatibility merges, while the greedy selected measurements remain `P=[1,1]`, `M=[0,0]`.

The material labels were used only after association to audit the known fixture; they were not inputs to the tracker. This is a tracker-level false-positive alias: a sparse look-alike exchange can become an apparently clean high-`P`/low-`M` continuation.

With `max_centroid_distance=0.31`, the same greedy location assignments remained high-`P`/low-`M`, but all alternatives became feasible and an ambiguity plus two splits and two merges were logged. The interpretation therefore changes materially with the gate, even though selected tracks do not.

This adversarial observation fixture is not evidence that such a swap occurred in the natural baseline. It demonstrates that the current tracker and `track_clean` filter cannot rule it out.

### 9. Cadence and parameter sensitivity

The concurrently added committed null varies cadences `{10,30,60}` and distance scales `{0.8,1.0,1.2}` on a slow, constant-size, fresh-ID known-continuity fixture. Direct execution passed all 9 cells with one lineage, endpoint `P=1`, and endpoint `M=0`.

The independent safe-margin grid additionally varied the size-ratio gate at `{0.8,1.0,1.2}` of nominal. It passed all 27 cells:

```text
cells = 27
one-lineage cells = 27
ambiguous cells = 0
```

The near-boundary count-turnover fixture showed the expected false-negative sensitivity:

- cadences 10 and 30 retained one lineage for `min_size_ratio` 0.20, 0.25, and 0.30;
- cadence 60 retained one lineage at 0.20 and 0.25;
- cadence 60 split the track into IDs `[0,1]` at 0.30 because the direct size change `16 -> 4` has ratio `0.25`.

This does not invalidate the nominal value `0.25`; it proves that candidate-specific conclusions near the gate require the promised tracker/detector sensitivity table. The committed null currently varies only centroid-distance scale, not `min_size_ratio`, detector radius, or detector `min_size`.

The baseline gate named `cadence_control_nonempty` checks only that each cadence produced at least one measurement. Non-emptiness does not establish cross-cadence lineage equivalence or candidate robustness.

### 10. Disappearance timestamps are not current-snapshot timestamps

`LineageTracker.update([])` has no step/time arguments. It records disappearance using each previous observation's step/time. In the lifecycle probe, the final empty update conceptually followed step 3 but recorded disappearance at step `3`, time `3.0` because no current empty-snapshot metadata could be represented.

The baseline calls `update([])` for empty detected snapshots, so these event timestamps can be stale. This prevents exact auditing of when a lineage disappeared and can affect interval joins.

### 11. Persisted association evidence is incomplete

The current continuity detail stores only a combined selected score. It does not persist selected and rejected candidate distances, size ratios, or gate outcomes. Ambiguity details use child local indices, while `entity_observations.csv` does not persist `local_index`. A future auditor therefore cannot losslessly reconstruct all association decisions from artefacts.

The baseline summary marks `tracker_auditable=true` whenever there is at least one event and at least one event kind. That condition is substantially weaker than lossless association auditability.

### 12. Baseline context inspected, not re-executed by this auditor

The committed baseline summary reports:

- `36,722` measurement rows;
- `384` rows in the initial `P>0.8, M<0.5` probe;
- probe fraction rising from about `0.00679` at cadence 10 to `0.02373` at cadence 60;
- `460` logged ambiguous associations;
- `kill_switch_all_green=true`.

The later candidate audit excludes tracks with logged split, merge, or ambiguity and explicitly acknowledges that track-clean rows may still be static occupancy or look-alike stitching. The sparse alias probe above is an example not detected by the current complex-event filter.

This auditor read those artefacts but did not independently rerun the 36 baseline trajectories. Their numeric contents are not claimed as independently reproduced in this journal.

## GATE VERDICT

| Gate | Verdict | Evidence |
|---|---|---|
| No direct final-`P` association | PASS | Source inspection and extreme phenotype-change probe leave topology unchanged. |
| No direct `M`/ID association | PASS | Source inspection and fresh disjoint IDs leave topology unchanged. |
| Periodic seam | PASS WITH MINOR CAVEAT | Same lineage, `P≈1`, `M=0`; raw centroid can equal `box_size`. |
| Detector threshold semantics | PASS | Inclusive radius and just-above behavior match protocol. |
| Detector bridge awareness | PASS AS DOCUMENTED RISK | Bridge chain reproduced; not a physical individuality guarantee. |
| Basic P/M separability | PASS WITH EMPTY-SET CAVEAT | Orthogonal values correct; empty/empty returns `M=1`. |
| Static material-flux null | PASS AS EXPECTED FALSE POSITIVE | Same lineage, `P=1`, `M=0`. |
| Nominal lifecycle event presence | PASS | Birth/continuity/split/merge/disappearance all emitted. |
| Split/merge semantic reliability | FAIL FOR INTERPRETATION | Compatibility alternatives are emitted as split/merge events during crossings. |
| Overlap ambiguity detection | PASS | Explicit ambiguity emitted when both alternatives are within gates. |
| Sparse crossing/gap safety | FAIL | Clean high-`P`/low-`M` swap emitted with no ambiguity at sparse cadence. |
| Ambiguous-transition measurement safety | FAIL | Local-index-only relabel changed `M=1` to `M=0`; measurements still emitted. |
| Cadence safe-margin fixture | PASS | Committed 9/9 cells and independent broader 27/27 cells passed. |
| Tracker/detector sensitivity coverage | PARTIAL / FAIL FOR FULL GATE | Near-boundary size false negative reproduced; committed null omits size-ratio and detector grid. |
| Lossless association auditability | FAIL | Rejected candidate terms/gates and persisted local detection IDs are missing; empty-snapshot death time is stale. |

### Overall verdict

`STOP / REPAIR LINEAGE MEASUREMENT PIPELINE BEFORE SCIENTIFIC INTERPRETATION OR PROMOTION OF HOLD-OUT SURVIVORS.`

The implementation passes the important direct-separation requirement: final `P`, Jaccard `M`, and IDs do not drive correspondence. It does not yet pass the stronger lineage/audit gate needed to assert `kill_switch_all_green=true`. The current baseline remains useful as a technical exploratory artefact, but its clean high-`P`/low-`M` rows are not protected against sparse look-alike stitching.

## INFERRED

- The tracker has removed a major historical false-negative mechanism: fresh IDs alone no longer terminate a geometrically continuous track.
- Correspondence selection still couples the observed `(P,M)` distribution to distance/size gates and deterministic tie-breaking. Formula-level separation of `P` and `M` is therefore necessary but not sufficient.
- The rise in natural baseline probe occupancy at sparser cadences is consistent with observer/tracker aliasing as an alternative explanation. It does not prove that every or any specific baseline row is an alias.
- Logged-complex filtering reduces one known contamination channel but cannot remove silent aliases whose wrong local match is the only edge inside the current distance gate.
- Current split/merge counts are counts of compatibility-event records, not necessarily counts of resolved physical split/merge processes.

## HYPOTHESIS

Some baseline high-`P`/low-`M` rows, including rows on tracks with no logged complex event, may be static material flux or sparse look-alike stitching rather than persistent dynamical individuality.

No conclusion about the existence or absence of the target phenomenon is made from these tracker probes.

## WHAT WOULD FALSIFY THIS?

The tracker-alias hypothesis would be weakened if all of the following were demonstrated on frozen candidates:

1. lossless candidate-edge logs show no unresolved or gate-induced alternative at every measured interval;
2. local-index or particle-storage-order relabeling cannot change selected physical correspondences or candidate `M` values;
3. a preregistered tracker/detector grid, including distance, size-ratio, detection radius, and minimum size, preserves the same physical lineage and endpoint observables;
4. denser snapshot schedules preserve the correspondence rather than revealing crossing, merge, or occupancy replacement;
5. direct trajectory audit and controlled intervention reject static occupancy/material-flux explanations;
6. a kinematic or multi-hypothesis tracker that remains independent of final `P`, `M`, and IDs reaches the same candidate verdict.

## FAILURES / DEAD ENDS

- The first `pytest` attempt failed because the system Python had no `pytest`.
- The system Python also had no `numpy`.
- The Codex bundled workspace-dependency resolver produced no result for more than one minute and was terminated. The audit then used temporary `--target` packages outside the repository and removed them.
- The repository was concurrently transformed from an unborn untracked tree into two committed/pushed revisions. The audited core hashes are recorded above to make the reviewed snapshot explicit.
- The long baseline experiment was not rerun by this auditor; only its persisted summary, manifest, and candidate-audit outputs were inspected.
- The adversarial crossing fixtures operate directly at the `EntityObservation` layer. They establish tracker behavior, not the frequency of such configurations under CORE V0 dynamics.

## DECISIONS MADE

- Classified direct non-use of final `P`, `M`, and IDs as PASS, while explicitly separating that fact from selection-induced dependence through size/distance and tie-breaking.
- Classified split/merge records generated solely from compatible alternatives as unresolved lineage hypotheses rather than confirmed topology changes.
- Classified the committed cadence null as a useful safe-margin smoke test, not a complete tracker/detector sensitivity gate.
- Classified the overall lineage/audit gate as failed despite the baseline's current `kill_switch_all_green=true` field.
- Made no implementation edits because the assigned scope explicitly restricted this agent to one journal file.

## UNRESOLVED RISKS

- Natural baseline rows were not individually replayed with animations or ground-truth diagnostic IDs, so the fraction affected by silent stitching is unknown.
- A tracker based only on previous centroid and count cannot distinguish every sparse look-alike exchange from material flux. A future solution must preserve the prohibition on optimizing final `P` or `M` while adding auditable kinematic evidence or explicit unresolved hypotheses.
- Circular-mean centroids can be unstable for spatially extended bridge-connected components with near-zero resultant vectors.
- `P` uses an unweighted RMS over pre-scaled features; tracker count gating shares information with the count feature, and unbounded velocity-derived features can dominate similarity. Raw-feature audit remains necessary.
- Split branches start new tracks and non-selected merge parents disappear, so `measure_tracks` does not propagate both sides of complex lineage graphs. This may create false negatives for continuity spanning actual split/merge processes.
- The candidate audit's track-level complex-event join depends on event timestamps and track IDs; stale disappearance time and incomplete candidate-edge persistence limit reconstruction.

## HANDOFF

Required before treating the lineage and cadence kill-switch gates as green:

1. Add regression tests for the sparse crossing alias and local-index-only ambiguous tie.
2. Preserve complete candidate-edge evidence: parent track, child detection ID/local index, distance, size ratio, each gate result, combined score, selected/rejected status, and ambiguity reason.
3. Persist detection/local-index identifiers in observation artefacts so event alternatives can be reconstructed.
4. Distinguish `candidate_split`/`candidate_merge` compatibility from resolved split/merge events, or represent an explicit lineage hypothesis graph.
5. Mark each `ContinuityMeasurement` with interval ambiguity/complexity or exclude unresolved intervals from the primary exploratory probe by construction.
6. Change empty-snapshot updates so the current snapshot step/time is supplied and disappearance timestamps are correct.
7. Add a frozen sensitivity grid over tracker distance, tracker size ratio, detector radius, detector minimum size, and cadences `{10,30,60}`; persist candidate-level tables.
8. Recompute the technical gate after repair. Do not reinterpret the existing 384 baseline probe rows as validated candidates merely because the current summary says all gates are green.
9. The frozen hold-out may remain a documented diagnostic plan, but any survivors require the repaired lineage audit and direct trajectory/static-flux controls before scientific promotion.

The main agent was sent the critical findings during this run. It must update `RUN_INDEX`, `PROJECT_STATE`, and any gate/hold-out disposition; this auditor did not modify those shared files.

## ENDING GIT STATE

- Branch: `main`
- HEAD at final check: `65af67e716ba157b4eef24ef1b69b589313d03f6`
- Remote state at final check: `origin/main` pointed to the same commit
- Concurrent uncommitted tracked changes at final check, not made or audited by this agent: `edlab/cli.py`, `edlab/entities/detection.py`, `edlab/entities/tracking.py`, `edlab/experiments/audit_candidates.py`, `edlab/experiments/baseline.py`, `edlab/specs.py`, `edlab/substrates/particle_dynamics/engine.py`, `edlab/validation/__init__.py`, `edlab/validation/nulls.py`, `tests/test_continuity.py`, and `tests/test_tracker.py`
- Other untracked file at final check: `docs/agent_journals/2026-07-10/0400_numerical-validation_RUN-20260710-0343-NUM.md`
- This journal was the only file created or modified by this auditor
- Important scope boundary: the verdict applies to the SHA-256-audited snapshot listed above. The concurrent post-audit changes to `tracking.py` and related files were not re-audited in this run.
- Commits created by this auditor: none
- Push performed by this auditor: no

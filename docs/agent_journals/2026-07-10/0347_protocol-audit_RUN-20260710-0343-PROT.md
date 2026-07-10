# Agent Journal — RUN-20260710-0343-PROT

## AGENT / ROLE

Independent scientific protocol auditor / CORE V0 acceptance-test reviewer.

## RUN ID

RUN-20260710-0343-PROT

## START TIME

2026-07-10 03:45:11 +02:00

## END TIME

2026-07-10 03:51:06 +02:00

## STARTING GIT STATE

- Repository: `C:\Users\tommy\Documents\ising v3`
- Branch: `master` (unborn)
- HEAD: none; repository had no commits
- Worktree: dirty because `docs/agent_journals/2026-07-10/0343_main-agent_run-001.md` was already untracked
- Scientific implementation present at inspection time: none visible; `rg --files` returned only the main-agent journal

## ASSIGNED SCOPE

Perform an independent pre-implementation scientific audit of the Emergent Dynamics Lab protocol, limited to:

- false-positive and false-negative risks;
- hidden dependencies between phenotypic continuity `P` and material continuity `M`;
- entity detection and temporal tracking;
- snapshot cadence;
- `STATIC MOTIF WITH MATERIAL FLUX`;
- independent second-path force validation;
- minimum technical kill-switch criteria;
- precise, modest CORE V0 acceptance tests.

Constraints received: do not invent a composite score; do not change the authorized protocol; write only this individual journal and modify no other file.

## ACTIONS PERFORMED

- Read the three supplied protocol attachments.
- Read the main agent's in-progress journal to establish the actual workspace state without treating its scientific claims as reproduced facts.
- Read the testing-strategy skill used to structure this audit as executable acceptance gates.
- Inspected the current file list and Git state.
- Converted the protocol's qualitative validation requirements into explicit, falsifiable CORE V0 acceptance tests.
- Audited the causal path `physical snapshots -> detector -> correspondence/tracker -> P and M`, including selection-induced dependence that is not visible from the formulas alone.
- Did not inspect or validate implementation code because no implementation code existed at the time of this audit.
- Did not execute a scientific experiment and did not reproduce any historical numerical result.

## FILES READ

- `C:\Users\tommy\.codex\attachments\0a71982a-acea-46be-8ebe-1ba772b4cedf\pasted-text.txt`
- `C:\Users\tommy\.codex\attachments\01dd5b79-2f16-4568-80d1-14c54faa59fa\pasted-text.txt`
- `C:\Users\tommy\.codex\attachments\aa16e538-4d58-4d6e-8454-b59fc1bf680c\pasted-text.txt`
- `C:\Users\tommy\Documents\ising v3\docs\agent_journals\2026-07-10\0343_main-agent_run-001.md`
- `C:\Users\tommy\.codex\plugins\cache\claude-cowork\engineering\1.2.0\skills\testing-strategy\SKILL.md`

## FILES CREATED OR MODIFIED

- Created only `docs/agent_journals/2026-07-10/0347_protocol-audit_RUN-20260710-0343-PROT.md`.

No implementation, protocol, state, index, experiment, configuration, or historical-repository file was modified by this agent.

## COMMANDS / EXPERIMENTS EXECUTED

Important read-only commands:

```powershell
rg --files
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short --branch
Get-Content -Raw -Encoding UTF8 <each supplied protocol attachment>
Get-Content -Raw -Encoding UTF8 docs/agent_journals/2026-07-10/0343_main-agent_run-001.md
```

No simulation, force calculation, tracker run, test suite, or historical-baseline reproduction was executed.

## OBSERVED

1. The protocol explicitly requires separate `P(tau)` and `M(tau)`, bans a `theseus_score`, and treats `P > 0.8, M < 0.5` only as an initial visualization/probe.
2. `M` is initially specified as Jaccard overlap of constituent IDs; IDs must remain diagnostic and must not affect physical dynamics.
3. `P` must be constructed from an ID-independent phenotype vector with documented features and normalization.
4. The protocol explicitly requires auditable birth, death, continuity, split, and merge events; periodic-compatible entity detection; tracker/cadence sensitivity; three nulls; and a second force path.
5. The protocol names `{10, 30, 60}` ticks as the historical starting cadence set but requires reasoning in simulated time.
6. The first kill-switch is a technical measurement-validity gate, not evidence that the target phenomenon exists.
7. At audit time there was no implementation to test. Therefore every item below is an acceptance recommendation, not a passed validation.

## INFERRED — PRIORITY FINDINGS

### P0 — The main hidden dependency is the tracker, not the formulas

Computing `P` without IDs and `M` from IDs does not by itself make the measurements operationally independent. Both values are computed only after the detector and tracker decide which entity at `t + tau` corresponds to which entity at `t`.

Two circular failure modes are especially dangerous:

1. If the tracker requires or heavily rewards constituent-ID overlap, it preferentially retains high-`M` links and can make low-`M` continuity undiscoverable by construction. This is a direct false-negative mechanism.
2. If the tracker directly maximizes the final `P` function, it preferentially selects high-`P` correspondences and can manufacture a high-`P` tail. This is a direct false-positive mechanism.

Minimum guardrail: freeze and document tracker association variables before the baseline; the primary association path must not call the final `P` or `M` evaluators as its objective or hard gate. In an unambiguous controlled fixture, replacing all IDs at every snapshot must leave the lineage topology unchanged. Association terms, gates, rejected alternatives, and ambiguity must remain auditable.

This does not assert that `P` and `M` should be statistically uncorrelated. They share detected entity membership and can be physically correlated. The valid requirement is construct separation under controlled interventions, not `r(P,M) = 0`.

### P0 — Validate the two axes by controlled interventions

The kill-switch phrase “`P` and `M` vary” is too weak if assessed only on random simulations. A constant or correlated result can come from the physics, tracker selection, or a broken observable. CORE V0 needs two controlled axes:

- Material-only change: preserve positions, velocities, types, entity geometry, and raw phenotype while replacing a known fraction of IDs. `P` must stay at its identity value while `M` follows the hand-computed Jaccard values.
- Phenotype-only change: preserve the constituent ID set while deforming a documented physical descriptor. `M` must remain `1`; the changed raw descriptor and `P` must respond in the documented direction.

This establishes technical separability without a composite score and without requiring statistical independence in natural trajectories.

### P0 — STATIC MOTIF WITH MATERIAL FLUX must be a passing false-positive null

The null is not supposed to be “rejected” by secretly adding a rescue heuristic. It must deliberately produce a persistent tracked motif with high `P` and low `M`, preferably the exact identity phenotype and disjoint material sets. Passing this null demonstrates that the pipeline correctly exposes the insufficiency of `(P,M)` alone.

Required interpretation: the initial probe may fire, but the run metadata identifies the sample as a null and it is not an empirical discovery. If the tracker breaks the track because IDs changed, or if the pipeline suppresses the quadrant, the null has failed.

### P0 — Detector/tracker validation must include periodic seams and lineage ambiguity

Periodic boundaries create common-mode failures in proximity, centroid, covariance, and compactness calculations. A connected cluster straddling a boundary must remain one entity and have the same raw descriptors as a translated interior copy. Particle storage order and diagnostic ID labels must not change detection.

Split and merge events must be represented as lineage edges, not silently collapsed to a nearest-centroid continuation. For indistinguishable crossing entities, an explicit ambiguity record is scientifically safer than a confident but untraceable identity swap.

### P0 — The second force path must be structurally independent and have analytic oracles

Agreement between two paths is weak evidence if they share pair enumeration, periodic displacement, cutoff logic, or vector accumulation. The paths may share immutable specs, but the optimized path should independently enumerate neighbors and accumulate forces. Pairwise analytic fixtures are still required because two implementations can share the same conceptual sign, index, cutoff, or periodic-image bug.

With an asymmetric interaction matrix, Newton's third law and zero total internal force are not valid generic acceptance criteria. The direction convention `A[type_i, type_j]` must be fixed by explicit asymmetric two-particle tests.

### P1 — Cadence affects observation, never physics

Changing the snapshot schedule must not change the simulated trajectory. At common simulation times, physical states and detections must be identical; only tracker reconstruction may differ. `tau` must be expressed in simulated time, not merely snapshot counts.

The `{10, 30, 60}` cadence grid should be run on an unambiguous known-continuity fixture before empirical use. Detector and tracker scale/gating sensitivity can be tested at documented baseline values and modest predeclared perturbations such as `0.8x`, `1.0x`, and `1.2x`, provided the fixture is constructed with sufficient geometric margin. This is a sensitivity table, not a score.

### P1 — Repeated `(P,M)` rows are not independent samples

Many taus, overlapping windows, or snapshots from the same track are pseudoreplicates. A correlation computed over thousands of rows must not be narrated as thousands of independent confirmations. Reports should retain counts by LawSpec, seed, track, tau, and snapshot cadence, alongside the raw row count. Candidate selection across many laws, taus, trackers, and cadences creates a multiple-search problem; the protocol's frozen hold-out rule is therefore essential.

## FALSE-POSITIVE AND FALSE-NEGATIVE REGISTER

| Risk | Direction | Mechanism | Required control |
|---|---|---|---|
| Tracker optimizes final `P` | False positive | Correspondence selection guarantees phenotypic similarity | Freeze association logic; prohibit direct use of final `P`; log competing edges and ambiguity |
| Look-alike re-identification after a gap | False positive | A new entity is attached to an old track, giving high `P` and low `M` | Gap/crossing fixture; explicit ambiguity; lineage event log |
| Split/merge child silently inherited as continuation | False positive | Low material overlap is created by lineage reassignment | Exact split/merge fixture; retain parent/child edges; flag measurements adjacent to lineage events |
| Static scaffold with particle flow | False positive by design | Morphology persists at a location while matter passes through | Mandatory `STATIC MOTIF WITH MATERIAL FLUX` null that fires the initial probe |
| Periodic centroid/unwrap error | Either | One entity is split, merged, or geometrically distorted at a seam | Boundary-straddling translation-equivalence fixture |
| Data-derived or saturating `P` normalization | Either | Screen data silently calibrate or clip phenotype similarity | Predeclare normalization on fixtures; retain raw descriptors; do not tune after screening |
| Many correlated windows treated as independent | False positive in inference | Pseudoreplication inflates apparent evidence and precision | Group/index by law, seed, track, tau, cadence; hold-out on fresh seeds |
| Tracker requires ID overlap | False negative | Low-`M` continuation cannot survive the association gate | Fresh-ID unambiguous lineage fixture; no hard `M` gate |
| Sparse snapshots | False negative | Displacement or turnover exceeds tracker gate between observations | `{10,30,60}` sensitivity in simulated time; known-continuity fixture |
| Detector radius/min-size threshold | False negative or positive | Stable diffuse motif fragments; bridge points merge motifs | Predeclared detector sensitivity table; threshold convention test |
| Phenotype panel overweights turnover-sensitive count/type features | False negative | Genuine geometric continuity is hidden by feature weighting | Raw feature deltas and one-feature fixtures; no post-hoc reweighting |
| Tau grid misses turnover scale | False negative | Material replacement occurs outside tested lags | Report tau in simulated time and relative to measured turnover time when available |
| Right-censoring at horizon `T` | False negative in narrative | “not observed by T” becomes “impossible” | Preserve censored emergence time and exact observation horizon |
| Shared force bug in both backends | Either | Numerically matching trajectories implement the same wrong force | Analytic pair oracles plus structurally separate enumeration/accumulation |

## PRECISE CORE V0 ACCEPTANCE TESTS

The following suite operationalizes requirements already present in the protocol. It adds no new substrate, transition mechanism, mutation, recycling, fitness, or composite score.

### A. Physics, determinism, and diagnostic-ID invariance

#### CORE-ACC-PHY-001 — Exact replay

Given one frozen `LawSpec`, `WorldSpec`, `RunSpec`, seed, backend, and software environment, execute the same short run twice.

Pass:

- positions, velocities, types, and snapshot times are exactly equal at every saved tick in the same process/environment;
- entity detections and lineage-event logs are identical;
- the persisted manifest records specs, seed, `dt`, tick count, snapshot cadence, boundary conditions, backend, and code revision.

#### CORE-ACC-PHY-002 — Global ID permutation

Create two worlds with identical particle storage order and physical state but a bijective permutation of diagnostic IDs.

Pass:

- force, position, and velocity arrays agree tick by tick to the documented engine tolerance;
- types remain identical;
- only ID-bearing diagnostic outputs change;
- no random draw, sort key, tie-breaker, or force path is keyed by ID.

#### CORE-ACC-PHY-003 — Particle storage-order permutation

Permute particle rows, run both worlds, undo the permutation on output.

Pass: physical states agree to the preregistered float64 tolerance. This catches accidental array-index semantics that an ID-only test can miss.

#### CORE-ACC-PHY-004 — Integrator/boundary smoke oracles

Use one-particle no-interaction cases and a boundary crossing.

Pass:

- no-interaction motion and friction follow the documented update rule exactly;
- periodic wrapping returns the documented interval;
- all states are finite; no NaN/Inf is silently accepted.

### B. Force law and independent backend

#### CORE-ACC-FORCE-001 — Analytic pair table

Evaluate hand-computed two-particle cases covering:

- inside short-range repulsion;
- inside finite-range interaction;
- just below, exactly at, and just above every cutoff using the documented `<`/`<=` convention;
- a pair separated across the periodic seam;
- asymmetric coefficients with `A[a,b] != A[b,a]`;
- coincident or near-coincident positions according to the explicitly documented singularity policy;
- `N = 0` and `N = 1`.

Pass: each per-particle force matches the analytic expectation; outputs are finite. Do not assert momentum conservation for an asymmetric law.

#### CORE-ACC-FORCE-002 — Reference versus second path

On a fixed bank of at least 32 small float64 worlds spanning `N in {2, 3, 8, 32, 64}`, one and multiple types, random asymmetric matrices, seam-adjacent particles, and cutoff-adjacent particles, compare per-particle forces before integration.

Recommended preregistered criterion for float64:

```text
abs(F_fast - F_ref) <= 1e-12 + 1e-10 * abs(F_ref)
```

Pass:

- every component satisfies the criterion;
- one-step states also satisfy the same combined absolute/relative criterion;
- the optimized path does not call the reference pair enumerator or reference vector accumulator;
- failures report the seed, specs, particle state, maximum absolute error, and maximum relative error.

The tolerance must be committed before screening and must not be relaxed after a failing case without a documented numerical reason.

### C. Entity detection

#### CORE-ACC-ENTITY-001 — Periodic seam equivalence

Construct a compact cluster split across opposite sides of the periodic box and an exact globally translated copy away from the seam.

Pass:

- both produce one entity with the same member set modulo the constructed mapping;
- count, type histogram, density, covariance/shape, radial/internal-distance descriptors, and any claimed translation-invariant descriptor agree to their documented tolerance;
- `P` between these copies equals the identity similarity if global translation is claimed invariant.

#### CORE-ACC-ENTITY-002 — Order and ID invariance

Permute particle rows and relabel diagnostic IDs without moving physical particles.

Pass: detected physical partitions are unchanged after undoing the row permutation. The output ordering may differ only if it is explicitly canonicalized and documented.

#### CORE-ACC-ENTITY-003 — Threshold semantics

Place pairs just below, exactly at, and just above the detector radius, plus a documented bridge-chain case.

Pass: results match the declared `<`/`<=` and connected-component/DBSCAN semantics exactly. The bridge behavior is documented as an algorithmic artifact, not physical individuality.

### D. Tracker and lineage

#### CORE-ACC-TRACK-001 — Exact lifecycle fixture

Feed deterministic snapshots containing, in order, birth, unambiguous continuation, split, merge, and disappearance.

Pass:

- the exact event multiset is emitted;
- every split lists one parent and all children;
- every merge lists all parents and one child;
- no split/merge is overwritten by a simple continuation;
- lineage edges are acyclic in forward simulated time;
- no detection is silently assigned to two same-role continuations.

Minimum audit fields per detection/edge:

- tick and simulated time;
- detection ID and stable track/lineage ID;
- member-ID list or lossless reproducible membership reference;
- event type;
- parent and child IDs;
- association terms, gates, and selected/rejected candidate evidence;
- ambiguity flag/reason.

#### CORE-ACC-TRACK-002 — Tracker independence from material labels

Run an unambiguous moving-motif sequence twice: once with persistent IDs, once with fresh disjoint IDs at every snapshot, while all physical snapshots remain identical.

Pass:

- lineage topology and event types are identical;
- `P` values are identical;
- `M` values differ exactly as implied by the constructed ID sets;
- the tracker does not terminate the fresh-ID track.

#### CORE-ACC-TRACK-003 — Look-alike crossing/gap

Construct two similar entities whose feasible association regions overlap after a sparse snapshot or crossing.

Pass: the tracker either preserves the predeclared kinematic association on a resolvable fixture or emits an explicit ambiguity. A silent high-confidence swap fails.

### E. P and M observables

#### CORE-ACC-OBS-001 — Jaccard algebra

For non-empty hand-written sets, test:

```text
M(A, A) = 1
M(A, B_disjoint) = 0
M({1,2,3,4}, {3,4,5,6}) = 2/6 = 1/3
M(A, B) = M(B, A)
```

Pass: exact values are returned. Empty-entity behavior must be explicitly rejected or documented; it must not silently create a valid tracked individual.

#### CORE-ACC-OBS-002 — P invariances and responsiveness

For a frozen entity snapshot:

- compare it with itself;
- permute row order;
- relabel IDs;
- globally translate it across a periodic seam if translation invariance is claimed;
- apply one controlled deformation while preserving IDs.

Pass:

- identity, row permutation, ID relabeling, and every claimed invariance give the documented identity similarity, normally `P = 1`;
- all raw phenotype descriptors are finite and within documented ranges;
- the controlled deformation changes the intended raw descriptor and yields `P < P_identity` by more than the numerical comparison tolerance;
- no invariance not explicitly claimed is silently assumed.

#### CORE-ACC-OBS-003 — Orthogonal construct fixtures

Material axis: compare equal-size entities with the same physical phenotype and material retention fractions `100%`, `50%`, and `0%`. For equal set sizes the expected Jaccards are respectively `1`, `1/3`, and `0`.

Pass: `P` remains at the identity value while `M` equals those exact values.

Phenotype axis: keep the same non-empty ID set while applying the controlled deformation from CORE-ACC-OBS-002.

Pass: `M = 1`, the raw phenotype delta is nonzero, and `P` changes in the documented direction.

This test is the minimum operational meaning of separate, non-trivial `P` and `M`; it does not require their natural-simulation correlation to vanish.

### F. Required nulls and cadence sensitivity

#### CORE-ACC-NULL-001 — ID permutation dynamics null

This is CORE-ACC-PHY-002 persisted as a first-class null artifact with specs, seed, state comparison, tolerance, and summary.

Pass: physical trajectory unchanged; diagnostic identity mapping changed as constructed.

#### CORE-ACC-NULL-002 — STATIC MOTIF WITH MATERIAL FLUX

Construct a deterministic sequence whose detected occupancy, geometry, type histogram, and other declared phenotype descriptors remain fixed while constituents are replaced until the endpoint ID sets are disjoint.

Pass:

- one auditable lineage persists through the sequence;
- raw phenotype descriptors match at endpoints within their declared tolerances;
- endpoint `P > 0.8` (ideally exact identity, if the P definition gives `1` for identical phenotype);
- endpoint `M = 0` and therefore also `M < 0.5`;
- the initial probe fires;
- output metadata marks the case as `STATIC_MOTIF_WITH_MATERIAL_FLUX` / null;
- no report counts it as evidence of dynamic individuality.

This test fails if ID turnover breaks the track, if P/M suppress the expected quadrant, or if an unregistered rescue feature is added solely to hide the false positive.

#### CORE-ACC-NULL-003 — Snapshot cadence is observer-only

Run one frozen physical trajectory while observing at cadences `{10, 30, 60}` ticks. Compare all common snapshot times.

Pass:

- physical states at common times are identical regardless of observation schedule;
- detections and raw descriptors at common times are identical;
- for an unambiguous known-continuity fixture, lineage topology remains the expected one at all three cadences;
- for equal endpoint simulated times, `P` and `M` are identical;
- logs include both ticks and `simulated_time = ticks * dt`.

Then run the same fixture with the small, preregistered tracker/detector sensitivity grid (for example `0.8x`, `1.0x`, `1.2x` for the explicitly chosen scale/gate parameters). Because the fixture is deliberately well inside its valid margins, all cells should retain the known lineage. Empirical candidates need a sensitivity table; a candidate present in only one cell is reported as tracker-sensitive and is not silently promoted as robust.

### G. Artifact-level reproducibility

#### CORE-ACC-ARTIFACT-001 — Re-run from persisted inputs

Starting only from the committed manifest and documented command, reproduce a validation run in a fresh output directory.

Pass:

- the same specs, seed, code revision, backend, `dt`, horizon, snapshot cadence, tracker parameters, and tolerances are recoverable;
- raw state/observable outputs, lineage logs, and summary are indexed;
- deterministic outputs match the original under the declared policy;
- historical agent-reported numbers are absent from `CURRENT OBSERVED` unless their original artifacts were actually re-executed.

## MINIMUM FIRST KILL-SWITCH

This gate answers only: “Is CORE V0 technically capable of measuring separate, non-trivial `P(tau)` and `M(tau)` on auditable lineages?”

`GO` to an independently executed baseline/EXP02 only if every gate below is green:

1. **Dynamics gate:** CORE-ACC-PHY-001 through 004 pass; diagnostic IDs and storage order do not alter physics.
2. **Force gate:** analytic pair table and independent second path pass at the frozen tolerance; periodic and asymmetric cases are included.
3. **Detection gate:** periodic seam, order/ID invariance, and threshold semantics pass.
4. **Lineage gate:** birth/death/continuity/split/merge fixture passes; fresh-ID continuity passes; ambiguity is auditable.
5. **Observable gate:** Jaccard exact cases, P invariances, and both orthogonal construct fixtures pass; raw descriptors are persisted.
6. **Null gate:** all three nulls pass, including the deliberately high-`P`/low-`M` static-flux false positive.
7. **Cadence gate:** observer schedule does not alter physics; the known unambiguous track survives `{10,30,60}` and the predeclared small sensitivity grid.
8. **Artifact gate:** the run can be reproduced from its persisted manifest and indexed outputs.
9. **Baseline non-triviality gate:** the current independently executed CORE baseline contains at least two distinct finite observed values of `P` and at least two distinct finite observed values of `M` beyond the declared numerical comparison tolerance. Report the full joint distribution; do not impose a post-hoc variance threshold.

Any failed gate means `STOP/REPAIR PIPELINE`, not “continue screening and see whether a pretty candidate appears.” No correlation value, candidate count, visual pattern, or high-`P`/low-`M` row can compensate for a failed technical gate.

Conversely, absence of the target quadrant in a valid baseline is a scientific negative result, not a pipeline failure. The static-flux null is expected to occupy that quadrant, so quadrant occupancy alone is not evidence of the target phenomenon.

## DECISIONS MADE

- Interpreted “independent P and M” as controlled construct separability plus freedom from direct tracker optimization on the evaluated metrics, not as statistical zero correlation.
- Treated the static-flux null as a required passing false positive rather than a classifier-rejection test.
- Required analytic force oracles in addition to backend agreement because independence of two implementations cannot remove common conceptual errors.
- Kept sensitivity outputs as a table over cadences/parameters and raw observables; created no composite score.
- Did not propose mutation, neighbor-induced type transition, recycling, a new substrate, a new fitness, or any mechanism outside the authorized CORE V0 protocol.

## HYPOTHESIS

The largest avoidable risk is that a seemingly clean implementation will calculate `P` and `M` in separate modules while still biasing both through tracker correspondence selection. This remains a hypothesis about the future implementation because no code existed to inspect.

## WHAT WOULD FALSIFY THIS?

The tracker-risk hypothesis would be weakened if code inspection and controlled fixtures show that:

- association does not directly optimize or hard-gate on final `P` or `M`;
- lineage is unchanged under fresh disjoint IDs in unambiguous physical sequences;
- the static-flux motif remains one lineage with high P and low M;
- ambiguous crossings are logged rather than silently reassigned;
- candidate behavior is stable under the declared cadence/tracker sensitivity grid.

## FAILURES / DEAD ENDS

- No code-level audit or test execution was possible because the workspace contained no implementation at the time inspected.
- Historical values (`7079`, `r = 0.68`, `0/7079`) were not reproduced and were not used as acceptance evidence.
- No attempt was made to choose final phenotype features or their weights; that would be an implementation/protocol decision beyond this independent pre-implementation audit.

## UNRESOLVED RISKS

- A scalar `P` necessarily combines phenotype information. Even without a banned `theseus_score`, undocumented feature scaling or weights can dominate P. Raw feature vectors and preregistered normalization remain essential.
- The detector definition and tracker association variables are not fixed in the supplied protocol; implementation choices can materially change the discovery space.
- Agreement tolerance depends on numeric dtype and summation order; the recommended float64 tolerance must be validated on controlled fixtures and documented before screening, not tuned against desired results.
- Second-path force agreement does not validate the time integrator; the integrator/boundary smoke oracles remain necessary.
- A valid snapshot phenotype may still miss dynamical individuality; the held-out dynamical-signature path exists for that later question and must not be pulled into CORE V0 fitness.
- Empirical entity-emergence time is censored by the observation horizon; a negative screen must retain the exact horizon and cannot imply impossibility.

## HANDOFF

Highest-priority implementation order for the main agent:

1. Freeze detector/tracker semantics and make association auditable without direct final-`P`/`M` optimization.
2. Implement the tiny analytic fixtures first: Jaccard algebra, phenotype invariances, material-only and phenotype-only axes.
3. Implement the static-flux null before interpreting any naturally occurring high-`P`/low-`M` row.
4. Add periodic-seam detection and exact split/merge lineage fixtures.
5. Validate analytic pair forces, then compare the structurally independent second path at a frozen float64 tolerance.
6. Run the `{10,30,60}` observer-only and tracker-sensitivity controls.
7. Do not launch or interpret EXP02 until every minimum kill-switch gate is green and persisted.

## ENDING GIT STATE

- Branch: `main` (unborn; changed concurrently from the starting `master` branch by another agent)
- HEAD: none; repository still had no commits at the final check
- Worktree: untracked `.gitignore`, `.runtime/`, `docs/`, `edlab/`, and `pyproject.toml`; files other than this journal appeared concurrently and were not created or modified by this auditor
- Commits created by this agent: none
- Push performed by this agent: no
- Only file created by this agent: this journal

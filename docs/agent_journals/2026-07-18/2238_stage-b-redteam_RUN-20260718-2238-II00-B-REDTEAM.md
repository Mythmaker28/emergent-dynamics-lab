# INTERVENTIONAL-INDIVIDUALITY-00 Stage B — independent adversarial review

- Role: independent adversarial reviewer
- Run ID: `RUN-20260718-2238-II00-B-REDTEAM`
- Start: 2026-07-18 22:38:27 +02:00
- End: in progress
- Starting branch: `codex/interventional-individuality-00-stage-b`
- Starting HEAD: `b0dbab7674816ebdf3f3f911694b2744ca4bfc76`
- Starting Git state: clean
- Accepted parent: `b0dbab7674816ebdf3f3f911694b2744ca4bfc76`
- Assigned scope: preregister Stage-B B0/B1 adversarial kill switches before inspecting any new B0 code; later audit B0 implementation, synthetic qualification, frozen B1 manifest, raw-only reproduction, and claim limits read-only; edit only this journal.
- Prohibited during the pre-B0 review: opening or initializing a DEV world; inspecting scientific results; editing implementation, tests, manifests, reports, indexes, or raw data.

## Bound sources read before preregistration

- attached Stage-B mission, SHA-256 `df688ccf78a70aa30e10d2e032dc0bf7556e1583727bf59f690884c2b62b9058`;
- `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, and the accepted-parent durable state/index records;
- Stage-A report, SHA-256 `adabd621438acdf4e0913ccfa0a22839049e022d288019768c88bd15f0241864`;
- Stage-A qualification, SHA-256 `bebd751f43b2a47d1d4a9377bcc98aac508c0d598fad4719f2be4e7f16270a3a`;
- Stage-A field/equation registry, SHA-256 `9b071d0b197732bc7a0f2a418e391ebd2d467ead45e8682987330a1390ded3c6`;
- Stage-A primary and independent red-team journals.

The attached mission accepts `STAGE_A_QUALIFIED` and authorizes B0 passive instrumentation followed, only after B0 qualification and a complete manifest freeze, by one fixed DEV regime map. Stage A qualifies mechanics only. In particular, neither a high-`b` shell nor a face cut is an entity or an autonomy result.

## Review method

1. Freeze the following gates before reading any new Stage-B implementation.
2. Inspect only named Stage-B code, tests, schemas, manifest and reports after the primary agent declares B0 ready.
3. Run deterministic synthetic checks only before B1 authorization.
4. Report any binding defect immediately. B0 passivity, tracker independence, event semantics, or turnover failure compels `REVISE_INSTRUMENTATION`; no DEV world may then be opened.
5. After a valid B1 freeze and execution, independently reproduce classifications from raw shards without importing or running the engine and audit the claim boundary.

## PRE-IMPLEMENTATION FREEZE — 2026-07-18 22:38:27 +02:00

This section was written before inspection of any new B0 implementation or test. Later observations may be appended but these gates and their polarity may not be weakened in response to fixtures or DEV yield.

### KS-B0-01 — measurement passivity

**Required identity.** For every hand-built initial state, LawSpec, boundary configuration, and horizon in the B0 suite, an uninstrumented trajectory and the corresponding fully instrumented trajectory must have byte-identical physical state `(m,n,b,step)` after every update and byte-identical native `StepLedger` serialization. The neutral comparison must start from independently cloned common bytes. Instrument enablement, callback order, logging cadence, output path, and optional diagnostic families may not alter the update count, arithmetic path, exception behavior, or physical serialization.

**Implementation constraints.** Instrumentation may read immutable snapshots or private copies only. It may not retain writable aliases, call a mutating engine path, alter a LawSpec, seed/RNG stream, face plan, timestep, state clock, or native ledger. No diagnostic cache may be read by physics. Logged and unlogged runs must also agree when logging is disabled after construction and when diagnostic order is permuted.

**Kill switch.** Any physical or native-ledger byte mismatch, writable-alias mutation, observer-dependent exception, hidden RNG/time dependence, or observer-to-engine dependency returns `REVISE_INSTRUMENTATION` before B1.

### KS-B0-02 — tracker-independent detection and association

The instantaneous detector is a pure function of one physical snapshot and prospectively frozen detector parameters. It may use declared local cell/face fields and periodic geometry, but not tracker state, diagnostic labels, tracer cohort, turnover score, future frames, regime class, desired candidate yield, causal conductance, intervention response, or face-cut performance. Any threshold is a measurement convention, not a membrane class, and never feeds physics.

The longitudinal tracker consumes immutable detections. Association may use only prospectively declared physical geometry/support/size terms. It may not optimize or hard-gate on tracer overlap, material retention/replacement, activity, throughput, `b` autocorrelation, final regime, or a future success label. All compatible and rejected edges plus individual gate terms must be persisted. Diagnostic IDs are assigned after physical compatibility and never enter dynamics or detection.

**Required invariances.** Permuting component enumeration, diagnostic IDs, dictionary insertion order, and equal-cost input order must leave the unordered physical detection/event graph and final regime classification invariant. Exact ties or many-to-many ambiguity must be logged as unresolved, not broken by labels or iteration order.

**Kill switch.** Detector dependence on tracking, tracking dependence on tracer/outcome/candidate variables, ID-sensitive association, hidden future information, unlogged alternatives, or arbitrary tie resolution returns `REVISE_INSTRUMENTATION`.

### KS-B0-03 — explicit lifecycle graph

The tracker output is an auditable directed bipartite graph between consecutive observation times. Event semantics are fixed by accepted/rejected physical compatibility edges and cannot be overwritten by a single preferred lineage:

- `APPEARANCE`: accepted indegree zero at the new detection;
- `DISSOLUTION`: accepted outdegree zero from the old detection;
- `CONTINUATION`: unique accepted one-to-one edge with no competing accepted edge at either endpoint;
- `SPLIT`: one predecessor has two or more accepted successors and those successors have no other accepted predecessor;
- `MERGE`: two or more predecessors have one accepted successor and those predecessors have no other accepted successor;
- `MANY_TO_MANY_UNRESOLVED`: any remaining accepted many-to-many subgraph;
- `TEMPORARY_CONTACT`: a separately logged proximity/contact relation between detections that remain distinct in the frozen component graph; it creates no ancestry edge and cannot be relabelled as merge merely because supports are adjacent.

If a fixture collapses two components into one instantaneous detection and later re-separates, passive geometry alone does not prove whether this was contact, merge, or alias; absent an independently frozen discriminant it must remain tracking-unresolved. A look-ahead rule may annotate an episode but cannot retroactively manufacture unique one-to-one ancestry.

**Kill switch.** Losing alternative edges, resolving many-to-many graphs into arbitrary lineages, treating proximity as merge, treating temporary detector collapse as known identity, or stale/missing event times returns `REVISE_INSTRUMENTATION`.

### KS-B0-04 — periodic topology and percolation

Boundedness must use the periodic component graph with displacement/winding bookkeeping. A non-contractible cycle with nonzero winding in either lattice axis is `PERCOLATED`, independently of a small wrapped bounding box or centroid. Translation of a fixture across a periodic seam must preserve component count, winding rank, geometry descriptors, event graph, and classification up to the declared coordinate transform.

Temporary adjacency across the seam is governed by the same local detector rule as interior adjacency; no seam-special exception or unwrapped bounding-box heuristic is admissible.

**Kill switch.** Missing a winding component, classifying it as bounded, seam-dependent labels, or using a naive axis-aligned box on wrapped coordinates returns `REVISE_INSTRUMENTATION`.

### KS-B0-05 — passive tracer and exact turnover accounting

The physical engine has Eulerian matter, not microscopic constituent IDs. Therefore exact turnover may be claimed only relative to a declared conserved passive dye/cohort measure. The admissible construction is a non-feedback diagnostic mass decomposition transported using the engine's same pre-step directed gross matter transfers and a frozen well-mixed-source-cell convention. For every cell and step, cohort masses must be nonnegative, their sum must equal physical `m` within an operation-derived tolerance, and global cohort totals must close exactly subject only to explicitly logged sources/sinks (none in the Stage-A matter law). Diagnostic cohort state is never supplied to physics, detection, tracking, or regime selection except through the separately frozen turnover gate.

Net face flux alone is insufficient when simultaneous counterflows exist. Cumulative gross or net boundary crossing is also insufficient to establish replacement because material may exit and re-enter. `COMPLETE_MATERIAL_REPLACEMENT` requires the live amount of the reference cohort inside the tracked support to meet the frozen residual criterion after a declared turnover time while structural persistence and valid tracking continue for the separately frozen survival interval. The raw record must preserve initial cohort mass, live in-support cohort mass, exported/imported cohort mass, all gross directed transfers, support membership, and closure residuals at each sample.

This is exact for the declared passive-mixing model only; it is not a claim about microscopic molecule identity. A tracer implementation that adds physical state, changes capacity, or feeds rates fails passivity.

**Kill switch.** Turnover inferred only from occupancy, low snapshot overlap, cumulative crossing, or net flux; nonconservative dye; negative dye; incomplete gross-flow coverage; tracer-to-physics/detector/tracker feedback; or an unqualified microscopic identity claim returns `REVISE_INSTRUMENTATION`.

### KS-B0-06 — activity, throughput, leakage, and accounting

Diagnostics must expose raw native quantities before aggregation:

- gross directed and net matter/resource transport on every canonical face;
- gross bond formation/rupture, external formation fuel, rupture heat, recycled maintenance work, weakening and dissolution partitions;
- per-component internal-face activity, component-crossing transport, and world totals;
- geometric boundary motion/membership changes separately from physical face flux;
- physical, tracer, and energy/work closure residuals.

Stored bond energy, high `b`, persistence, translation, support jitter, or detector membership churn alone is not activity or throughput. A nonzero candidate activity gate must be a prospectively frozen time-integrated native dynamic rate over a declared interval and cannot be the directly manipulated face-cut response. Leakage across a detector boundary must be computed from raw crossing faces and kept distinct from boundary reclassification work; a static bonded shell is a required non-individual null.

**Kill switch.** Activity derived solely from state stock/variance, throughput conflated with support relabelling, omitted face terms, unclosed work, or use of cut/conductance performance in Stage B classification returns `REVISE_INSTRUMENTATION` (or `MANIPULATION_OR_NUMERICAL_INVALID` if actual Stage-A physical invariants fail during valid DEV execution).

### KS-B0-07 — deterministic classifier

The classifier is a total, versioned pure function of a complete raw diagnostic record and a frozen threshold bundle. It must assign every original world exactly one primary class from the mission vocabulary, with a prospectively declared precedence for simultaneous conditions and explicit reason codes/gate values:

`EMPTY_OR_GAS`, `STATIC_CRYSTAL_OR_SHELL`, `PERCOLATED`, `DISSOLVED`, `ACTIVE_UNBOUNDED`, `PERSISTENT_NO_TURNOVER`, `TURNOVER_WITHOUT_PERSISTENCE`, `TRACKING_UNRESOLVED`, `BOUNDED_ACTIVE_TURNOVER_CANDIDATE`.

`TRACKING_UNRESOLVED` must dominate any candidate claim. `PERCOLATED` or other unbounded geometry must exclude the bounded candidate. Candidate status requires all separately frozen persistence, boundedness/nonpercolation, native activity/throughput, live cohort turnover, post-turnover survival, and valid-tracking gates. A classifier must not silently drop worlds or return a candidate on missing/NaN/nonfinite evidence.

Fixture expectations are fixed before B1 and include every mission fixture. Classification must be byte/order deterministic across repeated runs and raw row permutations after canonical sorting.

**Kill switch.** Partial classification, yield-dependent threshold selection, non-determinism, missing-data optimism, ambiguous precedence, or any candidate emitted despite a failed constituent gate returns `REVISE_INSTRUMENTATION`.

### KS-B0-08 — non-circular candidate gates and scientific separation

Formation/detection, association, turnover, activity, and candidate classification must be modular. A quantity may not both define the target and serve as the sole evidence for the target property. In particular:

- detector thresholds cannot be selected from Stage-B yield;
- tracker scoring cannot include material replacement or final persistence;
- candidate selection cannot use causal conductance, intervention/cut response, boundary closure under a manufactured cut, `b` as declared memory, a visual score, or an entity template;
- `b` dynamics/autocorrelation are ordinary fields only and do not establish memory;
- the original world, not component-time rows or tracks, is the statistical unit;
- a single spectacular world cannot qualify a region.

**Kill switch.** Circular selection, endpoint reuse, pseudoreplicate counts, post-hoc support choice, or candidate-by-visual-inspection invalidates the classifier and returns `REVISE_INSTRUMENTATION` before or invalidates the frozen B1 family after execution.

### KS-B0-09 — required synthetic fixtures

Before any DEV initialization, deterministic hand-built fixtures must independently exercise: stationary component; translating component; deformation without identity switch; split; merge; temporary contact without merge; periodic percolation; dissolution; static bonded shell; active unbounded wave; and complete passive-cohort replacement with structural persistence. Each fixture must assert raw detection/event/flux/tracer records and applicable passivity identities, not only a final label. A fixture assembled by directly providing a desired tracker answer or candidate label is tautological and fails.

The complete-replacement fixture must include an adversarial recirculation case showing why cumulative flux is not replacement. The contact fixture must show the physical discriminant that keeps components distinct; if it instead becomes an observationally indistinguishable detector collapse, expected status is unresolved, not a forced no-merge identity.

**Kill switch.** Missing mission fixture, test-only bypass of production logic, tautological expected graph, or lack of raw assertions returns `REVISE_INSTRUMENTATION`.

### KS-B1-01 — pre-execution DEV manifest freeze

Before the first DEV world is initialized, one canonical machine-readable manifest must bind by SHA-256:

- accepted parent and exact Stage-B code commit plus Python/NumPy/platform environment;
- exact LawSpec family, parameter names, closed ranges, deterministic sampling/mapping rule, and fixed law count;
- both neutral initial-condition families, their complete algorithms/distributions/bounds, deterministic world identifiers, and fixed original-world count;
- namespace, fixed run ordering, horizons, sampling cadence, stopping/censoring rules, and no replacement policy;
- detector, topology, tracker, tracer, activity, leakage and classifier versions, thresholds, tolerances, precedence and missing-data rules;
- prospectively frozen candidate minima, post-turnover survival interval, and region-level reproducibility rule;
- raw schema, atomic publication protocol, required files, canonical serialization, hashes/row counts, completion predicate, and raw-only reproduction command;
- explicit prohibitions on family extension, adaptive optimization, visual selection, organism templates, cuts/conductance endpoints, prospective namespace, and scientific-claim escalation.

The B0 qualification report must already be complete and hash-bound. A manifest that contains placeholders, unfrozen counts, open parameter ranges, optional replacement worlds, or output-contingent horizons does not authorize execution.

**Kill switch.** Any missing binding or any first world initialized before the exact manifest is complete and committed invalidates B1. No world may be replaced.

### KS-B1-02 — no extension, replacement, or adaptive rescue

All scheduled worlds, including ugly, failed, exception, empty, percolated, dissolved and tracking-unresolved worlds, remain enrolled and raw-preserved. A run exception is a failed/censored enrolled world under the frozen rule, not permission for a replacement. Once any world begins, changing a law range, IC distribution, count, horizon, threshold, detector/tracker/classifier, cadence, tolerance, region definition, or software/environment binding burns the family for the stated inference; a revised family requires new human authorization, not an appended DEV tranche.

**Kill switch.** Added worlds, removed failures, retries that change state, adaptive sampling/search/optimization, yield-based stopping, threshold relaxation, or region definition after outcome access invalidates `DEV_REGIME_CANDIDATE` and `DEV_FEASIBILITY_FAIL` alike.

### KS-B1-03 — raw shards and independent raw-only reproduction

Each original world must publish one immutable raw shard by temporary sibling directory plus atomic rename only after all tables and a shard manifest are flushed and hash/size/row-count verified. The raw record must be sufficient to reconstruct every detection, accepted/rejected association edge, lifecycle event, periodic winding result, tracer balance, activity/work diagnostic, individual gate value, class reason, and atlas cell without engine execution or report text.

The independent reproducer may read only the frozen manifest and raw shards. It must not import the physics engine, runner, online detector/tracker/classifier, candidate summary, report, or hand-picked world list. It must recompute classification and region aggregation independently, verify complete enrolled-world identity and hashes, and yield byte-identical machine-readable classifications on at least two clean runs. Disagreement, missing raw evidence, or a reproducer that merely reprints online labels fails the evidence gate.

### KS-B1-04 — candidate regions and world-level inference

The manifest must define a region adjacency/binning rule and a minimum region-level reproducibility criterion before execution. A candidate claim requires at least one predeclared LawSpec region satisfying that rule across independent original worlds and both the applicable frozen sampling/IC support obligations. A single candidate world, multiple tracks from one world, or visually selected neighbourhood is insufficient. The atlas must preserve counts and denominators for all nine regimes in every sampled region and IC class.

### KS-B1-05 — Stage-A invariant escalation

Every DEV shard must retain the Stage-A matter conservation and resource/bond-fuel/heat residuals at the frozen operation-derived tolerance. If a valid DEV state violates positivity, finite-state bounds, conservation, energy/work closure, deterministic replay, or neutral/open mechanics, the disposition is `MANIPULATION_OR_NUMERICAL_INVALID`, not an instrumentation revision or scientific regime result. Instrumentation-only failure remains `REVISE_INSTRUMENTATION`.

### KS-B1-06 — claim limits and allowed dispositions

- `DEV_REGIME_CANDIDATE` means only that at least one predeclared region reproducibly generated bounded, active, persistent, turnover-bearing structures under this DEV manifest. It does not establish individuality, autonomy, memory, ownership, life, reproduction, lineage, causal addressability, natural exclusion, or future Stage-C success.
- `DEV_FEASIBILITY_FAIL` means only that this exact frozen family and horizons produced no qualifying region. It is not a theorem that the substrate can never do so and may not be rescued inside the mission.
- `REVISE_INSTRUMENTATION` means the passive measurement/tracking/turnover/classification stack failed and B1 is unauthorized or invalid.
- `MANIPULATION_OR_NUMERICAL_INVALID` means Stage-A mechanical invariants failed under a valid actual DEV execution.

No positive or negative Stage-B disposition authorizes Stage C automatically. The only next action is human review.

## Initial adversarial hypotheses

### OBSERVED

- Stage A exposes a compact local deterministic engine and native face/work ledgers, but no detector, tracker, material IDs, entity, boundary, memory, or scientific endpoint.
- The Stage-B mission explicitly separates passive measurement qualification from the later frozen DEV map and forbids causal face cuts or conductance endpoints.

### INFERRED

- The largest B0 identifiability risk is calling Eulerian occupancy change or cumulative flux “exact material replacement.” A separate conserved passive cohort model can operationalize turnover, but its well-mixed transport convention and claim limit must be explicit.
- The largest tracking risk is forcing temporary detector collapse or many-to-many compatibility into a unique lineage. An unresolved result is scientifically safer than iteration-order identity.
- The largest topology risk is treating a wrapped bounding box as proof of boundedness; winding must be explicit.

### HYPOTHESIS

A dynamically passive stack can classify deterministic synthetic regimes without adding an entity to physics if detector, event graph, tracer, topology and classifier remain separately frozen pure observers and raw alternatives are preserved.

### WHAT WOULD FALSIFY THIS?

If exact turnover or valid split/merge-aware persistence requires a permanent physical ID, tracker feedback, outcome-tuned component rule, hidden mutable state, or changes to the Stage-A equations, B0 cannot qualify and must return `REVISE_INSTRUMENTATION` (or the substrate program must be stopped under a separately authorized architectural decision).

## Actions after freeze

The primary agent declared the first B0 candidate ready after the pre-implementation freeze. I inspected only:

- `edlab/substrates/lattice_bond/instrumentation.py`;
- the Stage-B exports added to `edlab/substrates/lattice_bond/__init__.py`;
- `tests/test_lattice_bond_instrumentation.py`.

No DEV world was initialized. The focused candidate suite passed `26 passed in 0.18s` using:

```text
C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m pytest -q tests/test_lattice_bond_instrumentation.py
```

I then ran one hand-built, seedless, synthetic counterexample script. It established:

- `max_area_fraction=0.0` and `max_area_fraction=1.0` both returned `BOUNDED_ACTIVE_TURNOVER_CANDIDATE` for the same fabricated track because the declared maximum-area threshold is never represented or read;
- the contact fixture has component counts `(2,1,2)`, emits a resolved `TEMPORARY_CONTACT`, leaves the middle detection unassigned, and reconnects each outer detection to its pre-contact track using the future frame;
- `advance_passive_tracer` accepted a NaN gross-flow array and returned a nonfinite tracer instead of failing closed;
- one synthetic association produced two public edges with `qualified=True`, while the private tracker selected one and rejected the other; `AssociationEdge` has no accepted/selected or reason field.

### First-audit binding defects reported to primary

1. **Boundedness gate absent.** `RegimeThresholds.max_area_fraction` is declared and validated but is absent from `TrackMetrics` and unused by `classify_regime`. A large nonpercolated component can therefore be labelled a bounded candidate.
2. **Future-resolved detector collapse.** The required contact fixture joins two components through occupied bridge cells, so the instantaneous detector observes a genuine `2 -> 1 -> 2` episode. `_contact_matches` then reads `t+1`, suspends both tracks, assigns no track to the middle component, and restores two old identities while calling the episode resolved contact. This violates KS-B0-02/03. A same-frame proximity relation between still-distinct components is admissible; a detector collapse must remain split/merge or unresolved absent an independent physical discriminant.
3. **Accepted/rejected association state not persisted.** `qualified` is only the physical compatibility gate. `_raw_graph_edges` applies an additional selection step, but the returned edge records do not say which qualified edge was accepted or why another was rejected. The event graph is therefore not independently reproducible from the raw edge table.
4. **Tracer does not fail closed on nonfinite flows.** Gross-flow dtype/finiteness and `dt` are not validated. NaNs survive because all min/max comparisons with NaN are false. The raw turnover chain can become nonfinite without raising.
5. **Many-to-many fixture is permissive rather than falsifying.** The named fixture accepts either `TRACKING_UNRESOLVED` or `MERGE`; its actual geometry is a two-to-one merge, not a two-by-two compatibility graph. The mission requires an explicit unresolved many-to-many test.
6. **Replacement/persistence conjunction not exercised.** The structural-persistence assertion uses an unrelated 10x12 detector fixture, while turnover uses a separate 2x2 tracer exchange. No cohort retention is measured within the tracked persistent support, so the required joint fixture is absent.
7. **No auditable raw-to-class path.** Classifier tests directly instantiate `TrackMetrics`/`WorldMetrics`; no production path derives maximum area, turnover chronology, post-turnover survival, activity, missingness and unresolved state from the detector/event/tracer/diagnostic record. Missing/nonfinite values and gate reason codes are also not represented. B0 cannot qualify on fabricated final metrics alone.

These are repairable instrumentation defects; current disposition is `REVISE_INSTRUMENTATION`. The primary agent was instructed not to create a B0 qualification checkpoint or B1 manifest until they are closed.

## Failures and dead ends

- No preregistration failure occurred.
- All 26 submitted fixtures passed, but several expectations were too weak or disconnected to exercise the stated mission gates. Passing the submitted suite therefore does not qualify B0.

## Decisions

Interim decision after first audit: **`REVISE_INSTRUMENTATION`**. No B1 manifest freeze or DEV initialization is admissible until the binding defects above are repaired and independently re-audited.

## Unresolved risks

- A passive tracer can be exact only relative to its declared continuum mixing convention.
- Temporary contact may be observationally indistinguishable from merge if the detector itself collapses the supports.
- A finite closed-resource substrate may show transient throughput only; the future manifest must freeze horizons and post-turnover survival without calling finite transients autonomy.

## Handoff

The primary agent may now implement B0 against the frozen gates. It must obtain B0 qualification and freeze a complete hash-bound B1 manifest before any DEV initialization.

## B0 repair and final re-audit

The primary agent repaired every first-audit defect and two additional counterexamples found during re-audit. I inspected each exact repair and reran only the authorized focused synthetic suites. No DEV world or result namespace was opened.

### Repair closure against the seven first-audit findings

1. **Boundedness:** closed. `TrackMetrics` now carries `maximum_area_fraction`; the raw assembler exact-checks the reported area fraction against `DetectedComponent.area/(H*W)` and the candidate gate enforces both the maximum-area and bounded-fraction limits.
2. **Contact/collapse:** closed. A detector-level `many-to-one-to-many` collapse is now propagated as `TRACKING_UNRESOLVED` on both adjacent transitions. No old track ID is carried through the collapsed detection. `TEMPORARY_CONTACT` is only a same-frame proximity annotation between two still-distinct detections at periodic Manhattan support distance two and creates no ancestry edge.
3. **Association auditability:** closed. Every physical candidate edge stores the individual numeric gate terms, qualification/rejection reason, selected boolean, and selection reason. Qualified unselected exact ties form an explicit ambiguity graph and force an unresolved event; lower-scoring alternatives to an already selected edge remain separately labelled.
4. **Tracer fail-closed behavior:** closed. Tracer, pre-matter and post-matter must be finite float64 fields of exactly identical shape; directed gross flows must be finite nonnegative float64 arrays of the exact face shape; `dt` must be finite positive; and pre/post matter must reproduce from the supplied gross flows before dye advection is accepted.
5. **Many-to-many:** closed. A strict hand-built two-horizontal to two-vertical support fixture produces four raw-overlap edges and must return only `TRACKING_UNRESOLVED`, never split or merge.
6. **Replacement plus persistence:** closed. One common 7x7 synthetic construction retains the same detected support/track while a balanced four-face gross swap removes the complete enrolled cohort from that support; reversing the same gross swap returns the cohort and proves that cumulative traffic cannot be the turnover estimator.
7. **Raw-to-class path:** closed. `assemble_world_metrics` binds each observation to a tracker point and detected component, rejects duplicates and orphan observations, exact-checks area and percolation, fail-closes missing/nonfinite/invalid inputs, computes first-turnover chronology and post-turnover observation count, and emits reason-coded track/world metrics consumed by the deterministic classifier.

### Additional counterexamples found and closed

- **Geometry spoof:** a winding detected component could initially be supplied as `percolated=False` and become a bounded candidate. Area/percolation are now exact-checked against the detector; the same counterexample returns `TRACKING_UNRESOLVED` with `PERCOLATION_GEOMETRY_MISMATCH`.
- **Finite invalid row:** with 13 observations, one invalid area row could be dropped while 12 remaining rows still produced a candidate. Every measurement-integrity reason now makes the track and world unresolved.
- **Orphan observation:** extra observations outside tracker points now fail closed.
- **Qualified exact tie:** a symmetric two-source/two-target geometry with four equal qualified scores initially became resolved dissolution plus appearance. The ambiguity graph now yields a false-resolved `TRACKING_UNRESOLVED` event and marks affected tracks unresolved.
- **Nonfinite tracker margin:** `NaN` and both infinities are rejected.
- **Broadcast shape:** a `(1,W)` post-matter field can no longer broadcast against `(H,W)` tracer/pre-matter.

### Independent exact evidence

Authorized final focused command:

```text
C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m pytest -q tests/test_lattice_bond.py tests/test_lattice_bond_instrumentation.py
```

Result on the final reviewed B0 code: **56 passed in 0.41s**. `py_compile` passed for `instrumentation.py`; `git diff --check` passed.

Independent hand-built checks, not copied from the submitted suite:

- all 4,096 binary supports on a 3x4 periodic lattice preserved detector component-area and winding signatures under three translations and reflection;
- 3,072 actual-engine tracer advances covering all 256 binary 2x2 `m/n` corner patterns, four uniform `b` values, and three cohort fractions stayed conserved and within `0<=q<=m`, with worst observed violation/residual `2.220446049250313e-16`;
- reversing component enumeration preserved the unordered physical event graph and edge records;
- the exact-tie and detector-collapse counterexamples now both return unresolved;
- all accepted-parent allowlist hashes, including the Stage-A engine and tests, match exactly.

Final reviewed B0 code hashes:

- `edlab/substrates/lattice_bond/instrumentation.py`: `f40c0817acaad99c881e47ca16a7059164735a37ab15f134f11d1d69c6fd6c88`;
- `edlab/substrates/lattice_bond/__init__.py`: `245ccce882e669c37782cf930bcfc076ff53daf8575db27246885b5ace0a3e95`;
- `tests/test_lattice_bond_instrumentation.py`: `d0d49e6f88d9b7faa5e4af3da33dd1f4a59d5575dfc97ddaf2e69a7af233c22b`.

### B0 claim audit

- Instrumentation is dynamically passive and the engine does not import it.
- Detector and tracker contain no tracer, throughput, `b`, conductance, cut, intervention, candidate-yield, memory, genome, fitness, reproduction, or permanent physical-ID input.
- Turnover is exact only for the declared well-mixed passive continuum cohort; no microscopic material-identity claim is permitted.
- A same-frame proximity annotation is not proof of entity identity. A detector collapse remains unresolved.
- Static shell, activity, throughput, persistence, turnover, or `b` dynamics alone establish no individuality, autonomy, memory, ownership, reproduction, or life.
- B0 contains no regime result. It authorizes only the preparation and human-audited freeze of the B1 manifest.

### Constraints carried into B1 manifest review

- The B1 runner and independent reproducer must use the admitted raw-to-metrics assembler path; fabricated summary metrics are not admissible evidence.
- The manifest must state exactly which raw internal-activity and incident energetic-work fields populate each normalized `TrackObservation`; boundary crossing/support relabelling may not masquerade as internal activity.
- Every detector, tracker, tracer, classifier, tolerance, threshold, horizon, IC, LawSpec, world count, region rule, namespace, environment and atomic raw schema binding must be complete and hash-bound before the first world.
- The placeholder independent raw-reproduction journal path in the current source allowlist must be replaced with an exact path before the B1 manifest is sealed.
- The B0 report's synthetic count must be updated from its stale draft value to the final 56 before checkpointing.

### Final B0 decision

The earlier interim `REVISE_INSTRUMENTATION` is superseded by the reviewed repairs.

**`PASS_B0_FOR_MANIFEST_FREEZE`**

This is not a Stage-B scientific disposition and does not by itself authorize DEV initialization. It authorizes only completion and independent review of one exact B1 manifest. No world may start until that manifest is committed, hash-bound, extension-free, and explicitly accepted against KS-B1-01 through KS-B1-06.

## B1 pre-manifest runner audit

After the B0 checkpoint `93f4a42d8972d2d4b9f8da6f1dc3c8161dc3c045` was committed and pushed, the primary agent requested a static audit of the draft runner, runner tests, raw schema and exact source-allowlist change. I inspected only those named files. I did not call `build_initial_state`, `run_world`, `run_family`, or any DEV initializer.

### Positive static observations

- World enumeration is deterministic, explicit and Cartesian over laws, both IC classes and fixed replicate indices; world IDs include all three coordinates.
- The initializer uses a stateless SHA-256 coordinate map rather than mutable RNG state and contains no organism template, genome, fitness, adaptive search, cut, intervention, memory writer or visual input.
- Each physical step is replayed from the same state, compared byte-for-byte, and compared to the scalar reference backend. Neutral intervention scales and all missing-flux/controller-onset fields are checked.
- Physics raw includes all `H+1` states, all `H` complete `StepLedger` records, reference errors and replay flags. That is sufficient in principle for an engine-free detector/tracker/tracer/classifier reproduction.
- Track observations derive activity from internal matter transport and energy throughput from internal bond formation/rupture work; boundary crossing is not used as internal activity.
- The online classifier operates on original-world rows, and a law region needs the frozen minimum in each of the two IC classes.
- A pre-existing final or partial family root is refused and no enrolled failure is replaced.

### Binding defects reported before checkpoint

1. **Optional/incomplete manifest seal.** `manifest_sha256_excluding_field` was accepted when missing or empty. The validator did not require a closed required source-hash set, canonical file bytes, repository path confinement, exact environment binding, positive integer horizon/shape/replicates, valid IC ranges, region minimum, finite LawSpecs or complete detector/tracker/classifier validation.
2. **Physical invalidity could be reclassified as instrumentation.** `result.state.validate(spec)` could raise outside the `NumericalInvalid` type and be caught by the broad world exception as `INSTRUMENTATION_INVALID`. Nonfinite ledger/reference fields could also evade `>` comparisons because NaN comparisons are false.
3. **Atomicity claim exceeded implementation.** The schema promised fsync/close/verification before rename, but JSON/NPZ writers closed and hashed without an explicit file fsync or a documented Windows directory-durability boundary.
4. **Root/raw completion underbound.** A complete shard manifest lacked the promised row counts. The root manifest bound only the classification file, not enrollment nor the exact list/hash/size/status of every enrolled shard manifest, raw schema and runtime manifest.
5. **Failure-family schema contradiction.** The raw schema defined completion as every shard status `COMPLETE`, while the runner intentionally publishes terminal `NUMERICAL_INVALID` or `INSTRUMENTATION_INVALID` shards to support the two fail dispositions.
6. **Family row validation absent.** `classify_family` assumed exact unique enrolled rows and known statuses/regimes. A duplicate, extra, missing or inconsistent candidate/status row could affect denominators or hide a failure if supplied by reconstruction.
7. **Qualification gaps.** The eight draft runner utility tests did not exercise fail-closed manifest validation, nonfinite/reference escalation, exact row identity, duplicate/extra rejection, root/shard binding or atomic/no-retry helpers.

Interim B1 runner disposition: **REVISE STATIC RUNNER — NO MANIFEST SEAL — NO DEV INITIALIZATION**.

## B1 repaired-runner re-audit

The primary agent repaired the first seven static-runner defects. I re-read the repaired `stage_b.py`, runner tests, raw schema, and source allowlist. I still did not call `build_initial_state`, `run_world`, `run_family`, or initialize a DEV world.

Focused static qualification on the repaired draft used the accepted parent environment:

```text
C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m py_compile edlab/substrates/lattice_bond/stage_b.py tests/test_lattice_bond_stage_b.py
C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m pytest -q tests/test_lattice_bond.py tests/test_lattice_bond_instrumentation.py tests/test_lattice_bond_stage_b.py
```

Result: `py_compile` passed and **70 passed in 0.41s**.

### Repaired obligations now closed

- The canonical manifest seal is mandatory and validated before source access.
- The source-hash keyset is exact and repository-confined; environment binding is exact.
- Structural values now receive substantially stronger finite/range/type validation.
- Nonfinite runtime states, ledgers, and scalar/vector comparisons fail closed.
- Physical invariant failures inside an update escalate as `NumericalInvalid`.
- JSON and NPZ files are flushed before rename; the Windows directory-fsync limitation is stated precisely.
- Terminal publication completion is distinct from scientific eligibility.
- Enrollment, classification, raw-schema hash, and every shard-manifest hash/size/status are bound by the root manifest.
- Family row validation rejects duplicates, omissions, extras, coordinate relabelling, unknown statuses/classes, malformed candidate IDs, and failed-world reclassification.

### Three remaining binding counterexamples

1. **The root verifier can bless a malformed complete shard.** I constructed all 12 expected synthetic shard directories with canonical shard manifests but deliberately used schema `WRONG`, a `physics.npz` containing the literal bytes `not-an-npz`, an invented object-typed `physics_inventory`, and `row_counts={"state_rows":-1}`. `_verify_partial_root` accepted all 12. It checks file hashes and the presence of a row-count object, but it does not validate the exact shard schema, reopen the NPZ with `allow_pickle=False`, recompute/compare the promised inventory, enforce the frozen array names/shapes/dtypes/horizon/lattice shape/finiteness, parse and exact-check `online.json`, or recompute the measurement counts. A bad writer implementation could therefore produce a root package that claims the raw-schema obligations while binding internally consistent hashes to structurally invalid evidence. The verifier must perform these checks before the family-root rename. Failed shards should likewise exact-check their schema and failure record status/identity.

2. **Initializer and law/IC admissibility are not frozen strongly enough.** `validate_manifest_structure` accepted the structural test manifest with the entire `initializer` object absent. It also accepted a law with `m_max=0.3`, `n_max=0.5` while the enrolled soup/compact IC ranges reach `m=0.6/0.9` and `n=0.9`. Thus an enrolled initial state can violate the exact law's admissible domain. `build_initial_state` validates the state before `run_world` enters its numerical-error `try`; the resulting `AdmissibilityError` is caught by the family-wide broad exception and mislabeled `INSTRUMENTATION_INVALID` rather than `MANIPULATION_OR_NUMERICAL_INVALID`. Require and freeze the exact fresh initializer namespace; validate every IC envelope against every enrolled law's `m_max/n_max`; bind the exact law-family sampling rule and ranges in the eventual manifest; and convert any residual initializer admissibility failure to `NumericalInvalid`.

3. **The scalar-reference audit ignores the physical clock.** I took one hand-built 2x2 synthetic step result, changed only the reference result state's `step` by `+7`, and `_reference_error` returned `0.0`. Arrays and the complete ledger are checked, but `state.step` is not. The frozen update includes the clock, and raw `state_step` is a required field, so the reference comparison must require exact step equality.

These are source-structural defects, not preferred-sign or scientific-result findings. The exact counterexample outputs were:

```text
malformed_shards_accepted=12
incompatible_ic_manifest_accepted=True initializer_present=False
wrong_reference_step_error=0.0
```

### Re-audit disposition

**REVISE STATIC RUNNER — NO MANIFEST SEAL — NO DEV INITIALIZATION.**

The three defects are repairable. After repair, the exact final source hashes, source allowlist, raw reproducer and manifest must be re-audited before the first DEV world. The passing 70-test suite does not supersede the explicit counterexamples.

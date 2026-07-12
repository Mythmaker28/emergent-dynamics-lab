# Decision Log

## D-001 — Autonomous repository instead of migration

**Date:** 2026-07-10  
**Decision:** Create a clean private `Mythmaker28/emergent-dynamics-lab` history. Treat `ising-life-lab` and local `9992e6c` as read-only reference.  
**Reason:** Preserve provenance and prevent legacy multi-domain claims or artefacts from silently entering the new protocol.

## D-002 — Exact 30-minute native heartbeat

**Date:** 2026-07-10  
**Decision:** Use native Codex heartbeat `Emergent Dynamics Lab Autonomous Research` at 30-minute recurrence, not the obsolete one-hour line and not a custom daemon.  
**Reason:** Explicit user correction and native sub-hour continuation support.

## D-003 — Conservative explicit overlap lock

**Date:** 2026-07-10  
**Decision:** Use an atomic JSON lock that is never cleared by age alone and can only be released by its run ID.  
**Reason:** Native heartbeat overlap is not documented as a hard guarantee; experiments may legitimately exceed 30 minutes.

## D-004 — Tracker association is separate from evaluated P and M

**Date:** 2026-07-10  
**Decision:** Associate detections using periodic centroid distance and size ratio only. IDs/Jaccard M and final phenotype P are forbidden from association gates. Log all alternatives and explicit ambiguity.  
**Reason:** Avoid manufacturing high P or suppressing low M through correspondence selection; preserve orthogonal falsification fixtures.

## D-005 — Fixed dimensionless phenotype normalization

**Date:** 2026-07-10  
**Decision:** Use committed physical normalization scales rather than z-scoring and recalibrating P separately for each run.  
**Reason:** Historical per-run calibration made cross-run comparability uncertain.

## D-006 — Halton screening sampler

**Date:** 2026-07-10  
**Decision:** Use a deterministic Halton low-discrepancy sequence (skip 32) for the current baseline and eligible EXP02 sampling.  
**Reason:** It is a justified quasi-random design with no SciPy dependency and fully deterministic mapping to LawSpec.

## D-007 — Frozen same-endpoint, cross-cadence fresh-seed gate

**Date:** 2026-07-10

**Decision:** Hold out laws 1, 3, 6, and 10 using the exact rule in `docs/experiments/HOLDOUT_COREV0_01_PROTOCOL.md`, then retain only laws qualifying in at least two of five fresh seeds.

**Reason:** The baseline probe is populated but heavily pseudoreplicated and partly lineage-complex. Requiring clean long tracks, identical physical endpoints under multiple cadences, multiple screening seeds, and fresh-seed survival tests robustness without changing P/M thresholds. The count is not a probability estimate.

## D-008 — Stop hold-out and supersede candidate interpretation after independent audits

**Date:** 2026-07-10

**Decision:** Do not execute `HOLDOUT-COREV0-20260710-001`. Preserve baseline 001 as a technical exploratory artefact, but supersede its candidate selection. Repair numerical domain checks and lineage auditability, then run a new baseline under a new experiment ID.

**Reason:** Independent audits found (a) vector norm underflow for subnormal separations, (b) a non-unique periodic direction when reach meets half the box, (c) non-finite specs accepted, (d) compatibility alternatives mislabeled as split/merge, (e) stale disappearance timestamps, (f) incomplete candidate-edge persistence, and (g) a sparse look-alike exchange that yields clean `P=1,M=0` without a competing spatial edge. Proceeding would turn a known measurement failure into a narrative candidate.

**Repair:** Use scale-stable `hypot`; require all relevant reaches below half the box; reject non-finite specs; validate forces and one-step states; distinguish unique split/merge from many-to-many ambiguity; persist every accepted/rejected association edge; flag complex measurement intervals; extend tracker/detector sensitivity; keep the sparse alias as an explicit live unresolved null.

**Interpretation boundary:** A repaired diagnostic hold-out may later test reproducibility, but no survivor can be promoted scientifically without direct trajectory audit and an intervention that rejects static occupancy/look-alike flux.

## D-009 — Normalize pair direction before multiplying force magnitude

**Date:** 2026-07-10

**Decision:** In the scalar reference path, compute `magnitude*(dx/distance)` rather than `magnitude*dx/distance`.

**Reason:** Exact-SHA re-audit showed that `hypot` fixed distance underflow but the old multiplication order still quantized subnormal displacements, first failing at `1e-315` and reaching a 0.3 force error at the smallest positive float64. The new order agrees with the vector path across the full tested subnormal range and preserves the same nominal formula.

## D-010 — Invalidate hold-out 002 after clean-cadence join bug

**Date:** 2026-07-10

**Decision:** Preserve but invalidate `HOLDOUT-COREV0-20260710-002`. Correct the audit so every cadence contributing to same-endpoint consistency must itself be a clean long track. Freeze hold-out 003 with law 3 only and five unseen seeds.

**Reason:** The old join counted all probe-positive cadences first, then applied cleanliness only to the current row. This could label an endpoint cross-cadence-consistent when the corroborating cadence was complex. The corrected baseline rule selects law 3 only. Reusing results for the other laws or keeping the old selection would be post-hoc narrative rescue.

## D-011 — Reject baseline law 3 and advance to broad EXP02

**Date:** 2026-07-10

**Decision:** Reject law 3 for perturbation preparation because only one of five unseen seeds passes the frozen corrected gate, below the required two. Start no alternative baseline-law hold-out; proceed to the 300-law EXP02 regime map after implementing streaming storage.

**Reason:** Substituting another law from invalidated hold-out 002 or relaxing cross-cadence cleanliness would be post-hoc rescue. A negative 12-law path does not justify changing substrate because EXP02 and EXP03-A/B/C remain required.

## D-012 — Immutable run shards and last-published COMPLETE manifest for EXP02

**Date:** 2026-07-10

**Decision:** Store each `(law_index, seed)` as one immutable directory containing the four unchanged CSV tables and a per-run manifest. Publish that directory by same-parent atomic rename only after files and manifest are flushed. Quarantine any unpublished temporary directory after an interrupted process. Publish derived outputs atomically and `manifest.json` last with `status=COMPLETE` only after all 900 planned shards, row counts, indexes, hashes, and derived outputs verify.

**Reason:** Run-level shards bound memory to one simulation, make completed work independently verifiable, and avoid ambiguous append/truncate recovery. The projected few thousand local files are acceptable relative to the stronger fail-closed semantics. Byte-equivalence fixtures confirm that storage changed without changing trajectories, detection, tracking, P, or M.

**Falsification / rollback:** Any partial final shard, duplicate/lost run, accepted corruption, row/index inconsistency, premature `COMPLETE` manifest, or non-idempotent resume blocks EXP02. A real subprocess exit is injected after shard fsync and before publication to exercise this boundary on Windows.

## D-013 — Canonical lag keys use integer step deltas, not float equality

**Date:** 2026-07-10

**Decision:** Group all downstream cadence/lag analysis by `(snapshot_cadence, end_step-start_step)` and derive `lag_snapshots` and displayed `tau` from the integer step delta and frozen `dt`. Preserve the original EXP02 `measurement_aggregates.csv` and explicitly mark its float-string fragmentation; generate a separate corrected aggregate rather than silently rewriting the parent artefact.

**Reason:** Independent statistical QA found that mathematically identical `tau` values had multiple binary float strings, fragmenting 7,280 logical groups into 36,937 rows. Raw start/end steps, all row totals, P/M values, hashes, and scientific trajectories remain intact, so a raw rerun is neither necessary nor justified.

**Falsification:** Corrected integer-delta groups must reproduce all 648,740 rows, exactly nine global cadence/lag cells, and the independent per-cell counts. Any mismatch invalidates the corrected analysis.

## D-014 — Freeze all nine EXP02-eligible laws for one five-seed diagnostic hold-out

**Date:** 2026-07-10

**Decision:** Run laws `{0,12,35,52,73,94,209,225,298}` on unseen seeds `{3001,3002,3003,3004,3005}` with unchanged CORE V0 settings and the corrected whole-track-clean, same-endpoint cross-cadence gate. Retain a law only at `>=2/5` fresh seeds. Include all nine eligible laws; do not rank or filter them by raw probe rate or observational motion metrics.

**Reason:** Each law passed the frozen EXP02 `>=2/3` screening permission gate. Direct diagnostics reproduce P/M exactly and show no hidden compatible edge, but cannot reject static occupancy/look-alike alias. A common fresh-seed gate tests recurrence without narratively selecting attractive examples.

**Interpretation boundary:** Survival is diagnostic only and authorizes an intervention design; it is not a probability estimate or evidence of individuality. Failure is negative and cannot be rescued by a replacement law or relaxed threshold.

## D-015 — Freeze HOLDOUT04 survivors `{0,52}` for alias-rejecting intervention design

**Date:** 2026-07-10

**Decision:** Retain only laws `{0,52}` for `ALIAS-INTERVENTION-COREV0-20260710-001`. Law 0 qualifies in fresh seeds `{3002,3004}` and law 52 in `{3001,3003}` under the preregistered `>=2/5` gate. Reject laws `{12,35,73,94,209,225,298}` without replacement. Require an exact sham and a causal endpoint that can reject stationary spatial occupancy or sparse look-alike flux before any perturbation-recovery interpretation.

**Reason:** The 45-run hold-out used unseen seeds and unchanged thresholds, observer settings, tracker logic, laws, and simulation horizon. Recurrence passed for two laws, but every qualifying row still carries the mandatory alias null. Freezing the survivor set now prevents post-hoc ranking by motion, probe abundance, or visual appeal.

**Interpretation boundary:** `2/5` is a diagnostic recurrence gate, not a probability estimate. Laws 0 and 52 are not promoted scientific candidates by this decision. Any intervention implementation must preserve diagnostic-ID independence, keep P and M separate, and pass no-op/sham plus validated-reference controls before execution.

## D-016 — Correct the ALIAS-INTERVENTION readout to follow the displaced set and use robust re-establishment

**Date:** 2026-07-10 (RUN-20260710-1801-ALIASINT-FABLE5, Fable 5)

**Decision:** Before committing any causal result, self-review found two readout bugs in the first harness
implementation (both in derived measurement only; physics, enrollment, branches, and the frozen protocol design
were unaffected): (a) the PLACEBO branch followed the candidate constituents `C`, but in the placebo branch `C`
is not displaced (a matched non-candidate clump `C'` is), so placebo persistence wrongly measured the in-place
candidate; (b) `carrier_persist_consecutive` counted from the first post snapshot and was reset to zero by the
brief, expected post-displacement transient dip. Corrected: each branch follows the set it actually displaced
(candidate for control/sham/perturbed; `C'` for placebo), measured against that set's own reference phenotype
and its own origin/home site, with a robust late-window re-establishment metric. This makes the implementation
faithful to the already-frozen protocol decision rule (baf1fca §8–9: "PERTURBED must exceed PLACEBO; old site
does not regenerate"). Additionally, genuine "individuality under constituent turnover" is scored only when the
displaced candidate re-establishes phenotype **while** its material retention is not ~1.0 (a rigid cohesive
cluster translating with M→1.0 is trivial translation-covariance, not the target phenomenon).

**Reason:** The uncorrected placebo comparison was meaningless and the consecutive metric was fragile; both were
caught in self-review before any results were committed (no committed artefact is invalidated). The correction is
more conservative and matches the frozen preregistration, in the spirit of D-010/D-013.

**Falsification:** the corrected harness must still pass every validation gate (sham==control bit-for-bit,
conservation, off-site displacement, IDs-not-in-physics, determinism, HOLDOUT04 reproduction): 46/46 tests pass.

## D-017 — Close CORE V0 survivors {0,52} after alias-intervention (CASE A); advance to EXP03-A

**Date:** 2026-07-10 (RUN-20260710-1801-ALIASINT-FABLE5, Fable 5)

**Decision:** ALIAS-INTERVENTION-COREV0-20260710-001 executed the frozen same-state matched-branch displacement
test on fresh causal seeds 5001-5040 per law. Enrolled 5 (law 0) and 9 (law 52) first-eligible-endpoint units;
all sham branches equalled control bit-for-bit; no non-informative or catastrophic interventions. Genuine
constituent-turnover individuality (displaced candidate re-establishes at the new site, exceeds a displaced
non-candidate placebo, old site does not regenerate, material retention below the turnover threshold) occurred in
0/5 and 0/9 units. Three law-52 units re-established only as rigid cohesive clusters (M~1.0, no turnover) and did
not reach the majority bar. Per the frozen decision rule this is CASE A: close laws 0 and 52 as CORE V0
candidates and proceed to EXP03-A.

**Reason:** The stationary-occupancy / sparse look-alike alias is not rejected across a majority of enrolled fresh
seeds. High P under low M in CORE V0 is not shown to reflect constituent-carried dynamical individuality. No
threshold was lowered; a negative result stays negative.

**Falsification / reopen:** A CORE V0 law whose displaced candidate re-establishes with genuine turnover,
exceeding placebo, no old-site regeneration, clean alias audit, across a majority of fresh seeds, would reopen
the question. None observed.

## D-018 — EXP03-A (density preference) screen NEGATIVE; advance to EXP03-B

**Date:** 2026-07-10 (RUN-20260710-1850-EXP03A). Model: claude-opus-4-8 (Fable 5 lock explicitly lifted by user).

**Decision:** The preregistered EXP03-A screen (protocol @3406ef0; isolated comfortable-neighbour density mechanism,
neutral limit = CORE V0 bit-for-bit) ran matched OFF/ON on 64 Halton laws x 3 seeds x 3 cadences. The OFF arm
reproduces CORE V0 (descriptive r(P,M)=0.7328; permits {17,52}, incl. known survivor 52). Under ON, density
preference lowered mean P (-0.064) and mean M (-0.042), reduced long tracks (2293->2042), raised censoring
(15227->20511), and yielded **0 screening-permitted laws vs 2 for CORE V0**. Density preference did not enrich the
high-P/low-M regime; it depleted it. Per the frozen decision rule this is EXP03-A SCREEN NEGATIVE. Advance to
EXP03-B (CORE V0 + orbital/transverse interaction only). No fresh-seed hold-out triggered; thresholds unchanged;
no composite; laws 0/52 not reopened (their appearance is only the OFF=CORE V0 control).

**Reason:** Falsifier F1 confirmed (ON did not increase the eligible-law count over OFF). The mechanism's net
effect is homeostatic settling / reduced coherent persistence, consistent with PASS B, not turnover-individuality.

**Falsification / reopen:** A pre-declared (not post-hoc) density parameterisation under which ON yields more
screening-permitted laws than OFF with genuine turnover would reopen EXP03-A. Not observed.

## D-019 — EXP03-B (orbital interaction) screen NEGATIVE; advance to EXP03-C

**Date:** 2026-07-10 (RUN-20260710-1930-EXP03B). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The preregistered EXP03-B screen (protocol @a788500; isolated transverse/orbital pair force,
neutral limit = CORE V0 bit-for-bit, momentum conserved) ran matched OFF/ON on 64 laws x 3 seeds x 3 cadences.
OFF reproduces CORE V0 (r=0.7328, permits {17,52}, |circ|=0.103). ON injected circulation (|circ|->0.640) and
drove pervasive mixing (mean M 0.836->0.324, long tracks 2293->563, censoring 15227->47048); the RAW probe
fraction rose (0.0163->0.0239) but the frozen clean-long cross-cadence gate yielded **0 screening-permitted laws
vs 2 OFF**. Orbital alone does not enrich the robust candidate regime; the raw probe increase is the low-M
look-alike regime the gate rejects (PASS B). Per the frozen rule this is EXP03-B SCREEN NEGATIVE. Advance to
EXP03-C (CORE V0 + density + orbital). No hold-out; thresholds unchanged; no composite; laws 0/52 not reopened.

**Reason:** Falsifier F1 confirmed (ON permitted 0 < OFF 2); F2 relevant (raw probe rise explained by
mixing/circulation, not turnover-individuality).

**Falsification / reopen:** A pre-declared orbital parameterisation under which ON yields more screening-permitted
laws than OFF with robust turnover would reopen EXP03-B. Not observed.

## D-020 — EXP03-C (density+orbital) screen NEGATIVE; Particle Dynamics ladder exhausted, substrate decision due

**Date:** 2026-07-10 (RUN-20260710-1945-EXP03C). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The preregistered EXP03-C screen (protocol @ed06075; combined validated density + orbital
mechanisms; neutral limit both strengths 0 = CORE V0 bit-for-bit; partial limits recover EXP03-A/B) ran matched
OFF/ON on 64 laws x 3 seeds x 3 cadences. OFF reproduces CORE V0 (r=0.7328, permits {17,52}). ON injected the most
circulation of the ladder (|circ| 0.103->1.012) yet lowered P (0.853->0.588), lowered M (0.836->0.427), collapsed
long tracks (2293->513), and REDUCED the raw probe fraction (0.0163->0.0059), yielding **0 screening-permitted
laws vs 2 OFF**. The D-019 hypothesis that density homeostasis would bound orbital mixing to yield candidates is
falsified. Per the frozen rule EXP03-C is SCREEN NEGATIVE.

**Ladder outcome:** CORE V0 (CASE A, D-017), EXP03-A density (NEGATIVE, D-018), EXP03-B orbital (NEGATIVE, D-019),
EXP03-C combined (NEGATIVE, this). Across the full preregistered Particle Dynamics causal ladder, no law family
produced audited constituent-turnover individuality. A **Particle Dynamics substrate decision / kill-switch
evaluation** is now due per the charter; substrate switching requires the documented kill-switch review and is not
undertaken autonomously here. Thresholds unchanged; no composite; laws 0/52 not reopened.

## D-021 — Retire Particle Dynamics for the current question (EXP-REF-01 measurement positive control PASS)

**Date:** 2026-07-10 (RUN-20260710-2015-EXPREF01). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** Before any substrate switch, EXP-REF-01 (protocol @0ab80d1) tested whether the FROZEN
detector/tracker/P/M stack can recognize a KNOWN persistent dissipative organization under constituent turnover
and separate it from the static-flux null. A scripted rotating packet with gradual membership turnover was fed to
the frozen stack alongside a matched zero-velocity static-flux null (P not recalibrated; ID labels passive). The
stack RECOGNIZED the reference (single continuous track, P=1.0, M->0.25, 55 probe-positive endpoints) and
SEPARATED it from the null on frozen dynamical observables (|circulation| 0.147 vs 0.000; velocity dispersion
0.090 vs 0.000), even though raw P/M were identical for both. Per the preregistered (user-specified) rule the
measurement is adequate, so the ladder negatives (D-017..D-020) are SUBSTRATE results. **Retire Particle Dynamics
for the persistent-individuality question.** See `docs/PARTICLE_DYNAMICS_KILL_SWITCH_REVIEW.md`. Propose the next
substrate with Flow-Lenia as a candidate to be tested, not assumed (`docs/NEXT_SUBSTRATE_PROPOSAL.md`).

**Reason:** The measurement is not blind to persistent dissipative organization; the substrate genuinely lacked
auditable turnover-individuality across the preregistered ladder. Thresholds unchanged; no composite; no free-form
observer retuning was performed; substrate not switched autonomously (a user decision point).

**Scope caveat:** observer separation was established vs the zero-velocity static-flux null; the flowing-occupancy
alias is resolved only by the same-state causal intervention, which the next substrate must carry.

## D-022 — Flow-Lenia field stack QUALIFIED (EXP_FL_00); launch EXP_FL_01 blind regime map

**Date:** 2026-07-10 (RUN-20260710-2030-EXPFL00). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** EXP_FL_00 (protocol @817d417) implemented a minimal fixed-law mass-conservative Flow-Lenia core
(FFT potential, concentration-limited flow, reintegration-tracking transport) with strictly passive cohort tracers
(same operator, never influencing dynamics, sum==A), a field detector + frozen geometry tracker + field phenotype
(P=exp(-RMS dPhi), declared scales, not recalibrated), and a preregistered cohort field M(tau). All nine
qualification checks PASS: mass conservation (~1.6e-16), nonnegativity, cohort-partition, determinism,
passive-tracer invariance, FFT-vs-direct reference-path agreement (~1.6e-15), detector/tracker on real dynamics,
and the EXP-REF-01 positive control (recognized + separated) on the new field stack. **QUALIFIED** -> preregister
and autonomously launch EXP_FL_01 as a blind low-discrepancy regime map under the same five evidence levels and
causal discipline (no composite; thresholds frozen; P/M separate; same-state causal intervention carried over).

**Reason:** The new substrate + measurement stack meet the same falsifiable-protocol bar Particle Dynamics was
held to, verified independently, before any law search.

## D-023 — EXP-FL-01 first blind Flow-Lenia map NEGATIVE (persistence without turnover)

**Date:** 2026-07-10 (RUN-20260710-2045-EXPFL01). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The preregistered blind Halton regime map (protocol @b2b3124; 24 Flow-Lenia laws x 3 seeds on the
qualified field stack) produced persistent structures in every law (mean field P=0.987; all laws have long tracks)
but with essentially no constituent turnover (mean field M=0.990; 0 probe-positive rows; mean |circulation|=0),
yielding 0 screening-permitted laws. Because EXP_FL_00 already validated that the same 8-cohort field M registers
turnover when present (EXP-REF-01 reference M_min=0.067), M~0.99 here is a genuine regime result, not measurement
blindness. Per the frozen rule EXP-FL-01 (map #1) is SCREEN NEGATIVE. Authorized next step: PRE-DECLARE a wider/
refined blind map (finer cohort granularity for M sensitivity and a flux-favouring parameter range) under the same
protocol and five evidence levels; no threshold relaxation, no composite, no visual selection. The same-state
causal intervention remains the survivor-resolving tool for any future candidate.

**Reason:** F1/F2 confirmed — no permission; the observed persistence is the trivial static/cohesive-blob regime
(no turnover), not turnover-individuality.

## D-024 — Tracer resolution G*=8 verified adequate (EXP_FL_00B); map #1 negative not a resolution artifact

**Date:** 2026-07-10 (RUN-20260710-2115-EXPFL00B). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** A preregistered passive-tracer resolution sensitivity check (protocol @357bc2f) compared cohort
granularities 8/16/32 (plus a 64 convergence probe) on the validated turnover reference and on blind static map-#1
regimes. Dynamics are identical across granularity (A max diff 0.0 -> cohorts strictly passive). The reference
turnover is resolved at all granularities (M_min 0.067/0.0024/...). Static regimes stay at mean M ~0.991 across
8/16/32 -> finer tracers do NOT fabricate turnover. By the pre-declared measurement-resolution criterion (coarsest
adequate + convergent; yield-independent) the selected cohort resolution is **G*=8**. The EXP-FL-01 map #1 negative
is therefore a genuine regime result, not a tracer under-resolution artifact. Map #2 must widen the flux-favouring
PARAMETER DOMAIN, not the tracer granularity.

**Reason:** Prevents reactively lowering M to manufacture candidates; the metric resolution is validated against
the known-turnover reference and shown specific on static regimes.

## D-025 — EXP-FL-01 map #2 NEGATIVE (720 runs); minimal Flow-Lenia core lacks material throughput

**Date:** 2026-07-10 (RUN-20260710-2130-EXPFL01M2). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The preregistered wide blind map (protocol @79f0cbd; 240 laws x 3 seeds over a mechanistically
flux-favouring domain -- flow_gain [0.8,2.5], concentration_theta [0.30,1.20], dt [0.20,0.60], wider kernel/growth
vs map #1) yielded 0 screening-permitted laws. Persistent structures form in 720/720 runs (P median 0.99) but with
essentially no constituent turnover: minimum mean field M across all runs = 0.933; 0.0% of runs have mean M < 0.8;
mean |circulation| = 0.0003. Verified NOT a metric artefact (tracer G*=8 adequate and granularity-invariant, D-024)
nor a map-size artefact (720 runs, wide domain). ASSESSMENT (not a metric change): the minimal fixed-law
mass-conservative Flow-Lenia core lacks a material-throughput mechanism -- conserved mass advects as coherent,
self-retaining lumps and does not pass constituents through persistent structures. EXP-FL-01 map #2 is SCREEN
NEGATIVE. Authorized next step (user decision): a mass-conservative, single-law Flow-Lenia configuration that
introduces genuine material throughput (glider/traveling-structure regime with mass regeneration, or an explicit
open-flux / balanced source-sink term), preregistered under the same falsifiable protocol, same passive-tracer M,
qualified stack, and same-state causal intervention. No metric relaxation; no composite; no visual selection.

**Reason:** F1/F2 confirmed at scale; the observed persistence is rigid mass-lump persistence, not turnover-
individuality; the limiting factor is a missing throughput mechanism, established by quantification rather than by
loosening the measure.

## D-026 — EXP-FL-02 reservoir-exchange throughput: first placebo-controlled causal survivors {2,16,40,59}

**Date:** 2026-07-10 (RUN-20260710-2200-EXPFL02). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The isolated, globally mass-conservative active-field/reservoir exchange (protocol @30c01b0; EXACT
OFF limit reproducing the current core bit-for-bit; spatially generic; detector-independent; no glider mechanism)
was screened matched OFF/ON (64 laws x 3 seeds). ON reached the turnover regime the minimal core could never
reach (median min-M 0.224 vs 0.969; 24 permitted laws vs 0 for OFF). Discipline was then followed end to end:
fresh-seed hold-out (>=2/5, unseen seeds) -> 21/24 survivors; direct alias audit -> 6 rejected as
dissolution/look-alike, 15 persistent-with-turnover; same-state matched-branch causal intervention
(CONTROL/SHAM/PERTURBED/PLACEBO, sham==control bit-for-bit in every unit) -> **4/15 show audited, placebo-
controlled re-establishment: laws {2,16,40,59}** (displaced structures carry their organization to the new site;
old site does not regenerate; placebo produces nothing). Law 53 was REJECTED because its placebo also organized
(a placebo-criterion correction applied before deciding, per D-016's lesson).

**Status: DIAGNOSTIC SURVIVORS, NOT A DISCOVERY.** Based on one causal seed per law. Required before any claim:
multi-seed causal replication; verification that the re-established structure continues to turn over; independent
adversarial re-audit; field-stack cadence/tracker sensitivity. No thresholds changed; no composite; no visual
selection; the static-flux null and passive-tracer invariance remain in force.

**Reason:** Unlike CORE V0 law 52 (rigid cluster, M~1.0, trivial translation-covariance), these structures combine
genuine constituent turnover (M<0.5 with measured reservoir-origin uptake) with constituent-carried organization
under a placebo-controlled displacement.

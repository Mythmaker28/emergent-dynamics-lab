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

## D-027 — EXP-FL-03: the EXP-FL-02 positive is WITHDRAWN (non-replication + frozen lumps + observer artefact)

**Date:** 2026-07-10 (RUN-20260710-2300-EXPFL03). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** With laws {2,16,40,59}, the mechanism, P/M and all thresholds FROZEN before any run (protocol
@14c3a97), the causal intervention was replicated on 12 UNSEEN seeds per law (48 units; explicit denominator
N_POST = actual post-snapshot count, 15 at cadence 10). Result: **AUDITED 2/46 enrolled = 4.3% [Wilson 95% CI
1.2%-14.5%]** (2 censored, reported), versus 4/4 laws audited on the single seed 9501 in EXP-FL-02. The DOMINANT
failure mode is **frozen_lump = 30/46 (65%)**: structures re-establish at the new site, exceed the placebo, leave
the old site unregenerated -- and then STOP exchanging constituents (trivial translation-covariance; the same
failure that killed CORE V0 law 52). The preregistered observer-sensitivity check kills the last two: **0/2 survive
cadence 5/20** (they survive tracker x0.8/x1.2). placebo_failure = 0 and occupancy_alias = 0; sham == control
bit-for-bit in every unit. An adversarial re-audit sustained objections O1 (seed luck), O2 (frozen lumps), O3
(observer artefact) and found no route by which the positive could be real.

**NET: 0 audited successes survive. The EXP-FL-02 diagnostic survivors {2,16,40,59} are WITHDRAWN. Nothing is
promoted.** No threshold, metric, mechanism or law was changed to reach this conclusion. Falsifiers F1, F2, F5 confirmed.

**Recommendation:** STOP adding mechanisms to the closed, globally mass-conservative Flow-Lenia system. Its
active/reservoir exchange yields constituent turnover WITHOUT sustained constituent-carried individuality. The next
honest step is a genuinely OPEN-SYSTEM / reaction-diffusion substrate (true sources and sinks, non-equilibrium
driving), preregistered under the same falsifiable protocol.

## D-028 — OPEN reaction-diffusion substrate QUALIFIED (EXP-RD-00); Flow-Lenia closed system retired

**Date:** 2026-07-10 (RUN-20260710-2330-EXPRD00). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** Following D-027 (EXP-FL-02 positive withdrawn; closed Flow-Lenia retired, no rescue mechanisms), a
minimal genuinely OPEN reaction-diffusion substrate (Gray-Scott) was implemented and qualified: spatially
homogeneous, detector-independent feed F*(1-U) and removal (F+k)*V; real source and sinks (material NOT conserved,
+99.4% from a non-equilibrium probe); an EXACT controlled limit F=k=0 that conserves U+V (drift 0.0); passive
origin tracers partitioning BOTH species with an explicit FEED (external-origin) cohort; and the frozen P/M
separation with unchanged thresholds. All 12 qualification checks PASS, including the **HOMOGENEITY NULL**
(a uniform state remains exactly uniform, ptp = 0.0 -> the forcing provably cannot impose a spatial pattern) and
the POSITIVE/NEGATIVE measurement controls: a frozen/imposed pattern is INDISTINGUISHABLE from a real dissipative
organization on P/M alone (both P=1.0, M_min=0.065) and is separated ONLY by the open-system rates
(production/activity 0.117/0.085 vs 0.000/0.000).

**Consequence:** EXP-RD-01 (blind low-discrepancy map over F, k, Du, Dv, matched OPEN vs the exact CLOSED limit) is
authorized under the five evidence levels, frozen thresholds, continued-turnover requirement,
CONTROL/SHAM/PERTURBED/PLACEBO causal discipline and observer-sensitivity checks. No composite score, no visual
selection, no threshold relaxation.

## D-029 — Temporal feed cohorts (pulse-chase) replace the saturating single FEED cohort

**Date:** 2026-07-10 (RUN-20260710-2345-EXPRD00B). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The EXP-RD-00 tracer used a single permanent FEED cohort, which SATURATES: once feed-origin mass
dominates a structure its cohort composition stops changing and CONTINUED turnover becomes invisible. Confirmed:
the legacy tracer reports median late-window M = 0.936 on a continuously-replacing structure that is 100%
feed-origin (blind), with discrimination of only 0.064 against a ceased-turnover control. Replaced by ROTATING
TEMPORAL FEED COHORTS (pulse-chase): fed material is labelled by WHEN it entered; the reaction transfer carries the
source species' local cohort proportions; homogeneous removal scales all cohorts equally; cohorts remain strictly
passive (zeroing them leaves U,V bit-identical) and partition both species exactly. Two pre-declared controls:
C1 continuous throughput must still register turnover (median late M < 0.5); C2 one-time replacement then the EXACT
closed limit must report no further turnover; discrimination > 0.30. Temporal resolution selected by this
measurement-discrimination criterion ONLY (coarsest adequate; never candidate yield or quadrant occupancy):
**TracerSpec(n_spatial=8, n_temporal=8, tau_feed=250)** -> C1 late-M 0.109, C2 late-M 1.000, discrimination 0.891.
The full open-RD qualification re-passes 12/12 with the new tracer.

**Consequence:** the tracer is FROZEN at (8 spatial, 8 temporal, tau=250). EXP-RD-01 (blind matched OPEN vs exact
CLOSED map) is authorized.

## D-030 — EXP-RD-01 blind map: 9 OPEN screening-permitted laws, 0 in the exact CLOSED limit (NOT candidates)

**Date:** 2026-07-10 (RUN-20260710-2345-EXPRD00B continuation). Model: claude-opus-4-8 (lock lifted).

**Decision:** The preregistered blind matched map (protocol @b3badb8; 24 Halton laws over F,k,Du,Dv x 3 seeds x
{CLOSED = exact limit F=k=0, OPEN}; frozen temporal-feed-cohort tracer, frozen P/M and thresholds) gives:
CLOSED mean M 0.990, 0 probe rows, **0 permitted laws**; OPEN mean M 0.381, median min-M 0.009, 8629 probe rows,
**9 permitted laws** {1,5,7,10,11,13,14,16,19}, production 6.4x CLOSED. Openness reaches the continued-turnover
regime the exact closed limit cannot.

**NOTHING IS PROMOTED.** Screening permission is not a candidate. The Flow-Lenia precedent is explicit: an
identically-shaped screen (24 permitted vs 0 control) died under replication (D-027: 2/46 audited on unseen seeds,
65% frozen lumps, last two cadence artefacts). Live falsifier here: OPEN shows ~3x the track count of CLOSED
(21.3 vs 6.7) -> fragmentation/churn; imposed-pattern/occupancy alias untested at this stage.

**Mandatory next chain (frozen, in order):** fresh-seed hold-out (>=2/5 unseen seeds) -> direct alias audit
including the imposed-pattern/occupancy check -> same-state CONTROL/SHAM/PERTURBED/PLACEBO causal intervention WITH
the continued-turnover requirement -> observer (cadence/tracker) sensitivity -> adversarial re-audit; explicit
denominators, censored seeds, effect sizes, Wilson CIs. No threshold changes, no composite, no visual selection.

## D-031 — EXP-RD-02 NEGATIVE: no audited individuality survives the frozen chain in the open RD substrate

**Date:** 2026-07-11 (RUN-20260711-0000-EXPRD02). Model: claude-opus-4-8 (Fable 5 lock lifted by user).

**Decision:** The nine EXP-RD-01 screening-permitted laws {1,5,7,10,11,13,14,16,19} were FROZEN (no ranking,
replacement or visual selection) and run through the frozen chain. **Level 3 fresh-seed hold-out: 9/9 SURVIVE**
(seven at 5/5) -- the screening signal recurs robustly on unseen seeds. **Level 4 alias audit:** 0/8
dissolution/reformation, but laws 5, 11, 14 are stationary (occupancy-suspect), law 11 shows heavy fragmentation
(27 splits, 20 ambiguous), law 13 has no eligible clean-long track. **Level 5 causal intervention** (9 laws x 10
UNSEEN causal seeds = 90 units; CONTROL/SHAM/PERTURBED/PLACEBO from identical states; SHAM == CONTROL bit-for-bit
in every unit; denominator N_POST = 15): **AUDITED 6/90 = 6.7% [Wilson 95% CI 3.1%, 13.8%]**, 0 censored;
**destroyed = 75/90 (83%)**, placebo_failure 6, occupancy_alias 3, frozen_lump 0. **Preregistered observer
sensitivity: 0/6 audited units survive** (all fail cadence; all survive both tracker perturbations) -> all six are
withdrawn as observer artefacts. **NET: 0 audited successes survive.**

**EXP-RD-02 is NEGATIVE. Nothing is promoted.** Displacing an open-RD dissipative structure destroys it in 83% of
units: the organization is maintained by its LOCATION in the chemical field, not carried by its material. The
Flow-Lenia frozen-lump failure did not recur (0 frozen lumps) because these structures do not survive displacement
at all. This run is the project's clearest demonstration that Level 3 (recurrence: 9/9) and Level 5 (causal
re-establishment: 0) are genuinely different levels.

**Self-flagged method weakness (not used as a rescue):** my cadence perturbation also shifts the enrollment time
(t* = WARMUP_SNAP * cadence), conflating observer and enrollment changes; all 6 units survive the PURE tracker
perturbations. The remedy is a future pre-declared sensitivity that perturbs the observer WITHOUT moving the
enrollment point. It does not change this verdict: the 6/90 base rate, the 83% destruction rate and the
placebo/occupancy failures already fail to support a claim.

No thresholds, composites, mechanisms or laws were changed.

## D-032 — EXP-RD-02 observer-sensitivity eliminations WITHDRAWN; Gray-Scott NOT retired

**Date:** 2026-07-11
**Status:** CORRECTION (supersedes the observer-sensitivity portion of D-031; D-031 is retained unmodified)
**Protocol:** docs/experiments/EXP_RD_03_PROTOCOL.md (SHA 9c3aba3798c946b7b28f99c1a4f36f0078f77baf)

D-031 withdrew the six audited causal units of EXP-RD-02 on an "observer sensitivity" test. That test is
**invalid** and its eliminations are **withdrawn**:

1. **Cadence was not an observer-only perturbation.** Enrollment used `t* = WARMUP_SNAP * cadence`. Changing the
   cadence therefore changed the **enrollment time**, enrolling a **different structure at a different time**.
   It perturbed the physics/enrollment, not the observation.
2. **The tracker perturbation was a no-op.** `tracker_scale` constructed a `TrackerSpec` that the causal readout
   never consumes (the readout is detection + site proximity; the lineage tracker is not in that path). The
   reported "survives tracker x0.8/x1.2" was **vacuous**, not evidence.

**Corrected verdict of EXP-RD-02:**
- **No promotion.**
- **6/90 = 6.7% [Wilson 3.1%, 13.8%] PROVISIONAL causal successes** — units (1,12007), (7,12007), (11,12003),
  (14,12001), (14,12006), (14,12008). They are **not** recorded as observer failures.
- **Observer robustness: UNRESOLVED.**
- **Gray-Scott is NOT retired.** All other EXP-RD-02 findings stand: hold-out 9/9; destroyed 75/90; placebo_failure 6;
  occupancy_alias 3; frozen_lump 0; sham==control bit-for-bit in every unit; 0 censored.

**Consequence:** EXP-RD-03 is preregistered in two parts — (A) observer-ONLY sensitivity at strictly fixed physics,
fixed pre-intervention state, fixed `t*` and fixed branches, varying only offline observation cadence and readout
site radius; (B) a causal-boundary displacement sweep over nested supports derived mechanistically from each law's
diffusion length `ell = sqrt(Du/F)`, because a Gray-Scott entity may include its U-depletion field and RD halo and
not only the detected V mask.

**Self-criticism recorded:** I had already flagged the enrollment/cadence confound in my own adversarial re-audit
(objection O5, docs/agent_journals/2026-07-11/0010_exprd02-adversarial-reaudit_*.md) and applied the frozen rule
anyway. A frozen rule must not be applied through a test that is known to be invalid; the correct action was to
declare the test void and the question unresolved. Applying a broken falsifier is not rigour — it is
falsification theatre, and it destroys true positives exactly as readily as false ones.

## D-033 — EXP-RD-03: candidate RETAINED (no promotion); boundary hypothesis refuted; observer robustness resolved

**Date:** 2026-07-12
**Status:** CANDIDATE RETAINED — NO PROMOTION. Gray-Scott NOT retired.
**Protocol:** docs/experiments/EXP_RD_03_PROTOCOL.md (SHA 9c3aba3798c946b7b28f99c1a4f36f0078f77baf), frozen at 280a1e8.

- **Part A (observer-ONLY, fixed physics / fixed `t*` = 400 / fixed branches):** 4/6 EXP-RD-02 provisional successes
  AUDITED in **all 9** observer settings (cadence {25,50,100} x site radius {0.8,1.0,1.2}). Observer robustness
  **RESOLVED**. Corrected EXP-RD-02 rate **4/90 = 4.4 % [1.7 %, 10.9 %]**. The 2 fragile units are borderline at the
  frozen `frac_new > 0.5` line; threshold unchanged.
- **Part B (nested supports from `ell = sqrt(Du/F)`; U, V and all cohorts translated together):** 36 units, 0 censored.
  S0 5/36 (13.9 %), S1 3/36 (8.3 %), S2 1/36 (2.8 %), S3 4/36 (11.1 %) — **no improvement with support size**.
  **Entity-boundary hypothesis REFUTED**; re-establishment is **not** niche/site-carried. Neither the "broad niche →
  reject" nor the "no support succeeds → retire" branch of the frozen rule applies.
- **Ambient-spot null (added; could have killed everything):** CONTROL frac_new_organized = **0.00 in 5/5**;
  PERTURBED 0.60–1.00. Nothing phenotype-matching grows at the destination on its own.
- **Combined (126 unseen causal units):** observer-robust, compact-support causal re-establishment with continued
  turnover = **5/126 = 4.0 % [Wilson 1.7 %, 9.0 %]**. Law **14** supplies 4/5, replicating across two independent
  unseen seed batches.

**Retracted within the same analysis:** the support-monotonicity argument (5/5 S0-successes fail at S3) is
**confounded** — enlarging the support also imports a U-depleted halo into the destination, chemically starving the
re-forming spot. It carries **no eliminative weight**. Using it would have repeated the exact error of D-032.

**Blocking gap:** the pipeline's **false-positive rate has never been measured**. 4 % positive is not
distinguishable from 4 % artefact. **EXP-RD-04 Part 3 (non-entity cargo → false-positive rate) is run FIRST**;
if the noise floor matches 4 %, the candidate is withdrawn and classical Gray-Scott is retired.

## D-034 — CORRECTION to D-033: support sweep is INCONCLUSIVE, not refuting; law-14 denominators restated

**Date:** 2026-07-12
**Status:** CORRECTION (D-033 stands except as amended here)

**(1) The causal-boundary hypothesis is NOT refuted. The support sweep is INCONCLUSIVE.**
D-033 concluded "entity-boundary hypothesis REFUTED" from the fact that re-establishment does not improve with
support size. That inference is invalid. Enlarging the support is **not** a clean "carry more of the entity"
operation: it simultaneously **transports a chemically U-depleted halo into the destination**, which locally starves
the re-forming spot. The two effects are **confounded with opposite signs**, so a null or negative trend across
supports is uninformative about the true entity boundary. The sweep establishes only that:
- re-establishment does not *require* a broad support (the "niche/site-carried → REJECT" branch does not fire), and
- no support tested produces a *higher* rate than the bare mask.
It does **not** establish where the entity boundary lies. **Recorded as INCONCLUSIVE.** I had already retracted the
monotonicity claim on these grounds and then failed to apply the same reasoning to the aggregate trend — the same
error, one level up.

**(2) Law-14 denominators. The phrase "law 14 supplies 4/5" was a share of SUCCESSES, not a rate.**
Corrected, against ENROLLED units (observer-robust = AUDITED in all 9 offline observer settings):

| law | batch 1 (12001–12010) | batch 2 (13001–13004) | pooled | observer-robust rate, Wilson 95% |
|---|---|---|---|---|
| 14 | 3/10 | 1/4 | **4/14** | **28.6 % [11.7 %, 54.6 %]** |
| 11 | 1/10 | 0/4 | 1/14 | 7.1 % [1.3 %, 31.5 %] |
| 1, 5, 7, 10, 13, 16, 19 | — | — | 0/14 each | 0.0 % [0.0 %, 21.5 %] |
| **all other 8 laws pooled** | | | **1/112** | **0.9 % [0.2 %, 4.9 %]** |
| **ALL** | | | **5/126** | **4.0 % [1.7 %, 9.0 %]** |

Law 14 (28.6 %) and the other laws pooled (0.9 %) have non-overlapping Wilson intervals. **Law 14 was NOT
preselected.** This concentration is a POST-HOC observation and cannot be tested on the data that produced it.
It is a **hypothesis for prospective replication**, and is treated as nothing more.

## D-035 — EXP-RD-04: candidate WITHDRAWN; classical Gray-Scott RETIRED; scrambled-cargo null made mandatory

**Date:** 2026-07-12
**Status:** CLEAN FALSIFICATION
**Protocol:** docs/experiments/EXP_RD_04_PROTOCOL.md (SHA c08a2cc6b1d8233c75db5352b1728a6944f2cd7d), frozen at f9da63d.

Law 14 (frozen), seeds 14001–14040 (entirely unseen), 40/40 enrolled, 0 censored, sham==control 40/40.
Endpoint AUDITED_ROBUST (audited in all 9 offline observer settings), identical for every arm; matched to the same
pre-intervention state, destination, support geometry, total U/V mass, cohort composition and |DELTA|.

- INTACT **17/40 = 42.5 %** [28.5, 57.8]
- **NULL-SC (scrambled cargo, organization destroyed, everything else identical) 19/40 = 47.5 %** [32.9, 62.5]
- NULL-NE 0/40; NULL-NE-M 0/40; null pooled 19/120 = 15.8 %
- Ambient-target control fires 3/40 = 7.5 %

Decision rule: S1 PASS (42.5 % > 0); S2 PASS (Newcombe LB +0.108 > 0.10); **S3 FAIL** (exact McNemar b=1, c=3,
both=16, **p = 0.625**). All three were required → **CANDIDATE WITHDRAWN, classical Gray-Scott RETIRED.**

**Interpretation.** The scrambled lump re-establishes at least as often as the intact entity. What the causal
protocol was measuring was **delivery of sufficient V-rich material to a receptive site**, not the persistence of an
organized individual. Continued cohort turnover, absence of old-site regeneration, observer robustness and a clean
ambient null are **all satisfied by a scrambled lump** — they were never evidence of individuality.

**S2's PASS was a pooling artefact.** NULL-NE / NULL-NE-M score 0 by construction (no V to regrow), so pooling them
diluted the true floor from 47.5 % to 15.8 % and let a dead candidate clear the margin. Only S3 — the paired,
organization-destroying null — caught it.

**BINDING METHODOLOGICAL CHANGE (all future substrates):** the **scrambled-cargo null is a mandatory arm of every
causal intervention**. No re-establishment claim may be made without it. Every prior causal stage of this project
used a *non-candidate, low-V* PLACEBO — a straw-man null of the NULL-NE class — and therefore **never tested any
positive against a cargo with the right matter and the wrong organization**. This retroactively removes the
evidential weight of the EXP-FL-02 survivors and the EXP-RD-02/03 candidates; it does not change their
already-negative or non-promoted status.

**Next:** motile open-system substrate (docs/NEXT_SUBSTRATE_MOTILE_PROPOSAL.md), whose qualification gate includes
the scrambled-cargo null from day one.

## D-036 — Gray-Scott formally retired; causal methodology generalized (R1–R6); EXP-MO-00 authorized

**Date:** 2026-07-12
**Status:** ACCEPTED (D-035 accepted in full)

**Classical Gray-Scott is formally RETIRED for the current question and tested domain** (open Gray-Scott, spot/
labyrinth regimes, the 24-law Halton domain F∈[0.010,0.060], k∈[0.040,0.070], Du∈[0.10,0.20], Dv∈[0.04,0.10]).
The retirement is scoped: it is a statement about this substrate on this question, not a universal claim.
**The previously negative substrates (Particle Dynamics D-021, Flow-Lenia D-027) are NOT rerun.**

**Causal methodology generalized — binding on all future substrates** (`docs/CAUSAL_METHODOLOGY.md`):
R1 never pool qualitatively unequal null arms; report each separately. R2 a null incapable of producing the measured
outcome carries no eliminative weight and may not enter a decision rule. R3 the decisive null is the
organization-destroying (scrambled-cargo) null; it is mandatory and the primary statistic is the paired
intact-vs-scrambled comparison. R4 **GATE-0** — organization must be load-bearing — precedes every law search.
R5 every intervention carries executable assertions that it changed its intended variable. R6 observer sensitivity
is offline, at fixed physics and fixed `t*`.

**EXP-MO-00 authorized:** minimal genuinely open **motile polar-field** substrate. GATE-0 first. No blind law map
may begin unless GATE-0 passes. If GATE-0 fails, the substrate is retired immediately — no rescue mechanisms.

## D-037 — EXP-MO-00: qualification FAILED; motile polar substrate RETIRED before GATE-0; R7 added

**Date:** 2026-07-12
**Status:** SUBSTRATE RETIRED AT QUALIFICATION (GATE-0 never run)
**Protocol:** docs/experiments/EXP_MO_00_GATE0_PROTOCOL.md (SHA 779749854bacd74a1abf293c5965c8e3edb2e2ba)

The minimal open motile polar-field substrate **does not produce a localized entity**. Its active phase is a
Fisher-KPP invasion front with uniform steady state `rho* = F*(R0 - k/g0)/k`, so it is **bistable between the only
two outcomes that contain no entities**: `rho* > 0.30` → the phase fills the whole 64x64 lattice (the "detected
entity" at t* is **4096/4096 cells**); `rho* < 0.30` → extinction. **21 declared parameter points across two
preregistered grids** found no localized regime (12/12 extinct; 8/9 extinct + 1/9 space-filling). Selection criteria
were declared before searching and never referenced intact-vs-scrambled separation.

**The search stopped there.** Localizing the structure would require adding cohesion / density-dependent
aggregation — a **rescue mechanism**, forbidden. **Substrate RETIRED.**

**Two of my own results are VOID and are withdrawn:**
1. The first qualification (persistence 24/24, speed 0.95 cells/step, min M ≈ 8e-7) was computed on a **space-filling
   field** whose periodic centroid is ill-defined. There was no structure.
2. The instrument validation (**INTACT 27/27 robust vs SCRAMBLED 0/27**) was **displacing the entire lattice**. It
   looked like a decisive positive. It was an artefact.

**R5 caught it**: a whole-domain support overlaps its own translate, so the displacement cannot conserve mass, and
the assertion fired loudly on the first real unit. R5 paid for itself within one experiment of being written.

**R7 added to `docs/CAUSAL_METHODOLOGY.md`:** localization precedes everything. A substrate must be shown to produce
localized, persistent, turning-over structures **before** GATE-0. Gate order is now **R7 → GATE-0 (R4) → law search**.
GATE-0 presupposes an entity; do not ask whether organization matters before establishing that something is organized.

## D-038 — EXP-CH-00: R7 PASSES (laws 2, 4, 5). First substrate to clear the localization gate. GATE-0 authorized.

**Date:** 2026-07-12
**Status:** R7 PASS — substrate RETAINED, GATE-0 authorized (and nothing beyond it)
**Protocol:** docs/experiments/EXP_CH_00_PROTOCOL.md (SHA 119188cf74052267cc02239c8d87e40630ce7147), frozen before any screen.

Open chemotactic self-aggregation substrate. **Cohesion is constitutive**: cells secrete `c` and climb `grad(c)`, so
the field they produce pulls them together. The **finite-density regularization is in the core, not a rescue**:
receptor saturation `1/(1+(c/c_sat)^2)` and volume exclusion `q(rho)=max(0,1-rho/rho_max)` in **both** the
chemotactic flux (evaluated on the RECEIVING cell) and the growth source. `0 <= rho <= rho_max` is a **proven
invariant** (asserted in tests), so blow-up is impossible.

**R7 (blind Halton sample of the frozen bounded domain, 32 points, threshold-independent diagnostics):**
- **4/32 localized at t\* and persistent through the window: laws 2, 4, 5, 18.** 20/32 space-filling, 0 diverged.
- **Across 5 qualification seeds (>= 80 % required): law 2 → 5/5, law 5 → 5/5, law 4 → 4/5 → PASS.
  Law 18 → 3/5 → FAIL (PR 0.152, 0.153 against the frozen 0.15). Law 18 REJECTED; no threshold relaxed.**
- Survivors: PR 0.107–0.145, **entity Rg 1.2–2.1 cells**, largest component <= 0.8 % of the domain, occupancy
  <= 0.15 at **every** threshold in the frozen band {0.2,0.3,0.4,0.5,0.6}. `rho <= rho_max` in 32/32.

**Validation (laws 2, 4, 5, all pass):** uniform state stays **exactly** uniform (rho ptp = 0.0, c ptp = 0.0 — the
forcing provably cannot impose a pattern); exact closed limit `g0=k=0` conserves mass (drift 0.0e+00–2.2e-16);
`sum_c C == rho` cell-wise (err ~2e-15); determinism bitwise; **passive tracers bitwise** (cohort relabelling leaves
`rho`, `c`, `N` bit-identical); **continued temporal-cohort turnover** (min M = 0.24–0.43 < 0.5).
**CAUSAL CONTROL: with `chi0 = 0`, PR = 1.000 and localization FAILS for all three laws — cohesion is *caused* by
the internal chemotactic field, not assumed.**

**TWO CORRECTIONS made before any qualification result was used (both disclosed in the protocol):**
1. **The finite-density claim was false as first implemented.** `q` multiplied the *donor* cell and did not
   regularize growth at all; a smoke test reached `rho = 1.408 > rho_max = 1.0`. Fixed; the bound is now proven.
2. **The global radius-of-gyration criterion could not fire.** It measures the spread of the ENSEMBLE, not of an
   entity: a synthetic field of **30 perfectly compact spots scores global Rg = 23.9 against 26.1 for a uniform
   field** (`tests/test_chemotaxis.py::test_global_rg_cannot_detect_compact_multispot`). It was therefore incapable
   of passing ANY multi-spot localized state — the same "test that cannot fire" defect as the pooled null (R2) and
   the Nyquist-violating cadence. Corrected to a **per-entity Rg**. **PR, occupancy and component thresholds were
   NOT touched**, and the same frozen 32 points were re-run from scratch.

**Next and only next: GATE-0** — intact vs organization-destroyed scrambled cargo on laws {2, 4, 5}. **No law map is
authorized unless GATE-0 passes.**

## D-039 — Laws {2,4,5} FROZEN. The 32-point R7 run is CANDIDATE SELECTION, not a prevalence estimate.

**Date:** 2026-07-12
**Status:** ACCEPTED (D-038 accepted; its status downgraded as below)

**Laws {2, 4, 5} are FROZEN.** No law may be added, replaced, ranked or visually selected.

**Statistical status of the 32-point R7 screen, corrected.** D-038 reported "4/32 localized". That figure is **NOT a
preregistered estimate of localized-regime prevalence** and must never be quoted as one: the **per-entity Rg repair
occurred after the first readout of those same 32 points**. Although the repair was justified a priori (a synthetic
field of 30 perfectly compact spots proves the global-Rg criterion cannot fire) and although PR, occupancy and
component thresholds were untouched, the diagnostic was nonetheless *changed after seeing data from those points*.
The run is therefore recorded as an **R7 QUALIFICATION / CANDIDATE-SELECTION exercise** whose only output is the
frozen candidate set {2, 4, 5}. Any honest prevalence estimate would require a fresh Halton block screened with the
now-frozen diagnostic; none is claimed.

**Consequently: ALL GATE-0 evidence uses entirely unseen seeds.** Qualification consumed 5001–5005 and 7001–7002.
GATE-0 uses per-law disjoint unseen blocks: law 2 → 40001–40040, law 4 → 41001–41040, law 5 → 42001–42040.

## D-040 — EXP-CH-01 GATE-0: NO LAW PASSES. Chemotactic substrate RETIRED. R8 added.

**Date:** 2026-07-12
**Status:** CLEAN FALSIFICATION — substrate retired before any law map
**Protocol:** docs/experiments/EXP_CH_01_GATE0_PROTOCOL.md (SHA 9d3e63200154597789f3164feda43843d152a044), frozen first.

Laws {2,4,5} frozen; entirely unseen disjoint per-law seed blocks; N = 40 per law; decided **per law, never pooled**;
Holm–Bonferroni across the three laws.

| law | enrolled | INTACT | **JOINT-SCRAMBLE** | INDEP-SCRAMBLE | PLACEBO | Holm McNemar | diff |
|---|---|---|---|---|---|---|---|
| 2 | 40/40 | 45.0 % | **42.5 %** | 35.0 % | **0 %** | 1.000 | +0.025 |
| 4 | 35/40 | 37.1 % | **37.1 %** | 37.1 % | **0 %** | 1.000 | +0.000 |
| 5 | 26/40 | 23.1 % | **26.9 %** | 34.6 % | **0 %** | 1.000 | −0.038 |

**No law passes.** The joint-scrambled cargo — everything preserved, only positions permuted — re-establishes as
often as the intact aggregate. R5 confirms the null bit: organization existed (z > 2 vs its own permutation null)
and was reduced to chance (|z| < 3), with every preserved statistic exact.

**PLACEBO = 0/40, 0/35, 0/26.** Against the non-entity placebo all three laws would have "passed" overwhelmingly.
This is the Gray-Scott false positive reproduced exactly — and this time the correct null shows there is nothing.

**R8 added — distinguishability precedes individuality.** The common cause of the last two substrate deaths:
(a) **self-assembly defeats load-bearing organization** — an entity that forms spontaneously from noise (which R7
rewards) will re-form from a scrambled lump, so R7 and GATE-0 are in structural tension; (b) **interchangeable
entities make individuality vacuous** — if every entity has the same phenotype, "the same individual re-established"
has no truth conditions. Both dead substrates had exactly one kind of entity.
**Gate order is now: R7 → R8 → GATE-0 → law map.**

Six substrates, six negatives. Nothing promoted. `origin/main` still requires the user's credentials to push.

## D-041 — D-040 accepted; TWO OVERCLAIMS in it CORRECTED; R8 split into three separately-fireable gates

**Date:** 2026-07-12
**Status:** CORRECTION (D-040's verdict stands; two of its inferences were too strong)

Chemotactic substrate **retired for the current question**. Gate order **R7 → R8 → GATE-0 → law map** stands.

**OVERCLAIM 1 — "self-assembly defeats load-bearing organization" was stated as a universal. It is not.**
Correct statement: **self-assembly from noise implies GATE-0 failure *here* because this substrate has essentially
ONE interchangeable aggregate attractor.** A substrate can perfectly well self-assemble entities from noise *and*
have load-bearing organization — provided the assembly is **multistable**, i.e. the same global law admits several
metastable internal organizations. Then a scrambled cargo may re-assemble *an* entity while failing to recover *the
source* entity. Spontaneity is not the problem; **uniqueness of the attractor** is. R7 and GATE-0 are in tension
**only for single-attractor substrates**.

**OVERCLAIM 2 — "individuality was never expressible" was stated as a universal. It is not.**
Correct statement: individuality was **not identifiable in the tested single-phenotype substrates**. This is a
property of Gray-Scott spots and chemotactic aggregates (one entity type, mutually interchangeable), not a claim
about individuality in general, and not a claim about substrates we have not tested. The failure was one of
**identifiability**, not of expressibility.

**Consequence: R8 is split into three gates, each of which must be shown to be able to FIRE and to FAIL on synthetic
cases before it is used on any substrate** (`docs/R8_GATES.md`):
- **R8-A diversity** — between-entity phenotype distance > within-entity temporal drift, by a frozen margin, after
  removing translation, rotation and other trivial symmetries.
- **R8-B predictive identity** — a frozen classifier / nearest-neighbour rule fitted on EARLY states only must
  re-identify the same entity later and on held-out trajectories, despite constituent turnover. **Position, total
  mass, absolute orientation and tracker ID are FORBIDDEN identity features.**
- **R8-C causal identity** — intact displaced cargo must preferentially reconstruct its **source-specific**
  phenotype; organization-destroyed scrambled cargo may reconstruct a *generic* entity but must not recover the
  **source identity** at the same rate. **The primary outcome is identity-specific recovery, not entity presence.**

## D-042 — EXP-MA-00: R8 FAILS; multistable droplet substrate RETIRED. No GATE-0, no law map.

**Date:** 2026-07-12
**Status:** RETIRED AT R8 (GATE-0 never authorized)
**Protocol:** docs/experiments/EXP_MA_00_PROTOCOL.md (SHA f59dd700baac59620c50f739b2fb2ad6ce4b0e13), frozen first.

**Structural finding: in this frozen domain, localization and multistability are mutually exclusive.**
Blind 32-point Halton screen (`lam ∈ [0.5,6.0]`): the only laws that pass R7 (2, 4) have **mixed** droplets
(demixing_index 0.043 / 0.008); every genuinely demixed law (5, 9, 16, 17, 18; 0.18–0.42, Janus-scale) **fails R7**.
**0/32 are both localized and demixed.** Median demixing over all 115 detected entities: 0.012.

**R8 on the R7 survivors (unseen seeds 7101–7108):** law 2 → R8-A ratio **1.42** (need > 2.0) FAIL, R8-B accuracy
**0.19** vs chance 0.12 FAIL. Law 4 → **1.31** FAIL, **0.15** FAIL. **The built-in `lam = 0` NEGATIVE CONTROL fails
identically** (1.32 / 0.21): at the laws that localize, the demixing term is doing nothing, and the frozen law is
statistically indistinguishable from the control with multistability switched off.

**Substrate RETIRED. No mechanism added. GATE-0 and the law map remain unauthorized**, exactly as preregistered.

**Scope, stated precisely:** this does NOT show multistable substrates cannot support individuality. It shows that
**this** two-species demixing droplet, **in this bounded domain**, cannot cohere and structure its interior at the
same time — cohesion (shared attractant) and demixing (mutual repulsion) **compete for the same flux**. A substrate
whose cohesion and internal structure ride on **different, non-competing degrees of freedom** is not excluded; it is
what this result points to.

Seven substrates, seven negatives. Nothing promoted.

## D-043 — D-042 accepted and SCOPED; EXP-SC-00 authorized (orthogonal scaffold + internal network)

**Date:** 2026-07-12
**Status:** ACCEPTED, scoped

**EXP-MA-00 retired for the current question and the tested parameter domain.** Scope, precisely:
**in that architecture** localization and demixing are antagonistic **because cohesion and internal structuring
compete through the same transport flux** — a single advective term moved both species, so any parameter regime
strong enough to cohere overwhelmed the repulsion, and any regime strong enough to demix tore the droplet apart.
**This does NOT generalize to multistable droplets in general**, nor to architectures in which cohesion and internal
structure are carried by different degrees of freedom. It is a statement about one coupling, in one bounded box.

**EXP-SC-00 authorized**, designed from the outset with **functionally orthogonal degrees of freedom**:
(1) a localized **open scaffold** (chemotactic cohesion + volume exclusion) providing cohesion and finite-density
support — the mechanism already validated at R7 in EXP-CH-00; (2) an **internal bistable reaction network confined
to the scaffold**, which plays **no part in cohesion**; (3) passive temporal tracers; (4) a **causal coupling by
which the internal state predicts a future behavioural observable** (nutrient uptake), so identity is not a
decorative label. `beta = 0` (no coupling) is a built-in negative control for (4).

**Nothing may be screened until an ORTHOGONALITY QUALIFICATION (O1–O4) passes**
(`docs/experiments/EXP_SC_00_PROTOCOL.md`), then R8-A → R8-B → R8-C, in that order.
**No law map, no GATE-0, until at least two distinguishable, temporally persistent internal organizations exist
under the same frozen global law on unseen seeds.**

## D-044 — EXP-SC-00: orthogonality FAILS at O2; substrate RETIRED before R8. Couplings must be separated, not just DOFs.

**Date:** 2026-07-12
**Status:** RETIRED AT ORTHOGONALITY QUALIFICATION (R8 never reached)
**Protocol:** docs/experiments/EXP_SC_00_PROTOCOL.md (SHA aed457c2) + Amendment 1 (SHA fc4f4d97), frozen first.

Scaffold = **exactly** the EXP-CH-00 law-2 R7 survivor. All metrics passed synthetic must-pass/must-fail cases first.

**PASS: O1** — scaffold coheres with the internal network disabled (PR 0.133, Rg 2.36). **O3** — internal fields alone
create zero entities. **O4** — flipping the internal state changes future specific uptake by 13–28 %; the `beta = 0`
negative control changes it by **0.0 %**. Identity is causally efficacious, not decorative.

**FAIL: O2** — at **every** `beta` in the declared grid (0.05, 0.10, 0.15, 0.20), on **both** unseen seeds. Entity Rg
varies across internal states by 1.83–4.12 cells (tolerance 1.5). At the smallest coupling O2 *and* O4 both fail:
**no coupling strength makes identity efficacious while leaving localization invariant.**

**Finding (scoped):** identity acting through **uptake** is not orthogonal to cohesion, because **uptake feeds growth
and growth feeds the scaffold's mass balance**. Third instance of one pattern: EXP-MA-00 shared the *transport flux*;
EXP-SC-00 shares the *mass balance*. **Separating the degrees of freedom is not enough — the COUPLINGS must be
separated too.** This points at couplings that do not feed the scaffold's mass balance (motility *direction*,
oscillation *phase*, response to an external probe). Not added here; that is a new substrate, preregistered from the
outset.

**Near-miss, recorded:** at hand-set `beta = 0.6` O2 failed; a post-hoc scan "found" `beta = 0.15` passing O2+O4 on
the very seed the failure was seen on (dRg 1.04). Rather than adopt it, `beta` was re-declared as **prospectively
selected** by the qualification on a frozen grid and unseen seeds (Amendment 1). **On unseen seed 8101, `beta = 0.15`
fails O2 (dRg 1.95).** The post-hoc window did not replicate. Taking it would have carried a non-qualifying substrate
into R8.

Eight substrates, eight negatives. Nothing promoted.

## D-045 — D-044 STANDS under its own criterion, but O2 was MIS-SPECIFIED; EXP-SC-00B authorized with O2'

**Date:** 2026-07-12
**Status:** CORRECTION OF SCOPE (D-044's result is unchanged and is NOT reinterpreted)

**D-044 remains a valid result under its original preregistered O2.** It is not amended, not reinterpreted, and its
seeds (8001, 8101, 8102) are **not reused**.

**But O2 was the wrong criterion, and its failure does NOT show the architecture is invalid.**
O2 demanded **near-invariance of entity radius** across internal states (|dRg| <= 1.5 cells). An internal state whose
whole purpose is to **alter uptake** must alter growth, and therefore must alter morphology. **O2 and O4 were
contradictory by construction** — which is exactly why no `beta` could satisfy both, and why at the weakest coupling
both failed at once. That is a property of my criterion, not of the substrate.

**Functional orthogonality requires (a) scaffold-independent cohesion and (b) VIABILITY across identity states — not
identical body size.** Size and shape are *expected* to differ; they must be **reported, not thresholded away**.

**EXP-SC-00B authorized** as a **new prospective qualification on entirely unseen seeds** (8201–8203), replacing O2
with **O2'** (viability, not invariance) and strengthening O4 to **O4'** (the internal state must predict future
behaviour **after controlling for current mass, radius, density and size** — so identity cannot be a proxy for
trivial morphology). O1 and O3 unchanged. `beta` selected prospectively on a frozen grid by O1/O2'/O3/O4' only.
If no `beta` preserves viability across internal states, the substrate is retired and identity coupling moves to
**motility direction, oscillatory phase, or probe response** — channels that do not feed the scaffold's mass balance.

## D-046 — EXP-SC-00B: qualifies prospectively (O1/O2'/O3/O4' PASS), then FAILS R8-B. Substrate RETIRED.

**Date:** 2026-07-12
**Status:** RETIRED AT R8-B (R8-C never reached)
**Protocol:** docs/experiments/EXP_SC_00B_PROTOCOL.md (SHA a6d301870b29b4ef046194b68466727dc6e4ddb6), frozen first.
Substrate UNCHANGED. Unseen seeds only. D-044's seeds not reused; D-044 not reinterpreted.

**QUALIFICATION PASSES at `beta = 0.10`** (frozen prospective rule, selection references no identity outcome):
- **O1 PASS** — scaffold coheres with the internal network disabled (PR 0.126/0.116/0.116).
- **O2' PASS** — every internal state independently viable (localization, no invasion, no extinction, no
  catastrophic fragmentation, persistence 1.00, continued turnover) on 3 states x 3 unseen seeds. Body size DIFFERS
  across states (u: 21–24 entities; v: 11–12) and is **reported, not thresholded** — vindicating the O2 -> O2' fix.
- **O3 PASS** — internal fields alone create zero entities.
- **O4' PASS — r_partial = +0.521, permutation p < 0.0005, n = 96.** The internal state predicts **future** uptake
  **after controlling for mass, radius, density and size.** Identity is causally efficacious and is **not** a proxy
  for morphology (the confound case is a must-fail unit test the metric provably rejects).

**R8-A PASS** — between-entity distance 0.836 vs within-entity drift 0.394 → ratio **2.12** (margin 2.0).
**R8-B FAIL** — early-half prototypes re-identify late-half observations at accuracy **0.286** vs chance 0.083;
required chance + 0.25 = **0.333**. **3.4x chance is a real signal but does not meet the preregistered bar. The bar
is not moved.**

**Cause:** within-entity temporal drift (0.394) is nearly half the between-entity distance (0.836). The internal
organizations are diverse but **not temporally stable** — the toggle domains coarsen and rearrange while the material
is replaced. R8-A only just passes for the same reason. **Identity exists here; it does not persist.**

**Scope:** this does NOT invalidate the scaffold+internal-network architecture — the architecture worked on every
orthogonality criterion, including the strongest causal result this project has produced (O4', r = +0.52). What
failed is the **pinning** of the internal organization under constituent turnover. Lowering `D_int` or strengthening
bistability now would be **tuning-after-failure and is forbidden**. The next substrate must declare a **pinning
mechanism in advance**.

Nine substrates, nine negatives. Nothing promoted. But O4' is the first time an internal identity has been shown to
causally predict future behaviour independently of trivial morphology.

## D-047 — D-046 stands; its INTERPRETATION corrected. D_int untouched. EXP-GT-00 (metrology) authorized first.

**Date:** 2026-07-12
**Status:** INTERPRETATION CORRECTION (D-046 unchanged; nothing promoted; no retrospective rescoring)

**D-046 is unchanged.** The frozen **snapshot-based** R8-B failed (accuracy 0.286 vs required 0.333) and nothing is
promoted. No threshold is moved, no result rescored.

**What EXP-SC-00B DID establish:**
- internal states that are **behaviourally efficacious** (O4': r_partial = +0.521, p < 0.0005, after controlling for
  mass, radius, density and size — identity is not a proxy for morphology), and
- internal states that are **between-entity diverse** (R8-A: ratio 2.12).

**What it did NOT establish: longitudinal individual identity.** The snapshot representation could not re-identify an
entity with its own earlier self. That is a failure of a **snapshot** representation on a **dynamic** object — it is
NOT evidence that no dynamic identity exists, and it is NOT evidence that one does.

**D_int is NOT lowered and no pinning mechanism is added.** Doing so now would be a new substrate motivated directly
by the observed failure, on the exact parameter the failure points at, and it risks converting a *dynamic* identity
into a **constructed static barcode** — which would be a measurement artefact dressed as a discovery.

**Order of work, authorized:**
1. **EXP-GT-00 — a separate GROUND-TRUTH METROLOGY branch.** A minimal Game-of-Life computational hierarchy
   (glider/channel → logic gate → memory bit → tiny FSM). The discovery observer sees **only raw cell-state
   trajectories**; a separate evaluator retains the hidden component locations, causal graph, memory states, inputs,
   outputs and program identity. A dynamic-identity representation must be **validated against this ground truth**
   before it is trusted on the droplet substrate.
2. **EXP-SC-01** — R8-B-**dynamic** on the **unchanged** beta = 0.10 scaffold substrate, entirely unseen seeds,
   fixed-length temporal windows instead of single snapshots. Representation, classifier, threshold, window length
   and censoring rules frozen **before** any EXP-SC-01 outcome is inspected, and only after passing synthetic AND
   ground-truth must-pass/must-fail cases.
3. If dynamic identity passes prospectively → **R8-C**. If **both** static and dynamic R8-B fail → retire the
   substrate, and **only then** design an intrinsically pinned internal-organization substrate with the pinning
   mechanism declared from the outset.

## D-048 — EXP-GT-00: ground-truth benchmark built and VERIFIED; observer v1 FAILS it. EXP-SC-01 BLOCKED.

**Date:** 2026-07-12
**Status:** METROLOGY BRANCH WORKING — it rejected the observer before it could touch the science.

**The benchmark is real and verified.** Game-of-Life computational hierarchy, every component checked empirically:
glider/channel (period-4 displacement exactly (+1,+1)); eater (absorbs a stream, survives); **inhibit gate / memory
bit** (bit=1 → output 194, bit=0 → output 0); **tiny FSM** (output = 194 × open channels, exactly as the hidden
causal model predicts). The discovery observer sees **only raw cell states**; the evaluator holds component
locations, causal graph, memory contents, I/O and program identity, and never shows them.

**Observer v1 (persistent-site transverse profile on intrinsic axes + population spectrum + output autocorrelation)
FAILS.**

| challenge | distance | required | verdict |
|---|---|---|---|
| (d) exact copy, reset history | 0.000 | ≈ 0 | PASS |
| (c) **identical visible output, different mechanism** | 1.417 | LARGE | **PASS** |
| (a) same architecture, different program | 1.213 | LARGE | PASS |
| (a) same architecture, different output | 1.219 | LARGE | PASS |
| (b) different architecture, same program | 0.684 | > 0 | PASS |
| **(e) progressive component replacement** | **1.518** | **small** | **FAIL** |

**separation = min(different)/max(same) = 0.45 — below 1.0. The observer is NOT fit for use.**

**Why it fails — and it is the failure that matters most.** Under progressive micro-component replacement the
representation moves **further** (1.518) than it does between genuinely different programs (1.213–1.417). The
observer keys on **flow and output statistics**, which are disturbed while a component is briefly absent (output
388 → 662 during the gaps). It therefore **mistakes "same individual, parts replaced" for "different individual"** —
the exact Ship-of-Theseus confusion the whole research programme is about. Had this representation been taken
straight to the droplets, it would have manufactured identity changes out of constituent turnover.

**A second silent no-op caught (the 6th of this session).** Challenge (e) as first written deleted a still-life eater
and re-placed an identical one at the same phase — restoring the exact grid: **0/701 frames differed**. It could not
fire, and it "passed" at d = 0.0000. It now removes the component, lets the channel run open for 6 steps (gliders
genuinely leak; 526/701 frames differ) and installs a fresh one, with function continuing throughout.

**EXP-SC-01 IS BLOCKED.** No representation may be used on the droplet substrate until it passes EXP-GT-00 and is
then frozen and evaluated on held-out architectures, programs and layouts. **D-046 is unchanged; D_int untouched; no
substrate tuning; no threshold moved.**

## D-049 — D-048 accepted. The observer's ONTOLOGY was wrong, not its weights. EXP-GT-01 preregistered.

**Date:** 2026-07-12
**Status:** ACCEPTED. EXP-SC-01 remains BLOCKED. EXP-GT-00 observer and results preserved UNCHANGED.

**The diagnosis is not "tune the weights until (e) passes".** A single scalar identity distance was being asked to
answer five different questions at once — causal architecture, program/memory state, input-output function,
historical lineage, and material implementation. Under component replacement, **material** changes while
**architecture, program, function and lineage** are preserved; a scalar has no way to say that, so it said
"different individual". The failure is **ontological**, and tuning a scalar would only have hidden it.

**EXP-GT-01 preregisters a FACTORIZED ground-truth target** (`docs/experiments/EXP_GT_01_PROTOCOL.md`):
**A** causal architecture · **S** program/memory state · **F** functional I/O equivalence · **L** historical lineage ·
**M** microscopic/material implementation. **Every challenge carries an explicit expected VECTOR, not a same/different
label. Heads are never collapsed into a composite score** (that would recreate the very error being fixed, and
composites are banned project-wide).

**The replacement challenge is split**, because the old one conflated two different things:
- **E1 — function-preserving handoff** (the real Ship-of-Theseus gate): a component is replaced by a functionally
  equivalent but **microscopically distinct** implementation, with **assertions** that (i) the grid trajectory
  changed, (ii) the replacement actually occurred, and (iii) the **complete input-output behaviour is identical at
  every timestep — no silent interval**. Expected vector: **A=same, S=same, F=same, L=same, M=DIFFERENT.**
- **E2 — damage-and-repair**: functional continuity may legitimately break while lineage and recovery continuity
  hold. Expected vector: **A=same, S=same, F=BROKEN-then-restored, L=same, M=different.**
  **E2 is NOT used as the hard Ship-of-Theseus gate.** The old EXP-GT-00 challenge (e) was an E2-style
  damage-and-repair masquerading as an E1 gate — which is a second reason it produced a nonsense verdict.

**EXP-GT-00 is preserved unchanged** as the record of a failed observer. **EXP-SC-01 stays blocked.**

## D-050 — EXP-GT-01: factorized suite built; observer v2 FAILS it. Droplets stay BLOCKED.

**Date:** 2026-07-12
**Status:** OBSERVER v2 FAILS the factorized ground-truth suite. EXP-SC-01 remains BLOCKED.
**Protocol:** docs/experiments/EXP_GT_01_PROTOCOL.md (SHA d3ac99b316a235207422519fd36978034ee42f97), frozen first.
EXP-GT-00's observer and results are **preserved unchanged**.

**What was built and VERIFIED:**
- **E1, the real Ship-of-Theseus gate, is now non-vacuous.** A gate component is handed off to a functionally
  equivalent but microscopically distinct implementation (relief installed *before* the incumbent is removed, so the
  gate is never unmanned). All three assertions hold: **trajectory changed (441/701 frames), replacement actually
  occurred (old persistent cells 0, new 7), and I/O identical at EVERY timestep — no silent interval.**
  A **held-out implementation** also passes the assertions. (My first held-out value put the relief *below* the
  output line; assertion (iii) caught it. That is what assertions are for.)
- **E2 (damage-and-repair) is separated** and is **not** used as the Ship-of-Theseus gate.
- **The L head reports INDETERMINACY for an exact copy** rather than guessing: two identical circuits produce
  literally identical trajectories, so lineage is **not identifiable from trajectories alone**. Saying so is the only
  honest answer — **and a scalar observer had no way to say it.** The factorized ontology is already earning its keep.

**Observer v2 (blinded causal-response fingerprints) FAILS:**

| comparison | A | S | F | M | expected |
|---|---|---|---|---|---|
| E1 handoff (dev) | 1.000 | 0.182 | 0.503 | 0.264 | same, same, same, DIFF |
| E1 handoff (held-out) | 1.000 | 0.182 | 0.503 | 0.264 | same, same, same, DIFF |
| (c) identical output, different memory | 0.027 | **0.000** | 0.000 | 0.467 | same, **DIFF**, same, DIFF |
| (a) same arch, different program | 0.353 | **0.000** | 0.500 | 0.304 | same, **DIFF**, DIFF, DIFF |
| (b) different arch, same program | 1.000 | 0.091 | 0.000 | 0.905 | DIFF, same, same, DIFF |

**Two specific, diagnosable defects — the value of factorizing:**
1. **The S head is BLIND.** It scores **0.000** for 1010 vs 0101, which differ in memory. The blinded probe grid
   (stride 20) is too coarse to land on the channel tracks, so no pulse ever discriminates a gated channel from an
   open one. **The probe grid has a RESOLUTION requirement that was never stated or verified** — a must-pass case is
   required: a probe design must be shown able to read a known memory word before it is trusted to read an unknown one.
2. **The A and F heads are CONFOUNDED.** Fingerprints for the E1 arms were computed on the **post-handoff final
   frame** — a mid-flight state with gliders in transit — and compared against fingerprints from a **fresh** grid.
   That compares *different transients*, not different architectures. Fingerprints must be **phase-matched**.

**Verdict: FAIL. The droplets remain BLOCKED.** No head is tuned to pass; both defects require a corrected probe
design and phase-matched comparison, each with its own must-pass case, in the next iteration.
**D-046 unchanged. D_int untouched. No threshold moved. No substrate tuned. No composite score anywhere.**

## D-051 — EXP-GT-02: S head REPAIRED and COVERAGE-CERTIFIED. A/F/L repairs pending. Droplets stay BLOCKED.

**Date:** 2026-07-12
**Status:** PARTIAL INSTRUMENT REPAIR. **EXP-SC-01 remains BLOCKED.**
**Protocol:** docs/experiments/EXP_GT_02_PROTOCOL.md (SHA ca9a0c5a76fb77aab67d5bb5f8083231d0a2bcf1), frozen first.
**Observer v2 (EXP-GT-01) and its failures are preserved unchanged.**

**OBSERVABILITY CONTRACT preregistered.** Every case carries **two** labels — the relation (SAME/DIFFERENT) **and
whether it is identifiable from the supplied observations**. Every head may output **INDETERMINATE**, and **correct
abstention is a PASS**; resolving a relation the data cannot support is **fabrication and scored as failure**.

**S HEAD: REPAIRED AND CERTIFIED.** The v2 stride-20 grid never intersected the channel tracks (they sit at
`gun_col + 29` = 34/74/114/154; a stride-20 scan from 20 touches none of them), so S was **blind by construction**
and no distance function could have been tuned into sight. Replaced by an **exhaustive stride-1 blind scan** with two
intervention types and **no access to labels, positions, bits or the causal graph**:
- **INJECTION** upstream: a standardized pulse absorbed iff its diagonal meets a gate ⇒ marks **GATED** channels.
- **DELETION** downstream: a blind 5x5 tile cleared for 8 steps (≥ 2 glider periods, so no clock phase can hide a
  stream) ⇒ output drops iff a live stream passes ⇒ marks **OPEN** channels.

**COVERAGE CERTIFICATE — GRANTED.** The probe reconstructs **every known word, exactly**:

| circuit | probe reads | truth | channels |
|---|---|---|---|
| dev 1010 / 0101 / 1111 / 0000 | 1010 / 0101 / 1111 / 0000 | ✔ all correct | 4/4 |
| **held-out layout** 1010 / 0101 | 1010 / 0101 | ✔ correct | 4/4 |

**MUST-FAIL controls PASS** (identical words → SAME, including across a held-out layout).
**MUST-PASS discriminations PASS** — including **1010 vs 0101 → DIFFERENT**, *the exact case on which the old S head
scored 0.000*.

**A bug found and disclosed by the certificate itself:** the deletion arm originally summed the output over **272**
frames against a **281**-frame baseline, so it "detected a drop" at **every column, including empty space** — an
accounting artefact, not a signal. Both arms are now frame-matched. **The certificate caught it before a single
unknown program was read.** That is precisely what a coverage certificate is for.

**STILL OUTSTANDING (droplets stay blocked):**
- **A and F**: phase matching not yet implemented — fingerprints must be accumulated over a **complete inferred clock
  period** and configurations **re-settled** to a common established state. **A transient post-handoff frame must
  never be compared with a fresh initialization** (v2's confound).
- **L**: must demonstrate **calibrated SAME / DIFFERENT / INDETERMINATE**, including correct abstention on exact
  copies.
- E1 and E2 evaluated separately, on development **and entirely held-out** replacement implementations.

**EXP-SC-01 remains BLOCKED until A, S and F pass their held-out criteria and L is calibrated. No composite score.
No head tuned to pass. D-046 unchanged, D_int untouched.**

## D-052 — EXP-GT-02B: F and L PASS. A fails on held-out for want of a CERTIFIED RESOLUTION. Droplets stay BLOCKED.

**Date:** 2026-07-12
**Status:** PARTIAL REPAIR. **EXP-SC-01 remains BLOCKED.**
**Protocol:** docs/experiments/EXP_GT_02B_PROTOCOL.md (SHA 3fdd3cc69f075a38048dfa1c0084ce6411abe176), frozen first.
The certified S head (D-051) is **preserved exactly**; its scope is recorded narrowly (the declared word family,
development + held-out layouts — **not** a universal memory detector). Observer v2 preserved unchanged.

**Clock inferred from RAW trajectories, no hidden labels → period 30 = the true gun period.** The passive signature
is an **FFT magnitude over a fixed window every inferred period divides**, so it is cyclic-phase-invariant **by
construction, not by alignment**. Configurations are **re-settled**; a post-handoff transient is **never** compared
with a fresh initialization.

| comparison | A | F | expected | |
|---|---|---|---|---|
| **PURE PHASE SHIFT** (+15 = half period) | SAME | SAME | A=SAME, F=SAME | **PASS** |
| different ARCHITECTURE, same function | **SAME** | SAME | A=**DIFFERENT**, F=SAME | **FAIL** |
| different PROGRAM (1010 vs 0101) | SAME | DIFFERENT | A=SAME, F=DIFFERENT | **PASS** |
| E1 handoff, development impl | SAME | SAME | A=SAME, F=SAME | **PASS** |
| E1 handoff, **HELD-OUT** impl | SAME | SAME | A=SAME, F=SAME | **PASS** |

**F: 5/5 PASS** — phase-invariant; SAME across different architectures implementing the same function; DIFFERENT on a
different program; SAME across both E1 handoffs.
**L: 3/3 PASS** — continuously observed E1 handoff → **SAME**; observed branch with divergent trajectories →
**DIFFERENT**; exact copies with observationally identical data → **INDETERMINATE**. **Correct abstention, not
fabricated certainty.**

**A: STRUCTURAL BUG FIXED, RESOLUTION NOT CERTIFIED.** A was contaminated by the program: a channel's detected
*column* depends on how it is gated (absorbed injection at ~gun+30, deleted stream at ~gun+63), so A moved when only
S moved. Rebuilt on the **intrinsic diagonal** `d = row − col` — the invariant a glider actually travels along —
which is identical however the channel is gated. A now correctly reports SAME under phase shift, SAME under a program
change, and SAME across both E1 handoffs.

**But A FAILS the decisive case**: the held-out layout's channel gaps differ by **5 columns**, while A's
**preregistered tolerance is 6.0**. The architectural difference is **below A's declared resolution**, so it reports
SAME. **The tolerance is NOT retuned** — that would be exactly the weight-tuning this experiment forbids, and the
held-out architecture is the very case it would be tuned on.

**The missing instrument step, and it is the S lesson again:** A needs a **RESOLUTION CERTIFICATE**, exactly parallel
to S's coverage certificate. The tolerance must be **derived from the development null** (the phase-shift-only
comparison, which is the measured noise floor), declared **before** evaluation, and A must **certify the minimum
architectural difference it can resolve** before it is trusted to say two architectures are the same.
**An instrument must certify what it can resolve before its "SAME" is worth anything.**

**EXP-SC-01 remains BLOCKED** until A passes prospectively on held-out cases. No composite. No head tuned to pass.
D-046 unchanged, D_int untouched.

## D-053 — EXP-GT-A0: the "A failure" was a BENCHMARK-ONTOLOGY ERROR. D-052's repair is WITHDRAWN. Tolerance untouched.

**Date:** 2026-07-13
**Status:** **FAILED — ONTOLOGY.** EXP-SC-01 remains BLOCKED. D-046 unchanged, D_int untouched.
**Run:** `results/EXP-GT-A0-20260713-001`. Observer v2, the certified S head (D-051), and F/L (D-052) are all
**preserved exactly**. **No threshold was moved. No head was tuned.**

**D-052 recorded that `A` failed because two architectures' channel gaps differ by 5 columns while `A`'s
preregistered tolerance is 6.0, and prescribed an A RESOLUTION CERTIFICATE to sharpen it. That prescription is
withdrawn, because the label it would have been graded against is wrong.**

**The two "architectures" are the same causal graph.** `build()` writes its edges over **channel ordinals** —
`(gun_i → out_i)`, `(gun_i → gate_i → out_i)`. **The gun columns never enter the graph.** Verified on all three
programs, against **both** ground-truth graphs:

| program | sp40 vs sp45 | declared edges identical | structurally isomorphic | **verified active-influence isomorphic** | **measured delays equal** |
|---|---|---|---|---|---|
| 1010 | — | **yes** | yes | **yes** | **yes** — (174,174,234,234) |
| 0101 | — | **yes** | yes | **yes** | **yes** |
| 1111 | — | **yes** | yes | **yes** | **yes** — (234,234,234,234) |

The active-influence graph is **measured, not assumed**: every gun and every gate is ablated in turn and the
per-channel output response is recorded with its delay. The two layouts differ **only in gun-column spacing**
(40 vs 45). `arch_id = "A" + "-".join(gun_cols)` was a **layout id wearing an architecture's name**.

**`A = SAME` was the CORRECT answer.** Expected label corrected to **A = SAME, G = DIFFERENT**.

**Why this matters more than a relabelling.** Had the prescribed repair been executed, `A`'s tolerance would have
been driven below the layout noise floor so that a 5-column spacing change read as DIFFERENT — i.e. **`A` would
have been tuned into a layout detector, destroying the translation/layout invariance that is its entire
definition.** The instrument was right and the reference was wrong. **Sharpening a ruler because it disagrees with
a mislabelled standard is how an instrument gets silently broken.** The ban on tuning a head to pass a case is not
enough on its own: **the expected label must itself be auditable.**

**`G` — geometric embedding — is introduced** as an auxiliary diagnostic head. It records layout (channel spacings,
translation-invariant). It is **reported separately and NEVER composited**, and **G is not identity**. `A` is
**graph-isomorphism-aware and embedding-invariant**, and is read off the **structural** graph (program-independent),
not the **active-influence** graph (program-dependent — a closed gate severs a path that structurally still exists).
Binding ontology: `docs/IDENTITY_ONTOLOGY.md`.

**SECOND BUG, found by the same audit: `ARCH_HELD_OUT[1] = (10,46,82,118)` is a DEAD CIRCUIT.** Zero output on all
four channels under programs 1010 and 1111; under 0101 it emits debris with spurious cross-channel influence
(`gate2` ablation perturbs **all four** outputs). Cause: the Gosper gun spans **36 columns**, so at spacing 36
adjacent guns **touch** and annihilate. Each gun works **alone** at each of those columns, so the fault is the
**layout**, not the component. Swept spacing 34–49: **34–37 BROKEN, ≥38 VIABLE**. This layout has been in the
benchmark manifest since EXP-GT-00. **It is VOID and quarantined.** No reported EXP-GT-00/01/02/02B metric depends
on it (all decisive comparisons used sp45), but its representations were computed and stored as if valid.
**Nobody had ever asserted that a declared circuit computes anything.** A **viability assertion** — every declared
channel actually carries a stream, and the declared graph is the graph the dynamics realizes — is now **mandatory
for every circuit admitted to the benchmark**.

**THIRD CONSEQUENCE: EXP-GT-00's case (b) "PASS" is CORRECTED to a FAIL.** `d_diff_arch_same_program = 0.684`
against a criterion of "must be > 0" was **credit for reporting a large distance between two systems with the same
causal architecture**. Under the corrected label the criterion inverts. Observer v1's persistent-site transverse
profile is **layout-sensitive by construction** — it was a **G** detector, never an **A** detector. EXP-GT-00's
artefacts are **preserved unchanged**; only the label moves.

**THE BLOCKER, stated plainly: the benchmark has never contained ONE genuinely different causal architecture.**
Every circuit in the family is four independent parallel channels `gun_i → (gate_i) → out_i` — no edge addition, no
edge removal, no delay change, no redundancy, no feedback, no cross-channel coupling. **`A` has never been tested
against a real architectural difference, and a finer tolerance would have had nothing to resolve.**

**NEXT AUTHORIZED ACTION:** build a **verified circuit library with genuine topological contrasts**, each circuit's
declared graph **empirically verified against the dynamics** by privileged knockout, each layout passing the
viability assertion. Only then may EXP-GT-A-CERT derive a resolution — in **causal-graph space** (smallest
detectable edge edit / delay change / redundancy change), **never in column-distance space**.

## D-054 — A verified GoL architecture library with genuine topological contrasts. SETTLE=400 was never settled.

**Date:** 2026-07-13
**Status:** INSTRUMENT PREREQUISITE BUILT. EXP-SC-01 remains BLOCKED.

D-053 showed the benchmark contained exactly **one** causal architecture (four independent parallel channels) drawn
at three spacings — so `A` had **nothing to resolve**. This supplies what was missing. Every primitive was found
**empirically** and locked by tests; none is taken from Game-of-Life folklore.

**Verified primitives.** A **delay edit**: a gun moved by (k,k) keeps its diagonal, so the output *column* is
identical, but the stream arrives **exactly 4k steps earlier** (finest edit: 4 steps). A **cross-stream
inhibitor**: an SW (column-mirrored) gun's stream *mutually annihilates* an SE stream — both are consumed, nothing
reaches the output — which adds a genuine edge **and**, emergently, a **shielding edge**: the inhibitor stream is
consumed by its target, so ablating the target's gun frees it to travel on and kill the *next* channel. **A naive
declared graph misses that edge; the measured graph finds it.** An **inert block** (output bit-identical), a
**decoy eater** (gate-like density and appearance, off-track, causally silent — the trap for any observer keying on
looks instead of causation), and a **redundant two-path**.

**CROWN CASE: `GATE3` (a channel closed by a memory gate) and `XINHIB` (the same channel closed by a cross-stream
inhibitor) produce a FRAME-FOR-FRAME IDENTICAL output series** (mean 1.9967, |FFT| distance 0.000000) **with
completely different causal graphs.** `F` cannot separate them. Only causal tomography can.

**Two independent paths to every graph.** `predict_active()` derives it from **geometry**; `measured_graph()`
derives it by **intervention**. They share no code and must agree **edge-for-edge**, or the circuit is **rejected**,
not patched. This differential check caught **three of my own bugs**: an SW gun whose bounding box **overlapped**
gun3 (so ablating one mutilated the other — no component-overlap assertion had ever existed); a delay edit on an
*interior* channel that closed the 4-column gap to its neighbour and **killed the circuit while remaining perfectly
"periodic"** (an empty grid is periodic); and a redundant-path edge the geometry missed.

**DISCLOSED DEFECT INHERITED FROM EXP-GT-02/02B: `SETTLE = 400` was described as "a common established state". It is
not.** These circuits are still transient at t=400 and become exactly periodic (grid period **60**) only from ~700.
`SETTLE` is now **720**. The S/F/L heads are **preserved exactly**; this is a protocol correction, not a retune.

14/14 architectures admitted (viable, non-overlapping, both graph paths agreeing). 21 tests.

## D-055 — EXP-GT-A-CERT: A is CERTIFIED in causal-graph space. Resolution 4 steps / 1 edge / 1 node. Program-invariance is VACUOUS here.

**Date:** 2026-07-13
**Status:** **QUALIFIED — on development data.** EXP-SC-01 remains **BLOCKED** (held-out evaluation not yet run).
**Run:** `results/EXP-GT-ACERT-20260713-001`. Certificate: `docs/ARCHITECTURE_RESOLUTION_CERTIFICATE.md`.
Contract: `docs/OBSERVABILITY_CONTRACT.md`. S (D-051), F and L (D-052) **preserved exactly**. D-046 unchanged,
D_int untouched. **No head was tuned to pass a case; no threshold was derived from a held-out circuit.**

**The blind head sees only raw frames, its own interventions, and the declared output line.** It recovers the hidden
causal graph of every development circuit — including the **emergent shielding edge** that the hand-written wiring
diagram did not contain.

**DERIVED TOLERANCE = 0 steps.** Across all eight development nulls — clock phase (+15/+30/+45), translation
(+10/+20), spacing (40→45), inert decoration, and decoy eaters — the maximum delay deviation is **zero**.
**false-DIFFERENT: 0/8. false-SAME: 0/8.**

**CERTIFIED RESOLUTION: delay edit 4 steps** (the finest the substrate admits) · **edge edit 1** · **node edit 1** ·
**redundancy change detected** · **component separation limit 4 cells**.

**All three verdicts fired correctly.** Starved of coverage, `A` returns **INDETERMINATE**, not SAME: an output that
is demonstrably live and whose cause was never found is *missing evidence, not evidence of sameness*.

**ONE PREREGISTERED REPAIR CYCLE, on development data only, and it is disclosed.** The first certificate FAILED:
false-DIFFERENT 2/8, false-SAME 1/8, resolution 8 steps. Two defects, both in the estimator, both visible **only
because the null was measured rather than assumed**:
1. **The delay estimator was phase-dependent.** Ablating at *t*=0 destroys whatever is in the box *at that phase*,
   so a naive "first frame the output changes" onset swung by **15 steps** (214 vs 229 under a half-period shift).
   A causal delay is a property of the **path**, not of when we happened to strike it — it is now the **earliest
   onset over a full cycle of strike phases**. The null deviation fell from 15 to **0**.
2. **Floor-quantizing a delay is not "within tolerance".** 214 and 229 differ by 15, but with tol = 15 they land in
   buckets 13 and 14 and the head called them DIFFERENT. **A boundary between two buckets is not a tolerance.**
   Delays are now compared **pairwise** after the components are matched by edge structure.

**A REAL CONFOUND, CORRECTED — and it invalidates naive ablation tomography.** A destructive **micro**-ablation does
not *remove* a component; it can **REPLACE** it. A 5×5 tile cleared inside a Gosper gun does not delete the gun — it
**mutilates it into a different working machine** that emits a stream down a new diagonal, arriving at output
columns that carry nothing in the intact circuit (measured: 55–58, 95–98, 135–138). The first tomography inferred a
graph of a system **that never existed**: 20 spurious "components" for a 4-component circuit, with edges in which
*deleting matter made an output rise*. **Interventions are now applied at the scale of a DISCOVERED COMPONENT and
must be PROVED clean** (efficacy, specificity, non-shattering, non-overlap). An intervention that fails verification
is **CONFOUNDED and excluded** — not quietly used anyway.

**Also corrected: an abstention caused by the observer's own impatience is not honest uncertainty.** The
non-shattering test initially fired at *t* = OBS, before a freed stream had time to refill the pipeline to the
boundary — flagging **two perfectly clean ablations as confounded**. Periodicity is now judged after a full
re-settle.

**NOT CERTIFIED — and this is the most important line in the certificate.**
**`A`'s invariance to a PROGRAM change is NOT CONSTRUCTIBLE on this substrate.** In this circuit family a memory bit
of 0 is implemented by **ADDING AN EATER**, so setting a bit adds a node and two edges: **the program IS the
architecture.** "Same architecture, different program" **cannot be built here**, and any head that "passes"
program-invariance in this family passes a test that **cannot fire**. **EXP-GT-02B's A head passed it by comparing
channel POSITIONS, which no program can move — that PASS is hereby marked VACUOUS.** Certifying that `A` ignores the
program requires a substrate whose memory is a **STATE of fixed wiring** (a latch or storage loop), not a component
that appears and disappears. **This is a required property of the next benchmark and it is on the benchmark card.**

Also not certified: component separation ≤ 4 cells (matter closer than this merges); redundancy with identical `F`
(not realizable without a glider reflector — the redundant path doubles the stream rate, disclosed not faked); and
**held-out generalization, which has not been tested.**

**NEXT AUTHORIZED ACTION:** EXP-GT-03 — quarantine every inspected circuit as `DIAGNOSTIC_ONLY`, generate entirely
new held-out families with a frozen manifest and hashes and executable leakage assertions, **freeze every head**,
and evaluate the full factorized observer prospectively. **EXP-SC-01 stays BLOCKED.**

## D-056 — EXP-GT-03: the frozen observer FAILS prospectively. The development null could not fire. Hold-outs quarantined.

**Date:** 2026-07-13
**Status:** **FAILED — IMPLEMENTATION.** EXP-SC-01 remains **BLOCKED**. D-046 unchanged, D_int untouched.
**Run:** `results/EXP-GT-03-20260713-001`. Manifest `docs/GROUND_TRUTH_SPLIT_MANIFEST.json` (hash 308268400dd3ac49).
Card: `docs/BENCHMARK_CARD.md`. **No head was retuned. The failure is preserved.**

The observer was **frozen** (`A_DELAY_TOL = 0`, derived from the development null, D-055) and evaluated on held-out
families sharing **no** layout, spacing, program word, clock phase, topology instance or component implementation
with development — `assert_no_leakage()` proves it executably.

**IT PASSES** translation, layout change (sp48 vs sp43), inert circuitry, decoy gates, a delay edit on an **interior**
channel (an edit the development layout physically cannot host), node addition (six channels), exact copy, and `L` on
all three regimes including correct **INDETERMINATE** on observationally identical data. `F`, `M` and `G` pass every
case. E1's assertions all hold (764 frames differ, incumbent gone, relief established 7/7, **I/O identical at every
timestep**), and E2 breaks F for 264 steps and recovers.

**IT FAILS on three, and the first one is the lesson of the session.**

**1. `A` IS NOT PHASE-INVARIANT ON UNSEEN PHASES — AND THE DEVELOPMENT NULL COULD NOT HAVE CAUGHT IT.**
The delay estimator strikes at phases **(0, 15, 30, 45)** and takes the earliest onset. The development phase-null
used **THE SAME FOUR PHASES.** The estimator's sampling grid and the null's test grid **coincided**, so the null was
structurally incapable of detecting that the strike grid is too coarse. On the held-out phases (7, 22, 37, 52) —
disjoint **by design of the split** — every delay moves **214 → 222**, and `A` reports **DIFFERENT on a pure phase
shift**: the exact false-DIFFERENT the certificate reported as **0/8**.

**The certificate was not wrong; it was uninformative, and it could not know.** This is the project's own D-035 rule
turned on its author: **a null that cannot fire is not a null.** The held-out set caught it in one run. *This is
what held-out evaluation is for, and it is the strongest argument in the whole session for never certifying an
instrument on development data alone.*

**2. `A` OVER-ABSTAINS, in contradiction of its own contract.** It returns INDETERMINATE if **any** intervention is
confounded. `OBSERVABILITY_CONTRACT.md` says a confounded intervention is **"excluded from the evidence"** — not
that it invalidates the graph. On held-out cross-inhibitor circuits the collision remnant cannot be cleanly ablated,
so `A` abstains **even though it recovered the correct graph and coverage was complete** (`uncovered = []`). Two
cases lost, including the crown case. **The code does not implement its own preregistered spec.**

**3. A DELAY-PRESERVING E1 IS NOT CONSTRUCTIBLE, so the E1 expected label was WRONG — a D-053-class error, mine.**
The handoff installs the relief 12 rows upstream, which **changes the component's causal delay** (184 → 229). A delay
is part of the causal graph, so a handoff that MOVES a component **is** an architectural change and **`A` is RIGHT to
call it DIFFERENT.** The expected label is corrected: the case is a **DISPLACED handoff**, not an E1. A true E1 needs
an in-place material swap, and the only clean unseen absorber (the LOAF) is a **reactive seed**, not a still life,
which cannot be installed into a running stream.

**A CIRCUIT WAS REJECTED BY THE BENCHMARK'S OWN ADMISSION CRITERIA, and that is the machinery working.** The LOAF
gate's declared graph (`gate3 → out[164]`) is **not** the graph the dynamics realizes (measured: no such edge), so
`assert_graph_agrees` rejected it. Grading a head against it would have been grading against a mislabelled case —
the precise error D-053 exists to prevent. **Consequence: there is NO validated held-out component implementation.**
BOAT, SNAKE and BEEHIVE all absorb cleanly **in isolation** and then **destroy the neighbouring channel** in the real
circuit; on the last channel there is no neighbour, so the isolated test passes. **A component validated in isolation
is not a validated component** — the same error as the dead sp36 layout (D-053) and the overlapping SW gun (D-054).

**QUARANTINE.** The EXP-GT-03 held-out families have now been inspected while diagnosing these failures. They are
**`DIAGNOSTIC_ONLY — NOT ELIGIBLE FOR FINAL EVIDENCE`**. Their results are preserved; none may certify anything.

**NEXT AUTHORIZED ACTION — one preregistered repair cycle, on DEVELOPMENT DATA ONLY:**
1. make the delay estimator's strike phases cover the **full grid period**, so the estimator's sampling grid can
   never again coincide with the null's test grid — **and preregister a phase null whose phases are DISJOINT from the
   estimator's, so that it CAN fire**;
2. make `head_A` implement its contract: **exclude** a confounded locus from the evidence; abstain **only** on
   insufficient coverage;
3. **generate entirely NEW held-out families** (the current ones are burned);
4. re-freeze and re-run as **EXP-GT-03B**. **If the repaired observer still fails, RETIRE this observer design and
   build a conceptually different one.**

**EXP-SC-01 remains BLOCKED. No composite. No head tuned to pass. S/F/L preserved exactly.**

## D-058 — EXP-GT-03R: the repaired A head FAILS prospectively. **A-HEAD V3 IS RETIRED.** Not patched.

**Date:** 2026-07-14
**Status:** **FAILED — GROUND-TRUTH GENERALIZATION → RETIRED.** EXP-SC-01 remains **BLOCKED**.
**Run:** `results/EXP-GT-03R-20260714-001` (manifest `f321ddbba18d8f49`, leakage NONE).
Everything is **preserved**: V2, V3, both certificates, both sets of contaminated hold-outs, every failure.
**No head was retuned. No threshold was lowered. The failed hold-outs will not be reused.**

This was the **one authorized repair cycle** for the ablation-tomography A design. It failed. Under mission §8 the
design is **RETIRED**, and a conceptually different observer is authorized without further permission.

### What passed, and it is not nothing

On entirely new hold-outs (layouts sp42/sp46/sp50, spacings 42/46/50, programs 1011/0110, phases 27–55, delay
patterns k=5/k=7, five-channel topology), the frozen V3 observer got **right**: layout change, phase shift, inert
decoration, node addition, a different-topology/same-F pair, exact copy, **E1 in full** (A_TOPO=SAME, A_TAU=DIFFERENT,
G=DIFFERENT, F=SAME, M=DIFFERENT, L=SAME — with every assertion firing: 864 frames changed, incumbent gone, relief
established, **I/O identical at every timestep**, no exact restoration), **E2**, **L** on all three regimes, and **S**
(preserved exactly, D-051). **F, M and G passed every single case.**

The **A_TOPO/A_TAU/G ontology (§2) is NOT retired.** It is vindicated: separating topology from timing is what let
E1 be labelled correctly at last — a handoff that *moves* a part preserves connectivity and changes path length, and
D-056 had scored the head wrong for saying so.

### The three failures — all one disease

**1. THE INTERVENTION'S VALIDITY IS PHASE-SENSITIVE, AND THE CERTIFICATE COULD NOT SEE IT.**
Clearing a component's box for `HOLD` steps clips an in-flight glider at some strike phases and leaves a block.
Measured on the **development** circuit — the one the certificate certified — **6 of 60 clock phases (2, 3, 5, 32,
33, 35) make every intervention unusable**: at phase 33, `valid=0, confounded=4`. The head detects this and abstains,
which is *correct*; but it therefore **cannot identify the architecture at 10% of phases**, and three held-out cases
came back INDETERMINATE where the evidence should have been decisive.

**2. THE "INDEPENDENT" NULL GENERATOR WAS ITSELF BIASED.** `gt_nulls.draw_phase_nulls` did
`sorted(set(lcg(...)))[:n]` — **sorting and truncating**, which keeps only the smallest draws. The raw LCG produced
31, 48, 33, 58; the generator returned `[1,4,6,8,9,10,11,14,16,17,20,23]`, **all ≤ 23**. The bad phases at 32/33/35
were **unreachable by construction**. I wrote a module whose entire purpose was independence from the estimator, and
put a bias in the sampler. **The third instance in this project of: the test and the thing tested were not
independent.**

**3. A_TAU CANNOT RESOLVE A DELAY EDIT ON A GATED PATH — AND THIS IS THE DEEPEST RESULT OF THE SESSION.**
Move a gun 5 rows along its own diagonal on a *gated* channel. The evaluator measures the gate→output causal delay
moving **184 → 164** — a real 20-step change of causal timing. The blind head reports **median 185.5 in BOTH
circuits**. A **false-SAME on the certified edit scale**.

The cause is not a bug. It is the repair itself. **D-056 failed because the delay estimator was phase-sensitive, so
V3 made it phase-invariant by taking the MEDIAN OVER ALL 60 STRIKE PHASES — i.e. by integrating the phase out. For
an edge whose onset is gated by a periodic arrival, that marginal is invariant to exactly the quantity it is meant to
measure.**

> **The cure for a nuisance parameter is not always to integrate it out. Integrating it out can integrate out the
> signal along with the nuisance.**

V3 resolves a delay edit on an **ungated (source)** edge — the k=7 case passed. It is blind to one on an **inhibitor**
edge. The information is *present* (after the gate is removed, channel 1's stream reaches the output at a shifted
phase **relative to the other channels**) — but every V3 summary (median onset, |FFT| magnitude) **discards relative
phase**. So it is a head limitation, **not** a fundamental non-identifiability, and mission stop-condition 2 does not
apply.

### RETIREMENT

**A-head V3 (ablation tomography with box-clearing, per-component validity, and phase-marginalized timing) is
RETIRED.** `edlab/identity/blind_a3.py` is preserved unchanged and marked RETIRED. It will not be patched.

**What is retired:** the *estimator* — destructive box-ablation whose cleanliness is a hostage to the microstate at
the moment of the strike, per-component (not per-phase) validity, and timing represented as a phase **marginal**.
**What survives:** the **ontology** (A_TOPO / A_TAU / G, never composited), the observability contract, the
whole-component specificity rule, the two-level coverage rule, and the E1/E2 expected-vector spec.

### NEXT AUTHORIZED ACTION — a conceptually different observer, no permission required (§8)

**ARCHITECTURE HEAD V4**, preregistered in `docs/ARCHITECTURE_HEAD_V4_SPEC.md`, restarting certification from
must-pass/must-fail cases — including the two that killed V3 (**strike phase 33**, and a **delay edit on a gated
path**). Its three conceptual changes:

1. **Validity is PHASE-RESOLVED.** Each `(component, strike-phase)` pair is graded independently; the graph is built
   from the valid pairs. A phase at which the probe misbehaves costs that phase, not the whole circuit.
2. **DO NOT INTEGRATE OUT THE NUISANCE — QUOTIENT BY IT.** Timing is the full phase-resolved response profile
   `τ(φ)`. A global phase shift acts on the data as a **common cyclic rotation of every edge's profile**. So
   invariance is obtained by **quotienting by that group action** (comparing profiles up to a *common* shift, e.g.
   via their pairwise differences), never by averaging. A *relative* timing change is not a group element and
   therefore **survives**.
3. **The null generator is rebuilt** with an executable uniformity/coverage assertion, because the old one was
   biased and that bias is not inherited.

**EXP-SC-01 remains BLOCKED. No composite. S, F and L preserved exactly.**

## D-060 — EXP-GT-03R2: architecture head V4 QUALIFIES prospectively. EXP-SC-01 still BLOCKED (hierarchy not run).

**Date:** 2026-07-16
**Status:** **QUALIFIED** on a third, entirely-new hold-out split. **EXP-SC-01 remains BLOCKED** — mission §11
requires the hierarchical discovery benchmark, and it has not been run.
**Run:** `results/EXP-GT-03R2-20260716-001` (manifest `e7e9955892e0495c`, leakage NONE).
Everything preserved. **No head retuned. TAU_TOL frozen at 0.0, derived from the coverage-asserted independent null.**

The split touches **neither** burned hold-out set (EXP-GT-03's, burned diagnosing D-056; EXP-GT-03R's, burned
diagnosing D-058) on any axis: spacings 44/47/52, programs 0111/1001, phases 19/26/43/51/58, delay patterns
(ch2,k=4) and (ch1,k=6), a five-channel topology, a new perturbation schedule, a new seed.

**RESULT: 0 head failures.**

| | |
|---|---|
| 12 pairwise cases (layout · translation · phase · **delay edit on an ungated path** · **delay edit on a GATED path** · different-topology/same-F · edge added · node added · inert decoration · program word · exact copy) | **12/12** |
| **E1-B** — function-preserving handoff, fresh configuration, head run **exactly once** | **6/6** — `A_TOPO=SAME, A_TAU=DIFFERENT, G=DIFFERENT, F=SAME, M=DIFFERENT, L=SAME` |
| E2 — damage and repair | fires (311 timesteps broken) and recovers |
| L — three regimes | **3/3**, including correct **INDETERMINATE** on observationally identical data |
| S — the certified D-051 probe, preserved exactly | correctly reports **OUT_OF_SCOPE** for layouts outside its scan window |

**The case that killed V3 now passes prospectively.** A delay edit on a **gated** path — where V3 returned a
false-SAME on its own certified edit scale — gives `A_TOPO = SAME, A_TAU = DIFFERENT`. **Quotienting by the phase
group recovers exactly the signal that marginalizing over it destroyed.**

### Two things I must not paper over

**1. THE FIRST HELD-OUT E1 WAS OUT OF SCOPE, AND ITS REBUILD IS DIAGNOSTIC, NOT PROSPECTIVE.**
I placed the E1 relief **one row** from gun0 — inside the head's **certified component-separation limit of 4 cells**
(D-057/D-059). The head merged them and reported a different topology. **That is a split-design error of mine, not a
head failure**: I graded the instrument on a case its certificate says *in advance* it cannot resolve — the same
mistake as putting a held-out layout outside `S`'s scan window. I rebuilt the case in scope and it passed. **But a
held-out case that has been inspected and re-designed after its failure is no longer prospective evidence, whatever
it says afterwards.** That E1 is marked **DIAGNOSTIC_ONLY**. The prospective E1 claim rests **only** on **E1-B**, a
fresh configuration (sp47, channel 2), in scope by construction, on which the head was run **exactly once**.

The line drawn, and it is the honest one: **I may search the PHYSICS to build a valid handoff** (does the relief
establish? is the I/O unbroken? — ground-truth facts, checked by assertions). **I may not search the HEAD'S ANSWER.**
No head is consulted anywhere during construction.

**2. THE HEAD HAS NO SCOPE SELF-CHECK. It silently merged two components and emitted a confident verdict.**
V4 declares a component-separation limit of 4 cells but **never checks that the data respect it**. When two
components fall inside the limit it merges them and reports DIFFERENT — a **fabricated certainty**, which the
observability contract forbids. It should return INDETERMINATE.

**This is NOT patched.** Patching an estimator after a prospective run is exactly what §8 forbids, and — this is the
test of whether the rule is being obeyed honestly — **fixing it could not rescue any case anyway**: it would only
turn DIFFERENT into INDETERMINATE, and E1's expected label was SAME. It is recorded as a **required property of the
next head**, with an executable scope assertion now guarding every benchmark case.

### Still NOT available, unchanged

**HELD-OUT COMPONENT IMPLEMENTATION: NOT AVAILABLE → subclaim INDETERMINATE.** Every candidate clears exactly one of
the two bars. BOAT/SNAKE/BEEHIVE pass in isolation and **destroy the neighbouring channel** in context. LOAF/EATER2
pass the behavioural bar — EATER2 even reproduces the development gate's output line **bit-for-bit** at spacings
42/46/50 on middle channels — and fail admissibility: both are **reactive seeds**, not still lifes, so their declared
component is empty at settle and `assert_graph_agrees` rejects them. §5.1 forbids manufacturing evidence by reusing a
development component at a new position, **so I did not**.

**Required property of the next component library:** a **still-life** absorber, distinct from EATER1, whose declared
footprint **is** its settled footprint. Also still required: **state-based memory** (a latch/storage loop), without
which `A`'s program-invariance is not constructible; and a **causal cycle**, without which feedback is not testable.

### NEXT AUTHORIZED ACTION

**EXP-GT-HIERARCHY-00** (mission §9): blind hierarchical discovery from raw trajectories and self-chosen
interventions — micro-patterns, velocities, channels, clock, gates, memory, program, I/O, FSM, macro causal graph,
with counterfactual validation and calibrated abstention. **Not started.** **EXP-SC-01 stays BLOCKED until it passes.**

## D-063 — EXP-GT-HIERARCHY-00: the three addenda QUALIFY. Blind discovery FAILS prospectively. Hold-outs burned.

**Date:** 2026-07-18
**Status:** **addenda QUALIFIED · discovery FAILED — DISCOVERY.** EXP-SC-01 remains **BLOCKED**.
**Run:** `results/EXP-GT-HIER-20260718-001`. Everything preserved. V4, admission, S/F/L/M/G all untouched.

### The three binding addenda: ALL PASS

**A1 — admission is SCALE-RELATIVE.** The 4-cell De Morgan gate, taken as **one composite macro-object**, is
**ADMITTED** even though its internal NOTs have distinct internal effects — *that is what being made of parts
means*. Two gates with **different external interfaces** forced into one object are **OUT_OF_SCOPE**: a sub-part
leaking an interface the parent does not have is the merged-blob signature, one level up. **D-061 is re-read, not
revised: it certified admission at the ELEMENTARY-COMPONENT level, and it remains valid there.**

**A2 — architecture is MULTI-SCALE.** direct vs De Morgan: **DIFFERENT at micro**. At macro the observer must
**EARN** the quotient — and it correctly **REFUSES** it (`INDETERMINATE`), because the De Morgan gate has **3 steps
of latency through the object** while the direct gate has **1**; their *total* path latencies match only because
the output wire compensates. Given a **delay-matched** direct gate (AND + 2 buffers, latency 3), the observer
**establishes all three** — functional, interface **and** delay equivalence — and returns **SAME**. *The quotient
can both fire and be refused.*

**A3 — structure is CONTEXT-DEPENDENT.** With **no** discovered context the certificate returns
**`STRUCTURAL_GRAPH_INCOMPLETE`**, never a false absence. With contexts **discovered blind** (the memory
signature), the known conditional paths are revealed and the graph is **COMPLETE**. Edges carry explicit
conditions `X → Y | S=1`.

### What the blind observer actually recovered — from raw cells and its own interventions only

**Clock period · clock source · all 3 gates · all 3 registers · the write-enable · 14 components — EXACT**, on the
development worlds, with **no count hard-coded at any rung** and **no evaluator label anywhere in its path**.
It separates registers from the global write-enable **by interface breadth alone**.

### Prospective result: **FAILED — DISCOVERY**

| held-out world | T | source | gate P/R | mem R | counterfactual |
|---|---|---|---|---|---|
| p010, new layout | ✅ | ✅ | 1.00 / 1.00 | 1.00 | 0.69 |
| **p110, De Morgan** | ✅ | ❌ | **0.00 / 0.00** | 1.00 | 0.90 |
| p001, delay-2 detour | ✅ | ❌ | 1.00 / 1.00 | 1.00 | 0.69 |
| p111, feedback + decoy | ✅ | ✅ | 1.00 / 1.00 | 1.00 | 1.00 |

**1. THE GATE DETECTOR DOES NOT TRANSFER TO AN UNSEEN IMPLEMENTATION.** It finds gates as *the earliest cell in a
discovered memory's influence cone*. In the direct implementation that cell **is** the AND. In De Morgan the first
cell downstream of the register is `NOT(reg)` — which has **no output interface** under the gate-opening context —
so the detector finds **nothing**. **Gate recall 0.00 on the one held-out world with a different micro-implementation.**
It was calibrated, without my noticing, on a single gate implementation.

**2. Source detection fails** on the De Morgan and detour worlds, and **counterfactual accuracy falls to 0.69**:
predicted interfaces of memories and gates do not always match the observed set of changed outputs.

### A benchmark-label error of mine, corrected (D-053 class, again)

I scored `clock_period_correct` against the **clock cell's** period. In the world with the feedback ring the
**fundamental period of the WORLD is 24** (lcm of the clock's 8 and the ring's 3) — and the observer correctly
reported **24**. **I marked the observer wrong when it was right.** The truth is now taken from the evaluator's own
`period_of()`, not from a constant I assumed. **The observer infers the period of the world, which is the only
thing it can see, and that is the right quantity.**

### Two identifiability traps found in the substrate itself, and removed rather than papered over

- **An ablation ONSET is not a DELAY.** With a square-wave clock the first step at which an output deviates depends
  on the **phase**, not the path length: the three cells of a buffered gate reported onsets 17/17/12, giving a
  "latency" of 6 for an object whose true latency is 3. Latency is now measured by **exact series alignment**,
  which is phase-invariant. *The same disease that killed A-head V2 and V3, in a new substrate.*
- **With a 50 % duty cycle, `NOT(x)` is EXACTLY `x` delayed by half a period.** Inversion and delay become
  indistinguishable, and the De Morgan gate's latency read 7 instead of 3. This is a genuine identifiability trap
  **built into the clock**. The honest fix is to remove the degeneracy from the **world**, not to patch the
  estimator: the clock now has a **3-of-8 duty cycle**, and `NOT(x)` is a shift of nothing.

### Failure classification and next action

**Type: OBSERVABILITY / IMPLEMENTATION** — the gate detector's rule is *implementation-specific*, not a physics or
ontology failure. **Preserved. The held-out worlds are now BURNED** (`DIAGNOSTIC_ONLY`).

**ONE preregistered repair cycle is authorized, on DEVELOPMENT data only.** The gate detector must be rebuilt on a
principle that does not assume a gate implementation — e.g. **a gate is a cell with TWO causal parents**, found by
testing whether a cell's series is a lagged copy of *one* upstream cell (a wire) or a *function of two* (a gate),
under contexts that vary each parent independently. Then: **generate an entirely new held-out split** and re-run.
**If the repaired observer still fails, the discovery design is RETIRED.**

**EXP-SC-01 remains BLOCKED.**

---

## D-064 — the repair of D-063 QUALIFIES on development (EXP-GT-MODULES, 18/18)

`edlab/identity/modules.py`. The retired detector defined a gate as *the earliest cell in a discovered memory's
influence cone* — a **position**, not a computation. It is replaced by **implementation-independent causal module
discovery**: a module is the **maximal connected cluster of computing cells, bounded by conductors**, whose
boundary has ≥ 2 independently manipulable parents, and whose boundary, parents, outputs, truth table, delays and
quotient are all **inferred by intervention**.

Five findings, each of which had first appeared as a defect of mine:

1. **An ablation cannot isolate a direct edge.** Clamping one input of an AND only shows at its output when the
   *other* input is favourable, so "the child deviates one step after the parent" is phase-dependent and found the
   gate in *no* implementation. A **one-step pulse** isolates it: nothing else differs at step `t`, so whatever
   differs at `t+1` is a direct child. Sweeping `t` over a period covers every phase; the flip forces the negation
   of the cell's own value, so it is non-vacuous by construction.
2. **A structural edge can be dynamically masked** (A3). With its register at 1, `OR(x,1)` is *saturated*: the
   channel→gate edge is invisible, the gate has one parent, and it *disappears* — measured, 0 modules. The graph is
   therefore built under every discovered context and unioned, and each edge records the contexts in which it fires.
3. **A cell that is constant zero can still be a causal parent.** De Morgan's `NOT(reg)` is constant 0 while the
   register holds 1; a candidate set built from baseline activity excludes it and the OR never gets its second
   parent. A part of the machine that is quiet today is still part of the machine.
4. **Absence of evidence taken as evidence of absence.** A passive copy test on a wire whose input has gone silent
   returns "not a copy" — and made the gate's own output wire look like a computation. Polarity is now read off the
   **pulse**, which moves the parent by construction and is defined even for a register that never moves on its own.
5. **The boundary is not a growth rule.** Growing outward from a junction works on a *chain* and shatters on a
   *diamond*; which junction "won" depended on iteration order — an arbitrary answer dressed as a measured one.

Certificate: 18/18 on development circuits only. Positives fire on one-cell, 3-cell, 4-cell and **reconvergent**
gates; negatives fire on wires, on **active clock-correlated decoration**, on a cell with **three active geometric
neighbours and one causal parent**, and on `AND(x,x)` (**two incoming edges, one effective parent**). The `or_gate`
and `xor_gate` worlds emit **byte-identical output traces** at program 000 and are separated **only** by
manipulating a discovered register context. The burned De Morgan hold-out was not used as evidence.

## D-065 — the repaired design FAILS the single prospective run. **RETIRED.**

`EXP-GT-HIER-R`, 8 fresh worlds, jointly holding out topology, layout, phase (development ran *entirely* at
`clk_phase = 0`), program, module implementation and intervention schedule, including two gate implementations
never used or inspected during the repair. The frozen observer was run **once**.

**What the repair fixed, and it is real.** On the unseen implementations: gate recall **100 %** (it was 0.00),
boundary **exact 100 %** (mean IoU 1.000), parent interface **100 %**, output interface **100 %**, internal delay
**100 %**, micro cell count **100 %**. The conceptual failure of D-063 — a gate is a position — is gone.

**What it failed.** Function accuracy **50 %** on unseen implementations (75 % overall), conditional-edge accuracy
58 % on unseen, and **FALSE CERTAINTY 6/24** against a bar of **zero** that was written into the harness *before*
the run. Every failure is `xnor_and`.

**The cause, stated without reference to any of my labels.** `xnor_and`'s module is bounded by conductors, so its
boundary parents are the register, the channel's last cell, **and a re-timing buffer carrying a delayed copy of
that same channel cell**. The detector treated all three as *independent* inputs, clamped them independently —
exploring assignments the machine can never realize — and confidently reported a three-input table with no
two-input reduction. Consequently
`macro_quotient(one-cell AND, unseen xnor_and AND) = DIFFERENT / DIFFERENT`: **the observer cannot recognize an
unseen implementation of AND as the same macro object as the AND it already knows.** That was the entire purpose
of the repair.

I built the "coincident correlation" control at the **cell** level (`AND(x,x)`) and it passed. I never built it at
the **module boundary** level, and nothing in the development family had a buffer feeding a boundary. The held-out
world did — by construction, since I designed it for asymmetric input latency — and the design broke on precisely
that.

It is the same error as D-053 (two "architectures" that were one causal graph) and D-063 (a gate that was a
position): **a representational boundary mistaken for a causal one.** The conductor-bounded frontier is a graph
artefact; the module's real inputs are its independent causal *sources*.

**Per the preregistered rule, this discovery architecture is RETIRED. No second repair cycle.** No threshold is
adjusted; no implementation-specific template is added. `edlab/identity/modules.py` is preserved unchanged, and the
eight prospective worlds are **BURNED** (`DIAGNOSTIC_ONLY`).

**EXP-SC-01 remains BLOCKED.**

### Design direction for a conceptually different observer (not implemented here)

A module's interface must be its **independent causal sources**, not its conductor-bounded frontier: trace every
boundary parent back through conductors to the cell that *originates* it, and deduplicate parents that share a
source. The input space of a module is the set of assignments the machine **can actually realize** — a truth table
measured off that manifold is not the module's function, and must either be declared off-manifold or abstained
from. Independence between parents must be **tested**, never assumed from the fact that they are distinct cells.

---

## D-066 — the source-transducer observer QUALIFIES on development (EXP-GT-SOURCE, 20/20)

A conceptually new observer (`edlab/identity/sources.py`), not a repair of the retired one. The object is no longer
a box with wires. It is a **transducer from a minimal set of independent causal sources, and their histories, to an
output, measured only on the joint histories the world can actually realize.**

Four things that were previously one are now kept apart: the **spatial frontier** (geometry), a **boundary tap** (a
consequence), an **independent source** (a root — a cause), and the **reachable manifold** (what the dynamics can
produce). Interventions are applied to **sources, never to taps**: a tap is a consequence, and clamping it
fabricates a world.

20/20 on development. Three taps yield two causes (`dup_same`); a duplicated source, an inverted-delayed tap and a
history-dependent detector are all resolved to one cause; two registers with **byte-identical baseline series** are
kept independent (`and3`) while a wire and its own buffer are merged; `AND(x,x)`, active clock-correlated
decoration and a three-neighbour wire bundle are all rejected; a state machine yields `FINITE_STATE` **and no
invented table**; two modules identical on the manifold and different only off it yield **INDETERMINATE, not SAME**
(`lag8`), while two modules with **byte-identical free-running outputs** are correctly separated by clamping the
source (`lag15`) rather than abstained from. Every verdict — SAME, DIFFERENT, INDEPENDENT, DEPENDENT, UNRESOLVED,
INDETERMINATE — was shown able to fire.

## D-067 — the source-transducer observer FAILS the single prospective run. **RETIRED.**

`EXP-GT-SOURCE-P`, 8 fresh worlds, jointly holding out topology, layout, phase, program, implementation, delay
asymmetry, source-duplication pattern and intervention schedule, with four gate implementations never used or
inspected during development. Frozen observer, run once.

**FALSE ABSTENTION 12/24.** Twelve modules declared `FINITE_STATE` — *"this module remembers something I cannot
explain"* — and **not one is a state machine.** Transducer class 50 %, function on the reachable manifold 29.2 %.
The verdicts are graded exactly by distance from the clock: 0 on channel 0, 4 on channel 1, 8 on channel 2.

**The cause.** `harvest()` labels each sample's source history as `g[t − d]`. When the lag `d` exceeds `t`, the
index is negative and numpy reads from the **end** of the array. The row is labelled with a source history from a
different time — a state the world never produced. The observer whose entire thesis is *never evaluate a function
on states the world cannot realize* **fabricated source histories itself, by indexing before the beginning of
time**. Its consistency check worked perfectly: it detected the contradiction and reported hidden state. The thing
hiding state was the array index. `assert_manifold_generated` guarded the wrong side of the pair — it verified that
every row had a *generated output*, never that the row was *labelled with the history that produced it*.

**Why development missed it.** All 20 development cases inspect **channel 0 of three** — the only channel whose
clock lag falls below the settle margin, hence the only one where the defect cannot appear. A certificate that
exercises one third of the ground truth available to it is not a certificate.

**An error of mine, reported because it inflates the failure rather than excusing it.** On closed-gate channels the
observer named the **write-enable rail** as the second source instead of the register — and it is *right*: pulsing
`we` makes the register load, and `y = clk AND we` is a correct, complete description at coverage 1.0. My
`truth_sources` had filtered that cell out as an "inert rail", a justification I wrote **in order to make the ground
truth produce the source count I expected**. That is the D-053 error, committed by me, in the scorer, after
everything. It means part of the scored false certainty is mine — and it changes nothing: the 12 false abstentions
are real and fail the run on their own.

**RETIRED per the preregistered rule.** Preserved unchanged, not patched, no second cycle.
Classification: **MANIFOLD IDENTIFICATION** (primary), with a **SCOPE CALIBRATION** failure in my own verification.
**Not** source discovery: source counts were 95.8 % correct and every uncorrupted channel was classed correctly.

**EXP-SC-01 remains BLOCKED.**

### Next strategy

An **active experiment-planning observer** that chooses interventions to maximise causal identifiability instead of
executing a fixed tomography schedule — and that, before estimating any function, proves that every feature it uses
was **observed inside the window it claims to have observed it in**. Two standing additions to the method,
independent of any observer:

1. **A certificate must exercise every instance the world offers, not the most convenient one.** Channel 0 was
   easiest to write and is the only channel that could not fail.
2. **An assertion must guard the side that can be wrong.** "Every row was generated" was true, and useless.

---

## D-068 — the ACTIVE causal observer QUALIFIES on development (EXP-GT-PROV 20/20, EXP-GT-ACTIVE 15/15)

Two contracts were built **before** the observer that depends on them.

**TEMPORAL PROVENANCE (`provenance.py`).** A feature is not a number; it is a claim — *"at time t−d, in episode e,
source s held value v"* — and every claim is **re-read from the episode and compared byte-for-byte**. `_idx()`
REFUSES a negative index rather than wrapping. The window is sized to the widest hypothesis the observer will
**test** (`max_lag + MAX_HISTORY`), and sampling begins at `max(margin, max_lag)`, not at a constant chosen in
advance. 20/20, including the D-067 defect injected and caught three separate ways.

**GROUND-TRUTH CAUSAL AUDIT (`audit.py`).** A variable is causal if an admissible intervention on it changes the
downstream distribution — even if it is silent in the baseline. The write-enable rail **is** a cause; the
privileged source set is program-dependent. Two paths (declared wiring, intervention-derived) must agree or the
world is rejected before the observer sees it.

**THE OBSERVER (`active.py`).** It plans. It holds a lazily-refined version space, predicts what each admissible
regime would reveal *before paying for it* (possible because the sources are roots), executes the most informative,
and then **validates by predicting a regime it has never run**. A regime whose outcome is already known is
inadmissible — not caution, but expense. Development: 15/15 across **45 transducers, exactly 15 per channel** —
unlike the certificate that missed D-067, which inspected channel 0 of three. Cost 150/306 episodes (49 %), with
6 distinct exploration plans across 15 worlds.

## D-069 — the active observer FAILS the single prospective run. **RETIRED.**

8 fresh worlds, jointly holding out topology, layout, program, phase, implementation, **channel distance**, source
duplication, delay asymmetry and context schedule; four implementations never used or inspected. Run once.

**What it established, prospectively, on unseen implementations:**
independent source **count** 100 % · source **identities** 100 % against the privileged audit ·
**function on the reachable manifold 100 %** against privileged simulation · hidden state claimed on exactly the
two true state machines and nowhere else · partial manifold correctly returned as `EQUIVALENCE_CLASS_ONLY` ·
**0 fabricated provenance rows, 0 excluded rows, and NO degradation from lag 17 to lag 56.**
**The D-067 defect is definitively gone.**

**What failed: transducer CLASS, 21/24.** All three failures are `xor3`, whose output gate reads its two inputs at
different depths. The observer measured both clock lags — correctly — and its table agrees with the privileged
simulation on **every row**. But the second lag is **functionally redundant**: the minimal model is
`DELAYED_STATIC` with one lag, and it reported `FINITE_HISTORY` with two.

> **The version space only ever WIDENS.** On contradiction it escalates to a longer history. It never asks the
> opposite question — *is this lag necessary?* — so it returns a correct model with too many arguments and derives
> the wrong class from it. §7 asks for the smallest predictive representation; a search that only grows cannot find
> one.

**And my scorer was wrong for the third time.** `TRUE["xor3"]` was a lambda hand-declared from the circuit I
*intended* to build, not the one I built. §2 required an intervention-derived second path for every claimed
function and I built it only for the sources; under my own contract that world should have been rejected before the
observer ran. Scored correctly, the observer's function accuracy is 100 % — my defective scorer flagged the right
rows for the wrong reason. It does not rescue the design (the class bar fails on the correct ground truth too), but
it is on the record: three observers retired, and in **two** of them my own evaluator was independently wrong, each
time in the direction that made the ground truth produce the number I expected.

**RETIRED per the preregistered rule.** Preserved unchanged, not patched, no second cycle.
Classification: **TRANSDUCER INFERENCE / MODEL MINIMALITY.** Not source discovery, not manifold identification, not
temporal provenance, not scope calibration.

**Per §13, automatic construction of further observers STOPS.** The programme-level synthesis of what is and is not
identifiable is in `docs/PROGRAMME_SYNTHESIS.md`. **EXP-SC-01 remains BLOCKED** — through three observers, and
blocking it was right every time: each would have produced a confident, wrong description of an unknown world.

---

## D-070 — programme-level synthesis. Capability matrix; R8-B-dynamic does not require minimality; Route B is legitimate **conditional on repertoire-limited transfer**. STOP for strategic review.

**Scope of D-069, restated exactly.** `FAILED — IMPLEMENTATION / MODEL MINIMALITY`, with an independent
evaluator-ground-truth defect of mine. The active observer is retired under its **full-hierarchy criterion**. The
causal source–transducer **ontology is not falsified**. **It predicted every measured function correctly** and
**failed the preregistered minimal-representation criterion** on 3/24. It is not fully qualified, and it did not
fail to understand the prospective worlds.

**Prospectively DEMONSTRATED (G6, frozen, run once, against a privileged intervention-derived audit):** causal
source recovery (count 100 %, identities 100 %) · temporal provenance (0 fabricated rows, 0 excluded rows, no
degradation from lag 17 to lag 56) · reachable-manifold function (100 % vs privileged simulation) · hidden-state
detection (6/6, on the true state machines and nowhere else) · calibrated abstention · active experiment planning
(49 % of an exhaustive schedule on development; the plan is a function of the world).

**FAILED:** minimal transducer-class identification — 3/24 — because the search can widen but cannot **eliminate a
redundant history variable**. Full capability matrix across all seven observer generations, with every capability
marked `QUALIFIED` / `DIAGNOSTIC ONLY` / `FAILED` / `UNTESTED`: `docs/CAPABILITY_MATRIX.md`.

### The strategic question

**Does R8-B-dynamic require a provably minimal causal model, or only a stable, discriminative causal-response
fingerprint?**

**It does not require minimality.** Minimality is a property of a **description**; R8-B is a **matching problem**
over **responses**. Two descriptions that are observationally equivalent on the reachable manifold predict
identically — which is precisely the D-069 failure: the `xor3` table was right on every row and only the *class
label* was wrong. A response-based fingerprint is invariant to that error by construction; a fingerprint carrying
class labels or lag sets inherits it and would manufacture **false DIFFERENCE**.

Four binding conditions: **(C1)** response-only — no class, lag set, arity or minimality quantity may enter;
**(C2)** the active planner is switched **OFF** inside the fingerprint (a coordinate system that adapts to the
thing it measures is not one) and used only to design a frozen battery on ground truth; **(C3)** timed and untimed
components reported separately, never composited; **(C4)** SAME is never claimed — only
`INDISTINGUISHABLE-UNDER-REPERTOIRE`, above a preregistered coverage floor.

### Routes

**Route A** (block until a bidirectional grow-and-prune observer exists) remains **mandatory** for any claim of
architecture, minimal structure, or "the same individual" — and is **not compelled by this use case**. Building it
to satisfy R8-B would be scope creep driven by the benchmark rather than the question.

**Route B** (narrow prospective qualification of the frozen causal-response layer) is **logically legitimate**,
using only prospectively qualified capabilities and excluding model class and minimality completely.

**Specified, NOT executed: `EXP-GT-FINGERPRINT-00`** — a NEW prospective claim, not a post-hoc rescue. Invariance
under redundant lags, retiming, microscopically different implementations, channel distance, and **progressive
implementation replacement mid-trajectory** (the Ship-of-Theseus arm — the direct analogue of R8-B's early/late
split under constituent turnover). Discrimination of different functions, source counts, true hidden state and
context-gated paths. **Mandatory abstention** on the off-manifold twins. And a **must-fail case (F11)**: a
deliberately contaminated fingerprint carrying the class label must be shown to break — otherwise C1 is decoration.

### THE HARD GATE — and it is where this most likely stops

Ground truth offers **rich** intervention access. The droplet offers almost none. A qualification obtained under
rich access transferred to a poor one would be the same category of error as every retirement in this programme.
**`EXP-GT-FINGERPRINT-00` must therefore contain a REPERTOIRE-LIMITED ARM**, crippled to droplet-like access, and
the fingerprint must qualify **there**.

- qualifies only under rich access → **transfer NOT authorized; continued blocking; end of route.**
- qualifies under the limited repertoire → **and only then** → `SC-PILOT-CAUSAL-FINGERPRINT` may be defined:
  explicitly **exploratory**, the R8-B matching statistic **unchanged** on a fingerprint feature space, with
  **β = 0.10, `D_int` and every droplet equation untouched**. A PASS would authorize one sentence — *"a
  causal-response fingerprint is predictive across the early/late split under repertoire R at coverage c"* — and
  **could not be called proof of identity**, nor a GATE-0, nor a law-map step. A FAIL would be a **stronger
  negative** than the phenotype-based R8-B failure and would close the question.

**Dominant risk: FALSE SAMENESS.** A poor repertoire yields a small reachable manifold; on a small manifold
genuinely different entities collapse into one fingerprint — and the collapse would present itself as *"identity
persists"*, which is the answer this programme has an interest in seeing. That is the failure mode most likely to
fool me, and §6 of the synthesis exists to catch it.

**Route B is not recommended in order to resume droplet experiments.** If the repertoire-limited arm fails, the
correct outcome is continued blocking and a publication-oriented metrology synthesis.

**NOTHING EXECUTED. NO OBSERVER BUILT. NO RETIRED IMPLEMENTATION MODIFIED. EXP-SC-01 REMAINS BLOCKED.
STOPPING FOR STRATEGIC REVIEW.**

---

## D-071 — scope clarifications appended (two capabilities that do not travel)

**1. Temporal provenance is qualified ONLY for the certified Boolean-world pipeline and its executable provenance
contract.** The 20/20 certificate is a statement about `provenance.py`, `Episode`, `_idx` and the assertion that
re-reads every source sample from its own episode — not about any other substrate's data path.

**2. Exact direct-edge recovery is established ONLY in the synchronous Boolean substrate under one-step pulse
access.** "Flip a cell at step t and whatever differs at t+1 is a direct child" is a theorem about a synchronous,
discrete, unit-delay rule with arbitrary single-cell write access. A droplet is continuous and diffusive; there is
no "one step later", and no experimenter flips one lattice site of its interior.

**Neither is assumed to transfer to droplets.** Any droplet claim must re-earn both under that substrate's own
access constraints.

## D-072 — EXP-GT-FINGERPRINT-00: **BOTH ARMS PASS PROSPECTIVELY.** SC-PILOT-CAUSAL-FINGERPRINT authorized (exploratory), NOT executed. EXP-SC-01 remains BLOCKED.

**The claim, and nothing wider:** a frozen, standardized causal-response fingerprint remains **stable** under
microscopically different but behaviourally equivalent implementations while **distinguishing** systems that differ
in reachable function or genuine hidden state. Model minimality, architecture discovery and lineage identity are
**outside** the claim. The instrument **never says SAME**: its verdicts are `INDISTINGUISHABLE_UNDER_REPERTOIRE`,
`DIFFERENT`, `INDETERMINATE`.

**Development: 18/18, both arms.** Continuity distances **exactly 0.0000**; a real gap in each arm.
**Prospective: 9/9, both arms. Zero false difference. Zero false sameness.** Seven of ten systems use
implementations never fingerprinted; topologies and phases used in no development world. **The droplet arm
qualified INDEPENDENTLY** — a rich-access pass could not have authorized transfer, and did not have to.

**E1, the Ship-of-Theseus arm:** two microscopically different AND implementations, **swapped mid-trajectory**.
Behaviour identical before the swap, a bounded 14-step transient, uninterrupted thereafter — and the
**pre/post fingerprint distance is 0.0000**. The material of the computation is replaced while the behaviour
continues, and the fingerprint does not move.

**The two load-bearing controls both fired.** **L1:** re-adding the class label and lag set **recreates** the D-069
false difference (0.0000 → 0.0612) — the exclusion of description-level quantities is load-bearing, not decoration.
**L2:** removing the discriminating probe **collapses** two genuinely different systems into one fingerprint
(0.0347 → 0.0000) — probe-repertoire adequacy is load-bearing.

**Four defects development caught, any of which would have been a false result:** a deviation-only fingerprint is
**blind to output inversion** (d(AND, XOR) = 0.0000, a false sameness); **zero-padding turned latency into a
difference** (d = 0.0946 between a channel and its own lengthened twin); the rich battery's **length depended on the
system** (a coordinate system with a variable number of axes); and a response **still in flight** was recorded as
permanent (the memory signature contaminated by impatience — D-067's error arriving from the other end of the
trace).

**A benchmark-label correction, made on development, before the freeze, with a stated principle.** I declared
`(xor3, xor_gate)` and `(toggle, fsm_gate)` to be continuity pairs; under rich access the fingerprint separated
them, **and it was right to**: `xor3`'s reconvergent paths **glitch** on a register step, and `fsm_gate` **freezes**
where `toggle` does not. Measured responses, not labels. **The benchmark was wrong; the measurement was not.**
Principle: **equivalence is relative to a repertoire.**

**THE COST OF POOR ACCESS, MEASURED.** 4/4 pairs DIFFERENT under rich access are INDISTINGUISHABLE under the
droplet repertoire — a third cause, a gated state machine, the redundant-lag system, and an OR that equals an AND
at its own register value. **False sameness rises as access falls.** That is a property of the droplet, and it
bounds everything the pilot could ever claim.

**DECISION (mission §8): both arms passed independently → `SC-PILOT-CAUSAL-FINGERPRINT` is AUTHORIZED as an
EXPLORATORY experiment and is NOT EXECUTED here.** β = 0.10, `D_int` and every substrate equation are untouched.
The strongest sentence a pilot pass could authorize is: *"under the frozen available perturbation repertoire,
within-droplet causal-response continuity exceeded between-droplet similarity during material turnover"* — which is
**not** proof of persistent individual identity, **not** preserved minimal architecture, **not** life, **not**
selfhood, and **not** a resolved Ship-of-Theseus case.

**Declared limitations, before the run and not discovered after it:** the two STATE systems reuse development
implementations (the substrate has no unseen state machine and I would not add one after the instrument was
frozen); and this qualifies the fingerprint **logic** under a droplet-*like* repertoire in a **Boolean** substrate —
per D-071 the droplet must build and certify its **own** provenance contract.

**EXP-SC-01 REMAINS BLOCKED. Stopping for strategic review.**

---

## D-073 — PREFLIGHT AUDIT of SC-PILOT-CAUSAL-FINGERPRINT: **`PREFLIGHT_FAIL`. THE PILOT WAS NOT EXECUTED.**

Repository clean at `b87f4cb` when the audit began. No historical artifact overwritten or amended; every prior
failure and development diagnostic preserved. **The fingerprint was not tuned, patched or modified.**

### P1 — the 14-step replacement transient. **OUTCOME P1-B.**

My report said *"behaviour uninterrupted"* **and** *"bounded 14-step transient"*. One half of that was wrong.
Measured on the declared behavioural output: the accessible output **deviated on exactly one step** (t = 53,
channel 2). **The figure 14 is a SPAN** — from the swap to the last deviating step — **not a count.**

**"Uninterrupted behaviour" is WITHDRAWN.** Corrected claim: *the pre-replacement accessible behaviour was
recovered after a bounded 14-step transient; continuity was NOT exact at every intermediate step.* This changes no
fingerprint verdict — the E1 *fingerprint* distance of 0.0000 is untouched, as are 18/18 development and 9/9
prospective — but the trajectory claim was overstated and is corrected in place.

### P2 — ground-truth independence. **PASS, 18/18.**

A privileged full-state path (`exp_preflight.py`) that **never imports `fingerprint.py`**, decides by **exact
equality of raw engine traces**, and uses **no distance, no block structure, no radii and no verdict rule** of the
instrument, reproduces **every** declared expectation on **both** arms — including the droplet-arm collision
`AND(clk,1) ≡ OR(clk,0)`. Labels were declared from construction and committed at `b87f4cb` **before** the run.
Declared shared assumption: the two paths share the **nuisance model** (clock phase, internal latency) and nothing
else.

The audit found **three defects in itself** and fixed them **in the audit, not the instrument**: a single cyclic
shift cannot absorb phase and latency together; `T_SIG = 128` truncated the longer-latency system's aligned block
(**a window shorter than the response — the D-067 defect, reappearing in my own audit**); and non-responding rows
aligned to the window start leak latency (**the same defect the instrument had already found and fixed in its own
development**). Each produced a false difference *in the audit*. None was in the instrument.

### P3 — the bounded partition-dependence addendum. **NOT EXECUTED.**

The frozen protocol contains **no partition gate** (verified: no *partition* / *lobe* / *alias* / *bifurcation* /
*observer_relative* / *object count* / *replication* / *duplication* anywhere in `FINGERPRINT_FREEZE_MANIFEST.json`),
and no stress test covering the seven required cases exists. **Classified honestly as an unexecuted bounded
diagnostic that is not part of the fingerprint qualification.** No retrospective PASS is fabricated. It would have
to be executed *inside* any pilot, because within-versus-between logic presupposes an object count.

### P4 — RAISED BY THE AUDIT. **The frozen instrument is not defined on the droplet's observable.**

The instrument builds `uint8` arrays, forms `dev = (obs != bas)` by **exact inequality**, and decides by
**Hamming distance** — which presupposes **discrete symbols**. The droplet's accessible observable, `uptake`, is a
**continuous float** of order 1e-3.

- **Cast to `uint8`:** every sample truncates to 0 → every droplet's fingerprint is identical → **universal false
  sameness.**
- **Compared as floats:** exact inequality fires on every sample → every droplet differs from every other **and from
  its own later self** → **universal false difference.**

**Neither is a measurement.** Missing from the freeze: any quantization or thresholding rule for a continuous
observable; any tolerance `ε` or continuous metric; any mapping from the frozen **binary** probe amplitudes `{0,1}`
to `N`/`c` field units. **Each is a free parameter that materially controls the within-versus-between separation the
pilot exists to test.** Supplying them is **defining the instrument**, not adapting it — and a patched instrument
cannot inherit the prospective qualification of the unpatched one.

**This is exactly the failure the preflight was mandated to catch.** I should have seen it at D-072: I flagged that
**temporal provenance** does not transfer to a continuous substrate and did not notice that the **response
representation** does not either. The omission is mine and it is on the record. The capability matrix is updated:
*the response representation is qualified ONLY for a binary observable.*

### DECISION

**`PREFLIGHT_FAIL` — PILOT NOT EXECUTED.** Per Phase 2: execution would require modifying the instrument, so we
stop. The fingerprint is **not** patched, and no patched version is called prospectively qualified.

**Recommendation (no work authorized by it).** A droplet pilot requires a **continuous-observable response
representation** — quantization or a continuous metric, a tolerance, and a physical amplitude mapping — which is a
**new instrument-definition step**. It cannot be qualified on the Boolean substrate, which is binary; it would need
a **continuous ground-truth substrate with known causal structure**, its own development certificate, and its own
prospective run. That is a well-posed piece of work and it is **not** authorized here.

**EXP-SC-01 remains BLOCKED.**


---

## D-074 — EXP-GT-CONTINUOUS-FINGERPRINT-00: FAIL. Instrument RETIRED. Droplet pilot remains BLOCKED.

**Context.** D-073 returned `PREFLIGHT_FAIL`: the frozen Boolean fingerprint is **undefined** on a continuous
observable. Cast to `uint8` -> universal false sameness. Exact float inequality -> universal false difference,
including a system against **its own later self**. Both were **reproduced on the new substrate**, confirming the
problem being solved is the real one (uint8 -> all zeros; float inequality -> 304/304 samples differ).

**What was done.** A new continuous ground-truth substrate (`ctrans`), a privileged evaluator that never imports
the instrument, a dev/prospective split **committed at `de97ee0` before the instrument existed** (verifiably
disjoint: no shared names, no shared spec fingerprints, disjoint seeds, disjoint parameter grids, one topology
reserved to prospective), a preregistered protocol with exact gates G1–G10 and a calibration rule
(`SAFETY=2.0, SEP_FACTOR=3.0`) fixed **before any distance was seen**, and a new instrument
(`cfingerprint.py`) frozen and hash-gated.

**Development: 52/52. Two-path validation: 52/52, 0 disagreements. Must-fail controls: 7/8.**

**Prospective: 52/54. G2 FAILED.** `P_cascade` was refused by the in-flight guard, which fired on a genuinely
slower **second-order** tail (5.3% of peak vs the 5% threshold). The privileged path puts its true settling time at
**108**, inside the 160-sample window. **The instrument abstained on a case it could have decided.**

**Decision.** Per the freeze manifest's own failure rule, written before the run: the version is **RETIRED**, not
repaired. The fix is a one-line threshold change; **it is not made**, because a repaired instrument would be one
tuned on its hold-out, and the hold-out is now **burned**. A future version requires a **new split** and a **new
authorization**.

**Five defects were found and are preserved, not hidden:**

1. **Metric aggregation (observer failure).** A MEAN over probe blocks diluted the `supply_cause` pair's real
   separation of 21.8 down to 8.6 with 24 blocks of pure noise. Fixed by the **quantifier**: "indistinguishable
   under the repertoire" is a FOR-ALL, certified by its WORST case, so the aggregate is a **max**.
2. **Noise-scale estimator error x signal (normalization failure).** `z = r/sigma_hat`, so a 1.4% error in
   `sigma_hat` injects `eps * z_signal` into a system's comparison **with itself**. Signature: **more repeats made
   the instrument worse** (null 5.2 -> 9.4 -> 25.8 at R=4/8/16). Fixed by independent per-probe baselines and by
   quotienting over one common scale clipped to the estimator's own confidence band. **Declared price: gain
   differences below ~4% are not resolvable.**
3. **Thresholds below the noise they threshold (observer failure).** `Z_DET=5` ("five sigma") sat below the drift
   excursion; a **silent system scored 1/32 "responses"** and was handed a confident DIFFERENT. Recalibrated on
   **noise-only** rows.
4. **Benchmark-label failure.** `D_noisy` was built at true SNR **1.97** — marginally *above* its noise floor, not
   below it. The instrument correctly detected it. **The failing thing was the system, not the instrument.** The
   system was fixed; the threshold was **not** moved, because moving it would have been fitting a threshold to a
   label.
5. **Evaluator / ground-truth failure — caught by the two-path check, which is what it is for.** The privileged
   evaluator quotiented by a **free affine map**, which absorbs a doubled gain (`a=2`) and an inverted sign
   (`a=-1`), and it duly certified two flagship DIFFERENCE cases as EQUIVALENT. **A benchmark whose truth path is
   wrong cannot fail an instrument; it can only slander one.**

**Also recorded: L6 DID NOT FIRE.** The lexicographic phase quotient is stable in this benchmark. The cyclic-shift
quotient remains the principled choice but is **not demonstrated load-bearing here**. A control that does not fire
is not a control, and the protection is **unproven**, not proven.

**Infrastructure hazard, recorded.** The repository is mounted on a filesystem with coarse mtimes on which Python's
bytecode cache is unreliable: a **stale `.pyc` masked a truncated source file**, and an early "differential
verification" that appeared to reproduce reference numbers exactly was in fact **running old bytecode and verifying
nothing**. All runs now use a per-run `PYTHONPYCACHEPREFIX` and every source file is `py_compile`d from disk before
use. Classified: **provenance / implementation failure**.

`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`: **NOT AUTHORIZED.**
`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**.
No droplet experiment was launched. `beta`, `D_int` and the droplet equations were not touched.


---

## D-075 — EXP-GT-CONTINUOUS-FINGERPRINT-01: FAIL at DEVELOPMENT. Not frozen. Prospective NOT run. Hold-out PRESERVED.

**Context.** v00 died conflating "is the signal still moving?" with "can the unobserved remainder change the
verdict?". It measured `P_cascade` at 64.15 against a radius of 23.36 and abstained anyway.

**Built.** A tail substrate (first/second/third-order, underdamped, multi-timescale, delayed-onset, delayed second
component, weak/strong long tails, non-settling, out-of-contract), a NEW split committed at `fb449b2` BEFORE the
instrument changed (v01 prospective reuses ZERO v00 systems; the burned pair appears ONLY as development regression
T1), and a tail-uncertainty guard that BOUNDS THE EVENTUAL DISTANCE rather than modelling the tail.

**Development 52/54. Controls 6/10.**

**WHAT WORKS, AND IT IS THE THING THAT MATTERED:** T1 — the burned case classifies BY BOUND (`D_lo = 41.9` vs
`r_sep = 22.1`), with no hard-coded exception anywhere. v00's exact defect is fixed for the right reason. Also T2
(non-settling abstains), T3 (slow-but-harmless classifies), T6 (noise is not a cause), T9 (guard load-bearing),
T10 (v00's guard reproduces its own death).

**WHAT KILLS IT: T4, the decisive control.** The bound's remaining-envelope statistic reaches **7.40 on pure
noise** (288 noise-only blocks), forcing `TAIL_NOISE = 9.0`. T4's REAL remainder — ~10% of the pair's difference
energy lies beyond the window, confirmed by the privileged path — measures **8.25**. It sits INSIDE the floor. The
bound cannot see it, calls it SETTLED, and returns a confident DIFFERENT on a pair whose answer is still partly
outside the window. **That is v00's error in the opposite direction, on the one case that distinguishes a
principled tail guard from a threshold-raising hack.**

**Also declared: the out-of-contract check cannot separate tau=130 from TAU_MAX=80** (per-sub-block decay 0.825 vs
0.732, against comparable noise). It reliably detects only tau > ~2.5 x TAU_MAX. In the band (TAU_MAX,
2.5 x TAU_MAX) the bound is UNSOUND and cannot tell that it is. UNVERIFIED SCOPE, stated rather than left to be
found later.

**Six defects preserved, each classified before repair:** (1) I called F0.admit() directly and it SILENTLY
RE-IMPOSED v00'S IN-FLIGHT GUARD -- six of eight initial failures, T1 among them. Inheriting a core means
inheriting its bugs unless you name the one you are replacing. (2) estimating the decay RATE from a ratio of two
noisy block means declared the NULL out of contract -- reading the estimator's variance as the world refusing to
relax. (3) SUBTRACTING the noise from the decrement when bounding the remainder -- the direction that flatters the
instrument, and precisely what produced the T4 failure. (4) one confidence constant for both the CHECK and the
BOUND. (5) TAU_MAX=40 against a 160-sample window would have made the three-way distinction VACUOUS -- caught
before any instrument code existed. (6) a name-keyed acquisition cache silently served a stale re-parameterised
system.

**DECISION: RETIRED AT DEVELOPMENT. The prospective split was NOT run and is NOT burned.** Freezing an instrument
whose defect is already measured, and spending the hold-out to confirm it, would destroy an asset for no
information. The identified fix -- a LONGER OBSERVATION WINDOW, giving the tail region leverage against its noise
floor -- is a BATTERY change and therefore a NEW instrument, which is not attempted here.

v00's six frozen files were NOT modified and still verify byte-for-byte against its freeze manifest.

`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`: **NOT AUTHORIZED.**
`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**.
No droplet experiment. beta, D_int and the droplet equations untouched.


---

## D-076 — EXP-GT-CONTINUOUS-FINGERPRINT-02: FAIL AT DEVELOPMENT. Sealed split untouched. The longer-window hypothesis is FALSIFIED.

**Preregistered at 44121e9, before any sweep:** horizon grid {160,240,320,480,640}, margin k=3.0, admissibility
`B_critical(W) >= k*B_noise(W)`, decision-relevance defined privileged and instrument-independent, and the rule
"select the SMALLEST horizon passing every gate, not the prettiest separation".

**MEASURED RATIO B_signal/B_noise ACROSS THE GRID: 0.89 / 2.55 / 2.56 / 1.18 / 0.29.**
**IT PEAKS AT 2.56 AND COLLAPSES. IT NEVER REACHES 3.0. THE BAR WAS NOT MOVED.**

**THE STRUCTURAL RESULT.** B_noise improves as exp(-(W-84)/(3*TAU_MAX)); B_signal decays as exp(-W/tau). The signal
dies faster than the floor improves whenever tau < 3*TAU_MAX -- true for essentially every in-contract system,
since TAU_MAX is BY DEFINITION the slowest admitted. **A longer window destroys the very evidence it was supposed
to reveal.** At the end of v01 the previous agent (me) proposed exactly this fix. It is now falsified by
measurement. The tail-bound FAMILY has a resolution ceiling no horizon can raise; a successor must change the
METHOD, not the budget.

**SECOND FINDING: the floor is DRIFT-limited.** White-noise theory predicts B_noise -> 0.58 at W=320; measured 3.49,
and it stops improving. Sub-block means wander with the OU baseline while `sd` (a differenced white-noise estimate)
is blind to drift by construction. The longer you look, the more the baseline has wandered. Corollary: the
out-of-contract bars are NOT constants -- carrying v01's W=160 values across the grid made EVERY pair, including
the NULL, come back OUT OF CONTRACT.

**THIRD FINDING, and it invalidates v01's controls retrospectively:** a PREFIX of a long episode is NOT a short
episode with the same seed. The engine draws noise (T samples) then drift from the same RNG stream, so drift
depends on episode length. Measured max|Z_long[:320] - Z_short(320)| = 6.48 ON A SYSTEM COMPARED WITH ITSELF.
v01's T7/T8 re-simulated to vary the window and were therefore measuring the RNG. v02 supplies prefix().

**WHAT v02 ACHIEVES (13/15 dev gates at the best horizon W=320):** D1 -- the v00 burned cascade classifies BY BOUND
(D_lo=45.52 vs r_sep=22.89, DECIDABLE_SETTLED), no exception anywhere. Harmless slow tails classify; non-settling,
out-of-contract, drifting and silent systems abstain; gain, hidden state, extra causes separate; continuity and
EQUIVALENCE_CLASS_ONLY hold. Failing: sign and delayed-second-component (drift-driven false-unbounded blocks).

**T4 abstains at W=320 -- FOR THE WRONG REASON.** Its bracket straddles because a block went unbounded from DRIFT,
not because the bound resolved the remainder (B=8.92 < k*B_noise=10.47). A CORRECT-BY-ACCIDENT VERDICT IS NOT A
QUALIFICATION.

**DECISION: RETIRED AT DEVELOPMENT. The sealed prospective split (31 systems, 27 cases, third-order cascade) was
NOT touched and is NOT burned.** Audited: no Q_* acquisition has ever existed on disk or in git history. No more
flexible estimator was invented after seeing the failure, per the preregistered stop rule. No freeze manifest was
written -- v02 never earned one.

v00 and v01 untouched; v00's six frozen files still verify byte-for-byte; v00 tests 11/11.
`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`: **NOT AUTHORIZED.**
`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**.
No droplet experiment. beta, D_int and the droplet equations untouched.


---

## D-077 — EXP-GT-CONTINUOUS-FINGERPRINT-03: BENCHMARK_INVALID. The target quantity is ill-posed. BRANCH CLOSED — NO V04.

**Preregistered at cc39c6c, before any fitting:** alpha=0.05 MARGINAL coverage; disjoint FIT(14)/CAL(14)/CHALLENGE(22)
partition (verified: no system, parameter tuple or seed appears twice; none matches a sealed-prospective system; the
reserved third-order cascade appears nowhere in development); a MATCHED SHAM channel (baseline episodes only,
differing solely in the absence of intervention amplitude) to measure the drift scale v02's differenced `sd` was
blind to; ridge on label-free features, fit-set CV only; split conformal; radii from FIT-SET NULLS only
(r_cont=7.96, r_sep=23.88).

**The sham channel works** -- it returns a per-system drift scale of 1.264 noise units, exactly the quantity that
set v02's floor. **Then the pre-fit truth check (G11) failed, and it failed for a reason that invalidates the
question itself.**

**THE FINDING. The fingerprint distance is an RMS OVER AN OBSERVATION WINDOW. For any TRANSIENT difference it
dilutes at EXACTLY sqrt(W/W') and TENDS TO ZERO as the window grows.** Measured noise-free, same metric, only the
window changed: v00 burned cascade 47.35 -> 22.64 (0.478); v01 T4 30.18 -> 14.45 (0.479); gain x2 115.32 -> 55.13
(0.478); sign 230.64 -> 110.27 (0.478). sqrt(320/1400) = 0.478. **The PERSISTENT hidden-state pair does NOT dilute
(346.43 -> 348.01, ratio 1.005) -- the control that proves the effect is the METRIC's normalization, not the
systems.**

**Therefore "the distance at a longer window" is not a fact about the pair. It is a fact about the pair AND the
window.** The privileged path places the v00 burned cascade at D_inf=22.64, BELOW the preregistered r_sep=23.88 --
inside the ambiguity gap -- so G5 (must classify) and G2 (no confident wrong verdict) cannot both hold.
Construction truth and privileged truth DISAGREE. **G11 forbids scoring. BENCHMARK_INVALID.** The radii were
preregistered and are NOT moved; the target was preregistered and is NOT redefined after seeing that it fails.

**RETROSPECTIVE CONSEQUENCE FOR THE WHOLE BRANCH: for a FIXED window the instrument already sees everything it will
ever see. There is no "unseen remainder" affecting D_W -- the only uncertainty is MEASUREMENT NOISE. v00's in-flight
guard, v01's tail-uncertainty bound and v02's resolution certificate were each defeated by A QUANTITY THAT DOES NOT
EXIST.** The one legitimate truncation concern is PERSISTENCE, which does not dilute and is already captured by any
window exceeding the settling time plus the declared delay horizon. v00's persistence logic was addressing the real
problem; its in-flight guard was addressing a phantom.

**A well-posed continuous fingerprint needs a WINDOW-INVARIANT discrepancy functional -- an integral rather than a
mean, or normalization by response energy rather than window length. That changes the METRIC, the one component
unchanged since v00, and is therefore a NEW PROGRAMME, not a new version.**

**STATUS.** No freeze manifest -- v03 never earned one. No calibration was performed -- the calibration set is
untouched. **The sealed prospective split (31 systems, 27 cases) was NEVER SPENT** and remains sealed; audited
again: no Q_* acquisition has ever existed on disk or in git history.

Methodological synthesis of v00-v03 written to docs/CFP03_SYNTHESIS.md.

`SC-PILOT-CONTINUOUS-FINGERPRINT-PREFLIGHT`: **NOT AUTHORIZED.**
`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**.
**CONTINUOUS-FINGERPRINT BRANCH CLOSED — NO V04.**
No droplet experiment was ever executed in this branch. beta, D_int and the droplet equations untouched.


---

## D-078 — EXP-GT-CAUSAL-RESPONSE-DECOMPOSITION-00: FAIL AT DEVELOPMENT (19/20). New split untouched.

NEW PROGRAMME, not continuous-fingerprint v04. The v00-v03 branch stays closed and historically intact; the
historical sealed hold-out has still never been generated.

**THE CENTRAL REPAIR WORKS.** On nested prefixes of ONE acquisition the old window-normalized scalar dilutes
144.04 -> 83.17 (ratio 0.577 = sqrt(160/480), exactly), while E_trans -- AN INTEGRAL, NOT A MEAN -- converges
upward and P_inf correctly stays at zero for a transient with an identical asymptote. The two quantities the old
scalar conflated are now measured on separate axes and each separates on its own:
  EQUAL-ENERGY control -> PEAK RATIO 3.09x ; EQUAL-PEAK control -> ENERGY RATIO 7.04x.
Those controls required a real construction: a single leaky path CANNOT dissociate peak from energy (shape factor
E/A^2 stays in 18-41 across Tx 1..64; best achievable peak ratio 1.36). My first attempt at them failed silently.

**DEVELOPMENT 19/20**, accuracy-checked against privileged truth (estimated energies land within 0.68-1.21x).
Passing: pure transient, pure persistent, hidden state, latency, both dissociation controls, gain, sign, units,
solver, equivalent implementations, limited-access collision (exact zeros, EQUIVALENCE_CLASS_ONLY), DRIFT-ONLY
(zero causal components on every axis), slow response without drift, and all abstention cases.

**THE FAILURE: Z-17, a slow causal response UNDER HEAVY DRIFT.** E_trans overstated 7.1x (3.05e6 vs a privileged
4.30e5) and the drift excursion quoted as a causal peak (422.7 vs a true ~97). The instrument SILENTLY CALLS THE
DRIFT A RESPONSE instead of abstaining -- exactly what gate G8 forbids.

**DIAGNOSIS, MEASURED: A SHAM CAN CALIBRATE A BAND. IT CANNOT SUBTRACT A REALIZATION IT NEVER SAW.** The matched
sham has the same VARIANCE as the causal trace's drift but is an INDEPENDENT REALIZATION, so debiting its ENERGY is
unbiased in expectation and useless per pair -- E_raw and E_sham fluctuate independently and their difference
carries an error of the order of the thing being removed. That is why drift-ONLY passes perfectly (a band suffices)
and Z-17, which needs an actual subtraction, does not.

**TWO INHERITED ASSUMPTIONS, BOTH FOUND AND NAMED.** (a) The old BASELINE_MAX refusal, imported with admission,
re-imposed "refuse anything that drifts" and pre-empted the sham machinery -- THE SAME MISTAKE v01 MADE inheriting
v00's dead in-flight guard. (b) max-over-blocks is a VERDICT rule, not an ESTIMATOR: over 32 blocks it selects the
block where independent drift realizations conspire. Fixed to median-over-PHASES (replicates), max-over-PROBES
(distinct interventions). Not enough to save Z-17.

**DECISION: FAIL AT DEVELOPMENT. The new prospective split is NOT touched and remains sealed. No freeze manifest --
this version never earned one.** A successor must change the ACQUISITION CONTRACT, not the estimator: to SUBTRACT
drift rather than bound it, the sham must SHARE the drift realization (interleaved / common-mode acquisition), not
merely its distribution. Not attempted here; this stops for strategic review.

SC-PILOT-RESPONSE-DECOMPOSITION-PREFLIGHT: NOT AUTHORIZED.
SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.
No droplet experiment. beta, D_int and the droplet equations untouched.

## D-079 — CRD-01: common-mode acquisition PASSES ground truth; physical transfer NOT established
The Z-17 failure that killed CRD-00 (E_trans overstated 7.1x, A_peak 422.7 vs true ~97) is fixed by CHANGING WHAT
IS ACQUIRED, not the estimators: a SHARED drift realization across active/control/sham. E/E* = 1.01x, A/A* = 1.00x.
Prospective 8/8, all 12 gates pass, all 12 must-fail controls fail as required. CRD-00's independent sham is now
REFUSED (COMMON_MODE_NOT_ESTABLISHED) rather than corrected. The admission verdict TRACKS the accuracy boundary:
inside it, E/E* <= 1.32x; outside it, the instrument refuses instead of degrading.
DECISIVE CAVEAT: the passing contract needs a control that is THE SAME SYSTEM, UNPROBED, RECORDED SIMULTANEOUSLY.
No droplet can supply that -- you cannot intervene and not intervene on the same droplet at once. Classification:
MAPPING_REQUIRES_NEW_OBSERVABLE -> TRANSFER_NOT_ESTABLISHED. A co-recorded reference channel would reduce the
requirement to something buildable, but that variant was NOT tested and is therefore NOT claimed.
Three of my own bugs were caught and fixed by REPLACEMENT, not re-thresholding: a drift proxy sharing measurement
noise with the deviation it corrected (g_hat = -1.008 on a drift-FREE system -- the correction was injecting
noise); a worst-of-64 admission that reproduced CRD-00's own max-over-blocks error and failed the pure null; and a
contamination detector that fired on every case, kappa=0 included, because it confounded drift accumulation with
probe dependence.
SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.

## D-080 — CRD-02: referenced paired-episode decomposition FAILS AT DEVELOPMENT (contamination gate G5)
The paired-reference architecture removes CRD-01's unrealizable oracle twin: two SEPARATE episodes (active, sham),
each with its OWN simultaneous common-mode reference, d_A != d_S, corrected per-episode then differenced
(difference-in-differences). It WORKS on the drift half of the problem: Z-17 recovered E/E*=1.00 A/A*=1.02 with NO
oracle twin; different-drift episodes, gain mismatch to x3, lag to 24 samples, bandwidth loss, baseline mismatch,
persistence, hidden state, and peak/energy factorization all recovered; local unshared drift and no-reference
rejected; admission tracks validity on every axis EXCEPT one. G14 (physical plausibility) PASSES -- no simultaneous
twin is required.
IT FAILS gate G5. Contamination detection has an identifiability floor at kappa ~ 0.15: a 12% reference leak
(preregistered D4) attenuates the estimate 21% (E/E*=0.79) and is neither detected nor abstained -- clean cases
reach t-stat 2.8, kappa=0.12 reaches 2.84, so no threshold separates them. A 12% multiplicative reference bias is
statistically indistinguishable from a 12%-smaller true response without an absolute-scale reference. Five
detectors tried; none crosses the floor. Per the admission contract ("accepted cases inaccurate before rejection
-> the admission contract fails"), this is a development-gate failure.
DECISION: FAIL AT DEVELOPMENT. The prospective split (12xx) is NOT touched and remains sealed. SC-PILOT-RESPONSE-
DECOMPOSITION-PREFLIGHT: NOT AUTHORIZED. CRD-03, if authorized, must add a SECOND reference of known different
coupling (b' != b) to make kappa identifiable -- an acquisition change, not an estimator tweak.
Three of my own bugs were caught and fixed by construction, not tuning: differencing the wrong episodes (fixed by
proper difference-in-differences); Python salted-hash seeds making runs non-reproducible (fixed by a stable content
hash); and a degenerate AR(1) noise floor plus a 9s/arm Python OU loop (floor moved to the corrected residual; OU
blocked-vectorised, matching the literal recurrence to 1e-15, 300x faster).
CRD-01 stands unaltered. SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.

## D-081 — CRD-03: redundant references + signed interventions PASS in ground truth; transfer needs passive observables
The CRD-02 contamination failure is FIXED. Redundant passive references with DISTINCT drift couplings + signed
interventions correct DIFFERENTIAL reference contamination: the preregistered CRD-02 case (kappa=0.12 single
reference) -> CORRECTED, E/E*=1.00 A/A*=1.00 (was a silent 21% attenuation, floor kappa~0.15). Corrected out to
kappa~0.35. 21/21 dev cases, 15/15 dev gates; prospective 12/12 under a verified hash gate, all prospective gates
pass, opened once. Q2 (kappa=0.12 on an UNSEEN system) CORRECTED 1.00; unseen topologies (third-order, underdamped,
multiscale, feedback) recovered; collinear references abstain (ill-conditioned).
IDENTIFIABILITY THEOREM (symbolic + numeric, established BEFORE the instrument): drift-free signals z_i =
s(1-alpha_i kappa_i) span a 2-D space regardless of reference count; reference disagreement is a linear combination
of them. => shape always identifiable; DIFFERENTIAL contamination identifiable to kappa~0.002 (contamination
attenuates, largest-amplitude channel is cleanest, exact if any reference clean); COMMON-MODE contamination
(kappa_i prop a_i) exactly unidentifiable AND undetectable by any passive scheme -> reported as a LOWER BOUND
(D4 0.72, Q5 0.81). Absolute scale UNAVAILABLE on ctrans; not fabricated from privileged truth.
Transfer: MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE (>=3 passive references of distinct drift coupling; signed
schedule plausible; no oracle; G15 physical plausibility PASS). Verdict: GROUND_TRUTH PASS -- PASSIVE OBSERVABLE
DESIGN REQUIRED. Publication: METHODS PREPRINT READY.
CRD-01, CRD-02 unaltered. SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED. Prospective 14xx burned.

## D-082 — PASSIVE OBSERVABLE DESIGN: FAIL — CONTAMINATION DOMINATES
CRD-03 passed in ground truth but requires >=3 passive references with distinct drift couplings and low causal
contamination. The frozen scaffold droplet substrate does NOT expose them. Read-only calibration (permitted N
handle + declared internal-state initial conditions u/v/off; no equation, beta, D_int, rho/U/V modified; operational
references read only N/rho/c) established:
 - Spatial N sub-samples are COLLINEAR (couplings all ~0.20) -> must-fail #1 confirmed.
 - Reference TYPES have diversity (N-mean ~+0.20, N-derivative ~-0.004, attractant c ~-0.50; diversity 7.79,
   cond 1.14) BUT under a clean strong response the drift-observing references (N_global/background/core, c) carry
   the response at contam/drift ~0.79-0.90, with kappa_i/a_i CONSTANT across N refs (spread 0.056) = COMMON-MODE,
   the exact direction CRD-03 proved UNIDENTIFIABLE.
 - The low-contamination references (N_laplacian, N_flux) have drift couplings ~50x below the measurement's ->
   the CRD-03 correction amplifies their noise ~50x -> unusable.
 - No far-field clean region exists (the droplet fills the grid).
 - Reading internal state U/V/sigma directly WOULD separate response from drift and is FORBIDDEN oracle access.
PHYSICS: the causal response IS nutrient consumption (uptake via beta*sigma), which depletes N; the environmental
drift also lives in N. Response and drift share one field -> common-mode contamination is forced by geometry.
DECISION: FAIL — CONTAMINATION DOMINATES. SC-PILOT-RESPONSE-DECOMPOSITION-PREFLIGHT: NOT AUTHORIZED. The pilot was
NOT executed; no equation/beta/D_int/rho/U/V modified; only passive read-only diagnostics added (logging changes
no trajectory, verified). Quantum option NOT WARRANTED (the obstacle is observational rank-deficiency, not
computation). The CRD-03 methods result is UNAFFECTED and is in fact instantiated by this failure (T5): METHODS
PREPRINT READY FOR INDEPENDENT REPLICATION. SC-PILOT-CAUSAL-FINGERPRINT remains BLOCKED. EXP-SC-01 remains BLOCKED.

## D-083 — Independent replication: core reproduces, lower-bound theorem T6 FALSIFIED, quantitative transfer FAILS
Clean-room reimplementation (independent_replication/recover.py, imports numpy only) reproduces the CRD-03 core:
differential contamination identifiable/correctable (kappa=0.12 -> 1.001), common-mode unidentifiable (bound),
collinear abstains. So the historical PASS is not a code artifact.
BUT the lower-bound claim is FALSIFIED. argmax-amplitude assumes sign(lam_i*e_i)>=0 (attenuation). Under
amplification (e_i<0, OR g_i<0 with e_i>0) the FROZEN instrument returns CORRECTED with q_hat/q=1.106 (confident
10.5% OVERSTATEMENT); point-estimate coverage 0/40 amplifying, 3/40 mixed-sign. Never tested: all historical cases
used kappa>=0 and positive couplings; the droplet c_global has a=-0.50, so real substrates hit it. FIX (T6-prime):
report bracket [min|v|,max|v|] (40/40 coverage all regimes, sign-agnostic); emit a point only under an established
sign contract, else abstain. Verified independently.
Second substrate (FitzHugh-Nagumo): contamination LOGIC transfers (differential located, common-mode bounded,
amplifying abstains) but clean-case accuracy biased (q_hat/q~0.86) -> quantitative accuracy is ctrans-specific.
VERDICTS: CRD-03 INDEPENDENT REPLICATION: INDETERMINATE (core reproduces; a load-bearing operational claim fails
audit and must be restricted). SECOND SUBSTRATE: PASS (structural identifiability transfers) with quantitative
caveat. PUBLICATION STATUS: REPLICATION COMPLETE — CONSOLIDATION INCOMPLETE (T6 retraction + FHN gap + no
one-command rebuild). Historical CRD-03 freeze NOT rewritten; flaw documented. DROPLET CAUSAL-CONTINUITY PILOT
remains BLOCKED. EXP-SC-01 remains BLOCKED.

## D-084 — Sign-safe consolidation: T6 repaired, sign-safe instrument PASSES fresh prospective
Resolved the T6' contradiction: the 40/40 bracket coverage held ONLY because every tested regime had >=1 clean
reference; with no anchor the bracket is one-sided and its side is set by sign(alpha*kappa). Repaired theory
(T6-A attenuation lower bound, T6-B amplification UPPER bound, T6-C clean-anchor bracket, T6-D sparsity m>=2s+1,
T6-E no-anchor-no-sign impossibility with symbolic proof), property-tested >=0.97 over 400 trials each. Built an
independent sign-safe instrument (9 statuses, never max-amplitude default), committed a fresh split BEFORE fitting
(8b77031), froze (09016d7), ran prospective once: 10/10, 0 invalid. Safety metric (confident exclusion of truth) =
0 across 1600+ trials, all sign regimes, all (m,s). Second clean-room implementation agrees 20/20. FHN: structural
transfer, quantitative substrate-specific (0.86, pre-window calibration bias diagnosed). One-command reproduction
(make reproduce-paper) PASSES from disk; Dockerfile pinned but not built here.
VERDICTS: SIGN-SAFE IDENTIFIABILITY THEOREM: PASS. SIGN-SAFE INSTRUMENT PROSPECTIVE: PASS. SECOND SUBSTRATE:
STRUCTURAL PASS — QUANTITATIVE FAIL. ONE-COMMAND REPRODUCTION: PASS (container unverified). PUBLICATION STATUS:
METHODS PAPER SOLID (peer-review submission needs external human review + container E2E). Historical CRD-03 sign
bug documented, not patched. DROPLET PILOT and EXP-SC-01 remain BLOCKED.

## D-085 — FINAL HARDENING: theorems PASS, large hold-out FAILS (low-SNR null-gate), publication BLOCKED
THEOREMS SOUND: 0 validity violations across 4000 eps-separated trials (T6-A/B/C/E). The earlier 0.995/0.970 were
INFORMATIVENESS rates, not pass rates; all 14 residual cases were safe refusals (near-equal betas -> channels agree
-> common-mode not excludable without an anchor), and the theorem conclusions held in every one.
SIGN-CONTRACT PROVENANCE: all 8 point identifications in the benchmark were ORACLE-derived (anchor/sign read from
ground truth). Blind rerun -> 0 points, safety preserved. Point-identification claims are now explicitly CONDITIONAL
on externally established contracts; the benchmark does NOT show such contracts are obtainable from passive data.
LARGE HOLD-OUT FAILED: preregistered N=2000 stratified generator (a76f8a7), instrument hash-gated at 09016d7, run
once. 541/1333 emitted sets EXCLUDE the truth (40.6%); blind arm 541/541. Single systematic cause: the
null-response gate (median(amp) < 2*median(null)) MISFIRES at SNR=5, emitting POINT={0} ("no response") against a
real response (hand-verified case i=1: true |q|=0.428, instrument said 0). The 10-case prospective had no low-SNR
stratum and passed; the stratified hold-out failed immediately. STOP RULE INVOKED: failure preserved, instrument NOT
patched, hold-out BURNED. A harness bug (passing a_i instead of 1/a_i) was found and corrected first; signsafe.py
was never modified (hash-gated throughout) -- documented as an erratum.
CLAIM C12 ("never emits a set excluding the truth") WITHDRAWN. Theorems unaffected (the defect is an implementation
detection gate, not the identifiability theory). FHN: Track A (structural transfer; quantitative ctrans-specific).
Docker/CI never built -> clean reproduction INCOMPLETE.
VERDICTS: THEOREM PACKAGE: PASS. LARGE DISTRIBUTIONAL HOLD-OUT: FAIL. CLEAN REPRODUCTION: INCOMPLETE.
CROSS-SUBSTRATE: STRUCTURAL PASS. PUBLICATION STATUS: NOT READY. EXTERNAL HUMAN REVIEW: PENDING.
DROPLET CAUSAL-CONTINUITY PILOT remains BLOCKED. EXP-SC-01 remains BLOCKED.

## D-086 — Turnover PRESEAL 03C reconciles authority, family, approval, scopes, inference, and event evidence

**Date:** 2026-07-16

**Decision:** On the separate integration branch, supersede the non-authoritative Claude 03A addenda with direct
repairs to the existing canonical PRESEAL files. Freeze primary seeds `54001-54050`, feasibility reserve
`54051-54096`, hard cap 96, and minimum 18 valid original worlds. Reserve activation may use feasibility fields
only. Require a separate human-approval JSON bound to the exact execution-manifest Git blob.

**Statistical decision:** all L/N/P/E/G/B decoders use the same own-dose label and outer leave-one-original-world-
out predictions. Scaling is training-only, lambda is fixed, and uncertainty is computed from fixed original-world
fold losses. No bootstrap CV retraining across duplicated worlds is permitted.

**Measurement decision:** persist exact target-local, geometric-neighbour, pair, target-memory-masked environment,
complete target-centred world, and body scopes before the deep assay. Persist five evidence-only frames after the
first censor so fission, transient fragmentation, merge, loss, and death are distinguishable without following a
daughter.

**Authorization boundary:** Claude's “GO FOR SEAL” is not operator authorization. No `54xxx` seed was run. The
committed approval template remains unauthorized.

## D-087 — Turnover PRESEAL 03G uses one executable canonical chain on Windows AMD64

**Date:** 2026-07-16

**Decision:** Supersede 03C and 03E for any future prospective turnover execution with the single machine-indexed
03G path. The path must consume, in order, a verified seal, exact authorization, canonical-directory hash-chained
ledger, ordered seed family, atomically published canonical raw records, validated raw manifest, frozen grouped
analysis, executable A–F tree, and result certificate. No disconnected self-check or documentation-only evaluator
counts as an execution path.

**Platform decision:** Windows AMD64 with CPython 3.12.10 is the authoritative prospective platform. The complete
transitive pip lock must reproduce exactly in a fresh environment before any final seal. No Linux exact-reproduction
claim is made by 03G.

**Threat-model decision:** one authorized execution is enforced inside the declared canonical run directory, with
explicit same-binding resume and cryptographic replay evidence. A malicious actor controlling a copied open-source
repository cannot be technically prevented from rerunning modified code; that copy has a different untrusted ledger
and is not the sealed prospective execution.

**Provenance decision:** local `main` and `origin/main` were observed equal at
`6d0bed67339c1b422877b8bfaae6861669597a93`; protected `archive/main-f3921a4` remains the distinct archived lineage
at `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`. Neither ref is modified. No final seal, valid human authorization,
or `54xxx` execution is created by this decision.

## D-088 — Turnover 03G prospective execution certifies Outcome B without ownership

**Date:** 2026-07-17

**Decision:** Consume the single human authorization bound to final seal
`cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd`
and accept the frozen executable A-F tree's certified Outcome B. The canonical
runner completed primary seeds `54001-54050` exactly once and in order. It
obtained 21 valid original worlds, above the frozen minimum of 18, so no reserve
seed was executed.

**Scientific interpretation:** `G_OWN_PERM` and `G_CAUSAL` pass, while
`G_LOCAL_EXCLUSION` fails and `DISTRIBUTED_ENV` is false. A specific local
causal feeding effect survives deep turnover, but the target's own graded
history is not established as locally owned. This is a passive local causal
remnant and not individual memory. No identity, ownership, individuation, life,
or active-reconstruction claim is authorized.

**Execution boundary:** the 108-entry ledger is terminal `CERTIFIED` and
verifies at tip
`0d579d0fa40fd19afe7bfc26140133fc9c57de2b656a7606aa5a5bd8591791aa`.
The one authorization is consumed. No additional prospective execution is
authorized.

## D-089 — ACCESS-STRUCTURE-00 Phase 0 requires intervention qualification before preregistration

**Date:** 2026-07-17

**Decision:** Accept the new causal-localization question as distinct from 03G, preserve certified Outcome B and V5
unchanged, and adopt **REVISE** rather than GO or STOP. The minimal identifying design is a local/environment 2x2
factorial (`L0E0`, `L1E0`, `L0E1`, `L1E1`) plus matched-versus-crossed `LAEB`, body controls, global `up_ref`
ablation, direct-readout ablation, and manipulation-equivalent shams under one common future-feeding probe.

**Scientific boundary:** the 03G `L`, `E`, `B`, and `Gm` variables were finite decoder summaries, not isolated causal
compartments. `DISTRIBUTED_ENV=false` means that the own-dose label was not established through the frozen
low-dimensional E/G summaries; it does not establish absence of environmental or relational information.

**Engineering boundary:** already-open DEV deep states are deterministically reconstructible, but the repository has
no qualified full-environment reset, standardized-body operator, matched/crossed graft, or disturbance-matched graft
sham. Practical and equivalence margins are also unfrozen. These must be implemented and validated on already-open
DEV seeds before any complete preregistration or prospective authorization.

**Execution boundary:** no new family is selected or opened, no prospective seed is run, and active reconstruction
is not started. Human review is the next action.

## D-090 — ACCESS-STRUCTURE-00 Phase 0.5 exact exchange fails interface and arm-balance gates

**Date:** 2026-07-17

**Decision:** Retain **REVISE** after the explicitly authorized operator qualification on already-open DEV seeds
`50001-50010`. Define `L` only as the frozen 03G 11-statistic readout; define complete manipulable `C`, body subset
`B`, one-cell near-interface `H`, far `E`, cross-cutting physical fields `NP`, dynamic/global `G`, and complete
Markov phase `D`. Replace ambiguous null notation with explicit donor-labelled `C_A H_B E_B` arms and an
on-manifold same-seed/no-phase-drive reference `0`.

**Engineering decision:** use exact reciprocal core exchange rather than a one-way scaled graft. It preserves each
donor core under an integer toroidal translation and conserves every state-array total across the reciprocal pair.
No-op, serialization, same-source, coordinate-transform, and matched shams are exact; sham feeding bias is zero;
all six active arms are 4/4 viable for 40 steps; dynamic `up_ref=0` and `lam_plus=0,lam_minus=0.15` retain the uptake
endpoint. These passes establish mechanical feasibility only.

**Failure decision:** reject the current hard-boundary operator for causal inference. Across DEV, causal-field seam
ratios reach `22.872x` recipient natural boundaries, the one-cell halo changes after one update and the perturbation
propagates into far environment. Individual-arm mass/physical-field totals are unmatched even though reciprocal
pair totals conserve within the float64 criterion. A matched/crossed feeding difference could therefore be a seam,
phase, halo, balance, or global-channel artefact. Active crossed feeding was deliberately not evaluated.

**Execution boundary:** no prospective seed/family, seal, push, merge, V5/03G change, ownership claim, or active
reconstruction is authorized. Human review is required. Any boundary-aware/balance correction is a separately
approved DEV-only revision; if `C/H/E` cannot be separated without destroying the state under test, the next
decision must be STOP rather than threshold relaxation.

## D-091 — BALANCED-HISTORY-ISOLATION-00 passes semantics/allocation but fails four-target DEV feasibility

**Date:** 2026-07-17

**Design decision:** Accept the fresh categorical 2 x 2 history design as semantically valid. `a1/a2` are two
consecutive 60-step local nutrient episodes, and the four fixed histories orthogonalize cumulative dose from
EARLY-versus-LATE order within the historical support. Freeze DEV seeds `55001-55024`, a seed-only cyclic Latin
square, complete-block original-world inference, the qualified two-cell no-swap clamp, history-independent
`up_ref=0`, step-40 integrated tracked uptake, fixed first-stage quantities and `lam_plus=0` mediation control.

**Feasibility decision:** The single bounded family produces zero four-target pre-history eligible worlds. Seventeen
worlds have three selected targets and seven have two. Consequently no assignment is applied and no first-stage,
feeding, isolation, transport or mediation endpoint exists. The downstream gates are not evaluable; they are not
negative scientific results.

**Disposition:** Return `DEV-FEASIBILITY-FAIL — REVISE-MECHANICS`. The four-target design is not a prospective
candidate. Do not extend the family, weaken eligibility post hoc, analyze survivor targets, seal the draft or inspect
a prospective namespace. A new pre-data assignment-unit or world-generation design requires human review. Earlier
STOP results, 03G Outcome B, V5 and prior raw results remain unchanged.

## D-092 — COUNTERFACTUAL-HISTORY-CORE-00 exact clones are feasible but targeted memory first stages fail

**Date:** 2026-07-17

**Design decision:** Accept the exact-clone repair as a valid DEV counterfactual factorial. Freeze one focal target
per independent source world, four deterministic low/high dose by EARLY/LATE histories, fixed 1000-step turnover,
complete-block inference, ordinary and qualified isolated probes, body/physical controls, and `lam_plus=0`
mediation. Branches are potential outcomes and never independent replicates.

**Execution decision:** The pushed before-data freeze at `e504288` governed exactly seeds `57001-57024`. All 24
worlds were eligible and 17 supplied complete blocks. Cloning, common-boundary, isolation, global-channel, sham and
core-preservation gates pass. A raw-only analyzer that neither imports the runner nor initializes the engine
independently reproduces the counts, contrasts, gates and classification.

**Scientific decision:** Accept `NO_MEMORY_FIRST_STAGE`. The protocol-targeted positive core `m_plus` dose first
stage crosses zero. The protocol-targeted negative core `m_minus` EARLY-minus-LATE first stage is uniformly positive
and its sign is not flipped after inspection. Dose feeding is positive under coupling and isolation, but strong body
and physical-state differences remain and `lam_plus=0` does not support selective mediation; order feeding is not
established. This rules out the frozen targeted-memory interpretation, not all history-dependent state.

**Disposition:** STOP this preregistration candidate. Do not claim `DOSE_ONLY` or `DOSE_AND_ORDER`, open a
prospective namespace, seal the draft, modify 03G/V5, or begin reconstruction. A fresh pre-data design separating
the target memory coordinate from body/physical dose pathways requires human review.

## D-093 — Mechanism reconciliation corrects the mminus sign but leaves dose attribution unresolved

**Date:** 2026-07-17

**Theory decision:** Keep the frozen EARLY-minus-LATE contrast unchanged and correct the reduced-theory orientation.
For the exact write/decay rates, two 60-step episodes and 120-step settle, the slow `m2` component has a larger
negative EARLY-minus-LATE response than fast `m1`; therefore `m1-m2` and `m_minus` are positive. The frozen negative
orientation was not justified by the intended scalar recurrence. The exact spatial engine still has endogenous
`Psi`, transport and body dynamics, so magnitude requires the trajectory. This is a theory/sign correction, not a
discovery or post-outcome contrast redefinition.

**Evidence decision:** Accept deterministic same-manifest diagnostics only after all 17 complete worlds reproduce
their frozen final-state hashes and feeding values exactly. The positive `m_minus` order state is small and persists
under coupled and isolated probes, but feeding order remains unestablished. Targeted `mplus/mminus` predictors add
no reproducible original-world LOWO information.

**Attribution decision:** Physical carryover is the leading candidate because body mass/area, core and world `rho`,
physical fields and baseline uptake change with dose, while predeclared exploratory mass/area normalizations remove
and reverse the total-feeding contrast. Do not call it the only explanation: the fixed body/geometry model fails the
strict two-arm out-of-world explanation gate.

**Disposition:** `UNRESOLVED`; causal-landscape pilot `NO-GO`. Preserve `NO_MEMORY_FIRST_STAGE — STOP`, all parent
raw results, 03G and V5. No new seed, prospective run, landscape search, ownership, order-memory, identity, heredity,
or active-reconstruction claim is authorized. Human review may close the line or authorize preparation only of a
new body-equalization preregistration.

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

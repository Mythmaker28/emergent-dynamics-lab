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

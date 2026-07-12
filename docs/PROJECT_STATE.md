# Project State

## CURRENT QUESTION

Can CORE V0 local particle laws produce auditable high phenotype continuity under low material retention, beyond tracker and static-flux artefacts?

## CURRENT SUBSTRATE

OPEN reaction-diffusion (Gray-Scott) with spatially homogeneous feed/removal, as of D-028. Closed Flow-Lenia retired (D-027); Particle Dynamics retired (D-021). Both preserved and reusable.

## CURRENT CORE VERSION

`CORE V0`, code version `0.1.0`.

## VALIDATED COMPONENTS

- Repaired implementation plus EXP02, alias-intervention, EXP03-A/B/C, EXP-REF-01, the Flow-Lenia core + field stack, EXP-FL-01 map #1/#2, and the tracer sensitivity check: 101 tests pass.
- Deterministic engine and multi-step diagnostic-ID permutation fixture.
- Scalar and independent vectorized force paths on 32 controlled worlds.
- Periodic detector, ID/order/translation-invariant phenotype fixtures.
- Geometry/size tracker with explicit lifecycle and ambiguity events; no P/M association gate.
- Separate P and M plus orthogonal construct fixtures.
- ID-permutation and static-material-flux nulls.
- Conservative scheduled-run lock semantics.
- Baseline 001's original all-green claim is superseded by independent audits; repaired baseline 002 and hold-out 003 are complete.
- Exact-SHA numerical re-audit `NUM3` passed all 29 then-current tests, 1,024 force/one-step fixtures, and 167 subnormal radii.
- EXP02 per-run shards are written through temporary directories and atomic rename, pinned to a plan hash, verified by SHA-256/size on resume, and summarized without retaining all runs in memory.
- The streaming fixture proves byte-for-byte equality of all four raw tables against the full runner, rejects plan drift/corruption, and resumes without recomputation.
- Recovery fault injection includes a real child-process `os._exit(73)` after shard fsync and before atomic publication; restart quarantines the unpublished directory and converges to one verified result.
- Final derived files are atomically published, `manifest.json` is last, and `COMPLETE` requires all planned identities, hashes, sizes, actual CSV row counts, raw-index/summary consistency, and an exact reproduction command.

## ACTIVE EXPERIMENT

**Open-RD substrate: causal individuality NOT established (D-031).** EXP-RD-02 ran the frozen chain on the 9 frozen laws: hold-out 9/9 survive, but the causal intervention gives AUDITED 6/90 = 6.7% [3.1,13.8] with 83% destroyed, and 0/6 survive observer sensitivity -> NET 0 audited. Nothing promoted. Prior: EXP-RD-01 (D-030) gave 9 OPEN screening-permitted laws vs 0 in the exact CLOSED limit. NOTHING is promoted: the Flow-Lenia precedent (D-027) shows an identically-shaped screen died under replication. Tracer FROZEN (D-029); substrate QUALIFIED (D-028). The OPEN Gray-Scott substrate is QUALIFIED (D-028; 12/12, homogeneity null proves the forcing cannot impose a pattern; imposed-pattern control separated only by open-system rates). Closed Flow-Lenia retired (D-027). Prior: EXP-FL-03 WITHDREW the EXP-FL-02 positive (D-027): on 12 unseen seeds/law the audited rate collapsed to 2/46 (4.3%) and 0/2 survived cadence sensitivity; the dominant failure is frozen_lump (30/46) — structures re-establish but STOP turning over. Nothing is promoted. Prior: EXP-FL-02 (isolated mass-conservative reservoir-exchange throughput; exact OFF limit = current core) produced the project's first placebo-controlled, alias-audited causal survivors (D-026). NOT promoted: one causal seed per law. Prior: EXP-FL-01 map #2 (720 blind flux-favouring runs) was SCREEN NEGATIVE (D-025): 720/720 persistent structures (P~0.99), min mean-M=0.933, 0%% of runs with M<0.8, 0 permitted. Tracer resolution verified adequate (D-024; not a metric artefact). Assessment: the minimal fixed-law mass-conservative Flow-Lenia core LACKS a material-throughput mechanism. EXP_FL_00 qualified the stack (D-022); Particle Dynamics retired (D-021). Next (user decision): a mass-conservative single-law Flow-Lenia config WITH genuine material throughput (glider regeneration / open-flux), same falsifiable protocol; no metric relaxation. The full causal ladder is negative (D-017..D-020) AND the EXP-REF-01 measurement positive control PASSED (the frozen stack recognizes and separates a known persistent dissipative organization from static flux), so the negatives are substrate results, not measurement blindness. Kill-switch review: `docs/PARTICLE_DYNAMICS_KILL_SWITCH_REVIEW.md`. Next substrate proposal (Flow-Lenia candidate, not assumed): `docs/NEXT_SUBSTRATE_PROPOSAL.md`. Substrate NOT switched autonomously — awaiting user confirmation of the candidate.

## LAST COMPLETED EXPERIMENT

`EXP-REF-01-COREV0-20260710-001`: measurement positive control. Frozen stack RECOGNIZED a known persistent dissipative organization under turnover (P=1.0, M->0.25, probe-positive) and SEPARATED it from static flux on frozen observables (|circ| 0.147 vs 0; vdisp 0.090 vs 0) -> PASS (D-021, retire Particle Dynamics). Preceding: EXP03-C NEGATIVE (D-020); EXP03-B NEGATIVE (D-019); EXP03-A NEGATIVE (D-018); CORE V0 CASE A (D-017).

## OBSERVED

- Native Codex heartbeat `Emergent Dynamics Lab Autonomous Research` is ACTIVE at an exact 30-minute recurrence.
- New private GitHub repository `Mythmaker28/emergent-dynamics-lab` exists and is the `origin` remote.
- Historical local branch and commit exist; isolated historical tests: 19/19 pass.
- Archived historical CSV: 7,079 rows, Pearson `0.675724`, 0 rows for `P>0.8,M<0.5`.
- Current implementation tests: 38/38 pass.
- Current independent baseline: 36 runs, 36,722 repeated measurement rows, descriptive Pearson `r(P,M)=0.733162`, P range `0.287298–0.999985`, M range `0–1`.
- The unchanged initial probe contains 384 rows. Candidate audit finds 115 rows on clean tracks with at least eight observations and 20 physical endpoint pairs probe-positive under at least two cadences.
- The frozen cross-cadence/multi-seed rule selects laws `{1,3,6,10}` for fresh-seed hold-out.
- Independent numerical audit: nominal force agreement passed 10,000 fixtures, but the old vector norm failed at `r≈1e-158`; half-box reach and non-finite specs were unconstrained.
- Independent tracker audit: direct P/M/ID separation passed, but sparse look-alike alias, false split/merge semantics, incomplete edge logs, and stale death timestamps failed the stronger lineage/audit gate.
- First re-audit found one residual subnormal ordering error in the scalar force path; the reference now normalizes direction before multiplying magnitude, with a smallest-positive-subnormal regression test.
- Local post-fix validation: 1,024 force/one-step fixtures pass exactly and all 167 radii from `1e-158` through the minimum positive subnormal pass with zero path disagreement. Independent final numerical re-audit is still required.
- Repaired code uses `hypot`, finite/domain guards, force/one-step validation, full association-edge records, correct current timestamps, measurement interval flags, expanded tracker/detector sensitivity, and an explicit sparse-alias null.
- Final independent numerical re-audit `NUM3`: PASS exact; 29 tests, 1,024 fixtures, and 167 subnormal radii all pass.
- Repaired baseline 002 preserves 36,722 measurements, descriptive `r(P,M)=0.733162`, and 384 raw probe rows; 230 rows lack logged ambiguity/split/merge inside their interval, but all 384 retain unresolved alias risk.
- Candidate-audit join bug found after hold-out 002: corroborating cadences were not always independently clean. Hold-out 002 is invalidated with no accepted disposition.
- Corrected baseline selection yields only law 3, supported by screening seeds 101 and 303.
- Corrected hold-out 003: 5 runs, 5,885 repeated measurement rows, 30 raw probe rows; only seed 909 satisfies the clean-long cross-cadence endpoint rule. Frozen gate fails 1/5 < 2/5.
- EXP02: 648,740 measurements, descriptive `r(P,M)=0.731581`, 10,302 unchanged-probe rows, 7,186 interval-complexity-unflagged rows, 2,400 whole-track clean-long rows, and 94 same-endpoint cross-cadence endpoints.
- Independent candidate audit finds exactly nine laws eligible in two of three screening seeds: `{0,12,35,52,73,94,209,225,298}`. None qualifies in all three; all retain sparse-alias/static-flux risk and none is promoted.
- Independent statistical QA verified all 3,600 raw CSV hashes/sizes/row counts and found 10,101/86,573 tracks (11.67%) censored at time 12.
- The parent `measurement_aggregates.csv` fragmented nominally equal float `tau` keys. Raw data are intact; D-013 requires a separate integer-step corrected aggregate and preserves the flawed parent file unchanged.
- Direct diagnostics cover 47 cadence rows / 22 endpoints for the nine eligible laws: P and M recompute exactly, no compatible unselected edge is hidden, and zero rows reject static occupancy/look-alike alias.
- HOLDOUT04 executed all 45 preregistered law/seed runs from clean SHA `d9d9a52`: 41,889 measurement rows, descriptive `r(P,M)=0.698846`, 502 unchanged-probe rows, 140 whole-track-clean long rows, and 10 same-endpoint cross-cadence endpoints.
- Under the unchanged `>=2/5` fresh-seed gate, law 0 qualifies in seeds `{3002,3004}` and law 52 in `{3001,3003}`. Laws `{12,35,73,94,209,225,298}` fail and are not replaced.
- Every HOLDOUT04 probe and survivor retains unresolved static-flux/sparse-look-alike alias risk. The hold-out count is not an event-probability estimate and is not scientific promotion.
- ALIAS-INTERVENTION (frozen protocol @baf1fca, harness @b00322d): rigid off-site displacement of the candidate constituents, matched CONTROL/SHAM/PERTURBED/PLACEBO from an identical pre-intervention state. Enrolled units law0=5/40, law52=9/40 (rest censored). sham==control bit-for-bit everywhere; no F4/F5. Genuine turnover-individuality 0/5 and 0/9; three law-52 units re-establish only as rigid cohesive clusters (M~1.0, no turnover). Occupancy/look-alike NOT rejected at majority; CORE V0 survivors closed (CASE A, D-017).

## INFERRED

- The historical code is useful as audited reference behavior but its per-run P calibration and incomplete provenance should not be copied.
- The current tracker removes the historical hard dependency on shared IDs, reducing a central false-negative risk.
- Probe occupancy rises from `0.68%` at cadence 10 to `2.37%` at cadence 60, so sparse-observer effects remain a serious alternative explanation.
- Fresh-seed recurrence narrows the diagnostic target to laws `{0,52}` but does not distinguish an organization that moves or recovers from a stationary occupancy alias.

## OPEN HYPOTHESES

- CORE V0 may still couple loss of material to loss of morphology.
- Sparse snapshots or tracker thresholds may erase rare fast-turnover lineages.
- Density preference and orbital interactions may shift the joint P/M distribution if CORE V0 remains negative.
- A preregistered intervention that displaces a detected organization relative to its former spatial site, compared with an exact sham, may reject stationary occupancy without using diagnostic IDs for association or physics.

## KNOWN MEASUREMENT RISKS

- Tracker selection and ambiguous crossings.
- Connected-component bridge artefacts.
- P feature scaling and feature dominance.
- Repeated track/tau rows are pseudoreplicates, not independent trials.
- Right-censoring at the finite observation horizon.
- Static material-flux false positives.
- EXP02 raw shards are intentionally local/ignored; committed indexes and checksums prove integrity of present files but are not a remote raw-data backup.
- Crash recovery is fail-closed for missing, mismatched, or corrupt completed shards. Directory metadata fsync is not portable on this Windows path, so post-crash re-verification remains the durability boundary.

## NEXT ACTION

USER DECISION. Open Gray-Scott reaches the continued-turnover regime and its screening signal recurs robustly (hold-out 9/9), but displacement DESTROYS the structures (83%): the organization is maintained by its LOCATION in the chemical field, not carried by its material. Before any further substrate work, fix the self-flagged method weakness: pre-declare an observer-sensitivity design that perturbs cadence/tracker WITHOUT moving the enrollment point (t* must be held fixed across observer settings), and re-run it on any future audited unit. Options then: (a) accept that classical RD dissipative structures are site-maintained and are the wrong substrate for constituent-carried individuality; (b) test a substrate where structures are self-propelled/motile (so location is not the carrier); (c) revisit whether 'constituent-carried under displacement' is the right operationalisation of individuality at all. Do NOT relax thresholds, add composites, or select laws visually.


## MODEL NOTE (2026-07-10)

The Fable 5 model lock was **explicitly lifted by the user** on 2026-07-10. EXP03-A was designed, validated,
preregistered, and screened under `claude-opus-4-8` with the user's authorization. Earlier CORE V0 / alias-
intervention artefacts are deterministic and independently reproducible regardless of orchestrating model.

## DO NOT RESURRECT

- Historical Hopfield/CA claims or legacy memory scores.
- `theseus_score`, composite `memory_score`, or post-hoc threshold relaxation.
- Mutation, neighbor contagion/type transition, or particle recycling before the causal ladder authorizes them.
- Claims that the historical 7,079-row experiment was independently reproduced.

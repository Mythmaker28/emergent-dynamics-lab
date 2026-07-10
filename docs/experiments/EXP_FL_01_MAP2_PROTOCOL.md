# EXP_FL_01 map #2 — Frozen Protocol: wide blind Flow-Lenia map, flux-favouring domain

Status: **FROZEN before screening.** Preregistered by `RUN-20260710-2130-EXPFL01M2`. Corrects two issues with
map #1: (a) too small (24 laws) to support a substrate negative; (b) domain landed only in static-blob regimes.
Tracer resolution is FIXED at the verified G*=8 (D-024); this map widens the PARAMETER DOMAIN, not the tracer.

## QUESTION
Over a substantially wider, mechanistically flux-favouring blind Flow-Lenia parameter domain, do any fixed-law
regimes produce persistent organization with HIGH field P under LOW cohort field M (persistence under constituent
turnover)?

## LAW PARAMETERIZATION (blind Halton, 8 dims) -- `flow_lenia_law_from_halton_v2`
Wider ranges than map #1, expanded MECHANISTICALLY to favour material throughput (documented, not tuned to yield):
- kernel_mu [0.25,0.75] (map1 [0.35,0.65]); kernel_sigma [0.08,0.28] (map1 [0.10,0.22]).
- growth_mu [0.05,0.30] (map1 [0.08,0.26]); growth_sigma [0.008,0.050] (map1 [0.010,0.040]).
- dt [0.20,0.60] (map1 [0.20,0.50]).
- flow_gain [0.8,2.5] (map1 FIXED 1.0) -- stronger advection -> more throughput.
- concentration_theta [0.30,1.20] (map1 FIXED 1.2) -- LOWER cap penalises dense static lumps -> mass keeps flowing.
- concentration_n [1.0,3.0] (map1 FIXED 2.0) -- shape of the concentration cap.
Mechanism: map #1 settled into static cohesive blobs (flow -> equilibrium, mass locked in dense lumps). Raising
advection (flow_gain, dt) and lowering theta prevents settling and promotes sustained mass flux through
structures. This is the pre-declared flux-favouring expansion.

## SAMPLING / SEEDS / STEPS
240 laws (Halton indices 0..239) x 3 initial-condition seeds {8001,8002,8003} = 720 runs. Steps 300, cadence 10.
Three seeds is SCREENING, not a probability.

## STACK / P&M / GATE (FROZEN; G*=8)
Qualified field stack: field detector (0.15, 12 cells) + frozen geometry tracker + field phenotype
(P=exp(-RMS dPhi), declared scales, NOT recalibrated) + cohort field M(tau) at G*=8 (verified adequate, D-024).
Probe P>0.8, M<0.5 (INITIAL EXPLORATORY PROBE only). Gate: a (law,seed) is eligible if some track has a
probe-positive endpoint on a clean (no split/merge/ambiguous) long (>=8 obs) track; a law earns SCREENING
PERMISSION at >=2/3 seeds. No composite; thresholds frozen; no visual selection.

## FIVE EVIDENCE LEVELS (separate)
1 distributional shift (P/M/circulation/mass across the wider map); 2 screening signal (permitted laws);
3 fresh-seed recurrence; 4 alias rejection; 5 causal re-establishment. Only 1-2 in this screen.

## DECISION / DISCIPLINE
- Permitted laws -> frozen fresh-seed hold-out (>=2/5) -> direct alias audit -> same-state matched-branch causal
  intervention (displace a creature's mass off-site) if authorized. No threshold relaxation.
- Still concentrated at high-P/high-M -> QUANTIFY the failure mode (distribution over P, M, circulation; fraction
  of runs with M<0.5; flux/throughput proxy) and assess whether the MINIMAL fixed-law Flow-Lenia core LACKS a
  material-throughput mechanism -- i.e., its mass advects coherently but does not pass constituents through
  persistent structures -- rather than relaxing the metric. That assessment (not a metric change) is the outcome.

## FALSIFIERS
F1 no law earns permission; F2 any permission explained by static persistence / diffusion / tracker artefact;
F3 permitted laws fail fresh-seed hold-out; F4 survivors alias-compatible.

# EXP_FL_02 — Frozen Protocol: isolated reservoir-exchange material throughput (matched OFF/ON)

Status: **FROZEN before screening.** Preregistered by `RUN-20260710-2200-EXPFL02`. Authorized by D-025 (minimal
Flow-Lenia core lacks material throughput). ONE mechanism only.

## QUESTION
Does adding a single isolated, globally mass-conservative ACTIVE-FIELD/RESERVOIR exchange (material throughput)
produce persistent organization with HIGH field P under LOW cohort field M (persistence under constituent
turnover), compared with the current Flow-Lenia core?

## MECHANISM (isolated, spatially generic, detector-independent)
Active field A (Flow-Lenia: advected, detected, measured) + latent reservoir field R. Local exchange driven ONLY
by the local growth field G(U(A)):
  delta = exchange_rate * dt * ( max(G,0)*R - max(-G,0)*A ), clipped to [-A, R];  A += delta; R -= delta.
Mass moves R->A where growth is favourable and A->R where it is not; A+R is conserved EXACTLY, cell by cell. R is
transported by isotropic periodic diffusion (generic medium; mass-conserving). R never enters U, G or the flow
field F (which depend on A only). NO glider mechanism, no pattern/detector dependence, no localization, no
evolution, no multi-species. Gliders, if any, are OUTCOMES.

## EXACT OFF LIMIT
`exchange_rate = 0` reproduces the current Flow-Lenia core **bit-for-bit** (verified: max |dA| = 0.00e+00 over a
run, parametrized tests). OFF and ON share identical core law, reservoir, diffusion, seeds -- only exchange_rate
differs. This is the matched control.

## PASSIVE TRACERS / COHORTS (pre-declared) + THROUGHPUT VALIDATION
Cohorts partition BOTH pools: sum_c C_A = A and sum_c C_R = R. The verified spatial resolution G*=8 (D-024) is
applied SEPARATELY per pool, so cohorts distinguish ACTIVE-origin (0..7) from RESERVOIR-origin (8..15) mass
(16 cohorts). This is required for the tracer to register local A<->R exchange as turnover; a purely spatial
labelling would conflate reservoir and active mass at the same location. Cohorts are transported by exactly the
same operators as their fields (reintegration for A, diffusion for R); on exchange, transferred mass takes the
LOCAL cohort proportions of its source pool. Cohorts NEVER influence any dynamics (verified: zeroing them leaves
A and R bit-identical).
**Throughput positive control (validated):** with ON, reservoir-origin mass genuinely enters the active field
(>10% of active mass by t=300; measured 44%); with OFF it is exactly 0. So the passive tracers measure REAL local
constituent turnover.

## STACK / P&M / NULLS (FROZEN, UNCHANGED)
Qualified field stack: detector (0.15, 12 cells) + frozen geometry tracker + field phenotype
(P = exp(-RMS dPhi), declared scales, NOT recalibrated) + cohort field M(tau) (mass Jaccard). The static-flux
field null is RETAINED (unchanged). Probe = P>0.8, M<0.5 (INITIAL EXPLORATORY PROBE only). No composite score;
thresholds unchanged; P and M separate.

## SAMPLING (blind, matched)
64 laws (Halton) x {OFF, ON} x 3 seeds {8001,8002,8003} = 384 runs. Core law from the map-#2 flux-favouring
sampler; throughput params from 3 extra Halton dims: exchange_rate [0.05,0.80] (ON; 0 for OFF),
reservoir_diffusion [0.05,0.25], reservoir_fraction [0.5,2.0]. Steps 300, cadence 10.

## GATE / FIVE LEVELS
Eligible (law,seed) = a probe-positive endpoint on a clean (no split/merge/ambiguous) long (>=8 obs) track. A
(law, condition) earns SCREENING PERMISSION at >=2/3 seeds. Five evidence levels kept separate: 1 distributional
shift; 2 screening signal; 3 fresh-seed recurrence; 4 alias rejection; 5 causal re-establishment.

## DECISION / DISCIPLINE
- ON permitted laws -> frozen fresh-seed hold-out (>=2/5 unseen seeds) -> direct alias audit -> same-state
  matched-branch causal intervention (displace a structure's mass off-site; CONTROL/SHAM/PERTURBED/PLACEBO). No
  threshold relaxation; no composite; no visual selection; no replacement of rejected laws.
- ON remains negative -> STOP adding mechanisms; recommend a genuinely reaction-diffusion / open-system substrate.

## FALSIFIERS
F1 ON does not exceed OFF in permitted laws; F2 any ON permission explained by densification / fragmentation /
tracker churn / reservoir-driven blob replacement (look-alike) rather than turnover-individuality; F3 permitted
laws fail fresh-seed hold-out; F4 survivors alias-compatible.

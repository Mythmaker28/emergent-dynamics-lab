# Journal — EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00

- **Role:** primary scientific execution agent (interactive; isolated branch). **Base:** 25c419a (HMC final).
- **Scope:** does the frozen substrate contain a hidden state that is persistent, individual-specific,
  causally consequential, and accessible? Plus an interpretive erratum to the HMC verdict.

## OBSERVED
- Erratum: HMC "SNAPSHOT SUFFICIENT" unsupported (all regressions < baseline) -> corrected to NO
  HISTORY-SPECIFIC CAUSAL PERSISTENCE + PREDICTIVE INDETERMINATE.
- Library: 100 dev + 32 prospective trajectories, 4 ages each, canonical full states stored.
- Hidden existence: 63-71% of h variance beyond accessible snapshot (spatial U/V).
- Individuation AUC 0.40 dev / 0.30 prosp (within-traj drift 2.82 > same-attractor between 2.14). 4
  attractor classes; only 23% single-class over 900 steps.
- Causal: sigma-FLIP (attractor) 1.8-2.6x clone ceiling (no probe), 4.46-4.49x under nutrient probe
  (97-100% of states). sigma-SCRAMBLE (spatial, mean-sigma preserved) INERT 0.04-0.06x.
- Probe grid: N+0.5x15 most informative (5.67x), nutrient deprivation least (0.68x). All non-destructive.
- Markov partial-corr(h;future|x) = -0.09.

## INFERRED
- Internal state = GENERIC CAUSAL ATTRACTOR MEMORY: causally consequential + accessible only as a coarse
  attractor class (mean sigma, itself accessible via uptake); the genuinely-hidden fine organization is
  epiphenomenal; NOT individuating. Reproduces on the held-out family.

## HYPOTHESIS / FALSIFIER
- H: no individual-specific causal hidden state exists in the frozen physics.
- Falsifier: within-trajectory hidden similarity exceeding same-attractor between-trajectory (AUC>0.7),
  or a scramble (mean-sigma-preserving) that drives accessible divergence above the clone ceiling. Neither
  occurred, on dev or prospective.

## DECISION
- VERDICT PASS — GENERIC CAUSAL ATTRACTOR MEMORY. NEXT-PHYSICS B (design individual-specific memory
  mechanism; none added here). QUANTUM NOT USED.
- HMC prospective split remains SEALED. SC-PILOT-CAUSAL-FINGERPRINT and EXP-SC-01 remain BLOCKED.

## ENVIRONMENT
- Same create-only mount / stale-lock / no-background-jobs constraints as HMC; resumable budget runner +
  lock-free plumbing commits + /tmp compute. See memory [[ising-v3-git-mount-workaround]].

## HANDOFF / NEXT AUTHORIZED ACTION
- If pursued: preregister a physics mechanism that makes the internal organization (a) individuating
  (history-dependent basins, not 4 generic classes) and (b) causally coupled beyond mean sigma. Do not
  modify physics without a new protocol.

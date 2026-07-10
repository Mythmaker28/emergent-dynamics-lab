# EXP_FL_01 — Frozen Protocol: blind low-discrepancy Flow-Lenia regime map (first map)

Status: **FROZEN before screening.** Preregistered by `RUN-20260710-2045-EXPFL01`. Authorized by D-022
(EXP_FL_00 qualified). Blind: laws are sampled by a deterministic low-discrepancy sequence, not chosen.

## QUESTION
Do any fixed-law Flow-Lenia regimes produce persistent organization with HIGH field phenotype continuity P under
LOW cohort material retention M (persistence under constituent turnover), on the qualified field stack?

## LAW PARAMETERIZATION (blind Halton, 5 dims)
`flow_lenia_law_from_halton(i)` = FlowLeniaSpec(size 64, kernel_radius 10, concentration theta 1.2 n 2) with
kernel_mu in [0.35,0.65], kernel_sigma in [0.10,0.22], growth_mu in [0.08,0.26], growth_sigma in [0.010,0.040],
dt in [0.20,0.50] from Halton dims of `halton_point(i+32,5)`.

## SAMPLING / SEEDS
24 laws (Halton indices 0..23) x 3 initial-condition seeds {8001,8002,8003}. Three seeds is a SCREENING, not a
probability. Steps 300, snapshot cadence 10.

## STACK / P&M (frozen, qualified)
Field detector (threshold 0.15, min 12 cells) + frozen geometry LineageTracker + field phenotype
(P=exp(-RMS dPhi), declared scales) + preregistered cohort field M(tau) (mass Jaccard). No composite; P not
recalibrated. Probe = P>0.8, M<0.5 (INITIAL EXPLORATORY PROBE only).

## SCREENING GATE
A (law, seed) is eligible if some track has a probe-positive (P>0.8, M<0.5) endpoint on a clean (no
split/merge/ambiguous) long (>=8 observations) track. A law earns SCREENING PERMISSION at >=2/3 seeds. Permission
is not a candidate.

## FIVE EVIDENCE LEVELS (kept separate)
1 distributional shift (descriptive P/M/circulation/mass across the map); 2 screening signal (permitted laws);
3 fresh-seed recurrence; 4 alias rejection; 5 causal re-establishment. Only levels 1-2 are evaluated in this screen.

## DECISION / DISCIPLINE
- No permitted law -> EXP_FL_01 (this map) NEGATIVE; document; a wider or refined blind map may be pre-declared
  next (no threshold relaxation).
- Permitted laws -> frozen fresh-seed hold-out (>=2/5) -> direct alias audit -> same-state matched-branch causal
  intervention (displace a creature's mass off-site) if authorized. Do not lower thresholds; no composite; no
  visual selection; no replacement of rejected laws. Same discipline as CORE V0.

## FALSIFIERS
F1 no law earns permission; F2 any permission explained by static persistence (M~1, no turnover) / diffusion /
tracker artefact rather than turnover-individuality; F3 permitted laws fail fresh-seed hold-out; F4 survivors
alias-compatible.

## VALIDATION / REPRODUCTION
`pytest tests/test_exp_fl_01.py`; `edlab.experiments.exp_fl_01.screen_records`.

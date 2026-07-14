# EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00 — ANALYSIS RESULTS

Raw: `results/sc_hsi/{lib_dev,lib_prospective,div_dev,div_prospective,causal_dev,causal_prospective,
probes_agg,certificate}.*`. Figure: `results/sc_hsi/EXP_SC_HSI_00_figures.png`.

## Attractor analysis (deliverable 5)
k=4 attractor classes on the internal (mean σ, het, n_domains) coordinates; sizes 32/12/46/10 (dev).
Between-attractor hidden distance (3.74) > same-attractor (2.14): classes are genuinely separated.
Attractor dynamics: consecutive-checkpoint class stability 0.58; only 23% of trajectories remain in one
class over 900 steps — a SHORT-lived generic memory that drifts across classes.

## Individuation analysis (deliverable 6)
within-trajectory hidden distance 2.82 vs same-attractor between-trajectory 2.14 →
individuation AUC = 0.40 (dev), 0.30 (prospective). Below 0.5: an entity resembles its own past LESS than
it resembles a same-attractor peer. No individual-specific hidden state.

## Hidden-state existence
Mean residual fraction of h given accessible X = 0.71 (dev), 0.63 (prospective). Hidden info beyond the
snapshot EXISTS, carried by the spatial organization (mean σ is the most X-explained component, R²=0.59).

## Exact-clone ceiling (deliverable 9)
Median clone divergence 0.35 (no probe), 1.28 (under N+0.5×15). Clones stay well below the σ-flip signal
in 97–100% of states — a valid, tight stochastic ceiling.

## Future-divergence & causal consequence (deliverable 10)
Median divergence / clone ceiling:
```
                     no probe    nutrient probe   exceeds ceiling (probe)
  σ-flip (attractor)  1.81 / 2.61   4.46 / 4.49        97% / 100%     (dev / prospective)
  σ-scramble (spatial)0.06 / 0.04   0.01 / 0.01         5% /   3%
```
Attractor class is causally consequential and probe-amplified; spatial organization is epiphenomenal.
Natural aliasing pairs diverge 4× the ceiling but same-attractor (6.7×) ≈ different-attractor (7.2×),
i.e. inter-entity divergence is chaotic-microstate-dominated, not attractor-specific.

## Probe-selection results (deliverable 8)
median flip/clone ratio (alive 100% for all): N+0.5×15 = 5.67 (SELECTED); c×0.3×15 = 4.49; N+0.5×5 = 3.77;
c×0.3×5 = 2.51; c+0.5×5 = 2.08; c+0.5×15 = 1.51; N×0.3×15 = 0.75; N×0.3×5 = 0.68.

## Markov-sufficiency (deliverable 11)
Among snapshot-matched pairs, partial correlation of hidden distance with future divergence, controlling
snapshot distance = −0.09 (≈ 0). The accessible snapshot (incl. uptake) is approximately Markov-sufficient
for accessible futures; the hidden residual adds no causal information. This is a POSITIVE result (the
controlled scramble is inert), not an underpowered null.

## Temporal-order control (deliverable 12)
Consecutive-in-time hidden distance / non-consecutive = 0.78: mild temporal continuity, no individuating
memory. G9 not required (no history claim).

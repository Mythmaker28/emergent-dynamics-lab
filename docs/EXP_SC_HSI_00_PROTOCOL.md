# EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00 — PROTOCOL & METHODS (preregistered)

Config: `edlab/experiments/sc_hsi/config.py`. Physics imported unchanged from the frozen sc_hmc line.
New disjoint families; HMC prospective seeds 9501-9516 are NOT reused.

## Descriptors (strict accessible/hidden separation)
- Accessible snapshot X (8-d): geometry [log size, rg, anisotropy, compactness, core-fraction] + external
  fields [mean c, mean N over entity] + [specific uptake]. Uptake is an accessible behaviour.
- Privileged hidden h (6-d): ID-independent phenotype [het, n_domains, interface, radial_u, janus] + mean σ.
- Attractor coordinates (3-d): mean σ, heterogeneity, n_domains. k-means k=4 fit on DEV (frozen).
Trajectory ID is stored for ground-truth scoring ONLY; it never enters X, h, or any instrument feature.

## Checkpoint library (deliverable 3)
DEV = 100 trajectories (seeds 20000-20099); PROSPECTIVE = 32 (seeds 21000-21031). Each: warm up 2000
frozen steps, then checkpoints at ages {0,300,600,900}. Canonical age 600 stores compact full states
(float32 rho,U,V,c,N,uptake) sufficient to re-evolve; cohorts are irrelevant here (passive) and reset to
a single mono bin on reload.

## Matching (deliverable 4; frozen on DEV)
Standardize X and h on DEV canonical states. Snapshot-matched = X-distance in the lowest 10% quantile;
hidden-different = h-distance in the highest 60% quantile. Rank by (x_dist − 0.3·h_dist); cap 60 dev /
40 prospective pairs. Controls: exact clone (independent env noise), σ-scramble (permute U/V within the
entity — preserves mean σ and the internal histogram, destroys spatial organization), σ-flip (swap U↔V →
opposite attractor, rho/c/N held), same-attractor unrelated, different-attractor.

## Direct future-divergence (deliverables 9,10; PRIMARY test)
Evolve states under identical deterministic forcing for 150 steps; accessible-axis feature trajectory
[size, rg, uptake, mass] sampled every 30 steps; divergence = standardized L2. Exact clones evolve under
independent multiplicative environmental noise (σ=0.01) on N,c only → stochastic ceiling. Causal
consequence requires the hidden intervention to exceed the clone ceiling.

## Intervention grid (deliverable 7; searched on DEV, then frozen)
Bounded N/c grid: {N +0.5, N ×0.3, c +0.5, c ×0.3} × {5, 15} steps. Score = median (σ-flip divergence /
clone divergence) subject to ≥90% non-destruction. Selected & frozen probe: **N+0.5×15**.

## Splits & gates (deliverables 2, 15)
Development fits all standardizations, attractor model, matching thresholds, and probe. Prospective family
(21000-21031) is evaluated once with the frozen instrument. Development gates G1-G12 (Section 15 of the
mission) gate the prospective evaluation; the individuation gate G6 is a RESULT discriminator (pass →
individual identity; fail → generic attractor). Verdicts per Section 17.

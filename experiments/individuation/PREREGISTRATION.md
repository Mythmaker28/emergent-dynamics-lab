# PREREGISTRATION — LOCAL-CAUSAL-INDIVIDUATION-00 (frozen before prospective)

Engine: frozen C1c MultiChannelMemoryEngine (no modification). Branch: exp/local-causal-individuation-00.
No new physics; no new architecture (that is Experiment 2). Thresholds below are calibrated on DEV seeds
50001–50010 and are FROZEN; they will NOT be adjusted after observing prospective seeds.

## Question
Can co-existing droplets, given distinct *local* histories, (1) store their own, (2) causally express their
own history rather than the global history, (3) maintain the distinction through material turnover, without
using labels or future responses?

## Hypotheses
- **H1 (individuation):** with well-separated targets, the causal influence matrix is diagonally dominant,
  each droplet's OWN local history is decodable well above its neighbours' histories, and this survives
  turnover.
- **H0 (no individuation):** diffusion and/or the global write-reference synchronize droplets so that
  off-diagonal influence is large or own≈neighbour decode.

## Frozen design
- World: scaffold self-organized, 64×64 periodic, warmup 800 steps.
- Targets: K = 3 droplets, size ≥ 45 cells, pairwise periodic centroid distance ≥ **24 cells** (safe
  separation; contamination < 1% at ≥24 in DEV).
- Local history: fixed spatial Gaussian on N, σ = 0.8·r_g (min 3), two phases (early amp a1, late amp a2),
  each phase 60 steps (total drive 120), amplitude scale a ∈ [0.005, 0.035]; histories assigned to targets by
  a balanced (Latin-square) design so own/neighbour contrasts are not confounded with target index.
- Coordinates: per target, dose = a1+a2 and order = a2−a1 (as in C1c), but applied LOCALLY per droplet.

## Metrics
- **C_ij (memory-write):** mean |Δm_plus| in droplet j when target i is locally driven, vs same-seed no-drive
  baseline. Diagonal dominance DD = mean(diag)/mean(|off|).
- **C_ij^behav (causal expression):** mean |Δ(specific uptake)| and |Δ(mean c)| in j when i is driven — the
  behavioural (readout) footprint.
- **Own vs neighbour decode:** grouped leave-one-history-out ridge (λ=1) of a droplet's OWN dose/order from its
  memory features (R²_own) vs decoding a NEIGHBOUR's history from the same features (R²_neigh).
- **Maintenance:** R²_own recomputed longitudinally through renewal to M ≤ 0.5 (frozen tracker).
- **Trivial-feature baseline:** decode own history from size+mass+position only.
- Uncertainty: donor-level percentile bootstrap, n=3000, seed 20260715 (same convention as V4 reproduction).

## Mandatory controls
(1) global common history; (2) fake local pulses (drive empty space, no droplet); (3) permuted signals between
droplets; (4) inert memory channel (λ_plus=λ_minus=0); (5) readout ablation; (6) matched counterfactual, same
seed; (7) periodic detection + longitudinal tracking; (8) global/local/body-environment baselines; (9)
tracker-independence (largest vs longitudinal).

## Kill-switches (frozen thresholds)
- **K1 storage individuation** established iff DD ≥ 10 AND median off-diagonal contamination < 0.05 at safe
  separation. (DEV: DD ≈ 3000–7700, off ≈ 0.001 — large margin.)
- **K2 causal expression** established iff behavioural own-history decode R²_own > 0.50 AND (R²_own − R²_neigh)
  95% CI excludes 0.
- **K3 maintenance through turnover** established iff R²_own lower 95% CI > 0.50 at M ≤ 0.5.
- **K4 non-triviality:** if size+mass+position decodes own history as well as memory (CIs overlap), the result
  is NOT attributed to memory.
- **K5 tracker-independence:** DD and decodes must hold under both trackers.
- **Overall individuation** is claimed ONLY if K1 ∧ K2 ∧ K3 ∧ K4(memory advantage) ∧ K5. Any failure →
  documented negative + architecture proposal (Experiment 2 / boundaries).

## Execution
Prospective family 51001–51012 executed ONCE after this freeze; confirmation 52001–52012 once. No threshold
adjustment after observation. Observed/inferred/falsified/speculative labelled explicitly in the report.

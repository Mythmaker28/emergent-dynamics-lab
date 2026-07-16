# LCI-CAUSAL-TURNOVER-PREREG-03 — Phase 6: Global channel audit

*Does the global `up_ref` channel (or the common environment) resynchronize the droplets during turnover, such that
a surviving "own" signal is really the global history? Audited IN the turnover regime, not extrapolated from rest.*

## 1. The channel

Memory writing is `Ψ = tanh( k_exp·(N − c) + k_up·(uptake − up_ref) )` with `up_ref = mean uptake over all alive
cells` (`sc_mcm/engine.py:103–104`). The `(N − c)` term is **local** (per-cell fields); `up_ref` is the **only
world-global scalar** in the write. Additional global-ish couplings are field diffusion (`D_N=0.5, D_c=0.68,
D_m=0.010`, all **local**, decaying with distance) and uniform nutrient replenishment `F·(N0−N)` (a spatially uniform
relaxation, not droplet-to-droplet).

## 2. Prior characterization was rest-only

`P0_TECHNICAL_AUDIT.md` measured up_ref at rest (120-step drive): far |Δm| ≈ 8e-6, "does not synchronize distant
droplets." That is a **rest** statement. Turnover is 600–900 steps of continuous rewriting with the histories no
longer reinforced, so the concern must be re-measured in-regime.

## 3. In-regime measurement (DEV feasible seeds)

**Write-signal decomposition at the deep snapshot** (seed 50002, `M_i≤0.25`):

```
|k_exp·(N − c)|              mean = 5.56e-01      (LOCAL term)
|k_up·(uptake − up_ref)|     mean = 3.24e-04      (global-influenced term)
ratio global/local          = 6e-4               up_ref = 2.5e-04
```

The global-influenced term is **~1700× smaller** than the local term. `up_ref` itself is small and *declines* over
turnover (~3.6e-4 → 2.5e-4 across all feasible seeds). **Conclusion: up_ref cannot resynchronize the droplets — its
in-regime contribution to writing is ~0.06 % of the local term.**

## 4. Memory DOES homogenize — but locally, not globally

Inter-droplet spread of deep memory `m₊` shrinks over turnover in all 4 feasible worlds:

```
seed 50002: std 0.067 -> 0.054      seed 50004: 0.045 -> 0.032
seed 50005: 0.071 -> 0.007          seed 50007: 0.064 -> 0.049
```

and the *ordering* of droplet m₊ values changes (e.g. 50002 [0.249,0.095,0.221] → [0.15,0.173,0.274]). This
homogenization is driven by **local** forgetting (`η_d`), templating (`η_t`), and diffusion (`D_m`) as the reinforcing
histories fade and all droplets settle into similar neutral local environments — **not** by up_ref (§3). This is the
mechanism behind the graded-storage degradation (deep own-dose decode fails), and it is a *different* failure mode
from global synchronization.

## 5. The key dissociation: spatial locality survives, graded content does not

The interventional own-effect stays sharply own-specific at depth (own +0.131; own−neigh world-CI [0.114, 0.148] > 0;
own−sham [0.114, 0.148] > 0; neighbour and sham ≈ 0; **4/4 worlds**). This survives **because each droplet's memory is
spatially co-located with it**: erasing droplet i's memory reduces i's local coupled feeding regardless of whether the
graded magnitudes have homogenized. So:

> **Spatial-locality individuation survives turnover (interventional). Graded-content individuation does not
> (metrological homogenization).** The global up_ref channel explains neither — it is negligible in-regime.

## 6. Pre-registered global-channel controls (for the confirmatory family)

1. **In-regime write decomposition** (§3) reported per world; flag if global/local ratio ever exceeds a pre-declared
   bound (e.g. 0.05).
2. **`up_ref`-neutralized diagnostic** — a `up_ref := 0` engine variant (keeps the local `uptake` term, removes the
   global reference). If own-specificity is unchanged, up_ref is causally irrelevant. (An easier `k_up = 0` variant
   removes the whole uptake-surprise term and bounds the same thing from above; both are counterfactual diagnostics,
   not the main line.)
3. **Own vs neighbour vs global-mean history decoders** — decode own dose from (a) own-region deep features, (b) the
   neighbour's, (c) the world-mean-history features. "Individuation" requires own to beat both neighbour and
   global-mean prospectively. (DEV: own-dose 0.135 vs neigh-dose 0.580 at n=12 — underpowered and *not* passing;
   this is the rung most likely to fail prospectively.)
4. **Permuted-history control** — assign each droplet a neighbour's history label; own-decode must collapse.
5. **Inter-droplet memory spread** (§4) reported as a homogenization trajectory; not gating but interpretive.

Individuation may be claimed only if, prospectively, own remains separable from **both** neighbour **and** global.

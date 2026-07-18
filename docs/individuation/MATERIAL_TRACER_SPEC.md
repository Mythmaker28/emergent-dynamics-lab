# LCI-CAUSAL-TURNOVER-PREREG-03 — Phase 3: Material tracer spec & separated definitions

*Per-target passive material tracer for the frozen scaffold/MCM engine, and the strictly-separated M / P / F / G
measurements. No composite score. Implementation: `experiments/individuation/material_tracer.py`.*

## 1. Tracer design (strictly observational, zero engine change)

At the rest snapshot `S0`, for each of the 3 targets, append one passive origin cohort to the state's cohort array:

```
tracer_i  :=  rho · region_mask_i          (droplet i's current mass, labelled)
C  ->  concatenate(C, [tracer_0, tracer_1, tracer_2])      # indices base, base+1, base+2
```

The frozen engine then advects, death-scales, and feeds `C` exactly as before. Two facts make this a correct,
non-perturbing material tracer:

1. **No physical feedback.** The engine reads `C` only to move it (advection with the flux, homogeneous death
   `×(1−k·dt)`, feed deposit into `active_feed_cohort`). `rho, U, V, c, N, Mf, uptake` evolve **without reading `C`**.
   Verified byte-identical (standard-C vs extended-C, max|Δ| = 0.0 over the full 850-step turnover horizon) and
   two-run deterministic (max|Δ| = 0.0).
2. **Tracers never receive feed.** `active_feed_cohort(step) = n_spatial + (step//tau_feed) % n_temporal < base`
   always (asserted at run start). So tracer_i only **decays by death** and **advects passively** — exactly "the
   snapshot material of droplet i." Feed grows `rho` into the pre-existing feed cohorts, i.e. "new material."

## 2. `M_i(t)` — material continuity (per droplet, measured not estimated)

On the bijectively-tracked region `R_i(t)` (mask of the component track `i` currently owns), with `den = Σ_{R_i} rho`:

```
M_i(t)          =  Σ_{R_i} tracer_i / den            own snapshot material still in region i
cross_{i<-j}(t) =  Σ_{R_i} tracer_j / den            neighbour j's snapshot material now in region i  (contamination)
new_i(t)        =  1 − M_i − Σ_j cross_{i<-j}        freshly-fed material
```

- `M_i = 1` at the start of turnover; **deep ≡ `M_i ≤ 0.25` for each of the three** (≥75 % replaced).
- This **replaces** the inherited analytic `(1−k·dt)^T` scalar. DEV: `M_i` is essentially **monotone** (0.96→0.19
  etc.; near-zero up-jumps) with **no feed-cohort periodicity artifact** (per-target tracers are immune to the feed
  cycle). Cross-attribution is reported explicitly and gates the world (any material handoff between droplets is a
  MERGE/AMBIGUOUS event → world invalid).

## 3. `P_i(t)` — phenotype continuity (separately reported, no composite)

From `detect()` (`SCEntity`) on the tracked component + the fields, each reported on its own:

- **size** (cells), **mass** (`Σ rho`), **radius of gyration** `rg`;
- **shape / localisation**: `janus` (interior polarity magnitude), `radial_u`, `interface` fraction;
- **basal uptake** (`specific_uptake`), **attractant** (`mean c` in region), **internal state** `mean_sig`;
- **viability**: alive = component present, `size ≥ min_cells`, non-censored.

## 4. `F_i(t)` — causal fingerprint (separate components, NOT one scalar)

The frozen confirm-02 battery (`nm.measure`, probe 0.25×5, N-standardise, horizon 40, bijective + fixed readout),
each contrast reported separately:

- `intact − erase-target` (own), `intact − erase-neighbour`, `intact − sham`;
- `ablation` (λ→0 manipulation check), `tracked` (bijective) and `fixed-mask` (tracker-free convergent);
- uptake vs growth vs attractant sub-effects.

Reported at **rest** and at the **deep** snapshot, with the deep/rest ratio (G5) — never collapsed to a single number.

## 5. `G(t)` — global coupling (separately reported)

- `up_ref` (global mean uptake over alive cells) and its trajectory;
- world-mean uptake; inter-droplet memory (m₊) spread and correlation;
- own→neighbour material contamination (`cross`), own→neighbour memory contamination;
- predictability of own dose from own features vs from global-mean features.

## 6. No composite

`M`, `P`, `F`, `G` are **never** summed into a "continuity score." Each isolates a distinct failure mode: a droplet
can keep its material (`M`) yet lose its causal own-specificity (`F`), or keep a positive interventional `F` yet lose
graded storage — these must not cancel in an average. The ladder (règle finale) is read rung by rung, each measure
standing alone.

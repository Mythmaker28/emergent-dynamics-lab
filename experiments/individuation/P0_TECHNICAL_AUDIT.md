# Phase 0 — Technical audit: locality channels on the frozen C1c engine

**Branch:** `exp/local-causal-individuation-00` (from the frozen-engine release tip 23b53ae; `main` and the
V4/release branch are untouched — a new branch pointer only). **Engine unchanged** (no new physics).
**Question:** can co-existing droplets receive *distinct local histories*, store their own, and express them
causally rather than the global history? V4 established that *globally-applied* history (h1) is
non-individuating; here we apply history **locally**.

## 1. World
The scaffold self-organizes from near-uniform low density into **~34 droplets** on a 64×64 periodic lattice
(dt=0.1). Cost ≈ 2.6 ms/step (2000-step warmup ≈ 5 s). Detection: connected components of {ρ>0.30}, ≥12 cells
(frozen `SCDetectionSpec`); uses only ρ, never a label or future response.

## 2. Local-signal channel (how to apply a strictly local history without label/future)
A fixed **spatial Gaussian patch** added to the nutrient field N, centred at a droplet's detected centroid at
drive-onset, σ = 0.8·r_g (min 3). The patch is a property of *space*, not of the droplet's identity: it uses
only the current ρ-based centroid (allowed), never the droplet's label, tag, or future response. Droplets
drift (chemotaxis) during a drive; the patch stays spatially fixed (a local *environment*), which is the
non-circular choice.

## 3. Global-synchronization channels (audited in the frozen engine)
1. **Write-signal global reference.** The memory write is Ψ = tanh(k_exp(N−c) + k_up(uptake − ⟨uptake⟩)),
   where ⟨uptake⟩ is the **global mean uptake over all alive cells** (`up_ref`, sc_mcm/engine.py:103). This is
   a genuine global coupling: driving one droplet shifts ⟨uptake⟩ (~19% in a pilot). **However**, its spatial
   effect on distant droplets' memory is negligible (see §4): the local (N−c) term dominates the write.
2. **Field diffusion.** N (D_N=0.5) and c (D_c=0.68) diffuse; memory m diffuses (D_m=0.010). This is the
   dominant contamination channel and it is **local** (decays with distance).
3. **Global nutrient replenishment** N ← N + dt·F·(N0−N), F=0.02421 — a slow, uniform relaxation; not a
   droplet-to-droplet coupling.

## 4. Quantified contamination vs distance (dev seeds 50001–50003, differential design)
A local drive (amp 0.03, 120 steps) on one target, compared to a same-seed no-drive counterfactual; |Δmemory|
in every droplet relative to the driven target:

| distance (cells) | relative |Δm| |
|---|---|
| 0 (target) | 1.000 |
| 13–16 (nearest neighbours) | 0.07 – 0.20 |
| ≥ 24 | < 0.01 (typically < 0.001) |
| ≥ 30 | ~ 0.000 |

**Contamination is a local diffusion halo that decays to <1% by ~24 cells.** The global `up_ref` term does not
synchronize distant droplets (far |Δm| ~ 8e−6).

## 5. Dev influence matrix (memory-write footprint, pairwise ≥ 24 cells)
Selecting K=3 targets pairwise ≥ 24 cells apart (size ≥ 45), the normalized influence matrix C_ij (perturb i,
measure |Δm| in j) is near-diagonal on dev seeds:
```
seed 50001 (dists 24.7–36.9):  off/diag ≈ 0.000–0.001 ; diagonal dominance ≈ 2957
seed 50002 (dists 27.7–35.3):  off/diag ≈ 0.000–0.001 ; diagonal dominance ≈ 7733
```

## 6. Feasibility verdict (dev, not prospective)
- **Storage individuation is achievable** on the frozen C1c engine **provided targets are separated by ≥ ~24
  cells** (a "safe separation" derived from the diffusion decay). Locally-applied histories remain local in
  memory (diagonal C_ij).
- **Still to be tested prospectively:** (a) *causal expression* — does droplet j's behaviour express its OWN
  history (not neighbours')?; (b) *maintenance through material turnover*; (c) *own-vs-neighbour history
  decode*; (d) independence from trivial size/mass/position; (e) tracker-independence.
- This does **not** reopen h2 on C1c and does not modify V4. It is a distinct question (local vs global
  history application) with a frozen engine.

## 7. Artefact watch
- Patch drift vs droplet motion (mitigated by fixed-space patch + short window; flagged for the tracker).
- Near-neighbour contamination (7–20% at 13–16 cells) → **enforce min-separation ≥ 24 in target selection**.
- The global `up_ref` term is a real coupling; report it explicitly and include the global-history and
  permuted-signal controls to bound any residual synchronization.

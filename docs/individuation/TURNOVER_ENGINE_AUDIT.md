# LCI-CAUSAL-TURNOVER-PREREG-03 — Phase 2: Turnover engine audit

*What turnover machinery already exists, what is reusable, and what must NOT be reused blindly. All findings are
from the frozen tip `9c8a62c`; the engine is not modified.*

## 1. The inherited turnover runner is inadequate on four independent axes

`experiments/individuation/exp1_maintenance.py` (the "K3 maintenance-through-turnover" runner from
LOCAL-CAUSAL-INDIVIDUATION-00) is the direct predecessor. It is **not safe to reuse**:

| axis | inherited behaviour | why it fails | this mission |
|---|---|---|---|
| material `M` | **analytic** `M_est = (1−k·dt)^TURN ≈ 0.21` — one global scalar, identical for all 3 droplets | measures no real per-droplet material; ignores advection, growth/shrink, exchange | per-target **passive cohorts**, `M_i` measured per entity (`MATERIAL_TRACER_SPEC.md`) |
| tracker | **old non-bijective overlap** (cadence 5, θ=0.1, no censorship) | the exact bug that inflated the merge incident ×4.8 (several tracks lock onto one fused blob) | **bijective tracker** with MERGE/SPLIT/LOST/AMBIGUOUS censorship |
| assay | re-reads memory features at depth; **no causal assay, no null** | cannot test causal survival; storage-decode only | frozen confirm-02 `nm.measure` battery at rest AND deep |
| controls | **no global-channel control, no sham/neighbour at depth** | cannot separate own from neighbour/global | `GLOBAL_CHANNEL_AUDIT.md` + own/neigh/sham at depth |

Its result (deep own-dose R²=0.37 [0.14,0.72] indeterminate; own-order collapses −0.66) was obtained under all four
weaknesses simultaneously, so it is uninformative as a certified turnover outcome — but its *direction* (graded own
storage does not clearly survive) is corroborated by this mission's DEV pilots (§5).

## 2. Legacy constants that must stay retired

From `sc_iom/config.py` (the LOCAL-CAUSAL-INDIVIDUATION-00 preregistration):

- `PROBE = ("N", "add", 0.50, 15)` — the **fusing** probe (cumulative +7.5 N0) that caused the merge incident
  (percolation to 52 % of the grid). **Replaced** by the frozen confirm-02 probe `uniform 0.25×5` (cum 1.25 N0).
- `M_LOW = 0.35` — the legacy depth. This mission uses the **deeper** `M_i ≤ 0.25` (per brief). Deeper is more
  demanding: it lengthens the turnover and (DEV §5) lowers feasibility.
- `G_TURNOVER_KEEP = 0.5` — an **arbitrary** retention threshold. The mission explicitly forbids re-inventing 0.50;
  any retention gate must be justified from the question and power, else stay secondary/descriptive.

## 3. The material machinery that IS reusable — and where it lives

- The **scaffold cohort field `C`** (`SCState.C`, `IOMState.C`) partitions `rho` and is transported by the same flux,
  scaled by homogeneous death, and grown only into `tracer.active_feed_cohort(step)`. Crucially **`C` never enters
  any physical rate** — verified: `rho,U,V,c,N,Mf,uptake` are byte-identical with vs without extra cohorts over the
  full 850-step horizon (max|Δ| = 0.0). This is the correct, non-perturbing substrate for a material tracer.
- The **pulse-chase temporal feed cohorts** (`reaction_diffusion/engine.py::TracerSpec`, n_spatial + n_temporal,
  `tau_feed`) are the engine's "old vs new material" design. They label material by feed-time-window so that a
  structure which keeps replacing material keeps shifting cohort composition — i.e. "new material" is the feed-cohort
  fraction. This mission adds **per-target** origin cohorts on top (Phase 3) because the built-in cohorts are not
  per-droplet.

## 4. Observables that must NOT be reused (category error)

`observables/continuity.py` (`material_retention` = Jaccard of **particle IDs**), `entities/tracking.py`
(`LineageTracker` over `particle_indices`, `minimum_image`, `box_size`), and `observables/phenotype.py`
(`ParticleState.positions/velocities`) are the **particle-dynamics** lineage. The individuation work is on the
**continuous scaffold field** (no discrete particles). Applying particle-ID Jaccard or particle phenotypes to the
scaffold is a category error. The scaffold material tracer is built from the cohort field `C`; the scaffold
phenotype comes from `detect()` (`SCEntity`).

## 5. The ten Phase-2 questions, answered

1. **Compute `M_i(t)` separately for three droplets** — per-target passive cohort `i` seeded at the rest snapshot as
   `rho·region_i`; `M_i = tracer_i mass in bijective region_i / total rho in region_i`. Per-droplet, not a shared scalar.
2. **Is a passive per-target tracer necessary?** — Yes. The built-in cohorts are per-spatial-region / per-feed-window,
   not per-droplet, and were seeded at world creation (already turned over by the rest snapshot). A fresh per-target
   label at the snapshot is required.
3. **Can the tracers be strictly observational, no physical feedback?** — Yes, verified byte-identical (max|Δ| = 0.0
   over 850 steps). Cohorts never enter any rate.
4. **Avoid the same material being attributed to two entities after contact** — read `M_i` only inside the
   bijectively-tracked region; cross-attribution (tracer_j found in region_i) is *measured* and reported, and any
   MERGE/AMBIGUOUS censors the world. Material that advects between droplets is thus visible, not silently mixed.
5. **Track three droplets bijectively during turnover** — `bijective_tracker.py`, one component ↔ one track,
   updated every step (10/10 unit tests pass).
6. **Detect fusion / division / loss / ambiguity** — the tracker's MERGED / SPLIT / LOST / AMBIGUOUS statuses. DEV
   §5: the observed failures are genuine **fission** (a 61-cell droplet → 38+22; a 105-cell → 68+36) and **loss**,
   not detector flicker.
7. **Define "new material"** — `new_i = 1 − Σ_j (tracer_j in region_i)/rho` = the fed/unlabelled fraction; deep ≡
   `M_i ≤ 0.25` (≥75 % new).
8. **Does the old turnover inject a fusing stimulus?** — No. Turnover here is **neutral** (no drive, no probe); the
   fusing `0.50×15` probe is retired. The causal probe `0.25×5` is applied only on assay branches, never on the
   turning-over world.
9. **Does writing continue during turnover?** — Yes; C1c is unchanged and memory writing is left active under a
   strictly neutral (no-drive) environment (justified/frozen in `PRESEAL_CANDIDATE_PROTOCOL.md` Phase 4C). A
   `eta_w = 0` **passive-decay null** is run as a diagnostic.
10. **Can up_ref / common environment resynchronize the memories?** — Audited in-regime: **no** — the global term is
    ~1700× smaller than the local write term at depth (`GLOBAL_CHANNEL_AUDIT.md`). Memory does homogenize, but by
    **local** forgetting/templating, not the global channel.

## 6. DEV corroboration (seeds 50001–50010, non-prospective)

Feasibility 4/8 eligible (50 %); failures are fission ×3 + loss ×1, **zero fusion**. On the 4 feasible worlds the
inherited "maintenance" question splits cleanly: the **interventional** own-effect survives to `M_i ≤ 0.25`
(own +0.131, sham/neigh ≈ 0, 4/4 worlds) while the **graded** own-dose decode does not (deep own-dose 0.135 vs
neighbour-dose 0.580, n=12, underpowered) — reproducing the direction of the inherited negative under a corrected,
per-droplet, bijective, causal design.

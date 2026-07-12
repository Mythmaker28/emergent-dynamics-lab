# EXP-RD-04 PROTOCOL — matched-null false-positive floor + prospective law-14 replication
**Preregistered and frozen before any EXP-RD-04 result is produced or inspected.**

## Purpose
A candidate rate near 4 % (pooled) / 28.6 % (law 14) is meaningless until the rate at which this exact pipeline
fires on something that is **not** an individual has been measured. EXP-RD-04 measures that floor with **matched**
nulls and, in the same units, prospectively replicates frozen law 14 on entirely unseen seeds.

## Frozen inputs
- **Law: 14 only.** Frozen from the preceding stage's own criterion. **No new laws.** No ranking, no visual selection.
- **Seeds: 14001–14040 (40 entirely unseen).** Never used in any prior stage.
- Thresholds unchanged: ORGANIZED_P 0.8, TURNOVER_M 0.5, PLACEBO_MARGIN 0.25, DET.threshold 0.25, DET.min_cells 12,
  SITE_RADIUS 10.0, DELTA (20,20), HORIZON 750, LAGS (1,3,6). Enrollment `t*` from the frozen reference cadence 50.
  No composites. No post-hoc null redesign.

## Matched-null design (pairing requirements)
Every arm below is generated from the **exact same pre-intervention state `s*`**, displaced to the **exact same
destination** `old_centroid + DELTA`, with the **exact same support geometry** (the detected mask, S0) and the
**exact same perturbation magnitude** `|DELTA|`. All arms are scored by the **identical frozen readout**.

| arm | cargo | what is matched | what is destroyed |
|---|---|---|---|
| CONTROL | nothing displaced | — | — |
| SHAM | zero displacement | exact no-op (verified bit-for-bit) | — |
| PERTURBED-INTACT | the detected entity (U, V, all temporal cohorts) | — | — |
| **NULL-SC** (scrambled) | same cargo, cells randomly permuted **inside the support**, the same permutation applied to U, V, CU, CV | state, destination, support geometry, **total U mass, total V mass, per-cohort mass, the full multiset of per-cell values**, perturbation magnitude — **exactly** | **internal spatial organization only** |
| **NULL-NE** (non-entity) | same support geometry sampled at a non-entity location (mean V below detection) | state, destination, geometry, magnitude; conservative (no rescaling) | organization *and* mass — the mass/composition mismatch is **reported**, not hidden |
| **NULL-NE-M** (non-entity, mass-matched) | NULL-NE rescaled so total U mass, total V mass and cohort composition equal the intact cargo's | state, destination, geometry, magnitude, **total U/V mass, cohort composition** | organization; **rescaling is non-conservative — the injected/removed mass is reported per unit** |
| PLACEBO | matched non-candidate support, same cell count, same DELTA (unchanged from RD-02/03) | — | — |
| ambient-target control | CONTROL scored at the destination site | — | — |

**NULL-SC is the decisive null**: it matches every low-order statistic the protocol could be responding to and
destroys only the organization. If the scrambled cargo re-establishes as often as the intact one, the transported
*organization* carries nothing and individuality is refuted.

## Endpoint (identical for every arm)
**AUDITED_ROBUST** = AUDITED under **all 9** offline observer settings (cadence {25,50,100} × site-radius scale
{0.8,1.0,1.2}), where AUDITED requires jointly: SHAM ≡ CONTROL; re-establishment at the new site
(frac_new_organized > 0.5); exceeds PLACEBO by > 0.25; **no old-site regeneration**; and **continued temporal-cohort
turnover** after recovery (min M < 0.5 at lags 1,3,6) — a frozen lump is a failure. Physics is computed once per
branch; the 9 observer settings are pure offline re-observations of that same stored trajectory (fixed `t*`).

## Predeclared statistics
- `p_intact` = AUDITED_ROBUST / enrolled. `p_null` = pooled AUDITED_ROBUST over **NULL-SC + NULL-NE + NULL-NE-M**
  (denominator 3 × enrolled). Wilson 95 % intervals on every rate; denominators always stated.
- **Newcombe hybrid-score 95 % CI** on the difference `p_intact − p_null`.
- **Exact two-sided McNemar** (binomial on discordant pairs) for the paired comparison **INTACT vs NULL-SC**.
- **MARGIN = 0.10** (absolute).

## Decision rule (frozen; all three conditions required)
The candidate **SURVIVES** iff:
1. **S1** `p_intact` > 0 on the prospective unseen seeds (nonzero), **and**
2. **S2** the Newcombe 95 % lower bound of (`p_intact` − `p_null`) **> 0.10**, **and**
3. **S3** exact two-sided McNemar p < 0.05 for INTACT vs NULL-SC.

If **any** condition fails → **candidate WITHDRAWN and classical Gray-Scott RETIRED**, and the next step is a
motile open-system substrate.

## Stopping rule
**No sequential stopping. Fixed N = 40 seeds.** Interim results are not inspected for a stopping decision. If
runtime forces truncation, the actual denominator is reported and the result is declared **INCONCLUSIVE** — the run
is never stopped on a favourable interim.

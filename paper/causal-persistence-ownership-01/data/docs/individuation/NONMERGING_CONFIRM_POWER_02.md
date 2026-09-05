# NONMERGING_CONFIRM_POWER_02 — power analysis & family sizing (frozen pre-data)

*DEV-calibrated power for LCI-CAUSAL-NONMERGING-CONFIRM-02. Uses DEV effect estimates ONLY to size the family;
the probe was selected by geometry (not this effect), and NO positive claim is drawn from DEV. `power_explore.py`.*

## World-level effect (DEV, 8 worlds, world = mean over 3 targets), probe uniform 0.25×5

| horizon | own mean ± sd | need_n (own) | own−sham | own−neigh |
|---|---|---|---|---|
| 30 | +0.168 ± 0.050 | 0.7 | ≡ own (sham≈0) | ≡ own (neigh≈0) |
| **40** | **+0.218 ± 0.063** | **0.7** | ≡ own | ≡ own |
| 60 | +0.308 ± 0.084 | 0.6 | ≡ own | ≡ own |
| 80 | +0.396 ± 0.111 | 0.6 | ≡ own | ≡ own |
| 120 | +0.591 ± 0.158 | 0.6 | ≡ own | ≡ own |

`need_n = (2.8·sd/mean)²` = valid worlds for a one-sided worldboot lower bound > 0 at power ≈ 0.8 (α = 0.025).

## Key facts

- **need_n < 1 at every horizon** — the world-level own effect is large relative to its between-world sd
  (CV ≈ 0.29). Power is not the binding constraint.
- **sham and neighbour effects are numerically ≈ 0** (byte-level: e.g. −1.3×10⁻⁷). `own − sham` and
  `own − neighbour` therefore equal `own`; their worldboot lower bounds > 0 whenever `own` does. This is the
  strongest possible locality/specificity result (perfect confinement), not a fragile ratio.
- **Horizon = 40** chosen: geometry is safe at all horizons (coverage 3.3–3.7 %), and H = 40 gives the largest
  geometric margin and the cleanest (earliest) readout while remaining amply powered (need_n 0.7).

## Family sizing

- Unit = world. Required valid worlds for power ≈ 0.8: < 1. For scientific credibility (replication across many
  distinct worlds, not statistical necessity), the feasibility floor is set at **MIN_VALID_WORLDS = 12** — ~17×
  the power requirement.
- Historical initial eligibility (≥3 targets, size≥45, pairwise≥24): 54 % (confirm-01, 52xxx) to 80 % (DEV).
  Expected G0-validity of eligible worlds under 0.25×5: high (DEV 8/8 = 100 % non-fusing).
- At ~55–80 % eligibility × ~100 % G0-validity → ~0.55–0.80 valid worlds per seed.
- **Family sealed: 53001–53032 (32 seeds), cap 32.** Expected valid worlds ≈ 17–25 — comfortably above the
  12-world floor, with margin for feasibility failure (Case C) being pre-declared rather than patched.
- **No extension after seeing outcomes.** If valid worlds < 12 OR non-fusing fraction of eligible < 0.85 →
  **FEASIBILITY FAIL** (Case C), not a scientific result.

*Frozen pre-data. No positive claim from DEV. main/V4/release intacts. Rien poussé/mergé/publié.*

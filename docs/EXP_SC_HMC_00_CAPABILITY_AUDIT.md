# EXP-SC-HISTORY-MATERIAL-CONTINUITY-00 — PHASE 0 CAPABILITY & TRACER-PASSIVITY REPORT

Verdict: **`SUBSTRATE_OK`** (the substrate can support the phenomenon; thresholds set only afterward).
Raw: `results/sc_hmc/capability.json`. Seeds audited: 9401–9404 (+ 12/12 dev valid).

| # | Capability | Result |
|---|-----------|--------|
| Q1 | localized mesoscopic entity forms | 4/4 (e.g. size 23, rg 2.03) |
| Q2 | stable through the checkpoint window | 4/4 alive at t_c |
| Q3 | material genuinely exchanged (pulse-chase) | 4/4; labelled leaving 9.9→3.0, new entering 3.7→7.6 |
| Q4 | cohort field dynamically passive | **max physics deviation = 0.0** (bit-identical) |
| Q5 | material overlap decays | M: 0.73→0.49→0.34→0.28 |
| Q6 | N and c perturb without immediate destruction | 4/4 survive all 4 interventions |
| Q7 | entities coexist without filling the grid | occupancy ~0.07, 8 entities |
| Q8 | segmentation without tracker IDs | yes (detect is ID-free by construction) |
| Q9 | internal U,V persistent & functionally relevant | interior heterogeneity > 0; β·σ couples to uptake |
| Q10 | recovery / hysteresis | measured properly in P5 (co-evolved control), reported in dev results |

## Cohort-tracer passivity (K1)
Running the identical warmed state forward 200 steps under the 32-bin frozen tracer versus the 2-bin
pulse-chase tracer yields **bit-identical** rho, U, V, c, N, uptake (max |Δ| = 0.0) across all seeds.
The cohort field only advects/decays alongside rho and never feeds back into any physical update; the
pulse-chase measurement therefore cannot perturb the trajectory it measures. **K1/G3 PASS.**

## M(t0,t) partition dependence
At the final probe, M = {0.283, 0.283, 0.289} for detector thresholds {0.25, 0.30, 0.35} — the
material-continuity estimate is robust to boundary choice, not an artefact of one segmentation.

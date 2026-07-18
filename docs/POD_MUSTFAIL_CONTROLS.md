# POD MUST-FAIL CONTROLS

| # | control | required behaviour | observed |
|---|---|---|---|
| 1 | three collinear spatial N samples | fail conditioning | N_global/background/core/sectors couplings all ≈ 0.20 (collinear) |
| 2 | far-field-only references miss local drift | — | N/A — droplet fills the grid, no far-field region exists |
| 3 | near-field references causally contaminated | contaminated | whole-field N contam/drift ≈ 0.85 |
| 4 | tracker-based references create leakage | leakage | our references read only N/rho/c — **no tracker IDs**; a tracker-based one would leak |
| 5 | oracle masks improve conditioning | forbidden | masks derived from rho-observable only, not privileged U/V interior |
| 6 | insufficient temporal sampling loses bandwidth | bandwidth loss | drift τ≈40; sub-Nyquist sampling would alias (declared) |
| 7 | spatial averaging erases diversity | diversity loss | quadrant/global N means are collinear — averaging removed all spatial diversity |
| 8 | neighbouring droplet carries own response | contaminated | c_global (droplet-produced) contam/drift ≈ 0.64 |
| 9 | removing a discriminating reference collapses rank | rank collapse | dropping the derivative/c types leaves only the collinear N-mean group |
| 10 | common-mode contamination non-identifiable | lower bound | κ_i/a_i constant across N refs (spread 0.056) → CRD-03 lower bound |
| 11 | direct read of forbidden internal state helps but is oracle | classified oracle | reading σ = (u−v)/(u+v) separates response from drift, and is forbidden |
| 12 | passive logging changes trajectories | zero change | logged vs unlogged trajectories byte-identical |

All controls behave as required. Controls 1, 3, 7, 10 are the load-bearing ones: they show the failure is
structural, not a tuning artifact.

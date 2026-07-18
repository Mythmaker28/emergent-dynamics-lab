# PASSIVE-OBSERVABLE INVENTORY — scaffold droplet substrate

Read-only audit of every observable derivable from `SCState` without touching `engine.py`, `β`, `D_int`, or any
governing equation. State fields: `rho` (cohesion), `U, V` (internal bistable identity network, extensive),
`c` (attractant, PRODUCED by rho), `N` (external nutrient), `C` (material cohorts), `uptake` (behaviour).

| candidate | source | spatial support | segmentation? | tracker? | contamination risk | drift coupling | passive? | verdict |
|---|---|---|---|---|---|---|---|---|
| N_global | N | whole grid | no | no | HIGH (uptake depletes N) | strong (~0.20) | yes | contaminated |
| N_background | N | low-rho cells (rho-quantile mask) | mask from rho only | no | HIGH | strong (~0.19) | yes | contaminated |
| N_core | N | high-rho cells | mask from rho only | no | HIGH | strong (~0.21) | yes | contaminated |
| N_sectorTL/BR | N | fixed quadrants | no | no | HIGH | strong, **collinear** with N_global | yes | collinear + contaminated |
| N_laplacian | N | whole grid (diffusion filter) | no | no | LOW (0.11) | **weak (~0.003)** | yes | does not observe drift |
| N_flux | N | whole grid (gradient) | no | no | LOW (0.07) | **weak (~0.005)** | yes | does not observe drift |
| c_global | c | whole grid | no | no | HIGH (droplet-produced, downstream) | strong (~-0.50) | yes | contaminated |
| uptake | uptake | — | — | — | IS the response | — | — | the QUANTITY, never a reference |
| U, V, sigma | internal state | — | — | — | — | — | **reads identity directly** | ORACLE — forbidden |
| C cohorts | C | — | — | requires cohort labels | — | — | tracker-adjacent | excluded (leakage risk) |

**Why no clean far-field reference exists.** At the frozen initial-condition family the droplet fills the 64×64
grid (rho > threshold almost everywhere), so there is no region "far from the droplet." Every N reference sits
inside the uptake footprint.

**The structural obstacle.** The causal response is a change in **uptake**, and uptake **depletes N**. So the
response and the environmental (nutrient) drift act through the *same field* N. Any reference that observes the
nutrient drift also observes the droplet consuming nutrient — i.e. the response. This is not a defect of a
particular reference; it is the geometry of the substrate.

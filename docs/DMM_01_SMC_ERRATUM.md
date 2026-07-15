# DMM-01 — SMC-01 Interpretive Erratum (committed before mechanism work)

SMC-01 concluded "h2 does not survive turnover" from a single forward trajectory in which elapsed time,
memory diffusion (D_m·lap), templating (eta_t·(_tmean−m)), forgetting (eta_d), and material replacement all
changed together. That trajectory **cannot** attribute the loss to constituent turnover specifically.

Replace: "h2 is material-bound" / "turnover erases h2"
With: **h2 decays during the tested turnover trajectory; the causal decomposition between temporal
relaxation, maintenance homogenization (templating+diffusion smoothing), and constituent dilution remains
required.** DMM-01 Phase A performs that decomposition.

Code facts established this session (grounding):
- Templating `eta_t·(_tmean(m)−m)` = `0.25·eta_t·lap(m)`; with `D_m·lap(m)` the memory field is smoothed with
  effective coefficient ≈ 0.25·0.010 + 0.010 = 0.0125/step. Both terms are spatial LOW-PASS filters that
  reduce the value-dispersion h2 rides on.
- New material inherits the LOCAL intensive memory (`Mf += g·m`), and death scales all fields uniformly, so
  growth/death largely PRESERVE intensive memory. This predicts the dispersion loss is homogenization, not
  zero-memory dilution — to be tested, not assumed.

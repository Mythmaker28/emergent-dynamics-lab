# Authoritative feasibility and family-size specification — PRESEAL 03C

## Inputs

DEV observations are exploratory: 8/10 geometrically eligible and 4/8 feasible among eligible. Claude's corrected
Jeffreys-prior propagation used:

- eligibility `Beta(8.5, 2.5)`;
- feasibility conditional on eligibility `Beta(4.5, 4.5)`.

Under that declared model, the parent 50-seed plan had only `P(N_valid >= 18) = 0.57`. The repaired total cap of 96
has `P(N_valid >= 18) = 0.93`.

## Reconciled family

- Primary: `54001-54050` (50).
- Reserve: `54051-54096` (46).
- Hard cap: 96 total.
- Minimum valid worlds: 18.
- Reserve trigger: all primary complete AND valid-world count below 18.
- Reserve stopping: first point at which 18 valid worlds exist, otherwise seed 54096.

The trigger uses feasibility only. No response, dose, causal contrast, decoder score, or confidence interval can
activate or stop the reserve.

## Interpretation

The 18-world floor is a minimum analysis condition, not a guarantee of detecting an arbitrarily small effect.
If the cap ends below 18 valid worlds, report feasibility failure. Do not extend the family or weaken the gate.

The direct feeding contrast is not the sizing target because it is algebraically coupled and was already
over-powered in DEV. The binding target is grouped comparison of target-local memory against neighbour,
target-memory-masked environment, and body baselines.

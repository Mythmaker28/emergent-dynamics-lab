# EXP-SC-IOM-00 — MECHANISM EQUATIONS, MINIMALITY RATIONALE, METHODS

## Memory-mechanism equations (deliverable 3)
Extensive memory Mf[k] = rho * m_k, k in {1,2}. Per step (dt=0.1), on the scaffold rho:
- advection: Mf advects with rho by the SAME donor-cell face-flux scheme used for U,V (reused, unchanged);
- growth inheritance: newly grown mass g acquires the local memory, Mf += g * m  (impression);
- homogeneous death: Mf *= (1 - dt*k)  (turnover; concentrations invariant);
- intensive update on m_k (alive cells): m_k += dt*(eta_w*Psi - eta_d[k]*m_k + eta_t*(T(m_k)-m_k) + D_m*lap(m_k)); clip to [-1,1];
- experience signal: Psi = tanh(k_exp*(N - c) + k_up*(uptake - <uptake>)), local only;
- templating: T(m) = 4-neighbour periodic mean (self-maintenance + coherence);
- functional coupling: uptake_eff = uptake*(1 + lam_m*tanh(m1+m2)).

Selected (development) parameters: eta_w=0.05, eta_d1=0.03, eta_d2=0.003, eta_t=0.01, D_m=0.01, lam_m=0.25,
k_exp=2.0, k_up=1.0, n_comp=2.

## Minimal-parameter rationale (deliverable 4)
- Two components (not one): a single leaky scalar cannot separate A->B from B->A at a common final
  environment; two timescales (fast m1, slow m2) are the minimal store that records order. (Order is thus
  WRITTEN; the scalar coupling's failure to READ it is reported, not hidden.)
- One functional coupling (Section 7 "one minimal coupling"): uptake only. This is deliberately minimal;
  the individuation failure is a direct, interpretable consequence of that minimality.
- No never-decaying / lab-frame-fixed / unique-initial field; all entities start m=0. No tags (G12).

## Backward compatibility (deliverable 7)
lam_m=0 -> base fields bit-identical to frozen engine (verified max deviation 0.0 over 300 steps);
eta_w=lam_m=0 -> memory identically 0.

## Experience protocols (Section 11) and counterfactuals (Section 12)
Four matched-dose histories ending in the same neutral environment: H1 (N-rich then c-rich), H2 (c then
N), H3 (alternating), H4 (neutral). Counterfactuals hold the body fixed and vary only memory: ERASE
(Mf->0), TRANSPLANT (donor memory into a common erased body B0, and cross-body), SCRAMBLE (permute memory
within the entity), ABLATION (lam_m=0), EXACT CLONE (independent environmental noise -> stochastic ceiling).
Causal claims rest on probe RESPONSES, not on reading m (privileged diagnostic only).

## Continuous-history individuation (Sections 14,15)
Sectored histories assign independent nutrient-boost amplitudes to 4 spatial quadrants (a continuous
4-parameter history family) -> can write high-cardinality spatial memory. Memory dimensionality (PCA
participation ratio), within- vs between-history distances, individuation AUC, and LOO decoding of the
history parameters from the CAUSAL response are reported for dev and prospective families.

## Splits (deliverable 6)
Development trajectories 30000-30039 and history seeds 30100-30103; prospective 31000-31031 and 31100-31103.
The sealed HMC prospective (9501-9516) and the HSI held-out family are NOT reused.

## Parameter grid (deliverable 5, preregistered in config.PARAM_GRID)
eta_w in {0.03,0.05,0.08} x eta_d2 in {0.003,0.001} x lam_m in {0.15,0.25}; weakest passing preferred.
The default point above passes all memory-property gates; individuation fails structurally (coupling
dimensionality), which no grid point in this family can fix -> a design change, not a tuning change, is
required (next-project decision).

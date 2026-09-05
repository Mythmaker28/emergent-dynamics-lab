# Exact model notes for manuscript integration

Source revision: `06fd9524f5c7ffb329ee850a10bd9959f2f0bde5`. All values below are read from static source, without importing the engine. `source_check.py` independently extracts the numeric dataclass defaults and C1c/beta overrides to `SOURCE_CHECK.json`. This is source verification, not a new simulation.

## Update law and ordering

The grid is a periodic 64 x 64 square lattice; cell spacing is the numerical unit and dt = 0.1. The code transports density rho, extensive fields U = rho*u, V = rho*v, two extensive memory fields Mf_k = rho*m_k, and passive tracer fields. Nutrient N and attractant c are separate fields. `lap(f)` is the four-neighbour sum minus 4f.

For the face from x to x+e, let dc=c(x+e)-c(x), rho_up/rho_dn be selected by the sign of dc, and

`chi_face = chi0 / [1 + ((c(x)+c(x+e))/(2*c_sat))^2]`.

The density face flux is

`J = chi_face*dc*rho_up*max(0, 1-rho_dn/rho_max) - D_rho*(rho(x+e)-rho(x))`.

Density receives minus the discrete divergence of J times dt. Each extensive field follows the same signed flux times its donor concentration, using the sign of the total J for donor selection. Do not substitute a continuum equation without identifying it as a schematic: the exact clipped split-step scheme is authoritative.

After transport, form `sigma=(u-v)/(u+v+epsilon)`, `m_plus=tanh(m1+m2)`, and

`g = clip(dt*g0*rho*N*max(0,1-rho/rho_max)*(1+beta*sigma)*(1+lambda_plus*m_plus), 0, max(N,0))`.

`g` is nutrient consumed during this one update (not an instantaneous continuous-time rate). Update N <- N-g, rho <- rho+g, U <- U+g*u, V <- V+g*v, Mf_k <- Mf_k+g*m_k, and add g to the active feed cohort. Then multiply rho, U, V, Mf and all cohorts by `1-dt*k`.

Internal concentrations next follow **mutual inhibition**, with alive mask `rho>1e-4`:

`u <- max[0, u + dt*(tau*(a/(1+(v/K)^2)-u) + D_int*lap(u)*alive)]*alive`,

and symmetrically for v with u and v exchanged, using the common pre-update values for both reactions. This is not the usual FitzHugh-Nagumo model. Recompute U=rho*u and V=rho*v.

The memory update uses the post-uptake/post-decay density and nutrient, the previous c, and the uptake g just recorded:

`up_ref = mean(g on alive cells)`;

`Psi = tanh(k_exp*(N-c)+k_up*(g-up_ref))`;

`m_k <- clip[m_k+dt*alive*(eta_w*Psi-eta_d,k*m_k+eta_t*(four_neighbour_mean(m_k)-m_k)+D_m*lap(m_k)), -1, 1]*alive`.

Set Mf_k = rho*m_k. The four-neighbour mean minus m is exactly lap(m)/4. Thus the two spatial-memory terms combine to `(D_m+eta_t/4)*lap(m)=0.0125*lap(m)`. The code's label "templating" does not create an additional attractor-restoration mechanism.

Finally, with m_minus=tanh(updated m1-updated m2):

`c <- c+dt*(D_c*lap(c)+s*rho_start*(1+lambda_minus*m_minus)-delta*c)`;

`N <- N+dt*(D_N*lap(N)+F*(N0-N))`.

`rho_start` is saved at entry to the update, before transport/growth/death. Reporting attractant production as using the final rho would describe a different integration scheme.

## Frozen numeric parameters

Generated numeric values are in SOURCE_CHECK.json. Scaffold: chi0=9.5, D_rho=0.07778, D_c=0.68, s=0.2, delta=0.06909, g0=0.06154, k=0.02588, F=0.02421, D_N=0.5, N0=1, rho_max=1, c_sat=1, a=2, K=0.5, D_int=0.008, tau=0.2, **beta=0.10** (the HMC override, not the ScaffoldSpec default 0.6). Numerical epsilon=1e-12.

Memory: eta_w=0.015, eta_d1=0.35, eta_d2=0.006, eta_t=0.01, D_m=0.01, lambda_plus=0.25, lambda_minus=0.15, k_exp=1, k_up=1. The plus-only ablation has lambda_plus=0 and lambda_minus=0.15. The full readout ablation sets both to zero; these are distinct controls.

Storage: 800 warm-up steps; choose three detected components of at least 45 cells separated by at least 24 cells; two nutrient-drive phases of 60 steps, with each target's phase amplitude sampled uniformly in [0.005,0.035] and Gaussian width max(3,0.8*radius_of_gyration). The label called own-dose is the sum of these two amplitudes, not a direct measurement of integrated nutrient uptake. Then settle 120 steps.

Random-number provenance: `turnover_engine_03g._storage` first calls `cc.seed_world(seed)` and later initializes `np.random.default_rng(seed)` for the six phase amplitudes. `cc.seed_world` calls `exp_sc_00.seed_state`, which also initializes `np.random.default_rng(seed)` for the random initial density and internal fields. These are separately instantiated generators reusing one seed and starting stream, not independently seeded substreams. This source fact limits claims of independent randomized history assignment; its quantitative effect on decoding is unknown. It does not itself invalidate the within-snapshot erasure comparison.

Turnover: unperturbed evolution with writing active, maximum 1500 steps; stop at the first step all three tracked targets meet M_i<=0.25, remain admissible and meet coverage conditions. The causal assays reset N to N0, settle 40 steps, then add 0.25 nutrient for five steps and measure integrated uptake over 40 steps. This is **nutrient standardization**, not evidence of natural washout. The historical confirmation runner's 120-step probe is not the 03G probe.

## Analytical reference, with its limits

Growth copying alone preserves intensive memory exactly:

`(rho*m+g*m)/(rho+g)=m`.

Uniform removal alone preserves it too:

`(q*rho*m)/(q*rho)=m`, q>0.

These identities explain why material replacement need not erase an intensive state. They do not predict the full simulation, which also transports, writes, forgets, smooths and clips memory. For a frozen state with unchanged body/nutrient and no uptake clipping, instantaneous fractional uptake reduction after zeroing m is `lambda_plus*m_plus/(1+lambda_plus*m_plus)`. A 40-step paired assay also includes feedback and state evolution, so this expression is a reference, not an exact replacement of that assay.

## Access scopes and material labels

L consists of 11 descriptive statistics of m1/m2 within the target. E computes radial means of eight fields over radii [0,6), [6,12), [12,24), masking **only m1 and m2** on the target. E therefore retains target density, internal state, nutrient, attractant and uptake. Gm likewise masks only target memory before global summaries. Neither removes the full target body; call them target-memory-excluded summaries. B uses target cell count, density mass/mean/std, u/v means, N mean and c mean.

The tracer labels rho inside each of the three initial target masks, not all pre-existing material in the world. M_i is the fraction of current target mass originating in its own initial mask. The complementary unlabelled fraction includes newly supplied material and material initially outside these masks. The gate constrains M_i, not the sum of all initial material. All 63 valid target values retain positive own-mask material (range and mean generated in SOURCE_CHECK.json). Recorded cross-target contributions are numerically tiny, but this does not relabel initially unmarked material as new synthesis. This scope must be clear in the main text or methods.

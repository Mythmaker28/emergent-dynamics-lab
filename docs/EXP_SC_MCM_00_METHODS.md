# EXP-SC-MCM-00 — READOUT EQUATIONS, MINIMALITY, STORAGE AUDIT, METHODS

## Read-out equations (deliverable 3; writing frozen from IOM-00)
m_plus = m1 + m2 ; m_minus = m1 - m2.
  uptake_eff       = uptake * (1 + lam_plus  * tanh(m_plus))     # channel 1 (dose; == IOM-00 when lam_plus=lam_m)
  c_production_eff = s * rho * (1 + lam_minus * tanh(m_minus))   # channel 2 (order; NEW)
Selected: lam_plus=0.25, lam_minus=0.15. Backward compat: lam_minus=0 -> IOM-00 bit-identical; lam_plus=lam_minus=0 -> frozen scaffold.

## Minimality rationale (deliverable 4)
Level R1 of the read-out ladder (two orthogonal scalar channels) is the weakest level tested and it passes
the order-read-out gates, so R2-R4 (cross-coupled, spatial-moment, extra components) were NOT used. The
second channel (attractant production) is an existing physical function, bounded, causal, independently
ablatable, measurable without reading m, and non-redundant with uptake (order appears only on the c axis).

## Storage-information audit (deliverable 2)
Order reproducibly stored in m- (100% held-out classification dev+prosp). Net exposure stored in m+.
Continuous magnitude / 4-sector spatial history NOT reproducibly stored (held-out R2 ~ 0.01 / -1.6): the
write signal Psi = tanh(k_exp*(N-c)+k_up*(uptake-<uptake>)) saturates, so storage is effectively ~1-D +
sign-of-order in viable regimes. Decision S1 -> freeze writing, expand read-out only.

## Experience protocols (deliverable, Section 11)
Discrete matched-dose H1 (N->c), H2 (c->N), H3 (alternating), H4 (neutral), amplitude 0.03, T=60 per phase
(gentler than IOM-00's 0.06 which saturates attractant c and disperses the droplet). Continuous family:
two independent phase nutrient-drives (p1 early, p2 late) in [0.007,0.024], matched to the memory's two
timescales; all histories end in the same neutral environment before read-out.

## Multi-axis response + isolation (deliverables 10,12)
R = [size, rg, uptake, mass, mean_c]. The memory read-out is isolated from history-induced body changes by
transplanting the entity's mean memory into a COMMON erased body and settling in a neutral environment;
the two channels then re-express the memory (uptake for m+, mean_c for m-). Erase / channel-ablation /
exact-clone-noise controls per axis.

## Splits (deliverable 6) and grid (deliverable 5)
Dev trajectories 32000-32015, continuous seeds 32100-32103; prospective 33000-33011 / 33100-33103. HMC,
HSI and IOM-00 held-outs are NOT reused. Read-out grid lam_plus in {0.15,0.25,0.30} x lam_minus in
{0.05,0.15,0.25}; writing parameters NOT retuned. Environment: python 3.10.12, numpy 2.2.6, scipy 1.15.3.

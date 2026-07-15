# From Material Turnover to Causal Memory: A Falsification Ladder for Organizational Continuity in a Simulated Droplet

**Title candidates**
1. From Material Turnover to Causal Memory: A Falsification Ladder for Organizational Continuity in a Simulated Droplet
2. One Dimension of Causal Memory Survives; A Second Does Not: Boundaries of Organizational Continuity in a Reaction-Transport Droplet
3. Decodability Is Not Memory: Prospective Causal and Turnover Tests of Engineered Organizational State in a Simulated Droplet

## Abstract
We ask whether a persistent simulated droplet can carry an internal memory of its experience that is causal,
transplantable, and robust to replacement of its constituent material. Using a reaction-transport "scaffold"
droplet with a designed two-component intensive memory field coupled to nutrient uptake (m+) and attractant
production (m-), we run a preregistered ladder of interventions with grouped, prospective, kill-switched
evaluation. We establish one positive result: a one-dimensional, engineered cumulative-experience coordinate
(h1) is prospectively decodable (R2~0.94), causally expressed through uptake and transplantable into a fresh
standardized body (R2~0.61), survives ~80% constituent turnover (R2~0.93, 95% CI [0.83,1.00] at old-material
fraction M~0.21), and exceeds trivial body-size/mass baselines especially after turnover. We then show, through
five successive experiments and their corrections, that a *second* candidate coordinate (h2, a temporal-order /
value-dispersion statistic) fails to qualify: it is decodable at rest but its causal response is ~1-D, its
turnover behaviour is family-dependent and underpowered, and an adequately powered sealed kill-switch returns a
deep-turnover effect near zero (h2 R2~-0.02 at M~0.21). Our methodological contribution is a falsification
ladder showing that high internal variation, decodability, and causal expression at rest each fail to imply a
turnover-surviving causal memory dimension, and that preregistered grouped evaluation and kill-switches prevent
indefinite mechanism escalation. We make no claim of life, agency, identity, reproduction or heredity.

## 1. Introduction
Biological individuals persist while their material turns over; persistence of *organization* rather than
*matter* is a candidate basis for biological memory and identity. We ask a deflationary, testable version of
this question in a simulated droplet: can an internal state encode the droplet's history in a way that is (i)
causal, (ii) separable from the current body and environment (transplantable), and (iii) maintained while the
constituent material is replaced? We stress that *decodability* of a history variable is insufficient — a
readout may exploit residual environment, body size, or laboratory-frame position — and that a memory worth
the name must causally shape dynamics and survive turnover. Individuation requires strictly more than
persistence and is not claimed here.

## 2. System and methods
**Droplet.** A periodic 2-D reaction-transport "scaffold" (64x64, dt=0.1) supporting a localized, viable,
self-maintaining density field rho with internal (U,V) chemistry, nutrient N and attractant c.
**Memory.** A designed bounded intensive field m=(m1,m2), extensive Mf=rho*m, written by a local experience
signal Psi=tanh(k_exp(N-c)+k_up(uptake-<uptake>)) on two time constants (fast eta_d1, slow eta_d2), spatially
templated (eta_t 4-neighbour mean) and diffused (D_m), and inherited by new mass (Mf += g*m during growth).
Readouts: m+=m1+m2 modulates uptake (lam_plus); m-=m1-m2 modulates attractant production (lam_minus).
Coordinates: for two-phase nutrient histories, h1=a_early+a_late (cumulative), h2=a_late-a_early (order).
The final frozen writing configuration (C1c) de-saturates Psi (k_exp 2->1) and speeds the fast component
(eta_d1 0.03->0.35, eta_w 0.05->0.015). The memory is ENGINEERED, not spontaneous; its persistence and causal
consequences are what we test.
**Turnover.** A passive pulse-chase tracer re-bins the (physics-inert) cohort field; old-material fraction M is
the old-cohort mass share of the entity. Tracing never enters the dynamics.
**Interventions.** Erase (Mf=0); mean-field and full-field transplant into a standardized erased body;
channel-specific readout ablation (lam_plus/lam_minus -> 0); exact-clone / stochastic ceiling.
**Statistics.** Grouped leave-history-out ridge decoding (rows sharing a history/donor kept together); no
row-wise LOO; development vs prospective separated; sealed prospective families (hashed before selection,
executed once); donor-level bootstrap CIs; shuffled-history, constant, and trivial-feature nulls.

## 3. Results
**3.1 Persistent organization under turnover (HMC/HSI).** The droplet remains a localized viable entity while
material turns over; a hidden internal state exists but behaves as a generic causal attractor, not a
history-specific identity (HSI individuation AUC ~0.3-0.4).
**3.2 An engineered causal memory, h1 (IOM/MCM).** The two-component field is causal and erasable (ablation
lam=0 removes the effect exactly), transplantable, and turnover-related; the initial causal readout collapses
onto a ~1-D cumulative coordinate.
**3.3 Temporal order made readable (MCM).** A second orthogonal readout (m- -> attractant) makes matched-dose
temporal order causally readable; the order contrast collapses ~70x/73x (dev/prospective) under lam_minus
ablation and is absent on the uptake axis.
**3.4 Apparent dimensionality corrected (WD-01 Phase B).** The original continuous-history "high-dimensional"
claim was an artefact of a 20-47x amplitude mismatch and replicate-leaking row-LOO; grouped evaluation reduces
the headline continuous R2 from 0.57 to 0.19; three estimators agree the frozen writing is rank ~1.
**3.5 Two-coordinate storage at rest (WD-01 Phase C).** A minimal de-saturating writing change (C1c) yields
two prospectively decodable coordinates at rest (h1,h2 ~0.94 held-out), sigma2/sigma1 rising 0.02->0.23; the
rank gate (0.30) is marginally missed (0.283).
**3.6 Causal-response collapse (WD-01 Phase C).** Despite 2-D storage, the causal response is ~1-D: h1 is
causally expressed (transplant 0.61, in-place 0.50) but h2 is not (mean-transplant -0.04, in-place 0.30).
**3.7 Family-dependent turnover (SMC-01 -> DMM-01).** h2 is a frame-free value-dispersion statistic (not a
resolvable geometric pattern; lab-frame edge collapses under translation). Its turnover behaviour is highly
family-dependent: an initial single-family "collapse" (SMC-01) did not replicate; a pooled analysis retained
h2 to M~0.58 (CI [0.57,0.97]) but deep turnover was indeterminate. The loss is neither smoothing (ablations
verified active but negligible on the decode; dispersion grows) nor dilution (new material passively inherits
h2 as well as old).
**3.8 Deep-turnover kill-switch (H2-CERT-01).** On a sealed family executed once, with M<=0.25 reached at full
viability (48/48), held-out h2 = -0.02 (95% CI [-2.17,0.93]) at M=0.21; new-material h2 = 0.28; all four seed
families fail. h2 does not qualify as a turnover-surviving causal dimension.
**3.9 The surviving result (h1).** h1 is prospectively decodable (0.94), survives deep turnover (0.93, CI
[0.83,1.00] at M=0.21), is causal and transplantable (0.61/0.50), collapses under the memory-inert control,
and exceeds body-size/mass baselines especially after turnover (0.93 vs 0.64 at M=0.21). It is low-dimensional
and cumulative by design; its scientific content is causal persistence through material replacement.

## 4. Discussion
Our ladder separates concepts usually conflated. (i) *Memory vs decodability*: a decodable history variable
(h2 at rest) need not be a memory. (ii) *Storage vs causal expression*: 2-D storage co-existed with 1-D causal
response. (iii) *Passive copying vs reconstruction*: local growth copies intensive memory into new mass by
construction, which is propagation, not active reconstruction toward a target. (iv) *Material replacement vs
organizational inheritance*: h1's information persists in the internal memory when body size no longer carries
it. h2 was closed by a preregistered kill-switch after adequately powered sealed evaluation, not by fiat.
Individuation would additionally require multiple independent, causal, transplantable, turnover-surviving
coordinates and lineage reconstruction — none demonstrated. The limitation is of the tested C1c architecture,
not proven of the substrate in general.

## 5. Limitations
Engineered (not emergent) memory; simulator-specific dynamics; small entities (~30-55 active cells); finite
seed families; designed two-phase histories; low-dimensional cumulative h1; explicit local memory copying
during growth; no reproduction; no active reconstruction; no identity/lineage claim; the transplant readout is
mean-field; substrate-general capacity untested.

## 6. Conclusion
A persistent simulated droplet can carry an engineered one-dimensional internal memory of cumulative
experience that is causally readable, erasable, transplantable, and robust to substantial material turnover.
A second decodable history coordinate did not qualify as an independent causal, turnover-surviving
organizational-memory dimension. We report this boundary as the result: decodability, internal variation, and
rest-state causal expression are each insufficient for turnover-surviving causal memory. h2 escalation is
closed on the current architecture; individuation, reproduction, and a genome are not warranted by the evidence.

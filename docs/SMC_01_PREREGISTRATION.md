# SMC-01 — Preregistration (committed before development/selection)

## 1. Hypotheses
H1 organizational spatial memory; H2 material residue; H3 environmental residue; H4 lab-frame artefact;
H5 measurement bottleneck (spatial readout expresses h2); H6 stored but causally silent. (See position.)

## 2. Frozen mechanism
C1c EXACTLY: eta_w0.015, eta_d1 0.35, eta_d2 0.006, eta_t0.010, D_m0.010, lam_plus0.25, lam_minus0.15,
k_exp1.0, k_up1.0. No writing/readout/dynamics change. Protocol: warm(C0,2000)→erase Mf→2-phase nutrient
history (a_e for T=60, a_l for T=60)→settle S=20. h1=a_e+a_l, h2=a_l−a_e. Band F_mid=[0.003,0.020] (viable).

## 3. Entity-centric spatial coordinate system
Center on circular centroid (periodic-safe, existing `detect`). Scale-normalize by rg. Three decoders compared:
- **DIST** (frame-free): [mean,std,p10,p50,p90] of m1,m2 over entity cells (10-D; the Phase C decoder).
- **GEOM-inv** (entity-relative, rotation/reflection-invariant): polar raster (4 r-bins × 8 θ-bins) of m1,m2
  about COM; descriptor = radial profiles + angular power spectrum |FFT_θ| (rotation-invariant) + m1·m2 radial cross.
- **LAB** (frame-sensitive): fixed absolute-grid raster of m1,m2 (translation/rotation-sensitive) — leakage probe.

## 4. Alignment rules
No principal-axis sign resolved using h2/labels. Symmetric bodies handled by rotation-invariant descriptors
(GEOM-inv uses |FFT_θ|, so orientation is marginalized). No history label ever enters representation.

## 5. Frame controls
Translation: same history at ≥3 grid offsets (place warmed body at shifted COM). Rotation/reflection: applied
to the entity raster. Pass = h2 decodable by DIST and GEOM-inv, invariant to translation/rotation/reflection;
LAB decoder must NOT exceed frame-free decoders (else lab-frame leakage → H4).

## 6. Turnover (PulseChaseTracer, passive; existing metric M = old-cohort mass fraction)
After history, relabel all material as "old" (cohort 0), run C1c forward; new growth feeds cohort 1.
Checkpoints M≈{0.75,0.50,0.25,≤0.15}. At each: decode h2 from current memory (DIST, GEOM-inv); viability.
Controls: static no-turnover; fresh snapshot-matched; erased; shuffled-memory; old-material-disrupted.
Pass P4 = h2 decodable at M≤0.25 from continuing organization, above shuffled/old-material-map nulls.

## 7. Environmental reset
Compare decode/response for: (1) full post-history; (2) env reset (N,c standardized), memory kept;
(3) memory erased, env kept; (4) both erased; (5) transplant, env standardized. Pass P3 = h2 follows memory.

## 8. Structured transplant T0–T7 (fresh standardized recipient body B*, no donor material/env)
T0 erase; T1 mean-only; T2 full-field structured (map donor entity-relative m1(x),m2(x) into recipient by
COM-aligned nearest-cell, no labels); T3 spatial scramble (permute cell values, keep histogram+means);
T4 rotate; T5 reflect; T6 component-misalign (different transform to m1 vs m2); T7 matched-moment (payload
with same m+,m− means but different pattern). Correctness tests: donor material/env/tracker NOT transferred.

## 9. Spatial causal response observables (already-existing dynamics; kept separate, no composite score)
attractant dipole |∫c·r̂|, quadrupole, uptake anisotropy, polarization magnitude+direction, COM drift over a
fixed settle. Decode h2 from each and jointly; the memory-isolated effect = full − both-ablated on same body.

## 10. Decoders / hygiene
Linear ridge, **grouped leave-history-out** (rows sharing a history/donor in one fold). Nulls: constant,
shuffled-history, shuffled-spatial-pattern, same-law/different-seed, exact-clone. No row-LOO. Donor-grouped bootstrap CIs.

## 11. Development seeds {36001,36002,36003}. Prospective seeds {36501,36502,36503} (disjoint from 32-35xxx).
N_hist=14 dev / 12 prospective. Novel h1/h2 values (see sealed manifest).

## 12. Gates: G1–G29 (see mission §17). Rank criterion: σ₂/σ₁ vs shuffled-null (report 0.30 reference).
Primary causal threshold: h2 causal R² ≥ 0.50 (structured transplant, held-out, grouped).

## 13. Stopping rule
If a load-bearing prerequisite fails (storage replication, frame, turnover), run only diagnostic controls and
report the failing Outcome; do not run downstream positive-claim tests. If all pass, freeze→prospective once→report.

# METHODS PAPER — OUTLINE & PUBLICATION PACKAGE
## "Identifiability limits of reference-based drift correction for factorized causal-response decomposition"

The passive-observable FAIL does **not** invalidate this paper; it *instantiates* its central theorem on a physical
substrate. The paper stands on the ground-truth results alone.

## Title / thesis
Reference-based drift correction can recover factorized causal-response components under heavy drift **iff** the
reference contamination is *differential*; *common-mode* contamination is exactly unidentifiable without an
absolute scale. Demonstrated in ground truth and confirmed as the binding obstacle on a physical droplet substrate.

## Central theorem statements
- **T1 (dilution).** RMS-over-window differencing dilutes a transient difference as √(W/W′) → 0; an integral
  (E_trans) does not. (CFP → CRD-00.)
- **T2 (common-mode acquisition).** A matched sham calibrates a band but cannot subtract a drift realization it
  never saw; a *shared* realization cancels to the noise floor. (CRD-01.)
- **T3 (paired-episode DiD).** Two separate referenced episodes with independent drift recover the response
  without an oracle twin — but a single reference leaves `s(1−ακ)`, indistinguishable from a smaller response.
  (CRD-02.)
- **T4 (identifiability, main result).** With references `r_i = a_i d + κ_i s`, drift-free signals
  `z_i = s(1−α_i κ_i)` span a 2-D space regardless of reference count; differential contamination is identifiable
  to κ≈0.002, common-mode is exactly unidentifiable. (CRD-03.)
- **T5 (physical instantiation).** On the scaffold droplet, the causal response (uptake) and environmental drift
  (nutrient N) share a field, forcing common-mode contamination (κ_i/a_i constant, spread 0.056). (POD.)

## Claims table
| claim | evidence | scope |
|---|---|---|
| differential contamination correctable to κ≈0.002 | CRD-03 dev + prospective 12/12 | synthetic ground truth |
| CRD-02 κ=0.12 failure fixed (E/E*=1.00) | CRD-03 D2/Q2 | synthetic |
| common-mode unidentifiable → lower bound | CRD-03 D4/Q5; POD | theorem + physical instance |
| collinear references abstain | CRD-03 D6/Q9; POD MF1 | synthetic + physical |
| passive droplet references are common-mode contaminated | POD contamination analysis | physical substrate |
| NO claim of droplet identity / continuity / transfer | — | explicitly out of scope |

## Figure plan
1. Dilution curve (E_trans integral vs RMS scalar).
2. CRD-01 shared vs independent drift cancellation.
3. CRD-03 identifiability diagram: differential vs common-mode subspace.
4. CRD-03 contamination frontier (corrected to κ≈0.35) + prospective table.
5. POD reference matrix: coupling diversity vs contamination; κ_i/a_i common-mode collapse.
6. Lineage v00→CRD-03→POD.

## Experiment lineage
v00 CFP (boolean→continuous transfer fail) → CFP-01/02/03 (BENCHMARK_INVALID, ill-posed target) → CRD-00
(factorized, sham cannot subtract a realization) → CRD-01 (shared-drift PASS, oracle twin, TRANSFER_NOT_ESTABLISHED)
→ CRD-02 (paired-episode, FAIL on contamination) → CRD-03 (redundant references, PASS, theorem) → POD (physical
references common-mode contaminated, transfer FAIL).

## Reproducibility checklist
- Content-addressed seeds; blocked-OU verified to 1e-15; privileged evaluators import no instrument code; freeze
  manifests (v00 6/6, CRD-01 4/4, CRD-03 4/4) hash-verified; prospective splits opened once under hash gates;
  all sources compile from disk; git fsck clean.

## Results requiring independent replication
- The CRD-03 identifiability theorem (currently demonstrated numerically + a symbolic linear-dependence identity;
  a full general proof is the main open theoretical task).
- The POD common-mode result on a higher-fidelity or localized-droplet substrate (where a far-field region exists).

## Candidate venues
Methods/complexity venues (e.g. PLoS Comp Bio methods, Physical Review E, or an identifiability/systems venue). A
short version fits a workshop on causal representation / identifiability.

## Preprint readiness
Ground-truth results, theorem statements, controls, and reproducibility are complete. The paper is a **methods +
limits** contribution and does not depend on droplet transfer succeeding.

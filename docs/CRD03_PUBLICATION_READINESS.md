# CRD-03 PUBLICATION-READINESS ASSESSMENT

**Central methodological claim.** Redundant passive references with *distinct* drift couplings, combined with
signed interventions, identify and correct **differential** reference contamination while preserving quantitative
factorized causal-response estimates under drift; **common-mode** contamination is provably unidentifiable without
an absolute-scale anchor, and is reported as a rigorous lower bound rather than a confident attenuated value.

**Strongest positive result.** The CRD-02 load-bearing failure (κ=0.12 reference contamination → silent 21%
attenuation, detection floor κ≈0.15) is corrected to E/E\* = 1.00, prospectively on an unseen system, with
contamination corrected out to κ≈0.35. 21/21 development cases, 15/15 development gates, 12/12 prospective cases,
all prospective gates.

**Strongest negative result.** Common-mode reference contamination (κ_i ∝ a_i) is exactly unidentifiable AND
undetectable by any passive-reference scheme (proved symbolically and confirmed numerically). On the ctrans
substrate no absolute-scale anchor is available (`ABSOLUTE_SCALE_UNAVAILABLE`), so this direction stays a declared
lower-bound limitation.

**Theorem / identifiability boundary.** Drift-free signals `z_i = s(1 − α_i κ_i)` span a two-dimensional space
regardless of reference count; the differential contamination `(κ_i − g κ_j)` is identifiable, the common-mode
direction is not. This is the sharp boundary between what redundant references can and cannot recover.

**Prospective evidence.** 12/12 unseen cases under a verified hash gate, opened once. No confident
contamination-induced attenuation outside the frozen allowance.

**Independent checks.** Privileged noise-free/drift-free evaluator importing no instrument code; symbolic algebra
(`sympy`) confirming the linear-dependence identity; 15 must-fail controls all failing as required; blocked-OU
matching the literal recurrence to 1e-15; content-addressed reproducible seeds.

**Remaining transfer gap.** `MAPPING_REQUIRES_NEW_PASSIVE_OBSERVABLE`: needs several co-recorded passive references
of *distinct* drift coupling on a physical substrate, plus a signed-intervention schedule. Common-mode remains a
lower bound absent an absolute scale. No physical/droplet demonstration exists.

**Recommended paper type.** A methods + identifiability-theorem paper: "Identifiability limits of reference-based
drift correction for causal-response decomposition." The theorem, the instrument, and the ground-truth prospective
validation are complete and self-contained; the physical transfer is explicitly out of scope.

**Minimum missing experiment for a stronger claim.** Co-record ≥3 passive references of distinct drift coupling on
a real (or higher-fidelity) substrate and demonstrate the differential-contamination correction and the
common-mode lower bound outside synthetic ground truth.

## Classification

    METHODS PREPRINT READY

Not `PEER-REVIEW SUBMISSION READY` (no physical validation; the theorem, while demonstrated, is stated
operationally rather than proved in full generality). Not `DROPLET RESULT PAPER READY` (no droplet experiment).
The result is a clean, honest methods-and-limits contribution with reproducible ground-truth evidence.

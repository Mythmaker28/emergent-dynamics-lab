# PASSIVE OBSERVABLE DESIGN — FINAL REPORT

## Verdict

    PASSIVE OBSERVABLE DESIGN: FAIL — CONTAMINATION DOMINATES

The frozen scaffold droplet substrate does **not** expose three passive references that are simultaneously
diverse, drift-observing, and low-contamination. The obstacle is structural and physical, not a tuning artifact.

## 1. The question

Does the droplet state expose ≥3 physically plausible, non-destructive reference observables with sufficiently
distinct couplings to environmental (nutrient) drift, and low enough causal contamination, to support CRD-03
admission? Calibration used only the permitted N handle and the declared internal-state initial conditions;
`β`, `D_int`, and the equations were untouched; the operational references never read privileged state.

## 2. What was found

- **Diversity exists at the level of reference TYPES** — N-field mean (a≈+0.20), N spatial-derivative (a≈−0.004),
  attractant c (a≈−0.50): coupling diversity 7.79, condition number 1.14. Spatial *sub-samples* of N are
  collinear (must-fail #1).
- **But the diverse, drift-observing references are common-mode contaminated.** Under a clean strong response
  (internal active vs inert), N_global/background/core carry the response at **contam/drift ≈ 0.79–0.90**, with
  `κ_i/a_i` constant across them (spread **0.056**). This is exactly the direction CRD-03 proved
  **unidentifiable** — the substrate hands us the worst case as its generic case.
- **The low-contamination references cannot observe the drift.** N_laplacian/N_flux have contam/drift ≈ 0.07–0.14
  but drift couplings ~50× below the measurement's, so the CRD-03 correction amplifies their noise ~50×.
- **No clean far-field region exists** — the droplet fills the grid.
- **Reading the internal state (`U, V, σ`) directly would separate response from drift — and is forbidden oracle
  access.**

## 3. Why (the physics)

The causal response *is* nutrient consumption (uptake, via the `β·σ` coupling), and uptake depletes the nutrient
field N. The environmental drift also lives in N. Response and drift therefore share one field, so every passive
observation of the nutrient drift is simultaneously an observation of the droplet consuming nutrient — the
response. Common-mode contamination is forced by this shared-field geometry.

## 4. Consequence for the programme

CRD-03's prospective PASS stands, in synthetic ground truth, exactly as reported. Its transfer to this droplet
substrate is **blocked at the observability layer**: the required non-collinear, low-contamination passive
references do not exist here. This is a clean confirmation of the CRD-03 theorem — the physical substrate realizes
its unidentifiable common-mode direction.

A different substrate (a *localized* droplet with a genuine far-field, or an environmental drift carried by a field
the droplet does **not** consume) could expose clean references. That is a substrate-design question and is out of
scope; no equation was modified to manufacture success.

## 5. Standing constraints

`SC-PILOT-CAUSAL-FINGERPRINT` remains **BLOCKED**. `EXP-SC-01` remains **BLOCKED**. The pilot was not executed. No
droplet equation, `β`, `D_int`, `rho`, `U`, or `V` was modified. Only passive read-only diagnostics were added.
Passive logging changes no trajectory (verified). CRD-01/02/03 stand unaltered; all freeze manifests intact.

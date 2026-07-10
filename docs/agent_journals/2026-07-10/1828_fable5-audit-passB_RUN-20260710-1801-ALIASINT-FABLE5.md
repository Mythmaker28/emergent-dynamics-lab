# Fable 5 Audit — PASS B (intervention / sham challenge)

- Auditor: Claude **Fable 5** (self-audit; no Opus 4.8, no subagent). Independent of PASS A's conclusions.
- Parent run: `RUN-20260710-1801-ALIASINT-FABLE5`.
- Questions: **Does the sham truly control the pipeline? Does the perturbation test the organization, or only
  banal physical fragility?**

## Objections raised and disposition

B1. *The Δ=0 sham equals control bit-for-bit, so it controls only the serialization/reinstantiation path — not
    the physical act of moving a clump.* — TRUE. `test_sham_is_pipeline_exact_noop` and
    `test_sham_trajectory_equals_control_bit_for_bit` prove the harness (copy -> select -> modify -> reconstruct
    -> resume) injects nothing: SHAM is a proven-non-perturbing pipeline/no-op reference. But a PERTURBED-vs-SHAM
    difference could therefore be generic "you moved six particles across the box" disturbance. **The PLACEBO
    branch (translate a matched non-candidate connected component by the same Δ) is the necessary active control.**
    The organization-specific claim requires PERTURBED to exceed PLACEBO, not merely SHAM/CONTROL. Folded into the
    decision rule. **Mitigated.**

B2. *Does the perturbation test "the organization"?* — Scope limitation stated honestly: a rigid off-site
    translation preserves internal structure, so it tests **site-binding (stationary occupancy) vs
    constituent-carrying (individuality)** — the DOMINANT unrejected alias per D-015 and the 0/47 direct-audit
    result. It does NOT test internal self-repair / re-establishment after structural disruption; that is a
    distinct future perturbation (out of scope here and declared as such). This matches D-015's specific
    requirement to "reject stationary spatial occupancy or sparse look-alike flux." **Accepted as scoped.**

B3. *Banal physical fragility: moving the blob into a new neighborhood may destroy it by collision.* — Handled
    two ways: (i) Falsifier F5 (catastrophic) fires if PERTURBED destroys the organization everywhere; (ii) the
    PLACEBO undergoes the identical new-site collision risk, so if PERTURBED and PLACEBO disperse equally that is
    generic fragility, not organization-specific. **Mitigated by PLACEBO + F5.**

B4. *Fixed Δ could hit a lattice resonance / symmetric image.* — Δ=(0.30,0.30) is generic w.r.t. the random
    other-particle configuration and is applied identically to the PLACEBO, so any Δ-specific artifact is
    controlled. A fixed pre-declared Δ also avoids per-run tuning. Each component 0.30 < box/2 (unique minimum
    image); |Δ|min-image = 0.424 > tracker gate 0.16 and > detection radius 0.11 (off-site). **Resolved.**

B5. *Energy/momentum injection.* — Velocities are untouched, so total momentum and every particle velocity are
    conserved (`test_perturbation_conserves_globals...`). Translation does change potential energy (new
    neighbors) — inherent to any displacement and matched by the PLACEBO. No net kick/boost is introduced.
    **Resolved.**

## PASS B verdict

The Δ=0 sham is a valid, proven-non-perturbing pipeline control, but insufficient on its own; the matched
PLACEBO is the load-bearing active control and the decision is comparative. The perturbation legitimately tests
the occupancy/look-alike alias (its declared purpose), not internal self-repair (declared out of scope).
Falsifiers F4 (non-informative) and F5 (catastrophic) guard the two degenerate regimes. **No blocking objection.
Proceed with PLACEBO mandatory and the decision rule comparative.**

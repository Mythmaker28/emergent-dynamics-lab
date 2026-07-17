# ACCESS-STRUCTURE-00 — proposed preregistration after Phase 0.5

**DRAFT v0.5 — REVISE — NOT SEALED — NOT AUTHORIZED — DO NOT EXECUTE PROSPECTIVELY**

This is a design-review artifact. It incorporates the DEV-only operator qualification but does not authorize a
prospective family. Fields marked `BLOCKED` must be resolved and reviewed before any seal.

## Question and fixed prior

Given certified 03G Outcome B, determine whether the turnover-surviving causal feeding state is accessible from the
tracked target's local/core state, from its environment, redundantly from both, or only from their matched
combination. 03G and manuscript V5 are fixed prior evidence and will not be rerun, reinterpreted, or modified.

## Nomenclature

- `L`: exactly the frozen 03G 11-statistic decoder readout. It is never used as a complete state or intervention.
- `C`: complete manipulable local/core simulator state on a frozen spatial support.
- `B`: detected body/support/geometry and structural state; `B subset C` operationally.
- `H`: the declared near-interface causal collar, separate from far environment.
- `E`: remaining far environment.
- `NP`: nutrient and physical fields distributed across `C/H/E`, not a separate spatial compartment.
- `G`: dynamically shared/global channels, especially recomputed `up_ref`.
- `D`: complete Markov dynamical phase: persistent arrays, scheduler step, and common engine context. No persistent
  RNG, velocity/momentum, previous-state, flux/gradient buffer, or solver cache exists.

The historical decoder letters are written `N_03G/P_03G` when mentioned. No `L0E0/L1E0` shorthand is permitted.

## Unit, eligibility, and world validity

- Statistical unit: original world.
- Exactly three targets are selected by the frozen outcome-independent geometry rule before intervention.
- Target and crossed technical branches are averaged inside original world before inference.
- Donors `A/B` are selected without future feeding from a frozen written-history contrast rule. The Phase 0.5
  candidate maximizes normalized Euclidean contrast in `(dose,order)` and names the higher lexicographic member A.
- Every opened world, including ineligible and invalid worlds, appears in raw output. Reserve activation may use
  eligibility variables only.
- Hard feasibility floor: at least 18 valid original worlds. This is a minimum, not a power justification.
- `BLOCKED`: prospective family size and reserve rule require a design-based power calculation after a corrected
  operator passes DEV.
- A world is invalid if any primary/control branch has fewer than three distinct targets, any
  `MERGE/SPLIT/LOST/AMBIGUOUS`, coverage `>=0.15`, non-finite state, invalid tracked/fixed-mask readout, failed
  balance, or failed surgery gate.

## Candidate spatial partition and state reference

Phase 0.5 used a periodic radius-10 `C`, one-cell four-neighbour `H`, and complementary `E`. This contained every
qualified DEV source body, but its hard boundary failed the seam gate. Therefore this support is **not frozen for
prospective use**.

The candidate standard reference `0` is an on-manifold world from the same seed, law, and absolute scheduler time
without the two phase drives. Its candidate `C_0/B_0` is the median-area detected component with deterministic
geometric ties. It is never a literal blank grid or zero field.

`BLOCKED`: freeze one boundary-aware `C/H/E` support and construction that preserves complete donor `C/B`, keeps
far `E` fixed, exposes rather than erases `H`, passes balance, and does not use future feeding.

## Exact branch sources

The minimal primary cells, once an operator passes, are:

| Branch | `C/B` source | `H` source | far `E` source | Purpose |
|---|---|---|---|---|
| `C_0 H_0 E_0` | on-manifold standard | standard | standard | common reference; not an absence claim |
| `C_A H_0 E_0` | exact A | standard | standard | local/core causal sufficiency / environment reset |
| `C_0 H_A E_A` | standard | A | A | environmental sufficiency with standardized core/body |
| `C_A H_A E_A` | A | A | A | matched joint access |
| `C_A H_B E_B` | exact A | B | B | crossed access; B differs from A by frozen history rule |
| `C_B H_A E_A` | exact B | A | A | reciprocal crossed branch and conservation partner |

To protect the near-interface alternative, add exactly two disambiguation cells rather than a radial scan:

| Branch | Purpose |
|---|---|
| `C_0 H_A E_0` | halo-only sufficiency under standard core and far environment |
| `C_A H_A E_0` | core+matched-halo sufficiency with far environment standardized |

Every branch record must state the source of recipient location, `C`, `B`, `H`, `E`, every `NP` array inside and
outside the support, `G`, `D`, scheduler step, RNG status, coordinate transform, collar construction, balance
correction, and any recomputation. The current integer-roll/no-blend operator is recorded but rejected.

## Intervention implementation and controls

The Phase 0.5 exact reciprocal exchange established that source cores can be preserved without interpolation or
scaling and totals can be conserved across branch pairs. It failed branch-level balance and interface gates.

The corrected operator must have one unique implementation used by:

1. no-op continuation;
2. physics serialization/reconstruction;
3. same-source reinsert sham;
4. coordinate-transform roundtrip sham;
5. matched `C+H+E` reconstruction;
6. crossed `A/B` exchange;
7. `C_A H_0 E_0` environment standardization/reset;
8. `C_0 H_A E_A` body/core standardization with environment preserved;
9. the two halo-disambiguation arms;
10. dynamic global `up_ref=0` repetition;
11. `lam_plus=0, lam_minus=0.15` readout ablation.

The readout ablation removes only memory's positive modulation of feeding. It may never zero, bypass, or replace
the primary uptake endpoint.

## Common probe

Primary endpoint: integrated future feeding on the bijectively tracked target under identical external forcing.
Fixed initial-mask feeding is a convergent tracker-independent control.

The existing `0.25 x 5`, horizon-40 uniform additive probe is a candidate only. The 03G `N:=N0` reset plus 40-step
standardization cannot be reused automatically because it would overwrite part of the environment under test.

`BLOCKED`: qualify and freeze one common probe, surgery-to-probe interval, and horizon after the corrected operator
passes. The probe may add the same forcing to all branches but may not reset or homogenize `H/E`.

## Pre-outcome kill-switches

All gates run before any active-arm future feeding is exposed.

1. **Exact path:** no-op, serialization, same-source, coordinate-transform, and matched shams meet
   `abs(error) <= 1e-12 + 1e-10*abs(reference)` immediately and after continuation.
2. **Support/body:** complete `B` lies inside `C`; declared supports do not overlap; exact transfers have immediate
   body overlap and IoU of 1.
3. **Partition:** only declared `C` and separately declared `H` change at surgery; forbidden far-`E`, scheduler,
   engine, and observer fields do not.
4. **Boundary:** every causal-field mean seam ratio is at most the unsealed DEV candidate `1.25x` recipient natural
   boundary, plus a separately frozen absolute one-step `H` disturbance bound. Thresholds cannot be relaxed later.
5. **Balance:** arm-level target mass/body state and declared local/global `rho,U,V,N,c` totals meet the frozen
   float64 criterion. Reciprocal-pair conservation alone does not pass.
6. **Cohorts/material:** base-cohort `sum(C)=rho`, tracer no-feedback, and donor material accounting pass.
7. **Sham:** active-operation sham matches every copy, transform, boundary, balance, and numerical call. Its feeding
   bias lies inside a frozen equivalence margin.
8. **Tracker/geometry:** all primary and control branches have three distinct bijective tracks, no censor event,
   coverage `<0.15`, valid fixed-mask convergence, finite arrays, and 40-step viability.
9. **Global channel:** identifying cells repeat with dynamic `up_ref=0`; initial arrays and all local equations stay
   unchanged.
10. **D/RNG:** same engine and scheduler step; no hidden persistent buffer or RNG; no phase scramble.
11. **Outcome independence:** no feature, decoder, PID estimator, hyperparameter, eligibility rule, pair rule,
   boundary map, or correction is selected using confirmation outcomes.
12. **Feasibility fail:** any failure yields `FEASIBILITY_FAIL/UNRESOLVED`; no source or absence claim is allowed.

## Primary contrasts and claim logic

Let world-level means define:

- local/core sufficiency: `Y(C_A H_0 E_0) - Y(C_0 H_0 E_0)`;
- environmental sufficiency: `Y(C_0 H_A E_A) - Y(C_0 H_0 E_0)`;
- joint access: `Y(C_A H_A E_A) - Y(C_0 H_0 E_0)`;
- interaction: joint minus local minus environment plus reference;
- matching: matched joint minus mean reciprocal crossed branches;
- halo-only and core+halo contrasts from the two named halo cells.

`BLOCKED`: freeze practical sufficiency margin, equivalence margin, simultaneous interval/multiplicity method, and
power from design/manipulation noise only.

- **LOCAL OWNERSHIP supported** only if local/core sufficiency exceeds its margin and prospectively exceeds
  environmental, body, halo, sham, crossed, and global controls.
- **ENVIRONMENTAL ACCESS supported** only if environment remains sufficient with the same standardized `C_0/B_0`.
- **REDUNDANT supported** only if local/core and environment are independently sufficient.
- **SYNERGISTIC supported** only if joint and interaction exceed margins while both separate upper equivalence
  bounds lie below their margins; matched must exceed crossed without a surgery-artifact failure.
- **UNRESOLVED** covers wide uncertainty, failed equivalence, halo/phase ambiguity, and all failed controls.

“Not established” never means “absent.” No result establishes identity, individual memory, metaphysical ownership,
life, or active reconstruction.

## Secondary analyses

- Predeclare conditional decoding from frozen `L`, complete named `C/H/E` representations, matched/crossed inputs,
  and body/geometry/neighbour/global baselines.
- Scaling, tuning, and fitting occur inside held-out original-world folds.
- Predeclare one named, assumption-explicit continuous PID estimator for unique-local, unique-environment,
  redundancy, and synergy.
- Decoding and PID are secondary and cannot rescue a failed causal or feasibility gate.

## Phase 0.5 evidence and current recommendation

On the four already-open deep-feasible DEV worlds, exact shams and serialization had zero error, every active arm
was 4/4 viable for 40 steps, and immediate changes stayed inside the declared core. However, maximum seam ratio was
22.87, the one-cell halo reacted immediately, and individual-arm totals were unmatched despite paired
conservation. Active crossed feeding was not evaluated.

Current recommendation: **REVISE**. Human review is required. No prospective family, seal, push, merge, V5 change,
or active reconstruction is authorized by this draft.

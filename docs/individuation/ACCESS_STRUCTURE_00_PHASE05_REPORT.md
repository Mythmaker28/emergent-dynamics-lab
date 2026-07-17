# ACCESS-STRUCTURE-00 — Phase 0.5 DEV-only operator qualification

**Status: PHASE 0.5 COMPLETE — REVISE — NOT PROSPECTIVE-READY — HUMAN REVIEW REQUIRED**

This report qualifies intervention mechanics only. It does not answer where the turnover-surviving causal state
resides. No active crossed-arm future-feeding result was generated, no prospective seed or family was opened, and
03G raw data/results and manuscript V5 remain fixed prior evidence.

## 1. Independent scientific judgment

The simulator state can be reconstructed, serialized, translated, and reciprocally exchanged exactly. A paired
exchange is materially better than a one-way scaled graft: it preserves each donor core without interpolation or
rescaling and conserves every state-array total across the reciprocal branch pair. The exact no-op, serialization,
same-source, coordinate-transform, and matched-state shams all have zero numerical error and zero future-feeding
bias on the four already-open deep-feasible DEV worlds.

That is not enough for a prospective causal access experiment. The current exact exchange puts dynamically
incompatible fields next to one another. Mean boundary jumps reach 22.87 times the recipient's natural boundary
jump, the one-cell halo responds strongly after one update, and the disturbance reaches far environment by step
40. Individual branches also do not satisfy the requested mass/physical-field-total matching; conservation holds
only across the reciprocal pair. These are precisely the artefacts that could make a genuinely synergistic matched
state and a numerically shocked crossed state look different.

Therefore the exact exchange operator is **mechanically executable but causally uninterpretable in its current
form**. The recommendation is **REVISE**, not GO. STOP is premature because all active arms remain viable and
trackable for 40 steps, so a bounded interface/balance correction remains technically plausible.

## 2. Nomenclature and complete state map

### 2.1 Required meanings

- `L` remains exactly the frozen 03G 11-statistic decoder readout of target-support `m1,m2`. It is a lossy
  observation and is never treated as a manipulable state compartment.
- `C` is the complete manipulable local/core simulator microstate on a frozen spatial support.
- `B` is body/support/geometry. Operationally, `B` is the detected connected component and its structural
  `rho,U,V`; `B` is a subset of `C`, not independent of it.
- `H` is the one-cell four-neighbour stencil collar immediately outside `C`.
- `E` is the remaining grid after removing `C` and `H`.
- `NP` denotes the cross-cutting nutrient and physical fields. These arrays exist across `C/H/E`; `NP` is not a
  disjoint spatial compartment.
- `G` denotes world-global or shared dynamical channels, principally the recomputed `up_ref`, plus common engine
  parameters.
- `D` denotes dynamical phase/state required for exact continuation. It overlaps the state arrays, `G`, and the
  scheduler step; it is not a separate independent cause.
- The historical 03G decoder scopes named `N` and `P` are written below as `N_03G` and `P_03G` to avoid confusing
  them with nutrient `N` or physical-state notation.

### 2.2 Persistent simulation variables

| Variable | Exact support/type | Causal for future physics? | Membership/overlap | Treatment under exchange |
|---|---|---|---|---|
| `rho[64,64]` | persistent extensive scaffold density | yes: flux, growth, death, detection/body | `NP`; defines `B`; partitioned over `C/H/E`; part of `D` | exact donor values inside `C`; recipient outside |
| `U[64,64]` | persistent extensive internal toggle amount | yes: determines `u`, `sigma`, growth response | `B`/`NP` inside body; partitioned over `C/H/E`; part of `D` | exact donor inside `C` |
| `V[64,64]` | persistent extensive internal toggle amount | yes: determines `v`, `sigma`, growth response | same overlaps as `U` | exact donor inside `C` |
| `c[64,64]` | persistent physical attractant field | yes: drives scaffold flux, memory writing, and future `c` | `NP` across `C/H/E`; part of `D` | exact donor inside `C`, recipient outside; no recompute |
| `N[64,64]` | persistent nutrient field | yes: growth/feeding, memory writing, replenishment | `NP` across `C/H/E`; part of `D` | exact donor inside `C`, recipient outside; no recompute |
| `Mf[2,64,64]` | persistent extensive two-channel memory | yes: `m_plus` modulates feeding; `m_minus` modulates `c`; is rewritten/transported | local causal state inside `C`, also present in `H/E`; part of `D` | exact donor inside `C` |
| `C[15,64,64]` at qualified deep snapshots | 12 frozen passive cohorts plus 3 appended snapshot-material tracers | no feedback to `rho,U,V,c,N,Mf,uptake`; causal only to its own diagnostic continuation | diagnostic material accounting overlapping `B/C/H/E`; part of exact `D` | exact donor inside `C`; base-cohort invariant audited |
| `uptake[64,64]` | stored previous-step readout | no: the next `step()` never reads the incoming value and overwrites it | observer/readout state across `C/H/E`; included for bit-exact reconstruction | exact donor inside `C`; never “ablated” as the endpoint |
| `step` | integer scheduler phase | affects which diagnostic feed cohort receives new material; no physical feedback from cohort identity | `D`; overlaps tracer schedule | recipient and donor steps must be identical; preserved |

The deep qualification serializer persists every array above and `step`. Exact continuation additionally requires
the frozen engine law and parameters from the repository; these are validated external context rather than
duplicated in the state payload.

### 2.3 Engine context, derived values, observers, and hidden-state audit

| Item | Status | Causal/observational role | Operator rule |
|---|---|---|---|
| `ScaffoldSpec` | immutable engine context | causal law/parameters | common to every branch; never transplanted |
| `MCParams` | immutable engine context | causal memory write/read parameters | intact except named `up_ref` or readout ablation branches |
| tracer specification | immutable context | changes diagnostic `C` cohort index only | common; `step` preserved |
| `u=U/rho`, `v=V/rho`, `sigma` | derived each update/read | causal intermediates, not stored separately | derive from exchanged extensive arrays |
| `m=Mf/rho`, `m_plus`, `m_minus` | derived each update/read | causal intermediates | derive; never separately copied or zeroed in the exchange |
| face fluxes, Laplacians, `_tmean`, growth `g`, `Psi`, `qq`, alive mask | temporary arrays inside `step()` | causal intermediates | recomputed; no persistent cache exists |
| `up_ref=mean(current uptake over alive cells)` | derived inside each update | world-global causal write channel `G` | not stored/transplanted; named ablation sets it to zero dynamically |
| detector entities/features | derived observer state | geometry/readout only | recomputed after surgery |
| bijective tracker masks/status/born/died/assignment history/next ID | external observer state | no physics feedback | not transplanted; re-seeded from post-surgery geometry for qualification |
| material-tracer `base` index | external diagnostic metadata | material readout only | fixed from original cohort count; no physics feedback |
| RNG | used in initial world/history construction only | no RNG call or persistent RNG state after snapshot | absent from continuation and every intervention |
| velocity/momentum, prior-state, flux/gradient buffers, solver cache | none | no hidden phase variable exists | nothing to transplant or scramble |

Thus the physics state is Markov at the array snapshot plus `step` under a compatible frozen engine. `D` has been
made explicit; there is no justification for a phase-scramble experiment.

## 3. Operational spatial partition

For Phase 0.5 only:

- the target component centroid is rounded to the nearest periodic grid cell;
- `C` is the periodic disk of radius 10 cells;
- `H` is the next one-cell ring, matching the engine's direct four-neighbour stencil;
- `E` is the complement;
- diagnostic distance bands are `C`, `H_d1`, `E_d2_3`, `E_d4_6`, and `E_far`.

This choice was based only on already-open DEV geometry. All 12 qualified source bodies fit in radius 10; the worst
observed body support radius was 8.93 cells. Radius-11 blocks remained separated because the minimum target-centre
distance was 25.04 cells. `C` is therefore deliberately broader than droplet material and contains local physical
field around `B`. Any eventual positive result with this definition could establish **local/core access**, not
material ownership or droplet-only storage.

## 4. Exact operator definitions

| Operator | Exact implementation | Purpose and qualification status |
|---|---|---|
| no-op continuation | deep state `.copy()`, same engine and step | exact at surgery and after 10 steps, 4/4 |
| physics serialization/reconstruction | serialize all eight arrays plus `step`; reconstruct compatible `IOMState` | bit-exact at surgery and after 10 steps, 4/4 |
| same-source reinsert sham | extract and assign the same `C` cells without transform | bit-exact, 4/4 |
| coordinate-transform sham | integer toroidal roll `(7,-9)`, exact inverse, then reinsert same source | bit-exact and zero feeding bias, 4/4 |
| matched `C+H+E` | unmanipulated state plus same-site reciprocal exchange-kernel sham | bit-exact, 4/4 |
| crossed `A/B` | two branch clones exchange complete `C_A` and `C_B` reciprocally; output branches are `C_B H_A E_A` and `C_A H_B E_B` | source cores exact; pair-conserved; seams fail |
| environment standardization/reset | reciprocal exchange between a history world and an on-manifold no-history world; output `C_A H_0 E_0` | no literal blank/zero; viable; seams and branch balance fail |
| body/core standardization with environment preserved | reciprocal output `C_0 H_A E_A` from the same operation | same unique operator, not a redundant arm; viable; seams and balance fail |
| global `up_ref` ablation | future engine update computes `up_ref:=0`; all local equations and initial arrays retained | 4/4 viable; endpoint retained |
| readout ablation | `lam_plus=0`, frozen `lam_minus=0.15`; future feeding equation remains active | 4/4 viable; uptake endpoint present every step |

The on-manifold reference `0` is the same seed, law, and absolute scheduler time evolved without the two phase
drives. Its standard body is the median-area detected component with deterministic geometric ties. It is not an
empty grid, a zero-memory field, or a claim that the causal state is absent.

Every active exchange uses an integer periodic translation. There is no interpolation, rotation, scale change,
zero fill, collar blend, relaxation, or surgery-time recomputation. `H/E` remain the recipient's values at the
instant of surgery. That exactness is what reveals the unresolved boundary mismatch.

## 5. Donor-labelled arm table

`A/B` are selected without future feeding: among the three frozen targets, choose the pair with maximum normalized
Euclidean contrast in the already-written `(dose, order)` coordinates; name the higher lexicographic
`(dose,order)` member `A`. This rule is a DEV operator qualification rule, not a sealed prospective rule.

| Arm | `C` and `B` source | `H` source | far `E` source | `NP` source | `G` | `D`, RNG, transform/collar/recompute |
|---|---|---|---|---|---|---|
| `C_A H_A E_A` | history target A | A recipient | A recipient | A inside `C`; A outside | intact dynamic | original step; no RNG; no transform |
| `C_B H_B E_B` | history target B | B recipient | B recipient | B inside/outside | intact dynamic | same |
| `C_A H_B E_B` | exact translated A | B recipient | B recipient | A inside `C`; B outside | recomputed from crossed future | matched step; integer roll; no blend/recompute |
| `C_B H_A E_A` | exact translated B | A recipient | A recipient | B inside `C`; A outside | recomputed | same |
| `C_0 H_0 E_0` | no-history reference | no-history | no-history | no-history throughout | intact dynamic | same absolute step; no RNG after construction |
| `C_A H_0 E_0` | exact translated A | no-history recipient | no-history recipient | A inside `C`; reference outside | recomputed | reciprocal cross-world exchange |
| `C_0 H_A E_A` | exact translated reference | A recipient | A recipient | reference inside `C`; A outside | recomputed | reciprocal arm of preceding exchange |
| `C_B H_0 E_0` | exact translated B | no-history recipient | no-history recipient | B inside `C`; reference outside | recomputed | reciprocal cross-world exchange |
| `C_0 H_B E_B` | exact translated reference | B recipient | B recipient | reference inside `C`; B outside | recomputed | reciprocal arm of preceding exchange |

The reciprocal implementation conserves totals across each two-branch pair. It does **not** make individual branch
totals equal; that distinction is central to the REVISE decision.

## 6. DEV-only results

Machine-readable results are in `ACCESS_STRUCTURE_00_PHASE05_DEV_QUALIFICATION.json`.

### 6.1 World dispositions

- Deep-feasible and actively qualified: 50002, 50004, 50005, 50007.
- Existing no-operator dispositions: 50001 split at 153; 50003 lost at 236; 50006 split at 692; 50009 split
  at 436; 50008 and 50010 ineligible.
- No seed outside 50001–50010 was accepted or executed.

### 6.2 Passed mechanical checks

| Check | DEV result |
|---|---:|
| no-op immediate maximum error | `0.0` |
| serialization immediate maximum error | `0.0` |
| serialization versus no-op after 10 steps | `0.0` |
| same-source reinsert error | `0.0` |
| coordinate-transform sham error | `0.0` |
| matched exchange-kernel sham error | `0.0` |
| coordinate-sham versus no-op future-feeding bias | `0.0` tracked and fixed-mask |
| immediate unintended `H/E` change | `0.0` |
| source and standard body contained by `C` | 16/16 relevant source checks |
| immediate expected-body overlap/IoU after active surgery | minimum `1.0 / 1.0` |
| base cohort `sum(C)-rho` maximum error | `2.56e-15` |
| paired exchange conservation maximum error | `9.10e-13`, inside frozen float64 criterion |
| active arm 40-step tracker/viability | every one of six arms 4/4 |
| `up_ref=0` 40-step tracker/endpoint | 4/4 valid, uptake present |
| `lam_plus=0` 40-step tracker/endpoint | 4/4 valid, uptake present |

No active crossed or standardized arm was sent through the future-feeding probe. The only probe comparison was
between bit-identical no-op and transform-sham states, so these results contain no evidence for `H_L/H_E/H_R/H_S`.

### 6.3 Failed interpretation checks

**Boundary/off-manifold failure.** Across 168 field × arm × world seam ratios, only 4 are at or below the candidate
`1.25x` natural-boundary envelope; 9 are at or below `1.5x`, 18 at or below `2x`, 53 at or below `3x`, and 114 at
or below `5x`. The maximum is `22.872x` for `rho` in seed 50002 `C_B H_A E_A`. Other examples include `13.024x`
for `v`, `9.861x` for `u`, and `7.500x` for nutrient `N`. Inflating the threshold to cover these observations
would calibrate acceptance to the failed operator itself and is rejected.

**Halo and phase propagation.** Maximum band RMS differences versus recipient no-op continuation were:

| Step | `H_d1` | `E_d2_3` | `E_d4_6` | `E_far` |
|---:|---:|---:|---:|---:|
| 1 | 0.809 | 3.61e-4 | 3.27e-8 | 2.78e-8 |
| 5 | 0.871 | 0.274 | 2.29e-4 | 1.34e-7 |
| 20 | 0.919 | 0.456 | 0.102 | 2.11e-5 |
| 40 | 0.985 | 0.615 | 0.126 | 0.0287 |

The exact values combine fields on different physical scales and are not a scalar acceptance score. Their role is
localization: the disturbance begins at the interface and propagates outward. This directly protects `H_HALO` and
`H_PHASE`; it forbids interpreting 40-step viability as evidence that the surgery is innocuous.

**Individual-branch balance failure.** Although reciprocal-pair totals are conserved, maximum absolute changes in
one branch versus its recipient include `84.58` for `c`, `58.14` for `U`, and `40.72` for `rho`. Those changes are
the exact donor-core replacement, not numerical leakage, but the requested arm-level mass/body/physical-field
matching is therefore not satisfied. A future global-channel effect could follow these total changes rather than
storage access.

These failures precede any feeding outcome and trigger FEASIBILITY_FAIL under the proposed claim logic.

## 7. Competing hypotheses and signatures after a valid operator exists

Let `Y(C,H,E)` be future target feeding under one common probe. A positive contrast requires a frozen practical
margin; a “failure” requires a frozen equivalence upper bound, not a non-significant result.

| Hypothesis | Required causal signature | What would falsify or leave it unresolved? |
|---|---|---|
| `H_L` uniquely local/core access | `C_A H_0 E_0 > C_0 H_0 E_0`; exceeds environmental, body, sham, crossed, halo and global controls | environment-only sufficiency, failed balance/seam controls, or wide interval |
| `H_E` environmental access | `C_0 H_A E_A > C_0 H_0 E_0` with the same standardized `C_0/B_0` | local/body difference, environment-total confound, or wide interval |
| `H_R` redundant access | both local-only and environment-only contrasts independently exceed their margins | either separate contrast fails equivalence-aware sufficiency |
| `H_S` synergistic/relational access | matched joint and interaction exceed margins while both separate upper bounds are below equivalence margins; matched beats crossed | crossed numerical shock, halo mismatch, or merely non-significant separate arms |
| `H_0` residual readout/body/global confounding | active effects collapse/follow `lam_plus`, body, total-state, seam, sham, tracker, or `up_ref` controls | clean causal sufficiency surviving all named controls would disfavor, not logically eliminate, this layer |

`H_0` is not mutually exclusive with local causal access. A short-lived directly coupled remnant could be locally
sufficient without establishing ownership, identity, individual memory, or active reconstruction.

## 8. Proposed kill-switches before any prospective data

These are unsealed proposal fields. The current operator fails items 4 and 6.

1. **Namespace/eligibility:** outcome-independent eligibility only; every opened original world appears in raw;
   no reserve activation based on feeding; minimum 18 valid original worlds plus a design-based power calculation.
2. **Exact reconstruction:** no-op, serialized, same-source, coordinate-transform, and matched shams must equal the
   reference path at `abs(error) <= 1e-12 + 1e-10*abs(reference)`.
3. **Support/body:** complete detected `B` plus declared causal interior must lie inside `C`; supports/collars cannot
   overlap; expected-body immediate overlap and IoU must be 1 for an exact source transfer.
4. **Boundary/H:** every causal-field post/pre natural seam ratio must be at most the unsealed candidate `1.25`, and
   the one-step `H` disturbance must be sham-equivalent under a separately frozen absolute metric. No threshold may
   be relaxed after feeding is observed.
5. **Partition fidelity:** only declared `C` and, if explicitly designed, `H` may change at surgery. Far `E`, step,
   engine parameters, tracker-independent geometry, and diagnostic invariants must pass.
6. **Balance:** the branch contract must hold arm-level target mass/body state and declared global/local
   `rho,U,V,N,c` totals at the frozen float64 criterion. Pairwise conservation alone is insufficient.
7. **Viability/tracker:** all primary/control branches require three distinct tracks, no
   `MERGE/SPLIT/LOST/AMBIGUOUS`, coverage `<0.15`, finite arrays, valid tracked and fixed-mask readouts, and the full
   40-step qualification horizon. One target failure invalidates the original world.
8. **Sham:** active-operation sham must match copy count, transform, collar handling, any balance projection, and
   numerical calls. Sham feeding bias must be inside a frozen equivalence margin.
9. **Global/readout:** repeat identifying cells under dynamic `up_ref=0`; `lam_plus=0,lam_minus=0.15` removes only
   memory's positive feeding modulation and never disables the uptake endpoint.
10. **D/RNG:** identical scheduler step and engine context; no hidden buffers or RNG; observer tracker re-seeding
    fixed from geometry. No phase scramble.
11. **Probe:** identical external forcing and horizon in every branch; it must not reset or homogenize the
    environment whose sufficiency is tested. Probe schedule remains unsealed until the revised surgery passes.
12. **Analysis:** original world is the statistical unit; technical targets/crosses are averaged within world;
    scaling/model fitting occur inside held-out original-world folds; no feature, decoder, PID estimator, eligibility
    rule, or operator is selected using confirmation outcomes.
13. **Feasibility fail:** failure of any operator/control gate yields `FEASIBILITY_FAIL/UNRESOLVED`, never a storage
    or absence claim.

## 9. Exact bounded revision required

One further DEV-only engineering revision would need to do all of the following before a preregistration can be
reviewed for GO:

1. replace the hard donor/recipient interface with one predeclared, equation-aware boundary construction that
   preserves donor `B/C`, treats `H` as an explicit possible causal compartment, and holds far `E` fixed;
2. add the minimum halo-disambiguation arms (`C_0 H_A E_0` and `C_A H_A E_0`) rather than hiding `H` inside a blend;
3. enforce arm-level mass and declared physical-field totals without a history- or feeding-dependent correction;
4. qualify the correction against matched active-operation shams, the `1.25x` seam candidate, concentric transient
   bands, geometry, tracker, viability, `G`, and complete `D`;
5. either pass unchanged on already-open DEV only or conclude STOP if interface state and far environment cannot be
   separated without destroying the state under test.

This is a bounded correction, not authorization to scan radii, scramble phase, inspect prospective seeds, or create
a new physical substrate.

## 10. Recommendation and human gate

**REVISE.** Exact state exchange is feasible, but the current operator fails the boundary/off-manifold and
individual-arm balance gates. No preregistration should be sealed and no prospective seed should be opened.

Exact next authorized action: human review of this Phase 0.5 report. A further DEV-only correction requires new
explicit approval. Without it, stop here.

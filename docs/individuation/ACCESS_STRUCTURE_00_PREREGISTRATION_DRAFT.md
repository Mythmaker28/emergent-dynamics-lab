# ACCESS-STRUCTURE-00 — proposed preregistration skeleton

**DRAFT — REVISE — NOT SEALED — NOT AUTHORIZED — DO NOT EXECUTE PROSPECTIVELY**

This is a design-review artifact, not an executable preregistration. Fields marked `MUST FREEZE` block any seal.

## Question and fixed prior

Given certified 03G Outcome B, determine whether the turnover-surviving causal feeding state is accessible from the
tracked target's local state, from its environment, redundantly from both, or only from their matched combination.
03G and manuscript V5 are fixed prior evidence and will not be rerun or reinterpreted.

## Unit and eligibility

- Statistical unit: original world.
- Exactly three targets are selected by the frozen outcome-independent 03G geometry rule before any intervention.
- All target, donor, and crossed technical replicates are averaged inside original world.
- A world is valid only if every primary and control branch has three distinct targets, no
  `MERGE/SPLIT/LOST/AMBIGUOUS` event, coverage below 0.15, finite state, and a valid bijective readout.
- Hard feasibility floor: at least 18 valid original worlds. This is a minimum, not a power justification.
- `MUST FREEZE`: prospective family size from a design-based power calculation after DEV manipulation qualification.
- All seeds, including invalid worlds, must appear in raw output. Reserve activation, if any, may read eligibility
  fields only.

## Frozen state partition

- `L`: target-support intensive memory `Mf/rho`.
- `B`: target support, `rho`, `U/rho`, and `V/rho`.
- `E`: `N,c` everywhere plus every physical state variable outside target support.
- `G`: dynamically recomputed global `up_ref`; not a stored state variable.
- `C`, material cohorts, target IDs, and tracker IDs: diagnostic only.

`MUST FREEZE`: exact target support, neutral body `B0`, neutral local state `L0`, standardized environment `E0`,
donor-to-recipient transform, seam/boundary rule, and energy matching. They must be selected from pre-outcome
manipulation validity only.

## Primary branches

For each eligible target, create from one canonical deep snapshot:

| Code | Local state | Body | Environment | Purpose |
|---|---|---|---|---|
| `L0E0` | neutral | standardized/fixed | standardized | double-null reference |
| `L1E0` | own target | same as `L0E0` | standardized | local causal sufficiency / environment reset |
| `L0E1` | neutral | same as `L1E1` | original matched | environmental sufficiency / local erase |
| `L1E1` | own target | same counterfactual body | original matched | joint matched access |
| `LAEB` | donor A | recipient-standardized | environment B | crossed access; all frozen eligible A!=B pairs |

Repeat the identifying cells with `up_ref=0`. Run `lam_plus=0, lam_minus=0.15` readout-ablation controls, body-only
controls, exact identity shams, active-operation shams, and fixed-mask readouts.

The common probe is the same additive forcing and horizon in every branch. It may not reset away the environment
whose sufficiency is being tested. `MUST FREEZE`: amplitude, duration, settle rule, horizon, and whether the existing
03G `0.25 x 5`, horizon 40 schedule remains geometry-valid after manipulation.

## Manipulation acceptance gates

Before looking at future feeding:

1. **MASS:** target mass and global conserved quantities match the declared branch contract within
   `abs(error) <= 1e-12 + 1e-10*abs(reference)`.
2. **BODY/GEOMETRY:** target `rho`, mask, centroid, radius/shape metrics, and `U,V` are identical wherever the design
   says body is held fixed; otherwise the branch is invalid.
3. **ENERGY/NUTRIENT:** declared global and local `N,c` totals match; the correction map is outcome-independent.
4. **COHORT:** `sum(C)=rho` and diagnostic-cohort zero-feedback hold exactly to the frozen numerical criterion.
5. **SHAM:** identity graft and active-operation sham remain inside a predeclared disturbance envelope.
6. **TRACKER:** all primary branches pass bijective and fixed-mask geometry checks; one target failure invalidates the
   world.
7. **NO-OP:** every active intervention changes exactly its intended state partition and no forbidden partition.
8. **REFERENCE:** an unmanipulated branch reproduces the scalar/reference path under the frozen float64 criterion.

`MUST FREEZE`: disturbance metrics, sham/equivalence envelope, and all branch-specific no-op assertions.

## Primary endpoint and contrasts

Endpoint: integrated feeding on the bijectively tracked target under the common probe. Fixed-mask integrated feeding
is a convergent control. Let world-level branch means define:

- `tau_L = Y(L1E0)-Y(L0E0)`;
- `tau_E = Y(L0E1)-Y(L0E0)`;
- `tau_LE = Y(L1E1)-Y(L0E0)`;
- `tau_S = Y(L1E1)-Y(L1E0)-Y(L0E1)+Y(L0E0)`;
- `tau_match = Y(L1E1)-mean(Y(LAEB))`.

`MUST FREEZE`: practical sufficiency margin `delta`, equivalence margin `epsilon`, simultaneous interval or
multiplicity method, and power. They must come from manipulation noise/design requirements, not future confirmation
outcomes.

## Decision tree

Evaluate feasibility and control gates first. If any fails: **FEASIBILITY_FAIL** or **UNRESOLVED**, with no source
claim.

- **LOCAL:** `tau_L` exceeds `delta`, exceeds E/body/sham/cross controls, and the E-only upper equivalence bound is
  below `epsilon`.
- **ENVIRONMENTAL:** `tau_E` exceeds `delta` with standardized local state/body, and the L-only upper equivalence
  bound is below `epsilon`.
- **REDUNDANT:** both `tau_L` and `tau_E` independently exceed `delta`.
- **SYNERGISTIC:** `tau_LE` and `tau_S` exceed their margins while both separate upper equivalence bounds are below
  `epsilon`; positive `tau_match` further supports relational matching.
- **UNRESOLVED:** every other pattern, including wide uncertainty or merely non-significant separate effects.

The words “absent,” “individual memory,” “identity,” “ownership” beyond this operational access test, and “active
reconstruction” are forbidden unless a separate future protocol directly establishes them.

## Secondary analyses

- Fixed before prospective data: `L`, `E`, `L+E`, matched/crossed conditional decoders; body, geometry, nearest-
  neighbour, and global-channel baselines.
- Scaling, tuning, and model fitting occur inside held-out original-world folds.
- Report a named, assumption-explicit continuous PID estimator for unique-L, unique-E, redundancy, and synergy.
- PID and decoding are secondary; no secondary analysis can rescue a failed causal gate.
- No feature, decoder, hyperparameter, eligibility rule, or branch map may be selected from confirmation outcomes.

## Execution discipline

One design review, one finalized preregistration, one explicitly authorized prospective run, and one independent
raw reproduction. Record code hashes, environment lock, manifests, exact commands, every branch state audit, and
all raw original worlds. Do not push, merge, submit, modify V5, or start active reconstruction under this draft.

## Human gate

Current recommendation: **REVISE**. Human review may authorize a DEV-only manipulation qualification, not a
prospective family. Prospective authorization requires a later complete preregistration with every `MUST FREEZE`
field resolved.

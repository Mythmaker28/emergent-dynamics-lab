# COUNTERFACTUAL-HISTORY-MECHANISM-RECONCILIATION-00 analysis plan

Status: **FROZEN BEFORE LOWO FITTING AND SAME-MANIFEST DIAGNOSTIC REPLAY**  
Date: 2026-07-17  
Parent result: `COUNTERFACTUAL-HISTORY-CORE-00` at `ea6e6a0ab2ccc3e94eba364ddb459088c96d6033`  
Scope: the already-open DEV family 57001--57024 only; no new seed, history, world, or prospective claim.

## Units and eligibility

The original source world is the only statistical unit. The analysis uses the 17 worlds whose four frozen potential-outcome branches formed complete blocks in the parent result. Branches are paired potential outcomes, not replicates. No incomplete-world outcome is imputed.

## Fixed algebra and descriptive quantities

All factorial contrasts retain the parent convention:

- dose = `0.5 * ((HE + HL) - (LE + LL))`;
- order = `0.5 * ((LE - LL) + (HE - HL))`;
- interaction = `(HE - HL) - (LE - LL)`.

The sign derivation uses the exact engine recurrence and a homogeneous scalar reduction with the frozen `dt`, write/decay rates, two 60-step episodes, and 120-step post-history settle. The scalar check is theory-only and cannot execute a world or read a feeding outcome.

Predefined physical variables for descriptive contrasts are: `body_mass`, `body_size`, `body_rg`, `core_rho_mass`, `nearest_neighbor_distance`, `core_N_mean`, `core_c_mean`, `core_u_mean`, `core_v_mean`, `core_sigma_mean`, `world_up_ref`, `world_N_mean`, `world_c_mean`, and `world_rho_mass`. Frozen feeding outcomes are reported for tracked and fixed masks, integrated and instantaneous at step 40.

Two exploratory normalizations are fixed here before their values are computed:

1. tracked integrated uptake divided within each history branch by that branch's pre-probe `body_mass`;
2. fixed-mask integrated uptake divided within each history branch by that branch's pre-probe detected `body_size` (a body-cell area proxy, not the unrecorded fixed-mask area).

Their world-level dose contrasts are descriptive secondary endpoints and never replace the frozen integrated-uptake endpoint.

## Fixed LOWO prediction family

For each of the coupled and isolated tracked-feeding dose contrasts, fit exactly these nested feature panels:

1. `mass_area`: `body_mass`, `body_size`;
2. `body_geometry`: `body_mass`, `body_size`, `body_rg`, `core_rho_mass`, `nearest_neighbor_distance`;
3. `body_geometry_memory`: the body/geometry panel plus `mplus_mean`, `mminus_mean`.

Every row is one original-world factorial dose contrast. Each leave-one-world-out fold standardizes predictors using the training worlds only. A fixed ridge regression with `alpha=1.0` and a training-fold intercept is used; there is no hyperparameter tuning, feature selection, or stepwise search. Constant training columns receive scale 1.

Report LOWO predictions, RMSE, MAE, PRESS-based Q2 relative to the global response mean, correlation when defined, and paired squared-error improvement over the training-mean predictor. Incremental targeted-memory value is the per-world squared error of `body_geometry` minus that of `body_geometry_memory`.

Targeted memory adds reproducible out-of-world information only if its mean squared-error improvement has a 95% Student-t interval wholly above zero in the isolated arm, has positive mean improvement in the coupled arm, and raises Q2 in both arms. Body/geometry explains the dose response only if Q2 is positive and the 95% interval for improvement over the training-mean predictor is wholly above zero in both arms.

## Same-manifest replay boundary

The frozen JSON does not contain target `m_minus` or target baseline uptake after the 40-step standardization settle or at the final step-40 probe endpoint. A deterministic replay is therefore technically required for those diagnostics. It is restricted to the same manifest, the same 17 complete 57001--57024 worlds, and the same code/parameters. Each replay must match the frozen final-state hashes and feeding values before its added diagnostics are accepted. It records:

- frozen deep/pre-probe target state;
- standardized pre-stimulus state after settle step 40;
- final state at the frozen horizon step 40;
- target `m1`, `m2`, `mplus`, `mminus`, mass, detected area, and instantaneous uptake.

These replays are diagnostic re-observations of authorized worlds, not new worlds or independent confirmation.

## Decision rule

Return `CAUSAL-LANDSCAPE-JUSTIFIED` only under the mission's stated conditions. Return `PHYSICAL-CARRYOVER-ONLY` only if the fixed body/geometry criterion passes in both primary arms, targeted memory fails its incremental criterion, the sign anomaly is a convention correction or negligible, and no named operator prediction remains. Otherwise return `UNRESOLVED`.


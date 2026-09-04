# PAPER SCOPE AND CLAIM MATRIX (LRCPS01 §3)

Strategy: `COMPANION_PAPER`  ·  claims: **20**  ·  
load-bearing: **15**  ·  self-test: **PASS**

No manuscript prose may be written except in service of a claim listed here, and no
claim may be stated above its wording ceiling.

## Claim matrix

| ID | Tier | Kind | Sections | Labels | Ceiling |
|---|---|---|---|---|---|
| A1 | `QUALIFIED` | LOAD_BEARING | abstract 3 4 S2 | 5 | 'predicted before the confirmation arms were run' — never 'predicts the system' in general. |
| A2 | `QUALIFIED` | LOAD_BEARING | abstract 4 Fig2 S4 S5 | 15 | 'agreed within the pre-declared margin' — never 'validated', never 'proved'. |
| A3 | `QUALIFIED` | LOAD_BEARING | abstract 4 6 Fig2 | 7 | 'unity is excluded from the interval' — never 'mobility is proved to matter'. |
| B0 | `QUALIFIED` | LOAD_BEARING | abstract 5 Fig3 S6 | 6 | 'over 116 historical mobile arms' must appear wherever this is stated; it is a retrospective check on the existing record, not part of the prospective confirmation. |
| B6 | `QUALIFIED` | LOAD_BEARING | 5 Fig3 S6 | 4 | This is a disclosure against our own interest and must not be omitted or softened. Never write that the profile agrees in both conditions. |
| B1 | `QUALIFIED` | LOAD_BEARING | 5 S6 | 6 | 'the historical residuals were negative' — a description of the record, not a physical claim. |
| B2 | `QUALIFIED` | LOAD_BEARING | abstract 5 Fig3 S6 | 13 | 'covers most of the static deficit' — never 'explains the residual', and never extend the sentence to the mobile condition. |
| B3 | `QUALIFIED` | LOAD_BEARING | abstract 5 6 Fig3 Fig4 S6 S7 | 6 | 'the surrogate does not account for the mobile deficit' — state the failure before the construction that repairs it. |
| B4 | `QUALIFIED` | LOAD_BEARING | 5 6 Fig3 S6 | 13 | 'orders the two accounts' — never 'the summary rule is refuted'. |
| B5 | `QUALIFIED` | LOAD_BEARING | abstract 5 Fig3 S6 | 10 | 'on the same frames' must appear — the two rules are applied to identical data. |
| B7 | `QUALIFIED` | LOAD_BEARING | 5 8 Fig3 S6 | 4 | Stated against our own interest. It must appear in the results, not only in the discussion. |
| C1 | `QUALIFIED` | LOAD_BEARING | 6 Fig4 S7 | 9 | 'this ingredient is necessary for the agreement' — never 'this is the mechanism'. |
| C2 | `QUALIFIED` | SUPPORTING | 6 S7 | 1 | 'over-dispersed relative to Poisson' — a measured moment ratio, nothing more. |
| C3 | `QUALIFIED` | SUPPORTING | 6 S7 | 1 | 'negligible in this regime' — never 'capacity never binds'. |
| D1 | `LOST_DOCUMENTARY` | NARRATIVE_ONLY | 7 | 0 | Named as project history with an explicit loss flag. No number, no figure, no table, no abstract sentence. |
| D2 | `NOT_TESTED` | NARRATIVE_ONLY | 7 8 | 0 | 'not tested' — never 'the region is empty', never 'the architecture cannot support it'. |
| A5 | `QUALIFIED` | LOAD_BEARING | 3 S1 | 4 | 'bit-identical over the checked run' — never 'the observer is provably inert in general'. |
| C4 | `QUALIFIED` | SUPPORTING | 6 S7 | 2 | 'errs by this much at this scale' — never 'continuum methods are invalid'. |
| C5 | `QUALIFIED` | LOAD_BEARING | 3 6 8 S2 | 6 | This is a limitation and must be stated in the discussion as an open problem. |
| C6 | `QUALIFIED` | LOAD_BEARING | abstract 4 8 | 6 | 'qualified' is the adjudicated word and is not to be upgraded to 'validated' or 'proved'. |

## Claims in full

### A1 — `QUALIFIED` — LOAD_BEARING

> A one-step conditional operator constructed from the frozen kinetics predicted, before any confirmation arm was run, the steady-state 0.8-quantile radial extent of the X field around a full-capacity source in both a static and a mobile condition.

- allowed sections: abstract, 3, 4, S2
- reconciliation labels: `r80_static_predicted_frozen`, `r80_mobile_predicted_frozen`, `prediction_status`, `fresh_static_predicted`, `fresh_mobile_predicted`
- wording ceiling: 'predicted before the confirmation arms were run' — never 'predicts the system' in general.
- why not stronger: The prediction is frozen for one source strength, one lattice, one parameter point. Generalisation beyond that point is not derived.

### A2 — `QUALIFIED` — LOAD_BEARING

> On 28 fresh arms (14 per condition, 0 extinctions, 0 invalid), the observed medians agreed with the frozen predictions to -0.14 % (static) and +0.24 % (mobile), both inside a pre-declared +/-2.9 % equivalence margin.

- allowed sections: abstract, 4, Fig2, S4, S5
- reconciliation labels: `fresh_arms_run`, `fresh_arms_analysable`, `fresh_arms_invalid`, `fresh_extinctions`, `fresh_static_observed`, `fresh_static_deviation_percent`, `fresh_static_ci95_low`, `fresh_static_ci95_high`, `fresh_static_pass`, `fresh_mobile_observed`, `fresh_mobile_deviation_percent`, `fresh_mobile_ci95_low`, `fresh_mobile_ci95_high`, `fresh_mobile_pass`, `equivalence_margin_percent`
- wording ceiling: 'agreed within the pre-declared margin' — never 'validated', never 'proved'.
- why not stronger: The independent unit is the arm (n=14 per condition). Equivalence inside a declared margin is not a proof of exactness; it bounds the discrepancy, it does not remove it.

### A3 — `QUALIFIED` — LOAD_BEARING

> The mobile/static extent ratio was 1.3464 observed against 1.3412 predicted (+0.39 %), and unity lies outside its confidence interval, so source mobility increases the steady-state extent by a margin the operator anticipated.

- allowed sections: abstract, 4, 6, Fig2
- reconciliation labels: `fresh_ratio_predicted`, `fresh_ratio_observed`, `fresh_ratio_deviation_percent`, `fresh_ratio_ci95_low`, `fresh_ratio_ci95_high`, `fresh_ratio_pass`, `ratio_one_excluded`
- wording ceiling: 'unity is excluded from the interval' — never 'mobility is proved to matter'.
- why not stronger: Two mobility settings only. The functional form of the dependence on hop rate is not measured; only the contrast between the two frozen settings is.

### B0 — `QUALIFIED` — LOAD_BEARING

> The field itself follows the frozen operator: over 116 historical mobile arms the observed and predicted cumulative radial profiles agree at every one of 15 radii, maximum |z| = 0.636 and maximum difference 0.0038 in cumulative probability. The deficit was therefore not in the field.

- allowed sections: abstract, 5, Fig3, S6
- reconciliation labels: `radial_profile_max_abs_z`, `radial_profile_radii_tested`, `radial_profile_max_abs_difference`, `profile_agrees_at_every_radius`, `radial_profile_mobile_arms`, `radial_profile_flag_scope`
- wording ceiling: 'over 116 historical mobile arms' must appear wherever this is stated; it is a retrospective check on the existing record, not part of the prospective confirmation.
- why not stronger: It is not a fresh-arm result and carries no pre-declared margin. It shows where the residual is not; it does not by itself establish where it is.

### B6 — `QUALIFIED` — LOAD_BEARING

> The same profile comparison in the static condition rests on three historical arms and is not informative: its largest standardised deviation is 8.90, at a radius where the absolute difference (0.031 in cumulative probability) is no larger than at radii whose |z| is below one, because a standard error estimated from three arms can collapse by chance. The source programme reports this cell as not evaluated.

- allowed sections: 5, Fig3, S6
- reconciliation labels: `radial_profile_static_max_abs_z`, `radial_profile_static_max_abs_difference`, `radial_profile_static_arms`, `radial_profile_flag_scope`
- wording ceiling: This is a disclosure against our own interest and must not be omitted or softened. Never write that the profile agrees in both conditions.
- why not stronger: Three arms cannot support a per-radius profile test. Reporting only the mobile figure without this line would misrepresent the scope of the flag.

### B1 — `QUALIFIED` — LOAD_BEARING

> Historical arm-median residuals against the same frozen construction were negative in both conditions: static median -1.83 % (n=3), mobile median -5.10 % (n=116).

- allowed sections: 5, S6
- reconciliation labels: `historical_static_median_residual_percent`, `historical_static_median_residual_n`, `historical_static_median_residual_z`, `historical_mobile_median_residual_percent`, `historical_mobile_median_residual_n`, `historical_mobile_median_residual_z`
- wording ceiling: 'the historical residuals were negative' — a description of the record, not a physical claim.
- why not stronger: The historical arms were not run under this mission's freeze discipline; they are described, not used as confirmatory replicates.

### B2 — `QUALIFIED` — LOAD_BEARING

> A surrogate containing no lattice dynamics at all -- independent draws from the predicted population law, summarised by the same frozen rule -- is already biased downwards by -1.21 % (static) and -1.31 % (mobile). Taking a median of a finite-sample first-crossing quantile is biased by construction, and that alone covers most of the observed static deficit of -1.83 %.

- allowed sections: abstract, 5, Fig3, S6
- reconciliation labels: `iid_static_population_r80`, `iid_static_median_summary`, `iid_static_median_ratio`, `iid_mobile_population_r80`, `iid_mobile_median_summary`, `iid_mobile_median_ratio`, `cell_static_median_observed_percent`, `cell_static_median_surrogate_percent`, `cell_mobile_median_surrogate_percent`, `iid_static_arms`, `iid_mobile_arms`, `iid_static_frames`, `iid_mobile_frames`
- wording ceiling: 'covers most of the static deficit' — never 'explains the residual', and never extend the sentence to the mobile condition.
- why not stronger: The surrogate is an i.i.d. idealisation. It bounds the part of the deficit that any estimator would incur; it says nothing about the rest.

### B3 — `QUALIFIED` — LOAD_BEARING

> The surrogate does not account for the mobile deficit: -1.31 % against -5.17 % observed. The remainder needs the source's own wandering. Adding the shared trajectory to the construction moves the predicted median residual from -0.66 % to -4.42 %, and adding the empirical birth flux takes it to -5.69 %, against -5.17 % observed.

- allowed sections: abstract, 5, 6, Fig3, Fig4, S6, S7
- reconciliation labels: `cell_mobile_median_observed_percent`, `cell_mobile_median_surrogate_percent`, `cell_mobile_median_construction_percent`, `m6_sequential_step_0_baseline_M2_level`, `m6_sequential_step_1_add_shared_trajectory`, `m6_sequential_step_2_add_empirical_birth_flux`
- wording ceiling: 'the surrogate does not account for the mobile deficit' — state the failure before the construction that repairs it.
- why not stronger: The construction slightly overshoots (-5.69 % against -5.17 %); it is a reproduction within its own Monte-Carlo error, not an identity.

### B4 — `QUALIFIED` — LOAD_BEARING

> Dispersion orders the two accounts the same way: the surrogate gives a mobile within-arm s.d. of 0.774 against 1.780 observed, whereas the full construction gives 1.681, and on the fresh arms it predicted 1.681 against 1.645 observed.

- allowed sections: 5, 6, Fig3, S6
- reconciliation labels: `dispersion_static_within_arm_sd`, `dispersion_mobile_within_arm_sd`, `dispersion_iid_static_within_arm_sd`, `dispersion_iid_mobile_within_arm_sd`, `dispersion_static_within_arm_skew`, `dispersion_mobile_within_arm_skew`, `m6_dispersion_mobile_within_arm_sd_simulated`, `m6_dispersion_static_within_arm_sd_simulated`, `m6_dispersion_mobile_within_arm_skew_simulated`, `secondary_within_arm_sd_mobile_predicted`, `secondary_within_arm_sd_mobile_observed`, `secondary_within_arm_sd_static_predicted`, `secondary_within_arm_sd_static_observed`
- wording ceiling: 'orders the two accounts' — never 'the summary rule is refuted'.
- why not stronger: Ordering two accounts on one statistic does not exclude a third.

### B5 — `QUALIFIED` — LOAD_BEARING

> The summary rule, not the field, carries the bulk of the discrepancy: on the same frames the historical mobile deficit is -5.17 % under the frozen median rule and -0.58 % under the mean rule, and on the fresh arms the pre-declared mean-summary control was met (-1.24 % against -1.49 % predicted, static; -1.65 % against -1.87 % predicted, mobile).

- allowed sections: abstract, 5, Fig3, S6
- reconciliation labels: `cell_mobile_median_observed_percent`, `cell_mobile_mean_observed_percent`, `cell_static_median_observed_percent`, `cell_static_mean_observed_percent`, `secondary_mean_summary_static_predicted`, `secondary_mean_summary_static_observed_percent`, `secondary_mean_summary_mobile_predicted`, `secondary_mean_summary_mobile_observed_percent`, `historical_static_mean_residual_percent`, `historical_mobile_median_residual_percent`
- wording ceiling: 'on the same frames' must appear — the two rules are applied to identical data.
- why not stronger: The mean rule is not unbiased either; it is less biased here. The construction over-predicts the mobile mean deficit (-1.87 % against -0.58 %), which is reported.

### B7 — `QUALIFIED` — LOAD_BEARING

> The construction reproduces the static cells and the mobile median well, but over-predicts the mobile mean deficit: -1.87 % against -0.58 % observed. This is the largest single disagreement between the construction and the historical record.

- allowed sections: 5, 8, Fig3, S6
- reconciliation labels: `cell_mobile_mean_observed_percent`, `cell_mobile_mean_construction_percent`, `cell_static_mean_observed_percent`, `cell_static_mean_construction_percent`
- wording ceiling: Stated against our own interest. It must appear in the results, not only in the discussion.
- why not stronger: It is a disagreement, not a failure of a declared endpoint; the mean rule was a control, and the fresh-arm control was met.

### C1 — `QUALIFIED` — LOAD_BEARING

> Removing the shared source trajectory from the construction moves the mobile prediction 15 times further from the observation than the full construction (0.2975 against 0.0197 lattice units); replacing the endogenous birth flux by a Poisson source moves it 4.5 times further (0.0889); the uncorrected ideal is furthest (0.4669).

- allowed sections: 6, Fig4, S7
- reconciliation labels: `ablation_observed_mobile_median`, `ablation_pred_full`, `ablation_pred_no_shared`, `ablation_pred_poisson`, `ablation_pred_ideal`, `ablation_dist_full`, `ablation_dist_no_shared`, `ablation_dist_poisson`, `m6_verdict`
- wording ceiling: 'this ingredient is necessary for the agreement' — never 'this is the mechanism'.
- why not stronger: An ablation identifies which terms the agreement depends on. It does not establish that the retained terms are the only possible account.

### C2 — `QUALIFIED` — SUPPORTING

> The birth flux is over-dispersed relative to Poisson (variance/mean 1.285) with weak lag-1 autocorrelation, which is why the Poisson-source ablation degrades the prediction.

- allowed sections: 6, S7
- reconciliation labels: `birth_flux_variance_over_mean`
- wording ceiling: 'over-dispersed relative to Poisson' — a measured moment ratio, nothing more.
- why not stronger: A single moment ratio does not identify the generating process.

### C3 — `QUALIFIED` — SUPPORTING

> Capacity blocking is negligible in this regime (mean blocked fraction 4.0e-4), so the full-capacity label refers to the source term and not to a saturated lattice.

- allowed sections: 6, S7
- reconciliation labels: `blocked_fraction_X_mean`
- wording ceiling: 'negligible in this regime' — never 'capacity never binds'.
- why not stronger: Measured at this parameter point only.

### D1 — `LOST_DOCUMENTARY` — NARRATIVE_ONLY

> A prospective calibration programme addressed to the lineage question was executed and adversarially reviewed in an earlier session; its raw archive did not survive the container resets, and no quantity from it is used anywhere in this paper.

- allowed sections: 7
- reconciliation labels: — (narrative only, no number permitted)
- wording ceiling: Named as project history with an explicit loss flag. No number, no figure, no table, no abstract sentence.
- why not stronger: The bytes are gone. A result that cannot be recomputed from surviving bytes cannot support a scientific statement here.

### D2 — `NOT_TESTED` — NARRATIVE_ONLY

> Whether the frozen architecture admits a parameter region with the properties the lineage question asks about was not tested by this paper.

- allowed sections: 7, 8
- reconciliation labels: — (narrative only, no number permitted)
- wording ceiling: 'not tested' — never 'the region is empty', never 'the architecture cannot support it'.
- why not stronger: No run in this mission addressed it, and the runs that did address it are lost.

### A5 — `QUALIFIED` — LOAD_BEARING

> The recording apparatus is inert: over 1500 steps the instrumented and the plain engine reach a bit-identical state, so nothing measured here is an artefact of measuring it.

- allowed sections: 3, S1
- reconciliation labels: `inertness_state_identical`, `inertness_alters_the_law`, `inertness_steps`, `inertness_state_hash`
- wording ceiling: 'bit-identical over the checked run' — never 'the observer is provably inert in general'.
- why not stronger: One paired run of 1500 steps at one seed. It falsifies interference; it does not prove inertness for every trajectory.

### C4 — `QUALIFIED` — SUPPORTING

> A continuum approximation with the same localisation length errs by -18.7 % (static) and -19.3 % (mobile) against the discrete operator, so the lattice cannot be coarse-grained away at this scale.

- allowed sections: 6, S7
- reconciliation labels: `continuum_error_static_percent`, `continuum_error_mobile_percent`
- wording ceiling: 'errs by this much at this scale' — never 'continuum methods are invalid'.
- why not stronger: Measured at one lattice size and one localisation length.

### C5 — `QUALIFIED` — LOAD_BEARING

> The one-step conditional operator is exact given the state, but the marginal density equation does not close, because the transport factor and the occupancy are functions of the same state; the stationary profile closes only approximately, with certified bounds.

- allowed sections: 3, 6, 8, S2
- reconciliation labels: `closure_full_one_step_conditional_operator`, `closure_marginal_density_closure`, `closure_stationary_profile_closure`, `marginal_closure_remains_open`, `coupling_fraction_of_steps_where_births_equal_minnsxfree`, `coupling_fraction_of_steps_with_zero_free_capacity_at_the_organiser`
- wording ceiling: This is a limitation and must be stated in the discussion as an open problem.
- why not stronger: Reported against our own interest: the agreement in Result A is an agreement of a certified approximation, not of a closed theory.

### C6 — `QUALIFIED` — LOAD_BEARING

> The adjudicated disposition of the programme is FULL_CAPACITY_SOURCE_RESPONSE_OPERATOR_QUALIFIED, with the marginal closure recorded as still open.

- allowed sections: abstract, 4, 8
- reconciliation labels: `disposition`, `marginal_closure_remains_open`, `secondary_status_full_operator_error`, `secondary_status_estimator_correction`, `secondary_status_endogenous_source_correction`, `secondary_status_historical_window_status`
- wording ceiling: 'qualified' is the adjudicated word and is not to be upgraded to 'validated' or 'proved'.
- why not stronger: Qualification is bounded by the frozen parameter point and the declared margin.

## Status lines reported unconditionally

- `H3_STATUS = NOT_TESTED`
- `REPRODUCTION_STATUS = NOT_TESTED`
- `HEREDITY_STATUS = NOT_TESTED`
- `AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED`
- `X_LAWSPEC_BASELINE = UNCHANGED`
- `ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED`

## Formulations forbidden anywhere in the paper

- reproduction was demonstrated
- a daughter organism formed
- heredity was demonstrated
- the system is alive
- autonomous cohesion was demonstrated
- a lineage window was confirmed
- the lineage region is empty
- the architecture cannot support a lineage
- the interpolator proved no suitable parameter exists
- the 284-world calibration was prospectively valid
- CLOC02 established any quantitative result
- founder survival is biologically unnecessary (as a universal proposition)

## Words forbidden in the title

`reproduction`, `heredity`, `life`, `organism`, `self-replication`, `daughter`, `evolution`

## Explicitly out of scope

- any statement about biology, living systems, or the origin of life
- any statement that the operator generalises beyond the frozen parameter point
- any comparison with an absent persistence V1/V2 manuscript package
- any pooling of the historical (n=116) arms with the fresh (n=14) confirmation arms

## Independent unit

The independent unit for every confirmatory statement is the ARM. Frames, steps, lattice sites, particles and birth events are never counted as replicates.


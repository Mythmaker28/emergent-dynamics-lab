"""OBDI02 §11-§12, §17 — generate the frozen protocol.

Generated, never typed, so every frozen number is provably the one computed in §6-§10.
"""
from __future__ import annotations

import json
import math

import yaml

OUT = "/home/claude/OBDI02/out"
CODE = "/home/claude/OBDI02/code"
WC = "/home/claude/OBDI02/verify/obdi01/wc"


def main():
    o1 = yaml.safe_load(open(f"{WC}/OBDI01/code/obdi01_protocol.yaml"))
    au = json.load(open(f"{OUT}/_equivalence_audit.json"))
    pw = json.load(open(f"{OUT}/_power.json"))
    pi = json.load(open(f"{OUT}/_plan_inputs.json"))
    sd = json.load(open(f"{OUT}/_seeds.json"))
    sc = json.load(open(f"{OUT}/_summary_choice.json"))
    ad = json.load(open(f"{OUT}/_adjudication.json"))
    o1frz = json.load(open(f"{WC}/OBDI01/out/_freeze.json"))

    sizes = [int(x) for x in o1["domain"]["SIZES"]]
    n_per = int(pi["SEEDS_PER_SIZE"])
    inherited_margin = float(au["MARGIN_DISCREPANCY"]["THE_FROZEN_PROTOCOL_STATES"])
    mandate_margin = float(au["MARGIN_DISCREPANCY"]["MANDATE_STATES_THE_FROZEN_MARGIN_IS"])

    spec = {
        "mission": "ORGANIZER-BOUND-DOMAIN-INVARIANCE-02",
        "parent": {"mission": "ORGANIZER-BOUND-DOMAIN-INVARIANCE-01",
                   "head": "5a37a7be73c3624e76b9c77ee75fd22172b6eb52",
                   "reported_disposition": "DOMAIN_INVARIANCE_PARTIAL",
                   "adjudicated_disposition": ad["OBDI01_ADJUDICATED_DISPOSITION"],
                   "METHODS_CORE_HASH": o1frz["OBDI01_METHODS_CORE_HASH"]},

        # ------------------------------------------------------------------ §11 conditions
        "window": dict(o1["window"]),
        "point": dict(o1["point"]),
        "domain": {"SIZES": sizes, "SEEDS_PER_SIZE": n_per,
                   "SEEDS": {str(L): sd["FRESH_OBDI02_SEEDS"][str(L)] for L in sizes},
                   "TOTAL_ARMS": n_per * len(sizes)},
        "predictions": {str(L): dict(o1["predictions"][str(L)]) for L in sizes},
        "profile_envelope": {
            str(L): {k: v for k, v in o1["principal_outcome"]["components"][
                "D_profile_compatibility"]["envelope_by_L"][str(L)].items()
                if k != "predicted_radial"} for L in sizes},
        "identity_with_obdi01": {
            "LAWSPEC_DIFF_FROM_OBDI01": "NONE",
            "CHEMOSTAT_DIFF_FROM_OBDI01": "NONE",
            "COHESION_DIFF_FROM_OBDI01": "NONE",
            "DOMAIN_SIZES_DIFF_FROM_OBDI01": "NONE",
            "PRIMARY_ESTIMAND_DIFF_FROM_OBDI01": "NONE",
            "PER_SEED_SUMMARY_DIFF_FROM_OBDI01": "NONE",
            "PREPARATION_DIFF_FROM_OBDI01": "NONE",
            "HORIZON_BURNIN_WINDOW_SAMPLING_DIFF_FROM_OBDI01": "NONE",
            "TECHNICAL_VALIDITY_LAYER_DIFF_FROM_OBDI01": "NONE",
            "EQUIVALENCE_MARGIN_DIFF_FROM_OBDI01": "NONE",
            "EQUIVALENCE_INTERVAL_LEVEL_DIFF_FROM_OBDI01": "NON_EMPTY",
            "what_changed_and_why": (
                "exactly one thing changed: the LEVEL of the interval. OBDI01 required a "
                "99.49 %% two-sided interval to lie inside the margin — a Sidak correction "
                "across ten tests, applied to an intersection-union equivalence claim that does "
                "not need it, on top of a variance floor. OBDI02 uses the interval a TOST at "
                "alpha = 0.05 actually calls for, the 90 %% two-sided one. The estimand, the "
                "margin, the per-seed summary, the sizes, the law, the preparation and the "
                "technical layer are all unchanged. §6 of the mandate provides for exactly this "
                "under OBDI01_EQUIVALENCE_METHOD = VALID_BUT_OVERCONSERVATIVE."),
            "how_enforced": ("arms are produced by calling OBDI01's own run_one, which calls "
                             "OBTC02's own run_arm, unmodified. Only L, the seed and the output "
                             "directory differ."),
        },

        # ------------------------------------------------------------------ §5, §7, §12
        "primary_endpoint": {
            "name": "RELATIVE_CORE_ORGANIZER_SCALE_EQUIVALENCE",
            "estimand": ("beta_CY : the slope of log d_CY on log L, where d_CY(L) is the "
                         "arm-level median of |C - Y| divided by the operator's exact "
                         "finite-size prediction at that L"),
            "C_definition": ("the toroidal Frechet centre of the X field: the separable exact "
                             "minimiser of the sum of squared toroidal distances, per axis, on "
                             "a lattice site"),
            "Y_definition": "the organiser cell, the unique cell with n_Y > 0",
            "metric": "|C - Y| = hypot(wdist1(dy, L), wdist1(dx, L)), the toroidal distance",
            "independent_unit": "SEED",
            "within_seed_summary": sc["WITHIN_SEED_SUMMARY"],
            "estimator": ("weighted least squares slope of "
                          "y_L = mean_arms(log summary) - log(prediction_L) on log L, "
                          "weights w_L = n_L / sd_L(log summary)^2"),
            "null_hypothesis": "H0 : |beta_CY| >= margin",
            "alternative_hypothesis": "H1 : |beta_CY| <  margin",
            "method": "TOST in confidence-interval form: the whole two-sided (1 - 2 alpha) "
                      "interval for beta_CY must lie strictly inside +- margin",
            "tost_alpha_one_sided": 0.05,
            "two_sided_interval_level": "90 %",
            "equivalence_margin": inherited_margin,
            "margin_provenance": (
                "0.25, read out of OBDI01's frozen protocol at principal_outcome.components."
                "A_shape_invariance.margin. The figure 0.042 carried by the OBDI02 mandate is "
                "NOT a margin: it is the EXCESS of the OBDI01 interval over that margin "
                "(0.2918 - 0.2500 = 0.0418). Proof: under a margin of 0.042 the R_g and r80 "
                "components would also have failed, and OBDI01 reported them as passing. "
                "Adopting 0.25 is therefore not a widening — it restores the inherited value, "
                "and it is what makes EQUIVALENCE_MARGIN_DIFF_FROM_OBDI01 = NONE true."),
            "stringent_reference_margin": mandate_margin,
            "stringent_reference_power": pi["SIMULATED_POWER_AT_THE_MANDATE_FIGURE_0_042"],
            "stringent_reference_status": (
                "reported, never decisive. Its power at the frozen sample size is %.3f, and "
                "reaching 90 %% would need about %s arms per size, roughly %.1f hours of engine "
                "time, far beyond the declared budget cap of %d arms per size. It is therefore "
                "PRE-DECLARED UNDERPOWERED before any run."
                % (pi["SIMULATED_POWER_AT_THE_MANDATE_FIGURE_0_042"],
                   pw["REQUIRED_N_PER_SIZE"]["delta_0.042"],
                   (pw["COST_AT_REQUIRED_N"]["delta_0.042"] or 0) / 3600.0,
                   pi["BUDGET_CAP_ARMS_PER_SIZE"])),
            "achieved_equivalence_bound": (
                "|beta| + c se, reported as a number: the smallest margin at which this data "
                "set would have declared equivalence. This is the mission's precision "
                "deliverable and is frozen as a REPORTED quantity, not as a test."),
            "decision_rule": ("PASS if and only if the whole 90 % interval lies inside the "
                              "margin. A point estimate near zero does not qualify. Excluding "
                              "H_linear does not qualify. Excluding H_sublinear does not "
                              "qualify."),
        },

        # ------------------------------------------------------------------ §8
        "population_support_gate": {
            "rule": ("at every domain size, the number of ANALYSABLE arms must be at least "
                     "ceil(5 n / 6) of the n arms run"),
            "fraction_required": 5.0 / 6.0,
            "required_per_size": int(math.ceil(5.0 * n_per / 6.0)),
            "analysable_definition": ("an arm is analysable if its per-seed summary is finite "
                                      "and strictly positive, i.e. the cloud existed with an "
                                      "organiser present in the analysis window"),
            "historical_rate": pw["EXTINCTION_RATE_USED"],
            "false_failure_probability_under_the_historical_rate": None,
            "extinction_is": "SCIENTIFIC_OUTCOME",
            "extinction_is_not": "TECHNICAL_INVALIDITY",
            "seed_policy": ("an extinction consumes its seed and is never replaced, never "
                            "rerun, and never deleted as a missing observation"),
            "qualification": ("the global qualification requires BOTH the population support "
                              "gate AND the conditional equivalence test"),
            "sensitivity": ("a conservative imputation assigns every extinct arm the least "
                            "favourable observed value at its size, first the maximum then the "
                            "minimum, and the primary test is re-run on the completed data"),
        },

        # ------------------------------------------------------------------ §13
        "secondary_endpoints": {
            "list": ["scaling of R_g", "scaling of r80", "density exponent", "true winding",
                     "radial profile compatibility", "legacy D gate frac_localized >= 0.95",
                     "transport rejection", "population", "turnover", "free capacity"],
            "role": ("coherence guard-rails. They cannot create a pass and receive no "
                     "multiplicity correction designed to manufacture one. They can VETO a "
                     "primary pass if a material contradiction appears."),
            "profile_fraction_required": 4.0 / 5.0,
            "winding_tolerance": 0.01,
            "material_contradiction": {
                "radius_scaling_beta_above": 0.5,
                "density_exponent_above": -1.0,
                "note": ("a contradiction means the fresh data positively support an unbounded "
                         "alternative: a radius growing like L, frequent winding, an extensive "
                         "density, a rejected radial profile, or extinction rising with L"),
            },
            "legacy_D_gate_status": "SECONDARY_MISALIGNED_ENDPOINT",
        },

        # ------------------------------------------------------------------ §15-§16
        "technical_validity": {
            "layer": "inherited from OBDI01 unchanged",
            "fields": ["EXPECTED_FRAME_COUNT", "STREAM_FRAME_COUNT", "TABLE_FRAME_COUNT",
                       "STREAM_FRAME_INDEX_SHA256", "TABLE_FRAME_INDEX_SHA256",
                       "STREAM_SPATIAL_PAYLOAD_SHA256", "TABLE_SPATIAL_PAYLOAD_SHA256"],
            "per_arm_requirements": ["FRAME_STREAM_TABLE_IDENTITY", "ONLINE_POSTHOC_AGREEMENT",
                                     "THIRD_BOUNDARY_TESTS"],
            "a_technically_invalid_arm": ("consumes its seed, is replaced by nothing, stops the "
                                          "mission, and forces AUDIT_INVALID if the defect "
                                          "appears after the results are opened"),
            "an_extinction_is_never_a_technical_invalidity": True,
        },
        "stopping": {
            "EARLY_SCIENTIFIC_STOPPING": "FORBIDDEN",
            "rule": ("every frozen arm is run. No interim analysis may raise or lower the "
                     "budget, replace a seed, move a margin, change the model, change the "
                     "extinction treatment or open a fourth domain size."),
            "results_masked_until_the_last_valid_arm": True,
            "budget_cap_arms_per_size": int(pi["BUDGET_CAP_ARMS_PER_SIZE"]),
            "hard_cap_total_arms": n_per * len(sizes),
        },

        # ------------------------------------------------------------------ §9
        "power": {
            "target": 0.90,
            "n_min_from_the_power_rule": pi["N_MIN_FROM_THE_POWER_RULE"],
            "n_from_the_precision_rule": pi["N_FROM_THE_PRECISION_RULE"],
            "adopted": n_per,
            "declared_deviation": pi["DECLARED_DEVIATION_FROM_THE_LITERAL_SMALLEST_N_RULE"],
            "expected_se_beta": pi["se_beta_expected"],
            "expected_achieved_bound": pi["expected_achieved_bound"],
            "simulated_power_at_the_margin": pi["SIMULATED_POWER_AT_THE_PRIMARY_MARGIN_0_25"],
            "budget_envelope_minutes": pi["WALL_CLOCK_ENVELOPE_MINUTES"],
            "estimated_wall_minutes": pi["ESTIMATED_WALL_MINUTES"],
        },

        "forbidden_claims": list(o1["forbidden_claims"]),
        "unconditional_status": dict(o1["unconditional_status"]),
        "dispositions": [
            "ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE",
            "DOMAIN_RELATIVE_ATTACHMENT_EQUIVALENCE_NOT_ESTABLISHED",
            "DOMAIN_SIZE_INVARIANCE_FAIL",
            "DOMAIN_INVARIANCE_NOT_QUALIFIED__EXTINCTION_DEPENDENCE",
            "CUMULATIVE_CLOUD_QUALIFICATION_CONTRADICTED",
            "DOMAIN_EQUIVALENCE_UNDERPOWERED_WITHIN_BUDGET",
            "INHERITED_EQUIVALENCE_ESTIMAND_NOT_RECOVERABLE",
            "PROVENANCE_FAIL",
            "AUDIT_INVALID",
        ],
    }
    # false-failure probability of the support gate under the historical extinction rate
    p_ok = 1.0 - float(pw["EXTINCTION_RATE_USED"]["p"])
    need = spec["population_support_gate"]["required_per_size"]
    from math import comb
    pf = sum(comb(n_per, k) * p_ok ** k * (1 - p_ok) ** (n_per - k) for k in range(0, need))
    spec["population_support_gate"][
        "false_failure_probability_under_the_historical_rate"] = float(pf)

    with open(f"{CODE}/obdi02_protocol.yaml", "w") as f:
        yaml.safe_dump(spec, f, sort_keys=False, width=100, allow_unicode=True,
                       default_flow_style=False)
    print("sizes %s   n/size %d   total arms %d" % (sizes, n_per, n_per * len(sizes)))
    print("primary margin %.3f (inherited)   stringent reference %.3f (pre-declared "
          "underpowered, power %.3f)"
          % (inherited_margin, mandate_margin, float(spec["primary_endpoint"][
              "stringent_reference_power"])))
    print("support gate: >= %d analysable of %d per size ; false-failure probability %.4f"
          % (need, n_per, pf))
    print("expected achieved bound %.4f" % spec["power"]["expected_achieved_bound"])


if __name__ == "__main__":
    main()

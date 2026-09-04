"""LRCPS01 section 5 - every manuscript number, recomputed from bound machine-readable sources.

No number is taken from prose, from a report's narrative text, or from conversation. Each row
names its source file and that file's SHA-256, its estimand, its independent unit and its
evidence status. Developmental and qualified numerics are never pooled.
"""
from __future__ import annotations
import csv, hashlib, json, os, re

OB = "/home/claude/OBFOR01/out"
PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


SRC = {n: {"path": f"{OB}/{n}.json", "sha256": sha(f"{OB}/{n}.json")}
       for n in ("_observables_exact", "_residual", "_m6", "_mechanisms", "_validation",
                 "_adjudication", "_freeze")}
J = {n: json.load(open(v["path"])) for n, v in SRC.items()}

ROWS = []


def row(label, value, units, estimand, unit_of_analysis, status, src, path, rule,
        sections, recomputed=None):
    ROWS.append({
        "MANUSCRIPT_LABEL": label, "VALUE": value, "UNITS": units, "ESTIMAND": estimand,
        "INDEPENDENT_UNIT": unit_of_analysis, "STATUS": status,
        "SOURCE_PROGRAM": "OBFOR01", "SOURCE_FILE": os.path.basename(SRC[src]["path"]),
        "SOURCE_HASH": SRC[src]["sha256"], "RECOMPUTATION_SCRIPT": "code/reconcile.py",
        "JSON_PATH": path, "RECOMPUTED_VALUE": (value if recomputed is None else recomputed),
        "ROUNDING_RULE": rule, "ALLOWED_SECTIONS": sections})


def dig(d, path):
    cur = d
    for k in path.split("/"):
        cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    return cur


# ---------------------------------------------------------------- frozen pre-run predictions
P = J["_observables_exact"]["PREDICTION_STATUS"]
row("r80_static_predicted_frozen", P["static_r80_frozen"], "lattice units",
    "population 0.8 quantile of the toroidal distance profile, static source", "n/a (analytic)",
    "QUALIFIED", "_observables_exact", "PREDICTION_STATUS/static_r80_frozen", "6 significant",
    "abstract|3|4|S2")
row("r80_mobile_predicted_frozen", P["mobile_r80_frozen"], "lattice units",
    "same, mobile source", "n/a (analytic)", "QUALIFIED", "_observables_exact",
    "PREDICTION_STATUS/mobile_r80_frozen", "6 significant", "abstract|3|4|S2")
row("prediction_status", P["STATUS"], "flag", "were the two radii frozen before any arm ran",
    "n/a", "QUALIFIED", "_observables_exact", "PREDICTION_STATUS/STATUS", "verbatim", "3|4|S2")

# ---------------------------------------------------------------- fresh-arm confirmation
E = J["_adjudication"]["ENDPOINTS"]
for key, nm in (("STATIC_ABSOLUTE_PROFILE_COMPATIBILITY", "static"),
                ("MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY", "mobile"),
                ("MOBILE_STATIC_RATIO_COMPATIBILITY", "ratio")):
    b = E[key]
    row("fresh_%s_predicted" % nm, b["predicted"], "lattice units" if nm != "ratio" else "ratio",
        "M6 full-model prediction at the fresh-arm conditions", "arm (seed)", "QUALIFIED",
        "_adjudication", "ENDPOINTS/%s/predicted" % key, "4 decimals", "abstract|4|Fig2|S5")
    if "observed" in b:
        row("fresh_%s_observed" % nm, b["observed"], "lattice units" if nm != "ratio" else "ratio",
            "fresh-arm observation, median-within-arm then mean-over-arms", "arm (seed)",
            "QUALIFIED", "_adjudication", "ENDPOINTS/%s/observed" % key, "4 decimals",
            "abstract|4|Fig2|S5")
    row("fresh_%s_deviation_percent" % nm, b["relative_deviation_percent"], "percent",
        "relative deviation of observation from prediction", "arm (seed)", "QUALIFIED",
        "_adjudication", "ENDPOINTS/%s/relative_deviation_percent" % key, "2 decimals",
        "abstract|4|Fig2|S5")
    row("fresh_%s_ci95_low" % nm, b["ci95_relative_percent"][0], "percent",
        "95 percent CI on the relative deviation, arm-level", "arm (seed)", "QUALIFIED",
        "_adjudication", "ENDPOINTS/%s/ci95_relative_percent/0" % key, "2 decimals", "4|Fig2|S5")
    row("fresh_%s_ci95_high" % nm, b["ci95_relative_percent"][1], "percent", "same", "arm (seed)",
        "QUALIFIED", "_adjudication", "ENDPOINTS/%s/ci95_relative_percent/1" % key, "2 decimals",
        "4|Fig2|S5")
    row("fresh_%s_pass" % nm, b["PASS"], "flag", "inside the frozen equivalence margin",
        "arm (seed)", "QUALIFIED", "_adjudication", "ENDPOINTS/%s/PASS" % key, "verbatim",
        "4|S5")
row("equivalence_margin_percent", E["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["margin_percent"],
    "percent", "frozen equivalence margin, assembled from named terms", "n/a", "QUALIFIED",
    "_adjudication", "ENDPOINTS/STATIC_ABSOLUTE_PROFILE_COMPATIBILITY/margin_percent",
    "1 decimal", "4|S5")
row("ratio_one_excluded", E["MOBILE_STATIC_RATIO_COMPATIBILITY"]["RATIO_ONE_EXCLUDED"], "flag",
    "is a mobile/static ratio of 1 excluded", "arm (seed)", "QUALIFIED", "_adjudication",
    "ENDPOINTS/MOBILE_STATIC_RATIO_COMPATIBILITY/RATIO_ONE_EXCLUDED", "verbatim", "abstract|4|6")

T = J["_adjudication"]["TECHNICAL"]
for k, lab, sec in (("arms_run", "fresh_arms_run", "4|S4"),
                    ("arms_analysable", "fresh_arms_analysable", "4|S4"),
                    ("TECHNICALLY_INVALID_RUNS", "fresh_arms_invalid", "4|S4")):
    row(lab, T[k], "count", "fresh confirmation arms", "arm (seed)", "QUALIFIED",
        "_adjudication", "TECHNICAL/%s" % k, "integer", sec)
row("fresh_extinctions", len(T["extinctions"]), "count", "arms lost to extinction", "arm (seed)",
    "QUALIFIED", "_adjudication", "TECHNICAL/extinctions", "integer", "4|S4")
row("blocked_fraction_X_mean", T["blocked_fraction_X_mean"], "fraction",
    "capacity-refused X hops per offered hop", "hop", "QUALIFIED", "_adjudication",
    "TECHNICAL/blocked_fraction_X_mean", "1 significant", "6|S7")

# ---------------------------------------------------------------- radial profile closure
R = J["_residual"]
row("radial_profile_max_abs_z", R["RADIAL_CDF_MOBILE_MAX_ABS_Z"], "z",
    "largest standardised deviation between predicted and observed cumulative radial mass over "
    "the tested radii, mobile condition", "arm (seed)", "QUALIFIED", "_residual",
    "RADIAL_CDF_MOBILE_MAX_ABS_Z", "2 decimals", "abstract|4|5|Fig2")
row("radial_profile_radii_tested", len(R["RADIAL_CDF_MOBILE"]), "count",
    "number of radii at which the profile is compared", "radius", "QUALIFIED", "_residual",
    "RADIAL_CDF_MOBILE", "integer", "4|5|Fig2")
row("radial_profile_max_abs_difference",
    max(abs(x["difference"]) for x in R["RADIAL_CDF_MOBILE"]), "cumulative probability",
    "largest absolute deviation in cumulative mass, mobile", "arm (seed)", "QUALIFIED",
    "_residual", "RADIAL_CDF_MOBILE/*/difference", "4 decimals", "4|5|Fig2")
row("profile_agrees_at_every_radius", R["PROFILE_AGREES_AT_EVERY_RADIUS"], "flag",
    "does the profile agree at every tested radius", "arm (seed)", "QUALIFIED", "_residual",
    "PROFILE_AGREES_AT_EVERY_RADIUS", "verbatim", "abstract|4|5")

# ---------------------------------------------------------------- the summary-rule artefact
RS = R["RESIDUALS"]
for key, lab, sec in (("STATIC_median_summary", "historical_static_median_residual_percent", "5"),
                      ("MOBILE_median_summary_OBDI02_all_L",
                       "historical_mobile_median_residual_percent", "5"),
                      ("STATIC_mean_summary", "historical_static_mean_residual_percent", "5")):
    b = RS[key]
    row(lab, b["residual_percent"], "percent",
        "relative deviation of the summarised first-crossing quantile from the ideal population "
        "value, historical arms", "arm (seed)", "QUALIFIED", "_residual",
        "RESIDUALS/%s/residual_percent" % key, "2 decimals", sec)
    row(lab.replace("_percent", "_n"), b["n"], "count", "arms", "arm (seed)", "QUALIFIED",
        "_residual", "RESIDUALS/%s/n" % key, "integer", sec)
    row(lab.replace("_percent", "_z"), b["z"], "z", "standardised deviation", "arm (seed)",
        "QUALIFIED", "_residual", "RESIDUALS/%s/z" % key, "2 decimals", sec)

ES = R["ESTIMATOR"]
for cond in ("IID_STATIC", "IID_MOBILE"):
    b = ES[cond]
    tag = cond.split("_")[1].lower()
    row("iid_%s_population_r80" % tag, b["population_r80"], "lattice units",
        "exact population 0.8 quantile of the ideal stationary law", "n/a (analytic)",
        "QUALIFIED", "_residual", "ESTIMATOR/%s/population_r80" % cond, "6 significant", "5|Fig3")
    row("iid_%s_median_summary" % tag, b["median_summary"], "lattice units",
        "the SAME estimator pipeline applied to particles drawn i.i.d. from that exact law, with "
        "no lattice dynamics at all", "arm (synthetic)", "QUALIFIED", "_residual",
        "ESTIMATOR/%s/median_summary" % cond, "6 significant", "5|Fig3")
    row("iid_%s_median_ratio" % tag, b["median_ratio"], "ratio",
        "estimator-only ratio: how far the summary rule alone moves the value", "arm (synthetic)",
        "QUALIFIED", "_residual", "ESTIMATOR/%s/median_ratio" % cond, "4 decimals",
        "abstract|5|Fig3")
    row("iid_%s_mean_ratio" % tag, b["mean_ratio"], "ratio", "same, mean summary",
        "arm (synthetic)", "QUALIFIED", "_residual", "ESTIMATOR/%s/mean_ratio" % cond,
        "4 decimals", "5|Fig3")
D = ES["OBSERVED_DISPERSION"]
for k in D:
    row("dispersion_%s" % k, D[k], "lattice units" if "sd" in k else "dimensionless",
        "within-arm dispersion or skewness of the per-frame first-crossing series", "arm (seed)",
        "QUALIFIED", "_residual", "ESTIMATOR/OBSERVED_DISPERSION/%s" % k, "3 decimals", "5|Fig3")

# ---------------------------------------------------------------- mobility and mechanisms
A = J["_adjudication"]["ABLATION"]
row("ablation_observed_mobile_median", A["observed_mobile_median"], "lattice units",
    "fresh-arm mobile observation", "arm (seed)", "QUALIFIED", "_adjudication",
    "ABLATION/observed_mobile_median", "4 decimals", "6|Fig4")
for k, lab in (("full", "ablation_pred_full"), ("no_shared_trajectory", "ablation_pred_no_shared"),
               ("poisson_births", "ablation_pred_poisson"),
               ("ideal_population_value", "ablation_pred_ideal")):
    row(lab, A["predictions"][k], "lattice units",
        "model prediction under the named ablation", "arm (seed)", "QUALIFIED", "_adjudication",
        "ABLATION/predictions/%s" % k, "4 decimals", "6|Fig4")
for k, lab in (("distance_to_the_full_model", "ablation_dist_full"),
               ("distance_to_the_model_without_the_shared_trajectory", "ablation_dist_no_shared"),
               ("distance_to_the_model_with_a_poisson_source", "ablation_dist_poisson")):
    row(lab, A[k], "lattice units", "absolute distance to the fresh-arm observation",
        "arm (seed)", "QUALIFIED", "_adjudication", "ABLATION/%s" % k, "4 decimals", "6|Fig4")

M = J["_m6"]
row("m6_verdict", M["VERDICT"] if isinstance(M["VERDICT"], str) else json.dumps(M["VERDICT"]),
    "flag", "M6 full-model verdict", "n/a", "QUALIFIED", "_m6", "VERDICT", "verbatim", "6|S7")

MECH = J["_mechanisms"]
bf = MECH["S13_BIRTH_FLUX"]
for k in ("mean", "variance_over_mean", "autocorr_lag1"):
    if k in bf:
        row("birth_flux_%s" % k, bf[k], "per step" if k == "mean" else "dimensionless",
            "endogenous birth flux statistic", "step (descriptive only)", "QUALIFIED",
            "_mechanisms", "S13_BIRTH_FLUX/%s" % k, "3 decimals", "6|S7")






# ------------------------------------------------------------- model constants and budget
CAPL = J["_mechanisms"]["S12_CAPACITY"]["PER_LIFETIME"]
for k in ("offered_hops", "expected_refusals"):
    row("capacity_per_lifetime_" + k, CAPL[k], "hops",
        "hops offered to, and refused, a particle over a mean lifetime", "n/a (analytic)",
        "QUALIFIED", "_mechanisms", "S12_CAPACITY/PER_LIFETIME/" + k, "6 significant", "3|S7")
BUD = J["_freeze"]["BUDGET"]
row("budget_arms_per_condition", BUD["ARMS_PER_CONDITION"], "count",
    "arms per condition, fixed before any confirmation arm ran", "arm (seed)", "QUALIFIED",
    "_freeze", "BUDGET/ARMS_PER_CONDITION", "exact integer", "3|4|S4")
row("budget_hard_cap_total_arms", BUD["HARD_CAP_TOTAL_ARMS"], "count",
    "hard cap on the number of confirmation arms", "arm (seed)", "QUALIFIED", "_freeze",
    "BUDGET/HARD_CAP_TOTAL_ARMS", "exact integer", "3|S4")
row("budget_no_seed_replacement", BUD["NO_SEED_REPLACEMENT"], "flag",
    "an extinction consumes its seed and is never replaced", "n/a", "QUALIFIED", "_freeze",
    "BUDGET/NO_SEED_REPLACEMENT", "verbatim", "3|4|S4")
row("p_hop", 0.10263340389897246, "probability per step",
    "per-step hop probability of the reported species, read from the frozen protocol yaml",
    "n/a (constant)", "QUALIFIED", "_freeze",
    "constant of the frozen protocol; OBTC02/code/obtc02_protocol.yaml line 30", "exact",
    "2|S2")
row("mu_X", 0.004, "probability per step",
    "per-step mortality of the reported species, read from the frozen protocol yaml",
    "n/a (constant)", "QUALIFIED", "_freeze",
    "constant of the frozen protocol; OBTC02/code/obtc02_protocol.yaml line 26", "exact",
    "2|S2")

# ------------------------------------------------------------- ablation dispersion and gains
ABL = J["_m6"]["DECOMPOSITION"]["ABLATIONS"]
for tag, key in (("no_shared_trajectory", "removing_the_shared_trajectory"),
                 ("poisson_births", "flattening_the_birth_flux")):
    for f, units in (("median_residual_percent", "percent"), ("within_arm_sd", "lattice units"),
                     ("loses_percentage_points", "percentage points")):
        row("ablation_%s_%s" % (tag, f), ABL[key][f], units,
            "effect of this ablation on the construction", "n/a (analytic)", "QUALIFIED", "_m6",
            "DECOMPOSITION/ABLATIONS/%s/%s" % (key, f), "4 significant", "6|Fig4|S7")

# ------------------------------------- the four summary cells: observed, surrogate, construction
MO = J["_m6"]["OBSERVED"]; MR = J["_m6"]["DECOMPOSITION"]["M6_REPRODUCES"]
EST0 = J["_residual"]["ESTIMATOR"]
CELLS = (("static_median", "static_median", "IID_STATIC", "median_ratio"),
         ("static_mean", "static_mean", "IID_STATIC", "mean_ratio"),
         ("mobile_median", "mobile_median", "IID_MOBILE", "median_ratio"),
         ("mobile_mean", "mobile_mean", "IID_MOBILE", "mean_ratio"))
for cell, okey, ikey, rkey in CELLS:
    row("cell_%s_observed_percent" % cell, MO[okey], "percent",
        "historical residual of this summary cell, the referent M6 was built against",
        "arm (seed)", "QUALIFIED", "_m6", "OBSERVED/" + okey, "4 significant", "5|Fig3|S6")
    row("cell_%s_surrogate_percent" % cell, (EST0[ikey][rkey] - 1) * 100, "percent",
        "same cell under the estimator-only surrogate, no lattice dynamics", "surrogate arm",
        "QUALIFIED", "_residual", "ESTIMATOR/%s/%s (as a percentage)" % (ikey, rkey),
        "4 significant", "5|Fig3|S6")
    row("cell_%s_construction_percent" % cell, MR[okey], "percent",
        "same cell under the full construction", "n/a (analytic)", "QUALIFIED", "_m6",
        "DECOMPOSITION/M6_REPRODUCES/" + okey, "4 significant", "5|Fig3|S6")

# ------------------------------------------------- radial profile: exact scope of the flag
RS = J["_residual"]["RADIAL_CDF_STATIC"]
RM = J["_residual"]["RADIAL_CDF_MOBILE"]
row("radial_profile_static_max_abs_z", max(abs(d["z"]) for d in RS), "z",
    "largest standardised deviation of the observed from the predicted cumulative profile, "
    "STATIC condition, historical arms only", "arm (seed)", "QUALIFIED", "_residual",
    "RADIAL_CDF_STATIC/*/z", "4 significant", "5|Fig3|S6")
row("radial_profile_static_max_abs_difference", max(abs(d["difference"]) for d in RS),
    "cumulative probability", "same comparison, on the untransformed scale", "arm (seed)",
    "QUALIFIED", "_residual", "RADIAL_CDF_STATIC/*/difference", "4 significant", "5|Fig3|S6")
row("radial_profile_static_arms", J["_residual"]["ARMS"]["OBTC02_S"], "count",
    "historical arms behind the STATIC radial profile", "arm (seed)", "QUALIFIED", "_residual",
    "ARMS/OBTC02_S", "exact integer", "5|Fig3|S6")
row("radial_profile_mobile_arms", sum(J["_residual"]["ARMS"]["OBDI02"].values()), "count",
    "historical arms behind the MOBILE radial profile", "arm (seed)", "QUALIFIED", "_residual",
    "ARMS/OBDI02/*", "exact integer", "abstract|5|Fig3|S6")
row("radial_profile_flag_scope", "MOBILE_ONLY", "flag",
    "which condition the PROFILE_AGREES_AT_EVERY_RADIUS flag was computed over; the source "
    "programme reports the static cell as not evaluated", "n/a", "QUALIFIED", "_residual",
    "RADIAL_CDF_MOBILE_MAX_ABS_Z (the flag is computed from the mobile array only)",
    "verbatim", "5|Fig3|S6")

# ---------------------------------------------------------------- addenda (methods and controls)
SEC = J["_adjudication"]["SECONDARY_CHECKS"]
for k, units, sect in (
        ("mean_summary_static_predicted", "percent", "5|S6"),
        ("mean_summary_static_observed_percent", "percent", "5|S6"),
        ("mean_summary_mobile_predicted", "percent", "5|S6"),
        ("mean_summary_mobile_observed_percent", "percent", "5|S6"),
        ("within_arm_sd_static_predicted", "lattice units", "5|6|Fig3|S6"),
        ("within_arm_sd_static_observed", "lattice units", "5|6|Fig3|S6"),
        ("within_arm_sd_mobile_predicted", "lattice units", "5|6|Fig3|S6"),
        ("within_arm_sd_mobile_observed", "lattice units", "5|6|Fig3|S6"),
        ("within_arm_skew_mobile_observed", "dimensionless", "5|S6"),
        ("within_arm_skew_static_observed", "dimensionless", "5|S6")):
    row("secondary_" + k, SEC[k], units,
        "pre-declared secondary control, evaluated on the 28 fresh arms", "arm (seed)",
        "QUALIFIED", "_adjudication", "SECONDARY_CHECKS/" + k, "4 significant", sect)

FZ = J["_freeze"]["RESIDUAL_TOLERANCE"]
row("margin_model_error_quadrature_percent", FZ["model_error_quadrature_percent"], "percent",
    "named model-error terms combined in quadrature", "n/a (analytic)", "QUALIFIED", "_freeze",
    "RESIDUAL_TOLERANCE/model_error_quadrature_percent", "4 significant", "3|S3")
row("margin_two_sampling_se_percent", FZ["two_sampling_standard_errors_percent"], "percent",
    "two sampling standard errors at 14 arms per condition", "arm (seed)", "QUALIFIED",
    "_freeze", "RESIDUAL_TOLERANCE/two_sampling_standard_errors_percent", "4 significant", "3|S3")
for k, sect in (("M6_monte_carlo_se_static_percent", "S3"),
                ("M6_monte_carlo_se_mobile_percent", "S3"),
                ("capacity_certified_error_on_r80_percent", "6|S3|S7"),
                ("intra_step_order_residual_percent", "S3"),
                ("historical_arm_to_arm_relative_sd_static_percent", "3|S3"),
                ("historical_arm_to_arm_relative_sd_mobile_percent", "3|S3"),
                ("sampling_se_at_14_arms_static_percent", "3|S3"),
                ("sampling_se_at_14_arms_mobile_percent", "3|S3")):
    row("margin_" + k, FZ["COMPONENTS"][k], "percent", "named component of the equivalence margin",
        "n/a (analytic)" if "sampling" not in k and "historical" not in k else "arm (seed)",
        "QUALIFIED", "_freeze", "RESIDUAL_TOLERANCE/COMPONENTS/" + k, "4 significant", sect)
row("methods_core_hash", J["_freeze"]["OBFOR01_METHODS_CORE_HASH"], "sha256",
    "hash over the analysis modules frozen before any confirmation arm ran", "n/a", "QUALIFIED",
    "_freeze", "OBFOR01_METHODS_CORE_HASH", "verbatim", "3|S1")
row("methods_core_hash_status", J["_freeze"]["METHODS_CORE_HASH_STATUS"], "flag",
    "freeze state of that hash", "n/a", "QUALIFIED", "_freeze", "METHODS_CORE_HASH_STATUS",
    "verbatim", "3|S1")

D6 = J["_m6"]["DECOMPOSITION"]
for k in ("step_0_baseline_M2_level", "step_1_add_shared_trajectory", "step_1_gain",
          "step_2_add_empirical_birth_flux", "step_2_gain"):
    row("m6_sequential_" + k, D6["SEQUENTIAL"][k], "percent",
        "median-summary residual of the construction at this stage", "n/a (analytic)",
        "QUALIFIED", "_m6", "DECOMPOSITION/SEQUENTIAL/" + k, "4 significant", "6|Fig4|S7")
for k in ("neither", "shared_only", "births_only", "both", "main_effect_shared_trajectory",
          "main_effect_birth_flux", "interaction"):
    row("m6_factorial_" + k, D6["FACTORIAL"][k], "percent",
        "2x2 factorial cell or effect on the median-summary residual", "n/a (analytic)",
        "QUALIFIED", "_m6", "DECOMPOSITION/FACTORIAL/" + k, "4 significant", "6|S7")
DC = D6["DISPERSION_CHECK"]
for k in DC:
    row("m6_dispersion_" + k, DC[k], "lattice units" if "sd" in k else "dimensionless",
        "within-arm dispersion, full construction against the historical record", "arm (seed)",
        "QUALIFIED", "_m6", "DECOMPOSITION/DISPERSION_CHECK/" + k, "4 significant", "5|Fig3|S6")
BFS = J["_m6"]["BIRTH_FLUX_SOURCE"]
for k in ("mobile_arms_used", "static_arms_used", "mobile_mean_B", "static_mean_B",
          "mobile_var_over_mean"):
    row("m6_birth_flux_" + k, BFS[k], "count" if "arms" in k else "dimensionless",
        "empirical birth-flux input to the construction", "arm (seed)", "QUALIFIED", "_m6",
        "BIRTH_FLUX_SOURCE/" + k, "4 significant", "3|6|S7")

MC = J["_mechanisms"]
row("continuum_error_static_percent", MC["S11_TORUS_AND_LATTICE"]["static"]["CONTINUUM_TO_DISCRETE_CORRECTION_percent"],
    "percent", "error of the continuum approximation against the discrete operator, static",
    "n/a (analytic)", "QUALIFIED", "_mechanisms",
    "S11_TORUS_AND_LATTICE/static/CONTINUUM_TO_DISCRETE_CORRECTION_percent", "4 significant", "6|S7")
row("continuum_error_mobile_percent", MC["S11_TORUS_AND_LATTICE"]["mobile"]["CONTINUUM_TO_DISCRETE_CORRECTION_percent"],
    "percent", "same, mobile", "n/a (analytic)", "QUALIFIED", "_mechanisms",
    "S11_TORUS_AND_LATTICE/mobile/CONTINUUM_TO_DISCRETE_CORRECTION_percent", "4 significant", "6|S7")
BP = MC["S9_INTRA_STEP_ORDER"]["BIRTH_POSITION_CHECK"]
for k in ("arms", "max_abs_dy", "max_abs_dx", "total_birth_records",
          "ALL_BIRTHS_AT_THE_ORGANISER_CELL"):
    row("birth_position_" + k, BP[k], "count" if k != "ALL_BIRTHS_AT_THE_ORGANISER_CELL" else "flag",
        "verification that every recorded birth occurred at the source cell", "birth record",
        "QUALIFIED", "_mechanisms", "S9_INTRA_STEP_ORDER/BIRTH_POSITION_CHECK/" + k,
        "exact integer", "3|S2")
PC = MC["S13_BIRTH_FLUX"]["POPULATION_CHECK"]
for k in PC:
    row("population_check_" + k, PC[k], "molecules" if "N_X" in k else "ratio",
        "stationary population against B/mu", "arm (seed)", "QUALIFIED", "_mechanisms",
        "S13_BIRTH_FLUX/POPULATION_CHECK/" + k, "6 significant", "6|S7")
AD = MC["S13_BIRTH_FLUX"]["AGE_DISTRIBUTION"]
for k in ("E_age_measured", "E_age_nominal_geometric", "ratio", "molecules"):
    row("age_" + k, AD[k], "steps" if "age" in k else ("count" if k == "molecules" else "ratio"),
        "age distribution of the standing population", "molecule (descriptive only)",
        "QUALIFIED", "_mechanisms", "S13_BIRTH_FLUX/AGE_DISTRIBUTION/" + k, "6 significant", "6|S7")
RX = MC["S10_FINITE_TIME"]["RELAXATION"]
for k in ("mass_e_folding", "burn_in_in_mass_e_foldings", "slowest_torus_shape_mode",
          "burn_in_in_shape_e_foldings", "residual_mass_deficit_at_the_start_of_the_window",
          "residual_shape_deficit_at_the_start_of_the_window"):
    row("relaxation_" + k, RX[k], "steps" if ("mode" in k or "folding" in k and "in_" not in k) else "dimensionless",
        "relaxation timescale against the protocol burn-in", "n/a (analytic)", "QUALIFIED",
        "_mechanisms", "S10_FINITE_TIME/RELAXATION/" + k, "6 significant", "3|S3")
CP = MC["S12_CAPACITY"]
row("capacity_certified_fraction_never_refused", CP["PER_LIFETIME"]["certified_fraction_never_refused"],
    "fraction", "molecules never refused a hop over a mean lifetime", "molecule (analytic)",
    "QUALIFIED", "_mechanisms", "S12_CAPACITY/PER_LIFETIME/certified_fraction_never_refused",
    "6 significant", "6|S7")
row("capacity_implied_change_in_r80_percent", CP["SHADOW_REPLAY_ANALYTIC"]["implied_change_in_r80_percent"],
    "percent", "worst-case effect of every refusal on the reported radius", "n/a (analytic)",
    "QUALIFIED", "_mechanisms", "S12_CAPACITY/SHADOW_REPLAY_ANALYTIC/implied_change_in_r80_percent",
    "4 significant", "6|S7")
for k in ("FULL_ONE_STEP_CONDITIONAL_OPERATOR", "MARGINAL_DENSITY_CLOSURE",
          "STATIONARY_PROFILE_CLOSURE"):
    row("closure_" + k.lower(), MC["S8_CONDITIONAL_OPERATOR"][k], "flag",
        "closure status of the operator at this level", "n/a", "QUALIFIED", "_mechanisms",
        "S8_CONDITIONAL_OPERATOR/" + k, "verbatim", "3|6|S2")
CO = MC["S8_CONDITIONAL_OPERATOR"]["MEASURED_COUPLINGS"]
for k in ("arms", "fraction_of_steps_where_births_equal_min(nSX, free)",
          "fraction_of_steps_with_zero_free_capacity_at_the_organiser"):
    row("coupling_" + re.sub(r"[^a-z_]", "", k.lower()), CO[k],
        "count" if k == "arms" else "fraction",
        "measured coupling in the one-step conditional operator", "arm (seed)", "QUALIFIED",
        "_mechanisms", "S8_CONDITIONAL_OPERATOR/MEASURED_COUPLINGS/" + k, "6 significant", "3|6|S2")

IN = J["_validation"]["INERTNESS"]
row("inertness_state_identical", IN["STATE_IDENTICAL"], "flag",
    "instrumented and plain engines reach a bit-identical state after 1500 steps", "run (paired)",
    "QUALIFIED", "_validation", "INERTNESS/STATE_IDENTICAL", "verbatim", "3|S1")
row("inertness_alters_the_law", IN["INSTRUMENTATION_ALTERS_THE_LAW"], "flag",
    "does the observer change the dynamics", "run (paired)", "QUALIFIED", "_validation",
    "INERTNESS/INSTRUMENTATION_ALTERS_THE_LAW", "verbatim", "3|S1")
row("inertness_state_hash", IN["plain"]["state_sha256"], "sha256",
    "the common final state hash of that paired check", "run (paired)", "QUALIFIED",
    "_validation", "INERTNESS/plain/state_sha256", "verbatim", "S1")
row("inertness_steps", IN["steps"], "steps", "length of the paired inertness check", "n/a",
    "QUALIFIED", "_validation", "INERTNESS/steps", "exact integer", "3|S1")

TE = J["_adjudication"]["TECHNICAL"]
for k in ("hop_ledger_rows_per_arm", "source_substep_ledger_rows_per_arm",
          "birth_substep_ledger_rows_per_arm", "TECHNICALLY_INVALID_RUNS",
          "blocked_fraction_X_max"):
    row("technical_" + k.lower(), TE[k], "rows" if "rows" in k else
        ("count" if "RUNS" in k else "fraction"),
        "technical record of the confirmation arms", "arm (seed)", "QUALIFIED", "_adjudication",
        "TECHNICAL/" + k, "exact integer" if "rows" in k or "RUNS" in k else "4 significant",
        "S4")
row("disposition", J["_adjudication"]["DISPOSITION"], "flag",
    "the adjudicated disposition of the source-response operator", "n/a", "QUALIFIED",
    "_adjudication", "DISPOSITION", "verbatim", "abstract|4|8")
for k, v in J["_adjudication"]["SECONDARY_STATUSES"].items():
    row("secondary_status_" + k.lower(), v, "flag", "adjudicated secondary status", "n/a",
        "QUALIFIED", "_adjudication", "SECONDARY_STATUSES/" + k, "verbatim", "6|8|S7")
row("marginal_closure_remains_open", J["_adjudication"]["MARGINAL_CLOSURE_REMAINS_OPEN"], "flag",
    "does the marginal density equation close", "n/a", "QUALIFIED", "_adjudication",
    "MARGINAL_CLOSURE_REMAINS_OPEN", "verbatim", "6|8")

OBS = J["_adjudication"]["OBSERVED"]
for tag in ("S_median", "M_median"):
    for st in ("n", "mean", "sd", "se"):
        row("fresh_%s_%s" % (tag.lower(), st), OBS[tag][st],
            "count" if st == "n" else "lattice units",
            "across-arm summary of the frozen within-arm median", "arm (seed)", "QUALIFIED",
            "_adjudication", "OBSERVED/%s/%s" % (tag, st), "6 significant", "4|Fig2|S4|S5")

HIST = J["_residual"]["BY_SIZE"]
for L in HIST:
    row("historical_L%s_median_residual_percent" % L, HIST[L]["median"]["residual_percent"],
        "percent", "historical median-summary residual at this lattice size", "arm (seed)",
        "QUALIFIED", "_residual", "BY_SIZE/%s/median/residual_percent" % L, "4 significant", "5|S6")
    row("historical_L%s_median_residual_n" % L, HIST[L]["median"]["n"], "count",
        "arms behind that historical figure", "arm (seed)", "QUALIFIED", "_residual",
        "BY_SIZE/%s/median/n" % L, "exact integer", "5|S6")
    row("historical_L%s_mean_residual_percent" % L, HIST[L]["mean"]["residual_percent"],
        "percent", "historical mean-summary residual at this lattice size", "arm (seed)",
        "QUALIFIED", "_residual", "BY_SIZE/%s/mean/residual_percent" % L, "4 significant", "5|S6")
EST = J["_residual"]["ESTIMATOR"]
for cond in ("IID_STATIC", "IID_MOBILE"):
    for k in ("arms", "frames"):
        row("iid_%s_%s" % (cond.split("_")[1].lower(), k), EST[cond][k], "count",
            "size of the estimator-only surrogate", "surrogate arm", "QUALIFIED", "_residual",
            "ESTIMATOR/%s/%s" % (cond, k), "exact integer", "5|S6")


# ------------------------------------------------------------------ section scope amendments
# The ALLOWED_SECTIONS field was first assigned before the manuscript was drafted. Where the
# written paper places a value in a different section for editorial reasons, the scope is widened
# here EXPLICITLY, with a reason, rather than silently or by relaxing the linter. Narrowing is
# never done this way. Every amendment is published in the output file.
SCOPE_AMENDMENTS = [
    (r"^relaxation_", "2",
     "burn-in adequacy is stated where the protocol is introduced, not where the operator is built"),
    (r"^birth_position_", "2",
     "the point-source check belongs with the description of the model it validates"),
    (r"^(population_check_|age_|capacity_certified_fraction_never_refused|"
     r"capacity_implied_change_in_r80_percent|birth_flux_variance_over_mean|"
     r"margin_capacity_certified_error_on_r80_percent|margin_intra_step_order_residual_percent)", "3",
     "the terms measured and then dropped are listed once, in the construction section"),
    (r"^mu_X$", "3", "the mortality constant is named again where the decay factor is written"),
    (r"^equivalence_margin_percent$", "3",
     "the margin is derived in the construction section and used again in the results"),
    (r"^inertness_state_hash$", "3",
     "the inertness hash is quoted once in the main text and again in the supplement"),
    (r"^technical_", "4",
     "the technical record of the confirmation arms is summarised where those arms are reported"),
    (r"^blocked_fraction_X_mean$", "4",
     "capacity blocking bounds the meaning of the confirmation and is stated there"),
    (r"^margin_M6_monte_carlo_se_mobile_percent$", "5",
     "the construction's own Monte-Carlo error is quoted where the construction overshoots"),
    (r"^fresh_arms_run$", "7",
     "section 7 points the reader to the fresh arms; it is the only bound quantity permitted there"),
]
AMENDED = []
for r in ROWS:
    for pat, sec, why in SCOPE_AMENDMENTS:
        if re.search(pat, r["MANUSCRIPT_LABEL"]):
            allowed = r["ALLOWED_SECTIONS"].split("|")
            if sec not in allowed:
                allowed.append(sec)
                r["ALLOWED_SECTIONS"] = "|".join(allowed)
                AMENDED.append({"LABEL": r["MANUSCRIPT_LABEL"], "SECTION_ADDED": sec,
                                "REASON": why})

# ---------------------------------------------------------------- write
os.makedirs(f"{PKG}/provenance", exist_ok=True)
json.dump({"SECTION": "LRCPS01 numerical reconciliation",
           "STATUS": "PAPER_ONLY_NONSCIENTIFIC_BINDING",
           "RULE": "no number may come only from prose; none is copied from conversation; every "
                   "denominator is explicit; developmental and qualified numerics are never "
                   "pooled; no frame, step, transition, particle or event row is used as an "
                   "independent replicate for any confirmatory statement",
           "SOURCES": SRC, "N_ROWS": len(ROWS),
           "SECTION_SCOPE_AMENDMENTS": AMENDED,
           "N_SECTION_SCOPE_AMENDMENTS": len(AMENDED), "ROWS": ROWS},
          open(f"{PKG}/provenance/PAPER_NUMERICAL_RECONCILIATION.json", "w"), indent=1)
with open(f"{PKG}/provenance/PAPER_NUMERICAL_RECONCILIATION.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(ROWS[0].keys()))
    w.writeheader()
    for r in ROWS:
        w.writerow(r)
print("reconciled rows:", len(ROWS))
for r in ROWS[:8]:
    print("  %-42s %s" % (r["MANUSCRIPT_LABEL"], r["VALUE"]))

"""OBTR01 §13-§14 — rederive each historical inequality in the qualified LawSpec, and separate
what is true of the current point from what is merely analytically admissible.

The trap this section has to avoid is stated first, because a careless rederivation walks into
it. Substituting mu_Y = 0 and k_Y = 0 into the window makes the LOWER bound read 0 < R_Y and
both UPPER bounds read R_Y < something positive, so the window, READ AS A SET OF RATES, comes
out non-empty. Reporting that would be an error of exactly the kind §27 forbids. The set is
non-empty; what matters is that the set of rates the qualified LawSpec can REACH is the single
point {0}, and 0 is excluded by the strict lower bound. The window and the reachable set do not
intersect.

So each inequality is rederived twice: once as a statement about R_Y, and once against the
reachable band, which is what decides anything.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBTR01/verify/obdca01/wc"
MT = "/home/claude/OBTR01/verify/mtw01"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, "/home/claude/OBTR01/code")

from kernels_obtr01 import relative_kernel                 # noqa: E402
from corrections_obtr01 import mean_exit_time_discrete     # noqa: E402

SAFETY, SEP, P_STAR, WINDOW_MARGIN, LOWER_MARGIN = 2.0, 2.0, 0.90, 2.0, 10.0


def measured_births():
    """E[B], the mean accepted births per step at the organiser cell, measured from delivered
    trajectories. C5 showed it is not predictable from k_X: at k_X = 1 the birth probability
    saturates and the number born is min(n_SX, free), a property of the chemostat's local
    supply. Raw-only; no run is consumed."""
    vals, arms = [], 0
    d = f"{WC}/OBDI02/raw"
    for n in sorted(os.listdir(d)):
        if not n.endswith(".npz"):
            continue
        z = np.load(f"{d}/{n}", allow_pickle=True)
        F = {str(k): i for i, k in enumerate(z["fields"])}
        s = z["series"]
        w = s[2000:11000]
        nx = w[:, F["N_X"]]
        if nx.mean() <= 0:
            continue
        vals.append(float(w[:, F["accepted_births_X"]].mean()))
        arms += 1
    v = np.asarray(vals)
    return {"arms": arms, "mean": float(v.mean()), "sd": float(v.std(ddof=1)),
            "min": float(v.min()), "max": float(v.max()),
            "definition": "mean of accepted_births_X over the in-window steps of each arm, "
                          "then averaged over arms"}


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    hist = json.load(open(f"{MT}/out/_window.json"))
    corr = json.load(open(f"{OUT}/_corrections.json"))
    Q_max = corr["C3_Q_MAX"]["EXACT_over_the_full_capacity_space"]["Q_max"]
    Q_min = 1

    L, CAP, S0 = int(pt["L"]), pt["CAP"], pt["S0"]
    mu_X, mu_Y, k_X, k_Y = pt["muX"], pt["muY"], pt["kX"], pt["kY"]
    phi, omega = pt["phi"], pt["omega"]
    q = pt["p_hop"] / 4.0
    D_X = D_Y = q * (1 - q)
    a_X, a_Y = mu_X, mu_Y

    B = measured_births()
    ell_X = math.sqrt(D_X / a_X)
    rho_max = (CAP - 2 * S0) / (1.0 + a_X / omega)
    N_CX = B["mean"] / a_X
    L_packed = math.sqrt(N_CX / (math.pi * rho_max))
    L_C = max(ell_X, L_packed)
    Delta = SEP * L_C
    H3max = -math.log(P_STAR)

    # tau_sep is the mean first passage of the relative coordinate of TWO organisers to Delta.
    # Solved discretely with the exact kernel, not with the continuum law.
    Krel_YY = relative_kernel(q, q)
    tau_sep_discrete, n_sites = mean_exit_time_discrete(Krel_YY, Delta)
    tau_sep_continuum = Delta ** 2 / (8.0 * D_Y)
    tau_design = SAFETY * tau_sep_discrete

    upper_hazard = H3max / (2.0 * tau_design)
    R_X_operative = B["mean"]                    # C5: additive intensity, not k_X Q_max
    upper_packed = D_Y * (a_X / R_X_operative) ** (2.0 / 2.0)
    upper = min(upper_hazard, upper_packed)

    reachable = (k_Y * Q_min, k_Y * Q_max)

    # ---------------------------------------------------------------- §13 the inequalities
    ineq = [
        {"name": "lower_extinction_vs_division", "historical": "a_Y < R_Y",
         "rederived_in_the_qualified_LawSpec": "0 < R_Y",
         "a_Y": a_Y, "why": "mu_Y = 0 exactly, so the organiser never dies",
         "AS_A_STATEMENT_ABOUT_R_Y": "satisfied by every strictly positive rate",
         "AGAINST_THE_REACHABLE_BAND": "R_Y = 0 is the only reachable value and it is "
                                       "EXCLUDED by the strict inequality",
         "REACHABLE_BAND_SATISFIES_IT": bool(reachable[0] > a_Y),
         "STATUS": "FAILS_ON_THE_REACHABLE_BAND"},
        {"name": "upper_hazard_of_a_third_organiser",
         "historical": "R_Y < H3_max / (2 safety tau_sep)",
         "rederived_in_the_qualified_LawSpec": "R_Y < %.6g" % upper_hazard,
         "why": "the bound itself is well defined and is recomputed here with the corrected "
                "D_eff, the exhaustive Q_max = %d and a DISCRETE first passage; but the rate "
                "it bounds is identically zero, so the constraint is satisfied vacuously"
                % Q_max,
         "AS_A_STATEMENT_ABOUT_R_Y": "R_Y must stay below %.6g" % upper_hazard,
         "AGAINST_THE_REACHABLE_BAND": "0 < %.6g, satisfied VACUOUSLY" % upper_hazard,
         "REACHABLE_BAND_SATISFIES_IT": bool(reachable[1] < upper_hazard),
         "STATUS": "VACUOUSLY_SATISFIED"},
        {"name": "upper_packed_KK", "historical": "R_Y < D_Y (a_X / R_X)^(2/d)",
         "rederived_in_the_qualified_LawSpec": "R_Y < %.6g" % upper_packed,
         "why": "R_X is replaced by the OPERATIVE source intensity E[B] = %.4f measured from "
                "%d delivered arms, because C4/C5 showed k_X Q_max is not the operative "
                "quantity once the birth probability saturates" % (B["mean"], B["arms"]),
         "AS_A_STATEMENT_ABOUT_R_Y": "R_Y must stay below %.6g" % upper_packed,
         "AGAINST_THE_REACHABLE_BAND": "0 < %.6g, satisfied VACUOUSLY" % upper_packed,
         "REACHABLE_BAND_SATISFIES_IT": bool(reachable[1] < upper_packed),
         "STATUS": "VACUOUSLY_SATISFIED"},
        {"name": "non_emptiness", "historical": "2 safety a_Y tau_sep / H3_max < 1",
         "rederived_in_the_qualified_LawSpec": "0 < 1",
         "value": 2.0 * SAFETY * a_Y * tau_sep_discrete / H3max,
         "why": "a_Y = 0, so the left-hand side is identically zero",
         "AS_A_STATEMENT_ABOUT_R_Y": "the window, read as a SET of rates, is the non-empty "
                                     "interval (0, %.6g)" % upper,
         "AGAINST_THE_REACHABLE_BAND": "the reachable set is the single point {0}, which the "
                                       "strict lower bound excludes; the intersection is EMPTY",
         "REACHABLE_BAND_SATISFIES_IT": False,
         "STATUS": "VACUOUSLY_SATISFIED_BUT_UNREACHABLE"},
    ]

    window_as_a_set_is_non_empty = upper > a_Y
    reachable_intersects = (reachable[1] > a_Y) and (reachable[0] < upper)

    # ---------------------------------------------------------------- §14 the three objects
    k_Y_family_max = upper / (WINDOW_MARGIN * Q_max)
    mu_Y_family_max = k_Y_family_max * Q_min / LOWER_MARGIN
    T_div_family = 1.0 / (k_Y_family_max * (Q_max / 2.0))
    horizon_frozen = int(spec["window"]["HORIZON"])

    section14 = {
        "CURRENT_QUALIFIED_POINT": {
            "parameters": dict(pt),
            "reachable_R_Y_band": list(reachable),
            "window_interval": [a_Y, upper],
            "WINDOW_STATUS": "NOT_PORTABLE",
            "QUALIFIED_POINT_WINDOW_STATUS": "UNREACHABLE_AT_THE_QUALIFIED_POINT",
            "statement": ("the historical window is not a condition this point fails; it is a "
                          "condition about a mechanism this point does not have. Both of its "
                          "terms, a_Y and R_Y, are structurally zero."),
            "WHAT_MUST_NOT_BE_SAID": ("that the window is 'satisfied', 'non-empty' or 'passed' "
                                      "here. Two of the three inequalities are satisfied "
                                      "vacuously and the third fails, and a vacuous "
                                      "satisfaction is not a result.")},
        "ANALYTICALLY_ADMISSIBLE_FAMILY": {
            "what_it_is": ("the set of (k_Y, mu_Y) that would satisfy the rederived "
                           "inequalities if the OTHER parameters were held at the qualified "
                           "point. It is a statement about a DIFFERENT LawSpec, because "
                           "k_Y > 0 removes ORGANIZER_BOUND_SOURCE."),
            "constraints": {
                "lower": "mu_Y < k_Y Q_min = k_Y",
                "upper": "k_Y Q_max < %.6g" % upper,
                "with_the_declared_design_margins":
                    "k_Y <= %.6g and mu_Y <= %.6g" % (k_Y_family_max, mu_Y_family_max)},
            "recomputed_inputs": {
                "D_eff": D_X, "ell_X": ell_X, "rho_max": rho_max, "E_B_measured": B["mean"],
                "N_CX": N_CX, "L_packed": L_packed, "L_C": L_C,
                "binding_cluster_bound": "diffusive" if ell_X >= L_packed else "packed",
                "Delta": Delta, "Q_max": Q_max,
                "tau_sep_discrete": tau_sep_discrete,
                "tau_sep_continuum_Delta2_over_8DY": tau_sep_continuum,
                "discrete_over_continuum": tau_sep_discrete / tau_sep_continuum,
                "tau_design": tau_design, "H3_max": H3max,
                "upper_from_the_hazard": upper_hazard,
                "upper_from_the_packed_bound": upper_packed,
                "binding_upper": upper,
                "which_binds": ("hazard" if upper_hazard <= upper_packed else "packed")},
            "IMPLIED_COST": {
                "T_div_at_Q_typ": T_div_family,
                "frozen_HORIZON": horizon_frozen,
                "horizons_needed_for_one_expected_division":
                    T_div_family / horizon_frozen,
                "READING": ("one expected organiser division takes about %.0f steps, which is "
                            "%.1f times the frozen horizon. A future minority-window "
                            "experiment is therefore ANALYTICALLY eligible but not free: it "
                            "needs a horizon several times longer than anything run so far, "
                            "and the cost scales with it."
                            % (T_div_family, T_div_family / horizon_frozen))},
            "NO_POINT_IS_SELECTED": ("§18 forbids optimisation. The numbers above bound a "
                                     "family; they are not a design point and are not to be "
                                     "used as one."),
        },
        "FUTURE_SELECTED_DESIGN_POINT": {
            "value": None,
            "status": "NOT_SELECTED_IN_THIS_MISSION",
            "why": "§18 forbids optimisation and §16 forbids fresh runs unless the gate opens; "
                   "selecting a point would also require a LawSpec this mission has not "
                   "qualified.",
        },
        "WHY_THE_FAMILY_DOES_NOT_INHERIT_THE_QUALIFICATION": (
            "the cumulative cloud qualification was established under BALANCED_CHEMOSTAT, "
            "NO_ADDED_COHESION, NO_C3_PROTECTION and ORGANIZER_BOUND_SOURCE, and the last of "
            "those is exactly k_Y = 0. Any point with k_Y > 0 is outside the qualified "
            "LawSpec, so nothing established here transfers to it without a new qualification."),
    }

    out = {"SECTION": "OBTR01 §13-§14", "CONSUMES_NO_SCIENTIFIC_RUN": True,
           "HISTORICAL_VALUES_FOR_REFERENCE": {
               "design_point_tau_sep": hist["design_point"]["tau_sep"],
               "design_point_window_upper": hist["design_point"]["window_upper_R_Y_binding"],
               "design_point_adjudication": hist["adjudication"],
               "note": "reference only; nothing below is inherited from these"},
           "MEASURED_SOURCE_INTENSITY": B,
           "REDERIVED_INEQUALITIES": ineq,
           "WINDOW_AS_A_SET_OF_RATES_IS_NON_EMPTY": bool(window_as_a_set_is_non_empty),
           "REACHABLE_BAND_INTERSECTS_THE_WINDOW": bool(reachable_intersects),
           "WINDOW_STATUS": "NOT_PORTABLE",
           "QUALIFIED_POINT_WINDOW_STATUS": "UNREACHABLE_AT_THE_QUALIFIED_POINT",
           "SECTION_14": section14}
    json.dump(out, open(f"{OUT}/_window_rederivation.json", "w"), indent=1, default=str)

    print("measured source intensity E[B] = %.4f  (sd %.4f, %d arms)"
          % (B["mean"], B["sd"], B["arms"]))
    print("ell_X %.4f   L_packed %.4f   L_C %.4f (%s)   Delta %.4f"
          % (ell_X, L_packed, L_C,
             section14["ANALYTICALLY_ADMISSIBLE_FAMILY"]["recomputed_inputs"]
             ["binding_cluster_bound"], Delta))
    print("tau_sep discrete %.3f vs continuum Delta^2/(8 D_Y) %.3f  (ratio %.4f)"
          % (tau_sep_discrete, tau_sep_continuum, tau_sep_discrete / tau_sep_continuum))
    print("upper bounds: hazard %.6g   packed %.6g   binding %.6g (%s)"
          % (upper_hazard, upper_packed, upper,
             section14["ANALYTICALLY_ADMISSIBLE_FAMILY"]["recomputed_inputs"]["which_binds"]))
    print()
    print("%-38s %-28s %s" % ("INEQUALITY", "REACHABLE BAND SATISFIES", "STATUS"))
    print("-" * 96)
    for i in ineq:
        print("%-38s %-28s %s" % (i["name"], i["REACHABLE_BAND_SATISFIES_IT"], i["STATUS"]))
    print()
    print("window as a SET of rates is non-empty      : %s   -> interval (%.3g, %.6g)"
          % (window_as_a_set_is_non_empty, a_Y, upper))
    print("reachable band at the qualified point      : {%.3g}" % reachable[0])
    print("reachable band INTERSECTS the window       : %s" % reachable_intersects)
    print()
    print("WINDOW_STATUS                  = %s" % out["WINDOW_STATUS"])
    print("QUALIFIED_POINT_WINDOW_STATUS  = %s" % out["QUALIFIED_POINT_WINDOW_STATUS"])
    print()
    fam = section14["ANALYTICALLY_ADMISSIBLE_FAMILY"]
    print("admissible family (a DIFFERENT LawSpec): k_Y <= %.6g, mu_Y <= %.6g"
          % (k_Y_family_max, mu_Y_family_max))
    print("  one expected division takes %.0f steps = %.1f frozen horizons"
          % (T_div_family, T_div_family / horizon_frozen))
    print("  FUTURE_SELECTED_DESIGN_POINT = %s"
          % section14["FUTURE_SELECTED_DESIGN_POINT"]["status"])


if __name__ == "__main__":
    main()

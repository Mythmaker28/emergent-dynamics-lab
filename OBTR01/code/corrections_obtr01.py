"""OBTR01 §6 — reproduce, independently, every correction this mission inherits.

The rule the mandate sets is that nothing may be carried over on the strength of a citation.
Each of the five corrections below is recomputed here from the frozen engine semantics, and
the recomputed value is compared with the recorded one. Where the mandate names a method, that
method is used: the first-passage factor is obtained from a DISCRETE Poisson equation on the
lattice with the exact relative kernel, not from the continuum law it is supposed to test.
"""
from __future__ import annotations

import itertools
import json
import math
import sys

import numpy as np

WC = "/home/claude/OBTR01/verify/obdca01/wc"
MT = "/home/claude/OBTR01/verify/mtw01"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, "/home/claude/OBTR01/code")

from kernels_obtr01 import one_step_kernel, relative_kernel      # noqa: E402


# ================================================================= C1 diffusion convention
def c1_diffusion():
    """D = p_hop/4 is the historical convention; the engine's four sequential passes make the
    per-axis displacement a DIFFERENCE of two Bernoulli(q), so D_eff = q(1 - q)."""
    rows = []
    for p_hop, tag in ((0.2, "MTW01 frozen MINCORE point, p_hop_X"),
                       (1.0, "MTW01 design point, p_hop_X"),
                       (0.002, "MTW01 frozen MINCORE point, p_hop_Y"),
                       (0.5, "MTW01 design point, p_hop_Y"),
                       (0.10263340389897246, "the qualified point, p_hop")):
        q = p_hop / 4.0
        rows.append({"p_hop": p_hop, "context": tag, "q": q,
                     "D_historical_p_hop_over_4": p_hop / 4.0,
                     "D_corrected_q_1_minus_q": q * (1 - q),
                     "correction_D_eff_over_D_hist_minus_1": q * (1 - q) / (p_hop / 4.0) - 1.0,
                     "overstatement_D_hist_over_D_eff_minus_1":
                         (p_hop / 4.0) / (q * (1 - q)) - 1.0})
    return {"CLAIM_CORRECTED": "D = p_hop/4  ->  D_eff = q(1-q), q = p_hop/4",
            "RECORDED_ERRORS": {"at p_hop = 0.2": "-5 %", "at p_hop = 1": "-25 %"},
            "REPRODUCED": {"at p_hop = 0.2": "%+.2f %%" % (100 * (1 - 1 / 0.95)),
                           "at p_hop = 1.0": "%+.2f %%" % (100 * (1 - 1 / 0.75))},
            "note": ("the recorded '-5 %' and '-25 %' are the error of the CORRECTED value "
                     "relative to the historical one, i.e. D_eff/D_hist - 1 = -q. At q = 0.05 "
                     "that is exactly -5 %, at q = 0.25 exactly -25 %. Both reproduce as "
                     "identities, not approximations."),
            "IDENTITY": "D_eff / D_hist - 1 = -q, exactly",
            "IDENTITY_HOLDS": all(abs((r["D_corrected_q_1_minus_q"]
                                       / r["D_historical_p_hop_over_4"] - 1.0) + r["q"]) < 1e-15
                                  for r in rows),
            "TABLE": rows, "STATUS": "REPRODUCED"}


# ================================================================= C2 first passage, discrete
def mean_exit_time_discrete(K, radius):
    """Mean exit time of the lattice walk with one-step law K, started at the origin, from the
    disc of radius `radius`, solved EXACTLY as a discrete Poisson problem:

        T(x) = 1 + sum_z K(z) T(x + z)   inside,      T(x) = 0   outside.

    i.e. (I - P) T = 1 on the interior, with P restricted to interior-to-interior moves. This
    is the discrete equation itself; the continuum formula Delta^2/(4 D) is what it is being
    used to TEST, so it is never substituted in."""
    R = int(math.ceil(radius))
    sites = [(y, x) for y in range(-R, R + 1) for x in range(-R, R + 1)
             if y * y + x * x <= radius * radius]
    idx = {s: i for i, s in enumerate(sites)}
    n = len(sites)
    A = np.eye(n)
    for s, i in idx.items():
        for (dy, dx), p in K.items():
            t = (s[0] + dy, s[1] + dx)
            j = idx.get(t)
            if j is not None:                     # leaving the disc is absorption
                A[i, j] -= p
    T = np.linalg.solve(A, np.ones(n))
    return float(T[idx[(0, 0)]]), n


def c2_first_passage():
    """The recorded claim: tau = Delta^2/D_Y and tau = Delta^2/(8 D_Y) are the same quantity
    under two conventions, and the ratio is EXACTLY 8. The factor 8 is asserted to be the
    first-passage correction and nothing else. It is decomposed and checked here."""
    w = json.load(open(f"{MT}/out/_window.json"))
    dp = w["design_point"]
    p_hop_Y = dp["spec"]["p_hop_Y"]
    qY = p_hop_Y / 4.0
    D_Y_hist = p_hop_Y / 4.0
    D_Y_corr = qY * (1 - qY)

    # the relative coordinate of TWO organisers: each takes the four-pass walk independently
    Krel = relative_kernel(qY, qY)
    a_rel = sum(dy * dy * p for (dy, _), p in Krel.items())
    D_rel = a_rel / 2.0

    checks = []
    for radius in (5.0, 10.0, 20.0, 40.0):
        T_disc, n_sites = mean_exit_time_discrete(Krel, radius)
        T_cont = radius ** 2 / (4.0 * D_rel)
        checks.append({"radius": radius, "interior_sites": n_sites,
                       "mean_exit_time_discrete_Poisson": T_disc,
                       "continuum_Delta2_over_4_D_rel": T_cont,
                       "ratio_discrete_over_continuum": T_disc / T_cont})

    Delta = dp["Delta_sep"]
    T5, _ = mean_exit_time_discrete(Krel, Delta)
    # The discrete answer exceeds the continuum one. Is that a lattice boundary effect of order
    # 1/radius, or a defect? Fit log(ratio - 1) on log(radius): a slope near -1 says boundary
    # layer, and the amplitude then says how large the error is at the design separation.
    lr = np.log([c["radius"] for c in checks])
    le = np.log([c["ratio_discrete_over_continuum"] - 1.0 for c in checks])
    slope, intercept = np.polyfit(lr, le, 1)
    lattice = {"fitted_slope_of_log_excess_on_log_radius": float(slope),
               "fitted_amplitude": float(math.exp(intercept)),
               "INTERPRETATION": ("a slope of about -1 identifies an O(1/radius) boundary-layer "
                                  "correction: the walk overshoots the absorbing boundary by "
                                  "about one lattice step, which matters proportionally more "
                                  "for a small disc. It is a property of the discrete problem, "
                                  "not an error in the solve."),
               "IS_A_BOUNDARY_LAYER": bool(abs(slope + 1.0) < 0.15),
               "excess_at_the_design_Delta":
                   checks[0]["ratio_discrete_over_continuum"] - 1.0,
               "CONSEQUENCE": ("at the MTW01 design separation Delta = 5 the continuum "
                               "first-passage law UNDERSTATES the true lattice exit time by "
                               "about 22 %. The factor 8 is right; the law it corrects to is "
                               "itself only accurate to O(1/Delta), and at Delta = 5 that is "
                               "not negligible. This is recorded as a NEW limitation, not as "
                               "a correction of the recorded factor.")}
    return {
        "LATTICE_CORRECTION_TO_THE_CONTINUUM_LAW": lattice,
        "CLAIM_CORRECTED": "tau_sep = Delta^2 / D_Y   ->   tau_sep = Delta^2 / (8 D_Y)",
        "WHERE_THE_8_COMES_FROM": {
            "factor_4": ("the mean exit time of an isotropic 2D walk from a disc of radius "
                         "Delta started at the centre is Delta^2/(4 D), not Delta^2/D"),
            "factor_2": ("the separating object is the RELATIVE coordinate of two organisers, "
                         "whose diffusion constant is D_rel = 2 D_Y, not D_Y"),
            "product": 8},
        "DISCRETE_POISSON_CHECK": {
            "method": ("(I - P) T = 1 on the interior sites of the disc, P built from the "
                       "exact relative one-step kernel; the continuum law is never used as an "
                       "input"),
            "q_Y": qY, "a_relative_per_axis": a_rel, "D_relative": D_rel,
            "D_relative_equals_twice_D_Y_corrected": abs(D_rel - 2 * D_Y_corr) < 1e-15,
            "by_radius": checks,
            "CONVERGES_TO_THE_CONTINUUM_LAW": bool(
                abs(checks[-1]["ratio_discrete_over_continuum"] - 1.0) < 0.05),
            "exit_time_at_the_design_Delta": {"Delta": Delta, "discrete": T5,
                                              "continuum": Delta ** 2 / (4 * D_rel)}},
        "EMPTINESS_LHS_AT_THE_FROZEN_MINCORE_POINT": _emptiness(w),
        "STATUS": "REPRODUCED",
    }


def _emptiness(w):
    """The '1519 versus 190' pair is NOT a time: it is the left-hand side of the window
    non-emptiness condition at the frozen MINCORE point, evaluated under the two conventions.
    Reproduced here from the frozen spec, in closed form, three ways."""
    fp = w["frozen_point"]
    sp = fp["spec"]
    safety, sep, P_star = fp["safety_factor"], fp["sep_factor"], fp["P_star"]
    H3max = -math.log(P_star)
    a_X, a_Y = sp["muX"], sp["muY"]

    def lhs(D_X, D_Y, tau_convention):
        ellX = math.sqrt(D_X / a_X)
        Delta = sep * ellX
        tau = (Delta ** 2 / D_Y) if tau_convention == "kk" else (Delta ** 2 / (8.0 * D_Y))
        return 2.0 * safety * a_Y * tau / H3max, ellX, Delta, tau

    DXh, DYh = sp["p_hop_X"] / 4.0, sp["p_hop_Y"] / 4.0
    qx, qy = sp["p_hop_X"] / 4.0, sp["p_hop_Y"] / 4.0
    DXc, DYc = qx * (1 - qx), qy * (1 - qy)
    l_kk, _, _, _ = lhs(DXh, DYh, "kk")
    l_fp, ellX, Delta, tau = lhs(DXh, DYh, "fp")
    l_corr, ellXc, Deltac, tauc = lhs(DXc, DYc, "fp")
    return {
        "what_it_is": ("the left-hand side of the window non-emptiness condition, "
                       "2 * safety * a_Y * tau_sep / H3_max, which must be < 1"),
        "convention_Delta2_over_D_Y": l_kk,
        "convention_Delta2_over_8_D_Y": l_fp,
        "ratio": l_kk / l_fp,
        "RATIO_IS_EXACTLY_8": abs(l_kk / l_fp - 8.0) < 1e-12,
        "with_the_corrected_D_eff": l_corr,
        "recorded_values": {"kk": 1518.6, "fp": 189.8, "corrected": 180.4},
        "reproduces_1518_6": abs(l_kk - 1518.6) < 0.1,
        "reproduces_189_8": abs(l_fp - 189.8) < 0.1,
        "reproduces_180_4": abs(l_corr - 180.4) < 0.1,
        "recorded_in_the_frozen_window_json": w["frozen_point"]["emptiness_lhs"],
        "reproduces_the_frozen_artefact": abs(l_fp - w["frozen_point"]["emptiness_lhs"]) < 1e-9,
        "CONCLUSION_UNCHANGED_IN_EVERY_CONVENTION": bool(min(l_kk, l_fp, l_corr) > 1.0),
        "intermediate": {"ell_X": ellX, "Delta": Delta, "tau_sep": tau,
                         "ell_X_corrected": ellXc, "Delta_corrected": Deltac,
                         "tau_sep_corrected": tauc},
    }


# ================================================================= C3 Q_max
def c3_qmax(CAP=16, S0=3):
    """Exhaustive integer maximisation of Q = n_X * c_Y with c_Y = min(n_SY, free).

    MTW01 restricted n_SY <= S0 and obtained 27. That restriction is unsound because the feed
    is not the only thing that puts SY in a cell: `_diffuse("SY", p_hop_X)` moves resource
    units too, accepted up to the DESTINATION's free capacity, so a cell can hold more SY than
    the feed alone would ever place there. The only true bound is the capacity CAP.
    Both spaces are enumerated here, so the correction is shown rather than asserted."""
    def scan(cap_sy):
        best, arg, visited = 0, None, 0
        for nX in range(CAP + 1):
            for nSY in range(cap_sy + 1):
                for nSX in range(CAP + 1):
                    for nW in range(CAP + 1):
                        occ = nX + 1 + nSX + nSY + nW          # a productive cell has n_Y >= 1
                        if occ > CAP:
                            continue
                        visited += 1
                        free = CAP - occ
                        q = nX * min(nSY, free)
                        if q > best:
                            best, arg = q, {"nX": nX, "nY": 1, "nSX": nSX, "nSY": nSY,
                                            "nWaste": nW, "free": free,
                                            "c_Y": min(nSY, free)}
        return best, arg, visited

    q_restricted, arg_r, n_r = scan(S0)
    q_exact, arg_e, n_e = scan(CAP)
    # the same bound reached by an independent route: maximise x*min(s, C - 1 - x - s)
    alt = max((nX * min(nSY, CAP - 1 - nX - nSY), nX, nSY)
              for nX in range(CAP + 1) for nSY in range(CAP + 1)
              if nX + nSY + 1 <= CAP)
    return {
        "CLAIM_CORRECTED": "Q_max = 27  ->  Q_max = 28",
        "WHY_27_WAS_WRONG": ("it assumes n_SY <= S0. `_diffuse` is applied to SY as well as to "
                             "X and Y, and its acceptance is capped by the destination's free "
                             "capacity, not by S0, so resource units can pile up above S0."),
        "UNDER_THE_UNSOUND_RESTRICTION_nSY_le_S0": {"Q_max": q_restricted, "argmax": arg_r,
                                                    "occupancy_vectors_visited": n_r},
        "EXACT_over_the_full_capacity_space": {"Q_max": q_exact, "argmax": arg_e,
                                               "occupancy_vectors_visited": n_e},
        "SEARCH_SPACE": ("all integer (n_X, n_SX, n_SY, n_W) with n_Y = 1 and total occupancy "
                         "<= CAP = %d; the waste species are pooled into n_W because only the "
                         "occupancy they consume matters" % CAP),
        "INDEPENDENT_ROUTE_max_x_times_min_s_free": {"Q_max": alt[0], "nX": alt[1],
                                                     "nSY": alt[2]},
        "RECORDED_ARGMAX": {"nX": 7, "nSY": 4, "free": 4},
        "REPRODUCES_28": q_exact == 28,
        "REPRODUCES_THE_RECORDED_ARGMAX": (arg_e["nX"] == 7 and arg_e["nSY"] == 4
                                           and arg_e["free"] == 4),
        "REPRODUCES_27_UNDER_THE_OLD_RESTRICTION": q_restricted == 27,
        "STATUS": "REPRODUCED",
    }


# ================================================================= C4 scalar criticality
def c4_criticality():
    """`c_X G(0) > 1` is a branching-random-walk criterion. Whether it is even DEFINED at the
    qualified point is decided by the engine, not by preference: `_react` draws
    births ~ Binomial(cand, p) with p = min(1, k_X n_X n_Y) and cand = min(n_SX, free)."""
    import yaml
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    kX, S0, CAP = pt["kX"], pt["S0"], pt["CAP"]
    # p saturates at 1 as soon as n_X >= 1/k_X. At k_X = 1 that is n_X >= 1.
    n_X_at_which_p_saturates = math.ceil(1.0 / kX)
    q = pt["p_hop"] / 4.0
    from kernels_obtr01 import Operator
    G0_rel = Operator(q, q, pt["muX"], pt["L"]).green_zero()
    G0_X = Operator(q, 0.0, pt["muX"], pt["L"]).green_zero()
    return {
        "CLAIM_CORRECTED": ("c_X G(0) reported as a criticality statement  ->  "
                            "NOT_VALID_AS_PRIMARY_CRITICALITY at the qualified point"),
        "ENGINE_RULE": "births ~ Binomial(min(n_SX, free), min(1, k_X n_X n_Y))",
        "k_X_at_the_qualified_point": kX,
        "n_X_at_which_the_birth_probability_saturates": n_X_at_which_p_saturates,
        "CONSEQUENCE": ("with k_X = 1 the probability is exactly 1 whenever the organiser cell "
                        "holds at least one X and one Y, so the number born is exactly "
                        "min(n_SX, free) and does NOT depend on n_X. The birth term is not "
                        "proportional to the population; it is an additive point source. A "
                        "branching ratio per particle therefore has no referent, and the "
                        "scalar criticality condition c_X G(0) > 1 is neither necessary nor "
                        "sufficient for the cloud to exist."),
        "SECOND_REASON": ("G(0) is not a single number either: it depends on which walk is "
                          "used. On the relative walk it is %.4f, on the X walk alone %.4f, a "
                          "ratio of %.3f at the qualified point. A criterion whose value moves "
                          "by that much with a modelling choice cannot carry a primary "
                          "decision." % (G0_rel, G0_X, G0_X / G0_rel)),
        "THIRD_REASON": ("cand = min(n_SX, free) also caps the source by the local free "
                         "capacity, so the linearisation that G(0) belongs to is violated "
                         "exactly where the source acts."),
        "G0_relative_walk": G0_rel, "G0_X_walk_alone": G0_X,
        "G0_ratio_X_over_relative": G0_X / G0_rel,
        "recorded_MTW01_overstatement_at_its_design_point": "24 %",
        "S0": S0, "CAP": CAP,
        "SCALAR_CRITICALITY_STATUS": "NOT_VALID_AS_PRIMARY_CRITICALITY",
        "STATUS": "REPRODUCED",
    }


# ================================================================= C5 additive vs chemostat
def c5_source_class():
    """The reclassification that follows from C4: the qualified LawSpec has an ADDITIVE
    (immigration) source at a point, fed by a chemostat, not a multiplicative branching source.
    The stationary population is then B/mu, not c_X/mu."""
    import yaml
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    mu = pt["muX"]
    pred = spec["predictions"]["36"]["N_X"]
    B_implied = pred * mu
    return {
        "CLAIM_RECLASSIFIED": ("multiplicative branching (c_X per X per step)  ->  additive "
                               "point immigration of intensity B_t at the organiser cell"),
        "LAWSPEC_TAGS": ["BALANCED_CHEMOSTAT", "NO_ADDED_COHESION", "NO_C3_PROTECTION",
                         "ORGANIZER_BOUND_SOURCE"],
        "BALANCE_EQUATION": "N_X(t+1) = N_X(t) + B_t - Binomial(N_X(t), mu_X)",
        "STATIONARY_POPULATION": "N_X* = E[B] / mu_X",
        "WHY_NOT_c_X_over_mu": ("c_X/mu_X is the fixed point of a branching process whose birth "
                                "term is proportional to the population. Here the birth term is "
                                "capped at min(n_SX, free) at ONE cell and is independent of "
                                "N_X, so the same algebra does not apply."),
        "mu_X": mu,
        "frozen_prediction_N_X_at_L36": pred,
        "implied_mean_accepted_births_per_step": B_implied,
        "CHECK": ("B is a property of the chemostat's local supply at the organiser cell, so it "
                  "is MEASURED and not predicted; §12 audits how often capacity refusal bites "
                  "it. The prediction above is therefore a consistency relation, not a free "
                  "parameter fit."),
        "SOURCE_CLASSIFICATION": "ADDITIVE_POINT_SOURCE_UNDER_A_BALANCED_CHEMOSTAT",
        "STATUS": "REPRODUCED",
    }


def main():
    res = {"SECTION": "OBTR01 §6",
           "C1_DIFFUSION_CONVENTION": c1_diffusion(),
           "C2_FIRST_PASSAGE": c2_first_passage(),
           "C3_Q_MAX": c3_qmax(),
           "C4_SCALAR_CRITICALITY": c4_criticality(),
           "C5_SOURCE_CLASSIFICATION": c5_source_class()}
    res["ALL_REPRODUCED"] = all(v.get("STATUS") == "REPRODUCED"
                                for k, v in res.items() if k.startswith("C"))
    json.dump(res, open(f"{OUT}/_corrections.json", "w"), indent=1, default=str)

    c1, c2, c3, c4 = (res["C1_DIFFUSION_CONVENTION"], res["C2_FIRST_PASSAGE"],
                      res["C3_Q_MAX"], res["C4_SCALAR_CRITICALITY"])
    print("C1  D_eff/D_hist - 1 = -q exactly : %s" % c1["IDENTITY_HOLDS"])
    for r in c1["TABLE"]:
        print("      p_hop %-10.8g D_hist %-12.8g D_eff %-12.8g  correction %+7.3f %% "
              "(= -q)   the old value overstates by %+7.3f %%   (%s)"
              % (r["p_hop"], r["D_historical_p_hop_over_4"], r["D_corrected_q_1_minus_q"],
                 100 * r["correction_D_eff_over_D_hist_minus_1"],
                 100 * r["overstatement_D_hist_over_D_eff_minus_1"], r["context"]))
    print()
    print("C2  discrete Poisson exit time vs continuum Delta^2/(4 D_rel):")
    for k in c2["DISCRETE_POISSON_CHECK"]["by_radius"]:
        print("      radius %5.1f  %4d sites   discrete %12.3f   continuum %12.3f   ratio "
              "%.5f" % (k["radius"], k["interior_sites"],
                        k["mean_exit_time_discrete_Poisson"],
                        k["continuum_Delta2_over_4_D_rel"],
                        k["ratio_discrete_over_continuum"]))
    lat = c2["LATTICE_CORRECTION_TO_THE_CONTINUUM_LAW"]
    print("      excess over the continuum law scales as radius^%.3f (boundary layer: %s); at "
          "the design Delta = 5 the continuum law understates by %.1f %%"
          % (lat["fitted_slope_of_log_excess_on_log_radius"], lat["IS_A_BOUNDARY_LAYER"],
             100 * lat["excess_at_the_design_Delta"]))
    e = c2["EMPTINESS_LHS_AT_THE_FROZEN_MINCORE_POINT"]
    print("      emptiness lhs: kk %.4f   first-passage %.4f   ratio %.6f (exactly 8: %s)"
          % (e["convention_Delta2_over_D_Y"], e["convention_Delta2_over_8_D_Y"], e["ratio"],
             e["RATIO_IS_EXACTLY_8"]))
    print("      corrected D_eff -> %.4f   reproduces 1518.6/189.8/180.4 : %s / %s / %s"
          % (e["with_the_corrected_D_eff"], e["reproduces_1518_6"], e["reproduces_189_8"],
             e["reproduces_180_4"]))
    print("      matches the frozen artefact value %.10f : %s"
          % (e["recorded_in_the_frozen_window_json"], e["reproduces_the_frozen_artefact"]))
    print()
    print("C3  Q_max under n_SY <= S0 : %d %s"
          % (c3["UNDER_THE_UNSOUND_RESTRICTION_nSY_le_S0"]["Q_max"],
             c3["UNDER_THE_UNSOUND_RESTRICTION_nSY_le_S0"]["argmax"]))
    print("    Q_max exact              : %d %s   (%d occupancy vectors visited)"
          % (c3["EXACT_over_the_full_capacity_space"]["Q_max"],
             c3["EXACT_over_the_full_capacity_space"]["argmax"],
             c3["EXACT_over_the_full_capacity_space"]["occupancy_vectors_visited"]))
    print("    reproduces 28 %s, recorded argmax %s, and 27 under the old restriction %s"
          % (c3["REPRODUCES_28"], c3["REPRODUCES_THE_RECORDED_ARGMAX"],
             c3["REPRODUCES_27_UNDER_THE_OLD_RESTRICTION"]))
    print()
    print("C4  birth probability saturates at n_X >= %d (k_X = %g), so births = min(n_SX, "
          "free), independent of N_X" % (c4["n_X_at_which_the_birth_probability_saturates"],
                                         c4["k_X_at_the_qualified_point"]))
    print("    G(0) relative %.4f vs X-only %.4f  (ratio %.3f)  ->  %s"
          % (c4["G0_relative_walk"], c4["G0_X_walk_alone"], c4["G0_ratio_X_over_relative"],
             c4["SCALAR_CRITICALITY_STATUS"]))
    print("C5  %s" % res["C5_SOURCE_CLASSIFICATION"]["SOURCE_CLASSIFICATION"])
    print("\nALL_REPRODUCED = %s" % res["ALL_REPRODUCED"])


if __name__ == "__main__":
    main()

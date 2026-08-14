"""Post-run analysis of the block-1 stop. PURE ALGEBRA plus arithmetic on the four recorded
arms. No world is constructed, nothing is advanced, no start is consumed.

Two kinds of statement are produced and they are labelled separately:

  DERIVED_FROM_SOURCE   an exact consequence of the frozen rate semantics, true whether or not
                        any run had happened.
  OUTCOME_INFORMED      anything that uses a number measured in the four arms. Nothing in this
                        class may be used to select a parameter inside this mission.
"""
from __future__ import annotations

import json
import math

BASE = "/home/claude/MTW01"
S0, CAP, phi, omega = 3, 16, 0.05, 0.05


def G0(p_hop_X, D_X, ell_X):
    """Expected number of steps a body molecule spends in the cell where it was created,
    including diffusive returns, in a 2D lattice walk with decay.

      residence   the engine applies four independent direction attempts per step, each with
                  probability p_hop/4, so the probability of staying put for a whole step is
                  (1 - p_hop/4)^4 and the residence is its geometric mean life.
      returns     the standard two-dimensional lattice Green's function with decay,
                  ln(1 + ell_X^2)/(4*pi*D_X).
    """
    q_stay = (1.0 - p_hop_X / 4.0) ** 4
    residence = 1.0 / (1.0 - q_stay)
    returns = math.log(1.0 + ell_X ** 2) / (4.0 * math.pi * D_X)
    return residence + returns, residence, returns


def fixed_point(c_X, g0, muX):
    """Self-consistency of the body cloud around ONE organiser.

      production per step   S = c_X * P(at least one body molecule in the organiser's cell)
      occupancy there       u = S * G(0)
      Poisson closure       P(>=1) = 1 - exp(-u)
      =>                    u = c_X * G(0) * (1 - exp(-u))

    A positive root exists if and only if c_X*G(0) > 1. That is the self-maintenance condition.
    """
    a = c_X * g0
    if a <= 1.0:
        return {"c_X_G0": a, "supercritical": False, "u": 0.0, "S": 0.0, "N_X": 0.0}
    u = a
    for _ in range(200):                       # fixed-point iteration, monotone and contracting
        u = a * (1.0 - math.exp(-u))
    S = u / g0
    return {"c_X_G0": a, "supercritical": True, "u": u, "S": S, "N_X": S / muX}


def analyse(tag, sp, c_X):
    D_X = sp["p_hop_X"] / 4.0
    ell_X = math.sqrt(D_X / sp["muX"])
    g0, res, ret = G0(sp["p_hop_X"], D_X, ell_X)
    fp = fixed_point(c_X, g0, sp["muX"])
    hard_cap = S0 / sp["muX"]                  # cand_X <= S0, so production <= S0 per step
    return {"tag": tag, "spec": sp, "D_X": D_X, "ell_X": ell_X,
            "G0": g0, "G0_residence": res, "G0_returns": ret, "c_X_assumed": c_X,
            "fixed_point": fp,
            "N_X_hard_cap_per_organiser": hard_cap,
            "N_X_predicted": min(fp["N_X"], hard_cap)}


if __name__ == "__main__":
    blocks = json.load(open(BASE + "/out/_blocks.json"))
    arms = blocks["blocks"][0]["arms"]

    DESIGN = {"p_hop_X": 1.0, "p_hop_Y": 0.5, "muX": 0.04, "muY": 1.9511206603301160e-06,
              "kX": 1.0, "kY": 1.9511206603301162e-05}
    FROZEN = {"p_hop_X": 0.20, "p_hop_Y": 0.002, "muX": 0.005, "muY": 0.0005,
              "kX": 0.02, "kY": 0.0008}

    # c_X is the sustainable candidate count in the organiser's own cell. Two closed-form
    # brackets, both DERIVED_FROM_SOURCE:
    #   upper  c_X <= S0 = 3, the hard cap from cand = min(n[SX], free) and n[SX] <= S0
    #   lower  a stationary organiser depletes its cell and can only draw the local feed,
    #          phi*S0 = 0.15 per step
    # A mobile organiser sits between the two. Both brackets are evaluated.
    res = {"labels": {
        "DERIVED_FROM_SOURCE": "exact consequence of the frozen rate semantics",
        "OUTCOME_INFORMED": "uses a number measured in the four arms; may not select a "
                            "parameter inside this mission"}}
    res["design_c_X_upper"] = analyse("MTW01 design, c_X = S0 = 3", DESIGN, 3.0)
    res["design_c_X_lower"] = analyse("MTW01 design, c_X = phi*S0 = 0.15", DESIGN, phi * S0)
    res["frozen_c_X_upper"] = analyse("MINCORE frozen, c_X = S0 = 3", FROZEN, 3.0)
    res["frozen_c_X_lower"] = analyse("MINCORE frozen, c_X = phi*S0 = 0.15", FROZEN, phi * S0)

    # ---- what the four arms actually recorded (OUTCOME_INFORMED)
    obs = []
    for a in arms:
        g = a["gate"] or {}
        obs.append({"seed": a["seed"], "outcome": a["outcome"], "steps": a["steps_used"],
                    "N_X_at_gate": g.get("N_X"), "Q_at_gate": g.get("Q_mean_over_window"),
                    "Rg_at_gate": g.get("Rg_X_about_organiser"),
                    "Q_time_average_over_the_run": a["Q_trace_mean"],
                    "Q_max_over_the_run": a["Q_trace_max"],
                    "N_X_at_end": a["N_X_at_end"], "N_Y_at_end": a["N_Y_at_end"],
                    "H3_exact": a["H3_exact"]})
    res["observed"] = obs
    res["observed_summary"] = {
        "arms": len(obs),
        "arms_whose_body_cloud_never_established": sum(
            1 for o in obs if (o["N_X_at_gate"] or 0) < 10),
        "arms_whose_body_cloud_established_then_collapsed": sum(
            1 for o in obs if (o["N_X_at_gate"] or 0) >= 10 and o["N_X_at_end"] == 0),
        "arms_in_which_a_second_organiser_appeared": sum(
            1 for o in obs if o["H3_exact"] > 0.0),
        "total_H3_accumulated_across_all_arms": sum(o["H3_exact"] for o in obs)}

    # ---- the missing inequality, stated in closed form
    muX = DESIGN["muX"]
    res["missing_condition"] = {
        "label": "DERIVED_FROM_SOURCE",
        "statement": "cand_X = min(n[SX], free) and n[SX] <= S0, so ONE organiser cell can "
                     "convert at most S0 resource units per step. The body cloud it maintains "
                     "therefore obeys the exact bound N_X <= S0/muX, and N_X = 0 is an "
                     "absorbing state because every birth probability carries the factor nX*nY.",
        "N_X_hard_cap_at_the_design_point": S0 / muX,
        "N_X_hard_cap_at_the_frozen_MINCORE_point": S0 / FROZEN["muX"],
        "consequence": "a body cloud of a few tens of molecules around a single organiser is a "
                       "small population next to an absorbing state. Neither Kamimura and "
                       "Kaneko, whose molecules are conserved and held by an attractive "
                       "potential, nor the MTW01 preplan, which gated the cloud only at one "
                       "instant, contains this condition.",
        "required_form_of_the_missing_gate":
            "muX <= S0/N_ROBUST for a declared robust cloud size N_ROBUST, evaluated jointly "
            "with ell_X = sqrt(D_X/muX) and with the two Kamimura-Kaneko timescale inequalities"}

    # ---- is the three-condition region non-empty? closed form, no run
    feas = []
    for N_ROBUST in (100, 300, 1000):
        muX_r = S0 / N_ROBUST
        for ell in (2.5, 3.0):
            D_Xr = muX_r * ell ** 2
            p_hop = 4 * D_Xr
            if p_hop > 1.0:
                feas.append({"N_ROBUST": N_ROBUST, "ell_X": ell, "feasible": False,
                             "reason": "p_hop_X = %.3f exceeds 1" % p_hop})
                continue
            g0r, _, _ = G0(p_hop, D_Xr, ell)
            fp_lo = fixed_point(phi * S0, g0r, muX_r)
            D_Yr = D_Xr / 2.0
            tau = ell ** 2 / (2.0 * D_Yr)
            upper = (-math.log(0.90)) / (2.0 * 2.0 * tau)
            kY_r = upper / (2.0 * 27.0)
            feas.append({
                "N_ROBUST": N_ROBUST, "ell_X": ell, "muX": muX_r, "D_X": D_Xr,
                "p_hop_X": p_hop, "G0": g0r,
                "self_maintenance_c_X_G0_at_the_pessimistic_c_X": fp_lo["c_X_G0"],
                "supercritical_even_at_the_pessimistic_c_X": fp_lo["supercritical"],
                "N_X_at_that_fixed_point": min(fp_lo["N_X"], S0 / muX_r),
                "D_Y": D_Yr, "tau_sep": tau, "window_upper_R_Y": upper, "k_Y": kY_r,
                "T_div_at_Q_7": 1.0 / (kY_r * 7.0),
                "feasible": bool(fp_lo["supercritical"] and p_hop <= 1.0)})
    res["feasibility_scan"] = {
        "label": "DERIVED_FROM_SOURCE for the inequalities; the choice of which point to test "
                 "next would be OUTCOME_INFORMED and is NOT made here",
        "rows": feas,
        "region_non_empty": any(r.get("feasible") for r in feas)}

    json.dump(res, open(BASE + "/out/_postmortem.json", "w"), indent=1)

    print("== self-maintenance and cloud size ==")
    for k in ("design_c_X_upper", "design_c_X_lower", "frozen_c_X_upper", "frozen_c_X_lower"):
        r = res[k]
        print(" %-38s G0=%6.3f  c_X*G0=%8.3f  supercrit=%-5s  N_X*=%8.1f  cap=%8.1f"
              % (r["tag"], r["G0"], r["fixed_point"]["c_X_G0"],
                 r["fixed_point"]["supercritical"], r["fixed_point"]["N_X"],
                 r["N_X_hard_cap_per_organiser"]))
    print("\n== what the four arms recorded ==")
    for o in obs:
        print(" seed %-4d %-32s N_X(gate)=%-5s Q(gate)=%-6s Q(time-avg)=%-8s N_X(end)=%-4s H3=%.3g"
              % (o["seed"], o["outcome"][:32], o["N_X_at_gate"], o["Q_at_gate"],
                 (("%.4f" % o["Q_time_average_over_the_run"])
                  if o["Q_time_average_over_the_run"] is not None else "n/a"),
                 o["N_X_at_end"], o["H3_exact"]))
    print("\n total H3 accumulated across all four arms =",
          res["observed_summary"]["total_H3_accumulated_across_all_arms"])
    print("\n== feasibility of the three conditions together ==")
    for r in feas:
        if "muX" in r:
            print(" N_ROBUST=%-5d ell_X=%.1f  p_hop_X=%.4f  c_X*G0=%7.2f  N_X*=%7.1f  "
                  "tau_sep=%7.1f  k_Y=%.4g  T_div(Q=7)=%9.0f  feasible=%s"
                  % (r["N_ROBUST"], r["ell_X"], r["p_hop_X"],
                     r["self_maintenance_c_X_G0_at_the_pessimistic_c_X"],
                     r["N_X_at_that_fixed_point"], r["tau_sep"], r["k_Y"],
                     r["T_div_at_Q_7"], r["feasible"]))
        else:
            print(" N_ROBUST=%-5d ell_X=%.1f  INFEASIBLE: %s"
                  % (r["N_ROBUST"], r["ell_X"], r["reason"]))
    print("\n region non-empty =", res["feasibility_scan"]["region_non_empty"])

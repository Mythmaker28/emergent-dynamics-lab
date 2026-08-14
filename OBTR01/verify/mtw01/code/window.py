"""MINCORE-TIMESCALE-WINDOW-01 — analytic adjudication of the minority timescale window.

PURE ALGEBRA. This module imports no engine, constructs no World, advances nothing and draws no
random number. Every number it prints is a closed-form evaluation of the rate semantics read
directly from MINCORE/code/mincore.py (sha256 f5ecd405...c385af1). It runs BEFORE any start of
the mission and its result decides whether any start happens at all.

EXACT RATE SEMANTICS, read from the frozen source
-------------------------------------------------
_react(), per cell, per step, nX and nY the counts in that cell:
    p_s    = min(1, k_s * nX * nY)                       s in {X, Y}
    cand_s = min(n[res_s], max(free, 0))                 res_X = SX, res_Y = SY
    free   = CAP - sum over (X,Y,SX,SY,WX,WY)
    births_s ~ Binomial(cand_s, p_s)
    The reaction turns one resource unit into one product unit, so occupancy is invariant under
    _react and `free` is identical for the X and the Y sub-step.
_decay():   d_s ~ Binomial(n[s], mu_s).
_diffuse(s, p_hop): four directions per step, movers ~ Binomial(n, p_hop/4), accepted =
    min(movers, dest_free). Unconstrained mean square displacement is p_hop per step, so
    D_s = p_hop/4 in the convention <r^2> = 4*D*t.
_feed_and_outflow(): SX and SY each get Binomial(min(S0 - n, free), phi); WX and WY lose
    Binomial(n, omega). No X and no Y is ever fed.

DERIVED QUANTITIES USED BELOW
    a_X = muX,  a_Y = muY                       per particle per step
    R_Y = k_Y * nX* * c_Y = k_Y * Q             per organiser, Q = nX* * c_Y
    R_X = k_X * nX* * c_X, capped by cand and by resource supply
    D_X = p_hop_X/4,  D_Y = p_hop_Y/4
"""
from __future__ import annotations

import json
import math

# ---------------------------------------------------------------- Kamimura & Kaneko, verbatim
KK = {
    "reference": "Kamimura & Kaneko, PRL 105, 268103 (2010); arXiv:1005.1142v1",
    "reactions": ["X + Y -(p*gamma_X)-> 2X + Y", "X + Y -(p*gamma_Y)-> 2Y + X",
                  "X -(a_X)-> 0", "Y -(a_Y)-> 0"],
    "definitions": ["r_X = p*gamma_X", "r_Y = p*gamma_Y", "R_Y = r_Y * nbar_X",
                    "gamma_X = 1 - gamma_Y >= gamma_Y, so Y is the minority species"],
    "lower_boundary_extinction_vs_division": "a_Y < R_Y",
    "upper_boundary_division_vs_explosion_3D": "R_Y = D_Y * (a_X/R_X)^(2/3)",
    "cluster_size_3D": "L_C ~ N_CX^(1/3)",
    "separation_time": "tau_D = L_C^2 / D_Y   (equivalently L_C^2 ~ D_Y * tau_D)",
    "single_diffusion_constant": "KK sets D = 1 for EVERY species; the minority character of Y "
                                 "is carried by gamma_Y, not by a reduced mobility.",
    "generalisation_to_dimension_d":
        "The 3D boundary is R_Y = D_Y/L_C^2 with L_C = N_CX^(1/3) and N_CX = R_X/a_X. In "
        "dimension d the same packing argument gives L_C = N_CX^(1/d), hence "
        "R_Y < D_Y * (a_X/R_X)^(2/d); for d = 2 the exponent is 1.",
}


# ---------------------------------------------------------------- hard capacity bound on Q
def q_bounds(CAP, S0):
    """Exact integer maximisation of Q = nX * c_Y over EVERY occupancy vector the engine allows.
    c_Y = min(nSY, free), free = CAP - occ, and nSY <= S0 because nothing but the feed creates
    SY and the feed stops at S0. Exhaustive, no approximation."""
    best, arg = 0, None
    for nX in range(CAP + 1):
        for nSY in range(S0 + 1):
            for nSX in range(CAP + 1):
                for nW in range(CAP + 1):
                    occ = nX + 1 + nSX + nSY + nW          # a productive cell has nY >= 1
                    if occ > CAP:
                        continue
                    q = nX * min(nSY, CAP - occ)
                    if q > best:
                        best, arg = q, {"nX": nX, "nY": 1, "nSX": nSX, "nSY": nSY,
                                        "nWaste": nW, "free": CAP - occ,
                                        "c_Y": min(nSY, CAP - occ)}
    return best, arg


# ---------------------------------------------------------------- cluster size, both bounds
def cluster_size(D_X, a_X, kX, Q_max, S0, phi, CAP, omega, d=2):
    """L_C is the larger of two lower bounds, because both must hold.

    DIFFUSIVE. MINCORE has no cohesive interaction, so the body cloud around one organiser is a
    diffusion-decay cloud of size ell_X = sqrt(D_X/a_X). This bound does not depend on any rate
    constant of the reaction.

    PACKED (the KK bound). N_CX = R_X/a_X body molecules cannot occupy fewer than N_CX/rho_max
    sites, so a disc holding them has radius sqrt(N_CX/(pi*rho_max)).

    R_X is capped twice: kinetically by k_X*Q_max, and by resource supply. A point sink in a
    field that relaxes to S0 at rate phi has screening length ell_S = sqrt(D_X/phi) and can draw
    at most 2*pi*D_X*S0/ln(1 + ell_S/a) units per step with a = 1 lattice site.
    rho_max is the largest sustainable X density: CAP minus the two resources, divided by
    (1 + a_X/omega) because each X carries its own steady-state waste."""
    ell_X = math.sqrt(D_X / a_X)
    ell_S = math.sqrt(D_X / phi)
    R_X_resource = 2.0 * math.pi * D_X * S0 / math.log(1.0 + ell_S)
    R_X_kinetic = kX * Q_max
    R_X = min(R_X_kinetic, R_X_resource)
    N_CX = R_X / a_X
    rho_max = (CAP - 2 * S0) / (1.0 + a_X / omega)
    L_packed = math.sqrt(N_CX / (math.pi * rho_max))
    return {"ell_X": ell_X, "ell_S": ell_S, "R_X_kinetic_cap": R_X_kinetic,
            "R_X_resource_cap": R_X_resource, "R_X": R_X, "N_CX": N_CX, "rho_max": rho_max,
            "L_packed": L_packed, "L_C": max(ell_X, L_packed),
            "binding": "diffusive" if ell_X >= L_packed else "packed"}


# ---------------------------------------------------------------- the window
def window(sp, d=2, sep_factor=2.0, safety=2.0, P_star=0.90, Q_max=27, Q_min=1, Q_typ=15):
    D_X, D_Y = sp["p_hop_X"] / 4.0, sp["p_hop_Y"] / 4.0
    a_X, a_Y = sp["muX"], sp["muY"]
    cs = cluster_size(D_X, a_X, sp["kX"], Q_max, sp["S0"], sp["phi"], sp["CAP"], sp["omega"], d)
    L_C = cs["L_C"]

    Delta = sep_factor * L_C                       # separation criterion, sites
    # KK writes tau_D = L_C^2/D_Y as a SCALING form. The exact quantity is the mean first
    # passage of the RELATIVE coordinate of two walkers, which has diffusion constant
    # D_rel = 2*D_Y, from separation 0 to separation Delta. In two dimensions the mean exit
    # time from a disc of radius Delta starting at the centre is Delta^2/(4*D_rel), so
    #       tau_sep = Delta^2 / (8*D_Y).
    # Using the KK convention instead would overstate tau_sep by a factor 8 at Delta = 2*L_C,
    # which would place the design point far inside the window, make every control block
    # indecisive and make every run eight times longer. Both are reported.
    tau_sep = Delta ** 2 / (8.0 * D_Y)
    tau_sep_kk_convention = L_C ** 2 / D_Y
    tau_design = safety * tau_sep

    # Cumulative hazard of a THIRD organiser while the two existing ones move apart.
    #   H3(tau) = INT_0^tau [lambda_Y1(t) + lambda_Y2(t)] dt,  lambda_Yi = k_Y * nX*_i * c_Y,i
    #   births conditionally Poisson given the rates  =>  P(no third) = exp(-H3)
    # Requiring P >= P_star gives H3 <= -ln P_star and, at the constant worst-case rate R_Y,
    #   R_Y <= -ln(P_star) / (2 * tau)
    H3_max = -math.log(P_star)
    upper_diff = H3_max / (2.0 * tau_design)

    # KK packed form, as a cross-check on the same worst case
    upper_pack = D_Y * (a_X / cs["R_X"]) ** (2.0 / d)

    R_Y_min, R_Y_max, R_Y_typ = sp["kY"] * Q_min, sp["kY"] * Q_max, sp["kY"] * Q_typ

    # emptiness condition, obtained by substituting Delta = sep*L_C and, when the diffusive
    # bound binds, L_C = sqrt(D_X/a_X):
    #   (2*safety*sep^2 / -ln P*) * (a_Y/a_X) * (D_X/D_Y)  <  1
    coef = 2.0 * safety * sep_factor ** 2 / (8.0 * H3_max)
    lhs = coef * (a_Y / a_X) * (D_X / D_Y)

    # coherence: how far the organiser wanders in one body-molecule lifetime, in cloud radii
    chi = math.sqrt(4.0 * D_Y / a_X) / cs["ell_X"]

    out = {"spec": sp, "d": d, "D_X": D_X, "D_Y": D_Y, "a_X": a_X, "a_Y": a_Y,
           "sep_factor": sep_factor, "safety_factor": safety, "P_star": P_star,
           "cluster": cs, "Delta_sep": Delta, "tau_sep": tau_sep,
           "tau_sep_kk_convention": tau_sep_kk_convention, "tau_sep_design": tau_design,
           "H3_max": H3_max,
           "window_lower_R_Y": a_Y, "window_upper_R_Y_diffusive": upper_diff,
           "window_upper_R_Y_KK_packed": upper_pack,
           "window_upper_R_Y_binding": min(upper_diff, upper_pack),
           "window_ratio": min(upper_diff, upper_pack) / a_Y if a_Y > 0 else float("inf"),
           "emptiness_lhs": lhs, "emptiness_coefficient": coef,
           "window_non_empty": bool(a_Y < min(upper_diff, upper_pack)),
           "Q_min": Q_min, "Q_typ": Q_typ, "Q_max": Q_max,
           "R_Y_at_Q_min": R_Y_min, "R_Y_at_Q_typ": R_Y_typ, "R_Y_at_Q_max": R_Y_max,
           "margin_lower": R_Y_min / a_Y if a_Y > 0 else float("inf"),
           "margin_upper": min(upper_diff, upper_pack) / R_Y_max,
           "whole_reachable_band_inside":
               bool(R_Y_min > a_Y and R_Y_max < min(upper_diff, upper_pack)),
           "coherence_chi": chi,
           "H3_true_at_Q_max": 2.0 * R_Y_max * tau_sep,
           "P_no_third_at_Q_max": math.exp(-2.0 * R_Y_max * tau_sep),
           "H3_design_at_Q_max": 2.0 * R_Y_max * tau_design,
           "P_no_third_at_Q_max_design": math.exp(-2.0 * R_Y_max * tau_design),
           "T_div_at_Q_min": 1.0 / R_Y_min, "T_div_at_Q_typ": 1.0 / R_Y_typ,
           "T_div_at_Q_max": 1.0 / R_Y_max}
    p_gate, p_dup = 0.98, 0.99
    pc = p_gate * p_dup * out["P_no_third_at_Q_max_design"]
    po = p_gate * p_dup * out["P_no_third_at_Q_max"]
    out["power"] = {"p_gate_assumed": p_gate, "p_duplication_within_horizon_assumed": p_dup,
                    "p_arm_conservative": pc, "p_arm_optimistic": po,
                    "P_all_four_conservative": pc ** 4, "P_all_four_optimistic": po ** 4}
    return out


def show(tag, r):
    print("\n=== %s ===" % tag)
    c = r["cluster"]
    print(" D_X=%.6g D_Y=%.6g a_X=%.6g a_Y=%.6g  k_X=%.4g k_Y=%.6g"
          % (r["D_X"], r["D_Y"], r["a_X"], r["a_Y"], r["spec"]["kX"], r["spec"]["kY"]))
    print(" ell_X=%.4f  L_packed=%.4f  L_C=%.4f (%s)  R_X=%.4g (kin %.4g / res %.4g)"
          % (c["ell_X"], c["L_packed"], c["L_C"], c["binding"], c["R_X"],
             c["R_X_kinetic_cap"], c["R_X_resource_cap"]))
    print(" Delta_sep=%.3f  tau_sep=%.2f (KK-convention %.1f)  tau_design=%.2f  chi=%.3f"
          % (r["Delta_sep"], r["tau_sep"], r["tau_sep_kk_convention"], r["tau_sep_design"],
             r["coherence_chi"]))
    print(" window R_Y in (%.6g , %.6g)   upper: diffusive=%.6g  KK-packed=%.6g"
          % (r["window_lower_R_Y"], r["window_upper_R_Y_binding"],
             r["window_upper_R_Y_diffusive"], r["window_upper_R_Y_KK_packed"]))
    print(" NON_EMPTY=%s   emptiness lhs=%.6g (must be < 1), coefficient=%.4f"
          % (r["window_non_empty"], r["emptiness_lhs"], r["emptiness_coefficient"]))
    print(" reachable R_Y band (Q in [%d,%d]) = (%.6g , %.6g)  fully inside=%s"
          % (r["Q_min"], r["Q_max"], r["R_Y_at_Q_min"], r["R_Y_at_Q_max"],
             r["whole_reachable_band_inside"]))
    print("   margins: lower=%.4g   upper=%.4g" % (r["margin_lower"], r["margin_upper"]))
    print(" H3 at Q_max: true=%.5g -> P=%.4f ; with safety=%.5g -> P=%.4f"
          % (r["H3_true_at_Q_max"], r["P_no_third_at_Q_max"],
             r["H3_design_at_Q_max"], r["P_no_third_at_Q_max_design"]))
    print(" T_div: Q_max=%.5g  Q_typ=%.5g  Q_min=%.5g steps"
          % (r["T_div_at_Q_max"], r["T_div_at_Q_typ"], r["T_div_at_Q_min"]))
    print(" power P(all four): conservative=%.4f  optimistic=%.4f"
          % (r["power"]["P_all_four_conservative"], r["power"]["P_all_four_optimistic"]))


if __name__ == "__main__":
    CAP, S0, phi, omega = 16, 3, 0.05, 0.05
    Q_max, Q_arg = q_bounds(CAP, S0)
    print("Q_max (exact integer capacity bound) =", Q_max, Q_arg)

    FROZEN = {"p_hop_X": 0.20, "p_hop_Y": 0.002, "muX": 0.005, "muY": 0.0005,
              "kX": 0.02, "kY": 0.0008, "CAP": CAP, "S0": S0, "phi": phi, "omega": omega}

    # ---- MTW01 design point, fixed in this order and by these inequalities only:
    #  1. ell_X = 2.5 sites: the cloud must span several sites (lattice resolution) and every
    #     cost below scales as ell_X^2, so it is set at the smallest value that still gives a
    #     separation criterion Delta = 2*ell_X = 5 sites.
    #  2. D_X = 0.25, the largest the lattice allows (p_hop_X = 1)  ->  muX = D_X/ell_X^2
    #  3. D_Y = D_X/2: KK uses D_Y = D_X but KK's cluster is held by an attractive potential
    #     that MINCORE does not have. D_Y = D_X/2 puts the organiser's wander over one body
    #     lifetime at sqrt(2) cloud radii, so the cloud stays with its organiser.
    #  4. k_X = 1.0, deliberately far above the marginal value for cloud existence. It enters
    #     no boundary of the window; it only has to make the cloud exist.
    #  5. k_Y from the upper gate at the WORST case Q = Q_max, with margin 2.
    #  6. mu_Y from the lower gate with margin 10 against R_Y at Q_min = 1.
    ell = 2.5
    D_X = 0.25
    muX = D_X / ell ** 2
    D_Y = D_X / 2.0
    tau_sep = (2 * ell) ** 2 / (8.0 * D_Y)
    upper = (-math.log(0.90)) / (2.0 * 2.0 * tau_sep)
    kY = upper / (2.0 * Q_max)
    muY = kY * 1 / 10.0
    DESIGN = {"p_hop_X": 4 * D_X, "p_hop_Y": 4 * D_Y, "muX": muX, "muY": muY,
              "kX": 1.0, "kY": kY, "CAP": CAP, "S0": S0, "phi": phi, "omega": omega}

    rf = window(FROZEN, Q_max=Q_max)
    rd = window(DESIGN, Q_max=Q_max)
    show("MINCORE FROZEN POINT (the configuration that stopped)", rf)
    show("MTW01 DESIGN POINT (derived above, not tuned)", rd)

    verdict = ("WINDOW_NON_EMPTY_WITH_MARGIN" if
               (rd["window_non_empty"] and rd["whole_reachable_band_inside"]
                and min(rd["margin_lower"], rd["margin_upper"]) >= 2.0)
               else "WINDOW_NOT_DEMONSTRATED")
    print("\nADJUDICATION:", verdict)
    print("DESIGN SPEC:", json.dumps({k: DESIGN[k] for k in
                                      ("p_hop_X", "p_hop_Y", "muX", "muY", "kX", "kY",
                                       "CAP", "S0", "phi", "omega")}, indent=1))
    json.dump({"kamimura_kaneko": KK,
               "capacity_bound": {"CAP": CAP, "S0": S0, "Q_max": Q_max, "argmax": Q_arg},
               "frozen_point": rf, "design_point": rd, "adjudication": verdict},
              open("out/_window.json", "w"), indent=1)

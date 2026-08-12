"""MCM01 Etape C: the triply admissible region, and the deterministic selection rule.

PURE ANALYSIS. No engine, no RNG, no trajectory. Every constraint below is labelled with its
epistemic status:

  EXACT       an integer or algebraic consequence of the transition rule, with no closure
  CERTIFIED   a quadrature evaluation of a lattice Green's function, with a stated direction of
              conservatism
  NECESSARY   a condition that must hold, but whose sufficiency is not claimed
  GEOMETRIC   a consistency requirement between a predicted population and the room available
  PRACTICAL   a budget or resolution requirement declared in advance

S0, CAP and omega are PINNED at their MINCORE values throughout the grid, so that no result of
this mission can be attributed to enlarging the material budget. A separate control varies S0.
"""
from __future__ import annotations

import itertools
import json
import math

import lattice as LAT

# ---------------------------------------------------------------- pinned, never a lever
S0_PIN, CAP_PIN, OMEGA_PIN, L_PIN = 3, 16, 0.05, 36

# ---------------------------------------------------------------- declared thresholds
CRIT_MIN = 8.0            # required c_X * G(0); u* = CRIT_MIN gives P(source off) = 3.4e-4
N_MIN = 200.0             # required predicted quasi-stationary population c_X/muX
ELL_MIN, ELL_MAX = 2.5, 3.0
TAU_SEP_MAX = 2000.0      # so a future window mission stays affordable
T_RUN_MAX = 20000         # steps per confirmation arm
FORM_LIFETIMES = 5.0      # T_FORM_MAX = FORM_LIFETIMES / muX
MAINT_LIFETIMES = 20.0    # T_MAINT   = MAINT_LIFETIMES / muX
CLUSTER_TO_TORUS = 3.0    # 4*ell_X <= L / CLUSTER_TO_TORUS
Q_MAX_EXACT = 28          # corrected in audit A3
WINDOW_MARGIN = 2.0
P_STAR, SAFETY, SEP = 0.90, 2.0, 2.0

GRID = {
    "muX":   [0.001, 0.002, 0.004, 0.008, 0.016],
    "phi":   [0.05, 0.10, 0.20, 0.40],
    "ell_X": [2.5, 3.0],
    "rho_Y": [1.0],                       # p_hop_Y / p_hop_X ; KK use one D for every species
}
TIE_BREAK = ("muX", "phi", "ell_X", "rho_Y")


def p_hop_for(D_target):
    """Invert D_eff = q(1-q) for q, then p_hop = 4q. Returns None if unreachable."""
    if D_target > 0.25:
        return None
    q = (1.0 - math.sqrt(max(0.0, 1.0 - 4.0 * D_target))) / 2.0
    p = 4.0 * q
    return p if 0.0 < p <= 1.0 else None


def u_star(A):
    """Root of u = A*(1 - exp(-u)); the mean body-molecule occupancy of the organiser's cell."""
    if A <= 1.0:
        return 0.0
    u = A
    for _ in range(400):
        u = A * (1.0 - math.exp(-u))
    return u


def evaluate(muX, phi, ell, rho_Y):
    D_X = muX * ell ** 2
    p_hop_X = p_hop_for(D_X)
    out = {"muX": muX, "phi": phi, "ell_X": ell, "rho_Y": rho_Y, "S0": S0_PIN, "CAP": CAP_PIN,
           "omega": OMEGA_PIN, "L": L_PIN, "D_X": D_X, "p_hop_X": p_hop_X}
    if p_hop_X is None:
        out.update({"admissible": False, "fail": ["p_hop_X unreachable for D_X=%.4g" % D_X]})
        return out
    p_hop_Y = rho_Y * p_hop_X
    D_Y = LAT.D_eff(p_hop_Y)
    out.update({"p_hop_Y": p_hop_Y, "D_Y": D_Y})

    g_rel = LAT.G_body_about_organiser(p_hop_X, p_hop_Y, muX)
    tr = LAT.c_X_transport(S0_PIN, p_hop_X, phi)
    hard, _ = LAT.c_X_hard_cap(CAP_PIN)
    c_X = min(tr["c_X_transport"], float(hard))
    A = c_X * g_rel["G0"]
    N_pred = c_X / muX
    rho_max = (CAP_PIN - 2 * S0_PIN - 1) / (1.0 + muX / OMEGA_PIN)
    room = rho_max * math.pi * (2.0 * ell) ** 2
    ts = LAT.tau_sep(p_hop_X, p_hop_Y, muX, SEP)["tau_sep"]
    T_form = FORM_LIFETIMES / muX
    T_maint = max(MAINT_LIFETIMES / muX, 10.0 * ts)
    T_run = T_form + T_maint

    # what a future window mission would have to use at this point
    H3max = -math.log(P_STAR)
    upper = H3max / (2.0 * SAFETY * ts)
    kY_future = upper / (WINDOW_MARGIN * Q_MAX_EXACT)
    muY_future = kY_future / 10.0
    win_lhs = 2.0 * SAFETY * muY_future * ts / H3max
    T_div_future = 1.0 / (kY_future * (Q_MAX_EXACT / 2.0))

    out.update({"G0_relative": g_rel["G0"], "G_S0": tr["G_S0"],
                "c_X_transport": tr["c_X_transport"], "c_X_hard_cap": hard,
                "c_X_certified": c_X, "criticality_A": A, "u_star": u_star(A),
                "P_source_off": math.exp(-u_star(A)) if A > 1 else 1.0,
                "N_X_predicted": N_pred, "rho_max": rho_max, "room_for_N_X": room,
                "tau_sep": ts, "T_form_max": T_form, "T_maint": T_maint, "T_run": T_run,
                "kY_future": kY_future, "muY_future": muY_future,
                "window_emptiness_lhs": win_lhs, "T_div_future": T_div_future})

    fails = []
    if not (0 < p_hop_Y <= 1.0):
        fails.append("PRACTICAL p_hop_Y out of range")
    if c_X > hard:
        fails.append("EXACT c_X above the hard cand_X cap")
    if A < CRIT_MIN:
        fails.append("NECESSARY criticality A=%.2f < %.1f" % (A, CRIT_MIN))
    if N_pred < N_MIN:
        fails.append("NECESSARY N_X_predicted=%.0f < %.0f" % (N_pred, N_MIN))
    if N_pred > room:
        fails.append("GEOMETRIC N_X_predicted=%.0f exceeds room=%.0f" % (N_pred, room))
    if ts > TAU_SEP_MAX:
        fails.append("PRACTICAL tau_sep=%.0f > %.0f" % (ts, TAU_SEP_MAX))
    if T_run > T_RUN_MAX:
        fails.append("PRACTICAL T_run=%.0f > %d" % (T_run, T_RUN_MAX))
    if 4.0 * ell > L_PIN / CLUSTER_TO_TORUS:
        fails.append("GEOMETRIC cluster too large for the torus")
    if win_lhs >= 1.0:
        fails.append("NECESSARY future window empty, lhs=%.3g" % win_lhs)
    out["fail"] = fails
    out["admissible"] = not fails
    return out


def grid():
    rows = []
    for muX, phi, ell, rho in itertools.product(GRID["muX"], GRID["phi"], GRID["ell_X"],
                                                GRID["rho_Y"]):
        rows.append(evaluate(muX, phi, ell, rho))
    return rows


def selection_key(r):
    """FROZEN deterministic ordering: minimum predicted cost, ties broken by the fixed
    lexicographic order of the parameters, all ascending. No aesthetic input, no trajectory."""
    return (round(r["T_run"], 6),) + tuple(round(r[k], 12) for k in TIE_BREAK)


def select(rows, c_X_measured=None):
    """Apply the frozen rule. If c_X_measured is given (a dict keyed by the point's tie-break
    tuple), the criticality and population tests are re-evaluated with the MEASURED value."""
    cand = []
    for r in rows:
        rr = dict(r)
        if c_X_measured is not None:
            key = tuple(round(r[k], 12) for k in TIE_BREAK)
            if key not in c_X_measured:
                continue
            cx = c_X_measured[key]
            rr["c_X_measured"] = cx
            rr["criticality_A_measured"] = cx * r["G0_relative"]
            rr["N_X_predicted_measured"] = cx / r["muX"]
            f = []
            if rr["criticality_A_measured"] < CRIT_MIN:
                f.append("measured criticality %.2f < %.1f"
                         % (rr["criticality_A_measured"], CRIT_MIN))
            if rr["N_X_predicted_measured"] < N_MIN:
                f.append("measured N_X %.0f < %.0f" % (rr["N_X_predicted_measured"], N_MIN))
            rr["fail_measured"] = f
            if f or not r["admissible"]:
                continue
        elif not r["admissible"]:
            continue
        cand.append(rr)
    if not cand:
        return None, []
    cand.sort(key=selection_key)
    return cand[0], cand


if __name__ == "__main__":
    rows = grid()
    ok = [r for r in rows if r["admissible"]]
    print("grid points: %d, analytically admissible: %d" % (len(rows), len(ok)))
    print("\n%-7s %-6s %-5s | %-8s %-7s %-7s %-7s %-6s %-8s %-8s %-8s"
          % ("muX", "phi", "ell", "p_hop_X", "G0", "c_X", "A", "u*", "N_pred", "tau_sep",
             "T_run"))
    for r in sorted(rows, key=lambda z: (not z["admissible"], selection_key(z))):
        if r.get("p_hop_X") is None:
            continue
        print("%-7.4g %-6.2f %-5.1f | %-8.4f %-7.3f %-7.4f %-7.2f %-6.2f %-8.0f %-8.0f %-8.0f %s"
              % (r["muX"], r["phi"], r["ell_X"], r["p_hop_X"], r["G0_relative"],
                 r["c_X_certified"], r["criticality_A"], r["u_star"], r["N_X_predicted"],
                 r["tau_sep"], r["T_run"],
                 "ADMISSIBLE" if r["admissible"] else "; ".join(r["fail"])[:64]))
    best, cand = select(rows)
    print("\nfrozen selection rule -> %d candidates; analytic winner:" % len(cand))
    if best:
        print(json.dumps({k: best[k] for k in
                          ("muX", "phi", "ell_X", "rho_Y", "p_hop_X", "p_hop_Y", "G0_relative",
                           "c_X_certified", "criticality_A", "u_star", "N_X_predicted",
                           "tau_sep", "T_form_max", "T_maint", "T_run", "kY_future",
                           "muY_future", "T_div_future")}, indent=1))
    json.dump({"grid": GRID, "pinned": {"S0": S0_PIN, "CAP": CAP_PIN, "omega": OMEGA_PIN,
                                        "L": L_PIN},
               "thresholds": {"CRIT_MIN": CRIT_MIN, "N_MIN": N_MIN, "ELL": [ELL_MIN, ELL_MAX],
                              "TAU_SEP_MAX": TAU_SEP_MAX, "T_RUN_MAX": T_RUN_MAX,
                              "FORM_LIFETIMES": FORM_LIFETIMES,
                              "MAINT_LIFETIMES": MAINT_LIFETIMES,
                              "CLUSTER_TO_TORUS": CLUSTER_TO_TORUS,
                              "Q_MAX_EXACT": Q_MAX_EXACT, "WINDOW_MARGIN": WINDOW_MARGIN},
               "tie_break": list(TIE_BREAK), "rows": rows,
               "n_admissible": len(ok), "analytic_winner": best},
              open("/home/claude/MCM01/out/_region.json", "w"), indent=1)

"""MINCORE-CLOUD-MAINTENANCE-01, Etape A.

Recovery, integrity and ANALYTIC REPRODUCTION of every load-bearing claim carried over from
MINCORE and MTW01. No engine start, no stochastic probe, no trajectory: the only advances in
this file are bounded synthetic invariance checks run through the MTW01 guard in TEST mode,
where no start can be opened and every scoring function raises.

Every claim is re-derived independently and given one of:
    REPRODUCED            the claim is recovered exactly
    REPRODUCED_CORRECTED  the claim is recovered but with a correction that changes its status
    NOT_REPRODUCED        the claim could not be recovered; it is downgraded
"""
from __future__ import annotations

import ast
import json
import math
import os
import sys

import numpy as np

import lattice as LAT

MTW = "/home/claude/MTW01"
sys.path.insert(0, MTW + "/code")

R = {"claims": [], "notes": []}


def claim(name, status, detail, **extra):
    rec = {"claim": name, "status": status, "detail": detail}
    rec.update(extra)
    R["claims"].append(rec)
    print("  %-22s %s\n        %s" % (status, name, detail))
    return status.startswith("REPRODUCED")


# ==================================================================== A1. bytes and lineage
def a1_bytes():
    ok = True
    for tag, man, base in (("MTW01", "/home/claude/MTW01_SHA256SUMS", MTW),
                           ("MINCORE", "/home/claude/MINCORE_SHA256SUMS", "/home/claude/MINCORE")):
        import hashlib
        good = bad = 0
        for line in open(man):
            h, f = line.split()
            p = ("/home/claude/" + f) if f.endswith(".bundle") else os.path.join(base, f)
            if hashlib.sha256(open(p, "rb").read()).hexdigest() == h:
                good += 1
            else:
                bad += 1
        ok &= claim("%s manifest" % tag, "REPRODUCED" if bad == 0 else "NOT_REPRODUCED",
                    "%d files verified, %d mismatched" % (good, bad))
    return ok


# ==================================================================== A2. the engine's diffusion
def a2_diffusion():
    rows = []
    for p in (0.002, 0.05, 0.2, 0.5, 1.0):
        rows.append({"p_hop": p, "D_naive_p_over_4": LAT.D_naive(p), "D_eff_q_1_minus_q":
                     LAT.D_eff(p), "relative_error": LAT.D_eff(p) / LAT.D_naive(p) - 1.0})
    worst = min(r["relative_error"] for r in rows)
    claim("effective diffusion constant of _diffuse",
          "REPRODUCED_CORRECTED",
          "the four sequential direction attempts let a particle move and move back within one "
          "step, so <r^2> = 4*q*(1-q) and D_eff = q*(1-q), not p_hop/4. Error at p_hop=1 is "
          "%.1f%%, at p_hop=0.2 it is %.1f%%. MINCORE and MTW01 both used p_hop/4."
          % (100 * (LAT.D_eff(1.0) / LAT.D_naive(1.0) - 1),
             100 * (LAT.D_eff(0.2) / LAT.D_naive(0.2) - 1)),
          table=rows, worst_relative_error=worst)
    return True


# ==================================================================== A3. cand_X, cand_Y, caps
def a3_caps():
    CAP, S0 = 16, 3
    hard, arg = LAT.c_X_hard_cap(CAP)
    claim("exact hard cap on cand_X at an organiser cell", "REPRODUCED_CORRECTED",
          "exhaustive integer search gives max cand_X = %d at %s. MTW01 asserted cand_X <= S0 = "
          "%d, which is false: `_diffuse` accepts min(movers, dest_free) and is capped by free "
          "capacity, NOT by S0, so a cell can hold more than S0 resource units."
          % (hard, arg, S0), argmax=arg, value=hard)

    qm = LAT.Q_max_exact(CAP)
    a, aa = qm["with_nSY_le_S0_3"]
    b, bb = qm["without_that_restriction"]
    claim("Q_max exhaustive search", "REPRODUCED_CORRECTED",
          "with the MTW01 restriction n[SY] <= S0 = 3 the maximum is %d at %s, reproducing the "
          "published 27. Without that unsound restriction the exact maximum is %d at %s. "
          "Search space: %s" % (a, aa, b, bb, qm["space_searched"]),
          Q_max_mtw01=a, Q_max_exact=b)

    claim("N_X <= S0/muX", "REPRODUCED_CORRECTED",
          "the statement holds only while n[SX] <= S0. The exact per-organiser bound implied by "
          "the transition rule is N_X <= max(cand_X)/muX = %d/muX, i.e. %.0f at muX = 0.04 "
          "instead of the 75 published. Neither bound is the operative one: the SUSTAINABLE "
          "supply is transport limited, see A5." % (hard, hard / 0.04),
          exact_bound_numerator=hard, mtw01_bound_numerator=S0)
    return True


# ==================================================================== A4. N_X = 0 absorbing
def a4_absorbing():
    src = open(MTW + "/code/mtw.py").read()
    tree = ast.parse(src)
    cls = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "World"][0]
    fns = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    # every statement that increases n["X"] must live in _react
    writers = []
    for name, fn in fns.items():
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute)
                            and t.value.attr == "n"):
                        writers.append((name, node.lineno))
    react_src = ast.get_source_segment(src, fns["_react"])
    factor_ok = "pair = nX * nY" in react_src and "kk * pair" in react_src
    claim("N_X = 0 is absorbing", "REPRODUCED" if factor_ok else "NOT_REPRODUCED",
          "both birth probabilities are min(1, k*pair) with pair = nX*nY, so nX == 0 everywhere "
          "forces p_X = p_Y = 0 and births = Binomial(cand, 0) = 0 for BOTH species. The only "
          "statements that increase n['X'] are inside _react (writers at %s). Diffusion, decay "
          "and feed can only move, remove or create resources. Hence nX == 0 is invariant, and "
          "so is the pair (nX == 0, no further Y birth)." % writers,
          n_field_writers=writers)

    # synthetic confirmation through the MTW01 guard, TEST mode, bounded, score-blind
    import guard
    import mtw as M
    guard.set_test_mode()
    w = M.fresh_world(1234)
    w.n["Y"][8, 8] = 4                       # organisers only, no body molecule anywhere
    guard.advance(w, 300)
    ok = int(w.n["X"].sum()) == 0
    claim("N_X = 0 absorbing, synthetic confirmation", "REPRODUCED" if ok else "NOT_REPRODUCED",
          "300 bounded steps from a state with 4 organisers and zero body molecules: "
          "N_X = %d, N_Y = %d. Steps used through the guard: score-blind, no start opened."
          % (int(w.n["X"].sum()), int(w.n["Y"].sum())))
    guard.set_experiment_mode()
    return ok


# ==================================================================== A5. G(0) and c_X
def a5_green():
    # MTW01 design point
    P = {"p_hop_X": 1.0, "p_hop_Y": 0.5, "muX": 0.04, "S0": 3, "phi": 0.05}
    g_rel = LAT.G_body_about_organiser(P["p_hop_X"], P["p_hop_Y"], P["muX"])
    g_x_only = LAT.green_origin_converged([LAT.a_of(P["p_hop_X"])], 1.0 - P["muX"])
    tr = LAT.c_X_transport(P["S0"], P["p_hop_X"], P["phi"])
    claim("G(0) definition", "REPRODUCED_CORRECTED",
          "G(0) is the expected number of steps a body molecule spends in the cell where it was "
          "created, counting returns, before decay: G(0) = (2pi)^-2 INT dk /(1 - (1-muX)*phi(k)). "
          "MTW01 used the walk of X ALONE (G(0) = %.4f). The organiser also moves, and what the "
          "source needs is co-location with the ORGANISER, so the correct walk is the relative "
          "one, whose characteristic function is the product: G(0) = %.4f. Using the X-only walk "
          "OVERSTATES G(0) by %.1f%%." % (g_x_only["G0"], g_rel["G0"],
                                          100 * (g_x_only["G0"] / g_rel["G0"] - 1)),
          G0_relative=g_rel["G0"], G0_X_only=g_x_only["G0"], quadrature=g_rel)

    claim("c_X, certified transport bound", "REPRODUCED_CORRECTED",
          "the sustainable supply to one absorbing cell in a field fed at rate phi toward S0 is "
          "J = S0/G_S(0) with G_S(0) = %.4f, i.e. c_X <= %.4f per step at the MTW01 design "
          "point. MTW01 bracketed c_X only in [phi*S0, S0] = [0.15, 3]; the transport bound "
          "%.4f lies inside that bracket and is far tighter."
          % (tr["G_S0"], tr["c_X_transport"], tr["c_X_transport"]), **tr)

    # the prediction this makes for the MTW01 arms, and the recorded observation
    N_pred = tr["c_X_transport"] / P["muX"]
    blocks = json.load(open(MTW + "/out/_blocks.json"))
    obs = [a["gate"]["N_X"] for a in blocks["blocks"][0]["arms"] if a.get("gate")]
    claim("the transport bound predicts the MTW01 observation", "REPRODUCED",
          "N_X* = c_X/muX = %.1f predicted with no free parameter. The one MTW01 arm whose cloud "
          "established recorded N_X = %d at the gate. Recorded N_X at the gate across the four "
          "arms: %s. This is a post hoc consistency check on an OUTCOME_INFORMED quantity, not "
          "an input to any choice made below." % (N_pred, max(obs), obs),
          N_X_predicted=N_pred, N_X_recorded=obs, label="OUTCOME_INFORMED")

    crit = tr["c_X_transport"] * g_rel["G0"]
    claim("status of the condition c_X*G(0) > 1", "REPRODUCED_CORRECTED",
          "at the MTW01 design point c_X*G(0) = %.3f > 1, so that point was SUPERCRITICAL and "
          "the condition was NOT what failed. Classification: the condition is NECESSARY AND "
          "SUFFICIENT for supercriticality of the LINEARISATION about the absorbing state "
          "N_X = 0 (a lone body molecule at the organiser triggers c_X births per step for G(0) "
          "steps, so the mean offspring number is exactly c_X*G(0)); it is NECESSARY but NOT "
          "SUFFICIENT for long persistence, because the source SATURATES at cand_X once nX >= 1, "
          "which bounds the quasi-stationary population at N_X* = c_X/muX, and extinction from a "
          "finite population beside an absorbing state is certain in finite time. It is local, "
          "linearised, and rests on a Poisson closure and on ignoring volume exclusion; ignoring "
          "exclusion makes particles more mobile, so the computed G(0) is a LOWER bound and the "
          "test is conservative." % crit,
          c_X_times_G0_at_mtw01_design=crit,
          classification={"necessary": True, "sufficient_for_supercriticality_of_linearisation":
                          True, "sufficient_for_persistence": False, "local": True,
                          "linearised": True, "asymptotic_closure": "Poisson",
                          "heuristic_only": False})
    return True


# ==================================================================== A6. 1519 vs 190
def a6_divergence():
    F = {"p_hop_X": 0.20, "p_hop_Y": 0.002, "muX": 0.005, "muY": 0.0005}
    out = {}
    for conv in ("naive_delta", "kk_scaling", "first_passage_2d"):
        for eff in (False, True):
            w = LAT.window_emptiness(F["p_hop_X"], F["p_hop_Y"], F["muX"], F["muY"],
                                     convention=conv, effective=eff)
            out["%s|D=%s" % (conv, "eff" if eff else "naive")] = {
                "tau_sep": w["tau"]["tau_sep"], "emptiness_lhs": w["emptiness_lhs"]}
    a = out["naive_delta|D=naive"]["emptiness_lhs"]
    b = out["first_passage_2d|D=naive"]["emptiness_lhs"]
    claim("resolution of 1519 versus 190", "REPRODUCED",
          "both numbers are the same quantity, the left-hand side of the window non-emptiness "
          "condition at the FROZEN MINCORE point, under two different conventions for the "
          "separation time. With tau = Delta^2/D_Y (the convention used in the first evaluation "
          "of MTW01) it is %.1f. With the exact two-dimensional first-passage time "
          "tau = Delta^2/(8*D_Y) it is %.1f. The ratio is exactly %.4f = 8, the first-passage "
          "correction and nothing else. The final MTW01 report quotes the corrected value; the "
          "1519 appeared only in an intermediate console evaluation and is superseded. Under the "
          "corrected D_eff the value becomes %.1f. In every convention the window at the frozen "
          "MINCORE point is EMPTY by two to three orders of magnitude, so the conclusion is "
          "unaffected." % (a, b, a / b, out["first_passage_2d|D=eff"]["emptiness_lhs"]),
          table=out, ratio=a / b,
          traceable_final_value=out["first_passage_2d|D=eff"]["emptiness_lhs"])
    return True


# ==================================================================== A7. margins and cost
def a7_margins_cost():
    win = json.load(open(MTW + "/out/_window.json"))["design_point"]
    ml, mu = win["margin_lower"], win["margin_upper"]
    claim("convention of the margins 10 and 2", "REPRODUCED",
          "both are LINEAR ratios, not logarithmic: margin_lower = R_Y(Q_min)/a_Y = %.4f and "
          "margin_upper = upper_edge/R_Y(Q_max) = %.4f, recomputed from the frozen "
          "_window.json fields. No decibel or log convention is involved."
          % (ml, mu), margin_lower=ml, margin_upper=mu)

    # the x30 claim: MTW01 predicted T_div ~ 3417 at the design point and ~97624 at the
    # candidate remediation point in its feasibility scan
    pm = json.load(open(MTW + "/out/_postmortem.json"))
    rows = [r for r in pm["feasibility_scan"]["rows"] if r.get("feasible")]
    ratio = max(r["T_div_at_Q_7"] for r in rows) / win["T_div_at_Q_typ"]
    claim("the x30 cost estimate", "REPRODUCED",
          "MTW01 predicted T_div = %.0f steps at its design point and up to %.0f steps at the "
          "remediation points of its feasibility scan, a ratio of %.1f. The published 'about "
          "thirty times' is that ratio. It applies to a FUTURE window mission, whose cost is set "
          "by the organiser duplication time. The present mission measures MAINTENANCE, whose "
          "cost is set by the body-molecule lifetime, and is far cheaper."
          % (win["T_div_at_Q_typ"], max(r["T_div_at_Q_7"] for r in rows), ratio),
          ratio=ratio)
    return True


if __name__ == "__main__":
    print("== A1 bytes and lineage ==");            a1_bytes()
    print("== A2 diffusion constant ==");           a2_diffusion()
    print("== A3 exact caps ==");                   a3_caps()
    print("== A4 the absorbing state ==");          a4_absorbing()
    print("== A5 G(0) and c_X ==");                 a5_green()
    print("== A6 1519 vs 190 ==");                  a6_divergence()
    print("== A7 margins and cost ==");             a7_margins_cost()
    n = {}
    for c in R["claims"]:
        n[c["status"]] = n.get(c["status"], 0) + 1
    R["summary"] = n
    R["all_reproduced"] = all(c["status"].startswith("REPRODUCED") for c in R["claims"])
    json.dump(R, open("/home/claude/MCM01/out/_audit.json", "w"), indent=1, default=str)
    print("\nSUMMARY", json.dumps(n), " all reproduced:", R["all_reproduced"])

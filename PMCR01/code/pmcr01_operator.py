"""PMCR01 §6 — the exact discrete minority operator, in the scheduler's true event order.

Nothing here is fitted and nothing is simulated. Two things are computed:

  1. the ADMISSIBLE cell-state set, by exhaustive enumeration under the occupancy invariant,
     which gives the exact ceiling Q_max on the per-step birth intensity;
  2. the EXACT one-step offspring law of one Y, written from the code path and then VERIFIED
     against the arguments the scheduler actually passes to `binomial`, captured at the point
     of use on a NON_SCIENTIFIC_SEMANTIC_FIXTURE. No sampling: `rng.binomial(n, p)` IS the
     binomial law, so proving the arguments proves the law.

The occupancy invariant is the load-bearing category-A fact:

    _diffuse accepts min(movers, dest_free) and so cannot exceed CAP;
    _react converts SY -> Y and SX -> X, conserving occupancy;
    _decay converts Y -> WY and X -> WX, conserving occupancy;
    _exchange removes exactly as many units as it inserts, conserving occupancy.

Hence, at every cell and every step, nX + nY + nSX + nSY + nWX + nWY <= CAP = 16.
"""
from __future__ import annotations

import itertools
import json
import math
import subprocess
import sys

import numpy as np

sys.path.insert(0, "/home/claude/PMCR01/code")
import pmcr01_sentinel as SENT                            # noqa: E402
import pmcr01_oracles as OR                               # noqa: E402

OUT = "/home/claude/PMCR01/out"
SPECIES = ("X", "Y", "SX", "SY", "WX", "WY")


# ------------------------------------------------------------ admissible states, exactly
def admissible_Q(CAP=16, nY=1):
    """Q = nX * min(nSY, free) over EVERY admissible cell state with nY organisers present.
    Exhaustive: the state space is the compositions of at most CAP units over six species."""
    best, achieved, zeros = -1, set(), 0
    argmax = None
    total = 0
    for nX in range(CAP + 1):
        for nSY in range(CAP + 1 - nX):
            for nSX in range(CAP + 1 - nX - nSY):
                for nWX in range(CAP + 1 - nX - nSY - nSX):
                    for nWY in range(CAP + 1 - nX - nSY - nSX - nWX):
                        occ = nX + nY + nSX + nSY + nWX + nWY
                        if occ > CAP:
                            continue
                        total += 1
                        free = CAP - occ
                        Q = nX * min(nSY, free)
                        achieved.add(Q)
                        if Q == 0:
                            zeros += 1
                        if Q > best:
                            best, argmax = Q, {"nX": nX, "nY": nY, "nSX": nSX, "nSY": nSY,
                                               "nWX": nWX, "nWY": nWY, "free": free}
    return {"CAP": CAP, "nY_assumed": nY,
            "n_admissible_cell_states": total,
            "Q_max": best, "argmax_state": argmax,
            "achieved_Q_values": sorted(achieved),
            "Q_EQUALS_ZERO_IS_ADMISSIBLE": 0 in achieved,
            "n_admissible_states_with_Q_zero": zeros,
            "fraction_of_admissible_states_with_Q_zero": zeros / total,
            "INFIMUM_OF_Q_OVER_THE_ADMISSIBLE_SET": 0,
            "WHY_THE_INFIMUM_MATTERS": (
                "category A knows the admissible SET. A positive value of E[Q] is a property "
                "of the MEASURE on that set, i.e. of the realized cloud. The set alone gives "
                "0 <= Q <= %d and nothing tighter." % best)}


# ------------------------------------------------------------ the exact offspring law
def offspring_pgf(z, c, p, m):
    """f(z) = E[z^Z] for ONE Y in one step, in the scheduler's order.

        _react   births ~ Binomial(c, p),  c = min(nSY, free),  p = min(1, kY*nX*nY)
        _decay   every Y present AFTER _react, parent and newborns alike, dies w.p. m = muY

    The parent contributes (m + (1-m) z). Each of the c independent candidate trials
    contributes 1 - p + p (m + (1-m) z). Newborns are exposed to decay in their birth step
    because _decay runs after _react in the same step: that is not an assumption, it is the
    order in kinetics.World._one_step."""
    par = m + (1.0 - m) * z
    trial = 1.0 - p * (1.0 - m) * (1.0 - z)
    return par * (trial ** c)


def offspring_moments(c, p, m):
    R = (1.0 - m) * (1.0 + c * p)
    var = (m * (1.0 - m)
           + c * p * m * (1.0 - m)
           + (1.0 - m) ** 2 * c * p * (1.0 - p))
    return {"mean_offspring_R": R, "variance": var}


def verify_law_against_the_scheduler(EN, V2):
    """Capture (n, p) at the point of use across a grid and compare with the analytic law."""
    rows = []
    for q, s, sx in ((3, 4, 2), (7, 4, 0), (1, 7, 0), (0, 5, 3), (5, 0, 2)):
        for kY, muY in ((0.0, 0.0), (0.05, 0.0), (0.05, 0.25), (0.5, 0.9)):
            r = OR.one_step_record(EN, V2, {"kY": kY, "muY": muY}, q=q, s=s, sx=sx)
            occ = q + 1 + s + sx
            free = 16 - occ
            c_pred = min(s, free)
            p_pred = min(1.0, kY * q * 1)
            bino = [call for call in r["calls_main"] if call["fn"] == "binomial"]
            # the frozen order: 4 diffusion passes X, 4 Y, 4 SX, 4 SY, then react (X, Y),
            # then decay (X, Y). p_hop is 0 in the fixture, so diffusion still draws.
            y_birth = bino[17] if len(bino) > 17 else None
            y_death = bino[19] if len(bino) > 19 else None
            got_c = int(np.max(y_birth["n"])) if y_birth else None
            got_p = float(np.max(y_birth["p"])) if y_birth else None
            got_m = float(np.max(y_death["p"])) if y_death else None
            rows.append({
                "cell_state": {"nX": q, "nY": 1, "nSY": s, "nSX": sx,
                               "occupancy": occ, "free": free},
                "kY": kY, "muY": muY,
                "analytic_c": c_pred, "scheduler_c": got_c, "C_MATCHES": c_pred == got_c,
                "analytic_p": p_pred, "scheduler_p": got_p,
                "P_MATCHES": (got_p is not None and abs(p_pred - got_p) < 1e-15),
                "analytic_m": muY, "scheduler_m": got_m,
                "M_MATCHES": (got_m is not None and abs(muY - got_m) < 1e-15),
                "R": offspring_moments(c_pred, p_pred, muY)["mean_offspring_R"],
                "n_binomial_calls": len(bino)})
    return rows


def x_hazard_saturation(EN, V2):
    """p_X = min(1, kX*nX*nY) with kX = 1.0. For any nX >= 1 and nY >= 1 this is EXACTLY 1.
    So one organiser already saturates the X source hazard, and a second Y in the SAME cell
    adds nothing; only a second Y in a DIFFERENT cell adds a source. Category A, exact."""
    rows = []
    for q, ny in ((0, 1), (1, 1), (3, 1), (3, 2), (7, 3)):
        with SENT.fixture("x-saturation"):
            w, sp = OR.build_fixture(EN, V2, {"kY": 0.0, "muY": 0.0}, q=q, s=4, sx=2)
            w.n["Y"][1, 1] = ny
            w._one_step()
            bino = [c for c in w.rng.calls if c["fn"] == "binomial"]
            px = float(np.max(bino[16]["p"])) if len(bino) > 16 else None
        rows.append({"nX": q, "nY_same_cell": ny, "kX": 1.0,
                     "analytic_p_X": min(1.0, 1.0 * q * ny), "scheduler_p_X": px,
                     "MATCHES": px is not None and abs(min(1.0, 1.0 * q * ny) - px) < 1e-15})
    return {"ROWS": rows,
            "SATURATED_FOR_ANY_nX_TIMES_nY_GE_1": all(
                r["analytic_p_X"] == 1.0 for r in rows if r["nX"] * r["nY_same_cell"] >= 1),
            "CONSEQUENCE": (
                "at kX = 1.0 the X birth probability is exactly 1 wherever an organiser meets "
                "one X molecule. The organiser count is therefore NOT a minority variable in "
                "the causal sense: one Y already drives the source at full strength, and a "
                "second Y changes the system only by creating a SECOND SOURCE CELL once it "
                "separates. 'Minority in count' and 'minority in causal role' come apart.")}


def single_organiser_observable_layer():
    """The inherited observable layer resolves the organiser as the FIRST nonzero Y cell."""
    src = subprocess.run(("git", "show", "HEAD:OBTC02/code/metrics_obtc.py"),
                         cwd="/home/claude/edl", capture_output=True, text=True).stdout
    line = [l.strip() for l in src.splitlines() if 'organiser_y"], out["organiser_x"]' in l]
    return {"evidence": line,
            "READING": ("metrics_obtc.frame takes oy[0], ox[0] from np.nonzero(nY). With two "
                        "organisers it silently reports one of them, chosen by row-major "
                        "order, and r80_organiser is measured about that arbitrary centre. "
                        "Every inherited observable, every frozen gate and the qualified "
                        "source-response operator are SINGLE-ORGANISER BY CONSTRUCTION."),
            "CLASS": "the qualified environment is not defined for nY >= 2 in distinct cells"}


def exact_kernel_constants():
    """From the frozen point and OBTR01's exact one-step displacement law."""
    p_hop = 0.10263340389897246
    q = p_hop / 4.0
    a = 2 * q * (1 - q)
    D = q * (1 - q)
    D_rel = 2 * D
    return {"p_hop": p_hop, "q_per_direction": q,
            "per_axis_activity_a": a, "D_per_species": D,
            "D_relative_two_Y": D_rel,
            "CHECK_against_the_frozen_manifest": {"a_X": 0.05, "D_X": 0.025,
                                                  "D_relative": 0.05},
            "MATCHES": (abs(a - 0.05) < 1e-12 and abs(D - 0.025) < 1e-12
                        and abs(D_rel - 0.05) < 1e-12),
            "separation_time_steps": {str(d): d * d / (4.0 * D_rel)
                                      for d in (1.0, 2.5, 5.0, 6.082762530298219,
                                                8.54400374531753)},
            "WHY": ("two Y molecules perform independent exact walks, so their separation "
                    "diffuses with D_rel = 2 D_Y and <r^2> = 4 D_rel t. The displacement law "
                    "is the difference of two Bernoulli(q) per axis, not p_hop/4.")}


def main():
    equiv = OR.verify_on_disk_equals_committed()
    if not all(v["IDENTICAL"] for v in equiv.values()):
        raise SystemExit("on-disk files are not the committed blobs")
    sys.path.insert(0, "/home/claude/ORR01/code")
    sys.path.insert(0, "/home/claude/OBTC02/code")
    import pmcr01_oracles as _OR
    SENT.install(seed_register_paths=_OR.SEED_REGISTERS)
    _raw_before = SENT.raw_dir_witness(_OR.RAW_DIRS)
    import lawspec_v2 as V2
    import engine_obtc as EN
    import guard_obtc as GD

    adm = admissible_Q()
    ver = verify_law_against_the_scheduler(EN, V2)
    sat = x_hazard_saturation(EN, V2)
    obs = single_organiser_observable_layer()
    ker = exact_kernel_constants()

    out = {
        "SECTION": "PMCR01 §6 — the exact discrete minority operator",
        "OCCUPANCY_INVARIANT": (
            "_diffuse accepts min(movers, dest_free); _react and _decay are species "
            "conversions; _exchange removes exactly what it inserts. Occupancy per cell is "
            "therefore bounded by CAP and, under BALANCED_CHEMOSTAT, conserved after the "
            "initial condition."),
        "ADMISSIBLE_STATES": adm,
        "EXACT_ONE_STEP_OFFSPRING_LAW": {
            "pgf": "f(z) = (m + (1-m) z) * (1 - p (1-m) (1-z))^c",
            "c": "min(nSY, free)   -- the candidate count in _react",
            "p": "min(1, kY * nX * nY)   -- the birth probability in _react",
            "m": "muY   -- the decay probability in _decay, applied AFTER _react",
            "mean_offspring_R": "(1 - muY) * (1 + c p)",
            "NEWBORNS_ARE_EXPOSED_TO_DECAY_IN_THEIR_BIRTH_STEP": True,
            "WHY": "the frozen order is diffuse x4 -> react -> decay -> exchange",
            "SCHEDULER_VERIFICATION": ver,
            "ALL_ARGUMENTS_MATCH": all(r["C_MATCHES"] and r["P_MATCHES"] and r["M_MATCHES"]
                                       for r in ver)},
        "STATE_REPRESENTATION": {
            "IS_A_SCALAR_BRANCHING_RATIO_LEGITIMATE": False,
            "why": ("c and p are functions of the Y's OWN cell state (nSY, free, nX), and nX "
                    "at that cell is produced BY the Y itself: _react creates X only where "
                    "nX*nY >= 1. The environment of the lineage is endogenous, so the "
                    "smallest exact state is (lineage size, cell environment) and the "
                    "environment is not exogenous noise."),
            "SMALLEST_EXACT_STATE": "(n_Y at each occupied cell, and (nX, nSY, free) at each "
                                    "such cell)",
            "CONDITIONAL_EXACTNESS": "CONDITIONAL_EXACT — exactly as the parent found for X",
            "MARGINAL_CLOSURE": "NOT_CLOSED — for the same structural reason"},
        "X_HAZARD_SATURATION": sat,
        "OBSERVABLE_LAYER": obs,
        "EXACT_KERNEL_CONSTANTS": ker,
        "SENTINEL": SENT.report(GD, _raw_before, SENT.raw_dir_witness(_OR.RAW_DIRS)),
    }
    json.dump(out, open(f"{OUT}/_operator.json", "w"), indent=1, default=str)

    print("admissible cell states with nY=1 : %d" % adm["n_admissible_cell_states"])
    print("Q_max = nX * min(nSY, free)      : %d   at %s" % (adm["Q_max"], adm["argmax_state"]))
    print("Q = 0 admissible                 : %s  (%.1f %% of admissible states)"
          % (adm["Q_EQUALS_ZERO_IS_ADMISSIBLE"],
             100 * adm["fraction_of_admissible_states_with_Q_zero"]))
    print("infimum of Q over the set        : %d" % adm["INFIMUM_OF_Q_OVER_THE_ADMISSIBLE_SET"])
    print("\nscheduler verification of the exact law: all arguments match = %s"
          % out["EXACT_ONE_STEP_OFFSPRING_LAW"]["ALL_ARGUMENTS_MATCH"])
    for r in ver[:6]:
        print("   nX=%d nSY=%d free=%2d kY=%-5s muY=%-5s | c %d/%s p %.6g/%.6g m %.6g/%.6g "
              "| R=%.8f"
              % (r["cell_state"]["nX"], r["cell_state"]["nSY"], r["cell_state"]["free"],
                 r["kY"], r["muY"], r["analytic_c"], r["scheduler_c"], r["analytic_p"],
                 r["scheduler_p"] if r["scheduler_p"] is not None else -1,
                 r["analytic_m"], r["scheduler_m"] if r["scheduler_m"] is not None else -1,
                 r["R"]))
    print("\nX hazard saturation (kX = 1.0):")
    for r in sat["ROWS"]:
        print("   nX=%d nY=%d -> p_X analytic %.3f scheduler %s match %s"
              % (r["nX"], r["nY_same_cell"], r["analytic_p_X"], r["scheduler_p_X"],
                 r["MATCHES"]))
    print("\nexact kernel: a=%.6f D=%.6f D_rel=%.6f  matches manifest %s"
          % (ker["per_axis_activity_a"], ker["D_per_species"], ker["D_relative_two_Y"],
             ker["MATCHES"]))
    print("separation times (steps): %s"
          % {k: round(v, 1) for k, v in ker["separation_time_steps"].items()})
    s = out["SENTINEL"]
    print("\nSENTINEL construct=%d advance=%d sci_starts=%d sci_seeds=%d ALL_FOUR_ZERO=%s"
          % (s["ENGINE_CONSTRUCT_CALLS"], s["ENGINE_ADVANCE_CALLS"],
             s["SCIENTIFIC_WORLD_STARTS"], s["SCIENTIFIC_SEEDS_OPENED"], s["ALL_FOUR_ZERO"]))


if __name__ == "__main__":
    main()

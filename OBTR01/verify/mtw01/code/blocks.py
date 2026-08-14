"""MTW01 protocol. 4 blocks x 4 arms = 16 outcome-informative starts. TECHNICAL_RESERVE = 0.

Every constant in the PROTOCOL section is fixed either by code/window.py or by an exact capacity
argument, before any start. None is fitted to any output of this mission or of any earlier one;
the provenance table in the preplan gives the origin of each one.

DESIGN. All four blocks share an IDENTICAL preparation: one organiser at the centre of the
torus with X_SEED body molecules, the design parameters, and the same body-cloud gate. The
block's perturbation, if any, is applied at the gate and only at the gate. A block therefore
differs from block 1 in exactly one parameter, applied at exactly one moment, so a difference in
outcome is attributable to that parameter and to nothing about the preparation.

Block 1 runs first and ALL FOUR of its arms must pass before any other block is started. That
is enforced here, not asserted in prose.
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np

import guard
import observe
from mtw import Spec, fresh_world, seed_one_organiser, spec_with

OUT = "/home/claude/MTW01/out"

# ------------------------------------------------------------------ FROZEN PROTOCOL
L_C = Spec.ell_X()                          # 2.5 exactly, = sqrt(D_X/muX)
DELTA_SEP = 2.0 * L_C                       # 5.0 sites: two clouds of radius L_C, just disjoint
TAU_SEP = DELTA_SEP ** 2 / (8.0 * Spec.D_Y())   # 25.0 steps, exact 2D first passage
X_SEED = 4                                  # body molecules placed with the single organiser
T_X = 100                                   # cloud establishment: 4 body lifetimes (1/muX = 25)
T_Q = 50                                    # Q is averaged over the last T_Q steps before the gate
N_X_MIN = 10
RG_MAX_ELL = 3.0                            # Rg of the cloud about its organiser, in units of L_C
FILL_MAX_FRAC = 0.25                        # occupied support may not exceed a quarter of the torus
Q_FLOOR = 6.0                               # below this the core is too weak to adjudicate
SEEDS = (101, 202, 303, 404)

Q_TYP = 15.0                                # predicted realised Q; used ONLY to size horizons
R_Y_TYP = Spec.kY * Q_TYP                   # 2.9267e-4 per step

BLOCKS = [
    {"name": "ONE_Y_FIXED_CORE",
     "override": {},
     "horizon": 40000,
     "predicted": ["SEPARATED"],
     "rationale": "the design point. For every reachable Q the per-organiser replication rate "
                  "R_Y = k_Y*Q lies inside the window with a factor 10 below the upper edge at "
                  "Q_min and a factor 2 at Q_max, so the two organisers reach separation "
                  "Delta_sep before a third appears. Predicted P(no third) = 0.974 at Q_max.",
     "requirement": "ALL_FOUR_MUST_PASS"},
    {"name": "WINDOW_UPPER_VIOLATED",
     "override": {"kY": Spec.kY * 300.0},
     "horizon": 5000,
     "predicted": ["EXPLOSION"],
     "rationale": "R_Y is pushed 300x above the design point at the gate and nowhere else. The "
                  "cumulative hazard over one separation window becomes H3 = 2*R_Y*tau_sep = "
                  "4.39, so P(no third organiser) = 0.0124.",
     "requirement": "AT_LEAST_3_OF_4_PREDICTED"},
    {"name": "WINDOW_LOWER_VIOLATED",
     "override": {"muY": 10.0 * Spec.kY * Q_TYP},
     "horizon": 5000,
     "predicted": ["EXTINCTION", "ORGANISER_LOST_IN_WINDOW"],
     "rationale": "a_Y is set to 10 x R_Y at the typical Q, violating the KK lower boundary "
                  "a_Y < R_Y. P(the organiser duplicates before it decays) = R_Y/(R_Y+a_Y) = "
                  "1/11 = 0.091, so 91 percent of arms should lose the organiser.",
     "requirement": "AT_LEAST_3_OF_4_PREDICTED"},
    {"name": "SLOW_ORGANISER_MINCORE_MOBILITY",
     "override": {"p_hop_Y": 0.002},
     "horizon": 40000,
     "predicted": ["EXPLOSION"],
     "rationale": "p_hop_Y is returned to the literal MINCORE value 0.002, i.e. D_Y = 5e-4. The "
                  "upper edge of the window is proportional to D_Y, so it collapses by 250x "
                  "while R_Y is untouched: H3 = 2*R_Y*tau_sep = 3.66 and P(no third) = 0.0257. "
                  "This block tests the specific design defect named in the scope-correction "
                  "addendum and changes nothing else. At MINCORE's RATIO D_Y = D_X/100 the "
                  "prediction would be P = 0.48, which is why the literal value is used.",
     "requirement": "AT_LEAST_3_OF_4_PREDICTED"},
]


def predictions():
    """Closed-form prediction for each block, computed here so that it is written to the
    frozen record BEFORE any start."""
    out = {}
    for b in BLOCKS:
        sp = spec_with(**b["override"]) if b["override"] else Spec
        tau = DELTA_SEP ** 2 / (8.0 * sp.D_Y())
        R_Y = sp.kY * Q_TYP
        R_Y_max = sp.kY * 27.0
        out[b["name"]] = {
            "tau_sep": tau, "R_Y_at_Q_typ": R_Y, "R_Y_at_Q_max": R_Y_max,
            "H3_at_Q_typ": 2.0 * R_Y * tau, "H3_at_Q_max": 2.0 * R_Y_max * tau,
            "P_no_third_at_Q_typ": math.exp(-2.0 * R_Y * tau),
            "P_no_third_at_Q_max": math.exp(-2.0 * R_Y_max * tau),
            "T_div_at_Q_typ": 1.0 / R_Y,
            "P_duplicate_before_decay_at_Q_typ": R_Y / (R_Y + sp.muY),
            "predicted_outcome": b["predicted"], "horizon": b["horizon"]}
    return out


def protocol_constants():
    return {"L_C": L_C, "DELTA_SEP": DELTA_SEP, "TAU_SEP": TAU_SEP, "X_SEED": X_SEED,
            "T_X": T_X, "T_Q": T_Q, "N_X_MIN": N_X_MIN, "RG_MAX_ELL": RG_MAX_ELL,
            "FILL_MAX_FRAC": FILL_MAX_FRAC, "Q_FLOOR": Q_FLOOR, "SEEDS": list(SEEDS),
            "Q_TYP": Q_TYP, "R_Y_TYP": R_Y_TYP,
            "ESCAPEE_MAX_MASS": observe.ESCAPEE_MAX_MASS,
            "MINORITY_MAX": observe.MINORITY_MAX,
            "MIN_BODY_PER_ORGANISER": observe.MIN_BODY_PER_ORGANISER,
            "design_spec": Spec.as_dict(),
            "blocks": [{k: b[k] for k in ("name", "override", "horizon", "predicted",
                                          "requirement", "rationale")} for b in BLOCKS],
            "predictions": predictions()}


def run_arm(block, seed):
    tag = "%s/seed%d" % (block["name"], seed)
    H = int(block["horizon"])
    w = fresh_world(seed, Spec)                      # identical preparation in every block
    seed_one_organiser(w, X_SEED)
    rec = {"block": block["name"], "seed": seed, "override": block["override"],
           "horizon": H, "predicted": block["predicted"]}
    st = {"t2": None, "outcome": None, "gate": None, "gated": False,
          "q_win": [], "q_trace": []}

    def gate_now(ww):
        q_mean = float(np.mean(st["q_win"])) if st["q_win"] else 0.0
        g = observe.gate_X(ww, L_C, N_X_MIN, RG_MAX_ELL, FILL_MAX_FRAC, Q_FLOOR, q_mean)
        st["gate"], st["gated"] = g, True
        if not g["PASS"]:
            st["outcome"] = "GATE_FAIL:" + ",".join(k for k, v in g["checks"].items() if not v)
            return False
        if block["override"]:                        # the single, pre-declared perturbation
            ww.sp = spec_with(**block["override"])
        return True

    def per_step(ww):
        ny = int(ww.n["Y"].sum())
        if not st["gated"]:
            st["q_win"].append(observe.realised_Q(ww))       # rolling window, always defined
            if len(st["q_win"]) > T_Q:
                st["q_win"].pop(0)
            if ny == 0:
                st["outcome"] = "EXTINCTION_BEFORE_GATE"
                return "STOP"
            if ny >= 2 or ww.step >= T_X:
                # the gate is evaluated at min(T_X, t of the second organiser)
                if ny >= 3:
                    st["outcome"] = "EXPLOSION_BEFORE_GATE"
                    return "STOP"
                if not gate_now(ww):
                    return "STOP"
                if ny == 2:
                    st["t2"] = ww.step
                    ww.H3_exact, ww.H3_kk = 0.0, 0.0
                    ww.hazard_armed = True
            return None
        # ---- window phase
        if ww.step % 25 == 0 and len(st["q_trace"]) < 4000:
            st["q_trace"].append(observe.realised_Q(ww))
        if ny == 0:
            st["outcome"] = "EXTINCTION"
            return "STOP"
        if st["t2"] is None:
            if ny >= 3:
                st["outcome"] = "EXPLOSION"
                return "STOP"
            if ny == 2:
                st["t2"] = ww.step
                ww.H3_exact, ww.H3_kk = 0.0, 0.0
                ww.hazard_armed = True
            return None
        if ny >= 3:
            st["outcome"] = "EXPLOSION"
            return "STOP"
        if ny == 1:
            st["outcome"] = "ORGANISER_LOST_IN_WINDOW"
            return "STOP"
        if observe.max_pair_separation(ww) >= DELTA_SEP:
            st["outcome"] = "SEPARATED"
            return "STOP"
        return None

    with guard.start("arm", tag, H):
        guard.advance(w, H, per_step=per_step)
    w.hazard_armed = False
    if st["outcome"] is None:
        st["outcome"] = ("CENSORED_NO_DUPLICATION" if st["t2"] is None
                         else "CENSORED_NO_SEPARATION")

    rec.update({
        "outcome": st["outcome"], "gate": st["gate"], "steps_used": w.step,
        "t_second_organiser": st["t2"],
        "tau_sep_observed": (w.step - st["t2"]) if st["t2"] is not None else None,
        "tau_sep_predicted": DELTA_SEP ** 2 / (8.0 * w.sp.D_Y()),
        "H3_exact": w.H3_exact, "H3_kk_form": w.H3_kk,
        "P_no_third_organiser": math.exp(-w.H3_exact),
        "N_X_at_end": int(w.n["X"].sum()), "N_Y_at_end": int(w.n["Y"].sum()),
        "N_Y_at_separation": int(w.n["Y"].sum()),
        "Q_trace_mean": float(np.mean(st["q_trace"])) if st["q_trace"] else None,
        "Q_trace_max": float(np.max(st["q_trace"])) if st["q_trace"] else None})
    if st["outcome"] == "SEPARATED":
        rec["components"] = observe.component_report(w)
        discs = []
        for p in observe.organiser_positions(w):
            nx, ny_, _ = observe.disc_counts(w, p, L_C)
            discs.append({"centre": list(p), "N_X": nx, "N_Y": ny_})
        rec["discs_at_separation"] = discs
        ok, verdict = observe.arm_verdict(rec, L_C, DELTA_SEP)
    else:
        rec["components"] = None
        rec["discs_at_separation"] = []
        ok, verdict = False, st["outcome"]
    rec["PASS"] = bool(ok)
    rec["verdict"] = verdict
    return rec


def main():
    guard.set_experiment_mode()
    results = {"protocol": protocol_constants(), "blocks": [], "stopped": None}
    for bi, block in enumerate(BLOCKS):
        arms = []
        for seed in SEEDS:
            r = run_arm(block, seed)
            arms.append(r)
            print("  %-32s seed=%-4d %-30s steps=%-6d t2=%-7s tau_obs=%-6s H3=%.4g P=%.4f"
                  % (block["name"], seed, r["outcome"], r["steps_used"],
                     r["t_second_organiser"], r["tau_sep_observed"], r["H3_exact"],
                     r["P_no_third_organiser"]), flush=True)
        n_pred = sum(1 for a in arms if a["outcome"] in block["predicted"])
        n_pass = sum(1 for a in arms if a["PASS"])
        blk = {"name": block["name"], "predicted": block["predicted"],
               "requirement": block["requirement"], "rationale": block["rationale"],
               "n_arms": len(arms), "n_matching_prediction": n_pred, "n_pass": n_pass,
               "MET": bool(n_pass == 4) if block["requirement"] == "ALL_FOUR_MUST_PASS"
                      else bool(n_pred >= 3),
               "arms": arms}
        results["blocks"].append(blk)
        print("BLOCK %d %s: matching=%d/4 pass=%d/4 MET=%s\n"
              % (bi + 1, block["name"], n_pred, n_pass, blk["MET"]), flush=True)
        if bi == 0 and not blk["MET"]:
            results["stopped"] = "BLOCK1_GATE_NOT_MET__NO_FURTHER_BLOCK_STARTED"
            break
    results["ledger"] = guard.audit()
    json.dump(results, open(OUT + "/_blocks.json", "w"), indent=1, default=str)
    return results


if __name__ == "__main__":
    main()
    sys.exit(0)

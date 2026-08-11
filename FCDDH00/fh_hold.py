"""FCDDH00 prospective fixed-axis hold-out validation, H0-H9, exact 2^16 randomization and the
immutable parent-P2 hold-out distribution. Runs ONLY after FCDDH00_HOLDOUT_ACTIVE_RAW_LOCK is
committed. Zero engine starts. No fit, no centering, no rescaling, no reorientation.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fh_core as FC                                              # noqa: E402
import fh_decode as DEC                                           # noqa: E402
import HOLDOUT_FIXED_AXIS_SCORER_V1 as SC                         # noqa: E402
import EXACT_RANDOMIZATION_ENUMERATOR_V1 as EN                    # noqa: E402

ROLE = "HOLDOUT"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    DEC.require_raw_lock("HOLDOUT")
    parent = DEC.load_parent()
    axis = SC.load_axis(f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.npz",
                        f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.json")
    lock, thr, blocks, rows = DEC.decode(ROLE, parent)
    order = sorted(range(len(blocks)), key=lambda i: blocks[i]["upstream_seed"])
    blocks = [blocks[i] for i in order]
    ids = [b["upstream_seed"] for b in blocks]

    npass = sum(1 for r in rows if r["cell_material"])
    H1 = npass == len(rows) and len(rows) == 128
    contrasts = []
    for b in blocks:
        for bd in b["descendants"].values():
            v, n2, four = DEC.contrast_material(bd)
            contrasts.append({"block": b["upstream_seed"], "did": bd["did"], "verdict": v,
                              "contrast_norm_sq": n2.as_pair(), "four_tau_sq": four.as_pair()})
    H2 = all(c["verdict"] == "PASS" for c in contrasts) and len(contrasts) == 64

    vnorm_hi = float(FC.isqrt_iv(FC.dot_iv([FC.Iv.exact(Fr(t)) for t in axis.v],
                                           [FC.Iv.exact(Fr(t)) for t in axis.v])).hi)

    # ---- both orientations of the single fair geometry coin, recomputed through the scorer ----
    per_block = []
    for b in blocks:
        ent = {"block": b["upstream_seed"], "geometry_coin": b["geometry_coin"], "orient": {}}
        for eps, swap in ((+1, False), (-1, True)):
            x, dn, df, gN, gF = DEC.block_x(parent, b, swap_geometry=swap)
            s = SC.score_block(axis, x)
            p = SC.pair_margins(axis, dn, df)
            ap = {(aN, aF): FC.A_PAIR(b["descendants"][(gN, aN)]["tau_iv"],
                                      b["descendants"][(gF, aF)]["tau_iv"])
                  for aN in (0, 1) for aF in (0, 1)}
            J, m, verd, marg = SC.block_success(p, ap, vnorm_hi)
            ent["orient"][eps] = {"x": x, "s": s, "J": J, "m": m, "p": p, "A_PAIR": ap,
                                  "verdicts": verd, "NEAR_is": gN}
        sp, sm = ent["orient"][+1]["s"], ent["orient"][-1]["s"]
        ent["equivariance_exact"] = bool(sp.lo == -sm.hi and sp.hi == -sm.lo)
        per_block.append(ent)

    sH = [e["orient"][+1]["s"] for e in per_block]
    JH = [e["orient"][+1]["J"] for e in per_block]
    mH = [e["orient"][+1]["m"] for e in per_block]
    K_H = sum(JH)
    T_lo = sum((s.lo for s in sH), Fr(0))
    T_hi = sum((s.hi for s in sH), Fr(0))
    T_H = FC.Iv(T_lo, T_hi)

    lic = json.load(open(f"{HERE}/RANDOMIZATION_LICENSE.json"))
    licensed = lic["FCDDH00_RANDOMIZATION_LICENSE"] is True
    randj = {"FCDDH00_RANDOMIZATION_LICENSE": lic["FCDDH00_RANDOMIZATION_LICENSE"],
             "conditions": lic["conditions"]}
    if licensed:
        rT = EN.enumerate_T([s.lo for s in sH], [s.hi for s in sH])
        rK = EN.enumerate_K([e["orient"][+1]["J"] for e in per_block],
                            [e["orient"][-1]["J"] for e in per_block], K_H)
        randj.update({
            "P_RANDOMIZATION_T": str(rT["p_exact"]) if rT["exact"] else None,
            "P_RANDOMIZATION_T_float": float(rT["p_exact"]) if rT["exact"] else None,
            "P_RANDOMIZATION_T_bracket": [str(rT["p_lo"]), str(rT["p_hi"])],
            "n_assignments": rT["n_assignments"], "count_ge_certain": rT["count_ge_certain"],
            "count_undecided": rT["count_undecided"],
            "K_ASSIGNMENT_TAIL_SENSITIVITY": str(rK["tail"]),
            "K_ASSIGNMENT_TAIL_SENSITIVITY_float": float(rK["tail"]),
            "K_ASSIGNMENT_TAIL_INFERENTIAL_STATUS": rK["K_ASSIGNMENT_TAIL_INFERENTIAL_STATUS"],
            "exact_equivariance_verified_per_block": [e["equivariance_exact"] for e in per_block],
            "recomputed_through_frozen_scorer_per_orientation": True,
            "sharp_null": ("within every neutral branch slot and allocation orbit, the outside-P2 "
                           "carrier-differential response would be unchanged if the explicit "
                           "geometry assignment were switched between NEAR and FAR"),
            "design_reference_K_ge_12_of_16": str(EN.design_reference_K_ge_12_of_16()),
            "design_reference_float": float(EN.design_reference_K_ge_12_of_16())})
        H6 = rT["exact"] and rT["p_exact"] <= Fr(5, 100)
        HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS = (
            "LICENSED__RESPONSE_ONLY_T_P=" + str(rT["p_exact"]) if rT["exact"]
            else "NUMERICALLY_UNRESOLVED")
    else:
        randj["P_RANDOMIZATION_T"] = "NOT_LICENSED"
        H6 = None
        HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS = "NOT_LICENSED__REASON=" + lic["reason"]

    npos = sum(1 for s in sH if s.gt0() is True)
    H7 = (T_H.gt0() is True) and npos >= 12
    sq = [float(s.mid()) ** 2 for s in sH]
    H8v = max(sq) / sum(sq) if sum(sq) > 0 else float("nan")
    H8 = H8v < 0.50
    H3 = all(not bd["gauge_cooptimal"] for b in blocks for bd in b["descendants"].values())
    H4 = all(r["reference_M2sq_agrees"] and r["reference_gauge_agrees"] for r in rows) and \
        all(t["reference_agrees_tau"] for t in thr["thresholds"])
    H5 = K_H >= 12
    H0 = True
    H9 = True

    # ---- absolute materiality on the fixed axis --------------------------------------------
    xs = [e["orient"][+1]["x"] for e in per_block]
    XB = [FC.Iv.exact(0)] * FC.DIM
    for x in xs:
        XB = [XB[i] + x[i] for i in range(FC.DIM)]
    XB = [(XB[i] * FC.Iv.exact(Fr(1, len(xs)))).round_out() for i in range(FC.DIM)]
    S_BAR = (FC.dot_float(list(axis.v), XB)).round_out()
    AX = []
    for b in blocks:
        AX.append(FC.A_X_block([b["descendants"][(g, a)]["tau_iv"] for g in ("NEAR", "FAR") for a in (0, 1)]))
    AXB = FC.Iv.exact(0)
    for t in AX:
        AXB = AXB + t
    AXB = (AXB * FC.Iv.exact(Fr(1, len(AX)))).round_out()
    mat = FC.certified_verdict(S_BAR, AXB)
    nXB = FC.norm_iv(XB)
    rot_inv = FC.certified_verdict(nXB, AXB)

    # ---- immutable parent-P2 hold-out distribution -------------------------------------------
    tube = parent.tube
    desc = []
    for b in blocks:
        for (g, a), bd in b["descendants"].items():
            R = bd["R_P2_DESC"]
            desc.append({"block": b["upstream_seed"], "did": bd["did"], "geometry": g,
                         "allocation": a, "R_P2_DESC": R.as_pair(), "R_P2_DESC_float": float(R.mid()),
                         "Q_P2_DESC": float(R.mid() / tube),
                         "exceeds_tube": bool(R.lo > tube)})
    exceed = sum(1 for d in desc if d["exceeds_tube"])
    anc = []
    for b in blocks:
        vals = [float(bd["R_P2_DESC"].mid()) for bd in b["descendants"].values()]
        lows = [bd["R_P2_DESC"].lo for bd in b["descendants"].values()]
        anc.append({"block": b["upstream_seed"], "R_P2_ANCESTRY_MEAN": sum(vals) / 4,
                    "R_P2_ANCESTRY_MAX": max(vals),
                    "J_P2_ALL4": int(all(l <= tube for l in lows))})
    all4 = sum(a["J_P2_ALL4"] for a in anc)

    gates = {"H0": H0, "H1": H1, "H2": H2, "H3": H3, "H4": H4, "H5": H5,
             "H6": H6, "H7": H7, "H8": H8, "H9": H9}
    core_ok = all(gates[k] for k in ("H0", "H1", "H2", "H3", "H4", "H5", "H7", "H8", "H9"))
    if not licensed:
        repl = ("FINITE_PANEL_COHERENT__RANDOMIZATION_NOT_LICENSED" if core_ok else "NOT_VALIDATED")
    else:
        repl = "RANDOMIZED_HOLDOUT_VALIDATED" if (core_ok and H6) else "NOT_VALIDATED"

    out = {
        "HOLDOUT_CELL_MATERIALITY_STATUS": "PASS_128_OF_128" if H1 else f"FAIL_{npass}_OF_128",
        "HOLDOUT_DIRECT_CARRIER_CONTRAST_STATUS": "PASS_64_OF_64" if H2 else "FAIL",
        "HOLDOUT_FIXED_AXIS_DIRECTIONAL_REPLICATION_STATUS": repl,
        "HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS": HOLDOUT_FIXED_AXIS_RANDOMIZATION_STATUS,
        "HOLDOUT_ALLOCATION_AVERAGED_DIRECTION_SECONDARY_STATUS":
            ("PASS" if (npos >= 12 and licensed and H6) else
             ("RANDOMIZATION_NOT_LICENSED" if not licensed else "FAIL")),
        "HOLDOUT_INTERACTION_ABSOLUTE_MATERIALITY_STATUS":
            {"PASS": "FIXED_DIRECTION_ABSOLUTELY_MATERIAL",
             "FAIL": "FIXED_DIRECTION_BELOW_ABSOLUTE_MATERIALITY",
             "UNRESOLVED": "UNRESOLVED"}[mat],
        "HOLDOUT_ALLOCATION_ORBIT_ROBUSTNESS_STATUS":
            ("ROBUST_ACROSS_FULL_COMPLEMENTARY_ORBIT" if K_H >= 12 else
             ("ALLOCATION_AVERAGED_ONLY__WORST_PAIR_FAILS" if npos >= 12 else "NO_DIRECTIONAL_SUPPORT")),
        "K_H": K_H, "K_H_of_16": f"{K_H}_OF_16", "BLOCK_SUCCESS_FRACTION": K_H / 16,
        "T_H": T_H.as_pair(), "T_H_float": float(T_H.mid()),
        "n_positive_s_H": npos, "max_leverage": H8v,
        "S_BAR": S_BAR.as_pair(), "S_BAR_float": float(S_BAR.mid()),
        "A_X_BAR": AXB.as_pair(), "A_X_BAR_float": float(AXB.mid()),
        "absolute_materiality_verdict": mat,
        "rotation_invariant_norm_verdict": rot_inv,
        "norm_X_BAR_H": nXB.as_pair(),
        "alignment_of_holdout_mean_with_vD": float(
            sum(axis.v[i] * XB[i].fl() for i in range(FC.DIM)) /
            (float(nXB.mid()) if float(nXB.mid()) > 0 else 1.0)),
        "gates": gates,
        "P2_HOLDOUT_DESCENDANT_SCORE_STATUS": "COMPLETE_64_OF_64",
        "P2_HOLDOUT_DESCENDANT_EXCEED_COUNT_OF_64": exceed,
        "P2_HOLDOUT_ALL4_ANCESTRY_COUNT_OF_16": all4,
        "P2_HOLDOUT_GENERATOR_INTERVAL_LICENSE": "NOT_LICENSED",
        "FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS": "FAILED_AS_PREDECLARED",
        "P2_POPULATION_TRANSFER_INTERPRETATION": "INCONCLUSIVE_FROM_THIS_GATE_ALONE",
    }
    json.dump(out, open(f"{HERE}/HOLDOUT_GATE_LADDER.json", "w"), indent=1)
    json.dump({"HOLDOUT_CELL_MATERIALITY_STATUS": out["HOLDOUT_CELL_MATERIALITY_STATUS"],
               "rows": rows, "contrasts": contrasts},
              open(f"{HERE}/HOLDOUT_ALL_ROWS_AND_CONTRASTS.json", "w"), indent=1)
    json.dump({"blocks": [{"block": e["block"], "geometry_coin": e["geometry_coin"],
                           "s_H": e["orient"][+1]["s"].as_pair(),
                           "s_H_float": float(e["orient"][+1]["s"].mid()),
                           "J": e["orient"][+1]["J"],
                           "m": e["orient"][+1]["m"].as_pair(),
                           "m_float": float(e["orient"][+1]["m"].mid()),
                           "s_H_swapped": e["orient"][-1]["s"].as_pair(),
                           "J_swapped": e["orient"][-1]["J"],
                           "equivariance_exact": e["equivariance_exact"],
                           "pair_margins": {f"aN{a}_aF{c}": e["orient"][+1]["p"][(a, c)].as_pair()
                                            for a in (0, 1) for c in (0, 1)},
                           "A_PAIR": {f"aN{a}_aF{c}": e["orient"][+1]["A_PAIR"][(a, c)].as_pair()
                                      for a in (0, 1) for c in (0, 1)},
                           "verdicts": {f"aN{a}_aF{c}": e["orient"][+1]["verdicts"][(a, c)]
                                        for a in (0, 1) for c in (0, 1)}} for e in per_block],
               "K_H": K_H, "T_H": T_H.as_pair()},
              open(f"{HERE}/HOLDOUT_FIXED_AXIS_SCORES_AND_BLOCK_SUCCESS.json", "w"), indent=1)
    json.dump(randj, open(f"{HERE}/HOLDOUT_EXACT_2POW16_RANDOMIZATION.json", "w"), indent=1)
    json.dump({"per_block_worst_margin": [{"block": ids[k], "m": mH[k].as_pair(),
                                           "m_float": float(mH[k].mid()), "J": JH[k]}
                                          for k in range(len(ids))],
               "allocation_averaged_positive": npos,
               "note": "u[b;v] > 0 means every NEAR allocation member lies above every FAR "
                       "allocation member along the fixed carrier-differential axis"},
              open(f"{HERE}/HOLDOUT_ALLOCATION_ORBIT_REPORT.json", "w"), indent=1)
    json.dump({"S_BAR": S_BAR.as_pair(), "A_X_BAR": AXB.as_pair(),
               "verdict": mat, "rotation_invariant_verdict": rot_inv,
               "norm_X_BAR_H": nXB.as_pair(),
               "per_block_A_X": [t.as_pair() for t in AX]},
              open(f"{HERE}/HOLDOUT_ABSOLUTE_MATERIALITY_REPORT.json", "w"), indent=1)
    json.dump({"TUBE_P2_LOBO_parent": str(tube), "descendants": desc, "ancestries": anc,
               "P2_HOLDOUT_DESCENDANT_EXCEED_COUNT_OF_64": exceed,
               "P2_HOLDOUT_ALL4_ANCESTRY_COUNT_OF_16": all4,
               "P2_HOLDOUT_GENERATOR_INTERVAL_LICENSE": "NOT_LICENSED",
               "clustering_note": "the 64 descendants are clustered within sixteen ancestries and "
                                  "are never treated as 64 independent Bernoulli trials",
               "FSQBT00_LEGACY_STRICT_MAX4_ALL_BLOCK_CONTAINMENT_STATUS": "FAILED_AS_PREDECLARED",
               "P2_POPULATION_TRANSFER_INTERPRETATION": "INCONCLUSIVE_FROM_THIS_GATE_ALONE"},
              open(f"{HERE}/IMMUTABLE_P2_HOLDOUT_DISTRIBUTION_REPORT.json", "w"), indent=1)
    json.dump({"rows_M2sq_agree": sum(1 for r in rows if r["reference_M2sq_agrees"]),
               "rows_total": len(rows),
               "gauge_agree": sum(1 for r in rows if r["reference_gauge_agrees"]),
               "tau_agree": sum(1 for t in thr["thresholds"] if t["reference_agrees_tau"]),
               "tau_total": len(thr["thresholds"]), "H4": H4,
               "production_reference_agreement_bound": {"relative": DEC.REL_TOL, "absolute": DEC.ABS_TOL}},
              open(f"{HERE}/HOLDOUT_PRODUCTION_REFERENCE_RECOMPUTATION.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, (list, dict))}, indent=1))


if __name__ == "__main__":
    main()

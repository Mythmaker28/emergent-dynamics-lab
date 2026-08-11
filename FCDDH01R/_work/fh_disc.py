"""FCDDH00 discovery decode, D0-D11 gate ladder and (only if licensed) axis serialization.

Runs ONLY after FCDDH00_DISCOVERY_ACTIVE_RAW_LOCK is committed. Zero engine starts.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fh_core as FC                                              # noqa: E402
import fh_decode as DEC                                           # noqa: E402
import fh_ref as RF                                               # noqa: E402
import DISCOVERY_AXIS_TRAINER_V1 as TR                            # noqa: E402

ROLE = "DISCOVERY"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
COOPT_ENUM_CAP = 12


def main():
    DEC.require_raw_lock("DISCOVERY")
    parent = DEC.load_parent()
    lock, thr, blocks, rows = DEC.decode(ROLE, parent)
    ids = [b["upstream_seed"] for b in blocks]
    order = sorted(range(len(ids)), key=lambda i: ids[i])
    blocks = [blocks[i] for i in order]
    ids = sorted(ids)

    # ---------------------------------------------------------------- D1 / D2
    npass = sum(1 for r in rows if r["cell_material"])
    D1 = npass == len(rows) and len(rows) == 96
    contrasts = []
    for b in blocks:
        for key, bd in b["descendants"].items():
            v, n2, four = DEC.contrast_material(bd)
            contrasts.append({"block": b["upstream_seed"], "did": bd["did"],
                              "geometry": bd["geometry"], "allocation": bd["allocation"],
                              "verdict": v, "contrast_norm_sq": n2.as_pair(),
                              "four_tau_sq": four.as_pair(),
                              "ratio": float(n2.mid() / four.mid()) if four.mid() > 0 else None})
    D2 = all(c["verdict"] == "PASS" for c in contrasts) and len(contrasts) == 48

    # ---------------------------------------------------------------- x, A_X, X_BAR
    xs, ax, orbit = [], [], []
    for b in blocks:
        x, dn, df, _, _ = DEC.block_x(parent, b)
        xs.append(x)
        four_tau = [b["descendants"][(g, a)]["tau_iv"] for g in ("NEAR", "FAR") for a in (0, 1)]
        ax.append(FC.A_X_block(four_tau))
        orbit.append({"block": b["upstream_seed"], "d_near": dn, "d_far": df,
                      "tau": {f"{g}_a{a}": b["descendants"][(g, a)]["tau_iv"]
                              for g in ("NEAR", "FAR") for a in (0, 1)}})
    XB = TR.mean_x(xs)
    nXB = FC.norm_iv(XB)
    AXB = FC.Iv.exact(0)
    for t in ax:
        AXB = AXB + t
    AXB = (AXB * FC.Iv.exact(Fr(1, len(ax)))).round_out()

    # P2 orthogonality of every x[b]
    p2x = []
    for x in xs:
        px = FC.mat_vec(parent.P2, x)
        p2x.append(float(FC.isqrt_iv(FC.dot_iv(px, px)).mid()))

    D3 = nXB.gt0() is True
    D4 = FC.certified_verdict(nXB, AXB) == "PASS"

    # ---------------------------------------------------------------- trainer + LOAO
    srcs = [f"{HERE}/DISCOVERY_ACTIVE_RAW_ARCHIVE"]
    full, folds = TR.loao(ids, xs, parent, srcs)
    vD = full["v_D"]
    axis_norm_upper = float(FC.isqrt_iv(FC.dot_iv([FC.Iv.exact(Fr(t)) for t in vD],
                                                  [FC.Iv.exact(Fr(t)) for t in vD])).hi)

    import HOLDOUT_FIXED_AXIS_SCORER_V1 as SC                      # frozen scorer, used for J/p
    Jres = []
    for k, b in enumerate(blocks):
        _, dn, df, _, _ = DEC.block_x(parent, b)
        vfold = folds[k]["v_fold"]
        for tag, vv in (("fold", vfold), ("full", vD)):
            p = {}
            for aN in (0, 1):
                for aF in (0, 1):
                    p[(aN, aF)] = FC.dot_float(vv, FC.vec_sub(dn[aN], df[aF]))
            ap = {(aN, aF): FC.A_PAIR(b["descendants"][("NEAR", aN)]["tau_iv"],
                                      b["descendants"][("FAR", aF)]["tau_iv"])
                  for aN in (0, 1) for aF in (0, 1)}
            nu = float(FC.isqrt_iv(FC.dot_iv([FC.Iv.exact(Fr(t)) for t in vv],
                                             [FC.Iv.exact(Fr(t)) for t in vv])).hi)
            J, m, verd, marg = SC.block_success(p, ap, nu)
            Jres.append({"block": b["upstream_seed"], "axis": tag, "J": J,
                         "m": m.as_pair(), "m_float": float(m.mid()),
                         "verdicts": {f"aN{a}_aF{c}": verd[(a, c)] for a in (0, 1) for c in (0, 1)},
                         "p": {f"aN{a}_aF{c}": p[(a, c)].as_pair() for a in (0, 1) for c in (0, 1)},
                         "A_PAIR": {f"aN{a}_aF{c}": ap[(a, c)].as_pair() for a in (0, 1) for c in (0, 1)}})
    Jfold = {r["block"]: r for r in Jres if r["axis"] == "fold"}
    Jfull = {r["block"]: r for r in Jres if r["axis"] == "full"}
    D5n = sum(Jfold[b]["J"] for b in ids)
    D5 = D5n >= 10
    D6v = min(f["alignment_sq"] for f in folds)
    D6 = D6v >= 0.80
    sfull, lev = TR.leverage(vD, xs)
    D7v = max(lev)
    D7 = D7v < 0.50

    # D8: block deletions with the FULL-discovery sign, no reorientation
    d8 = []
    for k, b in enumerate(ids):
        keep = [xs[j] for j in range(len(xs)) if j != k]
        Xm = TR.mean_x(keep)
        lo = FC.dot_float(vD, Xm)
        mm = sum(Jfull[ids[j]]["m_float"] for j in range(len(ids)) if j != k) / (len(ids) - 1)
        d8.append({"deleted": b, "lower_dot": lo.as_pair(), "positive": lo.gt0() is True,
                   "mean_m_excl": mm, "mean_m_positive": mm > 0})
    D8 = all(r["positive"] and r["mean_m_positive"] for r in d8)

    # D9: allocation exchanges + co-optimal gauge orbits
    alloc_inv = []
    for k, b in enumerate(blocks):
        swapped = {"descendants": {}}
        for (g, a), bd in b["descendants"].items():
            swapped["descendants"][(g, 1 - a)] = bd
        xs2, _, _, _, _ = DEC.block_x(parent, swapped)
        same = all(xs2[i].lo == xs[k][i].lo and xs2[i].hi == xs[k][i].hi for i in range(FC.DIM))
        alloc_inv.append({"block": ids[k], "x_identical_under_allocation_exchange": bool(same)})
    coopt = [bd["did"] for b in blocks for bd in b["descendants"].values() if bd["gauge_cooptimal"]]
    D9 = all(r["x_identical_under_allocation_exchange"] for r in alloc_inv) and \
        (len(coopt) == 0 or len(coopt) <= COOPT_ENUM_CAP)
    D10 = all(r["reference_M2sq_agrees"] for r in rows) and \
        all(r["reference_gauge_agrees"] for r in rows) and \
        all(t["reference_agrees_tau"] for t in thr["thresholds"])

    # D11: dependency audit of the trainer
    import ast
    tsrc = ast.parse(open(f"{HERE}/DISCOVERY_AXIS_TRAINER_V1.py").read())
    timports = sorted({al.name for n in ast.walk(tsrc) if isinstance(n, ast.Import) for al in n.names} |
                      {(n.module or "") for n in ast.walk(tsrc) if isinstance(n, ast.ImportFrom)})
    forbidden = [m for m in timports if m in ("HOLDOUT_FIXED_AXIS_SCORER_V1",) or
                 any(t in m for t in ("FSQBT00", "FCRA00", "WL2SMF00", "FWL2CF00", "SQDT00"))]
    D11 = forbidden == [] and all(str(p).startswith(TR.ALLOWED_ROOT) for p in srcs)
    D0 = True

    gates = {"D0": D0, "D1": D1, "D2": D2, "D3": D3, "D4": D4, "D5": D5, "D6": D6,
             "D7": D7, "D8": D8, "D9": D9, "D10": D10, "D11": D11}
    failed = [k for k, v in gates.items() if not v]
    licensed = not failed

    # ---------------------------------------------------------------- reports
    json.dump({"DISCOVERY_CELL_MATERIALITY_STATUS": "PASS_96_OF_96" if D1 else f"INCOMPLETE_{npass}_OF_96",
               "n_pass": npass, "n_rows": len(rows), "rows": rows},
              open(f"{HERE}/DISCOVERY_ALL_ROWS_AND_CONTRASTS.json", "w"), indent=1)
    json.dump({"DISCOVERY_DIRECT_CARRIER_CONTRAST_STATUS":
               "PASS_48_OF_48" if D2 else "INCOMPLETE",
               "contrasts": contrasts}, open(f"{HERE}/DISCOVERY_CONTRASTS.json", "w"), indent=1)
    json.dump({"blocks": [{"block": ids[k],
                           "x_enclosure": [t.as_pair() for t in xs[k]],
                           "x_float": [t.fl() for t in xs[k]],
                           "A_X": ax[k].as_pair(), "A_X_float": float(ax[k].mid()),
                           "P2_x_norm": p2x[k],
                           "J_full_axis": Jfull[ids[k]]["J"],
                           "worst_margin_full_axis": Jfull[ids[k]]["m_float"],
                           "J_fold_axis": Jfold[ids[k]]["J"],
                           "worst_margin_fold_axis": Jfold[ids[k]]["m_float"],
                           "pair_margins_full": Jfull[ids[k]]["p"],
                           "A_PAIR_full": Jfull[ids[k]]["A_PAIR"]} for k in range(len(ids))],
               "X_BAR_D": [t.as_pair() for t in XB], "X_BAR_D_float": [t.fl() for t in XB],
               "norm_X_BAR_D": nXB.as_pair(), "norm_X_BAR_D_float": float(nXB.mid()),
               "A_X_BAR": AXB.as_pair(), "A_X_BAR_float": float(AXB.mid()),
               "allocation_exchange_invariance": alloc_inv,
               "cooptimal_gauge_descendants": coopt},
              open(f"{HERE}/DISCOVERY_INTERACTION_AND_ORBIT_TABLE.json", "w"), indent=1)
    json.dump({"folds": [{"left_out": f["left_out"], "alignment": f["alignment"],
                          "alignment_sq": f["alignment_sq"],
                          "score_omitted": f["score_omitted"].as_pair(),
                          "score_omitted_float": float(f["score_omitted"].mid()),
                          "J_omitted_fold_axis": Jfold[f["left_out"]]["J"],
                          "worst_margin_fold_axis": Jfold[f["left_out"]]["m_float"],
                          "v_fold": f["v_fold"],
                          "rank1_projector_trace": float(sum(t * t for t in f["v_fold"])),
                          "canonicalisation": f["canonicalisation"]} for f in folds],
               "min_alignment_sq": D6v, "n_fold_J1": D5n,
               "block_separability_proof":
                   "the immutable parent-P2 residual gauge statistic D_desc = sum_o (u_o - mu)^T Q v_o "
                   "depends only on that descendant's own two carrier rows and on immutable parent "
                   "objects; it is therefore descendant separable and a fortiori block separable, so "
                   "every fold rebuilds each retained and omitted descendant gauge identically from "
                   "that descendant's own response, never from a full-panel gauge",
               "block_deletions_D8": d8},
              open(f"{HERE}/DISCOVERY_LOAO_AXIS_ARBITRATION.json", "w"), indent=1)
    json.dump({"cooptimal_gauge_descendants": coopt,
               "n_cooptimal": len(coopt),
               "gauge_statistic_per_descendant":
                   [{"did": bd["did"], "D_enclosure": bd["gauge_statistic"].as_pair(),
                     "sign": bd["gauge_sign"], "cooptimal": bd["gauge_cooptimal"],
                     "reference_sign": bd["ref_gauge_sign"]}
                    for b in blocks for bd in b["descendants"].values()],
               "enumeration_cap": COOPT_ENUM_CAP},
              open(f"{HERE}/DISCOVERY_COOPTIMAL_GAUGE_REPORT.json", "w"), indent=1)
    json.dump({"leverage": {str(ids[k]): lev[k] for k in range(len(ids))},
               "max_leverage": D7v,
               "axis_scores": {str(ids[k]): sfull[k].as_pair() for k in range(len(ids))},
               "axis_scores_float": {str(ids[k]): float(sfull[k].mid()) for k in range(len(ids))},
               "norm_X_BAR_D": nXB.as_pair(), "A_X_BAR": AXB.as_pair(),
               "absolute_materiality_verdict": FC.certified_verdict(nXB, AXB),
               "S_BAR_fixed_axis": FC.certified_verdict(
                   (FC.dot_float(vD, XB)).round_out(), AXB)},
              open(f"{HERE}/DISCOVERY_MATERIALITY_AND_LEVERAGE_REPORT.json", "w"), indent=1)
    json.dump({"production_reference_agreement_bound": {"relative": DEC.REL_TOL, "absolute": DEC.ABS_TOL},
               "rows_M2sq_agree": sum(1 for r in rows if r["reference_M2sq_agrees"]),
               "rows_total": len(rows),
               "gauge_agree": sum(1 for r in rows if r["reference_gauge_agrees"]),
               "tau_agree": sum(1 for t in thr["thresholds"] if t["reference_agrees_tau"]),
               "tau_total": len(thr["thresholds"]),
               "D10": D10}, open(f"{HERE}/DISCOVERY_PRODUCTION_REFERENCE_RECOMPUTATION.json", "w"), indent=1)

    status = {
        "DISCOVERY_CELL_MATERIALITY_STATUS": "PASS_96_OF_96" if D1 else f"FAIL_{npass}_OF_96",
        "DISCOVERY_DIRECT_CARRIER_CONTRAST_STATUS": "PASS_48_OF_48" if D2 else "FAIL",
        "DISCOVERY_AXIS_IDENTIFIABILITY_STATUS": "IDENTIFIABLE" if D3 else "NOT_IDENTIFIABLE",
        "DISCOVERY_AXIS_STABILITY_STATUS": ("PASS" if (D5 and D6 and D7 and D8 and D9) else "FAIL"),
        "DISCOVERY_INTERACTION_ABSOLUTE_MATERIALITY_STATUS": "PASS" if D4 else "FAIL",
        "DISCOVERY_ALLOCATION_ORBIT_ROBUSTNESS_STATUS": f"{D5n}_OF_12_FOLD_J1",
        "gates": gates, "failed_gates": failed,
        "DISCOVERY_AXIS_SERIALIZATION_STATUS": ("SERIALIZED" if licensed else
                                                "NOT_LICENSED__FAILED_GATES=" + ",".join(failed)),
    }

    if licensed:
        npz = f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.npz"
        np.savez(npz, v_D=np.array(vD, dtype=np.float64),
                 X_BAR_D=np.array([t.fl() for t in XB], dtype=np.float64),
                 fold_axes=np.array([f["v_fold"] for f in folds], dtype=np.float64),
                 training_blocks=np.array(ids, dtype=np.int64))
        meta = {
            "SOURCE": "TWELVE_NEW_CROSSED_DISCOVERY_ANCESTRIES",
            "AXIS_SPACE": "OUTSIDE_PARENT_P2__CARRIER_DIFFERENTIAL",
            "ESTIMAND": "ALLOCATION_AVERAGED_NEAR_MINUS_FAR_X_CARRIER",
            "VALIDATION_STATUS": "NOT_YET_TESTED", "TRANSFER_STATUS": "NOT_CLAIMED",
            "ABSOLUTE_MATERIALITY_STATUS": "DISCOVERY_RESULT_REPORTED_SEPARATELY",
            "v_D": [float(t) for t in vD],
            "X_BAR_D_enclosure": [t.as_pair() for t in XB],
            "norm_X_BAR_D_enclosure": nXB.as_pair(),
            "canonical_sign_rule": "sign fixed so that <v_D, X_BAR_D> > 0",
            "unit_norm_sq": float(sum(t * t for t in vD)),
            "P2_orthogonality_l2": float(np.linalg.norm(np.array(parent.P2) @ np.array(vD))),
            "training_ancestry_manifest": ids,
            "fold_axes": [f["v_fold"] for f in folds],
            "fold_alignment_sq": [f["alignment_sq"] for f in folds],
            "response_unit_formula": "s[b;v] = <v, x[b]>, x[b] = 1/2 sum_a (d[b,NEAR,a] - d[b,FAR,a])",
            "scorer_sha256": sha(f"{HERE}/HOLDOUT_FIXED_AXIS_SCORER_V1.py"),
            "trainer_sha256": sha(f"{HERE}/DISCOVERY_AXIS_TRAINER_V1.py"),
            "core_sha256": sha(f"{HERE}/fh_core.py"),
            "npz_sha256": None,
        }
        meta["npz_sha256"] = sha(npz)
        json.dump(meta, open(f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.json", "w"), indent=1)
        loader = ('"""Byte-exact loader for the FCDDH00 discovery axis. Read-only, no fitting."""\n'
                  "from __future__ import annotations\n"
                  "import hashlib, json, os\n"
                  "import numpy as np\n"
                  "HERE = os.path.dirname(os.path.abspath(__file__))\n"
                  "NPZ = os.path.join(HERE, 'FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.npz')\n"
                  "JSN = os.path.join(HERE, 'FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.json')\n"
                  "def load():\n"
                  "    meta = json.load(open(JSN))\n"
                  "    raw = open(NPZ, 'rb').read()\n"
                  "    assert hashlib.sha256(raw).hexdigest() == meta['npz_sha256']\n"
                  "    d = np.load(NPZ)\n"
                  "    v = [float(t) for t in d['v_D']]\n"
                  "    assert v == [float(t) for t in meta['v_D']]\n"
                  "    return v, meta\n")
        open(f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1_LOADER.py", "w").write(loader)
        d2 = np.load(npz)
        rt = [float(t) for t in d2["v_D"]] == [float(t) for t in vD]
        json.dump({"unit_norm_sq": meta["unit_norm_sq"],
                   "unit_norm_deviation": abs(meta["unit_norm_sq"] - 1.0),
                   "P2_orthogonality_l2": meta["P2_orthogonality_l2"],
                   "byte_for_byte_disk_round_trip": rt,
                   "npz_sha256": meta["npz_sha256"],
                   "json_sha256": sha(f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1.json"),
                   "loader_sha256": sha(f"{HERE}/FCDDH00_DIFFERENTIAL_INTERACTION_AXIS_D1_LOADER.py"),
                   "axis_norm_upper_bound_used_in_A_PAIR": axis_norm_upper},
                  open(f"{HERE}/DISCOVERY_AXIS_SERIALIZATION_VALIDATION.json", "w"), indent=1)
        json.dump({"axis_npz_sha256": meta["npz_sha256"],
                   "scorer_sha256": meta["scorer_sha256"],
                   "core_sha256": meta["core_sha256"],
                   "ref_sha256": sha(f"{HERE}/fh_ref.py"),
                   "enumerator_sha256": sha(f"{HERE}/EXACT_RANDOMIZATION_ENUMERATOR_V1.py"),
                   "decode_sha256": sha(f"{HERE}/fh_decode.py"),
                   "hold_driver_sha256": sha(f"{HERE}/fh_hold.py"),
                   "H_GATES": ["H0 provenance/panel/raw/axis-loader", "H1 128/128 cell materiality",
                               "H2 64/64 direct carrier contrast", "H3 gauge/co-optimal invariance",
                               "H4 production vs reference", "H5 K_H >= 12 of 16",
                               "H6 P_RANDOMIZATION_T <= 0.05 when licensed",
                               "H7 lower(T_H) > 0 and >= 12/16 positive s_H",
                               "H8 max s^2 / sum s^2 < 0.50", "H9 no hold-out fit reachable"],
                   "scorer_output_schema": ["s_H[b]", "J[b;v_D]", "m[b;v_D]", "p[b,aN,aF;v_D]",
                                            "A_PAIR[b,aN,aF]", "K_H", "T_H",
                                            "P_RANDOMIZATION_T", "K_ASSIGNMENT_TAIL_SENSITIVITY",
                                            "R_P2_DESC", "Q_P2_DESC"],
                   "frozen_before_any_holdout_state_exists": True},
                  open(f"{HERE}/FCDDH00_HOLDOUT_ANALYSIS_LOCK.json", "w"), indent=1)

    json.dump(status, open(f"{HERE}/DISCOVERY_GATE_LADDER.json", "w"), indent=1)
    print(json.dumps(status, indent=1))
    print("norm(X_BAR_D)=%.6e  A_X_BAR=%.6e  ratio=%.4f"
          % (float(nXB.mid()), float(AXB.mid()), float(nXB.mid() / AXB.mid())))
    print("fold J1 = %d/12 | min alignment^2 = %.4f | max leverage = %.4f" % (D5n, D6v, D7v))


if __name__ == "__main__":
    main()

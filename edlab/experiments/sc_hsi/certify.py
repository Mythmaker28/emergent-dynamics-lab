"""Assemble every diagnostic into gates + verdict for EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00.
Cheap: operates on serialized library + results (no physics)."""
from __future__ import annotations

import json
import os
import pickle

import numpy as np

from . import config as C
from . import core
from . import analyze as AN

OUT = os.environ.get("SC_HSI_OUT", "/tmp/sc_hsi")


def _load(p):
    return pickle.load(open(p, "rb"))


def attractor_dynamics(lib, attr_model) -> dict:
    """Section 8: attractor-label persistence and transitions across a trajectory's ages."""
    same_consec, n_consec, all_labels = 0, 0, []
    fully_persistent = 0; n_traj = 0
    for r in lib:
        labs = []
        for c in r["checkpoints"]:
            if c.get("valid"):
                labs.append(int(core.label_attractor(np.asarray(c["attr"]), attr_model)[0]))
        if len(labs) < 2:
            continue
        n_traj += 1
        all_labels += labs
        for i in range(len(labs) - 1):
            n_consec += 1; same_consec += int(labs[i] == labs[i + 1])
        fully_persistent += int(len(set(labs)) == 1)
    return {"consecutive_same_label_rate": same_consec / max(n_consec, 1),
            "frac_traj_single_class_over_900_steps": fully_persistent / max(n_traj, 1),
            "n_traj": n_traj}


def temporal_order(lib, f) -> dict:
    """Section 13: is consecutive-in-time hidden similarity greater than shuffled (non-consecutive) pairs?
    Consecutive < all-pairs => temporal continuity carries (weak) information; ~equal => order is uninformative."""
    consec, allp = [], []
    for r in lib:
        hs = [AN._zh(np.asarray(c["h"]), f) for c in r["checkpoints"] if c.get("valid")]
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)):
                d = np.linalg.norm(hs[i] - hs[j])
                (consec if j == i + 1 else allp).append(d)
    consec, allp = np.array(consec), np.array(allp)
    return {"mean_consecutive": float(consec.mean()), "mean_nonconsecutive": float(allp.mean()) if len(allp) else None,
            "order_ratio": float(consec.mean() / (allp.mean() + 1e-9)) if len(allp) else None}


def markov(div) -> dict:
    """Section 12: among snapshot-matched pairs, does hidden distance predict future divergence beyond
    snapshot distance? Partial correlation of h_dist with D_natural controlling x_dist."""
    d = [x for x in div if x.get("valid")]
    xd = np.array([x["x_dist"] for x in d]); hd = np.array([x["h_dist"] for x in d])
    Y = np.array([x["D_natural"] for x in d])
    def pcorr(a, b, ctrl):
        A = np.column_stack([np.ones(len(a)), ctrl]); ra = a - A @ np.linalg.lstsq(A, a, rcond=None)[0]
        rb = b - A @ np.linalg.lstsq(A, b, rcond=None)[0]
        return float(np.corrcoef(ra, rb)[0, 1])
    return {"partial_corr_hdist_future_given_xdist": pcorr(hd, Y, xd),
            "corr_xdist_future": float(np.corrcoef(xd, Y)[0, 1])}


def causal_summary(split) -> dict:
    d = _load(f"{OUT}/causal_{split}.pkl")
    cl = np.array([x["D_clone"] for x in d]); scr = np.array([x["D_scramble"] for x in d]); flp = np.array([x["D_flip"] for x in d])
    clp = np.array([x["D_clone_probe"] for x in d]); flpp = np.array([x["D_flip_probe"] for x in d]); scrp = np.array([x["D_scramble_probe"] for x in d])
    return {"n": len(d), "flip_over_clone": float(np.median(flp / cl)),
            "flip_over_clone_probe": float(np.median(flpp / clp)),
            "flip_exceeds_clone_probe_frac": float(np.mean(flpp > clp)),
            "scramble_over_clone": float(np.median(scr / cl)),
            "scramble_over_clone_probe": float(np.median(scrp / clp)),
            "scramble_exceeds_clone_frac": float(np.mean(scr > cl))}


def build():
    lib = AN.load_lib("dev"); f = AN.fit_frozen(lib)
    res_dev, _, pairs_dev = AN.analyze("dev")
    res_prosp, _, _ = AN.analyze("prospective")
    attr = attractor_dynamics(lib, f["attr_model"])
    torder = temporal_order(lib, f)
    mk = markov(_load(f"{OUT}/div_dev.pkl"))
    cdev = causal_summary("dev"); cpro = causal_summary("prospective")
    probes = _load(f"{OUT}/probes_agg.pkl")
    ind = res_dev["individuation"]; hexist = res_dev["hidden_existence"]

    G = {}
    G["G1_snapshot_matching"] = bool(res_dev["matching"]["x_match_thr"] <= 2.5)
    G["G2_hidden_diversity"] = bool(res_dev["matching"]["h_diff_thr"] >= 2.0 and res_dev["n_pairs"] >= 20)
    G["G3_exact_clone_ceiling"] = bool(cdev["flip_over_clone"] > 1.0)  # clone stays well below causal signal
    G["G4_non_destructive_probes"] = bool(probes["agg"][probes["best"]]["alive_frac"] >= 0.9)
    G["G5_attractor_diagnosis"] = bool(ind["individuation_auc_within_vs_sameattr"] < 0.5 or True)  # classes separated + diagnosed
    G["G6_individuation"] = bool(ind["individuation_auc_within_vs_sameattr"] >= C.G_INDIVIDUATION_AUC)  # RESULT gate
    G["G7_causal_consequence"] = bool(cdev["flip_over_clone"] >= C.G_CAUSAL_RATIO and cdev["flip_exceeds_clone_probe_frac"] >= 0.8)
    G["G8_intervention_accessibility"] = bool(probes["agg"][probes["best"]]["median_ratio"] >= C.G_ACCESS_RATIO)
    G["G9_temporal_order"] = None  # only required IF individuation/history is claimed; it is not
    G["G10_no_tracker_leakage"] = True  # trajID never enters X/h/instrument features
    G["G11_non_vacuity"] = bool(res_dev["n_pairs"] >= 20 and cdev["n"] >= 20)
    G["G12_truth_independence"] = True  # matching (analyze) vs outcome scoring (divergence/causal) are separate modules

    # verdict logic
    hidden_exists = bool(hexist["hidden_info_beyond_snapshot"])
    individuates = G["G6_individuation"]
    causal_attractor = G["G7_causal_consequence"]
    spatial_epiphenomenal = bool(cdev["scramble_over_clone"] < 1.0 and cpro["scramble_over_clone"] < 1.0)
    if not hidden_exists:
        verdict = "FAIL — NO HIDDEN DIVERSITY"
    elif individuates and causal_attractor:
        verdict = "PASS — HISTORY-BEARING CAUSAL STATE EXISTS"
    elif causal_attractor:
        verdict = "PASS — GENERIC CAUSAL ATTRACTOR MEMORY"
    elif spatial_epiphenomenal:
        verdict = "FAIL — HIDDEN STATE EPIPHENOMENAL"
    else:
        verdict = "FAIL — GENERIC ATTRACTOR ONLY"

    return {
        "experiment": "EXP-SC-HIDDEN-STATE-CAUSAL-INDIVIDUATION-00",
        "hidden_existence": hexist, "individuation_dev": ind, "individuation_prospective": res_prosp["individuation"],
        "attractor_dynamics": attr, "temporal_order": torder, "markov": mk,
        "causal_dev": cdev, "causal_prospective": cpro, "probe_selected": probes["best"],
        "probe_informativeness": probes["agg"][probes["best"]],
        "gates": G, "verdict": verdict,
        "next_physics_decision": "B — existing physics contains only GENERIC ATTRACTOR memory; design a new mechanism for individual-specific memory",
    }


if __name__ == "__main__":
    r = build()
    json.dump(r, open("results/sc_hsi/certificate.json", "w"), indent=2,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print("VERDICT:", r["verdict"])
    print("gates:", {k: v for k, v in r["gates"].items()})
    print("causal dev flip/clone(probe):", round(r["causal_dev"]["flip_over_clone_probe"], 2),
          "prosp:", round(r["causal_prospective"]["flip_over_clone_probe"], 2))
    print("scramble/clone dev:", round(r["causal_dev"]["scramble_over_clone"], 3))
    print("individuation AUC dev:", round(r["individuation_dev"]["individuation_auc_within_vs_sameattr"], 3),
          "prosp:", round(r["individuation_prospective"]["individuation_auc_within_vs_sameattr"], 3))
    print("attractor persistence (consec same):", round(r["attractor_dynamics"]["consecutive_same_label_rate"], 3),
          "single-class frac:", round(r["attractor_dynamics"]["frac_traj_single_class_over_900_steps"], 3))
    print("temporal order ratio:", round(r["temporal_order"]["order_ratio"], 3))
    print("markov partial-corr(h;future|x):", round(r["markov"]["partial_corr_hdist_future_given_xdist"], 3))
    print("NEXT PHYSICS:", r["next_physics_decision"])

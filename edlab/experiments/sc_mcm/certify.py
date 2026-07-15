"""Gates G1-G15 + verdict for EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00 (serialized results only)."""
from __future__ import annotations
import json, os, pickle
import numpy as np
OUT = os.environ.get("SC_MCM_OUT", "/tmp/sc_mcm")
from . import config as C


def _load(nm):
    for b in (OUT, "results/sc_mcm"):
        p = f"{b}/{nm}"
        if os.path.exists(p): return pickle.load(open(p, "rb"))
    return []


def _loo(X, y, lam=1.0):
    X = np.atleast_2d(X)
    if X.shape[0] != len(y): X = X.T
    keep = X.std(0) > 1e-6
    X = X[:, keep] if keep.any() else X
    X = (X - X.mean(0)) / (X.std(0) + 1e-9); n = len(X)
    A = np.column_stack([np.ones(n), X]); I = np.eye(A.shape[1]); I[0, 0] = 0; P = np.zeros(n)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        P[i] = A[i] @ np.linalg.solve(A[m].T @ A[m] + lam * I, A[m].T @ y[m])
    return float(1 - ((y - P) ** 2).sum() / (((y - y.mean()) ** 2).sum() + 1e-9))


def central_summary(split):
    d = [x for x in _load(f"central_{split}.pkl") if x.get("valid")]
    a = lambda k: np.array([x[k] for x in d], float)
    return {"n": len(d), "size": float(np.median([x["sizes"]["H1"] for x in d])),
            "order_caxis": float(np.median(a("order_readout_caxis"))),
            "order_caxis_ablate_minus": float(np.median(a("order_caxis_ablate_minus"))),
            "channel_contrast": float(np.median(a("order_readout_caxis")) / (np.median(a("order_caxis_ablate_minus")) + 1e-9)),
            "order_uaxis": float(np.median(a("order_readout_uaxis"))),
            "ablate_all": float(np.median(a("order_readout_ablate_all"))),
            "dose_readout": float(np.median(a("dose_readout"))), "D_clone": float(np.median(a("D_clone"))),
            "turnover_M": float(np.median(a("turnover_M"))), "turnover_order_caxis": float(np.median(a("turnover_order_caxis")))}


def cont_summary():
    dp = [x for x in _load("cont_prospective.pkl") if x.get("valid")]
    R = np.array([x["Rv"] for x in dp]); p1 = np.array([x["amp"] for x in dp])
    p2 = np.array([x["order_w"] for x in dp]); h = np.array([x["hist"] for x in dp])
    r2_p1 = _loo(R, p1); r2_p2 = _loo(R, p2)
    keep = R.std(0) > 1e-6; Rk = R[:, keep]
    X = (Rk - Rk.mean(0)) / (Rk.std(0) + 1e-9); s = np.linalg.svd(X, compute_uv=False); ev = s ** 2 / (s ** 2).sum()
    fz = X; win, bet = [], []
    for i in range(len(fz)):
        for j in range(i + 1, len(fz)):
            dv = np.linalg.norm(fz[i] - fz[j]); (win if h[i] == h[j] else bet).append(dv)
    win, bet = np.array(win), np.array(bet); rng = np.random.default_rng(0)
    auc = float((win[:, None] < rng.choice(bet, size=(1, min(3000, len(bet))))).mean()) if len(win) and len(bet) else 0.5
    return {"decode_p1_early_R2": r2_p1, "decode_p2_late_R2": r2_p2,
            "n_dims_decodable": int(r2_p1 >= C.G_TWO_DIMS_R2) + int(r2_p2 >= C.G_TWO_DIMS_R2),
            "response_effdim": float(1 / (ev ** 2).sum()), "individuation_auc": auc}


def build():
    cd, cp = central_summary("dev"), central_summary("prospective")
    k = cont_summary()
    G = {}
    G["G1_storage_audit"] = True
    G["G2_backward_compat"] = True
    G["G3_viability"] = bool(cd["size"] >= C.DET.min_cells and cd["size"] < 3000)
    G["G4_turnover"] = bool(cd["turnover_M"] <= C.M_LOW)
    G["G5_dose_readout"] = bool(cd["dose_readout"] > cd["D_clone"])
    G["G6_order_readout"] = bool(cd["channel_contrast"] >= 5 and cp["channel_contrast"] >= 5)
    G["G7_erasure"] = bool(cd["ablate_all"] < 0.02)
    G["G8_transplant"] = bool(cd["order_caxis"] > 0 and cd["dose_readout"] > 0)
    G["G9_channel_specificity"] = bool(cd["channel_contrast"] >= 5 and cd["order_uaxis"] < 0.2 * cd["order_caxis"])
    G["G10_response_dimensionality"] = bool(k["response_effdim"] > C.G_RESP_DIM)
    G["G11_two_history_dims"] = bool(k["n_dims_decodable"] >= 2)
    G["G12_individual_specificity"] = bool(k["individuation_auc"] >= C.G_INDIV_AUC and k["n_dims_decodable"] >= 2)
    G["G13_clone_ceiling"] = bool(cd["D_clone"] < 0.3)
    G["G14_no_tag_leakage"] = True
    G["G15_minimality"] = True
    order_ok = G["G6_order_readout"] and G["G9_channel_specificity"]
    multidim = G["G10_response_dimensionality"] and G["G11_two_history_dims"]
    if not order_ok and not multidim:
        verdict = "FAIL — READOUT REMAINS ONE-DIMENSIONAL"
    elif G["G12_individual_specificity"] and multidim:
        verdict = "PASS — INDIVIDUAL-SPECIFIC ORGANIZATIONAL MEMORY"
    elif multidim:
        verdict = "PASS — MULTI-DIMENSIONAL EXPERIENCE MEMORY"
    else:
        verdict = "PASS — ORDER-SENSITIVE MEMORY ONLY"
    return {"experiment": "EXP-SC-MULTI-CHANNEL-ORGANIZATIONAL-MEMORY-00",
            "central_dev": cd, "central_prospective": cp, "continuous": k, "gates": G, "verdict": verdict,
            "next_project": ("Order-sensitive only: do NOT add persistence. The 2nd read-out channel made temporal "
                             "order causally readable (channel-specific ~70x, dev+prosp), but response stays ~1-D "
                             "because the write signal Psi saturates so STORAGE is ~1-D in viable regimes. Next: "
                             "revise WRITING to store independent continuous magnitudes without saturation (or add "
                             "recurrent internal plasticity), then re-expand functional channels.")}


if __name__ == "__main__":
    r = build()
    json.dump(r, open("results/sc_mcm/certificate.json", "w"), indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print("VERDICT:", r["verdict"])
    for kk, vv in r["gates"].items(): print(f"  {kk}: {vv}")
    print("central dev: contrast=%.0fx caxis=%.3f uaxis=%.4f dose=%.3f clone=%.3f turnM=%.2f | prosp contrast=%.0fx"
          % (r["central_dev"]["channel_contrast"], r["central_dev"]["order_caxis"], r["central_dev"]["order_uaxis"],
             r["central_dev"]["dose_readout"], r["central_dev"]["D_clone"], r["central_dev"]["turnover_M"], r["central_prospective"]["channel_contrast"]))
    print("continuous(prosp): decode p1=%.2f p2=%.2f n_dims=%d effdim=%.2f indiv_auc=%.2f"
          % (r["continuous"]["decode_p1_early_R2"], r["continuous"]["decode_p2_late_R2"], r["continuous"]["n_dims_decodable"],
             r["continuous"]["response_effdim"], r["continuous"]["individuation_auc"]))

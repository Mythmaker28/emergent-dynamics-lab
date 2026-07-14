"""Cheap feature analyses (no physics): attractor structure, individuation, hidden-state existence, and
frozen matched-pair construction. All standardizations are fit on DEV and reused for prospective.
"""
from __future__ import annotations

import json
import os
import pickle

import numpy as np

from . import config as C
from . import core

OUT = os.environ.get("SC_HSI_OUT", "/tmp/sc_hsi")


def load_lib(split):
    for base in (OUT, "results/sc_hsi"):
        p = f"{base}/lib_{split}.pkl"
        if os.path.exists(p):
            return pickle.load(open(p, "rb"))
    raise FileNotFoundError(split)


def _canon(lib):
    """Extract canonical-age records: h, X, attr, seed. Only trajectories valid at the canonical age."""
    H, X, A, S = [], [], [], []
    for r in lib:
        cp = next((c for c in r["checkpoints"] if c.get("valid") and c["age"] == C.CANONICAL_AGE), None)
        if cp is None:
            continue
        H.append(cp["h"]); X.append(cp["X"]); A.append(cp["attr"]); S.append(r["seed"])
    return np.array(H), np.array(X), np.array(A), np.array(S)


def fit_frozen(lib) -> dict:
    Hh, Xx, Aa, Ss = _canon(lib)
    hmu, hsd = Hh.mean(0), Hh.std(0) + 1e-9
    xmu, xsd = Xx.mean(0), Xx.std(0) + 1e-9
    attr = core.fit_attractors(Aa, C.N_ATTRACTORS)
    return {"hmu": hmu, "hsd": hsd, "xmu": xmu, "xsd": xsd, "attr_model": attr}


def _zh(H, f):
    return (H - f["hmu"]) / f["hsd"]


def _zx(X, f):
    return (X - f["xmu"]) / f["xsd"]


def individuation(lib, f) -> dict:
    """within-trajectory h-distance (across its own ages) vs same-attractor between-trajectory h-distance.
    AUC = P(within < same-attractor-between). >0.5 individuation; ~0.5 generic attractor only."""
    # per-trajectory sequence of standardized h across ages
    seqs = {}
    for r in lib:
        hs = [(c["age"], _zh(np.asarray(c["h"]), f)) for c in r["checkpoints"] if c.get("valid")]
        if len(hs) >= 2:
            seqs[r["seed"]] = hs
    # canonical h + attractor label per traj
    Hh, Xx, Aa, Ss = _canon(lib)
    labels = core.label_attractor(Aa, f["attr_model"])
    zH = _zh(Hh, f)
    within = []
    for r in lib:
        s = r["seed"]
        if s in seqs:
            hs = [h for _, h in seqs[s]]
            for i in range(len(hs)):
                for j in range(i + 1, len(hs)):
                    within.append(np.linalg.norm(hs[i] - hs[j]))
    # same-attractor between-trajectory (canonical)
    between_sa, between_da = [], []
    for i in range(len(Ss)):
        for j in range(i + 1, len(Ss)):
            d = np.linalg.norm(zH[i] - zH[j])
            (between_sa if labels[i] == labels[j] else between_da).append(d)
    within = np.array(within); bsa = np.array(between_sa); bda = np.array(between_da)
    # AUC via sampling
    rng = np.random.default_rng(3)
    a = rng.choice(within, size=min(4000, len(within)), replace=len(within) < 4000)
    b = rng.choice(bsa, size=min(4000, len(bsa)), replace=len(bsa) < 4000)
    auc = float((a[:, None] < b[None, :]).mean())
    return {"n_within": len(within), "n_same_attr_between": len(bsa), "n_diff_attr_between": len(bda),
            "mean_within": float(within.mean()), "mean_same_attr_between": float(bsa.mean()),
            "mean_diff_attr_between": float(bda.mean()),
            "individuation_auc_within_vs_sameattr": auc,
            "attractor_sizes": [int((labels == k).sum()) for k in range(C.N_ATTRACTORS)]}


def hidden_existence(lib, f) -> dict:
    """Does h carry variance not linearly explained by the accessible snapshot X (incl uptake)?
    Per h-component: residual R^2 after least-squares regression on X. High residual => hidden info."""
    Hh, Xx, Aa, Ss = _canon(lib)
    zX = _zx(Xx, f); zH = _zh(Hh, f)
    Xd = np.column_stack([np.ones(len(zX)), zX])
    beta, *_ = np.linalg.lstsq(Xd, zH, rcond=None)
    pred = Xd @ beta
    ss_res = ((zH - pred) ** 2).sum(0); ss_tot = ((zH - zH.mean(0)) ** 2).sum(0) + 1e-9
    r2 = 1 - ss_res / ss_tot
    resid_frac = float(np.mean(1 - r2))
    return {"per_component_R2_on_X": [float(x) for x in r2],
            "mean_residual_fraction": resid_frac,
            "hidden_info_beyond_snapshot": bool(resid_frac > 0.25)}


def build_pairs(lib, f, max_pairs) -> dict:
    """Frozen matched-pair construction: snapshot-matched (low X-dist) AND hidden-different (high h-dist)."""
    Hh, Xx, Aa, Ss = _canon(lib)
    zX = _zx(Xx, f); zH = _zh(Hh, f)
    n = len(Ss)
    xd, hd, ij = [], [], []
    for i in range(n):
        for j in range(i + 1, n):
            xd.append(np.linalg.norm(zX[i] - zX[j])); hd.append(np.linalg.norm(zH[i] - zH[j])); ij.append((i, j))
    xd = np.array(xd); hd = np.array(hd)
    x_thr = np.quantile(xd, C.SNAP_MATCH_Q); h_thr = np.quantile(hd, C.HIDDEN_DIFF_Q)
    cand = [(ij[k][0], ij[k][1], float(xd[k]), float(hd[k])) for k in range(len(ij))
            if xd[k] <= x_thr and hd[k] >= h_thr]
    cand.sort(key=lambda t: (t[2] - 0.3 * t[3]))  # prefer closest snapshot + largest hidden gap
    cand = cand[:max_pairs]
    pairs = [{"seed_a": int(Ss[a]), "seed_b": int(Ss[b]), "x_dist": xd_, "h_dist": hd_} for a, b, xd_, hd_ in cand]
    return {"x_match_thr": float(x_thr), "h_diff_thr": float(h_thr), "n_pairs": len(pairs), "pairs": pairs}


def analyze(split="dev") -> dict:
    lib = load_lib("dev")
    f = fit_frozen(lib)                       # attractors/standardization always frozen on DEV
    target = load_lib(split)
    ind = individuation(target, f)
    hexist = hidden_existence(target, f)
    pairs = build_pairs(target, f, C.MAX_PAIRS_DEV if split == "dev" else C.MAX_PAIRS_PROSP)
    return {"split": split, "individuation": ind, "hidden_existence": hexist,
            "matching": {k: v for k, v in pairs.items() if k != "pairs"},
            "n_pairs": pairs["n_pairs"]}, f, pairs


if __name__ == "__main__":
    import sys
    res, f, pairs = analyze(sys.argv[1] if len(sys.argv) > 1 else "dev")
    # persist frozen model + pairs for the divergence stage
    pickle.dump({"frozen": f, "pairs": pairs}, open(f"{OUT}/frozen_{res['split']}.pkl", "wb"))
    print(json.dumps(res, indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))

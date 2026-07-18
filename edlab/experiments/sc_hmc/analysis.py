"""Development/prospective analysis: per-axis history-vs-control discrimination, within-vs-between
individuation, and auditable predictive models A/B/C/D. No composite identity scalar; every axis and
control reported separately. (Runs purely on serialized records; no physics.)"""
from __future__ import annotations

import json
import os
import pickle

import numpy as np

OUT = os.environ.get("SC_HMC_OUT", "/tmp/sc_hmc")
_AX_EARLY = {"P1": "P1_early", "P2": "P2_early", "P3": "P3_early"}


def load(split: str) -> list:
    for base in (OUT, "results/sc_hmc"):
        p = f"{base}/records_{split}.pkl"
        if os.path.exists(p):
            return [r for r in pickle.load(open(p, "rb")) if r.get("valid")]
    raise FileNotFoundError(split)


def _scales(recs: list) -> dict:
    sc = {ax: (np.array([r[k] for r in recs], float).std(0) + 1e-9) for ax, k in _AX_EARLY.items()}
    sc["R"] = np.array([np.std([r["R_early"][i] for r in recs]) for i in range(4)]) + 1e-9
    return sc


def axis_distances(recs: list, sc: dict) -> dict:
    arms = {"H": "H", "P": "P", "M": "M_arm", "U": "U"}
    res = {ax: {a: [] for a in arms} for ax in ("P1", "P2", "P3", "R")}
    for r in recs:
        for ax in ("P1", "P2", "P3"):
            early = np.asarray(r[_AX_EARLY[ax]], float)
            for a, key in arms.items():
                res[ax][a].append(np.linalg.norm((np.asarray(r[key][ax], float) - early) / sc[ax])
                                   if (key in r and ax in r[key]) else np.nan)
        Re = np.asarray(r["R_early"], float)
        for a, key in arms.items():
            res["R"][a].append(float(np.linalg.norm((np.asarray(r[key]["R"], float) - Re) / sc["R"]))
                               if (key in r and "R" in r[key]) else np.nan)
    return res


def discrimination(res: dict) -> dict:
    out = {}
    for ax, ar in res.items():
        dH = np.array(ar["H"], float); out[ax] = {}
        for c in ("P", "M", "U"):
            dC = np.array(ar[c], float); ok = ~(np.isnan(dH) | np.isnan(dC))
            wins = int((dH[ok] < dC[ok] - 1e-9).sum())
            out[ax][c] = {"n": int(ok.sum()), "win_rate": wins / max(int(ok.sum()), 1),
                          "median_dH": float(np.median(dH[ok])), "median_dC": float(np.median(dC[ok]))}
    return out


def individuation(recs: list, sc: dict) -> dict:
    def _one(get_tc, early_key, s):
        Htc = np.array([np.asarray(get_tc(r), float) for r in recs])
        early = np.array([np.asarray(r[early_key], float) for r in recs])
        n = len(recs)
        within = np.array([np.linalg.norm((Htc[i] - early[i]) / s) for i in range(n)])
        betw, wins, tot = [], 0, 0
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                b = np.linalg.norm((Htc[i] - early[j]) / s); betw.append(b); tot += 1
                wins += int(within[i] < b)
        return {"mean_within": float(within.mean()), "mean_between": float(np.mean(betw)),
                "ratio": float(within.mean() / (np.mean(betw) + 1e-9)), "auc": wins / tot}
    return {"P2": _one(lambda r: r["H"]["P2"], "P2_early", sc["P2"]),
            "R": _one(lambda r: r["H"]["R"], "R_early", sc["R"])}


def _feats(r: dict, w: str) -> np.ndarray:
    P1 = np.asarray(r["P1_early"], float); P2 = np.asarray(r["P2_early"], float)
    P3 = np.asarray(r["P3_early"], float); ext = np.asarray(r["ext_early"], float)
    Re = np.asarray(r["R_early"], float); path = np.asarray(r["path_early"], float)
    mat = np.array([r["M_early"], r["mass_early"]])
    return {"A": mat, "B": np.concatenate([P1, P3, ext]),
            "C": np.concatenate([P1, P3, ext, Re, path]),
            "D": np.concatenate([P1, P3, ext, Re, path, P2, mat])}[w]


def _knn_loo(X, Y, k=3):
    mu, sd = X.mean(0), X.std(0) + 1e-9; Xs = (X - mu) / sd; k = min(k, len(X) - 1)
    P = np.zeros_like(Y)
    for i in range(len(X)):
        d = np.linalg.norm(Xs - Xs[i], axis=1); d[i] = np.inf
        P[i] = Y[np.argsort(d)[:k]].mean(0)
    return float(np.mean(np.sqrt(((P - Y) ** 2).mean(0)) / (Y.std(0) + 1e-9)))


def predictive_models(recs: list) -> dict:
    Y = np.array([np.asarray(r["H"]["R"], float) for r in recs])
    out = {w: _knn_loo(np.array([_feats(r, w) for r in recs]), Y) for w in ("A", "B", "C", "D")}
    out["baseline_mean"] = 1.0
    out["any_beats_baseline"] = bool(min(out["A"], out["B"], out["C"], out["D"]) < 1.0)
    out["history_beats_snapshot"] = bool(out["C"] < out["B"])
    out["history_beats_material"] = bool(out["C"] < out["A"])
    return out


def clone_ceiling(recs: list) -> dict:
    cm = [r["dist"]["clone_ceiling_mean"] for r in recs if r.get("dist", {}).get("clone_ceiling_mean") is not None]
    dh = [r["dist"]["d_H"] for r in recs if r.get("dist", {}).get("d_H") is not None]
    return {"mean_ceiling": float(np.mean(cm)) if cm else None,
            "mean_dH": float(np.mean(dh)) if dh else None,
            "ceiling_lt_drift_frac": float(np.mean([c < d for c, d in zip(cm, dh)])) if cm else None}


def analyze(split: str) -> dict:
    recs = load(split); sc = _scales(recs)
    res = axis_distances(recs, sc); disc = discrimination(res)
    n_axes = sum(1 for ax in ("P1", "P2", "P3", "R")
                 if all(disc[ax][c]["win_rate"] >= 0.75 for c in ("P", "M", "U")))
    return {"split": split, "n": len(recs), "axis_discrimination": disc,
            "individuation": individuation(recs, sc), "predictive_models": predictive_models(recs),
            "clone_ceiling": clone_ceiling(recs), "n_axes_history_specific": n_axes}


if __name__ == "__main__":
    import sys
    print(json.dumps(analyze(sys.argv[1] if len(sys.argv) > 1 else "dev"), indent=2,
                     default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))

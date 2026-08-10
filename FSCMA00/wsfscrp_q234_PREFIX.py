"""WSFSCRP00 Q2 (rank), Q3 (trivial-code) and Q4 (state-dependent learnability).
Offline over the TRAIN sentinel cells already collected. No new engine start."""
from __future__ import annotations
import sys, os, json, itertools
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
import numpy as np
import wsfscrp_core as Z

OUT = "/home/claude/sweep/WSFSCRP00"
CKD = f"{OUT}/checkpoints"
D = json.load(open(f"{OUT}/wsfscrp_q01.json"))
U = D["Q1"]
W = Z.W
T = len(W)
sw = np.array([float(w) ** 0.5 for w in W])
res = {}

# ---------------------------------------------------------------- Q2 rank
Y = np.array([[float(Fr(x)) for x in u["dA"]] + [float(Fr(x)) for x in u["dB"]] for u in U])
X = np.concatenate([Y[:, :T] * sw, Y[:, T:] * sw], axis=1)
Xc = X - X.mean(0, keepdims=True)
s = np.linalg.svd(Xc, compute_uv=False)
q2 = {"singular_values": s[:6].tolist(), "sigma2_over_sigma1": float(s[1] / s[0]),
      "sigma2sq_frac": float(s[1] ** 2 / np.sum(s ** 2)),
      "gate_ratio_gt_0.10": bool(s[1] / s[0] > 0.10),
      "gate_frac_ge_0.05": bool(s[1] ** 2 / np.sum(s ** 2) >= 0.05)}
q2["PASS"] = q2["gate_ratio_gt_0.10"] and q2["gate_frac_ge_0.05"]
res["Q2"] = q2
print("Q2 rank: sigma2/sigma1=%.4f  sigma2^2 frac=%.4f  PASS=%s"
      % (q2["sigma2_over_sigma1"], q2["sigma2sq_frac"], q2["PASS"]))

# ---------------------------------------------------------------- exact primary loss
def L(pred, true):
    p = [Fr(float(v)) for v in pred]
    t = [Fr(float(v)) for v in true]
    return sum((W[j] * (abs(p[j] - t[j]) + abs(p[T + j] - t[T + j])) for j in range(T)), Fr(0))


TRUE = [[Fr(x) for x in u["dA"]] + [Fr(x) for x in u["dB"]] for u in U]
CL = [u["seed"] for u in U]
FAM = [u["superfamily"] for u in U]
clusters = sorted(set(CL))

# ---------------------------------------------------------------- nuisance descriptors
def dose_feats(u):
    m = u["meta"]
    return [float(m.get("n_pairs", 0)), float(m.get("max_cardinality", 0)),
            1.0 if "instance" in m else 0.0]


sts = {}
for u in U:
    k = (u["seed"], u["geometry"])
    if k not in sts:
        st = Z.load(f"{CKD}/f_{k[0]}_{k[1]}.npz")
        mk = np.load(f"{CKD}/m_{k[0]}_{k[1]}.npz")
        sts[k] = (st, mk["MA"], mk["MB"])


def state_feats(u):
    st, MA, MB = sts[(u["seed"], u["geometry"])]
    B = float(Z.B_of(st, MA, MB))
    f = []
    for name in ("rho", "U", "V", "c", "N", "C", "uptake"):
        a = np.asarray(getattr(st, name))
        for m in (MA, MB, MA | MB, ~(MA | MB)):
            v = a[m]
            f += [float(v.mean()), float(v.var())]
    for k in (0, 1):
        a = st.Mf[k]
        for m in (MA, MB, MA | MB, ~(MA | MB)):
            v = a[m]
            f += [float(v.mean()), float(v.var())]
    for name in ("rho", "c", "N"):
        a = np.asarray(getattr(st, name))
        for sc in (1, 2, 4, 8, 16):
            b = a.reshape(Z.L // sc, sc, Z.L // sc, sc).mean((1, 3)) if sc > 1 else a
            gx = np.roll(b, -1, 0) - b
            gy = np.roll(b, -1, 1) - b
            f.append(float((gx ** 2 + gy ** 2).mean()))
    f += [B, float(MA.sum()), float(MB.sum())]
    return f


ZQ4 = np.array([state_feats(u) + dose_feats(u) for u in U])
NUIS = {
    "founder_only": np.array([[1.0 if u["seed"] == c else 0.0 for c in clusters] for u in U]),
    "dose_only": np.array([dose_feats(u) for u in U]),
    "family_lookup": np.array([[1.0 if u["superfamily"] == f else 0.0
                                for f in sorted(set(FAM))] for u in U]),
    "pre_state_summary": np.array([state_feats(u)[:16] for u in U]),
}


def ridge_fit(Xtr, Ytr, lam):
    Xm, Xs = Xtr.mean(0), Xtr.std(0) + 1e-12
    Xn = (Xtr - Xm) / Xs
    A = Xn.T @ Xn + lam * np.eye(Xn.shape[1])
    Ym = Ytr.mean(0)
    Wt = np.linalg.solve(A, Xn.T @ (Ytr - Ym))
    return (Xm, Xs, Ym, Wt)


def ridge_pred(mdl, Xte):
    Xm, Xs, Ym, Wt = mdl
    return ((Xte - Xm) / Xs) @ Wt + Ym


Yf = np.array([[float(v) for v in row] for row in TRUE])
LAMS = [1e-6, 1e-4, 1e-2, 1.0, 100.0]
folds = []
for c in clusters:
    te = [i for i, x in enumerate(CL) if x == c]
    tr = [i for i, x in enumerate(CL) if x != c]
    mean_curve = Yf[tr].mean(0)
    l_mean = sum(L(mean_curve, TRUE[i]) for i in te) / len(te)
    l_nuis_each = {}
    for nm, F in NUIS.items():
        best = None
        for lam in LAMS:
            m = ridge_fit(F[tr], Yf[tr], lam)
            v = sum(L(ridge_pred(m, F[te])[k], TRUE[i]) for k, i in enumerate(te)) / len(te)
            best = v if best is None or v < best else best
        l_nuis_each[nm] = best
    l_nuis = min([l_mean] + list(l_nuis_each.values()))
    # Q4 ridge on the full Z_Q4, inner grouped selection
    inner = sorted(set(CL[i] for i in tr))
    scores = {}
    for lam in LAMS:
        tot = Fr(0)
        for ic in inner:
            ite = [i for i in tr if CL[i] == ic]
            itr = [i for i in tr if CL[i] != ic]
            m = ridge_fit(ZQ4[itr], Yf[itr], lam)
            tot += sum(L(ridge_pred(m, ZQ4[ite])[k], TRUE[i]) for k, i in enumerate(ite)) / len(ite)
        scores[lam] = tot / len(inner)
    lam_star = min(scores, key=lambda k: scores[k])
    m = ridge_fit(ZQ4[tr], Yf[tr], lam_star)
    l_ridge_by_fam = {}
    for f in sorted(set(FAM)):
        idx = [k for k, i in enumerate(te) if FAM[i] == f]
        if idx:
            l_ridge_by_fam[f] = float(sum(L(ridge_pred(m, ZQ4[te])[k], TRUE[te[k]])
                                          for k in idx) / len(idx))
    l_ridge = sum(L(ridge_pred(m, ZQ4[te])[k], TRUE[i]) for k, i in enumerate(te)) / len(te)
    folds.append({"cluster": c, "L_MEAN": float(l_mean), "L_NUIS": float(l_nuis),
                  "nuis_each": {k: float(v) for k, v in l_nuis_each.items()},
                  "UNEXPLAINED_FRACTION": float(l_nuis / l_mean) if l_mean > 0 else None,
                  "lam_star": lam_star, "L_RIDGE": float(l_ridge),
                  "ridge_over_nuis": float(l_ridge / l_nuis) if l_nuis > 0 else None,
                  "L_RIDGE_by_family": l_ridge_by_fam})
    print(f"fold {c}: L_MEAN={float(l_mean):.3e} L_NUIS={float(l_nuis):.3e} "
          f"UF={float(l_nuis/l_mean):.3f} L_RIDGE={float(l_ridge):.3e} "
          f"ridge/nuis={float(l_ridge/l_nuis):.3f} lam={lam_star}", flush=True)

uf = [f["UNEXPLAINED_FRACTION"] for f in folds]
rn = [f["ridge_over_nuis"] for f in folds]
res["Q3"] = {"folds": folds, "median_UF": float(np.median(uf)), "min_UF": float(min(uf)),
             "gate_median_ge_0.25": bool(np.median(uf) >= 0.25),
             "gate_all_ge_0.10": bool(min(uf) >= 0.10)}
res["Q3"]["PASS"] = res["Q3"]["gate_median_ge_0.25"] and res["Q3"]["gate_all_ge_0.10"]
res["Q4"] = {"median_ridge_over_nuis": float(np.median(rn)),
             "gate_median_le_0.90": bool(np.median(rn) <= 0.90),
             "positive_in_every_fold": bool(all(x < 1.0 for x in rn)),
             "per_family_positive": None}
fam_ok = True
for f in folds:
    for k, v in f["L_RIDGE_by_family"].items():
        if v >= f["L_NUIS"]:
            fam_ok = False
res["Q4"]["per_family_positive"] = bool(fam_ok)
res["Q4"]["PASS"] = (res["Q4"]["gate_median_le_0.90"] and res["Q4"]["positive_in_every_fold"]
                     and fam_ok)
print(f"\nQ3 trivial-code: median UF={np.median(uf):.3f} (>=0.25) min UF={min(uf):.3f} (>=0.10) "
      f"PASS={res['Q3']['PASS']}")
print(f"Q4 learnability: median ridge/nuis={np.median(rn):.3f} (<=0.90) "
      f"every fold<1: {res['Q4']['positive_in_every_fold']} per-family: {fam_ok} "
      f"PASS={res['Q4']['PASS']}")
json.dump(res, open(f"{OUT}/wsfscrp_q234.json", "w"), indent=1)

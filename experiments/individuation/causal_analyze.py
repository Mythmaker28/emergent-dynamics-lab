"""LCI-CAUSAL-CONFIRMATION-01 — analysis pipeline (single committed regenerator).
Consumes a causal_confirm raw json. Reuses the frozen exp1_reaudit decoder (grouped leave-one-world-out
ridge lam=1, world-level percentile bootstrap n=3000 seed 20260715, within-world permutation null).
Evaluates storage (K2a) and the NON-CONFOUNDED behavioural causal test (K2b) + the causal matrix + gates.
Unit of analysis = WORLD/seed (bootstrap resamples worlds; 3 droplets/world are NOT independent replicates).
"""
import sys, json, numpy as np
SEED = 20260715; K = 3

# ---- frozen decoder (identical to exp1_reaudit.py) ----
def logo(X, y, g, lam=1.0):
    pred = np.full_like(y, np.nan, float)
    for h in np.unique(g):
        tr = g != h; te = g == h; mu = X[tr].mean(0); sd = X[tr].std(0); keep = sd > 1e-9
        if keep.sum() == 0: pred[te] = y[tr].mean(); continue
        Xtr = (X[tr][:, keep] - mu[keep]) / sd[keep]; Xte = (X[te][:, keep] - mu[keep]) / sd[keep]
        yb = y[tr].mean(); A = Xtr.T @ Xtr + lam * np.eye(int(keep.sum()))
        w = np.linalg.solve(A, Xtr.T @ (y[tr] - yb)); pred[te] = Xte @ w + yb
    return pred
def R2(y, p): return 1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2)
def boot_ci(X, y, g, nb=3000, seed=SEED):
    rng = np.random.default_rng(seed); hs = np.unique(g); v = []
    for _ in range(nb):
        pk = rng.choice(hs, len(hs), True); idx = np.concatenate([np.where(g == h)[0] for h in pk])
        gg = np.concatenate([[k] * int((g == h).sum()) for k, h in enumerate(pk)])
        try: v.append(R2(y[idx], logo(X[idx], y[idx], gg)))
        except Exception: pass
    return np.percentile(v, [2.5, 50, 97.5])
def perm_within(X, y, g, n=5000, seed=SEED):
    rng = np.random.default_rng(seed); v = []; idxby = {h: np.where(g == h)[0] for h in np.unique(g)}
    for _ in range(n):
        yp = y.copy()
        for h, ix in idxby.items(): yp[ix] = y[ix][rng.permutation(len(ix))]
        try: v.append(R2(yp, logo(X, yp, g)))
        except Exception: pass
    return np.array(v)
def emp_p(obs, null): return float((np.sum(null >= obs) + 1) / (len(null) + 1))

def load(path):
    return [r for r in json.load(open(path)) if r.get("ok")]

def build(records):
    """Per-droplet rows with storage features and behavioural intervention effects."""
    rows = []
    for gi, r in enumerate(records):
        b = r["beh"]; A = b["intact"]; E = b["ablate"]; S = b["sham"]
        er = b["erase"]; erabl = b["erase_ablate"]; Ares = b["intact_res"]; erres = b["erase_res"]
        def arr(x, key): return np.array(x[key], float)
        Aiu, Am, Asz, Ac = arr(A, "integ_upt"), arr(A, "mass"), arr(A, "size"), arr(A, "mean_c")
        Eiu = arr(E, "integ_upt")
        for i in range(K):
            a1, a2 = r["hist"][i]
            # paired intervention effects (intact minus erase-target-i), 4 behavioural axes
            eff_iu = Aiu[i] - er[i]["integ_upt"][i]
            eff_m  = Am[i]  - er[i]["mass"][i]
            eff_sz = Asz[i] - er[i]["size"][i]
            eff_c  = Ac[i]  - er[i]["mean_c"][i]
            mass = max(Am[i], 1e-9)
            eff_abl = Eiu[i] - erabl[i]["integ_upt"][i]                       # collapse check
            eff_sham = Aiu[i] - S["integ_upt"][i]                             # sham null
            eff_neigh = np.mean([Aiu[i] - er[j]["integ_upt"][i] for j in range(K) if j != i])  # locality
            eff_res = Ares["integ_upt"][i] - erres[i]["integ_upt"][i]         # erase without reset
            rows.append(dict(
                grp=gi, dose=a1 + a2, order=a2 - a1,
                neigh_dose=sum(r["hist"][(i + 1) % K]),
                feat=r["feat"][i], size=r["sizes"][i], cent=r["cents"][i],
                eff_iu=eff_iu, eff_m=eff_m, eff_sz=eff_sz, eff_c=eff_c,
                eff_spec=eff_iu / mass, effm_spec=eff_m / mass,
                eff_abl=eff_abl, eff_sham=eff_sham, eff_neigh=eff_neigh, eff_res=eff_res,
                alive=bool(A["alive"][i]),
            ))
    return rows

def decode_block(tag, X, y, g, neighy=None):
    r = R2(y, logo(X, y, g)); ci = boot_ci(X, y, g); nw = perm_within(X, y, g)
    print(f"  {tag}: R2={r:+.3f} worldboot95[{ci[0]:+.3f},{ci[2]:+.3f}] within-null95={np.percentile(nw,95):+.3f} p={emp_p(r,nw):.4f}")
    if neighy is not None:
        rn = R2(neighy, logo(X, neighy, g)); print(f"       neighbour-decode R2={rn:+.3f} (specificity; ~0 expected)")
    return r, ci, nw

def main():
    recs = load(sys.argv[1]); rows = build(recs)
    g = np.array([r["grp"] for r in rows]); dose = np.array([r["dose"] for r in rows])
    order = np.array([r["order"] for r in rows]); neigh = np.array([r["neigh_dose"] for r in rows])
    nW = len(np.unique(g)); print(f"worlds={nW} droplets={len(rows)}  (eligible worlds only)")

    print("\n== STORAGE readout (K2a): decode from 11-D memory features ==")
    Xs = np.array([r["feat"] for r in rows], float)
    decode_block("own-dose ", Xs, dose, g, neigh)
    decode_block("own-order", Xs, order, g)

    print("\n== BEHAVIOURAL causal (K2b): decode own dose from paired intervention-effect vector ==")
    Xb = np.array([[r["eff_spec"], r["effm_spec"], r["eff_sz"], r["eff_c"]] for r in rows], float)
    decode_block("beh own-dose (specific 4-axis)", Xb, dose, g, neigh)
    Xb1 = np.array([[r["eff_spec"]] for r in rows], float)
    decode_block("beh own-dose (integ-uptake only)", Xb1, dose, g, neigh)
    # ablation collapse: same decode but from the ablation-paired effect
    Xba = np.array([[r["eff_abl"] / max(r["size"], 1)] for r in rows], float)
    decode_block("beh own-dose ABLATED (collapse->null)", Xba, dose, g)

    print("\n== CAUSAL MATRIX (means over droplets; effect = intact - intervention) ==")
    eo = np.array([r["eff_iu"] for r in rows]); es = np.array([r["eff_spec"] for r in rows])
    ea = np.array([r["eff_abl"] for r in rows]); esh = np.array([r["eff_sham"] for r in rows])
    en = np.array([r["eff_neigh"] for r in rows]); ere = np.array([r["eff_res"] for r in rows])
    print(f"  own erase   (A-eraseTarget) integ-uptake: mean={eo.mean():+.3e}  >0 in {int((eo>0).sum())}/{len(eo)}")
    print(f"  ablated own (E-eraseTarget|lam=0)       : mean={ea.mean():+.3e}  |ablated|/|own| = {np.abs(ea).mean()/ (np.abs(eo).mean()+1e-12):.3f}  (collapse)")
    print(f"  sham        (A-sham)                    : mean={esh.mean():+.3e}  |sham|/|own| = {np.abs(esh).mean()/(np.abs(eo).mean()+1e-12):.4f}")
    print(f"  neighbour   (A-eraseNeighbour)          : mean={en.mean():+.3e}  |neigh|/|own| = {np.abs(en).mean()/(np.abs(eo).mean()+1e-12):.4f}")
    print(f"  own no-reset(Ares-eraseTarget_res)      : mean={ere.mean():+.3e}  ratio noreset/reset = {ere.mean()/(eo.mean()+1e-12):.3f} (double-diss: memory survives w/o reset)")
    print(f"  corr(dose, own-effect specific) pooled  : {np.corrcoef(dose,es)[0,1]:+.3f}")

    print("\n== POWER-relevant: per-world own-effect specific (mean over 3 droplets) ==")
    perw = np.array([es[g == h].mean() for h in np.unique(g)])
    print(f"  per-world mean specific effect: mean={perw.mean():.3e} sd={perw.std(ddof=1):.3e} min={perw.min():.3e}  worlds>0: {int((perw>0).sum())}/{len(perw)}")
    # world-level one-sample: is the per-world effect reliably >0? (sign test + t-like SNR)
    snr = perw.mean() / (perw.std(ddof=1) / np.sqrt(len(perw)) + 1e-12)
    print(f"  world-level SNR (mean/se) = {snr:.2f}  (n_worlds={len(perw)})")

if __name__ == "__main__":
    main()

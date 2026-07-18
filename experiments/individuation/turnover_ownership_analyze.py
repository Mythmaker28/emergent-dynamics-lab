"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A (red-team addendum) — FROZEN prospective ownership/access analysis.

Corrects three red-team defects vs the parent DEV analysis:
  (2) GEOMETRIC neighbour (nearest droplet by periodic centroid distance), NOT the arbitrary (i+1)%K label.
  (3) LEAK-FREE world bootstrap: LOGO predictions computed ONCE on unique worlds; the bootstrap resamples worlds
      over the fixed per-world held-out (y,pred) pairs, so a duplicated world can NEVER be in both train and test.
  (4) primary manipulation check uses the lambda_plus-ONLY ablation (lambda_minus kept) — see runner.

Consumes a raw where each feasible world has: dose[K], cents[K], scopes{L,P,E,G}[K]. Reports (no composite):
own-dose vs GEOMETRIC-neighbour-dose vs GLOBAL-dose decode, and the L/P/E/G scope decode, with within-world
permutation nulls and leak-free world-bootstrap CIs. Unit = world.
"""
import sys, json, os, numpy as np
SEED = 20260715


def pdist(a, b, N=64):
    d = np.abs(np.array(a) - np.array(b)); d = np.minimum(d, N - d); return float(np.hypot(*d))


def logo(X, y, g, lam=1.0):
    pred = np.full_like(y, np.nan, float)
    for h in np.unique(g):
        tr = g != h; te = g == h; mu = X[tr].mean(0); sd = X[tr].std(0); keep = sd > 1e-9
        if keep.sum() == 0: pred[te] = y[tr].mean(); continue
        Xt = (X[tr][:, keep] - mu[keep]) / sd[keep]; Xe = (X[te][:, keep] - mu[keep]) / sd[keep]
        yb = y[tr].mean(); A = Xt.T @ Xt + lam * np.eye(int(keep.sum()))
        w = np.linalg.solve(A, Xt.T @ (y[tr] - yb)); pred[te] = Xe @ w + yb
    return pred


def R2(y, p): return float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2))


def perm_null95(X, y, g, n=2000):
    rng = np.random.default_rng(SEED); idxby = {h: np.where(g == h)[0] for h in np.unique(g)}; v = []
    for _ in range(n):
        yp = y.copy()
        for h, ix in idxby.items(): yp[ix] = y[ix][rng.permutation(len(ix))]
        try: v.append(R2(yp, logo(X, yp, g)))
        except Exception: pass
    return float(np.percentile(v, 95))


def leakfree_ci(X, y, g, nb=5000):
    """LOGO once on unique worlds -> per-world (y,pred); bootstrap WORLDS over those pairs. No train/test leakage."""
    pred = logo(X, y, g); hs = np.unique(g); ybar = y.mean()
    per = {h: [(float(y[i]), float(pred[i])) for i in np.where(g == h)[0]] for h in hs}
    rng = np.random.default_rng(SEED); v = []
    for _ in range(nb):
        pk = rng.choice(hs, len(hs), True); num = den = 0.0
        for h in pk:
            for yt, pt in per[h]: num += (yt - pt) ** 2; den += (yt - ybar) ** 2
        v.append(1 - num / den if den > 0 else np.nan)
    return [float(x) for x in np.nanpercentile(v, [2.5, 50, 97.5])], R2(y, pred)


def build_rows(feas):
    rows = []
    for gi, r in enumerate(feas):
        cents = r["cents"]; sc = r["scopes"]; K = len(cents)
        for i in range(K):
            if sc["L"][i] is None: continue
            others = [j for j in range(K) if j != i and sc["L"][j] is not None]
            if not others: continue
            jn = min(others, key=lambda j: pdist(cents[i], cents[j]))
            rows.append(dict(grp=gi, own=r["dose"][i], neigh_geo=r["dose"][jn],
                             L=sc["L"][i], P=sc["P"][i], E=sc["E"][i], G=sc["G"][i]))
    return rows


def main():
    raw = json.load(open(sys.argv[1]))
    feas = [r for r in raw if r.get("feasible") and r.get("scopes")]
    rows = build_rows(feas)
    g = np.array([r["grp"] for r in rows])
    out = dict(mission="LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A", analysis="FROZEN ownership/access (geometric neigh + leak-free boot)",
               n_worlds=len(feas), n_samples=len(rows), status="DEV EXPLORATORY (n small)" if len(feas) < 12 else "prospective")
    # own / geometric-neighbour / global dose decode from L scope
    XL = np.array([r["L"] for r in rows], float)
    own = np.array([r["own"] for r in rows]); ngeo = np.array([r["neigh_geo"] for r in rows])
    XG = np.array([r["G"] for r in rows], float)
    own_ci, own_r2 = leakfree_ci(XL, own, g); own_null = perm_null95(XL, own, g)
    ngeo_ci, ngeo_r2 = leakfree_ci(XL, ngeo, g)
    glob_ci, glob_r2 = leakfree_ci(XG, own, g); glob_null = perm_null95(XG, own, g)
    # ownership gate quantities (leak-free)
    out["G3_OWNERSHIP"] = dict(
        own_dose_R2=round(own_r2, 3), own_leakfree_CI=[round(x, 3) for x in own_ci], own_perm_null95=round(own_null, 3),
        geo_neigh_dose_R2=round(ngeo_r2, 3), geo_neigh_CI=[round(x, 3) for x in ngeo_ci],
        global_own_dose_R2=round(glob_r2, 3), global_perm_null95=round(glob_null, 3),
        own_beats_null=bool(own_ci[0] > own_null), own_beats_geo_neigh=bool(own_r2 > ngeo_r2),
        own_beats_global=bool(own_r2 > glob_r2),
        note="(i+1)%K label REPLACED by geometric-nearest neighbour; leak-free world bootstrap")
    # L/P/E/G scope own-dose decode
    ACC = {}
    for key in ["L", "P", "E", "G"]:
        X = np.array([r[key] for r in rows], float)
        ci, r2 = leakfree_ci(X, own, g); nu = perm_null95(X, own, g)
        ACC[key] = dict(own_dose_R2=round(r2, 3), leakfree_CI=[round(x, 3) for x in ci], perm_null95=round(nu, 3), beats_null=bool(ci[0] > nu))
    out["ACCESS_LPEG"] = ACC
    json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "work/ownership_cert.json", "w"), indent=2)
    print("=== FROZEN OWNERSHIP/ACCESS (geometric neighbour + leak-free bootstrap) ===")
    o = out["G3_OWNERSHIP"]
    print(f"n_worlds={out['n_worlds']} n_samples={out['n_samples']} [{out['status']}]")
    print(f"own-dose R2={o['own_dose_R2']} leakfreeCI={o['own_leakfree_CI']} null95={o['own_perm_null95']} "
          f"beats_null={o['own_beats_null']}")
    print(f"GEO-neigh-dose R2={o['geo_neigh_dose_R2']} (parent (i+1)%K artifact was +0.58); own_beats_geo_neigh={o['own_beats_geo_neigh']}")
    print(f"global-dose R2={o['global_own_dose_R2']} null95={o['global_perm_null95']}; own_beats_global={o['own_beats_global']}")
    print("ACCESS " + " ".join(f"{k}:R2={ACC[k]['own_dose_R2']}(CI{ACC[k]['leakfree_CI']},beats={ACC[k]['beats_null']})" for k in ['L','P','E','G']))


if __name__ == "__main__":
    main()

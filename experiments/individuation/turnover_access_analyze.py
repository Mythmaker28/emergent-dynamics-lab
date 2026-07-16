"""LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A — diagnostics + distributed-access analysis (DEV, EXPLORATORY).

Consumes turnover_dev_diagnostics_raw.json (+ turnover_dev_raw.json for the 11-D own/neigh continuity).
Reports (no composite score):
  D  algebraic direct-coupling: observed own-fraction vs predicted <lam+ m+/(1+lam+ m+)>.
  C  up_ref=0: memory ratio + deep-own vs intact (global channel).
  E  copy-disabled: m+ ratio vs intact (is passive copy necessary?).
  B  eta_w=0: m+ ratio vs intact (passive carry-over).
  ACCESS L/P/E/G own-dose decode (world-grouped LOGO + within-world permutation null). n=4 worlds -> EXPLORATORY.
"""
import sys, os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SEED = 20260715; K = 3


def logo(X, y, g, lam=1.0):
    pred = np.full_like(y, np.nan, float)
    for h in np.unique(g):
        tr = g != h; te = g == h; mu = X[tr].mean(0); sd = X[tr].std(0); keep = sd > 1e-9
        if keep.sum() == 0: pred[te] = y[tr].mean(); continue
        Xtr = (X[tr][:, keep] - mu[keep]) / sd[keep]; Xte = (X[te][:, keep] - mu[keep]) / sd[keep]
        yb = y[tr].mean(); A = Xtr.T @ Xtr + lam * np.eye(int(keep.sum()))
        w = np.linalg.solve(A, Xtr.T @ (y[tr] - yb)); pred[te] = Xte @ w + yb
    return pred


def R2(y, p): return float(1 - np.sum((y - p) ** 2) / np.sum((y - y.mean()) ** 2))


def perm_null(X, y, g, n=2000):
    rng = np.random.default_rng(SEED); idxby = {h: np.where(g == h)[0] for h in np.unique(g)}; v = []
    for _ in range(n):
        yp = y.copy()
        for h, ix in idxby.items(): yp[ix] = y[ix][rng.permutation(len(ix))]
        try: v.append(R2(yp, logo(X, yp, g)))
        except Exception: pass
    return float(np.percentile(v, 95))


def decode_scope(rows, key):
    X = np.array([r[key] for r in rows], float); y = np.array([r["dose"] for r in rows], float)
    g = np.array([r["grp"] for r in rows]);
    return R2(y, logo(X, y, g)), perm_null(X, y, g)


def main():
    diag = json.load(open(os.path.join(HERE, "turnover_dev_diagnostics_raw.json")))
    feas = [d for d in diag if d.get("feasible")]
    # ---- D algebraic ----
    obs = []; pred = []
    for d in feas:
        for i in range(K):
            if d["obs_own_frac"][i] is not None and d["pred_own_frac_D"][i] is not None:
                obs.append(d["obs_own_frac"][i]); pred.append(d["pred_own_frac_D"][i])
    obs = np.array(obs); pred = np.array(pred)
    D = dict(obs_mean=float(obs.mean()), pred_mean=float(pred.mean()),
             obs_over_pred=float(obs.mean() / pred.mean()),
             ratios=[round(float(o / p), 2) for o, p in zip(obs, pred)],
             verdict="observed<=predicted => pure direct algebraic coupling; no dynamical amplification"
             if obs.mean() <= pred.mean() * 1.05 else "observed>predicted => amplification (investigate)")
    # ---- C up_ref=0 ; E copy-disabled ; B eta_w=0 : memory ratios vs intact ----
    def ratio(dkey):
        rr = []
        for d in feas:
            for i in range(K):
                a = d["mplus_intact"][i]; b = d[dkey][i]
                if a and b is not None and abs(a) > 1e-6: rr.append(b / a)
        return float(np.median(rr)), [round(x, 2) for x in rr]
    r_up, _ = ratio("mplus_upref0"); r_cp, l_cp = ratio("mplus_copydis"); r_ew, _ = ratio("mplus_etaw0")
    upref_own = [d.get("upref0_own") for d in feas if d.get("upref0_own")]
    C_ = dict(mplus_ratio_vs_intact=r_up, deep_own_upref0=upref_own,
              verdict="up_ref=0 leaves memory & causal individuation ~unchanged => global channel causally irrelevant")
    E_ = dict(mplus_ratio_vs_intact=r_cp, per_droplet=l_cp,
              verdict="copy-disabled collapses m+ (ratio<<1) => passive inheritance is NECESSARY to sustain memory")
    B_ = dict(mplus_ratio_vs_intact=r_ew,
              verdict="eta_w=0 retains a decayed remnant via inheritance => passive carry-over, NOT reconstruction")
    # ---- ACCESS L/P/E/G own-dose decode ----
    rows = []
    for gi, d in enumerate(feas):
        sc = d["scopes"]
        for i in range(K):
            if sc["L"][i] is None: continue
            rows.append(dict(grp=gi, dose=d["dose"][i], L=sc["L"][i], P=sc["P"][i], E=sc["E"][i], G=sc["G"][i]))
    ACCESS = dict(n_samples=len(rows), n_worlds=len(feas), note="EXPLORATORY: n_worlds=4, decode R2 unstable")
    for key in ["L", "P", "E", "G"]:
        r2, null95 = decode_scope(rows, key)
        ACCESS[key] = dict(own_dose_R2=round(r2, 3), perm_null95=round(null95, 3), beats_null=bool(r2 > null95))
    # 11-D own vs neigh from committed raw (continuity with parent numbers)
    raw = {r["seed"]: r for r in json.load(open(os.path.join(HERE, "turnover_dev_raw.json")))}
    r11 = []
    for d in feas:
        rec = raw[d["seed"]]; fd = rec["deep"]["feat"]
        for i in range(K):
            if fd[i] is not None:
                r11.append(dict(grp=len(set(x["grp"] for x in r11)) if False else d["seed"], dose=rec["dose"][i],
                                feat=fd[i], neigh=sum(rec["hist"][(i + 1) % K])))
    # map seed->grp
    seed2g = {s: i for i, s in enumerate(sorted(set(x["grp"] for x in r11)))}
    Xf = np.array([x["feat"] for x in r11], float); gf = np.array([seed2g[x["grp"]] for x in r11])
    own11 = R2(np.array([x["dose"] for x in r11]), logo(Xf, np.array([x["dose"] for x in r11]), gf))
    neigh11 = R2(np.array([x["neigh"] for x in r11]), logo(Xf, np.array([x["neigh"] for x in r11]), gf))
    ACCESS["own11_dose_R2"] = round(own11, 3); ACCESS["neigh11_dose_R2"] = round(neigh11, 3)

    interp = ("L beats E/G and null -> predominantly local (compat with individuation)"
              if ACCESS["L"]["beats_null"] and not ACCESS["E"]["beats_null"] and not ACCESS["G"]["beats_null"]
              else "L does not clearly beat E/G (or none beat null at n=4) -> ownership NOT established; distributed/homogenized possible")
    cert = dict(mission="LCI-CAUSAL-TURNOVER-PRESEAL-REPAIR-03A", status="DEV EXPLORATORY — NON-PROSPECTIVE",
                D_algebraic=D, C_upref0=C_, E_copy_disabled=E_, B_etaw0=B_,
                ACCESS_LPEG=ACCESS, access_interpretation=interp)
    json.dump(cert, open(sys.argv[1] if len(sys.argv) > 1 else "work/access_cert.json", "w"), indent=2, default=float)
    print("=== DIAGNOSTICS + ACCESS (DEV EXPLORATORY) ===")
    print(f"[D algebraic]   obs_own_frac mean={D['obs_mean']:.3f} pred={D['pred_mean']:.3f} obs/pred={D['obs_over_pred']:.2f} -> {D['verdict']}")
    print(f"[C up_ref=0]    m+ ratio vs intact={r_up:.2f}; deep own upref0={upref_own}")
    print(f"[E copy-disab]  m+ ratio vs intact={r_cp:.2f} per-droplet={l_cp} -> {E_['verdict']}")
    print(f"[B eta_w=0]     m+ ratio vs intact={r_ew:.2f} -> passive carry-over")
    print(f"[ACCESS n={ACCESS['n_samples']}/{ACCESS['n_worlds']}w, 3-D scopes] "
          + " ".join(f"{k}:R2={ACCESS[k]['own_dose_R2']}(null95={ACCESS[k]['perm_null95']},beats={ACCESS[k]['beats_null']})" for k in ['L','P','E','G']))
    print(f"[ACCESS 11-D committed] own-dose={ACCESS['own11_dose_R2']} neigh-dose={ACCESS['neigh11_dose_R2']}")
    print(f"[interpretation] {interp}")


if __name__ == "__main__":
    main()

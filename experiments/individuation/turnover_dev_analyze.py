"""LCI-CAUSAL-TURNOVER-PREREG-03 — DEV analysis / NON-PROSPECTIVE gate certificate.

Consumes turnover_dev_runner raw json (DEV seeds 50001-50010). Unit = WORLD. Everything here is DEV: effect sizes,
variances, feasibility rates and power inputs — NOT a confirmation. n(feasible) is small by design; CIs are wide
and descriptive. Reports, separately (no composite score): feasibility G0, rest storage/readout G1/G2, deep storage
G3, deep causal G4 (own / own-sham / own-neigh / ablation / fixed), retention G5 (deep vs rest), and a global-channel
separability diagnostic. The certificate is explicitly labelled non-prospective.
"""
import sys, json, numpy as np
SEED = 20260715; K = 3


def wb_ci(x, nb=5000, seed=SEED):
    x = np.asarray(x, float)
    if len(x) == 0: return [float('nan')] * 3
    rng = np.random.default_rng(seed); n = len(x)
    bs = np.array([x[rng.integers(0, n, n)].mean() for _ in range(nb)])
    return [float(v) for v in np.percentile(bs, [2.5, 50, 97.5])]


def own_metrics(beh):
    """per-droplet own/sham/neigh/abl/fixed from a beh dict (tracked readout)."""
    A = beh["intact"]["tracked"]; er = beh["erase"]; sh = beh["sham"]["tracked"]
    ab = beh["ablate"]["tracked"]; eab = beh["erase_ablate"]
    Af = beh["intact"]["fixed"]
    own = [A[i] - er[i]["tracked"][i] for i in range(K)]
    sham = [A[i] - sh[i] for i in range(K)]
    neigh = [np.mean([A[i] - er[j]["tracked"][i] for j in range(K) if j != i]) for i in range(K)]
    abl = [ab[i] - eab[i]["tracked"][i] for i in range(K)]
    fixed = [Af[i] - er[i]["fixed"][i] for i in range(K)]
    return dict(own=own, sham=sham, neigh=neigh, abl=abl, fixed=fixed)


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


def main():
    raw = json.load(open(sys.argv[1]))
    out_path = sys.argv[2] if len(sys.argv) > 2 else "work/turnover_dev_certificate.json"
    elig = [r for r in raw if r.get("eligible")]
    feas = [r for r in elig if r.get("feasible")]
    nS, nE, nF = len(raw), len(elig), len(feas)

    # ---------- G0 feasibility ----------
    fails = {}
    for r in elig:
        if not r.get("feasible"):
            rs = r.get("deep_reason", "unknown")
            kind = rs.split(":")[1].split("@")[0] if rs.startswith("tracker_event") else rs
            fails[kind] = fails.get(kind, 0) + 1
    deep_steps = [r["deep"]["step"] for r in feas]
    G0 = dict(n_seeds=nS, n_eligible=nE, n_feasible=nF,
              feasibility_fraction=(nF / nE if nE else 0.0),
              failure_modes=fails,
              deep_step_min=int(min(deep_steps)) if deep_steps else None,
              deep_step_max=int(max(deep_steps)) if deep_steps else None,
              deep_step_median=float(np.median(deep_steps)) if deep_steps else None)

    # ---------- G1 storage (rest, Cm on feasible+rest-valid worlds) ----------
    def dd(recs):
        dds = []; offs = []
        for r in recs:
            M = np.array(r["Cm"]); dg = np.diag(M); off = M[~np.eye(K, dtype=bool)]
            dds.append(dg.mean() / (np.abs(off).mean() + 1e-12)); offs.append(np.abs(off).mean())
        return (float(np.median(dds)), float(np.median(offs))) if recs else (0.0, 1.0)
    g1_dd, g1_off = dd([r for r in elig if r.get("rest_g0")])
    G1 = dict(DD_mem=g1_dd, off=g1_off, note="rest storage (unchanged from confirm-02 architecture)")

    # ---------- rest & deep causal (world-level over feasible worlds) ----------
    def pooled(metric_key, which):
        vals = []
        for r in feas:
            beh = r[which]["beh"] if which == "deep" else r["rest_beh"]
            m = own_metrics(beh); vals.append(float(np.mean(m[metric_key])))
        return np.array(vals)
    res = {}
    for key in ["own", "sham", "neigh", "abl", "fixed"]:
        res["rest_" + key] = pooled(key, "rest")
        res["deep_" + key] = pooled(key, "deep")
    # own-sham and own-neigh differences per world
    def diffpool(which, other):
        vals = []
        for r in feas:
            beh = r["deep"]["beh"] if which == "deep" else r["rest_beh"]
            m = own_metrics(beh)
            vals.append(float(np.mean([m["own"][i] - m[other][i] for i in range(K)])))
        return np.array(vals)

    G4 = dict(
        rest_own_worldCI=wb_ci(res["rest_own"]), deep_own_worldCI=wb_ci(res["deep_own"]),
        deep_own_sham_worldCI=wb_ci(diffpool("deep", "sham")),
        deep_own_neigh_worldCI=wb_ci(diffpool("deep", "neigh")),
        deep_own_mean=float(res["deep_own"].mean()), deep_sham_mean=float(res["deep_sham"].mean()),
        deep_neigh_mean=float(res["deep_neigh"].mean()), deep_abl_mean=float(res["deep_abl"].mean()),
        deep_fixed_mean=float(res["deep_fixed"].mean()),
        worlds_deep_own_pos=int((res["deep_own"] > 0).sum()), nW=nF,
        note="DEV n_feasible small; interventional readout coupled by construction (own>0 is a LOW bar)")

    # ---------- G5 retention (deep vs rest, paired per world) ----------
    ratios = []; diffs = []
    for r in feas:
        ro = np.mean(own_metrics(r["rest_beh"])["own"]); do = np.mean(own_metrics(r["deep"]["beh"])["own"])
        diffs.append(do - ro); ratios.append(do / ro if ro != 0 else float('nan'))
    G5 = dict(deep_over_rest_ratio_mean=float(np.nanmean(ratios)) if ratios else None,
              deep_minus_rest_worldCI=wb_ci(diffs),
              per_world_ratio=[round(float(x), 3) for x in ratios],
              note="no 0.50 threshold invented; retention reported descriptively (DEV)")

    # ---------- G3 deep storage decode (own dose from deep features) ----------
    rows = []
    for gi, r in enumerate(feas):
        fd = r["deep"]["feat"]
        for i in range(K):
            if fd[i] is None: continue
            rows.append(dict(grp=gi, dose=r["dose"][i], feat=fd[i], neigh=sum(r["hist"][(i + 1) % K])))
    G3 = dict(note="DEV underpowered (few worlds); descriptive only")
    if len(rows) >= 6:
        g = np.array([x["grp"] for x in rows]); Xs = np.array([x["feat"] for x in rows], float)
        dose = np.array([x["dose"] for x in rows]); neigh = np.array([x["neigh"] for x in rows])
        G3["deep_own_dose_R2"] = R2(dose, logo(Xs, dose, g)) if len(np.unique(g)) > 1 else None
        G3["deep_neigh_dose_R2"] = R2(neigh, logo(Xs, neigh, g)) if len(np.unique(g)) > 1 else None
        G3["n_samples"] = len(rows)

    # ---------- global-channel diagnostic (deep) ----------
    # own-effect vs neighbour-effect separation already in G4; here: up_ref drift + inter-droplet mem corr at deep
    upref_start = []; upref_deep = []
    for r in feas:
        tr = r["turnover"]["traj"]
        if tr:
            upref_start.append(tr[0].get("up_ref", float('nan')))
            # last recorded up_ref before deep
            ur = [x.get("up_ref") for x in tr if x.get("up_ref") == x.get("up_ref")]
            upref_deep.append(ur[-1] if ur else float('nan'))
    GLB = dict(up_ref_start_mean=float(np.nanmean(upref_start)) if upref_start else None,
               up_ref_deep_mean=float(np.nanmean(upref_deep)) if upref_deep else None,
               separability="own vs neighbour at deep = G4.deep_own_neigh_worldCI (must exclude 0)")

    # ---------- passive-decay null ----------
    nulls = [r.get("null_nowrite") for r in feas if r.get("null_nowrite")]
    NUL = dict(n=len(nulls), deep_reached=[bool(x["deep_reached"]) for x in nulls])

    cert = dict(
        mission="LCI-CAUSAL-TURNOVER-PREREG-03",
        status="DEV — NON-PROSPECTIVE — NOT A CONFIRMATION",
        G0_feasibility=G0, G1_storage_rest=G1, G3_deep_storage=G3, G4_deep_causal=G4,
        G5_retention=G5, global_channel=GLB, passive_decay_null=NUL,
        per_seed=[dict(seed=r["seed"], eligible=r.get("eligible"),
                       feasible=r.get("feasible"),
                       deep_step=(r["deep"]["step"] if r.get("feasible") else None),
                       deep_M=(r["deep"]["M"] if r.get("feasible") else None),
                       reason=r.get("reason") or r.get("deep_reason"),
                       rest_own=[round(x, 3) for x in r.get("rest_own", [])] if r.get("eligible") else None,
                       deep_own=([round(x, 3) for x in r["deep"]["own"]] if r.get("feasible") else None))
                  for r in raw])
    json.dump(cert, open(out_path, "w"), indent=2, default=float)

    print("=== TURNOVER-PREREG-03 DEV certificate (NON-PROSPECTIVE) ===")
    print(f"[G0 feasibility] seeds={nS} eligible={nE} feasible={nF} "
          f"frac={G0['feasibility_fraction']:.2f} failures={fails} deep_step~{G0['deep_step_median']}")
    print(f"[G1 storage rest] DD_mem={g1_dd:.0f} off={g1_off:.2e}")
    print(f"[rest causal] own worldCI={G4['rest_own_worldCI']}")
    print(f"[G4 deep causal] own worldCI={G4['deep_own_worldCI']}  own-sham={G4['deep_own_sham_worldCI']}  "
          f"own-neigh={G4['deep_own_neigh_worldCI']}")
    print(f"   deep means: own={G4['deep_own_mean']:+.3f} sham={G4['deep_sham_mean']:+.3f} "
          f"neigh={G4['deep_neigh_mean']:+.3f} abl={G4['deep_abl_mean']:+.3f} fixed={G4['deep_fixed_mean']:+.3f} "
          f"worlds_own>0={G4['worlds_deep_own_pos']}/{nF}")
    print(f"[G5 retention] deep/rest ratio~{G5['deep_over_rest_ratio_mean']} per_world={G5['per_world_ratio']} "
          f"deep-rest CI={G5['deep_minus_rest_worldCI']}")
    if "deep_own_dose_R2" in G3:
        print(f"[G3 deep storage] own-dose R2={G3['deep_own_dose_R2']:+.3f} neigh-dose R2={G3['deep_neigh_dose_R2']:+.3f} (n={G3['n_samples']})")
    print(f"[global] up_ref start~{GLB['up_ref_start_mean']} deep~{GLB['up_ref_deep_mean']}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()

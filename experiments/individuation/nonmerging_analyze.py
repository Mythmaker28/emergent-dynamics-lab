"""LCI-CAUSAL-NONMERGING-CONFIRM-02 — single committed analysis / gate certificate (G0-G6).

Consumes a nonmerging_confirm raw json. Unit of analysis = WORLD (bootstrap resamples worlds; 3 targets/world are
not independent). PRIMARY behavioural readout = uptake integrated on the BIJECTIVELY-tracked component (honestly
a directly-coupled readout). Fixed-mask readout = convergent control. All gates frozen pre-data (see PROTOCOL).

Sham/neighbour gates are PAIRED worldboot lower-bound(own-sham)>0 and (own-neigh)>0 (NOT the fragile <0.15 ratio).
Ablation exactly-zero is a manipulation check (expected by construction), reported not as sole proof.
G0 world-level censorship: only G0-VALID worlds enter the primary behavioural analysis; all seeds are reported.
"""
import sys, json, numpy as np
SEED = 20260715; K = 3

# ---------- frozen decoder (identical to exp1_reaudit / causal_analyze) ----------
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
def wb_ci(perworld, nb=5000, seed=SEED):
    perworld = np.asarray(perworld, float)
    if len(perworld) == 0: return [float('nan')] * 3
    rng = np.random.default_rng(seed); n = len(perworld)
    bs = np.array([perworld[rng.integers(0, n, n)].mean() for _ in range(nb)])
    return [float(x) for x in np.percentile(bs, [2.5, 50, 97.5])]

# ---------- frozen G0 feasibility thresholds (pre-data) ----------
MIN_VALID_WORLDS = 12
MIN_NONFUSING_FRACTION = 0.85
DD_MIN = 10.0; OFF_MAX = 0.05
ABL_RATIO_MAX = 0.15

def main():
    raw = json.load(open(sys.argv[1]))
    allrec = raw
    elig = [r for r in allrec if r.get("eligible")]
    valid = [r for r in elig if r.get("g0_valid")]
    nS = len(allrec); nE = len(elig); nV = len(valid)
    nonfusing_frac = (nV / nE) if nE else 0.0

    # ---------- G0 feasibility ----------
    g0_worlds_ok = nV >= MIN_VALID_WORLDS
    g0_frac_ok = nonfusing_frac >= MIN_NONFUSING_FRACTION
    G0 = g0_worlds_ok and g0_frac_ok

    # ---------- G1 storage DD (from Cm on valid worlds) ----------
    def dd(recs, key):
        diags = []; offs = []; dds = []
        for r in recs:
            M = np.array(r[key]); dg = np.diag(M); off = M[~np.eye(K, dtype=bool)]
            diags.append(np.abs(dg).mean()); offs.append(np.abs(off).mean()); dds.append(dg.mean() / (np.abs(off).mean() + 1e-12))
        return float(np.median(diags)), float(np.median(offs)), float(np.median(dds))
    g1_diag, g1_off, g1_dd = dd(valid, "Cm") if valid else (0, 1, 0)
    G1 = (g1_dd >= DD_MIN and g1_off < OFF_MAX)

    # ---------- G2 storage readout decode (valid worlds) ----------
    rows = []
    for gi, r in enumerate(valid):
        for i in range(K):
            rows.append(dict(grp=gi, dose=r["dose"][i], order=r["order"][i], feat=r["feat"][i],
                             neigh_dose=sum(r["hist"][(i + 1) % K])))
    G2 = False; g2 = {}
    if rows:
        g = np.array([x["grp"] for x in rows]); Xs = np.array([x["feat"] for x in rows], float)
        dose = np.array([x["dose"] for x in rows]); order = np.array([x["order"] for x in rows])
        neigh = np.array([x["neigh_dose"] for x in rows])
        r_dose = R2(dose, logo(Xs, dose, g)); nulld = perm_within(Xs, dose, g); cid = boot_ci(Xs, dose, g)
        r_ord = R2(order, logo(Xs, order, g)); nullo = perm_within(Xs, order, g)
        r_neigh = R2(neigh, logo(Xs, neigh, g))
        g2 = dict(dose_R2=float(r_dose), dose_ci=[float(cid[0]), float(cid[2])], dose_null95=float(np.percentile(nulld, 95)),
                  dose_p=emp_p(r_dose, nulld), order_R2=float(r_ord), order_null95=float(np.percentile(nullo, 95)),
                  order_p=emp_p(r_ord, nullo), neighbour_dose_R2=float(r_neigh))
        best_low = max(cid[0], boot_ci(Xs, order, g)[0])
        best_null = max(np.percentile(nulld, 95), np.percentile(nullo, 95))
        G2 = (best_low > best_null) and (r_dose > r_neigh)

    # ---------- G3/G4/G5 behavioural (valid worlds only) ----------
    def perworld_metric(fn):
        return np.array([np.mean([fn(r, i) for i in range(K)]) for r in valid]) if valid else np.array([])
    def tk(r, cond): return r["beh"][cond]["tracked"]
    def fx(r, cond): return r["beh"][cond]["fixed"]
    own = perworld_metric(lambda r, i: tk(r, "intact")[i] - r["beh"]["erase"][i]["tracked"][i])
    sham = perworld_metric(lambda r, i: tk(r, "intact")[i] - tk(r, "sham")[i])
    neigh = perworld_metric(lambda r, i: np.mean([tk(r, "intact")[i] - r["beh"]["erase"][j]["tracked"][i] for j in range(K) if j != i]))
    own_m_sham = perworld_metric(lambda r, i: (tk(r, "intact")[i] - r["beh"]["erase"][i]["tracked"][i]) - (tk(r, "intact")[i] - tk(r, "sham")[i]))
    own_m_neigh = perworld_metric(lambda r, i: (tk(r, "intact")[i] - r["beh"]["erase"][i]["tracked"][i]) - np.mean([tk(r, "intact")[i] - r["beh"]["erase"][j]["tracked"][i] for j in range(K) if j != i]))
    abl = perworld_metric(lambda r, i: tk(r, "ablate")[i] - r["beh"]["erase_ablate"][i]["tracked"][i])
    own_fixed = perworld_metric(lambda r, i: fx(r, "intact")[i] - r["beh"]["erase"][i]["fixed"][i])

    ci_own = wb_ci(own); ci_osh = wb_ci(own_m_sham); ci_one = wb_ci(own_m_neigh); ci_fx = wb_ci(own_fixed)
    abl_ratio = (np.abs(abl).mean() / (np.abs(own).mean() + 1e-12)) if len(own) else 1.0
    G3 = (len(own) > 0 and ci_own[0] > 0 and ci_osh[0] > 0 and ci_one[0] > 0
          and abl_ratio < ABL_RATIO_MAX and own_fixed.mean() > 0)
    G4 = (len(own) > 0 and ci_one[0] > 0)
    # G5 robustness: same sign per world, quantify gap
    same_sign = int(np.sum(np.sign(own) == np.sign(own_fixed))) if len(own) else 0
    G5 = (len(own) > 0 and ci_fx[0] > 0 and same_sign == len(own))
    G6 = bool(G0 and G1 and G2 and G3 and G4)

    # ---------- per-seed table ----------
    per_seed = []
    for r in allrec:
        if not r.get("eligible"):
            per_seed.append(dict(seed=r["seed"], eligible=False, reason=r.get("reason"))); continue
        A = r["beh"]["intact"]; er = r["beh"]["erase"]
        ownv = float(np.mean([A["tracked"][i] - er[i]["tracked"][i] for i in range(K)]))
        per_seed.append(dict(seed=r["seed"], eligible=True, g0_valid=r["g0_valid"],
                             max_cov=r["max_cov_intact"], own_tracked=ownv,
                             invalid_reason=r.get("invalid_reason")))

    out = dict(
        mission="LCI-CAUSAL-NONMERGING-CONFIRM-02",
        n_seeds=nS, n_eligible=nE, n_g0_valid=nV, nonfusing_fraction=nonfusing_frac,
        G0=dict(passed=bool(G0), valid_worlds=nV, min_valid=MIN_VALID_WORLDS, worlds_ok=bool(g0_worlds_ok),
                nonfusing_fraction=nonfusing_frac, min_fraction=MIN_NONFUSING_FRACTION, frac_ok=bool(g0_frac_ok)),
        G1=dict(passed=bool(G1), DD_mem=g1_dd, diag=g1_diag, off=g1_off),
        G2=dict(passed=bool(G2), **g2),
        G3=dict(passed=bool(G3), own_worldCI=ci_own, own_sham_worldCI=ci_osh, own_neigh_worldCI=ci_one,
                own_mean=float(own.mean()) if len(own) else None, sham_mean=float(sham.mean()) if len(sham) else None,
                neigh_mean=float(neigh.mean()) if len(neigh) else None,
                ablation_ratio=float(abl_ratio), ablation_mean=float(abl.mean()) if len(abl) else None,
                own_fixed_mean=float(own_fixed.mean()) if len(own_fixed) else None,
                worlds_own_pos=int((own > 0).sum()) if len(own) else 0, nW=nV,
                note="readout is directly coupled to m+ by construction; ablation~0 is a manipulation check"),
        G4=dict(passed=bool(G4), own_neigh_worldCI=ci_one, neigh_mean=float(neigh.mean()) if len(neigh) else None,
                note="neighbour effect ~0 (perfect locality); bijective tracker => no shared components"),
        G5=dict(passed=bool(G5), own_fixed_worldCI=ci_fx, same_sign_worlds=same_sign,
                tracked_over_fixed=float(own.mean() / own_fixed.mean()) if (len(own) and own_fixed.mean()) else None),
        G6=dict(passed=bool(G6), rule="G0 & G1 & G2 & G3 & G4"),
        per_seed=per_seed)
    json.dump(out, open(sys.argv[2] if len(sys.argv) > 2 else "work/nm_certificate.json", "w"), indent=2)

    print(f"=== NONMERGING-CONFIRM-02 certificate ===")
    print(f"seeds={nS} eligible={nE} G0-valid={nV} nonfusing_frac={nonfusing_frac:.2f}")
    print(f"[G0 feasibility] valid>={MIN_VALID_WORLDS}:{g0_worlds_ok} frac>={MIN_NONFUSING_FRACTION}:{g0_frac_ok} -> {'PASS' if G0 else 'FAIL'}")
    print(f"[G1 storage]     DD_mem={g1_dd:.0f} off={g1_off:.2e} -> {'PASS' if G1 else 'FAIL'}")
    if g2: print(f"[G2 readout]     dose_R2={g2['dose_R2']:+.3f} null95={g2['dose_null95']:+.3f} neigh={g2['neighbour_dose_R2']:+.3f} -> {'PASS' if G2 else 'FAIL'}")
    print(f"[G3 causal]      own CI={ci_own} own-sham CI={ci_osh} own-neigh CI={ci_one} abl_ratio={abl_ratio:.3f} own_fixed={out['G3']['own_fixed_mean']} -> {'PASS' if G3 else 'FAIL'}")
    print(f"[G4 locality]    own-neigh CI={ci_one} neigh_mean={out['G4']['neigh_mean']} -> {'PASS' if G4 else 'FAIL'}")
    print(f"[G5 robustness]  own_fixed CI={ci_fx} same_sign={same_sign}/{nV} tracked/fixed={out['G5']['tracked_over_fixed']} -> {'PASS' if G5 else 'FAIL'}")
    print(f">>> G6 causal individuation: {'PASS' if G6 else 'FAIL'}")
    print(f"wrote {sys.argv[2] if len(sys.argv)>2 else 'work/nm_certificate.json'}")

if __name__ == "__main__":
    main()

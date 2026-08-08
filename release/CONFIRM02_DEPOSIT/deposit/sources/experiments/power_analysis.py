"""LCI-CAUSAL-CONFIRMATION-01 — world-level power analysis (calibrated on DEV 50001-50010 ONLY).
Empirical power via resampling the observed DEV world-level effect structure, for two pre-declared gates:
 (G-EXIST) behavioural causal EXISTENCE: per-world own-erase effect reliably >0 (one-sample world bootstrap
           2.5-pct > 0) AND intervention collapse under ablation. Certifies "stored memory causally drives
           own later behaviour, locally".
 (G-DECODE) behavioural dose READOUT: grouped LOGO R2 world-bootstrap 2.5-pct > within-world null 95-pct.
           The stronger claim (behaviour encodes the specific dose value).
Accounts for observed eligibility (fraction of seeds yielding K=3). Decides whether 52001-52012 suffices.
"""
import sys, json, numpy as np
SEED = 20260715; K = 3
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

recs = [r for r in json.load(open(sys.argv[1])) if r.get("ok")]
# per-world arrays
W = []
for r in recs:
    b = r["beh"]; A = b["intact"]; er = b["erase"]
    dose = np.array(r["dose"]); mass = np.array(A["mass"], float)
    effspec = np.array([(A["integ_upt"][i] - er[i]["integ_upt"][i]) / max(mass[i], 1e-9) for i in range(K)])
    effm = np.array([(A["mass"][i] - er[i]["mass"][i]) / max(mass[i], 1e-9) for i in range(K)])
    effsz = np.array([A["size"][i] - er[i]["size"][i] for i in range(K)], float)
    effc = np.array([A["mean_c"][i] - er[i]["mean_c"][i] for i in range(K)], float)
    W.append(dict(dose=dose, X=np.column_stack([effspec, effm, effsz, effc]), effspec=effspec))
nW = len(W); elig = nW / len([r for r in json.load(open(sys.argv[1]))])
print(f"DEV eligible worlds={nW}  observed eligibility={elig:.2f}")

def within_null95(X, y, g, n=2000, seed=SEED):
    rng = np.random.default_rng(seed); v = []; idxby = {h: np.where(g == h)[0] for h in np.unique(g)}
    for _ in range(n):
        yp = y.copy()
        for h, ix in idxby.items(): yp[ix] = y[ix][rng.permutation(len(ix))]
        try: v.append(R2(yp, logo(X, yp, g)))
        except Exception: pass
    return np.percentile(v, 95)
def boot_lo(X, y, g, nb=800, seed=SEED):
    rng = np.random.default_rng(seed); hs = np.unique(g); v = []
    for _ in range(nb):
        pk = rng.choice(hs, len(hs), True); idx = np.concatenate([np.where(g == h)[0] for h in pk])
        gg = np.concatenate([[k] * int((g == h).sum()) for k, h in enumerate(pk)])
        try: v.append(R2(y[idx], logo(X[idx], y[idx], gg)))
        except Exception: pass
    return np.percentile(v, 2.5)

def assemble(sample_worlds):
    X = np.vstack([W[j]["X"] for j in sample_worlds]); y = np.concatenate([W[j]["dose"] for j in sample_worlds])
    g = np.concatenate([[k] * K for k in range(len(sample_worlds))]); return X, y, g

rng = np.random.default_rng(SEED)
print("\n n_worlds | P(EXIST: per-world eff>0, boot2.5%>0) | P(DECODE: LOGO CIlo>within-null95)")
for n in (6, 9, 12, 15, 18, 24):
    pe = 0; pd = 0; REPS = 200
    for _ in range(REPS):
        samp = rng.integers(0, nW, n)
        # EXISTENCE: one-sample world bootstrap of per-world mean specific effect
        perw = np.array([W[j]["effspec"].mean() for j in samp])
        bs = np.array([np.mean(perw[rng.integers(0, n, n)]) for _ in range(400)])
        if np.percentile(bs, 2.5) > 0: pe += 1
        # DECODE
        X, y, g = assemble(samp)
        try:
            r = R2(y, logo(X, y, g)); lo = boot_lo(X, y, g, nb=400); nl = within_null95(X, y, g, n=400)
            if lo > nl: pd += 1
        except Exception: pass
    print(f"   {n:3d}    |   {pe/REPS:5.2f}                              |   {pd/REPS:5.2f}")

# expected eligible worlds for 12 sealed confirmation seeds
for fam in (12, 18, 24):
    print(f"  family of {fam} confirmation seeds -> expected eligible ~{fam*elig:.1f} worlds")

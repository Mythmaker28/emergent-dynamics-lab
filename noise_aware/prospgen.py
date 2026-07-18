"""FRESH PROSPECTIVE GENERATOR — EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00.
NEW generator version (distinct seed namespace from development). Committed and hash-gated BEFORE
execution. N>=5000 with substantial low-SNR mass: 25% SNR<=5, 25% 5-10, 25% 10-30, 25% >30. Stratified
by sign, anchors, contamination, reference count, conditioning and noise family. NO tuning after
execution. The instrument is frozen; this file feeds it and is never edited post-hoc.
"""
from __future__ import annotations
import numpy as np
import devgen                       # reuse ONLY the frozen noise model _noise and structural strata

PROSP_SEED_BASE = 0x5A5A0000        # distinct from dev (0x0DE7)
N_PROSP = 5000
SNR_BANDS = [(0.5, 5.0), (5.0, 10.0), (10.0, 30.0), (30.0, 100.0)]   # 25% mass each
STRATA = devgen.STRATA
NOISE_FAMILIES = devgen.NOISE_FAMILIES

def _snr(rng, band):
    lo, hi = band
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))        # log-uniform within band

def gen_case(i, L=120):
    rng = np.random.default_rng(PROSP_SEED_BASE*1_000_003 + i)
    band = SNR_BANDS[i % 4]                                          # exact 25% per band
    stratum = STRATA[(i // 4) % len(STRATA)]
    nf = NOISE_FAMILIES[(i // (4*len(STRATA))) % len(NOISE_FAMILIES)]
    m = int(rng.choice([2, 3, 3, 4, 5, 8]))
    base = rng.uniform(0.5, 2.0, m) * rng.choice([-1, 1], size=m, p=[0.25, 0.75])
    illcond = (stratum == "illcond") or (rng.random() < 0.08)
    if illcond:
        base = np.full(m, 1.0) + rng.normal(0, 0.02, m)
    kap = np.zeros(m)
    def some(frac):
        k = max(1, int(np.ceil(m*frac))); return rng.choice(m, min(k, m), replace=False)
    if   stratum=="attenuate":        idx=some(0.7); kap[idx]=rng.uniform(.05,.35,len(idx))
    elif stratum=="amplify":          idx=some(0.7); kap[idx]=-rng.uniform(.05,.35,len(idx))
    elif stratum=="mixed":            idx=some(0.7); kap[idx]=rng.uniform(-.35,.35,len(idx))
    elif stratum=="common_mode":      kap=rng.uniform(-.15,.15)*base
    elif stratum=="no_anchor_atten":  kap=rng.uniform(.05,.35,m)
    elif stratum=="no_anchor_amp":    kap=-rng.uniform(.05,.35,m)
    elif stratum=="sparse1":          kap[rng.integers(m)]=rng.uniform(-.35,.35)
    elif stratum=="majority":         idx=some(0.6); kap[idx]=rng.uniform(-.3,.3,len(idx))
    elif stratum=="all_contaminated": kap=rng.uniform(-.35,.35,m); kap[np.abs(kap)<.04]=.06
    elif stratum=="dropout":          kap[rng.integers(m)]=rng.uniform(-.3,.3)
    elif stratum=="nonlinear_contam": idx=some(0.7); kap[idx]=rng.uniform(.05,.3,len(idx))
    anchor_true = bool(np.any(np.abs(kap) < 1e-9))
    sparsity_true = int(np.sum(np.abs(kap) > 1e-9))
    alpha = 1.0/np.where(np.abs(base) > 1e-9, base, 1e-9)
    beta = alpha*kap
    nz = beta[np.abs(beta) > 1e-9]
    sign_true = None if nz.size==0 else ("attenuate" if np.all(nz>0) else ("amplify" if np.all(nz<0) else None))
    if   stratum=="true_null": q = 0.0
    elif stratum=="weak":      q = float(rng.uniform(0.15, 0.6))*rng.choice([-1, 1])
    else:                      q = float(rng.uniform(0.3, 2.0))*rng.choice([-1, 1])
    snr = _snr(rng, band)
    return dict(i=i, m=m, base=base, kap=kap, alpha=alpha, q=q, snr=snr, nf=nf, stratum=stratum,
                band=f"{band[0]:g}-{band[1]:g}", sign_true=sign_true, anchor_true=anchor_true,
                sparsity_true=sparsity_true, dropout=(stratum=="dropout"),
                nonlin=(stratum=="nonlinear_contam"), illcond=bool(illcond), L=L)

def build(i, L=120):
    cs = gen_case(i, L)
    rng = np.random.default_rng(PROSP_SEED_BASE*7_000_003 + i)
    m = cs["m"]; q = cs["q"]; t = np.arange(L); p = np.exp(-t/40.0)
    fac = (1 + 0.3*np.tanh(q)) if cs["nonlin"] else 1.0
    c = np.array([q*(1 - cs["alpha"][j]*cs["kap"][j]*fac) for j in range(m)])
    scale = (abs(q) if abs(q) > 1e-6 else 1.0)/cs["snr"]
    N = devgen._noise(cs["nf"], m, L, scale, rng)
    Y = c[:, None]*p[None, :] + N
    if cs["dropout"]:
        Y[0] = N[0]
    lam = 1.0/np.where(np.abs(cs["base"]) > 1e-9, cs["base"], 1e-9)
    op = np.random.default_rng(PROSP_SEED_BASE*13 + i)
    op_sign = cs["sign_true"] if (cs["sign_true"] is not None and op.random() < 0.55) else None
    op_anchor = bool(cs["anchor_true"] and op.random() < 0.40)
    op_sparsity = cs["sparsity_true"] if op.random() < 0.30 else None
    cs.update(dict(Y=Y, p=p, lam=lam, c=c, qmag=abs(q),
                   op_sign=op_sign, op_anchor=op_anchor, op_sparsity=op_sparsity))
    return cs

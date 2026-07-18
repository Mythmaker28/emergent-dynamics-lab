"""DEVELOPMENT GENERATOR — EXP-GT-NOISE-AWARE-SET-IDENTIFICATION-00 (development partition only).

NOT the prospective generator. Used to CALIBRATE and FREEZE the uncertainty method. Content-addressed
seeds (stable, not process-local). Never reuse the burned N=2000 hold-out (consolidation/holdout_gen.py)
as prospective evidence; a small sample of its failure pattern is reproduced here ONLY as a named
historical regression (see regressions.py), never as prospective qualification.

Case record fields:
  Y (m,L) noisy channels ; p (L,) known profile ; lam (m,) pre-window couplings ;
  qmag = |q| (target, in coefficient units) ;
  truth contracts   : sign_true (contamination action), anchor_true, sparsity_true
  operational contracts (knowable WITHOUT the response truth, from sensor-physics calibration /
                         intervention geometry) : op_sign, op_anchor, op_sparsity
The BLIND arm may consume ONLY op_* ; the CONDITIONAL arm may consume the truth contracts.
"""
from __future__ import annotations
import numpy as np

DEV_SEED_BASE = 0x0DE7  # 3559 ; development namespace (distinct from prospective)
SNR_GRID = [0.5, 1, 2, 3, 5, 8, 10, 20, 50, 100]
NOISE_FAMILIES = ["white", "ar1", "ou", "heavy", "hetero", "refdep"]
STRATA = ["clean", "attenuate", "amplify", "mixed", "common_mode",
          "no_anchor_atten", "no_anchor_amp", "sparse1", "majority",
          "all_contaminated", "dropout", "nonlinear_contam", "true_null", "weak", "illcond"]


def _noise(kind, m, L, scale, rng):
    if kind == "white":
        return rng.normal(0, scale, (m, L))
    if kind == "ar1":                      # correlated Gaussian, phi=0.7
        e = rng.normal(0, scale, (m, L)); x = np.empty((m, L)); x[:, 0] = e[:, 0]
        for t in range(1, L): x[:, t] = 0.7*x[:, t-1] + np.sqrt(1-0.49)*e[:, t]
        return x
    if kind == "ou":                       # OU drift residual: slow mean-reverting drift + white
        theta = 0.05; d = np.empty((m, L)); d[:, 0] = rng.normal(0, scale, m)
        for t in range(1, L): d[:, t] = (1-theta)*d[:, t-1] + rng.normal(0, scale*0.6, m)
        return d + rng.normal(0, scale*0.5, (m, L))
    if kind == "heavy":                    # heavy-tailed: Student-t, df=3, matched scale
        z = rng.standard_t(3, (m, L)); return z*scale/np.sqrt(3.0)
    if kind == "hetero":                   # heteroscedastic: variance grows along the window
        w = np.linspace(0.4, 1.8, L)[None, :]; return rng.normal(0, 1, (m, L))*scale*w
    if kind == "refdep":                   # reference-dependent scale (per channel)
        s = scale*np.exp(rng.normal(0, 0.5, m))[:, None]; return rng.normal(0, 1, (m, L))*s
    raise ValueError(kind)


def gen_case(i, L=120):
    """Deterministic development case i."""
    rng = np.random.default_rng(DEV_SEED_BASE*1_000_003 + i)
    stratum = STRATA[i % len(STRATA)]
    nf = NOISE_FAMILIES[(i // len(STRATA)) % len(NOISE_FAMILIES)]
    m = int(rng.choice([2, 3, 3, 4, 5, 8]))
    # couplings: distinct, mixed signs; some ill-conditioned
    base = rng.uniform(0.5, 2.0, m) * rng.choice([-1, 1], size=m, p=[0.25, 0.75])
    illcond = (stratum == "illcond") or (rng.random() < 0.08)
    if illcond:
        base = np.full(m, 1.0) + rng.normal(0, 0.02, m)
    kap = np.zeros(m)
    def some(frac):
        k=max(1,int(np.ceil(m*frac))); return rng.choice(m, min(k,m), replace=False)
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
    # clean / true_null / weak / illcond -> kap stays 0 (unless illcond overwrote base)
    anchor_true = bool(np.any(np.abs(kap) < 1e-9))
    sparsity_true = int(np.sum(np.abs(kap) > 1e-9))
    alpha = 1.0/np.where(np.abs(base) > 1e-9, base, 1e-9)
    beta = alpha*kap                                        # contamination action beta_i
    nz = beta[np.abs(beta) > 1e-9]
    if nz.size == 0:       sign_true = None
    elif np.all(nz > 0):   sign_true = "attenuate"
    elif np.all(nz < 0):   sign_true = "amplify"
    else:                  sign_true = None
    # response magnitude
    if stratum == "true_null":
        q = 0.0
    elif stratum == "weak":
        q = float(rng.uniform(0.15, 0.6)) * rng.choice([-1, 1])
    else:
        q = float(rng.uniform(0.3, 2.0)) * rng.choice([-1, 1])
    snr = float(rng.choice(SNR_GRID))
    dropout = (stratum == "dropout"); nonlin = (stratum == "nonlinear_contam")
    return dict(i=i, m=m, base=base, kap=kap, alpha=alpha, beta=beta, q=q, snr=snr, nf=nf,
                stratum=stratum, sign_true=sign_true, anchor_true=anchor_true,
                sparsity_true=sparsity_true, dropout=dropout, nonlin=nonlin, illcond=bool(illcond), L=L)


def build(i, L=120):
    cs = gen_case(i, L)
    rng = np.random.default_rng(DEV_SEED_BASE*7_000_003 + i)   # independent noise stream
    m = cs["m"]; q = cs["q"]; t = np.arange(L); p = np.exp(-t/40.0)
    c = np.array([q*(1 - cs["alpha"][j]*cs["kap"][j]) for j in range(m)])
    if cs["nonlin"]:
        c = np.array([q*(1 - cs["alpha"][j]*cs["kap"][j]*(1+0.3*np.tanh(q))) for j in range(m)])
    scale = (abs(q) if abs(q) > 1e-6 else 1.0)/cs["snr"]       # noise scale; for true-null use unit ref
    N = _noise(cs["nf"], m, L, scale, rng)
    Y = c[:, None]*p[None, :] + N
    if cs["dropout"]:
        Y[0] = N[0]                                            # one reference is pure noise
    lam = 1.0/np.where(np.abs(cs["base"]) > 1e-9, cs["base"], 1e-9)
    qmag = abs(q)
    # ---- operational contracts (knowable WITHOUT the response truth) ----
    # sensor-physics sign: the sign of the contamination action is knowable for a fraction of cases
    # from an independent calibration of each reference's gain; here declared for ~55% of signed cases.
    op_rng = np.random.default_rng(DEV_SEED_BASE*13 + i)
    op_sign = cs["sign_true"] if (cs["sign_true"] is not None and op_rng.random() < 0.55) else None
    # intervention geometry can guarantee a clean reference for ~40% of anchored cases
    op_anchor = bool(cs["anchor_true"] and op_rng.random() < 0.40)
    op_sparsity = cs["sparsity_true"] if op_rng.random() < 0.30 else None
    cs.update(dict(Y=Y, p=p, lam=lam, c=c, qmag=qmag,
                   op_sign=op_sign, op_anchor=op_anchor, op_sparsity=op_sparsity))
    return cs

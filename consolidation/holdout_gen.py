"""LARGE FROZEN DISTRIBUTIONAL HOLD-OUT generator. Committed BEFORE execution.
N=2000 stratified cases. Instrument stays frozen; no threshold or theorem may change after this commit.

Contract provenance: sign/anchor are DECLARED per case. Two arms are evaluated:
  ARM-ORACLE   contracts supplied from ground truth (upper bound on achievable identification)
  ARM-BLIND    NO contracts supplied (what passive data alone permits)
The PRIMARY SAFETY ENDPOINT is evaluated on BOTH: proportion of emitted identified sets EXCLUDING the truth.
"""
from __future__ import annotations
import numpy as np

HOLDOUT_SEED = 90_210_000
N_CASES = 2000

STRATA = ["attenuate","amplify","mixed","common_mode","no_anchor_atten","no_anchor_amp",
          "all_contaminated","sparse1","majority","dropout","nonlinear_contam","clean"]

def gen_case(i):
    """Deterministic case i. Returns (couplings, kappas, anchor_true, sign_true, stratum, snr, m)."""
    rng = np.random.default_rng(HOLDOUT_SEED + i)
    stratum = STRATA[i % len(STRATA)]
    m = int(rng.choice([2,3,3,4,5,8]))
    # couplings: distinct, mixed signs allowed; conditioning varies
    base = rng.uniform(0.5, 2.0, m) * rng.choice([-1,1], size=m, p=[0.25,0.75])
    if rng.random() < 0.12:                       # ill-conditioned stratum
        base = np.full(m, 1.0) + rng.normal(0, 0.02, m)
    kap = np.zeros(m)
    if stratum=="attenuate":       idx=rng.choice(m,max(1,m-1),replace=False); kap[idx]=rng.uniform(.05,.35,len(idx))
    elif stratum=="amplify":       idx=rng.choice(m,max(1,m-1),replace=False); kap[idx]=-rng.uniform(.05,.35,len(idx))
    elif stratum=="mixed":         idx=rng.choice(m,max(1,m-1),replace=False); kap[idx]=rng.uniform(-.35,.35,len(idx))
    elif stratum=="common_mode":   c=rng.uniform(-.15,.15); kap=c*base
    elif stratum=="no_anchor_atten": kap=rng.uniform(.05,.35,m)
    elif stratum=="no_anchor_amp":   kap=-rng.uniform(.05,.35,m)
    elif stratum=="all_contaminated":kap=rng.uniform(-.35,.35,m); kap[np.abs(kap)<.03]=.05
    elif stratum=="sparse1":       kap[rng.integers(m)]=rng.uniform(-.35,.35)
    elif stratum=="majority":      idx=rng.choice(m,max(1,int(np.ceil(m*0.6))),replace=False); kap[idx]=rng.uniform(-.3,.3,len(idx))
    elif stratum=="dropout":       kap[rng.integers(m)]=rng.uniform(-.3,.3)   # one ref later zeroed-out (noise only)
    elif stratum=="nonlinear_contam": idx=rng.choice(m,max(1,m-1),replace=False); kap[idx]=rng.uniform(.05,.3,len(idx))
    # 'clean' -> kap stays 0
    anchor_true = bool(np.any(np.abs(kap) < 1e-9))
    beta = kap / np.where(np.abs(base)>1e-9, base, 1e-9)   # beta_i = alpha_i*kappa_i with alpha_i = 1/a_i (gy=1)
    nz = beta[np.abs(beta)>1e-9]
    if nz.size==0: sign_true=None
    elif np.all(nz>0): sign_true="attenuate"
    elif np.all(nz<0): sign_true="amplify"
    else: sign_true=None
    snr = float(rng.choice([5.,15.,50.]))
    return base, kap, anchor_true, sign_true, stratum, snr, m, bool(stratum=="dropout"), bool(stratum=="nonlinear_contam")

def build(i, T=240, tp=120):
    base,kap,anchor,sign,stratum,snr,m,dropout,nonlin = gen_case(i)
    rng = np.random.default_rng(HOLDOUT_SEED + 500000 + i)
    prof=np.zeros(T); prof[tp:]=np.exp(-np.arange(T-tp)/40.)
    q = float(rng.uniform(0.5,2.0)) * rng.choice([-1,1])     # response SIGN varies
    noise = abs(q)/snr
    alpha = 1.0/np.where(np.abs(base)>1e-9, base, 1e-9)
    v=[]
    for j in range(m):
        k = kap[j]
        if nonlin: k = k*(1.0 + 0.3*np.tanh(q))              # amplitude-dependent contamination
        chan = q*(1 - alpha[j]*k)*prof + rng.normal(0,noise,T)
        if dropout and j==0: chan = rng.normal(0,noise,T)     # reference dropout -> pure noise
        v.append(chan)
    return np.stack(v), base, prof, tp, q, anchor, sign, stratum, snr, m

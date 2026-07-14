"""DEVELOPMENT GENERATOR — EXP-GT-POINT-CERTIFIED-SET-IDENTIFICATION-00.
Distinct seed namespace. Includes the full dropout ontology and contamination regimes required by the
mission. Content-addressed seeds. Never reuses the burned N=5000 hold-out prospectively.
"""
from __future__ import annotations
import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "noise_aware"))
import devgen   # frozen noise model only

PC_DEV_SEED = 0x9C0DE7
SNR_GRID = [0.5,1,2,3,5,8,10,20,50,100]
NF = ["white","ar1","ou","heavy","hetero","refdep"]
STRATA = ["no_dropout","one_dropout","multi_dropout","intermittent_dropout","gain_collapse",
          "bandwidth_collapse","sparse1","majority","all_contaminated","clean_lowSNR_anchor",
          "contaminated_highSNR","mixed_ampatten","collinear","dropout_post_calib",
          "dropout_post_intervention","true_null","weak","clean_strong"]

def _apply_dropout(chan, kind, onset, rng, scale):
    L=len(chan)
    if kind=="missing":     return rng.normal(0,scale,L)
    if kind=="gain":        return chan*0.02 + rng.normal(0,scale,L)
    if kind=="flatline":    return np.full(L, chan[0]) + rng.normal(0,scale*0.2,L)
    if kind=="bandwidth":                      # heavy low-pass: destroys the response shape
        k=np.ones(21)/21; return np.convolve(chan,k,mode="same")*0.1 + rng.normal(0,scale,L)
    if kind=="intermittent":
        m=rng.random(L)<0.4; c=chan.copy(); c[m]=rng.normal(0,scale,m.sum()); return c
    if kind=="post":                            # dropout only after intervention onset
        c=chan.copy(); c[onset:]=rng.normal(0,scale,L-onset); return c
    return chan

def build(i, L=120):
    rng=np.random.default_rng(PC_DEV_SEED*1_000_003+i)
    stratum=STRATA[i%len(STRATA)]; nf=NF[(i//len(STRATA))%len(NF)]
    m=int(rng.choice([3,3,4,5,8]))
    base=rng.uniform(0.5,2.0,m)*rng.choice([-1,1],size=m,p=[0.25,0.75])
    if stratum=="collinear": base=np.full(m,1.0)+rng.normal(0,0.02,m)
    kap=np.zeros(m); alpha=1.0/np.where(np.abs(base)>1e-9,base,1e-9)
    def some(f): k=max(1,int(np.ceil(m*f))); return rng.choice(m,min(k,m),replace=False)
    if stratum in ("sparse1","dropout_post_calib","dropout_post_intervention"): kap[rng.integers(m)]=rng.uniform(-.35,.35)
    elif stratum=="majority": kap[some(0.6)]=rng.uniform(-.3,.3,max(1,int(np.ceil(m*0.6))))
    elif stratum=="all_contaminated": kap=rng.uniform(-.35,.35,m); kap[np.abs(kap)<.04]=.06
    elif stratum=="contaminated_highSNR": kap[some(0.7)]=rng.uniform(.05,.35,max(1,int(np.ceil(m*0.7))))
    elif stratum=="mixed_ampatten": kap[some(0.7)]=rng.uniform(-.35,.35,max(1,int(np.ceil(m*0.7))))
    elif stratum in ("one_dropout","multi_dropout","intermittent_dropout","gain_collapse","bandwidth_collapse"):
        kap[some(0.5)]=rng.uniform(.05,.3,max(1,int(np.ceil(m*0.5))))
    anchor_true=bool(np.any(np.abs(kap)<1e-9)); sparsity_true=int(np.sum(np.abs(kap)>1e-9))
    beta=alpha*kap; nz=beta[np.abs(beta)>1e-9]
    sign_true=None if nz.size==0 else ("attenuate" if np.all(nz>0) else ("amplify" if np.all(nz<0) else None))
    if stratum=="true_null": q=0.0
    elif stratum in ("weak","clean_lowSNR_anchor"): q=float(rng.uniform(0.15,0.6))*rng.choice([-1,1])
    else: q=float(rng.uniform(0.3,2.0))*rng.choice([-1,1])
    if stratum=="clean_lowSNR_anchor": snr=float(rng.choice([2,3,5]))
    elif stratum in ("contaminated_highSNR","clean_strong"): snr=float(rng.choice([20,50,100]))
    else: snr=float(rng.choice(SNR_GRID))
    t=np.arange(L); p=np.exp(-t/40.0); onset=0
    c=np.array([q*(1-alpha[j]*kap[j]) for j in range(m)])
    scale=(abs(q) if abs(q)>1e-6 else 1.0)/snr
    N=devgen._noise(nf,m,L,scale,rng); Y=c[:,None]*p[None,:]+N
    # dropout mechanics
    drop=set()
    dk={"one_dropout":"missing","multi_dropout":"missing","intermittent_dropout":"intermittent",
        "gain_collapse":"gain","bandwidth_collapse":"bandwidth","dropout_post_calib":"missing",
        "dropout_post_intervention":"post"}.get(stratum)
    if dk:
        ndrop=2 if stratum=="multi_dropout" and m>=5 else 1
        for j in rng.choice(m,min(ndrop,m-2),replace=False):
            Y[j]=_apply_dropout(Y[j],dk,L//6,rng,scale); drop.add(int(j))
    lam=1.0/np.where(np.abs(base)>1e-9,base,1e-9)
    op=np.random.default_rng(PC_DEV_SEED*13+i)
    op_sign=sign_true if (sign_true is not None and op.random()<0.55) else None
    op_anchor=bool(anchor_true and op.random()<0.40)
    op_sparsity=sparsity_true if op.random()<0.30 else None
    return dict(Y=Y,p=p,lam=lam,qmag=abs(q),nonzero=abs(q)>1e-9,snr=snr,nf=nf,stratum=stratum,m=m,
                sign_true=sign_true,anchor_true=anchor_true,sparsity_true=sparsity_true,
                op_sign=op_sign,op_anchor=op_anchor,op_sparsity=op_sparsity,dropout_channels=drop)

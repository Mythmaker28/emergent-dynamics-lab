"""FRESH PROSPECTIVE GENERATOR — EXP-GT-POINT-CERTIFIED-SET-IDENTIFICATION-00.
NEW seed namespace. N=10000, >=40% dropout/sparse, oversampled low-SNR anchors, mixed-sign contamination,
high-SNR contaminated references, conditioning boundaries. Committed and hash-gated BEFORE execution.
"""
from __future__ import annotations
import os,sys,numpy as np
sys.path.insert(0,os.path.join(os.path.dirname(__file__),"..","noise_aware"))
import devgen
sys.path.insert(0,os.path.dirname(__file__)); import pcgen

PC_PROSP_SEED=0x50507A9E
N_PROSP=10000
# 20-slot schedule: 8 dropout/sparse (=40%) + 12 others
SCHED=["one_dropout","multi_dropout","intermittent_dropout","gain_collapse","bandwidth_collapse",
       "dropout_post_calib","dropout_post_intervention","sparse1",                       # 8 dropout/sparse
       "no_dropout","majority","all_contaminated","clean_lowSNR_anchor","contaminated_highSNR",
       "mixed_ampatten","collinear","true_null","weak","clean_strong","mixed_ampatten","majority"]
NF=pcgen.NF

def _snr(rng):
    b=rng.random()
    if b<0.40: return float(np.exp(rng.uniform(np.log(0.5),np.log(5))))
    if b<0.70: return float(np.exp(rng.uniform(np.log(5),np.log(10))))
    if b<0.90: return float(np.exp(rng.uniform(np.log(10),np.log(30))))
    return float(np.exp(rng.uniform(np.log(30),np.log(100))))

def build(i,L=120):
    rng=np.random.default_rng(PC_PROSP_SEED*1_000_003+i)
    stratum=SCHED[i%len(SCHED)]; nf=NF[(i//len(SCHED))%len(NF)]
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
    snr=_snr(rng)
    if stratum=="clean_lowSNR_anchor": snr=min(snr,float(rng.choice([2,3,5])))
    if stratum in ("contaminated_highSNR","clean_strong"): snr=max(snr,float(rng.choice([20,50])))
    t=np.arange(L); p=np.exp(-t/40.0)
    c=np.array([q*(1-alpha[j]*kap[j]) for j in range(m)])
    scale=(abs(q) if abs(q)>1e-6 else 1.0)/snr
    N=devgen._noise(nf,m,L,scale,rng); Y=c[:,None]*p[None,:]+N
    drop=set()
    dk={"one_dropout":"missing","multi_dropout":"missing","intermittent_dropout":"intermittent",
        "gain_collapse":"gain","bandwidth_collapse":"bandwidth","dropout_post_calib":"missing",
        "dropout_post_intervention":"post"}.get(stratum)
    if dk:
        nd=2 if stratum=="multi_dropout" and m>=5 else 1
        for j in rng.choice(m,min(nd,m-2),replace=False):
            Y[j]=pcgen._apply_dropout(Y[j],dk,L//6,rng,scale); drop.add(int(j))
    lam=1.0/np.where(np.abs(base)>1e-9,base,1e-9)
    op=np.random.default_rng(PC_PROSP_SEED*13+i)
    op_sign=sign_true if (sign_true is not None and op.random()<0.55) else None
    op_anchor=bool(anchor_true and op.random()<0.40); op_sparsity=sparsity_true if op.random()<0.30 else None
    return dict(Y=Y,p=p,lam=lam,qmag=abs(q),nonzero=abs(q)>1e-9,snr=snr,nf=nf,stratum=stratum,m=m,
                sign_true=sign_true,anchor_true=anchor_true,sparsity_true=sparsity_true,
                op_sign=op_sign,op_anchor=op_anchor,op_sparsity=op_sparsity,dropout_channels=drop,
                is_dropsparse=bool(dk or stratum=="sparse1"))

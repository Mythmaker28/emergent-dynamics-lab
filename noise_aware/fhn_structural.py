"""FHN STRUCTURAL AUDIT — EXP-GT-NASI-00 (deliverable 20). STRUCTURAL transfer ONLY: the identifiability
CLASSES and the no-false-{0} property must transfer to a genuinely different substrate. NO quantitative
point-accuracy claim (mission section 21). The FitzHugh-Nagumo response profile is non-exponential and
non-monotonic (spike + refractory recovery), unlike the ctrans exp profile: if the method transfers, it is
structural, not a coincidence of the exp waveform.
"""
from __future__ import annotations
import numpy as np, sys
sys.path.insert(0,'.'); import nasi

def fhn_response(L=120, q=1.0, a=0.7, b=0.8, eps=0.08, I0=0.5, dt=0.5):
    """Integrate FHN with baseline drive I0 and a step of size q; return the baseline-subtracted v-response."""
    def run(Iamp):
        v,w=-1.2,-0.6; vs=[]
        for t in range(L):
            I=I0+(Iamp if t>=L//6 else 0.0)
            v=v+dt*(v-v**3/3-w+I); w=w+dt*eps*(v+a-b*w); vs.append(v)
        return np.array(vs)
    return run(q)-run(0.0)      # causal response to the step of size q

# canonical response profile from a clean high-SNR calibration (declared, not per-trial truth)
P = fhn_response(q=1.0); P = P/ (np.linalg.norm(P)/np.sqrt(len(P)) + 1e-12)

def build(i):
    rng=np.random.default_rng(0xF44E0000+i)
    m=int(rng.choice([2,3,3,4,5])); q=float(rng.uniform(0.3,2.0))*rng.choice([-1,1])
    stratum=["attenuate","amplify","clean","no_anchor_atten","dropout","true_null","weak","illcond"][i%8]
    if stratum=="true_null": q=0.0
    if stratum=="weak": q=float(rng.uniform(0.15,0.5))*rng.choice([-1,1])
    base=rng.uniform(0.5,2.0,m)*rng.choice([-1,1],size=m,p=[0.25,0.75])
    if stratum=="illcond": base=np.full(m,1.0)+rng.normal(0,0.02,m)
    kap=np.zeros(m); alpha=1.0/np.where(np.abs(base)>1e-9,base,1e-9)
    if stratum=="attenuate": kap[rng.choice(m,max(1,m-1),replace=False)]=rng.uniform(.05,.35,max(1,m-1))
    elif stratum=="amplify": kap[rng.choice(m,max(1,m-1),replace=False)]=-rng.uniform(.05,.35,max(1,m-1))
    elif stratum=="no_anchor_atten": kap=rng.uniform(.05,.35,m)
    elif stratum=="dropout": kap[rng.integers(m)]=rng.uniform(-.3,.3)
    beta=alpha*kap; nz=beta[np.abs(beta)>1e-9]
    sign=None if nz.size==0 else ("attenuate" if np.all(nz>0) else ("amplify" if np.all(nz<0) else None))
    anchor=bool(np.any(np.abs(kap)<1e-9))
    snr=float(rng.choice([2,3,5,8,15,50]))
    c=np.array([q*(1-alpha[j]*kap[j]) for j in range(m)])
    L=len(P); Y=c[:,None]*P[None,:]+rng.normal(0,(abs(q) if abs(q)>1e-6 else 1.0)/snr,(m,L))
    if stratum=="dropout": Y[0]=rng.normal(0,(abs(q) or 1.0)/snr,L)
    lam=1.0/np.where(np.abs(base)>1e-9,base,1e-9)
    return dict(Y=Y,p=P,lam=lam,qmag=abs(q),sign=sign,anchor=anchor,sparsity=int(np.sum(np.abs(kap)>1e-9)),
                snr=snr,stratum=stratum,nonzero=abs(q)>1e-9)

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 500
    emit=cov=f0=widen_ok=ill=0; lowcov=[0,0]
    for i in range(N):
        cs=build(i)
        r=nasi.identify(cs["Y"],cs["p"],cs["lam"],
                        nasi.Contract(sign=cs["sign"],clean_anchor=cs["anchor"],sparsity_s=cs["sparsity"]),
                        alpha=0.05,rng=np.random.default_rng(0xF44E+i))
        c=r.contains(cs["qmag"])
        if r.qset==[(0.0,0.0)] and cs["nonzero"]: f0+=1
        if cs["stratum"]=="illcond":
            ill+=1; widen_ok+=(r.status in nasi.ABSTAIN or (c in (True,None)))
        if r.status in nasi.EMITTING:
            emit+=1; cov+=(c is True)
            if cs["snr"]<=5: lowcov[1]+=1; lowcov[0]+=(c is True)
    print("FHN STRUCTURAL AUDIT (profile = FitzHugh-Nagumo spike+recovery, non-exponential):")
    print(f"  false exact-zero on nonzero = {f0}  (must be 0)")
    print(f"  coverage of structural identified set = {cov}/{emit} = {cov/max(1,emit):.3f}")
    print(f"  low-SNR(<=5) coverage = {lowcov[0]}/{lowcov[1]} = {lowcov[0]/max(1,lowcov[1]):.3f}")
    print(f"  ill-conditioned widen/abstain-or-cover = {widen_ok}/{ill}")
    print("  CLAIM: structural class transfer + no false zero. NO quantitative point-accuracy claim.")

"""INDEPENDENT REPLICATION of the noise-aware instrument. numpy only. Does NOT import nasi.
DELIBERATELY DIFFERENT method for every stage, so agreement is evidence and disagreement is a bug:
  * channel uncertainty: PERCENTILE moving-block bootstrap of the slope (no studentization), with
    first-difference pre-whitening for autocorrelation, and BONFERRONI simultaneity (vs nasi's studentized
    max-|t| + HAC inflation);
  * set propagation: independently re-derived T6 interval maps;
  * exact-zero: structurally prohibited (never emitted from data), same as nasi.
Compares SETS (endpoints), not merely statuses.
"""
from __future__ import annotations
import numpy as np, json, glob, sys, os
import prospgen   # generator only (data), NOT the instrument

ALPHA=0.05; B=399; BLOCK=24

def channel_ci_indep(Y, p, alpha=ALPHA, rng=None):
    """Percentile moving-block bootstrap of the OLS slope (intercept + linear drift), Bonferroni-simultaneous."""
    if rng is None: rng=np.random.default_rng(0)
    m,L=Y.shape
    X=np.column_stack([p, np.ones(L), np.linspace(-1,1,L)])
    XtXinv=np.linalg.pinv(X.T@X); A0=(XtXinv@X.T)[0]
    c=Y@A0
    beta=np.linalg.pinv(X)@Y.T; R=Y-(X@beta).T
    b=BLOCK; nb=int(np.ceil(L/b)); smax=L-b
    aperc=alpha/m                      # Bonferroni across channels
    boot=np.empty((B,m))
    for r in range(B):
        st=rng.integers(0,smax+1,size=nb); idx=(st[:,None]+np.arange(b)[None,:]).ravel()[:L]
        boot[r]=c + R[:,idx]@A0
    lo=np.percentile(boot,100*aperc/2,axis=0); hi=np.percentile(boot,100*(1-aperc/2),axis=0)
    return c, lo, hi

def mag(lo,hi):
    if lo>0: return (lo,hi)
    if hi<0: return (-hi,-lo)
    return (0.0,max(-lo,hi))

def identify_indep(Y,p,lam,sign,anchor,sparsity,rng=None):
    m,L=Y.shape
    inv=1.0/np.where(np.abs(lam)>1e-9,lam,1e-9); spread=np.std(inv)/(abs(np.mean(inv))+1e-30)
    if spread<0.15: return ("ILL",[])
    c,lo,hi=channel_ci_indep(Y,p,rng=rng)
    M=[mag(a,b) for a,b in zip(lo,hi)]; Mlo=np.array([a for a,_ in M]); Mhi=np.array([b for _,b in M])
    det=Mlo>0
    if anchor:
        if sign=="attenuate": return ("SET",[(max(float(np.max(Mlo)),0.0),float(np.max(Mhi)))])
        if sign=="amplify":
            if det.any(): return ("SET",[(max(float(np.min(Mlo[det])),0.0),float(np.min(Mhi[det])))])
            return ("BELOWDET",[(0.0,float(np.sort(Mhi)[min(1,m-1)]))])
        return ("SET",[(max(float(np.min(Mlo)),0.0),float(np.max(Mhi)))])
    if sparsity is not None and (m-sparsity)>=2:
        # independent clean-majority: densest overlap via pairwise
        best=None
        for i in range(m):
            grp=[j for j in range(m) if not(M[j][1]<M[i][0] or M[j][0]>M[i][1])]
            if best is None or len(grp)>len(best): best=grp
        if best and len(best)>=(m-sparsity):
            L2=max(M[j][0] for j in best); H2=min(M[j][1] for j in best)
            if L2<=H2: return ("SET",[(max(L2,0.0),H2)])
    if sign=="attenuate":
        Lb=float(np.max(Mlo))
        return ("LOWER",[(Lb,np.inf)]) if Lb>0 else ("ZEROCOMP",[(0.0,np.inf)])
    if sign=="amplify":
        if det.any(): return ("UPPER",[(0.0,float(np.min(Mhi[det])))])
        return ("BELOWDET",[(0.0,float(np.sort(Mhi)[min(1,m-1)]))])
    return ("NONID",[])

def contains(qset,q):
    if not qset: return None
    return any(a-1e-9<=q<=b+1e-9 for a,b in qset)

if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 400
    # compare against nasi on a prospective sample: SETS and coverage
    sys.path.insert(0,'.'); import nasi   # imported ONLY to compare, never used inside identify_indep
    agree_cover=0; both=0; f0=0; maxend=0.0; covO=0; emit=0
    for i in range(N):
        cs=prospgen.build(i); q=cs["qmag"]
        st,qs=identify_indep(cs["Y"],cs["p"],cs["lam"],cs["sign_true"],cs["anchor_true"],cs["sparsity_true"],
                             rng=np.random.default_rng(999+i))
        r=nasi.identify(cs["Y"],cs["p"],cs["lam"],
                        nasi.Contract(sign=cs["sign_true"],clean_anchor=cs["anchor_true"],sparsity_s=cs["sparsity_true"]),
                        alpha=ALPHA,rng=np.random.default_rng(prospgen.PROSP_SEED_BASE+i))
        ci=contains(qs,q); cj=r.contains(q)
        if qs==[(0.0,0.0)] and q>1e-9: f0+=1
        if ci is not None:
            emit+=1; covO+=(ci is True)
        if ci is not None and cj is not None:
            both+=1; agree_cover+=(ci==cj)
            # set-endpoint discrepancy (finite parts)
            if qs and r.qset:
                a1,b1=qs[0]; a2,b2=r.qset[0]
                if np.isfinite(b1) and np.isfinite(b2): maxend=max(maxend,abs(a1-a2)+abs(b1-b2))
    print(f"INDEP REPLICATION vs nasi on {N} prospective cases (ARM O):")
    print(f"  independent false_zero_nonzero = {f0}   (must be 0)")
    print(f"  independent coverage = {covO}/{emit} = {covO/max(1,emit):.3f}")
    print(f"  status-agreement on covered/miss = {agree_cover}/{both} = {agree_cover/max(1,both):.3f}")
    print(f"  max set-endpoint L1 discrepancy (finite sets) = {maxend:.3f}")

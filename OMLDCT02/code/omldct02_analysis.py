"""OMLDCT02 — the frozen paired analysis: exact Pratt signed-rank by conditional sign-flip
enumeration, and the intersection-union AND rule with concordant direction.

Every rule here is the owner's, frozen before world 1. Nothing in this file is chosen by me.
"""
from __future__ import annotations
import math
from fractions import Fraction

ALPHA=0.05
MINIMUM_VALID_PAIR_COUNT=41

def midranks(vals):
    """deterministic midranks of |d| over ALL pairs, zeros included — this is what makes it Pratt
    rather than plain Wilcoxon."""
    idx=sorted(range(len(vals)),key=lambda i:vals[i])
    r=[0.0]*len(vals); i=0
    while i<len(idx):
        j=i
        while j+1<len(idx) and vals[idx[j+1]]==vals[idx[i]]: j+=1
        m=(i+j)/2.0+1.0
        for k in range(i,j+1): r[idx[k]]=m
        i=j+1
    return r

def pratt_statistic(d):
    """W+ over the NON-ZERO differences, using midranks computed over all pairs including zeros.
    Zero differences remain valid pairs and contribute zero signed weight."""
    a=[abs(x) for x in d]
    r=midranks(a)
    return sum(r[i] for i in range(len(d)) if d[i]>0), r

def exact_two_sided_p(d):
    """Exact conditional sign-flip distribution over the NON-ZERO signed differences, with Pratt
    ranks that include the zero observations in the ranking. Dynamic programming over the
    achievable sums of the non-zero ranks; every sign assignment is equiprobable under the null.

    Returns (p, W_plus, n_nonzero, n_zero). If every difference is zero, p = 1 by the frozen rule.
    """
    n=len(d)
    Wp,r=pratt_statistic(d)
    nz=[r[i] for i in range(n) if d[i]!=0]
    z=n-len(nz)
    if not nz: return 1.0,Wp,0,z
    # ranks are integers or half-integers; double them so the DP is exact in integers
    dbl=[int(round(2*x)) for x in nz]
    assert all(abs(2*x-y)<1e-9 for x,y in zip(nz,dbl)), "midranks must be integer or half-integer"
    tot=sum(dbl)
    counts=[0]*(tot+1); counts[0]=1
    for w in dbl:
        nc=[0]*(tot+1)
        for s,c in enumerate(counts):
            if c:
                nc[s]+=c
                nc[s+w]+=c
        counts=nc
    N=1<<len(dbl)
    target=int(round(2*Wp))
    # two-sided: P(|W+ - mu| >= |observed - mu|), mu = tot/2, on the doubled scale
    mu2=tot/2.0
    dev=abs(target-mu2)
    hits=sum(c for s,c in enumerate(counts) if abs(s-mu2)>=dev-1e-9)
    return hits/N,Wp,len(dbl),z

def median(v):
    s=sorted(v); n=len(s)
    if n==0: return None
    return s[n//2] if n%2 else (s[n//2-1]+s[n//2])/2.0

def hodges_lehmann(d):
    """the Wilcoxon-consistent location estimate: the median of the Walsh averages."""
    n=len(d)
    w=[(d[i]+d[j])/2.0 for i in range(n) for j in range(i,n)]
    return median(w)

def hl_interval(d,alpha=ALPHA):
    """distribution-free interval for the Hodges-Lehmann estimate, from the exact null
    distribution of W+ over the non-zero Pratt ranks."""
    n=len(d)
    w=sorted((d[i]+d[j])/2.0 for i in range(n) for j in range(i,n))
    m=len(w)
    if m==0: return (None,None)
    # exact symmetric cut from the untied signed-rank null on n pairs
    tot=n*(n+1)//2
    counts=[0]*(tot+1); counts[0]=1
    for k in range(1,n+1):
        nc=[0]*(tot+1)
        for s,c in enumerate(counts):
            if c:
                nc[s]+=c
                if s+k<=tot: nc[s+k]+=c
        counts=nc
    N=1<<n; cum=0; k=0
    for s,c in enumerate(counts):
        if cum+c> alpha/2*N: k=s; break
        cum+=c
    lo=w[k] if k<m else w[0]
    hi=w[m-1-k] if m-1-k>=0 else w[-1]
    return (lo,hi)

def decide(dur_diffs,exp_diffs,n_valid_pairs):
    """the owner's intersection-union rule, verbatim:

      SUPPORTED iff n_valid_pairs >= 41
                AND p_duration < 0.05 AND p_exposure < 0.05
                AND median_duration_difference != 0 AND median_exposure_difference != 0
                AND sign(median_duration_difference) == sign(median_exposure_difference)
    """
    assert len(dur_diffs)==len(exp_diffs)==n_valid_pairs
    pd_,Wd,nzd,zd=exact_two_sided_p(dur_diffs)
    pe_,We,nze,ze=exact_two_sided_p(exp_diffs)
    md=median(dur_diffs); me=median(exp_diffs)
    sd=(0 if md==0 else (1 if md>0 else -1)); se=(0 if me==0 else (1 if me>0 else -1))
    ok_n=n_valid_pairs>=MINIMUM_VALID_PAIR_COUNT
    ok_p=(pd_<ALPHA) and (pe_<ALPHA)
    ok_m=(md!=0) and (me!=0)
    ok_s=(sd==se) and sd!=0
    supported=bool(ok_n and ok_p and ok_m and ok_s)
    return {
     "n_valid_pairs":n_valid_pairs,"MINIMUM_VALID_PAIR_COUNT":MINIMUM_VALID_PAIR_COUNT,
     "n_valid_pairs_sufficient":ok_n,
     "duration":{"W_plus":Wd,"n_nonzero":nzd,"n_zero":zd,"exact_two_sided_p":pd_,
       "median_difference":md,"hodges_lehmann":hodges_lehmann(dur_diffs),
       "hl_interval":hl_interval(dur_diffs),"rejects":pd_<ALPHA},
     "exposure":{"W_plus":We,"n_nonzero":nze,"n_zero":ze,"exact_two_sided_p":pe_,
       "median_difference":me,"hodges_lehmann":hodges_lehmann(exp_diffs),
       "hl_interval":hl_interval(exp_diffs),"rejects":pe_<ALPHA},
     "both_reject":ok_p,"both_medians_nonzero":ok_m,
     "direction_concordant":ok_s,"duration_sign":sd,"exposure_sign":se,
     "AND_RULE_PASSES":supported,
     "TERMINAL":("MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_SUPPORTED" if supported else
                 ("INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS" if not ok_n else
                  "MATCHED_LOCKED_DAUGHTER_CONTROL_EFFECT_NOT_DETECTED__INCONCLUSIVE_UNDER_FROZEN_POWER")),
     "NULL_RESULT_INTERPRETATION":"INCONCLUSIVE__NO_CLAIM_OF_EQUIVALENCE__NO_CLAIM_OF_NO_EFFECT"}

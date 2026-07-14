import numpy as np, signsafe as SS
def make(q, alphas, kappas, noise=2e-3, T=240, tp=120, seed=0):
    rng=np.random.default_rng(seed)
    prof=np.zeros(T); prof[tp:]=np.exp(-np.arange(T-tp)/40.)
    lam=1.0/np.array(alphas)                          # alpha_i = gy/a_i ; here pass alpha directly
    v=np.stack([q*(1-alphas[i]*kappas[i])*prof + rng.normal(0,noise,T) for i in range(len(alphas))])
    return v, lam, prof, tp
def coverage_by_regime(N=300):
    rng=np.random.default_rng(3); res={}
    regimes={
      'clean_anchor_mixedsign': ('anchor',None,   lambda:( [1.0,0.7,1.3], _mix_with_clean(rng) )),
      'noanchor_attenuate':     (False,'attenuate',lambda:( [1.0,0.7,1.3], list(rng.uniform(0.05,0.5,3)) )),
      'noanchor_amplify':       (False,'amplify',  lambda:( [1.0,0.7,1.3], list(-rng.uniform(0.05,0.5,3)) )),
      'noanchor_nosign':        (False,None,       lambda:( [1.0,0.7,1.3], list(rng.uniform(-0.4,0.4,3)) )),
    }
    for nm,(anch,sign,gen) in regimes.items():
        cov=0; excl=0; npoint=0; nset=0
        for t in range(N):
            q=rng.uniform(0.5,2); alphas,kappas=gen()
            anchor = (anch=='anchor')
            v,lam,prof,tp=make(q,alphas,kappas,seed=t*7+hash(nm)%1000)
            st,iset,rep=SS.identify(v,lam,tp,120,clean_anchor=anchor,sign=sign)
            qmag=q*np.std(prof[tp:])
            if st==SS.POINT: npoint+=1; ok=abs(iset[0]-qmag)<=0.12*qmag+1e-9
            elif st==SS.INTERVAL: nset+=1; ok=iset[0]*0.9<=qmag<=iset[1]*1.1
            elif st==SS.LOWER: nset+=1; ok=iset[0]<=qmag*1.06
            elif st==SS.UPPER: nset+=1; ok=iset[1]>=qmag*0.94
            else: ok=None
            if ok is True: cov+=1
            if ok is False:
                excl+=1
                if st==SS.POINT: pass
        res[nm]={'N':N,'covered':cov,'invalid':excl,'points':npoint,'sets':nset}
    return res
def _mix_with_clean(rng):
    k=[0.0, rng.uniform(-0.4,0.4), rng.uniform(-0.4,0.4)]; rng.shuffle(k); return k
def refcount(N=120):
    rng=np.random.default_rng(5); rows=[]
    for m in [1,2,3,4,5,8,12,16]:
        for s in sorted(set([0,1,min(2,m),m//2,m])):
            if s>m: continue
            good=0; refuse=0; invalid=0
            for t in range(N):
                q=rng.uniform(0.5,2)
                alphas=list(0.5+rng.uniform(0,1.5,m))
                kappas=[0.0]*m
                idx=rng.choice(m,size=s,replace=False) if s>0 else []
                for i in idx: kappas[i]=rng.uniform(0.05,0.4)*rng.choice([-1,1])
                anchor=(s<m)  # a clean ref exists iff not all contaminated
                v,lam,prof,tp=make(q,alphas,kappas,seed=t*13+m*100+s,T=240,tp=120)
                st,iset,rep=SS.identify(v,lam,tp,120,clean_anchor=anchor,sign=None)
                qmag=q*np.std(prof[tp:])
                if st in (SS.NONID,SS.ILL): refuse+=1
                elif st==SS.POINT:
                    good += abs(iset[0]-qmag)<=0.12*qmag+1e-9
                    invalid += abs(iset[0]-qmag)>0.12*qmag+1e-9
                elif st==SS.INTERVAL:
                    good += iset[0]*0.9<=qmag<=iset[1]*1.1
                    invalid += not(iset[0]*0.9<=qmag<=iset[1]*1.1)
            rows.append((m,s,good,refuse,invalid,N))
    return rows
if __name__=="__main__":
    print("COVERAGE BY SIGN REGIME (invalid = set/point excludes truth; the safety metric)")
    for k,v in coverage_by_regime().items():
        print("  %-26s covered=%d invalid=%d points=%d sets=%d /%d"%(k,v['covered'],v['invalid'],v['points'],v['sets'],v['N']))
    print("\nREFERENCE-COUNT / SPARSITY (m refs, s contaminated; anchor iff s<m)")
    print("  %-4s %-4s %-8s %-8s %-8s"%("m","s","point-ok","refuse","INVALID"))
    for m,s,g,r,inv,N in refcount():
        flag=' <-- INVALID' if inv>0 else ''
        print("  %-4d %-4d %-8d %-8d %-8d%s"%(m,s,g,r,inv,flag))

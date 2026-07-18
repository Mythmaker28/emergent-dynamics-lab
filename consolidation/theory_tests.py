import numpy as np, signsafe as SS
# synthetic channel generator directly in the algebra: v_i = q*(1-beta_i) + noise
def make(q, betas, noise=2e-3, T=240, tp=120, seed=0):
    rng=np.random.default_rng(seed)
    prof=np.zeros(T); prof[tp:]=np.exp(-np.arange(T-tp)/40.)     # response shape
    v=np.stack([q*(1-b)*prof + rng.normal(0,noise,T) for b in betas])
    lam=np.array([0.8,1.5,1.15,0.6,2.0][:len(betas)])            # distinct couplings -> good spread
    return v, lam, prof, tp
def run():
    rng=np.random.default_rng(7); res={}
    # T6-A: attenuation, no anchor -> max|v| is a LOWER bound (max|v| <= |q|)
    ok=0; N=400
    for t in range(N):
        q=rng.uniform(0.5,2); betas=rng.uniform(0.0,0.6,3)       # all attenuate, NO clean
        v,lam,prof,tp=make(q,betas,seed=t)
        st,iset,rep=SS.identify(v,lam,tp,120,clean_anchor=False,sign="attenuate")
        maxv=max(rep["amp"]); qmag=q*np.std(prof[tp:])
        ok += (st==SS.LOWER and maxv<=qmag*1.05)
    res["T6-A max|v|<=|q| (attenuate,no anchor)"]=ok/N
    # T6-B: amplification, no anchor -> min|v| is an UPPER bound (min|v| >= |q|)
    ok=0
    for t in range(N):
        q=rng.uniform(0.5,2); betas=-rng.uniform(0.05,0.6,3)     # all amplify
        v,lam,prof,tp=make(q,betas,seed=1000+t)
        st,iset,rep=SS.identify(v,lam,tp,120,clean_anchor=False,sign="amplify")
        minv=min(rep["amp"]); qmag=q*np.std(prof[tp:])
        ok += (st==SS.UPPER and minv>=qmag*0.95)
    res["T6-B min|v|>=|q| (amplify,no anchor)"]=ok/N
    # T6-C: clean anchor, mixed signs, no sign contract -> bracket covers |q|
    ok=0
    for t in range(N):
        q=rng.uniform(0.5,2)
        betas=np.array([0.0, rng.uniform(-0.5,0.5), rng.uniform(-0.5,0.5)]); rng.shuffle(betas)
        v,lam,prof,tp=make(q,betas,seed=2000+t)
        st,iset,rep=SS.identify(v,lam,tp,120,clean_anchor=True,sign=None)
        qmag=q*np.std(prof[tp:])
        lo,hi=rep["bracket"]
        ok += (st in (SS.INTERVAL,SS.POINT) and lo*0.95<=qmag<=hi*1.05)
    res["T6-C bracket covers |q| (clean anchor)"]=ok/N
    # T6-E: no anchor, no sign -> NON_IDENTIFIABLE (must refuse)
    ok=0
    for t in range(N):
        q=rng.uniform(0.5,2); betas=rng.uniform(-0.4,0.4,3)      # mixed, no guaranteed clean
        v,lam,prof,tp=make(q,betas,seed=3000+t)
        st,iset,rep=SS.identify(v,lam,tp,120,clean_anchor=False,sign=None)
        ok += (st==SS.NONID)
    res["T6-E refuses (no anchor,no sign)"]=ok/N
    return res
if __name__=="__main__":
    for k,v in run().items(): print("%-45s %.3f  %s"%(k,v,"PASS" if v>0.95 else "**CHECK**"))

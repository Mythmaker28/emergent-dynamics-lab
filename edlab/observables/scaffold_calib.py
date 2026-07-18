import numpy as np
from edlab.substrates.scaffold.engine import ScaffoldSpec, ScaffoldEngine
from edlab.experiments.exp_sc_00 import seed_state, TRACER
from edlab.observables import scaffold_refs as R

sp=ScaffoldSpec(); eng=ScaffoldEngine(sp,TRACER); n=sp.size
NAMES=list(R.REFERENCES)

def ou(T,sig,tau,rng):
    phi=np.exp(-1/tau); e=rng.normal(0,sig,T); e[0]=0; x=np.zeros(T)
    for t in range(1,T): x[t]=phi*x[t-1]+e[t]
    return x

def run(internal, drift, seed, settle=50):
    """Run with a given INITIAL internal state and an imposed nutrient drift d(t) (allowed N handle only)."""
    st=seed_state(sp,TRACER,seed,internal)
    for _ in range(settle): st=eng.step(st)
    recs={k:[] for k in NAMES}; upt=[]
    for t in range(len(drift)):
        st.N = st.N + sp.dt*sp.F*drift[t]*sp.N0     # environmental nutrient drift via the permitted N handle
        st=eng.step(st)
        r=R.read_all(st)
        for k in NAMES: recs[k].append(r[k])
        upt.append(R.response_uptake(st))
    return {k:np.array(v) for k,v in recs.items()}, np.array(upt)

def reference_matrix(seed=8001, T=200, drift_amp=0.03):
    rng=np.random.default_rng(seed)
    d=ou(T,drift_amp,40.,rng)
    # THREE internal states from the declared family: u (+response), v (-response), off (no internal drive)
    ru,uu=run("u",d,seed); rv,uv=run("v",d,seed); ro,uo=run("off",d,seed)
    s = uu-uv                                       # causal RESPONSE (what the internal state does to uptake)
    dd=d-d.mean(); sd=s-s.mean()
    A={}; K={}
    for k in NAMES:
        # drift coupling a_i: regress the OFF-run reference (no internal response) on the drift
        x=ro[k]-ro[k].mean()
        A[k]=float(x@dd/ (dd@dd))
        # contamination kappa_i: the reference's u-minus-v difference projected on the response s
        diff=(ru[k]-rv[k]); diff=diff-diff.mean()
        K[k]=float(diff@sd/(sd@sd)) if sd@sd>0 else 0.0
    return A,K,d,s

if __name__=="__main__":
    A,K,d,s=reference_matrix()
    print("response magnitude: std(uptake_u - uptake_v) = %.3e (the causal quantity)"%np.std(s))
    print()
    print("%-14s %12s %12s"%("reference","a_i (drift)","kappa_i (contam)"))
    for k in NAMES:
        print("%-14s %12.4e %12.4e"%(k,A[k],K[k]))
    # normalize a_i for conditioning (couplings up to scale)
    a=np.array([A[k] for k in NAMES]); kap=np.array([K[k] for k in NAMES])
    print()
    # pick the candidate CLEAN references (low |kappa/a|) and test their diversity
    ratio=np.abs(kap)/ (np.abs(a)+1e-30)
    order=np.argsort(ratio)
    print("cleanest references by |kappa/a|:")
    for i in order[:5]:
        print("  %-14s |kappa/a|=%.3f  a=%.3e"%(NAMES[i],ratio[i],a[i]))

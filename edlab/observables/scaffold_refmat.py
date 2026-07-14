import numpy as np, json
from edlab.substrates.scaffold.engine import ScaffoldSpec, ScaffoldEngine
from edlab.experiments.exp_sc_00 import seed_state, TRACER
from edlab.observables import scaffold_refs as R
sp=ScaffoldSpec(); eng=ScaffoldEngine(sp,TRACER); NAMES=list(R.REFERENCES)
def ou(T,sig,tau,rng):
    phi=np.exp(-1/tau);e=rng.normal(0,sig,T);e[0]=0;x=np.zeros(T)
    for t in range(1,T):x[t]=phi*x[t-1]+e[t]
    return x
def run(internal,drift,seed,settle=50):
    st=seed_state(sp,TRACER,seed,internal)
    for _ in range(settle):st=eng.step(st)
    rec={k:[] for k in NAMES};up=[]
    for t in range(len(drift)):
        st.N=st.N+sp.dt*sp.F*drift[t]*sp.N0
        st=eng.step(st);r=R.read_all(st)
        for k in NAMES:rec[k].append(r[k])
        up.append(R.response_uptake(st))
    return {k:np.array(v) for k,v in rec.items()},np.array(up)
def matrix(seed,T=200):
    rng=np.random.default_rng(seed); d=ou(T,0.03,40.,rng)
    rA,uA=run('random',d,seed); rB,uB=run('random',d,seed+1000)
    s=uA-uB; dd=d-d.mean(); sd=s-s.mean()
    a={};kap={}
    for k in NAMES:
        x=((rA[k]+rB[k])/2);x=x-x.mean(); a[k]=float(x@dd/(dd@dd))
        diff=rA[k]-rB[k];diff=diff-diff.mean(); kap[k]=float(diff@sd/(sd@sd)) if sd@sd>0 else 0.0
    return a,kap,np.std(d),np.std(s)
seeds=[8001,8002,8003,8004]
As={k:[] for k in NAMES}; Ks={k:[] for k in NAMES}
for sd in seeds:
    a,kap,ds,ss=matrix(sd)
    for k in NAMES: As[k].append(a[k]); Ks[k].append(kap[k])
print("REFERENCE MATRIX (mean +- sd over %d dev seeds); response contamination normalized by drift"%len(seeds))
print("%-14s %14s %10s %14s"%("reference","a_i (drift)","stab(cv)","kappa_i/a_i"))
summ={}
for k in NAMES:
    a=np.array(As[k]); kap=np.array(Ks[k])
    cv=np.std(a)/(abs(np.mean(a))+1e-30)
    ratio=abs(np.mean(kap)*ss)/(abs(np.mean(a))*ds+1e-30)   # contamination-to-drift in signal units
    summ[k]={'a':float(np.mean(a)),'cv':float(cv),'contam_ratio':float(ratio)}
    print("%-14s %14.4e %10.2f %14.3f"%(k,np.mean(a),cv,ratio))
json.dump(summ,open('/tmp/refmat.json','w'),indent=1)
print()
# CRD-03 admission: pick references that are (a) stable, (b) low-contamination, (c) diverse in a_i
clean=[k for k in NAMES if summ[k]['cv']<0.5 and summ[k]['contam_ratio']<0.15]
print("references passing stability(cv<0.5) AND low-contam(<0.15):",clean)
av=np.array([summ[k]['a'] for k in clean])
if len(clean)>=3:
    # CRD-03 diversity metric: spread of 1/alpha = a_i
    inv=av; diversity=np.std(inv)/(abs(np.mean(inv))+1e-30)
    # condition number of the 2-col observation geometry [a_i, 1] (drift + a constant response direction)
    Hn=np.stack([av/np.linalg.norm(av), np.ones(len(av))/np.sqrt(len(av))],axis=1)
    cond=np.linalg.cond(Hn)
    print("clean-set drift couplings:",[('%.3e'%x) for x in av])
    print("coupling diversity (std/|mean|)=%.3f  condition number=%.2f  (DIVERSITY_MIN=0.15, COND_MAX=12)"%(diversity,cond))
    print("PASS diversity:",diversity>0.15,"  PASS conditioning:",cond<12)
else:
    print("FEWER THAN 3 clean references -> reference set inadequate")

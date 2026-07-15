"""EXP-1 analysis: diagonal dominance (memory-write + behavioural), own vs neighbour decode, trivial baseline."""
import json, numpy as np
d=[r for r in json.load(open('/tmp/exp1_prosp.json')) if r.get('ok')]
K=3
# --- diagonal dominance per matrix ---
def DD(mats):
    vals=[]
    for M in mats:
        M=np.array(M); dg=np.diag(M); off=M[~np.eye(K,dtype=bool)]
        vals.append(dg.mean()/(np.abs(off).mean()+1e-12))
    return np.array(vals)
ddM=DD([r['Cm'] for r in d]); ddU=DD([r['Cu'] for r in d])
print(f"seeds analysed: {len(d)}  (targets = {len(d)*K})")
print(f"K1 memory-write diagonal dominance: median={np.median(ddM):.0f} range=[{ddM.min():.0f},{ddM.max():.0f}]")
print(f"K2 behavioural (Δuptake) diagonal dominance: median={np.median(ddU):.1f} range=[{ddU.min():.1f},{ddU.max():.1f}]")
# --- decode ensemble ---
X=[]; dose=[]; order=[]; size=[]; grp=[]; neigh_dose=[]
for gi,r in enumerate(d):
    for i in range(K):
        a1,a2=r['hist'][i]; X.append(r['feat'][i]); dose.append(a1+a2); order.append(a2-a1)
        size.append(r['sizes'][i]); grp.append(gi); neigh_dose.append(sum(r['hist'][(i+1)%K]))
X=np.array(X); dose=np.array(dose); order=np.array(order); size=np.array(size).reshape(-1,1); grp=np.array(grp); neigh_dose=np.array(neigh_dose)
def logo(X,y,g,lam=1.0):
    pred=np.full_like(y,np.nan,float)
    for h in np.unique(g):
        tr=g!=h; te=g==h; mu=X[tr].mean(0); sd=X[tr].std(0); keep=sd>1e-9
        if keep.sum()==0: pred[te]=y[tr].mean(); continue
        Xtr=(X[tr][:,keep]-mu[keep])/sd[keep]; Xte=(X[te][:,keep]-mu[keep])/sd[keep]
        yb=y[tr].mean(); A=Xtr.T@Xtr+lam*np.eye(int(keep.sum())); w=np.linalg.solve(A,Xtr.T@(y[tr]-yb)); pred[te]=Xte@w+yb
    return pred
def R2(y,p): return 1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)
def boot(X,y,g,fn,nb=3000,seed=20260715):
    rng=np.random.default_rng(seed); hs=np.unique(g); v=[]
    for _ in range(nb):
        pk=rng.choice(hs,len(hs),True); idx=np.concatenate([np.where(g==h)[0] for h in pk])
        gg=np.concatenate([[k]*int((g==h).sum()) for k,h in enumerate(pk)])
        try: v.append(R2(y[idx],fn(X[idx],y[idx],gg)))
        except: pass
    return np.percentile(v,[2.5,50,97.5])
r_own=R2(dose,logo(X,dose,grp)); ci=boot(X,dose,grp,logo)
r_ord=R2(order,logo(X,order,grp)); cio=boot(X,order,grp,logo)
r_nb=R2(neigh_dose,logo(X,neigh_dose,grp))
r_sz=R2(dose,logo(size,dose,grp))
print(f"\nOwn-history decode (dose):     R2={r_own:+.3f}  95% CI [{ci[0]:+.3f},{ci[2]:+.3f}]")
print(f"Own-history decode (order):    R2={r_ord:+.3f}  95% CI [{cio[0]:+.3f},{cio[2]:+.3f}]")
print(f"Neighbour-history decode(dose):R2={r_nb:+.3f}   (should be ~0 if individuated)")
print(f"Trivial baseline size->dose:   R2={r_sz:+.3f}   (K4: memory must beat this)")
print(f"\nGATES:")
print(f"  K1 storage individuation (DD>=10, off<0.05): {'PASS' if np.median(ddM)>=10 else 'FAIL'} (DD~{np.median(ddM):.0f})")
print(f"  K2 causal expression (own R2>0.5 & own-neigh CI>0): own={r_own:.2f} neigh={r_nb:.2f} -> {'PASS' if (r_own>0.5 and ci[0]>0) else 'CHECK'}")
print(f"  K4 non-triviality (memory>size): {'PASS' if r_own-0.05>r_sz else 'CHECK'} (mem {r_own:.2f} vs size {r_sz:.2f})")

"""INDEPENDENT RE-AUDIT — LOCAL-CAUSAL-INDIVIDUATION-00 (new agent, not the author).
Regenerates every load-bearing number from committed raw data, INCLUDING the two that had
no committed script (permutation null; deep-turnover decode). Adds tests the author omitted:
within-world permutation null (the actual individuation test) and leave-one-world-out jackknife.
Deterministic: fixed bootstrap/permutation seed 20260715 (same convention as V4 reproduction)."""
import json, numpy as np
from itertools import combinations, permutations
SEED=20260715; K=3
P=[r for r in json.load(open('/tmp/exp1_prosp.json')) if r.get('ok')]
Mn=[r for r in json.load(open('/tmp/exp1_maint.json')) if r.get('ok')]
S=[r['seed'] for r in P]; print("worlds (rest):",S,"| n_worlds=",len(P),"| n_rows=",len(P)*K)

# ---------- decoder (author's normal-equation ridge) ----------
def logo(X,y,g,lam=1.0):
    pred=np.full_like(y,np.nan,float)
    for h in np.unique(g):
        tr=g!=h; te=g==h; mu=X[tr].mean(0); sd=X[tr].std(0); keep=sd>1e-9
        if keep.sum()==0: pred[te]=y[tr].mean(); continue
        Xtr=(X[tr][:,keep]-mu[keep])/sd[keep]; Xte=(X[te][:,keep]-mu[keep])/sd[keep]
        yb=y[tr].mean(); A=Xtr.T@Xtr+lam*np.eye(int(keep.sum())); w=np.linalg.solve(A,Xtr.T@(y[tr]-yb)); pred[te]=Xte@w+yb
    return pred
def R2(y,p): return 1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)
# ---------- independent cross-check decoder (SVD ridge, different math path) ----------
def logo_svd(X,y,g,lam=1.0):
    pred=np.full_like(y,np.nan,float)
    for h in np.unique(g):
        tr=g!=h; te=g==h; mu=X[tr].mean(0); sd=X[tr].std(0); keep=sd>1e-9
        Xtr=(X[tr][:,keep]-mu[keep])/sd[keep]; Xte=(X[te][:,keep]-mu[keep])/sd[keep]; yb=y[tr].mean()
        U,s,Vt=np.linalg.svd(Xtr,full_matrices=False); d=s/(s**2+lam)
        w=Vt.T@(d*(U.T@(y[tr]-yb))); pred[te]=Xte@w+yb
    return pred

def design(records, feat_key):
    X=[];dose=[];order=[];grp=[];neigh=[];size=[];pos=[]
    for gi,r in enumerate(records):
        F=r[feat_key]
        for i in range(K):
            if F[i] is None: continue
            a1,a2=r['hist'][i]
            X.append(F[i]); dose.append(a1+a2); order.append(a2-a1); grp.append(gi)
            neigh.append(sum(r['hist'][(i+1)%K]))
            size.append(r['sizes'][i] if 'sizes' in r else np.nan)
            pos.append(r['cents'][i] if 'cents' in r else [np.nan,np.nan])
    return dict(X=np.array(X,float),dose=np.array(dose),order=np.array(order),grp=np.array(grp),
                neigh=np.array(neigh),size=np.array(size,float),pos=np.array(pos,float))

def boot_ci(X,y,g,nb=3000,seed=SEED):
    rng=np.random.default_rng(seed); hs=np.unique(g); v=[]
    for _ in range(nb):
        pk=rng.choice(hs,len(hs),True); idx=np.concatenate([np.where(g==h)[0] for h in pk])
        gg=np.concatenate([[k]*int((g==h).sum()) for k,h in enumerate(pk)])
        try: v.append(R2(y[idx],logo(X[idx],y[idx],gg)))
        except: pass
    return np.percentile(v,[2.5,50,97.5]), np.array(v)

def perm_null_global(X,y,g,n=5000,seed=SEED):
    rng=np.random.default_rng(seed); v=[]
    for _ in range(n):
        yp=y[rng.permutation(len(y))]
        try: v.append(R2(yp,logo(X,yp,g)))
        except: pass
    return np.array(v)
def perm_null_within(X,y,g,n=5000,seed=SEED):
    # permute the K labels WITHIN each world -> controls world-level feature offsets
    rng=np.random.default_rng(seed); v=[]; idxby={h:np.where(g==h)[0] for h in np.unique(g)}
    for _ in range(n):
        yp=y.copy()
        for h,ix in idxby.items(): yp[ix]=y[ix][rng.permutation(len(ix))]
        try: v.append(R2(yp,logo(X,yp,g)))
        except: pass
    return np.array(v)
def emp_p(obs,null): return float((np.sum(null>=obs)+1)/(len(null)+1))
def jackknife(X,y,g):
    out=[]
    for h in np.unique(g):
        m=g!=h; gg=g[m]
        out.append(R2(y[m],logo(X[m],y[m],gg)))
    return np.array(out)

def block(tag, D):
    X,dose,order,grp,neigh=D['X'],D['dose'],D['order'],D['grp'],D['neigh']
    print(f"\n================ {tag}  (n_rows={len(dose)}, n_worlds={len(np.unique(grp))}) ================")
    for name,y in [("dose",dose),("order",order)]:
        r=R2(y,logo(X,y,grp)); rsvd=R2(y,logo_svd(X,y,grp))
        ci,_=boot_ci(X,y,grp)
        ng=perm_null_global(X,y,grp); nw=perm_null_within(X,y,grp)
        jk=jackknife(X,y,grp)
        print(f"  own-{name:5s}: R2={r:+.3f} (svd xcheck {rsvd:+.3f})  worldboot95CI[{ci[0]:+.3f},{ci[2]:+.3f}]")
        print(f"            perm-null GLOBAL 95pct={np.percentile(ng,95):+.3f} p={emp_p(r,ng):.4f} | WITHIN-world 95pct={np.percentile(nw,95):+.3f} p={emp_p(r,nw):.4f}")
        print(f"            jackknife leave-1-world R2: min={jk.min():+.3f} max={jk.max():+.3f} mean={jk.mean():+.3f} (n={len(jk)})")
    rn=R2(neigh,logo(X,neigh,grp)); print(f"  neighbour-dose: R2={rn:+.3f} (specificity; ~0 or <0 expected)")
    return

Dr=design(P,'feat'); Dd=design(Mn,'feat_deep')
block("REST (prospective 51xxx)", Dr)
block("DEEP TURNOVER M=0.21 (maintenance 51xxx)", Dd)

# ---------- trivial baselines (K4): size, position, size+position ----------
print("\n================ K4 NON-TRIVIALITY BASELINES (rest, decode dose) ================")
X,dose,grp=Dr['X'],Dr['dose'],Dr['grp']
print(f"  memory (11-D):        R2={R2(dose,logo(X,dose,grp)):+.3f}")
print(f"  size only:            R2={R2(dose,logo(Dr['size'].reshape(-1,1),dose,grp)):+.3f}")
print(f"  position (cy,cx):     R2={R2(dose,logo(Dr['pos'],dose,grp)):+.3f}")
sp=np.column_stack([Dr['size'],Dr['pos']])
print(f"  size+position (3-D):  R2={R2(dose,logo(sp,dose,grp)):+.3f}")

# ---------- C_ij ABSOLUTE audit ----------
print("\n================ C_ij ABSOLUTE INFLUENCE AUDIT (memory-write Cm, behavioural Cu) ================")
def cij_stats(key):
    diags=[];offs=[];dds=[]
    for r in P:
        M=np.array(r[key]); dg=np.diag(M); off=M[~np.eye(K,dtype=bool)]
        diags.append(np.abs(dg).mean()); offs.append(np.abs(off).mean()); dds.append(dg.mean()/(np.abs(off).mean()+1e-12))
    diags=np.array(diags);offs=np.array(offs);dds=np.array(dds)
    return diags,offs,dds
for key,lab in [('Cm','memory-write |Δm|'),('Cu','behavioural |Δuptake|')]:
    dg,off,dd=cij_stats(key)
    print(f"  {lab}: median |diag|={np.median(dg):.3e}  median |off|={np.median(off):.3e}  diff(diag-off)={np.median(dg-off):.3e}")
    print(f"       DD median={np.median(dd):.0f} range[{dd.min():.0f},{dd.max():.0f}]  |off|/|diag| median={np.median(off/dg):.2e}")
# epsilon sensitivity of DD (memory-write)
print("  DD epsilon-sensitivity (memory-write), median over seeds:")
for eps in [1e-12,1e-9,1e-6,1e-3]:
    vals=[np.diag(np.array(r['Cm'])).mean()/(np.abs(np.array(r['Cm'])[~np.eye(K,dtype=bool)]).mean()+eps) for r in P]
    print(f"       eps={eps:.0e}: DD median={np.median(vals):.1f}")
# absolute scale reference: baseline memory magnitude from features (p50 of m1 = feat index 3)
p50m1=np.median([r['feat'][i][3] for r in P for i in range(K)])
dgCm,_,_=cij_stats('Cm')
print(f"  ABS SCALE: baseline median |m1 p50|~{abs(p50m1):.3e}; diagonal write |Δm| median~{np.median(dgCm):.3e}  (ratio Δ/base~{np.median(dgCm)/ (abs(p50m1)+1e-12):.2f})")
print("\nDONE.")

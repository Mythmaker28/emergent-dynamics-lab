import pickle, numpy as np
D=pickle.load(open("/tmp/wd01/diag.pkl","rb"))

print("="*72); print("D2  CONSTANT-DRIVE SATURATION CURVE (seed 32100, T=60 + settle)"); print("="*72)
print(" drive p |  psi_occ(|Psi|>0.9)  m1_mean  m2_mean   m+_mean  clip1  clip2  size")
for r in sorted(D["D2"], key=lambda x:x["p"]):
    f=r["feat"]
    if f is None: print(f" {r['p']:.3f}  | entity lost"); continue
    print(f" {r['p']:.3f}  |   {r['psi_occ']:.3f}            {f['m_mean'][0]:+.3f}  {f['m_mean'][1]:+.3f}   {f['mplus']:+.3f}  {f['clip1']:.2f}  {f['clip2']:.2f}  {f['size']}")

def cc(a,b):
    a=a-a.mean(); b=b-b.mean(); d=np.linalg.norm(a)*np.linalg.norm(b)
    return float(a@b/d) if d>0 else 0.0

def ridge_loo_group(F, y, lam=1.0):
    """leave-one-row-out ridge over history-level rows (F: n x d already history-aggregated)."""
    F=np.atleast_2d(F); n=len(y)
    keep=F.std(0)>1e-9; F=F[:,keep] if keep.any() else F
    mu=F.mean(0); sd=F.std(0)+1e-9; Fs=(F-mu)/sd
    A=np.column_stack([np.ones(n),Fs]); I=np.eye(A.shape[1]); I[0,0]=0; P=np.zeros(n)
    for i in range(n):
        m=np.ones(n,bool); m[i]=False
        P[i]=A[i]@np.linalg.solve(A[m].T@A[m]+lam*I, A[m].T@y[m])
    ss=((y-y.mean())**2).sum()
    return float(1-((y-P)**2).sum()/(ss+1e-12))

def sens_svd(P1,P2,M):
    """standardized linear sensitivity of memory M (n x d) to inputs [p1,p2]; return singular values of coef."""
    X=np.column_stack([P1,P2]); Xs=(X-X.mean(0))/(X.std(0)+1e-12)
    Ms=(M-M.mean(0))/(M.std(0)+1e-12)
    beta,_,_,_=np.linalg.lstsq(np.column_stack([np.ones(len(Xs)),Xs]), Ms, rcond=None)
    J=beta[1:]            # 2 x d  (d input-sensitivity rows)
    s=np.linalg.svd(J, compute_uv=False)
    return s

print("\n"+"="*72); print("D1  STORAGE RANK & DIRECT-FROM-MEMORY DECODE (grouped leave-history-out)"); print("="*72)
for cond in ("A_mismatch","B_matched_mid","C_matched_low"):
    rows=[r for r in D["D1"] if r["cond"]==cond]
    valid=[r for r in rows if r.get("valid")]
    # aggregate to history level (mean over seeds)
    His=sorted({r["hi"] for r in valid})
    P1=[];P2=[];MM=[];SP=[];clip=[]
    for hi in His:
        g=[r for r in valid if r["hi"]==hi]
        P1.append(np.mean([r["p1"] for r in g])); P2.append(np.mean([r["p2"] for r in g]))
        MM.append(np.mean([r["m_mean"] for r in g],axis=0))
        SP.append(np.mean([r["spatial"] for r in g],axis=0))
        clip.append(np.mean([[r["clip1"],r["clip2"]] for r in g],axis=0))
    P1=np.array(P1);P2=np.array(P2);MM=np.array(MM);SP=np.array(SP);clip=np.array(clip)
    nH=len(His); nlost=len(rows)-len(valid)
    print(f"\n--- {cond}:  {len(valid)}/{len(rows)} valid runs, {nH} histories, {nlost} lost(viability)")
    print(f"    design corr(p1,p2)={cc(P1,P2):+.2f}   mean clip1={clip[:,0].mean():.2f} clip2={clip[:,1].mean():.2f}")
    print(f"    collinearity corr(m1,m2)={cc(MM[:,0],MM[:,1]):+.3f}")
    s_mm=sens_svd(P1,P2,MM); s_sp=sens_svd(P1,P2,SP)
    print(f"    sensitivity SVD (entity-mean m):  s1={s_mm[0]:.2f} s2={s_mm[1]:.2f}  ratio s2/s1={s_mm[1]/s_mm[0]:.3f}")
    print(f"    sensitivity SVD (spatial 10-D):   s1={s_sp[0]:.2f} s2={s_sp[1]:.2f}  ratio s2/s1={s_sp[1]/s_sp[0]:.3f}")
    for tgt,nm in ((P1,"p1(early)"),(P2,"p2(late )")):
        r2_mm=ridge_loo_group(MM,tgt); r2_sp=ridge_loo_group(SP,tgt)
        print(f"    decode {nm}:  from entity-mean(2D) R2={r2_mm:+.2f}   from spatial(10D) R2={r2_sp:+.2f}")

import pickle, numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
D=pickle.load(open("/tmp/wd01/diag.pkl","rb"))

def cc(a,b):
    a=a-a.mean(); b=b-b.mean(); d=np.linalg.norm(a)*np.linalg.norm(b); return float(a@b/d) if d>0 else 0.0
def ridge_loo(F,y,lam=1.0):
    F=np.atleast_2d(F); n=len(y); keep=F.std(0)>1e-9; F=F[:,keep] if keep.any() else F
    Fs=(F-F.mean(0))/(F.std(0)+1e-9); A=np.column_stack([np.ones(n),Fs]); I=np.eye(A.shape[1]); I[0,0]=0; P=np.zeros(n)
    for i in range(n):
        m=np.ones(n,bool); m[i]=False; P[i]=A[i]@np.linalg.solve(A[m].T@A[m]+lam*I,A[m].T@y[m])
    return float(1-((y-P)**2).sum()/(((y-y.mean())**2).sum()+1e-12))
def sens(P1,P2,M):
    X=np.column_stack([P1,P2]); Xs=(X-X.mean(0))/(X.std(0)+1e-12); Ms=(M-M.mean(0))/(M.std(0)+1e-12)
    b,_,_,_=np.linalg.lstsq(np.column_stack([np.ones(len(Xs)),Xs]),Ms,rcond=None); s=np.linalg.svd(b[1:],compute_uv=False); return s

def agg(cond):
    v=[r for r in D["D1"] if r["cond"]==cond and r.get("valid")]
    His=sorted({r["hi"] for r in v}); P1=[];P2=[];MM=[]
    for hi in His:
        g=[r for r in v if r["hi"]==hi]; P1.append(np.mean([r["p1"] for r in g])); P2.append(np.mean([r["p2"] for r in g])); MM.append(np.mean([r["m_mean"] for r in g],0))
    return np.array(P1),np.array(P2),np.array(MM),v
conds=["A_mismatch","B_matched_mid","C_matched_low"]; labels=["A: mismatch\n(original design)","B: matched\n[0.005,0.025]","C: matched-low\n[0.001,0.006]"]

fig,ax=plt.subplots(2,2,figsize=(12,9)); fig.suptitle("EXP-SC-WRITING-DIMENSIONALITY-01  —  frozen-writing diagnostic (writing NOT modified)",fontsize=13,fontweight="bold")
# P1: saturation curve
d2=sorted(D["D2"],key=lambda x:x["p"]); ps=[r["p"] for r in d2]
m1=[r["feat"]["m_mean"][0] for r in d2]; m2=[r["feat"]["m_mean"][1] for r in d2]; occ=[r["psi_occ"] for r in d2]
a=ax[0,0]; a.plot(ps,m1,"o-",label="m1 (fast)"); a.plot(ps,m2,"s-",label="m2 (slow)"); a.plot(ps,occ,"^--",color="crimson",label="Ψ sat. occ. (proxy)")
a.axhline(1.0,color="gray",ls=":",lw=1); a.set_xscale("log"); a.set_xlabel("constant drive p (log)"); a.set_ylabel("entity-mean value")
a.set_title("D2: memory & Ψ saturate across the whole viable drive range\n(m2 already ≥0.73 at p=0.001; clip at p≳0.02)"); a.legend(fontsize=8); a.grid(alpha=.3)
# P2: collinearity scatter
a=ax[0,1]
for cond,lb,mk in zip(conds,["A","B","C"],["o","s","^"]):
    _,_,MM,_=agg(cond); a.scatter(MM[:,0],MM[:,1],label=f"{lb}: corr={cc(MM[:,0],MM[:,1]):+.2f}",alpha=.7,marker=mk)
a.set_xlabel("entity-mean m1"); a.set_ylabel("entity-mean m2"); a.set_title("Stored memory is rank-1 in every regime\n(m1,m2 near-collinear)"); a.legend(fontsize=8); a.grid(alpha=.3)
# P3: decode R2 bars
a=ax[1,0]; x=np.arange(len(conds)); w=0.35; r_p1=[];r_p2=[]
for cond in conds:
    P1,P2,MM,_=agg(cond); r_p1.append(ridge_loo(MM,P1)); r_p2.append(ridge_loo(MM,P2))
a.bar(x-w/2,r_p1,w,label="decode p1 (early)"); a.bar(x+w/2,r_p2,w,label="decode p2 (late)")
a.axhline(0.5,color="crimson",ls="--",label="G_TWO_DIMS threshold (0.5)"); a.axhline(0,color="k",lw=.8)
a.axhline(0.57,color="gray",ls=":",label="cert. p2=0.57 (row-LOO, leaky)")
a.set_xticks(x); a.set_xticklabels(labels,fontsize=8); a.set_ylabel("held-out R²  (grouped leave-history-out)")
a.set_title("Direct-from-memory decode: no regime yields 2 coords ≥0.5\n(matching ranges does NOT rescue a 2nd dimension)"); a.legend(fontsize=7); a.grid(alpha=.3,axis="y")
# P4: sensitivity SVD ratio
a=ax[1,1]; ratios=[]
for cond in conds:
    P1,P2,MM,_=agg(cond); s=sens(P1,P2,MM); ratios.append(s[1]/s[0])
a.bar(x,ratios,color="teal"); a.set_xticks(x); a.set_xticklabels(labels,fontsize=8)
a.set_ylabel("σ₂/σ₁ of (p1,p2)→(m1,m2) sensitivity"); a.set_ylim(0,1)
a.set_title("Input→memory map is rank-1 (σ₂/σ₁ ≤ 0.015)\ndecoder-independent evidence"); a.grid(alpha=.3,axis="y")
for i,r in enumerate(ratios): a.text(i,r+0.02,f"{r:.3f}",ha="center",fontsize=9)
plt.tight_layout(rect=[0,0,1,0.96]); plt.savefig("/tmp/wd01/wd01_diagnostic.png",dpi=110); print("figure saved")

# derived summary json
summ={"D2_saturation":[{"p":r["p"],"psi_occ":r["psi_occ"],"m1":r["feat"]["m_mean"][0],"m2":r["feat"]["m_mean"][1],"clip1":r["feat"]["clip1"],"clip2":r["feat"]["clip2"],"size":r["feat"]["size"]} for r in d2],
"D1_conditions":{}}
for cond in conds:
    P1,P2,MM,v=agg(cond); s=sens(P1,P2,MM)
    summ["D1_conditions"][cond]={"n_valid":len(v),"n_hist":len(P1),"collinearity_m1m2":cc(MM[:,0],MM[:,1]),
        "sens_svd_ratio":float(s[1]/s[0]),"decode_p1_R2":ridge_loo(MM,P1),"decode_p2_R2":ridge_loo(MM,P2)}
json.dump(summ,open("/tmp/wd01/diag_summary.json","w"),indent=2)
print("summary saved"); print(json.dumps(summ["D1_conditions"],indent=1))

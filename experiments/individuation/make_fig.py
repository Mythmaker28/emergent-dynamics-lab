import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
SEED=20260715; K=3
P=[r for r in json.load(open('/tmp/exp1_prosp.json')) if r.get('ok')]
Mn=[r for r in json.load(open('/tmp/exp1_maint.json')) if r.get('ok')]
def logo(X,y,g,lam=1.0):
    pred=np.full_like(y,np.nan,float)
    for h in np.unique(g):
        tr=g!=h; te=g==h; mu=X[tr].mean(0); sd=X[tr].std(0); keep=sd>1e-9
        if keep.sum()==0: pred[te]=y[tr].mean(); continue
        Xtr=(X[tr][:,keep]-mu[keep])/sd[keep]; Xte=(X[te][:,keep]-mu[keep])/sd[keep]
        yb=y[tr].mean(); A=Xtr.T@Xtr+lam*np.eye(int(keep.sum())); w=np.linalg.solve(A,Xtr.T@(y[tr]-yb)); pred[te]=Xte@w+yb
    return pred
def R2(y,p): return 1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)
def design(records,key):
    X=[];dose=[];order=[];grp=[];neigh=[];size=[];pos=[]
    for gi,r in enumerate(records):
        F=r[key]
        for i in range(K):
            if F[i] is None: continue
            a1,a2=r['hist'][i]; X.append(F[i]); dose.append(a1+a2); order.append(a2-a1); grp.append(gi)
            neigh.append(sum(r['hist'][(i+1)%K])); size.append(r['sizes'][i] if 'sizes' in r else np.nan)
            pos.append(r['cents'][i] if 'cents' in r else [0,0])
    return dict(X=np.array(X,float),dose=np.array(dose),order=np.array(order),grp=np.array(grp),
                neigh=np.array(neigh),size=np.array(size,float),pos=np.array(pos,float))
def bootci(X,y,g,nb=3000,seed=SEED):
    rng=np.random.default_rng(seed); hs=np.unique(g); v=[]
    for _ in range(nb):
        pk=rng.choice(hs,len(hs),True); idx=np.concatenate([np.where(g==h)[0] for h in pk])
        gg=np.concatenate([[k]*int((g==h).sum()) for k,h in enumerate(pk)])
        try: v.append(R2(y[idx],logo(X[idx],y[idx],gg)))
        except: pass
    return np.percentile(v,[2.5,97.5])
def nullg(X,y,g,n=5000,seed=SEED):
    rng=np.random.default_rng(seed); v=[]
    for _ in range(n):
        yp=y[rng.permutation(len(y))]
        try:v.append(R2(yp,logo(X,yp,g)))
        except:pass
    return np.array(v)
def nullw(X,y,g,n=5000,seed=SEED):
    rng=np.random.default_rng(seed); v=[]; ib={h:np.where(g==h)[0] for h in np.unique(g)}
    for _ in range(n):
        yp=y.copy()
        for h,ix in ib.items(): yp[ix]=y[ix][rng.permutation(len(ix))]
        try:v.append(R2(yp,logo(X,yp,g)))
        except:pass
    return np.array(v)
def jack(X,y,g):
    return np.array([R2(y[g!=h],logo(X[g!=h],y[g!=h],g[g!=h])) for h in np.unique(g)])
Dr=design(P,'feat'); Dd=design(Mn,'feat_deep')
# core numbers
res={}
for tag,D in [('rest',Dr),('deep',Dd)]:
    for nm,y in [('dose',D['dose']),('order',D['order'])]:
        r=R2(y,logo(D['X'],y,D['grp'])); ci=bootci(D['X'],y,D['grp']); jk=jack(D['X'],y,D['grp'])
        res[f'{tag}_{nm}']=dict(r2=float(r),ci=[float(ci[0]),float(ci[1])],jk=[float(jk.min()),float(jk.max())])
    res[f'{tag}_neigh']=float(R2(D['neigh'],logo(D['X'],D['neigh'],D['grp'])))
res['rest_size']=float(R2(Dr['dose'],logo(Dr['size'].reshape(-1,1),Dr['dose'],Dr['grp'])))
res['rest_pos']=float(R2(Dr['dose'],logo(Dr['pos'],Dr['dose'],Dr['grp'])))
ng=nullg(Dr['X'],Dr['order'],Dr['grp']); nw=nullw(Dr['X'],Dr['order'],Dr['grp'])
res['order_null_global_95']=float(np.percentile(ng,95)); res['order_null_within_95']=float(np.percentile(nw,95))
ngd=nullg(Dr['X'],Dr['dose'],Dr['grp']); nwd=nullw(Dr['X'],Dr['dose'],Dr['grp'])
res['dose_null_global_95']=float(np.percentile(ngd,95)); res['dose_null_within_95']=float(np.percentile(nwd,95))
res['dose_null_within_p']=float((np.sum(nwd>=res['rest_dose']['r2'])+1)/(len(nwd)+1))
res['order_null_within_p']=float((np.sum(nw>=res['rest_order']['r2'])+1)/(len(nw)+1))
res['deep_dose_null_within_p']=float((np.sum(nullw(Dd['X'],Dd['dose'],Dd['grp'])>=res['deep_dose']['r2'])+1)/5001)
# Cij absolute
def cij(key):
    dg=[];off=[]
    for r in P:
        M=np.array(r[key]); dg.append(np.abs(np.diag(M)).mean()); off.append(np.abs(M[~np.eye(K,dtype=bool)]).mean())
    return np.array(dg),np.array(off)
dgm,offm=cij('Cm'); dgu,offu=cij('Cu')
res['Cm_diag_med']=float(np.median(dgm)); res['Cm_off_med']=float(np.median(offm))
res['Cu_diag_med']=float(np.median(dgu)); res['Cu_off_med']=float(np.median(offu))
res['DD_mem_med']=float(np.median(dgm/(offm+1e-12))); res['DD_beh_med']=float(np.median(dgu/(offu+1e-12)))
json.dump(res,open('/tmp/indiv/reaudit_summary.json','w'),indent=2)

# ---------------- FIGURE ----------------
plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':0.25})
fig=plt.figure(figsize=(13,9)); gs=GridSpec(2,2,figure=fig,hspace=0.34,wspace=0.24)
C1,C2,CN,CB='#1f77b4','#d62728','#7f7f7f','#2ca02c'
# A: rest decode bars
axA=fig.add_subplot(gs[0,0])
labels=['own\norder','own\ndose','neighbour\ndose','size','position']
vals=[res['rest_order']['r2'],res['rest_dose']['r2'],res['rest_neigh'],res['rest_size'],res['rest_pos']]
cols=[C1,C1,CN,'#bbbbbb','#bbbbbb']
bars=axA.bar(labels,vals,color=cols,edgecolor='k',linewidth=0.6)
# jackknife whiskers on own bars
for i,k in [(0,'rest_order'),(1,'rest_dose')]:
    lo,hi=res[k]['jk']; axA.plot([i,i],[lo,hi],color='k',lw=2)
axA.axhline(res['order_null_within_95'],ls='--',color=C2,lw=1.2,label='within-world null 95%')
axA.axhline(0,color='k',lw=0.8)
axA.set_ylabel('grouped LOGO $R^2$ (own history)'); axA.set_title('A. Rest: own-history readout is specific & non-trivial')
axA.legend(fontsize=8,loc='upper right'); axA.set_ylim(-0.5,0.95)
axA.text(0.02,0.02,'own ≫ neighbour ≈ baselines\njackknife bars = leave-1-world range',transform=axA.transAxes,fontsize=7.5,va='bottom')
# B: rest vs deep, dose & order, with CI, 0.5 threshold
axB=fig.add_subplot(gs[0,1])
pts=[('rest_order','rest\norder',C1),('deep_order','deep\norder',C2),
     ('rest_dose','rest\ndose',C1),('deep_dose','deep\ndose',C2)]
for j,(k,lab,c) in enumerate(pts):
    r=res[k]['r2']; lo,hi=res[k]['ci']
    axB.errorbar(j,r,yerr=[[r-lo],[hi-r]],fmt='o',color=c,capsize=4,ms=8)
axB.set_xticks(range(4)); axB.set_xticklabels([p[1] for p in pts])
axB.axhline(0.5,ls='--',color='k',lw=1.1,label='0.50 certification bar')
axB.axhline(0,color='gray',lw=0.8)
axB.set_ylabel('$R^2$ (world-bootstrap 95% CI)'); axB.set_title('B. Turnover: dose partly retained, order lost')
axB.legend(fontsize=8); axB.set_ylim(-1.0,1.0)
axB.annotate('dose: sig>null,\nnot certified >0.5',(3,res['deep_dose']['r2']),xytext=(2.3,-0.55),fontsize=7.5,
             arrowprops=dict(arrowstyle='->',lw=0.7))
# C: Cij absolute log
axC=fig.add_subplot(gs[1,0])
cats=['mem |Δm|\ndiag','mem |Δm|\noff','behav |Δu|\ndiag','behav |Δu|\noff']
cv=[res['Cm_diag_med'],res['Cm_off_med'],res['Cu_diag_med'],res['Cu_off_med']]
cc=['#1f77b4','#9ecae1','#2ca02c','#a1d99b']
axC.bar(cats,cv,color=cc,edgecolor='k',linewidth=0.6); axC.set_yscale('log')
axC.set_ylabel('median |Δ| (log)'); axC.set_title('C. Influence matrix is diagonal in ABSOLUTE terms')
axC.text(0.02,0.95,f"DD_mem≈{res['DD_mem_med']:.0f}   DD_behav≈{res['DD_beh_med']:.0f}\ndiagonal write ≈11× baseline memory",
         transform=axC.transAxes,fontsize=8,va='top')
# D: null distributions for own-order
axD=fig.add_subplot(gs[1,1])
axD.hist(ng,bins=40,color=CN,alpha=0.6,density=True,label='global null')
axD.hist(nw,bins=40,color=C2,alpha=0.5,density=True,label='within-world null')
axD.axvline(res['rest_order']['r2'],color=C1,lw=2.5,label=f"observed order R²={res['rest_order']['r2']:.2f}")
axD.axvline(0.5,ls='--',color='k',lw=1)
axD.set_xlabel('$R^2$ under label permutation'); axD.set_ylabel('density')
axD.set_title(f"D. Own-order beats within-world null (p={res['order_null_within_p']:.4f})")
axD.legend(fontsize=8)
fig.suptitle('LOCAL-CAUSAL-INDIVIDUATION-00 — independent re-audit (rest storage/readout real; behavioural-causal claim not shown; turnover: dose partial, order lost)',
             fontsize=11,y=0.985)
fig.savefig('/tmp/indiv/figure_individuation_audit.png',dpi=140,bbox_inches='tight')
print("figure + summary written")
print(json.dumps(res,indent=2))

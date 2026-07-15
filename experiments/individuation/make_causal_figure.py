"""Simple confirmation figure for Tommy: existence, causal matrix, storage replication."""
import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
SEED = 20260715; K = 3
raw = json.load(open("/tmp/causal_confirmation_52xxx.json")); recs = [r for r in raw if r.get("ok")]
nW = len(recs)

# per-world own effect + controls
def eff(r):
    b = r["beh"]; A = b["intact"]; er = b["erase"]; E = b["ablate"]; erabl = b["erase_ablate"]
    S = b["sham"]; Ares = b["intact_res"]; erres = b["erase_res"]; Al = b["intact_long"]; erl = b["erase_long"]
    own = np.mean([A["integ_upt"][i]-er[i]["integ_upt"][i] for i in range(K)])
    abl = np.mean([E["integ_upt"][i]-erabl[i]["integ_upt"][i] for i in range(K)])
    sham = np.mean([A["integ_upt"][i]-S["integ_upt"][i] for i in range(K)])
    neigh = np.mean([np.mean([A["integ_upt"][i]-er[j]["integ_upt"][i] for j in range(K) if j!=i]) for i in range(K)])
    res = np.mean([Ares["integ_upt"][i]-erres[i]["integ_upt"][i] for i in range(K)])
    lon = np.mean([Al["integ_upt"][i]-erl[i]["integ_upt"][i] for i in range(K)])
    return own, abl, sham, neigh, res, lon
E = np.array([eff(r) for r in recs]); own, abl, sham, neigh, res, lon = E.T
rng = np.random.default_rng(SEED)
bs = np.array([own[rng.integers(0,nW,nW)].mean() for _ in range(5000)]); ci = np.percentile(bs,[2.5,97.5])

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
fig.suptitle("LCI-CAUSAL-CONFIRMATION-01 — non-confounded behavioural causal test of local memory (52001–52024, 13 worlds)", fontsize=12, fontweight="bold")

# Panel 1: existence — per-world own effect
ax[0].axhline(0, color="k", lw=0.8)
ax[0].scatter(np.arange(nW), np.sort(own), s=42, color="#1f77b4", zorder=3)
ax[0].axhspan(ci[0], ci[1], color="#1f77b4", alpha=0.15)
ax[0].axhline(own.mean(), color="#1f77b4", lw=1.5, label=f"mean {own.mean():.2f}\n95%CI[{ci[0]:.2f},{ci[1]:.2f}]")
ax[0].set_title("A. Causal existence\nown-erase effect (intact − erase-target)", fontsize=10)
ax[0].set_xlabel("world (sorted)"); ax[0].set_ylabel("Δ integrated feeding")
ax[0].legend(fontsize=8, loc="upper left"); ax[0].text(0.5,0.03,f"{int((own>0).sum())}/{nW} worlds >0",transform=ax[0].transAxes,fontsize=9,color="#1f77b4")

# Panel 2: causal matrix
labs = ["own\nerase", "washout\nsurvival", "no-reset\n(double-diss)", "neighbour\nerase", "sham", "ablation\n(λ=0)"]
vals = [own.mean(), lon.mean(), res.mean(), neigh.mean(), sham.mean(), abl.mean()]
cols = ["#1f77b4", "#1f77b4", "#2ca02c", "#ff7f0e", "#ff7f0e", "#d62728"]
ax[1].bar(range(6), vals, color=cols)
ax[1].axhline(0, color="k", lw=0.8)
for i, v in enumerate(vals): ax[1].text(i, v + 0.05, f"{v:.2f}", ha="center", fontsize=8)
ax[1].set_xticks(range(6)); ax[1].set_xticklabels(labs, fontsize=8)
ax[1].set_title("B. Causal matrix (mean Δ feeding)\nmemory-caused ≫ controls; ablation→0", fontsize=10)
ax[1].set_ylabel("Δ integrated feeding")

# Panel 3: storage decode (own vs neighbour dose R2)
def logo(X,y,g,lam=1.0):
    pred=np.full_like(y,np.nan,float)
    for h in np.unique(g):
        tr=g!=h;te=g==h;mu=X[tr].mean(0);sd=X[tr].std(0);keep=sd>1e-9
        Xtr=(X[tr][:,keep]-mu[keep])/sd[keep];Xte=(X[te][:,keep]-mu[keep])/sd[keep]
        yb=y[tr].mean();A=Xtr.T@Xtr+lam*np.eye(int(keep.sum()));w=np.linalg.solve(A,Xtr.T@(y[tr]-yb));pred[te]=Xte@w+yb
    return pred
def R2(y,p): return 1-np.sum((y-p)**2)/np.sum((y-y.mean())**2)
X=[];dose=[];g=[];nb=[]
for gi,r in enumerate(recs):
    for i in range(K):
        X.append(r["feat"][i]); dose.append(sum(r["hist"][i])); g.append(gi); nb.append(sum(r["hist"][(i+1)%K]))
X=np.array(X);dose=np.array(dose);g=np.array(g);nb=np.array(nb)
pr=logo(X,dose,g)
ax[2].scatter(dose, pr, s=36, color="#1f77b4")
lo,hi=dose.min(),dose.max(); ax[2].plot([lo,hi],[lo,hi],"k--",lw=0.8)
ax[2].set_title(f"C. Storage readout replicated\nown-dose R²={R2(dose,pr):.2f} (neighbour {R2(nb,logo(X,nb,g)):+.2f})", fontsize=10)
ax[2].set_xlabel("true own dose"); ax[2].set_ylabel("decoded dose (LOGO)")

plt.tight_layout(rect=[0,0,1,0.94])
plt.savefig("/root/lci/work/CAUSAL_CONFIRMATION_FIGURE_01.png", dpi=130)
print("figure saved")

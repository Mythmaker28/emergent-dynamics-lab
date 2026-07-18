"""Two-panel figure (deliverables 16,17) from raw artifacts only."""
import json,glob,hashlib,os,collections,math,numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="../docs/point_cert/figures"; os.makedirs(OUT,exist_ok=True)
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
def band(s): return "<=5" if s<=5 else ("5-10" if s<=10 else ("10-30" if s<=30 else ">30"))
def wilson(k,n,z=1.96):
    if n==0: return (0,0,0)
    p=k/n; den=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return (p,(c-h)/den,(c+h)/den)
old=json.load(open("../consolidation/HOLDOUT_RESULTS.json"))
nasi=[]
for f in sorted(glob.glob("../results/EXP-GT-NASI-PROSPECTIVE/rows_*.json")): nasi+=json.load(open(f))
pc=[]
for f in sorted(glob.glob("../results/EXP-GT-PC-PROSPECTIVE/rows_*.json")): pc+=json.load(open(f))
order=["<=5","5-10","10-30",">30"]
fig,(axA,axB)=plt.subplots(1,2,figsize=(11,4))
def fz_old():
    d=collections.defaultdict(lambda:[0,0])
    for r in old["rows"]["oracle"]:
        if not r.get("emitted"): continue
        b="<=5" if r["snr"]<=5 else ("5-10" if r["snr"]<=10 else ("10-30" if r["snr"]<=30 else ">30"))
        d[b][1]+=1; d[b][0]+=(r["valid"] is False)
    return d
def fz(rows,zkey):
    d=collections.defaultdict(lambda:[0,0])
    for r in rows:
        if not r.get("nonzero"): continue
        d[band(r["snr"])][1]+=1; d[band(r["snr"])][0]+=bool(r.get(zkey))
    return d
series=[("old sign-safe",fz_old(),"#c0392b"),("NASI set",fz(nasi,"exact_zero"),"#2980b9"),("point-certified",fz(pc,"false0"),"#27ae60")]
for k,(name,d,col) in enumerate(series):
    xs=[]; y=[]; lo=[]; hi=[]
    for i,bnd in enumerate(order):
        if d[bnd][1]:
            p,l,h=wilson(d[bnd][0],d[bnd][1]); xs.append(i+0.08*(k-1)); y.append(p); lo.append(max(0,p-l)); hi.append(max(0,h-p))
    axA.errorbar(xs,y,yerr=[lo,hi],fmt="o-",color=col,label=name,capsize=3)
axA.set_xticks(range(4)); axA.set_xticklabels(order); axA.set_xlabel("SNR band"); axA.set_ylabel("P(Q={0} | q!=0)")
axA.set_title("Panel A: false exact-zero rate"); axA.legend(fontsize=8); axA.set_ylim(-0.03,1.03)
issued=[r for r in pc if r["point_issued"]]
reg=collections.defaultdict(lambda:[0,0])
for r in issued:
    g="dropout" if r["has_dropout"] else ("sparse" if r["stratum"]=="sparse1" else ("contam_highSNR" if r["stratum"]=="contaminated_highSNR" else "other"))
    reg[g][1]+=1; reg[g][0]+=(r["point_contains"] is False)
cata=sum(1 for r in issued if r["catastrophic"])
labels=list(reg.keys()); rates=[reg[k][0]/reg[k][1] for k in labels]
errs=[[],[]]
for k in labels:
    p,l,h=wilson(reg[k][0],reg[k][1]); errs[0].append(max(0,p-l)); errs[1].append(max(0,h-p))
axB.bar(labels,rates,yerr=errs,capsize=4,color=["#8e44ad","#16a085","#c0392b","#7f8c8d"][:len(labels)])
for i,k in enumerate(labels):
    axB.text(i,rates[i]+0.05,f"{reg[k][0]}/{reg[k][1]}",ha="center",fontsize=8)
axB.axhline(0.05,ls="--",color="k",lw=1,label="5% reference")
ch=labels.index("contam_highSNR") if "contam_highSNR" in labels else None
if ch is not None: axB.annotate("stable unidentified bias",(ch,rates[ch]),xytext=(ch-0.3,0.8),fontsize=8,arrowprops=dict(arrowstyle="->"))
axB.set_ylabel("P(q not in I_point | issued)"); axB.set_ylim(0,1.0); axB.legend(fontsize=7)
gtot=sum(reg[k][0] for k in labels); gden=sum(reg[k][1] for k in labels)
axB.set_title(f"Panel B: invalid point-cert rate by regime\nglobal {gtot}/{gden}, catastrophic {cata}/{gden}")
plt.tight_layout()
outp=os.path.join(OUT,"fig_pc_twopanel.png"); fig.savefig(outp,dpi=110,bbox_inches="tight"); plt.close(fig)
json.dump([dict(figure="fig_pc_twopanel.png",
   panelA="false exact-zero rate by SNR: old sign-safe vs NASI vs point-certified",
   panelB=f"invalid point-cert rate by regime; catastrophic={cata}",
   sources=[{"file":"../consolidation/HOLDOUT_RESULTS.json","sha256":sha("../consolidation/HOLDOUT_RESULTS.json")}],
   artifact_sha256=sha(outp))], open(os.path.join(OUT,"figure_provenance.json"),"w"),indent=1)
print("two-panel figure written; catastrophic on issued points =",cata)

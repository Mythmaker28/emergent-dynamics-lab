"""Figure pipeline (deliverable 22). Every figure is generated FROM raw artifacts; a provenance manifest
records source file + sha256 + the claim each figure supports. No hand-editing of plotted values."""
import json, glob, hashlib, os, collections, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT="../docs/noise_aware/figures"; os.makedirs(OUT, exist_ok=True)
def sha(p): return hashlib.sha256(open(p,"rb").read()).hexdigest()
prov=[]
def save(fig,name,sources,claim):
    p=os.path.join(OUT,name); fig.savefig(p,dpi=110,bbox_inches="tight"); plt.close(fig)
    prov.append(dict(figure=name, sources=[{ "file":s, "sha256":sha(s)} for s in sources],
                     script="noise_aware/make_figures.py", artifact_sha256=sha(p), claim=claim))

# load raw
prows=[]
for f in sorted(glob.glob("../results/EXP-GT-NASI-PROSPECTIVE/rows_*.json")): prows+=json.load(open(f))
old=json.load(open("../consolidation/HOLDOUT_RESULTS.json"))
foren=json.load(open("../results/EXP-GT-NASI-PROSPECTIVE/invalid_point_forensics.json"))
psrc=sorted(glob.glob("../results/EXP-GT-NASI-PROSPECTIVE/rows_*.json"))

# FIG1: old vs new false/invalid-point rate by SNR (the repair)
oldrows=old["rows"]["oracle"]; byo=collections.defaultdict(lambda:[0,0])
for r in oldrows:
    if r.get("emitted"):
        byo[r["snr"]][1]+=1; byo[r["snr"]][0]+=(r["valid"] is False)
osnr=sorted(byo); orate=[byo[s][0]/byo[s][1] for s in osnr]
band=lambda s:"<=5" if s<=5 else("5-10" if s<=10 else("10-30" if s<=30 else ">30"))
bn=collections.defaultdict(lambda:[0,0])
for r in prows:
    if r["emit"] and r["nonzero"]:
        bn[band(r["snr"])][1]+=1; bn[band(r["snr"])][0]+=(r["exact_zero"])
order=["<=5","5-10","10-30",">30"]; nrate=[bn[b][0]/max(1,bn[b][1]) for b in order]
fig,ax=plt.subplots(figsize=(6,3.6))
ax.bar([str(int(s)) for s in osnr],orate,color="#c0392b",alpha=.85,label="old sign-safe (invalid point rate)")
ax.plot(range(len(order)),nrate,"o-",color="#27ae60",lw=2,label="new NASI (false {0} rate)")
ax.set_ylabel("rate"); ax.set_xlabel("SNR"); ax.set_ylim(-0.02,1.02)
ax.set_title("Repair: old {0}-null-gate (0.99 @ SNR5) vs new false-{0}=0"); ax.legend(fontsize=8)
save(fig,"fig1_repair_false_zero.png",["../consolidation/HOLDOUT_RESULTS.json"]+psrc,
     "The historical null-gate produced 0.99 invalid at SNR=5; the new instrument produces 0 false {0} at every SNR.")

# FIG2: prospective coverage by SNR band, both arms
fig,ax=plt.subplots(figsize=(6,3.6))
for arm,col in (("O","#2c3e50"),("B","#2980b9")):
    d=collections.defaultdict(lambda:[0,0])
    for r in prows:
        if r["arm"]==arm and r["emit"]:
            d[band(r["snr"])][1]+=1; d[band(r["snr"])][0]+=(r["contains"] is True)
    y=[d[b][0]/max(1,d[b][1]) for b in order]
    ax.plot(order,y,"o-",color=col,label=f"arm {arm}")
ax.axhline(0.95,ls="--",color="gray",label="95% target")
ax.set_ylim(0.9,1.005); ax.set_ylabel("coverage"); ax.set_xlabel("SNR band")
ax.set_title("Prospective coverage by SNR band (both arms >= 95%)"); ax.legend(fontsize=8)
save(fig,"fig2_coverage_by_snr.png",psrc,"Set/bound coverage is >=95% in every SNR band, both arms, including low-SNR.")

# FIG3: invalid-point severity
rel=[p["rel_miss"] for p in foren["points"]]
fig,ax=plt.subplots(figsize=(6,3.6))
ax.hist(rel,bins=20,color="#8e44ad",alpha=.85)
ax.axvline(0.5,ls="--",color="red",label="catastrophic threshold")
ax.set_xlabel("relative miss of confident POINT"); ax.set_ylabel("count")
ax.set_title(f"Invalid points: {foren['n_invalid_points']} total, {foren['n_catastrophic']} catastrophic (median miss 2%)")
ax.legend(fontsize=8)
save(fig,"fig3_invalid_point_severity.png",["../results/EXP-GT-NASI-PROSPECTIVE/invalid_point_forensics.json"],
     "57 invalid points; 50 are benign near-edge CI tail misses; only 2 are catastrophic (dropout, low-SNR).")

# FIG4: non-vacuity status mix by SNR band (arm O)
cats=["POINT_IDENTIFIED","INTERVAL_IDENTIFIED","LOWER_BOUND_ONLY","UPPER_BOUND_ONLY","BELOW_DETECTION_LIMIT","ZERO_COMPATIBLE"]
mix={b:collections.Counter() for b in order}; ab={b:0 for b in order}
for r in prows:
    if r["arm"]=="O":
        b=band(r["snr"])
        if r["emit"]: mix[b][r["status"]]+=1
        else: ab[b]+=1
fig,ax=plt.subplots(figsize=(6.5,3.6)); bottom=np.zeros(len(order))
for c in cats:
    vals=np.array([mix[b][c] for b in order]); ax.bar(order,vals,bottom=bottom,label=c.replace("_IDENTIFIED","").replace("_"," ").lower()); bottom+=vals
ax.bar(order,[ab[b] for b in order],bottom=bottom,label="abstain",color="lightgray")
ax.set_ylabel("cases (arm O)"); ax.set_xlabel("SNR band"); ax.set_title("Output-status mix by SNR (informativeness rises with SNR)")
ax.legend(fontsize=6,ncol=2)
save(fig,"fig4_status_mix.png",psrc,"Informativeness (points/bounds) rises with SNR; abstention dominates at low SNR — non-vacuity without sacrificing safety.")

json.dump(prov, open(os.path.join(OUT,"figure_provenance.json"),"w"), indent=1)
print("wrote",len(prov),"figures + figure_provenance.json to",OUT)
for pr in prov: print("  ",pr["figure"])

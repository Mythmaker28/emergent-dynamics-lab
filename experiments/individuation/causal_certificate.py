"""Evaluate the FROZEN gates on the sealed confirmation raw (no new hyperparameters; frozen seed 20260715)."""
import json, sys, numpy as np
SEED = 20260715; K = 3
raw = json.load(open(sys.argv[1])); recs = [r for r in raw if r.get("ok")]
nW = len(recs); print(f"eligible worlds={nW}/{len(raw)}  droplets={nW*K}")

def wb_ci(perworld, nb=5000, seed=SEED):
    rng = np.random.default_rng(seed); n = len(perworld)
    bs = np.array([perworld[rng.integers(0, n, n)].mean() for _ in range(nb)])
    return np.percentile(bs, [2.5, 50, 97.5])

# ---- gather per-droplet effects + per-world means ----
rows = []
for r in recs:
    b = r["beh"]; A = b["intact"]; er = b["erase"]; E = b["ablate"]; erabl = b["erase_ablate"]
    S = b["sham"]; Ares = b["intact_res"]; erres = b["erase_res"]; Al = b["intact_long"]; erl = b["erase_long"]
    m = np.array(A["mass"], float)
    for i in range(K):
        rows.append(dict(seed=r["seed"], i=i, dose=r["dose"][i],
            own=A["integ_upt"][i]-er[i]["integ_upt"][i],
            own_spec=(A["integ_upt"][i]-er[i]["integ_upt"][i])/max(m[i],1e-9),
            own_fixed=A["integ_fixed"][i]-er[i]["integ_fixed"][i],
            abl=E["integ_upt"][i]-erabl[i]["integ_upt"][i],
            sham=A["integ_upt"][i]-S["integ_upt"][i],
            neigh=np.mean([A["integ_upt"][i]-er[j]["integ_upt"][i] for j in range(K) if j!=i]),
            res=Ares["integ_upt"][i]-erres[i]["integ_upt"][i],
            lon=Al["integ_upt"][i]-erl[i]["integ_upt"][i]))
def col(k): return np.array([x[k] for x in rows], float)
def perworld(k):
    out=[];
    for r in recs:
        idx=[j for j,x in enumerate(rows) if x["seed"]==r["seed"]]
        out.append(np.mean([rows[j][k] for j in idx]))
    return np.array(out)

own=col("own"); own_spec=col("own_spec"); own_fixed=col("own_fixed")
abl=col("abl"); sham=col("sham"); neigh=col("neigh"); res=col("res"); lon=col("lon")

pw_own = perworld("own"); pw_spec = perworld("own_spec"); pw_fixed = perworld("own_fixed"); pw_lon = perworld("lon")
ci_own = wb_ci(pw_own); ci_spec = wb_ci(pw_spec); ci_fixed = wb_ci(pw_fixed); ci_lon = wb_ci(pw_lon)

# ---- C-K1 storage influence DD ----
def dd(key):
    diags=[];offs=[];dds=[]
    for r in recs:
        M=np.array(r[key]); dg=np.diag(M); off=M[~np.eye(K,dtype=bool)]
        diags.append(np.abs(dg).mean()); offs.append(np.abs(off).mean()); dds.append(dg.mean()/(np.abs(off).mean()+1e-12))
    return np.median(diags),np.median(offs),np.median(dds)
dmg=dd("Cm"); dug=dd("Cu")

print("\n===== GATE CERTIFICATE (frozen thresholds) =====")
print(f"[C-K1 storage] DD_mem median={dmg[2]:.0f} (>=10) |diag|={dmg[0]:.3e} |off|={dmg[1]:.3e} (<0.05) -> {'PASS' if dmg[2]>=10 and dmg[1]<0.05 else 'FAIL'}")
print(f"[G3a existence] eff_own per-world worldboot95 CI=[{ci_own[0]:+.3e},{ci_own[2]:+.3e}] median={ci_own[1]:+.3e}; worlds>0 {int((pw_own>0).sum())}/{nW}; SNR={pw_own.mean()/(pw_own.std(ddof=1)/np.sqrt(nW)):.2f} -> {'PASS' if ci_own[0]>0 else 'FAIL'}")
print(f"        specific eff worldboot95 CI=[{ci_spec[0]:+.3e},{ci_spec[2]:+.3e}] -> {'PASS' if ci_spec[0]>0 else 'FAIL'}")
r_abl=np.abs(abl).mean()/(np.abs(own).mean()+1e-12); print(f"[G3b ablation collapse] |abl|/|own|={r_abl:.4f} (<0.15) -> {'PASS' if r_abl<0.15 else 'FAIL'}")
r_ne=np.abs(neigh).mean()/(np.abs(own).mean()+1e-12); print(f"[G3c neighbour locality] |neigh|/|own|={r_ne:.4f} (<0.35) -> {'PASS' if r_ne<0.35 else 'FAIL'}")
r_sh=np.abs(sham).mean()/(np.abs(own).mean()+1e-12); print(f"[G3d sham null] |sham|/|own|={r_sh:.4f} (<0.15) -> {'PASS' if r_sh<0.15 else 'FAIL(marginal)'}; own-sham corrected eff={own.mean()-sham.mean():+.3e} (own/sham={np.abs(own).mean()/(np.abs(sham).mean()+1e-12):.1f}x)")
ratio=res.mean()/(own.mean()+1e-12); print(f"[G3e double-diss] eff_res={res.mean():+.3e} ratio res/own={ratio:.3f} (0.5..2, >0) -> {'PASS' if (res.mean()>0 and 0.5<ratio<2.0) else 'FAIL'}")
print(f"[G3f washout survival] eff_long per-world worldboot95=[{ci_lon[0]:+.3e},{ci_lon[2]:+.3e}] worlds>0 {int((pw_lon>0).sum())}/{nW} -> {'PASS' if ci_lon[0]>0 else 'FAIL'}")
print(f"[C-K5 tracker-indep] eff_own_FIXED worldboot95=[{ci_fixed[0]:+.3e},{ci_fixed[2]:+.3e}] worlds>0 {int((pw_fixed>0).sum())}/{nW} -> {'PASS' if ci_fixed[0]>0 else 'FAIL'}")
g3 = (ci_own[0]>0 and r_abl<0.15 and r_ne<0.35 and r_sh<0.15 and res.mean()>0 and 0.5<ratio<2.0 and ci_lon[0]>0 and ci_fixed[0]>0)
print(f"\n>>> G3 behavioural causal expression: {'ESTABLISHED' if g3 else 'NOT ESTABLISHED'}")

# per-seed table
print("\nseed  | minDist | dose(mean) | eff_own(3) | eff_long | eff_abl")
for r in recs:
    idx=[j for j,x in enumerate(rows) if x["seed"]==r["seed"]]
    eo=[rows[j]["own"] for j in idx]; el=np.mean([rows[j]["lon"] for j in idx]); ea=np.mean([rows[j]["abl"] for j in idx])
    print(f"{r['seed']} | {min(r['dists']):5.1f}   | {np.mean(r['dose']):.3f}      | {[round(x,2) for x in eo]} | {el:+.2f}   | {ea:+.2e}")

out={"eligible_worlds":nW,"seeds":[r["seed"] for r in recs],
 "C-K1":{"DD_mem":dmg[2],"diag":dmg[0],"off":dmg[1],"DD_behav":dug[2]},
 "G3":{"established":bool(g3),"eff_own_worldCI":list(ci_own),"eff_spec_worldCI":list(ci_spec),
   "worlds_pos":int((pw_own>0).sum()),"SNR":float(pw_own.mean()/(pw_own.std(ddof=1)/np.sqrt(nW))),
   "ablation_ratio":float(r_abl),"neighbour_ratio":float(r_ne),"sham_ratio":float(r_sh),
   "doublediss_ratio":float(ratio),"washout_survival_CI":list(ci_lon),"fixed_mask_CI":list(ci_fixed),
   "own_minus_sham":float(own.mean()-sham.mean())}}
json.dump(out, open("/root/lci/work/gate_cert.json","w"), indent=2)
print("\nsaved /root/lci/work/gate_cert.json")

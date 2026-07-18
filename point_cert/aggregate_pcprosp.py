import json,glob,collections,math,numpy as np
rows=[]
for f in sorted(glob.glob("../results/EXP-GT-PC-PROSPECTIVE/rows_*.json")): rows+=json.load(open(f))
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; den=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)); return ((c-h)/den,(c+h)/den)
print(f"TOTAL rows={len(rows)} cases={len(rows)//2}")
rep={}
for arm in ("O","B"):
    R=[r for r in rows if r["arm"]==arm]
    setr=[r for r in R if r["set_contains"] is not None]; setcov=sum(r["set_contains"] for r in setr)
    pts=[r for r in R if r["point_issued"]]; pcov=sum(r["point_contains"] for r in pts)
    cata=[r for r in pts if r["catastrophic"]]
    near=[r for r in pts if r["point_contains"] is False and not r["catastrophic"]]
    dropfa=[r for r in pts if r["has_dropout"] and r["point_contains"] is False]
    dfacata=[r for r in pts if r["has_dropout"] and r["catastrophic"]]
    f0=sum(r["false0"] and r["nonzero"] for r in R)
    ut=sum(r["used_truth"] for r in R)
    swl=wilson(setcov,len(setr)); pwl=wilson(pcov,len(pts))
    rep[arm]=dict(set_emit=len(setr),set_cov=setcov,set_rate=setcov/max(1,len(setr)),set_wilson=swl,
        points=len(pts),point_cov=pcov,point_rate=pcov/max(1,len(pts)),point_wilson=pwl,
        catastrophic=len(cata),near_edge=len(near),dropout_false_accept=len(dropfa),dropout_catastrophic=len(dfacata),
        false0=f0,used_truth=ut)
    print(f"\nARM {arm}: set_cov={setcov}/{len(setr)}={setcov/max(1,len(setr)):.4f} Wilson[{swl[0]:.4f},{swl[1]:.4f}]")
    print(f"  points={len(pts)} point_cov={pcov}/{len(pts)}={pcov/max(1,len(pts)):.3f} Wilson[{pwl[0] if pwl[0] else 0:.3f},{pwl[1] if pwl[1] else 0:.3f}]")
    print(f"  CATASTROPHIC={len(cata)} near_edge_invalid={len(near)} dropout_false_accept={len(dropfa)} (catastrophic on dropout={len(dfacata)})")
    print(f"  false_exact_zero={f0}  blind_used_truth={ut}")
    # set coverage by dropout/sparse vs other
    for lab,fn in (("dropsparse",lambda r:r["is_dropsparse"]),):
        d=collections.defaultdict(lambda:[0,0])
        for r in setr: d[fn(r)][1]+=1; d[fn(r)][0]+=r["set_contains"]
        print("  set cov dropsparse vs other:",{("dropsparse" if k else "other"):f"{v[0]}/{v[1]}={v[0]/v[1]:.3f}" for k,v in d.items()})
    # non-vacuity by SNR
    snrp=collections.defaultdict(lambda:[0,0])
    for r in R:
        b="<=5" if r["snr"]<=5 else("5-10" if r["snr"]<=10 else("10-30" if r["snr"]<=30 else ">30"))
        snrp[b][1]+=1; snrp[b][0]+=r["point_issued"]
    print("  point-cert rate by SNR:",{k:f"{v[0]}/{v[1]}={v[0]/v[1]:.3f}" for k,v in sorted(snrp.items())})
# gates
G={}
G["G_false_zero"]=(rep["O"]["false0"]==0 and rep["B"]["false0"]==0)
G["G_set_cov95"]=(rep["O"]["set_wilson"][1]>=0.95 and rep["B"]["set_wilson"][1]>=0.95 and rep["O"]["set_rate"]>=0.93 and rep["B"]["set_rate"]>=0.93)
G["G_zero_catastrophic"]=(rep["O"]["catastrophic"]==0 and rep["B"]["catastrophic"]==0)
G["G_point_cov"]=(rep["B"]["points"]==0 or rep["B"]["point_wilson"][1]>=0.95)
G["G_no_oracle_blind"]=(rep["B"]["used_truth"]==0)
G["G_dropout_no_catastrophic"]=(rep["O"]["dropout_catastrophic"]==0 and rep["B"]["dropout_catastrophic"]==0)
G["G_armO_no_points"]=(rep["O"]["points"]==0)
print("\nPROSPECTIVE GATES:")
for k,v in G.items(): print(f"  {'PASS' if v else '**FAIL**'} {k}")
print("HARD GATES (false-zero + zero-catastrophic):","PASS" if (G["G_false_zero"] and G["G_zero_catastrophic"]) else "FAIL")
json.dump({"report":rep,"gates":G},open("../results/EXP-GT-PC-PROSPECTIVE/prospective_summary.json","w"),
          default=lambda o:(list(o) if isinstance(o,tuple) else (bool(o) if isinstance(o,(bool,np.bool_)) else float(o))))
print("wrote prospective_summary.json")

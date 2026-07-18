"""Aggregate the prospective chunks; compute the dependence-aware coverage/safety/non-vacuity audit."""
import json, glob, collections, math, numpy as np
rows=[]
for f in sorted(glob.glob("../results/EXP-GT-NASI-PROSPECTIVE/rows_*.json")):
    rows += json.load(open(f))
def cp_upper(k,n,alpha=0.05):   # Clopper-Pearson upper 1-sided
    if n==0: return None
    from math import comb
    lo,hi=0.0,1.0
    for _ in range(100):
        mid=(lo+hi)/2
        # P(X<=k) under mid; want = alpha -> upper bound
        p=sum(comb(n,j)*mid**j*(1-mid)**(n-j) for j in range(0,k+1))
        if p>alpha: lo=mid
        else: hi=mid
    return hi
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; den=1+z*z/n; c=p+z*z/(2*n); h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))
    return ((c-h)/den,(c+h)/den)

byarm={a:[r for r in rows if r["arm"]==a] for a in ("O","B")}
print(f"TOTAL rows={len(rows)}  cases={len(rows)//2}")
report={}
for a in ("O","B"):
    R=byarm[a]; emit=[r for r in R if r["emit"]]
    inv=[r for r in emit if r["contains"] is False]
    f0=[r for r in emit if r["exact_zero"] and r["nonzero"]]
    ip=[r for r in emit if r["invalid_point"]]
    cov=sum(1 for r in emit if r["contains"] is True)
    pts=[r for r in emit if r["status"]=="POINT_IDENTIFIED"]
    onesd=[r for r in emit if r["status"] in ("LOWER_BOUND_ONLY","UPPER_BOUND_ONLY","BELOW_DETECTION_LIMIT")]
    abst=[r for r in R if not r["emit"]]
    widths=[r["width"] for r in emit if r["width"] is not None and np.isfinite(r["width"])]
    covrate=cov/max(1,len(emit)); wl=wilson(cov,len(emit))
    report[a]=dict(N=len(R),emit=len(emit),cov=cov,covrate=covrate,cov_wilson=wl,
                   invalid=len(inv),false_zero=len(f0),invalid_points=len(ip),
                   points=len(pts),onesided=len(onesd),abstain=len(abst),
                   median_width=float(np.median(widths)) if widths else None,
                   blind_used_truth=sum(1 for r in R if r.get("used_truth")))
    print(f"\n=== ARM {a} ===")
    print(f"  emitted={len(emit)}/{len(R)}  coverage={covrate:.4f}  Wilson95=[{wl[0]:.4f},{wl[1]:.4f}]")
    print(f"  invalid(any status)={len(inv)}  false_zero_nonzero={len(f0)}  INVALID_POINTS={len(ip)}")
    print(f"  points={len(pts)} onesided={len(onesd)} abstain={len(abst)} median_width={report[a]['median_width']}")
    print(f"  blind_used_truth={report[a]['blind_used_truth']}")
    # coverage by SNR band (safety), low-SNR
    for kf,lab in ((lambda r:r["band"],"band"),):
        d=collections.defaultdict(lambda:[0,0])
        for r in emit:
            d[kf(r)][1]+=1; d[kf(r)][0]+=(r["contains"] is True)
        print(f"  coverage by {lab}:", {k:f"{v[0]}/{v[1]}={v[0]/v[1]:.3f}" for k,v in sorted(d.items())})
    # per-stratum invalid
    ds=collections.defaultdict(lambda:[0,0])
    for r in emit:
        ds[r["stratum"]][1]+=1; ds[r["stratum"]][0]+=(r["contains"] is False)
    worst=sorted(((v[0],v[0]/max(1,v[1]),k,v[1]) for k,v in ds.items()),reverse=True)[:5]
    print("  worst strata (invalid/emit):", [(k,f"{iv}/{n}") for iv,rt,k,n in worst])

# INVALID POINT forensics
print("\n===== INVALID-POINT FORENSICS =====")
ip_all=[r for r in rows if r["invalid_point"]]
print(f"total invalid points across both arms: {len(ip_all)}")
by=collections.Counter((r["arm"],r["band"]) for r in ip_all)
print("by (arm,band):", dict(by))
bystrat=collections.Counter(r["stratum"] for r in ip_all)
print("by stratum:", dict(bystrat))
# how far outside? need set vs qmag - recompute width and miss magnitude approx via qmag & status
print("sample invalid points:")
for r in ip_all[:12]:
    print(f"   arm={r['arm']} band={r['band']} snr={r['snr']} strat={r['stratum']} m={r['m']} |q|={r['qmag']:.3f} status={r['status']}")

json.dump(report, open("../results/EXP-GT-NASI-PROSPECTIVE/prospective_summary.json","w"),
          default=lambda o: (list(o) if isinstance(o,tuple) else float(o)))
print("\nwrote prospective_summary.json")

"""FLRS02 §9 — exact binomial decision capability. No normal approximation anywhere."""
import json, math, datetime
import numpy as np
from scipy.stats import binom, beta
OUT="/home/claude/edl/FLRS02/out"
KEYS=("T_50","T_primary","T_80","T_90")
ATL={pt:json.load(open(f"{OUT}/FLRS02_{pt}_DIRECT_ATLAS.json")) for pt in ("B1","B2")}
ALPHA=0.05; POWER=0.80; NMAX=192

def cp(k,n,conf=0.95):
    a=(1-conf)/2
    lo=0.0 if k==0 else float(beta.ppf(a,k,n-k+1))
    hi=1.0 if k==n else float(beta.ppf(1-a,k+1,n-k))
    return lo,hi

def crit(n,p0,alpha=ALPHA):
    """Smallest c with P(X >= c | p0) <= alpha. Exact."""
    c=int(binom.isf(alpha,n,p0))+1
    while c>0 and binom.sf(c-1,n,p0)<=alpha: c-=1
    while binom.sf(c-1,n,p0)>alpha: c+=1
    return c
def power_at(n,p0,p1):
    return float(binom.sf(crit(n,p0)-1,n,p1))
def n_required(p0,p1,nmax=4000):
    if p1<=p0: return None
    for n in range(5,nmax+1):
        if power_at(n,p0,p1)>=POWER: return n
    return None

# ---- deterministic point-selection rule (FLRS02 §9) ----
def margins(pt,k):
    R=ATL[pt]["ATLAS"]["RATES"]
    m={"functional_maturation":R[f"P_JOINT_FUNCTIONAL_SUCCESS_{k}"]["exact_binomial_95"][0],
       "lineage_survival":R["P_LINEAGE_NON_EXTINCTION"]["exact_binomial_95"][0],
       "third_centre_control":cp(R["P_THIRD_BEFORE_FUNCTION"]["n"]-R["P_THIRD_BEFORE_FUNCTION"]["count"],
                                 R["P_THIRD_BEFORE_FUNCTION"]["n"])[0],
       "X_integrity":R["P_X_INTEGRITY"]["exact_binomial_95"][0]}
    m["MIN_LOWER_MARGIN"]=min(m.values())
    return m
SEL={k:{pt:margins(pt,k) for pt in ("B1","B2")} for k in KEYS}
for k in KEYS:
    a,b=SEL[k]["B1"]["MIN_LOWER_MARGIN"],SEL[k]["B2"]["MIN_LOWER_MARGIN"]
    SEL[k]["WINNER"]="B1" if a>b else ("B2" if b>a else "TIE")
best=SEL["T_primary"]["WINNER"]

# ---- power for a fresh disjoint experiment ----
GRID=[0.05,0.075,0.10,0.125,0.15,0.20,0.25]
POW={}
for pt in ("B1","B2"):
    R=ATL[pt]["ATLAS"]["RATES"]["P_JOINT_FUNCTIONAL_SUCCESS_T_primary"]
    phat=R["point_estimate"]; lo=R["exact_binomial_95"][0]
    rows=[]
    for p0 in GRID:
        nO=n_required(p0,phat); nC=n_required(p0,lo)
        rows.append({"p0_null":p0,
          "planning_p1_observed":phat,"n_required_at_observed":nO,
          "fits_in_192_at_observed":(nO is not None and nO<=NMAX),
          "planning_p1_conservative_lower_95":lo,"n_required_at_conservative":nC,
          "fits_in_192_at_conservative":(nC is not None and nC<=NMAX),
          "power_at_n192_observed":power_at(NMAX,p0,phat),
          "power_at_n192_conservative":power_at(NMAX,p0,lo),
          "critical_count_at_n192":crit(NMAX,p0)})
    POW[pt]={"observed_joint_T_primary":R,"grid":rows,
      "precision_at_n192":{"if_true_p_equals_observed":{"expected_count":phat*NMAX,
        "exact_95_interval":list(cp(int(round(phat*NMAX)),NMAX))}}}

# largest p0 still separable within 192 worlds
def max_sep(pt,key="conservative"):
    R=ATL[pt]["ATLAS"]["RATES"]["P_JOINT_FUNCTIONAL_SUCCESS_T_primary"]
    p1=R["exact_binomial_95"][0] if key=="conservative" else R["point_estimate"]
    best_=None
    for p0 in np.arange(0.01,p1,0.005):
        if power_at(NMAX,float(p0),p1)>=POWER: best_=float(p0)
    return best_
J={"SECTION":"FLRS02 §9 — exact binomial decision capability",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "METHOD":"exact binomial throughout; no normal approximation is used at any step",
 "ALPHA":ALPHA,"TARGET_POWER":POWER,"MAX_PRIMARY_WORLDS":NMAX,
 "NO_INHERITED_0_50_THRESHOLD":"see FLRS02_THRESHOLD_PROVENANCE.json — the decision-capable region is reported instead",
 "POINT_SELECTION_RULE":"maximise the minimum 95% lower confidence margin across functional maturation, lineage survival, third-centre control and X integrity",
 "SELECTION":SEL,"SELECTED_POINT":best,
 "POWER":POW,
 "LARGEST_SEPARABLE_NULL_WITHIN_192":{pt:{"at_observed_p1":max_sep(pt,"observed"),
                                          "at_conservative_p1":max_sep(pt,"conservative")} for pt in ("B1","B2")}}
json.dump(J,open(f"{OUT}/FLRS02_POWER_ANALYSIS.json","w"),indent=2)
for k in KEYS:
    print("%-10s B1 min-margin=%.4f  B2 min-margin=%.4f  winner=%s"%(k,
      SEL[k]["B1"]["MIN_LOWER_MARGIN"],SEL[k]["B2"]["MIN_LOWER_MARGIN"],SEL[k]["WINNER"]))
print("\nSELECTED_POINT (T_primary rule):",best)
for pt in ("B1","B2"):
    print("\n=== %s  observed joint T_primary = %d/%d = %.4f  (95%% lower %.4f) ==="%(pt,
      POW[pt]["observed_joint_T_primary"]["count"],POW[pt]["observed_joint_T_primary"]["n"],
      POW[pt]["observed_joint_T_primary"]["point_estimate"],POW[pt]["observed_joint_T_primary"]["exact_binomial_95"][0]))
    for r in POW[pt]["grid"]:
        print("   p0=%.3f  n_req(obs)=%-5s n_req(cons)=%-5s  fits192: obs=%-5s cons=%-5s  power@192: %.3f / %.3f"%(
          r["p0_null"],r["n_required_at_observed"],r["n_required_at_conservative"],
          r["fits_in_192_at_observed"],r["fits_in_192_at_conservative"],
          r["power_at_n192_observed"],r["power_at_n192_conservative"]))
print("\nlargest separable null within 192:",J["LARGEST_SEPARABLE_NULL_WITHIN_192"])

"""FLRS02 §5+§7+§8 — world-level pointwise atlas, exact binomial intervals, threshold audit."""
import json, math, csv, datetime
import numpy as np
from scipy.stats import beta
OUT="/home/claude/edl/FLRS02/out"
A=json.load(open(f"{OUT}/_checkerA.json"))
KEYS=("T_50","T_primary","T_80","T_90")
BAND=json.load(open(f"{OUT}/FLRS02_FUNCTIONAL_CRITERION.json"))["MANDATORY_SENSITIVITY_BAND"]
REF=json.load(open(f"{OUT}/_A0_reference.json"))["A0_SINGLE_CENTRE_REFERENCE"]
def cp(k,n,conf=0.95):
    if n==0: return [None,None]
    a=(1-conf)/2
    lo=0.0 if k==0 else float(beta.ppf(a,k,n-k+1))
    hi=1.0 if k==n else float(beta.ppf(1-a,k+1,n-k))
    return [lo,hi]
def rate(k,n,name):
    return {"quantity":name,"n":int(n),"count":int(k),
            "point_estimate":(k/n if n else None),"exact_binomial_95":cp(k,n)}
def phase_b(pt):
    W=[r for r in A if r["point"]==pt]; n=len(W)
    S=[r for r in W if r["first_S"]>=0]
    seps=[r["first_S"]-r["first_birth"] for r in S if r["first_birth"]>=0 and r["first_S"]>r["first_birth"]]
    d={"POINT":pt,"kY":W[0]["kY"],"muY":W[0]["muY"],"N_worlds":n,
     "N_with_first_birth":sum(r["n_births"]>=1 for r in W),
     "N_lineage_extinctions":sum(r["extinct"] for r in W),
     "N_reaching_geometric_S":len(S),
     "geometric_separation_time_distribution":{
        "n":len(seps),"min":min(seps) if seps else None,"median":float(np.median(seps)) if seps else None,
        "mean":float(np.mean(seps)) if seps else None,"max":max(seps) if seps else None},
     "N_reaching_P":sum(r["first_P"]>=0 for r in W),
     "P_before_geometric_separation":sum(1 for r in W if r["first_P"]>=0 and r["first_S"]>=0 and r["first_P"]<r["first_S"]),
     "P_after_S_but_before_functional_maturation":{k:sum(1 for r in W if r.get(f"P_before_event_{k}") is True) for k in KEYS},
     "P_only_after_functional_maturation":{k:sum(1 for r in W if r["first_P"]>=0 and r[f"joint_timing_{k}"]) for k in KEYS},
     "X_source_integrity_failures":sum(0 if r["integrity_ok"] else 1 for r in W),
     "S_duration_worlds_reaching_S_sorted":sorted([r["max_S_duration"] for r in S],reverse=True)}
    for k in KEYS: d[f"N_with_S_lasting_ge_{k}"]=sum(r[f"dur_ok_{k}"] for r in W)
    rr={k:[r[f"weak_centre_X_ratio_{k}"] for r in W if r[f"weak_centre_X_ratio_{k}"] is not None] for k in KEYS}
    d["WEAK_CENTRE_X_RATIO"]={k:{"n":len(v),"median":float(np.median(v)) if v else None,
        "mean":float(np.mean(v)) if v else None,"min":min(v) if v else None,"max":max(v) if v else None,
        "required_fraction":{"T_50":0.5,"T_primary":1-1/math.e,"T_80":0.8,"T_90":0.9}[k]} for k,v in rr.items()}
    return d
def atlas(pt):
    W=[r for r in A if r["point"]==pt]; n=len(W)
    out={"POINT":pt,"N_WORLDS":n,"UNIT":"one world; steps and episodes are never independent replicates",
         "INTERVAL":"Clopper-Pearson exact binomial, 95%","RATES":{}}
    R=out["RATES"]
    R["P_FIRST_BIRTH"]=rate(sum(r["n_births"]>=1 for r in W),n,"at least one dynamic Y birth")
    R["P_LINEAGE_NON_EXTINCTION"]=rate(sum(not r["extinct"] for r in W),n,"lineage alive at the recorded horizon")
    R["P_GEOMETRIC_TWO_CENTRES"]=rate(sum(r["first_S"]>=0 for r in W),n,"reaches exactly two spatial centres")
    for k in KEYS:
        R[f"P_FUNCTIONAL_MATURATION_{k}"]=rate(sum(r[f"joint_timing_{k}"] for r in W),n,
            "two centres held >= %.4f steps with no third centre before the event"%BAND[k])
    R["P_THIRD_BEFORE_FUNCTION"]=rate(sum(1 for r in W if r.get("P_before_event_T_primary") is True),n,
        "third centre appears before the primary functional maturation event")
    R["P_X_INTEGRITY"]=rate(sum(r["integrity_ok"] for r in W),n,"no X/source integrity failure")
    for k in KEYS:
        R[f"P_JOINT_FUNCTIONAL_SUCCESS_{k}"]=rate(sum(r[f"joint_{k}"] for r in W),n,
            "all seven conditions including the direct local-X response requirement")
    S=[r for r in W if r["first_S"]>=0]
    out["DIAGNOSTIC_CONDITIONALS"]={
      "P_function_given_reached_S":{k:rate(sum(r[f"joint_{k}"] for r in S),len(S),"conditional") for k in KEYS},
      "WARNING":"conditional rates are diagnostics only; the direct-test decision uses unconditional world probabilities"}
    return out
for pt in ("B1","B2"):
    json.dump({"PHASE_B_DESCRIPTIVE":phase_b(pt),"ATLAS":atlas(pt),"A0_SINGLE_CENTRE_REFERENCE":REF},
              open(f"{OUT}/FLRS02_{pt}_DIRECT_ATLAS.json","w"),indent=2)
json.dump({"POINT":"A0","ROLE":"single-centre control, kY = 0 and muY = 0 so no Y birth is possible",
  "N_WORLDS":40,"N_with_first_birth":0,"N_reaching_S":0,
  "USE":"supplies the single-centre local-X reference level only","REFERENCE":REF},
  open(f"{OUT}/FLRS02_A0_CONTROL.json","w"),indent=2)
cols=["world","point","split","stop","kY","muY","steps","first_birth","n_births","extinct",
      "first_S","first_P","n_S_episodes","max_S_duration","integrity_ok"]
for k in KEYS:
    cols+=[f"dur_ok_{k}",f"noP_ok_{k}",f"resp_ok_{k}",f"event_step_{k}",
           f"weak_centre_X_ratio_{k}",f"weak_centre_X_abs_{k}",f"P_before_event_{k}",
           f"joint_timing_{k}",f"joint_{k}"]
with open(f"{OUT}/FLRS02_PQEC01_WORLD_REANALYSIS.csv","w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=cols,extrasaction="ignore"); w.writeheader()
    for r in A: w.writerow(r)
json.dump(A,open(f"{OUT}/FLRS02_PQEC01_WORLD_REANALYSIS.json","w"),indent=1)
TP={"SECTION":"FLRS02 §8 — provenance audit of the inherited 0.50 probability threshold",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "INHERITED_VALUE":0.50,
 "WHERE_IT_IS_SET":"FLCR01/code/flcr01_science.py:328  THRESH = 0.5",
 "RECORDED_SELF_DESCRIPTION":"INHERITED - it is 1 - ALPHA_SURVIVAL   (FLCR01_LINEAGE_REGIONS.json)",
 "WHAT_ALPHA_SURVIVAL_ACTUALLY_WAS":{
   "definition":"FLCR01/code/flcr01_science.py:16  ALPHA = 0.5, used in C2_FOUNDER as (1-muY)^T_HORIZON >= 0.5",
   "meaning":"a floor on the probability that the ORIGINAL FOUNDER PARTICLE survives the horizon",
   "status_of_that_gate":"the founder-survival gate was REJECTED by FLCR01; FOUNDER_SURVIVAL_GATE = rejected"},
 "CLASSIFICATION":"ARBITRARY_DEVELOPMENTAL_THRESHOLD",
 "REASONING":("0.50 was never frozen as an intended condition-level success-probability claim. It is the "
   "numerical complement of a founder-survival floor belonging to a criterion that FLCR01 itself rejected, "
   "and it was then reused as a developmental success threshold for a different quantity. It therefore "
   "fails the test for PREEXISTING_SCIENTIFIC_THRESHOLD and is not merely CONVENTIONAL_BUT_NOT_DERIVED, "
   "because its stated provenance points at a quantity it does not measure."),
 "CONSEQUENCE":("FLRS02 does not inherit >= 0.50 and does not quietly substitute a new threshold. The future "
   "direct experiment is instead formulated as an exact binomial hypothesis test and the decision-capable "
   "region of candidate probabilities is reported in FLRS02_POWER_ANALYSIS.json."),
 "NO_NEW_THRESHOLD_INVENTED":True}
json.dump(TP,open(f"{OUT}/FLRS02_THRESHOLD_PROVENANCE.json","w"),indent=2)
for pt in ("B1","B2"):
    d=json.load(open(f"{OUT}/FLRS02_{pt}_DIRECT_ATLAS.json"))
    b=d["PHASE_B_DESCRIPTIVE"]
    print("=== %s (kY=%.6e muY=%.6e) ==="%(pt,b["kY"],b["muY"]))
    for k,v in d["ATLAS"]["RATES"].items():
        lo,hi=v["exact_binomial_95"]
        print("  %-38s %2d/%2d = %.4f  [%.4f, %.4f]"%(k,v["count"],v["n"],v["point_estimate"],lo,hi))
    print("   sep median=%s | P_after_S_before_function=%s | P_before_S=%d | ratio(T_primary) median=%.4f"%(
        b["geometric_separation_time_distribution"]["median"],b["P_after_S_but_before_functional_maturation"],
        b["P_before_geometric_separation"],b["WEAK_CENTRE_X_RATIO"]["T_primary"]["median"]))

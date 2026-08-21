"""MRFA01 §10-§11 — exact R2 failure partition over the 22 triggered blocks, and the
separation of population incidence from conditional autonomy."""
from __future__ import annotations
import json, glob, os, csv, statistics
from scipy.stats import beta
REPO="/home/claude/edl"; OUT=f"{REPO}/MRFA01/out"
A=json.load(open(f"{OUT}/_calcA_rows.json")); ROWS=A["rows"]
T=[r for r in ROWS if r["triggered"]]
REP={int(json.load(open(f))["block"]):json.load(open(f)) for f in glob.glob(f"{REPO}/MRFA01/replay/*.json")}

def classify(r):
    """Ordered, mutually exclusive, exhaustive over the 22 triggered blocks.
    Evaluated on the SELECTIVE arm, which is the arm the frozen R2 was scored on."""
    S=r["ARMS"]["SELECTIVE"]
    if S["third_centre_in_window"]:                       return "third_centre"
    if not S["integrity_ok_post"]:                        return "integrity_failure"
    if not S["daughter_exists"]:                          return "daughter_Y_centre_lost"
    if S["criterion_E_post_intervention_births_in_daughter"]==0:
                                                          return "no_post_intervention_X_births"
    if S["criterion_D"]:                                  return "FROZEN_R2_PASS"
    # E passed and D failed: split by whether local mass held or declined
    b=REP[int(r["block"])]["ARMS"]["SELECTIVE"]["_fixed_daughter_mass"]
    return ("local_mass_STABLE_but_frozen_D_fails" if b[249]>=0.9*b[0]
            else "local_mass_DECLINES_while_production_continues")

def main():
    part={}; rows=[]
    for r in sorted(T,key=lambda x:x["block"]):
        c=classify(r); part[c]=part.get(c,0)+1
        S=r["ARMS"]["SELECTIVE"]; H=r["ARMS"]["SHAM"]; G=r["ARMS"]["GLOBAL"]
        rp=REP[int(r["block"])]
        fm=lambda a,i: rp["ARMS"][a]["_fixed_daughter_mass"][i]
        fb=lambda a: sum(rp["ARMS"][a]["_fixed_daughter_births"])
        rows.append({"block":r["block"],"seed":r["seed"],"t_m":r["t_m"],"class":c,
          "R1_EXACT":r["_A_R1"],"fraction_new":round(r["_A_fraction_new"],6),
          "daughter_mass_tm":r["daughter_mass_tm"],"parent_mass_tm":r["parent_mass_tm"],
          "NX_world_at_intervention":r["NX_world_at_intervention"],
          "frozen_D_bound":S["survivor_upper_95"],
          "bound_minus_daughter_mass_tm":S["survivor_upper_95"]-r["daughter_mass_tm"],
          "SEL_D":S["criterion_D"],"SEL_E":S["criterion_E_post_intervention_births_in_daughter"],
          "SEL_daughter_exists":S["daughter_exists"],"SEL_R2":S["R2_PASS"],
          "SHAM_D":H["criterion_D"],"SHAM_daughter_exists":H["daughter_exists"],
          "GLOBAL_daughter_exists":G["daughter_exists"],
          "fixed_mass_start":fm("SELECTIVE",0),
          "SEL_fixed_mass_end":fm("SELECTIVE",249),"SHAM_fixed_mass_end":fm("SHAM",249),
          "GLOBAL_fixed_mass_end":fm("GLOBAL",249),
          "SEL_fixed_births":fb("SELECTIVE"),"SHAM_fixed_births":fb("SHAM"),"GLOBAL_fixed_births":fb("GLOBAL")})
    tot=sum(part.values())
    E_pass_D_fail=[x for x in rows if x["SEL_E"]>0 and not x["SEL_D"]]
    P={"SECTION":"MRFA01 §10 — exact R2 failure partition over the 22 triggered blocks",
      "ORDER":"third_centre -> integrity -> daughter lost -> no births -> D pass -> D fail split by local mass",
      "PARTITION":part,"SUM":tot,"N_TRIGGERED":len(T),"IS_A_PARTITION":tot==len(T),
      "E_PASSED_BUT_FROZEN_R2_FAILED":{
        "count":len(E_pass_D_fail),
        "why":("in every one of these the daughter Y centre survived, produced new X inside its own disc, "
               "held X integrity and saw no third centre. The ONLY frozen criterion they failed is D, "
               "the mass comparison against a bound computed on the whole world's X."),
        "median_bound":statistics.median([x["frozen_D_bound"] for x in E_pass_D_fail]),
        "median_daughter_mass_at_intervention":statistics.median([x["daughter_mass_tm"] for x in E_pass_D_fail]),
        "median_bound_minus_daughter_mass_at_intervention":statistics.median([x["bound_minus_daughter_mass_tm"] for x in E_pass_D_fail]),
        "blocks_where_the_bound_exceeded_the_daughters_ENTIRE_mass_at_intervention":
            sum(1 for x in E_pass_D_fail if x["bound_minus_daughter_mass_tm"]>0),
        "median_new_X_produced_in_the_fixed_daughter_disc":statistics.median([x["SEL_fixed_births"] for x in E_pass_D_fail]),
        "median_GLOBAL_control_births_in_the_same_disc":statistics.median([x["GLOBAL_fixed_births"] for x in E_pass_D_fail])},
      "BLOCKS":rows}
    json.dump(P,open(f"{OUT}/MRFA01_R2_FAILURE_PARTITION.json","w"),indent=1)
    with open(f"{OUT}/MRFA01_R2_FAILURE_PARTITION.csv","w",newline="") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]

    # ---------- §11 population vs conditional ----------
    def ci(k,n,c=0.95):
        a=(1-c)/2
        lo=0.0 if k==0 else beta.ppf(a,k,n-k+1); hi=1.0 if k==n else beta.ppf(1-a,k+1,n-k)
        return [float(lo),float(hi)]
    N=len(ROWS); M=len(T); K=sum(1 for r in T if r["ARMS"]["SELECTIVE"]["R2_PASS"])
    PC={"SECTION":"MRFA01 §11 — population incidence and conditional autonomy kept separate",
      "WHY":("a conditional success rate must never stand in for the population rate. Both must be "
             "visible in any future minimal-reproduction claim, together with their joint."),
      "P_TRIGGER":{"k":M,"n":N,"rate":M/N,"exact_95":ci(M,N),
                   "meaning":"probability that a seeded world forms a trigger-eligible functional daughter"},
      "P_AUTONOMY_GIVEN_TRIGGER_FROZEN_R2":{"k":K,"n":M,"rate":K/M,"exact_95":ci(K,M),
                   "meaning":"FMRT01's frozen conditional endpoint. Unchanged and not re-scored."},
      "P_JOINT_FROZEN_R2":{"k":K,"n":N,"rate":K/N,"exact_95":ci(K,N),
                   "meaning":"population-level minimal reproduction under the FROZEN criterion"},
      "NOTE":"the developmental figures under candidate criteria are in MRFA01_POST_OUTCOME_CRITERION_DIAGNOSTICS.json and are diagnostics, not results"}
    json.dump(PC,open(f"{OUT}/MRFA01_POPULATION_VS_CONDITIONAL_ANALYSIS.json","w"),indent=1)
    print(json.dumps({"PARTITION":part,"SUM":tot,"IS_A_PARTITION":tot==len(T)},indent=1))
    print("\nE passed but frozen R2 failed:",len(E_pass_D_fail))
    print(json.dumps(P["E_PASSED_BUT_FROZEN_R2_FAILED"],indent=1)[:1200])
    print("\nP_TRIGGER %d/%d = %.6f  CI %s"%(M,N,M/N,[round(x,6) for x in ci(M,N)]))
    print("P_AUT|TRIG %d/%d = %.6f  CI %s"%(K,M,K/M,[round(x,6) for x in ci(K,M)]))
    print("P_JOINT   %d/%d = %.6f  CI %s"%(K,N,K/N,[round(x,6) for x in ci(K,N)]))

if __name__=="__main__": main()

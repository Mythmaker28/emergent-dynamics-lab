"""§5 — the ANALYSIS qualified on SYNTHETIC inputs, before any outcome exists.

No archive is read here and no TLMR01 world is touched. The inputs are hand-built per-world
dictionaries with known answers, so the aggregation, the exact intervals, the support rule, the
world-clustered bootstrap, the eligibility clauses and the disposition cascade are all checked
against arithmetic that can be verified by hand. Running this on real archives would put outcomes
in front of the operator before the raw commitment, which the firewall forbids.
"""
from __future__ import annotations
import sys, json, datetime, math
import numpy as np
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_analyse as AN, tlmr01_design as DZ
U=datetime.datetime.now(datetime.timezone.utc).isoformat()

def world(tag,law,expo,forks,eps,mat,cand,trig,integrated,removed=True):
    """a synthetic per-world measurement with exactly the fields aggregate() consumes."""
    return {"tag":tag,"law":law,"seed":0,"steps_executed":11000,"integrity_ok":True,
      "TERMINAL_LABEL":"X","online_t_m":None,
      "M1":{"exposure_by_n":expo,"fork_to_two_or_more_by_n":forks,
            "fork_to_exactly_two_by_n":forks,"transition_table_by_n":{}},
      "M2_episodes":[],
      "M2":{str(n):{"episodes":eps.get(n,0),"matured":mat.get(n,0),
                    "terminators":{"MERGED_TO_ONE_CENTRE":eps.get(n,0)-mat.get(n,0)}}
            for n in set(eps)|set(mat)},
      "M3":{"n_matured":cand,"n_triggered":trig,
            "failure_modes":{"deadline":0,"not_exactly_two_centres":0,
                             "local_x_ratio":cand-trig},
            "first_trigger_step":None,"candidate_steps":[]},
      "M4":{"single_centre_steps":sum(expo.values()),"by_occupancy":expo,
            "steps_above_support_ceiling":sum(v for n,v in expo.items() if int(n)>5),
            "support_ceiling_sI":5,
            "fraction_of_horizon_single_centre":sum(expo.values())/11000.0,
            "max_single_centre_occupancy":max([int(n) for n in expo] or [0])},
      "M5":{"A_maturation_reached":cand>0,"B_trigger_fired":trig>0,
            "C_selective_removal_applied":bool(removed and trig>0),
            "D_post_removal_functional_complete_turnover":bool(integrated),
            "n_post_removal_complete_intervals":int(bool(integrated)),
            "n_post_removal_functional_intervals":int(bool(integrated)),
            "INTEGRATED":bool(integrated),"post_removal_intervals":[]}}

def near(a,b,tol=1e-12): return a is not None and b is not None and abs(a-b)<=tol

def main():
    rng=np.random.default_rng(12345); T=[]
    def rec(name,got,want,ok=None):
        T.append({"case":name,"got":got,"expected":want,
                  "PASS":(ok if ok is not None else got==want)})
    rows=[world("w%02d"%i,"L",{6:10,7:5},{6:1},{2:3},{2:1},2,1,(i<4)) for i in range(12)]
    a=AN.aggregate(rows,rng)
    rec("M4_total_exposure",a["M4_single_centre_exposure"]["single_centre_steps_total"],12*15)
    rec("M4_above_ceiling",a["M4_single_centre_exposure"]["steps_above_support_ceiling"],12*15)
    rec("M1_n6_numerator",a["M1_by_occupancy"]["6"]["k"],12)
    rec("M1_n6_denominator",a["M1_by_occupancy"]["6"]["n"],120)
    rec("M1_n6_rate",a["M1_by_occupancy"]["6"]["rate"],0.1,near(a["M1_by_occupancy"]["6"]["rate"],0.1))
    rec("M1_n7_zero_numerator",a["M1_by_occupancy"]["7"]["k"],0)
    rec("M1_n7_upper_bound_is_finite",
        a["M1_by_occupancy"]["7"]["one_sided_upper_95"] is not None,True)
    rec("M1_n7_lower_bound_is_zero",a["M1_by_occupancy"]["7"]["one_sided_lower_95"],0.0)
    rec("M1_above_ceiling_pools_only_strata_above_sI",
        a["M1_above_support_ceiling"]["strata"],[6,7])
    rec("M1_directly_measured_12_worlds_180_steps",
        a["M1_above_support_ceiling"]["DIRECTLY_MEASURED"],True)
    rec("M1_world_clustered_interval_present",
        a["M1_above_support_ceiling"]["world_clustered_95_CI"][0] is not None,True)
    rec("M2_n2_denominator",a["M2_by_occupancy_at_separation"]["2"]["n"],36)
    rec("M2_n2_numerator",a["M2_by_occupancy_at_separation"]["2"]["k"],12)
    rec("M3_denominator_is_matured_count",a["M3_trigger_given_matured"]["n"],24)
    rec("M3_numerator",a["M3_trigger_given_matured"]["k"],12)
    rec("M5_unit_is_the_world",a["M5_integrated"]["per_world"]["n"],12)
    rec("M5_numerator",a["M5_integrated"]["per_world"]["k"],4)
    rec("M5_chain_C_given_B",a["M5_integrated"]["chain"]["C_removal_given_B"]["n"],12)
    thin=[world("t%d"%i,"L",{9:2},{9:1},{},{},0,0,False) for i in range(3)]
    at=AN.aggregate(thin,rng)
    rec("support_rule_bites_on_3_worlds",at["M1_by_occupancy"]["9"]["DIRECTLY_MEASURED"],False)
    rec("support_rule_names_the_reason",
        at["M1_by_occupancy"]["9"].get("SUPPORT"),"SUPPORT_TOO_THIN__NOT_DIRECTLY_MEASURED")
    many=[world("m%02d"%i,"L",{9:4},{9:1},{},{},0,0,False) for i in range(10)]
    am=AN.aggregate(many,rng)
    rec("support_rule_passes_on_10_worlds_40_steps",
        am["M1_by_occupancy"]["9"]["DIRECTLY_MEASURED"],True)
    F=DZ.FLOOR["value"]
    for law,n,kbind in (("LAW_A_B1",128,4),("LAW_C_MCTT01",256,6)):
        for K,expect in ((kbind-1,False),(kbind,True)):
            rr=[world("e%03d"%i,law,{6:40},{6:4},{2:40},{2:20},20,10,i<K) for i in range(n)]
            agg=AN.aggregate(rr,rng)
            e=AN.eligibility(law,agg,n,0)
            rec("eligibility_%s_K%d"%(law,K),e["ELIGIBLE"],expect)
            if K==kbind:
                rec("eligibility_%s_lower_bound_exceeds_F"%law,e["lower_95"]>F,True)
                rec("eligibility_%s_confirmation_is_affordable"%law,
                    e["confirmation_n_required"] is not None and
                    e["confirmation_n_required"]<=DZ.CONFIRMATION_CEILING,True)
    rr=[world("s%03d"%i,"LAW_A_B1",{6:40},{6:4},{2:40},{2:20},20,10,i<8) for i in range(100)]
    e=AN.eligibility("LAW_A_B1",AN.aggregate(rr,rng),128,0)
    rec("E1_catches_a_short_denominator",e["CLAUSES"]["E1_complete_denominator_no_unreplaced_technical_failure"],False)
    rec("E1_short_denominator_makes_it_ineligible",e["ELIGIBLE"],False)
    e2=AN.eligibility("LAW_A_B1",AN.aggregate(
        [world("f%03d"%i,"LAW_A_B1",{6:40},{6:4},{2:40},{2:20},20,10,i<8) for i in range(128)],rng),128,1)
    rec("E1_catches_a_technical_failure",e2["ELIGIBLE"],False)
    clustered=[world("c%02d"%i,"L",{6:100},{6:(100 if i<6 else 0)},{},{},0,0,False) for i in range(12)]
    ac=AN.aggregate(clustered,rng)
    naive=ac["M1_by_occupancy"]["6"]["exact_95_CI"]
    wc=ac["M1_by_occupancy"]["6"]["world_clustered_95_CI"]
    rec("clustered_interval_is_wider_than_the_naive_one",
        (wc[1]-wc[0])>(naive[1]-naive[0]),True)
    art={"MISSION":"TLMR01","SECTION":"5 — analysis qualification on synthetic inputs",
     "GENERATED_UTC":U,"NO_ARCHIVE_IS_READ":True,"NO_OUTCOME_IS_SEEN":True,
     "WHY_SYNTHETIC":"running the analysis on real archives before the raw commitment would put "
       "outcomes in front of the operator, which the firewall forbids. Synthetic inputs with "
       "hand-checkable answers test the same code.",
     "N_CASES":len(T),"ALL_PASS":all(t["PASS"] for t in T),"CASES":T}
    json.dump(art,open(f"{REPO}/TLMR01/out/TLMR01_ANALYSIS_QUALIFICATION.json","w"),indent=1)
    print("ANALYSIS_QUALIFICATION: %d cases, all pass = %s"%(len(T),art["ALL_PASS"]))
    for t in T:
        if not t["PASS"]: print("  FAIL",t)

if __name__=="__main__": main()

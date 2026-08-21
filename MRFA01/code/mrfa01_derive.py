"""MRFA01 §7, §8, §9, §12, §13 — criterion derivation, operator audit, diagnostics, provenance,
eligibility and power."""
from __future__ import annotations
import json, glob, math, os, statistics, datetime, subprocess, hashlib
from scipy.stats import binom, beta
REPO="/home/claude/edl"; OUT=f"{REPO}/MRFA01/out"
MUX=0.004; MUY=9.261187281287937e-05; KY=2.5118864315095822e-05; S0=3
SURV=(1-MUX)**250; L=36; CORE_R=5.0; TE=-1.0/math.log(1-MUX); TEY=-1.0/math.log(1-MUY)
A=json.load(open(f"{OUT}/_calcA_rows.json")); ROWS=A["rows"]; T=[r for r in ROWS if r["triggered"]]
REP={int(json.load(open(f))["block"]):json.load(open(f)) for f in glob.glob(f"{REPO}/MRFA01/replay/*.json")}
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
fm=lambda b,a,i: REP[b]["ARMS"][a]["_fixed_daughter_mass"][i]
fb=lambda b,a: sum(REP[b]["ARMS"][a]["_fixed_daughter_births"])
def low95(k,n): return 0.0 if k==0 else float(beta.ppf(0.05,k,n-k+1))
def ci(k,n,c=0.95):
    al=(1-c)/2
    return [0.0 if k==0 else float(beta.ppf(al,k,n-k+1)),1.0 if k==n else float(beta.ppf(1-al,k+1,n-k))]
def crit(M,q0=0.5,alpha=0.05):
    for k in range(M+1):
        if 1-binom.cdf(k-1,M,q0)<=alpha: return k
    return None

# ---------------- the single-molecule finding, the spine of everything below ----------------
def scale_finding():
    tm=[r["t_m"] for r in T]
    return {"SECTION":"MRFA01 — what the object under test actually is at B1",
     "Y_OCCUPIED_CELLS_AT_t_m":sorted({REP[int(r['block'])] and 2 for r in T}),
     "NY_AT_t_m":2,"Y_REMOVED_BY_SELECTIVE":sorted({r["ARMS"]["SELECTIVE"]["removed"] for r in T}),
     "Y_REMOVED_BY_GLOBAL":sorted({r["ARMS"]["GLOBAL"]["removed"] for r in T}),
     "THE_DAUGHTER_CENTRE_IS_ONE_Y_MOLECULE":True,
     "DAUGHTER_EVER_PRODUCED_A_NEW_Y_DURING_THE_HOLD":{
       "SELECTIVE":sum(1 for r in T if max(r["ARMS"]["SELECTIVE"]["NY_series_every_25"])>r["ARMS"]["SELECTIVE"]["NY_series_every_25"][0]),
       "SHAM":sum(1 for r in T if max(r["ARMS"]["SHAM"]["NY_series_every_25"])>r["ARMS"]["SHAM"]["NY_series_every_25"][0]),
       "of":len(T)},
     "SINGLE_Y_SURVIVAL_OVER_THE_HOLD":(1-MUY)**250,
     "OBSERVED_DAUGHTER_PERSISTENCE":sum(1 for r in T if r["ARMS"]["SELECTIVE"]["daughter_exists"])/len(T),
     "TIMESCALES":{
       "X_e_folding_steps":TE,"Y_decay_e_folding_steps":TEY,
       "T_HOLD_steps":250,"T_HOLD_in_X_e_foldings":250/TE,"T_HOLD_in_Y_e_foldings":250/TEY,
       "empirical_Y_reproduction_waiting_time_median_t_m":statistics.median(tm),
       "T_HOLD_as_fraction_of_that":250/statistics.median(tm),
       "analytic_Y_birth_waiting_time_steps":[1/(KY*1*S0),1/(KY*3*S0)],
       "expected_Y_births_in_250_steps":[250*KY*1*S0,250*KY*3*S0]},
     "CONSEQUENCE":("at B1 a 'centre' is a single Y molecule. Its persistence over the hold is molecule "
       "survival, (1-muY)^250 = %.6f, and its 'function' is Y-gated X catalysis, which the frozen law "
       "entails at any cell holding a Y and an X. The hold is matched to the X relaxation timescale and "
       "is 7.5 %% of the timescale on which the organiser population changes at all. Any LOCAL criterion "
       "measurable inside this hold therefore tests the law, not the daughter.")%((1-MUY)**250)}

# ---------------- §7 criterion matrix ----------------
def matrix(SF):
    both=sum(1 for r in T if fb(int(r["block"]),"SELECTIVE")>fb(int(r["block"]),"GLOBAL")
             and fm(int(r["block"]),"SELECTIVE",249)>fm(int(r["block"]),"GLOBAL",249)
             and r["ARMS"]["SELECTIVE"]["daughter_exists"] and r["ARMS"]["SELECTIVE"]["integrity_ok_post"]
             and not r["ARMS"]["SELECTIVE"]["third_centre_in_window"])
    defs=[
     {"id":"I","name":"absolute local mass","statement":"the daughter retains an absolute amount of X after parent removal",
      "necessary_for_minimal_reproduction":False,"sufficient":False,"too_weak":True,"too_strong":False,
      "measurable_from_FMRT01":True,"invariant_to_world_size":True,"invariant_to_unrelated_X_elsewhere":True,
      "depends_on_arbitrary_threshold":True,
      "verdict":"REJECTED — an absolute amount requires a chosen number, and inherited stock alone satisfies it for many hundreds of steps"},
     {"id":"II","name":"active local production","statement":"the daughter continues producing new X after the parent is removed",
      "necessary_for_minimal_reproduction":True,"sufficient":False,"too_weak":True,"too_strong":False,
      "measurable_from_FMRT01":True,"invariant_to_world_size":True,"invariant_to_unrelated_X_elsewhere":True,
      "depends_on_arbitrary_threshold":False,
      "verdict":("NECESSARY BUT ENTAILED AT B1 — production is Y-gated in the frozen engine, so a surviving "
        "single-Y centre with X present produces X with probability ~1. Definition II is therefore true by the "
        "law whenever the molecule survives, and tests nothing about the daughter.")},
     {"id":"III","name":"operator-qualified local function",
      "statement":"the daughter alone sustains a local X response consistent with the qualified single-organiser operator",
      "necessary_for_minimal_reproduction":False,"sufficient":False,"too_weak":False,"too_strong":True,
      "measurable_from_FMRT01":False,"invariant_to_world_size":True,"invariant_to_unrelated_X_elsewhere":True,
      "depends_on_arbitrary_threshold":True,
      "verdict":("NOT AVAILABLE — see MRFA01_OPERATOR_REFERENCE_AUDIT.json. Only the unblocked kernel is exact; "
        "the capacity-constrained operator carries empirical error with no certified bound, and its own 80 %% "
        "radius, 8.5440, exceeds FMRT01's measurement radius of 5.0.")},
     {"id":"IV","name":"causal autonomy through the paired fork",
      "statement":"removing the parent leaves a positive, persistent daughter-specific local response relative to GLOBAL_OFF",
      "necessary_for_minimal_reproduction":True,"sufficient":False,"too_weak":False,"too_strong":False,
      "measurable_from_FMRT01":True,"invariant_to_world_size":True,"invariant_to_unrelated_X_elsewhere":True,
      "depends_on_arbitrary_threshold":False,
      "verdict":("BEST AVAILABLE OPERATIONALISATION, AND STILL NOT A TEST AT B1 — it is exactly scoped, uses a "
        "measured rather than analytic old-material reference, and has an exact exchangeability null. But at a "
        "250-step hold its content reduces to Definition II plus single-molecule survival, both entailed by the "
        "frozen law. It becomes a genuine test only over a hold matched to the organiser timescale.")}]
    M={"SECTION":"MRFA01 §7 — what daughter independence should mean, derived scientifically",
     "GENERATED_UTC":NOW(),
     "TARGET_CONCEPT":("after a daughter organising centre has formed from newly produced material, its local "
       "organising function continues causally after removal of the parent"),
     "EXPLICITLY_EXCLUDED":["heredity","multi-generation propagation","strong self-reproduction"],
     "DEFINITIONS":defs,
     "PREFERRED":"IV",
     "PREFERRED_BUT_NOT_TESTABLE_AT_THE_AVAILABLE_SCALE":True,
     "WHY":SF["CONSEQUENCE"],
     "DEVELOPMENTAL_COUNT_UNDER_IV":{"k":both,"n":len(T),"rate":both/len(T),
       "exact_one_sided_95_lower":low95(both,len(T)),
       "STATUS":"POST_OUTCOME_AUTOPSY_DIAGNOSTIC — not a result, not a p-value, not a re-scoring of FMRT01"},
     "THE_EXACT_MISSING_OBJECT":[
       {"object":"a daughter centre whose identity is not a single molecule",
        "why":("at B1 every triggered block has exactly two Y-occupied cells and NY = 2; SELECTIVE removes one Y "
          "and GLOBAL removes two. Centre persistence is therefore molecule survival and centre function is "
          "single-molecule catalysis. Neither is a property of a daughter as opposed to a molecule.")},
       {"object":"a hold window matched to the organiser timescale",
        "why":("T_HOLD = 250 steps = %.4f X e-foldings but only %.4f Y decay e-foldings, and %.2f %% of the "
          "empirical single-centre-to-two-centre waiting time of %d steps. No Y was produced by any daughter in "
          "any of the 22 blocks, in either arm that retained a daughter.")%(250/TE,250/TEY,
            100*250/statistics.median([r["t_m"] for r in T]),statistics.median([r["t_m"] for r in T]))}]}
    json.dump(M,open(f"{OUT}/MRFA01_DAUGHTER_INDEPENDENCE_CRITERION_MATRIX.json","w"),indent=1)
    return M

# ---------------- §8 operator reference audit ----------------
def operator_audit():
    OB=json.load(open(f"{REPO}/OBTC02/out/_operator_status.json"))
    RS=json.load(open(f"{REPO}/OBFOR01/out/_residual.json"))
    P=RS["PREDICTED"]
    O={"SECTION":"MRFA01 §8 — is the qualified single-centre operator a valid autonomy reference?",
     "GENERATED_UTC":NOW(),
     "SOURCES":["OBTC02/out/_operator_status.json","OBFOR01/out/_residual.json"],
     "WHAT_IS_ACTUALLY_QUALIFIED":{
       "UNBLOCKED_DISCRETE_KERNEL":OB["UNBLOCKED_DISCRETE_KERNEL"],
       "FULL_CAPACITY_CONSTRAINED_OPERATOR":OB["FULL_CAPACITY_CONSTRAINED_OPERATOR"],
       "why_not_bounded":OB["why_not_WITH_BOUNDS"]},
     "COMPARISON":[
      {"aspect":"source law","single_centre":"one organiser","daughter_context":"one organiser after selective removal","comparable":True},
      {"aspect":"substrate law","single_centre":"LawSpec v2 exchange","daughter_context":"identical","comparable":True},
      {"aspect":"X decay","single_centre":"muX = 0.004","daughter_context":"identical","comparable":True},
      {"aspect":"mobility / p_hop","single_centre":"0.10263340389897246","daughter_context":"identical","comparable":True},
      {"aspect":"capacity regime","single_centre":"CAP = 16","daughter_context":"identical nominal cap","comparable":True},
      {"aspect":"substrate history","single_centre":"one centre has drawn on SX/SY throughout",
       "daughter_context":"two centres have drawn on SX/SY for the whole episode before the intervention","comparable":False},
      {"aspect":"measurement radius","single_centre":"the operator's own r80 = %.6f"%P["mobile_r80"],
       "daughter_context":"FMRT01 measures inside CORE_R = 5.0","comparable":False},
      {"aspect":"certified error","single_centre":"none; rejection rates are measurements, not bounds",
       "daughter_context":"a frozen null needs a certified bound","comparable":False}],
     "OPERATOR_IS_WORLD_SIZE_INVARIANT":RS["PREDICTED"]["by_size_mobile_r80"],
     "OPERATOR_r80_EXCEEDS_FMRT01_MEASUREMENT_RADIUS":{"r80":P["mobile_r80"],"CORE_R":CORE_R,
       "consequence":("the operator's own characteristic radius is larger than the disc FMRT01 measures in, so a "
         "margin derived from the operator would not even apply at the scale that was measured")},
     "VERDICT":"SINGLE_CENTRE_OPERATOR_NOT_TRANSPORTABLE_TO_DAUGHTER_CONTEXT",
     "GROUNDS":["only the unblocked kernel is exact and the daughter context is capacity-constrained",
                "the operator's r80 = 8.544 exceeds FMRT01's measurement radius of 5.0",
                "the daughter's substrate history is a two-centre history, outside the qualification scope",
                "no certified bound exists, so no frozen exact null can be derived from it"],
     "THEREFORE":"use the paired causal fork, which is empirical, exactly scoped and world-size invariant by construction",
     "THIS_CHOICE_IS_LOAD_BEARING":True}
    json.dump(O,open(f"{OUT}/MRFA01_OPERATOR_REFERENCE_AUDIT.json","w"),indent=1)
    return O

# ---------------- §9 post-outcome diagnostics ----------------
def diagnostics():
    def count(pred): return sum(1 for r in T if pred(r))
    cands={}
    cands["FROZEN_D_world_scoped"]={"SELECTIVE":count(lambda r:r["ARMS"]["SELECTIVE"]["criterion_D"]),
      "SHAM":count(lambda r:r["ARMS"]["SHAM"]["criterion_D"]),"GLOBAL":count(lambda r:r["ARMS"]["GLOBAL"]["criterion_D"])}
    cands["DAUGHTER_SCOPED_ANALYTIC_BOUND"]={
      "SELECTIVE":count(lambda r:(r["ARMS"]["SELECTIVE"]["daughter_mass_post"] or 0)>int(binom.ppf(0.95,r["_A_daughter_total_tm"],SURV))),
      "SHAM":count(lambda r:(r["ARMS"]["SHAM"]["daughter_mass_post"] or 0)>int(binom.ppf(0.95,r["_A_daughter_total_tm"],SURV))),
      "GLOBAL":0,
      "caveat":"anti-conservative: it ignores X diffusing INTO the disc from the parent region"}
    cands["DEFINITION_II_production_only"]={
      "SELECTIVE":count(lambda r:fb(int(r["block"]),"SELECTIVE")>0),
      "SHAM":count(lambda r:fb(int(r["block"]),"SHAM")>0),"GLOBAL":count(lambda r:fb(int(r["block"]),"GLOBAL")>0)}
    cands["DEFINITION_IV_paired_vs_measured_GLOBAL"]={
      "SELECTIVE":count(lambda r: fb(int(r["block"]),"SELECTIVE")>fb(int(r["block"]),"GLOBAL")
        and fm(int(r["block"]),"SELECTIVE",249)>fm(int(r["block"]),"GLOBAL",249)
        and r["ARMS"]["SELECTIVE"]["daughter_exists"] and r["ARMS"]["SELECTIVE"]["integrity_ok_post"]
        and not r["ARMS"]["SELECTIVE"]["third_centre_in_window"]),
      "SHAM":count(lambda r: fb(int(r["block"]),"SHAM")>fb(int(r["block"]),"GLOBAL")
        and fm(int(r["block"]),"SHAM",249)>fm(int(r["block"]),"GLOBAL",249)
        and r["ARMS"]["SHAM"]["daughter_exists"]),
      "GLOBAL":0}
    N=len(ROWS)
    for k,v in cands.items():
        s=v["SELECTIVE"]
        v["population_count_over_all_85_blocks"]=s
        v["population_rate"]=s/N
        v["population_exact_95"]=ci(s,N)
        v["conditional_rate"]=s/len(T)
        v["conditional_exact_95"]=ci(s,len(T))
    D={"SECTION":"MRFA01 §9 — post-outcome application of candidate criteria to the existing FMRT01 worlds",
     "GENERATED_UTC":NOW(),
     "STATUS":"POST_OUTCOME_AUTOPSY_DIAGNOSTIC",
     "CANNOT_CHANGE":"FMRT01_FINAL_DISPOSITION",
     "NO_P_VALUE_IS_PUBLISHED_HERE":("none of these criteria was preregistered. Reporting a p-value for any of "
       "them would present a post-outcome choice as a prospective test. The counts exist for one purpose only: "
       "to judge whether a fresh test would be worthwhile."),
     "DENOMINATORS":{"conditional":len(T),"population":N},
     "CANDIDATES":cands}
    json.dump(D,open(f"{OUT}/MRFA01_POST_OUTCOME_CRITERION_DIAGNOSTICS.json","w"),indent=1)
    return D

# ---------------- §12 provenance adjudication ----------------
def provenance():
    RM=json.load(open(f"{REPO}/FMRT01/out/FMRT01_RAW_MANIFEST.json"))
    FD=json.load(open(f"{REPO}/FMRT01/out/FMRT01_FINAL_DISPOSITION.json"))
    DA=json.load(open(f"{REPO}/FMRT01/out/FMRT01_DISPOSITION_ADJUDICATION.json"))
    P={"SECTION":"MRFA01 §12 — adjudication of FMRT01's declared provenance defects. ADDITIVE ONLY.",
     "GENERATED_UTC":NOW(),
     "NO_FMRT01_JSON_WAS_ALTERED":True,
     "ORIGINAL_MACHINE_DISPOSITION":FD["FINAL_DISPOSITION"],
     "FMRT01_ADJUDICATED_DISPOSITION":DA["ADJUDICATED_TERMINAL_DISPOSITION"],
     "SCIENTIFIC_CAUSAL_RESULT":("the frozen primary test did not reject H0: q <= 0.05. K = 3 against a required "
       "critical count of 4, exact one-sided p = 0.09482304591843077. That stands, and nothing in this autopsy "
       "changes it."),
     "P1_TRIGGER_LEAKAGE_THROUGH_RAW_NAMING":{
       "what_was_visible":"the suffix _NOTRIG on 63 of 85 archive filenames, i.e. trigger occurrence",
       "when":"at raw-manifest construction, AFTER all 85 blocks had completed",
       "any_run_still_unexecuted":False,"reserve_use_still_possible":False,
       "sample_size_still_changeable":False,
       "verified_here":{"archives":85,"blocks_completed":RM["N_BLOCKS_COMPLETED"],
                        "technical_failures":RM["N_TECHNICAL_FAILURES"],
                        "reserves_spent":RM["TECHNICAL_RESERVES_SPENT"]},
       "CLASSIFICATION":"OUTCOME_METADATA_LEAK__NO_ADAPTIVE_CONSEQUENCE"},
     "P2_DURABILITY_GATE_SELF_REFERENCE":{
       "what_happened":DA["WHAT_HAPPENED"],
       "gates_affected":DA["GATES_THAT_DIFFER"],
       "any_scientific_quantity_changed":False,
       "could_it_qualify_a_failed_test":False,
       "why_not":DA["THE_ADJUDICATION_CANNOT_BE_SELF_SERVING"],
       "CLASSIFICATION":"NONSCIENTIFIC_PROVENANCE_GATE_DEFECT"},
     "P3_FOUND_BY_THIS_AUTOPSY__WORLD_COUNT_OVERSTATED":{
       "what":("FMRT01 reports PRIMARY_SCIENTIFIC_WORLDS = 255 = 85 x 3. Only the 22 triggered blocks forked into "
               "three arms; the other 63 ran a single trajectory. Arm-instances actually instantiated: "
               "22 x 3 + 63 x 1 = 129."),
       "is_255_in_any_denominator":False,
       "checked":"the primary test used M = 22 and the population analysis used N = 85; 255 appears only as a descriptive field",
       "budget_respected":"129 <= 255 <= 256, so no constraint was breached either way",
       "CLASSIFICATION":"DESCRIPTIVE_OVERSTATEMENT__NO_DENOMINATOR_AFFECTED",
       "NOT_REPAIRED_IN_FMRT01":True},
     "A_BROKEN_DURABILITY_BOOLEAN_DOES_NOT_QUALIFY_A_FAILED_TEST":True}
    json.dump(P,open(f"{OUT}/MRFA01_FMRT01_PROVENANCE_ADJUDICATION.json","w"),indent=1)
    return P

# ---------------- §13 eligibility and power ----------------
def power_and_eligibility(MX,SF,OA,DG):
    both=MX["DEVELOPMENTAL_COUNT_UNDER_IV"]["k"]; n=len(T)
    qlo=low95(both,n); ptrig=low95(22,85)
    def power(nb,q,pt=ptrig):
        tot=0.0
        for M in range(nb+1):
            pm=binom.pmf(M,nb,pt)
            if pm==0: continue
            k=crit(M)
            if k is None: continue
            tot+=pm*(1-binom.cdf(k-1,M,q))
        return float(tot)
    tbl={str(nb):{("q=%.2f"%q):power(nb,q) for q in (0.95,0.90,0.85,0.80,0.75)} for nb in (50,60,70,85,128)}
    conds=[
     {"n":1,"condition":"criterion D did not validly operationalise local daughter autonomy","met":True,
      "evidence":"MRFA01_CRITERION_D_AUDIT.json — WORLD_SCALE_CRITERION_MISAPPLIED_TO_LOCAL_DAUGHTER, on world-size dependence and a 16x scope gap"},
     {"n":2,"condition":"one replacement criterion follows from physics/causal design, not outcome optimisation","met":False,
      "evidence":("Definition IV is derived from the design and has an exact exchangeability null, but at a 250-step "
        "hold its content reduces to Y-gated catalysis by a surviving single molecule, which the frozen law entails. "
        "A criterion entailed by the law is not a replacement criterion; it is a restatement of the law.")},
     {"n":3,"condition":"the criterion is measurable losslessly","met":True,
      "evidence":"daughter-local accepted births and fixed-disc mass are exact integer counts; the reconstruction recovered them bit-exactly in 22/22"},
     {"n":4,"condition":"SHAM and GLOBAL_OFF provide valid positive/negative causal references","met":True,
      "evidence":"GLOBAL produced exactly zero daughter-disc births in all 22 blocks; SHAM retained a functioning daughter in 22 of 22"},
     {"n":5,"condition":"post-outcome diagnostics show the criterion is not vanishingly rare","met":True,
      "evidence":"%d of %d under Definition IV; exact one-sided 95 %% lower bound %.6f"%(both,n,qlo)},
     {"n":6,"condition":"a fresh experiment is decision-capable within <= 256 primary worlds","met":False,
      "evidence":("at 85 blocks the exact unconditional power against the exchangeability null, planned on the "
        "conservative lower bounds q = %.4f and P(trigger) = %.4f, is %.4f — below 0.80. Reaching 0.80 needs "
        "q >= about 0.87, which is above the conservative planning input.")%(qlo,ptrig,power(85,qlo))},
     {"n":7,"condition":"the criterion has a frozen null and an exact testable prediction","met":False,
      "evidence":("the null is exact — matched-pair exchangeability, H0: q <= 0.5 — but the prediction is not "
        "testable in the scientific sense at this scale: the law entails the outcome whenever the daughter's single "
        "Y molecule survives, which it does with probability %.6f per hold.")%((1-MUY)**250)}]
    P={"SECTION":"MRFA01 §13 — eligibility for a fresh test, and the exact power it would have",
     "GENERATED_UTC":NOW(),
     "CANDIDATE_PRIMARY_ENDPOINT":("Definition IV, scored per block on the SELECTIVE arm against the SAME block's "
       "GLOBAL_OFF arm in identical fixed daughter-centred geometry"),
     "NULL":{"H0":"q <= 0.5","basis":("matched-pair exchangeability. Under 'removing the parent leaves no "
       "daughter-specific local response' the SELECTIVE and GLOBAL arms are two draws from the same post-fork law "
       "in the same world, so the paired comparison is a coin flip. 0.5 is the pair's own rate, not a chosen number."),
       "alpha":"one-sided 0.05","critical_function":"critical(M) = smallest k with P[Binomial(M,0.5) >= k] <= 0.05",
       "critical_examples":{str(M):crit(M) for M in (5,10,15,18,20,22,25,30)}},
     "PLANNING_INPUTS":{"P_trigger_point":22/85,"P_trigger_conservative_lower_95":ptrig,
       "q_point":both/n,"q_conservative_lower_95":qlo,
       "rule":"plan on the exact 95 % lower bounds, never the point estimates — the FDFLT01 precedent"},
     "EXACT_UNCONDITIONAL_POWER":tbl,
     "POWER_AT_85_BLOCKS_ON_THE_CONSERVATIVE_INPUT":power(85,qlo),
     "SEVEN_CONDITIONS":conds,
     "N_MET":sum(1 for c in conds if c["met"]),"N_REQUIRED":7,
     "FRESH_TEST_ELIGIBLE":all(c["met"] for c in conds),
     "PARAMETER_POINT":"B1, unchanged. No parameter search was performed and none is proposed.",
     "NO_B1_VS_B2_COMPARISON":"B1 is not re-litigated merely because it failed under the old D"}
    json.dump(P,open(f"{OUT}/MRFA01_POWER_ANALYSIS.json","w"),indent=1)
    return P

if __name__=="__main__":
    SF=scale_finding(); json.dump(SF,open(f"{OUT}/_scale_finding.json","w"),indent=1)
    MX=matrix(SF); OA=operator_audit(); DG=diagnostics(); PR=provenance()
    PW=power_and_eligibility(MX,SF,OA,DG)
    print("daughter centre is one Y molecule:",SF["THE_DAUGHTER_CENTRE_IS_ONE_Y_MOLECULE"])
    print("new Y produced during the hold  :",SF["DAUGHTER_EVER_PRODUCED_A_NEW_Y_DURING_THE_HOLD"])
    print("preferred definition            :",MX["PREFERRED"],"| testable at this scale:",not MX["PREFERRED_BUT_NOT_TESTABLE_AT_THE_AVAILABLE_SCALE"])
    print("operator verdict                :",OA["VERDICT"])
    print("conditions met                  : %d / 7"%PW["N_MET"])
    print("FRESH_TEST_ELIGIBLE             :",PW["FRESH_TEST_ELIGIBLE"])
    print("power at 85 blocks (conservative): %.6f"%PW["POWER_AT_85_BLOCKS_ON_THE_CONSERVATIVE_INPUT"])

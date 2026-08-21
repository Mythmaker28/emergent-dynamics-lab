"""DOTC01 §2-§5 — the old object stated, and the new organiser-level object defined.

These are DEFINITIONS. They contain no measurement and are written before any developmental
distribution is inspected, exactly as §8 requires.
"""
from __future__ import annotations
import json, os, math, datetime
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/DOTC01/out"; FRAW=f"{REPO}/FMRT01/raw"
NOW=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
FZ=json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
C=FZ["INHERITED_FROZEN_CONSTANTS"]; B1=FZ["PHASE_B"]["POINT_B1"]
MUY=B1["muY"]; KY=B1["kY"]; CORE_R=C["CORE_R"]; L=C["L"]; MUX=C["muX"]

# ------------------------------------------------------------------ §2
def old_object():
    """Verified from raw FMRT01 bytes, independently of MRFA01's modules."""
    files=sorted(f for f in os.listdir(FRAW) if f.endswith(".npz"))
    trig=[]; ncells=[]; grew=[]; surv=[]
    for f in files:
        z=np.load(os.path.join(FRAW,f),allow_pickle=True)
        m=json.loads(str(z["meta"][0]))
        if not m.get("triggered"): continue
        trig.append(m)
        ncells.append(int(z["cells_tm"].shape[0]))
        S=m["ARMS"]["SELECTIVE"]; H=m["ARMS"]["SHAM"]
        grew.append(max(S["NY_series_every_25"])>S["NY_series_every_25"][0]
                    or max(H["NY_series_every_25"])>H["NY_series_every_25"][0])
        surv.append(S["final_NY"]>=1)
    return {"SECTION":"DOTC01 §2 — the old daughter object, recomputed from raw FMRT01 bytes",
      "GENERATED_UTC":NOW(),
      "TRIGGERED_BLOCKS":len(trig),
      "Y_OCCUPIED_CELLS_AT_MATURATION_PER_WORLD":sorted(set(ncells)),
      "CELLS_PER_CENTRE_AT_MATURATION":1,
      "EVERY_WORLD_HAS_EXACTLY_TWO_Y_CELLS":set(ncells)=={2},
      "Y_REMOVED_BY_SELECTIVE":sorted({m["ARMS"]["SELECTIVE"]["removed"] for m in trig}),
      "Y_REMOVED_BY_GLOBAL":sorted({m["ARMS"]["GLOBAL"]["removed"] for m in trig}),
      "N_Y_AT_MATURATION":2,
      "NEW_Y_BIRTHS_BY_THE_DAUGHTER_IN_THE_CAUSAL_WINDOW":{
        "worlds_where_any_arm_grew_its_Y_count_above_its_start":sum(grew),
        "of":len(trig),
        "caveat":("FMRT01 stored N_Y only every 25 steps, so a birth and a death inside one 25-step "
                  "gap would be invisible. This is why the organiser question is answered from PQEC01's "
                  "exact event ledgers and not from FMRT01's sampled series.")},
      "DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW":{
        "analytic_single_Y":(1-MUY)**250,
        "observed_final_NY_ge_1":sum(surv),"of":len(trig),
        "observed_rate":sum(surv)/len(trig)},
      "OLD_DAUGHTER_OBJECT":"SINGLE_Y_PARTICLE_WITH_LOCAL_X_FUNCTION",
      "VERDICT":"VALID_LOCAL_SOURCE__INSUFFICIENT_ORGANISER_LEVEL_IDENTITY",
      "WHY_NOT_INVALID":("the old object is a real, causally efficacious local X source: FMRT01's GLOBAL_OFF "
        "arm produced exactly zero X births in the daughter disc while the SELECTIVE arm produced a median "
        "of 110. What it does not carry is an identity that could survive replacement of its material, "
        "because it has only one constituent.")}

# ------------------------------------------------------------------ §3
def organiser_object():
    return {"SECTION":"DOTC01 §3 — the organiser-level daughter object, defined without particle genealogy",
     "GENERATED_UTC":NOW(),
     "NO_GENEALOGY":("no parent-child assignment between Y molecules is invented, asserted or required. "
       "The engine keeps no Y tracker and DOTC01 does not create one."),
     "CENTRE":{"definition":"a time-indexed connected component of Y-occupied cells under the frozen centre rule",
       "frozen_rule":"toroidal single-linkage over Y-occupied cells with adjacency distance <= CORE_R",
       "CORE_R":CORE_R,"source":"FMRT01/code/fmrt01_identity.py components(), unchanged"},
     "CENTRE_IDENTITY_ACROSS_STEPS":{
       "method":"persistent spatial matching between consecutive steps",
       "rule":("a component at step t+1 continues a component at step t when it is the unique nearest "
         "component by toroidal centroid distance in both directions and that distance does not exceed "
         "CORE_R. A step at which the match is not mutually unique ENDS the identity interval; it is never "
         "resolved by preference."),
       "why_mutual_and_unique":"so that a fission or a merger terminates an identity interval instead of being absorbed into it"},
     "ORGANISER_LEVEL_CONTINUITY":{
       "an interval [t0,t1] on one continuously matched component C qualifies only if ALL SIX hold":[
        "1. C remains spatially coherent under the frozen centre rule at every step in [t0,t1]",
        "2. N_Y_C(t) >= 1 at every step in [t0,t1] — the component never becomes empty",
        "3. at least one constituent-Y REMOVAL event is recorded inside C during [t0,t1]",
        "4. at least one accepted constituent-Y BIRTH is recorded inside C during [t0,t1]",
        "5. centre identity survives those material changes under the persistent spatial matching above",
        "6. the local X organising function remains active across the turnover (see §5)"],
       "NAME":"FUNCTIONAL_CONTINUITY_ACROSS_CONSTITUENT_TURNOVER"},
     "WHY_N_Y_GE_2_IS_NOT_THE_CRITERION":("a static two-particle centre has more material but has demonstrated "
       "no organisational persistence through turnover; a single Y that survives a long time has demonstrated "
       "no material replacement. The criterion is the EVENT PAIR inside one continuous identity interval, not a count."),
     "REMOVAL_IS_DEFINED_AS":{
       "primary":"a Y decay event recorded inside C (the ydeath ledger)",
       "why_not_emigration":("for a one-cell component the component travels with its own Y, so a hop can never "
         "remove that Y from its own component. Once a component has two or more constituents, a constituent "
         "moving beyond CORE_R produces a SECOND component: that is centre fission, i.e. centre creation, which "
         "§9 requires be kept distinct from turnover. Emigration is therefore counted separately and never as turnover."),
       "recorded_separately":"YES"},
     "BIRTH_IS_ALWAYS_INSIDE_C":("a structural consequence of the frozen law, not an assumption: the Y birth "
       "branch of _react_core draws births with probability min(1, kY*nX*nY), which is zero at any cell with "
       "nY = 0. Every Y birth is therefore co-located with an existing constituent and is inside that "
       "constituent's component by construction.")}

# ------------------------------------------------------------------ §4
def turnover_event():
    return {"SECTION":"DOTC01 §4 — the constituent-turnover event, defined exactly",
     "GENERATED_UTC":NOW(),
     "PER_CENTRE_SERIES":{"Y_BIRTH_C(t)":"sum of ybirth n_born over cells belonging to C at step t",
       "Y_DEATH_C(t)":"sum of ydeath n_died over cells belonging to C at step t",
       "N_Y_C(t)":"sum of nY over cells belonging to C at step t",
       "membership":"cell membership is taken from the frozen centre rule applied to the ycells listing at step t"},
     "COMPLETE_TURNOVER":{"requires":[
        "the component remains nonempty throughout the identity interval",
        "at least one Y removal recorded inside C",
        "at least one accepted Y birth recorded inside C",
        "both events lie inside ONE continuous centre-identity interval"],
       "orderings_analysed":{
        "BIRTH_THEN_DEATH":{"admissible":True,
          "note":"the centre first grows to at least two constituents and then loses one, so it is never empty"},
        "DEATH_THEN_BIRTH":{"admissible":"ONLY IF N_Y_C >= 2 BEFORE THE DEATH",
          "proved_impossible_for_a_one_constituent_centre":True,
          "proof":("if N_Y_C = 1 and that constituent decays then N_Y_C = 0 and condition 2 fails at that step, "
            "ending the identity interval. A centre that begins the interval with one constituent can therefore "
            "reach COMPLETE_TURNOVER only through BIRTH_THEN_DEATH. This is a theorem about the frozen law and "
            "the definition, not an empirical claim.")}},
       "consequence_for_the_B1_daughter":("every FMRT01 daughter begins with exactly one constituent, so at B1 "
         "the ONLY route to complete turnover is a local Y birth followed by a local Y removal.")},
     "PARTIAL_TURNOVER":"an identity interval containing a birth inside C or a removal inside C, but not both",
     "NO_TURNOVER":"an identity interval containing neither",
     "GENEALOGY_REQUIRED":False}

# ------------------------------------------------------------------ §5
def functional_continuity():
    return {"SECTION":"DOTC01 §5 — functional continuity across turnover",
     "GENERATED_UTC":NOW(),
     "PRIMARY_OBSERVABLE":"accepted new X births inside the daughter-centred local functional domain",
     "WHY":("inherited X cannot create a birth event. FMRT01's causal lesson, established with a matched "
       "no-source arm, is that local production is diagnostic where absolute local stock is not: the GLOBAL_OFF "
       "arm produced exactly zero X births inside the daughter disc in 22 of 22 blocks."),
     "ALSO_RECORDED_BUT_NOT_ADJUDICATIVE":["daughter-local X mass","local radial X response","local nSY and the candidate pool"],
     "WORLD_TOTAL_X_MAY_NOT_ENTER":("MRFA01 classified FMRT01's criterion D as "
       "WORLD_SCALE_CRITERION_MISAPPLIED_TO_LOCAL_DAUGHTER because its reference scaled with the whole lattice. "
       "No world-total quantity enters this criterion."),
     "TURNOVER_GAP":{"definition":"an interval in which local production falls below an operator-derived floor for "
       "longer than a physically derived tolerance",
       "floor_transportable":False,
       "why_not":("MRFA01 §8 established SINGLE_CENTRE_OPERATOR_NOT_TRANSPORTABLE_TO_DAUGHTER_CONTEXT: only the "
         "unblocked kernel is exact, the capacity-constrained operator carries empirical error with no certified "
         "bound, and its own r80 = 8.544 exceeds the CORE_R = 5.0 measurement radius. No qualified local floor "
         "can therefore be derived, and none is invented."),
       "consequence":"no floor is defined and no gap test is used"},
     "FUNCTIONAL_CONTINUITY_MEASURE":"ACTIVE_LOCAL_X_PRODUCTION",
     "NO_ARBITRARY_ABSOLUTE_MASS_THRESHOLD":True,
     "OPERATIONAL_FORM":("across the identity interval containing the turnover event pair, the centre records at "
       "least one accepted X birth inside its local domain on both sides of the removal event. Zero is the only "
       "threshold used, and zero is not a choice: it is the value the matched no-source control takes.")}

if __name__=="__main__":
    os.makedirs(OUT,exist_ok=True)
    o=old_object(); json.dump(o,open(f"{OUT}/DOTC01_OLD_OBJECT_VERIFICATION.json","w"),indent=1)
    g=organiser_object(); json.dump(g,open(f"{OUT}/DOTC01_ORGANISER_OBJECT_DEFINITION.json","w"),indent=1)
    t=turnover_event(); json.dump(t,open(f"{OUT}/DOTC01_TURNOVER_EVENT_DEFINITION.json","w"),indent=1)
    f=functional_continuity(); json.dump(f,open(f"{OUT}/DOTC01_FUNCTIONAL_CONTINUITY_DEFINITION.json","w"),indent=1)
    print("triggered blocks:",o["TRIGGERED_BLOCKS"])
    print("every world exactly 2 Y cells:",o["EVERY_WORLD_HAS_EXACTLY_TWO_Y_CELLS"],o["Y_OCCUPIED_CELLS_AT_MATURATION_PER_WORLD"])
    print("Y removed SELECTIVE/GLOBAL:",o["Y_REMOVED_BY_SELECTIVE"],o["Y_REMOVED_BY_GLOBAL"])
    print("daughter Y survival analytic %.6f | observed %d/%d"%(
        o["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["analytic_single_Y"],
        o["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["observed_final_NY_ge_1"],
        o["DAUGHTER_Y_SURVIVAL_THROUGH_THE_OLD_250_STEP_WINDOW"]["of"]))
    print("OLD_DAUGHTER_OBJECT:",o["OLD_DAUGHTER_OBJECT"],"->",o["VERDICT"])
    print("DEATH_THEN_BIRTH impossible for a one-constituent centre:",
          t["COMPLETE_TURNOVER"]["orderings_analysed"]["DEATH_THEN_BIRTH"]["proved_impossible_for_a_one_constituent_centre"])

"""FIMRCC01 Section 2 — apply the pre-registered Precondition A rule to the 256 LAW_C results.

The verdict logic is a transcription of FIMRCC01_PRECONDITION_A_RULE.json, whose sha256 was
published before any of these numbers existed. Nothing below chooses a threshold.
"""
from __future__ import annotations
import json, glob, hashlib, datetime, os, math
REPO="/home/claude/edl"; OUT=f"{REPO}/FIMRCC01/out"
U=datetime.datetime.now(datetime.timezone.utc).isoformat()
RULE_PATH=f"{OUT}/FIMRCC01_PRECONDITION_A_RULE.json"
RULE_SHA=hashlib.sha256(open(RULE_PATH,"rb").read()).hexdigest()

rows=[json.load(open(p)) for p in sorted(glob.glob(f"{REPO}/FIMRCC01/work/pa_out/*.json"))]
assert len(rows)==256, len(rows)
assert all(r["law"]=="LAW_C_MCTT01" for r in rows)

N_WORLDS=len(rows)
triggered=[r for r in rows if r["n_triggered"]>0]
carried  =[r for r in triggered if r["identity_carried_to_maturation"]]
removed  =[r for r in rows if r["removal_applied"]]
labels={}
for r in rows: labels[r["TERMINAL_LABEL"]]=labels.get(r["TERMINAL_LABEL"],0)+1

# ---- Clopper-Pearson, as frozen in TLMR01 ----
def _betainv_lo(k,n,a):
    if k==0: return 0.0
    lo,hi=0.0,1.0
    for _ in range(200):
        mid=(lo+hi)/2
        s=sum(math.comb(n,i)*mid**i*(1-mid)**(n-i) for i in range(k,n+1))
        if s>a: hi=mid
        else: lo=mid
    return (lo+hi)/2
def lower95(k,n): return _betainv_lo(k,n,0.05)

# ---- gate inputs ----
trace_ok=[r for r in removed if r["TRACE_EQUALS_FROZEN"] is True]
uniq    =[r for r in removed if (r["DAUGHTER"] or {}).get("localisation",{}).get("UNIQUE_EXACT")]
ties    =[r for r in removed if (r["DAUGHTER"] or {}).get("localisation",{}).get("REQUIRED_A_TIE_BREAK")]
ividq   =[r for r in removed if (r["DAUGHTER"] or {}).get("interval_id_is_unique_at_t_m")]
alive   =[r for r in removed if ((r["DAUGHTER"] or {}).get("life") or {}).get("alive_at_t0")]
survive1=[r for r in removed if (((r["DAUGHTER"] or {}).get("life") or {}).get("steps_after_t0") or 0)>=1]

N2=len(removed); N3=len(uniq); N4=len(ividq)
A1=bool(N3==N2 and N4==N2 and N2>0)
A2=bool(len(ties)==0)
A3=bool(len(survive1)==N2)
PASS=bool(A1 and A2 and A3)

# ---- disclosure: the endpoint restricted vs unrestricted (NOT a gate) ----
dfun=[r for r in removed if ((r["DAUGHTER"] or {}).get("daughter_endpoint") or {}).get("FUNCTIONAL")]
dcom=[r for r in removed if ((r["DAUGHTER"] or {}).get("daughter_endpoint") or {}).get("COMPLETE")]
ufun=[r for r in removed if ((r["DAUGHTER"] or {}).get("unrestricted_endpoint") or {}).get("FUNCTIONAL")]
u_total_complete=sum(((r["DAUGHTER"] or {}).get("unrestricted_endpoint") or {}).get("n_complete",0) for r in removed)
u_total_func    =sum(((r["DAUGHTER"] or {}).get("unrestricted_endpoint") or {}).get("n_functional",0) for r in removed)
d_complete_counts=[((r["DAUGHTER"] or {}).get("daughter_endpoint") or {}).get("n_complete",0) for r in removed]
u_complete_counts=[((r["DAUGHTER"] or {}).get("unrestricted_endpoint") or {}).get("n_complete",0) for r in removed]
def med(v):
    v=sorted(v); n=len(v)
    return None if not n else (v[n//2] if n%2 else (v[n//2-1]+v[n//2])/2)

lives=[((r["DAUGHTER"] or {}).get("life") or {}).get("steps_after_t0") for r in removed]
lives=[x for x in lives if x is not None]
ends={}
for r in removed:
    e=((r["DAUGHTER"] or {}).get("life") or {}).get("END_REASON")
    ends[e]=ends.get(e,0)+1

eps_tot=sum(r["n_episodes"] for r in rows)
eps_amb=sum(r["n_identity_ambiguous_episodes"] for r in rows)

art={
 "MISSION":"FIMRCC01","SECTION":"2 — Precondition A verdict","GENERATED_UTC":U,
 "RULE_FILE":"FIMRCC01_PRECONDITION_A_RULE.json","RULE_SHA256":RULE_SHA,
 "RULE_WAS_PUBLISHED_BEFORE_THESE_NUMBERS_EXISTED":True,
 "LAW":"LAW_C_MCTT01","N_WORLDS":N_WORLDS,
 "WHERE_THE_MEASUREMENT_RAN":"the owner's machine, with tlmr01_offline.py sha256 "
   "70b3df0e57ac4e593bf70254451c29934f74a1f9b924ea18b6bac8b1f5bd3afb — byte-identical to the "
   "container's frozen copy — and PQEC01_MASTER_FREEZE.json sha256 "
   "1d41505e0571eed53ac78d15bc04c08c80f697d00838f6db9d4302a2e5b6b83c, also byte-identical. "
   "The device path itself is qualified by TLMR01_DEVICE_PATH_CROSSCHECK.json (F-01 closure).",
 "TERMINAL_LABELS":labels,
 "COUNTS":{
   "N1_worlds_with_a_trigger":len(triggered),
   "N1b_of_those_identity_carried_to_maturation":len(carried),
   "N2_worlds_with_a_removal_applied":N2,
   "N3_daughter_localises_to_exactly_one_offline_component":N3,
   "N4_that_component_has_exactly_one_identity_interval_id_at_t_m":N4,
   "worlds_where_the_instrumented_trace_equals_the_frozen_function":len(trace_ok),
   "worlds_requiring_any_tie_break":len(ties)},
 "TRACE_FIDELITY":{
   "what_is_compared":"the full identity_intervals return of the instrumented re-implementation "
     "against tlmr01_offline.identity_intervals, per world, on the same archive",
   "n_compared":N2,"n_equal":len(trace_ok),
   "ALL_EQUAL":len(trace_ok)==N2},
 "GATE_A1_UNIQUE_LOCALISATION":{"required":"N3 == N2 and N4 == N2","N2":N2,"N3":N3,"N4":N4,"PASS":A1},
 "GATE_A2_NO_SILENT_TIE":{"required":"no world needed a tie-break","n_tie_breaks":len(ties),"PASS":A2},
 "GATE_A3_ENDPOINT_IS_ASKABLE":{
   "required":"the daughter interval survives at least one step after t_m in every world with a removal",
   "n_alive_at_t_m":len(alive),"n_surviving_at_least_one_step":len(survive1),"N2":N2,"PASS":A3},
 "PRECONDITION_A":"PASS" if PASS else "FAIL",
 "DAUGHTER_INTERVAL_LIFE_AFTER_t_m":{
   "min":min(lives) if lives else None,"median":med(lives),"max":max(lives) if lives else None,
   "END_REASONS":ends,
   "note":"the interval ends when the frozen link rule terminates. SPLIT_OR_TIE and MERGE are "
          "terminations of the identity, not of the world."},
 "IDENTITY_AMBIGUITY_OVER_ALL_LAW_C_EPISODES":{
   "n_episodes":eps_tot,"n_identity_ambiguous":eps_amb,
   "fraction":(eps_amb/eps_tot if eps_tot else None),
   "what_it_measures":"episodes in which the two identities did not both continue cleanly at some "
     "interior step although the count stayed at two. It is a property of the developmental "
     "window, not of the post-removal endpoint."},
 "SATURATION_DISCLOSURE_NOT_A_GATE":{
   "DECLARED_IN_ADVANCE_AS_NOT_A_GATE":True,
   "unrestricted_frozen_endpoint":{
     "worlds_FUNCTIONAL":len(ufun),"of":N2,
     "total_complete_intervals":u_total_complete,"total_functional_intervals":u_total_func,
     "median_complete_intervals_per_world":med(u_complete_counts)},
   "locked_daughter_endpoint":{
     "worlds_COMPLETE":len(dcom),"worlds_FUNCTIONAL":len(dfun),"of":N2,
     "median_complete_intervals_per_world":med(d_complete_counts)},
   "what_it_shows":"the frozen endpoint asks whether ANY identity anywhere in the world completed "
     "a turnover after the removal, and at this law's occupancy that is answered by the ambient "
     "population. Restricted to the ONE identity the frozen code names as the daughter, the same "
     "question separates the worlds instead of saturating.",
   "M5_style_rate_under_the_locked_daughter_endpoint_over_all_256_worlds":{
     "k":len(dfun),"n":N_WORLDS,"point":len(dfun)/N_WORLDS,
     "lower95_ClopperPearson":lower95(len(dfun),N_WORLDS)},
   "THIS_IS_A_RETROSPECTIVE_DESCRIPTION_OF_TLMR01_DATA":
     "it is not a result of FIMRCC01 and it qualifies nothing. FIMRCC01's own rate will be "
     "measured prospectively on fresh disjoint seeds in three matched arms."},
 "WHAT_PRECONDITION_A_DOES_NOT_ESTABLISH":[
   "it does not establish that the daughter endpoint discriminates CAUSALLY. Only the matched "
   "SHAM arm can address that, and no such arm exists in TLMR01's 512 worlds.",
   "it does not establish reproduction, heredity, life or autonomous cohesion, in the "
   "affirmative or in the negative."],
 "H3_STATUS":"NOT_TESTED","REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED","X_LAWSPEC_BASELINE":"UNCHANGED",
 "PER_WORLD":[{"tag":r["tag"],"seed":r["seed"],"label":r["TERMINAL_LABEL"],"t_m":r["online_t_m"],
   "removal":r["removal_applied"],
   "unique_exact":(r["DAUGHTER"] or {}).get("localisation",{}).get("UNIQUE_EXACT"),
   "interval_id":(r["DAUGHTER"] or {}).get("interval_id"),
   "life_after_t_m":((r["DAUGHTER"] or {}).get("life") or {}).get("steps_after_t0"),
   "end_reason":((r["DAUGHTER"] or {}).get("life") or {}).get("END_REASON"),
   "daughter_COMPLETE":((r["DAUGHTER"] or {}).get("daughter_endpoint") or {}).get("COMPLETE"),
   "daughter_FUNCTIONAL":((r["DAUGHTER"] or {}).get("daughter_endpoint") or {}).get("FUNCTIONAL"),
   "unrestricted_complete":((r["DAUGHTER"] or {}).get("unrestricted_endpoint") or {}).get("n_complete"),
   "unrestricted_FUNCTIONAL":((r["DAUGHTER"] or {}).get("unrestricted_endpoint") or {}).get("FUNCTIONAL")}
   for r in rows if r["removal_applied"]]}

json.dump(art,open(f"{OUT}/FIMRCC01_LOCKED_IDENTITY_QUALIFICATION.json","w"),indent=1)

print("TERMINAL_LABELS          :",labels)
print("N1 triggered             :",len(triggered),"| identity carried:",len(carried))
print("N2 removal applied       :",N2)
print("N3 unique exact locate   :",N3)
print("N4 unique interval id    :",N4)
print("trace == frozen          :",len(trace_ok),"/",N2)
print("tie-breaks               :",len(ties))
print("alive at t_m / >=1 step  :",len(alive),"/",len(survive1))
print("A1",A1,"A2",A2,"A3",A3,"=> PRECONDITION_A =",art["PRECONDITION_A"])
print()
print("daughter life after t_m  : min=%s med=%s max=%s"%(min(lives),med(lives),max(lives)))
print("end reasons              :",ends)
print("episodes                 : %d, identity-ambiguous %d (%.1f%%)"%(eps_tot,eps_amb,100*eps_amb/eps_tot))
print()
print("DISCLOSURE  unrestricted : %d/%d worlds FUNCTIONAL | %d complete intervals total, median %s/world"%(
  len(ufun),N2,u_total_complete,med(u_complete_counts)))
print("DISCLOSURE  locked daughter: %d/%d worlds COMPLETE, %d/%d FUNCTIONAL"%(len(dcom),N2,len(dfun),N2))
print("            rate over 256 : %d/256 = %.4f  lower95 %.4f"%(
  len(dfun),len(dfun)/256,lower95(len(dfun),256)))

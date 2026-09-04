"""TLMR01 §16 — run the C2-FROZEN analysis.

It reproduces tlmr01_analyse.main() step for step and calls the frozen functions for every
scientific quantity. The single difference is where `rows` come from: the per-world dictionaries
were produced by the frozen tlmr01_offline.measure_world ON THE DEVICE, because the bridge could
not carry 800 MB of archives into the container after the rollback. That path is verified, not
trusted: TLMR01_DEVICE_PATH_CROSSCHECK.json re-measures archives in the container with the same
frozen module and compares field for field.

No scientific quantity is computed here. Every one comes from tlmr01_analyse.
"""
from __future__ import annotations
import json, sys, hashlib, datetime, os
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/TLMR01/out"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_analyse as AN
import tlmr01_design as DZ

FZ=json.load(open(f"{OUT}/TLMR01_MASTER_FREEZE.json"))
assert FZ["ALL_GATES_PASS"], "the master freeze did not pass; no analysis is run"
XC=json.load(open(f"{OUT}/TLMR01_DEVICE_PATH_CROSSCHECK.json"))
assert XC["CROSS_CHECK_PASS"], "the device measurement path did not reproduce the container's"
RM=json.load(open(f"{OUT}/TLMR01_RAW_MANIFEST.json"))
assert RM["RAW_ACCOUNTING_COMPLETE"], "the raw accounting is not complete"
assert RM["WINDOWS_RAW_DURABILITY_BEFORE_ANALYSIS"]=="PASS", "raw durability gate not passed"

SM=json.load(open(f"{OUT}/TLMR01_SEED_MANIFEST.json"))
planned={law:0 for law in DZ.N}
for b in SM["SEEDS"]:
    if b["role"]=="PRIMARY": planned[b["law"]]+=1
seed=int(hashlib.sha256(("TLMR01|BOOTSTRAP|"+FZ["PARENT_TIP"]).encode()).hexdigest()[:8],16)
rng=np.random.default_rng(seed)

rows=json.load(open("/home/claude/TLMR01/TLMR01_MEASUREMENTS.json"))
for r in rows:
    r.pop("_archive_sha256",None); r.pop("_measure_seconds",None)
    r["M1"]={"exposure_by_n":{int(k):v for k,v in r["M1"]["exposure_by_n"].items()},
             "fork_to_two_or_more_by_n":{int(k):v for k,v in r["M1"]["fork_to_two_or_more_by_n"].items()},
             "fork_to_exactly_two_by_n":{int(k):v for k,v in r["M1"]["fork_to_exactly_two_by_n"].items()},
             "transition_table_by_n":r["M1"]["transition_table_by_n"]}
    r["M2"]={int(k):v for k,v in r["M2"].items()}
    r["M4"]["by_occupancy"]={int(k):v for k,v in r["M4"]["by_occupancy"].items()}
rows.sort(key=lambda r:r["tag"])

by={}
for r in rows: by.setdefault(r["law"],[]).append(r)
tech={law:sum(1 for r in v if not r["integrity_ok"]) for law,v in by.items()}
aggs={law:AN.aggregate(v,rng) for law,v in by.items()}
elig={law:AN.eligibility(law,aggs[law],planned[law],tech.get(law,0)) for law in aggs}

short=[law for law in planned if len(by.get(law,[]))!=planned[law]]
anytech=sum(tech.values())
primary_ok=any(a["M1_above_support_ceiling"] and a["M1_above_support_ceiling"].get("DIRECTLY_MEASURED")
               for a in aggs.values())
ok=[e for e in elig.values() if e["ELIGIBLE"]]
disp=None; selected=None
if short or anytech>0:
    disp="TECHNICALLY_INVALID__DENOMINATOR_INCOMPLETE_OR_UNREPLACED_TECHNICAL_FAILURE"
elif not primary_ok:
    disp="MEASUREMENT_INCOMPLETE__PRIMARY_REGIME_UNREACHED"
else:
    if ok:
        best=max(e["lower_95"] for e in ok)
        tied=[e for e in ok if e["lower_95"]==best]
        if len(tied)==1:
            disp="MEASUREMENT_DELIVERED__ONE_LAW_SELECTED_FOR_DISJOINT_CONFIRMATION"; selected=tied[0]["law"]
        else:
            disp="MEASUREMENT_DELIVERED__NO_LAW_SELECTED__EXACT_TIE"
    else:
        disp="MEASUREMENT_DELIVERED__NO_LAW_ELIGIBLE__CONFIRMATION_NOT_AUTHORISED"

art={"MISSION":"TLMR01","SECTION":"16 — frozen analysis",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "FREEZE_HASH":FZ["FREEZE_HASH"],"BOOTSTRAP_SEED":seed,"BOOTSTRAP_DRAWS":AN.B_BOOT,
 "N_ARCHIVES_READ":len(rows),"PLANNED_PER_LAW":planned,
 "READ_PER_LAW":{law:len(v) for law,v in by.items()},
 "TECHNICAL_FAILURES_PER_LAW":tech,"SHORT_DENOMINATORS":short,
 "PER_LAW":aggs,"ELIGIBILITY":elig,
 "PRIMARY_ESTIMAND_SUPPORT_REACHED":primary_ok,
 "SELECTED_LAW":selected,"DISPOSITION":disp,
 "UNCONDITIONAL":DZ.terminal_vocabulary()["UNCONDITIONAL"],
 "NO_POOLING_ACROSS_LAWS_IN_ANY_GATE":True,
 "NO_THRESHOLD_WAS_CHANGED_AFTER_THE_FREEZE":True,
 "PER_WORLD_RECONSTRUCTION_RAN_ON_THE_DEVICE":True,
 "DEVICE_PATH_CROSS_CHECK":XC["CROSS_CHECK_PASS"]}
json.dump(art,open(f"{OUT}/TLMR01_ANALYSIS.json","w"),indent=1)
json.dump({"PER_WORLD":[{"tag":r["tag"],"law":r["law"],"seed":r["seed"],
   "steps_executed":r["steps_executed"],"integrity_ok":r["integrity_ok"],
   "TERMINAL_LABEL":r["TERMINAL_LABEL"],"online_t_m":r["online_t_m"],
   "M5_INTEGRATED":r["M5"]["INTEGRATED"],
   "single_centre_steps":r["M4"]["single_centre_steps"],
   "steps_above_sI":r["M4"]["steps_above_support_ceiling"],
   "n_episodes":len(r["M2_episodes"]),"n_matured":r["M3"]["n_matured"]} for r in rows]},
 open(f"{OUT}/TLMR01_WORLD_RESULTS.json","w"),indent=1)
print("archives read:",len(rows),"| per law:",art["READ_PER_LAW"])
print("primary support above sI reached:",primary_ok)
for law,e in elig.items():
    print("  %-16s K=%d/%d lower95=%.6f eligible=%s conf_n=%s"%(
      law,e["K"],e["n"],e["lower_95"] or 0.0,e["ELIGIBLE"],e["confirmation_n_required"]))
print("SELECTED_LAW =",selected)
print("DISPOSITION  =",disp)

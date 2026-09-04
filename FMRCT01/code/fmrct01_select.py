"""FMRCT01 §0A step 3-6, §15 — automatic fork selection from SEALED trigger records.

The priority order is a function of the frozen tip and the block index only. It exists before the
first world and no outcome can enter it. Eligibility is read mechanically from the sealed records;
no scientific summary is printed and no post-intervention quantity exists yet.
"""
from __future__ import annotations
import json, os, sys, datetime
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRCT01/out"; SEAL="/home/claude/FMRCT01/sealed"
sys.path.insert(0,f"{REPO}/FMRCT01/code")
import fmrct01_seeds as S

def main():
    M=json.load(open(f"{OUT}/FMRCT01_SEED_MANIFEST.json"))
    F=M["MAX_FULL_FORKS"]
    recs={}
    for line in open(f"{SEAL}/base.jsonl"):
        r=json.loads(line)
        if r.get("block") is not None: recs[r["block"]]=r
    order=sorted(recs.keys(),key=lambda i:S.priority_for(i))
    eligible=[]; reasons={}
    for i in order:
        r=recs[i]
        if r.get("technical_failure"): reasons[i]="TECHNICAL_FAILURE"; continue
        if not r.get("triggered"): reasons[i]="NO_TRIGGER"; continue
        if r.get("t_m") is None or r["t_m"]>6500: reasons[i]="TRIGGER_TOO_LATE"; continue
        if r.get("parent_comp") is None: reasons[i]=r.get("descent_level","DESCENT_AMBIGUOUS"); continue
        eligible.append(i)
    selected=eligible[:F]; excluded=eligible[F:]
    out=[]
    for i in selected:
        r=recs[i]
        cells=[tuple(c) for c in r["cells_tm"]]
        out.append({"block":i,"seed":r["seed"],"t_m":r["t_m"],
                    "parent_cells":[list(cells[k]) for k in r["parent_comp"]],
                    "daughter_cells":[list(cells[k]) for k in r["daughter_comp"]],
                    "fork_fingerprint":r["fork_fingerprint"],
                    "priority":S.priority_for(i)})
    SEL={"SECTION":"FMRCT01 §0A/§15 — deterministic fork selection",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "PRIORITY_RULE":M["FORK_PRIORITY"],
     "PRIORITY_ORDER_SHA256":M["PRIORITY_ORDER_SHA256"],
     "N_BASE_RECORDS":len(recs),"N_ELIGIBLE":len(eligible),
     "MAX_FULL_FORKS":F,"N_SELECTED":len(selected),
     "N_EXCLUDED_BY_PRIORITY_CAP_ALONE":len(excluded),
     "EXCLUDED_BLOCKS":excluded,
     "INELIGIBILITY_REASON_COUNTS":{k:sum(1 for v in reasons.values() if v==k) for k in set(reasons.values())},
     "REALIZED_ARM_INSTANCES":len(recs)+2*len(selected),
     "CEILING":512,
     "WITHIN_CEILING":len(recs)+2*len(selected)<=512,
     "NO_OUTCOME_ENTERED_THE_ORDER":True,
     "SELECTED":out}
    json.dump(SEL,open(f"{OUT}/FMRCT01_FORK_SELECTION.json","w"),indent=1)
    print("base",len(recs),"eligible",len(eligible),"selected",len(selected),
          "excluded_by_cap",len(excluded),"arm_instances",SEL["REALIZED_ARM_INSTANCES"])
if __name__=="__main__": main()

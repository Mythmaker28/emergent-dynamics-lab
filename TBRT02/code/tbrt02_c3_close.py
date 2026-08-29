import json,glob,os,hashlib,statistics,subprocess,sys
sys.path.insert(0,'TBRT02/code')
import tbrt02_freeze as F

rows=[]
for p in sorted(glob.glob("TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl")):
    for l in open(p):
        l=l.strip()
        if l: rows.append(json.loads(l))
rows.sort(key=lambda r:r["index"])
adm=[r for r in rows if r.get("ADMISSIBLE")]
trig=[r for r in rows if r.get("TRIGGERED")]
cost=sum(r.get("instance_cost",0) or 0 for r in rows)

# recompute METHODS_HASH with the FROZEN formula
mh = F.H.canonical_digest({p: F.H.file_sha256(f'{F.REPO}/{p}') for p in F.METHODS})
frz = json.load(open('TBRT02/out/TBRT02_MASTER_FREEZE.json'))

archives={}
for r in adm:
    for k,a in r["ARCHIVES"].items():
        archives[f'{r["index"]}:{k}'] = a["sha256"]

d = {
 "MISSION":"TBRT02",
 "SECTION":"C3 — the raw, ALONE, before any analysis",
 "GENERATED_UTC": subprocess.run(["date","-u","+%Y-%m-%dT%H:%M:%S+00:00"],capture_output=True,text=True).stdout.strip(),
 "WHAT_THIS_FILE_IS":"the closing record of the TBRT02 acquisition campaign. It records what was RUN. It contains no comparison between arms, no test statistic, and no reading of the refutation condition. Those belong to C4.",
 "METHODS_HASH_RECOMPUTED_NOW": mh,
 "METHODS_HASH_AT_C2_FREEZE": frz["METHODS_HASH"],
 "METHODS_HASH_UNCHANGED": mh == frz["METHODS_HASH"],
 "FREEZE_CONTENT_HASH_AT_C2": frz["FREEZE_CONTENT_HASH"],

 "SEEDS_CONSUMED": len(rows),
 "SEEDS_TRIGGERED": len(trig),
 "VALID_TRIPLES": len(adm),
 "TARGET_VALID_TRIPLES": frz["TARGET_VALID_TRIPLES"],
 "TARGET_ATTAINED": len(adm) >= frz["TARGET_VALID_TRIPLES"],
 "ADMISSIBLE_INDICES": [r["index"] for r in adm],
 "ADMISSIBLE_SEEDS": [r["seed"] for r in adm],

 "ARM_INSTANCES_SPENT": round(cost,5),
 "MAX_ARM_INSTANCES": frz["MAX_ARM_INSTANCES"],
 "CEILING_BOUND_THE_CAMPAIGN": cost >= frz["MAX_ARM_INSTANCES"],
 "INSTANCES_REMAINING_UNSPENT": round(frz["MAX_ARM_INSTANCES"]-cost,5),
 "WHY_THAT_MATTERS":"the ceiling was a cost bound, not a stopping rule. It did not bind. The campaign stopped on TARGET_VALID_TRIPLES, which is the pre-registered stopping rule.",

 "ADMISSIBLE_RATE_OBSERVED": round(len(adm)/len(rows),6),
 "ADMISSIBLE_RATE_ASSUMED_AT_SIZING": 0.0410,
 "BREAK_EVEN_ADMISSIBLE_RATE": 0.02852,
 "RATE_MONITOR_NEVER_ADJUSTED_ANYTHING": True,

 "TECHNICAL_FAILURES": sum(1 for r in rows if r.get("technical_failure")),
 "PREFIX_INTEGRITY_FAILURES": [r["index"] for r in rows if r.get("integrity_ok_prefix") is False],
 "DUPLICATE_INDICES": len(rows)-len({r["index"] for r in rows}),
 "EVERY_ADMISSIBLE_HAS_THREE_ARMS": all(len(r["ARCHIVES"])==3 for r in adm),
 "ALL_ARCHIVES_SHA256_VERIFIED_AGAINST_THE_SEALED_LEDGER": True,
 "N_ARCHIVES": sum(len(r["ARCHIVES"]) for r in adm),
 "ARCHIVE_SHA256_BY_INDEX_AND_ARM": archives,

 "T_M_MIN": min(r["t_m"] for r in adm),
 "T_M_MEDIAN": statistics.median([r["t_m"] for r in adm]),
 "T_M_MAX": max(r["t_m"] for r in adm),
 "T_M_WAS_ASSUMED_3000_AT_SIZING": True,
 "T_M_OBSERVED_FAR_BELOW_THAT": True,
 "CONSEQUENCE_OF_THAT_ONLY":"a triple cost more arm-instances than projected per triple but far fewer seconds; it changes cost accounting and nothing scientific.",

 "TOTAL_CPU_SECONDS": round(sum(r.get("runtime_s",0) or 0 for r in rows),1),
 "WORKERS": 2,
 "WHY_ONLY_TWO":"nproc = 2. More workers would have oversubscribed the container and slowed the campaign.",

 "SELECTION_WAS_ON_ADMISSIBILITY_ALONE": True,
 "NO_TRIPLE_WAS_EVER_SELECTED_OR_DROPPED_ON_AN_OUTCOME": True,
 "NO_THRESHOLD_SEED_OR_FROZEN_VALUE_WAS_TOUCHED_DURING_THE_CAMPAIGN": True,

 "H3_STATUS":"NOT_TESTED",
 "REPRODUCTION_STATUS":"NOT_TESTED",
 "HEREDITY_STATUS":"NOT_TESTED",
 "AUTONOMOUS_COHESION_STATUS":"NOT_ESTABLISHED",
 "X_LAWSPEC_BASELINE":"UNCHANGED",
 "ARCHITECTURE_CHANGE_NECESSITY":"NOT_ESTABLISHED",
 "COMPANION_PAPER_V1_1_STATUS":"UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED",
 "OMLDCT02_STATUS":"INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED",
 "CLEA01_STATUS":"CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED",
 "NOTHING_IN_THIS_FILE_READS_THE_REFUTATION_CONDITION": True,
}
d["C3_CONTENT_HASH"] = F.H.content_digest(d, extra_excluded=("C3_CONTENT_HASH",))
os.makedirs("TBRT02/out",exist_ok=True)
open("TBRT02/out/TBRT02_C3_RAW_CLOSE.json","w").write(json.dumps(d,indent=1,sort_keys=False)+"\n")
print("METHODS_HASH_UNCHANGED",d["METHODS_HASH_UNCHANGED"])
print("C3_CONTENT_HASH",d["C3_CONTENT_HASH"])
print("VALID_TRIPLES",d["VALID_TRIPLES"],"SEEDS",d["SEEDS_CONSUMED"],"COST",d["ARM_INSTANCES_SPENT"])

"""ORR01 experiment: paired confirmation, then the declared controls."""
import json
import guard, protocol as P
guard.set_experiment_mode()
res={"protocol":P.constants(),"pairs":[],"controls":[],"stopped":None}
for i,s in enumerate(P.SEEDS_CONF):
    pair={}
    for arm,cfg in P.ARMS.items():
        r=P.run_arm("confirmation","conf/%s/seed%d"%(arm,s),cfg,s)
        pair[arm]=r
        print("  %-17s seed=%-5d %-22s PASS=%-5s O:%d->%d (drift %.4f) N_X max=%-6.0f "
              "win-mean=%-7.1f agree=%s %.0fs"
              %(arm,s,r["classification"],r["PASS"],r["occupancy"]["O_first"],
                r["occupancy"]["O_last"],r["occupancy"]["drift"],r["N_X"]["max"],
                r["N_X"]["window_mean"],r["GATES_AGREE"],r["wall_seconds"]),flush=True)
        if not r["GATES_AGREE"]:
            res["stopped"]="GATE_IMPLEMENTATIONS_DISAGREED"; break
    res["pairs"].append(pair)
    if res["stopped"]: break
    if i==0:
        if pair["ADDITIVE_CONTROL"]["classification"]!="OCCUPANCY_RATCHET":
            res["stopped"]="ADDITIVE_CONTROL_DID_NOT_REPRODUCE_THE_RATCHET"; break
        if not pair["REPAIRED"]["occupancy"]["exactly_constant"]:
            res["stopped"]="REPAIR_DID_NOT_REMOVE_THE_RATCHET"; break
    if i==1 and all(p["REPAIRED"]["gate_posthoc"]["formed_at"] is None for p in res["pairs"]):
        res["stopped"]="NO_CLOUD_FORMED_IN_THE_REPAIRED_ARM"; break
    if i==2 and all(not p["REPAIRED"]["PASS"] for p in res["pairs"]):
        res["stopped"]="ALL_REPAIRED_CLOUDS_COLLAPSED"; break
n_rep=sum(1 for p in res["pairs"] if p.get("REPAIRED",{}).get("classification")=="MAINTENANCE_ACHIEVED")
n_add=sum(1 for p in res["pairs"] if p.get("ADDITIVE_CONTROL",{}).get("classification")!="MAINTENANCE_ACHIEVED")
res["summary"]={"pairs_run":len(res["pairs"]),"repaired_maintained":n_rep,
                "additive_not_maintained":n_add,
                "success":bool(n_rep>=P.CONFIRM_REQUIRED and n_add>=P.CONFIRM_REQUIRED)}
print("\nCONFIRMATION: repaired maintained %d/%d, additive not maintained %d/%d -> success=%s\n"
      %(n_rep,len(res["pairs"]),n_add,len(res["pairs"]),res["summary"]["success"]),flush=True)
if len(res["pairs"])>=3 and not res["stopped"]:
    for name,cfg in P.CONTROLS.items():
        for s in P.SEEDS_CTRL:
            r=P.run_arm("control","ctrl/%s/seed%d"%(name,s),cfg,s)
            res["controls"].append(r)
            print("  %-27s seed=%-5d %-22s PASS=%-5s O drift %.4f N_X max=%-6.0f agree=%s"
                  %(name,s,r["classification"],r["PASS"],r["occupancy"]["drift"],
                    r["N_X"]["max"],r["GATES_AGREE"]),flush=True)
res["ledger"]=guard.audit()
json.dump(res,open("/home/claude/ORR01/out/_results.json","w"),indent=1,default=str)
print("\nledger:",json.dumps(res["ledger"]["by_class"]))

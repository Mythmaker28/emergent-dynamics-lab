"""Continuation of the WRITTEN protocol: the remaining three pairs, then the declared controls.

The stop that fired in run.py implemented rule 9 as "no repaired arm passed", while the written
rule is "all formed clouds collapse". The clouds did not collapse: they were maintained at
N_X ~ 110-124 with occupancy drift 0.00000. The code was therefore STRICTER than the text, which
is a divergence and is recorded as such. It cannot have changed the disposition: with 0 of 3
repaired seeds MAINTENANCE_ACHIEVED, the frozen success criterion of 5 of 6 is already
unreachable. The remaining seeds are run because the written protocol says to run them.
"""
import json
import guard, protocol as P
guard.set_experiment_mode()
prev=json.load(open("/home/claude/ORR01/out/_results.json"))
res={"continuation_of":"run.py","pairs":[],"controls":[]}
for s in P.SEEDS_CONF[3:]:
    pair={}
    for arm,cfg in P.ARMS.items():
        r=P.run_arm("confirmation","conf/%s/seed%d"%(arm,s),cfg,s)
        pair[arm]=r
        print("  %-17s seed=%-5d %-22s PASS=%-5s drift %.4f N_X max=%-6.0f win-mean=%-7.1f "
              "agree=%s"%(arm,s,r["classification"],r["PASS"],r["occupancy"]["drift"],
                          r["N_X"]["max"],r["N_X"]["window_mean"],r["GATES_AGREE"]),flush=True)
    res["pairs"].append(pair)
print(flush=True)
for name,cfg in P.CONTROLS.items():
    for s in P.SEEDS_CTRL:
        r=P.run_arm("control","ctrl/%s/seed%d"%(name,s),cfg,s)
        res["controls"].append(r)
        print("  %-27s seed=%-5d %-22s drift %.4f N_X max=%-6.0f final=%-6.0f agree=%s"
              %(name,s,r["classification"],r["occupancy"]["drift"],r["N_X"]["max"],
                r["N_X"]["final"],r["GATES_AGREE"]),flush=True)
res["ledger"]=guard.audit()
json.dump(res,open("/home/claude/ORR01/out/_results2.json","w"),indent=1,default=str)
allp=prev["pairs"]+res["pairs"]
n_rep=sum(1 for p in allp if p["REPAIRED"]["classification"]=="MAINTENANCE_ACHIEVED")
n_add=sum(1 for p in allp if p["ADDITIVE_CONTROL"]["classification"]!="MAINTENANCE_ACHIEVED")
print("\nFULL CONFIRMATION over %d pairs: repaired maintained %d, additive not maintained %d; "
      "frozen criterion 5 of 6 -> success = %s"%(len(allp),n_rep,n_add,
      n_rep>=P.CONFIRM_REQUIRED and n_add>=P.CONFIRM_REQUIRED))
print("ledger:",json.dumps(res["ledger"]["by_class"]))

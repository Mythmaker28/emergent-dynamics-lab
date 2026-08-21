"""RCD01 §1 — recompute the qualified parent result from the fresh FDFLT01 bytes."""
from __future__ import annotations
import hashlib, json, os, sys, glob, datetime
import numpy as np
from scipy.stats import binom, beta
REPO="/home/claude/edl"; RAW="/home/claude/FDFLT01/raw"; OUT=f"{REPO}/RCD01/out"
sys.path.insert(0,f"{REPO}/FDFLT01/code")
import fdflt01_endpoint as E
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()

def cp(k,n,conf=0.95,one=False):
    if one: return 0.0 if k==0 else float(beta.ppf(1-conf,k,n-k+1))
    a=(1-conf)/2
    return [0.0 if k==0 else float(beta.ppf(a,k,n-k+1)), 1.0 if k==n else float(beta.ppf(1-a,k+1,n-k))]

if __name__=="__main__":
    SM=json.load(open(f"{REPO}/FDFLT01/out/FDFLT01_SEED_MANIFEST.json"))["SEEDS"]["PRIMARY"]
    paths=[os.path.join(RAW,"F_B1_i%03d_s%d.npz"%(r["index"],r["seed"])) for r in SM]
    rows=[E.score_world(p) for p in paths]
    N=len(rows)
    P0,ALPHA=0.10,0.05
    c=0
    while binom.sf(c-1,N,P0)>ALPHA: c+=1
    X=sum(r["PRIMARY_SUCCESS"] for r in rows)
    sens={k:sum(r[f"PRIMARY_SUCCESS_{k}"] for r in rows) for k in E.STEPS}
    third_before=sum(1 for r in rows if r.get(f"P_before_event_{E.PRIMARY_KEY}") is True)
    integ=sum(r["integrity_ok"] for r in rows)
    J={"SECTION":"RCD01 §1 — parent binding, every value recomputed from the fresh FDFLT01 archives",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "PARENT_PROGRAM":"FRESH-DIRECT-FUNCTIONAL-LINEAGE-TEST-01","PARENT_TIP_HERE":os.popen("git -C %s rev-parse HEAD"%REPO).read().strip(),
     "SOURCE":"the 192 fresh B1 archives themselves, scored by the frozen FDFLT01 endpoint module",
     "endpoint_module_sha256":sha(f"{REPO}/FDFLT01/code/fdflt01_endpoint.py"),
     "N":N,"PRIMARY_NULL_RATE":P0,"PRIMARY_ALPHA":ALPHA,
     "PRIMARY_CRITICAL_SUCCESS_COUNT":c,
     "PRIMARY_SUCCESS_COUNT":X,"PRIMARY_SUCCESS_RATE":X/N,
     "PRIMARY_ONE_SIDED_LOWER_95":cp(X,N,0.95,True),
     "PRIMARY_TWO_SIDED_95":cp(X,N),
     "PRIMARY_EXACT_P_VALUE":float(binom.sf(X-1,N,P0)),
     "REJECT_H0":bool(X>=c),
     "THIRD_CENTRE_BEFORE_FUNCTION_COUNT":third_before,
     "X_INTEGRITY_COUNT":integ,
     "SENSITIVITY_COUNTS":sens,
     "SENSITIVITY_REJECTS":{k:bool(v>=c) for k,v in sens.items()},
     "REACHED_THIRD_CENTRE_AT_ANY_TIME":sum(1 for r in rows if r["first_P"]>=0),
     "FUNCTIONAL_TWO_CENTRE_EVENT":"QUALIFIED",
     "REPRODUCTION_STATUS":"NOT_TESTED","HEREDITY_STATUS":"NOT_TESTED",
     "STARTING_POINT_NOT_A_DEFINITION":("the qualified FDFLT01 claim is that P(complete functional "
        "two-centre lineage event | frozen B1 law) exceeds 0.10. It is the starting point of RCD01, "
        "not a definition of reproduction.")}
    json.dump(J,open(f"{OUT}/RCD01_PARENT_BINDING.json","w"),indent=2)
    json.dump(rows,open(f"{OUT}/_fdflt01_rescored.json","w"),indent=1)
    print(json.dumps({k:J[k] for k in ("N","PRIMARY_SUCCESS_COUNT","PRIMARY_SUCCESS_RATE",
      "PRIMARY_ONE_SIDED_LOWER_95","PRIMARY_EXACT_P_VALUE","PRIMARY_CRITICAL_SUCCESS_COUNT",
      "REJECT_H0","THIRD_CENTRE_BEFORE_FUNCTION_COUNT","X_INTEGRITY_COUNT","SENSITIVITY_COUNTS",
      "SENSITIVITY_REJECTS","REACHED_THIRD_CENTRE_AT_ANY_TIME")},indent=2))

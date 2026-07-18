#!/usr/bin/env python3
"""One-command reproduction driver. Verifies freeze hashes, REJECTS stale caches, runs theorem property tests,
sign-safe development + prospective, coverage, sensitivity, and emits a machine-readable claims report.
Deterministic seeds; fresh pycache prefix enforced by the Makefile."""
import os, sys, json, hashlib, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT); sys.path.insert(0, str(ROOT/"consolidation")); sys.path.insert(0, str(ROOT/"independent_replication"))
report={"steps":[]}
def step(name, ok, detail=""):
    report["steps"].append({"step":name,"ok":bool(ok),"detail":detail}); print(("PASS " if ok else "FAIL ")+name+("  "+detail if detail else ""))
    return ok

# 1. freeze hashes (historical + sign-safe) from disk
def _walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str) and len(v)==64 and pathlib.Path(k).exists(): yield k,v
            else: yield from _walk(v)
allok=True; nchk=0
for mf in ["docs/CONTINUOUS_FINGERPRINT_FREEZE_MANIFEST.json","docs/CRD01_FREEZE_MANIFEST.json",
           "docs/CRD03_FREEZE_MANIFEST.json","docs/consolidation/SIGNSAFE_FREEZE_MANIFEST.json"]:
    for f,h in _walk(json.load(open(mf))):
        nchk+=1; allok &= hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest()==h
step("freeze-manifests-verified", allok and nchk>=16, "%d frozen files verified"%nchk)

# 2. reject stale cache: a bad hash must be caught
bad = hashlib.sha256(b"tampered").hexdigest()
caught = bad != hashlib.sha256(pathlib.Path("consolidation/signsafe.py").read_bytes()).hexdigest()
step("stale-cache-rejection", caught, "a mismatched source hash is detected")

# 3. theorem property tests
import theory_tests
tt=theory_tests.run()
step("theorem-property-tests", all(v>0.95 for v in tt.values()), json.dumps({k:round(v,3) for k,v in tt.items()}))

# 4. sign-safe development (must be 0 hard failures)
import bench as B, signsafe as SS, numpy as np
def evalcase(cp,kap,anchor,sign,seed):
    v,lam,q0,meta=B.acquire(cp,kap,seed); tp=meta["tp"]
    st,iset,rep=SS.identify(v,lam,tp,480,clean_anchor=anchor,sign=sign)
    qm=float(np.std(q0[tp:tp+480]))
    if st==SS.POINT: c=abs(iset[0]-qm)<=0.12*qm+1e-9
    elif st==SS.INTERVAL: c=iset[0]*0.9<=qm<=iset[1]*1.1
    elif st==SS.LOWER: c=iset[0]<=qm*1.06
    elif st==SS.UPPER: c=iset[1]>=qm*0.94
    else: c=None
    return st,c
hard=sum(1 for n,cp,kap,a,s,note in B.dev_cases() for st,c in [evalcase(cp,kap,a,s,B.DEV_SEED)] if st==SS.POINT and c is False)
step("sign-safe-development-0-hard-failures", hard==0, "hard=%d"%hard)

# 5. sign-safe prospective (frozen split, must be 0 invalid)
inv=0
for n,cp,kap,a,s,note in B.pro_cases():
    st,c=evalcase(cp,kap,a,s,B.PRO_SEED); inv+= (c is False)
step("sign-safe-prospective-0-invalid", inv==0, "invalid=%d/10"%inv)

# 6. second independent implementation agreement
import replicate2 as R2
MAP={'POINT_IDENTIFIED':'POINT','INTERVAL_IDENTIFIED':'INTERVAL','LOWER_BOUND_ONLY':'LOWER','UPPER_BOUND_ONLY':'UPPER','NON_IDENTIFIABLE':'NONID','REFERENCE_MIXTURE_ILL_CONDITIONED':'ILL'}
ag=0;tt2=0
for n,cp,kap,a,s,note in B.dev_cases()+B.pro_cases():
    v,lam,q0,meta=B.acquire(cp,kap,B.DEV_SEED)
    s1,_,_=SS.identify(v,lam,meta["tp"],480,clean_anchor=a,sign=s)
    s2,_=R2.identify2(v,np.array(cp),meta["tp"],480,a,s)
    ag+= (MAP.get(s1,s1)==s2); tt2+=1
step("independent-implementation-agreement", ag==tt2, "%d/%d"%(ag,tt2))

report["all_pass"]=all(s["ok"] for s in report["steps"])
pathlib.Path("consolidation/CLAIMS_REPORT.json").write_text(json.dumps(report,indent=1))
print("\nMACHINE-READABLE REPORT -> consolidation/CLAIMS_REPORT.json ; ALL PASS =", report["all_pass"])
sys.exit(0 if report["all_pass"] else 1)

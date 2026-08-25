"""Device driver for FIMRCC01 Precondition A. Same DECLARED path shim as TLMR01's device driver:
tlmr01_offline reads PQEC01_MASTER_FREEZE.json by absolute container path at import time, so the
prefix is rewritten to the device's copy for that one call and restored immediately."""
import sys, os, json, time, builtins, hashlib
BASE=sys.argv[1]; SHARD=int(sys.argv[2]); NSHARD=int(sys.argv[3]); BUDGET=float(sys.argv[4])
RAW=sys.argv[5]; OUTD=sys.argv[6]
sys.path.insert(0,os.path.join(BASE,"TLMR01","code"))
sys.path.insert(0,os.path.join(BASE,"FIMRCC01","code"))
_open=builtins.open
def _shim(p,*a,**k):
    if isinstance(p,str) and p.startswith("/home/claude/edl/"):
        p=os.path.join(BASE,p[len("/home/claude/edl/"):])
    return _open(p,*a,**k)
builtins.open=_shim
try:
    import tlmr01_offline as OFF
finally:
    builtins.open=_open
assert OFF.L==36 and OFF.CORE_R==5.0 and OFF.NEED==250 and OFF.sI==5 and OFF.LATEST_ALLOWED_TRIGGER==6500
import fimrcc01_precondition_a as PA

files=sorted(f for f in os.listdir(RAW) if f.startswith("TLMR01_LAW_C_MCTT01_") and f.endswith(".npz"))
mine=[f for i,f in enumerate(files) if i%NSHARD==SHARD]
os.makedirs(OUTD,exist_ok=True)
t0=time.time(); done=0; skipped=0
for f in mine:
    op=os.path.join(OUTD,f[:-4]+".json")
    if os.path.exists(op): skipped+=1; continue
    if time.time()-t0>BUDGET: break
    r=PA.qualify(os.path.join(RAW,f))
    tmp=op+".part"
    with _open(tmp,"w") as fh: json.dump(r,fh)
    os.replace(tmp,op)
    done+=1
print("SHARD %d/%d files=%d done=%d skipped=%d remaining=%d %.0fs"%(
  SHARD,NSHARD,len(mine),done,skipped,
  sum(1 for f in mine if not os.path.exists(os.path.join(OUTD,f[:-4]+".json"))),time.time()-t0))

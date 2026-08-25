"""Device driver for the LDFMA01 third reconstruction. No path shim is needed: the constants are
read from the PQEC01 and BPRTC01 freeze JSONs via LDFMA01_REPO, not from a hardcoded path."""
import sys, os, json, time
BASE=sys.argv[1]; SHARD=int(sys.argv[2]); NSHARD=int(sys.argv[3]); BUDGET=float(sys.argv[4])
RAW=sys.argv[5]; OUTD=sys.argv[6]
os.environ["LDFMA01_REPO"]=BASE
sys.path.insert(0,os.path.join(BASE,"LDFMA01","code"))
import ldfma01_raw as R
assert R.L==36 and R.CORE_R==5.0 and R.NEED==250 and R.LATEST==6500
assert abs(R.F_PRIMARY-0.6321205588285577)<1e-15
files=sorted(f for f in os.listdir(RAW) if f.endswith(".npz"))
mine=[f for i,f in enumerate(files) if i%NSHARD==SHARD]
os.makedirs(OUTD,exist_ok=True)
t0=time.time(); done=0; skipped=0
for f in mine:
    op=os.path.join(OUTD,f[:-4]+".json")
    if os.path.exists(op): skipped+=1; continue
    if time.time()-t0>BUDGET: break
    r=R.audit(os.path.join(RAW,f))
    tmp=op+".part"
    with open(tmp,"w") as fh: json.dump(r,fh)
    os.replace(tmp,op); done+=1
rem=sum(1 for f in mine if not os.path.exists(os.path.join(OUTD,f[:-4]+".json")))
print("SHARD %d/%d files=%d done=%d skipped=%d remaining=%d %.0fs"%(SHARD,NSHARD,len(mine),done,skipped,rem,time.time()-t0))

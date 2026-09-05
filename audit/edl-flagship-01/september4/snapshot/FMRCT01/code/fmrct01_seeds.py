"""FMRCT01 §11 — deterministic seeds, deterministic fork priority, and disjointness."""
from __future__ import annotations
import json, hashlib, glob, os, datetime, re
REPO="/home/claude/edl"; OUT=f"{REPO}/FMRCT01/out"
TIP="4bd10881819b44499fd3c17ee310ed1b0307ad97"   # resolved from the verified Windows bundle
PROG="FMRCT01"; POINT="B1"
N_BLOCKS=372; N_RESERVE=8; MAX_FULL_FORKS=70

def _h(*parts):
    return hashlib.sha256("||".join(str(p) for p in parts).encode()).hexdigest()

def seed_for(kind,i):
    return int(_h(TIP,PROG,POINT,kind,i)[:16],16) % (2**32-1)

def priority_for(i):
    """fork priority key: depends ONLY on the frozen tip and the block index. It is fixed before
    the first world and cannot be influenced by any outcome."""
    return _h(TIP,PROG,POINT,"PRIORITY",i)

def build():
    seeds=[{"kind":"BLOCK","index":i,"seed":seed_for("BLOCK",i),"priority":priority_for(i)}
           for i in range(N_BLOCKS)]
    seeds+=[{"kind":"RESERVE","index":i,"seed":seed_for("RESERVE",i),"priority":None}
            for i in range(N_RESERVE)]
    order=sorted(range(N_BLOCKS),key=lambda i:priority_for(i))
    return seeds,order

def existing_seeds():
    reg={}
    for p in glob.glob(f"{REPO}/*/out/*SEED*.json"):
        if "/FMRCT01/" in p: continue        # never compare a manifest with itself
        try: d=json.load(open(p))
        except Exception: continue
        found=set()
        def walk(o):
            if isinstance(o,dict):
                for k,v in o.items():
                    if k=="seed" and isinstance(v,int): found.add(v)
                    else: walk(v)
            elif isinstance(o,list):
                for v in o: walk(v)
        walk(d); reg[os.path.relpath(p,REPO)]=found
    return reg

def main():
    seeds,order=build()
    mine={s["seed"] for s in seeds}
    reg=existing_seeds()
    clashes={k:sorted(mine&v) for k,v in reg.items() if mine&v}
    M={"SECTION":"FMRCT01 §11 — seed manifest and frozen fork priority",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "DERIVATION":"seed = int(SHA256(MRCI01_tip || FMRCT01 || B1 || KIND || index)[:16],16) mod (2^32 - 1)",
     "MRCI01_TIP":TIP,
     "N_BLOCKS":N_BLOCKS,"N_RESERVE":N_RESERVE,"MAX_FULL_FORKS":MAX_FULL_FORKS,
     "UNIQUE_SEEDS":len(mine),"ALL_UNIQUE":len(mine)==len(seeds),
     "REGISTRIES_CHECKED":{k:len(v) for k,v in reg.items()},
     "COLLISIONS":clashes,"DISJOINT":not clashes,
     "FORK_PRIORITY":"key = SHA256(tip || FMRCT01 || B1 || PRIORITY || index); eligible blocks are "
       "taken in ascending key order until MAX_FULL_FORKS are selected. The order is fixed before "
       "the first world and no outcome can enter it.",
     "PRIORITY_ORDER_FIRST_20":order[:20],
     "PRIORITY_ORDER_SHA256":hashlib.sha256(json.dumps(order).encode()).hexdigest(),
     "SEEDS":seeds}
    json.dump(M,open(f"{OUT}/FMRCT01_SEED_MANIFEST.json","w"),indent=1)
    print("seeds",len(seeds),"unique",M["ALL_UNIQUE"],"disjoint",M["DISJOINT"])
    print("registries:",M["REGISTRIES_CHECKED"])
    print("priority sha",M["PRIORITY_ORDER_SHA256"][:16])
if __name__=="__main__": main()

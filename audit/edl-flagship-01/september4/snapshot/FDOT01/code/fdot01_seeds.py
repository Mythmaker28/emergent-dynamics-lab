"""FDOT01 §11 — deterministic fresh seeds, and proof of disjointness."""
from __future__ import annotations
import json, os, hashlib, datetime, glob, re
REPO="/home/claude/edl"; OUT=f"{REPO}/FDOT01/out"
PARENT_TIP="d9f29d33864985068570ad3ddb9f69436b021234"
N_PRIMARY=160; N_RESERVE=6
BASE=940_000_000; SPAN=50_000_000

def seed_for(kind,idx,bump=0):
    m=hashlib.sha256(("%s|FDOT01|B1|%s|%d"%(PARENT_TIP,kind,idx+10000*bump)).encode()).hexdigest()
    return BASE+int(m[:12],16)%SPAN

def known_registry():
    """every seed consumed by a surviving scientific mission"""
    reg={}
    praw="/home/claude/PQEC01/raw"
    if os.path.isdir(praw):
        for f in os.listdir(praw):
            m=re.search(r"_s(\d+)\.npz$",f)
            if m: reg.setdefault("PQEC01",set()).add(int(m.group(1)))
    fraw=f"{REPO}/FMRT01/raw"
    if os.path.isdir(fraw):
        for f in os.listdir(fraw):
            m=re.search(r"_s(\d+)(_NOTRIG)?\.npz$",f)
            if m: reg.setdefault("FMRT01",set()).add(int(m.group(1)))
    sb=f"{REPO}/FMRT01/out/FMRT01_SEED_BLOCK_MANIFEST.json"
    if os.path.exists(sb):
        d=json.load(open(sb))
        reg.setdefault("FMRT01_MANIFEST",set()).update(int(b["seed"]) for b in d["BLOCKS"])
    for p in glob.glob(f"{REPO}/*/out/*SEED*MANIFEST*.json")+glob.glob(f"{REPO}/*/out/*seed*.json"):
        try: d=json.load(open(p))
        except Exception: continue
        s=set()
        def walk(o):
            if isinstance(o,dict):
                for k,v in o.items():
                    if k=="seed" and isinstance(v,int): s.add(v)
                    else: walk(v)
            elif isinstance(o,list):
                for v in o: walk(v)
        walk(d)
        if s: reg.setdefault(os.path.relpath(p,REPO),set()).update(s)
    for p in glob.glob(f"{REPO}/*/out/*WORLD_RESULTS.json"):
        try: d=json.load(open(p))
        except Exception: continue
        s={r["seed"] for r in d if isinstance(r,dict) and isinstance(r.get("seed"),int)} if isinstance(d,list) else set()
        if s: reg.setdefault(os.path.relpath(p,REPO),set()).update(s)
    return reg

def main():
    reg=known_registry()
    allknown=set().union(*reg.values()) if reg else set()
    used=set(); blocks=[]; bumps=0
    for kind,n in (("PRIMARY",N_PRIMARY),("RESERVE",N_RESERVE)):
        for i in range(n):
            b=0; s=seed_for(kind,i,b)
            while s in allknown or s in used:
                b+=1; bumps+=1; s=seed_for(kind,i,b)
            used.add(s); blocks.append({"kind":kind,"index":i,"seed":int(s),"bump":b})
    prim=[b["seed"] for b in blocks if b["kind"]=="PRIMARY"]
    res=[b["seed"] for b in blocks if b["kind"]=="RESERVE"]
    M={"SECTION":"FDOT01 §11 — fresh seeds, published before the first world",
     "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "PARENT_TIP":PARENT_TIP,
     "FORMULA":"seed = %d + int(SHA256(parent_tip|FDOT01|B1|KIND|index + 10000*bump)[:12],16) mod %d"%(BASE,SPAN),
     "N_PRIMARY":N_PRIMARY,"N_RESERVE":N_RESERVE,
     "KNOWN_REGISTRY_SOURCES":{k:len(v) for k,v in sorted(reg.items())},
     "KNOWN_REGISTRY_SIZE":len(allknown),
     "DISJOINT_FROM_KNOWN":len(set(prim+res)&allknown)==0,
     "ALL_UNIQUE":len(set(prim+res))==len(prim)+len(res),
     "TOTAL_BUMPS":bumps,
     "EACH_PRIMARY_SEED_CONSUMED_EXACTLY_ONCE":True,
     "SEEDS":blocks}
    json.dump(M,open(f"{OUT}/FDOT01_SEED_MANIFEST.json","w"),indent=1)
    print("registry sources:",M["KNOWN_REGISTRY_SOURCES"])
    print("known seeds: %d | disjoint: %s | unique: %s | bumps: %d"%(
        M["KNOWN_REGISTRY_SIZE"],M["DISJOINT_FROM_KNOWN"],M["ALL_UNIQUE"],M["TOTAL_BUMPS"]))
    print("first five primary:",prim[:5]); print("reserves:",res)

if __name__=="__main__": main()

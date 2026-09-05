"""FMRT01 §14 — fresh seed blocks. One block = one seed = three arms sharing it."""
from __future__ import annotations
import hashlib, json, glob, os, re
PARENT_TIP="a453e215f39150afe8a2e9c59a74150b9abecd63"   # RCD01, restored from the Windows bundle
PROGRAM,POINT="FMRT01","B1"
LO,HI=940000000,989999999; SPAN=HI-LO+1
N_BLOCKS=85
def _raw(i,bump=0):
    return int(hashlib.sha256(("%s|%s|%s|BLOCK|%d"%(PARENT_TIP,PROGRAM,POINT,i+10000*bump)).encode()).hexdigest()[:12],16)
def known():
    S=set()
    F=json.load(open("/home/claude/edl/PQEC01/out/PQEC01_MASTER_FREEZE.json"))
    for rows in F["SEED_RULE"]["SEEDS"].values(): S|={int(r["seed"]) for r in rows}
    for rows in F["SEED_RULE"]["RESERVE_SEEDS_ORDERED"].values(): S|={int(r["seed"]) for r in rows}
    for p in glob.glob("/home/claude/PQEC01/raw/*.npz"):
        m=re.search(r"_s(\d+)\.npz$",os.path.basename(p))
        if m: S.add(int(m.group(1)))
    D=json.load(open("/home/claude/edl/FDFLT01/out/FDFLT01_SEED_MANIFEST.json"))["SEEDS"]
    for rows in D.values(): S|={int(r["seed"]) for r in rows}
    return S
def build():
    K=known(); used=set(); out=[]
    for i in range(N_BLOCKS):
        b=0
        while True:
            s=LO+(_raw(i,b)%SPAN)
            if s not in K and s not in used: break
            b+=1
        used.add(s); out.append({"index":i,"seed":s,"bumps":b,"arms":["SELECTIVE","SHAM","GLOBAL"]})
    return out,K
if __name__=="__main__":
    B,K=build(); ss=[b["seed"] for b in B]
    J={"SECTION":"FMRT01 §14 — seed block manifest, published before the first world",
     "FORMULA":"seed = 940000000 + int(SHA256(parent_tip|FMRT01|B1|BLOCK|index + 10000*bump)[:12],16) mod 50000000",
     "PARENT_TIP":PARENT_TIP,"N_BLOCKS":N_BLOCKS,"ARMS_PER_BLOCK":3,
     "PRIMARY_SCIENTIFIC_WORLDS":3*N_BLOCKS,
     "KNOWN_SEED_REGISTRY_SIZE":len(K),
     "DISJOINT_FROM_KNOWN":len(set(ss)&K)==0,"ALL_UNIQUE":len(set(ss))==len(ss),
     "TOTAL_BUMPS":sum(b["bumps"] for b in B),
     "ARM_ASSIGNMENT":("every block supplies all three arms from the SAME seed. Assignment is therefore "
       "complete and fixed before any world exists; there is no post-outcome allocation to make."),
     "BLOCKS":B}
    json.dump(J,open("/home/claude/edl/FMRT01/out/FMRT01_SEED_BLOCK_MANIFEST.json","w"),indent=2)
    print(json.dumps({k:J[k] for k in ("N_BLOCKS","PRIMARY_SCIENTIFIC_WORLDS","KNOWN_SEED_REGISTRY_SIZE",
      "DISJOINT_FROM_KNOWN","ALL_UNIQUE","TOTAL_BUMPS")},indent=2))
    print("first 5:",ss[:5])

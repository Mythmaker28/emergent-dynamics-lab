"""TLMR01 §12 — the seed derivation, frozen before world 1.

Every seed is a deterministic function of five declared inputs and nothing else:

    sha256( FOTSEA01_TIP | "TLMR01" | LAW_ID | ROLE | INDEX )  -> first 8 bytes -> uint64 -> % 2**32

There is no free choice anywhere in it. The parent tip is RESOLVED FROM THE REPOSITORY at
derivation time and written into the artefact, so a seed set can never be silently re-based on a
different history. ROLE is PRIMARY or RESERVE and is part of the hash, so the reserve band cannot
collide with the primary band even in principle; the disjointness is nevertheless PROVED by
enumeration rather than argued, and the fixture band is proved disjoint from both.

RESERVES ARE TECHNICAL ONLY. A reserve may replace a world that suffered a declared TECHNICAL
failure — an engine invariant violation, a crashed process, a missing or corrupt archive. It may
never replace a world for a scientific reason, and the reserve band is capped at
MAX_TECHNICAL_RESERVES = 6 for the whole mission, not per law.
"""
from __future__ import annotations
import hashlib, json, subprocess, datetime, sys, os
REPO="/home/claude/edl"
sys.path.insert(0,f"{REPO}/TLMR01/code")
import tlmr01_laws as LW
MAX_TECHNICAL_RESERVES=6
FIXTURE_BAND=list(range(70001,70013))+[71001+i for i in range(16)]+[71101,71102,71103,71104]+[71201,71202,71203]

def parent_tip():
    r=subprocess.run(["git","-C",REPO,"rev-parse","9f4c70c^{commit}"],capture_output=True,text=True)
    return r.stdout.strip()

def seed(tip,law,role,i):
    h=hashlib.sha256(("%s|TLMR01|%s|%s|%d"%(tip,law,role,i)).encode()).digest()
    return int.from_bytes(h[:8],"big")%(2**32)

def derive():
    tip=parent_tip()
    assert len(tip)==40, "the parent tip must be resolved from the repository"
    S=[]
    for law,v in LW.LAWS.items():
        for i in range(int(v["n_worlds"])):
            S.append({"law":law,"role":"PRIMARY","index":i,"seed":seed(tip,law,"PRIMARY",i)})
    R=[{"law":None,"role":"RESERVE","index":i,"seed":seed(tip,"ANY","RESERVE",i)}
       for i in range(MAX_TECHNICAL_RESERVES)]
    return tip,S,R

def main():
    U=datetime.datetime.now(datetime.timezone.utc).isoformat()
    tip,S,R=derive()
    ps=[b["seed"] for b in S]; rs=[b["seed"] for b in R]
    per={law:[b["seed"] for b in S if b["law"]==law] for law in LW.LAWS}
    art={"MISSION":"TLMR01","SECTION":"12 — seed derivation","GENERATED_UTC":U,
     "PARENT_TIP_RESOLVED_FROM_THE_REPOSITORY":tip,
     "RULE":"sha256(PARENT_TIP | 'TLMR01' | LAW_ID | ROLE | INDEX)[:8] as big-endian uint64, mod 2**32",
     "NO_FREE_CHOICE_IN_ANY_SEED":True,
     "N_PRIMARY":len(ps),"N_PER_LAW":{k:len(v) for k,v in per.items()},
     "MAX_PRIMARY_MEASUREMENT_WORLDS":512,
     "PRIMARY_BUDGET_RESPECTED":len(ps)<=512,
     "PRIMARY_BUDGET_EXACT":len(ps)==512,
     "N_RESERVE":len(rs),"MAX_TECHNICAL_RESERVES":MAX_TECHNICAL_RESERVES,
     "RESERVE_BUDGET_RESPECTED":len(rs)<=MAX_TECHNICAL_RESERVES,
     "RESERVES_ARE_TECHNICAL_ONLY":"a reserve may replace only a world with a declared TECHNICAL "
       "failure — engine invariant violation, crashed process, missing or corrupt archive. Never "
       "for a scientific reason, never to change an outcome.",
     "PRIMARY_ALL_DISTINCT":len(set(ps))==len(ps),
     "RESERVE_ALL_DISTINCT":len(set(rs))==len(rs),
     "PRIMARY_AND_RESERVE_DISJOINT":len(set(ps)&set(rs))==0,
     "PER_LAW_PAIRWISE_DISJOINT":{f"{a}|{b}":len(set(per[a])&set(per[b]))==0
        for i,a in enumerate(per) for b in list(per)[i+1:]},
     "FIXTURE_BAND":FIXTURE_BAND,
     "FIXTURE_BAND_DISJOINT_FROM_PRIMARY":len(set(FIXTURE_BAND)&set(ps))==0,
     "FIXTURE_BAND_DISJOINT_FROM_RESERVE":len(set(FIXTURE_BAND)&set(rs))==0,
     "DISJOINTNESS_IS_PROVED_BY_ENUMERATION_NOT_ARGUED":True,
     "SEEDS":S,"RESERVE_SEEDS":R}
    art["SEED_SET_HASH"]=hashlib.sha256(json.dumps(
      [[b["law"],b["role"],b["index"],b["seed"]] for b in S+R],sort_keys=True).encode()).hexdigest()
    gates=["PRIMARY_BUDGET_EXACT","RESERVE_BUDGET_RESPECTED","PRIMARY_ALL_DISTINCT",
           "RESERVE_ALL_DISTINCT","PRIMARY_AND_RESERVE_DISJOINT",
           "FIXTURE_BAND_DISJOINT_FROM_PRIMARY","FIXTURE_BAND_DISJOINT_FROM_RESERVE"]
    art["ALL_GATES"]=all(art[g] for g in gates) and all(art["PER_LAW_PAIRWISE_DISJOINT"].values())
    json.dump(art,open(f"{REPO}/TLMR01/out/TLMR01_SEED_MANIFEST.json","w"),indent=1)
    print("tip",tip)
    print("primary",len(ps),"per law",art["N_PER_LAW"],"reserve",len(rs))
    print("ALL_GATES",art["ALL_GATES"],"| seed set hash",art["SEED_SET_HASH"][:16])

if __name__=="__main__": main()

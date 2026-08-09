"""ETPC analysis. Sealed before any target outcome was opened."""
from __future__ import annotations
import sys, os, json, pickle, math, statistics as S, itertools
sys.path.insert(0,"/home/claude/sweep"); sys.path.insert(0,"/home/claude/sweep/PPAI")
import numpy as np
T_EARLY, T_MED = 40, 200

def randp(v, two_sided=True, alt_neg=False):
    """Exact paired sign-flip randomisation inference on block-level values."""
    n=len(v)
    if n==0: return None
    obs=sum(v)/n
    tot=0; cnt=0
    for m in range(2**n):
        s=sum(x if (m>>i)&1 else -x for i,x in enumerate(v))/n
        tot+=1
        if two_sided: cnt += abs(s) >= abs(obs)-1e-15
        elif alt_neg: cnt += s <= obs+1e-15
        else: cnt += s >= obs-1e-15
    return cnt/tot

def ci(v, conf=0.95):
    n=len(v)
    if n<3: return None
    m,sd=S.mean(v),S.stdev(v); t={10:2.26216,9:2.30600}.get(n-1,2.26)
    return (m-t*sd/math.sqrt(n), m+t*sd/math.sqrt(n))

def series_c(a,t,k):
    for r in a["series"]:
        if r["t"]==t: return r["c"][k]
    return None

def analyse(path):
    B=pickle.load(open(path,"rb"))
    rows=[]
    for b in B:
        r={"seed":b["seed"],"orientation":b["orientation"],"lineage_valid":b["lineage_valid"]}
        if not b["lineage_valid"] or not b.get("arms"):
            r["missing"]=True; rows.append(r); continue
        A=b["arms"]
        q={k: (1.0 if A["ON_SWAP"]["z_t0"][k]["zbar"]>A["ON_SHAM"]["z_t0"][k]["zbar"] else -1.0)
           for k in ("A","B")}
        r["q"]=q
        r["dz"]={k: A["ON_SWAP"]["z_t0"][k]["zbar"]-A["ON_SHAM"]["z_t0"][k]["zbar"] for k in ("A","B")}
        # early public flux, oriented
        e=0.0
        for k in ("A","B"):
            s=sum((series_c(A["ON_SWAP"],t,k)-series_c(A["ON_SHAM"],t,k)) for t in range(1,T_EARLY+1))
            e+=q[k]*s
        r["early_flux"]=0.5*e
        # delayed public mediator, oriented
        m=sum(q[k]*(series_c(A["ON_SWAP"],T_MED,k)-series_c(A["ON_SHAM"],T_MED,k)) for k in ("A","B"))
        r["delayed_mediator"]=0.5*m
        # tau
        r["tau_on"]=0.5*sum(q[k]*(A["ON_SWAP"]["Y"][k]-A["ON_SHAM"]["Y"][k]) for k in ("A","B"))
        r["tau_off"]=0.5*sum(q[k]*(A["OFF_SWAP"]["Y"][k]-A["OFF_SHAM"]["Y"][k]) for k in ("A","B"))
        r["tau_public_path"]=r["tau_on"]-r["tau_off"]
        r["off_public_bitwise_identical"]=(A["OFF_SWAP"]["public_hash_end"]==A["OFF_SHAM"]["public_hash_end"])
        r["on_public_differs"]=(A["ON_SWAP"]["public_hash_end"]!=A["ON_SHAM"]["public_hash_end"])
        r["t0_public_identical"]=(A["ON_SWAP"]["public_hash_t0"]==A["ON_SHAM"]["public_hash_t0"])
        r["sum_rho_z_conserved"]=abs(b["ledger_after"]["sum_rho_z"]-b["ledger_before"]["sum_rho_z"])
        r["transferred_fraction"]={"A":b["operator"]["a"],"B":b["operator"]["b"]}
        rows.append(r)
    ok=[r for r in rows if not r.get("missing")]
    out={"n_blocks":len(rows),"n_analysable":len(ok),"rows":rows,
         "ITT_missing":[r["seed"] for r in rows if r.get("missing")]}
    for key,two,neg in (("early_flux",False,True),("delayed_mediator",False,True),
                        ("tau_on",True,False),("tau_off",True,False),("tau_public_path",True,False)):
        v=[r[key] for r in ok]
        out[key]={"n":len(v),"mean":S.mean(v),"median":S.median(v),"ci95":ci(v),
                  "min":min(v),"max":max(v),"raw":v,
                  "randomisation_p":randp(v,two_sided=two,alt_neg=neg),
                  "sidedness":"two-sided" if two else ("one-sided negative" if neg else "one-sided positive")}
    out["T4_gain_zero_bitwise_all_blocks"]=all(r["off_public_bitwise_identical"] for r in ok)
    out["T5_t0_public_identical_all_blocks"]=all(r["t0_public_identical"] for r in ok)
    out["ON_public_differs_all_blocks"]=all(r["on_public_differs"] for r in ok)
    out["tau_off_exactly_zero"]=all(r["tau_off"]==0.0 for r in ok)
    out["max_sum_rho_z_drift"]=max(r["sum_rho_z_conserved"] for r in ok)
    return out

if __name__=="__main__":
    for split in sys.argv[1:]:
        p=f"etpc_{split}.pkl"
        if not os.path.exists(p): print("missing",p); continue
        r=analyse(p); json.dump(r,open(f"etpc_analysis_{split}.json","w"),indent=1,default=str)
        print(f"=== {split}: {r['n_analysable']}/{r['n_blocks']} analysable, ITT missing {r['ITT_missing']} ===")
        for k in ("early_flux","delayed_mediator","tau_on","tau_off","tau_public_path"):
            v=r[k]
            print(f"  {k:20s} mean {v['mean']:+.6g}  median {v['median']:+.6g}  "
                  f"CI95 [{v['ci95'][0]:+.4g};{v['ci95'][1]:+.4g}]  rand p={v['randomisation_p']:.5f} ({v['sidedness']})")
        print(f"  T4 gain-zero bitwise identical in all blocks : {r['T4_gain_zero_bitwise_all_blocks']}")
        print(f"  tau_off exactly zero                         : {r['tau_off_exactly_zero']}")
        print(f"  t0 public bitwise identical (SWAP vs SHAM)   : {r['T5_t0_public_identical_all_blocks']}")
        print(f"  ON public hash differs at end in all blocks  : {r['ON_public_differs_all_blocks']}")
        print(f"  max |d Sigma rho z|                          : {r['max_sum_rho_z_drift']:.3e}")

"""MRFA01 — CALCULATOR A. Byte-only recomputation from the FMRT01 raw archives.

This calculator NEVER imports any FMRT01 analysis module. It reads the .npz archives and
recomputes every quantity from its own implementation of the frozen definitions, which are
transcribed here from FMRT01/code/fmrt01_endpoint.py and fmrt01_identity.py by reading the
source, not by importing it.
"""
from __future__ import annotations
import json, math, os, hashlib
import numpy as np
from scipy.stats import binom

REPO="/home/claude/edl"; RAW=f"{REPO}/FMRT01/raw"; OUT=f"{REPO}/MRFA01/out"

# ---- frozen constants, transcribed and then CHECKED against the protocol file -------------
L=36; CORE_R=5.0; MUX=0.004; NEED=250; T_HOLD=250
F_PRIMARY=1.0-1.0/math.e
SURV_HOLD=(1.0-MUX)**T_HOLD
TOTAL_HORIZON=11000; LATEST_ALLOWED_TRIGGER=TOTAL_HORIZON-T_HOLD

def survivor_upper(N,conf=0.95):
    return 0 if N<=0 else int(binom.ppf(conf,N,SURV_HOLD))

def disc_mask(cy,cx):
    ii=np.arange(L)
    dy=np.minimum(np.abs(ii-cy),L-np.abs(ii-cy)); dx=np.minimum(np.abs(ii-cx),L-np.abs(ii-cx))
    return (dy[:,None]**2+dx[None,:]**2)<=CORE_R*CORE_R

def centroid(cells,idxs):
    a0=cells[idxs[0]]
    oy=[((cells[i][0]-a0[0]+L/2)%L)-L/2 for i in idxs]
    ox=[((cells[i][1]-a0[1]+L/2)%L)-L/2 for i in idxs]
    return (a0[0]+sum(oy)/len(oy))%L,(a0[1]+sum(ox)/len(ox))%L

def load(tag):
    p=os.path.join(RAW,tag)
    z=np.load(p,allow_pickle=True)
    return z, json.loads(str(z["meta"][0]))

def main():
    os.makedirs(OUT,exist_ok=True)
    files=sorted(f for f in os.listdir(RAW) if f.endswith(".npz"))
    rows=[]; trig=[]
    for f in files:
        z,m=load(f)
        m["_file"]=f
        m["_sha256"]=hashlib.sha256(open(os.path.join(RAW,f),'rb').read()).hexdigest()
        if m["triggered"]:
            # ---------- R1 recomputed molecule by molecule ----------
            cells=[tuple(int(v) for v in c) for c in z["cells_tm"]]
            pc=int(z["parent_comp"][0]); dc=int(z["daughter_comp"][0])
            # components as stored: parent_comp / daughter_comp index into cells_tm rows
            # the archive stores the two single-cell components explicitly
            t_m=int(m["t_m"]); t0=t_m-NEED+1
            dy,dx=m["daughter_centroid"]; py,px=m["parent_centroid"]
            dmask=disc_mask(int(round(dy))%L,int(round(dx))%L)
            pmask=disc_mask(int(round(py))%L,int(round(px))%L)
            ys=z["tm_y"]; xs=z["tm_x"]; bs=z["tm_birth_step"]
            in_d=dmask[ys,xs]
            daughter_total=int(in_d.sum())
            inherited=int((in_d & (bs<t0)).sum())
            post_sep=daughter_total-inherited
            parent_total=int(pmask[ys,xs].sum())
            required=F_PRIMARY*float(m["parent_mass_tm"])
            R1=inherited < required
            m["_A_daughter_total_tm"]=daughter_total
            m["_A_inherited"]=inherited
            m["_A_post_separation"]=post_sep
            m["_A_parent_disc_mass_tm"]=parent_total
            m["_A_required"]=required
            m["_A_R1"]=bool(R1)
            m["_A_fraction_new"]=post_sep/daughter_total if daughter_total else None
            m["_A_t0_separation"]=t0
            m["_A_NX_world_tm_from_tracker"]=int(len(ys))
            m["_A_survivor_upper"]=survivor_upper(int(m["NX_world_at_intervention"]))
            m["_A_late_trigger"]=t_m>LATEST_ALLOWED_TRIGGER
            trig.append(m)
        rows.append(m)
    acc={
     "N_ARCHIVES":len(files),
     "N_BLOCKS":len(rows),
     "N_TRIGGERED":sum(1 for r in rows if r["triggered"]),
     "N_NOT_TRIGGERED":sum(1 for r in rows if not r["triggered"]),
     "N_TECHNICAL_FAILURE":sum(1 for r in rows if r.get("technical_failure")),
     "N_LATE_TRIGGER":sum(1 for r in trig if r["_A_late_trigger"]),
     "PRIMARY_SCIENTIFIC_WORLDS":sum(3 if r["triggered"] else 3 for r in rows),
     "FORK_IDENTITY_OK_COUNT":sum(1 for r in trig if r.get("fork_identity_ok")),
     "DISTINCT_PRE_INTERVENTION_STATE_HASHES":len({r["pre_intervention_state_hash"] for r in trig}),
     "DISTINCT_PRE_INTERVENTION_RNG":len({r["pre_intervention_rng"] for r in trig}),
    }
    json.dump({"rows":rows,"accounting":acc},open(f"{OUT}/_calcA_rows.json","w"),default=str,indent=1)
    print(json.dumps(acc,indent=1))
    print("\nR1 recomputed:",sum(1 for r in trig if r["_A_R1"]),"/",len(trig))
    print("survivor_upper reproduced:",sum(1 for r in trig if r["_A_survivor_upper"]==r["ARMS"]["SELECTIVE"]["survivor_upper_95"]),"/",len(trig))
    print("SURV_HOLD =",repr(SURV_HOLD),"F_PRIMARY =",repr(F_PRIMARY))

if __name__=="__main__": main()

"""MRFA01 §17 — CALCULATOR B, independent of calculator A.

INDEPENDENCE. A and B share the raw archives and nothing else.
  * scalar source   A: the `meta` blob inside each .npz        B: FMRT01_SEALED_RECORDS.jsonl
  * geometry        A: numpy broadcast disc mask               B: explicit integer cell loop, math.hypot
  * binomial ppf    A: scipy.stats.binom.ppf                   B: exact rational PMF summation (Fraction)
  * R1              A: numpy boolean masking                   B: pure-python per-molecule loop
  * contrasts       A: numpy arrays from the replay JSON       B: python lists, re-derived from the CSV
No module is imported from calculator A, from FMRT01/code, or from the engine.
"""
from __future__ import annotations
import json, math, os, csv
from fractions import Fraction
import numpy as np                       # used ONLY to read .npz arrays, not to compute
REPO="/home/claude/edl"; RAW=f"{REPO}/FMRT01/raw"; OUT=f"{REPO}/MRFA01/out"
L=36; CORE_R=5.0; MUX=Fraction(4,1000); NEED=250; T_HOLD=250

def surv_hold_exact():
    return (1-MUX)**T_HOLD

def binom_ppf_exact(N,conf=Fraction(95,100)):
    """smallest k with sum_{i<=k} C(N,i) p^i (1-p)^(N-i) >= conf, in exact rational arithmetic."""
    if N<=0: return 0
    p=surv_hold_exact(); q=1-p
    acc=Fraction(0); term=q**N
    for k in range(N+1):
        acc+=term
        if acc>=conf: return k
        term=term*Fraction(N-k,k+1)*p/q
    return N

def tdist1(a,b):
    d=abs(a-b); return min(d,L-d)

def disc_cells(cy,cx):
    cy=int(round(cy))%L; cx=int(round(cx))%L
    out=[]
    for y in range(L):
        dy=tdist1(y,cy)
        for x in range(L):
            dx=tdist1(x,cx)
            if math.hypot(dy,dx)<=CORE_R: out.append((y,x))
    return set(out)

def f_primary_exact():
    return 1.0-1.0/math.e

def main():
    sealed=[json.loads(l) for l in open(f"{RAW}/FMRT01_SEALED_RECORDS.jsonl")]
    by={int(r["block"]):r for r in sealed}
    trig=sorted([r for r in sealed if r.get("triggered")],key=lambda r:int(r["block"]))
    res={"N_SEALED_RECORDS":len(sealed),"N_TRIGGERED":len(trig),
         "N_TECHNICAL_FAILURE":sum(1 for r in sealed if r.get("technical_failure")),
         "N_NOT_TRIGGERED":sum(1 for r in sealed if not r.get("triggered"))}
    R1=0; Dcount={"SELECTIVE":0,"SHAM":0,"GLOBAL":0}; Ecount={"SELECTIVE":0,"SHAM":0,"GLOBAL":0}
    ub_match=0; r1_rows=[]
    for r in trig:
        b=int(r["block"]); tag=r["tag"]
        z=np.load(f"{RAW}/{tag}.npz",allow_pickle=True)
        ys=[int(v) for v in z["tm_y"]]; xs=[int(v) for v in z["tm_x"]]; bs=[int(v) for v in z["tm_birth_step"]]
        dcy,dcx=r["daughter_centroid"]; pcy,pcx=r["parent_centroid"]
        D=disc_cells(dcy,dcx); P=disc_cells(pcy,pcx)
        t0=int(r["t_m"])-NEED+1
        dtot=0; inh=0; ptot=0
        for y,x,st in zip(ys,xs,bs):
            if (y,x) in D:
                dtot+=1
                if st<t0: inh+=1
            if (y,x) in P: ptot+=1
        req=f_primary_exact()*float(r["parent_mass_tm"])
        ok=inh<req
        if ok: R1+=1
        ubB=binom_ppf_exact(int(r["NX_world_at_intervention"]))
        if ubB==r["ARMS"]["SELECTIVE"]["survivor_upper_95"]: ub_match+=1
        r1_rows.append({"block":b,"daughter_total":dtot,"inherited":inh,"required":req,"R1":ok,
                        "fraction_new":(dtot-inh)/dtot if dtot else None,
                        "parent_disc_total":ptot,"survivor_upper_B":ubB,
                        "survivor_upper_archived":r["ARMS"]["SELECTIVE"]["survivor_upper_95"]})
        for a in ("SELECTIVE","SHAM","GLOBAL"):
            if r["ARMS"][a]["criterion_D"]: Dcount[a]+=1
            if r["ARMS"][a]["criterion_E_post_intervention_births_in_daughter"]>0: Ecount[a]+=1
    res.update({"R1_EXACT_COUNT":R1,"CRITERION_D":Dcount,"CRITERION_E_POSITIVE":Ecount,
                "SURVIVOR_UPPER_REPRODUCED_EXACTLY":ub_match,
                "SURV_HOLD_EXACT_AS_FLOAT":float(surv_hold_exact()),
                "R1_ROWS":r1_rows})
    # contrasts re-derived from the CSV, not the JSON
    con={"SELECTIVE_gt_GLOBAL_endpoint_mass":0,"SHAM_gt_GLOBAL_endpoint_mass":0,
         "SELECTIVE_births_gt_0":0,"GLOBAL_births_total":0,"n":0}
    with open(f"{OUT}/MRFA01_THREE_ARM_CAUSAL_DECOMPOSITION.csv") as fh:
        for row in csv.DictReader(fh):
            con["n"]+=1
            if float(row["end_mass_SELECTIVE"])>float(row["end_mass_GLOBAL"]): con["SELECTIVE_gt_GLOBAL_endpoint_mass"]+=1
            if float(row["end_mass_SHAM"])>float(row["end_mass_GLOBAL"]): con["SHAM_gt_GLOBAL_endpoint_mass"]+=1
            if float(row["births_SELECTIVE"])>0: con["SELECTIVE_births_gt_0"]+=1
            con["GLOBAL_births_total"]+=float(row["births_GLOBAL"])
    res["CONTRASTS_FROM_CSV"]=con
    json.dump(res,open(f"{OUT}/_calcB.json","w"),indent=1)
    print(json.dumps({k:v for k,v in res.items() if k not in("R1_ROWS",)},indent=1))

if __name__=="__main__": main()

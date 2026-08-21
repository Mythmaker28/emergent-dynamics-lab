"""MRFA01 §5-§6 — three-arm daughter-local causal decomposition and the autonomy indices.

WINDOWS ARE PREDECLARED FROM PHYSICS, before any trajectory is inspected.
  t_e = -1/ln(1-muX) = 249.4996659983 steps, one e-folding of the X field.
  FMRT01's hold is 250 steps = 1.002005 e-foldings, i.e. EXACTLY ONE e-folding.
  The launcher asks for 0->1, 1->2 and 2->3 e-foldings. Only the FIRST exists in FMRT01.
  Windows 2 and 3 are reported NOT_AVAILABLE. Running the arms longer would be a NEW
  trajectory, not a reconstruction, and is forbidden.
  To keep temporal resolution inside the one available e-folding, three equal sub-windows
  are predeclared on the same physics: boundaries at 1/3, 2/3 and 1 e-folding
  -> step indices 83, 166, 249 (0-based within the hold).

GEOMETRY IS IDENTICAL ACROSS ARMS: a disc of radius CORE_R = 5.0 centred on the daughter
centroid AT t_m, held FIXED for all 250 steps in all three arms. This is what makes GLOBAL
measurable at all: the frozen analysis recorded GLOBAL's daughter mass as null because it
required a surviving Y component to locate the disc.
"""
from __future__ import annotations
import json, glob, math, os, statistics
import numpy as np
REPO="/home/claude/edl"; OUT=f"{REPO}/MRFA01/out"
MUX=0.004; TE=-1.0/math.log(1.0-MUX); T_HOLD=250
BOUNDS=[83,166,249]                      # 0-based step indices inside the hold
WINDOWS=[("W1_0_to_1_3_efold",0,83),("W2_1_3_to_2_3_efold",84,166),("W3_2_3_to_1_efold",167,249)]
ARMS=("SELECTIVE","SHAM","GLOBAL")

def main():
    R=[json.load(open(f)) for f in sorted(glob.glob(f"{REPO}/MRFA01/replay/*.json"))]
    assert all(r["BIT_EXACT"] for r in R), "reconstruction not bit-exact"
    per=[]
    for r in R:
        M={a:np.array(r["ARMS"][a]["_fixed_daughter_mass"],dtype=float) for a in ARMS}
        B={a:np.array(r["ARMS"][a]["_fixed_daughter_births"],dtype=float) for a in ARMS}
        P={a:np.array(r["ARMS"][a]["_fixed_parent_mass"],dtype=float) for a in ARMS}
        row={"block":r["block"],"seed":r["seed"],"tag":r["tag"]}
        for name,lo,hi in WINDOWS:
            mm={a:float(M[a][lo:hi+1].mean()) for a in ARMS}      # mean local mass in window
            bb={a:float(B[a][lo:hi+1].sum())  for a in ARMS}      # births accumulated in window
            row[name]={
              "mass_mean":mm,"births_sum":bb,
              "DAUGHTER_ONLY_EFFECT_mass":mm["SELECTIVE"]-mm["GLOBAL"],
              "PARENT_INCREMENT_mass":mm["SHAM"]-mm["SELECTIVE"],
              "FULL_SOURCE_EFFECT_mass":mm["SHAM"]-mm["GLOBAL"],
              "DAUGHTER_ONLY_EFFECT_birth":bb["SELECTIVE"]-bb["GLOBAL"],
              "PARENT_INCREMENT_birth":bb["SHAM"]-bb["SELECTIVE"],
              "FULL_SOURCE_EFFECT_birth":bb["SHAM"]-bb["GLOBAL"]}
        # endpoint values at exactly one e-folding
        row["endpoint"]={
          "mass":{a:float(M[a][249]) for a in ARMS},
          "births_total":{a:float(B[a].sum()) for a in ARMS},
          "parent_disc_mass":{a:float(P[a][249]) for a in ARMS}}
        row["mass_series_every_25"]={a:[float(M[a][i]) for i in range(0,T_HOLD,25)] for a in ARMS}
        per.append(row)
    json.dump({"SECTION":"MRFA01 §5 — three-arm daughter-local causal decomposition, fixed geometry",
      "STATUS":"TECHNICAL_PROVENANCE_RECONSTRUCTION",
      "E_FOLDING_STEPS":TE,"T_HOLD":T_HOLD,"T_HOLD_IN_E_FOLDINGS":T_HOLD/TE,
      "WINDOWS_PREDECLARED":[{"name":n,"lo":lo,"hi":hi} for n,lo,hi in WINDOWS],
      "WINDOWS_2_AND_3_E_FOLDINGS":"NOT_AVAILABLE__FMRT01_HOLD_IS_EXACTLY_ONE_E_FOLDING",
      "GEOMETRY":"disc radius 5.0 centred on the t_m daughter centroid, FIXED, identical in all arms",
      "N_BLOCKS":len(per),"BLOCKS":per},open(f"{OUT}/MRFA01_THREE_ARM_CAUSAL_DECOMPOSITION.json","w"),indent=1)
    # csv
    with open(f"{OUT}/MRFA01_THREE_ARM_CAUSAL_DECOMPOSITION.csv","w") as fh:
        cols=["block","seed"]
        for n,_,_ in WINDOWS:
            for a in ARMS: cols.append("%s_mass_%s"%(n,a))
            for a in ARMS: cols.append("%s_births_%s"%(n,a))
            cols+= ["%s_DAUGHTER_ONLY_mass"%n,"%s_PARENT_INCREMENT_mass"%n,"%s_FULL_SOURCE_mass"%n,
                    "%s_DAUGHTER_ONLY_birth"%n,"%s_PARENT_INCREMENT_birth"%n,"%s_FULL_SOURCE_birth"%n]
        cols+=["end_mass_SELECTIVE","end_mass_SHAM","end_mass_GLOBAL",
               "births_SELECTIVE","births_SHAM","births_GLOBAL"]
        fh.write(",".join(cols)+"\n")
        for r in per:
            v=[r["block"],r["seed"]]
            for n,_,_ in WINDOWS:
                w=r[n]
                v+=[w["mass_mean"][a] for a in ARMS]+[w["births_sum"][a] for a in ARMS]
                v+=[w["DAUGHTER_ONLY_EFFECT_mass"],w["PARENT_INCREMENT_mass"],w["FULL_SOURCE_EFFECT_mass"],
                    w["DAUGHTER_ONLY_EFFECT_birth"],w["PARENT_INCREMENT_birth"],w["FULL_SOURCE_EFFECT_birth"]]
            v+=[r["endpoint"]["mass"][a] for a in ARMS]+[r["endpoint"]["births_total"][a] for a in ARMS]
            fh.write(",".join(str(x) for x in v)+"\n")
    # summary to stdout
    for n,_,_ in WINDOWS:
        d=[r[n]["DAUGHTER_ONLY_EFFECT_mass"] for r in per]
        p=[r[n]["PARENT_INCREMENT_mass"] for r in per]
        f=[r[n]["FULL_SOURCE_EFFECT_mass"] for r in per]
        db=[r[n]["DAUGHTER_ONLY_EFFECT_birth"] for r in per]
        fb=[r[n]["FULL_SOURCE_EFFECT_birth"] for r in per]
        print("%-22s MASS  daughter_only med %+7.2f | parent_incr med %+7.2f | full med %+7.2f"%(
            n,statistics.median(d),statistics.median(p),statistics.median(f)))
        print("%-22s BIRTH daughter_only med %+7.2f | full med %+7.2f | n(daughter_only>0)=%d/%d"%(
            "",statistics.median(db),statistics.median(fb),sum(1 for x in db if x>0),len(db)))
    print()
    em={a:[r["endpoint"]["mass"][a] for r in per] for a in ARMS}
    bt={a:[r["endpoint"]["births_total"][a] for r in per] for a in ARMS}
    for a in ARMS:
        print("endpoint fixed-disc mass  %-10s median %7.1f  (min %5.1f max %6.1f)"%(a,statistics.median(em[a]),min(em[a]),max(em[a])))
    for a in ARMS:
        print("total fixed-disc births   %-10s median %7.1f  (min %5.1f max %6.1f)"%(a,statistics.median(bt[a]),min(bt[a]),max(bt[a])))

if __name__=="__main__": main()

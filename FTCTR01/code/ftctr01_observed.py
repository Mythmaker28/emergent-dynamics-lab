"""FTCTR01 part B-E — measurement over the existing PQEC01 / OBTC02 record. Zero new runs."""
from __future__ import annotations
import json, glob, math
import numpy as np
import yaml

REPO="/home/claude/edl"; RAW="/home/claude/PQEC01/raw"; OUT="/home/claude/FTCTR01/out"
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
CORE_R=float(P["analytic"]["core_radius_cells"]); MUX=float(P["point"]["muX"])
TAU_FROZEN=125.0
EX=json.load(open(f"{OUT}/FTCTR01_FIRST_PASSAGE.json"))

def _classify(nY,ncen,ok):                    # verbatim FLCR01 flcr01_science.py:81
    if not ok: return "F"
    if nY==0: return "E"
    if ncen>=3: return "P"
    if nY==1: return "O"
    return "S" if ncen==2 else "C"

rows=[]; holds=[]; NX_alive=[]
for lab in ("B1","B2"):
    for p in sorted(glob.glob(f"{RAW}/B_{lab}_*.npz")):
        z=np.load(p,allow_pickle=True); m=json.loads(str(z["meta"][0]))
        nm=[str(x) for x in z["scalar_names"]]; s=z["scalars"]
        nY=s[:,nm.index("N_Y")].astype(int); nc=s[:,nm.index("n_centres")].astype(int)
        NX=s[:,nm.index("N_X")].astype(float); mpd=s[:,nm.index("max_pair_dist")].astype(float)
        yb=z["ybirth"]; ok=m["stop"]!="INTEGRITY_FAILURE"
        seq=[_classify(a,b,ok or i<len(nY)-1) for i,(a,b) in enumerate(zip(nY,nc))]
        runs,cur=[],0
        for st in seq:
            if st=="S": cur+=1
            else:
                if cur: runs.append(cur)
                cur=0
        if cur: runs.append(cur)
        fb=int(yb[:,0].min()) if yb.size else -1
        first_S=next((i for i,st in enumerate(seq) if st=="S"),-1)
        first_P=next((i for i,st in enumerate(seq) if st=="P"),-1)
        first_cross=next((i for i in range(len(mpd)) if mpd[i]>CORE_R),-1)
        extinct = seq[-1]=="E"
        rows.append({"world":m["tag"],"point":lab,"stop":m["stop"],"steps":int(s.shape[0]),
            "first_birth":fb,"first_S":first_S,"first_P":first_P,"first_cross":first_cross,
            "sep_delay":(first_S-fb) if (fb>=0 and first_S>fb) else None,
            "cross_delay":(first_cross-fb) if (fb>=0 and first_cross>fb) else None,
            "reached_S":first_S>=0,"reached_P":first_P>=0,"extinct":bool(extinct),
            "P_after_S":bool(first_S>=0 and first_P>first_S),
            "max_hold":int(max(runs)) if runs else 0,"n_episodes":len(runs)})
        holds+=runs
        # stationary X only over worlds that still carry an organiser at the horizon
        if not extinct: NX_alive.append(float(np.mean(NX[len(NX)//2:])))

def st(a):
    a=np.array([x for x in a if x is not None],dtype=float)
    return {"n":int(a.size),"median":float(np.median(a)),"mean":float(a.mean()),
            "sd":float(a.std(ddof=1)),"sem":float(a.std(ddof=1)/math.sqrt(a.size)),
            "min":float(a.min()),"max":float(a.max())} if a.size else None

SEP=st([r["sep_delay"] for r in rows]); CRO=st([r["cross_delay"] for r in rows])
E=EX["E_tau"]
zof=lambda o:(o["mean"]-E)/o["sem"] if o else None

# ---------------- X maturation: reported AS A FUNCTION OF THE RESPONSE FRACTION ----------
efold=-1.0/math.log(1.0-MUX)
R=json.load(open(f"{REPO}/OBTC02/out/_results.json"))
lev=[a["pre_removal_level"] for a in R["cross_arm"]["CAUSAL_SOURCE_DEPENDENCE"]["R_arms"]]
H_HOLD=float(np.median(holds))
t_of_f=lambda f: math.log(1.0-f)/math.log(1.0-MUX)
frac_in=lambda t: 1.0-(1.0-MUX)**t
GRID=[0.5,1-1/math.e,0.8,0.9,0.95,0.99]
CURVE=[{"response_fraction":f,"steps_from_empty":t_of_f(f),
        "shortfall_factor_vs_H_HOLD":t_of_f(f)/H_HOLD} for f in GRID]

MAT={"e_folding_steps_exact":efold,
 "frozen_e_folding":float(P["analytic"]["source_off_e_folding_steps"]),
 "e_folding_matches_frozen":abs(efold-float(P["analytic"]["source_off_e_folding_steps"]))<1e-9,
 "one_over_muX":1.0/MUX,
 "BUILD_UP_LAW":"N_X(t) = N_inf (1 - (1-muX)^t); t(f) = ln(1-f)/ln(1-muX). The response fraction f MUST be chosen explicitly; one e-folding is f = 1 - 1/e = %.10f, NOT full maturation."%(1-1/math.e),
 "MATURATION_TIME_VS_RESPONSE_FRACTION":CURVE,
 "historical_101_binding":{"source":"OBTC02/out/_results.json cross_arm.CAUSAL_SOURCE_DEPENDENCE.R_arms",
   "all_R_arm_pre_removal_levels":lev,"n_arms":len(lev),
   "mean":float(np.mean(lev)),"sd":float(np.std(lev,ddof=1)),
   "min":float(min(lev)),"max":float(max(lev)),
   "the_value_101_14_is":"ONE arm (R/seed9302), not a derived threshold",
   "AUDIT":"NOT_DEFENSIBLE_AS_A_THRESHOLD__IT_IS_A_SINGLE_ARM_OBSERVATION"},
 "N_X_stationary_non_extinct_worlds":float(np.mean(NX_alive)),
 "N_X_stationary_n_worlds":len(NX_alive),
 "N_X_stationary_sd":float(np.std(NX_alive,ddof=1)),
 "N_X_stationary_note":"late-window mean over worlds NOT extinct at the horizon; extinct worlds drive N_X to 0 and were excluded because the quantity wanted is the level an organiser SUSTAINS",
 "H_HOLD_observed_median_S_run":H_HOLD,
 "H_HOLD_provenance":"median of an OBSERVED distribution of S-runs, NOT a derived requirement",
 "n_S_episodes":len(holds),
 "hold_mean":float(np.mean(holds)),"hold_q90":float(np.quantile(holds,.9)),"hold_max":int(max(holds)),
 "fraction_of_cloud_built_in_H_HOLD_steps":frac_in(H_HOLD),
 "MIN_SHORTFALL_FACTOR_over_grid":min(c["shortfall_factor_vs_H_HOLD"] for c in CURVE),
 "P_hold_ge_one_e_folding":float(np.mean([h>=efold for h in holds])),
 "P_hold_ge_TAU_FROZEN":float(np.mean([h>=TAU_FROZEN for h in holds])),
 "P_hold_ge_E_tau":float(np.mean([h>=E for h in holds]))}

nS=sum(r["reached_S"] for r in rows); nPS=sum(r["P_after_S"] for r in rows)
OBS={"N_WORLDS":len(rows),"UNIT":"one world",
 "SEPARATION_DELAY_first_S_minus_first_birth":SEP,"z_sep_vs_exact":zof(SEP),
 "CROSSING_DELAY_max_pair_dist_gt_CORE_R":CRO,"z_cross_vs_exact":zof(CRO),
 "EXACT_E_tau":E,
 "THIRD_CENTRE":{"worlds_reaching_S":nS,"of_which_later_reach_P":nPS,
   "fraction":nPS/nS if nS else None},
 "MATURATION":MAT,"PER_WORLD":rows}
json.dump(OBS,open(f"{OUT}/FTCTR01_SEPARATION_VS_MATURATION.json","w"),indent=2)
print(json.dumps({"z_sep":OBS["z_sep_vs_exact"],"z_cross":OBS["z_cross_vs_exact"],
 "SEP":SEP,"THIRD":OBS["THIRD_CENTRE"],
 "NX_inf_alive":MAT["N_X_stationary_non_extinct_worlds"],"n_alive":MAT["N_X_stationary_n_worlds"],
 "H_HOLD":H_HOLD,"CURVE":CURVE,"MIN_SHORTFALL":MAT["MIN_SHORTFALL_FACTOR_over_grid"],
 "frac_in_H_HOLD":MAT["fraction_of_cloud_built_in_H_HOLD_steps"],
 "P_hold_ge_efold":MAT["P_hold_ge_one_e_folding"],"R_levels":lev},indent=2))

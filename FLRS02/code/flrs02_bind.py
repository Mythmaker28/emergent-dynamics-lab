"""FLRS02 §1 — bind the scientific parent and the timescale by bytes.

Every FTCTR01 headline quantity is RECOMPUTED here by an implementation that is
independent of the FTCTR01 code (grid propagation with np.roll instead of a sparse
absorbing-chain matrix). The FTCTR01 numbers are treated as clues, not inputs.
"""
from __future__ import annotations
import hashlib, json, math, os, glob, subprocess, datetime
import numpy as np, yaml

REPO="/home/claude/edl"; RAWP="/home/claude/PQEC01/raw"; OUT=f"{REPO}/FLRS02/out"
sha=lambda p: hashlib.sha256(open(p,'rb').read()).hexdigest()

# ------------------------------- §1a parent binding -------------------------------
def bind_tree(prog, sub=("code",)):
    rows=[]
    for s in sub:
        d=os.path.join(REPO,prog,s)
        if not os.path.isdir(d): continue
        for root,dirs,files in os.walk(d):
            dirs[:]=[x for x in dirs if x!="__pycache__"]
            for f in sorted(files):
                if f.endswith((".pyc",)): continue
                p=os.path.join(root,f)
                rows.append({"path":os.path.relpath(p,REPO),"bytes":os.path.getsize(p),"sha256":sha(p)})
    return rows

PROGS=["ORR01","OBTC02","OBFOR01","PQEC01","FLCR01","FTCTR01"]
PB={"BINDING":"FLRS02 §1 — parent binding, verified by bytes",
    "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "REPO":REPO,
    "PARENT_PROGRAMME":"FOUNDER-VERSUS-LINEAGE-CONTINUITY-RECONCILIATION-01",
    "LAST_VALID_PARENT_TIP":"06c592313df96601de8d2a89676d5a5cf79fc414",
    "PROGRAMMES":{}}
for p in PROGS:
    code=bind_tree(p,("code",)); out=bind_tree(p,("out",))
    PB["PROGRAMMES"][p]={"code_files":len(code),"out_files":len(out),
      "code_sha256_of_sorted_list":hashlib.sha256(
        "\n".join("%s %s"%(r["sha256"],r["path"]) for r in sorted(code,key=lambda r:r["path"])).encode()).hexdigest(),
      "code":code}
# raw archives
raws=sorted(glob.glob(f"{RAWP}/*.npz"))
PB["PQEC01_RAW"]={"n_archives":len(raws),"dir":RAWP,
  "by_point":{k:len([r for r in raws if os.path.basename(r).startswith(k)]) for k in ("A_A0","B_B1","B_B2")}}
# engine identity
K=f"{REPO}/MCM01/code/kinetics.py"
PB["FROZEN_ENGINE"]={"file":"MCM01/code/kinetics.py","sha256":sha(K),
  "expected_from_OBFOR01_METHODS_CORE":"d6b9e24daefd9a9ddd42780fa24da444a344a2773bb7836a8e168e44f026c4c4",
  "MATCH":sha(K)=="d6b9e24daefd9a9ddd42780fa24da444a344a2773bb7836a8e168e44f026c4c4"}
PB["LOST_PROGRAMMES_TREATED_AS_DOCUMENTARY_WARNINGS_ONLY"]={
  p:("ABSENT_FROM_REPOSITORY" if not os.path.isdir(os.path.join(REPO,p)) else "PRESENT")
  for p in ("CLOC02","RSLOC03","RIRA01")}
PB["LOST_PROGRAMME_NUMBERS_AS_DATA"]="forbidden — no numerical output of CLOC02/RSLOC03/RIRA01 enters any estimator in FLRS02"
json.dump(PB,open(f"{OUT}/FLRS02_PARENT_BINDING.json","w"),indent=2)

# --------------------- §1b timescale binding, INDEPENDENT recompute ---------------
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L=int(P["point"]["L"]); P_HOP=float(P["point"]["p_hop"]); MUX=float(P["point"]["muX"])
A_X=float(P["analytic"]["a_X"]); D_REL=float(P["analytic"]["D_relative"])
CORE_R=float(P["analytic"]["core_radius_cells"]); TAU_FROZEN=125.0

q=P_HOP/4.0
P1={+1:q*(1-q), -1:q*(1-q), 0:q*q+(1-q)**2}
PREL={}
for a,pa in P1.items():
    for b,pb in P1.items(): PREL[a-b]=PREL.get(a-b,0.0)+pa*pb

# INDEPENDENT METHOD C: propagate the full L x L probability grid with np.roll,
# zeroing absorbed mass each step. No sparse matrix, no state indexing.
ii=np.arange(L); mi=np.minimum(ii,L-ii)
DIST=np.sqrt(mi[:,None]**2+mi[None,:]**2)
ALIVE=(DIST<=CORE_R)
g=np.zeros((L,L)); g[0,0]=1.0
surv=[]; t=0
while True:
    s=float(g.sum()); surv.append(s)
    if s<1e-18 or t>600000: break
    ng=np.zeros_like(g)
    for dy,py in PREL.items():
        for dx,px in PREL.items():
            w=py*px
            if w>0: ng+=w*np.roll(np.roll(g,dy,axis=0),dx,axis=1)
    g=ng*ALIVE; t+=1
S=np.array(surv); tt=np.arange(len(S))
E_C=float(S.sum()); E2_C=float(((2*tt+1)*S).sum()); SD_C=math.sqrt(E2_C-E_C*E_C)
pmf=-np.diff(S); cdf=np.cumsum(pmf); supp=np.arange(1,len(pmf)+1)
qt=lambda p: float(supp[np.searchsorted(cdf,p)])

var_axis=sum(k*k*v for k,v in P1.items()); var_rel=sum(k*k*v for k,v in PREL.items())

# X response timing, recomputed
efold=-1.0/math.log(1.0-MUX)
t_of_f=lambda f: math.log(1.0-f)/math.log(1.0-MUX)
f_at   =lambda t: 1.0-(1.0-MUX)**t
FRACS={"f_50":0.50,"f_primary_1_minus_1_over_e":1.0-1.0/math.e,"f_80":0.80,"f_90":0.90}

# historical 101 provenance, recomputed from source
R=json.load(open(f"{REPO}/OBTC02/out/_results.json"))
arms=R["cross_arm"]["CAUSAL_SOURCE_DEPENDENCE"]["R_arms"]
lev=[a["pre_removal_level"] for a in arms]; tags=[a["tag"] for a in arms]

TB={"BINDING":"FLRS02 §1 — timescale binding; every quantity recomputed independently",
 "GENERATED_UTC":PB["GENERATED_UTC"],
 "INDEPENDENCE_STATEMENT":("the first-passage law is recomputed by grid propagation with np.roll and "
   "absorbing-mask zeroing. It shares no calculation code with FTCTR01's sparse absorbing-chain "
   "implementation; only the frozen protocol constants are shared."),
 "FROZEN_CONSTANTS_READ_FROM":"OBTC02/code/obtc02_protocol.yaml",
 "L":L,"p_hop":P_HOP,"muX":MUX,"CORE_R":CORE_R,"TAU_SEP_frozen":TAU_FROZEN,
 "KINETIC_CHECK":{"variance_one_axis_one_step":var_axis,"frozen_a_X":A_X,
   "MATCH":abs(var_axis-A_X)<1e-12,
   "D_relative_derived":var_rel/2.0,"frozen_D_relative":D_REL,
   "MATCH_D":abs(var_rel/2.0-D_REL)<1e-12},
 "GEOMETRIC_FIRST_PASSAGE":{
   "absorbing_rule":"toroidal min-image distance > CORE_R",
   "method_C_grid_propagation_mean":E_C,"method_C_sd":SD_C,
   "median":qt(0.5),"q25":qt(0.25),"q75":qt(0.75),
   "steps_until_mass_exhausted":len(S),
   "TAU_SEP_frozen":TAU_FROZEN,"ratio_exact_over_frozen":E_C/TAU_FROZEN,
   "frozen_understates_by_percent_of_frozen":100.0*(E_C-TAU_FROZEN)/TAU_FROZEN},
 "X_RESPONSE_TIMING":{
   "decay_law":"N_X(t) = N_X(0) (1-muX)^t   [OBTC02 source_operator.py]",
   "build_law":"N_X(t) = N_inf (1 - (1-muX)^t)",
   "e_folding_steps":efold,
   "frozen_e_folding":float(P["analytic"]["source_off_e_folding_steps"]),
   "MATCH":abs(efold-float(P["analytic"]["source_off_e_folding_steps"]))<1e-9,
   "one_over_muX":1.0/MUX,
   "response_fraction_after_16_steps":f_at(16.0),
   "T":{k:t_of_f(v) for k,v in FRACS.items()},
   "FRACTIONS":FRACS},
 "HISTORICAL_101_PROVENANCE":{
   "source":"OBTC02/out/_results.json :: cross_arm.CAUSAL_SOURCE_DEPENDENCE.R_arms[*].pre_removal_level",
   "arm_tags":tags,"arm_levels":lev,"n_arms":len(lev),
   "mean":float(np.mean(lev)),"sd":float(np.std(lev,ddof=1)),
   "the_value_101_14_is":"the pre_removal_level of ONE arm (%s)"%tags[lev.index(101.14)] if 101.14 in lev else None,
   "VERDICT":"NOT_A_DERIVED_THRESHOLD__SINGLE_ARM_OBSERVATION__RETIRED"},
 "RETIRED":{"H_HOLD_16":"retired as a functional maturity criterion (FLRS02 §2)",
            "X_BIRTHS_101":"retired as a qualified threshold (FLRS02 §2)"}}
json.dump(TB,open(f"{OUT}/FLRS02_TIMESCALE_BINDING.json","w"),indent=2)
print(json.dumps({"engine_match":PB["FROZEN_ENGINE"]["MATCH"],
 "raw":PB["PQEC01_RAW"]["by_point"],"lost":PB["LOST_PROGRAMMES_TREATED_AS_DOCUMENTARY_WARNINGS_ONLY"],
 "kin":TB["KINETIC_CHECK"],"fp":TB["GEOMETRIC_FIRST_PASSAGE"],
 "T":TB["X_RESPONSE_TIMING"]["T"],"f16":TB["X_RESPONSE_TIMING"]["response_fraction_after_16_steps"],
 "efold_match":TB["X_RESPONSE_TIMING"]["MATCH"],"101":TB["HISTORICAL_101_PROVENANCE"]["arm_levels"]},indent=2))

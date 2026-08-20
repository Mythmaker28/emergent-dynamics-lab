"""FLRS02 §3 + §4 — freeze the functional criterion BEFORE any lineage outcome is inspected.

The primary maturation timescale is adopted ONLY if the exact linear operator of the X
field shows that the population mode is the slowest relaxation mode of the functional
observable. That is demonstrated here by computing the full spectrum, not asserted.
"""
from __future__ import annotations
import json, math, datetime
import numpy as np, yaml

REPO="/home/claude/edl"; OUT=f"{REPO}/FLRS02/out"
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
L=int(P["point"]["L"]); P_HOP=float(P["point"]["p_hop"]); MUX=float(P["point"]["muX"])
CORE_R=float(P["analytic"]["core_radius_cells"]); CAP=int(P["point"]["CAP"])

# ---- exact spectrum of the per-step X operator  n -> (1-muX) * Hop(n) ----------------
q=P_HOP/4.0
P1={+1:q*(1-q), -1:q*(1-q), 0:q*q+(1-q)**2}
k=2.0*np.pi*np.arange(L)/L
phi=P1[0]+2.0*P1[1]*np.cos(k)                      # per-axis characteristic function
EIG=(1.0-MUX)*phi[:,None]*phi[None,:]              # 2D separable hop x uniform decay
RATE=-np.log(np.clip(EIG,1e-300,None))             # per-step decay rate of each mode
i0=(0,0)
slowest=float(RATE.min()); arg=np.unravel_index(int(np.argmin(RATE)),RATE.shape)
rate_k0=float(RATE[i0])
nonzero=RATE.copy(); nonzero[i0]=np.inf
second=float(nonzero.min()); arg2=np.unravel_index(int(np.argmin(nonzero)),nonzero.shape)
mu_rate=-math.log(1.0-MUX)

SPEC={"operator":"n -> (1-muX) * Hop(n); Hop is the engine's four ordered sub-shifts, separable per axis",
 "n_modes":int(L*L),
 "slowest_mode_index":[int(a) for a in arg],
 "slowest_rate_per_step":slowest,
 "k0_mode_rate_per_step":rate_k0,
 "minus_log_1_minus_muX":mu_rate,
 "SLOWEST_MODE_IS_THE_POPULATION_MODE":bool(arg==(0,0)),
 "K0_RATE_EQUALS_MU_RATE":bool(abs(rate_k0-mu_rate)<1e-14),
 "second_slowest_mode_index":[int(a) for a in arg2],
 "second_slowest_rate_per_step":second,
 "second_slowest_e_folding_steps":1.0/second,
 "spectral_gap_ratio_second_over_first":second/rate_k0,
 "INTERPRETATION":("every spatial mode decays strictly faster than the uniform population mode, so the "
   "long-time relaxation of ANY positive local X functional is governed by muX. The population "
   "e-folding is therefore the correct primary relaxation mode for the functional observable.")}

efold=1.0/mu_rate
t_of_f=lambda f: math.log(1.0-f)/math.log(1.0-MUX)
f_at  =lambda t: 1.0-(1.0-MUX)**t
F_PRIMARY=1.0-1.0/math.e
BAND={"T_50":t_of_f(0.50),"T_primary":t_of_f(F_PRIMARY),"T_80":t_of_f(0.80),"T_90":t_of_f(0.90)}

C={"SECTION":"FLRS02 §3 + §4 — functional criterion, frozen before any lineage outcome",
 "GENERATED_UTC":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "FROZEN_BEFORE_OUTCOME_ACCESS":True,
 "TWO_LEVELS":{
   "SOURCE_FUNCTION_ONSET":{"definition":"the step at which a spatial centre first sustains a local X source, i.e. the centre carries at least one Y and a non-empty accepted-birth candidate pool",
     "observable":"ycells candY > 0 at a cell belonging to the centre","timescale":"immediate — an event, not a relaxation"},
   "PROFILE_MATURATION":{"definition":"the step at which the centre's local X cloud has relaxed to the chosen fraction f of the level it would sustain",
     "observable":"local X mass within CORE_R of the centre","governing_rate":"muX, established as the slowest mode above",
     "law":"N_X(t) = N_inf (1 - (1-muX)^t)  =>  T(f) = ln(1-f)/ln(1-muX)"}},
 "SPECTRUM_DEMONSTRATION":SPEC,
 "PRIMARY_FUNCTIONAL_CRITERION":{
   "f_primary":F_PRIMARY,"T_primary_steps":BAND["T_primary"],
   "justification":"one e-folding of the slowest — and therefore governing — relaxation mode of the X field",
   "ADOPTED_BECAUSE_THE_SPECTRUM_DEMONSTRATES_IT":bool(arg==(0,0))},
 "MANDATORY_SENSITIVITY_BAND":{"T_50":BAND["T_50"],"T_primary":BAND["T_primary"],
   "T_80":BAND["T_80"],"T_90":BAND["T_90"],
   "purpose":"determine whether the route decision depends critically on one arbitrary response fraction"},
 "RETIRED_CRITERIA":{
   "H_HOLD_16":{"status":"RETIRED","response_fraction_it_actually_delivered":f_at(16.0),
     "reason":"it was the median of an observed S-run distribution, never a derived maturity requirement"},
   "X_BIRTHS_101":{"status":"RETIRED","reason":"the pre_removal_level of one OBTC02 arm, not a derived threshold"},
   "REHABILITATION_RULE":"neither may be reinstated because it yields a favourable historical outcome"},
 "LINEAGE_EVENT_DEFINITION":{
   "STATES":{"E":"no Y","O":"one organising centre","C":"multiple Y but one spatial centre",
             "S":"exactly two spatial centres","P":"three or more spatial centres",
             "F":"X/source integrity failure"},
   "CENTRE_RULE":"toroidal single-linkage over Y-occupied cells with adjacency distance <= CORE_R (%.1f)"%CORE_R,
   "FOUNDER_IDENTITY":"irrelevant — no genealogy is constructed or required",
   "FUNCTIONAL_TWO_CENTRE_SUCCESS_REQUIRES_ALL_OF":[
     "1. at least one dynamic Y birth occurs",
     "2. the lineage does not go extinct before functional maturation",
     "3. exactly two spatial centres form under the frozen centre classifier",
     "4. both centres remain spatially distinct for at least T(f) consecutive steps",
     "5. both centres exhibit the required local X response",
     "6. no third centre appears BEFORE the functional maturation event",
     "7. X/source integrity remains acceptable until that event"],
   "EXPLICITLY_NOT_REQUIRED":["survival of the original founder particle",
                              "old C1/C2/C3 formulas as substitutes for directly recorded events"]},
 "UNIT":"one world; steps and episodes are NEVER independent replicates"}
json.dump(C,open(f"{OUT}/FLRS02_FUNCTIONAL_CRITERION.json","w"),indent=2)
print(json.dumps({"SLOWEST_IS_K0":SPEC["SLOWEST_MODE_IS_THE_POPULATION_MODE"],
 "K0_RATE_EQUALS_MU":SPEC["K0_RATE_EQUALS_MU_RATE"],
 "second_slowest_efold":SPEC["second_slowest_e_folding_steps"],
 "gap_ratio":SPEC["spectral_gap_ratio_second_over_first"],
 "T":BAND,"f_at_16":f_at(16.0),"efold":efold},indent=2))

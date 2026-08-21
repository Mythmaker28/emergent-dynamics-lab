"""RCD01 §5 — the material-turnover criterion, DERIVED FROM PHYSICS BEFORE ANY PREVALENCE
IS EVALUATED. No arbitrary percentage is chosen.

Physics. X decay is applied in engine_obtc._decay_core as rng.binomial(n["X"], muX), i.e.
each X molecule independently dies with probability muX at every step. Therefore a molecule
alive at time t0 is still alive at t0 + D with probability exactly (1 - muX)^D, and the number
of survivors among N molecules is Binomial(N, (1 - muX)^D).

Consequence. Let t0 be the step at which the two centres first become spatially distinct and
t_m = t0 + T_PRIMARY_STEPS - 1 the frozen functional maturation event. Let N0 = total X in the
world at t0 and let Dm = the daughter candidate's local X mass within CORE_R at t_m. Every
molecule counted in Dm either survived from t0 or was born after t0. Hence

    new material in Dm  >=  Dm - (number of pre-separation survivors ANYWHERE at t_m)

and the survivor count is stochastically bounded above by the exact binomial quantile. The
bound is deliberately generous: it credits the daughter with EVERY surviving old molecule in
the whole world, including those still held by the parent, which is physically impossible.

CRITERION R1 (material reconstruction), threshold-free:
    R1 holds for a world iff  Dm  >  Q_{0.95}( Binomial(N0, (1 - muX)^(T_PRIMARY_STEPS-1)) )
i.e. the daughter's cloud is larger than the certified upper bound on ALL surviving
pre-separation material. When that holds, the daughter's cloud cannot be accounted for by
redistributed old material, whatever the transport did.

Reported alongside: the certified lower bound on the NEW fraction of the daughter's cloud,
    f_new_lower = (Dm - S_upper) / Dm .
"""
from __future__ import annotations
import json, math, sys, os
import yaml
from scipy.stats import binom
REPO="/home/claude/edl"
P=yaml.safe_load(open(f"{REPO}/OBTC02/code/obtc02_protocol.yaml"))
MUX=float(P["point"]["muX"]); CORE_R=float(P["analytic"]["core_radius_cells"])
sys.path.insert(0,f"{REPO}/FDFLT01/code")
import fdflt01_endpoint as E
DELTA=E.STEPS["T_primary"]-1                 # steps elapsed from t0 to the maturation event
SURV=(1.0-MUX)**DELTA
CONF=0.95
def survivor_upper(N0,conf=CONF):
    """Exact binomial upper quantile on the number of pre-separation molecules still alive."""
    if N0<=0: return 0
    return int(binom.ppf(conf,N0,SURV))
def r1_holds(Dm,N0): return Dm>survivor_upper(N0)
def f_new_lower(Dm,N0):
    if Dm<=0: return None
    return max(0.0,(Dm-survivor_upper(N0))/Dm)

if __name__=="__main__":
    J={"SECTION":"RCD01 §5 — material-turnover criterion, derived before any prevalence count",
     "muX":MUX,"T_PRIMARY_STEPS":E.STEPS["T_primary"],"DELTA_STEPS_t0_TO_MATURATION":DELTA,
     "PER_MOLECULE_SURVIVAL_OVER_DELTA":SURV,
     "SURVIVAL_LAW":"(1 - muX)^DELTA, exact, from rng.binomial(n[X], muX) applied every step",
     "SURVIVOR_COUNT_LAW":"Binomial(N0, (1-muX)^DELTA)",
     "CONFIDENCE_FOR_THE_UPPER_BOUND":CONF,
     "CRITERION_R1":"Dm > Q_0.95( Binomial(N0, (1-muX)^DELTA) )",
     "WHY_THRESHOLD_FREE":("no percentage is chosen. The comparison is between the daughter's "
        "measured cloud and the certified upper bound on the total surviving pre-separation "
        "material in the entire world."),
     "WHY_CONSERVATIVE":("the bound credits the daughter with every surviving old molecule "
        "anywhere, including those still held by the parent. A world that passes therefore "
        "passes by a margin larger than the one computed."),
     "WORKED_EXAMPLES":[{"N0":n0,"survivor_upper_95":survivor_upper(n0),
                         "daughter_mass_needed_to_pass":survivor_upper(n0)+1} for n0 in (50,100,150,200,250)],
     "EXACT_PROVENANCE_NOTE":("the engine carries a molecular Tracker (engine_obtc.Tracker) that "
        "records id, birth_step and birth cell for every X molecule and draws from its own "
        "generator. Its state was NOT written to the PQEC01/FDFLT01 archives, so exact per-molecule "
        "provenance is NOT recoverable from the raw data alone. It IS recoverable by deterministic "
        "replay of a seed, which RCD01 may not perform because NEW_WORLD_CONSTRUCTIONS = 0."),
     "CLASSIFICATION_FROM_ARCHIVES_ALONE":"CERTIFIED_LOWER_BOUND_ON_NEW_MATERIAL"}
    json.dump(J,open(f"{REPO}/RCD01/out/RCD01_MATERIAL_PROVENANCE_CRITERION.json","w"),indent=2)
    print(json.dumps(J,indent=2))

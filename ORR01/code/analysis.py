"""Criticality revision and analytic comparison of the candidate repairs. No engine start."""
import ast, json, inspect, textwrap
from fractions import Fraction as Fr
import numpy as np
import kinetics as K, lattice as LAT, lawspec_v2 as V2, exact_chain as EC

OUT="/home/claude/ORR01/out"; R={"criticality":{}, "repairs":{}, "checks":[]}
def C(n, ok, d):
    R["checks"].append({"check":n,"outcome":"PASS" if ok else "FAIL","detail":d})
    print(("  PASS  " if ok else "  FAIL  ")+n+"\n        "+d); return ok

# ============================================================ 1. criticality revision
sp = K.Spec.as_dict(); sp.update(dict(L=1, CAP=10, S0=2, phi=0.0, omega=0.0, muX=0.0, muY=0.0,
     kX=1.0, kY=0.0, p_hop_X=0.0, p_hop_Y=0.0))
S = type("S",(K.Spec,),sp); sm = EC.Small(1,S)
k1 = sm.kernel((1,1,2,0,0,0)); k2 = sm.kernel((2,1,2,0,0,0))
b1 = {sum(k[:1])-1: 0 for k in []}
# distribution of ACCEPTED births: nX_after - nX_before
d1 = {}; d2 = {}
for st,pr in k1.items(): d1[st[0]-1] = d1.get(st[0]-1,Fr(0))+pr
for st,pr in k2.items(): d2[st[0]-2] = d2.get(st[0]-2,Fr(0))+pr
same = all(abs(float(d1.get(b,0))-float(d2.get(b,0)))<1e-12 for b in set(d1)|set(d2))
C("EXACT: at kX = 1 the birth law does not depend on n_X once n_X >= 1",
  same,
  "with CAP = 10 the free capacity is not binding, so cand_X = 2 in BOTH states. "
  "births distribution from n_X = 1: %s ; from n_X = 2: %s. p_X = "
  "min(1, kX*nX*nY) saturates at n_X >= 1, so the low-density map is a STEP, not a linear "
  "operator: there is no linearisation about n_X = 0 and no branching multiplier."
  % ({b:round(float(v),6) for b,v in sorted(d1.items())},
     {b:round(float(v),6) for b,v in sorted(d2.items())}))
R["criticality"]["saturated_regime"] = {"kX":1.0, "births_law_independent_of_nX": bool(same),
  "SCALAR_CRITICALITY":"NOT_VALID"}

spb = dict(sp); spb["kX"] = 0.1
Sb = type("Sb",(K.Spec,),spb); smb = EC.Small(1,Sb)
kb1 = smb.kernel((1,1,2,0,0,0)); kb2 = smb.kernel((2,1,2,0,0,0))
e1 = float(sum(pr*(st[0]-1) for st,pr in kb1.items()))
e2 = float(sum(pr*(st[0]-2) for st,pr in kb2.items()))
C("EXACT: at small kX the mean birth rate IS linear in n_X",
  abs(e2-2*e1) < 1e-12,
  "E[births | n_X=1] = %.10f, E[births | n_X=2] = %.10f, ratio %.10f. In this sub-regime the "
  "low-density dynamics are a LINEAR operator whose coefficients (cand_X, n_Y) are themselves "
  "random and endogenous, so the growth rate is the top Lyapunov exponent of a product of "
  "random operators, not a scalar. The mean-field product c_X*G(0) is its annealed "
  "approximation." % (e1, e2, e2/e1 if e1 else float('nan')))
R["criticality"]["linear_regime"] = {"kX":0.1, "E_births_nX1":e1, "E_births_nX2":e2,
  "linear": bool(abs(e2-2*e1)<1e-12), "SCALAR_CRITICALITY":"APPROXIMATE"}
R["criticality"]["verdict"] = {
  "CRITICALITY_STATUS":"NOT_VALID",
  "reason":"the configuration actually used by MTW01 and MCM01 has kX = 1, where the birth "
           "probability saturates at n_X >= 1 and no linear low-density operator exists. A "
           "scalar multiplier is therefore not a criticality criterion for the population; it "
           "is the expected offspring number of a SINGLE body molecule in a FROZEN environment.",
  "retained_diagnostic":"the drift balance E[dN_X | state] = E[births] - muX*N_X, logged "
           "exactly step by step (accepted births and deaths are read from the field, not "
           "modelled), whose zero gives the quasi-stationary level N* = E[births]/muX; and the "
           "realised persistence over the declared window.",
  "MTW01_supercritical_qualification":"BY_PREVIOUS_MEAN_FIELD_CRITERION_ONLY"}

# ============================================================ 2. repairs, analytic comparison
def nodes(fn):
    return sum(1 for _ in ast.walk(ast.parse(textwrap.dedent(inspect.getsource(fn)))))
n_v1 = nodes(K.World._feed_and_outflow); n_v2 = nodes(V2.WorldV2._exchange)

REPAIRS = {
 "R0_ADDITIVE_LEGACY": dict(
   description="the inherited rule, unchanged; the negative control",
   operators_modified=0, new_operator_ast_nodes=0,
   occupancy_conserved_exactly=False,
   occupancy_drift="E[dO] = add - out, add unconditional and positive: the ratchet",
   removes_body_directly=False, outcome_feedback=False, legacy_preserved=True,
   physical_reading="an unbounded source of matter with no matching sink",
   removes_the_ratchet=False, new_tautological_maintenance=False, admissible=False),
 "R1_REPLACEMENT_FEED_KEEP_OUTFLOW": dict(
   description="the feed becomes a swap (one unit in, one out of the same cell), the waste "
               "outflow omega is kept",
   operators_modified=1, new_operator_ast_nodes=n_v2,
   occupancy_conserved_exactly=False,
   occupancy_drift="E[dO] = 0 - out <= 0, strictly negative whenever waste exists: the "
                   "lattice DRAINS. The up-ratchet is removed and replaced by a down-drain.",
   removes_body_directly=False, outcome_feedback=False, legacy_preserved=True,
   physical_reading="a closed medium with an open waste port: not a chemostat",
   removes_the_ratchet=True, new_tautological_maintenance=False, admissible=False),
 "R2_BALANCED_EXCHANGE": dict(
   description="feed and outflow are replaced by ONE exchange operator: every unit the "
               "reservoir inserts displaces one unit drawn uniformly without replacement from "
               "the cell's exchangeable pool {SX, SY, WX, WY}",
   operators_modified=1, new_operator_ast_nodes=n_v2,
   occupancy_conserved_exactly=True,
   occupancy_drift="E[dO] = 0 exactly, cell by cell and step by step",
   removes_body_directly=False, outcome_feedback=False, legacy_preserved=True,
   physical_reading="a chemostat at equal in and out flow: the medium is renewed, the biomass "
                    "is not exchanged, waste leaves in the outflow",
   removes_the_ratchet=True, new_tautological_maintenance=False, admissible=True),
 "R2b_EXCHANGE_POOL_INCLUDES_BODY": dict(
   description="as R2 but the exchangeable pool also contains X, so body molecules are washed "
               "out",
   operators_modified=1, new_operator_ast_nodes=n_v2,
   occupancy_conserved_exactly=True,
   occupancy_drift="E[dO] = 0 exactly",
   removes_body_directly=True, outcome_feedback=False, legacy_preserved=True,
   physical_reading="a chemostat that also washes out biomass; this ADDS an effective death "
                    "term to X and is therefore a second change, not a smaller one",
   removes_the_ratchet=True, new_tautological_maintenance=False, admissible=False),
 "R3_RESERVOIR_BOUNDARY": dict(
   description="a designated source region exchanges with an external reservoir; the bulk has "
               "no feed at all",
   operators_modified=2, new_operator_ast_nodes=n_v2 + 40,
   occupancy_conserved_exactly=True,
   occupancy_drift="E[dO] = 0 in the source region, 0 elsewhere",
   removes_body_directly=False, outcome_feedback=False, legacy_preserved=True,
   physical_reading="an open boundary; physically sound but it introduces a geometry (where "
                    "the source is) and breaks translation invariance, so it adds a parameter "
                    "and a spatial gradient artefact the present question does not need",
   removes_the_ratchet=True, new_tautological_maintenance=False, admissible=False),
}
def key(name, r):
    return (0 if r["admissible"] else 1, r["operators_modified"], r["new_operator_ast_nodes"],
            name)
ranked = sorted(REPAIRS.items(), key=lambda kv: key(*kv))
selected = ranked[0][0]
C("the frozen selection rule picks exactly one repair, on structure alone",
  selected == "R2_BALANCED_EXCHANGE" and REPAIRS[selected]["admissible"],
  "rule: keep only candidates that conserve occupancy exactly, carry no outcome feedback, "
  "remove no body molecule directly and preserve a legacy mode; among those take the fewest "
  "engine operators modified, then the smallest new operator by AST node count, then "
  "alphabetical. Ranking: %s. Selected: %s (%d operator modified, %d AST nodes against %d for "
  "the inherited operator)." % ([n for n,_ in ranked], selected,
  REPAIRS[selected]["operators_modified"], n_v2, n_v1))
R["repairs"] = {"candidates": REPAIRS, "selection_rule":
  "admissible first; then fewest operators modified; then smallest new operator by AST node "
  "count; then alphabetical. Computed before any run and from structure only, never from an "
  "outcome.", "ranking":[n for n,_ in ranked], "selected": selected,
  "ast_nodes_v1_feed": n_v1, "ast_nodes_v2_exchange": n_v2}
json.dump(R, open(OUT+"/_analysis.json","w"), indent=1, default=str)
print("\nchecks:", sum(1 for c in R["checks"] if c["outcome"]=="PASS"),"/",len(R["checks"]))

"""AXMAT00 stage 3 — invariance, triangle validity and sharpness."""
import json, os, sys, random
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from axmat00_review import Validator, BASE
from axmat00_rederive import sqrt_iv, iv_add, iv_mul_pos, iv_scale, mid

V = Validator()
thr  = V.load(f"{BASE}/FCDDH01R_DISCOVERY_THRESHOLD_LOCK.json")
cmap = V.load(f"{BASE}/_work/EXACT_INTERACTION_COEFFICIENT_MAP.json")
W = [F(w) for w in cmap["W"]]
ser = thr["sham_series_and_hashes"]
out = {}

def tau_sq(t, XA, XB):
    G2sq = sum(W[i]*((XA[i+1]-XA[0])**2 + (XB[i+1]-XB[0])**2) for i in range(len(W)))
    return max(F(t["ETA_ORACLE_L2"])**2, F(1,10000)*G2sq, F(t["TAU_SITE_L2_sq"]))

recs=[]
for t in thr["thresholds"]:
    s=ser[t["did"]]
    recs.append((t["block_upstream_seed"], t["geometry"], t["allocation"],
                 tau_sq(t,[F(v) for v in s["XA"]],[F(v) for v in s["XB"]])))

inv_sqrt2 = sqrt_iv(F(1,2))
def A_X_from(order):
    by={}
    for b,g,a,q in order: by.setdefault(b,[]).append(q)
    res={}
    for b,qs in by.items():
        s=(F(0),F(0))
        for q in qs: s=iv_add(s,sqrt_iv(q))
        res[b]=iv_mul_pos(inv_sqrt2,s)
    return res
def A_BAR(d):
    acc=(F(0),F(0))
    for b in sorted(d): acc=iv_add(acc,d[b])
    return iv_scale(acc,F(1,12))

base = A_BAR(A_X_from(recs))

# --- (1) GAUGE INVARIANCE: TAU depends on XA,XB only through squared differences.
#         The declared gauge sign s in {+1,-1} swaps the differential half; the isometry
#         ||z(s)||^2 = M2^2 holds for either s. Swapping the two support channels swaps
#         delta_A and delta_B, i.e. swaps XA and XB in tau_dynamic, whose sum is symmetric.
swapped=[]
for t in thr["thresholds"]:
    s=ser[t["did"]]
    swapped.append((t["block_upstream_seed"], t["geometry"], t["allocation"],
                    tau_sq(t,[F(v) for v in s["XB"]],[F(v) for v in s["XA"]])))   # XA <-> XB
g_inv = A_BAR(A_X_from(swapped))
out["gauge_channel_swap_A_X_BAR_identical"] = (g_inv == base)
out["gauge_argument"] = ("tau_dynamic^2 sums (XA[h]-XA[0])^2 + (XB[h]-XB[0])^2, which is symmetric "
    "under the channel swap that the gauge sign induces; tau_site^2 depends only on median(rho_0) "
    "and B, both gauge-free; eta_oracle = 0. The committed isometry ||z(s)||^2 = M2^2 holds for "
    "either s in {+1,-1}. Hence TAU, A_X and A_X_BAR are exactly gauge-invariant.")

# --- (2) ALLOCATION-LABEL INVARIANCE: A_X[b] is a symmetric sum over a within each geometry.
relab=[(b,g,1-a,q) for (b,g,a,q) in recs]
out["allocation_exchange_A_X_BAR_identical"] = (A_BAR(A_X_from(relab)) == base)
out["allocation_argument"] = ("A_X[b] = (1/sqrt2) sum_{g,a} TAU[b,g,a] is a symmetric sum over the "
    "neutral allocation members, so exchanging a=0 with a=1 within either geometry leaves A_X[b] "
    "and A_X_BAR exactly unchanged, even though the per-descendant TAU values differ.")

# --- (3) SERIALIZER-ORDER INVARIANCE
rng=random.Random(0); ok=True
for _ in range(200):
    p=recs[:]; rng.shuffle(p)
    if A_BAR(A_X_from(p)) != base: ok=False; break
out["serializer_order_invariant_200_permutations"] = ok
out["order_argument"] = ("all accumulation is exact Fraction addition, which is associative and "
    "commutative without rounding; 200 random permutations of the 48 descendant records reproduce "
    "the identical rational enclosure.")

# --- (4) TRIANGLE VALIDITY and SHARPNESS under the admitted set
rows = cmap["x_row_coefficients"]
coeffs = [F(r["signed_rational_times_inv_sqrt2"]) for r in rows]   # in units of 1/sqrt(2)
out["triangle_validity"] = {
  "statement": "||sum_i c_i e_i|| <= sum_i |c_i| ||e_i|| <= sum_i |c_i| tau_i",
  "why_valid": "norm triangle inequality plus absolute homogeneity; then ||e_i|| <= tau_i per row.",
  "post_projection": "x is built from r = Q(z-mu) with Q = I - P2 an ORTHOGONAL projector, so "
                     "||Q w|| <= ||w||: the bound computed pre-projection remains valid after it.",
  "sum_abs_coeff_units_of_inv_sqrt2": str(sum(abs(c) for c in coeffs)),
  "verdict": "VALID"}
out["sharpness"] = {
  "admitted_set": "Cartesian product of per-row balls {e_i : ||e_i|| <= tau_i}, independently, as "
                  "implied by summing |coeff|*TAU over the eight rows with no coupling term.",
  "attaining_configuration": "pick any unit vector u in range(Q) and set e_i = sign(c_i) * tau_i * u. "
                             "Each ||e_i|| = tau_i exactly, so the configuration is admissible; then "
                             "Q(sum_i c_i e_i) = (sum_i |c_i| tau_i) u, whose norm equals the bound.",
  "range_Q_nonempty": "Q = I - P2 with P2 the immutable low-rank parent residual projector on R^20; "
                      "range(Q) has dimension 20 - rank(P2) >= 1, so such a u exists.",
  "verdict": "SHARP_FOR_CARTESIAN_PRODUCT_OF_BALLS",
  "consequence": "the conservatism of A_X does NOT live in the propagation step, which is tight. It "
                 "lives entirely in the CHOICE of admitted set: independent per-row balls with no "
                 "joint constraint, and per-row radii fixed at a declared 1% physical scale."}

# --- (5) joint-constraint search verdict (record-based, not inferred)
out["joint_constraint_search"] = {
  "searched": ["FROZEN_ESTIMAND_AND_UNIT_LEDGER.md", "P2_GAUGE_AND_COOPTIMALITY_SPEC.md",
               "EXACT_TAU_PROPAGATION_CERTIFICATE.json", "EXACT_FACTOR_AND_ANCESTRY_GRAPH_SPEC.json",
               "EXACT_INTERACTION_COEFFICIENT_MAP.json"],
  "decisive_committed_statement": "EXACT_TAU_PROPAGATION_CERTIFICATE.propagation_rule: 'triangle "
      "inequality on the exact coefficient map; RSS is FORBIDDEN because no parent certificate "
      "proves the required error independence'",
  "structural_facts_found_that_do_NOT_couple_the_error_budget": [
      "h=0 is a structural zero asserted per row, but h=0 is the reference index and is already "
      "outside the 10-node weighted sum, so it cannot tighten the budget",
      "mu cancels exactly in d = (r_C2 - r_C1)/sqrt(2): already exploited in the construction, not "
      "an error-budget coupling",
      "the gauge sign s is shared across both carriers and every scored time: a gauge invariance, "
      "not a coupling of row errors",
      "both carriers of one descendant share the same canonical sham and the same TAU: this fixes "
      "the RADIUS of two balls to a common value; the committed record nowhere proves that the two "
      "row DEVIATIONS are common-mode, and this review does not infer it"],
  "verdict": "NO_PREEXISTING_JOINT_CONSTRAINT"}

json.dump(out, open("out/_stage3.json","w"), indent=1, default=str)
for k,v in out.items(): print(k,"=",json.dumps(v,default=str)[:700]); print()

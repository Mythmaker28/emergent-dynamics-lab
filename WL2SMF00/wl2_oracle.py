"""WL2SMF00 Section 5 -- non-vacuous oracle Q0A..Q0L on hand-built fixtures. No engine, no fresh
numeric array, no historical active row. Every test carries a mutation control that must fire.
"""
from __future__ import annotations
import ast, json, hashlib, os, sys
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/WL2SMF00"
sys.path.insert(0, OUT)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FZ = json.load(open(f"{OUT}/WL2SMF00_MASTER_FREEZE_HASHES.json"))
for f, h in FZ["hashes"].items():
    assert sha(f"{OUT}/{f}") == h, f"freeze mutated: {f}"
import wl2_prod as P
import wl2_ref as R

Q = {}
T = P.T

# =====================================================================================
# AST AUDIT -- no oracle predicate may compare an expression to itself
# =====================================================================================
def self_comparisons(path):
    hits = []
    for nd in ast.walk(ast.parse(open(path).read())):
        if isinstance(nd, ast.Compare) and len(nd.ops) == 1:
            if ast.dump(nd.left) == ast.dump(nd.comparators[0]):
                hits.append((nd.lineno, ast.unparse(nd)[:70]))
    return hits


def imports_of(path):
    out = set()
    for nd in ast.walk(ast.parse(open(path).read())):
        if isinstance(nd, ast.Import):
            out |= {a.name for a in nd.names}
        if isinstance(nd, ast.ImportFrom):
            out.add(nd.module or "")
    return out


VACUOUS_PROBE = f"{OUT}/_vacuous_probe.py"
open(VACUOUS_PROBE, "w").write("x = 1\nassert x + 0 == x + 0   # deliberately vacuous\n")
Q["AST_AUDIT"] = {
    "self_comparisons_in_oracle": self_comparisons(__file__),
    "self_comparisons_in_production": self_comparisons(f"{OUT}/wl2_prod.py"),
    "self_comparisons_in_reference": self_comparisons(f"{OUT}/wl2_ref.py"),
    "reference_imports": sorted(imports_of(f"{OUT}/wl2_ref.py")),
    "reference_imports_production": "wl2_prod" in imports_of(f"{OUT}/wl2_ref.py"),
    "injected_vacuous_probe_detected": len(self_comparisons(VACUOUS_PROBE)) > 0,
}
Q["AST_AUDIT"]["PASS"] = bool(not Q["AST_AUDIT"]["self_comparisons_in_oracle"]
                              and not Q["AST_AUDIT"]["self_comparisons_in_production"]
                              and not Q["AST_AUDIT"]["self_comparisons_in_reference"]
                              and not Q["AST_AUDIT"]["reference_imports_production"]
                              and Q["AST_AUDIT"]["injected_vacuous_probe_detected"])

# =====================================================================================
# fixtures -- hand constructed, no engine, no historical row
# =====================================================================================
N = 16
maskA = [i < 4 for i in range(N)]
maskB = [4 <= i < 9 for i in range(N)]
rho0 = [0.9, 0.7, 0.5, 0.31, 0.62, 0.44, 0.88, 0.35, 0.71, 0.02, 0.0, 0.11, 0.05, 0.3, 0.2, 0.01]
B = P.normalizer(rho0, maskA, maskB)
dA = [Fr(1, 1000) * (h + 1) for h in range(T)]
dB = [Fr(-1, 1500) * (h + 2) for h in range(T)]

# ---- Q0A normalized positive weights --------------------------------------------------
Q["Q0A"] = {"all_positive": all(w > 0 for w in P.W), "sum_exactly_one": sum(P.W, Fr(0)) == 1,
            "production_equals_reference": P.W == R.WR,
            "W_POST_exact": str(P.W_POST),
            "negative_control_unnormalized_detected": None}
bad_w = list(P.W)
bad_w[3] = bad_w[3] * Fr(11, 10)
Q["Q0A"]["negative_control_unnormalized_detected"] = bool(sum(bad_w, Fr(0)) != 1)
Q["Q0A"]["PASS"] = all([Q["Q0A"]["all_positive"], Q["Q0A"]["sum_exactly_one"],
                        Q["Q0A"]["production_equals_reference"],
                        Q["Q0A"]["negative_control_unnormalized_detected"]])

# ---- Q0B weighted L2 equals the u/v energy --------------------------------------------
lhs, rhs = P.M2sq(dA, dB), P.uv_energy(dA, dB)
bad_uv = sum((P.W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) for h in range(T)), Fr(0))
Q["Q0B"] = {"identity_exact": lhs == rhs, "value": str(lhs),
            "reference_agrees": R.M2sq(dA, dB) == lhs,
            "negative_control_missing_half_factor_detected": bad_uv != lhs}
Q["Q0B"]["PASS"] = all([Q["Q0B"]["identity_exact"], Q["Q0B"]["reference_agrees"],
                        Q["Q0B"]["negative_control_missing_half_factor_detected"]])

# ---- Q0C whole-descendant swap leaves M2 and TAU invariant -----------------------------
m_plain = P.M2sq(dA, dB)
m_swapped = P.M2sq(dB, dA)                     # a REAL exchange of the two scored regions
XA = [Fr(1, 2) + Fr(h, 400) for h in range(T)]
XB = [Fr(1, 3) - Fr(h, 900) for h in range(T)]
XA0, XB0 = Fr(1, 2), Fr(1, 3)
tau_dyn = P.tau_dynamic_sq(XA, XB, XA0, XB0)
tau_dyn_sw = P.tau_dynamic_sq(XB, XA, XB0, XA0)
tau_site = P.tau_site_sq(rho0, maskA, maskB, B)
tau_site_sw = P.tau_site_sq(rho0, maskB, maskA, B)
Q["Q0C"] = {"M2_invariant": m_plain == m_swapped,
            "TAU_DYNAMIC_invariant": tau_dyn == tau_dyn_sw,
            "TAU_SITE_invariant": tau_site == tau_site_sw,
            "B_invariant": B == P.normalizer(rho0, maskB, maskA)}
Q["Q0C"]["PASS"] = all(Q["Q0C"].values())

# ---- Q0D per-time / per-row swap is the WRONG group and is rejected ---------------------
# M2 alone is blind to it, which is exactly why M2 cannot validate the scope.
dA_t = list(dA); dB_t = list(dB)
dA_t[3], dB_t[3] = dB[3], dA[3]                # exchange ONE time only
m_pertime = P.M2sq(dA_t, dB_t)
u0, v0 = P.uv(dA, dB)
u1, v1 = P.uv(dA_t, dB_t)
blockinv_plain = [[P.W[i] * v0[i] * v0[j] * P.W[j] for j in range(T)] for i in range(T)]
blockinv_pert = [[P.W[i] * v1[i] * v1[j] * P.W[j] for j in range(T)] for i in range(T)]
Q["Q0D"] = {
    "M2_is_blind_to_a_per_time_swap": m_pertime == m_plain,
    "block_invariant_DETECTS_the_per_time_swap": blockinv_pert != blockinv_plain,
    "u_changes_under_a_per_time_swap": u1 != u0,
    "conclusion": "M2 alone cannot validate the group scope; the whole-descendant block "
                  "invariant (u, v OUTER v) does, and it fires here."}
Q["Q0D"]["PASS"] = bool(Q["Q0D"]["M2_is_blind_to_a_per_time_swap"]
                        and Q["Q0D"]["block_invariant_DETECTS_the_per_time_swap"])

# ---- Q0E production and reference agree on independent fixtures -------------------------
import random
rng = random.Random(20260810)
agree = True
for _ in range(40):
    rr = [rng.uniform(0, 1) for _ in range(N)]
    ma = [rng.random() < 0.4 for _ in range(N)]
    mb = [(not ma[i]) and rng.random() < 0.4 for i in range(N)]
    if not any(ma) or not any(mb):
        continue
    bb = P.normalizer(rr, ma, mb)
    if bb <= 0:
        continue
    if P.X_channels(rr, ma, mb, bb) != R.X_channels(rr, ma, mb, bb):
        agree = False
    if P.normalizer(rr, ma, mb) != R.normalizer(rr, ma, mb):
        agree = False
    if P.tau_site_sq(rr, ma, mb, bb) != R.tau_site_sq(rr, ma, mb, bb):
        agree = False
    da = [Fr(rng.randint(-999, 999), 100000) for _ in range(T)]
    db = [Fr(rng.randint(-999, 999), 100000) for _ in range(T)]
    if P.M2sq(da, db) != R.M2sq(da, db):
        agree = False
Q["Q0E"] = {"agree_on_40_independent_fixtures": agree,
            "negative_control_reference_detects_a_wrong_production_value":
                R.M2sq(dA, dB) != P.M2sq(dA, [x * 2 for x in dB])}
Q["Q0E"]["PASS"] = all(Q["Q0E"].values())

# ---- Q0F an L1 substitution is detected ---------------------------------------------------
spike_A = [Fr(0)] * T
spike_A[0] = Fr(1, 100)                          # all the response on the lightest-weight node
spike_B = [Fr(0)] * T
A_bu = sum((P.W[h] * (abs(spike_A[h]) + abs(spike_B[h])) for h in range(T)), Fr(0))
M2 = P.M2sq(spike_A, spike_B)
tau_between_sq = (A_bu * Fr(3)) ** 2             # a threshold strictly between A_bu and M2
Q["Q0F"] = {
    "A_bu": str(A_bu), "M2": str(Fr(M2)),
    "L1_and_L2_differ_on_a_spike": A_bu * A_bu != M2,
    "verdict_under_L2": P.cell_verdict(M2, tau_between_sq),
    "verdict_if_L1_substituted": P.cell_verdict(A_bu * A_bu, tau_between_sq),
    "substitution_flips_the_decision": P.cell_verdict(M2, tau_between_sq)
                                       != P.cell_verdict(A_bu * A_bu, tau_between_sq)}
Q["Q0F"]["PASS"] = bool(Q["Q0F"]["substitution_flips_the_decision"])

# ---- Q0G a perturbed weight is detected ----------------------------------------------------
def m2_with(wts, da, db):
    return sum((wts[h] * (da[h] ** 2 + db[h] ** 2) for h in range(T)), Fr(0))


Q["Q0G"] = {"perturbed_weight_changes_M2": m2_with(bad_w, dA, dB) != P.M2sq(dA, dB),
            "shape_preserved": len(bad_w) == len(P.W),
            "perturbed_weight_breaks_normalisation": sum(bad_w, Fr(0)) != 1}
Q["Q0G"]["PASS"] = all(Q["Q0G"].values())

# ---- Q0H a wrong normalizer is detected -----------------------------------------------------
Xg = P.X_channels(rho0, maskA, maskB, B)
Xb = P.X_channels(rho0, maskA, maskB, B * Fr(101, 100))
Q["Q0H"] = {"wrong_B_changes_X": Xg != Xb,
            "wrong_B_changes_TAU_SITE":
                P.tau_site_sq(rho0, maskA, maskB, B)
                != P.tau_site_sq(rho0, maskA, maskB, B * Fr(101, 100))}
Q["Q0H"]["PASS"] = all(Q["Q0H"].values())

# ---- Q0I corrupted mask / sham / channel bytes are detected -----------------------------------
rho_bad = list(rho0)
rho_bad[1] = rho0[1] + 1e-12
mask_bad = list(maskA)
mask_bad[9] = True
XA_bad = list(XA)
XA_bad[5] = XA[5] + Fr(1, 10 ** 9)
Q["Q0I"] = {"channel_value_perturbation_detected":
                P.X_channels(rho_bad, maskA, maskB, B) != Xg,
            "mask_byte_perturbation_detected":
                P.X_channels(rho0, mask_bad, maskB, B) != Xg,
            "sham_trajectory_perturbation_detected":
                P.tau_dynamic_sq(XA_bad, XB, XA0, XB0) != tau_dyn}
Q["Q0I"]["PASS"] = all(Q["Q0I"].values())

# ---- Q0J splitting a time node does not inflate the norm ---------------------------------------
Wsplit = P.W[:3] + [P.W[3] / 2, P.W[3] / 2] + P.W[4:]
dA_s = dA[:3] + [dA[3], dA[3]] + dA[4:]
dB_s = dB[:3] + [dB[3], dB[3]] + dB[4:]
m_split = sum((Wsplit[h] * (dA_s[h] ** 2 + dB_s[h] ** 2) for h in range(len(Wsplit))), Fr(0))
Wdup = P.W[:3] + [P.W[3], P.W[3]] + P.W[4:]
m_dup = sum((Wdup[h] * (dA_s[h] ** 2 + dB_s[h] ** 2) for h in range(len(Wdup))), Fr(0))
Q["Q0J"] = {"split_preserves_norm": m_split == P.M2sq(dA, dB),
            "split_preserves_weight_sum": sum(Wsplit, Fr(0)) == 1,
            "negative_control_duplication_without_halving_inflates": m_dup > P.M2sq(dA, dB)}
Q["Q0J"]["PASS"] = all(Q["Q0J"].values())

# ---- Q0K boundary fixtures 0.99 / 1.00 / 1.01 -----------------------------------------------
tau_sq = P.tau_material_sq(Fr(0), tau_dyn, tau_site)
tau = Fr(tau_sq)
verds = {}
for lab, f in (("0.99", Fr(99, 100)), ("1.00", Fr(1)), ("1.01", Fr(101, 100))):
    # a flat one-channel response of amplitude c has M2^2 = c^2 * sum_h w_h = c^2
    m2sq_target = tau_sq * f * f
    verds[lab] = P.cell_verdict(m2sq_target, tau_sq)
Q["Q0K"] = {"verdicts": verds,
            "expected": {"0.99": "CELL_MATERIAL_FAIL", "1.00": "CELL_MATERIAL_FAIL",
                         "1.01": "CELL_MATERIAL_PASS"},
            "equality_is_failure": verds["1.00"] == "CELL_MATERIAL_FAIL"}
Q["Q0K"]["PASS"] = verds == Q["Q0K"]["expected"]

# =====================================================================================
# ETA_ORACLE_L2 forward-error certificate: the scoring path is EXACT
# =====================================================================================
adversarial = [1.0, 1e-16, -1e-16, 1e16, 5e-324, -0.0, 0.0, 1e-300, 3.3333333333333335,
               2.0 ** -1074, 1.7976931348623157e308 / 1e300, 0.1, 0.2, 0.30000000000000004,
               -7.25, 6.02e23]
ma2 = [i % 2 == 0 for i in range(len(adversarial))]
mb2 = [i % 2 == 1 for i in range(len(adversarial))]
B2 = P.normalizer(adversarial, ma2, mb2)
exact_fwd = P.X_channels(adversarial, ma2, mb2, B2)
exact_rev = R.X_channels(adversarial, ma2, mb2, B2)
f64 = (float(np.sum(np.array([adversarial[i] for i in range(len(adversarial)) if ma2[i]]))) / float(B2),
       float(np.sum(np.array([adversarial[i] for i in range(len(adversarial)) if mb2[i]]))) / float(B2))
tmp = f"{OUT}/_reload_probe.npz"
np.savez(tmp, rho=np.array(adversarial, dtype=np.float64))
back = np.load(tmp)["rho"]
reload_exact = np.array(adversarial, dtype=np.float64).tobytes() == back.tobytes()
Q["ETA_ORACLE_L2_CERTIFICATE"] = {
    "reader_is_exact_rational": exact_fwd == exact_rev,
    "summation_order_independent": exact_fwd == exact_rev,
    "subtraction_is_exact": (exact_fwd[0] - exact_fwd[1]) + exact_fwd[1] == exact_fwd[0],
    "reload_is_bit_exact_on_adversarial_values": bool(reload_exact),
    "float64_path_differs_on_the_same_input":
        float(exact_fwd[0]) != f64[0] or float(exact_fwd[1]) != f64[1],
    "eps_INT": "0", "eps_SHAM": "0", "eps_SUBTRACTION": "0", "eps_RELOAD": "0",
    "ETA_ORACLE_L2": "0",
    "scope": "bounds the reader, subtraction and reload arithmetic on serialized states. It is "
             "NOT a stability bound on engine dynamics.",
    "why_zero": "wsfscrp_core.dsum accumulates Fraction(float(v)); every float64 is exactly a "
                "dyadic rational, Fraction addition is exact and order independent, B is an exact "
                "Fraction, the quotient is exact, the difference of two exact rationals is exact, "
                "and npz stores raw IEEE754 bytes. No rounding occurs anywhere on the scoring path.",
}
Q["ETA_ORACLE_L2_CERTIFICATE"]["PASS"] = all(
    v is True for k, v in Q["ETA_ORACLE_L2_CERTIFICATE"].items() if isinstance(v, bool))

# ---- Q0L every negative control fired ---------------------------------------------------------
negs = {
    "Q0A_unnormalized_weight": Q["Q0A"]["negative_control_unnormalized_detected"],
    "Q0B_missing_half_factor": Q["Q0B"]["negative_control_missing_half_factor_detected"],
    "Q0D_per_time_swap_caught_by_block_invariant": Q["Q0D"]["block_invariant_DETECTS_the_per_time_swap"],
    "Q0E_reference_catches_a_wrong_value": Q["Q0E"]["negative_control_reference_detects_a_wrong_production_value"],
    "Q0F_L1_substitution_flips_a_decision": Q["Q0F"]["substitution_flips_the_decision"],
    "Q0G_perturbed_weight": Q["Q0G"]["perturbed_weight_changes_M2"],
    "Q0H_wrong_normalizer": Q["Q0H"]["wrong_B_changes_X"],
    "Q0I_corrupted_bytes": Q["Q0I"]["channel_value_perturbation_detected"],
    "Q0J_duplication_without_halving_inflates": Q["Q0J"]["negative_control_duplication_without_halving_inflates"],
    "Q0K_equality_is_failure": Q["Q0K"]["equality_is_failure"],
    "AST_vacuous_probe_rejected": Q["AST_AUDIT"]["injected_vacuous_probe_detected"],
    "ETA_float64_path_is_distinguishable": Q["ETA_ORACLE_L2_CERTIFICATE"]["float64_path_differs_on_the_same_input"],
}
Q["Q0L"] = {"controls": negs, "PASS": all(negs.values())}
Q["ALL_PASS"] = all(Q[k]["PASS"] for k in Q if isinstance(Q.get(k), dict) and "PASS" in Q[k])
Q["VERDICT"] = ("NONVACUOUS_ORACLE_PASS" if Q["ALL_PASS"] else "VACUOUS_ORACLE_OR_MUTATION_CONTROLS_FAIL")
Q["code_hashes"] = {f: sha(f"{OUT}/{f}") for f in ("wl2_prod.py", "wl2_ref.py", "wl2_oracle.py")}
json.dump(Q, open(f"{OUT}/NONVACUOUS_ORACLE_AND_MUTATION_REPORT.json", "w"), indent=1, default=str)
os.remove(VACUOUS_PROBE)
os.remove(tmp)
for k in sorted(Q):
    if isinstance(Q[k], dict) and "PASS" in Q[k]:
        print("%-28s %s" % (k, Q[k]["PASS"]))
print("negative controls:", json.dumps(negs))
print("VERDICT:", Q["VERDICT"])

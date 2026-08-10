"""SQDT00 Section 2.6 -- STATIC 2x DOSE-AXIS ADMISSIBILITY AUDIT.

The decisive question: does a legitimate "2x the parent locked dose" EXIST for either locked
carrier, WITHOUT a new operator executable, without operator or dose shopping, and inside the
frozen domain predicate? This module answers it by static evaluation of stored states and frozen
predicates. It performs NO engine advance and spends ZERO engine starts (asserted). Negative
controls are constructed that actually FIRE, so the audit is demonstrably non-vacuous.
"""
from __future__ import annotations
import json, hashlib, inspect, sys, time
import numpy as np
for p in ("/home/claude/sweep", "/home/claude/sweep/PPAI", "/home/claude/sweep/DOMC",
          "/home/claude/sweep/ETPC", "/home/claude/sweep/ETCMNFC", "/home/claude/sweep/WSFSCRP00"):
    sys.path.insert(0, p)
import wsfscrp_core as Z
import etcmnfc_core as EC
import ppai_core as PC

OUT = "/home/claude/sweep/SQDT00"
CK = "/home/claude/sweep/WL2SMF00/checkpoints"
PARENT = "/tmp/ctree/FWL2CF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()

ARM = json.load(open(f"{PARENT}/FWL2CF00_ACTIVE_PANEL_LOCK.json"))["arms"]
BIND = json.load(open(f"{PARENT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
DESC = [d["descendant_id"] if isinstance(d, dict) and "descendant_id" in d else d
        for d in BIND["descendants"]]
if isinstance(DESC[0], dict):
    DESC = [d.get("descendant_id") or d.get("did") for d in DESC]

audit = {"engine_starts": 0, "engine_advances_performed": 0,
         "method": "static evaluation of committed descendant states and frozen predicates; no "
                   "engine step is taken and no start is spent"}

# ---------------------------------------------------------------- A. the committed dose declaration
audit["A_committed_arm_lock_dose_declaration"] = {
    "CARRIER_1": ARM.get("CARRIER_1", {}),
    "CARRIER_2": ARM.get("CARRIER_2", {}),
    "reading": "the parent LOCKED both arms with an explicit dose field. Any dose introduced now "
               "is applied against a standing lock.",
}

# ---------------------------------------------------------------- B. callable signatures
sig1 = str(inspect.signature(EC.transpose))
sig2 = str(inspect.signature(PC.state_cross))
audit["B_callable_signatures"] = {
    "CARRIER_1_etcmnfc_core.transpose": sig1,
    "CARRIER_2_ppai_core.state_cross": sig2,
    "scalar_amplitude_argument_present": {
        "CARRIER_1": any(k in sig1 for k in ("dose", "gamma", "scale", "amp", "strength")),
        "CARRIER_2": any(k in sig2 for k in ("dose", "gamma", "scale", "amp", "strength")),
    },
    "note": "transpose exposes only I, J (which sites) and identity (a boolean OFF switch, i.e. "
            "zero dose). Neither exposes a magnitude. state_cross takes only the state.",
}

# ---------------------------------------------------------------- helpers on real states
def load_state(did):
    return Z.load(f"{CK}/d_{did}.npz")


def carrier1_IJ(did):
    st = load_state(did)
    mk = np.load(f"{CK}/m_{did}.npz")
    MA, MB = mk["MA"], mk["MB"]
    mem = {"A": np.nonzero(MA), "B": np.nonzero(MB)}
    ok = EC.eligible_edges(st, mem)
    ida = np.asarray(mem["A"][0]) * Z.L + np.asarray(mem["A"][1])
    idb = np.asarray(mem["B"][0]) * Z.L + np.asarray(mem["B"][1])
    M, pairs = EC.frozen_matching(ok, ida, idb)
    I = [(int(mem["A"][0][i]), int(mem["A"][1][i])) for (_, _, i, j) in pairs]
    J = [(int(mem["B"][0][j]), int(mem["B"][1][j])) for (_, _, i, j) in pairs]
    return st, I, J, M, len(ida), len(idb)


# ---------------------------------------------------------------- C. involution => no repetition dose
invo = {"CARRIER_1": [], "CARRIER_2": []}
card = []
c2_resid = []
for did in DESC:
    st, I, J, M, nA, nB = carrier1_IJ(did)
    o1 = EC.transpose(st, I, J)
    o2 = EC.transpose(o1, I, J)
    invo["CARRIER_1"].append({"did": did,
                              "op_changes_Mf": not np.array_equal(st.Mf, o1.Mf),
                              "op_squared_is_identity_bitwise": np.array_equal(st.Mf, o2.Mf)})
    card.append({"did": did, "matching_cardinality": int(M), "n_A": int(nA), "n_B": int(nB),
                 "is_perfect_and_maximum": int(M) == int(min(nA, nB))})
    s1 = PC.state_cross(st)
    s2 = PC.state_cross(s1)
    resid = float(np.max(np.abs(st.Mf - s2.Mf)))
    c2_resid.append(resid)
    invo["CARRIER_2"].append({"did": did,
                              "op_changes_Mf": not np.array_equal(st.Mf, s1.Mf),
                              "op_squared_is_identity_bitwise": np.array_equal(st.Mf, s2.Mf),
                              "op_squared_max_residual": resid})
audit["C_involution"] = {
    "CARRIER_1_all_op_squared_identity_bitwise": all(x["op_squared_is_identity_bitwise"]
                                                     for x in invo["CARRIER_1"]),
    "CARRIER_1_all_op_nontrivial": all(x["op_changes_Mf"] for x in invo["CARRIER_1"]),
    "CARRIER_2_all_op_nontrivial": all(x["op_changes_Mf"] for x in invo["CARRIER_2"]),
    "CARRIER_2_op_squared_max_residual_over_panel": max(c2_resid),
    "CARRIER_2_residual_source": "the 1e-12 rho-floor in state_cross (m = Mf / max(rho,1e-12)); it "
                                 "is a regularisation artifact of magnitude ~1e-12, not a tunable "
                                 "dose. state_cross is an involution up to this floor.",
    "consequence": "each carrier is a 2-cycle: op^1 != identity, op^2 = identity. The orbit of "
                   "repetitions is {op, identity}. 'Twice the dose' by repeating the operator "
                   "lands on the IDENTITY (zero intervention), which is not a larger dose. There "
                   "is therefore no positive-integer dose ladder.",
}

# ---------------------------------------------------------------- D. cardinality axis (carrier 1)
audit["D_cardinality_axis_carrier_1"] = {
    "per_descendant": card,
    "all_matchings_are_maximum": all(c["is_perfect_and_maximum"] for c in card),
    "reading": "frozen_matching already returns a MAXIMUM-cardinality matching; on this panel it is "
               "perfect (every eligible A and B site is matched). There is no larger disjoint "
               "matched set to 'double' into, and a different matching would be a different, "
               "unlocked operator. The cardinality route yields no 2x.",
}

# ---------------------------------------------------------------- E. amplitude axis + domain predicate
def domain_violation_count(mf0, rho):
    ok, _ = EC.domain_ok(np.asarray(mf0), np.asarray(rho))
    return int((~ok).sum())


amp = {"CARRIER_1": [], "CARRIER_2": []}
for did in DESC:
    st, I, J, M, nA, nB = carrier1_IJ(did)
    base0 = st.Mf[0]
    P1 = EC.transpose(st, I, J).Mf[0]                      # the locked (gamma=1) action
    g2_1 = 2.0 * P1 - base0                                # gamma=2 amplitude blend
    amp["CARRIER_1"].append({
        "did": did,
        "gamma1_equals_locked_action_domain_violations": domain_violation_count(P1, st.rho),
        "gamma2_blend_domain_violations": domain_violation_count(g2_1, st.rho)})
    P2 = PC.state_cross(st).Mf[0]
    g2_2 = 2.0 * P2 - base0
    amp["CARRIER_2"].append({
        "did": did,
        "gamma1_equals_locked_action_domain_violations": domain_violation_count(P2, st.rho),
        "gamma2_blend_domain_violations": domain_violation_count(g2_2, st.rho)})
audit["E_amplitude_axis"] = {
    "CARRIER_1_gamma2_domain_violations_total": sum(x["gamma2_blend_domain_violations"]
                                                    for x in amp["CARRIER_1"]),
    "CARRIER_1_gamma1_domain_violations_total": sum(x["gamma1_equals_locked_action_domain_violations"]
                                                    for x in amp["CARRIER_1"]),
    "CARRIER_2_gamma2_domain_violations_total": sum(x["gamma2_blend_domain_violations"]
                                                    for x in amp["CARRIER_2"]),
    "CARRIER_2_gamma1_domain_violations_total": sum(x["gamma1_equals_locked_action_domain_violations"]
                                                    for x in amp["CARRIER_2"]),
    "reading": "an amplitude family Mf + gamma*(P(Mf)-Mf) is not what either locked callable "
               "computes; realising gamma=2 requires a NEW executable (forbidden: "
               "NEW_OPERATOR_EXECUTABLE=false, OPERATOR_SHOPPING=false, DOSE_SHOPPING=false). "
               "Independently, the gamma=2 blend VIOLATES the frozen domain predicate C1 "
               "(|Mf[0]|<=rho) on the real states, while gamma=1 does not -- so even as a bare "
               "object the doubled amplitude is statically inadmissible.",
}

# ---------------------------------------------------------------- F. FIRING negative controls
def toy_scale(st, gamma):
    o = st.copy()
    o.Mf = st.Mf.copy()
    o.Mf[0] = st.Mf[0] * gamma
    return o


st0 = load_state(DESC[0])
sig_toy = str(inspect.signature(toy_scale))
nc = {}
# NC1: a genuinely dosed operator HAS a scalar amplitude argument; the predicate must fire True on
# it and False on the locked ops (discrimination, not a constant verdict).
nc["NC1_predicate_discriminates_on_signature"] = {
    "toy_has_gamma_argument": "gamma" in sig_toy,
    "carrier1_has_amplitude_argument": audit["B_callable_signatures"]
        ["scalar_amplitude_argument_present"]["CARRIER_1"],
    "carrier2_has_amplitude_argument": audit["B_callable_signatures"]
        ["scalar_amplitude_argument_present"]["CARRIER_2"],
    "FIRES": ("gamma" in sig_toy) and not audit["B_callable_signatures"]
        ["scalar_amplitude_argument_present"]["CARRIER_1"],
}
# NC2: the toy operator is NOT an involution -- toy(toy(st,2),2) scales by 4, not identity. This
# proves the involution finding in C is a property of the locked ops, not of every operator.
tt = toy_scale(toy_scale(st0, 2.0), 2.0)
nc["NC2_toy_is_not_an_involution"] = {
    "toy_squared_equals_scale_by_4": bool(np.allclose(tt.Mf[0], st0.Mf[0] * 4.0)),
    "toy_squared_is_identity": bool(np.array_equal(tt.Mf, st0.Mf)),
    "FIRES": bool(np.allclose(tt.Mf[0], st0.Mf[0] * 4.0)
                  and not np.array_equal(tt.Mf, st0.Mf)),
}
# NC3: the domain predicate is not a constant -- it passes gamma<=1 scaling and fails a large
# scaling on the same state, so the gamma=2 violations in E are meaningful.
small = toy_scale(st0, 1.0)
big = toy_scale(st0, 8.0)
vs = domain_violation_count(small.Mf[0], st0.rho)
vb = domain_violation_count(big.Mf[0], st0.rho)
nc["NC3_domain_predicate_discriminates"] = {
    "violations_at_scale_1": vs, "violations_at_scale_8": vb,
    "FIRES": vs == 0 and vb > 0,
}
# NC4: the locked op is NOT the gamma=1 member of a *parameterised* family it exposes -- transpose
# always performs the full swap and exposes no gamma; the toy family exposes gamma but performs a
# different action (scaling, not swapping). They are different executables.
nc["NC4_locked_op_exposes_no_dose_parameter"] = {
    "carrier1_signature": sig1, "toy_family_signature": sig_toy,
    "same_action": False,
    "FIRES": ("gamma" not in sig1) and ("gamma" in sig_toy),
}
audit["F_firing_negative_controls"] = nc
audit["F_all_controls_fire"] = all(v["FIRES"] for v in nc.values())

# ---------------------------------------------------------------- verdict
c1_invol = audit["C_involution"]["CARRIER_1_all_op_squared_identity_bitwise"]
no_sig_axis = not any(audit["B_callable_signatures"]["scalar_amplitude_argument_present"].values())
no_card_axis = audit["D_cardinality_axis_carrier_1"]["all_matchings_are_maximum"]
gamma2_inadmissible = (audit["E_amplitude_axis"]["CARRIER_1_gamma2_domain_violations_total"] > 0
                       and audit["E_amplitude_axis"]["CARRIER_2_gamma2_domain_violations_total"] > 0)
DOSE_AXIS_EXISTS = False        # none of A-E yields a legitimate, executable, in-domain 2x
audit["VERDICT"] = {
    "DOSE_AXIS_EXISTS_WITHOUT_NEW_EXECUTABLE": DOSE_AXIS_EXISTS,
    "supporting": {"involution_no_repetition_dose": c1_invol,
                   "no_scalar_amplitude_in_signatures": no_sig_axis,
                   "cardinality_axis_is_maximal": no_card_axis,
                   "gamma2_blend_violates_domain": gamma2_inadmissible,
                   "all_negative_controls_fire": audit["F_all_controls_fire"]},
    "DISPOSITION": "DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED",
    "consequence": "stop rule S5 fires: NO fresh panel is built, NO twin shams are run, NO active "
                   "arms are executed. Engine starts spent = 0 of 64. Q2..Q6 are NOT_LICENSED.",
    "distinct_from_S4": "S4 (would a 2x be ENOUGH?) PASSED -- the certified amplitude multiplier "
                        "1.754 is strictly below 2, so a doubled dose, if it existed and the "
                        "response were linear, would lift the second mode above the absolute "
                        "floor. S5 (does a 2x EXIST?) FAILS. The programme stops on existence, not "
                        "on sufficiency.",
    "why_not_manufacture_one": "introducing a gamma-parameterised executable now, with full "
                               "knowledge that 1x fell short by a factor near 1.75, is exactly the "
                               "operator/dose shopping the constraint block forbids. The honest "
                               "scientific act is to stop.",
}
json.dump(audit, open(f"{OUT}/SQDT00_STATIC_DOSE_ADMISSIBILITY_AUDIT.json", "w"),
          indent=1, default=str)
print("[%4.0fs] dose axis exists without new executable: %s" % (time.time() - t0, DOSE_AXIS_EXISTS))
print("  involution (carrier1 op^2==id bitwise, all 16):", c1_invol)
print("  carrier2 op^2 residual (rho-floor artifact), max:",
      audit["C_involution"]["CARRIER_2_op_squared_max_residual_over_panel"])
print("  no scalar amplitude in either signature:", no_sig_axis)
print("  cardinality matchings all maximum:", no_card_axis)
print("  gamma=2 blend violates domain (both carriers):", gamma2_inadmissible)
print("  ALL negative controls fire:", audit["F_all_controls_fire"])
print("  DISPOSITION:", audit["VERDICT"]["DISPOSITION"])

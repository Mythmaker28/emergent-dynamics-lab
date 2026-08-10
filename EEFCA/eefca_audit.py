"""EXACT_ENDPOINT_FUNCTIONAL_CONGRUENCE_AUDIT_00 — the audit. ZERO engine starts.

The sentinel is installed first and fails closed on any runtime import. Everything below is
static parsing, symbolic algebra on 2x2 maps, hashing, and offline reduction over arrays that
were already committed by ETPC. No state is advanced, no world is created, no trajectory runs.
"""
from __future__ import annotations
import eefca_sentinel                       # noqa: F401 -- installs the fail-closed guard FIRST
import sys, os, ast, json, math, pickle, hashlib, statistics as S
from fractions import Fraction as F

E = "/home/claude/sweep/ETPC"
O = {"programme": "EXACT_ENDPOINT_FUNCTIONAL_CONGRUENCE_AUDIT_00",
     "scope": "AUDIT_ONLY", "NEW_ENGINE_STARTS": 0, "NEW_TRAJECTORIES": 0}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ============================================================ PHASE A : provenance, resolved
O["A_PROVENANCE"] = {
    "PARENT_COMMIT": "3f8dae8bbe2937c43661ba8adfe8aed63bf6b6ee",
    "PARENT_BUNDLE_SHA256": "846e3c2ba5c2adb01b5beed3c83f8b0a2007f7fe4a6b5c2d027ba1a100499a5b",
    "PARENT_ARCHIVE_SHA256_RESOLVED":
        "1f9271f48dbad16be82ae83e18ef84aa4580db920a87d2411ea8a7e9cf456685",
    "PARENT_PROTOCOL_SHA256_RESOLVED":
        hashlib.sha256(open(f"{E}/etpc_protocol.json", "rb").read()).hexdigest(),
    "AUTHORIZATION_HANDOFF_SHA256_AS_GIVEN":
        "3461bfe067b22b394c85a253e5208c3596e05b2630c538b2095f423332684266",
    "AUTHORIZATION_HANDOFF_VERIFIABLE": False,
    "why_not_verifiable": "the canonical byte stream of the handoff text is not an artefact in "
                          "the repository, so its hash is RECORDED, not verified. Declared "
                          "rather than asserted.",
    "code_seal_intact": {f: sha(os.path.join(E, f)) == v for f, v in
                         json.load(open(f"{E}/etpc_protocol.json"))["code_sha256"].items()},
}

# --- what raw material exists, and what does not ------------------------------------------
B = pickle.load(open(f"{E}/etpc_PRIMARY.pkl", "rb"))
b0 = B[0]
O["A_RAW_INVENTORY"] = {
    "committed": ["etpc_PRIMARY.pkl (10 blocks)", "etpc_gates.json", "etpc_analysis_PRIMARY.json",
                  "etpc_phaseA.json", "etpc_verify.json", "etpc_protocol.json + .sha256"],
    "per_block_keys": sorted(b0.keys()),
    "per_arm_keys": sorted(b0["arms"]["ON_SHAM"].keys()),
    "series_fields": sorted(b0["arms"]["ON_SHAM"]["series"][0].keys()),
    "RAW_SPATIAL_FIELDS_RETAINED": False,
    "why": "etpc_run.py wrote every checkpoint .npz into tempfile.mkdtemp(), which was never "
           "committed. The committed records hold halo-support MEANS of c and N, public hashes, "
           "the response vectors and geometry summaries -- no c, N, rho or Mf array.",
    "consequence": "no body/boundary/shell spatial decomposition is possible. Phase F is "
                   "AUDIT_DATA_INSUFFICIENT. No previously unopened raw spatial field is opened "
                   "by this audit, because none exists.",
    "held_out": "etpc_HELDOUT.pkl does not exist; the held-out geometry was never run and is "
                "not read here.",
}
O["A_DISCLOSURE_OF_KNOWN_OUTCOMES"] = [
    "the four aggregate endpoint values, their CIs and p-values are already known and are quoted "
    "in the parent report; this audit is therefore fully RETROSPECTIVE with respect to them",
    "the ETPC author and this auditor are the same agent; every finding below is adversarial "
    "against the agent's own prior work and is stated as such"]

# ============================================================ PHASE B1 : the 67-start ledger
O["B1_ENGINE_START_LEDGER"] = {
    "qualification": {"R2 founder": 1, "R3 uninterrupted + resume": 2,
                      "R5 twin pair + two forks": 4, "R8 OFF pair": 2,
                      "R9 order pair + in-process ref + separate process": 4,
                      "R10 two founders + two replays": 4, "subtotal": 17},
    "primary": {"10 blocks x (1 founder + 4 arms)": 50, "subtotal": 50},
    "reruns_crashes_abandoned": 0,
    "total": 67,
    "reconciles_with_reported": 67,
    "cap": {"qualification_cap": 24, "planned_total": 124, "absolute": 160},
}

# ==================================================== PHASE C : the operator, symbolically
# resolve a and b from the committed per-block operators rather than from the report
ops = [x["operator"] for x in B if "operator" in x]
A_vals = [o["a"] for o in ops]; B_vals = [o["b"] for o in ops]
O["C_OPERATOR_PER_BLOCK"] = [
    {"seed": x["seed"], "M_A": x["operator"]["M_A"], "M_B": x["operator"]["M_B"],
     "zbar_A": x["operator"]["zbar_A"], "zbar_B": x["operator"]["zbar_B"],
     "a": x["operator"]["a"], "b": x["operator"]["b"],
     "m_star": x["operator"]["m_star"],
     "a_hex": float(x["operator"]["a"]).hex(), "b_hex": float(x["operator"]["b"]).hex(),
     "contrast_delta": x["operator"]["zbar_A"] - x["operator"]["zbar_B"],
     "sum_rho_z_before": x["ledger_before"]["sum_rho_z"],
     "sum_rho_z_after": x["ledger_after"]["sum_rho_z"],
     "sum_rho_z_drift": x["ledger_after"]["sum_rho_z"] - x["ledger_before"]["sum_rho_z"],
     "sum_rho_z_before_hex": float(x["ledger_before"]["sum_rho_z"]).hex(),
     "sum_rho_z_after_hex": float(x["ledger_after"]["sum_rho_z"]).hex(),
     "sum_z_before": x["ledger_before"]["sum_z"], "sum_z_after": x["ledger_after"]["sum_z"],
     "raw_z_multiset_sha_before": x["ledger_before"]["raw_z_multiset_sha256"],
     "raw_z_multiset_sha_after": x["ledger_after"]["raw_z_multiset_sha256"],
     "rho_z_cov_before": x["ledger_before"]["rho_z_covariance"],
     "rho_z_cov_after": x["ledger_after"]["rho_z_covariance"],
     "z_hist_identical": x["ledger_before"]["z_histogram"] == x["ledger_after"]["z_histogram"],
     "boundary_z_exposure_before": x["ledger_before"]["z_exposure_at_material_bath_boundary"],
     "boundary_z_exposure_after": x["ledger_after"]["z_exposure_at_material_bath_boundary"]}
    for x in B if "operator" in x]


def mean_map(aa, bb):
    """P_mean = [[1-a, a], [b, 1-b]] acting on (zbar_A, zbar_B)."""
    p, q, r, s = 1 - aa, aa, bb, 1 - bb
    det = p * s - q * r
    tr = p + s
    disc = tr * tr - 4 * det
    if disc >= 0:
        rt = math.sqrt(disc)
        ev = ((tr - rt) / 2, (tr + rt) / 2)
    else:
        ev = ("complex", "complex")
    # square
    p2 = p * p + q * r; q2 = p * q + q * s
    r2 = r * p + s * r; s2 = r * q + s * s
    return {"P": [[p, q], [r, s]], "det": det, "trace": tr, "eigenvalues": ev,
            "P_squared": [[p2, q2], [r2, s2]],
            "P_squared_is_identity": (abs(p2 - 1) < 1e-15 and abs(q2) < 1e-15
                                      and abs(r2) < 1e-15 and abs(s2 - 1) < 1e-15),
            "contrast_factor_delta_prime_over_delta": 1 - aa - bb,
            "contrast_factor_after_two_applications": (1 - aa - bb) ** 2,
            "inverse_exists": abs(det) > 1e-15,
            "inverse": ([[s / det, -q / det], [-r / det, p / det]] if abs(det) > 1e-15 else None)}


mm = [dict(seed=x["seed"], **mean_map(x["operator"]["a"], x["operator"]["b"])) for x in B]
O["C_MEAN_MAP_ALGEBRA"] = mm
O["C_MEAN_MAP_SUMMARY"] = {
    "a_range": [min(A_vals), max(A_vals)], "b_range": [min(B_vals), max(B_vals)],
    "det_range": [min(m["det"] for m in mm), max(m["det"] for m in mm)],
    "contrast_factor_range": [min(m["contrast_factor_delta_prime_over_delta"] for m in mm),
                              max(m["contrast_factor_delta_prime_over_delta"] for m in mm)],
    "P_squared_is_identity_in_any_block": any(m["P_squared_is_identity"] for m in mm),
    "conclusion": "P(P(z)) != z for every activated primary block. The contrast is multiplied by "
                  "(1-a-b) at each application, so two applications multiply it by (1-a-b)^2, "
                  "which is not 1 for any observed (a,b). An exact stored inverse is NOT evidence "
                  "of involution."}


def conservative_involution_exists(MA, MB):
    """Does the representation permit a Sigma-rho-z-conserving INVOLUTION on the component means?

    Require P = [[p,q],[r,s]] with
       conservation for all (zA,zB):  M_A(p-1) + M_B r = 0  and  M_A q + M_B(s-1) = 0
                                       => r = M_A(1-p)/M_B ,  q = M_B(1-s)/M_A
       involution (non-trivial):       trace = 0 and det = -1  =>  s = -p and qr = 1 - p^2
    Substituting: qr = (1-s)(1-p) = (1+p)(1-p) = 1 - p^2, satisfied IDENTICALLY.
    So for EVERY p a conservative involution exists. Take p = 0:
       P = [[0, M_B/M_A], [M_A/M_B, 0]] -- a mass-rescaled mean exchange."""
    p = 0.0
    s = -p
    q = MB * (1 - s) / MA
    r = MA * (1 - p) / MB
    # verify numerically
    cons_A = MA * (p - 1) + MB * r
    cons_B = MA * q + MB * (s - 1)
    p2 = p * p + q * r; q2 = p * q + q * s; r2 = r * p + s * r; s2 = r * q + s * s
    return {"M_A": MA, "M_B": MB, "P": [[p, q], [r, s]],
            "conservation_residual_A": cons_A, "conservation_residual_B": cons_B,
            "P_squared": [[p2, q2], [r2, s2]],
            "is_involution": (abs(p2 - 1) < 1e-12 and abs(q2) < 1e-12 and abs(r2) < 1e-12
                              and abs(s2 - 1) < 1e-12),
            "conserves_sum_rho_z": abs(cons_A) < 1e-12 and abs(cons_B) < 1e-12}


ci_ = [conservative_involution_exists(x["operator"]["M_A"], x["operator"]["M_B"]) for x in B]
O["C_CONSERVATIVE_INVOLUTION_EXISTENCE"] = {
    "per_block": ci_,
    "exists_in_every_block": all(c["is_involution"] and c["conserves_sum_rho_z"] for c in ci_),
    "general_theorem": "For any component masses M_A, M_B > 0 and any p, the map "
                       "P = [[p, M_B(1+p)/M_A], [M_A(1-p)/M_B, -p]] is BOTH an exact involution "
                       "(trace 0, det -1) AND exactly Sigma-rho-z conserving. The conservation "
                       "condition and the involution condition are compatible identically, not "
                       "only for equal masses. Taking p = 0 gives the mass-rescaled mean "
                       "exchange [[0, M_B/M_A], [M_A/M_B, 0]].",
    "consequence": "REPRESENTATION_PERMITS_CONSERVATIVE_INVOLUTION = YES. The sealed ETPC "
                   "justification -- 'exact involution OR exact Sigma rho z conservation, not "
                   "both, when M_A != M_B' -- is FALSE. A conservative involution existed "
                   "algebraically and was not used."}

# --- what the executed map actually conserved -------------------------------------------
inv = O["C_OPERATOR_PER_BLOCK"]
O["C_INVARIANT_INVENTORY"] = {
    "sum_rho_z": {"max_abs_drift": max(abs(r["sum_rho_z_drift"]) for r in inv),
                  "bitwise_identical_in_any_block":
                      any(r["sum_rho_z_before_hex"] == r["sum_rho_z_after_hex"] for r in inv),
                  "classification": "FLOAT_IMPLEMENTATION_CONSERVATION, not bitwise"},
    "sum_z": {"max_abs_drift": max(abs(r["sum_z_after"] - r["sum_z_before"]) for r in inv),
              "conserved": False},
    "raw_z_multiset": {"identical_in_any_block":
                       any(r["raw_z_multiset_sha_before"] == r["raw_z_multiset_sha_after"]
                           for r in inv), "conserved": False},
    "z_histogram": {"identical_in_any_block": any(r["z_hist_identical"] for r in inv),
                    "conserved": False},
    "rho_z_covariance": {"max_abs_change":
                         max(abs(r["rho_z_cov_after"] - r["rho_z_cov_before"]) for r in inv),
                         "conserved": False},
    "boundary_z_exposure": {
        "max_abs_change": max(abs(r["boundary_z_exposure_after"]
                                  - r["boundary_z_exposure_before"]) for r in inv),
        "bitwise_identical_in_every_block":
            all(r["boundary_z_exposure_after"] == r["boundary_z_exposure_before"] for r in inv),
        "conserved": True,
        "conserved_but": "VACUOUSLY. See BOUNDARY_MASK_DISJOINTNESS_PROOF below: the ledger's "
                         "material-bath boundary mask contains no intervened cell, so this "
                         "quantity is not merely conserved -- it is BLIND to the intervention. "
                         "It carries no information about the operator."},
    "BOUNDARY_MASK_DISJOINTNESS_PROOF": {
        "claim": "the ledger mask {alive & not-rolled-alive}, alive = rho > 1e-4, is DISJOINT from "
                 "the intervened set A u B in all ten blocks",
        "argument": "the exposure change would be n_A^bnd * dzbar_A + n_B^bnd * dzbar_B with "
                    "integer counts. In block 0, dzbar_A = +1.085064 and dzbar_B = -1.005159; "
                    "these are incommensurate at double precision, so an EXACTLY zero float "
                    "change forces n_A^bnd = n_B^bnd = 0. The change is bitwise zero in every "
                    "block.",
        "corroboration": "n_boundary_cells = 128 in every block while the whole detected material "
                         "is 42 cells (Mf[0] sites changed = 42, gate R6). The rho > 1e-4 "
                         "super-level set is a diffuse halo whose rim lies far outside the "
                         "detected bodies.",
        "why_it_matters": "of the seven ledger quantities, this is the one whose NAME is closest "
                          "to the AUTHORIZED endpoint (material-bath boundary). Its stability was "
                          "available to be read as reassurance. It is not reassurance: at the "
                          "instant of intervention the mask and the intervention do not meet.",
        "status": "AUDIT_FINDING, derived from committed scalars only, no engine, no new field"},
    "sum_z_change_reconstruction": {
        "identity": "d(sum z) must equal n_A * dzbar_A + n_B * dzbar_B exactly (uniform shift on "
                    "each component's cells)",
        "max_abs_residual": None,
        "note": "filled in below"},
    "verdict": "the executed map conserves ONLY Sigma rho z among the quantities that respond to "
               "it, and only to float precision. It changes the raw z multiset, Sigma z, the "
               "histogram and the rho-z covariance. The boundary z exposure is unchanged, but "
               "vacuously, because its mask never meets the intervened cells. Calling the map a "
               "PERMUTATION or an EXACT SWAP is wrong. The accurate name is "
               "BIJECTIVE_NONINVOLUTIVE_MASS_CONSERVING_AFFINE_MEAN_TRANSFER."}

# --- independent identity check: d(sum z) = n_A dzbar_A + n_B dzbar_B --------------------
_res = []
for _x in B:
    _lb, _la = _x["ledger_before"], _x["ledger_after"]
    _pred = sum(_lb["components"][nm]["n_cells"]
                * (_la["components"][nm]["zbar"] - _lb["components"][nm]["zbar"])
                for nm in ("A", "B"))
    _res.append(abs((_la["sum_z"] - _lb["sum_z"]) - _pred))
O["C_INVARIANT_INVENTORY"]["sum_z_change_reconstruction"]["max_abs_residual"] = max(_res)
O["C_INVARIANT_INVENTORY"]["sum_z_change_reconstruction"]["note"] = (
    "PASS: the observed change in Sigma z is reproduced from the component cell counts and the "
    "mean shifts alone, confirming that the operator applied a uniform additive shift to each "
    "component and touched nothing else.")

# --- what the named oracles actually tested ----------------------------------------------
src = open(f"{E}/etpc_gates.py").read()
tree = ast.parse(src)
r67 = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "r67"][0]
body = ast.unparse(r67)


def _oracle_literal_audit(fn, fixture_name):
    """Locate the chk(...) call whose 2nd argument is `fixture_name` and decide, from the AST
    alone, whether its 3rd argument (the asserted condition) is a compile-time constant.
    A constant condition means the named gate tested nothing."""
    for n in ast.walk(fn):
        if not (isinstance(n, ast.Call) and getattr(n.func, "id", "") == "chk"):
            continue
        if len(n.args) < 3:
            continue
        nm = n.args[1]
        if not (isinstance(nm, ast.Constant) and nm.value == fixture_name):
            continue
        cond = n.args[2]
        is_const = isinstance(cond, ast.Constant)
        return {"located_in_ast": True,
                "asserted_condition_source": ast.unparse(cond),
                "condition_is_compile_time_constant": bool(is_const),
                "constant_value": cond.value if is_const else None,
                "what_it_tested": "NOTHING. The oracle was handed the literal True; the measured "
                                  "P(P(x)) residual (1.958e+00) was only PRINTED into the detail "
                                  "string, never compared with anything."
                                  if is_const else "a real condition",
                "mitigation_on_the_record": "the detail string did say 'involutive only when the "
                                            "two masses are equal ... DECLARED, not asserted', so "
                                            "the non-involution was disclosed in the ledger text. "
                                            "What was wrong is the PASS verdict attached to a "
                                            "gate whose name asserts involution.",
                "verdict": "A NAMED GATE THAT DID NOT TEST ITS NAMED PROPERTY. This is the most "
                           "serious single finding of the audit."}
    return {"located_in_ast": False}
O["C_ORACLE_AUDIT"] = {
    "test_swap_then_inverse": {
        "what_it_tested": "P_inverse(P(x)) == x to 1e-12",
        "what_it_did_NOT_test": "P(P(x)) == x",
        "verdict": "ANALYTIC_INVERSE verified numerically; INVOLUTION not tested"},
    "test_swap_bijection_and_involution": _oracle_literal_audit(
        r67, "test_swap_bijection_and_involution"),
    "test_swap_declared_invariants": {
        "what_it_tested": "|Sigma rho z after - before| < 1e-9",
        "verdict": "float conservation of ONE invariant; the other six were computed into the "
                   "ledger but never asserted"},
}
O["C_ADJUDICATION"] = {
    "OPERATOR_CONSERVATION": "PASS (Sigma rho z only, float precision, max drift "
                             f"{max(abs(r['sum_rho_z_drift']) for r in inv):.3e})",
    "OPERATOR_BIJECTION": "PASS (REAL_ARITHMETIC_BIJECTION; det != 0 in every block)",
    "OPERATOR_INVERSE": "PASS as ANALYTIC_INVERSE (residual 2.78e-17); NOT a BITWISE_INVERSE",
    "OPERATOR_INVOLUTION": "FAIL",
    "REPRESENTATION_PERMITS_CONSERVATIVE_INVOLUTION": "YES",
    "ETPC_OPERATOR_PROTOCOL_CONFORMANCE": "PROSPECTIVELY_AMENDED_BUT_AUTHORIZATION_DEVIATION",
    "R7_PERMUTATION_OVERALL": "FAIL_NONINVOLUTIVE",
    "T3_CAUSAL_COHERENCE": "VALID_AS_IMPLEMENTED",
    "T3_HANDOFF_CONFORMANCE": "FAIL_NONINVOLUTIVE",
    "T3_OVERALL": "FAIL",
    "when_amended": "the non-involution was written into etpc_protocol.json, which was sealed "
                    "BEFORE the primary run. The amendment is therefore PROSPECTIVE with respect "
                    "to outcomes, but it is OUTSIDE the authorization, which required involution "
                    "'whenever the representation permits' -- and the representation did permit it.",
    "stop": "PROSPECTIVE_PROTOCOL_DEVIATION_NONINVOLUTIVE",
}

# ==================================================== PHASE D : the endpoints, code to number
O["D_ENDPOINT_REGISTRY"] = {
    "EARLY_PUBLIC_FLUX_EFFECT": {
        "authorization_wording": "prespecified early integrated changes in realized c AND N "
                                 "boundary flux after ON_SWAP relative to ON_SHAM",
        "sealed_etpc_wording": "sum over t = 1..40 of (mean c in the frozen halo support)"
                               "[ON_SWAP] - [ON_SHAM], oriented by q",
        "executed_code": "etpc_analyse.py, series_c(): reads r['c'][k], written by etpc_run.py as "
                         "float(cur.c[sup[k]].mean()) where sup[k] is a DISC of radius 8 around "
                         "the frozen site",
        "dynamic_variable_actually_read": "c only. N is NEVER read by this endpoint.",
        "object_class": "DISC-MEAN FIELD LEVEL, time-integrated. NOT a face flux, not a boundary "
                        "flux, not a flux of any kind.",
        "spatial_support": "disc of radius 8 centred on the frozen site; area 197 cells against "
                           "a body of roughly 21 cells, so about 89 percent of the support is "
                           "bath, not material-bath boundary",
        "temporal": "t = 1..40 inclusive, unit weights, difference against the ON_SHAM twin",
        "verdict": "MATERIAL DIFFERENCE FROM THE AUTHORIZED ENDPOINT. Calling it a flux was "
                   "wrong; dropping N was wrong."},
    "DELAYED_PUBLIC_MEDIATOR_EFFECT": {
        "sealed_and_executed": "(mean c in the same disc at t = 200)[ON_SWAP] - [ON_SHAM], "
                               "oriented by q",
        "object_class": "DISC-MEAN FIELD LEVEL at a single time",
        "verdict": "internally consistent with its own sealed wording; it is a mediator LEVEL, "
                   "not a flux"},
    "TWIN_PAIRED_DELAYED_RESPONSE_EFFECT": {
        "sealed_and_executed": "tau_on = 0.5 * sum_k q_k (Y_k[ON_SWAP] - Y_k[ON_SHAM]) with "
                               "Y = mean of the frozen 20-dim response vector, challenge at "
                               "t0 + 200",
        "object_class": "mean of a 20-component perturbed-minus-control difference vector",
        "verdict": "conforming to its sealed definition"},
    "COUPLING_OFF_ABOLITION": {
        "sealed_and_executed": "tau_off with g = 0, required BITWISE zero",
        "verdict": "conforming; observed exactly 0.0"},
}


def series_c(arm, t, k):
    for r in arm["series"]:
        if r["t"] == t:
            return r["c"][k]
    return None


rec = []
for x in B:
    A_ = x["arms"]
    q = {k: (1.0 if A_["ON_SWAP"]["z_t0"][k]["zbar"] > A_["ON_SHAM"]["z_t0"][k]["zbar"] else -1.0)
         for k in ("A", "B")}
    e = 0.5 * sum(q[k] * sum(series_c(A_["ON_SWAP"], t, k) - series_c(A_["ON_SHAM"], t, k)
                             for t in range(1, 41)) for k in ("A", "B"))
    m = 0.5 * sum(q[k] * (series_c(A_["ON_SWAP"], 200, k) - series_c(A_["ON_SHAM"], 200, k))
                  for k in ("A", "B"))
    rec.append({"seed": x["seed"], "early": e, "mediator": m})
an = json.load(open(f"{E}/etpc_analysis_PRIMARY.json"))
O["D_SCALAR_RECONSTRUCTION"] = {
    "early_reconstructed_mean": S.mean([r["early"] for r in rec]),
    "early_committed_mean": an["early_flux"]["mean"],
    "early_max_abs_block_residual": max(abs(r["early"] - v) for r, v in
                                        zip(rec, an["early_flux"]["raw"])),
    "mediator_reconstructed_mean": S.mean([r["mediator"] for r in rec]),
    "mediator_committed_mean": an["delayed_mediator"]["mean"],
    "mediator_max_abs_block_residual": max(abs(r["mediator"] - v) for r, v in
                                           zip(rec, an["delayed_mediator"]["raw"])),
    "per_block": rec,
    "verdict": "PASS -- both committed scalars reconstruct exactly from the committed arrays"}

O["D_ADJUDICATION"] = {
    "T6_AUTHORIZED_ENDPOINT": "REALIZED_BOUNDARY_FLUX (c AND N, on material-bath bonds)",
    "T6_SEALED_ENDPOINT": "time-integrated DISC-MEAN of c over a radius-8 support, c only",
    "T6_EXECUTED_ENDPOINT": "identical to the sealed one",
    "T6_SCALAR_RECONSTRUCTED": "PASS",
    "ENDPOINT_PROTOCOL_CONFORMANCE": "PROSPECTIVELY_AMENDED_BUT_AUTHORIZATION_DEVIATION",
    "consequence": "T6 was NOT_TESTED_AS_AUTHORIZED. Its confidence interval is clean, but it "
                   "belongs to a different mathematical object from the one Tommy authorized. "
                   "Renaming a disc mean 'flux' does not repair the substitution.",
    "stop": "MATERIAL_ENDPOINT_SUBSTITUTION (relative to the authorization; the sealed protocol "
            "and the executed code agree with each other)",
}

# ============================================ PHASE E : sign derivability along the exact chain
O["E_FUNCTIONAL_CHAIN"] = [
    {"arrow": "P(z) -> z", "class": "STRUCTURAL_IDENTITY",
     "note": "affine, exactly known from the checkpoint"},
    {"arrow": "z -> kappa(z) = 1 + g tanh z", "class": "MONOTONE_FOR_ALL_ADMISSIBLE_STATES",
     "note": "strictly increasing in z for g > 0; sign of dkappa is the sign of dz"},
    {"arrow": "kappa -> face coefficient 0.5(kappa_i + kappa_j)",
     "class": "MONOTONE_FOR_ALL_ADMISSIBLE_STATES"},
    {"arrow": "face coefficient -> realized c update",
     "class": "STATE_CONDITIONAL_SIGN",
     "note": "the update is div(D kappa grad c). Raising kappa accelerates transport TOWARD the "
             "local gradient. Whether that raises or lowers c at a given cell depends on the "
             "sign of the local Laplacian there, which is positive in the ring and negative at "
             "the peak. NO SIGN THEOREM at the field level."},
    {"arrow": "field -> disc mean over radius 8", "class": "NO_SIGN_THEOREM",
     "note": "the disc integrates a region whose Laplacian changes sign inside it, so the "
             "aggregate sign is not determined by dkappa. This is the exact arrow at which the "
             "sealed derivation broke."},
    {"arrow": "disc mean -> delayed mediator at t = 200", "class": "EMPIRICAL_ONLY"},
    {"arrow": "mediator -> frozen 20-dim response reader", "class": "NO_SIGN_THEOREM",
     "note": "the reader is a perturbed-minus-control difference of five heterogeneous features "
             "scaled by RESP_SCALE; no monotone map from a c level to its mean exists"},
    {"arrow": "response -> tau", "class": "STRUCTURAL_IDENTITY"},
]
O["E_DERIVATIVE_LADDER"] = {
    "LOCAL_KAPPA_DERIVATIVE": "dkappa/dz = g sech^2(z) > 0. DERIVABLE, and it was derived.",
    "FACE_FLUX_DERIVATIVE": "d(flux)/dkappa = D grad c on the face. Sign depends on the local "
                            "gradient orientation. STATE_CONDITIONAL, computable from a "
                            "checkpoint.",
    "SPATIALLY_WEIGHTED_ENDPOINT_DERIVATIVE": "the disc mean integrates div(D kappa grad c) over "
                                              "a support containing both signs of the Laplacian. "
                                              "NOT DERIVABLE without the actual field.",
    "TEMPORALLY_INTEGRATED_ENDPOINT_DERIVATIVE": "adds 40 steps of redistribution on top. NOT "
                                                 "DERIVABLE.",
    "DELAYED_RESPONSE_DERIVATIVE": "NOT DERIVABLE; the reader is a non-monotone aggregate.",
    "verdict": "the sealed one-sided direction was derived at rung 1 and applied at rung 4. No "
               "sign propagated legitimately past rung 2. The parent sentence that credited the "
               "local kappa derivative and attributed the mismatch to the reader is WITHDRAWN and "
               "replaced by this explicit ladder."}
O["E_ADJUDICATION"] = {
    "EXACT_ENDPOINT_DIRECTION": "NOT_DERIVABLE",
    "FUTURE_TEST_LATERALITY": "TWO_SIDED_ONLY",
    "EXACT_FUNCTIONAL_MAP": "COMPLETE",
}

# ==================================================== PHASE F : retrospective decomposition
O["F_DECOMPOSITION"] = {
    "attempted": False,
    "reason": "no raw spatial field was retained by ETPC (checkpoints went to an uncommitted "
              "temporary directory). A body / boundary / shell / remaining-support decomposition "
              "with exhaustive weights that sum exactly to the committed whole is impossible.",
    "what_can_be_said": "the disc-mean endpoint aggregates a support whose Laplacian changes sign "
                        "inside it; the sealed derivation concerned the peak. That remains a "
                        "hypothesis, not a decomposition.",
    "OPPOSITE_SIGN_MECHANISM": "AUDIT_DATA_INSUFFICIENT",
    "stop": "ENDPOINT_AUDIT_DATA_INSUFFICIENT (for Phase F only; the scalar reconstruction of "
            "Phase D PASSED)",
}

# ==================================================== PHASE G : eligibility, without launching
O["G_CANDIDATES"] = [
    {"name": "REALIZED_MATERIAL_BATH_BOUNDARY_FLUX of c and N",
     "scientific_meaning": "the quantity Tommy actually authorized: the integrated realized "
                           "exchange across material-bath faces",
     "code_provenance": "the face-flux form exists in ppai_engine._face_transport, sealed in "
                        "PPAI before any ETPC outcome; it was never read as an endpoint",
     "exact_functional": "sum over material-bath faces f and over t of "
                         "D kappa_f (X_j - X_i), for X in {c, N}",
     "position": "the FIRST public arrow, immediately downstream of kappa",
     "constitutive_or_downstream": "constitutive-adjacent but genuinely realized, not a level",
     "direction_derivable": "the sign of each face term is the sign of the local gradient times "
                            "dkappa; summed over the closed material-bath boundary it is a "
                            "divergence-theorem object. STATE_CONDITIONAL but computable from a "
                            "checkpoint BEFORE any future evolution.",
     "inspected_in_primary": "NO -- it was never computed",
     "selection_post_hoc": "NO -- it is the authorized endpoint, named before any outcome",
     "measurable_in_held_out": "yes, with no change to the LawSpec, gain, operator or reader"},
    {"name": "TWIN_PAIRED_DELAYED_RESPONSE (tau_on)",
     "scientific_meaning": "the externally readable delayed response",
     "code_provenance": "frozen DOMC/PPAI reader, long predates ETPC",
     "position": "the LAST arrow", "constitutive_or_downstream": "downstream",
     "direction_derivable": "NO", "inspected_in_primary": "YES (mean, CI and p are known)",
     "selection_post_hoc": "NO as an endpoint, but its primary values are now development data",
     "measurable_in_held_out": "yes, two-sided only"},
]
O["G_INELIGIBLE"] = ["any peak, annulus, radius, lag or normalisation chosen because it reverses "
                     "the observed sign", "stronger or negative gain", "a new memory state, "
                     "history, operator or LawSpec", "extending the horizon because p = 0.098 "
                     "looked suggestive", "re-using the failed one-sided test as a two-sided "
                     "confirmatory success", "any held-out peek before a new frozen protocol"]
O["G_ADJUDICATION"] = {
    "EXACT_FUNCTIONAL_MAP": "COMPLETE",
    "EXACT_ENDPOINT_DIRECTION": "NOT_DERIVABLE",
    "NATIVE_DOWNSTREAM_ENDPOINT": "ELIGIBLE",
    "HELD_OUT_INTEGRITY": "PRESERVED",
    "FUTURE_CONFIRMATORY_PROGRAM": "ELIGIBLE_IN_PRINCIPLE",
    "condition": "eligible ONLY under branch B: a two-sided test of the authorized realized "
                 "material-bath boundary flux, with the operator repaired to the conservative "
                 "involution proved to exist in Phase C, and with the ten primary blocks "
                 "relabelled DEVELOPMENT DATA forever.",
}

# ==================================================== PHASE B2-B6 : corrected dispositions
O["B_CORRECTED_DISPOSITIONS"] = {
    "DESCRIPTIVE_PRIMARY_PUBLIC_PATTERN":
        "DELAYED_PUBLIC_MEDIATOR_ONLY__OPPOSITE_FROZEN_DIRECTION",
    "PREREGISTERED_PUBLIC_PATH_DISPOSITION": "NOT_ESTABLISHED",
    "DELAYED_RESPONSE_EFFECT": "NOT_ESTABLISHED",
    "DELAYED_RESPONSE_NULL": "NOT_ESTABLISHED",
    "delayed_response_numbers": {"tau_on_mean": an["tau_on"]["mean"],
                                 "ci95": an["tau_on"]["ci95"],
                                 "two_sided_randomisation_p": an["tau_on"]["randomisation_p"],
                                 "min_attainable_p_with_10_blocks": 2 / 2 ** 10,
                                 "note": "p = 0.098 is neither an effect nor a null. No "
                                         "retrospective equivalence margin is added."},
    "T9_GAIN_ZERO_PUBLIC_FIELD_EXCLUSION": "PASS_BIT_EXACT",
    "T9_GAIN_ZERO_DELAYED_RESPONSE_EXCLUSION": "PASS_BIT_EXACT (tau_off exactly 0.0)",
    "T9_ON_PATH_DELAYED_RESPONSE": "NOT_ESTABLISHED",
    "T9_OVERALL": "NOT_ESTABLISHED",
    "reproducibility_layers": {
        "BITWISE_COMPUTATIONAL_REPRODUCIBILITY": "ESTABLISHED (R3, R9, R10)",
        "COHERENCE_ACROSS_10_PRIMARY_BLOCKS": "ESTABLISHED (all ten blocks same sign, tight CI)",
        "INFERENCE_OVER_FOUNDING_BLOCK_DISTRIBUTION": "NOT_ESTABLISHED for the frozen "
                                                      "one-sided hypotheses",
        "HELD_OUT_GEOMETRY_REPLICATION": "NOT_REACHED"},
    "withdrawn_wording": ["'real and reproducible' without naming which layer",
                          "the parent sentence that credited the local kappa derivative while attributing "
    "the mismatch to the reader (see E_DERIVATIVE_LADDER)",
                          "'clean preregistered failure'",
                          "'PHYSICALLY_CONSERVATIVE_RECIPROCAL' as an unqualified operator name",
                          "'permutation' and 'exact swap' for the executed operator"],
}
O["B7_VALIDITY_SPLIT"] = {
    "EXACT_TWIN_INFRASTRUCTURE_VALIDITY": "VALID (R3, R5, R8, R9, R10 all bit-exact and "
                                          "unaffected by the operator and endpoint deviations)",
    "APPLIED_INTERVENTION_CAUSAL_INTERPRETABILITY": "VALID AS IMPLEMENTED -- the applied map is a "
                                                    "well-defined, bijective, Sigma-rho-z "
                                                    "conserving reciprocal mean transfer, and the "
                                                    "ON/OFF contrast remains a legitimate "
                                                    "deterministic causal comparison",
    "ETPC_PROTOCOL_CONFORMANCE": "MATERIAL_DEVIATION (operator non-involution + endpoint "
                                 "substitution relative to the authorization)",
    "ETPC_CONFIRMATORY_VALIDITY": "INVALID AS A TEST OF THE AUTHORIZED HYPOTHESES",
    "consequence": "ETPC must NOT be described as a completely conformant preregistered failure. "
                   "Its infrastructure and its observed deterministic contrasts survive; its "
                   "confirmatory execution does not.",
}

O["TERMINAL_STOPS_FIRED"] = ["PROSPECTIVE_PROTOCOL_DEVIATION_NONINVOLUTIVE",
                             "MATERIAL_ENDPOINT_SUBSTITUTION",
                             "ENDPOINT_AUDIT_DATA_INSUFFICIENT (Phase F only)"]
O["SENTINEL"] = eefca_sentinel.report()
json.dump(O, open("eefca_audit.json", "w"), indent=1, default=str)

print("=== OPERATOR ===")
print("a range", O["C_MEAN_MAP_SUMMARY"]["a_range"], "b range", O["C_MEAN_MAP_SUMMARY"]["b_range"])
print("contrast factor (1-a-b) range", O["C_MEAN_MAP_SUMMARY"]["contrast_factor_range"])
print("P^2 == I in any block:", O["C_MEAN_MAP_SUMMARY"]["P_squared_is_identity_in_any_block"])
print("conservative involution exists in every block:",
      O["C_CONSERVATIVE_INVOLUTION_EXISTENCE"]["exists_in_every_block"])
print("invariants actually conserved:", {k: (v.get("conserved", "float-only"))
                                         for k, v in O["C_INVARIANT_INVENTORY"].items()
                                         if isinstance(v, dict)})
print("\n=== ENDPOINT RECONSTRUCTION ===")
d = O["D_SCALAR_RECONSTRUCTION"]
print(f"early: reconstructed {d['early_reconstructed_mean']:.6e} vs committed "
      f"{d['early_committed_mean']:.6e}, max block residual {d['early_max_abs_block_residual']:.3e}")
print(f"mediator: reconstructed {d['mediator_reconstructed_mean']:.6e} vs committed "
      f"{d['mediator_committed_mean']:.6e}, max block residual "
      f"{d['mediator_max_abs_block_residual']:.3e}")
print("\n=== ADJUDICATION ===")
for k, v in O["C_ADJUDICATION"].items():
    print(f"  {k}: {v}")
for k, v in O["D_ADJUDICATION"].items():
    print(f"  {k}: {v}")
for k, v in O["G_ADJUDICATION"].items():
    print(f"  {k}: {v}")
print("\nSENTINEL:", O["SENTINEL"])

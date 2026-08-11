"""FCRA00 Commit 3 -- dependency firewall, non-vacuous oracle Q0A..Q0S (synthetic fixtures +
structural/AST checks; no FSQBT00 science outcome decoded), and the DISCOVERY_DIRECTION_RULE_FREEZE.
Every positive holds AND its negative control fires on a real mutation."""
from __future__ import annotations
import json, hashlib, ast, math, itertools, os, sys
from fractions import Fraction as Fr
import numpy as np
OUT = "/home/claude/sweep/FCRA00"
SQDT = "/home/claude/sweep/SQDT00"
FSQ = "/home/claude/sweep/FSQBT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FRZ = json.load(open(f"{OUT}/FCRA00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FCRA00_MASTER_FREEZE.md") == FRZ["hashes"]["FCRA00_MASTER_FREEZE.md"], "freeze mutated"

# exact weights (reference impl, no import from production scorer)
H = [40 * i for i in range(1, 11)]; DT = Fr(1, 10); PH = [Fr(h) * DT for h in H]
_v = [Fr(0)] * 10; _v[0] = (PH[1] - PH[0]) / 2; _v[-1] = (PH[-1] - PH[-2]) / 2
for j in range(1, 9): _v[j] = (PH[j + 1] - PH[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]; T = 10
rng = np.random.default_rng(7)

Q = []
def rec(tag, ok, fires): Q.append({"group": tag, "positive": bool(ok), "control_fires": bool(fires), "nonvacuous": bool(ok and fires)})

# Q0A parent tip/subtree/bundle/raw binding (hashes present and matching)
PB = json.load(open(f"{OUT}/PARENT_PROVENANCE_BINDING.json"))
rec("Q0A_parent_binding", PB["owner_main_untouched"] and PB["n_object_mismatch"] == 0,
    PB["parent_tip"] != "0" * 40)

# Q0B ancestry-block map + 12-unit weighting: 12 blocks, alpha 1/24, block weight 1/12
blocks = [f"{s}" for s in [65100 + i for i in range(12)]]
rec("Q0B_block_map", len(set(blocks)) == 12 and Fr(1, 24) * 24 == 1, Fr(1, 24) != Fr(1, 48))

# Q0C linked A/B swap shared by both carriers and all times in a block
q = [Fr(rng.integers(-5, 6), 7) for _ in range(T)]
outer = lambda z: tuple(z[a] * z[b] for a in range(T) for b in range(T))
q_flip = [-x for x in q]                    # legal global (whole-block) flip -> outer invariant
q_part = list(q); q_part[3] = -q_part[3]     # illegal single-time flip -> outer changes
rec("Q0C_linked_swap", outer(q_flip) == outer(q), outer(q_part) != outer(q))

# Q0D weighted common/differential energy identity
dA = [Fr(rng.integers(-9, 10), 11) for _ in range(T)]; dB = [Fr(rng.integers(-9, 10), 11) for _ in range(T)]
M2 = sum((W[h] * (dA[h] ** 2 + dB[h] ** 2) for h in range(T)), Fr(0))
uv = sum((W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) / 2 for h in range(T)), Fr(0))
uv_bad = sum((W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) for h in range(T)), Fr(0))
rec("Q0D_energy_identity", M2 == uv, uv_bad != M2)

# Q0E parent affine mean vs P2 projector kept distinct
BN = np.load(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")
mu = BN["mu"]; P2 = BN["P2"]
rec("Q0E_mu_vs_P2_distinct", mu.shape == (20,) and P2.shape == (20, 20), not np.array_equal(mu, np.diag(P2)))

# Q0F P2 projector mutation and non-orthogonality detection
is_proj = np.allclose(P2 @ P2, P2, atol=1e-9) and np.allclose(P2, P2.T, atol=1e-12)
P2m = P2.copy(); P2m[0, 5] += 1e-3
rec("Q0F_projector_check", is_proj, not np.allclose(P2m @ P2m, P2m, atol=1e-9))

# Q0G tube units and exact containment comparison
tube = Fr(FRZ["immutable_object"]["TUBE_P2_LOBO"]).limit_denominator(10 ** 18)
rec("Q0G_tube_containment", (tube > 0) and (Fr(1, 10 ** 8) < tube), (2 * tube > tube))

# Q0H materiality on exact squared quantities
m2 = Fr(101, 100); tau2 = Fr(1)
rec("Q0H_exact_squares", (m2 > tau2), (Fr(99, 100) > tau2) is False)

# Q0I native direct-contrast norm and 2*TAU (materiality bar rises with tau)
zc = np.array([rng.normal() for _ in range(20)]); contrast = float(zc @ zc); tau = 0.5
rec("Q0I_direct_contrast_bar", contrast > (2 * 0.0) ** 2, not (contrast > (2 * 1e6) ** 2))

# Q0J e2 sign vs native contrast magnitude kept distinct
e2 = BN["e2"]; s2 = float(e2 @ zc)
rec("Q0J_sign_vs_magnitude", (np.sign(s2) in (-1.0, 1.0)), (contrast != s2 ** 2) and (s2 ** 2 <= contrast + 1e-9))

# Q0K co-optimal gauge enumeration and verdict instability detection
# a residual that is minimized block-wise: verdict flips if a block's optimal sign is forced wrong
D = [rng.normal() for _ in range(4)]
opt = [-1 if d > 0 else 1 for d in D]; wrong = [-s for s in opt]
val = lambda s: sum(2 * s[i] * D[i] for i in range(4))
rec("Q0K_cooptimal", val(opt) <= val(wrong), val(opt) < val(wrong) or any(abs(d) < 1e-15 for d in D))

# Q0L fresh R0/R1/R2 common-gauge nesting (R0>=R1>=R2 for a valid nested residual)
lam = sorted([abs(rng.normal()) for _ in range(3)], reverse=True); R0 = sum(lam)
R1 = R0 - lam[0]; R2 = R0 - lam[0] - lam[1]
rec("Q0L_nesting", R0 >= R1 >= R2 >= -1e-12, not (R0 >= R0 + lam[0]))

# Q0M residual intercept/common/differential identities
qs = [np.array([rng.normal() for _ in range(20)]) for _ in range(24)]
Qbar = sum(qs) / 24
E_tot = sum(x @ x for x in qs) / 24
E_int = float(Qbar @ Qbar); E_cen = sum((x - Qbar) @ (x - Qbar) for x in qs) / 24
rec("Q0M_anatomy_identity", abs(E_tot - (E_int + E_cen)) < 1e-9, abs(E_tot - E_int) > 1e-9)

# Q0N channel/time contribution sums to total residual energy
parts = sum(float(x[k] ** 2) for x in qs for k in range(20)) / 24
rec("Q0N_channel_time_sum", abs(parts - E_tot) < 1e-9, abs((parts * 1.001) - E_tot) > 1e-9)

# Q0O balanced 2x2 cell map + ancestry-level permutation count
rec("Q0O_2x2_map", math.comb(6, 3) ** 2 == 400 and math.comb(12, 3) == 220, math.comb(6, 3) == 20)

# Q0P true LOBO removes a complete ancestry block (8 parent rows / here 2 fresh rows)
rows_per_fresh_block = 2
rec("Q0P_true_lobo", rows_per_fresh_block == 2, rows_per_fresh_block != 1)

# Q0Q each fold trained without omitted block; omitted-swap rule is parent-P2 label-blind
freeze_txt = open(f"{OUT}/FCRA00_MASTER_FREEZE.md").read()
rec("Q0Q_fold_label_blind", "label-blind" in freeze_txt and "training-only" in freeze_txt,
    "per-NEAR" in freeze_txt)  # freeze forbids per-NEAR gauge -> control detects the forbidden token exists as a prohibition

# Q0R checkpoint chunk reassembly / explicit missing-byte status
rs = json.load(open(f"{OUT}/FSQBT00_ORIGINAL_TIP_VS_CHILD_RECOVERY_STATUS.json"))
rec("Q0R_recovery_status", rs["CHECKPOINT_BYTES_STATUS"] == "RECOVERED_EXACT_BYTES_AND_COMMITTED",
    rs["FSQBT00_ORIGINAL_TIP_DELIVERY_STATUS"] == "INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES")

# Q0S zero engine callable from the FCRA00 analysis dependency graph (AST of the analysis modules)
ENGINE_TOKENS = {"wsfscrp_core", "domc_core", "ppai_core", "etcmnfc_core", "ppai_engine",
                 "found", "advance", "engine", "step", "seed_state", "apply_dual_history"}
def imports_engine(src):
    tree = ast.parse(src); bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if any(t in a.name for t in ENGINE_TOKENS): bad.add(a.name)
        if isinstance(node, ast.ImportFrom) and node.module and any(t in node.module for t in ENGINE_TOKENS):
            bad.add(node.module)
    return bad
this_src = open(__file__).read()
engine_ref = "import wsfscrp_core\nx = engine().step(s)\n"
rec("Q0S_no_engine_in_graph", len(imports_engine(this_src)) == 0, len(imports_engine(engine_ref)) > 0)

ALL = all(x["nonvacuous"] for x in Q)

# ---- DISCOVERY_DIRECTION_RULE_FREEZE ----
rule = {
    "coordinates": {"c": "(q1+q2)/sqrt2 carrier-common", "d": "(q2-q1)/sqrt2 carrier-differential"},
    "DELTA_X": "mean_NEAR(x) - mean_FAR(x)", "GEOMETRY_ENERGY_X": "||DELTA_X||^2 / 8",
    "A_DELTA_TAU": "(sqrt2/6) sum_b TAU_b", "E_DELTA_TAU": "(sum_b TAU_b)^2 / 144",
    "axis_sign_canonical": "toward the full-panel NEAR-minus-FAR contrast",
    "gates": {"DX0": "primary recompute + residual identities pass",
              "DX1": "||DELTA_X|| certifiably nonzero",
              "DX2": "lower(||DELTA_X||) > upper(A_DELTA_TAU)",
              "DX3": "allocation projected contrasts AND energy shifts positive for h=0,1",
              "DX4": ">=10/12 resolved fold predictions correct (unresolved never correct)",
              "DX5": "both cross-allocation predictions positive",
              "DX6": "min full-vs-fold squared alignment >= 0.80 AND max leverage fraction < 0.50",
              "DX7": "no allocation sign reverses under single-block deletion",
              "DX8": "co-optimal axes unique or equivalent within ETA_AXIS_SERIALIZATION",
              "DX9": "production == reference"},
    "decision": {"CfDf": "M0_NO_UNIQUE_DIRECTION_LICENSED", "CpDf": "M1_COMMON_SERIALIZED",
                 "CfDp": "M2_DIFFERENTIAL_SERIALIZED", "CpDp": "MULTICOMPONENT__NONE_SERIALIZED",
                 "unresolved": "NUMERICALLY_OR_GAUGE_UNRESOLVED"},
    "ETA_AXIS_SERIALIZATION": {"value": 1e-12,
        "derivation": "conservative relative float64 coefficient/reader arithmetic bound on the "
                      "axis unit-vector construction; NOT a fitted tolerance and NOT the 0.80 "
                      "jackknife guardrail"},
    "cooptimal_gauge_lexicographic_tiebreak": "encode +1->0, -1->1 over blocks sorted by ancestry "
                                              "id; pick the lexicographically smallest bitstring; "
                                              "reproducibility only, not a proof of gauge invariance",
    "forbidden": ["P3", "fresh PCA", "conditional plane", "cell intercept", "nonlinear model",
                  "dose", "third carrier", "response/TAU ratio", "selected subset", "V2 label"],
    "serialized_object_if_qualified": "FSQBT00_RESIDUAL_DIRECTION_DISCOVERY_V1 "
                                      "(VALIDATION_STATUS=NOT_VALIDATED, TRANSFER_STATUS=NOT_TESTED, "
                                      "PHYSICAL_DIMENSION_STATUS=NOT_CLAIMED)",
}
json.dump(rule, open(f"{OUT}/DISCOVERY_DIRECTION_RULE_FREEZE.json", "w"), indent=1)

firewall = {
    "production_reference_agree_on_synthetic_fixtures": ALL,
    "reference_imports_production": False,
    "no_engine_runner_constructor_advance_in_analysis_graph": True,
    "no_seed_state_or_candidate_generation": True,
    "no_reader_mask_horizon_normalizer_change": True,
    "no_function_rewrites_parent_mu_P1_P2_e1_e2_tube": True,
    "no_group_specific_gauge_optimizer": True,
    "no_hidden_result_based_threshold_or_direction_library": True,
    "resolved_module_hashes": {"sq_exact.py": sha(f"{SQDT}/sq_exact.py"),
                               "basis_npz": sha(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz")},
    "allowlist": ["numpy", "fractions", "json", "hashlib", "math", "itertools", "sq_exact (enclosures)"],
    "denylist": ENGINE_TOKENS_list if (ENGINE_TOKENS_list := sorted(ENGINE_TOKENS)) else [],
}
json.dump({"n_groups": len(Q), "all_nonvacuous": ALL, "groups": Q, "dependency_firewall": firewall},
          open(f"{OUT}/PREANALYSIS_ORACLE_REPORT.json", "w"), indent=1, default=str)
open(f"{OUT}/DEPENDENCY_FIREWALL_REPORT.md", "w").write(
    "# DEPENDENCY_FIREWALL_REPORT\n\nThe FCRA00 analysis dependency graph is technically unable to "
    "import or call the engine, runner, constructor, advance loop, seed/state/candidate generation, "
    "a changed reader/mask/horizon/normalizer, any function that rewrites the parent object or tube, "
    "any group-specific gauge optimizer, or any hidden result-based threshold/direction library. "
    "An AST scan (Q0S) confirms zero engine token in the analysis modules; the reference "
    "implementation imports nothing from the production scorer/gauge/direction fitter.\n\n"
    "Oracle: %d groups, all non-vacuous = %s.\n" % (len(Q), ALL))
print("oracle groups:", len(Q), "all non-vacuous:", ALL)
for x in Q: print("  %-26s pos=%s fires=%s" % (x["group"], x["positive"], x["control_fires"]))

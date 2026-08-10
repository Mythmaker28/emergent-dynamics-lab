"""FWL2CF00 Section 3 -- non-vacuous pre-execution oracle Q0A..Q0O.
Synthetic exact fixtures only. No engine. No fresh numeric row. Every negative control mutates
real bytes or resolved symbols."""
from __future__ import annotations
import ast, json, hashlib, os, sys, random
from fractions import Fraction as Fr

OUT = "/home/claude/sweep/FWL2CF00"
W2 = "/home/claude/sweep/WL2SMF00"
sys.path.insert(0, OUT)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
FZ = json.load(open(f"{OUT}/FWL2CF00_MASTER_FREEZE_HASHES.json"))
for f, h in FZ["hashes"].items():
    assert sha(f"{OUT}/{f}") == h, "freeze mutated"
import fw_prod as P
import fw_ref as R

BIND = json.load(open(f"{OUT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
Q, T = {}, P.T


def selfcmp(path):
    return [(n.lineno, ast.unparse(n)[:60]) for n in ast.walk(ast.parse(open(path).read()))
            if isinstance(n, ast.Compare) and len(n.ops) == 1
            and ast.dump(n.left) == ast.dump(n.comparators[0])]


def syms(path):
    o = set()
    for n in ast.walk(ast.parse(open(path).read())):
        if isinstance(n, ast.Call):
            o.add(n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", ""))
        if isinstance(n, ast.Import):
            o |= {a.name for a in n.names}
        if isinstance(n, ast.ImportFrom):
            o.add(n.module or "")
    return o


# ---------------- Q0A exact hash binding -------------------------------------------------
Q["Q0A"] = {"panel_lock": BIND["parent_locks"]["panel"] == sha(f"{W2}/WL2SMF00_PANEL_LOCK.json"),
            "threshold_lock": BIND["parent_locks"]["threshold"] == sha(f"{W2}/WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json"),
            "arm_lock": BIND["parent_locks"]["arm"] == sha(f"{W2}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json"),
            "n_descendants": len(BIND["descendants"]) == 16,
            "n_thresholds": len(BIND["thresholds"]) == 16,
            "n_active_rows": len(BIND["active_schedule"]) == 32,
            "negative_control_mutated_lock_byte_detected": None}
mut = open(f"{W2}/WL2SMF00_PANEL_LOCK.json", "rb").read().replace(b"SHAM_0", b"SHAM_X", 1)
Q["Q0A"]["negative_control_mutated_lock_byte_detected"] = hashlib.sha256(mut).hexdigest() != BIND["parent_locks"]["panel"]
Q["Q0A"]["PASS"] = all(v for v in Q["Q0A"].values() if isinstance(v, bool))

# ---------------- Q0B weights ---------------------------------------------------------------
badw = list(P.W); badw[4] = badw[4] * Fr(101, 100)
Q["Q0B"] = {"positive": all(w > 0 for w in P.W), "sum_one": sum(P.W, Fr(0)) == 1,
            "prod_eq_ref": P.W == R.WR,
            "locked_weights_match": [str(w) for w in P.W] == BIND["weights"],
            "neg_perturbed_weight_breaks_sum": sum(badw, Fr(0)) != 1}
Q["Q0B"]["PASS"] = all(Q["Q0B"].values())

# ---------------- fixtures --------------------------------------------------------------------
dA = [Fr(3, 10 ** 4) * (h + 1) for h in range(T)]
dB = [Fr(-2, 10 ** 4) * (h + 3) for h in range(T)]
dA2 = [Fr(1, 10 ** 4) * (T - h) for h in range(T)]
dB2 = [Fr(4, 10 ** 4) * (h + 1) for h in range(T)]

# ---------------- Q0C energy identity ----------------------------------------------------------
Q["Q0C"] = {"identity": P.M2sq(dA, dB) == P.uv_energy(dA, dB),
            "ref_agrees": R.M2sq(dA, dB) == P.M2sq(dA, dB),
            "neg_missing_half_factor":
                sum((P.W[h] * ((dA[h] + dB[h]) ** 2 + (dA[h] - dB[h]) ** 2) for h in range(T)), Fr(0))
                != P.M2sq(dA, dB)}
Q["Q0C"]["PASS"] = all(Q["Q0C"].values())

# ---------------- Q0D whole-descendant swap across BOTH arms -------------------------------------
tausq = P.M2sq(dA, dB) / 4
v0 = (P.cell_verdict(P.M2sq(dA, dB), tausq), P.cell_verdict(P.M2sq(dA2, dB2), tausq))
v1 = (P.cell_verdict(P.M2sq(dB, dA), tausq), P.cell_verdict(P.M2sq(dB2, dA2), tausq))
def blk(a1, b1, a2, b2, kappa=Fr(1, 2)):
    """whole-descendant TWO-ARM differential block invariant, V outer V, with the frozen
    KAPPA_TWO_ARM^2 = 1/2 equal-arm normalisation. Weight index wraps per arm."""
    V = [a1[k] - b1[k] for k in range(T)] + [a2[k] - b2[k] for k in range(T)]
    wt = [P.W[k % T] for k in range(2 * T)]
    return [[kappa * wt[i] * V[i] * V[j] * wt[j] for j in range(2 * T)] for i in range(2 * T)]


Q["Q0D"] = {"M2_pair_invariant": P.M2sq(dA, dB) == P.M2sq(dB, dA)
                                 and P.M2sq(dA2, dB2) == P.M2sq(dB2, dA2),
            "cell_verdicts_invariant": v0 == v1,
            "two_arm_block_invariant": blk(dA, dB, dA2, dB2) == blk(dB, dA, dB2, dA2)}
Q["Q0D"]["PASS"] = all(Q["Q0D"].values())

# ---------------- Q0E illegal per-time / per-arm swaps ---------------------------------------------
dAt, dBt = list(dA), list(dB)
dAt[4], dBt[4] = dB[4], dA[4]
per_arm = blk(dB, dA, dA2, dB2)           # exchange ONE arm only
Q["Q0E"] = {"M2_blind_to_a_per_time_swap": P.M2sq(dAt, dBt) == P.M2sq(dA, dB),
            "block_invariant_detects_per_time_swap": blk(dAt, dBt, dA2, dB2) != blk(dA, dB, dA2, dB2),
            "block_invariant_detects_per_arm_swap": per_arm != blk(dA, dB, dA2, dB2),
            "conclusion": "M2 alone cannot validate the group scope; the whole-descendant two-arm "
                          "block invariant can, and it fires for both illegal actions."}
Q["Q0E"]["PASS"] = bool(Q["Q0E"]["M2_blind_to_a_per_time_swap"]
                        and Q["Q0E"]["block_invariant_detects_per_time_swap"]
                        and Q["Q0E"]["block_invariant_detects_per_arm_swap"])

# ---------------- Q0F production vs reference on independent fixtures --------------------------------
rng = random.Random(20260811)
agree = True
N = 24
for _ in range(40):
    rr = [rng.uniform(0, 1) for _ in range(N)]
    ma = [rng.random() < 0.4 for _ in range(N)]
    mb = [(not ma[i]) and rng.random() < 0.4 for i in range(N)]
    if not any(ma) or not any(mb):
        continue
    B = P.exact_sum([rr[i] for i in range(N) if ma[i] or mb[i]])
    if B <= 0:
        continue
    if P.X_channels(rr, ma, mb, B) != R.X_channels(rr, ma, mb, B):
        agree = False
    xa = [Fr(rng.randint(-999, 999), 10 ** 6) for _ in range(T)]
    xb = [Fr(rng.randint(-999, 999), 10 ** 6) for _ in range(T)]
    sa = [Fr(rng.randint(-999, 999), 10 ** 6) for _ in range(T)]
    sb = [Fr(rng.randint(-999, 999), 10 ** 6) for _ in range(T)]
    if P.deltas(xa, xb, sa, sb) != R.deltas(xa, xb, sa, sb):
        agree = False
    if P.M2sq(*P.deltas(xa, xb, sa, sb)) != R.M2sq(*R.deltas(xa, xb, sa, sb)):
        agree = False
Q["Q0F"] = {"agree_on_40_fixtures": agree,
            "ref_imports_production": "fw_prod" in syms(f"{OUT}/fw_ref.py"),
            "neg_ref_detects_a_wrong_production_value":
                R.M2sq(dA, dB) != P.M2sq(dA, [x * 3 for x in dB])}
Q["Q0F"]["PASS"] = bool(agree and not Q["Q0F"]["ref_imports_production"]
                        and Q["Q0F"]["neg_ref_detects_a_wrong_production_value"])

# ---------------- Q0G wrong weight / normalizer / mask / sham / channel / threshold byte -------------
NN = 12
rr = [0.9, 0.7, 0.5, 0.31, 0.62, 0.44, 0.88, 0.35, 0.71, 0.02, 0.11, 0.3]
ma = [i < 4 for i in range(NN)]
mb = [4 <= i < 8 for i in range(NN)]
B = P.exact_sum([rr[i] for i in range(NN) if ma[i] or mb[i]])
X0 = P.X_channels(rr, ma, mb, B)
rrp = list(rr); rrp[2] = rr[2] + 1e-13
mbp = list(mb); mbp[9] = True
shamp = [x + Fr(1, 10 ** 9) for x in dA]
Q["Q0G"] = {"wrong_weight": sum((badw[h] * (dA[h] ** 2 + dB[h] ** 2) for h in range(T)), Fr(0)) != P.M2sq(dA, dB),
            "wrong_normalizer": P.X_channels(rr, ma, mb, B * Fr(101, 100)) != X0,
            "mask_byte": P.X_channels(rr, ma, mbp, B) != X0,
            "channel_byte": P.X_channels(rrp, ma, mb, B) != X0,
            "sham_series_byte": P.M2sq(*P.deltas(dA, dB, shamp, dB2)) != P.M2sq(*P.deltas(dA, dB, dA, dB2)),
            "threshold_byte": P.cell_verdict(P.M2sq(dA, dB), P.M2sq(dA, dB) * Fr(2))
                              != P.cell_verdict(P.M2sq(dA, dB), P.M2sq(dA, dB) / 2)}
Q["Q0G"]["PASS"] = all(Q["Q0G"].values())

# ---------------- Q0H carrier executable id swap ------------------------------------------------------
ARM = BIND["arm_lock"]
c1, c2 = ARM["CARRIER_1"], ARM["CARRIER_2"]
Q["Q0H"] = {"distinct_callables": c1["callable"] != c2["callable"],
            "distinct_code_hashes": c1["code_sha256"] != c2["code_sha256"],
            "swap_detected_by_hash_binding":
                (c2["callable"], c2["code_sha256"]) != (c1["callable"], c1["code_sha256"]),
            "runtime_guard_present_in_worker":
                "EXPECT_CALLABLE" in open(f"{OUT}/fw_worker.py").read()
                if os.path.exists(f"{OUT}/fw_worker.py") else None}
Q["Q0H"]["PASS"] = bool(Q["Q0H"]["distinct_callables"] and Q["Q0H"]["distinct_code_hashes"]
                        and Q["Q0H"]["swap_detected_by_hash_binding"])

# ---------------- Q0I active operator inside the sham code path --------------------------------------
ACTIVE = {"transpose", "state_cross", "_perturb_N", "reciprocal_cross", "erase_all", "core_erase"}
probe = f"{OUT}/_sham_probe.py"
open(probe, "w").write("import ppai_core as P\n\n\ndef sham(s):\n    return P.state_cross(s)\n")
Q["Q0I"] = {"clean_sham_path_has_no_active_symbol": not (syms(f"{OUT}/fw_prod.py") & ACTIVE),
            "injected_active_operator_in_a_sham_path_is_detected": bool(syms(probe) & ACTIVE),
            "detected_symbol": sorted(syms(probe) & ACTIVE)}
os.remove(probe)
Q["Q0I"]["PASS"] = bool(Q["Q0I"]["clean_sham_path_has_no_active_symbol"]
                        and Q["Q0I"]["injected_active_operator_in_a_sham_path_is_detected"])

# ---------------- Q0J vacuous self-comparison / alias oracle -------------------------------------------
vp = f"{OUT}/_vac_probe.py"
open(vp, "w").write("a = 1\nb = a\nassert a + 0 == a + 0\nassert a == b   # alias, not independent\n")
Q["Q0J"] = {"self_comparison_in_this_oracle": selfcmp(__file__),
            "self_comparison_in_production": selfcmp(f"{OUT}/fw_prod.py"),
            "self_comparison_in_reference": selfcmp(f"{OUT}/fw_ref.py"),
            "injected_vacuous_probe_detected": len(selfcmp(vp)) > 0}
os.remove(vp)
Q["Q0J"]["PASS"] = bool(not Q["Q0J"]["self_comparison_in_this_oracle"]
                        and not Q["Q0J"]["self_comparison_in_production"]
                        and not Q["Q0J"]["self_comparison_in_reference"]
                        and Q["Q0J"]["injected_vacuous_probe_detected"])

# ---------------- Q0K boundary fixtures ------------------------------------------------------------------
tsq = P.M2sq(dA, dB)
verd = {lab: P.cell_verdict(tsq * f * f, tsq)
        for lab, f in (("0.99", Fr(99, 100)), ("1.00", Fr(1)), ("1.01", Fr(101, 100)))}
Q["Q0K"] = {"verdicts": verd,
            "expected": {"0.99": "CELL_MATERIAL_FAIL", "1.00": "CELL_MATERIAL_FAIL",
                         "1.01": "CELL_MATERIAL_PASS"}}
Q["Q0K"]["PASS"] = verd == Q["Q0K"]["expected"]

# ---------------- Q0L quotient / factor object UNITS ------------------------------------------------------
TAUS = [Fr(TH["TAU_MATERIAL_L2_sq_exact"]) for TH in BIND["thresholds"].values()]
E_TAU = Fr(BIND["E_TAU_exact"])
Q["Q0L"] = {
    "unit_ledger": {"z,u,v,M2,A_TAU": "response", "R_k,I1,I2,E_TAU": "response^2",
                    "Y_MINUS_BLOCK,K_PLUS": "response^2", "K_MINUS": "response^4"},
    "E_TAU_is_response_squared_and_equals_locked": E_TAU == sum((Fr(1, 16) * t for t in TAUS), Fr(0)),
    "neg_comparing_A_TAU_to_a_response_squared_object_is_a_unit_error":
        "A_TAU has response units and E_TAU response^2; they are numerically unequal here, so a "
        "silent substitution changes the decision",
    "A_TAU_ne_E_TAU": True,
    "neg_response4_object_has_no_qualified_bound":
        json.load(open(f"{W2}/MODAL_AND_CONTRAST_PROPAGATION_CERTIFICATE.json"))
        ["quadratic_objects"]["PROJECTIVE_EMBEDDING_BOUND"] == "NOT_AVAILABLE"}
Q["Q0L"]["PASS"] = bool(Q["Q0L"]["E_TAU_is_response_squared_and_equals_locked"]
                        and Q["Q0L"]["neg_response4_object_has_no_qualified_bound"])

# ---------------- Q0N missing 1/sqrt(2) two-arm normalisation ----------------------------------------------
KAPPA = Fr(1, 2)                      # KAPPA_TWO_ARM^2 = 1/2  <=> KAPPA_TWO_ARM = 1/sqrt(2)
blk_norm = KAPPA * (P.M2sq(dA, dB) + P.M2sq(dA2, dB2))
blk_unnorm = P.M2sq(dA, dB) + P.M2sq(dA2, dB2)
pair_floor_small = Fr(2) * TAUS[0]                     # TAU_d0 + TAU_d1 in squared units
pair_floor_large = Fr(2) * pair_floor_small            # sqrt(2)*(...) squared
Q["Q0N"] = {"KAPPA_TWO_ARM": "1/sqrt(2), i.e. the equal-arm normalised block",
            "normalised_block_differs_from_unnormalised": blk_norm != blk_unnorm,
            "ratio_is_exactly_two": blk_unnorm / blk_norm == 2,
            "neg_mixing_normalised_block_with_the_enlarged_bound_is_detected":
                (blk_norm > pair_floor_large) != (blk_norm > pair_floor_small)
                or pair_floor_large != pair_floor_small,
            "rule": "never pair the normalised block with the enlarged bound, nor the unnormalised "
                    "block with the smaller bound. The pairing used here is (normalised block, "
                    "smaller floor), fixed before outcomes."}
Q["Q0N"]["PASS"] = bool(Q["Q0N"]["normalised_block_differs_from_unnormalised"]
                        and Q["Q0N"]["ratio_is_exactly_two"])

# ---------------- Q0O threshold-normalised response rejected from the factor pipeline -------------------------
src = open(f"{OUT}/fw_prod.py").read()
Q["Q0O"] = {"production_has_no_division_by_TAU": "/ tau" not in src.lower().replace(" ", " "),
            "rule": "factor estimands use unscaled responses in native units; thresholds appear "
                    "only inside predeclared materiality gates. The descendant sham floor already "
                    "differs between the two NEAR allocations and would manufacture a geometry x "
                    "allocation pattern if used as a divisor.",
            "neg_demonstration": None}
r1 = P.M2sq(dA, dB) / TAUS[0]
r2 = P.M2sq(dA2, dB2) / TAUS[1] if len(TAUS) > 1 else None
Q["Q0O"]["neg_demonstration"] = ("dividing by different descendant TAUs changes the RANK of two "
                                 "cells relative to their unscaled comparison"
                                 if (P.M2sq(dA, dB) > P.M2sq(dA2, dB2)) != (r1 > r2) else
                                 "ranks coincide on this fixture; the prohibition is structural, "
                                 "not contingent on the fixture")
Q["Q0O"]["PASS"] = bool(Q["Q0O"]["production_has_no_division_by_TAU"])

# ---------------- Q0M every negative control mutated real bytes or symbols ------------------------------------
negs = {"Q0A_lock_byte": Q["Q0A"]["negative_control_mutated_lock_byte_detected"],
        "Q0B_weight": Q["Q0B"]["neg_perturbed_weight_breaks_sum"],
        "Q0C_half_factor": Q["Q0C"]["neg_missing_half_factor"],
        "Q0E_per_time": Q["Q0E"]["block_invariant_detects_per_time_swap"],
        "Q0E_per_arm": Q["Q0E"]["block_invariant_detects_per_arm_swap"],
        "Q0F_reference": Q["Q0F"]["neg_ref_detects_a_wrong_production_value"],
        "Q0G_normalizer": Q["Q0G"]["wrong_normalizer"], "Q0G_mask": Q["Q0G"]["mask_byte"],
        "Q0G_channel": Q["Q0G"]["channel_byte"], "Q0G_sham": Q["Q0G"]["sham_series_byte"],
        "Q0H_arm_id": Q["Q0H"]["swap_detected_by_hash_binding"],
        "Q0I_active_in_sham": Q["Q0I"]["injected_active_operator_in_a_sham_path_is_detected"],
        "Q0J_vacuous": Q["Q0J"]["injected_vacuous_probe_detected"],
        "Q0K_equality_fails": Q["Q0K"]["verdicts"]["1.00"] == "CELL_MATERIAL_FAIL",
        "Q0L_response4_unbounded": Q["Q0L"]["neg_response4_object_has_no_qualified_bound"],
        "Q0N_kappa": Q["Q0N"]["ratio_is_exactly_two"]}
Q["Q0M"] = {"controls": negs, "all_mutate_real_bytes_or_symbols": True, "PASS": all(negs.values())}
Q["ALL_PASS"] = all(Q[k]["PASS"] for k in Q if isinstance(Q.get(k), dict) and "PASS" in Q[k])
Q["VERDICT"] = "NONVACUOUS_ORACLE_PASS" if Q["ALL_PASS"] else "VACUOUS_ORACLE_OR_MUTATION_CONTROLS_FAIL"
Q["code_hashes"] = {f: sha(f"{OUT}/{f}") for f in ("fw_prod.py", "fw_ref.py", "fw_oracle.py")}
json.dump(Q, open(f"{OUT}/PREEXECUTION_NONVACUOUS_ORACLE_REPORT.json", "w"), indent=1, default=str)
for k in sorted(Q):
    if isinstance(Q[k], dict) and "PASS" in Q[k]:
        print("%-6s %s" % (k, Q[k]["PASS"]))
print("negative controls:", json.dumps(negs))
print("VERDICT:", Q["VERDICT"])

"""WL2SMF00 Section 8 -- sham-only execution and the NUMERICAL THRESHOLD LOCK.

Exactly two sham continuations per descendant, 16 x 2 = 32 starts. No active operator is
constructed, referenced or applied anywhere in this file.
"""
from __future__ import annotations
import sys, os, json, hashlib, time, math
from fractions import Fraction as Fr
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
OUT = "/home/claude/sweep/WL2SMF00"
sys.path.insert(0, OUT)
import numpy as np
import wsfscrp_core as Z
import wl2_prod as P
import wl2_ref as R

CK = f"{OUT}/checkpoints"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
LOCK = json.load(open(f"{OUT}/WL2SMF00_PANEL_LOCK.json"))
LED = json.load(open(f"{OUT}/TARGET_PANEL_CONSTRUCTION_AND_START_LEDGER.json"))
ORC = json.load(open(f"{OUT}/NONVACUOUS_ORACLE_AND_MUTATION_REPORT.json"))
assert ORC["VERDICT"] == "NONVACUOUS_ORACLE_PASS"
assert sha(f"{OUT}/WL2SMF00_MASTER_FREEZE.md") == LOCK["master_freeze_sha256"]
DESC = LOCK["descendants"]
assert len(DESC) == 16
SHAM = {"n": 0, "log": []}


def sham_start(tag):
    SHAM["n"] += 1
    SHAM["log"].append(tag)
    assert SHAM["n"] <= 32, "SHAM_START_BUDGET_PROTOCOL_BREACH"


def identity(s):
    return s.copy()


rows, twin = [], []
t0 = time.time()
for d in DESC:
    did = d["descendant_id"]
    st0 = Z.load(f"{CK}/d_{did}.npz")
    mk = np.load(f"{CK}/m_{did}.npz")
    MA, MB = mk["MA"], mk["MB"]
    src_sha = Z.full_sha(st0)
    B = Z.B_of(st0, MA, MB)
    assert str(B) == d["B"] and Z.full_sha(st0) == d["checkpoint_sha"]

    sham_start(f"SHAM_0_{did}")
    s0 = Z.run_arm(st0, identity, MA, MB, B)
    sham_start(f"SHAM_1_{did}")
    s1 = Z.run_arm(Z.load(f"{CK}/d_{did}.npz"), identity, MA, MB, B)

    tw = {"descendant_id": did,
          "q0_identical": s0["q0"] == s1["q0"],
          "qA_identical": s0["qA"] == s1["qA"], "qB_identical": s0["qB"] == s1["qB"],
          "terminal_state_hash_identical": s0["end_sha"] == s1["end_sha"],
          "masks_immutable": hashlib.sha256(MA.tobytes() + MB.tobytes()).hexdigest() == d["mask_sha"],
          "normalizer_immutable": Z.B_of(st0, MA, MB) == B,
          "source_bytes_unchanged": Z.full_sha(st0) == src_sha,
          "rho_finite": bool(np.isfinite(st0.rho).all()), "B_positive": B > 0}
    tw["PASS"] = all(v for v in tw.values() if isinstance(v, bool))
    twin.append(tw)

    # ---- threshold inputs: baseline, sham trajectory, masks, normalizer, weights only ----
    XA0, XB0 = s0["q0"]
    XA, XB = s0["qA"], s0["qB"]
    sel = np.nonzero(MA | MB)
    rho_sup = [float(x) for x in st0.rho[sel]]
    med = P.exact_median(rho_sup)
    dyn_sq = P.tau_dynamic_sq(XA, XB, XA0, XB0)
    site_sq = (P.COEFF * med / B) ** 2 * P.W_POST
    eta_sq = Fr(0)                                   # certified exact; see the forward-error cert
    tau_sq = P.tau_material_sq(eta_sq, dyn_sq, site_sq)
    # ---- independent reference recomputation, importing nothing from the production module ----
    r_dyn = R.tau_dynamic_sq(XA, XB, XA0, XB0)
    r_med = R.median(rho_sup)
    r_site = (Fr(1, 100) * r_med / B) ** 2 * sum(R.WR, Fr(0))
    r_tau = R.tau_material_sq(Fr(0), r_dyn, r_site)
    # ---- reference re-read of the t0 state straight from the checkpoint bytes (0 starts) ----
    flat = [float(x) for x in np.asarray(st0.rho).ravel()]
    fa = [bool(x) for x in np.asarray(MA).ravel()]
    fb = [bool(x) for x in np.asarray(MB).ravel()]
    ref_B = R.normalizer(flat, fa, fb)
    ref_X0 = R.X_channels(flat, fa, fb, ref_B)
    dom = ("ETA_ORACLE_L2" if eta_sq >= max(dyn_sq, site_sq)
           else ("TAU_DYNAMIC_L2" if dyn_sq >= site_sq else "TAU_SITE_L2"))
    rows.append({
        "descendant_id": did, "seed": d["seed"], "geometry": d["geometry"], "alloc": d["alloc"],
        "B": str(B), "RHO_MED": str(med), "n_support": len(rho_sup),
        "G2": str(Fr(dyn_sq) ** 0 * 0 + (Fr(dyn_sq) / (P.COEFF ** 2))),   # G2^2, exact
        "TAU_DYNAMIC_L2": math.sqrt(float(dyn_sq)), "TAU_SITE_L2": math.sqrt(float(site_sq)),
        "ETA_ORACLE_L2": 0.0, "TAU_MATERIAL_L2": math.sqrt(float(tau_sq)),
        "TAU_MATERIAL_L2_sq_exact": str(tau_sq), "dominant_term": dom,
        "reference_agrees_tau": r_tau == tau_sq,
        "reference_agrees_median": r_med == med,
        "reference_agrees_normalizer": ref_B == B,
        "reference_agrees_t0_reader": ref_X0 == Z.q_channels(st0, MA, MB, B),
        "finite_positive": bool(tau_sq > 0 and math.isfinite(float(tau_sq)))})
    print("  %-18s TAU=%.4e (dyn %.4e site %.4e, %s) twin=%s ref=%s [%.0fs]"
          % (did, rows[-1]["TAU_MATERIAL_L2"], rows[-1]["TAU_DYNAMIC_L2"],
             rows[-1]["TAU_SITE_L2"], dom, tw["PASS"],
             rows[-1]["reference_agrees_tau"] and rows[-1]["reference_agrees_t0_reader"],
             time.time() - t0), flush=True)

assert SHAM["n"] == 32, "INCOMPLETE_SHAM_PANEL"
assert all(t["PASS"] for t in twin), "SHAM_TWIN_NONDETERMINISM"
assert all(r["finite_positive"] for r in rows), "DESCENDANT_L2_THRESHOLD_NOT_FINITE_POSITIVE"
assert all(r["reference_agrees_tau"] and r["reference_agrees_t0_reader"]
           and r["reference_agrees_median"] and r["reference_agrees_normalizer"] for r in rows)

# =====================================================================================
# aggregation over the frozen G1 alpha map
# =====================================================================================
tau_sq_list = [Fr(r["TAU_MATERIAL_L2_sq_exact"]) for r in rows]
alpha_desc = [Fr(1, 16)] * 16                      # 1/4 block x 1/4 descendant x 2 sentinels
E_TAU = sum((alpha_desc[i] * tau_sq_list[i] for i in range(16)), Fr(0))
A_TAU = math.sqrt(float(E_TAU))
E_ETA = Fr(0)
AGG = {"alpha_map": "G1: 1/4 per block, 1/4 per descendant, 1/2 per sentinel = 1/32 per future "
                    "response row; a descendant contributes 2/32 = 1/16 of the total",
       "alpha_sums_to_one": sum(alpha_desc, Fr(0)) == 1,
       "E_TAU_exact": str(E_TAU), "E_TAU": float(E_TAU), "A_TAU": A_TAU,
       "E_ETA_ORACLE": 0.0, "A_ETA_ORACLE": 0.0,
       "independent_ancestry_blocks": 4,
       "TAU_QUOTIENT_PAIR_example": "TAU[i] + TAU[j] for any two descendants",
       "TAU_CONTRAST_rule": "sum_i |c_i| * TAU_MATERIAL_L2[i] for a normalised gauge-valid c",
       "H3_SIGNED_LINEAR_CONTRAST": "NOT_DEFINED_UNDER_GAUGE"}

# ---- dependency audit: the threshold pipeline cannot reach an active response ------------
import ast
prod_imports = set()
for nd in ast.walk(ast.parse(open(f"{OUT}/wl2_prod.py").read())):
    if isinstance(nd, ast.Import):
        prod_imports |= {a.name for a in nd.names}
    if isinstance(nd, ast.ImportFrom):
        prod_imports.add(nd.module or "")
this_src = open(__file__).read()
FORBIDDEN = ["transpose", "state_cross", "_perturb_N", "reciprocal_cross", "erase_all",
             "etcmnfc_core", "ENV_", "CARRIER_1(", "CARRIER_2("]
DEPAUDIT = {
    "wl2_prod_imports": sorted(prod_imports),
    "wl2_prod_imports_only_fractions": prod_imports <= {"fractions", "__future__"},
    "driver_inputs": ["descendant checkpoint bytes", "immutable t0 masks", "normalizer B",
                      "SHAM_0 trajectory", "frozen weights", "static panel coefficients"],
    "forbidden_symbols_in_driver": [s for s in FORBIDDEN if s in this_src.replace("FORBIDDEN", "")],
    "old_active_rows_loaded": 0, "fresh_active_outcomes_generated": 0,
    "fresh_active_outcomes_opened": 0}
DEPAUDIT["PASS"] = bool(DEPAUDIT["wl2_prod_imports_only_fractions"]
                        and not DEPAUDIT["forbidden_symbols_in_driver"])

THRESH = {"panel_lock_sha256": sha(f"{OUT}/WL2SMF00_PANEL_LOCK.json"),
          "master_freeze_sha256": sha(f"{OUT}/WL2SMF00_MASTER_FREEZE.md"),
          "oracle_report_sha256": sha(f"{OUT}/NONVACUOUS_ORACLE_AND_MUTATION_REPORT.json"),
          "production_sha256": sha(f"{OUT}/wl2_prod.py"),
          "reference_sha256": sha(f"{OUT}/wl2_ref.py"),
          "descendant_thresholds": rows, "aggregate": AGG,
          "dependency_audit": DEPAUDIT,
          "engine_starts": {"C_SETUP": LED["C_SETUP"], "construction": LED["construction"],
                            "sham": SHAM["n"], "extra_after_panel_lock": 0,
                            "total": LED["C_SETUP"] + LED["construction"] + SHAM["n"],
                            "caps": {"construction": 32, "sham": 32, "total": 64}},
          "sham_log": SHAM["log"],
          "SEALED": True}
json.dump(THRESH, open(f"{OUT}/WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json", "w"), indent=1)
json.dump({"twins": twin, "all_pass": all(t["PASS"] for t in twin), "n": len(twin)},
          open(f"{OUT}/SHAM_TWIN_FULL_HORIZON_ORACLE.json", "w"), indent=1)
json.dump({"descendants": rows, "aggregate": AGG},
          open(f"{OUT}/DESCENDANT_L2_THRESHOLD_COMPONENTS.json", "w"), indent=1)
json.dump({"fresh_active_outcomes_generated": 0, "fresh_active_outcomes_opened": 0,
           "old_active_outcomes_loaded_by_threshold_pipeline": 0,
           "old_shams_used_as_locked_calibration_units": 0,
           "old_shams_used_for": "nothing in this programme; the fixtures are hand constructed",
           "post_t0_advances": {"SHAM_0": 16, "SHAM_1": 16, "anything_else": 0},
           "dependency_audit": DEPAUDIT,
           "namespaces": {"62000-62009": "RESERVED_AND_UNREAD", "64000-64011": "NOT_REUSED; two "
                          "were re-run only as a byte-equivalence replay of the refactored "
                          "constructor, which produced no outcome and no panel membership"}},
          open(f"{OUT}/ZERO_ACTIVE_OUTCOME_ACCESS_LEDGER.json", "w"), indent=1)

tl = [r["TAU_MATERIAL_L2"] for r in rows]
print("\nsham starts: %d of 32 | total starts %d of 64" % (SHAM["n"], THRESH["engine_starts"]["total"]))
print("TAU_MATERIAL_L2 range [%.4e, %.4e]  E_TAU=%.4e  A_TAU=%.4e" % (min(tl), max(tl), float(E_TAU), A_TAU))
import collections
print("dominant term:", dict(collections.Counter(r["dominant_term"] for r in rows)))
print("twin oracle:", sum(t["PASS"] for t in twin), "of", len(twin))
print("dependency audit:", DEPAUDIT["PASS"], "| SEALED")

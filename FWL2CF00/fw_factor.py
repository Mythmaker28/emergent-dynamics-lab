"""FWL2CF00 Sections 9-10 -- stratum transfer status, fresh G1xH3 factor objects, deliverables."""
from __future__ import annotations
import json, hashlib, itertools, math, os, sys
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/FWL2CF00"
sys.path.insert(0, OUT)
import fw_prod as P
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
CORE = json.load(open(f"{OUT}/_analysis_core.json"))
RW = json.load(open(f"{OUT}/_rows.json"))["rows"]
AP = json.load(open(f"{OUT}/FWL2CF00_ACTIVE_PANEL_LOCK.json"))
W = P.W
T = P.T
SW = np.array([float(w) ** 0.5 for w in W])
S2 = math.sqrt(2.0)
TAU = {k: math.sqrt(float(Fr(v))) for k, v in AP["thresholds_locked"].items()}

rows = []
for r in RW:
    dA = np.array([float(Fr(x)) for x in r["dA"]])
    dB = np.array([float(Fr(x)) for x in r["dB"]])
    rows.append({**{k: r[k] for k in ("descendant", "block", "geometry", "alloc", "arm")},
                 "u": SW * (dA + dB) / S2, "v": SW * (dA - dB) / S2,
                 "tau": TAU[r["descendant"]]})
IDX = {(r["block"], r["geometry"], r["alloc"], r["arm"]): i for i, r in enumerate(rows)}
BLOCKS = sorted({r["block"] for r in rows})
ARMS = ["CARRIER_1", "CARRIER_2"]
RES = {}

# ===================================================================================
# 9. FROZEN STRATUM TRANSFER -- status declared before any fresh data
# ===================================================================================
RES["stratum"] = {
    "FROZEN_FACTOR_PIPELINE_STATUS": "PARENT_OBJECT_NOT_EVALUABLE",
    "FRESH_STRATUM_TRANSFER": "NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT",
    "FRESH_STRATUM_TRANSFER_PLUS": "NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT",
    "FRESH_STRATUM_TRANSFER_MINUS": "NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT",
    "why": "GIMB00 serialised only scalar summaries of its founder-stratum object; psi_plus and "
           "Psi_minus are in no committed parent tree. Rebuilding them would require reopening and "
           "refitting the historical exposed active rows, which this handoff forbids. Declared in "
           "the master freeze BEFORE the sham replay, not discovered afterwards.",
    "additionally": "the fresh quotient did not reach material at-least-two, so transfer would "
                    "have been ineligible on that ground as well.",
    "FACTORIAL_ATTRIBUTION_STATUS_for_the_parent_stratum": "NOT_REACHED"}


# ===================================================================================
# 10. FRESH PREDECLARED FACTOR OBJECTS (PLUS sector), reported only as
#     FRESH_FACTOR_EFFECT_NOT_PARENT_STRATUM_EXPLANATION
# ===================================================================================
def contrast(coef):
    """coef: dict row-index -> raw coefficient. Normalised so sum c^2 = 1.
    Returns amplitude ||sum c_i u_i||, the conservative floor sum |c_i| TAU_i, and the verdict."""
    ks = sorted(coef)
    c = np.array([coef[k] for k in ks], dtype=float)
    nrm = math.sqrt(float((c ** 2).sum()))
    c = c / nrm
    X = sum(c[j] * rows[ks[j]]["u"] for j in range(len(ks)))
    amp = float(np.linalg.norm(X))
    floor = float(sum(abs(c[j]) * rows[ks[j]]["tau"] for j in range(len(ks))))
    return {"amplitude": amp, "floor": floor, "ratio": amp / floor,
            "MATERIAL": bool(amp > floor), "n_rows": len(ks), "X": X}


def geom_contrast(b, o):
    return {IDX[(b, "FAR", 0, o)]: 0.5, IDX[(b, "FAR", 1, o)]: 0.5,
            IDX[(b, "NEAR", 0, o)]: -0.5, IDX[(b, "NEAR", 1, o)]: -0.5}


def alloc_contrast(b, g, o):
    return {IDX[(b, g, 0, o)]: 1.0, IDX[(b, g, 1, o)]: -1.0}


F = {}
# --- geometry, per block and arm, then the equal-block mean -------------------------------
for o in ARMS:
    per = {b: contrast(geom_contrast(b, o)) for b in BLOCKS}
    merged = {}
    for b in BLOCKS:
        for k, c in geom_contrast(b, o).items():
            merged[k] = merged.get(k, 0.0) + c / len(BLOCKS)
    agg = contrast(merged)
    signs = [float(np.dot(per[b]["X"], agg["X"])) > 0 for b in BLOCKS]
    shares = [float(np.dot(per[b]["X"], agg["X"] / np.linalg.norm(agg["X"])) ** 2) for b in BLOCKS]
    loo = []
    for bo in BLOCKS:
        m2 = {}
        for b in BLOCKS:
            if b == bo:
                continue
            for k, c in geom_contrast(b, o).items():
                m2[k] = m2.get(k, 0.0) + c / (len(BLOCKS) - 1)
        loo.append(contrast(m2)["MATERIAL"])
    F[f"MANIPULATED_GEOMETRY_{o}"] = {
        "aggregate": {k: v for k, v in agg.items() if k != "X"},
        "per_block": {b: {k: v for k, v in per[b].items() if k != "X"} for b in BLOCKS},
        "four_block_coherent_sign": all(signs), "blocks_material": [per[b]["MATERIAL"] for b in BLOCKS],
        "max_single_block_share": max(shares) / sum(shares) if sum(shares) > 0 else None,
        "leave_one_block_out_all_material": all(loo)}
# --- unoriented allocation sensitivity ------------------------------------------------------
for o in ARMS:
    cells = {}
    for b in BLOCKS:
        for g in ("FAR", "NEAR"):
            cells[f"{b}|{g}"] = {k: v for k, v in contrast(alloc_contrast(b, g, o)).items() if k != "X"}
    mats = [c["MATERIAL"] for c in cells.values()]
    F[f"UNORIENTED_ALLOCATION_{o}"] = {
        "per_block_geometry": cells, "n_material": sum(mats), "n_cells": len(mats),
        "all_material": all(mats),
        "note": "unoriented: the object is the norm of the complementary-allocation difference; "
                "exchanging the neutral member labels leaves it exactly unchanged."}
# --- geometry modulation of the allocation sensitivity ---------------------------------------
for o in ARMS:
    mod = {}
    for b in BLOCKS:
        fa = contrast(alloc_contrast(b, "FAR", o))
        ne = contrast(alloc_contrast(b, "NEAR", o))
        mod[b] = {"FAR_amplitude": fa["amplitude"], "NEAR_amplitude": ne["amplitude"],
                  "difference": fa["amplitude"] - ne["amplitude"],
                  "conservative_floor": fa["floor"] + ne["floor"],
                  "MATERIAL": abs(fa["amplitude"] - ne["amplitude"]) > fa["floor"] + ne["floor"]}
    F[f"GEOMETRY_MODULATION_{o}"] = {
        "per_block": mod, "n_material": sum(m["MATERIAL"] for m in mod.values()),
        "coherent_sign": len({m["difference"] > 0 for m in mod.values()}) == 1,
        "floor_note": "a difference of NORMS is not a linear contrast; under the null both norms "
                      "are bounded by their own floors, so their difference is bounded in absolute "
                      "value by the SUM of the two floors. That conservative floor is used."}
# --- predeclared operator differences ----------------------------------------------------------
opdiff = {}
for name, mk in (("GEOMETRY", geom_contrast),):
    merged = {}
    for b in BLOCKS:
        for k, c in mk(b, "CARRIER_1").items():
            merged[k] = merged.get(k, 0.0) + c / len(BLOCKS)
        for k, c in mk(b, "CARRIER_2").items():
            merged[k] = merged.get(k, 0.0) - c / len(BLOCKS)
    opdiff[f"OPERATOR_DIFFERENCE_IN_{name}"] = {k: v for k, v in contrast(merged).items() if k != "X"}
alloc_op = {}
for b in BLOCKS:
    for g in ("FAR", "NEAR"):
        a1 = contrast(alloc_contrast(b, g, "CARRIER_1"))
        a2 = contrast(alloc_contrast(b, g, "CARRIER_2"))
        alloc_op[f"{b}|{g}"] = {"C1": a1["amplitude"], "C2": a2["amplitude"],
                                "difference": a1["amplitude"] - a2["amplitude"],
                                "conservative_floor": a1["floor"] + a2["floor"],
                                "MATERIAL": abs(a1["amplitude"] - a2["amplitude"]) > a1["floor"] + a2["floor"]}
opdiff["OPERATOR_DIFFERENCE_IN_ALLOCATION"] = alloc_op
F["OPERATOR_DIFFERENCES"] = opdiff

# --- H3 allocation-label invariance, exhaustive 2^8 ------------------------------------------------
pairs = [(b, g) for b in BLOCKS for g in ("FAR", "NEAR")]
base = {}
for o in ARMS:
    for (b, g) in pairs:
        base[(b, g, o)] = round(contrast(alloc_contrast(b, g, o))["amplitude"], 18)
inv = True
for bits in itertools.product([0, 1], repeat=8):
    flip = {pairs[i]: bits[i] for i in range(8)}
    for o in ARMS:
        for (b, g) in pairs:
            cc = alloc_contrast(b, g, o)
            if flip[(b, g)]:
                cc = {k: -v for k, v in cc.items()}
            if round(contrast(cc)["amplitude"], 18) != base[(b, g, o)]:
                inv = False
geo_inv = True
for bits in itertools.product([0, 1], repeat=8):
    for o in ARMS:
        for b in BLOCKS:
            if round(contrast(geom_contrast(b, o))["amplitude"], 18) != \
                    round(contrast(geom_contrast(b, o))["amplitude"], 18):
                geo_inv = False
F["H3_ALLOCATION_LABEL_GAUGE"] = {
    "n_exchanges_enumerated": 256,
    "unoriented_allocation_objects_invariant": inv,
    "geometry_contrast_is_allocation_symmetric_by_construction":
        "the geometry contrast averages over BOTH allocation members with equal weight, so it is "
        "invariant under exchanging them; verified structurally rather than by a self-comparison",
    "signed_allocation_contrast": "NOT_DEFINED_UNDER_GAUGE"}

# --- MINUS sector: shape diagnostics only ------------------------------------------------------------
KAPPA2 = 0.5
minus = {}
for b in BLOCKS:
    for g in ("FAR", "NEAR"):
        for a in (0, 1):
            V = np.concatenate([rows[IDX[(b, g, a, "CARRIER_1")]]["v"],
                                rows[IDX[(b, g, a, "CARRIER_2")]]["v"]])
            minus[f"{b}|{g}|a{a}"] = {"two_arm_block_trace": float(KAPPA2 * (V @ V))}
F["MINUS_SECTOR"] = {"per_descendant_block_trace": minus,
                     "KAPPA_TWO_ARM": "1/sqrt(2), paired with the smaller floor",
                     "STATUS": "TRANSFORMED_BOUND_NOT_QUALIFIED",
                     "why": "the parent propagation certificate records PROJECTIVE_EMBEDDING_BOUND "
                            "= NOT_AVAILABLE and H3_K_BOUND = NOT_AVAILABLE, so no response^2 or "
                            "response^4 object may be compared with a response-unit TAU. These are "
                            "shape diagnostics and carry no attribution."}

# --- statuses ------------------------------------------------------------------------------------------
def status(agg_key):
    c1 = F[f"{agg_key}_CARRIER_1"]
    c2 = F[f"{agg_key}_CARRIER_2"]
    if agg_key == "MANIPULATED_GEOMETRY":
        m1 = c1["aggregate"]["MATERIAL"] and c1["four_block_coherent_sign"] \
             and all(c1["blocks_material"]) and c1["leave_one_block_out_all_material"] \
             and (c1["max_single_block_share"] or 1) <= 0.5
        m2 = c2["aggregate"]["MATERIAL"] and c2["four_block_coherent_sign"] \
             and all(c2["blocks_material"]) and c2["leave_one_block_out_all_material"] \
             and (c2["max_single_block_share"] or 1) <= 0.5
    elif agg_key == "UNORIENTED_ALLOCATION":
        m1, m2 = c1["all_material"], c2["all_material"]
    else:
        m1 = c1["n_material"] == len(BLOCKS) and c1["coherent_sign"]
        m2 = c2["n_material"] == len(BLOCKS) and c2["coherent_sign"]
    if m1 and m2:
        return "PRESENT_NOT_PARENT_STRATUM_EXPLANATION"
    if m1 or m2:
        return "OPERATOR_SPECIFIC"
    return "BELOW_MATERIALITY"


RES["factor"] = F
RES["MANIPULATED_GEOMETRY_STATUS"] = status("MANIPULATED_GEOMETRY")
RES["UNORIENTED_ALLOCATION_STATUS"] = status("UNORIENTED_ALLOCATION")
RES["GEOMETRY_ALLOCATION_MODULATION_STATUS"] = status("GEOMETRY_MODULATION")
RES["FACTORIAL_ATTRIBUTION_PLUS"] = "FRESH_FACTOR_EFFECT_NOT_PARENT_STRATUM_EXPLANATION"
RES["FACTORIAL_ATTRIBUTION_MINUS"] = "TRANSFORMED_BOUND_NOT_QUALIFIED"
RES["FACTORIAL_ATTRIBUTION_STATUS"] = "NOT_REACHED"
json.dump(RES, open(f"{OUT}/_factor.json", "w"), indent=1, default=str)
print("stratum:", RES["stratum"]["FRESH_STRATUM_TRANSFER"])
for k in ("MANIPULATED_GEOMETRY_STATUS", "UNORIENTED_ALLOCATION_STATUS",
          "GEOMETRY_ALLOCATION_MODULATION_STATUS"):
    print("%-42s %s" % (k, RES[k]))
for o in ARMS:
    g = F[f"MANIPULATED_GEOMETRY_{o}"]["aggregate"]
    print("  geometry %-10s amp=%.4e floor=%.4e ratio=%.3f material=%s"
          % (o, g["amplitude"], g["floor"], g["ratio"], g["MATERIAL"]))
    al = F[f"UNORIENTED_ALLOCATION_{o}"]
    print("  allocation %-8s %d/%d cells material" % (o, al["n_material"], al["n_cells"]))
print("H3 2^8 allocation-label invariance:", F["H3_ALLOCATION_LABEL_GAUGE"]["unoriented_allocation_objects_invariant"])

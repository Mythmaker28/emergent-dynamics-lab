"""ETNBFC Phase B0 + B1 feasibility.

B0 is a STATIC audit of the executable: what is Mf[0] physically, what are the integration
weights, what is the exact conserved content, and what joint domain constraints bind Mf[0].
B1 then MEASURES, on DEVELOPMENT founding blocks only, whether an exact byte-matched A-B
common support exists at all. No target contrast is read anywhere in this file.
"""
from __future__ import annotations
import sys, os, ast, json, hashlib, itertools
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
import numpy as np
import domc_core as K, ppai_core as P, etpc_core as E
import ppai_engine as PE

STARTS = {"n": 0, "log": []}
O = {}


def start(tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)


# =============================================================== B0 : canonical semantics
src_ppai = open("/home/claude/sweep/PPAI/ppai_engine.py").read()
src_sc = open("/home/claude/sweep/edlab/substrates/scaffold/engine.py").read()
tree = ast.parse(src_ppai)
step_fn = [n for n in ast.walk(tree)
           if isinstance(n, ast.FunctionDef) and n.name == "step"][0]
step_src = ast.unparse(step_fn)

# --- how is Mf transported? divergence form or not?
transport_divergence = "dM += -(gm - np.roll(gm, 1, axis))" in src_ppai
mf_from_intensive = "Mf = rho * newm" in src_ppai
clip_pm1 = "np.clip(mk, -1.0, 1.0) * alive" in src_ppai
inheritance_removed = "Mf += g * m" not in src_ppai and "Mf += g*m" not in src_ppai
lap_has_no_dx = "4.0 * X)" in src_sc and "dx" not in src_sc

O["B0_REPRESENTATION"] = {
    "array": "Mf, shape (n_comp, L, L), float64, C-contiguous",
    "target_coordinate": "Mf[0]",
    "derived_intensive": "z_i = Mf[0]_i / max(rho_i, EPS), with EPS = 1e-12",
    "is_Mf0_an_amount_or_a_density": "AN AMOUNT (extensive content per cell)",
    "proof_1_construction": {
        "code": "Mf = rho * newm  (end of the writer)",
        "found": mf_from_intensive,
        "reading": "Mf[0] is literally the product of a cell density and a bounded intensive "
                   "concentration, i.e. a per-cell content."},
    "proof_2_transport_is_divergence_form": {
        "code": "mdon = donor-cell value of fM = Mf/rho ; gm = fl * mdon ; "
                "dM += -(gm - np.roll(gm, 1, axis))",
        "found": transport_divergence,
        "reading": "the transport update is an exact telescoping divergence of a face quantity. "
                   "A divergence-form update conserves the PLAIN SUM of the array. It would NOT "
                   "conserve a volume-weighted sum unless the weights were uniform. This is the "
                   "executable-derived reason for w_i, not an assumption about units."},
    "proof_3_uniform_measure": {
        "code": "lap(X) = roll(X,1,-2)+roll(X,-1,-2)+roll(X,1,-1)+roll(X,-1,-1)-4X",
        "no_grid_spacing_symbol_anywhere": lap_has_no_dx,
        "reading": "the stencil carries no dx and no per-cell area. Every cell of the 64x64 "
                   "periodic lattice has the identical unit measure. There are NO stored or "
                   "source bits for a varying cell volume or integration weight, because no such "
                   "quantity exists in the model."},
    "w_i": 1.0,
    "w_i_status": "CONSTANT AND EXACTLY 1.0 for every cell, established from the executable "
                  "(uniform stencil, divergence-form transport), not assumed from w_i = 1 "
                  "looking natural.",
    "exact_physical_content": "Q = exact_sum_i Mf[0]_i  (unweighted, because w_i == 1 exactly)",
    "state_increment_to_content_map": "an increment dMf0_i adds exactly dMf0_i to Q. The map is "
                                      "the identity; there is no capacity or storage weight "
                                      "between the state variable and the content.",
}

O["B0_DOMAIN_CONSTRAINTS"] = {
    "C1_bounded_intensive": {
        "constraint": "|Mf[0]_i| <= rho_i, i.e. |z_i| <= 1",
        "enforced_by": "np.clip(mk, -1.0, 1.0) applied to the INTENSIVE m before Mf = rho * newm",
        "found_in_source": clip_pm1,
        "joint": "YES -- it couples Mf[0] to rho. It is NOT a standalone box on Mf[0]."},
    "C2_alive_gate": {
        "constraint": "Mf[0]_i == 0.0 EXACTLY wherever alive_i is False, alive = rho > 1e-4",
        "enforced_by": "newm[kk] = np.clip(...) * alive, then Mf = rho * newm",
        "joint": "YES -- a second, independent coupling of Mf[0] to rho, with a threshold that "
                 "is NOT the same as rho > 0."},
    "C3_second_component": {
        "constraint": "Mf[1] obeys the same two constraints with the same rho",
        "coupling_to_Mf0": "NONE. The writer updates each component independently; no term in "
                           "dm_k reads m_j for j != k. Mf[1] therefore imposes no additional "
                           "constraint on an exchange of Mf[0].",
        "verified": "eta_d is indexed per component; Psi is common but is a function of N, c and "
                    "uptake only, never of m."},
    "C4_occupancy": {
        "constraint": "none. There is no occupancy variable distinct from rho.",
        "note": "rho itself is bounded above by the growth term's (1 - rho/rho_max) factor, but "
                "that bounds rho, not Mf[0]."},
    "conclusion": "The complete joint admissibility set for a modification of Mf[0] at site i, "
                  "holding every other field fixed, is:  |Mf[0]_i| <= rho_i AND "
                  "(Mf[0]_i == 0 if rho_i <= 1e-4).  '|z| <= 1' alone is NOT the full statement: "
                  "the alive gate is a separate, exact, joint condition.",
    "consequence_for_pairing": "two sites are exchange-compatible for Mf[0] if and only if they "
                               "have BIT-IDENTICAL rho. Equal rho gives an identical bound and an "
                               "identical alive flag, so the transposition is admissible by "
                               "construction and needs no clip. Nothing else in the schema binds "
                               "Mf[0].",
}

O["B0_PAIR_KEY"] = {
    "pair_key_i": "bytes(rho_i)",
    "why_no_other_field": "w_i is a compile-time constant 1.0 identical at every site, so it "
                          "contributes no discriminating bits; C3 and C4 add no constraint. rho "
                          "is the ONLY non-target field in the joint domain.",
    "explicitly_excluded_from_the_key": ["Mf[0]", "z", "kappa", "boundary exposure",
                                         "c", "N", "uptake", "any endpoint", "any future value"],
    "hash_basis": "raw float64 little-endian bytes, no rounding, no tolerance",
}

# =============================================================== B1 : feasibility, DEV blocks
DEV_SEEDS = (61000, 61001, 61002, 61003)      # DEVELOPMENT_EXPOSED, development-only forever
GEOM = "FAR"


def founder(seed):
    """Rebuild the ETPC founding checkpoint exactly. One engine start."""
    K.set_geometry(GEOM)
    start(f"DEV_FOUNDER_{seed}")
    eng = E.engine(E.GAIN_ON)
    f = K.advance(eng, K.found(seed), K.T_FOUND)
    hA, hB = (P.HIST_H, P.HIST_L) if seed % 2 == 0 else (P.HIST_L, P.HIST_H)
    return K.advance(eng, K.apply_dual_history(eng, f, hA, hB), K.SETTLE)


def key_bytes(rho, ys, xs):
    return [rho[y, x].tobytes() for y, x in zip(ys, xs)]


rows = []
for sd in DEV_SEEDS:
    st = founder(sd)
    mem, ncomp = E.members(st)
    if mem["A"] is None or mem["B"] is None:
        rows.append({"seed": sd, "lineage_valid": False})
        continue
    (ya, xa), (yb, xb) = mem["A"], mem["B"]
    ka, kb = key_bytes(st.rho, ya, xa), key_bytes(st.rho, yb, xb)
    from collections import Counter
    ca, cb = Counter(ka), Counter(kb)
    common = ca & cb                                     # multiset intersection
    n_pairs = sum(common.values())
    # how close do they get, if not exact?
    ra, rb = np.sort(st.rho[ya, xa]), np.sort(st.rho[yb, xb])
    # nearest-neighbour relative gap between the two rho sets
    gaps = [float(np.min(np.abs(rb - v)) / max(abs(v), 1e-300)) for v in ra]
    # how many bits of the mantissa agree at the closest partner?
    def ulp_dist(u, v):
        iu = np.frombuffer(np.float64(u).tobytes(), dtype=np.int64)[0]
        iv = np.frombuffer(np.float64(v).tobytes(), dtype=np.int64)[0]
        return int(abs(iu - iv))
    best = [min(ulp_dist(v, w) for w in rb) for v in ra]
    rows.append({
        "seed": sd, "lineage_valid": True, "n_components": ncomp,
        "n_A": len(ya), "n_B": len(yb),
        "distinct_rho_A": len(ca), "distinct_rho_B": len(cb),
        "exact_common_support_pairs": n_pairs,
        "coverage_sites_A": n_pairs / len(ya), "coverage_sites_B": n_pairs / len(yb),
        "min_relative_gap": min(gaps), "median_relative_gap": float(np.median(gaps)),
        "min_ulp_distance": min(best), "median_ulp_distance": float(np.median(best)),
        "rho_range_A": [float(ra[0]), float(ra[-1])],
        "rho_range_B": [float(rb[0]), float(rb[-1])],
        "mass_A": float(st.rho[ya, xa].sum()), "mass_B": float(st.rho[yb, xb].sum()),
    })
    print(f"seed {sd}: |A|={len(ya)} |B|={len(yb)} exact pairs={n_pairs} "
          f"min_ulp={min(best)} min_rel_gap={min(gaps):.3e}", flush=True)

O["B1_EXACT_SUPPORT_FEASIBILITY"] = {
    "blocks": rows,
    "role_of_these_blocks": "DEVELOPMENT_EXPOSED (ETPC primary seeds, development-only forever)",
    "what_was_read": "component membership, rho bytes, cell counts. NO endpoint, NO c/N series, "
                     "NO swap-sham contrast.",
    "total_exact_pairs_over_all_dev_blocks":
        sum(r.get("exact_common_support_pairs", 0) for r in rows),
}

json.dump({"phase": "B0_B1", "engine_starts": STARTS, **O},
          open("/home/claude/sweep/ETNBFC/etnbfc_b0.json", "w"), indent=1, default=str)
print("\nENGINE STARTS:", STARTS["n"], STARTS["log"])
print("TOTAL EXACT PAIRS:", O["B1_EXACT_SUPPORT_FEASIBILITY"]["total_exact_pairs_over_all_dev_blocks"])

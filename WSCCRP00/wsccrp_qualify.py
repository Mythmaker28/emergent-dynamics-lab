"""WSCCRP00 Phase A freeze + qualification tranche Q1-Q5.

TRAIN_SELECTION only. LOCKED_DEV_EVALUATION does not exist yet and is not touched.
The endpoint, grid, weights, superfamily taxonomy and every gate threshold are written to the
freeze file BEFORE the first outcome is computed, in this same file, top to bottom.
"""
from __future__ import annotations
import sys, os, json, hashlib
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
sys.path.insert(0, "/home/claude/sweep/ETPC")
sys.path.insert(0, "/home/claude/sweep/ETCMNFC")
import numpy as np
import domc_core as K, ppai_core as P, etpc_core as E, etcmnfc_core as Z
from edlab.experiments.sc_mcm import config as C

CK = "/home/claude/sweep/ETNBFC/checkpoints"
OUT = "/home/claude/sweep/WSCCRP00"
K.set_geometry("FAR")
DT = C.SPEC.dt

# ============================================================ FROZEN SPEC (written first)
H_GRID = [40, 80, 120, 160, 200, 240, 280, 320, 360, 400]     # inherited exactly from WSCPL00
PHYS = np.array(H_GRID, dtype=float) * DT                      # 4.0 .. 40.0
# trapezoidal weights over PHYSICAL time, normalised to sum 1
w = np.zeros(len(PHYS))
w[0] = (PHYS[1] - PHYS[0]) / 2
w[-1] = (PHYS[-1] - PHYS[-2]) / 2
for i in range(1, len(PHYS) - 1):
    w[i] = (PHYS[i + 1] - PHYS[i - 1]) / 2
W = w / w.sum()
ETA_ORACLE = 1e-12          # numerical replay margin; replay is bit-exact, this is a floor
STRATA = [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9]]      # three ~equal physical-time strata
TRAIN_FOUNDERS = [61000, 61001, 61002, 61003]

SUPERFAMILIES = {
    "S1_CONSERVATIVE_CARRIER_REDISTRIBUTION": {
        "role": "TRAIN",
        "algebra": "raw-byte transposition of Mf[0] on the frozen maximum-support lexicographic "
                   "cross-component matching; exactly content-conserving, byte-involutive",
        "descendants": ["matched_transposition"]},
    "S2_NONCONSERVATIVE_CARRIER_TRANSFORMATION": {
        "role": "TRAIN",
        "algebra": "carrier transformations that do NOT conserve the carrier content or its "
                   "multiset: lattice reflection of the intensive field, lattice reflection of "
                   "the extensive field, and total ablation. Cousins, not three superfamilies.",
        "descendants": ["intensive_reflection", "extensive_reflection", "total_ablation"]},
    "S3_ENVIRONMENTAL_FIELD_PERTURBATION": {
        "role": "LOCKED_DEV_EVALUATION",
        "algebra": "additive perturbation of the public nutrient field N; touches no carrier",
        "descendants": ["N_plus_0.5N0"],
        "note": "LOCKED. Not executed in qualification. Q2 explicitly forbids the material "
                "signal from being carried only by this arm, so it is the one held out."},
}

FREEZE = {
    "programme": "WARPED_SCALE_CONTINUOUS_CAUSAL_RESPONSE_PILOT_00",
    "parent_commit": "7cc1ffa0a782a34774a57094189ed19f6bd2b761",
    "parent_bundle_sha256": "d7c16ce4231ec750ad767d572127c616441f60a73e60c5aea2faf103a2b6a572",
    "parent_archive_sha256": "f23259abe0333a351090346cb90ddc7b76b28ee050f65e573f7760def9353c0e",
    "inherited_reader": {
        "source": "WSCPL00/wscpl_probe_responsive.py sha256 "
                  "207fa600c6fb220bb846c8fdae2cfb096d054a4fd9528a14fc75d4468d66bbd3",
        "mass_field": "st.rho summed over the cells returned by domc_core.read_sites",
        "membership": "DYNAMICALLY REDETECTED at every scored time by the frozen detector "
                      "(threshold 0.30, min_cells 12), NOT immutable t0 masks",
        "identity_persistence": "frozen-site nearest-entity assignment inside read_sites",
        "boundary": "periodic 64x64 lattice",
        "intervention_time": "the founding checkpoint, step 390",
        "h0_included": False,
        "split_merge_disappear": "if either A or B is unreadable the unit is undefined and the "
                                 "stage is NOT_IDENTIFIABLE; no imputation"},
    "endpoint": {
        "a": "abs(m_A - m_B) / (m_A + m_B), requires m_A>=0, m_B>=0, S>0",
        "r": "r[b,u,h] = a(F^h(INT_u(x_b))) - a(F^h(SHAM(x_b)))",
        "H_grid_native_steps": H_GRID, "physical_times": PHYS.tolist(),
        "quadrature": "trapezoidal in PHYSICAL time, normalised so sum_h w_h = 1",
        "w": W.tolist(), "ETA_ORACLE": ETA_ORACLE, "strata_indices": STRATA},
    "superfamilies": SUPERFAMILIES,
    "train_selection_founders": TRAIN_FOUNDERS,
    "locked_dev_evaluation": "NOT YET CREATED; no founder and no outcome exists",
    "gates": {"Q2": "A_bu > ETA_b for >=2 TRAIN superfamilies in >=3 founders",
              "Q3": "sigma_2/sigma_1 > 0.10 on the weighted response matrix",
              "Q4": "median LOFO unexplained fraction >= 0.25 and every fold >= 0.10",
              "Q5": "L_STATE <= 0.90 * L_NUIS in median grouped LOFO",
              "membership_dominance": "stop if >50% of quadrature-weighted response energy is "
                                      "attributable to membership change"},
}
json.dump(FREEZE, open(f"{OUT}/WSCCRP00_PROTOCOL_FREEZE.json", "w"), indent=1)
print("FREEZE written before any outcome. sha256:",
      hashlib.sha256(open(f"{OUT}/WSCCRP00_PROTOCOL_FREEZE.json", "rb").read()).hexdigest()[:16])

# ============================================================ endpoint machinery
STARTS = {"n": 0, "log": []}


def masses_dyn(st):
    pick, _, _ = K.read_sites(st)
    if pick["A"] is None or pick["B"] is None:
        return None
    return (float(st.rho[pick["A"].cells[:, 0], pick["A"].cells[:, 1]].sum()),
            float(st.rho[pick["B"].cells[:, 0], pick["B"].cells[:, 1]].sum()))


def masses_fix(st, mask):
    return (float(st.rho[mask["A"][0], mask["A"][1]].sum()),
            float(st.rho[mask["B"][0], mask["B"][1]].sum()))


def a_of(mm):
    if mm is None:
        return None
    mA, mB = mm
    S = mA + mB
    if not (mA >= 0 and mB >= 0 and S > 0):
        return None
    return abs(mA - mB) / S


def run(st0, op, mask, tag):
    STARTS["n"] += 1
    STARTS["log"].append(tag)
    eng = Z.engine(Z.GAIN_ON)
    cur = op(st0.copy())
    a0d, a0f = a_of(masses_dyn(cur)), a_of(masses_fix(cur, mask))
    dyn, fix = [], []
    for t in range(1, max(H_GRID) + 1):
        cur = eng.step(cur)
        if t in H_GRID:
            dyn.append(a_of(masses_dyn(cur)))
            fix.append(a_of(masses_fix(cur, mask)))
    return {"a0_dyn": a0d, "a0_fix": a0f, "dyn": dyn, "fix": fix}


ARMS = {
    "matched_transposition": ("S1_CONSERVATIVE_CARRIER_REDISTRIBUTION", None),
    "intensive_reflection": ("S2_NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                             lambda s, I, J: P.state_cross(s)),
    "extensive_reflection": ("S2_NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                             lambda s, I, J: K.reciprocal_cross(s)),
    "total_ablation": ("S2_NONCONSERVATIVE_CARRIER_TRANSFORMATION",
                       lambda s, I, J: P.erase_all(s)),
}

DATA = {}
for sd in TRAIN_FOUNDERS:
    st0 = E.load(f"{CK}/dev_FAR_{sd}.npz")
    mem, _ = E.members(st0)
    mask = {k: (np.asarray(mem[k][0]), np.asarray(mem[k][1])) for k in ("A", "B")}
    man, I, J = Z.manifest(st0, mem)
    sham = run(st0, lambda s: s.copy(), mask, f"Q_{sd}_SHAM")
    rows = {}
    for nm, (sf, fn) in ARMS.items():
        op = (lambda s: Z.transpose(s, I, J)) if fn is None else (lambda s, f=fn: f(s, I, J))
        arm = run(st0, op, mask, f"Q_{sd}_{nm}")
        r_dyn = [x - y for x, y in zip(arm["dyn"], sham["dyn"])]
        r_fix = [x - y for x, y in zip(arm["fix"], sham["fix"])]
        rows[nm] = {"superfamily": sf, "r_dyn": r_dyn, "r_fix": r_fix,
                    "r_at_h0": arm["a0_dyn"] - sham["a0_dyn"],
                    "A_bu": float(np.sum(W * np.abs(r_dyn)))}
    G_b = float(np.sum(W * np.abs(np.array(sham["dyn"]) - sham["a0_dyn"])))
    DATA[sd] = {"sham": sham, "arms": rows, "G_b": G_b,
                "ETA_b": max(ETA_ORACLE, 0.01 * G_b)}
    print(f"founder {sd}: G_b={G_b:.5f} ETA_b={DATA[sd]['ETA_b']:.6f} "
          + " ".join(f"{k}={v['A_bu']:.5f}" for k, v in rows.items()), flush=True)

json.dump({"freeze_sha": hashlib.sha256(open(f"{OUT}/WSCCRP00_PROTOCOL_FREEZE.json", "rb").read()).hexdigest(),
           "engine_starts": STARTS, "data": DATA},
          open(f"{OUT}/wsccrp_qualification_raw.json", "w"), indent=1, default=str)
print("\nSTARTS:", STARTS["n"])

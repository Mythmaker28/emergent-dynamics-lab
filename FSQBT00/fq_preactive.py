"""FSQBT00 -- compact the sham raw to a support-restricted archive (with sufficiency proof), build
the opaque 24-row active acquisition schedule, and write the preactive transfer lock. Zero starts."""
from __future__ import annotations
import json, hashlib, os, sys
from fractions import Fraction as Fr
import numpy as np
sys.path.insert(0, "/home/claude/sweep/WSFSCRP00"); sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/PPAI"); sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/ETPC")
import wsfscrp_core as Z
OUT = "/home/claude/sweep/FSQBT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
SQDT = "/home/claude/sweep/SQDT00"

MAN = json.load(open(f"{OUT}/FRESH_PANEL_MANIFEST.json"))
SS = json.load(open(f"{OUT}/FRESH_SHAM_SERIES_AND_HASHES.json"))
THR = json.load(open(f"{OUT}/FRESH_WEIGHTED_L2_THRESHOLDS.json"))
LIC = json.load(open(f"{OUT}/CORRECTED_TRANSFER_LICENSES.json"))

# --- compact sham_raw_full -> sham_raw (support restricted), prove sufficiency ---
SRC = f"{OUT}/sham_raw_full"; DST = f"{OUT}/sham_raw"; os.makedirs(DST, exist_ok=True)
compact_man = []
for blk in MAN["blocks"]:
    did = blk["did"]
    f = f"{SRC}/SHAM_0_{did}.npz"
    d = np.load(f); rho, MA, MB = d["rho"], d["MA"], d["MB"]
    sup = np.asarray(MA | MB).ravel(); idx = np.nonzero(sup)[0].astype(np.int32)
    vals = np.stack([np.asarray(rho[k]).ravel()[idx] for k in range(rho.shape[0])])
    outp = f"{DST}/{did}.npz"
    if os.path.exists(outp):
        os.remove(outp)
    np.savez_compressed(outp, rho_support=vals, support_index=idx, MA=MA, MB=MB)
    # sufficiency: rebuild reader series from the compact archive and match the committed sham series
    e = np.load(outp); v2, i2, A2, B2 = e["rho_support"], e["support_index"], e["MA"], e["MB"]
    fa = np.asarray(A2).ravel()[i2]; fb = np.asarray(B2).ravel()[i2]
    XA, XB, Bc = [], [], None
    for k in range(v2.shape[0]):
        row = [Fr(float(x)) for x in v2[k]]
        if k == 0:
            Bc = sum(row, Fr(0))
        XA.append(sum([row[i] for i in range(len(row)) if fa[i]], Fr(0)) / Bc)
        XB.append(sum([row[i] for i in range(len(row)) if fb[i]], Fr(0)) / Bc)
    ok = ([str(x) for x in XA] == SS[did]["XA"] and [str(x) for x in XB] == SS[did]["XB"]
          and str(Bc) == SS[did]["B"])
    compact_man.append({"did": did, "file": f"{did}.npz", "sha256": sha(outp),
                        "support_sites": int(idx.size), "reproduces_committed_series": bool(ok)})
suff = all(m["reproduces_committed_series"] for m in compact_man)
json.dump({"directory": "FSQBT00/sham_raw", "files": compact_man, "sufficiency": suff,
           "proof": "reader series rebuilt from the support-restricted archive equals the committed "
                    "sham series string-for-string in exact rational form"},
          open(f"{OUT}/FRESH_SHAM_RAW_MANIFEST.json", "w"), indent=1)

# --- opaque 24-row active schedule (deterministic, no outcome) ---
SALT = "FSQBT00_ACTIVE_v1"
schedule = {}
decode = {}
for blk in MAN["blocks"]:
    for arm in ("CARRIER_1", "CARRIER_2"):
        key = f"{blk['did']}|{arm}"
        oid = hashlib.sha256((SALT + "|" + key).encode()).hexdigest()[:16]
        schedule[oid] = {"checkpoint": f"panel/d_{blk['did']}.npz", "mask": f"panel/m_{blk['did']}.npz",
                         "arm": arm, "dose": "historical_1x"}
        decode[key] = oid
assert len(schedule) == 24 and len(set(schedule)) == 24

# --- carrier binding ---
CARRIERS = {
    "CARRIER_1": {"callable": "etcmnfc_core.transpose(st, I, J)", "touch_set": ["Mf"],
                  "code_sha256": sha("/home/claude/sweep/ETCMNFC/etcmnfc_core.py"),
                  "dose": "exact historical 1x (a permutation)", "application_time": "descendant t0"},
    "CARRIER_2": {"callable": "ppai_core.state_cross(st)", "touch_set": ["Mf"],
                  "code_sha256": sha("/home/claude/sweep/PPAI/ppai_core.py"),
                  "dose": "exact historical 1x (a reflection)", "application_time": "descendant t0"},
}
BN = f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz"
lock = {
    "panel_checkpoint_and_mask_hashes": [{"did": b["did"], "checkpoint_sha": b["checkpoint_sha"],
                                          "mask_sha": b["mask_sha"],
                                          "checkpoint_file_sha256": b["checkpoint_file_sha256"],
                                          "mask_file_sha256": b["mask_file_sha256"]} for b in MAN["blocks"]],
    "sham_series_sha256": sha(f"{OUT}/FRESH_SHAM_SERIES_AND_HASHES.json"),
    "thresholds_sha256": sha(f"{OUT}/FRESH_WEIGHTED_L2_THRESHOLDS.json"),
    "twin_identity_all_12": THR["twin_identity_all_12"],
    "TAU_sq_exact": {r["did"]: r["TAU_MATERIAL_L2_sq_exact"] for r in THR["thresholds"]},
    "E_TAU_FRESH_exact": THR["E_TAU_FRESH_exact"], "A_TAU_FRESH": THR["A_TAU_FRESH"],
    "carriers": CARRIERS,
    "corrected_licenses": {"P2": LIC["P2_TRANSFER_LICENSE_CORRECTED"],
                           "E2": LIC["E2_AXIS_TRANSFER_LICENSE_CORRECTED"],
                           "TUBE_P2_LOBO": LIC["TUBE_P2_LOBO"]},
    "parent_basis_object": {"npz_sha256": sha(BN), "json_sha256": sha(f"{SQDT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"),
                            "arrays": "mu,P1,P2,e1,e2 (immutable)"},
    "opaque_active_schedule": schedule,
    "opaque_decode_map_SEALED": decode,
    "gauge": "one optional A/B exchange per ancestry block, shared across carriers and all times",
    "alpha_per_row": "1/24", "E_TAU_formula": "sum_b TAU_b^2 / 12",
    "analysis_scripts_sha256": {f: sha(f"{OUT}/{f}") for f in
                                ["fq_lobo.py", "fq_oracle.py", "fq_construct.py", "fq_sham.py", "fq_preactive.py"]},
    "start_ledger": {"construction": 12, "sham": 24, "active_planned": 24, "other_diagnostic": 1,
                     "total_so_far": 36, "cap": 72,
                     "other_diagnostic_note": "one timing probe at seed 70000 after commit1 (deviation D3); "
                                              "read no outcome; seed 70000 consumed and excluded from the panel"},
    "stop_rules": "as frozen in FSQBT00_MASTER_FREEZE section 7",
}
json.dump(lock, open(f"{OUT}/PREACTIVE_TRANSFER_LOCK.json", "w"), indent=1)
# also write the sealed opaque label map as a standalone locked artifact
json.dump({"SALT": SALT, "decode_map_SEALED": decode, "schedule": schedule,
           "note": "decoded only after the raw-only active commit is independently read back"},
          open(f"{OUT}/OPAQUE_ACTIVE_LABEL_MAP_LOCK.json", "w"), indent=1)
print("sham compaction sufficiency:", suff, "| schedule rows:", len(schedule))
print("preactive lock written; twin identity all 12:", THR["twin_identity_all_12"])
print("A_TAU_FRESH:", THR["A_TAU_FRESH"], "TUBE:", LIC["TUBE_P2_LOBO"])

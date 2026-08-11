"""FSQBT00 Section 5 -- construct twelve fresh independent ancestry blocks (one descendant each)
from the deterministic clean namespace N=65100, round-robin over four (geometry,allocation)
subqueues, three acceptances per cell. Each constructed candidate (accepted or rejected) is one
charged construction start and is permanently consumed. Panel sealed at the twelfth acceptance."""
from __future__ import annotations
import json, hashlib, os, sys, time
from fractions import Fraction as Fr
import numpy as np
for p in ("/home/claude/sweep", "/home/claude/sweep/PPAI", "/home/claude/sweep/DOMC",
          "/home/claude/sweep/ETPC", "/home/claude/sweep/WSFSCRP00"):
    sys.path.insert(0, p)
import wsfscrp_core as Z
import domc_core as K
import ppai_core as PC
OUT = "/home/claude/sweep/FSQBT00"
PANEL = f"{OUT}/panel"
os.makedirs(PANEL, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
t0 = time.time()

FRZ = json.load(open(f"{OUT}/FSQBT00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FSQBT00_MASTER_FREEZE.md") == FRZ["hashes"]["FSQBT00_MASTER_FREEZE.md"], "freeze mutated"
LIC = json.load(open(f"{OUT}/CORRECTED_TRANSFER_LICENSES.json"))
assert LIC["FRESH_PANEL_LICENSE"] == "YES", "no fresh panel license"

N = 65100
SUBQUEUES = {
    ("NEAR", 0): [N + 0 + 4 * j for j in range(6)],
    ("NEAR", 1): [N + 1 + 4 * j for j in range(6)],
    ("FAR", 0): [N + 2 + 4 * j for j in range(6)],
    ("FAR", 1): [N + 3 + 4 * j for j in range(6)],
}
CELL_ORDER = [("NEAR", 0), ("NEAR", 1), ("FAR", 0), ("FAR", 1)]


def construct(seed, geom, alloc):
    K.set_geometry(geom)
    e = Z.engine()
    f = K.advance(e, K.found(seed), K.T_FOUND)
    hA, hB = (PC.HIST_H, PC.HIST_L) if alloc == 0 else (PC.HIST_L, PC.HIST_H)
    st = K.advance(e, K.apply_dual_history(e, f, hA, hB), K.SETTLE)
    return st


ledger = {"namespace_N": N, "subqueues": {f"{g}_a{a}": v for (g, a), v in SUBQUEUES.items()},
          "construction_starts": 0, "raw_advance_sequences": 0, "attempts": [], "accepted": []}
cursor = {c: 0 for c in CELL_ORDER}
accepted = {c: [] for c in CELL_ORDER}
MAX_STARTS = 24

# round-robin: one attempt per cell per round, until each cell has 3 or budget exhausted
done = False
while not done:
    progressed = False
    for cell in CELL_ORDER:
        if len(accepted[cell]) >= 3:
            continue
        g, a = cell
        if cursor[cell] >= len(SUBQUEUES[cell]):
            print("EXHAUSTED cell", cell, flush=True)
            continue
        if ledger["construction_starts"] >= MAX_STARTS:
            done = True
            break
        seed = SUBQUEUES[cell][cursor[cell]]
        cursor[cell] += 1
        ledger["construction_starts"] += 1
        ledger["raw_advance_sequences"] += 1
        progressed = True
        st = construct(seed, g, a)
        masks, meta = Z.t0_masks(st)
        did = f"{seed}_{g}_a{a}"
        if masks is None:
            ledger["attempts"].append({"seed": seed, "geometry": g, "alloc": a, "did": did,
                                       "status": "REJECTED__NOT_EXACTLY_TWO_ELIGIBLE", **meta})
            print("  reject %s (%s) [%.0fs]" % (did, meta.get("n_eligible"), time.time() - t0), flush=True)
            continue
        MA, MB = masks
        ref = Z.reference_masks(st)
        prod = tuple(sorted((tuple(meta["ids_A"]), tuple(meta["ids_B"]))))
        B = Z.B_of(st, MA, MB)
        finite = bool(np.isfinite(st.rho).all())
        agree = bool(ref == prod)
        ok = (B > 0) and agree and finite
        csha = Z.save(st, f"{PANEL}/d_{did}.npz")
        np.savez(f"{PANEL}/m_{did}.npz", MA=MA, MB=MB)
        rec = {"seed": seed, "geometry": g, "alloc": a, "did": did,
               "status": "ACCEPTED" if ok else "REJECTED__ADMISSIBILITY",
               "n_A": meta["n_A"], "n_B": meta["n_B"], "mask_sha": meta["mask_sha"],
               "checkpoint_sha": csha, "B": str(B), "B_positive": bool(B > 0),
               "production_reference_mask_agreement": agree, "rho_finite": finite,
               "checkpoint_file_sha256": sha(f"{PANEL}/d_{did}.npz"),
               "mask_file_sha256": sha(f"{PANEL}/m_{did}.npz")}
        ledger["attempts"].append(rec)
        if ok and len(accepted[cell]) < 3:
            accepted[cell].append(rec)
            ledger["accepted"].append(rec)
            print("  ACCEPT %s  n_A=%d n_B=%d [%.0fs]" % (did, meta["n_A"], meta["n_B"], time.time() - t0), flush=True)
        else:
            print("  reject %s (admissibility) [%.0fs]" % (did, time.time() - t0), flush=True)
    if all(len(accepted[c]) >= 3 for c in CELL_ORDER):
        done = True
    if not progressed:
        done = True

n_acc = sum(len(accepted[c]) for c in CELL_ORDER)
PANEL_COMPLETE = n_acc == 12
ledger["n_accepted"] = n_acc
ledger["panel_complete"] = PANEL_COMPLETE
ledger["per_cell_accepted"] = {f"{g}_a{a}": [r["did"] for r in accepted[(g, a)]] for (g, a) in CELL_ORDER}

# seal panel membership
if PANEL_COMPLETE:
    DESC = [r for c in CELL_ORDER for r in accepted[c]]
    panel_lock = {
        "namespace_N": N, "independent_ancestry_blocks": 12, "descendants_per_block": 1,
        "blocks": [{"did": r["did"], "seed": r["seed"], "geometry": r["geometry"], "alloc": r["alloc"],
                    "n_A": r["n_A"], "n_B": r["n_B"], "mask_sha": r["mask_sha"],
                    "checkpoint_sha": r["checkpoint_sha"], "B": r["B"],
                    "checkpoint_file_sha256": r["checkpoint_file_sha256"],
                    "mask_file_sha256": r["mask_file_sha256"]} for r in DESC],
        "balanced_nuisance": {"NEAR_a0": 3, "NEAR_a1": 3, "FAR_a0": 3, "FAR_a1": 3},
        "nuisance_is_balanced_only_no_causal_claim": True,
        "reader_module_sha256": sha("/home/claude/sweep/WSFSCRP00/wsfscrp_core.py"),
        "carrier1": "etcmnfc_core.transpose", "carrier2": "ppai_core.state_cross",
        "dose": "exact historical 1x", "sealed": True,
        "consumed_note": "at the first active byte all twelve are consumed for every future held-out role",
    }
    json.dump(panel_lock, open(f"{OUT}/FRESH_PANEL_MANIFEST.json", "w"), indent=1)
json.dump(ledger, open(f"{OUT}/CONSTRUCTION_START_LEDGER.json", "w"), indent=1)
print("\nconstruction starts: %d/%d | accepted %d/12 | panel_complete=%s"
      % (ledger["construction_starts"], MAX_STARTS, n_acc, PANEL_COMPLETE))
print("per cell:", ledger["per_cell_accepted"])

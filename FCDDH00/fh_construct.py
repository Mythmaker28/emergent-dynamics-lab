"""FCDDH00 G1 construction driver (one role per invocation).

Runs the frozen candidate queue in ascending order. For each candidate ancestry it constructs the
four descendants of the complete (NEAR/FAR) x (H3 member 0/1) factorial from ONE common upstream
precursor, in the frozen randomized descendant run order, each in a fresh process under the
write-ahead charging contract. A defect in ANY descendant rejects the whole four-descendant
candidate block; a rejected candidate is consumed, logged and never resumed.

    python3 -B fh_construct.py DISCOVERY|HOLDOUT
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fh_runner as RUN                                            # noqa: E402

ROLE = sys.argv[1]
assert ROLE in ("DISCOVERY", "HOLDOUT")
TARGET = 12 if ROLE == "DISCOVERY" else 16
BUDGET = 96 if ROLE == "DISCOVERY" else 128

QUEUES = json.load(open(f"{HERE}/DISCOVERY_HOLDOUT_ROLE_QUEUES.json"))
RAND = json.load(open(f"{HERE}/RANDOMIZATION_SEED_AND_ASSIGNMENT_MANIFEST.json"))
QUEUE = QUEUES[f"{ROLE}_CANDIDATE_QUEUE"]

PANEL = f"{HERE}/{ROLE}_PANEL"
MARKS = f"{HERE}/_marks/{ROLE}_construction"
os.makedirs(PANEL, exist_ok=True)
os.makedirs(MARKS, exist_ok=True)
LEDGER = RUN.StartLedger(f"{HERE}/{ROLE}_CANDIDATE_AND_START_LEDGER.jsonl")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

accepted, attempts, spent = [], [], 0
t0 = time.time()

for idx, seed in enumerate(QUEUE):
    if len(accepted) >= TARGET:
        break
    assign = RAND[ROLE][str(idx)]
    cells = assign["cells"]
    order = assign["descendant_run_order"]
    if spent + 4 > BUDGET:
        attempts.append({"candidate_index": idx, "upstream_seed": seed,
                         "status": "NOT_ATTEMPTED__BUDGET_WOULD_BE_EXCEEDED"})
        break
    rec = {"candidate_index": idx, "upstream_seed": seed, "geometry_coin": assign["geometry_coin"],
           "cells": cells, "descendant_run_order": order, "descendants": [], "charged": 0}
    block_ok, precursors = True, set()
    for k in order:
        c = cells[k]
        g, a = c["geometry"], c["allocation"]
        did = f"{seed}_{g}_a{a}"
        ck = f"{PANEL}/d_{did}.npz"
        mk = f"{PANEL}/m_{did}.npz"
        res = LEDGER.run("construction", ROLE, did,
                         [f"{HERE}/fh_cworker.py", str(seed), g, str(a), ck, mk],
                         MARKS, BUDGET, spent)
        spent = LEDGER.counts()["budget_charge"]
        rec["charged"] = spent
        if not res["ok"]:
            rec["descendants"].append({"did": did, "slot": c["slot"], "status": "WORKER_FAILED",
                                       "stderr": res["stderr"][-400:],
                                       "retry_permitted": res["retry_permitted"]})
            block_ok = False
            break
        p = res["payload"]
        precursors.add(p["precursor_sha256"])
        rec["descendants"].append({"did": did, "slot": c["slot"], "serializer_member": c["serializer_member"],
                                   **{kk: p[kk] for kk in p if kk != "ok"}})
        if not p["accepted"]:
            block_ok = False
            break
    rec["distinct_precursor_hashes"] = sorted(precursors)
    rec["identical_upstream_precursor_bytes"] = bool(len(precursors) == 1 and len(rec["descendants"]) == 4)
    rec["cells_complete"] = bool(len({(d.get("geometry"), d.get("allocation")) for d in rec["descendants"]
                                      if d.get("geometry")}) == 4)
    rec["status"] = ("ACCEPTED" if (block_ok and rec["identical_upstream_precursor_bytes"]
                                    and rec["cells_complete"]) else "REJECTED__WHOLE_BLOCK")
    attempts.append(rec)
    if rec["status"] == "ACCEPTED":
        accepted.append(rec)
    print("  cand %d seed %d -> %s  [charged %d/%d] [%.0fs]"
          % (idx, seed, rec["status"], spent, BUDGET, time.time() - t0), flush=True)

counts = LEDGER.counts()
complete = len(accepted) >= TARGET
lock = {
    "role": ROLE, "target_blocks": TARGET, "accepted_blocks": len(accepted),
    "PANEL_COMPLETE": complete,
    f"{ROLE}_CONSTRUCTION_STATUS": "COMPLETE" if complete else "INCOMPLETE",
    "independent_ancestry_blocks": len(accepted), "descendants_per_block": 4,
    "blocks": [{"candidate_index": r["candidate_index"], "upstream_seed": r["upstream_seed"],
                "geometry_coin": r["geometry_coin"],
                "precursor_sha256": r["distinct_precursor_hashes"][0],
                "descendants": [{kk: d[kk] for kk in
                                 ("did", "slot", "serializer_member", "geometry", "allocation",
                                  "checkpoint_state_sha", "mask_sha", "n_A", "n_B", "B_exact",
                                  "checkpoint_file_sha256", "mask_file_sha256",
                                  "production_reference_mask_agreement", "rho_finite",
                                  "g1_precursor_mask_identity", "blob_sha256",
                                  "forcing_trace_sha256", "engine_steps")}
                                for d in r["descendants"]]}
               for r in accepted[:TARGET]],
    "start_ledger": counts, "attempts": len(attempts),
    "sealed_note": "at this lock the descendants are permanently assigned to this role and can "
                   "never be replaced",
}
json.dump(lock, open(f"{HERE}/FCDDH00_{ROLE}_PANEL_LOCK.json", "w"), indent=1)
json.dump({"role": ROLE, "attempts": attempts, "start_ledger": counts,
           "budget": BUDGET, "queue": QUEUE},
          open(f"{HERE}/{ROLE}_CONSTRUCTION_ATTEMPTS.json", "w"), indent=1)
print("\n%s construction: %d/%d blocks | charged %d/%d | raw advances %d"
      % (ROLE, len(accepted), TARGET, counts["charged_total"], BUDGET, counts["raw_advance_total"]))

"""FCDDH00 acquisition driver: twin shams, then the two historical 1x carriers.

    python3 -B fh_acquire.py DISCOVERY|HOLDOUT sham
    python3 -B fh_acquire.py DISCOVERY|HOLDOUT active

Both phases launch the UNCHANGED committed parent worker through `fh_aworker.py` in separate
fresh processes, in the frozen randomized execution order, under the write-ahead charging
contract. Nothing here computes, prints, ranks or opens a delta, M2, TAU, score, label, quotient
or transfer quantity: the archive stays opaque until its raw-only lock is committed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fh_runner as RUN                                            # noqa: E402

ROLE, PHASE = sys.argv[1], sys.argv[2]
assert ROLE in ("DISCOVERY", "HOLDOUT") and PHASE in ("sham", "active")
BUDGET = (96 if ROLE == "DISCOVERY" else 128)
LOCK = json.load(open(f"{HERE}/FCDDH00_{ROLE}_PANEL_LOCK.json"))
assert LOCK["PANEL_COMPLETE"], "panel is not sealed complete; no sham and no active start"
RAND = json.load(open(f"{HERE}/RANDOMIZATION_SEED_AND_ASSIGNMENT_MANIFEST.json"))
if PHASE == "active":
    thr = f"{HERE}/FCDDH00_{ROLE}_THRESHOLD_LOCK.json"
    assert os.path.isfile(thr), "the threshold lock must be committed before any active start"

PANEL = f"{HERE}/{ROLE}_PANEL"
FULL = f"{HERE}/_{ROLE}_{PHASE}_full"
ARCH = f"{HERE}/{ROLE}_{PHASE.upper()}_RAW_ARCHIVE"
MARKS = f"{HERE}/_marks/{ROLE}_{PHASE}"
for p in (FULL, ARCH, MARKS):
    os.makedirs(p, exist_ok=True)
LEDGER = RUN.StartLedger(f"{HERE}/{ROLE}_{PHASE.upper()}_START_LEDGER.jsonl")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

EXPECT = {"SHAM": "identity_copy",
          "CARRIER_1": "etcmnfc_core.transpose(st, I, J)",
          "CARRIER_2": "ppai_core.state_cross(st)"}

jobs = []
for blk in LOCK["blocks"]:
    idx = blk["candidate_index"]
    for k, d in enumerate(blk["descendants"]):
        if PHASE == "sham":
            ops = [("SHAM", "SHAM_0"), ("SHAM", "SHAM_1")]
        else:
            ops = [(o, o) for o in RAND[ROLE][str(idx)]["carrier_run_order"][str(k)]]
        for op, tag in ops:
            jobs.append({"block": blk["upstream_seed"], "candidate_index": idx, "did": d["did"],
                         "op": op, "tag": tag, "ckpt_sha": d["checkpoint_state_sha"]})

spent, man, meta_all = 0, [], {}
t0 = time.time()
for job in jobs:
    did, op, tag = job["did"], job["op"], job["tag"]
    ck, mk = f"{PANEL}/d_{did}.npz", f"{PANEL}/m_{did}.npz"
    name = f"{tag}_{did}" if PHASE == "sham" else f"{op}_{did}"
    out = f"{FULL}/{name}.npz"
    res = LEDGER.run(PHASE, ROLE, name,
                     [f"{HERE}/fh_aworker.py", ck, mk, op, out, job["ckpt_sha"], EXPECT[op]],
                     MARKS, BUDGET, spent)
    spent = LEDGER.counts()["budget_charge"]
    if not res["ok"]:
        print("FATAL: %s failed (charged=%s, retry_permitted=%s)\n%s"
              % (name, res["charged"], res["retry_permitted"], res["stderr"][-800:]), flush=True)
        json.dump({"status": "INCOMPLETE", "failed": name, "start_ledger": LEDGER.counts()},
                  open(f"{HERE}/{ROLE}_{PHASE.upper()}_INCOMPLETE.json", "w"), indent=1)
        raise SystemExit(2)
    m = json.load(open(out + ".meta.json"))
    meta_all[name] = m
    # compact, support-restricted archive: the complete scored trajectory on the fixed support
    d = np.load(out)
    rho, MA, MB = d["rho"], d["MA"], d["MB"]
    sup = np.asarray(MA | MB).ravel()
    idxs = np.nonzero(sup)[0].astype(np.int32)
    vals = np.stack([np.asarray(rho[k]).ravel()[idxs] for k in range(rho.shape[0])])
    outp = f"{ARCH}/{name}.npz"
    np.savez_compressed(outp, rho_support=vals, support_index=idxs, MA=MA, MB=MB)
    man.append({"name": name, "did": did, "op": op, "tag": tag,
                "block_upstream_seed": job["block"],
                "compact_sha256": sha(outp), "full_field_sha256": m["output_sha256"],
                "terminal_state_sha": m["terminal_state_sha"],
                "per_time_state_sha": m["per_time_state_sha"],
                "n_frames": m["n_frames"], "scored_times": m["scored_times"],
                "touched_fields_at_t0": m["touched_fields_at_t0"],
                "touch_set_ok": m["touch_set_ok"], "input_unchanged": m["input_unchanged"],
                "rho_untouched_at_t0": m["rho_untouched_at_t0"], "rho_finite": m["rho_finite"],
                "B_exact": m["B_exact"], "mask_sha": m["mask_sha"],
                "expected_callable": m["expected_callable"], "support_sites": int(idxs.size)})
    print("  %-28s ok  charged %3d/%d  [%.0fs]" % (name, spent, BUDGET, time.time() - t0), flush=True)

counts = LEDGER.counts()
expect_n = 4 * len(LOCK["blocks"]) * 2
ok = len(man) == expect_n
json.dump({"role": ROLE, "phase": PHASE, "rows": len(man), "expected_rows": expect_n,
           "COMPLETE": ok, "start_ledger": counts,
           "labels_decoded": False, "scores_computed": False,
           "manifest": man},
          open(f"{HERE}/{ROLE}_{PHASE.upper()}_RAW_MANIFEST.json", "w"), indent=1)
print("\n%s %s: %d/%d rows | charged %d/%d | raw advances %d | COMPLETE=%s"
      % (ROLE, PHASE, len(man), expect_n, counts["charged_total"], BUDGET,
         counts["raw_advance_total"], ok))

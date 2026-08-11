"""FSQBT00 Section 7 -- acquire the 24 historical-1x carrier rows WRITE-ONLY under opaque ids,
via the parent's committed write-only worker in separate fresh processes. No delta/M2/score/label
is computed or opened here. Runtime physical oracle per row. 24 active starts."""
from __future__ import annotations
import json, hashlib, os, sys, subprocess, time
import numpy as np
sys.path.insert(0, "/home/claude/sweep"); sys.path.insert(0, "/home/claude/sweep/WSFSCRP00")
sys.path.insert(0, "/home/claude/sweep/PPAI"); sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/ETPC")
import wsfscrp_core as Z
OUT = "/home/claude/sweep/FSQBT00"
ARAW = f"{OUT}/active_raw_full"; os.makedirs(ARAW, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
WORKER = "/home/claude/sweep/FWL2CF00/fw_worker.py"
t0 = time.time()

FRZ = json.load(open(f"{OUT}/FSQBT00_MASTER_FREEZE_HASHES.json"))
assert sha(f"{OUT}/FSQBT00_MASTER_FREEZE.md") == FRZ["hashes"]["FSQBT00_MASTER_FREEZE.md"], "freeze mutated"
LOCK = json.load(open(f"{OUT}/PREACTIVE_TRANSFER_LOCK.json"))
SCH = LOCK["opaque_active_schedule"]
EXPECT = {"CARRIER_1": "etcmnfc_core.transpose(st, I, J)", "CARRIER_2": "ppai_core.state_cross(st)"}

START_LOG = open(f"{OUT}/START_AND_ACCESS_LEDGER.jsonl", "a")
def start_enter(tag):
    START_LOG.write(json.dumps({"kind": "active", "tag": tag}) + "\n"); START_LOG.flush(); os.fsync(START_LOG.fileno())

man, oracle = [], []
n_active = 0
for oid in sorted(SCH):
    row = SCH[oid]
    ck = f"{OUT}/{row['checkpoint']}"; mk = f"{OUT}/{row['mask']}"; arm = row["arm"]
    st0 = Z.load(ck); exp_sha = Z.full_sha(st0)
    out = f"{ARAW}/{oid}.npz"
    for p in (out, out + ".meta.json"):
        if os.path.exists(p):
            os.remove(p)
    start_enter(oid)
    r = subprocess.run([sys.executable, WORKER, ck, mk, arm, out, exp_sha, EXPECT[arm]],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"active worker {oid} failed: " + r.stderr[-800:])
    res = json.loads(r.stdout.strip())
    n_active += 1
    meta = json.load(open(out + ".meta.json"))
    # runtime physical oracle (no score): touch set, input unchanged, structural zero handled inside
    ok = (meta["touch_set_ok"] and meta["input_unchanged"] and meta["rho_untouched_at_t0"]
          and meta["rho_finite"] and meta["touched_fields_at_t0"] == ["Mf"])
    post_distinct = meta["terminal_state_sha"] != exp_sha
    oracle.append({"opaque": oid, "arm": arm, "touch_set_ok": meta["touch_set_ok"],
                   "touched_fields_at_t0": meta["touched_fields_at_t0"],
                   "input_unchanged": meta["input_unchanged"], "rho_untouched_at_t0": meta["rho_untouched_at_t0"],
                   "post_intervention_distinct_terminal": bool(post_distinct),
                   "expected_callable": meta["expected_callable"], "runtime_ok": bool(ok)})
    man.append({"opaque": oid, "file": f"{oid}.npz", "output_sha256": res["sha"],
                "terminal_state_sha": meta["terminal_state_sha"], "n_frames": meta["n_frames"]})
    print("  active %s arm=%s touch=%s ok=%s [%.0fs]" % (oid, arm, meta["touched_fields_at_t0"], ok, time.time() - t0), flush=True)

# compact to support-restricted (no scores; just raw rho on support)
DST = f"{OUT}/active_raw"; os.makedirs(DST, exist_ok=True)
compact = []
for oid in sorted(SCH):
    d = np.load(f"{ARAW}/{oid}.npz"); rho, MA, MB = d["rho"], d["MA"], d["MB"]
    sup = np.asarray(MA | MB).ravel(); idx = np.nonzero(sup)[0].astype(np.int32)
    vals = np.stack([np.asarray(rho[k]).ravel()[idx] for k in range(rho.shape[0])])
    outp = f"{DST}/{oid}.npz"
    if os.path.exists(outp):
        os.remove(outp)
    np.savez_compressed(outp, rho_support=vals, support_index=idx, MA=MA, MB=MB)
    compact.append({"opaque": oid, "file": f"{oid}.npz", "sha256": sha(outp), "support_sites": int(idx.size)})

ALL_OK = all(o["runtime_ok"] for o in oracle) and all(o["post_intervention_distinct_terminal"] for o in oracle)
json.dump({"n_active_starts": n_active, "opaque_raw_full_manifest": man,
           "compact_support_restricted": compact,
           "labels_decoded": False, "scores_computed": False,
           "runtime_oracle_all_ok": ALL_OK},
          open(f"{OUT}/FRESH_ACTIVE_RAW_MANIFEST.json", "w"), indent=1)
json.dump({"rows": oracle, "all_ok": ALL_OK, "note": "touch-set {Mf} only, rho untouched at t0, "
           "input checkpoint unchanged, terminal state distinct from source; no score computed"},
          open(f"{OUT}/ACTIVE_RUNTIME_ORACLE_REPORT.json", "w"), indent=1)
print("\nactive starts %d/24 | runtime oracle all ok: %s | labels_decoded=False scores_computed=False"
      % (n_active, ALL_OK))

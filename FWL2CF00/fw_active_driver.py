"""FWL2CF00 Section 5.2 -- the sealed 32-start active schedule, executed ONCE.
Write-only with respect to science: this driver serialises and hashes raw bytes and never computes,
prints, ranks or opens M2, TAU, quotient, transfer or factor scores. Outputs are named by OPAQUE id
so that no factor label appears in the raw run table."""
from __future__ import annotations
import json, hashlib, os, subprocess, sys, time
OUT = "/home/claude/sweep/FWL2CF00"; W2 = "/home/claude/sweep/WL2SMF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
AP = json.load(open(f"{OUT}/FWL2CF00_ACTIVE_PANEL_LOCK.json"))
CS = json.load(open(f"{OUT}/FWL2CF00_CANONICAL_SHAM_SERIES_LOCK.json"))
assert sha(f"{OUT}/FWL2CF00_CANONICAL_SHAM_SERIES_LOCK.json") == AP["canonical_sham_series_lock_sha256"]
assert CS["reconstruction_disposition"] == "SHAM_REFERENCE_RECONSTRUCTION_PASS_16_OF_16"
D = {d["descendant_id"]: d for d in AP["descendants"]}
EXPECT = {"CARRIER_1": AP["arms"]["CARRIER_1"]["worker_expect_callable"],
          "CARRIER_2": AP["arms"]["CARRIER_2"]["worker_expect_callable"]}
os.makedirs(f"{OUT}/active", exist_ok=True)
LOG = f"{OUT}/active/_START_ENTER.log"
n, res, t0 = 0, [], time.time()
for did, op in AP["schedule_32"]:
    oid = AP["opaque_ids"][f"{did}|{op}"]
    outp = f"{OUT}/active/{oid}.npz"
    assert not os.path.exists(outp), "predeclared output path already exists"
    n += 1
    with open(LOG, "a") as fh:
        fh.write(json.dumps({"i": n, "kind": "ACTIVE", "opaque": oid}) + "\n")
        fh.flush(); os.fsync(fh.fileno())
    assert n <= 32, "ACTIVE_CARRIER_START_BUDGET_PROTOCOL_BREACH"
    r = subprocess.run([sys.executable, f"{OUT}/fw_worker.py",
                        f"{W2}/checkpoints/d_{did}.npz", f"{W2}/checkpoints/m_{did}.npz",
                        op, outp, D[did]["checkpoint_sha"], EXPECT[op]],
                       capture_output=True, text=True)
    ok = r.returncode == 0 and os.path.exists(outp)
    res.append({"i": n, "opaque": oid, "returncode": r.returncode, "ok": ok,
                "stderr": r.stderr[-300:] if r.returncode else ""})
    print("  %2d/32  %s  %s [%.0fs]" % (n, oid, "ok" if ok else "FAIL " + r.stderr[-160:],
                                        time.time() - t0), flush=True)
json.dump({"n_starts": n, "cap": 32, "all_ok": all(x["ok"] for x in res), "results": res},
          open(f"{OUT}/active/_driver_result.json", "w"), indent=1)
print("ACTIVE starts:", n, "of 32 | all ok:", all(x["ok"] for x in res))

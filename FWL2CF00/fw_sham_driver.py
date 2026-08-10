"""FWL2CF00 Section 4.3 -- 16 canonical SHAM_0 replays. One fresh process per continuation.
Write-only with respect to science."""
from __future__ import annotations
import json, hashlib, os, subprocess, sys, time
OUT = "/home/claude/sweep/FWL2CF00"; W2 = "/home/claude/sweep/WL2SMF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
LOCK = json.load(open(f"{OUT}/FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json"))
assert sha(f"{OUT}/FWL2CF00_MASTER_FREEZE.md") == LOCK["master_freeze_sha256"]
os.makedirs(f"{OUT}/sham", exist_ok=True)
LOG = f"{OUT}/sham/_START_ENTER.log"
n = 0; t0 = time.time(); res = []
for did in LOCK["schedule"]:
    d = LOCK["descendants"][did]
    outp = f"{OUT}/sham/{did}.npz"
    assert not os.path.exists(outp), "predeclared output path already exists"
    n += 1
    with open(LOG, "a") as fh:                      # durable, fsynced, BEFORE the launch
        fh.write(json.dumps({"i": n, "kind": "SHAM_0_REPLAY", "descendant": did,
                             "out": os.path.basename(outp)}) + "\n")
        fh.flush(); os.fsync(fh.fileno())
    assert n <= 16, "SHAM_RECONSTRUCTION_START_BUDGET_PROTOCOL_BREACH"
    r = subprocess.run([sys.executable, f"{OUT}/fw_worker.py",
                        f"{W2}/checkpoints/d_{did}.npz", f"{W2}/checkpoints/m_{did}.npz",
                        "SHAM", outp, d["checkpoint_sha_full_state"], "identity_copy"],
                       capture_output=True, text=True)
    ok = r.returncode == 0 and os.path.exists(outp)
    res.append({"descendant": did, "returncode": r.returncode, "ok": ok,
                "stderr": r.stderr[-300:] if r.returncode else ""})
    print("  %-16s %s [%.0fs]" % (did, "ok" if ok else "FAIL " + r.stderr[-200:],
                                  time.time() - t0), flush=True)
json.dump({"n_starts": n, "cap": 16, "results": res,
           "all_ok": all(x["ok"] for x in res)},
          open(f"{OUT}/sham/_driver_result.json", "w"), indent=1)
print("SHAM_0 replays:", n, "of 16 | all ok:", all(x["ok"] for x in res))

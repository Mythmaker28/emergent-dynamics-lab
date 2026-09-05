"""OMLDCT02 — device driver running BOTH E3 classifiers over the developmental LAW_C removal
archives. Sharded and budgeted for the 45-second bridge limit. Archives never leave the device."""
import sys, os, json, time
BASE, SHARD, NSHARD, BUDGET, RAW, OUTD = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                          float(sys.argv[4]), sys.argv[5], sys.argv[6])
os.environ["OMLDCT02_REPO"] = BASE; os.environ["LDFMA01_REPO"] = BASE
sys.path.insert(0, os.path.join(BASE, "OMLDCT02", "code"))
import numpy as np
import omldct02_e3_a as AA, omldct02_e3_b as B
assert B.L == 36 and B.CORE_R == 5.0
files = sorted(f for f in os.listdir(RAW) if f.endswith(".npz"))
mine = [f for i, f in enumerate(files) if i % NSHARD == SHARD]
os.makedirs(OUTD, exist_ok=True)
t0 = time.time(); done = skipped = 0
for f in mine:
    op = os.path.join(OUTD, f[:-4] + ".json")
    if os.path.exists(op): skipped += 1; continue
    if time.time() - t0 > BUDGET: break
    p = os.path.join(RAW, f)
    z = np.load(p, allow_pickle=True); meta = json.loads(str(z["meta"][0])); z.close()
    t_m = meta.get("t_m")
    dcells = (meta.get("intervention") or {}).get("daughter_cells_after")
    rec = {"tag": f[:-4], "t_m": t_m, "has_daughter_cells": dcells is not None}
    if t_m is None or dcells is None:
        rec["A"] = {"OK": False, "REASON": "NO_REMOVAL_LEDGER"}
        rec["B"] = {"OK": False, "REASON": "NO_REMOVAL_LEDGER"}
    else:
        ta = time.time(); rec["A"] = AA.e3(p, t_m, dcells); rec["A_seconds"] = round(time.time() - ta, 2)
        tb = time.time(); rec["B"] = B.e3(p, t_m, dcells); rec["B_seconds"] = round(time.time() - tb, 2)
    tmp = op + ".part"
    with open(tmp, "w") as fh: json.dump(rec, fh)
    os.replace(tmp, op); done += 1
rem = sum(1 for f in mine if not os.path.exists(os.path.join(OUTD, f[:-4] + ".json")))
print("SHARD %d/%d files=%d done=%d skipped=%d remaining=%d %.0fs"
      % (SHARD, NSHARD, len(mine), done, skipped, rem, time.time() - t0))

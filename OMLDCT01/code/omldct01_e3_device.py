"""Device driver for classifier B over the developmental LAW_C removal archives.
Sharded and budgeted because the bridge kills a call at 45 s and cannot keep a background process.
Writes one small JSON per world; the archives never leave the device."""
import sys, os, json, time
BASE, SHARD, NSHARD, BUDGET, RAW, OUTD = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                          float(sys.argv[4]), sys.argv[5], sys.argv[6])
os.environ["OMLDCT01_REPO"] = BASE
sys.path.insert(0, os.path.join(BASE, "OMLDCT01", "code"))
import omldct01_e3_b as B
assert B.L == 36 and B.CORE_R == 5.0, (B.L, B.CORE_R)
files = sorted(f for f in os.listdir(RAW) if f.endswith(".npz"))
mine = [f for i, f in enumerate(files) if i % NSHARD == SHARD]
os.makedirs(OUTD, exist_ok=True)
t0 = time.time(); done = skipped = 0
for f in mine:
    op = os.path.join(OUTD, f[:-4] + ".json")
    if os.path.exists(op): skipped += 1; continue
    if time.time() - t0 > BUDGET: break
    r = B.e3(os.path.join(RAW, f))
    r["tag"] = f[:-4]
    tmp = op + ".part"
    with open(tmp, "w") as fh: json.dump(r, fh)
    os.replace(tmp, op); done += 1
rem = sum(1 for f in mine if not os.path.exists(os.path.join(OUTD, f[:-4] + ".json")))
print("SHARD %d/%d files=%d done=%d skipped=%d remaining=%d %.0fs"
      % (SHARD, NSHARD, len(mine), done, skipped, rem, time.time() - t0))

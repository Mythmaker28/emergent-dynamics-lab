"""TLMR01 — DEVICE-SIDE DRIVER. Non-load-bearing: it computes nothing.

It walks the retained archives and calls the FROZEN tlmr01_offline.measure_world on each, writing
that function's return value verbatim to one JSON per world. Every scientific decision is made by
the frozen module; this file only iterates, times, and serialises.

It runs on the device because the 512 archives live there and the bridge cannot carry 800 MB into
the container. The split is along the existing frozen module boundary: tlmr01_offline needs only
numpy, tlmr01_analyse needs scipy and runs in the container on these outputs.
"""
import sys, os, json, time, glob, hashlib, math, builtins
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

# PATH SHIM, DECLARED. tlmr01_offline.py reads its frozen constants from the absolute path
# /home/claude/edl/PQEC01/out/PQEC01_MASTER_FREEZE.json, which cannot be created on this device.
# The frozen module is NOT modified: its bytes are the ones the master freeze hashes. Only the
# lookup of that one path is redirected, during import, to the hash-verified copy shipped beside
# this driver. The constants that result are then checked against the frozen physics binding, so
# the redirection is verified rather than trusted.
_open = builtins.open
def _shim(p, *a, **k):
    if isinstance(p, str) and p.startswith("/home/claude/edl/"):
        p = os.path.join(BASE, p[len("/home/claude/edl/"):])
    return _open(p, *a, **k)
builtins.open = _shim
try:
    import tlmr01_offline as OFF
finally:
    builtins.open = _open

EXPECT = {"L": 36, "CORE_R": 5.0, "T_HORIZON": 11000, "NEED": 250,
          "LATEST_ALLOWED_TRIGGER": 6500}
assert OFF.L == EXPECT["L"], (OFF.L, EXPECT["L"])
assert OFF.CORE_R == EXPECT["CORE_R"], (OFF.CORE_R, EXPECT["CORE_R"])
assert OFF.T_HORIZON == EXPECT["T_HORIZON"], (OFF.T_HORIZON, EXPECT["T_HORIZON"])
assert OFF.NEED == EXPECT["NEED"], (OFF.NEED, EXPECT["NEED"])
assert OFF.LATEST_ALLOWED_TRIGGER == EXPECT["LATEST_ALLOWED_TRIGGER"]
assert OFF.F_PRIMARY == 1.0 - 1.0 / math.e
assert OFF.sI == 5
print("frozen constants verified: L=%d CORE_R=%s T_HORIZON=%d NEED=%d LATEST=%d sI=%d"
      % (OFF.L, OFF.CORE_R, OFF.T_HORIZON, OFF.NEED, OFF.LATEST_ALLOWED_TRIGGER, OFF.sI),
      flush=True)

RAW = sys.argv[1]
OUTD = sys.argv[2]
BUDGET = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
NPROC = int(sys.argv[4]) if len(sys.argv) > 4 else 1
SHARD = int(sys.argv[5]) if len(sys.argv) > 5 else 0
os.makedirs(OUTD, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

paths = sorted(glob.glob(os.path.join(RAW, "TLMR01_*_P_*.npz")))
paths = [p for i, p in enumerate(paths) if i % NPROC == SHARD]
print("archives in this shard: %d" % len(paths), flush=True)
t0 = time.time()
done = 0
for p in paths:
    if time.time() - t0 > BUDGET:
        print("BUDGET REACHED after %d" % done, flush=True); break
    tag = os.path.basename(p)[:-4]
    op = os.path.join(OUTD, tag + ".json")
    if os.path.exists(op):
        done += 1; continue
    t1 = time.time()
    r = OFF.measure_world(p)
    r["_archive_sha256"] = sha(p)
    r["_measure_seconds"] = round(time.time() - t1, 2)
    tmp = op + ".part"
    with open(tmp, "w") as f: json.dump(r, f)
    os.replace(tmp, op)
    done += 1
    if done % 10 == 0 or done == len(paths):
        print("  %d/%d  %.0fs elapsed" % (done, len(paths), time.time() - t0), flush=True)
print("DONE %d in %.0fs" % (done, time.time() - t0), flush=True)

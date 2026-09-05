"""FDFLT01 — frozen scientific execution at point B1.

THE EXECUTION LAW IS NOT REIMPLEMENTED. This module imports the frozen PQEC01 runner and
calls its own run_world, so the engine, LawSpec, observer, scheduler order, horizon and every
stop rule are literally the bytes that generated the historical B1 worlds. Only three things
differ, none of them physical: the raw output directory, the tag prefix, and the outcome
firewall applied to what leaves the worker.

OUTCOME FIREWALL (FDFLT01 §7). The live channel and the run ledger expose ONLY:
  opaque arm token, completion flag, predeclared technical-failure flag, checksum-written flag.
They expose NO seed, no success, no birth count, no centre count, no stop reason, no
steps_recorded, no runtime and no file size.
"""
from __future__ import annotations
import hashlib, json, os, sys

REPO = "/home/claude/edl"
RAW = "/home/claude/FDFLT01/raw"
OUT = f"{REPO}/FDFLT01/out"
sys.path.insert(0, f"{REPO}/PQEC01/code")
import pqec01_run as PR                                                        # noqa: E402

PR.RAW = RAW                        # redirect the frozen writer; nothing physical changes
os.makedirs(RAW, exist_ok=True)

SEEDS = json.load(open(f"{OUT}/FDFLT01_SEED_MANIFEST.json"))["SEEDS"]
FREEZE_POINT = json.load(open(f"{REPO}/PQEC01/out/PQEC01_MASTER_FREEZE.json"))["PHASE_B"]["POINT_B1"]
KY, MUY = FREEZE_POINT["kY"], FREEZE_POINT["muY"]

def token(kind, index):
    """Opaque randomised arm token. Carries no scientific information."""
    return hashlib.sha256(("FDFLT01|token|%s|%d" % (kind, index)).encode()).hexdigest()[:16]

def jobs(kind="PRIMARY"):
    return [("F", "B1", r["index"], r["seed"], KY, MUY, "FDFLT01_" + kind) for r in SEEDS[kind]]

TECHNICAL_FAILURE_DEFINITIONS = [
    "returncode != 0 (process interruption or unhandled exception)",
    "archive absent after the write",
    "schema_ok False (corrupt or incomplete serialization)",
    "engine_invariants_ok False (engine invariant violation preventing a readable outcome)",
    "sha256 recomputation over the written bytes disagrees with the value recorded at write time",
]

def run_one(job):
    rec = PR.run_world(job)
    kind = job[6].replace("FDFLT01_", "")
    ok_path = rec.get("exists") and rec.get("sha256")
    checksum_ok = False
    if ok_path and os.path.exists(rec["path"]):
        h = hashlib.sha256()
        with open(rec["path"], "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        checksum_ok = (h.hexdigest() == rec["sha256"])
    technical_failure = not (rec.get("returncode") == 0 and rec.get("schema_ok")
                             and rec.get("engine_invariants_ok") and checksum_ok)
    # ---- SEALED record: written to a sealed file, never to the live ledger ----
    sealed = dict(rec); sealed["checksum_verified"] = checksum_ok
    # ---- FIREWALLED record: this is all that reaches the live channel and the ledger ----
    public = {"arm_token": token(kind, job[2]), "kind": kind,
              "completed": bool(rec.get("returncode") == 0),
              "technical_failure": bool(technical_failure),
              "checksum_written": bool(checksum_ok)}
    return public, sealed

def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "PRIMARY"
    js = jobs(kind)
    import multiprocessing as mp
    led = open(f"{OUT}/FDFLT01_RUN_LEDGER.jsonl", "a")
    seal = open("/home/claude/FDFLT01/sealed_records.jsonl", "a")
    done = 0
    with mp.Pool(2) as pool:
        for public, sealed in pool.imap_unordered(run_one, js):
            led.write(json.dumps(public) + "\n"); led.flush()
            seal.write(json.dumps(sealed, default=str) + "\n"); seal.flush()
            done += 1
            print("  [%3d/%3d] arm=%s completed=%s technical_failure=%s checksum=%s"
                  % (done, len(js), public["arm_token"], public["completed"],
                     public["technical_failure"], public["checksum_written"]), flush=True)
    led.close(); seal.close()
    print("%s: %d starts attempted" % (kind, len(js)))

if __name__ == "__main__":
    main()

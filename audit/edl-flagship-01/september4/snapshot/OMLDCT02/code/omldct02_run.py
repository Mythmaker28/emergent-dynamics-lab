"""OMLDCT02 — the campaign runner.

FIREWALL. The live channel carries only an opaque token, completion, the predeclared technical
fields, and the arm-instance accounting. No endpoint value, no duration, no exposure and no count of
admissible pairs beyond what the accrual rule itself needs reaches the operator while worlds are
still running. The full per-seed record goes to a sealed file that is not read until C3.

BATCHES. At most MAX_UNEXTERNALISED arm instances may sit in the container un-externalised. After
each batch the archives are read back, their sha256 re-verified against what was written, and the
unexternalised count must return to zero before the next batch starts.

GUARD. Every construction passes omldct02_guard.assert_allowed first.

SCIPY SENTINEL. scipy reaches the process through the frozen engine's import of fmrt01_endpoint.
The only scipy call in that file is binom.ppf inside survivor_upper(), which is on no OMLDCT02 path.
The sentinel wraps it and records whether it is ever actually called, so the claim is measured
rather than asserted.
"""
from __future__ import annotations
import json, os, sys, time, hashlib, traceback

REPO = os.environ.get("OMLDCT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "OMLDCT02", "code"))
import omldct02_guard as G

OUT = f"{REPO}/OMLDCT02/out"
WORK = f"{REPO}/OMLDCT02/work"
RAW = os.environ.get("OMLDCT02_RAW", "/home/claude/OMLDCT02_raw")
SEALED = f"{WORK}/OMLDCT02_SEALED_LEDGER.jsonl"
STATE = f"{WORK}/OMLDCT02_RUN_STATE.json"

TARGET_VALID_PAIRED_BLOCKS = 41
MAX_PRIMARY_ARM_INSTANCES = 512
MAX_UNEXTERNALISED = 16

_SCIPY_CALLS = {"binom_ppf": 0}

def install_scipy_sentinel():
    try:
        from scipy.stats import binom
        orig = binom.ppf
        def wrapped(*a, **k):
            _SCIPY_CALLS["binom_ppf"] += 1
            return orig(*a, **k)
        binom.ppf = wrapped
        return True
    except Exception:
        return False

def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"next_index": 0, "valid_pairs": 0, "instances_used": 0.0, "seeds_attempted": 0,
            "unexternalised_arm_instances": 0, "externalised_batches": 0,
            "batch_open": [], "STOPPED": None}

def save_state(s):
    tmp = STATE + ".part"
    with open(tmp, "w") as fh: json.dump(s, fh, indent=1)
    os.replace(tmp, STATE)

def seal(rec):
    with open(SEALED, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")

def token(index):
    return hashlib.sha256(f"OMLDCT02|{index}".encode()).hexdigest()[:12]

def run_batch(max_seconds=900, max_seeds=None):
    """Runs seeds in frozen order until the batch's unexternalised budget is full, the accrual rule
    stops, or the time budget expires. Returns a LIVE-SAFE summary."""
    import omldct02_fork as F
    seeds = json.load(open(f"{OUT}/OMLDCT02_SEED_MANIFEST.json"))["BASE_SEEDS"]
    s = load_state()
    if s.get("STOPPED"): return {"STOPPED": s["STOPPED"], **{k: s[k] for k in
        ("next_index", "valid_pairs", "instances_used", "seeds_attempted")}}
    if s["unexternalised_arm_instances"] > 0:
        return {"REFUSED": "a previous batch is not externalised",
                "unexternalised_arm_instances": s["unexternalised_arm_instances"],
                "batch_open": s["batch_open"]}
    sci = install_scipy_sentinel()
    os.makedirs(RAW, exist_ok=True); os.makedirs(WORK, exist_ok=True)
    t0 = time.time(); started = []
    n_started = 0
    while True:
        if s["valid_pairs"] >= TARGET_VALID_PAIRED_BLOCKS:
            s["STOPPED"] = "TARGET_REACHED"; break
        if s["instances_used"] + 2.0 > MAX_PRIMARY_ARM_INSTANCES:
            s["STOPPED"] = "HARD_ARM_INSTANCE_CEILING"; break
        if s["next_index"] >= len(seeds):
            s["STOPPED"] = "BASE_SEED_LIST_EXHAUSTED"; break
        if s["unexternalised_arm_instances"] >= MAX_UNEXTERNALISED: break
        if time.time() - t0 > max_seconds: break
        if max_seeds is not None and n_started >= max_seeds: break
        row = seeds[s["next_index"]]
        idx, seed = row["index"], row["seed"]
        try:
            rec, ps, ph = F.run_pair(seed, idx, RAW)
            tech = False
        except G.PreC2ScientificScaleRefused:
            raise
        except Exception:
            rec = {"index": idx, "seed": seed, "technical_failure": True,
                   "ERROR": traceback.format_exc()[-800:]}
            tech = True; ps = ph = None
        rec["token"] = token(idx)
        rec["technical_failure"] = bool(tech or not rec.get("integrity_ok_prefix", True))
        seal(rec)
        s["seeds_attempted"] += 1; s["next_index"] = idx + 1
        s["instances_used"] = round(s["instances_used"] + rec.get("instance_cost", 0.0), 5)
        if rec.get("ADMISSIBLE"):
            s["valid_pairs"] += 1
            s["unexternalised_arm_instances"] += 2
            s["batch_open"].extend([rec["ARCHIVES"]["SELECTIVE"]["tag"], rec["ARCHIVES"]["SHAM"]["tag"]])
        started.append({"token": rec["token"], "admissible": bool(rec.get("ADMISSIBLE")),
                        "technical_failure": rec["technical_failure"],
                        "instance_cost": rec.get("instance_cost")})
        n_started += 1
    s["scipy_binom_ppf_calls"] = _SCIPY_CALLS["binom_ppf"]
    s["scipy_sentinel_installed"] = sci
    save_state(s)
    return {"batch_seeds": len(started), "elapsed_s": round(time.time() - t0, 1),
            "next_index": s["next_index"], "seeds_attempted": s["seeds_attempted"],
            "valid_pairs": s["valid_pairs"], "instances_used": s["instances_used"],
            "unexternalised_arm_instances": s["unexternalised_arm_instances"],
            "STOPPED": s.get("STOPPED"),
            "scipy_binom_ppf_calls": _SCIPY_CALLS["binom_ppf"],
            "batch_open": s["batch_open"]}

def verify_batch_readback():
    """Re-read every archive of the open batch and re-verify its sha256 against the sealed record."""
    if not os.path.exists(SEALED): return {"n": 0, "OK": 0, "FAILED": 0, "detail": []}
    want = {}
    for line in open(SEALED):
        r = json.loads(line)
        for a in (r.get("ARCHIVES") or {}).values(): want[a["tag"]] = a
    s = load_state(); out = []
    for tag in s["batch_open"]:
        a = want.get(tag)
        if not a: out.append({"tag": tag, "OK": False, "why": "not in the sealed ledger"}); continue
        p = a["path"]
        if not os.path.exists(p): out.append({"tag": tag, "OK": False, "why": "missing"}); continue
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
        out.append({"tag": tag, "OK": h.hexdigest() == a["sha256"], "bytes": os.path.getsize(p),
                    "sha256": h.hexdigest()})
    return {"n": len(out), "OK": sum(1 for x in out if x["OK"]),
            "FAILED": sum(1 for x in out if not x["OK"]), "detail": out}

def close_batch():
    """Called only after the batch has been written to Windows and read back successfully."""
    s = load_state()
    s["externalised_batches"] += 1
    s["unexternalised_arm_instances"] = 0
    s["batch_open"] = []
    save_state(s)
    return {"externalised_batches": s["externalised_batches"], "unexternalised_arm_instances": 0}

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=900)
    ap.add_argument("--max-seeds", type=int, default=None)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--close", action="store_true")
    a = ap.parse_args()
    if a.verify: print(json.dumps(verify_batch_readback(), indent=1))
    elif a.close: print(json.dumps(close_batch(), indent=1))
    else: print(json.dumps(run_batch(a.seconds, a.max_seeds), indent=1))

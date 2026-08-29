"""TBRT02 — rebuild the three archives the twenty-third rollback destroyed.

Declared in TBRT02/out/TBRT02_RECONSTRUCTION_DECLARATION.md before this file was run. It reads
the sealed ledger, re-executes the three already-counted seeds into a QUARANTINE directory, and
compares every produced archive to the sha256 the ledger sealed when the archive was first
written. Only a full nine-for-nine match promotes the files into TBRT02_raw.

It never opens the sealed ledger for writing. It adds no seed, no line, no cost.
"""
from __future__ import annotations
import os, sys, json, glob, shutil, hashlib, time
REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
sys.path.insert(0, os.path.join(REPO, "TBRT02/code"))

LOST = [793, 827, 866]
QUAR = "/home/claude/TBRT02_reconstruct"
RAW = os.environ.get("TBRT02_RAW", "/home/claude/TBRT02_raw")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sealed():
    rows = [json.loads(l) for p in sorted(glob.glob(f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_*.jsonl"))
            for l in open(p) if l.strip()]
    return {r["index"]: r for r in rows if r.get("index") in LOST}


def main(only=None):
    os.makedirs(QUAR, exist_ok=True)
    import tbrt02_fork as F
    want = sealed()
    out = []
    for idx in (LOST if only is None else [only]):
        w = want[idx]
        t0 = time.time()
        rec, arcs = F.one_seed(idx, w["seed"], QUAR)
        r = {"index": idx, "seed": w["seed"],
             "t_m_sealed": w["t_m"], "t_m_rebuilt": rec.get("t_m"),
             "t_m_matches": rec.get("t_m") == w["t_m"],
             "admissible_rebuilt": rec.get("ADMISSIBLE"),
             "runtime_s": round(time.time() - t0, 1), "arms": {}}
        for arm, a in sorted(w["ARCHIVES"].items()):
            got = arcs.get(arm)
            p = got.get("path") if got else None
            d = {"sealed_sha256": a["sha256"], "sealed_bytes": a["bytes"]}
            if p and os.path.exists(p):
                d["rebuilt_sha256"] = sha(p)
                d["rebuilt_bytes"] = os.path.getsize(p)
                d["MATCHES"] = d["rebuilt_sha256"] == a["sha256"]
            else:
                d["rebuilt_sha256"] = None; d["MATCHES"] = False
            r["arms"][arm] = d
        r["ALL_THREE_ARMS_MATCH"] = all(v["MATCHES"] for v in r["arms"].values()) and r["t_m_matches"]
        out.append(r)
        print(json.dumps({k: v for k, v in r.items() if k != "arms"}, sort_keys=True), flush=True)
        for arm, v in r["arms"].items():
            print("   ", arm, "MATCH" if v["MATCHES"] else "MISMATCH", flush=True)
        json.dump(out, open(f"{REPO}/TBRT02/work/RECONSTRUCTION_{idx}.json", "w"), indent=1)
    return out


def promote():
    """Move quarantined archives into TBRT02_raw — only for triples that matched nine for nine."""
    res = []
    for idx in LOST:
        p = f"{REPO}/TBRT02/work/RECONSTRUCTION_{idx}.json"
        if os.path.exists(p):
            res += json.load(open(p))
    seen = {}
    for r in res:
        seen[r["index"]] = r
    moved, refused = [], []
    for idx, r in sorted(seen.items()):
        if not r["ALL_THREE_ARMS_MATCH"]:
            refused.append(idx); continue
        for f in glob.glob(f"{QUAR}/TBRT02_i{idx:04d}_*.npz"):
            shutil.move(f, os.path.join(RAW, os.path.basename(f)))
            moved.append(os.path.basename(f))
    print(json.dumps({"promoted_files": moved, "refused_indices": refused,
                      "RULE": "a triple is promoted only if all three arms and t_m match the seal"},
                     indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "promote":
        promote()
    else:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else None)

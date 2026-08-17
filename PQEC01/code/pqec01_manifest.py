"""PQEC01 — raw manifest and checksums over every scientific archive."""
from __future__ import annotations
import glob, hashlib, json, os, sys
import numpy as np
RAW = "/home/claude/PQEC01/raw"
OUT = "/home/claude/edl/PQEC01/out"
FR = json.load(open(f"{OUT}/PQEC01_MASTER_FREEZE.json"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    frozen = {r["seed"]: (k, r["index"], r["split"])
              for k, v in FR["SEED_RULE"]["SEEDS"].items() for r in v}
    rows, sums = [], []
    for p in sorted(glob.glob(f"{RAW}/*.npz")):
        z = np.load(p, allow_pickle=True)
        m = json.loads(str(z["meta"][0]))
        d = sha(p)
        rows.append({"file": os.path.basename(p), "bytes": os.path.getsize(p), "sha256": d,
                     "seed": m["seed"], "phase": m["phase"], "point": m["point"],
                     "index": m["index"], "split": m["split"], "kY": m["kY"], "muY": m["muY"],
                     "steps_recorded": m["steps_recorded"],
                     "final_state_hash": m["final_state_hash"],
                     "keys": sorted(list(z.keys())),
                     "seed_is_frozen": m["seed"] in frozen,
                     "split_matches_freeze": frozen.get(m["seed"], (None, None, None))[2]
                     == m["split"]})
        sums.append("%s  %s" % (d, os.path.basename(p)))
    ran = {r["seed"] for r in rows}
    man = {"SECTION": "PQEC01 raw manifest", "N_ARCHIVES": len(rows),
           "TOTAL_BYTES": sum(r["bytes"] for r in rows),
           "ALL_SEEDS_FROZEN": all(r["seed_is_frozen"] for r in rows),
           "ALL_SPLITS_MATCH_FREEZE": all(r["split_matches_freeze"] for r in rows),
           "FROZEN_SEEDS": len(frozen), "SEEDS_PRESENT": len(ran),
           "COMPLETE": set(frozen) == ran,
           "MISSING_SEEDS": sorted(set(frozen) - ran),
           "EXTRA_SEEDS": sorted(ran - set(frozen)),
           "SCHEMA_KEYS_IDENTICAL": len({tuple(r["keys"]) for r in rows}) == 1,
           "ARCHIVES": rows}
    json.dump(man, open(f"{OUT}/PQEC01_RAW_MANIFEST.json", "w"), indent=1, default=str)
    open(f"{OUT}/PQEC01_RAW_SHA256SUMS", "w").write("\n".join(sums) + "\n")
    print("archives %d, bytes %.1f MB, complete %s, all seeds frozen %s, splits match %s, "
          "schema identical %s" % (man["N_ARCHIVES"], man["TOTAL_BYTES"] / 1e6, man["COMPLETE"],
                                   man["ALL_SEEDS_FROZEN"], man["ALL_SPLITS_MATCH_FREEZE"],
                                   man["SCHEMA_KEYS_IDENTICAL"]))
    return 0 if man["COMPLETE"] else 1


if __name__ == "__main__":
    sys.exit(main())

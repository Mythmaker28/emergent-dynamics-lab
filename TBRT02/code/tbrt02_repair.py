"""TBRT02 — post-rollback ledger repair. Run at every restore, BEFORE relaunching the workers.

THE PROBLEM THIS EXISTS FOR. This container reverts to the same snapshot roughly every ninety
minutes; eleven times so far. The sealed ledger is externalised to Windows and comes back intact,
but the raw archives are not — three .npz files per admissible triple, thirteen megabytes each time,
too much to push through the device bridge on every seed. So after a rollback the ledger can claim a
triple whose archives no longer exist. Left alone the campaign would silently accumulate entries
pointing at nothing, and the analysis would fail at the end with no way to recover the worlds.

THE REPAIR, and why it is legitimate rather than a rewrite of a sealed record. An entry whose
archives are gone is DROPPED so its seed runs again. Admissibility depends only on the seed and the
frozen law, and the engine is bit-deterministic — OMLDCT02 proved this after its own eighth
rollback by re-running 118 seeds and reproducing identical indices and totals. So the re-run
reproduces the same record; nothing is selected, nothing is discarded on its outcome, and the
decision to drop is made on FILE EXISTENCE alone, never on what the entry says.

Every drop is recorded with its reason in TBRT02_LEDGER_REPAIRS.jsonl, which is append-only. The
repair never touches a frozen method file, so METHODS_HASH is unaffected, and it never drops an
entry whose archives are present.
"""
from __future__ import annotations
import datetime as dt, glob, json, os, sys

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
WORK = f"{REPO}/TBRT02/work"
JOURNAL = f"{WORK}/TBRT02_LEDGER_REPAIRS.jsonl"


def main(apply=True):
    dropped, kept, checked = [], 0, 0
    for path in sorted(glob.glob(f"{WORK}/TBRT02_SEALED_LEDGER_*.jsonl")):
        rows = [json.loads(l) for l in open(path) if l.strip()]
        keep = []
        for r in rows:
            checked += 1
            if not r.get("ADMISSIBLE"):
                keep.append(r)
                continue
            miss = [a["path"] for a in r["ARCHIVES"].values() if not os.path.exists(a["path"])]
            if miss:
                dropped.append({"index": r["index"], "seed": r["seed"],
                                "shard_file": os.path.basename(path),
                                "missing_archives": miss,
                                "n_missing": len(miss), "of": len(r["ARCHIVES"])})
            else:
                keep.append(r)
                kept += 1
        if apply and len(keep) != len(rows):
            tmp = path + ".repair"
            with open(tmp, "w") as fh:
                for r in keep:
                    fh.write(json.dumps(r, sort_keys=True) + "\n")
                fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp, path)
    if dropped and apply:
        with open(JOURNAL, "a") as fh:
            fh.write(json.dumps({
                "REPAIRED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
                "REASON": "container rollback destroyed the raw archives of these admissible "
                          "triples while the sealed ledger survived on Windows",
                "DECISION_RULE": "drop on FILE EXISTENCE alone, never on what the entry says. The "
                                 "seed runs again and reproduces the same record, because "
                                 "admissibility depends only on the seed and the frozen law and the "
                                 "engine is bit-deterministic.",
                "NOT_AN_OUTCOME_DRIVEN_REPLACEMENT": True,
                "n_dropped": len(dropped), "dropped": dropped}, sort_keys=True) + "\n")
            fh.flush(); os.fsync(fh.fileno())
    return {"entries_checked": checked, "admissible_kept": kept,
            "admissible_dropped_for_missing_archives": len(dropped),
            "dropped": dropped, "applied": apply and bool(dropped)}


if __name__ == "__main__":
    r = main(apply="--dry-run" not in sys.argv)
    print(json.dumps(r, indent=1)[:1500])

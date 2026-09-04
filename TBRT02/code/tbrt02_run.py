"""TBRT02 — the frozen batch runner. Resumable by construction, and shard-parallel.

This container has been rolled back NINE times during this programme, the last one taking an entire
mission. So the ledger is appended one line per seed and fsync'd before the next seed starts, the
run state is written atomically, and a restart reads the ledger and skips what is done.

THE STOPPING RULE IS ON TRIPLES, NOT ON COST. OMLDCT02 froze a 41-pair target and a 512-instance
ceiling independently, checked them against a yield rate that turned out to be twice the truth, and
stopped on the ceiling at 33 pairs with no conclusion available. Here the ceiling is sized on the
PROSPECTIVE ledger with the rate's own uncertainty propagated. If it ever binds that is recorded as
a FAILURE OF THE DESIGN, not as a result.

Two workers take disjoint index residues and each appends to its OWN shard, so no two processes ever
write one file. The shards are read together everywhere; sharding is a throughput decision and
touches no rule.
"""
from __future__ import annotations
import json, os, sys, time
import datetime as dt

REPO = os.environ.get("TBRT02_REPO", "/home/claude/edl")
for p in ("TBRT02/code", "OMLDCT02/code"):
    sys.path.insert(0, os.path.join(REPO, p))
import omldct02_hashes as H          # noqa: E402
import tbrt02_guard as G             # noqa: E402

TARGET_VALID_TRIPLES = 41
MAX_ARM_INSTANCES = 926.0
CEILING_IS_NOT_A_STOPPING_RULE = ("the campaign stops on TARGET_VALID_TRIPLES. The ceiling is a "
                                  "cost bound. If it binds, that is a failure of the design and is "
                                  "recorded as one.")
RAWDIR = os.environ.get("TBRT02_RAW", "/home/claude/TBRT02_raw")
STATE = f"{REPO}/TBRT02/work/TBRT02_RUN_STATE.json"
N_SHARDS = int(os.environ.get("TBRT02_SHARDS", "2"))


def _shard_paths():
    return [f"{REPO}/TBRT02/work/TBRT02_SEALED_LEDGER_{i}.jsonl" for i in range(N_SHARDS)]


def _load():
    done, valid, cost = {}, 0, 0.0
    for p in _shard_paths():
        if not os.path.exists(p):
            continue
        for line in open(p):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["index"] in done:
                continue
            done[r["index"]] = r
            cost += r["instance_cost"]
            if r.get("ADMISSIBLE"):
                valid += 1
    return done, valid, round(cost, 5)


def _append(rec, shard):
    with open(_shard_paths()[shard], "a") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _state(d, shard):
    tmp = f"{STATE}.{shard}.part"
    with open(tmp, "w") as fh:
        json.dump(d, fh, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, f"{STATE}.{shard}")


def status():
    done, valid, cost = _load()
    return {"seeds_done": len(done), "valid_triples": valid, "arm_instances_spent": cost,
            "TARGET_VALID_TRIPLES": TARGET_VALID_TRIPLES, "MAX_ARM_INSTANCES": MAX_ARM_INSTANCES,
            "instances_remaining": round(MAX_ARM_INSTANCES - cost, 5),
            "fraction_of_target": round(valid / TARGET_VALID_TRIPLES, 4)}


def run_batch(n_seeds, shard=0):
    import tbrt02_fork as F
    man = json.load(open(f"{REPO}/TBRT02/out/TBRT02_SEED_MANIFEST.json"))
    done, valid, cost = _load()
    os.makedirs(RAWDIR, exist_ok=True)
    os.makedirs(f"{REPO}/TBRT02/work", exist_ok=True)
    t0 = time.time()
    ran = 0
    stop = None
    for s in man["BASE_SEEDS"]:
        if ran >= n_seeds:
            stop = "BATCH_SIZE_REACHED"; break
        if s["index"] % N_SHARDS != shard or s["index"] in done:
            continue
        if valid >= TARGET_VALID_TRIPLES:
            stop = "TARGET_REACHED"; break
        if cost >= MAX_ARM_INSTANCES:
            stop = "HARD_ARM_INSTANCE_CEILING"; break
        rec, arch = F.one_seed(s["index"], s["seed"], RAWDIR)
        _append(rec, shard)
        ran += 1
        done, valid, cost = _load()
        _state({"GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
                "MISSION": "TBRT02", **status(), "shard": shard,
                "CEILING_IS_NOT_A_STOPPING_RULE": CEILING_IS_NOT_A_STOPPING_RULE,
                "last_index": s["index"], "batch_seconds": round(time.time() - t0, 1)}, shard)
        print(f"  i{s['index']:04d} s{s['seed']}  "
              f"{'ADMISSIBLE' if rec.get('ADMISSIBLE') else rec.get('REASON','')[:28]:30s} "
              f"cost {cost:8.3f}  valid {valid}/{TARGET_VALID_TRIPLES}  {rec['runtime_s']:5.1f}s",
              flush=True)
    if stop is None:
        stop = "SEED_LIST_EXHAUSTED"
    st = {"GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(), "MISSION": "TBRT02",
          **status(), "STOPPED": stop, "shard": shard,
          "CEILING_IS_NOT_A_STOPPING_RULE": CEILING_IS_NOT_A_STOPPING_RULE,
          "CEILING_BOUND_THE_CAMPAIGN": stop == "HARD_ARM_INSTANCE_CEILING",
          "batch_seconds": round(time.time() - t0, 1), "batch_seeds": ran}
    _state(st, shard)
    return st


if __name__ == "__main__":
    if sys.argv[1] == "status":
        print(json.dumps(status(), indent=1))
    else:
        print(json.dumps(run_batch(int(sys.argv[1]),
                                   int(sys.argv[2]) if len(sys.argv) > 2 else 0), indent=1))

"""PQEC01 — frozen scientific execution. Phase A and Phase B.

OUTCOME FIREWALL. A worker returns to the parent process ONLY technical metadata: return code,
path, byte size, sha256, schema flag and engine-invariant flags. Scientific outcomes go into the
per-world archive and are not read by anything until every scheduled start is complete.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import traceback

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pqec01_observer as O                                                   # noqa: E402

RAW = "/home/claude/PQEC01/raw"
OUT = "/home/claude/edl/PQEC01/out"
FREEZE = json.load(open(f"{OUT}/PQEC01_MASTER_FREEZE.json"))
C = FREEZE["INHERITED_FROZEN_CONSTANTS"]
T_HORIZON, BURN_IN, CAP, CORE_R = C["T_HORIZON"], C["BURN_IN"], C["CAP"], C["CORE_R"]
N_STAR = int(C["N_STAR"])
SCALARS = ["step", "N_Y", "N_X", "n_y_cells", "n_centres", "max_pair_dist", "Q_founder",
           "nSY_founder", "free_founder", "nX_founder", "candY_founder", "sum_Q_position",
           "mean_nSY", "mean_free", "n_SY_total", "n_SX_total"]


def _centres(cells):
    """Single-linkage clusters of occupied Y cells at toroidal distance <= CORE_R."""
    n = len(cells)
    if n == 0:
        return 0, 0.0
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    mx = 0.0
    L = 36
    for i in range(n):
        for j in range(i + 1, n):
            dy = abs(cells[i][0] - cells[j][0])
            dx = abs(cells[i][1] - cells[j][1])
            dy, dx = min(dy, L - dy), min(dx, L - dx)
            d = (dy * dy + dx * dx) ** 0.5
            mx = max(mx, d)
            if d <= CORE_R:
                a, b = find(i), find(j)
                if a != b:
                    par[a] = b
    return len({find(i) for i in range(n)}), mx


def run_world(job):
    phase, point, idx, seed, kY, muY, split = job
    tag = "%s_%s_i%03d_s%d" % (phase, point, idx, seed)
    path = os.path.join(RAW, tag + ".npz")
    t0 = time.time()
    rec = {"tag": tag, "phase": phase, "point": point, "index": idx, "seed": seed,
           "split": split, "kY": kY, "muY": muY, "path": path}
    try:
        w, _, sp = O.build_world(seed, kY, muY, L=None, horizon=T_HORIZON, instrumented=True)
        scal = np.zeros((T_HORIZON, len(SCALARS)), np.float64)
        stop, stop_step = "HORIZON", T_HORIZON
        invariant_ok = True
        for t in range(T_HORIZON):
            w._one_step()
            nY, nX = w.n["Y"], w.n["X"]
            free = sp.CAP - sum(w.n[s] for s in O.SPECIES)
            if free.min() < 0 or max(w.n[s].max() for s in O.SPECIES) > sp.CAP:
                invariant_ok = False
                stop, stop_step = "INTEGRITY_FAILURE", t
                break
            ys, xs = np.nonzero(nY)
            cells = list(zip(ys.tolist(), xs.tolist()))
            ncen, mxd = _centres(cells)
            NY = int(nY.sum())
            if cells:
                fy, fx = cells[0]
                cf = int(min(w.n["SY"][fy, fx], max(free[fy, fx], 0)))
                qf, sf, ff, xf = int(nX[fy, fx]) * cf, int(w.n["SY"][fy, fx]), \
                    int(free[fy, fx]), int(nX[fy, fx])
            else:
                cf = qf = sf = ff = xf = 0
            candY = np.minimum(w.n["SY"], np.maximum(free, 0))
            scal[t] = [t, NY, int(nX.sum()), len(cells), ncen, mxd, qf, sf, ff, xf, cf,
                       float((nX * candY).sum()), float(w.n["SY"].mean()),
                       float(np.maximum(free, 0).mean()), float(w.n["SY"].sum()),
                       float(w.n["SX"].sum())]
            if NY == 0:
                stop, stop_step = "EXTINCT", t
                break
            if ncen >= 3:
                stop, stop_step = "PREMATURE_THIRD_CENTRE", t
                break
            if NY > N_STAR:
                stop, stop_step = "MAX_PERMITTED_Y", t
                break
        n_rec = min(stop_step + 1, T_HORIZON)
        F = w.pq_field[:n_rec]
        d = np.diff(F.astype(np.int16), axis=0).astype(np.int8)
        np.savez_compressed(
            path, field0=F[0], field_delta=d, scalars=scal[:n_rec].astype(np.float64),
            scalar_names=np.array(SCALARS),
            ycells=np.array(w.pq_ycells, np.int32) if w.pq_ycells else np.zeros((0, 9), np.int32),
            ybirth=np.array(w.pq_ybirth, np.int32) if w.pq_ybirth else np.zeros((0, 4), np.int32),
            ydeath=np.array(w.pq_ydeath, np.int32) if w.pq_ydeath else np.zeros((0, 4), np.int32),
            yhop=np.array(w.pq_yhop, np.int32) if w.pq_yhop else np.zeros((0, 7), np.int32),
            xevent=np.array(w.pq_xevent, np.int32) if w.pq_xevent else np.zeros((0, 3), np.int32),
            capacity=np.array(w.pq_capacity, np.int64),
            exchange=np.array(w.pq_exchange, np.int64),
            src=np.array(w.pq_src, np.int32),
            final=np.stack([w.n[s] for s in O.SPECIES]).astype(np.int32),
            meta=np.array([json.dumps({"tag": tag, "seed": seed, "phase": phase, "point": point,
                                       "index": idx, "split": split, "kY": kY, "muY": muY,
                                       "CAP": int(sp.CAP), "L": int(w.L),
                                       "steps_recorded": int(n_rec), "stop": stop,
                                       "stop_step": int(stop_step),
                                       "final_state_hash": w.state_hash()})]))
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 20), b""):
                h.update(b)
        z = np.load(path, allow_pickle=True)
        schema_ok = all(k in z for k in ("field0", "field_delta", "scalars", "ycells", "ybirth",
                                         "ydeath", "yhop", "capacity", "exchange", "src",
                                         "final", "meta"))
        rec.update({"returncode": 0, "exists": True, "bytes": os.path.getsize(path),
                    "sha256": h.hexdigest(), "schema_ok": bool(schema_ok),
                    "engine_invariants_ok": bool(invariant_ok),
                    "steps_recorded": int(n_rec),
                    "TECHNICALLY_VALID": bool(schema_ok and invariant_ok),
                    "seconds": round(time.time() - t0, 2)})
    except Exception:
        rec.update({"returncode": 1, "exists": os.path.exists(path), "bytes": 0, "sha256": None,
                    "schema_ok": False, "engine_invariants_ok": False,
                    "TECHNICALLY_VALID": False, "error": traceback.format_exc()[-800:],
                    "seconds": round(time.time() - t0, 2)})
    return rec


def jobs_for(phase):
    S = FREEZE["SEED_RULE"]["SEEDS"]
    out = []
    if phase == "A":
        for r in S["A"]:
            out.append(("A", "A0", r["index"], r["seed"], FREEZE["PHASE_A"]["kY"],
                        FREEZE["PHASE_A"]["muY"], r["split"]))
    else:
        for lab in ("B1", "B2"):
            pt = FREEZE["PHASE_B"]["POINT_" + lab]
            for r in S[lab]:
                out.append(("B", lab, r["index"], r["seed"], pt["kY"], pt["muY"], r["split"]))
    return out


def main():
    phase = sys.argv[1]
    os.makedirs(RAW, exist_ok=True)
    js = jobs_for(phase)
    led = os.path.join(OUT, "PQEC01_RUN_LEDGER.jsonl")
    import multiprocessing as mp
    done = 0
    with mp.Pool(2) as pool, open(led, "a") as fh:
        for rec in pool.imap_unordered(run_world, js):
            fh.write(json.dumps(rec, default=str) + "\n")
            fh.flush()
            done += 1
            # FIREWALL: only technical metadata is printed
            print("  [%3d/%3d] %s rc=%d bytes=%d schema=%s invariants=%s"
                  % (done, len(js), rec["tag"], rec["returncode"], rec.get("bytes", 0),
                     rec.get("schema_ok"), rec.get("engine_invariants_ok")), flush=True)
    print("phase %s: %d starts written" % (phase, len(js)))


if __name__ == "__main__":
    main()

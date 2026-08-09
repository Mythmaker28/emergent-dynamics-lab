"""ETPC runner: four-arm exact-twin design from one complete checkpoint per founding block."""
from __future__ import annotations
import sys, os, json, pickle, time, tempfile
sys.path.insert(0, "/home/claude/sweep"); sys.path.insert(0, "/home/claude/sweep/DOMC")
sys.path.insert(0, "/home/claude/sweep/PPAI")
import numpy as np
import domc_core as K, ppai_core as P, etpc_core as E

SEEDS = {"PRIMARY": tuple(range(61000, 61010)), "HELDOUT": tuple(range(62000, 62010))}
GEOM = {"PRIMARY": "FAR", "HELDOUT": "NEAR"}
STARTS = {"n": 0}
TMP = tempfile.mkdtemp(prefix="etpc_run_")

def block(seed, geom):
    K.set_geometry(geom); sup = P.halo_sup()
    STARTS["n"] += 1
    eng = E.engine(E.GAIN_ON)
    f = K.advance(eng, K.found(seed), K.T_FOUND)
    hA, hB = (P.HIST_H, P.HIST_L) if seed % 2 == 0 else (P.HIST_L, P.HIST_H)
    st0 = K.advance(eng, K.apply_dual_history(eng, f, hA, hB), K.SETTLE)
    cp = os.path.join(TMP, f"cp_{geom}_{seed}.npz")
    lh = E.save(st0, cp, E.runtime_manifest())
    mem, ncomp = E.members(st0)
    out = {"seed": seed, "geometry": geom, "orientation": "HL" if seed % 2 == 0 else "LH",
           "checkpoint_logical_hash": lh, "n_components": ncomp,
           "lineage_valid": mem["A"] is not None and mem["B"] is not None, "arms": {}}
    if not out["lineage_valid"]:
        out["ITT_note"] = "lineage invalid at the checkpoint; block retained in ITT with missing Y"
        return out
    op = E.build_operator(st0)
    out["operator"] = op
    out["ledger_before"] = E.invariant_ledger(st0, mem)
    for arm, (gain, do_swap) in E.ARMS.items():
        STARTS["n"] += 1
        s = E.apply_operator(E.load(cp), mem, op, identity=not do_swap)   # fork by reload
        if arm == "ON_SWAP":
            out["ledger_after"] = E.invariant_ledger(s, mem)
            out["touchset"] = E.touchset(st0, s)
        e = E.engine(gain)
        zt0 = E.z_summary(s, mem)
        series, cur = [], s.copy()
        for t in range(0, E.T_RESP + 1):
            if t <= E.T_EARLY or t in (100, 150, E.T_MED):
                series.append({"t": t,
                               "c": {k: float(cur.c[sup[k]].mean()) for k in ("A", "B")},
                               "N": {k: float(cur.N[sup[k]].mean()) for k in ("A", "B")}})
            if t == E.T_RESP: break
            cur = e.step(cur)
        R = P.challenge(e, cur)
        out["arms"][arm] = {"gain": gain, "swap": do_swap, "z_t0": zt0, "series": series,
                            "public_hash_t0": E.public_hash(s),
                            "public_hash_end": E.public_hash(cur),
                            "Y": {k: float(np.asarray(R[k]).mean()) for k in ("A", "B")},
                            "R": {k: np.asarray(R[k]).tolist() for k in ("A", "B")},
                            "geom_end": {k: (P.public_vector(cur, sup)[k]) for k in ("A", "B")}}
    return out

def main(split):
    p = f"etpc_{split}.pkl"
    done = pickle.load(open(p, "rb")) if os.path.exists(p) else []
    seen = {d["seed"] for d in done}; t0 = time.time()
    for s in SEEDS[split]:
        if s in seen: continue
        r = block(s, GEOM[split]); done.append(r); pickle.dump(done, open(p, "wb"))
        print(f"{split} {s}: lineage={r['lineage_valid']} ncomp={r['n_components']} "
              f"[{time.time()-t0:.0f}s]", flush=True)
    print(f"COMPLETE {split}: {len(done)} blocks, {STARTS['n']} engine starts", flush=True)
    json.dump({"engine_starts": STARTS["n"]}, open(f"etpc_{split}_starts.json", "w"))

if __name__ == "__main__":
    main(sys.argv[1])

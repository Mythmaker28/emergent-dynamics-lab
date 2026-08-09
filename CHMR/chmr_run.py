"""CHMR runner — the conservative core/halo mismatch experiment.

Usage: python3 chmr_run.py <GEOM> <SPLIT>
  GEOM  in {FAR, NEAR}      (the DOMC primary geometry and its already designated held-out one)
  SPLIT in {DEV, CONF, HELD}
"""
from __future__ import annotations
import sys, os, pickle, time
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
import numpy as np
import domc_core as K
import chmr_core as X
import chmr_lineage as LG

SEEDS = {"DEV": tuple(range(36000, 36008)),      # 8 development blocks (also used in Phase D)
         "CONF": tuple(range(37000, 37012)),     # 12 confirmatory blocks, never evolved before
         "HELD": tuple(range(38000, 38012))}     # 12 held-out-geometry blocks
T_RECOVERY = 350                                 # frozen on DEV, Phase D
T_PULSE = 350                                    # the mismatched halo is present for this long


def evolve_track(eng, st, steps, obs, sup, frames, edges, tag, restore_at=None, mid=None):
    rec = []
    cur = st.copy()
    stMid = None
    for t in range(0, steps + 1):
        if mid is not None and t == mid:
            stMid = cur.copy()
        if t in obs:
            rec.append({"tag": tag, "t": t, "halo": X.halo_vector(cur, sup),
                        "core": X.core_vector(cur), "geom": X.geometry_vector(cur)})
        if t == steps:
            break
        if restore_at is not None and t == restore_at:
            cur = X.halo_cross(cur)               # the involution restores the fields
            rec.append({"tag": tag + "_RESTORED", "t": t, "halo": X.halo_vector(cur, sup),
                        "core": X.core_vector(cur), "geom": X.geometry_vector(cur)})
        cur = eng.step(cur)
        if (t + 1) % X.CAD_LINEAGE == 0:
            f = LG.snapshot(cur)
            edges.append(LG.link(frames[-1], f))
            frames.append(f)
    return rec, cur, (stMid if stMid is not None else cur)


def block(seed, geom):
    K.set_geometry(geom)
    sup = X.halo_supports()
    eng = X.engine()
    out = {"seed": seed, "geometry": geom, "T_RECOVERY": T_RECOVERY, "arms": {}}

    # ---- prefix: founding, the two localized histories, the settle -----------------------
    f0 = K.advance(eng, K.found(seed), K.T_FOUND)
    s1 = K.apply_dual_history(eng, f0, X.HIST_H, X.HIST_L)
    st0 = K.advance(eng, s1, K.SETTLE)
    out["prefix"] = {"halo": X.halo_vector(st0, sup), "core": X.core_vector(st0),
                     "geom": X.geometry_vector(st0),
                     "realized_global_c": float(st0.c.sum()),
                     "realized_global_N": float(st0.N.sum()),
                     "realized_global_mass": float(st0.rho.sum())}

    for arm in X.ARMS:
        e = X.engine(writer_off=(arm in X.WRITER_OFF_ARMS))
        sv = X.INTERVENTIONS[arm](st0)
        led = X.ledger(st0, sv, arm)
        frames, edges = [LG.snapshot(sv)], []
        # EVERY arm runs the same total duration, so the pulse arm has a same-time reference in
        # every other arm. The primary endpoint is read at T_RECOVERY; the pulse endpoint at the
        # end. Only the pulse arm has the halo restored, at t = T_PULSE.
        steps = T_RECOVERY + T_PULSE
        obs = set(X.OBS_TIMES) | {T_RECOVERY, steps, 500}
        rec, stT, stMid = evolve_track(e, sv, steps, obs, sup, frames, edges, arm,
                                       restore_at=(T_PULSE if arm in X.PULSE_ARMS else None),
                                       mid=T_RECOVERY)
        rep = LG.analyse_track(frames, edges)
        R = X.challenge(e, stMid)          # the future response AT T_RECOVERY (primary)
        R2 = X.challenge(e, stT)           # and at the end (pulse endpoint)
        d = {"ledger": led, "series": rec,
             "lineage": {"n_components": rep["n_components"], "n_splits": rep["n_splits"],
                         "n_fusions": rep["n_fusions"],
                         "n_disappearances": len(rep["disappearances"]),
                         "n_argmax_switches": rep["n_argmax_switches"]},
             "final": {"halo": X.halo_vector(stT, sup), "core": X.core_vector(stT),
                       "geom": X.geometry_vector(stT),
                       "realized_global_c": float(stT.c.sum()),
                       "realized_global_N": float(stT.N.sum()),
                       "realized_global_mass": float(stT.rho.sum())},
             "response": {"A": R["A"].tolist(), "B": R["B"].tolist(),
                          "ctrl_A": R["ctrl_A"].tolist(), "ctrl_B": R["ctrl_B"].tolist()},
             "response_end": {"A": R2["A"].tolist(), "B": R2["B"].tolist()}}

        # ---- lineage-resolved turnover, on the frozen criterion, selected arms ----------
        if arm in X.TURNOVER_ARMS:
            pc = X.engine(writer_off=(arm in X.WRITER_OFF_ARMS), pulse_chase=True)
            stt = K.relabel(stMid)
            fr2, ed2 = [LG.snapshot(stt)], []
            cur = stt
            for t in range(X.T_TURN):
                cur = pc.step(cur)
                if (t + 1) % X.CAD_LINEAGE == 0:
                    ff = LG.snapshot(cur)
                    ed2.append(LG.link(fr2[-1], ff))
                    fr2.append(ff)
            rep2 = LG.analyse_track(fr2, ed2)
            lin = {}
            k0 = next((k for k, ff in enumerate(fr2) if len(ff) >= 2), None)
            if k0 is not None:
                for idx in (0, 1):
                    l = LG.founder_lineage(fr2, ed2, k0, idx)
                    s = LG.summarise(fr2, l)
                    lin[idx] = {"continuous_to_end": bool(l.get(len(fr2) - 1)),
                                "max_components": max((len(l[k]) for k in l), default=0),
                                "M_final": s[-1]["M"], "size_final": s[-1]["size"]}
            RT = X.challenge(pc, cur)
            d["turnover"] = {"M_by_lineage": lin,
                             "lineage": {"n_splits": rep2["n_splits"],
                                         "n_fusions": rep2["n_fusions"],
                                         "n_components": rep2["n_components"]},
                             "halo": X.halo_vector(cur, sup), "core": X.core_vector(cur),
                             "geom": X.geometry_vector(cur),
                             "M_site": K.turnover_M(cur),
                             "response": {"A": RT["A"].tolist(), "B": RT["B"].tolist()}}
        out["arms"][arm] = d
    return out


def main(geom, split):
    p = f"chmr_{geom}_{split}.pkl"
    done = pickle.load(open(p, "rb")) if os.path.exists(p) else []
    seen = {d["seed"] for d in done}
    t0 = time.time()
    for s in SEEDS[split]:
        if s in seen:
            continue
        r = block(s, geom)
        done.append(r)
        pickle.dump(done, open(p, "wb"))
        sp = sum(v["lineage"]["n_splits"] for v in r["arms"].values())
        fu = sum(v["lineage"]["n_fusions"] for v in r["arms"].values())
        print(f"{geom}/{split} block {s}: splits={sp} fusions={fu} "
              f"[{time.time()-t0:.0f}s]", flush=True)
    print(f"COMPLETE {geom}/{split}: {len(done)} blocks, {len(done)*len(X.ARMS)} trajectories, "
          f"{time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

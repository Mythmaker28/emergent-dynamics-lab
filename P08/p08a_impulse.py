"""08A -- can rho be predicted INDEPENDENTLY of the delivery curve it is supposed to predict?

P07 estimated rho by averaging delivered mass over a window, then "predicted" delivered mass
over the same window. That is circular for the plateau points. Here rho is measured by a
LOCAL PHYSICAL PROBE that never looks at any delivery curve:

  at a checkpoint time t of an ordinary forced (PARENT) trajectory, fork a clone, SATURATE the
  injection region in one shot (fill every source cell in the track to MMAX), then let the
  substrate run free with NO operator at all and measure how fast free room reopens:

        H(u) = sum over the frozen source mask of (MMAX - m)   at u steps after saturation

  The sustained throughput of a coupled operator that keeps the region saturated is, by
  construction, the reopening rate AT ZERO HEADROOM, i.e. the initial slope dH/du at u -> 0+.

The prediction rho_probe(t) = dH/du|_{0+} is then compared with the delivery rate actually
observed around t in the same trajectory. Neither quantity is fitted to the other.
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../P07")
from od_core import LatticeBondEngine, LatticeBondState, largest_bounded, cells_of, MMAX
from bridge00_harness import law_arms
import p07_core as P7
import p08_core as P8

T_B = 256
CHECKPOINTS = (272, 1296, 2320, 3344, 4368)
PROBE_STEPS = 64
SLOPE_WINDOW = 8            # steps used for the initial slope, frozen in advance
FORCED_END = 5376
SPACING, N_EVENTS = 16, 320
SIZES, SEEDS_PER, SEED_BASE = (24, 32), 9, 990000
AXORD = ("+x", "-x", "+y", "-y")
P7DIR = Path("../P07")


def headroom(state, mask, track):
    fm = state.m.reshape(-1)
    return math.fsum(MMAX - fm[i] for i in mask if i in track and fm[i] < MMAX)


def saturate(state, prov, mask, track):
    """One-shot fill of the injection region to MMAX. All injected matter is FRESH."""
    fm = state.m.reshape(-1)
    ff = prov.f["fre"].reshape(-1)
    added = 0.0
    for i in mask:
        if i not in track:
            continue
        room = MMAX - fm[i]
        if room > 1e-12:
            fm[i] += room
            ff[i] += room
            added += room
    prov.res_source += added
    return added


def clone_prov(pv, st0, cells, L):
    q = P7.Prov(st0, cells, L)
    for k in P7.COHORTS:
        q.f[k] = pv.f[k].copy()
    q.res_sink, q.res_source = pv.res_sink, pv.res_source
    q.sink_by_cohort = dict(pv.sink_by_cohort)
    return q


def main():
    law = law_arms()["LAW_16"]
    man = {b["block"]: b for b in json.loads((P7DIR / "p07a_manifest.json").read_text())["blocks"]}
    probes, curves = [], []
    calls = 0
    t0 = time.time()
    sched = {272 + SPACING * (e - 1) for e in range(1, N_EVENTS + 1)}
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            blk = f"L{L}_S{seed}"
            info = man.get(blk)
            if info is None or info.get("t256_status") != "T256_VALID_TRACK":
                continue
            a = np.load(P7DIR / f"_t256_{blk}.npy")
            b = np.load(P7DIR / f"_t256b_{blk}.npy")
            st = LatticeBondState(np.ascontiguousarray(a[0]), np.ascontiguousarray(a[1]),
                                  np.ascontiguousarray(b), T_B)
            c = largest_bounded(st)
            cells = cells_of(c)
            masks = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            prov = P7.Prov(st, cells, L)
            M256 = prov.M256
            qe = M256 / 80.0
            eng = LatticeBondEngine(law)
            calls += 1
            delivered_at = {}
            cum = 0.0
            t = int(st.step)
            while t < FORCED_END + 1:
                if t in sched:
                    cc = largest_bounded(st)
                    if cc is not None:
                        r = P8.exchange_event(st, prov, masks, cells_of(cc), L, qe, 0.0, MMAX)
                        cum += r["realized_sink"]
                if t in CHECKPOINTS:
                    delivered_at[t] = cum
                    cc = largest_bounded(st)
                    if cc is not None:
                        # --- the probe: a clone, saturated once, then left alone -----
                        cl = st.copy()
                        pv = clone_prov(prov, st, cells, L)
                        tr = cells_of(cc)
                        added = saturate(cl, pv, masks["source"], tr)
                        e2 = LatticeBondEngine(law)
                        calls += 1
                        H = []
                        for u in range(PROBE_STEPS + 1):
                            cur = largest_bounded(cl)
                            trk = cells_of(cur) if cur is not None else set()
                            H.append(headroom(cl, masks["source"], trk))
                            curves.append({"block": blk, "size": L, "checkpoint": t, "u": u,
                                           "headroom": H[-1], "M256": M256, "quantum": qe})
                            if u < PROBE_STEPS:
                                pre = cl
                                o = e2.step(pre)
                                pv.advance(pre.m, o.ledger, o.state.m, law.dt)
                                cl = o.state
                        slope = (H[SLOPE_WINDOW] - H[0]) / SLOPE_WINDOW
                        slope64 = (H[PROBE_STEPS] - H[0]) / PROBE_STEPS
                        probes.append({"block": blk, "size": L, "checkpoint": t,
                                       "saturation_mass_added": added, "M256": M256,
                                       "quantum": qe,
                                       "rho_probe_slope8": slope, "rho_probe_slope64": slope64,
                                       "H0": H[0], "H8": H[SLOPE_WINDOW],
                                       "H64": H[PROBE_STEPS]})
                if t >= FORCED_END:
                    break
                pre = st
                o = eng.step(pre)
                prov.advance(pre.m, o.ledger, o.state.m, law.dt)
                st = o.state
                t = int(st.step)
            for i, tt in enumerate(CHECKPOINTS):
                if tt in delivered_at and i + 1 < len(CHECKPOINTS) \
                        and CHECKPOINTS[i + 1] in delivered_at:
                    nxt = CHECKPOINTS[i + 1]
                    for p in probes:
                        if p["block"] == blk and p["checkpoint"] == tt:
                            p["rho_observed_next_window"] = \
                                (delivered_at[nxt] - delivered_at[tt]) / (nxt - tt)
                            p["window"] = f"{tt}-{nxt}"
            print(f"  {blk} ({time.time()-t0:.0f}s)", flush=True)
    for name, data in (("p08a_probe.csv", probes), ("p08a_probe_curves.csv", curves)):
        f = sorted({kk for d in data for kk in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p08a_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n08A probe: {len(probes)} sondes, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

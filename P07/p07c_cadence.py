"""07A-C -- throughput versus cadence, DISCOVERY phase (same blocks as 07A/07B).

Motivated by the 07A finding that from event ~13 onward the coupled event is bounded by the
SOURCE (free room MMAX - m in the injection region), not by the sink. If that is right, the
delivered throughput per unit time must saturate at rho, the rate at which the substrate
reopens free capacity in the injection region, and must be independent of the cadence once
the spacing exceeds s* = quantum / rho:

        Phi(s) = min(quantum / s, rho)          [mass per step]

Spacings 1, 4, 16, 64 are measured here and used to ESTIMATE rho.
Spacings 2, 8, 32, 128 are DELIBERATELY held out: they are the prospective test in 07D, on
fresh seeds, against a point prediction sealed before that run.
"""
from __future__ import annotations
import csv, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
from od_core import LatticeBondEngine, LatticeBondState, largest_bounded, cells_of
from bridge00_harness import law_arms
import p07_core as P

T_B, T0 = 256, 272
WINDOW = 2048
SPACINGS = (1, 4, 16, 64)
PLACEMENTS = ("INTERFACE", "DISPERSED")
SIZES, SEEDS_PER, SEED_BASE = (24, 32), 9, 990000
AXORD = ("+x", "-x", "+y", "-y")


def main():
    law = law_arms()["LAW_16"]
    rows, ev = [], []
    calls = 0
    t0 = time.time()
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            blk = f"L{L}_S{seed}"
            if not Path(f"_t256_{blk}.npy").exists():
                continue
            a = np.load(f"_t256_{blk}.npy")
            st0 = LatticeBondState(np.ascontiguousarray(a[0]), np.ascontiguousarray(a[1]),
                                   np.ascontiguousarray(np.load(f"_t256b_{blk}.npy")), T_B)
            c = largest_bounded(st0)
            if c is None:
                continue
            cells = cells_of(c)
            masks = P.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            pv0 = P.Prov(st0, cells, L)
            qe = pv0.M256 / 80.0
            eng = LatticeBondEngine(law)
            calls += 1
            base = st0.copy()
            for _ in range(T0 - T_B):
                pre = base
                o = eng.step(pre)
                pv0.advance(pre.m, o.ledger, o.state.m, law.dt)
                base = o.state

            for pl in PLACEMENTS:
                for s in SPACINGS:
                    st = base.copy()
                    pv = P.Prov(st0, cells, L)
                    for kk in P.COHORTS:
                        pv.f[kk] = pv0.f[kk].copy()
                    e = LatticeBondEngine(law)
                    calls += 1
                    n_ev = WINDOW // s
                    delivered = planned = 0.0
                    n_rej = 0
                    causes = {}
                    bound = {"PLANNED": 0, "SOURCE": 0, "SINK": 0}
                    for j in range(n_ev):
                        cc = largest_bounded(st)
                        planned += qe
                        if cc is None:
                            n_rej += 1
                            causes["NO_TRACK"] = causes.get("NO_TRACK", 0) + 1
                        else:
                            tr = cells_of(cc)
                            r = P.exchange_event(st, pv, masks, tr, L, qe,
                                                 source_placement=pl)
                            delivered += r["realized_sink"]
                            if r["rejected"]:
                                n_rej += 1
                                causes[r["reject_reason"]] = \
                                    causes.get(r["reject_reason"], 0) + 1
                            else:
                                qq = r["q_event"]
                                if abs(qq - qe) < 1e-9:
                                    bound["PLANNED"] += 1
                                elif abs(qq - r["source_capacity"]) < 1e-9:
                                    bound["SOURCE"] += 1
                                else:
                                    bound["SINK"] += 1
                            if j % max(1, n_ev // 32) == 0:
                                reg = (len([i for i in masks["sink"] if i in tr])
                                       / len(masks["sink"]))
                                ev.append({"block": blk, "size": L, "placement": pl,
                                           "spacing": s, "event": j,
                                           "time": int(st.step), "planned": qe,
                                           "realized": r["realized_sink"],
                                           "sink_capacity": r["sink_capacity"],
                                           "source_capacity": r["source_capacity"],
                                           "mask_registration": reg,
                                           "rejected": r["rejected"]})
                        for _ in range(s):
                            pre = st
                            o = e.step(pre)
                            pv.advance(pre.m, o.ledger, o.state.m, law.dt)
                            st = o.state
                    cc = largest_bounded(st)
                    alive = cc is not None
                    rows.append({"block": blk, "size": L, "placement": pl, "spacing": s,
                                 "n_events": n_ev, "window": WINDOW, "quantum": qe,
                                 "M256": pv0.M256, "planned_total": planned,
                                 "delivered_total": delivered,
                                 "PHI_per_step": delivered / WINDOW,
                                 "PHI_over_M256_per_1000":
                                     1000.0 * delivered / (WINDOW * pv0.M256),
                                 "delivered_fraction": delivered / planned if planned else None,
                                 "n_rejected": n_rej,
                                 "reject_causes": json.dumps(causes),
                                 "bound_by": json.dumps(bound),
                                 "track_alive_at_end": alive,
                                 "identity_residual": pv.identity_residual(st)})
            print(f"  {blk} ({time.time()-t0:.0f}s)", flush=True)
    for name, data in (("p07c_cadence_rows.csv", rows), ("p07c_cadence_events.csv", ev)):
        f = sorted({k for d in data for k in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p07c_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\ncadence: {len(rows)} conditions, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

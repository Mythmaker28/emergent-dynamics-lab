"""07A readout A + B -- capacity impulse response, paired clones.

Design frozen in the sealed p07a_protocol.json ("impulse_response_design") BEFORE any 07A
result existed. This file is hashed into p07a_impulse.sha256 before it is first executed.

readout A : one probe of amplitude a*quantum at t=272, then CAP_PARENT(t) is READ at every
            step for 128 steps with zero perturbation, against a paired no-probe clone.
readout B : one probe at t=272, then a SECOND identical probe after a delay d, against a
            paired clone that received no first probe. The ratio of realized bites is the
            causal recovery fraction.

Blocks are the independent units. Internal events are never replicates.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
from od_core import (LatticeBondEngine, LatticeBondState, largest_bounded, cells_of)
from bridge00_harness import law_arms
import p07_core as P

T_B, T_PROBE = 256, 272
AMPS = (1.0, 2.0, 4.0)
DELAYS = (1, 2, 4, 8, 16, 32, 64)
READOUT_A_STEPS = 128
SIZES, SEEDS_PER, SEED_BASE = (24, 32), 9, 990000
AXORD = ("+x", "-x", "+y", "-y")
PROTOCOL, SEAL = "p07a_protocol.json", "p07a_protocol.sha256"


def guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    want = Path(SEAL).read_text().split()[0].strip()
    if got != want:
        sys.exit("PRESEAL_GUARD: protocol hash mismatch")
    d = json.loads(Path(PROTOCOL).read_text())["impulse_response_design"]
    assert "tau50" in d["estimand"], "design not the sealed one"
    return got


def cap(state, masks, L):
    c = largest_bounded(state)
    if c is None:
        return None, None
    cells = cells_of(c)
    return P.capacity_spectrum(state, masks, cells, L), cells


def clone_prov(pv, st0, cells, L):
    """Deep clone of a provenance bundle. NECESSARY: a Prov constructed from the t256 state
    is inconsistent with any later state, which is exactly the defect that crashed the first
    run of this file (`tracer must lie in [0,pre_matter]`)."""
    q = P.Prov(st0, cells, L)
    for k in P.COHORTS:
        q.f[k] = pv.f[k].copy()
    q.res_sink, q.res_source = pv.res_sink, pv.res_source
    q.sink_by_cohort = dict(pv.sink_by_cohort)
    return q


def step_n(eng, prov, st, n, law):
    for _ in range(n):
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
    return st


def probe(st, prov, masks, L, q):
    c = largest_bounded(st)
    if c is None:
        return {"rejected": True, "realized_sink": 0.0, "reject_reason": "NO_TRACK",
                "sink_capacity": 0.0}
    return P.exchange_event(st, prov, masks, cells_of(c), L, q)


def main():
    seal = guard()
    print(f"PRESEAL_GUARD OK  {seal}", flush=True)
    law = law_arms()["LAW_16"]
    A, B = [], []
    calls = 0
    t0 = time.time()
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            blk = f"L{L}_S{seed}"
            fa, fb = Path(f"_t256_{blk}.npy"), Path(f"_t256b_{blk}.npy")
            if not fa.exists():
                continue
            a = np.load(fa)
            st0 = LatticeBondState(np.ascontiguousarray(a[0]), np.ascontiguousarray(a[1]),
                                   np.ascontiguousarray(np.load(fb)), T_B)
            c = largest_bounded(st0)
            if c is None:
                continue
            cells = cells_of(c)
            masks = P.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            qe = P.Prov(st0, cells, L).M256 / 80.0

            # advance the common ancestor to the probe time
            eng = LatticeBondEngine(law)
            calls += 1
            pv = P.Prov(st0, cells, L)
            base = step_n(eng, pv, st0.copy(), T_PROBE - T_B, law)

            # ---------------- readout A -------------------------------------
            conds = {"CTRL": None}
            for am in AMPS:
                conds[f"A{am:g}"] = am
            series = {}
            for name, am in conds.items():
                stx = base.copy()
                px = clone_prov(pv, st0, cells, L)  # provenance only for the operator's books
                e = LatticeBondEngine(law)
                calls += 1
                r0 = None
                if am is not None:
                    r0 = probe(stx, px, masks, L, am * qe)
                for s in range(READOUT_A_STEPS + 1):
                    cs, _ = cap(stx, masks, L)
                    series.setdefault(name, []).append(
                        None if cs is None else
                        (cs["CAP_PARENT"], cs["CAP_TRACKALL"], cs["MASK_REGISTRATION"],
                         cs["CAP_COMOVING"]))
                    if s < READOUT_A_STEPS:
                        stx = step_n(e, px, stx, 1, law)
                if am is not None:
                    A.append({"block": blk, "size": L, "amp": am, "kind": "PROBE_META",
                              "step": -1, "quantum": qe,
                              "realized_sink": r0["realized_sink"],
                              "rejected": r0["rejected"],
                              "sink_capacity_pre": r0["sink_capacity"]})
            for name in conds:
                for s, v in enumerate(series[name]):
                    A.append({"block": blk, "size": L, "cond": name, "step": s,
                              "CAP_PARENT": None if v is None else v[0],
                              "CAP_TRACKALL": None if v is None else v[1],
                              "MASK_REGISTRATION": None if v is None else v[2],
                              "CAP_COMOVING": None if v is None else v[3],
                              "quantum": qe,
                              "amp": conds[name] if conds[name] else 0.0, "kind": "CAP"})

            # ---------------- readout B -------------------------------------
            for first in (True, False):
                stx = base.copy()
                px = clone_prov(pv, st0, cells, L)
                e = LatticeBondEngine(law)
                calls += 1
                r1 = probe(stx, px, masks, L, qe) if first else None
                done, t = 0, 0
                for d in DELAYS:
                    stx = step_n(e, px, stx, d - t, law)
                    t = d
                    fork = stx.copy()
                    pf = clone_prov(px, st0, cells, L)   # fork the operator's books too
                    r2 = probe(fork, pf, masks, L, qe)
                    B.append({"block": blk, "size": L, "first_probe": first, "delay": d,
                              "quantum": qe,
                              "first_realized": r1["realized_sink"] if r1 else None,
                              "second_realized": r2["realized_sink"],
                              "second_capacity": r2["sink_capacity"],
                              "second_rejected": r2["rejected"],
                              "second_reject_reason": r2.get("reject_reason", "")})
            print(f"  {blk} ({time.time()-t0:.0f}s)", flush=True)

    for name, data in (("p07a_impulse_capacity.csv", A), ("p07a_impulse_probe.csv", B)):
        f = sorted({k for d in data for k in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p07a_impulse_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\nimpulse: {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

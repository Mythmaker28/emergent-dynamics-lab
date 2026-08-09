"""07D -- prospective confirmation on never-used seeds, a third size, a second law and
held-out cadences. Predictions are sealed in p07d_protocol.json before the first engine call.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
from od_core import (LatticeBondEngine, LatticeBondState, comps, largest_bounded, cells_of,
                     fhash)
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
import p07_core as P

T_B, SPACING, COAST, N_EVENTS = 256, 16, 2048, 320
SEED_BASE, SEEDS_PER = 950000, 9
AXORD = ("+x", "-x", "+y", "-y")
CAD = 16
SCHED = [272 + SPACING * (e - 1) for e in range(1, N_EVENTS + 1)]
HORIZON = SCHED[-1] + COAST
ARMS = {"SHAM": None, "PARENT": "INTERFACE", "SRC_SINKSIDE": "SINKSIDE"}
CONFIG = [("LAW_16", 24), ("LAW_16", 32), ("LAW_16", 40), ("LAW_29", 24), ("LAW_29", 32)]
HELD_OUT = (2, 8, 32, 128)
WINDOW = 2048
PROTOCOL, SEAL = "p07d_protocol.json", "p07d_protocol.sha256"


def preseal_guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    want = Path(SEAL).read_text().split()[0].strip()
    if got != want:
        sys.exit("PRESEAL_GUARD: protocol hash mismatch")
    for f, h in json.loads(Path(PROTOCOL).read_text())["code_sha256"].items():
        if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal")
    return got


def prephase(law, m, L):
    eng = LatticeBondEngine(law)
    st = LatticeBondState(m.copy(), np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
    while int(st.step) < T_B:
        st = eng.step(st).state
    return st


def dose_branch(law, st0, masks, arm, L, cells256, blk, lawname, ev_rows):
    pl = ARMS[arm]
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    qe = M256 / 80.0
    lin = P.Lineage()
    total0 = float(st.m.sum())
    sched = set(SCHED) if pl else set()
    realized = injected = planned = 0.0
    removed = {c: 0.0 for c in P.COHORTS}
    n_ev = n_rej = 0
    bound = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
    causes = {}
    max_id = max_bal = 0.0
    lin.update(st, T_B)
    t = int(st.step)
    while t < HORIZON:
        if t in sched:
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            planned += qe
            if not track:
                n_rej += 1
                causes["NO_TRACK"] = causes.get("NO_TRACK", 0) + 1
            else:
                r = P.exchange_event(st, prov, masks, track, L, qe, source_placement=pl)
                realized += r["realized_sink"]
                injected += r["realized_source"]
                for k in P.COHORTS:
                    removed[k] += r["removed_by_cohort"][k]
                if r["rejected"]:
                    n_rej += 1
                    causes[r["reject_reason"]] = causes.get(r["reject_reason"], 0) + 1
                else:
                    n_ev += 1
                    q = r["q_event"]
                    k = ("PLANNED" if abs(q - qe) < 1e-9 else
                         "SOURCE" if abs(q - r["source_capacity"]) < 1e-9 else
                         "SINK" if abs(q - r["sink_capacity"]) < 1e-9 else "OTHER")
                    bound[k] += 1
                if n_ev + n_rej <= 8 or (n_ev + n_rej) % 16 == 1:
                    ev_rows.append({"law": lawname, "block": blk, "size": L, "arm": arm,
                                    "time": t, "planned": qe, "q_event": r["q_event"],
                                    "realized_sink": r["realized_sink"],
                                    "sink_capacity": r["sink_capacity"],
                                    "source_capacity": r["source_capacity"],
                                    "n_sink_elig": r["n_sink_elig"],
                                    "rejected": r["rejected"],
                                    "reject_reason": r["reject_reason"]})
                max_id = max(max_id, prov.identity_residual(st))
                max_bal = max(max_bal, prov.global_balance_residual(st, total0))
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)
        if t % CAD == 0:
            lin.update(st, t)
    end = P.snapshot(st, prov, L, M256, I0)
    row = {"law": lawname, "arm": arm, "size": L, "block": blk, "M256": M256, "I0": I0,
           "quantum": qe, "n_scheduled": len(sched), "n_events": n_ev, "n_rejected": n_rej,
           "reject_causes": json.dumps(causes), "bound_by": json.dumps(bound),
           "planned_sink": planned, "realized_sink": realized, "realized_source": injected,
           "DELIVERED_FRACTION": realized / planned if planned else None,
           "incumbent_removed_total": sum(removed[k] for k in P.INCUMBENT),
           "incumbent_removed_over_M256": sum(removed[k] for k in P.INCUMBENT) / M256,
           "REPLACEMENT_EFFICIENCY": (sum(removed[k] for k in P.INCUMBENT) / realized)
                                     if realized > 0 else None,
           "ambient_removed_total": removed["amb"], "fresh_removed_total": removed["fre"],
           "same_track_continuous": lin.continuous, "loss": lin.lost, "merger": lin.merger,
           "split": lin.split, "first_failure_type": lin.first_failure_type,
           "first_failure_time": lin.first_failure_time,
           "max_identity_residual": max_id, "max_global_balance_residual": max_bal}
    for k in ("T", "I", "F", "A", "I_over_I0", "F_over_T", "T_over_M256",
              "mass_in_frozen_C256", "incumbent_in_frozen_C256", "jaccard_C256_Ct",
              "boundary_site_turnover", "area"):
        row[f"terminal_{k}"] = end.get(k) if end.get("track") else None
    return row


def cadence_branch(law, st0, masks, L, cells256, blk, s):
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P.Prov(st, cells256, L)
    M256 = prov.M256
    qe = M256 / 80.0
    n = WINDOW // s
    delivered = planned = 0.0
    inc = 0.0
    n_rej = 0
    bound = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
    for j in range(n):
        c = largest_bounded(st)
        planned += qe
        if c is None:
            n_rej += 1
        else:
            r = P.exchange_event(st, prov, masks, cells_of(c), L, qe,
                                 source_placement="INTERFACE")
            delivered += r["realized_sink"]
            inc += sum(r["removed_by_cohort"][k] for k in P.INCUMBENT)
            if r["rejected"]:
                n_rej += 1
            else:
                q = r["q_event"]
                k = ("PLANNED" if abs(q - qe) < 1e-9 else
                     "SOURCE" if abs(q - r["source_capacity"]) < 1e-9 else
                     "SINK" if abs(q - r["sink_capacity"]) < 1e-9 else "OTHER")
                bound[k] += 1
        for _ in range(s):
            pre = st
            o = eng.step(pre)
            prov.advance(pre.m, o.ledger, o.state.m, law.dt)
            st = o.state
    return {"block": blk, "size": L, "spacing": s, "n_events": n, "window": WINDOW,
            "quantum": qe, "M256": M256, "planned_total": planned,
            "delivered_total": delivered, "PHI_per_step": delivered / WINDOW,
            "incumbent_removed": inc, "delivered_fraction": delivered / planned,
            "n_rejected": n_rej, "bound_by": json.dumps(bound),
            "track_alive_at_end": largest_bounded(st) is not None}


def run():
    seal = preseal_guard()
    print(f"PRESEAL_GUARD OK  {seal}", flush=True)
    laws = law_arms()
    rows, ev, cad, man = [], [], [], []
    calls = 0
    t0 = time.time()
    for lawname, L in CONFIG:
        law = laws[lawname]
        for k in range(SEEDS_PER):
            seed = SEED_BASE + k
            blk = f"{lawname}_L{L}_S{seed}"
            m = np.ascontiguousarray(ic_single_disc(np.random.default_rng(seed), L, 0.35),
                                     dtype=np.float64)
            st = prephase(law, m, L)
            calls += 1
            c = largest_bounded(st)
            nc = len(comps(st))
            status = ("T256_VALID_TRACK" if (c is not None and not (c.wraps_x or c.wraps_y))
                      else "T256_DISSOLVED" if nc == 0
                      else "T256_WRAPPING" if c is not None else "T256_TRACK_LOST")
            man.append({"block": blk, "law": lawname, "size": L, "seed": seed,
                        "t256_status": status})
            if status != "T256_VALID_TRACK":
                continue
            cells = cells_of(c)
            masks = P.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            man[-1].update(t256_sha256=fhash(st.m, st.n, st.b), area256=c.area,
                           axis=AXORD[k % 4], n_components=nc)
            for arm in ARMS:
                r = dose_branch(law, st.copy(), masks, arm, L, cells, blk, lawname, ev)
                calls += 1
                r.update(seed=seed, axis=AXORD[k % 4])
                rows.append(r)
            if lawname == "LAW_16" and L in (24, 32):
                for s in HELD_OUT:
                    cad.append(cadence_branch(law, st.copy(), masks, L, cells, blk, s))
                    calls += 1
            print(f"  {blk} ({len(rows)} traj, {time.time()-t0:.0f}s)", flush=True)
    Path("p07d_manifest.json").write_text(json.dumps(
        {"phase": "07D", "protocol_sha256": seal, "blocks": man,
         "engine_invocations": calls}, indent=1))
    for name, data in (("p07d_rows.csv", rows), ("p07d_event_ledger.csv", ev),
                       ("p07d_cadence_rows.csv", cad)):
        if not data:
            continue
        f = sorted({kk for d in data for kk in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p07d_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n07D: {len(rows)} trajectoires, {len(cad)} cadences, {calls} appels moteur "
          f"({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

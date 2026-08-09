"""08D -- sealed confirmation on never-used seeds, and the two LAW_29 transports."""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../P07")
from od_core import (LatticeBondEngine, LatticeBondState, comps, largest_bounded, cells_of,
                     fhash, MMAX)
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
import p07_core as P7
import p08_core as P8

T_B, SPACING, COAST, N_OPP = 256, 16, 2048, 320
SEED_BASE, SEEDS_PER = 930000, 9
AXORD = ("+x", "-x", "+y", "-y")
CAD, SHADOW_EVERY = 16, 128
KAPPA, REG_FLOOR, BACKLOG_CAP = 0.9, 0.10, 4.0
PROBE_CHECKPOINTS = (272, 1296, 2320)
PROBE_STEPS, SLOPE_W = 32, 8
CONFIG = [("LAW_16", 24, ["SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP"]),
          ("LAW_16", 32, ["SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP"]),
          ("LAW_29", 24, ["SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP",
                          "ONLINE_STRICT", "ONLINE_NORMALIZED"]),
          ("LAW_29", 32, ["SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP",
                          "ONLINE_STRICT", "ONLINE_NORMALIZED"])]
PROTOCOL, SEAL = "p08d_protocol.json", "p08d_protocol.sha256"


def guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    if got != Path(SEAL).read_text().split()[0]:
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


def clone_prov(pv, st0, cells, L):
    q = P7.Prov(st0, cells, L)
    for k in P7.COHORTS:
        q.f[k] = pv.f[k].copy()
    q.res_sink, q.res_source = pv.res_sink, pv.res_source
    q.sink_by_cohort = dict(pv.sink_by_cohort)
    return q


def saturate(state, prov, mask, track):
    fm = state.m.reshape(-1)
    ff = prov.f["fre"].reshape(-1)
    added = 0.0
    for i in mask:
        if i in track:
            room = MMAX - fm[i]
            if room > 1e-12:
                fm[i] += room
                ff[i] += room
                added += room
    prov.res_source += added
    return added


def headroom(state, mask, track):
    fm = state.m.reshape(-1)
    return math.fsum(MMAX - fm[i] for i in mask if i in track and fm[i] < MMAX)


def branch(law, lawname, st0, masks, arm, L, cells256, blk, spacing, ev_rows, probes):
    online = arm.startswith("ONLINE")
    rule = "PARENT" if (arm in ("SHAM", "PARENT") or online) else arm
    floor, ceil = P8.AMOUNT_RULES[rule]
    opp_times = [272 + spacing * (e - 1) for e in range(1, N_OPP + 1)]
    horizon = opp_times[-1] + COAST
    opp = {t: i for i, t in enumerate(opp_times)}
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P7.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    qe = M256 / 80.0
    lin = P7.Lineage()
    total0 = float(st.m.sum())
    backlog = 0.0
    attempted = realized = 0.0
    removed = {c: 0.0 for c in P8.COHORTS}
    n_ev = n_rej = n_wait = 0
    bound = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
    causes = {}
    max_id = max_bal = 0.0
    delivered_at = {}
    cum = 0.0
    lin.update(st, T_B)
    t = int(st.step)
    while t < horizon:
        if t in opp:
            j = opp[t]
            attempted += qe
            backlog += qe
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            intended = min(backlog, BACKLOG_CAP * qe) if online else qe
            if not track:
                n_rej += 1
                causes["NO_TRACK"] = causes.get("NO_TRACK", 0) + 1
            elif arm == "SHAM":
                pass
            else:
                fire = True
                if online:
                    s = P8.sensor_readout(st, masks, track, L, floor, ceil)
                    fire = (s["feasible_q"] >= KAPPA * intended
                            and s["mask_registration"] >= REG_FLOOR) or j == len(opp_times) - 1
                if not fire:
                    n_wait += 1
                else:
                    r = P8.exchange_event(st, prov, masks, track, L, intended, floor, ceil)
                    realized += r["realized_sink"]
                    cum += r["realized_sink"]
                    for k in P8.COHORTS:
                        removed[k] += r["removed_by_cohort"][k]
                    if r["rejected"]:
                        n_rej += 1
                        causes[r["reject_reason"]] = causes.get(r["reject_reason"], 0) + 1
                    else:
                        n_ev += 1
                        bound[r["bound_by"]] += 1
                    backlog = max(0.0, backlog - intended)
                    max_id = max(max_id, prov.identity_residual(st))
                    max_bal = max(max_bal, prov.global_balance_residual(st, total0))
                    if j % 8 == 0 or r["rejected"]:
                        ev_rows.append({"law": lawname, "block": blk, "size": L, "arm": arm,
                                        "time": t, "opportunity": j, "intended": intended,
                                        "q_event": r["q_event"],
                                        "realized_sink": r["realized_sink"],
                                        "sink_capacity": r["sink_capacity"],
                                        "source_capacity": r["source_capacity"],
                                        "rejected": r["rejected"],
                                        "reject_reason": r["reject_reason"],
                                        "bound_by": r["bound_by"], "M256": M256})
            if arm == "PARENT" and t in PROBE_CHECKPOINTS and track:
                delivered_at[t] = cum
                cl = st.copy()
                pv = clone_prov(prov, st, cells256, L)
                added = saturate(cl, pv, masks["source"], track)
                e2 = LatticeBondEngine(law)
                H = []
                for u in range(PROBE_STEPS + 1):
                    cur = largest_bounded(cl)
                    H.append(headroom(cl, masks["source"], cells_of(cur) if cur else set()))
                    if u < PROBE_STEPS:
                        pre = cl
                        o = e2.step(pre)
                        pv.advance(pre.m, o.ledger, o.state.m, law.dt)
                        cl = o.state
                probes.append({"law": lawname, "block": blk, "size": L, "checkpoint": t,
                               "rho_probe_slope8": (H[SLOPE_W] - H[0]) / SLOPE_W,
                               "saturation_mass_added": added, "M256": M256, "quantum": qe})
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)
        if t % CAD == 0:
            lin.update(st, t)
            max_id = max(max_id, prov.identity_residual(st))
    for i, tt in enumerate(PROBE_CHECKPOINTS[:-1]):
        nx = PROBE_CHECKPOINTS[i + 1]
        if tt in delivered_at and nx in delivered_at:
            for p in probes:
                if p["block"] == blk and p["checkpoint"] == tt and p["law"] == lawname:
                    p["rho_observed_next_window"] = (delivered_at[nx] - delivered_at[tt]) \
                                                    / (nx - tt)
                    p["src_bound_fraction_next_window"] = None
    cur = largest_bounded(st)
    cs = cells_of(cur) if cur is not None else set()
    u = P8.unique_causal_replacement(prov, cs, M256)
    sh = P8.shadow_readout(st, cs, prov.cells256) if cur is not None else {}
    fm = st.m.reshape(-1)
    T = math.fsum(fm[i] for i in cs) if cs else None
    I = prov.incumbent_in(cs) if cs else 0.0
    row = {"law": lawname, "arm": arm, "size": L, "block": blk, "M256": M256, "I0": I0,
           "quantum": qe, "spacing": spacing, "floor": floor, "ceil": ceil,
           "n_opportunities": len(opp_times), "n_events": n_ev, "n_waited": n_wait,
           "n_rejected": n_rej, "reject_causes": json.dumps(causes),
           "bound_by": json.dumps(bound), "attempted_mass": attempted,
           "realized_sink": realized,
           "DELIVERED_FRACTION": realized / attempted if attempted else 0.0,
           "delivered_over_M256": realized / M256,
           "UCR": u["UCR"], "incumbent_removed_over_M256": u["inc_over_M256"],
           "fresh_over_M256": u["fresh_over_M256"],
           "futile_fraction": P8.futile_fraction(prov),
           "incumbent_displacement": (1.0 - I / I0) if I0 > 0 else None,
           "terminal_T": T, "terminal_I_over_I0": (I / I0) if (I0 > 0 and cs) else None,
           "same_track_continuous": lin.continuous, "loss": lin.lost, "split": lin.split,
           "merger": lin.merger, "reacquisition": lin.reacq,
           "first_failure_time": lin.first_failure_time,
           "first_failure_type": lin.first_failure_type,
           "max_identity_residual": max_id, "max_global_balance_residual": max_bal}
    row.update({f"terminal_{k}": v for k, v in sh.items()})
    return row


def sham_relaxation_spacing(law, st, masks, cells, L):
    """LAW_29 spacing normalisation, computed from a SHAM clone only."""
    eng = LatticeBondEngine(law)
    prov = P7.Prov(st, cells, L)
    a = st.copy()
    base = None
    steps = 0
    for u in range(256):
        cur = largest_bounded(a)
        if cur is None:
            break
        T = math.fsum(a.m.reshape(-1)[i] for i in cells_of(cur))
        if base is None:
            base = T
        elif abs(T - base) / base >= 0.02:
            steps = u
            break
        pre = a
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        a = o.state
    return max(1, steps)


def run():
    seal = guard()
    print(f"PRESEAL_GUARD OK  {seal}", flush=True)
    laws = law_arms()
    rows, ev, probes, man = [], [], [], []
    calls = 0
    t0 = time.time()
    tau = {}
    for lawname, L, arms in CONFIG:
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
            masks = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            man[-1].update(t256_sha256=fhash(st.m, st.n, st.b), area256=c.area)
            tau.setdefault((lawname, L), []).append(
                sham_relaxation_spacing(law, st.copy(), masks, cells, L))
            for arm in arms:
                sp = SPACING
                if arm == "ONLINE_NORMALIZED":
                    t29 = int(np.median(tau.get((lawname, L), [16])))
                    t16 = 16
                    r = max(1.0, t29 / t16)
                    sp = int(2 ** round(math.log2(SPACING * r)))
                    sp = max(4, min(64, sp))
                r = branch(law, lawname, st.copy(), masks, arm, L, cells, blk, sp, ev, probes)
                calls += 1
                r.update(seed=seed, axis=AXORD[k % 4])
                rows.append(r)
            print(f"  {blk} ({len(rows)} traj, {time.time()-t0:.0f}s)", flush=True)
    Path("p08d_manifest.json").write_text(json.dumps(
        {"phase": "08D", "protocol_sha256": seal, "blocks": man,
         "sham_relaxation_steps": {f"{k[0]}|L{k[1]}": v for k, v in tau.items()},
         "engine_invocations": calls}, indent=1))
    for name, data in (("p08d_rows.csv", rows), ("p08d_event_ledger.csv", ev),
                       ("p08d_probe.csv", probes)):
        if not data:
            continue
        f = sorted({kk for d in data for kk in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p08d_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n08D: {len(rows)} trajectoires, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

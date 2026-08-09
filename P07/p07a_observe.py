"""07A -- observational capacity spectrum + exact per-step sweep accounting.

Reproduces DEV_05's DIRECT_Q400_UNIFORM and DIRECT_Q800_UNIFORM bit-for-bit (fixture 2 proves
the operator is identical) and adds the instrumentation DEV_05 never saved. No new physics,
no new intervention: this phase MEASURES.

Refuses every engine call unless p07a_protocol.json matches its sealed SHA-256 and the sealed
code hashes still match.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
from od_core import (LatticeBondEngine, LatticeBondState, comps, largest_bounded, cells_of,
                     fhash, THRESH)
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
import p07_core as P

P_OCC = 0.35
SIZES = (24, 32)
SEEDS_PER = 9
SEED_BASE = 990000
T_B = 256
SPACING = 16
COAST = 2048
AXORD = ("+x", "-x", "+y", "-y")
CAD = 16
PROTOCOL, SEAL = "p07a_protocol.json", "p07a_protocol.sha256"


def uniform_sched(n):
    return [272 + SPACING * (e - 1) for e in range(1, n + 1)]


SCHED = {"PARENT_Q400_UNIFORM": uniform_sched(320), "PARENT_Q800_UNIFORM": uniform_sched(640),
         "SHAM": []}
ARMS = ["SHAM", "PARENT_Q400_UNIFORM", "PARENT_Q800_UNIFORM"]
TERM = {a: (SCHED[a][-1] + COAST if SCHED[a] else 0) for a in ARMS}
TERM["SHAM"] = max(TERM.values())
# the SHAM is probed (never acted on) at exactly the Q800 schedule times
PROBE_TIMES = {"SHAM": set(SCHED["PARENT_Q800_UNIFORM"])}


def preseal_guard():
    p, s = Path(PROTOCOL), Path(SEAL)
    if not p.exists() or not s.exists():
        sys.exit("PRESEAL_GUARD: protocol or seal missing -- no engine call permitted.")
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    want = s.read_text().split()[0].strip()
    if got != want:
        sys.exit(f"PRESEAL_GUARD: protocol hash mismatch\n sealed={want}\n actual={got}")
    for f, h in json.loads(p.read_text())["code_sha256"].items():
        cur = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        if cur != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal\n sealed={h}\n actual={cur}")
    return got


def prephase(law, m, L):
    eng = LatticeBondEngine(law)
    st = LatticeBondState(m.copy(), np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
    while int(st.step) < T_B:
        st = eng.step(st).state
    return st


def branch(law, st0, masks, arm, L, cells256, blk, ev_rows, tr_rows):
    sched = set(SCHED[arm]) or PROBE_TIMES.get(arm, set())
    acting = bool(SCHED[arm])
    horizon = TERM[arm]
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    qe = M256 / 80.0
    lin = P.Lineage()
    total0 = float(st.m.sum())

    cum = {"MATERIAL_CHANGE_ON_RETAINED_SITES": 0.0, "MASK_ENTRY": 0.0, "MASK_EXIT": 0.0,
           "TRACKER_SWEEP": 0.0}
    cum_abs_sweep = 0.0
    n_gap = 0                      # steps where the track was absent -> accounting suspended
    realized_sink = realized_source = planned_total = 0.0
    removed_tot = {c: 0.0 for c in P.COHORTS}
    n_events = n_rejected = 0
    reject_causes = {}
    max_ident = max_bal = 0.0
    snaps = {}

    cur = lin.update(st, T_B)
    prev_cells = cells_of(cur) if cur is not None else None
    prev_m = st.m.reshape(-1).copy()
    T_at_t256 = math.fsum(prev_m[i] for i in prev_cells) if prev_cells else float("nan")
    snaps[T_B] = P.snapshot(st, prov, L, M256, I0)

    t = int(st.step)
    while t < horizon:
        if t in sched:
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            if track:
                spec = P.capacity_spectrum(st, masks, track, L)     # BEFORE any mutation
                if acting:
                    r = P.exchange_event(st, prov, masks, track, L, qe)
                    planned_total += qe
                    realized_sink += r["realized_sink"]
                    realized_source += r["realized_source"]
                    for k in P.COHORTS:
                        removed_tot[k] += r["removed_by_cohort"][k]
                    if r["rejected"]:
                        n_rejected += 1
                        reject_causes[r["reject_reason"]] = \
                            reject_causes.get(r["reject_reason"], 0) + 1
                    else:
                        n_events += 1
                else:
                    r = {"q_event": 0.0, "realized_sink": 0.0, "realized_source": 0.0,
                         "removed_by_cohort": {k: 0.0 for k in P.COHORTS},
                         "n_sink_sites": 0, "n_source_sites": 0, "rejected": True,
                         "reject_reason": "SHAM", "n_sink_elig": spec["NEL_PARENT"],
                         "n_source_elig": 0, "sink_capacity": spec["CAP_PARENT"],
                         "source_capacity": float("nan"), "physical_state_delta": 0.0}
                ident = prov.identity_residual(st)
                bal = prov.global_balance_residual(st, total0)
                max_ident, max_bal = max(max_ident, ident), max(max_bal, bal)
                row = {"block": blk, "size": L, "arm": arm, "time": t, "planned": qe,
                       "q_event": r["q_event"], "realized_sink": r["realized_sink"],
                       "realized_source": r["realized_source"],
                       "n_sink_sites": r["n_sink_sites"], "n_source_sites": r["n_source_sites"],
                       "n_source_elig": r["n_source_elig"],
                       "source_capacity": r["source_capacity"],
                       "rejected": r["rejected"], "reject_reason": r["reject_reason"],
                       "incumbent_removed": sum(r["removed_by_cohort"][k] for k in P.INCUMBENT),
                       "ambient_removed": r["removed_by_cohort"]["amb"],
                       "fresh_removed": r["removed_by_cohort"]["fre"],
                       "core_removed": r["removed_by_cohort"]["core"],
                       "inter_removed": r["removed_by_cohort"]["inter"],
                       "bnd_removed": r["removed_by_cohort"]["bnd"],
                       "M256": M256, "identity_residual": ident, "global_balance_residual": bal}
                row.update(spec)
                ev_rows.append(row)
            else:
                ev_rows.append({"block": blk, "size": L, "arm": arm, "time": t, "planned": qe,
                                "rejected": True, "reject_reason": "NO_TRACK", "M256": M256})
                if acting:
                    n_rejected += 1
                    reject_causes["NO_TRACK"] = reject_causes.get("NO_TRACK", 0) + 1

        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)

        # ---- exact per-step sweep accounting ---------------------------------
        cc = largest_bounded(st)
        if cc is None:
            prev_cells, n_gap = None, n_gap + 1
        else:
            cells = cells_of(cc)
            fm = st.m.reshape(-1)
            d = P.sweep_decomposition(prev_cells, prev_m, cells, fm)
            if d is not None:
                for k in cum:
                    cum[k] += d[k]
                cum_abs_sweep += abs(d["MASK_ENTRY"]) + abs(d["MASK_EXIT"])
            prev_cells = cells
        prev_m = st.m.reshape(-1).copy()

        if t % CAD == 0:
            cur = lin.update(st, t)
            if cur is not None:
                cs = cells_of(cur)
                fm = st.m.reshape(-1)
                T = math.fsum(fm[i] for i in cs)
                I = prov.incumbent_in(cs)
                F = prov.mass_in(cs, "fre")
                A = prov.mass_in(cs, "amb")
                fmet = P.frame_metrics(st, prov, cs, L)
                tr = {"block": blk, "size": L, "arm": arm, "time": t, "track": True,
                      "T": T, "I": I, "F": F, "A": A, "M256": M256, "I0": I0,
                      "I_over_I0": I / I0 if I0 > 0 else None,
                      "F_over_T": F / T if T > 0 else None,
                      "T_over_M256": T / M256, "cy": cur.centroid_y, "cx": cur.centroid_x,
                      "same_track": lin.continuous, "n_gap_steps": n_gap,
                      "cum_dT_check": T - T_at_t256}
                tr.update(fmet)
                tr.update({f"CUM_{k}": v for k, v in cum.items()})
                tr["CUM_ABS_SWEEP"] = cum_abs_sweep
                tr_rows.append(tr)
                if t % 512 == 0 or t == horizon:
                    snaps[t] = P.snapshot(st, prov, L, M256, I0)
            else:
                tr_rows.append({"block": blk, "size": L, "arm": arm, "time": t, "track": False,
                                "M256": M256, "I0": I0, "n_gap_steps": n_gap,
                                "same_track": False})
            max_ident = max(max_ident, prov.identity_residual(st))

    end = P.snapshot(st, prov, L, M256, I0)
    snaps[horizon] = end
    tf = SCHED[arm][-1] if SCHED[arm] else 0
    row = {"arm": arm, "size": L, "block": blk, "M256": M256, "I0": I0, "quantum": qe,
           "n_scheduled": len(SCHED[arm]), "n_events": n_events, "n_rejected": n_rejected,
           "reject_causes": json.dumps(reject_causes), "terminal_time": horizon,
           "force_end_time": tf, "planned_sink": planned_total,
           "realized_sink": realized_sink, "realized_source": realized_source,
           "incumbent_removed_total": sum(removed_tot[k] for k in P.INCUMBENT),
           "ambient_removed_total": removed_tot["amb"],
           "fresh_removed_total": removed_tot["fre"],
           "same_track_continuous": lin.continuous, "merger": lin.merger, "split": lin.split,
           "loss": lin.lost, "reacquisition": lin.reacq, "n_gap_steps": n_gap,
           "first_failure_time": lin.first_failure_time,
           "first_failure_type": lin.first_failure_type,
           "max_identity_residual": max_ident, "max_global_balance_residual": max_bal,
           "T_at_t256": T_at_t256}
    row.update({f"CUM_{k}": v for k, v in cum.items()})
    row["CUM_ABS_SWEEP"] = cum_abs_sweep
    for k in ("T", "I", "F", "A", "I_over_I0", "F_over_T", "T_over_M256",
              "mass_in_frozen_C256", "incumbent_in_frozen_C256", "fresh_in_frozen_C256",
              "mass_in_C256_cap_Ct", "jaccard_C256_Ct", "boundary_site_turnover",
              "scaffold_cells", "scaffold_mass", "area", "perimeter"):
        row[f"terminal_{k}"] = end.get(k) if end.get("track") else None
    row["snapshots"] = json.dumps({str(k): {kk: vv for kk, vv in v.items() if kk != "cells"}
                                   for k, v in sorted(snaps.items())})
    return row


def run():
    seal = preseal_guard()
    print(f"PRESEAL_GUARD OK  protocol sha256 = {seal}", flush=True)
    law = law_arms()["LAW_16"]
    rows, ev, tr, manifest = [], [], [], []
    calls = 0
    t0 = time.time()
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            blk = f"L{L}_S{seed}"
            m = np.ascontiguousarray(ic_single_disc(np.random.default_rng(seed), L, P_OCC),
                                     dtype=np.float64)
            h0 = fhash(m, np.full((L, L), 0.8), np.zeros((2, L, L)))
            st = prephase(law, m, L)
            calls += 1
            c = largest_bounded(st)
            ncomp = len(comps(st))
            status = ("T256_VALID_TRACK" if (c is not None and not (c.wraps_x or c.wraps_y))
                      else "T256_DISSOLVED" if ncomp == 0
                      else "T256_WRAPPING" if c is not None else "T256_TRACK_LOST")
            if status != "T256_VALID_TRACK":
                manifest.append({"block": blk, "size": L, "seed": seed, "t256_status": status})
                continue
            cells = cells_of(c)
            hb = fhash(st.m, st.n, st.b)
            axis = AXORD[k % 4]
            masks = P.build_masks(cells, L, c.centroid_y, c.centroid_x, axis)
            core, inter, bnd = P.depth_partition(cells, L)
            probe = P.Prov(st, cells, L)
            manifest.append({"block": blk, "size": L, "seed": seed, "axis": axis,
                             "t256_status": status, "t0_sha256": h0, "t256_sha256": hb,
                             "M256": probe.M256, "area256": c.area,
                             "n_components_t256": ncomp, "n_core": len(core),
                             "n_inter": len(inter), "n_bnd": len(bnd),
                             "mask_sink": len(masks["sink"]),
                             "mask_source": len(masks["source"])})
            np.save(f"_t256_{blk}.npy", np.stack([st.m, st.n]))
            np.save(f"_t256b_{blk}.npy", st.b)
            for a in ARMS:
                r = branch(law, st.copy(), masks, a, L, cells, blk, ev, tr)
                calls += 1
                r.update(seed=seed, axis=axis, t0_sha256=h0, t256_sha256=hb,
                         t256_status=status, n_core=len(core), n_inter=len(inter),
                         n_bnd=len(bnd))
                rows.append(r)
                print(f"  {blk} {a:<22} ({len(rows)}/{len(ARMS)*18}, "
                      f"{time.time()-t0:.0f}s)", flush=True)

    Path("p07a_manifest.json").write_text(json.dumps(
        {"phase": "07A", "protocol_sha256": seal, "blocks": manifest,
         "engine_invocations": calls}, indent=1))
    for name, data in (("p07a_rows.csv", rows), ("p07a_event_ledger.csv", ev),
                       ("p07a_trace.csv", tr)):
        if not data:
            continue
        f = sorted({k for d in data for k in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p07a_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n07A: {len(rows)} trajectoires, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

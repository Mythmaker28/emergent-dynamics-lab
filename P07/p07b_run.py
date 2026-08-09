"""07B -- one gate at a time, matched dose, matched t256 state.

Reuses the 07A t256 checkpoints (SHA-256 verified) and the 07A SHAM / PARENT_Q400 branches as
reference arms, so no engine call is spent reproducing what is already sealed and identical.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
from od_core import (LatticeBondEngine, LatticeBondState, largest_bounded, cells_of, fhash)
from bridge00_harness import law_arms
import p07_core as P

T_B, SPACING, COAST = 256, 16, 2048
N_EVENTS = 320
SIZES, SEEDS_PER, SEED_BASE = (24, 32), 9, 990000
AXORD = ("+x", "-x", "+y", "-y")
CAD = 16
SCHED = [272 + SPACING * (e - 1) for e in range(1, N_EVENTS + 1)]
HORIZON = SCHED[-1] + COAST
PROTOCOL, SEAL = "p07b_protocol.json", "p07b_protocol.sha256"

ARMS = {
    "COMOVING":      dict(gate=P.Gate("COMOVING", mask="COMOVING"), src="INTERFACE"),
    "TRACKALL":      dict(gate=P.Gate("TRACKALL", mask="TRACKALL"), src="INTERFACE"),
    "MULTISITE":     dict(gate=P.Gate("MULTISITE", spread="MULTISITE"), src="INTERFACE"),
    "UNTRACKED":     dict(gate=P.Gate("UNTRACKED", track=False, thresh=True), src="INTERFACE"),
    "SRC_DISPERSED": dict(gate=P.Gate("PARENT"), src="DISPERSED"),
    "SRC_SINKSIDE":  dict(gate=P.Gate("PARENT"), src="SINKSIDE"),
}


def preseal_guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    want = Path(SEAL).read_text().split()[0].strip()
    if got != want:
        sys.exit(f"PRESEAL_GUARD: protocol hash mismatch\n sealed={want}\n actual={got}")
    for f, h in json.loads(Path(PROTOCOL).read_text())["code_sha256"].items():
        if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal")
    return got


def branch(law, st0, masks, arm, L, cells256, blk, ev_rows, tr_rows):
    spec_arm = ARMS[arm]
    gate, src = spec_arm["gate"], spec_arm["src"]
    sched = set(SCHED)
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    qe = M256 / 80.0
    lin = P.Lineage()
    total0 = float(st.m.sum())
    cum = {"MATERIAL_CHANGE_ON_RETAINED_SITES": 0.0, "MASK_ENTRY": 0.0, "MASK_EXIT": 0.0,
           "TRACKER_SWEEP": 0.0}
    cum_abs = 0.0
    n_gap = 0
    realized_sink = realized_source = planned_total = 0.0
    removed_tot = {c: 0.0 for c in P.COHORTS}
    n_events = n_rejected = 0
    causes = {}
    max_ident = max_bal = 0.0
    snaps = {}

    cur = lin.update(st, T_B)
    prev_cells = cells_of(cur) if cur is not None else None
    prev_m = st.m.reshape(-1).copy()
    T0 = math.fsum(prev_m[i] for i in prev_cells) if prev_cells else float("nan")
    snaps[T_B] = P.snapshot(st, prov, L, M256, I0)

    t = int(st.step)
    while t < HORIZON:
        if t in sched:
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            planned_total += qe
            if track:
                cs = P.capacity_spectrum(st, masks, track, L)
                r = P.exchange_event(st, prov, masks, track, L, qe, gate, src)
                realized_sink += r["realized_sink"]
                realized_source += r["realized_source"]
                for k in P.COHORTS:
                    removed_tot[k] += r["removed_by_cohort"][k]
                if r["rejected"]:
                    n_rejected += 1
                    causes[r["reject_reason"]] = causes.get(r["reject_reason"], 0) + 1
                else:
                    n_events += 1
                ident = prov.identity_residual(st)
                bal = prov.global_balance_residual(st, total0)
                max_ident, max_bal = max(max_ident, ident), max(max_bal, bal)
                row = {"block": blk, "size": L, "arm": arm, "time": t, "planned": qe,
                       "q_event": r["q_event"], "realized_sink": r["realized_sink"],
                       "realized_source": r["realized_source"],
                       "n_sink_sites": r["n_sink_sites"], "n_source_sites": r["n_source_sites"],
                       "n_sink_elig": r["n_sink_elig"], "n_source_elig": r["n_source_elig"],
                       "sink_capacity": r["sink_capacity"],
                       "source_capacity": r["source_capacity"],
                       "rejected": r["rejected"], "reject_reason": r["reject_reason"],
                       "incumbent_removed": sum(r["removed_by_cohort"][k] for k in P.INCUMBENT),
                       "ambient_removed": r["removed_by_cohort"]["amb"],
                       "fresh_removed": r["removed_by_cohort"]["fre"],
                       "M256": M256, "identity_residual": ident,
                       "global_balance_residual": bal}
                row.update(cs)
                ev_rows.append(row)
            else:
                n_rejected += 1
                causes["NO_TRACK"] = causes.get("NO_TRACK", 0) + 1
                ev_rows.append({"block": blk, "size": L, "arm": arm, "time": t, "planned": qe,
                                "rejected": True, "reject_reason": "NO_TRACK", "M256": M256})
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)
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
                cum_abs += abs(d["MASK_ENTRY"]) + abs(d["MASK_EXIT"])
            prev_cells = cells
        prev_m = st.m.reshape(-1).copy()
        if t % CAD == 0:
            cur = lin.update(st, t)
            if cur is not None:
                csx = cells_of(cur)
                fm = st.m.reshape(-1)
                T = math.fsum(fm[i] for i in csx)
                I = prov.incumbent_in(csx)
                F = prov.mass_in(csx, "fre")
                A = prov.mass_in(csx, "amb")
                tr = {"block": blk, "size": L, "arm": arm, "time": t, "track": True,
                      "T": T, "I": I, "F": F, "A": A, "M256": M256, "I0": I0,
                      "I_over_I0": I / I0 if I0 > 0 else None,
                      "F_over_T": F / T if T > 0 else None, "T_over_M256": T / M256,
                      "cy": cur.centroid_y, "cx": cur.centroid_x,
                      "same_track": lin.continuous, "n_gap_steps": n_gap}
                tr.update(P.frame_metrics(st, prov, csx, L))
                tr.update({f"CUM_{k}": v for k, v in cum.items()})
                tr["CUM_ABS_SWEEP"] = cum_abs
                tr_rows.append(tr)
                if t % 512 == 0:
                    snaps[t] = P.snapshot(st, prov, L, M256, I0)
            else:
                tr_rows.append({"block": blk, "size": L, "arm": arm, "time": t, "track": False,
                                "M256": M256, "I0": I0, "n_gap_steps": n_gap,
                                "same_track": False})
            max_ident = max(max_ident, prov.identity_residual(st))

    end = P.snapshot(st, prov, L, M256, I0)
    snaps[HORIZON] = end
    row = {"arm": arm, "size": L, "block": blk, "M256": M256, "I0": I0, "quantum": qe,
           "n_scheduled": len(SCHED), "n_events": n_events, "n_rejected": n_rejected,
           "reject_causes": json.dumps(causes), "terminal_time": HORIZON,
           "force_end_time": SCHED[-1], "planned_sink": planned_total,
           "realized_sink": realized_sink, "realized_source": realized_source,
           "DELIVERED_FRACTION": realized_sink / planned_total if planned_total else None,
           "incumbent_removed_total": sum(removed_tot[k] for k in P.INCUMBENT),
           "ambient_removed_total": removed_tot["amb"],
           "fresh_removed_total": removed_tot["fre"],
           "same_track_continuous": lin.continuous, "merger": lin.merger, "split": lin.split,
           "loss": lin.lost, "reacquisition": lin.reacq, "n_gap_steps": n_gap,
           "first_failure_time": lin.first_failure_time,
           "first_failure_type": lin.first_failure_type,
           "max_identity_residual": max_ident, "max_global_balance_residual": max_bal,
           "T_at_t256": T0, "gate": json.dumps(spec_arm["gate"].as_dict()),
           "source_placement": src}
    row.update({f"CUM_{k}": v for k, v in cum.items()})
    row["CUM_ABS_SWEEP"] = cum_abs
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
    man = {b["block"]: b for b in json.loads(Path("p07a_manifest.json").read_text())["blocks"]}
    rows, ev, tr = [], [], []
    calls = 0
    t0 = time.time()
    names = list(ARMS)
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            blk = f"L{L}_S{seed}"
            info = man.get(blk)
            if info is None or info.get("t256_status") != "T256_VALID_TRACK":
                continue
            a = np.load(f"_t256_{blk}.npy")
            b = np.load(f"_t256b_{blk}.npy")
            st = LatticeBondState(np.ascontiguousarray(a[0]), np.ascontiguousarray(a[1]),
                                  np.ascontiguousarray(b), T_B)
            hb = fhash(st.m, st.n, st.b)
            if hb != info["t256_sha256"]:
                sys.exit(f"T256 STATE HASH MISMATCH for {blk}: refusing to run.")
            c = largest_bounded(st)
            cells = cells_of(c)
            masks = P.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            for arm in names:
                r = branch(law, st.copy(), masks, arm, L, cells, blk, ev, tr)
                calls += 1
                r.update(seed=seed, axis=AXORD[k % 4], t256_sha256=hb)
                rows.append(r)
                print(f"  {blk} {arm:<16} ({len(rows)}/{len(names)*18}, "
                      f"{time.time()-t0:.0f}s)", flush=True)
    for name, data in (("p07b_rows.csv", rows), ("p07b_event_ledger.csv", ev),
                       ("p07b_trace.csv", tr)):
        if not data:
            continue
        f = sorted({k for d in data for k in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p07b_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n07B: {len(rows)} trajectoires, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

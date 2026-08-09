"""08B -- the 2x2 amount-rule factorial. WHEN and WHERE are held identical; only AMOUNT varies.

Refuses every engine call unless p08b_protocol.json matches its seal and the sealed code
hashes still match, and unless every t256 state hashes to the value recorded by P07.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../P07")
from od_core import LatticeBondEngine, LatticeBondState, largest_bounded, cells_of, fhash
from bridge00_harness import law_arms
import p07_core as P7
import p08_core as P8

T_B, SPACING, COAST, N_EVENTS = 256, 16, 2048, 320
SIZES, SEEDS_PER, SEED_BASE = (24, 32), 9, 990000
AXORD = ("+x", "-x", "+y", "-y")
CAD, SHADOW_EVERY = 16, 128
SCHED = [272 + SPACING * (e - 1) for e in range(1, N_EVENTS + 1)]
HORIZON = SCHED[-1] + COAST
ARMS = ["SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP", "BOTH_SAFE"]
P7DIR = Path("../P07")
PROTOCOL, SEAL = "p08b_protocol.json", "p08b_protocol.sha256"


def preseal_guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    want = Path(SEAL).read_text().split()[0]
    if got != want:
        sys.exit("PRESEAL_GUARD: protocol hash mismatch")
    for f, h in json.loads(Path(PROTOCOL).read_text())["code_sha256"].items():
        if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal")
    return got


def branch(law, st0, masks, arm, L, cells256, blk, ev_rows, tr_rows):
    floor, ceil = P8.AMOUNT_RULES.get(arm, (0.0, 1.0))
    mode = "SHAM" if arm == "SHAM" else "COUPLED"
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P7.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    qe = M256 / 80.0
    lin = P7.Lineage()
    total0 = float(st.m.sum())
    sched = set(SCHED)
    realized = injected = planned = 0.0
    removed = {c: 0.0 for c in P8.COHORTS}
    n_ev = n_rej = 0
    bound = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
    causes = {}
    max_id = max_bal = 0.0
    cum = {"MATERIAL_CHANGE_ON_RETAINED_SITES": 0.0, "MASK_ENTRY": 0.0, "MASK_EXIT": 0.0,
           "TRACKER_SWEEP": 0.0}
    cum_abs = 0.0
    n_gap = 0
    lin.update(st, T_B)
    cur = largest_bounded(st)
    prev_cells = cells_of(cur) if cur is not None else None
    prev_m = st.m.reshape(-1).copy()

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
                sen = P8.sensor_readout(st, masks, track, L, floor, ceil)
                r = P8.exchange_event(st, prov, masks, track, L, qe, floor, ceil, mode)
                realized += r["realized_sink"]
                injected += r["realized_source"]
                for k in P8.COHORTS:
                    removed[k] += r["removed_by_cohort"][k]
                if r["rejected"]:
                    n_rej += 1
                    causes[r["reject_reason"]] = causes.get(r["reject_reason"], 0) + 1
                else:
                    n_ev += 1
                    bound[r["bound_by"]] += 1
                ident = prov.identity_residual(st)
                bal = prov.global_balance_residual(st, total0)
                max_id, max_bal = max(max_id, ident), max(max_bal, bal)
                ev_rows.append({"block": blk, "size": L, "arm": arm, "time": t, "planned": qe,
                                "q_event": r["q_event"], "realized_sink": r["realized_sink"],
                                "sink_capacity": r["sink_capacity"],
                                "source_capacity": r["source_capacity"],
                                "n_sink_elig": r["n_sink_elig"],
                                "n_source_elig": r["n_source_elig"],
                                "n_sink_sites": r["n_sink_sites"],
                                "mask_registration": sen["mask_registration"],
                                "feasible_q": sen["feasible_q"],
                                "incumbent_removed": sum(r["removed_by_cohort"][k]
                                                         for k in P8.INCUMBENT),
                                "fresh_removed": r["removed_by_cohort"]["fre"],
                                "ambient_removed": r["removed_by_cohort"]["amb"],
                                "rejected": r["rejected"],
                                "reject_reason": r["reject_reason"],
                                "bound_by": r["bound_by"], "M256": M256,
                                "identity_residual": ident,
                                "global_balance_residual": bal})
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)
        cc = largest_bounded(st)
        if cc is None:
            prev_cells, n_gap = None, n_gap + 1
        else:
            cs = cells_of(cc)
            d = P7.sweep_decomposition(prev_cells, prev_m, cs, st.m.reshape(-1))
            if d is not None:
                for k in cum:
                    cum[k] += d[k]
                cum_abs += abs(d["MASK_ENTRY"]) + abs(d["MASK_EXIT"])
            prev_cells = cs
        prev_m = st.m.reshape(-1).copy()

        if t % CAD == 0:
            cur = lin.update(st, t)
            row = {"block": blk, "size": L, "arm": arm, "time": t, "M256": M256, "I0": I0,
                   "same_track": lin.continuous, "n_gap_steps": n_gap}
            if cur is not None:
                cs = cells_of(cur)
                fm = st.m.reshape(-1)
                T = math.fsum(fm[i] for i in cs)
                I = prov.incumbent_in(cs)
                F = prov.mass_in(cs, "fre")
                A = prov.mass_in(cs, "amb")
                u = P8.unique_causal_replacement(prov, cs, M256)
                row.update({"track": True, "T": T, "I": I, "F": F, "A": A,
                            "I_over_I0": I / I0 if I0 > 0 else None,
                            "F_over_T": F / T if T > 0 else None, "T_over_M256": T / M256,
                            "UCR": u["UCR"], "inc_removed_over_M256": u["inc_over_M256"],
                            "fresh_over_M256": u["fresh_over_M256"],
                            "futile_fraction": P8.futile_fraction(prov),
                            "cy": cur.centroid_y, "cx": cur.centroid_x})
                row.update(P7.frame_metrics(st, prov, cs, L))
                if t % SHADOW_EVERY == 0 or t == HORIZON:
                    row.update(P8.shadow_readout(st, cs, prov.cells256))
            else:
                row.update({"track": False,
                            "UCR": P8.unique_causal_replacement(prov, set(), M256)["UCR"],
                            "inc_removed_over_M256": sum(prov.sink_by_cohort[k]
                                                         for k in P8.INCUMBENT) / M256,
                            "fresh_over_M256": 0.0,
                            "futile_fraction": P8.futile_fraction(prov)})
            tr_rows.append(row)
            max_id = max(max_id, prov.identity_residual(st))

    cur = largest_bounded(st)
    cs = cells_of(cur) if cur is not None else set()
    u = P8.unique_causal_replacement(prov, cs, M256)
    sh = P8.shadow_readout(st, cs, prov.cells256) if cur is not None else {}
    fm = st.m.reshape(-1)
    T = math.fsum(fm[i] for i in cs) if cs else None
    I = prov.incumbent_in(cs) if cs else 0.0
    row = {"arm": arm, "size": L, "block": blk, "M256": M256, "I0": I0, "quantum": qe,
           "floor": floor, "ceil": ceil,
           "n_scheduled": len(SCHED), "n_events": n_ev, "n_rejected": n_rej,
           "reject_causes": json.dumps(causes), "bound_by": json.dumps(bound),
           "attempted_mass": planned, "realized_sink": realized, "realized_source": injected,
           "DELIVERED_FRACTION": realized / planned if planned else 0.0,
           "UCR": u["UCR"], "incumbent_removed_unique": u["incumbent_removed_unique"],
           "incumbent_removed_over_M256": u["inc_over_M256"],
           "fresh_retained": u["fresh_retained"], "fresh_over_M256": u["fresh_over_M256"],
           "futile_fraction": P8.futile_fraction(prov),
           "replacement_per_1000_steps": 1000.0 * u["UCR"] * M256 / (HORIZON - T_B),
           "replacement_per_attempted": (u["UCR"] * M256 / planned) if planned else None,
           "replacement_per_delivered": (u["UCR"] * M256 / realized) if realized > 0 else None,
           "delivered_per_1000_steps": 1000.0 * realized / (HORIZON - T_B),
           "incumbent_displacement": (1.0 - I / I0) if I0 > 0 else None,
           "terminal_T": T, "terminal_I": I,
           "terminal_I_over_I0": (I / I0) if (I0 > 0 and cs) else None,
           "terminal_F_over_T": (u["fresh_retained"] / T) if (T and T > 0) else None,
           "same_track_continuous": lin.continuous, "loss": lin.lost, "merger": lin.merger,
           "split": lin.split, "reacquisition": lin.reacq,
           "first_failure_time": lin.first_failure_time,
           "first_failure_type": lin.first_failure_type, "n_gap_steps": n_gap,
           "max_identity_residual": max_id, "max_global_balance_residual": max_bal}
    row.update({f"CUM_{k}": v for k, v in cum.items()})
    row["CUM_ABS_SWEEP"] = cum_abs
    row.update({f"terminal_{k}": v for k, v in sh.items()})
    return row


def run():
    seal = preseal_guard()
    print(f"PRESEAL_GUARD OK  {seal}", flush=True)
    man = {b["block"]: b for b in json.loads((P7DIR / "p07a_manifest.json").read_text())["blocks"]}
    law = law_arms()["LAW_16"]
    rows, ev, tr = [], [], []
    calls = 0
    t0 = time.time()
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
            hb = fhash(st.m, st.n, st.b)
            if hb != info["t256_sha256"]:
                sys.exit(f"T256 HASH MISMATCH {blk}")
            c = largest_bounded(st)
            cells = cells_of(c)
            masks = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            for arm in ARMS:
                r = branch(law, st.copy(), masks, arm, L, cells, blk, ev, tr)
                calls += 1
                r.update(seed=seed, axis=AXORD[k % 4], t256_sha256=hb)
                rows.append(r)
                print(f"  {blk} {arm:<12} ({len(rows)}/{len(ARMS)*18}, "
                      f"{time.time()-t0:.0f}s)", flush=True)
    for name, data in (("p08b_rows.csv", rows), ("p08b_event_ledger.csv", ev),
                       ("p08b_trace.csv", tr)):
        f = sorted({kk for d in data for kk in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p08b_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n08B: {len(rows)} trajectoires, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

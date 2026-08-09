"""P09 -- dose-yoked closure of the guard-sign question.

Six arms. WHEN and WHERE are identical between the two replay arms; only the per-site
allocation rule differs. The requested-quantity sequence is exogenous, sealed, and comes from
a DIFFERENT block of a DIFFERENT seed cohort.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, "..")
sys.path.insert(0, "../P07")
sys.path.insert(0, "../P08")
from od_core import (LatticeBondEngine, LatticeBondState, comps, largest_bounded, cells_of,
                     fhash, MMAX, THRESH)
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
import p07_core as P7
import p08_core as P8

T_B, SPACING, COAST, N_OPP = 256, 16, 2048, 320
SEED_BASE, SEEDS_PER = 890000, 9
AXORD = ("+x", "-x", "+y", "-y")
CAD = 16
OPP = [272 + SPACING * (e - 1) for e in range(1, N_OPP + 1)]
HORIZON = OPP[-1] + COAST
CELLS = [("LAW_16", 24), ("LAW_16", 32), ("LAW_29", 24), ("LAW_29", 32)]
ARMS = ["SHAM", "PARENT_FULL", "FLOOR_FULL", "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY",
        "PARENT_LOW_CONSTANT"]
FLOOR_ARMS = {"FLOOR_FULL", "FLOOR_Q_REPLAY"}
PROTOCOL, SEAL = "p09_protocol.json", "p09_protocol.sha256"


def guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    if got != Path(SEAL).read_text().split()[0]:
        sys.exit("PRESEAL_GUARD: protocol hash mismatch")
    d = json.loads(Path(PROTOCOL).read_text())
    for f, h in d["code_sha256"].items():
        if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal")
    s = hashlib.sha256(Path("p09_sequences.json").read_bytes()).hexdigest()
    if s != d["exogenous_sequence"]["sha256"]:
        sys.exit("PRESEAL_GUARD: exogenous sequence changed after seal")
    return got


def prephase(law, m, L):
    eng = LatticeBondEngine(law)
    st = LatticeBondState(m.copy(), np.full((L, L), 0.8), np.zeros((2, L, L)), 0)
    while int(st.step) < T_B:
        st = eng.step(st).state
    return st


def build_requests(arm, seq, M256, M256_donor, qe):
    """Return {time: requested_mass}. Only WHEN and the requested amount differ across arms;
    the allocation rule is passed separately."""
    if arm == "SHAM":
        return {}
    if arm in ("PARENT_FULL", "FLOOR_FULL"):
        return {t: qe for t in OPP}
    scale = M256 / M256_donor
    if arm in ("PARENT_Q_REPLAY", "FLOOR_Q_REPLAY"):
        return {e["WHEN"]: e["SINK_REQUESTED"] * scale for e in seq["events"]
                if e["SINK_REQUESTED"] * scale > 1e-12}
    # PARENT_LOW_CONSTANT: same total, same number of non-zero events, evenly spaced
    nz = [e for e in seq["events"] if e["SINK_REQUESTED"] > 1e-12]
    total = sum(e["SINK_REQUESTED"] for e in nz) * scale
    n = len(nz)
    per = total / n
    idx = [round(i * (len(OPP) - 1) / (n - 1)) for i in range(n)] if n > 1 else [0]
    return {OPP[i]: per for i in sorted(set(idx))}


def branch(law, lawname, st0, masks, arm, L, cells256, blk, requests, ev_rows, tr_rows):
    floor = (THRESH + P8.EPS_FLOOR) if arm in FLOOR_ARMS else 0.0
    ceil = MMAX
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P7.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    lin = P7.Lineage()
    total0 = float(st.m.sum())
    attempted = realized_sink = realized_source = 0.0
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
        if t in requests:
            q = requests[t]
            attempted += q
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            if not track:
                n_rej += 1
                causes["NO_TRACK"] = causes.get("NO_TRACK", 0) + 1
            else:
                r = P8.exchange_event(st, prov, masks, track, L, q, floor, ceil)
                realized_sink += r["realized_sink"]
                realized_source += r["realized_source"]
                for k in P8.COHORTS:
                    removed[k] += r["removed_by_cohort"][k]
                if r["rejected"]:
                    n_rej += 1
                    causes[r["reject_reason"]] = causes.get(r["reject_reason"], 0) + 1
                else:
                    n_ev += 1
                    bound[r["bound_by"]] += 1
                max_id = max(max_id, prov.identity_residual(st))
                max_bal = max(max_bal, prov.global_balance_residual(st, total0))
                if n_ev + n_rej <= 4 or (n_ev + n_rej) % 16 == 1 or r["rejected"]:
                    ev_rows.append({"law": lawname, "block": blk, "size": L, "arm": arm,
                                    "time": t, "requested": q, "q_event": r["q_event"],
                                    "realized_sink": r["realized_sink"],
                                    "realized_source": r["realized_source"],
                                    "sink_capacity": r["sink_capacity"],
                                    "source_capacity": r["source_capacity"],
                                    "n_sink_sites": r["n_sink_sites"],
                                    "rejected": r["rejected"],
                                    "reject_reason": r["reject_reason"],
                                    "bound_by": r["bound_by"], "M256": M256})
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
            if t % 512 == 0 and cur is not None:
                cs = cells_of(cur)
                u = P8.unique_causal_replacement(prov, cs, M256)
                tr_rows.append({"law": lawname, "block": blk, "size": L, "arm": arm,
                                "time": t, "UCR": u["UCR"],
                                "inc_over_M256": u["inc_over_M256"],
                                "fresh_over_M256": u["fresh_over_M256"],
                                "T_over_M256": math.fsum(st.m.reshape(-1)[i] for i in cs) / M256,
                                "same_track": lin.continuous})
            max_id = max(max_id, prov.identity_residual(st))

    cur = largest_bounded(st)
    cs = cells_of(cur) if cur is not None else set()
    u = P8.unique_causal_replacement(prov, cs, M256)
    sh = P8.shadow_readout(st, cs, prov.cells256) if cur is not None else {}
    fm = st.m.reshape(-1)
    T = math.fsum(fm[i] for i in cs) if cs else None
    I = prov.incumbent_in(cs) if cs else 0.0
    fmet = P7.frame_metrics(st, prov, cs, L) if cs else {}
    row = {"law": lawname, "arm": arm, "size": L, "block": blk, "M256": M256, "I0": I0,
           "floor": floor, "ceil": ceil,
           "n_requests": len(requests), "n_events": n_ev, "n_rejected": n_rej,
           "reject_causes": json.dumps(causes), "bound_by": json.dumps(bound),
           "attempted_mass": attempted, "attempted_over_M256": attempted / M256,
           "realized_sink": realized_sink, "realized_source": realized_source,
           "delivered_over_M256": realized_sink / M256,
           "source_realized_over_M256": realized_source / M256,
           "DELIVERED_FRACTION": realized_sink / attempted if attempted else 0.0,
           "UCR": u["UCR"], "incumbent_removed_once": u["incumbent_removed_unique"],
           "incumbent_removed_over_M256": u["inc_over_M256"],
           "fresh_retained_at_T": u["fresh_retained"], "fresh_over_M256": u["fresh_over_M256"],
           "futile_fraction": P8.futile_fraction(prov),
           "UCR_per_1000_steps": 1000.0 * u["UCR"] * M256 / (HORIZON - T_B),
           "UCR_per_attempted": (u["UCR"] * M256 / attempted) if attempted else None,
           "UCR_per_delivered": (u["UCR"] * M256 / realized_sink) if realized_sink > 0 else None,
           "incumbent_displacement": (1.0 - I / I0) if I0 > 0 else None,
           "terminal_T": T, "terminal_T_over_M256": (T / M256) if T else None,
           "terminal_I_over_I0": (I / I0) if (I0 > 0 and cs) else None,
           "terminal_F_over_T": (u["fresh_retained"] / T) if (T and T > 0) else None,
           "SURVIVAL_ITT": lin.continuous, "SPLIT": lin.split, "DISSOLUTION": lin.lost,
           "merger": lin.merger, "reacquisition": lin.reacq,
           "first_failure_time": lin.first_failure_time,
           "first_failure_type": lin.first_failure_type, "n_gap_steps": n_gap,
           "max_identity_residual": max_id, "max_global_balance_residual": max_bal}
    row.update({f"CUM_{k}": v for k, v in cum.items()})
    row["CUM_ABS_SWEEP"] = cum_abs
    row.update({f"terminal_{k}": v for k, v in fmet.items()})
    row.update({f"terminal_{k}": v for k, v in sh.items()})
    return row


def run():
    seal = guard()
    print(f"PRESEAL_GUARD OK  {seal}", flush=True)
    seqs = json.loads(Path("p09_sequences.json").read_text())["sequences"]
    laws = law_arms()
    rows, ev, tr, man = [], [], [], []
    calls = 0
    t0 = time.time()
    for lawname, L in CELLS:
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
            donor_key = f"L{L}|donor_index_{(k + 1) % SEEDS_PER}"
            man.append({"block": blk, "law": lawname, "size": L, "seed": seed,
                        "t256_status": status, "donor": seqs[donor_key]["donor_block"]})
            if status != "T256_VALID_TRACK":
                continue
            cells = cells_of(c)
            masks = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            probe = P7.Prov(st, cells, L)
            man[-1].update(t256_sha256=fhash(st.m, st.n, st.b), area256=c.area,
                           M256=probe.M256)
            qe = probe.M256 / 80.0
            seq = seqs[donor_key]
            for arm in ARMS:
                req = build_requests(arm, seq, probe.M256, seq["M256_donor"], qe)
                r = branch(law, lawname, st.copy(), masks, arm, L, cells, blk, req, ev, tr)
                calls += 1
                r.update(seed=seed, axis=AXORD[k % 4], donor=seq["donor_block"])
                rows.append(r)
            print(f"  {blk} ({len(rows)}/{len(CELLS)*SEEDS_PER*len(ARMS)}, "
                  f"{time.time()-t0:.0f}s)", flush=True)
    Path("p09_manifest.json").write_text(json.dumps(
        {"program": "P09", "protocol_sha256": seal, "blocks": man,
         "engine_invocations": calls}, indent=1))
    for name, data in (("p09_rows.csv", rows), ("p09_event_ledger.csv", ev),
                       ("p09_trace.csv", tr)):
        f = sorted({kk for d in data for kk in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p09_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\nP09: {len(rows)} trajectoires, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

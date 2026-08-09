"""08C -- WHEN only. AMOUNT and WHERE are held fixed; the attempted mass is matched exactly.

The amount rule is read from p08b_selected.json, which is written by the sealed 08B decision
rule before this file is executed. The harness refuses to run without it.
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

T_B, SPACING, COAST, N_OPP = 256, 16, 2048, 320
SIZES, SEEDS_PER, SEED_BASE = (24, 32), 9, 990000
AXORD = ("+x", "-x", "+y", "-y")
CAD, SHADOW_EVERY = 16, 128
OPP = [272 + SPACING * (e - 1) for e in range(1, N_OPP + 1)]
HORIZON = OPP[-1] + COAST
KAPPA, REG_FLOOR, BACKLOG_CAP, LAG = 0.9, 0.10, 4.0, 16
ARMS = ["SAFE_ONLINE_TRIGGER", "SAFE_DONOR_YOKED_REPLAY", "SAFE_LAGGED_SENSOR"]
P7DIR = Path("../P07")
PROTOCOL, SEAL = "p08c_protocol.json", "p08c_protocol.sha256"


def preseal_guard():
    got = hashlib.sha256(Path(PROTOCOL).read_bytes()).hexdigest()
    if got != Path(SEAL).read_text().split()[0]:
        sys.exit("PRESEAL_GUARD: protocol hash mismatch")
    for f, h in json.loads(Path(PROTOCOL).read_text())["code_sha256"].items():
        if hashlib.sha256(Path(f).read_bytes()).hexdigest() != h:
            sys.exit(f"PRESEAL_GUARD: {f} changed after seal")
    sel = Path("p08b_selected.json")
    if not sel.exists():
        sys.exit("08B selection missing -- 08C is not authorised.")
    return got, json.loads(sel.read_text())


def branch(law, st0, masks, arm, L, cells256, blk, floor, ceil, donor_plan,
           ev_rows, tr_rows):
    eng = LatticeBondEngine(law)
    st = st0.copy()
    prov = P7.Prov(st, cells256, L)
    M256, I0 = prov.M256, prov.incumbent_in(cells256)
    qe = M256 / 80.0
    lin = P7.Lineage()
    total0 = float(st.m.sum())
    opp = {t: i for i, t in enumerate(OPP)}
    backlog = 0.0
    plan = []                       # (opportunity index, intended bite) actually fired
    attempted = realized = injected = 0.0
    removed = {c: 0.0 for c in P8.COHORTS}
    n_ev = n_rej = n_wait = 0
    bound = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
    causes = {}
    max_id = max_bal = 0.0
    sensor_hist = {}
    lin.update(st, T_B)

    t = int(st.step)
    while t < HORIZON:
        if t in opp:
            j = opp[t]
            backlog += qe
            attempted += qe
            c = largest_bounded(st)
            track = cells_of(c) if c is not None else set()
            intended = min(backlog, BACKLOG_CAP * qe)
            last = (j == len(OPP) - 1)
            if not track:
                n_rej += 1
                causes["NO_TRACK"] = causes.get("NO_TRACK", 0) + 1
            else:
                sen = P8.sensor_readout(st, masks, track, L, floor, ceil)
                sensor_hist[t] = sen
                if arm == "SAFE_ONLINE_TRIGGER":
                    s = sen
                    fire = (s["feasible_q"] >= KAPPA * intended
                            and s["mask_registration"] >= REG_FLOOR) or last
                elif arm == "SAFE_LAGGED_SENSOR":
                    s = sensor_hist.get(t - LAG, sen)
                    fire = (s["feasible_q"] >= KAPPA * intended
                            and s["mask_registration"] >= REG_FLOOR) or last
                else:                                        # donor-yoked open-loop replay
                    fire = j in donor_plan
                    if fire:
                        intended = min(donor_plan[j], BACKLOG_CAP * qe)
                if not fire:
                    n_wait += 1
                else:
                    r = P8.exchange_event(st, prov, masks, track, L, intended, floor, ceil)
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
                        plan.append((j, intended))
                    backlog = max(0.0, backlog - intended)
                    ident = prov.identity_residual(st)
                    bal = prov.global_balance_residual(st, total0)
                    max_id, max_bal = max(max_id, ident), max(max_bal, bal)
                    ev_rows.append({"block": blk, "size": L, "arm": arm, "time": t,
                                    "opportunity": j, "intended": intended,
                                    "q_event": r["q_event"],
                                    "realized_sink": r["realized_sink"],
                                    "sink_capacity": r["sink_capacity"],
                                    "source_capacity": r["source_capacity"],
                                    "mask_registration": sen["mask_registration"],
                                    "feasible_q": sen["feasible_q"],
                                    "incumbent_removed": sum(r["removed_by_cohort"][k]
                                                             for k in P8.INCUMBENT),
                                    "fresh_removed": r["removed_by_cohort"]["fre"],
                                    "rejected": r["rejected"],
                                    "reject_reason": r["reject_reason"],
                                    "bound_by": r["bound_by"], "M256": M256})
        pre = st
        o = eng.step(pre)
        prov.advance(pre.m, o.ledger, o.state.m, law.dt)
        st = o.state
        t = int(st.step)
        if t % CAD == 0:
            cur = lin.update(st, t)
            row = {"block": blk, "size": L, "arm": arm, "time": t, "M256": M256, "I0": I0,
                   "same_track": lin.continuous}
            if cur is not None:
                cs = cells_of(cur)
                fm = st.m.reshape(-1)
                T = math.fsum(fm[i] for i in cs)
                I = prov.incumbent_in(cs)
                u = P8.unique_causal_replacement(prov, cs, M256)
                row.update({"track": True, "T": T, "I": I,
                            "I_over_I0": I / I0 if I0 > 0 else None,
                            "UCR": u["UCR"], "inc_removed_over_M256": u["inc_over_M256"],
                            "fresh_over_M256": u["fresh_over_M256"],
                            "futile_fraction": P8.futile_fraction(prov)})
                if t % SHADOW_EVERY == 0:
                    row.update(P8.shadow_readout(st, cs, prov.cells256))
            else:
                row.update({"track": False,
                            "UCR": P8.unique_causal_replacement(prov, set(), M256)["UCR"],
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
           "floor": floor, "ceil": ceil, "n_opportunities": len(OPP),
           "n_events": n_ev, "n_waited": n_wait, "n_rejected": n_rej,
           "reject_causes": json.dumps(causes), "bound_by": json.dumps(bound),
           "attempted_mass": attempted, "realized_sink": realized,
           "DELIVERED_FRACTION": realized / attempted if attempted else 0.0,
           "UCR": u["UCR"], "incumbent_removed_unique": u["incumbent_removed_unique"],
           "incumbent_removed_over_M256": u["inc_over_M256"],
           "fresh_retained": u["fresh_retained"], "fresh_over_M256": u["fresh_over_M256"],
           "futile_fraction": P8.futile_fraction(prov),
           "replacement_per_1000_steps": 1000.0 * u["UCR"] * M256 / (HORIZON - T_B),
           "replacement_per_attempted": (u["UCR"] * M256 / attempted) if attempted else None,
           "replacement_per_delivered": (u["UCR"] * M256 / realized) if realized > 0 else None,
           "delivered_per_1000_steps": 1000.0 * realized / (HORIZON - T_B),
           "incumbent_displacement": (1.0 - I / I0) if I0 > 0 else None,
           "terminal_T": T, "terminal_I_over_I0": (I / I0) if (I0 > 0 and cs) else None,
           "terminal_F_over_T": (u["fresh_retained"] / T) if (T and T > 0) else None,
           "same_track_continuous": lin.continuous, "loss": lin.lost,
           "first_failure_time": lin.first_failure_time,
           "first_failure_type": lin.first_failure_type,
           "max_identity_residual": max_id, "max_global_balance_residual": max_bal,
           "fire_plan": json.dumps(plan)}
    row.update({f"terminal_{k}": v for k, v in sh.items()})
    return row


def run():
    seal, sel = preseal_guard()
    floor, ceil = sel["floor"], sel["ceil"]
    print(f"PRESEAL_GUARD OK  {seal}\nAMOUNT rule from sealed 08B rule: "
          f"{sel['arm']} floor={floor} ceil={ceil}", flush=True)
    man = {b["block"]: b for b in json.loads((P7DIR / "p07a_manifest.json").read_text())["blocks"]}
    law = law_arms()["LAW_16"]
    rows, ev, tr = [], [], []
    calls = 0
    t0 = time.time()
    blocks = []
    for li, L in enumerate(SIZES):
        for k in range(SEEDS_PER):
            seed = SEED_BASE + li * 100 + k
            blk = f"L{L}_S{seed}"
            info = man.get(blk)
            if info and info.get("t256_status") == "T256_VALID_TRACK":
                blocks.append((li, L, k, seed, blk, info))
    plans = {}
    for arm in ARMS:
        for li, L, k, seed, blk, info in blocks:
            if arm == "SAFE_DONOR_YOKED_REPLAY":
                donor = f"L{L}_S{SEED_BASE + li * 100 + (k + 1) % SEEDS_PER}"
                dp = plans.get(("SAFE_ONLINE_TRIGGER", donor))
                if dp is None:
                    sys.exit("donor plan missing -- ONLINE must run first")
                donor_plan = {j: v for j, v in dp}
            else:
                donor_plan = {}
            a = np.load(P7DIR / f"_t256_{blk}.npy")
            b = np.load(P7DIR / f"_t256b_{blk}.npy")
            st = LatticeBondState(np.ascontiguousarray(a[0]), np.ascontiguousarray(a[1]),
                                  np.ascontiguousarray(b), T_B)
            if fhash(st.m, st.n, st.b) != info["t256_sha256"]:
                sys.exit(f"T256 HASH MISMATCH {blk}")
            c = largest_bounded(st)
            cells = cells_of(c)
            masks = P7.build_masks(cells, L, c.centroid_y, c.centroid_x, AXORD[k % 4])
            r = branch(law, st.copy(), masks, arm, L, cells, blk, floor, ceil, donor_plan,
                       ev, tr)
            calls += 1
            r.update(seed=seed, axis=AXORD[k % 4])
            rows.append(r)
            plans[(arm, blk)] = json.loads(r["fire_plan"])
            print(f"  {blk} {arm:<24} ({len(rows)}/{len(ARMS)*len(blocks)}, "
                  f"{time.time()-t0:.0f}s)", flush=True)
    for name, data in (("p08c_rows.csv", rows), ("p08c_event_ledger.csv", ev),
                       ("p08c_trace.csv", tr)):
        f = sorted({kk for d in data for kk in d})
        with Path(name).open("w", newline="") as h:
            w = csv.DictWriter(h, fieldnames=f)
            w.writeheader()
            w.writerows(data)
    Path("_p08c_calls.json").write_text(json.dumps({"engine_invocations": calls}))
    print(f"\n08C: {len(rows)} trajectoires, {calls} appels moteur ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    run()

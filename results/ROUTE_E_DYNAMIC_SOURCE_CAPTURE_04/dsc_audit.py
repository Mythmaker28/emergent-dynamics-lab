"""ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04 -- section 3: MECHANICAL AUDIT of the source filter.

Replays the PARENT operator decisions (REDESIGN_02, arms COUPLED_D1_SMOOTH_LOW and
COUPLED_D2_SMOOTH_LOW) with an instrumented source loop. No new physics: the law, seeds,
schedule, doses, masks and axis order are exactly the parent's, so these are reproductions of
already-executed parent trajectories, counted separately from mission engine calls.

Produces source_filter_audit.json.
"""
from __future__ import annotations
import json, math, time
from pathlib import Path
import numpy as np

from od_core import *
from od_ops import do_event
from bridge00_harness import law_arms
from morph02_ic import ic_single_disc
from rc_harness import build_masks2, prephase, SMOOTH, AXORD, T_B, T_E, P, SIZES, SEEDS_PER

# ---------------------------------------------------------------- taxonomy
P2PRIME_EPS = 1e-9

REASONS = ("REJECT_OUTSIDE_MASK", "REJECT_OCCUPIED", "REJECT_CAPACITY",
           "REJECT_INSIDE_TRACK", "REJECT_TRACK_ADJACENCY",
           "REJECT_SOURCE_SOURCE_ADJACENCY", "REJECT_OTHER_COMPONENT_ADJACENCY",
           "REJECT_MERGE_RISK", "REJECT_QUOTA", "REJECT_OTHER", "ACCEPTED")

# The audited predicate chain, in the exact order od_ops.do_event applies it.
# P0 mask membership (build_masks: gd==k and proj<0)  -> REJECT_OUTSIDE_MASK
# P1 if fm[s] >= THRESH: continue                     -> REJECT_OCCUPIED
# P2 if any(n in track for n in nbrs(s,L)): continue   -> REJECT_TRACK_ADJACENCY
# P3 cap = MMAX - fm[s]; if cap <= 1e-12: continue     -> REJECT_CAPACITY
# budget exhausted before reaching s                   -> REJECT_QUOTA


def audit_source_event(fm, track, mask, want, L):
    """Replay the source loop of od_ops.do_event, classifying EVERY mask site.

    Returns (delivered, per-reason count/mass dict, counterfactual deliveries).
    Mutation semantics identical to the production operator; nothing is written here.
    """
    counts = {r: 0 for r in REASONS}
    mass = {r: 0.0 for r in REASONS}
    b = want
    delivered = 0.0
    stopped = False
    for s in mask:
        capacity_here = max(0.0, MMAX - fm[s])
        if b <= 1e-12:
            stopped = True
            counts["REJECT_QUOTA"] += 1
            mass["REJECT_QUOTA"] += capacity_here
            continue
        if s in track:                                    # cannot happen for gd>=1, checked
            counts["REJECT_INSIDE_TRACK"] += 1; mass["REJECT_INSIDE_TRACK"] += capacity_here; continue
        if fm[s] >= THRESH:                               # P1
            counts["REJECT_OCCUPIED"] += 1; mass["REJECT_OCCUPIED"] += capacity_here; continue
        if any(n in track for n in nbrs(s, L)):           # P2
            counts["REJECT_TRACK_ADJACENCY"] += 1; mass["REJECT_TRACK_ADJACENCY"] += capacity_here; continue
        if capacity_here <= 1e-12:                        # P3
            counts["REJECT_CAPACITY"] += 1; mass["REJECT_CAPACITY"] += capacity_here; continue
        add = min(b, capacity_here)
        counts["ACCEPTED"] += 1; mass["ACCEPTED"] += add
        delivered += add; b -= add
    # ---- P2' : the SMALLEST safe relaxation -------------------------------
    # A track-adjacent site may receive matter, but only up to a value that keeps it
    # STRICTLY sub-threshold, so it stays detector-empty and the operator never creates
    # a supra-threshold bridge to the component. Non-adjacent sites keep the legacy cap.
    cf = {}
    bb = want; d2p = 0.0; head = 0.0
    for s in mask:
        if s in track:
            continue
        adj = any(n in track for n in nbrs(s, L))
        cap = (max(0.0, THRESH - fm[s] - P2PRIME_EPS) if adj else max(0.0, MMAX - fm[s]))
        head += cap
        if bb <= 1e-12 or cap <= 1e-12:
            continue
        add = min(bb, cap); d2p += add; bb -= add
    cf["P2PRIME_SAFE_RELAXATION"] = d2p
    cf["P2PRIME_CAPACITY_THIS_EVENT"] = head

    # ---- counterfactuals: drop ONE predicate, keep the others, same order ----
    for drop in ("P1_OCCUPIED", "P2_TRACK_ADJACENCY", "P3_CAPACITY", "NONE"):
        bb = want; d = 0.0
        for s in mask:
            if bb <= 1e-12: break
            if s in track: continue
            if drop != "P1_OCCUPIED" and fm[s] >= THRESH: continue
            if drop != "P2_TRACK_ADJACENCY" and any(n in track for n in nbrs(s, L)): continue
            cap = max(0.0, MMAX - fm[s])
            if drop != "P3_CAPACITY" and cap <= 1e-12: continue
            if cap <= 1e-12: continue          # never inject into a physically full site
            add = min(bb, cap); d += add; bb -= add
        cf[drop] = d
    # total physical headroom of the mask, ignoring every eligibility predicate
    cf["GEOMETRIC_HEADROOM"] = float(sum(max(0.0, MMAX - fm[s]) for s in mask if s not in track))
    cf["SUBTHRESHOLD_HEADROOM"] = float(sum(max(0.0, MMAX - fm[s]) for s in mask
                                            if s not in track and fm[s] < THRESH))
    return delivered, counts, mass, cf, stopped


def replay(law, arm_key, src_key, dose_frac, seeds_sizes, log):
    """Reproduce parent trajectories with the source loop instrumented."""
    out = []
    S = set(SMOOTH)
    for (L, k) in seeds_sizes:
        seed = 960000 + (0 if L == 24 else 100) + k
        m = np.ascontiguousarray(ic_single_disc(np.random.default_rng(seed), L, P), dtype=np.float64)
        st = prephase(law, m, L)
        c = largest_bounded(st)
        if c is None or c.wraps_x or c.wraps_y:
            continue
        cs = cells_of(c)
        M256 = float(sum(st.m.reshape(-1)[i] for i in cs))
        axis = AXORD[k % 4]
        masks = build_masks2(cs, L, c.centroid_y, c.centroid_x, axis)
        mask = masks[src_key]
        eng = LatticeBondEngine(law)
        init = np.zeros_like(st.m); fi = init.reshape(-1); fmm = st.m.reshape(-1)
        for i in cs: fi[i] = fmm[i]
        fresh = np.zeros_like(st.m)
        Q = dose_frac * M256; qe = Q / len(SMOOTH)
        res = {"sink": 0.0, "source": 0.0}
        tot = {r: 0 for r in REASONS}; tmass = {r: 0.0 for r in REASONS}
        tcf = {}
        delivered_total = 0.0; removed_total = 0.0; want_total = 0.0
        mask_size_t0 = len(mask)
        t = int(st.step)
        while t < T_E:
            if t in S:
                pt = per_track(st, init, fresh, M256)
                track = pt["cells"]
                fm = st.m.reshape(-1)
                # sink first (the production operator does sink then source, COUPLED want=removed)
                r = do_event(st, init, fresh, track, {**masks, "source_near": []},
                             "COUPLED_NEAR_SMOOTH_LOW", qe, L, res)
                removed = r["removed"]; removed_total += removed; want_total += removed
                # now audit the source side against the post-sink field
                fm = st.m.reshape(-1)
                d, cnt, msz, cf, _ = audit_source_event(fm, track, mask, removed, L)
                for kk in REASONS:
                    tot[kk] += cnt[kk]; tmass[kk] += msz[kk]
                for kk, vv in cf.items():
                    tcf[kk] = tcf.get(kk, 0.0) + vv
                # apply the REAL production source loop so the trajectory stays faithful
                b = removed
                for s in mask:
                    if b <= 1e-12: break
                    if fm[s] >= THRESH: continue
                    if any(n in track for n in nbrs(s, L)): continue
                    cap = MMAX - fm[s]
                    if cap <= 1e-12: continue
                    add = min(b, cap); fm[s] += add; fresh.reshape(-1)[s] += add
                    delivered_total += add; b -= add
                res["source"] -= d
            pre = st; o = eng.step(pre)
            init = advect(init, pre.m, o.ledger, o.state.m, law.dt)
            fresh = advect(fresh, pre.m, o.ledger, o.state.m, law.dt)
            st = o.state; t = int(st.step)
        out.append({"L": L, "seed": seed, "axis": axis, "M256": M256,
                    "mask_size_t0": mask_size_t0,
                    "planned_dose": Q, "want_total": want_total,
                    "realized_sink_removal": removed_total,
                    "realized_source_injection": delivered_total,
                    "delivery_ratio": delivered_total / want_total if want_total else float("nan"),
                    "reject_counts": tot, "reject_mass": tmass, "counterfactual": tcf})
        log(f"    {arm_key} L={L} seed={seed}: inj={delivered_total:.3f} / want={want_total:.3f}"
            f"  ({delivered_total/want_total*100 if want_total else 0:.1f}%)")
    return out


def main():
    t0 = time.time()
    law = law_arms()["LAW_16"]
    lines = []
    def log(s):
        print(s, flush=True); lines.append(s)

    seeds_sizes = [(L, k) for L in SIZES for k in range(SEEDS_PER)]
    log("=== AUDIT MECANIQUE DU FILTRE SOURCE (reproduction du parent REDESIGN_02) ===")
    log("  arme D2 = source_near (gd==2, proj<0), filtre legacy, dose 0.05 x M256, smooth 80")
    d2 = replay(law, "COUPLED_D2_SMOOTH_LOW", "source_near", 0.05, seeds_sizes, log)
    log("  arme D1 = source_d1 (gd==1, proj<0), filtre legacy, dose 0.05 x M256, smooth 80")
    d1 = replay(law, "COUPLED_D1_SMOOTH_LOW", "source_d1", 0.05, seeds_sizes, log)

    def agg(rows):
        a = {"n": len(rows), "reject_counts": {r: 0 for r in REASONS},
             "reject_mass": {r: 0.0 for r in REASONS}, "counterfactual": {}}
        for r in rows:
            for k in REASONS:
                a["reject_counts"][k] += r["reject_counts"][k]
                a["reject_mass"][k] += r["reject_mass"][k]
            for k, v in r["counterfactual"].items():
                a["counterfactual"][k] = a["counterfactual"].get(k, 0.0) + v
        a["want_total"] = sum(r["want_total"] for r in rows)
        a["realized"] = sum(r["realized_source_injection"] for r in rows)
        a["delivery_ratio"] = a["realized"] / a["want_total"] if a["want_total"] else float("nan")
        a["mask_size_t0_median"] = sorted(r["mask_size_t0"] for r in rows)[len(rows) // 2] if rows else 0
        return a

    audit = {
        "mission": "ROUTE_E_DYNAMIC_SOURCE_CAPTURE_DEV_04",
        "section": "3_MECHANICAL_SOURCE_FILTER_AUDIT",
        "code_path": {
            "file": "od_ops.py",
            "function": "do_event",
            "source_block": "the `if do_src:` block",
            "predicate_order": [
                "P0 mask membership, od_core.build_masks / rc_harness.build_masks2: "
                "source_near = {i : graph_distance(C256)[i] == 2 and proj[i] < 0}; "
                "source_d1 = {i : graph_distance(C256)[i] == 1 and proj[i] < 0}",
                "P1 `if fm[s] >= THRESH: continue`  (THRESH = 0.45)",
                "P2 `if any(n in track for n in nbrs(s,L)): continue`  (track = cells of C_t, CURRENT)",
                "P3 `cap = MMAX - fm[s]; if cap <= 1e-12: continue`",
                "quota `if b <= 1e-12: break`",
            ],
            "note": "`track` is the CURRENT component C_t, but the mask is frozen at t256 from C256. "
                    "P2 is therefore time-varying even though the mask is not.",
        },
        "arms": {"COUPLED_D2_SMOOTH_LOW_gd2": agg(d2), "COUPLED_D1_SMOOTH_LOW_gd1": agg(d1)},
        "per_trajectory": {"gd2": d2, "gd1": d1},
        "reproduction_engine_calls": len(d2) + len(d1),
        "reproduction_engine_calls_are_mission_output": False,
        "wall_clock_s": round(time.time() - t0, 1),
    }
    Path("source_filter_audit.json").write_text(json.dumps(audit, indent=1))
    log(f"\n-> source_filter_audit.json  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()

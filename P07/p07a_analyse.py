"""07A analysis. Written and hashed BEFORE any 07A result was read.

Answers, or declares unanswerable, the four sealed questions:
  Q1 de-registration vs depletion       Q2 actuator vs dynamics
  Q3 tracker sweep vs material change   Q4 recovery time constant with uncertainty
"""
from __future__ import annotations
import csv, json, math, statistics as S
from pathlib import Path

OUT = {}
DEV05 = Path("../DR05")


def num(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def rd(p):
    return list(csv.DictReader(open(p)))


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def boot_ci(xs, f=S.median, n=4000, seed=20260809):
    """Block-level bootstrap. Blocks are the independent units."""
    xs = [x for x in xs if x is not None]
    if len(xs) < 3:
        return (None, None)
    rng = __import__("random").Random(seed)
    out = []
    for _ in range(n):
        out.append(f([xs[rng.randrange(len(xs))] for _ in xs]))
    out.sort()
    return (out[int(0.025 * n)], out[int(0.975 * n)])


def sign_test(pairs):
    """Exact two-sided sign test on paired block differences."""
    d = [b - a for a, b in pairs if a is not None and b is not None]
    pos = sum(1 for x in d if x > 0)
    neg = sum(1 for x in d if x < 0)
    n = pos + neg
    if n == 0:
        return {"n": 0, "pos": 0, "neg": 0, "p": None}
    from math import comb
    k = min(pos, neg)
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)
    return {"n": n, "pos": pos, "neg": neg, "p": p, "median_diff": med(d)}


# ============================================================ 0. reproduction
def reproduction():
    """07A must reproduce DEV_05 exactly: same operator, same seeds, same schedule."""
    new = {(r["block"], r["arm"]): r for r in rd("p07a_rows.csv")}
    old = {}
    for f in ("direct_replacement_rows_a.csv", "direct_replacement_rows_b.csv"):
        p = DEV05 / f
        if p.exists():
            for r in rd(p):
                old[(r["block"], r["arm"])] = r
    pairs = [("PARENT_Q400_UNIFORM", "DIRECT_Q400_UNIFORM"),
             ("PARENT_Q800_UNIFORM", "DIRECT_Q800_UNIFORM")]
    worst = {}
    for na, oa in pairs:
        w = 0.0
        n = 0
        miss = 0
        for (blk, arm), r in new.items():
            if arm != na:
                continue
            o = old.get((blk, oa))
            if o is None:
                miss += 1
                continue
            for key in ("realized_sink", "realized_source", "n_events", "n_rejected", "M256"):
                a, b = num(r.get(key)), num(o.get(key))
                if a is None or b is None:
                    continue
                w = max(w, abs(a - b) / max(1.0, abs(b)))
            n += 1
        worst[na] = {"n_blocks_compared": n, "n_missing_parent": miss,
                     "worst_relative_deviation": w}
    OUT["REPRODUCTION_OF_DEV05"] = worst
    OUT["REPRODUCTION_VERDICT"] = (
        "EXACT" if all(v["worst_relative_deviation"] <= 1e-9 for v in worst.values()
                       if v["n_blocks_compared"]) else "DEVIATION_PRESENT")


# ====================================================== Q1 de-reg vs depletion
def q1():
    ev = [r for r in rd("p07a_event_ledger.csv") if r.get("CAP_PARENT")]
    res = {}
    for arm in ("PARENT_Q400_UNIFORM", "PARENT_Q800_UNIFORM", "SHAM"):
        for L in ("24", "32"):
            g = [r for r in ev if r["arm"] == arm and r["size"] == L]
            if not g:
                continue
            rej = [r for r in g if r["rejected"] == "True"]
            key = f"{arm}|L{L}"
            res[key] = {
                "n_events_with_track": len(g),
                "n_rejected": len(rej),
                "rejection_rate": len(rej) / len(g) if g else None,
                "median_MASK_REGISTRATION": med([num(r["MASK_REGISTRATION"]) for r in g]),
                "median_CAP_PARENT": med([num(r["CAP_PARENT"]) for r in g]),
                "median_CAP_TRACKALL": med([num(r["CAP_TRACKALL"]) for r in g]),
                "median_NEL_PARENT": med([num(r["NEL_PARENT"]) for r in g]),
                "median_SHORTFALL_DEREGISTRATION":
                    med([num(r["SHORTFALL_DEREGISTRATION"]) for r in g]),
                "median_SHORTFALL_SUBTHRESHOLD":
                    med([num(r["SHORTFALL_SUBTHRESHOLD"]) for r in g]),
                "median_HEADROOM_COMOVING": med([num(r["HEADROOM_COMOVING"]) for r in g]),
                "median_HEADROOM_TRACKALL": med([num(r["HEADROOM_TRACKALL"]) for r in g]),
            }
            if rej:
                res[key]["AT_REJECTION"] = {
                    "median_MASK_REGISTRATION": med([num(r["MASK_REGISTRATION"]) for r in rej]),
                    "median_CAP_TRACKALL": med([num(r["CAP_TRACKALL"]) for r in rej]),
                    "median_CAP_COMOVING": med([num(r["CAP_COMOVING"]) for r in rej]),
                    "median_CAP_FROZEN_ANY": med([num(r["CAP_FROZEN_ANY"]) for r in rej]),
                    "frac_rejections_with_TRACKALL_capacity":
                        sum(1 for r in rej if (num(r["CAP_TRACKALL"]) or 0) > 1e-9) / len(rej),
                    "frac_rejections_with_FROZEN_ANY_capacity":
                        sum(1 for r in rej if (num(r["CAP_FROZEN_ANY"]) or 0) > 1e-9) / len(rej),
                    "causes": {c: sum(1 for r in rej if r["reject_reason"] == c)
                               for c in sorted({r["reject_reason"] for r in rej})}}
    OUT["Q1_CAPACITY_SPECTRUM"] = res


# ==================================================== Q2 actuator vs dynamics
def q2():
    ev = rd("p07a_event_ledger.csv")
    by = {}
    for r in ev:
        c = num(r.get("CAP_PARENT"))
        if c is None:
            continue
        by.setdefault((r["block"], r["arm"]), {})[int(r["time"])] = {
            "cap": c, "reg": num(r.get("MASK_REGISTRATION")),
            "trackall": num(r.get("CAP_TRACKALL"))}
    out = {}
    for arm in ("PARENT_Q400_UNIFORM", "PARENT_Q800_UNIFORM"):
        for L in ("24", "32"):
            pr_cap, pr_reg, pr_ta = [], [], []
            blocks = sorted({b for (b, a) in by if a == arm and b.startswith(f"L{L}_")})
            for b in blocks:
                f = by.get((b, arm), {})
                s = by.get((b, "SHAM"), {})
                common = sorted(set(f) & set(s))
                if len(common) < 10:
                    continue
                # ratio of medians over the matched times, one number per BLOCK
                pr_cap.append((med([s[t]["cap"] for t in common]),
                               med([f[t]["cap"] for t in common])))
                pr_reg.append((med([s[t]["reg"] for t in common]),
                               med([f[t]["reg"] for t in common])))
                pr_ta.append((med([s[t]["trackall"] for t in common]),
                              med([f[t]["trackall"] for t in common])))
            k = f"{arm}|L{L}"
            out[k] = {
                "n_blocks": len(pr_cap),
                "CAP_PARENT_sham_median": med([a for a, _ in pr_cap]),
                "CAP_PARENT_forced_median": med([b for _, b in pr_cap]),
                "CAP_PARENT_sign_test": sign_test(pr_cap),
                "MASK_REGISTRATION_sham_median": med([a for a, _ in pr_reg]),
                "MASK_REGISTRATION_forced_median": med([b for _, b in pr_reg]),
                "MASK_REGISTRATION_sign_test": sign_test(pr_reg),
                "CAP_TRACKALL_sham_median": med([a for a, _ in pr_ta]),
                "CAP_TRACKALL_forced_median": med([b for _, b in pr_ta]),
                "CAP_TRACKALL_sign_test": sign_test(pr_ta)}
    OUT["Q2_ACTUATOR_VS_DYNAMICS"] = out


# ================================================= Q3 tracker sweep vs matter
def q3():
    rows = rd("p07a_rows.csv")
    out = {}
    ident = []
    for r in rows:
        T0, Tt = num(r.get("T_at_t256")), num(r.get("terminal_T"))
        cm, ce, cx = (num(r.get("CUM_MATERIAL_CHANGE_ON_RETAINED_SITES")),
                      num(r.get("CUM_MASK_ENTRY")), num(r.get("CUM_MASK_EXIT")))
        gap = num(r.get("n_gap_steps")) or 0
        if None not in (T0, Tt, cm, ce, cx):
            ident.append({"block": r["block"], "arm": r["arm"], "gap": gap,
                          "residual": (Tt - T0) - (cm + ce + cx)})
    gapless = [x["residual"] for x in ident if x["gap"] == 0]
    OUT["Q3_SWEEP_IDENTITY"] = {
        "n_trajectories": len(ident),
        "n_gapless": len(gapless),
        "worst_residual_gapless": max((abs(x) for x in gapless), default=None),
        "n_with_gaps": sum(1 for x in ident if x["gap"] > 0),
        "note": "the identity is exact only on gap-free trajectories; steps during which no "
                "bounded component existed are excluded from the cumulative sums by "
                "construction and are counted, never silently dropped"}
    for arm in ("SHAM", "PARENT_Q400_UNIFORM", "PARENT_Q800_UNIFORM"):
        for L in ("24", "32"):
            g = [r for r in rows if r["arm"] == arm and r["size"] == L]
            if not g:
                continue
            M = [num(r["M256"]) for r in g]
            def per(k):
                return [(num(r.get(k)) / num(r["M256"])) if num(r.get(k)) is not None else None
                        for r in g]
            sw = per("CUM_TRACKER_SWEEP")
            mc = per("CUM_MATERIAL_CHANGE_ON_RETAINED_SITES")
            ab = per("CUM_ABS_SWEEP")
            out[f"{arm}|L{L}"] = {
                "n_blocks": len(g),
                "median_CUM_TRACKER_SWEEP_over_M256": med(sw),
                "ci_CUM_TRACKER_SWEEP": boot_ci(sw),
                "median_CUM_MATERIAL_over_M256": med(mc),
                "ci_CUM_MATERIAL": boot_ci(mc),
                "median_CUM_ABS_SWEEP_over_M256": med(ab),
                "median_terminal_mass_in_frozen_C256_over_M256":
                    med([(num(r.get("terminal_mass_in_frozen_C256")) or 0) / num(r["M256"])
                         for r in g if num(r.get("terminal_mass_in_frozen_C256")) is not None]),
                "median_terminal_incumbent_in_frozen_C256_over_M256":
                    med([(num(r.get("terminal_incumbent_in_frozen_C256")) or 0) / num(r["M256"])
                         for r in g
                         if num(r.get("terminal_incumbent_in_frozen_C256")) is not None]),
                "median_terminal_fresh_in_frozen_C256_over_M256":
                    med([(num(r.get("terminal_fresh_in_frozen_C256")) or 0) / num(r["M256"])
                         for r in g if num(r.get("terminal_fresh_in_frozen_C256")) is not None]),
                "median_terminal_jaccard_C256_Ct":
                    med([num(r.get("terminal_jaccard_C256_Ct")) for r in g]),
                "median_terminal_boundary_site_turnover":
                    med([num(r.get("terminal_boundary_site_turnover")) for r in g]),
                "n_terminal_track_lost": sum(1 for r in g if num(r.get("terminal_T")) is None),
                "n_scheduled_blocks_ITT": len(g)}
    OUT["Q3_SWEEP_VS_MATERIAL"] = out


# ============================================== Q4 impulse response, tau50/90
def q4():
    p = Path("p07a_impulse_capacity.csv")
    if not p.exists():
        OUT["Q4_IMPULSE"] = "NOT_RUN"
        return
    cap = [r for r in rd(p) if r.get("kind") == "CAP"]
    by = {}
    for r in cap:
        v = num(r.get("CAP_PARENT"))
        by.setdefault((r["block"], r["size"], r["cond"]), {})[int(r["step"])] = v
    res = {}
    for L in ("24", "32"):
        for cond in ("A1", "A2", "A4"):
            t50, t90, amp0 = [], [], []
            blocks = sorted({b for (b, s, c) in by if s == L and c == cond})
            for b in blocks:
                f = by.get((b, L, cond), {})
                c0 = by.get((b, L, "CTRL"), {})
                steps = sorted(set(f) & set(c0))
                d = {s: (f[s] - c0[s]) for s in steps
                     if f[s] is not None and c0[s] is not None}
                if 0 not in d or abs(d[0]) < 1e-9:
                    continue
                a0 = abs(d[0])
                amp0.append(a0)
                s50 = next((s for s in sorted(d) if s > 0 and abs(d[s]) <= 0.5 * a0), None)
                s90 = next((s for s in sorted(d) if s > 0 and abs(d[s]) <= 0.1 * a0), None)
                t50.append(s50)
                t90.append(s90)
            n = len(amp0)
            cens50 = sum(1 for x in t50 if x is None)
            cens90 = sum(1 for x in t90 if x is None)
            res[f"L{L}|{cond}"] = {
                "n_blocks": n, "median_initial_deficit": med(amp0),
                "tau50_median_steps": med(t50), "tau50_ci": boot_ci([x for x in t50 if x]),
                "tau50_censored_blocks": cens50,
                "tau90_median_steps": med(t90), "tau90_ci": boot_ci([x for x in t90 if x]),
                "tau90_censored_blocks": cens90,
                "censoring_note": f"a censored block never returned inside the band within "
                                  f"128 steps; medians are computed on uncensored blocks only "
                                  f"and the censored count is reported, never hidden"}
    OUT["Q4_IMPULSE_CAPACITY_RELAXATION"] = res

    pb = Path("p07a_impulse_probe.csv")
    if pb.exists():
        rows = rd(pb)
        by2 = {}
        for r in rows:
            by2.setdefault((r["block"], r["size"], r["first_probe"] == "True"),
                           {})[int(r["delay"])] = num(r["second_realized"])
        out2 = {}
        for L in ("24", "32"):
            blocks = sorted({b for (b, s, f) in by2 if s == L})
            for d in (1, 2, 4, 8, 16, 32, 64):
                ratios, ps, ns = [], [], []
                for b in blocks:
                    p1 = by2.get((b, L, True), {}).get(d)
                    p0 = by2.get((b, L, False), {}).get(d)
                    if p1 is None or p0 is None or p0 <= 1e-12:
                        continue
                    ratios.append(p1 / p0)
                    ps.append(p1)
                    ns.append(p0)
                out2[f"L{L}|d{d}"] = {
                    "n_blocks": len(ratios), "median_recovery_ratio": med(ratios),
                    "ci": boot_ci(ratios),
                    "median_bite_after_first_probe": med(ps),
                    "median_bite_no_first_probe": med(ns)}
        OUT["Q4_IMPULSE_SECOND_PROBE_RECOVERY"] = out2


def main():
    reproduction()
    q1()
    q2()
    q3()
    q4()
    Path("p07a_summary.json").write_text(json.dumps(OUT, indent=1, default=str))
    print(json.dumps(OUT, indent=1, default=str)[:9000])


if __name__ == "__main__":
    main()

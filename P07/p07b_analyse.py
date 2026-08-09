"""07B analysis against the sealed endpoints. PARENT and SHAM are read from the 07A rows
(identical code hash, identical t256 states, no engine call was spent re-running them)."""
from __future__ import annotations
import csv, json, math, statistics as S
from pathlib import Path

OUT = {}
ARM_ORDER = ["SHAM", "PARENT", "COMOVING", "TRACKALL", "MULTISITE", "UNTRACKED",
             "SRC_DISPERSED", "SRC_SINKSIDE"]


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def boot(xs, seed=20260809, nb=4000):
    xs = [x for x in xs if x is not None]
    if len(xs) < 3:
        return (None, None)
    r = __import__("random").Random(seed)
    o = sorted(S.median([xs[r.randrange(len(xs))] for _ in xs]) for _ in range(nb))
    return (o[int(0.025 * nb)], o[int(0.975 * nb)])


def sign(pairs):
    d = [b - a for a, b in pairs if a is not None and b is not None]
    pos = sum(1 for x in d if x > 0)
    neg = sum(1 for x in d if x < 0)
    m = pos + neg
    if m == 0:
        return {"n": 0, "pos": 0, "neg": 0, "p": None, "median_diff": 0.0}
    from math import comb
    k = min(pos, neg)
    return {"n": m, "pos": pos, "neg": neg,
            "p": min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m),
            "median_diff": med(d)}


def load():
    rows = {}
    for r in csv.DictReader(open("p07b_rows.csv")):
        rows[(r["block"], r["arm"])] = r
    for r in csv.DictReader(open("p07a_rows.csv")):
        a = {"SHAM": "SHAM", "PARENT_Q400_UNIFORM": "PARENT"}.get(r["arm"])
        if a:
            rows[(r["block"], a)] = dict(r, arm=a)
    for k, r in rows.items():
        if r.get("DELIVERED_FRACTION") in (None, ""):
            ps = n(r.get("planned_sink"))
            r["DELIVERED_FRACTION"] = (n(r.get("realized_sink")) / ps) if ps else None
    return rows


def main():
    rows = load()
    # ---- pre-registered decision rule, evaluated on 07A ---------------------
    ev = [r for r in csv.DictReader(open("p07a_event_ledger.csv"))
          if r["arm"].startswith("PARENT_") and r["rejected"] == "True"
          and n(r.get("CAP_TRACKALL")) is not None]
    R = sum(1 for r in ev if (n(r["CAP_TRACKALL"]) or 0) > 1e-9
            and (n(r["CAP_PARENT"]) or 0) <= 1e-9) / len(ev) if ev else None
    OUT["PREREGISTERED_DECISION_RULE"] = {
        "R": R, "n_rejections_examined": len(ev),
        "branch_taken": ("MASK_REGISTRATION -> primary contrast COMOVING vs PARENT"
                         if R is not None and R >= 0.5
                         else "MATERIAL_DEPLETION -> primary contrast SRC_DISPERSED vs PARENT"),
        "note": "the rule was sealed in p07b_protocol.json before any 07A result was read"}

    # ---- primary + co-primary ----------------------------------------------
    prim = {}
    for L in ("24", "32"):
        blocks = sorted({b for (b, a) in rows if b.startswith(f"L{L}_")})
        par = {b: n(rows[(b, "PARENT")]["DELIVERED_FRACTION"]) for b in blocks
               if (b, "PARENT") in rows}
        for arm in ARM_ORDER:
            g = [(b, rows[(b, arm)]) for b in blocks if (b, arm) in rows]
            if not g:
                continue
            df = [n(r["DELIVERED_FRACTION"]) for _, r in g]
            cont = sum(1 for _, r in g if r.get("same_track_continuous") == "True")
            rej = [(n(r["n_rejected"]) or 0) / max(1.0, n(r["n_scheduled"]) or 1)
                   for _, r in g]
            bd = {"PLANNED": 0, "SOURCE": 0, "SINK": 0}
            causes = {}
            for _, r in g:
                for k, v in json.loads(r.get("reject_causes") or "{}").items():
                    causes[k] = causes.get(k, 0) + v
            e = {"n_blocks_ITT": len(g),
                 "DELIVERED_FRACTION_median": med(df), "DELIVERED_FRACTION_ci": boot(df),
                 "ITT_TRACK_CONTINUITY": f"{cont}/{len(g)}",
                 "rejection_rate_median": med(rej),
                 "reject_causes_total": causes,
                 "terminal_I_over_I0_median":
                     med([n(r.get("terminal_I_over_I0")) for _, r in g]),
                 "terminal_F_over_T_median": med([n(r.get("terminal_F_over_T")) for _, r in g]),
                 "n_terminal_track_lost": sum(1 for _, r in g
                                              if n(r.get("terminal_T")) is None),
                 "CUM_TRACKER_SWEEP_over_M256":
                     med([(n(r.get("CUM_TRACKER_SWEEP")) or 0) / n(r["M256"]) for _, r in g]),
                 "CUM_ABS_SWEEP_over_M256":
                     med([(n(r.get("CUM_ABS_SWEEP")) or 0) / n(r["M256"]) for _, r in g]),
                 "terminal_mass_in_frozen_C256_over_M256":
                     med([(n(r.get("terminal_mass_in_frozen_C256")) or None) and
                          n(r["terminal_mass_in_frozen_C256"]) / n(r["M256"]) for _, r in g])}
            if arm not in ("PARENT", "SHAM"):
                e["vs_PARENT_sign_test"] = sign([(par.get(b), n(r["DELIVERED_FRACTION"]))
                                                 for b, r in g])
                pc = sum(1 for b, r in g
                         if rows.get((b, "PARENT"), {}).get("same_track_continuous") == "True")
                e["IMPROVEMENT_VERDICT"] = (
                    "IMPROVEMENT" if (e["vs_PARENT_sign_test"]["p"] or 1) < 0.05
                    and (e["vs_PARENT_sign_test"]["median_diff"] or 0) > 0
                    and cont >= pc
                    else "THROUGHPUT_GAIN_WITH_CONTINUITY_COST"
                    if (e["vs_PARENT_sign_test"]["median_diff"] or 0) > 0 and cont < pc
                    else "NO_IMPROVEMENT")
            prim[f"L{L}|{arm}"] = e
    OUT["PRIMARY_AND_COPRIMARY"] = prim

    # ---- what binds each executed event -------------------------------------
    bind = {}
    for r in csv.DictReader(open("p07b_event_ledger.csv")):
        if r.get("rejected") != "False":
            continue
        q, pl = n(r.get("q_event")), n(r.get("planned"))
        sc, kc = n(r.get("source_capacity")), n(r.get("sink_capacity"))
        if q is None:
            continue
        k = ("PLANNED" if abs(q - (pl or 0)) < 1e-9 else
             "SOURCE" if sc is not None and abs(q - sc) < 1e-9 else
             "SINK" if kc is not None and abs(q - kc) < 1e-9 else "OTHER")
        d = bind.setdefault(f"L{r['size']}|{r['arm']}", {"PLANNED": 0, "SOURCE": 0,
                                                         "SINK": 0, "OTHER": 0})
        d[k] += 1
    for r in csv.DictReader(open("p07a_event_ledger.csv")):
        if r["arm"] != "PARENT_Q400_UNIFORM" or r.get("rejected") != "False":
            continue
        q, pl = n(r.get("q_event")), n(r.get("planned"))
        sc, kc = n(r.get("source_capacity")), n(r.get("CAP_PARENT"))
        if q is None:
            continue
        k = ("PLANNED" if abs(q - (pl or 0)) < 1e-9 else
             "SOURCE" if sc is not None and abs(q - sc) < 1e-9 else
             "SINK" if kc is not None and abs(q - kc) < 1e-9 else "OTHER")
        d = bind.setdefault(f"L{r['size']}|PARENT", {"PLANNED": 0, "SOURCE": 0,
                                                     "SINK": 0, "OTHER": 0})
        d[k] += 1
    for k, d in bind.items():
        t = sum(d.values()) or 1
        d["fraction_SOURCE_bound"] = d["SOURCE"] / t
        d["fraction_SINK_bound"] = d["SINK"] / t
        d["n_executed"] = t
    OUT["WHAT_BINDS_EACH_EXECUTED_EVENT"] = bind

    Path("p07b_summary.json").write_text(json.dumps(OUT, indent=1, default=str))
    # compact console table
    print(f"{'arm':<15}{'L':>3}{'DELIVERED':>11}{'ci':>21}{'ITT':>7}{'rej':>7}"
          f"{'I/I0':>8}{'F/T':>7}{'src-bound':>10}  verdict")
    for L in ("24", "32"):
        for arm in ARM_ORDER:
            e = prim.get(f"L{L}|{arm}")
            if not e:
                continue
            ci = e["DELIVERED_FRACTION_ci"]
            b = bind.get(f"L{L}|{arm}", {})
            print(f"{arm:<15}{L:>3}{(e['DELIVERED_FRACTION_median'] or 0):>11.4f}"
                  f"{('[%.3f,%.3f]' % ci) if ci[0] is not None else '':>21}"
                  f"{e['ITT_TRACK_CONTINUITY']:>7}{(e['rejection_rate_median'] or 0):>7.3f}"
                  f"{(e['terminal_I_over_I0_median'] or float('nan')):>8.3f}"
                  f"{(e['terminal_F_over_T_median'] or float('nan')):>7.3f}"
                  f"{b.get('fraction_SOURCE_bound', float('nan')):>10.3f}  "
                  f"{e.get('IMPROVEMENT_VERDICT', '-')}")
        print()
    print("decision rule R =", OUT["PREREGISTERED_DECISION_RULE"]["R"])


if __name__ == "__main__":
    main()

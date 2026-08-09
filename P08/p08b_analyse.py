"""08B analysis under the sealed decision rules, plus the frozen selection rule that hands one
amount rule to 08C. Written and hashed BEFORE any 08B result was read."""
from __future__ import annotations
import csv, json, math, statistics as S
from pathlib import Path

ARMS = ["SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP", "BOTH_SAFE"]
GUARDS = {"PARENT": 0, "SINK_FLOOR": 1, "SRC_CAP": 1, "BOTH_SAFE": 2}
OUT = {}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def boot(xs, nb=4000, seed=20260812):
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


rows = {}
for r in csv.DictReader(open("p08b_rows.csv")):
    rows[(r["block"], r["arm"])] = r
tr = list(csv.DictReader(open("p08b_trace.csv")))

# shadow survival at the horizon, per block per arm
shadow = {}
for r in rows.values():
    for th in (40, 45, 50, 55, 60):
        k = f"terminal_shadow_{th}_alive"
        shadow[(r["block"], r["arm"], th)] = (r.get(k) == "True")
# margin distribution at the horizon
margin = {(r["block"], r["arm"]): n(r.get("terminal_margin_frac_below_0.05"))
          for r in rows.values()}

res = {}
for L in ("24", "32"):
    blocks = sorted({b for (b, a) in rows if b.startswith(f"L{L}_")})
    par = {b: n(rows[(b, "PARENT")]["UCR"]) for b in blocks if (b, "PARENT") in rows}
    pcont = sum(1 for b in blocks if rows.get((b, "PARENT"), {}).get(
        "same_track_continuous") == "True")
    pdel = med([n(rows[(b, "PARENT")]["realized_sink"]) / n(rows[(b, "PARENT")]["M256"])
                for b in blocks if (b, "PARENT") in rows])
    pfut = med([n(rows[(b, "PARENT")]["futile_fraction"]) for b in blocks
                if (b, "PARENT") in rows])
    psh55 = sum(1 for b in blocks if shadow.get((b, "PARENT", 55)))
    for arm in ARMS:
        g = [(b, rows[(b, arm)]) for b in blocks if (b, arm) in rows]
        if not g:
            continue
        ucr = [n(r["UCR"]) for _, r in g]
        cont = sum(1 for _, r in g if r["same_track_continuous"] == "True")
        dele = [n(r["realized_sink"]) / n(r["M256"]) for _, r in g]
        fut = [n(r["futile_fraction"]) for _, r in g]
        sh55 = sum(1 for b, _ in g if shadow.get((b, arm, 55)))
        causes = {}
        bd = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
        for _, r in g:
            for k, v in json.loads(r["reject_causes"] or "{}").items():
                causes[k] = causes.get(k, 0) + v
            for k, v in json.loads(r["bound_by"] or "{}").items():
                bd[k] = bd.get(k, 0) + v
        e = {"n_blocks_ITT": len(g),
             "UCR_median": med(ucr), "UCR_ci": boot(ucr),
             "ITT_TRACK_CONTINUITY": f"{cont}/{len(g)}",
             "shadow55_alive": f"{sh55}/{len(g)}",
             "shadow50_alive": f"{sum(1 for b, _ in g if shadow.get((b, arm, 50)))}/{len(g)}",
             "shadow60_alive": f"{sum(1 for b, _ in g if shadow.get((b, arm, 60)))}/{len(g)}",
             "margin_frac_below_0.05_median": med([margin.get((b, arm)) for b, _ in g]),
             "delivered_over_M256_median": med(dele),
             "futile_fraction_median": med(fut),
             "incumbent_removed_over_M256": med([n(r["incumbent_removed_over_M256"])
                                                 for _, r in g]),
             "fresh_over_M256": med([n(r["fresh_over_M256"]) for _, r in g]),
             "terminal_I_over_I0": med([n(r.get("terminal_I_over_I0")) for _, r in g]),
             "incumbent_displacement": med([n(r.get("incumbent_displacement")) for _, r in g]),
             "replacement_per_1000_steps": med([n(r["replacement_per_1000_steps"])
                                                for _, r in g]),
             "replacement_per_attempted": med([n(r["replacement_per_attempted"])
                                               for _, r in g]),
             "replacement_per_delivered": med([n(r.get("replacement_per_delivered"))
                                               for _, r in g]),
             "delivered_per_1000_steps": med([n(r["delivered_per_1000_steps"]) for _, r in g]),
             "CUM_ABS_SWEEP_over_M256": med([(n(r.get("CUM_ABS_SWEEP")) or 0) / n(r["M256"])
                                             for _, r in g]),
             "rejection_rate": med([(n(r["n_rejected"]) or 0) / 320 for _, r in g]),
             "reject_causes": causes, "bound_by": bd,
             "n_terminal_track_lost": sum(1 for _, r in g if not r.get("terminal_T"))}
        if arm not in ("PARENT", "SHAM"):
            st = sign([(par.get(b), n(r["UCR"])) for b, r in g])
            e["UCR_vs_PARENT_sign_test"] = st
            improves = ((st["p"] or 1) < 0.05 and (st["median_diff"] or 0) > 0
                        and cont >= pcont and med(fut) <= (pfut or 0) + 0.10
                        and sh55 >= psh55)
            abstention = (med(dele) < 0.5 * (pdel or 1)
                          and not ((st["p"] or 1) < 0.05 and (st["median_diff"] or 0) > 0))
            gaming = (cont >= pcont and sh55 < psh55) or ((med(
                [margin.get((b, arm)) for b, _ in g]) or 0) > 0.5)
            e["VERDICT"] = ("TRACKER_GAMING_DETECTED" if gaming else
                            "SAFE_ABSTENTION" if abstention else
                            "IMPROVES" if improves else "NO_EFFECT")
        res[f"L{L}|{arm}"] = e
OUT["FACTORIAL"] = res

# ---- frozen selection rule handed to 08C ----------------------------------
elig = []
for arm in ("PARENT", "SINK_FLOOR", "SRC_CAP", "BOTH_SAFE"):
    v = [res.get(f"L{L}|{arm}") for L in ("24", "32")]
    if any(x is None for x in v):
        continue
    bad = any(x.get("VERDICT") in ("TRACKER_GAMING_DETECTED", "SAFE_ABSTENTION") for x in v
              if "VERDICT" in x)
    if bad:
        continue
    pooled = med([n(rows[(b, arm)]["UCR"]) for (b, a) in rows if a == arm])
    lo = min(x["UCR_ci"][0] for x in v)
    hi = max(x["UCR_ci"][1] for x in v)
    elig.append({"arm": arm, "pooled_UCR": pooled, "ci_lo": lo, "ci_hi": hi,
                 "guards": GUARDS[arm]})
elig.sort(key=lambda d: (-d["pooled_UCR"], d["guards"]))
best = elig[0]
# simplicity tie-break: if a simpler arm's CI overlaps the best arm's CI, take the simpler one
simpler = [d for d in elig if d["guards"] < best["guards"] and d["ci_hi"] >= best["ci_lo"]]
if simpler:
    simpler.sort(key=lambda d: (d["guards"], -d["pooled_UCR"]))
    best = simpler[0]
import p08_core as _P8
floor, ceil = _P8.AMOUNT_RULES[best["arm"]]
Path("p08b_selected.json").write_text(json.dumps(
    {"arm": best["arm"], "floor": floor, "ceil": ceil, "pooled_UCR": best["pooled_UCR"],
     "rule": "highest pooled UCR among arms that are neither SAFE_ABSTENTION nor "
             "TRACKER_GAMING_DETECTED; a simpler arm whose CI overlaps the winner's is "
             "preferred", "candidates": elig}, indent=1))
OUT["SELECTION_FOR_08C"] = {"selected": best, "candidates": elig}

Path("p08b_summary.json").write_text(json.dumps(OUT, indent=1, default=str))

print(f"{'arm':<12}{'L':>3}{'UCR':>8}{'ci':>18}{'ITT':>6}{'sh50':>6}{'sh55':>6}"
      f"{'delivre':>9}{'futile':>8}{'inc':>7}{'fresh':>7}{'rej':>7}  verdict")
for L in ("24", "32"):
    for arm in ARMS:
        e = res.get(f"L{L}|{arm}")
        if not e:
            continue
        ci = e["UCR_ci"]
        print(f"{arm:<12}{L:>3}{(e['UCR_median'] or 0):>8.4f}"
              f"{('[%.3f,%.3f]' % ci) if ci[0] is not None else '':>18}"
              f"{e['ITT_TRACK_CONTINUITY']:>6}{e['shadow50_alive']:>6}{e['shadow55_alive']:>6}"
              f"{e['delivered_over_M256_median']:>9.3f}{e['futile_fraction_median']:>8.3f}"
              f"{e['incumbent_removed_over_M256']:>7.3f}{e['fresh_over_M256']:>7.3f}"
              f"{e['rejection_rate']:>7.3f}  {e.get('VERDICT','-')}")
    print()
print("SELECTION POUR 08C:", json.dumps(OUT["SELECTION_FOR_08C"]["selected"]))

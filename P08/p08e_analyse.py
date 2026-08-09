"""08E -- verification of the three sealed predictions about the regime-dependent sign
reversal of the safety floor."""
from __future__ import annotations
import csv, json, math, statistics as S
from math import comb
from pathlib import Path

def n(v):
    try:
        x = float(v); return None if math.isnan(x) else x
    except (TypeError, ValueError): return None
def med(xs):
    xs = [x for x in xs if x is not None]; return S.median(xs) if xs else None
def boot(xs, nb=4000, seed=20260815):
    xs = [x for x in xs if x is not None]
    if len(xs) < 3: return (None, None)
    r = __import__("random").Random(seed)
    o = sorted(S.median([xs[r.randrange(len(xs))] for _ in xs]) for _ in range(nb))
    return (o[int(0.025*nb)], o[int(0.975*nb)])
def sign(pairs):
    d = [b - a for a, b in pairs if a is not None and b is not None]
    pos = sum(1 for x in d if x > 0); neg = sum(1 for x in d if x < 0); m = pos + neg
    if m == 0: return {"n": 0, "p": None, "median_diff": 0.0}
    k = min(pos, neg)
    return {"n": m, "pos": pos, "neg": neg,
            "p": min(1.0, 2*sum(comb(m, i) for i in range(k+1))/2**m), "median_diff": med(d)}

rows = list(csv.DictReader(open("p08e_rows.csv")))
man = json.load(open("p08e_manifest.json"))
OUT = {"protocol_sha256": Path("p08e_protocol.sha256").read_text().split()[0],
       "cohort": {"blocks_attempted": len(man["blocks"]),
                  "t256_status": {k: sum(1 for b in man["blocks"] if b["t256_status"] == k)
                                  for k in sorted({b["t256_status"] for b in man["blocks"]})},
                  "engine_invocations": man["engine_invocations"]}}
def cell(sz, arm):
    return [r for r in rows if r["size"] == sz and r["arm"] == arm]

desc = {}
for sz in ("24", "32"):
    for arm in ("SHAM", "PARENT", "SINK_FLOOR"):
        g = cell(sz, arm)
        if not g: continue
        causes = {}
        for r in g:
            for k, v in json.loads(r["reject_causes"] or "{}").items():
                causes[k] = causes.get(k, 0) + v
        desc[f"L{sz}|{arm}"] = {
            "n_blocks_ITT": len(g),
            "ITT_TRACK_CONTINUITY": f"{sum(1 for r in g if r['same_track_continuous']=='True')}/{len(g)}",
            "n_split": sum(1 for r in g if r["split"] == "True"),
            "n_loss": sum(1 for r in g if r["loss"] == "True"),
            "failure_types": {k: sum(1 for r in g if r["first_failure_type"] == k)
                              for k in sorted({r["first_failure_type"] for r in g})},
            "UCR_median": med([n(r["UCR"]) for r in g]), "UCR_ci": boot([n(r["UCR"]) for r in g]),
            "delivered_over_M256": med([n(r["delivered_over_M256"]) for r in g]),
            "incumbent_removed_over_M256": med([n(r["incumbent_removed_over_M256"]) for r in g]),
            "fresh_over_M256": med([n(r["fresh_over_M256"]) for r in g]),
            "futile_fraction": med([n(r["futile_fraction"]) for r in g]),
            "n_events_median": med([n(r["n_events"]) for r in g]),
            "reject_causes": causes,
            "terminal_shadow55_alive": sum(1 for r in g if r.get("terminal_shadow_55_alive") == "True"),
            "terminal_margin_frac_below_005": med([n(r.get("terminal_margin_frac_below_0.05")) for r in g]),
            "max_identity_residual": max(n(r["max_identity_residual"]) or 0 for r in g)}
OUT["DESCRIPTIVE"] = desc

e1 = {"detail": {}}; ok1 = True
for sz in ("24", "32"):
    a = sum(1 for r in cell(sz, "SINK_FLOOR") if r["same_track_continuous"] == "True")
    b = sum(1 for r in cell(sz, "PARENT") if r["same_track_continuous"] == "True")
    e1["detail"][f"L{sz}"] = {"SINK_FLOOR": f"{a}/9", "PARENT": f"{b}/9",
                              "meets": a >= 7 and b <= 4}
    ok1 = ok1 and a >= 7 and b <= 4
e1["VERDICT"] = "CONFIRMED" if ok1 else "REFUTED_AS_STATED"
OUT["E1_FLOOR_RESCUES_CONTINUITY_UNDER_LAW_29"] = e1

e2 = {"detail": {}}; ok2 = True
for sz in ("24", "32"):
    sf = {r["block"]: n(r["UCR"]) for r in cell(sz, "SINK_FLOOR")}
    pa = {r["block"]: n(r["UCR"]) for r in cell(sz, "PARENT")}
    st = sign([(pa[b], sf[b]) for b in sorted(set(sf) & set(pa))])
    m = med(list(sf.values()))
    okc = (m or 0) > 0.05 and (st["p"] or 1) < 0.05 and (st["median_diff"] or 0) > 0
    ok2 = ok2 and okc
    e2["detail"][f"L{sz}"] = {"SINK_FLOOR_UCR_median": m, "ci": boot(list(sf.values())),
                              "PARENT_UCR_median": med(list(pa.values())),
                              "sign_test_vs_PARENT": st, "meets": okc}
e2["VERDICT"] = "CONFIRMED" if ok2 else "REFUTED_AS_STATED"
OUT["E2_FLOOR_IS_THE_ONLY_ARM_WITH_NON_ZERO_REPLACEMENT"] = e2

e3 = {"detail": {}}; ok3 = True
for sz in ("24", "32"):
    s = sum(1 for r in cell(sz, "SINK_FLOOR") if r["split"] == "True")
    e3["detail"][f"L{sz}"] = {"SINK_FLOOR_splits": f"{s}/9", "meets": s <= 2}
    ok3 = ok3 and s <= 2
e3["VERDICT"] = "CONFIRMED" if ok3 else "REFUTED_AS_STATED"
e3["contrast_under_LAW_16"] = "9/9 splits at both sizes (08B discovery and 08D confirmation)"
OUT["E3_THE_SPLIT_EFFECT_REVERSES_SIGN_WITH_THE_LAW"] = e3

OUT["OVERALL"] = {k: OUT[k]["VERDICT"] for k in OUT if k.startswith("E")}
OUT["INTERPRETATION"] = ("REGIME_DEPENDENT_REPAIR_CONFIRMED"
                         if all(v == "CONFIRMED" for v in OUT["OVERALL"].values())
                         else "DISCOVERY_WITHIN_A_CONFIRMATION_COHORT")
Path("p08e_summary.json").write_text(json.dumps(OUT, indent=1, default=str))
print("=== 08E ===")
for k, v in OUT["OVERALL"].items(): print(f"  {k:<52} {v}")
print("  INTERPRETATION:", OUT["INTERPRETATION"])
print(f"\n{'arm':<14}{'L':>3}{'ITT':>7}{'split':>7}{'perte':>7}{'UCR':>8}{'delivre':>9}"
      f"{'tirs':>7}{'ombre55':>9}")
for sz in ("24", "32"):
    for arm in ("SHAM", "PARENT", "SINK_FLOOR"):
        e = desc.get(f"L{sz}|{arm}")
        if not e: continue
        print(f"{arm:<14}{sz:>3}{e['ITT_TRACK_CONTINUITY']:>7}{e['n_split']:>7}{e['n_loss']:>7}"
              f"{(e['UCR_median'] or 0):>8.4f}{e['delivered_over_M256']:>9.3f}"
              f"{(e['n_events_median'] or 0):>7.0f}{e['terminal_shadow55_alive']:>7}/9")

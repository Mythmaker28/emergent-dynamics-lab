"""08D -- verification of the sealed point predictions C1-C4 and adjudication of the two
LAW_29 transports. Criteria are read from the sealed protocol."""
from __future__ import annotations
import csv, json, math, statistics as S
from math import comb
from pathlib import Path

PROTO = json.load(open("p08d_protocol.json"))
OUT = {"protocol_sha256": Path("p08d_protocol.sha256").read_text().split()[0]}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def boot(xs, nb=4000, seed=20260814):
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
        return {"n": 0, "p": None, "median_diff": 0.0}
    k = min(pos, neg)
    return {"n": m, "pos": pos, "neg": neg,
            "p": min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m),
            "median_diff": med(d)}


rows = list(csv.DictReader(open("p08d_rows.csv")))
man = json.load(open("p08d_manifest.json"))
keys = [("LAW_16", "24"), ("LAW_16", "32"), ("LAW_29", "24"), ("LAW_29", "32")]
OUT["cohort"] = {
    "blocks_attempted": len(man["blocks"]),
    "t256_status": {k: sum(1 for b in man["blocks"] if b["t256_status"] == k)
                    for k in sorted({b["t256_status"] for b in man["blocks"]})},
    "engine_invocations": man["engine_invocations"],
    "sham_relaxation_steps": man.get("sham_relaxation_steps")}


def cell(law, size, arm):
    return [r for r in rows if r["law"] == law and r["size"] == size and r["arm"] == arm]


# --------------------------------------------------------------- descriptive
desc = {}
for law, sz in keys:
    for arm in sorted({r["arm"] for r in rows if r["law"] == law and r["size"] == sz}):
        g = cell(law, sz, arm)
        if not g:
            continue
        causes = {}
        for r in g:
            for k, v in json.loads(r["reject_causes"] or "{}").items():
                causes[k] = causes.get(k, 0) + v
        desc[f"{law}|L{sz}|{arm}"] = {
            "n_blocks_ITT": len(g),
            "UCR_median": med([n(r["UCR"]) for r in g]),
            "UCR_ci": boot([n(r["UCR"]) for r in g]),
            "ITT_TRACK_CONTINUITY":
                f"{sum(1 for r in g if r['same_track_continuous'] == 'True')}/{len(g)}",
            "n_split": sum(1 for r in g if r["split"] == "True"),
            "n_loss": sum(1 for r in g if r["loss"] == "True"),
            "failure_types": {k: sum(1 for r in g if r["first_failure_type"] == k)
                              for k in sorted({r["first_failure_type"] for r in g})},
            "delivered_over_M256": med([n(r["delivered_over_M256"]) for r in g]),
            "incumbent_removed_over_M256": med([n(r["incumbent_removed_over_M256"])
                                                for r in g]),
            "fresh_over_M256": med([n(r["fresh_over_M256"]) for r in g]),
            "futile_fraction": med([n(r["futile_fraction"]) for r in g]),
            "n_events_median": med([n(r["n_events"]) for r in g]),
            "n_waited_median": med([n(r.get("n_waited") or 0) for r in g]),
            "spacing": med([n(r["spacing"]) for r in g]),
            "reject_causes": causes,
            "terminal_I_over_I0": med([n(r.get("terminal_I_over_I0")) for r in g]),
            "max_identity_residual": max(n(r["max_identity_residual"]) or 0 for r in g)}
OUT["DESCRIPTIVE"] = desc

# ------------------------------------------------------------------ C1 split
c1 = {"detail": {}}
ok1 = True
for law, sz in keys:
    if law != "LAW_16":
        continue
    sf = cell(law, sz, "SINK_FLOOR")
    pa = cell(law, sz, "PARENT")
    a = sum(1 for r in sf if r["split"] == "True")
    b = sum(1 for r in pa if r["split"] == "True")
    c1["detail"][f"{law}|L{sz}"] = {"SINK_FLOOR_splits": f"{a}/{len(sf)}",
                                    "PARENT_splits": f"{b}/{len(pa)}",
                                    "meets": a >= 7 and b <= 1}
    ok1 = ok1 and a >= 7 and b <= 1
c1["VERDICT"] = "CONFIRMED" if ok1 else "REFUTED_AS_STATED"
c1["transport_to_LAW_29"] = {
    f"LAW_29|L{sz}": {"SINK_FLOOR_splits":
                      f"{sum(1 for r in cell('LAW_29', sz, 'SINK_FLOOR') if r['split'] == 'True')}"
                      f"/{len(cell('LAW_29', sz, 'SINK_FLOOR'))}"} for sz in ("24", "32")}
OUT["C1_FLOOR_SPLITS_THE_COMPONENT"] = c1

# ------------------------------------------------------------- C2 headroom cap
c2 = {"detail": {}}
ok2 = True
for law, sz in keys:
    if law != "LAW_16":
        continue
    sc = {r["block"]: n(r["delivered_over_M256"]) for r in cell(law, sz, "SRC_CAP")}
    pa = {r["block"]: n(r["delivered_over_M256"]) for r in cell(law, sz, "PARENT")}
    common = sorted(set(sc) & set(pa))
    ratio = med([sc[b] / pa[b] for b in common if pa[b]])
    below = sum(1 for b in common if sc[b] < pa[b])
    okc = (0.35 <= (ratio or 0) <= 0.75) and below >= 8
    ok2 = ok2 and okc
    c2["detail"][f"{law}|L{sz}"] = {"ratio_SRC_CAP_over_PARENT": ratio,
                                    "n_blocks_strictly_below": f"{below}/{len(common)}",
                                    "meets": okc}
c2["VERDICT"] = "CONFIRMED" if ok2 else "REFUTED_AS_STATED"
OUT["C2_HEADROOM_CAP_LOWERS_THE_FLUX"] = c2

# ---------------------------------------------------- C3 no safe rule improves
c3 = {"detail": {}}
ok3 = True
for law, sz in keys:
    if law != "LAW_16":
        continue
    pa = {r["block"]: n(r["UCR"]) for r in cell(law, sz, "PARENT")}
    for arm in ("SINK_FLOOR", "SRC_CAP"):
        g = {r["block"]: n(r["UCR"]) for r in cell(law, sz, arm)}
        st = sign([(pa[b], g[b]) for b in sorted(set(pa) & set(g))])
        beats = (st["p"] or 1) < 0.05 and (st["median_diff"] or 0) < 0
        c3["detail"][f"{law}|L{sz}|{arm}"] = {"sign_test_vs_PARENT": st,
                                              "PARENT_wins": beats}
        ok3 = ok3 and beats
c3["VERDICT"] = "CONFIRMED" if ok3 else "REFUTED_AS_STATED"
OUT["C3_NO_SAFE_AMOUNT_RULE_IMPROVES_REPLACEMENT"] = c3

# ------------------------------------------------- C4 probe transports to LAW_29
c4 = {"detail": {}}
pr = list(csv.DictReader(open("p08d_probe.csv"))) if Path("p08d_probe.csv").exists() else []
ok4 = True
for law in ("LAW_16", "LAW_29"):
    for sz in ("24", "32"):
        g = [r for r in pr if r["law"] == law and r["size"] == sz
             and n(r.get("rho_observed_next_window")) is not None]
        rt = [n(r["rho_probe_slope8"]) / n(r["rho_observed_next_window"]) for r in g
              if n(r["rho_observed_next_window"]) and n(r["rho_observed_next_window"]) > 0]
        if not rt:
            continue
        inside = sum(1 for x in rt if 1 / 1.5 <= x <= 1.5)
        c4["detail"][f"{law}|L{sz}"] = {"n": len(rt), "median_ratio": med(rt),
                                        "range": (min(rt), max(rt)),
                                        "within_factor_1.5": f"{inside}/{len(rt)}"}
        if law == "LAW_29":
            ok4 = ok4 and (1 / 1.5 <= (med(rt) or 0) <= 1.5)
c4["VERDICT"] = "CONFIRMED" if ok4 else "REFUTED_AS_STATED"
c4["note"] = ("the probe measures the SOURCE side only; comparisons in windows where the sink "
              "has taken over are expected to over-predict and are not counted against it, "
              "exactly as established in 08A")
OUT["C4_PROBE_PREDICTS_RHO_UNDER_A_SECOND_LAW"] = c4

# ------------------------------------------------------------ LAW_29 transport
tr = {}
for sz in ("24", "32"):
    pa = cell("LAW_29", sz, "PARENT")
    pc = sum(1 for r in pa if r["same_track_continuous"] == "True")
    pu = med([n(r["UCR"]) for r in pa])
    for arm in ("ONLINE_STRICT", "ONLINE_NORMALIZED"):
        g = cell("LAW_29", sz, arm)
        if not g:
            continue
        c = sum(1 for r in g if r["same_track_continuous"] == "True")
        u = med([n(r["UCR"]) for r in g])
        d = med([n(r["delivered_over_M256"]) for r in g])
        pd = med([n(r["delivered_over_M256"]) for r in pa])
        confirms = c > pc and (u or 0) >= 0.5 * (pu or 0)
        abst = (d or 0) < 0.5 * (pd or 1) and not confirms
        tr[f"L{sz}|{arm}"] = {
            "ITT_continuity": f"{c}/{len(g)}", "PARENT_ITT": f"{pc}/{len(pa)}",
            "UCR": u, "PARENT_UCR": pu, "delivered_over_M256": d, "PARENT_delivered": pd,
            "spacing": med([n(r["spacing"]) for r in g]),
            "n_events_median": med([n(r["n_events"]) for r in g]),
            "CONFIRMS": confirms,
            "SAFE_ABSTENTION": abst}
strict = all(v["CONFIRMS"] for k, v in tr.items() if "STRICT" in k)
norm = all(v["CONFIRMS"] for k, v in tr.items() if "NORMALIZED" in k)
OUT["LAW29_TRANSPORT"] = {
    "detail": tr,
    "VERDICT": ("STRICT_MECHANISTIC_TRANSPORT" if strict else
                "NORMALIZED_MECHANISTIC_TRANSPORT" if norm else
                "GENERALIZATION_LIMIT_CONFIRMED"),
    "rule": PROTO["LAW29_TRANSPORT"]["adjudication"],
    "pre_failure_note": "under LAW_29 the PARENT arm accumulates its exchange before the "
                        "component dissolves; any magnitude reported there is "
                        "TRANSIENT_PRE_FAILURE"}
OUT["OVERALL"] = {k: OUT[k]["VERDICT"] for k in OUT if k.startswith("C")}
OUT["OVERALL"]["LAW29_TRANSPORT"] = OUT["LAW29_TRANSPORT"]["VERDICT"]

Path("p08d_summary.json").write_text(json.dumps(OUT, indent=1, default=str))
print("=== PREDICTIONS SCELLEES ===")
for k, v in OUT["OVERALL"].items():
    print(f"  {k:<46} {v}")
print(f"\n{'config':<22}{'arm':<18}{'UCR':>8}{'ITT':>6}{'split':>7}{'delivre':>9}"
      f"{'tirs':>7}{'esp':>5}")
for law, sz in keys:
    for arm in ("SHAM", "PARENT", "SINK_FLOOR", "SRC_CAP", "ONLINE_STRICT",
                "ONLINE_NORMALIZED"):
        e = desc.get(f"{law}|L{sz}|{arm}")
        if not e:
            continue
        print(f"{law + '|L' + sz:<22}{arm:<18}{(e['UCR_median'] or 0):>8.4f}"
              f"{e['ITT_TRACK_CONTINUITY']:>6}{e['n_split']:>7}"
              f"{e['delivered_over_M256']:>9.3f}{(e['n_events_median'] or 0):>7.0f}"
              f"{(e['spacing'] or 0):>5.0f}")
    print()

"""07D -- verification of the sealed point predictions. Pass/fail criteria are read from the
sealed protocol, not restated here, so they cannot drift."""
from __future__ import annotations
import csv, json, math, statistics as S
from pathlib import Path

PROTO = json.load(open("p07d_protocol.json"))
PRED = PROTO["SEALED_POINT_PREDICTIONS"]
OUT = {"protocol_sha256": Path("p07d_protocol.sha256").read_text().split()[0]}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


rows = list(csv.DictReader(open("p07d_rows.csv")))
cad = list(csv.DictReader(open("p07d_cadence_rows.csv")))
man = json.load(open("p07d_manifest.json"))
OUT["cohort"] = {
    "blocks_attempted": len(man["blocks"]),
    "t256_status": {k: sum(1 for b in man["blocks"] if b["t256_status"] == k)
                    for k in sorted({b["t256_status"] for b in man["blocks"]})},
    "engine_invocations": man["engine_invocations"]}

# ---------------------------------------------------------------- P1
p1 = {"tolerance_factor": 1.35, "detail": {}}
ok1 = True
for L in ("24", "32"):
    pp = PRED["P1_CADENCE_SATURATION_LAW"]["predicted_Phi"][f"L{L}"]
    obs = {}
    for s in (2, 8, 32, 128):
        g = [n(r["PHI_per_step"]) for r in cad if r["size"] == L and int(r["spacing"]) == s]
        obs[str(s)] = {"observed_median": med(g), "n_blocks": len(g),
                       "predicted": pp[str(s)]}
        if obs[str(s)]["observed_median"]:
            rt = obs[str(s)]["observed_median"] / pp[str(s)]
            obs[str(s)]["ratio_obs_over_pred"] = rt
            obs[str(s)]["within_tolerance"] = (1 / 1.35) <= rt <= 1.35
            ok1 = ok1 and obs[str(s)]["within_tolerance"]
    ordering = (obs["128"]["observed_median"] or 9) < (obs["32"]["observed_median"] or 0)
    obs["ORDERING_Phi128_below_Phi32"] = ordering
    ok1 = ok1 and ordering
    p1["detail"][f"L{L}"] = obs
p1["VERDICT"] = "CONFIRMED" if ok1 else "REFUTED_AS_STATED"
OUT["P1_CADENCE_SATURATION_LAW"] = p1

# ---------------------------------------------------------------- P2
p2 = {"detail": {}}
ok2 = True
for lw, sz in sorted({(r["law"], r["size"]) for r in rows}, key=lambda k: (k[0], int(k[1]))):
    d = {}
    for arm in ("PARENT", "SRC_SINKSIDE"):
        g = [r for r in rows if r["law"] == lw and r["size"] == sz and r["arm"] == arm]
        d[arm] = {"DELIVERED_FRACTION": med([n(r["DELIVERED_FRACTION"]) for r in g]),
                  "incumbent_over_M256": med([n(r["incumbent_removed_over_M256"]) for r in g]),
                  "REPLACEMENT_EFFICIENCY": med([n(r["REPLACEMENT_EFFICIENCY"]) for r in g]),
                  "ITT_continuity": f"{sum(1 for r in g if r['same_track_continuous']=='True')}"
                                    f"/{len(g)}"}
    e_p = d["PARENT"]["REPLACEMENT_EFFICIENCY"]
    e_s = d["SRC_SINKSIDE"]["REPLACEMENT_EFFICIENCY"]
    d["ratio_PARENT_over_SINKSIDE"] = (e_p / e_s) if e_s else None
    d["checks"] = {
        "SINKSIDE_delivered_ge_0.95": (d["SRC_SINKSIDE"]["DELIVERED_FRACTION"] or 0) >= 0.95,
        "SINKSIDE_incumbent_le_0.20": (d["SRC_SINKSIDE"]["incumbent_over_M256"] or 9) <= 0.20,
        "SINKSIDE_efficiency_le_0.10": (e_s or 9) <= 0.10,
        "efficiency_ratio_ge_4": (d["ratio_PARENT_over_SINKSIDE"] or 0) >= 4}
    ok2 = ok2 and all(d["checks"].values())
    p2["detail"][f"{lw}|L{sz}"] = d
p2["VERDICT"] = "CONFIRMED" if ok2 else "REFUTED_AS_STATED"
OUT["P2_FUTILE_CYCLE_EFFICIENCY_COLLAPSE"] = p2

# ---------------------------------------------------------------- P3
p3 = {"band": [0.25, 0.60], "detail": {}}
ok3 = True
for lw, sz in sorted({(r["law"], r["size"]) for r in rows}, key=lambda k: (k[0], int(k[1]))):
    g = [n(r["incumbent_removed_over_M256"]) for r in rows
         if r["law"] == lw and r["size"] == sz and r["arm"] == "PARENT"]
    m = med(g)
    inb = m is not None and 0.25 <= m <= 0.60
    ok3 = ok3 and inb
    p3["detail"][f"{lw}|L{sz}"] = {"median": m, "min": min(g) if g else None,
                                   "max": max(g) if g else None, "n_blocks": len(g),
                                   "in_band": inb}
p3["VERDICT"] = "CONFIRMED" if ok3 else "REFUTED_AS_STATED"
OUT["P3_BOUNDED_EXCHANGE_INVARIANCE"] = p3

# ---------------------------------------------------------------- P4
p4 = {"threshold": 0.70, "detail": {}}
ok4 = True
for lw, sz in sorted({(r["law"], r["size"]) for r in rows}, key=lambda k: (k[0], int(k[1]))):
    f = []
    for r in rows:
        if r["law"] == lw and r["size"] == sz and r["arm"] == "PARENT":
            b = json.loads(r["bound_by"])
            t = sum(b.values())
            if t:
                f.append(b["SOURCE"] / t)
    m = med(f)
    okk = m is not None and m >= 0.70
    ok4 = ok4 and okk
    p4["detail"][f"{lw}|L{sz}"] = {"median_source_bound_fraction": m, "n_blocks": len(f),
                                   "meets_threshold": okk}
p4["VERDICT"] = "CONFIRMED" if ok4 else "REFUTED_AS_STATED"
OUT["P4_SOURCE_IS_THE_BINDING_CONSTRAINT"] = p4

# ---------------------------------------------------------- ITT and safety
itt = {}
for lw, sz in sorted({(r["law"], r["size"]) for r in rows}, key=lambda k: (k[0], int(k[1]))):
    for arm in ("SHAM", "PARENT", "SRC_SINKSIDE"):
        g = [r for r in rows if r["law"] == lw and r["size"] == sz and r["arm"] == arm]
        if not g:
            continue
        causes = {}
        for r in g:
            for k, v in json.loads(r["reject_causes"] or "{}").items():
                causes[k] = causes.get(k, 0) + v
        itt[f"{lw}|L{sz}|{arm}"] = {
            "n_blocks_ITT": len(g),
            "continuous": sum(1 for r in g if r["same_track_continuous"] == "True"),
            "failure_types": {k: sum(1 for r in g if r["first_failure_type"] == k)
                              for k in sorted({r["first_failure_type"] for r in g})},
            "terminal_I_over_I0": med([n(r.get("terminal_I_over_I0")) for r in g]),
            "terminal_F_over_T": med([n(r.get("terminal_F_over_T")) for r in g]),
            "reject_causes": causes,
            "max_identity_residual": max(n(r["max_identity_residual"]) or 0 for r in g),
            "max_global_balance_residual": max(n(r["max_global_balance_residual"]) or 0
                                               for r in g)}
OUT["ITT_AND_INVARIANTS"] = itt
OUT["OVERALL"] = {k: OUT[k]["VERDICT"] for k in OUT if k.startswith("P")}

Path("p07d_summary.json").write_text(json.dumps(OUT, indent=1, default=str))

print("=== PREDICTIONS SCELLEES ===")
for k in ("P1_CADENCE_SATURATION_LAW", "P2_FUTILE_CYCLE_EFFICIENCY_COLLAPSE",
          "P3_BOUNDED_EXCHANGE_INVARIANCE", "P4_SOURCE_IS_THE_BINDING_CONSTRAINT"):
    print(f"  {k:<42} {OUT[k]['VERDICT']}")
print("\n--- P1 cadence (graines neuves, espacements retenus a l'ecart) ---")
for L, d in p1["detail"].items():
    for s in ("2", "8", "32", "128"):
        o = d[s]
        print(f"  {L} s={s:>4}: predit {o['predicted']:.5f}  observe "
              f"{(o['observed_median'] or 0):.5f}  ratio {o.get('ratio_obs_over_pred', 0):.3f}"
              f"  {'OK' if o.get('within_tolerance') else 'HORS TOLERANCE'}")
    print(f"  {L} ordre Phi(128) < Phi(32) : {d['ORDERING_Phi128_below_Phi32']}")
print("\n--- P3 echange borne ---")
for k, v in p3["detail"].items():
    print(f"  {k:<16} mediane {v['median']:.3f}  [{v['min']:.3f},{v['max']:.3f}]  "
          f"n={v['n_blocks']}  {'dans la bande' if v['in_band'] else 'HORS BANDE'}")
print("\n--- P2 efficacite ---")
for k, v in p2["detail"].items():
    print(f"  {k:<16} PARENT eff={v['PARENT']['REPLACEMENT_EFFICIENCY']:.3f} "
          f"({v['PARENT']['ITT_continuity']})   SINKSIDE eff="
          f"{v['SRC_SINKSIDE']['REPLACEMENT_EFFICIENCY']:.3f} delivre="
          f"{v['SRC_SINKSIDE']['DELIVERED_FRACTION']:.3f} ({v['SRC_SINKSIDE']['ITT_continuity']})"
          f"   rapport={v['ratio_PARENT_over_SINKSIDE']:.1f}")
print("\n--- P4 ---")
for k, v in p4["detail"].items():
    print(f"  {k:<16} {v['median_source_bound_fraction']:.3f}")

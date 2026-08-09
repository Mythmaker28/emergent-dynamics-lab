"""P09 analysis and sealed adjudication. Written and hashed BEFORE any P09 result was read."""
from __future__ import annotations
import csv, json, math, statistics as S
from math import comb
from pathlib import Path

PROTO = json.load(open("p09_protocol.json"))
MARGIN_IN = (0.847, 1.180)
MARGIN_CI = (0.781, 1.280)
OUT = {"protocol_sha256": Path("p09_protocol.sha256").read_text().split()[0],
       "sequence_sha256": PROTO["exogenous_sequence"]["sha256"]}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def boot(xs, nb=6000, seed=20260816):
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
        return {"n": 0, "pos": 0, "neg": 0, "p": None, "median_diff": 0.0, "ci": (None, None)}
    k = min(pos, neg)
    return {"n": m, "pos": pos, "neg": neg,
            "p": min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m),
            "median_diff": med(d), "ci": boot(d)}


def fisher(a, b):
    """Two-sided Fisher exact on 2x2 [[a_succ, a_fail],[b_succ, b_fail]] with n=9 each."""
    from math import comb as C
    n1 = n2 = 9
    tot = a + b
    def p(k):
        return C(n1, k) * C(n2, tot - k) / C(n1 + n2, tot) if 0 <= tot - k <= n2 else 0.0
    obs = p(a)
    return min(1.0, sum(p(k) for k in range(0, n1 + 1) if p(k) <= obs + 1e-12))


rows = list(csv.DictReader(open("p09_rows.csv")))
man = json.load(open("p09_manifest.json"))
CELLS = [("LAW_16", "24"), ("LAW_16", "32"), ("LAW_29", "24"), ("LAW_29", "32")]
ARMS = ["SHAM", "PARENT_FULL", "FLOOR_FULL", "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY",
        "PARENT_LOW_CONSTANT"]
OUT["cohort"] = {"blocks": len(man["blocks"]),
                 "t256_status": {k: sum(1 for b in man["blocks"] if b["t256_status"] == k)
                                 for k in sorted({b["t256_status"] for b in man["blocks"]})},
                 "engine_invocations": man["engine_invocations"],
                 "n_trajectories": len(rows)}


def cell(law, sz, arm):
    return [r for r in rows if r["law"] == law and r["size"] == sz and r["arm"] == arm]


# ------------------------------------------------------------------ descriptive
desc = {}
for law, sz in CELLS:
    for arm in ARMS:
        g = cell(law, sz, arm)
        if not g:
            continue
        causes = {}
        bd = {"PLANNED": 0, "SOURCE": 0, "SINK": 0, "OTHER": 0}
        for r in g:
            for k, v in json.loads(r["reject_causes"] or "{}").items():
                causes[k] = causes.get(k, 0) + v
            for k, v in json.loads(r["bound_by"] or "{}").items():
                bd[k] = bd.get(k, 0) + v
        ucr = [n(r["UCR"]) for r in g]
        desc[f"{law}|L{sz}|{arm}"] = {
            "n_blocks_ITT": len(g),
            "SURVIVAL_ITT": sum(1 for r in g if r["SURVIVAL_ITT"] == "True"),
            "SPLIT": sum(1 for r in g if r["SPLIT"] == "True"),
            "DISSOLUTION": sum(1 for r in g if r["DISSOLUTION"] == "True"),
            "failure_types": {k: sum(1 for r in g if r["first_failure_type"] == k)
                              for k in sorted({r["first_failure_type"] for r in g})},
            "UCR_median": med(ucr), "UCR_ci": boot(ucr),
            "attempted_over_M256": med([n(r["attempted_over_M256"]) for r in g]),
            "delivered_over_M256": med([n(r["delivered_over_M256"]) for r in g]),
            "delivered_range": (min(n(r["delivered_over_M256"]) for r in g),
                                max(n(r["delivered_over_M256"]) for r in g)),
            "source_realized_over_M256": med([n(r["source_realized_over_M256"]) for r in g]),
            "incumbent_removed_once_over_M256": med([n(r["incumbent_removed_over_M256"])
                                                     for r in g]),
            "fresh_retained_over_M256": med([n(r["fresh_over_M256"]) for r in g]),
            "futile_fraction": med([n(r["futile_fraction"]) for r in g]),
            "UCR_per_1000_steps": med([n(r["UCR_per_1000_steps"]) for r in g]),
            "UCR_per_attempted": med([n(r.get("UCR_per_attempted")) for r in g]),
            "UCR_per_delivered": med([n(r.get("UCR_per_delivered")) for r in g]),
            "incumbent_displacement": med([n(r.get("incumbent_displacement")) for r in g]),
            "terminal_I_over_I0": med([n(r.get("terminal_I_over_I0")) for r in g]),
            "terminal_T_over_M256": med([n(r.get("terminal_T_over_M256")) for r in g]),
            "tracker_sweep_abs_over_M256": med([(n(r.get("CUM_ABS_SWEEP")) or 0) / n(r["M256"])
                                                for r in g]),
            "fixed_frame_mass_in_C256_over_M256":
                med([(n(r.get("terminal_mass_in_frozen_C256")) or None) and
                     n(r["terminal_mass_in_frozen_C256"]) / n(r["M256"]) for r in g]),
            "intersection_jaccard_C256_Ct": med([n(r.get("terminal_jaccard_C256_Ct"))
                                                 for r in g]),
            "shadow55_alive": sum(1 for r in g if r.get("terminal_shadow_55_alive") == "True"),
            "shadow50_alive": sum(1 for r in g if r.get("terminal_shadow_50_alive") == "True"),
            "n_events": med([n(r["n_events"]) for r in g]),
            "n_rejected": med([n(r["n_rejected"]) for r in g]),
            "reject_causes": causes, "bound_by": bd,
            "max_identity_residual": max(n(r["max_identity_residual"]) or 0 for r in g)}
OUT["DESCRIPTIVE"] = desc

# ------------------------------------------------------- dose equivalence check
eq = {}
eq_ok = {}
for law, sz in CELLS:
    a = {r["block"]: n(r["delivered_over_M256"]) for r in cell(law, sz, "PARENT_Q_REPLAY")}
    b = {r["block"]: n(r["delivered_over_M256"]) for r in cell(law, sz, "FLOOR_Q_REPLAY")}
    common = sorted(set(a) & set(b))
    ratios = [b[k] / a[k] for k in common if a[k] and a[k] > 0]
    m = med(ratios)
    ci = boot(ratios)
    ok = (m is not None and MARGIN_IN[0] <= m <= MARGIN_IN[1]
          and ci[0] is not None and MARGIN_CI[0] <= ci[0] and ci[1] <= MARGIN_CI[1])
    eq_ok[(law, sz)] = ok
    eq[f"{law}|L{sz}"] = {"n_blocks": len(ratios), "median_ratio": m, "ci": ci,
                          "range": (min(ratios), max(ratios)) if ratios else None,
                          "PARENT_Q_REPLAY_delivered": med(list(a.values())),
                          "FLOOR_Q_REPLAY_delivered": med(list(b.values())),
                          "attempted_identical": med(
                              [n(r["attempted_over_M256"]) for r in cell(law, sz, "PARENT_Q_REPLAY")])
                          == med([n(r["attempted_over_M256"]) for r in cell(law, sz, "FLOOR_Q_REPLAY")]),
                          "EQUIVALENCE_PASSES": ok}
OUT["DOSE_EQUIVALENCE"] = {"margin_inner": MARGIN_IN, "margin_ci": MARGIN_CI, "detail": eq,
                           "PASSES_EVERYWHERE": all(eq_ok.values()),
                           "PASSES_UNDER_LAW_29": all(v for (l, s), v in eq_ok.items()
                                                      if l == "LAW_29")}

# --------------------------------------------------------------- four contrasts
def contrast(law, sz, a_arm, b_arm):
    a = {r["block"]: r for r in cell(law, sz, a_arm)}
    b = {r["block"]: r for r in cell(law, sz, b_arm)}
    common = sorted(set(a) & set(b))
    sa = sum(1 for k in common if a[k]["SURVIVAL_ITT"] == "True")
    sb = sum(1 for k in common if b[k]["SURVIVAL_ITT"] == "True")
    return {"n_blocks": len(common),
            "survival": {a_arm: f"{sa}/{len(common)}", b_arm: f"{sb}/{len(common)}",
                         "difference": sb - sa, "fisher_p": fisher(sa, sb)},
            "UCR_sign_test": sign([(n(a[k]["UCR"]), n(b[k]["UCR"])) for k in common]),
            "delivered_sign_test": sign([(n(a[k]["delivered_over_M256"]),
                                          n(b[k]["delivered_over_M256"])) for k in common]),
            "splits": {a_arm: sum(1 for k in common if a[k]["SPLIT"] == "True"),
                       b_arm: sum(1 for k in common if b[k]["SPLIT"] == "True")},
            "dissolutions": {a_arm: sum(1 for k in common if a[k]["DISSOLUTION"] == "True"),
                             b_arm: sum(1 for k in common if b[k]["DISSOLUTION"] == "True")}}


con = {}
for law, sz in CELLS:
    con[f"{law}|L{sz}"] = {
        "ALLOCATION  FLOOR_Q_REPLAY - PARENT_Q_REPLAY":
            contrast(law, sz, "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY"),
        "TEMPORAL    PARENT_Q_REPLAY - PARENT_LOW_CONSTANT":
            contrast(law, sz, "PARENT_LOW_CONSTANT", "PARENT_Q_REPLAY"),
        "DOSE        PARENT_LOW_CONSTANT - PARENT_FULL":
            contrast(law, sz, "PARENT_FULL", "PARENT_LOW_CONSTANT"),
        "P08_REPLIC  FLOOR_FULL - PARENT_FULL":
            contrast(law, sz, "PARENT_FULL", "FLOOR_FULL")}
OUT["PRIMARY_CONTRASTS"] = con

# ----------------------------------------------------------------- adjudication
def surv(law, sz, arm):
    g = cell(law, sz, arm)
    return sum(1 for r in g if r["SURVIVAL_ITT"] == "True"), len(g)


adj = {}
for law in ("LAW_16", "LAW_29"):
    sizes = [s for (l, s) in CELLS if l == law]
    pf = {s: surv(law, s, "PARENT_FULL")[0] for s in sizes}
    pq = {s: surv(law, s, "PARENT_Q_REPLAY")[0] for s in sizes}
    fq = {s: surv(law, s, "FLOOR_Q_REPLAY")[0] for s in sizes}
    lc = {s: surv(law, s, "PARENT_LOW_CONSTANT")[0] for s in sizes}
    ff = {s: surv(law, s, "FLOOR_FULL")[0] for s in sizes}
    adj[law] = {"PARENT_FULL": pf, "FLOOR_FULL": ff, "PARENT_Q_REPLAY": pq,
                "FLOOR_Q_REPLAY": fq, "PARENT_LOW_CONSTANT": lc,
                "dose_equivalence": {s: eq_ok[(law, s)] for s in sizes}}

eq29 = all(eq_ok[(l, s)] for (l, s) in CELLS if l == "LAW_29")
eq16 = all(eq_ok[(l, s)] for (l, s) in CELLS if l == "LAW_16")


def better(law, a, b, key="SURVIVAL"):
    """b beats a at both sizes (survival), or on UCR by sign test at both sizes."""
    out = []
    for s in [x for (l, x) in CELLS if l == law]:
        if key == "SURVIVAL":
            out.append(surv(law, s, b)[0] > surv(law, s, a)[0])
        else:
            c = contrast(law, s, a, b)["UCR_sign_test"]
            out.append((c["p"] or 1) < 0.05 and (c["median_diff"] or 0) > 0)
    return all(out)


floor_helps29 = better("LAW_29", "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY")
floor_harms16 = any(contrast("LAW_16", s, "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY")
                    ["survival"]["difference"] < 0
                    or contrast("LAW_16", s, "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY")
                    ["splits"]["FLOOR_Q_REPLAY"] >= 7
                    for s in ("24", "32"))
lowconst_rescues29 = all(surv("LAW_29", s, "PARENT_LOW_CONSTANT")[0]
                         >= 0.75 * surv("LAW_29", s, "FLOOR_FULL")[0] for s in ("24", "32"))
qreplay_rescues29 = all(surv("LAW_29", s, "PARENT_Q_REPLAY")[0]
                        > surv("LAW_29", s, "PARENT_FULL")[0] for s in ("24", "32"))
floor_indist_parent29 = all(
    contrast("LAW_29", s, "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY")["survival"]["difference"] == 0
    for s in ("24", "32"))

if not eq29:
    verdict = "FLOOR_SPECIFIC_MECHANISM_NOT_IDENTIFIABLE"
elif floor_helps29 and floor_harms16:
    verdict = "ALLOCATION_SIGN_REVERSAL_ESTABLISHED"
elif lowconst_rescues29 and floor_indist_parent29:
    verdict = "DOSE_THROTTLING_EXPLAINS_RESCUE"
elif qreplay_rescues29 and not lowconst_rescues29:
    verdict = "OPEN_LOOP_AMOUNT_PROFILE_EFFECT"
elif floor_helps29:
    verdict = "MIXED_DOSE_AND_ALLOCATION_MECHANISM"
else:
    verdict = "DOSE_THROTTLING_EXPLAINS_RESCUE"
OUT["ADJUDICATION"] = {
    "survival_by_arm": adj,
    "dose_equivalence_LAW_16": eq16, "dose_equivalence_LAW_29": eq29,
    "floor_beneficial_under_LAW_29": floor_helps29,
    "floor_harmful_under_LAW_16": floor_harms16,
    "low_constant_rescues_LAW_29": lowconst_rescues29,
    "q_replay_rescues_LAW_29": qreplay_rescues29,
    "floor_indistinguishable_from_parent_under_LAW_29": floor_indist_parent29,
    "VERDICT": verdict,
    "maximal_permitted_wording": PROTO["maximal_permitted_wording"]}

Path("p09_summary.json").write_text(json.dumps(OUT, indent=1, default=str))

print("=== EQUIVALENCE DE DOSE (marge scellee: mediane dans [0.847,1.180], IC dans "
      "[0.781,1.280]) ===")
for k, v in eq.items():
    ci = v["ci"]
    print(f"  {k:<14} rapport median {v['median_ratio']:.3f}  IC "
          f"[{ci[0]:.3f},{ci[1]:.3f}]  {'PASS' if v['EQUIVALENCE_PASSES'] else 'ECHEC'}"
          f"   (PARENT {v['PARENT_Q_REPLAY_delivered']:.3f} vs FLOOR "
          f"{v['FLOOR_Q_REPLAY_delivered']:.3f})")
print(f"\n{'cellule':<14}{'bras':<22}{'surv':>6}{'split':>7}{'dissol':>8}{'UCR':>8}"
      f"{'tente':>8}{'delivre':>9}{'inc':>7}{'frais':>7}")
for law, sz in CELLS:
    for arm in ARMS:
        e = desc.get(f"{law}|L{sz}|{arm}")
        if not e:
            continue
        print(f"{law+'|L'+sz:<14}{arm:<22}{e['SURVIVAL_ITT']:>3}/9{e['SPLIT']:>7}"
              f"{e['DISSOLUTION']:>8}{(e['UCR_median'] or 0):>8.4f}"
              f"{e['attempted_over_M256']:>8.3f}{e['delivered_over_M256']:>9.3f}"
              f"{e['incumbent_removed_once_over_M256']:>7.3f}"
              f"{e['fresh_retained_over_M256']:>7.3f}")
    print()
print("VERDICT =", verdict)

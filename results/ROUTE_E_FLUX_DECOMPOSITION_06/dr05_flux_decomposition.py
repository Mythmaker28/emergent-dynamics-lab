"""ROUTE_E_DIRECT_EXCHANGE_FLUX_DECOMPOSITION_06 -- raw-only mechanistic decomposition.

NO scientific engine is imported or stepped. Everything is read from the DEV_05 ledgers.
Every comparison is paired block by block; marginal medians are never subtracted.
"""
from __future__ import annotations
import csv, json, math, statistics as st, sys
from pathlib import Path

SRC = Path("../DR05")
TOL = 1e-9
SIZES = (24, 32)
CLEAN = {24: ["DIRECT_Q100_ANCHOR", "DIRECT_Q200_UNIFORM", "DIRECT_Q400_UNIFORM"],
         32: ["DIRECT_Q100_ANCHOR", "DIRECT_Q200_UNIFORM", "DIRECT_Q400_UNIFORM",
              "DIRECT_Q800_UNIFORM"]}
ALL_ARMS = ["SHAM", "DIRECT_Q100_ANCHOR", "DIRECT_Q200_UNIFORM", "DIRECT_Q400_UNIFORM",
            "DIRECT_Q800_UNIFORM", "DIRECT_Q400_BURST", "SINK_ONLY_Q800", "SOURCE_ONLY_Q800"]

FORBIDDEN = ("edlab", "od_core", "dr_core", "dsc_core", "dr_harness")


def num(v):
    """Explicit parse. Never uses truthiness."""
    if v is None:
        return None
    if isinstance(v, str):
        if v in ("", "None", "nan", "NaN"):
            return None
        try:
            v = float(v)
        except ValueError:
            return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def boolean(v):
    return v == "True" or v is True


def UNDEF(numer, denom):
    if numer is None or denom is None or abs(denom) <= 0.0:
        return None
    return numer / denom


rows = []
for f in ("direct_replacement_rows_a.csv", "direct_replacement_rows_b.csv"):
    rows += list(csv.DictReader(open(SRC / f)))
for r in rows:
    r["size"] = int(r["size"])
SNAP = {(r["size"], r["block"], r["arm"]): json.loads(r["snapshots"]) for r in rows}
ROW = {(r["size"], r["block"], r["arm"]): r for r in rows}
BLOCKS = {L: sorted({r["block"] for r in rows if r["size"] == L}) for L in SIZES}


def snap_at(L, blk, arm, t):
    s = SNAP.get((L, blk, arm), {}).get(str(int(t)))
    if s is None or s.get("track") is not True:
        return None
    return s


# =============================================== 2+3. paired flux decomposition
paired = []
pair_fail = 0
for L in SIZES:
    for blk in BLOCKS[L]:
        for arm in ALL_ARMS:
            if arm == "SHAM":
                continue
            r = ROW.get((L, blk, arm))
            if r is None:
                continue
            M = num(r["M256"]); I0 = num(r["I0"])
            term = int(num(r["terminal_time"]))
            tr = snap_at(L, blk, arm, term)
            sh = snap_at(L, blk, "SHAM", term)
            e = {"size": L, "block": blk, "arm": arm, "terminal_time": term, "M256": M, "I0": I0,
                 "sham_matched": sh is not None, "treated_track_alive": tr is not None}
            if tr is None or sh is None:
                e.update({k: None for k in ("INCUMBENT_EXCESS_EGRESS", "FRESH_PRESENT",
                                            "AMBIENT_DELTA", "TOTAL_MASS_DELTA",
                                            "PAIR_IDENTITY_RESIDUAL", "I_over_I0_treated",
                                            "I_over_T_treated", "F_over_T_treated",
                                            "A_over_T_treated", "T_over_M256_treated",
                                            "I_over_I0_sham", "A_over_T_sham")})
                e["status"] = ("TREATED_TRACK_LOST" if tr is None else "SHAM_NOT_MATCHED")
                paired.append(e)
                continue
            It, Ft, At, Tt = tr["I"], tr["F"], tr["A"], tr["T"]
            Is, As, Ts = sh["I"], sh["A"], sh["T"]
            exc = (Is - It) / M
            frp = Ft / M
            amb = (At - As) / M
            tmd = (Tt - Ts) / M
            # T = I + F + A holds in both arms, so the four terms must close exactly
            resid = (Is - It) - (Ft + (At - As) - (Tt - Ts))
            if abs(resid) > 1e-9:
                pair_fail += 1
            e.update({"INCUMBENT_EXCESS_EGRESS": exc, "FRESH_PRESENT": frp,
                      "AMBIENT_DELTA": amb, "TOTAL_MASS_DELTA": tmd,
                      "PAIR_IDENTITY_RESIDUAL": resid,
                      "I_over_I0_treated": It / I0, "I_over_T_treated": It / Tt,
                      "F_over_T_treated": Ft / Tt, "A_over_T_treated": At / Tt,
                      "T_over_M256_treated": Tt / M,
                      "I_over_I0_sham": Is / I0, "A_over_T_sham": As / Ts,
                      "status": "OK"})
            paired.append(e)
with (Path("dr05_paired_flux_rows.csv")).open("w", newline="") as h:
    f = sorted({k for e in paired for k in e})
    w = csv.DictWriter(h, fieldnames=f); w.writeheader(); w.writerows(paired)
PAIR_IDENTITY = "PASS" if pair_fail == 0 else "FAIL"

# =========================================================== 2. risk sets
risk = []
for L in SIZES:
    for arm in ALL_ARMS:
        g = [ROW[(L, b, arm)] for b in BLOCKS[L] if (L, b, arm) in ROW]
        itt = len(g)
        intact = sum(1 for r in g if boolean(r["same_track_continuous"]))
        loss = sum(1 for r in g if boolean(r["loss"]))
        merged = sum(1 for r in g if boolean(r["merger"]))
        split = sum(1 for r in g if boolean(r["split"]))
        term_alive = sum(1 for r in g if snap_at(L, r["block"], arm,
                                                 int(num(r["terminal_time"]))) is not None)
        ft = sorted({r["first_failure_type"] for r in g})
        risk.append({"size": L, "arm": arm, "INTENTION_TO_TREAT_RISK_SET": itt,
                     "TERMINAL_INTACT_RISK_SET": intact, "TRACK_FAILURES": itt - intact,
                     "loss": loss, "merger": merged, "split": split,
                     "terminal_track_alive": term_alive,
                     "first_failure_types": "|".join(ft),
                     "analysis_label": ("PRIMARY" if arm in CLEAN[L] or arm == "SHAM"
                                        else "SURVIVOR_CONDITIONAL_N_%d" % intact
                                        if intact < itt else "SECONDARY")})
with Path("dr05_failure_risk_sets.csv").open("w", newline="") as h:
    w = csv.DictWriter(h, fieldnames=list(risk[0])); w.writeheader(); w.writerows(risk)

# ============================================= 4. cohort fates from the ledgers
fates = []
for L in SIZES:
    for blk in BLOCKS[L]:
        for arm in ALL_ARMS:
            r = ROW.get((L, blk, arm))
            if r is None:
                continue
            M = num(r["M256"])
            gross_fresh = num(r["realized_source"])
            gross_sink = num(r["realized_sink"])
            inc_rm = num(r["incumbent_removed_total"])
            amb_rm = num(r["ambient_removed_total"])
            fre_rm = num(r["fresh_removed_total"])
            tf = int(num(r["force_end_time"]))
            term = int(num(r["terminal_time"]))
            def F_at(t):
                s = snap_at(L, blk, arm, t)
                return None if s is None else s["F"]
            f_end = F_at(tf) if tf > 0 else None
            f16, f128, f2048 = F_at(tf + 16), F_at(tf + 128), F_at(tf + 2048)
            fates.append({
                "size": L, "block": blk, "arm": arm, "M256": M,
                "GROSS_FRESH_ADDED": gross_fresh, "GROSS_SINK_REMOVAL": gross_sink,
                "INCUMBENT_REMOVED_BY_SINK": inc_rm, "AMBIENT_REMOVED_BY_SINK": amb_rm,
                "FRESH_REMOVED_BY_LATER_SINKS": fre_rm,
                "FRESH_AT_END_OF_FORCE": f_end, "FRESH_AFTER_16": f16,
                "FRESH_AFTER_128": f128, "FRESH_AFTER_2048": f2048,
                "FRESH_WASHOUT_FRACTION": UNDEF(fre_rm, gross_fresh),
                "INCUMBENT_SINK_YIELD": UNDEF(inc_rm, gross_sink),
                "AMBIENT_SINK_YIELD": UNDEF(amb_rm, gross_sink),
                "FRESH_SINK_YIELD": UNDEF(fre_rm, gross_sink),
                "FRESH_TERMINAL_RETENTION": UNDEF(f2048, gross_fresh),
                "FRESH_COAST_RETENTION": UNDEF(f2048, f_end),
                # ---- operator vs dynamics, exact at the terminal ----
                # the operator's net contribution per cohort is known exactly from the ledger
                "OPERATOR_DELTA_TOTAL_MASS": (None if gross_fresh is None or gross_sink is None
                                              else gross_fresh - gross_sink),
                "OPERATOR_DELTA_INCUMBENT": (None if inc_rm is None else -inc_rm),
                "OPERATOR_DELTA_AMBIENT": (None if amb_rm is None else -amb_rm),
                "OPERATOR_DELTA_FRESH": (None if gross_fresh is None or fre_rm is None
                                         else gross_fresh - fre_rm),
            })
# dynamic (non-operator) net change per cohort, at the terminal
for e in fates:
    s = snap_at(e["size"], e["block"], e["arm"], int(num(ROW[(e["size"], e["block"], e["arm"])]
                                                         ["terminal_time"])))
    I0 = num(ROW[(e["size"], e["block"], e["arm"])]["I0"])
    if s is None:
        for k in ("DYNAMIC_NET_INCUMBENT", "DYNAMIC_NET_AMBIENT", "DYNAMIC_NET_FRESH",
                  "DYNAMIC_NET_TOTAL"):
            e[k] = None
        continue
    e["DYNAMIC_NET_INCUMBENT"] = (s["I"] - I0) - e["OPERATOR_DELTA_INCUMBENT"]
    e["DYNAMIC_NET_AMBIENT"] = (s["A"] - 0.0) - e["OPERATOR_DELTA_AMBIENT"]
    e["DYNAMIC_NET_FRESH"] = s["F"] - e["OPERATOR_DELTA_FRESH"]
    e["DYNAMIC_NET_TOTAL"] = (s["T"] - e["M256"]) - e["OPERATOR_DELTA_TOTAL_MASS"]
with Path("dr05_event_cohort_fates.csv").open("w", newline="") as h:
    f = sorted({k for e in fates for k in e})
    w = csv.DictWriter(h, fieldnames=f); w.writeheader(); w.writerows(fates)
FATE = {(e["size"], e["block"], e["arm"]): e for e in fates}

# ================================================= 6. rate effect decomposition
RATE_KEYS = ["I_over_I0", "F_over_T", "A_over_T", "T_over_M256",
             "INCUMBENT_REMOVED_BY_SINK", "FRESH_WASHOUT_FRACTION",
             "FRESH_TERMINAL_RETENTION", "CORE_256_SURVIVAL", "BOUNDARY_256_SURVIVAL",
             "COAST_LOSS"]


def rate_metrics(L, blk, arm):
    r = ROW.get((L, blk, arm))
    if r is None:
        return None
    term = int(num(r["terminal_time"])); tf = int(num(r["force_end_time"]))
    s = snap_at(L, blk, arm, term)
    sf = snap_at(L, blk, arm, tf)
    if s is None:
        return None
    I0 = num(r["I0"]); M = num(r["M256"])
    fa = FATE[(L, blk, arm)]
    return {"I_over_I0": s["I"] / I0, "F_over_T": s["F"] / s["T"], "A_over_T": s["A"] / s["T"],
            "T_over_M256": s["T"] / M,
            "INCUMBENT_REMOVED_BY_SINK": fa["INCUMBENT_REMOVED_BY_SINK"] / M,
            "FRESH_WASHOUT_FRACTION": fa["FRESH_WASHOUT_FRACTION"],
            "FRESH_TERMINAL_RETENTION": fa["FRESH_TERMINAL_RETENTION"],
            "CORE_256_SURVIVAL": s["core_in_track"] / I0,
            "BOUNDARY_256_SURVIVAL": s["bnd_in_track"] / I0,
            "COAST_LOSS": (None if sf is None or sf["F"] <= 0 else 1.0 - s["F"] / sf["F"])}


rate = []
for L in SIZES:
    for blk in BLOCKS[L]:
        u = rate_metrics(L, blk, "DIRECT_Q400_UNIFORM")
        b = rate_metrics(L, blk, "DIRECT_Q400_BURST")
        if u is None or b is None:
            continue
        e = {"size": L, "block": blk}
        for k in RATE_KEYS:
            e[f"uniform_{k}"] = u.get(k)
            e[f"burst_{k}"] = b.get(k)
            e[f"delta_uniform_minus_burst_{k}"] = (None if u.get(k) is None or b.get(k) is None
                                                   else u[k] - b[k])
        rate.append(e)
with Path("dr05_rate_effect_decomposition.csv").open("w", newline="") as h:
    f = sorted({k for e in rate for k in e})
    w = csv.DictWriter(h, fieldnames=f); w.writeheader(); w.writerows(rate)

# =================================================== 7. scaffold time course
scaf = []
for L in SIZES:
    for blk in BLOCKS[L]:
        for arm in ALL_ARMS:
            s = SNAP.get((L, blk, arm))
            if s is None:
                continue
            I0 = num(ROW[(L, blk, arm)]["I0"])
            for t in sorted(int(k) for k in s):
                e = s[str(t)]
                if e.get("track") is not True:
                    scaf.append({"size": L, "block": blk, "arm": arm, "time": t, "track": False})
                    continue
                scaf.append({"size": L, "block": blk, "arm": arm, "time": t, "track": True,
                             "scaffold_cells": e["scaffold_cells"],
                             "scaffold_mass_over_I0": e["scaffold_mass_over_I0"],
                             "CORE_256_SURVIVAL": e["core_in_track"] / I0,
                             "INTERMEDIATE_256_SURVIVAL": e["inter_in_track"] / I0,
                             "BOUNDARY_256_SURVIVAL": e["bnd_in_track"] / I0,
                             "CORE_SHARE_OF_REMAINING_INCUMBENT":
                                 (e["core_in_track"] / e["I"] if e["I"] > 0 else None),
                             "I_over_I0": e["I_over_I0"], "area": e["area"],
                             "cy": e["cy"], "cx": e["cx"]})
with Path("dr05_scaffold_timecourse.csv").open("w", newline="") as h:
    f = sorted({k for e in scaf for k in e})
    w = csv.DictWriter(h, fieldnames=f); w.writeheader(); w.writerows(scaf)

print("artefacts ecrits.  PAIR_IDENTITY =", PAIR_IDENTITY,
      "| lignes appariees:", len(paired), "| fates:", len(fates),
      "| rate pairs:", len(rate), "| scaffold points:", len(scaf))
Path("_pair_identity.json").write_text(json.dumps(
    {"PAIR_IDENTITY": PAIR_IDENTITY, "failures": pair_fail, "n_pairs": len(paired)}))

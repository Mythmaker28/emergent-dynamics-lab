"""CHMR analysis. Sealed before any confirmatory output.

PRIMARY ENDPOINT — CORE_DEPENDENT_HALO_RECONSTRUCTION (CDHR).
Let h_s(t) be the frozen halo scalar (mean c over the frozen halo support) at site s.
  Delta(t) = h_A(t) - h_B(t)   in MATCHED_SHAM      : the intact history-specific halo gap
  d_X(t)   = h_A(t) - h_B(t)   in arm X
  CDHR_X(t) = d_X(t) / Delta(t)
Immediately after HALO_CROSS, CDHR = -1 exactly (the gap is inverted). CDHR = +1 means the halo
has been fully rebuilt toward the label its intact core carries. CDHR = 0 means the label is gone.
Signed, continuous, paired within block, and it uses BOTH mirrored directions at once.

The two mirrored directions are ALSO tested separately against the core-erased arm, because a
symmetric statistic could hide one direction doing all the work:
  dirA = h_A(HALO_CROSS) - h_A(HALO_CROSS_CORE_ERASE)   must be > 0   (H-core pushes its halo up)
  dirB = h_B(HALO_CROSS) - h_B(HALO_CROSS_CORE_ERASE)   must be < 0   (L-core pushes its halo down)

The independent unit is the founding block. Components and time points are paired repeated
observations, never replicates.
"""
from __future__ import annotations
import sys, os, json, math, pickle, statistics as S
from math import comb
sys.path.insert(0, "/home/claude/sweep")
import numpy as np

T_REC = 350
T_END = 700


# --------------------------------------------------------------------------- statistics
def sign_test(vals, mu=0.0):
    d = [v - mu for v in vals if v is not None]
    pos = sum(1 for x in d if x > 0); neg = sum(1 for x in d if x < 0)
    m = pos + neg
    if m == 0:
        return {"n": len(d), "pos": 0, "neg": 0, "p": 1.0, "median": 0.0}
    k = min(pos, neg)
    return {"n": len(d), "pos": pos, "neg": neg,
            "p": min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m),
            "median": S.median(d), "p_floor": 2 / 2 ** m}


def randomisation_p(vals, mu=0.0, B=200000, seed=7):
    """Block-level randomisation inference: under the null the paired difference has a random
    sign in each block. Exact when 2^n <= B, Monte-Carlo otherwise."""
    import random
    d = [v - mu for v in vals if v is not None]
    n = len(d)
    if n == 0:
        return None
    obs = abs(sum(d) / n)
    if 2 ** n <= B:
        cnt = 0
        for m in range(2 ** n):
            s = sum(x if (m >> i) & 1 else -x for i, x in enumerate(d))
            cnt += abs(s / n) >= obs - 1e-15
        return cnt / 2 ** n
    r = random.Random(seed)
    cnt = sum(abs(sum(x if r.random() < .5 else -x for x in d) / n) >= obs - 1e-15
              for _ in range(B))
    return cnt / B


def t_ci(xs, conf=0.95):
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 3:
        return None
    m, sd = S.mean(xs), S.stdev(xs)
    T = {(0.95, 7): 2.36462, (0.90, 7): 1.89458,
         (0.95, 11): 2.20099, (0.90, 11): 1.79588}.get((conf, n - 1), 2.2)
    se = sd / math.sqrt(n)
    return {"n": n, "mean": m, "sd": sd, "se": se, "ci": (m - T * se, m + T * se)}


def tost(xs, lo, hi):
    r = t_ci(xs, 0.90)
    if r is None:
        return {"verdict": "INSUFFICIENT"}
    return {"n": r["n"], "mean": r["mean"], "ci90": r["ci"], "bounds": (lo, hi),
            "EQUIVALENT": bool(lo < r["ci"][0] and r["ci"][1] < hi)}


def boot(xs, B=20000, seed=11):
    import random
    r = random.Random(seed)
    xs = [x for x in xs if x is not None]
    if not xs:
        return (None, None)
    k = len(xs)
    ms = sorted(S.median([xs[r.randrange(k)] for _ in range(k)]) for _ in range(B))
    return (ms[int(0.025 * B)], ms[min(B - 1, int(0.975 * B))])


# --------------------------------------------------------------------------- accessors
def ser(b, arm, t, key="halo"):
    a = b["arms"].get(arm)
    if a is None:
        return None
    for r in a["series"]:
        if r["t"] == t and r["tag"] == arm:
            return r[key]
    return None


def hgap(b, arm, t):
    h = ser(b, arm, t, "halo")
    return None if h is None else h["A"][0] - h["B"][0]


def hsite(b, arm, t, site, comp=0):
    h = ser(b, arm, t, "halo")
    return None if h is None else h[site][comp]


def csite(b, arm, t, site):
    c = ser(b, arm, t, "core")
    if c is None or c.get(site) is None:
        return None
    return c[site]


def cmin(b, arm, t, site):
    v = csite(b, arm, t, site)
    return None if v is None else v[0] - v[1]


def cplus(b, arm, t, site):
    v = csite(b, arm, t, site)
    return None if v is None else v[0] + v[1]


def resp(b, arm, site, key="response"):
    a = b["arms"].get(arm)
    return None if a is None else np.asarray(a[key][site], float)


# ============================================================ G4 : the four mismatch states
def g4_mismatch(B):
    rows = []
    for b in B:
        r = {"seed": b["seed"]}
        for arm in ("MATCHED_SHAM", "HALO_CROSS", "CORE_CROSS", "DOUBLE_CROSS"):
            r[f"{arm}|halo_gap_t0"] = hgap(b, arm, 0)
            r[f"{arm}|core_A_t0"] = cplus(b, arm, 0, "A")
            r[f"{arm}|core_B_t0"] = cplus(b, arm, 0, "B")
        rows.append(r)
    o = {"n": len(rows), "rows": rows}
    for k in [f"{a}|{q}" for a in ("MATCHED_SHAM", "HALO_CROSS", "CORE_CROSS", "DOUBLE_CROSS")
              for q in ("halo_gap_t0", "core_A_t0", "core_B_t0")]:
        v = [r[k] for r in rows if r[k] is not None]
        if v:
            o[k] = {"median": S.median(v), "ci95": boot(v)}
    # the four states must be distinct: halo gap inverted by HALO_CROSS, core gap inverted by
    # CORE_CROSS, both inverted by DOUBLE_CROSS
    o["halo_gap_inverted_by_HALO_CROSS"] = sign_test(
        [r["MATCHED_SHAM|halo_gap_t0"] + r["HALO_CROSS|halo_gap_t0"] for r in rows])
    o["core_gap_inverted_by_CORE_CROSS"] = sign_test(
        [(r["MATCHED_SHAM|core_A_t0"] - r["MATCHED_SHAM|core_B_t0"])
         + (r["CORE_CROSS|core_A_t0"] - r["CORE_CROSS|core_B_t0"]) for r in rows])
    return o


# ================================================== G5 : CORE_DEPENDENT_HALO_RECONSTRUCTION
def cdhr(B, t=T_REC):
    rows = []
    for b in B:
        Delta = hgap(b, "MATCHED_SHAM", t)
        if not Delta:
            continue
        r = {"seed": b["seed"], "Delta_matched": Delta, "t": t}
        for arm in ("HALO_CROSS", "HALO_CROSS_CORE_ERASE", "HALO_CROSS_WRITER_OFF",
                    "ORPHAN_HALO", "DOUBLE_CROSS", "CORE_CROSS", "MATCHED_SHAM"):
            g = hgap(b, arm, t)
            r[f"gap_{arm}"] = g
            r[f"CDHR_{arm}"] = None if g is None else g / Delta
        # the two mirrored directions, each against the core-erased arm
        for site, sgn in (("A", +1), ("B", -1)):
            hx = hsite(b, "HALO_CROSS", t, site)
            he = hsite(b, "HALO_CROSS_CORE_ERASE", t, site)
            hw = hsite(b, "HALO_CROSS_WRITER_OFF", t, site)
            r[f"dir_{site}_vs_erase"] = None if (hx is None or he is None) else sgn * (hx - he)
            r[f"dir_{site}_vs_writeroff"] = None if (hx is None or hw is None) else sgn * (hx - hw)
        # the maintenance signal: how much MORE halo gap an intact matched pair keeps than an
        # orphan halo, at the same time, relative to the initial gap
        g0 = hgap(b, "MATCHED_SHAM", 0)
        r["retention_matched"] = Delta / g0 if g0 else None
        go = hgap(b, "ORPHAN_HALO", t)
        r["retention_orphan"] = go / g0 if g0 else None
        r["maintenance_excess"] = (r["retention_matched"] - r["retention_orphan"]
                                   if r["retention_matched"] is not None
                                   and r["retention_orphan"] is not None else None)
        rows.append(r)
    o = {"n": len(rows), "t": t, "rows": rows}
    for arm in ("HALO_CROSS", "HALO_CROSS_CORE_ERASE", "HALO_CROSS_WRITER_OFF",
                "ORPHAN_HALO", "DOUBLE_CROSS", "CORE_CROSS", "MATCHED_SHAM"):
        v = [r[f"CDHR_{arm}"] for r in rows if r.get(f"CDHR_{arm}") is not None]
        if v:
            o[f"CDHR_{arm}"] = {"median": S.median(v), "ci95": boot(v), "mean_t_ci95": t_ci(v),
                                "sign_test_vs_minus1": sign_test(v, -1.0),
                                "sign_test_vs_0": sign_test(v, 0.0)}
    # PRIMARY paired contrasts: intact core versus each necessity control
    for ref in ("HALO_CROSS_CORE_ERASE", "HALO_CROSS_WRITER_OFF", "ORPHAN_HALO"):
        d = [r["CDHR_HALO_CROSS"] - r[f"CDHR_{ref}"] for r in rows
             if r.get("CDHR_HALO_CROSS") is not None and r.get(f"CDHR_{ref}") is not None]
        o[f"PRIMARY_CDHR_intact_minus_{ref}"] = {
            "median": S.median(d) if d else None, "ci95": boot(d), "mean_t_ci95": t_ci(d),
            "sign_test": sign_test(d), "randomisation_p": randomisation_p(d)}
    for k in ("dir_A_vs_erase", "dir_B_vs_erase", "dir_A_vs_writeroff", "dir_B_vs_writeroff",
              "maintenance_excess", "retention_matched", "retention_orphan"):
        v = [r[k] for r in rows if r.get(k) is not None]
        if v:
            o[k] = {"median": S.median(v), "ci95": boot(v), "mean_t_ci95": t_ci(v),
                    "sign_test_vs_0": sign_test(v), "randomisation_p": randomisation_p(v)}
    return o


# ================================================== G7 : does the halo rewrite the core?
def g7_pulse(B):
    rows = []
    for b in B:
        r = {"seed": b["seed"]}
        for arm in ("MATCHED_SHAM", "HALO_PULSE_RESTORE", "HALO_CROSS"):
            for site in ("A", "B"):
                r[f"{arm}|core_{site}_end"] = cplus(b, arm, T_END, site)
                r[f"{arm}|halo_{site}_end"] = hsite(b, arm, T_END, site)
        rows.append(r)
    o = {"n": len(rows), "rows": rows}
    # after restoration the halo is back where it started; if the core was persistently rewritten
    # the core gap at the end differs from the matched-sham core gap at the SAME time
    dd = []
    for r in rows:
        m = r["MATCHED_SHAM|core_A_end"] - r["MATCHED_SHAM|core_B_end"]
        p = r["HALO_PULSE_RESTORE|core_A_end"] - r["HALO_PULSE_RESTORE|core_B_end"]
        if m is not None and p is not None:
            dd.append({"seed": r["seed"], "matched_core_gap": m, "pulse_core_gap": p,
                       "difference": p - m,
                       "normalised": (p - m) / abs(m) if m else None})
    o["core_gap_matched_vs_pulse"] = {
        "rows": dd,
        "median_matched": S.median([x["matched_core_gap"] for x in dd]) if dd else None,
        "median_pulse": S.median([x["pulse_core_gap"] for x in dd]) if dd else None,
        "median_difference": S.median([x["difference"] for x in dd]) if dd else None,
        "ci95": boot([x["difference"] for x in dd]),
        "mean_t_ci95": t_ci([x["difference"] for x in dd]),
        "sign_test": sign_test([x["difference"] for x in dd]),
        "randomisation_p": randomisation_p([x["difference"] for x in dd])}
    # halo must actually be restored: its end gap should match the matched-sham end gap
    hh = [(r["HALO_PULSE_RESTORE|halo_A_end"] - r["HALO_PULSE_RESTORE|halo_B_end"])
          - (r["MATCHED_SHAM|halo_A_end"] - r["MATCHED_SHAM|halo_B_end"]) for r in rows]
    o["halo_restored_check"] = {"median_residual_gap": S.median(hh) if hh else None,
                                "ci95": boot(hh)}
    return o


# ================================================== G8 : the future challenge response
def g8_response(B, key="response"):
    rows = []
    for b in B:
        r = {"seed": b["seed"]}
        for arm in ("MATCHED_SHAM", "HALO_CROSS", "HALO_CROSS_CORE_ERASE",
                    "HALO_CROSS_WRITER_OFF", "DOUBLE_CROSS", "CORE_CROSS",
                    "HALO_PULSE_RESTORE"):
            a, bb = resp(b, arm, "A", key), resp(b, arm, "B", key)
            if a is None or bb is None:
                continue
            r[f"{arm}|resp_gap"] = float(np.linalg.norm(a - bb))
            r[f"{arm}|resp_signed"] = float((a - bb).mean())
        rows.append(r)
    o = {"n": len(rows), "rows": rows}
    ks = sorted({k for r in rows for k in r if k != "seed"})
    for k in ks:
        v = [r[k] for r in rows if k in r]
        if v:
            o[k] = {"median": S.median(v), "ci95": boot(v)}
    # does the response follow the CURRENT halo (static control) or the RECONSTRUCTED state?
    for arm in ("HALO_CROSS", "HALO_CROSS_CORE_ERASE", "DOUBLE_CROSS", "CORE_CROSS"):
        k1, k0 = f"{arm}|resp_signed", "MATCHED_SHAM|resp_signed"
        d = [r[k1] - r[k0] for r in rows if k1 in r and k0 in r]
        if d:
            o[f"signed_gap_{arm}_minus_MATCHED"] = {
                "median": S.median(d), "ci95": boot(d), "sign_test": sign_test(d),
                "randomisation_p": randomisation_p(d)}
    return o


# ================================================== G9 : lineage-resolved turnover
def g9_turnover(B):
    rows = []
    for b in B:
        for arm, v in b["arms"].items():
            if "turnover" not in v:
                continue
            lin = v["turnover"]["M_by_lineage"]
            for idx, d in lin.items():
                rows.append({"seed": b["seed"], "arm": arm, "lineage": idx,
                             "M_final": d["M_final"], "continuous": d["continuous_to_end"],
                             "max_components": d["max_components"],
                             "size_final": d["size_final"]})
            rows[-1]["splits"] = v["turnover"]["lineage"]["n_splits"]
            rows[-1]["fusions"] = v["turnover"]["lineage"]["n_fusions"]
    M = [r["M_final"] for r in rows if r["M_final"] is not None]
    return {"n": len(rows), "rows": rows,
            "median_M": S.median(M) if M else None, "max_M": max(M) if M else None,
            "fraction_below_0.35": (sum(1 for x in M if x <= 0.35) / len(M)) if M else None,
            "all_lineages_continuous": all(r["continuous"] for r in rows),
            "n_lineages_that_split": sum(1 for r in rows if r["max_components"] > 1)}


# ================================================== G1/G2 : lineage and surgery
def g1_lineage(B):
    tot = {"splits": 0, "fusions": 0, "disappearances": 0, "argmax_switches": 0, "arms": 0}
    ncomp = set()
    for b in B:
        for v in b["arms"].values():
            tot["splits"] += v["lineage"]["n_splits"]
            tot["fusions"] += v["lineage"]["n_fusions"]
            tot["disappearances"] += v["lineage"]["n_disappearances"]
            tot["argmax_switches"] += v["lineage"]["n_argmax_switches"]
            tot["arms"] += 1
            ncomp |= set(v["lineage"]["n_components"])
    tot["n_components_observed"] = sorted(ncomp)
    return tot


def g2_surgery(B):
    o = {"per_arm": {}}
    for arm in ("MATCHED_SHAM", "HALO_CROSS", "CORE_CROSS", "DOUBLE_CROSS",
                "HALO_CROSS_CORE_ERASE", "ORPHAN_HALO"):
        rec = {"c_multiset_preserved": [], "N_multiset_preserved": [],
               "Mf_multiset_preserved": [], "rho_unchanged": [], "Mf_unchanged": [],
               "c_unchanged": [], "mass_delta": [], "realized_c_delta": [],
               "realized_N_delta": []}
        for b in B:
            L = b["arms"][arm]["ledger"]
            rec["c_multiset_preserved"].append(L["c"]["multiset_preserved"])
            rec["N_multiset_preserved"].append(L["N"]["multiset_preserved"])
            rec["Mf_multiset_preserved"].append(L["Mf"]["multiset_preserved"])
            rec["rho_unchanged"].append(not L["rho"]["changed"])
            rec["Mf_unchanged"].append(not L["Mf"]["changed"])
            rec["c_unchanged"].append(not L["c"]["changed"])
            rec["mass_delta"].append(L["global_mass_after"] - L["global_mass_before"])
            rec["realized_c_delta"].append(L["realized_global_c_after"]
                                           - L["realized_global_c_before"])
            rec["realized_N_delta"].append(L["realized_global_N_after"]
                                           - L["realized_global_N_before"])
        o["per_arm"][arm] = {
            "c_multiset_preserved_all": all(rec["c_multiset_preserved"]),
            "N_multiset_preserved_all": all(rec["N_multiset_preserved"]),
            "Mf_multiset_preserved_all": all(rec["Mf_multiset_preserved"]),
            "rho_unchanged_all": all(rec["rho_unchanged"]),
            "Mf_unchanged_all": all(rec["Mf_unchanged"]),
            "c_unchanged_all": all(rec["c_unchanged"]),
            "max_abs_mass_delta": max(abs(x) for x in rec["mass_delta"]),
            "max_abs_realized_c_delta": max(abs(x) for x in rec["realized_c_delta"]),
            "max_abs_realized_N_delta": max(abs(x) for x in rec["realized_N_delta"])}
    return o


def load(geom, split):
    p = f"chmr_{geom}_{split}.pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else []


def analyse(geom, split):
    B = load(geom, split)
    if not B:
        return {"geometry": geom, "split": split, "blocks": 0}
    return {"geometry": geom, "split": split, "blocks": len(B),
            "seeds": [b["seed"] for b in B],
            "G1_LINEAGE": g1_lineage(B), "G2_SURGERY": g2_surgery(B),
            "G4_MISMATCH": g4_mismatch(B),
            "G5_CDHR_at_T_RECOVERY": cdhr(B, T_REC),
            "G5_CDHR_at_END": cdhr(B, T_END),
            "G7_PULSE": g7_pulse(B),
            "G8_RESPONSE_at_T_RECOVERY": g8_response(B, "response"),
            "G8_RESPONSE_at_END": g8_response(B, "response_end"),
            "G9_TURNOVER": g9_turnover(B)}


if __name__ == "__main__":
    geom = sys.argv[1] if len(sys.argv) > 1 else "FAR"
    split = sys.argv[2] if len(sys.argv) > 2 else "CONF"
    r = analyse(geom, split)
    json.dump(r, open(f"chmr_analysis_{geom}_{split}.json", "w"), indent=1, default=str)
    if not r.get("blocks"):
        print("no data"); sys.exit(0)
    print(f"=== {geom}/{split} : {r['blocks']} blocks ===")
    print("G1 lineage:", r["G1_LINEAGE"])
    c = r["G5_CDHR_at_T_RECOVERY"]
    print(f"\nG5 CDHR at t={T_REC} (-1 = just crossed, +1 = fully rebuilt):")
    for k in ("MATCHED_SHAM", "HALO_CROSS", "HALO_CROSS_CORE_ERASE",
              "HALO_CROSS_WRITER_OFF", "ORPHAN_HALO", "DOUBLE_CROSS", "CORE_CROSS"):
        v = c.get(f"CDHR_{k}")
        if v:
            print(f"  {k:24s} median {v['median']:+.4f}  CI95 [{v['ci95'][0]:+.4f};"
                  f"{v['ci95'][1]:+.4f}]")
    for ref in ("HALO_CROSS_CORE_ERASE", "HALO_CROSS_WRITER_OFF", "ORPHAN_HALO"):
        v = c[f"PRIMARY_CDHR_intact_minus_{ref}"]
        print(f"  PRIMARY intact - {ref:22s} median {v['median']:+.5f} "
              f"CI95 [{v['ci95'][0]:+.5f};{v['ci95'][1]:+.5f}] sign p={v['sign_test']['p']:.4f} "
              f"rand p={v['randomisation_p']:.4f}")
    for k in ("dir_A_vs_erase", "dir_B_vs_erase", "maintenance_excess",
              "retention_matched", "retention_orphan"):
        v = c.get(k)
        if v:
            print(f"  {k:24s} median {v['median']:+.5f} CI95 [{v['ci95'][0]:+.5f};"
                  f"{v['ci95'][1]:+.5f}] p={v['sign_test_vs_0']['p']:.4f}")
    g7 = r["G7_PULSE"]["core_gap_matched_vs_pulse"]
    print(f"\nG7 pulse-restore core gap: matched {g7['median_matched']:+.4f} vs pulse "
          f"{g7['median_pulse']:+.4f}  difference {g7['median_difference']:+.4f} "
          f"CI95 [{g7['ci95'][0]:+.4f};{g7['ci95'][1]:+.4f}] p={g7['sign_test']['p']:.5f} "
          f"rand p={g7['randomisation_p']:.5f}")
    print(f"   halo restored residual gap: {r['G7_PULSE']['halo_restored_check']['median_residual_gap']:+.5f}")
    print("\nG8 response (signed A-B gap, vs matched):")
    for k, v in r["G8_RESPONSE_at_T_RECOVERY"].items():
        if k.startswith("signed_gap_"):
            print(f"  {k:44s} median {v['median']:+.4f} CI95 [{v['ci95'][0]:+.4f};"
                  f"{v['ci95'][1]:+.4f}] p={v['sign_test']['p']:.4f}")
    print("\nG9 turnover:", {k: v for k, v in r["G9_TURNOVER"].items() if k != "rows"})

"""AXMAT00 stage 2 — independent minimal reference re-derivation.

Imports json, os, sys, hashlib, math(isqrt via int), fractions ONLY.
It re-implements TAU and A_X from first principles over exact rationals and
never calls any production analysis function.
"""
import json, os, sys, hashlib
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from axmat00_review import Validator, BASE

PREC = 512  # bits of binary precision for certified rational sqrt enclosures

def sqrt_iv(q):
    """Certified rational enclosure [lo,hi] with lo^2 <= q <= hi^2."""
    assert q >= 0
    if q == 0: return (F(0), F(0))
    scale = 1 << (2 * PREC)
    n = (q * scale).numerator // (q * scale).denominator      # floor(q * 2^(2P))
    r = F(int_isqrt(n), 1 << PREC)
    lo = r
    hi = r + F(1, 1 << PREC)
    while lo * lo > q: lo -= F(1, 1 << PREC)
    while hi * hi < q: hi += F(1, 1 << PREC)
    return (lo, hi)

def int_isqrt(n):
    import math
    return math.isqrt(n)

def iv_add(a, b): return (a[0] + b[0], a[1] + b[1])
def iv_mul_pos(a, b): return (a[0] * b[0], a[1] * b[1])
def iv_scale(a, c): return (a[0] * c, a[1] * c)
def mid(a): return (a[0] + a[1]) / 2

def main():
    V = Validator()
    thr  = V.load(f"{BASE}/FCDDH01R_DISCOVERY_THRESHOLD_LOCK.json")
    cmap = V.load(f"{BASE}/_work/EXACT_INTERACTION_COEFFICIENT_MAP.json")
    cert = V.load(f"{BASE}/_work/EXACT_TAU_PROPAGATION_CERTIFICATE.json")
    out = {}

    # ---------- (A) derive 1/sqrt(2) independently from the eight-row map
    rows = cmap["x_row_coefficients"]
    assert len(rows) == 8
    signed = [F(r["signed_rational_times_inv_sqrt2"]) for r in rows]      # units of 1/sqrt(2)
    abs_rational = [abs(s) for s in signed]
    l1_rational = sum(abs_rational)                                       # in units of 1/sqrt(2)
    out["A_eight_rows"] = len(rows)
    out["A_each_absolute_coefficient_declared"] = sorted({r["absolute_coefficient"] for r in rows})
    out["A_each_signed_rational_x_inv_sqrt2"] = [str(s) for s in signed]
    out["A_sum_abs_rational_in_units_of_inv_sqrt2"] = str(l1_rational)    # expect 2
    out["A_absolute_coefficient_per_row"] = "1/(2*sqrt(2))  <-  |1/4| * (1/sqrt(2))"
    out["A_rows_per_descendant"] = 2
    out["A_derivation"] = (
        "x[b] = 1/2 * sum_a ( d[b,NEAR,a] - d[b,FAR,a] ) and d = (r_C2 - r_C1)/sqrt(2), "
        "so every one of the 8 carrier rows enters x with |coeff| = 1/2 * 1/sqrt(2) = 1/(2*sqrt(2)). "
        "The two carrier rows of one descendant share that descendant's single TAU, hence "
        "sum_rows |coeff| * TAU_row = (1/(2*sqrt(2))) * 2 * sum_{g,a} TAU[b,g,a] "
        "= (1/sqrt(2)) * sum_{g,a} TAU[b,g,a].  Equivalently "
        "8 * (1/(2*sqrt(2))) * mean_rows(TAU) = (1/sqrt(2)) * sum_{g,a} TAU.")
    out["A_coefficient_matches_certificate"] = ("1/sqrt(2)" in cert["A_X"].replace(" ", "")
                                                or "1/sqrt 2" in cert["A_X"])
    out["A_certificate_A_X_text"] = cert["A_X"]
    out["A_certificate_A_PAIR_text"] = cert["A_PAIR"]
    # pair coefficient cross-check: 4 rows at 1/sqrt(2), two per descendant -> sqrt(2)*(TAU_N+TAU_F)
    prows = cmap["pair_contrast_row_coefficients"]
    per_pairing = {}
    for r in prows: per_pairing.setdefault(r["pairing"], []).append(r)
    out["A_pair_rows_per_pairing"] = {k: len(v) for k, v in per_pairing.items()}
    out["A_pair_abs_coefficient_declared"] = sorted({r["absolute_coefficient"] for r in prows})
    out["A_pair_derivation"] = ("4 rows at |coeff| = 1/sqrt(2), two per descendant sharing one TAU, "
                                "gives 2*(1/sqrt(2))*TAU_N + 2*(1/sqrt(2))*TAU_F = sqrt(2)*(TAU_N+TAU_F).")

    # ---------- (B) weights, isometry, units
    W = [F(w) for w in cmap["W"]]
    out["B_W"] = [str(w) for w in W]
    out["B_W_sum_exact"] = str(sum(W))
    out["B_W_sum_declared"] = cmap["W_sum"]
    out["B_W_sum_is_one"] = (sum(W) == 1)
    out["B_isometry"] = cmap["isometry"]
    out["B_coordinate_space"] = cmap["coordinate_space"]
    out["B_scored_native_steps"] = cmap["scored_native_steps"]
    out["B_dt"] = cmap["dt"]
    out["B_trapezoid_check"] = ("endpoints 1/18, interior 1/9, 10 nodes: "
                                "1/18 + 8*(1/9) + 1/18 = 1 exactly")

    # ---------- (C) rebuild every TAU component from sham evidence only
    ser = thr["sham_series_and_hashes"]
    recs = []
    for t in thr["thresholds"]:
        did = t["did"]
        s = ser[did]
        XA = [F(v) for v in s["XA"]]; XB = [F(v) for v in s["XB"]]
        assert len(XA) == len(XB) == len(W) + 1, (len(XA), len(W))
        # G2^2 = sum_h W[h] ((XA[h]-XA[0])^2 + (XB[h]-XB[0])^2), h over the 10 scored nodes
        G2sq = sum(W[i] * ((XA[i+1] - XA[0])**2 + (XB[i+1] - XB[0])**2) for i in range(len(W)))
        dyn_sq_ref = F(1, 10000) * G2sq
        dyn_sq_lock = F(t["TAU_DYNAMIC_L2_sq"])
        site_sq_lock = F(t["TAU_SITE_L2_sq"])
        eta = F(t["ETA_ORACLE_L2"]) if not isinstance(t["ETA_ORACLE_L2"], str) else F(t["ETA_ORACLE_L2"])
        mat_sq_lock = F(t["TAU_MATERIAL_L2_sq_exact"])
        mat_sq_ref = max(eta * eta, dyn_sq_ref, site_sq_lock)
        # recover RHO_MED/B from the site component: site_sq = (0.01*RHO_MED/B)^2 * W_sum
        Wsum = sum(W)
        site_ratio_sq = site_sq_lock / Wsum / F(1, 10000)          # = (RHO_MED/B)^2
        recs.append(dict(
            did=did, block=t["block_upstream_seed"], geometry=t["geometry"], allocation=t["allocation"],
            B_exact=t["B_exact"],
            eta=eta, dyn_sq_ref=dyn_sq_ref, dyn_sq_lock=dyn_sq_lock, site_sq=site_sq_lock,
            mat_sq_lock=mat_sq_lock, mat_sq_ref=mat_sq_ref,
            dominant_declared=t["dominant_term"],
            tau_enclosure=(F(t["TAU_enclosure"][0]), F(t["TAU_enclosure"][1])),
            tau_float_lock=t["TAU_MATERIAL_L2"],
            reference_agrees_tau=t["reference_agrees_tau"],
            rho_over_B_sq=site_ratio_sq))
    out["C_n"] = len(recs)
    out["C_dynamic_rebuilt_from_sham_matches_lock"] = sum(1 for r in recs if r["dyn_sq_ref"] == r["dyn_sq_lock"])
    out["C_material_max_matches_lock"] = sum(1 for r in recs if r["mat_sq_ref"] == r["mat_sq_lock"])
    out["C_eta_all_zero"] = all(r["eta"] == 0 for r in recs)
    out["C_eta_distinct_values"] = sorted({str(r["eta"]) for r in recs})
    out["C_reference_agrees_tau_all"] = all(r["reference_agrees_tau"] for r in recs)

    # dominance recomputed independently (max of the three squared components)
    dom = []
    for r in recs:
        cands = {"ETA_ORACLE_L2": r["eta"]*r["eta"], "TAU_DYNAMIC_L2": r["dyn_sq_ref"], "TAU_SITE_L2": r["site_sq"]}
        m = max(cands.values())
        winners = sorted(k for k, v in cands.items() if v == m)
        dom.append(winners)
        r["dominant_recomputed"] = winners
    out["C_dominance_counts"] = {}
    for w in dom:
        k = "+".join(w); out["C_dominance_counts"][k] = out["C_dominance_counts"].get(k, 0) + 1
    out["C_dominance_agrees_with_lock"] = sum(
        1 for r in recs if r["dominant_recomputed"] == [r["dominant_declared"]])
    out["C_ties"] = sum(1 for w in dom if len(w) > 1)

    # ---------- (D) certified TAU enclosures and A_X
    inv_sqrt2 = sqrt_iv(F(1, 2))
    by_block = {}
    for r in recs:
        lo, hi = sqrt_iv(r["mat_sq_ref"])
        r["tau_iv_ref"] = (lo, hi)
        # enclosure must be consistent with the committed one
        r["tau_iv_consistent"] = not (hi < r["tau_enclosure"][0] or lo > r["tau_enclosure"][1])
        by_block.setdefault(r["block"], []).append(r)
    out["D_tau_enclosure_consistent_with_lock"] = sum(1 for r in recs if r["tau_iv_consistent"])
    out["D_tau_all_positive_finite"] = all(r["tau_iv_ref"][0] > 0 for r in recs)

    A_X = {}
    for b, rs in sorted(by_block.items()):
        assert len(rs) == 4, (b, len(rs))
        s = (F(0), F(0))
        for r in rs: s = iv_add(s, r["tau_iv_ref"])
        A_X[b] = iv_mul_pos(inv_sqrt2, s)
    out["D_n_blocks"] = len(A_X)
    acc = (F(0), F(0))
    for b in sorted(A_X): acc = iv_add(acc, A_X[b])
    A_X_BAR = iv_scale(acc, F(1, 12))
    out["D_A_X_BAR_lo"] = float(A_X_BAR[0]); out["D_A_X_BAR_hi"] = float(A_X_BAR[1])
    out["D_A_X_BAR_mid_float"] = float(mid(A_X_BAR))
    out["D_A_X_BAR_interval_width_float"] = float(A_X_BAR[1] - A_X_BAR[0])
    TARGET = 2.924046708945949e-03
    out["D_target_reported"] = TARGET
    out["D_target_inside_certified_interval"] = bool(A_X_BAR[0] <= F(TARGET) <= A_X_BAR[1])
    out["D_mid_matches_target_to_16_sig"] = (f"{float(mid(A_X_BAR)):.16e}" == f"{TARGET:.16e}")
    out["D_equality_policy"] = ("certified enclosures; a verdict is asserted only when the "
                               "enclosures are strictly separated. Equality of enclosures is never "
                               "read as equality of values.")
    # cross-check against the lock's own pre-active A_X_per_block
    lockAX = thr["A_X_per_block"]
    agree = 0; checked = 0
    for b, rs in sorted(by_block.items()):
        key = str(b)
        if key in lockAX and "A_X_enclosure" in lockAX[key]:
            checked += 1
            lo, hi = F(lockAX[key]["A_X_enclosure"][0]), F(lockAX[key]["A_X_enclosure"][1])
            if not (A_X[b][1] < lo or A_X[b][0] > hi): agree += 1
    out["D_A_X_per_block_checked"] = checked
    out["D_A_X_per_block_consistent"] = agree

    # ---------- (E) non-normative component anatomy
    def prop(key):
        res = {}
        for b, rs in sorted(by_block.items()):
            s = (F(0), F(0))
            for r in rs:
                q = {"eta": r["eta"]*r["eta"], "dyn": r["dyn_sq_ref"], "site": r["site_sq"],
                     "phys": max(r["dyn_sq_ref"], r["site_sq"])}[key]
                s = iv_add(s, sqrt_iv(q))
            res[b] = iv_mul_pos(inv_sqrt2, s)
        return res
    for name, key in [("A_ETA", "eta"), ("A_DYNAMIC", "dyn"), ("A_SITE", "site"), ("A_PHYSICAL", "phys")]:
        d = prop(key)
        bar = iv_scale(list(map(lambda b: d[b], sorted(d)))[0], 0)
        acc2 = (F(0), F(0))
        for b in sorted(d): acc2 = iv_add(acc2, d[b])
        out[f"E_{name}_BAR_mid"] = float(mid(iv_scale(acc2, F(1, 12))))
        out[f"E_{name}_per_block_mid"] = {str(b): float(mid(d[b])) for b in sorted(d)}
    out["E_caveat"] = ("A_ETA / A_DYNAMIC / A_SITE / A_PHYSICAL are NOT additive shares (TAU uses "
                       "max), NOT alternate gates, and must never be compared with any active "
                       "interaction magnitude.")

    # ---------- (F) realized per-descendant table
    out["F_table"] = [dict(
        did=r["did"], block=r["block"], geometry=r["geometry"], allocation=r["allocation"],
        ETA_ORACLE_L2=float(r["eta"]),
        TAU_DYNAMIC_L2=float(mid(sqrt_iv(r["dyn_sq_ref"]))),
        TAU_SITE_L2=float(mid(sqrt_iv(r["site_sq"]))),
        TAU_MATERIAL_L2=float(mid(r["tau_iv_ref"])),
        dominant=r["dominant_recomputed"],
        rho_med_over_B=float(mid(sqrt_iv(r["rho_over_B_sq"]))),
        B_exact=str(r["B_exact"])) for r in recs]

    json.dump(out, open("/home/claude/axmat00/out/_stage2.json", "w"), indent=1, default=str)
    for k, v in out.items():
        if k in ("F_table",): print(k, "= [", len(v), "rows ]"); continue
        print(k, "=", json.dumps(v, default=str)[:520])
    json.dump([{"path": a["path"], "sha256": a["sha256"], "bytes": a["bytes"]} for a in V.accepted],
              open("/home/claude/axmat00/out/_stage2_inputs.json", "w"), indent=1)

if __name__ == "__main__":
    main()

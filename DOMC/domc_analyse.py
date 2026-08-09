"""DOMC analysis. Every estimand below is defined BEFORE the prospective split is read, and is
paired within a founding block. The independent unit is the founding block, always. Components,
cells and time points are never pooled as replicates.

THE 2 x 2. Two history assignments realise a fully crossed design within each block:
      DUAL_AB:  site A owns H1, site B owns H2
      DUAL_BA:  site A owns H2, site B owns H1
  so (site, history) -> response is complete:
      (A,H1) = R_A[AB]   (A,H2) = R_A[BA]   (B,H1) = R_B[BA]   (B,H2) = R_B[AB]
  and, by fixture 7, the two assignments have an IDENTICAL global forcing time series.

  d_history = mean( ||(A,H1)-(A,H2)|| , ||(B,H1)-(B,H2)|| )     same site, different history
  d_site    = mean( ||(A,H1)-(B,H1)|| , ||(A,H2)-(B,H2)|| )     same history, different site
  OWNERSHIP = d_history / d_site
"""
from __future__ import annotations
import sys, os, json, pickle, math, statistics as S
from math import comb
sys.path.insert(0, "/home/claude/sweep")
import numpy as np


# ------------------------------------------------------------------------------ statistics
def sign_test(pairs):
    """Exact two-sided sign test on paired (a, b); tests median(b - a) != 0."""
    d = [b - a for a, b in pairs if a is not None and b is not None]
    pos = sum(1 for x in d if x > 0); neg = sum(1 for x in d if x < 0)
    m = pos + neg
    if m == 0:
        return {"n": len(d), "pos": 0, "neg": 0, "p": 1.0, "median_diff": 0.0}
    k = min(pos, neg)
    return {"n": len(d), "pos": pos, "neg": neg,
            "p": min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m),
            "median_diff": S.median(d),
            "min_attainable_p": 2 / 2 ** m}


def boot(xs, B=20000, seed=20260809):
    import random
    r = random.Random(seed)
    xs = [x for x in xs if x is not None]
    if not xs:
        return (None, None)
    k = len(xs)
    ms = sorted(S.median([xs[r.randrange(k)] for _ in range(k)]) for _ in range(B))
    return (ms[int(0.025 * B)], ms[min(B - 1, int(0.975 * B))])


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


def D(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    return float(np.linalg.norm(a - b) / np.sqrt(len(a)))


# ------------------------------------------------------------------------------- accessors
def arm(blk, asg, iv):
    return blk["arms"].get(f"{asg}|{iv}")


def R(blk, asg, iv, site, when):
    a = arm(blk, asg, iv)
    if a is None:
        return None
    w = a[when]
    if not w[f"alive_{site}"]:
        return None
    return np.asarray(w[f"R_{site}"], float)


def SC(blk, asg, iv, site, when, key):
    a = arm(blk, asg, iv)
    if a is None:
        return None
    s = a[when]["scalars"].get(site)
    return None if s is None else s[key]


def MM(blk, asg, iv, site):
    a = arm(blk, asg, iv)
    return None if a is None else a["turn"][f"M_{site}"]


# ------------------------------------------------------------- G1 : the world is a clean pair
def g1_feasibility(blocks):
    ok_found = sum(1 for b in blocks if b["founding"]["PAIR_OK"])
    per_arm = {}
    for b in blocks:
        for k, v in b["arms"].items():
            d = per_arm.setdefault(k, {"t0_both_alive": 0, "turn_both_alive": 0, "n": 0})
            d["n"] += 1
            d["t0_both_alive"] += int(v["t0"]["alive_A"] and v["t0"]["alive_B"])
            d["turn_both_alive"] += int(v["turn"]["alive_A"] and v["turn"]["alive_B"])
    return {"blocks": len(blocks), "founding_pair_ok": ok_found, "per_arm": per_arm,
            "n_components_at_t0": sorted({v["t0"]["n_components"]
                                          for b in blocks for v in b["arms"].values()}),
            "n_components_after_turnover": sorted({v["turn"]["n_components"]
                                                   for b in blocks for v in b["arms"].values()})}


# ------------------------------------------- G2 : material turnover on the frozen criterion
def g2_turnover(blocks, M_LOW=0.35):
    per = {}
    for b in blocks:
        for k, v in b["arms"].items():
            for site in ("A", "B"):
                m = v["turn"][f"M_{site}"]
                if m is None:
                    continue
                per.setdefault(k, []).append(m)
    allm = [x for v in per.values() for x in v]
    return {"M_LOW": M_LOW, "median_M": med(allm), "max_M": max(allm) if allm else None,
            "fraction_below_M_LOW": (sum(1 for x in allm if x <= M_LOW) / len(allm)) if allm else None,
            "per_arm_median": {k: med(v) for k, v in per.items()}}


# ------------------------------------------------ G3 : ownership -- history beats position
def ownership(blocks, when):
    rows = []
    for b in blocks:
        aH1 = R(b, "AB", "NONE", "A", when); aH2 = R(b, "BA", "NONE", "A", when)
        bH1 = R(b, "BA", "NONE", "B", when); bH2 = R(b, "AB", "NONE", "B", when)
        if any(x is None for x in (aH1, aH2, bH1, bH2)):
            rows.append({"seed": b["seed"], "valid": False})
            continue
        dh = 0.5 * (D(aH1, aH2) + D(bH1, bH2))
        ds = 0.5 * (D(aH1, bH1) + D(aH2, bH2))
        rows.append({"seed": b["seed"], "valid": True, "d_history": dh, "d_site": ds,
                     "ratio": dh / ds if ds > 0 else None,
                     "d_hist_A": D(aH1, aH2), "d_hist_B": D(bH1, bH2),
                     "d_site_H1": D(aH1, bH1), "d_site_H2": D(aH2, bH2)})
    ok = [r for r in rows if r["valid"]]
    return {"rows": rows, "n": len(ok),
            "median_d_history": med([r["d_history"] for r in ok]),
            "median_d_site": med([r["d_site"] for r in ok]),
            "median_ratio": med([r["ratio"] for r in ok]),
            "ratio_ci95": boot([r["ratio"] for r in ok]),
            "sign_test_history_gt_site":
                sign_test([(r["d_site"], r["d_history"]) for r in ok])}


# ------------------------------------- G4 : selective erasure and the double dissociation
def erasure(blocks, when):
    rows = []
    for b in blocks:
        base_A = R(b, "AB", "NONE", "A", when); base_B = R(b, "AB", "NONE", "B", when)
        sh_A = R(b, "AB", "ERASE_SHAM", "A", when); sh_B = R(b, "AB", "ERASE_SHAM", "B", when)
        if sh_A is None and arm(b, "AB", "ERASE_SHAM") is None:
            sh_A, sh_B = base_A, base_B          # arm absent: fixture 6 proves it a no-op
        eA_A = R(b, "AB", "ERASE_A", "A", when); eA_B = R(b, "AB", "ERASE_A", "B", when)
        eB_A = R(b, "AB", "ERASE_B", "A", when); eB_B = R(b, "AB", "ERASE_B", "B", when)
        if any(x is None for x in (base_A, base_B, sh_A, sh_B, eA_A, eA_B, eB_A, eB_B)):
            rows.append({"seed": b["seed"], "valid": False}); continue
        rows.append({"seed": b["seed"], "valid": True,
                     "sham_A": D(base_A, sh_A), "sham_B": D(base_B, sh_B),
                     "eraseA_on_A": D(base_A, eA_A), "eraseA_on_B": D(base_B, eA_B),
                     "eraseB_on_A": D(base_A, eB_A), "eraseB_on_B": D(base_B, eB_B)})
    ok = [r for r in rows if r["valid"]]
    return {"rows": rows, "n": len(ok),
            "median": {k: med([r[k] for r in ok]) for k in
                       ("sham_A", "sham_B", "eraseA_on_A", "eraseA_on_B",
                        "eraseB_on_A", "eraseB_on_B")},
            "sham_is_null": {"max_sham_A": max([r["sham_A"] for r in ok], default=None),
                             "max_sham_B": max([r["sham_B"] for r in ok], default=None)},
            "dissoc_A": sign_test([(r["eraseA_on_B"], r["eraseA_on_A"]) for r in ok]),
            "dissoc_B": sign_test([(r["eraseB_on_A"], r["eraseB_on_B"]) for r in ok]),
            "selectivity_A": med([r["eraseA_on_A"] / r["eraseA_on_B"]
                                  for r in ok if r["eraseA_on_B"] > 0]),
            "selectivity_B": med([r["eraseB_on_B"] / r["eraseB_on_A"]
                                  for r in ok if r["eraseB_on_A"] > 0])}


# --------------------------- G5 : the reciprocal permutation exchanges the FUTURE responses
def transfer_fraction(r_cross, r_own, r_oth):
    """Project the post-exchange response onto the axis joining the two owned responses.
    t = 0  : the exchange moved nothing -- the response is not carried by the memory state.
    t = 1  : the exchange moved the response the whole way -- it is fully carried by it.
    The projection is signed and unbounded, so a negative value (moving AWAY from the other
    owner) is reported as such and never clipped."""
    a = np.asarray(r_own, float); b = np.asarray(r_oth, float); c = np.asarray(r_cross, float)
    ab = b - a
    den = float(ab @ ab)
    if den <= 0:
        return None
    return float(((c - a) @ ab) / den)


def crossing(blocks, when, iv="CROSS"):
    rows = []
    for b in blocks:
        aH1 = R(b, "AB", "NONE", "A", when); aH2 = R(b, "BA", "NONE", "A", when)
        bH1 = R(b, "BA", "NONE", "B", when); bH2 = R(b, "AB", "NONE", "B", when)
        cA = R(b, "AB", iv, "A", when); cB = R(b, "AB", iv, "B", when)
        shA = R(b, "AA", "CROSS", "A", when); shB = R(b, "AA", "CROSS", "B", when)
        aaA = R(b, "AA", "NONE", "A", when); aaB = R(b, "AA", "NONE", "B", when)
        if any(x is None for x in (aH1, aH2, bH1, bH2, cA, cB)):
            rows.append({"seed": b["seed"], "valid": False}); continue
        # in DUAL_AB, site A owns H1 and site B owns H2. After the reciprocal permutation the
        # memory that arrives at A is B's, i.e. H2's; the swap index is positive when A's future
        # response has moved TOWARDS the response A shows when it owns H2.
        own_A, oth_A = D(cA, aH1), D(cA, aH2)
        own_B, oth_B = D(cB, bH2), D(cB, bH1)
        scale = 0.5 * (D(aH1, aH2) + D(bH1, bH2))
        tA = transfer_fraction(cA, aH1, aH2)
        tB = transfer_fraction(cB, bH2, bH1)
        r = {"seed": b["seed"], "valid": True,
             "displacement_A": own_A, "displacement_B": own_B,
             "toward_other_A": own_A - oth_A, "toward_other_B": own_B - oth_B,
             "swap_index": ((own_A - oth_A) + (own_B - oth_B)) / (2 * scale) if scale > 0 else None,
             "transfer_A": tA, "transfer_B": tB,
             "transfer": None if (tA is None or tB is None) else 0.5 * (tA + tB),
             "d_history_scale": scale}
        if shA is not None and shB is not None and aaA is not None and aaB is not None:
            r["mech_floor_A"] = D(aaA, shA); r["mech_floor_B"] = D(aaB, shB)
            # the SAME projection applied to the purely mechanical displacement of the sham
            r["transfer_sham_A"] = transfer_fraction(shA, aaA, aH2)
            r["transfer_sham_B"] = transfer_fraction(shB, aaB, bH1)
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    out = {"rows": rows, "n": len(ok), "intervention": iv,
           "PRIMARY_median_transfer_fraction": med([r["transfer"] for r in ok]),
           "PRIMARY_transfer_ci95": boot([r["transfer"] for r in ok]),
           "PRIMARY_sign_test_transfer_positive":
               sign_test([(0.0, r["transfer"]) for r in ok if r["transfer"] is not None]),
           "median_transfer_A": med([r["transfer_A"] for r in ok]),
           "median_transfer_B": med([r["transfer_B"] for r in ok]),
           "median_transfer_sham": med([0.5 * (r["transfer_sham_A"] + r["transfer_sham_B"])
                                        for r in ok if r.get("transfer_sham_A") is not None
                                        and r.get("transfer_sham_B") is not None]),
           "median_swap_index": med([r["swap_index"] for r in ok]),
           "swap_index_ci95": boot([r["swap_index"] for r in ok]),
           "sign_test_swap_positive": sign_test([(0.0, r["swap_index"]) for r in ok
                                                 if r["swap_index"] is not None]),
           "median_displacement": med([0.5 * (r["displacement_A"] + r["displacement_B"])
                                       for r in ok])}
    fl = [0.5 * (r["mech_floor_A"] + r["mech_floor_B"]) for r in ok if "mech_floor_A" in r]
    if fl:
        out["median_mechanical_floor_CROSS_SHAM"] = med(fl)
        out["displacement_over_floor"] = sign_test(
            [(0.5 * (r["mech_floor_A"] + r["mech_floor_B"]),
              0.5 * (r["displacement_A"] + r["displacement_B"]))
             for r in ok if "mech_floor_A" in r])
    return out


# ---------------------------------- G6 : the distinction is not a low-dimensional scalar
CONF = ("mass", "size", "rg", "mean_sig", "specific_uptake", "local_mean_c", "local_mean_N")


def scalar_matching(blocks, when):
    """Paired, within-block: for each site, the response difference between owning H1 and owning
    H2, and the difference of every confounding scalar over the same pair. If a scalar explained
    the response difference, residualising the response on it would remove the difference."""
    rows = []
    for b in blocks:
        for site, a1, a2 in (("A", "AB", "BA"), ("B", "BA", "AB")):
            r1 = R(b, a1, "NONE", site, when); r2 = R(b, a2, "NONE", site, when)
            if r1 is None or r2 is None:
                continue
            row = {"seed": b["seed"], "site": site, "dR": D(r1, r2)}
            for k in CONF + ("m_plus", "m_minus"):
                v1 = SC(b, a1, "NONE", site, when, k); v2 = SC(b, a2, "NONE", site, when, k)
                row["d_" + k] = None if (v1 is None or v2 is None) else v1 - v2
            rows.append(row)
    out = {"rows": rows, "n": len(rows), "median_dR": med([r["dR"] for r in rows])}
    # per-scalar: how much of the response difference could it carry? Report the paired
    # magnitude of each scalar shift, standardised by its own between-block spread.
    det = {}
    for k in CONF + ("m_plus", "m_minus"):
        v = [r["d_" + k] for r in rows if r["d_" + k] is not None]
        if not v:
            continue
        spread = S.pstdev([abs(x) for x in v]) if len(v) > 1 else 0.0
        det[k] = {"median_abs_shift": med([abs(x) for x in v]),
                  "median_signed_shift": med(v),
                  "sign_test_nonzero": sign_test([(0.0, x) for x in v]),
                  "spread": spread}
    out["per_scalar"] = det
    # ridge leave-one-out decode of the OWNED HISTORY from the confounders alone, vs from the
    # response. If the confounders decode the history as well as the response does, the
    # distinction is a scalar effect.
    out["loo"] = _loo_compare(rows)
    return out


def _loo(X, y, lam=1.0):
    X = np.atleast_2d(np.asarray(X, float))
    if X.shape[0] != len(y):
        X = X.T
    keep = X.std(0) > 1e-12
    X = X[:, keep] if keep.any() else X
    if X.size == 0 or X.shape[1] == 0:
        return float("nan")
    X = (X - X.mean(0)) / (X.std(0) + 1e-12)
    n = len(X)
    A = np.column_stack([np.ones(n), X]); I = np.eye(A.shape[1]); I[0, 0] = 0
    P = np.zeros(n)
    for i in range(n):
        m = np.ones(n, bool); m[i] = False
        P[i] = A[i] @ np.linalg.solve(A[m].T @ A[m] + lam * I, A[m].T @ np.asarray(y)[m])
    y = np.asarray(y, float)
    return float(1 - ((y - P) ** 2).sum() / (((y - y.mean()) ** 2).sum() + 1e-12))


def _loo_compare(rows):
    """Target: the SIGN of the (H1 - H2) contrast is +1 by construction for every row, so it
    cannot be decoded. The informative target is the magnitude of the response difference; we
    ask whether the confounding scalar shifts predict it out of sample."""
    y = np.array([r["dR"] for r in rows], float)
    Xc = np.array([[r["d_" + k] if r["d_" + k] is not None else 0.0 for k in CONF]
                   for r in rows], float)
    Xm = np.array([[r["d_" + k] if r["d_" + k] is not None else 0.0
                    for k in ("m_plus", "m_minus")] for r in rows], float)
    return {"R2_response_gap_from_confounding_scalars": _loo(Xc, y),
            "R2_response_gap_from_memory_scalars": _loo(Xm, y), "n": len(rows)}


# ---------------------------------------------------------------------------------- driver
def load(geom, split, pair):
    p = f"domc_{geom}_{split}_{pair}.pkl"
    return pickle.load(open(p, "rb")) if os.path.exists(p) else []


def analyse(geom, split, pair):
    B = load(geom, split, pair)
    if not B:
        return {"geometry": geom, "split": split, "pair": pair, "blocks": 0}
    have = {k for b in B for k in b["arms"]}
    out = {"geometry": geom, "split": split, "pair": pair, "blocks": len(B),
           "arms_present": sorted(have),
           "seeds": [b["seed"] for b in B],
           "G1_dual_feasibility": g1_feasibility(B),
           "G2_material_turnover": g2_turnover(B)}
    for when in ("t0", "turn"):
        out[f"G3_ownership_{when}"] = ownership(B, when)
        out[f"G6_scalar_matching_{when}"] = scalar_matching(B, when)
        if "AB|ERASE_A" in have:
            out[f"G4_selective_erasure_{when}"] = erasure(B, when)
        if "AB|CROSS" in have:
            out[f"G5_reciprocal_cross_{when}"] = crossing(B, when, "CROSS")
        if "AB|CROSS_ROLL" in have:
            out[f"G5b_cross_roll_{when}"] = crossing(B, when, "CROSS_ROLL")
    return out


if __name__ == "__main__":
    geom = sys.argv[1] if len(sys.argv) > 1 else "FAR"
    split = sys.argv[2] if len(sys.argv) > 2 else "DEV"
    pair = sys.argv[3] if len(sys.argv) > 3 else "cc-00"
    r = analyse(geom, split, pair)
    json.dump(r, open(f"domc_analysis_{geom}_{split}_{pair}.json", "w"), indent=1,
              default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print(json.dumps({k: v for k, v in r.items() if not isinstance(v, dict)}, indent=1))
    for k, v in r.items():
        if not isinstance(v, dict):
            continue
        vv = {kk: x for kk, x in v.items() if kk != "rows"}
        print(f"\n### {k}\n" + json.dumps(vv, indent=1, default=str)[:2200])

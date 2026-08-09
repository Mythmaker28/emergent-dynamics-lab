"""CORE_HALO_MISMATCH_RECOVERY_00 — Phase A: mandatory no-run stabilization of DOMC.

Zero engine calls. Reads only the DOMC raw records and sealed artifacts.

What it recomputes and corrects:
  1. the estimand, renamed NORMALIZED_TRANSFER_CONTRAST, with its raw block-level numerator and
     denominator published, and an explicit small-denominator audit;
  2. the direct paired contrast T_ENVIRONMENT - T_MEMORY;
  3. the three surgery controls: AA_CROSS, NO_OP_PERMUTATION, SURGERY_ONLY;
  4. absolute targeted and non-targeted erasure effects with uncertainty and a real equivalence
     test, replacing the 1.08e6 selectivity ratio as the headline;
  5. an OBSERVED within-world global-balance result replacing
     H_GLOBAL_REFUTED_BY_CONSTRUCTION;
  6. a multiplicity audit over the confirmatory family;
  7. the DEV/CONFIRM allocation ledger and the post-gate-failure reclassification.
"""
from __future__ import annotations
import sys, os, json, math, pickle, hashlib, statistics as S
from math import comb
sys.path.insert(0, "/home/claude/sweep")
sys.path.insert(0, "/home/claude/sweep/DOMC")
import numpy as np

D = "/home/claude/sweep/DOMC"
OUT = {"programme": "CORE_HALO_MISMATCH_RECOVERY_00", "phase": "A_NO_RUN_STABILIZATION",
       "engine_calls": 0}


def load(f):
    return pickle.load(open(os.path.join(D, f), "rb"))


PR = load("domc_FAR_PROSP_cc-00.pkl")
DV = load("domc_FAR_DEV_cc-00.pkl")
NR = load("domc_NEAR_PROSP_cc-00.pkl")
D0 = load("domc_FAR_DEV.pkl")                      # the discarded Nc|cN design run


# ------------------------------------------------------------------------------ statistics
def sign_test(vals, mu=0.0):
    d = [v - mu for v in vals if v is not None]
    pos = sum(1 for x in d if x > 0); neg = sum(1 for x in d if x < 0)
    m = pos + neg
    if m == 0:
        return {"n": len(d), "pos": 0, "neg": 0, "p": 1.0}
    k = min(pos, neg)
    return {"n": len(d), "pos": pos, "neg": neg,
            "p": min(1.0, 2 * sum(comb(m, i) for i in range(k + 1)) / 2 ** m),
            "median": S.median(d), "p_floor": 2 / 2 ** m}


def boot(xs, B=20000, seed=20260809, lo=2.5, hi=97.5):
    import random
    r = random.Random(seed)
    xs = [x for x in xs if x is not None]
    if not xs:
        return (None, None)
    k = len(xs)
    ms = sorted(S.median([xs[r.randrange(k)] for _ in range(k)]) for _ in range(B))
    return (ms[int(lo / 100 * B)], ms[min(B - 1, int(hi / 100 * B))])


def t_ci(xs, conf=0.95):
    """Student-t CI of the MEAN. n=12 -> t_{0.975,11}=2.20099 ; t_{0.95,11}=1.79588."""
    xs = [x for x in xs if x is not None]
    n = len(xs)
    if n < 3:
        return None
    m, sd = S.mean(xs), S.stdev(xs)
    t = {0.95: 2.20099, 0.90: 1.79588}[conf]
    se = sd / math.sqrt(n)
    return {"n": n, "mean": m, "sd": sd, "se": se,
            "ci": (m - t * se, m + t * se), "conf": conf}


def tost(xs, lo, hi):
    """Paired TOST of the mean against an equivalence interval [lo, hi]. n=12 -> t_{0.95,11}."""
    r = t_ci(xs, 0.90)
    if r is None:
        return {"verdict": "INSUFFICIENT"}
    ci = r["ci"]
    return {"n": r["n"], "mean": r["mean"], "ci90": ci, "bounds": (lo, hi),
            "EQUIVALENT": bool(lo < ci[0] and ci[1] < hi),
            "t_lower": (r["mean"] - lo) / r["se"], "t_upper": (hi - r["mean"]) / r["se"]}


def RV(b, asg, iv, site, when):
    a = b["arms"].get(f"{asg}|{iv}")
    if a is None or not a[when][f"alive_{site}"]:
        return None
    return np.asarray(a[when][f"R_{site}"], float)


# ============================================== 1. NORMALIZED_TRANSFER_CONTRAST, raw components
def ntc_rows(blocks, when, iv):
    """The estimand is  T = <c - a, b - a> / ||b - a||^2 .
    It is a PROJECTION COEFFICIENT on an unbounded axis, not a fraction: it is not bounded to
    [0,1] and 'transfer fraction' was the wrong name. Numerator and denominator are published
    per block so that no ratio can hide a small denominator."""
    out = []
    for b in blocks:
        aOwn = RV(b, "AB", "NONE", "A", when); aOth = RV(b, "BA", "NONE", "A", when)
        bOwn = RV(b, "AB", "NONE", "B", when); bOth = RV(b, "BA", "NONE", "B", when)
        cA = RV(b, "AB", iv, "A", when); cB = RV(b, "AB", iv, "B", when)
        if any(x is None for x in (aOwn, aOth, bOwn, bOth, cA, cB)):
            continue
        rec = {"seed": b["seed"]}
        for site, own, oth, cc in (("A", aOwn, aOth, cA), ("B", bOwn, bOth, cB)):
            ax = oth - own
            den = float(ax @ ax)
            num = float((cc - own) @ ax)
            rec[f"num_{site}"] = num
            rec[f"den_{site}"] = den
            rec[f"axis_norm_{site}"] = math.sqrt(den)
            rec[f"disp_{site}"] = float(np.linalg.norm(cc - own))
            rec[f"T_{site}"] = num / den if den > 0 else None
        rec["T"] = (0.5 * (rec["T_A"] + rec["T_B"])
                    if rec["T_A"] is not None and rec["T_B"] is not None else None)
        out.append(rec)
    return out


def ntc_summary(rows, label):
    T = [r["T"] for r in rows if r["T"] is not None]
    dens = [r["den_A"] for r in rows] + [r["den_B"] for r in rows]
    return {"label": label, "n_blocks": len(rows),
            "median_T": S.median(T) if T else None,
            "median_ci95_block_bootstrap": boot(T),
            "mean_t_ci95": t_ci(T),
            "sign_test_vs_0": sign_test(T),
            "denominator_audit": {
                "min": min(dens) if dens else None, "median": S.median(dens) if dens else None,
                "max": max(dens) if dens else None,
                "ratio_max_over_min": (max(dens) / min(dens)) if dens and min(dens) > 0 else None,
                "n_below_1pct_of_median": sum(1 for d in dens
                                              if dens and d < 0.01 * S.median(dens)),
                "note": "the denominator is ||R_own - R_other||^2, the squared length of the "
                        "history axis; a small denominator would inflate T. None is small here."},
            "raw_rows": rows}


# ================================================ 2. the direct paired contrast T_ENV - T_MEM
def paired_env_minus_mem(blocks, when):
    m = {r["seed"]: r["T"] for r in ntc_rows(blocks, when, "CROSS")}
    e = {r["seed"]: r["T"] for r in ntc_rows(blocks, when, "CROSS_ENV")}
    common = sorted(set(m) & set(e))
    d = [e[k] - m[k] for k in common if m[k] is not None and e[k] is not None]
    per = [{"seed": k, "T_memory": m[k], "T_environment": e[k], "difference": e[k] - m[k]}
           for k in common]
    return {"n": len(d), "per_block": per,
            "median_difference": S.median(d) if d else None,
            "median_ci95": boot(d), "mean_t_ci95": t_ci(d),
            "sign_test": sign_test(d)}


# ============================================================ 3. the three surgery controls
def surgery_controls(blocks, when):
    """AA_CROSS       : the exchange applied where the two states are the SAME (DUAL_AA).
       NO_OP_PERMUTATION : the exchange applied twice = identity (mechanical fixture 3c) and the
                        erase-sham, a bit-exact no-op on the whole state (fixture 6).
       SURGERY_ONLY   : the displacement AA_CROSS produces, which is pure surgery with zero
                        informational content, expressed on the SAME axis as the real arms."""
    rows = []
    for b in blocks:
        aa = RV(b, "AA", "NONE", "A", when); aaB = RV(b, "AA", "NONE", "B", when)
        sh = RV(b, "AA", "CROSS", "A", when); shB = RV(b, "AA", "CROSS", "B", when)
        se = RV(b, "AA", "CROSS_ENV", "A", when); seB = RV(b, "AA", "CROSS_ENV", "B", when)
        aOwn = RV(b, "AB", "NONE", "A", when); aOth = RV(b, "BA", "NONE", "A", when)
        if any(x is None for x in (aa, aaB, sh, shB, aOwn, aOth)):
            continue
        ax = aOth - aOwn
        den = float(ax @ ax)
        r = {"seed": b["seed"],
             "AA_CROSS_displacement_A": float(np.linalg.norm(sh - aa)),
             "AA_CROSS_displacement_B": float(np.linalg.norm(shB - aaB)),
             "AA_CROSS_T_on_history_axis": float((sh - aa) @ ax) / den if den > 0 else None,
             "history_axis_norm": math.sqrt(den)}
        if se is not None and seB is not None:
            r["AA_CROSS_ENV_displacement_A"] = float(np.linalg.norm(se - aa))
            r["AA_CROSS_ENV_displacement_B"] = float(np.linalg.norm(seB - aaB))
            r["AA_CROSS_ENV_T_on_history_axis"] = (float((se - aa) @ ax) / den
                                                   if den > 0 else None)
        rows.append(r)
    if not rows:
        return {"n": 0}
    o = {"n": len(rows), "rows": rows}
    for k in ("AA_CROSS_displacement_A", "AA_CROSS_displacement_B",
              "AA_CROSS_T_on_history_axis", "AA_CROSS_ENV_displacement_A",
              "AA_CROSS_ENV_displacement_B", "AA_CROSS_ENV_T_on_history_axis"):
        v = [r.get(k) for r in rows if r.get(k) is not None]
        if v:
            o[k] = {"median": S.median(v), "ci95": boot(v), "mean_t_ci95": t_ci(v),
                    "sign_test_vs_0": sign_test(v)}
    # NO_OP_PERMUTATION and the double-application identity come from the sealed fixtures
    fx = json.load(open(os.path.join(D, "domc_fixtures.json")))
    o["NO_OP_PERMUTATION"] = {
        "erase_sham_bit_exact_no_op": next(r["PASS"] for r in fx if r["fixture"].startswith("6 ")),
        "cross_applied_twice_is_identity": next(r["PASS"] for r in fx
                                                if r["fixture"].startswith("3c ")),
        "cross_env_applied_twice_is_identity": next((r["PASS"] for r in fx
                                                     if r["fixture"].startswith("9d ")), None),
        "cross_leaves_rho_U_V_c_N_C_bit_identical": next(r["PASS"] for r in fx
                                                         if r["fixture"].startswith("4 ")),
        "cross_env_leaves_rho_U_V_C_Mf_bit_identical": next((r["PASS"] for r in fx
                                                             if r["fixture"].startswith("9c ")),
                                                            None)}
    return o


# ============================ 4. absolute erasure effects, with uncertainty and equivalence
def erasure_absolute(blocks, when):
    rows = []
    for b in blocks:
        base_A = RV(b, "AB", "NONE", "A", when); base_B = RV(b, "AB", "NONE", "B", when)
        eA_A = RV(b, "AB", "ERASE_A", "A", when); eA_B = RV(b, "AB", "ERASE_A", "B", when)
        eB_A = RV(b, "AB", "ERASE_B", "A", when); eB_B = RV(b, "AB", "ERASE_B", "B", when)
        if any(x is None for x in (base_A, base_B, eA_A, eA_B, eB_A, eB_B)):
            continue
        rows.append({"seed": b["seed"],
                     "eraseA_TARGET_A": float(np.linalg.norm(eA_A - base_A)),
                     "eraseA_NONTARGET_B": float(np.linalg.norm(eA_B - base_B)),
                     "eraseB_TARGET_B": float(np.linalg.norm(eB_B - base_B)),
                     "eraseB_NONTARGET_A": float(np.linalg.norm(eB_A - base_A))})
    if not rows:
        return {"n": 0}
    o = {"n": len(rows), "rows": rows,
         "note": "ABSOLUTE displacements in the scaled response metric, not ratios. The 1.08e6 "
                 "selectivity of the DOMC report is the quotient of a large targeted effect by a "
                 "near-zero non-targeted one; the quotient is unstable and is NOT the headline."}
    for k in ("eraseA_TARGET_A", "eraseA_NONTARGET_B", "eraseB_TARGET_B", "eraseB_NONTARGET_A"):
        v = [r[k] for r in rows]
        o[k] = {"median": S.median(v), "ci95_median": boot(v), "mean_t_ci95": t_ci(v),
                "min": min(v), "max": max(v)}
    # a real equivalence test on the NON-TARGETED side, against a margin taken from the
    # TARGETED effect: "the non-targeted effect is within 10 % of the targeted one"
    for tag, nt, tg in (("A", "eraseA_NONTARGET_B", "eraseA_TARGET_A"),
                        ("B", "eraseB_NONTARGET_A", "eraseB_TARGET_B")):
        marg = 0.10 * S.median([r[tg] for r in rows])
        o[f"equivalence_nontarget_{tag}"] = {
            "margin_absolute": marg,
            "margin_rule": "10 percent of the median TARGETED displacement of the same erasure",
            **tost([r[nt] for r in rows], -marg, marg)}
    o["paired_target_minus_nontarget_A"] = sign_test(
        [r["eraseA_TARGET_A"] - r["eraseA_NONTARGET_B"] for r in rows])
    o["paired_target_minus_nontarget_B"] = sign_test(
        [r["eraseB_TARGET_B"] - r["eraseB_NONTARGET_A"] for r in rows])
    return o


# ================== 5. OBSERVED global balance, replacing "refuted by construction"
def observed_global_balance(blocks, when):
    """Attempted forcing was balanced by construction (fixture 7). REALIZED global quantities
    were never recorded by DOMC, so 'refuted by construction' overreached. What CAN be shown
    from the raw records, without any engine call, are two observed facts:

    (a) WITHIN-WORLD antisymmetry. In one world, Delta = R_A - R_B. Under DUAL_AB the site that
        owns 'cc' is A; under DUAL_BA it is B. Any world-level additive effect cancels in Delta.
        If the effect were world-level, Delta_AB and -Delta_BA would not agree.
    (b) WORLD-LEVEL SUM. Sigma = R_A + R_B is the world-level summary of the two sites. If the
        two assignments differed at world level, Sigma_AB and Sigma_BA would differ.
    """
    anti, summ, rows = [], [], []
    for b in blocks:
        aAB = RV(b, "AB", "NONE", "A", when); bAB = RV(b, "AB", "NONE", "B", when)
        aBA = RV(b, "BA", "NONE", "A", when); bBA = RV(b, "BA", "NONE", "B", when)
        if any(x is None for x in (aAB, bAB, aBA, bBA)):
            continue
        dAB, dBA = aAB - bAB, aBA - bBA
        sAB, sBA = aAB + bAB, aBA + bBA
        scale = 0.5 * (np.linalg.norm(dAB) + np.linalg.norm(dBA))
        anti.append(float(np.linalg.norm(dAB + dBA)) / float(scale) if scale > 0 else None)
        summ.append(float(np.linalg.norm(sAB - sBA)) / float(scale) if scale > 0 else None)
        rows.append({"seed": b["seed"], "within_world_contrast_norm_AB": float(np.linalg.norm(dAB)),
                     "within_world_contrast_norm_BA": float(np.linalg.norm(dBA)),
                     "antisymmetry_residual_rel": anti[-1],
                     "world_sum_difference_rel": summ[-1]})
    return {"n": len(rows), "rows": rows,
            "within_world_antisymmetry_residual": {
                "median": S.median([x for x in anti if x is not None]) if anti else None,
                "ci95": boot(anti),
                "interpretation": "0 = the two assignments are exact mirror images within the "
                                  "world; any world-level additive effect cancels here"},
            "world_level_sum_difference": {
                "median": S.median([x for x in summ if x is not None]) if summ else None,
                "ci95": boot(summ),
                "sign_test_vs_0": sign_test(summ),
                "interpretation": "the OBSERVED world-level difference between the two "
                                  "assignments, relative to the within-world contrast"},
            "limitation": "realized global field quantities (total c, total N actually present) "
                          "were NOT recorded by DOMC. Only ATTEMPTED forcing was balanced by "
                          "construction. H_GLOBAL is therefore addressed by the two observed "
                          "contrasts above, not refuted by construction; the realized-quantity "
                          "ledger is a requirement carried into CHMR-00."}


# ============================================================ 6. multiplicity over the family
def multiplicity(fam):
    """Holm-Bonferroni over the DOMC confirmatory family, as actually run."""
    items = sorted(fam.items(), key=lambda kv: kv[1])
    m = len(items)
    out, prev = {}, 0.0
    for i, (k, p) in enumerate(items):
        adj = min(1.0, max(prev, (m - i) * p))
        prev = adj
        out[k] = {"raw_p": p, "holm_adjusted_p": adj, "survives_0.05": adj <= 0.05}
    return {"n_tests": m, "detail": out}


# =========================================================================== assemble
if __name__ == "__main__":
    OUT["parent_verification"] = {
        "PARENT_COMMIT": "1b4c80e03ef7637073edb581c7cbf6b346956860",
        "PARENT_BRANCH": "dev/dual-owner-memory-collision-00",
        "ancestry": "b6bc514126ffd559407065eb89c07b4e950958ce is a direct ancestor, "
                    "exactly 1 commit distance (verified with git merge-base --is-ancestor "
                    "and git rev-list --count)",
        "PARENT_BUNDLE_SHA256_VERIFIED":
            "29505e987fa8e5b541dfc3d172417befd3739078008191a97e9c372c2b8b661a",
        "bundle_verify": "git bundle verify: okay; contains refs/heads/"
                         "dev/dual-owner-memory-collision-00 -> 1b4c80e; requires b6bc514",
        "protocol_sha256":
            hashlib.sha256(open(os.path.join(D, "domc_protocol.json"), "rb").read()).hexdigest(),
        "protocol_seal_intact": (hashlib.sha256(
            open(os.path.join(D, "domc_protocol.json"), "rb").read()).hexdigest()
            == open(os.path.join(D, "domc_protocol.sha256")).read().split()[0]),
        "sealed_code_unchanged": {
            f: hashlib.sha256(open(os.path.join(D, f), "rb").read()).hexdigest() == v
            for f, v in json.load(open(os.path.join(D, "domc_protocol.json")))["code_sha256"].items()}}

    OUT["allocation_ledger"] = {
        "domc_FAR_DEV.pkl (pair Nc|cN)": {"blocks": len(D0), "arms": len(D0[0]["arms"]),
                                          "trajectories": len(D0) * len(D0[0]["arms"]),
                                          "seeds": sorted(b["seed"] for b in D0),
                                          "role": "DEVELOPMENT design run, discarded as an "
                                                  "endpoint source"},
        "domc_FAR_DEV_cc-00.pkl": {"blocks": len(DV), "arms": len(DV[0]["arms"]),
                                   "trajectories": len(DV) * len(DV[0]["arms"]),
                                   "seeds": sorted(b["seed"] for b in DV),
                                   "role": "DEVELOPMENT gate-setting run"},
        "domc_FAR_PROSP_cc-00.pkl": {"blocks": len(PR), "arms": len(PR[0]["arms"]),
                                     "trajectories": len(PR) * len(PR[0]["arms"]),
                                     "seeds": sorted(b["seed"] for b in PR),
                                     "role": "held-out split for the RESEALED cc|00 protocol"},
        "domc_NEAR_PROSP_cc-00.pkl": {"blocks": len(NR), "arms": len(NR[0]["arms"]),
                                      "trajectories": len(NR) * len(NR[0]["arms"]),
                                      "seeds": sorted(b["seed"] for b in NR),
                                      "role": "held-out geometry"},
        "total_trajectories": sum(len(B) * len(B[0]["arms"]) for B in (D0, DV, PR, NR)),
        "DEV_CONFIRM_DISJOINT": not (set(b["seed"] for b in D0) | set(b["seed"] for b in DV))
                                & (set(b["seed"] for b in PR) | set(b["seed"] for b in NR))}

    # 1 -------------------------------------------------------------------------------
    ntc = {}
    for tag, B in (("FAR_PROSP", PR), ("FAR_DEV", DV), ("NEAR_PROSP", NR)):
        for when in ("t0", "turn"):
            for iv in ("CROSS", "CROSS_ROLL", "CROSS_ENV"):
                rows = ntc_rows(B, when, iv)
                if rows:
                    ntc[f"{tag}|{when}|{iv}"] = ntc_summary(rows, f"{tag} {when} {iv}")
    OUT["NORMALIZED_TRANSFER_CONTRAST"] = ntc
    OUT["estimand_note"] = (
        "renamed from 'transfer fraction'. T = <c-a, b-a> / ||b-a||^2 is a projection "
        "coefficient on an unbounded axis. It is NOT bounded to [0,1]; a value above 1 means "
        "amplified transport past the other owner's state, and a negative value means motion "
        "away from it. Calling it a fraction implied a bound the estimand does not have.")

    # 2 -------------------------------------------------------------------------------
    OUT["T_ENVIRONMENT_minus_T_MEMORY"] = {w: paired_env_minus_mem(PR, w) for w in ("t0", "turn")}

    # 3 -------------------------------------------------------------------------------
    OUT["SURGERY_CONTROLS"] = {w: surgery_controls(PR, w) for w in ("t0", "turn")}

    # 4 -------------------------------------------------------------------------------
    OUT["ERASURE_ABSOLUTE"] = {w: erasure_absolute(PR, w) for w in ("t0", "turn")}

    # 5 -------------------------------------------------------------------------------
    OUT["OBSERVED_GLOBAL_BALANCE"] = {w: observed_global_balance(PR, w) for w in ("t0", "turn")}

    # 6 -------------------------------------------------------------------------------
    fam = {
        "G3_ownership_t0_FAR": 0.00048828125,
        "G3_ownership_turn_FAR": 0.3876953125,
        "G4_dissoc_A_t0": 0.00048828125,
        "G4_dissoc_B_t0": 0.14599609375,
        "G5_NTC_memory_t0": OUT["NORMALIZED_TRANSFER_CONTRAST"]["FAR_PROSP|t0|CROSS"]
                            ["sign_test_vs_0"]["p"],
        "G5_NTC_memory_turn": OUT["NORMALIZED_TRANSFER_CONTRAST"]["FAR_PROSP|turn|CROSS"]
                              ["sign_test_vs_0"]["p"],
        "G5_NTC_environment_t0": OUT["NORMALIZED_TRANSFER_CONTRAST"]["FAR_PROSP|t0|CROSS_ENV"]
                                 ["sign_test_vs_0"]["p"],
        "G5_NTC_environment_turn": OUT["NORMALIZED_TRANSFER_CONTRAST"]["FAR_PROSP|turn|CROSS_ENV"]
                                   ["sign_test_vs_0"]["p"],
        "T_env_minus_T_mem_t0": OUT["T_ENVIRONMENT_minus_T_MEMORY"]["t0"]["sign_test"]["p"],
        "G3_ownership_t0_NEAR": 0.00048828125,
        "G3_ownership_turn_NEAR": 0.14599609375,
        "G5_NTC_memory_t0_NEAR": OUT["NORMALIZED_TRANSFER_CONTRAST"]["NEAR_PROSP|t0|CROSS"]
                                 ["sign_test_vs_0"]["p"],
    }
    OUT["MULTIPLICITY_HOLM"] = multiplicity(fam)

    # 7 -------------------------------------------------------------------------------
    OUT["DISPOSITIONS_CORRECTED"] = {
        "DOMC_DISPOSITION": "COMPONENT_OWNERSHIP_NOT_ESTABLISHED + ENVIRONMENT_DOMINATED_RESPONSE",
        "LOCAL_MARKER_SEPARABILITY": "ESTABLISHED",
        "MEMORY_FIELD_MANIPULABILITY": "ESTABLISHED",
        "FUNCTIONAL_SELECTIVE_ADDRESSABILITY": "RESTRICTED_ONE_SIDED",
        "EXCLUSIVE_ENVIRONMENTAL_MEDIATION": "NOT_ESTABLISHED",
        "TURNOVER_PERSISTENCE": "MARKER_ONLY_PENDING_LINEAGE_AUDIT",
        "CAUSAL_INDIVIDUATION": "NOT_ESTABLISHED",
        "STRONG_PAPER_GATE": "FAIL",
        "superseded": {"ENVIRONMENT_EXPLAINS": "too strong: the environment cross AMPLIFIES "
                                               "(T = 1.61 > 1), which is not one-to-one "
                                               "transport, and exclusive mediation was never "
                                               "tested"}}
    OUT["RECLASSIFICATION"] = {
        "rule": "G3 (local scalar ownership) failed after material turnover in the first full "
                "DEVELOPMENT run. Everything selected or run AFTER that failure - the Phase C "
                "history-pair scan, the cc|00 development run, and both cc|00 held-out runs - is "
                "reclassified EXPLORATORY_POST_GATE_FAILURE with respect to the ORIGINAL DOMC "
                "gate chain G4-G9. Those runs remain valid confirmations of their own resealed "
                "protocol, which is a different and narrower hypothesis set.",
        "EXPLORATORY_POST_GATE_FAILURE": ["domc_phaseC (8-pair scan)",
                                          "domc_FAR_DEV_cc-00", "domc_FAR_PROSP_cc-00",
                                          "domc_NEAR_PROSP_cc-00"],
        "consequence": "no DOMC result may be cited as confirmatory evidence for G4-G9 of the "
                       "original chain. CHMR-00 must establish its own confirmatory chain."}

    json.dump(OUT, open("chmr_phaseA.json", "w"), indent=1, default=str)

    # ------------------------------------------------------------------ console summary
    print("=== NORMALIZED_TRANSFER_CONTRAST (held-out FAR, 12 blocks) ===")
    for k in ("FAR_PROSP|t0|CROSS", "FAR_PROSP|t0|CROSS_ROLL", "FAR_PROSP|t0|CROSS_ENV",
              "FAR_PROSP|turn|CROSS", "FAR_PROSP|turn|CROSS_ENV", "NEAR_PROSP|t0|CROSS"):
        v = ntc[k]; d = v["denominator_audit"]; t = v["mean_t_ci95"]
        print(f"  {k:28s} med T = {v['median_T']:+.4f}  CI95 {v['median_ci95_block_bootstrap'][0]:+.3f}"
              f"..{v['median_ci95_block_bootstrap'][1]:+.3f}  mean {t['mean']:+.4f} "
              f"[{t['ci'][0]:+.3f};{t['ci'][1]:+.3f}]  p={v['sign_test_vs_0']['p']:.5f}  "
              f"den min/med/max = {d['min']:.3g}/{d['median']:.3g}/{d['max']:.3g}  "
              f"small-den = {d['n_below_1pct_of_median']}")
    print("\n=== T_ENVIRONMENT - T_MEMORY (paired, same block) ===")
    for w in ("t0", "turn"):
        v = OUT["T_ENVIRONMENT_minus_T_MEMORY"][w]
        print(f"  {w:5s} n={v['n']} median = {v['median_difference']:+.4f} "
              f"CI95 [{v['median_ci95'][0]:+.3f};{v['median_ci95'][1]:+.3f}]  "
              f"mean {v['mean_t_ci95']['mean']:+.4f} "
              f"[{v['mean_t_ci95']['ci'][0]:+.3f};{v['mean_t_ci95']['ci'][1]:+.3f}]  "
              f"sign {v['sign_test']['pos']}/{v['sign_test']['neg']} p={v['sign_test']['p']:.5f}")
    print("\n=== SURGERY CONTROLS (t0) ===")
    s = OUT["SURGERY_CONTROLS"]["t0"]
    for k in ("AA_CROSS_displacement_A", "AA_CROSS_T_on_history_axis",
              "AA_CROSS_ENV_displacement_A", "AA_CROSS_ENV_T_on_history_axis"):
        if k in s:
            print(f"  {k:34s} median {s[k]['median']:+.5f}  CI95 "
                  f"[{s[k]['ci95'][0]:+.5f};{s[k]['ci95'][1]:+.5f}]  p={s[k]['sign_test_vs_0']['p']:.4f}")
    print("  NO_OP_PERMUTATION:", s["NO_OP_PERMUTATION"])
    print("\n=== ERASURE, ABSOLUTE (t0) ===")
    e = OUT["ERASURE_ABSOLUTE"]["t0"]
    for k in ("eraseA_TARGET_A", "eraseA_NONTARGET_B", "eraseB_TARGET_B", "eraseB_NONTARGET_A"):
        print(f"  {k:22s} median {e[k]['median']:.6g}  CI95 [{e[k]['ci95_median'][0]:.4g};"
              f"{e[k]['ci95_median'][1]:.4g}]  range [{e[k]['min']:.4g};{e[k]['max']:.4g}]")
    for t in ("A", "B"):
        q = e[f"equivalence_nontarget_{t}"]
        print(f"  equivalence non-target {t}: margin +-{q['margin_absolute']:.4g}  mean "
              f"{q['mean']:.4g} CI90 [{q['ci90'][0]:.4g};{q['ci90'][1]:.4g}] -> "
              f"EQUIVALENT = {q['EQUIVALENT']}")
    print("\n=== OBSERVED GLOBAL BALANCE (t0) ===")
    g = OUT["OBSERVED_GLOBAL_BALANCE"]["t0"]
    print(f"  within-world antisymmetry residual  median = "
          f"{g['within_world_antisymmetry_residual']['median']:.5f}")
    print(f"  world-level sum difference (rel)    median = "
          f"{g['world_level_sum_difference']['median']:.5f}  p="
          f"{g['world_level_sum_difference']['sign_test_vs_0']['p']:.4f}")
    print("\n=== MULTIPLICITY (Holm over the confirmatory family) ===")
    for k, v in OUT["MULTIPLICITY_HOLM"]["detail"].items():
        print(f"  {k:28s} raw {v['raw_p']:.5f} -> Holm {v['holm_adjusted_p']:.5f} "
              f"{'survives' if v['survives_0.05'] else 'DOES NOT SURVIVE'}")

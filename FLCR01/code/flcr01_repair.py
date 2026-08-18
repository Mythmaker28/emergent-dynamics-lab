"""FLCR01 — the single authorized repair round, after the one adversarial review.

Every accepted finding was re-derived by the operator before being acted on.
"""
from __future__ import annotations
import glob, json, math, os, sys
from math import comb
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flcr01_science as S


def _prof2(kY, muY, c, nx, t1=9000, t2=11000):
    """Both horizons from ONE chain build: M^t1 and M^t2 by binary power."""
    M = S._chain(kY, muY, c, nx)
    A = np.linalg.matrix_power(M, t1)
    B = A @ np.linalg.matrix_power(M, t2 - t1)
    e = np.zeros(M.shape[0]); e[1] = 1.0
    P1, P2 = e @ A, e @ B
    cc = max(int(round(c)), 1)
    p1 = min(1.0, kY * nx * 1.0)
    fb = 1.0 - (math.exp(t1 * cc * math.log1p(-p1)) if p1 < 1 else 0.0)
    return fb, float(1 - P2[0]), float(P2[int(NSTAR):].sum())

REPO = "/home/claude/edl"; OUT = f"{REPO}/FLCR01/out"; RAW = "/home/claude/PQEC01/raw"
W, T, ALPHA, GAMMA, MINEV, CAP, NSTAR = 9000, 11000, 0.5, 0.5, 1.0, 16, 10.0
T_BIRTH = 9000


def phase_a_environment():
    """PQEC01's OWN Phase-A environment, per world — not the grandparent's pooled constants."""
    rows = []
    for p in sorted(glob.glob(f"{RAW}/A_*.npz")):
        z = np.load(p, allow_pickle=True)
        yc = z["ycells"]
        m = yc[:, 0] >= 2000
        rows.append({"world": os.path.basename(p)[:-4],
                     "mean_cand": float(yc[m, 7].mean()), "mean_nX": float(yc[m, 4].mean()),
                     "mean_Q": float(yc[m, 8].mean())})
    return rows


def _binom_two_sided(k, n, p):
    c = lambda j: comb(n, j) * p ** j * (1 - p) ** (n - j)
    lo = sum(c(i) for i in range(0, k + 1))
    hi = 1 - sum(c(i) for i in range(0, k))
    return float(min(1.0, 2 * min(lo, hi)))


def chain_calibration(env):
    """The chain that produced the region, tested against the only two points where the data
    can speak. A model rejected by the data cannot carry a quantitative region."""
    cm, nm = float(np.mean([r["mean_cand"] for r in env])), float(np.mean([r["mean_nX"] for r in env]))
    out = []
    for lab, kY, muY, obs in (("B1", 2.51189e-05, 9.26119e-05, 16),
                              ("B2", 2.15443e-05, 1e-08, 18)):
        old = S._profile(kY, muY, 0.961651, 4.312563)["P_first_birth_by_T"]
        new = S._profile(kY, muY, cm, nm)["P_first_birth_by_T"]
        # world-level: average the per-world prediction instead of predicting at the mean
        pw = float(np.mean([S._profile(kY, muY, r["mean_cand"], r["mean_nX"])["P_first_birth_by_T"]
                            for r in env]))
        out.append({"point": lab, "kY": kY, "muY": muY, "observed_worlds_with_a_birth": obs,
                    "of": 44, "observed_fraction": obs / 44,
                    "predicted_mean_field_GRANDPARENT_constants": old,
                    "p_value_grandparent": _binom_two_sided(obs, 44, old),
                    "predicted_mean_field_PQEC01_constants": new,
                    "p_value_pqec01_mean_field": _binom_two_sided(obs, 44, new),
                    "predicted_world_level_average": pw,
                    "p_value_world_level": _binom_two_sided(obs, 44, pw)})
    return {"PER_POINT": out,
            "MEAN_FIELD_REJECTED": all(o["p_value_pqec01_mean_field"] < 0.05 for o in out),
            "WORLD_LEVEL_REJECTED": all(o["p_value_world_level"] < 0.05 for o in out),
            "MECHANISM": ("P(at least one birth) is CONCAVE in exposure, so predicting at the "
                          "mean exposure over-predicts relative to averaging the per-world "
                          "predictions (Jensen). Discarding world-level dispersion is not a "
                          "presentational shortcut here -- it is what makes the model wrong, and "
                          "it errs in the PERMISSIVE direction."),
            "CONSEQUENCE": ("a chain the data reject at both testable points cannot carry a "
                            "quantitative candidate region. Its output is downgraded to a "
                            "NECESSARY-CONDITION SCREEN: a point outside it is excluded, a point "
                            "inside it is not endorsed.")}


def region_with_world_uncertainty(env):
    gk = [10.0 ** v for v in np.linspace(-6, -2, 41)]
    gm = [10.0 ** v for v in np.linspace(-8, -1, 41)]
    cm = float(np.mean([r["mean_cand"] for r in env]))
    nm = float(np.mean([r["mean_nX"] for r in env]))
    per_world_hits = []
    for r in env:
        hit = set()
        for i, kY in enumerate(gk):
            if kY * CAP * NSTAR > 0.1:
                continue
            for j, muY in enumerate(gm):
                fb, alive, big = _prof2(kY, muY, r["mean_cand"], r["mean_nX"])
                if fb >= .5 and alive >= .5 and big <= .5:
                    hit.add((i, j))
        per_world_hits.append(hit)
    cnt = {}
    for h in per_world_hits:
        for k in h:
            cnt[k] = cnt.get(k, 0) + 1
    n = len(env)
    mean_reg = []
    for i, kY in enumerate(gk):
        if kY * CAP * NSTAR > 0.1:
            continue
        for j, muY in enumerate(gm):
            fb, alive, big = _prof2(kY, muY, cm, nm)
            if fb >= .5 and alive >= .5 and big <= .5:
                mean_reg.append((kY, muY))
    def box(pts):
        if not pts:
            return None
        return {"kY": [min(p[0] for p in pts), max(p[0] for p in pts)],
                "muY": [min(p[1] for p in pts), max(p[1] for p in pts)]}
    core90 = [(gk[i], gm[j]) for (i, j), c in cnt.items() if c >= math.ceil(0.90 * n)]
    inter = [(gk[i], gm[j]) for (i, j), c in cnt.items() if c == n]
    return {
        "UNIT": "one world — the region is evaluated separately in EVERY Phase-A world's own "
                "measured environment, then summarized across worlds",
        "N_WORLDS": n, "GRID": "41 x 41 log points for the per-world sweep",
        "AT_THE_MEASURED_MEAN": {"n_points": len(mean_reg), "box": box(mean_reg)},
        "ROBUST_CORE_90PCT_OF_WORLDS": {"n_points": len(core90), "box": box(core90),
                                        "worlds_required": math.ceil(0.90 * n)},
        "INTERSECTION_OVER_ALL_WORLDS": {"n_points": len(inter), "box": box(inter)},
        "WORLDS_WITH_AN_EMPTY_REGION": int(sum(1 for h in per_world_hits if not h)),
        "L1_HORIZON_CORRECTED": {"declared_T_birth": T_BIRTH, "previously_evaluated_at": T,
                                 "now_evaluated_at": T_BIRTH},
        "NON_EMPTINESS_IS_ROBUST": len(core90) > 0,
        "QUANTITATIVE_BOX_IS_NOT": ("the published box [1.58e-05, 5.62e-04] x [1.00e-08, "
                                    "1.19e-03] was computed at a single imported exposure that "
                                    "is 1.5011x PQEC01's own measured mean. It is withdrawn."),
    }


def composition_correction(env):
    """Which criterion change actually produces the non-emptiness? Not the one claimed."""
    cm = float(np.mean([r["mean_cand"] for r in env]))
    nm = float(np.mean([r["mean_nX"] for r in env]))
    E = float(np.mean([r["mean_Q"] for r in env]))
    gk = [10.0 ** v for v in np.linspace(-6, -2, 81)]
    gm = [10.0 ** v for v in np.linspace(-8, -1, 81)]
    reg = []
    for kY in gk:
        if kY * CAP * NSTAR > 0.1:
            continue
        for muY in gm:
            fb, alive, big = _prof2(kY, muY, cm, nm)
            if fb >= .5 and alive >= .5 and big <= .5:
                reg.append((kY, muY))
    c1 = sum(1 for k, m in reg if k * E * W >= MINEV)
    c2 = sum(1 for k, m in reg if (1 - m) ** T >= 1 - ALPHA)
    c3 = sum(1 for k, m in reg if k * E * W * (1 - m) ** 111.0 <= GAMMA)
    # counterfactuals on the ORIGINAL frozen set
    drop_c2 = sum(1 for kY in gk for muY in gm
                  if kY * E * W >= MINEV and kY * E * W * (1 - muY) ** 111.0 <= GAMMA
                  and kY * CAP * NSTAR <= 0.1)
    drop_c3 = sum(1 for kY in gk for muY in gm
                  if kY * E * W >= MINEV and (1 - muY) ** T >= 1 - ALPHA
                  and kY * CAP * NSTAR <= 0.1)
    return {
        "WITHDRAWN_CLAIM": ("'replacing founder survival by lineage non-extinction is what "
                            "dissolves the contradiction'"),
        "WHY_IT_WAS_WRONG": ("of the region's points, %.1f%% ALREADY satisfy C2_FOUNDER while "
                             "only %.1f%% satisfy C3. The non-emptiness is therefore driven "
                             "mainly by dropping C3 -- the prohibition on a separated second "
                             "centre -- not by replacing the founder gate."
                             % (100 * c2 / max(len(reg), 1), 100 * c3 / max(len(reg), 1))),
        "REGION_POINTS": len(reg),
        "SATISFY_C1": c1, "SATISFY_C2_FOUNDER": c2, "SATISFY_C3": c3,
        "COUNTERFACTUAL_ON_THE_ORIGINAL_FROZEN_SET": {
            "drop_C2_FOUNDER_only": drop_c2, "drop_C3_only": drop_c3,
            "READING": ("dropping C3 alone admits %d grid points; dropping C2_FOUNDER alone "
                        "admits %d. The larger relaxation is C3." % (drop_c3, drop_c2))},
        "WHAT_STILL_STANDS": ("both changes are scientifically justified and neither was chosen "
                              "for its region. C3 forbids the second centre the programme exists "
                              "to detect; C2_FOUNDER imposes particle identity. But the CAUSAL "
                              "attribution in the C2 commit message and the audit was wrong, and "
                              "is corrected here."),
        "L3_TO_L7_NEVER_EVALUATED_IN_THE_REGION": ("the region uses only L1, L2 and the N_STAR "
                                                   "bound. L3, L4 and L5 -- including the "
                                                   "declared C3 replacement -- are measured at "
                                                   "two points and enter no region computation. "
                                                   "The region is therefore a LINEAGE-COUNT "
                                                   "region, not a two-centre region."),
    }


def gate_and_architecture_fixes():
    op = json.load(open(f"{OUT}/FLCR01_STATE_OPERATOR.json"))
    lr = json.load(open(f"{OUT}/FLCR01_LINEAGE_REGIONS.json"))
    meas = lr["TWO_CENTRE_FUNCTIONAL_REGION"]["MEASURED_AT_TWO_POINTS_ONLY"]
    h = op["TWO_CENTRE_HOLD_DURATIONS"]
    return {
        "L4_WAS_DEGENERATE": {
            "definition_used": "P(max two-centre hold >= H_hold) with H_hold = median episode "
                               "length = %.0f steps" % h["median"],
            "why_degenerate": ("every world that ever reached state S held it for at least the "
                               "MEDIAN episode length, so L4 returned exactly L3 at both points "
                               "(%.3f and %.3f). A gate that cannot fail independently of "
                               "another gate is not a gate."
                               % (meas["B1"]["P_hold_ge_H"], meas["B2"]["P_hold_ge_H"])),
            "CORRECTED": ("H_hold must be a high quantile of the episode distribution, declared "
                          "before evaluation. At the frozen TAU_SEP = 125 the same measurement "
                          "gives %.3f and %.3f -- a gate that does discriminate."
                          % (meas["B1"]["P_hold_ge_TAU_FROZEN"],
                             meas["B2"]["P_hold_ge_TAU_FROZEN"])),
            "STATUS": "L4 is WITHDRAWN as evaluated; it is handed to the successor with the "
                      "quantile requirement attached"},
        "L1_AND_L2_ALSO_FAIL_AT_BOTH_POINTS": {
            "L1_first_birth": {"B1": meas["B1"]["P_first_birth"], "B2": meas["B2"]["P_first_birth"],
                               "threshold": 0.5, "fails_at_both": True},
            "L2_lineage_alive": {"B1": meas["B1"]["P_lineage_alive_at_end"],
                                 "B2": meas["B2"]["P_lineage_alive_at_end"],
                                 "threshold": 0.5, "fails_at": "B1 only"},
            "STATEMENT": ("the candidate report named L3's failure but did not say that L1 fails "
                          "at BOTH measured points and L2 fails at B1 -- and L1 and L2 are the "
                          "only gates the region actually uses. Pooled across both points, "
                          "34 of 88 worlds have a birth. This is stated now.")},
        "ARCHITECTURE_TEST_SCORING_CORRECTED": {
            "test_A": {"was": False,
                       "now": "NOT_ESTABLISHED — the evidence cited contained no third-centre "
                              "term at all, so it could not have settled a claim about "
                              "third-centre control"},
            "test_C": {"was": "NOT_ESTABLISHED", "now": "NOT_ESTABLISHED (unchanged)"},
            "WITHDRAWN_SENTENCE": "'none of the five tests A-E holds'",
            "CORRECTED_SENTENCE": ("two of the five tests (A and C) are NOT_ESTABLISHED rather "
                                   "than false; three (B, D, E) do not hold. No test holds, so "
                                   "architecture change remains unjustified -- but the record "
                                   "must not report an open question as a settled negative."),
            "ARCHITECTURE_CHANGE_NECESSITY": "NOT_ESTABLISHED"},
    }


def main():
    env = phase_a_environment()
    cal = chain_calibration(env)
    reg = region_with_world_uncertainty(env)
    comp = composition_correction(env)
    fix = gate_and_architecture_fixes()
    rec = {"SECTION": "FLCR01 single repair round",
           "OPERATOR_REVERIFIED_EVERY_ACCEPTED_FINDING": True,
           "R1_ENVIRONMENT_PROVENANCE": {
               "WAS": {"c": 0.961651, "nX": 4.312563,
                       "source": "pqec01_design.DEV_MEAN_CAND_Y / DEV_MEAN_NX_ORG, measured on "
                                 "MYQBD01's 14 mobile arms — the GRANDPARENT programme"},
               "NOW": {"c": float(np.mean([r["mean_cand"] for r in env])),
                       "nX": float(np.mean([r["mean_nX"] for r in env])),
                       "source": "PQEC01's own 40 Phase-A worlds, event-aligned ycells"},
               "EFFECTIVE_EXPOSURE_WAS": 1 * 4.312563,
               "PQEC01_MEASURED_MEAN_Q": float(np.mean([r["mean_Q"] for r in env])),
               "INFLATION_FACTOR": 4.312563 / float(np.mean([r["mean_Q"] for r in env])),
               "NOTE": ("round(0.961651) = 1 collapsed the candidate pool to a single trial, so "
                        "the chain's effective exposure was nX alone")},
           "R2_CHAIN_CALIBRATION": cal,
           "R3_REGION_WITH_WORLD_LEVEL_UNCERTAINTY": reg,
           "R4_COMPOSITION_CORRECTION": comp,
           "R5_GATE_AND_ARCHITECTURE_FIXES": fix}
    json.dump(rec, open(f"{OUT}/FLCR01_REPAIR.json", "w"), indent=1, default=str)
    print("R1 chain env was c=0.961651 nX=4.312563 (GRANDPARENT); PQEC01's own c=%.6f nX=%.6f; "
          "inflation %.4f" % (rec["R1_ENVIRONMENT_PROVENANCE"]["NOW"]["c"],
                              rec["R1_ENVIRONMENT_PROVENANCE"]["NOW"]["nX"],
                              rec["R1_ENVIRONMENT_PROVENANCE"]["INFLATION_FACTOR"]))
    for o in cal["PER_POINT"]:
        print("R2 %s obs %.4f | mean-field(grandparent) %.4f p=%.2e | mean-field(PQEC01) %.4f "
              "p=%.3f | world-level %.4f p=%.3f"
              % (o["point"], o["observed_fraction"],
                 o["predicted_mean_field_GRANDPARENT_constants"], o["p_value_grandparent"],
                 o["predicted_mean_field_PQEC01_constants"], o["p_value_pqec01_mean_field"],
                 o["predicted_world_level_average"], o["p_value_world_level"]))
    print("R3 region at mean %d | robust core (>=90%% of worlds) %d | intersection over all %d | "
          "worlds with empty region %d"
          % (reg["AT_THE_MEASURED_MEAN"]["n_points"], reg["ROBUST_CORE_90PCT_OF_WORLDS"]["n_points"],
             reg["INTERSECTION_OVER_ALL_WORLDS"]["n_points"], reg["WORLDS_WITH_AN_EMPTY_REGION"]))
    print("   robust core box:", reg["ROBUST_CORE_90PCT_OF_WORLDS"]["box"])
    print("R4 %d points: satisfy C1 %d, C2_FOUNDER %d, C3 %d | drop-C3-only %d vs drop-C2-only %d"
          % (comp["REGION_POINTS"], comp["SATISFY_C1"], comp["SATISFY_C2_FOUNDER"],
             comp["SATISFY_C3"],
             comp["COUNTERFACTUAL_ON_THE_ORIGINAL_FROZEN_SET"]["drop_C3_only"],
             comp["COUNTERFACTUAL_ON_THE_ORIGINAL_FROZEN_SET"]["drop_C2_FOUNDER_only"]))


if __name__ == "__main__":
    main()

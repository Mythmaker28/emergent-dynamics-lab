"""SEAL — repair round (the single permitted one).

Six confirmed defects were returned by the mandatory adversarial review. This script
recomputes, from the delivered raw evidence and the delivered predictor, the numbers needed
to state each defect quantitatively instead of asserting it in prose:

  R1  replication of the birth-flux ablation           -> is the 1.27 pp effect real?
  R2  sensitivity of the prediction to the source intensity (per doubling of B)
  R3  Monte-Carlo standard deviation of the M6 POINT PREDICTIONS themselves
  R4  a zero-physics NULL BASELINE available before OBFOR01, run against the same endpoints
  R5  sensitivity of the historical -5.10 % to the outcome-dependent inclusion rule
  R6  the TOST-style p on a t distribution, and the intervals with the prediction sd propagated

NO SCIENTIFIC ENGINE START. m6_obfor01.simulate_arm is the IDEAL-PROCESS predictor written from
the frozen rules; it is the same object the mission used to build its predictions. The seeds used
here are M6 predictor seeds in a 9xxxxx block, disjoint from every scientific seed register.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import sys

import numpy as np

V = "/home/claude/SEAL01/verify/wc"
OUT = "/home/claude/SEAL01/out"
sys.path.insert(0, f"{V}/OBFOR01/code")
sys.path.insert(0, f"{V}/OBTR01/code")
sys.path.insert(0, f"{V}/OBTC02/code")
sys.path.insert(0, f"{V}/ORR01/code")

import m6_obfor01 as m6                                  # noqa: E402
import metrics_obtc as M                                 # noqa: E402

BURN_IN, HORIZON = 2000, 11000
R_REPLICATES, ARMS_PER_REPLICATE = 16, 30
SEED_BLOCK = 900_000

_B = None
_Q = _MU = None


def wd(v, L):
    v = np.abs(v) % L
    return np.minimum(v, L - v)


# --------------------------------------------------------------------- M6 replication
def _one_replicate(job):
    """(mobile, birth_flux, B_scale, replicate index) -> the M6 point prediction of that
    replicate, i.e. the mean over ARMS_PER_REPLICATE arms of the per-arm median r80."""
    mobile, flux, scale, r = job
    meds = []
    for a in range(ARMS_PER_REPLICATE):
        rng = np.random.default_rng(SEED_BLOCK + 1000 * r + a
                                    + (100_000 if mobile else 0)
                                    + (200_000 if flux == "poisson" else 0)
                                    + (400_000 if scale != 1.0 else 0))
        fr = m6.simulate_arm(36, mobile, _Q, _MU, _B, rng,
                             shared_trajectory=True, birth_flux=flux,
                             B_const=float(_B.mean()) * scale)
        if len(fr):
            meds.append(float(np.median(fr)))
    return float(np.mean(meds))


def _init(b, q, mu):
    global _B, _Q, _MU
    _B, _Q, _MU = b, q, mu


def replicate_all(b, q, mu):
    cache = f"{OUT}/_repair_replicates.npz"
    if os.path.exists(cache):
        z = np.load(cache)
        return {k: z[k] for k in z.files}
    jobs = ([(True, "empirical", 1.0, r) for r in range(R_REPLICATES)]
            + [(True, "poisson", 1.0, r) for r in range(R_REPLICATES)]
            + [(False, "empirical", 1.0, r) for r in range(R_REPLICATES)]
            + [(True, "poisson", 2.0, r) for r in range(R_REPLICATES)])
    with mp.Pool(2, initializer=_init, initargs=(b, q, mu)) as pool:
        vals = pool.map(_one_replicate, jobs, chunksize=1)
    out = {}
    for key, sl in (("mobile_empirical", slice(0, R_REPLICATES)),
                    ("mobile_poisson", slice(R_REPLICATES, 2 * R_REPLICATES)),
                    ("static_empirical", slice(2 * R_REPLICATES, 3 * R_REPLICATES)),
                    ("mobile_poisson_2B", slice(3 * R_REPLICATES, 4 * R_REPLICATES))):
        out[key] = np.asarray(vals[sl], float)
    np.savez(cache, **out)
    return out


def mean_in_window_population(b, q, mu, flux, scale, seeds=(700001, 700002, 700003)):
    """A control for R2: does doubling the Poisson intensity actually double the cloud?"""
    got = []
    for s in seeds:
        rng = np.random.default_rng(s)
        py = np.zeros(0, np.int64)
        px = np.zeros(0, np.int64)
        oy = ox = 0
        ns = []
        for t in range(1, HORIZON + 1):
            n = len(py)
            if n:
                py += rng.binomial(1, q, n) - rng.binomial(1, q, n)
                px += rng.binomial(1, q, n) - rng.binomial(1, q, n)
            oy += int(rng.binomial(1, q)) - int(rng.binomial(1, q))
            ox += int(rng.binomial(1, q)) - int(rng.binomial(1, q))
            nb = int(rng.choice(b)) if flux == "empirical" else \
                int(rng.poisson(float(b.mean()) * scale))
            if nb:
                py = np.concatenate([py, np.full(nb, oy, np.int64)])
                px = np.concatenate([px, np.full(nb, ox, np.int64)])
            n = len(py)
            if n:
                k = rng.random(n) >= mu
                py, px = py[k], px[k]
            if t > BURN_IN and t % 50 == 0:
                ns.append(len(py))
        got.append(float(np.mean(ns)))
    return float(np.mean(got))


# --------------------------------------------------------------------- historical arms
def historical_arms():
    """Every OBDI02/OBTC02 arm, WITHOUT the mission's population filter, so the filter's
    effect can be measured rather than inherited."""
    rows = []
    for root, prefix, mobile, src in ((f"{V}/OBDI02/raw", "L", True, "OBDI02"),
                                      (f"{V}/OBTC02/raw", "S__", False, "OBTC02"),
                                      (f"{V}/OBTC02/raw", "P__", True, "OBTC02")):
        for n in sorted(os.listdir(root)):
            if not n.startswith(prefix):
                continue
            z = np.load(f"{root}/{n}", allow_pickle=True)
            f, fy = z["nX_final"], z["nY_final"]
            fr = [json.loads(str(s)) for s in z["frames"]]
            w = [x for x in fr if x["step"] > BURN_IN]
            v = np.array([x["r80_organiser"] for x in w
                          if x.get("r80_organiser") is not None
                          and np.isfinite(x["r80_organiser"])], float)
            rows.append({"file": n, "src": src, "mobile": mobile, "L": int(f.shape[0]),
                         "nX_final": int(f.sum()), "nY_final": int(fy.sum()),
                         "n_frames": int(len(v)),
                         "median": float(np.median(v)) if len(v) else float("nan")})
    return rows


def ideal_r80(L, mobile, q, mu):
    from kernels_obtr01 import Operator
    op = Operator(q, q if mobile else 0.0, mu, L)
    prof = op.stationary_profile()
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    o = np.argsort(d.ravel(), kind="stable")
    dd, ww = d.ravel()[o], prof.ravel()[o]
    cw = np.cumsum(ww) / ww.sum()
    return float(dd[int(np.searchsorted(cw, 0.8, side="left"))])


def filter_sensitivity(rows, q, mu):
    IDEAL = {(L, m): ideal_r80(L, m, q, mu) for L in (36, 72, 96) for m in (True, False)}
    mob = [r for r in rows if r["mobile"] and r["src"] == "OBDI02" and r["nY_final"] >= 1]

    def resid(rs):
        v = np.array([r["median"] / IDEAL[(r["L"], True)] for r in rs])
        se = v.std(ddof=1) / math.sqrt(len(v))
        return {"n": len(v), "percent": 100 * (v.mean() - 1), "se_percent": 100 * se}

    lv = {}
    lv["A_mission_rule__nX_final_ge_40_and_ge_50_frames"] = resid(
        [r for r in mob if r["nX_final"] >= 40 and r["n_frames"] >= 50])
    lv["B_drop_the_population_threshold__keep_ge_50_frames"] = resid(
        [r for r in mob if r["n_frames"] >= 50])
    lv["C_no_outcome_dependent_threshold_at_all"] = resid(
        [r for r in mob if r["n_frames"] >= 1])
    excl = sorted([r for r in mob
                   if r["n_frames"] >= 50 and r["nX_final"] < 40],
                  key=lambda r: -(r["median"] / IDEAL[(r["L"], True)] - 1))
    return {
        "WHAT_THE_RULE_IS": ("residual_obfor01.py keeps an arm only if nY_final >= 1 AND "
                             "nX_final >= 40 AND at least 50 in-window frames carry a finite "
                             "r80. nX_final is the terminal population: an OUTCOME of the arm, "
                             "not a design variable. Conditioning on it is outcome-dependent "
                             "selection."),
        "LEVELS": lv,
        "BAND_percent": [lv["C_no_outcome_dependent_threshold_at_all"]["percent"],
                         lv["A_mission_rule__nX_final_ge_40_and_ge_50_frames"]["percent"]],
        "ARMS_EXCLUDED_BY_THE_POPULATION_THRESHOLD": [
            {"file": r["file"], "L": r["L"], "nX_final": r["nX_final"],
             "n_frames": r["n_frames"],
             "residual_percent": 100 * (r["median"] / IDEAL[(r["L"], True)] - 1)}
            for r in excl],
        "DIRECTION": ("the excluded arms carry systematically HIGHER residuals, so the rule "
                      "pushes the headline downward. The magnitude of the headline residual "
                      "is therefore partly a property of the inclusion rule."),
        "WHY_THE_SEAL_DID_NOT_CATCH_IT_ALONE": (
            "seal_flow_and_numbers.historical() re-implements the same three conditions "
            "byte-for-byte. Re-executing a filter is a REPRODUCTION of the pipeline, not an "
            "independent check of it. Only varying the rule exposes it."),
    }


def null_baseline(rows, q, mu):
    """The zero-physics predictor available BEFORE OBFOR01: 'the fresh L=36 arms will look
    like the historical L=36 arms'. It uses no kernel, no operator and no simulation."""
    mob36 = [r for r in rows if r["mobile"] and r["src"] == "OBDI02" and r["L"] == 36
             and r["nY_final"] >= 1 and r["nX_final"] >= 40 and r["n_frames"] >= 50]
    sta = [r for r in rows if not r["mobile"] and r["nY_final"] >= 1
           and r["nX_final"] >= 40 and r["n_frames"] >= 50]
    pm = float(np.mean([r["median"] for r in mob36]))
    ps = float(np.mean([r["median"] for r in sta]))
    return {"predicted_static_r80_median": ps, "n_historical_static_arms": len(sta),
            "predicted_mobile_r80_median": pm, "n_historical_mobile_L36_arms": len(mob36),
            "predicted_ratio": pm / ps,
            "AVAILABILITY": ("both numbers are means over arms delivered by OBDI02 and "
                             "OBTC02, both present in the tree at OBTR01's tip 062d3735, "
                             "i.e. before OBFOR01 opened. No information from the 28 fresh "
                             "arms enters."),
            "PHYSICS_CONTENT": "none: no kernel, no operator, no simulation, no mechanism"}


# --------------------------------------------------------------------- statistics
def t_sf(t, df):
    """Upper tail of Student's t, by the regularised incomplete beta, without scipy."""
    t = abs(float(t))
    x = df / (df + t * t)
    return 0.5 * betainc(df / 2.0, 0.5, x)


def betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta) / a
    if x < (a + 1) / (a + b + 2):
        return front * _cf(a, b, x)
    return 1.0 - math.exp(math.log(1 - x) * b + math.log(x) * a - lbeta) / b * _cf(b, a, 1 - x)


def _cf(a, b, x):
    f, c, d = 1.0, 1.0, 0.0
    for i in range(0, 300):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        d = 1e-30 if abs(d) < 1e-30 else d
        d = 1.0 / d
        c = 1.0 + num / c
        c = 1e-30 if abs(c) < 1e-30 else c
        f *= c * d
        if abs(1.0 - c * d) < 1e-12:
            break
    return f - 1.0


def fresh_arm_medians():
    val = json.load(open(f"{V}/OBFOR01/out/_validation.json"))
    S, Mo = [], []
    for a in val["ARMS"]:
        z = np.load(f"{V}/OBFOR01/raw/%s.npz" % a["tag"].replace("/", "__"), allow_pickle=True)
        fr = [json.loads(str(s)) for s in z["frames"]]
        w = [x for x in fr if x["step"] > BURN_IN]
        v = np.array([x["r80_organiser"] for x in w
                      if x.get("r80_organiser") is not None
                      and np.isfinite(x["r80_organiser"])], float)
        (S if a["condition"] == "S" else Mo).append(float(np.median(v)))
    return np.asarray(S), np.asarray(Mo)


def restate_statistics(S, Mo, pred_sd):
    frz = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))
    ep = frz["PRIMARY_PREDICTIONS"]
    delta = frz["RESIDUAL_TOLERANCE"]["EQUIVALENCE_MARGIN_percent"] / 100.0
    ps = ep["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["predicted_r80_median"]
    pm = ep["MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY"]["predicted_r80_median"]
    pr = ep["MOBILE_STATIC_RATIO_COMPATIBILITY"]["predicted_ratio_under_M6"]

    def one(name, v, pred, sd_pred_pc):
        m, n = v.mean(), len(v)
        se = v.std(ddof=1) / math.sqrt(n)
        r, rse = m / pred - 1, se / pred
        df = n - 1
        tcrit = 2.1604 if df == 13 else 1.96
        with_pred = math.sqrt(rse ** 2 + (sd_pred_pc / 100.0) ** 2)
        return {
            "NAME": name, "n": n, "df": df,
            "prediction": pred, "PREDICTION_MONTE_CARLO_SD_percent": sd_pred_pc,
            "observed": float(m), "relative_error_percent": 100 * r,
            "se_relative_percent": 100 * rse,
            "FROZEN_POINT_RULE_percent": 100 * delta,
            "POINT_INSIDE__THE_CRITERION_OF_RECORD": bool(abs(r) <= delta),
            "POST_FREEZE_whole_interval_normal_1p96": 100 * (abs(r) + 1.96 * rse),
            "POST_FREEZE_whole_interval_t_%d_df" % df: 100 * (abs(r) + tcrit * rse),
            "POST_FREEZE_whole_interval_t_with_prediction_sd_propagated":
                100 * (abs(r) + tcrit * with_pred),
            "TOST_p_NORMAL_as_originally_reported":
                float(1 - 0.5 * (math.erf((delta - abs(r)) / (rse * math.sqrt(2))) + 1)),
            "TOST_p_t_%d_df__CORRECTED" % df: float(t_sf((delta - abs(r)) / rse, df)),
        }

    ms, mm = S.mean(), Mo.mean()
    ses, sem = S.std(ddof=1) / math.sqrt(len(S)), Mo.std(ddof=1) / math.sqrt(len(Mo))
    rrel = math.sqrt((sem / mm) ** 2 + (ses / ms) ** 2)
    rr = (mm / ms) / pr - 1
    sd_ratio = math.sqrt(pred_sd["mobile"] ** 2 + pred_sd["static"] ** 2) / 100.0
    ratio = {
        "NAME": "ratio", "n_static": len(S), "n_mobile": len(Mo),
        "prediction": pr, "PREDICTION_MONTE_CARLO_SD_percent": 100 * sd_ratio,
        "observed": float(mm / ms), "relative_error_percent": 100 * rr,
        "se_relative_percent": 100 * rrel,
        "FROZEN_POINT_RULE_percent": 100 * delta,
        "POINT_INSIDE__THE_CRITERION_OF_RECORD": bool(abs(rr) <= delta),
        "POST_FREEZE_whole_interval_normal_1p96": 100 * (abs(rr) + 1.96 * rrel),
        "POST_FREEZE_whole_interval_t_26_df": 100 * (abs(rr) + 2.0555 * rrel),
        "POST_FREEZE_whole_interval_t_with_prediction_sd_propagated":
            100 * (abs(rr) + 2.0555 * math.sqrt(rrel ** 2 + sd_ratio ** 2)),
    }
    return {"static": one("static", S, ps, pred_sd["static"]),
            "mobile": one("mobile", Mo, pm, pred_sd["mobile"]),
            "ratio": ratio}


# --------------------------------------------------------------------- main
def main():
    frz = json.load(open(f"{V}/OBFOR01/out/_freeze.json"))
    pt = frz["FREEZE_MANIFEST"]["frozen_point"]
    q, mu = pt["p_hop"] / 4.0, pt["muX"]
    b, n_hist = m6.empirical_birth_flux(f"{V}/OBDI02/raw", "L", 40)

    print("R1-R3  replicating the M6 point predictions (%d x %d arms x 4 conditions)"
          % (R_REPLICATES, ARMS_PER_REPLICATE))
    rep = replicate_all(b, q, mu)
    print("R2     dose-delivery control")
    pop_B = mean_in_window_population(b, q, mu, "poisson", 1.0)
    pop_2B = mean_in_window_population(b, q, mu, "poisson", 2.0)
    S, Mo = fresh_arm_medians()
    obs_mobile = float(Mo.mean())

    pop_mob = m6.population_r80(36, True, q, mu)
    pop_sta = m6.population_r80(36, False, q, mu)

    def pc(v, pop):
        return 100 * (v / pop - 1)

    me, mp_, ms_, m2b = (pc(rep["mobile_empirical"], pop_mob),
                         pc(rep["mobile_poisson"], pop_mob),
                         pc(rep["static_empirical"], pop_sta),
                         pc(rep["mobile_poisson_2B"], pop_mob))
    d = me.mean() - mp_.mean()
    sd_d = math.sqrt(me.var(ddof=1) / len(me) + mp_.var(ddof=1) / len(mp_))
    dose = m2b.mean() - mp_.mean()
    sd_dose = math.sqrt(m2b.var(ddof=1) / len(m2b) + mp_.var(ddof=1) / len(mp_))

    R = {
        "SECTION": "SEAL repair round (the single permitted one)",
        "NO_ENGINE_START": True,
        "WHAT_WAS_SIMULATED": ("m6_obfor01.simulate_arm, the delivered ideal-process "
                               "predictor. %d replicates x %d arms in each of four "
                               "conditions. Seeds in the %d block, disjoint from every "
                               "scientific register." % (R_REPLICATES, ARMS_PER_REPLICATE,
                                                         SEED_BLOCK)),

        "R1_BIRTH_FLUX_ABLATION_REPLICATED": {
            "THE_CLAIM_UNDER_TEST": ("the frozen ablation reported that replacing the "
                                     "measured birth flux by a Poisson source of the same "
                                     "mean moves the mobile prediction by 1.27 percentage "
                                     "points. That single comparison was one 30-arm run "
                                     "against one other 30-arm run."),
            "mobile_empirical_percent_mean": float(me.mean()),
            "mobile_empirical_percent_sd_over_replicates": float(me.std(ddof=1)),
            "mobile_poisson_percent_mean": float(mp_.mean()),
            "mobile_poisson_percent_sd_over_replicates": float(mp_.std(ddof=1)),
            "difference_pp": float(d), "se_pp": float(sd_d),
            "t": float(d / sd_d), "df_welch_approx": 2 * R_REPLICATES - 2,
            "ORIGINAL_SINGLE_RUN_DIFFERENCE_pp": -1.2709565395839455,
            "WHERE_THE_TWO_FROZEN_RUNS_SIT_IN_THEIR_OWN_REPLICATE_DISTRIBUTIONS": {
                "frozen_empirical_run_percent": -5.69468260538053,
                "z_against_the_replicated_empirical_mean":
                    float((-5.69468260538053 - me.mean()) / me.std(ddof=1)),
                "frozen_poisson_run_percent": -4.4237260657965845,
                "z_against_the_replicated_poisson_mean":
                    float((-4.4237260657965845 - mp_.mean()) / mp_.std(ddof=1))},
            "VERDICT": ("the 1.27 pp effect does not replicate, and it does not even "
                        "replicate in sign. Sixteen independent 30-arm replicates per side "
                        "give empirical %+.3f %% and Poisson %+.3f %%, a difference of "
                        "%+.3f +- %.3f pp (t = %.2f on %d df). The frozen single runs sit "
                        "%.2f and %.2f replicate standard deviations from their own means, "
                        "in OPPOSITE directions: the 1.27 pp was two ordinary Monte-Carlo "
                        "excursions read as one mechanism. The static side of the same "
                        "ablation had already come out at 0.068 pp, nineteen times smaller, "
                        "which should have raised the alarm at the time and did not."
                        % (me.mean(), mp_.mean(), d, sd_d, d / sd_d, 2 * R_REPLICATES - 2,
                           (-5.69468260538053 - me.mean()) / me.std(ddof=1),
                           (-4.4237260657965845 - mp_.mean()) / mp_.std(ddof=1))),
            "HONEST_RESIDUAL_EFFECT": ("a shape effect of at most a few tenths of a "
                                       "percentage point may exist; its sign is not "
                                       "established by this evidence and it is an order of "
                                       "magnitude below what was claimed."),
            "CONSEQUENCE": ("the sentence 'the shape of the birth flux is load-bearing "
                            "(1.27 points)' is withdrawn. The 2x2 factorial main effect of "
                            "-1.30 pp rests on the same two runs and is withdrawn with it. "
                            "The shared-trajectory main effect of -3.74 pp is NOT withdrawn: "
                            "it is six times the replicate sd and it is confirmed "
                            "independently by the fresh ablation endpoint."),
        },

        "R2_SOURCE_INTENSITY_SENSITIVITY": {
            "DESIGN": ("Poisson source at the measured mean B = %.5f versus Poisson at 2B, "
                       "everything else frozen. If the prediction depends on the source at "
                       "all in the tested regime, this is where it must show." % float(b.mean())),
            "poisson_B_percent": float(mp_.mean()),
            "poisson_2B_percent": float(m2b.mean()),
            "effect_per_doubling_pp": float(dose), "se_pp": float(sd_dose),
            "t": float(dose / sd_dose),
            "CONTROL__mean_in_window_population": {
                "at_B": pop_B, "at_2B": pop_2B,
                "REALISED_RATIO": pop_2B / pop_B,
                "why": ("without this control a null dose response could just mean the dose "
                        "was never delivered. It was: the cloud really doubles.")},
            "READING": ("doubling the source intensity doubles the cloud (%.1f -> %.1f "
                        "particles) and moves the mobile prediction by %+.2f +- %.2f pp, "
                        "i.e. not at all. In the tested regime the median-summarised r80 "
                        "residual is INTENSITY-INVARIANT: the finite-population bias is "
                        "already saturated at N ~ 117, and the residual is carried by the "
                        "shared organiser trajectory, not by the source strength."
                        % (pop_B, pop_2B, dose, sd_dose)),
            "CONSEQUENCE_FOR_THE_CONDITIONALITY": (
                "this REMOVES the numerical argument for CONDITIONAL as well. What remains "
                "is derivational and it is sufficient: M6 cannot be started without being "
                "handed a birth-flux law measured from delivered engine output, because it "
                "does not derive the source from the chemostat. A prediction whose inputs "
                "include a measurement of the system it predicts is conditional on that "
                "measurement whatever its sensitivity happens to be. The measured "
                "insensitivity is reported as a ROBUSTNESS result, not as a licence to "
                "upgrade the claim."),
        },

        "R3_PREDICTION_MONTE_CARLO_SD": {
            "WHAT_IT_IS": ("the standard deviation, across independent replicates of the "
                           "frozen 30-arm design, of the M6 POINT PREDICTION itself. The "
                           "frozen artefact reported only the within-replicate standard "
                           "error of the mean (0.275 static, 0.602 mobile); this is the "
                           "directly measured dispersion of the quantity that was frozen."),
            "static_percent": float(ms_.std(ddof=1)),
            "mobile_percent": float(me.std(ddof=1)),
            "frozen_within_replicate_se_static_percent":
                frz["RESIDUAL_TOLERANCE"]["COMPONENTS"]["M6_monte_carlo_se_static_percent"],
            "frozen_within_replicate_se_mobile_percent":
                frz["RESIDUAL_TOLERANCE"]["COMPONENTS"]["M6_monte_carlo_se_mobile_percent"],
            "OBLIGATION": ("every frozen prediction must from now on be quoted with this sd "
                           "beside it. A point prediction carrying an unstated +-%.2f %% "
                           "Monte-Carlo sd is not a point."
                           % float(me.std(ddof=1))),
            "CONSEQUENCE_FOR_THE_MOBILE_PREDICTION": (
                "the frozen mobile prediction 8.0574 (-5.69 %%) is itself %.2f replicate sd "
                "below the replicated M6 mean of %+.2f %%. Scored against that replicated "
                "mean the fresh mobile observation would be off by %+.2f %% instead of "
                "+0.24 %% -- still far inside the margin, so the conclusion survives, but "
                "the apparent precision of the original agreement was partly luck."
                % ((-5.69468260538053 - me.mean()) / me.std(ddof=1), me.mean(),
                   100 * (obs_mobile / (pop_mob * (1 + me.mean() / 100.0)) - 1))),
        },
        "R3_HISTORICAL_ARMS_BEHIND_THE_BIRTH_FLUX": n_hist,
    }

    print("R4-R5  historical arms, unfiltered")
    rows = historical_arms()
    R["R5_INCLUSION_RULE_SENSITIVITY"] = filter_sensitivity(rows, q, mu)
    nb = null_baseline(rows, q, mu)

    print("R6     restating the fresh statistics")
    pred_sd = {"static": float(ms_.std(ddof=1)), "mobile": float(me.std(ddof=1))}
    R["R6_FRESH_STATISTICS_RESTATED"] = restate_statistics(S, Mo, pred_sd)

    # ---- the null baseline scored on the same three endpoints
    ms, mm = S.mean(), Mo.mean()
    ses, sem = S.std(ddof=1) / math.sqrt(len(S)), Mo.std(ddof=1) / math.sqrt(len(Mo))
    delta = frz["RESIDUAL_TOLERANCE"]["EQUIVALENCE_MARGIN_percent"]

    def score(obs, se, pred):
        r = 100 * (obs / pred - 1)
        rse = 100 * se / pred
        return {"predicted": pred, "observed": float(obs), "relative_error_percent": r,
                "se_percent": rse, "t_against_the_prediction": r / rse,
                "whole_interval_width_percent": abs(r) + 1.96 * rse,
                "POINT_INSIDE_THE_2p9_MARGIN": bool(abs(r) <= delta),
                "WHOLE_INTERVAL_INSIDE_THE_2p9_MARGIN": bool(abs(r) + 1.96 * rse <= delta)}

    rrel = math.sqrt((sem / mm) ** 2 + (ses / ms) ** 2)
    ep = frz["PRIMARY_PREDICTIONS"]
    R["R4_DISCRIMINATING_POWER"] = {
        "NULL_BASELINE": nb,
        "NULL_SCORED_ON_THE_THREE_FROZEN_ENDPOINTS": {
            "static": score(ms, ses, nb["predicted_static_r80_median"]),
            "mobile": score(mm, sem, nb["predicted_mobile_r80_median"]),
            "ratio": {"predicted": nb["predicted_ratio"], "observed": float(mm / ms),
                      "relative_error_percent": 100 * ((mm / ms) / nb["predicted_ratio"] - 1),
                      "se_percent": 100 * rrel,
                      "t_against_the_prediction":
                          ((mm / ms) / nb["predicted_ratio"] - 1) / rrel,
                      "whole_interval_width_percent":
                          abs(100 * ((mm / ms) / nb["predicted_ratio"] - 1)) + 100 * 1.96 * rrel,
                      "POINT_INSIDE_THE_2p9_MARGIN":
                          bool(abs(100 * ((mm / ms) / nb["predicted_ratio"] - 1)) <= delta),
                      "WHOLE_INTERVAL_INSIDE_THE_2p9_MARGIN":
                          bool(abs(100 * ((mm / ms) / nb["predicted_ratio"] - 1))
                               + 100 * 1.96 * rrel <= delta)}},
        "WHAT_THE_TEST_DOES_REJECT": {
            "the uncorrected ideal operator": {
                "static": score(ms, ses, m6.population_r80(36, False, q, mu)),
                "mobile": score(mm, sem, m6.population_r80(36, True, q, mu))},
            "the model with the shared trajectory removed": score(
                mm, sem, m6.population_r80(36, True, q, mu)
                * (1 + ep["ABLATION_RULE"]["M6_no_shared_trajectory_percent"] / 100.0))},
        "VERDICT": ("a zero-physics predictor that simply copies the historical arms passes "
                    "all three frozen endpoints. The fresh test therefore does NOT "
                    "discriminate M6 from 'the fresh arms resemble the old ones'. It DOES "
                    "reject the uncorrected ideal operator and the model without the shared "
                    "organiser trajectory. The correct statement is: the prediction was not "
                    "falsified, and the shared-trajectory mechanism is required. It is not: "
                    "the operator predicts prospectively where nothing else could."),
        "WAS_THE_NULL_AVAILABLE_BEFORE_THE_RUN": True,
    }

    json.dump(R, open(f"{OUT}/OBFOR01_SEAL_REPAIR_EVIDENCE.json", "w"), indent=1, default=str)

    # ---------------------------------------------------------------- console
    a = R["R1_BIRTH_FLUX_ABLATION_REPLICATED"]
    print("\nR1  empirical %+.3f %%  poisson %+.3f %%  diff %+.3f +- %.3f pp  t %.2f  "
          "(single-run claim -1.271)"
          % (a["mobile_empirical_percent_mean"], a["mobile_poisson_percent_mean"],
             a["difference_pp"], a["se_pp"], a["t"]))
    e = R["R2_SOURCE_INTENSITY_SENSITIVITY"]
    print("R2  doubling B: %+.2f +- %.2f pp  t %.2f"
          % (e["effect_per_doubling_pp"], e["se_pp"], e["t"]))
    s = R["R3_PREDICTION_MONTE_CARLO_SD"]
    print("R3  prediction sd  static %.3f %%  mobile %.3f %%"
          % (s["static_percent"], s["mobile_percent"]))
    n4 = R["R4_DISCRIMINATING_POWER"]["NULL_SCORED_ON_THE_THREE_FROZEN_ENDPOINTS"]
    for k, v in n4.items():
        print("R4  null baseline %-7s %+6.2f %%  t %5.2f  whole-int %.2f  point in %s  "
              "whole in %s"
              % (k, v["relative_error_percent"], v["t_against_the_prediction"],
                 v["whole_interval_width_percent"], v["POINT_INSIDE_THE_2p9_MARGIN"],
                 v["WHOLE_INTERVAL_INSIDE_THE_2p9_MARGIN"]))
    rej = R["R4_DISCRIMINATING_POWER"]["WHAT_THE_TEST_DOES_REJECT"]
    for k in ("static", "mobile"):
        v = rej["the uncorrected ideal operator"][k]
        print("R4  uncorrected ideal %-7s %+6.2f %%  point in %s"
              % (k, v["relative_error_percent"], v["POINT_INSIDE_THE_2p9_MARGIN"]))
    v = rej["the model with the shared trajectory removed"]
    print("R4  no-shared-trajectory mobile %+6.2f %%  point in %s"
          % (v["relative_error_percent"], v["POINT_INSIDE_THE_2p9_MARGIN"]))
    for k, v in R["R5_INCLUSION_RULE_SENSITIVITY"]["LEVELS"].items():
        print("R5  %-52s n=%3d  %+6.2f %%" % (k, v["n"], v["percent"]))
    for k, v in R["R6_FRESH_STATISTICS_RESTATED"].items():
        print("R6  %-7s point %+6.2f %% (rule %.1f) ; whole-int normal %.3f  t %.3f  "
              "t+pred_sd %.3f"
              % (k, v["relative_error_percent"], v["FROZEN_POINT_RULE_percent"],
                 v["POST_FREEZE_whole_interval_normal_1p96"],
                 [x for kk, x in v.items() if kk.startswith("POST_FREEZE_whole_interval_t_")
                  and "prediction" not in kk][0],
                 v["POST_FREEZE_whole_interval_t_with_prediction_sd_propagated"]))
    for k in ("static", "mobile"):
        v = R["R6_FRESH_STATISTICS_RESTATED"][k]
        print("R6  %-7s TOST p normal %.3e -> t(%d) %.3e   ratio %.0fx"
              % (k, v["TOST_p_NORMAL_as_originally_reported"], v["df"],
                 v["TOST_p_t_%d_df__CORRECTED" % v["df"]],
                 v["TOST_p_t_%d_df__CORRECTED" % v["df"]]
                 / max(v["TOST_p_NORMAL_as_originally_reported"], 1e-300)))


if __name__ == "__main__":
    main()

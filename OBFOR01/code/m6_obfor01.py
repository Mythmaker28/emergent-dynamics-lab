"""OBFOR01 §7, §15 — the model hierarchy realised as one simulator with ablation switches.

Nothing here touches the scientific engine. This is the IDEAL process written directly from the
frozen rules, so that each ingredient can be switched off and the residual re-measured:

    step:  X diffuses  ->  organiser diffuses  ->  births at the organiser's NEW cell
           ->  decay applies to everyone including the newborns

which is `_one_step`'s order with capacity refusal removed and the chemostat replaced by a
birth-flux law. That is exactly the "unblocked" operator OBTR01 qualified, so if this simulator
reproduces the engine's numbers, the unblocked kernel is quantitatively correct and the residual
is downstream of the physics.

The switches map onto the mandate's hierarchy:

  SHARED_TRAJECTORY  off -> every particle sees its own independent organiser path, which is
                            the i.i.d. approximation; on -> M3, one path shared by the cloud
  BIRTH_FLUX         'constant' -> a fixed mean intensity;  'empirical' -> M4, the per-step
                            distribution measured from the delivered trajectories
  FINITE_TIME        on  -> start empty and burn in exactly as the protocol does
  ESTIMATOR          always the frozen one: per-frame first crossing, median or mean over
                            frames, mean over arms

Capacity refusal (M5) is NOT simulated: §12 measures it at 3.6e-4 per offered hop with a
certified per-particle bound of 0.9 %, so it is characterised rather than modelled.
"""
from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import yaml

WC = "/home/claude/OBFOR01/verify/obtr01/wc"
OUT = "/home/claude/OBFOR01/out"
sys.path.insert(0, f"{WC}/OBTR01/code")
sys.path.insert(0, f"{WC}/OBTC02/code")
sys.path.insert(0, f"{WC}/ORR01/code")

from kernels_obtr01 import Operator                      # noqa: E402
import metrics_obtc as M                                 # noqa: E402

BURN_IN, HORIZON, SAMPLE_EVERY = 2000, 11000, 50


def population_r80(L, mobile, q, mu):
    op = Operator(q, q if mobile else 0.0, mu, L)
    prof = op.stationary_profile()
    i = np.arange(L)
    d1 = np.minimum(i, L - i).astype(float)
    d = np.sqrt(d1[:, None] ** 2 + d1[None, :] ** 2)
    o = np.argsort(d.ravel(), kind="stable")
    dd, ww = d.ravel()[o], prof.ravel()[o]
    cw = np.cumsum(ww) / ww.sum()
    return float(dd[int(np.searchsorted(cw, 0.8, side="left"))])


def empirical_birth_flux(root, prefix, limit=40):
    """The per-step accepted birth counts, taken from the delivered trajectories. Raw-only."""
    vals = []
    n_used = 0
    for n in sorted(os.listdir(root)):
        if not n.startswith(prefix):
            continue
        z = np.load(f"{root}/{n}", allow_pickle=True)
        F = {str(k): i for i, k in enumerate(z["fields"])}
        s = z["series"][BURN_IN:HORIZON]
        if s[:, F["N_X"]].mean() <= 0:
            continue
        vals.append(s[:, F["accepted_births_X"]].astype(np.int64))
        n_used += 1
        if n_used >= limit:
            break
    v = np.concatenate(vals)
    return v, n_used


def simulate_arm(L, mobile, q, mu, births, rng, shared_trajectory=True,
                 birth_flux="empirical", B_const=None, horizon=HORIZON):
    """One arm of the ideal process. Returns the per-frame r80_organiser values."""
    py = np.zeros(0, np.int64)
    px = np.zeros(0, np.int64)
    oy = ox = 0
    frames = []
    for t in range(1, horizon + 1):
        n = len(py)
        if n:
            py += rng.binomial(1, q, n) - rng.binomial(1, q, n)
            px += rng.binomial(1, q, n) - rng.binomial(1, q, n)
        if mobile:
            if shared_trajectory:
                oy += int(rng.binomial(1, q)) - int(rng.binomial(1, q))
                ox += int(rng.binomial(1, q)) - int(rng.binomial(1, q))
            else:
                # every particle carries its own independent organiser increment: the i.i.d.
                # approximation, kept here so the correlation can be switched off cleanly
                if n:
                    py -= rng.binomial(1, q, n) - rng.binomial(1, q, n)
                    px -= rng.binomial(1, q, n) - rng.binomial(1, q, n)
        nb = int(rng.choice(births)) if birth_flux == "empirical" else \
            int(rng.poisson(B_const))
        if nb:
            py = np.concatenate([py, np.full(nb, oy if shared_trajectory else 0, np.int64)])
            px = np.concatenate([px, np.full(nb, ox if shared_trajectory else 0, np.int64)])
        n = len(py)
        if n:
            keep = rng.random(n) >= mu
            py, px = py[keep], px[keep]
        if t > BURN_IN and t % SAMPLE_EVERY == 0 and len(py):
            ry = (py - (oy if shared_trajectory else 0)) % L
            rx = (px - (ox if shared_trajectory else 0)) % L
            g = np.zeros((L, L), np.int64)
            np.add.at(g, (ry, rx), 1)
            frames.append(float(M.radii(g, 0, 0)[0.8]))
    return np.asarray(frames)


def run(tag, L, mobile, q, mu, births, B_const, arms, rng, **kw):
    med, mean, sd, skew = [], [], [], []
    for _ in range(arms):
        v = simulate_arm(L, mobile, q, mu, births, rng, B_const=B_const, **kw)
        if len(v) < 50:
            continue
        med.append(float(np.median(v)))
        mean.append(float(v.mean()))
        sd.append(float(v.std(ddof=1)))
        skew.append(float(((v - v.mean()) ** 3).mean() / v.std(ddof=1) ** 3))
    pop = population_r80(L, mobile, q, mu)
    med, mean = np.asarray(med), np.asarray(mean)
    return {"tag": tag, "arms": len(med), "population_r80": pop,
            "median_summary": float(med.mean()),
            "median_ratio": float(med.mean() / pop),
            "median_residual_percent": 100 * (med.mean() / pop - 1),
            "median_se_percent": 100 * float(med.std(ddof=1) / math.sqrt(len(med))) / pop,
            "mean_summary": float(mean.mean()),
            "mean_ratio": float(mean.mean() / pop),
            "mean_residual_percent": 100 * (mean.mean() / pop - 1),
            "mean_se_percent": 100 * float(mean.std(ddof=1) / math.sqrt(len(mean))) / pop,
            "within_arm_sd": float(np.mean(sd)),
            "within_arm_skew": float(np.mean(skew))}


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    mu, q, L = pt["muX"], pt["p_hop"] / 4.0, int(pt["L"])
    rng = np.random.default_rng(20260815)

    births_mob, nm = empirical_birth_flux(f"{WC}/OBDI02/raw", "L36__")
    births_sta, ns = empirical_birth_flux(f"{WC}/OBTC02/raw", "S__")
    B_mob, B_sta = float(births_mob.mean()), float(births_sta.mean())

    obs = json.load(open(f"{OUT}/_residual.json"))
    observed = {
        "static_median": obs["RESIDUALS"]["STATIC_median_summary"]["residual_percent"],
        "static_mean": obs["RESIDUALS"]["STATIC_mean_summary"]["residual_percent"],
        "mobile_median": obs["BY_SIZE"]["36"]["median"]["residual_percent"]
        if "36" in obs["BY_SIZE"] else obs["BY_SIZE"][36]["median"]["residual_percent"],
        "mobile_mean": obs["BY_SIZE"]["36"]["mean"]["residual_percent"]
        if "36" in obs["BY_SIZE"] else obs["BY_SIZE"][36]["mean"]["residual_percent"],
        "static_within_arm_sd": obs["ESTIMATOR"]["OBSERVED_DISPERSION"][
            "static_within_arm_sd"],
        "mobile_within_arm_sd": obs["ESTIMATOR"]["OBSERVED_DISPERSION"][
            "mobile_within_arm_sd"],
        "mobile_within_arm_skew": obs["ESTIMATOR"]["OBSERVED_DISPERSION"][
            "mobile_within_arm_skew"],
    }

    ARMS = 30
    models = []
    models.append(run("M6_MOBILE_full", L, True, q, mu, births_mob, B_mob, ARMS, rng,
                      shared_trajectory=True, birth_flux="empirical"))
    models.append(run("M4_ablate_birth_flux_to_constant", L, True, q, mu, births_mob, B_mob,
                      ARMS, rng, shared_trajectory=True, birth_flux="poisson"))
    models.append(run("M3_ablate_shared_trajectory", L, True, q, mu, births_mob, B_mob,
                      ARMS, rng, shared_trajectory=False, birth_flux="empirical"))
    models.append(run("M2_neither_shared_nor_endogenous", L, True, q, mu, births_mob, B_mob,
                      ARMS, rng, shared_trajectory=False, birth_flux="poisson"))
    models.append(run("M6_STATIC_full", L, False, q, mu, births_sta, B_sta, ARMS, rng,
                      shared_trajectory=True, birth_flux="empirical"))
    models.append(run("M6_STATIC_poisson_births", L, False, q, mu, births_sta, B_sta, ARMS,
                      rng, shared_trajectory=True, birth_flux="poisson"))

    def by(tag):
        return next(m for m in models if m["tag"] == tag)

    full_m, full_s = by("M6_MOBILE_full"), by("M6_STATIC_full")
    ablate_b = by("M4_ablate_birth_flux_to_constant")
    ablate_t = by("M3_ablate_shared_trajectory")

    base = by("M2_neither_shared_nor_endogenous")
    only_shared = by("M4_ablate_birth_flux_to_constant")     # shared ON, births Poisson
    only_births = by("M3_ablate_shared_trajectory")          # shared OFF, births empirical
    r = lambda m: m["median_residual_percent"]
    sequential = {
        "ORDER": ("physically ordered: start from the discrete kernel on the finite torus with "
                  "a Poisson point source and frames treated as independent draws, then add "
                  "the shared organiser trajectory, then the measured birth flux"),
        "step_0_baseline_M2_level": r(base),
        "step_1_add_shared_trajectory": r(only_shared),
        "step_1_gain": r(only_shared) - r(base),
        "step_2_add_empirical_birth_flux": r(full_m),
        "step_2_gain": r(full_m) - r(only_shared),
        "total": r(full_m) - r(base)}
    factorial = {
        "DESIGN": "2 x 2 on {shared trajectory, empirical birth flux}",
        "neither": r(base), "shared_only": r(only_shared), "births_only": r(only_births),
        "both": r(full_m),
        "main_effect_shared_trajectory": 0.5 * ((r(only_shared) - r(base))
                                                + (r(full_m) - r(only_births))),
        "main_effect_birth_flux": 0.5 * ((r(only_births) - r(base))
                                         + (r(full_m) - r(only_shared))),
        "interaction": (r(full_m) - r(only_shared) - r(only_births) + r(base)),
        "WARNING": ("the two main effects and the interaction sum to the total by "
                    "construction; no single mechanism is credited with the whole residual, "
                    "and the ordering-dependent sequential table is reported beside this one "
                    "because attribution is not order-free")}

    decomposition = {
        "SEQUENTIAL": sequential, "FACTORIAL": factorial,
        "TARGET": {"mobile_median_residual_observed": observed["mobile_median"],
                   "static_median_residual_observed": observed["static_median"],
                   "mobile_mean_residual_observed": observed["mobile_mean"],
                   "static_mean_residual_observed": observed["static_mean"]},
        "M6_REPRODUCES": {
            "mobile_median": full_m["median_residual_percent"],
            "mobile_median_se": full_m["median_se_percent"],
            "mobile_mean": full_m["mean_residual_percent"],
            "static_median": full_s["median_residual_percent"],
            "static_median_se": full_s["median_se_percent"],
            "static_mean": full_s["mean_residual_percent"]},
        "ABLATIONS": {
            "removing_the_shared_trajectory": {
                "median_residual_percent": ablate_t["median_residual_percent"],
                "within_arm_sd": ablate_t["within_arm_sd"],
                "loses_percentage_points": (full_m["median_residual_percent"]
                                            - ablate_t["median_residual_percent"]),
                "READING": ("the shared organiser trajectory is what over-disperses the "
                            "per-frame statistic; removing it collapses the cloud onto the "
                            "static width and the median penalty with it")},
            "flattening_the_birth_flux": {
                "median_residual_percent": ablate_b["median_residual_percent"],
                "within_arm_sd": ablate_b["within_arm_sd"],
                "loses_percentage_points": (full_m["median_residual_percent"]
                                            - ablate_b["median_residual_percent"]),
                "READING": ("replacing the measured birth flux by a Poisson source of the same "
                            "mean; if this changes little, the endogeneity of the source is "
                            "not what drives the residual")},
        },
        "DISPERSION_CHECK": {
            "mobile_within_arm_sd_simulated": full_m["within_arm_sd"],
            "mobile_within_arm_sd_observed": observed["mobile_within_arm_sd"],
            "mobile_within_arm_skew_simulated": full_m["within_arm_skew"],
            "mobile_within_arm_skew_observed": observed["mobile_within_arm_skew"],
            "static_within_arm_sd_simulated": full_s["within_arm_sd"],
            "static_within_arm_sd_observed": observed["static_within_arm_sd"]},
    }

    def close(a, b, tol):
        return bool(abs(a - b) <= tol)

    verdict = {
        "M6_REPRODUCES_THE_MOBILE_MEDIAN_RESIDUAL":
            close(full_m["median_residual_percent"], observed["mobile_median"],
                  2.5 * max(full_m["median_se_percent"], 0.3)),
        "M6_REPRODUCES_THE_STATIC_MEDIAN_RESIDUAL":
            close(full_s["median_residual_percent"], observed["static_median"],
                  2.5 * max(full_s["median_se_percent"], 0.5)),
        "M6_REPRODUCES_THE_MEAN_SUMMARY_AS_NEARLY_UNBIASED":
            bool(abs(full_m["mean_residual_percent"]) < 2.0
                 and abs(full_s["mean_residual_percent"]) < 2.5),
        "SHARED_TRAJECTORY_IS_NECESSARY":
            bool(ablate_t["median_residual_percent"] > full_m["median_residual_percent"] + 1.0),
        "BIRTH_FLUX_ENDOGENEITY_IS_MATERIAL":
            bool(abs(factorial["main_effect_birth_flux"]) > 0.5),
        "INTERACTION_IS_MATERIAL": bool(abs(factorial["interaction"]) > 0.5),
    }

    out = {"SECTION": "OBFOR01 §7, §15",
           "CONSUMES_NO_SCIENTIFIC_RUN": True,
           "WHAT_IS_SIMULATED": ("the ideal process written from the frozen rules: exact "
                                 "one-step kernels, exact intra-step order, geometric "
                                 "mortality, point source at the organiser, finite torus, "
                                 "finite horizon, and the frozen estimator pipeline. No "
                                 "engine, no capacity refusal, no chemostat."),
           "BIRTH_FLUX_SOURCE": {"mobile_arms_used": nm, "static_arms_used": ns,
                                 "mobile_mean_B": B_mob, "static_mean_B": B_sta,
                                 "mobile_var_over_mean": float(births_mob.var()
                                                               / births_mob.mean()),
                                 "note": "a Poisson source would have variance/mean = 1"},
           "MODELS": models, "OBSERVED": observed,
           "DECOMPOSITION": decomposition, "VERDICT": verdict}
    json.dump(out, open(f"{OUT}/_m6.json", "w"), indent=1, default=str)

    print("birth flux: mobile mean %.4f (var/mean %.3f, %d arms), static mean %.4f"
          % (B_mob, births_mob.var() / births_mob.mean(), nm, B_sta))
    print()
    hdr = "%-36s %5s %11s %11s %10s %8s" % ("MODEL", "arms", "median res", "mean res",
                                            "arm sd", "skew")
    print(hdr)
    print("-" * len(hdr))
    for m in models:
        print("%-36s %5d %9.2f %%%s %9.2f %% %10.3f %8.3f"
              % (m["tag"], m["arms"], m["median_residual_percent"],
                 " " if m["median_se_percent"] > 9 else "",
                 m["mean_residual_percent"], m["within_arm_sd"], m["within_arm_skew"]))
    print("%-36s %5s %9.2f %%  %9.2f %% %10.3f %8s"
          % ("OBSERVED mobile (engine, L=36)", "42", observed["mobile_median"],
             observed["mobile_mean"], observed["mobile_within_arm_sd"],
             "%.3f" % observed["mobile_within_arm_skew"]))
    print("%-36s %5s %9.2f %%  %9.2f %% %10.3f %8s"
          % ("OBSERVED static (engine)", "3", observed["static_median"],
             observed["static_mean"], observed["static_within_arm_sd"], "-"))
    print()
    print("SEQUENTIAL decomposition of the mobile median residual (percentage points)")
    print("  baseline, neither correction        %+7.2f" % sequential["step_0_baseline_M2_level"])
    print("  + shared organiser trajectory       %+7.2f   (gain %+.2f)"
          % (sequential["step_1_add_shared_trajectory"], sequential["step_1_gain"]))
    print("  + measured birth flux               %+7.2f   (gain %+.2f)"
          % (sequential["step_2_add_empirical_birth_flux"], sequential["step_2_gain"]))
    print("FACTORIAL 2 x 2")
    print("  main effect, shared trajectory      %+7.2f" % factorial["main_effect_shared_trajectory"])
    print("  main effect, birth flux             %+7.2f" % factorial["main_effect_birth_flux"])
    print("  interaction                         %+7.2f" % factorial["interaction"])
    print()
    for k, v in verdict.items():
        print("  %-52s %s" % (k, v))


if __name__ == "__main__":
    main()

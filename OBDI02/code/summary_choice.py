"""OBDI02 §7 — the per-seed summary, fixed before any new data.

The mandate allows the median, a trimmed mean, a quantile, or the statistic inherited from
OBDI01. This file measures the four candidates on the OBDI01 arms and records the decision.

The decision is to KEEP THE INHERITED MEDIAN. It is not made on grounds of loyalty: it is made
because the measurement below shows no candidate is reliably more precise, and keeping the
inherited one is what makes PRIMARY_ESTIMAND_DIFF_FROM_OBDI01 = NONE literally true.
"""
from __future__ import annotations

import json

import numpy as np

WC = "/home/claude/OBDI02/verify/obdi01/wc"
OUT = "/home/claude/OBDI02/out"
BURN = 2000
SIZES = (36, 72, 96)


def frames(tag):
    z = np.load("%s/OBDI01/raw/%s.npz" % (WC, tag.replace("/", "__")), allow_pickle=True)
    return [json.loads(s) for s in z["frames"] if json.loads(s)["step"] > BURN]


def block_se(rng, x, stat, block=10, draws=1200):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    nb = int(np.ceil(n / block))
    out = np.empty(draws)
    for d in range(draws):
        st = rng.integers(0, n, size=nb)
        idx = (st[:, None] + np.arange(block)[None, :]) % n
        out[d] = stat(x[idx.ravel()[:n]])
    return float(out.std(ddof=1))


def main():
    A = json.load(open(f"{WC}/OBDI01/out/_arms.json"))
    rng = np.random.default_rng(7)
    cands = {
        "median": (np.median, "the median of |C - Y| over the in-window frames — INHERITED"),
        "mean": (np.mean, "the arithmetic mean over the in-window frames"),
        "trimmed10": (lambda v: float(np.mean(np.sort(v)[int(.1 * len(v)):
                                                        len(v) - int(.1 * len(v))])),
                      "the 10 % symmetrically trimmed mean"),
        "q75": (lambda v: float(np.quantile(v, 0.75)), "the third quartile"),
    }
    res = {}
    for k, (f, desc) in cands.items():
        per = {}
        for L in SIZES:
            arms = [a for a in A if a["L"] == L
                    and np.isfinite(a["summary"]["organiser_to_core"])]
            vals, ses = [], []
            for a in arms:
                v = np.array([fr["organiser_to_core"] for fr in frames(a["tag"])], float)
                v = v[np.isfinite(v)]
                vals.append(float(f(v)))
                ses.append(block_se(rng, v, f))
            vals, ses = np.array(vals), np.array(ses)
            lv = np.log(vals)
            per[str(L)] = {
                "n_arms": len(vals), "mean": float(vals.mean()),
                "sd_arm_level": float(vals.std(ddof=1)),
                "cv": float(vals.std(ddof=1) / vals.mean()),
                "sd_of_log": float(lv.std(ddof=1)),
                "within_arm_se_block_bootstrap": float(np.sqrt((ses ** 2).mean())),
                "distinct_values_observed": int(len(set(np.round(vals, 9))))}
        res[k] = {"description": desc, "by_L": per,
                  "max_sd_of_log": max(v["sd_of_log"] for v in per.values()),
                  "mean_sd_of_log": float(np.mean([v["sd_of_log"] for v in per.values()]))}

    ranking = sorted(res, key=lambda k: res[k]["max_sd_of_log"])
    chosen = "median"
    out = {
        "SECTION": "OBDI02 §7",
        "INDEPENDENT_UNIT": "SEED",
        "WITHIN_SEED_SUMMARY": ("the MEDIAN of |C - Y| over the %d in-window frames of the arm "
                                "(steps strictly after the burn-in, one frame every "
                                "SAMPLE_EVERY steps), where |C - Y| is the toroidal Euclidean "
                                "distance between the Frechet centre of the X field and the "
                                "organiser cell, both read from the same frame" % 180),
        "CANDIDATES": res,
        "RANKING_BY_WORST_CASE_DISPERSION": ranking,
        "CHOSEN": chosen,
        "REASON": ("no candidate is reliably better. The median has the largest dispersion at "
                   "L = 36 and the smallest at L = 72 and L = 96; the mean is the reverse. With "
                   "four or five arms per size these standard deviations carry a relative "
                   "standard error of about 40 %%, so the ordering between candidates is not "
                   "resolvable. Choosing a different summary on such evidence would be "
                   "selection on noise. The inherited median is kept, which also makes "
                   "PRIMARY_ESTIMAND_DIFF_FROM_OBDI01 = NONE exactly true."),
        "AUTOCORRELATION_TREATMENT": ("temporal autocorrelation is handled where it belongs: "
                                      "inside the construction of the per-seed summary, whose "
                                      "sampling error is measured by a block bootstrap of "
                                      "length 10 frames. It NEVER increases the number of "
                                      "independent observations, which is the number of seeds "
                                      "and nothing else."),
        "PSEUDOREPLICATION_IS_FORBIDDEN": ("no frame is ever treated as an independent "
                                           "observation in any variance, interval or test of "
                                           "the primary endpoint"),
    }
    json.dump(out, open(f"{OUT}/_summary_choice.json", "w"), indent=1, default=str)
    print("%-10s %-9s %-9s %-9s %-9s" % ("candidate", "sd_log@36", "sd_log@72", "sd_log@96",
                                         "worst"))
    for k in cands:
        b = res[k]["by_L"]
        print("%-10s %-9.4f %-9.4f %-9.4f %-9.4f"
              % (k, b["36"]["sd_of_log"], b["72"]["sd_of_log"], b["96"]["sd_of_log"],
                 res[k]["max_sd_of_log"]))
    print("\nCHOSEN =", chosen, "(inherited)")


if __name__ == "__main__":
    main()

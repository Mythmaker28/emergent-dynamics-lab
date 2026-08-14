"""CSC01 §11 — the passive calibration assay for lambda.

It reads ONE structural statistic of the REFERENCE arm — the median number of X neighbours of an
X molecule inside the core — and nothing else. No gate verdict, no PASS, no classification and
no compactness statistic of the assay enters the choice. The target (half the death rate at the
median neighbour count) and the factor 1/2 were declared in `mechanisms.py` before this ran.
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import observe as OBS            # noqa: E402

import guard_csc as GC           # noqa: E402
import lawspec_v3 as V3          # noqa: E402
import mechanisms as M           # noqa: E402
import protocol_csc as PC        # noqa: E402
import spatial as SP             # noqa: E402

OUT = "/home/claude/CSC01/out"
ASSAY_HORIZON = 4000             # declared: T_FORM_MAX + 2000
ASSAY_FROM = 2000                # declared: the statistic is read only after T_FORM_MAX
SAMPLE_EVERY = PC.W_["SAMPLE_EVERY"]


def assay_arm(seed):
    sp = PC.spec_for()
    rec = OBS.Recorder()
    w = V3.fresh_world(seed, sp, lawspec=V3.V2.LAWSPEC_V2_EXCHANGE,
                       rng_mode="split_feed_stream", exchangeable=V3.V2.EXCHANGEABLE_DEFAULT,
                       insert_mode="reservoir", rec=rec, cohesion=None, lam=0.0)
    V3.seed_one_organiser(w, PC.X_SEED)
    per_frame = []

    def per_step(ww):
        if ww.step % SAMPLE_EVERY or ww.step < ASSAY_FROM:
            return
        nX = ww.n["X"]
        if nX.sum() <= 0:
            return
        cy, cx, _ = SP.frechet_centre(nX)
        d = SP.dist_field(ww.L, cy, cx)
        ball = d <= PC.CORE_R
        m = V3.neighbour_count(nX)
        # one entry per MOLECULE, so the median is over molecules and not over cells
        vals = np.repeat(m[ball], nX[ball])
        if vals.size:
            per_frame.append({"step": int(ww.step), "n_molecules_in_core": int(vals.size),
                              "median_m": float(np.median(vals)),
                              "mean_m": float(vals.mean()),
                              "N_X": int(nX.sum())})

    t0 = time.time()
    with GC.start("calibration", "assay/C0/seed%d" % seed, ASSAY_HORIZON):
        GC.advance(w, ASSAY_HORIZON, per_step=per_step)
    return {"seed": seed, "wall_seconds": time.time() - t0, "frames": per_frame,
            "median_over_frames": float(np.median([f["median_m"] for f in per_frame]))
            if per_frame else float("nan")}


def main():
    seeds = M.CALIBRATION["assay_seeds"]
    forbidden = set(PC.SPEC["protocol"]["forbidden_seeds"])
    assert not (set(seeds) & forbidden), "calibration seed collides with a forbidden seed"
    arms = [assay_arm(s) for s in seeds]
    all_med = [f["median_m"] for a in arms for f in a["frames"]]
    m_star_raw = float(np.median(all_med)) if all_med else float("nan")
    m_star = int(round(m_star_raw)) if np.isfinite(m_star_raw) else 0
    lam = V3.lambda_from_m_star(m_star)
    out = {"rule": M.CALIBRATION, "assay_horizon": ASSAY_HORIZON,
           "assay_measured_from": ASSAY_FROM, "sample_every": SAMPLE_EVERY,
           "core_radius_cells": PC.CORE_R,
           "per_arm_median": {a["seed"]: a["median_over_frames"] for a in arms},
           "n_frames_pooled": len(all_med),
           "m_star_raw_median": m_star_raw, "m_star": m_star,
           "rounding": "to the nearest integer, declared with the rule",
           "lambda": lam,
           "mu_eff_at_m_star": (PC.POINT["muX"] * (1 - lam) ** m_star) if lam else None,
           "mu_X_isolated": PC.POINT["muX"],
           "ell_X_isolated": V3.effective_ell(PC.spec_for(), 0.0, 0),
           "ell_X_at_m_star": V3.effective_ell(PC.spec_for(), lam, m_star) if lam else None,
           "STATUS": "COHESION_CALIBRATION_FAIL" if not lam else "CALIBRATED",
           "ledger": GC.audit()}
    json.dump(out, open(f"{OUT}/_calibration.json", "w"), indent=1, default=str)
    for a in arms:
        print("  seed %d  median m over frames = %.2f  (%d frames)"
              % (a["seed"], a["median_over_frames"], len(a["frames"])))
    print()
    print("m_star (pooled median, rounded) = %d   from raw %.3f" % (m_star, m_star_raw))
    print("lambda = 1 - 2^(-1/m_star)      = %.6f" % lam if lam else "lambda UNDEFINED")
    if lam:
        print("mu_eff at m_star = %.6f  against mu_X = %.6f  (ratio %.3f)"
              % (out["mu_eff_at_m_star"], PC.POINT["muX"],
                 out["mu_eff_at_m_star"] / PC.POINT["muX"]))
        print("ell_X isolated = %.4f   ell_X at m_star = %.4f"
              % (out["ell_X_isolated"], out["ell_X_at_m_star"]))
    print("STATUS =", out["STATUS"])
    print("SCIENTIFIC_RUNS_USED =", GC.scientific_runs_used())


if __name__ == "__main__":
    main()

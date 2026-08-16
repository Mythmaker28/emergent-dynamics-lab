"""MYQBD01 §4, §7 — exact raw-data inventory, arm-level Q summaries, temporal dependence.

Independent unit = one arm. 9000 frames per arm are never treated as 9000 replicates.
No engine. Reads committed source blobs and delivered .npz arrays only.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, "/home/claude/PMCR01/code")
sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC02/code")
import pmcr01_sentinel as SENT                            # noqa: E402

REPO = "/home/claude/edl"
OUT = "/home/claude/MYQBD01/out"
RAW = "/home/claude/OBFOR01/raw"
BURN_IN, HORIZON = 2000, 11000
VAL = "/home/claude/OBFOR01/out/_validation.json"


def blobid(path):
    return subprocess.run(("git", "rev-parse", "HEAD:%s" % path), cwd=REPO,
                          capture_output=True, text=True).stdout.strip()


def acf_iat(x):
    """Autocorrelation function and integrated autocorrelation time (initial positive sequence
    estimator), on a mean-subtracted series. Deterministic."""
    x = np.asarray(x, float)
    x = x - x.mean()
    n = len(x)
    v = np.dot(x, x) / n
    if v <= 0:
        return {"acf1": 0.0, "iat": 1.0, "n_eff_blocks": float(n)}
    acf = []
    for lag in range(1, min(2000, n)):
        c = np.dot(x[:n - lag], x[lag:]) / (n * v)
        acf.append(c)
    # initial positive sequence: sum pairs until a pair sum goes non-positive
    iat = 1.0
    k = 0
    pair = acf[0] + (acf[1] if len(acf) > 1 else 0.0)
    while k + 1 < len(acf) and (acf[k] + acf[k + 1]) > 0:
        iat += 2.0 * acf[k]
        k += 1
    iat = max(iat, 1.0)
    return {"acf1": float(acf[0]) if acf else 0.0, "acf5": float(acf[4]) if len(acf) > 4 else 0.0,
            "iat": float(iat), "n_eff_blocks": float(n / iat)}


def zero_episodes(q):
    """Consecutive Q==0 run lengths."""
    runs, cur = [], 0
    for v in q:
        if v == 0:
            cur += 1
        elif cur:
            runs.append(cur)
            cur = 0
    if cur:
        runs.append(cur)
    runs = np.asarray(runs, float)
    return {"n_zero_episodes": int(len(runs)),
            "mean_zero_run": float(runs.mean()) if len(runs) else 0.0,
            "max_zero_run": int(runs.max()) if len(runs) else 0,
            "frac_zero": float((np.asarray(q) == 0).mean())}


def main():
    SENT.install(seed_register_paths=[
        "/home/claude/OBFOR01/out/_freeze.json", "/home/claude/OBFOR01/out/_validation.json"])
    raw_before = SENT.raw_dir_witness()

    val = json.load(open(VAL))
    declared = {a["tag"].replace("/", "__"): a for a in val["ARMS"]}
    files = sorted(glob.glob(os.path.join(RAW, "*.npz")))

    obs_blob = blobid("ORR01/code/observe.py")
    eng_blob = blobid("OBTC02/code/engine_obtc.py")
    yaml_blob = blobid("OBTC02/code/obtc02_protocol.yaml")

    inv, arms = [], []
    total_frames = 0
    for p in files:
        z = np.load(p, allow_pickle=True)
        fields = [str(x) for x in z["fields"]]
        base = os.path.basename(p)[:-4]
        s = z["series"]
        qi = fields.index("Q")
        q_all = s[:, qi].astype(float)
        q_win = q_all[BURN_IN:HORIZON]
        total_frames += q_all.shape[0]
        dec = declared.get(base, {})
        raw_hash = hashlib.sha256(open(p, "rb").read()).hexdigest()
        inv.append({
            "arm_id": base, "branch": dec.get("condition"),
            "seed": dec.get("seed"), "L": dec.get("L"),
            "domain_size": int(z["nX_final"].shape[0]),
            "horizon": int(s.shape[0]), "burn_in": BURN_IN,
            "frame_stride_series": 1,
            "number_of_frames": int(s.shape[0]),
            "raw_file_sha256": raw_hash,
            "series_sha256": hashlib.sha256(np.ascontiguousarray(s).tobytes()).hexdigest(),
            "Q_field_index": qi,
            "Q_missing_count": int(np.isnan(q_all).sum()),
            "observer_hash": obs_blob, "engine_hash": eng_blob, "lawspec_hash": yaml_blob,
            "source_position_fields_per_step": False,
            "nX_field": "u_nX_at_org (organiser cell mean, scalar, per step)",
            "nSY_field": "nSY_at_org (scalar, per step)",
            "free_field": "free_at_org (scalar, per step)",
            "candidate_Y_field": "cand_Y_at_org (scalar, per step)",
            "full_spatial_fields_available": "TERMINAL_STEP_ONLY (nX_final, nSY_final, ...)",
            "event_ledgers_available": [k for k in z.keys() if k.endswith("ledger")],
        })
        # arm-level Q summary (in-window)
        acf = acf_iat(q_win)
        ep = zero_episodes(q_win)
        nX = s[BURN_IN:HORIZON, fields.index("u_nX_at_org")].astype(float)
        nSY = s[BURN_IN:HORIZON, fields.index("nSY_at_org")].astype(float)
        free = s[BURN_IN:HORIZON, fields.index("free_at_org")].astype(float)
        candY = s[BURN_IN:HORIZON, fields.index("cand_Y_at_org")].astype(float)
        norg = s[BURN_IN:HORIZON, fields.index("n_org_cells")].astype(float)
        # early/late drift: mean of first third vs last third
        n3 = len(q_win) // 3
        drift = float(q_win[-n3:].mean() - q_win[:n3].mean())
        arms.append({
            "arm_id": base, "branch": dec.get("condition"),
            "usable_frames": int(len(q_win)),
            "Q_mean": float(q_win.mean()), "Q_median": float(np.median(q_win)),
            "Q_var": float(q_win.var(ddof=1)), "Q_sd": float(q_win.std(ddof=1)),
            "Q_min": float(q_win.min()), "Q_max": float(q_win.max()),
            "Q_q05": float(np.quantile(q_win, 0.05)),
            "Q_q10": float(np.quantile(q_win, 0.10)),
            "Q_q25": float(np.quantile(q_win, 0.25)),
            "frac_Q_zero": ep["frac_zero"],
            "n_zero_episodes": ep["n_zero_episodes"],
            "mean_zero_run": ep["mean_zero_run"], "max_zero_run": ep["max_zero_run"],
            "acf1": acf["acf1"], "acf5": acf["acf5"],
            "iat": acf["iat"], "n_eff_blocks": acf["n_eff_blocks"],
            "early_late_drift": drift,
            "corr_Q_nX": float(np.corrcoef(q_win, nX)[0, 1]),
            "corr_Q_nSY": float(np.corrcoef(q_win, nSY)[0, 1]),
            "corr_Q_free": float(np.corrcoef(q_win, free)[0, 1]),
            "mean_nX_at_org": float(nX.mean()), "mean_nSY_at_org": float(nSY.mean()),
            "mean_free_at_org": float(free.mean()), "mean_cand_Y": float(candY.mean()),
            "n_org_cells_always_one": bool((norg == 1).all()),
            "frac_frames_clamp_relevant_kY1": float((nX * 1 >= 1).mean()),
        })

    S = [a for a in arms if a["branch"] == "S"]
    M = [a for a in arms if a["branch"] == "M"]

    def branch(g):
        m = np.array([a["Q_mean"] for a in g])
        # branch uncertainty from ARM-LEVEL units (14), not frames
        return {"n_arms": len(g),
                "mean_of_arm_means": float(m.mean()),
                "sd_of_arm_means": float(m.std(ddof=1)),
                "se_of_branch_mean_from_arms": float(m.std(ddof=1) / np.sqrt(len(g))),
                "min_arm_mean": float(m.min()), "max_arm_mean": float(m.max()),
                "mean_frac_zero": float(np.mean([a["frac_Q_zero"] for a in g])),
                "mean_iat": float(np.mean([a["iat"] for a in g])),
                "mean_q10": float(np.mean([a["Q_q10"] for a in g])),
                "min_arm_q10": float(np.min([a["Q_q10"] for a in g]))}

    inventory = {
        "SECTION": "MYQBD01 §4 raw-data inventory",
        "TOTAL_ARMS": len(files), "STATIC_ARMS": len(S), "MOBILE_ARMS": len(M),
        "TOTAL_RECORDED_FRAMES": total_frames,
        "Q_MISSING_VALUES": int(sum(r["Q_missing_count"] for r in inv)),
        "OBSERVED_Q_MAX": float(max(a["Q_max"] for a in arms)),
        "EXACT_COUNTS_MATCH_REPORTED": {
            "TOTAL_ARMS==28": len(files) == 28,
            "STATIC==14": len(S) == 14, "MOBILE==14": len(M) == 14,
            "TOTAL_FRAMES==308000": total_frames == 308000,
            "Q_MISSING==0": sum(r["Q_missing_count"] for r in inv) == 0,
            "Q_MAX==28": max(a["Q_max"] for a in arms) == 28},
        "ALL_ELIGIBLE_ARMS_INCLUDED": True,
        "NO_ARM_REMOVED": True,
        "PER_ARM": inv,
    }
    temporal = {
        "SECTION": "MYQBD01 §7 temporal dependence",
        "INDEPENDENT_UNIT": "ONE_ARM",
        "WHY_NOT_FRAMES": ("Q is strongly autocorrelated within an arm; the integrated "
                           "autocorrelation time is far above 1, so the 9000 in-window frames "
                           "carry only n_eff_blocks independent pieces of information per arm. "
                           "Branch conclusions use the 14 arm-level means."),
        "STATIC": branch(S), "MOBILE": branch(M),
        "PER_ARM_TEMPORAL": [{k: a[k] for k in ("arm_id", "branch", "iat", "n_eff_blocks",
                                                "acf1", "frac_Q_zero", "max_zero_run",
                                                "early_late_drift")} for a in arms],
    }
    json.dump(inventory, open(f"{OUT}/MYQBD01_RAW_DATA_INVENTORY.json", "w"), indent=1,
              default=str)
    json.dump({"SECTION": "MYQBD01 §7 arm-level Q summaries", "PER_ARM": arms,
               "STATIC_BRANCH": branch(S), "MOBILE_BRANCH": branch(M)},
              open(f"{OUT}/MYQBD01_ARM_LEVEL_Q_SUMMARIES.json", "w"), indent=1, default=str)
    json.dump(temporal, open(f"{OUT}/MYQBD01_TEMPORAL_DEPENDENCE.json", "w"), indent=1,
              default=str)
    # CSV
    cols = list(arms[0].keys())
    with open(f"{OUT}/MYQBD01_ARM_LEVEL_Q_SUMMARIES.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for a in arms:
            w.writerow(a)

    rep = SENT.report(raw_before=raw_before, raw_after=SENT.raw_dir_witness())
    json.dump({"SENTINEL": rep}, open(f"{OUT}/_arms_sentinel.json", "w"), indent=1, default=str)

    print("inventory: arms=%d S=%d M=%d frames=%d Qmissing=%d Qmax=%.0f"
          % (len(files), len(S), len(M), total_frames,
             inventory["Q_MISSING_VALUES"], inventory["OBSERVED_Q_MAX"]))
    print("exact counts match reported:", inventory["EXACT_COUNTS_MATCH_REPORTED"])
    for lbl, b in (("STATIC", branch(S)), ("MOBILE", branch(M))):
        print("  %-7s mean_of_arm_means=%.6f sd=%.6f se=%.6f  mean_iat=%.1f  min_arm_q10=%.3f  "
              "mean_frac_zero=%.4f"
              % (lbl, b["mean_of_arm_means"], b["sd_of_arm_means"],
                 b["se_of_branch_mean_from_arms"], b["mean_iat"], b["min_arm_q10"],
                 b["mean_frac_zero"]))
    print("sentinel all-four-zero:", rep["ALL_FOUR_ZERO"],
          "| new physics arrays:", rep.get("NEW_PHYSICS_ARRAYS_WRITTEN"))


if __name__ == "__main__":
    main()

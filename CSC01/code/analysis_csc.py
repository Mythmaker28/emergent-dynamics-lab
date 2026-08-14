"""CSC01 — the confirmatory analysis and the figure."""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402

import observe as OBS             # noqa: E402

OUT, RAW = "/home/claude/CSC01/out", "/home/claude/CSC01/raw"
F = list(OBS.Recorder.FIELDS)
ARMS = ("C0_NO_CHANGE", "C3_NEIGHBOUR_PROTECTED_DECAY")


def main():
    d = json.load(open(f"{OUT}/_results.json"))
    per = {a: [] for a in ARMS}
    for p in d["pairs"]:
        for a in ARMS:
            r = p[a]
            c = r["gate_posthoc"].get("checks", {})
            per[a].append({
                "seed": r["seed"], "classification": r["classification"],
                "formed_at": r["gate_posthoc"].get("formed_at"),
                "N_X_window_mean": r["N_X"]["window_mean"],
                "cohesion_fraction": c.get("cohesive_vs_N3b_fraction"),
                "core_exists_fraction": c.get("core_exists_fraction"),
                "compact_vs_N1_fraction": c.get("compact_vs_N1_fraction"),
                "turnover": c.get("material_turnover"),
                "mu_effective": r["gate_posthoc"]["stats"].get("mu_effective_observed"),
                "core_free": c.get("core_free_capacity_mean"),
                "occupancy_drift": r["occupancy"]["drift"],
                "occupancy_exactly_constant": r["occupancy"]["exactly_constant"],
                "longest_excursion": c.get("longest_excursion"),
                "GATES_AGREE": r["GATES_AGREE"]})

    def agg(a, k):
        v = [x[k] for x in per[a] if x[k] is not None]
        return {"n": len(v), "mean": float(np.mean(v)) if v else None,
                "median": float(np.median(v)) if v else None,
                "min": float(np.min(v)) if v else None, "max": float(np.max(v)) if v else None,
                "values": v}

    summary = {a: {k: agg(a, k) for k in
                   ("cohesion_fraction", "core_exists_fraction", "N_X_window_mean", "turnover",
                    "mu_effective", "core_free", "occupancy_drift")} for a in ARMS}
    classes = {a: {} for a in ARMS}
    for a in ARMS:
        for x in per[a]:
            classes[a][x["classification"]] = classes[a].get(x["classification"], 0) + 1

    # the paired difference in the cohesion statistic, seed by seed
    paired = []
    for p in d["pairs"]:
        c0 = p["C0_NO_CHANGE"]["gate_posthoc"].get("checks", {}).get("cohesive_vs_N3b_fraction")
        c3 = p["C3_NEIGHBOUR_PROTECTED_DECAY"]["gate_posthoc"].get(
            "checks", {}).get("cohesive_vs_N3b_fraction")
        if c0 is not None and c3 is not None:
            paired.append({"seed": p["C0_NO_CHANGE"]["seed"], "C0": c0, "C3": c3,
                           "difference": c3 - c0})
    diffs = [x["difference"] for x in paired]
    # exact two-sided sign test on the paired differences
    from math import comb
    pos = sum(1 for x in diffs if x > 0)
    neg = sum(1 for x in diffs if x < 0)
    n = pos + neg
    k = min(pos, neg)
    p_two = min(1.0, 2.0 * sum(comb(n, i) for i in range(k + 1)) / (2.0 ** n)) if n else None

    out = {"per_arm": per, "summary": summary, "class_counts": classes,
           "paired_cohesion_statistic": paired,
           "paired_difference": {"mean": float(np.mean(diffs)) if diffs else None,
                                 "n_positive": pos, "n_negative": neg, "n_pairs": len(diffs),
                                 "exact_two_sided_sign_test_p": p_two,
                                 "reading": "the sign test is DESCRIPTIVE. The frozen success "
                                            "criterion is 5 of 6 arms COHESION_ACHIEVED, and "
                                            "that criterion is what decides the disposition."},
           "controls": [{"tag": c["tag"], "classification": c["classification"],
                         "N_X_max": c["N_X"]["max"], "N_X_final": c["N_X"]["final"],
                         "GATES_AGREE": c["GATES_AGREE"]} for c in d["controls"]],
           "gates_agree_everywhere": bool(all(x["GATES_AGREE"] for a in ARMS for x in per[a])
                                          and all(c["GATES_AGREE"] for c in d["controls"])),
           "summary_line": d["summary"]}
    json.dump(out, open(f"{OUT}/_analysis.json", "w"), indent=1, default=str)

    # ---------------------------------------------------------------- figure
    fig, ax = plt.subplots(2, 2, figsize=(11.5, 8))
    colours = {"C0_NO_CHANGE": "#3b6ea5", "C3_NEIGHBOUR_PROTECTED_DECAY": "#b4442e"}
    for a in ARMS:
        for p in d["pairs"]:
            r = p[a]
            arr = np.load(f"{RAW}/{r['raw_npz']}")["series"]
            ax[0, 0].plot(arr[:, F.index("step")], arr[:, F.index("N_X")],
                          color=colours[a], lw=0.6, alpha=0.7)
    ax[0, 0].set_xlabel("step")
    ax[0, 0].set_ylabel("N_X")
    ax[0, 0].set_title("population, six paired seeds")
    ax[0, 0].plot([], [], color=colours["C0_NO_CHANGE"], label="C0 reference")
    ax[0, 0].plot([], [], color=colours["C3_NEIGHBOUR_PROTECTED_DECAY"], label="C3 mechanism")
    ax[0, 0].legend(fontsize=8)

    x = np.arange(len(paired))
    ax[0, 1].bar(x - 0.2, [p["C0"] for p in paired], 0.4, color=colours["C0_NO_CHANGE"],
                 label="C0 reference")
    ax[0, 1].bar(x + 0.2, [p["C3"] for p in paired], 0.4,
                 color=colours["C3_NEIGHBOUR_PROTECTED_DECAY"], label="C3 mechanism")
    ax[0, 1].axhline(0.80, color="k", ls="--", lw=1)
    ax[0, 1].text(0.02, 0.82, "declared threshold 0.80", fontsize=8, transform=ax[0, 1].transAxes)
    ax[0, 1].set_xticks(x)
    ax[0, 1].set_xticklabels([p["seed"] for p in paired], fontsize=8)
    ax[0, 1].set_ylabel("fraction of instants below the N3b q05", fontsize=9)
    ax[0, 1].set_title("the cohesion statistic, paired")
    ax[0, 1].legend(fontsize=8)

    for a in ARMS:
        ax[1, 0].scatter([x["core_exists_fraction"] for x in per[a] if x["core_exists_fraction"]],
                         [x["cohesion_fraction"] for x in per[a] if x["core_exists_fraction"]],
                         color=colours[a], s=42, label=a.split("_")[0])
    ax[1, 0].axvline(0.90, color="k", ls="--", lw=1)
    ax[1, 0].axhline(0.80, color="k", ls="--", lw=1)
    ax[1, 0].set_xlabel("axis 2: fraction of frames with a core")
    ax[1, 0].set_ylabel("axis 1: cohesion statistic")
    ax[1, 0].set_title("the two axes that decide, with their thresholds")
    ax[1, 0].legend(fontsize=8)

    sa = json.load(open(f"{OUT}/_stage_a.json"))
    labels = ["N1\ncomplete\nrandomness", "N4\nlabel\npermutation", "N3\nstatic\npoint source",
              "N3b\nwandering\npoint source"]
    vals = []
    for k in ("N1", "N4", "N3"):
        vals.append(np.mean([r["N%s_r80_observed_quantile" % ("1" if k == "N1" else "3")]
                             if k in ("N1", "N3") else 0.0 for r in sa["per_arm"]]))
    vals = [np.mean([r["N1_r80_observed_quantile"] for r in sa["per_arm"]]),
            0.0,
            np.mean([r["N3_r80_observed_quantile"] for r in sa["per_arm"]]),
            np.mean([v["r80"]["mean_observed_quantile"]
                     for v in sa["N3b_observed_quantiles"].values()])]
    ax[1, 1].bar(range(4), vals, color=["#777", "#777", "#b4442e", "#b4442e"])
    ax[1, 1].axhline(0.05, color="k", ls="--", lw=1)
    ax[1, 1].set_ylim(0, 1)
    ax[1, 1].set_xticks(range(4))
    ax[1, 1].set_xticklabels(labels, fontsize=7)
    ax[1, 1].set_ylabel("quantile of the observed r80 in the null", fontsize=9)
    ax[1, 1].set_title("ORR01 autopsy: localised, but only\nas much as a point source", fontsize=10)
    fig.suptitle("CSC01 — the inherited cloud is source-tethered; the selected mechanism raises "
                 "cohesion without qualifying it", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(f"{OUT}/csc01_cohesion.png", dpi=140)
    print("wrote %s/csc01_cohesion.png" % OUT)

    for a in ARMS:
        print("%-30s %s" % (a, classes[a]))
    print("cohesion statistic  C0 mean %.3f   C3 mean %.3f"
          % (summary["C0_NO_CHANGE"]["cohesion_fraction"]["mean"],
             summary["C3_NEIGHBOUR_PROTECTED_DECAY"]["cohesion_fraction"]["mean"]))
    print("core-exists         C0 mean %.3f   C3 mean %.3f"
          % (summary["C0_NO_CHANGE"]["core_exists_fraction"]["mean"],
             summary["C3_NEIGHBOUR_PROTECTED_DECAY"]["core_exists_fraction"]["mean"]))
    print("mu effective        C0 %.6f      C3 %.6f"
          % (summary["C0_NO_CHANGE"]["mu_effective"]["mean"],
             summary["C3_NEIGHBOUR_PROTECTED_DECAY"]["mu_effective"]["mean"]))
    print("paired difference   mean %.3f  positive %d of %d  exact sign test p = %s"
          % (out["paired_difference"]["mean"], pos, len(diffs), p_two))
    print("gates agree everywhere:", out["gates_agree_everywhere"])


if __name__ == "__main__":
    main()

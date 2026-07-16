"""V4.1 reconciliation analysis using committed artifacts only.

No simulation is launched. The script reads the canonical V4 raw artifacts and
recomputes all manuscript headline results with original-world grouped outer
validation.

Primary inferential unit
------------------------
An original world is identified by the simulation seed. Each world was branched
across the same history grid. Outer validation therefore leaves one seed/world
out at a time. This prevents rows descended from the same original world from
appearing in both training and testing.

Uncertainty
-----------
The repository contains only 3 original worlds for the longitudinal and
transplant analyses, 2 for the in-place analysis, and 4 for the historical
body-baseline comparison. We report:

* fold-level R2 values, one per held-out original world;
* a small-sample t interval across those fold values (descriptive, fragile);
* an exact world-block percentile interval over fixed out-of-world predictions.

The latter has only W**W ordered resamples and is not presented as a reliable
nominal 95% confidence interval when W is this small.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import pickle
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
from scipy.stats import t as student_t

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RIDGE_LAMBDA = 1.0
THRESHOLD = 0.50
BOOT_SEED_V4 = 20260715
N_BOOT_V4 = 3000

SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[4]
V41 = SCRIPT.parents[1]
FIGURES = V41 / "figures"
OUTPUTS = V41 / "outputs"

LONGITUDINAL_RAW = REPO / "results" / "observer" / "tca_holdout_raw.pkl"
CAUSAL_TRANSPLANT_RAW = (
    REPO / "results" / "wd01_phasec" / "phasec_causal_transplant_raw.pkl"
)
CAUSAL_INPLACE_RAW = (
    REPO / "results" / "wd01_phasec" / "phasec_causal_inplace_raw.pkl"
)
H2CERT_RAW = REPO / "results" / "h2cert" / "h2cert_sealed_raw.pkl"

CHECKPOINTS = ((0, "initial"), (400, "moderate"), (650, "deep_1"), (800, "deep"))


def load_pickle(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def r2(y: np.ndarray, prediction: np.ndarray) -> float:
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - residual / total if total > 0 else float("nan")


def ridge_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    ridge_lambda: float = RIDGE_LAMBDA,
) -> np.ndarray:
    """Fit on one outer-training set and predict its held-out world."""
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    keep = std > 1e-9
    if not np.any(keep):
        return np.full(len(x_test), y_train.mean(), dtype=float)

    train = (x_train[:, keep] - mean[keep]) / std[keep]
    test = (x_test[:, keep] - mean[keep]) / std[keep]
    intercept = y_train.mean()
    lhs = train.T @ train + ridge_lambda * np.eye(int(np.sum(keep)))
    weights = np.linalg.solve(lhs, train.T @ (y_train - intercept))
    return test @ weights + intercept


def grouped_oof(
    x: np.ndarray, y: np.ndarray, groups: np.ndarray
) -> tuple[np.ndarray, dict[str, float]]:
    prediction = np.full(len(y), np.nan, dtype=float)
    fold_scores: dict[str, float] = {}
    for group in np.unique(groups):
        test = groups == group
        train = ~test
        prediction[test] = ridge_predict(x[train], y[train], x[test])
        fold_scores[str(int(group))] = r2(y[test], prediction[test])
    return prediction, fold_scores


def crossed_oof(
    x: np.ndarray,
    y: np.ndarray,
    worlds: np.ndarray,
    histories: np.ndarray,
) -> np.ndarray:
    """Sensitivity: each test row excludes both its world and its history."""
    prediction = np.full(len(y), np.nan, dtype=float)
    for index in range(len(y)):
        train = (worlds != worlds[index]) & (histories != histories[index])
        prediction[index] = ridge_predict(x[train], y[train], x[index : index + 1])[0]
    return prediction


def descriptive_t_interval(fold_values: np.ndarray) -> list[float]:
    n_worlds = len(fold_values)
    if n_worlds < 2:
        return [float("nan"), float("nan")]
    critical = float(student_t.ppf(0.975, n_worlds - 1))
    standard_error = float(fold_values.std(ddof=1) / math.sqrt(n_worlds))
    mean = float(fold_values.mean())
    return [mean - critical * standard_error, mean + critical * standard_error]


def exact_world_block_interval(
    y: np.ndarray,
    prediction: np.ndarray,
    worlds: np.ndarray,
) -> dict[str, Any]:
    unique_worlds = np.unique(worlds)
    values: list[float] = []
    for picked in itertools.product(unique_worlds, repeat=len(unique_worlds)):
        indices = np.concatenate([np.flatnonzero(worlds == world) for world in picked])
        values.append(r2(y[indices], prediction[indices]))
    array = np.asarray(values, dtype=float)
    return {
        "ordered_resamples": int(len(array)),
        "percentile_2_5_50_97_5": [
            float(value) for value in np.percentile(array, [2.5, 50.0, 97.5])
        ],
        "min": float(array.min()),
        "max": float(array.max()),
        "nominal_coverage_warning": (
            "Descriptive only: too few original worlds for a reliable nominal "
            "95% cluster-bootstrap confidence interval."
        ),
    }


def result_block(
    x: np.ndarray,
    y: np.ndarray,
    worlds: np.ndarray,
    histories: np.ndarray,
) -> dict[str, Any]:
    world_prediction, fold_scores = grouped_oof(x, y, worlds)
    history_prediction, _ = grouped_oof(x, y, histories)
    crossed_prediction = crossed_oof(x, y, worlds, histories)
    folds = np.asarray(list(fold_scores.values()), dtype=float)
    return {
        "world_grouped_point_r2": r2(y, world_prediction),
        "world_fold_r2": fold_scores,
        "world_fold_mean_r2": float(folds.mean()),
        "world_fold_t_interval_95_descriptive": descriptive_t_interval(folds),
        "world_block_resampling": exact_world_block_interval(y, world_prediction, worlds),
        "history_grouped_v4_point_r2": r2(y, history_prediction),
        "crossed_world_and_history_exclusion_r2": r2(y, crossed_prediction),
        "n_rows": int(len(y)),
        "n_original_worlds": int(len(np.unique(worlds))),
        "n_histories": int(len(np.unique(histories))),
        "_prediction": world_prediction,
    }


def longitudinal_features(record: dict[str, Any], step: int, tracker: str) -> np.ndarray:
    packed = record["ck"][step][tracker]
    return np.asarray(list(packed[0]) + [packed[3]], dtype=float)


def audit_v4_bootstrap() -> dict[str, Any]:
    rng = np.random.default_rng(BOOT_SEED_V4)
    unique_counts: list[int] = []
    for _ in range(N_BOOT_V4):
        picked = rng.choice(np.arange(12), size=12, replace=True)
        unique_counts.append(int(len(np.unique(picked))))
    all_unique = sum(count == 12 for count in unique_counts)
    theoretical_all_unique = math.factorial(12) / (12**12)
    return {
        "v4_bootstrap_replicates": N_BOOT_V4,
        "replicates_with_at_least_one_duplicate_history": N_BOOT_V4 - all_unique,
        "replicates_with_all_unique_histories": all_unique,
        "theoretical_probability_all_unique": theoretical_all_unique,
        "theoretical_probability_at_least_one_duplicate": 1.0
        - theoretical_all_unique,
        "unique_history_count_distribution": {
            str(count): unique_counts.count(count) for count in sorted(set(unique_counts))
        },
        "leakage_finding": (
            "V4 assigned each duplicate draw a new fold id. Every one of the 3000 "
            "realized bootstrap replicates therefore placed exact duplicated "
            "original-world rows in both training and testing."
        ),
    }


def strip_predictions(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_predictions(child)
            for key, child in value.items()
            if key != "_prediction"
        }
    if isinstance(value, list):
        return [strip_predictions(child) for child in value]
    return value


def paired_difference(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    first_values = np.asarray(list(first["world_fold_r2"].values()), dtype=float)
    second_values = np.asarray(list(second["world_fold_r2"].values()), dtype=float)
    difference = first_values - second_values
    return {
        "mean_difference_r2": float(difference.mean()),
        "world_fold_differences": [float(value) for value in difference],
        "world_fold_t_interval_95_descriptive": descriptive_t_interval(difference),
    }


def analyse() -> dict[str, Any]:
    records = load_pickle(LONGITUDINAL_RAW)
    worlds = np.asarray([record["seed"] for record in records])
    histories = np.asarray([record["hi"] for record in records])

    longitudinal: dict[str, Any] = {}
    for step, label in CHECKPOINTS:
        checkpoint: dict[str, Any] = {}
        for coordinate in ("h1", "h2"):
            x = np.asarray(
                [longitudinal_features(record, step, "long") for record in records]
            )
            y = np.asarray([record[coordinate] for record in records], dtype=float)
            checkpoint[coordinate] = result_block(x, y, worlds, histories)
        checkpoint["mean_M"] = float(
            np.mean([record["ck"][step]["long"][1] for record in records])
        )
        checkpoint["at_or_below_M_0_25"] = int(
            sum(record["ck"][step]["long"][1] <= 0.25 for record in records)
        )
        longitudinal[label] = checkpoint

    deep_long = result_block(
        np.asarray([longitudinal_features(record, 800, "long") for record in records]),
        np.asarray([record["h1"] for record in records], dtype=float),
        worlds,
        histories,
    )
    deep_largest = result_block(
        np.asarray(
            [longitudinal_features(record, 800, "largest") for record in records]
        ),
        np.asarray([record["h1"] for record in records], dtype=float),
        worlds,
        histories,
    )

    causal_transplant = load_pickle(CAUSAL_TRANSPLANT_RAW)
    transplant_worlds = np.asarray([record["seed"] for record in causal_transplant])
    transplant_histories = np.asarray([record["hi"] for record in causal_transplant])
    causal: dict[str, Any] = {}
    for coordinate in ("h1", "h2"):
        y = np.asarray([record[coordinate] for record in causal_transplant], dtype=float)
        for key in ("R_full", "R_both0", "R_erase"):
            x = np.asarray([record[key] for record in causal_transplant], dtype=float)
            causal[f"transplant_{key}_{coordinate}"] = result_block(
                x, y, transplant_worlds, transplant_histories
            )

    causal_inplace = load_pickle(CAUSAL_INPLACE_RAW)
    inplace_worlds = np.asarray([record["seed"] for record in causal_inplace])
    inplace_histories = np.asarray([record["hi"] for record in causal_inplace])
    for coordinate in ("h1", "h2"):
        y = np.asarray([record[coordinate] for record in causal_inplace], dtype=float)
        x = np.asarray(
            [
                np.asarray(record["Rfull"], dtype=float)
                - np.asarray(record["Rboth0"], dtype=float)
                for record in causal_inplace
            ]
        )
        causal[f"inplace_delta_{coordinate}"] = result_block(
            x, y, inplace_worlds, inplace_histories
        )

    h2cert = load_pickle(H2CERT_RAW)
    baseline_worlds = np.asarray([record["seed"] for record in h2cert])
    baseline_histories = np.asarray([record["hi"] for record in h2cert])
    baseline_y = np.asarray([record["h1"] for record in h2cert], dtype=float)
    body_baseline: dict[str, Any] = {}
    for step, label in ((0, "initial"), (650, "deep")):
        memory = result_block(
            np.asarray([record["traj"][step]["all"] for record in h2cert], dtype=float),
            baseline_y,
            baseline_worlds,
            baseline_histories,
        )
        body = result_block(
            np.asarray(
                [
                    [
                        record["traj"][step]["size"],
                        record["traj"][step]["mass"],
                    ]
                    for record in h2cert
                ],
                dtype=float,
            ),
            baseline_y,
            baseline_worlds,
            baseline_histories,
        )
        body_baseline[label] = {
            "memory_features": memory,
            "body_size_and_mass": body,
            "paired_memory_minus_body": paired_difference(memory, body),
            "tracker_warning": (
                "This historical H2-CERT comparison used largest-component "
                "reselection, not the later longitudinal tracker."
            ),
        }

    results = {
        "analysis": {
            "name": "ORGANIZATIONAL-MEMORY-PAPER-V4.1-RECONCILIATION",
            "no_new_simulations": True,
            "ridge_lambda": RIDGE_LAMBDA,
            "primary_outer_group": "original world (simulation seed)",
            "threshold": THRESHOLD,
            "uncertainty_warning": (
                "Only 2-4 original worlds are available. World-fold t intervals "
                "and exact block resampling are descriptive and cannot support "
                "high-confidence certification."
            ),
        },
        "v4_bootstrap_audit": audit_v4_bootstrap(),
        "longitudinal": longitudinal,
        "tracker_sensitivity": {
            "longitudinal": deep_long,
            "largest_at_each_frame": deep_largest,
            "paired_longitudinal_minus_largest": paired_difference(
                deep_long, deep_largest
            ),
            "fusion_audit": {
                "event_level_masks_or_edges_committed": False,
                "merge_or_fusion_flags_present_in_raw": False,
                "finding": (
                    "The summary raw artifact contains lost/switch flags but no "
                    "mask-overlap edges, ambiguity alternatives, or merge/fusion "
                    "events. Actual fusion handling cannot be independently "
                    "reconstructed without new simulation."
                ),
            },
        },
        "causal": causal,
        "body_baseline": body_baseline,
        "observed_counts": {
            "records": len(records),
            "original_worlds": len(np.unique(worlds)),
            "histories": len(np.unique(histories)),
            "survived": len(records)
            - sum(bool(record.get("lost", False)) for record in records),
            "lost": sum(bool(record.get("lost", False)) for record in records),
            "recorded_switches": sum(
                int(record.get("switch", 0)) for record in records
            ),
            "deep_M_at_or_below_0_25": sum(
                record["ck"][800]["long"][1] <= 0.25 for record in records
            ),
        },
    }
    return results


def write_prediction_rows(results: dict[str, Any]) -> None:
    records = load_pickle(LONGITUDINAL_RAW)
    worlds = np.asarray([record["seed"] for record in records])
    histories = np.asarray([record["hi"] for record in records])
    path = OUTPUTS / "longitudinal_world_oof_predictions.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "checkpoint",
                "step",
                "seed",
                "history",
                "coordinate",
                "truth",
                "prediction",
                "M",
                "tracker",
            ]
        )
        for step, label in CHECKPOINTS:
            x = np.asarray(
                [longitudinal_features(record, step, "long") for record in records]
            )
            for coordinate in ("h1", "h2"):
                y = np.asarray([record[coordinate] for record in records], dtype=float)
                prediction, _ = grouped_oof(x, y, worlds)
                for index, record in enumerate(records):
                    writer.writerow(
                        [
                            label,
                            step,
                            int(worlds[index]),
                            int(histories[index]),
                            coordinate,
                            float(y[index]),
                            float(prediction[index]),
                            float(record["ck"][step]["long"][1]),
                            "longitudinal",
                        ]
                    )


def make_figures(results: dict[str, Any]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)

    labels = ["initial", "moderate", "deep_1", "deep"]
    m_values = [results["longitudinal"][label]["mean_M"] for label in labels]
    colors = {"h1": "#155f45", "h2": "#9d2b25"}

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for axis, coordinate in zip(axes, ("h1", "h2")):
        points = [
            results["longitudinal"][label][coordinate]["world_grouped_point_r2"]
            for label in labels
        ]
        lows = [
            results["longitudinal"][label][coordinate][
                "world_fold_t_interval_95_descriptive"
            ][0]
            for label in labels
        ]
        highs = [
            results["longitudinal"][label][coordinate][
                "world_fold_t_interval_95_descriptive"
            ][1]
            for label in labels
        ]
        yerr = np.vstack(
            [np.asarray(points) - np.asarray(lows), np.asarray(highs) - np.asarray(points)]
        )
        axis.errorbar(
            m_values,
            points,
            yerr=yerr,
            fmt="o-",
            color=colors[coordinate],
            capsize=4,
            lw=2,
        )
        axis.axhline(THRESHOLD, color="0.35", ls="--", lw=1.2)
        axis.axhline(0.0, color="0.7", lw=0.8)
        axis.set_xlim(1.05, 0.12)
        axis.set_ylim((0.0, 1.45) if coordinate == "h1" else (-6.0, 3.6))
        axis.set_xlabel("mean surviving original-material fraction M")
        axis.set_title(
            "$h_1$ cumulative drive" if coordinate == "h1" else "$h_2$ order contrast"
        )
    axes[0].set_ylabel("leave-one-original-world-out $R^2$")
    fig.suptitle(
        "V4.1 grouped reconciliation (bars: descriptive world-fold t intervals; W=3)"
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_world_grouped_longitudinal.png", dpi=180)
    plt.close(fig)

    tracker = results["tracker_sensitivity"]
    names = ["Longitudinal", "Largest each frame"]
    points = [
        tracker["longitudinal"]["world_grouped_point_r2"],
        tracker["largest_at_each_frame"]["world_grouped_point_r2"],
    ]
    fold_matrix = np.asarray(
        [
            list(tracker["longitudinal"]["world_fold_r2"].values()),
            list(tracker["largest_at_each_frame"]["world_fold_r2"].values()),
        ]
    )
    fig, axis = plt.subplots(figsize=(7.2, 4.5))
    for column in range(fold_matrix.shape[1]):
        axis.plot(names, fold_matrix[:, column], "o-", color="0.55", alpha=0.85)
    axis.scatter(names, points, color=["#155f45", "#365f91"], s=80, zorder=3)
    axis.axhline(THRESHOLD, color="0.35", ls="--", lw=1.2)
    axis.set_ylabel("held-out-world $R^2$ for $h_1$ at deep turnover")
    axis.set_title("Tracker sensitivity is small relative to world-to-world variation")
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_tracker_world_sensitivity.png", dpi=180)
    plt.close(fig)

    causal = results["causal"]
    baseline = results["body_baseline"]["deep"]
    labels_c = ["Transplant\nfull", "Transplant\ninert", "Memory\nfeatures", "Size + mass"]
    values_c = [
        causal["transplant_R_full_h1"]["world_grouped_point_r2"],
        causal["transplant_R_both0_h1"]["world_grouped_point_r2"],
        baseline["memory_features"]["world_grouped_point_r2"],
        baseline["body_size_and_mass"]["world_grouped_point_r2"],
    ]
    colors_c = ["#155f45", "#777777", "#6d4c9b", "#c28c2c"]
    fig, axis = plt.subplots(figsize=(8.5, 4.6))
    axis.bar(labels_c, values_c, color=colors_c)
    axis.axhline(THRESHOLD, color="0.35", ls="--", lw=1.2)
    axis.axhline(0.0, color="0.65", lw=0.8)
    axis.set_ylabel("leave-one-original-world-out $R^2$")
    axis.set_title("Secondary V4.1 reanalyses (different artifact families)")
    axis.text(
        0.02,
        0.96,
        "Transplant W=3; baseline W=4 and uses historical largest-component reselection.",
        transform=axis.transAxes,
        fontsize=8,
        color="0.35",
        va="top",
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_secondary_reconciliation.png", dpi=180)
    plt.close(fig)


def write_reconciliation_csv(results: dict[str, Any]) -> None:
    rows = [
        (
            "h1 initial",
            "0.7846 [0.5571,0.9438]",
            "0.7382; descriptive world-t interval [0.3026,1.1738]",
            "CORRECTED",
            "Outer grouping changed from history to original world.",
        ),
        (
            "h1 moderate",
            "0.9328 [0.8892,0.9789]",
            "0.9020; descriptive world-t interval [0.7851,1.0189]",
            "CORRECTED",
            "Point remains high; V4 interval withdrawn.",
        ),
        (
            "h1 deep-1",
            "0.8970 [0.8596,0.9740]",
            "0.8432; descriptive world-t interval [0.5448,1.1416]",
            "CORRECTED",
            "Only three independent worlds.",
        ),
        (
            "h1 deep headline",
            "0.8878 [0.8366,0.9581], CERTIFIED",
            "0.6947; descriptive world-t interval [0.0513,1.3381]",
            "WITHDRAWN",
            "The lower bound no longer clears 0.50; certification is withdrawn.",
        ),
        (
            "h2 initial",
            "0.8010 [0.5318,0.9224]",
            "0.7631; descriptive world-t interval [0.5701,0.9561]",
            "CORRECTED",
            "World-grouped point remains positive.",
        ),
        (
            "h2 deep headline",
            "-0.2394 [-0.7850,0.3182]",
            "-1.1183; descriptive world-t interval [-5.6757,3.4390]",
            "CORRECTED",
            "Not established under either analysis; world variation is much larger.",
        ),
        (
            "track survival",
            "36/36",
            "36/36 recorded surviving",
            "UNCHANGED",
            "Artifact count reproduces; event-level fusion audit is unavailable.",
        ),
        (
            "recorded reassignment switches",
            "0",
            "0",
            "UNCHANGED",
            "Raw summary flag reproduces.",
        ),
        (
            "deep M",
            "mean 0.1902; 94% <= 0.25",
            "mean 0.1902; 34/36 <= 0.25",
            "UNCHANGED",
            "Directly regenerated from committed raw records.",
        ),
        (
            "tracker sensitivity h1 deep",
            "0.8878 longitudinal / 0.9123 largest",
            "0.6947 longitudinal / 0.6706 largest",
            "CORRECTED",
            "Paired mean difference 0.0241; tracker similarity supports global content, not local storage.",
        ),
        (
            "transplant h1",
            "0.61 [-0.69,0.87]",
            "0.6468; descriptive world-t interval [0.5074,0.7861]",
            "CORRECTED",
            "Canonical 5-D response-vector decoder; W=3 donor worlds and one common recipient body.",
        ),
        (
            "transplant inert / erase h1",
            "-0.19 / -0.19",
            "0.0000 / 0.0000",
            "CORRECTED",
            "Under world-held-out validation the constant controls equal the no-information baseline.",
        ),
        (
            "in-place delta h1",
            "0.50 [-1.39,0.92]",
            "0.7039; descriptive world-t interval [-1.0663,2.4741]",
            "CORRECTED",
            "Only two original worlds; no inferential claim is retained.",
        ),
        (
            "deep memory vs size+mass",
            "0.93 vs 0.64",
            "0.7692 vs 0.4538; paired difference 0.3154 [-0.2394,0.8701]",
            "CORRECTED",
            "Historical largest-component data; difference not separated.",
        ),
        (
            "local storage claim",
            "Droplet-level organizational memory wording",
            "No local-specific estimate available",
            "WITHDRAWN",
            "History was imposed globally and local/environment access structures were not separated.",
        ),
        (
            "fusion-free continuity claim",
            "Implicit in 36/36 longitudinal continuity",
            "Not independently reconstructable",
            "WITHDRAWN",
            "No committed masks, association edges, or fusion/merge event records.",
        ),
    ]
    path = V41 / "numerical_reconciliation.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["quantity", "V4.0 canonical", "V4.1 grouped result", "classification", "reason"]
        )
        writer.writerows(rows)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    results = analyse()
    write_prediction_rows(results)
    make_figures(results)
    write_reconciliation_csv(results)

    public_results = strip_predictions(results)
    with (V41 / "headline_results_v4_1.json").open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        json.dump(public_results, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("V4.1 reconciliation analysis complete")
    print(f"  input:  {LONGITUDINAL_RAW.relative_to(REPO)}")
    print(f"  output: {(V41 / 'headline_results_v4_1.json').relative_to(REPO)}")
    print(
        "  deep h1 world-grouped R2 = "
        f"{results['longitudinal']['deep']['h1']['world_grouped_point_r2']:.6f}"
    )
    print(
        "  V4 bootstrap duplicate leakage = "
        f"{results['v4_bootstrap_audit']['replicates_with_at_least_one_duplicate_history']}"
        f"/{N_BOOT_V4}"
    )


if __name__ == "__main__":
    main()

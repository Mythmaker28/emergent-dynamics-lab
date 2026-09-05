"""Recompute manuscript statistics and generate figures from committed bytes only.

This script never imports the simulation engine or executes a seed. It reads exact
Git blobs from the three protected source histories, independently recomputes the
V4.1 grouped longitudinal statistics and CONFIRM-02 raw contrasts, invokes the
independent 03M raw-only turnover implementation, and emits paper-only artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import math
import pickle
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
from scipy.stats import t as student_t

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


V41 = "847d51ef78d0d55d30f05df275d97aa4af0c558f"
V40 = "23b53aee4169deeda30aad2a9dba8587024f8d3d"
CONFIRM_PRESEAL = "9b7580bc3a09293a4b0b19b70cff8c39c5cb1378"
CONFIRM_RESULT = "830c2d006f5278295e965887f8ccedee34d47e67"
CONFIRM_ADDENDUM = "9c8a62cd3f6794eb9ac435f638671e5561086cd0"
TURNOVER_AUTHORIZATION = "c158bc0b848710edeafd425f31dfcbd5aefc0934"
TURNOVER_RESULT = "9cb996bb891f9a618e593f2f5c302f30210458de"
RAW_REPRODUCTION = "a8d6446fade6dbeb984e269fab27ddd5ebf75286"
FINAL_SEAL_SHA256 = "cdf7277a00e3017a1389e9334d983364b9aa0af88c646cdec2999e6ad88757fd"

SCRIPT = Path(__file__).resolve()
PAPER = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
DATA = PAPER / "data"
FIGURES = PAPER / "figures"

SOURCE_SPECS = [
    (V41, "paper/organizational-memory-v4-1-reconciliation/v4.1/NUMERICAL_RECONCILIATION.md", "V4.1 correction ledger"),
    (V41, "paper/organizational-memory-v4-1-reconciliation/v4.1/headline_results_v4_1.json", "V4.1 machine results"),
    (V41, "paper/organizational-memory-v4-1-reconciliation/v4.1/scripts/reconcile_v4_1.py", "V4.1 grouped estimator"),
    (V41, "results/observer/tca_holdout_raw.pkl", "V4.1 committed longitudinal raw"),
    (V41, "docs/paper/full/ORGANIZATIONAL_MEMORY_FULL_MANUSCRIPT_V4.tex", "preserved V4.0 manuscript source"),
    (CONFIRM_PRESEAL, "docs/individuation/NONMERGING_CONFIRM_PROTOCOL_02.md", "CONFIRM-02 frozen protocol"),
    (CONFIRM_RESULT, "experiments/individuation/nonmerging_confirm_raw.json", "CONFIRM-02 committed raw"),
    (CONFIRM_RESULT, "docs/individuation/NONMERGING_CONFIRM_CERTIFICATE_02.json", "CONFIRM-02 certificate"),
    (TURNOVER_RESULT, "docs/individuation/TURNOVER_PROTOCOL_03G.md", "turnover frozen protocol"),
    (TURNOVER_RESULT, "docs/individuation/TURNOVER_EXECUTION_MANIFEST_03G.json", "turnover execution manifest"),
    (TURNOVER_RESULT, "docs/individuation/FINAL_SEAL_MANIFEST_03G.json", "prospective final seal"),
    (TURNOVER_RESULT, "docs/individuation/TURNOVER_AUTHORIZATION_03G.json", "human authorization"),
    (TURNOVER_RESULT, "results/LCI-TURNOVER-PROSPECTIVE-03G/raw_manifest_03g.json", "prospective raw manifest"),
    (TURNOVER_RESULT, "results/LCI-TURNOVER-PROSPECTIVE-03G/execution_ledger_03g.jsonl", "prospective execution ledger"),
    (TURNOVER_RESULT, "results/LCI-TURNOVER-PROSPECTIVE-03G/analysis/analysis_certificate_03g.json", "prospective certificate"),
    (RAW_REPRODUCTION, "analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py", "independent raw-only estimator"),
    (RAW_REPRODUCTION, "analysis/lci-turnover-raw-reproduction-03m/REPRODUCTION_RESULT_03M.json", "independent reproduction result"),
]

BLUE = "#146C94"
GREEN = "#0A9D78"
ORANGE = "#D66A00"
RED = "#B23A48"
GREY = "#64748B"
LIGHT = "#EEF3F7"
INK = "#17212B"


def git_bytes(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout


def git_text(commit: str, path: str) -> str:
    return git_bytes(commit, path).decode("utf-8")


def git_blob(commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{commit}:{path}"], cwd=REPO, text=True
    ).strip()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def check_ancestry() -> dict[str, bool]:
    checks = {
        "turnover_result_is_ancestor_of_reproduction": (TURNOVER_RESULT, RAW_REPRODUCTION),
        "confirm_result_is_ancestor_of_turnover": (CONFIRM_RESULT, TURNOVER_RESULT),
        "turnover_authorization_is_parent_of_result": (TURNOVER_AUTHORIZATION, TURNOVER_RESULT),
    }
    result: dict[str, bool] = {}
    for name, (ancestor, descendant) in checks.items():
        code = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=REPO,
            check=False,
        ).returncode
        result[name] = code == 0
    parent = subprocess.check_output(
        ["git", "rev-parse", f"{TURNOVER_RESULT}^"], cwd=REPO, text=True
    ).strip()
    result["turnover_authorization_is_parent_of_result"] = parent == TURNOVER_AUTHORIZATION
    if not all(result.values()):
        raise AssertionError(result)
    return result


def source_bindings() -> dict[str, Any]:
    records = []
    for commit, path, role in SOURCE_SPECS:
        content = git_bytes(commit, path)
        records.append(
            {
                "role": role,
                "commit": commit,
                "path": path,
                "git_blob": git_blob(commit, path),
                "sha256": sha256(content),
                "bytes": len(content),
            }
        )
    return {
        "schema": "PERSISTENCE-WITHOUT-OWNERSHIP-SOURCE-BINDINGS-05-v1",
        "final_seal_sha256": FINAL_SEAL_SHA256,
        "ancestry": check_ancestry(),
        "sources": records,
    }


def r2(y: np.ndarray, prediction: np.ndarray) -> float:
    residual = float(np.sum((y - prediction) ** 2))
    total = float(np.sum((y - y.mean()) ** 2))
    return 1.0 - residual / total if total > 0 else 0.0


def ridge_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    keep = std > 1e-9
    if not np.any(keep):
        return np.full(len(x_test), y_train.mean(), dtype=float)
    train = (x_train[:, keep] - mean[keep]) / std[keep]
    test = (x_test[:, keep] - mean[keep]) / std[keep]
    intercept = y_train.mean()
    lhs = train.T @ train + np.eye(int(np.sum(keep)))
    weights = np.linalg.solve(lhs, train.T @ (y_train - intercept))
    return test @ weights + intercept


def grouped_oof(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> tuple[float, dict[str, float]]:
    prediction = np.full(len(y), np.nan, dtype=float)
    folds: dict[str, float] = {}
    for group in np.unique(groups):
        test = groups == group
        prediction[test] = ridge_predict(x[~test], y[~test], x[test])
        folds[str(int(group))] = r2(y[test], prediction[test])
    return r2(y, prediction), folds


def t95(values: list[float] | np.ndarray) -> list[float]:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    if len(array) < 2:
        return [mean, mean, mean]
    critical = float(student_t.ppf(0.975, len(array) - 1))
    half = critical * float(array.std(ddof=1)) / math.sqrt(len(array))
    return [mean - half, mean, mean + half]


def v41_recompute() -> dict[str, Any]:
    path = "results/observer/tca_holdout_raw.pkl"
    records = pickle.loads(git_bytes(V41, path))
    worlds = np.asarray([record["seed"] for record in records])
    histories = np.asarray([record["hi"] for record in records])
    checkpoints = [(0, "initial"), (400, "moderate"), (650, "deep_1"), (800, "deep")]
    output: dict[str, Any] = {}
    for step, label in checkpoints:
        x = np.asarray(
            [list(record["ck"][step]["long"][0]) + [record["ck"][step]["long"][3]] for record in records],
            dtype=float,
        )
        block: dict[str, Any] = {}
        for coordinate in ("h1", "h2"):
            y = np.asarray([record[coordinate] for record in records], dtype=float)
            point, folds = grouped_oof(x, y, worlds)
            block[coordinate] = {
                "world_grouped_r2": point,
                "world_fold_r2": folds,
                "world_fold_t95_descriptive": t95(list(folds.values())),
            }
        block["mean_M"] = float(np.mean([r["ck"][step]["long"][1] for r in records]))
        block["M_le_0_25"] = int(sum(r["ck"][step]["long"][1] <= 0.25 for r in records))
        output[label] = block
    result = {
        "schema": "PERSISTENCE-WITHOUT-OWNERSHIP-V41-RECOMPUTE-05-v1",
        "source_commit": V41,
        "source_path": path,
        "source_blob": git_blob(V41, path),
        "source_sha256": sha256(git_bytes(V41, path)),
        "n_rows": len(records),
        "n_original_worlds": int(len(np.unique(worlds))),
        "n_histories": int(len(np.unique(histories))),
        "survived": int(len(records) - sum(bool(r.get("lost", False)) for r in records)),
        "recorded_switches": int(sum(int(r.get("switch", 0)) for r in records)),
        "checkpoints": output,
        "engine_imported": False,
        "seed_executed": False,
    }
    if abs(result["checkpoints"]["deep"]["h1"]["world_grouped_r2"] - 0.69469387421633) > 1e-12:
        raise AssertionError("V4.1 deep h1 mismatch")
    return result


def confirm02_recompute() -> dict[str, Any]:
    raw_path = "experiments/individuation/nonmerging_confirm_raw.json"
    cert_path = "docs/individuation/NONMERGING_CONFIRM_CERTIFICATE_02.json"
    records = json.loads(git_text(CONFIRM_RESULT, raw_path))
    cert = json.loads(git_text(CONFIRM_RESULT, cert_path))
    valid = [record for record in records if record.get("g0_valid")]
    world_rows = []
    for record in valid:
        behavior = record["beh"]
        own = []
        neighbour = []
        sham = []
        fixed = []
        ablation = []
        for target in range(3):
            own.append(behavior["intact"]["tracked"][target] - behavior["erase"][target]["tracked"][target])
            neighbour_index = (target + 1) % 3
            neighbour.append(behavior["intact"]["tracked"][target] - behavior["erase"][neighbour_index]["tracked"][target])
            sham.append(behavior["intact"]["tracked"][target] - behavior["sham"]["tracked"][target])
            fixed.append(behavior["intact"]["fixed"][target] - behavior["erase"][target]["fixed"][target])
            ablation.append(behavior["ablate"]["tracked"][target] - behavior["erase_ablate"][target]["tracked"][target])
        world_rows.append(
            {
                "seed": record["seed"],
                "own": float(np.mean(own)),
                "neighbour": float(np.mean(neighbour)),
                "sham": float(np.mean(sham)),
                "fixed": float(np.mean(fixed)),
                "ablation": float(np.mean(ablation)),
                "max_coverage": float(record["max_cov_intact"]),
            }
        )
    summary = {name: t95([row[name] for row in world_rows]) for name in ("own", "neighbour", "sham", "fixed", "ablation")}
    raw_target_mean = float(np.mean([row["own"] for row in world_rows]))
    if abs(raw_target_mean - cert["G3"]["own_mean"]) > 1e-12:
        raise AssertionError((raw_target_mean, cert["G3"]["own_mean"]))
    return {
        "schema": "PERSISTENCE-WITHOUT-OWNERSHIP-CONFIRM02-RECOMPUTE-05-v1",
        "source_commit": CONFIRM_RESULT,
        "raw_path": raw_path,
        "raw_blob": git_blob(CONFIRM_RESULT, raw_path),
        "raw_sha256": sha256(git_bytes(CONFIRM_RESULT, raw_path)),
        "n_seeds": len(records),
        "n_eligible": int(sum(bool(r.get("eligible")) for r in records)),
        "n_valid_worlds": len(valid),
        "world_rows": world_rows,
        "descriptive_t95_over_world_means": summary,
        "certified_world_bootstrap": {
            "own": cert["G3"]["own_worldCI"],
            "own_minus_sham": cert["G3"]["own_sham_worldCI"],
            "own_minus_neighbour": cert["G3"]["own_neigh_worldCI"],
            "fixed": cert["G5"]["own_fixed_worldCI"],
        },
        "gates": {key: value["passed"] for key, value in cert.items() if key.startswith("G")},
        "engine_imported": False,
        "seed_executed": False,
    }


def load_turnover_module() -> Any:
    path = REPO / "analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py"
    spec = importlib.util.spec_from_file_location("turnover_independent_03m_for_paper", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load independent 03M module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def turnover_recompute() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    module = load_turnover_module()
    result = module.run(REPO)
    _, records, raw_audit = module.load_validated_raw(REPO)
    if result["outcome"] != "B" or result["n_valid_worlds"] != 21:
        raise AssertionError("turnover outcome mismatch")
    result["paper_recompute"] = {
        "raw_audit": raw_audit,
        "source_script_commit": RAW_REPRODUCTION,
        "source_script_blob": git_blob(RAW_REPRODUCTION, "analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py"),
        "source_script_sha256": sha256(git_bytes(RAW_REPRODUCTION, "analysis/lci-turnover-raw-reproduction-03m/independent_crosscheck_03m.py")),
        "engine_imported": False,
        "seed_executed": False,
    }
    return result, records


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "figure.titlesize": 15,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.dpi": 240,
        }
    )


def footer(fig: plt.Figure, source: str) -> None:
    fig.text(
        0.01,
        0.008,
        f"Source: {source} | Generator: paper/persistence-without-ownership-05/scripts/recompute_and_figures_05.py",
        fontsize=6.5,
        color=GREY,
    )


def save(fig: plt.Figure, name: str, source: str) -> None:
    footer(fig, source)
    fig.savefig(FIGURES / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax: plt.Axes, x: float, y: float, w: float, h: float, text: str, color: str, lw: float = 1.5) -> None:
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", linewidth=lw, edgecolor=color, facecolor="white")
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=INK, fontsize=9, wrap=True)


def figure1_ladder() -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.axis("off")
    steps = [
        ("1  Engineered state\nstores experience", GREEN),
        ("2  State is readable and\ncausally affects feeding", GREEN),
        ("3  State remains active\nthrough deep turnover", GREEN),
        ("4  Coexisting droplets show\nlocal effects without fusion", GREEN),
        ("5  Target-local information\nbeats E and B scopes", RED),
        ("6  Individual memory /\nlocal ownership", RED),
    ]
    for index, (label, color) in enumerate(steps):
        row, col = divmod(index, 3)
        x = 0.05 + col * 0.32
        y = 0.62 - row * 0.40
        box(ax, x, y, 0.26, 0.19, label, color, 2)
        ax.text(x + 0.13, y - 0.045, "PASS" if color == GREEN else "FAIL / NOT ESTABLISHED", ha="center", color=color, fontweight="bold")
        if col < 2:
            ax.add_patch(FancyArrowPatch((x + 0.265, y + 0.095), (x + 0.315, y + 0.095), arrowstyle="-|>", mutation_scale=15, color=GREY))
    ax.add_patch(FancyArrowPatch((0.91, 0.62), (0.91, 0.48), arrowstyle="-|>", mutation_scale=15, color=GREY))
    ax.text(0.5, 0.94, "Falsification ladder: persistence survives; ownership does not", ha="center", fontsize=16, fontweight="bold")
    ax.text(0.5, 0.07, "Outcome B: a causal feeding effect without ownership", ha="center", fontsize=14, color=BLUE, fontweight="bold")
    save(fig, "fig1_falsification_ladder.png", "protocol chain at commits 830c2d00 and 9cb996bb")


def figure2_model() -> None:
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Frozen scaffold, engineered memory, and two causal readout channels", ha="center", fontsize=15, fontweight="bold")
    ax.add_patch(Rectangle((0.04, 0.18), 0.25, 0.62, facecolor=LIGHT, edgecolor=GREY))
    ax.text(0.165, 0.74, "Frozen scaffold", ha="center", fontweight="bold")
    for i, (label, y) in enumerate(((r"density $\rho$", 0.64), (r"chemistry $U,V$", 0.54), (r"nutrient $N$", 0.44), (r"attractant $c$", 0.34))):
        ax.text(0.165, y, label, ha="center")
    ax.add_patch(Rectangle((0.37, 0.18), 0.26, 0.62, facecolor="#F3FAF7", edgecolor=GREEN, linewidth=2))
    ax.text(0.50, 0.74, "Engineered state", ha="center", fontweight="bold", color=GREEN)
    ax.text(0.50, 0.61, r"$\Psi=\tanh[k_{exp}(N-c)+k_{up}(u-\bar u)]$", ha="center", fontsize=9)
    ax.text(0.50, 0.51, "state update\nwrite - decay + templating + diffusion", ha="center", fontsize=8.6)
    ax.text(0.50, 0.44, r"fast/slow retention: $\eta_{d,1}\ne\eta_{d,2}$", ha="center", fontsize=9)
    ax.text(0.50, 0.34, r"extensive transport: $M_f=\rho m$", ha="center")
    ax.text(0.50, 0.26, "new material passively inherits\nlocal intensive state", ha="center", fontsize=8.5)
    box(ax, 0.71, 0.54, 0.24, 0.20, "$m_+=m_1+m_2$\n$\\rightarrow$ nutrient uptake\n$\\lambda_+=0.25$", BLUE)
    box(ax, 0.71, 0.23, 0.24, 0.20, "$m_-=m_1-m_2$\n$\\rightarrow$ attractant production\n$\\lambda_-=0.15$", ORANGE)
    for y in (0.64, 0.33):
        ax.add_patch(FancyArrowPatch((0.63, 0.49), (0.71, y), arrowstyle="-|>", mutation_scale=15, color=GREY))
    ax.add_patch(FancyArrowPatch((0.29, 0.49), (0.37, 0.49), arrowstyle="-|>", mutation_scale=15, color=GREY))
    save(fig, "fig2_model_memory_channels.png", "V4.0 model source at commit 23b53aee; turnover protocol 03G")


def figure3_nonfusing(confirm: dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.7), gridspec_kw={"width_ratios": [1, 1.3]})
    ax = axes[0]
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    centers = [(0.30, 0.68), (0.69, 0.68), (0.50, 0.31)]
    for index, (x, y) in enumerate(centers):
        ax.add_patch(Circle((x, y), 0.13, facecolor="#D7ECF7", edgecolor=BLUE, linewidth=2))
        ax.text(x, y, f"droplet {index + 1}\nlocal $m_+$", ha="center", va="center", fontsize=8)
    ax.add_patch(Circle(centers[0], 0.07, facecolor="white", edgecolor=RED, linewidth=2, hatch="///"))
    ax.text(0.18, 0.91, "do(erase target memory)", color=RED, fontweight="bold")
    ax.text(0.5, 0.07, "3 distinct components throughout; no merge, split, loss, or ambiguity", ha="center", fontsize=8.5)
    ax = axes[1]
    labels = ["own", "own - sham", "own - neighbour", "fixed mask"]
    intervals = [
        confirm["certified_world_bootstrap"]["own"],
        confirm["certified_world_bootstrap"]["own_minus_sham"],
        confirm["certified_world_bootstrap"]["own_minus_neighbour"],
        confirm["certified_world_bootstrap"]["fixed"],
    ]
    y = np.arange(len(labels))[::-1]
    means = [v[1] for v in intervals]
    lo = [v[1] - v[0] for v in intervals]
    hi = [v[2] - v[1] for v in intervals]
    ax.errorbar(means, y, xerr=np.asarray([lo, hi]), fmt="o", color=GREEN, ecolor=GREY, capsize=4)
    ax.axvline(0, color=INK, linewidth=1)
    ax.set_yticks(y, labels)
    ax.set_xlabel("feeding contrast (95% preregistered world bootstrap)")
    ax.set_title("CONFIRM-02: local causal effect at rest")
    ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Non-fusing local intervention establishes causal locality before turnover", fontweight="bold")
    save(fig, "fig3_nonfusing_local_intervention.png", "CONFIRM-02 raw and certificate, commit 830c2d00")


def figure4_turnover(records: list[dict[str, Any]]) -> None:
    valid = [record for record in records if record["feasibility"]["valid"]]
    m_values = [value for record in valid for value in record["scientific"]["material_tracer"]["deep_M"]]
    world_means = [float(np.mean(record["scientific"]["material_tracer"]["deep_M"])) for record in valid]
    seeds = [record["seed"] for record in valid]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.7), gridspec_kw={"width_ratios": [0.75, 1.2, 1.5]})
    axes[0].bar(["valid", "invalid"], [len(valid), len(records) - len(valid)], color=[GREEN, GREY])
    axes[0].axhline(18, color=ORANGE, linestyle="--", label="minimum 18")
    axes[0].set_ylabel("world count")
    axes[0].legend(frameon=False, fontsize=8)
    axes[0].set_title("Feasibility")
    axes[1].hist(m_values, bins=np.linspace(0.08, 0.31, 9), color=BLUE, edgecolor="white")
    axes[1].axvline(0.5, color=ORANGE, linestyle="--")
    axes[1].set_xlabel(r"deep old-material fraction $M_i$")
    axes[1].set_ylabel("target count")
    axes[1].set_title("63 targets in 21 valid worlds")
    order = np.argsort(world_means)
    axes[2].scatter(np.arange(len(valid)), np.asarray(world_means)[order], color=BLUE, s=24)
    axes[2].axhline(0.5, color=ORANGE, linestyle="--", label="deep-turnover bound")
    axes[2].set_xticks(np.arange(len(valid)), np.asarray(seeds)[order], rotation=75, fontsize=7)
    axes[2].set_ylabel("world mean deep $M_i$")
    axes[2].set_title("Valid-world turnover distribution")
    axes[2].legend(frameon=False, fontsize=8)
    fig.suptitle("Deep material replacement was achieved before the ownership test", fontweight="bold")
    save(fig, "fig4_material_turnover_validity.png", "50 prospective raw records, commit 9cb996bb; raw-only 03M loader")


def figure5_causal(turnover: dict[str, Any]) -> None:
    c = turnover["causal"]
    items = [
        ("own", c["own_t95"]),
        ("own - sham", c["own_minus_sham_t95"]),
        ("own - neighbour", c["own_minus_neighbour_t95"]),
        ("fixed mask", c["own_fixed_t95"]),
        (r"$\lambda_+$ only ablated", c["own_under_lambda_plus_only_ablation_t95"]),
    ]
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    y = np.arange(len(items))[::-1]
    means = np.array([v["mean"] for _, v in items])
    lower = np.array([v["lower"] for _, v in items])
    upper = np.array([v["upper"] for _, v in items])
    colors = [GREEN, GREEN, GREEN, GREEN, ORANGE]
    for yi, mean, lo, hi, color in zip(y, means, lower, upper, colors):
        ax.errorbar(mean, yi, xerr=[[mean - lo], [hi - mean]], fmt="o", color=color, ecolor=GREY, capsize=4)
    ax.axvline(0, color=INK, linewidth=1)
    ax.set_yticks(y, [label for label, _ in items])
    ax.set_xlabel("world-level mean feeding contrast (95% Student t interval)")
    ax.set_title("The local feeding effect remains causal after deep turnover")
    ax.grid(axis="x", alpha=0.25)
    save(fig, "fig5_causal_contrast_after_turnover.png", "03M independent recomputation from 21 valid prospective worlds")


def figure6_ownership(turnover: dict[str, Any]) -> None:
    comparisons = turnover["ownership"]["G_LOCAL_EXCLUSION"]["comparisons"]
    order = ["N", "E", "Gm", "B"]
    fig, ax = plt.subplots(figsize=(8.8, 5.4))
    y = np.arange(len(order))[::-1]
    for yi, key in zip(y, order):
        interval = comparisons[key]["t95"]
        passed = interval["lower"] > 0
        color = GREEN if passed else RED
        ax.errorbar(
            interval["mean"], yi,
            xerr=[[interval["mean"] - interval["lower"]], [interval["upper"] - interval["mean"]]],
            fmt="o", color=color, ecolor=GREY, capsize=4,
        )
        ax.text(interval["upper"] + 0.03, yi, "pass" if passed else "fails exclusion", va="center", color=color, fontsize=9)
    ax.axvline(0, color=INK, linewidth=1)
    ax.set_yticks(y, ["L over N", "L over E", "L over G-minus-target", "L over B"])
    ax.set_xlabel("paired world loss advantage of L (95% Student t interval)")
    ax.set_title("Ownership fails because L does not exclude E or B")
    ax.grid(axis="x", alpha=0.25)
    save(fig, "fig6_ownership_scope_exclusion.png", "03M independent recomputation; frozen L/N/E/Gm/B scopes")


def figure7_tree(turnover: dict[str, Any]) -> None:
    gates = turnover["gates"]
    fig, ax = plt.subplots(figsize=(10.5, 6.3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.95, "Frozen A-F decision tree selects one outcome", ha="center", fontsize=15, fontweight="bold")
    nodes = [
        (0.37, 0.78, "FEASIBILITY\nTRUE", GREEN),
        (0.17, 0.55, "G_OWN_PERM\nTRUE", GREEN),
        (0.42, 0.55, "G_LOCAL_EXCLUSION\nFALSE", RED),
        (0.67, 0.55, "G_CAUSAL\nTRUE", GREEN),
        (0.42, 0.31, "DISTRIBUTED_ENV\nFALSE", ORANGE),
        (0.31, 0.08, "OUTCOME B\ncausal feeding effect without ownership", BLUE),
    ]
    for x, y, label, color in nodes:
        box(ax, x, y, 0.26 if "OUTCOME" not in label else 0.38, 0.12, label, color, 2)
    arrows = [((0.50, 0.78), (0.30, 0.67)), ((0.50, 0.78), (0.55, 0.67)), ((0.50, 0.78), (0.80, 0.67)), ((0.55, 0.55), (0.55, 0.43)), ((0.55, 0.31), (0.50, 0.20))]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, color=GREY))
    ax.text(0.07, 0.17, "Other outcomes A, C, D, E, F\nare rejected by the frozen gate vector.", fontsize=9, color=GREY)
    if gates != {"FEASIBILITY": True, "G_OWN_PERM": True, "G_LOCAL_EXCLUSION": False, "G_CAUSAL": True, "DISTRIBUTED_ENV": False}:
        raise AssertionError(gates)
    save(fig, "fig7_decision_tree_outcome_b.png", "TURNOVER_DECISION_TREE_03G.json and independent gate vector")


def figure8_claims() -> None:
    fig, ax = plt.subplots(figsize=(11, 7.2))
    ax.axis("off")
    ax.text(0.5, 0.96, "Claim boundary: what the evidence licenses", ha="center", fontsize=16, fontweight="bold")
    columns = [
        (0.03, 0.53, "ESTABLISHED", GREEN, ["one-shot sealed execution", "21 valid deep-turnover worlds", "own signal > permutation null", "feeding effect remains causal", "local-ownership gate fails", "raw-only reproduction exact"]),
        (0.52, 0.53, "SUPPORTED WITH QUALIFICATION", BLUE, ["passively inherited local remnant", "low-dimensional scopes are not exhaustive", "persistence and ownership dissociate"]),
        (0.03, 0.08, "NOT ESTABLISHED", GREY, ["individual memory", "exclusive local storage", "identity", "active reconstruction", "reproduction or heredity", "evolution or life"]),
        (0.52, 0.08, "FALSIFIED WITHIN TESTED CRITERIA", RED, ["persistence alone is sufficient for memory", "turnover-surviving ownership in frozen C1c"]),
    ]
    for x, y, title, color, claims in columns:
        ax.add_patch(FancyBboxPatch((x, y), 0.45, 0.34, boxstyle="round,pad=0.02", facecolor="white", edgecolor=color, linewidth=2))
        ax.text(x + 0.225, y + 0.30, title, ha="center", color=color, fontweight="bold", fontsize=10)
        ax.text(x + 0.03, y + 0.265, "\n".join(f"• {claim}" for claim in claims), va="top", fontsize=9, linespacing=1.35)
    save(fig, "fig8_claim_boundary.png", "claim ledger synthesized from V4.1, CONFIRM-02, 03G, and 03M")


def write_numerical_csv(v41: dict[str, Any], confirm: dict[str, Any], turnover: dict[str, Any]) -> None:
    rows = [
        ["V4.1", "deep_h1_world_grouped_r2", v41["checkpoints"]["deep"]["h1"]["world_grouped_r2"], "3 original worlds", "corrected; no certification"],
        ["V4.1", "deep_h2_world_grouped_r2", v41["checkpoints"]["deep"]["h2"]["world_grouped_r2"], "3 original worlds", "not established"],
        ["CONFIRM-02", "own_feeding_mean", confirm["descriptive_t95_over_world_means"]["own"][1], "23 original worlds", "raw recomputation"],
        ["03G", "own_scope_mean_skill", turnover["ownership"]["G_OWN_PERM"]["observed_mean_skill"], "21 original worlds", "G_OWN_PERM=true"],
        ["03G", "causal_own_mean", turnover["causal"]["own_t95"]["mean"], "21 original worlds", "G_CAUSAL=true"],
        ["03G", "L_over_E_mean", turnover["ownership"]["G_LOCAL_EXCLUSION"]["comparisons"]["E"]["t95"]["mean"], "21 original worlds", "fails: lower <= 0"],
        ["03G", "L_over_B_mean", turnover["ownership"]["G_LOCAL_EXCLUSION"]["comparisons"]["B"]["t95"]["mean"], "21 original worlds", "fails: lower <= 0"],
    ]
    path = PAPER / "NUMERICAL_RECONCILIATION_05.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["source_family", "quantity", "value", "sample_unit", "disposition"])
        writer.writerows(rows)


def raw_registry(bindings: dict[str, Any], v41: dict[str, Any], confirm: dict[str, Any], turnover: dict[str, Any]) -> dict[str, Any]:
    turnover_raw = turnover["inputs"]["raw_manifest"]
    return {
        "schema": "PERSISTENCE-WITHOUT-OWNERSHIP-RAW-REGISTRY-05-v1",
        "no_new_simulation": True,
        "families": [
            {
                "family": "V4.1 historical longitudinal correction",
                "commit": V41,
                "path": v41["source_path"],
                "git_blob": v41["source_blob"],
                "sha256": v41["source_sha256"],
                "rows": v41["n_rows"],
                "original_worlds": v41["n_original_worlds"],
                "status": "historical corrected grouped inference",
            },
            {
                "family": "CONFIRM-02 non-fusing local intervention",
                "commit": CONFIRM_RESULT,
                "path": confirm["raw_path"],
                "git_blob": confirm["raw_blob"],
                "sha256": confirm["raw_sha256"],
                "seeds": confirm["n_seeds"],
                "valid_worlds": confirm["n_valid_worlds"],
                "status": "prospective at original commit; no turnover retest",
            },
            {
                "family": "03G deep-turnover ownership",
                "commit": TURNOVER_RESULT,
                "path": turnover_raw["raw_manifest_path"],
                "sha256": turnover_raw["raw_manifest_sha256"],
                "raw_worlds": turnover["n_raw_worlds"],
                "valid_worlds": turnover["n_valid_worlds"],
                "status": "sealed prospective one-shot execution",
            },
        ],
        "source_binding_registry_sha256": sha256(json.dumps(bindings, sort_keys=True).encode("utf-8")),
    }


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    setup_style()
    bindings = source_bindings()
    v41 = v41_recompute()
    confirm = confirm02_recompute()
    turnover, turnover_records = turnover_recompute()
    write_json(PAPER / "SOURCE_BINDINGS_05.json", bindings)
    write_json(DATA / "v41_recomputed_05.json", v41)
    write_json(DATA / "confirm02_recomputed_05.json", confirm)
    write_json(DATA / "turnover_recomputed_05.json", turnover)
    write_json(PAPER / "RAW_DATA_REGISTRY_05.json", raw_registry(bindings, v41, confirm, turnover))
    write_numerical_csv(v41, confirm, turnover)
    figure1_ladder()
    figure2_model()
    figure3_nonfusing(confirm)
    figure4_turnover(turnover_records)
    figure5_causal(turnover)
    figure6_ownership(turnover)
    figure7_tree(turnover)
    figure8_claims()
    print(
        json.dumps(
            {
                "v41_deep_h1": v41["checkpoints"]["deep"]["h1"]["world_grouped_r2"],
                "confirm02_valid": confirm["n_valid_worlds"],
                "turnover_valid": turnover["n_valid_worlds"],
                "turnover_outcome": turnover["outcome"],
                "engine_imported": False,
                "seed_executed": False,
                "figures": 8,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

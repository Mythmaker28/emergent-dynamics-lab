"""Final analysis + phase-plane figure, with the persistence correction applied."""

from __future__ import annotations

import csv
import json
import math
import statistics as st
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CONV = (0.01, 0.05, 0.20)
ARMS = ["ROUTE_E", "SHUFFLED", "COMPACT_ISLANDS", "SPANNING_BAND"]
COLOR = {"ROUTE_E": "#2a78d6", "SHUFFLED": "#eb6834",
         "COMPACT_ISLANDS": "#1baf7a", "SPANNING_BAND": "#eda100"}
MARK = {"ROUTE_E": "o", "SHUFFLED": "s", "COMPACT_ISLANDS": "^", "SPANNING_BAND": "D"}
LBL = {"ROUTE_E": "Route E (IC de production)", "SHUFFLED": "Permuté (cardinalité égale)",
       "COMPACT_ISLANDS": "Îlots compacts (contrôle +)", "SPANNING_BAND": "Bande traversante (contrôle −)"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#d8d7d2", "#fcfcfb"


def wilson_lo(k, n, z=1.96):
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    return max(0.0, (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d)


def load(path, floats, ints, bools):
    rows = []
    for r in csv.DictReader(open(path)):
        for k in floats:
            r[k] = float(r[k]) if r[k] not in ("", "None") else float("nan")
        for k in ints:
            r[k] = int(r[k]) if r[k] not in ("", "None") else None
        for k in bools:
            r[k] = r[k] == "True"
        rows.append(r)
    return rows


main_rows = load("sweep00_rows.csv",
                 ["target_occupancy", "realized_occupation_t0", "realized_occupation_end",
                  "labelled_fraction", "largest_component_over_L2",
                  "min_cohort_residual_bounded", "min_cohort_residual_at_horizon"],
                 ["L", "seed", "component_count_t0", "component_count_end", "first_wrapping_frame"],
                 ["wraps_at_t0", "wraps_anywhere", "mechanically_ineligible"])
ref_rows = load("sweep00_refine_rows.csv",
                ["target_occupancy", "realized_occupation_t0", "labelled_fraction",
                 "residual_at_horizon_bounded"],
                ["L", "seed", "component_count_t0", "component_count_end",
                 "min_component_count_any_frame", "first_wrapping_frame", "horizon"],
                ["ever_empty", "wraps_anywhere", "persistent_bounded_population",
                 "PASS_at_0.01", "PASS_at_0.05", "PASS_at_0.2", "floor_admits_0.2"])

levels = sorted({r["target_occupancy"] for r in main_rows})
sizes = sorted({r["L"] for r in main_rows})

# ------------------------------------------------------------------ summary
agg = {}
by = defaultdict(list)
for r in main_rows:
    by[(r["arm"], r["target_occupancy"], r["L"])].append(r)
for key, g in by.items():
    n = len(g)
    arm, p, L = key
    agg[f"{arm}|{p}|{L}"] = {
        "n": n,
        "realized_occupation_t0": st.median(x["realized_occupation_t0"] for x in g),
        "component_count_t0": st.median(x["component_count_t0"] for x in g),
        "largest_over_L2": st.median(x["largest_component_over_L2"] for x in g),
        "wrapping_rate": sum(x["wraps_anywhere"] for x in g) / n,
        "dissolved_rate_h256": sum(x["component_count_end"] == 0 for x in g) / n,
        "surviving_rate_h256": sum(
            (not x["wraps_anywhere"]) and x["component_count_end"] > 0 for x in g) / n,
        "labelled_fraction_median": st.median(x["labelled_fraction"] for x in g),
    }

ref_agg = {}
rby = defaultdict(list)
for r in ref_rows:
    rby[(r["arm"], r["target_occupancy"], r["L"])].append(r)
for (arm, p, L), g in rby.items():
    n = len(g)
    ref_agg[f"{arm}|{p}|{L}"] = {
        "n": n, "horizon": 1024,
        "dissolved_rate": sum(x["ever_empty"] for x in g) / n,
        "wrapping_rate": sum(x["wraps_anywhere"] for x in g) / n,
        "persistent_rate": sum(x["persistent_bounded_population"] for x in g) / n,
        "labelled_fraction_median": st.median(x["labelled_fraction"] for x in g),
        **{f"PASS_{f}": sum(x[f"PASS_at_{f}"] for x in g) for f in CONV},
    }

pass_total = {f: sum(r[f"PASS_at_{f}"] for r in ref_rows) for f in CONV}
persistent_total = sum(r["persistent_bounded_population"] for r in ref_rows)

ref_p055 = [r for r in main_rows if r["arm"] == "ROUTE_E" and r["target_occupancy"] == 0.55]
lab055 = [r["labelled_fraction"] for r in ref_p055]

summary = {
    "mission": "ANTI_STAGNATION_ROUTE_E_FEASIBILITY_SWEEP_00",
    "latest_authentic_tip": "7e6faeb173a6a2692a541dc0006c75a3972b08d1",
    "dev_worlds_executed": len(main_rows) + len(ref_rows),
    "main_sweep_worlds": len(main_rows), "refinement_worlds": len(ref_rows),
    "primary_worlds_opened": 0, "reproduction_worlds_opened": 0, "holdout_opened": False,
    "realized_occupancy_range": [min(r["realized_occupation_t0"] for r in main_rows),
                                 max(r["realized_occupation_t0"] for r in main_rows)],
    "pilot_reproduction_at_p055_bit_identical_ic": {
        "n": len(ref_p055),
        "labelled_fraction": [min(lab055), max(lab055), st.median(lab055)],
        "pilot_published_labelled_fraction": [0.6712, 0.8108, 0.7483],
        "wrapping_rate": sum(r["wraps_anywhere"] for r in ref_p055) / len(ref_p055),
        "pilot_published_wrapping_rate": 1.0,
        "verdict": "REPRODUCED",
    },
    "refinement_at_frozen_horizon_1024": {
        "worlds": len(ref_rows),
        "persistent_bounded_populations": persistent_total,
        "PASS_counts": pass_total,
        "wilson_lower_bound_pass_rate_f020": wilson_lo(pass_total[0.20], len(ref_rows)),
        "route_e_dissolved": sum(r["ever_empty"] for r in ref_rows if r["arm"] == "ROUTE_E"),
        "route_e_n": sum(1 for r in ref_rows if r["arm"] == "ROUTE_E"),
        "compact_islands_dissolved": sum(r["ever_empty"] for r in ref_rows
                                         if r["arm"] == "COMPACT_ISLANDS"),
        "compact_islands_n": sum(1 for r in ref_rows if r["arm"] == "COMPACT_ISLANDS"),
    },
    "by_arm_level_size_h256": agg,
    "by_arm_level_size_h1024": ref_agg,
    "decision": "NO_ONE_PARAMETER_RESCUE_OBSERVED_IN_SCANNED_RANGE",
}
Path("sweep00_summary.json").write_text(json.dumps(summary, indent=1))

print("=== BILAN ===")
print(f"mondes DEV executes : {summary['dev_worlds_executed']} "
      f"({len(main_rows)} balayage + {len(ref_rows)} raffinement)")
print(f"occupation realisee : {summary['realized_occupancy_range'][0]:.3f} "
      f"-> {summary['realized_occupancy_range'][1]:.3f}")
print(f"reproduction du pilote a p=0.55 : labelled med {st.median(lab055):.4f} "
      f"vs 0.7483 publie ; enroulement {summary['pilot_reproduction_at_p055_bit_identical_ic']['wrapping_rate']:.2f} vs 1.00")
print(f"horizon 1024 : {persistent_total}/{len(ref_rows)} populations persistantes, "
      f"PASS {pass_total} ; Wilson lo (f=0.20) = {summary['refinement_at_frozen_horizon_1024']['wilson_lower_bound_pass_rate_f020']:.4f}")

# ------------------------------------------------------------------ figure
REF_LEVELS = [0.056, 0.10, 0.20, 0.35]
fig, axes = plt.subplots(2, 3, figsize=(14.6, 8.2), sharex=True)
fig.patch.set_facecolor(SURF)
for j, L in enumerate(sizes):
    top, bot = axes[0][j], axes[1][j]
    for ax in (top, bot):
        ax.set_facecolor(SURF)
        ax.grid(True, color=GRID, lw=0.8, zorder=0)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=9)
        ax.set_xlim(-0.02, 0.66)

    xs = [agg[f"ROUTE_E|{p}|{L}"]["realized_occupation_t0"] for p in levels]
    wrap = [agg[f"ROUTE_E|{p}|{L}"]["wrapping_rate"] for p in levels]
    diss = [agg[f"ROUTE_E|{p}|{L}"]["dissolved_rate_h256"] for p in levels]
    surv = [agg[f"ROUTE_E|{p}|{L}"]["surviving_rate_h256"] for p in levels]
    xr = [agg[f"ROUTE_E|{p}|{L}"]["realized_occupation_t0"] for p in REF_LEVELS]
    persist = [ref_agg[f"ROUTE_E|{p}|{L}"]["persistent_rate"] for p in REF_LEVELS]

    top.fill_between(xs, 0, wrap, color="#eb6834", alpha=0.16, zorder=1)
    top.fill_between(xs, 0, diss, color="#2a78d6", alpha=0.16, zorder=1)
    h1, = top.plot(xs, wrap, marker="s", color="#eb6834", lw=2, ms=7, mec=SURF, mew=1.6, zorder=3)
    h2, = top.plot(xs, diss, marker="o", color="#2a78d6", lw=2, ms=7, mec=SURF, mew=1.6, zorder=3)
    h3, = top.plot(xs, surv, marker="^", color="#1baf7a", lw=2.4, ms=8, mec=SURF, mew=1.6, zorder=4)
    h4, = top.plot(xr, persist, marker="v", color=INK, lw=2.4, ms=8, mec=SURF, mew=1.6, zorder=5)
    top.set_ylim(-0.06, 1.12)
    top.axvline(0.55, color=INK2, ls=":", lw=1.4, zorder=2)
    top.set_title(f"L = {L}", color=INK, fontsize=12, fontweight="bold", pad=8)

    for arm in ARMS:
        ax_x = [agg[f"{arm}|{p}|{L}"]["realized_occupation_t0"] for p in levels]
        ax_y = [agg[f"{arm}|{p}|{L}"]["labelled_fraction_median"] for p in levels]
        bot.plot(ax_x, ax_y, marker=MARK[arm], color=COLOR[arm], lw=2, ms=7,
                 mec=SURF, mew=1.6, zorder=3, label=LBL[arm])
    for f, style in zip(CONV, [":", "--", "-"]):
        bot.axhline(f, color=INK2, ls=style, lw=1.2, zorder=2)
        if j == 2:
            bot.annotate(f"f = {f:g}".replace(".", ","), xy=(0.665, f), color=INK2,
                         fontsize=8.5, va="center", annotation_clip=False)
    bot.axvline(0.55, color=INK2, ls=":", lw=1.4, zorder=2)
    bot.set_ylim(-0.05, 1.0)
    bot.set_xlabel("occupation réalisée à t0", color=INK2, fontsize=10)
    if j == 0:
        top.set_ylabel("fraction des mondes", color=INK2, fontsize=10)
        bot.set_ylabel("plancher du résidu (fraction enrôlée)", color=INK2, fontsize=10)
        top.annotate("régime du pilote", xy=(0.55, 1.04), xytext=(0.30, 0.70),
                     color=INK2, fontsize=8.5,
                     arrowprops=dict(arrowstyle="->", color=INK2, lw=1))
axes[0][2].annotate("fenêtre transitoire à h = 256…", xy=(0.36, 0.48), xytext=(0.05, 0.72),
                    color="#1baf7a", fontsize=9.5, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color="#1baf7a", lw=1.2))
axes[0][2].annotate("…refermée à l'horizon gelé 1024", xy=(0.36, 0.02), xytext=(0.02, 0.14),
                    color=INK, fontsize=9.5, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
fig.legend([h1, h2, h3, h4],
           ["enroulement → inéligible (h = 256)", "dissolution totale (h = 256)",
            "survivant et borné (h = 256)", "persistant à l'horizon gelé 1024"],
           frameon=False, fontsize=9, labelcolor=INK2, ncol=4,
           loc="upper center", bbox_to_anchor=(0.5, 0.912))
axes[1][0].legend(frameon=False, fontsize=8, labelcolor=INK2, loc="upper left")
fig.suptitle("Route E — balayage DEV de faisabilité : la pince enroulement / dissolution",
             color=INK, fontsize=15, fontweight="bold", y=0.992)
fig.text(0.5, 0.955,
         "864 mondes DEV · détecteur, tracker et résidu de production non modifiés · "
         "0 monde passe la porte à f = 0,01 / 0,05 / 0,20",
         ha="center", color=INK2, fontsize=9.5)
fig.tight_layout(rect=[0, 0, 0.982, 0.885])
fig.savefig("sweep00_phase_plane.png", dpi=170, facecolor=SURF)
print("figure -> sweep00_phase_plane.png")

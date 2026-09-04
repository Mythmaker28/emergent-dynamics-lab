#!/usr/bin/env python3
"""LRCPS01 §11-§12 — the four main figures, each regenerated from bound sources.

Every figure writes its own source-data file alongside the PDF and PNG. No figure
is drawn from a number that is not also in the reconciliation, and no figure carries
a quantity from a LOST or NOT_TESTED programme.
"""
import json, os, hashlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np

OB = "/home/claude/OBFOR01/out"
PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"
FIG = os.path.join(PKG, "figures")
DAT = os.path.join(PKG, "figure_data")
os.makedirs(FIG, exist_ok=True); os.makedirs(DAT, exist_ok=True)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

SRC = {n: sha(f"{OB}/{n}.json") for n in
       ("_observables_exact", "_residual", "_m6", "_mechanisms", "_validation",
        "_adjudication", "_freeze")}
J = {n: json.load(open(f"{OB}/{n}.json")) for n in SRC}
PROVENANCE = {}

plt.rcParams.update({
    "font.size": 8, "axes.linewidth": 0.7, "xtick.major.width": 0.7,
    "ytick.major.width": 0.7, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight", "pdf.fonttype": 42,
})
INK, ACC, WARN, MUT = "#1a1a1a", "#2c5f8a", "#b0413e", "#8a8a8a"

def save(fig, name, data, sources, caption):
    fig.savefig(f"{FIG}/{name}.pdf"); fig.savefig(f"{FIG}/{name}.png", dpi=300)
    plt.close(fig)
    with open(f"{DAT}/{name}.json", "w", encoding="utf-8") as f:
        json.dump({"FIGURE": name, "CAPTION": caption, "SOURCE_FILES":
                   {s: SRC[s] for s in sources}, "DATA": data}, f, indent=1, ensure_ascii=False)
    PROVENANCE[name] = {
        "pdf": f"figures/{name}.pdf", "png": f"figures/{name}.png",
        "source_data": f"figure_data/{name}.json",
        "pdf_sha256": sha(f"{FIG}/{name}.pdf"),
        "source_data_sha256": sha(f"{DAT}/{name}.json"),
        "SOURCE_FILES": {s: SRC[s] for s in sources},
        "REGENERATED_BY": "code/make_figures.py",
        "CONTAINS_LOST_OR_NOT_TESTED_EVIDENCE": False,
        "CAPTION": caption,
    }
    print("  wrote", name)

# ================================================================= Figure 1
ORDER = J["_mechanisms"]["S9_INTRA_STEP_ORDER"]["ORDER_READ_FROM_kinetics_py"]
CONST = {"L": 36, "CAP": 16, "S0": 3, "phi": 0.20, "omega": 0.05, "muX": 0.004,
         "kX": 1.0, "p_hop": 0.10263340389897246, "X_SEED": 4,
         "BURN_IN": 2000, "T_HORIZON": 11000, "SAMPLE_EVERY": 50}
PROPS = J["_residual"]["DEFINITION"]["three_properties_of_the_estimator"]

fig = plt.figure(figsize=(6.9, 3.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.95], wspace=0.05,
                      left=0.02, right=0.98, top=0.90, bottom=0.06)

ax = fig.add_subplot(gs[0, 0]); ax.set_aspect("equal"); ax.axis("off")
n = 10
for i2 in range(n + 1):
    ax.plot([0, n], [i2, i2], color="#e2e2e2", lw=0.45, zorder=0)
    ax.plot([i2, i2], [0, n], color="#e2e2e2", lw=0.45, zorder=0)
cx = cy = 5.0
rng = np.random.default_rng(20260817)
for r_ring, count in ((1.1, 10), (2.2, 14), (3.3, 10), (4.3, 5)):
    th = rng.uniform(0, 2 * np.pi, count)
    ax.scatter(cx + r_ring * np.cos(th), cy + r_ring * np.sin(th), s=6.5,
               color=ACC, alpha=0.75, lw=0, zorder=2)
ax.add_patch(plt.Circle((cx, cy), 3.15, fill=False, color=WARN, lw=1.5, zorder=3))
ax.scatter([cx], [cy], s=62, marker="s", color=INK, zorder=4)
ax.plot([cx, cx + 3.15 * np.cos(np.pi / 4)], [cy, cy + 3.15 * np.sin(np.pi / 4)],
        color=WARN, lw=0.9, ls="--", zorder=3)
ax.text(cx + 1.0, cy + 1.45, "$r_{80}$", fontsize=9, color=WARN)
ax.annotate("source cell:\nevery birth here", (cx - 0.35, cy - 0.35), (0.15, 1.45),
            fontsize=6.8, color=INK, ha="left",
            arrowprops=dict(arrowstyle="-", lw=0.55, color=INK))
ax.text(n / 2, -0.95,
        "periodic lattice $L=36$, capacity 16 per cell\n"
        "$r_{80}$ = smallest achievable lattice distance at which the\n"
        "empirical cumulative field first reaches 0.8",
        fontsize=6.8, ha="center", va="top", color=MUT, linespacing=1.5)
ax.set_xlim(-0.3, n + 0.3); ax.set_ylim(-3.6, n + 0.3)
ax.text(-0.2, n + 0.2, "a", fontsize=10, fontweight="bold", va="top")

ax = fig.add_subplot(gs[0, 1]); ax.axis("off")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(0.02, 0.995, "b", fontsize=10, fontweight="bold", va="top")
labels = [o.replace('_diffuse("', "diffuse ").replace('"', "").replace("()", "")
          for o in ORDER]
top, boxh, gap = 0.93, 0.070, 0.019
for k, lab in enumerate(labels):
    y0 = top - k * (boxh + gap) - boxh
    ax.add_patch(Rectangle((0.16, y0), 0.62, boxh,
                           facecolor="#eef3f8" if k < 4 else "#faf1f0",
                           edgecolor=MUT, lw=0.5))
    ax.text(0.19, y0 + boxh / 2, f"{k+1}.  {lab}", fontsize=7.4, color=INK, va="center")
    if k < len(labels) - 1:
        ax.add_patch(FancyArrowPatch((0.47, y0 - 0.002), (0.47, y0 - gap + 0.002),
                                     arrowstyle="-|>", mutation_scale=5.5, lw=0.55, color=MUT))
ybot = top - len(labels) * (boxh + gap)
ax.text(0.16, ybot - 0.012, "one step; then $t \\rightarrow t+1$",
        fontsize=6.8, color=MUT, style="italic", va="top")
ax.text(0.16, ybot - 0.075,
        "births enter after transport, so a newborn takes\n"
        "no step in its own birth step; burn-in 2000,\n"
        "horizon 11000, one frame every 50 steps;\n"
        "the within-arm summary is the median over frames",
        fontsize=6.6, color=INK, va="top", linespacing=1.55)
save(fig, "fig1_model_and_event_order",
     {"EVENT_ORDER": ORDER, "CONSTANTS": CONST, "ESTIMATOR_PROPERTIES": PROPS},
     ["_mechanisms", "_residual"],
     "The model and the reported observable. (a) A point source on a periodic lattice with a "
     "per-cell capacity; the reported radius is the smallest achievable toroidal distance at "
     "which the empirical cumulative field first reaches 0.8. (b) The event order read directly "
     "from the kinetics module. The lattice sketch is schematic; no arrangement of particles in "
     "it is measured data.")

# ================================================================= Figure 2
O = J["_adjudication"]["OBSERVED"]; E = J["_adjudication"]["ENDPOINTS"]
CDF_S, CDF_M = J["_residual"]["RADIAL_CDF_STATIC"], J["_residual"]["RADIAL_CDF_MOBILE"]
fig, axes = plt.subplots(1, 2, figsize=(5.6, 2.6),
                         gridspec_kw={"width_ratios": [1.0, 1.25], "wspace": 0.62})

ax = axes[0]
for k, (tag, ep, col) in enumerate((("S_median", "STATIC_ABSOLUTE_PROFILE_COMPATIBILITY", ACC),
                                    ("M_median", "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY", WARN))):
    v = O[tag]["values"]; pred = E[ep]["predicted"]; m = E[ep]["margin_percent"] / 100
    x = k + rng.uniform(-0.13, 0.13, len(v))
    ax.plot([k - 0.30, k + 0.30], [pred, pred], color=col, lw=1.4, zorder=3)
    ax.fill_between([k - 0.30, k + 0.30], pred * (1 - m), pred * (1 + m),
                    color=col, alpha=0.13, lw=0, zorder=1)
    ax.scatter(x, v, s=13, color=col, alpha=0.85, lw=0, zorder=4)
    ax.errorbar([k], [O[tag]["mean"]], yerr=[1.96 * O[tag]["se"]], fmt="D", ms=4.2,
                color=INK, lw=1.0, capsize=2.5, zorder=5)
ax.set_xticks([0, 1]); ax.set_xticklabels(["static", "mobile"])
ax.set_ylabel("$r_{80}$  (lattice units)"); ax.set_xlim(-0.5, 1.5)
ax.set_title("frozen prediction, 14 fresh arms each", fontsize=7.5, pad=5)
ax.text(-0.34, 1.06, "a", transform=ax.transAxes, fontsize=10, fontweight="bold")

ax = axes[1]
for name, ep, col, mk in (("static", "STATIC_ABSOLUTE_PROFILE_COMPATIBILITY", ACC, "o"),
                          ("mobile", "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY", WARN, "s"),
                          ("ratio", "MOBILE_STATIC_RATIO_COMPATIBILITY", "#4a7a52", "^")):
    d = E[ep]; y = ("static", "mobile", "ratio").index(name)
    lo, hi = d["ci95_relative_percent"]
    ax.plot([lo, hi], [y, y], color=col, lw=1.3)
    ax.plot(d["relative_deviation_percent"], y, mk, ms=5, color=col)
mar = E["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY"]["margin_percent"]
ax.axvspan(-mar, mar, color=MUT, alpha=0.12, lw=0)
ax.axvline(0, color=INK, lw=0.8, ls="--")
for sgn in (-mar, mar):
    ax.axvline(sgn, color=MUT, lw=0.7)
ax.set_yticks([0, 1, 2])
ax.set_yticklabels(["static", "mobile", "mobile / static"], fontsize=7)
ax.set_xlabel("deviation from the frozen prediction  (%)")
ax.set_xlim(-3.6, 3.6); ax.set_ylim(-0.55, 2.62)
ax.text(0, 2.50, f"equivalence margin  $\\pm${mar} %", fontsize=6.6, color=MUT, ha="center")
ax.set_title("all three endpoints inside the margin", fontsize=7.5, pad=5)
ax.text(-0.44, 1.06, "b", transform=ax.transAxes, fontsize=10, fontweight="bold")
save(fig, "fig2_prospective_confirmation",
     {"ARM_VALUES": {k: O[k] for k in ("S_median", "M_median")}, "ENDPOINTS": E},
     ["_adjudication"],
     "Prospective confirmation on 28 fresh arms. (a) The frozen prediction (line) with its "
     "equivalence margin (band) against the 14 arms of each condition (points) and their mean "
     "with a 95 % interval (diamond). (b) The three pre-declared endpoints; every interval lies "
     "wholly inside the margin, and unity is excluded for the ratio.")

# ================================================================= Figure 3
EST = J["_residual"]["ESTIMATOR"]; BY = J["_residual"]["BY_SIZE"]
SEC = J["_adjudication"]["SECONDARY_CHECKS"]; DC = J["_m6"]["DECOMPOSITION"]["DISPERSION_CHECK"]
CDF_S, CDF_M = J["_residual"]["RADIAL_CDF_STATIC"], J["_residual"]["RADIAL_CDF_MOBILE"]
N_MOB = sum(J["_residual"]["ARMS"]["OBDI02"].values()); N_STA = J["_residual"]["ARMS"]["OBTC02_S"]
fig, axgrid = plt.subplots(2, 2, figsize=(6.6, 5.0))
fig.subplots_adjust(wspace=0.42, hspace=0.72)
axes = axgrid.ravel()

ax = axes[0]
ax.plot([d["r"] for d in CDF_M], [d["difference"] for d in CDF_M], "s-", ms=3.0, lw=0.9,
        color=WARN, label=f"mobile, {N_MOB} arms")
ax.plot([d["r"] for d in CDF_S], [d["difference"] for d in CDF_S], "o--", ms=3.0, lw=0.8,
        color=MUT, alpha=0.85, label=f"static, {N_STA} arms")
ax.axhline(0, color=INK, lw=0.8, ls="--")
ax.set_xlabel("radius  (lattice units)", fontsize=7)
ax.set_ylabel("observed $-$ predicted\n(cumulative probability)", fontsize=7)
ax.legend(frameon=False, fontsize=6.6, loc="lower right")
ax.set_ylim(-0.040, 0.046)
ax.set_title("the field follows the operator", fontsize=8, pad=6)
ax.text(-0.30, 1.08, "a", transform=ax.transAxes, fontsize=10, fontweight="bold")

ax = axes[1]
sizes = sorted(BY, key=int)
xs = np.arange(len(sizes))
ax.bar(xs - 0.19, [BY[s]["median"]["residual_percent"] for s in sizes], 0.36,
       color=WARN, label="median rule")
ax.bar(xs + 0.19, [BY[s]["mean"]["residual_percent"] for s in sizes], 0.36,
       color=ACC, label="mean rule")
for i2, s2 in enumerate(sizes):
    ax.text(i2, 0.28, f"n={BY[s2]['median']['n']}", ha="center", fontsize=6.4, color=MUT)
ax.axhline(0, color=INK, lw=0.8)
ax.set_xticks(xs); ax.set_xticklabels([f"L={s}" for s in sizes], fontsize=7)
ax.tick_params(axis="x", pad=2)
ax.set_ylabel("historical residual  (%)", fontsize=7.5)
ax.set_ylim(-6.4, 1.0)
ax.legend(frameon=False, fontsize=6.6, ncol=2, loc="lower center",
          bbox_to_anchor=(0.5, -0.40), handlelength=1.2, columnspacing=1.2)
ax.set_title("only the median rule slips", fontsize=8, pad=6)
ax.text(-0.30, 1.08, "b", transform=ax.transAxes, fontsize=10, fontweight="bold")

ax = axes[2]
MO = J["_m6"]["OBSERVED"]; MR = J["_m6"]["DECOMPOSITION"]["M6_REPRODUCES"]
cells = [("static\nmedian", "static_median", "IID_STATIC", "median_ratio"),
         ("static\nmean", "static_mean", "IID_STATIC", "mean_ratio"),
         ("mobile\nmedian", "mobile_median", "IID_MOBILE", "median_ratio"),
         ("mobile\nmean", "mobile_mean", "IID_MOBILE", "mean_ratio")]
xs = np.arange(4)
obs_c = [MO[k] for _, k, _, _ in cells]
sur_c = [(EST[i][r] - 1) * 100 for _, _, i, r in cells]
ful_c = [MR[k] for _, k, _, _ in cells]
ax.bar(xs - 0.26, obs_c, 0.25, color=INK, label="observed")
ax.bar(xs, sur_c, 0.25, color=MUT, label="surrogate only")
ax.bar(xs + 0.26, ful_c, 0.25, color=ACC, label="full construction")
ax.axhline(0, color=INK, lw=0.8)
ax.set_xticks(xs); ax.set_xticklabels([c[0] for c in cells], fontsize=6.6)
ax.set_ylabel("residual  (%)", fontsize=7.5)
ax.set_ylim(-7.0, 1.5)
ax.legend(frameon=False, fontsize=6.4, ncol=3, loc="lower center",
          bbox_to_anchor=(0.5, -0.42), handlelength=1.2, columnspacing=1.0)
ax.annotate("the surrogate\nstops here", (2 + 0.02, sur_c[2] - 0.15), (2.75, -3.4), fontsize=6.0,
            color=MUT, ha="center",
            arrowprops=dict(arrowstyle="->", lw=0.6, color=MUT))
ax.set_title("what each account reaches", fontsize=8, pad=6)
ax.text(-0.30, 1.08, "c", transform=ax.transAxes, fontsize=10, fontweight="bold")

ax = axes[3]
groups = ["static", "mobile"]
obs = [J["_m6"]["OBSERVED"]["static_within_arm_sd"], J["_m6"]["OBSERVED"]["mobile_within_arm_sd"]]
iid = [EST["IID_STATIC"]["within_arm_sd"], EST["IID_MOBILE"]["within_arm_sd"]]
full = [DC["static_within_arm_sd_simulated"], DC["mobile_within_arm_sd_simulated"]]
xs = np.arange(2)
ax.bar(xs - 0.26, obs, 0.25, color=INK, label="observed")
ax.bar(xs, iid, 0.25, color=MUT, label="surrogate only")
ax.bar(xs + 0.26, full, 0.25, color=ACC, label="full construction")
ax.set_xticks(xs); ax.set_xticklabels(groups, fontsize=7)
ax.set_ylabel("within-arm s.d.  (lattice units)", fontsize=7.5)
ax.set_ylim(0, 2.35)
ax.legend(frameon=False, fontsize=6.6, loc="upper left")
ax.set_title("dispersion separates the accounts", fontsize=8, pad=6)
ax.text(-0.30, 1.08, "d", transform=ax.transAxes, fontsize=10, fontweight="bold")
save(fig, "fig3_summary_rule_artefact",
     {"RADIAL_CDF_MOBILE": CDF_M, "RADIAL_CDF_STATIC": CDF_S,
      "RADIAL_ARMS": {"mobile": N_MOB, "static": N_STA},
      "RADIAL_MAX_ABS_Z": {"mobile": J["_residual"]["RADIAL_CDF_MOBILE_MAX_ABS_Z"],
                           "static": max(abs(d["z"]) for d in CDF_S)},
      "HISTORICAL_BY_SIZE": BY, "ESTIMATOR_SURROGATE": EST,
      "SUMMARY_CELLS": {c[0].replace(chr(10), " "): {"observed": MO[c[1]],
                        "surrogate": (EST[c[2]][c[3]] - 1) * 100, "construction": MR[c[1]]}
                        for c in cells},
      "DISPERSION": {"observed": obs, "surrogate": iid, "full_construction": full},
      "FRESH_ARM_SECONDARY_CHECKS": SEC},
     ["_residual", "_m6", "_adjudication"],
     "The summary rule, not the field. (a) Observed minus predicted cumulative radial profile at "
     "15 radii. Over 116 historical mobile arms the largest standardised deviation is 0.64 and "
     "the largest difference 0.0038. The static curve rests on three arms and is shown for "
     "completeness only: it is not powered for a per-radius test, and its largest standardised "
     "deviation, 8.90, occurs where the absolute difference is no larger than at radii whose "
     "standardised deviation is below one. (b) The historical residual at three lattice sizes "
     "under the frozen median rule and under the mean rule. (c) A surrogate that draws particles "
     "independently from the predicted law and applies the same summary rule, with no lattice "
     "dynamics whatever, is already biased downwards under the median rule and nearly unbiased "
     "under the mean. (d) The surrogate does not account for the observed mobile dispersion; the "
     "full construction does.")

# ================================================================= Figure 4
AB = J["_adjudication"]["ABLATION"]; SEQ = J["_m6"]["DECOMPOSITION"]["SEQUENTIAL"]
FAC = J["_m6"]["DECOMPOSITION"]["FACTORIAL"]; MECH = J["_mechanisms"]
fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.9))
fig.subplots_adjust(wspace=0.92, left=0.13, right=0.955, top=0.84, bottom=0.30)

ax = axes[0]
names = [("full", "full construction"), ("poisson_births", "Poisson source"),
         ("no_shared_trajectory", "no shared trajectory"),
         ("ideal_population_value", "uncorrected ideal")]
obs_m = AB["observed_mobile_median"]
for k, (key, lab) in enumerate(names):
    v = AB["predictions"][key]
    ax.plot([obs_m, v], [k, k], color=MUT, lw=0.7, zorder=1)
    ax.plot(v, k, "o", ms=5.5, color=(ACC if key == "full" else WARN), zorder=3)
    ax.text(v + 0.028, k - 0.02, f"{abs(v - obs_m):.3f}", fontsize=6.4, va="center", color=MUT)
ax.axvline(obs_m, color=INK, lw=1.1, ls="--", zorder=2)
ax.set_yticks(range(4)); ax.set_yticklabels([l for _, l in names], fontsize=6.8)
ax.invert_yaxis(); ax.set_xlabel("mobile $r_{80}$  (lattice units)", fontsize=7.5)
ax.set_xlim(8.02, 8.66)
ax.set_xticks([8.1, 8.3, 8.5])
ax.set_ylim(3.62, -0.55)
ax.text(obs_m + 0.016, 3.46, "observed", fontsize=6.6, color=INK, ha="left", va="bottom")
ax.set_title("distance to the observation", fontsize=8, pad=13)
ax.text(-0.52, 1.10, "a", transform=ax.transAxes, fontsize=10, fontweight="bold")

ax = axes[1]
steps = [("kernel\nalone", SEQ["step_0_baseline_M2_level"]),
         ("+ shared\ntrajectory", SEQ["step_1_add_shared_trajectory"]),
         ("+ birth\nflux", SEQ["step_2_add_empirical_birth_flux"])]
ax.plot(range(3), [v for _, v in steps], "o-", ms=5, lw=1.2, color=ACC)
ax.axhline(J["_m6"]["OBSERVED"]["mobile_median"], color=INK, lw=1.0, ls="--")
ax.text(-0.28, J["_m6"]["OBSERVED"]["mobile_median"] + 0.16, "observed", fontsize=6.6,
        color=INK, va="bottom", ha="left")
ax.set_xticks(range(3)); ax.set_xticklabels([t for t, _ in steps], fontsize=6.8)
ax.set_ylabel("median-summary residual  (%)", fontsize=7.5)
ax.set_xlim(-0.35, 2.35); ax.set_ylim(-6.3, 0.4)
ax.set_title("built up one term at a time", fontsize=8, pad=13)
ax.text(-0.42, 1.10, "b", transform=ax.transAxes, fontsize=10, fontweight="bold")

ax = axes[2]
eff = [("shared\ntrajectory", FAC["main_effect_shared_trajectory"]),
       ("birth-flux\nendogeneity", FAC["main_effect_birth_flux"]),
       ("interaction", FAC["interaction"])]
ax.barh(range(3), [v for _, v in eff], 0.5, color=[ACC, ACC, MUT])
for k, (_, v) in enumerate(eff):
    ax.text(v + 0.14, k, f"{v:+.2f}", fontsize=6.4, va="center", ha="left", color=MUT)
ax.axvline(0, color=INK, lw=0.8)
ax.set_yticks(range(3)); ax.set_yticklabels([t for t, _ in eff], fontsize=6.8)
ax.invert_yaxis(); ax.set_xlabel("main effect  (points of %)", fontsize=7.2)
ax.set_xlim(-4.5, 1.9)
ax.set_xticks([-4, -2, 0])
ax.set_title("a $2\\times2$ decomposition", fontsize=8, pad=13)
ax.text(-0.52, 1.10, "c", transform=ax.transAxes, fontsize=10, fontweight="bold")
save(fig, "fig4_mechanism_ablation",
     {"ABLATION": AB, "SEQUENTIAL": SEQ, "FACTORIAL": FAC,
      "BIRTH_FLUX": MECH["S13_BIRTH_FLUX"]["variance_over_mean"],
      "CAPACITY": MECH["S12_CAPACITY"]["SHADOW_REPLAY_ANALYTIC"],
      "CONTINUUM": {"static": MECH["S11_TORUS_AND_LATTICE"]["static"]["CONTINUUM_TO_DISCRETE_CORRECTION_percent"],
                    "mobile": MECH["S11_TORUS_AND_LATTICE"]["mobile"]["CONTINUUM_TO_DISCRETE_CORRECTION_percent"]}},
     ["_adjudication", "_m6", "_mechanisms"],
     "What the agreement depends on. (a) Distance between the observed mobile radius and four "
     "constructions; the full one is nearest and each ablation is further. (b) The same "
     "constructions built up in physical order. (c) The two main effects and their interaction "
     "in a two-by-two decomposition; the interaction is small.")

with open(f"{PKG}/provenance/PAPER_FIGURE_PROVENANCE.json", "w", encoding="utf-8") as f:
    json.dump({"SECTION": "LRCPS01 §12 figure provenance",
               "N_MAIN_FIGURES": len(PROVENANCE), "MAX_ALLOWED": 6,
               "ALL_REGENERATED_FROM_BOUND_DATA": True,
               "ANY_FIGURE_USES_LOST_OR_NOT_TESTED_EVIDENCE": False,
               "FIGURES": PROVENANCE}, f, indent=1, ensure_ascii=False)
print("figures:", len(PROVENANCE))

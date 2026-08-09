"""P09 figures."""
from __future__ import annotations
import csv, json, math, statistics as S
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d8d7d2"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "grid.color": GRID,
                     "font.size": 9, "axes.titlesize": 9.5, "axes.grid": True,
                     "grid.linewidth": 0.6, "axes.linewidth": 0.8, "legend.frameon": False})

CELLS = [("LAW_16", "24"), ("LAW_16", "32"), ("LAW_29", "24"), ("LAW_29", "32")]
ARMS = ["SHAM", "PARENT_FULL", "PARENT_LOW_CONSTANT", "PARENT_Q_REPLAY", "FLOOR_Q_REPLAY",
        "FLOOR_FULL"]
SHORT = {"SHAM": "sham", "PARENT_FULL": "parent\npleine dose",
         "PARENT_LOW_CONSTANT": "parent\nbas constant", "PARENT_Q_REPLAY": "parent\nq-replay",
         "FLOOR_Q_REPLAY": "plancher\nq-replay", "FLOOR_FULL": "plancher\npleine dose"}


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


rows = list(csv.DictReader(open("p09_rows.csv")))
summ = json.load(open("p09_summary.json"))


def cell(law, sz, arm):
    return [r for r in rows if r["law"] == law and r["size"] == sz and r["arm"] == arm]


def fig1():
    """Survival and delivered mass: the dose axis vs the allocation axis."""
    fig, ax = plt.subplots(2, 2, figsize=(13.0, 7.4))
    x = np.arange(len(ARMS))
    for j, (law, sz) in enumerate(CELLS):
        a = ax[j // 2][j % 2]
        surv = [sum(1 for r in cell(law, sz, k) if r["SURVIVAL_ITT"] == "True") / 9
                for k in ARMS]
        dele = [med([n(r["delivered_over_M256"]) for r in cell(law, sz, k)]) or 0 for k in ARMS]
        spl = [sum(1 for r in cell(law, sz, k) if r["SPLIT"] == "True") for k in ARMS]
        dis = [sum(1 for r in cell(law, sz, k) if r["DISSOLUTION"] == "True") for k in ARMS]
        cols = [C[0] if "PARENT" in k or k == "SHAM" else C[1] for k in ARMS]
        a.bar(x, surv, 0.56, color=cols, edgecolor=SURF)
        a2 = a.twinx()
        a2.plot(x, dele, color=C[5], marker="D", ms=5, lw=1.4, ls="--",
                label="masse délivrée")
        a2.set_ylim(0, 0.72)
        a2.set_ylabel(r"masse délivrée / $M_{256}$", color=C[5], fontsize=8)
        a2.tick_params(axis="y", colors=C[5], labelsize=7)
        a2.grid(False)
        for i, (s, sp, dd) in enumerate(zip(surv, spl, dis)):
            tag = []
            if sp:
                tag.append(f"{sp} sciss.")
            if dd:
                tag.append(f"{dd} dissol.")
            a.text(i, s + 0.04, f"{int(s*9)}/9" + ("\n" + " ".join(tag) if tag else ""),
                   ha="center", fontsize=6.5, color=INK if s == 1 else C[1])
        a.set_xticks(x)
        a.set_xticklabels([SHORT[k] for k in ARMS], fontsize=6.8)
        a.set_ylim(0, 1.28)
        a.set_ylabel("survie ITT (fraction des 9 blocs)")
        a.set_title(f"{law} · L = {sz}", fontsize=10)
    fig.suptitle("P09 · survie et masse délivrée : bleu = allocation PARENT, orange = "
                 "allocation PLANCHER", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig("p09_fig1_survie.png", dpi=160)
    plt.close(fig)


def fig2():
    """Dose equivalence and the four sealed contrasts."""
    eq = summ["DOSE_EQUIVALENCE"]["detail"]
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.3))

    a = ax[0]
    ks = list(eq)
    y = np.arange(len(ks))
    m = [eq[k]["median_ratio"] for k in ks]
    lo = [eq[k]["ci"][0] for k in ks]
    hi = [eq[k]["ci"][1] for k in ks]
    a.axvspan(0.847, 1.180, color=C[2], alpha=0.16)
    a.axvline(1.0, color=INK2, lw=0.9, ls=":")
    a.errorbar(m, y, xerr=[np.array(m) - lo, np.array(hi) - np.array(m)], fmt="o",
               color=C[0], capsize=3)
    for i, k in enumerate(ks):
        a.text(1.36, i, "PASS" if eq[k]["EQUIVALENCE_PASSES"] else "ÉCHEC", va="center",
               fontsize=8, color=INK if eq[k]["EQUIVALENCE_PASSES"] else C[1],
               weight="bold")
    a.set_yticks(y)
    a.set_yticklabels([k.replace("|", "\n") for k in ks], fontsize=7.5)
    a.set_xlim(0.7, 1.5)
    a.set_xlabel("masse délivrée : plancher-q-replay / parent-q-replay")
    a.set_title("équivalence de dose\n(marge scellée avant exécution)", fontsize=9.5)

    a = ax[1]
    names = ["ALLOCATION  FLOOR_Q_REPLAY - PARENT_Q_REPLAY",
             "TEMPORAL    PARENT_Q_REPLAY - PARENT_LOW_CONSTANT",
             "DOSE        PARENT_LOW_CONSTANT - PARENT_FULL",
             "P08_REPLIC  FLOOR_FULL - PARENT_FULL"]
    lab = ["allocation", "profil temporel", "réduction de dose", "réplication P08"]
    w = 0.2
    for j, (law, sz) in enumerate(CELLS):
        v = [summ["PRIMARY_CONTRASTS"][f"{law}|L{sz}"][k]["survival"]["difference"] / 9
             for k in names]
        a.bar(np.arange(len(names)) + (j - 1.5) * w, v, w * 0.9, color=C[j],
              label=f"{law.replace('LAW_','L')} L{sz}", edgecolor=SURF)
    a.axhline(0, color=INK2, lw=0.9)
    a.set_xticks(range(len(names)))
    a.set_xticklabels(lab, fontsize=7.5, rotation=18, ha="right")
    a.set_ylabel("effet sur la survie ITT (fraction des 9 blocs)")
    a.set_title("les quatre contrastes primaires scellés", fontsize=9.5)
    a.legend(fontsize=7)

    a = ax[2]
    for j, (law, sz) in enumerate(CELLS):
        dl = [med([n(r["delivered_over_M256"]) for r in cell(law, sz, k)]) or 0 for k in ARMS]
        sv = [sum(1 for r in cell(law, sz, k) if r["SURVIVAL_ITT"] == "True") / 9
              for k in ARMS]
        mk = ["o" if "PARENT" in k or k == "SHAM" else "s" for k in ARMS]
        for d_, s_, m_ in zip(dl, sv, mk):
            a.scatter(d_, s_ + (j - 1.5) * 0.012, color=C[j], marker=m_, s=44, zorder=3)
        a.plot(dl, [s + (j - 1.5) * 0.012 for s in sv], color=C[j], lw=0.9, alpha=0.4,
               label=f"{law.replace('LAW_','L')} L{sz}")
    a.set_xlabel(r"masse délivrée / $M_{256}$")
    a.set_ylabel("survie ITT")
    a.set_title("survie contre dose délivrée\n(rond = allocation parent, carré = plancher)",
                fontsize=9.5)
    a.legend(fontsize=7)
    fig.suptitle("P09 · l'axe dose et l'axe allocation, séparés", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p09_fig2_contrastes.png", dpi=160)
    plt.close(fig)


def fig3():
    """UCR components and the frames."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.3))
    x = np.arange(len(ARMS))
    a = ax[0]
    for j, (law, sz) in enumerate(CELLS):
        v = [med([n(r["UCR"]) for r in cell(law, sz, k)]) or 0 for k in ARMS]
        a.plot(x, v, color=C[j], marker="o", lw=1.4,
               label=f"{law.replace('LAW_','L')} L{sz}")
    a.set_xticks(x)
    a.set_xticklabels([SHORT[k] for k in ARMS], fontsize=6.8)
    a.set_ylabel("UNIQUE_CAUSAL_REPLACEMENT")
    a.set_title("remplacement causal unique", fontsize=9.5)
    a.legend(fontsize=7)

    a = ax[1]
    law, sz = "LAW_29", "24"
    inc = [med([n(r["incumbent_removed_over_M256"]) for r in cell(law, sz, k)]) or 0
           for k in ARMS]
    fr = [med([n(r["fresh_over_M256"]) for r in cell(law, sz, k)]) or 0 for k in ARMS]
    a.bar(x - 0.19, inc, 0.36, color=C[2], label="incumbent retiré (compté une fois)")
    a.bar(x + 0.19, fr, 0.36, color=C[4], label="frais retenu à l'horizon")
    a.set_xticks(x)
    a.set_xticklabels([SHORT[k] for k in ARMS], fontsize=6.8)
    a.set_ylabel(r"fraction de $M_{256}$")
    a.set_title("LAW_29 L=24 · les deux composantes de l'UCR\n"
                "(l'UCR est leur minimum)", fontsize=9.5)
    a.legend(fontsize=7)

    a = ax[2]
    for j, (law, sz) in enumerate(CELLS):
        v = [med([(n(r.get("terminal_mass_in_frozen_C256")) or 0) / n(r["M256"])
                  for r in cell(law, sz, k)]) or 0 for k in ARMS]
        w = [med([n(r.get("terminal_jaccard_C256_Ct")) for r in cell(law, sz, k)]) or 0
             for k in ARMS]
        a.plot(x, v, color=C[j], marker="o", lw=1.4,
               label=f"{law.replace('LAW_','L')} L{sz} · repère fixe")
        a.plot(x, w, color=C[j], marker="^", lw=1.0, ls="--", alpha=0.7)
    a.set_xticks(x)
    a.set_xticklabels([SHORT[k] for k in ARMS], fontsize=6.8)
    a.set_ylabel("plein : masse dans $C_{256}$ figé  ·  tirets : Jaccard $C_{256}\\cap C_t$")
    a.set_title("repère fixe et repère d'intersection", fontsize=9.5)
    a.legend(fontsize=6.5)
    fig.suptitle("P09 · composantes de l'endpoint et référentiels", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p09_fig3_endpoints.png", dpi=160)
    plt.close(fig)


for f in (fig1, fig2, fig3):
    try:
        f()
        print("ok", f.__name__)
    except Exception:
        import traceback
        traceback.print_exc()

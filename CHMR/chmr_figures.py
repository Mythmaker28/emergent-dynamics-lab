"""CHMR figures."""
from __future__ import annotations
import sys, json, statistics as S
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import chmr_analyse as A

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d8d7d2"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "grid.color": GRID,
                     "font.size": 9, "axes.titlesize": 9.5, "axes.grid": True,
                     "grid.linewidth": 0.6, "axes.linewidth": 0.8, "legend.frameon": False})

CF = A.load("FAR", "CONF")
HD = A.load("NEAR", "HELD")
DV = A.load("FAR", "DEV")
DD = json.load(open("chmr_devD.json"))
PL = json.load(open("chmr_phaseL.json"))
TIMES = [0, 25, 50, 100, 150, 200, 250, 300, 350, 400, 500, 700]


def med(x):
    x = [v for v in x if v is not None]
    return S.median(x) if x else float("nan")


def fig1():
    """Timescale separation, and the halo through time."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.2))
    a = ax[0]
    sc = DD["T_RECOVERY_scan"]
    t = [x["t"] for x in sc]
    r = [x["max_residual_c"] for x in sc]
    a.plot(t, r, color=C[1], marker="o", lw=1.6, label="halo orphelin (résidu max, 8 blocs DEV)")
    ret = [med([A.hgap(b, "MATCHED_SHAM", tt) / A.hgap(b, "MATCHED_SHAM", 0) for b in CF])
           for tt in TIMES if tt <= 400]
    a.plot([x for x in TIMES if x <= 400], ret, color=C[0], marker="s", lw=1.6,
           label="paire intacte appariée (rétention)")
    a.axhline(0.10, color=C[2], lw=1.2, ls="--")
    a.axvline(350, color=INK2, lw=1.0, ls=":")
    a.text(355, 0.8, r"$T_{RECOVERY}=350$", fontsize=7.5, color=INK2)
    a.text(5, 0.115, "critère gelé : résidu ≤ 10 %", fontsize=7.5, color=C[2])
    a.set_xlabel("pas depuis l'intervention")
    a.set_ylabel("écart de halo restant / écart initial")
    a.set_title("séparation des échelles de temps\n(choisie sur DEV, avant tout résultat)",
                fontsize=9)
    a.legend(fontsize=7.5)

    a = ax[1]
    ARMS = [("MATCHED_SHAM", "apparié (sham)", C[2]), ("HALO_CROSS", "halo croisé", C[0]),
            ("HALO_CROSS_CORE_ERASE", "halo croisé + cœur effacé", C[4]),
            ("HALO_CROSS_WRITER_OFF", "halo croisé + écrivain coupé", C[5]),
            ("ORPHAN_HALO", "halo orphelin", C[1])]
    for arm, lab, col in ARMS:
        y = [med([A.hgap(b, arm, tt) for b in CF]) for tt in TIMES if tt <= 400]
        a.plot([x for x in TIMES if x <= 400], y, color=col, marker="o", ms=3.5, lw=1.5,
               label=lab)
    a.axhline(0, color=INK2, lw=0.9)
    a.axvline(350, color=INK2, lw=1.0, ls=":")
    a.set_xlabel("pas depuis l'intervention")
    a.set_ylabel(r"écart de halo $h_A - h_B$")
    a.set_title("le halo dans le temps, par bras\n(12 blocs confirmatoires, médiane)",
                fontsize=9)
    a.legend(fontsize=7)

    a = ax[2]
    labs, vals, cis, cols = [], [], [], []
    for tag, B, col in (("FAR confirmatoire", CF, C[0]), ("NEAR tenu à l'écart", HD, C[3])):
        c = A.cdhr(B, 350)
        for arm, nm in (("HALO_CROSS", "halo croisé"),
                        ("HALO_CROSS_CORE_ERASE", "+ cœur effacé"),
                        ("HALO_CROSS_WRITER_OFF", "+ écrivain coupé"),
                        ("DOUBLE_CROSS", "double croisement")):
            v = c.get(f"CDHR_{arm}")
            if v:
                labs.append(f"{nm}\n{tag}"); vals.append(v["median"]); cis.append(v["ci95"])
                cols.append(col)
    y = np.arange(len(labs))
    lo = [v - x[0] for v, x in zip(vals, cis)]
    hi = [x[1] - v for v, x in zip(vals, cis)]
    a.axvline(-1, color=C[1], lw=1.2, ls="--")
    a.axvline(0, color=INK2, lw=0.9)
    a.axvline(1, color=C[2], lw=1.2, ls="--")
    a.text(-1, len(labs) - 0.3, "état croisé", fontsize=7, color=C[1], ha="center")
    a.text(1, len(labs) - 0.3, "reconstruit", fontsize=7, color=C[2], ha="center")
    for i in range(len(labs)):
        a.errorbar(vals[i], y[i], xerr=[[lo[i]], [hi[i]]], fmt="o", color=cols[i], capsize=3)
    a.set_yticks(y); a.set_yticklabels(labs, fontsize=6.8)
    a.set_xlim(-1.25, 1.35)
    a.set_xlabel("CDHR à $T_{RECOVERY}$")
    a.set_title("critère primaire scellé", fontsize=9)
    fig.suptitle("CHMR · le halo ne revient pas vers le label de son cœur", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("chmr_fig1_halo.png", dpi=160)
    plt.close(fig)


def fig2():
    """Core through time, the pulse, and the response."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.2))
    a = ax[0]
    for arm, lab, col in (("MATCHED_SHAM", "apparié (sham)", C[2]),
                          ("HALO_CROSS", "halo croisé", C[0]),
                          ("HALO_PULSE_RESTORE", "halo pulsé puis restauré", C[1]),
                          ("CORE_CROSS", "cœur croisé", C[5])):
        y = [med([(A.cplus(b, arm, tt, "A") - A.cplus(b, arm, tt, "B"))
                  if A.cplus(b, arm, tt, "A") is not None
                  and A.cplus(b, arm, tt, "B") is not None else None for b in CF])
             for tt in TIMES]
        a.plot(TIMES, y, color=col, marker="o", ms=3.5, lw=1.5, label=lab)
    a.axvline(350, color=INK2, lw=1.0, ls=":")
    a.text(357, a.get_ylim()[1] * 0.86, "halo restauré", fontsize=7, color=INK2)
    a.axhline(0, color=INK2, lw=0.9)
    a.set_xlabel("pas depuis l'intervention")
    a.set_ylabel(r"écart de cœur $m_+^A - m_+^B$")
    a.set_title("le cœur dans le temps :\nun halo imposé le réécrit", fontsize=9)
    a.legend(fontsize=7)

    a = ax[1]
    rows = []
    for tag, B, col in (("FAR confirmatoire", CF, C[0]), ("NEAR tenu à l'écart", HD, C[3])):
        g = A.g7_pulse(B)["core_gap_matched_vs_pulse"]
        rows.append((tag, g["median_matched"], g["median_pulse"], g["median_difference"],
                     g["ci95"], col))
    x = np.arange(len(rows))
    a.bar(x - 0.19, [r[1] for r in rows], 0.36, color=C[2], label="apparié (jamais croisé)")
    a.bar(x + 0.19, [r[2] for r in rows], 0.36, color=C[1], label="pulsé puis restauré")
    for i, r in enumerate(rows):
        a.text(i, min(r[1], r[2]) - 0.06, f"Δ = {r[3]:+.3f}\n[{r[4][0]:+.3f};{r[4][1]:+.3f}]",
               ha="center", fontsize=7)
    a.axhline(0, color=INK2, lw=0.9)
    a.set_xticks(x); a.set_xticklabels([r[0] for r in rows], fontsize=8)
    a.set_ylabel(r"écart de cœur à $t=700$")
    a.set_title("G7 · le halo réécrit-il le cœur ?\n(mêmes temps, halo restauré)", fontsize=9)
    a.legend(fontsize=7.5)

    a = ax[2]
    labs, vals, cis, cols = [], [], [], []
    for tag, B, col in (("FAR", CF, C[0]), ("NEAR", HD, C[3])):
        g = A.g8_response(B, "response")
        for arm, nm in (("HALO_CROSS", "halo croisé"),
                        ("HALO_CROSS_CORE_ERASE", "halo croisé\n+ cœur effacé"),
                        ("CORE_CROSS", "cœur croisé"),
                        ("DOUBLE_CROSS", "double croisement")):
            k = f"signed_gap_{arm}_minus_MATCHED"
            if k in g:
                labs.append(f"{nm}  ({tag})"); vals.append(g[k]["median"])
                cis.append(g[k]["ci95"]); cols.append(col)
    y = np.arange(len(labs))
    lo = [max(v - x[0], 0) for v, x in zip(vals, cis)]
    hi = [max(x[1] - v, 0) for v, x in zip(vals, cis)]
    a.axvline(0, color=INK2, lw=0.9)
    for i in range(len(labs)):
        a.errorbar(vals[i], y[i], xerr=[[lo[i]], [hi[i]]], fmt="o", color=cols[i], capsize=3)
    a.set_yticks(y); a.set_yticklabels(labs, fontsize=6.8)
    a.set_xlabel("réponse au défi : écart signé A−B, moins l'apparié")
    a.set_title("G8 · la réponse future suit le halo courant,\npas le cœur", fontsize=9)
    fig.suptitle("CHMR · la direction causale va du halo vers le cœur", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("chmr_fig2_core.png", dpi=160)
    plt.close(fig)


def fig3():
    """Lineage audit and turnover."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.2))
    a = ax[0]
    fw = PL["PART2_frozen_world_largest_audit"]
    x = np.arange(len(fw))
    a.bar(x - 0.27, [r["n_argmax_switches"] for r in fw], 0.24, color=C[1],
          label="changements de lignée de largest(st)")
    a.bar(x, [r["n_splits"] for r in fw], 0.24, color=C[0], label="scissions")
    a.bar(x + 0.27, [r["n_fusions"] for r in fw], 0.24, color=C[3], label="fusions")
    a.set_xticks(x); a.set_xticklabels([str(r["seed"]) for r in fw], fontsize=8)
    a.set_ylabel("événements en 2600 pas")
    a.set_title("le monde gelé sc_mcm :\n`largest(st)` est une statistique de rang", fontsize=9)
    a.legend(fontsize=7)

    a = ax[1]
    tot = {}
    for tag, B in (("FAR dev", DV), ("FAR conf", CF), ("NEAR tenu à l'écart", HD)):
        if not B:
            continue
        g = A.g1_lineage(B)
        tot[tag] = g
    x = np.arange(len(tot))
    for j, k in enumerate(("splits", "fusions", "disappearances", "argmax_switches")):
        a.bar(x + (j - 1.5) * 0.2, [tot[t][k] for t in tot], 0.18, color=C[j], label=k)
    a.set_xticks(x); a.set_xticklabels(list(tot), fontsize=8)
    a.set_ylabel("événements, toutes trajectoires confondues")
    a.set_ylim(0, 1)
    a.set_title("la lignée prospective du programme :\nzéro scission, zéro fusion", fontsize=9)
    a.legend(fontsize=7)

    a = ax[2]
    for j, (tag, B, col) in enumerate((("FAR conf", CF, C[0]), ("NEAR tenu à l'écart", HD, C[3]),
                                       ("FAR dev", DV, C[4]))):
        if not B:
            continue
        g = A.g9_turnover(B)
        M = [r["M_final"] for r in g["rows"] if r["M_final"] is not None]
        a.scatter(np.full(len(M), j) + np.random.default_rng(j).uniform(-.16, .16, len(M)),
                  M, s=16, color=col, alpha=0.75, zorder=3)
        a.text(j, 0.02, f"n={len(M)}\nmed={S.median(M):.3f}", ha="center", fontsize=7)
    a.axhline(0.35, color=C[1], lw=1.2, ls="--")
    a.text(2.4, 0.363, r"$M_{LOW}=0{,}35$ (gelé)", fontsize=7.5, color=C[1], ha="right")
    a.set_xticks(range(3))
    a.set_xticklabels(["FAR conf", "NEAR tenu\nà l'écart", "FAR dev"], fontsize=8)
    a.set_ylim(0, 0.5)
    a.set_ylabel(r"$M$ résolu par lignée continue")
    a.set_title("G9 · renouvellement résolu par lignée\n(ce que DOMC ne pouvait pas établir)",
                fontsize=9)
    fig.suptitle("CHMR · audit de lignée et renouvellement", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("chmr_fig3_lineage.png", dpi=160)
    plt.close(fig)


for f in (fig1, fig2, fig3):
    try:
        f(); print("ok", f.__name__)
    except Exception:
        import traceback; traceback.print_exc()

"""DOMC figures."""
from __future__ import annotations
import sys, json, pickle, statistics as S
sys.path.insert(0, "/home/claude/sweep")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import domc_analyse as A

C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#4a3aa7"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d8d7d2"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF,
                     "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "grid.color": GRID,
                     "font.size": 9, "axes.titlesize": 9.5, "axes.grid": True,
                     "grid.linewidth": 0.6, "axes.linewidth": 0.8, "legend.frameon": False})

PR = A.load("FAR", "PROSP", "cc-00")
DV = A.load("FAR", "DEV", "cc-00")
D0 = A.load("FAR", "DEV", "")            # the Nc|cN design run, if present under the old name
if not D0:
    try:
        D0 = pickle.load(open("domc_FAR_DEV.pkl", "rb"))
    except Exception:
        D0 = []
NR = A.load("NEAR", "PROSP", "cc-00")
PC = json.load(open("domc_phaseC.json"))


def med(x):
    x = [v for v in x if v is not None]
    return S.median(x) if x else float("nan")


# ------------------------------------------------------------------------------------ fig 1
def fig1():
    """The world, the states, and the collision."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.1))

    a = ax[0]
    ks = list(PC["per_pair"])
    q = [PC["per_pair"][k]["median_Q"] for k in ks]
    dm = [PC["per_pair"][k]["median_abs_dm_plus"] for k in ks]
    ds = [PC["per_pair"][k]["median_abs_dsize"] / PC["per_pair"][k]["median_mean_size"]
          for k in ks]
    y = np.arange(len(ks))
    a.barh(y - 0.2, dm, 0.38, color=C[0], label=r"séparation mémoire $|\Delta m_+|$")
    a.barh(y + 0.2, ds, 0.38, color=C[1], label="désaccord de corps $|\\Delta$taille$|$/taille")
    for i, k in enumerate(ks):
        a.text(3.05, i, f"Q={q[i]:.2f}", va="center", fontsize=7,
               weight="bold" if k == PC["SELECTED_PAIR"] else "normal",
               color=C[2] if k == PC["SELECTED_PAIR"] else INK2)
    a.set_yticks(y); a.set_yticklabels(ks, fontsize=7.5)
    a.set_xlim(0, 3.6)
    a.set_title("Phase C · les 8 paires d'histoires candidates\n"
                "(sélection sur DEV, dictionnaire scalaire gelé)", fontsize=9)
    a.legend(fontsize=7, loc="lower right")

    a = ax[1]
    codes = list(PC["collision"])
    lk = [PC["collision"][c]["median_leak_plus"] for c in codes]
    a.bar(range(len(codes)), lk, 0.5, color=C[3])
    for i, v in enumerate(lk):
        a.text(i, v * 1.4, f"{v:.5f}", ha="center", fontsize=7.5)
    a.set_yscale("log"); a.set_ylim(1e-5, 1.0)
    a.axhline(1.0, color=C[1], lw=1.0, ls="--")
    a.text(len(codes) - 0.55, 1.05, "collision totale", fontsize=7, color=C[1], ha="right")
    a.set_xticks(range(len(codes))); a.set_xticklabels(codes)
    a.set_ylabel(r"$|\Delta m_+|$ non pilotée / $|\Delta m_+|$ pilotée")
    a.set_title("la collision mesurée : ce qui fuit\ndans la mémoire de l'autre composant",
                fontsize=9)

    a = ax[2]
    if PR:
        for j, (k, lab) in enumerate((("AB|NONE", "DUAL_AB"), ("BA|NONE", "DUAL_BA"),
                                      ("AA|NONE", "DUAL_AA"), ("AB|CROSS", "AB + échange"))):
            mA = [b["arms"][k]["t0"]["scalars"]["A"]["m_plus"] for b in PR
                  if b["arms"].get(k) and b["arms"][k]["t0"]["scalars"]["A"]]
            mB = [b["arms"][k]["t0"]["scalars"]["B"]["m_plus"] for b in PR
                  if b["arms"].get(k) and b["arms"][k]["t0"]["scalars"]["B"]]
            a.scatter([j - 0.13] * len(mA), mA, s=26, color=C[0], zorder=3,
                      label="site A" if j == 0 else None)
            a.scatter([j + 0.13] * len(mB), mB, s=26, color=C[1], marker="s", zorder=3,
                      label="site B" if j == 0 else None)
        a.set_xticks(range(4))
        a.set_xticklabels(["DUAL_AB", "DUAL_BA", "DUAL_AA", "AB +\néchange"], fontsize=8)
    a.axhline(0, color=INK2, lw=0.8)
    a.set_ylabel(r"état mémoire $m_+$ du composant")
    a.set_title("les états sont distincts, adressables,\net l'échange les permute\n"
                "(12 blocs prospectifs)", fontsize=9)
    a.legend(fontsize=7.5)
    fig.suptitle("DOMC · un monde à deux composants, deux états, une collision mesurée",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("domc_fig1_states.png", dpi=160)
    plt.close(fig)


# ------------------------------------------------------------------------------------ fig 2
def fig2():
    """The causal tests: erasure, exchange, and the environment rival."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.1))

    a = ax[0]
    er = A.erasure(PR, "t0") if PR else None
    if er:
        m = er["median"]
        lab = ["effacer A\n→ A", "effacer A\n→ B", "effacer B\n→ B", "effacer B\n→ A"]
        v = [m["eraseA_on_A"], m["eraseA_on_B"], m["eraseB_on_B"], m["eraseB_on_A"]]
        col = [C[0], C[4], C[1], C[4]]
        a.bar(range(4), [max(x, 1e-8) for x in v], 0.55, color=col)
        for i, x in enumerate(v):
            a.text(i, max(x, 1e-8) * 1.6, f"{x:.2e}" if x < 1e-3 else f"{x:.2f}",
                   ha="center", fontsize=7)
        a.set_yscale("log")
        a.set_xticks(range(4)); a.set_xticklabels(lab, fontsize=7.5)
        a.set_ylabel("déplacement de la réponse causale")
        a.set_title(f"effacement sélectif\nsélectivité A = {er['selectivity_A']:.3g}× · "
                    f"B = {er['selectivity_B']:.2f}×", fontsize=9)

    a = ax[1]
    labs, vals, cis, cols = [], [], [], []
    for when, tag in (("t0", "à l'échéance"), ("turn", "après renouvellement")):
        for iv, nm, c in (("CROSS", "échange mémoire", C[0]),
                          ("CROSS_ROLL", "échange (translation)", C[5]),
                          ("CROSS_ENV", "échange environnement", C[1])):
            r = A.crossing(PR, when, iv) if PR else None
            if not r or r["n"] == 0:
                continue
            labs.append(f"{nm}\n{tag}")
            vals.append(r["PRIMARY_median_transfer_fraction"])
            cis.append(r["PRIMARY_transfer_ci95"])
            cols.append(c)
    y = np.arange(len(labs))
    lo = [v - c[0] for v, c in zip(vals, cis)]
    hi = [c[1] - v for v, c in zip(vals, cis)]
    a.axvspan(-0.05, 0.05, color=GRID, alpha=0.5)
    a.axvline(0, color=INK2, lw=0.9)
    a.axvline(1, color=C[2], lw=1.0, ls="--")
    a.text(1.0, -0.62, "échange complet", fontsize=7, color=C[2], ha="center")
    for i in range(len(labs)):
        a.errorbar(vals[i], y[i], xerr=[[lo[i]], [hi[i]]], fmt="o", color=cols[i], capsize=3)
    a.set_yticks(y); a.set_yticklabels(labs, fontsize=7)
    a.set_xlabel("FRACTION DE TRANSFERT (0 = rien, 1 = échange complet)")
    a.set_title("le critère primaire scellé", fontsize=9)

    a = ax[2]
    if PR:
        oh0 = A.ownership(PR, "t0"); oht = A.ownership(PR, "turn")
        for j, (o, tag, c) in enumerate(((oh0, "à l'échéance", C[0]),
                                         (oht, "après renouvellement", C[3]))):
            r = [x for x in o["rows"] if x["valid"]]
            a.scatter([x["d_site"] for x in r], [x["d_history"] for x in r],
                      s=34, color=c, label=f"{tag}  (médiane ×{o['median_ratio']:.1f})",
                      zorder=3)
        lim = max(1e-2, max([x["d_history"] for x in oh0["rows"] if x["valid"]] +
                            [x["d_history"] for x in oht["rows"] if x["valid"]]) * 1.4)
        a.plot([1e-2, lim], [1e-2, lim], color=INK2, lw=0.9, ls=":")
        a.set_xscale("log"); a.set_yscale("log")
        a.set_xlabel("distance MÊME histoire, AUTRE site")
        a.set_ylabel("distance MÊME site, AUTRE histoire")
        a.set_title("propriété : l'histoire, pas la position\n"
                    "(forçage global identique entre les deux bras)", fontsize=9)
        a.legend(fontsize=7)
    fig.suptitle("DOMC · effacer, échanger, et le rival environnemental", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("domc_fig2_causal.png", dpi=160)
    plt.close(fig)


# ------------------------------------------------------------------------------------ fig 3
def fig3():
    """Turnover, geometry, and the design run that had to be discarded as an endpoint."""
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.1))

    a = ax[0]
    for j, (B, tag, c) in enumerate(((PR, "FAR prospectif", C[0]),
                                     (NR, "NEAR prospectif", C[1]),
                                     (DV, "FAR dev", C[3]))):
        if not B:
            continue
        M = [v["turn"][f"M_{s}"] for b in B for v in b["arms"].values()
             for s in ("A", "B") if v["turn"][f"M_{s}"] is not None]
        a.scatter(np.full(len(M), j) + np.random.default_rng(j).uniform(-.16, .16, len(M)),
                  M, s=14, color=c, alpha=0.7, zorder=3)
        a.text(j, 0.02, f"n={len(M)}\nmed={S.median(M):.3f}", ha="center", fontsize=7)
    a.axhline(0.35, color=C[1], lw=1.2, ls="--")
    a.text(2.4, 0.365, r"$M_{LOW}=0{,}35$ (gelé)", fontsize=7.5, color=C[1], ha="right")
    a.set_xticks(range(3)); a.set_xticklabels(["FAR prosp.", "NEAR prosp.", "FAR dev"],
                                              fontsize=8)
    a.set_ylabel(r"$M$ : fraction de matière d'origine restante")
    a.set_ylim(0, 0.55)
    a.set_title("le critère de renouvellement matériel gelé\n(par composant, jamais mis en commun)",
                fontsize=9)

    a = ax[1]
    rows = []
    for B, tag in ((PR, "FAR"), (NR, "NEAR")):
        if not B:
            continue
        for when in ("t0", "turn"):
            o = A.ownership(B, when)
            cr = A.crossing(B, when, "CROSS")
            rows.append((f"{tag}\n{when}", o["median_ratio"],
                         cr["PRIMARY_median_transfer_fraction"] if cr["n"] else None))
    x = np.arange(len(rows))
    a.bar(x - 0.19, [r[1] for r in rows], 0.36, color=C[0], label="rapport de propriété")
    a2 = a.twinx()
    a2.bar(x + 0.19, [r[2] if r[2] is not None else 0 for r in rows], 0.36, color=C[1],
           label="fraction de transfert")
    a2.axhline(0, color=INK2, lw=0.8); a2.grid(False)
    a2.set_ylabel("fraction de transfert", color=C[1], fontsize=8)
    a2.tick_params(axis="y", colors=C[1], labelsize=7)
    a.set_xticks(x); a.set_xticklabels([r[0] for r in rows], fontsize=7.5)
    a.set_ylabel("rapport histoire / site", color=C[0])
    a.set_title("les deux géométries, les deux échéances", fontsize=9)

    a = ax[2]
    if D0:
        o0 = A.ownership(D0, "t0")
        sz = [(b["arms"]["AB|NONE"]["t0"]["scalars"]["A"]["size"],
               b["arms"]["AB|NONE"]["t0"]["scalars"]["B"]["size"]) for b in D0
              if b["arms"]["AB|NONE"]["t0"]["scalars"]["A"]]
        a.scatter([abs(p - q) for p, q in sz], [r["d_history"] for r in o0["rows"] if r["valid"]],
                  s=34, color=C[4], label="paire d'ordre  Nc|cN  (écartée)", zorder=3)
    if PR:
        oP = A.ownership(PR, "t0")
        szP = [(b["arms"]["AB|NONE"]["t0"]["scalars"]["A"]["size"],
                b["arms"]["AB|NONE"]["t0"]["scalars"]["B"]["size"]) for b in PR
               if b["arms"]["AB|NONE"]["t0"]["scalars"]["A"]]
        a.scatter([abs(p - q) for p, q in szP], [r["d_history"] for r in oP["rows"] if r["valid"]],
                  s=34, color=C[2], label="paire retenue  cc|00", zorder=3)
    a.set_xlabel("désaccord de corps : |taille A − taille B| (cellules)")
    a.set_ylabel("distance de réponse entre les deux histoires")
    a.set_title("pourquoi la paire d'ordre a été écartée :\nson « état » était une différence de corps",
                fontsize=9)
    a.legend(fontsize=7.5)
    fig.suptitle("DOMC · renouvellement, géométrie, et la paire écartée", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("domc_fig3_design.png", dpi=160)
    plt.close(fig)


for f in (fig1, fig2, fig3):
    try:
        f(); print("ok", f.__name__)
    except Exception:
        import traceback; traceback.print_exc()

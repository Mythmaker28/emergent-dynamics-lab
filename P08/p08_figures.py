"""PROGRAM_08 figures."""
from __future__ import annotations
import csv, json, math, statistics as S
from collections import defaultdict
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


def n(v):
    try:
        x = float(v)
        return None if math.isnan(x) else x
    except (TypeError, ValueError):
        return None


def rd(p):
    return list(csv.DictReader(open(p)))


def med(xs):
    xs = [x for x in xs if x is not None]
    return S.median(xs) if xs else None


# ============================================== fig 1 : rho is a real, decaying physical rate
def fig1():
    pr = rd("p08a_probe.csv")
    cur = rd("p08a_probe_curves.csv")
    aud = json.load(open("p08_audit.json"))
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.1))

    a = ax[0]
    byk = defaultdict(dict)
    for r in cur:
        byk[(r["size"], int(r["checkpoint"]), r["block"])][int(r["u"])] = n(r["headroom"])
    for j, cp in enumerate((272, 1296, 2320, 3344)):
        us = sorted({u for k, v in byk.items() if k[1] == cp for u in v})
        ys = [med([v.get(u) for k, v in byk.items() if k[0] == "24" and k[1] == cp])
              for u in us]
        a.plot(us, ys, color=C[j], lw=1.7, label=f"sonde a t = {cp}")
    a.set_xlabel("pas apres saturation")
    a.set_ylabel(r"place libre rouverte  $\Sigma(M_{max}-m)$")
    a.set_title("L=24 · reouverture apres saturation de la source\n"
                "(aucun operateur pendant la mesure)")
    a.legend(fontsize=7.5)

    a = ax[1]
    for j, L in enumerate(("24", "32")):
        cps, pb, ob = [], [], []
        for cp in (272, 1296, 2320, 3344):
            g = [r for r in pr if r["size"] == L and int(r["checkpoint"]) == cp
                 and n(r.get("rho_observed_next_window")) is not None]
            if not g:
                continue
            cps.append(cp)
            pb.append(med([n(r["rho_probe_slope8"]) for r in g]))
            ob.append(med([n(r["rho_observed_next_window"]) for r in g]))
        a.plot(cps, pb, color=C[j], marker="o", lw=1.7, label=f"L={L} · sonde (independante)")
        a.plot(cps, ob, color=C[j], marker="s", ls="--", lw=1.2,
               label=f"L={L} · debit observe")
    a.set_yscale("log")
    a.set_xlabel("temps du point de mesure")
    a.set_ylabel(r"$\rho$  (masse par pas)")
    a.set_title(r"$\rho$ est predit independamment et il DECROIT" "\n"
                r"(facteur 3,1 et 4,7 entre $t=272$ et $t=2320$)")
    a.legend(fontsize=7)

    a = ax[2]
    m = aud["A4_RIVAL_MODELS"]["detail"]
    names = ["CONSTANT_RATE", "FINITE_CAPACITY_RESERVOIR", "PROGRESSIVE_SATURATION",
             "POWER_LAW"]
    x = np.arange(len(names))
    for j, L in enumerate(("L24", "L32")):
        v = [m[L]["held_out_RMSE_median"][k] for k in names]
        a.bar(x + (j - 0.5) * 0.38, v, 0.36, color=C[j], label=L, edgecolor=SURF)
    a.set_xticks(x)
    a.set_xticklabels([k.replace("_", "\n") for k in names], fontsize=7)
    a.set_ylabel("RMSE hors echantillon (masse cumulee)")
    a.set_title("modeles rivaux, ajustes sur la 1re moitie,\n"
                "notes sur la 2de : CONSTANT_RATE gagne 0 bloc sur 18")
    a.legend(fontsize=8)
    fig.suptitle(r"PROGRAM_08 · $\rho$ est une vraie vitesse physique, mesurable seule — "
                 r"mais ce n'est pas une constante", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p08_fig1_rho.png", dpi=160)
    plt.close(fig)


# ==================================== fig 2 : the 2x2 amount factorial and the feedback arms
def fig2():
    b = json.load(open("p08b_summary.json"))["FACTORIAL"]
    c = json.load(open("p08c_summary.json"))["ARMS"]
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.2))

    arms = ["PARENT", "SINK_FLOOR", "SRC_CAP", "BOTH_SAFE"]
    x = np.arange(len(arms))
    a = ax[0]
    for j, L in enumerate(("24", "32")):
        v = [b[f"L{L}|{k}"]["UCR_median"] for k in arms]
        lo = [b[f"L{L}|{k}"]["UCR_ci"][0] for k in arms]
        hi = [b[f"L{L}|{k}"]["UCR_ci"][1] for k in arms]
        a.errorbar(x + (j - 0.5) * 0.16, v, yerr=[np.array(v) - lo, np.array(hi) - v],
                   color=C[j], marker="o", ls="none", capsize=3, label=f"L={L}")
    for i, k in enumerate(arms):
        cont = b[f"L24|{k}"]["ITT_TRACK_CONTINUITY"].split("/")[0]
        c32 = b[f"L32|{k}"]["ITT_TRACK_CONTINUITY"].split("/")[0]
        col = INK if cont == "9" and c32 == "9" else C[1]
        a.text(i, 0.44, f"{cont}/9\n{c32}/9", ha="center", fontsize=7.5, color=col,
               weight="bold" if col == INK else "normal")
    a.text(-0.55, 0.455, "continuite ITT\nL24 / L32", fontsize=6.5, color=INK2, ha="left")
    a.set_xticks(x)
    a.set_xticklabels(arms, fontsize=8, rotation=15)
    a.set_ylim(0.10, 0.52)
    a.set_ylabel("UNIQUE_CAUSAL_REPLACEMENT")
    a.set_title("08B · la regle de quantite : aucune garde n'ameliore,\n"
                "et le plancher fait SCISSIONNER 9/9")

    a = ax[1]
    fa = ["SAFE_FIXED_SCHEDULE", "SAFE_ONLINE_TRIGGER", "SAFE_DONOR_YOKED_REPLAY",
          "SAFE_LAGGED_SENSOR"]
    xx = np.arange(len(fa))
    for j, L in enumerate(("24", "32")):
        v = [c[f"L{L}|{k}"]["UCR_median"] for k in fa]
        lo = [c[f"L{L}|{k}"]["UCR_ci"][0] for k in fa]
        hi = [c[f"L{L}|{k}"]["UCR_ci"][1] for k in fa]
        a.errorbar(xx + (j - 0.5) * 0.16, v, yerr=[np.array(v) - lo, np.array(hi) - v],
                   color=C[j], marker="o", ls="none", capsize=3, label=f"L={L}")
    a.set_xticks(xx)
    a.set_xticklabels(["FIXE", "EN LIGNE", "DONNEUR\nASSERVI", "CAPTEUR\nRETARDE"],
                      fontsize=7.5)
    a.set_ylabel("UNIQUE_CAUSAL_REPLACEMENT")
    a.set_title("08C · le calendrier : en ligne = donneur asservi\n"
                "(p = 0,51 et 1,00) -> aucune information en ligne")
    a.legend(fontsize=8)

    a = ax[2]
    for j, L in enumerate(("24", "32")):
        dl, uc, lab = [], [], []
        for k in arms:
            dl.append(b[f"L{L}|{k}"]["delivered_over_M256_median"])
            uc.append(b[f"L{L}|{k}"]["UCR_median"])
            lab.append(k)
        for k in fa[1:]:
            dl.append(c[f"L{L}|{k}"]["delivered_over_M256"])
            uc.append(c[f"L{L}|{k}"]["UCR_median"])
            lab.append(k)
        a.scatter(dl, uc, color=C[j], s=38, marker="o" if j == 0 else "s", zorder=3,
                  label=f"L={L}")
        if j == 0:
            off = {"SAFE_DONOR_YOKED_REPLAY": (4, 8), "SAFE_LAGGED_SENSOR": (4, -10),
                   "SAFE_ONLINE_TRIGGER": (-46, -2)}
            for xx_, yy, ll in zip(dl, uc, lab):
                a.annotate(ll.replace("SAFE_", "").replace("_", " ").lower(), (xx_, yy),
                           fontsize=6, color=INK2, xytext=off.get(ll, (4, -3)),
                           textcoords="offset points")
    a.set_xlabel(r"masse delivree / $M_{256}$")
    a.set_ylabel("UNIQUE_CAUSAL_REPLACEMENT")
    a.set_title("la frontiere : plus on delivre, plus on remplace —\n"
                "aucune politique ne sort du faisceau")
    a.legend(fontsize=8)
    fig.suptitle("PROGRAM_08 · ni l'allocation sure ni le feedback local ne deplacent la "
                 "frontiere sous LAW_16", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p08_fig2_policies.png", dpi=160)
    plt.close(fig)


# ================================================ fig 3 : confirmation and LAW_29 transport
def fig3():
    p = Path("p08d_rows.csv")
    if not p.exists():
        return
    rows = rd(p)
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.2))
    keys = [("LAW_16", "24"), ("LAW_16", "32"), ("LAW_29", "24"), ("LAW_29", "32")]
    lab = [f"{l.replace('LAW_','L')}\nL={s}" for l, s in keys]
    x = np.arange(len(keys))

    a = ax[0]
    for i, (arm, cc) in enumerate((("PARENT", C[0]), ("SINK_FLOOR", C[1]),
                                   ("SRC_CAP", C[2]))):
        v = [med([n(r["UCR"]) for r in rows if r["law"] == l and r["size"] == s
                  and r["arm"] == arm]) for l, s in keys]
        a.bar(x + (i - 1) * 0.26, [0 if q is None else q for q in v], 0.24, color=cc,
              label=arm, edgecolor=SURF)
    a.set_xticks(x)
    a.set_xticklabels(lab, fontsize=7.5)
    a.set_ylabel("UNIQUE_CAUSAL_REPLACEMENT")
    a.set_title("C3 · sous LAW_16 aucune garde ne bat PARENT ;\nsous LAW_29 PARENT vaut 0",
                fontsize=9.5)
    a.legend(fontsize=7.5)

    a = ax[1]
    for i, (arm, cc) in enumerate((("PARENT", C[0]), ("SINK_FLOOR", C[1]),
                                   ("SRC_CAP", C[2]))):
        v = []
        for l, s in keys:
            g = [r for r in rows if r["law"] == l and r["size"] == s and r["arm"] == arm]
            v.append(sum(1 for r in g if r["split"] == "True") / max(1, len(g)))
        a.bar(x + (i - 1) * 0.26, v, 0.24, color=cc, label=arm, edgecolor=SURF)
    a.axhline(7 / 9, color=INK2, ls="--", lw=1.0)
    a.text(0.02, 7 / 9 + 0.02, "seuil predit scelle 7/9", fontsize=7, color=INK2,
           transform=a.get_yaxis_transform())
    a.set_xticks(x)
    a.set_xticklabels(lab, fontsize=7.5)
    a.set_ylim(0, 1.05)
    a.set_ylabel("fraction de blocs avec SCISSION")
    a.set_title("C1 · le plancher scinde le composant\n(LAW_16 seulement)", fontsize=9.5)
    a.legend(fontsize=7.5)

    a = ax[2]
    e = Path("p08e_rows.csv")
    if e.exists():
        er = rd(e)
        xs = np.arange(2)
        for i, (arm, cc) in enumerate((("PARENT", C[0]), ("SINK_FLOOR", C[1]))):
            cont, ucr, sh = [], [], []
            for sz in ("24", "32"):
                g = [r for r in er if r["size"] == sz and r["arm"] == arm]
                cont.append(sum(1 for r in g if r["same_track_continuous"] == "True")
                            / max(1, len(g)))
                ucr.append(med([n(r["UCR"]) for r in g]) or 0)
                sh.append(sum(1 for r in g if r.get("terminal_shadow_55_alive") == "True")
                          / max(1, len(g)))
            a.bar(xs + (i - 0.5) * 0.32, cont, 0.30, color=cc, label=arm, edgecolor=SURF)
            for j, (cv, uv, sv) in enumerate(zip(cont, ucr, sh)):
                a.text(j + (i - 0.5) * 0.32, cv + 0.03,
                       f"UCR {uv:.2f}\nombre 0,55\n{sv*9:.0f}/9", ha="center", fontsize=6,
                       color=INK2)
        a.set_xticks(xs)
        a.set_xticklabels(["LAW_29 L=24", "LAW_29 L=32"], fontsize=8)
        a.set_ylim(0, 1.35)
        a.set_ylabel("continuite ITT (fraction des 9 blocs)")
        a.set_title("08E · renversement confirme\nsous LAW_29 : 0/9 -> 9/9",
                    fontsize=9.5)
        a.legend(fontsize=7.5, loc="upper center")
        fig.suptitle("PROGRAM_08 · confirmation prospective, transport LAW_29, et le "
                     "renversement de signe de la garde de securite", fontsize=11)
        fig.tight_layout(rect=(0, 0, 1, 0.9))
        fig.savefig("p08_fig3_confirmation.png", dpi=160)
        plt.close(fig)
        return
    arms29 = ["PARENT", "ONLINE_STRICT", "ONLINE_NORMALIZED"]
    k29 = [("LAW_29", "24"), ("LAW_29", "32")]
    xx = np.arange(len(k29))
    for i, (arm, cc) in enumerate(zip(arms29, (C[0], C[3], C[5]))):
        cont, ucr = [], []
        for l, s in k29:
            g = [r for r in rows if r["law"] == l and r["size"] == s and r["arm"] == arm]
            cont.append(sum(1 for r in g if r["same_track_continuous"] == "True")
                        / max(1, len(g)))
            ucr.append(med([n(r["UCR"]) for r in g]) or 0)
        a.bar(xx + (i - 1) * 0.26, cont, 0.24, color=cc, label=arm, edgecolor=SURF)
        for j, (cv, uv) in enumerate(zip(cont, ucr)):
            a.text(j + (i - 1) * 0.26, cv + 0.02, f"UCR\n{uv:.2f}", ha="center", fontsize=6,
                   color=INK2)
    a.set_xticks(xx)
    a.set_xticklabels(["LAW_29 L=24", "LAW_29 L=32"], fontsize=8)
    a.set_ylim(0, 1.15)
    a.set_ylabel("continuite ITT (fraction des 9 blocs)")
    a.set_title("transport LAW_29 : strict et normalise")
    a.legend(fontsize=7.5)
    fig.suptitle("PROGRAM_08 · confirmation prospective sur graines jamais utilisees, "
                 "et les deux transports vers LAW_29", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p08_fig3_confirmation.png", dpi=160)
    plt.close(fig)


for f in (fig1, fig2, fig3):
    try:
        f()
        print("ok", f.__name__)
    except Exception:
        import traceback
        traceback.print_exc()

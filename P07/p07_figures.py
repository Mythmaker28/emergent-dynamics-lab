"""PROGRAM_07 figures."""
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
                     "axes.edgecolor": GRID, "axes.labelcolor": INK,
                     "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
                     "grid.color": GRID, "font.size": 9, "axes.titlesize": 10,
                     "axes.grid": True, "grid.linewidth": 0.6, "axes.linewidth": 0.8,
                     "legend.frameon": False})


def num(v):
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


# ============================================================== figure 1
def fig1():
    ev = rd("p07a_event_ledger.csv")
    by = defaultdict(lambda: defaultdict(list))
    for r in ev:
        c = num(r.get("CAP_PARENT"))
        if c is None:
            continue
        by[(r["arm"], r["size"])][r["block"]].append(
            (int(r["time"]), c, num(r.get("MASK_REGISTRATION")), num(r.get("CAP_TRACKALL")),
             num(r.get("source_capacity")), num(r.get("realized_sink"))))
    fig, ax = plt.subplots(2, 3, figsize=(13.4, 7.2))
    series = [("SHAM", C[0], "SHAM (aucun operateur)"),
              ("PARENT_Q800_UNIFORM", C[1], "forcage")]
    panels = [("capacite eligible du puits", 1),
              ("enregistrement du masque", 2),
              ("matiere retirable dans TOUT le composant", 3)]
    for col, (title, idx) in enumerate(panels):
        a = ax[0][col]
        for arm, cc, lab in series:
            d = by.get((arm, "24"))
            if not d:
                continue
            n = min(len(v) for v in d.values())
            xs = list(range(n))
            a.plot(xs, [med([sorted(v)[i][idx] for v in d.values()]) for i in xs],
                   color=cc, lw=1.7, label=lab if col == 0 else None)
        a.set_title(f"L=24 · {title}", fontsize=9.5)
        a.set_xlabel("indice d'evenement")
    ax[0][0].set_ylabel("$CAP_{PARENT}$")
    ax[0][1].set_ylabel(r"$|masque \cap C_t|\,/\,|masque|$")
    ax[0][1].set_ylim(-0.05, 1.05)
    ax[0][2].set_ylabel("$CAP_{TRACKALL}$")
    ax[0][2].set_ylim(0, None)
    ax[0][0].legend(fontsize=8, loc="center right")
    ax[0][0].text(0.30, 0.55, "les courbes forcees s'arretent a l'evenement ou le\n"
                  "dernier bloc perd encore sa piste : 9 blocs ITT, aucun\n"
                  "survivant presente comme la cohorte complete",
                  fontsize=6.5, color=INK2, transform=ax[0][0].transAxes)
    ax[0][2].text(0.03, 0.08, "le composant n'est JAMAIS epuise :\nil garde 97 % de sa matiere "
                  "retirable", fontsize=7.5, color=INK2, transform=ax[0][2].transAxes)

    a = ax[1][0]
    d = by.get(("PARENT_Q800_UNIFORM", "24"))
    n = min(len(v) for v in d.values())
    xs = list(range(n))
    a.plot(xs, [med([sorted(v)[i][4] for v in d.values()]) for i in xs], color=C[1], lw=1.7,
           label=r"place libre en amont  $\Sigma(M_{max}-m)$")
    a.plot(xs, [med([sorted(v)[i][5] for v in d.values()]) for i in xs], color=C[5], lw=1.2,
           label="masse effectivement delivree")
    q = med([num(r["planned"]) for r in ev if r["size"] == "24"])
    a.axhline(q, color=INK2, lw=1.0, ls=":", label="quantum planifie")
    a.set_yscale("log")
    a.set_title("L=24 · la SOURCE sature en ~13 evenements", fontsize=9.5)
    a.set_xlabel("indice d'evenement")
    a.set_ylabel("masse (echelle log)")
    a.legend(fontsize=7.5, loc="lower left")

    a = ax[1][1]
    b = json.load(open("p07b_summary.json"))["WHAT_BINDS_EACH_EXECUTED_EVENT"]
    arms = ["PARENT", "COMOVING", "TRACKALL", "MULTISITE", "UNTRACKED", "SRC_DISPERSED",
            "SRC_SINKSIDE"]
    w = 0.4
    for j, L in enumerate(("24", "32")):
        base = np.zeros(len(arms))
        for k, cc in (("PLANNED", C[2]), ("SOURCE", C[1]), ("SINK", C[0])):
            v = np.array([(b.get(f"L{L}|{a_}", {}).get(k, 0)
                           / max(1, b.get(f"L{L}|{a_}", {}).get("n_executed", 1)))
                          for a_ in arms])
            a.bar(np.arange(len(arms)) + (j - 0.5) * w, v, w * 0.9, bottom=base, color=cc,
                  label=k if j == 0 else None, edgecolor=SURF, lw=0.5)
            base += v
    a.set_xticks(range(len(arms)))
    a.set_xticklabels([x.replace("SRC_", "") for x in arms], rotation=32, ha="right",
                      fontsize=7.5)
    a.set_title("qui borne l'evenement execute\n(L=24 a gauche, L=32 a droite de chaque paire)",
                fontsize=9.5)
    a.set_ylim(0, 1)
    a.legend(fontsize=7.5, ncol=3, loc="lower center")

    a = ax[1][2]
    rows = {}
    for r in rd("p07b_rows.csv"):
        rows[(r["block"], r["arm"])] = r
    for r in rd("p07a_rows.csv"):
        if r["arm"] == "PARENT_Q400_UNIFORM":
            rows[(r["block"], "PARENT")] = r
    order = ["SRC_SINKSIDE", "TRACKALL", "COMOVING", "PARENT", "UNTRACKED",
             "SRC_DISPERSED", "MULTISITE"]
    y = np.arange(len(order))
    dl, ic, cont = [], [], []
    for a_ in order:
        g = [v for (bb, x), v in rows.items() if x == a_ and bb.startswith("L24_")]
        dl.append(med([num(v["realized_sink"]) / num(v["M256"]) for v in g]))
        ic.append(med([num(v["incumbent_removed_total"]) / num(v["M256"]) for v in g]))
        cont.append(sum(1 for v in g if v.get("same_track_continuous") == "True"))
    a.barh(y + 0.19, dl, 0.36, color=C[4], label="masse delivree / $M_{256}$")
    a.barh(y - 0.19, ic, 0.36, color=C[2], label="INCUMBENT retire / $M_{256}$")
    for i, (d_, c_) in enumerate(zip(dl, cont)):
        a.text(d_ + 0.08, i + 0.19, f"{d_:.2f}", va="center", fontsize=7, color=INK2)
        a.text(5.35, i, f"{c_}/9", va="center", ha="center", fontsize=7.5,
               color=INK if c_ == 9 else C[1], weight="bold" if c_ == 9 else "normal")
    a.text(5.35, len(order) - 0.35, "ITT", fontsize=7, color=INK2, va="bottom", ha="center")
    a.set_yticks(y)
    a.set_yticklabels([x.replace("SRC_", "") for x in order], fontsize=8)
    a.set_xlim(0, 5.8)
    a.set_xlabel(r"fraction de $M_{256}$")
    a.set_title("L=24 · delivrer plus n'est pas echanger plus", fontsize=9.5)
    a.legend(fontsize=7.5, loc="center right", bbox_to_anchor=(1.0, 0.32))

    fig.suptitle("PROGRAM_07 · le plafond de flux est une saturation CONJUGUEE : la source se "
                 "remplit, le puits se deregistre, le composant reste plein", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    fig.savefig("p07_fig1_mecanisme.png", dpi=160)
    plt.close(fig)


# ============================================================== figure 2
def fig2():
    rows = rd("p07c_cadence_rows.csv")
    conf = Path("p07d_cadence_rows.csv")
    pred = json.load(open("p07d_protocol.json"))["SEALED_POINT_PREDICTIONS"][
        "P1_CADENCE_SATURATION_LAW"]
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.0))
    for j, L in enumerate(("24", "32")):
        a = ax[j]
        for pi, pl in enumerate(("INTERFACE", "DISPERSED")):
            ss, ph, lo, hi = [], [], [], []
            for s in (1, 4, 16, 64):
                g = [num(r["PHI_per_step"]) for r in rows
                     if r["placement"] == pl and r["size"] == L and int(r["spacing"]) == s]
                if not g:
                    continue
                ss.append(s)
                ph.append(S.median(g))
                lo.append(min(g))
                hi.append(max(g))
            a.errorbar(ss, ph, yerr=[np.array(ph) - lo, np.array(hi) - ph], color=C[pi],
                       marker="o", lw=1.6, capsize=3, label=f"{pl} (decouverte)")
            if pl == "INTERFACE":
                rho = pred["rho_from_discovery_only"][f"L{L}"]
                q = med([num(r["quantum"]) for r in rows if r["size"] == L])
                xs = np.logspace(0, 2.2, 60)
                a.plot(xs, np.minimum(q / xs, rho), color=INK2, lw=1.0, ls="--",
                       label=r"loi $\min(q/s,\ \rho)$")
        if conf.exists():
            cr = rd(conf)
            ss, ph = [], []
            for s in (2, 8, 32, 128):
                g = [num(r["PHI_per_step"]) for r in cr
                     if r["size"] == L and int(r["spacing"]) == s]
                if g:
                    ss.append(s)
                    ph.append(S.median(g))
            a.plot(ss, ph, color=C[3], marker="D", ls="none", ms=7,
                   label="confirmation, graines neuves")
            pp = pred["predicted_Phi"][f"L{L}"]
            a.plot([int(k) for k in pp], [pp[k] for k in pp], color=C[5], marker="_",
                   ls="none", ms=14, mew=2, label="prediction scellee")
        a.set_xscale("log")
        a.set_yscale("log")
        a.set_xlabel("espacement s (pas entre evenements)")
        a.set_ylabel(r"$\Phi$ = masse delivree par pas")
        a.set_title(f"L={L}")
        a.legend(fontsize=7)
    a = ax[2]
    for j, L in enumerate(("24", "32")):
        ss, df = [], []
        for s in (1, 4, 16, 64):
            g = [num(r["delivered_fraction"]) for r in rows
                 if r["placement"] == "INTERFACE" and r["size"] == L and int(r["spacing"]) == s]
            if g:
                ss.append(s)
                df.append(S.median(g))
        a.plot(ss, df, color=C[j], marker="o", lw=1.6, label=f"L={L}")
    a.set_xscale("log")
    a.set_xlabel("espacement s")
    a.set_ylabel("fraction de la dose PLANIFIEE delivree")
    a.set_title("la dose planifiee est presque sans effet sur le flux :\n"
                "seule sa fraction delivree change")
    a.legend(fontsize=8)
    fig.suptitle(r"PROGRAM_07 · loi de saturation : $\Phi(s)\simeq\rho$, "
                 r"independante de la cadence et de la dose jusqu'a $s^*=q/\rho$", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p07_fig2_cadence.png", dpi=160)
    plt.close(fig)


# ============================================================== figure 3
def fig3():
    p = Path("p07d_rows.csv")
    if not p.exists():
        return
    rows = rd(p)
    pred = json.load(open("p07d_protocol.json"))["SEALED_POINT_PREDICTIONS"]
    keys = sorted({(r["law"], r["size"]) for r in rows},
                  key=lambda k: (k[0], int(k[1])))
    fig, ax = plt.subplots(1, 3, figsize=(13.2, 4.0))
    lab = [f"{l.replace('LAW_','L')}\nL={s}" for l, s in keys]
    x = np.arange(len(keys))
    a = ax[0]
    for i, (arm, cc) in enumerate((("PARENT", C[0]), ("SRC_SINKSIDE", C[1]))):
        v, lo, hi = [], [], []
        for l, s in keys:
            g = [num(r["incumbent_removed_over_M256"]) for r in rows
                 if r["law"] == l and r["size"] == s and r["arm"] == arm]
            v.append(S.median(g) if g else np.nan)
            lo.append(min(g) if g else np.nan)
            hi.append(max(g) if g else np.nan)
        a.errorbar(x + (i - 0.5) * 0.14, v, yerr=[np.array(v) - lo, np.array(hi) - v],
                   color=cc, marker="o", ls="none", capsize=3, label=arm)
    a.axhspan(0.25, 0.60, color=C[2], alpha=0.13)
    a.text(0.02, 0.60, "bande predite scellee [0,25 ; 0,60]", fontsize=7, color=INK2,
           va="bottom", transform=a.get_yaxis_transform())
    a.set_xticks(x)
    a.set_xticklabels(lab, fontsize=7.5)
    a.set_ylabel(r"incumbent retire / $M_{256}$")
    a.set_title("P3 · echange borne : CONFIRME dans la bande,\nmais decroissant avec la taille",
                fontsize=9.5)
    a.legend(fontsize=8, loc="upper right")
    for i, (l, sz) in enumerate(keys):
        g = [r for r in rows if r["law"] == l and r["size"] == sz and r["arm"] == "PARENT"]
        c = sum(1 for r in g if r["same_track_continuous"] == "True")
        a.text(i, 0.655, f"{c}/9", ha="center", fontsize=8,
               color=INK if c == 9 else C[1], weight="bold")
    a.text(-0.7, 0.655, "continuite ITT\ndu bras PARENT :", ha="left", fontsize=7, color=INK2)
    a.set_ylim(0.05, 0.70)

    a = ax[1]
    for i, (arm, cc) in enumerate((("PARENT", C[0]), ("SRC_SINKSIDE", C[1]))):
        for j, k in enumerate(("DELIVERED_FRACTION", "REPLACEMENT_EFFICIENCY")):
            v = [med([num(r[k]) for r in rows if r["law"] == l and r["size"] == s
                      and r["arm"] == arm]) for l, s in keys]
            a.bar(x + (i - 0.5) * 0.36 + (j - 0.5) * 0.17, v, 0.16, color=cc,
                  alpha=1.0 if j == 0 else 0.45, edgecolor=SURF,
                  label=f"{arm} · {'delivre' if j == 0 else 'efficacite'}")
    a.set_xticks(x)
    a.set_xticklabels(lab, fontsize=7.5)
    a.set_title("P2 · SINKSIDE delivre tout et ne remplace rien")
    a.legend(fontsize=6.5, ncol=2)

    a = ax[2]
    v = []
    for l, s in keys:
        f = []
        for r in rows:
            if r["law"] == l and r["size"] == s and r["arm"] == "PARENT":
                b = json.loads(r["bound_by"])
                t = sum(b.values()) or 1
                f.append(b["SOURCE"] / t)
        v.append(S.median(f) if f else np.nan)
    a.bar(x, v, 0.5, color=C[1], edgecolor=SURF)
    a.axhline(0.70, color=INK2, ls="--", lw=1.0)
    a.text(0.02, 0.72, "seuil predit scelle 0,70", fontsize=7, color=INK2,
           transform=a.get_yaxis_transform())
    a.set_xticks(x)
    a.set_xticklabels(lab, fontsize=7.5)
    a.set_ylim(0, 1.05)
    a.set_title("P4 · REFUTE : la borne active depend de la LOI", fontsize=9.5)
    fig.suptitle("PROGRAM_07 · confirmation prospective sur graines neuves, "
                 "troisieme taille et seconde loi", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig("p07_fig3_confirmation.png", dpi=160)
    plt.close(fig)


for f in (fig1, fig2, fig3):
    try:
        f()
        print("ok", f.__name__)
    except Exception as e:
        import traceback
        traceback.print_exc()

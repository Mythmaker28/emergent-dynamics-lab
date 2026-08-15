"""OBFOR01 §27 — the mission figure."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402

OUT = "/home/claude/OBFOR01/out"
C = {"pred": "#2ca02c", "obs": "#1f77b4", "bad": "#d62728", "sub": "#ff7f0e",
     "grey": "#7f7f7f", "dark": "#1a1a1a"}


def main():
    res = json.load(open(f"{OUT}/_residual.json"))
    m6 = json.load(open(f"{OUT}/_m6.json"))
    adj = json.load(open(f"{OUT}/_adjudication.json"))
    mech = json.load(open(f"{OUT}/_mechanisms.json"))

    fig, ax = plt.subplots(2, 3, figsize=(19.5, 10.6))

    # ---------------------------------------------------- (a) median versus mean
    a = ax[0, 0]
    labels = ["statique", "mobile"]
    med = [res["RESIDUALS"]["STATIC_median_summary"]["residual_percent"],
           res["RESIDUALS"]["MOBILE_median_summary_OBDI02_all_L"]["residual_percent"]]
    mea = [res["RESIDUALS"]["STATIC_mean_summary"]["residual_percent"],
           res["RESIDUALS"]["MOBILE_mean_summary_OBDI02_all_L"]["residual_percent"]]
    m2 = [res["RESIDUALS"]["STATIC_M2"]["residual_percent"],
          res["RESIDUALS"]["MOBILE_M2_OBDI02_all_L"]["residual_percent"]]
    x = np.arange(2)
    a.bar(x - 0.26, med, 0.24, color=C["bad"], label=r"$r_{80}$, résumé MÉDIANE (règle gelée)")
    a.bar(x, mea, 0.24, color=C["obs"], label=r"$r_{80}$, résumé MOYENNE, mêmes trames")
    a.bar(x + 0.26, m2, 0.24, color=C["pred"], label=r"$M_2$, moyenne par particule")
    a.axhline(0, color=C["dark"], lw=1.2)
    a.set_xticks(x)
    a.set_xticklabels(labels)
    a.set_ylabel("résidu contre l'opérateur idéal, %")
    a.set_title("(a) le résidu appartient à la RÈGLE DE RÉSUMÉ\n"
                "mêmes trames, mêmes nuages : seule la médiane décroche\n"
                "mobile $-5{,}10$ % en médiane contre $-0{,}70$ % en moyenne", fontsize=10)
    a.legend(fontsize=8)
    a.grid(alpha=.25, axis="y")

    # ---------------------------------------------------- (b) the whole radial profile
    b = ax[0, 1]
    cdf = res["RADIAL_CDF_MOBILE"]
    r = [c["r"] for c in cdf]
    b.plot(r, [c["predicted"] for c in cdf], "-", color=C["pred"], lw=2.6,
           label="opérateur idéal, forme close")
    b.plot(r, [c["observed"] for c in cdf], "o", color=C["obs"], ms=7,
           label="observé, 116 bras")
    b2 = b.twinx()
    b2.bar(r, [c["z"] for c in cdf], 0.35, color=C["grey"], alpha=.45)
    b2.set_ylabel("écart en unités d'erreur type", color=C["grey"])
    b2.set_ylim(-4, 4)
    b2.axhline(0, color=C["grey"], lw=0.8)
    b.set_xlabel("rayon torique depuis l'organisateur")
    b.set_ylabel("masse cumulée")
    b.set_title("(b) le profil RADIAL COMPLET est exact\n"
                r"max $|z| = %.2f$ sur 15 rayons ; écart maximal en probabilité 0,0038"
                % res["RADIAL_CDF_MOBILE_MAX_ABS_Z"], fontsize=10)
    b.legend(fontsize=8, loc="lower right")
    b.grid(alpha=.25)

    # ---------------------------------------------------- (c) the decomposition
    c = ax[0, 2]
    seq = m6["DECOMPOSITION"]["SEQUENTIAL"]
    steps = ["noyau discret\n+ tore + temps fini", "+ trajectoire\nde source partagée",
             "+ flux de naissance\nmesuré"]
    vals = [seq["step_0_baseline_M2_level"], seq["step_1_add_shared_trajectory"],
            seq["step_2_add_empirical_birth_flux"]]
    c.plot(range(3), vals, "o-", color=C["obs"], lw=2.6, ms=10)
    for i, v in enumerate(vals):
        c.annotate("%.2f %%" % v, (i, v), textcoords="offset points", xytext=(0, -18),
                   ha="center", fontsize=9)
    c.axhline(m6["OBSERVED"]["mobile_median"], ls="--", color=C["bad"], lw=2,
              label="observé (moteur, L=36) %.2f %%" % m6["OBSERVED"]["mobile_median"])
    fac = m6["DECOMPOSITION"]["FACTORIAL"]
    c.set_xticks(range(3))
    c.set_xticklabels(steps, fontsize=8.5)
    c.set_ylabel("résidu mobile en médiane, %")
    c.set_title("(c) décomposition séquentielle, et factorielle 2×2\n"
                "effets principaux : trajectoire %.2f, flux %.2f ; interaction %+.2f\n"
                "aucun mécanisme ne se voit créditer la totalité"
                % (fac["main_effect_shared_trajectory"], fac["main_effect_birth_flux"],
                   fac["interaction"]), fontsize=10)
    c.legend(fontsize=8.5)
    c.grid(alpha=.25)

    # ---------------------------------------------------- (d) the frozen endpoints
    d = ax[1, 0]
    E = adj["ENDPOINTS"]
    names = ["profil absolu\nstatique", "profil absolu\nmobile", "rapport\nmobile/statique"]
    keys = ["STATIC_ABSOLUTE_PROFILE_COMPATIBILITY", "MOBILE_ABSOLUTE_PROFILE_COMPATIBILITY",
            "MOBILE_STATIC_RATIO_COMPATIBILITY"]
    dev = [E[k]["relative_deviation_percent"] for k in keys]
    lo = [E[k]["ci95_relative_percent"][0] for k in keys]
    hi = [E[k]["ci95_relative_percent"][1] for k in keys]
    m = E[keys[0]]["margin_percent"]
    y = np.arange(3)
    d.axvspan(-m, m, color="#e8f4ea", label="marge d'équivalence gelée $\\pm$%.1f %%" % m)
    d.errorbar(dev, y, xerr=[np.array(dev) - np.array(lo), np.array(hi) - np.array(dev)],
               fmt="o", ms=11, lw=3, capsize=8, color=C["obs"])
    d.axvline(0, color=C["pred"], lw=1.8)
    d.set_yticks(y)
    d.set_yticklabels(names)
    d.set_xlabel("écart à la prédiction gelée, %")
    d.set_xlim(-4, 4)
    d.set_title("(d) 28 bras frais, prédictions gelées avant tout run\n"
                "écarts %+.2f %%, %+.2f %%, %+.2f %% — les trois passent"
                % tuple(dev), fontsize=10)
    d.legend(fontsize=8.5, loc="upper left")
    d.grid(alpha=.25, axis="x")

    # ---------------------------------------------------- (e) the ablation control
    e = ax[1, 1]
    ab = adj["ABLATION"]
    lab = ["modèle complet", "sans trajectoire\npartagée", "source de Poisson",
           "valeur idéale\nnon corrigée"]
    dist = [ab["distance_to_the_full_model"],
            ab["distance_to_the_model_without_the_shared_trajectory"],
            ab["distance_to_the_model_with_a_poisson_source"],
            abs(ab["observed_mobile_median"] - ab["predictions"]["ideal_population_value"])]
    cols = [C["pred"], C["bad"], C["sub"], C["grey"]]
    e.barh(np.arange(4), dist, color=cols, alpha=.9)
    for i, v in enumerate(dist):
        e.text(v + 0.008, i, "%.4f" % v, va="center", fontsize=9)
    e.set_yticks(np.arange(4))
    e.set_yticklabels(lab, fontsize=9)
    e.invert_yaxis()
    e.set_xlabel("distance à la médiane mobile observée")
    e.set_xlim(0, max(dist) * 1.25)
    e.set_title("(e) contrôle d'ablation : le modèle complet gagne\n"
                "retirer la trajectoire partagée coûte un facteur 15,\n"
                "ignorer l'estimateur un facteur 24", fontsize=10)
    e.grid(alpha=.25, axis="x")

    # ---------------------------------------------------- (f) the rival mechanisms
    f = ax[1, 2]
    rivals = [
        ("estimateur\n(règle de résumé)", abs(m6["OBSERVED"]["mobile_median"]), C["obs"]),
        ("continu → discret\n(modèle M0)",
         abs(mech["S11_TORUS_AND_LATTICE"]["mobile"][
             "CONTINUUM_TO_DISCRETE_CORRECTION_percent"]), C["sub"]),
        ("ordre intra-pas",
         mech["S9_INTRA_STEP_ORDER"]["MAGNITUDE_percent_on_r80"], C["grey"]),
        ("refus de capacité",
         mech["S12_CAPACITY"]["SHADOW_REPLAY_ANALYTIC"]["implied_change_in_r80_percent"],
         C["grey"]),
        ("tore fini", 0.005, C["grey"]),
    ]
    yy = np.arange(len(rivals))
    f.barh(yy, [r[1] for r in rivals], color=[r[2] for r in rivals], alpha=.9)
    for i, r in enumerate(rivals):
        f.text(r[1] * 1.15, i, "%.3g %%" % r[1], va="center", fontsize=9)
    f.set_yticks(yy)
    f.set_yticklabels([r[0] for r in rivals], fontsize=9)
    f.invert_yaxis()
    f.set_xscale("log")
    f.set_xlim(1e-3, 1e2)
    f.axvline(abs(m6["OBSERVED"]["mobile_median"]), ls="--", color=C["dark"], lw=1.4)
    f.set_xlabel(r"amplitude sur $r_{80}$, % (échelle logarithmique)")
    f.set_title("(f) les mécanismes rivaux, mis à l'échelle\n"
                "le continu se trompe de 19 %, mais il n'est pas le modèle utilisé ;\n"
                "capacité et ordre intra-pas sont sous le résidu de 2 à 3 décades",
                fontsize=10)
    f.grid(alpha=.25, axis="x", which="both")

    fig.suptitle("OBFOR01 — fermeture du résidu de l'opérateur source–transport–décroissance"
                 "   |   %s   |   28 runs frais" % adj["DISPOSITION"], fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(f"{OUT}/obfor01_operator_residual.png", dpi=145)
    print("wrote obfor01_operator_residual.png")


if __name__ == "__main__":
    main()

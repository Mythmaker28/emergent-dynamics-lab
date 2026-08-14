"""OBTR01 §28 — the mission figure."""
from __future__ import annotations

import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402

OUT = "/home/claude/OBTR01/out"
C = {"exact": "#1f77b4", "engine": "#d62728", "pred": "#2ca02c", "sub": "#ff7f0e",
     "grey": "#7f7f7f", "bad": "#d62728", "ok": "#1f77b4", "dark": "#1a1a1a"}


def main():
    ker = json.load(open(f"{OUT}/_kernels_operator.json"))
    obs = json.load(open(f"{OUT}/_observables.json"))
    tau = json.load(open(f"{OUT}/_timescales.json"))
    cap = json.load(open(f"{OUT}/_capacity.json"))
    hist = json.load(open(f"{OUT}/_historical_raw.json"))
    win = json.load(open(f"{OUT}/_window_rederivation.json"))
    frz = json.load(open(f"{OUT}/_freeze.json"))
    K = ker["KERNELS"]

    fig, ax = plt.subplots(2, 3, figsize=(19.5, 10.4))

    # ------------------------------------------------------- (a) the one-step law
    a = ax[0, 0]
    law = K["ONE_STEP_LAW"]
    eng = K["ENGINE_MONTE_CARLO"]["law"]
    keys = sorted(law, key=lambda s: (-law[s], s))
    xs = np.arange(len(keys))
    a.bar(xs - 0.2, [law[k] for k in keys], 0.4, color=C["exact"],
          label="exact, par énumération")
    a.bar(xs + 0.2, [eng.get(k, 0.0) for k in keys], 0.4, color=C["engine"], alpha=.85,
          label="moteur, 4000 tirages en mode TEST")
    a.set_yscale("log")
    a.set_xticks(xs)
    a.set_xticklabels([k.replace("(", "").replace(")", "").replace(" ", "") for k in keys],
                      fontsize=8, rotation=45)
    a.set_ylabel("probabilité d'un déplacement en un pas")
    mc = K["ENGINE_MONTE_CARLO"]
    msd = K["DIFFUSION_CONVENTION_TEST"]
    # the standard error implied by the recorded z against the corrected law, reused to place
    # the historical convention on the same scale
    se_msd = ((msd["msd_per_axis_measured"] - msd["msd_per_axis_predicted_a_t"])
              / msd["z_vs_corrected"])
    z_hist = ((msd["msd_per_axis_measured"]
               - msd["msd_per_axis_historical_p_hop_over_4_times_t"]) / se_msd)
    a.set_title("(a) la loi de déplacement exacte a un support DIAGONAL\n"
                "variation totale exacte/moteur %.5f contre 1 sigma par case %.5f\n"
                r"MSD/axe sur 400 pas : $a\,t$ à $z=%+.2f$, $(p_{hop}/4)\,t$ à $%.1f\,\sigma$"
                % (mc["total_variation_vs_exact"], mc["one_sigma_of_a_cell"],
                   msd["z_vs_corrected"], z_hist),
                fontsize=9.5)
    a.legend(fontsize=8)
    a.grid(alpha=.25, axis="y", which="both")

    # ------------------------------------------------------- (b) static vs mobile
    b = ax[0, 1]
    st = hist["STATIC_SOURCE"]
    ps, pm = st["PREDICTED_STATIC_r50_r80_r90"], st["PREDICTED_MOBILE_r50_r80_r90"]
    sv = st["OBSERVED"]["S_r80_organiser"]["values"]
    pv = st["OBSERVED"]["P_r80_organiser"]["values"]
    b.axhline(float(ps["0.8"]), color=C["pred"], ls="--", lw=1.8,
              label=r"prédit, source immobile  $a_{rel}=a_X$")
    b.axhline(float(pm["0.8"]), color=C["ok"], ls="--", lw=1.8,
              label=r"prédit, source mobile  $a_{rel}=a_X+a_Y$")
    b.plot(np.full(len(sv), 1) + np.linspace(-.12, .12, len(sv)), sv, "o", ms=9,
           color=C["pred"], label="observé, condition S (%d bras)" % len(sv))
    b.plot(np.full(len(pv), 2) + np.linspace(-.12, .12, len(pv)), pv, "s", ms=9,
           color=C["ok"], label="observé, condition P (%d bras)" % len(pv))
    d = st["DISCRIMINATION"]
    b.set_xticks([1, 2])
    b.set_xticklabels(["S : organisateur immobile", "P : organisateur mobile"])
    b.set_xlim(0.5, 2.5)
    b.set_ylabel(r"$r_{80}$ dans le repère de l'organisateur")
    b.set_title("(b) le noyau relatif tranche, sans paramètre ajusté\n"
                "rapport prédit %.4f, observé %.4f, IC 95 %% bootstrap [%.4f, %.4f]\n"
                "l'hypothèse « le mouvement de la source est sans effet » prédit 1,0000"
                % (st["PREDICTED_RATIO"], d["observed_ratio"],
                   d["bootstrap_95_interval"][0], d["bootstrap_95_interval"][1]),
                fontsize=9.5)
    b.legend(fontsize=8, loc="center left")
    b.grid(alpha=.25, axis="y")

    # ------------------------------------------------------- (c) population robustness
    c = ax[0, 2]
    agg = obs["DEMONSTRATION"]["AGGREGATE"]
    Ns = sorted(int(k) for k in agg["M2"] if agg["M2"][k])
    for key, lab, col, mk in (("M2", r"$M_2$ (moyenne par particule)", C["pred"], "^"),
                              ("W2_debiased", r"$W^2$ débiaisé exactement", C["ok"], "o"),
                              ("abs_C_minus_Y", r"$|C-Y|$  INTERDIT", C["bad"], "s"),
                              ("abs_m", r"$|m|$ (même vecteur, sa NORME)", C["sub"], "d")):
        v = [agg[key][str(n)]["ratio_of_means"] for n in Ns if agg[key].get(str(n))]
        c.plot(Ns[:len(v)], v, mk + "-", color=col, lw=2.2, ms=7, label=lab)
    c.axhline(1.0, ls="--", color=C["grey"], lw=1.3)
    c.set_xscale("log")
    c.set_xlabel("molécules conservées (sous-échantillonnage des champs RÉELS)")
    c.set_ylabel("rapport à la valeur pleine population")
    c.set_ylim(0.75, 1.55)
    c.set_title("(c) ce qui est robuste en population, et ce qui ne l'est pas\n"
                "%d bras réels, trois missions ; le défaut est la NORME, pas le centrage"
                % obs["DEMONSTRATION"]["arms_used"], fontsize=9.5)
    c.legend(fontsize=8, loc="upper right")
    c.grid(alpha=.25, which="both")

    # ------------------------------------------------------- (d) the timescale collapse
    d2 = ax[1, 0]
    units = tau["TIMESCALE_COLLAPSE"]["ALL_EIGHT_IN_UNITS_OF_ONE_OVER_mu"]
    names = [k for k in units if k != "TAU_SHAPE.TORUS_VARIANT"]
    vals = [units[k] for k in names]
    cols = [C["pred"] if v > 0.9 else C["ok"] for v in vals]
    y = np.arange(len(names))
    d2.barh(y, vals, color=cols, alpha=.85)
    d2.barh([len(names)], [units["TAU_SHAPE.TORUS_VARIANT"]], color=C["grey"], alpha=.7)
    d2.set_yticks(list(y) + [len(names)])
    d2.set_yticklabels([n.replace("TAU_", "") for n in names] + ["SHAPE.tore"], fontsize=8.5)
    d2.axvline(1.0, ls="--", color=C["dark"], lw=1.4)
    d2.axvline(0.5, ls=":", color=C["dark"], lw=1.2)
    d2.text(1.0, -0.9, r"$1/\mu_X$", ha="center", fontsize=9)
    d2.text(0.5, -0.9, r"$1/(2\mu_X)$", ha="center", fontsize=9)
    d2.set_xlabel(r"échelle de temps, en unités de $1/\mu_X$")
    d2.set_title("(d) sept des huit échelles sont des multiples RATIONNELS de "
                 r"$1/\mu_X$" "\n"
                 "les six pilotées par $\\mu_X$ ne s'écartent que de %.2f %% — "
                 "par construction\ndegrés de liberté temporels au point qualifié : %d"
                 % (100 * (tau["TIMESCALE_COLLAPSE"]["spread_max_over_min"] - 1),
                    tau["TIMESCALE_COLLAPSE"]["DEGREES_OF_FREEDOM_AS_TIMESCALES"]),
                 fontsize=9.5)
    d2.grid(alpha=.25, axis="x")

    # ------------------------------------------------------- (e) capacity refusal
    e = ax[1, 1]
    sp = cap["BY_SPECIES"]
    xs = np.arange(4)
    sps = ["X", "Y", "SX", "SY"]
    e.bar(xs, [sp[s]["mean"] for s in sps], 0.55, color=C["ok"], alpha=.85,
          yerr=[[0] * 4, [sp[s]["max"] - sp[s]["mean"] for s in sps]], capsize=6,
          label="moyenne sur 170 bras, barre = maximum")
    e.set_xticks(xs)
    e.set_xticklabels(sps)
    e.set_ylabel("fraction de sauts refusés par la capacité")
    bnd = cap["CERTIFIED_BOUND"]
    e.set_title("(e) le refus de capacité est minuscule et INDÉPENDANT du nuage\n"
                "pente log-log sur $N_X$ %+.3f ; L=36/72/96 sans tendance\n"
                r"borne certifiée : $\geq$ %.2f %% des molécules jamais refusées (pire bras)"
                % (cap["BY_POPULATION"]["log_log_slope_of_eps_on_N_X"],
                   100 * bnd["AT_THE_WORST_ARM"][
                       "fraction_of_molecules_certified_unblocked_lower_bound"]),
                fontsize=9.5)
    e.legend(fontsize=8)
    e.grid(alpha=.25, axis="y")

    # ------------------------------------------------------- (f) the window
    f = ax[1, 2]
    upper = float(win["SECTION_14"]["ANALYTICALLY_ADMISSIBLE_FAMILY"]
                  ["recomputed_inputs"]["binding_upper"])
    fam = float(win["SECTION_14"]["ANALYTICALLY_ADMISSIBLE_FAMILY"]["constraints"]
                ["with_the_declared_design_margins"].split("k_Y <= ")[1].split(" ")[0])
    f.axhspan(1e-9, upper, color="#e8f4ea", label="fenêtre, comme ENSEMBLE de taux $(0, %.3g)$"
                                                  % upper)
    f.axhline(upper, color=C["pred"], lw=2.0)
    f.plot([1], [1e-9], "v", ms=16, color=C["bad"], clip_on=False,
           label=r"bande atteignable au point qualifié : $\{0\}$")
    f.text(1, 3e-9, r"$R_Y \equiv 0$ exactement" "\n" r"(hors de l'axe log)", ha="center",
           fontsize=8.5, color=C["bad"])
    f.plot([2], [fam * 28], "o", ms=11, color=C["ok"],
           label="famille admissible, $k_Y Q_{max}$ (AUTRE LawSpec)")
    f.set_yscale("log")
    f.set_ylim(1e-9, 1e-2)
    f.set_xlim(0.4, 2.6)
    f.set_xticks([1, 2])
    f.set_xticklabels(["point qualifié\n$k_Y=0,\\ \\mu_Y=0$",
                       "famille analytiquement\nadmissible"])
    f.set_ylabel(r"taux de naissance de l'organisateur  $R_Y$")
    f.set_title("(f) la fenêtre n'échoue pas ici : son mécanisme est ABSENT\n"
                "l'ensemble est non vide, l'intersection avec l'atteignable est VIDE\n"
                "%s" % frz["DISPOSITION"], fontsize=9.5)
    f.legend(fontsize=8, loc="upper left")
    f.grid(alpha=.25, axis="y", which="both")

    fig.suptitle("OBTR01 — redérivation des échelles temporelles dans le LawSpec qualifié"
                 "   |   %s   |   runs scientifiques : 0"
                 % frz["DISPOSITION"], fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(f"{OUT}/obtr01_timescale_rederivation.png", dpi=145)
    print("wrote obtr01_timescale_rederivation.png")


if __name__ == "__main__":
    main()

"""OBDI02 §22 — the six mandatory figures."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt      # noqa: E402
import numpy as np                   # noqa: E402
import yaml                          # noqa: E402

OUT = "/home/claude/OBDI02/out"
CODE = "/home/claude/OBDI02/code"
C = {"data": "#1a1a1a", "ok": "#1f77b4", "bad": "#d62728", "pred": "#2ca02c",
     "sub": "#ff7f0e", "grey": "#7f7f7f"}


def main():
    spec = yaml.safe_load(open(f"{CODE}/obdi02_protocol.yaml"))
    R = json.load(open(f"{OUT}/_results.json"))
    A = json.load(open(f"{OUT}/_arms.json"))
    E = json.load(open(f"{OUT}/_evidence.json"))
    P, S, SEC = R["PRIMARY"], R["POPULATION_SUPPORT"], R["SECONDARY"]
    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    pred = spec["predictions"]
    LL = np.array(sizes, float)
    delta = float(P["equivalence_margin"])
    dm = float(P["STRINGENT_REFERENCE"]["margin"])

    fig, ax = plt.subplots(2, 3, figsize=(16.5, 9.4))

    # ---------------------------------------------------------------- (a) |C-Y| vs L
    a = ax[0, 0]
    for L in sizes:
        v = [x["summary"]["organiser_to_core"] for x in A if x["L"] == L
             and np.isfinite(x["summary"]["organiser_to_core"])]
        a.plot([L] * len(v), v, "o", ms=3.4, alpha=.35, color=C["data"], mfc="none")
    m = [P["per_L"][str(L)]["mean_of_summaries"] for L in sizes]
    se = [P["per_L"][str(L)]["se_of_log_mean"] * P["per_L"][str(L)]["mean_of_summaries"]
          for L in sizes]
    a.errorbar(sizes, m, yerr=np.array(se) * 1.6449, fmt="o-", color=C["ok"], lw=2.2, ms=8,
               capsize=5, label="moyenne des bras $\\pm$ 90 % IC")
    a.plot(sizes, [float(pred[str(L)]["organiser_to_core"]) for L in sizes], ":",
           color=C["pred"], lw=2, label="prédiction exacte de l'opérateur")
    a.set_xscale("log"); a.set_xticks(sizes); a.set_xticklabels(sizes)
    a.set_xlabel("taille de domaine $L$"); a.set_ylabel(r"$|C-Y|$  (cellules)")
    a.set_title("(a) distance cœur–organisateur contre $L$\n"
                "%d bras par taille, %d analysables"
                % (spec["domain"]["SEEDS_PER_SIZE"],
                   sum(v["n_analysable"] for v in P["per_L"].values())), fontsize=10)
    a.legend(fontsize=8); a.grid(alpha=.25, which="both")

    # ---------------------------------------------------------------- (b) the interval
    b = ax[0, 1]
    b.axvspan(-delta, delta, color="#e8f4ea", label="marge gelée $\\pm$%.2f" % delta)
    b.axvspan(-dm, dm, color="#cfe6d6", label="référence stringente $\\pm$%.3f" % dm)
    b.axvline(0, color=C["pred"], lw=1.5, label=r"$H_{bound}$ : $\beta=0$")
    b.axvline(0.5, color=C["sub"], ls="--", lw=1.3, label=r"$H_{sublinear}$")
    b.axvline(1.0, color=C["bad"], ls="--", lw=1.3, label=r"$H_{linear}$")
    lo, hi = P["interval"]
    b.errorbar([P["beta"]], [1.0], xerr=[[P["beta"] - lo], [hi - P["beta"]]], fmt="o", ms=10,
               lw=3, capsize=8, color=C["ok"] if P["PASS"] else C["bad"])
    b.text(P["beta"], 1.18, r"$\hat\beta_{CY}=%+.5f$" % P["beta"], ha="center", fontsize=10)
    b.text(P["beta"], 0.78, "IC 90 %% [%+.4f, %+.4f]\nborne atteinte %.4f"
           % (lo, hi, P["achieved_equivalence_bound"]), ha="center", fontsize=9)
    b.set_yticks([]); b.set_ylim(0.55, 1.45); b.set_xlim(-0.35, 1.12)
    b.set_xlabel(r"exposant d'échelle $\beta_{CY}$")
    b.set_title("(b) coefficient d'échelle et intervalle d'équivalence\n"
                "TOST, $\\alpha=0.05$ unilatéral  →  %s" % ("PASS" if P["PASS"] else "FAIL"),
                fontsize=10)
    b.legend(fontsize=7.5, loc="upper right"); b.grid(alpha=.25, axis="x")

    # ---------------------------------------------------------------- (c) Rg
    c = ax[0, 2]
    for stat, col, lab in (("Rg", C["ok"], "$R_g$"), ("r80", C["sub"], "$r_{80}$")):
        for L in sizes:
            v = [x["summary"][stat] for x in A if x["L"] == L
                 and np.isfinite(x["summary"][stat])]
            c.plot([L] * len(v), v, "o", ms=3, alpha=.28, color=col, mfc="none")
        mm = [SEC["scaling_" + stat]["per_L"][str(L)]["mean"] for L in sizes]
        c.plot(sizes, mm, "o-", color=col, lw=2, ms=7,
               label="%s  $\\beta=%+.4f$" % (lab, SEC["scaling_" + stat]["beta"]))
        c.plot(sizes, [float(pred[str(L)][stat]) for L in sizes], ":", color=C["pred"], lw=1.5)
    c.plot(LL, SEC["scaling_r80"]["per_L"]["36"]["mean"] * LL / 36, "--", color=C["bad"],
           lw=1.2, label=r"$H_{linear}$")
    c.set_xscale("log"); c.set_yscale("log")
    c.set_xticks(sizes); c.set_xticklabels(sizes)
    c.set_xlabel("taille de domaine $L$"); c.set_ylabel("rayon (cellules)")
    c.set_title("(c) $R_g$ et $r_{80}$ contre $L$\npointillé vert = prédiction exacte",
                fontsize=10)
    c.legend(fontsize=8); c.grid(alpha=.25, which="both")

    # ---------------------------------------------------------------- (d) density
    d = ax[1, 0]
    for L in sizes:
        v = [x["summary"]["density"] for x in A if x["L"] == L and x["summary"]["density"] > 0]
        d.plot([L] * len(v), v, "o", ms=3.4, alpha=.35, color=C["data"], mfc="none")
    dd = [SEC["density_exponent"]["per_L"][str(L)]["mean_density"] for L in sizes]
    d.plot(sizes, dd, "o-", color=C["ok"], lw=2.2, ms=8, label="moyenne des bras analysables")
    d0 = dd[0]
    d.plot(LL, d0 * (LL / 36) ** -2.0, ":", color=C["pred"], lw=2,
           label=r"$H_{bound}$ : $\rho\propto L^{-2}$")
    d.plot(LL, d0 * (LL / 36) ** -1.0, "--", color=C["sub"], lw=1.3,
           label=r"$H_{sublinear}$ : $L^{-1}$")
    d.plot(LL, d0 * np.ones_like(LL), "--", color=C["grey"], lw=1.3,
           label=r"$H_{fill}$ : constante")
    d.set_xscale("log"); d.set_yscale("log")
    d.set_xticks(sizes); d.set_xticklabels(sizes)
    d.set_xlabel("taille de domaine $L$"); d.set_ylabel(r"densité $N_X/L^2$")
    d.set_title(r"(d) densité contre $L$    $\hat\gamma=%+.4f\pm%.4f$"
                % (SEC["density_exponent"]["gamma"], SEC["density_exponent"]["se"]), fontsize=10)
    d.legend(fontsize=8); d.grid(alpha=.25, which="both")

    # ---------------------------------------------------------------- (e) winding
    e = ax[1, 1]
    w = SEC["true_winding"]["per_L"]
    fr = [w[str(L)]["fraction"] for L in sizes]
    e.bar([str(L) for L in sizes], [max(f, 3e-5) for f in fr], color=C["ok"], width=.5,
          label="observé")
    e.axhline(float(SEC["true_winding"]["tolerance"]), ls="--", color=C["bad"], lw=1.5,
              label="tolérance gelée 0.01")
    e.axhline(1.0, ls=":", color=C["grey"], lw=1.4, label=r"$H_{fill}$")
    for i, L in enumerate(sizes):
        e.text(i, 4e-5, "%d / %d trames" % (w[str(L)]["frames_with_winding"],
                                            w[str(L)]["frames"]), ha="center", va="bottom",
               fontsize=8)
    e.set_yscale("log"); e.set_ylim(2e-5, 3)
    e.set_xlabel("taille de domaine $L$")
    e.set_ylabel("fraction de trames enroulées")
    e.set_title("(e) winding véritable contre $L$", fontsize=10)
    e.legend(fontsize=8); e.grid(alpha=.25, axis="y", which="both")

    # ---------------------------------------------------------------- (f) support + legacy
    f = ax[1, 2]
    idx = np.arange(len(sizes))
    an = [S["per_L"][str(L)]["analysable"] for L in sizes]
    npl = int(spec["domain"]["SEEDS_PER_SIZE"])
    lg = [SEC["legacy_D_gate"]["per_L"][str(L)]["PASSING_ARMS"] for L in sizes]
    f.bar(idx - 0.19, an, width=.36, color=C["ok"], label="bras analysables")
    f.bar(idx + 0.19, lg, width=.36, color=C["grey"], label="bras passant le gate D hérité")
    f.axhline(S["required_per_size"], ls="--", color=C["bad"], lw=1.6,
              label="seuil de maintien %d/%d" % (S["required_per_size"], npl))
    f.axhline(npl, ls=":", color="#999999", lw=1.2, label="bras lancés %d" % npl)
    for i, L in enumerate(sizes):
        f.text(i - 0.19, an[i] + 0.6, "%d" % an[i], ha="center", fontsize=9)
        f.text(i + 0.19, lg[i] + 0.6, "%d" % lg[i], ha="center", fontsize=9)
    f.set_xticks(idx); f.set_xticklabels([str(L) for L in sizes])
    f.set_ylim(0, npl * 1.18)
    f.set_xlabel("taille de domaine $L$"); f.set_ylabel("nombre de bras")
    f.set_title("(f) maintien de population et endpoint historique\n"
                "extinctions : %s" % {str(L): R["extinctions_by_L"][str(L)] for L in sizes},
                fontsize=10)
    f.legend(fontsize=7.5, loc="lower right"); f.grid(alpha=.25, axis="y")

    fig.suptitle("OBDI02 — clôture de précision de l'attachement relatif   |   disposition : %s"
                 % E["DISPOSITION"], fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.963))
    fig.savefig(f"{OUT}/obdi02_precision_closure.png", dpi=150)
    print("wrote obdi02_precision_closure.png")


if __name__ == "__main__":
    main()

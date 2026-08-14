"""OBDCA01 — the adjudication figure."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt      # noqa: E402
import numpy as np                   # noqa: E402

OUT = "/home/claude/OBDCA01/out"
C = {"ok": "#1f77b4", "bad": "#d62728", "pred": "#2ca02c", "sub": "#ff7f0e", "grey": "#7f7f7f",
     "data": "#1a1a1a"}


def main():
    rec = json.load(open(f"{OUT}/_recompute.json"))
    cv = json.load(open(f"{OUT}/_construct_validity.json"))
    ad = json.load(open(f"{OUT}/_adjudication.json"))
    chk = ad["ALTERNATIVE_ESTIMANDS"]["RAW_ONLY_COMPARISON"]
    P = rec["PER_ARM"]
    t25, t042 = rec["TOST_AT_0P25"], rec["TOST_AT_0P042"]
    b, se = rec["BETA_CY"]["beta"], rec["BETA_CY"]["se"]

    fig, ax = plt.subplots(2, 2, figsize=(13.6, 9.2))

    # ---------------------------------------------------------------- (a) the two margins
    a = ax[0, 0]
    a.axvspan(-0.25, 0.25, color="#e8f4ea", label="marge gelée liante $\\pm$0,25")
    a.axvspan(-0.042, 0.042, color="#bcdcc6", label="référence secondaire $\\pm$0,042")
    a.axvline(0, color=C["pred"], lw=1.6, label=r"$\beta=0$")
    lo, hi = t25["interval"]
    a.errorbar([b], [1.0], xerr=[[b - lo], [hi - b]], fmt="o", ms=11, lw=3.2, capsize=9,
               color=C["ok"])
    a.text(b, 1.22, r"$\hat\beta_{CY}=%+.5f$" % b, ha="center", fontsize=11)
    a.text(b, 0.74, "IC 90 %% [%+.4f, %+.4f]\nTOST 0,25 : p = %.1e → PASS\n"
                    "TOST 0,042 : p = %.2f → FAIL"
           % (lo, hi, t25["tost_p_value"], t042["tost_p_value"]), ha="center", fontsize=9)
    a.set_yticks([]); a.set_ylim(0.5, 1.5); a.set_xlim(-0.30, 0.30)
    a.set_xlabel(r"exposant $\beta_{CY}$")
    a.set_title("(a) quelle marge liait réellement l'outcome primaire\n"
                "0,25 = champ equivalence_margin, gelé ; 0,042 = champ "
                "stringent_reference_margin,\n« reported, never decisive »", fontsize=10)
    a.legend(fontsize=8, loc="upper left"); a.grid(alpha=.25, axis="x")

    # ---------------------------------------------------------------- (b) N_X vs |C-Y|
    bx = ax[0, 1]
    mk = {36: "o", 72: "s", 96: "^"}
    for L in (36, 72, 96):
        v = [(p["N_X_mean"], p["summary_CY_route2"]) for p in P
             if p["L"] == L and p["N_X_mean"] > 0 and np.isfinite(p["summary_CY_route2"])]
        bx.plot([x for x, _ in v], [y for _, y in v], mk[L], ms=6, alpha=.7, mfc="none",
                label="$L=%d$" % L)
    cvd = cv["FINITE_CENTRE_ERROR"]["E_ABS_C_MINUS_Y_BY_N"]
    ns = sorted(int(k) for k in cvd)
    bx.plot(ns, [cvd[str(n)]["E_abs_C_minus_Y"] for n in ns], "-", color=C["bad"], lw=2.4,
            label="loi de Rice, erreur finie du centre")
    bx.set_xscale("log"); bx.set_yscale("log")
    bx.set_xlabel(r"population moyenne en fenêtre  $N_X$")
    bx.set_ylabel(r"$|C-Y|$ par graine")
    bx.set_title("(b) la métrique primaire est une fonction de la population\n"
                 r"$\mathrm{corr}(\log N_X,\ \log|C-Y|) = %.3f$"
                 % cv["CONDITIONAL_DIAGNOSTICS"]["corr_logN_log_offset"], fontsize=10)
    bx.legend(fontsize=8); bx.grid(alpha=.25, which="both")

    # ---------------------------------------------------------------- (c) the null
    c = ax[1, 0]
    null = cv["POPULATION_NULL"]
    rng = np.random.default_rng(0)
    # reconstruct a display sample from the recorded moments and quantiles
    q = null["null_quantiles"]
    xs = np.linspace(null["null_mean"] - 4 * null["null_sd"],
                     null["null_mean"] + 4 * null["null_sd"], 400)
    dens = np.exp(-0.5 * ((xs - null["null_mean"]) / null["null_sd"]) ** 2)
    dens /= dens.max()
    c.fill_between(xs, 0, dens, color=C["grey"], alpha=.35,
                   label="nul : mécanisme strictement invariant en $L$,\n"
                         "seules les populations observées sont injectées")
    for lab, val, col in ((r"$q_{95}$", q["0.95"] if "0.95" in q else q[0.95], C["sub"]),
                          (r"$q_{99}$", q["0.99"] if "0.99" in q else q[0.99], C["sub"])):
        c.axvline(val, ls=":", color=col, lw=1.4)
        c.text(val, 1.03, lab, ha="center", fontsize=8, color=col)
    c.axvline(null["null_mean"], ls="--", color=C["grey"], lw=1.4)
    c.axvline(b, color=C["bad"], lw=2.6, label=r"observé $\beta=%+.4f$" % b)
    c.set_xlabel(r"coefficient apparent $\beta_{CY}$")
    c.set_ylabel("densité (échelle relative)")
    c.set_ylim(0, 1.18)
    c.set_title("(c) l'effet observé est TYPIQUE d'un pur artefact de mesure\n"
                r"$P(\beta_{nul}\geq\beta_{obs}) = %.3f$  sur %d réplicats"
                % (null["P_beta_ge_observed"], null["replicates"]), fontsize=10)
    c.legend(fontsize=8, loc="upper right"); c.grid(alpha=.25)

    # ---------------------------------------------------------------- (d) downsampling
    d = ax[1, 1]
    ns2 = sorted(int(k) for k in chk["by_N"])
    d.plot(ns2, [chk["by_N"][str(n)]["abs_C_minus_Y_ratio"] for n in ns2], "o-", color=C["bad"],
           lw=2.2, ms=7, label=r"$|C-Y|$  (centre de Fréchet)")
    d.plot(ns2, [chk["by_N"][str(n)]["r80_Y_ratio"] for n in ns2], "s-", color=C["sub"], lw=2,
           ms=6, label=r"$r_{80,Y}$  (quantile source-centré)")
    d.plot(ns2, [chk["by_N"][str(n)]["mean_d2_ratio"] for n in ns2], "^-", color=C["pred"],
           lw=2.4, ms=7, label=r"moyenne par particule de $d_T(X_i,Y)^2$")
    d.axhline(1.0, ls="--", color=C["grey"], lw=1.3)
    d.set_xscale("log")
    d.set_xlabel("nombre de molécules conservées (sous-échantillonnage des champs RÉELS)")
    d.set_ylabel("rapport à la valeur pleine population")
    d.set_title("(d) sous-échantillonnage raw-only sur %d bras réels\n"
                "seule la moyenne par particule est structurellement non biaisée en $N$"
                % chk["arms"], fontsize=10)
    d.legend(fontsize=8.5); d.grid(alpha=.25, which="both")
    del rng

    fig.suptitle("OBDCA01 — adjudication du contrat de preuve   |   %s" % ad["DISPOSITION"],
                 fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    fig.savefig(f"{OUT}/obdca01_contract_audit.png", dpi=150)
    print("wrote obdca01_contract_audit.png")


if __name__ == "__main__":
    main()

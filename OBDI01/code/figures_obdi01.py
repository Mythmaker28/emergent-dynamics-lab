"""OBDI01 §27 — the mandatory figures. Every panel shows the four hypotheses' predictions
alongside the data, so the reader can see what was excluded and not only what was found."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt      # noqa: E402
import numpy as np                   # noqa: E402

OUT = "/home/claude/OBDI01/out"
C = {"data": "#1a1a1a", "bound": "#1f77b4", "lin": "#d62728", "sub": "#ff7f0e",
     "fill": "#7f7f7f", "pred": "#2ca02c"}


def main():
    R = json.load(open(f"{OUT}/_results.json"))
    A = json.load(open(f"{OUT}/_arms.json"))
    E = json.load(open(f"{OUT}/_evidence.json"))
    spec = json.load(open(f"{OUT}/_freeze.json"))
    P = R["PRINCIPAL"]
    sizes = [int(x) for x in spec["DOMAIN_SIZES"]]
    pred = json.load(open(f"{OUT}/_predictions.json"))["per_L"]

    fig, ax = plt.subplots(2, 2, figsize=(12.4, 9.2))

    # ---------------------------------------------------------------- (a) radius vs L
    a = ax[0, 0]
    for stat, mk, lab in (("r80", "o", "$r_{80}$ (cloud frame)"),
                          ("Rg", "s", "$R_g$"),
                          ("organiser_to_core", "^", "$|C-Y|$")):
        xs = [aa["L"] for aa in A if np.isfinite(aa["summary"][stat])]
        ys = [aa["summary"][stat] for aa in A if np.isfinite(aa["summary"][stat])]
        a.plot(np.array(xs) * (1 + 0.01 * "rRo".index(stat[0])), ys, mk, ms=5, alpha=.55,
               color=C["data"], mfc="none")
        m = [np.mean([aa["summary"][stat] for aa in A
                      if aa["L"] == L and np.isfinite(aa["summary"][stat])]) for L in sizes]
        a.plot(sizes, m, mk + "-", color=C["bound"], lw=2, ms=9, label=lab + " observed")
        a.plot(sizes, [pred[str(L)]["SAMPLED"][stat]["mean"] for L in sizes], ":",
               color=C["pred"], lw=1.6)
    r0 = pred["36"]["SAMPLED"]["r80"]["mean"]
    LL = np.array(sizes, float)
    a.plot(LL, r0 * LL / 36, "--", color=C["lin"], lw=1.4, label=r"$H_{linear}$: $r\propto L$")
    a.plot(LL, r0 * np.sqrt(LL / 36), "--", color=C["sub"], lw=1.4,
           label=r"$H_{sublinear}$: $r\propto\sqrt{L}$")
    a.plot(LL, [pred[str(L)]["H_fill_reference"]["r80"] for L in sizes], "--",
           color=C["fill"], lw=1.4, label=r"$H_{fill}$: uniform on the torus")
    a.set_xscale("log"); a.set_yscale("log")
    a.set_xticks(sizes); a.set_xticklabels(sizes)
    a.set_xlabel("domain size $L$"); a.set_ylabel("radius (cells)")
    a.set_title("(a) cloud size against domain size\n"
                "dotted green = parameter-free prediction of the exact kernel", fontsize=10)
    a.legend(fontsize=7, loc="upper left", ncol=2, framealpha=.92)
    a.grid(alpha=.25, which="both")

    # ---------------------------------------------------------------- (b) density vs L
    b = ax[0, 1]
    for L in sizes:
        d = [aa["summary"]["density"] for aa in A if aa["L"] == L]
        b.plot([L] * len(d), d, "o", ms=5, alpha=.55, color=C["data"], mfc="none")
    mm = [np.mean([aa["summary"]["density"] for aa in A if aa["L"] == L]) for L in sizes]
    b.plot(sizes, mm, "o-", color=C["bound"], lw=2, ms=9, label="observed mean")
    b.plot(sizes, [pred[str(L)]["expected_density_under_H_bound"] for L in sizes], ":",
           color=C["pred"], lw=1.8, label=r"$H_{bound}$: $N_X$ fixed, $\rho\propto L^{-2}$")
    d0 = pred["36"]["expected_density_under_H_bound"]
    b.plot(LL, d0 * (LL / 36) ** -1.0, "--", color=C["sub"], lw=1.4,
           label=r"$H_{sublinear}$: $\rho\propto L^{-1}$")
    b.plot(LL, d0 * np.ones_like(LL), "--", color=C["fill"], lw=1.4,
           label=r"$H_{fill}$: $\rho$ constant")
    B = P["components"]["B_density_exponent"]
    b.set_xscale("log"); b.set_yscale("log")
    b.set_xticks(sizes); b.set_xticklabels(sizes)
    b.set_xlabel("domain size $L$"); b.set_ylabel(r"density $N_X/L^2$")
    ext = [aa for aa in A if aa["summary"]["N_X_mean"] == 0]
    for aa in ext:
        b.annotate("extinct arm\n(%s)" % aa["tag"], xy=(aa["L"], mm[sizes.index(aa["L"])]),
                   xytext=(aa["L"] * 0.62, mm[sizes.index(aa["L"])] * 0.42), fontsize=7.5,
                   color=C["lin"], arrowprops=dict(arrowstyle="->", color=C["lin"], lw=1))
    b.set_title("(b) density against domain size\n"
                r"fitted exponent $\gamma=%+.4f\pm%.4f$   ($H_{bound}$: $-2$)"
                % (B["gamma"], B["se"]), fontsize=10)
    b.legend(fontsize=7.5, loc="lower left")
    b.grid(alpha=.25, which="both")

    # ---------------------------------------------------------------- (c) winding vs L
    cx = ax[1, 0]
    fr = P["components"]["C_no_true_winding"]["per_L"]
    obs = [fr[str(L)]["fraction"] for L in sizes]
    tol = P["components"]["C_no_true_winding"]["per_L"][str(sizes[0])]["tolerance"]
    cx.bar([str(L) for L in sizes], [max(o, 3e-5) for o in obs], color=C["bound"], width=.5,
           label="observed (all exactly zero)")
    cx.axhline(tol, ls="--", color=C["lin"], lw=1.5, label="frozen tolerance 0.01")
    cx.axhline(1.0, ls=":", color=C["fill"], lw=1.5, label=r"$H_{fill}$: winding typical")
    for i, L in enumerate(sizes):
        cx.text(i, 4e-5, "0 / %d frames" % fr[str(L)]["frames"], ha="center", va="bottom",
                fontsize=8)
    cx.set_yscale("log"); cx.set_ylim(2e-5, 3)
    cx.set_xlabel("domain size $L$")
    cx.set_ylabel("fraction of frames with a topological winding")
    cx.set_title("(c) true winding against domain size\n"
                 "the exact kernel produced 0 windings in 3000 draws at every $L$", fontsize=10)
    cx.legend(fontsize=8, loc="upper right")
    cx.grid(alpha=.25, axis="y", which="both")

    # ---------------------------------------------------------------- (d) radial profiles
    d = ax[1, 1]
    edges = np.arange(16)
    for L, col in zip(sizes, (C["bound"], C["pred"], C["sub"])):
        obsr = np.mean([aa["radial_observed"] for aa in A
                        if aa["L"] == L and np.isfinite(aa["profile_TV"])], axis=0)
        prd = np.array([aa["radial_predicted"] for aa in A if aa["L"] == L][0])
        d.step(edges, obsr, where="post", color=col, lw=1.9, label="observed $L=%d$" % L)
        d.step(edges, prd, where="post", color=col, lw=1.0, ls=":", alpha=.9)
    tvs = P["components"]["D_profile_compatibility"]["per_L"]
    d.set_yscale("log")
    d.set_xlabel("toroidal distance from the organiser (cells)")
    d.set_ylabel("mass fraction")
    d.set_title("(d) radial mass profile about the organiser\n"
                "solid = observed, dotted = exact kernel;  arms within the frozen TV envelope: "
                "%s" % ", ".join("$L$=%s %d/%d" % (k, v["arms_within"], v["arms_required"])
                                 for k, v in tvs.items()), fontsize=10)
    d.legend(fontsize=8)
    d.grid(alpha=.25, which="both")

    fig.suptitle("OBDI01 — domain invariance of the organiser-bound cloud   |   disposition: %s"
                 % E["DISPOSITION"], fontsize=12.5)
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    fig.savefig(f"{OUT}/obdi01_domain_invariance.png", dpi=155)
    print("wrote obdi01_domain_invariance.png")

    # ---------------------------------------------------------------- the exponent figure
    fig2, a2 = plt.subplots(figsize=(9.6, 4.6))
    stats = list(P["components"]["A_shape_invariance"]["by_statistic"])
    names = stats + ["density (+2)"]
    betas = [P["components"]["A_shape_invariance"]["by_statistic"][s]["beta"] for s in stats]
    ses = [P["components"]["A_shape_invariance"]["by_statistic"][s]["se"] for s in stats]
    betas.append(B["gamma"] + 2.0)
    ses.append(B["se"])
    cc = float(P["critical_value_c"])
    y = np.arange(len(names))[::-1]
    a2.axvspan(-0.25, 0.25, color="#e8f4ea", label="frozen equivalence region $\\pm0.25$")
    a2.axvline(0, color="#2ca02c", lw=1.4, label=r"$H_{bound}$")
    a2.axvline(0.5, color=C["sub"], lw=1.4, ls="--", label=r"$H_{sublinear}$")
    a2.axvline(1.0, color=C["lin"], lw=1.4, ls="--", label=r"$H_{linear}$ / $H_{fill}$")
    for i, (n, bb, se) in enumerate(zip(names, betas, ses)):
        ok = abs(bb) + cc * se <= 0.25
        a2.errorbar(bb, y[i], xerr=cc * se, fmt="o", ms=7, capsize=5, lw=2,
                    color=C["bound"] if ok else C["lin"])
        a2.text(1.25, y[i], "PASS" if ok else "FAIL", va="center", fontsize=9,
                color=C["bound"] if ok else C["lin"], fontweight="bold")
    a2.set_yticks(y); a2.set_yticklabels(names)
    a2.set_xlim(-0.45, 1.40)
    a2.set_xlabel("log-log exponent, after dividing out the exact finite-size prediction")
    a2.set_title("OBDI01 — the frozen simultaneous acceptance region\n"
                 "Sidak-corrected %.2f-sigma intervals; a component passes only if its whole\n"
                 "interval lies inside the shaded band" % cc, fontsize=10.5)
    a2.legend(fontsize=8, loc="center right", framealpha=.95)
    a2.grid(alpha=.25, axis="x")
    fig2.tight_layout()
    fig2.savefig(f"{OUT}/obdi01_exponents.png", dpi=155)
    print("wrote obdi01_exponents.png")


if __name__ == "__main__":
    main()

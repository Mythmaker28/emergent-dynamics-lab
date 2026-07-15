"""All manuscript figures/tables that display canonical numbers, generated ONLY from the pipeline results
dict (no hand-inscribed numbers). Imported by reproduction.primary. matplotlib Agg.

Figures: main longitudinal (h1+h2 vs M), h1 certification, h2 deep-turnover, gate-summary (claim) table.
Table: synthesis_table.tex (LaTeX booktabs fragment) + primary_table.csv (written by primary).
"""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THRESHOLD = 0.50
ORDER = ["init", "moderate", "deep-1", "deep"]
_PNG_META = {"Software": None}   # omit version/time chunks -> deterministic PNG bytes


def _series(per_ckpt, coord):
    M = [per_ckpt[k][coord]["meanM"] for k in ORDER]
    pt = [per_ckpt[k][coord]["point"] for k in ORDER]
    lo = [per_ckpt[k][coord]["ci_lo"] for k in ORDER]
    hi = [per_ckpt[k][coord]["ci_hi"] for k in ORDER]
    yerr = np.vstack([np.array(pt) - np.array(lo), np.array(hi) - np.array(pt)])
    return np.array(M), np.array(pt), yerr


def _panel(ax, per_ckpt, coord, title, color, shade_below=False):
    M, pt, yerr = _series(per_ckpt, coord)
    if shade_below:
        ax.axhspan(-1.2, THRESHOLD, color="#f2c2c2", alpha=0.35, zorder=0)
    ax.errorbar(M, pt, yerr=yerr, fmt="o-", color=color, lw=2, ms=7, capsize=5)
    ax.axhline(THRESHOLD, ls="--", color="0.4", lw=1.2)
    ax.text(0.60, THRESHOLD + 0.03, "0.50 qualification threshold", color="0.35", fontsize=8)
    ax.set_xlim(1.06, 0.10); ax.set_ylim(-1.2, 1.08)
    ax.set_xlabel("surviving original-material fraction $M$")
    ax.set_ylabel("held-out $R^2$")
    ax.set_title(title, fontsize=10.5)


def fig_longitudinal(per_ckpt, path):
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
    _panel(a, per_ckpt, "h1", "$h_1$ (cumulative dose): strongly decodable at deep turnover", "#1f6f3d")
    _panel(b, per_ckpt, "h2", "$h_2$ (temporal order): below threshold at deep turnover", "#b02418", shade_below=True)
    dh1 = per_ckpt["deep"]["h1"]; dh2 = per_ckpt["deep"]["h2"]
    a.annotate("deep: $R^2=%.2f$\n[%.2f, %.2f]" % (dh1["point"], dh1["ci_lo"], dh1["ci_hi"]),
               xy=(dh1["meanM"], dh1["point"]), xytext=(0.45, 0.30), fontsize=8.5, color="#154a29",
               arrowprops=dict(arrowstyle="->", color="#154a29"))
    b.annotate("deep: $R^2=%.2f$\n[%.2f, %.2f]" % (dh2["point"], dh2["ci_lo"], dh2["ci_hi"]),
               xy=(dh2["meanM"], dh2["point"]), xytext=(0.52, -0.70), fontsize=8.5, color="#7a1710",
               arrowprops=dict(arrowstyle="->", color="#7a1710"))
    fig.suptitle("Longitudinal certification (canonical reproducible pipeline)", fontsize=11, y=1.0)
    plt.tight_layout(); plt.savefig(path, dpi=150, bbox_inches="tight", metadata=_PNG_META); plt.close(fig)


def fig_h1_certification(per_ckpt, path):
    fig, ax = plt.subplots(figsize=(6, 4.2))
    _panel(ax, per_ckpt, "h1", "$h_1$ certification: retained through deep turnover", "#1f6f3d")
    d = per_ckpt["deep"]["h1"]
    ax.annotate("CERTIFIED\n$R^2=%.2f$ [%.2f, %.2f]\nlower bound $> 0.50$" % (d["point"], d["ci_lo"], d["ci_hi"]),
                xy=(d["meanM"], d["point"]), xytext=(0.5, 0.20), fontsize=9, color="#154a29",
                arrowprops=dict(arrowstyle="->", color="#154a29"))
    plt.tight_layout(); plt.savefig(path, dpi=150, bbox_inches="tight", metadata=_PNG_META); plt.close(fig)


def fig_h2_deepturnover(per_ckpt, path):
    fig, ax = plt.subplots(figsize=(6, 4.2))
    _panel(ax, per_ckpt, "h2", "$h_2$ deep turnover: not established (CI $\\leq 0.50$)", "#b02418", shade_below=True)
    d = per_ckpt["deep"]["h2"]
    ax.annotate("NOT ESTABLISHED\n$R^2=%.2f$ [%.2f, %.2f]" % (d["point"], d["ci_lo"], d["ci_hi"]),
                xy=(d["meanM"], d["point"]), xytext=(0.5, -0.75), fontsize=9, color="#7a1710",
                arrowprops=dict(arrowstyle="->", color="#7a1710"))
    plt.tight_layout(); plt.savefig(path, dpi=150, bbox_inches="tight", metadata=_PNG_META); plt.close(fig)


def fig_gate_summary(results, path):
    g = results["gates"]; deep = results["checkpoints"]["deep"]
    rows = [
        ["quantity", "h1 (cumulative dose)", "h2 (temporal order)"],
        ["deep-turnover held-out $R^2$", "%.2f" % deep["h1"]["point"], "%.2f" % deep["h2"]["point"]],
        ["95% CI", "[%.2f, %.2f]" % (deep["h1"]["ci_lo"], deep["h1"]["ci_hi"]),
                    "[%.2f, %.2f]" % (deep["h2"]["ci_lo"], deep["h2"]["ci_hi"])],
        ["vs 0.50 threshold", "CERTIFIED" if g["h1_deep_certified"] else "not certified",
                               "not established" if g["h2_deep_not_established"] else "certified"],
        ["track survival", "%d/%d" % (results["track_survival"]["survived"], results["track_survival"]["total"]), "(shared)"],
        ["reassignment switches", "%d" % results["track_survival"]["switches"], "(shared)"],
    ]
    fig, ax = plt.subplots(figsize=(9, 2.6)); ax.axis("off")
    ax.set_title("Canonical gate summary (from python -m reproduction.primary)", fontsize=11, fontweight="bold")
    colc = []
    for r, row in enumerate(rows):
        if r == 0: colc.append(["#d9d9d9"] * 3)
        else:
            cc = ["#eef2f6"]
            for cell in row[1:]:
                cc.append("#dff0e3" if cell in ("CERTIFIED",) else ("#f0dede" if "not " in cell else "white"))
            colc.append(cc)
    t = ax.table(cellText=rows, cellColours=colc, loc="center", cellLoc="center", bbox=[0, 0, 1, 0.86])
    t.auto_set_font_size(False); t.set_fontsize(9)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("white"); cell.set_linewidth(1.2)
        if r == 0 or c == 0: cell.set_text_props(fontweight="bold")
    plt.savefig(path, dpi=150, bbox_inches="tight", metadata=_PNG_META); plt.close(fig)


def synthesis_tex(results, path):
    pc = results["checkpoints"]
    lines = [r"\begin{tabular}{@{}lrrrr@{}}\toprule",
             r"checkpoint & mean $M$ & $h_1$ $R^2$ [95\% CI] & $h_2$ $R^2$ [95\% CI] & status\\\midrule"]
    labels = {"init": "initial", "moderate": "moderate", "deep-1": "deep$-$1", "deep": "deep"}
    for k in ORDER:
        h1 = pc[k]["h1"]; h2 = pc[k]["h2"]
        stat = "h1 certified / h2 n.e." if k == "deep" else ""
        lines.append(r"%s & %.2f & $%.2f$ [$%.2f,%.2f$] & $%.2f$ [$%.2f,%.2f$] & %s\\" % (
            labels[k], h1["meanM"], h1["point"], h1["ci_lo"], h1["ci_hi"],
            h2["point"], h2["ci_lo"], h2["ci_hi"], stat))
    surv = results["track_survival"]
    lines.append(r"\midrule \multicolumn{5}{@{}l}{track survival %d/%d, %d switches; decoder: grouped LOHO ridge $\lambda{=}1$, bootstrap $n{=}3000$ seed $20260715$}\\" % (
        surv["survived"], surv["total"], surv["switches"]))
    lines.append(r"\bottomrule\end{tabular}")
    open(path, "w").write("\n".join(lines) + "\n")


def make_all(per_ckpt, results, outdir):
    import os
    paths = {}
    paths["fig_longitudinal"] = os.path.join(outdir, "fig_longitudinal_v4.png")
    paths["fig_h1_certification"] = os.path.join(outdir, "fig_h1_certification_v4.png")
    paths["fig_h2_deepturnover"] = os.path.join(outdir, "fig_h2_deepturnover_v4.png")
    paths["fig_gate_summary"] = os.path.join(outdir, "fig_gate_summary_v4.png")
    paths["synthesis_tex"] = os.path.join(outdir, "synthesis_table.tex")
    fig_longitudinal(per_ckpt, paths["fig_longitudinal"])
    fig_h1_certification(per_ckpt, paths["fig_h1_certification"])
    fig_h2_deepturnover(per_ckpt, paths["fig_h2_deepturnover"])
    fig_gate_summary(results, paths["fig_gate_summary"])
    synthesis_tex(results, paths["synthesis_tex"])
    return paths

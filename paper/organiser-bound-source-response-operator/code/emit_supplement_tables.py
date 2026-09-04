#!/usr/bin/env python3
"""Generate the supplement's long tables as LaTeX, from the bound sources only."""
import json, os

OB = "/home/claude/OBFOR01/out"
PKG = "/home/claude/edl/paper/organiser-bound-source-response-operator"
J = {n: json.load(open(f"{OB}/{n}.json")) for n in
     ("_validation", "_freeze", "_adjudication", "_residual", "_m6", "_mechanisms")}
OUT = []

def esc(s):
    return str(s).replace("_", r"\_\allowbreak{}")

def hsplit(h, k=8):
    return r"\allowbreak{}".join(h[i:i + k] for i in range(0, len(h), k))

# ---- S4: the 28 arms ----
REG = {r["tag"]: r for r in J["_validation"]["START_REGISTER"]}
ARMS = J["_validation"]["ARMS"]
L = [r"\begin{longtable}{llrrrr}",
     r"\caption{The \freshArmsRun{} confirmation arms. Seeds come from a register that excludes "
     r"every seed appearing anywhere in the historical record. \emph{Final state hash} is the "
     r"SHA-256 of the full lattice state at the horizon, truncated here to 16 characters; the "
     r"untruncated values are in \texttt{\_validation.json}. No arm was rerun, replaced or "
     r"deleted.}\label{tab:arms}\\",
     r"\toprule",
     r"Tag & Final state hash & Seed & $r_{80}$ median & $N_X$ mean & Blocked fraction \\",
     r"\midrule \endfirsthead",
     r"\toprule Tag & Final state hash & Seed & $r_{80}$ median & $N_X$ mean & "
     r"Blocked fraction \\ \midrule \endhead",
     r"\bottomrule \endfoot"]
for a in ARMS:
    r = REG[a["tag"]]
    L.append(r"\texttt{%s} & \texttt{%s} & %d & %.4f & %.2f & %.2e \\" % (
        esc(a["tag"]), a["state_hash_final"][:16], r["seed"], a["r80_median"],
        a["N_X_window_mean"], a["blocked_fraction"]["X"]))
L.append(r"\end{longtable}")
OUT.append(("S4_arms", "\n".join(L)))

# ---- S1: methods core files ----
MC = J["_freeze"]["METHODS_CORE_FILES"]
L = [r"\begin{longtable}{ll}",
     r"\caption{The analysis modules hashed into \texttt{METHODS\_CORE} before any confirmation "
     r"arm ran, with their SHA-256 truncated to 16 characters. "
     r"\texttt{METHODS\_CORE\_MISSING} was empty.}\label{tab:methods}\\",
     r"\toprule File & SHA-256 (first 16) \\ \midrule \endfirsthead",
     r"\toprule File & SHA-256 (first 16) \\ \midrule \endhead",
     r"\bottomrule \endfoot"]
for k in sorted(MC):
    L.append(r"\texttt{%s} & \texttt{%s} \\" % (esc(k), MC[k][:16]))
L.append(r"\end{longtable}")
OUT.append(("S1_methods", "\n".join(L)))

# ---- S3: margin components ----
CO = J["_freeze"]["RESIDUAL_TOLERANCE"]["COMPONENTS"]
L = [r"\begin{center}", r"\small", r"\begin{tabular}{lr}", r"\toprule",
     r"Component & Value (\%) \\ \midrule"]
for k in ("M6_monte_carlo_se_static_percent", "M6_monte_carlo_se_mobile_percent",
          "capacity_certified_error_on_r80_percent", "intra_step_order_residual_percent",
          "historical_arm_to_arm_relative_sd_static_percent",
          "historical_arm_to_arm_relative_sd_mobile_percent",
          "sampling_se_at_14_arms_static_percent", "sampling_se_at_14_arms_mobile_percent"):
    L.append(r"\texttt{%s} & %.4f \\" % (esc(k), CO[k]))
L += [r"\midrule",
      r"model error, in quadrature & %.4f \\" % J["_freeze"]["RESIDUAL_TOLERANCE"]["model_error_quadrature_percent"],
      r"two sampling standard errors & %.4f \\" % J["_freeze"]["RESIDUAL_TOLERANCE"]["two_sampling_standard_errors_percent"],
      r"\textbf{declared margin} & \textbf{%.1f} \\" % J["_freeze"]["RESIDUAL_TOLERANCE"]["EQUIVALENCE_MARGIN_percent"],
      r"\bottomrule", r"\end{tabular}", r"\end{center}"]
OUT.append(("S3_margin", "\n".join(L)))

# ---- S6: radial profile, both conditions ----
L = [r"\begin{center}", r"\small", r"\begin{tabular}{rrrrrrrr}", r"\toprule",
     r"& \multicolumn{3}{c}{mobile (\radialProfileMobileArms{} arms)} & "
     r"& \multicolumn{3}{c}{static (\radialProfileStaticArms{} arms)} \\",
     r"\cmidrule(lr){2-4}\cmidrule(lr){6-8}",
     r"$r$ & predicted & observed & $z$ & & predicted & observed & $z$ \\ \midrule"]
for m, s in zip(J["_residual"]["RADIAL_CDF_MOBILE"], J["_residual"]["RADIAL_CDF_STATIC"]):
    L.append(r"%.1f & %.4f & %.4f & %+.3f & & %.4f & %.4f & %+.3f \\" % (
        m["r"], m["predicted"], m["observed"], m["z"], s["predicted"], s["observed"], s["z"]))
L += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
OUT.append(("S6_radial", "\n".join(L)))

# ---- S7: the six constructions ----
L = [r"\begin{center}", r"\small", r"\begin{tabular}{lrrrr}", r"\toprule",
     r"Construction & median & residual (\%) & mean residual (\%) & within-arm s.d. \\ \midrule"]
for m in J["_m6"]["MODELS"]:
    L.append(r"\texttt{%s} & %.4f & %+.4f & %+.4f & %.4f \\" % (
        esc(m["tag"]), m["median_summary"], m["median_residual_percent"],
        m["mean_residual_percent"], m["within_arm_sd"]))
L += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
OUT.append(("S7_models", "\n".join(L)))

os.makedirs(f"{PKG}/supplement", exist_ok=True)
for name, body in OUT:
    open(f"{PKG}/supplement/{name}.tex", "w", encoding="utf-8").write(body + "\n")
print("supplement tables:", [n for n, _ in OUT])

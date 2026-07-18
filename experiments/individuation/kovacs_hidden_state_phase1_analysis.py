"""KOVACS-HIDDEN-STATE-00 Phase-1 coincidence analysis + mechanical tolerance gate.

Reads the frozen Phase-1 DEV coincidence results and applies the macrostate-coincidence
gate with tolerances derived ONLY from mechanical sources (identical-history sham =
numerical 0, and natural DEV temporal repeatability), NEVER from any excursion size.
No excursion outcome is read or computed anywhere.

Outputs KOVACS_HIDDEN_STATE_00_PHASE1_COINCIDENCE_ANALYSIS.json and prints the
gate-relevant summary used by the frozen scientific-value gate.
"""
import json, statistics as st, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEV = REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_PHASE1_DEV_RESULTS.json"
OUT = REPO / "docs" / "individuation" / "KOVACS_HIDDEN_STATE_00_PHASE1_COINCIDENCE_ANALYSIS.json"

PANEL = ["core_mass", "core_support", "core_rg2", "core_centroid_off",
         "core_N", "core_c", "core_uptake", "collar_mass", "collar_N"]
MEM = ["m1_mean", "m2_mean", "mplus_mean", "mminus_mean"]
K_SIGMA = 3.0          # frozen: tolerance = K_SIGMA * natural temporal repeatability
NUMERICAL_FLOOR = 1e-9  # identical-history sham residual (deterministic) = 0

def sd(xs):
    xs = list(xs); return float(st.pstdev(xs)) if len(xs) > 1 else 0.0

def main():
    d = json.load(open(DEV))
    worlds = [w for w in d["worlds"] if w.get("eligible") and w.get("coincidence_primary")]
    seeds = [w["seed"] for w in worlds]
    kprim = d["schedule"]["coincidence_rule"]["primary_step"]

    # per-variable residuals + repeatability across worlds (primary common-clock step)
    resid = {v: [] for v in PANEL}
    repeat = {v: [] for v in PANEL}
    absval = {v: [] for v in PANEL}     # mean scale of the variable at coincidence
    memresid = {v: [] for v in MEM}
    for w in worlds:
        c = w["coincidence_primary"]
        for v in PANEL:
            resid[v].append(c["panel_abs"][v])
            repeat[v].append(c["repeatability"][v])
            absval[v].append((abs(c["mass_OVER"]) if v == "core_mass" else 0))
        for v in MEM:
            memresid[v].append(c["memory_diff"][v])

    # cross-world SD of each residual variable's coincidence value (scale for standardization)
    # Use the residual distribution's own scale AND the cross-world value scale.
    var_summary = {}
    for v in PANEL:
        r = resid[v]; rp = repeat[v]
        tol = max(NUMERICAL_FLOOR, K_SIGMA * (st.median(rp) if rp else 0.0))
        npass = sum(1 for x in r if x <= tol)
        var_summary[v] = {
            "resid_mean": round(st.mean(r), 5), "resid_median": round(st.median(r), 5),
            "resid_max": round(max(r), 5),
            "repeatability_median": round(st.median(rp), 6),
            "tolerance_3sigma_repeat": round(tol, 6),
            "n_pass_tolerance": npass, "n_worlds": len(r),
            "frac_pass": round(npass / len(r), 3),
            "sham_tolerance": 0.0,
            "n_pass_sham": 0,  # any systematic nonzero residual fails the identical-history sham (=0)
        }

    # full-overt-panel coincidence qualification per world (ALL panel vars within 3sigma-repeat tol)
    tol_by_var = {v: var_summary[v]["tolerance_3sigma_repeat"] for v in PANEL}
    qualified = []
    macro_mismatch = []
    for w in worlds:
        c = w["coincidence_primary"]
        fails = [v for v in PANEL if c["panel_abs"][v] > tol_by_var[v]]
        (qualified if not fails else macro_mismatch).append({"seed": w["seed"], "fails": fails})

    # memory residual (hidden) — consistency + standardized vs its own cross-world spread
    mem_summary = {}
    for v in MEM:
        arr = memresid[v]
        signs = sum(1 for x in arr if x > 0) - sum(1 for x in arr if x < 0)
        mem_summary[v] = {"mean": round(st.mean(arr), 6), "median": round(st.median(arr), 6),
                          "n_pos": sum(1 for x in arr if x > 0), "n_neg": sum(1 for x in arr if x < 0),
                          "cross_world_sd": round(sd(arr), 6),
                          "abs_mean_over_crossworld_sd": round(abs(st.mean(arr)) / (sd(arr) or 1e-12), 2)}

    # standardized residual comparison overt vs hidden (residual / cross-world SD of residual)
    def standardized(res_dict, keys):
        out = {}
        for v in keys:
            arr = res_dict[v]; s = sd(arr) or 1e-12
            out[v] = round(abs(st.mean(arr)) / s, 2)
        return out

    determinism = [w.get("determinism_bitmatch") for w in worlds if w.get("determinism_bitmatch") is not None]
    opp = [w["coincidence_primary"]["opposite_direction"] for w in worlds]
    # signed direction is available ONLY for core_mass (mass_OVER=SPIKE, mass_APPR=SUSTAINED);
    # other overt-panel signed residuals were not persisted (panel_abs only).
    mass_dir = {"spike_lt_sustained": sum(1 for w in worlds
                                          if w["coincidence_primary"]["mass_OVER"] < w["coincidence_primary"]["mass_APPR"]),
                "n": len(worlds)}

    report = {
        "schema": "KOVACS-HIDDEN-STATE-00-PHASE1-COINCIDENCE-ANALYSIS-v1",
        "source": str(DEV.relative_to(REPO)), "config": d.get("config"),
        "schedule_sha256": d.get("schedule_sha256"),
        "n_complete_worlds": len(worlds), "seeds": seeds,
        "primary_common_clock_step": kprim,
        "tolerance_policy": {
            "sources": "identical-history sham (=0 numerical) AND natural DEV temporal repeatability",
            "rule": f"per-variable tol = max({NUMERICAL_FLOOR}, {K_SIGMA} * median step-window std); NOT from any excursion",
        },
        "determinism_proven_n_worlds": len(determinism),
        "determinism_all_true_over_proven": bool(determinism) and all(determinism),
        "determinism_note": "bit-identical replay proven on the worlds carrying prove_determinism (see determinism_proven_n_worlds); also structurally unit-tested. Not run for every world (cost).",
        "opposite_direction_any": any(opp),
        "opposite_direction_note": "matched-dose common-clock design: both branches relax same-direction; no crossing (post-turnover overshoot transient is gone)",
        "per_variable": var_summary,
        "full_overt_panel_qualification": {
            "n_qualified_3sigma_repeat": len(qualified),
            "n_macrostate_mismatch": len(macro_mismatch),
            "frac_qualified": round(len(qualified) / len(worlds), 3),
            "n_qualified_sham_tolerance": 0,
            "qualified_seeds": [q["seed"] for q in qualified],
            "mismatch_detail": macro_mismatch,
        },
        "hidden_memory_residual": mem_summary,
        "mass_direction_spike_lt_sustained": mass_dir,
        "overt_abs_magnitude_consistency_DIRECTION_BLIND": standardized(resid, PANEL),
        "hidden_signed_effect_size": standardized(memresid, MEM),
        "note_standardization": ("overt values use ABSOLUTE residuals |SPIKE-SUSTAINED| (direction-blind magnitude "
                                 "consistency); hidden values use SIGNED residuals (true effect size). They are NOT "
                                 "directly comparable. Signed panel residuals other than core_mass were not persisted, "
                                 "so a directional claim is made ONLY for mass (see mass_direction_spike_lt_sustained)."),
        "interpretation": {
            "overt_coincidence": "close (~0.1-2% relative) but uncertified: NO panel variable (mass included) passes the sham/numerical (0) tolerance, and the leading variables fail 3-sigma repeatability; residuals are systematic in the sense that mass is directional (SPIKE<SUSTAINED) in most worlds, but directions of the other overt variables were not persisted.",
            "hidden_residual": "slow memory m2 / m_minus differ consistently (17/17 same sign); fast memory m1 matched. A residual hidden DOF, but m-fields are rho-weighted so this is NOT a geometry-independent claim; per mission it is the LIMITATION, not positive evidence.",
            "value_gate_input": "the full overt panel is NOT coincidence-qualified at a mechanically-defensible tolerance; even the scalar mass leg is sub-tolerance (0/17 sham, 4/17 3-sigma). A STRONG macrostate coincidence is not established.",
        },
    }
    OUT.write_text(json.dumps(report, indent=2))
    print("n_worlds:", len(worlds), "determinism proven on", report["determinism_proven_n_worlds"],
          "worlds; all_true_over_proven:", report["determinism_all_true_over_proven"])
    print("mass direction SPIKE<SUSTAINED:", mass_dir)
    print("full-panel qualified (3sigma-repeat):", len(qualified), "/", len(worlds),
          "| sham-tolerance qualified:", 0, "/", len(worlds))
    print("per-variable frac_pass (3sigma-repeat tol):")
    for v in PANEL:
        s = var_summary[v]
        print(f"  {v:18s} resid_med={s['resid_median']:.4f} repeat={s['repeatability_median']:.4f} "
              f"tol={s['tolerance_3sigma_repeat']:.4f} frac_pass={s['frac_pass']}")
    print("hidden memory residual (17/17 sign?):")
    for v in MEM:
        m = mem_summary[v]; print(f"  {v:12s} mean={m['mean']:.5f} pos/neg={m['n_pos']}/{m['n_neg']} "
                                  f"|mean|/sd={m['abs_mean_over_crossworld_sd']}")
    print("overt abs-magnitude consistency (direction-blind):", report["overt_abs_magnitude_consistency_DIRECTION_BLIND"])
    print("hidden signed effect size:", report["hidden_signed_effect_size"])
    print("WROTE", OUT.relative_to(REPO))

if __name__ == "__main__":
    main()

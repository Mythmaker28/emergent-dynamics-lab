"""OBDI01 §23-§27 — cumulative evidence matrix, post-hoc diagnostics (clearly separated from
the frozen verdict), the disposition, and the mandatory figures.

NOTHING HERE CAN CHANGE THE VERDICT. The principal outcome was evaluated once, by the frozen
gate, in `run_obdi01.py`. Every quantity below is either bookkeeping or an explicitly labelled
POST-HOC diagnostic that exists to explain the frozen result, not to revise it.
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import gate_obdi01 as GT           # noqa: E402

OUT = "/home/claude/OBDI01/out"

# The nine terminal states of this mission. The mandate's verbatim wording did not survive the
# context compaction of this session; the space is therefore RECONSTRUCTED here, exhaustively
# and by construction, and the reconstruction is declared as such rather than presented as a
# quotation. It is exhaustive and mutually exclusive: three pre-run stops, five post-run
# hypothesis verdicts, one undecided.
DISPOSITIONS = {
    "INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED":
        "§3 found an unmet frozen requirement on an axis other than D; no run is authorised",
    "DOMAIN_TEST_UNDERPOWERED":
        "§14 found no arm count reaching the required power; the plan is not frozen",
    "AUDIT_INVALID":
        "provenance, freeze identity, technical validity or evaluator agreement failed",
    "DOMAIN_INVARIANCE_ESTABLISHED":
        "every component of the frozen simultaneous region passed on fresh pre-registered data",
    "DOMAIN_INVARIANCE_PARTIAL":
        "the region did not pass in full, no unbounded alternative is supported, and the "
        "failing component(s) fail on PRECISION rather than on a detected dependence on L",
    "DOMAIN_INVARIANCE_REFUTED__H_LINEAR": "the data support a radius proportional to L",
    "DOMAIN_INVARIANCE_REFUTED__H_SUBLINEAR":
        "the data support an unbounded but slower-than-linear growth",
    "DOMAIN_INVARIANCE_REFUTED__H_FILL": "the data support the cloud filling the torus",
    "DOMAIN_INVARIANCE_NOT_DECIDED":
        "the arms are valid but discriminate none of the four hypotheses",
}


def wls(x, y, w):
    return GT.wls_slope(x, y, w)


def main():
    spec = GT.load()
    R = json.load(open(f"{OUT}/_results.json"))
    A = json.load(open(f"{OUT}/_arms.json"))
    frz = json.load(open(f"{OUT}/_freeze.json"))
    P = R["PRINCIPAL"]
    c = float(P["critical_value_c"])
    sizes = [int(x) for x in spec["domain"]["SIZES"]]

    # ---------------------------------------------------------------- the disposition
    comp = P["components"]
    failing = [k for k, v in comp.items() if not v["PASS"]]
    a_fail = [s for s, d in comp["A_shape_invariance"]["by_statistic"].items() if not d["PASS"]]
    any_alt = any(
        (not d["excludes_H_linear"]) or (not d["excludes_H_sublinear"])
        for d in comp["A_shape_invariance"]["by_statistic"].values()) \
        or not comp["B_density_exponent"]["excludes_H_fill"] \
        or not comp["B_density_exponent"]["excludes_H_sublinear"]

    if not R["all_planned_arms_run"] or R["technically_valid"] != R["n_arms"] \
            or R["gates_agree"] != R["n_arms"]:
        disp = "AUDIT_INVALID"
    elif P["DOMAIN_INVARIANCE_REGION_PASS"]:
        disp = "DOMAIN_INVARIANCE_ESTABLISHED"
    elif any_alt:
        disp = "DOMAIN_INVARIANCE_NOT_DECIDED"
    else:
        disp = "DOMAIN_INVARIANCE_PARTIAL"

    # ---------------------------------------------------------------- POST-HOC diagnostics
    extinct = [a["tag"] for a in A if not np.isfinite(a["summary"]["Rg"])]
    diag = {"LABEL": "POST-HOC — DIAGNOSTIC ONLY, CHANGES NOTHING",
            "extinct_arms": extinct,
            "why_this_matters": (
                "the frozen plan did NOT pre-specify how an extinct arm is handled. That is a "
                "design defect of this mission, and it is recorded as such. Its consequences "
                "are quantified below; none of them is applied.")}

    # (i) what the density exponent would be with the extinct arm removed
    xs, ys, ws = [], [], []
    for L in sizes:
        d = [a["summary"]["density"] for a in A if a["L"] == L and a["summary"]["N_X_mean"] > 0]
        m, s = float(np.mean(d)), float(np.std(d, ddof=1))
        xs.append(np.log(L))
        ys.append(np.log(m))
        ws.append((m / (s / np.sqrt(len(d)))) ** 2)
    g2, se2 = wls(xs, ys, ws)
    diag["density_exponent_excluding_extinct"] = {
        "gamma": g2, "se": se2, "frozen_gamma": comp["B_density_exponent"]["gamma"],
        "frozen_se": comp["B_density_exponent"]["se"],
        "comment": ("the frozen inverse-variance weighting already downweighted the "
                    "contaminated domain size, because the extinct arm inflated that group's "
                    "spread. The frozen verdict was therefore protected by the weighting — by "
                    "arithmetic, not by design.")}

    # (ii) what the failing component would need
    d2 = comp["A_shape_invariance"]["by_statistic"]["organiser_to_core"]
    need_se = (float(d2["margin"]) - abs(d2["beta"])) / c
    ratio = (d2["se"] / need_se) ** 2 if need_se > 0 else float("inf")
    diag["failing_component"] = {
        "statistic": "organiser_to_core", "beta": d2["beta"], "se": d2["se"],
        "interval_half_width": c * d2["se"], "margin": d2["margin"],
        "excess": d2["abs_beta_plus_c_se"] - d2["margin"],
        "se_required_to_pass": need_se,
        "variance_reduction_factor_required": ratio,
        "arms_per_L_that_would_have_sufficed": int(np.ceil(5 * ratio)),
        "reading": ("the point estimate is compatible with H_bound and BOTH unbounded "
                    "alternatives are excluded (|beta - 0.5| and |beta - 1| exceed c.se). The "
                    "component fails because the equivalence interval is too WIDE, not because "
                    "a dependence on L was found. Precision, not direction."),
        "root_cause": ("the pre-freeze power analysis of §14 sized the design against H_linear "
                       "using Rg. |core - organiser| has a pre-registered relative spread of "
                       "%.1f %% against Rg's %.1f %%, and an equivalence claim needs PRECISION, "
                       "which is a different requirement from power against a distant "
                       "alternative. Conflating the two is a defect of this mission's §14 and "
                       "is recorded, not excused."
                       % (100 * 0.3605 / 3.0798, 100 * 0.1386 / 5.8298))}

    # (iii) the naive exponent, without the finite-size correction
    naive = {}
    for s in GT.SHAPE_STATS:
        xs, ys, ws = [], [], []
        for L in sizes:
            v = [a["summary"][s] for a in A if a["L"] == L
                 and np.isfinite(a["summary"][s])]
            m, sd = float(np.mean(v)), float(np.std(v, ddof=1))
            xs.append(np.log(L))
            ys.append(np.log(m))
            ws.append((m / (sd / np.sqrt(len(v)))) ** 2)
        b, se = wls(xs, ys, ws)
        naive[s] = {"beta_uncorrected": b, "se": se}
    diag["uncorrected_exponents"] = {
        "by_statistic": naive,
        "comment": ("measured WITHOUT dividing out the operator's finite-size prediction. They "
                    "are close to the corrected ones because the correction itself is small "
                    "above L = 36; they are reported so the correction can be seen to be doing "
                    "little work rather than carrying the conclusion.")}

    # (iv) the legacy gate on fresh seeds against its §8 predicted false-negative rate
    OC = json.load(open(f"{OUT}/_legacy_gate_OC.json"))
    sec = R["SECONDARY"]
    obs = {str(L): 1.0 - sec["passing_by_L"][str(L)] / sec["arms_by_L"][str(L)] for L in sizes}
    diag["legacy_gate_check"] = {
        "observed_failure_rate_by_L": obs,
        "predicted_by_section_8": {"36": OC["by_L"]["36"]["false_negative_rate"],
                                   "72": OC["by_L"]["72"]["false_negative_rate"]},
        "overall_observed": 1.0 - sum(sec["passing_by_L"].values()) / R["n_arms"],
        "reading": ("under a law where H_bound holds, the locked legacy gate rejects %d of %d "
                    "healthy fresh arms, INCLUDING at L = 36. §8's bootstrap matched the L = 72 "
                    "rate closely (%.2f predicted, %.2f observed) but understated the L = 36 "
                    "one (%.3f predicted, %.2f observed) — with five arms per size these rates "
                    "are very imprecise. The qualitative conclusion of §7 is nevertheless "
                    "strengthened rather than weakened: the gate is a noisy ABSOLUTE test at "
                    "every domain size, not a large-domain problem."
                    % (R["n_arms"] - sum(sec["passing_by_L"].values()), R["n_arms"],
                       OC["by_L"]["72"]["false_negative_rate"], obs["72"],
                       OC["by_L"]["36"]["false_negative_rate"], obs["36"]))}

    # ---------------------------------------------------------------- §23 evidence matrix
    m02 = json.load(open(f"{OUT}/_obtc02_matrix.json"))
    ev = {
        "RULE": ("no seed contributes to two axes. OBTC02's seeds (9101-9503) established the "
                 "non-domain axes and are NOT reused here; OBDI01's seeds (771010-771214) "
                 "address the domain axis only and contribute to nothing else."),
        "axes": {
            "P_organiser_bound_cloud": {
                "evidence_from": "OBTC02", "seeds": "9101-9106",
                "result": m02["status"]["P_STATUS"], "OBDI01_contribution": "NONE",
                "note": "frozen; not re-opened, not re-scored"},
            "S_immobile_organiser": {
                "evidence_from": "OBTC02", "seeds": "9201-9203",
                "result": m02["status"]["S_STATUS"], "OBDI01_contribution": "NONE",
                "note": "no frozen requirement; structural NaN diagnosed in §3, not repaired"},
            "R_source_removal": {
                "evidence_from": "OBTC02", "seeds": "9301-9303",
                "result": m02["status"]["R_STATUS"], "OBDI01_contribution": "NONE"},
            "N_no_organiser": {
                "evidence_from": "OBTC02", "seeds": "9401-9402",
                "result": m02["status"]["N_STATUS"], "OBDI01_contribution": "NONE"},
            "D_domain": {
                "evidence_from_OBTC02": {"seeds": "9501-9503",
                                         "result": m02["status"]["D_STATUS"],
                                         "instrument": "the legacy absolute localisation gate",
                                         "status_of_that_instrument":
                                             frz["LEGACY_D_GATE_STATUS"]},
                "evidence_from_OBDI01": {"seeds": "771010-771214",
                                         "instrument": "DOMAIN_INVARIANCE_REGION",
                                         "result": ("PASS" if P["DOMAIN_INVARIANCE_REGION_PASS"]
                                                    else "PARTIAL"),
                                         "components": {k: v["PASS"] for k, v in comp.items()}},
                "double_counting": "NONE: disjoint seeds, disjoint instruments"},
            "E": {"result": m02["status"]["E_STATUS"], "OBDI01_contribution": "NONE"},
        },
        "SCIENTIFIC_RUNS": {"OBTC02": 17, "OBDI01": R["SCIENTIFIC_RUNS_USED"],
                            "shared": 0},
    }

    out = {
        "SECTION": "OBDI01 §23-§26",
        "DISPOSITION_SPACE": DISPOSITIONS,
        "DISPOSITION_SPACE_PROVENANCE": (
            "RECONSTRUCTED. The mandate's verbatim nine-item list did not survive this "
            "session's context compaction. The space above is rebuilt exhaustively from the "
            "mission's own terminal states — three pre-run stops named in the mandate summary, "
            "five hypothesis verdicts, one undecided — and is declared a reconstruction rather "
            "than quoted as the original."),
        "DISPOSITION": disp,
        "DISPOSITION_JUSTIFICATION": {
            "all_planned_arms_run": R["all_planned_arms_run"],
            "technically_valid": "%d/%d" % (R["technically_valid"], R["n_arms"]),
            "evaluators_agree": "%d/%d" % (R["gates_agree"], R["n_arms"]),
            "components_failing": failing, "A_statistics_failing": a_fail,
            "any_unbounded_alternative_supported": bool(any_alt),
            "why_not_ESTABLISHED": ("the simultaneous region requires every component; "
                                    "organiser_to_core did not meet the equivalence margin"),
            "why_not_REFUTED": ("every unbounded alternative is excluded on every statistic: "
                                "the exponents are %s, and the density exponent is %.4f "
                                "+- %.4f against -1 for H_sublinear and 0 for H_fill"
                                % ({s: round(d["beta"], 4) for s, d in
                                    comp["A_shape_invariance"]["by_statistic"].items()},
                                   comp["B_density_exponent"]["gamma"],
                                   comp["B_density_exponent"]["se"])),
            "why_not_NOT_DECIDED": ("three of four components passed and all four hypotheses "
                                    "were discriminated; the outcome is informative"),
        },

        # ---------------------------------------------------------------- §25
        "AUTHORISED_INTERPRETATION": {
            "may_be_said": [
                "on fresh pre-registered seeds and over a 2.67-fold range of domain size, the "
                "cloud's radius of gyration and its 80 pct radius show no dependence on L beyond "
                "the operator's own computed finite-size correction, with equivalence "
                "intervals of +-%.3f and +-%.3f on the log-log exponent"
                % (c * comp["A_shape_invariance"]["by_statistic"]["Rg"]["se"],
                   c * comp["A_shape_invariance"]["by_statistic"]["r80"]["se"]),
                "the population is independent of the domain size, so the density falls as "
                "L^%.3f +- %.3f, excluding both a constant density and a population growing "
                "with the linear size" % (comp["B_density_exponent"]["gamma"],
                                          comp["B_density_exponent"]["se"]),
                "no topological winding occurred in any of the %d in-window frames"
                % sum(v["frames"] for v in comp["C_no_true_winding"]["per_L"].values()),
                "the radial mass profile about the organiser is compatible with the exact "
                "kernel at every domain size",
                "the offset between the cloud core and the organiser was NOT shown to be "
                "domain-independent at the frozen margin: its point estimate is compatible "
                "with independence, its interval is too wide to establish it",
                "the legacy D gate, kept locked as a secondary endpoint, rejects healthy arms "
                "at every domain size including the smallest",
            ],
            "must_not_be_said": [
                "that domain invariance is established — the frozen region did not pass",
                "that the OBTC02 disposition is upgraded — it remains "
                "ORGANIZER_BOUND_CLOUD_PARTIAL, unchanged",
                "that the D axis of OBTC02 is now closed",
                "self-bound, autonomous cohesion, cell, membrane, identity, reproduction, "
                "memory, H3 confirmation, global Kamimura-Kaneko validation, life, organism, "
                "autopoiesis, fresh matter, material lineage",
            ],
            "H3_STATUS": "NOT_TESTED",
            "REPRODUCTION_STATUS": "NOT_TESTED",
            "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED",
        },

        # ---------------------------------------------------------------- §26
        "NEXT_ELIGIBILITY": {
            "eligible": [
                "a replication of the SAME frozen region with an arm count sized for the "
                "EQUIVALENCE precision of |core - organiser| — the diagnostic above gives the "
                "required variance reduction as %.2f, i.e. about %d arms per domain size — and "
                "with a pre-specified rule for extinct arms"
                % (diag["failing_component"]["variance_reduction_factor_required"],
                   diag["failing_component"]["arms_per_L_that_would_have_sufficed"]),
                "extending the domain range upward (L = 144 was shown eligible in §13) to "
                "shorten the equivalence interval through a longer lever arm rather than "
                "through more arms",
            ],
            "not_eligible": [
                "re-scoring OBTC02", "relaxing the equivalence margin after seeing the result",
                "dropping the failing statistic from the region",
                "opening the E axis, which no mission has yet defined",
                "any claim about H3, reproduction or autonomous cohesion",
            ],
        },
        "POST_HOC_DIAGNOSTICS": diag,
        "CUMULATIVE_EVIDENCE_MATRIX": ev,
        "OBTC02_DISPOSITION_AFTER_OBDI01": "ORGANIZER_BOUND_CLOUD_PARTIAL (unchanged)",
    }
    json.dump(out, open(f"{OUT}/_evidence.json", "w"), indent=1, default=str)
    print("DISPOSITION =", disp)
    print("failing components:", failing, " A failing:", a_fail)
    print("gamma excl. extinct = %+.4f +- %.4f  (frozen %+.4f +- %.4f)"
          % (g2, se2, comp["B_density_exponent"]["gamma"], comp["B_density_exponent"]["se"]))
    print("organiser_to_core needs se <= %.4f, has %.4f -> variance reduction %.2f, ~%d arms/L"
          % (need_se, d2["se"], ratio, diag["failing_component"]["arms_per_L_that_would_"
                                                                 "have_sufficed"]))
    print("legacy gate failure rate by L:", {k: round(v, 3) for k, v in obs.items()})


if __name__ == "__main__":
    main()

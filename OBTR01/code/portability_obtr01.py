"""OBTR01 §5 — recover the historical temporal question and decide, symbol by symbol, what
survives the move into the qualified LawSpec.

The mandate is explicit that a name staying the same is not evidence that the quantity is
portable. So every row below carries the historical DEFINITION, the value the qualified LawSpec
gives it, and the reason for its label. The label is assigned by a rule stated once, not by
judgement per row:

  INVALID_IN_QUALIFIED_LAWSPEC   the symbol's REFERENT — the mechanism it measures — does not
                                 exist at the qualified point, so no value of it can be
                                 informative. Zero here is not a small number; it is the
                                 absence of the channel.
  OBSOLETE                       the recorded EXPRESSION is superseded by a corrected one. The
                                 concept survives under its corrected form, listed separately.
  PORTABLE_AFTER_REDERIVATION    the definition survives unchanged but the value must be
                                 recomputed in the qualified LawSpec.
  PORTABLE_UNCHANGED             definition and value both carry over.
  UNRESOLVED                     the delivered and recovered artefacts do not decide it.
"""
from __future__ import annotations

import json
import math
import sys

import yaml

WC = "/home/claude/OBTR01/verify/obdca01/wc"
MT = "/home/claude/OBTR01/verify/mtw01"
OUT = "/home/claude/OBTR01/out"
sys.path.insert(0, "/home/claude/OBTR01/code")


def main():
    spec = yaml.safe_load(open(f"{WC}/OBDI02/code/obdi02_protocol.yaml"))
    pt = spec["point"]
    w = json.load(open(f"{MT}/out/_window.json"))
    corr = json.load(open(f"{OUT}/_corrections.json"))

    q = pt["p_hop"] / 4.0
    D_eff = q * (1 - q)
    a_X, a_Y = pt["muX"], pt["muY"]
    kY, kX = pt["kY"], pt["kX"]
    Q_max = corr["C3_Q_MAX"]["EXACT_over_the_full_capacity_space"]["Q_max"]
    ell_X = math.sqrt(D_eff / a_X)

    # ---------------------------------------------------------------- the historical question
    question = {
        "SOURCE": ["MTW01/code/window.py", "MTW01/out/_window.json",
                   "MTW01/out/MINCORE_TIMESCALE_WINDOW_PREPLAN.md"],
        "RECOVERY": "digest-verified against MCM01 C-2; see OBTR01/out/_mtw01_recovery.json",
        "THE_QUESTION": (
            "Is there a non-empty band of ORGANISER birth rate R_Y in which one organiser "
            "divides into two within the horizon, while a THIRD organiser does not appear "
            "before the two existing ones have separated by Delta = 2 L_C?"),
        "THE_TWO_INEQUALITIES": {
            "lower_extinction_vs_division": "a_Y < R_Y",
            "upper_division_vs_explosion":
                "R_Y < min( H3_max / (2 safety tau_sep) , D_Y (a_X/R_X)^(2/d) )"},
        "THE_NON_EMPTINESS_CONDITION":
            "2 safety a_Y tau_sep / H3_max < 1, with tau_sep = Delta^2 / (8 D_Y)",
        "WHAT_IT_WAS_FOR": ("MTW01 needed a design point at which an organiser could plausibly "
                            "duplicate without a third one confusing the observation. The "
                            "window is a DESIGN feasibility condition, not a claim about the "
                            "system."),
        "MTW01_ADJUDICATION": w["adjudication"],
        "MTW01_DISPOSITION_UNCHANGED":
            "WINDOW_NOT_CONFIRMED__FAILURE_NOT_ATTRIBUTABLE_TO_THE_HAZARD",
        "H3_OBSERVED_ON_ALL_FOUR_MTW01_ARMS": 0.0,
    }

    def row(sym, hist_def, hist_val, qual_val, label, why, corrected_form=None):
        d = {"symbol": sym, "historical_definition": hist_def,
             "historical_value": hist_val, "value_in_the_qualified_LawSpec": qual_val,
             "PORTABILITY": label, "reason": why}
        if corrected_form:
            d["corrected_form"] = corrected_form
        return d

    dead = ("the qualified LawSpec has kY = 0 and muY = 0 EXACTLY. There is no X + Y -> 2Y "
            "channel and no organiser death, so the organiser is a single conserved particle "
            "for the whole run. The mechanism this symbol measures does not exist here, and no "
            "measurement of it can be informative: the zero is structural, not small.")

    T = [
        row("R_Y", "organiser birth rate per organiser, R_Y = k_Y * Q",
            "k_Y Q, band [k_Y, 28 k_Y]", 0.0, "INVALID_IN_QUALIFIED_LAWSPEC", dead),
        row("gamma_Y", "Kamimura-Kaneko minority branching fraction, r_Y = p gamma_Y",
            "carried by k_Y", 0.0, "INVALID_IN_QUALIFIED_LAWSPEC",
            "gamma_Y parametrises the same absent channel. " + dead),
        row("a_Y", "organiser death rate per step, a_Y = mu_Y",
            w["frozen_point"]["a_Y"], a_Y, "INVALID_IN_QUALIFIED_LAWSPEC", dead),
        row("D_X = p_hop_X / 4", "body-molecule diffusion constant, historical convention",
            w["design_point"]["D_X"], pt["p_hop"] / 4.0, "OBSOLETE",
            "superseded by D_eff = q(1-q); the four sequential passes let a molecule move and "
            "move back within one step. The correction is exactly -q.",
            corrected_form="D_X = q(1-q) = %.10g at the qualified point" % D_eff),
        row("D_X (concept)", "body-molecule diffusion constant", None, D_eff,
            "PORTABLE_AFTER_REDERIVATION",
            "the concept survives; the value must be recomputed with the corrected law. "
            "Rederived in OBTR01 §7 and validated four ways."),
        row("D_Y", "organiser diffusion constant", w["design_point"]["D_Y"], D_eff,
            "PORTABLE_AFTER_REDERIVATION",
            "p_hop_Y = p_hop_X in the qualified point, so D_Y = D_X = %.10g. Under the frozen "
            "condition S the organiser is immobilised and D_Y = 0 exactly; both regimes are "
            "carried forward." % D_eff),
        row("Q = n_X * c_Y", "the capacity-limited product that drives organiser birth",
            "combinatorial, 0..28", "combinatorial, 0..%d" % Q_max,
            "PORTABLE_AFTER_REDERIVATION",
            "as a COMBINATORIAL quantity of the occupancy vector it is still well defined and "
            "its maximum is recomputed here. As the DRIVER of a rate it is invalid, because "
            "the rate it drives is k_Y Q = 0."),
        row("Q_max = 27", "maximum of Q under n_SY <= S0", 27, Q_max, "OBSOLETE",
            "the restriction n_SY <= S0 is unsound: SY diffuses and is accepted up to the "
            "destination's free capacity. Exhaustive enumeration over the full capacity space "
            "gives 28 at (n_X 7, n_SY 4, free 4); the old value is reproduced only under the "
            "old restriction.",
            corrected_form="Q_max = %d, reproduced by two independent routes" % Q_max),
        row("tau_sep = Delta^2 / (8 D_Y)",
            "mean time for two organisers to separate by Delta = 2 L_C",
            w["design_point"]["tau_sep"], None, "INVALID_IN_QUALIFIED_LAWSPEC",
            "there is never more than one organiser, so there is no pair to separate. " + dead),
        row("first-passage machinery behind tau_sep",
            "mean exit time of the relative walk from a disc of radius Delta", None,
            "rederived discretely in OBTR01 §6/§10", "PORTABLE_AFTER_REDERIVATION",
            "the MATHEMATICS is portable and is reused for TAU_FP_RELATIVE, but with two "
            "changes: the relative walk is now X against the organiser rather than organiser "
            "against organiser, and the discrete solve shows the continuum law understates the "
            "lattice exit time by %.1f %% at Delta = 5."
            % (100 * corr["C2_FIRST_PASSAGE"]["LATTICE_CORRECTION_TO_THE_CONTINUUM_LAW"]
               ["excess_at_the_design_Delta"])),
        row("window lower bound  a_Y < R_Y", "extinction versus division of the organiser",
            "0.0005 < R_Y", "0 < 0, which is FALSE", "INVALID_IN_QUALIFIED_LAWSPEC",
            "both sides are identically zero. The inequality is not merely violated; both of "
            "its terms are absent mechanisms. " + dead),
        row("window upper bound  R_Y < min(H3 gate, KK packed)",
            "division versus explosion of organisers",
            w["design_point"]["window_upper_R_Y_binding"],
            "vacuous: 0 < anything positive", "INVALID_IN_QUALIFIED_LAWSPEC",
            "the constraint is satisfied trivially because the rate it bounds is zero. A "
            "vacuously satisfied constraint carries no information and must not be reported "
            "as a passed condition. " + dead),
        row("H3_max = -ln P*", "admissible cumulative hazard of a third organiser",
            w["design_point"]["H3_max"], "hazard is exactly 0",
            "INVALID_IN_QUALIFIED_LAWSPEC",
            "the third-organiser hazard is identically zero because k_Y = 0. " + dead),
        row("T_div = 1 / R_Y", "expected time to organiser division",
            w["design_point"]["T_div_at_Q_max"], "infinite",
            "INVALID_IN_QUALIFIED_LAWSPEC", dead),
        row("ell_X = sqrt(D_X / a_X)", "diffusion-decay cloud radius of the body cloud",
            w["design_point"]["cluster"]["ell_X"], ell_X, "PORTABLE_AFTER_REDERIVATION",
            "definition unchanged; the value moves because D_X is corrected and mu_X differs. "
            "It is %.6f at the qualified point." % ell_X),
        row("L_C = max(ell_X, L_packed)", "cluster size, larger of the two lower bounds",
            w["design_point"]["cluster"]["L_C"], None, "PORTABLE_AFTER_REDERIVATION",
            "the packed branch depends on R_X, which C4/C5 reclassify: at k_X = 1 the birth "
            "probability saturates, so R_X is not a branching rate but the additive intensity "
            "min(n_SX, free). The packed bound must therefore be rebuilt on the measured "
            "source intensity, not on k_X Q_max."),
        row("R_X = min(k_X Q_max, resource cap)", "body-molecule production rate per organiser",
            w["design_point"]["cluster"]["R_X"], None, "OBSOLETE",
            "at k_X = 1 the birth probability min(1, k_X n_X n_Y) is exactly 1 whenever the "
            "organiser cell holds one X and one Y, so the number born is min(n_SX, free) and "
            "does not depend on n_X or on k_X. The kinetic cap k_X Q_max is not the operative "
            "quantity.",
            corrected_form="B_t = min(n_SX, free) at the organiser cell, measured not predicted"),
        row("c_X G(0) criticality", "scalar branching criticality of the body cloud",
            "2.53 at the MTW01 design point", None, "OBSOLETE",
            corr["C4_SCALAR_CRITICALITY"]["CONSEQUENCE"],
            corrected_form="NOT_VALID_AS_PRIMARY_CRITICALITY; the qualified source is additive"),
        row("chi = sqrt(4 D_Y / a_X) / ell_X",
            "organiser wander over one body-molecule lifetime, in cloud radii",
            w["design_point"]["coherence_chi"],
            math.sqrt(4.0 * D_eff / a_X) / ell_X, "PORTABLE_AFTER_REDERIVATION",
            "definition unchanged, value recomputed with the corrected diffusion constant."),
        row("safety, sep_factor, P*", "design constants of the MTW01 feasibility argument",
            {"safety": w["design_point"]["safety_factor"],
             "sep": w["design_point"]["sep_factor"], "P_star": w["design_point"]["P_star"]},
            "unchanged as conventions", "PORTABLE_UNCHANGED",
            "these are stipulations, not measurements. They carry over as conventions, but "
            "they are conventions OF A CONDITION that is itself invalid here, so carrying them "
            "over gives nothing."),
        row("N_X <= S0 / mu_X", "bound on the body-cloud population", "presented as exact",
            "not exact; the exact per-organiser cap is 7 / mu_X at CAP = 16", "OBSOLETE",
            "`_diffuse` accepts min(movers, dest_free), capped by free capacity and not by S0, "
            "so a cell can hold more than S0 resource units.",
            corrected_form="N_X <= 7 / mu_X = %.1f at the qualified point" % (7.0 / a_X)),
    ]

    counts = {}
    for r in T:
        counts[r["PORTABILITY"]] = counts.get(r["PORTABILITY"], 0) + 1

    invalid = [r["symbol"] for r in T if r["PORTABILITY"] == "INVALID_IN_QUALIFIED_LAWSPEC"]
    out = {
        "SECTION": "OBTR01 §5",
        "HISTORICAL_QUESTION": question,
        "QUALIFIED_LAWSPEC_PARAMETERS_THAT_DECIDE_MOST_ROWS": {
            "kY": kY, "muY": a_Y, "kX": kX, "muX": a_X, "p_hop": pt["p_hop"],
            "CONSEQUENCE": ("kY = 0 and muY = 0 remove the entire organiser birth-death "
                            "channel, which is what the historical window constrains.")},
        "LABELLING_RULE": {
            "INVALID_IN_QUALIFIED_LAWSPEC": "the referent mechanism does not exist here",
            "OBSOLETE": "the recorded expression is superseded by a corrected one",
            "PORTABLE_AFTER_REDERIVATION": "definition survives, value must be recomputed",
            "PORTABLE_UNCHANGED": "definition and value both carry over",
            "UNRESOLVED": "the artefacts do not decide it"},
        "TABLE": T,
        "COUNTS": counts,
        "SYMBOLS_WITHOUT_A_REFERENT_HERE": invalid,
        "UNRESOLVED_ROWS": [r["symbol"] for r in T if r["PORTABILITY"] == "UNRESOLVED"],
        "WHAT_THIS_ALREADY_IMPLIES_FOR_SECTION_13": (
            "every symbol appearing in BOTH historical inequalities is invalid in the "
            "qualified LawSpec. §13 must still rederive each inequality rather than inherit "
            "this conclusion, but the direction is set: the window is not a statement that "
            "fails here, it is a statement about a mechanism that is absent here."),
    }
    json.dump(out, open(f"{OUT}/_portability.json", "w"), indent=1, default=str)

    print("THE HISTORICAL QUESTION")
    print("  " + question["THE_QUESTION"])
    print("  lower : %s" % question["THE_TWO_INEQUALITIES"]["lower_extinction_vs_division"])
    print("  upper : %s" % question["THE_TWO_INEQUALITIES"]["upper_division_vs_explosion"])
    print("  MTW01 adjudication: %s ; disposition unchanged: %s"
          % (question["MTW01_ADJUDICATION"], question["MTW01_DISPOSITION_UNCHANGED"]))
    print()
    print("%-42s %s" % ("SYMBOL", "PORTABILITY"))
    print("-" * 84)
    for r in T:
        print("%-42s %s" % (r["symbol"][:42], r["PORTABILITY"]))
    print("-" * 84)
    for k, v in sorted(counts.items()):
        print("  %-32s %d" % (k, v))
    print()
    print("symbols with no referent at the qualified point: %d of %d"
          % (len(invalid), len(T)))


if __name__ == "__main__":
    main()

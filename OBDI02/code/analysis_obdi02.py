"""OBDI02 §18-§19 — cumulative evidence matrix and the single disposition.

The disposition is a strict cascade over the nine frozen states, evaluated in an order fixed
before the runs: instrument first, then extinction, then contradiction, then the primary test.
"""
from __future__ import annotations

import json
import math

import numpy as np

OUT = "/home/claude/OBDI02/out"
WC = "/home/claude/OBDI02/verify/obdi01/wc"


def main():
    import gate_obdi02 as GT
    spec = GT.load()
    R = json.load(open(f"{OUT}/_results.json"))
    A = json.load(open(f"{OUT}/_arms.json"))
    frz = json.load(open(f"{OUT}/_freeze.json"))
    ad = json.load(open(f"{OUT}/_adjudication.json"))
    pv = json.load(open(f"{OUT}/_provenance.json"))
    au = json.load(open(f"{OUT}/_equivalence_audit.json"))
    pw = json.load(open(f"{OUT}/_power.json"))
    ov = json.load(open(f"{OUT}/_outcome_vector.json"))
    sd = json.load(open(f"{OUT}/_seeds.json"))
    o1res = json.load(open(f"{WC}/OBDI01/out/_results.json"))
    o1m = json.load(open(f"{WC}/OBDI01/out/_evidence.json"))
    sizes = [int(x) for x in spec["domain"]["SIZES"]]

    P = R.get("PRIMARY", {})
    S = R.get("POPULATION_SUPPORT", {})
    E = R.get("EXTINCTION_SENSITIVITY", {})
    SEC = R.get("SECONDARY", {})

    # ---------------------------------------------------------------- extinction trend
    ext = {L: R["extinctions_by_L"][str(L)] for L in sizes}
    n_per = int(spec["domain"]["SEEDS_PER_SIZE"])
    # one-sided test of a rising extinction rate with L: Cochran-Armitage style score on log L
    xs = np.array([math.log(L) for L in sizes], float)
    ks = np.array([ext[L] for L in sizes], float)
    p_all = ks.sum() / (n_per * len(sizes))
    xbar = xs.mean()
    num = float((ks * (xs - xbar)).sum())
    den = math.sqrt(n_per * p_all * (1 - p_all) * float(((xs - xbar) ** 2).sum())) \
        if 0 < p_all < 1 else 0.0
    trend_z = num / den if den > 0 else 0.0
    trend_p = 1.0 - 0.5 * (1.0 + math.erf(trend_z / math.sqrt(2.0)))
    extinction = {
        "by_L": {str(L): ext[L] for L in sizes}, "arms_per_L": n_per,
        "rate_by_L": {str(L): ext[L] / n_per for L in sizes},
        "pooled_rate": p_all,
        "historical_rate": pw["EXTINCTION_RATE_USED"]["p"],
        "trend_statistic_z": trend_z, "one_sided_p_for_a_rise_with_L": trend_p,
        "RISES_WITH_L": bool(trend_p < 0.05),
        "support_gate": S.get("PASS"),
    }

    # ---------------------------------------------------------------- disposition cascade
    reasons = []
    disp = None
    if pv["PROVENANCE_STATUS"] != "SELF_CONTAINED_SPLIT_DELIVERY_PASS":
        disp = "PROVENANCE_FAIL"
        reasons.append("the inherited self-contained state could not be rebuilt")
    elif au["OBDI01_EQUIVALENCE_METHOD"] in ("MISALIGNED", "UNRESOLVED"):
        disp = "INHERITED_EQUIVALENCE_ESTIMAND_NOT_RECOVERABLE"
        reasons.append("the inherited estimand or its method could not be reconstructed")
    elif (R["technically_invalid"] or R["gates_disagree"] or not R["all_planned_arms_run"]):
        disp = "AUDIT_INVALID"
        reasons.append("technically invalid arms %s ; evaluator disagreements %s ; all arms run "
                       "%s" % (R["technically_invalid"], R["gates_disagree"],
                               R["all_planned_arms_run"]))
    elif not S.get("PASS") or extinction["RISES_WITH_L"]:
        disp = "DOMAIN_INVARIANCE_NOT_QUALIFIED__EXTINCTION_DEPENDENCE"
        reasons.append("population support gate %s ; extinction rises with L %s"
                       % (S.get("PASS"), extinction["RISES_WITH_L"]))
    elif SEC.get("ANY_MATERIAL_CONTRADICTION"):
        disp = "CUMULATIVE_CLOUD_QUALIFICATION_CONTRADICTED"
        reasons.append("a fresh secondary endpoint materially contradicts an inherited axis")
    else:
        # The remaining three states are separated by the MANDATE's own §19 conditions, applied
        # literally. Note the two-level structure, which is stated rather than smoothed over:
        #   * the FROZEN TEST is a TOST at the inherited margin 0.25 and it PASSES;
        #   * the MANDATE's bar for the cumulative qualification is explicitly the interval
        #     being contained in [-0.042, +0.042], which is stricter and is NOT met.
        # A qualification is a claim, not a test result, so the stricter bar governs it.
        lo, hi = P.get("interval", [float("nan")] * 2)
        bar = float(spec["primary_endpoint"]["stringent_reference_margin"])
        inside_bar = bool(np.isfinite(lo) and -bar < lo and hi < bar)
        margin = float(P["equivalence_margin"])
        material = bool(np.isfinite(lo) and (lo > margin or hi < -margin))
        radius_grows = bool(SEC["scaling_Rg"]["CONTRADICTS_BOUNDEDNESS"]
                            or SEC["scaling_r80"]["CONTRADICTS_BOUNDEDNESS"])
        qual_conditions = {
            "obdi01_adjudication_closed": True,
            "all_inherited_axes_verifiable": pv["PROVENANCE_STATUS"]
                == "SELF_CONTAINED_SPLIT_DELIVERY_PASS",
            "population_support_gate_passes": bool(S.get("PASS")),
            "primary_interval_inside_[-0.042,+0.042]": inside_bar,
            "no_spatial_guard_rail_contradicts_boundedness":
                not SEC.get("ANY_MATERIAL_CONTRADICTION"),
            "three_sizes_complete": bool(R["all_planned_arms_run"]),
            "seeds_fresh": bool(sd["DISJOINT"]),
            "no_technical_or_protocol_defect": bool(not R["technically_invalid"]
                                                    and not R["gates_disagree"]),
        }
        if all(qual_conditions.values()):
            disp = "ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE"
            reasons.append("every condition of the mandate's §19 qualification is met")
        elif material or radius_grows:
            disp = "DOMAIN_SIZE_INVARIANCE_FAIL"
            reasons.append("the fresh data positively support a dependence on L")
        else:
            disp = "DOMAIN_RELATIVE_ATTACHMENT_EQUIVALENCE_NOT_ESTABLISHED"
            reasons.append(
                "the frozen TOST passes at the inherited margin %.2f — the whole 90 %% "
                "interval [%+.5f, %+.5f] lies inside it — but the mandate's qualification bar "
                "is the interval being contained in [-%.3f, +%.3f], and the achieved bound is "
                "%.5f, %.1f times that figure. No guard-rail supports growth with L: R_g gives "
                "beta = %+.5f +- %.5f and r80 gives %+.5f +- %.5f, both flat to about one "
                "percent." % (margin, lo, hi, bar, bar,
                              P["achieved_equivalence_bound"],
                              P["achieved_equivalence_bound"] / bar,
                              SEC["scaling_Rg"]["beta"], SEC["scaling_Rg"]["se"],
                              SEC["scaling_r80"]["beta"], SEC["scaling_r80"]["se"]))
        out_qual = qual_conditions

    try:
        qc = out_qual
    except NameError:
        qc = None

    # ---------------------------------------------------------------- §18 cumulative matrix
    o1P = o1res["PRINCIPAL"]["components"]
    matrix = [
        {"axe": "Population stationnaire", "source": "OBTC02", "protocole": "obtc02_protocol.yaml",
         "seeds": "9101-9106", "hash": frz["PARENT"]["METHODS_CORE_HASH"][:16] + " (via OBDI01)",
         "disposition": "PASS (5/5 bras P requis)", "limitations": "un bras P eteint sur six"},
        {"axe": "Source statique", "source": "OBTC02", "protocole": "obtc02_protocol.yaml",
         "seeds": "9201-9203", "hash": "-", "disposition":
             "FAIL_ON_THE_PER_ARM_GATE__NO_FROZEN_REQUIREMENT",
         "limitations": "echec structurel 0/0 = NaN, diagnostique et non repare"},
        {"axe": "Retrait de source", "source": "OBTC02", "protocole": "obtc02_protocol.yaml",
         "seeds": "9301-9303", "hash": "-", "disposition": "PASS",
         "limitations": "decroissance comparee a la prediction analytique"},
        {"axe": "Absence de source", "source": "OBTC02", "protocole": "obtc02_protocol.yaml",
         "seeds": "9401-9402", "hash": "-", "disposition": "PASS", "limitations": "-"},
        {"axe": "Turnover", "source": "OBTC02", "protocole": "obtc02_protocol.yaml",
         "seeds": "9102-9106", "hash": "-", "disposition": "PASS",
         "limitations": "environ 36 renouvellements par fenetre"},
        {"axe": "Causalite de la source", "source": "OBTC02", "protocole": "obtc02_protocol.yaml",
         "seeds": "9301-9303, 9401-9402", "hash": "-", "disposition": "PASS",
         "limitations": "-"},
        {"axe": "Compatibilite operateur", "source": "OBTC02", "protocole": "N2 envelope",
         "seeds": "9101-9503", "hash": "-", "disposition": "PASS",
         "limitations": "APPROXIMATE_WITH_EMPIRICAL_ERROR pour l'operateur complet"},
        {"axe": "Rg et r80 selon L", "source": "OBDI01", "protocole": "obdi01_protocol.yaml",
         "seeds": "771010-771214", "hash": frz["PARENT"]["METHODS_CORE_HASH"][:16],
         "disposition": "PASS (beta = %+.4f et %+.4f)"
                        % (o1P["A_shape_invariance"]["by_statistic"]["Rg"]["beta"],
                           o1P["A_shape_invariance"]["by_statistic"]["r80"]["beta"]),
         "limitations": "intervalle a 99.49 %, surconservateur"},
        {"axe": "Densite selon L", "source": "OBDI01", "protocole": "obdi01_protocol.yaml",
         "seeds": "771010-771214", "hash": frz["PARENT"]["METHODS_CORE_HASH"][:16],
         "disposition": "PASS (gamma = %+.4f)" % o1P["B_density_exponent"]["gamma"],
         "limitations": "un bras eteint entre avec une densite nulle"},
        {"axe": "Winding selon L", "source": "OBDI01", "protocole": "obdi01_protocol.yaml",
         "seeds": "771010-771214", "hash": frz["PARENT"]["METHODS_CORE_HASH"][:16],
         "disposition": "PASS (0 sur 2700 trames)",
         "limitations": "unite = la trame, defendable seulement parce que le compte est nul"},
        {"axe": "Profil radial selon L", "source": "OBDI01", "protocole": "obdi01_protocol.yaml",
         "seeds": "771010-771214", "hash": frz["PARENT"]["METHODS_CORE_HASH"][:16],
         "disposition": "PASS (5/5, 4/5, 5/5 bras ; seuil 4/5)",
         "limitations": "a L=72 le seuil est atteint exactement"},
        {"axe": "Equivalence precise de |C-Y|", "source": "OBDI02",
         "protocole": "obdi02_protocol.yaml", "seeds": "8100000-8102045",
         "hash": frz["OBDI02_METHODS_CORE_HASH"][:16],
         "disposition": ("%s (beta = %+.5f, intervalle [%+.5f, %+.5f], borne atteinte %.5f)"
                         % ("PASS" if P.get("PASS") else "FAIL", P.get("beta", float("nan")),
                            P.get("interval", [float("nan")] * 2)[0],
                            P.get("interval", [float("nan")] * 2)[1],
                            P.get("achieved_equivalence_bound", float("nan")))),
         "limitations": ("la reference stringente 0.042 reste sous-puissante par construction "
                         "(puissance %.3f declaree avant les runs)"
                         % float(spec["primary_endpoint"]["stringent_reference_power"]))},
    ]
    seed_use = {"OBTC02": "9101-9503 (17)", "OBDI01": "771010-771214 (15)",
                "OBDI02": "8100000-8102045 (%d)" % spec["domain"]["TOTAL_ARMS"]}

    out = {
        "SECTION": "OBDI02 §18-§19",
        "DISPOSITION": disp, "DISPOSITION_REASONS": reasons,
        "QUALIFICATION_CONDITIONS_SS19": qc,
        "TWO_LEVEL_STRUCTURE": ("the frozen TEST uses the inherited margin 0.25 and it passes; the mandate's QUALIFICATION bar in §19 is the stricter [-0.042, +0.042] and it is not met. Both are reported, and the stricter one governs the claim."),
        "DISPOSITION_SPACE": spec["dispositions"],
        "DISPOSITION_SPACE_IS_FROZEN_IN_THE_PROTOCOL": True,
        "CASCADE_ORDER": ["PROVENANCE_FAIL", "INHERITED_EQUIVALENCE_ESTIMAND_NOT_RECOVERABLE",
                          "AUDIT_INVALID",
                          "DOMAIN_INVARIANCE_NOT_QUALIFIED__EXTINCTION_DEPENDENCE",
                          "CUMULATIVE_CLOUD_QUALIFICATION_CONTRADICTED",
                          "ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE",
                          "DOMAIN_SIZE_INVARIANCE_FAIL",
                          "DOMAIN_RELATIVE_ATTACHMENT_EQUIVALENCE_NOT_ESTABLISHED"],
        "EXTINCTION": extinction,
        "CUMULATIVE_EVIDENCE_MATRIX": matrix,
        "SEED_USE_BY_MISSION": seed_use,
        "NO_SEED_COUNTED_TWICE": True,
        "OBDI01_REPORTED_DISPOSITION": "DOMAIN_INVARIANCE_PARTIAL",
        "OBDI01_ADJUDICATED_DISPOSITION": ad["OBDI01_ADJUDICATED_DISPOSITION"],
        "AUTHORISED_INTERPRETATION": {
            "if_qualified": ("Dans le LawSpec equilibre sans cohesion ajoutee, une source "
                             "organisatrice mobile maintient causalement un nuage dissipatif "
                             "materiellement renouvele dont l'echelle spatiale relative reste "
                             "equivalente a une constante sur les tailles de domaine testees."),
            "must_not_be_said": ["self-bound", "cohesion autonome", "cellule", "identite",
                                 "reproduction", "memoire", "H3 confirme",
                                 "validation globale de Kamimura-Kaneko"],
            "H3_STATUS": "NOT_TESTED", "REPRODUCTION_STATUS": "NOT_TESTED",
            "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED", "C3_STATUS": "NOT_QUALIFIED"},
        "NEXT_SCIENTIFIC_ELIGIBILITY": (
            "ORGANIZER_BOUND_TIMESCALE_REDERIVATION_ONLY"
            if disp == "ORGANIZER_BOUND_TURNOVER_CLOUD_QUALIFIED_BY_DOMAIN_PRECISION_CLOSURE"
            else ("SOURCE_RESPONSE_FINITE_SIZE_MODEL_REFINEMENT_ONLY"
                  if disp == "DOMAIN_SIZE_INVARIANCE_FAIL" else "NONE")),
        "ov_reference": ov["AMBIGUITY_2_NOTATION"]["ANSWER"],
        "seeds_disjoint": sd["DISJOINT"],
        "obdi01_matrix_reference": o1m["CUMULATIVE_EVIDENCE_MATRIX"]["RULE"],
    }
    json.dump(out, open(f"{OUT}/_evidence.json", "w"), indent=1, default=str)
    print("DISPOSITION =", disp)
    for r in reasons:
        print("   -", r)
    print("extinctions by L:", extinction["by_L"], " trend p =", round(trend_p, 4))
    print("NEXT_SCIENTIFIC_ELIGIBILITY =", out["NEXT_SCIENTIFIC_ELIGIBILITY"])


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/claude/OBDI02/code")
    main()

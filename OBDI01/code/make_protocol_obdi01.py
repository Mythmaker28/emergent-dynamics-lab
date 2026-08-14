"""OBDI01 §9, §10, §15, §16, §21 — generate the FROZEN protocol.

The yaml is generated, not typed, so that every frozen number is provably the one computed in
§12-§14 and not a transcription of it. After this file has run, `obdi01_protocol.yaml` is the
single source of truth and nothing in the mission may change it.

The design decision this file records, and the reason for it:

  §7 established LEGACY_D_GATE_STATUS = MISALIGNED_WITH_DOMAIN_INVARIANCE. Its threshold is
  min(12.8, 0.35 L), which over 36 -> 72 moves by 1.6 %, so the gate measures an ABSOLUTE
  radius. Building the new principal outcome on absolute agreement with a prediction would
  repeat exactly that error. The principal outcome therefore tests the L-DEPENDENCE of each
  statistic after dividing out the operator's own finite-size prediction — a ratio, in which
  any L-independent bias of the capacity-constrained engine cancels.

  Rejecting "the exponent is 1" is NOT the same as establishing boundedness. The principal
  outcome is therefore an EQUIVALENCE test: it can only be passed by an interval that excludes
  every unbounded alternative, never by a failure to reject.
"""
from __future__ import annotations

import json
import math

import yaml

OUT = "/home/claude/OBDI01/out"
CODE = "/home/claude/OBDI01/code"

ALPHA_FAMILY = 0.05
EQUIV_MARGIN = 0.25              # on the log-log slope
EQUIV_MARGIN_DENSITY = 0.25
WINDING_TOLERANCE = 0.01         # pooled fraction of frames per domain size
PROFILE_ARMS_REQUIRED = 4        # of 5, per domain size
RADIAL_EDGES = list(range(0, 16))  # 0,1,...,15 then a final open bin


def sidak_c(k, alpha=ALPHA_FAMILY):
    per = 1.0 - (1.0 - alpha) ** (1.0 / k)
    lo, hi = 0.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 2.0 * (1.0 - 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0)))) > per:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi), per


def main():
    P = json.load(open(f"{OUT}/_predictions.json"))
    W = json.load(open(f"{OUT}/_power.json"))
    S = json.load(open(f"{OUT}/_seeds.json"))
    G = json.load(open(f"{OUT}/_legacy_D_gate_status.json"))
    obtc02 = yaml.safe_load(open(f"{CODE}/obtc02_protocol.yaml"))

    sizes = [int(x) for x in W["DOMAIN_SIZES"]]
    n_per = int(W["SEEDS_PER_DOMAIN_SIZE"])
    K = 3 + 1 + len(sizes) + len(sizes)
    c, per_test = sidak_c(K)

    pred = {L: {"Rg": P["per_L"][str(L)]["SAMPLED"]["Rg"]["mean"],
                "r80": P["per_L"][str(L)]["SAMPLED"]["r80"]["mean"],
                "organiser_to_core": P["per_L"][str(L)]["SAMPLED"]["organiser_to_core"]["mean"],
                "r80_organiser": P["per_L"][str(L)]["SAMPLED"]["r80_organiser"]["mean"],
                "density": P["N_X_anchor_used"] / L ** 2,
                "N_X": P["N_X_anchor_used"],
                "m2_periodic_image_deficit":
                    P["per_L"][str(L)]["EXACT_KERNEL"]["periodic_image_correction"][
                        "relative_deficit"]}
            for L in sizes}
    sd_prereg = {s: W["variance_decomposition"][s]["pooled_sd_used"]
                 for s in ("Rg", "r80", "r80_organiser", "organiser_to_core")}

    spec = {
        "mission": "ORGANIZER-BOUND-DOMAIN-INVARIANCE-01",
        "parent": {"mission": "ORGANIZER-BOUND-TURNOVER-CLOUD-02",
                   "head": "bb7fea748560ce8489d18ca64973f95e907ec382",
                   "disposition": "ORGANIZER_BOUND_CLOUD_PARTIAL",
                   "METHODS_CORE_HASH":
                       "747c1f5e68da95c7b63b81b09fcc531cc0dc7b0e13a3ceadb54d10103fc350f7"},

        # ---------------------------------------------------------------- §9
        "design_status": {
            "DESIGN_STATUS": "OUTCOME_INFORMED_TARGETED_FOLLOWUP",
            "why": ("this mission exists because a specific axis of OBTC02 did not close. The "
                    "DESIGN of the new outcome was chosen after seeing that result and is "
                    "therefore outcome-informed; saying otherwise would be false."),
            "CONFIRMATORY_DATA_STATUS": "FRESH_AND_PREREGISTERED",
            "why_data": ("every arm below is run on a seed disjoint from all earlier missions, "
                         "after this file is frozen and its digest recorded. No OBTC02 arm "
                         "contributes to the new principal outcome."),
            "consequence": ("an outcome-informed DESIGN evaluated on FRESH data supports a "
                            "claim about the domain axis only; it does not upgrade OBTC02, and "
                            "it does not license a claim that the whole qualification is now "
                            "complete."),
        },

        # ---------------------------------------------------------------- §10
        "route": {
            "ROUTE": "B",
            "definition": ("the legacy D gate stays a LOCKED SECONDARY endpoint. It is neither "
                           "removed nor reinterpreted nor retuned. The new principal outcome "
                           "measures the dependence on L directly."),
            "LEGACY_D_GATE_STATUS": G["LEGACY_D_GATE_STATUS"],
            "grounds": G["REASONS"],
            "rejected_routes": {
                "A": ("keep the legacy gate as the principal outcome. Rejected: §7 shows it "
                      "does not measure domain invariance at all, so passing or failing it "
                      "again would answer a different question."),
                "C": ("declare the axis unclosable with the frozen engine. Rejected: §12-§14 "
                      "show the operator makes sharp parameter-free predictions at every "
                      "candidate L and that the design has ample power.")},
        },

        # ---------------------------------------------------------------- §17-§19 identity
        "window": dict(obtc02["window"]),
        "point": dict(obtc02["point"]),
        "identity_with_obtc02": {
            "LAWSPEC_DIFF_FROM_OBTC02": "NONE",
            "CHEMOSTAT_DIFF_FROM_OBTC02": "NONE",
            "COHESION_DIFF_FROM_OBTC02": "NONE",
            "SCIENTIFIC_PARAMETER_DIFF_FROM_OBTC02": "NONE",
            "DOMAIN_TEST_DESIGN": "NEW_PREREGISTERED_TARGETED_FOLLOWUP",
            "how_enforced": ("the arms are produced by calling OBTC02's own `run_arm` "
                             "unmodified, with OBTC02's own spec object; only the domain size, "
                             "the seed and the output directory differ. Identity is therefore "
                             "a property of the call graph, not a claim to be trusted."),
            "molecular_raw_data": "recorded per arm exactly as in OBTC02: births, deaths, ids",
            "technical_validity": "OBTC02's technical layer, evaluated before any science",
        },

        # ---------------------------------------------------------------- §13, §20
        "domain": {
            "SIZES": sizes,
            "SEEDS_PER_SIZE": n_per,
            "SEEDS": {str(L): S["FRESH_OBDI01_SEEDS"][str(L)] for L in sizes},
            "TOTAL_ARMS": len(sizes) * n_per,
            "third_size_rule": W["THIRD_DOMAIN_RULE"],
            "third_size_evaluation": W["third_domain_evaluation"],
            "L_over_ell_relative": {str(L): L / P["constants"]["ell_relative"] for L in sizes},
            "L_over_r80_predicted": {str(L): L / pred[L]["r80_organiser"] for L in sizes},
        },

        # ---------------------------------------------------------------- §11
        "hypotheses": P["HYPOTHESES"],

        # ---------------------------------------------------------------- §12
        "predictions": {str(L): pred[L] for L in sizes},
        "prediction_status_layers": P["STATUS_LAYERS"],

        # ---------------------------------------------------------------- §14
        "power": {"SEEDS_PER_DOMAIN_SIZE": n_per,
                  "n_from_power": W["n_from_power"],
                  "n_from_estimability": W["n_from_estimability"],
                  "power_rule": W["POWER_RULE"],
                  "estimability_rule": W["ESTIMABILITY_FLOOR_RULE"],
                  "DOMAIN_TEST_UNDERPOWERED": W["DOMAIN_TEST_UNDERPOWERED"],
                  "prereg_sd": sd_prereg,
                  "sd_rule": ("the standard deviation used at each L is max(realised, "
                              "pre-registered). Using the realised one alone would let an "
                              "unusually tight sample widen the equivalence claim.")},

        # ---------------------------------------------------------------- §15 PRINCIPAL
        "principal_outcome": {
            "NAME": "DOMAIN_INVARIANCE_REGION",
            "form": "a SIMULTANEOUS acceptance region; every component must hold",
            "arm_summary": "median over the in-window frames, except density and winding",
            "multiplicity": {"K": K, "family_alpha": ALPHA_FAMILY,
                             "correction": "Sidak", "per_test_alpha": per_test,
                             "critical_value_c": c,
                             "two_readings": [
                                 "declaring invariance is an INTERSECTION-UNION claim: it "
                                 "requires every component to pass, so its level is the level "
                                 "of a single component and multiplicity does NOT inflate it",
                                 "failing the region when H_bound is true is a union event, and "
                                 "THAT is what the Sidak correction controls at 5 %"]},
            "components": {
                "A_shape_invariance": {
                    "statistics": ["Rg", "r80", "organiser_to_core"],
                    "construction": ("per arm y = log(observed) - log(predicted at that L); the "
                                     "predicted value already contains the exact periodic-image "
                                     "correction, so under H_bound y has NO trend in L, "
                                     "whatever L-independent bias the capacity cap introduces"),
                    "statistic": "beta = weighted least squares slope of y on log L",
                    "rule": "accept iff |beta| + c * se(beta) <= margin",
                    "margin": EQUIV_MARGIN,
                    "margin_justification": (
                        "0.25 is half the exponent of the SLOWEST unbounded alternative under "
                        "consideration (H_sublinear, alpha = 0.5). Accepting therefore excludes "
                        "every alternative in the family, not merely H_linear."),
                    "predicted_beta_under": {"H_bound": 0.0, "H_sublinear": 0.5,
                                             "H_linear": 1.0, "H_fill": 1.0}},
                "B_density_exponent": {
                    "statistic": "gamma = weighted least squares slope of log(N_X / L^2) on log L",
                    "rule": "accept iff |gamma + 2| + c * se(gamma) <= margin",
                    "margin": EQUIV_MARGIN_DENSITY,
                    "predicted_gamma_under": {"H_bound": -2.0, "H_sublinear": -1.0,
                                              "H_fill": 0.0},
                    "why": ("the population is NOT predicted by the operator — the birth rate is "
                            "a measured local quantity — so its scaling is a genuine test and "
                            "not a restatement of the profile")},
                "C_no_true_winding": {
                    "statistic": "pooled fraction of in-window frames with a topological winding",
                    "rule": "accept iff the fraction <= tolerance at EVERY domain size",
                    "tolerance": WINDING_TOLERANCE,
                    "note": ("the exact kernel produced 0 windings in 3000 draws at every "
                             "candidate L; the tolerance is far above that and still excludes "
                             "H_fill, under which winding is typical")},
                "D_profile_compatibility": {
                    "statistic": ("total variation distance between the pooled empirical radial "
                                  "mass distribution about the organiser and the exact "
                                  "predicted radial distribution"),
                    "radial_bin_edges": RADIAL_EDGES,
                    "rule": ("accept iff at least %d of the %d arms at each domain size have TV "
                             "<= the frozen envelope quantile" % (PROFILE_ARMS_REQUIRED, n_per)),
                    "arms_required": PROFILE_ARMS_REQUIRED,
                    "envelope_quantile": 0.99,
                    "envelope_n_effective_frames": None,      # filled by the freeze
                    "envelope_by_L": None},                   # filled by the freeze
            },
            "DECISION": ("DOMAIN_INVARIANCE_REGION_PASS = A and B and C and D, evaluated once, "
                         "after every planned arm has been run"),
        },

        # ---------------------------------------------------------------- §16 SECONDARY
        "secondary_endpoint": {
            "NAME": "LEGACY_D_GATE",
            "definition": ("fraction of in-window frames with r80_organiser <= "
                           "min(12.8, 0.35 L), required >= 0.95, per arm"),
            "status": "LOCKED — reported exactly as OBTC02 defined it, never retuned",
            "role": ("secondary. Its result on the new seeds is reported honestly whatever it "
                     "is, and it cannot change the principal outcome in either direction."),
            "expected_under_H_bound": ("from §8, a false-negative rate of about %.2f per arm at "
                                       "L=72 and above, rising with the number of frames; so a "
                                       "FAIL on some large-domain arms is the EXPECTED "
                                       "behaviour of this gate under a true H_bound and must "
                                       "not be read as evidence against boundedness"
                                       % json.load(open(f"{OUT}/_legacy_gate_OC.json"))["by_L"][
                                           "72"]["false_negative_rate"]),
        },

        # ---------------------------------------------------------------- §21
        "stopping": {
            "EARLY_SCIENTIFIC_STOPPING": "FORBIDDEN",
            "rule": ("every planned arm is run. No arm may be skipped, repeated, replaced or "
                     "reordered because of what an earlier arm showed."),
            "technical_abort_only": ("the run halts only if an arm is TECHNICALLY INVALID or if "
                                     "the two evaluators disagree — both are defects of the "
                                     "instrument, not results, and both are recorded as such"),
            "budget": {"confirmation_arms_planned": len(sizes) * n_per,
                       "hard_cap": len(sizes) * n_per},
        },

        # ---------------------------------------------------------------- forbidden claims
        "forbidden_claims": [
            "self-bound", "autonomous cohesion", "cell", "membrane", "identity",
            "reproduction", "memory", "H3 confirmed", "global Kamimura-Kaneko validation",
            "life", "organism", "autopoiesis", "fresh matter", "material lineage"],
        "unconditional_status": {
            "H3_STATUS": "NOT_TESTED",
            "REPRODUCTION_STATUS": "NOT_TESTED",
            "AUTONOMOUS_COHESION_STATUS": "NOT_ESTABLISHED"},
    }
    with open(f"{CODE}/obdi01_protocol.yaml", "w") as f:
        yaml.safe_dump(spec, f, sort_keys=False, width=100, allow_unicode=True,
                       default_flow_style=False)
    print("K = %d  per-test alpha = %.6f  c = %.4f" % (K, per_test, c))
    print("domain sizes", sizes, " seeds/size", n_per, " arms", len(sizes) * n_per)
    for L in sizes:
        print("  L=%-4d pred Rg=%.4f r80=%.4f d2org=%.4f density=%.6f  m2_deficit=%.2e"
              % (L, pred[L]["Rg"], pred[L]["r80"], pred[L]["organiser_to_core"],
                 pred[L]["density"], pred[L]["m2_periodic_image_deficit"]))


if __name__ == "__main__":
    main()

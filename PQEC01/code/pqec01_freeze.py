"""PQEC01 — the prospective master freeze. Written and committed ALONE, before the first
scientific start. Nothing here may be changed after any outcome is opened.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pqec01_design as D                                                    # noqa: E402

OUT = "/home/claude/edl/PQEC01/out"
CODE = os.path.dirname(os.path.abspath(__file__))


def methods_hash():
    h = hashlib.sha256()
    for f in sorted(os.listdir(CODE)):
        if f.endswith(".py"):
            h.update(f.encode())
            h.update(open(os.path.join(CODE, f), "rb").read())
    return h.hexdigest()


def main():
    b1 = D.maximin_point()
    b2 = D.b2_point(b1)
    ss = D.sample_sizes(total_cap=128, n_points=2)
    N_A = ss["PHASE_A"]["N_A"]
    N_B = ss["PHASE_B"]["N_B_PER_POINT"]

    used = set()
    seeds = {"A": D.make_seeds("A", "A0", N_A, used),
             "B1": D.make_seeds("B", "B1", N_B, used),
             "B2": D.make_seeds("B", "B2", N_B, used)}
    reserve = {k: D.make_seeds("RESERVE", k, 5, used) for k in ("A", "B1", "B2")}
    for k in seeds:
        for r in seeds[k]:
            r["split"] = D.split_of(r["seed"])
    splits = {k: {"DISCOVERY": sum(1 for r in v if r["split"] == "DISCOVERY"),
                  "VALIDATION": sum(1 for r in v if r["split"] == "VALIDATION")}
              for k, v in seeds.items()}
    all_seeds = [r["seed"] for v in seeds.values() for r in v]

    fz = {
        "PROGRAM": D.PROGRAM, "SHORT_NAME": "PQEC01",
        "PARENT_TIP": D.PARENT_TIP,
        "FREEZE_IS_COMMITTED_ALONE_BEFORE_ANY_SCIENTIFIC_START": True,
        "PQEC01_METHODS_HASH": methods_hash(),

        "SCIENTIFIC_QUESTION": (
            "Can a prospectively frozen, independently seeded calibration identify the "
            "event-aligned spatial environment encountered by one and two mobile Y lineages well "
            "enough to derive an executable (kY, muY) candidate region for a later, disjoint "
            "confirmatory test?"),

        "INDEPENDENT_UNIT": "ONE WORLD. Frames, cells, particles and event rows are never "
                            "independent experimental units.",

        "INHERITED_FROZEN_CONSTANTS": {
            "CAP": D.CAP, "S0": D.S0, "phi": D.PHI, "omega": 0.05, "muX": 0.004, "kX": 1.0,
            "L": 36, "X_SEED": 4, "p_hop_X": D.P_HOP, "p_hop_Y_mobile": D.P_HOP,
            "T_HORIZON": D.T_HORIZON, "T_WINDOW": D.T_WINDOW, "BURN_IN": D.BURN_IN,
            "CORE_R": D.CORE_R, "TAU_SEP": D.TAU_SEP, "ALPHA_SURVIVAL": D.ALPHA_SURVIVAL,
            "N_STAR": D.N_STAR, "GAMMA_SEP": D.GAMMA_SEP, "MIN_EVENTS": D.MIN_EVENTS},

        "PHASE_A": {
            "PURPOSE": "characterize the mobile source/X environment WITHOUT dynamic Y feedback",
            "kY": 0.0, "muY": 0.0, "p_hop_Y": D.P_HOP, "branch": "MOBILE",
            "X_SOURCE_LAWSPEC": "UNCHANGED (LAWSPEC_V2_EXCHANGE, frozen OBTC02 point)",
            "N_WORLDS": N_A, "LABEL": "A0",
            "RECORDS": "the full pre-reaction six-species field at EVERY step, plus all ledgers"},

        "PHASE_B": {
            "PURPOSE": ("observe real first births, co-location, movement, separation and "
                        "environmental feedback"),
            "INITIAL_CONDITION": "exactly one Y (the organiser), mobile branch, same X baseline",
            "NUMBER_OF_POINTS": 2, "N_WORLDS_PER_POINT": N_B,
            "POINT_B1": {"LABEL": "B1", "ROLE": "central maximin point",
                         "kY": b1["kY"], "muY": b1["muY"],
                         "SELECTION_RULE": b1["RULE"], "MARGINS_DECADES": b1["margins"],
                         "MIN_MARGIN_DECADES": b1["min_margin_decades"],
                         "ALL_BOUNDARIES_SATISFIED": b1["ALL_BOUNDARIES_SATISFIED"]},
            "POINT_B2": {"LABEL": "B2", "ROLE": "operator-identification point",
                         "kY": b2["kY"], "muY": b2["muY"],
                         "SELECTION_RULE": b2["RULE"],
                         "DESIGN_SCORE_EXPECTED_COLOCATED_STEPS":
                             b2["design_score_expected_colocated_steps"],
                         "MARGINS_DECADES": b2["margins"]},
            "BOTH_POINTS_FROZEN_BEFORE_PHASE_A_BEGINS": True,
            "B2_NOT_SELECTED_AFTER_SEEING_B1_OUTCOMES": True},

        "PROSPECTIVE_FINDING_DECLARED_BEFORE_ANY_RUN": {
            "STATEMENT": (
                "NO admissible (kY, muY) satisfies all five frozen boundaries simultaneously. "
                "The maximin point falls short by %.4f decades (a factor of %.2f); three "
                "boundaries are violated there at once: first-birth-not-too-rare, "
                "founder-not-extinct and no-premature-third-centre."
                % (-b1["min_margin_decades"], 10 ** (-b1["min_margin_decades"]))),
            "WHY_IT_IS_DECLARED_NOW": (
                "this is a property of the FROZEN boundary arithmetic and the parent's measured "
                "magnitudes. It is computable before a single world runs, so it is preregistered "
                "rather than discovered later. Recording it after the fact would look like a "
                "post-hoc excuse."),
            "WHAT_IT_DOES_NOT_MEAN": (
                "it is NOT structural preclusion, and it does NOT abort the calibration. PQEC01's "
                "task is to IDENTIFY the environmental operator from measured worlds, not to "
                "satisfy the window. The boundary arithmetic uses the parent's MEAN exposure as "
                "a proxy; the calibration replaces that proxy with measured, position-resolved, "
                "world-level quantities, which can move every boundary."),
            "CONSEQUENCE_PREREGISTERED": (
                "the candidate-region derivation may return an EMPTY region. That outcome is "
                "declared admissible here, in advance, and will not be treated as a failure of "
                "the calibration or as grounds for retuning.")},

        "STOP_RULES_PER_WORLD_ORDERED": [
            {"id": "EXTINCT", "condition": "N_Y == 0 (founder and all descendants gone)"},
            {"id": "PREMATURE_THIRD_CENTRE",
             "condition": "N_CENTRES(t) >= 3, where a CENTRE is a single-linkage cluster of "
                          "occupied Y cells at toroidal Euclidean distance <= CORE_R = 5.0",
             "binding": "this is the parent's frozen third-centre notion made per-world "
                        "observable; it is NOT replaced by an N_Y proxy"},
            {"id": "MAX_PERMITTED_Y", "condition": "N_Y > N_STAR = 10"},
            {"id": "INTEGRITY_FAILURE",
             "condition": "free(x) < 0 anywhere, or occupancy > CAP anywhere, or the organiser "
                          "cell cannot be located while N_Y > 0"},
            {"id": "HORIZON", "condition": "t reaches T_HORIZON = 11000"}],
        "PROXY_VARIABLES_ALSO_RECORDED_BUT_NOT_ADJUDICATIVE": ["N_Y", "max pairwise Y distance",
                                                               "number of occupied Y cells"],

        "SEED_RULE": {
            "FORMULA": "seed = 940000000 + int(SHA256(parent_tip|program|phase|point|index)"
                       "[:12], 16) mod 50000000",
            "BAND": [940000000, 989999999],
            "DISJOINT_FROM": "the OBFOR01 development band 9300000-9300027 and the "
                             "non-scientific fixture band 77000001-77900001",
            "COLLISION_RESOLUTION": "deterministic re-hash with index + 10000*bump; never manual",
            "ALL_SEEDS_PUBLISHED_IN_THIS_FREEZE": True,
            "NO_SEED_MAY_CHANGE_AFTER_OUTCOMES_ARE_OPENED": True,
            "UNIQUE_SEEDS": len(set(all_seeds)) == len(all_seeds),
            "SEEDS": seeds, "RESERVE_SEEDS_ORDERED": reserve},

        "SAMPLE_SIZE_DERIVATION": ss,

        "ANALYSIS_SPLIT": {
            "RULE": "DISCOVERY if int(SHA256('SPLIT|parent_tip|seed')[:8],16) mod 3 < 2 else "
                    "VALIDATION -- a hash of the FROZEN SEED, never of an outcome",
            "TARGET_RATIO": "two thirds discovery, one third validation",
            "REALISED": splits,
            "VALIDATION_IS_NOT_TOUCHED_UNTIL_THE_OPERATOR_IS_FROZEN": True,
            "NO_REFIT_AFTER_VIEWING_VALIDATION": True},

        "FROZEN_ANALYSIS_FORMULAS": {
            "free": "CAP - (nX+nY+nSX+nSY+nWX+nWY)",
            "candidate_Y": "min(nSY, free)", "candidate_X": "min(nSX, free)",
            "Q_POSITION": "nX * min(nSY, free)",
            "world_exposure_E_w": "mean over t in [BURN_IN, T_end) of Q at the founder cell",
            "world_low_quantile_S_w": "the 10th percentile over t in [BURN_IN, T_end) of the "
                                      "founder-cell Q",
            "branch_lower_bound": "the MINIMUM over worlds of S_w; with N >= 29 this is a 95% "
                                  "one-sided distribution-free lower bound for the 10th "
                                  "world-level percentile",
            "exact_first_birth_law": "P(no Y birth in world w) = prod_t (1 - p_t)^(c_t), with "
                                     "p_t = min(1, kY*nX_t*nY_t) and c_t = min(nSY_t, free_t) at "
                                     "the occupied Y cell -- the engine's own binomial, not an "
                                     "approximation",
            "radial_exposure": "mean of Q_POSITION over cells at toroidal distance in "
                               "[r, r+1) from the source, averaged over t, then over worlds",
            "feedback_delta": "E_B[.] - E_A[.] for nSY, free and N_X, compared at the "
                              "DISTRIBUTION level across worlds; never as a paired trajectory",
            "colocation_duration": "number of consecutive steps with >= 2 Y in one centre",
            "separation_time": "first step at which two centres exist, measured from the first "
                               "birth",
            "uncertainty": "world-level; the estimator of any branch quantity is the mean over "
                           "worlds and its standard error uses N_worlds, never N_frames"},

        "INCLUSION_RULES": {
            "EVERY_STARTED_WORLD_IS_INCLUDED": True,
            "NO_EXCLUSION_BY_OUTCOME": True,
            "EXPLICITLY_NOT_TECHNICAL_INVALIDITY": ["extinction", "no birth", "no separation",
                                                    "low Q", "high Q", "boundary contact",
                                                    "an unfavourable scientific outcome"],
            "TECHNICAL_INVALIDITY_ONLY": ["corrupt serialization", "process interruption",
                                          "observer schema failure", "checksum failure",
                                          "engine invariant violation (free < 0 or occ > CAP)"],
            "REPLACEMENT_POLICY": "a technically invalid world is replaced by the next unused "
                                  "reserve seed, in the frozen order; BOTH the failed start and "
                                  "the replacement are counted and appear in the run ledger"},

        "OUTCOME_FIREWALL": {
            "DURING_EXECUTION_THE_OPERATOR_MAY_INSPECT_ONLY":
                ["process return code", "expected file existence", "file size", "schema",
                 "checksum", "the technical-validity flags defined above"],
            "MAY_NOT_INSPECT_UNTIL_ALL_STARTS_COMPLETE":
                ["Y birth counts", "extinction", "separation", "Q", "spatial profiles",
                 "third-centre outcomes", "any primary scientific value"]},

        "TERMINAL_DISPOSITIONS": [
            "PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_IDENTIFIED",
            "PROSPECTIVE_Q_ENVIRONMENT_OPERATOR_NOT_IDENTIFIED__ADDITIONAL_INSTRUMENTATION_REQUIRED",
            "EXISTING_ARCHITECTURE_FEEDBACK_PRECLUDES_CONTROLLED_WINDOW",
            "CALIBRATION_TECHNICALLY_INVALID"],

        "DECISION_GATES_ALL_REQUIRED_FOR_THE_POSITIVE_DISPOSITION": [
            "PROSPECTIVE_FREEZE_PRECEDES_ALL_RUNS", "INSTRUMENTATION_INERTNESS",
            "ALL_FROZEN_STARTS_ACCOUNTED_FOR", "NO_OUTCOME_DRIVEN_REPLACEMENT",
            "PHASE_A_SPATIAL_OPERATOR_IDENTIFIED", "PHASE_B_REAL_DESCENDANT_EXPOSURE_RECORDED",
            "FIRST_BIRTH_OPERATOR_VALIDATED", "TWO_Y_OPERATOR_IDENTIFIED",
            "FEEDBACK_CONTROLLED_OR_EXPLICITLY_MODELLED", "INTERNAL_VALIDATION_PASS",
            "CANDIDATE_REGION_POSITIVE_WIDTH", "NO_SINGLE_WORLD_DOMINANCE",
            "NO_FRAME_PSEUDOREPLICATION"],

        "FORBIDDEN_IN_THIS_PROGRAMME": ["reproduction claim", "heredity claim",
                                        "autonomous cohesion claim", "life claim",
                                        "architecture change", "new species",
                                        "new physics state variable", "adaptive retuning",
                                        "outcome-driven seed/horizon/sample-size change",
                                        "arm replacement after scientific failure",
                                        "manuscript drafting"],
        "TOMMY_ACTION_REQUIRED": "NONE",
    }
    json.dump(fz, open(f"{OUT}/PQEC01_MASTER_FREEZE.json", "w"), indent=1, default=str)
    open(f"{OUT}/PQEC01_METHODS_HASH.txt", "w").write(fz["PQEC01_METHODS_HASH"] + "\n")
    print("METHODS_HASH", fz["PQEC01_METHODS_HASH"][:16])
    print("B1 kY=%.6g muY=%.6g  min margin %+.4f decades (all satisfied: %s)"
          % (b1["kY"], b1["muY"], b1["min_margin_decades"], b1["ALL_BOUNDARIES_SATISFIED"]))
    print("B2 kY=%.6g muY=%.6g  design score %.2f colocated steps"
          % (b2["kY"], b2["muY"], b2["design_score_expected_colocated_steps"]))
    print("N_A=%d  N_B=%d x 2  total=%d (cap 128, within: %s)"
          % (N_A, N_B, ss["TOTAL_OUTCOME_INFORMATIVE_STARTS"], ss["WITHIN_CAP"]))
    print("seeds unique:", fz["SEED_RULE"]["UNIQUE_SEEDS"], "| splits:", json.dumps(splits))
    return fz


if __name__ == "__main__":
    main()

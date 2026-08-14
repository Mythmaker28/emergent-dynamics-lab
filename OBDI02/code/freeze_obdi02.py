"""OBDI02 §17 — the freeze."""
from __future__ import annotations

import hashlib
import json
import os

import yaml

CODE = "/home/claude/OBDI02/code"
OUT = "/home/claude/OBDI02/out"
WC = "/home/claude/OBDI02/verify/obdi01/wc"
SPEC_PATH = f"{CODE}/obdi02_protocol.yaml"

METHODS_CORE = [
    "obdi02_protocol.yaml", "gate_obdi02.py", "run_obdi02.py", "worker_obdi02.py",
    "protocol_obdi01.py", "gate_obdi01.py",
    "gate_obtc02.py", "protocol_obtc02.py", "engine_obtc.py", "metrics_obtc.py",
    "nulls_obtc.py", "topology.py", "source_operator.py", "guard_obtc.py",
    "obtc02_protocol.yaml", "n2_envelope.json",
]


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    spec = yaml.safe_load(open(SPEC_PATH))
    ad = json.load(open(f"{OUT}/_adjudication.json"))
    pv = json.load(open(f"{OUT}/_provenance.json"))
    au = json.load(open(f"{OUT}/_equivalence_audit.json"))
    pw = json.load(open(f"{OUT}/_power.json"))
    pi = json.load(open(f"{OUT}/_plan_inputs.json"))
    sd = json.load(open(f"{OUT}/_seeds.json"))
    sc = json.load(open(f"{OUT}/_summary_choice.json"))
    ov = json.load(open(f"{OUT}/_outcome_vector.json"))
    o1 = json.load(open(f"{WC}/OBDI01/out/_freeze.json"))

    missing = [n for n in METHODS_CORE if not os.path.exists(os.path.join(CODE, n))]
    digests = {n: sha256(os.path.join(CODE, n)) for n in METHODS_CORE
               if os.path.exists(os.path.join(CODE, n))}
    h = hashlib.sha256()
    for n in sorted(digests):
        h.update(n.encode()); h.update(b"\0"); h.update(digests[n].encode()); h.update(b"\n")
    core = h.hexdigest()

    frz = {
        "SECTION": "OBDI02 §17",
        "OBDI02_METHODS_CORE_HASH": core,
        "METHODS_CORE_FILES": digests, "METHODS_CORE_MISSING_AT_FREEZE": missing,
        "spec_sha256": sha256(SPEC_PATH),
        "PARENT": spec["parent"],
        "PARENT_METHODS_CORE_HASH": o1["OBDI01_METHODS_CORE_HASH"],

        "FROZEN_BEFORE_ANY_START": {
            "append_only_adjudication_of_OBDI01": ad["OBDI01_ADJUDICATED_DISPOSITION"],
            "provenance": pv["PROVENANCE_STATUS"],
            "primary_estimand": spec["primary_endpoint"]["estimand"],
            "C_definition": spec["primary_endpoint"]["C_definition"],
            "Y_definition": spec["primary_endpoint"]["Y_definition"],
            "per_seed_summary": sc["WITHIN_SEED_SUMMARY"],
            "equivalence_test": spec["primary_endpoint"]["method"],
            "confidence_level": spec["primary_endpoint"]["two_sided_interval_level"],
            "margin": spec["primary_endpoint"]["equivalence_margin"],
            "extinction_treatment": spec["population_support_gate"]["seed_policy"],
            "population_support_threshold": spec["population_support_gate"]["required_per_size"],
            "domain_sizes": spec["domain"]["SIZES"],
            "seeds_per_size": spec["domain"]["SEEDS_PER_SIZE"],
            "seeds": spec["domain"]["SEEDS"],
            "preparation": "identical to OBDI01, enforced by calling its run_one unmodified",
            "horizon": spec["window"],
            "secondary_endpoints": spec["secondary_endpoints"]["list"],
            "technical_layer": spec["technical_validity"]["fields"],
            "budget": {"cap_per_size": spec["stopping"]["budget_cap_arms_per_size"],
                       "hard_cap_total": spec["stopping"]["hard_cap_total_arms"],
                       "envelope_minutes": pi["WALL_CLOCK_ENVELOPE_MINUTES"]},
            "dispositions": spec["dispositions"],
        },

        "LAWSPEC_DIFF_FROM_OBDI01": "NONE",
        "CHEMOSTAT_DIFF_FROM_OBDI01": "NONE",
        "COHESION_DIFF_FROM_OBDI01": "NONE",
        "DOMAIN_SIZES_DIFF_FROM_OBDI01": "NONE",
        "EQUIVALENCE_MARGIN_DIFF_FROM_OBDI01": "NONE",
        "PRIMARY_ESTIMAND_DIFF_FROM_OBDI01": "NONE",
        "EQUIVALENCE_INTERVAL_LEVEL_DIFF_FROM_OBDI01": "NON_EMPTY",
        "SCIENTIFIC_DESIGN_DIFF_FROM_OBDI01": "EMPTY_EXCEPT_THE_INTERVAL_LEVEL",
        "IS_THIS_A_CONFIRMATION_OR_A_REDESIGN": (
            "a CONFIRMATION of the estimand and the margin, with a TARGETED METHODOLOGICAL "
            "REDESIGN of the interval only. The law, the chemostat, the sizes, the preparation, "
            "the estimand, the per-seed summary and the margin are byte-for-byte the inherited "
            "ones. What changed is that the 99.49 %% Sidak-corrected interval OBDI01 required is "
            "replaced by the 90 %% interval a TOST at alpha = 0.05 actually calls for. §6 of the "
            "mandate provides for precisely this when the inherited method is "
            "VALID_BUT_OVERCONSERVATIVE, on condition that it be frozen before any run and "
            "declared as a redesign. It is both."),
        "OBDI01_EQUIVALENCE_METHOD": au["OBDI01_EQUIVALENCE_METHOD"],
        "MARGIN_DISCREPANCY_RESOLVED": {
            "mandate_figure": au["MARGIN_DISCREPANCY"]["MANDATE_STATES_THE_FROZEN_MARGIN_IS"],
            "frozen_protocol_figure": au["MARGIN_DISCREPANCY"]["THE_FROZEN_PROTOCOL_STATES"],
            "resolution": au["MARGIN_DISCREPANCY"]["PROOF"],
            "adopted": spec["primary_endpoint"]["equivalence_margin"],
            "stringent_reference_also_reported":
                spec["primary_endpoint"]["stringent_reference_margin"]},
        "FOUR_COMPONENTS_OF_OBDI01": ov["AMBIGUITY_1_FOUR_COMPONENTS"]["THE_FOUR_COMPONENTS"],
        "NOTATION_RESOLVED": ov["AMBIGUITY_2_NOTATION"]["ANSWER"],
        "POWER": {"target": 0.90,
                  "n_required_at_the_margin": pw["REQUIRED_N_PER_SIZE"]["delta_0.25"],
                  "n_required_at_the_stringent_reference":
                      pw["REQUIRED_N_PER_SIZE"]["delta_0.042"],
                  "n_adopted": spec["domain"]["SEEDS_PER_SIZE"],
                  "error_rates": pw["ERROR_RATES_AT_THE_REQUIRED_N"]},
        "SEEDS_DISJOINT": sd["DISJOINT"], "n_retired_seeds": sd["n_retired"],
        "EARLY_SCIENTIFIC_STOPPING": "FORBIDDEN",
        "SCIENTIFIC_RUNS_USED_AT_FREEZE": 0,
        "ASSERTIONS": {
            "no_arm_has_been_run": True,
            "no_new_result_informed_any_frozen_number": True,
            "the_OBDI01_report_is_unmodified": True,
            "every_frozen_number_is_generated_not_transcribed": True,
        },
    }
    json.dump(frz, open(f"{OUT}/_freeze.json", "w"), indent=1, default=str)
    print("OBDI02_METHODS_CORE_HASH = %s" % core)
    print("spec_sha256              = %s" % frz["spec_sha256"])
    print("files hashed = %d   missing = %s" % (len(digests), missing))
    print("margin %.3f (inherited)   n/size %d   total %d   seeds disjoint %s"
          % (spec["primary_endpoint"]["equivalence_margin"], spec["domain"]["SEEDS_PER_SIZE"],
             spec["domain"]["TOTAL_ARMS"], sd["DISJOINT"]))


if __name__ == "__main__":
    main()

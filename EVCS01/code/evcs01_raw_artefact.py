"""EVCS01 C2 — the raw, alone, before any adjudication.

Gate 0 and the composition, exactly as measured, with no interpretation attached. The sizing
instrument's frozen output is included because it is arithmetic on a frozen ledger, not a finding.
"""
from __future__ import annotations
import datetime as dt, json, os, sys
REPO = os.environ.get("EVCS01_REPO", "/home/claude/edl")
sys.path.insert(0, f"{REPO}/OMLDCT02/code"); sys.path.insert(0, f"{REPO}/EVCS01/code")
import omldct02_hashes as H
import evcs01_sizing as SZ

OUT = f"{REPO}/EVCS01/out"


def main():
    d = json.load(open(f"{REPO}/EVCS01/work/evcs01_raw.json"))
    per = sorted(d.values(), key=lambda v: (v["index"], v["arm"]))

    gate = {
        "MISSION": "EVCS01", "SECTION": "3 — gate 0, the reconstruction identity",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "WHAT_IS_COMPARED": "Model A reconstructed from LDFMA01's frozen classifier, then "
                            "E3_DURATION, E3_EXPOSURE and the interval row count recomputed under "
                            "the parent's own frozen conventions, against classifier A in "
                            "OMLDCT02_PAIR_MEASUREMENTS.json.",
        "TOLERANCE": "none. Exact integer equality on all three quantities in all 66 arms.",
        "N_ARMS": len(per),
        "N_PASS": sum(1 for v in per if v["GATE0_PASS"]),
        "DURATION_MISMATCHES": [[v["index"], v["arm"]] for v in per if not v["GATE0_DURATION_MATCHES"]],
        "EXPOSURE_MISMATCHES": [[v["index"], v["arm"]] for v in per if not v["GATE0_EXPOSURE_MATCHES"]],
        "ROW_COUNT_MISMATCHES": [[v["index"], v["arm"]] for v in per if not v["GATE0_ROWS_MATCH"]],
        "GATE0_PASS": all(v["GATE0_PASS"] for v in per),
        "WHAT_IT_LICENSES": "that the object decomposed in section 4 is bit-identical in its "
                            "aggregates to the object OMLDCT02 qualified. Without this the "
                            "decomposition would describe something else.",
    }
    gate["GATE0_CONTENT_HASH"] = H.content_digest(gate, extra_excluded=("GATE0_CONTENT_HASH",))
    json.dump(gate, open(f"{OUT}/EVCS01_GATE0_RECONSTRUCTION_IDENTITY.json", "w"), indent=1)

    def agg(arm):
        r = [v for v in per if v["arm"] == arm]
        tot = sum(v["E3_EXPOSURE_recomputed"] for v in r)
        c = sum(v["COMPOSITION"]["CERTAIN"] for v in r)
        p = sum(v["COMPOSITION"]["POSSIBLE_ONLY"] for v in r)
        n = sum(v["COMPOSITION"]["NO_CAUSAL_PATH"] for v in r)
        return {
            "n_arms": len(r), "E3_EXPOSURE_TOTAL": tot,
            "CERTAIN": c, "POSSIBLE_ONLY": p, "NO_CAUSAL_PATH": n,
            "CERTAIN_fraction": c / tot, "POSSIBLE_ONLY_fraction": p / tot,
            "NO_CAUSAL_PATH_fraction": n / tot,
            "arms_with_any_NO_CAUSAL_PATH_mass": sum(1 for v in r if v["COMPOSITION"]["NO_CAUSAL_PATH"]),
            "arms_with_any_POSSIBLE_ONLY_mass": sum(1 for v in r if v["COMPOSITION"]["POSSIBLE_ONLY"]),
            "interval_rows_carrying_zero_CERTAIN_mass": sum(v["rows_with_ZERO_CERTAIN_mass"] for v in r),
            "interval_rows_carrying_any_NO_CAUSAL_PATH_mass":
                sum(v["rows_with_any_NO_CAUSAL_PATH_mass"] for v in r),
        }

    affected = [{
        "index": v["index"], "arm": v["arm"], "t_m": v["t_m"],
        "E3_DURATION": v["E3_DURATION_recorded"], "E3_EXPOSURE": v["E3_EXPOSURE_recorded"],
        "CERTAIN": v["COMPOSITION"]["CERTAIN"], "POSSIBLE_ONLY": v["COMPOSITION"]["POSSIBLE_ONLY"],
        "NO_CAUSAL_PATH": v["COMPOSITION"]["NO_CAUSAL_PATH"],
        "NO_CAUSAL_PATH_share_of_this_arm":
            v["COMPOSITION"]["NO_CAUSAL_PATH"] / v["E3_EXPOSURE_recomputed"],
        "rows_with_any_NO_CAUSAL_PATH_mass": v["rows_with_any_NO_CAUSAL_PATH_mass"],
        "rows_with_ZERO_CERTAIN_mass": v["rows_with_ZERO_CERTAIN_mass"],
        "first_row_with_NO_CAUSAL_PATH_mass": v["first_row_with_NO_CAUSAL_PATH_mass"],
        "EXAMPLE_ROWS": v["EXAMPLE_ROWS"],
    } for v in per if v["COMPOSITION"]["NO_CAUSAL_PATH"] or v["COMPOSITION"]["POSSIBLE_ONLY"]]

    comp = {
        "MISSION": "EVCS01", "SECTION": "4 — composition of E3_EXPOSURE, threshold-free",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "THE_THREE_CLASSES": {
            "CERTAIN": "all of this cell's Y mass provably descends from the locked daughter",
            "POSSIBLE_ONLY": "a causal path exists but is not exclusive",
            "NO_CAUSAL_PATH": "no admissible source of this cell is even POSSIBLE",
        },
        "EXHAUSTIVE_AND_DISJOINT": True,
        "WHY": "CERTAIN is a subset of POSSIBLE at every row by construction, and NO_CAUSAL_PATH is "
               "the complement of POSSIBLE. Every unit of mass falls in exactly one class.",
        "OPERATOR_IMPORTED_UNCHANGED_FROM": "CLEA01/code/clea01_lineage_i2.py",
        "MODEL_A_RECONSTRUCTION_IMPORTED_UNCHANGED_FROM": "CLEA01/code/clea01_g4_containment.py",
        "NO_THRESHOLD_IS_APPLIED_ANYWHERE": True,
        "SELECTIVE": agg("SELECTIVE"), "SHAM": agg("SHAM"),
        "SELECTIVE_IS_UNINFORMATIVE_AND_THIS_WAS_DECLARED_BEFORE_THE_MEASUREMENT":
            "after the intervention the daughter is the world's only Y source, so every occupied "
            "cell descends from it by construction. A SELECTIVE composition of 100 per cent CERTAIN "
            "is the degeneracy CLEA01 already established, not evidence that the endpoint is clean. "
            "Launcher section 4 states this in advance.",
        "THE_INFORMATIVE_ARM_IS_SHAM": True,
        "AFFECTED_ARMS": affected,
        "PER_ARM": [{"index": v["index"], "arm": v["arm"],
                     "E3_DURATION": v["E3_DURATION_recorded"],
                     "E3_EXPOSURE": v["E3_EXPOSURE_recorded"],
                     "CERTAIN": v["COMPOSITION"]["CERTAIN"],
                     "POSSIBLE_ONLY": v["COMPOSITION"]["POSSIBLE_ONLY"],
                     "NO_CAUSAL_PATH": v["COMPOSITION"]["NO_CAUSAL_PATH"]} for v in per],
    }
    comp["COMPOSITION_CONTENT_HASH"] = H.content_digest(comp, extra_excluded=("COMPOSITION_CONTENT_HASH",))
    json.dump(comp, open(f"{OUT}/EVCS01_E3_COMPOSITION_RAW.json", "w"), indent=1)

    s, tests = SZ.run_self_tests()
    siz = {
        "MISSION": "EVCS01", "SECTION": "5 — the campaign sizing instrument",
        "GENERATED_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "INSTRUMENT": "EVCS01/code/evcs01_sizing.py",
        "DETERMINISTIC": True, "BOOTSTRAP_SEED": SZ.BOOTSTRAP_SEED,
        "FROZEN_OUTPUT_FOR_THE_CURRENT_DESIGN": {k: v for k, v in s.items() if not k.startswith("_")},
        "P_41_PAIRS_AT_THE_OMLDCT02_CEILING_512": s["_p512"],
        "THE_INSTRUMENT_REFUSES_512": s["_refuse512"],
        "THE_INSTRUMENT_ACCEPTS_800": s["_refuse800"],
        "SELF_TESTS": tests, "ALL_SELF_TESTS_PASS": all(t["PASS"] for t in tests),
        "TLMR01_DEVELOPMENTAL_SIZING": SZ.TLMR01_DEVELOPMENTAL_SIZING,
        "TWO_CAMPAIGNS_FROZEN_WITH_SINGLE_DIGIT_POWER": {
            "FIMRCC01": {"rule": "k >= 2 of n = 50 blocks",
                         "power_at_the_observed_rate_1_in_256": 0.0165,
                         "source": "FIMRCC01_FINAL_DISPOSITION.json LOCKED_DAUGHTER_N50_P_K_GE_2"},
            "OMLDCT02": {"rule": "41 valid paired blocks under a 512 arm-instance ceiling",
                         "power_at_the_realised_rate": s["_p512"],
                         "source": "recomputed here from OMLDCT02_SEALED_LEDGER.jsonl"},
            "COMMON_CAUSE": "a target and a cost ceiling frozen independently and never checked "
                            "against each other. This instrument exists so that check is not "
                            "optional.",
        },
        "THESE_ARE_SAMPLING_YIELD_QUANTITIES_NOT_THE_PAIRED_ENDPOINTS": True,
        "THE_OWNERS_RULE_IS_UNTOUCHED": "fewer than 41 pairs may not be interpreted using the "
                                        "paired p-values. Nothing here does.",
    }
    siz["SIZING_CONTENT_HASH"] = H.content_digest(siz, extra_excluded=("SIZING_CONTENT_HASH",))
    json.dump(siz, open(f"{OUT}/EVCS01_SIZING_INSTRUMENT.json", "w"), indent=1)

    print("GATE0_PASS =", gate["GATE0_PASS"], f"({gate['N_PASS']}/{gate['N_ARMS']})")
    for a in ("SELECTIVE", "SHAM"):
        g = comp[a]
        print(f"{a}: exposure {g['E3_EXPOSURE_TOTAL']}  CERTAIN {g['CERTAIN_fraction']:.6f}  "
              f"POSSIBLE_ONLY {g['POSSIBLE_ONLY_fraction']:.6f}  "
              f"NO_CAUSAL_PATH {g['NO_CAUSAL_PATH_fraction']:.6f}  "
              f"affected arms {g['arms_with_any_NO_CAUSAL_PATH_mass']}")
    print("sizing self-tests:", siz["ALL_SELF_TESTS_PASS"])


if __name__ == "__main__":
    main()

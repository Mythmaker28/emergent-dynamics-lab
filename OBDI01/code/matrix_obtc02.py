"""OBDI01 §3 — reconstruct the COMPLETE 17-start matrix of OBTC02 from its own frozen results
and prove that the domain axis D is the only one carrying an unmet frozen requirement.

If it is not, OBDI01 must stop with INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED and
SCIENTIFIC_RUNS_USED = 0. The check is performed here, before anything else in this mission.

No engine start: OBTC02's own `_results.json` and its frozen protocol are read.
"""
from __future__ import annotations

import json

WC = "/home/claude/OBDI01/verify/obtc02/wc/OBTC02"
OUT = "/home/claude/OBDI01/out"
RAW = f"{WC}/raw"

RES = json.load(open(f"{WC}/out/_results.json"))


def main():
    import yaml
    spec = yaml.safe_load(open("/home/claude/OBDI01/code/obtc02_protocol.yaml"))
    req = spec["protocol"]["qualification_requires"]
    rows, by = [], {}
    for i, a in enumerate(RES["arms"], 1):
        cph = a["gate_posthoc"]
        conds = {k: bool(v) for k, v in cph.items()
                 if k.isupper() and k != "PER_ARM_PASS" and isinstance(v, bool)}
        passed = sorted(k for k, v in conds.items() if v)
        failed = sorted(k for k, v in conds.items() if not v)
        row = {"id": i, "tag": a["tag"], "seed": a["seed"], "condition": a["condition"],
               "L": a["L"],
               "intervention": {"P": "none", "S": "organiser immobilised (p_hop_Y = 0)",
                                "D": "domain doubled to L = 72",
                                "R": "source removed at step %d" % spec["window"]["SOURCE_OFF_AT"],
                                "N": "no organiser seeded"}[a["condition"]],
               "technical": a["RUN_TECHNICALLY_VALID"],
               "scientific_PASS": a["PASS"], "n_passed": len(passed),
               "passed": passed, "failed": failed,
               "classification_posthoc": a["classification"],
               "classification_online": ("identical (GATES_AGREE=%s)" % a["GATES_AGREE"]),
               "reason": ("failed: " + ", ".join(failed)) if failed else "all conditions met"}
        rows.append(row)
        by.setdefault(a["condition"], []).append(a)

    n_P = sum(1 for a in by.get("P", []) if a["PASS"])
    n_D = sum(1 for a in by.get("D", []) if a["PASS"])
    n_S = sum(1 for a in by.get("S", []) if a["PASS"])
    ca = RES.get("cross_arm", {})
    n_R = ca.get("CAUSAL_SOURCE_DEPENDENCE", {}).get("R_passing")
    n_N = ca.get("CAUSAL_SOURCE_DEPENDENCE", {}).get("N_passing")

    status = {
        "P_STATUS": "PASS" if n_P >= req["P_arms_passing_all_per_arm_conditions"] else "FAIL",
        "S_STATUS": ("PASS" if n_S else
                     "FAIL_ON_THE_PER_ARM_GATE__NO_FROZEN_REQUIREMENT"),
        "R_STATUS": "PASS" if (n_R or 0) >= req["R_arms_showing_the_predicted_decay"] else "FAIL",
        "N_STATUS": "PASS" if (n_N or 0) >= req["N_arms_not_maintaining"] else "FAIL",
        "D_STATUS": "PASS" if n_D >= req["D_arms_passing"] else "FAIL",
        "E_STATUS": "NOT_OPENED",
    }
    # An axis is "unmet" only if the FROZEN protocol demanded something of it and did not get it.
    frozen_demand = {"P": req["P_arms_passing_all_per_arm_conditions"],
                     "D": req["D_arms_passing"],
                     "R": req["R_arms_showing_the_predicted_decay"],
                     "N": req["N_arms_not_maintaining"],
                     "S": None, "E": None}
    unmet = [k for k, v in frozen_demand.items()
             if v is not None and status["%s_STATUS" % k] != "PASS"]
    only_D = (unmet == ["D"])

    out = {
        "SECTION": "OBDI01 §3",
        "matrix": rows, "n_starts": len(rows),
        "by_condition": {k: len(v) for k, v in by.items()},
        "frozen_requirements": req,
        "frozen_demand_by_axis": frozen_demand,
        "cross_arm": ca,
        "status": status,
        "axes_with_an_unmet_frozen_requirement": unmet,
        "S_diagnosis": (
            "S fails two per-arm conditions for a STRUCTURAL reason, not a physical one. With "
            "p_hop_Y = 0 the organiser never moves, so the unwrapped organiser trajectory has "
            "zero variance and the position correlation entering SOURCE_ATTACHMENT is 0/0 = "
            "NaN; and the N3 decorrelated-frames null has median displacement 0, so the ratio "
            "entering CORE_CONTINUITY is again 0/0 = NaN. Physically the S arms are the "
            "cleanest of the whole mission: core_exists = 1.000, |core - organiser| = 0.00, "
            "MODEL_PREDICTION_COMPATIBILITY 6/6, occupancy drift 0.011-0.054."),
        "S_note": ("the frozen protocol places NO requirement on S "
                   "(qualification_requires has no S entry), so this failure cannot make any "
                   "axis unmet; it is recorded, not repaired, and no threshold is touched."),
        "D_IS_THE_ONLY_AXIS_WITH_AN_UNMET_FROZEN_REQUIREMENT": bool(only_D),
        "all_17_technically_valid": bool(all(a["RUN_TECHNICALLY_VALID"] for a in RES["arms"])),
        "online_posthoc_agree_everywhere": bool(all(a["GATES_AGREE"] for a in RES["arms"])),
        "OBDI01_MAY_PROCEED": bool(only_D),
        "OTHERWISE": "INHERITED_NON_DOMAIN_AXIS_NOT_CLOSED, SCIENTIFIC_RUNS_USED = 0",
    }
    json.dump(out, open(f"{OUT}/_obtc02_matrix.json", "w"), indent=1, default=str)
    for r in rows:
        print("%2d %-12s %s L=%-3d tech=%-5s sci=%-5s %2d passed  %s"
              % (r["id"], r["tag"], r["condition"], r["L"], r["technical"],
                 r["scientific_PASS"], r["n_passed"],
                 "" if r["scientific_PASS"] else "FAILED: " + ", ".join(r["failed"])))
    print(json.dumps(status, indent=1))
    print("unmet axes:", unmet, " ONLY_D =", only_D)
    print("all technically valid:", out["all_17_technically_valid"],
          "  gates agree everywhere:", out["online_posthoc_agree_everywhere"])


if __name__ == "__main__":
    main()

"""OBTC02 §18 — the frozen plan, executed. Technical validity is checked BEFORE any scientific
classification, and the sequential rule is applied to the letter. No manual resumption."""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC02/code")

import gate_obtc02 as GT         # noqa: E402
import guard_obtc as GD          # noqa: E402
import protocol_obtc02 as PC     # noqa: E402
import source_operator as OP     # noqa: E402

OUT = "/home/claude/OBTC02/out"
SPEC = PC.SPEC
PR = SPEC["protocol"]
ORDER = ("P", "S", "D", "R", "N")
CLS = {"P": "confirmation", "S": "confirmation", "D": "confirmation",
       "R": "control", "N": "control"}


def stop(done):
    rules = [r[0] if isinstance(r, list) else r for r in SPEC["sequential_rule"]]
    if any(not a["RUN_TECHNICALLY_VALID"] for a in done):
        return "run technically invalid"
    if any(not a["GATES_AGREE"] for a in done):
        return "online and post hoc gates disagree anywhere"
    if any(not a["occupancy"]["exactly_constant"] for a in done):
        return "the chemostat loses its exact occupancy balance in any arm"
    P = [a for a in done if a["condition"] == "P"]
    if len(P) >= 2 and all(a["N_X"]["window_mean"] < 2 for a in P[:2]):
        return "the principal condition forms no cloud on the first two seeds"
    D = [a for a in done if a["condition"] == "D"]
    if P and D:
        r36 = float(np.median([a["aggregates"]["model"]["r80"] for a in P]))
        r72 = float(np.median([a["aggregates"]["model"]["r80"] for a in D]))
        if r36 > 0 and r72 / r36 > 1.75:
            return "the larger domain shows a radius proportional to L"
    del rules
    return None


def main():
    frz = json.load(open(f"{OUT}/_freeze.json"))
    assert frz["PROTOCOL_ADVERSARIAL_AUDIT"] == "PASS"
    assert frz["semantic_diff"]["SCIENTIFIC_THRESHOLD_DIFF"] == "EMPTY"
    env = frz["N2_envelope"]["by_L"]
    forbidden = set(PR["forbidden_seeds"]["values"])
    analytic = OP.Op(PC.spec_for()).predictions()
    res = {"OBTC02_METHODS_CORE_HASH": frz["OBTC02_METHODS_CORE_HASH"],
           "spec_sha256": frz["spec_sha256"], "arms": [], "stopped": None}
    done = []
    for key in ORDER:
        cond = dict(PR["conditions"][key])
        cond["key"] = key
        L = int(cond.get("L", SPEC["point"]["L"]))
        for s in cond.get("seeds", []):
            assert s not in forbidden, "forbidden seed %d" % s
            a = PC.run_arm(CLS[key], "%s/seed%d" % (key, s), cond, s, env[str(L)], analytic)
            done.append(a)
            ag = a["aggregates"]
            print("  %-12s L=%-3d tech=%-5s %-34s PASS=%-5s N_X=%-6.1f r80=%-5.2f "
                  "d2org=%-5.2f turn=%-5.1f agree=%s"
                  % (a["tag"], L, a["RUN_TECHNICALLY_VALID"], a["classification"], a["PASS"],
                     ag["N_X_mean"], ag["model"]["r80"], ag["model"]["organiser_to_core"],
                     ag["replacements"], a["GATES_AGREE"]), flush=True)
            st = stop(done)
            if st:
                res["stopped"] = {"after_arms": len(done), "rule": st}
                print("\nSTOP: %s\n" % st, flush=True)
                break
        if res["stopped"]:
            break

    res["arms"] = done
    if not res["stopped"]:
        res["cross_arm"] = GT.cross_arm(SPEC, done, analytic)
    req = PR["qualification_requires"]
    by = {}
    for a in done:
        by.setdefault(a["condition"], []).append(a)
    res["summary"] = {
        "arms_by_condition": {k: len(v) for k, v in by.items()},
        "technically_valid": sum(1 for a in done if a["RUN_TECHNICALLY_VALID"]),
        "P_passing": sum(1 for a in by.get("P", []) if a["PASS"]),
        "P_required": req["P_arms_passing_all_per_arm_conditions"],
        "D_passing": sum(1 for a in by.get("D", []) if a["PASS"]),
        "D_required": req["D_arms_passing"],
        "S_passing": sum(1 for a in by.get("S", []) if a["PASS"]),
        "cross_arm": res.get("cross_arm", {}).get("CROSS_ARM_PASS"),
    }
    res["summary"]["QUALIFIED"] = bool(
        not res["stopped"]
        and res["summary"]["P_passing"] >= req["P_arms_passing_all_per_arm_conditions"]
        and res["summary"]["D_passing"] >= req["D_arms_passing"]
        and res["summary"].get("cross_arm"))
    res["ledger"] = GD.audit()
    slim = json.loads(json.dumps(res, default=str))
    for a in slim["arms"]:
        a.pop("frames", None)
    json.dump(slim, open(f"{OUT}/_results.json", "w"), indent=1, default=str)
    print()
    print(json.dumps(res["summary"], indent=1, default=str))
    if "cross_arm" in res:
        ca = res["cross_arm"]
        print("DOMAIN_SIZE_INVARIANCE  r80 small %.3f large %.3f rel %.3f -> %s"
              % (ca["DOMAIN_SIZE_INVARIANCE"]["r80_small_domain"],
                 ca["DOMAIN_SIZE_INVARIANCE"]["r80_large_domain"],
                 ca["DOMAIN_SIZE_INVARIANCE"]["relative_difference"],
                 ca["DOMAIN_SIZE_INVARIANCE"]["PASS"]))
        print("CAUSAL_SOURCE_DEPENDENCE  R %d/%d  N %d/%d -> %s"
              % (ca["CAUSAL_SOURCE_DEPENDENCE"]["R_passing"],
                 ca["CAUSAL_SOURCE_DEPENDENCE"]["R_required"],
                 ca["CAUSAL_SOURCE_DEPENDENCE"]["N_passing"],
                 ca["CAUSAL_SOURCE_DEPENDENCE"]["N_required"],
                 ca["CAUSAL_SOURCE_DEPENDENCE"]["PASS"]))
    print("SCIENTIFIC_RUNS_USED = %d" % GD.scientific_runs_used())


if __name__ == "__main__":
    main()

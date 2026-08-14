"""OBTC01 §12 and §17 — the frozen plan, and the sequential rule coded FROM the yaml.

Every stop predicate below quotes its yaml line verbatim in `rule`. No manual resumption after a
stop is permitted in this mission.
"""
from __future__ import annotations

import json
import sys

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBTC01/code")

import gate_obtc as GT           # noqa: E402
import guard_obtc as GD          # noqa: E402
import protocol_obtc as PC       # noqa: E402

OUT = "/home/claude/OBTC01/out"
SPEC = PC.SPEC
PR = SPEC["protocol"]
ORDER = ("P", "S", "D", "R", "N")
CLASS_OF = {"P": "confirmation", "S": "confirmation", "D": "confirmation",
            "R": "control", "N": "control"}


def stop_predicates(done, envelope):
    rules = SPEC["sequential_rule"]
    P = [r for r in done if r["condition"] == "P"]
    Dm = [r for r in done if r["condition"] == "D"]
    if any(not r["GATES_AGREE"] for r in done):
        return rules[3][0]
    if any(not r["occupancy"]["exactly_constant"] for r in done):
        return rules[5][0]
    if len(P) >= 2 and all(r["N_X"]["window_mean"] < 2 for r in P[:2]):
        return rules[7][0]
    if Dm and P:
        r36 = float(np.median([r["aggregates"]["model"]["r80"] for r in P]))
        r72 = float(np.median([r["aggregates"]["model"]["r80"] for r in Dm]))
        if r36 > 0 and r72 / r36 > 1.75:            # a radius proportional to L would be 2.0
            return rules[8][0]
    return None


def main():
    frz = json.load(open(f"{OUT}/_freeze.json"))
    assert frz["PROTOCOL_ADVERSARIAL_AUDIT"] == "PASS"
    assert frz["GATE_SATISFIABILITY"] == "PASS"
    envelope = frz["N2_envelope"]["by_L"]
    forbidden = set(PR["forbidden_seeds"]["values"])
    res = {"METHODS_CORE_HASH": frz["METHODS_CORE_HASH"], "spec_sha256": frz["spec_sha256"],
           "arms": [], "stopped": None}
    done = []
    for key in ORDER:
        cond = dict(PR["conditions"][key])
        cond["key"] = key
        L = int(cond.get("L", SPEC["point"]["L"]))
        env = envelope[str(L)]
        for s in cond.get("seeds", []):
            assert s not in forbidden, "forbidden seed %d" % s
            tag = "%s/seed%d" % (key, s)
            r = PC.run_arm(CLASS_OF[key], tag, cond, s, env)
            done.append(r)
            a = r["aggregates"]
            print("  %-14s L=%-3d %-38s PASS=%-5s N_X=%-6.1f r80=%-5.2f d2org=%-5.2f "
                  "turn=%-5.1f agree=%s"
                  % (tag, L, r["classification"], r["PASS"], a["N_X_mean"],
                     a["model"]["r80"], a["model"]["organiser_to_core"], a["replacements"],
                     r["GATES_AGREE"]), flush=True)
            st = stop_predicates(done, envelope)
            if st:
                res["stopped"] = {"after_arms": len(done), "rule": st}
                print("\nSTOP: %s\n" % st, flush=True)
                break
        if res["stopped"]:
            break

    res["arms"] = done
    res["ledger"] = GD.audit()
    slim = json.loads(json.dumps(res, default=str))
    for a in slim["arms"]:
        a.pop("frames", None)
    json.dump(slim, open(f"{OUT}/_results.json", "w"), indent=1, default=str)
    n_by = {}
    for r in done:
        n_by.setdefault(r["condition"], []).append(r)
    print()
    for k, v in n_by.items():
        print("  condition %s: %d arms, %d passing the per-arm gate"
              % (k, len(v), sum(1 for r in v if r["PASS"])))
    print("\nSCIENTIFIC_RUNS_USED = %d" % GD.scientific_runs_used())


if __name__ == "__main__":
    main()

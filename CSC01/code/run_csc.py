"""CSC01 §17-18 — the confirmatory plan, executed under the frozen protocol.

The sequential stopping rule is read from the yaml and implemented HERE in the same words, one
predicate per written line, so that the divergence recorded as ORR01 C-5 cannot recur.
"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/CSC01/code")

import gatelib as GL             # noqa: E402
import guard_csc as GC           # noqa: E402
import protocol_csc as PC        # noqa: E402

OUT = "/home/claude/CSC01/out"
SPEC = PC.SPEC
PR = SPEC["protocol"]


def stop_rules(pairs, arms_by_seed):
    """Every rule of the frozen list that can fire during the confirmation, in its written
    words. A rule fires only on the condition its text states."""
    reps = [p["C3_NEIGHBOUR_PROTECTED_DECAY"] for p in pairs]
    refs = [p["C0_NO_CHANGE"] for p in pairs]
    if any(r["classification"] == "COHESION_ACHIEVED" for r in refs):
        return ("5 the reference arm C0 is COHESION_ACHIEVED on any seed -> STOP, the gate does "
                "not discriminate")
    if len(pairs) >= 2 and all(r["gate_posthoc"]["formed_at"] is None for r in reps[:2]):
        return "6 no C3 arm forms on the first two seeds -> STOP"
    if len(pairs) >= 3 and all(r["classification"] in ("MATERIAL_COLLAPSE", "FROZEN_AGGREGATE")
                               for r in reps[:3]):
        return ("7 every C3 arm of the first three seeds is MATERIAL_COLLAPSE or "
                "FROZEN_AGGREGATE -> STOP")
    if any(not r["GATES_AGREE"] for r in reps + refs):
        return "2 the two gate implementations disagree anywhere -> STOP"
    return None


def main():
    frz = json.load(open(f"{OUT}/_freeze.json"))
    lam = frz["calibration"]["lambda"]
    assert frz["calibration"]["STATUS"] == "CALIBRATED"
    assert frz["PROTOCOL_ADVERSARIAL_AUDIT"] == "PASS"
    audit_pass = frz["PROTOCOL_ADVERSARIAL_AUDIT"] == "PASS"
    n1tab = GL.n1_table(SPEC)
    ARMS, CTRL = PC.arms(lam), PC.controls(lam)
    forbidden = set(PR["forbidden_seeds"])
    assert not (set(PR["seeds_confirmation"]) & forbidden)
    assert not (set(PR["seeds_control"]) & forbidden)

    res = {"METHODS_CORE_HASH": frz["METHODS_CORE_HASH"], "lambda": lam,
           "gate_spec_sha256": frz["gate_spec_sha256"], "pairs": [], "controls": [],
           "stopped": None}
    arms_by_seed = {}
    for s in PR["seeds_confirmation"]:
        pair = {}
        for name, cfg in ARMS.items():
            r = PC.run_arm("confirmation", "conf/%s/seed%d" % (name, s), cfg, s, n1tab,
                           audit_pass)
            pair[name] = r
            print("  %-30s seed=%-5d %-27s PASS=%-5s N_X win-mean=%-7.1f agree=%s"
                  % (name, s, r["classification"], r["PASS"], r["N_X"]["window_mean"],
                     r["GATES_AGREE"]), flush=True)
        arms_by_seed[s] = pair
        res["pairs"].append(pair)
        st = stop_rules(res["pairs"], arms_by_seed)
        if st:
            res["stopped"] = {"after_pairs": len(res["pairs"]), "rule": st}
            print("\nSTOP: %s\n" % st, flush=True)
            break

    n_coh = sum(1 for p in res["pairs"]
                if p["C3_NEIGHBOUR_PROTECTED_DECAY"]["classification"] == "COHESION_ACHIEVED")
    n_ref = sum(1 for p in res["pairs"]
                if p["C0_NO_CHANGE"]["classification"] != "COHESION_ACHIEVED")
    res["summary"] = {"pairs_run": len(res["pairs"]), "C3_cohesion_achieved": n_coh,
                      "C0_not_cohesion_achieved": n_ref,
                      "confirm_required": PR["confirm_required"],
                      "success": bool(n_coh >= PR["confirm_required"] and
                                      n_ref >= PR["confirm_required"])}
    print("\nCONFIRMATION over %d pairs: C3 cohesive %d, C0 not cohesive %d; criterion %d of 6 "
          "-> success = %s" % (len(res["pairs"]), n_coh, n_ref, PR["confirm_required"],
                               res["summary"]["success"]), flush=True)

    if len(res["pairs"]) >= 3 and not res["stopped"]:
        print("\ncontrols (rule 9: at least three confirmation pairs were executed)", flush=True)
        for name, cfg in CTRL.items():
            for s in PR["seeds_control"]:
                r = PC.run_arm("control", "ctrl/%s/seed%d" % (name, s), cfg, s, n1tab,
                               audit_pass)
                res["controls"].append(r)
                print("  %-16s seed=%-5d %-27s N_X max=%-6.0f final=%-6.0f agree=%s"
                      % (name, s, r["classification"], r["N_X"]["max"], r["N_X"]["final"],
                         r["GATES_AGREE"]), flush=True)

    res["ledger"] = GC.audit()
    slim = json.loads(json.dumps(res, default=str))
    for p in slim["pairs"]:
        for k in p:
            p[k].pop("frames", None)
    for c in slim["controls"]:
        c.pop("frames", None)
    json.dump(slim, open(f"{OUT}/_results.json", "w"), indent=1, default=str)
    import numpy as np
    for p in res["pairs"]:
        for k, v in p.items():
            np.savez_compressed("/home/claude/CSC01/raw/frames__%s.npz"
                                % v["tag"].replace("/", "__"),
                                frames=np.array([json.dumps(f) for f in v["frames"]]))
    print("\nSCIENTIFIC_RUNS_USED = %d" % GC.scientific_runs_used())


if __name__ == "__main__":
    main()

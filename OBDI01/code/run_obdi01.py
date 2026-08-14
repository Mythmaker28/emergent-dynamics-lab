"""OBDI01 — execute the frozen plan.

§21 NO EARLY SCIENTIFIC STOPPING. Every planned arm is run. The only halt is technical: an arm
that is not TECHNICALLY VALID, or on which the streaming and post-hoc evaluators disagree, is a
defect of the instrument and stops the run with the reason recorded. Nothing a result shows can
stop it.

The principal outcome is evaluated ONCE, after the last arm.
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import gate_obdi01 as GT           # noqa: E402
import guard_obtc as GD            # noqa: E402
import protocol_obdi01 as PR       # noqa: E402
import protocol_obtc02 as PC       # noqa: E402

OUT = "/home/claude/OBDI01/out"


def main():
    spec = GT.load()
    frz = json.load(open(f"{OUT}/_freeze.json"))
    assert frz["spec_sha256"] == GT.spec_sha256(), "the frozen spec has changed since the freeze"
    assert frz["SCIENTIFIC_RUNS_USED_AT_FREEZE"] == 0
    assert spec["stopping"]["EARLY_SCIENTIFIC_STOPPING"] == "FORBIDDEN"

    sizes = [int(x) for x in spec["domain"]["SIZES"]]
    seeds = {int(k): list(v) for k, v in spec["domain"]["SEEDS"].items()}
    hard_cap = int(spec["stopping"]["budget"]["hard_cap"])
    env_by_L = frz["N2_ENVELOPE"]["by_L"]
    analytic = PR.analytic_for()

    arms, halted = [], None
    for L in sizes:
        for s in seeds[L]:
            if len(arms) >= hard_cap:
                halted = "budget cap reached: %d arms" % hard_cap
                break
            tag = "L%d/seed%d" % (L, s)
            t0 = time.time()
            a = PR.run_one(tag, L, s, env_by_L[str(L)], analytic, spec)
            arms.append(a)
            sm = a["summary"]
            print("  %-16s L=%-3d tech=%-5s  N_X=%6.1f  Rg=%.3f  r80=%.3f  d2org=%.3f  "
                  "dens=%.5f  wind=%d  TV=%.4f  legacyD=%-5s  agree=%s  %.0fs"
                  % (tag, L, a["RUN_TECHNICALLY_VALID"], sm["N_X_mean"], sm["Rg"], sm["r80"],
                     sm["organiser_to_core"], sm["density"], a["winding_frames"],
                     a["profile_TV"], a["gate_posthoc"]["RELATIVE_LOCALIZATION"],
                     a["GATES_AGREE"], time.time() - t0), flush=True)
            if not a["RUN_TECHNICALLY_VALID"]:
                halted = "TECHNICAL: %s is not technically valid: %s" % (
                    tag, "; ".join(a["technical"]["reasons"]))
                break
            if not a["GATES_AGREE"]:
                halted = "TECHNICAL: online and post-hoc disagree on %s" % tag
                break
        if halted:
            break

    # ---------------------------------------------------------------- reduce and evaluate
    by_L = {}
    for L in sizes:
        aa = [a for a in arms if int(a["L"]) == L]
        if not aa:
            continue
        by_L[L] = {
            "values": {s: [a["summary"][s] for a in aa] for s in GT.SHAPE_STATS},
            "density": [a["summary"]["density"] for a in aa],
            "winding": (int(sum(a["winding_frames"] for a in aa)),
                        int(sum(a["window_frames"] for a in aa))),
            "profile_TV": [a["profile_TV"] for a in aa],
            "tags": [a["tag"] for a in aa],
        }

    res = {"OBDI01_METHODS_CORE_HASH": frz["OBDI01_METHODS_CORE_HASH"],
           "spec_sha256": frz["spec_sha256"], "halted": halted,
           "n_arms": len(arms), "planned_arms": spec["domain"]["TOTAL_ARMS"],
           "all_planned_arms_run": bool(len(arms) == spec["domain"]["TOTAL_ARMS"]
                                        and halted is None),
           "technically_valid": sum(1 for a in arms if a["RUN_TECHNICALLY_VALID"]),
           "gates_agree": sum(1 for a in arms if a["GATES_AGREE"]),
           "by_L": {str(k): v for k, v in by_L.items()}}

    if res["all_planned_arms_run"]:
        res["PRINCIPAL"] = GT.evaluate_principal(spec, by_L)
        res["SECONDARY"] = GT.evaluate_secondary(spec, arms)
        # cross-check: the secondary endpoint recomputed here must agree with the frozen
        # OBTC02 per-arm condition evaluated inside run_arm
        cross = [{"tag": a["tag"],
                  "obtc02_condition": bool(a["gate_posthoc"]["RELATIVE_LOCALIZATION"]),
                  "recomputed": r["PASS"]}
                 for a, r in zip(arms, res["SECONDARY"]["per_arm"])]
        res["SECONDARY"]["cross_check_against_obtc02_gate"] = {
            "rows": cross, "AGREE": bool(all(c["obtc02_condition"] == c["recomputed"]
                                             for c in cross))}
    else:
        res["PRINCIPAL"] = {"NOT_EVALUATED": "the plan did not complete", "reason": halted}

    res["ledger"] = GD.audit()
    res["SCIENTIFIC_RUNS_USED"] = GD.scientific_runs_used()

    slim = json.loads(json.dumps(res, default=str))
    json.dump(slim, open(f"{OUT}/_results.json", "w"), indent=1, default=str)

    perarm = [{k: a[k] for k in ("tag", "L", "seed", "RUN_TECHNICALLY_VALID", "GATES_AGREE",
                                 "summary", "winding_frames", "window_frames", "profile_TV",
                                 "state_hash_final", "blocked_fraction", "occupancy",
                                 "radial_observed", "radial_predicted")}
              for a in arms]
    for a, p in zip(arms, perarm):
        p["gate_posthoc_PER_ARM_PASS"] = bool(a["gate_posthoc"]["PER_ARM_PASS"])
        p["LEGACY_RELATIVE_LOCALIZATION"] = bool(a["gate_posthoc"]["RELATIVE_LOCALIZATION"])
        p["classification"] = a["classification"]
        p["r80_organiser_frames"] = a["r80_organiser_frames"]
    json.dump(perarm, open(f"{OUT}/_arms.json", "w"), indent=1, default=str)

    print("\narms run %d/%d   technically valid %d   evaluators agree %d   halted=%s"
          % (res["n_arms"], res["planned_arms"], res["technically_valid"], res["gates_agree"],
             halted))
    if "PRINCIPAL" in res and "DOMAIN_INVARIANCE_REGION_PASS" in res["PRINCIPAL"]:
        P = res["PRINCIPAL"]
        for s, d in P["components"]["A_shape_invariance"]["by_statistic"].items():
            print("  A %-18s beta=%+.4f  se=%.4f  |beta|+c.se=%.4f <= %.2f  -> %s"
                  % (s, d["beta"], d["se"], d["abs_beta_plus_c_se"], d["margin"], d["PASS"]))
        B = P["components"]["B_density_exponent"]
        print("  B density exponent  gamma=%+.4f se=%.4f  |gamma+2|+c.se=%.4f <= %.2f -> %s"
              % (B["gamma"], B["se"], B["abs_dev_plus_c_se"], B["margin"], B["PASS"]))
        print("  C winding  %s" % {k: v["fraction"] for k, v in
                                   P["components"]["C_no_true_winding"]["per_L"].items()})
        print("  D profile  %s" % {k: "%d/%d" % (v["arms_within"], v["arms_required"])
                                   for k, v in
                                   P["components"]["D_profile_compatibility"]["per_L"].items()})
        print("  DOMAIN_INVARIANCE_REGION_PASS = %s" % P["DOMAIN_INVARIANCE_REGION_PASS"])
        print("  SECONDARY legacy D gate: %s"
              % res["SECONDARY"]["LEGACY_D_GATE_ON_FRESH_SEEDS"])
    print("SCIENTIFIC_RUNS_USED = %d" % res["SCIENTIFIC_RUNS_USED"])


if __name__ == "__main__":
    main()

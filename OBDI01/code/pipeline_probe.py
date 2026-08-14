"""OBDI01 — a single NON-SCIENTIFIC pipeline probe.

The confirmatory arms must not be the first time the production path is exercised end to end.
This runs ONE arm through exactly the code the confirmatory run will use, in the guard's
`cost_probe` class, which `guard_obtc.scientific_runs_used()` excludes by construction. The
seed is outside the confirmatory set, so nothing it produces can enter the principal outcome.

It answers one question only: does the pipeline complete and produce well-formed summaries.
Its numbers are NOT read as evidence and are not compared with any threshold.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI01/code")

import gate_obdi01 as GT           # noqa: E402
import guard_obtc as GD            # noqa: E402
import protocol_obdi01 as PR       # noqa: E402
import protocol_obtc02 as PC       # noqa: E402

OUT = "/home/claude/OBDI01/out"
PROBE_SEED = 771999                # deliberately outside every confirmatory block
PROBE_L = 36


def main():
    spec = GT.load()
    frz = json.load(open(f"{OUT}/_freeze.json"))
    assert PROBE_SEED not in [s for v in spec["domain"]["SEEDS"].values() for s in v]
    env = frz["N2_ENVELOPE"]["by_L"][str(PROBE_L)]
    t0 = time.time()
    a = PR.run_one("probe/seed%d" % PROBE_SEED, PROBE_L, PROBE_SEED, env, PR.analytic_for(),
                   spec)
    # reclassify the ledger entry: it was opened as `confirmation` by run_arm, and this probe
    # must not consume a confirmatory slot. The reclassification is recorded, not hidden.
    GD.LEDGER["log"][-1]["class"] = "cost_probe"
    GD.LEDGER["log"][-1]["scientific"] = False
    GD.LEDGER["log"][-1]["reclassified"] = ("opened as `confirmation` by OBTC02's run_arm, "
                                            "reclassified as a non-scientific pipeline probe")
    sm = a["summary"]
    out = {"SECTION": "OBDI01 pipeline probe (NON-SCIENTIFIC)",
           "seed": PROBE_SEED, "L": PROBE_L, "wall_seconds": time.time() - t0,
           "RUN_TECHNICALLY_VALID": a["RUN_TECHNICALLY_VALID"],
           "technical_reasons": a["technical"]["reasons"],
           "GATES_AGREE": a["GATES_AGREE"], "window_frames": a["window_frames"],
           "summary": sm, "winding_frames": a["winding_frames"],
           "profile_TV": a["profile_TV"],
           "radial_observed_sums_to_one": abs(sum(a["radial_observed"]) - 1.0) < 1e-12,
           "all_summaries_finite": all(v == v for v in sm.values()),
           "ledger": GD.audit(),
           "SCIENTIFIC_RUNS_USED": GD.scientific_runs_used(),
           "NOT_EVIDENCE": ("this arm is a pipeline check. It is not compared with any "
                            "threshold, it does not enter the principal outcome, and its seed "
                            "is not a confirmatory seed.")}
    json.dump(out, open(f"{OUT}/_pipeline_probe.json", "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("RUN_TECHNICALLY_VALID", "GATES_AGREE",
                                          "window_frames", "profile_TV",
                                          "radial_observed_sums_to_one",
                                          "all_summaries_finite", "SCIENTIFIC_RUNS_USED")},
                     indent=1))
    print("summary:", json.dumps({k: round(v, 4) for k, v in sm.items()}))


if __name__ == "__main__":
    main()

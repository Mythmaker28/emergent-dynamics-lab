"""OBDI02 — one arm, one process.

The arm is produced by calling OBDI01's own `protocol_obdi01.run_one`, which calls OBTC02's own
`run_arm`, both unmodified. Running one arm per process is what allows the two available CPUs
to be used; it changes nothing about the arm, since every arm is seeded independently and the
guard ledger is per start. The per-process ledger entries are consolidated by the driver.

Usage: python3 worker_obdi02.py <L> <seed> <outdir>
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, "/home/claude/ORR01/code")
sys.path.insert(0, "/home/claude/OBDI02/code")

import numpy as np                 # noqa: E402
import yaml                        # noqa: E402

import protocol_obdi01 as PR       # noqa: E402
import guard_obtc as GD            # noqa: E402

O1SPEC = "/home/claude/OBDI02/verify/obdi01/wc/OBDI01/code/obdi01_protocol.yaml"
FREEZE01 = "/home/claude/OBDI02/verify/obdi01/wc/OBDI01/out/_freeze.json"


def main():
    L, seed, outdir = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    PR.RAW = os.path.join(outdir, "raw")
    PR.PC.RAW = PR.RAW
    os.makedirs(PR.RAW, exist_ok=True)
    spec01 = yaml.safe_load(open(O1SPEC))
    env = json.load(open(FREEZE01))["N2_ENVELOPE"]["by_L"][str(L)]
    tag = "L%d/seed%d" % (L, seed)
    t0 = time.time()
    a = PR.run_one(tag, L, seed, env, PR.analytic_for(), spec01)
    sm = a["summary"]
    rec = {
        "tag": tag, "L": L, "seed": seed, "wall_seconds": time.time() - t0,
        "RUN_TECHNICALLY_VALID": bool(a["RUN_TECHNICALLY_VALID"]),
        "technical": a["technical"], "GATES_AGREE": bool(a["GATES_AGREE"]),
        "gate_differences": a["gate_differences"],
        "window_frames": a["window_frames"], "winding_frames": a["winding_frames"],
        "summary": sm, "profile_TV": a["profile_TV"],
        "radial_observed": a["radial_observed"], "radial_predicted": a["radial_predicted"],
        "state_hash_final": a["state_hash_final"], "occupancy": a["occupancy"],
        "blocked_fraction": a["blocked_fraction"], "N_X": a["N_X"],
        "molecular": {k: a["molecular"][k] for k in
                      ("replacements", "initial_still_present", "final_born_in_window",
                       "mean_lifetime_steps", "tracker_consistent_with_counts")},
        "gate_posthoc_PER_ARM_PASS": bool(a["gate_posthoc"]["PER_ARM_PASS"]),
        "LEGACY_RELATIVE_LOCALIZATION": bool(a["gate_posthoc"]["RELATIVE_LOCALIZATION"]),
        "classification": a["classification"],
        "mean_free_at_organiser": a["aggregates"]["mean_free_org"],
        "r80_organiser_frames": a["r80_organiser_frames"],
        "EXTINCT": bool(not np.isfinite(sm["organiser_to_core"]) or sm["N_X_mean"] <= 0),
        "ledger": GD.audit(),
    }
    with open(os.path.join(outdir, "arm_%d_%d.json" % (L, seed)), "w") as f:
        json.dump(rec, f, default=str)
    print("%s L=%d tech=%s agree=%s NX=%.1f dCY=%s TV=%s %.0fs"
          % (tag, L, rec["RUN_TECHNICALLY_VALID"], rec["GATES_AGREE"], sm["N_X_mean"],
             sm["organiser_to_core"], rec["profile_TV"], rec["wall_seconds"]), flush=True)


if __name__ == "__main__":
    main()

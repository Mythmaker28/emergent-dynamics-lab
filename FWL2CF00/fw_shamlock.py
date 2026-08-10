"""FWL2CF00 Section 4.2 -- the SHAM RECONSTRUCTION LOCK. Written before the first replay.
No engine is instantiated here."""
from __future__ import annotations
import json, hashlib, sys, platform, os
OUT = "/home/claude/sweep/FWL2CF00"; W2 = "/home/claude/sweep/WL2SMF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
BIND = json.load(open(f"{OUT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
FZ = json.load(open(f"{OUT}/FWL2CF00_MASTER_FREEZE_HASHES.json"))
TWIN = json.load(open(f"{W2}/SHAM_TWIN_FULL_HORIZON_ORACLE.json"))
import numpy
ENV = {"python": sys.version.split()[0], "numpy": numpy.__version__,
       "platform": platform.platform(), "implementation": platform.python_implementation()}
ENGINE = {p: sha(f"/home/claude/sweep/{p}") for p in
          ("PPAI/ppai_engine.py", "edlab/substrates/scaffold/engine.py", "DOMC/domc_core.py",
           "WSFSCRP00/wsfscrp_core.py", "PPAI/ppai_core.py", "ETCMNFC/etcmnfc_core.py")}
D = {d["descendant_id"]: d for d in BIND["descendants"]}
CK = f"{W2}/checkpoints"
LOCK = {
 "purpose": "WL2SMF00 did not persist X_A[SHAM_0,d,h] / X_B[SHAM_0,d,h]. The active response "
            "cannot be formed without that reference. This successor authorises exactly one "
            "canonical sham replay per sealed descendant: 16 starts. It is a NEW successor budget, "
            "not a retroactive top-up of the parent's exhausted sham tranche, and it may not be "
            "used to estimate noise or to recalibrate any threshold.",
 "n_replays": 16, "sham_1_rerun": False, "third_twin": False, "retries": 0,
 "canonical_sham_executable": "identity copy, st.copy(), serializer role SHAM_0",
 "schedule": BIND["sham_schedule"],
 "descendants": {k: {"checkpoint_file": f"d_{k}.npz", "mask_file": f"m_{k}.npz",
                     "checkpoint_sha_full_state": v["checkpoint_sha"],
                     "checkpoint_file_sha256": sha(f"{CK}/d_{k}.npz"),
                     "mask_file_sha256": sha(f"{CK}/m_{k}.npz"), "mask_sha": v["mask_sha"],
                     "B_exact": v["B"],
                     "RHO_MED_exact": BIND["thresholds"][k]["RHO_MED"],
                     "G2_sq_exact": BIND["thresholds"][k]["G2"],
                     "TAU_MATERIAL_L2_sq_exact": BIND["thresholds"][k]["TAU_MATERIAL_L2_sq_exact"],
                     "ETA_ORACLE_L2": 0,
                     "expected_terminal_full_state_sha": None}
                 for k, v in sorted(D.items())},
 "expected_terminal_hash_note": "WL2SMF00's twin oracle recorded terminal-hash IDENTITY between "
                                "SHAM_0 and SHAM_1 but did not serialise the digest itself. The "
                                "replay's terminal hash is therefore checked for internal "
                                "consistency and against the exact locked aggregate scalars "
                                "(B, RHO_MED, G2^2, TAU^2), which are byte-derived from the same "
                                "trajectory. This is declared, not glossed.",
 "parent_twin_oracle": {"all_pass": TWIN["all_pass"], "n": TWIN["n"]},
 "physical_times": BIND["H_GRID"], "weights": BIND["weights"],
 "reader": {"module": "WSFSCRP00/wsfscrp_core.py", "sha256": ENGINE["WSFSCRP00/wsfscrp_core.py"],
            "normalizer": "B_of = dsum(rho[MA|MB]) exact rational", "horizon": 400,
            "scheduler": "Z.engine() = PPAIEngine(SPEC, PPAIParams(gain=1/3, z_index=0), TRACER)"},
 "engine_module_hashes": ENGINE, "environment": ENV,
 "worker": {"file": "fw_worker.py", "sha256": sha(f"{OUT}/fw_worker.py"),
            "one_continuation_per_fresh_process": True,
            "write_only_wrt_science": True,
            "overwrite_forbidden": True},
 "output_schema": {"npz": "rho stacked over [t0] + H_GRID, plus MA, MB",
                   "meta": "<out>.meta.json with per-time and terminal full-state hashes, "
                           "touch set, B, mask sha and input-sha-before/after",
                   "paths": [f"sham/{k}.npz" for k in sorted(D)]},
 "acceptance": ["B == locked B exactly", "RHO_MED == locked RHO_MED exactly",
                "G2^2 == locked G2^2 exactly",
                "TAU_MATERIAL_L2^2 recomputed ONLY as an oracle == locked value exactly",
                "production reader == independent reference reader exactly",
                "masks, normalizer, times, weights, horizon unchanged",
                "finite complete series for all 16",
                "input checkpoint sha unchanged before and after"],
 "operative_threshold": "the PARENT-LOCKED threshold, even after exact reproduction",
 "mismatch_disposition": "SHAM_BASELINE_RECONSTRUCTION_MISMATCH",
 "incomplete_disposition": "SHAM_RECONSTRUCTION_INCOMPLETE",
 "master_freeze_sha256": FZ["hashes"]["FWL2CF00_MASTER_FREEZE.md"],
 "binding_manifest_sha256": FZ["hashes"]["PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"],
 "oracle_report_sha256": sha(f"{OUT}/PREEXECUTION_NONVACUOUS_ORACLE_REPORT.json"),
}
json.dump(LOCK, open(f"{OUT}/FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json", "w"), indent=1)
print("SHAM RECONSTRUCTION LOCK sha:", sha(f"{OUT}/FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json")[:16])
print("env:", ENV["python"], "numpy", ENV["numpy"], "| 16 descendants bound")

"""FWL2CF00 -- CANONICAL SHAM SERIES LOCK + ACTIVE PANEL LOCK. No engine. Zero active outcome."""
from __future__ import annotations
import json, hashlib, os, sys, platform
OUT = "/home/claude/sweep/FWL2CF00"; W2 = "/home/claude/sweep/WL2SMF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
BIND = json.load(open(f"{OUT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json"))
SL = json.load(open(f"{OUT}/FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json"))
OR = json.load(open(f"{OUT}/SHAM_RECONSTRUCTION_EXACT_ORACLE.json"))
RB = json.load(open(f"{OUT}/SHAM_DISK_READBACK_CERTIFICATE.json"))
assert OR["DISPOSITION"] == "SHAM_REFERENCE_RECONSTRUCTION_PASS_16_OF_16"

man = sorted(f for f in os.listdir(f"{OUT}/sham"))
json.dump({"directory": "FWL2CF00/sham",
           "files": [{"name": f, "sha256": sha(f"{OUT}/sham/{f}"),
                      "bytes": os.path.getsize(f"{OUT}/sham/{f}")} for f in man],
           "contents": "per descendant: rho stacked over [t0] + the 10 scored times, the two "
                       "immutable masks, and a meta file carrying per-time and terminal full-state "
                       "hashes, the touch set, B, the mask sha and the input sha before/after."},
          open(f"{OUT}/SHAM_0_RECONSTRUCTED_RAW_MANIFEST.json", "w"), indent=1)

CS = {"n_descendants": 16, "starts_used": 16, "cap": 16, "retries": 0,
      "reconstruction_disposition": OR["DISPOSITION"],
      "exact_match_against_locked_scalars": OR["ALL_EXACT_MATCH"],
      "independent_disk_readback": RB["all_pass"],
      "identity_argument": OR["identity_argument"],
      "series_file": "sham_series.json", "series_sha256": sha(f"{OUT}/sham_series.json"),
      "raw_manifest_sha256": sha(f"{OUT}/SHAM_0_RECONSTRUCTED_RAW_MANIFEST.json"),
      "exact_oracle_sha256": sha(f"{OUT}/SHAM_RECONSTRUCTION_EXACT_ORACLE.json"),
      "readback_sha256": sha(f"{OUT}/SHAM_DISK_READBACK_CERTIFICATE.json"),
      "reconstruction_lock_sha256": sha(f"{OUT}/FWL2CF00_SHAM_RECONSTRUCTION_LOCK.json"),
      "operative_threshold": "PARENT-LOCKED, unchanged; the replay recomputation is an oracle only",
      "PARENT_THRESHOLDS_RECOMPUTED_OR_CHANGED": False}
json.dump(CS, open(f"{OUT}/FWL2CF00_CANONICAL_SHAM_SERIES_LOCK.json", "w"), indent=1)

ARM = BIND["arm_lock"]
AP = {
 "parent_provenance_sha256": sha(f"{OUT}/_provenance_raw.json"),
 "master_freeze_sha256": sha(f"{OUT}/FWL2CF00_MASTER_FREEZE.md"),
 "canonical_sham_series_lock_sha256": sha(f"{OUT}/FWL2CF00_CANONICAL_SHAM_SERIES_LOCK.json"),
 "descendants": BIND["descendants"],
 "ancestry_graph": {b: [d["descendant_id"] for d in BIND["descendants"] if str(d["seed"]) == b]
                    for b in sorted({str(d["seed"]) for d in BIND["descendants"]})},
 "independent_ancestry_blocks": 4,
 "design_G1": "seed x {NEAR,FAR}, geometry manipulated within ancestry",
 "design_H3": "neutral complementary-allocation members a=0,1; no physical sign; no cross-geometry "
              "anchoring of the labels",
 "arms": {"CARRIER_1": {**ARM["CARRIER_1"], "worker_expect_callable": "etcmnfc_core.transpose(st, I, J)",
                        "EXPECT_STRUCTURAL_ZERO_AT_H0": True},
          "CARRIER_2": {**ARM["CARRIER_2"], "worker_expect_callable": "ppai_core.state_cross(st)",
                        "EXPECT_STRUCTURAL_ZERO_AT_H0": True}},
 "structural_zero_proof": "both arms write Mf only and never rho; the reader integrates rho over "
                          "the immutable t0 masks; therefore X_A/X_B at h0 are identical to the "
                          "sham's and r(h0) = (0,0) exactly. The worker records the t0 touch set "
                          "and the rho-untouched flag for every arm as a runtime guard.",
 "reader": SL["reader"], "engine_module_hashes": SL["engine_module_hashes"],
 "environment": SL["environment"],
 "weights": BIND["weights"], "H_GRID": BIND["H_GRID"],
 "schedule_32": [list(x) for x in BIND["active_schedule"]], "opaque_ids": BIND["opaque_ids"],
 "no_warm_start": "every active arm starts from its sealed checkpoint bytes, never from a sham "
                  "terminal state; the input hash is checked before and after each continuation",
 "fresh_process_per_continuation": True, "overwrite_forbidden": True,
 "acquisition_driver_is_write_only_wrt_science": True,
 "estimands": {
   "cell": "PASS iff lower(M2^2) > upper(TAU_MATERIAL_L2^2); equality is FAILURE",
   "quotient": "R0,R1,R2 over all 2^15 linked descendant swaps; I1=R0-R1, I2=R1-R2; "
               "QDIM0 lower(R0)>upper(E_TAU); QDIM1 lower(sqrt(I2))>upper(A_TAU); "
               "QDIM2 lower(I2/I1)>0.01; QDIM3 lower(I2/R0)>=0.05",
   "one_family": "upper(R1/R0)<0.05 and every row upper(cell residual)<0.10, over EVERY co-optimal M1",
   "alpha": "1/32 per response row; n stays 4 ancestry blocks",
   "E_TAU_exact": BIND["E_TAU_exact"],
   "KAPPA_TWO_ARM": "1/sqrt(2), paired with the smaller floor TAU_d0+TAU_d1",
   "TAU_CONTRAST": "sum_i |c_i| TAU_i for normalised c, PLUS sector only",
   "MINUS_sector_bounds": "TRANSFORMED_BOUND_NOT_QUALIFIED (parent: PROJECTIVE_EMBEDDING_BOUND = "
                          "NOT_AVAILABLE, H3_K_BOUND = NOT_AVAILABLE)",
   "allocation_label_gauge": "2^8 independent allocation-member exchanges, one per (block,geometry)",
   "FROZEN_FACTOR_PIPELINE_STATUS": "PARENT_OBJECT_NOT_EVALUABLE",
   "FRESH_STRATUM_TRANSFER": "NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT",
 },
 "thresholds_locked": {k: v["TAU_MATERIAL_L2_sq_exact"] for k, v in BIND["thresholds"].items()},
 "code_hashes": {f: sha(f"{OUT}/{f}") for f in ("fw_prod.py", "fw_ref.py", "fw_worker.py",
                                                "fw_readback.py", "fw_oracle.py")},
 "rules": {"retries": 0, "replacements": 0, "top_ups": 0,
           "budget": {"sham": 16, "active": 32, "setup": 0, "total_max": 48},
           "no_label_decode_before_the_raw_panel_lock_is_committed_and_read_back": True},
}
json.dump(AP, open(f"{OUT}/FWL2CF00_ACTIVE_PANEL_LOCK.json", "w"), indent=1)
print("CANONICAL SHAM SERIES LOCK:", sha(f"{OUT}/FWL2CF00_CANONICAL_SHAM_SERIES_LOCK.json")[:16])
print("ACTIVE PANEL LOCK        :", sha(f"{OUT}/FWL2CF00_ACTIVE_PANEL_LOCK.json")[:16])

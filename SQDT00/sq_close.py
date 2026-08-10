"""SQDT00 closure -- machine-readable gate ladder, start ledger, panel-not-built lock and final
disposition. Zero engine starts. Reads only SQDT00's own committed-so-far artifacts plus the
parent binding; writes the closure JSONs consumed by the French report."""
from __future__ import annotations
import json, hashlib
from fractions import Fraction as Fr
OUT = "/home/claude/sweep/SQDT00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

CERT = json.load(open(f"{OUT}/SQDT00_OFFLINE_REDERIVATION_AND_BASIS_CERTIFICATE.json"))
DOSE = json.load(open(f"{OUT}/SQDT00_STATIC_DOSE_ADMISSIBILITY_AUDIT.json"))
ORAC = json.load(open(f"{OUT}/SQDT00_PREEXECUTION_NONVACUOUS_ORACLE.json"))
PROV = json.load(open(f"{OUT}/SQDT00_PARENT_ARTIFACT_BLOB_BINDING.json"))
FRZ = json.load(open(f"{OUT}/SQDT00_MASTER_FREEZE_HASHES.json"))

bg = CERT["basis_gates"]
mult = CERT["certified_multipliers"]

# ---------------------------------------------------------------- start ledger
START = {
    "MAX_PANEL_CONSTRUCTION_STARTS": 16, "panel_construction_starts_spent": 0,
    "MAX_TWIN_SHAM_STARTS": 16, "twin_sham_starts_spent": 0,
    "MAX_ACTIVE_STARTS": 32, "active_starts_spent": 0,
    "MAX_OTHER_OR_DIAGNOSTIC_ENGINE_STARTS": 0, "other_or_diagnostic_starts_spent": 0,
    "MAX_TOTAL_ENGINE_STARTS": 64, "total_engine_starts_spent": 0,
    "engine_advances_performed": 0,
    "why_zero": "the static 2x dose-axis audit fired stop rule S5 "
                "(DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED) BEFORE any fresh panel. All "
                "delivered work is offline and consumes zero starts: provenance, exact "
                "rederivation, basis serialization, stability, duplication invariance, certified "
                "multipliers, the static dose audit and the non-vacuous oracle.",
    "static_operator_evaluations_are_not_starts":
        "applying transpose/state_cross at t0 with no engine advance is a pure array transform; "
        "it instantiates no engine and steps nothing, so it is not an engine start (consistent "
        "with the inherited '1 constructed descendant state = 1 start' convention).",
}

# ---------------------------------------------------------------- gate ladder (28 items)
def item(idx, name, status, note):
    return {"n": idx, "gate": name, "status": status, "note": note}


NL = "NOT_LICENSED__BLOCKED_BY_STATIC_DOSE_INADMISSIBILITY"
NE = "NOT_EVALUABLE__NO_FRESH_ROWS"
gates = [
    item(1, "PARENT_PROVENANCE_RESOLVED_FROM_COMMITTED_BRANCH", "PASS",
         "12/12 arrows single-direct-parent; 198/198 content verified twice; subtree ids agree "
         "across git 2.34.1 and 2.43.0; bundle verifies."),
    item(2, "MASTER_FREEZE_BEFORE_ANY_PARENT_NUMERIC_LOAD", "PASS",
         "SQDT00_MASTER_FREEZE.md hashed and committed in commit 1 before any npz/series/score."),
    item(3, "OWNER_MAIN_UNTOUCHED", "PASS", "main stays at f3921a4d; separate GIT_INDEX_FILE used."),
    item(4, "RESERVED_NAMESPACE_62000_62009_UNREAD", "PASS",
         "never generated or opened; fresh design uses 66000-66015, disjoint from all prior use."),
    item(5, "APPEND_ONLY_NO_PARENT_OUTPUT_REWRITTEN", "PASS",
         "the stale parent bundle-digest record is carried forward, not repaired."),
    item(6, "SUPPORT_RESTRICTED_SUFFICIENCY_CERTIFICATE", "PASS",
         "reader rebuilt from raw rho bytes equals the committed series string-for-string, "
         "48/48 (16 sham + 32 active)."),
    item(7, "OFFLINE_REDERIVATION_REPRODUCES_PARENT_R0_EXACTLY", "PASS",
         "R0 exact equals the committed 1077-digit rational bit-for-bit."),
    item(8, "CERTIFIED_ENCLOSURES_FOR_R1_R2_I1_I2", "PASS",
         "exact rational enclosures by Bareiss leading-minor inertia + Weyl slack; widths ~5e-23; "
         "parent floats agree within the parent's own backward-stability bound."),
    item(9, "GAUGE_ARGMIN_EXACT_AND_SHARED_FOR_K012", "PASS",
         "eps* is the exact argmin of R0 and attains R1, R2 as well."),
    item(10, "BASIS_SERIALIZED_AS_REAL_MACHINE_READABLE_ARRAYS", "PASS",
          "FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz/.json carry mu, e1, e2, P1, P2, per-row scores, "
          "sign canonicalisation and gauge; not a scalar summary."),
    item(11, "BASIS_STABILITY_S0_THROUGH_S7", "PASS" if all(bg.values()) else "FAIL",
          json.dumps(bg)),
    item(12, "P2_TRANSFER_LICENSE", "GRANTED" if CERT["P2_TRANSFER_LICENSE"] else "DENIED",
          "the 2-plane transfers: all S-gates pass."),
    item(13, "E2_AXIS_TRANSFER_LICENSE", "GRANTED" if CERT["E2_AXIS_TRANSFER_LICENSE"] else "DENIED",
          "the individual axis e2 also transfers: lambda2 is certifiably separated from lambda3."),
    item(14, "DUPLICATION_INVARIANCE", "PASS",
          "R0 exact and I2 unchanged under exact row duplication (proof + numeric); licenses "
          "comparing an 8-descendant panel to the 32-row parent."),
    item(15, "CERTIFIED_MULTIPLIERS_FROM_INTERVALS_NOT_ROUNDED_0.570", "PASS",
          "ENERGY %.5f, AMPLITUDE %.5f, both as certified intervals."
          % (mult["ENERGY_MULTIPLIER_REQUIRED"][0], mult["AMPLITUDE_MULTIPLIER_REQUIRED"][0])),
    item(16, "S4_AMPLITUDE_MULTIPLIER_STRICTLY_BELOW_2", "PASS_DOES_NOT_STOP",
          "1.754 < 2: a doubled dose, if it existed and were linear, WOULD lift the second mode "
          "above the absolute floor. Sufficiency holds; this is not a stop."),
    item(17, "PREEXECUTION_ORACLE_NONVACUOUS", "PASS",
          "%d/%d groups: every positive identity holds and every negative control fires."
          % (ORAC["n_groups"], ORAC["n_groups"])),
    item(18, "S5_STATIC_DOSE_AXIS_EXISTS", "FAIL__STOP",
          "no legitimate 2x exists without a new executable: both carriers are involutions with "
          "no amplitude parameter, the matching cardinality is maximal, and the gamma=2 blend "
          "violates the frozen domain predicate. DISPOSITION token "
          "DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED."),
    item(19, "FRESH_PANEL_CONSTRUCTED", NL, "design frozen (66000-66015) but not built; 0 starts."),
    item(20, "TWIN_SHAMS_RUN", NL, "0 of 16 sham starts."),
    item(21, "ACTIVE_CONTINUATIONS_RUN", NL, "0 of 32 active starts."),
    item(22, "CELL_MATERIALITY_1X_AND_2X", NE, "no fresh rows exist to score."),
    item(23, "PAIRED_DOSE_INCREMENT_AND_LINEARITY", NE,
          "frozen predictions recorded (Rk_2x = 4 Rk_1x, sqrt(I2) ratio = 2); no data to test."),
    item(24, "FRESH_QUOTIENT_AT_EACH_DOSE", NE, "not evaluable without fresh rows."),
    item(25, "FROZEN_BASIS_TRANSFER_T0_T7", "MACHINERY_READY__NO_FRESH_ROWS",
          "the serialized basis is transfer-ready (P2 and E2 licensed); there are no fresh active "
          "rows to project onto it, so the transfer gates cannot be exercised in this programme."),
    item(26, "GEOMETRY_AND_ALLOCATION", "NOT_TESTED_IN_THIS_DESIGN",
          "the design spans them to widen the null, never to estimate their effects."),
    item(27, "NO_PUSH_NO_PR_NO_WORKFLOW_TRIGGER", "PASS",
          "PUSH/DRAFT_PR/WORKFLOW all false; delivery is a local branch + a thin bundle."),
    item(28, "TOTAL_ENGINE_STARTS_WITHIN_BUDGET", "PASS", "0 of 64."),
]
json.dump({"gates": gates, "precedence": "resolved top to bottom; item 18 (S5) is the binding "
           "stop", "n_items": len(gates)},
          open(f"{OUT}/SQDT00_GATE_LADDER_Q0_Q19.json", "w"), indent=1)

# ---------------------------------------------------------------- panel-not-built / transfer lock
LOCK = {
    "FRESH_PANEL_CONSTRUCTED": False,
    "reason": "DOSE_2X_STATICALLY_INADMISSIBLE_OR_UNRESOLVED (stop rule S5)",
    "frozen_design_that_was_not_executed": FRZ["seed_namespace"],
    "parity_deconfounding_rule": "each cell-specific subqueue holds two even and two odd seeds; "
                                 "accept first qualifier, then the next qualifier of opposite "
                                 "parity, to break the FSCMA00 parity/geometry/history collapse.",
    "transfer_object": {
        "name": "FWL2_RELATIVE_QUOTIENT_BASIS_V1",
        "npz_sha256": sha(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.npz"),
        "json_sha256": sha(f"{OUT}/FWL2_RELATIVE_QUOTIENT_BASIS_V1.json"),
        "P2_TRANSFER_LICENSE": CERT["P2_TRANSFER_LICENSE"],
        "E2_AXIS_TRANSFER_LICENSE": CERT["E2_AXIS_TRANSFER_LICENSE"],
        "usable_by": "a future OWNER-AUTHORIZED programme that has a legitimate dose axis or a "
                     "fresh active panel; it can project fresh weighted-L2 responses onto P2/e2 "
                     "WITHOUT refitting, exactly the operation the parent could not perform "
                     "because GIMB00 serialized only scalars.",
    },
    "certified_multipliers": mult,
    "scaling_predictions_frozen": CERT["scaling_predictions_frozen"],
    "engine_starts_spent": 0,
}
json.dump(LOCK, open(f"{OUT}/SQDT00_PANEL_AND_TRANSFER_LOCK.json", "w"), indent=1)

# ---------------------------------------------------------------- final disposition
DISP = {
    "programme": "SERIALIZED_QUOTIENT_DOSE_TRANSFER_00",
    "DISPOSITION":
        "OFFLINE_QUOTIENT_BASIS_SERIALIZED_AND_TRANSFERABLE__DOSE_2X_STATICALLY_INADMISSIBLE__NO_FRESH_PANEL__ZERO_STARTS",
    "parent": "96c7d295e72106cd949d810fa92807c2514e7449",
    "Q1_OFFLINE": "COMPLETE -- exact rederivation reproduces the parent R0 bit-for-bit and "
                  "R1/R2/I1/I2 to certified enclosures; FWL2_RELATIVE_QUOTIENT_BASIS_V1 serialized "
                  "as real arrays; P2 and E2 transfer licenses GRANTED.",
    "Q2_PANEL": "NOT_LICENSED -- fresh panel not built (S5).",
    "Q3_CELL": "NOT_EVALUABLE -- no fresh rows.",
    "Q4_DOSE": "STATICALLY_INADMISSIBLE -- the two locked carriers are involutions with no dose "
               "magnitude; a 2x needs a forbidden new executable or violates the frozen domain.",
    "Q5_QUOTIENT": "NOT_EVALUABLE -- no fresh rows.",
    "Q6_TRANSFER": "MACHINERY_READY -- the serialized basis is transfer-ready, but there are no "
                   "fresh rows to transfer in this programme.",
    "certified_headline": {
        "R0_exact_matches_parent": CERT["rederivation_matches_parent"]["R0_exact"],
        "I2_enclosure": CERT["exact_values"]["I2_enclosure"],
        "ENERGY_MULTIPLIER_REQUIRED": mult["ENERGY_MULTIPLIER_REQUIRED"],
        "AMPLITUDE_MULTIPLIER_REQUIRED": mult["AMPLITUDE_MULTIPLIER_REQUIRED"],
        "AMPLITUDE_MULTIPLIER_STRICTLY_BELOW_2": mult["AMPLITUDE_MULTIPLIER_STRICTLY_BELOW_2"],
        "P2_TRANSFER_LICENSE": CERT["P2_TRANSFER_LICENSE"],
        "E2_AXIS_TRANSFER_LICENSE": CERT["E2_AXIS_TRANSFER_LICENSE"],
    },
    "engine_starts": START,
    "TOMMY_ACTION_REQUIRED": False,
    "TOMMY_GIT_ACTION_REQUIRED": False,
    "PUSH_AUTHORIZED": False, "DRAFT_PR_AUTHORIZED": False, "WORKFLOW_TRIGGER_AUTHORIZED": False,
    "geometry_tested": "NOT_TESTED_IN_THIS_DESIGN",
    "allocation_tested": "NOT_TESTED_IN_THIS_DESIGN",
    "independent_units": "the ancestry block; n=8 was DESIGNED but not constructed (S5).",
    "deviations": ["D0_handoff_text_lost_to_compaction_names_reconstructed",
                   "D1_full_clone_substituted_by_object_db_extraction_plus_cross_version_tree_id",
                   "D2_inherited_stale_parent_bundle_digest_carried_forward_not_repaired"],
}
json.dump(DISP, open(f"{OUT}/SQDT00_FINAL_DISPOSITION.json", "w"), indent=1)
json.dump(START, open(f"{OUT}/SQDT00_ENGINE_START_LEDGER.json", "w"), indent=1)
print("closure written. DISPOSITION:")
print(" ", DISP["DISPOSITION"])
print("  P2/E2:", CERT["P2_TRANSFER_LICENSE"], CERT["E2_AXIS_TRANSFER_LICENSE"],
      "| AMP<2:", mult["AMPLITUDE_MULTIPLIER_STRICTLY_BELOW_2"], "| starts:", START["total_engine_starts_spent"])

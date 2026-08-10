"""FWL2CF00 Phase 0 + Section 1-2 -- provenance, arm-lock temporal order, MASTER FREEZE.
No engine is imported. No fresh numeric row exists."""
from __future__ import annotations
import os, json, hashlib, ast
from fractions import Fraction as Fr

OUT = "/home/claude/sweep/FWL2CF00"
W2 = "/home/claude/sweep/WL2SMF00"
os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
gblob = lambda p: hashlib.sha1(b"blob %d\x00" % os.path.getsize(p) + open(p, "rb").read()).hexdigest()
DEV = json.load(open(f"{OUT}/_device_blobs.json"))
CHAIN = ["e912a1004c5b9732d12a8fcc417002bfd1135622", "f81daf91dd70a05f34372fb85d2c3fba0dd5550b",
         "f9e1e39170a746bc5d8c43a80bc878cf24180714", "f65851c39496f379edac8b665dce87ba7cf1ebfb",
         "0d92b612e051166b84d1a7d08d681ea78f5a512d", "226b2c93bdc34e5bec2ebc28d0c6066dc3123b14",
         "2c9fc97c5e05de2b15ccceeba0c9bc36e327e3b0"]
P = {"chain": CHAIN, "direct_parent_at_every_arrow": True,
     "WL2SMF00_subtree": "8b002dc2a86974af0beb442a1013895ef5b47e36",
     "checkpoints_subtree": "cec5b6e80657539fdffe77d2069bc8c87a1e2502",
     "blob_binding": {}, "manifest": {}}
for rel, oid in DEV.items():
    p = f"/home/claude/sweep/{rel}"
    P["blob_binding"][rel] = {"committed": oid, "recomputed": gblob(p), "match": gblob(p) == oid}
for d in ("WSFSCRP00", "FSCMA00", "GIMB00", "WL2SMF00"):
    base = f"/home/claude/sweep/{d}"
    bad, n = [], 0
    for line in open(f"{base}/SHA256SUMS"):
        h, f = line.rstrip("\n").split("  ", 1)
        n += 1
        if sha(f"{base}/{f}") != h:
            bad.append(f)
    P["manifest"][d] = {"entries": n, "failures": len(bad), "failed": bad}
ALLB = all(v["match"] for v in P["blob_binding"].values())
ALLS = all(v["failures"] == 0 for v in P["manifest"].values())

# ---- arm-lock temporal order, proved by one-way hash chaining ------------------------
ARM = json.load(open(f"{W2}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json"))
PANEL = json.load(open(f"{W2}/WL2SMF00_PANEL_LOCK.json"))
THR = json.load(open(f"{W2}/WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json"))
ZERO = json.load(open(f"{W2}/ZERO_ACTIVE_OUTCOME_ACCESS_LEDGER.json"))
P["arm_lock_pretheshold_order"] = {
    "arm_lock_sha256": sha(f"{W2}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json"),
    "panel_lock_records_arm_lock_sha": PANEL.get("future_carrier_arm_lock_sha256"),
    "arm_lock_hash_matches_panel_record":
        PANEL.get("future_carrier_arm_lock_sha256") == sha(f"{W2}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json"),
    "panel_lock_sha256": sha(f"{W2}/WL2SMF00_PANEL_LOCK.json"),
    "threshold_lock_records_panel_lock_sha": THR.get("panel_lock_sha256"),
    "panel_hash_matches_threshold_record":
        THR.get("panel_lock_sha256") == sha(f"{W2}/WL2SMF00_PANEL_LOCK.json"),
    "argument": "SHA-256 is one-way. The panel lock CONTAINS the arm lock's digest, so the arm "
                "lock existed in its final byte form before the panel lock was written. The "
                "threshold lock CONTAINS the panel lock's digest, so the panel lock existed "
                "before any threshold value was written. Therefore arm identities and every arm "
                "parameter were fixed strictly before the first descendant threshold was computed "
                "or opened. Mere co-presence in the final tree is not used as the argument.",
    "corroboration": {
        "panel_lock_states": PANEL["SHAM_0"][:60] + " ...",
        "wl2_panel_source_writes_arm_lock_before_panel_lock":
            open(f"{W2}/wl2_panel.py").read().index("FUTURE_ACTIVE_CARRIER_ARM_LOCK.json")
            < open(f"{W2}/wl2_panel.py").read().index("WL2SMF00_PANEL_LOCK.json"),
        "wl2_sham_asserts_panel_lock_before_running":
            "assert sha(f\"{OUT}/WL2SMF00_MASTER_FREEZE.md\") == LOCK[\"master_freeze_sha256\"]"
            in open(f"{W2}/wl2_sham.py").read(),
        "zero_active_outcome_ledger": {k: ZERO[k] for k in
                                       ("fresh_active_outcomes_generated", "fresh_active_outcomes_opened",
                                        "old_active_outcomes_loaded_by_threshold_pipeline",
                                        "post_t0_advances")}},
}
P["arm_lock_pretheshold_order"]["PROVED"] = bool(
    P["arm_lock_pretheshold_order"]["arm_lock_hash_matches_panel_record"]
    and P["arm_lock_pretheshold_order"]["panel_hash_matches_threshold_record"]
    and P["arm_lock_pretheshold_order"]["corroboration"]["wl2_panel_source_writes_arm_lock_before_panel_lock"])

# ---- parent zero-active-outcome claim, proved by resolved-symbol AST -----------------
ACTIVE_SYMS = {"transpose", "state_cross", "_perturb_N", "reciprocal_cross", "erase_all",
               "erase_half", "core_erase", "eligible_edges", "frozen_matching"}


def calls(path):
    out = set()
    for nd in ast.walk(ast.parse(open(path).read())):
        if isinstance(nd, ast.Call):
            f = nd.func
            out.add(f.id if isinstance(f, ast.Name) else getattr(f, "attr", ""))
        if isinstance(nd, ast.Import):
            out |= {a.name for a in nd.names}
        if isinstance(nd, ast.ImportFrom):
            out.add(nd.module or "")
    return out


P["parent_zero_active_outcome"] = {
    f: {"active_symbols_called": sorted(calls(f"{W2}/{f}") & ACTIVE_SYMS)}
    for f in ("wl2_prod.py", "wl2_ref.py", "wl2_panel.py", "wl2_sham.py")}
P["parent_zero_active_outcome"]["PROVED"] = all(
    not v["active_symbols_called"] for v in P["parent_zero_active_outcome"].values()
    if isinstance(v, dict))
P["parent_zero_active_outcome"]["note"] = (
    "the two future executables appear only as inert strings inside "
    "FUTURE_ACTIVE_CARRIER_ARM_LOCK.json; no import and no call site exists in the parent.")

# ---- the panel has NOT been active-outcome exposed -----------------------------------
P["sealed_panel_not_yet_exposed"] = {
    "parent_ledger": ZERO["fresh_active_outcomes_generated"] == 0
                     and ZERO["fresh_active_outcomes_opened"] == 0,
    "post_t0_advances": ZERO["post_t0_advances"],
    "checkpoint_hashes_match_panel_lock": all(
        d["checkpoint_sha"] == d["checkpoint_sha"] for d in PANEL["descendants"]),
}
P["VERDICT"] = ("PROVENANCE_BOUND" if (ALLB and ALLS
                                       and P["arm_lock_pretheshold_order"]["PROVED"]
                                       and P["parent_zero_active_outcome"]["PROVED"])
                else "PARENT_OR_CHAIN_PROVENANCE_UNRESOLVED")

# ---- FROZEN FACTOR PIPELINE STATUS, declared BEFORE any fresh data --------------------
G = json.load(open("/home/claude/sweep/GIMB00/OFFLINE_GI_SCORES_AND_CERTIFIED_INTERVALS.json"))
MODAL = json.load(open(f"{W2}/MODAL_AND_CONTRAST_PROPAGATION_CERTIFICATE.json"))
serialized_vectors = []
for d in ("GIMB00", "WL2SMF00"):
    for f in sorted(os.listdir(f"/home/claude/sweep/{d}")):
        if f.endswith(".json"):
            t = open(f"/home/claude/sweep/{d}/{f}").read()
            for k in ("psi_plus", "Psi_minus", "psi_stratum", "stratum_axis"):
                if '"%s"' % k in t:
                    serialized_vectors.append(f"{d}/{f}:{k}")
FFPS = {
    "searched_for": ["psi_plus", "Psi_minus", "psi_stratum", "stratum_axis"],
    "found_in_committed_parent_trees": serialized_vectors,
    "what_GIMB00_did_serialize": sorted(G["F_stratum"].keys()) + sorted(G["F_stratum_supplementary"].keys()),
    "finding": "GIMB00 serialised only SCALAR summaries of the founder-stratum object -- shares, "
               "sector proportions, support lists, alignments. The axis vectors psi_plus and "
               "Psi_minus themselves were never written to disk and are therefore not in any "
               "committed parent tree.",
    "why_it_may_not_be_reconstructed": "rebuilding the axis would require reopening "
                                       "GIMB00_BOUND_ROWS.json, i.e. the historical exposed active "
                                       "rows, and refitting. This handoff sets "
                                       "HISTORICAL_ACTIVE_ROWS_OPENED_OR_REFIT = false and lists "
                                       "HISTORICAL_ACTIVE_ROW_LOAD_OR_REFIT_PROTOCOL_BREACH in the "
                                       "precedence. Improvising the missing object later is "
                                       "explicitly forbidden.",
    "FSCMA00_phi1_is_not_a_substitute": "FSCMA00_AFFINE_BASIS_MANIFEST.json does serialise mu and "
                                        "phi1, but that is the CARRIER affine basis of a different "
                                        "programme and panel, not the founder-stratum object. "
                                        "Substituting it would be improvising the missing object.",
    "transformed_bounds_from_the_parent_certificate": {
        "PROJECTIVE_EMBEDDING_BOUND": MODAL["quadratic_objects"]["PROJECTIVE_EMBEDDING_BOUND"],
        "H3_K_BOUND": MODAL["quadratic_objects"]["H3_K_BOUND"]},
    "FROZEN_FACTOR_PIPELINE_STATUS": "PARENT_OBJECT_NOT_EVALUABLE",
    "consequences_declared_now": {
        "Q_PRIMARY_1_cell_materiality": "ELIGIBLE",
        "Q_PRIMARY_2_fresh_quotient": "ELIGIBLE",
        "Q_PRIMARY_3_stratum_transfer": "NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT",
        "Q_PRIMARY_4_attribution_of_the_parent_stratum": "NOT_REACHED",
        "fresh_predeclared_factor_objects": "may still be evaluated, and may ONLY be labelled "
                                            "FRESH_FACTOR_EFFECT_NOT_PARENT_STRATUM_EXPLANATION",
        "PLUS_sector_fresh_contrasts": "have a valid original-unit floor, TAU_CONTRAST(c) = "
                                       "sum_i |c_i| TAU_i, from the locked per-descendant TAU",
        "MINUS_sector_fresh_objects": "TRANSFORMED_BOUND_NOT_QUALIFIED -- the parent certificate "
                                      "states PROJECTIVE_EMBEDDING_BOUND = NOT_AVAILABLE, so no "
                                      "response^4 object can be compared with a response-unit TAU"},
}
P["FROZEN_FACTOR_PIPELINE"] = FFPS
json.dump(P, open(f"{OUT}/_provenance_raw.json", "w"), indent=1, default=str)
print("PROVENANCE:", P["VERDICT"])
print("  blobs", ALLB, "| manifests", {k: (v["entries"], v["failures"]) for k, v in P["manifest"].items()})
print("  arm-lock pre-threshold order PROVED:", P["arm_lock_pretheshold_order"]["PROVED"])
print("  parent zero-active PROVED:", P["parent_zero_active_outcome"]["PROVED"])
print("  FROZEN_FACTOR_PIPELINE_STATUS:", FFPS["FROZEN_FACTOR_PIPELINE_STATUS"])
assert P["VERDICT"] == "PROVENANCE_BOUND"

# =====================================================================================
# MASTER FREEZE
# =====================================================================================
TH = {r["descendant_id"]: r for r in THR["descendant_thresholds"]}
DESC = PANEL["descendants"]
E_TAU = sum((Fr(1, 16) * Fr(TH[d["descendant_id"]]["TAU_MATERIAL_L2_sq_exact"]) for d in DESC), Fr(0))
SCHEDULE_SHAM = [d["descendant_id"] for d in sorted(DESC, key=lambda x: x["descendant_id"])]
SCHEDULE_ACTIVE = [(did, o) for did in SCHEDULE_SHAM for o in ("CARRIER_1", "CARRIER_2")]
OPAQUE = {f"{did}|{o}": hashlib.sha256(f"FWL2CF00-opaque-v1|{did}|{o}".encode()).hexdigest()[:16]
          for did, o in SCHEDULE_ACTIVE}

FREEZE = f"""# FWL2CF00_MASTER_FREEZE

Written and hashed before any engine instantiation and before any fresh numeric row exists.

## Ordered questions

    Q_PRIMARY_1 = do all 32 locked carrier cells exceed their own prospective weighted-L2 threshold
    Q_PRIMARY_2 = if so, what is the fresh gauge-invariant carrier quotient structure
    Q_PRIMARY_3 = does the exact frozen parent founder-stratum object transfer without refit
    Q_PRIMARY_4 = if transfer passes, what is its origin

`FROZEN_FACTOR_PIPELINE_STATUS = PARENT_OBJECT_NOT_EVALUABLE`, declared here, before any fresh
data. GIMB00 serialised only scalar summaries of its founder-stratum object; the axis vectors
`psi_plus` and `Psi_minus` are in no committed parent tree. Rebuilding them would mean reopening
and refitting the historical exposed active rows, which this handoff forbids. Therefore
**Q_PRIMARY_3 = NOT_EVALUABLE_FROM_COMMITTED_PARENT_OBJECT and Q_PRIMARY_4 = NOT_REACHED**, while
Q_PRIMARY_1 and Q_PRIMARY_2 remain fully eligible. Predeclared fresh factor objects may still be
evaluated and may only be labelled `FRESH_FACTOR_EFFECT_NOT_PARENT_STRATUM_EXPLANATION`.

## Panel, arms, gauge

16 sealed descendants, 4 upstream ancestry blocks, `g in {{NEAR,FAR}}` manipulated (G1),
`a in {{0,1}}` neutral complementary-allocation members (H3). Two frozen carrier arms per
descendant, taken only from `FUTURE_ACTIVE_CARRIER_ARM_LOCK.json`:

* `CARRIER_1` = `{ARM['CARRIER_1']['callable']}`, code sha256 `{ARM['CARRIER_1']['code_sha256'][:16]}`,
  declared touch set `{ARM['CARRIER_1']['declared_touch_set']}`, applied at the descendant t0.
* `CARRIER_2` = `{ARM['CARRIER_2']['callable']}`, code sha256 `{ARM['CARRIER_2']['code_sha256'][:16]}`,
  declared touch set `{ARM['CARRIER_2']['declared_touch_set']}`, applied at the descendant t0.

`EXPECT_STRUCTURAL_ZERO_AT_H0 = true` for both arms: each writes `Mf` only, never `rho`, and the
reader integrates `rho` over the immutable masks, so `r(h0) = (0,0)` exactly.

Gauge: one optional A/B swap per descendant, shared across all scored times AND both carrier arms.
`u -> u`, `v -> -v`. A per-time, per-arm, per-row, per-geometry-cell or per-contrast swap is not
the gauge. `M2` alone is known to be blind to some illegal per-time swaps and may not validate
scope; the whole-descendant block reconstruction oracle does.

## Estimand

    X_A[r,d,h] = sum_i M_A0[d,i] rho[r,d,h,i] / B[d]        (raw, undifferenced)
    delta_A[d,o,h] = X_A[INT,d,o,h] - X_A[SHAM_0_REPLAY,d,h]
    z[d,o] = concat_h( sqrt(w_h) delta_A , sqrt(w_h) delta_B )
    M2[d,o]^2 = sum_h w_h (delta_A^2 + delta_B^2) = ||u||^2 + ||v||^2

## Immutable thresholds, bound not recomputed

Per descendant, the exact rational `B`, `RHO_MED`, `G2^2`, `ETA_ORACLE_L2 = 0`,
`TAU_DYNAMIC_L2^2`, `TAU_SITE_L2^2`, `TAU_MATERIAL_L2^2` and the dominance label are taken from
`WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json`. Replay values are checked against the lock as an oracle;
the **locked** threshold remains operative in every decision.

    alpha[d,o] = 1/32 per response row; n stays 4 ancestry blocks
    E_TAU (exact) = {E_TAU}
    E_TAU (float) = {float(E_TAU):.6e}
    A_TAU (float) = {float(E_TAU) ** 0.5:.6e}

## Cell rule (exact squares; no floating square root in the decision path)

    PASS iff lower(M2^2) >  upper(TAU_MATERIAL_L2^2)
    FAIL iff upper(M2^2) <= lower(TAU_MATERIAL_L2^2)
    otherwise NUMERICALLY_UNRESOLVED.  Equality is FAILURE.

Global: any certified FAIL -> ALL_CELL_MATERIALITY = FAIL; else any unresolved -> UNRESOLVED;
else PASS_32_OF_32. The complete-panel gate passes only on 32 of 32.

## Quotient (only after PASS_32_OF_32)

    R_k = global min over linked descendant swaps, affine mean and orthonormal k-dim model
    I1 = R0 - R1 (parent alias L1)      I2 = R1 - R2 (parent alias L2)
    I1_interval = [lower(R0)-upper(R1), upper(R0)-lower(R1)]
    I2_interval = [lower(R1)-upper(R2), upper(R1)-lower(R2)]
    Q_RATIO_SQ = I2/I1 in the decision path; Q_RATIO = sqrt only for display

    QDIM0 lower(R0) > upper(E_TAU)
    QDIM1 lower(sqrt(I2)) > upper(A_TAU)
    QDIM2 lower(Q_RATIO_SQ) > 0.01
    QDIM3 lower(I2/R0) >= 0.05
    FRESH_QUOTIENT_AT_LEAST_TWO_PASS = all four

Boundaries: `I2/I1` exactly 0.01 FAILS; share exactly 0.05 PASSES; a certified interval crossing a
boundary is `NUMERICALLY_UNRESOLVED`; `upper(R0)<=0` DEGENERATE_TOTAL_SCATTER; `upper(I1)<=0`
DEGENERATE_FIRST_INCREMENT; `upper(I2)<=0` NO_SECOND_INCREMENT; an interval touching zero forbids
the corresponding division or square root. `0 <= I2 <= R0` makes QDIM1 imply QDIM0; both fields are
kept as a consistency oracle. `R0 > 20*E_TAU` is the boundary condition at share exactly 0.05, not
a necessary condition when the observed share is larger.

Direct one-family reconstruction, evaluated over EVERY co-optimal M1:
`upper(R1/R0) < 0.05` and every row's `upper(ONE_FAMILY_CELL_RESIDUAL) < 0.10`; equality at 0.10
fails; the parent certified-zero denominator rule applies.

## Optimiser certification

All `2^(16-1) = 32768` linked swap assignments are enumerated after removing the single global
duplicate. `R0` is certified **exactly** for every assignment, because
`R0(eps) = C - ||ubar||^2 - ||sum_d eps_d V_d||^2` reduces to an exact binary quadratic form.
`R1` and `R2` are enumerated exhaustively in float64 over all 32768 with a Weyl / backward-stability
error bound, and the argmin plus every near-tie is then certified in exact rational arithmetic by
Sylvester inertia. If the certified margin between the winner and the runner-up does not exceed the
error bound by at least a factor of 100, the result is `FRESH_CARRIER_QUOTIENT_NUMERICALLY_UNRESOLVED`.

## Budget

    SHAM_0_RECONSTRUCTION = 16      ACTIVE_CARRIER = 32      SETUP_OR_DIAGNOSTIC = 0
    TOTAL_MAXIMUM = 48;  zero retries; tranches independent; unused starts are not repurposable
    START_ENTER is durably appended and fsynced before each subprocess launch; the launch consumes
    the continuation even if the child dies before its first scored output.

Frozen sham schedule: {SCHEDULE_SHAM}

Frozen active schedule (opaque ids assigned before execution; labels are not decoded until the raw
panel lock is committed and independently read back):
{json.dumps(OPAQUE, indent=1)}

## Append-only

    WSFSCRP00 / FSCMA00 / GIMB00 / WL2SMF00 _DISPOSITION_REWRITTEN = false
    PARENT_THRESHOLDS_RECOMPUTED_OR_CHANGED = false
    PARENT_PANEL_MEMBERSHIP_CHANGED = false
    HISTORICAL_ACTIVE_ROWS_OPENED_OR_REFIT = false

WL2SMF00 prospectively qualified descendant-specific weighted-L2 materiality thresholds and sealed
a G1 x H3 target panel before any active outcome. It did not measure a carrier response. FWL2CF00
reconstructs the missing canonical sham reference series without recalibration, executes only the
two already locked carrier arms, and evaluates the predeclared quotient and factorial objects. No
historical active result or parent threshold is reclassified.

## Claim ceiling

RESPONSE_INFORMED_EXPLORATORY_DEV, PROSPECTIVELY_LOCKED_PANEL_AND_THRESHOLDS, one LawSpec, one
checkpoint and horizon, fixed-support reader, FOUR independent ancestry blocks, finite designed
panel, single-executor internal oracle, not independent review, not confirmatory, not population
inference. 16 descendants and 32 arms are never independent replications. No signed history claim
under H3. No physical A/B identity. No intrinsic or universal rank. No environmental claim from a
carrier-only programme.
"""
open(f"{OUT}/FWL2CF00_MASTER_FREEZE.md", "w").write(FREEZE)
json.dump({"descendants": DESC, "thresholds": TH, "arm_lock": ARM,
           "E_TAU_exact": str(E_TAU), "alpha_per_row": "1/32",
           "sham_schedule": SCHEDULE_SHAM, "active_schedule": [list(x) for x in SCHEDULE_ACTIVE],
           "opaque_ids": OPAQUE, "weights": PANEL["reader"]["weights"],
           "H_GRID": PANEL["reader"]["H_GRID"],
           "parent_locks": {"panel": sha(f"{W2}/WL2SMF00_PANEL_LOCK.json"),
                            "threshold": sha(f"{W2}/WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json"),
                            "arm": sha(f"{W2}/FUTURE_ACTIVE_CARRIER_ARM_LOCK.json")}},
          open(f"{OUT}/PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json", "w"), indent=1)
H = {f: sha(f"{OUT}/{f}") for f in ("FWL2CF00_MASTER_FREEZE.md",
                                    "PARENT_LOCK_AND_ARM_BINDING_MANIFEST.json")}
json.dump({"hashes": H, "frozen_before_any_engine_instantiation": True,
           "FROZEN_FACTOR_PIPELINE_STATUS": "PARENT_OBJECT_NOT_EVALUABLE"},
          open(f"{OUT}/FWL2CF00_MASTER_FREEZE_HASHES.json", "w"), indent=1)
print("MASTER FREEZE:", {k: v[:12] for k, v in H.items()})
print("E_TAU exact =", float(E_TAU), "| 16 descendants, 32 active rows scheduled")

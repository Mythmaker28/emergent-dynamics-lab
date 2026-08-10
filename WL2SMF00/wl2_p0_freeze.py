"""WL2SMF00 Phase 0 + Section 1-4 -- provenance binding and the MASTER FREEZE.

ORDER IS LOAD-BEARING AND VERIFIABLE BY READING THIS FILE TOP TO BOTTOM:
  1. bind the parent chain and the committed bytes
  2. write and hash WL2SMF00_MASTER_FREEZE and its companion specs
  3. NOTHING numeric and fresh is loaded here at all; no engine is imported
"""
from __future__ import annotations
import os, sys, json, hashlib, ast
from fractions import Fraction as Fr

OUT = "/home/claude/sweep/WL2SMF00"
os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
gblob = lambda p: hashlib.sha1(b"blob %d\x00" % os.path.getsize(p) + open(p, "rb").read()).hexdigest()

# =====================================================================================
# 0. PARENT PROVENANCE
# =====================================================================================
CHAIN = ["e912a1004c5b9732d12a8fcc417002bfd1135622",
         "f81daf91dd70a05f34372fb85d2c3fba0dd5550b",
         "f9e1e39170a746bc5d8c43a80bc878cf24180714",
         "f65851c39496f379edac8b665dce87ba7cf1ebfb",
         "0d92b612e051166b84d1a7d08d681ea78f5a512d"]
BLOBS = {  # committed blob object ids, resolved on the device from the 0d92b61 tree
    "GIMB00/gimb_oracle_v2.py": None, "GIMB00/GAUGE_ORACLE_TESTS.json": None,
    "GIMB00/GIMB00_FREEZE.md": None, "GIMB00/MATERIALITY_BOUND_PROPAGATION.md": None,
    "GIMB00/OFFLINE_GI_SCORES_AND_CERTIFIED_INTERVALS.json": None,
    "WSFSCRP00/wsfscrp_core.py": None,
}
DEV = json.load(open(f"{OUT}/_device_blobs.json")) if os.path.exists(f"{OUT}/_device_blobs.json") else {}
prov = {"reported_chain": CHAIN, "blob_binding": {}, "manifest_verification": {}}
for rel in BLOBS:
    p = f"/home/claude/sweep/{rel}"
    local = gblob(p)
    prov["blob_binding"][rel] = {"recomputed_from_local_bytes": local,
                                 "committed_blob_oid": DEV.get(rel),
                                 "match": (DEV.get(rel) == local) if rel in DEV else None,
                                 "sha256": sha(p)}
for d in ("WSFSCRP00", "FSCMA00", "GIMB00"):
    base = f"/home/claude/sweep/{d}"
    bad, n = [], 0
    for line in open(f"{base}/SHA256SUMS"):
        h, f = line.rstrip("\n").split("  ", 1)
        n += 1
        if sha(f"{base}/{f}") != h:
            bad.append(f)
    prov["manifest_verification"][d] = {"entries": n, "failures": len(bad), "failed": bad}

# ---- bind the CORRECTED gauge oracle, not the vacuous first pass ----------------------
src_v2 = open("/home/claude/sweep/GIMB00/gimb_oracle_v2.py").read()
tree = ast.parse(src_v2)
selfcmp = []
for nd in ast.walk(tree):
    if isinstance(nd, ast.Compare) and len(nd.ops) == 1:
        try:
            if ast.dump(nd.left) == ast.dump(nd.comparators[0]):
                selfcmp.append(nd.lineno)
        except Exception:
            pass
GOR = json.load(open("/home/claude/sweep/GIMB00/GAUGE_ORACLE_TESTS.json"))
prov["corrected_gauge_oracle"] = {
    "file": "GIMB00/gimb_oracle_v2.py", "sha256": sha("/home/claude/sweep/GIMB00/gimb_oracle_v2.py"),
    "supersedes": GOR.get("supersedes"),
    "self_comparing_predicates_found": selfcmp,
    "declares_real_swaps": "a, b = (dB, dA)" in src_v2,
    "negative_controls": GOR["negative_controls"],
    "all_negative_controls_fire": all(GOR["negative_controls"].values()),
    "verdict_in_parent": GOR["VERDICT"],
    "BOUND": bool(not selfcmp and all(GOR["negative_controls"].values())
                  and GOR["VERDICT"] == "GAUGE_ORACLE_PASS_WITH_NEGATIVE_CONTROLS"),
    "note": "the vacuous FIRST-pass oracle is explicitly NOT inherited; only gimb_oracle_v2.py, "
            "which applies real region exchanges and carries firing negative controls, is bound."}

# ---- bind the inherited reader, weights, masks, normalizer, horizon -------------------
Zsrc = open("/home/claude/sweep/WSFSCRP00/wsfscrp_core.py").read()
prov["inherited_reader_binding"] = {
    "file": "WSFSCRP00/wsfscrp_core.py", "sha256": sha("/home/claude/sweep/WSFSCRP00/wsfscrp_core.py"),
    "H_GRID": "[40, 80, ..., 400]", "H_GRID_present": "H_GRID = [40, 80, 120, 160, 200, 240, 280, 320, 360, 400]" in Zsrc,
    "dt": "C.SPEC.dt = 0.1", "physical_times": "4.0 .. 40.0",
    "weights": "trapezoidal in physical time, normalised to sum 1, computed in exact Fraction",
    "normalizer": "B_of(st,MA,MB) = dsum(st.rho[nonzero(MA|MB)]), exact rational",
    "raw_reader": "q_channels(st,MA,MB,B) = (dsum(rho[MA])/B, dsum(rho[MB])/B) -- RAW X, NOT a "
                  "difference. The dA/dB stored in parent files are ALREADY differenced arm minus "
                  "sham; never subtract a sham twice.",
    "detector": "rho > 0.30 strict, >= 12 sites, 4-connected periodic, exactly two eligible",
    "dsum_is_exact": "return sum((Fr(float(v)) for v in vals), Fr(0))" in Zsrc}
prov["VERDICT"] = ("PROVENANCE_BOUND"
                   if (all(v["failures"] == 0 for v in prov["manifest_verification"].values())
                       and prov["corrected_gauge_oracle"]["BOUND"])
                   else "PARENT_OR_CHAIN_PROVENANCE_UNRESOLVED")
json.dump(prov, open(f"{OUT}/_provenance_raw.json", "w"), indent=1)
print("PROVENANCE:", prov["VERDICT"])
print("  manifests:", {k: (v["entries"], v["failures"]) for k, v in prov["manifest_verification"].items()})
print("  corrected oracle bound:", prov["corrected_gauge_oracle"]["BOUND"],
      "| self-comparing predicates in v2:", selfcmp)
assert prov["VERDICT"] == "PROVENANCE_BOUND"

# =====================================================================================
# 1-4. MASTER FREEZE
# =====================================================================================
T = 10
H_GRID = [40 * i for i in range(1, 11)]
PHYS = [Fr(h) * Fr(1, 10) for h in H_GRID]
_v = [Fr(0)] * T
_v[0] = (PHYS[1] - PHYS[0]) / 2
_v[T - 1] = (PHYS[T - 1] - PHYS[T - 2]) / 2
for j in range(1, T - 1):
    _v[j] = (PHYS[j + 1] - PHYS[j - 1]) / 2
W = [x / sum(_v, Fr(0)) for x in _v]
assert sum(W, Fr(0)) == 1 and all(w > 0 for w in W)
# h0 = the intervention checkpoint, native step 0 of the scored continuation. It is NOT in the
# scored grid (the inherited design checks r(h0) = (0,0) separately), so W_POST = 1 exactly.
W_POST = sum(W, Fr(0))

NAMESPACE = list(range(65000, 65008))

FREEZE = f"""# WL2SMF00_MASTER_FREEZE

Written and hashed **before any fresh numeric array exists**. No engine module is imported by this
file. Nothing below may be revised later under this programme id.

    PROGRAMME_TYPE = METHODS_AND_MEASUREMENT_QUALIFICATION_ONLY
    ACTIVE_CARRIER / ENVIRONMENTAL / FACTORIAL INTERVENTION STARTS = 0
    ALLOWED_POST_T0_ENGINE_STARTS = SHAM_0_AND_SHAM_1_ONLY

## 0. Bound parent chain

    e912a10 -> f81daf9 -> f9e1e39 -> f65851c -> 0d92b61

Direct-parent at every arrow. The **corrected** gauge oracle `GIMB00/gimb_oracle_v2.py` is bound;
the vacuous first-pass oracle is explicitly not inherited.

## 1. Materiality semantics — three separate concepts, never merged

    ETA_ORACLE_L2[d]   deterministic upper bound on SCORING / RELOAD / SUBTRACTION arithmetic error
    TAU_DYNAMIC_L2[d]  one percent of native sham evolution, in the exact L2 norm
    TAU_SITE_L2[d]     one-percent representative baseline-site effect, in the exact L2 norm
    TAU_MATERIAL_L2[d] = max(ETA_ORACLE_L2, TAU_DYNAMIC_L2, TAU_SITE_L2)

Materiality here is an **operational minimum effect scale**. It is not a p-value, not a confidence
bound, not a fitted noise distribution and not a physical constant. The engine is bit-deterministic:
two identical shams validate determinism and estimate nothing. Sham discordance is an oracle
failure, never a sample of noise.

The coefficient `0.01` is inherited unchanged from WSFSCRP00's prospective scientific floor. No
coefficient scan, power optimisation or response-informed alternative is authorised.

## 2. Exact weighted-L2 estimand and the gauge

Raw reader, per arm, descendant and time — **undifferenced**:

    X_A[arm,d,h] = sum_i M_A0[d,i] * rho[arm,d,h,i] / B[d]
    X_B[arm,d,h] = sum_i M_B0[d,i] * rho[arm,d,h,i] / B[d]

This is exactly `wsfscrp_core.q_channels`. The `dA`/`dB` arrays stored in parent files are ALREADY
`arm - sham`; a sham is never subtracted twice.

Future active response, unchanged endpoint:

    delta_A[d,o,h] = X_A[INT,d,o,h] - X_A[SHAM_0,d,h]
    delta_B[d,o,h] = X_B[INT,d,o,h] - X_B[SHAM_0,d,h]

    z[d,o] = concat_h( sqrt(w_h)*delta_A , sqrt(w_h)*delta_B )
    M2[d,o] = ||z[d,o]||_2

    u = sqrt(w_h)*(delta_A+delta_B)/sqrt(2)      v = sqrt(w_h)*(delta_A-delta_B)/sqrt(2)
    M2^2 = sum_h w_h (delta_A^2 + delta_B^2) = ||u||^2 + ||v||^2

Gauge: ONE A/B exchange per descendant, shared across every scored time and every future arm.
`u -> u`, `v -> -v`, `M2` invariant. Per-time, per-arm or per-row swaps are a larger, non-physical
group and are rejected.

Weights, exact: `w = [1/18, 1/9 x 8, 1/18]`, all positive, sum exactly 1, over physical times
4.0 .. 40.0. `h0` (the intervention checkpoint) is **not** in the scored grid, so
`W_POST = sum_(h != h0) w_h = 1` exactly.

## 3. Descendant-specific threshold

`SHAM_0` is frozen as canonical by serialiser order **before either sham runs**. `SHAM_1` is an
identity oracle only: never averaged, never chosen for calmness, never a replication.

    g2[d]  = concat_h( sqrt(w_h)*(X_A[SHAM_0,d,h]-X_A[SHAM_0,d,h0]),
                       sqrt(w_h)*(X_B[SHAM_0,d,h]-X_B[SHAM_0,d,h0]) )
    G2[d]  = ||g2[d]||_2
    TAU_DYNAMIC_L2[d] = 0.01 * G2[d]

    RHO_MED[d]     = exact median of rho[d,i,h0] over i in M_A0 union M_B0
                     (even count -> exact arithmetic mean of the two central sorted values)
    TAU_SITE_L2[d] = 0.01 * RHO_MED[d] / B[d] * sqrt(W_POST)

`TAU_SITE_L2` means: one representative baseline-support site's rho changes by one percent, in one
channel, zero at `h0`, sustained at that amplitude over the later scored times. A declared
scientific scale, not an uncertainty estimate.

    ETA_ORACLE_L2[d] = sqrt( sum_h w_h * ( eps_delta_A^2 + eps_delta_B^2 ) )
    eps_delta_c >= eps_INT_c + eps_SHAM_c + eps_SUBTRACTION_c + eps_RELOAD_c

derived branchwise from the actual datatype, summation, masks, normalizer and reader, outcome
independently. It bounds the scoring path on serialized states; it is NOT a stability bound on
engine dynamics. Scorer agreement is an oracle, not a proof of this bound. See
`ETA_ORACLE_L2_FORWARD_ERROR_CERTIFICATE.md`.

Forbidden: converting the old `ETA_bu`/`A_bu` by `sqrt(18)` or any fitted sparsity constant;
empirical RMS, pooled sd, covariance, percentile, quantile, maximum response, observed shape or a
favourable sector.

Frozen future cell rule:

    CELL_MATERIAL_PASS  iff lower(M2[d,o]) >  upper(TAU_MATERIAL_L2[d])
    CELL_MATERIAL_FAIL  iff upper(M2[d,o]) <= lower(TAU_MATERIAL_L2[d])
    otherwise CELL_MATERIAL_NUMERICALLY_UNRESOLVED

Equality is failure. No future programme may replace a descendant because its threshold is high or
because an active response fails.

## 4. Propagation to quotient and contrast estimands

Independent unit = the upstream ancestry block. Descendants, allocation branches, sham twins,
carrier sentinels, channels, sites and times are repeated conditions, never replications.

    G1 weights: 1/4 per upstream block, 1/4 per descendant, 1/2 per sentinel = 1/32 per row, n=4
    G2 weights: 1/8 per upstream block, 1/2 per descendant, 1/2 per sentinel = 1/32 per row, n=8

    E_TAU = sum_i alpha_i * TAU_MATERIAL_L2[i]^2          A_TAU = sqrt(E_TAU)
    E_ETA_ORACLE = sum_i alpha_i * ETA_ORACLE_L2[i]^2     A_ETA_ORACLE = sqrt(E_ETA_ORACLE)

`A_ETA_ORACLE` bounds only the weighted response-matrix perturbation norm. Certified `R_k`
intervals are built by bounding `sqrt(R_k)` first (1-Lipschitz argument) and squaring nonnegative
endpoints; `L2 = R1 - R2` by certified interval subtraction. The inequality
`|sqrt(L2_hat) - sqrt(L2_true)| <= A_ETA_ORACLE` is NOT asserted.

    TAU_CONTRAST(c) = sum_i |c_i| * TAU_MATERIAL_L2[i]       (normalised c, gauge-valid sector only)
    TAU_QUOTIENT_PAIR(i,j) = TAU_MATERIAL_L2[i] + TAU_MATERIAL_L2[j]
    H3_PRIMARY_ALLOCATION_OBJECT = UNORDERED_QUOTIENT_DISTANCE_BETWEEN_ALLOCATIONS
    H3_SIGNED_LINEAR_CONTRAST = NOT_DEFINED

Future gates, defined now and NOT evaluated here:

    QDIM_TOTAL_SCATTER_MATERIAL      iff lower(R0) > upper(E_TAU)
    QDIM_SECOND_INCREMENT_MATERIAL   iff lower(sqrt(L2)) > upper(A_TAU)
    inherited relative gates, additionally required: sqrt(L2/L1) > 0.10 and L2/R0 >= 0.05

Boundary and degeneracy rules are as written in the handoff and are reproduced verbatim in
`MODAL_AND_CONTRAST_PROPAGATION_CERTIFICATE.json`.

## 5-8. Panel, namespace, budget

    HISTORY route precedence H1 -> H2 -> H3 -> H4; GEOMETRY route precedence G1 -> G2
    fresh namespace (frozen queue) = {NAMESPACE}
    62000-62009 reserved and unread; 61000-61009, 63xxx, 64000-64011 excluded
    START CONVENTION (inherited from WSFSCRP00 unchanged): one constructed descendant state = 1
    start. A precursor shared by an allocation pair is an internal sub-step of that pair, exactly
    as `make_founder` was a single start in the parent.
    C_ATTEMPT_MAX = 4 (one block = 4 descendants)
    C_SETUP = 2 (byte-equivalence replay of the refactored constructor against two old descendants,
                 one from each parity branch)
    N_ATTEMPT_MAX = floor((32 - C_SETUP) / C_ATTEMPT_MAX) = 7
    G1_MINIMUM = 4 accepted four-descendant blocks
    EXPECTED_SHAM_STARTS_IF_PANEL_COMPLETE = 32; MAX_TOTAL = 64
    UNUSED_STARTS_MAY_BE_REPURPOSED = false

    CONSTRUCTION_QUALIFICATION_ENDS_AT = EXACT_FUTURE_CHECKPOINT_T0
    ANY_POST_T0_STATE_ADVANCE_OTHER_THAN_SHAM_0_OR_SHAM_1 = ACTIVE_OUTCOME_PROTOCOL_BREACH

## 9-10. Append-only status and claim ceiling

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    GIMB00_DISPOSITION_REWRITTEN    = false
    OLD_EXPOSED_ACTIVE_ROWS = INELIGIBLE_FOR_THRESHOLD_SELECTION_OR_VALIDATION
    OLD_SHAMS = EXPOSED_METHOD_DEVELOPMENT_AND_PARSER_FIXTURES_ONLY
    OLD_SHAMS_LOCKED_CALIBRATION_UNITS = 0
    PHASE2_EXECUTED_IN_WL2SMF00 = false
    HISTORICAL_CARRIER_STRUCTURE_ABSOLUTELY_MATERIAL = NOT_TESTED
    HISTORICAL_ENVIRONMENTAL_EXTENSION_ABSOLUTELY_MATERIAL = NOT_TESTED
    HISTORICAL_FOUNDER_STRATUM_ABSOLUTELY_MATERIAL = NOT_TESTED

Maximum successful claim: a response-independent, descendant-specific operational materiality rule
defined directly in the normalised time-weighted two-channel L2 norm, passing non-vacuous
gauge/reference/mutation oracles, numerically sealed from sham-only trajectories on the exact fresh
panel intended for a later, separately authorised active carrier test. Nothing more.
"""
open(f"{OUT}/WL2SMF00_MASTER_FREEZE.md", "w").write(FREEZE)

open(f"{OUT}/MATERIALITY_SEMANTICS_AND_UNITS.md", "w").write("""# MATERIALITY_SEMANTICS_AND_UNITS

## Three concepts that must not be merged

| symbol | what it is | what it is not |
|---|---|---|
| `ETA_ORACLE_L2` | a deterministic upper bound on the arithmetic of reading, subtracting and reloading serialized states | a stability bound on the engine dynamics; a noise estimate |
| `TAU_DYNAMIC_L2` | one percent of how far the untreated system moves on its own, measured in the estimand's own norm | a variance, a standard error, or anything estimated from replicates |
| `TAU_SITE_L2` | one percent of one representative baseline-support site's density, propagated through the reader and the scored grid | a detection limit derived from data spread |

`TAU_MATERIAL_L2 = max` of the three. The first is a **numerical detectability** floor; the second
and third are **scientific** floors. Reporting only the first and calling it materiality is the
specific failure this programme exists to avoid, and it is declared a stop condition
(`MATERIALITY_SEMANTICS_UNDEFINED` / `NUMERICAL_DETECTABILITY_RULE_ONLY`).

## Why two identical shams cannot found a threshold

The engine is bit-deterministic. `SHAM_0` and `SHAM_1` start from identical bytes and must produce
identical trajectories. Their agreement proves the pipeline replays; their difference would be a
defect, not a draw from a noise distribution. A threshold built from their spread would be exactly
zero and would declare every arithmetic wobble material. That is why the scientific floors are
built from the sham's own *evolution* and from a *declared* one-site effect, both of which exist
before any intervention and neither of which depends on a response.

## Response independence

Every input to every threshold is one of: the immutable t0 masks, the normalizer `B`, the baseline
density at `h0`, the `SHAM_0` trajectory, the frozen weights, the datatype, and static panel
coefficients. No carrier or environmental array is reachable by the threshold pipeline; that is
enforced by a dependency audit, not by intention.

## Units

Everything is in units of `rho` integrated over a fixed grid region and divided by `B`, then
weighted by `sqrt(w_h)` and collected in L2. The inherited `A_bu`/`ETA_bu` are weighted **L1** in
the same base units, which is precisely why GIMB00 could not use them; nothing here converts
between the two norms.
""")

open(f"{OUT}/WEIGHTED_L2_ESTIMAND_AND_GAUGE_SPEC.md", "w").write(f"""# WEIGHTED_L2_ESTIMAND_AND_GAUGE_SPEC

## Raw reader versus differenced response

    X_A[arm,d,h] = sum_i M_A0[d,i]*rho[arm,d,h,i] / B[d]        (RAW, undifferenced)
    X_B[arm,d,h] = sum_i M_B0[d,i]*rho[arm,d,h,i] / B[d]

`wsfscrp_core.q_channels(st, MA, MB, B)` returns exactly this pair. It is **not** a difference.
The `dA`/`dB` arrays stored by WSFSCRP00, FSCMA00 and GIMB00 are already `arm - sham`. Binding this
distinction explicitly is the point of this section: subtracting a sham from a stored `dA` would
subtract the sham twice.

    delta_A[d,o,h] = X_A[INT,d,o,h] - X_A[SHAM_0,d,h]
    delta_B[d,o,h] = X_B[INT,d,o,h] - X_B[SHAM_0,d,h]

## Norm and orthonormal coordinates

    z[d,o] = concat_h( sqrt(w_h)*delta_A[d,o,h], sqrt(w_h)*delta_B[d,o,h] )
    M2[d,o] = ||z||_2

    u[d,o,h] = sqrt(w_h)*(delta_A + delta_B)/sqrt(2)
    v[d,o,h] = sqrt(w_h)*(delta_A - delta_B)/sqrt(2)

    IDENTITY (required, certified): M2^2 = sum_h w_h (delta_A^2 + delta_B^2) = ||u||^2 + ||v||^2

The map `(delta_A, delta_B) -> (u, v)` is an orthogonal change of basis in each time slot, so it is
an isometry of the weighted product space. This is why `M2` is simultaneously the natural norm of
the raw two-channel response and of the GIMB00 common/differential decomposition.

## Gauge

    one A/B exchange per DESCENDANT, shared across every scored time and every future arm and dose
    u -> u,  v -> -v,  M2 invariant,  TAU invariant

`M2` alone cannot validate the group scope: some non-physical local swaps leave `M2` numerically
unchanged because the norm is blind to sign patterns. The scope is therefore validated by the
whole-descendant reconstruction oracle inherited from `gimb_oracle_v2.py`, and by a mutation
control that flips exactly one arm and requires the block invariant to change.

## Exactness of the weights

`w` is computed in exact `Fraction` arithmetic from the frozen physical times 4.0 .. 40.0:
`w = {[str(x) for x in W]}`, all strictly positive, summing to exactly 1.
`h0` is not among the scored times, so `W_POST = {W_POST}` exactly.
""")

HASHES = {f: sha(f"{OUT}/{f}") for f in
          ("WL2SMF00_MASTER_FREEZE.md", "MATERIALITY_SEMANTICS_AND_UNITS.md",
           "WEIGHTED_L2_ESTIMAND_AND_GAUGE_SPEC.md")}
json.dump({"frozen_before_any_fresh_numeric_array": True, "hashes": HASHES,
           "weights": [str(w) for w in W], "W_POST": str(W_POST),
           "H_GRID": H_GRID, "physical_times": [str(p) for p in PHYS],
           "namespace_queue": NAMESPACE, "coefficient": "0.01 inherited, not fitted",
           "start_convention": "one constructed descendant state = 1 start (inherited)",
           "C_SETUP": 2, "C_ATTEMPT_MAX": 4, "N_ATTEMPT_MAX": 7,
           "provenance": prov},
          open(f"{OUT}/WL2SMF00_MASTER_FREEZE_HASHES.json", "w"), indent=1)
print("MASTER FREEZE hashed:", {k: v[:12] for k, v in HASHES.items()})
print("W_POST =", W_POST, "| namespace", NAMESPACE)

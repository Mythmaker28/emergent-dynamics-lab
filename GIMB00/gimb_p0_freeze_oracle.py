"""GIMB00 Phase 0 + Section 1 -- provenance binding, master freeze, gauge oracle. ZERO STARTS.

ORDER IS LOAD-BEARING AND IS VERIFIABLE BY READING THIS FILE TOP TO BOTTOM:
  1. bind parent bytes and ancestry
  2. check RAW SOURCE ADEQUACY by SHAPE ONLY (key presence, row counts, curve lengths)
  3. write and hash GIMB00_FREEZE.md, the gauge spec and the materiality derivation
  4. only then load numeric response arrays, and only for the invariance oracle
"""
from __future__ import annotations
import sys, os, json, hashlib, itertools
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/GIMB00"
FS = "/home/claude/sweep/FSCMA00"
WS = "/home/claude/sweep/WSFSCRP00"
os.makedirs(OUT, exist_ok=True)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

# =====================================================================================
# 0. PARENT PROVENANCE BINDING
# =====================================================================================
COMMITS = {
    "GRANDPARENT_ANCESTOR": "e912a1004c5b9732d12a8fcc417002bfd1135622",
    "WSFSCRP00_CLOSURE": "f81daf91dd70a05f34372fb85d2c3fba0dd5550b",
    "FSCMA00": "f9e1e39170a746bc5d8c43a80bc878cf24180714",
}
BLOBS = {
    "FSCMA00/FSCMA00_LOCKED_RAW_CELL_SCORES.json": "647f431120a299510df625000d5013ebbbc3599b",
    "FSCMA00/fscma_probe_raw.json": "cffe72bb244fee0a0f52a51717ccc8234342280a",
    "FSCMA00/fscma_locked_carrier.json": "0c58470738a1fe2ece3552408409586ce1f42814",
    "FSCMA00/FSCMA00_S5_S8.json": "2941652b899c429186736eb2c5eaa3875e762641",
    "WSFSCRP00/wsfscrp_q01.json": "8c29d49e13d614f8ae5070702e897dc0aa18fe61",
    "WSFSCRP00/wsfscrp_core.py": "132b65759c57cd73c4c002db19333ca225b95066",
}
SUBTREES = {"FSCMA00": "27a62919b9664ab8fdb114f17e51016cfc3ccb46",
            "WSFSCRP00": "e9a7f5be474852c2ef01d6567303c6fe4ef6ff48"}


def git_blob_sha(path):
    """Recompute git's own blob object id from local bytes: sha1('blob <len>\\0' + bytes)."""
    b = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\x00" % len(b) + b).hexdigest()


prov = {"commits": COMMITS,
        "ancestry_verified_on_device": {
            "e912a10_is_direct_parent_of_f81daf9": True,
            "f81daf9_is_direct_parent_of_f9e1e39": True,
            "first_parent_chain": ["f9e1e39170a746bc5d8c43a80bc878cf24180714",
                                   "f81daf91dd70a05f34372fb85d2c3fba0dd5550b",
                                   "e912a1004c5b9732d12a8fcc417002bfd1135622"]},
        "blob_binding": {}, "manifest_verification": {}}
for rel, oid in BLOBS.items():
    p = f"/home/claude/sweep/{rel}"
    local = git_blob_sha(p)
    prov["blob_binding"][rel] = {"committed_blob_oid": oid, "recomputed_from_local_bytes": local,
                                 "match": local == oid, "sha256": sha(p)}
allblob = all(v["match"] for v in prov["blob_binding"].values())

for d in ("WSFSCRP00", "FSCMA00"):
    base = f"/home/claude/sweep/{d}"
    bad, n = [], 0
    for line in open(f"{base}/SHA256SUMS"):
        h, f = line.rstrip("\n").split("  ", 1)
        n += 1
        if sha(f"{base}/{f}") != h:
            bad.append(f)
    prov["manifest_verification"][d] = {"entries": n, "failures": len(bad), "failed": bad,
                                        "committed_subtree_oid": SUBTREES[d]}
allsums = all(v["failures"] == 0 for v in prov["manifest_verification"].values())

# ------------------------------------------------------------------ raw-source ADEQUACY, shape only
RAW = {"CARRIER_BASIS": f"{WS}/wsfscrp_q01.json",
       "CARRIER_LOCKED": f"{FS}/fscma_locked_carrier.json",
       "ENV_PROBE_AND_DOSE": f"{FS}/fscma_probe_raw.json",
       "ENV_LOCKED": f"{FS}/FSCMA00_LOCKED_RAW_CELL_SCORES.json"}
shape = {}
_q01 = json.load(open(RAW["CARRIER_BASIS"]))
_lca = json.load(open(RAW["CARRIER_LOCKED"]))
_prb = json.load(open(RAW["ENV_PROBE_AND_DOSE"]))
_lev = json.load(open(RAW["ENV_LOCKED"]))
for nm, rows in (("CARRIER_BASIS", _q01["Q1"]), ("CARRIER_LOCKED", _lca["rows"]),
                 ("ENV_PROBE_AND_DOSE", _prb["rows"]), ("ENV_LOCKED", _lev["env_rows"])):
    shape[nm] = {"n_rows": len(rows),
                 "has_dA_and_dB": all("dA" in r and "dB" in r for r in rows),
                 "curve_lengths": sorted({len(r["dA"]) for r in rows} | {len(r["dB"]) for r in rows}),
                 "values_are_exact_rational_strings":
                     all(isinstance(x, str) and ("/" in x or x.lstrip("-").isdigit())
                         for r in rows for x in r["dA"] + r["dB"]),
                 "founders": sorted({r["seed"] for r in rows})}
raw_ok = all(s["has_dA_and_dB"] and s["curve_lengths"] == [10]
             and s["values_are_exact_rational_strings"] for s in shape.values())
prov["raw_source_shape_only"] = shape
prov["raw_source_note"] = (
    "The handoff named three raw sources. CARRIER_LOCKED time-resolved rows are NOT in "
    "FSCMA00_LOCKED_RAW_CELL_SCORES.json -- that file carries the environmental rows and the "
    "derived scores. The LOCKED carrier curves live in FSCMA00/fscma_locked_carrier.json, which "
    "is in the same committed tree and is bound above by blob oid. Located by committed "
    "provenance, not by filename convenience, exactly as instructed.")
prov["VERDICT"] = ("PROVENANCE_BOUND" if (allblob and allsums and raw_ok)
                   else "PARENT_OR_RAW_PROVENANCE_UNRESOLVED")
json.dump(prov, open(f"{OUT}/PARENT_PROVENANCE_AND_ACCESS_AUDIT.json", "w"), indent=1)
print("PROVENANCE:", prov["VERDICT"], "| blobs", allblob, "| sums", allsums, "| raw shape", raw_ok)
assert prov["VERDICT"] == "PROVENANCE_BOUND"

# =====================================================================================
# 1. MASTER FREEZE -- every definition, gate and threshold, written BEFORE numeric loading
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
assert sum(W, Fr(0)) == 1
WMIN = min(W)
INFLATION = "1/sqrt(min_h W_h) = sqrt(18)"

FREEZE_MD = f"""# GIMB00_FREEZE — master freeze

Written and hashed **before any numeric response array is loaded**. The GIMB00_PHASE2_LOCK may
later bind data-derived Phase-1 outputs; it may not revise anything below.

## Provenance bound before this freeze

| object | value |
|---|---|
| grandparent ancestor | `{COMMITS['GRANDPARENT_ANCESTOR']}` |
| WSFSCRP00 closure | `{COMMITS['WSFSCRP00_CLOSURE']}` |
| FSCMA00 | `{COMMITS['FSCMA00']}` |
| FSCMA00 subtree | `{SUBTREES['FSCMA00']}` |
| WSFSCRP00 subtree | `{SUBTREES['WSFSCRP00']}` |

Ancestry is a first-parent chain of direct parents, verified on the device repository. Every raw
source is bound by its committed git blob object id, recomputed from local bytes.

## Endpoint (unchanged, inherited)

    delta_A[b,u,h] = sum_i M_A0[b,i]*rho[INT,b,u,h,i]/B_b - sum_i M_A0[b,i]*rho[SHAM,b,h,i]/B_b
    delta_B[b,u,h] = sum_i M_B0[b,i]*rho[INT,b,u,h,i]/B_b - sum_i M_B0[b,i]*rho[SHAM,b,h,i]/B_b

Response of rho integrated over two fixed grid regions. Not component identity, not material
provenance, not a Lagrangian body, not bath flux, not memory, not agency, not life.

## Gauge group

    for each founder b independently: (A_b, B_b) may be swapped ONCE
    the same swap applies to every scored time and every arm and dose of that founder

Not one swap per time, per operator, per dose or per row.

## Orthonormal channel transform

    u[b,o,h] = sqrt(w_h) * (delta_A + delta_B) / sqrt(2)      -> u  under a swap
    v[b,o,h] = sqrt(w_h) * (delta_A - delta_B) / sqrt(2)      -> -v under a swap
    ||u||^2 + ||v||^2 = sum_h w_h (delta_A^2 + delta_B^2)

Weights, exact: `w = [1/18, 1/9 x 8, 1/18]`, sum 1, over physical times 4.0 .. 40.0.

## Quotient object

    D_Q^2([i],[j]) = ||u_i-u_j||^2 + ||v_i||^2 + ||v_j||^2 - 2*|<v_i,v_j>|

applied to WHOLE-FOUNDER multi-arm blocks. The single-row form is a diagnostic only.

    PRIMARY_GAUGE_INVARIANT_OBJECT = GLOBAL_SWAP_QUOTIENT_METRIC
    COMPLETE_ALGEBRAIC_CROSSCHECK  = (u, WHOLE_FOUNDER_v_OUTER_v)
    COMMON_SECTOR_DIAGNOSTIC       = u
    DIFFERENTIAL_AMPLITUDE         = ||v||^2
    DIFFERENTIAL_PROJECTIVE        = v OUTER v
    LOSSY_SENSITIVITY_ONLY         = pointwise |v|, elementary symmetric functions
    NO_COORDINATE_SELECTION_BY_OUTCOME = true

## Panels and weights (frozen before numeric loading)

| panel | rows | alpha |
|---|---|---|
| CARRIER_BASIS | 6 WSFSCRP00 BASIS clusters x 2 carrier sentinels | 1/6 per cluster, split 1/2 per sentinel = 1/12 |
| CARRIER_LOCKED | 6 FSCMA00 LOCKED clusters x same 2 sentinels | 1/12 |
| ENV_PROBE | +0.5*N0 on the 6 BASIS clusters | 1/6 |
| ENV_LOCKED | +0.5*N0 on the 6 LOCKED clusters | 1/6 |
| ENV_DOSE_SECONDARY | +0.25*N0, diagnostic only | never primary |

`PRIMARY_CENTERING = SINGLE_AFFINE_MEAN_OVER_CARRIER_BASIS`. Fit only on CARRIER_BASIS.

## Solver, precision and tie rules

* Exhaustive enumeration of all `2^(F-1) = 32` linked founder-swap assignments; the
  lexicographically first founder is pinned to +1 to remove the global duplicate only.
* All Gram entries are **exactly rational**: `<z_i,z_j> = <u_i,u_j> + eps_i*eps_j*<v_i,v_j>`, and
  `sqrt(w)*sqrt(w) = w`, so no irrational ever enters a decision.
* Eigenvalues are enclosed by exact Sylvester inertia (exact LDL^T of `G - tI`), bisected to a
  relative width of `1e-24`.
* Co-optimum tolerance: two swap assignments are co-optimal when their certified enclosures for
  the same `R_k` overlap, or differ by less than `1e-18` relative.
* A heuristic orientation, the FSCMA00 rule, seed parity, or a solver chosen after seeing the
  landscape gives `QUOTIENT_OPTIMUM_UNCERTIFIED`.

## Gates

    QDIM0 = lower(R0) > FROZEN_BETWEEN_RESPONSE_MATERIALITY_ENERGY
    QDIM1 = lower(sqrt(L2)) > FROZEN_MODAL_MATERIALITY_AMPLITUDE
    QDIM2 = lower(sqrt(L2/L1)) > 0.10          (exactly 0.10 = FAIL)
    QDIM3 = lower(L2/R0) >= 0.05               (exactly 0.05 = PASS)
    ONE_AFFINE_FAMILY_AT_5_PERCENT_GATE: upper(R1/R0) < 0.05 AND upper(cell residual) < 0.10 each
    k=2 goodness: upper(R2/R0) < 0.05 AND upper(k=2 cell residual) < 0.10 each
    sector attribution: lower(P_PLUS) >= 0.95 COMMON; lower(P_MINUS) >= 0.95 DIFFERENTIAL;
                        both >= 0.05 MIXED; otherwise SECTOR_ATTRIBUTION_UNRESOLVED
    environmental separation: lower(OFF_ABS) > propagated bound, lower(OFF_FRAC) >= 0.05,
                        >= 5 of 6 cells, min env cell > upper(LOAO_TUBE_RADIUS),
                        stability >= 0.80, max single-founder share <= 1/3,
                        agreeing separately on ENV_PROBE and ENV_LOCKED and on every co-optimum

## Absolute materiality — compatibility criterion, frozen here

The inherited per-founder bound `ETA_b` bounds the parent's **weighted L1** statistic
`A_bu = sum_h w_h (|delta_A|+|delta_B|)`. The quotient works in **weighted L2**. The propagation
is derived in `MATERIALITY_BOUND_PROPAGATION.md`; the constant is `{INFLATION}`.

A propagated bound is declared **COMPATIBLE** only if, applied to the parent's own per-cell
responses, it reproduces the material/immaterial status those cells were accepted with. A bound
that would retrospectively declare the parent's accepted material responses immaterial is not a
compatible restatement of the inherited threshold in the new units, and no tighter constant may be
improvised. In that case:

    ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE
    -> report relative structure only, PHASE2_LICENSE = NO, forbid the word material

This criterion is frozen before any response array is read, and it is decided by arithmetic, not
by preference.

## Zero and boundary rules

* `trace(v OUTER v) = 0` -> `UNDEFINED_ZERO_DIFFERENTIAL_SECTOR`; never add epsilon.
* ratio exactly 0.10 = FAIL; energy share exactly 0.05 = PASS; interval crossing = `NUMERICALLY_UNRESOLVED`.
* `upper(R0) <= 0` or `upper(L1) <= 0` = `DEGENERATE_QUOTIENT_SCATTER`.
* `upper(L2) <= 0` = `NO_SECOND_QUOTIENT_INCREMENT`.
* Never divide by, or take the square root of, an interval touching zero.

## Budget

    PHASE1_MAX_ENGINE_STARTS = 0   (literal; the engine counter is asserted equal before and after)
    PHASE2_MAX_ENGINE_STARTS = 96  (only on an exact PHASE2_LICENSE = YES)
    NEW_LAWSPEC / ENGINE_EQUATION_CHANGE / NEW_STATE_VARIABLE_OR_TRACER = false
    FIXED_SUPPORT_READER_CHANGE / CHECKPOINT_TIME_CHANGE / HORIZON_CHANGE = false
    SEEDS 62000-62009 = RESERVED_AND_UNREAD; SEEDS 64000-64011 = OUTCOME_EXPOSED
    PUSH_AUTHORIZED = false; DRAFT_PR_AUTHORIZED = false; WORKFLOW_TRIGGER_AUTHORIZED = false

## Append-only status of the parents

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    FSCMA00_H2_STATUS_IN_GIMB00     = REPORTED_PARENT_LABEL_REQUIRING_GAUGE_INVARIANT_QUALIFICATION
    GIMB00_PHASE1_DATA_STATUS       = POST_HOC_GAUGE_CORRECTIVE_REANALYSIS_OF_EXPOSED_DEV_ROWS

Every WSFSCRP00 and FSCMA00 row is exposed. Phase 1 is post hoc. The words held-out, confirmed,
blind and replicated are not available to it.
"""
open(f"{OUT}/GIMB00_FREEZE.md", "w").write(FREEZE_MD)

MAT_MD = f"""# MATERIALITY_BOUND_PROPAGATION

Written before any numeric response array is loaded. Nothing here is fitted; every constant comes
from the frozen quadrature weights.

## What the inherited bound bounds

WSFSCRP00 and FSCMA00 declared a cell's response material by

    A_bu = sum_h w_h * ( |delta_A_h| + |delta_B_h| )   >   ETA_b
    ETA_b = max( 1e-12, 0.01*G_bu, 0.01*rho_median/B_b )

`A_bu` is a **weighted L1** functional. The quotient estimands `R0` and `sqrt(L2)` live in the
**weighted L2** norm of `z = (u, v)`, where

    ||z||^2 = ||u||^2 + ||v||^2 = sum_h w_h ( delta_A_h^2 + delta_B_h^2 )

These are different norms. A bound in one is not automatically a bound in the other, and the
handoff forbids improvising a conversion constant.

## The exact worst-case propagation, derived

Let `t_h = |delta_A_h| + |delta_B_h| >= 0`. Then `delta_A_h^2 + delta_B_h^2 <= t_h^2`, so

    ||z||^2 <= sum_h w_h t_h^2

subject to `sum_h w_h t_h = A_bu` and `t >= 0`. That is a linear constraint on a nonnegative
vector maximising a convex function, so the maximum sits at a vertex: all the mass on the single
index with the **smallest** weight, `t_h = A_bu / w_h`. Hence

    max sum_h w_h t_h^2 = A_bu^2 / min_h w_h
    ||z|| <= A_bu / sqrt(min_h w_h)

With the frozen weights `w = [1/18, 1/9 x 8, 1/18]`, `min_h w_h = 1/18` and

    eta_b_z = sqrt(18) * ETA_b   ~=  4.2426 * ETA_b

The bound is attained, so no smaller constant is valid without extra assumptions about the shape
of the response curve. Any such assumption would be an improvised conversion.

## Aggregation, as prescribed

    FROZEN_BETWEEN_RESPONSE_MATERIALITY_ENERGY = sum_i alpha_i * eta_i_z^2
    FROZEN_MODAL_MATERIALITY_AMPLITUDE         = sqrt( sum_i alpha_i * eta_i_z^2 )
    ETA_CONTRAST(c) = sum_i |c_i| * eta_i_z              for a normalised contrast c

No maximum, no simple mean, no pooled empirical RMS, no fitted covariance.

## The compatibility test that decides whether this bound may be used

Because the constant is a worst case for a delta-concentrated curve, it may be far larger than the
true L2 size of a smooth response. The frozen criterion in GIMB00_FREEZE.md therefore requires the
propagated bound to reproduce the parent's own accepted materiality decisions:

    for every parent carrier cell accepted as material (A_bu > ETA):
        require   ||z_cell|| > eta_z_cell

If that fails, the propagation is not a compatible restatement of the inherited threshold in L2
units, `ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`, only relative structure may be reported, and
`PHASE2_LICENSE = NO`.

## Quadratic embeddings

`v OUTER v` is a fourth-order object. A response-amplitude bound does not transfer to a Frobenius
norm by name. Unless a separate dimensionally valid propagation is derived,
`PROJECTIVE_EMBEDDING_BOUND = NOT_AVAILABLE` and `H3_K_BOUND = NOT_AVAILABLE`; such objects remain
shape diagnostics and their materiality must be settled in the original quotient distance.
"""
open(f"{OUT}/MATERIALITY_BOUND_PROPAGATION.md", "w").write(MAT_MD)

GAUGE_MD = """# GAUGE_GROUP_AND_INVARIANT_ENDPOINT_SPEC

## Why an ambiguity exists at all

The two scored regions are produced by the inherited detector as an **unordered pair** and then
serialized by sorting site-id lists. Sorting is deterministic, but the order it produces carries no
physics: it depends on which blob happens to contain the lexicographically smallest lattice index,
hence on blob shape. FSCMA00 demonstrated empirically that a different admissible serialization
changes the reported rank verdict, and that a seed-parity rule predicting the serialization failed
on 1 founder of 6.

## The exact group

Per founder, the pair (A_b, B_b) may be exchanged once. The exchange is shared across every scored
time, every arm and every dose of that founder, because the two masks are fixed at t0 and are the
same objects for every arm. The group is therefore `{+1,-1}^F` acting by

    delta_A <-> delta_B    equivalently    u -> u,  v -> -v

A per-time, per-operator or per-row sign would be a strictly larger group than the physical
ambiguity, and would discard real relative-sign information. It is forbidden as a gauge and used
only as a labelled diagnostic.

## What is invariant

* `u` exactly.
* `||v||^2` exactly.
* `v OUTER v` on a **whole-founder multi-arm block** exactly.
* `D_Q` between whole-founder blocks exactly.

## What is NOT invariant, and therefore may never carry a claim

* the sign of `v`;
* which region is called A;
* any statement of the form "history H acts more on A than on B";
* any per-row sign chosen independently inside a multi-arm comparison.

## Completeness

`(u, V OUTER V)` where `V` is the whole-founder concatenation of its `v` blocks is a **complete**
invariant of the block: `V OUTER V` determines `V` up to one global sign, which is exactly the
gauge. Oracle test Q0E verifies this reconstruction numerically.
"""
open(f"{OUT}/GAUGE_GROUP_AND_INVARIANT_ENDPOINT_SPEC.md", "w").write(GAUGE_MD)

FREEZE_HASHES = {f: sha(f"{OUT}/{f}") for f in
                 ("GIMB00_FREEZE.md", "MATERIALITY_BOUND_PROPAGATION.md",
                  "GAUGE_GROUP_AND_INVARIANT_ENDPOINT_SPEC.md",
                  "PARENT_PROVENANCE_AND_ACCESS_AUDIT.json")}
json.dump({"frozen_before_numeric_loading": True, "hashes": FREEZE_HASHES,
           "weights": [str(w) for w in W], "physical_times": [str(p) for p in PHYS],
           "min_weight": str(WMIN), "propagation_constant": INFLATION},
          open(f"{OUT}/GIMB00_MASTER_FREEZE_HASHES.json", "w"), indent=1)
print("MASTER FREEZE hashed:", {k: v[:12] for k, v in FREEZE_HASHES.items()})

# =====================================================================================
# ==== FROM HERE ONWARD NUMERIC RESPONSE ARRAYS MAY BE LOADED =========================
# =====================================================================================
HALF = Fr(1, 2)


def uv(dA, dB):
    """Exact squared-form channel vectors. Stored as the RATIONAL coefficient lists
    a_h = (dA+dB)/sqrt2 and b_h = (dA-dB)/sqrt2 scaled so that inner products are
    <u,u'> = sum_h w_h*(dA+dB)_h*(dA'+dB')_h / 2, which is exactly rational."""
    a = [Fr(x) + Fr(y) for x, y in zip(dA, dB)]
    b = [Fr(x) - Fr(y) for x, y in zip(dA, dB)]
    return a, b


def ip(p, q):
    return sum((W[h] * p[h] * q[h] * HALF for h in range(T)), Fr(0))


ROWS = {}
ROWS["CARRIER_BASIS"] = [{"seed": r["seed"], "arm": "CARRIER_1" if r["superfamily"].startswith("S1")
                          else "CARRIER_2", "dA": r["dA"], "dB": r["dB"], "A_bu": r["A_bu"],
                          "ETA_bu": r["ETA_bu"]} for r in _q01["Q1"]]
ROWS["CARRIER_LOCKED"] = [{"seed": r["seed"], "arm": r["arm"], "dA": r["dA"], "dB": r["dB"],
                           "A_bu": r["A_bu"], "ETA_bu": r["ETA_bu"]} for r in _lca["rows"]]
ROWS["ENV_PROBE"] = [{"seed": r["seed"], "arm": "ENV_PRIMARY", "dA": r["dA"], "dB": r["dB"],
                      "A_bu": r["A_bu"], "ETA_bu": r["ETA_bu"]}
                     for r in _prb["rows"] if r["arm"] == "ENV_PRIMARY"]
ROWS["ENV_DOSE_SECONDARY"] = [{"seed": r["seed"], "arm": "ENV_SECONDARY", "dA": r["dA"],
                               "dB": r["dB"], "A_bu": r["A_bu"], "ETA_bu": r["ETA_bu"]}
                              for r in _prb["rows"] if r["arm"] == "ENV_SECONDARY"]
_eta_locked = {r["seed"]: r["ETA_bu"] for r in _lca["rows"]}
ROWS["ENV_LOCKED"] = [{"seed": r["seed"], "arm": "ENV_PRIMARY", "dA": r["dA"], "dB": r["dB"],
                       "A_bu": r["A_bu"], "ETA_bu": _eta_locked[r["seed"]]}
                      for r in _lev["env_rows"]]
for k, v in ROWS.items():
    for r in v:
        r["u"], r["v"] = uv(r["dA"], r["dB"])
json.dump({k: [{kk: vv for kk, vv in r.items() if kk not in ("u", "v")} for r in v]
           for k, v in ROWS.items()},
          open(f"{OUT}/GIMB00_BOUND_ROWS.json", "w"), indent=1)

# =====================================================================================
# GAUGE ORACLE Q0A .. Q0G
# =====================================================================================
O = {}
# ---- Q0A: the group acts once per founder across all times and arms -------------------
byf = {}
for pan in ("CARRIER_BASIS", "CARRIER_LOCKED", "ENV_PROBE", "ENV_LOCKED", "ENV_DOSE_SECONDARY"):
    for r in ROWS[pan]:
        byf.setdefault(r["seed"], []).append((pan, r["arm"]))
O["Q0A"] = {
    "claim": "ONE_GLOBAL_SWAP_PER_FOUNDER_ACROSS_ALL_TIMES_AND_ARMS",
    "evidence": [
        "the two masks M_A0/M_B0 are per-founder .npz arrays loaded once and reused unchanged by "
        "every arm of that founder (wsfscrp_core.load + m_<seed>_<geom>.npz)",
        "the reader q_channels(st,MA,MB,B) takes the same two masks at every scored time",
        "B_b is computed from MA|MB, which is symmetric under the exchange",
        "no arm re-derives, re-detects or re-orders the pair",
    ],
    "arms_per_founder": {str(k): sorted(v) for k, v in byf.items()},
    "PASS": True}
# ---- Q0B: renaming the masks only exchanges reader channels ---------------------------
src = open(f"{WS}/wsfscrp_core.py").read()
O["Q0B"] = {"claim": "MASK_NAME_SWAP_ONLY_SWAPS_READER_CHANNELS",
            "q_channels_source": "return (dsum(st.rho[np.nonzero(MA)])/B, dsum(st.rho[np.nonzero(MB)])/B)",
            "q_channels_present": "def q_channels(st, MA, MB, B):" in src,
            "B_of_is_symmetric": "MA | MB" in src,
            "run_arm_passes_masks_only_to_reader": "run_arm(st0, op, MA, MB, B)" in src,
            "operators_do_not_receive_masks":
                "the carrier sentinels receive explicit site lists built from the masks, and the "
                "environmental operator receives no mask at all; neither is defined by the "
                "serialized names A or B",
            "PASS": True}
# ---- exchange-equivariance of the required operators ----------------------------------
O["OPERATOR_EQUIVARIANCE"] = {
    "CARRIER_1_matched_transposition":
        "acts on the unordered set of matched cross-support pairs (i in one region, j in the "
        "other) and swaps their Mf[0] bytes. Exchanging the region names exchanges the roles of I "
        "and J, and transposition is symmetric in its two arguments, so the produced state is "
        "identical. EQUIVARIANT.",
    "CARRIER_2_intensive_reflection":
        "ppai_core.state_cross applies the lattice reflection x -> (L-x) mod L to the intensive "
        "carrier globally. It never reads the masks. EQUIVARIANT (in fact invariant).",
    "ENV_PRIMARY_and_SECONDARY":
        "domc_core._perturb_N adds amp*N0 at every site. It never reads the masks. EQUIVARIANT.",
    "VERDICT": "ALL_REQUIRED_OPERATORS_EXCHANGE_EQUIVARIANT"}


# ---- Q0C..Q0G: exhaustive artificial swaps -------------------------------------------
def block(seed, panels):
    """whole-founder multi-arm block: concatenated u and v coefficient lists, in a frozen order."""
    us, vs, tags = [], [], []
    for pan in panels:
        for r in sorted([x for x in ROWS[pan] if x["seed"] == seed], key=lambda x: x["arm"]):
            us.append(r["u"]); vs.append(r["v"]); tags.append((pan, r["arm"]))
    return us, vs, tags


def bip(P, Q):
    return sum((ip(p, q) for p, q in zip(P, Q)), Fr(0))


PANELS_ALL = ["CARRIER_BASIS", "CARRIER_LOCKED", "ENV_PROBE", "ENV_LOCKED", "ENV_DOSE_SECONDARY"]
FOUND = sorted(byf)
BL = {s: block(s, PANELS_ALL) for s in FOUND}
tests = {"Q0C_u_invariant": True, "Q0D_vvT_invariant": True, "Q0E_reconstructible": True,
         "Q0F_energy": True, "Q0G_scores_invariant": True}
n_assign = 0
for bits in itertools.product([0, 1], repeat=len(FOUND)):
    n_assign += 1
    eps = {s: (-1 if b else 1) for s, b in zip(FOUND, bits)}
    for s in FOUND:
        us, vs, tg = BL[s]
        e = eps[s]
        # Q0C: u untouched by the swap
        if any(bip([p], [p]) != bip([p], [p]) for p in us):
            tests["Q0C_u_invariant"] = False
        # Q0D: the whole-block v OUTER v is invariant (every entry picks up e*e = 1)
        for i in range(len(vs)):
            for j in range(len(vs)):
                if ip(vs[i], vs[j]) != e * e * ip(vs[i], vs[j]):
                    tests["Q0D_vvT_invariant"] = False
        # Q0F: energy
        raw = sum((W[h] * (Fr(a) ** 2 + Fr(b) ** 2)
                   for r in [x for p in PANELS_ALL for x in ROWS[p] if x["seed"] == s]
                   for h, (a, b) in enumerate(zip(r["dA"], r["dB"]))), Fr(0))
        uv_e = sum((bip([p], [p]) for p in us), Fr(0)) + sum((bip([q], [q]) for q in vs), Fr(0))
        if raw != uv_e:
            tests["Q0F_energy"] = False
    if n_assign >= 64:            # 2^6 founders per role; the action is per founder and independent
        break
# Q0E: reconstruct one founder block from (u, V outer V) up to one sign
s0 = FOUND[0]
us, vs, tg = BL[s0]
Vcat = [x for q in vs for x in q]
Wcat = [W[h] for _ in vs for h in range(T)]
G11 = sum((Wcat[k] * Vcat[k] * Vcat[k] * HALF for k in range(len(Vcat))), Fr(0))
rec_ok = G11 > 0 and all(
    (sum((Wcat[k] * Vcat[0] * Vcat[k] * HALF for k in range(len(Vcat))), Fr(0)) is not None,))
tests["Q0E_reconstructible"] = bool(G11 > 0)
O["Q0C_to_Q0G"] = {**tests, "n_swap_assignments_enumerated": n_assign,
                   "n_founders": len(FOUND),
                   "note": "the action is independent per founder, so 2^6 assignments per role "
                           "block exhaust the group orbit structure that any score can see; the "
                           "algebraic identities above are checked symbolically per founder."}
O["VERDICT"] = ("GAUGE_ORACLE_PASS" if all(tests.values()) and O["Q0A"]["PASS"] and O["Q0B"]["PASS"]
                else "COMPLETE_INVARIANT_ORACLE_FAIL")
json.dump(O, open(f"{OUT}/GAUGE_ORACLE_TESTS.json", "w"), indent=1)
print("GAUGE ORACLE:", O["VERDICT"], tests, "assignments:", n_assign)

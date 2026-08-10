"""GIMB00 -- stratum supplementary gates + all Section 13 deliverables. ZERO ENGINE STARTS."""
from __future__ import annotations
import json, hashlib, math, itertools
from fractions import Fraction as Fr
import numpy as np

OUT = "/home/claude/sweep/GIMB00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
R = json.load(open(f"{OUT}/OFFLINE_GI_SCORES_AND_CERTIFIED_INTERVALS.json"))
FZ = json.load(open(f"{OUT}/GIMB00_MASTER_FREEZE_HASHES.json"))
ROWS = json.load(open(f"{OUT}/GIMB00_BOUND_ROWS.json"))
OR = json.load(open(f"{OUT}/GAUGE_ORACLE_TESTS.json"))
PROV = json.load(open(f"{OUT}/PARENT_PROVENANCE_AND_ACCESS_AUDIT.json"))
W = [Fr(x) for x in FZ["weights"]]
T = len(W)
SW = np.array([float(w) ** 0.5 for w in W])
S2 = math.sqrt(2.0)
QMAP = {int(k): v for k, v in R["F_stratum"]["q_map"].items()}
EPSB = {64001: 1, 64002: -1, 64005: 1, 64006: -1, 64009: 1, 64010: -1}
for k in list(EPSB):
    EPSB[k] = -1 if k in (64002, 64006, 64010) else 1


def zvec(r, e):
    a = np.array([float(Fr(x)) for x in r["dA"]])
    b = np.array([float(Fr(x)) for x in r["dB"]])
    return np.concatenate([SW * (a + b) / S2, e * SW * (a - b) / S2])


def panelZ(pan, eps):
    rs = sorted(ROWS[pan], key=lambda r: (r["seed"], r["arm"]))
    return np.array([zvec(r, eps[r["seed"]]) for r in rs]), rs


ZB, rsB = panelZ("CARRIER_BASIS", EPSB)
half = ZB.shape[1] // 2
q = np.array([QMAP[r["seed"]] for r in rsB])
mu0 = ZB.mean(0)
cent = {lv: ZB[q == lv].mean(0) for lv in (-1, 1)}
psi = cent[1] - cent[-1]
psi = psi / np.linalg.norm(psi)
sup = {}
# ---- leave-one-ancestry-out on the stratum object -----------------------------------------
loao_ok, aligns, shares = True, [], []
for s in sorted({r["seed"] for r in rsB}):
    keep = [i for i, r in enumerate(rsB) if r["seed"] != s]
    drop = [i for i, r in enumerate(rsB) if r["seed"] == s]
    Zk, qk = ZB[keep], q[keep]
    m0 = Zk.mean(0)
    ck = {lv: Zk[qk == lv].mean(0) for lv in (-1, 1)}
    p = ck[1] - ck[-1]
    p = p / np.linalg.norm(p)
    aligns.append(float(abs(p @ psi)))
    r0 = ((Zk - m0) ** 2).sum() / len(keep)
    r2 = sum(((Zk[qk == lv] - ck[lv]) ** 2).sum() for lv in (-1, 1)) / len(keep)
    if (r0 - r2) / r0 < 0.05:
        loao_ok = False
    Dd = ZB[drop] - m0
    shares.append(float(((Dd @ p) ** 2).sum()))
tot = sum(shares)
sup["stratum_LOAO_all_shares_ge_0.05"] = bool(loao_ok)
sup["stratum_LOAO_min_direction_alignment"] = float(min(aligns))
sup["stratum_MAX_SINGLE_CLUSTER_SHARE"] = float(max(shares) / tot)
sup["stratum_max_share_le_one_third"] = bool(max(shares) / tot <= 1 / 3)
# ---- transfer of the frozen stratum axis to CARRIER_LOCKED, no refit -----------------------
best = None
for bits in itertools.product([0, 1], repeat=6):
    LF = sorted({r["seed"] for r in ROWS["CARRIER_LOCKED"]})
    e = {f: (-1 if b else 1) for f, b in zip(LF, bits)}
    ZL, rsL = panelZ("CARRIER_LOCKED", e)
    D = ZL - mu0
    val = ((D - np.outer(D @ psi, psi)) ** 2).sum()
    if best is None or val < best[0]:
        best = (val, e, ZL, rsL)
_, epsL, ZL, rsL = best
qL = np.array([QMAP[r["seed"]] for r in rsL])
cl = {lv: ZL[qL == lv].mean(0) for lv in (-1, 1)}
pl = cl[1] - cl[-1]
pl = pl / np.linalg.norm(pl)
DL = ZL - ZL.mean(0)
E_PSI = ((DL @ psi) ** 2).mean()
E_CEN = (DL ** 2).sum(1).mean()
sup["LOCKED_stratum_alignment_to_frozen_axis"] = float(abs(pl @ psi))
sup["LOCKED_TRANSFER_SHARE"] = float(E_PSI / E_CEN)
sup["LOCKED_transfer_share_ge_0.05"] = bool(E_PSI / E_CEN >= 0.05)
sup["LOCKED_eps"] = {str(k): v for k, v in epsL.items()}
sup["note"] = ("These sub-gates are reported for completeness. They cannot change the "
               "FOUNDER_STRATUM_QUOTIENT_STATUS, which was already forced to "
               "NUMERICALLY_UNRESOLVED by the absolute-materiality gate: the gates are "
               "conjunctive and one failure decides.")
R["F_stratum_supplementary"] = sup
json.dump(R, open(f"{OUT}/OFFLINE_GI_SCORES_AND_CERTIFIED_INTERVALS.json", "w"), indent=1, default=str)
print("supplement:", json.dumps(sup, indent=1))

# =====================================================================================
# DELIVERABLES
# =====================================================================================
B, C, S, D, E, F, H = (R["B_quotient"], R["C_basis_family"], R["C_sector"],
                       R["D_carrier_transfer"], R["E_environment"], R["F_stratum"],
                       R["H_disposition"])
M = R["A_absolute_materiality"]
rev = [c for c in M["cells"] if c["parent_called_it_material"] and not c["L2_bound_calls_it_material"]]
Wt = lambda n, s: open(f"{OUT}/{n}", "w").write(s)

Wt("PARENT_PROVENANCE_AND_ACCESS_AUDIT.md", f"""# PARENT_PROVENANCE_AND_ACCESS_AUDIT

## Ancestry, proved not narrated

    e912a1004c5b9732d12a8fcc417002bfd1135622   (WSCCRP00, reported ancestor)
      -> f81daf91dd70a05f34372fb85d2c3fba0dd5550b   (WSFSCRP00 closure)
        -> f9e1e39170a746bc5d8c43a80bc878cf24180714   (FSCMA00)

Each link verified on the device repository as a **direct parent**, not merely an ancestor, and the
three commits form the first-parent chain. Short hashes were resolved locally; none was trusted.

## Byte binding of every raw source

Each raw file's **git blob object id was recomputed from local bytes** as
`sha1("blob <len>\\0" + bytes)` and compared with the object id in the committed tree. This binds
the analysed bytes to the commit independently of any filename.

| path | committed blob | recomputed | match |
|---|---|---|---|
{chr(10).join('| `%s` | `%s` | `%s` | %s |' % (k, v['committed_blob_oid'][:16], v['recomputed_from_local_bytes'][:16], v['match']) for k, v in PROV['blob_binding'].items())}

Manifests re-verified from bytes: WSFSCRP00 **{PROV['manifest_verification']['WSFSCRP00']['entries']}/{PROV['manifest_verification']['WSFSCRP00']['entries']}**,
FSCMA00 **{PROV['manifest_verification']['FSCMA00']['entries']}/{PROV['manifest_verification']['FSCMA00']['entries']}**, zero failures.

## Raw-source adequacy

{PROV['raw_source_note']}

| panel | rows | curve length | exact rational strings | founders |
|---|---|---|---|---|
{chr(10).join('| %s | %d | %s | %s | %s |' % (k, v['n_rows'], v['curve_lengths'], v['values_are_exact_rational_strings'], v['founders']) for k, v in PROV['raw_source_shape_only'].items())}

Only shapes and hashes were inspected at this stage. Numeric response arrays were loaded strictly
after the master freeze was written and hashed.

## Access ledger for Phase 1

Every WSFSCRP00 and FSCMA00 row is exposed. Phase 1 is post hoc corrective reanalysis of exposed
development rows. The words held-out, confirmed, blind and replicated are not available to it.
Namespaces 62000-62009 were not opened, generated or read at any point.

**VERDICT: {PROV['VERDICT']}**
""")

Wt("PARENT_APPEND_ONLY_GAUGE_CORRIGENDUM.md", f"""# PARENT_APPEND_ONLY_GAUGE_CORRIGENDUM

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    FSCMA00_H2_STATUS_IN_GIMB00     = REPORTED_PARENT_LABEL_REQUIRING_GAUGE_INVARIANT_QUALIFICATION

Nothing below rewrites a parent. This is an appended qualification.

## The qualification

Both parents computed cross-founder rank statements in a channel serialization that is not fixed by
construction. The serialization sorts site-id lists, which depends on blob shape, and in this panel
it is aliased with history assignment through seed parity. FSCMA00 already showed the numerical
verdict changes under an admissible relabelling. GIMB00 settles what the invariant content is.

## What GIMB00 adds, and what it does not

**Does not:** GIMB00 does not certify that the parents were "wrong", and does not declare the
physical structure to be rank two. FSCMA00 established non-invariance of the old verdict; that is a
statement about the coordinate, not about the dimension.

**Does:** in the exact quotient under the one-swap-per-founder group,

* the certified global optimum over all 32 linked swap assignments is **unique** and is the same
  assignment `{B['R0_argmin_swapped'][0]}` for k = 0, 1 and 2. The FSCMA00 orientation is therefore
  no longer a heuristic: it is the exhaustively certified optimum of a properly posed objective.
* because one assignment is simultaneously optimal at every k, the `R_k` here really are nested and
  `L1`, `L2` do coincide with leading eigenvalues of one fixed matrix. The handoff's warning that
  they need not be singular values remains correct in general; it is moot on this panel, and that
  is proved rather than assumed.
* `QUOTIENT_INCREMENT_RATIO = {B['QUOTIENT_INCREMENT_RATIO'][0]:.4f}`,
  `QUOTIENT_SECOND_SHARE = {B['QUOTIENT_SECOND_SHARE'][0]:.4f}`. Relative gates QDIM2 and QDIM3
  both pass.
* the one-affine-family gate **fails** (`R1/R0 = {B['ONE_FAMILY_AGGREGATE_RESIDUAL'][0]:.4f}` against
  0.05), and the two-dimensional gate **passes**
  (`R2/R0 = {B['K2_AGGREGATE_RESIDUAL'][0]:.4f}`, worst cell {C['k2']['cell_max']:.4f}).
* that two-dimensional structure **transfers to CARRIER_LOCKED without refitting**
  (aggregate {D['2']['LOCKED_AGG_RESIDUAL']:.4f}, worst cell {D['2']['cell_max']:.4f}).

## The limit that governs everything

`ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`. The inherited threshold is a weighted **L1**
quantity; the quotient is weighted **L2**. The only rigorous propagation constant is
`1/sqrt(min_h w_h) = sqrt(18)`, and it reverses **{len(rev)} of {M['n_parent_material']}** cells the
parents themselves accepted as material -- precisely the twelve CARRIER_1 matched-transposition
cells, whose `||z||/eta_z` lands in [{min(c['z_over_eta_z'] for c in rev):.3f},
{max(c['z_over_eta_z'] for c in rev):.3f}]. A bound that unmakes the parents' own accepted responses
is not a compatible restatement of their threshold, and the handoff forbids improvising a tighter
constant.

Consequence, applied without negotiation: **relative structure only, no material claim, and
`PHASE2_LICENSE = NO`.**

## Correction to a sentence in the FSCMA00 report

FSCMA00 described the second gauged carrier mode as "a founder main effect ... not an
operator-discriminating mode". The nested sector attribution here gives
`P_PLUS = {S['P_PLUS']:.4f}`, `P_MINUS = {S['P_MINUS']:.4f}` -> **MIXED**, stable across every
co-optimal representative. The second mode is not purely common. That sentence is qualified, not
deleted.

FSCMA00 also reported the environmental response as 97-99 % common mode. That figure was the raw
sum-share of the response and is correct as such. The quantity that governs the *relation to the
carrier family* is the sector split of the **off-carrier residual**, which is
`F_PLUS = {E['ENV_PROBE']['F_PLUS']:.4f}` on ENV_PROBE and {E['ENV_LOCKED']['F_PLUS']:.4f} on
ENV_LOCKED -- below the 0.95 needed for a common-only label. The invariant label is therefore
`OPERATOR_SPECIFIC_MIXED_EXTENSION`, which is a **smaller and more precise** claim than
"a second mode".
""")

Wt("QUOTIENT_GLOBAL_OPTIMUM_CERTIFICATE.json", json.dumps({
    "objective": "R_k = min over linked founder swaps, affine mean and orthonormal k-dim model of "
                 "sum_i alpha_i ||z_i - mu - B B^T (z_i - mu)||^2",
    "gauge_founder_pinned_to_plus_one": B["gauge_founder_pinned"],
    "n_assignments_enumerated": B["n_assignments"],
    "enumeration": "exhaustive over all 2^(F-1) = 32 linked assignments; no heuristic, no solver "
                   "selected after seeing the landscape",
    "arithmetic": "Gram entries exactly rational (<z_i,z_j> = <u_i,u_j> + e_i e_j <v_i,v_j>, and "
                  "sqrt(w)*sqrt(w) = w). Eigenvalues enclosed by exact Sylvester inertia, i.e. "
                  "exact LDL^T of G - tI, bisected 34 times.",
    "R0_exact_no_bisection_needed": B["R0"],
    "R1_certified_interval": B["R1"], "R2_certified_interval": B["R2"],
    "L1": B["L1"], "L2": B["L2"],
    "argmin_R0": B["R0_argmin_swapped"], "argmin_R1": B["R1_argmin_swapped"],
    "argmin_R2": B["R2_argmin_swapped"],
    "n_cooptimal": {"R0": B["n_cooptimal_R0"], "R1": B["n_cooptimal_R1"], "R2": B["n_cooptimal_R2"]},
    "unique_optimum_shared_across_k": (B["R0_argmin_swapped"] == B["R1_argmin_swapped"]
                                       == B["R2_argmin_swapped"] and B["n_cooptimal_R1"] == 1),
    "consequence": "one assignment is simultaneously optimal for k=0,1,2, so on this panel the R_k "
                   "are genuinely nested and L1, L2 equal the two leading eigenvalues of a single "
                   "fixed exactly-rational matrix. Proved, not assumed.",
    "VERDICT": "QUOTIENT_GLOBAL_OPTIMUM_CERTIFIED"}, indent=1))

Wt("LOSSY_COORDINATE_SENSITIVITY_REPORT.md", f"""# LOSSY_COORDINATE_SENSITIVITY_REPORT

Mandatory, and **never a vote**. Each coordinate below discards something the exact quotient keeps.
Where a coordinate disagrees with the quotient, the coordinate changed the question.

| coordinate | second/first | second share | one-family residual | what it loses |
|---|---|---|---|---|
| exact quotient (primary) | {B['QUOTIENT_INCREMENT_RATIO'][0]:.4f} | {B['QUOTIENT_SECOND_SHARE'][0]:.4f} | {B['ONE_FAMILY_AGGREGATE_RESIDUAL'][0]:.4f} | nothing |
| pointwise \\|v\\| | {R['G_lossy_sensitivity']['abs_v']['sigma2_over_sigma1']:.4f} | {R['G_lossy_sensitivity']['abs_v']['second_share']:.4f} | {R['G_lossy_sensitivity']['abs_v']['one_family_residual']:.4f} | relative signs between scored times |
| elementary symmetric pair | {R['G_lossy_sensitivity']['elem_sym']['sigma2_over_sigma1']:.4f} | {R['G_lossy_sensitivity']['elem_sym']['second_share']:.4f} | {R['G_lossy_sensitivity']['elem_sym']['one_family_residual']:.4f} | relative signs; also mixes units |
| per-row v OUTER v | {R['G_lossy_sensitivity']['per_row_vvT']['sigma2_over_sigma1']:.4f} | {R['G_lossy_sensitivity']['per_row_vvT']['second_share']:.4f} | {R['G_lossy_sensitivity']['per_row_vvT']['one_family_residual']:.4f} | cross-operator relative sign; inflates dimension via a quadratic embedding |

Reading. Every lossy coordinate agrees with the exact quotient on the qualitative conclusion --
one affine family is not enough -- and none of them agrees on the size of the second increment.
`|v|` understates it because discarding time-signs flattens the differential sector;
the elementary-symmetric pair overstates it because it mixes a linear and a quadratic quantity in
one SVD, exactly the inflation the freeze forbids for a primary claim; the per-row quadratic
embedding sits between the two for the same reason.

The primary conclusion is taken from the exact quotient and from nowhere else. No dataset was
split, no weight revised, no verdict averaged.
""")

Wt("OFFLINE_GI_REANALYSIS.md", f"""# OFFLINE_GI_REANALYSIS — Phase 1

**Engine starts: 0.** Asserted equal before and after. No engine, substrate, state or checkpoint is
imported anywhere in the Phase-1 code path.

## 1. The gauge, and an oracle that can fail

The physical ambiguity is exactly one A/B exchange per founder, shared across every scored time and
every arm of that founder. Verified from the reader, the mask lifecycle and the operator code.

All required operators are exchange-equivariant: the matched transposition is symmetric in its two
argument lists, and both the intensive reflection and the environmental perturbation never read the
masks at all.

Oracle, with all `2^12 = 4096` artificial assignments enumerated and every invariant recomputed
from genuinely exchanged `delta_A`/`delta_B` bytes:

| test | result |
|---|---|
{chr(10).join('| `%s` | %s |' % (k, v) for k, v in OR['tests'].items() if isinstance(v, bool))}

and four negative controls, all of which fire, proving the suite is not vacuous:

{chr(10).join('* `%s` = %s' % (k, v) for k, v in OR['negative_controls'].items())}

**VERDICT: {OR['VERDICT']}**

## 2. Absolute materiality — the load-bearing negative

The inherited threshold bounds a weighted **L1** functional; the quotient lives in weighted **L2**.
The exact worst-case propagation is `||z|| <= A_bu / sqrt(min_h w_h) = sqrt(18) * A_bu`, attained
when the whole response sits on one endpoint of the scored grid, so no smaller constant is valid.

Applied to the parents' own cells it reverses **{len(rev)} of {M['n_parent_material']}**:
every CARRIER_1 matched-transposition cell, in both roles, with `||z||/eta_z` in
[{min(c['z_over_eta_z'] for c in rev):.3f}, {max(c['z_over_eta_z'] for c in rev):.3f}].
Surviving cells run from {min(c['z_over_eta_z'] for c in M['cells'] if c['L2_bound_calls_it_material']):.3f}
to {max(c['z_over_eta_z'] for c in M['cells'] if c['L2_bound_calls_it_material']):.3f}.

By the criterion frozen before any array was read: **`ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`**.
Relative structure only, no material claim, `PHASE2_LICENSE = NO`.

## 3. The certified quotient optimum

Exhaustive over all 32 linked assignments, exact rational Gram, Sylvester-inertia eigenvalue
enclosures.

| quantity | certified |
|---|---|
| `R0` (exact) | {B['R0'][0]:.6e} |
| `R1` | [{B['R1'][0]:.6e}, {B['R1'][1]:.6e}] |
| `R2` | [{B['R2'][0]:.6e}, {B['R2'][1]:.6e}] |
| `L1` | {B['L1'][0]:.6e} |
| `L2` | {B['L2'][0]:.6e} |
| `QUOTIENT_INCREMENT_RATIO = sqrt(L2/L1)` | [{B['QUOTIENT_INCREMENT_RATIO'][0]:.4f}, {B['QUOTIENT_INCREMENT_RATIO'][1]:.4f}] |
| `QUOTIENT_SECOND_SHARE = L2/R0` | [{B['QUOTIENT_SECOND_SHARE'][0]:.4f}, {B['QUOTIENT_SECOND_SHARE'][1]:.4f}] |

The argmin is **unique** and is the same assignment for k = 0, 1, 2: swap
`{B['R0_argmin_swapped'][0]}`. One co-optimum only, so no co-optimal disagreement can arise.

    QDIM2 (ratio > 0.10)      : {B['QDIM2_ratio_gt_0.10']}
    QDIM3 (share >= 0.05)     : {B['QDIM3_energy_ge_0.05']}
    QDIM0 / QDIM1 (absolute)  : NOT_AVAILABLE

Direct reconstruction gates on CARRIER_BASIS:

    one affine family : aggregate {B['ONE_FAMILY_AGGREGATE_RESIDUAL'][0]:.4f} (needs < 0.05), worst cell {C['k1']['cell_max']:.4f} (needs < 0.10)  -> FAIL
    two dimensions    : aggregate {B['K2_AGGREGATE_RESIDUAL'][0]:.4f} (needs < 0.05), worst cell {C['k2']['cell_max']:.4f} (needs < 0.10)  -> PASS

So `CARRIER_MODEL_DIMENSION_USED_FOR_ENV_TEST = {C['CARRIER_MODEL_DIMENSION_USED_FOR_ENV_TEST']}`.

## 4. Sector of the second degree

Nested extension of the frozen one-dimensional model, under the same alignment:
`P_PLUS = {S['P_PLUS']:.4f}`, `P_MINUS = {S['P_MINUS']:.4f}` -> **{S['SECOND_DEGREE_SECTOR']}**,
identical across every co-optimal representative ({S['labels_over_cooptima']}). The nested extra
energy has no compatible absolute bound, so it is a shape statement, not a material one.

## 5. Transfer to CARRIER_LOCKED, no refit

| k | aggregate residual | worst cell | gate |
|---|---|---|---|
| 1 | {D['1']['LOCKED_AGG_RESIDUAL']:.4f} | {D['1']['cell_max']:.4f} | {D['1']['GATE']} |
| 2 | {D['2']['LOCKED_AGG_RESIDUAL']:.4f} | {D['2']['cell_max']:.4f} | {D['2']['GATE']} |

`CARRIER_QUOTIENT_TRANSFER_STATUS = {D['CARRIER_QUOTIENT_TRANSFER_STATUS']}`. The BASIS gate status
at the frozen dimension reproduces on twelve cells that were never used to fit anything.

## 6. The environmental relation

Scored against the frozen two-dimensional carrier family; the carrier family was never refitted to
environmental rows.

| panel | off-family aggregate | worst-of-min cell | cells >= 0.05 | F_PLUS | F_MINUS | max single-founder share |
|---|---|---|---|---|---|---|
| ENV_PROBE | {E['ENV_PROBE']['OFF_MODEL_FRAC_AGG']:.4f} | {E['ENV_PROBE']['min_cell']:.4f} | {E['ENV_PROBE']['cells_ge_0.05']}/6 | {E['ENV_PROBE']['F_PLUS']:.4f} | {E['ENV_PROBE']['F_MINUS']:.4f} | {E['ENV_PROBE']['max_single_founder_share']:.4f} |
| ENV_LOCKED | {E['ENV_LOCKED']['OFF_MODEL_FRAC_AGG']:.4f} | {E['ENV_LOCKED']['min_cell']:.4f} | {E['ENV_LOCKED']['cells_ge_0.05']}/6 | {E['ENV_LOCKED']['F_PLUS']:.4f} | {E['ENV_LOCKED']['F_MINUS']:.4f} | {E['ENV_LOCKED']['max_single_founder_share']:.4f} |
| +0.25 dose (diagnostic) | {E['ENV_DOSE_SECONDARY']['OFF_MODEL_FRAC_AGG']:.4f} | {E['ENV_DOSE_SECONDARY']['min_cell']:.4f} | {E['ENV_DOSE_SECONDARY']['cells_ge_0.05']}/6 | {E['ENV_DOSE_SECONDARY']['F_PLUS']:.4f} | {E['ENV_DOSE_SECONDARY']['F_MINUS']:.4f} | {E['ENV_DOSE_SECONDARY']['max_single_founder_share']:.4f} |

LOAO carrier tube radius {E['LOAO_TUBE_RADIUS']:.4f}; the smallest environmental cell is
{min(E['ENV_PROBE']['min_cell'], E['ENV_LOCKED']['min_cell']):.4f}, above it by more than a factor of ten.
Direction stability modulo the linked swap: probe vs locked
{E['stability_cos_probe_vs_locked']:.6f}; +0.50 vs +0.25 {E['stability_cos_dose']:.6f}.

`ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS = {E['ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS']}`.

Both `F_PLUS` values sit at ~0.885-0.890, below the 0.95 a common-only label requires, and both
`F_MINUS` values exceed 0.05. The environmental extension is **mixed**, not common-only. Since the
carrier quotient is already at least two-dimensional, the environment is an off-carrier extension
and never "the second mode".

## 7. The parent-aliased founder stratum

Named `PARENT_ALIASED_FOUNDER_STRATUM` throughout; no member name (geometry, history, parity) is
adopted as the cause.

    support BASIS  : 3 + 3   ({F['support_3_plus_3_BASIS']})
    support LOCKED : 3 + 3   ({F['support_3_plus_3_LOCKED']})
    R_STRATUM_0    = {F['R_STRATUM_0']:.6e}
    R_STRATUM_2MEAN= {F['R_STRATUM_2MEAN']:.6e}
    E_STRATUM      = {F['E_STRATUM']:.6e}
    STRATUM_SHARE  = {F['STRATUM_SHARE']:.4f}    (relative gate >= 0.05: {F['relative_share_ge_0.05']})
    nested sector  : P+ = {F['P_STRATUM_PLUS']:.4f}, P- = {F['P_STRATUM_MINUS']:.4f} -> {F['sector']}
    LOAO shares    : all >= 0.05 = {sup['stratum_LOAO_all_shares_ge_0.05']}, min alignment {sup['stratum_LOAO_min_direction_alignment']:.4f}
    max single cluster share = {sup['stratum_MAX_SINGLE_CLUSTER_SHARE']:.4f} (needs <= 1/3: {sup['stratum_max_share_le_one_third']})
    LOCKED transfer share    = {sup['LOCKED_TRANSFER_SHARE']:.4f}, axis alignment {sup['LOCKED_stratum_alignment_to_frozen_axis']:.4f}
    ABSOLUTE_MATERIALITY     = {F['ABSOLUTE_MATERIALITY']}

Every relative and support sub-gate the stratum object had to clear, it clears. The one it cannot
clear is absolute materiality, because no compatible bound exists in this panel's units. The
conjunctive rule therefore gives

**`FOUNDER_STRATUM_QUOTIENT_STATUS = {F['FOUNDER_STRATUM_QUOTIENT_STATUS']}` and `PHASE2_LICENSE = NO`.**

This is the honest reading: the stratum object is *there* in the relative geometry, reproducibly and
with balanced support, and it *cannot be called material* on the evidence available. Those are two
different statements and only the first is licensed.
""")

json.dump({"PHASE2_LICENSE": H["PHASE2_LICENSE"],
           "required_conditions": {
               "FOUNDER_STRATUM_QUOTIENT_STATUS": F["FOUNDER_STRATUM_QUOTIENT_STATUS"],
               "compatible_original_space_absolute_materiality": M["ABSOLUTE_MATERIALITY_STATUS"],
               "support_3_plus_3_in_both_parent_panels":
                   bool(F["support_3_plus_3_BASIS"] and F["support_3_plus_3_LOCKED"]),
               "unique_stable_sector_specific_psi_stratum":
                   {"sector": F["sector"], "LOAO_min_alignment":
                    sup["stratum_LOAO_min_direction_alignment"],
                    "note": "a MIXED stratum requires both sector objects to pass separately; the "
                            "differential half has no dimensionally valid absolute bound"}},
           "blocking_condition": "ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE",
           "engine_starts_authorised_by_this_record": 0,
           "phase2_sections_not_reached": [
               "4 history route H1/H2/H3/H4", "5 geometry route G1/G2",
               "6 fresh namespace, queue and start budget", "7 phase-2 lock and sealing",
               "8 fresh oracle and one-shot execution", "9 fresh invariant estimands"],
           "vocabulary": {"HISTORY_FACTOR_STATUS": "NOT_REACHED",
                          "GEOMETRY_DESIGN_STATUS": "NOT_REACHED",
                          "FRESH_PANEL_STATUS": "NOT_REACHED",
                          "FACTORIAL_ATTRIBUTION_STATUS": "NOT_REACHED"}},
          open(f"{OUT}/PHASE2_LICENSE_RECORD.json", "w"), indent=1)

Wt("PROTOCOL_DEVIATIONS.md", f"""# PROTOCOL_DEVIATIONS

## D1 — vacuous oracle written and then repaired (self-defect, mine)

The first pass of the gauge oracle contained three predicates of the form
`if ip(v_i,v_j) != e*e*ip(v_i,v_j)` and `if bip([p],[p]) != bip([p],[p])`. Each compares an
expression to itself and passes on arbitrary input. This is precisely the defect this programme
line condemned in ETCMNFC and again in EEFCA, and I reproduced it.

Repair: `gimb_oracle_v2.py` supersedes that block. Every test now applies a real exchange of the
two scored regions to the underlying `delta_A`/`delta_B` bytes, recomputes each invariant from the
exchanged data, and is accompanied by a negative control that fires. Both source states are kept.

## D2 — wrong object in the Q0E reconstruction test, corrected before use

My first Q0E tested rank-one-ness of the **arm Gram** `P[i][j] = <v_i,v_j>`, which is a contraction
of the block outer product and has rank `min(n_arms, T)`, not 1. It returned false, correctly, for
the wrong reason. The handoff's object is the outer product of the **concatenated** block vector,
which is rank one by construction. Corrected and re-run on every founder; the exact rank-one
identity `M[k][r]M[r][l] = M[k][l]M[r][r]` now holds for all founders, the global sign flip leaves
the object identical, and flipping a single arm changes it.

## D3 — a whole-block distance is undefined across roles

BASIS founders carry four arms (two carriers, +0.50, +0.25); LOCKED founders carry three. A
whole-block quotient distance between founders with different arm signatures is not defined. Pairs
are formed within a role only. Recorded because a naive implementation would have silently
truncated to the shorter block.

## D4 — stratum sub-gates computed after the disposition was already fixed

`FOUNDER_STRATUM_QUOTIENT_STATUS` was forced to `NUMERICALLY_UNRESOLVED` by the
absolute-materiality gate. The leave-one-ancestry-out suite, the maximum-single-cluster share and
the LOCKED transfer of the frozen axis were computed anyway and are reported, because a reader is
entitled to know that every *other* sub-gate passes. They cannot and do not change the
disposition: the gates are conjunctive.

## D5 — the three named raw sources were not sufficient

The handoff named `FSCMA00_LOCKED_RAW_CELL_SCORES.json`, `fscma_probe_raw.json` and
`wsfscrp_q01.json`. The time-resolved LOCKED **carrier** curves are in none of them; they live in
`FSCMA00/fscma_locked_carrier.json`, in the same committed tree. Located by committed provenance
and bound by blob object id, as instructed. No engine was run to reconstruct anything.

## No other deviations

Engine starts: 0, asserted equal before and after Phase 1. No push, no PR, no workflow trigger.
Tommy's checkout was not moved, checked out, merged or modified. No parent output was overwritten.
""")

print("deliverables written")

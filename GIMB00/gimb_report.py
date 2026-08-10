"""GIMB00 -- final report, claim ledger, disposition, NOT_REACHED manifest, SHA256SUMS."""
from __future__ import annotations
import json, hashlib, os

OUT = "/home/claude/sweep/GIMB00"
R = json.load(open(f"{OUT}/OFFLINE_GI_SCORES_AND_CERTIFIED_INTERVALS.json"))
OR = json.load(open(f"{OUT}/GAUGE_ORACLE_TESTS.json"))
B, C, S, D, E, F, H = (R["B_quotient"], R["C_basis_family"], R["C_sector"],
                       R["D_carrier_transfer"], R["E_environment"], R["F_stratum"],
                       R["H_disposition"])
M, sup = R["A_absolute_materiality"], R["F_stratum_supplementary"]
rev = [c for c in M["cells"] if c["parent_called_it_material"] and not c["L2_bound_calls_it_material"]]
Wt = lambda n, s: open(f"{OUT}/{n}", "w").write(s)

FIELDS = {
    "OFFLINE_INVARIANT_STATUS": H["OFFLINE_INVARIANT_STATUS"],
    "CARRIER_QUOTIENT_STRUCTURE": H["CARRIER_QUOTIENT_STRUCTURE"],
    "CARRIER_QUOTIENT_TRANSFER_STATUS": H["CARRIER_QUOTIENT_TRANSFER_STATUS"],
    "ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS": H["ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS"],
    "FOUNDER_STRATUM_QUOTIENT_STATUS": H["FOUNDER_STRATUM_QUOTIENT_STATUS"],
    "PHASE2_LICENSE": H["PHASE2_LICENSE"],
    "HISTORY_FACTOR_STATUS": "NOT_REACHED",
    "GEOMETRY_DESIGN_STATUS": "NOT_REACHED",
    "FRESH_PANEL_STATUS": "NOT_REACHED",
    "FRESH_CARRIER_QUOTIENT_STRUCTURE": "NOT_REACHED",
    "FRESH_STRATUM_TRANSFER": "NOT_REACHED",
    "FACTORIAL_ATTRIBUTION_STATUS": "NOT_REACHED",
    "DELIVERY_STATUS": "COMPLETE",
}
DISP = "OFFLINE_GI_REDERIVATION_COMPLETE__NO_FRESH_PANEL_LICENSE"

json.dump({"GIMB00_DISPOSITION": DISP, "mandatory_fields": FIELDS,
           "precedence_applied": "items 1-9 of the global precedence list are all clear: "
                                 "provenance bound, raw time-resolved endpoint available, weights "
                                 "and normalizer resolved, master freeze intact, all required "
                                 "operators exchange-equivariant, swap action validated, complete "
                                 "invariant oracle passed with negative controls, quotient optimum "
                                 "certified, quotient dimension resolved. Item 10 applies.",
           "engine_starts": {"phase1": 0, "phase2": 0, "total_new": 0, "cap": 96},
           "key_numbers": {
               "quotient_increment_ratio": B["QUOTIENT_INCREMENT_RATIO"],
               "quotient_second_share": B["QUOTIENT_SECOND_SHARE"],
               "one_family_aggregate_residual": B["ONE_FAMILY_AGGREGATE_RESIDUAL"],
               "k2_aggregate_residual": B["K2_AGGREGATE_RESIDUAL"],
               "k2_locked_transfer_aggregate": D["2"]["LOCKED_AGG_RESIDUAL"],
               "env_off_carrier_probe": E["ENV_PROBE"]["OFF_MODEL_FRAC_AGG"],
               "env_off_carrier_locked": E["ENV_LOCKED"]["OFF_MODEL_FRAC_AGG"],
               "env_F_PLUS_probe": E["ENV_PROBE"]["F_PLUS"],
               "env_F_PLUS_locked": E["ENV_LOCKED"]["F_PLUS"],
               "env_direction_stability": E["stability_cos_probe_vs_locked"],
               "stratum_share": F["STRATUM_SHARE"],
               "materiality_cells_reversed": len(rev),
               "materiality_cells_parent_material": M["n_parent_material"]},
           "claim_ceiling": ["RESPONSE_INFORMED_EXPLORATORY_DEV", "ONE_LAWSPEC",
                             "ONE_CHECKPOINT_AND_HORIZON",
                             "FIXED_SUPPORT_EULERIAN_OR_FIXED_GRID_REGION_RESPONSE",
                             "SINGLE_EXECUTOR_INTERNAL_ORACLE", "NOT_INDEPENDENT_REVIEW",
                             "NOT_CONFIRMATORY", "NOT_POPULATION_INFERENCE"]},
          open(f"{OUT}/GIMB00_FINAL_DISPOSITION.json", "w"), indent=1)

json.dump({d: "NOT_REACHED" for d in [
    "CROSSED_FACTOR_ORBIT_IDENTIFIABILITY_AUDIT.md",
    "PREHISTORY_ANCHOR_OR_COMPLEMENTARY_ORBIT_AUDIT.md", "FRESH_QUEUE_AND_ANCESTRY_GRAPH.json",
    "FROZEN_START_BUDGET_MATRIX.json", "ENGINE_START_LEDGER.json",
    "CONTAMINATION_AND_ACCESS_LEDGER.json", "GIMB00_PHASE2_LOCK.json",
    "SEALED_PANEL_AND_ANALYSIS_LOCK.json", "FRESH_ORACLE_REPORT.md",
    "FRESH_RAW_RESPONSE_ARCHIVE", "FRESH_RAW_RESPONSE_MANIFEST.json",
    "FRESH_QUOTIENT_AND_FACTORIAL_RESULTS.md", "FRESH_MACHINE_READABLE_SCORES.json"]},
    open(f"{OUT}/PHASE2_DELIVERABLES_NOT_REACHED.json", "w"), indent=1)

Wt("PARENT_AND_GIMB00_CLAIM_LEDGER.md", f"""# PARENT_AND_GIMB00_CLAIM_LEDGER (append-only)

Parent dispositions are preserved verbatim. Nothing below rewrites them.

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    FSCMA00_H2_STATUS_IN_GIMB00     = REPORTED_PARENT_LABEL_REQUIRING_GAUGE_INVARIANT_QUALIFICATION
    GIMB00_PHASE1_DATA_STATUS       = POST_HOC_GAUGE_CORRECTIVE_REANALYSIS_OF_EXPOSED_DEV_ROWS

| # | claim | status | evidence |
|---|---|---|---|
| G1 | Ancestry `e912a10 -> f81daf9 -> f9e1e39` is a chain of direct parents. | ESTABLISHED | device repository, short hashes resolved, not trusted |
| G2 | Every analysed raw file is bound to the commit by a git blob object id recomputed from local bytes. | ESTABLISHED | 6 of 6 match; 49/49 and 35/35 manifest entries re-verified |
| G3 | The physical gauge is exactly one A/B exchange per founder, shared across all times and arms. | ESTABLISHED | reader, mask lifecycle and operator code; all required operators exchange-equivariant |
| G4 | The invariant oracle is not vacuous. | ESTABLISHED | 4096 real exchanges; 4 negative controls all fire |
| G5 | The certified global quotient optimum is unique and identical for k = 0, 1, 2: swap {B['R0_argmin_swapped'][0]}. | ESTABLISHED (exact) | exhaustive over 32 assignments, exact rational Gram, Sylvester inertia |
| G6 | On this panel `L1` and `L2` really are the two leading eigenvalues of one fixed matrix. | ESTABLISHED | a single assignment is simultaneously optimal at every k, so the `R_k` are genuinely nested here |
| G7 | One affine family is NOT enough for the carrier repertoire in the quotient. | ESTABLISHED (relative) | `R1/R0 = {B['ONE_FAMILY_AGGREGATE_RESIDUAL'][0]:.4f}` vs 0.05; worst cell {C['k1']['cell_max']:.4f} vs 0.10 |
| G8 | Two dimensions suffice, on both the aggregate and every cell. | ESTABLISHED (relative) | `R2/R0 = {B['K2_AGGREGATE_RESIDUAL'][0]:.4f}`, worst cell {C['k2']['cell_max']:.4f} |
| G9 | That two-dimensional structure transfers to CARRIER_LOCKED with no refit. | ESTABLISHED (relative) | aggregate {D['2']['LOCKED_AGG_RESIDUAL']:.4f}, worst cell {D['2']['cell_max']:.4f} |
| G10 | `QUOTIENT_INCREMENT_RATIO = {B['QUOTIENT_INCREMENT_RATIO'][0]:.4f}`, `QUOTIENT_SECOND_SHARE = {B['QUOTIENT_SECOND_SHARE'][0]:.4f}`. | ESTABLISHED (certified intervals) | QDIM2 and QDIM3 both pass |
| G11 | The second quotient degree is MIXED, not a pure common-mode founder offset. | ESTABLISHED (shape only) | nested extension `P+ = {S['P_PLUS']:.4f}`, `P- = {S['P_MINUS']:.4f}`, identical on every co-optimum |
| G12 | The environmental operator sits outside the carrier quotient family, on both exposed panels. | ESTABLISHED (relative) | off-family {E['ENV_PROBE']['OFF_MODEL_FRAC_AGG']:.4f} / {E['ENV_LOCKED']['OFF_MODEL_FRAC_AGG']:.4f}; smallest cell {min(E['ENV_PROBE']['min_cell'], E['ENV_LOCKED']['min_cell']):.4f} against a LOAO tube radius of {E['LOAO_TUBE_RADIUS']:.4f} |
| G13 | That extension is MIXED, not common-only. | ESTABLISHED | `F_PLUS = {E['ENV_PROBE']['F_PLUS']:.4f}` / {E['ENV_LOCKED']['F_PLUS']:.4f}, below the 0.95 a common-only label needs; `F_MINUS` above 0.05 on both |
| G14 | The environmental direction is stable across roles and across dose. | ESTABLISHED | {E['stability_cos_probe_vs_locked']:.6f} probe vs locked; {E['stability_cos_dose']:.6f} across +0.50 / +0.25 |
| G15 | The parent-aliased founder stratum survives in the relative quotient geometry with balanced support. | ESTABLISHED (relative only) | share {F['STRATUM_SHARE']:.4f}; 3+3 in both panels; LOAO min alignment {sup['stratum_LOAO_min_direction_alignment']:.4f}; max cluster share {sup['stratum_MAX_SINGLE_CLUSTER_SHARE']:.4f}; LOCKED transfer share {sup['LOCKED_TRANSFER_SHARE']:.4f} |
| G16 | No absolute materiality claim can be made anywhere in this programme. | ESTABLISHED, LIMITING | the only rigorous L1 -> L2 constant `sqrt(18)` reverses {len(rev)} of {M['n_parent_material']} parent-accepted cells; per the frozen criterion the bound is not compatible |
| G17 | Therefore the founder stratum is NOT licensed as material, and no fresh panel is licensed. | ESTABLISHED | `PHASE2_LICENSE = NO`, 0 engine starts |
| G18 | FSCMA00's `H2_SECOND_MODE_CONFIRMED_HELD_OUT` is qualified, not overturned. | APPENDED | the separation is real and invariant; its label becomes an off-carrier MIXED extension of an already two-dimensional carrier family, which is a smaller claim |

## Explicitly NOT claimed

* Not claimed: that the parents were wrong. Their arithmetic was certified exactly in FSCMA00 and
  their orientation is now certified as the exhaustive global optimum of a proper objective.
* Not claimed: that the physical response has rank two. `AT_LEAST_TWO` is an operational gate on
  one panel, not an intrinsic rank.
* Not claimed: any material magnitude, anywhere, in any sector.
* Not claimed: geometry, history order, memory, identity, agency, life, curvature, multiscale
  structure, or any population statement.
* Not claimed: that the second carrier degree or the stratum is caused by geometry. Its name in
  this programme is and stays `PARENT_ALIASED_FOUNDER_STRATUM`.

## Self-defects declared in this programme

See `PROTOCOL_DEVIATIONS.md`. In short: I wrote a vacuous oracle and repaired it with negative
controls; I tested the wrong object in Q0E and corrected it; the three named raw sources were
insufficient and the fourth was located by committed provenance.
""")

Wt("GIMB00_FINAL_REPORT.md", f"""# GIMB00_FINAL_REPORT

    GIMB00_DISPOSITION = {DISP}

{chr(10).join('    %-48s = %s' % (k, v) for k, v in FIELDS.items())}

    ENGINE_STARTS_PHASE1 = 0   ENGINE_STARTS_PHASE2 = 0   TOTAL_NEW = 0 of 96

## What the programme was asked to settle

Replace the A/B-labelled cross-founder analysis by the exact quotient under A/B exchange; find out
which reported structures survive; and, only if the aliased founder stratum survives as a material
object, build one fresh panel that breaks the geometry/history/parity alias.

## What survived the quotient

The carrier structure survived, and in a stronger form than the parents could state. The certified
global optimum over all 32 linked swap assignments is **unique** and is the same assignment for
k = 0, 1, 2, which means the FSCMA00 orientation was not a lucky heuristic and also means that on
this panel the model-complexity gains `L1` and `L2` genuinely are the two leading eigenvalues of a
single fixed matrix. One affine family fails its gate
(`{B['ONE_FAMILY_AGGREGATE_RESIDUAL'][0]:.4f}` against 0.05); two dimensions pass on the aggregate
and on every cell (`{B['K2_AGGREGATE_RESIDUAL'][0]:.4f}`, worst cell {C['k2']['cell_max']:.4f}); and
that two-dimensional family reproduces on the twelve CARRIER_LOCKED cells with **no refit**
(aggregate {D['2']['LOCKED_AGG_RESIDUAL']:.4f}, worst cell {D['2']['cell_max']:.4f}).

The second degree is **{S['SECOND_DEGREE_SECTOR']}** (`P+ = {S['P_PLUS']:.4f}`,
`P- = {S['P_MINUS']:.4f}`), which corrects the FSCMA00 sentence calling it a founder main effect.

The environmental separation survived too, and got smaller and sharper. Off the carrier family by
{E['ENV_PROBE']['OFF_MODEL_FRAC_AGG']:.4f} on ENV_PROBE and {E['ENV_LOCKED']['OFF_MODEL_FRAC_AGG']:.4f}
on ENV_LOCKED, with the smallest cell {min(E['ENV_PROBE']['min_cell'], E['ENV_LOCKED']['min_cell']):.4f}
against a leave-one-ancestry-out carrier tube radius of {E['LOAO_TUBE_RADIUS']:.4f}, direction
stability {E['stability_cos_probe_vs_locked']:.6f} across roles and {E['stability_cos_dose']:.6f}
across dose. But `F_PLUS` is {E['ENV_PROBE']['F_PLUS']:.4f} / {E['ENV_LOCKED']['F_PLUS']:.4f}, below
the 0.95 that a common-only label requires, so the invariant label is
**{E['ENVIRONMENTAL_QUOTIENT_RELATION_ON_EXPOSED_ROWS']}**. And because the carrier quotient is
already at least two-dimensional, the environment is never "the second mode" — it is an off-carrier
extension.

## What did not survive, and why it is the whole story

Nothing in this programme may be called **material**.

The inherited threshold bounds a weighted L1 statistic. The quotient is weighted L2. The only
rigorous propagation is `||z|| <= A_bu / sqrt(min_h w_h) = sqrt(18) * A_bu`, and it is attained, so
no smaller constant is valid. Applied to the parents' own cells it reverses **{len(rev)} of
{M['n_parent_material']}** — exactly the twelve CARRIER_1 matched-transposition cells, whose
`||z||/eta_z` lands between {min(c['z_over_eta_z'] for c in rev):.3f} and
{max(c['z_over_eta_z'] for c in rev):.3f}. A bound that retrospectively unmakes the parents' own
accepted responses is not a compatible restatement of their threshold, and the frozen rule forbids
improvising a tighter one.

So `ABSOLUTE_MATERIALITY_STATUS = NOT_AVAILABLE`, and every structure above is **relative
geometry only**.

## The founder stratum

Every relative and support sub-gate it had to clear, it clears: share {F['STRATUM_SHARE']:.4f},
3+3 support in both parent panels, leave-one-ancestry-out minimum direction alignment
{sup['stratum_LOAO_min_direction_alignment']:.4f}, maximum single-cluster share
{sup['stratum_MAX_SINGLE_CLUSTER_SHARE']:.4f}, and it transfers to CARRIER_LOCKED with share
{sup['LOCKED_TRANSFER_SHARE']:.4f} at axis alignment
{sup['LOCKED_stratum_alignment_to_frozen_axis']:.4f}. The one gate it cannot clear is absolute
materiality, for the reason above.

`FOUNDER_STRATUM_QUOTIENT_STATUS = {F['FOUNDER_STRATUM_QUOTIENT_STATUS']}` and therefore
`PHASE2_LICENSE = NO`. The fresh crossed panel is not built and no engine start is spent. The
stratum object is *there* in the relative geometry, reproducibly; it *cannot be called material* on
the evidence available. Those are different statements and only the first is licensed.

## Independent-unit count

Phase 1 used 6 BASIS ancestry clusters and 6 LOCKED ancestry clusters. Twelve carrier rows per role
are 6 clusters x 2 sentinels, not 12 replications. Timepoints and channels are not replications.

## Recommendation, not a programme

The blocking object is a units mismatch, not a physics question. Before any fresh panel is worth
96 starts, someone should define a materiality threshold **in the same norm as the estimand** —
that is, a weighted-L2 sham-referenced bound computed at the time the shams are run — so that
absolute claims become possible at all. That costs sham arms in a future programme, not analysis.
All new science remains suspended pending separate explicit owner authorization.

## Claim ceiling

RESPONSE_INFORMED_EXPLORATORY_DEV, ONE_LAWSPEC, ONE_CHECKPOINT_AND_HORIZON,
FIXED_SUPPORT_EULERIAN_OR_FIXED_GRID_REGION_RESPONSE, SINGLE_EXECUTOR_INTERNAL_ORACLE,
NOT_INDEPENDENT_REVIEW, NOT_CONFIRMATORY, NOT_POPULATION_INFERENCE. No life, agency, identity,
memory, provenance, bath, curvature or multiscale claim is made anywhere.
""")

# ---------------------------------------------------------------- SHA256SUMS
os.chdir(OUT)
if os.path.exists("SHA256SUMS"):
    os.remove("SHA256SUMS")
files = sorted(f for f in os.listdir(".") if os.path.isfile(f))
with open("SHA256SUMS", "w") as fh:
    for f in files:
        fh.write("%s  %s\n" % (hashlib.sha256(open(f, "rb").read()).hexdigest(), f))
print("files:", len(files))
bad = 0
for line in open("SHA256SUMS"):
    h, f = line.rstrip("\n").split("  ", 1)
    if hashlib.sha256(open(f, "rb").read()).hexdigest() != h:
        bad += 1
print("SHA256SUMS entries:", len(files), "failures:", bad)
print("DISPOSITION:", DISP)

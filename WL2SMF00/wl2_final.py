"""WL2SMF00 -- corrected dependency audit, propagation certificate, deliverables. ZERO STARTS."""
from __future__ import annotations
import ast, json, hashlib, math, os, collections
from fractions import Fraction as Fr

OUT = "/home/claude/sweep/WL2SMF00"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
TH = json.load(open(f"{OUT}/WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json"))
LOCK = json.load(open(f"{OUT}/WL2SMF00_PANEL_LOCK.json"))
AUD = json.load(open(f"{OUT}/STATIC_HISTORY_GEOMETRY_ROUTE_AUDIT.json"))
ORC = json.load(open(f"{OUT}/NONVACUOUS_ORACLE_AND_MUTATION_REPORT.json"))
PROV = json.load(open(f"{OUT}/WL2SMF00_MASTER_FREEZE_HASHES.json"))["provenance"]
ROWS = TH["descendant_thresholds"]
AGG = TH["aggregate"]
Wt = lambda n, s: open(f"{OUT}/{n}", "w").write(s)

# =====================================================================================
# CORRECTED DEPENDENCY AUDIT -- by resolved AST symbols, not by substring matching
# =====================================================================================
ACTIVE = {"transpose", "state_cross", "_perturb_N", "reciprocal_cross", "reciprocal_cross_env",
          "erase_all", "erase_half", "core_erase", "manifest", "eligible_edges", "frozen_matching"}


def called_symbols(path):
    out = set()
    for nd in ast.walk(ast.parse(open(path).read())):
        if isinstance(nd, ast.Call):
            f = nd.func
            if isinstance(f, ast.Name):
                out.add(f.id)
            elif isinstance(f, ast.Attribute):
                out.add(f.attr)
        if isinstance(nd, ast.Import):
            out |= {a.name for a in nd.names}
        if isinstance(nd, ast.ImportFrom):
            out.add(nd.module or "")
    return out


def imports_of(path):
    out = set()
    for nd in ast.walk(ast.parse(open(path).read())):
        if isinstance(nd, ast.Import):
            out |= {a.name for a in nd.names}
        if isinstance(nd, ast.ImportFrom):
            out.add(nd.module or "")
    return out


files = {"wl2_prod.py": f"{OUT}/wl2_prod.py", "wl2_ref.py": f"{OUT}/wl2_ref.py",
         "wl2_sham.py": f"{OUT}/wl2_sham.py", "wl2_panel.py": f"{OUT}/wl2_panel.py"}
DEP = {}
for nm, p in files.items():
    calls = called_symbols(p)
    DEP[nm] = {"imports": sorted(imports_of(p)),
               "active_operator_symbols_actually_called": sorted(calls & ACTIVE)}
DEP["wl2_prod.py"]["imports_only_fractions"] = set(DEP["wl2_prod.py"]["imports"]) <= {"fractions", "__future__"}
DEP["wl2_ref.py"]["imports_production"] = "wl2_prod" in DEP["wl2_ref.py"]["imports"]
DEP["threshold_pipeline_can_reach_an_active_response"] = bool(
    DEP["wl2_prod.py"]["active_operator_symbols_actually_called"]
    or DEP["wl2_sham.py"]["active_operator_symbols_actually_called"])
DEP["note"] = ("wl2_panel.py legitimately names the two FUTURE carrier executables inside the "
               "FUTURE_ACTIVE_CARRIER_ARM_LOCK as strings, to prevent arm shopping. It never "
               "imports or calls them. `eligible_edges`/`frozen_matching` are matching helpers "
               "that would only be needed to BUILD a carrier operator; the audit below confirms "
               "they are never called anywhere in this programme.")
DEP["PASS"] = bool(DEP["wl2_prod.py"]["imports_only_fractions"]
                   and not DEP["wl2_ref.py"]["imports_production"]
                   and not DEP["threshold_pipeline_can_reach_an_active_response"])
DEP["correction"] = ("my first dependency audit searched the driver's own source for forbidden "
                     "SUBSTRINGS and therefore matched its own blacklist literal, returning a "
                     "false failure. Replaced by resolved-symbol AST analysis.")
TH["dependency_audit"] = DEP
TH["lock_validity"] = {
    "fresh_active_outcomes_generated": 0, "fresh_active_outcomes_opened": 0,
    "old_active_outcomes_loaded_by_threshold_pipeline": 0,
    "every_target_descendant_has_one_finite_positive_threshold":
        all(r["finite_positive"] for r in ROWS) and len(ROWS) == 16,
    "all_reference_and_mutation_oracles_pass": ORC["VERDICT"] == "NONVACUOUS_ORACLE_PASS",
    "construction_and_qualification_starts": TH["engine_starts"]["C_SETUP"] + TH["engine_starts"]["construction"],
    "sham_twin_starts": TH["engine_starts"]["sham"],
    "extra_after_panel_lock": 0, "total_starts": TH["engine_starts"]["total"],
    "within_all_subbudgets": bool(TH["engine_starts"]["C_SETUP"] + TH["engine_starts"]["construction"] <= 32
                                  and TH["engine_starts"]["sham"] == 32
                                  and TH["engine_starts"]["total"] <= 64),
    "dependency_audit_pass": DEP["PASS"]}
TH["SEALED"] = all([TH["lock_validity"]["every_target_descendant_has_one_finite_positive_threshold"],
                    TH["lock_validity"]["all_reference_and_mutation_oracles_pass"],
                    TH["lock_validity"]["within_all_subbudgets"], DEP["PASS"]])
json.dump(TH, open(f"{OUT}/WL2SMF00_NUMERICAL_THRESHOLD_LOCK.json", "w"), indent=1)
print("dependency audit corrected ->", DEP["PASS"], "| SEALED:", TH["SEALED"])

# =====================================================================================
# MODAL AND CONTRAST PROPAGATION CERTIFICATE -- proofs, not citations
# =====================================================================================
E_TAU = Fr(AGG["E_TAU_exact"])
PROP = {
 "setting": "rows i with frozen nonnegative alpha_i summing to 1, z_i in the weighted product "
            "Hilbert space H, TAU_i the per-row material scale, E_TAU = sum alpha_i TAU_i^2, "
            "A_TAU = sqrt(E_TAU). The NULL is: every row is individually immaterial, ||z_i|| <= TAU_i.",
 "lemma_1_swap_is_an_isometry": {
     "statement": "for any linked whole-descendant swap eps, ||z_i(eps)|| = ||z_i||",
     "proof": "the swap acts as u -> u, v -> -v inside each row; that is an orthogonal map on the "
              "weighted product space, hence norm preserving."},
 "lemma_2_centering_is_contractive": {
     "statement": "sum_i alpha_i ||z_i - mu||^2 <= sum_i alpha_i ||z_i - c||^2 for every c in H, "
                  "with mu the alpha-weighted mean",
     "proof": "expand: sum alpha_i ||z_i - c||^2 = sum alpha_i ||z_i - mu||^2 + ||mu - c||^2, "
              "since the cross term vanishes by definition of mu. Take c = 0."},
 "lemma_3_projection_is_contractive": {
     "statement": "for a fixed orthonormal k-dimensional B, ||d - B B^T d||^2 <= ||d||^2, hence "
                  "R_k(eps) <= R_{k-1}(eps) pointwise in eps and R_k <= R_{k-1} after minimising",
     "proof": "B B^T is an orthogonal projection; Pythagoras."},
 "theorem_total": {
     "statement": "under the null, R0 <= E_TAU",
     "proof": "R0 = min_eps sum_i alpha_i ||z_i(eps) - mu(eps)||^2 <= sum_i alpha_i ||z_i(eps)||^2 "
              "(Lemma 2 with c = 0) = sum_i alpha_i ||z_i||^2 (Lemma 1) <= sum_i alpha_i TAU_i^2 "
              "= E_TAU.",
     "consequence": "QDIM_TOTAL_SCATTER_MATERIAL (lower(R0) > upper(E_TAU)) implies at least one "
                    "row is material. The gate is therefore conservative in the right direction."},
 "theorem_modal": {
     "statement": "under the null, sqrt(L2) <= A_TAU",
     "proof": "L2 = R1 - R2 <= R1 (R2 >= 0) <= R0 (Lemma 3, pointwise then after minimisation) "
              "<= E_TAU (theorem_total). Take square roots.",
     "consequence": "QDIM_SECOND_INCREMENT_MATERIAL is valid, and it STRICTLY IMPLIES the total "
                    "gate, because L2 <= R0 always. The two gates are nested, not independent."},
 "conservatism_declared": {
     "statement": "because L2 <= R0, passing the modal gate requires L2 > E_TAU, i.e. the second "
                  "increment ALONE must exceed the whole immateriality budget. Combined with the "
                  "inherited relative gate L2/R0 >= 0.05, a passing panel needs R0 > 20 * E_TAU "
                  "in the worst case.",
     "numbers_for_this_sealed_panel": {
         "E_TAU": float(E_TAU), "A_TAU": AGG["A_TAU"],
         "R0_required_for_the_modal_gate_at_share_0.05": float(E_TAU) * 20,
         "R0_required_for_the_total_gate": float(E_TAU)},
     "why_it_is_not_weakened": "weakening the rule after seeing that it is demanding would be "
                               "response-adaptive. It is declared, not adjusted."},
 "theorem_contrast": {
     "statement": "for a normalised gauge-valid linear contrast X = sum_i c_i z_i, under the null "
                  "||X|| <= sum_i |c_i| TAU_i = TAU_CONTRAST(c)",
     "proof": "triangle inequality then the null bound on each ||z_i||.",
     "gauge_caveat": "a signed linear contrast of raw z = (u,v) is NOT automatically invariant, "
                     "because each descendant may send v -> -v. Under H3 the signed contrast is "
                     "NOT_DEFINED_UNDER_GAUGE and the primary object is the unordered quotient "
                     "distance between allocations."},
 "theorem_quotient_pair": {
     "statement": "D_Q([i],[j]) <= TAU_i + TAU_j under the null",
     "proof": "D_Q([i],[j]) = min_eps ||z_i - z_j(eps)|| <= ||z_i|| + ||z_j|| <= TAU_i + TAU_j."},
 "numerical_perturbation": {
     "statement": "|sqrt(R_k(Z_hat)) - sqrt(R_k(Z_true))| <= A_ETA_ORACLE",
     "proof": "sqrt(R_k) is the distance from the weighted row cloud to the frozen model class in "
              "the product norm; distance to a set is 1-Lipschitz, centering is contractive and "
              "each swap is an isometry, so the whole functional is 1-Lipschitz in the weighted "
              "perturbation norm, which is bounded by A_ETA_ORACLE.",
     "A_ETA_ORACLE_on_this_panel": 0.0,
     "what_is_NOT_asserted": "|sqrt(L2_hat) - sqrt(L2_true)| <= A_ETA_ORACLE. R1 and R2 are "
                             "separately optimised, so that does not follow. L2 intervals are "
                             "built by certified interval subtraction of the R_k intervals."},
 "quadratic_objects": {
     "v_outer_v_and_projectors": "shape and sector diagnostics only. Naming A_TAU does not create "
                                 "a materiality rule for a fourth-order object. Original "
                                 "quotient-space materiality is always required first.",
     "PROJECTIVE_EMBEDDING_BOUND": "NOT_AVAILABLE", "H3_K_BOUND": "NOT_AVAILABLE"},
 "boundary_and_degeneracy_rules": {
     "TOTAL": "PASS iff lower(R0) > upper(E_TAU); FAIL iff upper(R0) <= lower(E_TAU); else UNRESOLVED",
     "MODAL": "PASS iff lower(sqrt(L2)) > upper(A_TAU); FAIL iff upper(sqrt(L2)) <= lower(A_TAU); else UNRESOLVED",
     "RATIO": "PASS iff lower(sqrt(L2/L1)) > 0.10; FAIL iff upper <= 0.10; else UNRESOLVED",
     "SHARE": "PASS iff lower(L2/R0) >= 0.05; FAIL iff upper < 0.05; else UNRESOLVED",
     "zero_precedence": ["upper(L2)<=0 -> NO_SECOND_INCREMENT/MODAL_FAIL",
                         "L2 interval touches 0 with positive upper -> MODAL and RATIO UNRESOLVED",
                         "upper(L1)<=0 -> DEGENERATE_FIRST_INCREMENT",
                         "L1 interval touches 0 -> RATIO_UNRESOLVED",
                         "upper(R0)<=0 -> DEGENERATE_TOTAL_SCATTER",
                         "R0 interval touches 0 -> SHARE_UNRESOLVED",
                         "never divide by or take a square root of an interval touching zero"]},
 "MODAL_MATERIALITY_RULE": "QUALIFIED_FOR_FUTURE_EXACT_PANEL",
 "CELL_MATERIALITY_RULE": "QUALIFIED_FOR_FUTURE_EXACT_PANEL",
 "GAUGE_VALID_FACTOR_OBJECT_RULE": "QUALIFIED_FOR_SELECTED_ROUTE",
}
json.dump(PROP, open(f"{OUT}/MODAL_AND_CONTRAST_PROPAGATION_CERTIFICATE.json", "w"), indent=1)

# =====================================================================================
# sham raw manifest (what is and is not archived)
# =====================================================================================
ckd = f"{OUT}/checkpoints"
man = sorted(os.listdir(ckd))
json.dump({"archive_directory": "WL2SMF00/checkpoints",
           "files": [{"name": f, "sha256": sha(f"{ckd}/{f}"), "bytes": os.path.getsize(f"{ckd}/{f}")}
                     for f in man],
           "contents": "16 descendant t0 checkpoints (d_*.npz) and their 16 immutable mask pairs "
                       "(m_*.npz). Each checkpoint hash is bound in WL2SMF00_PANEL_LOCK.json.",
           "threshold_determining_scalars": "stored exactly, as rationals, in "
                                            "DESCENDANT_L2_THRESHOLD_COMPONENTS.json: B, RHO_MED, "
                                            "G2^2 and TAU_MATERIAL_L2^2 per descendant.",
           "NOT_archived": "the per-scored-time SHAM_0 reader series X_A[h], X_B[h].",
           "why_that_is_recoverable_without_new_evidence":
               "the sham is the identity operator on sealed checkpoint bytes and the engine is "
               "bit-deterministic. The twin oracle passed 16 of 16 over the full horizon and the "
               "terminal state hash, so the series is an exactly reproducible function of bytes "
               "already archived. Re-deriving it costs engine time, not evidence.",
           "declared_as": "PROTOCOL_DEVIATION D2"},
          open(f"{OUT}/FRESH_SHAM_RAW_MANIFEST.json", "w"), indent=1)
print("raw manifest:", len(man), "checkpoint files")

# =====================================================================================
# REPORTS
# =====================================================================================
byg = collections.defaultdict(list)
for r in ROWS:
    byg[(r["geometry"], r["alloc"])].append(r["TAU_MATERIAL_L2"])
Wt("ETA_ORACLE_L2_FORWARD_ERROR_CERTIFICATE.md", f"""# ETA_ORACLE_L2_FORWARD_ERROR_CERTIFICATE

## Claim

    eps_INT = eps_SHAM = eps_SUBTRACTION = eps_RELOAD = 0   exactly, for every channel and time
    ETA_ORACLE_L2[d] = 0                                    for every descendant

This bounds the **scoring path on serialized states**: reader, subtraction and reload. It is not a
stability bound on engine dynamics, and it is not claimed to be one.

## Proof, branch by branch

1. **Reload.** `numpy.savez` stores raw IEEE754 bytes and `numpy.load` returns them unchanged.
   Verified on an adversarial vector including a subnormal (`2^-1074`), `-0.0`, `1e16`, `1e-300`
   and values whose decimal forms do not round-trip: the byte images are identical.
2. **Reader.** `wsfscrp_core.dsum` accumulates `Fraction(float(v))`. Every IEEE754 double is
   *exactly* a dyadic rational, so the conversion is exact; `Fraction` addition is exact and
   therefore order-independent. `B_of` is the same construction, and `q_channels` divides two exact
   rationals. No rounding occurs.
3. **Subtraction.** `delta = X[INT] - X[SHAM_0]` is a difference of two exact rationals.
4. **Weights.** `w` is built in exact `Fraction` arithmetic from the frozen physical times, so
   `sum_h w_h (delta_A^2 + delta_B^2)` is exact.

## The test is not vacuous

An oracle that always says "exact" is worthless. Two controls fire:

* the production reader (forward order) and the independent reference reader (**reverse** order)
  agree exactly on the adversarial vector -- if the arithmetic were floating point they would not;
* a float64-accumulating scorer on the **same input** produces a **different** value, so the test
  demonstrably distinguishes an exact path from an inexact one.

## Consequence for the threshold

Because `ETA_ORACLE_L2 = 0` on every descendant, it never dominates:
`TAU_MATERIAL_L2 = max(0, TAU_DYNAMIC_L2, TAU_SITE_L2)` is set by a **scientific** floor in
16 of 16 descendants, never by numerical detectability. That is exactly the separation this
programme was created to establish, and it is the reason the disposition is
`MATERIAL_AND_NUMERICAL_SEPARATED` rather than `NUMERICAL_ONLY`.
""")

Wt("INDEPENDENT_REFERENCE_IMPLEMENTATION_SPEC.md", """# INDEPENDENT_REFERENCE_IMPLEMENTATION_SPEC

`wl2_ref.py` is written from the estimand specification, not from the production code, and an AST
audit confirms it imports nothing from `wl2_prod.py`.

Deliberate differences, so that agreement is informative:

| quantity | production | reference |
|---|---|---|
| weights | trapezoid written as an explicit loop over interior nodes | trapezoid written as a matrix contraction against interval widths |
| summation | forward index order | reverse index order |
| norm | directly from `delta_A`, `delta_B` | only through the `u`, `v` coordinates |
| median | index arithmetic on the sorted list | counting argument on the sorted multiset |
| `max` | Python `max` over three terms | explicit pairwise comparison loop |

Agreement is required on 40 randomly generated fixtures for `X_channels`, `normalizer`,
`tau_site_sq` and `M2sq`, and on all 16 sealed descendants for `TAU_MATERIAL_L2`, `RHO_MED`, `B`
and the `t0` reader. A negative control confirms the reference detects a deliberately wrong
production value, so agreement is evidence rather than tautology.
""")

Wt("PARENT_PROVENANCE_AND_APPEND_ONLY_LEDGER.md", f"""# PARENT_PROVENANCE_AND_APPEND_ONLY_LEDGER

## Chain, proved

    e912a10 -> f81daf9 -> f9e1e39 -> f65851c -> 0d92b61

Direct-parent at every arrow, verified with `git rev-parse <c>^` on the device repository. Short
hashes were resolved to full hashes before any use. `0d92b61` carries the corrected GIMB00 tree
(26 entries) and is the intended append-only closure of `f65851c`.

Manifests re-verified from bytes in this session: WSFSCRP00 {PROV['manifest_verification']['WSFSCRP00']['entries']}/{PROV['manifest_verification']['WSFSCRP00']['entries']},
FSCMA00 {PROV['manifest_verification']['FSCMA00']['entries']}/{PROV['manifest_verification']['FSCMA00']['entries']},
GIMB00 {PROV['manifest_verification']['GIMB00']['entries']}/{PROV['manifest_verification']['GIMB00']['entries']}, zero failures.
Every source file used here is additionally bound by recomputing its git **blob object id** from
local bytes and comparing with the committed tree: 6 of 6 match.

## The corrected gauge oracle is bound; the vacuous one is not

`GIMB00/gimb_oracle_v2.py` is bound by blob id and re-audited here: zero self-comparing
predicates, real region exchanges present in the source, and all four of its negative controls
fire. The vacuous first-pass oracle that GIMB00 declared and superseded is **not** inherited,
merely because it appears in the record.

## Append-only meaning of this successor

GIMB00 established relative gauge-invariant carrier and environmental structure on exposed
development rows, but it did not possess a compatible absolute materiality threshold in the
weighted-L2 response norm. WL2SMF00 defines and prospectively instantiates such a rule on a fresh
sham-only target panel. **It does not reclassify any GIMB00, FSCMA00 or WSFSCRP00 active result.**

    WSFSCRP00_DISPOSITION_REWRITTEN = false
    FSCMA00_DISPOSITION_REWRITTEN   = false
    GIMB00_DISPOSITION_REWRITTEN    = false
    OLD_EXPOSED_ACTIVE_ROWS = INELIGIBLE_FOR_THRESHOLD_SELECTION_OR_VALIDATION
    OLD_SHAMS = EXPOSED_METHOD_DEVELOPMENT_AND_PARSER_FIXTURES_ONLY
    OLD_SHAMS_LOCKED_CALIBRATION_UNITS = 0

No historical sham was used at all: every oracle fixture in this programme is hand constructed.
No historical active row was loaded by any code path in this programme.
""")

Wt("PARENT_AND_WL2SMF00_CLAIM_LEDGER.md", f"""# PARENT_AND_WL2SMF00_CLAIM_LEDGER (append-only)

| # | claim | status | evidence |
|---|---|---|---|
| W1 | The chain `e912a10 -> f81daf9 -> f9e1e39 -> f65851c -> 0d92b61` is direct-parent at every arrow. | ESTABLISHED | device `rev-parse`; blob ids recomputed from local bytes, 6/6 |
| W2 | Materiality and numerical detectability are separated, not merged. | ESTABLISHED | `ETA_ORACLE_L2 = 0` on all 16 descendants, so the threshold is set by a scientific floor everywhere |
| W3 | The scoring path is exactly arithmetic-free of error. | ESTABLISHED (proof + 2 controls) | Fraction reader, exact subtraction, bit-exact npz reload; a float64 path differs on the same input |
| W4 | The oracle suite is non-vacuous. | ESTABLISHED | 14 groups pass, 12 negative controls fire, AST audit rejects an injected self-comparing predicate |
| W5 | `M2` alone cannot validate the gauge scope; the whole-descendant block invariant can. | ESTABLISHED | a per-time swap leaves `M2` unchanged and changes the block invariant |
| W6 | History route is `H3` (complementary allocation orbit); `H1` and `H2` are ineligible. | ESTABLISHED | `apply_dual_history` is lockstep with identical global forcing; no pre-designated physical anchor exists |
| W7 | Geometry route is `G1`: the upstream RNG precursor is geometry-independent. | ESTABLISHED | `seed_state` hashes identically under both geometry settings; geometry enters only via the blob mask |
| W8 | The refactored constructor is semantics-preserving. | ESTABLISHED | both old parity branches reproduced byte-for-byte against committed checkpoint hashes |
| W9 | A complete 16-descendant, 4-block G1 panel exists and is sealed. | ESTABLISHED | 4/4 blocks accepted, 16/16 admissible, panel lock written before the first sham |
| W10 | Every descendant has two byte-identical shams over the full horizon. | ESTABLISHED | 16/16, including the terminal state hash |
| W11 | Every descendant has one finite, positive, sealed threshold. | ESTABLISHED | 16/16; range {min(r['TAU_MATERIAL_L2'] for r in ROWS):.4e} .. {max(r['TAU_MATERIAL_L2'] for r in ROWS):.4e} |
| W12 | Production and independent reference agree everywhere. | ESTABLISHED | 40 random fixtures plus all 16 descendants; a control confirms the reference catches a wrong value |
| W13 | The modal, contrast and quotient-pair propagations are proved, not cited. | ESTABLISHED | isometry, contractive centering, contractive projection, then `L2 <= R1 <= R0 <= E_TAU` |
| W14 | The modal gate strictly implies the total gate. | ESTABLISHED, LIMITING | `L2 <= R0` always, so the two gates are nested; a passing panel needs `R0 > 20 * E_TAU` at share 0.05 |
| W15 | In NEAR geometry the two complementary allocations have systematically different sham drift. | ESTABLISHED (sham-only) | `TAU_DYNAMIC` a0 vs a1 separates in all four NEAR blocks; a purely baseline observation, no response claim |
| W16 | Zero active outcome was generated or opened. | ESTABLISHED | start ledger: 2 setup + 16 construction + 32 sham = 50 of 64; dependency audit shows the threshold pipeline cannot reach an active array |
| W17 | No parent disposition was reclassified. | BY CONSTRUCTION | append-only ledger; no historical active row was loaded by any code path |

## Explicitly NOT claimed

* Not claimed: that the historical carrier structure, environmental extension or founder stratum is
  absolutely material. All three are `NOT_TESTED` and remain so.
* Not claimed: that the old twelve reversed cells now pass. They were not scored under this rule
  and may not be.
* Not claimed: any geometry, history or allocation **response** effect. W15 is a sham drift
  observation about untreated trajectories.
* Not claimed: life, agency, identity, memory, provenance, bath, curvature, multiscale structure,
  universal dimension, population generalisation or independent confirmation.
* The sealed numeric thresholds are valid **only** for this exact reader, masks, normalizer,
  weights, checkpoint, horizon, LawSpec and descendant panel. The formula may inform later designs;
  the numbers do not transfer to other founders.
""")

Wt("PROTOCOL_DEVIATIONS.md", """# PROTOCOL_DEVIATIONS

## D1 — my first dependency audit false-failed on its own blacklist

The audit searched the driver's source for forbidden **substrings** and therefore matched the
blacklist literal it was itself carrying, reporting a failure that did not exist. Replaced by
resolved-symbol AST analysis over `wl2_prod.py`, `wl2_ref.py`, `wl2_sham.py` and `wl2_panel.py`,
which distinguishes a call from a mention. `wl2_panel.py` legitimately *names* the two future
carrier executables as strings inside `FUTURE_ACTIVE_CARRIER_ARM_LOCK.json`, to prevent arm
shopping; the corrected audit confirms it never imports or calls them, and that no active-operator
symbol is called anywhere in the programme.

## D2 — the per-time sham reader series was not persisted

`FRESH_SHAM_RAW_ARCHIVE` contains the 16 descendant checkpoints, the 16 immutable mask pairs, and
every threshold-determining scalar exactly as a rational (`B`, `RHO_MED`, `G2^2`,
`TAU_MATERIAL_L2^2`). It does **not** contain the per-scored-time `SHAM_0` series `X_A[h], X_B[h]`,
which I failed to serialise before the arrays went out of scope.

I did not re-run the shams to recover it. The sham tranche is exactly 32 starts, it was fully
spent, and `MAX_EXTRA_ZERO_OR_RELOAD_CONTROL_STARTS_AFTER_PANEL_LOCK = 0`. Re-running would have
been a `SHAM_START_BUDGET_PROTOCOL_BREACH`, and a budget that bends when it is inconvenient is not
a budget.

Scientific impact: none that I can identify. The sham is the identity operator applied to sealed
checkpoint bytes, the engine is bit-deterministic, and the twin oracle passed 16 of 16 over the
full horizon including the terminal state hash. The series is therefore an exactly reproducible
function of bytes that *are* archived. A future programme re-derives it by running `SHAM_0` again,
which it must do anyway to form `delta = X[INT] - X[SHAM_0]`.

## D3 — start-accounting convention, stated rather than assumed

One constructed descendant state counts as one start, which is exactly the convention WSFSCRP00
used for `make_founder` (found + relax + history + settle = 1). Here the precursor is computed once
per `(seed, geometry)` and shared by the two allocation branches, because the H3 pairing requires
identical precursor bytes. That is strictly **less** engine work than the inherited convention
assumes, so counting one per descendant over-counts rather than under-counts. The raw number of
engine advance sequences (28) is logged alongside the 18 charged starts so the two can be compared.

## No other deviations

No push, no pull request, no workflow trigger. Tommy's checkout untouched. No parent output
overwritten. No historical active row loaded. No active operator constructed or applied.
""")
print("reports written")

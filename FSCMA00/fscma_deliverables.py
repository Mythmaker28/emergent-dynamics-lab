"""FSCMA00 -- generate the Section 15 deliverables from the frozen artefacts. Zero engine starts."""
from __future__ import annotations
import json, hashlib, os, sys, subprocess
from fractions import Fraction as Fr

OUT = "/home/claude/sweep/FSCMA00"
PAR = "/home/claude/sweep/WSFSCRP00"
J = lambda p: json.load(open(p))
Q2 = J(f"{OUT}/FSCMA00_PARENT_Q2_MINIMAL_RECALCULATION.json")
ST = J(f"{OUT}/FSCMA00_STATIC_OBSERVABILITY_RAW.json")
RK = J(f"{OUT}/FSCMA00_RANK_CEILING_AND_PREDICTION.json")
S58 = J(f"{OUT}/FSCMA00_S5_S8.json")
PB = J(f"{OUT}/fscma_probe_raw.json")
PS = J(f"{OUT}/FSCMA00_PROBE_SCORED.json")
LA = J(f"{OUT}/fscma_locked_carrier.json")
LB = J(f"{OUT}/FSCMA00_LOCKED_RAW_CELL_SCORES.json")
PQ = J(f"{PAR}/wsfscrp_q01.json")
PLED = J(f"{PAR}/WSFSCRP00_CANDIDATE_QUEUE_AND_ACCEPTANCE_LEDGER.json")
W = lambda n, s: open(f"{OUT}/{n}", "w").write(s)

PARENT_COMMIT = "e912a1004c5b9732d12a8fcc417002bfd1135622"
ARCHIVE_SHA = "141fe743274c0502ae1d9d06a2ef875988b16fbd5815d7aea02811b1d3d6fcf1"

# =============================================================== 1. provenance and bug audit
W("FSCMA00_PARENT_PROVENANCE_AND_BUG_AUDIT.md", f"""# FSCMA00 -- parent provenance and bug audit

Parent programme: WARPED_SCALE_FIXED_SUPPORT_CAUSAL_RESPONSE_PILOT_00 (WSFSCRP00).
Device-chain parent commit: `{PARENT_COMMIT}` (WSCCRP00).
Parent payload archive sha256: `{ARCHIVE_SHA}` -- reproduced byte-for-byte in this session.

## 1. Integrity

* Archive sha256 recomputed from bytes: MATCHES the reported value exactly.
* `SHA256SUMS`: **49 of 49 entries verified from bytes**, zero failures.
* Parent engine-start ledger: {PQ['engine_starts']['n']} starts (12 GEN + 12 Q0 + 12 Q1), consistent
  with the parent's own log.

## 2. The `state_feats` bug, and why it provably cannot have touched Q2

The parent's `wsfscrp_q234.py` crashed with an `IndexError` in `state_feats` because `st.C` is
three-dimensional (a cohort tracer) and was indexed as if two-dimensional. Two source states are
preserved and separately hashed:

| state | sha256 |
|---|---|
| pre-fix `wsfscrp_q234_PREFIX.py` | `aff4b19937ef431e76420a824f2f888cb23c14364ca870090b872a726ba24521` |
| post-fix `wsfscrp_q234_POSTFIX.py` | `8261da7adbf32eb5f5110c7c6e900d4ec5b0b5adf22949edcec62337825a35f3` |

The minimal diff between them is 28 lines. The argument that Q2 is untouched is positional and
checkable, not a judgement call:

* Q2 is fully computed **and printed** by line 30.
* `state_feats` is first *defined* at line 61 and first *called* at line 90.
* Q0 and Q1 live in a different file (`wsfscrp_q01.py`) which the fix never opened.

A crash at line 90 cannot retroactively alter a value produced at line 30. The fix additionally
added a `time_template_only` nuisance baseline, which enters only as `min(...)` over baselines and
can therefore only **lower** `L_NUIS` -- it makes the Q3 gate strictly harder, never easier.

## 3. Independent recalculation of Q2 -- exact, with certificates

A separately coded verifier recomputed Q2 from the raw 12-row response matrix. It imports nothing
from the parent, re-derives the quadrature weights from the frozen physical grid, and decides both
gates in exact rational arithmetic with **no floating point in the decision path**.

The trick that makes exactness possible: the parent's design matrix carries `sqrt(w)`, which is
irrational, but the 12x12 Gram matrix `G = Xc Xc^T` carries `sqrt(w)*sqrt(w) = w` and is therefore
exactly rational. Singular values of `Xc` are square roots of eigenvalues of `G`. Eigenvalues are
counted exactly by Sylvester's law of inertia (exact LDL^T of `G - tI`).

| quantity | certified value | parent reported | relative difference |
|---|---|---|---|
| sigma2/sigma1 | {Q2['GATE_RATIO_sigma2_over_sigma1_gt_0.10']['certified_interval'][0][:20]} | {Q2['parent_reported']['sigma2_over_sigma1']:.10f} | {Q2['agreement']['parent_float_vs_certified_ratio_rel_error']:.2e} |
| sigma2^2 / sum sigma^2 | {Q2['GATE_FRAC_sigma2sq_over_sumsq_ge_0.05']['certified_interval'][0][:20]} | {Q2['parent_reported']['sigma2sq_frac']:.10f} | {Q2['agreement']['parent_float_vs_certified_frac_rel_error']:.2e} |

Certified brackets are narrower than float64 resolution (relative width ~1e-30), so the meaningful
comparison is the relative error above: the parent's float64 answer is correct to a couple of ULP.

**Gate decisions confirmed exactly.** `sigma2/sigma1 > 0.10` PASSES (by a factor 1.196).
`sigma2^2/sum >= 0.05` FAILS (by a factor 3.578 -- not marginally). The second gate is decided by a
single exact inertia count: exactly **1** eigenvalue is at or above `trace/20`; two were required.

**The parent's arithmetic is vindicated. Its interpretation is not** -- see the mode arbitration
report, which shows the rank-one reading is an artefact of an ungauged channel label.

## 4. A defect the parent recorded and did not act on

`wsfscrp_q01.json` records `domain_ok = false` for **6 of its 12 TRAIN cells** -- every cell using
the S2 sentinel (intensive reflection). This audit determines what failed:

* C1 (`|Mf[0]| <= rho`) holds for intensive reflection on all six founders.
* C2 (`Mf[0] == 0` exactly on the dead gate `rho <= 1e-4`) is violated on 31-67 sites per founder,
  carrying between 8.4e-6 and 2.5e-5 of the total absolute carrier content.
* The engine repairs it within one step: the writer ends every step with
  `newm = clip(m,-1,1) * alive` and `Mf = rho * newm`, so `Mf` is exactly zero off the gate at the
  end of every step, unconditionally. It is not inert, though: during that first step the carrier
  transport reads `fM = Mf/max(rho,EPS)`, so off-gate carrier can be advected onto live neighbours
  before the gate re-applies.

This is a defect in the parent's domain declaration or in its choice of S2 instance. It is
**recorded, not repaired**: parent outputs are append-only.

## 5. Delivery defect inherited from the parent

WSFSCRP00 produced no commit: the device bridge was disconnected when it finished. That delivery
gap is closed by this programme's Git section. Reattachment is a delivery repair, not a science
change; no parent disposition is altered by it.
""")

# =============================================================== 3. static observability
A = ST["A_coordinate_frame"]
B = ST["B_one_step_dependency_matrix"]
C = ST["C_operator_static_audit"]["per_operator"]
W("FSCMA00_STATIC_OBSERVABILITY_REPORT.md", f"""# FSCMA00 -- static structural-observability audit

**Zero engine starts.** Nothing in this phase called `engine.step()`. The dynamics were audited by
parsing the engine source, which is a statement about *all* states; the operators were audited by
applying them to checkpoint bytes and diffing. A probe would have told us about one state.

## A. Is a fixed grid-index mask correctly called *Eulerian*?

Criterion: the time-stepping must never re-index the lattice -- neighbour access only by literal
unit offsets, no index-permuting call, no spatial fancy indexing, and no state field rebound to a
permuted copy of itself.

| module | np.roll calls | all shifts literal, abs 1 | permuting calls | spatial re-index | rebinds |
|---|---|---|---|---|---|
{chr(10).join('| `%s` | %d | %s | %d | %d | %d |' % (m['file'].split('/')[-1], m['n_roll_calls'], m['all_roll_shifts_literal_and_unit'], len(m['other_index_permuting_calls']), len(m['spatial_reindexing_in_time_stepping']), len(m['state_field_rebound_to_permuted_self'])) for m in A['modules'])}

**VERDICT: {A['VERDICT']}.** The word *Eulerian* is licensed.

Scope caveat, which matters more than the verdict: {A['scope_caveat']}

{A['interventions_are_not_frame_motion']}

## B. One-step dependency matrix, derived from the AST

Def-use reachability over `PPAIEngine.step`; loops iterated to a fixed point, branches unioned.
Sound over-approximation: a listed dependency may be spurious, an **absent** one is provably
unreachable in one step.

| output | one-step input dependencies |
|---|---|
{chr(10).join('| `%s` | %s |' % (k, ', '.join('`%s`' % x for x in v)) for k, v in B['matrix_output_field_to_input_fields'].items())}

The decisive line: **`rho` depends on `N` in one step ({B['rho_depends_on_N_in_one_step']}) and on
`Mf` in one step ({B['rho_depends_on_Mf_in_one_step']})**. The carrier's only exit is
`z = newm[0] -> kappa(z) -> the face permeability of c and N`, updated at the end of the step, so
`rho` first sees it on the next step.

{B['scored_grid_caveat'] if 'scored_grid_caveat' in B else B['causal_order_to_rho']['scored_grid_caveat']}

## C. Per-operator static audit, 6 BASIS founders

| operator | touch set | consistent | no alias/cache | domain C1+C2 | exact sum preserved | delta support |
|---|---|---|---|---|---|---|
{chr(10).join('| `%s` | %s | %s | %s | %s | %s | %s |' % (n, s['touched_fields'], s['touched_fields_consistent_across_founders'], s['all_no_alias_no_cache'], s['all_domain_ok'], s['exact_sum_preserved_per_touched_field'], {k: ('subset of A u B' if v['subset_of_AuB'] else ('global' if v['global'] else 'wide')) for k, v in s['support'].items()}) for n, s in C.items())}

Intensive and extensive reflection both breach the declared joint domain (see the provenance
audit). Non-conservation of the carrier sum for intensive reflection and total ablation is by
construction, not a defect: those operators conserve the intensive multiset, or nothing.

## D. Intervention input span

Two disjoint native input blocks: **{ST['D_intervention_input_span']['carrier_block']}** for every
carrier operator, **{ST['D_intervention_input_span']['environmental_block']}** for every
environmental operator. **VERDICT: {ST['D_intervention_input_span']['VERDICT']}.**

Distinctness is proved three ways, not asserted:

{chr(10).join('%d. %s' % (i + 1, x) for i, x in enumerate(ST['D_intervention_input_span']['distinctness_proof']))}
""")

json.dump({"native_input_blocks": ST["D_intervention_input_span"]["native_input_blocks"],
           "n_distinct_native_blocks": ST["D_intervention_input_span"]["n_distinct_native_blocks"],
           "carrier_block": ST["D_intervention_input_span"]["carrier_block"],
           "environmental_block": ST["D_intervention_input_span"]["environmental_block"],
           "blocks_are_disjoint": ST["D_intervention_input_span"]["blocks_are_disjoint"],
           "distinctness_proof": ST["D_intervention_input_span"]["distinctness_proof"],
           "one_step_dependency_matrix": B["matrix_output_field_to_input_fields"],
           "ENV_SECONDARY_static_admissibility":
               ST["D_intervention_input_span"]["ENV_SECONDARY_static_admissibility"],
           "VERDICT": ST["D_intervention_input_span"]["VERDICT"],
           "per_operator_static_audit": C},
          open(f"{OUT}/FSCMA00_INTERVENTION_INPUT_SPAN_MANIFEST.json", "w"), indent=1)

# =============================================================== 5,6,7 freeze / panel / ledger
W("FSCMA00_PROTOCOL_FREEZE.md", f"""# FSCMA00 -- protocol freeze

Every item below was written to disk before the first environmental engine start of this
programme. Nothing was refitted afterwards.

## Carrier sentinels (inherited, uniqueness proved)

* **CARRIER_1** = `{S58['S6_protocol_freeze']['carrier_sentinels']['CARRIER_1']['instance']}`
  (`{S58['S6_protocol_freeze']['carrier_sentinels']['CARRIER_1']['callable']}`),
  superfamily {S58['S6_protocol_freeze']['carrier_sentinels']['CARRIER_1']['superfamily']}.
* **CARRIER_2** = `{S58['S6_protocol_freeze']['carrier_sentinels']['CARRIER_2']['instance']}`
  (`{S58['S6_protocol_freeze']['carrier_sentinels']['CARRIER_2']['callable']}`),
  superfamily {S58['S6_protocol_freeze']['carrier_sentinels']['CARRIER_2']['superfamily']}.

Uniqueness: {' '.join(S58['S6_protocol_freeze']['carrier_sentinels']['uniqueness_proof'])}
**VERDICT: {S58['S6_protocol_freeze']['carrier_sentinels']['VERDICT']}**

## Environmental operators

* **ENV_PRIMARY** `{S58['S6_protocol_freeze']['environmental_operators']['ENV_PRIMARY']['callable']}`
  -- {S58['S6_protocol_freeze']['environmental_operators']['ENV_PRIMARY']['algebra']}
* **ENV_SECONDARY** `{S58['S6_protocol_freeze']['environmental_operators']['ENV_SECONDARY']['callable']}`
  -- statically admissible and, unlike the plan sketched at the start, **executed**, because the
  frozen start-accounting matrix showed it fits.

## The A/B quotient

The endpoint pair is *unordered*, canonicalised per founder by sorted site-id lists, so channel A
of one founder has no a-priori relation to channel A of another. Fitting one family across founders
requires fixing that gauge first.

* Gauge: founder **{sorted(int(s) for s in S58['S5_AB_quotient']['orientation'])[0]}** fixed
  `no_swap`; the remaining five enumerated exhaustively (2^5 = 32).
* Objective: minimum exact weighted residual of the one-mode model, `trace(G) - lambda_1(G)`.
* Winner: swap **{S58['S5_AB_quotient']['winner']['swapped']}**.
* Exactly certified against the runner-up: winner residual upper bound
  {float(Fr(S58['S5_AB_quotient']['exact_certificate']['winner_residual_upper_bound'])):.6e} <
  runner-up lower bound
  {float(Fr(S58['S5_AB_quotient']['exact_certificate']['runner_up_residual_lower_bound'])):.6e},
  relative gap {S58['S5_AB_quotient']['exact_certificate']['relative_gap']:.3f}.
* **VERDICT: {S58['S5_AB_quotient']['VERDICT']}**

An independent, hypothesis-free rule -- align each founder's CARRIER_1 response in sign with the
gauge founder's -- selects the **same** three founders. The two rules were checked against each
other precisely because the enumeration objective could otherwise be accused of rewarding a
collapsed spread rather than a one-dimensional one.

## No-change declarations

{chr(10).join('* `%s` = %s' % (k, v) for k, v in S58['S6_protocol_freeze']['no_change_declarations'].items())}

## Frozen worst-case start accounting

Written before the first outcome. Caps: PROBE 24, LOCKED 60, TOTAL 84.

| line | planned | actually consumed |
|---|---|---|
| PROBE sham + replicate | 7 | 7 |
| PROBE ENV_PRIMARY | 6 | 6 |
| PROBE ENV_SECONDARY | 6 | 6 |
| PROBE discarded pre-outcome | 0 | 1 |
| LOCKED sham | 6 | 12 |
| LOCKED CARRIER_1 + CARRIER_2 | 12 | 12 |
| LOCKED ENV_PRIMARY | 6 | 6 |
| **total** | **43** | **50** |

**Deviation, disclosed:** the LOCKED sham line cost 12 instead of 6. Stage A of the sealed LOCKED
evaluation did not persist its sham forks, so stage B had to re-derive them. That is an oversight
in my staging design, not a cap breach: LOCKED consumed 30 of 60 and the programme 50 of 84.
""")

json.dump({"panel": S58["S7_panel"], "contamination": S58["S7_contamination_ledger"],
           "start_accounting_frozen": S58["S7_frozen_start_accounting"],
           "actual_starts": {"PROBE_scored": PB["engine_starts"]["n"],
                             "PROBE_discarded_pre_outcome": PB["engine_starts"]["discarded_pre_outcome"],
                             "LOCKED": LB["engine_starts"]["n"],
                             "TOTAL_CONSUMED": PB["engine_starts"]["n"]
                                               + PB["engine_starts"]["discarded_pre_outcome"]
                                               + LB["engine_starts"]["n"],
                             "CAP": 84},
           "deviation_disclosed": "the LOCKED sham line cost 12 rather than the 6 budgeted, because "
                                  "stage A of the seal did not persist its sham forks and stage B "
                                  "re-derived them. Within cap; disclosed rather than smoothed.",
           "ADDITIONAL_INHERITED_CONFOUND": {
               "finding": "geometry class, history order and canonical channel label are ONE axis, "
                          "not three: make_founder assigns (HIST_H, HIST_L) on even seeds and "
                          "(HIST_L, HIST_H) on odd seeds, while the frozen queue makes even seeds "
                          "FAR and odd seeds NEAR.",
               "consequence": "WSFSCRP00's claim of two independent geometry classes per role as a "
                              "diversity axis does not hold. The strata are perfectly confounded.",
               "status": "recorded against the parent, append-only; the gauge fixing in Section 5 "
                         "neutralises it for this programme's estimates."}},
          open(f"{OUT}/FSCMA00_PANEL_AND_ANCESTRY_MANIFEST.json", "w"), indent=1)

json.dump({**S58["S7_contamination_ledger"],
           "sealed_stages": ["LOCKED stage A ran sham + both carrier sentinels and derived the "
                             "orientation from CARRIER_1 alone; the environmental outcome did not "
                             "exist at that moment.",
                             "LOCKED stage B ran the environmental arm afterwards and refitted "
                             "nothing."],
           "predictions_frozen_before_the_data_they_predict": [
               "P1 (environmental common-mode share) and P2 (off-family) -- frozen before any "
               "environmental engine start.",
               "P3 (LOCKED orientation from seed parity) -- frozen before the first LOCKED start."],
           "held_out_namespaces": "62000-62009 never opened, never read, at any point."},
          open(f"{OUT}/FSCMA00_CONTAMINATION_AND_ACCESS_LEDGER.json", "w"), indent=1)

json.dump({"model": S58["S8_affine_family"]["model"],
           "definitions": S58["S8_affine_family"]["definitions"],
           "gates_on_the_ORIENTED_basis": S58["S8_affine_family"]["gates"],
           "BASIS_TUBE_PASS_at_k1": S58["S8_affine_family"]["BASIS_TUBE_PASS"],
           "cells": S58["S8_affine_family"]["cells"],
           "dimension_sweep_oriented": {str(k): {"carrier_OFF_max": PS["P2_off_family"]["per_k"][str(k)]["carrier_OFF_max"],
                                                 "carrier_O_energy": PS["P2_off_family"]["per_k"][str(k)]["carrier_O_energy"],
                                                 "tube_holds": PS["P2_off_family"]["per_k"][str(k)]["carrier_tube_holds_at_this_k"]}
                                        for k in (1, 2, 3, 4)},
           "smallest_k_with_a_valid_carrier_tube": PS["P2_off_family"]["smallest_k_with_carrier_tube"],
           "phi1": S58["S8_affine_family"]["phi1"], "mu": S58["S8_affine_family"]["mu"],
           "FINDING": "the one-mode affine family FAILS its own BASIS tube gate once the channel "
                      "gauge is fixed. H1 as posed is refuted on the carrier repertoire alone, "
                      "before any environmental data is used."},
          open(f"{OUT}/FSCMA00_AFFINE_BASIS_MANIFEST.json", "w"), indent=1)

json.dump({"prediction_frozen": LA["prediction"], "P3_checks": LA["P3_checks"],
           "P3_CONFIRMED": LA["P3_CONFIRMED"],
           "orientation_BASIS": S58["S5_AB_quotient"]["orientation"],
           "orientation_LOCKED": LA["orientation"],
           "O_CARRIER": LB["O_CARRIER"], "O_ENV": LB["O_ENV"], "J_ENV": LB["J_ENV"],
           "C_ENV": LB["C_ENV"], "stability": LB["stability"], "shares": LB["shares"],
           "LEARNABILITY": LB["LEARNABILITY"],
           "INTERNAL_MODE_STATUS": LB["INTERNAL_MODE_STATUS"],
           "MODE_ARBITRATION": LB["MODE_ARBITRATION"]},
          open(f"{OUT}/FSCMA00_LOCKED_PREDICTIONS_AND_PROJECTIONS.json", "w"), indent=1)

# =============================================================== oracle + probe + arbitration
W("FSCMA00_FIXED_SUPPORT_ORACLE_REPORT.md", f"""# FSCMA00 -- fixed-support oracle report

The reader, endpoint, grid, weights, detector and checkpoint time are inherited from WSFSCRP00
without a single change (`FIXED_SUPPORT_READER_CHANGE = false`).

## Oracle checks passed in this programme

* **Sham determinism re-verified in this container.** A replicate sham on the gauge founder
  reproduced the other sham bit-for-bit across the full horizon, including the terminal state
  hash: `{PB['determinism'][0]['sham_replicate_identical']}`.
* **Structural zero at h = 0.** Every one of the {len(PB['rows']) + len(LA['rows']) + 6} scored
  intervention arms in this programme has `r(h=0) = (0, 0)` exactly, in rational arithmetic.
* **Touch sets.** Every environmental arm touched `['N']` and nothing else; every carrier arm
  touched `['Mf']` and nothing else.
* **Source immutability.** The founder checkpoint bytes were re-hashed after every operator
  application and were unchanged in every case.
* **Exact budget injection.** `sum(N)` changed by exactly 2048.0 for `+0.50*N0` and exactly 1024.0
  for `+0.25*N0` on a 64x64 lattice with `N0 = 1` -- i.e. `amp * N0 * L^2`, to the bit.

## Material signal

| arm | A_bu range | A/ETA range |
|---|---|---|
| carrier (BASIS, parent) | 4.750e-03 .. 9.700e-03 | 3.69 .. 8.26 |
| carrier (LOCKED, this programme) | {min(float(Fr(r['A_bu'])) for r in LA['rows']):.3e} .. {max(float(Fr(r['A_bu'])) for r in LA['rows']):.3e} | {min(r['A_over_ETA'] for r in LA['rows']):.2f} .. {max(r['A_over_ETA'] for r in LA['rows']):.2f} |
| environmental +0.25 (BASIS) | {min(float(Fr(r['A_bu'])) for r in PB['rows'] if r['arm'] == 'ENV_SECONDARY'):.3e} .. {max(float(Fr(r['A_bu'])) for r in PB['rows'] if r['arm'] == 'ENV_SECONDARY'):.3e} | {min(r['A_over_ETA'] for r in PB['rows'] if r['arm'] == 'ENV_SECONDARY'):.2f} .. {max(r['A_over_ETA'] for r in PB['rows'] if r['arm'] == 'ENV_SECONDARY'):.2f} |
| environmental +0.50 (BASIS) | {min(float(Fr(r['A_bu'])) for r in PB['rows'] if r['arm'] == 'ENV_PRIMARY'):.3e} .. {max(float(Fr(r['A_bu'])) for r in PB['rows'] if r['arm'] == 'ENV_PRIMARY'):.3e} | {min(r['A_over_ETA'] for r in PB['rows'] if r['arm'] == 'ENV_PRIMARY'):.2f} .. {max(r['A_over_ETA'] for r in PB['rows'] if r['arm'] == 'ENV_PRIMARY'):.2f} |

Every cell clears its own ETA. The environmental response is about
{PS['amplitude']['env_over_carrier_median']:.1f}x the carrier response in weighted amplitude.
""")

W("FSCMA00_PROBE_ENVIRONMENTAL_REPORT.md", f"""# FSCMA00 -- environmental probe report

19 engine starts (plus 1 discarded pre-outcome), against a cap of 24. Two predictions were frozen
to disk **before** the first environmental start, both derived from static structure alone.

## The mechanism that generated the predictions

{chr(10).join('* ' + x for x in RK['G_preregistered_prediction']['mechanism'])}

## P1 -- common mode

Prediction: the environmental response loads on `s = dA + dB` more heavily than *any* carrier cell.
Threshold, fixed in advance from the 12 carrier cells: **{PS['P1_common_mode']['threshold_env_sum_share_gt']:.4f}**.

| set | sum-mode share |
|---|---|
| carrier, 12 cells | {PS['P1_common_mode']['carrier_sum_share']['min']:.4f} .. {PS['P1_common_mode']['carrier_sum_share']['max']:.4f} |
| environmental, 12 cells | {PS['P1_common_mode']['env_sum_share_min']:.4f} .. {PS['P1_common_mode']['env_sum_share_max']:.4f} |

**{PS['P1_common_mode']['VERDICT']}**, with no overlap and a separation factor of
{PS['P1_common_mode']['separation_factor']:.1f}. Carrier operators redistribute between the two
windows; the environmental operator fills both.

## P2 -- off-family

Prediction: environmental cells fall outside the affine family fitted on the carrier BASIS, at the
same 0.10 threshold the carrier cells must satisfy from the inside.

| k | carrier OFF max (tube valid?) | environmental OFF range |
|---|---|---|
{chr(10).join('| %d | %.4f (%s) | %.4f .. %.4f |' % (k, PS['P2_off_family']['per_k'][str(k)]['carrier_OFF_max'], PS['P2_off_family']['per_k'][str(k)]['carrier_tube_holds_at_this_k'], PS['P2_off_family']['per_k'][str(k)]['env_OFF_min'], PS['P2_off_family']['per_k'][str(k)]['env_OFF_max']) for k in (1, 2, 3, 4))}

At k = 1 the environmental response is essentially **orthogonal** to the carrier family
(OFF ~ 0.999). Even at k = 4, the smallest dimension at which the carrier tube closes at all, the
environmental cells remain at OFF ~ 0.15. **{PS['P2_off_family']['VERDICT_at_k1']}**.

## Dose

`|r(+0.50)| / |r(+0.25)| = {PS['dose']['median_norm_ratio']:.4f}` with cosine
`>= {PS['dose']['min_cosine']:.6f}`. The environmental response is a one-dimensional amplitude
family, close to linear in dose (slightly sublinear -- mild saturation), along a direction the
carrier repertoire cannot reach.

**Branch: {PS['BRANCH']}.**
""")

L = LB
W("FSCMA00_MODE_ARBITRATION_REPORT.md", f"""# FSCMA00 -- mode arbitration report

## What was asked, and why the question had to change

The handoff asked me to arbitrate between H1 (one affine 1-D response family transfers across the
carrier repertoire and the +0.5 environmental operator) and H2 (the carrier repertoire is limited
and the environmental operator adds a mode). Both were framed as useful, neither as a failure.

That framing rested on the parent's finding `RANK_ONE_FIXED_SUPPORT_RESPONSE`. I confirmed the
parent's arithmetic exactly -- and then found that the premise does not survive gauge fixing.

## Finding 1 -- the parent's rank-one result is a labelling artefact

The endpoint pair is unordered and canonicalised by sorted site-id lists. That rule is
deterministic but physically arbitrary: it does not link founder to founder. And it is confounded.
`make_founder` assigns `(HIST_H, HIST_L)` on even seeds and `(HIST_L, HIST_H)` on odd seeds, while
the frozen queue makes even seeds FAR and odd seeds NEAR. **Geometry class, history order and
channel label are one axis, not three.**

Fixing that gauge -- by two rules that agree, one of them the handoff's own -- changes the picture:

| quantity | parent frame (ungauged) | gauged frame |
|---|---|---|
| sigma2 / sigma1 | 0.1196 (certified exactly) | 0.3424 |
| lambda2 / trace | 0.0140 -- the gate that **failed** | 0.1035 -- the same gate **passes** |
| lambda1 / trace | 0.9767 | 0.8831 |
| per-cell OFF at k=1 | 0.094 .. 0.266 | 0.194 .. 0.525 |

The response was never rank one. Roughly nine tenths of the leading mode in the parent's frame is
the FAR/NEAR label flip, not dynamics.

## Finding 2 -- H1 is refuted on the carrier repertoire alone

In the gauged frame the affine family `mu + a*phi1` fails its own BASIS tube gate:
`O_BASIS = {S58['S8_affine_family']['gates']['O_BASIS']:.4f}` against a 0.05 threshold, and every
one of the 12 cells exceeds the 0.10 per-cell threshold. On the outcome-unseen LOCKED panel the
same family leaves `OFF_max = {L['O_CARRIER']['1']['locked_OFF_max']:.4f}` at k = 1.

**{L['INTERNAL_MODE_STATUS']['verdict']}.** The two gauged carrier modes are interpretable: the
first separates the two sentinels (an operator axis), the second separates the two founder strata
identically for both operators (a founder main effect carried by the confound, not an
operator-discriminating mode).

## Finding 3 -- H2 is confirmed on held-out founders

| metric | BASIS | LOCKED (outcome-unseen) |
|---|---|---|
| environmental OFF vs carrier family, k=1 | {PS['P2_off_family']['per_k']['1']['env_OFF_min']:.4f} | {L['O_ENV']['1']['locked_OFF_min']:.4f} |
| environmental OFF vs carrier family, k=4 | {PS['P2_off_family']['per_k']['4']['env_OFF_min']:.4f} | {L['O_ENV']['4']['locked_OFF_min']:.4f} |
| carrier common-mode share | <= {PS['P1_common_mode']['carrier_sum_share']['max']:.4f} | <= {L['C_ENV']['locked_carrier_sum_share']['max']:.4f} |
| environmental common-mode share | >= {PS['P1_common_mode']['env_sum_share_min']:.4f} | >= {L['C_ENV']['locked_env_sum_share']['min']:.4f} |

Stability of the environmental direction:

* `cos(BASIS env, LOCKED env) = {L['stability']['cos_basis_env_vs_locked_env']:.6f}`
* `cos(dose +0.50, dose +0.25) = {L['stability']['cos_basis_env_primary_vs_secondary_dose']:.6f}`
* `cos(env, carrier leading mode) = {L['stability']['cos_env_vs_carrier_leading_mode']:.4f}` -- about
  {__import__('math').degrees(__import__('math').acos(L['stability']['cos_env_vs_carrier_leading_mode'])):.1f} degrees, near orthogonal.

**{L['MODE_ARBITRATION']['label']}.**

## Learnability

A predictor fitted on BASIS alone -- the BASIS mean response of the same operator -- reaches a
median exact weighted L1 of {L['LEARNABILITY']['median_L_ARM_over_L_GRAND']:.4f} of the
operator-agnostic baseline on LOCKED cells, improving in **every** cell. Per arm:
{ {k: round(v, 4) for k, v in L['LEARNABILITY']['per_arm'].items()} }. The mode structure
transfers; it is not a per-founder curiosity.

## What does NOT transfer, stated plainly

`J_ENV` at k = 1 is {L['J_ENV']['1']['locked_OFF_max']:.4f}: the *direction* of the environmental
mode transfers almost perfectly (cosine 0.9998), but the fine founder-to-founder variation *within*
the environmental arm is not captured by one BASIS-fitted deviation direction. The claim is about
the mode, not about founder-level fine structure.

## A refuted prediction, reported because it was made

P3 predicted that LOCKED orientation would follow seed parity exactly, since parity drives the
history/geometry confound. **It failed on 1 of 6**: founder 64007 (odd, NEAR) required a swap, with
a decisive cosine of {[c['cos_plain'] for c in LA['P3_checks'] if c['seed'] == 64007][0]:+.4f} -- not a
borderline call. The canonical label depends on the lexicographically smallest site id, which
depends on blob *shape*, not only on which half-plane a body sits in. So the label is even less
trustworthy than the parity story implied. This strengthens the case for gauge fixing rather than
weakening it, but it is a refutation of something I wrote down in advance and it is recorded as one.

## Scope

* Single substrate, single LawSpec, one checkpoint time, one horizon, 12 founders total.
* `CONFIRMATORY_OR_POPULATION_CLAIM = false`. This is a developmental result on a fixed dev panel.
* The LOCKED panel is outcome-unseen but feature-exposed: its checkpoints and masks were generated
  and hashed by the parent.
* `INDEPENDENT_REVIEW = NOT_PERFORMED`. Single executor, sequential, internal procedural locking.
""")

# =============================================================== claim + start ledgers
W("FSCMA00_CLAIM_LEDGER.md", f"""# FSCMA00 -- claim ledger (append-only)

| # | claim | status | evidence |
|---|---|---|---|
| 1 | The WSFSCRP00 payload archive and all 49 SHA256SUMS entries verify from bytes. | ESTABLISHED | recomputed in-session |
| 2 | The parent's `state_feats` bug provably could not alter Q2, Q0 or Q1. | ESTABLISHED | positional argument: Q2 printed at line 30, crash site line 90, Q0/Q1 in a different file |
| 3 | The parent's Q2 numbers are exactly correct: sigma2/sigma1 = 0.11962171538728941..., sigma2^2/sum = 0.01397555789051734... | ESTABLISHED (exact, certificate-bearing) | independent verifier, Sylvester inertia in exact rational arithmetic; parent float64 correct to ~3e-16 relative |
| 4 | The frac gate fails by a factor 3.578, decided by a single exact inertia count (1 eigenvalue at or above trace/20; 2 required). | ESTABLISHED | no approximation in the decision path |
| 5 | The fixed t0 index masks are correctly called EULERIAN, but not Lagrangian. | ESTABLISHED | AST audit of both engine modules: 27 np.roll calls, all literal unit shifts; zero permuting calls; zero spatial re-indexing; zero rebinds |
| 6 | `rho` depends on `N` within one step and on `Mf` only from the second step. | ESTABLISHED | def-use reachability over the AST; absence in the matrix is a proof of unreachability |
| 7 | The intervention repertoire spans two disjoint native input blocks, {{Mf}} and {{N}}. | ESTABLISHED | bytewise touch sets on 6 founders x 6 operators, plus the budget argument |
| 8 | WSFSCRP00 recorded `domain_ok = false` in 6 of 12 TRAIN cells and did not act on it; the failure is C2 on 31-67 dead sites, repaired by the engine within one step. | ESTABLISHED, recorded against the parent | exact off-gate content measured per cell |
| 9 | Geometry class, history order and canonical channel label are one confounded axis in this panel. | ESTABLISHED | `make_founder` seed parity x frozen queue parity, verified in source and in the data |
| 10 | `RANK_ONE_FIXED_SUPPORT_RESPONSE` is an artefact of the ungauged channel label. Gauged, sigma2/sigma1 = 0.3424 and lambda2/trace = 0.1035, so the parent's failing gate passes. | ESTABLISHED | two independent gauge rules agree; certified exactly against the runner-up |
| 11 | H1 (one affine 1-D family) is refuted on the carrier repertoire alone, before any environmental data. | ESTABLISHED | BASIS tube gate fails: O_BASIS = {S58['S8_affine_family']['gates']['O_BASIS']:.4f} > 0.05, all 12 cells above 0.10 |
| 12 | The environmental operator adds a mode the carrier repertoire cannot reach, confirmed on outcome-unseen founders. | ESTABLISHED (developmental) | P1 and P2 both preregistered and both confirmed; LOCKED OFF = {L['O_ENV']['1']['locked_OFF_min']:.4f} at k=1; common-mode separation x{L['C_ENV']['separation_factor']:.1f} |
| 13 | The environmental mode is one-dimensional and near-linear in dose. | ESTABLISHED | cosine 0.9996 between +0.50 and +0.25; norm ratio {PS['dose']['median_norm_ratio']:.4f} |
| 14 | The mode structure is learnable and transfers: BASIS-fitted per-operator means beat the operator-agnostic baseline in every LOCKED cell. | ESTABLISHED | median L1 ratio {L['LEARNABILITY']['median_L_ARM_over_L_GRAND']:.4f} |
| 15 | P3 (LOCKED orientation follows seed parity) is REFUTED, 5 of 6. | REFUTED, recorded | founder 64007, cosine {[c['cos_plain'] for c in LA['P3_checks'] if c['seed'] == 64007][0]:+.4f} |
| 16 | Founder-level fine structure within the environmental arm does not transfer from one BASIS-fitted deviation direction. | ESTABLISHED, limiting | J_ENV at k=1 = {L['J_ENV']['1']['locked_OFF_max']:.4f} |
| 17 | No population or confirmatory claim is made. | BY CONSTRUCTION | `CONFIRMATORY_OR_POPULATION_CLAIM = false`; 12 founders, one substrate, one LawSpec |

## Withdrawn or superseded in this programme

Nothing produced by a parent programme is rewritten. Claim 10 **supersedes the interpretation**
attached to the parent's `RANK_ONE_FIXED_SUPPORT_RESPONSE` label while leaving the parent's numbers
standing exactly as reported -- they are correct, and this programme certifies them.

## Self-defects declared

1. My first orientation objective (minimum absolute weighted residual) can be gamed by collapsing
   the spread rather than making it one-dimensional. I noticed this before using it, checked it
   against an independent hypothesis-free rule, and reported that the two agree. Had they
   disagreed, the enumeration result would have been unusable.
2. My LOCKED seal cost 6 more engine starts than budgeted because stage A did not persist its sham
   forks. Within cap, disclosed above.
3. One PROBE engine start was consumed and discarded by a crash in a diagnostic line before the arm
   was scored. Pre-outcome infrastructure retry 1 of 6.
""")

json.dump({"parent_WSFSCRP00": {"n": PQ["engine_starts"]["n"], "log": PQ["engine_starts"]["log"]},
           "FSCMA00_phase0_and_phase1": {"n": 0,
                                         "note": "provenance, Q2 recalculation, coordinate frame, "
                                                 "dependency matrix, operator audit, rank algebra "
                                                 "and all Section 5-8 freezes cost zero starts"},
           "FSCMA00_PROBE": {"n": PB["engine_starts"]["n"], "cap": 24,
                             "discarded_pre_outcome": PB["engine_starts"]["discarded_pre_outcome"],
                             "log": PB["engine_starts"]["log"]},
           "FSCMA00_LOCKED": {"n": LB["engine_starts"]["n"], "cap": 60,
                              "log": LB["engine_starts"]["log"]},
           "TOTALS": {"scored": PB["engine_starts"]["n"] + LB["engine_starts"]["n"],
                      "discarded": PB["engine_starts"]["discarded_pre_outcome"],
                      "consumed": PB["engine_starts"]["n"] + LB["engine_starts"]["n"]
                                  + PB["engine_starts"]["discarded_pre_outcome"],
                      "MAX_TOTAL": 84},
           "MAX_POST_SCORED_OUTPUT_RETRIES": 0,
           "post_scored_retries_used": 0},
          open(f"{OUT}/FSCMA00_ENGINE_START_LEDGER.json", "w"), indent=1)
print("deliverables written")

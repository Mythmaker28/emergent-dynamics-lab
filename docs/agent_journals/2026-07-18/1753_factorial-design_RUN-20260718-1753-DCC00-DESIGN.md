# DEEP-CHECKPOINT-CAUSAL-CUT-00 Phase 0 factorial-design audit

- **Role:** independent factorial, estimand, hypothesis, raw-contract, and kill-switch designer
- **Run ID:** `RUN-20260718-1753-DCC00-DESIGN`
- **Start time:** 2026-07-18 17:53:47 +02:00
- **End time:** 2026-07-18 17:56:04 +02:00
- **Starting branch:** `codex/deep-checkpoint-causal-cut-00-phase0`
- **Starting Git state:** HEAD `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; only concurrent Phase-0
  integration/audit artefacts untracked; no tracked changes
- **Ending Git state:** HEAD unchanged at `cce7a27955f5cfb1fc3d95388bba9378bc8d85eb`; this journal untracked
  alongside concurrent Phase-0 artefacts; no tracked files changed by this auditor

## Assigned scope

Independently specify the non-executable Phase-0 scientific design for an exact-clone `C00/C10/C01/C11` local-cut
factorial starting from already-open deep DEV checkpoints, with separate future responses `Y_A/Y_B`, a full
non-symmetrized causal matrix, competing explanations, raw numerical diagnostics, and fail-closed gates. Audit only:
do not execute an intervention, inspect or compute feeding contrasts, initialize a seed, use `58xxx`, alter V5/03G,
or authorize a prospective family.

## Actions

- Read the repository operating contract and durable state in the required order, including the accepted
  `STOP_PAIR_MECHANICS` record.
- Read the Phase-0 pair-feasibility record and inspected the existing no-swap, local-memory-surgery, global-ablation,
  serialization, no-write, and frozen engine implementations.
- Inspected only mechanical metadata from existing DEV qualification records; no response/outcome value was read.
- Audited the identification content of a four-arm local-cut design and documented the conditions under which it
  would be interpretable.

## Important files read or changed

Read:

- `AGENTS.md`; `docs/RESEARCH_CHARTER.md`; `docs/PROJECT_STATE.md`; `docs/DECISION_LOG.md`;
  `docs/EXPERIMENT_INDEX.md`; `docs/RUN_INDEX.md`;
- latest partial integration journal and `DIRECTED_CAUSAL_PAIR_00_PHASE05_DEV_MANIFEST.json` / Phase-0.5 report;
- `DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`;
- `ACCESS_STRUCTURE_00_PHASE0_REPORT.md`, Phase-0.5 report, and Phase-0.6B no-swap design;
- `access_structure_operators.py`, `access_structure_noswap_operators.py`,
  `access_structure_noswap_dev_feasibility.py`, `turnover_diag_engine.py`, `turnover_dev_runner.py`, and
  `edlab/experiments/sc_mcm/engine.py`.

Changed: this uniquely named journal only.

## Reproducible commands and experiments

Read-only `git`, `rg`, PowerShell file reads, and standard-library JSON key/whitelist extraction. No simulation,
checkpoint reconstruction, cut, probe, feeding computation, prospective execution, or outcome analysis was run.
`git diff --check` and the trailing-whitespace scan passed. No code changed, so no engine test was run.

## Independent operator judgment

**STOP-LOCAL-CUT.** The repository currently has no operator that is simultaneously target-local, a deletion of a
candidate readout/access edge, no-writer, and mechanically interpretable:

- `lam_plus=0`, `up_ref=0`, and `copy_disabled` are world-global controls.
- local `Mf` erase/standardization removes or replaces the source state, not its access edge.
- the no-swap collar overwrites `rho,U,V,c,N,C,uptake,Mf` every step, is non-conservative, and proves bit-exact
  isolation only with the separate global `up_ref=0` modification. Its active reference replay has maximum collar
  jump `1.8145423147669801` and core disturbance `1.8655212794863028`, while the own-replay sham is `0.0/0.0`.
  It has no dual-target `C11` qualification.

The following design is therefore a conditional identification specification, not an invented implementation or
authorization.

## Minimal exact-clone factorial

For original DEV world `w`, require one immutable serialized checkpoint `S_w` containing exact `step` and
`rho,U,V,c,N,C,uptake,Mf`. Deserialize it four times, verify byte identity, and freeze two disjoint physical support
masks `D_A,D_B` from checkpoint geometry only. No diagnostic ID or arm-specific tracker result may enter physics.

Let `z_A,z_B` be cut indicators:

| Arm | `z_A` | `z_B` | Meaning |
|---|---:|---:|---|
| `C00` | 0 | 0 | neither candidate edge cut |
| `C10` | 1 | 0 | edge cut on A support only |
| `C01` | 0 | 1 | edge cut on B support only |
| `C11` | 1 | 1 | identical edge cut on both disjoint supports |

All arms share the serialized environment, boundary, body arrays, clock, probe, passive tracer, horizon, and strict
existing no-new-history continuation (`eta_w=0`). Passive copying of already-present `Mf` onto new mass is not a new
exposure history; any external boundary driver or overwrite of `Mf` is forbidden. A qualifying cut must be a
term-level edge deletion with zero state surgery. Each primary arm needs a code-path sham using the same masks and
branching but retaining the frozen coefficient, so active and sham both have zero instantaneous state disturbance.

Fixed masks are allowed only while the intended body remains wholly inside, the partner/sentinel remain outside,
and the masks stay disjoint. Dynamic masks based on diagnostic tracking would make treatment endogenous and violate
the diagnostic-ID invariant.

## Separate responses and non-symmetrized causal matrix

For every arm retain separate raw responses `Y_A^{ab}` and `Y_B^{ab}`. A defensible primary candidate is integrated
total uptake on each bijectively tracked entity over the frozen horizon. Per-step total uptake, specific uptake, mass,
and a fixed-mask convergence response remain separate raw fields. Post-cut body or geometry changes are mediators and
must not be adjusted away.

Use loss-under-cut signs. For response `r in {A,B}`:

```
D_r<-A = 1/2 * [(Y_r00 - Y_r10) + (Y_r01 - Y_r11)]
D_r<-B = 1/2 * [(Y_r00 - Y_r01) + (Y_r10 - Y_r11)]
I_r    = Y_r00 - Y_r10 - Y_r01 + Y_r11
```

The complete matrix retains row=response and column=cut source:

```
          cut A      cut B
Y_A       D_A<-A     D_A<-B
Y_B       D_B<-A     D_B<-B
```

Never symmetrize A/B. Also retain the four conditional effects for each response:

- `D_r<-A | B intact = Y_r00-Y_r10`;
- `D_r<-A | B cut    = Y_r01-Y_r11`;
- `D_r<-B | A intact = Y_r00-Y_r01`;
- `D_r<-B | A cut    = Y_r10-Y_r11`.

Directional asymmetry is the direct contrast `D_A<-B - D_B<-A`; it may not be inferred from one significant and
one non-significant crossed cell. The original world is the inference unit.

## Competing hypotheses

- **Diagonal access:** diagonal entries exceed a frozen practical margin; crossed entries and interactions meet
  equivalence bounds. If the cut deletes `m_plus -> uptake`, diagonal effects are partly algebraic positive controls,
  not individuality evidence.
- **A-to-B / B-to-A crossed access:** respectively `D_B<-A` or `D_A<-B` exceeds margin after causal-latency,
  confinement, sham, sentinel, fusion, tracker, and viability gates.
- **Reciprocal access:** both crossed entries exceed margin; their equality is tested, never assumed.
- **Global/common-mode:** both response rows move similarly after either cut and sentinel/far-field/global numerical
  diagnostics move at incompatible latency. The 2x2 alone cannot distinguish this from two parallel crossed paths.
- **Relational dependence:** one or both `I_r` exceed an interaction margin while the separate conditional effects
  satisfy the predeclared sufficiency/equivalence rules. Floor/ceiling nonlinearity remains an alternative.
- **Manipulation artefact:** active-sham imbalance, off-support change, unexpected source/sink, support escape,
  fusion/tracker event, or premature global response. No causal interpretation is permitted.
- **Null:** every entry and interaction meets prospective equivalence bounds; non-significance alone is insufficient.

A clean crossed effect is a directed total effect through the shared world, not proof of a direct member-to-member
wire. It may be environmentally mediated. A one-channel cut cannot establish storage location, ownership, identity,
life, or active reconstruction.

## Minimum raw numerical contract

1. Provenance: schema/version, DEV-only mode, code/operator/test hashes, allowed existing IDs, no prospective
   namespace, complete command, platform, and output predecessor chain.
2. Checkpoint: immutable path/file hash, state-content hash, exact step, per-field dtype/shape/hash, serialization
   round-trip equality, and explicit absence of persistent RNG/hidden buffers.
3. Pair: frozen A/B/sentinel indices, outcome-blind selection/orientation, deep-turnover evidence, masks, weighted
   centroids, separation/halo gap, and support hashes.
4. Clone equality: exact per-field and clock errors; common environment/body/boundary/probe hashes.
5. Arm: `C00/C10/C01/C11`, cut booleans, sham identity, coefficient/support hashes, intended and actual changed-term
   support, no-state-surgery hash, and no-write configuration.
6. Per step: state/field hashes; A/B/sentinel masks, sizes, masses, weighted centroids; continuous pair distance and
   halo overlap; every tracker candidate edge and gate term; split/merge/loss/ambiguity; support containment and
   wrong-body intersection; finite/viability flags; field totals; inside/near/far/partner/sentinel disturbance norms;
   causal-cone timing; and active-sham numerical deltas.
7. Responses: raw `Y_A/Y_B` time series in a separately sealed payload. The mechanical validator may hash but may
   not open it. No effect, interaction, classifier, or hypothesis verdict belongs in raw execution code.
8. Disposition: earliest mechanical failure and exact reasons per arm and whole original world. Only complete
   engine-free mechanical validation may release the response payload to a separate analyzer.

## Kill switches

- Missing, mismatched, or non-round-trip-exact serialized checkpoint.
- Any pre-intervention clone byte/clock mismatch.
- `eta_w != 0`, external boundary replay, or any overwrite that adds new history.
- Global scalar ablation, carrier erase/replacement, tracker-controlled mask, multi-field surgery, or any operation
  other than the frozen local edge deletion.
- Overlapping masks, partner/sentinel contact, target escape, arm-dependent masks, or non-compositional `C11` at the
  first update.
- Active/sham state mismatch at intervention or immediate off-support change outside the declared one-step closure.
- Premature far/global disturbance inconsistent with physical causal latency.
- Non-viability, separation failure, halo overlap, fusion, split, merge, loss, ambiguity, or fixed-mask/tracker
  convergence failure in any arm. Invalidity is whole-world; no surviving-subset rescue.
- Opening any response, contrast, interaction, margin, or outcome-bearing diagnostic before all mechanical gates.
- Any prospective seed/namespace or change to `58xxx`, 03G, or V5.

## GO / REVISE / STOP rule

- **GO for human mechanical review only:** exact serialized checkpoints exist; an already-existing local edge cut and
  exact sham pass the complete four-arm DEV mechanics; the raw chain reproduces engine-free; responses stay sealed.
- **REVISE:** only packaging, serialization, or schema implementation remains, without changing the already-qualified
  scientific operator.
- **STOP-LOCAL-CUT:** localization requires a new spatial engine term, global ablation, carrier destruction,
  external replay/writer, or tracker-dependent physics. This is the current result.

## OBSERVED

- Four deep DEV pair candidates exist at worlds/steps `50002/847`, `50004/793`, `50005/831`, and `50007/890`.
- Existing records retain state-content hashes but no exact serialized checkpoint artefacts.
- No existing implementation qualifies as a target-local access-edge cut.

## INFERRED

The factorial and non-symmetrized estimands are coherent, but identification is conditional on an operator that the
repository does not presently contain. The design cannot itself authorize inventing that operator.

## HYPOTHESIS

Were a term-level local cut independently qualified, crossed response cells after physical latency could distinguish
directional pair access from direct diagonal readout, subject to common-mode and relational alternatives.

## WHAT WOULD FALSIFY THIS?

A synthetic must-pass/must-fail suite showing the proposed matrix cannot distinguish the declared hypotheses even
with a perfect local cut; or DEV mechanics showing unavoidable global/off-support changes, support escape, or
tracker dependence for every admissible local implementation.

## Failures and dead ends

- Existing state hashes cannot substitute for serialized checkpoint bytes.
- The broad no-swap collar cannot be rescued by calling its zero-disturbance own replay a disturbance-matched sham.
- A local lambda field or dual driver would be a newly invented operator and is outside this audit.

## Decisions

- Accept `STOP_PAIR_MECHANICS` unchanged and do not reinterpret its worlds or thresholds.
- Preserve a conditional design but issue **STOP-LOCAL-CUT** on current evidence.
- Do not open outcomes, prospective families, or any protected artefact.

## Unresolved risks

- A future mission must freeze whether passive copying of existing `Mf` counts as permitted persistence under the
  strict no-new-history rule.
- Fixed supports can censor motion; dynamic supports can introduce treatment endogeneity.
- Four DEV worlds are mechanical cases only and cannot set margins, power, hard cap, or event probability.

## Handoff

Independent disposition: **STOP-LOCAL-CUT**. Exact next authorized action is human choice whether to open a distinct
operator-development mission for a term-level target-local readout cut and immutable checkpoint serialization.
That would not be execution or continuation of this Phase-0 audit.

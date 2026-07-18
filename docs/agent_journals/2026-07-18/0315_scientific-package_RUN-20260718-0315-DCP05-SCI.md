# Agent journal - DIRECTED-CAUSAL-PAIR-00 Phase 0.5 scientific package audit

- Role: independent estimand, multiplicity, and claim-classification auditor
- Run ID: `RUN-20260718-0315-DCP05-SCI`
- Start time: 2026-07-18 03:15 CEST
- End time: 2026-07-18 03:23 CEST
- Starting Git state: clean isolated worktree on branch
  `codex/directed-causal-pair-00-phase05` at
  `4bcb551092291b7383c4168f653818d4bade14f6`
- Ending Git state: branch HEAD remained
  `4bcb551092291b7383c4168f653818d4bade14f6`; this journal is this role's only change. The shared worktree also
  contained concurrent untracked files created by other roles, which this role did not modify.
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; this is a direct human-requested, read-only scientific-design audit, not a
  scheduled run, and it launches no world or experiment

## Assigned scope

Independently review the Phase-0 report and draft preregistration and specify the scientific portion of an
**unsealed, seedless** prospective candidate for Phase 0.5. The requested focus is:

1. one primary target-specific individuation estimand;
2. distinct directed secondary contrasts;
3. a mutually exclusive claim classifier;
4. operating-characteristic and multiplicity logic without reading or computing scientific pair outcomes;
5. the original world as the sole statistical unit.

Explicit exclusions for this role: no prospective namespace inspection or enumeration, no world execution, no
pair `Y`, `C`, or `I` computation, no equivalence claim, and no edit outside this unique journal.

## Durable context and important files read

Read in the repository-mandated order:

1. `AGENTS.md`;
2. `docs/RESEARCH_CHARTER.md`;
3. `docs/PROJECT_STATE.md`;
4. `docs/DECISION_LOG.md` through D-091;
5. `docs/EXPERIMENT_INDEX.md`;
6. `docs/RUN_INDEX.md`;
7. latest journal
   `docs/agent_journals/2026-07-18/0243_scientific-design_RUN-20260718-0243-DIRECTED-CAUSAL-PAIR-00-P0.md`;
8. current Phase-0 report and manifest-equivalent mechanical summary.

The direct scientific inputs were:

- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_REPORT.md`;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PREREGISTRATION_DRAFT.md`;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_PHASE0_DEV_FEASIBILITY.json`;
- `docs/individuation/DIRECTED_CAUSAL_PAIR_00_RAW_SCHEMA_DRAFT.json`;
- the Phase-0 mission and the Phase-0.5 authorization text supplied by the user.

No raw scientific outcome artefact was opened. No prospective seed identifier was inspected, listed, generated,
or reserved. The only numeric DEV material read was the already-persisted, outcome-blind Phase-0 mechanical
summary.

## OBSERVED

1. Phase 0 already fixes the directed convention correctly: row is recipient and column is writer source.
   Therefore `C_AB` is B-to-A and `C_BA` is A-to-B; these entries must not be symmetrized.
2. The four Phase-0 DEV worlds are mechanical examples only. They cannot estimate a scientific variance,
   covariance, effect size, equivalence margin, power, or prevalence.
3. The Phase-0 draft currently makes `H_I` depend on off-diagonal equivalence to zero and makes `H_0` depend on
   all effects falling inside null/equivalence regions. No independently justified scientific equivalence margin
   exists. Those two formulations therefore cannot enter the Phase-0.5 candidate as claims.
4. The proposed four-arm exact-clone factorial identifies all four directed marginal main effects and two
   recipient-specific interactions within each original world.
5. Targets, arms, access regimes, time steps, and reciprocal directions are repeated observations within one
   original world. Treating any of them as independent would be pseudoreplication.
6. Mechanical eligibility after treatment can itself be affected by a writer arm. Complete-block restriction is
   therefore scientifically non-innocent and must be disclosed, not hidden as ordinary missingness.

## Primary estimand

For original world `w` under ordinary coupling, retain the Phase-0 factorial definitions of
`C_AA,w`, `C_AB,w`, `C_BA,w`, and `C_BB,w`. Define the two reciprocal source-preference components:

```text
D_A,w = C_AA,w - C_BA,w
D_B,w = C_BB,w - C_AB,w
```

The single primary estimand is:

```text
Delta_IND,w = 0.5 * (D_A,w + D_B,w)
            = 0.5 * [(C_AA,w - C_BA,w) + (C_BB,w - C_AB,w)]

Delta_IND = E_w[Delta_IND,w | prospectively eligible complete original world]
```

Interpretation: `Delta_IND > 0` is evidence that a writer's effect is preferentially expressed by its own
recipient rather than the partner, averaged reciprocally across the two directions. It does **not** imply that
either cross effect is zero, that access is exclusively local, that ownership is established, or that the pair
contains metaphysically independent individuals.

`D_A` and `D_B` are reciprocal coherence guards for the primary claim, not extra primary estimands. A future
claim of two-target individuation should require both directions to support the same positive preference; a large
effect in only one direction must not be averaged into a two-individual claim.

The population target needs a precise qualifier. A world is a complete unit only if every essential history and
access arm passes the frozen mechanical gates. If writer-dependent invalidity occurs, the candidate must report
arm-specific invalidity and either return `MANIPULATION_INVALID` or `UNRESOLVED`; it must not silently describe the
surviving complete-block subset as all eligible worlds.

## Distinct directed secondary contrasts

All are computed first within an original world and only then summarized across worlds.

1. Directed entries, always separate:

   ```text
   C_AA, C_AB, C_BA, C_BB
   ```

2. Directed crossed asymmetry:

   ```text
   A_CROSS = C_AB - C_BA
   ```

   No favourable direction may be selected after observation.

3. Recipient-specific H11 interactions:

   ```text
   I_A = Y_A(11) - Y_A(10) - Y_A(01) + Y_A(00)
   I_B = Y_B(11) - Y_B(10) - Y_B(01) + Y_B(00)
   ```

4. Pair-total mean main response:

   ```text
   T_PAIR = 0.25 * (C_AA + C_AB + C_BA + C_BB)
   ```

   This scaling is the average across both writer sources and both recipients. It is not an individuation
   contrast.

5. Recipient-matched no-swap sensitivity, kept entry-specific:

   ```text
   S_NS,ij = C_ij,ORDINARY - C_ij,NOSWAP_RECIPIENT_i
   ```

6. World-global sensitivity, kept entry-specific:

   ```text
   S_G,ij = C_ij,ORDINARY - C_ij,UP_REF_ZERO
   ```

7. `I_A`, `I_B`, `T_PAIR`, all `S_NS,ij`, all `S_G,ij`, own-replay differences, fixed-mask differences, and
   sentinel responses remain separately named. They are never collapsed into a reader, feature battery, or
   composite identity score.

Body, mass, geometry, and halo trajectories are post-writer mediators. Primary and secondary causal effects are
unadjusted total effects. Mediator summaries are descriptive diagnostics and never regression-adjusted away.

## Claim classifier - mutually exclusive candidate

The classifier should operate on a fixed set of predeclared Boolean evidence flags and use the following order.
Its headline label is unique; all supporting flags and estimates remain visible.

### Pre-analysis gates

1. `G_VALID`: all clone, schedule, sham, tracker, fusion, separation, halo, no-swap, finite-state, raw-schema,
   outcome-firewall, hash, and ordered-prefix gates pass. A systematic or family-level failure gives
   `MANIPULATION_INVALID` immediately.
2. `G_INFO`: the frozen minimum number of whole valid original worlds is reached by the frozen hard cap and the
   planned interval/test remains identified. Failure gives `UNRESOLVED`, not a negative effect and not a zero.
3. Failed arms are never encoded as zero, imputed from another arm, replaced by a different pair, or counted as a
   partial world.

### Evidence flags

- `Q_IND`: the one-sided primary `Delta_IND` rule passes **and** both reciprocal coherence guards `D_A` and `D_B`
  pass a predeclared one-sided intersection-union rule. This guard only narrows the primary rejection region; it
  cannot create a claim that the scalar primary did not support.
- `Q_ASYM`: the multiplicity-controlled two-sided `A_CROSS` rule passes.
- `Q_PAIR`: at least one multiplicity-controlled H11 interaction or the predeclared pair-total rule passes.
- `Q_CROSS_ENV`: at least one multiplicity-controlled crossed entry or predeclared recipient/global sensitivity
  rule passes.

### Exclusive mapping

1. `not G_VALID` -> `MANIPULATION_INVALID`.
2. `G_VALID and not G_INFO` -> `UNRESOLVED`.
3. `Q_IND` -> `INDIVIDUATED_CAUSAL_ACCESS`. Secondary flags are reported as modifiers but cannot erase the
   primary target-preference result. The authorized wording is preferential target-specific access, not exclusive
   access or ownership.
4. If `Q_IND` fails and exactly one of the three secondary families fires:
   - `Q_ASYM` only -> `DIRECTED_ASYMMETRY`;
   - `Q_PAIR` only -> `PAIR_LEVEL_ACCESS`;
   - `Q_CROSS_ENV` only -> `CROSSED_OR_ENVIRONMENTAL_ACCESS`.
5. If `Q_IND` fails and more than one secondary family fires -> `UNRESOLVED`, with the supported channel flags
   listed. This avoids choosing an attractive story between non-nested mechanisms.
6. If all inferential flags fail in an otherwise complete, valid analysis ->
   `NO_INDIVIDUATION_ESTABLISHED`.

The final label means only that the corresponding evidence rule was or was not met. In particular,
`NO_INDIVIDUATION_ESTABLISHED` is a procedural failure to establish individuation. It is **never** reworded as no
individuation, no access, zero effect, or equivalence to zero.

## Multiplicity logic

The package can freeze the structure now while leaving numeric allocations unsealed:

1. Reserve `alpha_IND` for the primary individuation family and `alpha_SEC` for the fixed secondary claim family,
   with `alpha_IND + alpha_SEC <= alpha_FWER`. Numeric values require human seal review.
2. Use an intersection-union rule for reciprocal coherence: a two-target `Q_IND` claim requires both `D_A` and
   `D_B` directional guards. Testing each component at `alpha_IND` and requiring both to pass controls the union
   null without a multiplicity reward.
3. Put every elementary contrast capable of creating `Q_ASYM`, `Q_PAIR`, or `Q_CROSS_ENV` into one enumerated
   secondary family before seal. Apply Holm control at `alpha_SEC`. Do not add a contrast after seeing outcomes.
4. Treat other channel, mediator, fixed-mask, sentinel, and contamination outputs as diagnostics with simultaneous
   intervals or clearly descriptive status. They cannot enter a claim rule unless enumerated in the sealed
   secondary family.
5. Do not perform TOST, equivalence, or non-inferiority testing. No practical/equivalence margin is justified in
   this package. Ordinary confidence intervals may show uncertainty around zero without authorizing an absence
   claim.
6. Every resampling unit is one original world. Resampling targets, arms, steps, or matrix entries separately is
   prohibited.

The exact world-level interval/test engine remains unsealed. A transparent candidate is a studentized world-level
mean procedure checked by simulation for coverage under the frozen sample-size and distributional stress grid.
It must not be chosen by whichever method gives the smallest scientific p-value.

## Outcome-free operating characteristics

Before a human seal, implement a synthetic-only operating-characteristic harness. It must not load DEV scientific
outcomes, any prospective artefact, or any seed namespace. It should generate complete world-level factorial
vectors from declared synthetic distributions and evaluate the **whole classifier**, not just primary power.

Required mean-pattern scenarios:

1. global null;
2. reciprocal diagonal preference;
3. diagonal imbalance / one-direction-only preference;
4. symmetric crossed access;
5. directed crossed asymmetry;
6. pair-total response without target preference;
7. H11 interaction without marginal preference;
8. common environmental/global response across recipients;
9. mixed pair plus crossed mechanisms;
10. manipulation-invalid and information-incomplete cases.

Required stress axes:

- standardized effect sizes rather than values estimated from pair outcomes;
- original-world counts and hard-cap attrition grids;
- within-world covariance across recipients and arms, including strong positive and negative correlations;
- heteroskedastic, skewed, and heavy-tailed world effects;
- arm-dependent and arm-independent mechanical attrition;
- sentinel/global contamination patterns;
- exact-null and near-boundary patterns.

Report at minimum:

- global and per-family false-claim rates;
- coverage of the primary and named secondary intervals;
- probability of every mutually exclusive classifier label;
- power for reciprocal target preference;
- false `INDIVIDUATED_CAUSAL_ACCESS` under common/global, cross-only, one-direction-only, and interaction-only
  alternatives;
- `UNRESOLVED` and `MANIPULATION_INVALID` rates;
- sensitivity to covariance, tails, and whole-world attrition.

The final `n_min`, hard cap, alpha allocation, and any positive scientific effect threshold remain unsealed until
an external, pre-outcome justification exists. The four DEV worlds and future mechanical Phase-0.5 records may
qualify mechanics only; they may not calibrate scientific effect sizes, variances, margins, or power.

## INFERRED

1. `Delta_IND` answers the narrow pair question more directly than four unrelated entry-wise tests: it asks
   whether each source preferentially reaches its own recipient, while preserving direction in the component
   evidence.
2. Off-diagonal equivalence is stronger than needed for preferential causal individuation and is currently
   unjustified. Removing it avoids an invalid absence claim without weakening the positive question.
3. A single primary contrast does not justify ignoring asymmetry. The two reciprocal component guards prevent a
   one-sided result from masquerading as evidence for two distinct causal individuals.
4. A mutually exclusive headline label is possible only if mixed secondary mechanisms are either handled by a
   fixed hierarchy or returned as unresolved. Returning mixed non-nested evidence as `UNRESOLVED` is the more
   conservative choice.
5. The original-world complete vector preserves the covariance that makes the reciprocal contrast informative.
   Flattening that vector would inflate information and can reverse uncertainty conclusions.

## HYPOTHESIS

If A and B are distinct directed causal carriers, then both reciprocal source-preference components should be
positive and their average `Delta_IND` should be positive under ordinary coupling. Crossed, global, pair-total,
interaction, or asymmetric patterns may coexist, but they must be reported as separately named channels rather
than being averaged away or treated as proof against individuation.

## WHAT WOULD FALSIFY THIS?

1. Synthetic operating characteristics showing unacceptable false `INDIVIDUATED_CAUSAL_ACCESS` under a common
   environmental response, cross-only response, one-direction-only response, or heavy-tailed null would falsify
   the proposed claim rule.
2. A classifier whose labels depend on target/arm rows as independent samples would fail the original-world-unit
   requirement.
3. Any claim of absent cross access without an independently justified pre-outcome margin would invalidate the
   package.
4. Any Phase-0.5 mechanical record containing pair scientific outcomes, prohibited `Y/C/I` keys, or a prospective
   namespace would breach the outcome firewall and return `MANIPULATION_INVALID`.
5. Systematic writer-arm-dependent validity loss would prevent a clean complete-world causal estimand and require
   revision or stop, not complete-case storytelling.
6. Failure to pre-enumerate every secondary contrast that can alter the classifier would invalidate multiplicity
   control.

## Failures and dead ends

- No scientific outcome analysis was attempted; there was therefore no numerical effect, margin, or power result
  to report.
- The Phase-0 `H_I` off-diagonal-equivalence clause was rejected for the Phase-0.5 candidate because its margin is
  unqualified. It is not silently replaced with a zero threshold.
- A simple precedence rule among asymmetry, pair-level, and environmental claims was considered but rejected as
  scientifically arbitrary for mixed, non-nested evidence. Mixed secondary support is instead `UNRESOLVED` with
  all flags visible.
- A treatment-label randomization test was not recommended: all four deterministic clones are observed and there
  is no randomized treatment assignment that would justify ordinary randomization inference. Sampling inference
  must remain at the original-world level.

## Decisions

Recommended scientific-package status:

**CANDIDATE STRUCTURE ACCEPTABLE FOR AN UNSEALED PACKAGE, CONDITIONAL ON MECHANICAL QUALIFICATION AND SYNTHETIC
OPERATING-CHARACTERISTIC VALIDATION.**

This is not `GO` for a prospective family. It freezes algebra, unit, classifier structure, and multiplicity
architecture only. Numeric error allocation, sample size/hard cap, runtime bindings, any scientific margin, and
prospective authorization remain absent.

## Unresolved risks

- Post-writer complete-block selection may change the target population if validity differs by arm.
- The final interval/test engine and its finite-sample coverage are not yet selected or qualified.
- Pair-total and crossed/environmental mechanisms are not mutually exclusive in nature; the classifier's
  `UNRESOLVED` branch must remain available rather than forcing a narrative.
- No independent scientific scale exists for a practical positive margin or equivalence region.
- Clamp and `up_ref` sensitivity can diagnose channels but cannot by themselves prove exclusive localization.
- A positive `Delta_IND` remains preferential causal access, not ownership or identity in a metaphysical sense.

## Reproducible commands and experiments

Read-only audit commands used standard `git status`, `git rev-parse`, `rg`, and `Get-Content` against the files
listed above. No simulation, world initialization, scientific analyzer, decoder, reader, or prospective runner was
invoked. No experiment command exists for this role because executing one was explicitly forbidden.

Validation to perform after this journal write:

```powershell
git diff --check -- docs/agent_journals/2026-07-18/0315_scientific-package_RUN-20260718-0315-DCP05-SCI.md
git status --short --branch
git rev-parse HEAD
```

## Handoff

The integrator should carry the algebra and claim rules into the unsealed prospective candidate only if the
mechanical qualification completes outcome-blind. In particular:

1. replace off-diagonal-equivalence individuation language with preferential-access `Delta_IND` plus reciprocal
   coherence guards;
2. keep all four directed entries and all named channel contrasts separate;
3. implement the exclusive classifier with `MANIPULATION_INVALID` and `UNRESOLVED` ahead of scientific labels;
4. bind multiplicity to one original-world analysis vector;
5. add a synthetic-only operating-characteristic plan and keep all numeric seal choices blank;
6. retain a seedless manifest template and stop before any prospective namespace action.

No RUN/PROJECT/EXPERIMENT/DECISION index was edited by this role because the parent assignment explicitly limited
the role to this unique journal. The integrator owns durable index updates, commit, and push.

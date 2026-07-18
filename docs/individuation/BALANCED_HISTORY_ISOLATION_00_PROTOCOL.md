# BALANCED-HISTORY-ISOLATION-00 — frozen DEV protocol

**Status:** frozen before opening DEV seed 55001; DEV-only; no prospective execution or preregistration seal authorized.

**Canonical parent:** `6d1a5f718b965d2896f2a3e4d6cbcf5c8c83542f`

**Branch:** `claude/balanced-history-isolation-00-dev`

**Statistical unit:** original world.

This experiment does not reinterpret the stopped `HISTORY-TRANSPORT-00` random-history family. It asks a new,
pre-data question with orthogonal categorical histories: after deep material turnover, can an isolated complete core
causally express cumulative dose, temporal order at exactly matched dose, or both under common history-independent
spatial and global input?

## 1. Pre-implementation semantic gate — PASS

The frozen engine and historical writer establish the following before any new DEV world is run.

1. `a1` and `a2` are amplitudes of a local Gaussian nutrient patch, added to `N` around each eligible target.
2. They act in two distinct, consecutive temporal episodes. `a1` is applied for the first 60 engine steps and `a2`
   for the next 60 engine steps.
3. The episodes have zero intervening gap; the existing post-write settle follows both episodes.
4. Swapping `a1` and `a2` genuinely reverses which amplitude is delivered early versus late. It does not merely
   relabel simultaneous covariates.
5. The historical half-open numerical support is `[0.005, 0.035)`.
6. Every frozen amplitude below is strictly inside that support.
7. The added nutrient can diffuse and can therefore alter other targets, body/geometry, uptake, physical fields,
   and the ordinary world-global `up_ref`. Those post-assignment effects are part of the causal history. They are
   measured as first-stage/validity diagnostics and are not residualized away.
8. Four eligible targets are detected, spatially filtered and fixed before the manifest assignment is applied.

Failure of any of these semantics would have forced `SEMANTIC-FAIL`; no relabeling was needed.

## 2. Frozen histories

| History | `a1` | `a2` | Total | Order |
|---|---:|---:|---:|---|
| `H_L_EARLY` | 0.0175 | 0.0075 | 0.025 | larger exposure early |
| `H_L_LATE` | 0.0075 | 0.0175 | 0.025 | larger exposure late |
| `H_H_EARLY` | 0.0325 | 0.0225 | 0.055 | larger exposure early |
| `H_H_LATE` | 0.0225 | 0.0325 | 0.055 | larger exposure late |

These values and the 60 + 60 step writer are immutable for this family. Mechanical failure before inspection of a
scientific endpoint produces `REVISE-MECHANICS` and human review; it does not permit tuning.

## 3. Eligibility and allocation

At the end of the frozen 800-step warm-up, candidates must have detector size at least 45. Targets are selected in
descending size order and must have pairwise toroidal centroid separation at least 24 cells. Exactly four are
required. Selection is complete before treatment assignment.

The assignment manifest is
`BALANCED_HISTORY_ISOLATION_00_ASSIGNMENT_MANIFEST.json`. For seed `s`, spatial slots 0–3 receive a cyclic Latin
square with rotation `(s - 55001) mod 4`. The only allocation input is the original-world seed. Geometry quality
beyond prior eligibility, survival, memory, uptake and future outcomes are excluded. Each eligible world contains
all four histories; across 24 planned worlds, every history occupies every slot exactly six times.

Before simulation the runner verifies the manifest SHA-256, parent, exact seed list, exact history values, episode
timing, global rule, every seed-to-slot assignment, Latin balance and namespace audit. A mismatch aborts.

## 4. DEV seed family and namespace audit

The complete immutable family is `55001–55024` (24 original worlds). It cannot be extended automatically.
Semantic-integer searches found no member of this range in the working tree, reachable local history, valid local
or origin-tracking heads, the recovered malformed `probe/tmp01` commit tree, or remote-only `origin/main` commit
`a73ed40db96bc4b59f7562ae8f587c9918070f20a`.

The malformed ref is preserved unchanged. Its second line resolves to
`c8a8b354f10e0988adff4264bf0b1fdffcdf19c9`, an empty commit named `probe` with its parent's tree; it contains no
candidate seed. Prior DEV ranges `50001–50010` and `51000–54120` are excluded. No prospective namespace was
inspected or reserved.

## 5. Longitudinal validity and post-treatment selection

Each assigned target is tracked longitudinally through both episodes, settle, turnover and the probe. Diagnostic
particle IDs do not enter physics or association. No largest-component reselection is allowed.

A world is a primary complete block only if:

- four targets were eligible before history assignment;
- all four histories were applied;
- all four tracks remain alive independently through `M <= 0.25` for every target;
- no fusion, fragmentation, identity switch, coverage, geometry or tracker gate fails;
- all four primary arms remain valid through the probe; and
- the own-replay manipulation sham is numerically and state-hash exact.

The runner records first tracker events and condition-specific post-history/deep/probe survival. Failed individual
targets are never retained as independent observations and no feeding outcome is imputed. Fewer than four complete
original worlds gives `DEV-FEASIBILITY-FAIL`.

## 6. Deep intervention and common input

At the first valid all-target deep-turnover time, each complete world is cloned. The complete state inside each
radius-10 core remains untouched.

- `K_COUPLED`: ordinary frozen-engine continuation with the ordinary global `up_ref`.
- `K_COUPLED_G0`: ordinary spatial coupling with validated `up_ref = 0`.
- `K_SHAM_OWN_REPLAY_G0`: qualified two-cell no-swap clamp replaying that world's own future boundary, with
  `up_ref = 0`; it must reproduce `K_COUPLED_G0` exactly.
- `K_ISOLATED`: qualified two-cell no-swap clamp driven by a same-seed, same-time, no-history on-manifold reference
  trajectory, with `up_ref = 0`.

The primary isolated global treatment is the validated history-independent ablation `up_ref = 0`. It is identical
for all histories. `K_COUPLED` preserves the ordinary coupled control; `K_COUPLED_G0` distinguishes spatial
isolation from global-channel removal.

Only one physically defensible history-independent boundary reference existed before outcomes: the same-seed,
same-time no-history on-manifold trajectory. Own replay is a sham, not a second reference. No new boundary reference
may be selected after results, so a two-reference reversal test is not applicable rather than silently passed.

## 7. Frozen probe and outcomes

Every arm first receives `N := N0` uniformly. It then follows the frozen 40-step standardization period and frozen
40-step feeding probe; the existing nutrient stimulus is delivered during the frozen probe window. The primary
target outcome is integrated uptake over all 40 probe steps on the longitudinally tracked mask. Integrated uptake on
the step-40 fixed mask is the tracker-independent convergence control. Earlier and instantaneous outcomes are
diagnostic only.

## 8. Original-world factorial estimands

For each arm `K`, let `Y(h,K)` denote one target's frozen integrated tracked uptake. Contrasts are formed within one
complete original world before any cross-world summary:

`delta_D(K) = 0.5*(Y(H_H_EARLY,K)+Y(H_H_LATE,K)) - 0.5*(Y(H_L_EARLY,K)+Y(H_L_LATE,K))`

`delta_O(K) = 0.5*((Y(H_L_EARLY,K)-Y(H_L_LATE,K)) + (Y(H_H_EARLY,K)-Y(H_H_LATE,K)))`

`delta_DO(K) = (Y(H_H_EARLY,K)-Y(H_H_LATE,K)) - (Y(H_L_EARLY,K)-Y(H_L_LATE,K))`

Primary reports include `delta_D`, `delta_O` and `delta_DO` for `K_ISOLATED` and `K_COUPLED`, plus
`T_D = delta_D(K_ISOLATED)-delta_D(K_COUPLED)` and corresponding `T_O`, `T_DO`. The global-matched secondary
transport contrast subtracts `K_COUPLED_G0` instead.

Targets are paired treatment positions, not replicates. Across-world means, medians, signs and 95% Student-t
confidence intervals use only original-world contrasts. No target-level standard error or pooled regression is
permitted.

## 9. Frozen first stage

Before the probe, and without future uptake, each complete block records:

- mean core `tanh(m1+m2)` (`mplus`) and `tanh(m1-m2)` (`mminus`);
- the previously used 11-dimensional memory summary;
- fixed scalar `Mf` dispersion, channel correlation and roughness summaries;
- a fixed radius-10 two-channel full-field vector, summarized across worlds by leave-one-world-out cosine alignment;
- post-history body size, mass and radius of gyration, with their pre-history counterparts;
- core `rho`, `N`, `c`, `u`, `v`, `sigma`, and delivered patch mass.

The dose positive-control first stage is predeclared positive on core `mplus`. It passes only when at least 75% of
complete original worlds are positive and the 95% world-level t interval lies wholly above zero. The order first
stage is predeclared negative for `EARLY - LATE` on `mminus`: channel 1 forgets rapidly and should follow the later
episode more strongly than channel 2. It passes only when at least 75% are negative and the 95% interval lies wholly
below zero. Full-field order alignment must have positive median leave-one-world-out cosine for a prospective
candidate. Other predefined first-stage quantities are reported, not selected post hoc.

Body/geometry and physical-state contrasts are possible mediators of assigned history. They are not baseline
confounders and are not adjusted away. Their magnitude and orientation are reported alongside feeding; no
`Mf`-specific mediation claim is allowed without an intervention.

## 10. Feeding gates and `lam_plus` control

An isolated dose feeding effect passes when at least 75% of complete-world `delta_D(K_ISOLATED)` values are positive
and its 95% t interval is wholly positive. An order feeding effect has no imposed sign, but requires at least 75% in
one sign, a 95% t interval excluding zero, and the same median sign in coupled and isolated arms.

Two additional arms repeat coupled and isolated probes with `lam_plus = 0`. They are mediation controls, not
validity requirements. Collapse of a history contrast supports expression through the designed `mplus` uptake
readout; persistence suggests another complete-core pathway. Endpoint availability alone is not evidence, and
first-stage storage is not erased by this readout intervention.

## 11. Frozen DEV classification

- Fewer than four complete worlds: `DEV-FEASIBILITY-FAIL`.
- Inexact sham, invalid clamp/global input, tracking or primary arm: `MANIPULATION_INVALID`.
- Failed dose first-stage positive control: `STOP` with `FIRST_STAGE_FAIL`.
- Valid dose state and isolated feeding, but no stable order state: `DOSE_ONLY`.
- Valid order state but no causal isolated order feeding effect: `ORDER_STATE_WITHOUT_FEEDING`.
- Valid dose and order states, both feeding effects under isolation, same qualitative coupled direction and all
  gates passing: `DOSE_AND_ORDER`.
- Valid first stage but neither preregistered feeding contrast survives isolation: `NO_LOCAL_TRANSPORT`.
- Heterogeneous or uncertain remaining pattern: `UNRESOLVED`.
- Reversal across two preexisting defensible references, if two had existed: `REFERENCE_DEPENDENT`.

`PREREG-CANDIDATE-GO` requires semantics and allocation PASS, at least four complete worlds, valid sham/isolation
and global standardization, the expected dose first stage, an interpretable aligned order test, and a prospective
world-level design that does not use confirmation data. The executable gate is deliberately conservative and only
marks a candidate when the DEV result is `DOSE_AND_ORDER` with positive full-field order alignment. It never opens
prospective seeds.

All outcomes are feasibility classifications, not certified claims about individual memory, identity, ownership,
reconstruction, division or heredity.

## 12. Pre-execution kill switches

DEV execution is forbidden unless focused tests establish:

1. exact manifest-to-runtime assignment equality;
2. exact Latin-square balance;
3. allocation independence from outcome-like inputs;
4. four-target spatial eligibility and deterministic slotting;
5. clamp-disabled engine identity;
6. qualified two-cell isolation against external perturbation;
7. uniform nutrient reset and history-independent `up_ref = 0` in the isolated primary;
8. deterministic replay;
9. factorial/world-level aggregation without droplet pseudoreplication;
10. rejection of forbidden or non-frozen namespaces;
11. frozen step-40 integrated endpoint;
12. manifest hash, canonical parent and immutable family checks.

Any failed test aborts before seed 55001. The fixed 24-world family is then run once, resumably, with atomic raw
result writes. No extension, prospective run, sealing, main merge, publication change, or active reconstruction is
authorized.

# Agent journal — DIRECTED-CAUSAL-PAIR-00 Phase 0.5 API/mechanics audit

- Role: read-only API and mechanical-architecture auditor
- Run ID: `RUN-20260718-0315-DCP05-API`
- Start time: 2026-07-18 03:15 CEST
- End time: 2026-07-18 03:24 CEST
- Starting Git state: clean `codex/directed-causal-pair-00-phase05` at
  `4bcb551092291b7383c4168f653818d4bade14f6`
- Ending Git state: HEAD unchanged at the starting commit; this subagent added only this journal. A separate
  concurrently-created scientific-package journal was also untracked in the shared worktree and was not touched.
- Worktree: `C:\Users\tommy\Documents\ising-v3-directed-causal-pair-00-phase0`
- Runtime lock: not applicable; this was a direct human-requested, read-only source audit. No world was initialized or
  executed.

## Assigned scope

Audit the already-accepted turnover, writer, tracker, probe, state-clone, and no-swap APIs. Propose a concrete
implementation architecture for (1) passive per-step pair geometry, (2) exact `H00/H10/H01/H11` scheduling,
(3) pair-context recipient clamp/sham mechanics, and (4) probe-schedule viability with no feeding endpoint. Do not
run worlds, inspect or enumerate a prospective namespace, compute outcomes, or edit anything except this journal.

## Repository/provenance audit

Read in the required order: `AGENTS.md`, `docs/RESEARCH_CHARTER.md`, `docs/PROJECT_STATE.md`, the relevant complete
tail of `docs/DECISION_LOG.md` including D-089 through D-091, `docs/EXPERIMENT_INDEX.md`, `docs/RUN_INDEX.md`, the
latest Phase-0 journal, and the Phase-0 report plus its machine-readable DEV summary. Also read the frozen writer,
corrected probe, tracker, turnover reconstruction/runner, material tracer, state operator, no-swap operator,
no-swap qualification runner, engine, detector, and focused tests listed below.

The accepted Phase-0 result is D-091: four fixed already-open DEV worlds are compositionally plausible, but per-step
geometry, paired clone mechanics, and history-bearing pair-context clamp/sham remain unqualified. The statistical
unit remains the original world. This audit opened no result family and performed no simulation.

## Important files read

- `experiments/individuation/causal_confirm.py`
- `experiments/individuation/nonmerging_confirm.py`
- `experiments/individuation/bijective_tracker.py`
- `experiments/individuation/material_tracer.py`
- `experiments/individuation/turnover_dev_runner.py`
- `experiments/individuation/turnover_dev_diagnostics.py`
- `experiments/individuation/turnover_diag_engine.py`
- `experiments/individuation/access_structure_operators.py`
- `experiments/individuation/access_structure_dev_qualification.py`
- `experiments/individuation/access_structure_noswap_operators.py`
- `experiments/individuation/access_structure_noswap_dev_feasibility.py`
- `edlab/experiments/sc_iom/engine.py`
- `edlab/experiments/sc_mcm/engine.py`
- `edlab/substrates/scaffold/observables.py`
- the existing tracker/no-swap/Phase-0 test modules

## Exact reusable primitives

### Reuse directly

- State and exactness:
  - `IOMState.copy()`;
  - `access_structure_operators.STATE_FIELDS`;
  - `state_sha256`, `serialize_state`, `deserialize_state`, `exact_state_errors`;
  - `partition_state`, `periodic_distance`, and `access_structure_noswap_operators.core_and_collar`.
- Frozen writer contract:
  - `causal_confirm.seed_world`, `pick`, `patch`, `mask`;
  - constants `WARM=800`, `K=3`, `MINSIZE=45`, `SEP=24`, `PHASE=60`, `SETTLE=120`, and the unchanged amplitude
    interval;
  - `causal_confirm.build(causal_confirm.MEM_INTACT)`.
- Frozen dynamics and ablation:
  - `MultiChannelMemoryEngine.step`;
  - `DiagEngine(..., up_ref_zero=True)`;
  - `NoSwapClampEngine` only with a fresh driver per independent branch.
- Tracker/material continuity:
  - `BijectiveTracker` and its frozen `theta`, split, merge, loss, and ambiguity semantics;
  - `material_tracer.seed_tracers`, `assert_no_feed_collision`, and `read_material` for the unchanged H00 deep-step
    rule.
- Clamp primitives:
  - `BoundaryDriver` frame representation and `_read_ring_frame`;
  - `core_and_collar` with radius 10 and barrier width 2.
- Probe constants only:
  - `nonmerging_confirm.N0`, `SETTLE_STD=40`, `STIM_AMP=0.25`, `STIM_DUR=5`, `HORIZON=40`, `COVER_CAP=0.15`, and
    `THETA`.

### Do not call unchanged

- `nonmerging_confirm.measure`: it integrates and returns tracked/fixed uptake, which violates the qualification's
  outcome firewall. Reuse its constants and schedule only.
- `causal_confirm.run_seed` and `nonmerging_confirm.run_seed`: both calculate scientific response structures.
- `turnover_dev_diagnostics.to_S0`: it returns a state after the original three independent histories, not the
  common prewriter checkpoint needed by the four-arm factorial.
- `turnover_dev_diagnostics.run_to`: it has no continuous pair logger and does not expose all association edges.
- `turnover_dev_runner.turnover`: it emits phenotype/uptake fields and chooses a deep step independently for the
  state passed to it. Phase 0.5 needs an H00-only common deep step and then an exact fixed-length run in the other
  arms.
- `access_structure_dev_qualification._simulate`: it seeds one expected target first and then sorts the two largest
  others, so A/B/sentinel identities are not guaranteed to retain the fixed Phase-0 mapping. It also records uptake
  endpoint availability.
- `access_structure_noswap_operators.record_boundary` for probe arms: it advances a free engine with no N reset and
  no five-step stimulus. It is suitable only for unscheduled free continuations. Probe/sham qualification requires
  a schedule-aware recorder.

## Proposed implementation architecture

Use three modules with deliberately narrow responsibilities:

1. `directed_causal_pair_phase05_mechanics.py`: engine-aware but outcome-free dataclasses, pure geometry, passive
   tracker audit, frozen schedule, exact clone/writer scheduler, schedule-aware boundary recording, clamp audit, raw
   validation, and hard kill switches.
2. `directed_causal_pair_phase05_runner.py`: explicit allowlisted DEV world reconstruction and ordered execution.
   It must not glob or walk result directories. It receives the exact four world IDs from a bound manifest.
3. `directed_causal_pair_phase05_reproduce.py`: standard-library only. It reads only the persisted mechanical raw,
   recomputes counts/minima/gates/classification/hash chain, and writes canonical JSON. It must not import `edlab`,
   NumPy, any experiment runner, or any analyzer.

### A. Passive mechanical component and geometry layer

Create a rho-only component-mask extractor using the same periodic four-neighbour labelling and frozen detector
threshold/minimum cells. Do not call `detect()` inside the outcome-firewalled logger: although detection is
physically read-only, `detect()` also computes `specific_uptake` for every entity. A mask-only adapter avoids even
incidental endpoint extraction while preserving the component rule.

Seed the frozen tracker once in exact `[A, B, sentinel]` order from the fixed Phase-0 masks. Never rematch roles by
nearest centroid and never seed from detector ordering. Wrap, but do not alter, `BijectiveTracker.update`:

- copy all pre-update track masks;
- compute and persist every track-to-component overlap edge and the frozen gate values;
- call the existing update exactly once;
- persist status/event, chosen component-mask digest, alternatives, and post-update mask digest;
- use track IDs 0/1/2 only as diagnostic labels; they never enter physics or association scores.

The pure `geometry_from_masks(rho, A_mask, B_mask, sentinel_mask, fixed_collars)` function must hash the state before
and after itself and have no writable alias. It should record:

- rho-weighted periodic centroids and the shortest toroidal A-to-B vector;
- pair distance and `distance - 24`;
- integer-centered radius-10 core masks and radius-12 halo masks;
- discrete core overlap cells, discrete halo overlap cells, and continuous halo gap;
- body fraction inside its own core, body/collar intersection, partner/sentinel intersections with the recipient
  core and collar;
- fixed pair ordering `[A,B]`, fixed original target indices, component-mask digests, track statuses, and finiteness.

The distance gate and discrete halo gate are separate. Rounding a centroid can make the discrete radius-12 supports
overlap even when `distance-24` is slightly positive. Either failure censors the whole original world.

Use the detector's circular centroid logic, not the existing no-swap runner's arithmetic `_center_of(mask)`. The
latter is wrong for a component straddling a periodic boundary and can place a collar near the grid centre.

### B. Exact factorial scheduler

Build and serialize one prewriter checkpoint after exactly 800 warm steps. Derive all four arms by separately
deserializing the same bytes; verify identical content hashes and no shared array memory. Freeze pair assignment,
sentinel, patch arrays, patch hashes, and one already-open outcome-independent DEV amplitude tuple before any arm.
The future prospective tuple remains a seedless manifest input; Phase 0.5 must not inspect a new stream.

The writer loop is one canonical expression in every arm:

```text
N = N + hA * amplitude[phase] * patchA + hB * amplitude[phase] * patchB
```

Execute both terms in fixed A-then-B order for all 120 writer steps, including zero-bit shams. Record the same two
operation records per step in all arms, with bits as the only difference. The Gaussian tails overlap globally, so
changing addition order is not innocuous floating-point work; never loop over "treated targets only".

Track A/B/sentinel continuously through writer, settle, turnover, and probe. Do not re-identify them after the
writer. Append passive material tracers to each arm's post-writer/settle target masks. Let H00 alone determine the
first unchanged deep-turnover step. Run H10/H01/H11 for exactly that many turnover steps and require all three of
their material-retention values to satisfy the unchanged rule at that common step. Never extend a failed arm to its
own convenient deep step.

Create a new engine instance and new tracker per arm. The base engine is stateless, so execution order should not
matter; prove this by replaying the arm order in reverse. Clamp drivers are stateful and are the exception: sharing
one driver or merely calling `reset()` across branches risks order dependence. Construct a fresh `BoundaryDriver`
with immutable/copy-protected frames per branch.

### C. Outcome-free probe schedule

Represent the corrected probe as an immutable event schedule, not a call to `measure`:

1. set `N := N0` once;
2. run 40 settle engine steps;
3. on probe steps 1 through 5, apply uniform `N := N + 0.25` before the engine step;
4. run exactly 40 probe engine steps total.

The viability loop may read rho/component masks, tracker records, state finiteness, state hashes, separation, halo,
collar/core intersections, and schedule-operation digests. It must not sum, integrate, serialize, print, or compare
uptake as a recipient response. The engine necessarily produces the persistent `uptake` array; hashing it and
checking it for finiteness is mechanical state auditing, not endpoint extraction.

### D. Pair-context no-swap and sham

For each history arm and each recipient separately, keep the partner and sentinel in the same physical world.
Build one fixed radius-10 core and `10 < d <= 12` collar at the recipient's periodic deep centroid. Before starting,
and at every scheduled step, fail if recipient body leaves its core, recipient body touches its collar, partner or
sentinel touches the recipient core/collar, any pair halo overlaps, or any tracker event occurs.

Existing `record_boundary` is missing schedule operations. Add a schedule-aware recorder that applies exactly the
same N reset/stimulus events as the recipient run, advances one frozen engine step, then reads the ring frame.
Frames cover the entire 40-step settle plus 40-step probe sequence, not just the 40 probe steps.

- Own-replay sham: record the same history arm's free scheduled continuation, replay it into an exact clone under
  the identical schedule, and require every post-step full-state hash to equal the ordinary continuation. Final-only
  equality is insufficient.
- Reference no-swap: record the matching recipient role in H00 under the same engine flags and schedule, translate
  its ring to the recipient's deep centre, then replay it against H10/H01/H11. This is pair-context reference input:
  H00's partner remains present in the source trajectory.
- Exact isolation: under `up_ref=0`, compare two exact recipient clones using the same fixed driver, perturbing only
  far environment outside recipient, partner, and sentinel protected supports in one clone. Recipient-core fields
  must remain bit-identical at every step while the far perturbation remains nonzero.

Audit each `BoundaryDriver.apply`: step unchanged, all fields outside the declared ring byte-identical pre/post,
only declared fields on the ring writable, frame count and cursor exact, and source/recipient schedule digests equal.
Record pre-overwrite/post-overwrite collar jumps without treating them as outcomes.

Generate separate H00 reference drivers for ordinary and `up_ref=0` engines. Replaying an ordinary-driver frame into
an `up_ref=0` recipient is not a matched channel cut.

## Outcome firewall and resume contract

- Validate the manifest and exact allowlisted world sequence before importing or initializing an engine.
- Refuse duplicates, reordered prefixes, unknown worlds, unbound input hashes, or any path outside a small explicit
  input allowlist. Use no directory glob, recursive walk, or opportunistic resume discovery.
- Never import or call a causal/pair analyzer. Add an AST/import test for this property.
- Recursively reject DEV raw keys for recipient response, integrated/fixed uptake, directed matrix entries,
  interactions, or scientific classifications. Do not ban the physical state field `C` or the persistent field
  `uptake`; ban endpoint/estimand keys precisely.
- Persist one whole world block atomically only after all essential arms finish. Canonicalize JSON with sorted keys,
  compact separators, `allow_nan=False`, and one final newline.
- Bind each world block to the previous block digest, manifest digest, implementation digest, schema version, fixed
  arm order, and complete schedule digest. Resume accepts only the verified ordered prefix and always starts at the
  next expected world.
- The engine-free reproducer validates the chain, recomputes all mechanical gates and summary minima, and must
  generate byte-identical output twice. A failed arm remains failed with its exact reason; it is never encoded as
  zero or omitted.

## Minimal focused tests

1. **Namespace/firewall before engine init:** allowlisted worlds accepted; any other/duplicate/reordered world is
   rejected while a monkeypatched engine constructor remains uncalled. Path-open spying proves only bound inputs
   are read and no glob/walk occurs. AST proves no analyzer import/call. Recursive key scan rejects synthetic
   scientific outcome keys.
2. **Clone isolation:** four deserialized checkpoints have identical hashes, distinct array storage, unchanged
   scheduler phase, and one-arm mutation cannot affect another.
3. **Writer schedule:** exact 120 steps, two operations per step in every arm, identical A/B tuple, fixed addition
   order, H00 byte-identical to a zero-write reference, H10/H01 affect only their declared term, and forward versus
   reverse arm execution yields identical per-arm hashes.
4. **Passive logger:** logging leaves the state hash unchanged; logged and unlogged engine continuations are
   bit-identical; a periodic-boundary component has the correct circular centroid/distance; discrete halo overlap
   and continuous distance gates are independently tested; component-list permutation leaves digest-based raw
   evidence stable.
5. **Tracker audit:** every overlap edge and frozen gate term is persisted; merge, split, loss, ambiguity, and a
   continuous crossing/contact fixture fail closed. The existing crossing test only checks that both IDs remain
   alive; strengthen it to verify chosen component digests. An instantaneous between-frame teleport/swap is not
   identifiable from geometry alone and must not be advertised as detectable. Cadence 1 plus local motion should
   force a physical crossing through separation/contact gates; document this observability premise.
6. **Clamp locality:** `apply` changes only the ring, preserves step, rejects frame/shape mismatch, and fresh drivers
   start at cursor zero. A deliberately shared driver must be rejected or shown to create a different trace.
7. **Scheduled own replay:** under the full reset+settle+probe schedule, ordinary and own-replay states are identical
   at every step for every persistent field. A recorder without stimulus events must fail this test.
8. **Pair context:** synthetic recipient/partner/sentinel masks pass when disjoint and fail on partner intrusion,
   wrong-core/collar intersection, recipient body in collar, halo overlap, contact, or missing sentinel.
9. **Width-2 isolation with partner present:** under `up_ref=0`, a far-environment perturbation remains present while
   recipient-core hashes remain exact; repeat for H00/H10/H01/H11 schedule bits and both recipients using lightweight
   fixtures before full DEV execution.
10. **Probe viability only:** exact 40 settle + 40 probe steps, exactly five uniform additions, identical event
    digest across all arms/regimes, no response accumulator/output key, and nonfinite state fails closed.
11. **Raw/reproducer:** schema rejects NaN, missing/extra/reordered arms, outcome keys, broken hash links, incomplete
    blocks, or a zero-coded failure; two reproductions are byte-identical and the reproducer's imports are
    standard-library only.
12. **Regressions:** existing 03G, tracker, no-swap, clone/serialization, schema, compile, and frozen artefact hash
    checks remain required after implementation.

## OBSERVED

- The frozen base engine is stateless; `BoundaryDriver` is mutable through `_cursor`.
- The existing tracker is geometry-only and fail-closed on merge/split/loss/ambiguity, but its public summary omits
  the complete overlap graph and selected-component provenance needed here.
- `detect()` reads only state, but computes entity-specific uptake as part of its returned entity even if the caller
  wants geometry only.
- The old no-swap own replay is qualified for a free 40-step continuation, not for the corrected reset/settle/probe
  schedule.
- Existing `_simulate` does not preserve fixed A/B/sentinel ordering.
- The frozen Gaussian writer has nonzero tails across the torus, so A/B array-addition order can affect floating
  arithmetic despite the selected cores being far apart.
- The existing no-swap runner's `_center_of(mask)` is an arithmetic centroid and is unsafe for periodic wrapping.

## INFERRED

- The Phase-0.5 mechanics can be implemented without changing physics, writer, probe, tracker thresholds, turnover
  rule, or pair eligibility, but only if orchestration is separated from the existing outcome-producing helpers.
- A full-schedule own-replay source should be bit-exact because it records the post-step collar of an otherwise
  identical scheduled clone and the engine is deterministic. If it is not exact, the correct disposition is a
  mechanical failure, not a subtraction or tolerance.
- Reference clamp isolation is exact only with the global `up_ref` channel removed and a width-2 barrier; ordinary
  reference-clamp runs diagnose access but cannot claim mathematical environmental isolation.

## HYPOTHESIS

An outcome-free composition of exact common clones, the unchanged writer, cadence-1 geometry/tracker evidence, a
schedule-matched width-2 collar driver, and the corrected probe events will qualify mechanically on at least some of
the four fixed DEV worlds without needing threshold or physics changes.

## WHAT WOULD FALSIFY THIS?

- Any arm-order dependence after fresh per-arm state, engine, tracker, and driver construction.
- Any logger-induced state-hash change.
- Any nonzero own-replay versus ordinary difference under the complete scheduled probe.
- Any selected pair crossing the 24-cell gate, overlapping radius-12 halos, contacting/fusing, switching tracker
  identity, losing the sentinel, or intersecting a recipient collar in an essential arm.
- Any inability of the width-2/up-ref-zero clamp to keep the recipient core exact with a present partner.
- Any need to inspect response magnitude, relax a frozen threshold, choose another pair, or open a prospective
  namespace to repair the mechanics.

## Failures/dead ends identified

- Calling `nonmerging_confirm.measure` would be convenient but violates the no-outcome contract.
- Calling `record_boundary` unchanged for probe arms would produce a mismatched sham because its source trajectory
  omits reset/stimulus schedule operations.
- Reusing one `BoundaryDriver` across branches makes results depend on cursor history.
- Relying on nearest-centroid rematching or detector list order can silently change A/B/sentinel roles.
- A synthetic instantaneous teleport/swap cannot be identified by a geometry-only observer. The valid fail-closed
  crossing fixture must include the physically required intermediate separation/contact violation; diagnostic IDs
  must not be added to association to manufacture observability.

## Decisions and unresolved risks

Decision for implementation: compose new outcome-free orchestration around accepted primitives; do not fork or
modify the frozen scientific engine, writer, tracker gates, probe, or turnover threshold.

Unresolved risks for the integration agent to test on DEV:

- whether every H00 reference reaches the unchanged deep rule and every other arm meets it at the same H00 step;
- whether fixed radius-10 cores continue to contain the recipient body throughout the full 80-step probe schedule;
- whether full-schedule own replay remains exact when all persistent fields, including tracer cohorts and uptake,
  are written on the collar;
- whether the chosen pair remains continuously above both the floating separation and discrete halo gates;
- the exact raw volume of per-step association edges and state digests (a storage issue, never a reason to thin the
  required evidence).

## Reproducible audit commands

No experiment or world command was run. Read-only inspection used `Get-Content`, `rg`, `git rev-parse HEAD`, and
`git status --short --branch`. After this journal was created, `git diff --check` was the only validation required
for the subagent-owned change.

## Handoff

Implement the three-module separation above. The most important non-obvious corrections are: mask-only detection,
fixed `[A,B,sentinel]` tracker seeding, schedule-aware collar recording across all 80 probe-schedule steps, a fresh
driver per branch, H00-only deep-time selection, and periodic rather than arithmetic collar centroids. Do not claim
that the current `measure`, `_simulate`, `turnover`, or free-run `record_boundary` helpers already satisfy these
contracts.

Exact next authorized action for this subtask: the integration agent may implement and test the outcome-free
mechanical wrappers on the four fixed already-open DEV worlds. This auditor must not run those worlds.

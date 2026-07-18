# INTERVENTIONAL-INDIVIDUALITY-00 Stage A — independent adversarial review

- Role: independent adversarial reviewer
- Run ID: `RUN-20260718-2154-II00-A-REDTEAM`
- Start: 2026-07-18 21:54 +02:00
- End: 2026-07-18 22:23:25 +02:00
- Starting branch: `codex/interventional-individuality-00-stage-a`
- Starting HEAD: `44d91f0f66473b9f907618556020929656ca862f`
- Starting Git state: primary Stage-A journal untracked; no implementation files yet observed
- Ending HEAD at review handoff: `44d91f0f66473b9f907618556020929656ca862f` (primary agent has not yet
  committed the reviewed package)
- Ending Git state at review handoff: only the twelve authorized Stage-A implementation, test, report, journal,
  and durable-index paths are modified or untracked; no unauthorized path detected
- Assigned scope: derive and audit the anti-manufacture and mechanical kill switches for the minimal lattice-bond Stage-A implementation; inspect implementation, fixtures, qualification claims and evidence read-only; edit only this journal.
- Outcome firewall: no scientific data, result, world, checkpoint, seed, endpoint selection, V5/03G modification, merge, or PR.

## Sources read

- `AGENTS.md`
- `docs/RESEARCH_CHARTER.md`
- `docs/PROJECT_STATE.md`
- `docs/DECISION_LOG.md`
- `docs/EXPERIMENT_INDEX.md`
- `docs/RUN_INDEX.md`
- `docs/agent_journals/2026-07-18/2151_lattice-bond-stage-a_RUN-20260718-2151-II00-A.md`
- `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_PHASE0_REPORT.md`
- `docs/individuation/INTERVENTIONAL_INDIVIDUALITY_00_SPEC.json`
- attached Stage-A mission text

## Assigned review method

1. Derive the kill switches from the accepted design before inspecting implementation output.
2. Inspect only the isolated Stage-A worktree and explicitly relevant files.
3. Run deterministic code-only checks; never open scientific artefacts.
4. Report repairable defects immediately to the primary agent.
5. Return exactly one final disposition: `STAGE_A_QUALIFIED`, `REVISE_MECHANICS`, or `STOP_SUBSTRATE`.

## Pre-implementation kill-switch derivation

### Anti-manufacture

- **Preferred size:** fail if any physics term reads component size, area, perimeter, radius, target support, loop closure, or a detector-derived label, or if a hidden normalization forces a finite object scale. Local finite-range coefficients may set correlation lengths, but this must not be represented as a target size or globally corrected toward one.
- **Tracker influence:** fail if tracker, diagnostic IDs, component assignment, future association, split/merge choice, or an adaptive recentering support enters state updates, bond kinetics, intervention compilation, or fixture acceptance.
- **Threshold-defined membrane class:** fail if a bond threshold or membrane mask enters the equations. Thresholds may be used only by a passive detector, must be declared independently of yield, and cannot turn physics on/off.
- **Static-crystal false positive:** fail if low leakage, high bond conductance, persistence, or detector closure alone qualifies individuality. The inert static shell fixture must remain explicitly non-individual.
- **Conductance circularity:** fail if the same directly manipulated bond/resource conductance is later treated as the primary response or entity-success criterion. Stage A may report it only as a compliance/conservation diagnostic.
- **Autonomy manufactured by intervention:** fail if a cut constructs a reservoir, clamp, autonomous boundary, one-sided destination rule, moving tracker-defined boundary, nonlocal repair, or hidden work. A face gate must modify both endpoint contributions of an existing physical edge and expose missing flux/work without defining an entity.

### Mechanical

- **Antisymmetry:** every transported extensive face quantity must have one canonical oriented ledger entry with equal-and-opposite endpoint updates before explicit sources, sinks, and boundary work. Fail on destination-only arithmetic, duplicated directed updates, unaccounted periodic faces, or a residual outside operation-derived tolerance.
- **Positivity:** admissibility must follow from frozen input-state bounds, a deterministic common-input substep rule, or a symmetric input-derived limiter. Fail on post-update clipping, arm-specific steps, output-selected correction, negative mass/resource, or an unstated occupancy upper-bound violation.
- **Energy/work closure:** bond formation fuel withdrawal, stored bond-energy increase, rupture release/dissipation, local resource reaction, external source/sink, and intervention controller work must close in the declared operation order. Fail on free formation, hidden dissipation, double counting, incorrect sign, or an omitted gate work term.
- **Open identity:** an all-open plan must be exactly byte-identical to ordinary dynamics and should directly delegate where promised. Fail if compiling an open plan changes state bytes, arithmetic order, RNG, logs that are part of serialized state, or physics output.
- **Closed-gate confinement:** a closed face gate may alter only the declared pre-existing face terms. Fail if it overwrites state, changes bond kinetics, blocks unrelated matter/resource channels, adds a reporter, or applies any nonlocal balancing correction.
- **Uniform local law and symmetry:** the same law must act on every face, with translation and the applicable square-lattice rotation/reflection covariance. Fail on coordinate-, target-, component-, or orientation-special cases not required by a declared fixed lattice/boundary condition.
- **Fixture non-tautology:** dissolution, leakage, percolation, split, merge, inert shell, and active-unbounded cases must be hand-built constructions that exercise mechanics without being accepted as scientific entities. Fail if fixture expectations encode a desired scientific phenotype.
- **Endpoint firewall:** Stage A may name only endpoint families (`maintenance`, `recovery`, `internal activity`, `turnover`, `downstream response`). Fail if it freezes, selects, computes, optimizes, or evaluates a scientific downstream behavior, or uses the directly gated face flux/bond term as a primary response.

## Actions and reproducible commands

- Inspected `edlab/substrates/lattice_bond/engine.py`, its public exports, the frozen equation registry, source
  allowlist, and every deterministic fixture in `tests/test_lattice_bond.py`.
- Ran `C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe -m pytest tests/test_lattice_bond.py -q` after
  the coherent implementation and again after hardening: first `20 passed`, then `21 passed`.
- Ran an AST/static scan of the engine for clipping, global normalization, randomness, tracker/entity/component/
  membrane/owner/genome/fitness/response inputs and in-place state writes. No executable hit was found.
- Independently enumerated all `2x2` binary `m/n` corner states with uniform `b in {0,0.5,1}` at the predecessor
  of the analytic timestep bound under matter-limited, resource/bond-limited and combined stress specifications.
  No state-domain, conservation, or work-closure failure occurred.
- Independently enumerated 26,244 deterministic `2x2` ternary `m/n` states with four bond patterns under the
  combined stress specification at the admissible timestep limit. Minima were exactly zero, maxima were at most
  one, and the worst energy residual was `1.7763568394002505e-15`.
- Demonstrated that the first read-only NumPy plan representation could deliberately re-enable its WRITEABLE flag.
  Reported this to the primary agent. The implementation was then hardened to use arrays backed by immutable bytes,
  and the regression fixture proves `setflags(write=True)` fails.
- Challenged the initial nonzero maintenance sink/gross energetic debit as a possible departure from the accepted
  net Phase-0 energy trajectory. Before qualification, the implementation was revised: simultaneous gross on/off
  work is now explicitly internally recycled, external formation fuel is `epsilon_b*[delta b]_+`, and rupture heat
  is `epsilon_b*[-delta b]_+`.

## OBSERVED

- The executable state is exactly `(m,n,b,step)`; the engine exposes no detector, tracker, component, membrane
  class, entity/owner ID, history field, reporter, response, genome, fitness, reproduction, seed, or search path.
- `Psi_xy` and `T_xy` read only endpoint fields on the same physical face. The physics contains no threshold,
  component size, closure, inside/outside, target support, lattice-size parameter, global mean, or normalization.
- Each matter/resource face value is stored once and applied through a divergence, giving equal-and-opposite
  endpoint contributions. The scalar path separately applies the same canonical face float to both endpoints.
- The timestep inequalities are input/parameter derived. The implementation performs no clipping, substep tuning,
  arm-dependent schedule, or output repair. Independent boundary scans support the analytic positivity claim.
- Exact bond relaxation is decomposed into gross formation and gross rupture. Their common amount is logged as
  recycled maintenance work; only the net positive bond-energy change is debited from endpoint resource and only
  the net negative change is logged as heat. Weakening plus dissolution heat reproduces rupture heat.
- Ordinary execution and an explicit all-open face plan have byte-identical state-plus-ledger serialization.
  Binary fixed-face plans compose commutatively and idempotently; hardened coefficient arrays are immutable.
- A closed face multiplies only the two existing transported face terms. It does not change the pre-step state or
  the same-step bond kinetics, and it logs natural, active and missing flux with exact opposite endpoint deltas.
- The test-only `0.8` bond threshold is confined to a local graph-construction helper using binary `b` fixtures.
  It is absent from the engine and does not qualify a membrane or entity.
- The static-shell and active-unbounded fixtures are explicitly non-individual controls. Direct conductance/flux is
  used only as a mechanical diagnostic; no primary behavior is selected.

## INFERRED

- The engine qualifies the existence of a generic, locally addressable, conservative physical face operator. It
  does not show that the ungated dynamics form a boundary, that a boundary is operational, or that any pattern is
  autonomous or individual.
- Closing selected faces can manufacture a barrier by construction. Therefore the hook can support only a future
  existing-edge intervention after an independently formed physical support and separate downstream endpoint are
  frozen; it cannot itself count as evidence of emergent autonomy.
- The local coefficients set interaction and relaxation scales but no preferred object size. A later finite-size
  yield could still be a lattice/correlation-length effect and would require independent size/cadence controls.

## HYPOTHESIS

- The selected architecture can pass Stage A only if the implementation remains a generic conservative local field system whose open/closed intervention hooks operate on existing face terms and whose fixture suite contains explicit non-individual controls.

## WHAT WOULD FALSIFY THIS?

- A proof that exact conservation, positivity, or local composable cuts require a detector-defined membrane, permanent entity label, target size, unmeasured controller, output correction, or material change to Candidate C.

## Failures and dead ends

- The initial use of an owning read-only NumPy array did not provide strict plan immutability; fixed before final
  qualification without changing an equation.
- The first energy draft added an external maintenance sink and debited gross formation. It was rejected during
  pre-audit and replaced with the accepted net fuel/heat trajectory plus a raw internal-recycling ledger.

## Decisions

- **Final disposition: `STAGE_A_QUALIFIED`.** All equations, paired conservation, exact energy/work identities,
  positivity/admissible-timestep obligations, locality, symmetry, open identity, closed-face confinement,
  intervention composition, and endpoint-firewall mechanics passed the admissible focused evidence.
- This is a mechanical code-only qualification for human review. It establishes no natural boundary, operational
  entity, autonomy, individuality, memory, causal access, reproduction, scientific endpoint, or future instrument,
  and it does not authorize Stage B.
- The repository-wide regression run is not admissible Stage-A evidence. It is retained as a transparent
  evidence-firewall deviation because it traversed pre-existing seeded/scientific unit fixtures. The focused
  hand-built suite and independent deterministic lattice stress are sufficient for the mechanical disposition;
  no scientific contrast or inference from the deviation enters the qualification.

## Unresolved risks

- The homogeneous bond law may fail to form useful closed boundaries in any later fresh regime; Stage A does not
  test or predict yield.
- A face cut itself constructs reduced transport and must never be relabeled as observed autonomy.
- The current substrate has periodic external topology only. Its exact ledger closes internal transport and local
  bond fuel/heat; no claim about a separately imposed world boundary or external reservoir is qualified.
- The fixture-only graph threshold is not a scientific detector threshold and cannot be inherited by Stage B.
- The recorded evidence-firewall deviation is a process limitation for human review even though it does not alter
  the engine or the mechanical result.

## Handoff

- Primary agent should preserve this journal unchanged, finalize its own journal, verify the artifact hashes after
  any last edit, commit and push the isolated branch, and stop for human Stage-A review. No Stage B preparation or
  execution is authorized.

## Final exact evidence

- Focused deterministic suite: `21 passed in 0.24s` on the final reviewed files.
- Syntax: `py_compile` passed for both lattice-bond module files.
- JSON: source allowlist, field/equation registry, and qualification report parsed successfully.
- Frozen input hashes: every design/governance and style source matched the allowlist before the authorized durable
  indexes were updated.
- Qualification artifact hashes all matched current files:
  - engine `e027a9c56b773ed077cdfe725951d215b631c54b7080da73e5321ccedb6d9ff6`;
  - test `75ef218d24a6d7b79df0cd50fba131dc64f741ca4124b5fccdd30324fb366e20`;
  - registry `9b071d0b197732bc7a0f2a418e391ebd2d467ead45e8682987330a1390ded3c6`;
  - allowlist `7b884af05b8468b69e9813520e4a8478b079f22a8024103bddbf808ff08e79b5`.
- `git diff --check` passed; the current changed-path inventory contains twelve authorized paths and zero
  unauthorized paths.

**Independent recommendation: `STAGE_A_QUALIFIED` — HUMAN REVIEW ONLY — NO STAGE B.**

## Appended correction — 2026-07-18 22:24:44 +02:00

This section corrects two earlier statements without rewriting the historical audit record:

1. The opening line `Outcome firewall: no ... seed` is too broad as an execution-history statement. The corrected
   statement is: **no scientific seed, world, endpoint, or outcome was admitted to Stage-A qualification evidence or
   inference.** A completed repository-wide regression run and an isolated accepted-parent test reproduction did
   traverse pre-existing seeded/scientific unit fixtures outside the synthetic-only allowlist. That deviation is
   disclosed above and in the qualification package; it contributes no Stage-A evidence.
2. The final changed-file inventory contains **13 authorized file paths**, not 12. Exact re-enumeration with
   `git diff --name-only` plus `git ls-files --others --exclude-standard` found four modified durable indexes and
   nine untracked files: two journals, four individuation artefacts, two lattice-bond module files, and one focused
   test file. The earlier count of 12 came from `git status --short`, which collapses the two untracked module files
   into one directory row. Unauthorized path count remains zero.

These corrections do not change the independent disposition:
**`STAGE_A_QUALIFIED` — HUMAN REVIEW ONLY — NO STAGE B.**

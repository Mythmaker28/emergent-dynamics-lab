# INTERVENTIONAL-INDIVIDUALITY-00 Stage A journal

- **Role:** primary minimal lattice-bond engine implementer and mechanical qualification integrator
- **Run ID:** `RUN-20260718-2151-II00-A`
- **Start time:** 2026-07-18 21:51:45 +02:00
- **End time:** 2026-07-18 22:25 +02:00
- **Starting branch:** `codex/interventional-individuality-00-stage-a`
- **Starting HEAD:** `44d91f0f66473b9f907618556020929656ca862f`
- **Starting Git state:** clean isolated sparse worktree at the accepted Phase-0 design commit
- **Ending Git state:** clean after the intentional Stage-A commit and branch push; exact commit and remote status
  are reported in the user handoff because the commit containing this journal cannot self-record its own hash

## Assigned scope

Implement and mechanically qualify only the minimal Candidate-C lattice-matter engine with a uniform physical
face-bond field. Use deterministic hand-built fixtures only. Freeze exact local equations, conservative matter and
resource face ledgers, finite bond-energy/fuel/heat work accounting, positivity/admissible-timestep rules, and
generic face intervention hooks. Exclude scientific worlds, endpoints, seeds, search, memory/history fields,
organism or membrane classes, identity IDs, genome, fitness, reproduction, V5/03G modification, merge, and PR.

The only allowed final dispositions are `STAGE_A_QUALIFIED`, `REVISE_MECHANICS`, or `STOP_SUBSTRATE`. Even a
qualification authorizes human Stage-A review only.

## Repository boundary

The checked-out folder name is historical, but the package name in `pyproject.toml`, README title, task identity,
and `origin` URL all identify the repository as the generic `emergent-dynamics-lab` repository. No competing
generic repository appeared among the bounded sibling-directory check. The dirty primary checkout was not used for
changes. This isolated worktree was created from exact accepted commit `44d91f0...`; the Windows-incompatible
tracked `results/_tomo_cache` directory is excluded only from sparse materialization.

## Actions

- Audited the generic-repository boundary and created an isolated sparse worktree at the exact accepted Phase-0
  commit without modifying the dirty primary checkout.
- Read the operating contract, durable state, accepted Phase-0 report/spec/allowlist, and latest relevant journal
  before freezing Stage-A mechanics.
- Froze the compact state/domain, uniform local face equations, operation order, analytic timestep bounds, bond
  energy/work interpretation, immutable intervention algebra, and raw ledger before fixtures were evaluated.
- Implemented the engine as the isolated `edlab.substrates.lattice_bond` package. No existing scientific engine or
  substrate equation was changed.
- Implemented 21 deterministic, hand-built tests covering local mechanics, conservation, positivity, symmetries,
  scalar/vector identity, work accounting, intervention composition, and anti-manufacture counterexamples.
- Produced the machine-readable field/equation registry, source allowlist, qualification record, and Stage-A
  report.
- Commissioned an independent adversarial audit whose kill switches were frozen before it inspected code.

## Important files read or changed

- Read: `AGENTS.md`, the six required durable research files, accepted Phase-0 report/spec/allowlist, and the latest
  completed independent review journal.
- Added: `edlab/substrates/lattice_bond/__init__.py`, `edlab/substrates/lattice_bond/engine.py`, and
  `tests/test_lattice_bond.py`.
- Added: the four `INTERVENTIONAL_INDIVIDUALITY_00_STAGE_A_*` report/registry/qualification/allowlist artifacts.
- Added: this journal; the independent reviewer owns the separate `2154_lattice-bond-redteam...` journal.

## Reproducible commands and fixtures

The isolated sparse worktree does not materialize a virtual environment. Validation therefore used the primary
checkout's existing interpreter with `PYTHONPATH` explicitly bound to this worktree:

```powershell
$env:PYTHONPATH = (Get-Location).Path
& 'C:\Users\tommy\Documents\ising v3\.venv\Scripts\python.exe' -m pytest -q tests/test_lattice_bond.py
```

Admissible result: `21 passed`. The suite contains only deterministic, hand-built lattice arrays and initializes no
scientific world or seed.

The red-team independently enumerated 26,244 two-cell-torus states from ternary `m/n` values and four bond patterns
at the combined analytic timestep limit. It observed no domain violation and worst absolute energy residual
`1.78e-15`.

Final static/package validation:

```text
py_compile new module and test: PASS
three Stage-A JSON documents parse: PASS
qualification artifact hashes: PASS
git diff --check: PASS
changed paths outside the explicit authorization list: 0
```

## OBSERVED

- Phase 0 freezes causal roles and algebraic forms but intentionally leaves `Psi_xy`, `T_xy`, `p_n`, the compact
  admissible domain, parameter ranges, and exact numerical operation order for Stage A to freeze before code.
- The new human authorization clarifies that `b` is structural and carries no memory semantics in Stage A, while
  avoiding an architectural prohibition on what later evidence could establish. Stage A contains no history field
  or local-history factor.
- The exact relaxation can have simultaneous gross formation and rupture even when net bond energy changes in only
  one direction. Logging recycled maintenance work preserves the accepted state trajectory and closes both gross
  and external work partitions without inventing a new sink.
- A face intervention necessarily manufactures a barrier. Exact localization and accounting qualify only the
  coefficient hook, not natural autonomy or individuality.
- After the active-kinetics cut fixture was strengthened, the independent reviewer found no binding mechanical or
  anti-manufacture defect and returned `STAGE_A_QUALIFIED — HUMAN REVIEW ONLY — NO STAGE B`.

## INFERRED

The Stage-A engine must remain a generic physical lattice operator whose validity can be tested without detecting
or naming an entity. Boundary-like constructions are synthetic topology fixtures, not candidate scientific worlds.

## HYPOTHESIS

A fixed-face lattice with a single uniform local bond law, antisymmetric transported fluxes, and finite explicit
bond fuel/heat accounting can satisfy the mechanical intervention identities without encoding individuality.

## WHAT WOULD FALSIFY THIS?

If positivity, paired conservation, bond work closure, or a localized face cut requires a component label,
tracker, membrane mask, hidden global correction, or a material change to the accepted architecture, return
`STOP_SUBSTRATE`.

## Failures and dead ends

- The first validation command assumed a local `.venv`; the sparse worktree has none. No file changed. Subsequent
  validation used the pre-existing primary interpreter with an explicit Stage-A `PYTHONPATH`.
- A draft ledger debited simultaneous maintenance as an additional external sink. Pre-fixture review identified
  this as drift from the accepted Phase-0 trajectory; it was removed before qualification. Maintenance is now
  explicitly logged as internally recycled work.
- Early rotation/reflection helper assertions did not transform the sign of an oriented canonical face value.
  Engine state covariance already passed; the fixture transform was corrected to include orientation sign and the
  full symmetry test then passed.
- A repository-wide regression run was launched despite the synthetic-only evidence firewall. It traversed
  pre-existing scientific/seeded unit fixtures and reported `240 passed, 1 failed`; an isolated reproduction of the
  historical motile-polar assertion at the accepted parent was also run. A second full-suite attempt was terminated
  when the independent reviewer identified the scope problem. These are disclosed deviations, supply no Stage-A
  evidence or scientific inference, and motivated no code change outside this new substrate.

## Decisions

- Treat `44d91f0...` and all IsingV3 scientific evidence as read-only design provenance.
- No directly gated flux or bond term may become a scientific response in Stage A.
- Qualification relies exclusively on the focused synthetic lattice suite and independent hand-built stress scan;
  the out-of-scope repository regression is provenance only.

## Unresolved risks

- The intervention hook is an artificial barrier and remains scientifically inadmissible as evidence of autonomy.
- Stage A contains representability fixtures, not an entity detector or a persistence result.
- The evidence-firewall deviation cannot be undone; it is explicitly quarantined from the qualification argument.

## Handoff

Human architectural review only. Do not open Stage B automatically. Any accepted continuation must separately
preregister entity-independent persistence logic and may not treat Stage-A topology fixtures, face cuts, fluxes, or
bond terms as scientific evidence of individuality.

Final disposition: **`STAGE_A_QUALIFIED`** — mechanical code-only qualification for human review. No Stage B.

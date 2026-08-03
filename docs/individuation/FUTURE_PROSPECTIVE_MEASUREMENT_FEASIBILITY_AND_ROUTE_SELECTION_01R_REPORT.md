# FUTURE-PROSPECTIVE-MEASUREMENT-FEASIBILITY-AND-ROUTE-SELECTION-01R — report

## Part I — FROZEN CAPABILITY LEDGER AND EVALUATION PROTOCOL

This part is frozen before any measurement bridge is written and before any route is designed, drafted,
ranked or preferred. It is committed alone. Part II must cite this commit and be argued against it.
Nothing here may be silently revised: a required deviation is a reason to return
`MEASUREMENT_FEASIBILITY_REVISE`, not to edit this section.

**No bridge existed and no route was designed, drafted, ranked or preferred at this commit.** The
capability facts in §3–§6 are derived from source alone, before any route consequence is drawn. Where a
capability fact obviously bears on a route, the consequence is deferred to Part II and marked as
deferred here.

Part I is a **byte-exact prefix** of the final report.

---

### 1. Authority, scope, ancestry

| Role | Object |
|---|---|
| Authorizing branch | `codex/future-prospective-readiness-architecture-01-human-review` |
| Authorizing commit (this branch's parent) | `a735c64dd912dd52c06dd7b890d29e89bdf49b8d` |
| Its parent — sealed Architecture 01 | `02f7405d784deac69dd849baa7ae976c00240940` |
| This branch | `codex/future-prospective-measurement-feasibility-route-selection-01r` |
| `refs/heads/main` at start | `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77` (`HEAD` = `refs/heads/main`) |

The authorizing commit records `HUMAN_REVIEW_ACCEPTED`, acceptance of `ARCHITECTURE_REVISE`, no primary
and no backup route, and authorization of exactly one successor:
`FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R`.

**Scope.** One combined mission: exact source inspection; capability freeze; a measurement bridge with
tests; a prospective `MeasurementSpec`; a fail-closed external-root gate; fresh Route-E and Route-G
designs; symmetric comparison of E, G and F; two independent adversarial reviews; seal.

**Not in scope.** No scientific family, pilot, parameter sweep, scientific seed, outcome analysis or
scientific claim. No modification of the engine or of any accepted module.

### 2. Read ledger — every object read, by exact path

Verified against the authorizing commit `a735c64d`. Every file below was materialised into a closed
clean room under the agent container and verified blob-for-blob against the repository before use; the
Git blob id of each clean-room file equals `git rev-parse a735c64d:<path>` exactly.

| Exact path | Bytes | sha256 |
|---|---|---|
| `pyproject.toml` | 590 | `e187c1a5809a4b2631bd4e9b947a00ae6790b872a970ba625d283e855a5d498c` |
| `edlab/__init__.py` | 362 | `d3a973865ddaf07eebff73155b114ec8c1d441d99f7ed740a173bf6f5e58b5c5` |
| `edlab/specs.py` | 8,366 | `23c152ad33b4542cb9df3c0422186f1001217b2f988638b61830b18e7891fb70` |
| `edlab/state.py` | 1,607 | `2ed986908ff2e6c587344f65de2265d3c85c0153adc2e390f3aa18e184b36d5a` |
| `edlab/substrates/__init__.py` | 30 | `e6d73027f8343100cd9cbdd79d502b640dd753639aeb53831e2bdd748d7260ba` |
| `edlab/substrates/lattice_bond/__init__.py` | 1,907 | `9d3bea5ac70b514b592f71c2c46738dfdaec62e0072e8055a512b2e22ac6d5b0` |
| `edlab/substrates/lattice_bond/engine.py` | 27,439 | `e027a9c56b773ed077cdfe725951d215b631c54b7080da73e5321ccedb6d9ff6` |
| `edlab/substrates/lattice_bond/instrumentation.py` | 43,421 | `65d4185bd9ef212b013d8d30000499f291f043f289e3e7bccbd536f466e810ef` |
| `edlab/substrates/lattice_bond/lifecycle.py` | 46,397 | `3120d820e30f2b7f71a709ba0fe335a732a0dc849473265f506d2c0307d03053` |
| `edlab/substrates/lattice_bond/future_lifecycle_runner.py` | 18,652 | `7691da3583ecd0fa6a84b87ebedceb815815307340c62eddaabb3190f4b33d08` |
| `edlab/substrates/lattice_bond/future_lifecycle_owned_pipeline.py` | 47,716 | `cc617f06f517aba7c890b9efbf069b7994696af243fc5a584220411747cae919` |
| `tests/test_lattice_bond_instrumentation.py` | 28,948 | `f91fd9e7c2bc20f28ad523fa224fd371f70bdc4e62bc2c81b374a412a0ee2abf` |
| `tests/test_future_lifecycle_contract.py` | 37,445 | `b12b34651236c526ea772ce5c15ff5b2ca4054f638340069d0178be37c297126` |
| `tests/test_future_lifecycle_runner_integration.py` | 86,796 | `a982415a6796bd7185ef3afac241d263d50bd98b03cb549136854fffe2dfaa1b` |
| `tests/test_empty_right_nonunit_cadence_tracker_repair.py` | 36,956 | `50918cf0a77f0505e54e42f177de4084281dd2f05257b4e29942b2666615675e` |
| `tests/test_future_lifecycle_owned_pipeline.py` | 80,840 | `063b58bfebd5602fc2b15a420cd2e9ffdbeeda62b1cb5b709847d14076ea67ff` |

Documents read at aggregate level, by exact path under `docs/individuation/`: the five Architecture 01
documents (`..._01_REPORT.md` 165,415 B, `..._01_DECISION.json` 7,731 B, `..._01_ROADMAP.md` 13,660 B,
`..._01_REVIEW_JOURNAL.md` 23,271 B, `..._01_HUMAN_REVIEW.md` 25,556 B); the four owned-pipeline
documents; the runner-stack requalification report, qualification and human review.

**Declared preflight deviation.** Three paths named in the authorizing brief do not exist at
`a735c64d`, verified by exact object resolution and without any listing:

- `edlab/engine.py` — **absent**. The engine is `edlab/substrates/lattice_bond/engine.py`.
- `edlab/substrates/lattice_bond/specs.py` — **absent**. `LatticeBondSpec` is defined inside
  `engine.py`; the separate spec module is `edlab/specs.py`.
- `edlab/substrates/lattice_bond/state.py` — **absent**. `LatticeBondState` is defined inside
  `engine.py`; the separate state module is `edlab/state.py`.

The substituted paths qualify under the firewall's direct-dependency rule: each appears literally in an
already authorized import (`from .engine import LatticeBondSpec, LatticeBondState, StepLedger` in
`instrumentation.py`; `edlab/__init__.py` and `edlab/substrates/__init__.py` are the package
initialisers on the import path), each is predeclared here, and each was accessed directly without any
directory listing.

**Not read:** any historical scientific runner, Stage-B source, shard, shard name, manifest, world,
trajectory, candidate, checkpoint, autopsy input, result directory, historical or prospective
scientific namespace, Kovacs material, or global index. No broad repository search, no project-memory
search, no listing, glob, wildcard, `git status`, recursive tree listing, `find`, `rg --files` or
archive-on-tree was used at any point.

### 3. Engine capability ledger (frozen — derived from source)

**3.1 Construction and execution.**

| Item | Fact |
|---|---|
| Engine class | `LatticeBondEngine(spec: LatticeBondSpec \| None = None)` — a single optional spec; no other constructor input |
| State | `LatticeBondState(m, n, b, step=0)`: `m` cells `(H,W)` float64 in `[0, m_max]`; `n` cells `(H,W)` float64 in `[0, n_max]`; `b` faces `(2,H,W)` float64 in `[0,1]`; `step` a non-negative integer |
| Minimum lattice | `min(m.shape) >= 2`, enforced by `LatticeBondState.validate` |
| Step API | `engine.step(state, intervention=None, *, backend="vectorized") -> StepResult(state, ledger)` |
| Backends | `"vectorized"` and `"reference"`, two independent implementations of the same update — a built-in differential oracle |
| Mutation | **None.** `step` builds `m_next`, `n_next` and `terms.bond_next.copy()` and returns a new state. Input arrays are never written. `state.copy()` and `LatticeBondState.canonical_bytes()` exist |
| Observation without mutation | `engine.face_terms(state, backend=...)` returns all face quantities and mutates nothing |
| Frame/time semantics | `step` increments `state.step` by exactly **1** per call. `spec.dt` is the physical timestep. There is no wall clock anywhere in the engine |
| Sampled-frame labels | Come from `state.step`, a deterministic integer counter produced by the engine itself — **not** from a caller declaration |
| Randomness | **The engine contains no random number generator and no seed parameter.** `LatticeBondSpec` has no seed field. The update is a pure deterministic function of `(spec, state, intervention, backend)`. All stochasticity a design may want must enter through the caller-constructed initial state |
| Admissibility | `LatticeBondSpec.__post_init__` raises `AdmissibilityError` if `dt > admissible_dt_limit`; `state.validate(spec)` raises on shape, dtype, finiteness or range violation; `step` raises `ArithmeticError` if the declared bounds are violated at runtime |

**3.2 The intervention hook — present, executable, local.**

`FaceIntervention(matter_scale, resource_scale)` holds two immutable `(2,H,W)` coefficient arrays in
`[0,1]`, one per transported term, one coefficient per **individual face** `(axis, y, x)`.

- `FaceIntervention.open(shape)` — the identity plan (all ones).
- `FaceIntervention.from_cuts(shape, matter_faces=..., resource_faces=...)` — set named faces to zero.
- `compose(other)` — elementwise product; the plans form a commutative monoid under composition with
  `open` as identity.
- Immutability is enforced through a read-only buffer, not merely a flag.
- `engine.step` applies `matter_active = matter_natural * matter_scale`,
  `resource_active = resource_natural * resource_scale`, and records in the ledger both the applied
  scales and the **counterfactual** withheld flux: `matter_missing`, `resource_missing`, and their
  signed endpoint deltas `matter_missing_from_delta`, `matter_missing_to_delta`,
  `resource_missing_from_delta`, `resource_missing_to_delta`.

This is a real, executable, spatially local, composable intervention algebra with an explicit
counterfactual record. **Architecture 01 stated that no intervention algebra existed. That statement
was wrong**, and it is corrected here as a capability fact. The route consequence is deferred to
Part II.

**3.3 Per-step ledger channels (`StepLedger`, all `(2,H,W)` face arrays unless noted).**

`affinity` (cells), `matter_forward`, `matter_reverse`, `matter_natural`, `matter_active`,
`matter_missing`, `resource_permeability`, `resource_natural`, `resource_active`, `resource_missing`,
`bond_cue`, `bond_tension`, `r_on`, `r_off`, `gross_formation`, `gross_rupture`,
`gross_formation_work`, `gross_rupture_release`, `gross_weakening_release`,
`gross_dissolution_release`, `maintenance_recycled_work`, `formation_fuel`, `rupture_heat`,
`weakening_heat`, `dissolution_heat`, the four `*_missing_*_delta` arrays, `matter_scale`,
`resource_scale`; and the scalars `initial_matter`, `final_matter`, `matter_residual`,
`initial_stored_energy`, `final_stored_energy`, `total_rupture_heat`,
`total_maintenance_recycled_work`, `energy_residual`, `controller_onset_energy_jump`.
`StepLedger.canonical_bytes()` serialises all of it deterministically.

**3.4 Two derived structural facts, proved from source.**

**(a) The matter flux is an exact discrete gradient flow.** From
`matter_natural[axis] = κ_m (1-b) [ m (1 - m₊/m_max) e^{(a₊-a)/2} - m₊ (1 - m/m_max) e^{(a-a₊)/2} ]`,
factor `C = (1 - m/m_max)(1 - m₊/m_max)` out of both terms and write `g = m / (1 - m/m_max)`:

> `matter_natural = M · (χ - χ₊)` with `M = κ_m (1-b) C e^{(a+a₊)/2} ≥ 0` and `χ = g · e^{-a}`.

The mobility `M` is non-negative for every admissible state, and the driving term is the difference of
a **scalar cell potential** `χ`. There is no transverse, rotational, or chirality-carrying term
anywhere in the update: matter transport is relaxational along `χ`, resource transport is Fickian along
`n`, and the bond field relaxes exponentially toward the local `r_on/(r_on+r_off)` ratio.

**(b) Aggregation is intrinsic.** `χ = [m/(1-m/m_max)] e^{-a}` and the affinity
`a = θ_m · ¼Σ_neighbours m + θ_n · n` increases with the neighbourhood matter, so `χ` *decreases* with
local crowding at fixed `m`. Matter therefore flows toward dense neighbourhoods. Bond formation
`r_on = k_on (m/m_max)(m₊/m_max) min(n,n₊)/n_max` is largest exactly where matter is dense on both
sides of a face, and forming a bond multiplies the matter conductance by `(1-b)`. **Persistence and
material turnover are therefore coupled by construction and in opposite directions**: the bond field
that stabilises a dense region is the same field that suppresses the gross flux that would renew its
material. The route consequence is deferred to Part II.

### 4. `LatticeBondSpec` — every field, from source

| Field | Type | Default | Source validation | Syntactic domain | Prospective range justifiable without historical outcomes? |
|---|---|---|---|---|---|
| `dt` | float | 0.05 | finite, `> 0`, and `<= admissible_dt_limit` | `(0, admissible_dt_limit]` | **Yes** — the limit is analytic |
| `m_max` | float | 1.0 | finite, `> 0` | `(0, ∞)` | **Scale only** (see §4.2) |
| `n_max` | float | 1.0 | finite, `> 0` | `(0, ∞)` | **Scale only** |
| `kappa_m` | float | 0.05 | finite, `>= 0` | `[0, ∞)` | **Yes**, through `κ̂` (§4.2) |
| `theta_m` | float | 0.5 | finite, `>= 0` | `[0, ∞)` | **Only with a declared resolvability principle** |
| `theta_n` | float | 0.5 | finite, `>= 0` | `[0, ∞)` | **Only with a declared resolvability principle** |
| `resource_diffusivity` | float | 0.10 | finite, `>= 0` | `[0, ∞)` | **Yes**, through `D̂` |
| `resource_leak_floor` | float | 0.05 | finite, `∈ [0,1]` | `[0,1]` | **Yes** — closed in source |
| `epsilon_b` | float | 0.25 | finite, `>= 0` | `[0, ∞)` | **Yes**, through `ε̂_b` |
| `k_on` | float | 0.30 | finite, `>= 0` | `[0, ∞)` | **Yes**, through `k̂_on` |
| `k_off` | float | 0.05 | finite, `>= 0` | `[0, ∞)` | **Only with a declared resolvability principle** |
| `k_tension` | float | 0.15 | finite, `>= 0` | `[0, ∞)` | **Only with a declared resolvability principle** |

Derived properties, all analytic and all in source: `affinity_span = θ_m·m_max + θ_n·n_max`;
`matter_dt_bound = 1/(4 κ_m e^{affinity_span/2})` (∞ if `κ_m = 0`);
`resource_bond_dt_bound = 1/(4 D + 2 ε_b k_on / n_max)` (∞ if that rate is 0);
`analytic_dt_bound = min(...)`; `admissible_dt_limit = nextafter(analytic_dt_bound, 0)`.

**4.1 There is no lattice size, component size, contour, target, identity or tracker parameter in
`LatticeBondSpec`.** The lattice shape is a property of the caller-constructed state, not of the law.

**4.2 Dimensionless reduction (frozen).** `m_max`, `n_max` and `dt` are pure scales. Substituting
`m̂ = m/m_max`, `n̂ = n/n_max` and measuring rates per step, the update depends on the law **only**
through nine dimensionless groups:

> `κ̂ = κ_m·dt`  ·  `θ̂_m = θ_m·m_max`  ·  `θ̂_n = θ_n·n_max`  ·  `D̂ = D·dt`  ·
> `λ = resource_leak_floor`  ·  `ε̂_b = ε_b/n_max`  ·  `k̂_on = k_on·dt`  ·  `k̂_off = k_off·dt`  ·
> `k̂_tens = k_tension·dt`

and the two source bounds become, exactly:

> **(B1)** `κ̂ < ¼ · e^{-(θ̂_m + θ̂_n)/2}`   **(B2)** `4·D̂ + 2·ε̂_b·k̂_on < 1`   **(B3)** `λ ∈ [0,1]`

**B1–B3 are hard, finite, source-derived constraints.** `κ̂`, `D̂`, `ε̂_b·k̂_on` and `λ` are therefore
bounded above by source alone. `θ̂_m`, `θ̂_n`, `k̂_off` and `k̂_tens` are **not** bounded above by any
source constraint. Whether an admissible finite frame can nevertheless be declared for those four, and
on what principle, is a Part II question and is not prejudged here.

### 5. Channel availability (frozen)

Classification: **D** = directly available from engine output; **X** = deterministically derivable
from engine output by a declared pure function; **U** = unavailable without modifying an accepted
source.

| Channel | Class | Exact provenance |
|---|---|---|
| Float-valued matter | **D** | `state.m`, `(H,W)` float64 |
| Float-valued resource | **D** | `state.n` |
| Bond field | **D** | `state.b`, `(2,H,W)` float64 |
| Raw mask | **X** | `state.m >= DetectorSpec.matter_threshold` — the identical expression `detect_components` evaluates |
| Gross one-way matter flux | **D** | `ledger.matter_forward`, `ledger.matter_reverse` |
| Applied vs withheld flux | **D** | `matter_active`, `matter_missing`, `resource_active`, `resource_missing` and the four signed deltas |
| Cohort / particle identity | **X** | `advance_passive_tracer(tracer, pre_matter, matter_forward, matter_reverse, post_matter, dt)`, integrated **per engine step**; the tracer array is caller-owned |
| Component mass | **X** | `DetectedComponent.mass` on a state carrying the true float `m` |
| Area, centroid, pixel support, radius of gyration, wrap flags | **X** | `DetectedComponent.area`, `.centroid_y/.centroid_x`, `.cells`, `.radius_gyration`, `.wraps_y/.wraps_x` |
| Component energetic/flux diagnostics | **X** | `component_diagnostics(component, state, ledger, spec)` → `matter_internal_gross`, `matter_in_gross`, `matter_out_gross`, `resource_boundary_exchange`, `bond_work_throughput`, `mean_internal_bond`, `boundary_face_count` |
| Local intervention target | **D** | `FaceIntervention` per face `(axis, y, x)`; composable; counterfactual recorded |
| Shared-environment control | **X** | identical initial `n` field and identical law across co-housed regions; equalisation by construction of the initial state |
| **Signed internal state variable** | **U** | `m ≥ 0`, `n ≥ 0`, `b ∈ [0,1]`. **No field of the engine state takes both signs.** |
| **Symmetry partner of a signed observable** | **U** | Every signed derived quantity (`matter_natural`, `resource_natural`, the `*_delta` arrays) is antisymmetric under **endpoint exchange**, i.e. its sign encodes a direction in space, not a two-valued internal convention. By §3.4(a) the matter flux is `M·(χ−χ₊)` with `M ≥ 0`, so its sign is fixed pointwise by a scalar potential difference and cannot be spontaneously selected independently of the configuration |
| Transverse / orbital / chirality term | **U in this substrate** | `edlab/specs.py` defines `OrbitalSpec.orbital_strength` — explicitly "signed = chirality" — but that belongs to the **CORE V0 particle substrate** (`ParticleState`: positions, velocities, types, ids), for which no accepted detector, tracker, lifecycle contract or owned pipeline exists |

The route consequences of the three **U** rows are deferred to Part II. They are recorded here as
source facts because Phase 1 requires the capability surface to be frozen before any route is proposed.

### 6. Outcome- and eligibility-determining constants (frozen inventory)

Every constant below is compared against an observable and therefore participates in the primary
outcome. Each must appear in the prospective `MeasurementSpec`. **No constant may be introduced that
does not exist in source, and no parameter may be attributed to an API that does not expose it.**

| Constant | Value | Defined in | Caller-configurable | Scientific role |
|---|---|---|---|---|
| `DetectorSpec.matter_threshold` | `0.45` | `instrumentation.py` | yes (dataclass field) | decides cell occupancy, hence component existence |
| `DetectorSpec.min_cells` | `3` | `instrumentation.py` | yes | discards components below the size floor |
| `TrackerSpec.max_centroid_displacement` | `3.0` | `instrumentation.py` | yes | association score scale and qualification |
| `TrackerSpec.max_area_ratio` | `3.0` | `instrumentation.py` | yes | disqualifies association above this area ratio |
| `TrackerSpec.dilation_radius` | `1` | `instrumentation.py` | yes | dilated-IoU term of the association score |
| `TrackerSpec.unique_score_margin` | `1e-12` | `instrumentation.py` | yes | decides `TRACKING_UNRESOLVED`, hence `UNRESOLVED_HANDOFF` |
| `_FRAME_MATERIALIZATION["present_matter"]` | `0.8` | `future_lifecycle_owned_pipeline.py` | **no** — module-private | matter value written for a `True` mask cell |
| `_FRAME_MATERIALIZATION["absent_matter"]` | `0.1` | `future_lifecycle_owned_pipeline.py` | **no** | matter value written for a `False` mask cell |
| `_FRAME_MATERIALIZATION["resource"]` | `0.8` | `future_lifecycle_owned_pipeline.py` | **no** | resource field of the inert materialised state |
| `_FRAME_MATERIALIZATION["momentum"]` | `0.0` | `future_lifecycle_owned_pipeline.py` | **no** | third-field value of the inert materialised state |
| engine runtime tolerance | `1e-12 + 1e-10·max(m_max, n_max, 1)` | `engine.py` `step` | no | bound-violation guard, not an outcome criterion |
| tracer conservation tolerance | `1e-12 + 1e-10·max(1, max\|pre\|, max\|post\|)` | `instrumentation.py` | no | advection consistency assertion, **not** a turnover criterion |

**6.1 There is no `ε` parameter.** `advance_passive_tracer` exposes no tolerance argument, and its
internal tolerance is a conservation assertion on the advection step, not a criterion for material
replacement. Architecture 01's `ε` was an invented parameter; it is not reintroduced here under any
name. Any completion criterion a route needs must be defined explicitly in the `MeasurementSpec` as a
declared measurement convention with its own sensitivity set, never attributed to the tracer API.

**6.2 Exact mask cross-binding, proved from source.** The owned pipeline materialises a `True` cell as
`m = 0.8` and a `False` cell as `m = 0.1`, and `detect_components` occupies a cell iff
`m >= matter_threshold`. Therefore, for **any** `matter_threshold ∈ (0.1, 0.8]`, the pipeline's
re-derived occupancy is **bit-identical** to the mask it was handed. The default `0.45` lies strictly
inside that interval. This makes float→mask→pipeline cross-binding exact and independently checkable
rather than assumed, and it is the mechanism the bridge must exercise.

**6.3 Provenance status.** None of the six `DetectorSpec`/`TrackerSpec` defaults carries an independent
justification in source. Under the acceptance criteria of §7 each must therefore be treated as a
**declared measurement convention**: justified mechanically or geometrically, frozen in the
`MeasurementSpec`, and accompanied by a prospective sensitivity set fixed before any scientific data
exist. A value chosen because it is the library default is **not** justified.

### 7. Measurement acceptance criteria (frozen)

A measurement bridge is acceptable only if all of the following hold. These are pass/fail.

- **M-A1 — Produced, never accepted.** Every bound channel is computed by the bridge from engine
  output. No caller-supplied measurement document, digest, frame, morphology record or receipt may
  substitute for bridge execution.
- **M-A2 — Exact cross-binding.** The boolean mask handed to the owned pipeline is derived by the
  bridge from the exact float snapshot it binds, by the identical expression the detector evaluates,
  and this is demonstrated mechanically, not asserted.
- **M-A3 — Schedule identity.** Sampled-frame labels bound by the bridge equal `state.step` at
  acquisition, equal the labels passed to the owned pipeline, and equal the labels the pipeline
  re-reads. Frame counts match.
- **M-A4 — Root nesting.** The measurement root binds the owned-pipeline run root, and the
  owned-pipeline root binds the exact import/source set. Morphology-dependent evidence is inside the
  measurement root even though lifecycle semantics never consume morphology.
- **M-A5 — Declared unavailability.** A channel the engine does not contain is recorded as
  `unavailable`, with its reason. Synthesising a scientific quantity the engine does not produce is
  prohibited.
- **M-A6 — Distinctions preserved.** Zero detection remains distinguishable from zero acquisition;
  disappearance remains a counted outcome; split, merge, lost and unresolved handoff remain
  representable and are never exclusions.
- **M-A7 — Fail-closed anchoring.** Analysis access is refused unless a verifiable receipt binding the
  exact measurement-root digest is present. Absent, mismatched, or forged receipts all refuse.
  Publication authentication and public verification are separated: a credential may be required to
  publish; no secret may be required to verify.
- **M-A8 — Tamper detection is semantic.** Every mandatory mutant must be killed by a check that
  reasons about the evidence, not merely by a digest mismatch. Hash-only tripwires do not count.
- **M-A9 — Full coverage.** 100% statement and branch coverage of the new bridge module, with every
  accepted module's test suite still passing unchanged.

### 8. Route-independent fatal gates (frozen)

One common table for E, G and F. **No weighted average. One fatal gate failure rejects a route.**

| # | Gate | Requirement |
|---|---|---|
| **N1** | Executable measurement | Every quantity the route's endpoints need is **D** or **X** in §5, and is bound by the qualified bridge |
| **N2** | Independently justified parameter frame | Every law-space bound and every measurement constant has a justification from source invariants, numerical stability, symmetry, or a declared outcome-independent design principle |
| **N3** | Explicit estimand | One primary estimand with population, unit, condition, outcome, intercurrent-event strategy and summary measure |
| **N4** | Exact denominator | The enrolled denominator and the instant that fixes it are declared before any run |
| **N5** | No replacement | No enrolled unit is ever replaced, retried, re-seeded or topped up |
| **N6** | Informative both ways | Positive and negative conclusions are both expressible and both evidentially meaningful |
| **N7** | MDE and power | A numeric decision rule, an independently justified detectable effect or precision target, and adequate operating characteristics **in both arms**, evaluated under the design's own attrition |
| **N8** | Edge-event accounting | Split, merge, lost, disappearance, unresolved handoff and mechanical ineligibility each have a declared non-excluding treatment |
| **N9** | No closed-family tuning | No threshold, bound, prior, sample size or effect size derived from Stage B, from `11/64`, from `0/8`, or from `M_MINUS` |
| **N10** | No manufactured entity or convention | No geometry, initial condition, intervention or observable chosen because it produces the desired answer |
| **N11** | Independent reproduction | A separately authorised reproduction stage with a numeric criterion and its own power |
| **N12** | External-root gating | Analysis is impossible before a verified anchor receipt; the mechanism fails closed |
| **N13** | OP-L3 handling | Every morphology-dependent endpoint is inside the externally anchored root |
| **N14** | Bounded resources | A hard run-count and wall-clock ceiling and an outcome-independent termination rule |
| **N15** | Exact claim ceiling | The highest claim complete success would license, plus at least one thing it would not establish |

**Symmetric standard.** N1–N15 are applied identically to E, G and F. A capability that is deferrable
for one route is deferrable for the other; a capability that is fatal for one is fatal for the other.
This rule exists because Architecture 01's decisive defect was an asymmetric deferral standard.

### 9. Mechanical-test boundary (frozen)

At most **one** minimal deterministic engine compatibility test, and only if static inspection cannot
establish the interface. Conditions: executed under `/tmp`; a handcrafted minimal specification; no
historical input; no prospective namespace; no result directory; no parameter sweep; the minimum number
of steps needed to establish type, shape, timing and channel availability; **only interface facts
recorded, never physical outcomes**; temporary output deleted where possible.

The engine has **no seed parameter** (§3.1), so no scientific seed can be created by such a test. If a
caller-supplied initial state is needed it is handcrafted and constant, is labelled
`MECHANICAL_ONLY__NOT_FOR_SCIENTIFIC_USE`, and is prohibited from any later scientific family.

**This is an API test. It is never feasibility evidence, never a pilot, and never an outcome.** Any
statement in Part II that interprets a number produced by such a test as a physical result is a defect
by construction.

### 10. Route-selection rule (frozen)

1. Apply N1–N15 to each route. Record every failure with the gate and the reason. **One fatal failure
   rejects.** Gates are never averaged, weighted, scored or traded.
2. Among admissible routes, prefer the one with the **greater expected information about entity-local
   individuality per bounded run** — not the more spectacular narrative, not the newer idea, not the
   operator's stated interest.
3. `PROSPECTIVE_ROUTE_SELECTED` names exactly one primary route and at most one backup. A backup must
   pass all fifteen gates independently; a conditioned backup is not permitted.
4. **Route F is not a residue.** It is selected only if neither E nor G can be made prospectively
   interpretable, the missing capability is not repairable by a bounded, scientifically neutral change,
   and consolidation has higher expected epistemic value than the best admissible bounded family.
   Difficulty, expense, or another incomplete architecture is insufficient.
5. If no route passes and F's affirmative case is not established, the disposition is
   `MEASUREMENT_FEASIBILITY_REVISE` naming exactly **one** minimal successor authority.
6. `PROSPECTIVE_ROUTE_SELECTED` additionally requires PASS from both independent reviewers on the same
   final package.

### 11. Reviewer rules (frozen)

- **Reviewer A — engine, measurement and provenance.** Verify every claimed channel against source;
  attack float/mask/morphology cross-binding; attack constant provenance; attack anchor fail-closed
  behaviour; attack the bridge threat model; detect any scientific interpretation of mechanical smoke
  data.
- **Reviewer B — route selection and statistics.** Attack fresh-law-frame independence; search for
  hidden Stage-B tuning; recompute every power and MDE result; attack Route-E denominators and negative
  decisions; attack Route-G symmetry, equivalence, intervention and ownership claims; enforce the same
  deferral standard for E and G; challenge any selection of F.
- Either may return FAIL. Findings are applied **additively**; a claim shown false is **withdrawn**,
  not reworded, with the original text left standing. Both must PASS the same final package for
  `PROSPECTIVE_ROUTE_SELECTED`. If no route passes, the disposition is `MEASUREMENT_FEASIBILITY_REVISE`
  or `STOP_PROSPECTIVE_READINESS`, argued honestly. The journal records every finding, including any
  judged invalid, with the exact package digest each verdict was issued against.

### 12. Evidence firewall (frozen)

**Newly authorized:** exact source inspection of `edlab/substrates/lattice_bond/engine.py`, the exact
directly required engine/spec/state modules, the accepted generic tracker/lifecycle/owned-pipeline
modules, and the exact accepted architecture and human-review records — each by exact path, each
predeclared in §2.

**Still forbidden:** historical scientific runners; Stage-B source; shards or shard names; manifests;
worlds; trajectories; candidates; checkpoints; autopsy inputs; result directories; historical or
prospective scientific namespaces; Kovacs material; global indexes; broad repository searches;
project-memory searches. No directory listing, glob, wildcard, `git status`, recursive tree listing,
`find`, `rg --files`, tree-wide name diff or archive-on-tree.

**No historical scientific data may be used.** No parameter sweep, family, pilot, scientific seed or
outcome analysis. Deterministic analytic calculations from newly declared design targets are permitted
under `/tmp` and consume no historical observation.

Any breach is `STOP_MEASUREMENT_FIREWALL`, immediately.

### 13. Modification allowlist (frozen)

Only these six paths may change:

1. `edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py`
2. `tests/test_future_prospective_measurement_bridge.py`
3. `docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_REPORT.md`
4. `docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_DECISION.json`
5. `docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_MEASUREMENT_SPEC.json`
6. `docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_ROADMAP.md`
7. `docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_REVIEW_JOURNAL.md`

**Not modified:** the engine; `edlab/specs.py`; `edlab/state.py`; the tracker; the lifecycle contract;
any existing runner; any `__init__.py`; any existing test; any historical document. The exact
module-level import with pinned source hashes is frozen instead of opening a package-export detour. If
a modification outside this allowlist proves indispensable, the disposition is
`MEASUREMENT_FEASIBILITY_REVISE` naming exactly **one** minimal successor authority — not another
multi-step roadmap.

### 14. Test environment and evidence requirements (frozen)

Python 3.11.15; pytest 8.4.2 (`>=8.2,<9`); numpy 2.4.4; coverage for statement and branch measurement.
Selectors: `tests/test_lattice_bond_instrumentation.py`, `tests/test_future_lifecycle_contract.py`,
`tests/test_future_lifecycle_runner_integration.py`,
`tests/test_empty_right_nonunit_cadence_tracker_repair.py`,
`tests/test_future_lifecycle_owned_pipeline.py`, `tests/test_future_prospective_measurement_bridge.py`.

Required: all pass; 0 failed; 0 skipped; the complete ordered node-ID list and its digest (sha256 of
the node IDs joined by `\n` with no trailing newline); per-file counts; 100% statement and branch
coverage on the new bridge; no regression in any accepted module; every mandatory compiled bridge
mutant killed **semantically**.

### 15. Terminal dispositions (frozen)

| Disposition | Precondition |
|---|---|
| `PROSPECTIVE_ROUTE_SELECTED` | Exactly one primary route passing all fifteen gates; at most one backup, itself passing all fifteen; both reviewers PASS the same final package |
| `MEASUREMENT_FEASIBILITY_REVISE` | No route is selectable, or an indispensable change lies outside §13, or a required deviation from Part I is discovered — naming exactly one minimal successor authority |
| `STOP_PROSPECTIVE_READINESS` | No route passes **and** Route F's affirmative case under §10.4 is established |
| `STOP_MEASUREMENT_FIREWALL` | Automatic on any firewall breach or any scientific execution |

No disposition authorises implementation of a scientific family, a preregistration, a seed, or a run.
After the terminal disposition the only authorised next action is **human review of this mission**. If
a route is selected, its exact preregistration mission is **named and not begun**.

Part I must be an unmodified byte-exact prefix of the final report. If it would have to change, the
disposition is `MEASUREMENT_FEASIBILITY_REVISE`.

---

*Part II (route designs, bridge qualification, measurement spec, anchoring, comparison, reviews and
terminal disposition) is appended after this protocol is committed. This file's state at the
pre-design commit is the frozen reference.*

## Part II — BRIDGE QUALIFICATION, ROUTE DESIGNS, SYMMETRIC COMPARISON, DECISION

*Part I above is frozen and is a byte-exact prefix. Nothing in it is altered.*

### II.1 Mechanical-test boundary: what was executed

Static inspection established every interface fact in Part I §3–§6. No separate engine smoke test was
therefore required or performed under Part I §9.

The engine **is** executed inside the new bridge's own unit tests, on handcrafted 6×6 and 8×8 lattices
with handcrafted `LatticeBondSpec` values and short schedules. That execution is mechanical
qualification of the bridge, exactly as the accepted owned-pipeline qualification executes the tracker.
It is **not** a pilot, not a family, not feasibility evidence, and produces no scientific claim. The
engine has no seed (Part I §3.1), so no scientific seed was or could be created. No number produced by
a bridge test is interpreted physically anywhere in this report; the one table of engine-produced values
that appears (§II.2.4) is quoted solely to demonstrate that the turnover channel is non-degenerate, and
its physical content is explicitly disclaimed there.

### II.2 The measurement bridge — qualification

**II.2.1 Deliverables.**

| Path | Bytes | sha256 |
|---|---|---|
| `edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py` | 53,493 | `ecb0a03d16c0fe9429f13d76a5de82687ad23eb24d143ba422300274bc10b15e` |
| `tests/test_future_prospective_measurement_bridge.py` | 65,805 | `eecadb4aebe96aa16f5bf18283bd2d8fb6c5ebde62c6ad5e1fd47ade89cca30c` |

No other file changed. Verified by recomputing the sha256 of every pre-existing file in the clean room
against its authorized-parent value: **0 removed, 0 changed, 2 added.**

**II.2.2 Public API.** `MeasurementSpec`; `ComponentMeasurement`; `FrameMeasurement`;
`MeasurementRecord`; `AnchorReceipt`; `DeterministicAppendOnlyLog` (test-only, no network);
`run_measurement_bridge(run_directory, *, law_spec, initial_state, sampled_frames, measurement_spec,
intervention=None, backend="vectorized", acquisition_source_identity)`;
`write_anchor_receipt(run_directory, receipt)`;
`open_measured_analysis_access(run_directory, *, verifier)`. Error hierarchy: `BridgeError` with
`BridgeSpecificationError`, `BridgeScheduleError`, `BridgeChannelError`, `BridgeEvidenceError`,
`BridgeAnchorError`.

**II.2.3 The chain the bridge owns.**

> engine construction → per-step execution → per-step passive-cohort advection → per-sampled-frame
> capture of float matter, resource, bond, tracer and the derived mask → canonical persistence →
> discard → re-read → mask re-derivation from the re-read floats → owned-pipeline execution on the
> **re-read** masks → nested measurement root → external-anchor receipt → analysis access

There is no public parameter accepting frames, masks, tracking, lifecycle documents, manifests,
digests, roots or receipts. The acquisition source handed to `run_owned_future_pipeline` is a private
closure that returns the mask **re-read from disk**.

**II.2.4 Cross-binding, proved mechanically rather than asserted.**

| Claim | How it is established |
|---|---|
| The mask is derived from the exact bound float snapshot | on re-read the bridge recomputes `matter >= matter_threshold` from the persisted floats and refuses on any difference (`BridgeEvidenceError`); mutant **M05** removing that check is killed by a probe with no digest involved |
| The mask survives the pipeline's own detector unchanged | Part I §6.2: the pipeline materialises `True→0.8`, `False→0.1`, and `MeasurementSpec` **refuses** any `matter_threshold` outside `(0.1, 0.8]` at construction |
| Sampled-frame labels are the engine's | each label is read from `state.step` and compared with the declaration; mutant **M02** dropping that check is killed |
| Frame counts match | zero-detection frames are persisted as frames with no components; mutant **M16** dropping them is killed by a test that distinguishes zero detection from zero acquisition |
| The measurement root binds the owned root | mutant **M10** removing it is killed by a probe showing a substituted owned root would otherwise unlock analysis |
| The owned root binds the exact import/source set | mutant **M11** removing the source bindings is killed by a probe showing edited source hashes would otherwise unlock analysis |
| Morphology is inside the externally anchored root | area, mass, centroid, radius of gyration and a pixel-support digest enter the per-frame digest and hence the root; mutant **M09** removing them is killed by a probe showing a repinned morphology-only change would otherwise be accepted |
| No caller-prebuilt document can substitute | no such parameter exists; mutant **M04** handing the in-memory mask instead of the re-read one is killed |

**Turnover is entity-local and non-degenerate.** The first bridge implementation enrolled the cohort as
the **entire** matter field. That is degenerate: a passive tracer equal to the whole matter field
reproduces it bit-exactly forever, so `cohort_residual ≡ 1.0` and the channel can never measure
replacement. The defect was found by mutation testing — a mutant that changed the *enrolment time*
survived, because enrolment was unobservable — and was repaired, not papered over. The cohort is now
enrolled as the matter inside the **cell support of the detected components** at the enrolment frame and
zero elsewhere. On an 8×8 fixture the single component's residual then runs
`1.000 → 0.5267 → 0.5265 → 0.5264 → 0.5262` across five sampled frames, with ~87% of the lattice's
matter correctly unlabelled. *Those numbers are quoted only as evidence that the channel responds; no
physical meaning is claimed for them, and they are not evidence about any law.*

**II.2.5 The anchor gate.** `open_measured_analysis_access` performs, in this order: re-read and
re-verify all local evidence including the mask/float cross-binding; require `ANCHOR_RECEIPT.json`;
require `receipt.root_sha256` to equal the **recomputed** measurement root; require the injected
verifier to return `True`. Any failure raises `BridgeAnchorError` and `open_owned_analysis_access` is
**never reached**. Post-anchor mutation is detected because the root is recomputed, not remembered.
Mutants **M12** (digest unchecked), **M13** (verifier result ignored), **M14** (owned access opened
first) and **M15** (missing receipt tolerated) are each killed semantically.

**II.2.6 Test and mutation evidence.**

| Selector | Tests |
|---|---|
| `tests/test_lattice_bond_instrumentation.py` | 49 |
| `tests/test_future_lifecycle_contract.py` | 52 |
| `tests/test_future_lifecycle_runner_integration.py` | 87 |
| `tests/test_empty_right_nonunit_cadence_tracker_repair.py` | 63 |
| `tests/test_future_lifecycle_owned_pipeline.py` | 235 |
| `tests/test_future_prospective_measurement_bridge.py` | **160** |
| **total** | **646 passed · 0 failed · 0 skipped** |

Ordered node-ID digest (sha256 of the node IDs joined by `\n`, no trailing newline):
`76c0da8d0b22af12fe86b2dbbb3e78d1bde7098e0f10476d3eef9364447e4bed`.
Python 3.11.15, pytest 8.4.2, numpy 2.4.4.
Bridge coverage: **441 statements, 0 missed; 130 branches, 0 partial; 100%.**
No regression: the 486 accepted tests pass unchanged.

**Mutation ledger: 18 compiled mutants, 17 semantic kills, 1 declared survivor.** Every anchor matched
uniquely and every mutant compiled; there is no non-compiling entry. Four mandatory mutants (M05, M09,
M10, M11) were initially killed only by a digest mismatch; six new tests were added so that each is now
killed behaviourally, because Part I §7 M-A8 does not accept hash-only tripwires. The survivor is
**M17** (cohort enrolled at the initial state rather than the first sampled frame) as it stood against
the *first* implementation; after the entity-local enrolment repair it is a semantic kill on two nodes,
with `frames[0].total_cohort` differing 4.0 vs 7.594 and the persisted tracer nonzero in cells no
component owns. **No mutant survives the sealed implementation.**

**II.2.7 Bridge limitations (register `MB-L1…MB-L10`, in the module docstring).** No physical time is
authenticated; `published_at_label` is an opaque unauthenticated caller label; source hashes are
reproducibility bindings, not authority; the append-only log used in tests is a deterministic fake and
contacts nothing; morphology is bound by the bridge but is **not** consumed by lifecycle semantics
(OP-L3 is contained, not solved); `cohort_residual_fraction` is a **declared measurement convention**
and is never passed to `advance_passive_tracer`, which exposes no tolerance parameter; `matter_threshold`
is confined to `(0.1, 0.8]`; `step_count` is disclosed but not root-bound; entity-local enrolment does
not label matter outside the enrolled components, and components that appear after enrolment begin
unlabelled.

**II.2.8 A limitation this report does not soften.** The turnover readout and the persistence readout
are **not fully independent**. Turnover is computed from the cohort tracer advected by engine gross
flows, evaluated over the *detector's* component support; persistence is computed from *tracker*
association. They share the detector and its two constants; they do not share the tracker identity.
This is a real improvement over the architecture Architecture 01 rejected — where a single tracker
identity carried both readouts and a tracker identity swap produced the positive signature — but it is
**not** the full independence Part I §8 N1 would ideally want, and it is charged as such in §II.6.

### II.3 Prospective `MeasurementSpec`

The frozen document is
`docs/individuation/FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R_MEASUREMENT_SPEC.json`.
Its content is summarised here; the JSON is authoritative.

Every one of the six `DetectorSpec`/`TrackerSpec` constants is exposed, frozen, given a **mechanical or
geometric** justification, and given a prospective sensitivity set declared now and never revisited
after data exist:

| Constant | Frozen value | Mechanical/geometric justification | Prospective sensitivity set |
|---|---|---|---|
| `matter_threshold` | 0.45 | must lie strictly inside `(absent_matter, present_matter] = (0.1, 0.8]` so the pipeline's detector reproduces the handed mask exactly (Part I §6.2); 0.45 is the midpoint of `[0.1, 0.8]` to within one decimal and is not tuned to any outcome | `{0.30, 0.45, 0.60}` — all inside the admissible interval |
| `min_cells` | 3 | the smallest support that is not a point or a domino, i.e. the smallest set with a non-degenerate second moment, so that `radius_gyration` and `centroid` are defined on a two-dimensional object | `{2, 3, 5}` |
| `dilation_radius` | 1 | one lattice cell — the smallest dilation that can bridge a one-cell gap on a 4-connected lattice; 0 disables the dilated-IoU term entirely | `{0, 1, 2}` |
| `max_centroid_displacement` | 3.0 | the score term is `exp(-d/max_centroid_displacement)`; 3.0 cells is the smallest scale at which a component may move by its own `min_cells` support in one sampled interval without the term collapsing | `{1.5, 3.0, 6.0}` |
| `max_area_ratio` | 3.0 | a hard disqualification, not a score: an association whose two areas differ by more than 3× is not one object; 3 is the smallest integer ratio that admits the `min_cells = 3` to `9` growth of a compact object between samples | `{2.0, 3.0, 5.0}` |
| `unique_score_margin` | 1e-12 | a numerical tie-break, not a scientific criterion: it separates exactly-equal association scores in float64, where the representable gap near unity is ~2.2e-16 | `{1e-14, 1e-12, 1e-10}` |
| `cohort_residual_fraction` | 0.05 | **declared measurement convention.** A component is called *materially replaced* when at most 5% of its current mass is labelled. It is not an API tolerance; `advance_passive_tracer` has no such parameter | `{0.01, 0.05, 0.20}` |

Also frozen in the JSON: the four `_FRAME_MATERIALIZATION` constants as **read**, not chosen; every
channel definition and its unit or dimensionless interpretation; eligibility rules; split/merge/lost/
disappearance rules; missing-channel behaviour (a channel absent from the engine is recorded
`unavailable` with a reason and is never synthesised); the exact module-level import with the pinned
sha256 of the bridge, engine, instrumentation, lifecycle, runner and owned-pipeline sources; and the
anchor requirements.

**No default embedded invisibly in source is relied upon.** Every value above is written into the
document, and a run whose spec digest differs from the frozen digest is a different measurement.

### II.4 External-root anchoring

**Design.** The measurement root digest is sealed before analysis and committed **outside** the mutable
run directory. Analysis access is refused until a receipt binding that exact digest is present *and* an
injected verifier accepts it. Enforcement is in code and is covered by tests; it is not a convention.

**Publication authentication and public verification are separated.** A credential may be required to
*publish* a commitment; **no secret may be required to verify** it. This is the correction the
Architecture 01 human review applied, and this design adopts it: the requirement is an **independently
verifiable immutable or append-only commitment**, not credential-free publication.

- **Primary:** an externally pushed Git object or ref carrying the root digest, in the public
  repository. Content-addressed, publicly fetchable, verifiable by anyone with no secret. Immutability
  is argued, not assumed: the anchor is an **annotated tag object whose own object id is the receipt
  reference**, so a force-update or deletion of the ref cannot alter the object the receipt names — a
  verifier that cannot fetch that exact object id reports failure rather than success.
- **Fallback:** a timestamped registry entry, WORM commitment, transparency-log entry, or externally
  published root digest, recorded with its venue, retrievable reference and publication label.
- **Proxy 403 does not downgrade the requirement.** The agent environment cannot push. That means the
  sealed run **remains unanalysed** until Tommy or another authorised unproxied process anchors it. It
  does not mean the gate is relaxed, and the code refuses regardless of why the receipt is absent.
- **No external service was contacted in this mission.** The unit tests use
  `DeterministicAppendOnlyLog`, a deterministic in-process hash chain
  (`head₀ = sha256(b"genesis")`, `head_{k+1} = sha256(head_k ‖ d)`), which models append-only
  verification without any network.

### II.5 Fresh Route-E law frame

Constructed **only** from `LawSpec` syntax, source-visible invariants, numerical-stability reasoning,
scale/exchange arguments, and newly declared design principles. No Stage-B value, count, world
parameter, effect size, timing or fit enters at any point.

**II.5.1 Dimensionless coordinates.** By Part I §4.2 a law is fixed, up to the three scales `m_max`,
`n_max`, `dt`, by nine dimensionless groups. `m_max = n_max = 1.0` are fixed as the unit of matter and
of resource — a choice of units, not a scientific parameter. The frame is therefore a distribution over

> `(κ̂, θ̂_m, θ̂_n, D̂, λ, ε̂_b, k̂_on, k̂_off, k̂_tens)`

**II.5.2 Hard source constraints** (exact, from `engine.py`):
`(B1) κ̂ < ¼·e^{−(θ̂_m+θ̂_n)/2}`; `(B2) 4D̂ + 2·ε̂_b·k̂_on < 1`; `(B3) λ ∈ [0,1]`.

**II.5.3 The declared design principle: measurement resolvability.** A run has a declared step budget
`H` fixed **only** by the resource ceiling (§II.5.7). A law belongs to the frame only if its processes
are resolvable within `H` steps — neither frozen below one event per run nor complete within a single
step. This principle is outcome-independent: it refers to the *measurement*, never to what is measured.
It converts `H` into finite bounds through the engine's own equations:

- matter transport must occur at all: `κ̂ ≥ 1/H`, which with **(B1)** gives
  **`θ̂_m + θ̂_n ≤ 2·ln(H/4)`** — a finite bound on the two groups the source leaves unbounded;
- bond turnover must be resolvable: **`k̂_off ∈ [1/H, 1]`** and **`k̂_tens ∈ [0, 1]`** (a rate above one
  per step is unresolved at the finest possible sampling; a rate below one per `H` steps is invisible).

**II.5.4 The frame (frozen).** With `H` declared, draw independently:

| Group | Draw | Source of the bound |
|---|---|---|
| `θ̂_m, θ̂_n` | uniform on the simplex `θ̂_m, θ̂_n ≥ 0`, `θ̂_m + θ̂_n ≤ 2 ln(H/4)` | (B1) + resolvability |
| `ρ_κ` | uniform on `[1/(H·κ̂_max), 1)` where `κ̂_max = ¼ e^{−(θ̂_m+θ̂_n)/2}`; then `κ̂ = ρ_κ·κ̂_max` | (B1), compactified exactly |
| `D̂, ε̂_b, k̂_on` | uniform on the source-admissible region `4D̂ + 2ε̂_b k̂_on < 1` with `D̂ ≥ 1/H` | (B2) + resolvability |
| `λ` | uniform on `[0,1]` | (B3) |
| `k̂_off` | log-uniform on `[1/H, 1]` | resolvability |
| `k̂_tens` | uniform on `[0, 1]` | resolvability |

`dt` is then any value satisfying the source admissibility check; `κ_m = κ̂/dt`, `θ_m = θ̂_m/m_max`, and
so on. Every draw comes from one committed PRNG stream whose seed is published in the preregistration
before any run. **Log-uniform is used exactly where the group spans orders of magnitude and uniform
where it does not; that is a stated convention, and the frame's own sensitivity set replaces
log-uniform by uniform on `k̂_off` as a prespecified variant.**

**Pre-enrolment eligibility.** A draw that the engine's own `LatticeBondSpec.__post_init__` or
`LatticeBondState.validate` rejects is discarded **before** enrolment and redrawn from the same stream,
and the count of such rejections is reported. This is legitimate rejection sampling on a **pure
predicate over parameters**: both validators are read in §2 and neither integrates, steps, or inspects
any outcome. That is the check Architecture 01 could not perform because it had not read the source.

**II.5.5 Initial-condition classes.** `C = 2`, crossed within law. Two is the minimum number that
permits an initial-condition contrast at all; more classes multiply cost linearly without changing the
primary estimand. Both classes are generated by a declared procedure from the committed stream on the
dimensionless lattice, are disjoint by construction, and are defined without reference to any outcome:

- **IC-A — dispersed:** every cell drawn i.i.d. uniform on `[0, m_max]`, `n` uniform on `[0, n_max]`,
  `b ≡ 0`.
- **IC-B — concentrated:** total matter equal to IC-A's expectation, placed in one connected square
  block of side `⌈√(H_lattice·W_lattice/4)⌉` at `m = m_max`, the remainder at `0`; `n` as in IC-A;
  `b ≡ 0`.

Both are pure functions of the committed stream and the declared lattice shape.

**II.5.6 Route-E design (frozen).**

| Element | Value | Justification |
|---|---|---|
| Experimental unit | **law** | declared change of unit away from the entity; see the claim ceiling |
| Laws enrolled `L` | **104** | smallest `L` whose **worst-case** 95% Clopper–Pearson half-width is `≤ 0.10` (0.0997); the precision target `w = 0.10` is the coarsest resolution at which a three-way call with a non-degenerate indifference region is expressible on `[0,1]` |
| IC classes `C` | **2** | design minimality (§II.5.5) |
| Replicates per cell `R` | **6** | the **smallest** `R` whose strict-majority cell call satisfies `P(call \| p = 0.9) ≥ 0.95` (0.9841) and `P(call \| p = 0.3) ≤ 0.10` (0.0705). `R = 4` fails the first (0.9477); `R = 5` fails the second (0.1631) |
| Enrolled worlds `N = L·C·R` | **1,248** | fixed at allocation, before any run |
| Cell criterion | `k_cell ≥ 4` of 6 | strict majority — the canonical prior-free split |
| Law criterion | both IC cells positive | the estimand is about reproducibility *across* initial conditions |
| Primary estimand `Δ` | proportion of the 104 enrolled laws that are majority-instantiating in **both** IC classes | computable from the enrolled denominator alone |
| Interval | two-sided 95% Clopper–Pearson | exact, no normal approximation |

**The conjunction, per world.** A world scores 1 iff at least one track satisfies all four:

- **E-1 entity-like:** at every sampled frame at which it is observed, its component satisfies
  `wraps_y == False and wraps_x == False` (equivalently `percolates == False`) **and**
  `area ≤ ½·H_lattice·W_lattice`. The area bound is geometric, not fitted: an object occupying more
  than half the torus is the bulk phase, not an entity in it.
- **E-2 material replacement:** the component's `cohort_residual` — the fraction of its **current** mass
  that was labelled at enrolment — falls to `≤ cohort_residual_fraction = 0.05`. The cohort is
  entity-local by construction (§II.2.4).
- **E-3 persistence beyond replacement:** the track is continuously observed from enrolment to at least
  twice the sampled frame at which E-2 was first met. Two is the smallest integer strictly greater than
  one: persistence must outlast one complete replacement.
- **E-4 terminal state:** the track's lifecycle terminal state at the horizon is
  `RIGHT_CENSORED_AT_HORIZON`. **The rule and its gloss are the same rule** — a track that dissolves,
  splits, merges or handoff-fails at any point before satisfying E-3 does not satisfy the conjunction,
  and its world scores **0** rather than being removed. This is the E-4 ambiguity Architecture 01 was
  charged with (W15), resolved in favour of the explicit rule.

**Sampling schedule.** Declared jointly with the tracker window, as Part I requires: the schedule is
uniform with interval `Δf = ⌊H/64⌋` and the association window `max_centroid_displacement = 3.0` cells;
the pair `(Δf, 3.0)` is the frozen invariant, and the sensitivity set varies `Δf` by ×½ and ×2 with the
window held. The schedule is never reconstructed from transitions; it is passed to the qualified
tracker as the mandatory `sampled_frames`.

**Decision rule (numeric).** Floors `Δ₁ = 0.10 < Δ₀ = 0.50`, an indifference region of width 0.40, four
times the achieved precision `2w = 0.20`, so a single study can land strictly inside either arm.

| Decision | Rule | Realised region at `L = 104` |
|---|---|---|
| `POSITIVE` | CP lower bound `> Δ₀ = 0.50` | `k ≥ 63` |
| `NEGATIVE` | CP upper bound `< Δ₁ = 0.10` | `k ≤ 4` |
| `INDETERMINATE` | otherwise | `5 ≤ k ≤ 62` |

`Δ₀ = 0.50` is the canonical prior-free boundary: is the conjunction a property of a *typical* law of
the frame? `Δ₁ = 0.10` is the round order-of-magnitude floor below which it is not a property of the
frame at all. Neither is derived from any observation, and the pair is separated by four times the
design's own resolution.

**Operating characteristics** (exact, `/tmp/r1_design.py`, from design targets only):

| Quantity | Value |
|---|---|
| `P(POSITIVE \| Δ = Δ₀)` | 0.0195 |
| `P(NEGATIVE \| Δ = Δ₁)` | 0.0179 |
| **POSITIVE MDE at 80% power** | `Δ = 0.645` |
| **NEGATIVE MDE at 80% power** | `Δ = 0.029` |
| Power POSITIVE at `Δ = 0.70` | 0.9846 |
| Power NEGATIVE at `Δ = 0.02` | 0.9417 |
| Worst-case 95% CP half-width | 0.0997 |

**Both arms are powered against their own floors.** This is the exact defect Architecture 01 failed on
(its negative arm reached 80% only at `Δ ≈ 0.0138`, sevenfold below its single floor). Here the two
floors are distinct, the indifference region is real, and each arm has an 80%-power alternative on its
own side of it.

**Cell-criterion operating characteristics, prespecified and reported with the result** — including the
asymmetric panel Architecture 01 omitted:

| `p` (equal in both classes) | `P(cell)` | `P(law)` |  | `(p₁, p₂)` | `P(law)` |
|---|---|---|---|---|---|
| 0.1 | 0.0013 | 0.0000 |  | (0.9, 0.5) | 0.3383 |
| 0.3 | 0.0705 | 0.0050 |  | (0.9, 0.3) | 0.0694 |
| 0.5 | 0.3438 | 0.1182 |  | (0.8, 0.4) | 0.1615 |
| 0.7 | 0.7443 | 0.5540 |  | (0.95, 0.6) | 0.5431 |
| 0.9 | 0.9841 | 0.9686 |  | | |

`Δ` is therefore explicitly the density of **majority-instantiating** laws at `R = 6`, not a latent
probability; the attenuation, including its asymmetric-IC component, is reported with the estimate.

**Edge events.** Exactly one lifecycle terminal state per track from the exhaustive five. `DISSOLVED_DETECTED_TRACK`, `SPLIT_INTO_TRACKS`, `MERGED_INTO_TRACK` and `UNRESOLVED_HANDOFF` are
**outcomes**, counted, never exclusions; `RIGHT_CENSORED_AT_HORIZON` is the only state compatible with
the conjunction. Global rejection is reserved for contract violations — schema, schedule, digest,
duplicate id — which are software faults, and a family in which one fires is reported as a failed
family, not pruned. Mechanically ineligible worlds (no non-percolating, non-wrapping component ever
detected) score 0 **and** are reported separately; if they exceed 50% of the enrolled 1,248 the family
reports `INDETERMINATE — MECHANICAL_INELIGIBILITY` rather than `NEGATIVE`.

**Informative negative.** A null is decomposed by prespecified discriminators reported unconditionally,
not only when a floor fires: the mechanical-ineligibility fraction; the horizon-censoring fraction
(tracks never reaching E-2 before `H`); the **within-law concordance** of the two IC cells compared
against the rate implied by within-law independence — replacing the McNemar test, which is null
exactly where symmetric IC dependence is strongest — with a numeric threshold and its own
`POSITIVE/NEGATIVE/INDETERMINATE` mapping; the per-class marginal densities as co-primary description;
and `Δ̂` recomputed at every value of the seven-constant sensitivity set as a prespecified
detector/tracker-artefact discriminator. **Structural impossibility is never claimed.**

**II.5.7 Resource ceiling and termination.** Hard ceilings: **1,248 enrolled worlds**, `H` steps each,
and a declared wall-clock ceiling. `H` is fixed by the resource ceiling alone and never by a draw from
the frame — the horizon-calibration circularity Architecture 01 failed on does not arise, because the
resolvability principle runs from `H` to the frame, not from the frame to `H`. Termination fires on run
count and wall-clock only. No interim analysis; the family is analysed once. **Fail-closed
authorisation:** if the preregistration's measured per-run cost projects a total above the wall-clock
ceiling, the family is **not authorised** and is **not shrunk to fit**.

**II.5.8 Independent reproduction.** A separately authorised family of **`L₂ = 36`** laws from a third
disjoint PRNG block at the same pinned source hashes. 36 is the smallest `L₂` at which **both** arms are
reproducible: `POSITIVE` requires `k ≥ 25/36` and `NEGATIVE` requires `k = 0`. The criterion is numeric,
not "consistent with".

**II.5.9 Claim ceiling.** Complete success establishes at most:

> Within the declared law frame, the conjunction of entity-like persistence and complete entity-local
> material replacement is majority-instantiated by a proportion `Δ` of laws in **both** declared
> initial-condition classes, with the stated interval.

That is **below** claim-ladder rung 3, at the **law** level. Rung 3 says "*the state* persists across
material turnover", where "the state" is the exposure-storing, causally efficacious variable of rungs
1–2. Route E measures no state variable; it measures survival of a detected component through material
replacement. **Complete success would establish nothing about any state variable, nothing about
addressability, and nothing about ownership.** It is a prevalence-and-provisioning result.

### II.6 Route G — measurement feasibility

Route G is evaluated against Part I §8 with the same standard as Route E.

**II.6.1 What the engine now demonstrably provides.** Architecture 01 recorded that no intervention
algebra existed. **That was wrong**, and the correction is recorded here against the author's own
earlier position: `FaceIntervention` is a real, executable, spatially local, composable per-face
intervention algebra with a counterfactual record (Part I §3.2). Route G's requirements 6, 7 and 8 —
an executable local intervention algebra, target/sham/off-target operations, shared-environment and
partner controls — are therefore **satisfiable**: a target operation cuts or scales the faces of one
component, a sham operation applies an identity plan under the same code path, an off-target operation
cuts an equal number of faces elsewhere, and co-housing plus environmental equalisation follow from
constructing two components in one lattice with an identical resource field. Requirement 9 —
prospective turnover verification independent of the convention readout — is satisfiable by the
entity-local cohort channel, subject to the independence limitation of §II.2.8.

**II.6.2 What the engine does not provide.** Requirements 1, 2 and 4 fail, on source:

1. **No signed internal state variable exists.** The complete engine state is `m ≥ 0`, `n ≥ 0`,
   `b ∈ [0,1]`. No field takes both signs.
2. **No observable has a genuine symmetry partner.** Every signed derived quantity — `matter_natural`,
   `resource_natural`, the four `*_missing_*_delta` arrays — is antisymmetric under **endpoint
   exchange**: its sign encodes a direction in space, not a two-valued internal convention. Under a
   lattice reflection `S` the geometry transforms with the observable, so `S` exchanges *frames*, not
   *conventions* of a fixed configuration.
3. **The matter flux is an exact gradient flow.** From source, `matter_natural = M·(χ − χ₊)` with
   mobility `M = κ_m(1−b)(1−m/m_max)(1−m₊/m_max)e^{(a+a₊)/2} ≥ 0` and scalar cell potential
   `χ = [m/(1−m/m_max)]·e^{−a}` (Part I §3.4(a)). The sign of the flux on every face is therefore
   **fixed pointwise by a scalar potential difference**. It cannot be selected independently of the
   configuration, so it cannot carry a spontaneously broken two-valued convention. There is no
   transverse, rotational or chirality term anywhere in the update.
4. **The only chirality mechanism in the repository is in a different substrate.**
   `edlab/specs.py` defines `OrbitalSpec.orbital_strength`, documented as "signed = chirality", a
   transverse pair force. It belongs to the **CORE V0 particle substrate** (`ParticleState`: positions,
   velocities, types, ids), for which **no** accepted detector, tracker, lifecycle contract, owned
   pipeline or measurement bridge exists. Adopting it would require an entirely new measurement stack
   and its own qualification chain — far outside this mission's allowlist.

**II.6.3 Verdict, stated as the human review requires.** **Route G is not scientifically falsified.**
Its statistical skeleton — the fixed-sequence hierarchy, equivalence framing of independence with a
declared margin rather than non-significance, sign-exchange invariance of the analysis, and the five
predeclared competing causal models (entity-local, niche, partner-coupled, shared-field,
coordinate/detector artefact) — remains sound and reusable. But on the authorized substrate there is no
outcome-defined observable that changes sign under a transformation leaving the dynamics invariant.

> **Route G remains scientifically unresolved and presently measurement-incomplete.**

No signed observable was manufactured to rescue it. No historical `M_MINUS` result was used as
evidence, parameter guidance or confirmation. **No Route-G statistical numbers are stated**, because
Part I §8 N3 forbids an estimand without an outcome definition, and quoting sample sizes for an
undefined quantity is exactly the error Architecture 01 was charged with.

### II.7 Route F — stop and consolidate

Route F is selected only if neither E nor G can be made prospectively interpretable, the missing
capability is not repairable by a bounded, scientifically neutral change, and consolidation has higher
expected epistemic value than the best admissible bounded family.

The first condition fails: **Route E is prospectively interpretable and its measurement now exists and
is qualified.** Every capability its endpoints need is `D` or `X` in Part I §5 and is bound by a module
with 646 passing tests, 100% branch coverage and 17 semantic mutation kills. That is not a promise; it
is a built artefact.

Route G's missing capability — a signed internal degree of freedom with a symmetry partner — is a
**substrate** fact, not a repairable defect of this programme's engineering. That supports stopping
*Route G*, and this report does stop it. It does not support stopping the programme while an
admissible bounded family exists.

**Route F is not selected.** Difficulty, expense and Architecture 01's incompleteness are not
sufficient reasons, and none of them is relied on here.

### II.8 Symmetric fatal-gate table

One common table. `PASS` / `FAIL` / `N-A`. No weighted average. **One fatal failure rejects.**

| # | Gate | Route E | Route G | Route F |
|---|---|---|---|---|
| N1 | Executable measurement | **PASS** — every endpoint quantity is `D`/`X` and is bound by the qualified bridge | **FAIL** — no signed observable with a symmetry partner exists on the authorized substrate | N-A |
| N2 | Independently justified parameter frame | **PASS** — (B1)–(B3) from source plus one declared resolvability principle; all seven measurement constants justified mechanically or geometrically with sensitivity sets | **FAIL** — derivative of N1: an undefined observable has no parameter frame | N-A |
| N3 | Explicit estimand | **PASS** — six attributes declared | **FAIL** — attribute 4 (outcome) undefinable | N-A |
| N4 | Exact denominator | **PASS** — 104 laws / 1,248 worlds, fixed at allocation | **FAIL** — not computable | N-A |
| N5 | No replacement | **PASS** — pre-enrolment redraw is a pure parameter predicate; nothing after enrolment is replaced | PASS (design) | N-A |
| N6 | Informative both ways | **PASS** — distinct floors, non-degenerate indifference region, five prespecified null discriminators | **FAIL** — a null cannot be distinguished from "no observable was measured" | N-A |
| N7 | MDE and power | **PASS** — POSITIVE MDE 0.645 @80%, NEGATIVE MDE 0.029 @80%, both boundary error rates < 0.02 | **FAIL** — derivative of N3 | N-A |
| N8 | Edge-event accounting | **PASS** — five exhaustive terminal states, all counted, none excluding | PASS (design) | N-A |
| N9 | No closed-family tuning | **PASS** — every bound from source, geometry, or a declared resolvability principle | PASS | N-A |
| N10 | No manufactured entity or convention | **PASS** — E-1 is geometric; no observable chosen after inspection | **FAIL** — any convention observable would have to be chosen after inspecting what produces the desired entity |  N-A |
| N11 | Independent reproduction | **PASS** — `L₂ = 36` with a numeric two-arm criterion | **FAIL** — derivative | N-A |
| N12 | External-root gating | **PASS** — fail-closed in code, four mutants killed | PASS in principle (same gate) | N-A |
| N13 | OP-L3 handling | **PASS** — morphology inside the anchored root; contained, not solved | PASS in principle | N-A |
| N14 | Bounded resources | **PASS** — 1,248 worlds, `H` from the resource ceiling alone, fail-closed authorisation | **FAIL** — unbounded prerequisites (new substrate, new measurement stack) | N-A |
| N15 | Exact claim ceiling | **PASS** — below rung 3, law-level, with three explicit non-establishments | PASS (ceiling stated) | N-A |
| | **Result** | **0 fatal failures — admissible** | **9 fatal failures — inadmissible** | **not selected on §10.4** |

**Route F `N-A` reason, stated once as Part I §8 requires:** Route F enrols no unit, measures no
quantity and executes no family; every gate regulates a prospective design and therefore has no object
in its case. Its admissibility turns solely on Part I §10.4, which it fails (§II.7).

**Symmetry check.** The deferral standard is single: a capability absent from the authorized source is
fatal for **both** routes. Route E is not permitted to defer its population — the frame is fully
specified here, from source read in this mission. Route G is not charged with anything Route E is
forgiven. Two of Architecture 01's charges against Route G are **withdrawn** here because the source
disproves them: the intervention-algebra charge (`FaceIntervention` exists) and the
composite-framing asymmetry.

### II.9 Decision

**Primary route: Route E — replication density. Backup: none.**

By Part I §10.1 only Route E is admissible, so §10.2's information-per-run comparison is not reached.
No backup is named because §10.3 requires a backup to pass all fifteen gates independently and Route G
does not. Route G is recorded as the programme's **named successor question**, whose prerequisite is a
substrate with a signed degree of freedom carrying a symmetry partner — not a statistical redesign.

**Preliminary terminal disposition:** `PROSPECTIVE_ROUTE_SELECTED`, subject to both adversarial reviews.

---

## Part III — ADVERSARIAL REVIEW, WITHDRAWALS, TERMINAL DISPOSITION

*Parts I and II are unaltered. Part I remains a byte-exact 34,848-byte prefix. Per Part I §11 a claim
shown false is withdrawn here, not rewritten above.*

### III.1 Review conduct and verdicts

Both reviewers were launched after checkpoint 2 against the identical package (Parts I + II,
71,995 bytes, sha256 `76561445ebefdca3811353ddf0d1ed15d90a4a996c85baafda970008f869dc68`), the sealed
bridge module and its suite, and the design script.

| Reviewer | Verdict | Findings |
|---|---|---|
| A — engine, measurement and provenance | **FAIL** | A1–A19 (1 BLOCKER, 8 MAJOR, 10 MINOR) |
| B — route selection and statistics | **FAIL** | B1–B26 (6 BLOCKER, 11 MAJOR, 9 MINOR) |

Both independently reproduced the package's mechanical evidence exactly — 646 tests, node-ID digest
`76c0da8d…`, 441 statements / 130 branches / 100% coverage, the bridge sha256 — and Reviewer B
recomputed every statistic through an independent Clopper–Pearson implementation (Brent root-finding on
exact binomial tails rather than `beta.ppf`), agreeing to 4.9e-13. **The arithmetic held. The design
around it did not.**

The complete register is in the review journal.

### III.2 The decisive finding — B1

**Reviewer B falsified a frozen row of Part I §5.** Part I recorded, as a source fact, that no
observable on the authorized substrate has a genuine symmetry partner, and Part II §II.6.2 built
Route G's rejection on it. That is **wrong**, and the refutation is exact, mechanical and
independently reproducible.

- Reading `_face_terms_vectorized` and `_face_terms_reference`: every face quantity —
  `matter_forward`, `matter_reverse`, `resource_natural`, `bond_cue`, `bond_tension`, `r_on`, `r_off`
  — is the **identical expression** for `face_axis` 0 and 1, with the **same scalars**. There is no
  per-axis parameter anywhere in `LatticeBondSpec`, and `affinity` uses the symmetric four-neighbour
  sum.
- Therefore the **lattice transpose**
  `T : m → mᵀ, n → nᵀ, b[0] → b[1]ᵀ, b[1] → b[0]ᵀ`
  is an **exact symmetry of the update**. Verified independently by the author:
  `max |T(stepᵏ(s)) − stepᵏ(T s)| = 5.6e-17` over 20 steps on a 6×6 random state at the source-default
  spec — float round-off.
- The **axis-nematic bond order parameter** `Q = mean(b[0]) − mean(b[1])` satisfies `Q∘T = −Q` exactly:
  `max |Q(branch) + Q(T-branch)| = 2.2e-16` over the same 20 steps, with `Q` non-degenerate
  (≈ −0.0262 … −0.0266).
- `Q` is **entity-localisable**: restricted to a component's internal faces via `DetectedComponent`,
  the author measured a component-local `Q = −0.0978` over 11 axis-0 and 12 axis-1 internal faces —
  the same construction `component_diagnostics` already uses for `mean_internal_bond`. It is class
  **X**, not **U**.
- It is **addressable** by the intervention algebra already recorded in Part I §3.2: cutting axis-0
  versus axis-1 faces of one component is a targeted operation, an identity plan is the sham, and an
  equal number of faces elsewhere is the off-target arm.

The gradient-flow argument of Part I §3.4(a) is correct and was independently re-derived by both
reviewers — but it bounds the sign of the **matter flux** only. It says nothing about the **bond
field's axis anisotropy**, which relaxes per face toward `r_on/(r_on + r_off)` and carries an
orientational degree of freedom the argument never touched. Part II generalised a true statement about
one field into a false statement about the substrate.

**Consequence.** Part I §5's `U` row is false; Part II §II.6's rejection of Route G rests on it; and
`PROSPECTIVE_ROUTE_SELECTED` cannot stand. Under Part I §15 a required deviation from Part I is a
`MEASUREMENT_FEASIBILITY_REVISE` condition. This is exactly what the freeze exists to catch, and it
caught it.

### III.3 Withdrawn claims

Per Part I §11, each is **withdrawn**, not reworded; the original text stands above.

**W1 — Part I §5, row "Symmetry partner of a signed observable" = `U`, and the corresponding
`_UNAVAILABLE_CHANNELS` reason string in the bridge (B1).** **FALSE.** See §III.2. The correct
statement is narrower: *the matter flux carries no sign that can be selected independently of the
configuration*. Whether the axis-nematic bond order parameter `Q` can serve as a **maintained
entity-local convention** — as opposed to a transient consequence of component shape — is **open**, and
is the single question the successor mission must answer.

**W2 — §II.6.2 items 2–3 and §II.6.3, the Route-G rejection (B1).** **WITHDRAWN.** Route G is not
rejected. It is **reopened on a concrete, verified footing**: an exact symmetry `T`, a signed
observable `Q` with `Q∘T = −Q`, entity-localisation, and an executable intervention algebra. Route G's
gate row in §II.8 is void.

**W3 — §II.5.4, the law frame (A1, B2).** **FALSE — the frame is not a probability distribution.**
(B2) bounds only the **product** `ε̂_b·k̂_on`; neither factor is bounded above by source, and the
resolvability principle was applied to `κ̂`, `D̂`, `k̂_off` and `k̂_tens` but **not** to `k̂_on` or
`ε̂_b`. The region has infinite Lebesgue measure — for fixed `D̂`, `∬_{ε̂_b k̂_on < c} = ∫₀^∞ (c/e)de`
diverges logarithmically; Reviewer A measured 0.42 → 3.56 as the truncation moved from 10 to 10¹².
"Uniform" on it does not exist. §II.8's N2/N3/N4 `PASS` verdicts for Route E therefore rest on a frame
that cannot be sampled. The obvious repair — extend the same principle to `k̂_on` — is **not applied
here**, because repairing a frozen frame under review pressure is precisely the failure mode this
programme has already been destroyed by once.

**W4 — §II.5.6, the justification of `w = 0.10` (B3).** **SELF-REFUTED.** "The coarsest resolution at
which a three-way call with a non-degenerate indifference region is expressible" is false, and the
report computes its own counterexample: at `L = 36` both arms exist with a non-empty indeterminate zone
and a worst-case half-width of 0.1708. `w = 0.10` is 1.7× finer than the stated principle requires. It
is a round number, and it sets the entire resource envelope.

**W5 — §II.5.6, the justification of `R = 6` (B4).** **UNJUSTIFIED.** `p = 0.9`, `p = 0.3`, `0.95` and
`0.10` are latent per-world instantiation probabilities and operating-characteristic targets — expected
effect sizes — with no derivation from source, geometry, stability or any declared principle. They are
load-bearing: relaxing 0.95 to 0.94 selects `R = 4` and `N = 832`.

**W6 — §II.5.8 and §II.8 N11, the reproduction family (B5).** **MIS-SCORED.** `L₂ = 36` is the
smallest `L₂` at which the arms are *expressible*, not *powered*. At the primary's own 80% MDEs the
reproduction family's power is **0.333** (positive arm) and **0.347** (negative arm). N11 requires "its
own power"; none was stated. N11 `PASS` is withdrawn.

**W7 — §II.5 and §II.8's "Symmetry check" (B6).** **UNEARNED.** `H`, the lattice shape
`(H_lattice, W_lattice)` and the wall-clock ceiling are never given numeric values, yet every frame
bound, the sampling interval `Δf = ⌊H/64⌋`, IC-B's block side and E-1's area bound depend on them.
"Route E is not permitted to defer its population — the frame is fully specified here" is therefore
false, and the asymmetric-deferral defect Part I §8 exists to forbid recurred in this very document.

**W8 — §II.5.6, `Δf = ⌊H/64⌋` (B9).** **UNJUSTIFIED.** The constant 64 has no geometric, mechanical or
declared-convention argument, and N9 forbids any threshold traceable to `11/64`. The report offers
nothing to exclude the anchoring, which is itself the defect.

**W9 — §II.5.5, IC-B (A8, B12).** **INTERNALLY CONTRADICTORY.** "Total matter equal to IC-A's
expectation" gives `½·m_max·H·W`; the stated block of side `⌈√(H·W/4)⌉` gives `¼·m_max·H·W`. The two
clauses differ by exactly 2×; the procedure has no consistent output, so "both are pure functions of
the committed stream and the declared lattice shape" is false.

**W10 — §II.3, three constant justifications (A3, A4, B24).** **DECORATIVE.**
`min_cells = 3` — the "non-degenerate second moment" claim is false: the straight tromino is collinear
and its second-moment tensor is rank 1, and `centroid`/`radius_gyration` are already well defined at
areas 1 and 2. `max_area_ratio = 3.0` — the "3 → 9 growth" premise is circular, since 9 was chosen
because 9/3 = 3. `max_centroid_displacement = 3.0` — the justification addresses only the score scale
and omits that the constant is also a **hard disqualifier** (`REJECT_CENTROID_DISTANCE`), which Part I
§6 correctly recorded and Part II dropped. `matter_threshold = 0.45` (exact midpoint of the admissible
interval) and E-1's `½·H·W` torus bound survive.

**W11 — §II.8 N12, external-root gating (A5).** **OVERCLAIMED.** The bridge's own entry point is
fail-closed and Reviewer A could not break it. But `open_owned_analysis_access` remains a public export
of the accepted owned pipeline, takes a directory and nothing else, and on a completed bridge run
directory **with no receipt at all** it succeeds and yields the verified lifecycle and completion
evidence — where E-3 and E-4 live. "Analysis is impossible before a verified anchor receipt" is
therefore false as a gate statement. The correct statement is that the **measured** entry point is
fail-closed and a scientific protocol must use it exclusively.

**W12 — §II.2.6, "No mutant survives the sealed implementation" (A6).** **FALSE.** Swapping the two
anchor checks so the verifier runs before the digest comparison passes all 160 tests. The ordering is
stated in §II.2.5 as an ordered guarantee and is unpinned. The claim is withdrawn; the honest statement
is that no mutant *in the declared ledger* survives.

**W13 — §II.2.4, the residual series (A7, B17).** **SELECTIVELY PRESENTED.** The numbers reproduce
exactly, but the fixture runs `min_cells = 1`, not the frozen 3, and its background is hand-set to
0.449 — exactly 1e-3 below the threshold — so the 1.000 → 0.5267 drop is the component's **area
growing 4 → 12** across the threshold, not exchange within the enrolled support. After that single
step the series moves by 5e-4 over twelve further steps, i.e. the one trajectory quoted does **not**
approach E-2's 0.05 criterion. "Non-degenerate" is a claim about physical response and Part I §9
forbids interpreting mechanical test numbers physically. The software fact — the tracer is not
identically the matter field, so the channel is not the degenerate one that was repaired — stands; the
physical characterisation is withdrawn.

**W14 — §II.8 N1 and §II.2.8, the track↔component join (A9).** **NOT ESTABLISHED.** E-2 is defined on
a track's component and E-3 on the same track's continuity, but the map
`(frame, component_index) → track_id` lives in `TrackingResult.assignments`, is built in memory and is
**never persisted**; `LIFECYCLE.json` carries only `assignment_count` and the terminal record. The join
is deterministically pinned by root-bound masks and spec, but it is not *bound by the qualified bridge*
as N1's `PASS` asserts, and Part I §5 does not classify it as a channel at all.

**W15 — §II.5.6, arithmetic and unit errors (B18, B19, A16, B15, B25).** The indifference region
0.40 is **twice** the achieved full width 2w = 0.20, not four times. The 80%-power alternatives are
`Δ = 0.6404` and `Δ = 0.02984`; 0.645 and 0.029 are grid artefacts from two different, undeclared
grids. The mechanical-ineligibility floor is stated at the **world** level while every decision is at
the **law** level. The claim ceiling says "complete entity-local material replacement" where E-2 is a
declared 5% residual convention.

**W16 — §II.5.6, `Δ₁ = 0.10`'s gloss (B8).** **FALSE.** Under the design's own `k_cell ≥ 4 of 6`
attenuation, a uniform per-world instantiation probability of `p = 0.485` produces `Δ = 0.10`. A
`NEGATIVE` verdict is therefore compatible with the conjunction occurring in roughly two of every five
worlds of every enrolled law — not with its being "not a property of the frame at all".

**W17 — §II.8's citation of Part I §8 for an `N-A` category (B23).** **FABRICATED CROSS-REFERENCE.**
Part I §8 defines no `N-A` category and imposes no "state once" requirement; that language belongs to
the previous mission's gate set. Route F's inapplicability reason is correct on the merits and is
governed by Part I §10.4, not §8.

**W18 — §II.8's binary claim (B22).** The Route-G column carries "PASS (design)", "PASS in principle"
and "PASS (ceiling stated)" — not binary values. The table is void in any case under W2.

**W19 — miscellaneous defects accepted without separate argument.** `backend` is a public keyword that
materially changes the persisted floats and is **not** bound into the measurement root, so two
different measurements share one spec digest (A2). Part I §3.4(a)'s identity fails on the closed
boundary `m = m_max`, which IC-B deliberately visits, and survives only by continuity (A10). MB-L8
mis-states its own field list (A11). A whole-directory copy replays against the same receipt, inherited
from OP-L3 and not recorded in the register (A12). `backend="nonsense"` and the tracer's
`ArithmeticError` escape the `BridgeError` hierarchy, and a failed run leaves the directory poisoned
(A13). The `mass == 0` arm of `cohort_residual` is unreachable dead code carrying an unjustified
convention invisible to branch coverage (A14). Root fields `sampled_frames`, `unavailable_channels`,
`law_spec_sha256` and `initial_state_sha256` are protected only by a digest test, i.e. hash-only
tripwires, which Part I §7 M-A8 does not accept (A15). The resolvability inequality should be strict
and requires `H > 4` (A17, B20). `unique_score_margin` is called "not a scientific criterion" in
Part II while Part I lists it as outcome-determining (A18). The bridge binds mass-weighted morphology
while the tracker consumes binarised morphology, and the two differ (A19b). "Shared-environment
control" is misclassified as a derived channel when it is a property of the input state (A19c). The
resolvability principle is applied inconsistently across the four unbounded groups and against the
actual sampling interval (B10). The uniform/log-uniform convention is contradicted by the frame's own
table, concentrating `κ̂` on fast transport (B11). E-3's doubling rule is ambiguous about its origin and
its censoring mode is absent from the discriminators (B13). Operating characteristics are attrition-free
although Part I §8 N7 requires them under the design's own attrition (B14).
`cohort_residual_fraction = 0.05` restates itself and its sensitivity set has no decision mapping (B16).
`LatticeBondState.validate` is a predicate over the initial state, not over parameters, and a mid-run
`ArithmeticError` is an undeclared exit (B21). §II.7 contains no affirmative Route-F analysis, so the
package cannot adjudicate a stop if Route E falls (B26).

**No finding from either reviewer was judged invalid.**

### III.4 What survives

1. **The measurement bridge is qualified and is kept.** 646 tests pass (486 accepted, unchanged, plus
   160 new); 0 failed, 0 skipped; node-ID digest
   `76c0da8d0b22af12fe86b2dbbb3e78d1bde7098e0f10476d3eef9364447e4bed`; 441 statements and 130 branches
   at 100%; 18 compiled mutants with 17 semantic kills and the survivor honestly declared and then
   repaired; exactly two files added and none changed. Both reviewers reproduced all of it. Reviewer A
   could not break the anchor gate on any receipt-forgery variant, and confirmed the mask/float
   cross-binding is enforced semantically, the `(0.1, 0.8]` interval is exactly right at both endpoints,
   and the pipeline's detector reproduces the handed mask bit-for-bit.
2. **The capability ledger is accurate except one row.** Part I §3, §4 and §6 were checked line by line
   against source by Reviewer A and hold. The dimensionless reduction and the two source bounds
   (B1)–(B3) are correct. The gradient-flow factorisation is correct on the interior.
3. **Architecture 01's claim that no intervention algebra exists is refuted** — `FaceIntervention` is
   real, local, composable and counterfactual-recording. That correction stands.
4. **Route G is not merely unresolved — it now has a concrete candidate.** The programme gained an
   exact symmetry of its own dynamics and a signed, entity-localisable, intervenable order parameter.
   That is more than this mission set out to find, and it was found by the review, not by the author.
5. **The engine has no seed**, so no scientific seed was or could be created, and none was.

### III.5 Terminal disposition

> ## `MEASUREMENT_FEASIBILITY_REVISE`
>
> **Primary route: none. Backup: none. Route F: not selected.**

Grounds, each sufficient:

1. **Part I §15** — a required deviation from frozen Part I is discovered: §5's `U` row for the
   symmetry-partnered observable is false (W1, W2).
2. **Part I §10.6** — no route passes all fifteen gates. Route E fails N2, N3 and N4 on a frame that is
   not a probability distribution (W3), N7 on an unearned precision target and undeclared effect sizes
   (W4, W5, and the attrition-free operating characteristics), N11 on an unpowered reproduction stage
   (W6), N12 on an overclaimed gate (W11) and N14 on undeclared ceilings (W7). Route G's gate row is
   void pending the successor's evaluation of `Q`.
3. **Part I §10.4** — Route F is **not** selected. Its first condition fails: a candidate observable
   for Route G now exists and a bounded repair of Route E's frame is available. Stopping would be
   stopping in the presence of two live, named, bounded repairs.

`PROSPECTIVE_ROUTE_SELECTED` is unavailable: no route passes, and both reviewers returned FAIL.
`STOP_PROSPECTIVE_READINESS` is unavailable: Route F's affirmative case is not established.
`STOP_MEASUREMENT_FIREWALL` is inapplicable: no breach occurred, `engine.py` and the accepted modules
were read exactly and never modified, and no scientific family, pilot, sweep, seed or outcome analysis
was executed.

Part I is unmodified and remains a byte-exact 34,848-byte prefix.

### III.6 Sole successor authority

Exactly **one** minimal successor is named, as Part I §13 and §10.5 require. It is **not** begun here.

> ### `FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S`

Its three obligations, and nothing else:

1. **Close the frame.** Apply the resolvability principle uniformly to `k̂_on` and `ε̂_b` — and to the
   actual sampling interval, not to a one-step idealisation — so the law frame is a samplable
   probability distribution; declare `H`, the lattice shape and the wall-clock ceiling numerically with
   outcome-independent justifications; derive `w`, `R`, `Δf` and `L₂` from declared principles with
   stated power, in that order, and re-derive `L` and `N` from them.
2. **Adjudicate `Q`.** Evaluate the axis-nematic bond order parameter against the full symmetry
   battery: is `Q` a *maintained entity-local convention* or a transient consequence of component
   shape? Establish or refute, from source and mechanical qualification only: that `T` is an exact
   symmetry of the admissible ensemble as well as of the update; that both signs occur prospectively;
   that `Q` persists through verified material turnover; that co-housed components can select
   independently; that `FaceIntervention` discriminates entity-local from niche, partner-coupled,
   shared-field and coordinate/detector explanations. **A defeated candidate must be recorded as
   defeated, with the argument — never as "no such observable exists".** No historical `M_MINUS` result
   may be used as evidence, guidance or confirmation.
3. **Re-run the comparison symmetrically** over E, G and F under one gate standard, and select a route
   only if it passes every gate with both reviewers agreeing.

It inherits this mission's qualified bridge and must repair, in-allowlist, the defects recorded in W11
through W19 — binding `backend` into the root, persisting the track↔component join, pinning the anchor
check ordering, replacing the four hash-only root tripwires with semantic probes, typing the escaping
exceptions, and recording the directory-copy replay and the two-morphology facts in the register.

It may **not** run a scientific family, create a scientific seed, tune against Stage B, or claim a
scientific outcome. After it, the only authorised next action is human review.

### III.7 Firewall, refs, residue, scientific meaning

- **Firewall.** Exact object paths only. The newly authorized sources were read at their exact paths
  and hashed; the three paths named in the brief that do not exist were declared as a preflight
  deviation and substituted by their true direct-dependency paths. No listing, glob, wildcard,
  `git status`, recursive tree listing, `find`, `rg --files`, tree-wide diff, archive or memory search.
  No historical scientific runner, Stage-B source, shard, manifest, world, trajectory, candidate,
  checkpoint, autopsy input, result directory, prospective namespace, Kovacs material or global index.
- **Mechanical-execution disclosure.** No standalone engine smoke test was needed or performed. The
  engine **is** executed inside the bridge's unit tests on handcrafted 6×6 and 8×8 lattices, and by the
  author in one 20-step 6×6 verification of the transpose symmetry reported in §III.2. Both are
  mechanical API facts. The engine has no seed; none was created. Every physical characterisation drawn
  from such a run is withdrawn in W13, and the symmetry check reports an exact algebraic property
  (`5.6e-17`, `2.2e-16`), not a physical outcome.
- **Refs.** `refs/heads/main` remains `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`; `HEAD` remains
  `refs/heads/main`; no accepted ref moved.
- **Residue.** Temporary indexes and staging files under `/tmp` on the agent container and the device
  VM, outside the repository; the clean rooms `/home/claude/r1room` and `/home/claude/r1mut` in the
  ephemeral container. No new working-tree file: every deliverable was committed from `/tmp` via
  `git hash-object -w`. The pre-existing, undeletable `.opr00_probe_delete_me` (6 bytes) and Git's
  unlinkable `.git/objects/*/tmp_obj_*` staging artefacts remain — the mount is create-only and `rm`
  returns `EPERM`.
- **Scientific meaning: none.** No scientific claim is made, supported, weakened or implied. No
  scientific family, pilot, sweep, seed or outcome analysis was run, and no historical scientific data
  was opened. The programme's limiting factor has moved: it is no longer *whether a convention
  observable exists* — one candidate now demonstrably does — but whether that candidate is a
  maintained entity-local convention, and whether the law frame can be closed into a distribution.

**Only next action: human review of `FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R`.**
No preregistration mission is named, because no route was selected.

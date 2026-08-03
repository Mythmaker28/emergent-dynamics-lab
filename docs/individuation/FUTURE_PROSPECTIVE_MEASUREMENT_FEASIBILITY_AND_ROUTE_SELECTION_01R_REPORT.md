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

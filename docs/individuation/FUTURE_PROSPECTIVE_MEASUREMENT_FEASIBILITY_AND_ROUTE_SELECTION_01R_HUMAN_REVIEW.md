# HUMAN REVIEW — FUTURE_PROSPECTIVE_MEASUREMENT_FEASIBILITY_AND_ROUTE_SELECTION_01R

**Disposition: `HUMAN_REVIEW_ACCEPTED`.**

Accepting `MEASUREMENT_FEASIBILITY_REVISE`. **No route is selected, and this acceptance qualifies
neither Route E nor Route G.** It accepts an honest negative result in which the mission's own frozen
protocol caught a false capability claim the author had frozen, and in which both adversarial reviewers
returned `FAIL` against the author's preferred outcome.

---

## 1. Candidate and ancestry

| Role | Object |
|---|---|
| Branch | `codex/future-prospective-measurement-feasibility-route-selection-01r` |
| Authorized parent | `a735c64dd912dd52c06dd7b890d29e89bdf49b8d` |
| Frozen Part I | `f4bf11e4d2a7f7b4704fcd884e050bc94dce91cc` |
| Bridge and tests | `f19c9a8c9df85bd1bf8530ee21295115faea69ba` |
| Sealed package | `cc55137435f286a526ef634c5eeddb74b789f282` |

Exact linear ancestry verified by first-parent walk and by resolving each commit's parent individually:
`a735c64d → f4bf11e4 → f19c9a8c → cc551374`. Commit subjects, in order: *freeze 01r capability ledger
and evaluation protocol part I*; *qualified prospective measurement bridge and its test suite*;
*seal 01r measurement feasibility and route selection package*.

## 2. Pre-write verification

**2.1 Exactly seven paths added; no accepted path changed — proved constructively.** Two temporary
indexes under `/tmp`; no listing of any kind.

- **Forward:** `read-tree a735c64d` + `update-index --add --cacheinfo` for the seven declared paths →
  `write-tree` = **`397de828f3e49cdd6834b7897a42d591ef7529c4`** = `cc551374^{tree}` exactly.
- **Reverse:** `read-tree cc551374^{tree}` + `--force-remove` of the same seven →
  **`a6dfb5a9e260b2724f0dcc26fec1f20eb1f002a2`** = `a735c64d^{tree}` exactly.

Both directions agree, so the complete relation holds: seven paths added, **no undeclared path
changed** anywhere on the branch.

| Declared path | Bytes | Blob |
|---|---|---|
| `edlab/substrates/lattice_bond/future_prospective_measurement_bridge.py` | 53,493 | `a992fd03062edd2da468163ffab2976914d9bc9b` |
| `tests/test_future_prospective_measurement_bridge.py` | 65,805 | `44d531a61e46f1c9d1b952ef2a2aaa5cfb56de00` |
| `…_01R_REPORT.md` | 95,243 | `ef6785ffa5da9ef31f50675e86a5b1847019c343` |
| `…_01R_DECISION.json` | 10,204 | `52a46ff80811c144fbf430843d6dcaf0436ae1aa` |
| `…_01R_MEASUREMENT_SPEC.json` | 10,437 | `a60502a7972023458eb317bd163f48a8e14c66e8` |
| `…_01R_ROADMAP.md` | 4,762 | `0ba89df0342ec9649af8b15840d762912b426d80` |
| `…_01R_REVIEW_JOURNAL.md` | 9,562 | `74f7d381f75a19014f5e5588cb6b7ca150098f64` |

**2.2 Accepted sources byte-identical to the parent.** Blob ids resolved at `cc551374` and at
`a735c64d` and compared, all **SAME**: `engine.py` `0980525690…`; `instrumentation.py` `b5e5475c…`;
`lifecycle.py` `a3592eb7…`; `future_lifecycle_runner.py` `44135ee7…`;
`future_lifecycle_owned_pipeline.py` `5dd8a66a…`; `lattice_bond/__init__.py` `db72a3a0…`;
`edlab/specs.py` `93ec1094…`; `edlab/state.py` `daa01aab…`; `edlab/__init__.py` `fe0710e6…`;
`edlab/substrates/__init__.py` `9bc0abd9…`; `pyproject.toml` `98d78c1d…`; and all five accepted test
files. Historical documents are covered by the tree proof.

**2.3 Part I is a byte-exact prefix.** The frozen blob at `f4bf11e4` is 34,848 bytes, sha256
`b704ccff9d3bd38d608fba2aed2cadad7d2caee53c98e20feea46dc3df74a340`; the first 34,848 bytes of the
sealed 95,243-byte report hash to the same value. Sealed report sha256
`207a0c4a519a2fbc681960a110f163caf8d0bf16a6f5fd79adf932bba0f10e31`. Bridge sha256
`ecb0a03d16c0fe9429f13d76a5de82687ad23eb24d143ba422300274bc10b15e`; test suite
`eecadb4aebe96aa16f5bf18283bd2d8fb6c5ebde62c6ad5e1fd47ade89cca30c`.

**2.4 Decision JSON carries no selected route, estimand, MDE, threshold or sample size.** Read
directly: `terminal_disposition: "MEASUREMENT_FEASIBILITY_REVISE"`; `primary_route: null`;
`backup_route: null`; `route_F_selected: false`; `route_selected: false`; `selected_estimand: null`;
`sample_size_logic: null`; `mde: null`; `scientific_claim: null`;
`scientific_family_executed: false`; `scientific_seed_created: false`;
`parameter_sweep_executed: false`; `pilot_executed: false`; `historical_data_opened: false`;
`preregistration_mission_named: null`; `source_or_test_files_modified: 0`; `files_added: 2`. The
`estimand_note` field explicitly withdraws every design value — `L = 104`, `C = 2`, `R = 6`,
`N = 1248`, `Δ₀ = 0.50`, `Δ₁ = 0.10`, `w = 0.10`, `k_cell ≥ 4`, `L₂ = 36`,
`cohort_residual_fraction = 0.05`, MDE `0.6404`/`0.02984` — and forbids their reuse as anchors, priors
or starting points.

**2.5 Evidence reused, not rerun.** The bridge and test hashes at `cc551374` match the sealed package,
so nothing was re-executed. Recomputed from the qualification record: **646 collected, 646 passed,
0 failed, 0 skipped**; per-file 49 / 52 / 87 / 63 / 235 accepted = **486 accepted nodes unchanged**,
plus **160 new**; 486 + 160 = 646 ✓. Ordered node digest
`76c0da8d0b22af12fe86b2dbbb3e78d1bde7098e0f10476d3eef9364447e4bed`. Bridge coverage **441 statements,
0 missed; 130 branches, 0 partial; 100%**. Python 3.11.15, pytest 8.4.2, numpy 2.4.4.
`files_changed_outside_the_two_new_ones: 0`.

**2.6 Branch absent; refs unmoved.**
`refs/heads/codex/future-prospective-measurement-feasibility-route-selection-01r-human-review` did not
exist before this record. `refs/heads/main` = `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`, unmoved;
`HEAD` remains the symbolic ref `refs/heads/main`. Accepted branches unmoved:
`…architecture-01` = `02f7405d`, `…architecture-01-human-review` = `a735c64d`,
`…owned-pipeline-runner-00-human-review` = `d293eaf9`. Verified without `git status`.

**2.7 No selectable route is disguised as REVISE.** The decision JSON records three independent
grounds, and I checked each against the candidate's own frozen protocol. Route E fails on a law frame
that is not a probability distribution — a defect of definition, not of preference. Route G's gate row
is **void**, not passing: its rejection was withdrawn and no replacement adjudication was performed.
Route F is refused affirmatively under Part I §10.4. Nothing in the package satisfies the fifteen
gates, and both reviewers returned `FAIL`. **The REVISE is real.**

## 3. Bridge status — exact

**Qualified as a mechanical artefact, within a scope this record states precisely.**

*What is established:* a new module and suite added as exactly two files, changing nothing else; 646
tests passing with 0 failed and 0 skipped; 100% statement and branch coverage of the new module; the
486 accepted tests unchanged; a semantic mutation ledger; and, per the review journal, an adversarial
reviewer who reproduced all of it and could not defeat the anchor gate on any receipt-forgery variant
it constructed — absent receipt, valid reference with a wrong digest, correct digest with a bogus
reference, forged digest with a permissive verifier, and a single mask byte flip all refuse, the last
with a semantic error and no digest involved.

*What is **not** established, and is refused as an overclaim:*

1. **The bridge is not a globally non-bypassable evidence gate.** The accepted
   `open_owned_analysis_access` remains a public export of the owned pipeline, takes a directory and
   nothing else, and succeeds on a completed bridge run directory **with no anchor receipt at all** —
   yielding the verified lifecycle and completion evidence. The candidate withdrew the corresponding
   gate claim as W11. **Accepted as withdrawn.** The bridge provides a *supported anchored path*; it
   does not make every lower-level repository path non-bypassable.
2. **A bit-identical directory copy replays** against the same receipt: the root does not bind run
   identity. Scientific run identity and family enrolment are **not yet bound against replay**.
3. **The anchor-check ordering is not pinned by any test.** A mutant that runs the verifier before the
   digest comparison passes all 160 tests. The candidate withdrew "no mutant survives the sealed
   implementation" as W12 and restated it as "no mutant *in the declared ledger* survives".
   **Accepted as withdrawn.**
4. **The track↔component join is not persisted.** `TrackingResult.assignments` is built in memory and
   never written, so the map a future endpoint would need is not bound by the qualified bridge (W14).

**Ruling.** No scientific family may rely on this bridge until the supported scientific entry point,
the anchor-check order and the replay binding are frozen. The successor must repair items 1–4
in-allowlist. Subject to that scope, the bridge is a real, banked, reusable artefact and is kept.

## 4. Mutant-18 status — exact

The declared ledger contains **18 compiled mutants**: sixteen mandatory (`M01`–`M16`) and two marked
**extra** (`M17`, `M18`). Every anchor matched uniquely and every mutant compiled; **there is no
non-compiling entry**, and none is claimed as a kill that is not one.

- **`M18`** ("frame `ordinal` bound as constant 0") is a **semantic kill**, on
  `test_frame_labels_are_read_from_the_engine_state`, with ordinals returning `(0,0,0,0)` instead of
  `(0,1,2,3)`.
- The single entry that is **not** a kill in the "17 semantic kills" headline is **`M17`** ("cohort
  enrolled at the initial state rather than the first sampled frame"). Its exact classification, as
  recorded: an **explicitly extra, non-mandatory** mutant that was an **equivalent mutant against the
  first implementation** — demonstrated, not assumed, by byte-identical persisted channels — and which
  the entity-local enrolment repair converted into a **semantic kill on two nodes**
  (`frames[0].total_cohort` 4.0 vs 7.594, and a persisted tracer nonzero in cells no component owns).

Under the governing rule this is "equivalent … and explicitly non-mandatory, accurately recorded", so
**the accounting is accepted with that exact classification**. `M17` is **not** a live mandatory
survivor, so the bridge-qualification bar is not tripped by it.

**One correction of the candidate's own wording.** "18 compiled mutants, 17 semantic kills, 1 declared
survivor" describes the **pre-repair** state, while "no mutant survives the sealed implementation"
describes the **post-repair** state; the two sit in one paragraph and are in tension. The candidate's
reviewer charged this (A19a) and it was withdrawn under W19. The accurate sealed accounting, recorded
here, is: **18 of 18 semantic kills against the sealed implementation; 17 of 18 against the pre-repair
implementation, the single non-kill being the extra, equivalent `M17`.** Separately, a live survivor
**outside** the declared ledger exists — the anchor-ordering mutant of §3 item 3 — and is disclosed,
non-mandatory, and assigned to the successor.

**The cohort-enrolment defect was real, and all four conditions hold.** Verified from the sealed
documents: the original enrolment covered the **whole matter field** (`tracer = state.m.copy()`); a
passive tracer equal to the whole matter field reproduces it bit-exactly, so `cohort_residual ≡ 1.0`
and the **turnover channel was degenerate**; the final implementation enrols **entity-locally**, on the
cell support of the detected components at the enrolment frame and zero elsewhere; and the correction
is **tested** (new tests including a partial-turnover fixture and the now-killed `M17`) and **reviewed**
(Reviewer A attacked the fixture's presentation as A7, which was accepted and withdrawn as W13). This
is the mission's strongest evidence of good faith: mutation testing found a defect in the author's own
shipped work and the defect was repaired rather than argued away.

## 5. Reviewer interpretation

**Reviewer A: `FAIL`. Reviewer B: `FAIL`. 45 findings. 19 withdrawals. Zero findings judged invalid.**

Verified against the review journal: §3.3 "Findings judged invalid — **None**", and §3.2 maps every
major and minor finding to a numbered withdrawal, with no finding left unaccounted. Corrections against
the author's own position remain visible and are recorded as such: **W1** and **W2** withdraw the
author's frozen capability row and restore the route the author had rejected.

A final `FAIL`/`FAIL` is **compatible** with accepting this REVISE — the candidate's own Part I makes
`PASS`/`PASS` a precondition of `PROSPECTIVE_ROUTE_SELECTED` only, and that is not claimed. It is
**not** compatible with any claim of route qualification, and none is made. Round 2 was correctly not
run: a second round against a package whose central capability row is known false would test nothing.

## 6. Engine facts — independently verified from the exact authorized source

Verified by reading the exact blob `edlab/substrates/lattice_bond/engine.py` (`0980525690…`, unchanged
from the parent) and `instrumentation.py` (`b5e5475c…`). **No engine, tracker, bridge, test, coverage,
mutation, power calculation, symmetry check or scientific analysis was executed in this review.**

| Claim | Verdict | Source ground |
|---|---|---|
| `LatticeBondEngine` is deterministic | **CONFIRMED** | the update is a pure function of `(spec, state, intervention, backend)`; no stochastic call anywhere |
| No seed parameter or hidden RNG | **CONFIRMED** | `LatticeBondSpec` has twelve fields, none a seed; `LatticeBondEngine.__init__` takes only an optional spec |
| Frame labels derive from `state.step` | **CONFIRMED** | `LatticeBondState(m_next, n_next, terms.bond_next.copy(), int(state.step) + 1)` |
| Stepping does not mutate the input | **CONFIRMED** | new arrays are built and `bond_next` is copied; `_readonly_scale` makes intervention plans immutable through a read-only buffer, not merely a flag |
| `FaceIntervention` is executable, per-face local, composable, counterfactual-recording | **CONFIRMED** | `open`, `from_cuts(shape, matter_faces, resource_faces)`, `compose` (elementwise product, monoid with `open` as identity); the ledger records `matter_scale`, `resource_scale`, `matter_missing`, `resource_missing` and the four signed `*_missing_*_delta` arrays |
| Nine dimensionless groups | **CONFIRMED** | twelve law fields minus the three scales `dt`, `m_max`, `n_max`; the substitutions `κ̂ = κ_m·dt`, `θ̂ = θ·scale`, `D̂ = D·dt`, `ε̂_b = ε_b/n_max`, `k̂ = k·dt` reproduce the update |
| Bound (B1) `κ̂ < ¼·e^{−(θ̂_m+θ̂_n)/2}` | **CONFIRMED** | rearranging the source property `matter_dt_bound = 1/(4 κ_m e^{affinity_span/2})` with `affinity_span = θ_m m_max + θ_n n_max` |
| Bound (B2) `4D̂ + 2·ε̂_b·k̂_on < 1` | **CONFIRMED** | rearranging `resource_bond_dt_bound = 1/(4D + 2 ε_b k_on / n_max)` |
| Matter flux has the stated gradient-flow form | **CONFIRMED ON THE INTERIOR** | `matter_natural = M·(χ − χ₊)`, `M = κ_m(1−b)(1−m/m_max)(1−m₊/m_max)e^{(a+a₊)/2} ≥ 0`, `χ = [m/(1−m/m_max)]·e^{−a}`. The identity fails on the closed boundary `m = m_max`, where `χ = ∞` and `M = 0`; the candidate records this (A10 → W19) and the conclusion survives by continuity. **Accepted with that qualification** |

**Source facts versus mechanical observations — the line this record draws.** Everything in the table
above is a **source fact**: it follows from reading the exact authorized module. The residual series
(`1.000 → 0.5267 → …`), the `total_matter = 30.94` and `total_cohort = 4.0` figures, the 6×6 and 8×8
fixture outputs and the 20-step numerical residuals are **mechanical observations** on handcrafted
fixtures. **None of them is scientific evidence about anything**, and the candidate's own physical
characterisation of the residual series is withdrawn as W13. This record treats them only as evidence
that software behaves as its tests say.

## 7. Transpose symmetry — scoped

The candidate states the lattice transpose `T : m → mᵀ, n → nᵀ, b[0] → b[1]ᵀ, b[1] → b[0]ᵀ` to be
"an **exact symmetry of the update**", supported by a source argument and by one 20-step 6×6 numerical
check. **Three claims must be kept apart, and the candidate conflates the second and third.**

1. **Definitional.** If a transformation exchanges the two bond-axis channels, then
   `Q = mean(b[0]) − mean(b[1])` changes sign under it. This is true by construction and needs no
   verification.
2. **Mechanical evidence.** Residuals of `5.6e-17` and `2.2e-16` over 20 steps are strong evidence of
   equivariance **for the tested fixtures**: a 6×6 **square** lattice, periodic boundaries, the
   source-default `LatticeBondSpec`, one random state, **no intervention**, and the vectorized backend.
3. **Global exactness.** Those residuals are **not**, by themselves, a mathematical proof of exact
   symmetry for every lattice, boundary, law, intervention and shape.

**The source argument is a strong sketch, not a completed derivation.** Two of its premises are
genuinely source-verified — `LatticeBondSpec` contains **no per-axis parameter** (twelve fields, all
scalar), and every face expression in both `_face_terms_vectorized` and `_face_terms_reference` is the
identical formula for `face_axis` 0 and 1 with the same scalars, with `affinity` built from the
symmetric four-neighbour sum. Four conditions are **not** addressed anywhere in the package:

- **Square versus rectangular lattice.** `LatticeBondState.validate` requires only
  `min(m.shape) >= 2`; **rectangular lattices are admissible**. For `H ≠ W`, `T` maps an `(H,W)` system
  to a *different* `(W,H)* system: it is an isomorphism **between two systems**, not an automorphism
  **of one**. Spontaneous breaking of a two-valued convention requires the transformation to act on the
  system itself, so the `Z₂` structure Route G would need exists **only on a square lattice**. The
  verified fixture was 6×6; the report never states the restriction.
- **Boundary conditions.** The update is periodic on both axes throughout (`np.roll`), which is why
  transposition preserves neighbour structure. Source-visible and true, but it is a **condition**, not
  a given, and must be declared.
- **Transposition of interventions.** `FaceIntervention` carries `(2,H,W)` arrays that must transform
  as `scale[0] → scale[1]ᵀ`, `scale[1] → scale[0]ᵀ`. The candidate never states this map and its
  numerical check ran with `intervention=None`. **Equivariance under intervention is untested and
  unstated** — and the entire Route-G intervention battery depends on it.
- **Detector and tracker equivariance.** `detect_components` seeds components from
  `root = min(unseen)` over **linear indices** `y·W + x`, which is **not** transpose-equivariant:
  component *indices* are generally permuted under `T`, and `wraps_y`/`wraps_x`, `centroid_y`/
  `centroid_x` swap. Any per-component `Q` must therefore be matched geometrically, never by index.
  The package does not address this at all.

**Ruling: supersede the wording; do not defer.** The claim is superseded to read:

> On a **square** lattice with **periodic** boundaries and a law drawn from `LatticeBondSpec` — which
> contains no per-axis parameter — the transpose `T` is equivariant with the update, verified
> mechanically to float round-off on the tested fixtures and supported by a source argument that
> remains to be completed. Its status for rectangular lattices, under intervention, and through the
> detector and tracker is **open**.

Deferral is not warranted, because the scoping does **not** disturb the disposition. Even at its
narrowest — square lattice, periodic boundaries, no intervention — the configuration is squarely inside
the authorized substrate, so frozen Part I §5's row asserting that **no** observable has a genuine
symmetry partner is **still false**, and Part I §15's deviation trigger still fires. Moreover, the
disposition rests on **two further independent grounds** (§10.6 and §10.4) that do not involve the
symmetry at all.

## 8. `Q` — promise and ambiguity, recorded prominently

**What `Q` is.** A genuine **signed observable candidate**; **entity-localisable**, by restricting to a
component's internal faces exactly as `component_diagnostics` already computes `mean_internal_bond`;
and **addressable** by `FaceIntervention`, which can cut axis-0 versus axis-1 faces of one component,
apply an identity plan as a sham, and cut an equal number of faces elsewhere as an off-target arm.
That is more than the programme had before this mission, and it was found by review, not by the author.

**What `Q` is not.** **None of this establishes an internal convention.** Every one of the following
remains live, and each must be excluded prospectively rather than after the fact:

- `Q` may be **transient bond anisotropy** that relaxes away;
- `Q` may simply **track entity shape or orientation** — an elongated component has more internal faces
  on one axis, so a nonzero `Q` may be a restatement of morphology rather than a state;
- `Q` may be a **lattice-axis artefact** of the discretisation or of the detector's axis-dependent
  bookkeeping;
- an **intervention applied before selection could manufacture the sign it later "discovers"**;
- and on a rectangular lattice the `Z₂` does not act on the system at all (§7).

**Route G therefore requires a prospectively frozen discriminator** among: a maintained internal bond
convention; passive morphology or shape anisotropy; external or lattice orientation; an
intervention-imposed sign; and transient relaxation. Until that discriminator exists and is frozen
before any data, `Q` is a **measurement primitive, not a result**.

**Route G is reopened, not selected, and not scientifically confirmed.** Historical `M_MINUS` evidence
remains prohibited as evidence, as parameter guidance and as confirmation.

## 9. Route E — interpretation

Confirmed from the sealed package:

- the proposed law frame **was not a probability distribution**;
- bounding only the **product** `ε̂_b·k̂_on` left a region of **infinite Lebesgue measure**, on which no
  uniform distribution exists;
- **`H`, the lattice shape and the execution ceiling were never given numeric values**, so three
  outcome-determining constants were deferred — the asymmetric deferral the mission's own Part I
  forbids;
- the proposed reproduction family **did not meet its own precision requirement**: `L₂ = 36` is the
  smallest size at which the two arms are *expressible*, not at which they are *powered*;
- **four effect sizes were undeclared** — the `p = 0.9`, `p = 0.3`, `0.95` and `0.10` targets that
  selected `R = 6`, and relaxing `0.95` to `0.94` would have selected `R = 4` and `N = 832`;
- the reproduction family's power at the primary's own MDEs is approximately **0.33 and 0.35**;
- **all proposed `Δ₀`, `Δ₁`, `L`, `R`, `N` and `L₂` values are withdrawn** and may not be reused.

**Route E remains scientifically unresolved. Nothing about actual replication density follows from this
package.** The withdrawal is of a *design*, not of a *question*.

## 10. Anchoring — verified behaviour and retained limitations

The bridge's **local** fail-closed behaviour is verified and its four anchor mutants are killed
semantically: an unchecked receipt digest, an ignored verifier result, owned access opened before the
anchor checks, and a tolerated missing receipt are each caught. Publication authentication and public
verification are correctly separated — a credential may be required to publish; no secret is required
to verify — and no external service was contacted, the tests using a deterministic in-process hash
chain.

**All disclosed limitations are retained, none is softened:** the accepted
`open_owned_analysis_access` remains callable without a receipt; copying a directory may replay a
locally valid evidence package; the anchor-check ordering is not yet pinned; and scientific run
identity and family enrolment are not yet bound against replay.

**Therefore:** the bridge may provide a **supported anchored path**; it does **not** make every
lower-level repository path globally non-bypassable; and **no scientific family may rely on it** until
the supported scientific entry point and the check order are frozen.

## 11. Scientific interpretation, stated plainly

- **No prospective route passed.**
- **No scientific hypothesis was tested.**
- **No parameter estimate was obtained.**
- **No seed and no family exists** — the engine has no seed parameter, so none could be created.
- **No engine observation from this mission may be reused scientifically.** The 6×6, 8×8 and 20-step
  outputs are mechanical fixtures, not entities, worlds or results.
- **The value newly established is mechanical capability knowledge**: what the engine exposes, what the
  bridge can bind, and where the anchoring gate does and does not hold.
- **Route G now has a plausible measurement primitive rather than a result.**

## 12. Tree, refs, firewall, remote

- **Tree.** This record adds exactly one path and modifies nothing. Proved constructively with a
  temporary index under `/tmp`: `read-tree cc551374` + one `--cacheinfo` add reproduces this commit's
  tree, and removing that single path from this commit's tree reproduces `cc551374^{tree}`
  (`397de828f3e49cdd6834b7897a42d591ef7529c4`) exactly. No candidate document, source or test was
  modified.
- **Refs.** `refs/heads/main` remains `f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77`; `HEAD` remains
  `refs/heads/main`; `…-01r` remains `cc551374`; and the three accepted predecessor branches are
  unmoved.
- **Firewall.** Exact Git object paths only. No directory listing, glob, `git status`, recursive tree
  listing, broad grep, `find`, `rg --files`, archive operation or project-memory search. No historical
  scientific data or runner was opened. **Nothing was executed** — no engine, tracker, bridge, test,
  coverage run, mutation, power calculation, symmetry check or scientific analysis. Every verification
  in this record is either a Git object resolution, a digest of a blob, or a reading of exact source.
- **Residue.** Two temporary indexes under `/tmp`, outside the repository. No new working-tree file:
  this record was committed from `/tmp` via `git hash-object -w`. The pre-existing, undeletable
  `.opr00_probe_delete_me` (6 bytes) and Git's unlinkable `.git/objects/*/tmp_obj_*` staging artefacts
  remain — the mount is create-only and `rm` returns `EPERM`.
- **Remote.** `NOT SYNCHRONIZED`. One push attempt; HTTP 403 from the proxy, non-blocking; no retry, no
  credential change, local refs preserved:

  ```
  git -C "C:\Users\tommy\Documents\ising v3" push origin refs/heads/codex/future-prospective-measurement-feasibility-route-selection-01r-human-review:refs/heads/codex/future-prospective-measurement-feasibility-route-selection-01r-human-review
  ```

## 13. Sole successor authorization

Authorized, exactly and only:

> ### `FUTURE_PROSPECTIVE_AXIS_CONVENTION_AND_FRAME_CLOSURE_01S`

**One combined closure-and-selection mission.** It **was not begun** during this review.

It **may**:

1. Produce a **source-level transpose-equivariance derivation** and specify its exact valid domain.
2. Freeze: lattice dimensions and shape; boundary conditions; horizon; execution ceiling;
   sampled-frame schedule; and the state, law and **intervention** transpose maps.
3. Define a **finite normalized probability distribution** over the nine dimensionless law groups,
   independently of historical outcomes.
4. Resolve Route-E sample size, MDE, precision and reproduction-family arithmetic.
5. Define a **prospectively frozen shape-anisotropy observable** from the entity's matter/mask geometry.
6. Define the signed bond observable `Q` **independently of that shape measure**.
7. Build mechanical **paired counterexamples**: same shape, opposite `Q`; transposed shape and
   transposed `Q`; changed shape with maintained `Q`; changed `Q` with approximately maintained shape;
   passive relaxation without intervention; sham and off-target intervention.
8. Establish whether `Q` can, **in principle**, be maintained independently of shape rather than merely
   correlate with it.
9. Freeze **intervention timing** so that no sign-setting intervention occurs before spontaneous
   convention selection.
10. Close **anchor ordering and replay binding** for the supported future scientific entry point.
11. Re-evaluate **E, G and F symmetrically**.
12. Select a route **only** with reviewer `PASS`/`PASS`.

It **must not**: open historical scientific data; use `M_MINUS` evidence; run a prospective family;
create a scientific seed; tune parameters against mechanical outcomes; or interpret mechanical fixtures
as scientific entities.

**If no finite law distribution can be justified, or no shape-independent signed convention can be
justified, it must reject the relevant route definitively rather than defer it again for the same
reason.** Two deferrals on one ground is a pattern; a third would be an evasion.

It inherits the qualified bridge and must repair, in-allowlist, the four scope limitations of §3 and
the defects the candidate recorded as W11–W19.

---

**Scientific meaning of this review: none.** No scientific claim is made, supported, weakened or
implied. No data was opened and nothing was executed. This record accepts a governance finding: the
programme's limiting factor is no longer *whether a convention observable exists* — a candidate now
demonstrably does, within a scope this record narrows — but whether that candidate is a maintained
entity-local convention rather than a shadow of shape, and whether the law frame can be closed into a
distribution.

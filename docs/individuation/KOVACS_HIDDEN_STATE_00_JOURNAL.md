# KOVACS-HIDDEN-STATE-00 — Phase-0 mission journal

Mission-specific journal (kept under `docs/individuation/` to avoid touching shared indexes
`RUN_INDEX.md` / `EXPERIMENT_INDEX.md` / `DECISION_LOG.md` / `PROJECT_STATE.md`, which a parallel agent
active on 2026-07-18 may be editing). Branch: `claude/kovacs-hidden-state-00-phase0`. Commit SHA reported
in the session hand-off and project memory.

## 1. Mission and scope

Phase 0 only. Question: can two histories bring exact clones to the same declared macro-observable `Z`,
yet produce different subsequent relaxation under identical dynamics/environment/`up_ref`, probe-free?
Deliverables: derivation, candidate-`Z` selection, DEV crossing/timing feasibility, minimal protocol,
estimand & classification, null-diagnostic schema, preregistration draft, GO/REVISE/STOP, journal,
clean committed+pushed branch. Stop after Phase 0 for human review.

## 2. Lineage established from the repo (corrects/extends prior session memory)

The turnover line advanced past the memory index's 03E: `9cb996b` (`codex/lci-turnover-prospective-03g-001`)
**certified 03G Outcome B** — a causal feeding effect surviving deep material turnover — via a sealed
one-shot (`b5c0f02` final seal 03l), then `d4a146a` synthesised the V5 paper *Persistence Without
Ownership*. Downstream, ACCESS-STRUCTURE-00 Phase 0/0.5 (`fa26173`) built the qualified boundary/clamp
operators; the exact-clone history program then ran on top of it:

- `ea6e6a0` COUNTERFACTUAL-HISTORY-CORE-00 — exact-clone 2×2 dose×order factorial, 24 DEV worlds
  57001–57024, 17 complete; verdict **`NO_MEMORY_FIRST_STAGE` — STOP the preregistration candidate**
  (this is the "previous preregistration candidate was stopped" the mission refers to). Feeding shows a
  positive **dose** effect but it is not carried by the targeted memory coordinate; strong body/physical
  state survives to the probe.
- `03a909a` COUNTERFACTUAL-HISTORY-MECHANISM-RECONCILIATION-00 — verdict **`UNRESOLVED`**: the order
  state `m_minus` is a real but non-functional sign-corrected coordinate; **physical carryover (body
  mass 17/17, area, core ρ) is the leading channel**; it could not be upgraded to
  `PHYSICAL-CARRYOVER-ONLY` because the physical model did not generalise out-of-world in both arms. It
  explicitly pointed to a possible `BODY-EQUALIZATION-00` (equalise body mass/area → does the dose
  feeding contrast collapse).

Also present and to be left untouched: 58xxx DOWNSTREAM-ORDER-READER (closed, `NO_ACCESS_ESTABLISHED`),
DIRECTED-CAUSAL-PAIR (`7deeb8e`), and V5/03G artefacts.

## 3. Parent selection

Requirement: minimal **accepted** parent carrying both the exact-clone history machinery and the
qualified common-boundary continuation. The history lineage is linear off `fa26173`:
`fa26173 → 33c340e → 7deeb8e → 3823f72 → 8a690f6 → 6d1a5f7 → 4ef4bed → e504288 → ea6e6a0 → f831800 → 03a909a`.
The exact-clone machinery (`counterfactual_history_core_dev.py`) enters at `e504288`/`ea6e6a0`; the
qualified common-boundary continuation (`access_structure_operators.py`, `access_structure_noswap_operators.py`,
and the core protocol's common no-drive boundary source) is inherited from `fa26173`/`33c340e`. The
boundary-safe PHASE06A refinement (`bf5901a`) is on a *separate* branch off `fa26173` and is **not**
required (the core protocol's common-boundary continuation suffices).

**Chosen parent: `03a909a`** (`codex/counterfactual-history-mechanism-reconciliation-00`). It is the
accepted tip of the exact-clone line and contains both machineries plus the reconciled disposition
(`UNRESOLVED`, physical-carryover-leading) that scientifically motivates the Kovacs question and defines
the hidden-state candidates. The strictly machinery-minimal alternative `ea6e6a0` was considered and
rejected as the base only because it lacks the reconciliation context (which adds no execution baggage
and prevents re-deriving an accepted disposition). Both are on `origin`; `03a909a` verified at clone.

## 4. Why Kovacs, and how it differs from the pointed-at BODY-EQUALIZATION

BODY-EQUALIZATION-00 (as the reconciliation framed it) would equalise body mass/area and ask whether the
dose→**feeding** contrast collapses — a mediation question requiring surgery + residualisation, both now
**forbidden**. Kovacs instead: matches one macro-observable `Z` by **history/timing** (no surgery),
releases **probe-free** (no feeding), and tests a **dynamical autonomy** property (does matched `Z` stay
matched under identical dynamics). It answers a different, cleaner question and avoids every forbidden
move. Its establishable claim — `Z`-insufficiency + functionally-active hidden DOF — is also stronger and
more fundamental than "matching mass doesn't match area" (a static fact the DEV data already show).

## 5. Candidate-`Z` decision

Audit of already-open DEV data (`kovacs_hidden_state_candidate_z_audit.py` →
`..._CANDIDATE_Z_AUDIT.json`, 17 complete worlds): at a fixed **core-mass** match, fraction of history
variation surviving = area 0.46, shape 0.60, body mass 0.33, `m_plus` 0.996, `m_minus` 0.96 (body-mass-
referenced version — area 0.25, shape 0.57 — kept as secondary in the audit JSON).

**Primary `Z` = core-region mass** (frozen radius-10 checkpoint-centred mask): interpretable, **tracker-
free endpoint**, **identical support for both clones** (clean between-branch differencing), strong history
loading (dose 4.56), crossable. It **contains** body mass but is not equal to it — `core ≥ body`, and in
DEV core is 1.10–2.03× body (median 1.38×) — an accepted interpretability cost of the tracker-free common
support (corrected after the C1 audit finding). Refused: tracked body mass (tracker-dependent endpoint →
robustness co-observable that also flags intra- vs peri-focal divergence); body area (integer/coarse);
shape (weak, largely mass-independent → a hidden-DOF *report*); `m_plus`/`m_minus` (they *are* the hidden
coordinates); world mass / `up_ref` (environment, held common); feeding-ready (probe- and outcome-adjacent).

## 6. DEV feasibility (crossing + timing)

`kovacs_hidden_state_dev_crossing_probe.py` → `..._DEV_CROSSING.json`, 6 open worlds (first six complete-
block worlds by seed: 57001/03/06/08/09/10), 64×64 engine (~13 ms/step). Findings: overshoot-then-starve
gives a **non-monotone** mass (peak then decline) in **6/6** worlds (crossing `m*` from above is robust);
the declining branch descends into the gentle-approach value range in **3/6** (band overlap), but a
genuine **opposite-direction** crossing (approach still ascending at the shared value) is demonstrated in
only **1/6** (57003, marginal) — the gentle approach itself overshoots-and-declines in low-capacity
worlds, so opposite-direction crossing is a **Phase-1 calibration target**, not a current result.
Tolerance-level match (within `tol` at `N_min`) was **not** tested (placeholder `m*`). World mass scales
differ 2–3× and crossing times ≈2× (peaks at elapsed 133–298) → a fixed same-clock-time schedule is
**infeasible**; adopt a **frozen per-world crossing rule (option b)** with age controls. Only
matching-variable trajectories were computed — **no excursion outcome**; the engine is run on open DEV
worlds but no new namespace is opened and no design parameter is tuned from a response.

## 7. Estimand, classification, null schema

Primary estimand `D_w = K_OVER − K_APPR`, the between-history difference of reference-relative Kovacs
humps `K_b = Σ_s (Z_b(t_R+s) − Z_ref(t_ref+s))`; zero under `Z`-sufficiency; unit = source world;
unoriented gate (≥75 % common sign + 95 % t-interval excludes zero). Reference-relative humps chosen over
a bare between-branch difference to keep the classical Kovacs interpretation and blunt the
"velocity-at-match" critique. Classification `HIDDEN_STATE_SUPPORTED / Z_SUFFICIENT_NOT_ESTABLISHED /
MATCH_INVALID / UNRESOLVED` with a raw-field schema that keeps a genuine null strictly separable from an
invalid match (every match/release/sham/viability gate recorded per world; failures censor, never impute).

## 8. Dead-ends and rejected options

- Fixed same-clock-time schedule with an absolute `m*` — rejected (world heterogeneity 2–3×).
- Tracked body mass as primary `Z` — rejected (tracker-dependent endpoint; per-branch support breaks the
  clean difference); kept as robustness only.
- Bare between-branch estimand without a direct-relaxation reference — kept as a secondary; the
  reference-relative hump is primary for interpretability.
- `feeding-ready` / probe uptake as `Z` — rejected (probe- and outcome-adjacent).
- Computing any Kovacs excursion in Phase 0 — deliberately **not** done (integrity: no tuning from
  response; keeps DEV worlds unburned for the calibration/prospective phases).

## 9. Integrity firewalls maintained

No excursion outcome computed; no new seed namespace (only open 57001–57024 touched, read + matching
probe); no surgery/body-equalisation; no decoder/reader battery; no residualisation-as-causal; `Z` not
outcome-selected; all scalars frozen mechanically; V5/03G/DIRECTED-CAUSAL-PAIR/58xxx untouched; shared
indexes not edited.

## 10. Provenance

- Parent `03a909a`; DEV source `COUNTERFACTUAL_HISTORY_CORE_00_DEV_RESULTS.json` (raw SHA-256
  `d4e6f2d9…86da6`, manifest SHA-256 `298dcc02…9457`); engine equations/params from
  `M_MINUS_SIGN_DERIVATION.md`.
- New committed artifacts: `kovacs_hidden_state_candidate_z_audit.py` (+ `..._CANDIDATE_Z_AUDIT.json`),
  `kovacs_hidden_state_dev_crossing_probe.py` (+ `..._DEV_CROSSING.json`), and the seven KOVACS design
  documents. Cloud clone from `origin`; branch pushed to `origin`.

## 11. Verdict

**GO (conditional)** — advance to Phase-1 design finalisation (DEV crossing-rule calibration + power +
seal-time lock + independent re-audit) under human review. Not authorised: seal, prospective family, new
namespace, execution, ownership/identity/reconstruction claims. Phase 0 ends here.

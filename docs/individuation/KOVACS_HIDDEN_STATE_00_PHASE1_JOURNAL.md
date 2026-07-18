# KOVACS-HIDDEN-STATE-00 — Phase-1 mission journal

Branch `claude/kovacs-hidden-state-00-phase1` off Phase-0 `e76a94f` (which the user pushed to origin).
Mission-specific journal (no shared indexes edited). Autonomous execution; no excursion computed.

## 1. Scope and the Phase-1 correction

Phase 1 raised the bar: a positive excursion after scalar mass matching only shows "mass insufficient",
too weak given known physical carryover. The task: determine whether a **natural macrostate-coincidence**
(the full overt physical panel, not one scalar) is reachable without surgery/regression/transplant/tuning
— else `SCALAR_ONLY_FEASIBLE → STOP_PROSPECTIVE`. Hard firewall: no scientific excursion outcome computed.

## 2. Pilot pivot (the decisive engineering finding)

The first engine build reused the Phase-0 feed–starve overshoot crossing. Pilot (57001): **no post-turnover
mass crossing** — after the 1000-step deep turnover the overshoot transient is gone (≫ fast-memory τ≈28),
leaving a near-constant dose-carryover offset (strong branch stayed ~5.4 above the gentle branch). So an
opposite-direction crossing is not naturally reachable post-turnover (this also answers Task 4).

I pivoted to **matched total dose, different delivery pattern** (spike vs sustained): equal dose ⇒ equal
core mass at the same absolute time ⇒ a **common-clock coincidence by construction** (satisfying the Task-2
common-clock preference without variable release or age confounds). The scientific question becomes:
does the overt panel also coincide while hidden memory differs?

## 3. Architecture, panel, tolerances

Calibration/analysis clones are byte-identical replays of a single global-frozen, dose-matched schedule
(hashed before analysis); determinism proven bit-identical. The overt panel is tracker-free on the frozen
common core mask (mass, support, rg2, centroid, core N/c/uptake, collar mass/N); memory is a hidden
diagnostic only. Tolerances derive ONLY from the identical-history sham (=0) and natural DEV temporal
repeatability (3σ) — never from any excursion.

## 4. Result (17 complete DEV worlds)

- Overt panel matches ~1–2 % relative but **systematically** (spike consistently lighter/smaller/less
  energetic than sustained at matched dose). **0/17** pass the full panel at sham(0) or 3σ-repeatability.
- Hidden slow memory residual is 17/17-consistent (m2 −0.016, m_plus −0.015, m_minus +0.015; standardized
  |mean|/SD ≈ 4.6–5.0); fast memory m1 matched (noise). Timescale separation is real — but the overt
  residual is itself standardized-consistent (core_N 3.85, collar_N 3.71), i.e. a coherent overt
  difference, not just a hidden one.
- No opposite-direction crossing (dose-matched, same-direction relaxation).
- Determinism bit-identical; engine-free raw reproduction + focused tests + tracker/serialization
  self-tests all pass.

## 5. Verdict and reasoning

Frozen value gate: STRONG requires the full overt panel to coincide at tolerance; `0/17` do → not STRONG.
Matching used no future info/surgery/regression, clock time common → not MATCHING_INVALID. The protocol
reaches a close (~1–2 %) coincidence → not a "cannot approach" FEASIBILITY_FAIL. The systematic overt
residual is the limitation; the consistent memory residual does not upgrade the class (guardrail).
**→ `SCALAR_ONLY_FEASIBLE` → `STOP_PROSPECTIVE`.** Power confirms: coincidence-qualification rate 0 ⇒
STRONG prospective infeasible on attrition alone; the ≥75 % sign gate is unreachable unless `d ≳ 0.8`.

Deeper reason: with natural, surgery-free dynamics there is no free lunch — the same history difference
that writes a hidden residual also writes a coherent overt residual, so a clean "overt matched / hidden
differs" coincidence is not achievable. Surgery/transplant would achieve it but is forbidden.

## 6. Dead-ends / rejected

- Feed–starve overshoot crossing post-turnover — rejected (transient gone; no crossing).
- Upgrading to STRONG because slow memory differs — rejected (mission guardrail; overt residual is the
  limitation).
- Loosening the tolerance to pass the panel — rejected (no mechanical justification above sham/repeat).
- Reopening the order axis — out of scope (stopped line; weaker margin).

## 7. Provenance / deliverables / checkpoints

Engine `experiments/individuation/kovacs_hidden_state_phase1.py` (schedule hashed); analysis
`..._phase1_analysis.py`; engine-free reproduction `..._phase1_raw_reproduction.py`; tests
`test_kovacs_hidden_state_phase1.py`. Docs: PHASE1_COINCIDENCE_REPORT, PHASE1_DEV_RESULTS.json,
PHASE1_COINCIDENCE_ANALYSIS.json, PHASE1_CALIBRATION_SPEC, PHASE1_VALUE_GATE, PHASE1_POWER_REPORT,
FINAL_RAW_SCHEMA.json, PHASE1_FUTURE_ESTIMAND, PHASE1_PREREGISTRATION_CANDIDATE, this journal.
Checkpoints: `e877a33` (engine), `bfd9c43` (results+gate+tests), + final docs commit. Push is manual
(cloud has read-only git proxy; device_bash has no network) — bundle handed off to the device repo.

## 8. Final verdict

**`SCALAR_ONLY_FEASIBLE` — `STOP_PROSPECTIVE`.** No seal, no prospective family, no new namespace, no
excursion, no ownership/identity/reconstruction claim. Stop for human review.

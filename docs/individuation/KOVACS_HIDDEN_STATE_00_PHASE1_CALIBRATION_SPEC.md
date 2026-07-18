# KOVACS-HIDDEN-STATE-00 — Phase-1 calibration/analysis architecture spec (T1, T2)

Implementation: `experiments/individuation/kovacs_hidden_state_phase1.py`
(`schedule_sha256` recorded in the DEV results). No excursion is computed anywhere.

## 1. Calibration vs analysis clones (T1)

- **Source snapshot.** Per world, `make_checkpoint(seed)` warms the world 800 steps, selects the single
  pre-history focal target by the frozen parent rule, and serialises the complete Markov state once.
- **CALIBRATION clones** are byte-identical clones of that snapshot used only to *determine* the
  per-world coincidence (the common-clock relaxation step at which the two dose-matched histories meet).
  They never contribute an endpoint and never count toward `n`.
- **ANALYSIS clones** are **re-created independently** from the same exact snapshot and **replay the
  locked schedule** without reading or adapting to their own future trajectory. Because the engine is
  deterministic and the schedule is fixed a priori, the analysis trajectory is bit-identical to the
  calibration trajectory; the coincidence is thus a property of the frozen schedule, not of any response.
- **Schedule locking + hashing.** The schedule family (`H_SPIKE`, `H_SUSTAINED`, matched dose 2.40, deep
  turnover 1000, relaxation 180, common-clock coincidence step 90) is a single **global-frozen** literal,
  hashed with SHA-256 **before** any coincidence analysis and stamped into every world record. There is
  **no per-world outcome-dependent tuning**: the same schedule and the same crossing rule apply to every
  world, so no analysis information can leak into the schedule.

## 2. Determinism and exact schedule binding (proven)

For a world processed with `prove_determinism`, the runner re-clones the snapshot and re-applies each
history a second time, then compares the post-relaxation state SHA-256. Proven bit-identical on **2 of the
17 worlds** (seeds 57001, 57020; `prove_determinism` was run once per invocation to bound cost) and
structurally unit-tested
(`test_kovacs_hidden_state_phase1.py::test_exact_clone_determinism_and_panel_tracker_free`); the engine is
deterministic by construction (no RNG retained after init). The panel is a **pure function of
`(state, frozen core mask)`** — no per-step tracking — so the matching readout cannot drift with a tracker.

## 3. Common-clock preference (T2)

The Phase-1 design **satisfies the common-clock preference by construction**: the two histories deliver
the **same total dose** and are read at the **same absolute relaxation step**, so elapsed time and branch
age are identical for both branches and there is **no variable release time**. Equal dose and common clock
are exact; the resulting **core mass is only *approximately* equal there** (~1 % residual, not exact —
delivery efficiency differs, so this is a near-coincidence, §Report). The coincidence is read at a single
frozen common-clock step `k = 90` (robustness `k ∈ {60,90,120}`). History is **not** confounded with total
age or relaxation duration.

Consequently the option-(b) machinery (an outcome-independent crossing algorithm with branch-age,
elapsed-time, direct-relaxation and matched-waiting-time controls) is **not required** for the primary
design and was not used. It remains the documented fallback **only** if a future design abandons
dose-matching for a variable-release crossing; that fallback is not part of the current frozen protocol.

Note (Task-4 topology): post-turnover there is **no opposite-direction crossing** — both branches relax
in the same direction and coincide by dose-matching, not by a rising/falling intersection. The Phase-0
overshoot crossing does not survive the 1000-step turnover.

## 4. What is measured vs forbidden

Measured (matching + hidden diagnostic only): the overt physical panel and the memory residual at the
common-clock coincidence; matching stability over a ≤3-step look-ahead (a matching-quality check, never a
signed excursion). Forbidden and not done: any post-release excursion / Kovacs hump; any tuning of the
matching variable, target, tolerance or horizon from a response; any surgery, transplantation, regression
residualization, or decoder.

# PQEC01 — Instrumentation specification (observer-only)

## 1. Phase of record

Every field is captured at the **exact phase the parent qualified for `Q`**: immediately before
`WorldOBTC._react_core`, on the **post-diffusion, pre-reaction** state. Concretely, `PQECWorld._react`
snapshots, then calls `super()._react()`, which is what invokes `rec.pre_react` and `_react_core`.
Nothing mutates the lattice between the snapshot and the reaction.

**Step labelling.** Every PQEC01 buffer is indexed by the **pre-increment** step. `kinetics.World._one_step`
increments `self.step` after the operators run, so `post_increment_step = pre_increment_step + 1`.
Index `t` in `pq_field` is therefore the environment the reaction at step `t` actually saw. This is
proved, not assumed, in `PQEC01_INSTRUMENTATION_TESTS.json → STEP_LABEL_MAPPING`.

## 2. What is stored, and why nothing is lost

The buffer `pq_field` has shape `(T, 6, L, L)`, `uint8`, holding
`nX, nY, nSX, nSY, nWX, nWY` at every step.

Everything else the mandate names is an **exact function** of those six fields:

```
free(x,t)        = CAP - (nX + nY + nSX + nSY + nWX + nWY)
candidate_X(x,t) = min(nSX, free)
candidate_Y(x,t) = min(nSY, free)
Q_POSITION(x,t)  = nX * min(nSY, free)
```

So the six fields are a **lossless** encoding of the full ten-field mandate, at full cadence.
The cadence is **not** reduced: every scheduler step is stored. Derived fields are recomputed on
read rather than duplicated on disk — that is a redundancy reduction, not an information loss,
and the identity above is the preregistered mathematical bound proving it.

Occupancy is bounded by `CAP = 16`, so `uint8` is exact with headroom; no quantisation occurs.

## 3. Event ledgers

| ledger | columns | cadence |
|---|---|---|
| `pq_ycells` | `(step, y, x, nY, nX, nSY, free, cand_Y, Q_local)` | every occupied Y cell, every step |
| `pq_ybirth` | `(step, y, x, n_born)` | every Y birth |
| `pq_ydeath` | `(step, y, x, n_died)` | every Y death |
| `pq_yhop` | `(step, sub, shift, axis, y_from, x_from, n_accepted)` | every accepted Y hop, per frozen sub-shift |
| `pq_xevent` | `(step, n_X_born, n_X_died)` | every step |
| `pq_capacity` | `(step, species, hops_offered, hops_blocked)` | every species, every step |
| `pq_exchange` | `(step, dSX, dSY, dWX, dWY)` | every step, across `_feed_and_outflow` |
| `pq_src` | `(step, sub, species, y_before, x_before, y_after, x_after)` | organiser trajectory, per sub-step |
| `pq_stephash` | `(step, engine state_hash)` | every step |

`pq_ycells` is redundant with `pq_field` **by construction**; that redundancy is deliberate and is
used as a differential cross-check (`OBSERVER_OUTPUT_SEMANTICS`), not as extra information.

## 4. Lineage labelling — what is NOT claimed

The engine's reaction is **aggregate**: `births = rng.binomial(min(nSY, free0), min(1, kY·nX·nY))`
is drawn per cell, not per particle. When two or more `Y` occupy the same cell, the engine does
not identify which one "produced" a birth, **and neither does this observer**.

- No biological parent is invented.
- Where a birth cell holds more than one `Y`, the ledger records the cell and its occupancy; the
  admissible parent set is the whole occupancy of that cell — `SHARED_PARENT_POOL`.
- Lineage labels, where used in analysis, are **observer-only bookkeeping** derived after the run
  from positions and events. They consume no engine RNG and are never part of the physical state.
- Physical state (`pq_field`) and observer labels are stored in separate objects and never mixed.

## 5. The one place physics lines are duplicated — declared

`PQECWorld._diffuse` re-implements the engine's four frozen sub-shifts **verbatim** for species
`Y` only, because the per-sub-step `accepted` array is the only place an exact hop origin and
destination exists, and the base method does not expose it. This is the highest-risk part of the
instrumentation. It is checked two independent ways:

1. **normalized source-text equality** against `engine_obtc.WorldOBTC._diffuse`, with exactly one
   declared difference (an `enumerate()` wrapper that supplies an observer-only sub-shift index and
   consumes no RNG);
2. the **differential bit-exactness test** below.

For every other species the base method is called unchanged.

## 6. Qualification — inertness is proven, not asserted

`NON_SCIENTIFIC_INSTRUMENTATION_FIXTURE`: `L = 5`, 8 steps, seeds `77000001–77000010` — a band
disjoint from every scientific register in this programme. No scientific seed, no scientific
domain, no full scientific horizon is used.

An instrumented and an uninstrumented world are advanced side by side and required to agree
**bit-for-bit at every step** on:

- the six physical species fields;
- **all three** engine bit-generator states — `World.rng`, `WorldV2.rng_feed`, `Tracker.rng`;
- scheduler counters (`step`, `hops_offered`, `hops_blocked`, `births_total`);
- the engine's own `state_hash()`.

The fixture grid spans `kY ∈ {0, 0.30, 0.45, 0.60, 0.90}` and `muY ∈ {0, 0.02, 0.05, 0.10, 0.20}`
so that Y births, deaths, hops and multi-occupancy actually occur — a test on an inert `kY = 0`
world would prove nothing about the Y path. One fixture repeats with field recording disabled, to
show the buffer itself is not load-bearing.

**If any of this fails, the mission stops before scientific runs with `CALIBRATION_TECHNICALLY_INVALID`.**

## 7. Resource probe — declared, non-scientific, outcome-blind

Sizing the frozen design required knowing the wall time and compressed size of one world. A
`NON_SCIENTIFIC_RESOURCE_PROBE` was run at `L = 36` on seed `77900001` (non-scientific band) for
**500 steps** — not the scientific horizon — and only two numbers left it: **seconds** and
**bytes**. No outcome array was read, no scientific seed was opened, and it contributes **zero**
outcome-informative starts. Measured: ~29 s and ~9.3 MB (delta + zlib) per 11 000-step world, at
an instrumentation overhead of ×1.12. Those two numbers, and nothing else from that probe, entered
the sample-size arithmetic.

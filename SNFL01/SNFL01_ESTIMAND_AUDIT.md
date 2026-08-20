# SNFL01 — ESTIMAND AUDIT

## What `I/I0` is, exactly

`dr05_flux_decomposition.py` (sha256 `d7fbe914…`), line 107:

```python
"I_over_I0_treated": It / I0,   "I_over_T_treated": It / Tt,
```

with, at line 78, `M = num(r["M256"]); I0 = num(r["I0"])` — `I0` is read **per row**, i.e. per
`(size, block, arm)`. It is the block's own incumbent mass at `t256`. It is **not** a global constant,
**not** analytic, and **not** recomputed per condition.

**Denominator audit (recomputed by this mission, 0 runs).** For each of the 18 `(size, block)` pairs,
`I0` was compared across all seven arms: **0 of 18** blocks show a non-identical `I0`. The denominator
is therefore per-block but arm-invariant, and historical arm comparisons are denominator-consistent.
Any successor must keep this rule frozen: `I0` = the block's own `t256` incumbent mass, never pooled
across blocks, never recomputed per condition.

## The target is a joint endpoint

`direct_replacement_protocol.json` (sha256 `85d37725…`):

```
/endpoints/FORCED_COMPONENT_TURNOVER_80 = ["I/I0 <= 0.20", "I/T <= 0.20"]
```

**Both** must cross. This settles §8's question about the two historical values — but not in the way
the mission's framing assumes. `0.385` and `0.419` are **not** two contexts of one condition. They are
the **same endpoint at two different lattice sizes**:

| | L = 24 | L = 32 |
|---|---|---|
| `I/I0` at Q100 (×1) | 0.593736 (n = 9) | 0.660552 (n = 9) |
| `I/I0` at Q800 (×8) | **0.385416 (n = 2)** | **0.418707 (n = 9)** |

The L=24 figure is **survivor-conditioned**: of its 9 blocks, **7 carry `TREATED_TRACK_LOST`**. Its
median rests on two worlds, `[0.3682, 0.4027]`. The L=32 figure rests on all nine. Pooling them into
"a plateau near 0.385/0.419" merges a complete measurement with a two-survivor remnant at a different
size.

## No prior size-normalized estimand exists

A search for `I/(I0·|E|)` or any per-eligible-cell flux returns nothing. §4 forbids inventing one
merely because the mission is named "size-normalized", so **no secondary normalization is defined here.**

## The cardinality distribution §5 needs does not exist yet

Only a single scalar survives — `median_eligible_sink_sites_per_event: 1` in
`dr05_mechanism_adjudication.json` (sha256 `4f3fe96c…`). The minimum, mean, maximum, and the fractions
with `|E| = 0` and `|E| = 1` that §5 requires are **not** in any artefact.

They are, however, **recomputable with zero engine runs** from P07's surviving per-event ledgers
(`P07/p07a_event_ledger.csv.gz`, `P07/p07b_event_ledger.csv.gz`). That is the single most useful thing
a successor can do, and it is the core of the handoff.

## Independent unit

`direct_replacement_protocol.json`: `"inference": "n = 9 independent blocks per size, one LawSpec"`,
and explicitly `"forbidden": "144 logical trajectories must NEVER be reported as n = 144 independent"`.
The primary endpoint is a **median over blocks**, so any successor must use the pre-existing median
definition with a paired world-level interval — not a mean.

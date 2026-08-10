# MATERIALITY_SEMANTICS_AND_UNITS

## Three concepts that must not be merged

| symbol | what it is | what it is not |
|---|---|---|
| `ETA_ORACLE_L2` | a deterministic upper bound on the arithmetic of reading, subtracting and reloading serialized states | a stability bound on the engine dynamics; a noise estimate |
| `TAU_DYNAMIC_L2` | one percent of how far the untreated system moves on its own, measured in the estimand's own norm | a variance, a standard error, or anything estimated from replicates |
| `TAU_SITE_L2` | one percent of one representative baseline-support site's density, propagated through the reader and the scored grid | a detection limit derived from data spread |

`TAU_MATERIAL_L2 = max` of the three. The first is a **numerical detectability** floor; the second
and third are **scientific** floors. Reporting only the first and calling it materiality is the
specific failure this programme exists to avoid, and it is declared a stop condition
(`MATERIALITY_SEMANTICS_UNDEFINED` / `NUMERICAL_DETECTABILITY_RULE_ONLY`).

## Why two identical shams cannot found a threshold

The engine is bit-deterministic. `SHAM_0` and `SHAM_1` start from identical bytes and must produce
identical trajectories. Their agreement proves the pipeline replays; their difference would be a
defect, not a draw from a noise distribution. A threshold built from their spread would be exactly
zero and would declare every arithmetic wobble material. That is why the scientific floors are
built from the sham's own *evolution* and from a *declared* one-site effect, both of which exist
before any intervention and neither of which depends on a response.

## Response independence

Every input to every threshold is one of: the immutable t0 masks, the normalizer `B`, the baseline
density at `h0`, the `SHAM_0` trajectory, the frozen weights, the datatype, and static panel
coefficients. No carrier or environmental array is reachable by the threshold pipeline; that is
enforced by a dependency audit, not by intention.

## Units

Everything is in units of `rho` integrated over a fixed grid region and divided by `B`, then
weighted by `sqrt(w_h)` and collected in L2. The inherited `A_bu`/`ETA_bu` are weighted **L1** in
the same base units, which is precisely why GIMB00 could not use them; nothing here converts
between the two norms.

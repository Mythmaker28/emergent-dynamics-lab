# SHIP_OF_THESEUS_E1_E2_SPEC.md

**E1 and E2 are different experiments and must never be conflated.** EXP-GT-00's challenge (e) was an E2
masquerading as an E1, and it produced a nonsense verdict: the observer scored a component replacement as *further
away* than a different program (1.518 vs 1.213), i.e. it mistook constituent turnover for a new individual — the
exact confusion the whole research programme is about (D-048, D-049).

## E1 — FUNCTION-PRESERVING HANDOFF (the real Ship-of-Theseus gate)

A component is replaced by a functionally equivalent but **microscopically distinct** instance. The relief is
installed **before** the incumbent is removed, so the machine is never unmanned.

**Expected vector: A = SAME, S = SAME, F = SAME, L = SAME, M = DIFFERENT.**

**Three executable assertions, all of which must hold:**

1. the microtrajectory genuinely **CHANGED** (not a silent no-op — EXP-GT-00 shipped one that restored the grid
   exactly and "passed" at distance 0.0000);
2. the old component is genuinely **GONE** and the new one is genuinely **PRESENT and operating**;
3. the input-output behaviour is **IDENTICAL AT EVERY TIMESTEP. No silent interval.**

**Measured (EXP-GT-03):** 764 frames differ; 0 incumbent cells remain; the relief establishes 7/7 cells; I/O
identical at every timestep. **The handoff is non-vacuous and F, L, M all report correctly (SAME, SAME, DIFFERENT).**

**A DELAY-PRESERVING E1 IS NOT CONSTRUCTIBLE IN THIS COMPONENT LIBRARY, and this is a finding, not an excuse.**
The handoff that *can* be built installs the relief 12 rows upstream. That **changes the component's causal delay to
the output** (measured 184 → 229). A delay is part of the causal graph — the mission requires `A` to resolve delay
edits down to 4 steps — so **a handoff that MOVES a component is an architectural change, and `A` is right to call it
DIFFERENT.** The case as built is a **DISPLACED handoff**, not an E1.

A true E1 needs an **in-place** material swap: a different absorber occupying the *same* track position with the
*same* delay. The only clean unseen absorber found (the LOAF) is a **reactive seed**, not a still life — a glider
must consume it and the reaction settles into the absorber — so it cannot be installed into a running stream (swept
over a full gun period: no install time works). **Required capability of the next component library.**

## E2 — DAMAGE AND REPAIR

A component is destroyed and later rebuilt. **F may transiently BREAK** while lineage remains continuously
observable; recovery is measured **separately**.

**Expected: A = SAME, S = SAME, F = BROKEN-then-restored, L = SAME, M = DIFFERENT.**

**Measured (EXP-GT-03):** the I/O is broken for **264 timesteps** and the function **recovers** (tail rate 2.6667 =
control). Recovery is judged on the **phase-invariant rate**, not on bit-equality: a rebuilt gun restarts at a new
clock phase, so a repaired machine can never be bit-identical to the control — and demanding that it be would define
recovery out of existence.

**E2 IS NEVER THE SHIP-OF-THESEUS EQUIVALENCE GATE.**

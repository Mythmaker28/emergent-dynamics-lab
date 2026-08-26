# CLEA01 — CAUSAL GRAPH DEFINITION

## Permitted inputs

Y-occupied cell coordinates, nY per cell, the three event ledgers, pre/post-intervention physical
states, toroidal geometry, the frozen reaction and event order, and the locked daughter cells at the
fork.

## Edge types

| edge | from → to | set-valued? |
|---|---|---|
| persistence and transport | every Y-occupied cell within Moore-1 on row *t* → occupied cell *d* on row *t+1* | yes |
| accepted local Y birth | the Y present at *d* at react time → the birth recorded at *(t+1, d)* | only via transport |
| local X production | the same Y-bearing state at *d* → the X birth at *(t+1, d)* | only via transport |
| removal terminates causal mass | the Y at the removal cell → nothing | no |
| split | one-to-many transport; does not terminate the lineage | — |
| merge | many-to-one; POSSIBLE but not CERTAIN | — |

No molecular genealogy is invented anywhere. Where the physics does not determine ancestry the
bracket widens; it is never resolved by preference.

## Two implementations — and what G2 actually tests

`clea01_lineage_i1.py` enumerates `S(d)` with Python sets over nine explicit offsets.
`clea01_lineage_i2.py` computes the same set by boolean morphology:
`certain(t+1) = occ(t+1) & dilate(certain(t)) & ~dilate(occ(t) & ~certain(t))`.

**Corrected by the checker.** I claimed they share "no code". That was false — about 28 non-trivial
lines are identical (ledger parsing, flood fill, archive extraction, loop skeleton, accounting,
output). **G2 tests the propagation operator only**; archive reading, event labelling, horizon
handling and exposure accounting are common-mode.

The gap was closed another way: the checker derived the row cadence and event-label convention from
the engine source, and wrote a **third** implementation from the rule text alone — neighbour counting
with modular index tables, no `np.roll`, no set-subset test — which reproduced all 13 quantities on
all 66 arms with **zero disagreements**.

The morphological form equals the set form **given** `CERTAIN(t) ⊆ occ(t)`, which the pipeline
maintains by construction. My sketch omitted the condition. The checker verified the equivalence on
4000 random configurations (0 mismatches) and then broke the precondition deliberately on 2000 more
(2000 mismatches).

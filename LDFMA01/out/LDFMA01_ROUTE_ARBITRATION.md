# LDFMA01 — ROUTE ARBITRATION

```
1. Prefer Route A when a matched-control design is scientifically aligned, non-arbitrary
   and decision-capable.                                    -> A fails on decision-capability
2. Select Route B only when Route A fails and one minimal architecture change directly
   targets an identified mechanism.                          -> no candidate targets it
3. Otherwise pause.                                          -> SELECTED

SELECTED_ROUTE = ROUTE_C__PAUSE
```

| criterion | Route A | Route B | Route C |
|---|---|---|---|
| scientific alignment | E1-corrected aligned; E3, E5 not | none targets the measured mechanism | — |
| clarity of estimand | clear | clear | — |
| ability to falsify | only near-total suppression at 22 pairs | would falsify an unsupported hypothesis | — |
| independence from post-hoc thresholds | E1-corrected needs a repair found after the outcomes | B2, B3 need a swept value | — |
| world cost | 512 arm instances → ~22 pairs | 512 worlds | **0** |
| implementation risk | low | high — substrate change on an artefact | none |
| risk of another loop | **high** — underpowered NOT_REPLICATED | very high — uninterpretable | low |

The two candidates with *more* statistical power, E3 and E5, were rejected on **alignment**, not
power. That is deliberate: the launcher forbids choosing a route because a paired continuous
contrast is easier to move.

## A vocabulary gap, reported rather than resolved by invention

The evidence reached a state the frozen terminal set does not name: **the mechanism IS identified**
— quantitatively, and by a third independent reconstruction — **and no route is eligible**. The
four frozen terminals pair `MECHANISM_IDENTIFIED` with an eligible route, or pair a pause with
`NOT_IDENTIFIABLE`. No fifth disposition is permitted, so the pause terminal is used for its
**pause** half, and this note records that its `NOT_IDENTIFIABLE` half **understates the result**.

The mechanism is named in `LDFMA01_FAILURE_PARTITION.json` and
`LDFMA01_AMBIENT_SATURATION_MECHANISM.json`. Read it there, not from the terminal string.

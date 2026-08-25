# LDFMA01 — ROUTE B: MINIMAL ARCHITECTURE CANDIDATES

An architecture change is evaluated only if the funnel identifies a mechanism the unchanged
architecture cannot test cleanly. **That precondition is not met**, and the reason is the central
result of this mission.

## The mechanism is not in the architecture

Inside the 22 locked daughters the decay rate predicts **8.44** Y removals over **11 385**
particle-steps. **Eight of them are present in the ledger.** Every daughter survived them — **0 of
22** went extinct; all 22 identities ended by `SPLIT_OR_TIE`.

The frozen endpoint counts **one**. It asks whether the event cell is in the component's cell set
*at step t*, while the archive writes cell rows *after* the step — so a decay that empties a cell
is invisible to it. Attributing the identical ledger rows one step earlier recovers 8 of the 8.44
the decay rate predicts, and **5 of 22 worlds would read COMPLETE instead of 1**.

**The physics already produces locked-daughter constituent turnover. The measurement does not see
it.**

## The three candidates, and why each fails

| id | change | fails on |
|---|---|---|
| B1 | occupancy-floored Y removal (spare the last constituent) | targets a failure never observed — the removals happen and the daughters survive them |
| B2 | occupancy-dependent Y birth throttling | the ambient bloom arrives 706–2 614 steps *after* the removal and cannot change the daughter's fate; and no single throttling rule is derivable without a sweep |
| B3 | local cohesion regulation to stop splits | `p_hop_Y` is a frozen executed value; making it state-dependent needs a swept value, and suppressing splits inflates the denominator of the endpoint being tested |

No new species and no particle genealogy was considered. `X_LAWSPEC_BASELINE = UNCHANGED`.

## What would be justified, and is not authorised here

An **instrumentation** repair: record each ledger event with the component membership it had at the
moment it occurred. That changes no law, no parameter and no classifier. It is not an architecture
change, it is not authorised by this launcher, and **no handoff is emitted for it**.

Changing the physics to repair a measurement defect would be the worst available move: it would
alter the substrate on the strength of an artefact, and any apparent improvement would be
uninterpretable.

```
ROUTE_B_CLASSIFICATION        = NO_MINIMAL_CHANGE_JUSTIFIED
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED
```

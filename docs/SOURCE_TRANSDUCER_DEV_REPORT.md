# SOURCE-TRANSDUCER OBSERVER — DEVELOPMENT REPORT

`EXP-GT-SOURCE`, development circuits only. **20/20.** The burned `xnor_and`/`and_or` worlds were never consulted;
the failure that retired the previous design was reproduced *abstractly*, by circuits built from scratch, so that
the fix addresses the **class** of error and not the instance.

| | case | result |
|---|---|---|
| S1 | three taps, **two sources** (the D-065 failure, abstractly) — `dup_same` | 3 taps, 2 causes, table AND, coverage 1.0 |
| S2 | the 3-tap AND **is** the one-cell AND at the macro level | iface SAME, untimed SAME, timed DIFFERENT, micro DIFFERENT |
| S3 | `SAME_SOURCE_DIFFERENT_TAP` fires (two taps, one cause) | 1 tap pair traced to a single root |
| S4 | one macro transducer across 6 microscopically distinct machines | all untimed SAME; micro sizes 1–4 cells |
| S5 | one source at **two lags** → finite-history transducer | clock lags [14, 16], coverage 1.0 |
| S6 | direct **+ inverted-delayed** taps are still one source | 2 sources |
| S7 | stateful module → `FINITE_STATE`, **no table invented** | `toggle`: 1 ambiguous row, table = None |
| S8 | two registers, **byte-identical baseline series**, stay independent | 3 sources, all pairs INDEPENDENT |
| S9 | common hidden clock + two enables | 4 taps, 3 sources, clock at 2 lags |
| S10 | `DEPENDENT_COMMON_CAUSE` fires | `cascade`: one tap is a function of the other's cause |
| S11 | `UNRESOLVED` fires when no intervention separates | synthetic deaf world |
| S12 | partial manifold reported honestly | 4/8 rows, coverage 0.5, not rounded up |
| S13 | identical on the manifold, different off it → **INDETERMINATE, not SAME** | `lag8_and` vs `lag8_or` |
| S14 | a difference the world **can** produce is found, not abstained from | `lag15_or` vs `lag15_xor`: byte-identical free-running output, separated by clamping the source |
| S15 | different functions stay DIFFERENT | OR ≠ XOR |
| S16 | `AND(x,x)` is no transducer | 0 regions |
| S17 | active clock-correlated decoration rejected | 6/6 cells seen, all conductors, 0 regions |
| S18 | wire bundle: 3 active geometric neighbours, one cause | conductor, 0 regions |
| S19 | `INDETERMINATE` when the joint assignment is not enumerable | 7 sources |
| S20 | context-gated path recovered with the gate held shut | sources 2, table AND, coverage 1.0 |

Every criterion was shown able to **fire**, to **fail**, and to **abstain**.

## The flaw in this certificate, visible only afterwards

**Every case above inspects channel 0.** Channel 0 is the channel nearest the clock — the only one whose source lag
falls below the settle margin, and therefore the only one on which the negative-index defect of `harvest()` cannot
bite. Twenty cases, three channels available, one channel examined.

A certificate that exercises one third of the ground truth it has is not a certificate. It is a demonstration.

# FEEDBACK_CAUSALITY_REPORT.md

**Status: ACHIEVED.** Substrate: spatially embedded Boolean network.

## Why Game of Life could not do it

A causal cycle needs a component whose state depends on another whose state depends on it. **Guns are sources.**
In every measured V4 tomography the component→component dependency graph had edges **out of** guns and **none
into any gun** (D-059). A cycle needs an edge *into* a source. And two mutually-inhibiting glider streams do not
latch: **annihilation is symmetric**, so both go off. There is no bistable pair.

## The construction

Two genuine directed cycles:

1. **The register's self-loop.** `next = we ? data : self` — its next state depends on **its own** state.
2. **A ring of three inverters** — a second, oscillating cycle. It lifts the world's fundamental period from
   **8 to 24** (measured), which is itself an observable consequence of the cycle.

## The intervention proof — and the check that nearly ruined it

> **A transient perturbation of a memory has a PERMANENT effect. A feed-forward path forgets.**

Measured, with a **one-step** clamp (an intervention proved non-vacuous):

| target | output differs at | still differing at the end of the episode |
|---|---|---|
| **REGISTER** (a cycle) | 9 steps | **YES — permanent** |
| **WIRE** (feed-forward) | **1 step** (a single blip) | no — forgotten |

**The non-vacuity check itself had an off-by-one.** It inspected the state *before* the clamped step, so it
certified a clamp of `0 → 0` as non-vacuous — a **silent no-op** — which produced a beautiful, meaningless
"feed-forward" result of *zero* effect. *An intervention that does not change its target is not evidence of
anything, and a non-vacuity check that is off by one is worse than none, because it looks like rigour.*

## Distinguishing feedback from feed-forward with matched short-term outputs

The clock-driven combinational path and the register both produce a periodic output. Over a **limited episode**
they can be made to agree. They are separated **only** by the intervention above: **transient in → permanent out**
is the signature of a cycle, and nothing else in the world produces it.

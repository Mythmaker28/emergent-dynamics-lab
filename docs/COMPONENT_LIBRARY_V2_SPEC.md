# COMPONENT_LIBRARY_V2_SPEC.md

**Preregistered before any V2 result.** V4 and the admission layer are FROZEN throughout. This is a
**benchmark-construction** task, not an observer-repair task.

## The three questions the current library cannot ask

| | why it is not constructible in the Game-of-Life library |
|---|---|
| **1A. program ≠ architecture** | A memory bit of 0 is implemented by **adding an eater**. Setting a bit adds a node and two edges: **the program IS the architecture.** EXP-GT-02B's program-invariance pass was therefore **VACUOUS** (D-055). |
| **1B. feedback** | A causal cycle needs a component whose existence/state depends on another whose existence/state depends on it. **Guns are sources and depend on nothing.** The only dependent structure found — the collision remnant — depends on *both* guns and nothing depends on it (measured, D-059). Two mutually-inhibiting glider streams do not latch: they **annihilate each other**, so both go off. There is no bistable pair. |
| **1C. held-out implementation** | Every candidate clears exactly one of two bars. BOAT / SNAKE / BEEHIVE absorb in isolation and **destroy the neighbouring channel** in context. LOAF / EATER2 pass behaviourally (EATER2 reproduces the development gate's output **bit-for-bit**) and fail admissibility: both are **reactive seeds**, not still lifes, so their declared component is **empty at settle** (D-060). |

## The preregistered decision rule

Run **one** development cycle attempting all three in Game of Life. Record the outcome. Then, per the mission:

> *"If the Game-of-Life library cannot express these properties after one preregistered development cycle, record
> the limitation and autonomously choose a second ground-truth computational world … Do not weaken the requirements
> merely to remain in Game of Life."*

**The requirements will not be weakened.**

## The second world: a SPATIALLY EMBEDDED BOOLEAN NETWORK

Chosen because it makes all three constructible **exactly**, while preserving everything the observer relies on:
a discrete synchronous microscopic state, propagating signals, a clock, spatial embedding, stationary components,
exact hidden ground truth, and clamp interventions.

| requirement | how the substrate provides it |
|---|---|
| **program ≠ architecture** | **memory is a REGISTER cell with a self-loop** (`next = we ? data : self`). The **wiring is fixed**; the **program is the registers' initial contents**. Four programs, one graph. |
| **feedback** | a register's self-loop **is** a directed cycle; a ring of inverters is a second, oscillating one. Breaking one edge provably destroys the recurrence. |
| **held-out implementation** | one function, two microscopically distinct realisations — e.g. `AND` as a single gate cell vs. `NOT(OR(NOT a, NOT b))`. Different cells, different microtrajectories, **identical logical function**. |
| **delays** | a signal advances one cell per step, so **path length *is* delay**. Re-routing a wire is a pure `A_TAU` edit with `A_TOPO` fixed. |
| **component separation** | components are placed with a declared minimum gap; separation is a **construction parameter**, not an accident. |

The **causal ontology is unchanged**: `A_TOPO / A_TAU / G / S / F / L / M`, never composited; the observability
contract, the admission layer, and the whole-component / phase-quotient discipline all carry over verbatim.

## Qualification bar for every circuit admitted to the library

1. positive functional control (it computes what it claims);
2. negative functional control (a criterion that cannot fail is not a criterion);
3. intervention non-vacuity (every declared intervention provably changes its target);
4. exactly matched observation windows;
5. **two independent paths to the causal graph** — declared-from-wiring and measured-by-intervention — which must
   agree edge-for-edge, or the circuit is **rejected**, not patched;
6. stable operation over the declared clock window (exactly periodic);
7. phase coverage;
8. component separation ≥ the certified limit;
9. no hidden dependence on evaluator labels anywhere in the observer path.

# BENCHMARK CARD — what this observer can and cannot identify

**As of D-056 (2026-07-13). EXP-SC-01 remains BLOCKED.**

## What it is

A ground-truth metrology lab on a Game-of-Life computational hierarchy (guns → channels → gates → memory → FSM).
The **evaluator** holds component locations, the causal graph, the memory word, I/O and program identity. The
**observer** receives only raw cell trajectories, the right to intervene, and the declared output line.

Identity is **factorized** into `A` (causal architecture), `S` (program/memory state), `F` (functional I/O), `L`
(lineage), `M` (material continuity) and `G` (geometric embedding, auxiliary). **They are reported separately and
are never composited into a scalar.** A scalar identity score is what failed in D-048 and it is banned.

## CAN identify (certified on development, EXP-GT-A-CERT / D-055)

| capability | certified |
|---|---|
| **Causal architecture as a graph** — isomorphism-aware, layout-free, translation-free | yes |
| smallest detectable **delay edit** | **4 steps** (the finest the substrate admits) |
| smallest detectable **edge edit** | **1 edge** |
| smallest detectable **node edit** | **1 node** |
| **redundancy** change (1-path vs 2-path) | yes |
| **same function, different mechanism** — a memory gate vs a cross-stream inhibitor producing a **bit-identical output series** | **A = DIFFERENT** |
| **emergent edges** no wiring diagram declares (a shielding edge) | recovered blind |
| invariance to clock phase, translation, spacing, inert decoration, decoy gates | false-DIFFERENT **0/8** |
| **abstention** when a live output has no discovered cause | fires correctly |

**Held out (EXP-GT-03), still passing prospectively:** translation, layout change (sp48 vs sp43), inert
circuitry, decoy gates, a delay edit on an **interior** channel (impossible in the development layout), node
addition (six channels), exact copy, and `L` on all three regimes (SAME / DIFFERENT / **INDETERMINATE**).

## CANNOT identify — stated, not hidden

1. **`A` is NOT yet phase-invariant on unseen phases. FAILING.** The delay estimator strikes at phases
   (0, 15, 30, 45) and takes the earliest onset. The development phase-null used **the same four phases**, so it
   could never detect that the strike grid is too coarse. On held-out phases (7, 22, 37, 52) every delay shifts
   214 → 222 and `A` reports DIFFERENT on a pure phase shift. **A null that cannot fire is not a null.**

2. **`A` OVER-ABSTAINS.** It returns INDETERMINATE if **any** intervention is confounded, even when coverage is
   complete. The observability contract says a confounded intervention is *excluded from the evidence* — the code
   invalidates the whole graph instead. It therefore abstains on held-out cross-inhibitor circuits whose collision
   remnant cannot be cleanly ablated, **even though it recovered the correct graph.**

3. **`A`'s invariance to a PROGRAM change is NOT CONSTRUCTIBLE on this substrate.** A memory bit of 0 is
   implemented by *adding an eater*: **the program IS the architecture.** Any "pass" is a test that cannot fire —
   and **EXP-GT-02B's program-invariance PASS is VACUOUS** (it compared channel positions, which no program can
   move). Requires a substrate with **state-based memory** (a latch or storage loop). **Required property of the
   next benchmark.**

4. **A delay-preserving Ship-of-Theseus (E1) is NOT CONSTRUCTIBLE here.** A handoff that *moves* the component
   changes its causal delay (measured 184 → 229), which is a genuine architectural change — `A` is right to call it
   DIFFERENT. An in-place material swap needs a second absorber occupying the same track position; the only clean
   unseen absorber found (the LOAF) is a **reactive seed**, not a still life, and cannot be installed into a running
   stream. What IS demonstrated: a **displaced** handoff with `F = SAME`, `L = SAME`, `M = DIFFERENT`, I/O identical
   at **every** timestep, non-vacuous (764 frames differ).

5. **Component separation ≤ 4 cells.** Matter closer than this merges and cannot be resolved.

6. **`S` and `F` are extensionally equal in this family** (disclosed since D-052): the memory word fully determines
   the I/O relation and nothing else does. Their agreement is a property of the benchmark, **not** evidence that the
   heads are independent. The one case that breaks the entanglement is gate-vs-inhibitor: `A = DIFFERENT` while
   `S = SAME` and `F` is bit-identical.

7. **No validated held-out COMPONENT IMPLEMENTATION.** Of the still lifes searched, BOAT, SNAKE and BEEHIVE all
   "absorb and survive" **in isolation** and then **destroy the neighbouring channel** in the real circuit. The LOAF
   is clean but is a reactive seed whose declared graph does not match the dynamics — **rejected by the benchmark's
   own admission criteria.** A component validated in isolation is not a validated component.

8. **Never tested:** hierarchical blind discovery (EXP-GT-HIERARCHY-00) and transfer to a second substrate. **The
   observer has never been shown to discover a hierarchy it was not told the shape of.**

## Verdicts

| gate | verdict |
|---|---|
| EXP-GT-A0 (ontology audit) | **FAILED — ONTOLOGY** (benchmark-label error; D-052's repair withdrawn) |
| EXP-GT-A-CERT (development) | **QUALIFIED** |
| **EXP-GT-03 (held-out, frozen)** | **FAILED — IMPLEMENTATION** (3 head failures: phase invariance, over-abstention ×2) |
| EXP-SC-01 (droplets) | **BLOCKED** |

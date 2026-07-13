# BENCHMARK CARD — what each head can and cannot identify

**As of D-060 (2026-07-16). Architecture head V4. EXP-SC-01 remains BLOCKED.**

## The ontology

Identity is **factorized** and the factors are **never composited into a scalar** — a scalar is what failed in D-048.

| head | question |
|---|---|
| **A_TOPO** | causal **topology**: nodes, directed edges, excitatory/inhibitory role, redundancy, component→component dependency — **modulo graph isomorphism**. Carries **no delays and no geometry**. |
| **A_TAU** | causal **timing**: the phase-resolved delay structure of those edges. Compared **only after the topology matches**. |
| **G** | **geometry**: layout, spacing, routes. Auxiliary. **Never composited. G is not identity.** |
| **S** | program / memory word (the certified D-051 probe, preserved exactly) |
| **F** | functional I/O relation (per-output-node, phase-invariant by construction) |
| **L** | lineage (SAME / DIFFERENT / **INDETERMINATE**) |
| **M** | material continuity — **deliberately allowed to differ while A, S, F and L stay SAME. That is the Ship of Theseus.** |

## CAN identify — certified (D-059) and **prospectively confirmed on a third fresh hold-out split** (D-060)

| capability | status |
|---|---|
| causal topology as a graph — isomorphism-aware, layout-free, translation-free, **phase-free** | ✅ |
| smallest **edge** edit / **node** edit | **1 edge / 1 node** |
| smallest **delay** edit, **ungated** path | **4 steps** (the finest the substrate admits) |
| smallest **delay** edit, **gated** path | **8 steps** — *V3 could not do this at all* |
| **redundancy** (1-path vs 2-path) | ✅ |
| **same function, different mechanism** — a memory gate vs a cross-stream inhibitor with a **bit-identical output series** | **A_TOPO = DIFFERENT** |
| **emergent** edges no wiring diagram declares (a shielding edge; a collision remnant that is a *product* of two guns and causally inert) | recovered blind |
| invariance to clock phase, translation, spacing, inert decoration, decoy gates | false-DIFFERENT **0** |
| **E1** Ship-of-Theseus handoff | `A_TOPO=SAME, A_TAU=DIFFERENT, G=DIFFERENT, F=SAME, M=DIFFERENT, L=SAME` |
| **E2** damage-and-repair (never the equivalence gate) | breaks F, recovers |
| **abstention** when a live output has no discovered cause | fires |

**The design principle that earned this:** *do not integrate out the nuisance — quotient by it.* Timing is the whole
phase-resolved profile `τ(φ)`; a global phase shift is a **common cyclic rotation** of every profile, so invariance
comes from the **group quotient**. A *relative* timing shift is not a group element and therefore survives. V3 made
timing phase-invariant by **averaging** over phase, and thereby integrated out the signal along with the nuisance.

## CANNOT identify — stated, not hidden

1. **No scope self-check.** The head declares a **component-separation limit of 4 cells** but **does not verify the
   data respect it**. Two components closer than that are silently **merged**, and it emits a confident verdict where
   it should abstain. **A required property of the next head.** (Every benchmark case is now guarded by an executable
   scope assertion.)
2. **Program-invariance of `A` is NOT CONSTRUCTIBLE** on this substrate: a memory bit of 0 is implemented by *adding
   an eater*, so **the program IS the architecture**. EXP-GT-02B's program-invariance pass is **VACUOUS**. Requires
   **state-based memory** (a latch/storage loop).
3. **Feedback is NOT CONSTRUCTIBLE**: no causal cycle exists in this component library (guns are sources). The head
   *does* read component→component dependency and would see a cycle if one existed.
4. **No held-out COMPONENT IMPLEMENTATION.** BOAT/SNAKE/BEEHIVE absorb in isolation and **destroy the neighbouring
   channel** in context; LOAF/EATER2 are **reactive seeds** whose declared component is empty at settle. Requires a
   **still-life** absorber, distinct from EATER1, whose declared footprint is its settled footprint.
5. **`S` has a declared scan window** (columns 20–200). Layouts whose channels fall outside it are **OUT_OF_SCOPE** —
   neither a pass nor a failure, but an identifiability statement.
6. **10% of clock phases make a box-ablation unusable** (it clips an in-flight glider and leaves a block). V4 grades
   validity **per phase**, so this costs those phases and not the circuit — but the probe is still destructive.
7. **NEVER TESTED: hierarchical blind discovery** (EXP-GT-HIERARCHY-00) and **transfer to a second substrate.**
   **The observer has never been asked to discover a hierarchy it was not told the shape of.** That is the real target.

## Verdicts

| gate | verdict |
|---|---|
| EXP-GT-A0 — ontology audit | **FAILED — ONTOLOGY** (benchmark-label error) |
| EXP-GT-A-CERT / EXP-GT-03 (head V2) | QUALIFIED (dev) → **FAILED — IMPLEMENTATION** (held-out) |
| EXP-GT-ACERT2 / EXP-GT-03R (head V3) | QUALIFIED (dev) → **FAILED → RETIRED** (held-out) |
| **EXP-GT-ACERT3 / EXP-GT-03R2 (head V4)** | **QUALIFIED (dev) → QUALIFIED (held-out)** |
| EXP-GT-HIERARCHY-00 | **NOT STARTED** |
| **EXP-SC-01 (droplets)** | **BLOCKED** |

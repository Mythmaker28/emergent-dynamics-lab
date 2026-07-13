# HIERARCHICAL_DISCOVERY_PROTOCOL.md

**PREREGISTERED. Frozen before EXP-GT-HIERARCHY-00 is implemented.** Phases 2–6 of the mission.
**NOT YET RUN.** Written now so the discovery algorithm cannot be designed around results it has already seen.

## The information barrier (Phase 2)

The observer receives **only**: raw binary cell trajectories; world dimensions; the coordinates and times of **its
own** interventions and their results; and the declared I/O interface (which cells are outputs).

It does **not** receive: a bounding box, component positions, the **number** of components, channel locations, the
clock period, program bits, the causal graph, or the **depth of the hierarchy**.

The evaluator retains everything: cell ops and wiring, component identities and implementations, clock phase,
register contents, the program, the I/O map, the causal graph and delays, architecture equivalence classes,
lineage, material provenance, and which structures are inert.

## The discovery ladder — no count is hard-coded at any rung

1. recurring / persistent / propagating micro-patterns
2. signal velocities and directions
3. signal channels
4. clock period and cyclic phase group (the **smallest** exact period, so no harmonic can be reported)
5. interaction loci
6. candidate gates
7. **state-bearing regions** — discovered by the **memory signature**: a *transient* perturbation with a
   *permanent* effect. **Nothing else in the world produces it.**
8. input / output variables
9. program-state variables
10. time-lagged causal edges (delays via the **phase quotient**, never a marginal)
11. **feedback cycles**
12. the macro causal architecture

**Rung 7 is load-bearing for rung 12.** Structure behind a closed gate is **not identifiable from single
interventions** (measured, D-062): clamping a channel whose gate is shut does nothing. The observer must first
**discover the memory cells** (rung 7), then use them as a **CONTEXT** that opens the gates, and only then probe
the structure. **Context-discovery is a rung, not an oracle.**

## Three intervention types, and the distinction is substrate-deep

| | |
|---|---|
| **ABLATION** | clamp to 0 for the **whole** window. In a Boolean network a clamp is **reversible**, so a brief clamp measures only a transient. This is the analogue of destruction. |
| **PULSE** | clamp for **one** step. Distinguishes **memory** (permanent effect) from **feed-forward** (forgotten). |
| **CONTEXT** | hold cells at 1 for the whole window, to expose structure behind closed gates. |

## Macro-reality must be counterfactual (Phase 4)

A macro-object is **not** accepted because it is visually persistent or compresses the data. Every proposed
channel, gate, memory element and program variable must make **successful blinded counterfactual predictions**:

- perturb an inferred signal → predict its downstream targets;
- delay a channel → predict the resulting output delay;
- erase a memory candidate → predict **which** future outputs change;
- scramble a gate while **preserving local density** → predict loss of its **specific** function;
- perturb an inferred inert region → predict **negligible** effect;
- break a proposed feedback edge → predict loss of recurrence;
- replace a component implementation → predict which heads stay SAME and which change.

**A discovered level is accepted only when its interventions produce the predicted consequences on held-out
episodes.**

## Scoring

component precision/recall · edge precision/recall · delay error · clock-period accuracy · program decoding ·
memory-state decoding · FSM-transition accuracy · I/O prediction · **counterfactual prediction** ·
**false-certainty rate** · **calibrated abstention** · out-of-scope rate · computational cost.

## Gates

Every inference passes through the **frozen admission layer** first. **An A/S/F decision is INVALID unless
admission returns ADMITTED.** Verdicts: `QUALIFIED — HIERARCHY DISCOVERY` · `QUALIFIED — FACTORIZED IDENTITY ONLY`
· `FAILED — DISCOVERY` · `FAILED — CAUSAL VALIDATION` · `FAILED — SCOPE CALIBRATION` ·
`FAILED — GROUND-TRUTH GENERALIZATION` · `INDETERMINATE` · `RETIRED`. **"Promising" is not a decision.**

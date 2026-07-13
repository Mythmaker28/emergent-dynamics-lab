# HIERARCHY_ADDENDA.md — three BINDING clarifications

**Appended before EXP-GT-HIERARCHY-00 is implemented. Nothing in D-061 or D-062 is changed or withdrawn.**
The scope-admission certificate (D-061) and the component library V2 (D-062) stand exactly as recorded.

---

## A1 — ADMISSION AND ATOMICITY ARE **SCALE-RELATIVE**

The D-061 atomicity test asked: *can a proper sub-part be cleanly ablated to a different effect?* That is the
right question **for one level only** — it qualifies a region as an **ELEMENTARY COMPONENT at V4's declared
resolution**. It is the **wrong** question to ask of a **composite macro-object**, whose sub-parts *are supposed*
to have distinct causal effects. A four-cell De Morgan gate contains a NOT whose ablation differs from the gate's;
that is what it means to be **made of parts**, not evidence of an unresolved merge.

**Binding rule.** Admission is always relative to a **claimed level**. For an object `O` claimed at level `L`:

- **RESOLVABLE at L** — `O` is distinguishable from its neighbours *at level L* by intervention (its ablation
  signature is not identical to a neighbour's, and its boundary is not an artefact of the probe's resolution).
- **CAUSALLY COHERENT at L** — `O` acts as a **unit** on the level-`L` interface: every external consequence of
  ablating any sub-part is *subsumed* by the consequence of ablating `O`, and `O`'s external interface (its
  in-edges and out-edges at level `L`) is well defined.
- **NESTED SUBSTRUCTURE IS PERMITTED, NOT PENALISED.** Sub-parts with distinct *internal* effects are expected.
  A sub-part is disqualifying **only if** it has an **external** effect at level `L` that `O`'s own ablation does
  **not** produce — i.e. only if the sub-part is *leaking a level-`L` interface `O` does not have*. That is the
  merged-blob signature, and it is exactly the D-061 case: the relief opened an output the whole blob left dead.

**D-061 is therefore re-read, not revised:** it certified admission **at the elementary-component level**, and it
remains valid there.

---

## A2 — ARCHITECTURE IS EXPLICITLY **MULTI-SCALE**

`A_TOPO` and `A_TAU` are reported **relative to a discovered partition (a quotient)**, at four levels:

| level | nodes |
|---|---|
| **micro** | individual cells and their cell-to-cell causal edges |
| **component** | maximal causally-coherent cell groups (a wire chain, a gate, a register) |
| **circuit** | the graph over components |
| **machine** | the quotient by *established* functional equivalence |

**Binding rule for the implementation case.** `direct AND` and `De Morgan` **MUST be DIFFERENT at the micro level**
(different cells, different cell-edges). They may be **SAME at a discovered macro-component level *only if the
observer independently establishes all three*:**

1. **functional equivalence** — identical I/O over a probed input set (not asserted, *measured*);
2. **external causal-interface equivalence** — the same in-edges and out-edges at the component level;
3. **delay equivalence** — the same measured latency through the object.

**The hidden evaluator must not grant this quotient by label.** If the observer cannot establish all three, the
macro verdict is **INDETERMINATE**, not SAME.

**E1 consequence:** a Ship-of-Theseus handoff may preserve **macro** architecture while changing **micro**
architecture *and* material. That is now expressible, and it is the point.

---

## A3 — STRUCTURAL CAUSALITY IS **CONTEXT-DEPENDENT**

D-062 measured it: **structure behind a closed gate is not identifiable from single interventions.** Clamping a
channel whose gate is shut does nothing at all. A structural graph built from single interventions therefore
reports **false absence**, which is a fabricated certainty wearing the costume of a negative result.

**Binding rules.**

1. The observer must **autonomously discover context / register variables** — as cells whose *transient*
   perturbation has a *permanent* effect (**the memory signature**). **No evaluator-provided gate-opening state
   may ever enter the observer path.**
2. Edges are **explicitly conditional**: `X → Y | S = 1`. An unconditional edge is a special case
   (`X → Y | ∅`).
3. **CONTEXT-COVERAGE CERTIFICATE.** A structural graph may be declared **complete** only after the observer has
   explored enough discovered contexts to reveal the known conditional paths **on development controls**.
   Otherwise it returns **`STRUCTURAL_GRAPH_INCOMPLETE`** or **`INDETERMINATE`** — **never a false absence.**

---

**Unchanged and binding throughout:** no composite identity score; no held-out tuning; every previous observer,
admission layer, protocol and result preserved; **EXP-SC-01 remains BLOCKED** until prospective blind hierarchy
discovery qualifies.

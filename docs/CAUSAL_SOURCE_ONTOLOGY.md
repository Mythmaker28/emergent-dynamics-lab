# CAUSAL SOURCE ONTOLOGY

The ontology of EXP-GT-SOURCE-TRANSDUCER-00. It replaces "a box and the wires crossing it", which retired at D-065.

**Spatial frontier.** Every conductor cell crossing a candidate region's boundary. Observable geometry, and nothing
more. **It is not the causal interface.** A boundary is a thing I drew; a cause is a thing the world has.

**Boundary tap.** A signal observed on one frontier conductor. Several taps may be the *same* source, delayed,
inverted, or otherwise transformed. Counting taps is not counting causes.

**Independent causal source.** A process whose admissible intervention changes its contribution to the module
without that change being fully determined by another source. Operationally: a **root** — a cell with no causal
parent. A clock, a held register, an external input, an upstream module output.

**Source history.** A finite window of one source. A module may depend on `X(t)`, `X(t−d)`, or a longer past
*without those being separate sources*. One cause, remembered for different lengths of time.

**Reachable manifold.** The joint source histories the dynamics can actually produce under admissible intervention.
Everything outside it is fiction, and a function evaluated there is a fiction about a fiction.

**Causal transducer.** The measured relation `(source histories, contexts) → output histories`. Never a full truth
table when only a restricted manifold was observed.

## The distinction that retired the previous design

`xnor_and` had three boundary taps and two causes: one tap was a re-timing buffer carrying a *delayed copy* of
another. The retired observer clamped the three independently — asking the world "what if this wire disagreed with
its own source?" — and reported a three-input table with no two-input reduction, confidently.

The correction is not a better boundary. It is to stop taking the boundary as the interface at all: **trace every
tap back to the roots that feed it, and intervene only there.**

## Levels, never composited

`micro-architecture` · `source interface` · `untimed transducer` · `timed transducer` · `G` (spatial embedding,
auxiliary). A measured difference is reported as DIFFERENT. Behaviour the world cannot produce is reported as
INDETERMINATE. Collapsing those two — in either direction — is the failure this ontology exists to prevent.

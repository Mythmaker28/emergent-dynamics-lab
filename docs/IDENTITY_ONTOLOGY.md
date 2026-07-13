# IDENTITY_ONTOLOGY.md

**Status: BINDING.** Established by EXP-GT-A0 (D-053). Supersedes the implicit ontology used in EXP-GT-00..02B.

## Why this file exists

EXP-GT-00 asked a single scalar "are these two the same individual?" and got a nonsense answer, because five
different questions were being averaged into one number (D-049). EXP-GT-01/02/02B factorized the question into
heads. **EXP-GT-A0 shows that factorizing is not enough: a head is only as good as the ground-truth label it is
graded against.** `A` was graded DIFFERENT on a pair of circuits that have literally the same causal graph, and
the recorded conclusion was that `A` needed a *finer resolution*. Acting on that would have tuned `A` into a
layout detector — destroying the invariance `A` exists to provide.

**A head must have a definition sharp enough that the benchmark can be caught mislabelling it.** That is what
this file is for.

## The factors

Each factor is reported **separately**, with its own SAME / DIFFERENT / INDETERMINATE verdict.
**They are never composited into a scalar identity score.** A composite is what failed in D-048 and it is banned
project-wide.

| head | question | invariant to | sensitive to |
|---|---|---|---|
| **A** | *causal architecture / topology* | translation, spatial layout, channel spacing, cyclic clock phase, memory word, functionally-equivalent component replacement | node/edge count, connectivity, causal delays, redundancy, feedback, gate presence |
| **S** | *program / memory state* | layout, phase, material implementation | the memory word |
| **F** | *functional input→output relation* | mechanism, layout, phase | the I/O transfer relation |
| **L** | *historical / lineage continuity* | — | observed branch/merge events, continuity of the causal run |
| **M** | *microscopic / material continuity* | — | which cells actually carry the structure |
| **G** | *geometric embedding / layout* — **auxiliary diagnostic** | translation | channel spacing, absolute geometry |

### A is graph-isomorphism-aware and embedding-invariant

`A` is defined on the **structural causal graph**: which components exist and which can influence which, with
what delay. It is **not** defined on positions, columns, spacings, bounding boxes or pixel distances.

Two circuits that are **graph-isomorphic** have `A = SAME`, *however differently they are drawn*.

### G is layout. G is NOT identity.

`G` exists so that a real geometric difference has somewhere to be recorded **without being mistaken for an
architectural one**. `G` is reported separately and **never composited**. A pair may legitimately be
`A = SAME, G = DIFFERENT` — that is not an identity difference, it is a drawing difference.

**Do not redefine `A` post hoc to mean "anything geometrically different."** That is the error EXP-GT-A0 caught.

### Structural graph vs active-influence graph

A closed gate severs an influence path that structurally still exists. So:

- the **active-influence graph** (what an intervention actually propagates through) is **program-dependent**;
- the **structural graph** (the wiring) is **program-independent**.

`A` is read off the **structural** graph. If it were read off the active graph, a mere program change would move
`A` — the exact contamination D-052 already had to fix once (a channel's detected *column* depended on how it was
gated).

The blinded observer sees only influence. It must therefore reconstruct **structure** from influence measured
**across an intervention repertoire rich enough to expose gated paths** (upstream injection reveals a gate;
downstream deletion reveals the wire). That requirement is a **coverage obligation on the probe**, and it must be
certified — see `OBSERVABILITY_CONTRACT.md` and `ARCHITECTURE_RESOLUTION_CERTIFICATE.md`.

## Every ground-truth label carries a viability assertion

**A declared circuit that has never been shown to compute anything is not a ground truth. It is a comment.**

EXP-GT-A0 found `ARCH_HELD_OUT[1] = (10,46,82,118)` shipping as a "held-out architecture" since EXP-GT-00 while
producing **zero output on all four channels** (the Gosper gun spans 36 columns; at spacing 36 adjacent guns touch
and annihilate). Every circuit admitted to the benchmark must now pass an executable assertion that **every
declared channel actually carries a stream** and that the **declared graph is the graph the dynamics realizes**.

## Expected-label discipline

Every benchmark case carries an explicit expected **vector** over A, S, F, L, M, G — plus, per the observability
contract, whether each is **identifiable at all** from the supplied observations. `INDETERMINATE` is a first-class
answer: **correct abstention is a PASS; resolving a relation the data cannot support is fabrication and is
scored as a FAILURE.**

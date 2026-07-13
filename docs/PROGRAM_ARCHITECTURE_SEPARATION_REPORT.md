# PROGRAM_ARCHITECTURE_SEPARATION_REPORT.md

**Status: ACHIEVED.** Substrate: spatially embedded Boolean network (`edlab/substrates/boolnet`).

## The question Game of Life could not pose

A GoL memory bit of 0 was implemented by **adding an eater**. Setting a bit **added a node and two edges**: the
program *was* the architecture. "Same architecture, different program" was **not constructible**, so
EXP-GT-02B's program-invariance pass was a test that **could not fire** — **VACUOUS** (D-055).

## The construction

Memory is a **register cell** with a self-loop: `next = we ? data : self`. With `we` held low it **holds its
initial value forever**. The **wiring never changes**; the **program is the registers' initial contents**.

**Measured: the `op` and `src` arrays are bit-identical across all four programs.** Only the initial state differs.

## Result — and the finding that came with it

| | edges |
|---|---|
| **ACTIVE-influence graph** (clamp to 0), programs 111 / 101 / 010 / 000 | **18 / 12 / 6 / 0** — program-DEPENDENT |
| union over single 0- **and** 1-clamps | **18 / 16 / 14 / 12** — *still* program-dependent |
| **STRUCTURAL graph under a CONTEXT that opens the gates** | **18 / 18 / 18 / 18 — IDENTICAL** |

**A single-component intervention is not enough, and this is a real scientific point, not a technicality.**
Clamping a **channel** while its gate is shut does nothing — the gate outputs 0 whatever the channel does — so the
path stays invisible. **Structure behind a closed gate is not identifiable from single interventions.**

It **is** identifiable from **conditional** ones: hold a **context** that opens the gates, then probe. That is not
a trick; it is how a circuit is actually tested, and it is the substrate's honest answer to *which relations are
identifiable from which experiments*.

For the **evaluator** the context cells are known. A **blind observer must discover them** — as the cells whose
clamping has a **permanent** effect. *That is the memory signature*, and it makes context-discovery a rung on the
hierarchical-discovery ladder rather than an oracle.

## Consequence

**`A_TOPO` is program-invariant. `S` reads the program. `A` does not move.**
The factorization is, for the first time, **testable rather than asserted**.

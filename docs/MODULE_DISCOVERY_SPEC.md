# MODULE DISCOVERY — FROZEN SPECIFICATION (the single authorized repair of D-063)

> ## **Status: RETIRED (D-065).**
> The prospective run (`EXP-GT-HIER-R`) FAILED: function accuracy 50 % on unseen implementations and
> **6/24 false certainty** against a preregistered bar of zero. The design is preserved **unchanged** as a record.
> It must not be patched, re-tuned, or extended. See `docs/EXP_GT_HIER_R_REPORT.md`.
>
> What it *did* fix is real and stands: on implementations it had never seen, module boundary, parents, outputs,
> internal delay and cell count were recovered **exactly** (100 %, mean IoU 1.000); gate recall on an unseen
> implementation went from **0.00 to 1.00**. What it did not fix: it mistakes a **conductor-bounded frontier** for
> a causal interface, so a re-timing buffer carrying a *delayed copy of another parent* is counted as an
> independent input, and the module's function is measured off the manifold the machine can realize.

**Status when written: FROZEN.** Nothing below was changed, tuned, or extended before the prospective run.

| file | sha256 (first 16) |
|---|---|
| `edlab/identity/modules.py` | `b208d5197abcd1ff` |
| `edlab/identity/hier.py` | `f73424143ea170aa` |
| `edlab/identity/admission.py` | `64461df11a2c6740` |

Development certificate: `EXP-GT-MODULES`, **18/18**, on development circuits only.

---

## What failed (D-063)

The retired detector defined a gate as *the earliest cell in a discovered memory's influence cone*. That is a
**position**, not a computation. It happened to coincide with the gate in the one implementation I had built when I
wrote it. On the held-out world whose gate was a De Morgan pair, the first cell downstream of the register is
`NOT(reg)`, which has no output interface under the gate-opening context — so the detector found nothing. Gate
recall **0.00**. The rule had been calibrated on a single implementation without my noticing.

## The definition that replaces it

> A **module** is a maximal connected cluster of **computing** cells — cells that are neither conductors nor
> sources — bounded by conductors, whose external boundary has at least **two independently manipulable parents**
> and at least one output, and whose joint intervention-response relation cannot be explained as a lagged copy of
> any single parent under any discovered context.

Boundary, parents, outputs, truth table, delays and quotient are **all inferred by intervention**. None is received.
No template, no op-code, no position, no cell count, no spatial adjacency enters anywhere.

## The five primitives

**1. The micro causal graph, by one-step pulse.** An ablation cannot isolate a direct edge: clamping one input of
an AND only shows at its output when the *other* input is favourable, so "the child deviates one step after the
parent" is phase-dependent and finds nothing. A **one-step pulse** does isolate it — flip cell `p` at exactly step
`t` and nothing else differs at step `t`, so whatever differs at `t+1` can only be a **direct child** of `p`; an
indirect effect needs at least two steps. Sweep `t` over a full period to cover every phase. The flip forces the
negation of the cell's own value: **non-vacuous by construction**.

**2. Contexts, unioned (addendum A3).** A structural edge can be **dynamically masked**. With its register at 1,
`OR(x,1) = 1` is saturated: pulsing the channel changes nothing and the channel→gate edge is invisible; the gate
then has one parent, is not a junction, and *disappears*. So the graph is built under the baseline **and under
every discovered context**, and edges are unioned. Each edge records the contexts in which it fires — which is
exactly the conditional edge `x → y | S = s`. An edge present only under some context is reported as **conditional**,
never as a false absence.

**3. Classification, by pulse polarity.** Forcing a parent to `v` at step `t` and reading the child at `t+1`
evaluates that edge's transfer function *at v*: same value = it **carries**, opposite = it **inverts**. This is
defined even when the parent is a register that never moves on its own — a passive copy test on a register is
vacuous in *every* context, which is why De Morgan's `NOT(reg)` was previously unclassifiable.

- **source** — no parents.
- **conductor** — one parent, carries it. *A wire.*
- **unary** — one parent, transforms it. *An inverter.*
- **junction** — two or more independently manipulable parents. *A computation.*

An **open gate is observationally indistinguishable from a wire**: `AND(x,1) = x` carries its channel exactly.
What separates them is that a pulse on the *register* also moves the gate, and moves no wire. **A gate is not
something you can see; it is something you must manipulate.**

**4. The boundary is not a growth rule.** Growing outward from a junction, absorbing unary neighbours, works on a
*chain* and shatters on a *diamond*: in `AND(x,r) = XOR(OR(x,r), XOR(x,r))` three junctions read the same two
parents and reconverge, none is unary, nothing is absorbed, and one gate is reported as three — with the winner
decided by iteration order, an arbitrary answer dressed as a measured one. The boundary is the **maximal connected
cluster of computing cells**. Wires bound computation; that is a fact about the machine, not a heuristic about the
search.

**5. Function and delay.** The truth table is measured by clamping **every combination of the module's external
parents** and reading the module's **own boundary cell** (not the wire it drives — for a sub-module inside a
cluster, the wire it drives is the *next computation*). Internal delay is the **shortest one-step-edge path** from
an external parent to that cell: every edge of the micro graph was established by a one-step pulse, so every edge
*is* one step and the path length *is* the latency. (An onset is still not a delay — D-063.)

## Levels, kept separate

| level | what it is | reported as |
|---|---|---|
| micro-architecture | the cells and edges inside the module | cell set, sub-modules |
| macro interface | number of external parents and outputs | `n_parents`, `n_outputs` |
| conditional function | the measured truth table | `truth_table` |
| external delay | internal latency, in steps | `internal_delay` |
| spatial embedding | **G** — auxiliary, never composited | not part of any quotient |

**Multi-scale (addendum A2).** Both scales are reported and both are true: the De Morgan AND *really does contain*
an OR; the reconvergent AND *really is* built from an OR and two XORs. Neither level is granted by a label.

## The quotient must be earned, and reported level by level

- **untimed** = interface + function. A one-cell AND and a four-cell De Morgan AND are the **same macro object**.
- **timed** = + delay. They are **not** — and that is a fact about the world, not an inability to see it.
- **micro** — expected to differ. Reported. Never composited into either verdict.

`INDETERMINATE` is reserved for what is **genuinely unresolved** (an unresolved boundary, or parent coverage above
`MAX_PARENTS = 4`). Reporting a *measured difference* as "I cannot tell" is **false abstention** — the mirror image
of false certainty, and just as dishonest.

## Frozen constants

`MAX_PARENTS = 4` · `OBS = 96` · `HOLD = 6` · `SETTLE = 64` · `CLK_PERIOD = 8` (3-of-8 duty) ·
contexts = `{baseline, all-registers-0, all-registers-1}` · pulse sweep = every phase of the inferred period.

## Development family (all `assert_qualified`, all used in the repair)

`direct` (1-cell AND) · `direct_buf` (AND + 2 conducting buffers) · `demorgan` (4 cells) · `nand2` (3 cells) ·
`xor_or` (3 cells, **reconvergent**) · `or_gate` / `xor_gate` (different functions; **byte-identical output traces**
at program 000 — separable only by context manipulation) · `single_parent` (`AND(x,x)`: two incoming edges, **one**
effective parent) · `decoy=active` (clock-driven, correlated, computes nothing) · `decoy=cross` (three active
geometric neighbours, one causal parent).

## Held out, never used or inspected during the repair

`and_or` = `AND(AND(x,r), OR(x,r))` · `xnor_and` = `AND(x, NOT(XOR(x,r)))` with re-timing buffers, whose two
inputs reach the output at **different latencies** — an asymmetry no development implementation has.

Only their *circuits* were qualified (declared graph == measured graph, functional controls fire). The observer
has never been run on them.

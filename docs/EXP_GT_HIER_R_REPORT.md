# EXP-GT-HIER-R — the single prospective run. **VERDICT: FAIL → RETIRED.**

Frozen observer (`MODULE_DISCOVERY_SPEC.md`, sha256 `b208d519…`), fresh split, run **once**, per the preregistered
rule. Development certificate was 18/18. **No composite score.** Every metric below is reported separately,
including the ones that fail.

## The split

Eight worlds, **jointly** holding out topology (channel triples never used), layout (detour length), **phase**
(development ran *entirely* at `clk_phase = 0`; every world here is non-zero), program, module implementation and
intervention schedule. Two implementations — `and_or` = `AND(AND(x,r), OR(x,r))` and `xnor_and` =
`AND(x, NOT(XOR(x,r)))` with re-timing buffers — were **never used or inspected during the repair**. All eight
worlds passed `assert_qualified` (declared graph == measured graph, functional controls fire) *before* the observer
was run.

## Results — 24 gates

| metric | all | **unseen impls** | seen impls |
|---|---|---|---|
| gate recall (module found) | 100.0 % | **100.0 %** | 100.0 % |
| boundary EXACT (mean IoU) | 100.0 % (1.000) | **100.0 % (1.000)** | 100.0 % |
| parent interface EXACT | 100.0 % | **100.0 %** | 100.0 % |
| output interface EXACT | 100.0 % | **100.0 %** | 100.0 % |
| internal delay EXACT | 100.0 % | **100.0 %** | 100.0 % |
| micro cell count EXACT | 100.0 % | **100.0 %** | 100.0 % |
| **truth table / function** | **75.0 %** | **50.0 %** | 100.0 % |
| **conditional edge** | **79.2 %** | **58.3 %** | 100.0 % |
| **FALSE CERTAINTY** | **6 / 24** | 6 / 12 | 0 / 12 |
| abstentions (INDETERMINATE) | 0 / 24 | 0 / 12 | 0 / 12 |

Blind period recovery: 8/8 worlds correct. Component discovery, contexts and modules: 3 modules found per world,
8/8. Interventions per world: ~2 900.

**The bar of `FALSE CERTAINTY = 0` was written into the harness before the run.** It is 6/24.

## What the repair genuinely fixed

The conceptual failure of D-063 — *a gate is the earliest cell in a memory's influence cone*, i.e. a **position** —
is gone. On implementations it had never seen, the observer recovered the module boundary **exactly** (IoU 1.000),
its parents, its outputs, its internal latency and its cell count, at 100 %. Gate recall on an unseen
implementation went from **0.00 to 1.00**. That result stands.

## What it failed, and why

All six failures are `xnor_and`. Its module `{XOR, NOT, AND}` is bounded by conductors, so its boundary parents are

- the register,
- the channel's last cell, and
- **a re-timing buffer carrying a delayed copy of that same channel cell.**

The detector treated all three as **independent** inputs, clamped them independently — exploring assignments the
machine can never realize — and confidently reported a three-input truth table with no two-input reduction:

```
(chan, reg, buf) -> out        buf is chan, delayed by two steps.
(0,0,0)->0  (0,0,1)->1  (0,1,0)->0  (0,1,1)->0      Rows where buf != chan are OFF-MANIFOLD:
(1,0,0)->0  (1,0,1)->0  (1,1,0)->0  (1,1,1)->1      the machine cannot produce them.
```

Stated without reference to any of my labels:

> `macro_quotient(one-cell AND, unseen xnor_and AND)` = **DIFFERENT / DIFFERENT** (interface ✗, function ✗).
> **The observer cannot recognize an unseen implementation of AND as the same macro object as the AND it knows.**

That is the entire purpose of the repair, and it fails — with **no abstention**.

I built the *coincident correlation* control at the **cell** level (`AND(x,x)`: two incoming edges, one effective
parent) and it passed, in development and again here. I never built it at the **module boundary** level. Nothing in
the development family had a buffer feeding a boundary. The held-out world did — by construction, since I designed
it for asymmetric input latency — and the design broke on exactly that.

It is the same error as D-053 and D-063: **a representational boundary mistaken for a causal one.** The
conductor-bounded frontier is a graph artefact of my own definition; a module's real inputs are its independent
causal *sources*.

## Verdict

**RETIRED, per the preregistered rule. No second repair cycle.** No threshold is adjusted, no
implementation-specific template is added. `edlab/identity/modules.py` is preserved unchanged. The eight
prospective worlds are **BURNED** — `DIAGNOSTIC_ONLY` from here on.

**EXP-SC-01 remains BLOCKED.**

## Design direction for a conceptually different observer

1. A module's interface is its **independent causal sources**, not its conductor-bounded frontier. Trace each
   boundary parent back through conductors to the cell that *originates* it; deduplicate parents sharing a source.
2. A truth table must be measured on the **reachable manifold** of parent assignments. Rows the machine cannot
   realize are counterfactually meaningful but are **not the module's function**, and must never enter a quotient.
3. **Independence between parents must be tested, never assumed** from the fact that they are distinct cells.
4. Where the manifold cannot be established, the correct output is **INDETERMINATE** — not a confident table.

# GROUND-TRUTH CAUSAL AUDIT

> **A variable is causal if an admissible intervention on it changes the downstream distribution.**
> Not if it looks active. Not if it varies. Not if I meant it to matter.

## The defect this replaces

My D-067 scorer excluded the write-enable rail from ground truth, with the justification: *"a wire that never
changes is not a cause; it is a boundary condition."* It is constant 0 in every baseline — and clamping it to 1
makes every register **load**. The observer discovered that and named it a source. I marked the observer wrong.

I had written the exclusion **in order to make the ground truth produce the source count I expected**, and then
quoted it back at the observer as truth. That is the D-053 error, committed in the scorer, after two retirements
for exactly that class of mistake.

## Two paths, or it is not ground truth

**DECLARED** — the construction graph, read off `op`/`src`. What I built.
**PRIVILEGED** — the intervention-derived graph: clamp each cell to 0 and to 1, under the baseline and every
context, and look at the child. A clamp that cannot change the cell's own value is **vacuous** and proves nothing.

Every measured edge must be declared. Every declared edge must be measured **or provably masked**, and the mask
must be exhibited. Disagreement rejects the **world**, before any observer sees it.

## The must-pass cases, and what they show

| case | result |
|---|---|
| the write-enable is **silent in baseline** but changes register loading | `we → reg` **ACTIVE** when the register holds 0 (`base:1`) |
| the same edge is **masked** when the register already holds the data value | `we → reg` **INACTIVE** at program bit 1 — writing 1 to a register holding 1 changes nothing |
| a **closed gate** hides a structural path | the channel→gate edge fires only under the gate-opening context |
| two **synchronized** variables are independently causal | `and3` / `sync3`: two registers, byte-identical baseline series, both causal |
| a **visually active rail** is causally irrelevant | the clock-driven decoy: alive, correlated, and not a cause of any output |
| an apparently **inert context variable** opens a downstream path | the write-enable, above |

**Consequence, measured.** The privileged source set is **program-dependent**: `{clk, reg}` where the register
holds 1, `{clk, we}` where it holds 0. The active observer agreed with it on **24/24** prospective transducers.

## What I still got wrong, and it must be recorded

I applied the two-path contract to the **sources** and **not to the function**. `TRUE["xor3"]` was a lambda I
hand-declared from the circuit I *intended* to build. The circuit I actually built reads its two inputs at
different lags. Under §2 that world should have been **rejected before the observer ran**. It was not, because I
never built the second path for the function.

The correct check — comparing the observer's table against a privileged simulation using the observer's own
features — was run afterwards, uniformly on every world. **Every table agrees. The function accuracy is 100 %.**
My scorer had flagged the right rows for the wrong reason.
